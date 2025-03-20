from rest_framework import serializers
from django.contrib.auth.models import User
from allauth.socialaccount.helpers import complete_social_login
from allauth.socialaccount.models import SocialAccount
from rest_framework.exceptions import AuthenticationFailed
from .models import UserProfile
import requests

class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profiles"""
    email = serializers.EmailField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    
    class Meta:
        model = UserProfile
        fields = ('user_type', 'email', 'first_name', 'last_name')
        read_only_fields = fields

class GoogleAuthSerializer(serializers.Serializer):
    """Serializer for Google Auth payload - used for direct token verification"""
    auth_token = serializers.CharField()