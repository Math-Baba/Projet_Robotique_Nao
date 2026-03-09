# -*- coding: utf-8 -*-
import requests
import keyboard
from naoqi import ALProxy
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from modules.intelligent_vision_robot.voice_transcription.nao_speech_recognition import (
    record_audio,
    stop_recording,
    transfer_audio_file,
    speech_to_text
)

from config.nao_config import ROBOT_IP, PORT
from config.pc_config import PC_IP

LLM_SERVER = "http://{}:5000/chat".format(PC_IP)

tts = ALProxy("ALTextToSpeech", ROBOT_IP, PORT)


def ask_llm(text):
    print("[CLIENT] Envoi au serveur LLM : {}".format(text))
    
    try:
        response = requests.post(
            LLM_SERVER,
            json={"message": text},
            timeout=30
        )
        print("[CLIENT] Status code recu : {}".format(response.status_code))

        data = response.json()
        answer = data.get("response", u"")
        
        print("[CLIENT] Reponse LLM extraite : {}".format(answer.encode("utf-8")))
        
        return answer  

    except requests.exceptions.Timeout:
        print("[CLIENT][ERREUR] Timeout - le serveur ne repond pas")
        return None
    except requests.exceptions.ConnectionError:
        print("[CLIENT][ERREUR] Impossible de joindre le serveur")
        return None
    except Exception as e:
        print("[CLIENT][ERREUR] {}".format(str(e)))
        return None

def process_audio():
    transfer_audio_file()

    user_text = speech_to_text()

    if not user_text:
        tts.say("Je n'ai pas compris.")
        return

    answer = ask_llm(user_text)

    if not answer:
        tts.say("Je n'ai pas de reponse pour le moment.")
        return

    print("[CLIENT] NAO va dire : {}".format(answer.encode("utf-8")))
    tts.say(answer.encode("utf-8"))


def main():
    print("=" * 50)
    print("  NAO Chatbot - Pret !")
    print("  ESPACE  → Commencer a parler")
    print("  ENTREE  → Arreter l'enregistrement")
    print("  ECHAP   → Quitter")
    print("=" * 50)

    while True:
        print("\n[CLIENT] En attente... (ESPACE pour parler, ECHAP pour quitter)")

        # Attente ESPACE ou ECHAP
        event = keyboard.read_event(suppress=True)
        while event.event_type != "down" or event.name not in ("space", "esc"):
            event = keyboard.read_event(suppress=True)

        if event.name == "esc":
            print("[CLIENT] Arret du programme.")
            break

        print("[CLIENT] Enregistrement en cours... (ENTREE pour arreter)")
        record_audio(start_manual=True)

        keyboard.wait("enter")
        print("[CLIENT] Fin de l'enregistrement")
        stop_recording()

        process_audio()


if __name__ == "__main__":
    main()