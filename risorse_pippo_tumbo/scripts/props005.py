"""Test 005 - oggetti: tovaglia, paracadute a lenzuolo, cupola con foro, ala a celle, imbracatura, occhialoni, aereo."""
import bpy, math, numpy as np
from common import *
import set004
from set004 import MB


def mats005():
    M = {}
    M['nyl'] = [material('Q_nyl%d' % i, c, rough=0.55, spec=0.3) for i, c in enumerate(
        [(1.0, 0.30, 0.05), (1.0, 0.95, 0.90), (1.0, 0.80, 0.05), (0.05, 0.45, 1.0), (0.95, 0.10, 0.25), (0.10, 0.75, 0.35)])]
    M['sheet'] = material('Q_sheet', (0.96, 0.96, 0.92), rough=0.9, spec=0.1)
    M['sheet2'] = material('Q_sheet2', (0.60, 0.78, 1.0), rough=0.9, spec=0.1)
    M['line'] = material('Q_line', (0.98, 0.98, 0.95), rough=0.8)
    M['rope'] = material('Q_rope', (0.72, 0.52, 0.28), rough=0.9)
    M['web'] = material('Q_web', (0.08, 0.09, 0.12), rough=0.7)
    M['pack'] = material('Q_pack', (0.10, 0.35, 0.95), rough=0.6)
    M['packr'] = material('Q_packr', (0.95, 0.10, 0.15), rough=0.6)
    M['buckle'] = material('Q_buckle', (0.85, 0.87, 0.9), rough=0.25, metallic=0.9)
    M['toggle'] = material('Q_toggle', (1.0, 0.85, 0.05), rough=0.5)
    M['inside'] = material('Q_inside', (0.45, 0.12, 0.03), rough=0.9)
    M['gogf'] = material('Q_gogf', (0.45, 0.25, 0.10), rough=0.6)
    M['lens'] = material('Q_lens', (0.55, 0.85, 1.0), rough=0.05, spec=1.0)
    try:
        M['lens'].surface_render_method = 'BLENDED'; M['lens'].node_tree.nodes['Principled BSDF'].inputs['Alpha'].default_value = 0.35
    except Exception: pass
    M['pl_w'] = material('Q_plw', (0.98, 0.98, 0.96), rough=0.35, spec=0.6)
    M['pl_r'] = material('Q_plr', (0.95, 0.12, 0.10), rough=0.35, spec=0.6)
    M['pl_y'] = material('Q_ply', (1.0, 0.80, 0.05), rough=0.35, spec=0.6)
    M['pl_d'] = material('Q_pld', (0.06, 0.07, 0.10), rough=0.5)
    M['pl_g'] = material('Q_plg', (0.35, 0.70, 1.0), rough=0.08, spec=1.0)
    M['propdisc'] = material('Q_propdisc', (0.8, 0.8, 0.85), rough=0.5)
    try:
        M['propdisc'].surface_render_method = 'BLENDED'; M['propdisc'].node_tree.nodes['Principled BSDF'].inputs['Alpha'].default_value = 0.22
    except Exception: pass
    # tovaglia a quadretti (UV)
    m = material('Q_cloth', (1, 1, 1), rough=0.9, spec=0.1); nt = m.node_tree; b = nt.nodes['Principled BSDF']
    uv = nt.nodes.new('ShaderNodeTexCoord'); ch = nt.nodes.new('ShaderNodeTexChecker')
    ch.inputs['Scale'].default_value = 10.0; ch.inputs['Color1'].default_value = (0.92, 0.06, 0.08, 1); ch.inputs['Color2'].default_value = (1, 1, 1, 1)
    nt.links.new(uv.outputs['UV'], ch.inputs['Vector']); nt.links.new(ch.outputs['Color'], b.inputs['Base Color'])
    M['cloth'] = m
    return M


