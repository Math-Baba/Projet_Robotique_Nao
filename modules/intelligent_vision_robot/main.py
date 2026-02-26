# -*- coding: utf-8 -*-
import socket
import struct
import sys
import os
import cv2
import numpy as np
from pathlib import Path
import threading
import queue

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from detection.yolo_detection import YOLODetector
from recognition.facenet_recognizer import FaceRecognizer
from database.faces_repository import FacesRepository
from unknown_faces import UnknownFaceManager
from hand_gesture_detection import create_hand_detector, open_hand, mp

# ================= CONFIG =================
HOST = "0.0.0.0"
PORT = 5000

# Timeout réseau (en secondes)
ACCEPT_TIMEOUT = 10.0
RECV_TIMEOUT = 5.0

# Contrôles de charge
ENABLE_RECOGNITION = True           # Met à False pour tester sans détection/reconnaissance
PROCESS_EVERY_N_FRAMES = 3         # Ne traiter qu'1 frame sur N (augmenter si CPU/GPU saturé)
# ==========================================

PROJECT_ROOT = Path(__file__).parent.parent
MODEL_PATH = PROJECT_ROOT / "models" / "yolov8-face.pt"

MATCH_THRESHOLD = 0.4
CONFIDENCE_MARGIN = 0
UNKNOWN_DUP_THRESHOLD = 0.25
SAMPLES_TO_SAVE = 5
TRACK_MAX_DIST = 80
RELOAD_DB_EVERY_N_FRAMES = 90


def send_text_message(conn, text):
    """Envoie un message texte (UTF-8) au NAO avec en-tête de taille 4 octets."""
    data = text.encode("utf-8")
    conn.sendall(struct.pack(">L", len(data)) + data)


