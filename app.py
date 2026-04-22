import os
import asyncio
import logging
import uvicorn
from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.responses import PlainTextResponse
from dotenv import load_dotenv

from bioagent.config import WHATSAPP_VERIFY_TOKEN
from bioagent.startup import prepare_credentials
from bioagent.whatsapp_bot import process_whatsapp_message
from bioagent import rag
from bioagent import proactive

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

app = FastAPI(title="BioAgent WhatsApp Webhook")

@app.on_event("startup")
async def startup_event():
    logger.info("--- PREPARANDO CREDENCIALES ---")
    prepare_credentials()
    
    logger.info("🧠 Iniciando indexación RAG en segundo plano...")
    asyncio.create_task(rag.build_index_async())
    
    logger.info("🤖 Arrancando Motor Proactivo...")
    asyncio.create_task(proactive.proactive_loop())

@app.get("/")
def health_check():
    return {"status": "ok", "platform": "whatsapp_cloud_api"}

@app.get("/webhook")
async def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
):
    """
    Endpoint para verificación de Meta (Challenge).
    Meta hace un GET con estos parámetros. Debemos responder con el hub.challenge en texto plano.
    """
    if hub_mode == "subscribe" and hub_verify_token == WHATSAPP_VERIFY_TOKEN:
        logger.info("✅ Webhook verificado correctamente por Meta.")
        return PlainTextResponse(content=hub_challenge)
    
    logger.warning("❌ Falló la verificación del Webhook de Meta.")
    raise HTTPException(status_code=403, detail="Verificación fallida")

@app.post("/webhook")
async def receive_message(request: Request):
    """
    Endpoint para recibir mensajes de usuarios desde Meta (WhatsApp).
    """
    try:
        body = await request.json()
        # Lanzamos el procesamiento asíncrono para que Meta reciba un 200 rápido (exigen < 3s)
        asyncio.create_task(process_whatsapp_message(body))
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error procesando webhook: {e}")
        return {"status": "error"}

if __name__ == "__main__":
    load_dotenv()
    
    logger.info("--- DIAGNÓSTICO DE ENTORNO WHATSAPP ---")
    for var in ["WHATSAPP_TOKEN", "WHATSAPP_PHONE_ID", "WHATSAPP_VERIFY_TOKEN", "GEMINI_API_KEY", "OWNER_PHONE_NUMBER"]:
        val = os.getenv(var, "")
        masked = val[:4] + "..." + val[-4:] if len(val) > 8 else ("Configurado" if val else "FALTANTE")
        logger.info(f"🔍 {var}: {masked}")
        
    print("--- INICIANDO SERVIDOR WEBHOOK ---", flush=True)
    uvicorn.run(app, host="0.0.0.0", port=7860, log_level="warning")
