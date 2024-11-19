from flask import Flask, request, jsonify
from auth import login, generate_token

app = Flask(__name__)

@app.route("/login", methods=["POST"])
def login_route():
    token = request.headers.get("Authorization")
    return jsonify(*login(token))

@app.route("/generate-token", methods=["POST"])
def generate_token_route():
    return jsonify({"token": generate_token()})