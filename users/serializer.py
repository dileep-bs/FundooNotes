from rest_framework import serializers, status
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework_jwt.utils import jwt_response_payload_handler


class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']


class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class ResetSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['password']


class ForgotSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email']

