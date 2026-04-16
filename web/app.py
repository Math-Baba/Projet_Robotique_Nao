# -*- coding: utf-8 -*-
import os
import sys
import time
import threading
import subprocess
from pathlib import Path

import requests

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from flask import Flask, jsonify, render_template, request
from config.ip_manager import save_ip, load_ip
from core.nao_connection import test_connection
from config.python_paths import PYTHON2_PATH, PYTHON3_PATH, PYTHON310_PATH

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

app = Flask(__name__, template_folder="templates", static_folder="static")

process_registry = {}
process_lock = threading.Lock()


def project_path(*parts):
    return os.path.join(ROOT_DIR, *parts)


def describe_process(proc):
    return {
        "pid": proc.pid,
        "running": proc.poll() is None,
    }


def get_processes():
    with process_lock:
        return {
            name: {
                "command": data["command"],
                "started_at": data["started_at"],
                **describe_process(data["process"]),
            }
            for name, data in process_registry.items()
        }


def stop_process(name):
    with process_lock:
        data = process_registry.get(name)
        if not data:
            return False
        proc = data["process"]
        if proc.poll() is None:
            try:
                proc.terminate()
                proc.wait(timeout=5)
            except Exception:
                proc.kill()
        process_registry.pop(name, None)
        return True


def stop_all_processes():
    with process_lock:
        for name in list(process_registry.keys()):
            stop_process(name)


def start_process(name, command, cwd=None):
    with process_lock:
        if name in process_registry and process_registry[name]["process"].poll() is None:
            return process_registry[name]["process"]

        proc = subprocess.Popen(
            command,
            cwd=cwd or ROOT_DIR,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            text=True,
        )
        process_registry[name] = {
            "process": proc,
            "command": command,
            "started_at": time.time(),
        }
        return proc


def run_command(command, cwd=None):
    return subprocess.run(
        command,
        cwd=cwd or ROOT_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def run_background(target, name):
    thread = threading.Thread(target=target, name=name, daemon=True)
    thread.start()
    return thread


def ensure_server_ready(url, timeout=15.0):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            resp = requests.get(url, timeout=1)
            if resp.status_code == 200:
                return True
        except Exception:
            pass
        time.sleep(1)
    return False


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/info", methods=["GET"])
def api_info():
    return jsonify({
        "robot_ip": load_ip(),
        "python2": PYTHON2_PATH,
        "python3": PYTHON3_PATH,
        "python310": PYTHON310_PATH,
    })


@app.route("/api/connect", methods=["POST"])
def api_connect():
    payload = request.get_json(force=True)
    ip = payload.get("ip")
    if not ip:
        return jsonify({"error": "IP requise."}), 400

    success = test_connection(ip)
    if success:
        save_ip(ip)
        return jsonify({"ok": True, "message": "IP sauvegardée et connexion OK."})

    return jsonify({"ok": False, "message": "Connexion NAO échouée."}), 400


@app.route("/api/status", methods=["GET"])
def api_status():
    return jsonify({
        "processes": get_processes(),
    })


@app.route("/api/last_face", methods=["GET"])
def api_last_face():
    try:
        resp = requests.get("http://127.0.0.1:5001/last_face", timeout=2.0)
        return jsonify(resp.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/llm_history", methods=["GET"])
def api_llm_history():
    try:
        resp = requests.get("http://127.0.0.1:5000/history", timeout=2.0)
        return jsonify(resp.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/action", methods=["POST"])
def api_action():
    payload = request.get_json(force=True)
    action = payload.get("action")
    if not action:
        return jsonify({"error": "Action manquante."}), 400

    if action == "scenario_intro":
        run_background(lambda: run_command([PYTHON2_PATH, project_path("modules", "scenario_odysseo", "introduction_nao.py")]), "ScenarioIntro")
    elif action == "scenario_conclusion":
        run_background(lambda: run_command([PYTHON2_PATH, project_path("modules", "scenario_odysseo", "conclusion_nao.py")]), "ScenarioConclusion")
    elif action == "nao_game":
        def run_game():
            result = run_command([PYTHON3_PATH, project_path("modules", "nao_game", "load_data.py")])
            if result.returncode != 0:
                return
            run_command([PYTHON2_PATH, project_path("modules", "nao_game", "nao_game.py")])
        run_background(run_game, "NaoGame")
    elif action == "motion_scenario":
        run_background(lambda: run_command([PYTHON2_PATH, project_path("modules", "motion_control", "robot_motion_controller.py")]), "MotionScenario")
    elif action == "motion_game":
        def run_motion_game():
            vision = start_process("MotionVision", [PYTHON3_PATH, project_path("modules", "motion_control", "nao_object_detection.py")])
            run_command([PYTHON2_PATH, project_path("modules", "motion_control", "nao_video_stream_publisher.py")])
            stop_process("MotionVision")
        run_background(run_motion_game, "MotionGame")
    elif action == "ivr_full":
        def run_ivr_full():
            llm = start_process("LLMServer", [PYTHON3_PATH, project_path("modules", "intelligent_vision_robot", "nao_speech_interaction", "llm_server.py")])
            face = start_process("FaceServer", [PYTHON310_PATH, project_path("modules", "intelligent_vision_robot", "main.py")])
            time.sleep(3)
            run_command([PYTHON2_PATH, project_path("modules", "intelligent_vision_robot", "nao_video_stream_publisher.py")])
            stop_process("LLMServer")
            stop_process("FaceServer")
        run_background(run_ivr_full, "IVRFull")
    elif action == "ivr_chatbot":
        def run_ivr_chatbot():
            start_process("LLMServer", [PYTHON3_PATH, project_path("modules", "intelligent_vision_robot", "nao_speech_interaction", "llm_server.py")])
            run_command([PYTHON2_PATH, project_path("modules", "intelligent_vision_robot", "nao_speech_interaction", "nao_chatbot.py")])
        run_background(run_ivr_chatbot, "IVRChatbot")
    elif action == "ivr_face":
        def run_ivr_face():
            start_process("FaceServer", [PYTHON310_PATH, project_path("modules", "intelligent_vision_robot", "main.py")])
            run_command([PYTHON2_PATH, project_path("modules", "intelligent_vision_robot", "nao_video_stream_publisher.py")])
            stop_process("FaceServer")
        run_background(run_ivr_face, "IVRFace")
    elif action == "stop_all":
        stop_all_processes()
    else:
        return jsonify({"error": "Action inconnue."}), 400

    return jsonify({"ok": True, "action": action})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
