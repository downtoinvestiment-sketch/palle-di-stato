"""Pippo con le emozioni nuove (17 novembre 2026). Decisione finale dell'autore: l'aspetto resta quello di sempre,
cambiano solo le emozioni (gli occhi non cambiano mai misura, le sopracciglia si inclinano di piu'). Le varianti P/Q/R
restano qui solo come prove scartate.
pippo.py NON viene toccato: qui si costruisce il Pippo di sempre e gli si cambiano i pezzi.
Stessa interfaccia di pippo.py, quindi in un episodio basta cambiare l'import:

    import pippo2 as pippo
    P = pippo.build_pippo(chc)                       # con le scelte dell'autore (vedi SCELTE)
    P = pippo.build_pippo(chc, capelli='P2', occhi='Q1', corpo='R1')
    pippo.express(P, frame, smile=1.0, ...)          # stessi parametri di pippo.py, ma gli occhi non cambiano mai misura (regola dell'autore)

Opzioni (lo 0 e' sempre il Pippo di prima):
    capelli  P0 di prima | P1 ciuffo a onda | P2 ciuffo alto | P3 ricci (scartati dall'autore)
             P4 spettinato in avanti | P5 di lato | P6 punte all'insu' (ciocche a punta che seguono la testa)
             P7 ricci (scartati: «orrendi») | P8 ordinati, pettinati all'indietro (scartati: li vuole spettinati)
             P9 spettinati e bassi (scelto dall'autore) | P10 spettinati, piu' alti e selvaggi
    occhi    Q0 di prima | Q1 iride castana | Q2 iride azzurra | Q3 a bottone | Q4 come Gualtiero | Q5 come Gualtiero, piu' grandi
    corpo    R0 di prima | R1 spalle e fianchi | R2 spalle e fianchi piu' larghi (busto in un pezzo solo)"""
import bpy, math
from mathutils import Vector
from common import *
import pippo
from pippo import HEAD_C, HR, HIP_Z

SCELTE = dict(capelli='P0', occhi='Q0', corpo='R0')               # DECISIONE FINALE dell'autore (17 nov 2026): Pippo di sempre, cambiano solo le emozioni (occhi fermi)


def _via(o):
    for c in list(o.children):
        _via(c)
    bpy.data.objects.remove(o)


def _ciocca(nome, punti, raggi, mat, parent, coll):
    """Ciocca liscia che segue i punti (coordinate locali alla testa) con lo spessore dato in ogni punto."""
    cu = bpy.data.curves.new(nome, 'CURVE')
    cu.dimensions = '3D'; cu.bevel_depth = 1.0; cu.bevel_resolution = 5; cu.resolution_u = 10; cu.use_fill_caps = True
    sp = cu.splines.new('BEZIER'); sp.bezier_points.add(len(punti) - 1)
    for bp, co, r in zip(sp.bezier_points, punti, raggi):
        bp.co = co; bp.radius = r; bp.handle_left_type = 'AUTO'; bp.handle_right_type = 'AUTO'
    o = bpy.data.objects.new(nome, cu); o.parent = parent; coll.objects.link(o)
    cu.materials.append(mat)
    return o


def _fibonacci(n):
    """n direzioni ben distribuite sulla sfera."""
    g = math.pi * (3 - math.sqrt(5))
    for i in range(n):
        z = 1 - 2 * (i + 0.5) / n
        r = math.sqrt(max(0.0, 1 - z * z))
        yield Vector((r * math.cos(g * i), r * math.sin(g * i), z))


def _attaccatura(d):
    """quota (sulla sfera unitaria) sotto la quale non ci sono capelli: alta sulla fronte, bassa sulla nuca."""
    return max(-0.25, min(0.74, 0.22 - 0.6 * d.y))


# --------------------------------------------------------------------------- capelli
def _flusso(stile, d):
    """direzione in cui vanno pettinati i capelli nel punto d della testa (sfera unitaria)."""
    def cl(x): return min(1.0, max(0.0, x))
    if stile == 'P4':                                     # tutto in avanti verso la fronte, la nuca verso il basso
        w = cl((d.z - 0.15 - 0.6 * max(0.0, d.y)) / 0.5)
        return Vector((0.15 * d.x, -1, 0.15)) * w + Vector((0.2 * d.x, 0.25, -1)) * (1 - w)
    if stile == 'P5':                                     # riga a sinistra: quasi tutto verso destra
        if d.x < -0.45:
            return Vector((-1, -0.1, -0.6))
        return Vector((1, -0.35, -0.25))
    return Vector((0.0, 0.35, 1.0)) + d * 0.6               # P6: su e un po' indietro


