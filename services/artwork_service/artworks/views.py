from rest_framework import generics, viewsets, permissions, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.core.files.storage import default_storage
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from .models import Artwork, Tag
from .serializers import ArtworkSerializer, TagSerializer

class ArtworkUploadView(generics.ListCreateAPIView):
    """
    API endpoint for artists to upload their artworks
    Handles multipart/form-data with image validation and thumbnail generation
    """
    serializer_class = ArtworkSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Filter artworks by user_id or return all for gallery"""
        user_id = self.request.query_params.get('user_id')
        if user_id:
            return Artwork.objects.filter(user_id=user_id)
        return Artwork.objects.all()

    def perform_create(self, serializer):
        """Handle artwork creation with image processing"""
        with transaction.atomic():
            artwork = serializer.save()
            
            # Process image and generate thumbnail if provided
            if artwork.image:
                self._process_artwork_image(artwork)
            
            return artwork

    def _process_artwork_image(self, artwork):
        """Generate multiple sizes and optimize artwork image using Pillow"""
        try:
            from .image_processing import ArtworkImageProcessor
            
            # Process artwork image with multiple sizes
            result = ArtworkImageProcessor.process_artwork_upload(artwork.image, artwork)
            
            if result['success']:
                print(f"Successfully processed artwork {artwork.id}: {result['processed_images']}")
            else:
                print(f"Error processing artwork {artwork.id}: {result['error']}")
            
        except Exception as e:
            print(f"Error processing artwork image: {e}")

class ArtworkGalleryView(generics.ListAPIView):
    """
    Gallery endpoint to list all artworks with filtering options
    """
    serializer_class = ArtworkSerializer

    def get_queryset(self):
        """Support filtering by user_id, tags, and ordering"""
        queryset = Artwork.objects.all()
        
        # Filter by user_id
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        # Filter by tags
        tags = self.request.query_params.get('tags')
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',')]
            queryset = queryset.filter(tags__name__in=tag_list)
        
        # Ordering
        ordering = self.request.query_params.get('ordering', '-created_at')
        if ordering:
            queryset = queryset.order_by(ordering)
        
        return queryset

class ArtworkDetailView(generics.RetrieveAPIView):
    """
    Individual artwork view with full details
    """
    serializer_class = ArtworkSerializer
    lookup_field = 'id'

    def get_queryset(self):
        return Artwork.objects.all()

class TagViewSet(viewsets.ModelViewSet):
    """Tag management for categorization"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

class ArtworkViewSet(viewsets.ModelViewSet):
    """Full CRUD operations for Artwork model"""
    queryset = Artwork.objects.all()
    serializer_class = ArtworkSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['title', 'description', 'tags', 'user_id', 'created_at']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'title']
    ordering = ['-created_at']
