#!/bin/bash
# riprende il render del 027: toglie i PNG rotti in fondo, rilancia keep.sh e lo tiene vivo per ~8,5 minuti
cd /home/claude/pippo
[ $(pgrep -f render_t004 | wc -l) -eq 0 ] && /home/claude/venv/bin/python - <<'PY'
from PIL import Image
import glob, os
for f in sorted(glob.glob('t027/final/f*.png'))[-4:]:
    try: Image.open(f).load()
    except Exception: os.remove(f); print('tolto', f)
PY
end=$((SECONDS+510))
until [ $(ls t027/final | wc -l) -ge 1094 ] || [ $SECONDS -ge $end ]; do bash templates/keep.sh 027 1094 1080 1920 4 > /dev/null; sleep 30; done
ls t027/final | wc -l
