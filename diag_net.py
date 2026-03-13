import socket
import os
import sys

def check_dns(host):
    print(f"--- Checking DNS for {host} ---")
    try:
        addr = socket.gethostbyname(host)
        print(f"✅ gethostbyname({host}) -> {addr}")
    except Exception as e:
        print(f"❌ gethostbyname({host}) failed: {e}")

    try:
        info = socket.getaddrinfo(host, 443)
        print(f"✅ getaddrinfo({host}, 443) -> {info[0][4][0]} (Family: {info[0][0]})")
    except Exception as e:
        print(f"❌ getaddrinfo({host}, 443) failed: {e}")

    try:
        info = socket.getaddrinfo(host, 443, family=socket.AF_INET)
        print(f"✅ getaddrinfo({host}, 443, AF_INET) -> {info[0][4][0]}")
    except Exception as e:
        print(f"❌ getaddrinfo({host}, 443, AF_INET) failed: {e}")

def check_tcp(ip, port=443):
    print(f"--- Checking TCP Connection to {ip}:{port} ---")
    try:
        s = socket.create_connection((ip, port), timeout=5)
        s.close()
        print(f"✅ Connection to {ip}:{port} SUCCESS")
    except Exception as e:
        print(f"❌ Connection to {ip}:{port} FAILED: {e}")

if __name__ == "__main__":
    print("--- NETWORK DIAGNOSTIC ---")
    check_dns("google.com")
    check_dns("huggingface.co")
    check_dns("api.telegram.org")
    
    # Common Telegram IPs
    check_tcp("149.154.167.220") # api.telegram.org
    
    print("\n--- ENVIRONMENT VARIABLES ---")
    for k, v in os.environ.items():
        if any(x in k.lower() for x in ["proxy", "host", "dns", "url"]):
            print(f"{k}: {v}")
