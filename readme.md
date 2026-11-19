# 🧠 PERCEPTA PROJECT

![Status](https://img.shields.io/badge/status-active-success)
![Python](https://img.shields.io/badge/python-3.x-blue)
![Platform](https://img.shields.io/badge/platform-Raspberry%20Pi%204-red)

---

## 🇺🇸 English Version

### 📌 Description
**Percepta Project** is a distributed system that integrates a cloud server and a Raspberry Pi 4, using computer vision with COCO-based models for local and remote processing.

---

### ⚙️ Architecture

The project is divided into two main components:

- `CLOUD` → Server-side processing  
- `RASPBERRY_PI` → Edge device (Raspberry Pi 4)

---

### 🚀 Usage

1. Update Python

2. Configure IP addresses:

```python
# capacete_hibrido.py
SERVER_IP
```

```python
# server_cloud_secure.py
HOST_IP
```

3. Create and activate virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

4. Install dependencies:

```bash
pip install -r requirements.txt
```

5. Run the system:

```bash
# CLOUD (server)
python3 server_cloud_secure.py

# Raspberry Pi
python3 capacete_hibrido.py
```

---

### 🔘 Button Behavior

- Connected to **GPIO21**

| State | Mode |
|------|------|
| Not pressed | Remote mode |
| Pressed | Local mode |

---

### 🧠 Models

```python
# Server
MODEL_PATH = "percepta.pt"

# Raspberry Pi
MODEL_FILE = "percepta.tflite"
```

---

### 🏗️ System Structure

```
Projeto_Capacete_Final
├── CLOUD
│   ├── deploy_tflite.sh
│   ├── gen_keys.sh
│   ├── keys
│   ├── requirements.txt
│   ├── server_cloud_secure.py
 |   └── percepta.tflite
└── RASPBERRY_PI
    ├── capacete_hibrido.py
    ├── keys
    ├── requirements.txt
    └── percepta.tflite
```

---

## 🇧🇷 Versão em Português

### 📌 Descrição
O **Projeto Percepta** é um sistema distribuído que integra um servidor em nuvem e um Raspberry Pi 4, utilizando visão computacional com modelos baseados no COCO para processamento local e remoto.

---

### ⚙️ Arquitetura

O projeto é dividido em dois componentes principais:

- `CLOUD` → Processamento no servidor  
- `RASPBERRY_PI` → Dispositivo embarcado

---

### 🚀 Modo de Uso

1. Atualize o Python  

2. Configure os IPs:

```python
# capacete_hibrido.py
SERVER_IP
```

```python
# server_cloud_secure.py
HOST_IP
```

3. Ambiente virtual:

```bash
python -m venv .venv
source .venv/bin/activate
```

4. Instale dependências:

```bash
pip install -r requirements.txt
```

5. Execução:

```bash
# CLOUD
python3 server_cloud_secure.py

# Raspberry Pi
python3 capacete_hibrido.py
```

---

### 🔘 Botão

- Conectado ao **GPIO21**

| Estado | Modo |
|--------|------|
| Não pressionado | Remoto |
| Pressionado | Local |

---

### 🧠 Modelos

```python
# Servidor
MODEL_PATH = "percepta.pt"

# Raspberry Pi
MODEL_FILE = "percepta.tflite"
```

---

### 🏗️ Estrutura do Sistema

```
Projeto_Capacete_Final
├── CLOUD
│   ├── deploy_tflite.sh
│   ├── gen_keys.sh
│   ├── keys
│   ├── requirements.txt
│   ├── server_cloud_secure.py
 |   └── percepta.tflite
└── RASPBERRY_PI
    ├── capacete_hibrido.py
    ├── keys
    ├── requirements.txt
    └── percepta.tflite
```


---

## 📷 On-Demand Web Camera Viewer (v2)

The Raspberry Pi includes an optional web service to view the camera in a browser. The viewer is independent from the original inference/TLS client and is started as a separate process.

### Features

- Browser-based live preview using MJPEG.
- HTTP Basic Authentication (username and password required).
- Camera capture starts only when an authenticated viewer requests the video.
- Start/Stop controls in the web interface.
- Camera capture is released when the last video viewer disconnects.
- Configurable camera device, resolution, FPS, JPEG quality, host and port.
- No changes to the original `capacete_hibrido.py` inference loop.

### Installation (Raspberry Pi)

Open the new folder:

```bash
cd Projeto_Capacete_Final/RASPBERRY_PI/web_camera
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
nano .env
```

Set your own credentials in `.env`:

```ini
PERCEPTA_WEB_HOST=0.0.0.0
PERCEPTA_WEB_PORT=8080
PERCEPTA_WEB_USER=percepta
PERCEPTA_WEB_PASSWORD=CHANGE-ME-TO-A-LONG-RANDOM-PASSWORD
PERCEPTA_CAMERA_DEVICE=0
PERCEPTA_WEB_WIDTH=640
PERCEPTA_WEB_HEIGHT=480
PERCEPTA_WEB_FPS=15
PERCEPTA_WEB_JPEG_QUALITY=80
```

Start the viewer:

```bash
./run.sh
```

Find the Raspberry Pi IP address:

```bash
hostname -I
```

Open `http://RASPBERRY_PI_IP:8080` from a device on the same trusted network. The browser will request the configured username and password. Select **Start camera** to begin streaming and **Stop camera** to release it.

### Security

HTTP Basic Authentication over plain HTTP does not encrypt credentials or video. Use this service only on a trusted local network or through a VPN. For access over the Internet, put it behind an HTTPS reverse proxy; do not expose port 8080 directly.

### Camera access limitation

A camera device is commonly exclusive to one process. The original `capacete_hibrido.py` keeps the camera open while it is running, so the independent web viewer may not be able to open the same device at the same time. To support browser viewing while inference continues, a future integration must share a single frame-capture producer between the inference and web components. This version deliberately avoids changing the known-working inference program.

---

## 📷 Visualizador Web da Câmera sob Demanda (v2)

O Raspberry Pi agora possui um serviço web opcional para visualizar a câmera pelo navegador. Ele funciona em um processo separado e não altera o cliente original de inferência/TLS.

### Funcionalidades

- Visualização ao vivo pelo navegador usando MJPEG.
- Autenticação HTTP Basic com usuário e senha obrigatórios.
- A câmera só começa a capturar quando um usuário autenticado solicita o vídeo.
- Controles **Iniciar câmera** e **Parar câmera**.
- A captura é liberada quando o último visualizador desconecta.
- Configuração de dispositivo da câmera, resolução, FPS, qualidade JPEG, endereço e porta.
- O loop original de inferência em `capacete_hibrido.py` permanece inalterado.

### Instalação no Raspberry Pi

Acesse a nova pasta:

```bash
cd Projeto_Capacete_Final/RASPBERRY_PI/web_camera
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
nano .env
```

Configure suas próprias credenciais no arquivo `.env`:

```ini
PERCEPTA_WEB_HOST=0.0.0.0
PERCEPTA_WEB_PORT=8080
PERCEPTA_WEB_USER=percepta
PERCEPTA_WEB_PASSWORD=ALTERE-PARA-UMA-SENHA-ALEATORIA-FORTE
PERCEPTA_CAMERA_DEVICE=0
PERCEPTA_WEB_WIDTH=640
PERCEPTA_WEB_HEIGHT=480
PERCEPTA_WEB_FPS=15
PERCEPTA_WEB_JPEG_QUALITY=80
```

Inicie o serviço:

```bash
./run.sh
```

Descubra o IP do Raspberry Pi:

```bash
hostname -I
```

No navegador de um dispositivo conectado à mesma rede confiável, acesse:

```
http://IP_DO_RASPBERRY:8080
```

Informe usuário e senha e clique em **Iniciar câmera**. Para interromper a transmissão e liberar a câmera, clique em **Parar câmera**.

### Segurança

A autenticação HTTP Basic em HTTP simples não criptografa as credenciais nem o vídeo. Utilize somente em rede local confiável ou por VPN. Para acesso pela Internet, coloque o serviço atrás de um proxy reverso com HTTPS. Não exponha diretamente a porta 8080.

### Limitação de acesso à câmera

Normalmente, o dispositivo de câmera só pode ser controlado por um processo de cada vez. Como o `capacete_hibrido.py` mantém a câmera aberta enquanto está em execução, o visualizador web independente pode não conseguir abrir o mesmo dispositivo simultaneamente. Para visualizar o vídeo no navegador enquanto a inferência continua, será necessário compartilhar um único produtor de frames entre os dois componentes. Esta versão evita deliberadamente alterar o programa de inferência que já funciona.

### Estrutura atualizada

```text
Projeto_Capacete_Final
├── NITRO_5
│   ├── server_nitro_secure.py
│   ├── requirements.txt
│   └── keys/
└── RASPBERRY_PI
    ├── capacete_hibrido.py
    ├── requirements.txt
    ├── keys/
    └── web_camera/
        ├── camera_web.py
        ├── requirements.txt
        ├── .env.example
        ├── .gitignore
        ├── run.sh
        └── README.md
```

> **Versioning / Versionamento:** the web camera viewer is currently isolated in the `feature/web-camera-viewer-v2` branch. The `main` branch remains unchanged. / O visualizador web está isolado na branch `feature/web-camera-viewer-v2`. A branch `main` permanece inalterada.
