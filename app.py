import os
import sys
from pathlib import Path
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup sys.path to allow imports from backend
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Initialize database schema and default seeds
from backend.db_setup import init_db
init_db()

from backend.models import User, Reminder, InteractionLog, Settings
from backend.command_processor import process_command

# Initialize Flask app serving from frontend folder as static assets
app = Flask(__name__, static_folder="frontend", static_url_path="")
CORS(app)

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/favicon.ico")
def favicon():
    return send_from_directory(app.static_folder, "favicon.svg")

@app.route("/<path:path>")
def serve_static(path):
    # Ensure standard route fallbacks to static folder
    return send_from_directory(app.static_folder, path)

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "project": "FRIDAY AI Virtual Assistant"})

@app.route("/api/chat", methods=["POST"])
def chat():
    payload = request.get_json(silent=True) or {}
    message = (payload.get("message") or "").strip()

    if not message:
        return jsonify({"type": "text", "data": "Message is required"}), 400

    user_id = User.get_default_user_id()
    result = process_command(message, user_id)
    
    # Save the interaction to the database logs
    InteractionLog.log(user_id, message, result["data"], result["type"])
    
    return jsonify(result)

# CRUD: Reminders
@app.route("/api/reminders", methods=["GET"])
def get_reminders():
    user_id = User.get_default_user_id()
    reminders = Reminder.get_all(user_id)
    return jsonify(reminders)

@app.route("/api/reminders", methods=["POST"])
def add_reminder():
    payload = request.get_json(silent=True) or {}
    text = (payload.get("text") or "").strip()
    time = (payload.get("time") or "").strip()
    
    if not text or not time:
        return jsonify({"error": "Both 'text' and 'time' are required."}), 400
        
    user_id = User.get_default_user_id()
    reminder = Reminder.create(user_id, text, time)
    return jsonify(reminder), 201

@app.route("/api/reminders/complete", methods=["POST"])
def complete_reminder():
    payload = request.get_json(silent=True) or {}
    reminder_id = payload.get("id")
    
    if not reminder_id:
        return jsonify({"error": "Reminder ID is required."}), 400
        
    Reminder.complete(reminder_id)
    return jsonify({"success": True})

@app.route("/api/reminders/<int:reminder_id>", methods=["DELETE"])
def delete_reminder(reminder_id):
    Reminder.delete(reminder_id)
    return jsonify({"success": True})

# CRUD: History
@app.route("/api/history", methods=["GET"])
def get_history():
    user_id = User.get_default_user_id()
    history = InteractionLog.get_all(user_id)
    return jsonify(history)

@app.route("/api/history", methods=["DELETE"])
def clear_history():
    user_id = User.get_default_user_id()
    InteractionLog.clear(user_id)
    return jsonify({"success": True})

# CRUD: Settings
@app.route("/api/settings", methods=["GET"])
def get_settings():
    user_id = User.get_default_user_id()
    settings = Settings.get_by_user(user_id)
    return jsonify(settings)

@app.route("/api/settings", methods=["POST"])
def update_settings():
    payload = request.get_json(silent=True) or {}
    theme = payload.get("theme", "dark")
    voice_enabled = payload.get("voice_enabled", 1)
    volume = payload.get("volume", 1.0)
    rate = payload.get("rate", 190)
    weather_city = payload.get("weather_city", "Mumbai")
    
    user_id = User.get_default_user_id()
    updated = Settings.update(user_id, theme, voice_enabled, volume, rate, weather_city)
    return jsonify(updated)

if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)
