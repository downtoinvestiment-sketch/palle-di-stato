"""Oggetti del video 024 «Martina, il cono stradale».
- mats024(): materiali.
- cono(coll, M, H=0.9, occhi=False, font=None, nome='Martina', testo='MARTINA', tag_angolo=None): cono stradale fatto a mano
  (arancione, due fasce bianche, base nera) con il cartellino del nome appeso al collo. Origine al suolo, fronte -Y.
  Restituisce dict: root, corpo, base, tag (radice del cartellino), occhi (radice o None).
- semaforo(coll, M, H=3.3, nome='Sem'): semaforo all'italiana su palo, luci verso -Y. Ogni lampada ha un materiale suo:
  accendi(S, 'giallo', frame=...) accende una luce e spegne le altre (con frame mette le chiavi).
- rullo(coll, M, nome='Rullo'): rullo compressore cartoon, alto circa 3 m, avanza verso -X. Origine al suolo.
- italia(coll, scala=0.01, tipo='giorno'|'notte', coni=30000): Italia in rilievo e paesi vicini dalla cartina
  Natural Earth (assets/mappe/italia50m.json); scala = metri di scena per km. tipo 'giorno': l'Italia coperta di coni;
  'notte': vista dallo spazio, l'Italia fatta di lampeggianti arancioni.
- tornio, scatola_tonda, anello, nuvola: mattoni (solido di rotazione, scatola con gli spigoli tondi, toro, nuvola di vertici)."""
import os, math, json, random, bisect, itertools
import bpy, bmesh
from mathutils import Vector, geometry
from common import material, empty, shape, shared_mesh
from set004 import obj, cyl, ball_, box_c
import props023

PI = math.pi
QUI = os.path.dirname(os.path.abspath(__file__))
MAPPA = os.path.join(QUI, '..', 'assets', 'mappe', 'italia50m.json')


def mats024():
    M = {}
    M['arancio'] = material('M24_arancio', (1.0, 0.2, 0.015), rough=0.32, spec=0.6, coat=0.35, coat_rough=0.15)
    M['bianco'] = material('M24_rifrangente', (0.93, 0.93, 0.93), rough=0.22, spec=0.8, emit=(1, 1, 1), emit_strength=0.06)
    M['nero'] = material('M24_gomma', (0.025, 0.025, 0.03), rough=0.85)
    M['carta'] = material('M24_carta', (0.97, 0.95, 0.88), rough=0.85)
    M['rosso'] = material('M24_rosso_testo', (0.8, 0.03, 0.03), rough=0.6)
    M['spago'] = material('M24_spago', (0.72, 0.55, 0.35), rough=0.95)
    M['occhio'] = material('M24_occhio', (1, 1, 1), rough=0.25)
    M['pupilla'] = material('M24_pupilla', (0.015, 0.015, 0.02), rough=0.15)
    M['giallo'] = material('M24_giallo', (1.0, 0.5, 0.0), rough=0.4, coat=0.3)
    M['ferro'] = material('M24_ferro', (0.42, 0.44, 0.47), rough=0.32, metallic=0.9)
    M['scuro'] = material('M24_scuro', (0.05, 0.055, 0.06), rough=0.5)
    M['zincato'] = material('M24_zincato', (0.62, 0.64, 0.66), rough=0.38, metallic=0.8)
    M['verde_sem'] = material('M24_verde_sem', (0.035, 0.09, 0.06), rough=0.45)
    return M


# ---------------------------------------------------------------- mattoni
def tornio(nome, prof, coll, mats, seg=48, mat_idx=None, parent=None, smooth=True, loc=(0, 0, 0)):
    """solido di rotazione attorno a Z: prof = [(r, z), ...] dal basso in alto, primo e ultimo con r = 0 (chiuso).
    mat_idx(zmezzo) -> indice del materiale di ogni fascia."""
    bm = bmesh.new(); rings = []
    for r, z in prof:
        if r < 1e-6: rings.append([bm.verts.new((0, 0, z))]); continue
        rings.append([bm.verts.new((r * math.cos(2 * PI * i / seg), r * math.sin(2 * PI * i / seg), z)) for i in range(seg)])
    for a, b in zip(rings[:-1], rings[1:]):
        if len(a) == 1 and len(b) == 1: continue
        mi = mat_idx((a[0].co.z + b[0].co.z) / 2) if mat_idx else 0
        for i in range(seg):
            j = (i + 1) % seg
            if len(a) == 1: vs = (a[0], b[j], b[i])
            elif len(b) == 1: vs = (a[i], a[j], b[0])
            else: vs = (a[i], a[j], b[j], b[i])
            f = bm.faces.new(vs); f.material_index = mi; f.smooth = smooth
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(nome); bm.to_mesh(me); bm.free()
    for m in mats: me.materials.append(m)
    o = bpy.data.objects.new(nome, me); coll.objects.link(o); o.parent = parent; o.location = loc
    return o


