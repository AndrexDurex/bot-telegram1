#!/usr/bin/env python
"""
Punto de entrada para ejecutar el BioAgent bot.
Uso: python main.py
"""
from bioagent.startup import prepare_credentials

# Restaurar credenciales desde HF Secrets (no-op en local)
prepare_credentials()

from bioagent.bot import run

if __name__ == "__main__":
    import socket
    import os
    import sys
    print("--- DIAGNOSTICO STARTUP ---", flush=True)
    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    print(f"TELEGRAM_BOT_TOKEN length: {len(token)}", flush=True)
    if token:
        print(f"TELEGRAM_BOT_TOKEN starts with: {token[:5]}...", flush=True)
    else:
        print("❌ TELEGRAM_BOT_TOKEN is EMPTY or UNSET", flush=True)
    
    # Probar DNS externo (Google)
    try:
        print("Probando resolucion DNS para google.com...", flush=True)
        addr = socket.gethostbyname("google.com")
        print(f"✅ DNS GOOGLE OK: google.com -> {addr}", flush=True)
    except Exception as e:
        print(f"❌ ERROR DNS GOOGLE: {e}", flush=True)

    # Probar DNS Telegram
    try:
        print("Probando resolucion DNS para api.telegram.org...", flush=True)
        addr = socket.gethostbyname("api.telegram.org")
        print(f"✅ DNS TELEGRAM OK: api.telegram.org -> {addr}", flush=True)
    except Exception as e:
        print(f"❌ ERROR DNS TELEGRAM: {e}", flush=True)

    # Probar conexion TCP
    try:
        print("Probando conexion TCP a 8.8.8.8:53 (Google DNS)...", flush=True)
        s = socket.create_connection(("8.8.8.8", 53), timeout=5)
        s.close()
        print("✅ CONEXION TCP 8.8.8.8 OK", flush=True)
    except Exception as e:
        print(f"❌ ERROR CONEXION 8.8.8.8: {e}", flush=True)

    print("--- FIN DIAGNOSTICO ---", flush=True)
    sys.stdout.flush()
    run()

