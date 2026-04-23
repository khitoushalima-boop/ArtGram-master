"""
Backend Ping Endpoint for Testing Frontend-Backend Communication
Add this to your Django views.py to test connectivity
"""

from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import json
import time

@require_GET
def ping_endpoint(request):
    """
    Simple GET endpoint to test basic connectivity
    Usage: GET /api/ping/
    """
    try:
        response_data = {
            'status': 'pong',
            'message': 'Backend is alive and responding!',
            'timestamp': time.time(),
            'method': request.method,
            'path': request.path,
            'headers': dict(request.headers),
            'query_params': dict(request.GET),
            'server_info': {
                'django_version': '5.1.0',
                'python_version': '3.11+',
                'environment': 'development'
            }
        }
        
        print(f"🏓 PING received: {request.method} {request.path}")
        print(f"📊 Headers: {dict(request.headers)}")
        print(f"🔍 Query params: {dict(request.GET)}")
        
        return JsonResponse(response_data, status=200)
        
    except Exception as e:
        error_data = {
            'status': 'error',
            'message': f'Ping failed: {str(e)}',
            'timestamp': time.time(),
            'error_type': type(e).__name__
        }
        print(f"❌ PING ERROR: {str(e)}")
        return JsonResponse(error_data, status=500)

@require_POST
@csrf_exempt
def ping_post_endpoint(request):
    """
    POST endpoint to test POST requests and JSON handling
    Usage: POST /api/ping-post/
    """
    try:
        # Parse JSON body
        try:
            body_data = json.loads(request.body)
        except json.JSONDecodeError:
            body_data = {'raw_body': request.body.decode('utf-8')}
        
        response_data = {
            'status': 'pong',
            'message': 'POST request received successfully!',
            'timestamp': time.time(),
            'method': request.method,
            'path': request.path,
            'headers': dict(request.headers),
            'body_data': body_data,
            'content_type': request.content_type,
            'content_length': request.content_length,
            'query_params': dict(request.GET),
            'server_info': {
                'django_version': '5.1.0',
                'python_version': '3.11+',
                'environment': 'development'
            }
        }
        
        print(f"🏓 POST PING received: {request.method} {request.path}")
        print(f"📊 Headers: {dict(request.headers)}")
        print(f"📦 Body data: {body_data}")
        print(f"🔍 Query params: {dict(request.GET)}")
        
        return JsonResponse(response_data, status=200)
        
    except Exception as e:
        error_data = {
            'status': 'error',
            'message': f'POST ping failed: {str(e)}',
            'timestamp': time.time(),
            'error_type': type(e).__name__,
            'body_received': request.body.decode('utf-8', errors='ignore')
        }
        print(f"❌ POST PING ERROR: {str(e)}")
        return JsonResponse(error_data, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class PingView(View):
    """
    Class-based ping endpoint for testing different HTTP methods
    Usage: GET/POST/PUT/DELETE /api/ping-class/
    """
    
    def get(self, request):
        return JsonResponse({
            'status': 'pong',
            'message': 'Class-based GET ping successful',
            'method': request.method,
            'timestamp': time.time()
        })
    
    def post(self, request):
        try:
            body_data = json.loads(request.body) if request.body else {}
        except json.JSONDecodeError:
            body_data = {'raw_body': request.body.decode('utf-8')}
            
        return JsonResponse({
            'status': 'pong',
            'message': 'Class-based POST ping successful',
            'method': request.method,
            'timestamp': time.time(),
            'body_data': body_data
        })
    
    def put(self, request):
        return JsonResponse({
            'status': 'pong',
            'message': 'Class-based PUT ping successful',
            'method': request.method,
            'timestamp': time.time()
        })
    
    def delete(self, request):
        return JsonResponse({
            'status': 'pong',
            'message': 'Class-based DELETE ping successful',
            'method': request.method,
            'timestamp': time.time()
        })

@require_GET
def health_check_endpoint(request):
    """
    Comprehensive health check for backend services
    Usage: GET /api/health/
    """
    try:
        from django.db import connection
        
        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    response_data = {
        'status': 'healthy',
        'timestamp': time.time(),
        'services': {
            'database': db_status,
            'django': 'healthy',
            'api': 'healthy'
        },
        'environment': 'development',
        'version': '1.0.0'
    }
    
    return JsonResponse(response_data, status=200)

# URL patterns to add to your urls.py
"""
Add these to your Django urls.py:

from django.urls import path
from . import backend_ping_endpoint

urlpatterns = [
    # ... existing patterns
    path('api/ping/', backend_ping_endpoint.ping_endpoint, name='ping'),
    path('api/ping-post/', backend_ping_endpoint.ping_post_endpoint, name='ping_post'),
    path('api/ping-class/', backend_ping_endpoint.PingView.as_view(), name='ping_class'),
    path('api/health/', backend_ping_endpoint.health_check_endpoint, name='health'),
]
"""
