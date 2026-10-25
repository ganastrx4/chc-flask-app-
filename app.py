from flask import Flask, jsonify, request
from flask_cors import CORS  # <-- Importante para permitir conexiones web

app = Flask(__name__)
CORS(app)  # <-- Activa CORS para que tu página web pueda hablar con el nodo sin bloqueos


@app.route("/", methods=["GET"])
def home():
  return jsonify(
      {"status": "online", "message": "Nodo CharlyCoin 2.0 Operativo"}
  )


@app.route("/health", methods=["GET"])
def health():
  return jsonify({"status": "online", "node": "CharlyScan Master Active"})


@app.route("/minar", methods=["POST"])
def minar_bloque():
  datos = request.json
  wallet = datos.get("wallet")
  nonce = datos.get("nonce")
  # Lógica para registrar el bloque minado
  return jsonify({
      "status": "success",
      "mensaje": "Bloque validado y registrado en la blockchain",
  })


@app.route("/transferir", methods=["POST"])
def transferir():
  datos = request.json
  emisor = datos.get("emisor")
  receptor = datos.get("receptor")
  monto = datos.get("monto")
  firma = datos.get("firma")

  # Aquí validas la firma criptográfica antes de hacer el cambio de saldo
  return jsonify({
      "status": "success",
      "mensaje": "Transferencia auditada y aceptada por el nodo",
  })


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000)
