from rest_framework import viewsets, generics, permissions, status, serializers, views
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.conf import settings
from django.utils import timezone
from django.http import JsonResponse
import requests
import time
import logging
import traceback

# Configure logging
logger = logging.getLogger(__name__)
registration_logger = logging.getLogger('registration')

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

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def ping_endpoint(request):
    """Simple ping endpoint to test connectivity"""
    try:
        response_data = {
            'status': 'pong',
            'message': 'Backend is alive!',
            'timestamp': time.time(),
            'method': request.method,
            'path': request.path,
            'headers': dict(request.headers),
            'service': 'user-service',
            'version': '1.0.0'
        }
        
        print(f"🏓 PING received: {request.method} {request.path}")
        return JsonResponse(response_data, status=200)
        
    except Exception as e:
        error_data = {
            'status': 'error',
            'message': 'Ping failed',
            'error': str(e),
            'service': 'user-service'
        }
        print(f"❌ PING ERROR: {str(e)}")
        return JsonResponse(error_data, status=500)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def health_check(request):
    """Health check endpoint for Consul service discovery"""
    try:
        from django.db import connection
        from django.conf import settings
        
        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            db_status = "healthy"
        
        response_data = {
            'status': 'healthy',
            'service': 'user-service',
            'version': '1.0.0',
            'timestamp': time.time(),
            'checks': {
                'database': db_status,
                'django': 'healthy'
            },
            'environment': getattr(settings, 'ENVIRONMENT', 'development')
        }
        
        print(f"🏥 Health check passed: {request.method} {request.path}")
        return JsonResponse(response_data, status=200)
        
    except Exception as e:
        error_data = {
            'status': 'unhealthy',
            'service': 'user-service',
            'error': str(e),
            'timestamp': time.time(),
            'checks': {
                'database': 'unhealthy',
                'django': 'unhealthy'
            }
        }
        print(f"❌ Health check failed: {str(e)}")
        return JsonResponse(error_data, status=503)


class RegisterViewSet(viewsets.GenericViewSet):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request):
        registration_logger.info("=" * 50)
        registration_logger.info("🔍 REGISTRATION REQUEST STARTED")
        registration_logger.info(f"📊 Request Method: {request.method}")
        registration_logger.info(f"📊 Request Headers: {dict(request.headers)}")
        registration_logger.info(f"📊 Request Data: {request.data}")
        registration_logger.info(f"📊 Request Content-Type: {request.content_type}")
        
        try:
            serializer = self.get_serializer(data=request.data)
            registration_logger.info("✅ Serializer created successfully")
            
            # Validate with detailed error logging
            try:
                serializer.is_valid(raise_exception=True)
                registration_logger.info("✅ Serializer validation passed")
            except serializers.ValidationError as e:
                registration_logger.error(f"❌ Serializer validation failed: {e.detail}")
                registration_logger.error(f"📊 Validation Errors: {serializer.errors}")
                raise
            
            # Create user with detailed logging
            try:
                user = serializer.save()
                registration_logger.info(f"✅ User created successfully: {user.username} (ID: {user.id})")
                registration_logger.info(f"📊 User Email: {user.email}")
            except Exception as e:
                registration_logger.error(f"❌ User creation failed: {str(e)}")
                registration_logger.error(f"📊 Traceback: {traceback.format_exc()}")
                raise
            
            # Return response
            output_serializer = UserProfileSerializer(user, context={"request": request})
            response_data = output_serializer.data
            registration_logger.info(f"✅ Registration successful for user: {user.username}")
            registration_logger.info(f"📊 Response Data Keys: {list(response_data.keys())}")
            registration_logger.info("=" * 50)
            
            return Response(response_data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            registration_logger.error(f"💥 REGISTRATION FAILED: {str(e)}")
            registration_logger.error(f"📊 Exception Type: {type(e).__name__}")
            registration_logger.error(f"📊 Exception Args: {e.args}")
            registration_logger.error(f"📊 Traceback: {traceback.format_exc()}")
            registration_logger.info("=" * 50)
            raise


class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [permissions.AllowAny]


class DjangoLoginView(views.APIView):
    """
    Django session-based login view
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        from django.contrib.auth import authenticate, login
        from django.views.decorators.csrf import csrf_exempt
        from django.utils.decorators import method_decorator
        
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response({
                'error': 'Username and password are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user = authenticate(username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            # Return user data
            from .serializers import UserProfileSerializer
            serializer = UserProfileSerializer(user, context={'request': request})
            
            return Response({
                'success': True,
                'message': 'Login successful',
                'user': serializer.data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)


class DjangoLogoutView(views.APIView):
    """
    Django session-based logout view
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        from django.contrib.auth import logout
        
        logout(request)
        
        return Response({
            'success': True,
            'message': 'Logout successful'
        }, status=status.HTTP_200_OK)


class DjangoSessionView(views.APIView):
    """
    Check if user is authenticated via session or JWT token
    """
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        # First check if user is authenticated via session
        if request.user.is_authenticated:
            from .serializers import UserProfileSerializer
            serializer = UserProfileSerializer(request.user, context={'request': request})
            
            return Response({
                'authenticated': True,
                'user': serializer.data
            }, status=status.HTTP_200_OK)
        
        # Then check if user is authenticated via JWT token
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            from rest_framework_simplejwt.authentication import JWTAuthentication
            from rest_framework_simplejwt.exceptions import InvalidToken
            
            try:
                jwt_auth = JWTAuthentication()
                validated_token = jwt_auth.get_validated_token(auth_header[7:])  # Remove 'Bearer '
                user = jwt_auth.get_user(validated_token)
                
                if user and user.is_authenticated:
                    from .serializers import UserProfileSerializer
                    serializer = UserProfileSerializer(user, context={'request': request})
                    
                    return Response({
                        'authenticated': True,
                        'user': serializer.data
                    }, status=status.HTTP_200_OK)
            except (InvalidToken, Exception) as e:
                pass  # Token is invalid, continue to return False
        
        return Response({
            'authenticated': False,
            'user': None
        }, status=status.HTTP_200_OK)


from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.urls import reverse

def django_template_login(request):
    """
    Django template-based login view
    """
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            from django.contrib.auth import login
            user = form.get_user()
            login(request, user)
            messages.success(request, 'Login successful!')
            return redirect('login_success')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'simple_login.html', {'form': form})