def _ciuffi_ordinati(R, coll, M):
    """I capelli di sempre (ciocche a goccia, stesso colore) ma in ordine: tutti pettinati all'indietro e un po' verso l'alto,
    a strati come tegole, piu' lunghi in cima e corti sui lati, con un ciuffo davanti che sale. Niente punte storte."""
    from mathutils import Matrix
    head = R['head']; H = Vector(HR); C = Vector((0, 0, HEAD_C))

    def ciuffo(nome, pos, dirv, verso, rad, lung, mat):
        z = dirv.normalized(); x = (verso - z * verso.dot(z)).normalized(); y = z.cross(x)
        pv = empty(nome, tuple(pos), head, coll)
        pv.rotation_euler = Matrix((x, y, z)).transposed().to_euler()
        shape(nome + '_M', 'lock', (0, 0, -0.03), (rad, rad, lung), (0, 0, 0), pv, mat, coll)
        R['hair'].append(pv)

    indietro = Vector((0, 1, 0.25))
    for i, d in enumerate(_fibonacci(110)):
        if d.z < _attaccatura(d) + 0.03 or d.y < -0.55:
            continue
        alto = max(0.0, d.z)                                            # 1 in cima, 0 sui lati
        pos = C + Vector((d.x * H.x, d.y * H.y, d.z * H.z)) * 0.95
        dirv = d * (0.55 + 0.35 * alto) + indietro * 0.75 + Vector((d.x * 0.25, 0, 0))
        g = (i * 0.618) % 1
        ciuffo('P2_Ciuffo%d' % i, pos, dirv, indietro, 0.095 + 0.02 * alto + 0.01 * g, 0.10 + 0.08 * alto + 0.02 * g, M['hair2'] if i % 3 == 0 else M['hair1'])
    # davanti: cinque ciuffi che salgono e piegano indietro, il centrale piu' alto
    for j, (x, lung, rad) in enumerate(((-0.21, 0.13, 0.090), (-0.11, 0.17, 0.100), (0.0, 0.21, 0.108), (0.10, 0.19, 0.104), (0.20, 0.14, 0.092))):
        pos = C + Vector((x, -0.225 + 0.06 * abs(x) / 0.2, 0.24 - 0.03 * abs(x) / 0.2))
        dirv = Vector((x * 2.0 + 0.25, 0.15, 1.0))                       # a ventaglio e un po' piegati verso destra
        ciuffo('P2_Ciuffetto%d' % j, pos, dirv, Vector((0.6, 1, 0.1)), rad, lung, M['hair1'] if j % 2 else M['hair2'])


def _spettinati(R, coll, M, selvaggio=False):
    """Spettinati ma fatti bene: ciocche grosse a goccia, a strati, ognuna con la sua direzione ma entro un limite
    (niente punte orizzontali che escono dalla testa), qualcuna che si gira sui lati, frangia a ciuffi in direzioni diverse."""
    import random
    from mathutils import Matrix
    head = R['head']; H = Vector(HR); C = Vector((0, 0, HEAD_C)); rnd = random.Random(7 if not selvaggio else 21)
    caos = 0.55 if selvaggio else 0.38

    def ciuffo(nome, pos, dirv, verso, rad, lung, mat):
        z = dirv.normalized(); x = (verso - z * verso.dot(z)); x = (x if x.length > 1e-4 else Vector((1, 0, 0))).normalized(); y = z.cross(x)
        pv = empty(nome, tuple(pos), head, coll)
        pv.rotation_euler = Matrix((x, y, z)).transposed().to_euler()
        shape(nome + '_M', 'lock', (0, 0, -0.035), (rad, rad, lung), (0, 0, 0), pv, mat, coll)
        R['hair'].append(pv)

    for i, d in enumerate(_fibonacci(96)):
        if d.z < _attaccatura(d) + 0.03 or d.y < -0.6:
            continue
        alto = max(0.0, d.z)
        pos = C + Vector((d.x * H.x, d.y * H.y, d.z * H.z)) * 0.95
        a_caso = Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-0.3, 0.6)))
        dirv = d * 1.0 + (Vector((0, 0.35, 0.55)) if selvaggio else Vector((0, 0.55, 0.15))) * alto + a_caso * caos   # P9: piu' basso, piega indietro
        if dirv.normalized().z < -0.15:                                     # niente ciocche che puntano in giu' dalla testa
            dirv.z += 0.4
        verso = Vector((rnd.uniform(-1, 1), rnd.uniform(-0.5, 1), 0.2))      # da che parte piega la punta
        ciuffo('P2_Ciuffo%d' % i, pos, dirv, verso, rnd.uniform(0.09, 0.115) + 0.015 * alto, (rnd.uniform(0.11, 0.15) + 0.07 * alto) if selvaggio else (rnd.uniform(0.09, 0.12) + 0.02 * alto), M['hair2'] if i % 3 == 0 else M['hair1'])
    # frangia: ciuffi grossi che vanno ognuno per conto suo, uno ricade sulla fronte
    frangia = [(-0.22, (-0.9, -0.3, 0.7), (-1, 0.2, 0), 0.13), (-0.11, (-0.2, -0.6, 0.9), (-1, 0, 0), 0.17), (0.0, (0.15, -0.9, -0.35), (1, 0, 0), 0.15),
               (0.10, (0.35, -0.3, 1.0), (1, 0.3, 0), 0.20), (0.21, (1.0, -0.2, 0.55), (1, 0.2, 0), 0.14)]
    for j, (x, dv, vs, lung) in enumerate(frangia):
        pos = C + Vector((x, -0.225 + 0.06 * abs(x) / 0.22, 0.245 - 0.03 * abs(x) / 0.22))
        ciuffo('P2_Frangia%d' % j, pos, Vector(dv), Vector(vs), 0.10, lung * (1.15 if selvaggio else 0.8), M['hair1'] if j % 2 else M['hair2'])
    # due ciocche che si girano verso l'esterno sopra le orecchie
    for s_ in (-1, 1):
        pos = C + Vector((s_ * 0.33, 0.02, 0.12))
        ciuffo('P2_Giro', pos, Vector((s_ * 1.0, 0.3, 0.5)), Vector((0, 0, 1)), 0.08, 0.12, M['hair2'])


