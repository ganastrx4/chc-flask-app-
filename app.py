from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from web3 import Web3
from eth_account.messages import encode_defunct

app = Flask(__name__)
CORS(app)

w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_files(path):
    return send_from_directory('.', path)

@app.route('/api/validar_billetera', methods=['POST'])
def validar():
    data = request.json

    address = data.get('address')
    firma = data.get('firma')
    mensaje = data.get('mensaje')

    if not address or not firma or not mensaje:
        return jsonify({"success": False, "error": "Datos incompletos"}), 400

    try:
        # 🔥 NORMALIZAR MENSAJE (clave para Reown)
        mensaje = str(mensaje)

        msj_eth = encode_defunct(text=mensaje)
        recovered_addr = w3.eth.account.recover_message(msj_eth, signature=firma)

        # 🔥 COMPARACIÓN SEGURA
        if recovered_addr.lower() == address.lower():
            print(f"✅ Usuario verificado: {address}")

            return jsonify({
                "success": True,
                "address": address
            }), 200

        else:
            print(f"⚠️ Dirección no coincide: {recovered_addr} vs {address}")
            return jsonify({"success": False}), 401

    except Exception as e:
        print(f"❌ Error validando firma: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


import os

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
