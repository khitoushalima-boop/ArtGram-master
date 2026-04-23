"""
Authentication URLs for ArtGram Microservices
Provides endpoints for different authentication methods
"""

from django.urls import path
from . import authentication_views

app_name = 'auth'

urlpatterns = [
    # Basic Authentication
    path('basic/login/', authentication_views.basic_login_view, name='basic_login'),
    path('basic/protected/', authentication_views.basic_auth_protected_view, name='basic_protected'),
    
    # Session Authentication
    path('session/login/', authentication_views.session_auth_protected_view, name='session_protected'),
    path('session/logout/', authentication_views.session_logout_view, name='session_logout'),
    
    # Token Authentication
    path('token/login/', authentication_views.token_login_view, name='token_login'),
    path('token/logout/', authentication_views.token_logout_view, name='token_logout'),
    path('token/protected/', authentication_views.token_auth_protected_view, name='token_protected'),
    
    # JWT Authentication
    path('jwt/login/', authentication_views.jwt_login_view, name='jwt_login'),
    path('jwt/protected/', authentication_views.jwt_auth_protected_view, name='jwt_protected'),
    
    # Utility Endpoints
    path('comparison/', authentication_views.auth_comparison_view, name='auth_comparison'),
    path('status/', authentication_views.auth_status_view, name='auth_status'),
]
