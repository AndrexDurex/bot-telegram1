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

    # Probar DNS Telegram (Forzando IPv4)
    try:
        print("Probando resolucion DNS (AF_INET) para api.telegram.org...", flush=True)
        # Forzar IPv4
        info = socket.getaddrinfo("api.telegram.org", 443, family=socket.AF_INET)
        addr = info[0][4][0]
        print(f"✅ DNS TELEGRAM IPv4 OK: api.telegram.org -> {addr}", flush=True)
    except Exception as e:
        print(f"❌ ERROR DNS TELEGRAM IPv4: {e}", flush=True)

    # Si el anterior fallo, probar con un DNS provider explicito (opcional si tenemos dnspython)
    # Por ahora solo intentaremos ver si el error persiste con AF_INET.

    # Probar conexion TCP directa a IP de Telegram (saltando DNS)
    try:
        tg_ip = "149.154.167.220" # Una de las IPs de api.telegram.org
        print(f"Probando conexion TCP a {tg_ip}:443 (Telegram IP)...", flush=True)
        s = socket.create_connection((tg_ip, 443), timeout=5)
        s.close()
        print(f"✅ CONEXION TCP {tg_ip} OK (Red permite Telegram por IP)", flush=True)
    except Exception as e:
        print(f"❌ ERROR CONEXION IP {tg_ip}: {e}", flush=True)

    print("--- FIN DIAGNOSTICO ---", flush=True)
    sys.stdout.flush()
    run()

