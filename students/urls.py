from django.urls import path
from . import views

urlpatterns = [
    path('', views.StudentListView.as_view(), name='student-list'),
    path('create/', views.StudentCreateView.as_view(), name='student-create'),
    path('<uuid:student_id>/', views.StudentDetailView.as_view(), name='student-detail'),
    path('<uuid:student_id>/update/', views.StudentUpdateView.as_view(), name='student-update'),
    path('<uuid:student_id>/location/', views.StudentLocationUpdateView.as_view(), name='student-location'),
]