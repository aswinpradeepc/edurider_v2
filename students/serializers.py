from rest_framework import serializers
from .models import Student
from django.contrib.gis.geos import Point

class StudentLocationSerializer(serializers.Serializer):
    """
    Serializer for updating student location coordinates
    """
    longitude = serializers.FloatField()
    latitude = serializers.FloatField()
    
    def update(self, instance, validated_data):
        lon = validated_data.get('longitude')
        lat = validated_data.get('latitude')
        instance.update_coordinates(lon, lat)
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

class StudentListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for listing students
    """
    class_grade_display = serializers.CharField(source='get_class_grade_display', read_only=True)
    
    class Meta:
        model = Student
        fields = [
            'student_id', 'name', 'class_grade', 'class_grade_display', 
            'guardian_name', 'is_active'
        ]

class StudentCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating students with validation
    """
    longitude = serializers.FloatField(write_only=True, required=False)
    latitude = serializers.FloatField(write_only=True, required=False)
    
    class Meta:
        model = Student
        fields = [
            'name', 'class_grade', 'phone_number', 'email', 
            'address_text', 'longitude', 'latitude', 'guardian_name', 
            'route_plan', 'is_active'
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
        
        # Create student instance
        student = Student.objects.create(**validated_data)
        
        # Set coordinates if provided
        if lon is not None and lat is not None:
            student.coordinates = Point(lon, lat)
            student.save(update_fields=['coordinates'])
            
        return student
    
    def update(self, instance, validated_data):
        # Extract coordinate data
        lon = validated_data.pop('longitude', None)
        lat = validated_data.pop('latitude', None)
        
        # Update instance fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Update coordinates if provided
        if lon is not None and lat is not None:
            instance.coordinates = Point(lon, lat)
            
        instance.save()
        return instance