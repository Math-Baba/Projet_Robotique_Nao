# -*- coding: utf-8 -*-
import socket
import struct
import cv2
import numpy as np
import qi
import sys
import os
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from config.nao_config import ROBOT_IP, PORT
from config.pc_config import PC_IP, PC_PORT

# ------------------ Connexion NAO ------------------
session = qi.Session()
session.connect("tcp://{}:{}".format(ROBOT_IP, PORT))

video = session.service("ALVideoDevice")
tts = session.service("ALTextToSpeech")

# ------------------ CAMERA ------------------
name_id = video.subscribeCamera(
    "python_stream",
    0,      # caméra top
    1,      # 320x240
    11,     # RGB
    15      # FPS
)

# ------------------ SOCKET ------------------
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
sock.settimeout(0.05)  # petit timeout pour lecture non bloquante


def recv_text_message():
    """Lit un message texte depuis le PC (format 4 octets taille + UTF-8)."""
    try:
        header = sock.recv(4)
        if not header or len(header) < 4:
            return None
        size = struct.unpack(">L", header)[0]

        data = b""
        while len(data) < size:
            chunk = sock.recv(size - len(data))
            if not chunk:
                break
            data += chunk

        if not data:
            return None
        return data.decode("utf-8")
    except socket.timeout:
        return None
    except Exception:
        return None


# Attente serveur PC
while True:
    try:
        sock.connect((PC_IP, PC_PORT))
        print("[INFO] Connecté au PC")
        break
    except Exception:
        print("[INFO] Connexion refusée, attente du serveur PC...")
        time.sleep(0.5)

try:
    while True:
        # 1) Vérifier si le PC a envoyé une réponse KNOWN/UNKNOWN
        msg = recv_text_message()
        if msg:
            if msg.startswith("KNOWN:"):
                prenom = msg.split(":", 1)[1]
                print("[INFO] Reçu KNOWN pour {}".format(prenom))
                tts.say(u"Salut {}".format(prenom))
                # On ne capture pas d'image pendant le dialogue, puis on reprend
                continue
            elif msg == "UNKNOWN":
                print("[INFO] Reçu UNKNOWN")
                tts.say(u"Oh je crois pas te connaitre, donne moi ton prenom")
                prenom = raw_input("Entre ton prenom: ").strip()
                if prenom:
                    data = ("REGISTER:" + prenom).encode("utf-8")
                    sock.sendall(struct.pack(">L", len(data)) + data)
                # Puis on reprend la capture
                continue

        # 2) Capture et envoi d'image (flux normal)
        nao_image = video.getImageRemote(name_id)
        if nao_image is None:
            continue

        width = nao_image[0]
        height = nao_image[1]
        array = nao_image[6]

        frame = np.frombuffer(array, dtype=np.uint8).reshape((height, width, 3))
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        ret, jpeg = cv2.imencode(
            '.jpg',
            frame,
            [int(cv2.IMWRITE_JPEG_QUALITY), 70]
        )

        if not ret:
            continue

        data = jpeg.tobytes()

        try:
            sock.sendall(struct.pack(">L", len(data)) + data)
        except Exception:
            print("[ERROR] PC déconnecté")
            break

finally:
    print("[INFO] Nettoyage...")
    video.unsubscribe(name_id)
    sock.close()