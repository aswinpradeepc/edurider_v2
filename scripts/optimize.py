import os
import sys
import django
import json
import requests
from datetime import datetime

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from students.models import Student
from routeplan.models import Trip
from django.conf import settings

MAPBOX_TOKEN = os.getenv('MAPBOX_ACCESS_TOKEN')  # Match the env variable name
SCHOOL_COORDINATES = [76.328898, 10.0482921]  # [longitude, latitude]

def optimize_route(trip_id):
    """
    Optimize a single trip's route using Mapbox Optimization API
    """
    try:
        trip = Trip.objects.get(route_plan_id=trip_id)
        students = trip.students.all()
        
        if not students:
            print(f"No students found for trip {trip_id}")
            return
        
        # Prepare coordinates for optimization
        # Start and end at school
        coordinates = [SCHOOL_COORDINATES]
        
        # Add student locations
        for student in students:
            coordinates.append([student.location.x, student.location.y])
        
        # Add school again as end point
        coordinates.append(SCHOOL_COORDINATES)
        
        # Prepare the request for Mapbox Optimization API
        coordinates_str = ';'.join([f"{coord[0]},{coord[1]}" for coord in coordinates])
        url = f"https://api.mapbox.com/optimized-trips/v1/mapbox/driving/{coordinates_str}"
        
        params = {
            'access_token': MAPBOX_TOKEN,
            'source': 'first',
            'destination': 'last',
            'roundtrip': False,
            'geometries': 'geojson'
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if 'trips' in data:
            trip_data = data['trips'][0]
            waypoint_order = data['waypoints']
            
            # Prepare route data
            route_data = {
                'stops': [],
                'total_distance': trip_data['distance'] / 1000,  # Convert to km
                'estimated_duration': trip_data['duration']  # In seconds
            }
            
            # Add school as first stop
            route_data['stops'].append({
                'type': 'school',
                'coordinates': SCHOOL_COORDINATES
            })
            
            # Add student stops in optimized order
            student_list = list(students)
            for waypoint in waypoint_order[1:-1]:  # Skip first and last (school)
                student = student_list[waypoint['waypoint_index'] - 1]  # -1 to account for school
                route_data['stops'].append({
                    'type': 'student',
                    'coordinates': [student.location.x, student.location.y],
                    'student_name': student.name
                })
            
            # Add school as last stop
            route_data['stops'].append({
                'type': 'school',
                'coordinates': SCHOOL_COORDINATES
            })
            
            # Save optimized route to trip
            trip.route_order = route_data
            trip.save()
            
            print(f"Successfully optimized route for trip {trip_id}")
            print(f"Total distance: {route_data['total_distance']:.2f} km")
            print(f"Estimated duration: {route_data['estimated_duration'] / 60:.0f} minutes")
        else:
            print(f"Error optimizing route for trip {trip_id}: {data.get('message', 'Unknown error')}")
    
    except Trip.DoesNotExist:
        print(f"Trip {trip_id} not found")
    except Exception as e:
        print(f"Error optimizing route for trip {trip_id}: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python optimize.py <trip_id>")
        sys.exit(1)
    
    optimize_route(sys.argv[1])
