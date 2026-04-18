from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('auth/', views.login_signup_view, name='auth'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/<str:username>/', views.profile_view, name='profile'),
]
