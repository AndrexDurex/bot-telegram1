"""
BioAgent — Handler principal para WhatsApp Cloud API.
Motor de conversación con Gemini 2.5 Flash + memoria + RAG, adaptado para recibir Webhooks HTTP.
"""
import asyncio
import logging
import httpx
from typing import Dict, Any

from bioagent.config import (
    WHATSAPP_TOKEN, WHATSAPP_PHONE_ID, BOT_NAME, SYSTEM_PROMPT, 
    GEMINI_API_KEY, GEMINI_MODEL, OWNER_PHONE_NUMBER
)
from bioagent import rag, memory, calendar_service, tasks

logger = logging.getLogger(__name__)

# Motor de Gemini
_gemini_model = None

# Historial en memoria (fallback)
_conversation_history: dict[str, list] = {}

async def send_whatsapp_message(to_number: str, text: str) -> None:
    """Envía un mensaje de texto a través de WhatsApp Cloud API."""
    if not WHATSAPP_TOKEN or not WHATSAPP_PHONE_ID:
        logger.error("❌ Faltan credenciales de WhatsApp.")
        return

    url = f"https://graph.facebook.com/v19.0/{WHATSAPP_PHONE_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Adaptar formato markdown a WhatsApp
    # WhatsApp soporta *negrita*, _cursiva_, ~tachado~ y ```monospace```
    text = text.replace("**", "*")  # Convertimos el markdown estricto de Gemini
    
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {"body": text}
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json=payload, timeout=30.0)
            response.raise_for_status()
            logger.info(f"✅ Mensaje enviado exitosamente a {to_number}")
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ Error al enviar mensaje WhatsApp: {e.response.text}")
        except Exception as e:
            import traceback
            logger.error(f"❌ Excepción enviando WhatsApp: {e}\n{traceback.format_exc()}")

async def process_whatsapp_message(body: Dict[str, Any]) -> None:
    """Procesa el JSON entrante del webhook de WhatsApp."""
    try:
        # Navegamos el payload complejo de WhatsApp
        entry = body.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})
        
        # Ignoramos mensajes de sistema o status updates (entregado/leído)
        if "messages" not in value:
            return
            
        messages = value["messages"]
        contacts = value.get("contacts", [])
        
        for msg in messages:
            # Solo procesamos mensajes de texto por ahora
            if msg.get("type") != "text":
                continue
                
            from_number = msg["from"]     # El número que escribió
            text_body = msg["text"]["body"]  # El texto del mensaje
            
            # ── Guard de autorización ──
            if OWNER_PHONE_NUMBER and not from_number.endswith(OWNER_PHONE_NUMBER[-8:]):
                # Validamos terminación por posibles códigos de país ej: 521 vs 52
                logger.warning(f"🔒 Acceso denegado al número {from_number}")
                await send_whatsapp_message(from_number, "🔒 Acceso restringido. Soy un asistente privado.")
                continue

            logger.info(f"📥 WhatsApp de {from_number}: {text_body[:30]}...")
            
            # Lanzamos el procesamiento de IA
            await handle_ai_response(from_number, text_body)

    except Exception as e:
        logger.error(f"❌ Error procesando webhook de WhatsApp: {e}")

import contextvars
_current_user_id = contextvars.ContextVar('current_user_id')

def add_task_tool(title: str, priority: str = "media", category: str = "general") -> str:
    """
    Crea una nueva tarea pendiente para el usuario y la guarda en su base de datos.
    Usa esta herramienta SIEMPRE que el usuario te pida agregar una tarea, anotar algo pendiente o recordar algo.
    
    Args:
        title: El título o descripción concisa de la tarea.
        priority: Nivel de prioridad de la tarea. Opciones válidas: "alta", "media" o "baja".
        category: Categoría de la tarea. Opciones recomendadas: "salud", "tesis", "general".
    """
    try:
        user_id = _current_user_id.get()
        result = tasks.add_task(user_id, title=title, priority=priority, category=category)
        if result:
            return f"Tarea '{title}' agregada exitosamente con ID {result}"
        return "Error al agregar tarea en Firebase."
    except Exception as e:
        return f"Error interno de Python: {e}"

async def handle_ai_response(user_number: str, user_text: str) -> None:
    """Invoca la inteligencia y envía de vuelta a WhatsApp."""
    global _gemini_model
    
    # Tratar user_number como identifier para la memoria
    user_id = user_number 
    _current_user_id.set(user_id)
    
    try:
        # Inicializar modelo
        if _gemini_model is None:
            import google.generativeai as genai
            genai.configure(api_key=GEMINI_API_KEY)
            _gemini_model = genai.GenerativeModel(
                model_name=GEMINI_MODEL,
                system_instruction=SYSTEM_PROMPT,
                tools=[add_task_tool]
            )

        # 1. Recuperar memoria (Firebase)
        firebase_history = await asyncio.to_thread(memory.build_gemini_history, user_id)
        history = firebase_history if firebase_history else _conversation_history.get(user_id, [])

        # 2. Contexto (RAG + Calendar + Tasks)
        rag_context = await asyncio.to_thread(rag.search, user_text)
        agenda_context = await calendar_service.get_agenda_summary_async(days=3)
        tasks_context = await asyncio.to_thread(tasks.get_tasks_summary, user_id)

        # Construir prompt enriquecido
        parts = []
        if rag_context: parts.append(rag_context)
        if agenda_context: parts.append(agenda_context)
        if tasks_context: parts.append(tasks_context)
        parts.append(f"## Consulta del usuario:\n{user_text}")
        enriched_prompt = "\n\n".join(parts)

        # 3. Invocar Gemini
        chat = _gemini_model.start_chat(
            history=history,
            enable_automatic_function_calling=True
        )
        response = await asyncio.to_thread(
            lambda: chat.send_message(enriched_prompt)
        )
        bot_reply = response.text

        # 4. Guardar historiales
        await asyncio.to_thread(memory.save_message, user_id, "user", user_text)
        await asyncio.to_thread(memory.save_message, user_id, "model", bot_reply)
        _conversation_history[user_id] = chat.history

        # 5. Enviar mensaje por WhatsApp
        await send_whatsapp_message(user_number, bot_reply)

    except Exception as e:
        logger.error(f"❌ Error en Gemini/WhatsApp: {e}")
        await send_whatsapp_message(user_number, "⚠️ Tuve un problema procesando tu consulta. Intenta de nuevo en un momento.")
