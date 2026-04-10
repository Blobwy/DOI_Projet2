import time
import threading
from gpiozero import LED
import Config
from MqttSubscriber import MqttSubscriber

class LedSubscriber(MqttSubscriber):
    def __init__(self):
        super().__init__(client_id=Config.LED_CLIENT_ID, online_topic=Config.TOPIC_ONLINE)
        self.led = LED(Config.LED_PIN_BCM)
        self.blink_thread = None
        self.stop_blink = threading.Event()

    def on_message(self, client, userdata, msg):
        import json
        try:
            data = json.loads(msg.payload.decode())
            intent = data.get("intent")
            
            # Arrêter tout clignotement en cours avant une nouvelle action
            self.stop_blink.set()
            if self.blink_thread: self.blink_thread.join()
            self.stop_blink.clear()

            if intent == "on":
                self.led.on()
            elif intent == "off":
                self.led.off()
            elif intent == "blink":
                self.start_action_thread(self.blink_logic, 0.5)
            elif intent == "night":
                self.start_action_thread(self.blink_logic, 2.0) # Clignotement lent pour le mode nuit [cite: 253]
        except Exception as e:
            print(f"Erreur LED: {e}")

    def start_action_thread(self, target, speed):
        self.blink_thread = threading.Thread(target=target, args=(speed,))
        self.blink_thread.start()

    def blink_logic(self, speed):
        while not self.stop_blink.is_set():
            self.led.toggle()
            time.sleep(speed)