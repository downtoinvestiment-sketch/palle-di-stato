#!/bin/bash
# riprende il render del 030: toglie i PNG rotti in fondo, rilancia keep.sh e lo tiene vivo per ~9 minuti
cd "$(dirname "$0")/.."
[ $(pgrep -f render_t004 | wc -l) -eq 0 ] && /home/claude/venv/bin/python - <<'PY'
from PIL import Image
import glob, os
for f in sorted(glob.glob('t030/final/f*.png'))[-4:]:
    try: Image.open(f).load()
    except Exception: os.remove(f); print('tolto', f)
PY
end=$((SECONDS+${1:-540}))
until [ $(ls t030/final | wc -l) -ge 1075 ] || [ $SECONDS -ge $end ]; do bash templates/keep.sh 030 1075 1080 1920 3 > /dev/null; sleep 30; done
ls t030/final | wc -l
