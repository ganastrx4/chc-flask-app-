import os
import json
import time
import threading
import secrets
import requests
from flask import Flask, request, jsonify, render_template
from web3 import Web3
from functools import wraps

# ==========================================
# 🔐 CONFIG GLOBAL
# ==========================================

APP_ID = "app_7686f9027d3e3c0b53d987a3caf1e111"
ACTION = "verify-account"
VERIFY_URL = "https://developer.worldcoin.org/api/v1/verify"

SIGNER_KEY = os.environ.get("signer_key")
BSC_API_KEY = os.environ.get("BSC_API_KEY")

POOL_WALLET = "0xd4508db1adc48dea121f356b254a7155ddab36ae"

HASH_FILE = "hashes_bnb.json"
NULLIFIER_FILE = "nullifiers.txt"

WORLDCHAIN_RPC = os.environ.get("WORLDCHAIN_RPC")

# ==========================================
# 🚀 APP INIT
# ==========================================

app = Flask(__name__)

session = requests.Session()
session.headers.update({"Content-Type": "application/json"})

w3 = Web3(Web3.HTTPProvider(WORLDCHAIN_RPC)) if WORLDCHAIN_RPC else None

# ==========================================
# 🧠 UTILIDADES SEGURAS
# ==========================================

def safe_load_json(file, default):
    try:
        if not os.path.exists(file):
            return default
        with open(file, "r") as f:
            return json.load(f)
    except:
        return default

def safe_save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f)

# ==========================================
# 🔐 NULLIFIERS (ANTI MULTI CUENTA)
# ==========================================

def load_nullifiers():
    if not os.path.exists(NULLIFIER_FILE):
        return set()
    with open(NULLIFIER_FILE, "r") as f:
        return set(line.strip() for line in f.readlines())

def save_nullifier(value):
    with open(NULLIFIER_FILE, "a") as f:
        f.write(value + "\n")

# ==========================================
# 🔑 RP SIGNATURE (MiniKit)
# ==========================================

@app.route("/api/rp-signature", methods=["POST"])
def rp_signature():
    if not SIGNER_KEY:
        return jsonify({"error": "signer_key missing"}), 500

    nonce = secrets.token_hex(32)
    now = int(time.time())
    expires = now + 300

    return jsonify({
        "nonce": nonce,
        "created_at": now,
        "expires_at": expires
    })

# ==========================================
# ✅ VERIFY WORLD ID
# ==========================================

@app.route("/api/verify-proof", methods=["POST"])
def verify_proof():
    try:
        data = request.json or {}

        nullifier = data.get("nullifier_hash")

        if not nullifier:
            # fallback web
            if data.get("proof"):
                return jsonify({"success": True})
            return jsonify({"success": False, "error": "No nullifier"}), 400

        used = load_nullifiers()

        if nullifier in used:
            return jsonify({"success": False, "error": "Ya usado"}), 400

        payload = {
            "merkle_root": data.get("merkle_root"),
            "nullifier_hash": nullifier,
            "proof": data.get("proof"),
            "credential_type": "orb",
            "action": ACTION,
            "signal": "charlycoin"
        }

        r = session.post(VERIFY_URL, json=payload, timeout=10)
        result = r.json()

        if result.get("success"):
            save_nullifier(nullifier)
            return jsonify({"success": True})

        return jsonify({"success": False, "error": result}), 400

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ==========================================
# 💰 BNB → CHC BRIDGE
# ==========================================

def load_hashes():
    return set(safe_load_json(HASH_FILE, []))

def save_hash(h):
    hashes = load_hashes()
    hashes.add(h)
    safe_save_json(HASH_FILE, list(hashes))

def get_wld_price():
    try:
        r = session.get("https://api.binance.com/api/v3/ticker/price?symbol=WLDUSDT", timeout=5)
        return float(r.json()["price"])
    except:
        return 1.0

def detectar_bnb():
    if not BSC_API_KEY:
        return

    url = f"https://api.bscscan.com/api?module=account&action=txlist&address={POOL_WALLET}&sort=desc&apikey={BSC_API_KEY}"
    hashes = load_hashes()

    try:
        data = session.get(url, timeout=10).json()
        if data.get("status") != "1":
            return

        for tx in data["result"]:
            if tx["to"].lower() != POOL_WALLET.lower():
                continue

            h = tx["hash"]
            if h in hashes:
                continue

            value = int(tx["value"]) / 1e18
            conf = int(tx["confirmations"])

            if value >= 0.001 and conf >= 3:
                price = get_wld_price()
                chc = value * price * 100000

                session.post(
                    "https://binance-bot-hna7.onrender.com/transferir",
                    json={
                        "emisor": "BNB_POOL",
                        "receptor": "SISTEMA",
                        "monto": chc,
                        "firma": "BNB_BRIDGE"
                    },
                    timeout=10
                )

                save_hash(h)
                print(f"[💰] {value} BNB → {chc} CHC")

    except Exception as e:
        print("Error BNB:", e)

def loop_bnb():
    while True:
        detectar_bnb()
        time.sleep(20)

# ==========================================
# 🌐 RUTAS WEB
# ==========================================

@app.after_request
def headers(resp):
    resp.headers['Content-Security-Policy'] = "frame-ancestors 'self' https://*.world.org"
    return resp

@app.route("/")
def home():
    return render_template("index.html")

PAGES = [
    "buscador2.html","enviarwld.html","exchange.html","graficachcwld.html",
    "charlycoinapp.html","chcoin.html","faucets.html","chun.html",
    "next_page.html","ganarchun.html","glosario.html","wdd.html"
]

for p in PAGES:
    app.add_url_rule(f"/{p}", p, lambda p=p: render_template(p))

# ==========================================
# 🔄 API EXCHANGE
# ==========================================

@app.route("/api/exchange", methods=["POST"])
def exchange():
    data = request.json or {}
    tipo = data.get("tipo")
    cantidad = float(data.get("cantidad", 0))

    price = get_wld_price()

    if tipo == "comprar":
        return jsonify({"success": True, "chc": cantidad * 100000, "precio": price})

    return jsonify({"success": True, "wld": cantidad / 100000, "precio": price})

# ==========================================
# 🚀 START
# ==========================================

if __name__ == "__main__":
    threading.Thread(target=loop_bnb, daemon=True).start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
