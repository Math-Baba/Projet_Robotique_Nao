# -*- coding: utf-8 -*-
#Mathieu Baba
#Programme pour passer les questions et les réponses associés dans une base de donnée
import mysql.connector


# Connexion au serveur MySQL
connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="", # change le mot de passe
    database="nao_games"
)

cursor = connection.cursor()

# Création d'une table pour stocker les questions
cursor.execute("""
CREATE TABLE IF NOT EXISTS ListeQuestions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    question VARCHAR(1000),
    reponse VARCHAR(200)
)
""")

print("Combien de question à insérer ?")
nb=int(raw_input())

for i in range(nb):
    print("Entrez la question :")
    question=raw_input()
    print("Entrez la réponse à la question :")
    reponse=raw_input()

    cursor.execute("INSERT INTO ListeQuestions (question, reponse) VALUES (%s, %s)", (question, reponse))
    connection.commit()
    print("Valeur insérée.")

cursor.close()
connection.close()
