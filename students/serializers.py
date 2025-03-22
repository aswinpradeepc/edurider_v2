from rest_framework import serializers
from .models import Student
from django.contrib.gis.geos import Point

class StudentLocationSerializer(serializers.Serializer):
    """
    Serializer for updating student location using a Google Maps short URL
    """
    google_maps_url = serializers.URLField()

    def update(self, instance, validated_data):
        google_maps_url = validated_data.get('google_maps_url')
        # The actual update logic will be handled in the view
        return instance

class StudentSerializer(serializers.ModelSerializer):
    """
    Main serializer for Student model with all fields
    """
    # Convert Point object to readable format
    coordinates = serializers.SerializerMethodField()
    # Get display value for class grade
    class_grade_display = serializers.CharField(source='get_class_grade_display', read_only=True)
    
    class Meta:
        model = Student
        fields = [
            'student_id', 'name', 'class_grade', 'class_grade_display', 
            'phone_number', 'email', 'address_text', 'coordinates',
            'location_updated_at', 'guardian_name', 'route_plan',
            'created_at', 'updated_at', 'is_active'
        ]
        read_only_fields = ['student_id', 'created_at', 'updated_at']
    
    def get_coordinates(self, obj):
        """
        Convert the GeoDjango Point object to a simple lon/lat dictionary
        """
        if obj.coordinates:
            return {
                'longitude': obj.coordinates.x,
                'latitude': obj.coordinates.y
            }
        return None

class StudentLocationCoordinatesSerializer(serializers.Serializer):
    """
    Serializer for updating student location using latitude and longitude
    """
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()