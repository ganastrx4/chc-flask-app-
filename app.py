import os
import json
from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)

# =========================
# CONFIGURACION
# =========================
APP_ID = "app_7686f9027d3e3c0b53d987a3caf1e111"
ACTION = "login"
VERIFY_URL = "https://developer.worldcoin.org/api/v2/verify"

# archivo simple anti-duplicados
DB_FILE = "nullifiers.txt"


# =========================
# UTILIDADES
# =========================
def load_nullifiers():
    if not os.path.exists(DB_FILE):
        return set()
    with open(DB_FILE, "r") as f:
        return set(line.strip() for line in f.readlines())


def save_nullifier(value):
    with open(DB_FILE, "a") as f:
        f.write(str(value) + "\n")


# =========================
# WEB
# =========================
@app.route("/")
def home():
    return render_template("index.html")


# =========================
# VERIFY WORLD ID V4
# =========================
@app.route("/api/verify-proof", methods=["POST"])
def verify_proof():
    try:
        data = request.json

        if not data:
            return jsonify({
                "success": False,
                "error": "No data"
            }), 400

        # detectar nullifier en varias versiones
        nullifier = (
            data.get("nullifier_hash")
            or data.get("nullifier")
            or data.get("proof", {}).get("nullifier_hash")
        )

        if not nullifier:
            return jsonify({
                "success": False,
                "error": "No nullifier"
            }), 400

        # evitar duplicados
        used = load_nullifiers()

        if str(nullifier) in used:
            return jsonify({
                "success": False,
                "error": "Usuario ya verificado"
            }), 400

        # payload oficial world id
        payload = {
            "app_id": app_7686f9027d3e3c0b53d987a3caf1e111,
            "action": login,
            "proof": data.get("proof"),
            "merkle_root": data.get("merkle_root"),
            "nullifier_hash": nullifier,
            "credential_type": data.get("credential_type", "orb"),
            "signal": data.get("signal", "")
        }

        # request oficial
        r = requests.post(
            VERIFY_URL,
            json=payload,
            timeout=20
        )

        result = r.json()

        print("WORLD RESPONSE:", result)

        if r.status_code == 200 and result.get("success") is True:

            save_nullifier(nullifier)

            return jsonify({
                "success": True,
                "message": "Verificado"
            })

        return jsonify({
            "success": False,
            "error": result
        }), 400

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
# =========================
# buscador
# =========================
@app.route("/buscador2.html")
def buscador():
    return render_template("buscador2.html")
# =========================
# RUN
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
