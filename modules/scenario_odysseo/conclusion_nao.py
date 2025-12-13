# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import time
import qi
from load_env import load_env

env = load_env()

robot_ip = env.get("NAO_IP")
port = env.get("NAO_PORT")

if not robot_ip:
    print("IP du robot non définie")
    exit()

#Connexion au Nao
session=qi.Session()

try :
    session.connect("tcp://{}:{}".format(robot_ip, port))
    print("Connexion réussie")
except RuntimeError:
    print("Impossible de se connecter au robot")

tts = session.service("ALTextToSpeech")
motion = session.service("ALMotion")
posture = session.service("ALRobotPosture")
animation_player = session.service("ALAnimationPlayer")
tts.setLanguage("French")

# Mettre le robot en posture initiale
posture.goToPosture("StandInit", 0.5) 

tts.post.say("""Les enfants, vous avez vu ? Les mangroves, les herbiers et les coraux sont des trésors vivants ! 
Si on les protège, on protège aussi notre planète. 
Alors, qui veut devenir un gardien de l’océan ? Souvenez-vous qu’un petit geste de votre part pourra aider l’environnement.
A très bientôt.""")
animation_player.post.run("animations/Sit/Emotions/Positive/Happy_1")

time.sleep(0.5)

tts.post.say("Au revoir les amis !")
animation_player.post.run("animations/Sit/Gestures/Hey_3")
