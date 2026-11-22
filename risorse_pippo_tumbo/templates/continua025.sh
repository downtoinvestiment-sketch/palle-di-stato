#!/bin/bash
# riprende il render del 025: toglie i PNG rotti in fondo, rilancia keep.sh e lo tiene vivo per ~8,5 minuti
cd /home/claude/pippo
[ $(pgrep -f render_t004 | wc -l) -eq 0 ] && /home/claude/venv/bin/python - <<'PY'
from PIL import Image
import glob, os
for f in sorted(glob.glob('t025/final/f*.png'))[-4:]:
    try: Image.open(f).load()
    except Exception: os.remove(f); print('tolto', f)
PY
end=$((SECONDS+510))
until [ $(ls t025/final | wc -l) -ge 897 ] || [ $SECONDS -ge $end ]; do bash templates/keep.sh 025 897 1080 1920 4 > /dev/null; sleep 30; done
ls t025/final | wc -l