def scatola_tonda(nome, sx, sy, sz, r, mat, coll, parent=None, loc=(0, 0, 0), rot=(0, 0, 0)):
    """scatola centrata in loc, lati veri (sx, sy, sz) e spigoli arrotondati di raggio r."""
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts: v.co.x *= sx; v.co.y *= sy; v.co.z *= sz
    r = min(r, sx * 0.45, sy * 0.45, sz * 0.45)
    if r > 1e-4: bmesh.ops.bevel(bm, geom=list(bm.edges), offset=r, segments=3, affect='EDGES', profile=0.5)
    for f in bm.faces:
        n = f.normal; f.smooth = max(abs(n.x), abs(n.y), abs(n.z)) < 0.999
    me = bpy.data.meshes.new(nome); bm.to_mesh(me); bm.free(); me.materials.append(mat)
    o = bpy.data.objects.new(nome, me); coll.objects.link(o); o.parent = parent; o.location = loc; o.rotation_euler = rot
    return o


def anello(nome, R, r, mat, coll, parent=None, loc=(0, 0, 0), seg=40, segr=8):
    """toro orizzontale: raggio R, spessore r."""
    bm = bmesh.new(); vs = []
    for i in range(seg):
        a = 2 * PI * i / seg; c = Vector((math.cos(a), math.sin(a), 0))
        vs.append([bm.verts.new(c * (R + r * math.cos(2 * PI * j / segr)) + Vector((0, 0, r * math.sin(2 * PI * j / segr)))) for j in range(segr)])
    for i in range(seg):
        for j in range(segr):
            f = bm.faces.new((vs[i][j], vs[(i + 1) % seg][j], vs[(i + 1) % seg][(j + 1) % segr], vs[i][(j + 1) % segr])); f.smooth = True
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(nome); bm.to_mesh(me); bm.free(); me.materials.append(mat)
    o = bpy.data.objects.new(nome, me); coll.objects.link(o); o.parent = parent; o.location = loc
    return o


def nuvola(nome, pts, coll, parent=None):
    me = bpy.data.meshes.new(nome); me.from_pydata(pts, [], []); me.update()
    o = bpy.data.objects.new(nome, me); coll.objects.link(o); o.parent = parent
    return o


def istanze(nuv, figlio):
    """ripete 'figlio' su ogni vertice di 'nuv' (istanze leggere: un solo oggetto in memoria)."""
    nuv.instance_type = 'VERTS'; nuv.show_instancer_for_render = False; nuv.show_instancer_for_viewport = False
    figlio.parent = nuv; figlio.location = (0, 0, 0)


# ---------------------------------------------------------------- Martina
def _profilo_cono(H, k, fasce, n=16):
    z0, z1, r0, r1 = 0.045 * k, H - 0.022 * k, 0.165 * k, 0.026 * k
    rz = lambda z: r0 + (r1 - r0) * (z - z0) / (z1 - z0)
    zs = sorted(set([z0 + (z1 - z0) * i / n for i in range(n + 1)] + [a for f in fasce for a in f]))
    prof = [(0.0, z0), (r0 + 0.012 * k, z0), (r0 + 0.007 * k, z0 + 0.012 * k)]
    prof += [(rz(z), z) for z in zs if z > z0 + 0.02 * k]
    prof += [(r1 * 0.8, H - 0.008 * k), (0.0, H)]
    return prof, rz


