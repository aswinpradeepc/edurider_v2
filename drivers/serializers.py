from rest_framework import serializers
from .models import Driver
from django.contrib.gis.geos import Point
from django.utils import timezone

class DriverLocationSerializer(serializers.Serializer):
    """
    Serializer for updating driver location in real-time
    """
    longitude = serializers.FloatField()
    latitude = serializers.FloatField()
    
    def update(self, instance, validated_data):
        lon = validated_data.get('longitude')
        lat = validated_data.get('latitude')
        
        # Update driver location
        instance.current_location = Point(lon, lat)
        instance.location_updated_at = timezone.now()
        instance.save(update_fields=['current_location', 'location_updated_at'])
        return instance

class DriverSerializer(serializers.ModelSerializer):
    """
    Main serializer for Driver model with all fields
    """
    # Convert Point object to readable format
    current_location = serializers.SerializerMethodField()
    
    class Meta:
        model = Driver
        fields = [
            'driver_id', 'name', 'licence_no', 'phone_number', 
            'email', 'bus_no', 'current_location', 'location_updated_at'
        ]
        read_only_fields = ['driver_id', 'location_updated_at']
    
    def get_current_location(self, obj):
        """
        Convert the GeoDjango Point object to a simple lon/lat dictionary
        """
        if obj.current_location:
            return {
                'longitude': obj.current_location.x,
                'latitude': obj.current_location.y
            }
        return None