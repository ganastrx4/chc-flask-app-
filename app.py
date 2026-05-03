import os
from flask import Flask, request, jsonify, render_template
import requests
from web3 import Web3
import json
import time
import threading
import uuid
import hmac
import hashlib

# Configuración de Entorno
BSC_API_KEY = os.environ.get("BSC_API_KEY")
POOL_WALLET = "0xd4508db1adc48dea121f356b254a7155ddab36ae"
HASH_FILE = "hashes_bnb.json"
SIGNER_KEY = os.environ.get('signer_key') 

# Configuración de World ID (Basado en docs.world.org)
APP_ID = "app_7686f9027d3e3c0b53d987a3caf1e111"
# IMPORTANTE: Esta acción debe ser la misma que configuraste en el Developer Portal
ACTION = "verify-account" 
# URL Actualizada a v4 según la documentación oficial
VERIFY_URL = "[https://developer.world.org/api/v4/verify](https://developer.world.org/api/v4/verify)"
DB_FILE = "nullifiers.txt"

app = Flask(__name__)

# --- LÓGICA DE WORLD ID ---

def load_nullifiers():
    if not os.path.exists(DB_FILE):
        return set()
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f.readlines())

def save_nullifier(value):
    with open(DB_FILE, "a", encoding="utf-8") as f:
        f.write(str(value) + "\n")

@app.route('/api/rp-signature', methods=['POST'])
def get_signature():
    if not SIGNER_KEY:
        return jsonify({"error": "signer_key no configurada en Render"}), 500

    data = request.json
    # Usamos la acción global para mantener consistencia
    action = data.get('action', ACTION)
    
    nonce = str(uuid.uuid4())
    created_at = int(time.time())
    expires_at = created_at + 3600 

    # Generación de firma HMAC-SHA256 (Exigido para MiniKit)
    message = f"{action}:{nonce}:{created_at}:{expires_at}"
    signature = hmac.new(
        bytes.fromhex(SIGNER_KEY),
        message.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    return jsonify({
        "sig": signature,
        "nonce": nonce,
        "created_at": created_at,
        "expires_at": expires_at
    })

@app.route("/api/verify-proof", methods=["POST"])
def verify_proof():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data"}), 400

        # Según la doc, el payload de MiniKit envía el resultado en 'proof' o directo
        nullifier_hash = data.get("nullifier_hash")
        
        # 1. Verificación de Replay (Nullifier Check)
        used_nullifiers = load_nullifiers()
        if nullifier_hash in used_nullifiers:
            return jsonify({"success": False, "error": "Esta identidad ya ha sido utilizada"}), 400

        # 2. Preparar payload para la API v4 de Worldcoin
        # La API espera los campos: nullifier_hash, proof, merkle_root, verification_level, action, signal
        payload = {
            "nullifier_hash": nullifier_hash,
            "proof": data.get("proof"),
            "merkle_root": data.get("merkle_root"),
            "verification_level": data.get("verification_level", "orb"),
            "action": ACTION,
            "signal": data.get("signal", "charlycoin_login")
        }

        # 3. Petición a Worldcoin Developer Portal
        # Nota: La URL v4 requiere el app_id en la ruta: /api/v4/verify/{app_id}
        response = requests.post(f"{VERIFY_URL}/{APP_ID}", json=payload, timeout=20)
        result = response.json()

        if response.status_code == 200:
            save_nullifier(nullifier_hash)
            return jsonify({"success": True, "message": "Verificación exitosa"})
        else:
            return jsonify({"success": False, "error": result}), response.status_code

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# --- LÓGICA DE BLOCKCHAIN (BNB/WLD) ---

WORLDCHAIN_RPC = "[https://worldchain-mainnet.g.alchemy.com/v2/39Stwe7kZcWw8bQj6T0a7UIOgU7fq9P5](https://worldchain-mainnet.g.alchemy.com/v2/39Stwe7kZcWw8bQj6T0a7UIOgU7fq9P5)"
w3 = Web3(Web3.HTTPProvider(WORLDCHAIN_RPC))

def load_hashes():
    if not os.path.exists(HASH_FILE): return set()
    with open(HASH_FILE, "r") as f: return set(json.load(f))

def save_hash(h):
    hashes = load_hashes()
    hashes.add(h)
    with open(HASH_FILE, "w") as f: json.dump(list(hashes), f)

def get_wld_price():
    try:
        r = requests.get("[https://api.binance.com/api/v3/ticker/price?symbol=WLDUSDT](https://api.binance.com/api/v3/ticker/price?symbol=WLDUSDT)").json()
        return float(r["price"])
    except: return 1.0

def detectar_bnb():
    if not BSC_API_KEY: return
    url = f"[https://api.bscscan.com/api?module=account&action=txlist&address=](https://api.bscscan.com/api?module=account&action=txlist&address=){POOL_WALLET}&sort=desc&apikey={BSC_API_KEY}"
    hashes = load_hashes()
    try:
        data = requests.get(url).json()
        if data["status"] != "1": return
        for tx in data["result"]:
            if tx["to"].lower() != POOL_WALLET.lower(): continue
            hash_tx = tx["hash"]
            if hash_tx in hashes: continue
            
            monto = int(tx["value"]) / 10**18
            if monto >= 0.001 and int(tx["confirmations"]) >= 3:
                print(f"[💰] Deposito: {monto} BNB")
                wld_price = get_wld_price()
                chc = monto * wld_price * 100000
                requests.post("[https://binance-bot-hna7.onrender.com/transferir](https://binance-bot-hna7.onrender.com/transferir)", 
                              json={"emisor": "BNB_POOL", "receptor": "SISTEMA", "monto": chc, "firma": "BNB_BRIDGE"}, 
                              timeout=10)
                save_hash(hash_tx)
    except: pass

# --- RUTAS DE NAVEGACIÓN ---

@app.after_request
def add_header(response):
    response.headers['Content-Security-Policy'] = "frame-ancestors 'self' [https://world.org](https://world.org) https://*.world.org"
    return response

@app.route("/")
def home(): return render_template("index.html")

paginas = ["buscador2.html", "enviarwld.html", "exchange.html", "graficachcwld.html", 
           "charlycoinapp.html", "chcoin.html", "faucets.html", "chun.html", 
           "next_page.html", "ganarchun.html", "glosario.html", "wdd.html"]

for p in paginas:
    endpoint = f"route_{p.replace('.html', '')}"
    app.add_url_rule(f"/{p}", endpoint=endpoint, view_func=lambda p=p: render_template(p))

@app.route("/api/exchange", methods=["POST"])
def api_exchange():
    data = request.json
    tipo = data.get("tipo")
    cantidad = float(data.get("cantidad", 0))
    wld_price = get_wld_price()
    if tipo == "comprar":
        return jsonify({"success": True, "chc": cantidad * 100000, "precio": wld_price})
    return jsonify({"success": True, "wld": cantidad / 100000, "precio": wld_price})

def loop_bnb():
    while True:
        detectar_bnb()
        time.sleep(20)

threading.Thread(target=loop_bnb, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
