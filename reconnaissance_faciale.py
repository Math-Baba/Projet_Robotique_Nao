# -*- coding: utf-8 -*-
#Mathieu Baba
#Programme pour reconnaitre le visage d'un utilisateur ou de le stocker 
#s'il n'est pas enregistré dans la base de donnée interne de Nao

import mysql.connector
import json
from naoqi import ALProxy
import time
import numpy as np
import input



#--------------------------------------------------------------------- CONFIGURATION BASE DE DONNÉES ----------------------------------------------------------------
def creation_table_si_non_existant():
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='nao_games'
    )
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS faces (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255),
            face_data TEXT
        )
    """)
    connection.commit()
    cursor.close()
    connection.close()

def recuperer_les_donnees_du_visage():
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='nao_games'
    )
    cursor = connection.cursor()
    cursor.execute("SELECT name, face_data FROM faces")
    results = cursor.fetchall()
    cursor.close()
    connection.close()
    return results

def stocker_nouveau_visage(name, detected_face):
    creation_table_si_non_existant()
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='nao_games'
    )
    cursor = connection.cursor()
    face_data_json = json.dumps(detected_face)
    sql_query = "INSERT INTO faces (name, face_data) VALUES (%s, %s)"
    values = (name, face_data_json)
    cursor.execute(sql_query, values)
    connection.commit()
    cursor.close()
    connection.close()

# -------------------------------------------------------------------------- COMPARAISON DE VISAGES ----------------------------------------------------------------------

def vecteur_du_visage(face_data):
    # On extrait les "shape info" : coordonnées de la tête
    # Ex : face_data[0] contient bounding box + shape info
    # On prend uniquement les shape_info
    shape_info = face_data[0][1]
    return np.array(shape_info)

def proximite_du_visage(face1, face2, threshold=0.1):
    vec1 = vecteur_du_visage(face1)
    vec2 = vecteur_du_visage(face2)
    distance = np.linalg.norm(vec1 - vec2)
    return distance < threshold

def correspondance(detected_face, stored_faces):
    for name, face_data in stored_faces:
        face_data_json = json.loads(face_data)
        if proximite_du_visage(detected_face, face_data_json):
            return name
    return None

# ----------------------------------------------------------------- PROGRAMME RECONNAISSANCE FACIALE ---------------------------------------------------------------------------
ip_robot = "11.0.0.85"
port = 9559

def reconnaissance_faciale():
    tts = ALProxy("ALTextToSpeech", ip_robot, port)
    faceProxy = ALProxy("ALFaceDetection", ip_robot, port)
    memoryProxy = ALProxy("ALMemory", ip_robot, port)

    try:
        faceProxy.subscribe("FaceDetection")
        print("Recherche d'un visage...")
        time.sleep(5)  # Laisse le temps de détecter un visage
        data = memoryProxy.getData("FaceDetected")

        creation_table_si_non_existant()

        if data and isinstance(data, list) and len(data) >= 2:
            detected_faces = data[1]
            print("Données détectées :", json.dumps(detected_faces, indent=2))

            detected_face = detected_faces[0]  # On prend le premier visage détecté

            stored_faces = recuperer_les_donnees_du_visage()
            matched_name = correspondance(detected_face, stored_faces)

            if matched_name:
                tts.say("Eh salut {}, je vois que tu as encore envie de rejouer au jeu !".format(matched_name))
            else:
                tts.say("Salut, je m'appelle Nao. Et toi, Comment tu t'appelles ?")
                input.record_audio()
                input.transfer_audio_file()
                name = input.speech_to_text()  
                stocker_nouveau_visage(name, detected_face)
                tts.say("Super, maintenant je me souviendrai de toi, {} !".format(name))
        else:
            print("Aucun visage détecté.")
            tts.say("Je ne vois personne pour le moment.")

    finally:
        faceProxy.unsubscribe("FaceDetection")

