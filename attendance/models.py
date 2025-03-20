from django.db import models
import uuid

class Attendance(models.Model):
    """
    Attendance model to track student presence on bus trips.
    Records whether a student was present on a specific trip.
    """
    # Primary key
    attendance_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="Attendance ID"
    )
    
    # Foreign key to Student
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='attendance_records',
        help_text="Student whose attendance is being recorded"
    )
    
    # Foreign key to Trip (RoutePlan)
    trip = models.ForeignKey(
        'routeplan.Trip',
        on_delete=models.CASCADE,
        related_name='attendance_records',
        help_text="Trip for which attendance is being recorded"
    )
    
    # Date of attendance
    date = models.DateField(
        help_text="Date of attendance record"
    )
    
    # Presence status
    presence = models.BooleanField(
        default=False,
        help_text="Whether the student was present on the trip"
    )
    
    # Additional tracking fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    marked_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='attendance_records_marked',
        help_text="User who marked this attendance record"
    )
    
    def __str__(self):
        status = "Present" if self.presence else "Absent"
        return f"{self.student.name} - {status} - {self.date}"
    
    class Meta:
        verbose_name = "Attendance Record"
        verbose_name_plural = "Attendance Records"
        ordering = ['-date', 'student__name']
        # Ensure a student can only have one attendance record per trip
        unique_together = ['student', 'trip', 'date']
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['presence']),
        ]

    @classmethod
    def mark_student_present(cls, student_id, trip_id, date=None, user=None):
        """
        Mark a student as present for a specific trip
        
        Args:
            student_id: UUID of the student
            trip_id: UUID of the trip
            date: Optional date (defaults to current date)
            user: User who is marking attendance
            
        Returns:
            Created or updated attendance record
        """
        from django.utils import timezone
        from students.models import Student
        from routeplan.models import Trip
        
        if date is None:
            date = timezone.now().date()
            
        try:
            student = Student.objects.get(student_id=student_id)
            trip = Trip.objects.get(route_plan_id=trip_id)
            
            # Get or create attendance record
            attendance, created = cls.objects.update_or_create(
                student=student,
                trip=trip,
                date=date,
                defaults={
                    'presence': True,
                    'marked_by': user
                }
            )
            
            return attendance
        except (Student.DoesNotExist, Trip.DoesNotExist):
            return None

    @classmethod
    def mark_student_absent(cls, student_id, trip_id, date=None, user=None):
        """
        Mark a student as absent for a specific trip
        
        Args:
            student_id: UUID of the student
            trip_id: UUID of the trip
            date: Optional date (defaults to current date)
            user: User who is marking attendance
            
        Returns:
            Created or updated attendance record
        """
        from django.utils import timezone
        from students.models import Student
        from routeplan.models import Trip
        
        if date is None:
            date = timezone.now().date()
            
        try:
            student = Student.objects.get(student_id=student_id)
            trip = Trip.objects.get(route_plan_id=trip_id)
            
            # Get or create attendance record
            attendance, created = cls.objects.update_or_create(
                student=student,
                trip=trip,
                date=date,
                defaults={
                    'presence': False,
                    'marked_by': user
                }
            )
            
            return attendance
        except (Student.DoesNotExist, Trip.DoesNotExist):
            return None