import socket
import sys

# --- DNS WORKAROUND CRÍTICO PARA HUGGING FACE ---
# api.telegram.org -> 149.154.167.220
def _patched_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    if host and ("api.telegram.org" in host or "telegram.org" in host):
        # Retornamos la IP que si funciona en HF
        return [(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP, '', ('149.154.167.220', int(port)))]
    return socket._orig_getaddrinfo(host, port, family, type, proto, flags)

if not hasattr(socket, "_orig_getaddrinfo"):
    socket._orig_getaddrinfo = socket.getaddrinfo
    socket.getaddrinfo = _patched_getaddrinfo

# También parchamos gethostbyname
_orig_gethostbyname = socket.gethostbyname
def _patched_gethostbyname(host):
    if host and ("api.telegram.org" in host or "telegram.org" in host):
        return "149.154.167.220"
    return _orig_gethostbyname(host)
socket.gethostbyname = _patched_gethostbyname

print("--- [WORKAROUND] DNS Monkeypatch V2.5 ACTIVADO ---", flush=True)
# ---------------------------------------------

import logging
import os
from bioagent.startup import prepare_credentials
from bioagent.bot import run

if __name__ == "__main__":
    print("--- DIAGNOSTICO STARTUP V2.3 ---", flush=True)
    token = os.getenv("TELEGRAM_BOT_TOKEN", "" )
    print(f"TELEGRAM_BOT_TOKEN length: {len(token)}", flush=True)
    
    # Preparar credenciales decodificando desde b64
    prepare_credentials()
    
    # Pruebas finales de diagnostico
    try:
        print("Probando resolucion DNS parchada para api.telegram.org...", flush=True)
        addr = socket.gethostbyname("api.telegram.org")
        print(f"✅ DNS PARCHADO: api.telegram.org -> {addr}", flush=True)
    except Exception as e:
        print(f"❌ ERROR DNS PARCHADO: {e}", flush=True)

    try:
        print("Probando conexion TCP a api.telegram.org:443...", flush=True)
        s = socket.create_connection(("api.telegram.org", 443), timeout=5)
        s.close()
        print("✅ CONEXION TCP api.telegram.org OK", flush=True)
    except Exception as e:
        print(f"❌ ERROR CONEXION TCP PARCHADA: {e}", flush=True)

    print("--- FIN DIAGNOSTICO V2.3 (Bot arrancando...) ---", flush=True)
    sys.stdout.flush()
    run()
