from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    email = models.EmailField(unique=True)
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, help_text="High-resolution avatar image")
    avatar_thumbnail = models.ImageField(upload_to='avatars/thumbnails/', blank=True, null=True, help_text="Processed thumbnail for profile display")
    job_title = models.CharField(max_length=100, blank=True, null=True, help_text="Professional job title or role")
    location = models.CharField(max_length=100, blank=True, null=True, help_text="User's location")
    website = models.URLField(blank=True, null=True, help_text="Professional website or portfolio")
    updated_at = models.DateTimeField(auto_now=True, help_text="Timestamp for profile updates")
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

class Follow(models.Model):
    follower = models.ForeignKey(User, related_name='following', on_delete=models.CASCADE)
    following = models.ForeignKey(User, related_name='followers', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')

    def __str__(self):
        return f"{self.follower} follows {self.following}"


class Achievement(models.Model):
    CATEGORY_CHOICES = [
        ('milestone', 'Milestone'),
        ('community', 'Community'),
        ('creative', 'Creative'),
        ('engagement', 'Engagement'),
        ('professional', 'Professional'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50, blank=True, null=True)
    points = models.PositiveIntegerField(default=0)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='milestone')
    is_rare = models.BooleanField(default=False, help_text="Rare achievements are highlighted")
    unlock_threshold = models.PositiveIntegerField(default=1, help_text="Threshold for unlocking this achievement")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Achievement"
        verbose_name_plural = "Achievements"

    def __str__(self):
        return self.name


class UserAchievement(models.Model):
    user = models.ForeignKey(User, related_name='achievements', on_delete=models.CASCADE)
    achievement = models.ForeignKey(Achievement, related_name='user_achievements', on_delete=models.CASCADE)
    unlocked_at = models.DateTimeField(auto_now_add=True)
    progress = models.PositiveIntegerField(default=0, help_text="Current progress towards achievement")
    is_completed = models.BooleanField(default=False, help_text="Whether the achievement is fully completed")

    class Meta:
        verbose_name = "User Achievement"
        verbose_name_plural = "User Achievements"
        unique_together = ('user', 'achievement')

    def __str__(self):
        return f"{self.user.username} - {self.achievement.name} ({self.progress}/{self.achievement.unlock_threshold})"
