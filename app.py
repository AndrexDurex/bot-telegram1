
import os
import sys

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
    
    # Arrancamos el bot en un hilo normal, no demonio, para que al recibir SIGTERM
    # desde Hugging Face, de tiempo al event loop de telegram de cerrarse limpiamente
    # antes de que el proceso muera.
    bot_thread = threading.Thread(target=run_bot, daemon=False)
    bot_thread.start()
    
    # Arrancamos el servidor dummy en el hilo principal para satisfacer
    # el healthcheck de Hugging Face (espera algo en el puerto 7860).
    print("--- INICIANDO SERVIDOR DUMMY HEALTHCHECK EN 0.0.0.0:7860 ---", flush=True)
    uvicorn.run("app:app", host="0.0.0.0", port=7860, log_level="warning")
