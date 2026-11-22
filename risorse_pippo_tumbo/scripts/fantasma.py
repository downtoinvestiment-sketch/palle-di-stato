"""Il Fantasma: nuovo politico della serie (22 novembre 2026), chiesto dall'autore: un politico coperto da un telo da fantasma
con due buchi per gli occhi. Sotto il telo non si vede chi c'e' (nessuna faccia: non e' e non puo' diventare il ritratto di una persona reale).
    import fantasma as fa
    F = fa.fantasma(coll, stile='A')        # 'A' telo bianco e scarpe lucide, 'B' con cravatta rossa e spilla, 'C' con la giacca sopra il telo
    fa.occhi(F, f, look=(0, 0), lid=0.0, arrabbiato=0.0)     # gli occhi nei buchi sono l'unica espressione
    fa.emozione(F, f, 'furbo')               # una delle EMOZIONI
    fa.gesto(F, f, 'saluto')                 # uno dei GESTI (niente braccia: si piegano testa e telo)
Fronte -Y, base a z = 0. Alto circa 175 cm come Pippo (2,30 unita').
Dizionario: root, body, telo, head, eyeL/R, pupilL/R, lidL/R, browL/R, hipL/R, mats. Niente braccia; il telo finisce alle ginocchia e sotto si vedono i pantaloni da politico."""
import math, bpy, bmesh
from mathutils import Vector
from common import material, shape, empty
PI = math.pi
H = 2.30                                                                     # altezza in cima al telo
Z0 = 0.78                                                                    # il telo finisce alle ginocchia: sotto si vedono i pantaloni
ZE = 1.86                                                                    # quota dei buchi degli occhi


def mats(stile='A'):
    m = lambda n, c, **k: material('FAN_' + n, c, **k)
    return dict(telo=m('telo', (0.93, 0.93, 0.9), rough=0.75), buco=m('buco', (0.01, 0.01, 0.012), rough=0.9), bianco=m('bianco', (0.98, 0.98, 0.98), rough=0.3),
                nero=m('nero', (0.02, 0.02, 0.02), rough=0.15), scarpe=m('scarpe', (0.02, 0.02, 0.025), rough=0.08, spec=0.9), guanti=m('guanti', (0.97, 0.97, 0.97), rough=0.5),
                cravatta=m('cravatta', (0.75, 0.06, 0.08), rough=0.45), oro=m('oro', (1.0, 0.75, 0.2), rough=0.25, metallic=0.9),
                giacca=m('giacca', (0.1, 0.12, 0.2), rough=0.6), pantaloni=m('pantaloni', (0.1, 0.12, 0.2), rough=0.6), piega=m('piega', (0.05, 0.06, 0.1), rough=0.6), camicia=m('camicia', (0.95, 0.95, 0.97), rough=0.6), iride=m('iride', (0.3, 0.42, 0.25), rough=0.3))


def _raggio(z):
    """profilo del telo: cupola sulla testa, poi si allarga fino a terra"""
    zc, R = H - 0.4, 0.4
    if z >= zc - 0.1: return math.sqrt(max(0.0, R * R - (z - zc) ** 2)) if z > zc else R * (1 - 0.15 * (zc - z) / 0.1)
    t = (zc - 0.1 - z) / (zc - 0.1 - Z0)                                     # 0 sotto la testa, 1 all'orlo
    return 0.34 + 0.2 * max(0.0, t) ** 1.3


def _telo(coll, parent, mat):
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=96, v_segments=60, radius=1.0)
    for v in bm.verts:
        x, y, z = v.co; th = math.atan2(y, x); rr = math.hypot(x, y)
        zz = Z0 + (z + 1) / 2 * (H - Z0)                                     # dall'orlo (Z0) alla cima (H)
        if z < -0.97: zz = Z0 + 0.1; r = _raggio(Z0) * rr / 0.243 * 0.6        # dentro l'orlo (non si vede)
        else: r = _raggio(zz) * (1 + 0.035 * math.sin(11 * th + zz * 2.5) * (1 - min(1.0, (zz - Z0) / (H - 0.5 - Z0))))   # pieghe che si aprono verso il basso
        if rr < 1e-5: r = 0.0
        orlo = 0.035 * math.sin(7 * th) * max(0.0, 1 - (zz - Z0) / 0.2) if z >= -0.97 else 0.0        # orlo ondulato
        v.co = (math.cos(th) * r, math.sin(th) * r * 0.92, zz + orlo)
    me = bpy.data.meshes.new('FAN_Telo'); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    o = bpy.data.objects.new('FAN_Telo', me); coll.objects.link(o); o.parent = parent; me.materials.append(mat)
    o.modifiers.new('Liscio', 'SUBSURF').levels = 1
    return o


