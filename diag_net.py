import socket
import os
import sys

def run_diagnostic():
    print("\n" + "="*40)
    print("      NETWORK DIAGNOSTIC REPORT")
    print("="*40)
    
    hosts = ["google.com", "huggingface.co", "api.telegram.org", "github.com"]
    
    for host in hosts:
        print(f"\n--- DNS: {host} ---")
        try:
            addr = socket.gethostbyname(host)
            print(f"✅ gethostbyname -> {addr}")
        except Exception as e:
            print(f"❌ gethostbyname failed: {e}")

        try:
            # Test default getaddrinfo
            info = socket.getaddrinfo(host, 443)
            print(f"✅ getaddrinfo(default) -> {info[0][4][0]} (Family: {info[0][0]})")
        except Exception as e:
            print(f"❌ getaddrinfo(default) failed: {e}")

        try:
            # Test AF_INET
            info = socket.getaddrinfo(host, 443, family=socket.AF_INET)
            print(f"✅ getaddrinfo(AF_INET) -> {info[0][4][0]}")
        except Exception as e:
            print(f"❌ getaddrinfo(AF_INET) failed: {e}")

    print("\n--- TCP CONNECTION TESTS ---")
    ips = {
        "149.154.167.220": "api.telegram.org",
        "1.1.1.1": "Cloudflare DNS",
        "8.8.8.8": "Google DNS"
    }
    for ip, desc in ips.items():
        try:
            s = socket.create_connection((ip, 443), timeout=3)
            s.close()
            print(f"✅ Connection to {ip} ({desc}) SUCCESS")
        except Exception as e:
            print(f"❌ Connection to {ip} ({desc}) FAILED: {e}")

    print("\n--- PROXY / ENVIRONMENT ---")
    relevant_vars = ["HTTP_PROXY", "HTTPS_PROXY", "NO_PROXY", "ALL_PROXY", "HF_HUB_DISABLE_IMPLICIT_TOKEN"]
    for var in relevant_vars:
        val = os.environ.get(var)
        if val:
            print(f"🔍 {var}: {val}")
        else:
            print(f"🔍 {var}: (not set)")

    print("="*40 + "\n")

if __name__ == "__main__":
    run_diagnostic()
