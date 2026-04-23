# Consul Service Discovery Implementation for ArtGram Microservices

## Overview
This document provides a complete implementation of automated Service Discovery using HashiCorp Consul for the ArtGram Django microservices project.

## 🏗️ Architecture

```
┌─────────────────┐
│   Consul UI    │  http://localhost:8500
│   (Port 8500)   │
└─────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────┐
│  User Service  │  Artwork Service  │  Interaction Service  │  Notification Service
│  (Port 8000)   │  (Port 8002)     │  (Port 8003)          │  (Port 8004)
└─────────────────────────────────────────────────┘
        │
        ▼
    Consul Agent
    (Auto Registration)
```

## 📁 Files Created

### 1. Consul Utilities (`consul_utils.py`)
```python
# Key Features:
- Automatic service registration
- Health check implementation
- Service discovery
- Graceful deregistration
- Heartbeat monitoring
- Dynamic IP detection
```

### 2. Health Check Views (`health_views.py`)
```python
# Endpoints:
- /health/      - Comprehensive health check
- /ready/      - Readiness probe for K8s
- /live/       - Liveness probe for K8s
- /metrics/     - System metrics
```

### 3. Health URLs (`health_urls.py`)
```python
# URL patterns for health endpoints
app_name = 'health'
urlpatterns = [
    path('health/', health_views.health_check_view),
    path('ready/', health_views.readiness_check_view),
    path('live/', health_views.liveness_check_view),
    path('metrics/', health_views.metrics_view),
]
```

## 🔧 Configuration

### Docker Compose Integration
```yaml
# Environment Variables
SERVICE_NAME=user-service
SERVICE_PORT=8000
CONSUL_HOST=consul
CONSUL_PORT=8500
ENVIRONMENT=development

# Docker Labels
artgram.service=user-service
artgram.version=1.0.0
artgram.environment=development
consul.service.enable=true
```

### Django Settings Integration
```python
# core/settings.py
SERVICE_NAME = env('SERVICE_NAME', default='user-service')
SERVICE_PORT = env('SERVICE_PORT', default='8000')
CONSUL_HOST = env('CONSUL_HOST', default='consul')
CONSUL_PORT = env('CONSUL_PORT', default='8500')

# URL Configuration
from django.urls import include, path
urlpatterns = [
    path('api/health/', include('health_urls')),
    path('', include('accounts.urls')),
]
```

## 🚀 Service Registration

### Automatic Registration on Startup
```python
# accounts/apps.py
def ready(self):
    try:
        from consul_utils import register_django_service
        
        service_name = getattr(settings, 'SERVICE_NAME', 'user-service')
        service_port = int(os.environ.get('SERVICE_PORT', '8000'))
        health_check_url = f"http://127.0.0.1:{service_port}/health/"
        
        tags = [
            'django',
            'microservice',
            'api',
            'artgram',
            'authentication',
            os.environ.get('ENVIRONMENT', 'development')
        ]
        
        success = register_django_service(
            service_name=service_name,
            service_port=service_port,
            health_check_url=health_check_url,
            tags=tags
        )
        
        if success:
            print(f"✅ {service_name} registered with Consul")
        else:
            print(f"❌ Failed to register {service_name} with Consul")
            
    except Exception as e:
        print(f"❌ Error registering service with Consul: {str(e)}")
```

## 🔍 Service Discovery

### Finding Service Instances
```python
from consul_utils import discover_service

# Discover all user-service instances
services = discover_service('user-service')

for service in services:
    print(f"Service ID: {service['service_id']}")
    print(f"Address: {service['address']}:{service['port']}")
    print(f"Health: {service['health']}")
    print(f"Tags: {service['tags']}")
```

### Getting Service URL
```python
from consul_utils import get_service_url

# Get user-service URL
user_service_url = get_service_url('user-service')

# Returns: http://192.168.1.100:8000
```

## 🏥 Health Checks

