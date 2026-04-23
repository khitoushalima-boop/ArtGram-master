"""
Authentication Views for ArtGram Microservices
Demonstrates 4 authentication methods:
1. Basic Authentication
2. Session Authentication  
3. Token Authentication (DRF authtoken)
4. JWT Authentication (djangorestframework-simplejwt)
"""

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import (
    BasicAuthentication,
    SessionAuthentication,
    TokenAuthentication
)
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.authtoken.models import Token
from authentication_config import (
    AUTHENTICATION_CLASSES,
    PERMISSION_CLASSES,
    API_DOCS
)


@api_view(['GET', 'POST'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def basic_auth_protected_view(request):
    """
    Basic Authentication Protected View
    Header: Authorization: Basic base64(username:password)
    Use: Quick testing, simple API calls
    """
    user = request.user
    return Response({
        'message': 'Basic Authentication successful',
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
        },
        'auth_type': 'Basic',
        'auth_docs': API_DOCS['BASIC_AUTH']
    })


@api_view(['GET', 'POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def session_auth_protected_view(request):
    """
    Session Authentication Protected View
    Header: Cookie: sessionid=<session-id>
    Use: Admin dashboard, web interface
    """
    user = request.user
    return Response({
        'message': 'Session Authentication successful',
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
        },
        'auth_type': 'Session',
        'auth_docs': API_DOCS['SESSION_AUTH']
    })


@api_view(['GET', 'POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def token_auth_protected_view(request):
    """
    Token Authentication Protected View
    Header: Authorization: Token <token>
    Use: API clients, mobile apps
    """
    user = request.user
    return Response({
        'message': 'Token Authentication successful',
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
        },
        'auth_type': 'Token',
        'auth_docs': API_DOCS['TOKEN_AUTH']
    })


@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def jwt_auth_protected_view(request):
    """
    JWT Authentication Protected View
    Header: Authorization: Bearer <jwt-token>
    Use: Microservices communication, stateless APIs
    """
    user = request.user
    return Response({
        'message': 'JWT Authentication successful',
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
        },
        'auth_type': 'JWT',
        'auth_docs': API_DOCS['JWT_AUTH']
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def basic_login_view(request):
    """
    Basic Authentication Login
    POST: /api/auth/basic/login/
    Body: {"username": "test", "password": "test"}
    """
    username = request.data.get('username')
    password = request.data.get('password')
    
    user = authenticate(username=username, password=password)
    
    if user is not None:
        return Response({
            'error': 'Invalid credentials'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    login(request, user)
    
    return Response({
        'message': 'Basic login successful',
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
        }
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def token_login_view(request):
    """
    Token Authentication Login
    POST: /api/auth/token/login/
    Body: {"username": "test", "password": "test"}
    """
    username = request.data.get('username')
    password = request.data.get('password')
    
    user = authenticate(username=username, password=password)
    
    if user is not None:
        return Response({
            'error': 'Invalid credentials'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    token, created = Token.objects.get_or_create(user=user)
    
    return Response({
        'message': 'Token login successful',
        'token': token.key,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
        }
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def jwt_login_view(request):
    """
    JWT Authentication Login
    POST: /api/auth/jwt/login/
    Body: {"username": "test", "password": "test"}
    """
    username = request.data.get('username')
    password = request.data.get('password')
    
    user = authenticate(username=username, password=password)
    
    if user is not None:
        return Response({
            'error': 'Invalid credentials'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    refresh = RefreshToken.for_user(user)
    
    return Response({
        'message': 'JWT login successful',
        'access_token': str(refresh.access_token),
        'refresh_token': str(refresh),
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
        }
    })


@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def session_logout_view(request):
    """
    Session Logout
    POST: /api/auth/session/logout/
    """
    logout(request)
    return Response({
        'message': 'Session logout successful'
    })


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def token_logout_view(request):
    """
    Token Logout
    POST: /api/auth/token/logout/
    """
    try:
        # Delete the user's token
        request.user.auth_token.delete()
        return Response({
            'message': 'Token logout successful'
        })
    except:
        return Response({
            'error': 'Invalid token'
        }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
@permission_classes([AllowAny])
def auth_comparison_view(request):
    """
    Authentication Comparison View
    GET: /api/auth/comparison/
    """
    return Response({
        'title': 'ArtGram Authentication Methods Comparison',
        'methods': [
            {
                'name': 'Basic Authentication',
                'type': 'basic',
                'header': 'Authorization: Basic base64(username:password)',
                'example': 'Authorization: Basic dXNlc2VybmFtZTpwYXNzd29yZA==',
                'pros': [
                    'Simple to implement',
                    'Standard HTTP method',
                    'Good for quick testing',
                    'No additional setup required'
                ],
                'cons': [
                    'Credentials sent in every request',
                    'Base64 encoding is not encryption',
                    'Not suitable for production',
                    'Hard to manage multiple users'
                ],
                'use_case': 'Quick testing, simple API calls',
                'security': 'Low - credentials exposed in headers'
            },
            {
                'name': 'Session Authentication',
                'type': 'session',
                'header': 'Cookie: sessionid=<session-id>',
                'example': 'Cookie: sessionid=abc123def456',
                'pros': [
                    'Stateful - user context maintained',
                    'Secure (HTTPS cookies)',
                    'Easy to implement',
                    'Good for web interfaces',
                    'Built-in Django support',
                    'Can control session lifetime'
                ],
                'cons': [
                    'Requires server-side storage',
                    'Not suitable for mobile APIs',
                    'Session fixation vulnerabilities',
                    'CSRF protection needed',
                    'Scaling issues in distributed systems'
                ],
                'use_case': 'Admin dashboard, web interface',
                'security': 'Medium - depends on HTTPS and CSRF protection'
            },
            {
                'name': 'Token Authentication',
                'type': 'token',
                'header': 'Authorization: Token <token>',
                'example': 'Authorization: Token 9944b09199c62bcbbd254c5a1c8ed1d',
                'pros': [
                    'Stateless - no server storage',
                    'Good for mobile apps',
                    'Can revoke individual tokens',
                    'Scalable in microservices',
                    'Simple client implementation',
                    'DRF built-in support'
                ],
                'cons': [
                    'Tokens can be stolen',
                    'No automatic expiration',
                    'Manual token management',
                    'Storage overhead for tokens table'
                ],
                'use_case': 'API clients, mobile apps',
                'security': 'Medium - depends on token storage security'
            },
            {
                'name': 'JWT Authentication',
                'type': 'jwt',
                'header': 'Authorization: Bearer <jwt-token>',
                'example': 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjEsImV4c2UiOjE2LCJleHAiOjE2LCJpYXQiOjE2fQ.signed_token',
                'pros': [
                    'Stateless - perfect for microservices',
                    'Self-contained - no server storage',
                    'Can include claims and metadata',
                    'Standardized (RFC 7519)',
                    'Built-in expiration',
                    'Easy to scale horizontally',
                    'Cross-origin support'
                ],
                'cons': [
                    'Cannot revoke tokens easily',
                    'Larger request headers',
                    'Complex key management',
                    'Requires HTTPS in production',
                    'Token theft risk until expiration'
                ],
                'use_case': 'Microservices communication, stateless APIs',
                'security': 'High - when properly implemented with HTTPS'
            }
        ],
        'recommendations': {
            'development': 'Use Basic Auth for quick testing',
            'production': 'Use JWT for microservices communication',
            'admin_interface': 'Use Session Auth for admin dashboard',
            'mobile_apps': 'Use Token Auth or JWT',
            'security_best_practices': [
                'Always use HTTPS in production',
                'Implement proper token expiration',
                'Use secure cookie settings',
                'Implement rate limiting',
                'Log authentication attempts',
                'Use CSRF protection for web forms'
            ]
        }
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def auth_status_view(request):
    """
    Authentication Status Check
    GET: /api/auth/status/
    """
    auth_methods = []
    
    if request.user.is_authenticated:
        user = request.user
        auth_methods.append({
            'type': 'authenticated',
            'user': user.username,
            'method': request.auth.__class__.__name__ if request.auth else None
        })
    
    return Response({
        'status': 'Authentication status',
        'authenticated': request.user.is_authenticated,
        'user': request.user.username if request.user.is_authenticated else None,
        'auth_method': request.auth.__class__.__name__ if request.auth else None,
        'available_methods': auth_methods
    })
