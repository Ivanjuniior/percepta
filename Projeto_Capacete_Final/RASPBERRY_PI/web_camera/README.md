# Percepta — Visualizador Web da Câmera (v2)

Serviço opcional e independente para ver a câmera do Raspberry Pi 4 pelo navegador. Não modifica `capacete_hibrido.py`, o protocolo TLS nem o processamento de IA. A câmera só é aberta quando um cliente autenticado solicita `/video`; ao parar ou desconectar, ela é liberada.

## Instalação

Na pasta `Projeto_Capacete_Final/RASPBERRY_PI/web_camera`:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
nano .env
```

Defina usuário e senha próprios em `.env`. Use senha aleatória com pelo menos 16 caracteres. Inicie:

```bash
./run.sh
```

Descubra o IP do Pi com `hostname -I` e acesse de um dispositivo da rede:
`http://IP_DO_RASPBERRY:8080`

O navegador solicitará usuário/senha via HTTP Basic. Depois clique em **Iniciar câmera**.

## Configuração

| Variável | Padrão | Descrição |
|---|---:|---|
| `PERCEPTA_WEB_HOST` | `0.0.0.0` | Interface |
| `PERCEPTA_WEB_PORT` | `8080` | Porta |
| `PERCEPTA_WEB_USER` | — | Usuário obrigatório |
| `PERCEPTA_WEB_PASSWORD` | — | Senha obrigatória (mínimo 12 caracteres) |
| `PERCEPTA_CAMERA_DEVICE` | `0` | Índice ou caminho da câmera |
| `PERCEPTA_WEB_WIDTH` | `640` | Largura |
| `PERCEPTA_WEB_HEIGHT` | `480` | Altura |
| `PERCEPTA_WEB_FPS` | `15` | FPS (máximo 30) |
| `PERCEPTA_WEB_JPEG_QUALITY` | `80` | Qualidade JPEG (40–95) |

## Segurança

HTTP Basic sobre HTTP **não cifra as credenciais nem o vídeo**. Use apenas em rede local confiável ou VPN. Para acesso pela Internet, coloque atrás de um proxy HTTPS e não exponha diretamente a porta 8080. O serviço se recusa a iniciar sem autenticação. O arquivo `.env` não deve ser versionado.

## Câmera já ocupada

O OpenCV normalmente não permite que dois processos controlem simultaneamente a mesma webcam. Como o `capacete_hibrido.py` mantém a câmera aberta durante sua execução, o visualizador independente pode não conseguir abri-la enquanto o Percepta estiver operando. Este recurso foi deixado fora do ciclo original para preservar o sistema funcional. Para ver a imagem sem interromper o processamento, será necessário uma etapa futura de compartilhamento do mesmo produtor de frames dentro do processo principal.

## Endpoints

- `/` interface web autenticada
- `/video` transmissão MJPEG autenticada
- `/health` estado do serviço autenticado

Branch de desenvolvimento: `feature/web-camera-viewer-v2`. A branch `main` permanece intocada.
