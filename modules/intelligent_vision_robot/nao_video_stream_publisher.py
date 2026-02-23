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

        nao_image = video.getImageRemote(name_id)
        if nao_image is None:
            continue

        width = nao_image[0]
        height = nao_image[1]
        array = nao_image[6]

        # Reconstruction image
        frame = np.frombuffer(array, dtype=np.uint8).reshape((height, width, 3))
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        # Compression JPEG
        ret, jpeg = cv2.imencode(
            '.jpg',
            frame,
            [int(cv2.IMWRITE_JPEG_QUALITY), 70]
        )

        if not ret:
            continue

        data = jpeg.tobytes()

        # Envoi taille + image
        try:
            sock.sendall(struct.pack(">L", len(data)) + data)
        except (BrokenPipeError, ConnectionResetError):
            print("[ERROR] PC déconnecté")
            break

finally:
    print("[INFO] Nettoyage...")
    video.unsubscribe(name_id)
    sock.close()