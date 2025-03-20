from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import ParentGoogleLoginView, DriverGoogleLoginView, GoogleCallbackView, LogoutView, UserProfileView

urlpatterns = [
    # Separate endpoints for parent and driver login
    path('parent/google-login/', ParentGoogleLoginView.as_view(), name='parent_google_login'),
    path('driver/google-login/', DriverGoogleLoginView.as_view(), name='driver_google_login'),
    path('google/callback/', GoogleCallbackView.as_view(), name='google_callback'),
    path('logout/', LogoutView.as_view(), name='auth_logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', UserProfileView.as_view(), name='user_profile'),
]