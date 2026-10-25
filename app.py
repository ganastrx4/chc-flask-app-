from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Ruta principal (Home / Minería)
@app.route('/')
def home():
    # Renderiza el archivo HTML principal que tengas en la carpeta 'templates'
    return render_template('index.html') 

# Ruta específica para ganarchun.html
@app.route('/ganarchun.html')
def ganar_chun():
    return render_template('ganarchun.html')

# Ruta genérica para cualquier otra página HTML que tengas en templates
@app.route('/<path:nombre_pagina>')
def cargar_pagina(nombre_pagina):
    try:
        return render_template(nombre_pagina)
    except Exception:
        return "Página no encontrada en el nodo CHC", 404

# Endpoints de la API del nodo (para minería y transferencias)
@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "online", "message": "Nodo CharlyCoin funcionando"})

@app.route('/minar', methods=['POST'])
def minar_bloque():
    datos = request.json
    return jsonify({"status": "success", "mensaje": "Bloque registrado"})

@app.route('/transferir', methods=['POST'])
def transferir():
    datos = request.json
    return jsonify({"status": "success", "mensaje": "Transferencia procesada"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
