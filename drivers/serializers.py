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

class DriverListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for listing drivers
    """
    class Meta:
        model = Driver
        fields = [
            'driver_id', 'name', 'bus_no'
        ]

class DriverCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating drivers with validation
    """
    longitude = serializers.FloatField(write_only=True, required=False)
    latitude = serializers.FloatField(write_only=True, required=False)
    
    class Meta:
        model = Driver
        fields = [
            'name', 'licence_no', 'phone_number', 'email', 
            'bus_no', 'longitude', 'latitude'
        ]
    
    def validate(self, data):
        """
        Validate that both longitude and latitude are provided together
        """
        lon = data.get('longitude')
        lat = data.get('latitude')
        if (lon is not None and lat is None) or (lon is None and lat is not None):
            raise serializers.ValidationError(
                "Both longitude and latitude must be provided together"
            )
        return data
    
    def create(self, validated_data):
        # Extract coordinate data
        lon = validated_data.pop('longitude', None)
        lat = validated_data.pop('latitude', None)
        
        # Create driver instance
        driver = Driver.objects.create(**validated_data)
        
        # Set coordinates if provided
        if lon is not None and lat is not None:
            driver.current_location = Point(lon, lat)
            driver.location_updated_at = timezone.now()
            driver.save(update_fields=['current_location', 'location_updated_at'])
            
        return driver
    
    def update(self, instance, validated_data):
        # Extract coordinate data
        lon = validated_data.pop('longitude', None)
        lat = validated_data.pop('latitude', None)
        
        # Update instance fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Update coordinates if provided
        if lon is not None and lat is not None:
            instance.current_location = Point(lon, lat)
            instance.location_updated_at = timezone.now()
            
        instance.save()
        return instance