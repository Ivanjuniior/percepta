#!/usr/bin/env bash
set -u
cd "$(dirname "$0")"
if [ ! -f .env ]; then
  echo "Arquivo .env ausente. Copie .env.example para .env e configure usuário/senha." >&2
  exit 1
fi
set -a
# shellcheck disable=SC1091
source .env
set +a
exec python3 camera_web.py
