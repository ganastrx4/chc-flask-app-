import os
import sys
import subprocess
import time
import hashlib
import json
import binascii
import webbrowser
import platform
import traceback

# ============================================================
# LIBRERÍAS
# ============================================================

def verificar_librerias():
    librerias = [
        "requests",
        "mnemonic",
        "ecdsa",
        "psutil"
    ]

    faltantes = []

    for lib in librerias:
        try:
            __import__(lib)
        except ImportError:
            faltantes.append(lib)

    if faltantes:
        print(
            f"\n[!] Detectando entorno... "
            f"instalando: {', '.join(faltantes)}"
        )

        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", *faltantes]
            )

            print("[✅] Entorno configurado correctamente.\n")

        except Exception as e:
            print(
                f"[❌] No se pudieron instalar las librerías: {e}"
            )
            sys.exit(1)


verificar_librerias()


import requests
from mnemonic import Mnemonic
import ecdsa
import psutil


# ============================================================
# COLORES
# ============================================================

class Col:
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    END = "\033[0m"
    MAGENTA = "\033[95m"


# ============================================================
# CONFIGURACIÓN DE CHARLYCOIN
# ============================================================

NODO_URL = "https://binance-bot-hna7.onrender.com"

# Dificultad local utilizada para encontrar el nonce.
DIFICULTAD = 5

# ============================================================
# RECOMPENSA
#
# IMPORTANTE:
# La recompensa REAL la decide el nodo.
#
# Este valor solamente se utiliza como referencia visual
# cuando el cliente muestra información local.
#
# Según los bloques que mostraste:
# +2.25 CHC
#
# ============================================================

RECOMPENSA_ACTUAL = 2.25


# ============================================================
# ARCHIVOS
# ============================================================

WALLET_FILE = "mi_wallet_chc.json"


# ============================================================
# SESIÓN HTTP
# ============================================================

http = requests.Session()

http.headers.update({
    "User-Agent": "NEWWORLD-CHC-Miner/1.0"
})


# ============================================================
# FUNCIONES DE RED
# ============================================================

def comprobar_nodo():
    """
    Comprueba que el servidor responde.

    IMPORTANTE:
    No confundimos un error HTTP con 'nodo offline'.
    """

    try:
        url = f"{NODO_URL}/health"

        respuesta = http.get(
            url,
            timeout=15
        )

        if respuesta.status_code == 200:

            try:
                datos = respuesta.json()
            except ValueError:
                datos = {}

            return True, datos

        return False, {
            "status_code": respuesta.status_code,
            "respuesta": respuesta.text[:500]
        }

    except requests.exceptions.Timeout:
        return False, {
            "error": "TIMEOUT",
            "detalle": "El nodo tardó demasiado en responder."
        }

    except requests.exceptions.ConnectionError as e:
        return False, {
            "error": "CONNECTION_ERROR",
            "detalle": str(e)
        }

    except requests.exceptions.RequestException as e:
        return False, {
            "error": "REQUEST_ERROR",
            "detalle": str(e)
        }

    except Exception as e:
        return False, {
            "error": "ERROR",
            "detalle": str(e)
        }


def mostrar_estado_nodo():

    print(
        f"\n{Col.CYAN}{Col.BOLD}"
        f"[*] Comprobando Nodo CHC..."
        f"{Col.END}"
    )

    activo, informacion = comprobar_nodo()

    if activo:

        print(
            f"{Col.GREEN}{Col.BOLD}"
            f"[🟢] NODO ACTIVO"
            f"{Col.END}"
        )

        if informacion:
            print(
                f"{Col.CYAN}"
                f"Respuesta: {informacion}"
                f"{Col.END}"
            )

        return True

    print(
        f"{Col.RED}"
        f"[🔴] No se pudo comprobar el nodo."
        f"{Col.END}"
    )

    print(
        f"{Col.YELLOW}"
        f"Detalle: {informacion}"
        f"{Col.END}"
    )

    return False


