from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from artworks.views import (
    ArtworkUploadView,
    ArtworkGalleryView,
    ArtworkDetailView,
    TagViewSet,
    ArtworkViewSet
)

router = DefaultRouter()
router.register(r'artworks', ArtworkViewSet)
router.register(r'tags', TagViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/artworks/', include(router.urls)),
    path('api/artworks/', include('artworks.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