def _tube(V, F, MI, p0, p1, r, mi):
    """prisma triangolare sottile tra due punti (topologia fissa: 6 vertici, 3 facce)."""
    p0 = np.array(p0, float); p1 = np.array(p1, float); d = p1 - p0; n = np.linalg.norm(d)
    d = d / n if n > 1e-9 else np.array([0, 0, 1.0])
    a = np.cross(d, [0, 1, 0]);
    if np.linalg.norm(a) < 1e-3: a = np.cross(d, [1, 0, 0])
    a /= np.linalg.norm(a); b = np.cross(d, a)
    i0 = len(V)
    for p in (p0, p1):
        for k in range(3):
            an = k * 2.0944; V.append(tuple(p + r * (math.cos(an) * a + math.sin(an) * b)))
    for k in range(3):
        k2 = (k + 1) % 3; F.append((i0 + k, i0 + k2, i0 + 3 + k2, i0 + 3 + k)); MI.append(mi)


def _obj(name, V, F, MI, mats, coll, parent=None, loc=(0, 0, 0), smooth_upto=None, uvs=None):
    me = bpy.data.meshes.new(name); me.from_pydata(V, [], F)
    for m in mats: me.materials.append(m)
    me.polygons.foreach_set('material_index', MI)
    if smooth_upto:
        sm = [i < smooth_upto for i in range(len(F))]; me.polygons.foreach_set('use_smooth', sm)
    if uvs is not None:
        l = me.uv_layers.new(name='UVMap')
        for li, loop in enumerate(me.loops): l.data[li].uv = uvs[loop.vertex_index]
    me.update()
    o = bpy.data.objects.new(name, me); o.location = loc; o.parent = parent; coll.objects.link(o)
    return o


def _add_key(o, name, V):
    if not o.data.shape_keys: o.shape_key_add(name='Basis')
    k = o.shape_key_add(name=name); k.data.foreach_set('co', np.array(V, float).ravel()); k.value = 0.0
    return k


# ---------------------------------------------------------------------------------------------- tovaglia
def tablecloth(coll, M, parent=None, loc=(0, 0, 0), a=0.95, hand=0.42):
    """tovaglia a quadretti tenuta per i 4 angoli (due per mano). Origine = altezza mani. Chiavi: 'inv' (rovesciata), 'flat'."""
    N = 20
    def gen(mode):
        V = []
        for i in range(N + 1):
            for j in range(N + 1):
                u = -1 + 2 * i / N; v = -1 + 2 * j / N; q = 1 - 0.5 * (u * u + v * v)
                if mode == 'open':
                    x = a * u; y = 0.8 * a * v; z = 0.62 * max(q, 0) ** 0.75 + 0.02 * math.sin(6 * u + 4 * v)
                elif mode == 'inv':
                    x = 0.30 * a * u * (1 + 0.3 * math.sin(5 * v)); y = 0.24 * a * v + 0.05 * math.sin(6 * u)
                    z = 0.18 + 1.55 * max(q, 0) + 0.07 * math.sin(7 * u + 3 * v)
                else:   # flat: stesa (sul tavolo)
                    x = a * u; y = a * v; z = 0.0
                if mode != 'flat':
                    w = (abs(u) * abs(v)) ** 3; tx = math.copysign(hand, u) if u != 0 else 0
                    x = x * (1 - w) + tx * w; y = y * (1 - w) + (0.05 * v) * w; z = z * (1 - w)
                V.append((x, y, z))
        return V
    F = []; idx = lambda i, j: i * (N + 1) + j
    for i in range(N):
        for j in range(N): F.append((idx(i, j), idx(i + 1, j), idx(i + 1, j + 1), idx(i, j + 1)))
    uvs = [(i / N, j / N) for i in range(N + 1) for j in range(N + 1)]
    o = _obj('Tovaglia', gen('open'), F, [0] * len(F), [M['cloth']], coll, parent, loc, smooth_upto=len(F), uvs=uvs)
    _add_key(o, 'inv', gen('inv')); _add_key(o, 'flat', gen('flat'))
    return o


