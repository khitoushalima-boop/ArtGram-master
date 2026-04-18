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
SECRET_KEY = 'django-insecure-artwork-service-key'

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
    'artworks',
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
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

CORS_ALLOW_ALL_ORIGINS = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
STATIC_URL = 'static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'artworks.authentication.ServiceJWTAuthentication',
    ),
}

SIMPLE_JWT = {
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': os.environ.get('JWT_SIGNING_KEY', 'django-insecure-user-service-key'),
    'VERIFYING_KEY': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
}
