from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from rest_framework.routers import DefaultRouter
from interactions.views import LikeViewSet, CommentViewSet

def health_check(request):
    return JsonResponse({'status': 'healthy', 'service': 'interaction-service'})

def api_root(request):
    return JsonResponse({
        'message': 'Interaction Service API',
        'endpoints': {
            'likes': '/api/interactions/likes/',
            'comments': '/api/interactions/comments/',
            'health': '/health/',
            'admin': '/admin/'
        }
    })

router = DefaultRouter()
router.register(r'likes', LikeViewSet)
router.register(r'comments', CommentViewSet)

urlpatterns = [
    path('', api_root),
    path('health/', health_check),
    path('admin/', admin.site.urls),
    path('api/interactions/', include(router.urls)),
]
