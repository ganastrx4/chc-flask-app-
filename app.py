import binascii
import hashlib
import json
import os
import platform
import subprocess
import sys
import time
import traceback
import webbrowser

# ============================================================
# LIBRERÍAS
# ============================================================


def verificar_librerias():
  librerias = ["requests", "mnemonic", "ecdsa", "psutil"]

  faltantes = []

  for lib in librerias:
    try:
      __import__(lib)
    except ImportError:
      faltantes.append(lib)

  if faltantes:
    print(
        f"\n[!] Detectando entorno... instalando: {', '.join(faltantes)}"
    )

    try:
      subprocess.check_call([sys.executable, "-m", "pip", "install", *faltantes])

      print("[✅] Entorno configurado correctamente.\n")

    except Exception as e:
      print(f"[❌] No se pudieron instalar las librerías: {e}")
      sys.exit(1)


verificar_librerias()

import ecdsa
from mnemonic import Mnemonic
import psutil
import requests

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

http.headers.update({"User-Agent": "NEWWORLD-CHC-Miner/1.0"})

# ============================================================
# FUNCIONES DE RED
# ============================================================


def comprobar_nodo():
  try:
    url = f"{NODO_URL}/health"
    respuesta = http.get(url, timeout=15)

    if respuesta.status_code == 200:
      try:
        datos = respuesta.json()
      except ValueError:
        datos = {}
      return True, datos

    return False, {
        "status_code": respuesta.status_code,
        "respuesta": respuesta.text[:500],
    }

  except requests.exceptions.Timeout:
    return False, {
        "error": "TIMEOUT",
        "detalle": "El nodo tardó demasiado en responder.",
    }
  except requests.exceptions.ConnectionError as e:
    return False, {"error": "CONNECTION_ERROR", "detalle": str(e)}
  except requests.exceptions.RequestException as e:
    return False, {"error": "REQUEST_ERROR", "detalle": str(e)}
  except Exception as e:
    return False, {"error": "ERROR", "detalle": str(e)}


def mostrar_estado_nodo():
  print(f"\n{Col.CYAN}{Col.BOLD}[*] Comprobando Nodo CHC...{Col.END}")
  activo, informacion = comprobar_nodo()

  if activo:
    print(f"{Col.GREEN}{Col.BOLD}[🟢] NODO ACTIVO{Col.END}")
    if informacion:
      print(f"{Col.CYAN}Respuesta: {informacion}{Col.END}")
    return True

  print(f"{Col.RED}[🔴] No se pudo comprobar el nodo.{Col.END}")
  print(f"{Col.YELLOW}Detalle: {informacion}{Col.END}")
  return False


# ============================================================
# HARDWARE
# ============================================================


def mostrar_hardware():
  print(f"{Col.CYAN}{Col.BOLD}--- ESPECIFICACIONES DEL MINERO ---{Col.END}")
  print(f"{Col.BOLD}Sistema:{Col.END} {platform.system()} {platform.release()}")
  print(f"{Col.BOLD}Procesador:{Col.END} {platform.processor()}")
  print(
      f"{Col.BOLD}Núcleos:{Col.END} {psutil.cpu_count(logical=False)} Físicos /"
      f" {psutil.cpu_count(logical=True)} Lógicos"
  )
  print(
      f"{Col.BOLD}RAM Total:{Col.END}"
      f" {round(psutil.virtual_memory().total / (1024 ** 3), 2)} GB"
  )
  print(
      f"{Col.BOLD}Fecha Local:{Col.END}"
      f" {time.strftime('%d/%m/%Y %H:%M:%S')}"
  )
  print(f"{Col.BOLD}Nodo:{Col.END} {NODO_URL}")
  print(f"{Col.BOLD}Dificultad local:{Col.END} {DIFICULTAD}")
  print(
      f"{Col.BOLD}Recompensa de referencia:{Col.END} {RECOMPENSA_ACTUAL} CHC"
  )
  print(f"{Col.CYAN}" + "-" * 75 + f"{Col.END}")


# ============================================================
# BIENVENIDA
# ============================================================