def fantasma(coll, stile='A', M=None, scala=1.0):
    M = M or mats(stile); R = {'mats': M, 'stile': stile}
    S = lambda n, k, loc, sc=(1, 1, 1), par=None, mat=None, rot=(0, 0, 0): shape('FAN_' + n, k, loc, sc, rot, par, mat, coll)
    E = lambda n, loc, par: empty('FAN_' + n, loc, par, coll)
    root = R['root'] = E('Root', (0, 0, 0), None); root.scale = (scala,) * 3; body = R['body'] = E('Body', (0, 0, 0), root)
    R['telo'] = _telo(coll, body, M['telo'])
    head = R['head'] = E('Head', (0, 0, ZE), body)
    yf = -_raggio(ZE) * 0.92                                                 # davanti al telo all'altezza degli occhi
    for s_, nm in ((-1, 'L'), (1, 'R')):
        x = s_ * 0.13; yy = yf * math.sqrt(max(0.0, 1 - (x / _raggio(ZE)) ** 2))
        S('Buco', 'sphere', (x, yy + 0.006, 0.0), (0.085, 0.03, 0.085), head, M['buco'])   # i due buchi tondi nel telo
        eye = R['eye' + nm] = E('Eye' + nm, (x, yy - 0.014, 0.0), head)                    # l'occhio tondo si vede dentro il buco
        S('Occhio', 'sphere', (0, 0, 0), (0.058, 0.022, 0.058), eye, M['bianco'])
        pu = R['pupil' + nm] = E('Sguardo' + nm, (0, -0.02, 0), eye)
        S('Iride', 'sphere', (0, 0.004, 0), (0.035, 0.012, 0.04), pu, M['iride']); S('Pupilla', 'sphere', (0, 0, 0), (0.018, 0.012, 0.022), pu, M['nero'])
        S('Luce', 'sphere_lo', (0.012, -0.03, 0.02), (0.008, 0.005, 0.01), eye, M['bianco'])
        R['lid' + nm] = S('Palpebra', 'sphere', (0, -0.008, 0.06), (0.062, 0.032, 0.001), eye, M['buco'])   # il bordo del buco che si chiude
        b = R['brow' + nm] = E('Brow' + nm, (x, yy - 0.005, 0.13), head)
        S('Piega', 'sphere', (0, 0, 0), (0.09, 0.02, 0.018), b, M['telo'])  # piega del telo sopra il buco: fa da sopracciglio
    # niente braccia (22 nov): sotto il telo spuntano i pantaloni da politico, con la piega, e le scarpe lucide
    for s_, nm in ((-1, 'L'), (1, 'R')):
        hp = R['hip' + nm] = E('Hip' + nm, (s_ * 0.15, 0, 0.95), body)
        S('Gamba', 'cap:0.105:0.42', (0, 0, -0.42), par=hp, mat=M['pantaloni']); S('Piega', 'cyl:1:1', (0, -0.1, -0.45), (0.006, 0.006, 0.36), hp, M['piega'])
        S('Orlo', 'cyl:0.112:0.03', (0, 0, -0.82), par=hp, mat=M['pantaloni'])
        S('Scarpa', 'sphere', (0, -0.06, -0.88), (0.11, 0.19, 0.07), hp, M['scarpe'])
    if stile in ('B', 'C'):                                                  # cravatta e spilla appuntate sul telo
        dy = -0.13 if stile == 'C' else 0.0                                  # con la giacca la cravatta sta sopra la camicia
        S('Nodo', 'sphere', (0, -0.385 + dy, 1.42 if stile == 'C' else 1.5), (0.05, 0.03, 0.045), body, M['cravatta'])
        S('Cravatta', 'sphere', (0, -0.42 + dy, 1.2 if stile == 'C' else 1.25), (0.065, 0.03, 0.22), body, M['cravatta'], rot=(-0.12, 0, 0))
        S('Spilla', 'cyl:1:1', (-0.17, -0.41 + dy, 1.4 if stile == 'C' else 1.48), (0.035, 0.035, 0.01), body, M['oro'], rot=(PI / 2 - 0.15, 0, 0))
    if stile == 'C':                                                         # giacca da politico infilata sopra il telo
        S('Giacca', 'cap:0.5:0.3', (0, 0.0, 1.12), (1.12, 1.02, 0.75), body, M['giacca'])   # sotto gli occhi, fino ai fianchi
        for s_ in (-1, 1): S('Bavero', 'sphere', (s_ * 0.13, -0.5, 1.3), (0.09, 0.03, 0.2), body, M['giacca'], rot=(0, s_ * 0.35, 0))
        S('Sparato', 'sphere', (0, -0.51, 1.3), (0.12, 0.02, 0.16), body, M['camicia'])
        for k in range(2): S('Bottone', 'sphere', (0.0, -0.56, 1.05 - 0.14 * k), (0.025, 0.012, 0.025), body, M['oro'])
    emozione(R, None, 'furbo'); gesto(R, None, 'riposo')
    return R


