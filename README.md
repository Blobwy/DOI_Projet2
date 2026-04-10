# 🎙️ Assistant Vocal de Lampe Intelligente

## 1. Description du Projet
Ce projet consiste en un prototype d'assistant vocal local conçu pour piloter une lampe intelligente (représentée par une DEL) sur **Raspberry Pi**. Le système permet une interaction naturelle sans interface graphique complexe. Il intègre un pipeline complet : détection de mot d'activation, reconnaissance vocale (STT), interprétation par expressions régulières, communication asynchrone via le protocole **MQTT**, exécution physique sur GPIO et synthèse vocale (TTS) pour le feedback utilisateur.

## 2. Matériel Utilisé
* **Raspberry Pi** : Unité centrale de traitement pour l'exécution des modules.
* **Microphone USB** : Utilisé pour la capture audio et la reconnaissance vocale.
* **Haut-parleur ou Écouteurs** : Utilisés pour fournir un retour vocal à l'utilisateur (TTS).
* **DEL et résistance** : Matériel représentant la lampe intelligente et ses états physiques.
* **Composants de prototypage** : Plaque d'essai (breadboard) et fils de raccordement pour le montage GPIO.

## 3. Dépendances
Le projet repose sur les bibliothèques et services suivants :
* **Services Système** : `mosquitto` (Broker MQTT) et `mariadb-server` (Base de données SQL).
* **Bibliothèques Python** :
    * `paho-mqtt` : Pour la communication entre les différents modules.
    * `speech_recognition` : Pour la conversion de la parole en texte (STT).
    * `pyttsx3` : Pour la synthèse vocale locale (TTS).
    * `pymysql` : Pour la connexion et la journalisation dans MariaDB.
    * `gpiozero` : Pour le pilotage des broches GPIO de la DEL.

## 4. Étapes d'Installation
1. **Mise à jour et Services** : Installer et activer les services Mosquitto et MariaDB sur le Raspberry Pi.
2. **Installation Python** : Installer les dépendances Python nécessaires via `pip` ou `apt`.
3. **Base de données** : Créer la base de données et les tables `events` et `telemetry` pour la persistance des données.
4. **Configuration** : Ajuster les adresses IP du broker et les identifiants de connexion dans le fichier `Config.py`.

## 5. Procédure de Lancement
1. S'assurer que les services Mosquitto et MariaDB sont actifs (`systemctl is-active`).
2. Lancer l'application via le script principal :
   ```bash
   python3 Main.py