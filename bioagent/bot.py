"""
BioAgent — Handler principal de Telegram.
Motor de conversación con Gemini 2.5 Flash + memoria + RAG.
"""
import asyncio
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from bioagent.config import TELEGRAM_BOT_TOKEN, BOT_NAME, SYSTEM_PROMPT, GEMINI_API_KEY, GEMINI_MODEL, OWNER_CHAT_ID
from bioagent import rag, memory, calendar_service, tasks, scheduler

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ── Gemini setup ──────────────────────────────────────────────────────────────
import google.generativeai as genai

genai.configure(api_key=GEMINI_API_KEY)
_gemini_model = genai.GenerativeModel(
    model_name=GEMINI_MODEL,
    system_instruction=SYSTEM_PROMPT,
)

# Historial en memoria (fallback si Firebase no está disponible)
_conversation_history: dict[int, list] = {}


# ── Guard de autorización ─────────────────────────────────────────────────────
async def _is_owner(update: Update) -> bool:
    """Devuelve True solo si el mensaje viene del dueño del bot."""
    user_id = update.effective_user.id if update.effective_user else None
    if user_id != OWNER_CHAT_ID:
        logger.warning(f"Acceso denegado al usuario {user_id}")
        await update.message.reply_text("🔒 Acceso restringido.")
        return False
    return True


# ── Comandos ──────────────────────────────────────────────────────────────────
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Mensaje de bienvenida."""
    if not await _is_owner(update):
        return
    user = update.effective_user
    await update.message.reply_text(
        f"🧬 *Hola {user.first_name}!* Soy *{BOT_NAME}*.\n\n"
        f"Soy tu asistente de salud de élite, especializado en los protocolos "
        f"del Dr. La Rosa 💪\n\n"
        f"Puedes preguntarme sobre:\n"
        f"• 🔥 Testosterona y hormonas\n"
        f"• ⏱️ Ayuno intermitente\n"
        f"• 💊 Suplementación y longevidad\n"
        f"• 😴 Optimización del sueño\n"
        f"• 🏋️ Metabolismo y grasa corporal\n"
        f"• ✨ Estética y cabello\n\n"
        f"_¡Escríbeme tu consulta!_",
        parse_mode="Markdown",
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Lista de comandos disponibles."""
    if not await _is_owner(update):
        return
    await update.message.reply_text(
        "📋 *Comandos disponibles:*\n\n"
        "/start — Bienvenida\n"
        "/help — Lista de comandos\n"
        "/agenda — Ver tu agenda de la semana\n"
        "/reset — Limpiar historial de conversación\n"
        "/pilares — Ver los 6 Pilares de Salud\n",
        parse_mode="Markdown",
    )


async def cmd_reset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Limpia el historial de conversación."""
    if not await _is_owner(update):
        return
    user_id = update.effective_user.id
    _conversation_history.pop(user_id, None)
    await update.message.reply_text(
        "🔄 Historial limpiado. ¡Empezamos de cero!"
    )


async def cmd_pilares(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Muestra los 6 Pilares de Salud."""
    if not await _is_owner(update):
        return
    await update.message.reply_text(
        "🏛️ *Los 6 Pilares de Salud del Dr. La Rosa:*\n\n"
        "1️⃣ *Optimización Hormonal* — Testosterona, disruptores, sueño\n"
        "2️⃣ *Longevidad y Suplementación* — NAD, NMN, AKG, hongos medicinales\n"
        "3️⃣ *Salud Digestiva y Detox* — Microbiota, Candida, hígado graso\n"
        "4️⃣ *Metabolismo y Grasa Corporal* — Ayuno, glucosa, entrenamiento\n"
        "5️⃣ *Sueño, Hábitos y Disciplina* — Ritmo circadiano, dopamina, rutinas\n"
        "6️⃣ *Estética y Salud Regenerativa* — Piel, cabello, visión\n\n"
        "Pregúntame sobre cualquiera de estos temas 🧬",
        parse_mode="Markdown",
    )


