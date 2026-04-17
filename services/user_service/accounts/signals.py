from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.core.files.base import ContentFile
from .models import User
from .avatar_processing import AvatarProcessor

@receiver(pre_save, sender=User)
def process_avatar_on_save(sender, instance, **kwargs):
    """
    Automatically process avatar image when user saves profile
    """
    if instance.avatar and hasattr(instance, '_original_avatar'):
        # Check if avatar has changed
        if instance.avatar != instance._original_avatar:
            # Process the new avatar
            AvatarProcessor.process_avatar(instance.avatar, instance.avatar_thumbnail)

@receiver(post_save, sender=User)
def create_default_avatar(sender, instance, created, **kwargs):
    """
    Create default avatar for new users or when avatar is cleared
    """
    if created or not instance.avatar:
        if not instance.avatar_thumbnail:
            # Create default avatar with user's initial
            default_avatar = AvatarProcessor.create_default_avatar(instance.username)
            if default_avatar:
                instance.avatar_thumbnail.save(default_avatar.name, default_avatar, save=True)
                instance.save(update_fields=['avatar_thumbnail'])

# Store original avatar for change detection
@receiver(post_save, sender=User)
def store_original_avatar(sender, instance, **kwargs):
    """
    Store original avatar for change detection on next save
    """
    if instance.avatar:
        instance._original_avatar = instance.avatar
    else:
        instance._original_avatar = None
