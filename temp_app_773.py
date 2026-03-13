import socket
import sys

# --- DNS WORKAROUND V3.0 (Host Swapping) ---
if not hasattr(socket, "_orig_getaddrinfo"):
    socket._orig_getaddrinfo = socket.getaddrinfo
    def _patched_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
        try:
            if host:
                h = host.decode() if isinstance(host, bytes) else host
                if "api.telegram.org" in h:
                    host = "149.154.167.220"
        except:
            pass
        return socket._orig_getaddrinfo(host, port, family, type, proto, flags)
    socket.getaddrinfo = _patched_getaddrinfo

import os
import subprocess

if __name__ == "__main__":
    print("--- [WORKAROUND] DNS Host-Swap (app.py) ACTIVADO ---", flush=True)
    subprocess.run(["python", "main.py"])
