from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from rest_framework.routers import DefaultRouter
from artworks.views import (
    ArtworkUploadView,
    ArtworkGalleryView,
    ArtworkDetailView,
    TagViewSet,
    ArtworkViewSet
)

def health_check(request):
    return JsonResponse({'status': 'healthy', 'service': 'artwork-service'})

def api_root(request):
    return JsonResponse({
        'message': 'Artwork Service API',
        'endpoints': {
            'artworks': '/api/artworks/',
            'tags': '/api/artworks/tags/',
            'health': '/health/',
            'admin': '/admin/'
        }
    })

router = DefaultRouter()
router.register(r'artworks', ArtworkViewSet)
router.register(r'tags', TagViewSet)

urlpatterns = [
    path('', api_root),
    path('health/', health_check),
    path('admin/', admin.site.urls),
    path('api/artworks/', include(router.urls)),
    path('api/artworks/', include('artworks.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
