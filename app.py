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


BSC_API_KEY = os.environ.get("BSC_API_KEY")
POOL_WALLET = "0xd4508db1adc48dea121f356b254a7155ddab36ae"
HASH_FILE = "hashes_bnb.json"

def load_hashes():
    if not os.path.exists(HASH_FILE):
        return set()
    with open(HASH_FILE, "r") as f:
        return set(json.load(f))

def save_hash(h):
    hashes = load_hashes()
    hashes.add(h)
    with open(HASH_FILE, "w") as f:
        json.dump(list(hashes), f)

def get_wld_price():
    try:
        r = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=WLDUSDT").json()
        return float(r["price"])
    except:
        return 1.0

def detectar_bnb():
    url = f"https://api.bscscan.com/api?module=account&action=txlist&address={POOL_WALLET}&sort=desc&apikey={BSC_API_KEY}"
    hashes = load_hashes()
    try:
        data = requests.get(url).json()
        for tx in data["result"]:
            if tx["to"].lower() != POOL_WALLET.lower():
                continue
            hash_tx = tx["hash"]
            monto = int(tx["value"]) / 10**18
            if hash_tx in hashes:
                continue
            if monto < 0.001:
                continue
            if int(tx["confirmations"]) < 3:
                continue
            print(f"[💰] Deposito detectado: {monto} BNB")
            wld_price = get_wld_price()
            chc = monto * wld_price * 100000
            try:
                requests.post("https://binance-bot-hna7.onrender.com/transferir", json={
                    "emisor": "BNB_POOL",
                    "receptor": "SISTEMA",
                    "monto": chc,
                    "firma": "BNB_BRIDGE"
                }, timeout=10)
            except:
                pass
            save_hash(hash_tx)
    except Exception as e:
        print("Error BNB:", e)

app = Flask(__name__)

# Lee la clave directamente desde las variables de entorno de Render
# Asegúrate de que en Render la llave se llame exactamente: signer_key
SIGNER_KEY = os.environ.get('signer_key') 

@app.route('/api/rp-signature', methods=['POST'])
def get_signature():
    if not SIGNER_KEY:
        return jsonify({"error": "signer_key no configurada en Render"}), 500

    data = request.json
    action = data.get('action', 'verify-account')
    
    nonce = str(uuid.uuid4())
    created_at = int(time.time())
    expires_at = created_at + 3600  # Válido por 1 hora

    # Generación de la firma HMAC-SHA256 exigida por World ID 4.0
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

APP_ID = "app_7686f9027d3e3c0b53d987a3caf1e111"
ACTION = "login"
VERIFY_URL = "https://developer.worldcoin.org/api/v2/verify"
DB_FILE = "nullifiers.txt"

WORLDCHAIN_RPC = "https://worldchain-mainnet.g.alchemy.com/v2/39Stwe7kZcWw8bQj6T0a7UIOgU7fq9P5"
w3 = Web3(Web3.HTTPProvider(WORLDCHAIN_RPC))

def load_nullifiers():
    if not os.path.exists(DB_FILE):
        return set()
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f.readlines())

def save_nullifier(value):
    with open(DB_FILE, "a", encoding="utf-8") as f:
        f.write(str(value) + "\n")

@app.after_request
def add_header(response):
    response.headers['Content-Security-Policy'] = "frame-ancestors 'self' https://world.org https://*.world.org"
    return response

@app.route("/")
@app.route("/index.html")
def home():
    return render_template("index.html")

paginas = [
    "buscador2.html", "enviarwld.html", "exchange.html", 
    "graficachcwld.html", "charlycoinapp.html", "chcoin.html", 
    "faucets.html", "chun.html", "next_page.html", 
    "ganarchun.html", "glosario.html", "wdd.html"
]

def create_route(page):
    endpoint = f"route_{page.replace('.html', '')}"
    @app.route(f"/{page}", endpoint=endpoint)
    def v(): return render_template(page)

for p in paginas:
    create_route(p)

@app.route("/api/verify-proof", methods=["POST"])
def verify_proof():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data"}), 400
        proof_data = data.get("proof", {})
        nullifier = data.get("nullifier_hash") or data.get("nullifier") or proof_data.get("nullifier_hash")
        if not nullifier:
            return jsonify({"success": False, "error": "No nullifier"}), 400
        used = load_nullifiers()
        if str(nullifier) in used:
            return jsonify({"success": False, "error": "Usuario ya verificado"}), 400
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
            save_nullifier(nullifier)
            return jsonify({"success": True, "message": "Verificado"})
        return jsonify({"success": False, "error": result}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/exchange", methods=["POST"])
def api_exchange():
    data = request.json
    tipo = data.get("tipo")
    cantidad = float(data.get("cantidad", 0))
    wld_price = get_wld_price()
    if tipo == "comprar":
        chc = cantidad * 100000
        return jsonify({"success": True, "chc": chc, "precio": wld_price})
    elif tipo == "vender":
        wld = cantidad / 100000
        return jsonify({"success": True, "wld": wld, "precio": wld_price})
    return jsonify({"success": False})

def loop_bnb():
    while True:
        detectar_bnb()
        time.sleep(15)

threading.Thread(target=loop_bnb, daemon=True).start()

@app.route("/api/status")
def status():
    return jsonify({
        "success": True,
        "app": "CHC Network",
        "blockchain_connected": w3.is_connected(),
        "world_id": True
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
