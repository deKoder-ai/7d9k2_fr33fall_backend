# backend/users/views.py
from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.conf import settings
from .models import CustomUser, EmailVerificationToken, PasswordResetToken, BlacklistedToken
from .serializers import (
    UserSerializer, 
    RegisterSerializer, 
    LoginSerializer, 
    PasswordResetRequestSerializer,
    PasswordResetSerializer,
    EmailVerificationSerializer
)
from .authentication import JWTAuthentication, create_jwt_pair

class AuthViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny]
    
    def get_serializer_class(self):
        if self.action == 'login':
            return LoginSerializer
        elif self.action == 'register':
            return RegisterSerializer
        return UserSerializer
        
    def login(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        access_token, refresh_token = create_jwt_pair(user)
        
        response = Response({
            'user': UserSerializer(user).data,
            'message': 'Login successful'
        })
        
        # Set refresh token in httpOnly cookie
        response.set_cookie(
            key='refresh_token',
            value=refresh_token,
            httponly=True,
            secure=settings.JWT_AUTH['JWT_COOKIE_SECURE'],
            samesite=settings.JWT_AUTH['JWT_COOKIE_SAMESITE'],
            max_age=settings.JWT_AUTH['JWT_REFRESH_TOKEN_EXPIRATION']
        )
        
        return response
        
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Create verification token
        token = get_random_string(64)
        EmailVerificationToken.objects.create(
            user=user,
            token=token,
            expires_at=timezone.now() + timedelta(hours=24)
        )
        
        # Send verification email
        verification_url = f"{settings.FRONTEND_URL}/verify-email/{token}"
        send_mail(
            'Verify your email',
            f'Please click the following link to verify your email: {verification_url}',
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )
        
        return Response({
            'message': 'Registration successful. Please check your email to verify your account.'
        }, status=status.HTTP_201_CREATED)
        
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        access_token = request.COOKIES.get('access_token')
        refresh_token = request.COOKIES.get('refresh_token')
        
        if access_token:
            BlacklistedToken.objects.create(
                token=access_token,
                expires_at=datetime.fromtimestamp(jwt.decode(access_token, options={'verify_signature': False})['exp'])
            )
            
        if refresh_token:
            BlacklistedToken.objects.create(
                token=refresh_token,
                expires_at=datetime.fromtimestamp(jwt.decode(refresh_token, options={'verify_signature': False})['exp'])
            )
            
        response = Response({'message': 'Logout successful'})
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        return response
        
    @action(detail=False, methods=['post'])
    def refresh_token(self, request):
        refresh_token = request.COOKIES.get('refresh_token')
        
        if not refresh_token:
            return Response({'error': 'Refresh token not found'}, status=status.HTTP_401_UNAUTHORIZED)
            
        try:
            payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return Response({'error': 'Refresh token expired'}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.DecodeError:
            return Response({'error': 'Invalid refresh token'}, status=status.HTTP_401_UNAUTHORIZED)
            
        user_id = payload['user_id']
        try:
            user = CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
            
        access_token, _ = create_jwt_pair(user)
        
        response = Response({'message': 'Token refreshed'})
        response.set_cookie(
            key='access_token',
            value=access_token,
            httponly=True,
            secure=settings.JWT_AUTH['JWT_COOKIE_SECURE'],
            samesite=settings.JWT_AUTH['JWT_COOKIE_SAMESITE'],
            max_age=settings.JWT_AUTH['JWT_ACCESS_TOKEN_EXPIRATION']
        )
        return response

class PasswordResetViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny]
    
    def get_serializer_class(self):
        if self.action == 'request_reset':
            return PasswordResetRequestSerializer
        return PasswordResetSerializer
        
    def request_reset(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response({'message': 'If this email exists in our system, you will receive a reset link'})
            
        # Generate token and send email
        token = get_random_string(64)
        expires_at = timezone.now() + timedelta(hours=6)
        
        PasswordResetToken.objects.update_or_create(
            user=user,
            defaults={'token': token, 'expires_at': expires_at}
        )
        
        reset_url = f"{settings.FRONTEND_URL}/reset-password/{token}"
        send_mail(
            'Password Reset Request',
            f'Please click the following link to reset your password: {reset_url}\nThis link will expire in 6 hours.',
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )
        
        return Response({'message': 'If this email exists in our system, you will receive a reset link'})
        
    def reset_password(self, request, token=None):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            reset_token = PasswordResetToken.objects.get(token=token)
        except PasswordResetToken.DoesNotExist:
            return Response({'error': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)
            
        if timezone.now() > reset_token.expires_at:
            return Response({'error': 'Token has expired'}, status=status.HTTP_400_BAD_REQUEST)
            
        user = reset_token.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        reset_token.delete()
        
        # Invalidate existing tokens
        access_token = request.COOKIES.get('access_token')
        refresh_token = request.COOKIES.get('refresh_token')
        
        BlacklistedToken.objects.create(
            token=access_token,
            expires_at=datetime.fromtimestamp(jwt.decode(access_token, options={'verify_signature': False})['exp'])
        )
        BlacklistedToken.objects.create(
            token=refresh_token,
            expires_at=datetime.fromtimestamp(jwt.decode(refresh_token, options={'verify_signature': False})['exp'])
        )
        
        return Response({'message': 'Password successfully reset'})

class EmailVerificationView(generics.GenericAPIView):
    serializer_class = EmailVerificationSerializer
    permission_classes = [AllowAny]
    
    def post(self, request, token=None):
        try:
            verification_token = EmailVerificationToken.objects.get(token=token)
        except EmailVerificationToken.DoesNotExist:
            return Response({'error': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)
            
        if timezone.now() > verification_token.expires_at:
            return Response({'error': 'Token has expired'}, status=status.HTTP_400_BAD_REQUEST)
            
        user = verification_token.user
        user.is_email_verified = True
        user.save()
        
        verification_token.delete()
        
        return Response({'message': 'Email successfully verified'})

class CurrentUserView(generics.RetrieveAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user