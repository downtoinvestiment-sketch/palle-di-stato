"""Animali nello stile di Pippo e Tumbo: capsule, ellissoidi, occhi grandi, materiali opachi. Niente modelli a cubo.
Tutti guardano verso -Y con rot_z = 0, origine a terra. Ogni funzione restituisce un dizionario:
root, body, head, eyeL/R, pupilL/R, legs[] (dove ci sono), tail (dove c'e').
Uso: import animali; A = animali.crea('mucca', coll); A['root'].location = (x, y, 0)"""
import bpy, math
from mathutils import Vector
from common import material, shape, empty, collection
PI = math.pi
cap = lambda r, L: 'cap:%g:%g' % (r, L)

def _mat(name, col, **k):
    return bpy.data.materials.get(name) or material(name, col, **k)

def _kit(coll, pfx):
    S = lambda n, k, loc, sc, par, mat, rot=(0, 0, 0): shape(pfx + n, k, loc, sc, rot, par, mat, coll)
    E = lambda n, loc, par: empty(pfx + n, loc, par, coll)
    M = {'white': _mat('AN_EyeW', (1, 1, 1), rough=0.3, spec=0.5), 'pupil': _mat('AN_Pupil', (0.02, 0.015, 0.02), rough=0.15, spec=1.0),
         'shine': _mat('AN_Shine', (1, 1, 1), rough=0.2, emit=(1, 1, 1), emit_strength=1.5), 'black': _mat('AN_Black', (0.03, 0.025, 0.03), rough=0.4, spec=0.5),
         'cream': _mat('AN_Cream', (1.0, 0.90, 0.72), rough=0.85, spec=0.15), 'pink': _mat('AN_Pink', (1.0, 0.60, 0.66), rough=0.8, spec=0.2),
         'hoof': _mat('AN_Hoof', (0.16, 0.10, 0.07), rough=0.6), 'orange': _mat('AN_Orange', (1.0, 0.45, 0.05), rough=0.6, spec=0.3)}
    return S, E, M

def _eyes(R, S, E, head, M, dx, y, z, k=1.0, brow=None):
    """occhi come quelli di Tumbo: ellissoide bianco, pupilla scura, riflesso."""
    for s, nm in ((-1, 'L'), (1, 'R')):
        eye = E('Eye' + nm, (s * dx, y, z), head)
        S('EyeW' + nm, 'sphere', (0, 0, 0), (0.088 * k, 0.052 * k, 0.098 * k), eye, M['white'])
        pup = E('Pupil' + nm, (0, -0.045 * k, 0), eye)
        S('Pup' + nm, 'sphere', (0, 0, 0), (0.052 * k, 0.022 * k, 0.062 * k), pup, M['pupil'])
        S('Shine' + nm, 'sphere_lo', (-0.016 * k, -0.019 * k, 0.024 * k), (0.016 * k, 0.009 * k, 0.018 * k), pup, M['shine'])
        R['eye' + nm] = eye; R['pupil' + nm] = pup
        if brow:
            b = E('Brow' + nm, (s * dx, y + 0.03 * k, z + 0.115 * k), head); S('BrowS' + nm, 'sphere', (0, 0, 0), (0.07 * k, 0.03 * k, 0.03 * k), b, brow); R['brow' + nm] = b

def _tube(S, name, pts, r0, r1, par, mat, n=14):
    """tubo morbido fatto di sfere lungo una spezzata (proboscidi, code, colli)."""
    pts = [Vector(p) for p in pts]; seg = [(pts[i + 1] - pts[i]).length for i in range(len(pts) - 1)]; tot = sum(seg)
    for k in range(n + 1):
        d = tot * k / n; i = 0
        while i < len(seg) - 1 and d > seg[i]: d -= seg[i]; i += 1
        p = pts[i].lerp(pts[i + 1], min(1.0, d / seg[i]) if seg[i] > 0 else 0.0); r = r0 + (r1 - r0) * k / n
        S('%s%d' % (name, k), 'sphere_lo', tuple(p), (r, r, r), par, mat)

def _spot(S, name, a, y, rx, rz, sy, sz, par, mat, thick=0.045):
    """macchia piatta appoggiata sul fianco di un corpo con asse lungo Y (a = angolo attorno all'asse)."""
    S(name, 'sphere', (rx * 0.985 * math.cos(a), y, rz * 0.985 * math.sin(a)), (thick, sy, sz), par, mat, rot=(0, -a, 0))

def _start(coll, pfx, name, zbody, scale):
    S, E, M = _kit(coll or collection('Animali'), pfx)
    R = {'mats': M, 'name': name}; root = E('Root', (0, 0, 0), None); root.scale = (scale,) * 3; root.rotation_mode = 'XYZ'
    body = E('Body', (0, 0, zbody), root); R.update(root=root, body=body, legs=[]); return S, E, M, R, root, body

