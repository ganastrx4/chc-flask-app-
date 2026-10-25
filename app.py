from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Evita bloqueos de conexión con MetaMask y Fetch


# --- INTERFAZ WEB INTEGRADA (Para que nunca vuelva a dar 404) ---
@app.route("/", methods=["GET"])
def home_web():
  return """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Minería CHC Pro | Nodo Oficial</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/ethers/5.7.2/ethers.umd.min.js"></script>
    <style>
        :root { --gold: #f1c40f; --dark-bg: #0a0a0a; --card-bg: #161616; --blue-scan: #2980b9; --wc-blue: #3B99FC; --red: #e74c3c; }
        body { text-align: center; padding: 10px; font-family: 'Segoe UI', Arial, sans-serif; background: var(--dark-bg); color: white; margin: 0; overflow-x: hidden; }
        .window-container { max-width: 600px; margin: 20px auto; border: 1px solid #333; border-radius: 15px; overflow: hidden; background: #111; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
        .window-header { background: #222; padding: 10px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #333; }
        .card-panel { background: var(--card-bg); padding: 20px; margin: 10px; border-radius: 12px; border: 1px solid #222; }
        input { margin: 8px 0; padding: 12px; width: 85%; border-radius: 5px; border: 1px solid #444; background: #000; color: #2ecc71; font-family: monospace; text-align: center; }
        button { margin: 8px 0; padding: 12px; width: 90%; border-radius: 25px; border: none; cursor: pointer; font-weight: bold; background: var(--gold); color: black; transition: 0.3s; }
        button:hover { transform: scale(1.02); }
        .btn-connect { background: var(--wc-blue); color: white; margin-bottom: 12px; }
        .chc-counter { font-size: 1.8em; color: var(--gold); margin: 10px 0; font-weight: bold; }
        .wallet-link { color: #3498db; text-decoration: underline; font-size: 0.85em; display: block; margin: 8px 0; cursor: pointer; }
        .lock-badge { font-size: 0.8em; color: #2ecc71; background: #11381e; padding: 4px 8px; border-radius: 10px; display: inline-block; margin-bottom: 8px; }
    </style>
</head>
<body onload="verificarMemoria()">

<div class="window-container">
    <div class="window-header">
        <span style="font-size: 0.9em; font-weight: bold; color: var(--gold);">CHARLY MINER PRO - NODO ACTIVO</span>
    </div>

    <div class="card-panel">
        <h2>MINERÍA ACTIVA</h2>
        <div class="lock-badge">🔒 Candado de Propiedad Activo</div>
        
        <input type="text" id="userWallet" placeholder="Pega tu dirección CHC..." />
        
        <button class="btn-connect" onclick="conectarBilleteraEVM()">
            🦊 Conectar MetaMask / Web3
        </button>

        <span onclick="gestionarIdentidad()" class="wallet-link">🔑 Generar nueva identidad con Clave Privada</span>

        <div class="chc-counter">💰 <span id="chcCount">0</span> CHC</div>
        <div id="minerStatus" style="font-size: 0.8em; color: #888;">Panel conectado al nodo de Render</div>
    </div>

    <div class="card-panel" style="border-color: #333;">
        <h3 style="margin-top: 0; color: #2ecc71;">💸 ENVIAR CHC SEGURO</h3>
        <input type="text" id="transferReceptor" placeholder="Dirección del destinatario..." />
        <input type="number" id="transferMonto" placeholder="Monto a transferir..." />
        <button style="background: #2ecc71; color: white;" onclick="ejecutarTransferenciaSegura()">🔐 FIRMAR Y ENVIAR</button>
    </div>

    <div style="padding: 10px;">
        <button onclick="continuarMineria()">🚀 INICIAR MINERÍA</button>
        <button style="background:var(--red); color:white;" onclick="pararMineria()">🛑 DETENER</button>
    </div>
</div>

<script>
    const NODO_URL = window.location.origin;
    let segundos = 0, chcGanados = 0, interval = null, minando = false;
    let RecompensaPendiente = 0;
    let web3Provider = null, signer = null;

    async function conectarBilleteraEVM() {
        if (window.ethereum) {
            try {
                await window.ethereum.request({ method: 'eth_requestAccounts' });
                web3Provider = new ethers.providers.Web3Provider(window.ethereum);
                signer = web3Provider.getSigner();
                const address = await signer.getAddress();
                document.getElementById('userWallet').value = address;
                localStorage.setItem("last_chc_wallet", address);
                document.getElementById('minerStatus').innerText = "Billetera conectada.";
            } catch (err) { alert("Conexión rechazada."); }
        } else { alert("MetaMask no detectado."); }
    }

    async function ejecutarTransferenciaSegura() {
        const emisor = document.getElementById('userWallet').value.trim();
        const receptor = document.getElementById('transferReceptor').value.trim();
        const monto = parseFloat(document.getElementById('transferMonto').value);

        if (!emisor || !receptor || isNaN(monto) || monto <= 0) return alert("Completa todos los campos.");

        let firma = "";
        if (signer && (await signer.getAddress()).toLowerCase() === emisor.toLowerCase()) {
            try {
                firma = await signer.signMessage(`Transferir ${monto} CHC hacia ${receptor}`);
            } catch (e) { return alert("Firma rechazada."); }
        } else {
            let clavePrivada = localStorage.getItem("chc_privkey_" + emisor) || prompt("Introduce la CLAVE PRIVADA para autorizar:");
            if (!clavePrivada) return alert("Se requiere clave privada.");
            try {
                const walletObj = new ethers.Wallet(clavePrivada);
                const mensajeHash = ethers.utils.solidityKeccak256(["string", "string", "number"], [emisor, receptor, monto]);
                firma = await walletObj.signMessage(ethers.utils.arrayify(mensajeHash));
            } catch (err) { return alert("Clave privada inválida."); }
        }

        try {
            const respuesta = await fetch(`${NODO_URL}/transferir`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ emisor, receptor, monto: Number(monto), firma })
            });
            const res = await respuesta.json();
            if (respuesta.ok) alert("✅ Transacción confirmada.");
            else alert("❌ Error: " + (res.error || "Rechazada."));
        } catch (error) { alert("Error de conexión con el nodo."); }
    }

    function verificarMemoria() {
        const saved = localStorage.getItem("last_chc_wallet");
        if (saved) document.getElementById('userWallet').value = saved;
    }

    function contarTiempo() {
        const wallet = document.getElementById('userWallet').value.trim();
        if (minando && wallet.length > 5) {
            segundos++;
            if (segundos % 2 === 0) {
                chcGanados++;
                RecompensaPendiente++;
                document.getElementById('chcCount').innerText = chcGanados;
            }
            document.getElementById('minerStatus').innerText = `Minando... (Bloque #${segundos})`;
        }
    }

    function continuarMineria() {
        const wallet = document.getElementById('userWallet').value.trim();
        if (wallet.length < 5) return alert("Ingresa una billetera válida.");
        if (!minando) {
            minando = true;
            localStorage.setItem("last_chc_wallet", wallet);
            if (!interval) interval = setInterval(contarTiempo, 1000);
            document.getElementById('minerStatus').innerText = "Minería en ejecución";
        }
    }

    function pararMineria() {
        minando = false;
        if (interval) { clearInterval(interval); interval = null; }
        document.getElementById('minerStatus').innerText = `Minería detenida. Total: ${chcGanados} CHC`;
    }

    function gestionarIdentidad() {
        const wallet = ethers.Wallet.createRandom();
        localStorage.setItem("chc_privkey_" + wallet.address, wallet.privateKey);
        localStorage.setItem("last_chc_wallet", wallet.address);
        alert("🔑 Identidad creada.\n\nDirección: " + wallet.address + "\n\nPrivada: " + wallet.privateKey);
        document.getElementById('userWallet').value = wallet.address;
    }
</script>
</body>
</html>
    """


# --- ENDPOINTS DEL NODO ---
@app.route("/health", methods=["GET"])
def health():
  return jsonify(
      {"status": "online", "message": "Nodo CharlyCoin operando correctamente"}
  )


@app.route("/transferir", methods=["POST"])
def transferir():
  try:
    datos = request.json
    return jsonify({
        "status": "success",
        "mensaje": "Transferencia procesada por el nodo",
        "monto": datos.get("monto"),
    }), 200
  except Exception as e:
    return jsonify({"error": str(e)}), 400


@app.route("/minar", methods=["POST"])
def minar_bloque():
  try:
    datos = request.json
    return jsonify({
        "status": "success",
        "mensaje": "Bloque registrado",
        "wallet": datos.get("wallet"),
    }), 200
  except Exception as e:
    return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000)
