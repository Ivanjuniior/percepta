#!/usr/bin/env python3
"""Visualizador MJPEG sob demanda para a câmera do Percepta.

A câmera só é aberta enquanto existe ao menos um cliente autenticado em /video.
O processo não interfere no capacete_hibrido.py nem no socket TLS de inferência.
"""
from __future__ import annotations

import base64
import hmac
import logging
import os
import signal
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

import cv2

HOST = os.environ.get("PERCEPTA_WEB_HOST", "0.0.0.0")
PORT = int(os.environ.get("PERCEPTA_WEB_PORT", "8080"))
CAMERA_DEVICE = os.environ.get("PERCEPTA_CAMERA_DEVICE", "0")
USERNAME = os.environ.get("PERCEPTA_WEB_USER", "")
PASSWORD = os.environ.get("PERCEPTA_WEB_PASSWORD", "")
FRAME_WIDTH = int(os.environ.get("PERCEPTA_WEB_WIDTH", "640"))
FRAME_HEIGHT = int(os.environ.get("PERCEPTA_WEB_HEIGHT", "480"))
FPS = max(1, min(int(os.environ.get("PERCEPTA_WEB_FPS", "15")), 30))
JPEG_QUALITY = max(40, min(int(os.environ.get("PERCEPTA_WEB_JPEG_QUALITY", "80")), 95))
BOUNDARY = b"percepta-frame"

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("percepta-camera")


