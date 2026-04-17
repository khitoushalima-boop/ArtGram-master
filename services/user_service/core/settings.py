import os
import importlib.util
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
try:
    import environ
except ImportError:  # pragma: no cover - fallback for minimal local setups
    environ = None

if environ:
    env = environ.Env(DEBUG=(bool, False))
else:
    env = None

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-user-service-key'

DEBUG = env('DEBUG') if env else os.environ.get('DEBUG', '').lower() in {'1', 'true', 'yes'}

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'accounts',
]
if importlib.util.find_spec('corsheaders'):
    INSTALLED_APPS.append('corsheaders')

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]
if importlib.util.find_spec('corsheaders'):
    MIDDLEWARE.insert(0, 'corsheaders.middleware.CorsMiddleware')

ROOT_URLCONF = 'core.urls'

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
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'allauth.account.context_processors.account',
                'allauth.socialaccount.context_processors.socialaccount',
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

AUTH_USER_MODEL = 'accounts.User'

# Django-allauth authentication backend
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    )
}

from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

CORS_ALLOW_ALL_ORIGINS = True # In production, restrict this to your domain

# Google OAuth Configuration for django-allauth (localhost development)
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '985300164541-aneiq6of2u1tdfefll3hiaa59sasdkn5.apps.googleusercontent.com')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', 'your-google-client-secret')

# Django-allauth Google OAuth2 settings
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'offline',
        },
        'OAUTH_PKCE_ENABLED': True,
        'APP': {
            'client_id': GOOGLE_CLIENT_ID,
            'secret': GOOGLE_CLIENT_SECRET,
            'key': '',
        }
    }
}

# Session and cookie settings for OAuth on localhost
SESSION_COOKIE_SECURE = False  # Allow on HTTP for localhost
CSRF_COOKIE_SECURE = False      # Allow on HTTP for localhost
SESSION_COOKIE_SAMESITE = 'None'  # Required for OAuth redirects
CSRF_COOKIE_SAMESITE = 'None'      # Required for OAuth redirects
SECURE_SSL_REDIRECT = False       # Don't force HTTPS for localhost
SECURE_REFERRER_POLICY = 'no-referrer-when-downgrade'

# OAuthlib insecure transport for localhost
import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Django-allauth settings
SITE_ID = 1
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'none'  # Disable email verification for localhost
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_LOGIN_ATTEMPTS_LIMIT = 5
ACCOUNT_LOGIN_ATTEMPT_TIMEOUT = 300
ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'http'

# Redirect URLs for localhost
LOGIN_REDIRECT_URL = 'http://localhost:8001/'
LOGOUT_REDIRECT_URL = 'http://localhost:8001/'
ACCOUNT_SIGNUP_REDIRECT_URL = 'http://localhost:8001/'
SOCIALACCOUNT_LOGIN_REDIRECT_URL = 'http://localhost:8001/'
SOCIALACCOUNT_SIGNUP_REDIRECT_URL = 'http://localhost:8001/'

# JWT Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'oauth2_provider.contrib.rest_framework.OAuth2Authentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ]
}

# RabbitMQ Configuration
RABBITMQ_URL = os.environ.get('RABBITMQ_URL', 'amqp://guest:guest@localhost:5672/')

# RabbitMQ Event Publishing
def publish_user_event(user_id, event_type, user_data=None):
    import pika
    import json
    
    try:
        connection = pika.BlockingConnection(RABBITMQ_URL)
        channel = connection.channel()
        
        # Declare exchange
        channel.exchange_declare(exchange='user_events', exchange_type='topic')
        
        # Prepare message
        message = {
            'event_type': event_type,
            'user_id': user_id,
            'timestamp': str(timezone.now()),
            'data': user_data or {}
        }
        
        # Publish message
        channel.basic_publish(
            exchange='user_events',
            routing_key=f'user.{event_type}',
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            ))
        
        connection.close()
        print(f"Published {event_type} event for user {user_id}")
    except Exception as e:
        print(f"Failed to publish {event_type} event: {e}")

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
STATIC_URL = 'static/'
MEDIA_URL = '/media/avatars/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
