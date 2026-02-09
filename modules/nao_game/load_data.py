import json
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from database.question_repository import QuestionRepository

questions_list = [QuestionRepository.get_random_question() for _ in range(10)]

with open("questions.json", "w") as f:
    json.dump(questions_list, f)