# ---------------------------------------------------------------------------------------------------- mucca
def mucca(coll=None, scale=1.15):
    S, E, M, R, root, body = _start(coll, 'Mu_', 'mucca', 0.86, scale)
    w = _mat('AN_CowW', (0.97, 0.96, 0.93), rough=0.85, spec=0.15); horn = _mat('AN_Horn', (0.93, 0.85, 0.66), rough=0.5); bell = _mat('AN_Bell', (1.0, 0.78, 0.12), rough=0.3, metallic=0.7)
    S('Corpo', cap(0.40, 0.62), (0, 0, 0), (1, 1, 1), body, w, rot=(PI / 2, 0, 0))
    for i, (a, y, sy, sz) in enumerate(((0.5, -0.25, 0.2, 0.17), (1.3, 0.25, 0.26, 0.2), (2.4, -0.1, 0.2, 0.22), (2.9, 0.45, 0.16, 0.14), (0.1, 0.42, 0.17, 0.2), (1.9, -0.5, 0.14, 0.13), (3.6, 0.1, 0.15, 0.14), (-0.5, -0.05, 0.15, 0.13))):
        _spot(S, 'Macchia%d' % i, a, y, 0.40, 0.40, sy, sz, body, M['black'])
    S('Mammella', 'sphere', (0, 0.3, -0.37), (0.18, 0.2, 0.12), body, M['pink'])
    head = E('Head', (0, -0.86, 0.3), body); R['head'] = head
    S('Testa', 'sphere', (0, 0, 0), (0.33, 0.31, 0.31), head, w); S('Muso', 'sphere', (0, -0.24, -0.1), (0.25, 0.17, 0.17), head, M['pink'])
    S('ToppaOcchio', 'sphere', (0.15, -0.2, 0.1), (0.15, 0.1, 0.16), head, M['black'])
    for s in (-1, 1):
        S('Narice%d' % s, 'sphere', (s * 0.09, -0.4, -0.07), (0.03, 0.02, 0.035), head, M['black'])
        S('Corno%d' % s, 'cone', (s * 0.19, 0.0, 0.24), (0.05, 0.05, 0.19), head, horn, rot=(0, s * 0.5, 0))
        S('Orecchio%d' % s, 'sphere', (s * 0.37, 0.03, 0.12), (0.15, 0.05, 0.08), head, w, rot=(0, -s * 0.3, 0))
    _eyes(R, S, E, head, M, 0.13, -0.265, 0.09, 1.15)
    S('Campanaccio', 'sphere', (0, -0.8, -0.2), (0.075, 0.075, 0.085), body, bell)
    for (sx, sy) in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        lg = E('Leg%d%d' % (sx, sy), (sx * 0.24, sy * 0.42, -0.25), body); R['legs'].append(lg)
        S('Gamba%d%d' % (sx, sy), cap(0.095, 0.5), (0, 0, -0.2), (1, 1, 1), lg, w); S('Zoccolo%d%d' % (sx, sy), 'cyl:0.105:0.14', (0, 0, -0.54), (1, 1, 1), lg, M['hoof'])
    tail = E('Tail', (0, 0.72, 0.12), body); R['tail'] = tail
    _tube(S, 'Coda', ((0, 0.02, 0), (0, 0.1, -0.25), (0, 0.1, -0.52)), 0.035, 0.03, tail, w, 8); S('Ciuffo', 'sphere', (0, 0.1, -0.6), (0.07, 0.07, 0.1), tail, M['black'])
    return R

