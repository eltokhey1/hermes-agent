"""Loopback-only read-only TradeDocs pilot API. No external integrations."""
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pilot_workflow import run
from email_triage import classify_message
from pathlib import Path

MAX_REQUEST = 100_000

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.client_address[0] not in ("127.0.0.1", "::1") or self.headers.get("Host") != f"127.0.0.1:{self.server.server_address[1]}":
            self.send_error(403, "Local host only")
            return
        if self.path not in ("/review", "/triage"):
            self.send_error(404)
            return
        try:
            size = int(self.headers.get("Content-Length", "-1"))
            if not 0 < size <= MAX_REQUEST:
                self.send_error(413, "Invalid request size")
                return
            if self.headers.get("Origin") not in (None, f"http://127.0.0.1:{self.server.server_address[1]}"):
                self.send_error(403, "Origin not allowed")
                return
            if self.headers.get("Content-Type", "").split(";", 1)[0].strip().lower() != "application/json":
                self.send_error(415, "Expected JSON")
                return
            payload = json.loads(self.rfile.read(size))
            result = classify_message(payload) if self.path == "/triage" else run(payload)
            body = json.dumps(result, ensure_ascii=False).encode("utf-8")
            status = 200
        except (ValueError, KeyError, TypeError, json.JSONDecodeError):
            body = b'{"error":"INVALID_REVIEW_INPUT"}'
            status = 400
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.client_address[0] not in ("127.0.0.1", "::1") or self.headers.get("Host") != f"127.0.0.1:{self.server.server_address[1]}":
            self.send_error(403, "Local host only")
            return
        if self.path == "/":
            body = Path(__file__).with_name("global_pilot.html").read_bytes()
            content_type = "text/html; charset=utf-8"
        elif self.path == "/health":
            body = b'{"status":"LOCAL_REVIEW_ONLY"}'
            content_type = "application/json"
        else:
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", 8765), Handler)
    print("TradeDocs review API on http://127.0.0.1:8765 (loopback only)")
    server.serve_forever()
