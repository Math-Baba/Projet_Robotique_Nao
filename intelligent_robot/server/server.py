# -*- coding: utf-8 -*-
import socket
from AI_model import ai_response

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 6000

def start_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((SERVER_HOST, SERVER_PORT))
    s.listen(5)  # peut gérer 5 connexions en attente
    print("Serveur en écoute sur {}:{}".format(SERVER_HOST, SERVER_PORT))

    try:
        while True:  # boucle infinie, serveur toujours actif
            conn, addr = s.accept()
            print("Connexion établie avec {}".format(addr))
            try:
                while True:  # lire les messages envoyés par ce client
                    data = conn.recv(1024)
                    if not data:
                        break

                    # Décoder les bytes en string
                    message = data.decode("utf-8")
                    print("Message reçu :", message)

                    # Passer la string à l'IA
                    response = ai_response(message)
                    if response is None:
                        response = "Ok"

                    print("Message envoyé : ", response)

                    # Envoyer la réponse encodée
                    conn.sendall((response + "\n").encode("utf-8"))

            except Exception as e:
                print("Erreur pendant la connexion :", e)
            finally:
                conn.close()
                print("Connexion fermée avec {}".format(addr))
    except KeyboardInterrupt:
        print("\nServeur arrêté manuellement.")
    finally:
        s.close()

if __name__ == "__main__":
    start_server()
