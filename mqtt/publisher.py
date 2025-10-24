import time
import json, random, struct

from paho.mqtt import client as mqtt_client

BROKER = '127.0.0.1'
PORT = 1884
CLIENT_ID = f'publish-{random.randint(0, 1000)}'

DEVICE_NAME = "Demo Device"
SERIAL_NUMBER = "SN-001"
SENSOR_NAME = "Thermo-A"
SENSOR_TYPE = "Thermometer"
SENSOR_MODEL = "T-1000"
USERNAME = "username"
PASSWORD = "username"
DEVICE_NAME_FROM_RAW_BYTES = "AM-1"

relay = False
light_level = 30


def on_connect(client, userdata, flags, rc):
    if rc == 0:  # rc stands for result code if not zero the connection may be corrupted
        print("Connected to MQTT v5 broker")

        # Original subscriptions
        client.subscribe("data/get_light_level")
        client.subscribe("sensor/request/setRelay")
        client.subscribe(f"sensor/{DEVICE_NAME}/request/getRelay/+")
        client.subscribe(f"devices/{DEVICE_NAME}/attrs")

        # Optional: listen for attribute request demo
        client.subscribe("v1/devices/me/attributes/request")
        req = {"relay": "relay"}
        client.publish("v1/devices/me/attributes/request", json.dumps(req), )
    else:
        print(f"Connect failed: rc={rc}")


def generate_messages():
    return {
        "temp": round(random.uniform(18.0, 28.0), 2),
        "hum": round(random.uniform(30.0, 70.0), 2),
        "current": round(random.uniform(0.1, 3.0), 2),
        "Temp_1": round(random.uniform(18.0, 28.0), 2),
        "energy": round(random.uniform(100.0, 200.0), 2),
        "power": round(random.uniform(10.0, 500.0), 2),
        "pf": round(random.uniform(0.7, 1.0), 2),

    }


def parse_incoming_payload_data(payload_bytes):
    """Accept either a JSON string (e.g. '"sensor;level=topic/to/reply"') or plain text."""
    content = None
    try:
        content = payload_bytes.decode('utf-8')
        json_data = json.loads(content)
        if isinstance(json_data, str):
            return json_data
        return content
    except Exception as e:
        print("An error occurred: while parsing incoming payload", e)
        return content


def on_message(client, userdata, message):
    global relay, light_level
    topic = message.topic
    payload = message.payload
    if topic == "sensor/request/setRelay":
        # Expecting JSON: true/false or 1/0
        try:
            data = json.loads(payload.decode())
            relay = bool(data)
            print(f"[SET] relay -> {relay}")
        except Exception as e:
            print(f"[SET] bad payload: {e}")

    elif topic.startswith(f"sensor/{DEVICE_NAME}/request/getRelay/"):
        request_id = topic.split("/")[-1]
        resp_topic = f"sensor/{DEVICE_NAME}/response/getRelay/{request_id}"
        client.publish(resp_topic, json.dumps({"relay": relay}))
        print(f"[GET] relay={relay} -> {resp_topic}")

    elif topic.startswith(f"devices/{DEVICE_NAME}/attrs"):
        print(f"Received attributes for {DEVICE_NAME}: {payload.decode()}")
        data = payload.decode()
        relay = bool(data)

    elif topic == "data/get_light_level":
        # Old “JSON string that then gets split” path; also accepts plain text
        json_data = parse_incoming_payload_data(payload)
        try:
            print(f"Received RPC request `{payload.decode()}` from `{topic}` topic")
            reply_topic = json_data.split(";")[1].split("=")[1]
            light_level = random.randint(0, 100)
            client.publish(reply_topic, json.dumps({"light_level": light_level}))
        except Exception as e:
            print(f"[RPC] bad format for get_light_level: err={e}")


def publish(client):
    messages = generate_messages()

    client.publish(
        "data/",
        json.dumps({
            'frequency': random.randint(0, 100),
            'power': random.randint(0, 100),
            'temperature': random.randint(0, 100),
            'humidity': random.randint(0, 100),
            'relay': relay
        }
        ))

    # sensor/data  — message-based device info
    client.publish("sensor/data", json.dumps({
        "serialNumber": SERIAL_NUMBER,
        "sensorType": SENSOR_TYPE,
        "sensorModel": SENSOR_MODEL,
        "temp": messages["temp"],
        "hum": messages["hum"]
    }))
    client.publish(f"sensor/{SENSOR_NAME}/data", json.dumps({
        "sensorModel": SENSOR_MODEL,
        "temp": messages["temp"],
        "hum": messages["hum"]
    }))

    name4 = (DEVICE_NAME_FROM_RAW_BYTES[:4]).encode("ascii", errors="ignore").ljust(4, b"_")
    raw = name4 + struct.pack(">f", messages["temp"])  # 4 + 4 bytes
    client.publish("sensor/raw_data", raw)

    client.publish(f"custom/sensors/{SENSOR_NAME}", json.dumps({
        "temperature": messages["temp"],
        "humidity": messages["hum"],
        "batteryLevel": random.randint(20, 100)
    }))

    client.publish("data/metrics", json.dumps({
        "serialNumber": SERIAL_NUMBER,
        "temp": messages["temp"]
    }))


def main():
    client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION1, client_id=CLIENT_ID)
    client.username_pw_set(username=USERNAME, password=PASSWORD)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, PORT)
    client.loop_start()
    try:
        while True:
            publish(client)
            time.sleep(1)
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    print("Starting publisher")
    main()
