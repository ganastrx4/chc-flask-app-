from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# --- CONFIGURACIÓN ---
# Asegúrate de que este ID sea el de la app que dejaste activa en el portal
APP_ID = "app_ad065b6571dd4628b88a124ff444e14a"
ACTION_ID = "login"

@app.route('/')
def index():
    # Esto busca el archivo index.html dentro de la carpeta /templates
    return render_template('index.html')

# --- ESTO ES LO QUE VA "DENTRO" DE LA RUTA /api/verify-worldid ---
@app.route('/api/verify-worldid', methods=['POST'])
def verify_worldid():
    try:
        data = request.json
        
        # 1. Armamos el paquete para enviarlo a Worldcoin
        verification_payload = {
            "nullifier_hash": data.get("nullifier_hash"),
            "merkle_root": data.get("merkle_root"),
            "proof": data.get("proof"),
            "verification_level": data.get("verification_level"),
            "action": ACTION_ID,
            "signal": data.get("signal", "")
        }

        # 2. Hacemos la petición al API oficial de Worldcoin
        response = requests.post(
            f"https://developer.worldcoin.org/api/v1/verify/{APP_ID}",
            json=verification_payload,
            headers={"Content-Type": "application/json"}
        )

        # 3. Si Worldcoin dice que es OK (status 200)
        if response.status_code == 200:
            return jsonify({"success": True}), 200
        else:
            # Si falla, devolvemos el error que nos dio Worldcoin
            return jsonify({"success": False, "detail": response.json()}), response.status_code

    except Exception as e:
        return jsonify({"success": False, "detail": str(e)}), 500

@app.route('/api/validar_billetera', methods=['POST'])
def validar_billetera():
    # Esta ruta maneja el paso final de la wallet
    return jsonify({"success": True}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
