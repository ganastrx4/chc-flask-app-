import os
import time
import hmac
import hashlib
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# --- CONFIGURACIÓN DESDE VARIABLES DE ENTORNO ---
# Aquí le decimos a Python que busque "signer_key" en la configuración de Render
APP_ID = "app_7686f9027d3e3c0b53d987a3caf1e111"
ACTION = "login"
RP_ID = "rp_aa5ead0710fce1dc" # Pon tu RP_ID aquí o también como variable
SIGNING_KEY = os.environ.get('signer_key') # <--- Lee la variable de Render

def sign_request(signing_key_hex, action):
    # Verificación de seguridad por si la variable no cargó
    if not signing_key_hex:
        print("ERROR: No se encontró la SIGNING_KEY en las variables de entorno.")
        return None

    key = bytes.fromhex(signing_key_hex)
    nonce = str(int(time.time() * 1000))
    created_at = int(time.time())
    expires_at = created_at + 3600 
    
    message = f"{action}:{nonce}:{created_at}:{expires_at}".encode()
    sig = hmac.new(key, message, hashlib.sha256).hexdigest()
    
    return {
        "sig": sig,
        "nonce": nonce,
        "created_at": created_at,
        "expires_at": expires_at
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/rp-signature', methods=['POST'])
def get_signature():
    # Retorna la firma para que el Frontend pueda iniciar IDKit
    return jsonify(sign_request(SIGNING_KEY, ACTION))

@app.route('/api/rp-signature', methods=['POST'])
def get_signature():
    try:
        sig_data = sign_request(SIGNING_KEY, ACTION)
        if sig_data is None:
            return jsonify({"error": "No se pudo generar la firma. Revisa la SIGNING_KEY."}), 500
        
        print(f"Firma generada con éxito: {sig_data['nonce']}") # Esto saldrá en tus logs
        return jsonify(sig_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/verify-proof', methods=['POST'])
def verify_proof():
    # Recibe el payload completo de IDKit y lo manda a Worldcoin (Step 5)
    idkit_data = request.json 
    
    worldcoin_url = f"https://developer.world.org/api/v4/verify/{RP_ID}"
    
    response = requests.post(
        worldcoin_url,
        json=idkit_data,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        return jsonify({"success": True}), 200
    else:
        return jsonify({"error": "Fallo en Worldcoin", "detail": response.json()}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
