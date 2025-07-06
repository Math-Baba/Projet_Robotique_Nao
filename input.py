# -*- coding: utf-8 -*-
# Mathieu Baba
# Programme contenant les fonctions pour convertir les audios passés en entrée de Nao en texte via l'API google_speech_recognition
import paramiko
import speech_recognition as sr
from naoqi import ALProxy
import time

ip_robot = "11.0.0.98" # ip du robot
port=9559 # port associé au Nao
nao_audio_file="/home/nao/recording.wav" # le fichier audio du Nao
local_audio_file= "./recording.wav" # le fichier audio en local sur la machine
nao_username="nao" # nom d'utilisateur de Nao
nao_password="udm2021" # mot de passe du Nao


# Fonction pour écouter les réponses des utilisateurs
def record_audio():
    audio_recorder= ALProxy("ALAudioRecorder", ip_robot, port)

    try:
        audio_recorder.stopMicrophonesRecording()  # Arrête tout enregistrement en cours
    except RuntimeError:
        pass  # Ignorer l'erreur si aucun enregistrement n'est actif

    print("Enregistrement de l'audio...")
    audio_recorder.startMicrophonesRecording(nao_audio_file, "wav", 16000, (0,0,1,0)) #Démmarage de l'enregistrement audio  
    time.sleep(5) # Durée de 5 secondes pour l'enregistrement 
    audio_recorder.stopMicrophonesRecording()
    print("Fin de l'enregistrement")




#Fonction pour transférer le fichier audio localement
def transfer_audio_file():
    print("Transfert du fichier de Nao à la machine local...")

    ssh=paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip_robot, username=nao_username, password=nao_password)

    scp=paramiko.SFTPClient.from_transport(ssh.get_transport())
    scp.get(nao_audio_file, local_audio_file)
    scp.close()
    print("Transfert complété")




# Fonction pour convertir l'audio en texte
def speech_to_text():
    recognizer = sr.Recognizer()

    # Charger le fichier audio enregistré par Nao
    with sr.AudioFile(local_audio_file) as source:
        print("Analyse de l'audio...")
        recognizer.adjust_for_ambient_noise(source)  # Ajuste au bruit
        try:
            audio = recognizer.record(source)  # Récupère tout l'audio
            text = recognizer.recognize_google(audio, language="fr-FR", show_all=False)  # Détection en français et on évite d'affiche les transcriptions de speech_recognition
            print("Tu as dit : " + text)
            return text
        except sr.UnknownValueError:
            print("Nao n'a pas compris.")
            return None
        except sr.RequestError:
            print("Erreur de connexion à Google Speech Recognition.")
            return None