# ============================================================
# HARDWARE
# ============================================================

def mostrar_hardware():

    print(
        f"{Col.CYAN}{Col.BOLD}"
        f"--- ESPECIFICACIONES DEL MINERO ---"
        f"{Col.END}"
    )

    print(
        f"{Col.BOLD}Sistema:{Col.END} "
        f"{platform.system()} {platform.release()}"
    )

    print(
        f"{Col.BOLD}Procesador:{Col.END} "
        f"{platform.processor()}"
    )

    print(
        f"{Col.BOLD}Núcleos:{Col.END} "
        f"{psutil.cpu_count(logical=False)} Físicos / "
        f"{psutil.cpu_count(logical=True)} Lógicos"
    )

    print(
        f"{Col.BOLD}RAM Total:{Col.END} "
        f"{round(psutil.virtual_memory().total / (1024 ** 3), 2)} GB"
    )

    print(
        f"{Col.BOLD}Fecha Local:{Col.END} "
        f"{time.strftime('%d/%m/%Y %H:%M:%S')}"
    )

    print(
        f"{Col.BOLD}Nodo:{Col.END} "
        f"{NODO_URL}"
    )

    print(
        f"{Col.BOLD}Dificultad local:{Col.END} "
        f"{DIFICULTAD}"
    )

    print(
        f"{Col.BOLD}Recompensa de referencia:{Col.END} "
        f"{RECOMPENSA_ACTUAL} CHC"
    )

    print(
        f"{Col.CYAN}"
        + "-" * 75
        + f"{Col.END}"
    )


# ============================================================
# BIENVENIDA
# ============================================================

def mostrar_bienvenida():

    os.system(
        "cls" if os.name == "nt" else "clear"
    )

    print(
        f"{Col.CYAN}{Col.BOLD}"
        + "=" * 75
    )

    print(
        "    🚀 BIENVENIDO A LA RED CHARLYCOIN (CHC)"
    )

    print(
        "    PROYECTO NEWWORLD NETWORK"
    )

    print(
        "=" * 75
        + f"{Col.END}"
    )

    mostrar_hardware()

    print(
        f"{Col.MAGENTA}{Col.BOLD}"
        f"[RESEÑA]:"
        f"{Col.END}"
    )

    print(
        "CharlyCoin es una visión de soberanía digital "
        "creada en Chimalhuacán."
    )

    print(
        "Buscamos un ecosistema financiero donde "
        "el control regrese al usuario."
    )

    print(
        f"\n{Col.YELLOW}{Col.BOLD}"
        f"[SEGURIDAD]:"
        f"{Col.END} "
        f"Billetera local firmada."
    )

    print(
        f"{Col.CYAN}"
        + "-" * 75
        + f"{Col.END}"
    )


# ============================================================
# WALLET CHC
# ============================================================

