from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# Reemplaza con tus datos del Developer Portal
APP_ID = "app_ad065b6571dd4628b88a124ff444e14a"
ACTION_ID = "login"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/verify-worldid', methods=['POST'])
def verify_worldid():
    data = request.json
    
    # Esta es la llamada al backend de Worldcoin
    verify_res = requests.post(
        f"https://developer.worldcoin.org/api/v1/verify/{APP_ID}",
        json={
            "condition": "uniqueness-plus", # O el nivel que hayas elegido
            "action": ACTION_ID,
            "signal": data.get("signal", ""),
            "merkle_root": data.get("merkle_root"),
            "nullifier_hash": data.get("nullifier_hash"),
            "proof": data.get("proof"),
            "verification_level": data.get("verification_level")
        }
    )
    
    if verify_res.status_code == 200:
        return jsonify({"success": True}), 200
    else:
        return jsonify({"success": False, "detail": verify_res.json()}), 400

if __name__ == '__main__':
    app.run(debug=True)
