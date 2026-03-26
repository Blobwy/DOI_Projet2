MQTT_BROKER_HOST = "localhost"
MQTT_BROKER_PORT = 1883
MQTT_KEEPALIVE = 60

DB_HOST = "localhost"
DB_USER = "iot"
DB_PASSWORD = "iot"
DB_NAME = "iot_b3"

TEAM = "jp-gauthier"
DEVICE = "pi01"

TOPIC_ONLINE = f"ahuntsic/aec-iot/b3/{TEAM}/{DEVICE}/status/online"
MQTT_PREFIX = f"ahuntsic/aec-iot/b3/{TEAM}/{DEVICE}"
MQTT_TOPIC_FILTER = f"{MQTT_PREFIX}/#"
SENSOR_PUB_CLIENT_ID = "b3-logger-jp-gauthier-pi01"
MARIADB_CLIENT_ID = "b3-logger-jp-gauthier-pi01-mariadb"
LED_CLIENT_ID = "b3-logger-jp-gauthier-pi01-led"

TOPIC_JSON_TEMP = f"ahuntsic/aec-iot/b3/{TEAM}/{DEVICE}/sensors/temperature"
TOPIC_VALUE_TEMP = f"ahuntsic/aec-iot/b3/{TEAM}/{DEVICE}/sensors/temperature/value"

TOPIC_CMD = f"ahuntsic/aec-iot/b3/{TEAM}/{DEVICE}/actuators/led/cmd"
TOPIC_STATE = f"ahuntsic/aec-iot/b3/{TEAM}/{DEVICE}/actuators/led/state"

QOS_SENSOR_TEMP = 0
QOS_STATUS_TEMP = 1
PUBLISH_PERIOD_S_TEMP = 2.0

QOS_CMD_LED = 1
LED_PIN_BCM = 27