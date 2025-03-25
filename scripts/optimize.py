import os
import sys
import django
import json
import requests
import logging
from datetime import datetime
from time import sleep

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from routeplan.models import Trip
from students.models import Student

MAPBOX_TOKEN = os.environ.get('MAPBOX_TOKEN')
BASE_URL = "https://api.mapbox.com/optimized-trips/v2"
SCHOOL_COORDINATES = [76.328898, 10.0482921]  # [longitude, latitude]

def create_optimization_request(students):
    """Create the optimization request body for Mapbox API for a single trip."""
    # Create locations list starting with school
    locations = [{
        "name": "school",
        "coordinates": SCHOOL_COORDINATES
    }]
    
    # Add student locations
    for idx, student in enumerate(students):
        locations.append({
            "name": f"student-{idx}",
            "coordinates": [student.coordinates.x, student.coordinates.y]
        })
    
    # Create single vehicle
    vehicles = [{
        "name": "bus-1",
        "routing_profile": "mapbox/driving",
        "start_location": "school",
        "end_location": "school"
    }]
    
    # Create services list (using services instead of shipments since we just need to visit each location)
    services = []
    for idx in range(len(students)):
        services.append({
            "name": f"student-service-{idx}",
            "location": f"student-{idx}"
        })
    
    # Create the request body
    request_body = {
        "version": 1,
        "locations": locations,
        "vehicles": vehicles,
        "services": services,
        "options": {
            "objectives": ["min-total-travel-duration"]
        }
    }
    
    return request_body

def submit_optimization_request(request_body):
    """Submit the optimization request to Mapbox API."""
    response = requests.post(
        f"{BASE_URL}?access_token={MAPBOX_TOKEN}",
        json=request_body,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code != 202:
        raise Exception(f"Failed to submit optimization request: {response.text}")
    
    return response.json()["id"]

def get_optimization_result(job_id):
    """Get the optimization result from Mapbox API."""
    while True:
        response = requests.get(
            f"{BASE_URL}/{job_id}?access_token={MAPBOX_TOKEN}"
        )
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 202:
            logging.info("Optimization in progress, waiting 5 seconds...")
            sleep(5)
        else:
            raise Exception(f"Failed to get optimization result: {response.text}")

def update_trip_order(trip, solution):
    """Update the trip with the optimized order of students."""
    try:
        # Extract the ordered stops from the solution
        route = solution["routes"][0]  # We only have one route
        stops = []
        student_order = []
        
        for stop in route["stops"]:
            if stop["type"] == "service":
                # Extract student index from the location name (format: "student-{idx}")
                student_idx = int(stop["location"].split("-")[1])
                student_order.append(student_idx)
                
                # Get the student's coordinates
                student = list(trip.student_list.all())[student_idx]
                stops.append({
                    "type": "student",
                    "coordinates": [student.coordinates.x, student.coordinates.y],
                    "student_name": student.name
                })
            elif stop["type"] in ["start", "end"]:
                stops.append({
                    "type": stop["type"],
                    "coordinates": SCHOOL_COORDINATES,
                    "location": "school"
                })
        
        # Calculate total distance (in km) and duration
        total_distance = route["stops"][-1]["odometer"] / 1000  # Convert to kilometers
        estimated_duration = (
            datetime.fromisoformat(route["stops"][-1]["eta"]) - 
            datetime.fromisoformat(route["stops"][0]["eta"])
        ).total_seconds()
        
        # Store the optimized route in the trip's route_order field
        route_data = {
            "stops": stops,
            "total_distance": total_distance,
            "estimated_duration": estimated_duration
        }
        
        # Update trip fields
        trip.route_order = route_data
        trip.total_distance = total_distance
        
        # Update the student order in the many-to-many relationship
        students = list(trip.student_list.all())
        ordered_students = [students[idx] for idx in student_order]
        
        trip.student_list.clear()
        for student in ordered_students:
            trip.student_list.add(student)
        
        trip.save()
        logging.info(f"Updated order for trip {trip.route_plan_id}")
        logging.info(f"Total distance: {total_distance:.2f}km, Duration: {estimated_duration/60:.1f}min")
        
    except Exception as e:
        logging.error(f"Error updating trip order: {str(e)}")
        raise

def optimize_routes(date_str):
    """Optimize the order of students in each existing trip."""
    try:
        # Convert date string to date object
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        # Get all trips for the date
        trips = Trip.objects.filter(trip_date=date)
        
        if not trips:
            logging.info(f"No trips found for {date}")
            return
        
        # Process each trip
        for trip in trips:
            students = list(trip.student_list.all())
            if not students:
                logging.warning(f"Trip {trip.route_plan_id} has no students, skipping...")
                continue
            
            logging.info(f"Optimizing order for trip {trip.route_plan_id} with {len(students)} students")
            
            # Create and submit optimization request
            request_body = create_optimization_request(students)
            job_id = submit_optimization_request(request_body)
            logging.info(f"Submitted optimization request with ID: {job_id}")
            
            # Get optimization result
            solution = get_optimization_result(job_id)
            logging.info("Received optimization solution")
            
            # Update trip with optimized order
            update_trip_order(trip, solution)
            
        logging.info("Successfully optimized all trips")
        
    except Exception as e:
        logging.error(f"Error optimizing routes: {str(e)}")
        raise

if __name__ == "__main__":
    if len(sys.argv) < 2:
        logging.error("Please provide a date in YYYY-MM-DD format")
        sys.exit(1)
    
    date_str = sys.argv[1]
    optimize_routes(date_str)
