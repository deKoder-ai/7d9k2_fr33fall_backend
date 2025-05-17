# backend/config/urls.py
from django.urls import path, include
from django.contrib import admin
from rest_framework.routers import DefaultRouter
from users.views import AuthViewSet, PasswordResetViewSet, EmailVerificationView
from core.views import CurrentUserView
from django.http import JsonResponse

# Import for DRF Spectacular (API documentation)
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView
)

# API Router
router = DefaultRouter()
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'reset-password', PasswordResetViewSet, basename='password-reset')

def index(request):
    return JsonResponse({
        'message': 'Welcome to the Django React Auth Project',
        'documentation': 'Visit /api/docs/swagger/ for API documentation'
    })

urlpatterns = [
    path('', index),
    path('admin/', admin.site.urls),
    
    # API Routes
    path('api/', include(router.urls)),
    path('api/user/', CurrentUserView.as_view(), name='current-user'),
    path('api/verify-email/<str:token>/', EmailVerificationView.as_view(), name='verify-email'),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/docs/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]