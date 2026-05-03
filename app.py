import os
import json
import time
import uuid
import hmac
import hashlib
import threading
import requests
from flask import Flask, request, jsonify, render_template
from web3 import Web3
from functools import wraps
from flask import session, redirect

app.secret_key = os.environ.get("FLASK_SECRET", "super_secret_session_key")

USERS_FILE = "users.json"

# =========================
# 📦 USERS (simple storage)
# =========================
def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)

def get_or_create_user(nullifier):
    users = load_users()

    if nullifier not in users:
        users[nullifier] = {
            "id": nullifier,
            "created_at": int(time.time()),
            "balance": 0
        }
        save_users(users)

    return users[nullifier]


# =========================
# 🔐 LOGIN REQUIRED
# =========================
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect("/")
        return f(*args, **kwargs)
    return wrapper
# ==========================================
# 🔐 CONFIG
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

app = Flask(__name__)

session = requests.Session()
w3 = Web3(Web3.HTTPProvider(WORLDCHAIN_RPC)) if WORLDCHAIN_RPC else None

# ==========================================
# 🧠 NULLIFIERS
# ==========================================
def load_nullifiers():
    if not os.path.exists(NULLIFIER_FILE):
        return set()
    with open(NULLIFIER_FILE, "r") as f:
        return set(line.strip() for line in f.readlines())

def save_nullifier(n):
    with open(NULLIFIER_FILE, "a") as f:
        f.write(n + "\n")

# ==========================================
# 🔑 RP SIGNATURE (CLAVE)
# ==========================================
@app.route("/api/rp-signature", methods=["POST"])
def rp_signature():

    if not SIGNER_KEY:
        return jsonify({"error": "signer_key missing"}), 500

    nonce = str(uuid.uuid4())
    now = int(time.time())
    expires = now + 300

    message = f"{ACTION}:{nonce}:{now}:{expires}"

    signature = hmac.new(
        bytes.fromhex(SIGNER_KEY),
        message.encode(),
        hashlib.sha256
    ).hexdigest()

    return jsonify({
        "signature": signature,
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
            return jsonify({"success": False, "error": "No nullifier"}), 400

        used = load_nullifiers()

        # 👇 opcional: permite login si ya existe
        # if nullifier in used:
        #     user = get_or_create_user(nullifier)
        #     session["user_id"] = user["id"]
        #     return jsonify({"success": True})

        payload = {
            "merkle_root": data.get("merkle_root"),
            "nullifier_hash": nullifier,
            "proof": data.get("proof"),
            "credential_type": "orb",
            "action": ACTION,
            "signal": "charlycoin_login"
        }

        r = requests.post(VERIFY_URL, json=payload, timeout=10)
        result = r.json()

        if result.get("success"):

            save_nullifier(nullifier)

            # 🔥 CREAR / OBTENER USUARIO
            user = get_or_create_user(nullifier)

            # 🔐 CREAR SESIÓN
            session["user_id"] = user["id"]

            return jsonify({"success": True})

        return jsonify({"success": False, "error": result}), 400

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ==========================================
# 💰 BNB → CHC BRIDGE
# ==========================================
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
        r = session.get("https://api.binance.com/api/v3/ticker/price?symbol=WLDUSDT")
        return float(r.json()["price"])
    except:
        return 1.0

def detectar_bnb():
    if not BSC_API_KEY:
        return

    url = f"https://api.bscscan.com/api?module=account&action=txlist&address={POOL_WALLET}&sort=desc&apikey={BSC_API_KEY}"
    hashes = load_hashes()

    try:
        data = session.get(url).json()

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
                    }
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
# 🌐 HEADERS
# ==========================================
@app.after_request
def headers(resp):
    resp.headers['Content-Security-Policy'] = "frame-ancestors 'self' https://*.world.org"
    return resp

# ==========================================
# 🌐 logout
# ==========================================
@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"success": True})


# ==========================================
# 🌐 route
# ==========================================
@app.route("/api/me")
def me():
    if "user_id" not in session:
        return jsonify({"logged": False})

    users = load_users()
    user = users.get(session["user_id"])

    return jsonify({
        "logged": True,
        "user": user
    })
# ==========================================
# 🌐 PAGINAS
# ==========================================
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
# 🔄 EXCHANGE
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
# 🚀 panel
# ==========================================
@app.route("/panel.html")
@login_required
def panel():
    return render_template("panel.html")
# ==========================================
# 🚀 START
# ==========================================
if __name__ == "__main__":
    threading.Thread(target=loop_bnb, daemon=True).start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
