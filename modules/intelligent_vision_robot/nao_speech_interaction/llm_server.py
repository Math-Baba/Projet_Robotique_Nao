from flask import Flask, request, jsonify
from ollama import chat
from collections import deque
from datetime import datetime

app = Flask(__name__)

SYSTEM_PROMPT = """Tu es Nao, un robot assistant éducatif friendly et concis.
- Réponds toujours en français
- Garde tes réponses courtes (2-3 phrases max)
- Tu es chaleureux et encourageant avec les élèves
- Si tu ne sais pas quelque chose, dis-le simplement"""

conversation_history = deque(maxlen=10)


def log(tag, message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print("[{}][{}] {}".format(timestamp, tag, message))


@app.route("/chat", methods=["POST"])
def chat_endpoint():
    log("SERVER", "Requete recue")

    try:
        data = request.json
        user_message = data.get("message")
        log("SERVER", "Message utilisateur : {}".format(user_message))

        if not user_message:
            log("SERVER", "ERREUR - Message vide")
            return jsonify({"error": "No message provided"}), 400

        conversation_history.append({
            "role": "user",
            "content": user_message
        })
        log("SERVER", "Historique : {}/{} messages".format(len(conversation_history), conversation_history.maxlen))

        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + list(conversation_history)
        log("SERVER", "Appel LLM avec {} messages (system inclus)".format(len(messages)))

        response = chat(
            model="llama3.2:3b",
            messages=messages,
            options={
                "temperature": 0.75,
                "top_p": 0.9,
                "num_predict": 80,
            }
        )

        assistant_reply = response["message"]["content"]
        log("SERVER", "Reponse LLM : {}".format(assistant_reply))

        conversation_history.append({
            "role": "assistant",
            "content": assistant_reply
        })

        log("SERVER", "Envoi de la reponse au client")
        return jsonify({"response": assistant_reply})

    except Exception as e:
        log("SERVER", "ERREUR - {}".format(str(e)))
        return jsonify({"error": str(e)}), 500


@app.route("/reset", methods=["POST"])
def reset():
    conversation_history.clear()
    log("SERVER", "Memoire de conversation effacee")
    return jsonify({"status": "Memoire effacee"})


@app.route("/history", methods=["GET"])
def history():
    log("SERVER", "Consultation de l'historique")
    return jsonify({"history": list(conversation_history)})


if __name__ == "__main__":
    log("SERVER", "Demarrage du serveur LLM sur port 5000...")
    app.run(host="0.0.0.0", port=5000)