# ---------------------------------------------------------------------------------------------------- elefante
def elefante(coll=None, scale=1.0):
    S, E, M, R, root, body = _start(coll, 'El_', 'elefante', 1.2, scale)
    g = _mat('AN_Ele', (0.62, 0.66, 0.74), rough=0.85, spec=0.15); gd = _mat('AN_EleD', (0.50, 0.54, 0.62), rough=0.85, spec=0.15); ivory = _mat('AN_Ivory', (0.98, 0.95, 0.86), rough=0.35)
    S('Corpo', 'sphere', (0, 0, 0), (0.72, 0.92, 0.68), body, g)
    head = E('Head', (0, -0.98, 0.32), body); R['head'] = head
    S('Testa', 'sphere', (0, 0, 0), (0.5, 0.48, 0.5), head, g)
    for s in (-1, 1):
        S('Orecchio%d' % s, 'sphere', (s * 0.62, 0.12, 0.05), (0.42, 0.07, 0.5), head, g, rot=(0, 0, s * 0.35)); S('OrecchioIn%d' % s, 'sphere', (s * 0.61, 0.07, 0.03), (0.31, 0.05, 0.38), head, M['pink'], rot=(0, 0, s * 0.35))
        S('Zanna%d' % s, 'cone', (s * 0.2, -0.4, -0.25), (0.06, 0.06, 0.34), head, ivory, rot=(1.95, 0, 0))
    _tube(S, 'Proboscide', ((0, -0.44, -0.08), (0, -0.54, -0.32), (0, -0.58, -0.55), (0, -0.62, -0.75), (0, -0.70, -0.92), (0, -0.83, -1.02), (0, -0.97, -1.0), (0, -1.05, -0.9)), 0.17, 0.085, head, g, 26)
    _eyes(R, S, E, head, M, 0.22, -0.415, 0.12, 1.3)
    for (sx, sy) in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        lg = E('Leg%d%d' % (sx, sy), (sx * 0.36, sy * 0.5, 0), body); R['legs'].append(lg)
        S('Gamba%d%d' % (sx, sy), cap(0.19, 0.45), (0, 0, -0.62), (1, 1, 1), lg, g); S('Piede%d%d' % (sx, sy), 'cyl:0.21:0.2', (0, 0, -1.1), (1, 1, 1), lg, gd)
        for k in (-1, 0, 1): S('Unghia%d%d%d' % (sx, sy, k), 'sphere', (k * 0.1, -0.19 + abs(k) * 0.03, -1.15), (0.05, 0.03, 0.05), lg, M['cream'])
    tail = E('Tail', (0, 0.9, 0.1), body); R['tail'] = tail
    _tube(S, 'Coda', ((0, 0, 0), (0, 0.08, -0.25), (0, 0.08, -0.5)), 0.04, 0.03, tail, g, 8); S('Ciuffo', 'sphere', (0, 0.08, -0.57), (0.06, 0.06, 0.09), tail, gd)
    return R

# ---------------------------------------------------------------------------------------------------- pinguino
def pinguino(coll=None, scale=0.85):
    S, E, M, R, root, body = _start(coll, 'Pi_', 'pinguino', 0.5, scale)
    b = _mat('AN_Peng', (0.07, 0.09, 0.14), rough=0.6, spec=0.3); wh = _mat('AN_PengW', (0.98, 0.98, 0.97), rough=0.8)
    S('Corpo', 'sphere', (0, 0, 0), (0.33, 0.3, 0.46), body, b); S('Pancia', 'sphere', (0, -0.07, -0.03), (0.27, 0.26, 0.4), body, wh)
    head = E('Head', (0, -0.02, 0.5), body); R['head'] = head
    S('Testa', 'sphere', (0, 0, 0), (0.27, 0.26, 0.25), head, b)
    for s in (-1, 1): S('Guancia%d' % s, 'sphere', (s * 0.09, -0.11, 0.0), (0.14, 0.17, 0.16), head, wh)
    S('Becco', 'cone', (0, -0.24, -0.05), (0.075, 0.05, 0.17), head, M['orange'], rot=(PI / 2, 0, 0))
    _eyes(R, S, E, head, M, 0.1, -0.245, 0.05, 0.9)
    for s in (-1, 1):
        w = E('Wing%d' % s, (s * 0.31, 0, 0.2), body); w.rotation_euler = (0, -s * 0.3, 0); R['wing' + ('L' if s < 0 else 'R')] = w
        S('Ala%d' % s, cap(0.075, 0.3), (0, 0, -0.2), (1, 0.45, 1), w, b)
        S('Piede%d' % s, 'sphere', (s * 0.13, -0.13, -0.465), (0.13, 0.18, 0.045), body, M['orange'])
    S('Codino', 'cone', (0, 0.24, -0.3), (0.09, 0.06, 0.16), body, b, rot=(-2.0, 0, 0))
    return R

