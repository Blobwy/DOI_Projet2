import json
from typing import Any
import paho.mqtt.client as mqtt

BROKER_HOST = "localhost"
BROKER_PORT = 1883
KEEPALIVE_S = 60
TEAM = "jp-gauthier"
DEVICE = "pi01"
CLIENT_ID = "jp"
TOPIC_CMD = f"ahuntsic/aec-iot/b3/{TEAM}/{DEVICE}/actuators/led/cmd"
TOPIC_STATE = f"ahuntsic/aec-iot/b3/{TEAM}/{DEVICE}/actuators/led/state"
QOS_CMD = 1

def parse_command(payload_text: str) -> str | None:
    try:
        data: dict[str, Any] = json.loads(payload_text)
    except json.JSONDecodeError:
        return None

    if "state" in data and isinstance(data["state"], str):
        s = data["state"].strip().lower()
        if s in ("on", "off"):
            return s
    if "value" in data:
        v = data["value"]
        if v in (1, True, "1", "on", "ON"):
            return "on"
        if v in (0, False, "0", "off", "OFF"):
            return "off"

    return None

def on_connect(userdata, flags, reason_code, properties=None):
    print(f"[CONNECT] reason_code={reason_code}")
    if reason_code == 0:
        client.subscribe(TOPIC_CMD, qos=QOS_CMD)
        print(f"[SUB] {TOPIC_CMD} (qos={QOS_CMD})")
def on_message(userdata, msg: mqtt.MQTTMessage):
    payload_text = msg.payload.decode("utf-8", errors="replace")
    print(f"[MSG] topic={msg.topic} qos={msg.qos} retain={msg.retain} payload={payload_text}")
    command = parse_command(payload_text)
    if command is None:
        print("[WARN] Commande invalide (JSON attendu). Ignorée.")
        return


def on_disconnect(client, userdata, reason_code, properties=None):
    print(f"[DISCONNECT] reason_code={reason_code}")

client = mqtt.Client(client_id=CLIENT_ID, protocol=mqtt.MQTTv311)
client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect
client.reconnect_delay_set(min_delay=1, max_delay=30)
client.connect(BROKER_HOST, BROKER_PORT, keepalive=KEEPALIVE_S)
client.loop_forever()