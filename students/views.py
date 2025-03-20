from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from core.permissions import IsOwnerOrAdmin, IsGuardianOrAdmin
from .models import Student
from .serializers import (
    StudentSerializer, 
    StudentListSerializer, 
    StudentCreateUpdateSerializer,
    StudentLocationSerializer
)

class StudentListView(generics.ListAPIView):
    """
    List all students. Only accessible to admins.
    For guardians, only shows their associated student.
    """
    serializer_class = StudentListSerializer
    permission_classes = [IsAuthenticated, IsGuardianOrAdmin]
    
    def get_queryset(self):
        # For admins, return all students
        if self.request.user.is_staff:
            return Student.objects.all()
            
        # For guardians, return only their associated student
        if hasattr(self.request, 'auth') and self.request.auth:
            associated_id = self.request.auth.payload.get('associated_id')
            if associated_id:
                return Student.objects.filter(student_id=associated_id)
                
        return Student.objects.none()

class StudentDetailView(generics.RetrieveAPIView):
    """
    Retrieve details for a specific student.
    Parents can only access their own student's details.
    Admins can access any student's details.
    """
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    lookup_field = 'student_id'
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    owner_id_field = 'student_id'  # Tell permission class which field to check

class StudentCreateView(generics.CreateAPIView):
    """
    Create a new student. Only accessible to admins.
    """
    queryset = Student.objects.all()
    serializer_class = StudentCreateUpdateSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

class StudentUpdateView(generics.UpdateAPIView):
    """
    Update a student's details. Only accessible to admins.
    """
    queryset = Student.objects.all()
    serializer_class = StudentCreateUpdateSerializer
    lookup_field = 'student_id'
    permission_classes = [IsAuthenticated, IsAdminUser]

class StudentLocationUpdateView(generics.UpdateAPIView):
    """
    Update a student's location. Only accessible to the student's guardian or admins.
    """
    queryset = Student.objects.all()
    serializer_class = StudentLocationSerializer
    lookup_field = 'student_id'
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    owner_id_field = 'student_id'