def _nuca(R, coll):
    """Capelli dietro la testa per il Pippo di sempre: due giri di ciocche che scendono sulla nuca e sopra le orecchie,
    cosi' si copre il bordo seghettato della calotta e non si vede la pelle dietro (l'autore, 17 nov 2026)."""
    from mathutils import Matrix
    head, M = R['head'], R['mats']; H = Vector(HR); C = Vector((0, 0, HEAD_C))
    for giro, (zq, n, da, a, rad, lung) in enumerate(((0.24, 13, -92, 92, 0.085, 0.11), (0.0, 9, -65, 65, 0.08, 0.10))):
        for i in range(n):
            ang = math.radians(da + (a - da) * i / (n - 1))
            dxy = Vector((math.sin(ang), math.cos(ang), 0)) * math.sqrt(1 - zq * zq)
            d = Vector((dxy.x, dxy.y, zq))
            pos = C + Vector((d.x * H.x, d.y * H.y, d.z * H.z)) * 1.0
            z = Vector((d.x * 0.8, d.y * 0.8, -1.0)).normalized()                       # giu' e in fuori, aderenti alla testa
            x = Vector((math.cos(ang), -math.sin(ang), 0)); x = (x - z * x.dot(z)).normalized(); y = z.cross(x)
            pv = empty('P2_Nuca%d_%d' % (giro, i), tuple(pos), head, coll)
            pv.rotation_euler = Matrix((x, y, z)).transposed().to_euler()
            g = 0.9 + 0.2 * ((i * 0.618) % 1)
            shape('P2_NucaM', 'lock', (0, 0, -0.04), (rad * g, rad * g, lung * g), (0, (i % 2 - 0.5) * 0.5, 0), pv, M['hair2'] if (i + giro) % 2 else M['hair1'], coll)
            R['hair'].append(pv)


def _ricci(R, coll, M):
    """Capelli ricci e pieni: una massa di riccioli tondi in due strati, piu' alta in cima, e boccoli a molla sulla fronte e ai lati."""
    head = R['head']; H = Vector(HR); C = Vector((0, 0, HEAD_C))
    S = lambda name, loc, r, mat: shape(name, 'sphere', tuple(loc), (r, r, r * 0.92), (0, 0, 0), head, mat, coll)
    for strato, (n, rr, alto, dim) in enumerate(((150, 1.02, 0.10, 0.092), (90, 1.13, 0.16, 0.085))):
        for i, d in enumerate(_fibonacci(n)):
            if d.z < _attaccatura(d) + (0.0 if strato == 0 else 0.12) + 0.24 * max(0.0, -d.y - 0.35):   # fronte libera: le sopracciglia si devono vedere
                continue
            k = rr + alto * max(0.0, d.z) ** 2 + 0.03 * math.sin(i * 2.3)
            r = dim * (1 + 0.22 * math.sin(i * 1.7 + strato))
            R['hair'].append(S('P2_Riccio%d_%d' % (strato, i), C + Vector((d.x * H.x, d.y * H.y, d.z * H.z)) * k, r, M['hair2'] if (i + strato) % 3 == 0 else M['hair1']))
    # boccoli a molla: sulla fronte e davanti alle orecchie
    boccoli = [(-0.20, -0.20, 0.33, 0.07), (-0.06, -0.24, 0.355, 0.075), (0.08, -0.24, 0.355, 0.07), (0.21, -0.19, 0.33, 0.07),
               (-0.335, -0.10, 0.10, 0.15), (0.335, -0.10, 0.10, 0.15)]
    for j, (x, y, z, L) in enumerate(boccoli):
        pts, raggi = [], []
        for t in range(13):
            u = t / 12; a = u * 2.6 * math.tau
            pts.append(Vector((x + 0.034 * math.cos(a), y - 0.034 * math.sin(a) - 0.01, HEAD_C + z - L * u)))
            raggi.append(0.030 * (1 - 0.55 * u) + 0.006)
        R['hair'].append(_ciocca('P2_Boccolo%d' % j, pts, raggi, M['hair1'] if j % 2 else M['hair2'], head, coll))