def login_success(request):
    """
    Login success page
    """
    if request.user.is_authenticated:
        return render(request, 'login_success.html')
    else:
        return redirect('django_template_login')


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


class ProfileView(generics.RetrieveAPIView):
    """
    API endpoint for retrieving user profile by ID or current user.
    Requires JWT authentication.
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        """
        Return user profile by ID from URL parameter or current user.
        """
        # Check if user_id is provided in URL
        user_id = self.kwargs.get('user_id')
        
        if user_id:
            try:
                # Get user by ID
                user = User.objects.get(id=user_id)
                print(f"👤 Loading profile for user_id: {user_id}")
                return user
            except User.DoesNotExist:
                print(f"❌ User not found with ID: {user_id}")
                raise NotFound(f"User with ID {user_id} not found")
        else:
            # Return current authenticated user
            print(f"👤 Loading current user profile: {self.request.user.username}")
            return self.request.user
    
    def get(self, request, *args, **kwargs):
        """
        Override get method to provide better error messages.
        """
        try:
            return super().get(request, *args, **kwargs)
        except NotFound as e:
            return Response(
                {'error': str(e), 'detail': 'User not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            print(f"❌ Profile view error: {str(e)}")
            return Response(
                {'error': 'Failed to load profile', 'detail': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )


class ProfileByUsernameView(generics.RetrieveAPIView):
    """
    API endpoint for retrieving user profile by username.
    Requires JWT authentication.
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def get_object(self):
        """
        Return user profile by username from URL parameter.
        """
        username = self.kwargs.get('username')
        
        if not username:
            print(f"❌ No username provided")
            return Response(
                {'error': 'User not specified'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Get user by username
            user = User.objects.get(username=username)
            print(f"👤 Loading profile for username: {username}")
            return user
        except User.DoesNotExist:
            print(f"❌ User not found with username: {username}")
            raise NotFound(f"User '{username}' not found")
    
    def get(self, request, *args, **kwargs):
        """
        Override get method to provide better error messages.
        """
        try:
            username = self.kwargs.get('username')
            
            if not username:
                return Response(
                    {'error': 'User not specified'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            return super().get(request, *args, **kwargs)
        except NotFound as e:
            return Response(
                {'error': 'User not found', 'detail': str(e)}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            print(f"❌ Profile by username view error: {str(e)}")
            return Response(
                {'error': 'Failed to load profile', 'detail': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
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


class FollowUserView(generics.GenericAPIView):
    """
    API endpoint for following a user.
    Only authenticated users can follow other users.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, user_id):
        """
        Follow a user by user_id.
        """
        try:
            # Get the user to follow
            user_to_follow = User.objects.get(id=user_id)
            
            # Prevent self-following
            if request.user == user_to_follow:
                return Response(
                    {'error': 'You cannot follow yourself.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check if already following
            if Follow.objects.filter(follower=request.user, following=user_to_follow).exists():
                return Response(
                    {'error': 'You are already following this user.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create follow relationship
            Follow.objects.create(follower=request.user, following=user_to_follow)
            
            return Response({
                'message': f'You are now following {user_to_follow.username}.',
                'following': True
            }, status=status.HTTP_201_CREATED)
            
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': 'Failed to follow user.', 'details': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UnfollowUserView(generics.GenericAPIView):
    """
    API endpoint for unfollowing a user.
    Only authenticated users can unfollow other users.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, user_id):
        """
        Unfollow a user by user_id.
        """
        try:
            # Get the user to unfollow
            user_to_unfollow = User.objects.get(id=user_id)
            
            # Find the follow relationship
            follow_relationship = Follow.objects.filter(
                follower=request.user, 
                following=user_to_unfollow
            ).first()
            
            if not follow_relationship:
                return Response(
                    {'error': 'You are not following this user.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Delete follow relationship
            follow_relationship.delete()
            
            return Response({
                'message': f'You have unfollowed {user_to_unfollow.username}.',
                'following': False
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': 'Failed to unfollow user.', 'details': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class FollowersListView(generics.ListAPIView):
    """
    API endpoint for listing a user's followers.
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        """
        Get followers for a specific user.
        """
        user_id = self.kwargs.get('user_id')
        try:
            user = User.objects.get(id=user_id)
            # Get users who follow this user
            followers_ids = Follow.objects.filter(following=user).values_list('follower', flat=True)
            return User.objects.filter(id__in=followers_ids)
        except User.DoesNotExist:
            return User.objects.none()


class FollowingListView(generics.ListAPIView):
    """
    API endpoint for listing users that a user follows.
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        """
        Get users that this user follows.
        """
        user_id = self.kwargs.get('user_id')
        try:
            user = User.objects.get(id=user_id)
            # Get users that this user follows
            following_ids = Follow.objects.filter(follower=user).values_list('following', flat=True)
            return User.objects.filter(id__in=following_ids)
        except User.DoesNotExist:
            return User.objects.none()


