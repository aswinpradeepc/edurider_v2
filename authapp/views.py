from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.conf import settings
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.contrib.auth import logout
from students.models import Student
from drivers.models import Driver
from .models import UserProfile
from .serializers import UserProfileSerializer, GoogleAuthSerializer
import requests
import urllib.parse

class ParentGoogleLoginView(APIView):
    """
    Initiate Google OAuth flow for parents/guardians
    This only begins the auth process - verification happens in the callback
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Redirect to Google OAuth with parent flow marker"""
        # Construct Google OAuth URL
        google_auth_url = 'https://accounts.google.com/o/oauth2/auth'
        redirect_uri = f"{settings.BASE_URL}/api/auth/google/callback/"
        
        params = {
            'client_id': settings.GOOGLE_OAUTH2_CLIENT_ID,
            'redirect_uri': redirect_uri,
            'response_type': 'code',
            'scope': 'email profile',
            'access_type': 'online',
            'state': 'parent'  # Mark this as parent flow
        }
        
        auth_url = f"{google_auth_url}?{urllib.parse.urlencode(params)}"
        return Response({'auth_url': auth_url})

class DriverGoogleLoginView(APIView):
    """
    Initiate Google OAuth flow for drivers
    This only begins the auth process - verification happens in the callback
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Redirect to Google OAuth with driver flow marker"""
        # Construct Google OAuth URL
        google_auth_url = 'https://accounts.google.com/o/oauth2/auth'
        redirect_uri = f"{settings.BASE_URL}/api/auth/google/callback/"
        
        params = {
            'client_id': settings.GOOGLE_OAUTH2_CLIENT_ID,
            'redirect_uri': redirect_uri,
            'response_type': 'code',
            'scope': 'email profile',
            'access_type': 'online',
            'state': 'driver'  # Mark this as driver flow
        }
        
        auth_url = f"{google_auth_url}?{urllib.parse.urlencode(params)}"
        return Response({'auth_url': auth_url})

class GoogleCallbackView(APIView):
    """
    Handle Google OAuth callback
    Verifies user is pre-registered, and issues token as JSON response
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Process OAuth callback and validate against pre-registered users"""
        code = request.GET.get('code')
        state = request.GET.get('state')  # 'parent' or 'driver'
        
        if not code:
            return Response({'error': 'Authorization code not provided'}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        # Exchange code for token
        token_url = 'https://oauth2.googleapis.com/token'
        token_data = {
            'code': code,
            'client_id': settings.GOOGLE_OAUTH2_CLIENT_ID,
            'client_secret': settings.GOOGLE_OAUTH2_CLIENT_SECRET,
            'redirect_uri': f"{settings.BASE_URL}/api/auth/google/callback/",
            'grant_type': 'authorization_code'
        }
        
        token_response = requests.post(token_url, data=token_data)
        if not token_response.ok:
            return Response({'error': 'Failed to obtain access token'}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        access_token = token_response.json().get('access_token')
        
        # Get user info from Google
        user_info_url = 'https://www.googleapis.com/oauth2/v3/userinfo'
        user_info_response = requests.get(
            user_info_url, 
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        if not user_info_response.ok:
            return Response({'error': 'Failed to get user info'}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        user_info = user_info_response.json()
        email = user_info.get('email')
        
        if not email:
            return Response({'error': 'Email not provided by Google'}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user is pre-registered based on the flow (parent or driver)
        if state == 'parent':
            # Check if email matches any student's email
            student = Student.objects.filter(email=email).first()
            if not student:
                return Response({
                    'error': 'Unauthorized. Your email is not registered as a student contact.'
                }, status=status.HTTP_403_FORBIDDEN)
            
            user_type = 'guardian'
            associated_id = str(student.student_id)
            
        elif state == 'driver':
            # Check if email matches any driver's email
            driver = Driver.objects.filter(email=email).first()
            if not driver:
                return Response({
                    'error': 'Unauthorized. Your email is not registered as a driver.'
                }, status=status.HTTP_403_FORBIDDEN)
            
            user_type = 'driver'
            associated_id = str(driver.driver_id)
            
        else:
            return Response({'error': 'Invalid authentication flow'}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        # Check if this user has a Django user account
        # If not, create one based on the pre-registered email
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Auto-create a Django user account, but only for pre-verified emails
            user = User.objects.create(
                username=email,
                email=email,
                first_name=user_info.get('given_name', ''),
                last_name=user_info.get('family_name', ''),
                is_active=True
            )
            
            # Create the user profile right away
            UserProfile.objects.create(
                user=user,
                user_type=user_type
            )
        
        # Update or get user profile
        profile, created = UserProfile.objects.update_or_create(
            user=user,
            defaults={'user_type': user_type}
        )
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        # Add custom claims
        refresh['user_type'] = user_type
        refresh['associated_id'] = associated_id
        
        # Instead of redirecting, return the tokens as JSON
        return Response({
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'user_type': user_type,
                'associated_id': associated_id
            }
        })

class LogoutView(APIView):
    """
    Logout endpoint - blacklist the refresh token
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            return Response({'success': 'Successfully logged out'}, status=status.HTTP_200_OK)
        except TokenError:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(generics.RetrieveAPIView):
    """View for retrieving user profile information"""
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer
    
    def get_object(self):
        """Get the profile for the logged-in user"""
        try:
            return UserProfile.objects.get(user=self.request.user)
        except UserProfile.DoesNotExist:
            return None