def _punte(R, coll, stile, M):
    """ciocche a punta: partono dentro la testa, scorrono sulla superficie nel verso del flusso e si staccano in punta."""
    head = R['head']; H = Vector(HR); C = Vector((0, 0, HEAD_C))
    n, passo, stacco, spess = {'P4': (46, 0.24, 0.20, 0.125), 'P5': (46, 0.25, 0.18, 0.12), 'P6': (36, 0.09, 0.95, 0.135)}[stile]
    for i, d in enumerate(_fibonacci(n * 2)):
        if d.z < _attaccatura(d) + 0.02:
            continue
        pts, cur = [], Vector(d)
        for k in range(5):
            r = 0.97 + stacco * (k / 4) ** 1.6
            pts.append(C + Vector((cur.x * H.x, cur.y * H.y, cur.z * H.z)) * r)
            f = _flusso(stile, cur); t = f - cur * f.dot(cur)
            if t.length < 1e-4:
                break
            cur = (cur + t.normalized() * passo).normalized()
            if stile == 'P4' and cur.y < -0.45 and cur.z < 0.52:     # la frangia si ferma sopra gli occhi
                cur = Vector((cur.x, cur.y, 0.52)).normalized()
        if len(pts) < 3:
            continue
        g = 0.85 + 0.3 * ((i * 0.618) % 1)
        rad = [spess * g * x for x in (1.0, 0.95, 0.72, 0.42, 0.06)][:len(pts)]
        R['hair'].append(_ciocca('P2_Punta%d' % i, pts, rad, M['hair2'] if i % 3 == 0 else M['hair1'], head, coll))


