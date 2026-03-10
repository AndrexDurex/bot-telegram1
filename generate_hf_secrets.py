"""
Script de ayuda: genera los secrets en base64 para Hugging Face Spaces.
Ejecutar UNA VEZ localmente: python generate_hf_secrets.py
Luego copia los valores a los HF Secrets de tu Space.
"""
import base64
import json

files = {
    "FIREBASE_CREDENTIALS_B64": "firebase-credentials.json",
    "GOOGLE_CALENDAR_TOKEN_B64": "calendar_token.json",
}

print("=" * 60)
print("🔐 Secrets para Hugging Face Spaces")
print("Copia cada valor en la configuración de tu Space.")
print("=" * 60)

for secret_name, filename in files.items():
    try:
        with open(filename, "rb") as f:
            content = f.read()
        encoded = base64.b64encode(content).decode("utf-8")
        print(f"\n✅ {secret_name}:")
        print(encoded)
    except FileNotFoundError:
        print(f"\n❌ {filename} no encontrado.")

print("\n" + "=" * 60)
print("📋 También configura estos secrets con sus valores directos:")
print("  TELEGRAM_BOT_TOKEN")
print("  OWNER_CHAT_ID")
print("  GEMINI_API_KEY")
print("  GEMINI_MODEL=models/gemini-2.5-flash")
print("  FIREBASE_PROJECT_ID")
print("  FIREBASE_RTDB_URL")
print("  GITHUB_TOKEN")
print("  GITHUB_REPO")
print("  GOOGLE_CALENDAR_ID=primary")
print("  CHROMA_PERSIST_DIR=./chroma_db")
print("=" * 60)
