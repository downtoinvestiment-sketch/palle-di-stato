"""Video 027: mette la bocca rifatta (t027/bocca, da render027_bocca.py) sopra i fotogrammi del render intero (t027/final) e scrive
t027/final2. Si fonde solo un cerchio stretto attorno alla bocca (centro e raggio da centri027_bocca.py), col bordo sfumato; i
fotogrammi dove la faccia non si vede vengono copiati cosi' come sono.
Controllo delle texture: se nel cerchio della zona rifatta compaiono pixel magenta (texture mancante) il fotogramma NON viene composto
e finisce in t027/bocca/da_rifare.json (va rifatto con render027_bocca.py dopo aver tolto la sua voce da bordi.json).
Uso: python componi027_bocca.py"""
import sys, os, json, shutil
import numpy as np
from PIL import Image
QUI = os.path.dirname(os.path.abspath(__file__)); T27 = os.path.join(QUI, '..', 't027'); A = os.path.join(T27, 'final'); B = os.path.join(T27, 'bocca'); C = os.path.join(T27, 'final2')
os.makedirs(C, exist_ok=True); bordi = json.load(open(os.path.join(B, 'bordi.json'))); centri = json.load(open(os.path.join(B, 'centri.json'))); fatti = 0; rifare = []
for f in range(1, 1167):
    a = os.path.join(A, 'f%04d.png' % f); c = os.path.join(C, 'f%04d.png' % f); b = bordi.get(str(f))
    if not os.path.exists(a) or str(f) not in bordi: continue                      # non ancora rifatto: lo salta (si rilancia alla fine)
    if b is None:
        if not os.path.exists(c): shutil.copyfile(a, c)
        continue
    if os.path.exists(c): continue                                                  # gia' composto (si puo' rilanciare)
    x0, y0, x1, y1 = b; cx, cy, r = centri[str(f)]
    va = np.asarray(Image.open(a).convert('RGB'), np.float32); vb = np.asarray(Image.open(os.path.join(B, 'b%04d.png' % f)).convert('RGB'), np.float32)
    yy, xx = np.mgrid[y0:y1, x0:x1]; R = max(6.0, 0.74 * r); sf = max(3.0, 0.14 * r)
    d = np.sqrt((xx + 0.5 - cx) ** 2 + (yy + 0.5 - cy) ** 2); m = np.clip((R - d) / sf, 0, 1); m = m * m * (3 - 2 * m)
    orlo = np.minimum(np.minimum(xx - x0, x1 - 1 - xx), np.minimum(yy - y0, y1 - 1 - yy))  # mai oltre il rettangolo rifatto (meno 2 pixel)
    m = m * np.clip((orlo - 2) / 4.0, 0, 1)
    pa, pb = va[y0:y1, x0:x1], vb[y0:y1, x0:x1]
    magenta = (pb[:, :, 0] > 200) & (pb[:, :, 2] > 175) & (pb[:, :, 1] < 0.85 * pb[:, :, 2]) & (np.abs(pb - pa).max(axis=2) > 30) & (m > 0.2)
    if magenta.sum() > max(6, 0.004 * (m > 0.2).sum()):
        rifare.append(f); continue
    out = va.copy(); out[y0:y1, x0:x1] = pa * (1 - m[:, :, None]) + pb * m[:, :, None]
    Image.fromarray(np.clip(out + 0.5, 0, 255).astype(np.uint8)).save(c + '.tmp.png'); os.replace(c + '.tmp.png', c); fatti += 1
json.dump(rifare, open(os.path.join(B, 'da_rifare.json'), 'w'))
print('composti', fatti, 'fotogrammi; da rifare (texture mancanti nel cerchio):', len(rifare), rifare[:30])
