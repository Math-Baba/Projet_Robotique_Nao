# Projet robotique NAO 

Ce dépôt regroupe les modules développés autour du robot **NAO** (SoftBank Robotics) : reconnaissance faciale, interaction vocale avec LLM, scénarios pédagogiques, jeux et contrôle moteur. Le PC joue le rôle de serveur de traitement (vision, base de données, API HTTP) tandis que le NAO exécute des scripts **Python 2.7** avec le SDK **NAOqi**.

---

## Description du projet

### Objectifs

- **Reconnaissance faciale** : flux vidéo depuis la caméra du NAO vers le PC, détection de visages (YOLO), reconnaissance d’identité (FaceNet), détection de geste (main ouverte via MediaPipe), enregistrement des visages inconnus.
- **Interaction vocale** : chatbot côté NAO qui s’appuie sur un **serveur LLM** local (Ollama) et sur une API de porté par la reconnaissance faciale du **dernier visage reconnu**.
- **Données** : persistance des embeddings faciaux et des paires question/réponse dans **PostgreSQL**.
- **Autres modules** : scénarios Odysseo, jeu NAO avec QR codes, contrôle moteur (manette), etc.

### Architecture logique (résumé)

| Composant | Environnement | Rôle |
|-----------|----------------|------|
| `modules/intelligent_vision_robot/main.py` | Python 3.10 (recommandé) | Serveur TCP (flux JPEG + messages `KNOWN` / `UNKNOWN` / `REGISTER`) + API Flask (ex. `5001`) |
| `nao_video_stream_publisher.py` | Python 2.7 sur NAO | Capture caméra NAO, envoi du flux au PC, lecture des réponses et TTS |
| `llm_server.py` | Python 3 (voir `python_paths.py`) | API Flask sur le port **5000** (chat LLM via Ollama) |
| `nao_chatbot.py` | Python 2.7 sur NAO | Speech, appels HTTP vers le PC (LLM + visage) |
| `modules/launch.py` | Python 3 | Menu pour lancer les scénarios et le stack « Intelligent Vision Robot » |

---

## Prérequis

- **NAO** : NAOqi / Choregraphe ou environnement permettant d’exécuter du Python 2.7 avec `qi`, OpenCV et accès réseau au PC.
- **PC** :
  - **Python 2.7** + dépendances (`requirements_py27.txt`) pour les scripts NAO lancés depuis le PC ou pour le développement.
  - **Python 3.10** pour la vision lourde (torch, ultralytics, mediapipe, etc.) — fichier `requirements_py310.txt`.
  - **Python 3** (souvent 3.13 dans ce projet) pour le serveur LLM et certains outils — `requirements_py313.txt` (contient notamment `ollama` pour `llm_server.py`).
- **PostgreSQL** : instance accessible depuis le PC, avec les tables décrites plus bas.
- **Ollama** : installé et démarré sur la machine qui exécute `llm_server.py`, avec le modèle référencé dans le code (ex. `qwen2.5:1.5b` — à aligner avec votre installation).
- **Modèles** :
  - Fichier **YOLO visage** attendu sous `models/` (ex. `yolov8-face.pt`, nom utilisé par le code).
  - Fichier **MediaPipe** `hand_landmarker.task` : téléchargé automatiquement au premier usage par `hand_gesture_detection.py` (ou placé manuellement à la racine du module si vous bloquez le réseau).

---

## Installation

### 1. Cloner le dépôt

```bash
git clone https://github.com/Math-Baba/Projet_Robotique_Nao.git
cd "Projet robotique Nao"
```

Travaillez depuis la **racine du projet** pour que les imports relatifs (`modules`, `config`, `database`) fonctionnent.

### 2. Environnements Python et dépendances

Créez un **environnement virtuel par famille de scripts** (recommandé) ou installez globalement selon votre politique.

**Vision / reconnaissance faciale (Python 3.10)**

```bash
py -3.10 -m venv .venv310
.venv310\Scripts\activate
pip install -r requirements_py310.txt
```

> **NumPy / PyTorch** : en cas d’avertissement ou d’erreur liée à NumPy 2.x avec une ancienne build de torch, privilégiez une version NumPy &lt; 2 (déjà ciblée dans `requirements_py310.txt`).

**Serveur LLM et outils Python 3 récents**

```bash
py -3.13 -m venv .venv313
.venv313\Scripts\activate
pip install -r requirements_py313.txt
```

**Scripts NAO / Python 2.7 (machine de développement ou outils associés)**

```bash
# avec l'interpréteur Python 2.7 approprié
pip install -r requirements_py27.txt
```

### 3. Fichier `.env` (non versionné)

