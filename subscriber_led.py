import json
import paho.mqtt.client as mqtt
from gpiozero import LED
import datetime

BROKER_HOST = "localhost"
BROKER_PORT = 1883
KEEPALIVE_S = 60
TEAM = "jp-gauthier"
DEVICE = "pi01"
CLIENT_ID = "b3-sub-jp-gauthier-pi01-led"
LED_PIN_BCM = 27

TOPIC_CMD = f"ahuntsic/aec-iot/b3/{TEAM}/{DEVICE}/actuators/led/cmd"
TOPIC_STATE = f"ahuntsic/aec-iot/b3/{TEAM}/{DEVICE}/actuators/led/state"

led = LED(LED_PIN_BCM)

def publish_led_state(client: mqtt.Client):
    if led.is_lit:
        val_state = "on"
    else:
        val_state = "off"

    payload_dict = {
        "device": DEVICE,
        "actuator": "led",
        "state": val_state,
        "ts": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }

    payload_json = json.dumps(payload_dict)
    client.publish(TOPIC_STATE, payload_json, qos=1, retain=True)
    print(f" [STATE] {TOPIC_STATE} -> {payload_json}")

def parse_command(payload_text: str) -> str | None:
    try:
        data = json.loads(payload_text)
        if "state" in data:
            s = str(data["state"]).lower().strip()
            if s in ("on", "off"): return s
    except:
        pass
    return None

def on_connect(client, userdata, flags, reason_code, properties=None):
    print(f" [CONNECT] connecté au broker (code {reason_code})")
    if reason_code == 0:
        client.subscribe(TOPIC_CMD, qos=1)
        print(f" [SUB] Abonné à : {TOPIC_CMD}")
        publish_led_state(client)

def on_message(client, userdata, msg):
    payload = msg.payload.decode("utf-8", errors="replace")
    print(f"[MSG] Topic: {msg.topic} | Payload: {payload}")
    
    command = parse_command(payload)
    if command == "on":
        led.on()
    elif command == "off":
        led.off()
    else:
        print("[WARN] Commande JSON invalide reçue")
        return

    publish_led_state(client)

client = mqtt.Client(client_id=CLIENT_ID, protocol=mqtt.MQTTv311)
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER_HOST, BROKER_PORT, keepalive=KEEPALIVE_S)
print("[INFO] Subscriber LED démarré. En attente de commandes...")
client.loop_forever()