def cono(coll, M, H=0.9, occhi=False, font=None, nome='Martina', testo='MARTINA', tag_angolo=None, seg=48):
    k = H / 0.9
    R = empty(nome, (0, 0, 0), None, coll)
    base = scatola_tonda(nome + 'Base', 0.42 * k, 0.42 * k, 0.045 * k, 0.025 * k, M['nero'], coll, parent=R, loc=(0, 0, 0.0225 * k))
    fasce = [(0.42 * k, 0.52 * k), (0.60 * k, 0.67 * k)]
    prof, rz = _profilo_cono(H, k, fasce)
    corpo = tornio(nome + 'Corpo', prof, coll, [M['arancio'], M['bianco']], seg=seg, parent=R,
                   mat_idx=lambda z: 1 if any(a < z < b for a, b in fasce) else 0)
    out = {'root': R, 'corpo': corpo, 'base': base, 'tag': None, 'occhi': None, 'rz': rz, 'H': H}
    if occhi:                                                          # occhi grandi tra le due fasce, con le ciglia
        ze = 0.29 * k; re_ = rz(ze); E = empty(nome + 'Occhi', (0, 0, 0), R, coll); out['occhi'] = E
        for sx in (-1, 1):
            th = sx * 0.42; d = Vector((math.sin(th), -math.cos(th), 0))
            c = d * (re_ + 0.004 * k) + Vector((0, 0, ze))
            o = ball_(nome + 'Occhio', 1.0, c, M['occhio'], coll, parent=E, sc=(0.046 * k, 0.02 * k, 0.056 * k)); o.rotation_euler = (0, 0, th)
            p = ball_(nome + 'Pupilla', 1.0, c + d * 0.017 * k + Vector((0, 0, -0.01 * k)), M['pupilla'], coll, parent=E, sc=(0.022 * k, 0.01 * k, 0.028 * k))
            p.rotation_euler = (0, 0, th)
            t = Vector((math.cos(th), math.sin(th), 0))
            for j in (-1, 0, 1):                                       # tre ciglia sopra ogni occhio, aperte a ventaglio verso l'esterno
                a = c + Vector((0, 0, 0.05 * k)) + t * (j * 0.022 * k + sx * 0.012 * k) + d * 0.004 * k
                b = a + Vector((0, 0, 0.03 * k)) + t * ((j + sx) * 0.011 * k) + d * 0.01 * k
                props023.tubo(nome + 'Ciglio', a, b, 0.0034 * k, M['pupilla'], coll, parent=E)
    if testo:
        th = 0.0 if tag_angolo is None else tag_angolo
        out['tag'] = cartellino(coll, M, R, rz, k, th, font, testo, nome)
    return out


def cartellino(coll, M, parent, rz, k, th, font, testo, nome='Martina', zl=None):
    """cartellino col nome appeso a un laccio attorno al collo di un cono; rz(z) = raggio del cono alla quota z; th = angolo dal davanti (-Y)."""
    zl = 0.71 * k if zl is None else zl; rl = rz(zl) + 0.003 * k
    T = empty(nome + 'Cartellino', (0, 0, 0), parent, coll)
    anello(nome + 'Laccio', rl, 0.0035 * k, M['spago'], coll, parent=T, loc=(0, 0, zl))
    d = Vector((math.sin(th), -math.cos(th), 0)); t = Vector((math.cos(th), math.sin(th), 0))
    p_l = d * rl + Vector((0, 0, zl))
    cc = d * (rl + 0.055 * k) + Vector((0, 0, zl - 0.15 * k))
    scatola_tonda(nome + 'Carta', 0.24 * k, 0.006 * k, 0.105 * k, 0.012 * k, M['carta'], coll, parent=T, loc=cc, rot=(0.0, 0.0, th))
    for s_ in (-1, 1): props023.tubo(nome + 'Spago', p_l, cc + t * (s_ * 0.085 * k) + Vector((0, 0, 0.045 * k)), 0.0025 * k, M['spago'], coll, parent=T)
    props023.testo(coll, nome + 'Nome', testo, 0.058 * k, M['rosso'], tuple(cc + d * 0.0042 * k + Vector((0, 0, -0.004 * k))),
                   rot=(PI / 2, 0, th), parent=T, font=font, estrudi=0.0012 * k)
    return T



