from django.urls import path
from . import views

urlpatterns = [
    path('<uuid:student_id>/', views.StudentDetailView.as_view(), name='student-detail'),
    path('<uuid:student_id>/location/', views.StudentLocationUpdateView.as_view(), name='student-location'),
]