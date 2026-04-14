import subprocess
import threading
import queue
import time
import os

AUDIOS = {
    "Pessoa": "audios/Pessoa.m4a",
    "Gato": "audios/Gato.m4a",
    "Livro": "audios/Livro.m4a",
    "Á Sua Frente": "audios/Á Sua Frente.m4a"
}

audio_q = queue.Queue()

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
                ["ffplay", "-nodisp", "-autoexit", arquivo],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        except Exception as e:
            print(f"[ERRO] Falha ao tocar: {e}")
        
        audio_q.task_done()

threading.Thread(target=audio_loop, daemon=True).start()


def falar_objeto(nome):
    arquivo = AUDIOS.get(nome)
    if arquivo:
        print(f"[TOCANDO] {nome}")
        audio_q.put(arquivo)
    else:
        print(f"[ERRO] Áudio não mapeado: {nome}")


if __name__ == "__main__":
    print("Teste de áudio iniciado...\n")
    
    falar_objeto("Pessoa")
    time.sleep(3)
    
    falar_objeto("Gato")
    falar_objeto("Á Sua Frente")
    time.sleep(3)
    
    falar_objeto("Livro")
    

    audio_q.join()
    print("\nTeste finalizado.")