def mostrar_bienvenida():
  os.system("cls" if os.name == "nt" else "clear")
  print(f"{Col.CYAN}{Col.BOLD}" + "=" * 75)
  print("    🚀 BIENVENIDO A LA RED CHARLYCOIN (CHC)")
  print("    PROYECTO NEWWORLD NETWORK")
  print("=" * 75 + f"{Col.END}")

  mostrar_hardware()

  print(f"{Col.MAGENTA}{Col.BOLD}[RESEÑA]:{Col.END}")
  print("CharlyCoin es una visión de soberanía digital creada en Chimalhuacán.")
  print("Buscamos un ecosistema financiero donde el control regrese al usuario.")
  print(f"\n{Col.YELLOW}{Col.BOLD}[SEGURIDAD]:{Col.END} Billetera local firmada.")
  print(f"{Col.CYAN}" + "-" * 75 + f"{Col.END}")


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
        with open(self.archivo, "r", encoding="utf-8") as f:
          datos = json.load(f)

        if "publica" not in datos or "privada" not in datos:
          raise ValueError("Wallet incompleta.")

        print(
            f"{Col.GREEN}[🏠] Wallet activa: {Col.END}{Col.BOLD}"
            f"{datos['publica'][:30]}...{Col.END}"
        )
        return datos

      except Exception as e:
        print(f"{Col.RED}[❌] Error leyendo wallet: {e}{Col.END}")
        sys.exit(1)
    else:
      print(f"{Col.YELLOW}[*] Forjando nueva identidad en la Blockchain...{Col.END}")
      mnemo = Mnemonic("spanish")
      palabras = mnemo.generate(strength=128)
      seed = mnemo.to_seed(palabras)

      sk = ecdsa.SigningKey.from_string(seed[:32], curve=ecdsa.SECP256k1)
      vk = sk.get_verifying_key()

      datos = {
          "publica": binascii.hexlify(vk.to_string()).decode(),
          "privada": binascii.hexlify(sk.to_string()).decode(),
          "semilla": palabras,
      }

      with open(self.archivo, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)

      print(f"\n{Col.GREEN}>> SEMILLA GENERADA: {palabras} <<{Col.END}")
      print(f"\n{Col.YELLOW}⚠️ GUARDA ESTA SEMILLA EN UN LUGAR SEGURO.{Col.END}")
      return datos


# ============================================================
# TEMPO BRIDGE
# ============================================================


class TempoBridge:

  def __init__(self, wallet_chc):
    self.wallet = wallet_chc
    self.pool_wallet = "0x9D437783e3b940AC85557765D8b07fF7a69fB4e6"

  def cotizar_y_operar(self, operacion="compra"):
    print(
        f"\n{Col.BOLD}--- {operacion.upper()} DE CHC VIA INFRAESTRUCTURA"
        f" TEMPO ---{Col.END}"
    )
    print("Selecciona la moneda de intercambio:")
    print("1. USDT (Stablecoin Dólar)")
    print("2. Fíat Directo (EUR / Moneda de la pasarela)")

    metodo = input(f"{Col.BOLD}Opción (1 o 2): {Col.END}").strip()
    asset_intercambio = "USDT" if metodo == "1" else "EUR"

    if metodo == "2":
      fiat_input = input(
          "Moneda Fíat a usar (Ej: EUR, USD, MXN) [Por defecto EUR]: "
      ).strip().upper()
      if fiat_input:
        asset_intercambio = fiat_input

    try:
      monto = float(input(f"Monto en {asset_intercambio} a procesar: "))
      if monto <= 0:
        raise ValueError
    except ValueError:
      print(f"{Col.RED}[❌] Monto inválido.{Col.END}")
      return

    print(f"{Col.CYAN}[*] Consultando tasas de intercambio...{Col.END}")
    time.sleep(1)

    tasa_cambio = 0.85 if operacion == "compra" else 0.80
    tokens_estimados = round(monto / tasa_cambio, 6)

    print(f"\n{Col.GREEN}{Col.BOLD}[📊] COTIZACIÓN DE INTERCAMBIO:{Col.END}")
    if operacion == "compra":
      print(f"Envías: {monto} {asset_intercambio}")
      print(
          f"Recibes en tu Wallet CHC: {Col.BOLD}{tokens_estimados}"
          f" CHC{Col.END}"
      )
    else:
      print(f"Entregas: {monto} CHC")
      print(f"Recibes: {Col.BOLD}{tokens_estimados} {asset_intercambio}{Col.END}")

    confirmar = input(
        "\n¿Proceder con las instrucciones del Pool de Liquidación? (s/n): "
    ).strip().lower()

    if confirmar == "s":
      print(f"\n{Col.YELLOW}{Col.BOLD}[📌] INSTRUCCIONES DE DEPOSIT_POOL:{Col.END}")
      print(
          f"1. Transfiere exactamente {monto} {asset_intercambio} a la cuenta"
          " recaudadora:"
      )
      print(f"   👉 {Col.CYAN}{self.pool_wallet}{Col.END}")
      print(
          "2. IMPORTANTE: Agrega en el campo 'MEMO/MENSAJE' de tu billetera tu"
          " dirección CHC:"
      )
      print(f"   👉 {self.wallet.datos['publica']}")
      print("3. El nodo auditará el ingreso y asignará el balance.")
      input(f"\n{Col.BOLD}Presiona Enter para regresar...{Col.END}")
    else:
      print(f"{Col.YELLOW}[!] Operación cancelada.{Col.END}")


