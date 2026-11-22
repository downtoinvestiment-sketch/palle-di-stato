#!/bin/bash
# Tiene vivo il rifacimento della zona della bocca (render027_bocca.py) finche' non ha passato tutti i fotogrammi.
# Uso: (setsid nohup bash scripts/render027_bocca.sh > /dev/null 2>&1 &)    Log: t027/bocca.log
cd "$(dirname "$0")"; PY=${PY:-/home/claude/venv/bin/python}
exec 9> /tmp/render027_bocca.lock; flock -n 9 || exit 0
until grep -q '^FINITO' ../t027/bocca.log 2>/dev/null; do
  $PY render027_bocca.py 2>&1 | grep -E "^bocca|^FINITO|Traceback|Error:" >> ../t027/bocca.log
  sleep 3
done
