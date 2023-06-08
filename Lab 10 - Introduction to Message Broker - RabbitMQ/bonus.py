import pika
import json

broker_host = "172.17.66.235"
broker_port = 5672
username = "admin"
password = "pass"

exchange = "kadalipp"
queue_name = "puhatu_queue"
input_routing_key = "puhatu.kadalipp.raw"

credentials = pika.PlainCredentials(username, password)
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=broker_host, port=broker_port, credentials=credentials))
channel = connection.channel()



def lab_callback(ch, method, properties, body):
    message = dict(json.loads(body.decode()))
    message.pop("name")
    for name, value in message.items():
        ch.basic_publish(exchange=exchange, routing_key=f"puhatu.kadalipp.raw.{name}", body=str(value))
        print(f"Publish: puhatu.kadalipp.raw.{name}")

# Create a new queue
channel.queue_declare(queue="bonus_queue", durable=True)
# Binding Exchange and queue with the routing key
channel.queue_bind(exchange=exchange, queue="bonus_queue", routing_key=f"{input_routing_key}.*")

try:
    channel.basic_consume(queue=queue_name, on_message_callback=lab_callback)
    channel.start_consuming()
except KeyboardInterrupt or SystemExit:
    channel.close()
    connection.close()
