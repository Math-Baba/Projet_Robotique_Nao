# -*- coding: utf-8 -*-
from database.connection import get_db_connection

class QuestionRepository:

    @staticmethod
    def get_random_question():
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT id, question, answer FROM questions_list ORDER BY RANDOM() LIMIT 1"
        )
        row = cur.fetchone()
        cur.close()
        conn.close()
        return row

    @staticmethod
    def add_question(question, answer):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO questions_list (question, answer) VALUES (%s, %s)",
            (question, answer)
        )
        conn.commit()
        cur.close()
        conn.close()
 
    @staticmethod
    def get_all_answers():
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT answer FROM questions_list")
        rows = cur.fetchall()
        cur.close()
        conn.close()

        return [row[0] for row in rows]
