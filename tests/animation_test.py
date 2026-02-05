# -*- coding: utf-8 -*-
import qi
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from config.nao_config import ROBOT_IP, PORT

if not ROBOT_IP:
    print("IP du robot non définie")
    exit()

#Connexion au Nao
session=qi.Session()

try :
    session.connect("tcp://{}:{}".format(ROBOT_IP, PORT))
    print("Connexion réussie")
except RuntimeError:
    print("Impossible de se connecter au robot")

motion = session.service("ALMotion")
animation_player = session.service("ALAnimationPlayer")

print("début de l'animation")
animation_player.run("animations/Stand/Emotions/Positive/Excited_2")

session.close()