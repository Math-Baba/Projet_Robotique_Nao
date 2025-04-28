# -*- coding: utf-8 -*-
#Mathieu Baba
#Programme contenant la phase de présentation de Nao aux enfants de façon général

import qi
import time

ip_robot = "11.0.0.87" #ip du robot
port=9559 #port associé au Nao



#Connexion au Nao
session=qi.Session()

try :
    session.connect("tcp://{}:{}".format(ip_robot, port))
    print("Connexion réussie")
except RuntimeError:
    print("Impossible de se connecter au robot")

tts = session.service("ALTextToSpeech")
tts.setLanguage("French")

tts.say("Bonjour les enfants! Je m'appelle Nao")
time.sleep(1)
tts.say("Aujourd'hui je serai votre ami, on va bien s'amuser")
time.sleep(1)
tts.say("Mais avant de commencer, je voudrais que tout le monde se mette debout pour chanter l'hymne nationale de Maurice")
time.sleep(1)
tts.say("J'espère que vous la connaissez")