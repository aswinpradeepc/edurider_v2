import os
import sys
import django
import random
from faker import Faker
from django.contrib.gis.geos import Point

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from students.models import Student

def generate_fake_students(count=200):
    fake = Faker('en_IN')  # Using Indian locale for more relevant names
    
    # Kochi coordinates
    BASE_LAT = 10.0425812
    BASE_LON = 76.3259579
    
    # Class choices from the model
    CLASS_CHOICES = [choice[0] for choice in Student.CLASS_CHOICES]
    
    for _ in range(count):
        # Generate random coordinates within roughly 5km radius
        lat = BASE_LAT + random.uniform(-0.05, 0.05)
        lon = BASE_LON + random.uniform(-0.05, 0.05)
        
        # Create student
        student = Student(
            name=fake.name(),
            class_grade=random.choice(CLASS_CHOICES),
            phone_number=fake.phone_number(),
            email=fake.email(),
            address_text=fake.address(),
            coordinates=Point(lon, lat),
            guardian_name=fake.name(),
            is_active=True
        )
        student.save()
        print(f"Created student: {student.name}")

if __name__ == "__main__":
    print("Starting to generate fake students...")
    generate_fake_students()
    print("Completed generating fake students!")
