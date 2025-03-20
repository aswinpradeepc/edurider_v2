from django.db import models
import uuid
from django.contrib.gis.db import models as gis_models
from django.utils import timezone
from django.contrib.gis.geos import Point


class Student(models.Model):
    """
    Student model to store information about each student in the bus management system.
    """
    # Primary key using UUID for better security and distribution
    student_id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
    )
    
    # Basic student information
    name = models.CharField(max_length=100)
    # Using CharField with choices for class levels
    CLASS_CHOICES = [
        ('KG', 'Kindergarten'),
        ('1', 'Class 1'),
        ('2', 'Class 2'),
        ('3', 'Class 3'),
        ('4', 'Class 4'),
        ('5', 'Class 5'),
        ('6', 'Class 6'),
        ('7', 'Class 7'),
        ('8', 'Class 8'),
        ('9', 'Class 9'),
        ('10', 'Class 10'),
        ('11', 'Class 11'),
        ('12', 'Class 12'),
    ]
    class_grade = models.CharField(max_length=3, choices=CLASS_CHOICES)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    
    # Address information
    address_text = models.TextField()
    # Using PointField for storing geographic coordinates (requires PostGIS)
    coordinates = gis_models.PointField(blank=True, null=True)
    location_updated_at = models.DateTimeField(blank=True, null=True)
    
    # Guardian information - as specified in task.md
    guardian_name = models.CharField(max_length=100)
    
    # Foreign Key to Trip model in the Routeplan app (nullable as it's assigned dynamically)
    route_plan = models.ForeignKey(
        'routeplan.Trip', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='students'
    )
    
    # Record keeping fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} - {self.get_class_grade_display()}"
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Student'
        verbose_name_plural = 'Students'
    
    def update_coordinates(self, longitude, latitude):
        """
        Update the student's geographic coordinates
        
        Args:
            longitude (float): Longitude coordinate
            latitude (float): Latitude coordinate
        """
        self.coordinates = Point(longitude, latitude)
        self.location_updated_at = timezone.now()
        self.save(update_fields=['coordinates', 'location_updated_at'])
        return self.coordinates