from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    FollowViewSet, 
    LoginView, 
    RegisterViewSet, 
    UserViewSet,
    AchievementViewSet,
    ProfileView,
    ProfileByUsernameView,
    ProfileUpdateView,
    google_login_callback,
    ping_endpoint,
    health_check,
)

router = DefaultRouter()
router.register(r"profiles", UserViewSet, basename="profiles")
router.register(r"follows", FollowViewSet, basename="follows")
router.register(r"achievements", AchievementViewSet, basename="achievements")

urlpatterns = [
    path("ping/", ping_endpoint, name="ping"),
    path("health/", health_check, name="health_check"),
    path("register/", RegisterViewSet.as_view({"post": "create"}), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("profile/<int:user_id>/", ProfileView.as_view(), name="profile_by_id"),
    path("profile/username/<str:username>/", ProfileByUsernameView.as_view(), name="profile_by_username"),
    path("profile/update/", ProfileUpdateView.as_view(), name="profile_update"),
    
    # Google OAuth endpoint
    path("google/callback/", google_login_callback, name="google_login_callback"),
    
    path("", include(router.urls)),
]
