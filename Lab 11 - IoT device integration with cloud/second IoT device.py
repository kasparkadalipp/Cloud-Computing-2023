from base64 import b64encode, b64decode
from hashlib import sha256
from time import time, sleep
from urllib import parse
from hmac import HMAC
import uamqp, uuid, urllib, json, os, random
import pandas as pd

def generate_sas_token(uri, key, policy_name, expiry=3600):
    ttl = time() + expiry
    sign_key = "%s\n%d" % ((parse.quote_plus(uri)), int(ttl))
    print(sign_key)
    signature = b64encode(HMAC(b64decode(key), sign_key.encode('utf-8'), sha256).digest())

    rawtoken = {
        'sr' :  uri,
        'sig': signature,
        'se' : str(int(ttl))
    }

    if policy_name is not None:
        rawtoken['skn'] = policy_name

    return 'SharedAccessSignature ' + parse.urlencode(rawtoken)


iot_hub_name = "kadalipp"
hostname = "kadalipp.azure-devices.net"
device_id = "kadalipp-device-01"
username = f'{device_id}@sas.{iot_hub_name}'
access_key = os.getenv('ACCESS_KEY')
sas_token = generate_sas_token(f'{hostname}/devices/{device_id}'.format(hostname=hostname, device_id=device_id), access_key, None)
operation = f'/devices/{device_id}/messages/events'.format(device_id=device_id)
uri = 'amqps://{}:{}@{}{}'.format(urllib.parse.quote_plus(username), urllib.parse.quote_plus(sas_token), hostname, operation)


dataframe = pd.read_csv('puhatu.csv')
messages = json.loads(dataframe.to_json(orient="records"))

with uamqp.SendClient(uri, debug=True) as send_client:
    while True:
        msg_props = uamqp.message.MessageProperties()
        msg_props.message_id = str(uuid.uuid4())
        message_json = random.choice(messages)
        msg_data = json.dumps(message_json)
        # msg_data = {'temperature': 22}
        message = uamqp.Message(msg_data, properties=msg_props)
        print(f"device: {device_id}, send message {message}")
        result = send_client.send_message(message)
        print(result)
        sleep(10)