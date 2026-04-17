from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Like, Comment
from .serializers import LikeSerializer, CommentSerializer
from .producer import publish_event

class LikeViewSet(viewsets.ModelViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        if response.status_code == status.HTTP_201_CREATED:
            # Publish event: type 'LIKE', body with details
            publish_event('LIKE', response.data)
        return response

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        if response.status_code == status.HTTP_201_CREATED:
            # Publish event: type 'COMMENT', body with details
            publish_event('COMMENT', response.data)
        return response
