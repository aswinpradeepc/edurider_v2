from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin  # Use GISModelAdmin instead of OSMGeoAdmin
from .models import Student

@admin.register(Student)
class StudentAdmin(GISModelAdmin):  # Changed from OSMGeoAdmin to GISModelAdmin
    """Admin configuration for the Student model."""
    
    # Fields to display in the list view
    list_display = ('name', 'class_grade', 'guardian_name', 'phone_number', 'is_active')
    
    # Fields to filter on in the right sidebar
    list_filter = ('class_grade', 'is_active', 'created_at')
    
    # Fields to search on
    search_fields = ('name', 'guardian_name', 'email', 'phone_number', 'address_text')
    
    # Organize fields into fieldsets for better readability
    fieldsets = (
        ('Basic Information', {
            'fields': ('student_id', 'name', 'class_grade', 'is_active')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone_number')
        }),
        ('Location Information', {
            'fields': ('address_text', 'coordinates')
        }),
        ('Guardian Information', {
            'fields': ('guardian_name',)
        }),
        ('Trip Assignment', {
            'fields': ('route_plan',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    # Make certain fields read-only
    readonly_fields = ('student_id', 'created_at', 'updated_at')
    
    # Default fields for creating a new student
    add_fieldsets = (
        (None, {
            'fields': ('name', 'class_grade', 'email', 'phone_number', 'address_text', 
                      'coordinates', 'guardian_name', 'route_plan')
        }),
    )
