import json
import datetime
import Config
import paho.mqtt.client as mqtt
from gpiozero import LED


led = LED(Config.LED_PIN_BCM)

def publish_led_state(client: mqtt.Client):
    if led.is_lit:
        val_state = "on"
    else:
        val_state = "off"

    payload_dict = {
        "device": Config.DEVICE,
        "actuator": "led",
        "state": val_state,
        "ts": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }

    payload_json = json.dumps(payload_dict)
    client.publish(Config.TOPIC_STATE, payload_json, qos=1, retain=True)
    print(f" [STATE] {Config.TOPIC_STATE} -> {payload_json}")

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
        client.publish(Config.TOPIC_ONLINE, payload="online", qos=1, retain=True)
        client.subscribe(Config.TOPIC_CMD, qos=1)
        print(f" [SUB] Abonné à : {Config.TOPIC_CMD}")
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
    
client = mqtt.Client(client_id=Config.CLIENT_ID, protocol=mqtt.MQTTv311)
client.will_set(Config.TOPIC_ONLINE, payload="offline", qos=1, retain=True)
client.on_connect = on_connect
client.on_message = on_message

client.connect(Config.MQTT_BROKER_HOST, Config.MQTT_BROKER_PORT, keepalive=Config.MQTT_KEEPALIVE)
print("[INFO] Subscriber LED démarré. En attente de commandes...")
client.loop_forever()