# ---------------------------------------------------------------------------------------------- cupola tonda
def round_canopy(coll, M, name, mats, pattern, R=2.3, D=1.55, nseg=12, vent=0.0, L=3.0, riser=0.22, line_mat=None, parent=None, loc=(0, 0, 0), scallop=0.07, parts='all'):
    """cupola a spicchi con funi che convergono su due bretelle. Origine = attacco spalle. Chiave 'closed' (a fiamma, sgonfia).
    mats: lista materiali; pattern(g) -> indice materiale dello spicchio g; ultimi due materiali = funi, bretelle."""
    sub = 4; nr = 10; nk = nseg * sub; th0 = math.asin(min(0.99, vent / R)) if vent > 0 else 0.10; th1 = 1.72
    LI = len(mats) - 2; WI = len(mats) - 1
    def gen(mode):
        V = []
        for i in range(nr + 1):
            th = th0 + (th1 - th0) * i / nr
            for k in range(nk):
                an = 2 * math.pi * k / nk; fr_ = (k % sub) / sub
                r = R * math.sin(th) * (1 + scallop * math.sin(math.pi * fr_) * (i / nr) ** 2); z = D * math.cos(th)
                if mode == 'closed':
                    r = 0.10 * r * (1 + 0.5 * math.sin(3 * an + i)) + 0.05; z = 1.9 * D * math.cos(th) - 0.3 * L + 0.1 * math.sin(4 * an)
                V.append((r * math.cos(an), r * math.sin(an), L + z))
        if vent <= 0: V.append((0, 0, L + (D if mode != 'closed' else 1.9 * D - 0.3 * L)))
        base = len(V); F = []; MI = []
        for i in range(nr):
            for k in range(nk):
                if parts == 'lines': continue
                k2 = (k + 1) % nk; F.append((i * nk + k, (i + 1) * nk + k, (i + 1) * nk + k2, i * nk + k2)); MI.append(pattern(k // sub, i))
        if vent <= 0 and parts != 'lines':
            for k in range(nk): F.append((base - 1, k, (k + 1) % nk)); MI.append(pattern(k // sub, 0))
        nsm = len(F)
        tops = {s: (s * riser * 1.15, 0.0, 0.55) for s in (-1, 1)}
        if vent > 0 and parts != 'lines':            # bordo rinforzato del foro
            for k in range(nk): _tube(V, F, MI, V[k], V[(k + 1) % nk], 0.035, WI)
        if parts == 'cloth': return V, F, MI, nsm
        for s in (-1, 1): _tube(V, F, MI, (s * riser, 0, 0), tops[s], 0.028, WI)
        for g in range(nseg):
            p = V[nr * nk + g * sub]; s = 1 if p[0] >= 0 else -1
            _tube(V, F, MI, tops[s], p, 0.011, LI)
        return V, F, MI, nsm
    V, F, MI, nsm = gen('open')
    o = _obj(name, V, F, MI, mats, coll, parent, loc, smooth_upto=nsm)
    _add_key(o, 'closed', gen('closed')[0])
    return o


def vent_patch(coll, mat, r, parent, z):
    """toppa che copre il foro in cima (viene 'tagliata via')."""
    V = [(0, 0, 0.02)]; n = 24
    for k in range(n): V.append((r * 1.08 * math.cos(2 * math.pi * k / n), r * 1.08 * math.sin(2 * math.pi * k / n), -0.03))
    F = [(0, 1 + k, 1 + (k + 1) % n) for k in range(n)]
    return _obj('VentPatch', V, F, [0] * n, [mat], coll, parent, (0, 0, z), smooth_upto=n)


# ---------------------------------------------------------------------------------------------- ala a celle
def ram_air(coll, M, name='Ala', span=5.4, chord=2.3, ncell=9, L=3.3, parent=None, loc=(0, 0, 0), cols=(0, 2, 1)):
    """paracadute a profilo alare: celle gonfie, bocche aperte sul bordo d'attacco (-Y), funi, comandi. Chiave 'closed'.
    Origine = attacco spalle. Restituisce (oggetto, posizione dei comandi L/R nello spazio locale)."""
    sub = 4; ns = ncell * sub; nc = 10; arc = 0.62; Ra = (span / 2) / arc; th = 0.13 * chord
    mats = [M['nyl'][cols[0]], M['nyl'][cols[1]], M['nyl'][cols[2]], M['inside'], M['line'], M['web'], M['toggle']]
    def prof(c):
        return th * (2.969 * math.sqrt(c) - 1.26 * c - 3.516 * c * c + 2.843 * c ** 3 - 1.015 * c ** 4) / 1.0
    def pt(s, c, top, mode, cf):
        ph = s * arc; t = prof(c)
        zl = (0.62 * t + 0.07 * abs(math.sin(math.pi * cf)) * (1 - c) ** 0.5) if top else (-0.22 * t - 0.025 * abs(math.sin(math.pi * cf)))
        zl += 0.10 * chord * (c - 0.35)            # incidenza: bordo d'attacco più basso
        b = 1.0 if (mode == 'brakeL' and s < 0) or (mode == 'brakeR' and s > 0) else 0.0
        if b and c > 0.7: zl -= 0.34 * chord * ((c - 0.7) / 0.3) ** 2 * min(1.0, abs(s) * 2.5)
        x = (Ra + zl) * math.sin(ph); z = (Ra + zl) * math.cos(ph) - Ra; y = (c - 0.35) * chord
        if mode == 'closed':
            x = 0.10 * x + 0.06 * math.sin(9 * c + 5 * s); y = 0.35 * y; z = 0.25 * zl + 0.9 * c - 0.2 * L + 0.4 * abs(s)
        return (x, y, L + z)
    def gen(mode):
        V = []; F = []; MI = []
        def cellmat(cell):
            m = abs(cell - ncell // 2); return 2 if m == 0 else (0 if m % 2 else 1)
        ctop = [j / nc for j in range(nc + 1)]; cbot = [0.10 + 0.90 * j / nc for j in range(nc + 1)]
        T0 = len(V)
        for i in range(ns + 1):
            for c in ctop: V.append(pt(-1 + 2 * i / ns, c, True, mode, (i % sub) / sub))
        B0 = len(V)
        for i in range(ns + 1):
            for c in cbot: V.append(pt(-1 + 2 * i / ns, c, False, mode, (i % sub) / sub))
        W = nc + 1
        for i in range(ns):
            for j in range(nc):
                F.append((T0 + i * W + j, T0 + (i + 1) * W + j, T0 + (i + 1) * W + j + 1, T0 + i * W + j + 1)); MI.append(cellmat(i // sub))
                F.append((B0 + i * W + j, B0 + i * W + j + 1, B0 + (i + 1) * W + j + 1, B0 + (i + 1) * W + j)); MI.append(cellmat(i // sub))
        for i in range(0, ns + 1, sub):            # centine (interno scuro) + chiusura alle estremità
            for j in range(nc):
                F.append((T0 + i * W + j, T0 + i * W + j + 1, B0 + i * W + j + 1, B0 + i * W + j)); MI.append(3 if 0 < i < ns else cellmat(min(i // sub, ncell - 1)))
        nsm = len(F)
        tops = {}
        for s in (-1, 1):
            for fy, tag in ((-0.07, 'f'), (0.09, 'r')):
                tops[(s, tag)] = (s * 0.27, fy, 0.62); _tube(V, F, MI, (s * 0.21, 0.0, 0.0), tops[(s, tag)], 0.024, 5)
        for i in range(0, ns + 1, sub):
            s = -1 if i < ns / 2 else 1
            if i == ns // 2: continue
            for jc, tag in ((1, 'f'), (4, 'f'), (7, 'r')):
                _tube(V, F, MI, tops[(s, tag)], V[B0 + i * W + jc], 0.010, 4)
        tg = {}
        for s in (-1, 1):
            b = 1.0 if (mode == 'brakeL' and s < 0) or (mode == 'brakeR' and s > 0) else 0.0
            tg[s] = (s * (0.40 + 0.02 * b), 0.16 - 0.06 * b, 0.52 - 1.02 * b); casc = (s * 0.40, 0.16, 1.02 - 0.5 * b)
            for i in ([2, 6, 10, 14] if s < 0 else [ns - 2, ns - 6, ns - 10, ns - 14]):
                _tube(V, F, MI, casc, V[B0 + i * W + nc], 0.008, 4)
            _tube(V, F, MI, casc, tg[s], 0.010, 4)
            _tube(V, F, MI, (tg[s][0] - 0.07, tg[s][1], tg[s][2]), (tg[s][0] + 0.07, tg[s][1], tg[s][2]), 0.026, 6)
        # slider (rettangolo di tela tra le bretelle)
        for (a_, b_) in (((-0.33, -0.12, 1.0), (0.33, -0.12, 1.0)), ((-0.33, 0.14, 1.0), (0.33, 0.14, 1.0)), ((-0.33, -0.12, 1.0), (-0.33, 0.14, 1.0)), ((0.33, -0.12, 1.0), (0.33, 0.14, 1.0))):
            _tube(V, F, MI, a_, b_, 0.02, 2)
        return V, F, MI, nsm, tg
    V, F, MI, nsm, tg = gen('open')
    o = _obj(name, V, F, MI, mats, coll, parent, loc, smooth_upto=nsm)
    _add_key(o, 'closed', gen('closed')[0]); _add_key(o, 'brakeL', gen('brakeL')[0]); _add_key(o, 'brakeR', gen('brakeR')[0])
    return o, tg


# ---------------------------------------------------------------------------------------------- imbracatura / zaino / occhialoni
def harness(coll, M, body, pack=True, reserve=False):
    """imbracatura sul busto di Pippo (figlia di 'body'): bretelle, pettorale, cosciali, zaino con maniglia rossa."""
    mb = MB([M['web'], M['pack'], M['packr'], M['buckle'], M['toggle']])
    for s in (-1, 1):
        mb.box((s * 0.13, -0.235, 0.52), (0.055, 0.03, 0.44), 0, rx=0.06)           # bretelle davanti
        mb.box((s * 0.13, 0.235, 0.52), (0.055, 0.03, 0.44), 0, rx=-0.06)
        mb.box((s * 0.13, 0.0, 0.775), (0.055, 0.50, 0.03), 0)                       # sopra la spalla
        mb.box((s * 0.14, 0.0, 0.03), (0.07, 0.30, 0.035), 0)                        # cosciali
        mb.box((s * 0.13, -0.255, 0.60), (0.07, 0.03, 0.05), 3)                      # fibbie
    mb.box((0, -0.248, 0.47), (0.32, 0.03, 0.05), 0); mb.box((0, -0.262, 0.47), (0.07, 0.03, 0.06), 3)
    mb.box((0, 0.0, 0.20), (0.50, 0.50, 0.04), 0)                                    # cintura
    if pack:
        mb.box((0, 0.36, 0.46), (0.40, 0.20, 0.52), 1); mb.box((0, 0.47, 0.46), (0.30, 0.04, 0.40), 0)
        mb.box((0.21, 0.30, 0.30), (0.03, 0.08, 0.10), 2)                            # maniglia apertura
    if reserve:
        mb.box((0, 0.36, 0.80), (0.36, 0.18, 0.16), 2); mb.box((-0.19, -0.262, 0.56), (0.04, 0.03, 0.10), 2)
    o = mb.build('Imbracatura', coll); o.parent = body
    return o


def goggles(coll, M, head, eye_x, eye_y, eye_z, r=0.11, tilt=0.0, strap_r=(0.30, 0.28)):
    """occhialoni da aviatore: due anelli con lente, ponte e cinghia. Centrati in (0, eye_y, eye_z) locale alla testa."""
    root = empty('Occhialoni', (0, eye_y, eye_z), head, coll); root.rotation_euler = (tilt, 0, 0)
    for s in (-1, 1):
        set004.cyl('GogRing', r, 0.07, (s * eye_x, 0, 0), M['gogf'], coll, rot=(math.pi / 2, 0, 0), parent=root)
        set004.cyl('GogLens', r * 0.82, 0.075, (s * eye_x, -0.004, 0), M['lens'], coll, rot=(math.pi / 2, 0, 0), parent=root)
    set004.obj('GogBridge', set004.box_c(), (0, 0, 0), (eye_x * 1.2, 0.04, 0.04), M['gogf'], coll, parent=root)
    st = shape('GogStrap', 'cyl:1.0:1.0', (0, -eye_y, 0), (strap_r[0], strap_r[1], 0.045), (0, 0, 0), root, M['web'], coll)
    return root


# ---------------------------------------------------------------------------------------------- aereo
def plane(coll, M):
    """aereo cartoon ad ala alta, muso verso -Y, portellone aperto sul fianco +X. Restituisce (root, elica)."""
    root = empty('Aereo', (0, 0, 0), None, coll)
    S = lambda n, k, loc, sc, mat, rot=(0, 0, 0), par=None: shape(n, k, loc, sc, rot, par or root, mat, coll)
    S('A_Fus', 'cap:1.0:1.0', (0, 0.4, 0), (1.05, 1.15, 3.2), M['pl_w'], rot=(math.pi / 2, 0, 0))
    S('A_Belly', 'cap:1.0:1.0', (0, 0.4, -0.25), (1.0, 0.95, 3.1), M['pl_r'], rot=(math.pi / 2, 0, 0))
    S('A_Nose', 'sphere', (0, -3.0, -0.05), (0.80, 0.9, 0.80), M['pl_r'])
    S('A_Spin', 'sphere', (0, -3.85, -0.05), (0.28, 0.35, 0.28), M['pl_y'])
    S('A_Wind', 'sphere', (0, -1.75, 0.62), (0.80, 0.85, 0.50), M['pl_g'])
    mb = MB([M['pl_y'], M['pl_w'], M['pl_r'], M['pl_d'], M['pl_g']])
    mb.box((0, -0.6, 1.28), (11.0, 1.9, 0.20), 0); mb.box((0, -0.6, 1.40), (10.6, 1.5, 0.08), 0)       # ala
    for s in (-1, 1):
        mb.box((s * 5.55, -0.6, 1.30), (0.25, 1.7, 0.30), 2)                                           # estremità rosse
        mb.box((s * 2.4, -0.55, 0.45), (0.10, 0.12, 2.3), 1, rz=0.0, rx=0.0)                           # montanti
        mb.box((s * 1.25, -1.0, -1.35), (0.14, 0.14, 0.9), 1)                                         # carrello
        shape('A_Wheel', 'cyl:0.38:0.22', (s * 1.25, -1.0, -1.85), (1, 1, 1), (0, math.pi / 2, 0), root, M['pl_d'], coll)
        for wy in (-0.2, 1.0, 2.0): mb.box((s * 1.03, wy + (1.2 if s > 0 else 0), 0.42), (0.06, 0.55, 0.45), 4)       # finestrini
    mb.box((0, 4.6, 1.05), (0.16, 1.4, 1.7), 2); mb.box((0, 4.75, 0.30), (3.8, 1.0, 0.14), 0)           # deriva e piani di coda
    mb.box((1.04, 0.35, 0.05), (0.08, 1.25, 1.5), 3)                                                    # portellone aperto (vano scuro)
    mb.box((1.10, 1.70, 0.05), (0.06, 1.25, 1.5), 1)                                                    # porta scorrevole
    mb.box((1.15, 0.35, -0.78), (0.5, 1.3, 0.08), 3)                                                    # predellino
    for z in (-0.02,): mb.box((0, 1.6, 0.05), (2.12, 3.6, 0.16), 2)                                     # fascia rossa
    o = mb.build('A_Parts', coll); o.parent = root
    prop = empty('Elica', (0, -3.95, -0.05), root, coll)
    for k in range(2):
        b = shape('A_Blade', 'sphere', (0, 0, 0), (0.12, 0.04, 1.25), (0, k * math.pi / 2, 0), prop, M['pl_d'], coll)
    shape('A_Disc', 'cyl:1.0:1.0', (0, 0, 0), (1.25, 1.25, 0.02), (math.pi / 2, 0, 0), prop, M['propdisc'], coll)
    return root, prop


def bandana(coll, M, parent, loc, rot=(0, 0, 0), w=0.30, h=0.26):
    """fazzoletto a quadretti (un pezzo della tovaglia)."""
    V = [(-w / 2, 0, 0), (w / 2, 0, 0), (0, 0, -h), (-w / 2, 0.03, 0.05), (w / 2, 0.03, 0.05)]
    F = [(0, 1, 2), (0, 3, 4, 1)]
    o = _obj('Bandana', V, F, [0, 0], [M['cloth']], coll, parent, loc, uvs=[(0, 0.3), (0.3, 0.3), (0.15, 0.0), (0, 0.36), (0.3, 0.36)])
    o.rotation_euler = rot
    return o
