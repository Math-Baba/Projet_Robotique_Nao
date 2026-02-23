# -*- coding: utf-8 -*-
import cv2
from pathlib import Path
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from recognition.facenet_recognizer import FaceRecognizer
from database.faces_repository import FacesRepository
from unknown_faces import UnknownFaceManager

PROJECT_ROOT = Path(__file__).parent.parent


def main():
    print("Face Registration System")
    print("-" * 40)
    
    recognizer = FaceRecognizer()
    unknown_manager = UnknownFaceManager()
    
    # Récupération des visages inconnus non encore enregistrés
    unregistered = unknown_manager.get_unregistered_faces()
    
    if not unregistered:
        print("No unregistered faces found.")
        return
    
    print(f"Found {len(unregistered)} unregistered faces")
    print()

    # On ne s'intéresse qu'au DERNIER visage inconnu (le plus récent)
    # Les IDs sont du type "unknown_YYYYMMDD_HHMMSS", donc tri lexicographique = tri temporel.
    face_ids = sorted(unregistered.keys(), reverse=True)[:1]
    index = 0
    
    while index < len(face_ids):
        face_id = face_ids[index]
        face_data = unregistered[face_id]
        
        # Chargement de l’image du visage inconnu
        frame_path = unknown_manager.base_dir / f"{face_id}.jpg"
        
        if frame_path.exists():
            frame = cv2.imread(str(frame_path))
            cv2.imshow("Unknown Face", frame)
        
        print(f"\nFace {index + 1}/{len(face_ids)} (dernier UNKNOWN): {face_id}")
        print("Options:")
        print("  1. Register with a name")
        print("  2. Skip")
        print("  3. Delete")
        print("  4. Exit")
        
        choice = input("Choice (1-4): ").strip()
        
        if choice == "1":
            name = input("Enter person's full name: ").strip()
            
            if name:
                embedding = face_data['embedding']
                
                # ✅ Insertion via repository
                FacesRepository.insert_person(name, embedding)
                
                # Marquer comme enregistré
                unknown_manager.register_unknown_face(face_id, name)
                
                print(f"✓ {name} registered successfully!")
                index += 1
            else:
                print("Name cannot be empty.")
        
        elif choice == "2":
            print("Skipped.")
            index += 1
        
        elif choice == "3":
            unknown_manager.delete_unknown_face(face_id)
            face_ids.remove(face_id)
            print("Deleted.")
        
        elif choice == "4":
            break
        
        else:
            print("Invalid choice.")
    
    cv2.destroyAllWindows()
    print("\nRegistration complete!")


if __name__ == "__main__":
    main()