def transenna(coll, M, nome='Transenna', L=1.6, H=1.0):
    """transenna da cantiere: asse a strisce bianche e rosse su due cavalletti. Origine al suolo, lunga lungo X, fronte -Y."""
    R = empty(nome, (0, 0, 0), None, coll)
    mrosso = material('M24_rosso_transenna', (0.85, 0.03, 0.02), rough=0.35, coat=0.2)
    n = 8; w = L / n
    for i in range(n):
        scatola_tonda(nome + 'Striscia', w + 0.002, 0.03, 0.2, 0.004, mrosso if i % 2 == 0 else M['bianco'], coll, R, (-L / 2 + w * (i + 0.5), 0, H - 0.1), rot=(0, 0, 0))
    for sx in (-1, 1):
        x = sx * (L / 2 - 0.12)
        for sy in (-1, 1): props023.tubo(nome + 'Gamba', (x, sy * 0.28, 0.0), (x, 0.03 * sy, H - 0.18), 0.022, M['zincato'], coll, parent=R)
    return R


# ---------------------------------------------------------------- semaforo
_COL_SEM = (('rosso', (1.0, 0.035, 0.015)), ('giallo', (1.0, 0.5, 0.0)), ('verde', (0.04, 1.0, 0.3)))


def semaforo(coll, M, H=3.3, nome='Sem', pannello=True):
    R = empty(nome, (0, 0, 0), None, coll)
    scatola_tonda(nome + 'Piede', 0.36, 0.36, 0.07, 0.02, M['scuro'], coll, R, (0, 0, 0.035))
    hp = H - 1.05
    cyl(nome + 'Palo', 0.055, hp, (0, 0, hp / 2 + 0.06), M['zincato'], coll, parent=R)
    zc = H - 0.52
    scatola_tonda(nome + 'Cassa', 0.33, 0.27, 1.02, 0.045, M['verde_sem'], coll, R, (0, 0.0, zc))
    if pannello:                                                       # pannello nero col bordo bianco, come in Italia
        scatola_tonda(nome + 'Bordo', 0.6, 0.02, 1.28, 0.03, M['bianco'], coll, R, (0, 0.15, zc))
        scatola_tonda(nome + 'Pannello', 0.54, 0.025, 1.22, 0.025, M['scuro'], coll, R, (0, 0.14, zc))
    lamp = {}
    for i, (nm, c) in enumerate(_COL_SEM):
        z = zc + 0.33 - i * 0.33
        mat = material('%s_lamp_%s' % (nome, nm), tuple(v * 0.05 for v in c), rough=0.15, spec=0.8, emit=c, emit_strength=0.0)
        lente = ball_(nome + 'Lente' + nm, 0.108, (0, -0.128, z), mat, coll, parent=R, sc=(1, 0.3, 1))
        scatola_tonda(nome + 'Visiera' + nm, 0.25, 0.17, 0.018, 0.008, M['verde_sem'], coll, R, (0, -0.215, z + 0.125), rot=(-0.18, 0, 0))
        for sx in (-1, 1): scatola_tonda(nome + 'VisLato' + nm, 0.016, 0.15, 0.14, 0.006, M['verde_sem'], coll, R, (sx * 0.118, -0.21, z + 0.06))
        L = bpy.data.lights.new(nome + 'Luce' + nm, 'POINT'); lo = bpy.data.objects.new(nome + 'Luce' + nm, L); coll.objects.link(lo)
        lo.parent = R; lo.location = (0, -0.42, z); L.color = c; L.energy = 0.0; L.shadow_soft_size = 0.15
        try: L.use_shadow = False
        except Exception: pass
        lamp[nm] = (lente, mat, c, lo)
    return {'root': R, 'lampade': lamp, 'testa_z': zc}


def accendi(S, colore, forza=14.0, luce=35.0, frame=None):
    """accende una lampada ('rosso', 'giallo', 'verde' o None per spegnere tutto); con frame mette le chiavi (costanti)."""
    for nm, (o, mat, c, lo) in S['lampade'].items():
        b = mat.node_tree.nodes['Principled BSDF']; on = nm == colore
        b.inputs['Emission Strength'].default_value = forza if on else 0.0
        b.inputs['Base Color'].default_value = (*(c if on else tuple(v * 0.05 for v in c)), 1)
        lo.data.energy = luce if on else 0.0
        if frame is not None:
            for s in ('Emission Strength', 'Base Color'): b.inputs[s].keyframe_insert('default_value', frame=frame)
            lo.data.keyframe_insert('energy', frame=frame)


