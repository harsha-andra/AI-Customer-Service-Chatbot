"""
Flask Web API for AI Customer Chatbot
Serves the frontend and handles chat requests.
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.chatbot_engine import ChatbotSession

app = Flask(__name__, static_folder="../frontend", static_url_path="")
CORS(app)

# One session per app instance (extend with Redis for multi-user)
session = None

def get_session():
    global session
    if session is None:
        session = ChatbotSession()
    return session


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "").strip()
    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    try:
        bot = get_session()
        reply = bot.chat(user_message)
        return jsonify({"reply": reply, "session_id": bot.session_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/reset", methods=["POST"])
def reset():
    global session
    if session:
        session.save_log()
    session = None
    return jsonify({"status": "Session reset"})


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "provider": "configured"})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
