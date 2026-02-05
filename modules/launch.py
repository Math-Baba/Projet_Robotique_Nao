# -*- coding: utf-8 -*-
import subprocess
import os
from config.python_paths import PYTHON2_PATH

def launch_scenario():
    """
    Menu pour choisir le scénario Odysseo à exécuter :
    - introduction
    - conclusion
    """
    # Dossier des scripts Python2.7
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
        
        # Lancer le script Python2.7
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
