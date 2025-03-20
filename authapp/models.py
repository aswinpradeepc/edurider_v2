from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    """Extended profile for users"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    USER_TYPE_CHOICES = (
        ('admin', 'Administrator'),
        ('driver', 'Bus Driver'),
        ('guardian', 'Student Guardian'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    
    # For parent/guardian - which student they're associated with
    student = models.ForeignKey(
        'students.Student', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='user_profiles'
    )
    
    # For driver - which driver profile they're associated with
    driver = models.ForeignKey(
        'drivers.Driver', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='user_profiles'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.email} - {self.get_user_type_display()}"