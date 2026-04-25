from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    FollowViewSet, 
    LoginView, 
    DjangoLoginView,
    DjangoLogoutView,
    DjangoSessionView,
    django_template_login,
    login_success,
    RegisterViewSet, 
    UserViewSet,
    AchievementViewSet,
    ProfileView,
    ProfileByUsernameView,
    ProfileUpdateView,
    FollowUserView,
    UnfollowUserView,
    FollowersListView,
    FollowingListView,
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
    path("django-login/", DjangoLoginView.as_view(), name="django_login"),
    path("django-logout/", DjangoLogoutView.as_view(), name="django_logout"),
    path("session/", DjangoSessionView.as_view(), name="django_session"),
    path("template-login/", django_template_login, name="django_template_login"),
    path("login-success/", login_success, name="login_success"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("profile/<int:user_id>/", ProfileView.as_view(), name="profile_by_id"),
    path("profile/username/<str:username>/", ProfileByUsernameView.as_view(), name="profile_by_username"),
    path("profile/update/", ProfileUpdateView.as_view(), name="profile_update"),
    
    # Follow/Unfollow endpoints
    path("follow/<int:user_id>/", FollowUserView.as_view(), name="follow_user"),
    path("unfollow/<int:user_id>/", UnfollowUserView.as_view(), name="unfollow_user"),
    path("followers/<int:user_id>/", FollowersListView.as_view(), name="followers_list"),
    path("following/<int:user_id>/", FollowingListView.as_view(), name="following_list"),
    
    # Google OAuth endpoint
    path("google/callback/", google_login_callback, name="google_login_callback"),
    
    path("", include(router.urls)),
]
