#!/bin/bash
# Monta il video 027: fotogrammi + audio (canzone + effetti) + testo della canzone. Uso, dalla cartella del progetto:
#   bash scripts/monta027.sh [NUMERO_FOTOGRAMMI] [NOME]      (default: 1166 fotogrammi, out/pippo_t027.mp4)
# Prima controlla che tutti i PNG siano interi (dopo un riavvio dell'ambiente un PNG puo' restare troncato).
N=${1:-1166}; NAME=${2:-pippo_t027}; PY=${PY:-/home/claude/venv/bin/python}; export FOTOGRAMMI=${FOTOGRAMMI:-final2}; CRF=${CRF:-18}   # final2 = con la bocca corretta (componi027_bocca.py)
cd "$(dirname "$0")/.."; mkdir -p out
$PY - "$N" <<'PYEOF' || exit 1
import sys, os
from PIL import Image
n = int(sys.argv[1]); rotti = []
for f in range(1, n + 1):
    p = 't027/%s/f%04d.png' % (os.environ['FOTOGRAMMI'], f)
    try:
        im = Image.open(p); im.load(); assert im.size == (1080, 1920)
    except Exception as e:
        rotti.append(f)
        if os.path.exists(p): os.remove(p)
print('PNG controllati:', n, 'rotti o mancanti:', rotti[:20])
sys.exit(1 if rotti else 0)
PYEOF
PRIMO=${PRIMO:-1}                                   # primo fotogramma del montaggio (41 = parte da «Si e' rotta la macchina», senza il coro iniziale)
DUR=$($PY -c "print(round(($N - $PRIMO + 1) / 24.0, 3))"); DA=$($PY -c "print(round(($PRIMO - 1) / 24.0, 4))")
ffmpeg -y -loglevel error -framerate 24 -start_number $PRIMO -i t027/$FOTOGRAMMI/f%04d.png -ss $DA -i audio/t027.wav -af "afade=t=in:st=0:d=0.03" \
  -vf "eq=saturation=1.18:contrast=1.03,ass=t027/captions.ass:fontsdir=assets/font" \
  -c:v libx264 -crf $CRF -preset medium -pix_fmt yuv420p -r 24 -c:a aac -b:a 256k -t $DUR -movflags +faststart out/$NAME.mp4 && ls -la out/$NAME.mp4
