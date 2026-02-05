# -*- coding: utf-8 -*-

import subprocess
import os
from config.python_paths import PYTHON2_PATH

def test_connection(ip=None):
    """
    Lance le script Python2.7 pour tester la connexion NAO.
    Si ip est fourni, on l'utilise, sinon le script utilise la config.
    """
    script_path = os.path.join("scripts", "test_connection.py")

    # Ajouter l'IP comme argument optionnel
    args = [PYTHON2_PATH, script_path]
    if ip:
        args.append(ip)

    result = subprocess.run(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    print("[DEBUG] stdout:", result.stdout)
    print("[DEBUG] stderr:", result.stderr)

    return "OK" in result.stdout
