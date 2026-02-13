#!/bin/bash
mkdir -p keys
cd keys
echo "Gerando CA..."
openssl genrsa -out ca.key 4096
openssl req -new -x509 -days 3650 -key ca.key -out ca.crt -subj "/CN=CapaceteCA"
echo "Gerando Server..."
openssl genrsa -out server.key 2048
openssl req -new -key server.key -out server.csr -subj "/CN=Nitro5Server"
openssl x509 -req -days 365 -in server.csr -CA ca.crt -CAkey ca.key -set_serial 01 -out server.crt
echo "Gerando Client..."
openssl genrsa -out client.key 2048
openssl req -new -key client.key -out client.csr -subj "/CN=RaspberryPiClient"
openssl x509 -req -days 365 -in client.csr -CA ca.crt -CAkey ca.key -set_serial 02 -out client.crt
rm *.csr
echo "Chaves OK."
