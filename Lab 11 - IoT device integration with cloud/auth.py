import asyncio
import uuid
from azure.iot.device.aio import ProvisioningDeviceClient
from azure.iot.device.aio import IoTHubDeviceClient
from azure.iot.device import Message
import json, os, random
import pandas as pd

provisioning_host = "global.azure-devices-provisioning.net"
id_scope = "0ne009F4281"
request_key = os.getenv('REQUEST_KEY')
device_id = "kadalipp-device-01"

# USE this to generate key
# reg_id = str(uuid.uuid4())
# enrollment_key = os.getenv('ENROLLMENT_KEY')

dataframe = pd.read_csv('puhatu.csv')
messages = json.loads(dataframe.to_json(orient="records"))

async def main():
    provisioning_device_client = ProvisioningDeviceClient.create_from_symmetric_key(
        provisioning_host=provisioning_host,
        registration_id=device_id,
        id_scope=id_scope,
        symmetric_key=request_key,
    )
    registration_result = await provisioning_device_client.register()

    if registration_result.status == "assigned":
        print("Registration succeeded")
        device_client = IoTHubDeviceClient.create_from_symmetric_key(
            symmetric_key=request_key,
            hostname=registration_result.registration_state.assigned_hub,
            device_id=registration_result.registration_state.device_id,
        )
        # Connect the client.
        await device_client.connect()
        print("Device connected successfully")

        message_json = random.choice(messages)
        msg_data = json.dumps(message_json)

        message = Message(msg_data)
        message.message_id = uuid.uuid4()

        await device_client.send_message(message)



if __name__ == "__main__":
    asyncio.run(main())