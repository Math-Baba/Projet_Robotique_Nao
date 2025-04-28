# -*- coding: utf-8 -*-
#Mathieu Baba
#Programme principal du projet contenant le jeu dans son entiereté
import time
import qi
import speech_recognition as sr
from naoqi import ALProxy
import random
import mysql.connector
import reconnaissance_faciale
import input




ip_robot = "11.0.0.87" #ip du robot
port=9559 #port associé au Nao
nao_audio_file="/home/nao/recording.wav" #le fichier audio du Nao
local_audio_file= "./recording.wav" #le fichier audio en local sur la machine
nao_username="nao"
nao_password="udm2021"



#------------------------------------------------------------------------- JEU ----------------------------------------------------------------------------------

#Fonction de présentation de Nao
def presentation():

    time.sleep(0.5)
    tts.say("Veux-tu que je texplique comment jouer au jeu ?")

    while(True) :
        input.record_audio()
        input.transfer_audio_file()
        reponse = input.speech_to_text()
        if "oui" in reponse or "ouais" in reponse:
            regles() 
            break
        elif "non" in reponse :
            tts.say("Okay d'accord, passons directement aux questions")
            break
        else :
            tts.say("je n'ai pas très bien compris, peux tu me répondre par oui ou par non ?")




# Fonction pour énoncer les règles du jeu
def regles():
    tts.say("Voici les règles du jeu, je vais décrire plusieurs animaux marins et tu devras deviner lequel c'est. Tu auras trois chances pour répondre correctement. Si tu réponds bien tu auras un point, si tu réponds faux, tu ne gagnes aucun point")
    time.sleep(0.5)
    tts.say("As-tu compris ?")
    input.record_audio()
    input.transfer_audio_file()
    reponse = input.speech_to_text()
    if reponse and ("oui" in reponse or "ouais" in reponse):
        return 
    elif reponse is None:
        tts.say("Alors je vais reformuler, tu devras deviner l'animal que je vais décrire. Mais attention tu n'as que 3 chances seulement de répondre juste. Tu as un point si tu as la bonne réponse et pas de points si tu réponds pas bien")
    else:
        tts.say("Alors je vais reformuler, tu devras deviner l'animal que je vais décrire. Mais attention tu n'as que 3 chances seulement de répondre juste. Tu as un point si tu as la bonne réponse et pas de points si tu réponds pas bien")



#Fonction de validation des réponses
def verification(mot, pts):
    tentative=3
    while(tentative>0):
        input.record_audio()
        input.transfer_audio_file()
        reponse = input.speech_to_text()
        if reponse is None:
            tts.say("Je n'ai pas très bien compris, redis moi")
            continue

        # Assurez-vous que 'reponse' est au format Unicode
        if isinstance(reponse, str):
            reponse = reponse.decode('utf-8')  # Décodage UTF-8

        if mot in reponse :
            tts.say("Bonne réponse, tu gagnes 1 points")
            pts+=1
            return pts
        else:
            tentative-=1
            if(tentative>0):
                tts.say("C'est pas la bonne réponse! Allez tu as encore {} tentatives.".format(tentative))
            else:
                tts.say("Oups, c'est dommage, c'était {} la réponse".format(mot))
    return pts



#Fonction pour parcourir une table de base de donnée les informations sur les questions et la réponse associée
def get_question_reponse(numero_question):
    #connection à la base de données
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="", 
        database="nao_games"
    )
    cursor = connection.cursor()
    cursor.execute("SELECT question FROM ListeQuestions WHERE id=%s", (numero_question, ))
    question=cursor.fetchone()[0]

    cursor.execute("SELECT reponse FROM ListeQuestions WHERE id=%s", (numero_question, ))
    reponse=cursor.fetchone()[0]
    

    return question, reponse





#------------------------------------------------------------------ PROGRAMME PRINCIPAL----------------------------------------------------------------------------


#Connexion au Nao
session=qi.Session()

try :
    session.connect("tcp://{}:{}".format(ip_robot, port))
    print("Connexion réussie")
except RuntimeError:
    print("Impossible de se connecter au robot")

tts = session.service("ALTextToSpeech")
tts.setLanguage("French")

try :
    faceProxy = ALProxy("ALFaceDetection", ip_robot, port) # Crée une connexion avec le module de détection de visages du robot
    charProxy = ALProxy("ALFaceCharacteristics", ip_robot, port) # Crée une connexion avec le module des caractéristiques des visages détectés
    memoryProxy = ALProxy("ALMemory", ip_robot, port) # Crée une connexion avec le module ALMemory pour récupérer les données
except RuntimeError : 
    print("Connexion à la reconnaissance faciale de NAO echoué!")


pts=0

reconnaissance_faciale.reconnaissance_faciale()

presentation()


nombreAleatoire=[]
nombreAleatoire = random.sample(range(1, 11), 5) #On stocke une liste de nombre aléatoire


for nombre in nombreAleatoire:
    question, reponse = get_question_reponse(nombre)
    str_question=question.encode('utf-8')#problème avec l'encodage ASCII
    tts.say(str_question)
    pts=verification(reponse, pts)


tts.say("Tu as donc {} points sur 5.".format(pts))

session.close()
print("Connexion fermée")

