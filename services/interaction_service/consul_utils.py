"""
Consul Service Discovery Utilities for ArtGram Microservices
Handles automatic service registration, health checks, and deregistration
"""

import consul
import socket
import requests
import time
import logging
import signal
import sys
import os
from threading import Thread

logger = logging.getLogger(__name__)

class ConsulServiceRegistry:
    """Consul Service Registry for Django Microservices"""
    
    def __init__(self, consul_host='consul', consul_port=8500):
        self.consul_host = consul_host
        self.consul_port = consul_port
        self.consul = consul.Consul(host=consul_host, port=consul_port)
        self.service_id = None
        self.registration_thread = None
        self.running = False
        
    def get_local_ip(self):
        """Get local IP address for service registration"""
        try:
            # Connect to an external service to get local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except Exception:
            return "127.0.0.1"
    
    def register_service(self, service_name, service_port, health_check_url=None, tags=None):
        """Register service with Consul - Fixed parameter structure"""
        try:
            local_ip = self.get_local_ip()
            
            # Ensure all parameters are properly cast to strings
            service_name = str(service_name)
            service_port = int(service_port)
            local_ip = str(local_ip)
            
            # Create service ID as string
            service_id = f"{service_name}-{local_ip}-{service_port}"
            
            # Prepare health check as dictionary - use container name for internal Docker networking
            # For Docker environment, use container name for health checks
            health_check_url = health_check_url or f"http://interaction-service:8000/health/"
            health_check = {
                'HTTP': str(health_check_url),
                'Interval': '10s',
                'Timeout': '3s',
                'DeregisterCriticalServiceAfter': '30s'
            }
            
            # Prepare metadata as dictionary with string values
            meta = {
                'version': '1.0.0',
                'environment': str(os.environ.get('ENVIRONMENT', 'development')),
                'service_type': 'django-microservice'
            }
            
            # Ensure tags are list of strings
            tags = [str(tag) for tag in (tags or [])]
            
            # Register service with individual parameters (not dictionary)
            self.consul.agent.service.register(
                name=service_name,                    # ✅ Clean string
                service_id=service_id,                # ✅ Clean string
                address=local_ip,                    # ✅ Clean string
                port=service_port,                   # ✅ Integer
                tags=tags,                           # ✅ List of strings
                check=health_check                   # ✅ Dictionary
                # Note: 'meta' parameter not supported in this version of python-consul
            )
            
            self.service_id = service_id
            
            logger.info(f"✅ {service_name} registered with Consul")
            logger.info(f"   Service ID: {self.service_id}")
            logger.info(f"   Address: {local_ip}:{service_port}")
            logger.info(f"   Health Check: {health_check['HTTP']}")
            logger.info(f"   Tags: {tags}")
            logger.info(f"   Meta: {meta}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to register service {service_name}: {str(e)}")
            import traceback
            logger.error(f"📊 Full traceback: {traceback.format_exc()}")
            return False
    
    def deregister_service(self, service_id=None):
        """Deregister service from Consul"""
        try:
            service_id = service_id or self.service_id
            if service_id:
                self.consul.agent.service.deregister(service_id)
                logger.info(f"✅ Service {service_id} deregistered from Consul")
            else:
                logger.warning("⚠️ No service ID provided for deregistration")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to deregister service: {str(e)}")
            return False

# Global Consul registry instance
consul_registry = None

def get_consul_registry():
    """Get or create global Consul registry instance"""
    global consul_registry
    if consul_registry is None:
        consul_host = os.environ.get('CONSUL_HOST', 'consul')
        consul_port = int(os.environ.get('CONSUL_PORT', '8500'))
        consul_registry = ConsulServiceRegistry(consul_host, consul_port)
    return consul_registry

def register_django_service(service_name, service_port, health_check_url=None, tags=None):
    """Convenience function to register Django service with Consul"""
    registry = get_consul_registry()
    return registry.register_service(service_name, service_port, health_check_url, tags)

def deregister_django_service(service_id=None):
    """Convenience function to deregister Django service from Consul"""
    registry = get_consul_registry()
    return registry.deregister_service(service_id)

# Signal handlers for graceful shutdown
def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info("🛑 Received shutdown signal, deregistering from Consul...")
    deregister_django_service()
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
