import os
import sys
from pathlib import Path

from flask import Flask, jsonify, redirect, request
from flask_cors import CORS


ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / "backend"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from project1_2.friday_brain import friday_engine


app = Flask(__name__)
CORS(app)


@app.get("/")
def home():
    return redirect("/index.html", code=307)


@app.get("/favicon.ico")
def favicon():
    return redirect("/favicon.svg", code=307)


@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})


@app.post("/api/chat")
def chat():
    payload = request.get_json(silent=True) or {}
    message = (payload.get("message") or "").strip()

    if not message:
        return jsonify({"type": "text", "data": "Message is required"}), 400

    return jsonify(friday_engine(message))


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)
