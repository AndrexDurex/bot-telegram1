"""
Script de autenticación OAuth para Google Calendar.
Ejecutar UNA SOLA VEZ: python auth_calendar.py
Genera calendar_token.json con el refresh_token persistente.
"""
import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import json

SCOPES = ["https://www.googleapis.com/auth/calendar"]
CREDENTIALS_FILE = "google_credentials.json"
TOKEN_FILE = "calendar_token.json"


def main():
    creds = None

    # Si ya existe un token válido, usarlo
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    # Si no hay creds válidas, arrancar el flujo OAuth
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            print("✅ Token renovado automáticamente.")
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
            print("✅ Autenticación exitosa.")

        # Guardar token para uso futuro
        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())
        print(f"💾 Token guardado en: {TOKEN_FILE}")

    # Verificar que funciona listando próximos eventos
    from googleapiclient.discovery import build
    service = build("calendar", "v3", credentials=creds)
    events_result = service.events().list(
        calendarId="primary",
        maxResults=3,
        singleEvents=True,
        orderBy="startTime",
    ).execute()
    events = events_result.get("items", [])

    print(f"\n📅 Próximos {len(events)} eventos en tu calendario:")
    for e in events:
        start = e["start"].get("dateTime", e["start"].get("date"))
        print(f"  • {start} — {e.get('summary', 'Sin título')}")

    if not events:
        print("  (No hay eventos próximos)")

    print("\n🎉 ¡Configuración de Google Calendar completada!")


if __name__ == "__main__":
    main()
