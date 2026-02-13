# capacete_hibrido.py
# Sistema Dual: Processamento Local (yolov8s.tflite) OU Remoto (yolov8x no Server)
import cv2, socket, struct, time, subprocess, threading, queue, ssl, os, sys
from gpiozero import Button

# --- CONFIGURAÇÕES ---
SERVER_IP = '192.168.X.X' # EDITAR ESTE IP!
SERVER_PORT = 5000
BUTTON_PIN = 21 
WEBCAM_DEVICE = 0 

# Chaves
CERT_FILE = "keys/client.crt"
KEY_FILE = "keys/client.key"
CA_FILE = "keys/ca.crt"

# Local
MODEL_FILE = "yolov8s.tflite" 
CONF_LOCAL = 0.50
FOCAL_LOCAL = 600

# Áudio
VOICE_CMD = ["espeak-ng", "-v", "pt-br+f4", "-s", "175", "-a", "200"]
audio_q = queue.Queue()

ALT_REF = {"Pessoa":1.70, "Carro":1.50, "Cadeira":0.9}
TRANS = {"person":"Pessoa", "car":"Carro", "chair":"Cadeira"}

def audio_loop():
    ram_file = "/dev/shm/fala.wav"
    while True:
        t = audio_q.get()
        if t is None: break
        try: 
            subprocess.run(VOICE_CMD + ["-w", ram_file, t], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["aplay", "-q", ram_file], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except: pass
        audio_q.task_done()

threading.Thread(target=audio_loop, daemon=True).start()

def falar(t):
    print(f"[FALA] {t}")
    audio_q.put(t)

def run_local(cap):
    falar("Modo Local (Modelo S).")
    
    # LAZY IMPORT
    try:
        from ultralytics import YOLO
    except ImportError:
        falar("Erro: Ultralytics não instalado.")
        return
    except Exception as e:
        print(f"Erro Local: {e}")
        return

    if not os.path.exists(MODEL_FILE):
        falar("Erro: Arquivo .tflite não encontrado.")
        return
        
    try:
        model = YOLO(MODEL_FILE, task='detect')
    except:
        falar("Falha ao carregar modelo.")
        return
        
    last_spk = {}
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break
        # Resize 320 obrigatorio
        res = model(cv2.resize(frame, (320,320)), stream=True, conf=CONF_LOCAL, verbose=False)
        objs = []
        for r in res:
            for box in r.boxes:
                raw = r.names[int(box.cls[0])] if r.names else str(int(box.cls[0]))
                lbl = TRANS.get(raw.lower(), raw)
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                if (y2-y1) < 10: continue
                dist = (ALT_REF.get(lbl, 1.0) * FOCAL_LOCAL) / (y2-y1)
                if dist < 8.0: objs.append((lbl, dist))
        
        if objs:
            objs.sort(key=lambda x: x[1])
            nm, d = objs[0]
            now = time.time()
            if nm not in last_spk or (now - last_spk[nm] > 4.0):
                last_spk[nm] = now
                falar(f"{nm} a {d:.1f}".replace(".",","))
        time.sleep(0.01)

def run_remote(cap):
    falar("Modo Remoto (Modelo X).")
    if not os.path.exists(CA_FILE):
        falar("Erro Chaves.")
        return
    
    try:
        ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=CA_FILE)
        ctx.load_cert_chain(CERT_FILE, KEY_FILE)
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_REQUIRED
    except: return

    while True:
        sock = None
        try:
            sock = ctx.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM), server_hostname=SERVER_IP)
            sock.settimeout(5.0)
            sock.connect((SERVER_IP, SERVER_PORT))
            sock.settimeout(None)
            falar("Conectado.")
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret: break
                res, jpg = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
                b = jpg.tobytes()
                sock.sendall(struct.pack(">L", len(b)) + b)
                resp = sock.recv(1024).decode('utf-8')
                if not resp: break
                if resp != "NO_CMD": falar(resp)
        except KeyboardInterrupt:
            raise # Passa para o main
        except Exception as e:
            # Captura erros gerais de rede/SSL
            print(f"[REDE] Erro ou reconexão: {e}")
            falar("Conexão perdida.")
            time.sleep(2)
        finally:
            if sock: 
                try: sock.close()
                except: pass

def main():
    cap = cv2.VideoCapture(WEBCAM_DEVICE)
    cap.set(3, 640); cap.set(4, 480)
    try: btn = Button(BUTTON_PIN)
    except: btn = None
    
    falar("Sistema ligado.")
    print("Segure GPIO 21 para Local (S), solte para Remoto (X).")
    time.sleep(4)
    
    if btn and btn.is_pressed: run_local(cap)
    else: run_remote(cap)
    cap.release()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n--- Desligando Sistema (Ctrl+C) ---")
        try: sys.exit(0)
        except: os._exit(0)