def _capelli(R, coll, stile):
    head, M = R['head'], R['mats']
    for pv in R['hair']:
        _via(pv)
    R['hair'] = []
    H = Vector(HR); C = Vector((0, 0, HEAD_C))
    S = lambda name, kind, loc, sc, parent, mat, rot=(0, 0, 0): shape(name, kind, loc, sc, rot, parent, mat, coll)
    c2 = lambda i: M['hair2'] if i % 2 else M['hair1']
    if stile in ('P4', 'P5', 'P6'):
        _punte(R, coll, stile, M); return
    if stile == 'P7':
        _ricci(R, coll, M); return
    if stile == 'P8':
        _ciuffi_ordinati(R, coll, M); return
    if stile in ('P9', 'P10'):
        _spettinati(R, coll, M, stile == 'P10'); return
    if stile == 'P1':
        # ciuffo a onda: la frangia sale e piega tutta da una parte, il resto scende ordinato verso la nuca
        for i, x in enumerate((-0.23, -0.12, 0.0, 0.12, 0.22)):
            b = Vector((x, -0.205 + 0.02 * abs(x) / 0.23, HEAD_C + 0.245))
            pts = [b + Vector((0, 0.07, -0.03)), b + Vector((0.01, -0.07, 0.07)), b + Vector((0.07, -0.10, 0.165)), b + Vector((0.165, -0.05, 0.215)), b + Vector((0.235, 0.02, 0.185))]
            R['hair'].append(_ciocca('P2_Ciuffo%d' % i, pts, (0.07, 0.092, 0.098, 0.075, 0.022), c2(i), head, coll))
        for i, x in enumerate((-0.26, -0.09, 0.09, 0.26)):          # sopra, verso dietro
            pts = [Vector((x * 0.8, -0.10, HEAD_C + 0.30)), Vector((x, 0.05, HEAD_C + 0.355)), Vector((x * 1.05, 0.20, HEAD_C + 0.30)), Vector((x * 1.02, 0.31, HEAD_C + 0.17))]
            R['hair'].append(_ciocca('P2_Sopra%d' % i, pts, (0.085, 0.105, 0.10, 0.035), c2(i + 1), head, coll))
        for i, x in enumerate((-0.27, -0.10, 0.10, 0.27)):          # nuca
            pts = [Vector((x, 0.20, HEAD_C + 0.20)), Vector((x * 1.03, 0.315, HEAD_C + 0.05)), Vector((x * 0.95, 0.31, HEAD_C - 0.13))]
            R['hair'].append(_ciocca('P2_Nuca%d' % i, pts, (0.095, 0.10, 0.03), c2(i), head, coll))
        for s in (-1, 1):                                             # lati e basette
            pts = [Vector((s * 0.27, -0.06, HEAD_C + 0.24)), Vector((s * 0.365, 0.04, HEAD_C + 0.12)), Vector((s * 0.355, 0.13, HEAD_C - 0.05))]
            R['hair'].append(_ciocca('P2_Lato', pts, (0.08, 0.085, 0.03), M['hair1'], head, coll))
            pts = [Vector((s * 0.30, -0.10, HEAD_C + 0.17)), Vector((s * 0.352, -0.075, HEAD_C + 0.06)), Vector((s * 0.345, -0.06, HEAD_C - 0.04))]
            R['hair'].append(_ciocca('P2_Basetta', pts, (0.06, 0.05, 0.018), M['hair2'], head, coll))
    elif stile == 'P2':
        # ciuffo alto: la frangia sale in un'onda morbida e torna indietro, lati corti e puliti
        for i, x in enumerate((-0.20, -0.10, 0.0, 0.10, 0.20)):
            h = 1.0 - 0.35 * abs(x) / 0.2
            pts = [Vector((x, -0.20, HEAD_C + 0.21)), Vector((x * 1.05, -0.255, HEAD_C + 0.21 + 0.17 * h)), Vector((x * 1.1, -0.17, HEAD_C + 0.30 + 0.22 * h)),
                   Vector((x * 1.1, -0.02, HEAD_C + 0.33 + 0.16 * h)), Vector((x * 1.05, 0.14, HEAD_C + 0.33 + 0.04 * h))]
            R['hair'].append(_ciocca('P2_Ciuffo%d' % i, pts, (0.06, 0.085, 0.095, 0.085, 0.05), c2(i), head, coll))
        for i, x in enumerate((-0.27, -0.13, 0.0, 0.13, 0.27)):          # dietro, pettinati verso la nuca
            pts = [Vector((x * 0.8, 0.0, HEAD_C + 0.34)), Vector((x, 0.18, HEAD_C + 0.30)), Vector((x * 1.02, 0.30, HEAD_C + 0.15)), Vector((x * 0.95, 0.31, HEAD_C - 0.10))]
            R['hair'].append(_ciocca('P2_Dietro%d' % i, pts, (0.085, 0.10, 0.09, 0.03), c2(i + 1), head, coll))
        for s in (-1, 1):                                                 # lati corti
            for k, y in enumerate((-0.08, 0.06)):
                pts = [Vector((s * 0.25, y, HEAD_C + 0.28)), Vector((s * 0.355, y + 0.04, HEAD_C + 0.13)), Vector((s * 0.355, y + 0.07, HEAD_C - 0.02))]
                R['hair'].append(_ciocca('P2_Lato', pts, (0.07, 0.07, 0.02), c2(k), head, coll))
    elif stile == 'P3':
        # ricci: tante palline su tutta la testa, due toni
        i = 0
        for d in _fibonacci(120):
            if d.z < _attaccatura(d) - 0.02:
                continue
            k = 1.03 + 0.05 * math.sin(i * 2.4)
            pos = Vector((d.x * H.x, d.y * H.y, d.z * H.z)) * k
            r = 0.082 + 0.018 * math.sin(i * 1.7)
            R['hair'].append(S('P2_Riccio%d' % i, 'sphere', tuple(C + pos), (r, r, r), head, c2(i)))
            i += 1
        for j, x in enumerate((-0.20, -0.07, 0.06, 0.19)):            # riccioli sulla fronte
            R['hair'].append(S('P2_RiccioFronte%d' % j, 'sphere', (x, -0.275 + 0.03 * abs(x) / 0.2, HEAD_C + 0.235 - 0.02 * (j % 2)), (0.075, 0.07, 0.075), head, c2(j)))


