# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
import time
import qi
from config.nao_config import ROBOT_IP, PORT
from config.settings import apply_settings
from utils.speech_and_animation_player import say_with_animation


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

apply_settings(session)

tts = session.service("ALTextToSpeech")
motion = session.service("ALMotion")
posture = session.service("ALRobotPosture")
animation_player = session.service("ALAnimationPlayer")
tts.setLanguage("French")

# Mettre le robot en posture initiale
posture.goToPosture("StandInit", 0.5) 

tts.say(""" Bonjour tout le monde ! 
Je m’appelle Nao, et je suis un robot passionné par la mer !  
J’adore découvrir les animaux marins et comprendre comment nous pouvons protéger l’océan. 
Est-ce que vous aimez la mer, vous aussi ? """)

time.sleep(3)

tts.say("Super ! Aujourd’hui, mes amis d’Odysseo et moi, nous allons voyager ensemble sous la mer.")

time.sleep(0.5)

tts.say("Avant que mes amis commencent la présentation, nous allons chanter et danser ensemble. Suivez mes pas !")

# Paramètres de mouvements : x=avance, y=latéral, theta=rotation (en radians)
motion.moveTo(0.0, 0.0, 1.57)  # 1.57 rad ≈ 90° vers la gauche

say_with_animation(tts, animation_player, "S'il te plaît, est ce que je peux danser et chanter avec les enfants ?", "animations/Stand/Gestures/Explain_10")

motion.moveTo(0.0, 0.0, -1.57)  # -1.57 rad ≈ 90° droite





