#!/bin/bash
# Tiene vivo il render: se non c'e' un processo e mancano fotogrammi, lo fa ripartire (render_t004.py salta i PNG gia' fatti).
# Uso in un ciclo (i comandi in primo piano durano al massimo 10 minuti):
#   end=$((SECONDS+570)); until [ $(ls ../tNNN/final | wc -l) -ge TOT ] || [ $SECONDS -ge $end ]; do bash templates/keep.sh NNN TOT; sleep 30; done
T=$1; TOT=$2; W=${3:-1080}; H=${4:-1920}; S=${5:-6}; PY=${PY:-/home/claude/venv/bin/python}
cd "$(dirname "$0")/../scripts"
if [ $(pgrep -f render_t004 | wc -l) -eq 0 ] && [ $(ls ../t$T/final 2>/dev/null | wc -l) -lt $TOT ]; then
  mkdir -p ../t$T/final; (nohup $PY render_t004.py ../t$T/pippo_t$T.blend ../t$T/final $W $H $S 1-$TOT > ../t$T/render.log 2>&1 &); echo restarted
fi
ls ../t$T/final | wc -l
