#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
#Mathieu Baba
#Programme pour reconnaitre le visage d'un utilisateur ou de le stocker 
#s'il n'est pas enregistré dans la base de donnée interne de Nao
from naoGames import ip_robot, port, tts, record_audio, transfer_audio_file, speech_to_text
from naoqi import ALProxy
import time




#Fonction pour stocker les données du visage et les associées au prénom de l'enfant
def get_visage(name):

    faceProxy.subscribe("FaceDetection")
    charProxy.analyzeFace(True)  # Active l'analyse faciale
    
    time.sleep(5)  # Laisse le temps au robot d'analyser

    try:
        if charProxy.learnFace(name):
            print("Visage de {} enregistré avec succès !".format(name))
            tts.say("Okay {}, je me souviendrais de ton prénom".format(name))
        else:
            print("Échec de l'enregistrement.")
    except Exception as e:
        print("Erreur :", e)

    charProxy.analyzeFace(False)  # Désactive l'analyse faciale
    faceProxy.unsubscribe("FaceDetection")



#Reconnaissance d'un visage 
def face_recognition():
    faceProxy.subscribe("FaceDetection")

    for i in range(10):  # Essaye de reconnaître pendant 10 secondes
        data = memoryProxy.getData("FaceDetected")

        if data and len(data) > 1:
            faces = data[1]
            for face in faces:
                recognized = charProxy.recognizeFace()
                if recognized[0]:  # Si un visage est reconnu
                    print("Visage reconnu : {}".format(recognized[1]))  # Affiche le nom
                    tts.say("Eh salut {}, je vois que tu as envie de rejouer au jeu avec moi".format(name))
                else:
                    print("Visage non reconnue!")
                    tts.say("Salut, je m'appelle Nao, et toi ? Comment t'appelles-tu ?")
                    record_audio()
                    transfer_audio_file()
                    name = speech_to_text()
                    get_visage(name)
                    tts.say("Super {}, on va jouer au jeu du Qui suis je.".format(name))
        time.sleep(1)

    faceProxy.unsubscribe("FaceDetection")




#Test
try :
    faceProxy = ALProxy("ALFaceDetection", ip_robot, port) # Crée une connexion avec le module de détection de visages du robot
    charProxy = ALProxy("ALFaceCharacteristics", ip_robot, port) # Crée une connexion avec le module des caractéristiques des visages détectés
    memoryProxy = ALProxy("ALMemory", ip_robot, port) # Crée une connexion avec le module ALMemory pour récupérer les données
except RuntimeError : 
    print("Connexion à la reconnaissance faciale de NAO echoué!")

face_recognition()




