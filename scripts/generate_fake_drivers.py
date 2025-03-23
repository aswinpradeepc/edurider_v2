import os
import sys
import django
from faker import Faker

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from drivers.models import Driver

def generate_fake_drivers(count=15):
    """
    Generate fake drivers with Indian names and details
    """
    fake = Faker('en_IN')  # Using Indian locale for more relevant names
    
    # License number format: DL-YYYYCCCCCCCC
    # DL = Driving License
    # YYYY = Year of issue
    # CCCCCCCC = 8-digit unique code
    license_year = 2020
    license_counter = 1
    
    print(f"Creating {count} drivers...")
    
    for i in range(count):
        name = fake.name_male()  # Using male names as most drivers are male in India
        
        # Generate unique license number
        license_no = f"DL-{license_year}{str(license_counter).zfill(8)}"
        license_counter += 1
        
        # Create driver
        driver = Driver.objects.create(
            name=name,
            licence_no=license_no,
            phone_number=fake.phone_number(),
            email=fake.email(),
            status='available',
            is_active=True
        )
        
        print(f"✓ Created driver: {driver.name} (License: {driver.licence_no})")

if __name__ == "__main__":
    print("Starting to generate fake drivers...")
    generate_fake_drivers()
    print("\nCompleted generating drivers!")
