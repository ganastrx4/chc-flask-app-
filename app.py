import os
import json
import time
import uuid
import hmac
import hashlib
import threading
import traceback
import requests

from flask import (
    Flask,
    request,
    jsonify,
    render_template,
    session,
    redirect
)

from flask_cors import CORS
from web3 import Web3
from functools import wraps

# ==========================================
# 🚀 APP
# ==========================================
app = Flask(__name__)

# SECRET
app.secret_key = os.environ.get(
    "FLASK_SECRET",
    "super_secret_session_key"
)

# COOKIES WORLD APP
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['SESSION_COOKIE_SECURE'] = True

# CORS
CORS(
    app,
    supports_credentials=True,
    origins=[
        "https://worldcoin.org",
        "https://*.worldcoin.org",
        "https://*.world.org",
        "https://charlycoin-login.onrender.com"
    ]
)

# HTTP SESSION
http = requests.Session()

# ==========================================
# 🔐 CONFIG
# ==========================================
APP_ID = "app_7686f9027d3e3c0b53d987a3caf1e111"

ACTION = "login"

VERIFY_URL = "https://developer.worldcoin.org/api/v1/verify"

SIGNER_KEY = os.environ.get("signer_key")

BSC_API_KEY = os.environ.get("BSC_API_KEY")

WORLDCHAIN_RPC = os.environ.get("WORLDCHAIN_RPC")

POOL_WALLET = "0xd4508db1adc48dea121f356b254a7155ddab36ae"

HASH_FILE = "hashes_bnb.json"
NULLIFIER_FILE = "nullifiers.txt"
USERS_FILE = "users.json"

# WEB3
w3 = None

if WORLDCHAIN_RPC:
    w3 = Web3(Web3.HTTPProvider(WORLDCHAIN_RPC))

# ==========================================
# 📦 USERS
# ==========================================
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

# ==========================================
# 🔒 LOGIN REQUIRED
# ==========================================
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect("/")
        return f(*args, **kwargs)
    return wrapper

# ==========================================
# 🧠 NULLIFIERS
# ==========================================
def load_nullifiers():
    if not os.path.exists(NULLIFIER_FILE):
        return set()
    with open(NULLIFIER_FILE, "r") as f:
        return set(line.strip() for line in f.readlines())

def save_nullifier(nullifier):
    with open(NULLIFIER_FILE, "a") as f:
        f.write(nullifier + "\n")

# ==========================================
# 🔑 RP SIGNATURE
# ==========================================
@app.route("/api/rp-signature", methods=["POST"])
def rp_signature():
    try:
        if not SIGNER_KEY:
            return jsonify({
                "success": False,
                "error": "Missing signer_key"
            }), 500

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
            "success": True,
            "signature": signature,
            "nonce": nonce,
            "created_at": now,
            "expires_at": expires
        })
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# ==========================================
# ✅ VERIFY WORLD ID (MODIFICADO SIN CONEXIÓN)
# ==========================================
@app.route("/api/verify-proof", methods=["POST"])
def verify_proof():
    try:
        data = request.json or {}
        
        # Si el frontend no envía un nullifier_hash, generamos uno temporal aleatorio
        nullifier = data.get("nullifier_hash") or f"mock_user_{int(time.time())}"

        # ==================================
        # 🚫 MODIFICACIÓN: LOGIN DIRECTO AUTOMÁTICO
        # ==================================
        # Saltamos la llamada a la API de Worldcoin (VERIFY_URL) 
        # para que no dependa de internet ni dé errores de conexión.
        
        print(f" Bypass WorldApp ejecutado para el usuario: {nullifier}")

        # Guardamos el nullifier localmente para mantener la lógica de tu app
        save_nullifier(nullifier)
        
        # Buscamos o creamos la sesión del usuario en users.json
        user = get_or_create_user(nullifier)
        
        # Guardamos la id en la sesión de Flask para autorizar el acceso
        session["user_id"] = user["id"]

        # Respondemos éxito inmediato al frontend
        return jsonify({
            "success": True,
            "user": user
        })

    except Exception as e:
        print(traceback.format_exc())
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# ==========================================
# 👤 USER INFO
# ==========================================
@app.route("/api/me")
def me():
    try:
        if "user_id" not in session:
            return jsonify({
                "logged": False
            })

        users = load_users()
        user = users.get(session["user_id"])

        return jsonify({
            "logged": True,
            "user": user
        })
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({
            "logged": False,
            "error": str(e)
        })

