# backend/config/settings.py
import os
from pathlib import Path
import environ as django_environ  # Using alias to avoid conflict

# Initialize environment variables
BASE_DIR = Path(__file__).parent.parent

# Create env instance and load .env file
env = django_environ.Env()
django_environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# Build paths inside the project like this: BASE_DIR / 'subdir'.
# BASE_DIR is already defined above

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/    

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('DJANGO_SECRET_KEY', default='fallback-secret-key-for-dev')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DJANGO_DEBUG', default=True)

# Allowed hosts
ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS', default=['localhost', '127.0.0.1'])

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party apps
    'rest_framework',          # Django REST Framework
    'drf_spectacular',         # For API documentation
    'django_filters',          # For filtering API results
    'corsheaders',             # For handling Cross-Origin Resource Sharing
    
    # Local apps
    'users.apps.UsersConfig',  # Custom user app
    'core.apps.CoreConfig',    # Core app with shared models
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # CORS middleware
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/ #databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST'),
        'PORT': env('DB_PORT'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/ #auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/ 
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Bangkok'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/ 
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/ #default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'users.CustomUser'

# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'users.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}

# DRF Spectacular Configuration (for API docs)
SPECTACULAR_SETTINGS = {
    'TITLE': 'Django React Auth Project API',
    'DESCRIPTION': 'API documentation for the Django + React authentication project',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

# CORS Settings
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
]

# CSRF Trusted Origins
CSRF_TRUSTED_ORIGINS = ["http://localhost:3000"]

# JWT Settings
JWT_AUTH = {
    'JWT_ACCESS_TOKEN_EXPIRATION': env.int('JWT_ACCESS_TOKEN_EXPIRATION', default=300),  # 5 minutes
    'JWT_REFRESH_TOKEN_EXPIRATION': env.int('JWT_REFRESH_TOKEN_EXPIRATION', default=86400),  # 24 hours
    'JWT_COOKIE_SAMESITE': env('JWT_COOKIE_SAMESITE', default='Lax'),
    'JWT_COOKIE_SECURE': env.bool('JWT_COOKIE_SECURE', default=False),
    'JWT_CSRF_PROTECTION': env.bool('JWT_CSRF_PROTECTION', default=True),
    'JWT_CSRF_HEADER_NAME': env('JWT_CSRF_HEADER_NAME', default='X-CSRFToken'),
    'JWT_CSRF_COOKIE_NAME': env('JWT_CSRF_COOKIE_NAME', default='csrftoken'),
    'JWT_BLACKLIST_ENABLED': env.bool('JWT_BLACKLIST_ENABLED', default=True),
    'JWT_BLACKLIST_TTL': env.int('JWT_BLACKLIST_TTL', default=86400),
}

# Email Settings
EMAIL_BACKEND = env('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
if EMAIL_BACKEND == 'django.core.mail.backends.smtp.EmailBackend':
    EMAIL_HOST = env('EMAIL_HOST')
    EMAIL_PORT = env.int('EMAIL_PORT')
    EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS')
    EMAIL_HOST_USER = env('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')

# Rate limiting
REVIEW_RATE_LIMIT = '5/m'
SIGNUP_RATE_LIMIT = '5/h'