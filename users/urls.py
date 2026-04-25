from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # Traditional form-based authentication
    path('auth/', views.login_signup_view, name='auth'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/<str:username>/', views.profile_view, name='profile'),
    
    # API endpoints (for frontend-backend communication)
    path('api/login/', views.api_login, name='api_login'),
    path('api/register/', views.api_register, name='api_register'),
    path('api/logout/', views.api_logout, name='api_logout'),
    path('api/profile/', views.api_user_profile, name='api_profile'),
    path('api/csrf-token/', views.api_csrf_token, name='api_csrf_token'),
]