# ---------------------------------------------------------------------------------------------------- giraffa
def giraffa(coll=None, scale=1.0):
    S, E, M, R, root, body = _start(coll, 'Gi_', 'giraffa', 1.55, scale)
    y_ = _mat('AN_Gir', (1.0, 0.62, 0.08), rough=0.85, spec=0.15); br = _mat('AN_GirB', (0.42, 0.19, 0.05), rough=0.85, spec=0.15)
    S('Corpo', 'sphere', (0, 0, 0), (0.44, 0.72, 0.46), body, y_)
    for i, (a, y, sy, sz) in enumerate(((0.3, -0.2, 0.17, 0.16), (1.1, 0.15, 0.19, 0.17), (2.0, -0.15, 0.18, 0.17), (2.8, 0.2, 0.17, 0.16), (0.0, 0.32, 0.15, 0.15), (1.6, 0.42, 0.14, 0.14), (3.3, -0.1, 0.15, 0.14), (-0.4, 0.0, 0.15, 0.14), (0.8, -0.42, 0.13, 0.13), (2.4, -0.44, 0.13, 0.13))):
        k = math.sqrt(max(0.05, 1 - (y / 0.72) ** 2)); _spot(S, 'Macchia%d' % i, a, y, 0.44 * k, 0.46 * k, sy, sz, body, br)
    neck = ((0, -0.42, 0.18), (0, -0.62, 0.6), (0, -0.8, 1.05), (0, -0.95, 1.5))
    _tube(S, 'Collo', neck, 0.22, 0.15, body, y_, 28)
    for i in range(9):
        t = (i + 0.5) / 9; p = Vector(neck[0]).lerp(Vector(neck[3]), t); r = 0.22 - 0.07 * t
        S('Criniera%d' % i, 'sphere_lo', (0, p.y + r * 0.95, p.z + r * 0.35), (0.04, 0.05, 0.06), body, br)
        if i % 2 == 0:
            for s in (-1, 1): S('MacchiaCollo%d%d' % (i, s), 'sphere_lo', (s * r * 0.85, p.y - 0.02 * s, p.z), (0.04, 0.1, 0.1), body, br)
    head = E('Head', (0, -1.0, 1.64), body); R['head'] = head
    S('Testa', 'sphere', (0, 0, 0), (0.2, 0.26, 0.2), head, y_); S('Muso', 'sphere', (0, -0.24, -0.06), (0.15, 0.16, 0.12), head, M['cream'])
    for s in (-1, 1):
        S('Narice%d' % s, 'sphere', (s * 0.06, -0.385, -0.03), (0.02, 0.014, 0.025), head, br)
        S('Corno%d' % s, cap(0.03, 0.12), (s * 0.08, 0.03, 0.24), (1, 1, 1), head, y_); S('CornoPunta%d' % s, 'sphere', (s * 0.08, 0.03, 0.34), (0.05, 0.05, 0.05), head, br)
        S('Orecchio%d' % s, 'sphere', (s * 0.26, 0.07, 0.08), (0.12, 0.04, 0.07), head, y_, rot=(0, -s * 0.3, 0))
    _eyes(R, S, E, head, M, 0.11, -0.2, 0.06, 0.95)
    for (sx, sy) in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        lg = E('Leg%d%d' % (sx, sy), (sx * 0.24, sy * 0.45, 0), body); R['legs'].append(lg)
        S('Gamba%d%d' % (sx, sy), cap(0.1, 1.1), (0, 0, -0.8), (1, 1, 1), lg, y_)
        S('Zoccolo%d%d' % (sx, sy), 'cyl:0.112:0.15', (0, 0, -1.475), (1, 1, 1), lg, br)
    tail = E('Tail', (0, 0.58, 0.12), body); R['tail'] = tail
    _tube(S, 'Coda', ((0, 0, 0), (0, 0.12, -0.3), (0, 0.13, -0.6)), 0.035, 0.028, tail, y_, 9); S('Ciuffo', 'sphere', (0, 0.13, -0.68), (0.06, 0.06, 0.1), tail, br)
    return R

# ---------------------------------------------------------------------------------------------------- maiale
def maiale(coll=None, scale=1.0):
    S, E, M, R, root, body = _start(coll, 'Ma_', 'maiale', 0.55, scale)
    p = _mat('AN_Pig', (1.0, 0.64, 0.70), rough=0.8, spec=0.2); pd = _mat('AN_PigD', (0.95, 0.44, 0.52), rough=0.75, spec=0.2)
    S('Corpo', cap(0.36, 0.36), (0, 0, 0), (1, 1, 1), body, p, rot=(PI / 2, 0, 0))
    head = E('Head', (0, -0.62, 0.12), body); R['head'] = head
    S('Testa', 'sphere', (0, 0, 0), (0.32, 0.3, 0.3), head, p); S('Grugno', 'cyl:0.125:0.1', (0, -0.3, -0.05), (1, 1, 0.8), head, pd, rot=(PI / 2, 0, 0))
    for s in (-1, 1):
        S('Narice%d' % s, 'sphere', (s * 0.045, -0.352, -0.05), (0.024, 0.012, 0.038), head, M['hoof'])
        S('Orecchio%d' % s, 'cone', (s * 0.2, -0.04, 0.2), (0.11, 0.045, 0.2), head, pd, rot=(0.75, s * 0.45, 0))
        S('Guancia%d' % s, 'sphere', (s * 0.2, -0.2, -0.08), (0.06, 0.03, 0.045), head, pd)
    _eyes(R, S, E, head, M, 0.12, -0.26, 0.08, 1.05)
    for (sx, sy) in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        lg = E('Leg%d%d' % (sx, sy), (sx * 0.2, sy * 0.3, 0), body); R['legs'].append(lg)
        S('Gamba%d%d' % (sx, sy), cap(0.085, 0.12), (0, 0, -0.36), (1, 1, 1), lg, p); S('Zoccolo%d%d' % (sx, sy), 'cyl:0.09:0.08', (0, 0, -0.51), (1, 1, 1), lg, pd)
    tail = E('Tail', (0, 0.7, 0.1), body); R['tail'] = tail
    _tube(S, 'Coda', ((0, 0, 0), (0.07, 0.06, 0.06), (0, 0.1, 0.12), (-0.07, 0.08, 0.17), (0, 0.04, 0.21), (0.05, 0.07, 0.25)), 0.03, 0.022, tail, pd, 16)
    return R

