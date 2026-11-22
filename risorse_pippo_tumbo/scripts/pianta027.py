"""Pianta dall'alto della coreografia del video 027 (senza render): percorso, appoggi dei piedi, punti dove arrivano mani e piedi
nei colpi. Con la citta' (se anim027 ha scritto ../t027/piano.json) disegna anche palazzi, bersagli, folla ed eventi.
Uso: python -I scripts/pianta027.py  -> ../out/pianta027.png"""
import sys, os, math, json
QUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, QUI)
import bpy  # noqa
from mathutils import Vector
from PIL import Image, ImageDraw
import coreo027 as c, mocap_pippo as mp

S = 150.0; X0, X1, Y0, Y1 = -4.2, 4.2, -5.6, 6.2


def px(x, y):
    return ((x - X0) * S, (Y1 - y) * S)


if __name__ == '__main__':
    seq, inizi, posto = c.sequenza()
    bm, bl = c.braccia(Vector((-0.553, -0.829, 0.099)), Vector((0.22, -0.86, 0.38)))
    mp.cinematica(seq, posto=posto, braccio_mic=bm, braccio_libero=bl)
    im = Image.new('RGB', (int((X1 - X0) * S), int((Y1 - Y0) * S)), (245, 245, 240)); d = ImageDraw.Draw(im)
    for gx in range(int(X0), int(X1) + 1):
        d.line([px(gx, Y0), px(gx, Y1)], fill=(225, 225, 225)); d.text(px(gx + 0.03, Y1 - 0.02), str(gx), fill=(120, 120, 120))
    for gy in range(int(Y0), int(Y1) + 1):
        d.line([px(X0, gy), px(X1, gy)], fill=(225, 225, 225)); d.text(px(X0 + 0.03, gy + 0.13), str(gy), fill=(120, 120, 120))
    piano = os.path.join(QUI, '..', 't027', 'piano.json')
    if os.path.exists(piano):
        P = json.load(open(piano))
        for b in P.get('palazzi', []):
            col = {'su': (190, 190, 200), 'piatto': (235, 170, 120), 'caduto': (240, 120, 120)}[b['stato']]
            if b.get('bersaglio'): col = (120, 160, 255) if b['stato'] == 'su' else (150, 120, 255)
            d.rectangle([px(b['x'] - b['sx'] / 2, b['y'] + b['sy'] / 2), px(b['x'] + b['sx'] / 2, b['y'] - b['sy'] / 2)], fill=col, outline=(90, 90, 90))
            d.text(px(b['x'] - 0.12, b['y'] + 0.06), '%.1f' % b['h'], fill=(0, 0, 0))
            if b.get('ret'):
                r = b['ret']; d.rectangle([px(r[0], r[3]), px(r[1], r[2])], outline=(220, 60, 60))
            if b.get('f'): d.text(px(b['x'] - 0.12, b['y'] - 0.04), '%.1fs' % ((b['f'] - 1) / c.FPS), fill=(160, 0, 0))
        for g in P.get('gente', []):
            q = px(g[0], g[1]); d.ellipse([q[0] - 2, q[1] - 2, q[0] + 2, q[1] + 2], fill=(40, 160, 60))
        for a in P.get('auto', []):
            q = px(a[0], a[1]); d.rectangle([q[0] - 4, q[1] - 4, q[0] + 4, q[1] + 4], outline=(200, 140, 0))
    colori = [(30, 90, 200), (200, 60, 40), (20, 140, 60), (150, 60, 170), (220, 140, 20), (0, 150, 160)]
    nomi = sorted(inizi.items(), key=lambda q: q[1])
    for i, (nome, k0) in enumerate(nomi):
        k1 = nomi[i + 1][1] if i + 1 < len(nomi) else len(seq)
        pts = [px(s['mondo'].x, s['mondo'].y) for s in seq[k0:k1 + 1]]
        d.line(pts, fill=colori[i % 6], width=3)
        d.text((pts[0][0] + 5, pts[0][1] - 12), '%s %.1fs' % (nome, k0 / c.FPS), fill=colori[i % 6])
    prev = None
    for k, s in enumerate(seq):                                                # appoggi: un puntino dove atterra ogni piede
        if s['piede'] != prev and not s['volo']:
            p = s['suole'][s['piede']]; q = px(p.x, p.y); d.ellipse([q[0] - 4, q[1] - 4, q[0] + 4, q[1] + 4], outline=(0, 0, 0))
        prev = s['piede']
    for h in c.punti_colpo(seq):
        q = px(h['x'], h['y']); o = px(h['cx'], h['cy'])
        d.line([o, q], fill=(255, 0, 180), width=2); d.ellipse([q[0] - 5, q[1] - 5, q[0] + 5, q[1] + 5], fill=(255, 0, 180))
        d.text((q[0] + 6, q[1] - 5), '%s z%.2f %.1fs' % (h['nome'], h['z'], h['t']), fill=(160, 0, 110))
        print(h)
    os.makedirs(os.path.join(QUI, '..', 'out'), exist_ok=True); im.save(os.path.join(QUI, '..', 'out', 'pianta027.png'))
    print('appoggi sulle battute dispari della camminata:', [(round(k / c.FPS, 2), round(s['suole'][s['piede']].y, 2)) for k, s in enumerate(seq[:225]) if k and s['piede'] != seq[k - 1]['piede']])
