# Percepta — Visualizador Web da Câmera (v2)

Serviço opcional e independente para visualizar a câmera do Raspberry Pi 4 pelo navegador. O serviço **não altera** `capacete_hibrido.py`, o protocolo TLS de inferência ou o fluxo de áudio. A câmera só é aberta quando um usuário autenticado inicia a transmissão em `/video`; ao desconectar ou clicar em **Parar câmera**, a captura é liberada.

## Recursos

- Página web com botão iniciar/parar.
- Vídeo ao vivo MJPEG, sem inferência e sem envio contínuo ao Nitro.
- HTTP Basic Authentication obrigatório (usuário e senha).
- Uma única captura OpenCV compartilhada entre visualizadores simultâneos.
- Fechamento da câmera quando não há clientes de vídeo.
- Configuração por variáveis de ambiente; nenhum segredo versionado.

## Instalação no Raspberry Pi

Na pasta `Projeto_Capacete_Final/RASPBERRY_PI/web_camera`:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
nano .env
```

Edite ao menos `PERCEPTA_WEB_USER` e `PERCEPTA_WEB_PASSWORD`. Use uma senha aleatória longa, com 16 caracteres ou mais. Não reutilize a senha do Raspberry Pi.

Para carregar as variáveis e iniciar:

```bash
set -a
source .env
set +a
python3 camera_web.py
```

O terminal exibirá o endereço, por exemplo `http://0.0.0.0:8080`. Em outro dispositivo da mesma rede, acesse `http://IP_DO_RASPBERRY:8080`, informe usuário/senha e clique em **Iniciar câmera**.

Descubra o IP do Raspberry Pi com:

```bash
hostname -I
```

## Configurações

| Variável | Padrão | Descrição |
|---|---:|---|
| `PERCEPTA_WEB_HOST` | `0.0.0.0` | Interface de escuta |
| `PERCEPTA_WEB_PORT` | `8080` | Porta HTTP |
| `PERCEPTA_WEB_USER` | — | Usuário obrigatório |
| `PERCEPTA_WEB_PASSWORD` | — | Senha obrigatória (mínimo 12 caracteres) |
| `PERCEPTA_CAMERA_DEVICE` | `0` | Índice ou caminho da câmera |
| `PERCEPTA_WEB_WIDTH` | `640` | Largura |
| `PERCEPTA_WEB_HEIGHT` | `480` | Altura |
| `PERCEPTA_WEB_FPS` | `15` | Quadros por segundo (máximo 30) |
| `PERCEPTA_WEB_JPEG_QUALITY` | `80` | Qualidade JPEG (40–95) |

## Segurança importante

HTTP Basic Authentication não cifra a senha: **não exponha esta porta diretamente à Internet** em HTTP. Use apenas em uma LAN confiável ou VPN, ou coloque o serviço atrás de um proxy HTTPS (por exemplo, Caddy/Nginx com TLS). Não faça port-forward público da porta 8080. Em HTTP simples, qualquer pessoa capaz de observar o tráfego local pode capturar credenciais e vídeo.

O serviço exige usuário e senha e se recusa a iniciar sem essas variáveis. O arquivo `.env` está ignorado pelo Git.

## Uso simultâneo com o Percepta

Execute o serviço web em um terminal/processo separado. O programa original `capacete_hibrido.py` continua com seu comportamento normal e não precisa ser modificado. **A câmera física pode não permitir dois processos simultâneos**. Se o Percepta já estiver usando a webcam, o visualizador poderá falhar ao abri-la; interrompa o uso original antes de iniciar a visualização. Uma futura integração com um único produtor de frames pode permitir compartilhar a mesma câmera sem disputa, mas exigiria modificar o ciclo de captura funcional.

## Endpoints

- `/` — interface web autenticada.
- `/video` — fluxo MJPEG autenticado, inicia a captura sob demanda.
- `/health` — estado simples autenticado do serviço.

## Observação sobre a versão

Esta implementação está isolada na branch `feature/web-camera-viewer-v2`. Não substitui nem modifica a branch `main`.
