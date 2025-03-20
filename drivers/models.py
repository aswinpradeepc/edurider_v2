from django.db import models
import uuid
from django.contrib.gis.db import models as gis_models


class Driver(models.Model):
    """
    Driver model to store information about bus drivers in the system.
    Includes location tracking capabilities for real-time bus tracking.
    """
    # Primary key using UUID
    driver_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    # Basic driver information
    name = models.CharField(max_length=100)
    licence_no = models.CharField(max_length=50, unique=True)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    
    # Bus information
    bus_no = models.CharField(max_length=20)
    
    # Real-time location tracking
    current_location = gis_models.PointField(
        blank=True, 
        null=True, 
        help_text="Updated via WebSocket when driver is on a trip"
    )
    
    # Last location update timestamp for tracking freshness
    location_updated_at = models.DateTimeField(
        blank=True, 
        null=True, 
        help_text="Timestamp of the last location update"
    )
    
    # Status of the driver
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('on_trip', 'On Trip'),
        ('offline', 'Offline'),
        ('on_leave', 'On Leave'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='available'
    )
    
    # Record keeping fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} ({self.bus_no})"
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Driver'
        verbose_name_plural = 'Drivers'
        indexes = [
            models.Index(fields=['email']),  # For authentication lookups
            models.Index(fields=['status']),  # For filtering active drivers
            models.Index(fields=['bus_no']),  # For bus number searches
        ]
    
    def update_location(self, longitude, latitude):
        """
        Update the driver's current location and timestamp
        
        Args:
            longitude (float): Longitude coordinate
            latitude (float): Latitude coordinate
        """
        from django.utils import timezone
        from django.contrib.gis.geos import Point
        
        self.current_location = Point(longitude, latitude)
        self.location_updated_at = timezone.now()
        self.save(update_fields=['current_location', 'location_updated_at'])
