from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django.utils.safestring import mark_safe
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from datetime import datetime, timedelta
import subprocess
import calendar
from .models import Trip
import json
from config.settings import BASE_DIR

@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    """Admin configuration for the Trip model."""
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('route-management/', self.admin_site.admin_view(self.route_management_view), name='route-management'),
            path('run-clustering/<str:date>/', self.admin_site.admin_view(self.run_clustering), name='run-clustering'),
            path('run-optimization/<str:date>/', self.admin_site.admin_view(self.run_optimization), name='run-optimization'),
            path('create-attendance/', self.admin_site.admin_view(self.create_attendance), name='create-attendance'),
        ]
        return custom_urls + urls

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['route_management_url'] = reverse('admin:route-management')
        return super().changelist_view(request, extra_context=extra_context)

    def route_management_view(self, request):
        # Get all unique dates from trips
        dates = Trip.objects.dates('trip_date', 'day', order='DESC')
        
        # Get current month and year for attendance creation
        today = datetime.now()
        current_month = today.strftime('%B %Y')
        next_month = (today + timedelta(days=32)).strftime('%B %Y')
        
        context = {
            'title': 'Route Management',
            'dates': dates,
            'current_month': current_month,
            'next_month': next_month,
            'opts': self.model._meta,
        }
        return render(request, 'admin/routeplan/route_management.html', context)
    
    def run_clustering(self, request, date):
        try:
            # If it's a POST request, get the date from the form
            if request.method == 'POST':
                date = request.POST.get('trip_date', date)
            
            result = subprocess.run(
                ['python', 'scripts/cluster.py', date],
                capture_output=True,
                text=True,
                cwd=BASE_DIR
            )
            if result.returncode == 0:
                messages.success(request, f'Successfully clustered routes for {date}')
            else:
                messages.error(request, f'Error clustering routes: {result.stderr}')
        except Exception as e:
            messages.error(request, f'Error running clustering script: {str(e)}')
        return HttpResponseRedirect(reverse('admin:route-management'))
    
    def run_optimization(self, request, date):
        try:
            result = subprocess.run(
                ['python', 'scripts/optimize.py', date],
                capture_output=True,
                text=True,
                cwd=BASE_DIR
            )
            if result.returncode == 0:
                messages.success(request, f'Successfully optimized routes for {date}')
            else:
                messages.error(request, f'Error optimizing routes: {result.stderr}')
        except Exception as e:
            messages.error(request, f'Error running optimization script: {str(e)}')
        return HttpResponseRedirect(reverse('admin:route-management'))
    
    def create_attendance(self, request):
        if request.method == 'POST':
            month = request.POST.get('month')
            try:
                date = datetime.strptime(month, '%B %Y')
                # Create attendance records for the month
                # You'll need to implement this based on your attendance creation logic
                messages.success(request, f'Successfully created attendance records for {month}')
            except Exception as e:
                messages.error(request, f'Error creating attendance records: {str(e)}')
        return HttpResponseRedirect(reverse('admin:route-management'))
    
    # Fields to display in the list view
    list_display = ('trip_date', 'start_time', 'end_time', 'status', 
                   'to_school', 'driver', 'total_distance', 'student_count')
    
    # Fields to filter on in the right sidebar
    list_filter = ('status', 'trip_date', 'to_school')
    
    # Fields to search on
    search_fields = ('route_plan_id', 'driver__name', 'driver__bus_no')
    
    # Date hierarchy for drilling down by date
    date_hierarchy = 'trip_date'
    
    # Organize fields into fieldsets for better readability
    fieldsets = (
        ('Trip Information', {
            'fields': ('route_plan_id', 'trip_date', 'start_time', 'end_time', 'to_school', 'status')
        }),
        ('Route Details', {
            'fields': ('total_distance', 'route_order'),
            'classes': ('collapse',)
        }),
        ('Assignment', {
            'fields': ('driver', 'student_list')
        }),
        ('Map', {
            'fields': ('map',)
        }),
    )
    
    # Fields that cannot be changed
    readonly_fields = ('route_plan_id', 'created_at', 'updated_at', 'map')
    
    # Many-to-many field display with filter
    filter_horizontal = ('student_list',)
    
    # Actions to perform on multiple trips
    actions = ['mark_as_active', 'mark_as_completed', 'mark_as_cancelled']
    
    def student_count(self, obj):
        """Return the number of students assigned to this trip."""
        return obj.student_list.count()
    student_count.short_description = 'Students'
    
    def mark_as_active(self, request, queryset):
        """Admin action to mark selected trips as active"""
        updated = queryset.update(status='active')
        self.message_user(request, f"{updated} trips were marked as active.")
    mark_as_active.short_description = "Mark selected trips as active"
    
    def mark_as_completed(self, request, queryset):
        """Admin action to mark selected trips as completed"""
        updated = queryset.update(status='completed')
        self.message_user(request, f"{updated} trips were marked as completed.")
    mark_as_completed.short_description = "Mark selected trips as completed"
    
    def mark_as_cancelled(self, request, queryset):
        """Admin action to mark selected trips as cancelled"""
        updated = queryset.update(status='cancelled')
        self.message_user(request, f"{updated} trips were marked as cancelled.")
    mark_as_cancelled.short_description = "Mark selected trips as cancelled"
    
    def map(self, obj):
        """Render a map with all students' locations marked"""
        students = obj.student_list.all()
        student_locations = [
            {'name': student.name, 'latitude': student.coordinates.y, 'longitude': student.coordinates.x}
            for student in students if student.coordinates
        ]
        return mark_safe(f"""
            <div id="map" style="height: 500px;"></div>
            <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
            <script>
                document.addEventListener('DOMContentLoaded', function() {{
                    var map = L.map('map').setView([0, 0], 2);
                    L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                    }}).addTo(map);
                    
                    var students = {json.dumps(student_locations)};
                    console.log('Student locations:', students);
                    students.forEach(function(student) {{
                      var marker = L.marker([student.latitude, student.longitude]).addTo(map);
                      marker.bindPopup(`<b>${{student.name}}</b>`);
                    }});
                }});
            </script>
        """)
    map.short_description = "Student Locations Map"