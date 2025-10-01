# -*- coding: utf-8 -*-
import socket
import sys
import os

# Ajouter le dossier parent pour importer nao_input
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
import nao_input

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 6000

def send_to_server(message):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((SERVER_HOST, SERVER_PORT))
        s.sendall(message.encode("utf-8"))
        print("Texte envoyé au serveur :", message)
        s.close()
    except Exception as e:
        print("Erreur lors de l'envoi au serveur :", e)

def on_press(key, recording_flag):
    try:
        if key.char == 't':
            if not recording_flag[0]:
                print("Début de l'enregistrement...")
                nao_input.record_audio(start_manual=True)  
                recording_flag[0] = True
            else:
                nao_input.stop_recording()  
                print("Fin de l'enregistrement")
                recording_flag[0] = False
                # Après arrêt, transférer, transcrire et envoyer
                nao_input.transfer_audio_file()
                texte = nao_input.speech_to_text()
                print("Transcription :", texte)
                if texte:
                    send_to_server(texte)
    except AttributeError:
        pass

def main():
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
                send_to_server(texte)
        elif cmd == 'q':
            print("Client arrêté.")
            break


if __name__ == "__main__":
    main()
