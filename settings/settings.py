from pathlib import Path
import os
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-z_0%de1dkr=hfj%d_98dtxnvyb9+4^vi6&jh067msqr0@^r74q'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
if DEBUG:
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

ALLOWED_HOSTS = []

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt.token_blacklist',
    'rest_framework.authtoken',
    'corsheaders',  # Allow Cross-Origin Requests
    'courses',
    'organisations',
    'users',
    'mermaid_model',
    'discussions',
    'ytlive',
    'live_chat',  # Newly added app for real-time chat
    'channels',   # Added for WebSocket support
]

# Reference your custom User model
AUTH_USER_MODEL = 'users.User'

# Rest Framework and SimpleJWT settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',  # Enforce default permissions
    ],
}

# Configure SimpleJWT
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),  # Short-lived access token
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),  # Longer-lived refresh token
    'ROTATE_REFRESH_TOKENS': True,  # Issue a new refresh token when used
    'BLACKLIST_AFTER_ROTATION': True,  # Blacklist old refresh tokens
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'exp',
}

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # Allow cross-origin requests
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'settings.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

# WSGI replaced with ASGI for WebSocket support
ASGI_APPLICATION = 'settings.asgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
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
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files
STATIC_URL = '/static/'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'settings/media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS settings for development
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:3002",
    "http://localhost:3003",
]
CORS_ALLOW_CREDENTIALS = True  # Allow cookies for cross-origin requests

# CSRF settings for frontend compatibility
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:3002",
    "http://localhost:3003",
]

# Additional settings for cookies
SESSION_COOKIE_SECURE = not DEBUG  # Secure cookies in production
CSRF_COOKIE_SECURE = not DEBUG

# Redis configuration for Django Channels
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('127.0.0.1', 6379)],  # Redis server details
        },
    },
}

# YouTube API configuration
YOUTUBE_CLIENT_ID = '1024413164093-adjs2lqjht0jaqh200fm07blr2qe285k.apps.googleusercontent.com'
YOUTUBE_CLIENT_SECRET = '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'
YOUTUBE_REDIRECT_URI = 'http://localhost:8000/api/ytlive/oauth2callback/'
YOUTUBE_API_SCOPES = [
    'https://www.googleapis.com/auth/youtube',
    'https://www.googleapis.com/auth/youtube.force-ssl',
]
