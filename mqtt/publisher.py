import random
import time
import json

from paho.mqtt import client as mqtt_client


broker = '127.0.0.1'
port = 1884
topic = 'data/'
# Generate a Client ID with the publish prefix.
client_id = f'publish-{random.randint(0, 1000)}'

device_name = 'Demo Device'
light_level = 30
relay = False


def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
            client.subscribe('data/get_light_level')
            client.subscribe('sensor/request/setRelay')
            client.subscribe(f'sensor/{device_name}/request/getRelay/+')
            client.subscribe(f'devices/{device_name}/attrs')

            client.publish('v1/devices/me/attributes/request', json.dumps({'relay': 'relay'}))
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(broker, port)
    return client


def on_message(client, userdata, msg):
    if msg.topic == 'sensor/request/setRelay':
        print(f"Set relay request received for {device_name}")
        global relay
        data = json.loads(msg.payload.decode())
        relay = bool(data)
        print(f"Set relay to {relay}")
    elif msg.topic.startswith(f'sensor/{device_name}/request/getRelay/'):
        print(f"Get relay state request received for {device_name}")
        request_id = msg.topic.split('/')[-1]
        client.publish(f'sensor/{device_name}/response/getRelay/{request_id}', json.dumps({'relay': relay}))
    elif msg.topic.startswith(f'devices/{device_name}/attrs'):
        print(f"Received attributes for {device_name}: {msg.payload.decode()}")
        data = msg.payload.decode()
        relay = bool(data)
    elif msg.topic == 'data/get_light_level':
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        s = json.loads(msg.payload.decode())
        r = s.split(';')[1].split('=')[1]
        client.publish(r, json.dumps({'light_level': light_level}))


def make_msg():
    return json.dumps({
        'frequency': random.randint(0, 100),
        'power': random.randint(0, 100),
        'temperature': random.randint(0, 100),
        'humidity': random.randint(0, 100),
        'relay': relay
    })


def publish(client):
    while True:
        msg = make_msg()
        result = client.publish(topic, msg)
        status = result[0]
        if status == 0:
            print(f"Send `{msg}` to topic `{topic}`")
        else:
            print(f"Failed to send message to topic {topic}")

        time.sleep(1)


def run():
    client = connect_mqtt()
    client.loop_start()
    publish(client)
    client.loop_stop()


if __name__ == '__main__':
    print("STARTED")
    run()
