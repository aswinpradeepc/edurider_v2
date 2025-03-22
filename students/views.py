import requests
from django.contrib.gis.geos import Point
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from core.permissions import IsOwnerOrAdmin
from .models import Student
from .serializers import StudentSerializer, StudentLocationSerializer, StudentLocationCoordinatesSerializer

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
        
        # Expand the short URL
        try:
            response = requests.head(google_maps_url, allow_redirects=True)
            expanded_url = response.url
        except Exception as e:
            return Response({'error': 'Failed to expand the Google Maps URL'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Extract coordinates from the expanded URL
        try:
            # Example expanded URL: https://www.google.com/maps/place/37.7749,-122.4194
            if '@' in expanded_url:
                coordinates = expanded_url.split('@')[1].split(',')[:2]
            elif '/place/' in expanded_url:
                coordinates = expanded_url.split('/place/')[1].split(',')[:2]
            elif '/maps?q=' in expanded_url:
                coordinates = expanded_url.split('/maps?q=')[1].split(',')[:2]
            else:
                raise ValueError('Unsupported URL format')
            
            latitude = float(coordinates[0])
            longitude = float(coordinates[1])
        except Exception as e:
            return Response({'error': 'Failed to extract coordinates from the URL'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Update the student's location
        instance.current_location = Point(longitude, latitude)
        instance.save(update_fields=['current_location'])
        
        return Response({'success': 'Location updated successfully'}, status=status.HTTP_200_OK)


class StudentLocationCoordinatesUpdateView(generics.GenericAPIView):
    """
    Update a student's location using latitude and longitude.
    Only accessible to the student's guardian.
    """
    queryset = Student.objects.all()
    serializer_class = StudentLocationCoordinatesSerializer
    lookup_field = 'student_id'
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    owner_id_field = 'student_id'

    def post(self, request, *args, **kwargs):
        """
        Update the student's location using latitude and longitude.
        """
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        latitude = serializer.validated_data.get('latitude')
        longitude = serializer.validated_data.get('longitude')
        
        # Update the student's location
        instance.coordinates = Point(longitude, latitude)
        instance.save(update_fields=['coordinates'])
        
        return Response({'success': 'Location updated successfully'}, status=status.HTTP_200_OK)