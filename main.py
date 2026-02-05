# -*- coding: utf-8 -*-

from config.ip_manager import save_ip, load_ip
from core.nao_connection import test_connection
from modules.launch import launch_scenario

def main():
    ip = input("Entrez l'adresse IP du robot NAO : ")

    if test_connection(ip):
        save_ip(ip)
        print("IP sauvegardée avec succès")
    else:
        print("Impossible de se connecter au NAO")
        return
    
    while True:
        print("\n=== Choix du module ===")
        print("1 - Scénario Odysseo")
        print("2 - Motion Controller")
        print("3 - IA / Reconnaissance faciale")
        print("4 - QR Game")
        print("0 - Quitter")

        choix = input("Votre choix : ").strip()

        if choix == "1":
            launch_scenario()
        elif choix == "2":
            break
        elif choix == "3":
            break
        elif choix == "4":
            break
        elif choix == "0":
            break
        else:
            print("Choix invalide, réessayez.")


if __name__ == "__main__":
    main()
