"""Ritaglia da world-atlas (dati Natural Earth, pubblico dominio) l'Italia e i paesi vicini, in km attorno a 12,5 E e 42 N.
Uso:  python -I mappa_italia.py /percorso/countries-50m.json ../assets/mappe/italia50m.json
Esce un JSON {id: {nome, poligoni: [[anello esterno, buchi...], ...]}} con le coordinate (x verso est, y verso nord) in km."""
import sys, json, math

src, dst = sys.argv[1], sys.argv[2]
T = json.load(open(src))
sx, sy = T['transform']['scale']; tx, ty = T['transform']['translate']
arcs = []
for a in T['arcs']:                                   # gli archi sono quantizzati e scritti come differenze
    x = y = 0; pts = []
    for dx, dy in a:
        x += dx; y += dy; pts.append((x * sx + tx, y * sy + ty))
    arcs.append(pts)


def arco(i):
    return arcs[i] if i >= 0 else arcs[~i][::-1]


def anello(idx):
    pts = []
    for i in idx:
        p = arco(i)
        pts.extend(p if not pts else p[1:])
    return pts


LON0, LAT0 = 12.5, 42.0
KX = 111.32 * math.cos(math.radians(LAT0)); KY = 110.57
BB = (2.0, 34.0, 23.0, 49.0)                          # lon min, lat min, lon max, lat max
out = {}
for g in T['objects']['countries']['geometries']:
    if g['type'] == 'Polygon': polys = [g['arcs']]
    elif g['type'] == 'MultiPolygon': polys = g['arcs']
    else: continue
    tieni = []
    for P in polys:
        rings = [anello(r) for r in P]
        xs = [p[0] for p in rings[0]]; ys = [p[1] for p in rings[0]]
        if max(xs) < BB[0] or min(xs) > BB[2] or max(ys) < BB[1] or min(ys) > BB[3]: continue
        tieni.append([[(round((lon - LON0) * KX, 2), round((lat - LAT0) * KY, 2)) for lon, lat in r] for r in rings])
    if tieni: out[g.get('id') or g['properties'].get('name')] = {'nome': g['properties'].get('name'), 'poligoni': tieni}
json.dump(out, open(dst, 'w'), separators=(',', ':'))
print(len(out), sorted(v['nome'] for v in out.values()))