def main():

    print("[INFO] Initialisation...")

    detector = YOLODetector(str(MODEL_PATH))
    recognizer = FaceRecognizer()
    unknown_manager = UnknownFaceManager()

    persons_db = FacesRepository.get_all_persons()
    print(f"[INFO] {len(persons_db)} personnes chargees")

    # Initialisation du détecteur de main (MediaPipe)
    hand_detector = create_hand_detector()

    # État pour la détection de main (MediaPipe déjà configuré dans hand_gesture_detection)
    frame_timestamp_ms = 0
    hand_event_active = False  # éviter plusieurs déclenchements successifs

    # Structures pour le traitement asynchrone (détection/reconnaissance)
    frame_queue = queue.Queue(maxsize=1)
    boxes_lock = threading.Lock()
    boxes_and_labels = []
    stop_event = threading.Event()

    def processing_loop():
        nonlocal boxes_and_labels, persons_db
        local_frame_idx = 0
        last_unknown_id = None

        while not stop_event.is_set():
            try:
                frame_to_process = frame_queue.get(timeout=0.1)
            except queue.Empty:
                continue

            local_frame_idx += 1
            if local_frame_idx % PROCESS_EVERY_N_FRAMES != 0:
                continue

            # Reload DB périodiquement (sur le thread de traitement)
            if local_frame_idx % RELOAD_DB_EVERY_N_FRAMES == 0:
                persons_db = FacesRepository.get_all_persons()

            faces = detector.detect_faces(frame_to_process, conf=0.6)
            new_boxes_and_labels = []

            for (x1, y1, x2, y2) in faces:
                face_crop = frame_to_process[y1:y2, x1:x2]
                if face_crop.size == 0:
                    continue

                embedding = recognizer.get_embedding(face_crop)
                if embedding is None:
                    continue

                name, distance = recognizer.find_best_match(
                    embedding, persons_db,
                    threshold=MATCH_THRESHOLD,
                    confidence_margin=CONFIDENCE_MARGIN
                )

                if name:
                    label = f"{name} ({distance:.2f})"
                    color = (0, 255, 0)
                else:
                    label = "UNKNOWN"
                    color = (0, 165, 255)

                    # Sauvegarde automatique du dernier visage inconnu,
                    # pour pouvoir l'enregistrer ensuite via register_faces.py
                    last_unknown_id = unknown_manager.add_unknown_face(
                        embedding,
                        frame=face_crop
                    )

                new_boxes_and_labels.append((x1, y1, x2, y2, label, color))

            with boxes_lock:
                boxes_and_labels = new_boxes_and_labels

    # -------- SOCKET SERVER (reçoit NAO) --------
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(1)
    server_socket.settimeout(ACCEPT_TIMEOUT)

    print("[INFO] En attente connexion NAO...]")
    try:
        conn, addr = server_socket.accept()
        print("[INFO] Connecté :", addr)
        conn.settimeout(RECV_TIMEOUT)

        # Lancement du thread de traitement si la reconnaissance est activée
        processing_thread = None
        if ENABLE_RECOGNITION:
            processing_thread = threading.Thread(target=processing_loop, daemon=True)
            processing_thread.start()
    except socket.timeout:
        print("[ERROR] Timeout en attente de connexion NAO")
        server_socket.close()
        return

    data_buffer = b''
    frame_count = 0

    face_tracks = {}
    next_track_id = 0

    print("[INFO] Reconnaissance faciale en cours (ESC pour quitter)")

    try:
        while True:

            # -------- Lecture taille image --------
            while len(data_buffer) < 4:
                try:
                    packet = conn.recv(4096)
                except socket.timeout:
                    print("[WARN] Timeout réception (taille image)")
                    raise ConnectionError("Timeout réception taille image")
                if not packet:
                    raise ConnectionError("Connexion NAO fermée (taille image)")
                data_buffer += packet

            packed_size = data_buffer[:4]
            data_buffer = data_buffer[4:]
            msg_size = struct.unpack(">L", packed_size)[0]

            # -------- Lecture image complète --------
            while len(data_buffer) < msg_size:
                try:
                    packet = conn.recv(4096)
                except socket.timeout:
                    print("[WARN] Timeout réception (données image)")
                    raise ConnectionError("Timeout réception données image")
                if not packet:
                    raise ConnectionError("Connexion NAO fermée (données image)")
                data_buffer += packet

            img_data = data_buffer[:msg_size]
            data_buffer = data_buffer[msg_size:]
            data_buffer = b''

            # -------- Gestion éventuelle d'un message texte REGISTER:prenom --------
            is_text_msg = False
            try:
                text_msg = img_data.decode("utf-8")
                is_text_msg = True
            except UnicodeDecodeError:
                is_text_msg = False

            if is_text_msg and text_msg.startswith("REGISTER:"):
                prenom = text_msg.split(":", 1)[1].strip()
                print(f"[INFO] Message REGISTER reçu pour: {prenom}")

                unregistered = unknown_manager.get_unregistered_faces()
                if unregistered:
                    last_id = sorted(unregistered.keys(), reverse=True)[0]
                    emb = unregistered[last_id]["embedding"]
                    FacesRepository.insert_person(prenom, emb)
                    unknown_manager.register_unknown_face(last_id, prenom)
                    print(f"[INFO] Nouveau visage enregistré en base pour {prenom}")
                else:
                    print("[WARN] Aucun visage inconnu disponible pour REGISTER")

                continue

            # -------- Decode image --------
            nparr = np.frombuffer(img_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if frame is None:
                continue

            frame_count += 1

            # Envoi de la frame au thread de traitement (sans bloquer le flux)
            if ENABLE_RECOGNITION:
                try:
                    if frame_queue.full():
                        _ = frame_queue.get_nowait()
                    frame_queue.put_nowait(frame.copy())
                except queue.Empty:
                    pass
                except queue.Full:
                    pass

            # -------- Détection de main ouverte (MediaPipe) --------
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            result = hand_detector.detect_for_video(mp_image, frame_timestamp_ms)
            frame_timestamp_ms += 33  # ~30 FPS

            open_hand_detected = False
            if result.hand_landmarks:
                for hand_landmarks in result.hand_landmarks:
                    if open_hand(hand_landmarks):
                        open_hand_detected = True
                        break

            # Si main ouverte détectée et pas déjà traitée -> reconnaissance ponctuelle
            if open_hand_detected and not hand_event_active and ENABLE_RECOGNITION:
                hand_event_active = True

                faces_for_gesture = detector.detect_faces(frame, conf=0.6)
                if faces_for_gesture:
                    x1, y1, x2, y2 = faces_for_gesture[0]
                    face_crop = frame[y1:y2, x1:x2]
                    emb = recognizer.get_embedding(face_crop) if face_crop.size != 0 else None

                    if emb is not None:
                        name, distance = recognizer.find_best_match(
                            emb, persons_db,
                            threshold=MATCH_THRESHOLD,
                            confidence_margin=CONFIDENCE_MARGIN
                        )
                        if name:
                            print(f"[INFO] Visage reconnu (geste main): {name}")
                            send_text_message(conn, f"KNOWN:{name}")
                        else:
                            print("[INFO] Visage inconnu (geste main), sauvegarde...")
                            _ = unknown_manager.add_unknown_face(emb, frame=face_crop)
                            send_text_message(conn, "UNKNOWN")
                    else:
                        print("[WARN] Impossible d'extraire un embedding lors du geste main.")
                else:
                    print("[INFO] Aucune face détectée lors du geste main.")

            if not open_hand_detected:
                hand_event_active = False

            # Récupération des dernières détections pour affichage
            if ENABLE_RECOGNITION:
                with boxes_lock:
                    current_boxes_and_labels = list(boxes_and_labels)

                for (x1, y1, x2, y2, label, color) in current_boxes_and_labels:
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                    cv2.putText(
                        frame, label, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2
                    )

            cv2.imshow("NAO Face Recognition", frame)

            if cv2.waitKey(1) & 0xFF == 27:
                break

    finally:
        # Arrêt propre
        stop_event.set()
        try:
            processing_thread.join(timeout=2.0)
        except Exception:
            pass

        conn.close()
        server_socket.close()
        cv2.destroyAllWindows()
        print("[INFO] Arret du systeme")


if __name__ == "__main__":
    main()