# ---------------------------------------------------------------- rullo compressore
def rullo(coll, M, nome='Rullo'):
    R = empty(nome, (0, 0, 0), None, coll)
    mlamp = material(nome + '_lampeggiante', (1.0, 0.42, 0.02), rough=0.2, emit=(1.0, 0.38, 0.02), emit_strength=6.0)
    tam = cyl(nome + 'Tamburo', 0.7, 1.8, (-1.2, 0, 0.7), M['ferro'], coll, rot=(PI / 2, 0, 0), parent=R)
    for sy in (-0.92, 0.92): cyl(nome + 'Disco', 0.72, 0.06, (-1.2, sy, 0.7), M['giallo'], coll, rot=(PI / 2, 0, 0), parent=R)
    for sy in (-0.97, 0.97): cyl(nome + 'Mozzo', 0.2, 0.1, (-1.2, sy, 0.7), M['scuro'], coll, rot=(PI / 2, 0, 0), parent=R)
    scatola_tonda(nome + 'Ponte', 0.55, 2.1, 0.2, 0.06, M['giallo'], coll, R, (-1.2, 0, 1.52))
    for sy in (-1.02, 1.02): scatola_tonda(nome + 'Braccio', 0.26, 0.1, 0.9, 0.04, M['giallo'], coll, R, (-1.2, sy, 1.08))
    scatola_tonda(nome + 'Collo', 0.7, 0.7, 0.45, 0.08, M['giallo'], coll, R, (-0.72, 0, 1.38))
    scatola_tonda(nome + 'Corpo', 1.9, 1.55, 1.05, 0.2, M['giallo'], coll, R, (0.55, 0, 1.08))
    for i in range(5):                                                 # griglia del motore, dietro
        scatola_tonda(nome + 'Griglia', 0.03, 1.1, 0.07, 0.01, M['scuro'], coll, R, (1.51, 0, 0.82 + i * 0.13))
    for sy in (-1, 1):                                                 # strisce gialle e nere ai lati
        for i in range(6):
            scatola_tonda(nome + 'Zebra', 0.14, 0.012, 0.32, 0.01, M['scuro'], coll, R, (-0.15 + i * 0.3, sy * 0.78, 0.85), rot=(0, 0.6, 0))
    for sy in (-0.74, 0.74):
        cyl(nome + 'Ruota', 0.58, 0.5, (1.02, sy * 1.0, 0.58), M['nero'], coll, rot=(PI / 2, 0, 0), parent=R)
        cyl(nome + 'Cerchio', 0.3, 0.52, (1.02, sy * 1.0, 0.58), M['giallo'], coll, rot=(PI / 2, 0, 0), parent=R)
    scatola_tonda(nome + 'Sedile', 0.5, 0.62, 0.12, 0.04, M['scuro'], coll, R, (0.55, 0, 1.68))
    scatola_tonda(nome + 'Schienale', 0.12, 0.62, 0.55, 0.04, M['scuro'], coll, R, (0.82, 0, 1.98))
    cyl(nome + 'Piantone', 0.035, 0.55, (0.05, 0, 1.85), M['scuro'], coll, rot=(0, -0.5, 0), parent=R)
    anello(nome + 'Volante', 0.17, 0.022, M['scuro'], coll, parent=R, loc=(-0.08, 0, 2.1)).rotation_euler = (0, -0.5, 0)
    for sx, sy in ((-0.2, -0.72), (-0.2, 0.72), (1.3, -0.72), (1.3, 0.72)): cyl(nome + 'Montante', 0.04, 1.25, (sx, sy, 2.2), M['scuro'], coll, parent=R)
    scatola_tonda(nome + 'Tetto', 1.75, 1.65, 0.09, 0.035, M['giallo'], coll, R, (0.55, 0, 2.86))
    ball_(nome + 'Lampeggiante', 0.12, (0.55, 0, 3.0), mlamp, coll, parent=R, sc=(1, 1, 1.25))
    cyl(nome + 'Scarico', 0.06, 0.95, (1.3, 0.52, 1.95), M['scuro'], coll, parent=R)
    return {'root': R, 'tamburo': tam, 'lampeggiante': mlamp}


