import pika
import random
import datetime
import json

broker_host = "172.17.66.235"
broker_port = 5672
username = "admin"
password = "pass"

exchange = "kadalipp"
routing_key = "iotdevice.kadalipp.tempsensor"

credentials = pika.PlainCredentials(username, password)
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=broker_host, port=broker_port, credentials=credentials))
channel = connection.channel()

try:
    while True:
        message = {
            "device_name": "kadalipp_sensor",
            "temperature": random.randint(20, 40),
            "time": str(datetime.datetime.now())
        }

        message_str = json.dumps(message)
        channel.basic_publish(exchange=exchange, routing_key=routing_key, body=message_str)
        print("Published message:", message)
        connection.sleep(5)  # Sleep for 5 seconds before publishing the next message
except KeyboardInterrupt or SystemExit:
    channel.close()
    connection.close()
