"""Guarda in fretta una cartella di registrazioni BVH (formato CMU/cgspeed) portate su Pippo: numeri e omini stilizzati.
Uso: python -I scripts/mocap_esplora.py CARTELLA_BVH CARTELLA_USCITA [nome1 nome2 ...]
Per ogni registrazione scrive un'immagine con 16 pose viste di fronte e il percorso visto dall'alto."""
import sys, os, math, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy  # noqa
from mathutils import Vector, Matrix
from PIL import Image, ImageDraw
import mocap_pippo as mp


def scheletro(s):
    """Punti dell'omino nel mondo per un fotogramma di sequenza()."""
    Rz = Matrix.Rotation(s['yaw'], 3, 'Z'); base = Vector(s['loc'])
    qb = s['qb'].to_matrix(); P = {}
    P['bacino'] = base + Vector((0, 0, 0.70))
    for k in 'LR':
        P['anca' + k] = base + Rz @ mp.ANCA[k]
        P['piede' + k] = base + Rz @ (mp.ANCA[k] + mp.GAMBA * s['gambe'][k])
        sp = Vector(((0.31 if k == 'R' else -0.31), 0, 0.65))                      # spalla nel sistema del busto (perno a z 0.7)
        P['spalla' + k] = base + Rz @ (Vector((0, 0, 0.70)) + qb @ sp)
        P['mano' + k] = P['spalla' + k] + Rz @ (qb @ (0.51 * s['braccia'][k]))
    P['collo'] = base + Rz @ (Vector((0, 0, 0.70)) + qb @ Vector((0, 0, 0.75)))
    P['testa'] = base + Rz @ (Vector((0, 0, 0.70)) + qb @ Vector((0, 0, 1.07)))
    P['naso'] = P['testa'] + Rz @ (qb @ Vector((0, -0.36, 0)))
    return P


def numeri(nome, seq, b):
    n = len(seq); dur = n / 24.0
    cambi = sum(1 for i in range(1, n) if seq[i]['piede'] != seq[i - 1]['piede'])
    path = sum((Vector(seq[i]['loc']).xy - Vector(seq[i - 1]['loc']).xy).length for i in range(1, n))
    netto = (Vector(seq[-1]['loc']).xy - Vector(seq[0]['loc']).xy).length
    giro = sum(abs(seq[i]['yaw'] - seq[i - 1]['yaw']) for i in range(1, n))
    alz = max(max(0.0, -s['gambe'][k].z) for s in seq for k in 'LR')
    piede_alto = max(max(Vector(s['loc']).z + 0.70 + mp.GAMBA * s['gambe'][k].z for k in 'LR') for s in seq)
    mani_su = sum(1 for s in seq if max(s['braccia'][k].z for k in 'LR') > 0.3) / n
    volo = sum(1 for s in seq if s['volo']) / n
    zmax = max(s['loc'][2] for s in seq)
    return dict(nome=nome, fps=round(1 / b.dt), durata=round(dur, 2), passi_al_s=round(cambi / dur, 2), percorso=round(path, 2), netto=round(netto, 2),
                giri=round(giro / (2 * math.pi), 2), piede_alto=round(piede_alto, 2), mani_su=round(mani_su, 2), volo=round(volo, 2), salto=round(zmax - 0.0, 2))


def disegna(nome, seq, out, celle=16):
    W, H = 150, 210; im = Image.new('RGB', (W * celle, H + 220), (250, 250, 250)); d = ImageDraw.Draw(im)
    n = len(seq)
    for c in range(celle):
        s = seq[int(c * (n - 1) / (celle - 1))]; P = scheletro(s); base = Vector(s['loc'])
        def px(v):
            return (c * W + W / 2 + (v.x - base.x) * 78, H - 12 - v.z * 78)
        dietro = math.cos(s['yaw']) < 0                                           # di spalle alla camera
        d.line([px(Vector((base.x - 0.9, 0, 0))), px(Vector((base.x + 0.9, 0, 0)))], fill=(200, 200, 200))
        for k, col in (('L', (40, 90, 220)), ('R', (220, 60, 40))):
            d.line([px(P['anca' + k]), px(P['piede' + k])], fill=col, width=5)
            d.line([px(P['spalla' + k]), px(P['mano' + k])], fill=col, width=4)
        d.line([px(P['bacino']), px(P['collo'])], fill=(60, 60, 60), width=7)
        t = px(P['testa']); r = 20
        d.ellipse([t[0] - r, t[1] - r, t[0] + r, t[1] + r], outline=(60, 60, 60), width=3, fill=(160, 160, 160) if dietro else (255, 235, 200))
        ns = px(P['naso']); d.line([t, ns], fill=(0, 0, 0), width=2)
        d.text((c * W + 4, 2), '%.1fs' % (int(c * (n - 1) / (celle - 1)) / 24.0), fill=(0, 0, 0))
    # percorso dall'alto
    xs = [s['loc'][0] for s in seq]; ys = [s['loc'][1] for s in seq]
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2; sc = min(60.0, 190.0 / max(0.5, max(xs) - min(xs), max(ys) - min(ys)))
    ox, oy = 130, H + 110
    pts = [(ox + (x - cx) * sc, oy + (y - cy) * sc) for x, y in zip(xs, ys)]
    d.line(pts, fill=(0, 120, 0), width=2); d.ellipse([pts[0][0] - 4, pts[0][1] - 4, pts[0][0] + 4, pts[0][1] + 4], fill=(0, 160, 0))
    for i in range(0, n, 12):
        a = seq[i]['yaw']; d.line([pts[i], (pts[i][0] + 9 * math.sin(a), pts[i][1] + 9 * math.cos(a))], fill=(200, 0, 0))
    d.text((270, H + 8), nome, fill=(0, 0, 0))
    im.save(out, quality=85)


if __name__ == '__main__':
    src, dst = sys.argv[1], sys.argv[2]; os.makedirs(dst, exist_ok=True)
    nomi = sys.argv[3:] or sorted(os.path.basename(f)[:-4] for f in glob.glob(os.path.join(src, '**', '*.bvh'), recursive=True))
    for nm in nomi:
        f = glob.glob(os.path.join(src, '**', nm + '.bvh'), recursive=True)[0]
        try:
            b = mp.bvh(f); seq = mp.sequenza([mp.clip(f)])
            print(numeri(nm, seq, b), flush=True)
            disegna(nm, seq, os.path.join(dst, nm + '.jpg'))
        except Exception as e:
            print(nm, 'ERRORE', repr(e)[:200], flush=True)
