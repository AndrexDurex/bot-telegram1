import socket
import sys

# --- DNS WORKAROUND CRÍTICO PARA HUGGING FACE ---
# api.telegram.org -> 149.154.167.220
def _patched_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    if host == "api.telegram.org":
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, '', ('149.154.167.220', int(port)))]
    return socket._orig_getaddrinfo(host, port, family, type, proto, flags)

if not hasattr(socket, "_orig_getaddrinfo"):
    socket._orig_getaddrinfo = socket.getaddrinfo
    socket.getaddrinfo = _patched_getaddrinfo
    print("--- [WORKAROUND] DNS Monkeypatch (app.py) ACTIVADO ---", flush=True)

import os
import subprocess

if __name__ == "__main__":
    print("Starting BioAgent from app.py wrapper...")
    subprocess.run(["python", "main.py"])
