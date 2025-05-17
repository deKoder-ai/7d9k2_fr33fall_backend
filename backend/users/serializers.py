# backend/users/serializers.py
from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import CustomUser, EmailVerificationToken, PasswordResetToken

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'is_email_verified', 'is_active', 'date_of_birth']

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'})
    
    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        
        if email and password:
            user = authenticate(username=email, password=password)
            
            if user is None:
                raise serializers.ValidationError('Incorrect email or password')
                
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
                
            if not user.is_email_verified:
                raise serializers.ValidationError('Email address not verified')
                
        return data

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    confirm_password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    
    class Meta:
        model = CustomUser
        fields = ['email', 'password', 'confirm_password']
        
    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
            
        return data
        
    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = CustomUser.objects.create_user(**validated_data, is_active=True)
        return user

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    
class PasswordResetSerializer(serializers.Serializer):
    new_password = serializers.CharField(min_length=8, style={'input_type': 'password'})
    confirm_password = serializers.CharField(style={'input_type': 'password'})
    
    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
            
        return data

class EmailVerificationSerializer(serializers.Serializer):
    pass