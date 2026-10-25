from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Permite que tu interfaz web se conecte sin bloqueos


@app.route("/", methods=["GET"])
@app.route("/health", methods=["GET"])
def health():
  return jsonify(
      {"status": "online", "message": "Nodo CharlyCoin funcionando correctamente"}
  )


@app.route("/minar", methods=["POST"])
def minar_bloque():
  datos = request.json
  return jsonify({
      "status": "success",
      "mensaje": "Bloque aceptado por el nodo",
      "wallet": datos.get("wallet"),
      "nonce": datos.get("nonce"),
  })


@app.route("/transferir", methods=["POST"])
def transferir():
  datos = request.json
  return jsonify({
      "status": "success",
      "mensaje": "Transferencia validada con éxito",
      "monto": datos.get("monto"),
  })


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000)
