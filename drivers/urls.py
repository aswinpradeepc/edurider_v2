from django.urls import path
from . import views

urlpatterns = [
    path('<uuid:driver_id>/', views.DriverDetailView.as_view(), name='driver-detail'),
    path('<uuid:driver_id>/location/', views.DriverLocationUpdateView.as_view(), name='driver-location'),
]