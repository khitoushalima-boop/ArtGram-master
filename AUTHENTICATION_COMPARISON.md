# ArtGram Authentication Methods Comparison

## Overview
This document provides a comprehensive comparison of 4 authentication methods implemented in the ArtGram Django REST Framework microservices project.

## 1. Basic Authentication

### Configuration
```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.BasicAuthentication',
    # ... other auth classes
    ],
}

# View Example
@api_view(['GET', 'POST'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def basic_auth_protected_view(request):
    user = request.user
    return Response({'user': user.username})
```

### Usage
```bash
# Login
curl -X POST http://localhost:8000/api/auth/basic/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "password": "test"}'

# Protected Request
curl -X GET http://localhost:8000/api/auth/basic/protected/ \
  -H "Authorization: Basic dXNlc2VybmFtZTpwYXNzd29yZA=="
```

### Pros
- ✅ Simple to implement
- ✅ Standard HTTP method
- ✅ Good for quick testing
- ✅ No additional setup required
- ✅ Works with any HTTP client

### Cons
- ❌ Credentials sent in every request
- ❌ Base64 encoding is not encryption
- ❌ Not suitable for production
- ❌ Hard to manage multiple users
- ❌ No automatic expiration

### Security Level: **Low**
- Use for development and testing only

---

## 2. Session Authentication

### Configuration
```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    # ... other auth classes
    ],
}

# View Example
@api_view(['GET', 'POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def session_auth_protected_view(request):
    user = request.user
    return Response({'user': user.username})
```

### Usage
```bash
# Login (via Django login form)
POST http://localhost:8000/api/auth/session/login/

# Protected Request
curl -X GET http://localhost:8000/api/auth/session/protected/ \
  -H "Cookie: sessionid=abc123def456"
```

### Pros
- ✅ Stateful - user context maintained
- ✅ Secure (HTTPS cookies)
- ✅ Easy to implement
- ✅ Good for web interfaces
- ✅ Built-in Django support
- ✅ Can control session lifetime

### Cons
- ❌ Requires server-side storage
- ❌ Not suitable for mobile APIs
- ❌ Session fixation vulnerabilities
- ❌ CSRF protection needed
- ❌ Scaling issues in distributed systems

### Security Level: **Medium**
- Requires HTTPS and CSRF protection

---

## 3. Token Authentication (DRF Authtoken)

### Configuration
```python
# settings.py
INSTALLED_APPS = [
    # ...
    'rest_framework.authtoken',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        # ... other auth classes
    ],
}

# View Example
@api_view(['GET', 'POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def token_auth_protected_view(request):
    user = request.user
    return Response({'user': user.username})
```

### Usage
```bash
# Login
curl -X POST http://localhost:8000/api/auth/token/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "password": "test"}'

# Protected Request
curl -X GET http://localhost:8000/api/auth/token/protected/ \
  -H "Authorization: Token 9944b09199c62bcbbd254c5a5c1a8ed1d"
```

### Pros
- ✅ Stateless - no server storage
- ✅ Good for mobile apps
- ✅ Can revoke individual tokens
- ✅ Scalable in microservices
- ✅ Simple client implementation
- ✅ DRF built-in support

### Cons
- ❌ Tokens can be stolen
- ❌ No automatic expiration
- ❌ Manual token management
- ❌ Storage overhead for tokens table

### Security Level: **Medium**
- Depends on token storage security

---

## 4. JWT Authentication (djangorestframework-simplejwt)

### Configuration
```python
# settings.py
INSTALLED_APPS = [
    # ...
    'rest_framework_simplejwt',
]

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': 'your-secret-key',
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        # ... other auth classes
    ],
}

# View Example
@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def jwt_auth_protected_view(request):
    user = request.user
    return Response({'user': user.username})
```

### Usage
```bash
# Login
curl -X POST http://localhost:8000/api/auth/jwt/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "password": "test"}'

# Protected Request
curl -X GET http://localhost:8000/api/auth/jwt/protected/ \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Pros
- ✅ Stateless - perfect for microservices
- ✅ Self-contained - no server storage
- ✅ Can include claims and metadata
- ✅ Standardized (RFC 7519)
- ✅ Built-in expiration
- ✅ Easy to scale horizontally
- ✅ Cross-origin support

### Cons
- ❌ Cannot revoke tokens easily
- ❌ Larger request headers
- ❌ Complex key management
- ❌ Requires HTTPS in production
- ❌ Token theft risk until expiration

### Security Level: **High**
- When properly implemented with HTTPS and proper key management

---

## Implementation Recommendations

### For Development
1. **Basic Authentication** - Quick testing and simple API calls
2. **JWT Authentication** - Microservices communication and stateless APIs

### For Production
1. **JWT Authentication** - Primary method for microservices
2. **Session Authentication** - Admin dashboard and web interface
3. **Token Authentication** - Mobile apps and API clients

### Security Best Practices
- Always use HTTPS in production
- Implement proper token expiration
- Use secure cookie settings
- Implement rate limiting
- Log authentication attempts
- Use CSRF protection for web forms

### URL Endpoints
```
/api/auth/basic/login/          - Basic Authentication Login
/api/auth/basic/protected/     - Basic Authentication Protected View
/api/auth/session/login/         - Session Authentication Login  
/api/auth/session/logout/          - Session Authentication Logout
/api/auth/session/protected/      - Session Authentication Protected View
/api/auth/token/login/           - Token Authentication Login
/api/auth/token/logout/           - Token Authentication Logout
/api/auth/token/protected/        - Token Authentication Protected View
/api/auth/jwt/login/             - JWT Authentication Login
/api/auth/jwt/protected/           - JWT Authentication Protected View
/api/auth/comparison/            - Authentication Methods Comparison
/api/auth/status/                - Authentication Status Check
```

### Integration with Existing ArtGram URLs
```python
# core/urls.py
from django.urls import path, include

urlpatterns = [
    path('api/auth/', include('authentication_urls')),
    path('api/users/', include('accounts.urls')),
    # ... other URLs
]
```

This comprehensive authentication system provides flexibility for different use cases while maintaining security best practices for microservices architecture.
