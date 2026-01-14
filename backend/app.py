from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sys, os
from flask import send_from_directory


import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# from project1_2.friday_brain import friday_engine
from project1_2.friday_brain import friday_engine


app = Flask(__name__)
CORS(app)

# IMAGE_DIR = os.path.abspath("../project1_2/images")
IMAGE_DIR = os.path.join(os.path.dirname(__file__), "images")

@app.route("/chat", methods=["POST"])
def chat():
    msg = request.json.get("message", "")
    return jsonify(friday_engine(msg))

@app.route("/images/<filename>")
def images(filename):
    return send_from_directory(IMAGE_DIR, filename)

# app.run(port=5000)
# app.run(port=5000, debug=True, use_reloader=False)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

# @app.route("/images/<path:filename>")
# def serve_image(filename):
#     return send_from_directory("../project1_2/images", filename)
