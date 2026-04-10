import pymysql

import Config
from MqttSubscriber import MqttSubscriber

class MariadbLogger(MqttSubscriber):
    def __init__(self):
        super().__init__(
            client_id="mariadb_logger",
            online_topic=Config.TOPIC_ONLINE,
        )
        self.db = self.connect_db()

    def connect_db(self):
        return pymysql.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME,
            autocommit=True,
            charset="utf8mb4",
        )

    def subscribe_topic(self):
        self.subscribe(Config.MQTT_TOPIC_FILTER)

    def on_message(self, client, userdata, msg):
        try:
            topic = msg.topic
            payload_raw = msg.payload.decode("utf-8")
            data = json.loads(payload_raw) 
            
            ts = self.get_time_now()
            device = self.extract_device(topic)

            text_audio = data.get("text", "N/A")
            intention = data.get("intent", "unknown")
            resultat = data.get("state", "processed")

            with self.db.cursor() as cursor:
                sql = """INSERT INTO events (ts_utc, device, topic, kind, payload) 
                        VALUES (%s, %s, %s, %s, %s)"""
                cursor.execute(sql, (ts, device, topic, intention, payload_raw))
                
            print(f"[DB] Commande vocale enregistrée : {intention}")

        except Exception as e:
            print(f"[ERROR DB] {e}")

    def is_telemetry(self, topic):
        return "/sensors/" in topic and not topic.endswith("/value")

    def classify_kind(self, topic):
        if "/cmd/" in topic:
            return "cmd"
        elif "/state/" in topic:
            return "state"
        elif "/status/" in topic:
            return "status"
        else:
            return "other"

    def extract_device(self, topic):
        parts = topic.split("/")
        return parts[4] if len(parts) >= 5 else "unknown"

    def insert_telemetry(self, ts, device, topic, payload):
        with self.db.cursor() as cursor:
            sql = "INSERT INTO telemetry (ts_utc, device, topic, payload) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (ts, device, topic, payload))

    def insert_event(self, ts, device, topic, kind, payload):
        with self.db.cursor() as cursor:
            sql = "INSERT INTO events (ts_utc, device, topic, kind, payload) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (ts, device, topic, payload))