from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.notifications_view, name='home'),
    path('mark-read/<int:pk>/', views.mark_read, name='mark_read'),
]