# ---------------------------------------------------------------------------------------------------- leone
def leone(coll=None, scale=1.0):
    S, E, M, R, root, body = _start(coll, 'Le_', 'leone', 0.82, scale)
    t = _mat('AN_Lion', (0.98, 0.58, 0.12), rough=0.85, spec=0.15); mn = _mat('AN_Mane', (0.45, 0.19, 0.04), rough=0.9, spec=0.1)
    S('Corpo', cap(0.33, 0.56), (0, 0, 0), (1, 1, 1), body, t, rot=(PI / 2, 0, 0)); S('Pancia', 'sphere', (0, -0.02, -0.17), (0.26, 0.5, 0.2), body, M['cream'])
    head = E('Head', (0, -0.72, 0.3), body); R['head'] = head
    S('Criniera', 'sphere', (0, 0.08, 0.0), (0.5, 0.34, 0.5), head, mn)
    for i in range(11):
        a = i / 11 * 2 * PI + 0.28; S('Ciocca%d' % i, 'sphere', (0.43 * math.cos(a), -0.02, 0.43 * math.sin(a)), (0.17, 0.16, 0.17), head, mn)
    S('Testa', 'sphere', (0, -0.12, 0), (0.31, 0.29, 0.29), head, t); S('Muso', 'sphere', (0, -0.36, -0.08), (0.17, 0.14, 0.12), head, M['cream'])
    S('Naso', 'sphere', (0, -0.48, -0.03), (0.06, 0.04, 0.045), head, M['hoof']); S('Mento', 'sphere', (0, -0.33, -0.17), (0.1, 0.09, 0.05), head, M['cream'])
    for s in (-1, 1): S('Orecchio%d' % s, 'sphere', (s * 0.25, -0.13, 0.26), (0.09, 0.05, 0.09), head, t)
    _eyes(R, S, E, head, M, 0.12, -0.365, 0.07, 1.05, brow=mn)
    for (sx, sy) in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        lg = E('Leg%d%d' % (sx, sy), (sx * 0.2, sy * 0.4, 0), body); R['legs'].append(lg)
        S('Gamba%d%d' % (sx, sy), cap(0.09, 0.3), (0, 0, -0.4), (1, 1, 1), lg, t); S('Zampa%d%d' % (sx, sy), 'sphere', (0, -0.02, -0.74), (0.11, 0.14, 0.08), lg, M['cream'])
    tail = E('Tail', (0, 0.6, 0.1), body); R['tail'] = tail
    _tube(S, 'Coda', ((0, 0, 0), (0, 0.22, 0.06), (0, 0.4, 0.28), (0, 0.44, 0.56)), 0.045, 0.035, tail, t, 14); S('Ciuffo', 'sphere', (0, 0.44, 0.64), (0.09, 0.09, 0.12), tail, mn)
    return R

# ---------------------------------------------------------------------------------------------------- scimmia
def scimmia(coll=None, scale=0.9):
    S, E, M, R, root, body = _start(coll, 'Sc_', 'scimmia', 0.62, scale)
    b = _mat('AN_Monk', (0.52, 0.31, 0.14), rough=0.85, spec=0.15)
    S('Corpo', 'sphere', (0, 0, 0), (0.27, 0.24, 0.34), body, b); S('Pancia', 'sphere', (0, -0.08, -0.02), (0.2, 0.18, 0.25), body, M['cream'])
    head = E('Head', (0, -0.03, 0.5), body); R['head'] = head
    S('Testa', 'sphere', (0, 0, 0), (0.28, 0.26, 0.26), head, b)
    for s in (-1, 1):
        S('Viso%d' % s, 'sphere', (s * 0.085, -0.115, 0.04), (0.14, 0.16, 0.15), head, M['cream'])
        S('Orecchio%d' % s, 'sphere', (s * 0.3, 0.0, 0.02), (0.1, 0.04, 0.11), head, b); S('OrecchioIn%d' % s, 'sphere', (s * 0.31, -0.028, 0.02), (0.065, 0.03, 0.075), head, M['cream'])
        S('Narice%d' % s, 'sphere', (s * 0.03, -0.325, -0.07), (0.014, 0.01, 0.018), head, M['hoof'])
    S('Muso', 'sphere', (0, -0.21, -0.1), (0.16, 0.12, 0.11), head, M['cream'])
    _eyes(R, S, E, head, M, 0.1, -0.255, 0.05, 0.95)
    for s in (-1, 1):
        arm = E('Arm%d' % s, (s * 0.27, 0, 0.16), body); arm.rotation_euler = (0, -s * 0.16, 0); R['arm' + ('L' if s < 0 else 'R')] = arm
        S('Braccio%d' % s, cap(0.055, 0.42), (0, 0, -0.26), (1, 1, 1), arm, b); S('Mano%d' % s, 'sphere', (0, -0.01, -0.54), (0.075, 0.075, 0.075), arm, M['cream'])
        lg = E('Leg%d' % s, (s * 0.12, 0, 0), body); R['legs'].append(lg)
        S('Gamba%d' % s, cap(0.07, 0.14), (0, 0, -0.44), (1, 1, 1), lg, b); S('Piede%d' % s, 'sphere', (0, -0.06, -0.575), (0.09, 0.14, 0.05), lg, M['cream'])
    tail = E('Tail', (0, 0.2, -0.15), body); R['tail'] = tail
    _tube(S, 'Coda', ((0, 0, 0), (0, 0.28, -0.06), (0, 0.45, 0.18), (0, 0.42, 0.44), (0, 0.28, 0.52), (0, 0.2, 0.44)), 0.038, 0.03, tail, b, 22)
    return R

