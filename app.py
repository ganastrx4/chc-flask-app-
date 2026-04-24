import os
import time
import hmac
import hashlib
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# --- CONFIGURACIÓN ---
APP_ID = "app_7686f9027d3e3c0b53d987a3caf1e111"
ACTION = "login"
RP_ID = "rp_aa5ead0710fce1dc" 
# Lee la variable desde el panel de Render (Settings -> Environment)
SIGNING_KEY = os.environ.get('signer_key') 

def sign_request(signing_key_hex, action):
    """Genera la firma criptográfica para World ID 4.0"""
    if not signing_key_hex:
        print("ERROR: La variable 'signer_key' no está configurada en Render.")
        return None

    try:
        # Convertimos la clave hex a bytes eliminando espacios
        key = bytes.fromhex(signing_key_hex.strip())
        nonce = str(int(time.time() * 1000))
        created_at = int(time.time())
        expires_at = created_at + 3600 # 1 hora de validez
        
        # Formato de mensaje estándar de World ID 4.0
        message = f"{action}:{nonce}:{created_at}:{expires_at}".encode()
        sig = hmac.new(key, message, hashlib.sha256).hexdigest()
        
        return {
            "sig": sig,
            "nonce": nonce,
            "created_at": created_at,
            "expires_at": expires_at
        }
    except Exception as e:
        print(f"Error interno al firmar: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/rp-signature', methods=['POST'])
def get_signature():
    """Ruta para entregar la firma al Frontend"""
    try:
        sig_data = sign_request(SIGNING_KEY, ACTION)
        if sig_data is None:
            return jsonify({
                "error": "Error de configuración en el servidor",
                "detail": "Asegúrate de que 'signer_key' sea un valor hexadecimal válido en Render."
            }), 500
        
        return jsonify(sig_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/verify-proof', methods=['POST'])
def verify_proof():
    """Ruta para validar la prueba final con los servidores de Worldcoin"""
    try:
        idkit_data = request.json
        if not idkit_data:
            return jsonify({"error": "No se recibieron datos de IDKit"}), 400

        worldcoin_url = f"https://developer.world.org/api/v4/verify/{RP_ID}"
        
        response = requests.post(
            worldcoin_url,
            json=idkit_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            return jsonify({"success": True}), 200
        else:
            return jsonify({
                "success": False, 
                "error": "Fallo en Worldcoin", 
                "detail": response.json()
            }), response.status_code

    except Exception as e:
        return jsonify({"error": "Error interno del servidor", "detail": str(e)}), 500

if __name__ == '__main__':
    # Render usa la variable de entorno PORT
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
