from django.db import models
import uuid

class Attendance(models.Model):
    """
    Attendance model to track student presence for each day.
    Records whether a student was present on a specific date.
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
    
    # Date of attendance
    date = models.DateField(
        help_text="Date of attendance record"
    )
    
    # Presence status
    presence = models.BooleanField(
        default=True,
        help_text="Whether the student was present on this day"
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
    
    class Meta:
        verbose_name = "Attendance Record"
        verbose_name_plural = "Attendance Records"
        unique_together = ['student', 'date']  # One attendance record per student per day
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['student', 'date']),
        ]
    
    def __str__(self):
        status = "Present" if self.presence else "Absent"
        return f"{self.student.name} - {status} - {self.date}"
    
    @classmethod
    def mark_student_present(cls, student_id, date, user=None):
        """
        Mark a student as present for a specific date
        
        Args:
            student_id: UUID of the student
            date: Date to mark attendance for
            user: User who is marking attendance
        """
        from students.models import Student
        
        try:
            student = Student.objects.get(student_id=student_id)
            
            attendance, created = cls.objects.get_or_create(
                student=student,
                date=date,
                defaults={
                    'presence': True,
                    'marked_by': user
                }
            )
            
            if not created:
                # Update existing record
                attendance.presence = True
                attendance.marked_by = user
                attendance.save()
            
            return attendance
        except Student.DoesNotExist:
            return None