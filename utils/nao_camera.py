# -*- coding: utf-8 -*-

import cv2
import numpy as np
from pyzbar import pyzbar

def scan_qr_code(video_service):
    """
    Ouvre la caméra du NAO et attend qu'un QR code soit détecté.
    Retourne le texte du QR code.
    """
    CAMERA = 0
    RESOLUTION = 2
    COLOR_SPACE = 11
    FPS = 30

    name_id = video_service.subscribeCamera("python_nao_qr", CAMERA, RESOLUTION, COLOR_SPACE, FPS)

    try:
        while True:
            nao_image = video_service.getImageRemote(name_id)
            if nao_image is None:
                continue

            width, height = nao_image[0], nao_image[1]
            array = nao_image[6]

            image = np.frombuffer(array, dtype=np.uint8).reshape((height, width, 3))
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            # Scanner les QR codes
            qrcodes = pyzbar.decode(image)
            if qrcodes:
                qr_text = qrcodes[0].data.decode("utf-8")
                return qr_text  # Retourne le mot clé dès qu'un QR est détecté

            # Affichage optionnel pour debug
            cv2.imshow("NAO QR Camera", image)
            if cv2.waitKey(1) & 0xFF == 27:  # ESC pour quitter
                break
    finally:
        video_service.unsubscribe(name_id)
        cv2.destroyAllWindows()
