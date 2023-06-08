import pika
import json
import pandas as pd

broker_host = "172.17.66.235"
broker_port = 5672
username = "admin"
password = "pass"

exchange = "kadalipp"
routing_key = "puhatu.kadalipp.raw"

credentials = pika.PlainCredentials(username, password)
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=broker_host, port=broker_port, credentials=credentials))
channel = connection.channel()

dataframe = pd.read_csv('puhatu.csv')
messages = json.loads(dataframe.to_json(orient="records"))

i = 0
try:
    while True:
        message = json.dumps(messages[i])
        channel.basic_publish(exchange=exchange, routing_key=routing_key, body=message)
        print("Published message:", message)
        connection.sleep(1)  # Sleep for x seconds before publishing the next message
        i += 1
        if i >= len(messages):
            i = 0
except KeyboardInterrupt or SystemExit:
    channel.close()
    connection.close()
