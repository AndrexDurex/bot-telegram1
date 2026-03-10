"""
BioAgent — Módulo de gestión de tareas con Firebase RTDB.
Guarda/recupera/actualiza tareas del usuario.

Estructura en RTDB:
  users/{user_id}/tasks/{task_id}/
    title: str
    done: bool
    priority: "alta"|"media"|"baja"
    category: str  (salud, tesis, lab, general, etc.)
    due_date: str|None  (ISO date)
    notes: str
    created_at: int (timestamp)
"""
import logging
import time
from typing import Optional

from firebase_admin import db

from bioagent.memory import _init_firebase

logger = logging.getLogger(__name__)


def add_task(
    user_id: int,
    title: str,
    priority: str = "media",
    category: str = "general",
    due_date: Optional[str] = None,
    notes: str = "",
) -> Optional[str]:
    """
    Crea una nueva tarea. Retorna el task_id o None si falla.
    """
    if not _init_firebase():
        return None
    try:
        ref = db.reference(f"users/{user_id}/tasks")
        task = {
            "title": title,
            "done": False,
            "priority": priority,
            "category": category,
            "due_date": due_date or "",
            "notes": notes,
            "created_at": int(time.time()),
        }
        result = ref.push(task)
        logger.info(f"✅ Tarea creada: {title} ({result.key})")
        return result.key
    except Exception as e:
        logger.error(f"❌ add_task error: {e}")
        return None


def get_tasks(user_id: int, only_pending: bool = True) -> list[dict]:
    """
    Retorna las tareas del usuario.
    Cada tarea incluye 'id' además de sus datos.
    """
    if not _init_firebase():
        return []
    try:
        ref = db.reference(f"users/{user_id}/tasks")
        data = ref.order_by_child("created_at").get()
        if not data:
            return []
        tasks = []
        for task_id, task_data in data.items():
            if only_pending and task_data.get("done", False):
                continue
            tasks.append({"id": task_id, **task_data})
        # Ordenar: alta → media → baja
        priority_order = {"alta": 0, "media": 1, "baja": 2}
        tasks.sort(key=lambda t: priority_order.get(t.get("priority", "media"), 1))
        return tasks
    except Exception as e:
        logger.error(f"❌ get_tasks error: {e}")
        return []


def complete_task(user_id: int, task_id: str) -> bool:
    """Marca una tarea como completada."""
    if not _init_firebase():
        return False
    try:
        ref = db.reference(f"users/{user_id}/tasks/{task_id}")
        ref.update({"done": True, "completed_at": int(time.time())})
        logger.info(f"✅ Tarea completada: {task_id}")
        return True
    except Exception as e:
        logger.error(f"❌ complete_task error: {e}")
        return False


def delete_task(user_id: int, task_id: str) -> bool:
    """Elimina una tarea permanentemente."""
    if not _init_firebase():
        return False
    try:
        db.reference(f"users/{user_id}/tasks/{task_id}").delete()
        return True
    except Exception as e:
        logger.error(f"❌ delete_task error: {e}")
        return False


def format_tasks_list(tasks: list[dict]) -> str:
    """Formatea la lista de tareas para mostrar en Telegram."""
    if not tasks:
        return "✅ No tienes tareas pendientes."

    priority_emoji = {"alta": "🔴", "media": "🟡", "baja": "🟢"}
    lines = ["📋 *Tareas pendientes:*\n"]
    for i, t in enumerate(tasks, 1):
        emoji = priority_emoji.get(t.get("priority", "media"), "⚪")
        title = t.get("title", "Sin título")
        cat = t.get("category", "")
        due = t.get("due_date", "")
        line = f"{emoji} {i}. {title}"
        if cat and cat != "general":
            line += f" _[{cat}]_"
        if due:
            line += f" — 📆 {due}"
        lines.append(line)
    return "\n".join(lines)


def get_tasks_summary(user_id: int) -> str:
    """Resumen de tareas para inyectar en el prompt de Gemini."""
    tasks = get_tasks(user_id, only_pending=True)
    if not tasks:
        return ""
    lines = ["## Tareas pendientes del usuario:"]
    for t in tasks[:8]:  # máximo 8 para no saturar el prompt
        priority = t.get("priority", "media")
        title = t.get("title", "")
        due = t.get("due_date", "")
        cat = t.get("category", "general")
        line = f"- [{priority}] {title} (cat: {cat})"
        if due:
            line += f" vence: {due}"
        lines.append(line)
    return "\n".join(lines)
