import os
import sys
import socket
from pathlib import Path
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import functools

class FastHTTPRequestHandler(SimpleHTTPRequestHandler):
    def address_string(self):
        # Tranh bi treo boi reverse DNS lookup tren Windows
        return str(self.client_address[0])

    def end_headers(self):
        # Cho phep cache hop ly va ho tro CORS
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()

class DualStackServer(ThreadingHTTPServer):
    address_family = socket.AF_INET6
    def server_bind(self):
        try:
            self.socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
        except Exception:
            pass
        return super().server_bind()

def main():
    port = 5500
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass

    frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
    handler = functools.partial(FastHTTPRequestHandler, directory=str(frontend_dir))

    try:
        server = DualStackServer(('::', port), handler)
    except Exception:
        # Fallback neu IPv6 khong kha dung
        server = ThreadingHTTPServer(('0.0.0.0', port), handler)

    print(f"==================================================")
    print(f" Frontend server dang chay tai:")
    print(f"   -> http://localhost:{port}/html/public/index.html")
    print(f"   -> http://127.0.0.1:{port}/html/public/index.html")
    print(f"==================================================")
    print("Nhan Ctrl+C de dung server.\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nDang dung Frontend server...")
    finally:
        server.server_close()

if __name__ == "__main__":
    main()
