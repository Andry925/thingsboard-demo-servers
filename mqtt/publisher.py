import random
import time
import json

from paho.mqtt import client as mqtt_client


broker = '127.0.0.1'
port = 1884
topic = 'data/'
# Generate a Client ID with the publish prefix.
client_id = f'publish-{random.randint(0, 1000)}'


def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def make_msg():
    return json.dumps({
        'frequency': random.randint(0, 100),
        'power': random.randint(0, 100),
        'temperature': random.randint(0, 100),
        'humidity': random.randint(0, 100)
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
