from django.urls import path
from . import views

urlpatterns = [
    path('', views.DriverListView.as_view(), name='driver-list'),
    path('create/', views.DriverCreateView.as_view(), name='driver-create'),
    path('<uuid:driver_id>/', views.DriverDetailView.as_view(), name='driver-detail'),
    path('<uuid:driver_id>/update/', views.DriverUpdateView.as_view(), name='driver-update'),
    path('<uuid:driver_id>/location/', views.DriverLocationUpdateView.as_view(), name='driver-location'),
]