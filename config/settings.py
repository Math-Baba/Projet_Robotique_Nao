# -*- coding: utf-8 -*-

def apply_settings(session):
    try:
        tts = session.service("ALTextToSpeech")

        # Régler le volume à 65%
        tts.setVolume(0.65)
        print("[INFO] Volume réglé à 65%")

        # Régler la langue par défaut sur français
        tts.setLanguage("French")
        print("[INFO] Langue par défaut réglée sur Français")

    except Exception as e:
        print("[ERROR] Impossible d'appliquer les settings :", e)
