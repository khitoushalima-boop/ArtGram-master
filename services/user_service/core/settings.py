import os
from pathlib import Path
import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Initialize environment variables
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY', default='django-insecure-key-user-service-ArtGram-2026')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DEBUG', default=True)

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['*'])

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party apps
    'rest_framework',
    'corsheaders',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    
    # Local apps
    'accounts',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

# Service Configuration
SERVICE_NAME = env('SERVICE_NAME', default='user-service')
SERVICE_PORT = env('SERVICE_PORT', default='8000')
CONSUL_HOST = env('CONSUL_HOST', default='consul')
CONSUL_PORT = env('CONSUL_PORT', default='8500')

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': '/app/registration.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'accounts': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'registration': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

# URL configuration will be handled in urls.py

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

WSGI_APPLICATION = 'core.wsgi.application'

# Database Configuration - SQLite for local development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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

# Custom User Model
AUTH_USER_MODEL = 'accounts.User'

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS Configuration - Django 4.0+ Compatible
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

# Specific allowed origins (more secure than allowing all)
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8001",   # Gateway port
    "http://127.0.0.1:8001",
    "http://localhost:8003",   # Direct frontend port
    "http://127.0.0.1:8003",
    "http://localhost:3000",   # React/Vue frontend port
    "http://127.0.0.1:3000",   # React/Vue frontend port
]

# Allowed origin patterns for development
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https?://localhost:800[1-3].*$",
    r"^https?://127\.0\.0\.1:800[1-3].*$",
    r"^https?://localhost:3000.*$",
    r"^https?://127\.0\.0\.1:3000.*$",
]

# CSRF Configuration for Django 4.0+ - MUST INCLUDE ALL ORIGINS
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8001",   # Gateway port
    "http://127.0.0.1:8001",
    "http://localhost:8003",   # Direct frontend port  
    "http://127.0.0.1:8003",
    "http://localhost:3000",   # React/Vue frontend port
    "http://127.0.0.1:3000",   # React/Vue frontend port
]
CSRF_COOKIE_SECURE = False  # For development
CSRF_COOKIE_HTTPONLY = False  # Allow JavaScript access
CSRF_COOKIE_SAMESITE = 'Lax'  # Allow same-origin requests

# Additional Django 4.0+ CSRF settings
CSRF_USE_SESSIONS = False
CSRF_COOKIE_HTTPONLY = False

# Authentication Backends
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# JWT Configuration
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': os.environ.get('JWT_SECRET_KEY', 'your-secret-key-change-in-production'),
    'VERIFYING_KEY': os.environ.get('JWT_SECRET_KEY', 'your-secret-key-change-in-production'),
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',
    'AUTH_TOKEN_CLASSES': (
        'rest_framework_simplejwt.tokens.AccessToken',
    ),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

# REST Framework Configuration - Secure but allows public endpoints
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',  # Allow read access for unauthenticated users
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    # Add permission policies for specific endpoints
    'DEFAULT_PERMISSION_POLICY': None,  # Allow view-level permissions to override defaults
}

# RabbitMQ Event Publishing Function
import pika
import json
from django.utils import timezone  # ✅ Fixed missing import

def publish_user_event(event_type, user_data):
    """Publish user-related events to RabbitMQ with enhanced error handling"""
    try:
        # Get RabbitMQ connection details from environment
        rabbitmq_url = os.environ.get('RABBITMQ_URL', 'amqp://guest:guest@rabbitmq:5672/')
        
        # Parse connection parameters
        import urllib.parse
        parsed = urllib.parse.urlparse(rabbitmq_url)
        
        # Establish connection with timeout and retry logic
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=parsed.hostname,
                    port=parsed.port or 5672,
                    virtual_host=parsed.path[1:] if parsed.path else '/',
                    credentials=pika.PlainCredentials(
                        parsed.username or 'guest',
                        parsed.password or 'guest'
                    ),
                    # Note: Some pika versions don't support timeout parameters
                    # connection_timeout=5,  # 5 second timeout
                    # blocked_connection_timeout=5  # 5 second blocked timeout
                )
            )
        except pika.exceptions.AMQPConnectionError as conn_error:
            print(f"❌ RabbitMQ connection failed: {str(conn_error)}")
            return  # Don't crash registration, just skip event publishing
        
        channel = connection.channel()
        
        # Declare exchange
        exchange_name = 'user_events'
        try:
            channel.exchange_declare(exchange=exchange_name, exchange_type='topic', durable=True)
        except pika.exceptions.ChannelClosedByBroker as exchange_error:
            print(f"❌ Failed to declare exchange: {str(exchange_error)}")
            connection.close()
            return
        
        # Create routing key
        routing_key = f'user.{event_type}'
        
        # Publish message
        message = {
            'event_type': event_type,
            'user_data': user_data,
            'timestamp': str(timezone.now()),  # ✅ Now properly imported
            'service': 'user-service'
        }
        
        try:
            channel.basic_publish(
                exchange=exchange_name,
                routing_key=routing_key,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # make message persistent
                    content_type='application/json'
                )
            )
            
            print(f"✅ Published {event_type} event for user {user_data.get('username')}")
            
        except pika.exceptions.AMQPError as publish_error:
            print(f"❌ Failed to publish message: {str(publish_error)}")
        
        # Close connection
        try:
            connection.close()
        except pika.exceptions.AMQPError as close_error:
            print(f"❌ Failed to close RabbitMQ connection: {str(close_error)}")
        
    except Exception as e:
        print(f"❌ Unexpected error in publish_user_event: {str(e)}")
        import traceback
        print(f"📊 Full traceback: {traceback.format_exc()}")
        # Don't raise exception to avoid breaking user registration
