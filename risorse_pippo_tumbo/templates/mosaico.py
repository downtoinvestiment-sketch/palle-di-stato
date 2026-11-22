"""Mosaico di verifica dal video finito. Uso: python templates/mosaico.py out/NOME.mp4 /tmp/mosaico.png 1 3.5 6 9 ...  (secondi)"""
import sys, subprocess, os
from PIL import Image
mp4, out, ts = sys.argv[1], sys.argv[2], sys.argv[3:]
ims = []
for i, t in enumerate(ts):
    p = '/tmp/_mz_%02d.png' % i; subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-ss', t, '-i', mp4, '-frames:v', '1', '-vf', 'scale=216:384', p], check=True); ims.append(Image.open(p))
cols = 7; rows = (len(ims) + cols - 1) // cols; M = Image.new('RGB', (216 * cols, 384 * rows))
for i, im in enumerate(ims): M.paste(im, ((i % cols) * 216, (i // cols) * 384))
M.save(out); print(out, M.size)
