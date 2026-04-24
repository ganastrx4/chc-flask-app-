import os
import time
import hmac
import hashlib
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# ---------------- CONFIGURACIÓN ----------------
APP_ID = "app_7686f9027d3e3c0b53d987a3caf1e111"
ACTION = "login"
RP_ID = "rp_aa5ead0710fce1dc"

# Variable de entorno en Render:
# signer_key = TU_CLAVE_HEX
SIGNING_KEY = os.getenv("signer_key", "").strip()

# Archivo simple para usuarios ya verificados
DB_FILE = "nullifiers.txt"


# ---------------- BASE SIMPLE ----------------
def save_nullifier(nullifier):
    with open(DB_FILE, "a", encoding="utf-8") as f:
        f.write(f"{nullifier}\n")


def is_nullifier_used(nullifier):
    if not os.path.exists(DB_FILE):
        return False

    with open(DB_FILE, "r", encoding="utf-8") as f:
        used = f.read().splitlines()

    return nullifier in used


# ---------------- FIRMA WORLD ID 4.0 ----------------
def sign_request(signing_key_hex, action):
    if not signing_key_hex:
        return None

    try:
        # Limpieza de seguridad
        clean_key = (
            signing_key_hex
            .strip()
            .replace("0x", "")
            .replace('"', "")
            .replace("{", "")
            .replace("}", "")
            .replace("\n", "")
            .replace("\r", "")
            .replace(" ", "")
        )

        key = bytes.fromhex(clean_key)

        nonce = str(int(time.time() * 1000))
        created_at = int(time.time())
        expires_at = created_at + 3600

        message = f"{action}:{nonce}:{created_at}:{expires_at}".encode()

        sig = hmac.new(
            key,
            message,
            hashlib.sha256
        ).hexdigest()

        return {
            "sig": sig,
            "nonce": nonce,
            "created_at": created_at,
            "expires_at": expires_at
        }

    except Exception as e:
        print("Error en firma:", e)
        return None


# ---------------- RUTAS ----------------
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/rp-signature", methods=["POST"])
def get_signature():
    # Si no existe clave
    if not SIGNING_KEY:
        return jsonify({
            "error": "Falta signer_key",
            "detail": "Configura la variable en Render"
        }), 500

    sig_data = sign_request(SIGNING_KEY, ACTION)

    # Si clave mala
    if sig_data is None:
        return jsonify({
            "error": "Clave inválida",
            "detail": "La signer_key no es hexadecimal válida"
        }), 500

    return jsonify(sig_data), 200


@app.route("/api/verify-proof", methods=["POST"])
def verify_proof():
    try:
        idkit_data = request.get_json()

        if not idkit_data:
            return jsonify({
                "error": "No hay datos"
            }), 400

        # ---------------- Anti duplicados ----------------
        nullifier = (
            idkit_data.get("nullifier_hash")
            or idkit_data.get("nullifier")
        )

        if nullifier and is_nullifier_used(nullifier):
            return jsonify({
                "success": False,
                "error": "Identidad duplicada",
                "detail": "Esta persona ya fue verificada"
            }), 400

        # ---------------- Verificación oficial ----------------
        worldcoin_url = f"https://developer.world.org/api/v4/verify/{RP_ID}"

        response = requests.post(
            worldcoin_url,
            json=idkit_data,
            timeout=15
        )

        # ---------------- Correcto ----------------
        if response.status_code == 200:
            if nullifier:
                save_nullifier(nullifier)

            return jsonify({
                "success": True
            }), 200

        # ---------------- Error World ----------------
        try:
            detail = response.json()
        except:
            detail = response.text

        return jsonify({
            "success": False,
            "detail": detail
        }), response.status_code

    except Exception as e:
        return jsonify({
            "error": "Error interno",
            "detail": str(e)
        }), 500


# ---------------- MAIN ----------------
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
