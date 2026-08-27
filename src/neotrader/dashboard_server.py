from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import hmac
import json
import os
from pathlib import Path

from .operator import OperatorStore


class DashboardHandler(BaseHTTPRequestHandler):
    store = OperatorStore()
    root = Path(__file__).resolve().parents[2] / "dashboard" / "index.html"
    operator_token = os.getenv("NEOTRADER_OPERATOR_TOKEN", "")

    def _authorized(self) -> bool:
        if not self.operator_token:
            return True
        supplied = self.headers.get("X-NeoTrader-Token", "")
        return hmac.compare_digest(supplied, self.operator_token)

    def _json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path == "/health":
            self._json(200, {"status": "ok", "paper_only": True})
            return
        if self.path.startswith("/api/") and not self._authorized():
            self._json(401, {"error": "unauthorized"})
            return
        if self.path == "/api/status":
            self._json(200, self.store.snapshot())
            return
        if self.path in {"/", "/index.html"}:
            body = self.root.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        self.send_error(404)

    def do_POST(self) -> None:
        if not self._authorized():
            self._json(401, {"error": "unauthorized"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length) or b"{}")
        except (ValueError, json.JSONDecodeError):
            self._json(400, {"error": "invalid_json"})
            return
        if self.path == "/api/control/enabled":
            self._json(200, self.store.set_enabled(bool(payload.get("enabled"))).__dict__)
            return
        if self.path == "/api/control/kill-switch":
            self._json(200, self.store.set_kill_switch(bool(payload.get("active"))).__dict__)
            return
        self.send_error(404)


def serve(host: str | None = None, port: int | None = None) -> None:
    bind_host = host or os.getenv("DASHBOARD_HOST", "0.0.0.0")
    bind_port = port or int(os.getenv("DASHBOARD_PORT", "8000"))
    ThreadingHTTPServer((bind_host, bind_port), DashboardHandler).serve_forever()


if __name__ == "__main__":
    serve()