Créez un fichier **`.env`** à la racine du projet. Le module `database/connection.py` charge ces variables via `python-dotenv` :

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=votre_db
DB_USER=votre_user
DB_PASSWORD=votre_mot_de_passe
```

### 4. `config/pc_config.py`

Fichier local : **adresse IP du PC** telle que vue depuis le NAO, et **port du socket vidéo** (doit correspondre au `PORT` dans `intelligent_vision_robot/main.py`, typiquement **5002**).

- `PC_IP` : IP du PC sur le réseau partagé avec le robot.
- `PC_PORT` : port TCP d’écoute du flux vidéo côté PC.

Ne versionnez pas ce fichier s’il contient des informations réseau spécifiques à votre installation.

### 5. `config/nao_config.py`

Fichier local pour la connexion NAOqi et options audio (selon les scripts qui l’utilisent) :

- `ROBOT_IP` : IP du NAO.
- `PORT` : port NAOqi (souvent **9559**).
- `NAO_AUDIO_FILE`, `LOCAL_AUDIO_FILE` : chemins des fichiers audio si utilisés.
- `NAO_USERNAME`, `NAO_PASSWORD` : identifiants SSH / compte robot si requis par vos scripts.

Adaptez chaque valeur à **votre** flotte de robots et à votre réseau.

### 6. `config/python_paths.py`

Indique les **chemins absolus** des exécutables Python utilisés par `modules/launch.py` :

- `PYTHON2_PATH` : Python 2.7 avec NAOqi (ou binaire fourni par Aldebaran).
- `PYTHON3_PATH` : Python 3 utilisé pour le **serveur LLM** (`llm_server.py`) — doit avoir Flask + client `ollama` installés.
- `PYTHON310_PATH` : Python 3.10 pour **`intelligent_vision_robot/main.py`**.

Mettez à jour les chemins selon votre machine (Windows / Linux / chemins utilisateur).

### 7. Base de données PostgreSQL

Créez une base dédiée, puis les tables suivantes (noms et colonnes alignés sur le code).

**Table `persons`** — visages enregistrés pour FaceNet (embedding de dimension **512**) :

```sql
CREATE TABLE persons (
    id          SERIAL PRIMARY KEY,
    first_name  TEXT NOT NULL,
    embedding   REAL[] NOT NULL  -- tableau de 512 flottants (compatible avec list Python / psycopg2)
);
```

**Table `questions_list`** — jeu / FAQ (module `question_repository.py`) :

```sql
CREATE TABLE questions_list (
    id         SERIAL PRIMARY KEY,
    question   TEXT NOT NULL,
    answer     TEXT NOT NULL
);
```

Accordez les droits `SELECT` / `INSERT` / `UPDATE` à l’utilisateur défini dans `.env`.

### 8. Ollama et modèle LLM

1. Installez [Ollama](https://ollama.com/) sur la machine qui exécute `llm_server.py`.
2. Téléchargez le modèle utilisé dans `llm_server.py` (ex. `ollama pull qwen2.5:1.5b`).
3. Vérifiez que le service Ollama tourne avant de lancer le menu « système complet ».

---

## Guide d’utilisation

### Lancement centralisé (`modules/launch.py`)

Depuis la racine du projet, avec l’interpréteur Python 3 qui contient `requests` et les chemins configurés :

```bash
py -3.13 modules\launch.py
```

(ou le Python défini dans votre IDE.)

Dans le menu, choisissez **Intelligent Vision Robot** pour accéder à :

1. **Système complet** : démarre le serveur LLM (5000), le serveur vision (5001 + 5002), puis le flux vidéo NAO et le chatbot.
2. **Chatbot seul** : suppose ou lance le LLM selon l’option.
3. **Reconnaissance faciale uniquement** : serveur vision + script flux vidéo NAO.

### Lancement manuel (débogage)

Ordre typique pour la chaîne vision + NAO :

1. PC : activer l’environnement 3.10 et lancer  
   `py -3.10 modules\intelligent_vision_robot\main.py`
2. NAO (ou PC avec NAOqi) : lancer  
   `nao_video_stream_publisher.py`  
   après que le PC écoute sur le port configuré (`PC_PORT` / `PORT` dans `main.py`).

Pour le LLM seul :

```bash
py -3.13 modules\intelligent_vision_robot\nao_speech_interaction\llm_server.py
```

### Enregistrement de visages

- **Automatique dans le flux** : visages marqués inconnus peuvent être stockés via `UnknownFaceManager` (fichiers + pickle local dans `modules/data/unknown_faces/`).
- **Script interactif** : `register_faces.py` permet de parcourir les inconnus et d’insérer en base via `FacesRepository`.
- **Scénario main levée + NAO** : selon votre version du flux, le PC peut envoyer `KNOWN:` / `UNKNOWN` et recevoir `REGISTER:prenom` depuis le script NAO ; l’enregistrement final repose sur la même base `persons`.

### Autres entrées du menu `launch.py`

- **Scénario Odysseo** : scripts dans `modules/scenario_odysseo/`.
- **Nao Game** : `modules/nao_game/` (chargement de données + jeu sur le robot).
- **Motion control** : `modules/motion_control/`.

---

## Structure des dossiers (aperçu)

```
config/           # Paramètres locaux (IP, chemins Python) — à créer / adapter
database/         # Connexion PostgreSQL, repositories
modules/
  intelligent_vision_robot/   # Vision, gestes, speech, LLM
  launch.py                   # Menu principal
  scenario_odysseo/
  nao_game/
  motion_control/
models/           # Poids YOLO visage, etc.
```

---

## Auteur
- **Math-Baba** - [GitHub](https://github.com/Math-Baba)
