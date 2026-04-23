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
        """Register service with Consul"""
        try:
            local_ip = self.get_local_ip()
            
            service_config = {
                'ID': f"{service_name}-{local_ip}-{service_port}",
                'Name': service_name,
                'Tags': tags or [],
                'Address': local_ip,
                'Port': service_port,
                'Check': {
                    'HTTP': health_check_url or f"http://{local_ip}:{service_port}/health/",
                    'Interval': '10s',
                    'Timeout': '3s',
                    'DeregisterCriticalServiceAfter': '30s'
                },
                'Meta': {
                    'version': '1.0.0',
                    'environment': os.environ.get('ENVIRONMENT', 'development'),
                    'service_type': 'django-microservice'
                }
            }
            
            # Register service
            self.consul.agent.service.register(service_config)
            self.service_id = service_config['ID']
            
            logger.info(f"✅ Service {service_name} registered with Consul")
            logger.info(f"   Service ID: {self.service_id}")
            logger.info(f"   Address: {local_ip}:{service_port}")
            logger.info(f"   Health Check: {service_config['Check']['HTTP']}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to register service {service_name}: {str(e)}")
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
    
    def discover_service(self, service_name):
        """Discover service instances from Consul"""
        try:
            _, services = self.consul.health.service(service_name, passing=True)
            
            if not services:
                logger.warning(f"⚠️ No healthy instances of {service_name} found")
                return []
            
            service_instances = []
            for service in services:
                instance = {
                    'service_id': service['Service']['ID'],
                    'address': service['Service']['Address'],
                    'port': service['Service']['Port'],
                    'tags': service['Service'].get('Tags', []),
                    'health': 'passing' if service['Checks'] else 'unknown'
                }
                service_instances.append(instance)
            
            logger.info(f"✅ Found {len(service_instances)} instances of {service_name}")
            return service_instances
            
        except Exception as e:
            logger.error(f"❌ Failed to discover service {service_name}: {str(e)}")
            return []
    
    def get_all_services(self):
        """Get all registered services from Consul"""
        try:
            _, services = self.consul.agent.services()
            logger.info(f"✅ Retrieved {len(services)} services from Consul")
            return services
        except Exception as e:
            logger.error(f"❌ Failed to get services: {str(e)}")
            return {}
    
    def health_check(self, service_name, service_port):
        """Perform health check for a service"""
        try:
            health_url = f"http://127.0.0.1:{service_port}/health/"
            response = requests.get(health_url, timeout=5)
            
            if response.status_code == 200:
                logger.info(f"✅ Health check passed for {service_name}")
                return True
            else:
                logger.warning(f"⚠️ Health check failed for {service_name}: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Health check error for {service_name}: {str(e)}")
            return False
    
    def start_heartbeat(self, service_name, service_port):
        """Start heartbeat to keep service healthy in Consul"""
        def heartbeat_loop():
            while self.running:
                try:
                    health_url = f"http://127.0.0.1:{service_port}/health/"
                    response = requests.get(health_url, timeout=5)
                    
                    if response.status_code != 200:
                        logger.warning(f"⚠️ Service {service_name} health check failed")
                    
                    time.sleep(10)  # Check every 10 seconds
                    
                except Exception as e:
                    logger.error(f"❌ Heartbeat error for {service_name}: {str(e)}")
                    time.sleep(10)
        
        self.registration_thread = Thread(target=heartbeat_loop, daemon=True)
        self.registration_thread.start()
        logger.info(f"✅ Started heartbeat for {service_name}")
    
    def stop_heartbeat(self):
        """Stop heartbeat thread"""
        self.running = False
        if self.registration_thread:
            self.registration_thread.join(timeout=5)
        logger.info("🛑 Heartbeat stopped")

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

def discover_service(service_name):
    """Convenience function to discover service instances"""
    registry = get_consul_registry()
    return registry.discover_service(service_name)

def get_service_url(service_name, path=""):
    """Get service URL from Consul discovery"""
    instances = discover_service(service_name)
    if not instances:
        return None
    
    # Return first healthy instance
    instance = instances[0]
    url = f"http://{instance['address']}:{instance['port']}{path}"
    logger.info(f"✅ Service URL for {service_name}: {url}")
    return url

# Signal handlers for graceful shutdown
def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info("🛑 Received shutdown signal, deregistering from Consul...")
    deregister_django_service()
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
