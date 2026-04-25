from django.apps import AppConfig
import os


class NotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notifications'
    
    def ready(self):
        # Register service with Consul
        try:
            from consul_utils import register_django_service
            from django.conf import settings
            
            # Get service configuration with proper string casting
            service_name = str(os.environ.get('SERVICE_NAME', 'notification-service'))
            service_port = int(os.environ.get('SERVICE_PORT', '8005'))
            # Use container name for Consul health checks (internal Docker networking)
            health_check_url = f"http://notification-service:8000/health/"
            
            # Service tags for discovery
            tags = [
                'django',
                'microservice',
                'api',
                'artgram',
                'notification',
                'messaging',
                os.environ.get('ENVIRONMENT', 'development')
            ]
            
            # Register with Consul
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
