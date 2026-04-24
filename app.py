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
SIGNING_KEY = os.environ.get('signer_key') 

# Archivo local para persistencia de usuarios (Base de Datos simple)
DB_FILE = "nullifiers.txt"

def save_nullifier(nullifier):
    """Guarda el ID anónimo en un archivo para que no se borre al reiniciar"""
    with open(DB_FILE, "a") as f:
        f.write(f"{nullifier}\n")

def is_nullifier_used(nullifier):
    """Revisa si el usuario ya se había verificado antes"""
    if not os.path.exists(DB_FILE):
        return False
    with open(DB_FILE, "r") as f:
        used_nullifiers = f.read().splitlines()
    return nullifier in used_nullifiers

def sign_request(signing_key_hex, action):
    """Genera la firma criptográfica obligatoria para World ID 4.0"""
    if not signing_key_hex:
        return None
    try:
        # Limpieza de seguridad
        clean_key = signing_key_hex.strip().replace('0x', '').replace('"', '').replace('{', '').replace('}', '')
        key = bytes.fromhex(clean_key)
        
        nonce = str(int(time.time() * 1000))
        created_at = int(time.time())
        expires_at = created_at + 3600 
        
        message = f"{action}:{nonce}:{created_at}:{expires_at}".encode()
        sig = hmac.new(key, message, hashlib.sha256).hexdigest()
        
        return {
            "sig": sig, "nonce": nonce, 
            "created_at": created_at, "expires_at": expires_at
        }
    except Exception as e:
        print(f"Error en firma: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/rp-signature', methods=['POST'])
def get_signature():
    """Step 3: Provee la firma al frontend"""
    sig_data = sign_request(SIGNING_KEY, ACTION)
    if sig_data is None:
        return jsonify({"error": "Error de configuración", "detail": "Revisa la clave en Render"}), 500
    return jsonify(sig_data)

@app.route('/api/verify-proof', methods=['POST'])
def verify_proof():
    """Step 5 y 6: Verifica con Worldcoin y protege contra duplicados"""
    try:
        idkit_data = request.json
        if not idkit_data:
            return jsonify({"error": "No hay datos"}), 400

        # --- STEP 6: PROTECCIÓN SYBIL (Detección de duplicados) ---
        # El nullifier_hash identifica de forma anónima a la persona física
        nullifier = idkit_data.get('nullifier_hash') or idkit_data.get('nullifier')
        
        if nullifier and is_nullifier_used(nullifier):
            return jsonify({
                "success": False, 
                "error": "Identidad duplicada", 
                "detail": "Esta persona ya ha sido verificada en CharlyCoin."
            }), 400

        # --- STEP 5: VALIDACIÓN CON WORLDCOIN ---
        worldcoin_url = f"https://developer.world.org/api/v4/verify/{RP_ID}"
        response = requests.post(worldcoin_url, json=idkit_data, timeout=10)
        
        if response.status_code == 200:
            # Guardamos para que no pueda volver a registrarse
            if nullifier:
                save_nullifier(nullifier)
            return jsonify({"success": True}), 200
        else:
            return jsonify({"success": False, "detail": response.json()}), response.status_code

    except Exception as e:
        return jsonify({"error": "Error interno", "detail": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
