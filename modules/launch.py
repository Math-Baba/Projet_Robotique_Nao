# -*- coding: utf-8 -*-
import subprocess
import os
from config.python_paths import PYTHON2_PATH, PYTHON3_PATH

def launch_scenario():
    """
    Menu pour choisir le scénario Odysseo à exécuter :
    - introduction
    - conclusion
    """
    # Dossier des scripts python
    base_path = os.path.join("modules", "scenario_odysseo")
    
    while True:
        print("\n=== Scénario Odysseo ===")
        print("1 - Introduction")
        print("2 - Conclusion")
        print("0 - Retour au menu principal")
        
        choix = input("Votre choix : ").strip()
        
        if choix == "1":
            script = os.path.join(base_path, "introduction_nao.py")
        elif choix == "2":
            script = os.path.join(base_path, "conclusion_nao.py")
        elif choix == "0":
            break
        else:
            print("Choix invalide, réessayez.")
            continue
        
        print("[INFO] Lancement du script :", os.path.basename(script))
        
        try:
            result = subprocess.run(
                [PYTHON2_PATH, script],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            print("=== Sortie du script ===")
            print(result.stdout)
            if result.stderr:
                print("=== Erreurs éventuelles ===")
                print(result.stderr)
        except Exception as e:
            print("[ERROR] Impossible d'exécuter le script :", e)

def launch_nao_game():
    """
    Menu pour choisir le script de jeu à exécuter :
    - Nao Game
    - Ajouter une question/réponse
    - Générer les QR codes
    """
    base_path = os.path.join("modules", "nao_game")
    while True:
        print("\n=== Nao Game ===")
        print("1 - Charger de nouvelles questions")
        print("2 - Lancer le jeu")
        print("0 - Retour au menu principal")

        choix = input("Votre choix : ").strip()
        
        if choix == "1":
            script = os.path.join(base_path, "load_data.py")
            python_exec = PYTHON3_PATH
        elif choix == "2":
            script = os.path.join(base_path, "nao_game.py")
            python_exec = PYTHON2_PATH 
        elif choix == "0":
            break
        else:
            print("Choix invalide, réessayez.")
            continue
        
        print("[INFO] Lancement du script :", os.path.basename(script))
        
        try:
            result = subprocess.run(
                [python_exec, script],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            print("=== Sortie du script ===")
            print(result.stdout)
            if result.stderr:
                print("=== Erreurs éventuelles ===")
                print(result.stderr)
        except Exception as e:
            print("[ERROR] Impossible d'exécuter le script :", e)


def launch_motion_control():
    """
    Menu pour le script de contrôle manuel du robot
    à partir d'une manette PS3
    """
    base_path = os.path.join("modules", "motion_control")
    while True:
        print("\n=== Robot Motion Control ===")
        print("1 - Contrôle scénario")
        print("2 - Jeu ramassage de bouteilles")
        print("0 - Retour au menu principal")

        choix = input("Votre choix : ").strip()
        
        # initialiser script à None pour éviter UnboundLocalError
        script = None

        if choix == "1":
            script = os.path.join(base_path, "robot_motion_controller.py")
        elif choix == "2":
            # Lancer le script Python 3 (vision)
            script_py3 = os.path.join(base_path, "nao_object_detection.py")
            print("[INFO] Lancement du script Python 3 :", os.path.basename(script_py3))
            py3_proc = subprocess.Popen(
                [PYTHON3_PATH, script_py3]
            )

            # Lancer le script Python 2.7 (motion & pickup)
            script_py2 = os.path.join(base_path, "nao_video_stream_publisher.py")
            print("[INFO] Lancement du script Python 2.7 :", os.path.basename(script_py2))
            try:
                result = subprocess.run(
                    [PYTHON2_PATH, script_py2],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                print("=== Sortie du script Python 2.7 ===")
                print(result.stdout)
                if result.stderr:
                    print("=== Erreurs éventuelles ===")
                    print(result.stderr)
            except Exception as e:
                print("[ERROR] Impossible d'exécuter le script Python 2.7 :", e)

            # Quand le script Python 2.7 se termine, on tue le script Python 3
            try:
                py3_proc.terminate()
                py3_proc.wait()
            except Exception:
                pass
            print("[INFO] Script Python 3 terminé")
            # script reste None pour éviter ré-exécution en bas
        elif choix == "0":
            break
        else:
            print("Choix invalide, réessayez.")
            continue

        # Si un script a été sélectionné (hors cas choix==2 géré ci-dessus), l'exécuter
        if script is None:
            continue

        print("[INFO] Lancement du script :", os.path.basename(script))

        try:
            result = subprocess.run(
                [PYTHON2_PATH, script],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            print("=== Sortie du script ===")
            print(result.stdout)
            if result.stderr:
                print("=== Erreurs éventuelles ===")
                print(result.stderr)
        except Exception as e:
            print("[ERROR] Impossible d'exécuter le script :", e)