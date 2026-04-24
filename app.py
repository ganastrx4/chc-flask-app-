import os
from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)

# =========================
# CONFIGURACION
# =========================
APP_ID = "app_7686f9027d3e3c0b53d987a3caf1e111"
ACTION = "login"
VERIFY_URL = "https://developer.worldcoin.org/api/v2/verify"

DB_FILE = "nullifiers.txt"


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
# PAGINAS
# =========================
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/buscador2.html")
def buscador2():
    return render_template("buscador2.html")


@app.route("/enviarwld.html")
def enviarwld():
    return render_template("enviarwld.html")


@app.route("/exchange.html")
def exchange():
    return render_template("exchange.html")


@app.route("/graficachcwld.html")
def graficachcwld():
    return render_template("graficachcwld.html")


@app.route("/charlycoinapp.html")
def charlycoinapp():
    return render_template("charlycoinapp.html")


@app.route("/chcoin.html")
def chcoin():
    return render_template("chcoin.html")


@app.route("/faucets.html")
def faucets():
    return render_template("faucets.html")


@app.route("/chun.html")
def chun():
    return render_template("chun.html")


@app.route("/next_page.html")
def next_page():
    return render_template("next_page.html")


@app.route("/index.html")
def index():
    return render_template("index.html")


@app.route("/ganarchun.html")
def ganarchun():
    return render_template("ganarchun.html")


@app.route("/glosario.html")
def glosario():
    return render_template("glosario.html")


@app.route("/wdd.html")
def wdd():
    return render_template("wdd.html")


# =========================
# WORLD ID VERIFY
# =========================
@app.route("/api/verify-proof", methods=["POST"])
def verify_proof():
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "error": "No data"
            }), 400

        # detectar nullifier
        proof_data = data.get("proof", {})

        nullifier = (
            data.get("nullifier_hash")
            or data.get("nullifier")
            or proof_data.get("nullifier_hash")
        )

        if not nullifier:
            return jsonify({
                "success": False,
                "error": "No nullifier"
            }), 400

        # evitar duplicados
        used = load_nullifiers()

        if str(nullifier) in used:
            return jsonify({
                "success": False,
                "error": "Usuario ya verificado"
            }), 400

        # payload correcto
        payload = {
            "app_id": APP_ID,
            "action": ACTION,
            "proof": data.get("proof"),
            "merkle_root": data.get("merkle_root"),
            "nullifier_hash": nullifier,
            "credential_type": data.get("credential_type", "orb"),
            "signal": data.get("signal", "")
        }

        # request oficial
        r = requests.post(
            VERIFY_URL,
            json=payload,
            timeout=20
        )

        result = r.json()

        print("WORLD RESPONSE:", result)

        if r.status_code == 200 and result.get("success") is True:
            save_nullifier(nullifier)

            return jsonify({
                "success": True,
                "message": "Verificado"
            })

        return jsonify({
            "success": False,
            "error": result
        }), 400

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# =========================
# STATUS
# =========================
@app.route("/api/status")
def status():
    return jsonify({
        "success": True,
        "app": "CHC Flask",
        "world_id": True
    })


# =========================
# RUN
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