# --------------------------------------------------------------------------- occhi
def _occhi(R, coll, stile):
    M = R['mats']
    S = lambda name, kind, loc, sc, parent, mat: shape(name, kind, loc, sc, (0, 0, 0), parent, mat, coll)
    if stile in ('Q1', 'Q2'):
        iride = material('P2_IrideCastana', (0.42, 0.20, 0.05), rough=0.25, spec=0.8) if stile == 'Q1' else material('P2_IrideAzzurra', (0.05, 0.38, 0.85), rough=0.25, spec=0.8)
        bordo = material('P2_IrideBordo', (0.10, 0.05, 0.02), rough=0.3) if stile == 'Q1' else material('P2_IrideBordoBlu', (0.01, 0.10, 0.30), rough=0.3)
    for nm in ('L', 'R'):
        eye, pup = R['eye' + nm], R['pupil' + nm]
        for c in list(pup.children):
            _via(c)
        if stile in ('Q1', 'Q2'):
            S('P2_IrideBordo' + nm, 'sphere', (0, 0.010, 0), (0.084, 0.030, 0.098), pup, bordo)
            S('P2_Iride' + nm, 'sphere', (0, 0.002, 0), (0.074, 0.030, 0.087), pup, iride)
            S('P2_Pupilla' + nm, 'sphere', (0, -0.010, 0), (0.040, 0.022, 0.048), pup, M['pupil'])
            S('P2_Luce' + nm, 'sphere_lo', (-0.026, -0.030, 0.034), (0.024, 0.012, 0.027), pup, M['shine'])
            S('P2_Lucina' + nm, 'sphere_lo', (0.026, -0.028, -0.030), (0.011, 0.007, 0.012), pup, M['shine'])
        elif stile in ('Q4', 'Q5'):
            # come Gualtiero: occhio bianco piccolo a uovo e pupilla nera piccola, senza riflessi
            k = 1.0 if stile == 'Q4' else 1.22
            for c in list(eye.children):
                if c != pup:
                    _via(c)
            S('P2_Bianco' + nm, 'sphere', (0, 0.005, -0.005), (0.096 * k, 0.058, 0.108 * k), eye, M['white'])
            S('P2_Pupilla' + nm, 'sphere', (0, 0.012, -0.006), (0.042 * k, 0.024, 0.050 * k), pup, M['pupil'])
        elif stile == 'Q3':
            for c in list(eye.children):
                if c != pup:
                    _via(c)                                         # via il bianco
            S('P2_Bottone' + nm, 'sphere', (0, 0.030, 0), (0.070, 0.034, 0.108), pup, M['pupil'])
            S('P2_Luce' + nm, 'sphere_lo', (-0.022, 0.002, 0.045), (0.024, 0.012, 0.030), pup, M['shine'])
            S('P2_Lucina' + nm, 'sphere_lo', (0.022, 0.004, -0.045), (0.011, 0.007, 0.013), pup, M['shine'])


# --------------------------------------------------------------------------- corpo
def _corpo(R, coll, stile):
    """Il busto diventa un pezzo solo che si allarga dolcemente alle spalle e ai fianchi (niente pezzi attaccati)."""
    M = R['mats']
    f = {'R1': (0.30, 0.10), 'R2': (0.42, 0.16)}[stile]                 # quanto si allargano spalle e fianchi
    t = next(o for o in R['body'].children if o.name.startswith('P_Torso'))
    t.data = t.data.copy()
    def sm(a, b, x):
        u = min(1.0, max(0.0, (x - a) / (b - a))); return u * u * (3 - 2 * u)
    zc = pippo.TORSO_C
    for v in t.data.vertices:
        z = v.co.z + zc                                                  # quota nel corpo (0 = bacino, 0.79 = collo)
        spalle = sm(0.30, 0.58, z) * (1 - 0.55 * sm(0.66, 0.80, z))     # cresce fino alle spalle, poi si arrotonda verso il collo
        fianchi = 1 - sm(0.05, 0.30, z)
        v.co.x *= 1 + f[0] * spalle + f[1] * fianchi
        v.co.y *= 1 - 0.08 * spalle
    sx = pippo.TORSO_R * (1 + f[0]) + 0.045                            # il braccio appoggiato al busto, un po' dentro
    for s_, nm in ((-1, 'L'), (1, 'R')):
        R['shoulder' + nm].location.x = s_ * sx
        R['hip' + nm].location.x = s_ * (0.115 + 0.24 * f[1] * 0.5)


def express(R, f, brow=0.0, brow_lift=0.0, eye_open=1.0, smile=0.0, mouth_open=0.0, look=(0.0, 0.0), eye_scale=1.0):
    """Come pippo.express, ma gli occhi restano sempre della stessa misura: niente occhi che si rimpiccioliscono o si ingrandiscono
    (regola dell'autore, 17 nov 2026). eye_open ed eye_scale vengono accettati per compatibilita' ma ignorati.
    L'emozione la fanno le sopracciglia (inclinate di piu' che in pippo.py), la bocca e lo sguardo."""
    pippo.express(R, f, brow=brow * 1.7, brow_lift=brow_lift, eye_open=1.0, smile=smile, mouth_open=mouth_open, look=look, eye_scale=1.0)


