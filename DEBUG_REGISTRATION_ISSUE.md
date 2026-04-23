# Google OAuth2 Registration Debugging Guide

## 🔍 Issue Analysis

Based on the Docker logs showing:
```
Method Not Allowed: /api/users/login/
Bad Request: /api/users/register/
```

The frontend is trying to access the correct endpoints, but they're failing.

## 🛠️ Step-by-Step Debugging Checklist

### 1. Check Docker Logs for Exact Error
```bash
# Get real-time logs
docker logs -f artgram-master-user-service-1

# Get last 50 lines
docker logs artgram-master-user-service-1 --tail=50
```

### 2. Test Backend Endpoints Directly
```bash
# Test login endpoint
curl -X POST http://localhost:8001/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "password": "test"}'

# Test register endpoint  
curl -X POST http://localhost:8001/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "email": "test@example.com", "password": "test123"}'
```

### 3. Check Database Migrations
```bash
# Enter user service container
docker exec -it artgram-master-user-service-1 bash

# Run migrations
python manage.py migrate

# Check if tables exist
python manage.py showmigrations
```

### 4. Verify CORS Configuration
```python
# Check CORS settings in settings.py
grep -n "CORS" /app/core/settings.py

# Test CORS preflight
curl -X OPTIONS http://localhost:8001/api/users/login/ \
  -H "Origin: http://localhost:8001" \
  -H "Access-Control-Request-Method: POST"
```

### 5. Check URL Routing
```python
# Test URL patterns
python manage.py show_urls

# Check if endpoints are accessible
curl http://localhost:8001/api/users/
```

## 🔧 Common Issues & Solutions

### Issue 1: "Method Not Allowed" on Login
**Possible Causes:**
- URL pattern not matching
- Wrong HTTP method in ViewSet
- Missing `@api_view` decorator
- URL routing conflict

**Solutions:**
```python
# In accounts/urls.py - ensure correct path
urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),  # NOT login/
    path("register/", RegisterViewSet.as_view({"post": "create"}), name="register"),
]

# In views.py - check view class
class LoginView(TokenObtainPairView):
    # Ensure this extends the correct class
    pass
```

### Issue 2: "Bad Request" on Registration
**Possible Causes:**
- Serializer validation failing
- Missing required fields
- Invalid data format
- Database constraint violation

**Solutions:**
```python
# Check serializer validation
class RegisterSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        # Add custom validation
        if 'email' not in attrs:
            raise serializers.ValidationError("Email is required")
        return attrs

# Check view error handling
def create(self, request):
    try:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserProfileSerializer(user), status=201)
    except serializers.ValidationError as e:
        return Response({'error': str(e)}, status=400)
    except Exception as e:
        return Response({'error': str(e)}, status=500)
```

### Issue 3: CORS Problems
**Possible Causes:**
- `CORS_ALLOW_ALL_ORIGINS = True` but specific origins needed
- Missing CORS headers in response
- Pre-flight request handling

**Solutions:**
```python
# In settings.py
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True  # For cookies
CORS_ALLOW_HEADERS = [
    'Content-Type',
    'Authorization',
    'X-Requested-With'
]

# In middleware
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    # ... other middleware
]
```

### Issue 4: Database Connection Issues
**Possible Causes:**
- Database not migrated
- Wrong connection string
- PostgreSQL not running

**Solutions:**
```bash
# Check database connection
docker exec artgram-master-user-service-1 python manage.py dbshell

# Run migrations
docker exec artgram-master-user-service-1 python manage.py migrate

# Check PostgreSQL
docker logs artgram-master-db_user-1
```

### Issue 5: Frontend Error Handling
**Current Problem:**
```javascript
// Generic error handling
fetch('/api/users/register/', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(formData)
})
.then(response => {
    if (!response.ok) {
        alert('Registration failed!');
        return;
    }
    // No specific error details
})
```

**Improved Error Handling:**
```javascript
async function registerUser(formData) {
    try {
        const response = await fetch('/api/users/register/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify(formData)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            console.error('Registration failed:', errorData);
            
            // Show specific error message
            if (errorData.error) {
                alert(`Registration failed: ${errorData.error}`);
            } else if (errorData.detail) {
                alert(`Registration failed: ${errorData.detail}`);
            } else {
                alert('Registration failed. Please try again.');
            }
            return;
        }
        
        const data = await response.json();
        console.log('Registration successful:', data);
        // Handle success
        localStorage.setItem('token', data.access);
        localStorage.setItem('user', JSON.stringify(data.user));
        window.location.href = '/index.html';
        
    } catch (error) {
        console.error('Network error:', error);
        alert('Network error. Please check your connection.');
    }
}
```

## 🌐 Google OAuth2 Specific Debugging

### Check Google Cloud Console Configuration
1. **Authorized JavaScript Origins:**
   - `http://localhost:8001`
   - `http://127.0.0.1:8001`

2. **Authorized Redirect URIs:**
   - `http://localhost:8001/api/users/google/callback/`
   - `http://127.0.0.1:8001/api/users/google/callback/`

3. **Client ID Configuration:**
   - Verify Client ID matches exactly
   - Check Client Secret is correct

### Test Google OAuth Flow
```javascript
// Test direct Google OAuth URL
window.location.href = 'http://localhost:8001/api/users/google/login/';

// Check if Google redirects properly
console.log('Testing Google OAuth redirect...');
```

## 📝 Quick Fixes to Try

### 1. Fix URL Routing
```python
# accounts/urls.py
from django.urls import path
from .views import LoginView, RegisterViewSet

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),  # Remove extra slash
    path("register/", RegisterViewSet.as_view({"post": "create"}), name="register"),
]
```

### 2. Add Debug Logging
```python
# views.py
import logging

logger = logging.getLogger(__name__)

class RegisterViewSet(viewsets.GenericViewSet):
    def create(self, request):
        logger.info(f"Registration attempt: {request.data}")
        # ... rest of code
```

### 3. Test with Simple Data
```bash
# Test with minimal valid data
curl -X POST http://localhost:8001/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser", 
    "email": "test@example.com", 
    "password": "test123456"
  }'
```

### 4. Check Environment Variables
```bash
# Verify Docker environment
docker exec artgram-master-user-service-1 env | grep -E "(SERVICE_NAME|SERVICE_PORT|DATABASE_URL)"
```

## 🎯 Action Plan

1. **Immediate**: Check Docker logs for exact error messages
2. **Backend**: Test endpoints directly with curl
3. **Database**: Verify migrations and connections
4. **CORS**: Confirm settings are correct
5. **Frontend**: Improve error handling with specific messages
6. **OAuth**: Verify Google Cloud Console configuration

Follow this checklist systematically to identify and fix the registration issue.