async def cmd_agenda(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Muestra la agenda de la semana."""
    if not await _is_owner(update):
        return
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    summary = await calendar_service.get_agenda_summary_async(days=7)
    await update.message.reply_text(summary, parse_mode="Markdown")


async def cmd_tareas(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Muestra las tareas pendientes."""
    if not await _is_owner(update):
        return
    user_id = update.effective_user.id
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    task_list = await asyncio.to_thread(tasks.get_tasks, user_id, True)
    msg = tasks.format_tasks_list(task_list)
    await update.message.reply_text(msg, parse_mode="Markdown")


# ── Handler de mensajes principales ──────────────────────────────────────────
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Procesa cualquier mensaje de texto y responde con Gemini."""
    if not await _is_owner(update):
        return
    user_id = update.effective_user.id
    user_text = update.message.text

    # Recuperar historial desde Firebase (o fallback en memoria)
    firebase_history = await asyncio.to_thread(memory.build_gemini_history, user_id)
    if firebase_history:
        history = firebase_history
    else:
        history = _conversation_history.get(user_id, [])

    # Indicador de "escribiendo..."
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id, action="typing"
    )

    try:
        # 🔍 RAG: buscar contexto relevante del Dr. La Rosa
        rag_context = await asyncio.to_thread(rag.search, user_text)

        # 📅 Calendar: obtener agenda actual para contexto
        agenda_context = await calendar_service.get_agenda_summary_async(days=3)

        # ✅ Tareas: resumen de pendientes
        tasks_context = await asyncio.to_thread(tasks.get_tasks_summary, user_id)

        # Construir el mensaje enriquecido
        parts = []
        if rag_context:
            parts.append(rag_context)
        if agenda_context:
            parts.append(agenda_context)
        if tasks_context:
            parts.append(tasks_context)
        parts.append(f"## Consulta del usuario:\n{user_text}")
        enriched_prompt = "\n\n".join(parts)

        # Gemini chat con historial — llamada síncrona envuelta en thread
        chat = _gemini_model.start_chat(history=history)
        response = await asyncio.to_thread(chat.send_message, enriched_prompt)
        bot_reply = response.text

        # 💾 Guardar turno en Firebase RTDB
        await asyncio.to_thread(memory.save_message, user_id, "user", user_text)
        await asyncio.to_thread(memory.save_message, user_id, "model", bot_reply)
        # Fallback en memoria para compatibilidad
        _conversation_history[user_id] = chat.history

        await update.message.reply_text(bot_reply, parse_mode="Markdown")

    except Exception as e:
        logger.error(f"Error en handle_message: {e}")
        await update.message.reply_text(
            "⚠️ Tuve un problema procesando tu consulta. Intenta de nuevo en un momento."
        )


# ── Error handler global ──────────────────────────────────────────────────────
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(f"Update {update!r} causó el error: {context.error!r}")


async def cmd_brief(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Dispara el brief matutino ahora (para testing)."""
    if not await _is_owner(update):
        return
    await update.message.reply_text("⏳ Generando tu brief matutino...")
    await scheduler.fire_morning_brief_now()


async def cmd_checkin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Dispara el check-in nocturno ahora (para testing)."""
    if not await _is_owner(update):
        return
    await update.message.reply_text("⏳ Generando check-in nocturno...")
    await scheduler.fire_evening_checkin_now()


# ── Bootstrap ─────────────────────────────────────────────────────────────────
def run() -> None:
    """Punto de entrada principal del bot."""
    if not TELEGRAM_BOT_TOKEN:
        raise ValueError("❌ TELEGRAM_BOT_TOKEN no está configurado en el .env")
    if not GEMINI_API_KEY:
        raise ValueError("❌ GEMINI_API_KEY no está configurado en el .env")

    logger.info(f"🚀 {BOT_NAME} iniciado. Escuchando mensajes...")

    # Indexar knowledge base al arrancar (async, sin bloquear el bot)
    async def _post_init(application):
        # RAG
        logger.info("🧠 Iniciando indexación RAG en segundo plano...")
        n = await rag.build_index_async()
        if n > 0:
            logger.info(f"✅ RAG listo: {n} chunks indexados.")
        else:
            logger.warning("⚠️ RAG no disponible.")
        # Scheduler de proactividad
        scheduler.init_scheduler(application)
        logger.info("✅ Scheduler de proactividad activo.")

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).post_init(_post_init).build()

    # Comandos
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("reset", cmd_reset))
    app.add_handler(CommandHandler("pilares", cmd_pilares))
    app.add_handler(CommandHandler("agenda", cmd_agenda))
    app.add_handler(CommandHandler("tareas", cmd_tareas))
    app.add_handler(CommandHandler("brief", cmd_brief))
    app.add_handler(CommandHandler("checkin", cmd_checkin))

    # Mensajes de texto
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Error global
    app.add_error_handler(error_handler)

    logger.info(f"🚀 {BOT_NAME} iniciado. Escuchando mensajes...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    run()
