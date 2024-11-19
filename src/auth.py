from flask import Flask, request, jsonify
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

app = Flask(__name__)

@app.route("/login", methods=["POST"])
def login():
    token = request.headers.get("Authorization")
    if not token:
        return jsonify({"message": "Unauthorized"}), 401

    # Check token in Supabase
    response = supabase.table("tokens").select("token").eq("token", token).execute()
    if response.data:
        return jsonify({"message": "Access granted"}), 200
    return jsonify({"message": "Unauthorized"}), 403

if __name__ == "__main__":
    app.run(debug=True)
