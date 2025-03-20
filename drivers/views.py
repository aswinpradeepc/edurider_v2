from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from core.permissions import IsOwnerOrAdmin
from .models import Driver
from .serializers import DriverSerializer, DriverLocationSerializer
from rest_framework.response import Response
from rest_framework import status

class DriverDetailView(generics.RetrieveAPIView):
    """
    Retrieve details for a specific driver.
    Drivers can only access their own details.
    """
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer
    lookup_field = 'driver_id'
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    owner_id_field = 'driver_id'

class DriverLocationUpdateView(generics.GenericAPIView):
    """
    Update a driver's location in real-time.
    Drivers can only update their own location.
    """
    queryset = Driver.objects.all()
    serializer_class = DriverLocationSerializer
    lookup_field = 'driver_id'
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    owner_id_field = 'driver_id'

    def patch(self, request, *args, **kwargs):
        """
        Partially update the driver's location.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)