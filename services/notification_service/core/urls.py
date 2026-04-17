from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from notifications.views import NotificationViewSet

router = DefaultRouter()
router.register(r'notifications', NotificationViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/notifications/', include(router.urls)),
]
