import pika
import json
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from notifications.models import Notification

def callback(ch, method, properties, body):
    data = json.loads(body)
    event_type = data.get('type')
    body_data = data.get('body')

    # Example: Create notification for the owner of the artwork
    # In a real scenario, we would need to know the artwork's owner
    # Here we assume user_id is the recipient (sender triggered it)
    
    Notification.objects.create(
        user_id=body_data.get('user_id'), # Simplified
        sender_id=body_data.get('user_id'), # Sender who liked/commented
        artwork_id=body_data.get('artwork_id'),
        type=event_type,
        message=f"New {event_type} on your artwork {body_data.get('artwork_id')}"
    )

rabbitmq_url = os.environ.get('RABBITMQ_URL', 'amqp://guest:guest@rabbitmq:5672/')
params = pika.URLParameters(rabbitmq_url)
connection = pika.BlockingConnection(params)
channel = connection.channel()

channel.queue_declare(queue='notifications')
channel.basic_consume(queue='notifications', on_message_callback=callback, auto_ack=True)

print('Waiting for notifications...')
channel.start_consuming()
