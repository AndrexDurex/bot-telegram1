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
    print(f"--- DIAGNOSTICO STARTUP ---")
    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    print(f"TELEGRAM_BOT_TOKEN length: {len(token)}")
    print(f"TELEGRAM_BOT_TOKEN starts with: {token[:4]}...")
    
    try:
        print("Probando resolucion DNS para api.telegram.org...")
        addr = socket.gethostbyname("api.telegram.org")
        print(f"✅ DNS OK: api.telegram.org -> {addr}")
    except Exception as e:
        print(f"❌ ERROR DNS: {e}")

    try:
        print("Probando conexion a port 443 de api.telegram.org...")
        s = socket.create_connection(("api.telegram.org", 443), timeout=5)
        s.close()
        print("✅ CONEXION TCP OK")
    except Exception as e:
        print(f"❌ ERROR CONEXION: {e}")
    print(f"---------------------------")
    run()