# ---------------------------------------------------------------------------------------------------- pulcino
def pulcino(coll=None, scale=0.75):
    S, E, M, R, root, body = _start(coll, 'Pu_', 'pulcino', 0.36, scale)
    y_ = _mat('AN_Chick', (1.0, 0.84, 0.16), rough=0.85, spec=0.15); yd = _mat('AN_ChickD', (0.98, 0.68, 0.08), rough=0.85, spec=0.15)
    S('Corpo', 'sphere', (0, 0, 0), (0.3, 0.3, 0.3), body, y_)
    head = E('Head', (0, -0.1, 0.34), body); R['head'] = head
    S('Testa', 'sphere', (0, 0, 0), (0.23, 0.22, 0.22), head, y_); S('Becco', 'cone', (0, -0.2, -0.03), (0.06, 0.045, 0.12), head, M['orange'], rot=(PI / 2, 0, 0))
    for k, (dx, r) in enumerate(((0, 0), (-0.045, -0.35), (0.045, 0.35))): S('Piuma%d' % k, cap(0.02, 0.07), (dx, 0.01, 0.245), (1, 1, 1), head, yd, rot=(0, r, 0))
    _eyes(R, S, E, head, M, 0.09, -0.195, 0.04, 0.85)
    for s in (-1, 1):
        S('Ala%d' % s, 'sphere', (s * 0.29, 0.02, 0.0), (0.07, 0.16, 0.12), body, yd, rot=(0, -s * 0.3, 0))
        S('Zampa%d' % s, 'cyl:0.02:0.1', (s * 0.1, 0, -0.3), (1, 1, 1), body, M['orange']); S('Piede%d' % s, 'sphere', (s * 0.1, -0.06, -0.34), (0.08, 0.12, 0.025), body, M['orange'])
    S('Codino', 'cone', (0, 0.24, 0.08), (0.08, 0.05, 0.15), body, yd, rot=(-1.1, 0, 0))
    return R

# ---------------------------------------------------------------------------------------------------- granchio
def granchio(coll=None, scale=0.85):
    S, E, M, R, root, body = _start(coll, 'Gr_', 'granchio', 0.3, scale)
    r = _mat('AN_Crab', (0.93, 0.19, 0.11), rough=0.6, spec=0.3); rl = _mat('AN_CrabL', (1.0, 0.62, 0.46), rough=0.7)
    S('Corpo', 'sphere', (0, 0, 0), (0.4, 0.3, 0.2), body, r); S('Pancia', 'sphere', (0, -0.03, -0.07), (0.33, 0.26, 0.14), body, rl)
    R['head'] = body
    for s in (-1, 1): S('Stelo%d' % s, cap(0.028, 0.14), (s * 0.12, -0.2, 0.24), (1, 1, 1), body, r)
    _eyes(R, S, E, body, M, 0.12, -0.225, 0.38, 1.0)
    for s in (-1, 1):
        _tube(S, 'Braccio%d' % s, ((s * 0.34, -0.1, 0.0), (s * 0.5, -0.24, 0.08), (s * 0.58, -0.36, 0.2)), 0.065, 0.055, body, r, 9)
        claw = E('Claw%d' % s, (s * 0.62, -0.42, 0.28), body); claw.rotation_euler = (0, 0, s * 0.35); R['claw' + ('L' if s < 0 else 'R')] = claw
        S('Chela%d' % s, 'sphere', (0, -0.05, 0.05), (0.13, 0.2, 0.1), claw, r); S('ChelaSotto%d' % s, 'sphere', (0, -0.09, -0.08), (0.08, 0.15, 0.05), claw, r, rot=(0.35, 0, 0))
        for k, y in enumerate((-0.04, 0.1, 0.21)):
            _tube(S, 'Zampa%d%d' % (s, k), ((s * 0.32, y, -0.02), (s * 0.56, y + 0.02, 0.03), (s * 0.67, y + 0.03, -0.27)), 0.038, 0.025, body, r, 10)
    return R

