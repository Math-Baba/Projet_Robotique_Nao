# -*- coding: utf-8 -*-
import socket
import struct
import cv2
import sys
import os
import numpy as np
from naoqi import ALProxy
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from config.nao_config import ROBOT_IP, PORT
from config.settings import apply_settings

# ================= CONFIG =================
PC_IP = "11.0.0.59"   # ip de l'ordinateur local 
PC_PORT = 5000
# ==========================================

# Connexion caméra NAO
video = ALProxy("ALVideoDevice", ROBOT_IP, PORT)

name_id = video.subscribeCamera(
    "python_stream",
    0,      # caméra haute
    1,      # résolution 320x240 (plus rapide pour test)
    11,     # BGR
    15      # FPS
)

# Connexion socket vers PC
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((PC_IP, PC_PORT))

print("Connexion au PC réussie")

try:
    while True:
        nao_image = video.getImageRemote(name_id)
        if nao_image is None:
            continue

        width = nao_image[0]
        height = nao_image[1]
        array = nao_image[6]

        frame = np.frombuffer(array, dtype=np.uint8).reshape((height, width, 3))

        # Compression JPEG pour envoi rapide
        _, jpeg = cv2.imencode('.jpg', frame)
        data = jpeg.tostring()

        # Envoi taille + image
        sock.sendall(struct.pack(">L", len(data)) + data)

finally:
    video.unsubscribe(name_id)
    sock.close()