class CameraStream:
    """Gerencia uma única captura compartilhada e fecha-a quando não há viewers."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._condition = threading.Condition(self._lock)
        self._capture = None
        self._frame: bytes | None = None
        self._clients = 0
        self._running = True
        self._thread: threading.Thread | None = None

    def _open_locked(self) -> None:
        if self._capture is not None and self._capture.isOpened():
            return
        device = int(CAMERA_DEVICE) if CAMERA_DEVICE.isdigit() else CAMERA_DEVICE
        cap = cv2.VideoCapture(device)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
        cap.set(cv2.CAP_PROP_FPS, FPS)
        if not cap.isOpened():
            cap.release()
            raise RuntimeError(f"Não foi possível abrir a câmera {CAMERA_DEVICE}")
        self._capture = cap
        self._frame = None
        self._thread = threading.Thread(target=self._capture_loop, name="camera-capture", daemon=True)
        self._thread.start()
        log.info("Câmera aberta sob demanda: %s", CAMERA_DEVICE)

    def _capture_loop(self) -> None:
        interval = 1.0 / FPS
        while True:
            with self._lock:
                if not self._running or self._clients <= 0 or self._capture is None:
                    break
                cap = self._capture
            ok, frame = cap.read()
            if ok:
                encoded, buffer = cv2.imencode(
                    ".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), JPEG_QUALITY]
                )
                if encoded:
                    with self._condition:
                        self._frame = buffer.tobytes()
                        self._condition.notify_all()
            else:
                log.warning("Falha ao capturar quadro da câmera")
                time.sleep(0.2)
            time.sleep(interval)

        with self._condition:
            if self._capture is not None:
                self._capture.release()
                self._capture = None
            self._frame = None
            self._condition.notify_all()
        log.info("Câmera liberada (sem visualizadores)")

    def subscribe(self):
        with self._lock:
            if not self._running:
                raise RuntimeError("Serviço está encerrando")
            self._clients += 1
            if self._clients == 1:
                try:
                    self._open_locked()
                except Exception:
                    self._clients -= 1
                    raise
        return self.frames()

    def unsubscribe(self) -> None:
        with self._condition:
            self._clients = max(0, self._clients - 1)
            self._condition.notify_all()

    def frames(self):
        last_frame = None
        while True:
            with self._condition:
                self._condition.wait_for(
                    lambda: self._frame is not None and self._frame is not last_frame
                    or not self._running or self._clients <= 0,
                    timeout=5.0,
                )
                if not self._running or self._clients <= 0:
                    return
                frame = self._frame
            if frame is None or frame is last_frame:
                continue
            last_frame = frame
            yield (
                b"--" + BOUNDARY + b"\r\n"
                b"Content-Type: image/jpeg\r\n"
                b"Content-Length: " + str(len(frame)).encode("ascii") + b"\r\n\r\n"
                + frame + b"\r\n"
            )

    def stop(self) -> None:
        with self._condition:
            self._running = False
            self._clients = 0
            self._condition.notify_all()
        with self._lock:
            if self._capture is not None:
                self._capture.release()
                self._capture = None


stream = CameraStream()


def make_auth_header() -> str:
    token = base64.b64encode(f"{USERNAME}:{PASSWORD}".encode()).decode("ascii")
    return f"Basic {token}"


class CameraHandler(BaseHTTPRequestHandler):
    server_version = "PerceptaCamera/1.0"

    def log_message(self, fmt, *args):
        log.info("%s - %s", self.client_address[0], fmt % args)

    def _authorized(self) -> bool:
        supplied = self.headers.get("Authorization", "")
        return bool(supplied) and hmac.compare_digest(supplied, make_auth_header())

    def _require_auth(self) -> bool:
        if self._authorized():
            return True
        self.send_response(401)
        self.send_header("WWW-Authenticate", 'Basic realm="Percepta Camera", charset="UTF-8"')
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", "0")
        self.end_headers()
        return False

    def do_GET(self):
        path = urlparse(self.path).path
        if path not in ("/", "/video", "/health"):
            self.send_error(404)
            return
        if not self._require_auth():
            return

        if path == "/health":
            body = b'{"status":"ok","service":"percepta-camera"}'
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)
            return

        if path == "/":
            html = b"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Percepta | Camera</title>
<style>
:root{color-scheme:dark;font-family:system-ui,sans-serif;background:#0b1220;color:#e8eefc}
*{box-sizing:border-box}body{margin:0;min-height:100vh;display:grid;place-items:center;padding:24px}
main{width:min(100%,1000px)}header{display:flex;align-items:center;justify-content:space-between;gap:16px}
h1{font-size:clamp(1.4rem,4vw,2rem);margin:.2rem 0}.tag{color:#77e0c0;font-size:.85rem}
p{color:#aab8d1}.screen{margin-top:20px;background:#050914;border:1px solid #26344e;border-radius:16px;overflow:hidden;min-height:240px;display:grid;place-items:center}
img{width:100%;height:auto;display:block}.hint{padding:28px;text-align:center}
button{border:0;border-radius:10px;padding:12px 18px;background:#58d6b4;color:#06131a;font-weight:700;cursor:pointer}
button.secondary{background:#26344e;color:#e8eefc;margin-left:8px}
.controls{margin-top:16px;display:flex;gap:8px;flex-wrap:wrap}
small{color:#8190aa}
</style></head><body><main>
<header><div><div class="tag">PERCEPTA / EDGE CAMERA</div><h1>Visualização ao vivo</h1></div><small>MJPEG • sob demanda</small></header>
<p>A câmera fica ativa somente enquanto esta visualização estiver conectada.</p>
<div class="screen"><div id="hint" class="hint">Pressione “Iniciar câmera” para abrir o vídeo.</div><img id="feed" alt="Vídeo ao vivo da câmera" hidden></div>
<div class="controls"><button id="start">Iniciar câmera</button><button id="stop" class="secondary">Parar câmera</button></div>
<p><small>Ao fechar esta página ou pressionar Parar, a captura será liberada.</small></p>
</main><script>
const feed=document.getElementById('feed'),hint=document.getElementById('hint');
function stop(){feed.removeAttribute('src');feed.hidden=true;hint.hidden=false}
document.getElementById('start').onclick=()=>{hint.hidden=true;feed.hidden=false;feed.src='/video?ts='+Date.now()};
document.getElementById('stop').onclick=stop;
window.addEventListener('pagehide',stop);
</script></body></html>"""
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(html)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(html)
            return

        try:
            frames = stream.subscribe()
        except Exception as exc:
            log.exception("Não foi possível iniciar a câmera")
            self.send_error(503, str(exc))
            return
        self.send_response(200)
        self.send_header("Content-Type", "multipart/x-mixed-replace; boundary=percepta-frame")
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Connection", "close")
        self.end_headers()
        try:
            for chunk in frames:
                self.wfile.write(chunk)
                self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            pass
        except Exception:
            log.exception("Erro durante o envio do vídeo")
        finally:
            stream.unsubscribe()

    def log_request(self, code="-", size="-"):
        super().log_request(code, size)


def main() -> None:
    if not USERNAME or not PASSWORD:
        raise SystemExit(
            "Configure PERCEPTA_WEB_USER e PERCEPTA_WEB_PASSWORD antes de iniciar. "
            "O servidor não inicia sem autenticação."
        )
    if len(PASSWORD) < 12:
        raise SystemExit("A senha PERCEPTA_WEB_PASSWORD deve ter pelo menos 12 caracteres.")
    if PORT < 1 or PORT > 65535:
        raise SystemExit("PERCEPTA_WEB_PORT deve estar entre 1 e 65535.")

    server = ThreadingHTTPServer((HOST, PORT), CameraHandler)
    server.daemon_threads = True
    server.allow_reuse_address = True
    log.info("Visualizador disponível em http://%s:%s (autenticação obrigatória)", HOST, PORT)
    log.warning("Use HTTPS ou acesse somente por rede confiável/VPN; HTTP Basic não cifra credenciais.")
    try:
        server.serve_forever(poll_interval=0.5)
    except KeyboardInterrupt:
        log.info("Encerrando...")
    finally:
        server.shutdown()
        stream.stop()
        server.server_close()


if __name__ == "__main__":
    main()
