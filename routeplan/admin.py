from django.contrib import admin
from .models import Trip

@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    """Admin configuration for the Trip model."""
    
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
        ('Assignments', {
            'fields': ('driver', 'student_list')
        }),
    )
    
    # Fields that cannot be changed
    readonly_fields = ('route_plan_id', 'created_at', 'updated_at')
    
    # Many-to-many field display with filter
    filter_horizontal = ('student_list',)
    
    # Actions to perform on multiple trips
    actions = ['mark_as_active', 'mark_as_completed', 'mark_as_cancelled']
    
    def student_count(self, obj):
        """Display the number of students assigned to this trip"""
        return obj.student_list.count()
    student_count.short_description = "Students"
    
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