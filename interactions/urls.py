from django.urls import path
from . import views

app_name = 'interactions'

urlpatterns = [
    path('like/<int:artwork_id>/', views.like_artwork, name='like'),
    path('comment/<int:artwork_id>/', views.comment_artwork, name='comment'),
    path('follow/<str:username>/', views.follow_user, name='follow'),
]
