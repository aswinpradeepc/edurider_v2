from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin
from .models import Driver

@admin.register(Driver)
class DriverAdmin(GISModelAdmin):
    """Admin configuration for the Driver model."""
    
    # Fields to display in the list view
    list_display = ('name', 'bus_no', 'status', 'phone_number', 'email', 
                   'location_status', 'is_active')
    
    # Fields to filter on in the right sidebar
    list_filter = ('status', 'is_active', 'created_at')
    
    # Fields to search on
    search_fields = ('name', 'bus_no', 'licence_no', 'email', 'phone_number')
    
    # Organize fields into fieldsets for better readability
    fieldsets = (
        ('Driver Information', {
            'fields': ('driver_id', 'name', 'licence_no', 'is_active')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone_number')
        }),
        ('Bus Details', {
            'fields': ('bus_no', 'status')
        }),
        ('Location Tracking', {
            'fields': ('current_location', 'location_updated_at'),
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    # Make certain fields read-only
    readonly_fields = ('driver_id', 'location_updated_at', 'created_at', 'updated_at')
    
    # Add custom actions
    actions = ['mark_as_available', 'mark_as_offline', 'mark_as_on_leave']
    
    def location_status(self, obj):
        """Display the status of driver location data"""
        if not obj.current_location:
            return "No location data"
        
        from django.utils import timezone
        if not obj.location_updated_at:
            return "Location data incomplete"
        
        # Calculate how long ago the location was updated
        time_diff = timezone.now() - obj.location_updated_at
        minutes_ago = int(time_diff.total_seconds() / 60)
        
        if minutes_ago < 5:
            return f"Current ({minutes_ago}m ago)"
        elif minutes_ago < 60:
            return f"Recent ({minutes_ago}m ago)"
        else:
            hours_ago = int(minutes_ago / 60)
            return f"Outdated ({hours_ago}h ago)"
    
    location_status.short_description = "Location Status"
    
    def mark_as_available(self, request, queryset):
        """Admin action to mark selected drivers as available"""
        updated = queryset.update(status='available')
        self.message_user(request, f"{updated} drivers were marked as available.")
    mark_as_available.short_description = "Mark selected drivers as available"
    
    def mark_as_offline(self, request, queryset):
        """Admin action to mark selected drivers as offline"""
        updated = queryset.update(status='offline')
        self.message_user(request, f"{updated} drivers were marked as offline.")
    mark_as_offline.short_description = "Mark selected drivers as offline"
    
    def mark_as_on_leave(self, request, queryset):
        """Admin action to mark selected drivers as on leave"""
        updated = queryset.update(status='on_leave')
        self.message_user(request, f"{updated} drivers were marked as on leave.")
    mark_as_on_leave.short_description = "Mark selected drivers as on leave"