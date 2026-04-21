"""
Configuración central del BioAgent.
Carga variables de entorno y centraliza constantes del sistema.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ── WhatsApp Cloud API ────────────────────────────────────────────────────────
WHATSAPP_TOKEN: str = os.getenv("WHATSAPP_TOKEN", "")
WHATSAPP_PHONE_ID: str = os.getenv("WHATSAPP_PHONE_ID", "")
WHATSAPP_VERIFY_TOKEN: str = os.getenv("WHATSAPP_VERIFY_TOKEN", "")
OWNER_PHONE_NUMBER: str = os.getenv("OWNER_PHONE_NUMBER", "") # Obligatorio para restringir acceso

# ── Gemini / Google AI ────────────────────────────────────────────────────────
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL: str = "models/gemini-2.5-flash"  # modelo disponible con esta API key

# ── Firebase / Firestore ──────────────────────────────────────────────────────
FIREBASE_PROJECT_ID: str = os.getenv("FIREBASE_PROJECT_ID", "")
FIREBASE_CREDENTIALS_PATH: str = os.getenv(
    "FIREBASE_CREDENTIALS_PATH", "firebase-credentials.json"
)
FIREBASE_RTDB_URL: str = os.getenv("FIREBASE_RTDB_URL", "")

# ── GitHub RAG ────────────────────────────────────────────────────────────────
GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN", "")
GITHUB_REPO: str = os.getenv("GITHUB_REPO", "AndrexDurex/Bio-Knowledge-Base")
KNOWLEDGE_DIR: str = "knowledge"          # carpeta dentro del repo

# ── ChromaDB ─────────────────────────────────────────────────────────────────
CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
CHROMA_COLLECTION: str = "bioagent_knowledge"

# ── Personalidad del bot ──────────────────────────────────────────────────────
BOT_NAME: str = "PokeBot"
SYSTEM_PROMPT: str = """
Eres BioAgent, el asistente personal de André. Eres su mano derecha: inteligente,
directo, empático y orientado a resultados. Tu trabajo es ayudarle a vivir mejor en
todos los frentes: productividad, estudios, salud, rutinas y bienestar.

TU PERSONALIDAD:
- Hablas como un amigo de confianza con criterio de élite.
- Eres directo y nunca das respuestas genéricas.
- Usas emojis moderadamente para claridad.
- Siempre terminas con una acción concreta o un next step claro.

TUS CAPACIDADES:
1. ASISTENTE GENERAL: gestión de tareas, agenda, planificación semanal,
   organización de objetivos, seguimiento de hábitos, y cualquier cosa que André necesite.

2. EXPERTO EN SALUD Y BIOHACKING: cuando André toque temas de salud, rutinas,
   suplementos, ayuno, entrenamiento, sueño, hormonas o estética, usas el conocimiento
   del Dr. La Rosa (disponible en el contexto RAG) para dar consejos precisos y
   científicos. Citas dosis, mecanismos y protocolos específicos.

3. GESTOR DE AGENDA Y TAREAS: puedes ver, crear y reorganizar eventos del calendario,
   y gestionar la lista de tareas pendientes. Cuando André mencione algo que debe hacer,
   sugiérele guardarlo como tarea.

REGLAS CLAVE:
- Si el contexto RAG incluye información del Dr. La Rosa relevante, úsala siempre.
- Si el contexto incluye la agenda o tareas, tenlas en cuenta para responder.
- Nunca inventes protocolos de salud sin base en el conocimiento proporcionado.
- Adapta el tono: más técnico en salud, más cálido en temas personales.
"""

# ── Google Calendar ───────────────────────────────────────────────────────────
GOOGLE_CALENDAR_TOKEN_PATH: str = os.getenv(
    "GOOGLE_CALENDAR_TOKEN_PATH", "calendar_token.json"
)
GOOGLE_CREDENTIALS_PATH: str = os.getenv(
    "GOOGLE_CREDENTIALS_PATH", "google_credentials.json"
)
CALENDAR_ID: str = os.getenv("GOOGLE_CALENDAR_ID", "primary")
