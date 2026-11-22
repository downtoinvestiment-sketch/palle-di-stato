"""Fotogrammi di prova del video 030: uno o piu' fotogrammi per inquadratura (da ../t030/shots.json) a 540x960, poi un foglio.
Uso: python prova030.py [frazioni, es. 0.5 oppure 0.2,0.8] [inquadrature, es. 3,7,12]  ->  ../t030/prova/foglio_*.jpg"""
import sys, os, json, subprocess
QUI = os.path.dirname(os.path.abspath(__file__)); T = os.path.join(QUI, '..', 't030'); OUT = os.path.join(T, 'prova'); os.makedirs(OUT, exist_ok=True)
fra = [float(x) for x in (sys.argv[1] if len(sys.argv) > 1 else '0.5').split(',')]
shots = json.load(open(os.path.join(T, 'shots.json'))); quali = [int(x) for x in sys.argv[2].split(',')] if len(sys.argv) > 2 else list(range(1, len(shots) + 1))
fr = []
for i in quali:
    a, b = shots[i - 1]
    for u in fra: fr.append((i, int(round((a + (b - a) * u) * 24)) + 1))
for i, f in fr:
    p = os.path.join(OUT, 'f%04d.png' % f)
    if os.path.exists(p): os.remove(p)
subprocess.run([sys.executable, os.path.join(QUI, 'render_t004.py'), os.path.join(T, 'pippo_t030.blend'), OUT, '540', '960', '4', ','.join(str(f) for _, f in fr)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
from PIL import Image, ImageDraw
n = len(fr); cols = 7 if n > 12 else min(n, 6); rows = (n + cols - 1) // cols; w, h = 270, 480
im = Image.new('RGB', (cols * w, rows * h), (20, 20, 20)); d = ImageDraw.Draw(im)
for k, (i, f) in enumerate(fr):
    p = os.path.join(OUT, 'f%04d.png' % f)
    if not os.path.exists(p): continue
    im.paste(Image.open(p).convert('RGB').resize((w, h)), ((k % cols) * w, (k // cols) * h)); d.text(((k % cols) * w + 6, (k // cols) * h + 4), '%d  f%d' % (i, f), fill=(255, 255, 0))
nome = os.path.join(OUT, 'foglio_%s.jpg' % ('tutto' if len(sys.argv) <= 2 else sys.argv[2].replace(',', '_'))); im.save(nome, quality=88); print(nome)
