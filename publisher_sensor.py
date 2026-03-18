import json
import random
import time
import Config
from datetime import datetime, timezone
import paho.mqtt.client as mqtt

def read_temperature_c() -> float:
    return round (random.uniform(0.0, 40.0), 2)

def on_connect(client, userdata, flags, reason_code, properties=None):
    client.publish(Config.TOPIC_ONLINE, payload="online", qos=1, retain=True)
    global connected
    print(f"[CONNECT] reason_code={reason_code}")
    connected = (reason_code == 0)
 
def on_disconnect(client, userdata, reason_code, properties=None):

    global connected
    print(f"[DISCONNECT] reason_code={reason_code}")
    connected = False

connected = False

client = mqtt.Client(
    client_id=Config.CLIENT_ID,
    protocol=mqtt.MQTTv311
)

client.on_connect = on_connect
client.on_disconnect = on_disconnect

client.will_set(
    topic=Config.TOPIC_ONLINE,
    payload="offline",
    qos=Config.QOS_STATUS_TEMP,
    retain=True
)

client.reconnect_delay_set(min_delay=1, max_delay=30)

client.connect_async(Config.MQTT_BROKER_HOST, Config.MQTT_BROKER_PORT, keepalive=Config.MQTT_KEEPALIVE)
client.loop_start()

try:
    client.publish(Config.TOPIC_ONLINE, "online", qos=Config.QOS_STATUS_TEMP, retain=True)
    while True:
        if not connected:
            print("[WAIT] en attente de connexion MQTT...")
            time.sleep(1.0)
            continue

        temperature_c = read_temperature_c()

        payload = {
            "device_id": Config.DEVICE,
            "sensor": "temperature",
            "value": temperature_c,
            "unit": "C",
            "ts": datetime.now(timezone.utc).isoformat()
        }

        client.publish(Config.TOPIC_JSON_TEMP, json.dumps(payload), qos=Config.QOS_SENSOR_TEMP, retain=False)

        client.publish(Config.TOPIC_VALUE_TEMP, str(temperature_c), qos=Config.QOS_SENSOR_TEMP, retain=False)
        print(f"[PUB] {Config.TOPIC_JSON_TEMP} -> {payload}")
        time.sleep(Config.PUBLISH_PERIOD_S_TEMP)
except KeyboardInterrupt:
    print("\n[STOP] arrêt demandé (Ctrl+C)")
finally:
    client.publish(Config.TOPIC_ONLINE, "offline", qos=Config.QOS_STATUS_TEMP, retain=True)
    client.loop_stop()
    client.disconnect() 
