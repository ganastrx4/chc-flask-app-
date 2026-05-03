<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Casino CharlyScan - World ID</title>
    
    <!-- SDK OFICIAL DE WORLD ID -->
    <script src="https://unpkg.com/@worldcoin/idkit-standalone@1.1.0/dist/index.global.js"></script>

    <style>
        :root { --gold: #f1c40f; --iron: #bdc3c7; --bg: #0a0a0a; --green: #2ecc71; --red: #e74c3c; }
        body { background: var(--bg); color: white; font-family: 'Segoe UI', sans-serif; text-align: center; padding: 10px; }
        
        .coin-container { perspective: 1000px; width: 150px; height: 150px; margin: 20px auto; }
        #coin { width: 100%; height: 100%; position: relative; transform-style: preserve-3d; }
        .spinning { transition: transform 4s cubic-bezier(0.1, 0.5, 0.1, 1); }
        .side { 
            position: absolute; width: 100%; height: 100%; border-radius: 50%; 
            backface-visibility: hidden; display: flex; align-items: center; 
            justify-content: center; font-weight: bold; border: 4px solid var(--gold);
            box-shadow: 0 0 15px rgba(241, 196, 15, 0.3);
        }
        .cara { background: linear-gradient(135deg, var(--gold), #d4af37); color: black; }
        .aguila { background: linear-gradient(135deg, #333, #000); color: var(--gold); transform: rotateY(180deg); }

        .bet-panel { background: #1a1a1a; padding: 20px; border-radius: 15px; max-width: 400px; margin: 0 auto; border: 1px solid #333; }
        .wallet-input { width: 90%; padding: 10px; border-radius: 5px; border: 1px solid #444; background: #000; color: var(--green); font-family: monospace; font-size: 11px; margin-bottom: 15px; }
        input[type="number"] { padding: 10px; background: #000; color: white; border: 1px solid var(--gold); border-radius: 5px; width: 60px; }
        
        .btn { padding: 12px 20px; border-radius: 25px; border: none; cursor: pointer; font-weight: bold; margin: 5px; transition: 0.3s; }
        .btn-play { background: var(--gold); color: black; width: 100%; font-size: 1.1em; }
        .btn-play:disabled { background: #555; cursor: not-allowed; }
        .btn-world { background: white; color: black; width: 100%; margin-top: 15px; display: flex; align-items: center; justify-content: center; gap: 10px; }
        .btn-home { background: transparent; color: #888; text-decoration: none; font-size: 0.9em; }

        #status { margin-top: 15px; min-height: 40px; font-weight: bold; }
        #streakInfo { color: var(--iron); font-size: 0.8em; margin-top: 10px; }
        #verifyStatus { color: var(--green); font-size: 0.8em; margin-top: 5px; display: none; }
    </style>
</head>
<body>

    <a href="/" class="btn-home">🏠 VOLVER AL INICIO</a>
    <h2>CASINO CHARLYSCAN</h2>
    
    <div class="coin-container">
        <div id="coin">
            <div class="side cara">CHC<br>CARA</div>
            <div class="side aguila">CASA<br>ÁGUILA</div>
        </div>
    </div>

    <div class="bet-panel">
        <!-- BOTÓN DE WORLD ID (RESTAURADO) -->
        <button id="world-id-button" class="btn btn-world">
            <img src="https://worldcoin.org/icons/logo-dark.svg" width="20"> Verificar con World ID
        </button>
        <div id="verifyStatus">✅ Usuario Verificado (Orb)</div>

        <hr style="border: 0.5px solid #333; margin: 20px 0;">

        <input type="text" id="userWallet" class="wallet-input" placeholder="Dirección de minero CHC..." />
        
        <div style="margin-bottom: 15px;">
            <span>Apuesta: </span>
            <input type="number" id="betAmount" value="1" min="1" max="10" />
            <span style="color: var(--gold)">CHC</span>
        </div>

        <button id="playBtn" class="btn btn-play" onclick="procesarApuesta()" disabled>VERIFÍCATE PARA JUGAR</button>
        
        <div id="status">Debes verificar tu World ID primero</div>
        <div id="streakInfo">Racha de pérdidas: 0</div>
    </div>

<script>
    const MASTER_PUBLIC = "93aab2b2ee274042d81954cd6569085ac3f1f660d600e6c7ca3aa11adbf94e62544ff783541316f3c7269d751079414e879f18804dde24c1b83c70c4e13cd4ee";
    const NODO_URL = "https://binance-bot-hna7.onrender.com";
    const AUTH_KEY = "e52bcda04bcebb7dfebf42b2ddcfac46";

    let perdidasConsecutivas = 0;
    let maxApuesta = 10;
    let verificado = false;

    // --- CONFIGURACIÓN DE IDKIT (WORLD ID) ---
    IDKit.init({
        app_id: "app_7686f9027d3e3c0b53d987a3caf1e111", // Tu App ID
        action: "login",
        onSuccess: (result) => {
            verificado = true;
            document.getElementById('world-id-button').style.display = 'none';
            document.getElementById('verifyStatus').style.display = 'block';
            document.getElementById('playBtn').disabled = false;
            document.getElementById('playBtn').innerText = "APOSTAR Y LANZAR";
            document.getElementById('status').innerText = "¡Listo! Haz tu apuesta.";
            console.log("World ID verificado correctamente");
        },
        onError: (error) => console.error("Error World ID:", error)
    });

    document.getElementById('world-id-button').onclick = () => {
        IDKit.open();
    };

    async function procesarApuesta() {
        if(!verificado) return alert("Por favor, verifícate con World App.");
        
        const wallet = document.getElementById('userWallet').value.trim();
        const betInput = document.getElementById('betAmount');
        const apuesta = parseFloat(betInput.value);
        const status = document.getElementById('status');
        const coin = document.getElementById('coin');
        const playBtn = document.getElementById('playBtn');

        if (wallet.length < 10) return alert("Ingresa tu dirección de minero.");
        if (apuesta > maxApuesta) return alert(`Límite actual: ${maxApuesta} CHC`);

        playBtn.disabled = true;
        coin.classList.remove('spinning');
        coin.style.transform = `rotateY(0deg)`;
        await new Promise(r => setTimeout(r, 50));
        
        const ganaUsuario = Math.random() > 0.60;
        const totalRotation = 3600 + (ganaUsuario ? 0 : 180);
        
        coin.classList.add('spinning');
        coin.style.transform = `rotateY(${totalRotation}deg)`;
        status.innerText = "¡Lanzando moneda!";

        setTimeout(async () => {
            if (ganaUsuario) {
                perdidasConsecutivas = 0;
                maxApuesta = 10;
                status.innerHTML = `<span style="color:var(--green)">GANASTE +${apuesta} CHC</span>`;
                await enviarTokens(MASTER_PUBLIC, wallet, apuesta);
            } else {
                perdidasConsecutivas++;
                status.innerHTML = `<span style="color:var(--red)">PERDISTE -${apuesta} CHC</span>`;
                
                if(perdidasConsecutivas >= 5) {
                    maxApuesta = 300;
                    status.innerHTML += "<br><small>¡Modo Martingala nivel 5!</small>";
                } else if (perdidasConsecutivas >= 1) {
                    maxApuesta = 20;
                }
                betInput.max = maxApuesta;
            }
            document.getElementById('streakInfo').innerText = `Racha de pérdidas: ${perdidasConsecutivas}`;
            playBtn.disabled = false;
        }, 4000);
    }

    async function enviarTokens(emisor, receptor, monto) {
        try {
            await fetch(`${NODO_URL}/transferir`, {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'Authorization': AUTH_KEY 
                },
                body: JSON.stringify({
                    emisor: emisor,
                    receptor: receptor,
                    monto: monto,
                    firma: "CASINO_WORLD_ID_VERIFIED"
                })
            });
        } catch (e) { console.log("Error de red"); }
    }
</script>
</body>
</html>
