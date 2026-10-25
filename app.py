from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route("/health", methods=["GET"])
def health():
  return jsonify(
      {"status": "online", "message": "Nodo CharlyCoin funcionando correctamente"}
  )


@app.route("/minar", methods=["POST"])
def minar_bloque():
  datos = request.json
  # Aquí procesas el bloque que envía el minero
  return jsonify({"status": "success", "mensaje": "Bloque aceptado por el nodo"})


@app.route("/transferir", methods=["POST"])
def transferir():
  datos = request.json
  # Aquí procesas la transferencia
  return jsonify(
      {"status": "success", "mensaje": "Transacción registrada en la blockchain"}
  )


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000)
