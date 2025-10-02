# -*- coding: utf-8 -*-
import socket
import sys
import os
from naoqi import ALProxy
import qi
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

# Ajouter le dossier parent pour importer nao_input
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
import nao_input

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 6000

ip_robot = "11.0.0.147" # ip du robot
port=9559 # port associé au Nao


def send_to_server(message):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((SERVER_HOST, SERVER_PORT))

        # Convertir en unicode si ce n'est pas déjà le cas
        if isinstance(message, str):
            message = message.decode('utf-8')

        s.sendall(message.encode("utf-8"))
        print(u"Texte envoyé au serveur :", message)

        # Attendre la réponse du serveur
        data = s.recv(4096)
        response_str = ""
        if data:
            response_str = data.decode("utf-8").strip()
            print(u"Réponse du serveur :", response_str)
        s.close()
        return response_str
    
    except Exception as e:
        print("Erreur lors de l'envoi au serveur :", e)


def main():
    #Connexion au Nao
    session=qi.Session()

    try :
        session.connect("tcp://{}:{}".format(ip_robot, port))
        print("Connexion réussie")
    except RuntimeError:
        print("Impossible de se connecter au robot")

    tts = session.service("ALTextToSpeech")
    tts.setLanguage("French")

    print("Client actif. Tape 't' et Enter pour commencer/arrêter l'enregistrement.")
    while True:
        cmd = raw_input("Commande (t pour start/stop, q pour quitter) : ").strip()
        if cmd == 't':
            print("Début de l'enregistrement...")
            nao_input.record_audio(start_manual=True)
            raw_input("Appuie sur Enter pour arrêter l'enregistrement...")
            nao_input.stop_recording()
            print("Fin de l'enregistrement")
            nao_input.transfer_audio_file()
            texte = nao_input.speech_to_text()
            print("Transcription :", texte)

            if texte:
                response = send_to_server(texte)
                if response:
                    # Convertir la réponse en string pour le TTS
                    if isinstance(response, unicode):
                        response_str = response.encode('utf-8')
                    else:
                        response_str = response
                    tts.say(response_str)
            
        elif cmd == 'q':
            print("Client arrêté.")
            break


if __name__ == "__main__":
    main()
