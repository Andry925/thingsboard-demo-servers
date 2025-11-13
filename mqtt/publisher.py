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
CUSTOM_DEVICE_NAME = "AN-1"
SENSOR_MODEL = "T-1000"
DEVICE_NAME_FROM_RAW_BYTES = "AM-1"

relay = False
light_level = 30


def on_connect(client, userdata, flags, rc):
    if rc == 0:  # rc stands for result code if not zero the connection may be corrupted
        print("Connected to MQTT v5 broker")

        # Original subscriptions
        client.subscribe("data/get_light_level")
        client.subscribe("data/set_light_level")
        client.subscribe("sensor/request/setRelay")
        client.subscribe(f"sensor/{DEVICE_NAME}/request/getRelay/+")
        client.subscribe(f"devices/{DEVICE_NAME}/attrs")
        client.subscribe('sensor/+/request/+/+')
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
        "energy": round(random.uniform(100.0, 200.0), 2),
        "power": round(random.uniform(10.0, 500.0), 2),
        "pf": round(random.uniform(0.7, 1.0), 2),
        "battery": round(random.uniform(30.0, 90.0), 2),

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
            client.publish(reply_topic, json.dumps({"light_level": light_level}))
        except Exception as e:
            print(f"[RPC] bad format for get_light_level: err={e}")

    elif topic == "data/set_light_level":
        json_data = parse_incoming_payload_data(payload)
        try:
            print(f"Received RPC request `{payload.decode()}` from `{topic}` topic")
            light_level = json_data

            client.publish("data/response", json.dumps({"light_level": light_level}))

        except Exception as e:
            print(f"[RPC] bad format for set_light_level: err={e}")


    elif topic.startswith('sensor') and '/request/' in topic:
        print('This is custom a Two-way RPC call. Going to reply now!')
        try:
            json_payload = json.loads(payload)
            request_id = topic.split('/')[-1]

            received_rpc = json.dumps({"light_level": light_level})
            print('Sending a response message: ' + received_rpc)
            client.publish(f"sensor/{json_payload['deviceName']}/response/{json_payload['methodName']}/{request_id}",
                           received_rpc)
            print('Sent a response message: ' + received_rpc)
        except Exception as e:
            print(f"[RPC] bad format to handle: err={e}")


def be_bytes(value: int, length: int) -> bytes:
    value = max(0, int(value))
    maxv = (1 << (8 * length)) - 1
    return min(value, maxv).to_bytes(length, byteorder='little')


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

    temperature = str(random.randint(20, 30))
    whole_data = DEVICE_NAME_FROM_RAW_BYTES + temperature
    frame = bytes(whole_data, 'utf-8')
    client.publish("sensor/raw_data", frame)

    temp_scaled = int(round(messages["temp"] * 100))  # two bytes
    hum_pct = int(round(messages["hum"]))  # one byte
    battery = int(round(messages["battery"]))  # one byte

    frame = b"".join([
        be_bytes(temp_scaled, 2),
        be_bytes(hum_pct, 1),
        be_bytes(battery, 1),
    ])

    hex_payload = "0x" + frame.hex()  # e.g. 0x092964
    client.publish(f"custom/sensors/{CUSTOM_DEVICE_NAME}", hex_payload)


def main():
    client = mqtt_client.Client(client_id=CLIENT_ID)
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
