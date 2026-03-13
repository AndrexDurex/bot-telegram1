
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

def run_bot():
    """Ejecuta el bot en su propio thread para que tenga su propio event loop."""
    print("--- INICIANDO HILO DEL BOT DE TELEGRAM ---", flush=True)
    import asyncio
    from bioagent.bot import run
    
    # Necesario para que apscheduler y telegram tengan su propio loop en este thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
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
    
    # Arrancamos el bot en un hilo normal, no demonio, para que al recibir SIGTERM
    # desde Hugging Face, dé tiempo al event loop de telegram de cerrarse limpiamente
    # antes de que el proceso muera.
    bot_thread = threading.Thread(target=run_bot, daemon=False)
    bot_thread.start()
    
    # Arrancamos el servidor dummy en el hilo principal para satisfacer
    # el healthcheck de Hugging Face (espera algo en el puerto 7860).
    print("--- INICIANDO SERVIDOR DUMMY HEALTHCHECK EN 0.0.0.0:7860 ---", flush=True)
    uvicorn.run("app:app", host="0.0.0.0", port=7860, log_level="warning")
