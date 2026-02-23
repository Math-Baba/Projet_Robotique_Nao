# -*- coding: utf-8 -*-
import numpy as np
from database.connection import get_db_connection

class FacesRepository:

    @staticmethod
    def insert_person(name, embedding):
        """
        Insère une nouvelle personne dans la base
        name : prénom
        embedding : numpy array (512,)
        """
        conn = get_db_connection()
        cur = conn.cursor()

        embedding_list = embedding.tolist()

        cur.execute(
            "INSERT INTO persons (first_name, embedding) VALUES (%s, %s)",
            (name, embedding_list)
        )

        conn.commit()
        cur.close()
        conn.close()


    @staticmethod
    def get_all_persons():
        """
        Récupère tous les visages connus
        Retourne : [(name, numpy_array_512), ...]
        """
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT first_name, embedding FROM persons")
        rows = cur.fetchall()

        cur.close()
        conn.close()

        result = []

        for name, embedding in rows:
            if embedding is None:
                continue

            arr = np.array(embedding, dtype=float).flatten()

            if len(arr) != 512:
                print(f"[WARN] Embedding pour {name}: mauvaise taille {len(arr)}, attendu 512")
                continue

            result.append((name, arr))

        return result