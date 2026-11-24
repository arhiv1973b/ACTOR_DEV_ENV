import json
import os
import sys
import urllib.request
import urllib.error
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, r"H:\ACTOR_DEV_ENV")
try:
    from gemini_router import AliasRouter
except Exception as exc:
    AliasRouter = None
    IMPORT_ERR = str(exc)
else:
    IMPORT_ERR = ""

HOST = "127.0.0.1"
PORT = int(os.environ.get("ROUTER_PORT", "8000"))

DEFAULT_MODELS = [
    "models/gemini-3.5-pro",
    "models/gemini-3.1-pro-preview",
    "models/gemini-pro-latest",
    "models/gemini-2.5-pro",
    "models/gemini-flash-latest",
]

def resolve_api_key():
    for env_name in ("GEMINI_API_KEY", "GOOGLE_API_KEY"):
        val = os.environ.get(env_name, "").strip()
        if val:
            return val
    key_file = os.path.expanduser("~/.gemini_key")
    if os.path.isfile(key_file):
        return open(key_file, encoding="utf-8", errors="ignore").read().strip()
    return ""

def resolve_manifest():
    candidates = [
        os.path.expanduser("~/evidence_manifest.json"),
        r"H:\ACTOR_DEV_ENV\audit_manifest.json",
        r"H:\ACTOR_DEV_ENV\batch_manifest.json",
        r"H:\ACTOR_DEV_ENV\dag_manifest.json",
    ]
    for path in candidates:
        if os.path.isfile(path):
            return path
    return ""

def get_models_list():
    manifest_path = resolve_manifest()
    models = list(DEFAULT_MODELS)
    if manifest_path:
        try:
            with open(manifest_path, encoding="utf-8", errors="ignore") as f:
                data = json.load(f)
            if isinstance(data, dict) and isinstance(data.get("available_models"), list):
                for m in data["available_models"]:
                    if isinstance(m, str) and m not in models:
                        models.append(m)
        except Exception:
            pass
    return models

API_KEY = resolve_api_key()
MANIFEST_PATH = resolve_manifest()
ROUTER_INSTANCE = None
if AliasRouter and API_KEY:
    try:
        ROUTER_INSTANCE = AliasRouter(
            api_key=API_KEY,
            manifest_path=MANIFEST_PATH or os.path.expanduser("~/evidence_manifest.json"),
            alias_name=DEFAULT_MODELS[0],
            fallback_models=DEFAULT_MODELS[1:],
            timeout_sec=15,
        )
    except Exception:
        ROUTER_INSTANCE = None

class Handler(BaseHTTPRequestHandler):
    def _send_json(self, code, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path.rstrip("/") in ("/v1/models", "/models"):
            models = get_models_list()
            data = [{"id": m, "object": "model", "owned_by": "local-router"} for m in models]
            self._send_json(200, {"object": "list", "data": data})
            return
        if self.path.rstrip("/") in ("/health", "/"):
            self._send_json(200, {
                "status": "ok",
                "has_api_key": bool(API_KEY),
                "manifest": MANIFEST_PATH,
                "alias_router_ready": ROUTER_INSTANCE is not None,
                "import_error": IMPORT_ERR,
            })
            return
        self._send_json(404, {"error": "Not found"})

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length).decode("utf-8", errors="ignore")
        try:
            req = json.loads(raw) if raw else {}
        except Exception:
            req = {}

        if self.path.rstrip("/") not in ("/v1/chat/completions", "/chat/completions"):
            self._send_json(404, {"error": "Not found"})
            return

        messages = req.get("messages") or []
        prompt = "\n".join(
            f"{m.get('role', 'user')}: {m.get('content', '')}"
            for m in messages if isinstance(m, dict)
        ).strip() or "Hello"

        if ROUTER_INSTANCE is not None:
            try:
                res = ROUTER_INSTANCE.execute(prompt)
                chosen_model = res.get("model", "free-auto")
                text = res.get("text", "")
                self._send_json(200, {
                    "id": "chatcmpl-local-router",
                    "object": "chat.completion",
                    "model": chosen_model,
                    "choices": [{
                        "index": 0,
                        "message": {"role": "assistant", "content": text},
                        "finish_reason": "stop",
                    }],
                })
                return
            except Exception as exc:
                self._send_json(502, {"error": {"message": f"Router execution failed: {exc}"}})
                return

        self._send_json(503, {
            "error": {
                "message": "AliasRouter is not active (set GEMINI_API_KEY or GOOGLE_API_KEY in environment, or check ~/.gemini_key).",
                "import_error": IMPORT_ERR,
            }
        })

    def log_message(self, fmt, *args):
        sys.stderr.write(f"[bridge] {fmt % args}\n")

if __name__ == "__main__":
    print(f"Starting router bridge on http://{HOST}:{PORT} (key={bool(API_KEY)}, manifest={MANIFEST_PATH or 'none'})", flush=True)
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
