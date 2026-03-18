import json
import Config
from datetime import datetime, timezone
from typing import Any, Optional

import pymysql
import paho.mqtt.client as mqtt

def utc_now_naive() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)

def db_connect() -> pymysql.connections.Connection:
    return pymysql.connect(
    host=Config.DB_HOST,
    user=Config.DB_USER,
    password=Config.DB_PASSWORD,
    database=Config.DB_NAME,
    autocommit=True,
    charset="utf8mb4",
 )

db = db_connect()

def extract_device(topic: str) -> str:
    parts = topic.split("/")
    return parts[4] if len(parts) >= 5 else "unknown"

def is_telemetry(topic: str) -> bool:
    if "/sensors/" not in topic:
        return False
    if topic.endswith("/value"):
        return False
    return True

def classify_kind(topic: str) -> str:
    if "/cmd/" in topic:
        return "cmd"
    if "/state/" in topic:
        return "state"
    if "/status/" in topic:
        return "status"
    return "other"
    
def try_parse_json(payload_text: str) -> Optional[dict[str, Any]]:
    try:
        obj = json.loads(payload_text)
        return obj if isinstance(obj, dict) else None
    except json.JSONDecodeError:
        return None

def insert_telemetry(ts_utc: datetime, device: str, topic: str, payload_text: str) -> None:

    obj = try_parse_json(payload_text)
    value = None
    unit = None

    if obj is not None:
        if "value" in obj:
            try:
                value = float(obj["value"])
            except (TypeError, ValueError):
                value = None
        if "unit" in obj and isinstance(obj["unit"], str):
            unit = obj["unit"][:16]

        sql = """
            INSERT INTO telemetry (ts_utc, device, topic, value, unit, payload)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
 
        with db.cursor() as cur:
            cur.execute(sql, (ts_utc, device, topic, value, unit, payload_text))

def insert_event(ts_utc: datetime, device: str, topic: str, kind: str, payload_text: str) -> None:

    sql = """
        INSERT INTO events (ts_utc, device, topic, kind, payload)
        VALUES (%s, %s, %s, %s, %s)
        """
    with db.cursor() as cur:
        cur.execute(sql, (ts_utc, device, topic, kind, payload_text))

def on_connect(client, _userdata, _flags, reason_code, properties=None):
    print(f"[CONNECT] reason_code={reason_code}")
    if reason_code == 0:
        client.subscribe(Config.MQTT_TOPIC_FILTER, qos=0)
        client.publish(Config.TOPIC_ONLINE, payload="online", qos=1, retain=True)
        print(f"[SUB] {Config.MQTT_TOPIC_FILTER}")
    else:
        print("[ERROR] Connexion MQTT échouée.")

def on_message(_client, _userdata, msg: mqtt.MQTTMessage):

    topic = msg.topic
    payload_text = msg.payload.decode("utf-8", errors="replace")
    device = extract_device(topic)
    ts = utc_now_naive()
    try:
        if is_telemetry(topic):
            insert_telemetry(ts, device, topic, payload_text)
            print(f"[DB] telemetry <- {topic}")
        else:
            kind = classify_kind(topic)
            insert_event(ts, device, topic, kind, payload_text)
            print(f"[DB] events({kind}) <- {topic}")

    except pymysql.MySQLError as e:
        print(f"[DB-ERROR] {e} -> reconnexion")
        global db
        try:
            db.close()
        except Exception:
            pass
        db = db_connect()

def on_disconnect(_client, _userdata, reason_code, properties=None):
    print(f"[DISCONNECT] reason_code={reason_code}")

client = mqtt.Client(client_id=Config.MQTT_CLIENT_ID, protocol=mqtt.MQTTv311)

client.will_set(Config.TOPIC_ONLINE, payload="offline", qos=1, retain=True)
client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect
client.connect(Config.MQTT_BROKER_HOST, Config.MQTT_BROKER_PORT, keepalive=Config.MQTT_KEEPALIVE)
print("[INFO] Logger démarré. CTRL+C pour arrêter.")
try:
    client.loop_forever()
except KeyboardInterrupt:
    print("\n[STOP] arrêt demandé")
finally:
    try:
        db.close()
    except Exception:
        pass
    client.disconnect() 
    