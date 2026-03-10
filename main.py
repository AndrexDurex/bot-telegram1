import socket
import sys

# --- DNS WORKAROUND V3.0 (Host Swapping) ---
# Resolvemos api.telegram.org -> 149.154.167.220 internamente.
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

if not hasattr(socket, "_orig_gethostbyname"):
    socket._orig_gethostbyname = socket.gethostbyname
    def _patched_gethostbyname(host):
        if host and "api.telegram.org" in host:
            return "149.154.167.220"
        return socket._orig_gethostbyname(host)
    socket.gethostbyname = _patched_gethostbyname

print("--- [WORKAROUND] DNS Host-Swap V3.0 ACTIVADO ---", flush=True)

import logging
import os
from bioagent.startup import prepare_credentials
from bioagent.bot import run

if __name__ == "__main__":
    print("--- STARTUP BIOAGENT V3.0 ---", flush=True)
    prepare_credentials()
    sys.stdout.flush()
    run()