# ---------------------------------------------------------------- l'Italia
def _anelli(P, scala):
    out = []
    for r in P:
        pts = []
        for x, y in r:
            p = (x * scala, y * scala)
            if not pts or abs(p[0] - pts[-1][0]) > 1e-7 or abs(p[1] - pts[-1][1]) > 1e-7: pts.append(p)
        if len(pts) > 1 and abs(pts[0][0] - pts[-1][0]) < 1e-7 and abs(pts[0][1] - pts[-1][1]) < 1e-7: pts.pop()
        if len(pts) >= 3: out.append(pts)
    return out


def estrudi(nome, anelli, z0, z1, mat_top, mat_lato, coll, parent=None):
    """poligono con buchi (anelli 2D) estruso da z0 a z1. Restituisce (oggetto, triangoli, punti)."""
    loops = [[Vector((x, y, 0.0)) for x, y in L] for L in anelli]
    tris = geometry.tessellate_polygon(loops)
    flat = [v for L in loops for v in L]
    bm = bmesh.new()
    T = [bm.verts.new((v.x, v.y, z1)) for v in flat]; B = [bm.verts.new((v.x, v.y, z0)) for v in flat]
    for t in tris:
        try:
            f = bm.faces.new([T[i] for i in t]); f.material_index = 0
            g = bm.faces.new([B[i] for i in reversed(t)]); g.material_index = 1
        except ValueError: pass
    off = 0
    for L in loops:
        n = len(L)
        for i in range(n):
            a, b = off + i, off + (i + 1) % n
            try: f = bm.faces.new((B[a], B[b], T[b], T[a])); f.material_index = 1
            except ValueError: pass
        off += n
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    up = sum(f.normal.z * f.calc_area() for f in bm.faces if f.material_index == 0)
    if up < 0: bmesh.ops.reverse_faces(bm, faces=bm.faces)
    me = bpy.data.meshes.new(nome); bm.to_mesh(me); bm.free()
    me.materials.append(mat_top); me.materials.append(mat_lato)
    o = bpy.data.objects.new(nome, me); coll.objects.link(o); o.parent = parent
    return o, tris, flat


def punti_su(tris, flat, n, z, rnd):
    """n punti a caso sui triangoli (in proporzione all'area), alla quota z."""
    if not tris: return []
    ar = []
    for t in tris:
        a, b, c = (flat[i] for i in t); ar.append(abs((b.x - a.x) * (c.y - a.y) - (c.x - a.x) * (b.y - a.y)) / 2)
    cum = list(itertools.accumulate(ar)); tot = cum[-1]; pts = []
    for _ in range(n):
        i = min(bisect.bisect_left(cum, rnd.random() * tot), len(tris) - 1)
        a, b, c = (flat[j] for j in tris[i]); r1, r2 = rnd.random(), rnd.random()
        if r1 + r2 > 1: r1, r2 = 1 - r1, 1 - r2
        p = a + (b - a) * r1 + (c - a) * r2; pts.append((p.x, p.y, z))
    return pts


_ICO = {}
def _ico():
    """icosfera leggera (80 facce) condivisa, per le lucine."""
    if 'm' in _ICO and _ICO['m'].name in bpy.data.meshes: return _ICO['m']
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=1.0)
    me = bpy.data.meshes.new('unit_ico1'); bm.to_mesh(me); bm.free(); me.materials.append(None); _ICO['m'] = me; return me


