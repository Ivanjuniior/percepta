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
