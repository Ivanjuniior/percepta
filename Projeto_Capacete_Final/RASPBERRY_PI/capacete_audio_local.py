import cv2
import time
import subprocess
import threading
import queue
import os

# ================= CONFIG =================
WEBCAM_DEVICE = 0

MODEL_FILE = "yolov8s.tflite" 
CONF_LOCAL = 0.5
FOCAL_LOCAL = 600

AUDIOS = {
    "Pessoa": "audios/pessoa.m4a",
    "Carro": "audios/carro.m4a",
    "Cadeira": "audios/cadeira.m4a"
}

ALT_REF = {"Pessoa":1.70, "Carro":1.50, "Cadeira":0.9}
TRANS = {"person":"Pessoa", "car":"Carro", "chair":"Cadeira"}

audio_q = queue.Queue()

# ================= ÁUDIO =================
def audio_loop():
    while True:
        arquivo = audio_q.get()
        if arquivo is None:
            break
        
        if not os.path.exists(arquivo):
            print(f"[ERRO] Arquivo não encontrado: {arquivo}")
            audio_q.task_done()
            continue
        
        try:
            subprocess.run(
                ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", arquivo],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        except Exception as e:
            print(f"[ERRO ÁUDIO] {e}")
        
        audio_q.task_done()

threading.Thread(target=audio_loop, daemon=True).start()

def falar_objeto(nome):
    arquivo = AUDIOS.get(nome)
    if arquivo:
        print(f"[TOCANDO] {nome}")
        audio_q.put(arquivo)

# ================= IA LOCAL =================
def run():
    print("Iniciando sistema com áudio gravado...")

    try:
        from ultralytics import YOLO
    except:
        print("Erro: instale com -> pip install ultralytics")
        return

    if not os.path.exists(MODEL_FILE):
        print("Modelo não encontrado!")
        return

    model = YOLO(MODEL_FILE)

    cap = cv2.VideoCapture(WEBCAM_DEVICE)
    cap.set(3, 640)
    cap.set(4, 480)

    last_spk = {}

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame, conf=CONF_LOCAL, verbose=False)

        objs = []

        for r in results:
            for box in r.boxes:
                raw = r.names[int(box.cls[0])]
                lbl = TRANS.get(raw.lower(), raw)

                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()

                if (y2 - y1) < 10:
                    continue

                dist = (ALT_REF.get(lbl, 1.0) * FOCAL_LOCAL) / (y2 - y1)

                if dist < 8.0:
                    objs.append((lbl, dist))

        if objs:
            objs.sort(key=lambda x: x[1])
            nm, d = objs[0]

            now = time.time()

            if nm not in last_spk or (now - last_spk[nm] > 4):
                last_spk[nm] = now
                falar_objeto(nm)

        # opcional: mostrar imagem
        cv2.imshow("Camera", frame)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

# ================= MAIN =================
if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("Encerrado.")