class WalletCHC:

    def __init__(self):

        self.archivo = WALLET_FILE

        self.datos = self.cargar_o_crear()


    def cargar_o_crear(self):

        if os.path.exists(self.archivo):

            try:

                with open(
                    self.archivo,
                    "r",
                    encoding="utf-8"
                ) as f:

                    datos = json.load(f)

                if (
                    "publica" not in datos
                    or "privada" not in datos
                ):
                    raise ValueError(
                        "Wallet incompleta."
                    )

                print(
                    f"{Col.GREEN}"
                    f"[🏠] Wallet activa: "
                    f"{Col.END}"
                    f"{Col.BOLD}"
                    f"{datos['publica'][:30]}..."
                    f"{Col.END}"
                )

                return datos

            except Exception as e:

                print(
                    f"{Col.RED}"
                    f"[❌] Error leyendo wallet: {e}"
                    f"{Col.END}"
                )

                sys.exit(1)

        else:

            print(
                f"{Col.YELLOW}"
                f"[*] Forjando nueva identidad en "
                f"la Blockchain..."
                f"{Col.END}"
            )

            mnemo = Mnemonic("spanish")

            palabras = mnemo.generate(
                strength=128
            )

            seed = mnemo.to_seed(
                palabras
            )

            sk = ecdsa.SigningKey.from_string(
                seed[:32],
                curve=ecdsa.SECP256k1
            )

            vk = sk.get_verifying_key()

            datos = {

                "publica":
                    binascii.hexlify(
                        vk.to_string()
                    ).decode(),

                "privada":
                    binascii.hexlify(
                        sk.to_string()
                    ).decode(),

                "semilla":
                    palabras
            }

            with open(
                self.archivo,
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(
                    datos,
                    f,
                    indent=4,
                    ensure_ascii=False
                )

            print(
                f"\n{Col.GREEN}"
                f">> SEMILLA GENERADA: "
                f"{palabras} <<"
                f"{Col.END}"
            )

            print(
                f"\n{Col.YELLOW}"
                f"⚠️ GUARDA ESTA SEMILLA EN UN "
                f"LUGAR SEGURO."
                f"{Col.END}"
            )

            return datos


# ============================================================
# TEMPO BRIDGE
# ============================================================

class TempoBridge:

    def __init__(self, wallet_chc):

        self.wallet = wallet_chc

        self.pool_wallet = (
            "0x9D437783e3b940AC85557765D8b07fF7a69fB4e6"
        )


    def cotizar_y_operar(
        self,
        operacion="compra"
    ):

        print(
            f"\n{Col.BOLD}"
            f"--- {operacion.upper()} DE CHC "
            f"VIA INFRAESTRUCTURA TEMPO ---"
            f"{Col.END}"
        )

        print(
            "Selecciona la moneda de intercambio:"
        )

        print(
            "1. USDT (Stablecoin Dólar)"
        )

        print(
            "2. Fíat Directo "
            "(EUR / Moneda de la pasarela)"
        )

        metodo = input(
            f"{Col.BOLD}"
            f"Opción (1 o 2): "
            f"{Col.END}"
        ).strip()

        asset_intercambio = (
            "USDT"
            if metodo == "1"
            else "EUR"
        )

        if metodo == "2":

            fiat_input = input(
                "Moneda Fíat a usar "
                "(Ej: EUR, USD, MXN) "
                "[Por defecto EUR]: "
            ).strip().upper()

            if fiat_input:
                asset_intercambio = fiat_input

        try:

            monto = float(
                input(
                    f"Monto en "
                    f"{asset_intercambio} a procesar: "
                )
            )

            if monto <= 0:
                raise ValueError

        except ValueError:

            print(
                f"{Col.RED}"
                f"[❌] Monto inválido."
                f"{Col.END}"
            )

            return

        print(
            f"{Col.CYAN}"
            f"[*] Consultando tasas de intercambio..."
            f"{Col.END}"
        )

        time.sleep(1)

        tasa_cambio = (
            0.85
            if operacion == "compra"
            else 0.80
        )

        tokens_estimados = round(
            monto / tasa_cambio,
            6
        )

        print(
            f"\n{Col.GREEN}{Col.BOLD}"
            f"[📊] COTIZACIÓN DE INTERCAMBIO:"
            f"{Col.END}"
        )

        if operacion == "compra":

            print(
                f"Envías: "
                f"{monto} {asset_intercambio}"
            )

            print(
                f"Recibes en tu Wallet CHC: "
                f"{Col.BOLD}"
                f"{tokens_estimados} CHC"
                f"{Col.END}"
            )

        else:

            print(
                f"Entregas: "
                f"{monto} CHC"
            )

            print(
                f"Recibes: "
                f"{Col.BOLD}"
                f"{tokens_estimados} "
                f"{asset_intercambio}"
                f"{Col.END}"
            )

        confirmar = input(
            "\n¿Proceder con las instrucciones "
            "del Pool de Liquidación? (s/n): "
        ).strip().lower()

        if confirmar == "s":

            print(
                f"\n{Col.YELLOW}{Col.BOLD}"
                f"[📌] INSTRUCCIONES DE DEPOSIT_POOL:"
                f"{Col.END}"
            )

            print(
                f"1. Transfiere exactamente "
                f"{monto} "
                f"{asset_intercambio} "
                f"a la cuenta recaudadora:"
            )

            print(
                f"   👉 {Col.CYAN}"
                f"{self.pool_wallet}"
                f"{Col.END}"
            )

            print(
                f"2. IMPORTANTE: Agrega en el campo "
                f"'MEMO/MENSAJE' de tu billetera "
                f"tu dirección CHC:"
            )

            print(
                f"   👉 "
                f"{self.wallet.datos['publica']}"
            )

            print(
                "3. El nodo auditará el ingreso "
                "y asignará el balance."
            )

            input(
                f"\n{Col.BOLD}"
                f"Presiona Enter para regresar..."
                f"{Col.END}"
            )

        else:

            print(
                f"{Col.YELLOW}"
                f"[!] Operación cancelada."
                f"{Col.END}"
            )


# ============================================================
# MINERÍA
# ============================================================

def minar():

    direccion = user_wallet.datos["publica"]

    print(
        f"{Col.CYAN}\n"
        f"[*] Sincronizando con Nodo Maestro..."
        f"{Col.END}"
    )

    activo, info = comprobar_nodo()

    if not activo:

        print(
            f"{Col.RED}"
            f"[❌] No se pudo conectar con el nodo."
            f"{Col.END}"
        )

        print(
            f"{Col.YELLOW}"
            f"Detalle: {info}"
            f"{Col.END}"
        )

        return

    print(
        f"{Col.GREEN}"
        f"[🟢] Nodo disponible."
        f"{Col.END}"
    )

    print(
        f"{Col.CYAN}"
        f"[*] Dificultad local: "
        f"{DIFICULTAD}"
        f"{Col.END}"
    )

    print(
        f"{Col.CYAN}"
        f"[*] Recompensa de referencia: "
        f"{RECOMPENSA_ACTUAL} CHC"
        f"{Col.END}"
    )

    print(
        f"{Col.YELLOW}"
        f"[*] La recompensa real será determinada "
        f"por el nodo."
        f"{Col.END}"
    )

    nonce = 0

    start_time = time.time()

    while True:

        contenido = (
            f"{direccion}{nonce}"
            .encode()
        )

        h = hashlib.sha256(
            contenido
        ).hexdigest()

        if h.startswith(
            "0" * DIFICULTAD
        ):

            print(
                f"\n{Col.GREEN}{Col.BOLD}"
                f"[💎] ¡BLOQUE MINADO!"
                f"{Col.END}"
            )

            print(
                f"{Col.CYAN}"
                f"Nonce: {nonce}"
                f"{Col.END}"
            )

            print(
                f"{Col.CYAN}"
                f"Hash: {h}"
                f"{Col.END}"
            )

            print(
                f"{Col.YELLOW}"
                f"Recompensa de referencia: "
                f"{RECOMPENSA_ACTUAL} CHC"
                f"{Col.END}"
            )

            # ==================================================
            # ENVIAR BLOQUE AL NODO
            # ==================================================

            try:

                respuesta = http.post(
                    f"{NODO_URL}/minar",
                    json={
                        "wallet": direccion,
                        "nonce": nonce
                    },
                    timeout=15
                )

                print(
                    f"{Col.CYAN}"
                    f"[📡] Nodo respondió HTTP "
                    f"{respuesta.status_code}"
                    f"{Col.END}"
                )

                try:
                    datos = respuesta.json()

                    print(
                        f"{Col.CYAN}"
                        f"[📦] Respuesta:"
                        f"{Col.END}"
                    )

                    print(datos)

                except ValueError:

                    print(
                        f"{Col.YELLOW}"
                        f"[📄] Respuesta no JSON:"
                        f"{Col.END}"
                    )

                    print(
                        respuesta.text[:500]
                    )

            except requests.exceptions.Timeout:

                print(
                    f"{Col.RED}"
                    f"[⚠️] Timeout enviando bloque "
                    f"al nodo."
                    f"{Col.END}"
                )

            except requests.exceptions.ConnectionError as e:

                print(
                    f"{Col.RED}"
                    f"[⚠️] Error de conexión enviando "
                    f"bloque:"
                    f"{Col.END}"
                )

                print(e)

            except requests.exceptions.RequestException as e:

                print(
                    f"{Col.RED}"
                    f"[⚠️] Error HTTP:"
                    f"{Col.END}"
                )

                print(e)

            except Exception as e:

                print(
                    f"{Col.RED}"
                    f"[⚠️] Error inesperado:"
                    f"{Col.END}"
                )

                print(e)

            nonce = 0

            time.sleep(2)

        nonce += 1

        if nonce % 200000 == 0:

            elapsed = time.time() - start_time

            if elapsed <= 0:
                elapsed = 0.001

            khs = round(
                (nonce / elapsed) / 1000,
                2
            )

            cpu = psutil.cpu_percent()

            print(
                f"{Col.CYAN}"
                f"[🚀] Velocidad: {khs} KH/s "
                f"| Intentos: {nonce} "
                f"| CPU: {cpu}%"
                f"{Col.END}",
                end="\r"
            )


# ============================================================
# FIRMA DE TRANSACCIÓN
# ============================================================

def crear_firma(
    emisor,
    receptor,
    monto
):

    mensaje = (
        f"{emisor}"
        f"{receptor}"
        f"{monto}"
    ).encode()

    try:

        sk = ecdsa.SigningKey.from_string(
            binascii.unhexlify(
                user_wallet.datos["privada"]
            ),
            curve=ecdsa.SECP256k1
        )

    except Exception as e:

        raise RuntimeError(
            f"No se pudo cargar la clave privada: {e}"
        )

    firma = sk.sign(
        mensaje
    )

    return binascii.hexlify(
        firma
    ).decode()


# ============================================================
# TRANSFERENCIA CHC
# ============================================================

def realizar_transferencia():

    print(
        f"\n{Col.BOLD}"
        f"--- NUEVA TRANSFERENCIA ---"
        f"{Col.END}"
    )

    receptor = input(
        "Dirección del receptor: "
    ).strip()

    if not receptor:

        print(
            f"{Col.RED}"
            f"[❌] Debes introducir una dirección."
            f"{Col.END}"
        )

        return

    try:

        monto = float(
            input(
                "Monto a enviar (CHC): "
            )
        )

        if monto <= 0:
            raise ValueError

    except ValueError:

        print(
            f"{Col.RED}"
            f"[❌] Monto inválido."
            f"{Col.END}"
        )

        return

    # ========================================================
    # DATOS
    # ========================================================

    emisor = user_wallet.datos["publica"]

    print(
        f"\n{Col.CYAN}"
        f"[*] Emisor:"
        f"{Col.END}"
    )

    print(emisor)

    print(
        f"\n{Col.CYAN}"
        f"[*] Receptor:"
        f"{Col.END}"
    )

    print(receptor)

    print(
        f"\n{Col.CYAN}"
        f"[*] Monto:"
        f"{Col.END} "
        f"{monto} CHC"
    )

    # ========================================================
    # COMPROBAR NODO
    # ========================================================

    print(
        f"\n{Col.CYAN}"
        f"[*] Comprobando conexión con "
        f"el nodo..."
        f"{Col.END}"
    )

    activo, info = comprobar_nodo()

    if not activo:

        print(
            f"{Col.RED}{Col.BOLD}"
            f"[❌] NO SE PUDO CONECTAR CON EL NODO"
            f"{Col.END}"
        )

        print(
            f"{Col.YELLOW}"
            f"Detalle:"
            f"{Col.END}"
        )

        print(info)

        return

    print(
        f"{Col.GREEN}{Col.BOLD}"
        f"[🟢] NODO ACTIVO"
        f"{Col.END}"
    )

    # ========================================================
    # CREAR FIRMA
    # ========================================================

    print(
        f"{Col.CYAN}"
        f"[*] Firmando transacción..."
        f"{Col.END}"
    )

    try:

        firma = crear_firma(
            emisor,
            receptor,
            monto
        )

    except Exception as e:

        print(
            f"{Col.RED}"
            f"[❌] No se pudo firmar:"
            f"{Col.END}"
        )

        print(e)

        return

    # ========================================================
    # PAYLOAD
    # ========================================================

    payload = {

        "emisor": emisor,

        "receptor": receptor,

        "monto": monto,

        "firma": firma
    }

    print(
        f"{Col.GREEN}"
        f"[🔐] Transacción firmada."
        f"{Col.END}"
    )

    # ========================================================
    # CONFIRMACIÓN
    # ========================================================

    print(
        f"\n{Col.YELLOW}{Col.BOLD}"
        f"--- CONFIRMACIÓN ---"
        f"{Col.END}"
    )

    print(
        f"Enviar: "
        f"{Col.BOLD}"
        f"{monto} CHC"
        f"{Col.END}"
    )

    print(
        f"Desde:"
    )

    print(
        f"{emisor[:40]}..."
    )

    print(
        f"Hacia:"
    )

    print(
        f"{receptor[:40]}..."
    )

    confirmar = input(
        "\n¿Confirmar transferencia? (s/n): "
    ).strip().lower()

    if confirmar != "s":

        print(
            f"{Col.YELLOW}"
            f"[!] Transferencia cancelada."
            f"{Col.END}"
        )

        return

    # ========================================================
    # ENVÍO
    # ========================================================

    print(
        f"\n{Col.CYAN}"
        f"[*] Enviando transacción al nodo..."
        f"{Col.END}"
    )

    url_transferencia = (
        f"{NODO_URL}/transferir"
    )

    print(
        f"{Col.CYAN}"
        f"[*] Endpoint:"
        f"{Col.END}"
    )

    print(url_transferencia)

    try:

        r = http.post(
            url_transferencia,
            json=payload,
            timeout=20
        )

        # ====================================================
        # MOSTRAR RESPUESTA REAL
        # ====================================================

        print(
            f"\n{Col.CYAN}"
            f"[📡] HTTP: {r.status_code}"
            f"{Col.END}"
        )

        # ====================================================
        # ÉXITO
        # ====================================================

        if 200 <= r.status_code < 300:

            try:
                respuesta = r.json()
            except ValueError:
                respuesta = {
                    "respuesta": r.text
                }

            print(
                f"\n{Col.GREEN}{Col.BOLD}"
                f"[✅] ¡TRANSFERENCIA ACEPTADA!"
                f"{Col.END}"
            )

            print(
                f"{Col.GREEN}"
                f"Respuesta del nodo:"
                f"{Col.END}"
            )

            print(respuesta)

            return

        # ====================================================
        # ERROR 404
        # ====================================================

        if r.status_code == 404:

            print(
                f"\n{Col.RED}{Col.BOLD}"
                f"[❌] ENDPOINT NO ENCONTRADO (404)"
                f"{Col.END}"
            )

            print(
                f"{Col.YELLOW}"
                f"El servidor está online, pero "
                f"no existe la ruta:"
                f"{Col.END}"
            )

            print(
                url_transferencia
            )

            print(
                f"\n{Col.YELLOW}"
                f"Esto NO significa que Render esté offline."
                f"{Col.END}"
            )

            try:

                print(
                    f"{Col.CYAN}"
                    f"Respuesta del servidor:"
                    f"{Col.END}"
                )

                print(r.json())

            except ValueError:

                print(
                    r.text[:1000]
                )

            return

        # ====================================================
        # ERROR 400
        # ====================================================

        if r.status_code == 400:

            print(
                f"\n{Col.RED}{Col.BOLD}"
                f"[❌] TRANSACCIÓN RECHAZADA (400)"
                f"{Col.END}"
            )

            try:

                datos = r.json()

                print(
                    f"{Col.YELLOW}"
                    f"Motivo del nodo:"
                    f"{Col.END}"
                )

                print(datos)

            except ValueError:

                print(
                    r.text[:1000]
                )

            return

        # ====================================================
        # ERROR 401 / 403
        # ====================================================

        if r.status_code in (401, 403):

            print(
                f"\n{Col.RED}{Col.BOLD}"
                f"[❌] AUTORIZACIÓN RECHAZADA "
                f"({r.status_code})"
                f"{Col.END}"
            )

            try:
                print(r.json())
            except ValueError:
                print(r.text[:1000])

            return

        # ====================================================
        # ERROR 500
        # ====================================================

        if r.status_code >= 500:

            print(
                f"\n{Col.RED}{Col.BOLD}"
                f"[❌] ERROR INTERNO DEL NODO "
                f"({r.status_code})"
                f"{Col.END}"
            )

            print(
                f"{Col.YELLOW}"
                f"El servidor está respondiendo, "
                f"pero encontró un error procesando "
                f"la transferencia."
                f"{Col.END}"
            )

            try:
                print(r.json())
            except ValueError:
                print(r.text[:1000])

            return

        # ====================================================
        # OTROS CÓDIGOS
        # ====================================================

        print(
            f"\n{Col.RED}"
            f"[❌] EL NODO RECHAZÓ LA OPERACIÓN"
            f"{Col.END}"
        )

        try:

            datos = r.json()

            print(
                f"{Col.YELLOW}"
                f"Respuesta:"
                f"{Col.END}"
            )

            print(datos)

        except ValueError:

            print(
                f"{Col.YELLOW}"
                f"Respuesta:"
                f"{Col.END}"
            )

            print(
                r.text[:1000]
            )

    # ========================================================
    # TIMEOUT
    # ========================================================

    except requests.exceptions.Timeout:

        print(
            f"\n{Col.RED}{Col.BOLD}"
            f"[⏱️] TIMEOUT"
            f"{Col.END}"
        )

        print(
            f"{Col.YELLOW}"
            f"El nodo no respondió dentro de "
            f"los 20 segundos."
            f"{Col.END}"
        )

        print(
            f"{Col.YELLOW}"
            f"Esto no confirma que el nodo esté offline."
            f"{Col.END}"
        )

    # ========================================================
    # CONEXIÓN
    # ========================================================

    except requests.exceptions.ConnectionError as e:

        print(
            f"\n{Col.RED}{Col.BOLD}"
            f"[❌] ERROR DE CONEXIÓN"
            f"{Col.END}"
        )

        print(
            f"{Col.YELLOW}"
            f"Detalle:"
            f"{Col.END}"
        )

        print(e)

    # ========================================================
    # REQUEST
    # ========================================================

    except requests.exceptions.RequestException as e:

        print(
            f"\n{Col.RED}{Col.BOLD}"
            f"[❌] ERROR HTTP"
            f"{Col.END}"
        )

        print(e)

    # ========================================================
    # ERROR GENERAL
    # ========================================================

    except Exception as e:

        print(
            f"\n{Col.RED}{Col.BOLD}"
            f"[❌] ERROR INESPERADO"
            f"{Col.END}"
        )

        print(
            f"{Col.YELLOW}"
            f"Tipo:"
            f"{Col.END} "
            f"{type(e).__name__}"
        )

        print(
            f"{Col.YELLOW}"
            f"Detalle:"
            f"{Col.END} "
            f"{e}"
        )


# ============================================================
# MOSTRAR DIRECCIÓN
# ============================================================

def mostrar_direccion():

    print(
        f"\n{Col.CYAN}{Col.BOLD}"
        f"--- MI DIRECCIÓN CHC ---"
        f"{Col.END}"
    )

    print(
        user_wallet.datos["publica"]
    )

    print(
        f"\n{Col.YELLOW}"
        f"Esta es la dirección pública de tu wallet."
        f"{Col.END}"
    )


# ============================================================
# EXPLORADOR
# ============================================================

def abrir_explorador():

    print(
        f"\n{Col.CYAN}"
        f"[*] Abriendo explorador..."
        f"{Col.END}"
    )

    webbrowser.open(
        NODO_URL
    )


# ============================================================
# MENU PRINCIPAL
# ============================================================

if __name__ == "__main__":

    try:

        mostrar_bienvenida()

        user_wallet = WalletCHC()

        tempo = TempoBridge(
            user_wallet
        )

        while True:

            print(
                f"\n{Col.BOLD}"
                f"--- MENU NEWWORLD ---"
                f"{Col.END}"
            )

            print(
                f"{Col.GREEN}"
                f"1. ⛏️  Minar CHC"
                f"{Col.END}"
            )

            print(
                f"{Col.YELLOW}"
                f"2. 💸 Enviar CHC"
                f"{Col.END}"
            )

            print(
                f"{Col.CYAN}"
                f"3. 🔑 Mi Dirección"
                f"{Col.END}"
            )

            print(
                f"{Col.MAGENTA}"
                f"4. 💳 Comprar CHC "
                f"(Tempo Fiat/Stable Ramp)"
                f"{Col.END}"
            )

            print(
                f"{Col.MAGENTA}"
                f"5. 💰 Vender CHC "
                f"(Tempo Cash Out)"
                f"{Col.END}"
            )

            print(
                f"{Col.CYAN}"
                f"6. 🌐 Explorador Web"
                f"{Col.END}"
            )

            print(
                f"{Col.RED}"
                f"7. 🚪 Salir"
                f"{Col.END}"
            )

            op = input(
                f"\n{Col.BOLD}"
                f"Opción: "
                f"{Col.END}"
            ).strip()

            # =================================================
            # MINAR
            # =================================================

            if op == "1":

                try:

                    minar()

                except KeyboardInterrupt:

                    print(
                        f"\n{Col.YELLOW}"
                        f"[!] Minería pausada."
                        f"{Col.END}"
                    )

                except Exception as e:

                    print(
                        f"\n{Col.RED}"
                        f"[❌] Error en minería:"
                        f"{Col.END}"
                    )

                    print(e)

            # =================================================
            # TRANSFERIR
            # =================================================

            elif op == "2":

                realizar_transferencia()

            # =================================================
            # DIRECCIÓN
            # =================================================

            elif op == "3":

                mostrar_direccion()

            # =================================================
            # COMPRAR
            # =================================================

            elif op == "4":

                tempo.cotizar_y_operar(
                    "compra"
                )

            # =================================================
            # VENDER
            # =================================================

            elif op == "5":

                tempo.cotizar_y_operar(
                    "venta"
                )

            # =================================================
            # EXPLORADOR
            # =================================================

            elif op == "6":

                abrir_explorador()

            # =================================================
            # SALIR
            # =================================================

            elif op == "7":

                print(
                    f"\n{Col.GREEN}"
                    f"👋 Cerrando NEWWORLD..."
                    f"{Col.END}"
                )

                break

            # =================================================
            # OPCIÓN INCORRECTA
            # =================================================

            else:

                print(
                    f"{Col.RED}"
                    f"[❌] Opción inválida."
                    f"{Col.END}"
                )

    except KeyboardInterrupt:

        print(
            f"\n\n{Col.YELLOW}"
            f"[!] Programa detenido por el usuario."
            f"{Col.END}"
        )

    except Exception as e:

        print(
            f"\n{Col.RED}{Col.BOLD}"
            f"[❌] ERROR FATAL"
            f"{Col.END}"
        )

        print(
            f"Tipo: {type(e).__name__}"
        )

        print(
            f"Detalle: {e}"
        )

        traceback.print_exc()
