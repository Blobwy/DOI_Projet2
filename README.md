# DOI_Projet1

# Projet Final : Système de Monitoring IoT
**Étudiant :** Jean-Philippe / Gauthier  
**Équipe :** jp-gauthier-pi01  
**Date de remise :** 20 mars 2026

---

## 1) Description du projet
Ce projet consiste à mettre en place une infrastructure IoT complète sur Raspberry Pi. Il permet de lire une température simulée, de contrôler une DEL physique via une interface mobile (MQTT Dash) et d'archiver tous les échanges dans une base de données MariaDB.

## 2) Matériel requis
* **Raspberry Pi 3/4/5**
* **DEL** connectée sur le port BCM 27
* **Résistance** 220-330 Ohms
* **Fils d'extension** et breadboard
* **Smartphone** android avec l'application MQTT Dash

## 3) Schéma de branchement
La DEL est branchée sur la **broche 27 (BCM)**. L'anode est reliée au GPIO et la cathode à la masse (GND) via une résistance.

---

## 4) Architecture du système

### 4.1 Diagramme d'architecture
L'architecture suit un modèle **Étoile** avec le Broker au centre.



### 4.2 Contrat MQTT
| Topic | Rôle | Payload exemple |
| :--- | :--- | :--- |
| `.../sensors/temperature` | Télémétrie | `{"value": 22.5, "unit": "C", ...}` |
| `.../actuators/led/cmd` | Commande | `{"state": "on"}` |
| `.../status` | Statut LWT | `{"status": "offline"}` |

---

## 5) Base de données
Le système utilise **MariaDB** avec deux tables principales :
1. `telemetry` : Stocke les valeurs numériques des capteurs.
2. `events` : Stocke les commandes et les changements d'état.

---

## 6) Installation
1. Cloner le dépôt.
2. Créer l'environnement virtuel : `python -m venv .venv`.
3. Installer les dépendances : `pip install -r requirements.txt`.
4. Importer la base de données : `mariadb -u root -p < db/schema.sql`.

## 7) Utilisation
Lancer les scripts dans cet ordre :
1. `python src/logger_mariadb.py`
2. `python src/subscriber_led.py`
3. `python src/publisher_sensor.py`

## 8) Démonstration
Pour la démo, nous validons :
* La publication en direct via `mosquitto_sub`.
* La jauge et le switch sur MQTT Dash.
* La persistance des données avec entre autre la requête "10 dernières mesures".
* Le bonus **LWT** (statut online/offline).