import cv2
import urllib.request
import os
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# ------------------------ TÉLÉCHARGEMENT DU MODÈLE -----------------------------
# model_url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
model_path = "hand_landmarker.task"

# if not os.path.exists(model_path):
#     print("Téléchargement du modèle MediaPipe...")
#     urllib.request.urlretrieve(model_url, model_path)
#     print("✓ Modèle téléchargé!")

# ----------------------------- CODE DE DÉTECTION ---------------------------------

# Configuration OPTIMISÉE pour le mouvement
base_options = python.BaseOptions(model_asset_path=model_path)
options = vision.HandLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.VIDEO,  # MODE VIDEO pour mouvement fluide
    num_hands=2,  # Peut détecter 2 mains
    min_hand_detection_confidence=0.5,  # Plus permissif
    min_hand_presence_confidence=0.5,   # Plus permissif
    min_tracking_confidence=0.5         # Plus permissif pour suivre le mouvement
)

detector = vision.HandLandmarker.create_from_options(options)

cap = cv2.VideoCapture(0)

# Compteur de frames pour le mode VIDEO
frame_timestamp_ms = 0

def main_ouverte(landmarks):
    """Vérifie si la main est ouverte (tous les doigts levés)"""
    finger_tips = [8, 12, 16, 20]
    finger_mcps = [5, 9, 13, 17]
    
    # Compter les doigts levés
    doigts_leves = 0
    
    for tip, mcp in zip(finger_tips, finger_mcps):
        if landmarks[tip].y < landmarks[mcp].y:
            doigts_leves += 1
    
    # Vérifier le pouce
    if abs(landmarks[4].x - landmarks[2].x) > 0.05:
        doigts_leves += 1
    
    # Main ouverte = au moins 4 doigts levés (tolérance)
    return doigts_leves >= 4

def draw_hand(image, landmarks):
    """Dessiner la main"""
    height, width = image.shape[:2]
    
    # Dessiner les points
    for lm in landmarks:
        x, y = int(lm.x * width), int(lm.y * height)
        cv2.circle(image, (x, y), 4, (0, 255, 0), -1)
    
    # Connexions
    connections = [
        (0, 1), (1, 2), (2, 3), (3, 4),
        (0, 5), (5, 6), (6, 7), (7, 8),
        (0, 9), (9, 10), (10, 11), (11, 12),
        (0, 13), (13, 14), (14, 15), (15, 16),
        (0, 17), (17, 18), (18, 19), (19, 20),
        (5, 9), (9, 13), (13, 17)
    ]
    
    for start_idx, end_idx in connections:
        start = landmarks[start_idx]
        end = landmarks[end_idx]
        pt1 = (int(start.x * width), int(start.y * height))
        pt2 = (int(end.x * width), int(end.y * height))
        cv2.line(image, pt1, pt2, (255, 0, 0), 2)

print("=" * 50)
print("DÉTECTION DE MAIN OUVERTE EN MOUVEMENT")
print("=" * 50)
print("Instructions:")
print("- Montrez votre main ouverte devant la caméra")
print("- Bougez-la librement")
print("- Le message 'MAIN OUVERTE' s'affichera")
print("- ESC pour quitter")
print("=" * 50)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    frame = cv2.flip(frame, 1)
    height, width = frame.shape[:2]
    
    # Conversion pour MediaPipe
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
    
    # Détection avec timestamp pour mode VIDEO
    result = detector.detect_for_video(mp_image, frame_timestamp_ms)
    frame_timestamp_ms += 33  # ~30 FPS
    
    main_ouverte_detectee = False
    
    if result.hand_landmarks:
        for hand_landmarks in result.hand_landmarks:
            # Dessiner la main
            draw_hand(frame, hand_landmarks)
            
            # Vérifier si la main est ouverte
            if main_ouverte(hand_landmarks):
                main_ouverte_detectee = True
    
    # Affichage du statut
    if main_ouverte_detectee:
        cv2.putText(frame, "MAIN OUVERTE", (50, 100),
                   cv2.FONT_HERSHEY_SIMPLEX, 2.5, (0, 255, 0), 6)
        print("Main ouverte détectée!")
    elif result.hand_landmarks:
        cv2.putText(frame, "Main fermee", (50, 100),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)
    else:
        cv2.putText(frame, "Aucune main", (50, 100),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
    
    # Afficher le FPS
    cv2.putText(frame, f"FPS: {int(1000/33)}", (10, 30),
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    cv2.imshow("Detection Main Ouverte", frame)
    
    if cv2.waitKey(1) & 0xFF == 27:  # ESC pour quitter
        break

cap.release()
cv2.destroyAllWindows()
print("\nArrêt du programme")