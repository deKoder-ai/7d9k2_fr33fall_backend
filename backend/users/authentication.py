# backend/users/authentication.py
import jwt
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import CustomUser, BlacklistedToken

def create_jwt_pair(user):
    """
    Create a pair of tokens: access and refresh
    Access token is short-lived, refresh token is longer-lived
    """
    payload = {
        'user_id': str(user.id),
        'exp': datetime.utcnow() + timedelta(seconds=settings.JWT_AUTH['JWT_ACCESS_TOKEN_EXPIRATION']),
        'iat': datetime.utcnow(),
    }
    
    access_token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    refresh_token = jwt.encode({
        **payload,
        'exp': datetime.utcnow() + timedelta(seconds=settings.JWT_REFRESH_TOKEN_EXPIRATION)
    }, settings.SECRET_KEY, algorithm='HS256')
    
    return access_token, refresh_token


class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        access_token = request.COOKIES.get('access_token')
        
        if not access_token:
            return None
            
        try:
            payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Access token expired')
        except jwt.DecodeError:
            raise AuthenticationFailed('Invalid token')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid token')
            
        if BlacklistedToken.objects.filter(token=access_token).exists():
            raise AuthenticationFailed('Token has been blacklisted')
            
        user_id = payload['user_id']
        
        try:
            user = CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            raise AuthenticationFailed('User not found')
            
        if not user.is_active:
            raise AuthenticationFailed('User is inactive')
            
        if payload['exp'] < int(timezone.now().timestamp()):
            raise AuthenticationFailed('Access token expired')
            
        return (user, None)
        
    def authenticate_header(self, request):
        return 'Bearer'