def italia(coll, scala=0.01, tipo='giorno', coni=30000, seme=3, nome='Italia', vista=(2200.0, 2000.0)):
    """Italia e vicini; l'Italia (id 380) e' piu' alta dei vicini. Restituisce dict: root, italia (lista di oggetti), vicini, mare,
    punti (nuvole di istanze), h (altezza dell'Italia)."""
    D = json.load(open(MAPPA)); rnd = random.Random(seme)
    R = empty(nome, (0, 0, 0), None, coll)
    notte = tipo == 'notte'
    if notte:
        m_mare = material('M24_mare_notte', (0.004, 0.012, 0.035), rough=0.3, spec=0.7)
        m_terra = material('M24_terra_notte', (0.05, 0.055, 0.05), rough=0.9)
        m_ita = material('M24_italia_notte', (0.09, 0.04, 0.02), rough=0.9)
        m_lato = m_terra
    else:
        m_mare = material('M24_mare', (0.05, 0.25, 0.45), rough=0.18, spec=0.6)
        m_terra = material('M24_terra', (0.33, 0.42, 0.25), rough=0.9)
        m_ita = material('M24_italia', (0.9, 0.16, 0.0), rough=0.6)
        m_lato = material('M24_lato', (0.42, 0.33, 0.22), rough=0.9)
    W = 9000 * scala
    mare = obj(nome + 'Mare', box_c(), (0, 0, -0.01 * scala * 100), (W, W, 0.02 * scala * 100), m_mare, coll, parent=R)
    h_v, h_i = 2.5 * scala, 9.0 * scala                                # metri di scena: i vicini bassi, l'Italia piu' alta (plastico)
    ita, vic, tri_i, tri_v = [], [], [], []
    for cid, c in D.items():
        for P in c['poligoni']:
            if not any(abs(x) < vista[0] and abs(y) < vista[1] for x, y in P[0]): continue
            an = _anelli(P, scala)
            if not an: continue
            if cid == '380':
                o, tr, fl = estrudi(nome + 'Terra', an, 0.0, h_i, m_ita, m_lato, coll, R); ita.append(o); tri_i.append((tr, fl))
            else:
                o, tr, fl = estrudi(nome + 'Vicino', an, 0.0, h_v, m_terra, m_lato, coll, R); vic.append(o); tri_v.append((tr, fl))
    nuv = []
    if notte:                                                          # lampeggianti arancioni (Italia) e qualche luce di citta' (vicini)
        def punti(gruppi, n, z):
            ar = [sum(abs((fl[t[1]].x - fl[t[0]].x) * (fl[t[2]].y - fl[t[0]].y) - (fl[t[2]].x - fl[t[0]].x) * (fl[t[1]].y - fl[t[0]].y)) / 2 for t in tr) for tr, fl in gruppi]
            tot = sum(ar) or 1; out = []
            for (tr, fl), a in zip(gruppi, ar): out += punti_su(tr, fl, int(n * a / tot), z, rnd)
            return out
        for nm, gr, n, col, forza, r, z in (('Arancio', tri_i, int(coni * 0.8), (1.0, 0.28, 0.0), 4.5, 2.2, h_i),
                                             ('Giallo', tri_i, int(coni * 0.2), (1.0, 0.7, 0.05), 9.0, 2.8, h_i),
                                             ('Citta', tri_v, int(coni * 0.25), (1.0, 0.86, 0.62), 2.5, 1.8, h_v)):
            pts = punti(gr, n, z + 0.3 * scala)
            if not pts: continue
            N = nuvola(nome + 'Punti' + nm, pts, coll, R)
            pal = obj(nome + 'Luce' + nm, _ico(), (0, 0, 0), (r * scala,) * 3,
                      material('M24_luce_' + nm, col, emit=col, emit_strength=forza), coll)
            istanze(N, pal); nuv.append(N)
    else:                                                              # un tappeto di coni minuscoli (stessi colori di Martina)
        kk = 10.0 * scala; Hm = 0.9 * kk; r0 = 0.165 * kk; r1 = 0.03 * kk
        rzm = lambda z: r0 + (r1 - r0) * z / Hm
        fa, fb = 0.45 * Hm, 0.58 * Hm
        prof = [(0.0, 0.0), (r0, 0.0), (rzm(fa), fa), (rzm(fb), fb), (r1, Hm), (0.0, Hm)]
        mc = tornio(nome + 'ConoMini', prof, coll, [material('M24_cono_mini', (1.0, 0.13, 0.0), rough=0.45), material('M24_fascia_mini', (0.95, 0.95, 0.95), rough=0.4)],
                    seg=8, mat_idx=lambda z: 1 if fa < z < fb else 0)
        ar = [sum(abs((fl[t[1]].x - fl[t[0]].x) * (fl[t[2]].y - fl[t[0]].y) - (fl[t[2]].x - fl[t[0]].x) * (fl[t[1]].y - fl[t[0]].y)) / 2 for t in tr) for tr, fl in tri_i]
        tot = sum(ar) or 1; pts = []
        for (tr, fl), a in zip(tri_i, ar): pts += punti_su(tr, fl, int(coni * a / tot), h_i, rnd)
        N = nuvola(nome + 'PuntiConi', pts, coll, R); istanze(N, mc); nuv.append(N)
    return {'root': R, 'italia': ita, 'vicini': vic, 'mare': mare, 'punti': nuv, 'h': h_i}