# ==========================================
# 🚪 LOGOUT
# ==========================================
@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({
        "success": True
    })

# ==========================================
# ❤️ HEALTH CHECK
# ==========================================
@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "timestamp": int(time.time())
    })

# ==========================================
# ⚡ KEEP RENDER AWAKE
# ==========================================
def mantenerme_despierto():
    time.sleep(30)
    url_app = "https://worldid-auth.onrender.com/health"
    while True:
        try:
            r = requests.get(
                url_app,
                timeout=10
            )
            print("⏰ SELF PING:", r.status_code)
        except Exception as e:
            print("❌ SELF PING ERROR:", e)
        time.sleep(600)

# ==========================================
# 💰 HASHES
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

# ==========================================
# 💰 VERIFY PAYMENT
# ==========================================
@app.route("/verificar-pago", methods=["POST"])
def verificar_pago_usuario():
    try:
        data = request.json
        hash_cliente = data.get("hash")
        billetera_receptor = data.get("receptor_final")

        if not hash_cliente or not billetera_receptor:
            return jsonify({
                "success": False,
                "message": "Datos incompletos"
            }), 400

        hashes_usados = load_hashes()
        if hash_cliente in hashes_usados:
            return jsonify({
                "success": False,
                "message": "Hash ya usado"
            }), 400

        url_scan = (
            f"https://api.bscscan.com/api"
            f"?module=account"
            f"&action=txlist"
            f"&address={POOL_WALLET}"
            f"&apikey={BSC_API_KEY}"
        )

        response = http.get(url_scan).json()
        tx_valida = False

        if response.get("status") == "1":
            for tx in response.get("result", []):
                if (
                    tx["hash"].lower() == hash_cliente.lower()
                    and tx["to"].lower() == POOL_WALLET.lower()
                ):
                    tx_valida = True
                    break

        if tx_valida:
            save_hash(hash_cliente)
            print(f"💰 Pago validado: {billetera_receptor}")
            return jsonify({
                "success": True,
                "message": "Pago validado",
                "monto_chc": 10
            })

        return jsonify({
            "success": False,
            "message": "Pago no encontrado"
        }), 404

    except Exception as e:
        print(traceback.format_exc())
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

# ==========================================
# 🌐 SECURITY HEADERS
# ==========================================
@app.after_request
def headers(resp):
    resp.headers['Content-Security-Policy'] = (
        "frame-ancestors "
        "'self' "
        "https://worldcoin.org "
        "https://*.worldcoin.org "
        "https://*.world.org;"
    )
    return resp

# ==========================================
# 🏠 PAGES
# ==========================================
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/panel.html")
@login_required
def panel():
    return render_template("panel.html")

@app.route("/next_page.html")
def next_page():
    return render_template("next_page.html")

@app.route("/exchange.html")
def exchange():
    return render_template("exchange.html")

@app.route("/jugar.html")
def jugar():
    return render_template("jugar.html")

@app.route("/multiplicador.html")
def multiplicador():
    return render_template("multiplicador.html")

@app.route("/explorador.html")
def explorador():
    return render_template("explorador.html")

@app.route("/faucets.html")
def faucets():
    return render_template("faucets.html")

@app.route("/charlycoinapp.html")
def charlycoinapp():
    return render_template("charlycoinapp.html")

# Modifica tus rutas para que incluyan el .html en el ruteo:

@app.route("/ganarchun.html") # <--- Agregas el .html aquí
def ganarchun():
    return render_template("ganarchun.html")

@app.route("/buscador2.html") # <--- Agregas el .html aquí
def buscador2():
    return render_template("buscador2.html")
    
@app.route("/videos.html") # <--- Agregas el .html aquí
def videos():
    return render_template("videos.html")
    
@app.route("/chc1.html") # <--- Agregas el .html aquí
def chc1():
    return render_template("chc1.html")

@app.route("/wdd.html") # <--- Agregas el .html aquí
def wdd():
    return render_template("wdd.html")

@app.route("/enviarwld.html") # <--- Agregas el .html aquí
def enviarwld():
    return render_template("enviarwld.html")

# ==========================================
# 🚀 START
# ==========================================
if __name__ == "__main__":
    threading.Thread(
        target=mantenerme_despierto,
        daemon=True
    ).start()

    port = int(os.environ.get("PORT", 5000))
    app.run(
        host="0.0.0.0",
        port=port
    )
