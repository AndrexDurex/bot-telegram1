import socket
import sys
import os

# --- [URGENTE] DNS WORKAROUND V7.0 (Top-Level Patch) ---
# Se aplica ANTES de cualquier otro import para asegurar que todas las librerías 
# (httpx, httpcore, etc.) usen la versión parcheada.
if not hasattr(socket, "_orig_getaddrinfo"):
    socket._orig_getaddrinfo = socket.getaddrinfo
    
    def _patched_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
        # logging minimal para no saturar pero confirmar que funciona
        if "telegram" in host:
            try:
                # Intentamos resolución IPv4 (AF_INET es fundamental en HF)
                return socket._orig_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)
            except Exception as e:
                print(f"⚠️ [DNS Fallback] Falló resolución para {host}: {e}. Usando IP de rescate.", flush=True)
                # El 'Rescue' con la IP oficial de Telegram (149.154.167.220)
                # El puerto debe ser int en el addr de AF_INET
                return [(socket.AF_INET, socket.SOCK_STREAM, 6, '', ('149.154.167.220', int(port)))]
        return socket._orig_getaddrinfo(host, port, family, type, proto, flags)
    
    socket.getaddrinfo = _patched_getaddrinfo
    print("--- [WORKAROUND] DNS Fallback V7.0 ACTIVADO (api.telegram.org -> Auto-Rescue) ---", flush=True)

import logging
import threading
import uvicorn
from fastapi import FastAPI
from dotenv import load_dotenv
from bioagent.startup import prepare_credentials
from diag_net import run_diagnostic

app = FastAPI(title="BioAgent Health Check")

@app.get("/")
def health_check():
    return {"status": "ok", "bot": "running"}

def run_server():
    print("--- INICIANDO SERVIDOR HEALTHCHECK EN HILO SECUNDARIO ---", flush=True)
    uvicorn.run(app, host="0.0.0.0", port=7860, log_level="warning")

def run_bot():
    print("--- INICIANDO BOT DE TELEGRAM (HILO PRINCIPAL) ---", flush=True)
    from bioagent.bot import run
    try:
        run()
    except Exception as e:
        print(f"❌ ERROR CRÍTICO EN EL BOT: {e}", flush=True)

if __name__ == "__main__":
    load_dotenv()
    
    # Diagnóstico de variables críticas
    print("--- DIAGNÓSTICO DE ENTORNO ---", flush=True)
    for var in ["TELEGRAM_BOT_TOKEN", "GEMINI_API_KEY", "FIREBASE_RTDB_URL", "OWNER_CHAT_ID"]:
        val = os.getenv(var, "")
        masked = val[:4] + "..." + val[-4:] if len(val) > 8 else ("Configurado" if val else "FALTANTE")
        print(f"🔍 {var}: {masked}", flush=True)

    # Correr diagnóstico de red completo
    try:
        run_diagnostic()
    except Exception as e:
        print(f"⚠️ Error en diagnóstico: {e}", flush=True)

    # Preparar credenciales
    print("--- PREPARANDO CREDENCIALES ---", flush=True)
    prepare_credentials()
    
    # Iniciar servidor healthcheck
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Iniciar bot
    run_bot()
