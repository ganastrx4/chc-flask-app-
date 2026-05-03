import os
from flask import Flask, request, jsonify, render_template
import requests
from web3 import Web3  # Importación de Web3 añadida

app = Flask(__name__)

# =========================
# CONFIGURACION
# =========================
APP_ID = "app_7686f9027d3e3c0b53d987a3caf1e111"
ACTION = "login"
VERIFY_URL = "https://developer.worldcoin.org/api/v2/verify"

DB_FILE = "nullifiers.txt"

# --- CONEXIÓN A WORLD CHAIN ---
# Aquí integramos tu Alchemy URL para conectarte a la red real
WORLDCHAIN_RPC = "https://worldchain-mainnet.g.alchemy.com/v2/39Stwe7kZcWw8bQj6T0a7UIOgU7fq9P5"
w3 = Web3(Web3.HTTPProvider(WORLDCHAIN_RPC))

# Validamos la conexión
if w3.is_connected():
    print("✅ Conectado exitosamente a World Chain")
else:
    print("❌ Error de conexión a World Chain")

# =========================
# UTILIDADES
# =========================
def load_nullifiers():
    if not os.path.exists(DB_FILE):
        return set()
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f.readlines())

def save_nullifier(value):
    with open(DB_FILE, "a", encoding="utf-8") as f:
        f.write(str(value) + "\n")

# =========================
# SEGURIDAD (FUNDAMENTAL PARA APROBACIÓN)
# =========================
@app.after_request
def add_header(response):
    # Esto permite que tu app se vea dentro de World App sin bloqueos
    response.headers['Content-Security-Policy'] = "frame-ancestors 'self' https://world.org https://*.world.org"
    return response

# =========================
# PAGINAS (RUTAS)
# =========================
@app.route("/")
@app.route("/index.html")
def home():
    return render_template("index.html")

# Agrupé tus rutas para que el código sea más limpio
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
# WORLD ID VERIFY (BACKEND)
# =========================
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


# =====================================================
# CONFIGURACIÓN DE LA MASTER WALLET (VÍA ENV)
# =====================================================

# Intentamos obtener la llave del entorno; si no existe, el servidor avisará
MASTER_PRIVADA = os.environ.get("MASTER_PRIVADA")

# Tu dirección pública (esta puede quedarse en el código, es segura de compartir)
MASTER_PUBLICA = "93aab2b2ee274042d81954cd6569085ac3f1f660d600e6c7ca3aa11adbf94e62544ff783541316f3c7269d751079414e879f18804dde24c1b83c70c4e13cd4ee"

# Verificación de seguridad al arrancar
if not MASTER_PRIVADA:
    print("⚠️ ADVERTENCIA: La variable MASTER_PRIVADA no está configurada en el entorno.")

@app.route("/regalo_bienvenida", methods=["POST"])
def regalo_bienvenida():
    if not MASTER_PRIVADA:
        return jsonify({"mensaje": "Error de configuración en el servidor"}), 500

    data = request.get_json(force=True)
    wallet_usuario = str(data.get("wallet", "")).strip()

    if not wallet_usuario:
        return jsonify({"mensaje": "Wallet de destino necesaria"}), 400

    monto_regalo = 10.0 

    # 1. Verificar saldo de la Master
    saldo_master = saldo_wallet(MASTER_PUBLICA)
    if saldo_master < monto_regalo:
        return jsonify({"mensaje": "Sin fondos de regalo por ahora"}), 400

    # 2. Crear el bloque con la autorización de la llave del entorno
    ultimo = collection.find_one(sort=[("indice", -1)])
    
    nuevo_bloque = {
        "indice": ultimo["indice"] + 1,
        "timestamp": time.time(),
        "transacciones": [{
            "emisor": MASTER_PUBLICA,
            "receptor": wallet_usuario,
            "monto": monto_regalo,
            # Usamos la llave que jalamos de os.environ
            "autorizacion": hashlib.sha256(MASTER_PRIVADA.encode()).hexdigest()
        }],
        "nonce": "GIVEAWAY_ENV",
        "hash_anterior": ultimo["hash"]
    }
    
    nuevo_bloque["hash"] = calcular_hash(nuevo_bloque)

    try:
        collection.insert_one(nuevo_bloque)
        return jsonify({
            "ok": True, 
            "monto": monto_regalo, 
            "tx_hash": nuevo_bloque["hash"][:16]
        })
    except Exception as e:
        return jsonify({"mensaje": "Error al insertar en la red"}), 500

# =========================
# STATUS
# =========================
@app.route("/api/status")
def status():
    return jsonify({
        "success": True,
        "app": "CharlyCoin Flask",
        "blockchain_connected": w3.is_connected(),
        "network": "World Chain Mainnet"
    })

# =========================
# RUN
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # Importante: debug=False cuando lo subas para que te lo aprueben
    app.run(host="0.0.0.0", port=port, debug=False)
