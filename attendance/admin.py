from django.contrib import admin
from django.utils.html import format_html
from .models import Attendance

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    """Admin configuration for the Attendance model."""
    
    # Fields to display in the list view
    list_display = ('student_name', 'trip_info', 'date', 'attendance_status', 
                   'marked_by_user', 'created_at')
    
    # Fields to filter on in the right sidebar
    list_filter = ('presence', 'date', 'trip__to_school', 'created_at')
    
    # Date hierarchy for drilling down by date
    date_hierarchy = 'date'
    
    # Fields to search on
    search_fields = ('student__name', 'trip__route_plan_id', 'marked_by__username')
    
    # Organize fields into fieldsets for better readability
    fieldsets = (
        ('Attendance Information', {
            'fields': ('attendance_id', 'student', 'trip', 'date', 'presence')
        }),
        ('Record Keeping', {
            'fields': ('marked_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    # Fields that cannot be changed
    readonly_fields = ('attendance_id', 'created_at', 'updated_at')
    
    # Sorting options
    ordering = ('-date', 'student__name')
    
    # Actions for multiple records
    actions = ['mark_selected_present', 'mark_selected_absent']
    
    def student_name(self, obj):
        """Format student name with link to student admin"""
        return format_html(
            '<a href="/admin/students/student/{}/change/">{}</a>',
            obj.student.student_id, obj.student.name
        )
    student_name.short_description = "Student"
    student_name.admin_order_field = "student__name"
    
    def trip_info(self, obj):
        """Format trip information with direction"""
        direction = "To School" if obj.trip.to_school else "From School"
        return format_html(
            '<a href="/admin/routeplan/trip/{}/change/">{} ({})</a>',
            obj.trip.route_plan_id, obj.trip.trip_date, direction
        )
    trip_info.short_description = "Trip"
    trip_info.admin_order_field = "trip__trip_date"
    
    def attendance_status(self, obj):
        """Display attendance status with color coding"""
        if obj.presence:
            return format_html(
                '<span style="color: green; font-weight: bold;">Present</span>'
            )
        else:
            return format_html(
                '<span style="color: red; font-weight: bold;">Absent</span>'
            )
    attendance_status.short_description = "Status"
    attendance_status.admin_order_field = "presence"
    
    def marked_by_user(self, obj):
        """Format the user who marked attendance"""
        if obj.marked_by:
            return format_html(
                '<a href="/admin/auth/user/{}/change/">{}</a>',
                obj.marked_by.id, obj.marked_by.username
            )
        return "-"
    marked_by_user.short_description = "Marked By"
    marked_by_user.admin_order_field = "marked_by__username"
    
    def mark_selected_present(self, request, queryset):
        """Admin action to mark selected attendance records as present"""
        updated = queryset.update(presence=True)
        self.message_user(request, f"{updated} attendance records were marked as present.")
    mark_selected_present.short_description = "Mark selected students as present"
    
    def mark_selected_absent(self, request, queryset):
        """Admin action to mark selected attendance records as absent"""
        updated = queryset.update(presence=False)
        self.message_user(request, f"{updated} attendance records were marked as absent.")
    mark_selected_absent.short_description = "Mark selected students as absent"
    
    def get_queryset(self, request):
        """Optimize queryset by prefetching related objects"""
        queryset = super().get_queryset(request)
        return queryset.select_related('student', 'trip', 'marked_by')