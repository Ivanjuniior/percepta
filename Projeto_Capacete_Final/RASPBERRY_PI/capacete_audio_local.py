import cv2
import time
import threading
import queue
import os
import pygame

# ================= CONFIG =================
WEBCAM_DEVICE = 0

MODEL_FILE = "yolov8s.tflite"
CONF_LOCAL = 0.5
FOCAL_LOCAL = 600

# ================= AUDIO =================
pygame.mixer.init()
audio_q = queue.Queue()

# ================= ÁUDIOS =================
AUDIOS = {
    "a": "audios_wav/a.wav",
    "a sua direita": "audios_wav/á sua direita.wav",
    "a sua esquerda": "audios_wav/á sua esquerda.wav",
    "a sua frente": "audios_wav/á sua frente.wav",
    
    "bicicleta": "audios_wav/bicicleta.wav",
    
    "cachorro": "audios_wav/cachorro.wav",
    "cama": "audios_wav/cama.wav",
    "caminhao": "audios_wav/caminhão.wav",
    "celular": "audios_wav/celular.wav",
    "centimetros": "audios_wav/centímetros.wav",
    "copo": "audios_wav/copo.wav",
    
    "direita": "audios_wav/direita.wav",
    "esquerda": "audios_wav/esquerda.wav",
    "frente": "audios_wav/frente.wav",
    
    "garrafa": "audios_wav/garrafa.wav",
    "gato": "audios_wav/gato.wav",
    
    "livro": "audios_wav/livro.wav",
    
    "mesa": "audios_wav/mesa.wav",
    "mouse": "audios_wav/mouse.wav",
    
    "notebook": "audios_wav/notebook.wav",
    
    "o sistema identificou": "audios_wav/o sistema identificou.wav",
    "o": "audios_wav/o.wav",
    "onibus": "audios_wav/ônibus.wav",
    
    "pessoa": "audios_wav/pessoa.wav",
    
    "relogio": "audios_wav/relógio.wav",
    
    "semaforo": "audios_wav/semáforo.wav",
    "sinal vermelho": "audios_wav/sinal vermelho.wav",
    "sobre": "audios_wav/sobre.wav",
    
    "teclado": "audios_wav/teclado.wav",
    "televisao": "audios_wav/televisão.wav",
    
    "TV": "audios_wav/TV.wav",
}

AUDIOS_NUM = {
    "0": "audios_wav/0.wav",
    "1": "audios_wav/1.wav",
    "2": "audios_wav/2.wav",
    "3": "audios_wav/3.wav",
    "4": "audios_wav/4.wav",
    "5": "audios_wav/5.wav",
    "6": "audios_wav/6.wav",
    "7": "audios_wav/7.wav",
    "8": "audios_wav/8.wav",
    "9": "audios_wav/9.wav",
    "a": "audios_wav/a.wav",
    "metros": "audios_wav/metros.wav"
}

ALT_REF = {"pessoa": 1.70, "carro": 1.50, "cadeira": 0.9}
TRANS = {"person": "pessoa", "cell phone": "celular", "glass": "copo"}

# ================= AUDIO THREAD =================
def tocar_audio_sequencial(lista):
    pygame.mixer.music.stop()  

    for arquivo in lista:
        if arquivo and os.path.exists(arquivo):
            pygame.mixer.music.load(arquivo)
            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy():
                time.sleep(0.05)


def audio_worker():
    while True:
        lista = audio_q.get()
        if lista is None:
            break

        try:
            tocar_audio_sequencial(lista)
        except Exception as e:
            print("[ERRO ÁUDIO]", e)

        audio_q.task_done()

threading.Thread(target=audio_worker, daemon=True).start()

# ================= DISTÂNCIA =================
def calcular_distancia(y1, y2, lbl):
    altura = (y2 - y1)
    if altura < 10:
        return None

    return (ALT_REF.get(lbl, 1.0) * FOCAL_LOCAL) / altura


def normalizar(dist):
    return int(round(dist))  # 1 metro por nível


# ================= MEMÓRIA =================
last_spoken = {}
audio_q.queue.clear()

# ================= REGRA DE FALA =================
def pode_falar(lbl, dist):
    dist = normalizar(dist)

    if lbl not in last_spoken:
        last_spoken[lbl] = dist
        return True

    if last_spoken[lbl] != dist:
        last_spoken[lbl] = dist
        return True

    return False


# ================= FALA =================
def falar_objeto(nome, dist_m):
    audio_q.queue.clear() 
    lista = []

    if nome in AUDIOS:
        lista.append(AUDIOS[nome])

    dist_m = normalizar(dist_m)
    dist_m = max(0, min(9, dist_m))

    lista.append(AUDIOS_NUM["a"])
    lista.append(AUDIOS_NUM[str(dist_m)])
    lista.append(AUDIOS_NUM["metros"])

    print(f"{nome} a {dist_m} metros")

    audio_q.put(lista)


# ================= MAIN =================
def run():
    print("Iniciando sistema...")

    try:
        from ultralytics import YOLO
    except:
        print("Instale: pip install ultralytics")
        return

    model = YOLO(MODEL_FILE)

    cap = cv2.VideoCapture(WEBCAM_DEVICE)
    cap.set(3, 640)
    cap.set(4, 480)

    seen = {}

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame, conf=CONF_LOCAL, verbose=False)

        current = set()

        for r in results:
            for box in r.boxes:
                raw = r.names[int(box.cls[0])]
                lbl = TRANS.get(raw.lower(), raw)

                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()

                dist = calcular_distancia(y1, y2, lbl)
                if dist is None:
                    continue

                if dist < 8.0:
                    current.add(lbl)

                    if lbl not in seen:
                        seen[lbl] = True

                    if pode_falar(lbl, dist):
                        falar_objeto(lbl, dist)

        # remove objetos que sumiram + limpa memória
        for old in list(seen.keys()):
            if old not in current:
                del seen[old]
                last_spoken.pop(old, None)

        cv2.imshow("Camera", frame)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
    audio_q.put(None)


# ================= START =================
if __name__ == "__main__":
    run()