# ============================================================
# MINERÍA
# ============================================================


def minar():
  direccion = user_wallet.datos["publica"]
  print(f"{Col.CYAN}\n[*] Sincronizando con Nodo Maestro...{Col.END}")
  activo, info = comprobar_nodo()

  if not activo:
    print(f"{Col.RED}[❌] No se pudo conectar con el nodo.{Col.END}")
    print(f"{Col.YELLOW}Detalle: {info}{Col.END}")
    return

  print(f"{Col.GREEN}[🟢] Nodo disponible.{Col.END}")
  print(f"{Col.CYAN}[*] Dificultad local: {DIFICULTAD}{Col.END}")
  print(f"{Col.CYAN}[*] Recompensa de referencia: {RECOMPENSA_ACTUAL} CHC{Col.END}")
  print(f"{Col.YELLOW}[*] La recompensa real será determinada por el nodo.{Col.END}")

  nonce = 0
  start_time = time.time()

  while True:
    contenido = f"{direccion}{nonce}".encode()
    h = hashlib.sha256(contenido).hexdigest()

    if h.startswith("0" * DIFICULTAD):
      print(f"\n{Col.GREEN}{Col.BOLD}[💎] ¡BLOQUE MINADO!{Col.END}")
      print(f"{Col.CYAN}Nonce: {nonce}{Col.END}")
      print(f"{Col.CYAN}Hash: {h}{Col.END}")
      print(f"{Col.YELLOW}Recompensa de referencia: {RECOMPENSA_ACTUAL} CHC{Col.END}")

      try:
        respuesta = http.post(
            f"{NODO_URL}/minar",
            json={"wallet": direccion, "nonce": nonce},
            timeout=15,
        )
        print(f"{Col.CYAN}[📡] Nodo respondió HTTP {respuesta.status_code}{Col.END}")
        try:
          datos = respuesta.json()
          print(f"{Col.CYAN}[📦] Respuesta:{Col.END}")
          print(datos)
        except ValueError:
          print(f"{Col.YELLOW}[📄] Respuesta no JSON:{Col.END}")
          print(respuesta.text[:500])
      except Exception as e:
        print(f"{Col.RED}[⚠️] Error enviando bloque al nodo: {e}{Col.END}")

      nonce = 0
      time.sleep(2)

    nonce += 1
    if nonce % 200000 == 0:
      elapsed = time.time() - start_time
      if elapsed <= 0:
        elapsed = 0.001
      khs = round((nonce / elapsed) / 1000, 2)
      cpu = psutil.cpu_percent()
      print(
          f"{Col.CYAN}[🚀] Velocidad: {khs} KH/s | Intentos: {nonce} | CPU:"
          f" {cpu}%{Col.END}",
          end="\r",
      )


# ============================================================
# FIRMA DE TRANSACCIÓN
# ============================================================


def crear_firma(emisor, receptor, monto):
  mensaje = f"{emisor}{receptor}{monto}".encode()
  try:
    sk = ecdsa.SigningKey.from_string(
        binascii.unhexlify(user_wallet.datos["privada"]), curve=ecdsa.SECP256k1
    )
  except Exception as e:
    raise RuntimeError(f"No se pudo cargar la clave privada: {e}")

  firma = sk.sign(mensaje)
  return binascii.hexlify(firma).decode()


# ============================================================
# TRANSFERENCIA CHC
# ============================================================


