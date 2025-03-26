from django.core.management.base import BaseCommand
from drivers.models import Driver
from django.contrib.gis.geos import Point

class Command(BaseCommand):
    help = 'Creates a test driver for WebSocket testing'

    def handle(self, *args, **kwargs):
        # Create a test driver
        driver, created = Driver.objects.get_or_create(
            email='test.driver@edurider.com',
            defaults={
                'name': 'Test Driver',
                'licence_no': 'TEST123456',
                'phone_number': '9876543210',
                'bus_no': 'BUS001',
                'current_location': Point(76.328898, 10.0482921)  # School coordinates
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(
                f'Successfully created test driver with ID: {driver.driver_id}'
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                f'Test driver already exists with ID: {driver.driver_id}'
            ))
