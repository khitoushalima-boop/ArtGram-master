from rest_framework import permissions, status, viewsets, generics, serializers
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from django.utils import timezone
import requests

from .models import User, Follow, Achievement, UserAchievement
from .serializers import (
    CustomTokenObtainPairSerializer,
    FollowSerializer,
    RegisterSerializer,
    UserSerializer,
    UserProfileSerializer,
    AchievementSerializer,
    UserAchievementSerializer,
    ProfileUpdateSerializer,
)
from .aggregation import profile_aggregator


class RegisterViewSet(viewsets.GenericViewSet):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        output_serializer = UserProfileSerializer(user, context={"request": request})
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [permissions.AllowAny]


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='me')
    def current_user_profile(self, request):
        """Get current user's profile with achievements"""
        serializer = UserProfileSerializer(request.user, context={"request": request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='aggregated')
    def aggregated_profile(self, request):
        """Get aggregated profile data from all microservices"""
        try:
            # Get auth token from request
            auth_header = request.headers.get('Authorization', '')
            token = auth_header.replace('Bearer ', '') if auth_header.startswith('Bearer ') else ''
            
            # For now, return basic aggregated data (async implementation would require Django async support)
            user_data = UserProfileSerializer(request.user, context={"request": request}).data
            
            # Add mock aggregated data from other services
            aggregated_data = {
                **user_data,
                'arts_data': {
                    'total_arts': 3,
                    'recent_arts': [
                        {'title': 'Sunset Dreams', 'views': 156, 'likes': 42},
                        {'title': 'Ocean Waves', 'views': 89, 'likes': 28},
                        {'title': 'Forest Path', 'views': 234, 'likes': 67}
                    ],
                    'total_views': 479,
                    'total_likes': 137
                },
                'interaction_data': {
                    'total_followers': 25,
                    'total_following': 18,
                    'engagement_rate': 4.2
                },
                'derived_metrics': {
                    'engagement_score': 78.5,
                    'activity_level': 'medium',
                    'influence_score': 65.0,
                    'profile_completion': 85
                },
                'aggregated_at': timezone.now().isoformat()
            }
            
            return Response(aggregated_data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AchievementViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Achievement.objects.all()
    serializer_class = AchievementSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'])
    def unlock_achievement(self, request, pk=None):
        """Unlock an achievement for the current user"""
        try:
            achievement = Achievement.objects.get(pk=pk)
            user_achievement, created = UserAchievement.objects.get_or_create(
                user=request.user,
                achievement=achievement
            )
            
            if created:
                # Publish achievement unlocked event
                from core.settings import publish_user_event
                achievement_data = {
                    'achievement_name': achievement.name,
                    'points': achievement.points,
                    'description': achievement.description
                }
                publish_user_event(request.user.id, 'Achievement_Unlocked', achievement_data)
                
                return Response({
                    'message': f'Achievement "{achievement.name}" unlocked!',
                    'achievement': AchievementSerializer(achievement).data
                }, status=status.HTTP_201_CREATED)
            else:
                return Response(
                    {'error': 'Achievement already unlocked'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Achievement.DoesNotExist:
            return Response(
                {'error': 'Achievement not found'},
                status=status.HTTP_404_NOT_FOUND
            )

class FollowViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = [permissions.IsAuthenticated]


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def google_login_callback(request):
    """
    Handle Google OAuth token verification and create/login user
    """
    try:
        token = request.data.get('token')
        if not token:
            return Response(
                {'error': 'Google token is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify Google token with Google API
        google_response = requests.get(
            f'https://www.googleapis.com/oauth2/v2/userinfo?access_token={token}'
        )
        
        if google_response.status_code != 200:
            return Response(
                {'error': 'Invalid Google token'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        google_data = google_response.json()
        email = google_data.get('email')
        
        if not email:
            return Response(
                {'error': 'Could not get email from Google'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create or get user
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': google_data.get('name', email.split('@')[0]).replace(' ', '_'),
                'first_name': google_data.get('given_name', ''),
                'last_name': google_data.get('family_name', ''),
                'is_active': True,
            }
        )
        
        # Download and save avatar if available
        if created and google_data.get('picture'):
            try:
                avatar_response = requests.get(google_data['picture'])
                if avatar_response.status_code == 200:
                    from django.core.files.base import ContentFile
                    import os
                    from datetime import datetime
                    
                    filename = f"avatar_{user.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                    user.avatar.save(filename, ContentFile(avatar_response.content), save=True)
            except Exception as e:
                print(f"Failed to save avatar: {e}")
        
        # Publish User_Created event if new user
        if created:
            from core.settings import publish_user_event
            user_data = {
                'username': user.username,
                'email': user.email,
                'avatar': user.avatar.url if user.avatar else None,
                'is_social': True,
                'provider': 'google'
            }
            publish_user_event(user.id, 'User_Created', user_data)
        
        # Generate JWT tokens for user
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'avatar': user.avatar.url if user.avatar else None,
            }
        })
            
    except Exception as e:
        return Response(
            {'error': f'Authentication error: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class ProfileUpdateView(generics.RetrieveUpdateAPIView):
    """
    API endpoint for updating user profile information.
    Only authenticated users can update their own profile.
    """
    serializer_class = ProfileUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        """
        Get the user object for the current authenticated user.
        """
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        """
        Handle profile update with proper error handling.
        """
        try:
            # Get the current user instance
            user = self.get_object()
            
            # Validate that user is updating their own profile
            if user.id != request.user.id:
                return Response(
                    {'error': 'You can only update your own profile.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Partial update is allowed
            serializer = self.get_serializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            
            # Save updated profile
            updated_user = serializer.save()
            
            # Return updated user data
            return Response({
                'message': 'Profile updated successfully.',
                'user': {
                    'id': updated_user.id,
                    'username': updated_user.username,
                    'email': updated_user.email,
                    'first_name': updated_user.first_name,
                    'bio': updated_user.bio,
                    'job_title': updated_user.job_title,
                    'location': updated_user.location,
                    'website': updated_user.website,
                    'avatar': updated_user.avatar.url if updated_user.avatar else None,
                    'avatar_thumbnail': updated_user.avatar_thumbnail.url if updated_user.avatar_thumbnail else None,
                    'updated_at': updated_user.updated_at.isoformat() if updated_user.updated_at else None
                }
            })
            
        except serializers.ValidationError as e:
            return Response({
                'error': 'Validation failed.',
                'details': e.detail
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                'error': 'Failed to update profile.',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


