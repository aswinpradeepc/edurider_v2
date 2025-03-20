import requests
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from core.permissions import IsOwnerOrAdmin
from .models import Student
from .serializers import StudentSerializer, StudentLocationSerializer
from rest_framework.response import Response
from rest_framework import status

class StudentDetailView(generics.RetrieveAPIView):
    """
    Retrieve details for a specific student.
    Parents can only access their own student's details.
    """
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    lookup_field = 'student_id'
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    owner_id_field = 'student_id'  # Tell permission class which field to check

class StudentLocationUpdateView(generics.GenericAPIView):
    """
    Update a student's location. Only accessible to the student's guardian.
    """
    queryset = Student.objects.all()
    serializer_class = StudentLocationSerializer
    lookup_field = 'student_id'
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    owner_id_field = 'student_id'

    def post(self, request, *args, **kwargs):
        """
        Update the student's location using a Google Maps short URL.
        """
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        google_maps_url = serializer.validated_data.get('google_maps_url')
        
        if not google_maps_url:
            return Response({'error': 'Google Maps URL is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Fetch the actual URL from the short URL
        try:
            response = requests.get(google_maps_url, allow_redirects=False)
            actual_url = response.headers['Location']
        except Exception as e:
            return Response({'error': 'Failed to fetch the actual URL from the short URL'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Extract coordinates from the actual URL
        try:
            # Example URL: https://www.google.com/maps/place/CUSAT+Student+Amenity+Centre/@10.0425759,76.3259579,17z/data=!3m1!4b1!4m6!3m5!1s0x3b080c37738769d3:0x5ef54323a29bcbfb!8m2!3d10.0425759!4d76.3285328!16s%2Fg%2F1tgf1n9l?entry=ttu&g_ep=EgoyMDI1MDMxOC4wIKXMDSoASAFQAw%3D%3D
            coordinates = actual_url.split('@')[1].split(',')[:2]
            latitude = float(coordinates[0])
            longitude = float(coordinates[1])
        except Exception as e:
            return Response({'error': 'Failed to extract coordinates from the URL'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Update the student's location
        instance.update_coordinates(longitude, latitude)
        return Response({'success': 'Location updated successfully'}, status=status.HTTP_200_OK)