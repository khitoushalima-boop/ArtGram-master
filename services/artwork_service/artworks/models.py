from django.db import models
from django.utils import timezone

class Artwork(models.Model):
    """
    Core Artwork model for the ArtGram platform - Heart of the Platform
    """
    title = models.CharField(max_length=255, help_text="Artwork title")
    description = models.TextField(blank=True, null=True, help_text="Detailed artwork description")
    image = models.ImageField(upload_to='artworks/', help_text="High-quality artwork image")
    thumbnail = models.ImageField(upload_to='artworks/thumbnails/', blank=True, null=True, help_text="Generated thumbnail for gallery display")
    # Reference to user_id from User Service
    user_id = models.IntegerField(help_text="User ID from User Service")
    tags = models.ManyToManyField('Tag', related_name='artworks', blank=True, help_text="Artwork tags for categorization")
    views = models.PositiveIntegerField(default=0, help_text="Number of views for analytics")
    likes = models.PositiveIntegerField(default=0, help_text="Number of likes for engagement")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Creation timestamp")
    updated_at = models.DateTimeField(auto_now=True, help_text="Last update timestamp")

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user_id']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.title} by user {self.user_id}"

    @property
    def engagement_rate(self):
        """Calculate engagement rate as likes/views ratio"""
        if self.views > 0:
            return round((self.likes / self.views) * 100, 2)
        return 0

class Tag(models.Model):
    """
    Tag model for artwork categorization and discovery
    """
    name = models.CharField(max_length=100, unique=True, help_text="Unique tag name")
    color = models.CharField(max_length=7, default='#007bff', help_text="Tag color for UI display")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Tag creation timestamp")

    class Meta:
        ordering = ['name']
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'

    def __str__(self):
        return self.name
