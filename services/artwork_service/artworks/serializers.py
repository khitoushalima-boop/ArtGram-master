from rest_framework import serializers
from .models import Artwork, Tag

class ArtworkSerializer(serializers.ModelSerializer):
    """
    Enhanced serializer for Artwork model with proper image handling
    """
    image = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()
    engagement_rate = serializers.SerializerMethodField()
    tag_names = serializers.SerializerMethodField()

    class Meta:
        model = Artwork
        fields = [
            'id', 'title', 'description', 'image', 'thumbnail', 
            'user_id', 'tags', 'views', 'likes', 
            'created_at', 'updated_at', 'engagement_rate', 'tag_names'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'views', 'likes']

    def get_image(self, obj):
        """Return full image URL through gateway"""
        if obj.image:
            return f"/media/{obj.image.name}"
        return None

    def get_thumbnail(self, obj):
        """Return thumbnail URL through gateway"""
        if obj.thumbnail:
            return f"/media/{obj.thumbnail.name}"
        return None

    def get_engagement_rate(self, obj):
        """Return calculated engagement rate"""
        return obj.engagement_rate

    def get_tag_names(self, obj):
        """Return list of tag names for frontend"""
        return [tag.name for tag in obj.tags.all()]

    def validate_image(self, value):
        """Validate image upload with proper constraints"""
        if not value:
            return None
        
        # Check file size (max 10MB)
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("Image size cannot exceed 10MB")
        
        # Check file type
        allowed_types = ['image/jpeg', 'image/png', 'image/webp', 'image/gif']
        if value.content_type not in allowed_types:
            raise serializers.ValidationError(
                f"Invalid image type. Allowed types: {', '.join(allowed_types)}"
            )
        
        return value

class TagSerializer(serializers.ModelSerializer):
    """Enhanced serializer for Tag model"""
    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'created_at']
        read_only_fields = ['id', 'created_at']