# ---------------------------------------------------------------------------------------------------- fantasma e pupazzo di neve (non animali, stesso stile)
def fantasma(coll=None, scale=1.0):
    S, E, M, R, root, body = _start(coll, 'Fa_', 'fantasma', 0.98, scale)
    w = _mat('AN_Ghost', (0.95, 0.97, 1.0), rough=0.6, spec=0.3, emit=(0.75, 0.85, 1.0), emit_strength=0.35)
    S('Corpo', cap(0.42, 0.5), (0, 0, 0), (1, 1, 1), body, w)
    for i in range(7):
        a = i / 7 * 2 * PI; S('Orlo%d' % i, 'sphere', (0.31 * math.cos(a), 0.31 * math.sin(a), -0.5), (0.16, 0.16, 0.22), body, w)
    R['head'] = body; _eyes(R, S, E, body, M, 0.15, -0.385, 0.3, 1.5); S('Bocca', 'sphere', (0, -0.415, 0.03), (0.07, 0.03, 0.1), body, M['black'])
    for s in (-1, 1): S('Braccio%d' % s, 'sphere', (s * 0.47, -0.1, 0.06), (0.17, 0.1, 0.1), body, w, rot=(0, -s * 0.5, 0))
    return R

def pupazzo_neve(coll=None, scale=1.0):
    S, E, M, R, root, body = _start(coll, 'Pn_', 'pupazzo', 0.0, scale)
    sn = _mat('AN_Snow', (0.96, 0.98, 1.0), rough=0.7); red = _mat('AN_Scarf', (0.85, 0.08, 0.08), rough=0.8); tw = _mat('AN_Twig', (0.3, 0.18, 0.08), rough=0.8)
    S('Base', 'sphere', (0, 0, 0.46), (0.5, 0.5, 0.46), body, sn); S('Busto', 'sphere', (0, 0, 1.08), (0.36, 0.36, 0.34), body, sn)
    head = E('Head', (0, 0, 1.58), body); R['head'] = head
    S('Testa', 'sphere', (0, 0, 0), (0.27, 0.27, 0.26), head, sn); S('Naso', 'cone', (0, -0.25, 0.0), (0.05, 0.05, 0.28), head, M['orange'], rot=(PI / 2, 0, 0))
    for s in (-1, 1): S('Carbone%d' % s, 'sphere', (s * 0.1, -0.235, 0.075), (0.042, 0.03, 0.05), head, M['black']); S('Riflesso%d' % s, 'sphere_lo', (s * 0.1 - 0.012, -0.262, 0.092), (0.012, 0.008, 0.014), head, M['shine'])
    for i in range(5): S('Sorriso%d' % i, 'sphere', ((i - 2) * 0.048, -0.25 + 0.006 * (i - 2) ** 2, -0.12 + 0.016 * (i - 2) ** 2), (0.02, 0.014, 0.02), head, M['black'])
    S('Tesa', 'cyl:0.27:0.03', (0, 0, 0.215), (1, 1, 1), head, M['black']); S('Cilindro', 'cyl:0.175:0.28', (0, 0, 0.36), (1, 1, 1), head, M['black']); S('Nastro', 'cyl:0.18:0.06', (0, 0, 0.26), (1, 1, 1), head, red)
    S('Sciarpa', 'sphere', (0, 0, 1.37), (0.31, 0.31, 0.085), body, red); S('SciarpaCoda', 'sphere', (0.17, -0.27, 1.2), (0.07, 0.04, 0.21), body, red)
    for k, (y, z) in enumerate(((-0.345, 1.17), (-0.36, 1.03), (-0.475, 0.62), (-0.5, 0.45))): S('Bottone%d' % k, 'sphere', (0, y, z), (0.035, 0.025, 0.035), body, M['black'])
    for s in (-1, 1):
        arm = E('Arm%d' % s, (s * 0.33, 0, 1.15), body); arm.rotation_euler = (0, s * 1.05, 0); R['arm' + ('L' if s < 0 else 'R')] = arm
        S('Ramo%d' % s, cap(0.022, 0.5), (0, 0, 0.27), (1, 1, 1), arm, tw); S('Dito%da' % s, cap(0.016, 0.12), (0.05, 0, 0.52), (1, 1, 1), arm, tw, rot=(0, 0.6, 0)); S('Dito%db' % s, cap(0.016, 0.12), (-0.05, 0, 0.5), (1, 1, 1), arm, tw, rot=(0, -0.6, 0))
    return R