def build_pippo(coll=None, capelli=None, occhi=None, corpo=None):
    """Costruisce Pippo con i pezzi scelti. Senza argomenti usa SCELTE (le scelte dell'autore)."""
    capelli = capelli or SCELTE['capelli']; occhi = occhi or SCELTE['occhi']; corpo = corpo or SCELTE['corpo']
    coll = coll or collection('Pippo')
    R = pippo.build_pippo(coll)
    if capelli != 'P0':
        _capelli(R, coll, capelli)
    else:
        _nuca(R, coll)
    if capelli in ('P7', 'P9', 'P10'):
        # sopracciglia un po' piu' giu', avanti e piu' spesse, cosi' i ricci non le coprono (express() continua a muoverle)
        for nm in ('L', 'R'):
            for c in R['brow' + nm].children:
                c.location = (0, -0.035, -0.035); c.scale = (0.135, 0.048, 0.052)
    if occhi != 'Q0':
        _occhi(R, coll, occhi)
    if corpo != 'R0':
        _corpo(R, coll, corpo)
    R['versione'] = (capelli, occhi, corpo)
    return R


# --------------------------------------------------------------------------- emozioni esagerate
# Richiesta dell'autore (17 nov 2026): emozioni esagerate, ma gli occhi restano sempre della stessa misura.
# L'esagerazione la fanno sopracciglia e bocca spinte al massimo, la posa (testa, busto, braccia) e i segni da cartone
# animato: lacrime, goccia di sudore, guance rosse, vena della rabbia, fumo dalle orecchie.
EMOZIONI_FORTI = {
    'normale':    dict(faccia=dict(smile=0.4), braccia=((-0.08, 0, -1), (0.08, 0, -1))),
    'felice':     dict(faccia=dict(smile=2.0, brow_lift=0.9), braccia=((-0.75, -0.15, 0.75), (0.75, -0.15, 0.75)), testa=(-0.15, 0, 0.12), extra=('guance',)),
    'ride':       dict(faccia=dict(smile=1.6, mouth_open=1.5, brow_lift=1.0, brow=-0.3), braccia=((0.45, -0.75, -0.45), (-0.45, -0.75, -0.45)),
                       testa=(-0.38, 0, 0.18), busto=(-0.14, 0), extra=('guance', 'lacrime_gioia')),
    'arrabbiato': dict(faccia=dict(brow=1.6, smile=-1.6, mouth_open=0.8), braccia=((-0.22, 0.30, -1), (0.22, 0.30, -1)), testa=(0.22, 0, 0), busto=(0.16, 0),
                       extra=('rabbia', 'vena', 'fumo')),
    'triste':     dict(faccia=dict(brow=-1.6, brow_lift=0.3, smile=-2.0, look=(0, -0.9)), braccia=((0.05, -0.35, -1), (-0.05, -0.35, -1)), testa=(0.55, 0, 0), busto=(0.20, 0),
                       extra=('lacrime',)),
    'spaventato': dict(faccia=dict(brow=-1.6, brow_lift=1.3, smile=-0.8, mouth_open=1.6), braccia=((-0.25, -0.95, 0.55), (0.25, -0.95, 0.55)), testa=(-0.12, 0, 0),
                       busto=(-0.22, 0), extra=('goccia',)),
    'sorpreso':   dict(faccia=dict(brow_lift=1.5, mouth_open=1.6, smile=0.0), braccia=((0.15, -0.30, 0.95), (-0.15, -0.30, 0.95)), testa=(-0.12, 0, 0), busto=(-0.08, 0)),
    'furbo':      dict(faccia=dict(smile=1.4, look=(1, 0)), braccia=((-0.08, 0, -1), (-0.45, -0.8, 0.40)), testa=(0.05, 0, -0.30), busto=(0, 0.06),
                       sopracciglia=(1.4, -0.9)),
}


