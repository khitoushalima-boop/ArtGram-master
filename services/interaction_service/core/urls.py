from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from interactions.views import LikeViewSet, CommentViewSet

router = DefaultRouter()
router.register(r'likes', LikeViewSet)
router.register(r'comments', CommentViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/interactions/', include(router.urls)),
]
