import os
import sys
import django
import calendar
from datetime import datetime

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.utils import timezone
from students.models import Student
from attendance.models import Attendance

def mark_monthly_attendance(year, month):
    """
    Mark attendance for all students for a given month.
    Creates attendance records for each day.
    Skips weekends (Saturday and Sunday).
    
    Args:
        year (int): Year to mark attendance for
        month (int): Month to mark attendance for (1-12)
    """
    # Get all active students
    students = list(Student.objects.filter(is_active=True))
    if not students:
        print("No active students found!")
        return

    total_students = len(students)
    print(f"Found {total_students} active students")
    
    # Get the number of days in the month
    num_days = calendar.monthrange(year, month)[1]
    
    # Process each day
    for day in range(1, num_days + 1):
        date = datetime(year, month, day).date()
        
        # Skip weekends
        if date.weekday() >= 5:  # 5 is Saturday, 6 is Sunday
            continue
            
        print(f"\nProcessing attendance for {date}...")
        
        # Mark attendance for each student
        for student in students:
            Attendance.mark_student_present(
                student_id=student.student_id,
                date=date
            )
        
        print(f"✓ Marked {total_students} students present for {date}")

if __name__ == "__main__":
    # Get current year and month if not provided
    current_date = timezone.now()
    year = current_date.year
    month = current_date.month
    
    if len(sys.argv) > 2:
        year = int(sys.argv[1])
        month = int(sys.argv[2])
    
    print(f"Marking attendance for {calendar.month_name[month]} {year}")
    mark_monthly_attendance(year, month)
    print("\nCompleted marking attendance for all students!")
