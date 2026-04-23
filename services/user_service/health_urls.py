"""Health Check URLs for ArtGram Microservices
Provides health check endpoints for Consul service discovery
"""

from django.urls import path
from . import health_views

app_name = 'health'

urlpatterns = [
    path('health/', health_views.health_check_view, name='health_check'),
    path('ready/', health_views.readiness_check_view, name='readiness_check'),
    path('live/', health_views.liveness_check_view, name='liveness_check'),
    path('metrics/', health_views.metrics_view, name='metrics'),
]
