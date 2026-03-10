"""
BioAgent — Módulo de proactividad con APScheduler.
El bot envía mensajes a André sin que él los inicie.

Horarios por defecto (America/Lima):
  07:00 — Resumen matutino: agenda del día + tip del Dr. La Rosa
  21:00 — Check-in nocturno: revisión de tareas + motivación

El usuario puede cambiar los horarios diciéndole al bot.
"""
import asyncio
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from bioagent.config import OWNER_CHAT_ID
from bioagent import calendar_service, tasks
from bioagent import rag

logger = logging.getLogger(__name__)

TZ = ZoneInfo("America/Lima")

# Scheduler global (singleton)
_scheduler: AsyncIOScheduler | None = None
_bot_app = None   # referencia a la Application de telegram


def init_scheduler(app) -> AsyncIOScheduler:
    """Inicializa y arranca el scheduler con los jobs por defecto."""
    global _scheduler, _bot_app
    _bot_app = app

    _scheduler = AsyncIOScheduler(timezone=TZ)

    # ── Resumen matutino — 7:00 AM ────────────────────────────────────────────
    _scheduler.add_job(
        _morning_brief,
        CronTrigger(hour=7, minute=0, timezone=TZ),
        id="morning_brief",
        replace_existing=True,
    )

    # ── Check-in nocturno — 9:00 PM ──────────────────────────────────────────
    _scheduler.add_job(
        _evening_checkin,
        CronTrigger(hour=21, minute=0, timezone=TZ),
        id="evening_checkin",
        replace_existing=True,
    )

    _scheduler.start()
    logger.info("⏰ Scheduler de proactividad iniciado (07:00 y 21:00 Lima).")
    return _scheduler


async def _send_to_owner(message: str) -> None:
    """Envía un mensaje proactivo al dueño del bot."""
    if not _bot_app:
        logger.warning("⚠️ Scheduler: bot_app no inicializado.")
        return
    try:
        await _bot_app.bot.send_message(
            chat_id=OWNER_CHAT_ID,
            text=message,
            parse_mode="Markdown",
        )
    except Exception as e:
        logger.error(f"❌ Error enviando mensaje proactivo: {e}")


async def _morning_brief() -> None:
    """Resumen matutino: agenda del día + tareas pendientes + tip de salud."""
    logger.info("🌅 Ejecutando resumen matutino...")
    now = datetime.now(TZ)
    weekday = now.strftime("%A")
    date_str = now.strftime("%d/%m/%Y")

    # Obtener agenda de hoy
    agenda = await asyncio.to_thread(
        calendar_service.get_upcoming_events, 1, 5
    )

    # Obtener tareas pendientes de alta prioridad
    all_tasks = await asyncio.to_thread(tasks.get_tasks, OWNER_CHAT_ID, True)
    urgent_tasks = [t for t in all_tasks if t.get("priority") == "alta"]

    # Obtener tip de salud del RAG
    rag_tip = await asyncio.to_thread(
        rag.search, "consejo de salud importante para comenzar el día"
    )

    lines = [
        f"🌅 *Buenos días André!* — {weekday} {date_str}\n",
    ]

    # Agenda
    if agenda:
        lines.append("📅 *Tu agenda de hoy:*")
        for e in agenda:
            start = e["start"].replace("T", " ").split("+")[0][11:16]
            lines.append(f"  • {start}h — {e['title']}")
    else:
        lines.append("📅 Agenda libre hoy — buen día para avanzar con tus objetivos.")

    lines.append("")

    # Tareas urgentes
    if urgent_tasks:
        lines.append("🔴 *Tareas urgentes pendientes:*")
        for t in urgent_tasks[:3]:
            lines.append(f"  • {t['title']}")
        lines.append("")

    # Tip del Dr. La Rosa (solo el primer fragmento)
    if rag_tip:
        # Extraer un tip corto del contexto RAG
        lines.append("💡 *Tip del día (Dr. La Rosa):*")
        tip_text = rag_tip.split("\n")[2:5]  # primeras líneas del contexto
        tip_clean = " ".join(tip_text).strip()[:200]
        if tip_clean:
            lines.append(f"_{tip_clean}..._")
        lines.append("")

    lines.append("_¿Listo para conquistar el día? 💪_")

    await _send_to_owner("\n".join(lines))


async def _evening_checkin() -> None:
    """Check-in nocturno: resumen de lo pendiente + motivación."""
    logger.info("🌙 Ejecutando check-in nocturno...")
    now = datetime.now(TZ)

    # Tareas pendientes
    all_tasks = await asyncio.to_thread(tasks.get_tasks, OWNER_CHAT_ID, True)
    total = len(all_tasks)
    high = [t for t in all_tasks if t.get("priority") == "alta"]

    # Agenda de mañana
    tomorrow_events = await asyncio.to_thread(
        calendar_service.get_upcoming_events, 2, 5
    )
    # Filtrar solo los de mañana
    tomorrow_str = now.strftime("%Y-%m-%d")

    lines = [
        "🌙 *Check-in nocturno*\n",
        "¿Cómo fue tu día? Aquí va el resumen:\n",
    ]

    if total > 0:
        lines.append(f"📋 Tienes *{total} tarea(s) pendiente(s)*")
        if high:
            lines.append(f"  ↳ {len(high)} de alta prioridad:")
            for t in high[:2]:
                lines.append(f"     • {t['title']}")
    else:
        lines.append("✅ *No tienes tareas pendientes* — ¡excelente día!")

    lines.append("")

    if tomorrow_events:
        lines.append("📅 *Mañana te espera:*")
        for e in tomorrow_events[:3]:
            start = e["start"].replace("T", " ").split("+")[0][11:16]
            lines.append(f"  • {start}h — {e['title']}")
        lines.append("")

    lines.append(
        "💤 Recuerda: *el sueño es el suplemento #1* del Dr. La Rosa.\n"
        "Apaga pantallas 30 min antes. Mañana lo retomamos 🙌"
    )

    await _send_to_owner("\n".join(lines))


async def fire_morning_brief_now() -> None:
    """Dispara el brief matutino inmediatamente (para testing)."""
    await _morning_brief()


async def fire_evening_checkin_now() -> None:
    """Dispara el check-in nocturno inmediatamente (para testing)."""
    await _evening_checkin()
