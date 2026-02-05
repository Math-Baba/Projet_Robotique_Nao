# -*- coding: utf-8 -*-

import sys
import qi

from config.nao_config import PORT  # le port reste fixe

# Lecture IP depuis argument si fourni
if len(sys.argv) > 1:
    ROBOT_IP = sys.argv[1]
else:
    from config.nao_config import ROBOT_IP  # sinon config
    ROBOT_IP = ROBOT_IP

print("[INFO] IP utilisée pour tester NAO :", ROBOT_IP)

session = qi.Session()
try:
    session.connect("tcp://{}:{}".format(ROBOT_IP, PORT))
    print("OK")
except RuntimeError as e:
    print("FAIL", e)
