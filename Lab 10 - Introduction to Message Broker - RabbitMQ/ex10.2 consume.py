import pika
import random
import datetime
import json

broker_host = "172.17.66.235"
broker_port = 5672

username = "admin"
password = "pass"
credentials = pika.PlainCredentials(username, password)

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=broker_host, port=broker_port, credentials=credentials))

channel = connection.channel()

queue_name = "kadalipp_queue"
channel.queue_declare(queue=queue_name, durable=True)

routing_key = "iotdevice.*.tempsensor"

exchange = "kadalipp"
channel.queue_bind(exchange=exchange, queue=queue_name, routing_key=routing_key)


def lab_callback(ch, method, properties, body):
    print("Inbox:% r" % body.decode())
    ch.basic_ack(delivery_tag=method.delivery_tag)


try:
    channel.basic_consume(queue=queue_name, on_message_callback=lab_callback)
    channel.start_consuming()
except KeyboardInterrupt or SystemExit:
    channel.close()
    connection.close()
