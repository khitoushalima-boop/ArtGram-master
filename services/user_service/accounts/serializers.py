from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.db import models

from .models import Follow, User, Achievement, UserAchievement


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    avatar = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ("id", "username", "email", "password", "avatar")
        read_only_fields = ("id",)

    def validate_email(self, value):
        normalized_email = value.lower().strip()
        if User.objects.filter(email__iexact=normalized_email).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return normalized_email

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        
        # Publish User_Created event to RabbitMQ
        from core.settings import publish_user_event
        user_data = {
            'username': user.username,
            'email': user.email,
            'avatar': user.avatar.url if user.avatar else None,
            'is_social': False
        }
        publish_user_event(user.id, 'User_Created', user_data)
        
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "avatar", "bio")
        read_only_fields = ("id",)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = {
            "id": self.user.id,
            "username": self.user.username,
            "email": self.user.email,
            "avatar": self.user.avatar.url if self.user.avatar else None,
        }
        return data




class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = "__all__"


class AchievementSerializer(serializers.ModelSerializer):
    progress_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = Achievement
        fields = "__all__"
    
    def get_progress_percentage(self, obj):
        # This will be calculated in UserAchievementSerializer
        return 0


class UserAchievementSerializer(serializers.ModelSerializer):
    achievement = AchievementSerializer(read_only=True)
    progress_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = UserAchievement
        fields = "__all__"
    
    def get_progress_percentage(self, obj):
        if obj.achievement.unlock_threshold > 0:
            return min(100, (obj.progress / obj.achievement.unlock_threshold) * 100)
        return 100


class UserProfileSerializer(serializers.ModelSerializer):
    """Extended user profile serializer with achievements and identity branding"""
    achievements = UserAchievementSerializer(many=True, read_only=True)
    total_points = serializers.SerializerMethodField()
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    arts_count = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ("id", "username", "email", "avatar", "bio", "job_title", "location", "website", 
                 "total_points", "achievements", "followers_count", "following_count", "arts_count")
        read_only_fields = ("id",)
    
    def get_total_points(self, obj):
        return obj.achievements.aggregate(
            total=models.Sum('achievement__points')
        )['total'] or 0
    
    def get_followers_count(self, obj):
        return obj.followers.count()
    
    def get_following_count(self, obj):
        return obj.following.count()
    
    def get_arts_count(self, obj):
        # This would typically fetch from artwork service
        # For now, return a placeholder
        return 0


class ProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user profile information.
    Handles personal info, professional info, and avatar updates.
    """
    
    # Predefined job titles for validation
    VALID_JOB_TITLES = [
        'Illustrator', 'Graphic Designer', 'Digital Artist', 'Photographer',
        'UI/UX Designer', 'Web Designer', 'Motion Designer', '3D Artist',
        'Concept Artist', 'Art Director', 'Creative Director', 'Visual Designer',
        'Brand Designer', 'Product Designer', 'Game Artist', 'Animator',
        'Fine Artist', 'Digital Painter', 'Mixed Media Artist'
    ]
    
    first_name = serializers.CharField(required=False, allow_blank=True, max_length=50)
    bio = serializers.CharField(required=False, allow_blank=True, max_length=500)
    job_title = serializers.CharField(required=False, allow_blank=True, max_length=100)
    avatar = serializers.ImageField(required=False, allow_null=True)
    
    class Meta:
        model = User
        fields = ['first_name', 'bio', 'job_title', 'avatar']
    
    def validate_job_title(self, value):
        """Validate job title against predefined list or allow custom valid string."""
        if not value:
            return value
            
        value = value.strip()
        
        # Check if it's in predefined list
        if value in self.VALID_JOB_TITLES:
            return value
        
        # Allow custom job titles (basic validation)
        if len(value) >= 2 and len(value) <= 100:
            # Check for basic profanity or invalid characters
            if any(char in value for char in ['<', '>', '&', '"', "'", '\\', '/']):
                raise serializers.ValidationError("Job title contains invalid characters.")
            return value
        
        raise serializers.ValidationError(
            f"Invalid job title. Choose from: {', '.join(self.VALID_JOB_TITLES[:5])}..."
        )
    
    def validate_first_name(self, value):
        """Validate full name field."""
        if value:
            value = value.strip()
            if len(value) < 2:
                raise serializers.ValidationError("Full name must be at least 2 characters long.")
            if len(value) > 50:
                raise serializers.ValidationError("Full name cannot exceed 50 characters.")
        return value
    
    def validate_bio(self, value):
        """Validate bio field."""
        if value:
            value = value.strip()
            if len(value) > 500:
                raise serializers.ValidationError("Bio cannot exceed 500 characters.")
        return value
    
    def update(self, instance, validated_data):
        """
        Handle avatar update logic with Pillow processing.
        """
        avatar = validated_data.get('avatar')
        
        # If new avatar is provided, process it with Pillow
        if avatar and avatar != instance.avatar:
            # Use the enhanced avatar processing service
            from .avatar_processing import AvatarProcessor
            
            # Process the new avatar with old thumbnail cleanup
            result = AvatarProcessor.process_avatar_update(avatar, instance.avatar_thumbnail)
            if not result['success']:
                raise serializers.ValidationError(f"Failed to process avatar image: {result.get('error', 'Unknown error')}")
        
        # Update user instance
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance
