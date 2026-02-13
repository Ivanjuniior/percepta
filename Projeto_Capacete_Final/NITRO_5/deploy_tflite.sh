#!/bin/bash
# Script de Conversão para o Modelo 'S' (Small)
mkdir -p temp_build
cd temp_build

echo "Criando ambiente virtual..."
python3 -m venv .venv || { echo "Instale python3-venv"; exit 1; }
source .venv/bin/activate

echo "Instalando dependências..."
pip install ultralytics
pip install "numpy<2.0"

echo "Convertendo yolov8s.pt para TFLite Otimizado..."
# Note que agora usamos yolov8s.pt (Small)
yolo export model=yolov8s.pt format=tflite int8=true imgsz=320 data=coco128.yaml

# Tenta encontrar e mover
echo "Procurando arquivo gerado..."
find . -name "*.tflite" -type f -exec mv {} ../yolov8s.tflite \; -quit

deactivate
cd ..
# rm -rf temp_build  <-- REMOVIDO PARA DEBUG MANUAL

if [ -f "yolov8s.tflite" ]; then
    echo "SUCESSO: 'yolov8s.tflite' movido para a pasta principal!"
    echo "Pode apagar a pasta temp_build e copiar o arquivo pro Pi."
else
    echo "AVISO: O arquivo não foi movido automaticamente."
    echo "Verifique dentro da pasta 'temp_build' e mova o .tflite manualmente."
fi
