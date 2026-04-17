import pika
import json
import os

def publish_event(event_type, body):
    rabbitmq_url = os.environ.get('RABBITMQ_URL', 'amqp://guest:guest@rabbitmq:5672/')
    params = pika.URLParameters(rabbitmq_url)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()

    channel.queue_declare(queue='notifications')

    message = {
        'type': event_type,
        'body': body
    }
    
    channel.basic_publish(
        exchange='',
        routing_key='notifications',
        body=json.dumps(message)
    )
    connection.close()
