from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ArtworkUploadView,
    ArtworkGalleryView,
    ArtworkDetailView,
    TagViewSet
)

# Create router for artwork endpoints (only for ViewSets)
router = DefaultRouter()
router.register(r'tags', TagViewSet, basename='tags')

# Custom URLs for specific artwork operations
urlpatterns = [
    # Artwork upload endpoint
    path('upload/', ArtworkUploadView.as_view(), name='artwork-upload'),
    
    # Artwork gallery with filtering
    path('gallery/', ArtworkGalleryView.as_view(), name='artwork-gallery'),
    
    # Individual artwork details
    path('artwork/<int:id>/', ArtworkDetailView.as_view(), name='artwork-detail'),
    
    # Include router endpoints
    path('', include(router.urls)),
]
