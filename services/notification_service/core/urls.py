from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from rest_framework.routers import DefaultRouter
from notifications.views import NotificationViewSet

def health_check(request):
    return JsonResponse({'status': 'healthy', 'service': 'notification-service'})

def api_root(request):
    return JsonResponse({
        'message': 'Notification Service API',
        'endpoints': {
            'notifications': '/api/notifications/',
            'health': '/health/',
            'admin': '/admin/'
        }
    })

router = DefaultRouter()
router.register(r'notifications', NotificationViewSet)

urlpatterns = [
    path('', api_root),
    path('health/', health_check),
    path('admin/', admin.site.urls),
    path('api/notifications/', include(router.urls)),
]
