
import os
import sys
import logging
from dotenv import load_dotenv
from bioagent.startup import prepare_credentials

# Si Hugging Face espera que abramos un puerto (FastAPI/Gradio), le daremos un 
# pequeño servidor dummy de salud para que no mate el contenedor por timeout.
# Y ejecutamos el bot de Telegram en un hilo en segundo plano.

import threading
import uvicorn
from fastapi import FastAPI

app = FastAPI(title="BioAgent Health Check")

@app.get("/")
def health_check():
    return {"status": "ok", "bot": "running"}

def run_server():
    """Ejecuta el servidor FastAPI en un hilo secundario."""
    print("--- INICIANDO SERVIDOR HEALTHCHECK EN HILO SECUNDARIO ---", flush=True)
    # Usamos la instancia 'app' directamente aquí ya que 'app:app' 
    # a veces da problemas en hilos secundarios con uvicorn.
    uvicorn.run(app, host="0.0.0.0", port=7860, log_level="warning")

def run_bot():
    """Ejecuta el bot en el hilo principal."""
    print("--- INICIANDO BOT DE TELEGRAM (HILO PRINCIPAL) ---", flush=True)
    from bioagent.bot import run
    try:
        run()
    except Exception as e:
        print(f"❌ ERROR CRÍTICO EN EL BOT: {e}", flush=True)

if __name__ == "__main__":
    # 1. Cargar variables de entorno (especialmente importante en local)
    load_dotenv()

    # Diagnóstico de variables críticas (enmascaradas)
    print("--- DIAGNÓSTICO DE ENTORNO ---", flush=True)
    for var in ["TELEGRAM_BOT_TOKEN", "GEMINI_API_KEY", "FIREBASE_RTDB_URL", "OWNER_CHAT_ID"]:
        val = os.getenv(var, "")
        masked = val[:4] + "..." + val[-4:] if len(val) > 8 else ("Configurado" if val else "FALTANTE")
        print(f"🔍 {var}: {masked}", flush=True)

    # 2. Restaurar credenciales desde secrets si estamos en producción
    print("--- PREPARANDO CREDENCIALES ---", flush=True)
    prepare_credentials()
    
    # 3. Arrancamos el servidor dummy en un hilo secundario (demonio)
    # Lo ponemos como demonio para que si el bot muere, el proceso termine.
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # 4. Arrancamos el bot en el hilo principal (REQUERIDO para señales de sistema)
    run_bot()
