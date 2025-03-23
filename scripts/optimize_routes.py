import os
import sys
import django
import numpy as np
from sklearn.cluster import KMeans
from datetime import datetime
import math
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from students.models import Student
from routeplan.models import Trip
from drivers.models import Driver
from attendance.models import Attendance
from django.utils import timezone

MAX_STUDENTS_PER_TRIP = 40

def get_student_coordinates(students):
    """
    Extract coordinates from student objects
    Returns: List of coordinates and dictionary mapping coordinates to students
    """
    coords = []
    coord_to_student = {}
    
    for student in students:
        if student.coordinates:
            coord = (student.coordinates.x, student.coordinates.y)
            coords.append(coord)
            coord_to_student[coord] = student
        else:
            logging.warning(f"Student {student.name} has no coordinates set")
    
    if not coords:
        raise ValueError("No students have coordinates set")
    
    return np.array(coords), coord_to_student

def optimize_routes(date, direction='to_school'):
    """
    Optimize routes for a specific date using K-means clustering.
    Only includes students who are marked present for that date.
    Creates clusters with maximum size of 40 students.
    
    Args:
        date (datetime.date): Date to optimize routes for
        direction (str): 'to_school' or 'from_school'
    """
    logging.info(f"Optimizing routes for {date} ({direction})...")
    
    try:
        # Get all students who are marked present for this date
        present_students = Student.objects.filter(
            attendance_records__date=date,
            attendance_records__presence=True,
            coordinates__isnull=False  # Only include students with coordinates
        ).distinct()
        
        total_students = present_students.count()
        if not total_students:
            logging.info(f"No students marked present for {date}")
            return
        
        logging.info(f"Found {total_students} students marked present")
        
        # Calculate optimal number of clusters
        num_clusters = math.ceil(total_students / MAX_STUDENTS_PER_TRIP)
        logging.info(f"Creating {num_clusters} optimized routes")
        
        # Get available drivers
        available_drivers = list(Driver.objects.filter(status='available', is_active=True))
        if len(available_drivers) < num_clusters:
            logging.warning(f"Warning: Need {num_clusters} drivers but only {len(available_drivers)} available")
            num_clusters = len(available_drivers)
            logging.info(f"Reducing to {num_clusters} routes due to driver availability")
        
        # Get coordinates for clustering
        coords, coord_to_student = get_student_coordinates(present_students)
        
        # Perform K-means clustering
        kmeans = KMeans(
            n_clusters=num_clusters,
            random_state=42,
            n_init=10  # Number of times to run with different centroid seeds
        ).fit(coords)
        
        # Group students by cluster
        clusters = {i: [] for i in range(num_clusters)}
        for i, label in enumerate(kmeans.labels_):
            coord = tuple(coords[i])
            student = coord_to_student[coord]
            clusters[label].append(student)
        
        # Delete existing trips for this date and direction
        Trip.objects.filter(trip_date=date, to_school=direction=='to_school').delete()
        
        # Create new optimized trips
        for cluster_id, cluster_students in clusters.items():
            if not cluster_students:
                continue
                
            driver = available_drivers[cluster_id]
            
            # Calculate cluster center
            cluster_coords = np.array([(s.coordinates.x, s.coordinates.y) for s in cluster_students])
            center = cluster_coords.mean(axis=0)
            
            # Create new trip
            trip = Trip.objects.create(
                trip_date=date,
                to_school=(direction == 'to_school'),
                start_time='07:30:00' if direction == 'to_school' else '15:30:00',
                end_time='08:30:00' if direction == 'to_school' else '16:30:00',
                status='pending',
                driver=driver
            )
            
            # Assign students to trip
            trip.student_list.set(cluster_students)
            
            logging.info(f"✓ Created optimized trip for {len(cluster_students)} students with driver {driver.name}")
            logging.info(f"  Cluster center: ({center[0]:.6f}, {center[1]:.6f})")
    
    except Exception as e:
        logging.error(f"Error optimizing routes: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        logging.error("Please provide a date in YYYY-MM-DD format")
        sys.exit(1)
        
    try:
        date = datetime.strptime(sys.argv[1], '%Y-%m-%d').date()
        logging.info(f"Optimizing routes for date: {date}")
        
        # Optimize both morning and afternoon routes
        optimize_routes(date, 'to_school')
        optimize_routes(date, 'from_school')
        
        logging.info("\nRoute optimization completed!")
    except Exception as e:
        logging.error(f"Error: {str(e)}")
