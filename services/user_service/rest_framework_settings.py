"""
REST Framework Configuration for ArtGram Microservices
Configures authentication classes and permissions for different use cases
"""

from rest_framework.authentication import (
    BasicAuthentication,
    SessionAuthentication,
    TokenAuthentication
)
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

# REST Framework Configuration
REST_FRAMEWORK = {
    # Authentication Classes - Multiple methods supported
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    
    # Permission Classes
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    
    # Pagination
    'PAGE_SIZE': 20,
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    
    # Filtering
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ],
    
    # Serialization
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    
    # Versioning
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.URLPathVersioning',
    'DEFAULT_VERSION': 'v1',
    
    # Throttling
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour'
    }
}

# Authentication Method Selection
def get_authentication_classes(auth_type=None):
    """
    Returns appropriate authentication classes based on type
    """
    if auth_type == 'basic':
        return [BasicAuthentication]
    elif auth_type == 'session':
        return [SessionAuthentication]
    elif auth_type == 'token':
        return [TokenAuthentication]
    elif auth_type == 'jwt':
        return [JWTAuthentication]
    else:
        return [
            'rest_framework.authentication.SessionAuthentication',
            'rest_framework.authentication.BasicAuthentication',
            'rest_framework.authentication.TokenAuthentication',
            'rest_framework_simplejwt.authentication.JWTAuthentication',
        ]

# Permission Class Selection
def get_permission_classes(permission_type=None):
    """
    Returns appropriate permission classes based on type
    """
    if permission_type == 'public':
        return []
    elif permission_type == 'admin_only':
        return [IsAuthenticated]
    else:
        return [IsAuthenticated]
