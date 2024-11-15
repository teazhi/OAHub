import secrets
import json
import os
from flask import request, jsonify

TOKEN_FILE = os.path.join(os.path.dirname(__file__), "..", "config", "tokens.json")
valid_tokens = []

def load_tokens():
    global valid_tokens
    try:
        with open(TOKEN_FILE, "r") as file:
            valid_tokens = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        valid_tokens = []

def save_tokens():
    with open(TOKEN_FILE, "w") as file:
        json.dump(valid_tokens, file)

load_tokens()

def login():
    load_tokens()
    token = request.headers.get("Authorization")
    if token in valid_tokens:
        return jsonify({"message": "Access granted"}), 200
    return jsonify({"message": "Unauthorized"}), 403

def generate_token():
    token = secrets.token_hex(16)
    valid_tokens.append(token)
    save_tokens()
    return token