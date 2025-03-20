from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from core.permissions import IsOwnerOrAdmin, IsDriverOrAdmin
from .models import Driver
from .serializers import (
    DriverSerializer, 
    DriverListSerializer, 
    DriverCreateUpdateSerializer,
    DriverLocationSerializer
)

class DriverListView(generics.ListAPIView):
    """
    List all drivers. Full list is only accessible to admins.
    For drivers, only shows their own profile.
    """
    serializer_class = DriverListSerializer
    permission_classes = [IsAuthenticated, IsDriverOrAdmin]
    
    def get_queryset(self):
        # For admins, return all drivers
        if self.request.user.is_staff:
            return Driver.objects.all()
            
        # For drivers, return only their own profile
        if hasattr(self.request, 'auth') and self.request.auth:
            associated_id = self.request.auth.payload.get('associated_id')
            if associated_id:
                return Driver.objects.filter(driver_id=associated_id)
                
        return Driver.objects.none()

class DriverDetailView(generics.RetrieveAPIView):
    """
    Retrieve details for a specific driver.
    Drivers can only access their own details.
    Admins can access any driver's details.
    """
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer
    lookup_field = 'driver_id'
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    owner_id_field = 'driver_id'  # Tell permission class which field to check

class DriverCreateView(generics.CreateAPIView):
    """
    Create a new driver. Only accessible to admins.
    """
    queryset = Driver.objects.all()
    serializer_class = DriverCreateUpdateSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

class DriverUpdateView(generics.UpdateAPIView):
    """
    Update a driver's details. Only accessible to admins.
    """
    queryset = Driver.objects.all()
    serializer_class = DriverCreateUpdateSerializer
    lookup_field = 'driver_id'
    permission_classes = [IsAuthenticated, IsAdminUser]

class DriverLocationUpdateView(generics.UpdateAPIView):
    """
    Update a driver's location in real-time.
    Drivers can only update their own location.
    """
    queryset = Driver.objects.all()
    serializer_class = DriverLocationSerializer
    lookup_field = 'driver_id'
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    owner_id_field = 'driver_id'