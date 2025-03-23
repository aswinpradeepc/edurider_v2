from django.contrib import admin
from django.utils.html import format_html
from .models import Attendance

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student_name', 'date', 'attendance_status')
    list_filter = ('date', 'presence')
    search_fields = ('student__name', 'date')
    date_hierarchy = 'date'
    raw_id_fields = ('student',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('student', 'date', 'presence')
        }),
    )
    
    def student_name(self, obj):
        """Display student name with link"""
        return format_html(
            '<a href="/admin/students/student/{}/change/">{}</a>',
            obj.student.student_id, obj.student.name
        )
    student_name.short_description = "Student"
    student_name.admin_order_field = "student__name"
    
    def attendance_status(self, obj):
        """Display attendance status with color coding"""
        if obj.presence:
            return format_html(
                '<span style="color: green;">Present</span>'
            )
        return format_html(
            '<span style="color: red;">Absent</span>'
        )
    attendance_status.short_description = "Status"
    
    def get_queryset(self, request):
        """Optimize queryset by prefetching related objects"""
        return super().get_queryset(request).select_related('student')