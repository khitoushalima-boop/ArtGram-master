from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    FollowViewSet, 
    LoginView, 
    RegisterViewSet, 
    UserViewSet,
    AchievementViewSet,
    ProfileUpdateView,
    google_login_callback,
)

router = DefaultRouter()
router.register(r"profiles", UserViewSet, basename="profiles")
router.register(r"follows", FollowViewSet, basename="follows")
router.register(r"achievements", AchievementViewSet, basename="achievements")

urlpatterns = [
    path("register/", RegisterViewSet.as_view({"post": "create"}), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("profile/update/", ProfileUpdateView.as_view(), name="profile_update"),
    
    # Google OAuth endpoint
    path("google/callback/", google_login_callback, name="google_login_callback"),
    
    path("", include(router.urls)),
]
