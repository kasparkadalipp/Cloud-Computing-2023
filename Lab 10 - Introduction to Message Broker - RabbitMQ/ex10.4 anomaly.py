import pika
import json
from termcolor import colored # pip install termcolor

broker_host = "172.17.66.235"
broker_port = 5672
username = "admin"
password = "pass"

exchange = "kadalipp"
queue_name = "outdoor_queue"
# input_routing_key = "puhatu.kadalipp.anomaly"
input_routing_key = "puhatu.kadalipp.outdoor"

credentials = pika.PlainCredentials(username, password)
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=broker_host, port=broker_port, credentials=credentials))
channel = connection.channel()

# Create a new queue
channel.queue_declare(queue=queue_name, durable=True)

# Binding Exchange and queue with the routing key
channel.queue_bind(exchange=exchange, queue=queue_name, routing_key=input_routing_key)

indoor_devices = ['fipy_e1', 'fipy_b1', 'fipy_b2', 'fipy_b3']
outdoor_devices = ['puhatu_b1', 'puhatu_b2', 'puhatu_b3', 'puhatu_c1', 'puhatu_c2', 'puhatu_c3', 'puhatu_l1']


def lab_callback(ch, method, properties, body):
    message = json.loads(body.decode())
    dist = message['dist']
    air_Temp_float = message['air_Temp_float']
    if float(dist) > 70:
        output_routing_key = "puhatu.kadalipp.anomaly.dist "
        dist = colored(dist, "red")
    elif float(air_Temp_float) > 25:
        output_routing_key = "puhatu.kadalipp.anomaly.air_Temp_float "
        air_Temp_float = colored(air_Temp_float, "red")
    else:
        return
    print(f"The IoT device {message['dev_id']} has anomaly data: dist: {dist}, air_Temp_float: {air_Temp_float}")
    ch.basic_publish(exchange = exchange, routing_key = output_routing_key, body = body.decode())


# anomaly
# channel.queue_declare(queue ="anomaly_queue", durable = True)
# channel.queue_bind(exchange = exchange, queue ="anomaly_queue", routing_key = "puhatu.kadalipp.anomaly.*")

try:
    channel.basic_consume(queue=queue_name, on_message_callback=lab_callback)
    channel.start_consuming()
except KeyboardInterrupt or SystemExit:
    channel.close()
    connection.close()