# ---------------------------------------------------------------------------------------------------- pellicano
def pellicano(coll=None, scale=1.0, tipo='A'):
    """Pellicano (copione n. 27A: ruba i pomodori dal cielo). tipo: 'A' bianco classico, 'B' ladro con la mascherina nera, 'C' rosa.
    Perni: head, jaw (la sacca del becco: rotation_euler.x > 0 la apre), wingL/R (rotation_euler.y le alza), legs. Fronte -Y."""
    S, E, M, R, root, body = _start(coll, 'Pe%s_' % tipo, 'pellicano', 0.62, scale)
    col = {'A': (0.97, 0.97, 0.95), 'B': (0.97, 0.97, 0.95), 'C': (1.0, 0.42, 0.60)}[tipo]
    wh = _mat('AN_Pel_' + tipo, col, rough=0.75); pun = _mat('AN_PelPunta', (0.10, 0.10, 0.13), rough=0.6)
    bec = _mat('AN_PelBecco', (1.0, 0.70, 0.12), rough=0.5); sac = _mat('AN_PelSacca', (1.0, 0.50, 0.22), rough=0.55)
    S('Corpo', 'sphere', (0, 0.05, 0), (0.36, 0.48, 0.36), body, wh); S('Petto', 'sphere', (0, -0.22, 0.05), (0.27, 0.26, 0.30), body, wh)
    S('Coda', 'cone', (0, 0.46, 0.02), (0.16, 0.05, 0.22), body, wh, rot=(-PI / 2 - 0.3, 0, 0))
    _tube(S, 'Collo', [(0, -0.30, 0.20), (0, -0.42, 0.50), (0, -0.30, 0.78), (0, -0.34, 0.98)], 0.14, 0.11, body, wh, n=12)
    head = E('Head', (0, -0.34, 1.04), body); R['head'] = head
    S('Testa', 'sphere', (0, 0, 0), (0.19, 0.21, 0.18), head, wh)
    for k, a in enumerate((-0.3, 0.0, 0.3)): S('Ciuffo%d' % k, 'cone', (0.0, 0.10 + 0.03 * k, 0.13), (0.035, 0.035, 0.16), head, wh, rot=(-0.7 - 0.2 * k, a, 0))
    S('BeccoSu', 'sphere', (0, -0.60, -0.015), (0.095, 0.50, 0.05), head, bec); S('Uncino', 'sphere', (0, -1.08, -0.045), (0.045, 0.06, 0.06), head, _mat('AN_PelUncino', (0.95, 0.35, 0.05), rough=0.5))
    jaw = E('Jaw', (0, -0.14, -0.05), head); R['jaw'] = jaw
    S('Sacca', 'sphere', (0, -0.38, -0.12), (0.115, 0.42, 0.19), jaw, sac); S('BeccoGiu', 'sphere', (0, -0.43, -0.015), (0.085, 0.44, 0.022), jaw, bec)
    _eyes(R, S, E, head, M, 0.105, -0.165, 0.06, 0.8)
    if tipo == 'B':
        S('Mascherina', 'sphere', (0, -0.11, 0.065), (0.2, 0.13, 0.065), head, M['black'])
    for s in (-1, 1):
        nm = 'L' if s < 0 else 'R'; w = E('Wing' + nm, (s * 0.33, 0.05, 0.16), body); w.rotation_euler = (0, -s * 0.25, 0); R['wing' + nm] = w
        S('Ala' + nm, 'sphere', (s * 0.02, 0.06, -0.26), (0.06, 0.34, 0.30), w, wh); S('Punta' + nm, 'sphere', (s * 0.03, 0.26, -0.44), (0.05, 0.22, 0.16), w, pun)
        g = E('Leg' + nm, (s * 0.15, 0.02, -0.30), body); R['legs'].append(g)
        S('Zampa' + nm, cap(0.035, 0.22), (0, 0, -0.13), (1, 1, 1), g, M['orange']); S('Piede' + nm, 'sphere', (0, -0.11, -0.30), (0.13, 0.19, 0.03), g, M['orange'])
    return R

ANIMALI = {'pellicano': pellicano, 'fantasma': fantasma, 'pupazzo_neve': pupazzo_neve, 'mucca': mucca, 'elefante': elefante, 'pinguino': pinguino, 'giraffa': giraffa, 'maiale': maiale, 'leone': leone, 'scimmia': scimmia, 'pulcino': pulcino, 'granchio': granchio}

def crea(nome, coll=None, scale=None):
    """crea l'animale per nome (vedi ANIMALI). scale=None usa la misura naturale accanto a Pippo."""
    return ANIMALI[nome](coll) if scale is None else ANIMALI[nome](coll, scale)
