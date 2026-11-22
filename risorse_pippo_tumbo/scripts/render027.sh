#!/bin/bash
# Tiene vivo il render finale del video 027 finche' non ci sono tutti i fotogrammi. Un solo render alla volta (limite di memoria).
# Uso: (setsid nohup bash scripts/render027.sh > /dev/null 2>&1 &)   Stato: ls t027/final | grep -c '^f'   Log: t027/render.log
cd "$(dirname "$0")"; TOT=${1:-1166}; PY=${PY:-/home/claude/venv/bin/python}
exec 9> /tmp/render027.lock; flock -n 9 || exit 0
while [ $(ls ../t027/final 2>/dev/null | grep -c '^f') -lt $TOT ]; do
  $PY render027.py >> ../t027/render.log 2>&1
  sleep 3
done
echo "TUTTI I FOTOGRAMMI $(date)" >> ../t027/render.log
