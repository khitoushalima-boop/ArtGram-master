from django.db import models
from django.conf import settings
from PIL import Image
import os

class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    color = models.CharField(max_length=7, default='#b59a6a') # Default gold color from CSS
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Artwork(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='artworks/')
    thumbnail = models.ImageField(upload_to='artworks/thumbnails/', blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='artworks')
    tags = models.ManyToManyField(Tag, related_name='artworks', blank=True)
    views = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} by {self.user.username}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image:
            self.generate_thumbnail()

    def generate_thumbnail(self):
        if not self.image:
            return

        img = Image.open(self.image.path)
        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            
            thumb_name = f"thumb_{os.path.basename(self.image.name)}"
            thumb_path = os.path.join(settings.MEDIA_ROOT, 'artworks', 'thumbnails', thumb_name)
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(thumb_path), exist_ok=True)
            
            img.save(thumb_path)
            self.thumbnail.name = f"artworks/thumbnails/{thumb_name}"
            super().save(update_fields=['thumbnail'])