def _segni(P):
    """Costruisce (spenti) i segni da cartone animato attaccati alla testa."""
    if 'segni' in P:
        return P['segni']
    head = P['head']; coll = head.users_collection[0]; C = HEAD_C
    acqua = material('P2_Lacrima', (0.45, 0.80, 1.0), rough=0.05, spec=1.0, emit=(0.3, 0.6, 1.0), emit_strength=0.4)
    rosso = material('P2_Rossore', (1.0, 0.25, 0.30), rough=0.6)
    vena = material('P2_Vena', (0.85, 0.02, 0.05), rough=0.4)
    fumo = material('P2_Fumo', (1, 1, 1), rough=1.0, emit=(1, 1, 1), emit_strength=0.6)
    S = lambda n, k, loc, sc, par, mat, rot=(0, 0, 0): shape(n, k, loc, sc, rot, par, mat, coll)
    seg = {}
    def gruppo(nome):
        g = empty('P2_Segno_' + nome, (0, 0, 0), head, coll); seg[nome] = g; return g
    g = gruppo('lacrime')                                   # due fiumi di lacrime che scendono fino al mento
    for s_ in (-1, 1):
        S('P2_LacrimaFiume', 'cap:0.032:0.20', (s_ * 0.15, -0.300, C - 0.13), (1, 1, 1), g, acqua, rot=(0.25, 0, 0))
        S('P2_LacrimaGoccia', 'sphere', (s_ * 0.155, -0.27, C - 0.30), (0.045, 0.045, 0.06), g, acqua)
    g = gruppo('lacrime_gioia')                             # lacrime che schizzano di lato quando ride
    for s_ in (-1, 1):
        for k in range(3):
            S('P2_LacrimaSchizzo', 'sphere', (s_ * (0.30 + 0.07 * k), -0.20 + 0.02 * k, C + 0.06 - 0.03 * k), (0.03, 0.022, 0.04), g, acqua)
    g = gruppo('goccia')                                    # goccia di sudore sulla tempia
    S('P2_Sudore', 'sphere', (0.30, -0.17, C + 0.17), (0.045, 0.035, 0.07), g, acqua)
    S('P2_SudorePunta', 'cone', (0.30, -0.17, C + 0.215), (0.028, 0.022, 0.06), g, acqua)
    for nome in ('guance', 'rabbia'):                       # guance rosa (felice) o rosse (arrabbiato)
        g = gruppo(nome)
        for s_ in (-1, 1):
            S('P2_Guancia', 'sphere', (s_ * 0.205, -0.262, C - 0.075), (0.085 if nome == 'rabbia' else 0.06, 0.03, 0.05 if nome == 'rabbia' else 0.035), g, rosso)
    g = gruppo('vena')                                      # il simbolo della vena sulla fronte
    for k, (dx, dz, r) in enumerate(((-0.03, 0.03, 0.6), (0.03, 0.03, -0.6), (-0.03, -0.03, -0.6), (0.03, -0.03, 0.6))):
        S('P2_Vena', 'cap:0.012:0.04', (0.20 + dx, -0.25, C + 0.27 + dz), (1, 1, 1), g, vena, rot=(0, r, 0))
    g = gruppo('fumo')                                      # fumo dalle orecchie
    for s_ in (-1, 1):
        for k in range(3):
            S('P2_Fumo', 'sphere', (s_ * (0.42 + 0.06 * k), 0.0, C + 0.02 + 0.09 * k), (0.06 + 0.02 * k,) * 3, g, fumo)
    for g in seg.values():
        g.scale = (0.001,) * 3
    P['segni'] = seg
    return seg


def emozione(P, f, nome, forza=1.0):
    """Emozione esagerata al fotogramma f: faccia, posa e segni da cartone. forza 0..1 per dosarla.
    Gli occhi non cambiano mai misura. Le braccia vanno in rotazione QUATERNION (come negli episodi)."""
    e = EMOZIONI_FORTI[nome]
    fa = {k: (tuple(x * forza for x in v) if isinstance(v, tuple) else v * forza) for k, v in e['faccia'].items()}
    express(P, f, **fa)
    if 'sopracciglia' in e:                                  # un sopracciglio su e uno giu' (furbo)
        for (s_, nm), b in zip(((-1, 'L'), (1, 'R')), e['sopracciglia']):
            br = P['brow' + nm]; br.rotation_euler = (0, s_ * b * 0.45 * forza, 0); br.location.z = HEAD_C + 0.215 + 0.07 * max(0.0, -b) * forza
            br.keyframe_insert('rotation_euler', frame=f); br.keyframe_insert('location', index=2, frame=f)
    for nm, d in zip(('L', 'R'), e['braccia']):
        sh = P['shoulder' + nm]; sh.rotation_mode = 'QUATERNION'
        dv = Vector((0, 0, -1)).lerp(Vector(d).normalized(), forza)
        sh.rotation_quaternion = Vector((0, 0, -1)).rotation_difference(dv); sh.keyframe_insert('rotation_quaternion', frame=f)
    tx, ty, tz = e.get('testa', (0, 0, 0)); P['head'].rotation_euler = (tx * forza, ty * forza, tz * forza); P['head'].keyframe_insert('rotation_euler', frame=f)
    bx_, by_ = e.get('busto', (0, 0)); P['body'].rotation_euler = (bx_ * forza, by_ * forza, 0); P['body'].keyframe_insert('rotation_euler', frame=f)
    seg = _segni(P)
    for k, g in seg.items():
        g.scale = (1, 1, 1) if (k in e.get('extra', ()) and forza > 0.3) else (0.001,) * 3
        g.keyframe_insert('scale', frame=f)