def _k(o, prop, f):
    if f is not None: o.keyframe_insert(prop, frame=f)


def occhi(R, f, look=(0.0, 0.0), lid=0.0, arrabbiato=0.0, alza=0.0, grandi=1.0):
    """look (x, z); lid 0 aperto .. 1 chiuso; arrabbiato > 0 pieghe a V, < 0 preoccupato; alza solleva le pieghe; grandi scala gli occhi."""
    for s_, nm in ((-1, 'L'), (1, 'R')):
        p = R['pupil' + nm]; p.location = (look[0] * 0.022, -0.02, look[1] * 0.025); _k(p, 'location', f)
        l = R['lid' + nm]; l.scale = (0.062, 0.032, 0.001 + 0.065 * lid); l.location = (0, -0.008, 0.06 - 0.06 * lid); _k(l, 'scale', f); _k(l, 'location', f)
        b = R['brow' + nm]; b.rotation_euler = (0, -s_ * arrabbiato * 0.45, 0); b.location = (b.location.x, b.location.y, 0.13 + 0.04 * alza - 0.02 * max(0.0, arrabbiato)); _k(b, 'rotation_euler', f); _k(b, 'location', f)
        e = R['eye' + nm]; e.scale = (grandi,) * 3; _k(e, 'scale', f)


EMOZIONI = {
    'neutro': dict(), 'furbo': dict(lid=0.45, look=(-0.7, 0), arrabbiato=0.4), 'arrabbiato': dict(arrabbiato=1.2, lid=0.25), 'sorpreso': dict(alza=1.0, grandi=1.25),
    'spaventato': dict(alza=1.2, arrabbiato=-0.8, grandi=1.3, look=(0, 0.6)), 'colpevole': dict(lid=0.5, look=(0.8, -0.6), arrabbiato=-0.5), 'annoiato': dict(lid=0.6),
}
def emozione(R, f, nome): occhi(R, f, **EMOZIONI[nome])

GESTI = {                                                                    # niente braccia: il telo si piega (testa rot x, y, z; busto rot x, y)
    'riposo': ((0, 0, 0), (0, 0)), 'saluto': ((0, 0.12, 0), (0, 0.08)), 'comizio': ((-0.12, 0, 0), (-0.08, 0)), 'buuu': ((0.12, 0, 0), (0.15, 0)),
    'non sono stato io': ((0, 0, 0.25), (0, 0.1)), 'inchino': ((0.2, 0, 0), (0.35, 0)), 'sospetto': ((0.05, 0.15, -0.2), (0.05, -0.08)),
}
def gesto(R, f, nome):
    t, b = GESTI[nome]
    R['head'].rotation_euler = t; _k(R['head'], 'rotation_euler', f); R['body'].rotation_euler = (b[0], b[1], 0); _k(R['body'], 'rotation_euler', f)
