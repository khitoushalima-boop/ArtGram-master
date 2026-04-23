"""
Authentication Configuration for ArtGram Microservices
Supports 4 authentication methods:
1. Basic Authentication (for testing)
2. Session Authentication (for admin dashboard)
3. Token Authentication (DRF authtoken)
4. JWT Authentication (djangorestframework-simplejwt)
"""

from rest_framework.authentication import (
    BasicAuthentication,
    SessionAuthentication,
    TokenAuthentication,
    JWTAuthentication
)
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication as SimpleJWTAuthentication
from rest_framework_simplejwt.settings import jwt_settings

# Authentication Classes for different use cases
AUTHENTICATION_CLASSES = {
    'basic': BasicAuthentication,
    'session': SessionAuthentication,
    'token': TokenAuthentication,
    'jwt': SimpleJWTAuthentication,
}

# Permission Classes
PERMISSION_CLASSES = {
    'default': [IsAuthenticated],
    'public': [],  # No authentication required
    'admin_only': [IsAuthenticated],
}

# Token Settings
TOKEN_SETTINGS = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

# JWT Settings
JWT_SETTINGS = {
    'ACCESS_TOKEN_LIFETIME': jwt_settings.ACCESS_TOKEN_LIFETIME,
    'REFRESH_TOKEN_LIFETIME': jwt_settings.REFRESH_TOKEN_LIFETIME,
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': 'your-secret-key-change-in-production',
    'VERIFYING_KEY': 'your-secret-key-change-in-production',
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

# Basic Authentication Settings
BASIC_AUTH_SETTINGS = {
    'ENABLED': True,
    'REALM': 'ArtGram API',
}

# Session Authentication Settings
SESSION_AUTH_SETTINGS = {
    'ENABLED': True,
    'SESSION_COOKIE_AGE': 86400,  # 24 hours
    'SESSION_COOKIE_HTTPONLY': True,
    'SESSION_COOKIE_SECURE': False,  # For localhost
}

# Token Authentication Settings
TOKEN_AUTH_SETTINGS = {
    'ENABLED': True,
    'DEFAULT_TOKEN_LIFETIME': 86400,  # 24 hours
    'ALLOWED_TOKENS_PER_USER': 5,
}

# API Documentation
API_DOCS = {
    'BASIC_AUTH': {
        'header': 'Authorization',
        'format': 'Basic base64(username:password)',
        'example': 'Authorization: Basic dXNlc2VybmFtZTpwYXNzd29yZA==',
        'use_case': 'Quick testing, simple API calls'
    },
    'SESSION_AUTH': {
        'header': 'Cookie',
        'format': 'sessionid=<session-id>',
        'example': 'Cookie: sessionid=abc123def456',
        'use_case': 'Admin dashboard, web interface'
    },
    'TOKEN_AUTH': {
        'header': 'Authorization',
        'format': 'Token <token>',
        'example': 'Authorization: Token 9944b09199c62bcbbd254c5a5c1a8ed1d',
        'use_case': 'API clients, mobile apps'
    },
    'JWT_AUTH': {
        'header': 'Authorization',
        'format': 'Bearer <jwt-token>',
        'example': 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjEsImV4c2UiOjE2LCJleHAiOjE2LCJpYXQiOjE2fQ.signed_token',
        'use_case': 'Microservices communication, stateless APIs'
    }
}
