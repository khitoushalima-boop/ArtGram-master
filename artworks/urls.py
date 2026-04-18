from django.urls import path
from . import views

app_name = 'artworks'

urlpatterns = [
    path('', views.home, name='home'),
    path('artwork/<int:pk>/', views.artwork_detail, name='artwork_detail'),
    path('search/', views.search_view, name='search'),
]
