#!/usr/bin/env python3
"""Visualizador MJPEG sob demanda para a câmera do Percepta."""
from __future__ import annotations

import base64
import hmac
import logging
import os
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
WIDTH = int(os.environ.get("PERCEPTA_WEB_WIDTH", "640"))
HEIGHT = int(os.environ.get("PERCEPTA_WEB_HEIGHT", "480"))
FPS = max(1, min(int(os.environ.get("PERCEPTA_WEB_FPS", "15")), 30))
QUALITY = max(40, min(int(os.environ.get("PERCEPTA_WEB_JPEG_QUALITY", "80")), 95))
BOUNDARY = b"percepta-frame"

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("percepta-camera")


class CameraStream:
    """Compartilha uma captura e a libera quando o último cliente sai."""

    def __init__(self):
        self.lock = threading.RLock()
        self.condition = threading.Condition(self.lock)
        self.capture = None
        self.frame = None
        self.clients = 0
        self.running = True
        self.thread = None

    def _capture_loop(self):
        interval = 1.0 / FPS
        while True:
            with self.lock:
                if not self.running or self.clients == 0 or self.capture is None:
                    break
                cap = self.capture
            ok, image = cap.read()
            if ok:
                success, encoded = cv2.imencode(
                    ".jpg", image, [int(cv2.IMWRITE_JPEG_QUALITY), QUALITY]
                )
                if success:
                    with self.condition:
                        self.frame = encoded.tobytes()
                        self.condition.notify_all()
            else:
                log.warning("Falha ao capturar quadro da câmera")
                time.sleep(0.2)
            time.sleep(interval)

        with self.condition:
            if self.capture is not None:
                self.capture.release()
                self.capture = None
            self.frame = None
            self.condition.notify_all()
        log.info("Câmera liberada (sem visualizadores)")

    def subscribe(self):
        with self.lock:
            if not self.running:
                raise RuntimeError("Serviço está encerrando")
            self.clients += 1
            if self.clients == 1:
                device = int(CAMERA_DEVICE) if CAMERA_DEVICE.isdigit() else CAMERA_DEVICE
                cap = cv2.VideoCapture(device)
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
                cap.set(cv2.CAP_PROP_FPS, FPS)
                if not cap.isOpened():
                    cap.release()
                    self.clients -= 1
                    raise RuntimeError(f"Não foi possível abrir a câmera {CAMERA_DEVICE}")
                self.capture = cap
                self.frame = None
                self.thread = threading.Thread(target=self._capture_loop, daemon=True)
                self.thread.start()
                log.info("Câmera aberta sob demanda: %s", CAMERA_DEVICE)
        return self.frames()

    def unsubscribe(self):
        with self.condition:
            self.clients = max(0, self.clients - 1)
            self.condition.notify_all()

    def frames(self):
        last_frame = None
        while True:
            with self.condition:
                self.condition.wait_for(
                    lambda: (self.frame is not None and self.frame is not last_frame)
                    or not self.running or self.clients == 0,
                    timeout=5.0,
                )
                if not self.running or self.clients == 0:
                    return
                frame = self.frame
            if frame is None or frame is last_frame:
                continue
            last_frame = frame
            yield (
                b"--" + BOUNDARY + b"\r\n"
                b"Content-Type: image/jpeg\r\n"
                b"Content-Length: " + str(len(frame)).encode("ascii") + b"\r\n\r\n"
                + frame + b"\r\n"
            )

    def stop(self):
        with self.condition:
            self.running = False
            self.clients = 0
            self.condition.notify_all()
        with self.lock:
            if self.capture is not None:
                self.capture.release()
                self.capture = None


stream = CameraStream()


def auth_value():
    raw = base64.b64encode(f"{USERNAME}:{PASSWORD}".encode("utf-8")).decode("ascii")
    return "Basic " + raw


class Handler(BaseHTTPRequestHandler):
    server_version = "PerceptaCamera/1.0"

    def log_message(self, fmt, *args):
        log.info("%s - %s", self.client_address[0], fmt % args)

    def authorized(self):
        return bool(self.headers.get("Authorization")) and hmac.compare_digest(
            self.headers.get("Authorization", ""), auth_value()
        )

    def require_auth(self):
        if self.authorized():
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
        if not self.require_auth():
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
            page = b"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Percepta | Camera</title><style>
:root{color-scheme:dark;font-family:system-ui,sans-serif;background:#0b1220;color:#e8eefc}
*{box-sizing:border-box}body{margin:0;min-height:100vh;display:grid;place-items:center;padding:24px}
main{width:min(100%,1000px)}header{display:flex;align-items:center;justify-content:space-between;gap:16px}
h1{font-size:clamp(1.4rem,4vw,2rem);margin:.2rem 0}.tag{color:#77e0c0;font-size:.85rem}
p{color:#aab8d1}.screen{margin-top:20px;background:#050914;border:1px solid #26344e;border-radius:16px;overflow:hidden;min-height:240px;display:grid;place-items:center}
img{width:100%;height:auto;display:block}.hint{padding:28px;text-align:center}
button{border:0;border-radius:10px;padding:12px 18px;background:#58d6b4;color:#06131a;font-weight:700;cursor:pointer}
button.secondary{background:#26344e;color:#e8eefc;margin-left:8px}.controls{margin-top:16px;display:flex;gap:8px;flex-wrap:wrap}
small{color:#8190aa}</style></head><body><main>
<header><div><div class="tag">PERCEPTA / EDGE CAMERA</div><h1>Visualização ao vivo</h1></div><small>MJPEG • sob demanda</small></header>
<p>A câmera fica ativa somente enquanto esta visualização estiver conectada.</p>
<div class="screen"><div id="hint" class="hint">Pressione “Iniciar câmera” para abrir o vídeo.</div><img id="feed" alt="Vídeo ao vivo da câmera" hidden></div>
<div class="controls"><button id="start">Iniciar câmera</button><button id="stop" class="secondary">Parar câmera</button></div>
<p><small>Ao fechar esta página ou pressionar Parar, a captura será liberada.</small></p></main>
<script>
const feed=document.getElementById('feed'),hint=document.getElementById('hint');
function stop(){feed.removeAttribute('src');feed.hidden=true;hint.hidden=false}
document.getElementById('start').onclick=()=>{hint.hidden=true;feed.hidden=false;feed.src='/video?ts='+Date.now()};
document.getElementById('stop').onclick=stop;window.addEventListener('pagehide',stop);
</script></body></html>"""
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(page)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(page)
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
            log.exception("Erro durante envio do vídeo")
        finally:
            stream.unsubscribe()


def main():
    if not USERNAME or not PASSWORD:
        raise SystemExit("Configure PERCEPTA_WEB_USER e PERCEPTA_WEB_PASSWORD antes de iniciar.")
    if len(PASSWORD) < 12:
        raise SystemExit("A senha deve ter pelo menos 12 caracteres.")
    if not 1 <= PORT <= 65535:
        raise SystemExit("PERCEPTA_WEB_PORT deve estar entre 1 e 65535.")

    server = ThreadingHTTPServer((HOST, PORT), Handler)
    server.daemon_threads = True
    log.info("Visualizador em http://%s:%s; autenticação obrigatória", HOST, PORT)
    log.warning("HTTP Basic não cifra credenciais: use LAN confiável, VPN ou proxy HTTPS.")
    try:
        server.serve_forever(poll_interval=0.5)
    except KeyboardInterrupt:
        log.info("Encerrando visualizador")
    finally:
        stream.stop()
        server.server_close()


if __name__ == "__main__":
    main()
