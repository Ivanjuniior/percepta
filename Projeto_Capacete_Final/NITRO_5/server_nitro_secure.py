# server_nitro_secure.py
# ======================================================================
# SERVIDOR DE INFERÊNCIA SEGURO (Nitro 5 - Ubuntu 24.04)
# Modelo: YOLOv8x (Extra Large) - Máxima Precisão na GPU
# ======================================================================

import socket
import struct
import cv2
import numpy as np
from ultralytics import YOLO
import time
import torch
import math
import ssl

HOST_IP = '0.0.0.0'
PORT = 5000

# --- CERTIFICADOS ---
CERT_FILE = "keys/server.crt"
KEY_FILE = "keys/server.key"
CA_FILE = "keys/ca.crt"

# --- CONFIGURAÇÕES DA IA ---
# Usando o modelo X (Extra Large) pois a RTX 3050 aguenta e a precisão é vital
MODEL_PATH = "yolov8x.pt"      
CONF_THRESHOLD = 0.50
FOCAL_LENGTH = 600

# --- ANTI-FLOOD ---
COOLDOWN_MESMO_LUGAR = 10.0
DIST_MEMORIA_PIXELS = 150

ALTURAS_REF = {
    "Pessoa": 1.70, "Carro": 1.50, "Moto": 1.0, "Cadeira": 0.9, 
    "Garrafa": 0.25, "Copo": 0.15, "Cachorro": 0.50, "Gato": 0.30
}

TRADUCOES = {
    "person": "Pessoa", "car": "Carro", "motorcycle": "Moto",
    "dog": "Cachorro", "cat": "Gato", "chair": "Cadeira", "bottle": "Garrafa"
}

spatial_memory = []

def process_logic(frame, model):
    global spatial_memory
    dev = 0 if torch.cuda.is_available() else 'cpu'
    
    # Inferência
    results = model(frame, verbose=False, conf=CONF_THRESHOLD, device=dev)
    
    command_to_send = "NO_CMD"
    now = time.time()
    spatial_memory = [rec for rec in spatial_memory if (now - rec['time']) < (COOLDOWN_MESMO_LUGAR * 2)]
    
    for r in results:
        for box in r.boxes:
            cls_id = int(box.cls[0])
            raw_name = model.names[cls_id]
            label_pt = TRADUCOES.get(raw_name.lower(), raw_name)
            
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
            cx, cy = int((x1+x2)/2), int((y1+y2)/2)
            altura_px = y2 - y1
            
            altura_real = ALTURAS_REF.get(label_pt, 1.0)
            distancia = (altura_real * FOCAL_LENGTH) / altura_px
            
            should_speak = True
            for mem in spatial_memory:
                if mem['label'] == label_pt:
                    dist_pixels = math.sqrt((mem['x'] - cx)**2 + (mem['y'] - cy)**2)
                    if dist_pixels < DIST_MEMORIA_PIXELS and (now - mem['time']) < COOLDOWN_MESMO_LUGAR:
                        should_speak = False
                        break
            
            if should_speak:
                spatial_memory.append({'label': label_pt, 'x': cx, 'y': cy, 'time': now})
                dist_str = f"{distancia:.1f}".replace(".", ",")
                if distancia < 1.0: return f"Cuidado! {label_pt} a {dist_str}"
                else: return f"{label_pt} a {dist_str}"
    
    return command_to_send

def main():
    print("--- SERVIDOR NITRO 5 SEGURO (MODELO X) ---")
    
    try:
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain(certfile=CERT_FILE, keyfile=KEY_FILE)
        context.load_verify_locations(cafile=CA_FILE)
        context.verify_mode = ssl.CERT_REQUIRED
    except Exception as e:
        print(f"Erro SSL: {e}. Rode o script gen_keys.sh!")
        return

    print(f"Carregando {MODEL_PATH} na GPU... (Pode demorar um pouco)")
    try: model = YOLO(MODEL_PATH)
    except Exception as e: 
        print(f"Erro: Coloque o arquivo {MODEL_PATH} nesta pasta! {e}")
        return

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST_IP, PORT))
    s.listen(1)
    print(f"🔒 Ouvindo em {PORT}...")

    try:
        while True:
            print("\n>>> Aguardando conexão...")
            try:
                newsocket, fromaddr = s.accept()
                conn = context.wrap_socket(newsocket, server_side=True)
                print(f">>> Conectado: {fromaddr}")
                
                data = b""
                payload_size = struct.calcsize(">L")
                
                while True:
                    while len(data) < payload_size:
                        packet = conn.recv(4096)
                        if not packet: break
                        data += packet
                    if not data: break
                    
                    packed_msg_size = data[:payload_size]
                    data = data[payload_size:]
                    msg_size = struct.unpack(">L", packed_msg_size)[0]
                    
                    while len(data) < msg_size:
                        data += conn.recv(4096)
                    
                    frame_data = data[:msg_size]
                    data = data[msg_size:]
                    
                    frame = cv2.imdecode(np.frombuffer(frame_data, dtype=np.uint8), cv2.IMREAD_COLOR)
                    if frame is not None:
                        resp = process_logic(frame, model)
                        if resp != "NO_CMD": print(f"> {resp}")
                        conn.sendall(resp.encode('utf-8'))
                        
                        cv2.imshow('Server View', frame)
                        if cv2.waitKey(1) & 0xFF == ord('q'): break
            except Exception as e:
                print(f"Fim da sessão: {e}")
            finally:
                try: conn.close()
                except: pass
                cv2.destroyAllWindows()
    except KeyboardInterrupt:
        pass
    finally:
        s.close()

if __name__ == "__main__":
    main()