### Comprehensive Health Endpoint
```json
GET /api/health/

Response:
{
    "status": "healthy",
    "timestamp": 1649385600,
    "service": "user-service",
    "version": "1.0.0",
    "checks": {
        "database": "healthy",
        "memory_usage": "45.2%",
        "disk_usage": "23.1%",
        "response_time_ms": 12
    },
    "metadata": {
        "environment": "development",
        "debug": true,
        "host": "localhost"
    }
}
```

### Health Status Codes
- **200** - Service is healthy
- **503** - Service is unhealthy (database issues, high memory/disk)
- **500** - Service error (exception occurred)

## 🔄 Service Lifecycle

### Registration Process
1. **Service Starts** → Django `apps.py` calls `ready()`
2. **Consul Registration** → Service registered with health check URL
3. **Health Monitoring** → Consul checks service every 10 seconds
4. **Service Discovery** → Other services can find this service via Consul

### Deregistration Process
1. **Graceful Shutdown** → Signal handlers trigger deregistration
2. **Consul Cleanup** → Service removed from service catalog
3. **Heartbeat Stop** → Health check monitoring stops

## 📊 Monitoring & Metrics

### Health Check Metrics
```json
GET /api/health/metrics/

Response:
{
    "timestamp": 1649385600,
    "service": "user-service",
    "system": {
        "cpu_percent": 15.2,
        "memory": {
            "total": 8589934592,
            "available": 4563402752,
            "percent": 45.2
        },
        "disk": {
            "total": 500000000000,
            "free": 384500000000,
            "percent": 23.1
        }
    }
}
```

## 🌐 API Endpoints

### Service Discovery Endpoints
```
# Consul UI
http://localhost:8500

# Health Checks
GET http://localhost:8000/api/health/health/
GET http://localhost:8000/api/health/ready/
GET http://localhost:8000/api/health/live/
GET http://localhost:8000/api/health/metrics/

# Service Discovery (via Consul API)
GET http://localhost:8500/v1/health/service/user-service
```

## 🐳 Docker Integration

### Container Labels for Service Discovery
```yaml
labels:
  - "artgram.service=user-service"
  - "artgram.version=1.0.0"
  - "artgram.environment=development"
  - "consul.service.enable=true"
```

### Environment Variables
```yaml
environment:
  - SERVICE_NAME=user-service
  - SERVICE_PORT=8000
  - CONSUL_HOST=consul
  - CONSUL_PORT=8500
  - ENVIRONMENT=development
```

## 🔧 Requirements

### Python Dependencies
```txt
django==5.1.0
djangorestframework==3.15.2
python-consul==1.1.0
psutil==5.9.0
```

### Consul Configuration
- **Consul Agent**: Running at `consul:8500`
- **Service Registration**: Automatic on Django startup
- **Health Checks**: Every 10 seconds
- **Service Discovery**: Via Consul API or UI

## 🚀 Usage Instructions

### 1. Update Requirements
```bash
pip install python-consul psutil
```

### 2. Configure Environment
```bash
export CONSUL_HOST=consul
export CONSUL_PORT=8500
export SERVICE_NAME=user-service
export SERVICE_PORT=8000
```

### 3. Start Services
```bash
docker-compose up -d
```

### 4. Verify Registration
```bash
# Check Consul UI
http://localhost:8500

# Check service health
curl http://localhost:8000/api/health/

# Discover services
curl http://localhost:8500/v1/health/service/user-service
```

## 🎯 Benefits

### ✅ **Automatic Service Discovery**
- No hardcoded service URLs
- Dynamic load balancing
- Service health monitoring
- Graceful failover handling
- Zero-downtime deployments

### ✅ **Kubernetes Ready**
- Liveness and readiness probes
- Health check endpoints
- Container labels for service discovery
- Environment-based configuration

### ✅ **Production Ready**
- Service versioning
- Environment-specific tags
- Health check timeouts
- Graceful shutdown handling
- Comprehensive monitoring

This implementation provides a robust, production-ready service discovery system for your ArtGram microservices architecture using HashiCorp Consul.
