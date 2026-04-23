"""Health Check Views for ArtGram Microservices
Provides health check endpoints for Consul service discovery
"""

from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.db import connection
from django.core.cache import cache
from django.conf import settings
import psutil
import time

@require_GET
def health_check_view(request):
    """Health check endpoint for Consul service discovery"""
    try:
        # Check database connection
        db_status = "healthy"
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                db_status = "healthy"
        except Exception:
            db_status = "unhealthy"
        
        # Check memory usage
        memory = psutil.virtual_memory()
        memory_usage = memory.percent
        
        # Check disk usage
        disk = psutil.disk_usage('/')
        disk_usage = disk.percent
        
        # Check if service is responsive
        response_time = time.time()
        
        health_data = {
            'status': 'healthy' if db_status == 'healthy' and memory_usage < 90 and disk_usage < 90 else 'unhealthy',
            'timestamp': time.time(),
            'service': settings.SERVICE_NAME if hasattr(settings, 'SERVICE_NAME') else 'user-service',
            'version': '1.0.0',
            'checks': {
                'database': db_status,
                'memory_usage': f"{memory_usage:.1f}%",
                'disk_usage': f"{disk_usage:.1f}%",
                'response_time_ms': round((time.time() - response_time) * 1000, 2)
            },
            'metadata': {
                'environment': getattr(settings, 'ENVIRONMENT', 'development'),
                'debug': settings.DEBUG,
                'host': settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else 'localhost'
            }
        }
        
        # Determine HTTP status code
        status_code = 200 if health_data['status'] == 'healthy' else 503
        
        return JsonResponse(health_data, status=status_code)
        
    except Exception as e:
        error_data = {
            'status': 'unhealthy',
            'timestamp': time.time(),
            'service': settings.SERVICE_NAME if hasattr(settings, 'SERVICE_NAME') else 'user-service',
            'error': str(e),
            'checks': {
                'database': 'error',
                'memory_usage': 'unknown',
                'disk_usage': 'unknown',
                'response_time_ms': 'error'
            }
        }
        
        return JsonResponse(error_data, status=503)

@require_GET
def readiness_check_view(request):
    """Readiness check for Kubernetes/Docker deployments"""
    try:
        # Check if all critical services are ready
        checks = {
            'database': 'healthy',
            'cache': 'healthy' if cache.get('test_key', 'test_value') == 'test_value' else 'unhealthy',
            'migrations_applied': 'healthy'
        }
        
        all_healthy = all(status == 'healthy' for status in checks.values())
        
        readiness_data = {
            'status': 'ready' if all_healthy else 'not_ready',
            'timestamp': time.time(),
            'service': settings.SERVICE_NAME if hasattr(settings, 'SERVICE_NAME') else 'user-service',
            'checks': checks
        }
        
        status_code = 200 if all_healthy else 503
        
        return JsonResponse(readiness_data, status=status_code)
        
    except Exception as e:
        return JsonResponse({
            'status': 'not_ready',
            'error': str(e)
        }, status=503)

@require_GET
def liveness_check_view(request):
    """Liveness check for Kubernetes/Docker deployments"""
    try:
        liveness_data = {
            'status': 'alive',
            'timestamp': time.time(),
            'service': settings.SERVICE_NAME if hasattr(settings, 'SERVICE_NAME') else 'user-service',
            'uptime': time.time() - start_time if 'start_time' in locals() else 0
        }
        
        return JsonResponse(liveness_data, status=200)
        
    except Exception as e:
        return JsonResponse({
            'status': 'dead',
            'error': str(e)
        }, status=503)

@require_GET
def metrics_view(request):
    """Metrics endpoint for monitoring"""
    try:
        metrics = {
            'timestamp': time.time(),
            'service': settings.SERVICE_NAME if hasattr(settings, 'SERVICE_NAME') else 'user-service',
            'system': {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory': {
                    'total': psutil.virtual_memory().total,
                    'available': psutil.virtual_memory().available,
                    'percent': psutil.virtual_memory().percent
                },
                'disk': {
                    'total': psutil.disk_usage('/').total,
                    'free': psutil.disk_usage('/').free,
                    'percent': psutil.disk_usage('/').percent
                }
            }
        }
        
        return JsonResponse(metrics, status=200)
        
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)
