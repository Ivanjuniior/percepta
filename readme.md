# PROJETO PERCEPTA

## FUNCIONAMENTO DO PROJETO

* Baixe o projeto. Ele possui duas pastas:

  * **`NITRO_5`**
  * **`RASPBERRY_PI`**
* A pasta **`NITRO_5`** deve ficar dentro do servidor.
* A pasta **`RASPBERRY_PI`** deve ficar dentro do Raspberry Pi 4 (modelo testado).

---

## MODO DE USO

1. Atualize o Python.
2. No arquivo **`capacete_hibrido.py`**, altere a variável:

   ```python
   SERVER_IP
   ```
3. No arquivo **`server_nitro_secure.py`**, altere a variável:

   ```python
   HOST_IP
   ```
4. Crie e ative o ambiente virtual:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
5. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```
6. Execute o projeto:

   **NITRO_5**

   ```bash
   python3 server_nitro_secure.py
   ```

   **RASPBERRY_PI**

   ```bash
   python3 capacete_hibrido.py
   ```

---

## BOTÃO

O botão está conectado ao **GPIO21**.

* Ao ligar o Raspberry Pi e carregar o sistema:

  * **Se o botão NÃO for pressionado → modo remoto**
  * **Se o botão for pressionado → modo local**

---

## MODELO TREINADO

No arquivo **`server_nitro_secure.py`**, altere a variável para o modelo presente na pasta raiz:

```python
MODEL_PATH = "yolov8x.pt"
```

No arquivo **`capacete_hibrido.py`**, altere a variável para o modelo presente na pasta raiz:

```python
MODEL_FILE = "yolov8s.tflite"
```

---

## ARQUITETURA DO SISTEMA

```
Projeto_Capacete_Final
├── NITRO_5
│   ├── deploy_tflite.sh
│   ├── gen_keys.sh
│   ├── keys
│   │   ├── ca.crt
│   │   ├── ca.key
│   │   ├── client.crt
│   │   ├── client.key
│   │   ├── server.crt
│   │   └── server.key
│   ├── requirements.txt
│   └── server_nitro_secure.py
└── RASPBERRY_PI
    ├── capacete_hibrido.py
    ├── keys
    │   ├── ca.crt
    │   ├── ca.key
    │   ├── client.crt
    │   ├── client.key
    │   ├── server.crt
    │   └── server.key
    ├── requirements.txt
    └── yolov8s.tflite
```
