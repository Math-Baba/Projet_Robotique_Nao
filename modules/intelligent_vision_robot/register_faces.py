# -*- coding: utf-8 -*-
import cv2
from pathlib import Path
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from recognition.facenet_recognizer import FaceRecognizer
from database.faces_repository import FacesRepository
from unknown_faces import UnknownFaceManager

# 👉 Import ton système MediaPipe ici
from hand_gesture_detector import main_ouverte_detectee  

def main():
    print("Gesture-Based Face Greeting System")
    print("-" * 40)

    recognizer = FaceRecognizer()
    unknown_manager = UnknownFaceManager()

    cap = cv2.VideoCapture(0)

    salutation_faite = False

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # 👋 Détection main ouverte (ta logique Mediapipe)
        gesture_detected = main_ouverte_detectee(frame)

        if gesture_detected and not salutation_faite:
            print("👋 Main détectée, reconnaissance faciale...")

            result = recognizer.recognize(frame)

            if result["recognized"]:
                name = result["name"]
                print(f"🤖 Salut {name}")
                # tts.say(f"Salut {name}")  # si NAO

            else:
                print("🤖 Oh je crois pas te connaitre, donne moi ton prénom : ")
                name = input().strip()

                if name:
                    embedding = result["embedding"]

                    # ✅ Insertion BDD
                    FacesRepository.insert_person(name, embedding)

                    # ✅ Sauvegarde unknown face
                    unknown_manager.register_unknown_face(result["face_id"], name)

                    print(f"✓ {name} enregistré avec succès !")

            salutation_faite = True

        # Reset si plus de main
        if not gesture_detected:
            salutation_faite = False

        cv2.imshow("Camera", frame)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
    print("Arrêt du système")

if __name__ == "__main__":
    main()