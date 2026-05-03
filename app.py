import os
from flask import Flask, request, jsonify, render_template
import requests
from web3 import Web3

app = Flask(__name__)

# =========================
# CONFIGURACION
# =========================
APP_ID = "app_7686f9027d3e3c0b53d987a3caf1e111"
ACTION = "login"
VERIFY_URL = "https://developer.worldcoin.org/api/v2/verify"

# Este es el archivo que recuperamos, el que guarda a tus usuarios
DB_FILE = "nullifiers.txt"

# --- NODO ALCHEMY (Para que la App sea válida en World Chain) ---
WORLDCHAIN_RPC = "https://worldchain-mainnet.g.alchemy.com/v2/39Stwe7kZcWw8bQj6T0a7UIOgU7fq9P5"
w3 = Web3(Web3.HTTPProvider(WORLDCHAIN_RPC))

# =========================
# UTILIDADES (RECUPERADAS)
# =========================
def load_nullifiers():
    """Carga los usuarios que ya se registraron"""
    if not os.path.exists(DB_FILE):
        return set()
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f.readlines())

def save_nullifier(value):
    """Guarda un nuevo usuario verificado"""
    with open(DB_FILE, "a", encoding="utf-8") as f:
        f.write(str(value) + "\n")

# =========================
# SEGURIDAD Y RUTAS
# =========================
@app.after_request
def add_header(response):
    response.headers['Content-Security-Policy'] = "frame-ancestors 'self' https://world.org https://*.world.org"
    return response

@app.route("/")
@app.route("/index.html")
def home():
    return render_template("index.html")

# Registro automático de tus páginas .html
paginas = [
    "buscador2.html", "enviarwld.html", "exchange.html", 
    "graficachcwld.html", "charlycoinapp.html", "chcoin.html", 
    "faucets.html", "chun.html", "next_page.html", 
    "ganarchun.html", "glosario.html", "wdd.html"
]

def create_route(page):
    endpoint = page.replace(".html", "")
    @app.route(f"/{page}", endpoint=endpoint)
    def v(): return render_template(page)

for p in paginas:
    create_route(p)

# =========================
# WORLD ID VERIFY (TU LÓGICA QUE SI SERVÍA)
# =========================
@app.route("/api/verify-proof", methods=["POST"])
def verify_proof():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data"}), 400

        # Recuperamos la detección del nullifier que funcionaba antes
        proof_data = data.get("proof", {})
        nullifier = data.get("nullifier_hash") or data.get("nullifier") or proof_data.get("nullifier_hash")

        if not nullifier:
            return jsonify({"success": False, "error": "No nullifier"}), 400

        # Verificamos si ya existe en tu base de datos local
        used = load_nullifiers()
        if str(nullifier) in used:
            return jsonify({"success": False, "error": "Usuario ya verificado"}), 400

        # Payload para World Coin
        payload = {
            "app_id": APP_ID,
            "action": ACTION,
            "proof": data.get("proof"),
            "merkle_root": data.get("merkle_root"),
            "nullifier_hash": nullifier,
            "credential_type": data.get("credential_type", "orb"),
            "signal": data.get("signal", "")
        }

        r = requests.post(VERIFY_URL, json=payload, timeout=20)
        result = r.json()

        if r.status_code == 200 and result.get("success") is True:
            save_nullifier(nullifier) # Guardamos en tu archivo txt
            return jsonify({"success": True, "message": "Verificado"})

        return jsonify({"success": False, "error": result}), 400

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# =========================
# STATUS (HÍBRIDO: TU APP + WORLD CHAIN)
# =========================
@app.route("/api/status")
def status():
    return jsonify({
        "success": True,
        "app": "CHC Network",
        "blockchain_connected": w3.is_connected(), # Verifica tu nodo Alchemy
        "world_id": True # Confirma que el sistema de World ID está activo
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