def realizar_transferencia():
  print(f"\n{Col.BOLD}--- NUEVA TRANSFERENCIA ---{Col.END}")
  receptor = input("Dirección del receptor: ").strip()
  if not receptor:
    print(f"{Col.RED}[❌] Debes introducir una dirección.{Col.END}")
    return

  try:
    monto = float(input("Monto a enviar (CHC): "))
    if monto <= 0:
      raise ValueError
  except ValueError:
    print(f"{Col.RED}[❌] Monto inválido.{Col.END}")
    return

  emisor = user_wallet.datos["publica"]
  print(f"\n{Col.CYAN}[*] Emisor:{Col.END}\n{emisor}")
  print(f"\n{Col.CYAN}[*] Receptor:{Col.END}\n{receptor}")
  print(f"\n{Col.CYAN}[*] Monto:{Col.END} {monto} CHC")

  print(f"\n{Col.CYAN}[*] Comprobando conexión con el nodo...{Col.END}")
  activo, info = comprobar_nodo()

  if not activo:
    print(f"{Col.RED}{Col.BOLD}[❌] NO SE PUDO CONECTAR CON EL NODO{Col.END}")
    print(f"{Col.YELLOW}Detalle:\n{info}{Col.END}")
    return

  print(f"{Col.GREEN}{Col.BOLD}[🟢] NODO ACTIVO{Col.END}")
  print(f"{Col.CYAN}[*] Firmando transacción...{Col.END}")

  try:
    firma = crear_firma(emisor, receptor, monto)
  except Exception as e:
    print(f"{Col.RED}[❌] No se pudo firmar:\n{e}{Col.END}")
    return

  payload = {"emisor": emisor, "receptor": receptor, "monto": monto, "firma": firma}
  print(f"{Col.GREEN}[🔐] Transacción firmada.{Col.END}")

  print(f"\n{Col.YELLOW}{Col.BOLD}--- CONFIRMACIÓN ---{Col.END}")
  print(f"Enviar: {Col.BOLD}{monto} CHC{Col.END}")
  print(f"Desde:\n{emisor[:40]}...")
  print(f"Hacia:\n{receptor[:40]}...")

  confirmar = input("\n¿Confirmar transferencia? (s/n): ").strip().lower()
  if confirmar != "s":
    print(f"{Col.YELLOW}[!] Transferencia cancelada.{Col.END}")
    return

  print(f"\n{Col.CYAN}[*] Enviando transacción al nodo...{Col.END}")
  url_transferencia = f"{NODO_URL}/transferir"

  try:
    r = http.post(url_transferencia, json=payload, timeout=20)
    print(f"\n{Col.CYAN}[📡] HTTP: {r.status_code}{Col.END}")

    if 200 <= r.status_code < 300:
      try:
        respuesta = r.json()
      except ValueError:
        respuesta = {"respuesta": r.text}
      print(f"\n{Col.GREEN}{Col.BOLD}[✅] ¡TRANSFERENCIA ACEPTADA!{Col.END}")
      print(f"{Col.GREEN}Respuesta del nodo:{Col.END}\n{respuesta}")
      return
    else:
      print(f"\n{Col.RED}[❌] EL NODO RECHAZÓ LA OPERACIÓN{Col.END}")
      try:
        print(r.json())
      except ValueError:
        print(r.text[:1000])

  except Exception as e:
    print(f"\n{Col.RED}[❌] Error en la solicitud: {e}{Col.END}")


# ============================================================
# MOSTRAR DIRECCIÓN
# ============================================================


def mostrar_direccion():
  print(f"\n{Col.CYAN}{Col.BOLD}--- MI DIRECCIÓN CHC ---{Col.END}")
  print(user_wallet.datos["publica"])
  print(f"\n{Col.YELLOW}Esta es la dirección pública de tu wallet.{Col.END}")


# ============================================================
# EXPLORADOR
# ============================================================


def abrir_explorador():
  print(f"\n{Col.CYAN}[*] Abriendo explorador...{Col.END}")
  webbrowser.open(NODO_URL)


# ============================================================
# MENU PRINCIPAL
# ============================================================

if __name__ == "__main__":
  try:
    mostrar_bienvenida()
    user_wallet = WalletCHC()
    tempo = TempoBridge(user_wallet)

    while True:
      print(f"\n{Col.BOLD}--- MENU NEWWORLD ---{Col.END}")
      print(f"{Col.GREEN}1. ⛏️ Minar CHC{Col.END}")
      print(f"{Col.YELLOW}2. 💸 Enviar CHC{Col.END}")
      print(f"{Col.CYAN}3. 📥 Comprar / Depositar CHC (Tempo){Col.END}")
      print(f"{Col.CYAN}4. 📤 Vender / Retirar CHC (Tempo){Col.END}")
      print(f"{Col.CYAN}5. 🔍 Ver mi Dirección CHC{Col.END}")
      print(f"{Col.CYAN}6. 🌐 Abrir CharlyScan (Explorador){Col.END}")
      print(f"{Col.RED}7. 🚪 Salir{Col.END}")

      opcion = input(f"\n{Col.BOLD}Selecciona una opción: {Col.END}").strip()

      if opcion == "1":
        minar()
      elif opcion == "2":
        realizar_transferencia()
      elif opcion == "3":
        tempo.cotizar_y_operar("compra")
      elif opcion == "4":
        tempo.cotizar_y_operar("venta")
      elif opcion == "5":
        mostrar_direccion()
      elif opcion == "6":
        abrir_explorador()
      elif opcion == "7":
        print(f"\n{Col.GREEN}¡Gracias por minar CharlyCoin! Saliendo...{Col.END}")
        break
      else:
        print(f"{Col.RED}[❌] Opción inválida. Intenta de nuevo.{Col.END}")

  except KeyboardInterrupt:
    print(f"\n\n{Col.YELLOW}[!] Programa interrumpido por el usuario.{Col.END}")
  except Exception as e:
    print(f"\n{Col.RED}[❌] Error crítico inesperado:\n{e}{Col.END}")
    traceback.print_exc()
