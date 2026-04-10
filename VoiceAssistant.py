import speech_recognition as sr
import re
import json
import pyttsx3
import Config
from MqttPublisher import MqttPublisher

class VoiceAssistant(MqttPublisher):
    def __init__(self):
        super().__init__(client_id=Config.LED_CLIENT_ID + "-assistant", online_topic=Config.TOPIC_ONLINE)
        self.engine = pyttsx3.init()
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        self.patterns = {
            "on": re.compile(r"(allume|ouvrir|active).*(lampe|lumière)", re.IGNORECASE),
            "off": re.compile(r"(éteins|fermer|désactive).*(lampe|lumière)", re.IGNORECASE),
            "blink": re.compile(r"(clignoter|clignote).*(lampe|lumière)", re.IGNORECASE),
            "status": re.compile(r"(donne|quel).*(état|statut)", re.IGNORECASE),
            "night": re.compile(r"(active|mode).*(nuit)", re.IGNORECASE)
        }

    def speak(self, text):
        print(f"[SYSTEME] {text}")
        self.engine.say(text)
        self.engine.runAndWait()

    def listen_and_recognize(self, timeout=5):
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            try:
                print("Écoute en cours...")
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=5)
                text = self.recognizer.recognize_google(audio, language="fr-FR")
                print(f"[RECONNU] {text}")
                return text
            except (sr.WaitTimeoutError, sr.UnknownValueError):
                return None
            except sr.RequestError:
                self.speak("Erreur de connexion au service vocal")
                return None

    def run(self):
        self.speak("Assistant prêt.")
        while True:
            print("\nEn attente du mot d'activation...")
            trigger = self.listen_and_recognize(timeout=None)
            
            if trigger and "assistant" in trigger.lower():
                self.speak("Je vous écoute")
                
                command_text = self.listen_and_recognize()
                if command_text:
                    intent = self.interpret_command(command_text)
                    if intent:
                        self.execute_intent(intent, command_text)
                    else:
                        self.speak("Je n'ai pas compris la commande.")
                else:
                    self.speak("Je n'ai rien entendu.")

    def interpret_command(self, text):
        for intent, pattern in self.patterns.items():
            if pattern.search(text):
                return intent
        return None

    def execute_intent(self, intent, original_text):
        payload = {"intent": intent, "text": original_text, "state": "unknown"}
        
        if intent == "on":
            payload["state"] = "on"
            self.speak("Lampe allumée")
        elif intent == "off":
            payload["state"] = "off"
            self.speak("Lampe éteinte")
        elif intent == "blink":
            payload["state"] = "blink"
            self.speak("Clignotement activé")
        elif intent == "night":
            payload["state"] = "night"
            self.speak("Mode nuit activé")
        elif intent == "status":
            self.speak("Je demande l'état au système")

        self.publish(Config.TOPIC_CMD, json.dumps(payload), qos=1)

    def publish_data(self): pass

if __name__ == "__main__":
    assistant = VoiceAssistant()
    assistant.connect()
    assistant.run()