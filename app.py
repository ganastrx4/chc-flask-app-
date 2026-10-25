from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Permite conexiones cruzadas desde tu frontend


# 1. Ruta de verificación de estado (Health Check)
@app.route("/", methods=["GET"])
@app.route("/health", methods=["GET"])
def health():
  return jsonify(
      {"status": "online", "message": "Nodo CharlyCoin funcionando al 100%"}
  )


# 2. Ruta para recibir los bloques minados
@app.route("/minar", methods=["POST"])
def minar_bloque():
  try:
    datos = request.json
    wallet = datos.get("wallet")
    nonce = datos.get("nonce")

    print(f"[NODO] Bloque recibido de wallet: {wallet} con nonce: {nonce}")

    # Aquí puedes agregar tu lógica para sumar el bloque a la blockchain
    return jsonify({
        "status": "success",
        "mensaje": "Bloque aceptado y registrado en el nodo",
        "wallet": wallet,
        "nonce": nonce,
    }), 200
  except Exception as e:
    return jsonify({"error": str(e)}), 400


# 3. Ruta para procesar las transferencias seguras con firma
@app.route("/transferir", methods=["POST"])
def transferir():
  try:
    datos = request.json
    emisor = datos.get("emisor")
    receptor = datos.get("receptor")
    monto = datos.get("monto")
    firma = datos.get("firma")

    print(f"[NODO] Transacción recibida: {monto} CHC de {emisor} a {receptor}")

    # Aquí validas la firma criptográfica o procesas el saldo
    return jsonify({
        "status": "success",
        "mensaje": "Transferencia validada y procesada correctamente",
        "monto": monto,
    }), 200
  except Exception as e:
    return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000)
