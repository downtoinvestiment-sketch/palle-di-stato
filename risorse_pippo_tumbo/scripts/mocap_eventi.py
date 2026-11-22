"""Trova dentro una registrazione i momenti che servono alla coreografia: pugni (polso lontano dal corpo, in avanti),
calci (piede alto), salti (stacco e atterraggio), giri. Uso: python -I scripts/mocap_eventi.py file.bvh [...]"""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy  # noqa
from mathutils import Vector
import mocap_pippo as mp


def eventi(percorso, fps=24):
    pose = mp.clip(percorso, fps=fps); seq = mp.sequenza([pose], fps=fps); n = len(seq); out = dict(pugni=[], calci=[], salti=[], durata=n / fps)
    # pugni: massimo locale dell'estensione orizzontale del polso rispetto alla spalla (direzione del braccio quasi orizzontale e in avanti/di lato)
    for lp in 'LR':
        e = [math.hypot(s['braccia'][lp].x, s['braccia'][lp].y) for s in seq]      # 1 = braccio orizzontale
        v = [0.0] + [math.hypot(*(Vector(seq[i]['braccia'][lp]) - Vector(seq[i - 1]['braccia'][lp])).to_tuple()[:2]) * fps for i in range(1, n)]
        for i in range(2, n - 2):
            if e[i] > 0.88 and e[i] >= max(e[i - 2:i + 3]) and max(v[max(0, i - 6):i + 1]) > 2.5:
                if not out['pugni'] or i / fps - out['pugni'][-1][0] > 0.25 or out['pugni'][-1][1] != lp:
                    d = seq[i]['braccia'][lp]; out['pugni'].append((round(i / fps, 2), lp, round(math.degrees(math.atan2(d.x, -d.y)))))
        h = [mp.GAMBA * (1 + s['gambe'][lp].z) + s['loc'][2] for s in seq]           # quanto il piede e' alzato rispetto a quando pende dritto
        g = [math.hypot(s['gambe'][lp].x, s['gambe'][lp].y) for s in seq]
        for i in range(2, n - 2):
            if g[i] > 0.62 and g[i] >= max(g[i - 3:i + 4]) and not seq[i]['volo']:
                if not out['calci'] or i / fps - out['calci'][-1][0] > 0.3:
                    d = seq[i]['gambe'][lp]; out['calci'].append((round(i / fps, 2), lp, round(math.degrees(math.atan2(d.x, -d.y))), round(g[i], 2)))
    i = 0
    while i < n:
        if seq[i]['volo']:
            j = i
            while j < n and seq[j]['volo']: j += 1
            zm = max(s['loc'][2] for s in seq[i:j])
            if j - i >= 4: out['salti'].append((round(i / fps, 2), round(j / fps, 2), round(zm, 2)))
            i = j
        else: i += 1
    out['giri'] = round((seq[-1]['yaw'] - seq[0]['yaw']) / (2 * math.pi), 2)
    out['spostamento'] = tuple(round(seq[-1]['loc'][k] - seq[0]['loc'][k], 2) for k in (0, 1))
    return out


if __name__ == '__main__':
    for f in sys.argv[1:]:
        print(os.path.basename(f), eventi(f), flush=True)
