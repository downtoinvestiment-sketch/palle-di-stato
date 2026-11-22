"""Oggetti del video 029 «La guerra per il petrolio» (copione n. 29C v5).
T-rex (tre tipi), pozzo di petrolio (P1 pompa a cavallo, P2 torre di trivellazione), distributore (D1 anni '50, D2 moderno con pensilina),
cannone, collare e guinzaglio di Rospina, cannuccia gigante, deserto con le dune (posto generico: niente bandiere, leader o luoghi veri).
    import props029 as P9
    M = P9.mats029()
    R = P9.trex(coll, M, 'T1')          # root, body, neck, head, jaw, armL/R, legL/R, tail[...], eyes, berretto (cappello da benzinaio, nascosto)
    W = P9.pompa(coll, M)               # root, beam (rotation x), crank (rotation x)
    W = P9.torre(coll, M)               # root, trivella (si abbassa in z)
    D = P9.distributore(coll, M, 'D1')  # root, display (testo del prezzo)
Fronte sempre verso -Y, base a z = 0."""
import math, os, bpy, bmesh
from mathutils import Vector
from common import material, shape, empty
import set004
QUI = os.path.dirname(os.path.abspath(__file__))
PI = math.pi


def font(nome='Poppins-Black'):
    return bpy.data.fonts.load(os.path.join(QUI, '..', 'assets', 'font', nome + '.ttf'), check_existing=True)


def mats029():
    m = lambda n, c, **k: material('P29_' + n, c, **k)
    return dict(
        T1=m('t1', (0.24, 0.58, 0.18), rough=0.55), T1p=m('t1p', (0.93, 0.86, 0.52), rough=0.6), T1s=m('t1s', (0.12, 0.38, 0.10), rough=0.55),
        T2=m('t2', (0.30, 0.25, 0.16), rough=0.7), T2p=m('t2p', (0.68, 0.58, 0.42), rough=0.75), T2s=m('t2s', (0.16, 0.13, 0.08), rough=0.7),
        T3=m('t3', (0.42, 0.18, 0.62), rough=0.5), T3p=m('t3p', (1.0, 0.62, 0.20), rough=0.55), T3s=m('t3s', (1.0, 0.45, 0.08), rough=0.5),
        bianco=m('bianco', (0.97, 0.97, 0.96), rough=0.3), nero=m('nero', (0.02, 0.02, 0.02), rough=0.15), dente=m('dente', (0.98, 0.95, 0.85), rough=0.35),
        bocca=m('bocca', (0.35, 0.04, 0.06), rough=0.5), lingua=m('lingua', (0.92, 0.35, 0.42), rough=0.45), unghia=m('unghia', (0.25, 0.22, 0.2), rough=0.4),
        giallo=m('giallo', (1.0, 0.72, 0.05), rough=0.4), giallo_s=m('giallo_s', (0.85, 0.55, 0.02), rough=0.45), ferro=m('ferro', (0.18, 0.19, 0.21), rough=0.35, metallic=0.7),
        rosso=m('rosso', (0.82, 0.06, 0.05), rough=0.35), rosso_s=m('rosso_s', (0.55, 0.03, 0.03), rough=0.4), cromo=m('cromo', (0.85, 0.86, 0.9), rough=0.12, metallic=1.0),
        petrolio=m('petrolio', (0.01, 0.01, 0.012), rough=0.18, spec=0.8, coat=0.6), vetro=m('globo', (1.0, 0.98, 0.92), rough=0.2, emit=(1.0, 0.95, 0.8), emit_strength=1.2),
        verde=m('verde', (0.05, 0.55, 0.30), rough=0.4), bianco_l=m('bianco_l', (1, 1, 1), rough=0.5, emit=(1, 1, 1), emit_strength=0.6),
        display=m('display', (0.02, 0.03, 0.02), rough=0.3), cifre=m('cifre', (1.0, 0.25, 0.1), rough=0.4, emit=(1.0, 0.3, 0.05), emit_strength=4.0),
        cifre_v=m('cifre_v', (0.3, 1.0, 0.4), rough=0.4, emit=(0.2, 1.0, 0.35), emit_strength=4.0), legno=m('legno', (0.45, 0.28, 0.12), rough=0.7),
        collare=m('collare', (0.85, 0.05, 0.1), rough=0.35), borchia=m('borchia', (1.0, 0.75, 0.2), rough=0.25, metallic=0.9), corda=m('corda', (0.85, 0.05, 0.1), rough=0.5),
        cannuccia=m('cannuccia', (1.0, 1.0, 1.0), rough=0.3), cannuccia_r=m('cannuccia_r', (0.95, 0.15, 0.25), rough=0.3),
        tappetino=m('tappetino', (0.55, 0.25, 0.85), rough=0.6), tappetino2=m('tappetino2', (0.1, 0.75, 0.65), rough=0.6),
    )


def _txt(coll, nome, body, size, mat, loc, rot=(PI / 2, 0, 0), parent=None, ext=0.02, fnt=None):
    cu = bpy.data.curves.new(nome, 'FONT'); cu.body = body; cu.size = size; cu.align_x = 'CENTER'; cu.align_y = 'CENTER'; cu.extrude = ext; cu.font = fnt or font()
    o = bpy.data.objects.new(nome, cu); o.location = loc; o.rotation_euler = rot; o.parent = parent; coll.objects.link(o); cu.materials.append(mat); return o


def box(nome, centro, dim, mat, coll, parent=None, rot=(0, 0, 0)):
    o = set004.obj(nome, set004.box_c(), centro, dim, mat, coll, parent=parent); o.rotation_euler = rot; return o


# ======================= T-REX =======================
def trex(coll, M, tipo='T1'):
    """T-rex da cartone, alto circa 8,5 m (testa a 7 m). tipo T1 verde, T2 marrone, T3 viola con le punte arancioni."""
    pel, pan, scu = M[tipo], M[tipo + 'p'], M[tipo + 's']
    S = lambda n, k, loc, sc=(1, 1, 1), par=None, mat=None, rot=(0, 0, 0): shape('TR_' + n, k, loc, sc, rot, par, mat, coll)
    E = lambda n, loc, par: empty('TR_' + n, loc, par, coll)
    R = {'tipo': tipo}
    root = R['root'] = E('Root', (0, 0, 0), None); root.rotation_mode = 'XYZ'
    body = R['body'] = E('Body', (0, 0.4, 4.3), root); body.rotation_mode = 'XYZ'
    S('Corpo', 'sphere', (0, 0.3, 0.2), (1.55, 2.5, 1.65), body, pel, rot=(-0.35, 0, 0))
    S('Pancia', 'sphere', (0, -0.55, -0.15), (1.25, 1.7, 1.3), body, pan, rot=(-0.45, 0, 0))
    neck = R['neck'] = E('Neck', (0, -1.6, 1.25), body); neck.rotation_mode = 'XYZ'
    S('Collo', 'sphere', (0, -0.1, 0.3), (0.95, 1.2, 1.25), neck, pel, rot=(-0.6, 0, 0))
    S('Gola', 'sphere', (0, -0.45, 0.05), (0.7, 0.75, 0.9), neck, pan, rot=(-0.5, 0, 0))
    head = R['head'] = E('Head', (0, -0.5, 1.2), neck); head.rotation_mode = 'XYZ'
    S('Cranio', 'sphere', (0, -0.75, 0.25), (1.05, 1.55, 0.85), head, pel)
    S('Muso', 'sphere', (0, -1.75, 0.05), (0.85, 0.95, 0.6), head, pel)
    S('Labbro', 'sphere', (0, -1.55, -0.28), (0.95, 1.45, 0.25), head, pan)
    for s_ in (-1, 1):
        S('Narice', 'sphere', (s_ * 0.28, -2.55, 0.3), (0.09, 0.06, 0.06), head, M['nero'])
        ey = E('Occhio' + ('L' if s_ < 0 else 'R'), (s_ * 0.62, -1.0, 0.78), head); R['eye' + ('L' if s_ < 0 else 'R')] = ey
        S('Bianco', 'sphere', (0, 0, 0), (0.36, 0.34, 0.4), ey, M['bianco'])
        R['pupil' + ('L' if s_ < 0 else 'R')] = S('Pupilla', 'sphere', (s_ * 0.06, -0.24, 0.0), (0.17, 0.14, 0.2), ey, M['nero'])
        S('Luce', 'sphere_lo', (s_ * 0.02, -0.34, 0.1), (0.05, 0.03, 0.06), ey, M['bianco'])
        R['lid' + ('L' if s_ < 0 else 'R')] = S('Palpebra', 'sphere', (0, -0.01, 0.42), (0.38, 0.36, 0.001), ey, pel)
        b = E('Sopr' + ('L' if s_ < 0 else 'R'), (s_ * 0.62, -1.15, 1.15), head); b.rotation_mode = 'XYZ'; R['brow' + ('L' if s_ < 0 else 'R')] = b
        S('Arcata', 'sphere', (0, 0, 0), (0.42, 0.18, 0.12), b, scu)
        for j in range(6):                                                    # denti di sopra (corti, da cartone)
            y = -2.45 + j * 0.3
            S('Dente', 'cone', (s_ * (0.55 + 0.07 * j), y, -0.33), (0.08, 0.08, 0.17), head, M['dente'], rot=(PI, 0, 0))
    jaw = R['jaw'] = E('Jaw', (0, 0.05, -0.2), head); jaw.rotation_mode = 'XYZ'
    S('Mascella', 'sphere', (0, -1.25, -0.25), (0.85, 1.45, 0.32), jaw, pel)
    S('MascellaSotto', 'sphere', (0, -1.15, -0.32), (0.7, 1.2, 0.22), jaw, pan)
    S('Bocca', 'sphere', (0, -1.2, -0.1), (0.72, 1.3, 0.12), jaw, M['bocca'])
    S('Lingua', 'sphere', (0, -1.1, -0.04), (0.45, 0.9, 0.1), jaw, M['lingua'])
    for s_ in (-1, 1):
        for j in range(5):
            S('DenteSotto', 'cone', (s_ * (0.5 + 0.06 * j), -2.25 + j * 0.3, -0.05), (0.07, 0.07, 0.14), jaw, M['dente'])
    # braccine ridicole
    for s_, nm in ((-1, 'L'), (1, 'R')):
        a = R['arm' + nm] = E('Arm' + nm, (s_ * 0.95, -1.75, 0.15), body); a.rotation_mode = 'XYZ'
        S('Braccino', 'cap:0.16:0.45', (0, -0.15, -0.3), par=a, mat=pel, rot=(0.6, 0, 0))
        for d in (-1, 1): S('Artiglio', 'cone', (d * 0.07, -0.42, -0.62), (0.05, 0.05, 0.13), a, M['unghia'], rot=(PI - 0.5, 0, 0))
    # gambe
    for s_, nm in ((-1, 'L'), (1, 'R')):
        g = R['leg' + nm] = E('Leg' + nm, (s_ * 1.05, 0.55, 4.1), root); g.rotation_mode = 'XYZ'
        S('Coscia', 'sphere', (s_ * 0.12, 0.1, -0.75), (0.85, 1.15, 1.35), g, pel)
        S('Stinco', 'sphere', (s_ * 0.12, 0.45, -2.4), (0.45, 0.5, 1.15), g, pel, rot=(-0.25, 0, 0))
        S('Piede', 'sphere', (s_ * 0.12, -0.25, -3.85), (0.6, 1.05, 0.28), g, pel)
        for d in (-1, 0, 1): S('Unghia', 'cone', (s_ * 0.12 + d * 0.32, -1.2, -3.9), (0.09, 0.14, 0.12), g, M['unghia'], rot=(PI / 2, 0, 0))
    # coda: catena di perni che dondola
    R['tail'] = []; par = body; prev = Vector((0, 2.2, 0.0))
    for k in range(8):
        e = E('Coda%d' % k, tuple(prev) if k == 0 else (0, 0.85, -0.12), par); e.rotation_mode = 'XYZ'; R['tail'].append(e)
        r = 1.05 * (1 - k / 9.0) + 0.12
        S('CodaPezzo', 'sphere', (0, 0.45, 0), (r, 0.75, r * 0.95), e, pel)
        if tipo == 'T3' and k < 6: S('Punta', 'cone', (0, 0.45, r * 0.9), (0.18 * r + 0.06, 0.25, 0.3 * r + 0.12), e, scu)
        par = e
    if tipo in ('T2', 'T3'):                                                 # strisce sulla schiena (T2) o punte (T3)
        for k in range(6):
            y = 1.6 - k * 0.55; z = 1.65 + 0.12 * k
            if tipo == 'T3': S('PuntaSchiena', 'cone', (0, y, z), (0.18, 0.3, 0.38), body, scu)
            else: S('Striscia', 'sphere', (0, y, z - 0.08), (0.9 - 0.05 * k, 0.12, 0.18), body, scu, rot=(-0.35, 0, 0))
        for k in range(3): S('PuntaTesta' if tipo == 'T3' else 'StrisciaTesta', 'cone' if tipo == 'T3' else 'sphere', (0, -0.3 - 0.45 * k, 1.05), (0.14, 0.2, 0.28) if tipo == 'T3' else (0.5, 0.1, 0.06), head, scu)
    # cappello da benzinaio (nascosto: si accende con berretto(R, f, True))
    cap = R['berretto'] = E('Berretto', (0, -0.8, 1.0), head)
    S('Calotta', 'sphere', (0, 0, 0.05), (0.85, 0.95, 0.42), cap, M['rosso']); S('Visiera', 'sphere', (0, -0.95, -0.1), (0.75, 0.55, 0.06), cap, M['rosso_s'])
    _txt(coll, 'TR_Logo', 'BENZINA', 0.22, M['bianco'], (0, -0.86, 0.2), rot=(PI / 2 - 0.35, 0, 0), parent=cap, ext=0.02)
    cap.scale = (0.001,) * 3
    return R


def berretto(R, f, on):
    R['berretto'].scale = (1, 1, 1) if on else (0.001,) * 3; R['berretto'].keyframe_insert('scale', frame=f)


def trex_pose(R, f, jaw=0.15, testa=(0.0, 0.0, 0.0), collo=0.0, corpo=(0.0, 0.0), coda=0.0, braccia=0.0, gambe=(0.0, 0.0), look=(0.0, 0.0), brow=0.0, lid=0.0):
    """Posa del T-rex al fotogramma f. jaw 0 chiusa .. 1 spalancata; testa (rot x, y, z); collo rot x; corpo (rot x, z);
    coda = fase dell'ondeggio (radianti) ; braccia 0..1 agitate; gambe (rot x sinistra, destra); look (x, z) pupille; brow > 0 arrabbiato."""
    def K(o, p):
        if f is not None: o.keyframe_insert(p, frame=f)
    R['jaw'].rotation_euler = (0.65 * jaw, 0, 0); K(R['jaw'], 'rotation_euler')
    R['head'].rotation_euler = testa; K(R['head'], 'rotation_euler')
    R['neck'].rotation_euler = (collo, 0, 0); K(R['neck'], 'rotation_euler')
    R['body'].rotation_euler = (corpo[0], 0, corpo[1]); K(R['body'], 'rotation_euler')
    for k, e in enumerate(R['tail']):
        e.rotation_euler = (0.04 * math.sin(coda + k * 0.5), 0, 0.12 * math.sin(coda + k * 0.6)); K(e, 'rotation_euler')
    for s_, nm in ((-1, 'L'), (1, 'R')):
        a = R['arm' + nm]; a.rotation_euler = (-0.8 * braccia * (1 + 0.3 * s_), 0, 0); K(a, 'rotation_euler')
        p = R['pupil' + nm]; p.location = (s_ * 0.06 + look[0] * 0.1, -0.24, look[1] * 0.1); K(p, 'location')
        l = R['lid' + nm]; l.scale = (0.38, 0.36, 0.001 + 0.43 * lid); l.location = (0, -0.01, 0.42 - 0.4 * lid); K(l, 'scale'); K(l, 'location')
        b = R['brow' + nm]; b.rotation_euler = (0, s_ * 0.45 * brow, 0); b.location = (s_ * 0.62, -1.15, 1.15 - 0.08 * max(0, brow) + 0.1 * max(0, -brow)); K(b, 'rotation_euler'); K(b, 'location')
    R['legL'].rotation_euler = (gambe[0], 0, 0); R['legR'].rotation_euler = (gambe[1], 0, 0); K(R['legL'], 'rotation_euler'); K(R['legR'], 'rotation_euler')


# ======================= POZZI =======================
def pompa(coll, M, colore='giallo'):
    """P1: pompa a cavallo (alta circa 6,5 m). R['beam'] oscilla attorno a x, R['crank'] gira attorno a x."""
    g, gs, fe = M[colore], M[colore + '_s'] if colore + '_s' in M else M['giallo_s'], M['ferro']
    R = {}; root = R['root'] = empty('PO_Root', (0, 0, 0), None, coll); root.rotation_mode = 'XYZ'
    box('PO_Base', (0, 0, 0.15), (1.6, 7.5, 0.3), fe, coll, root)
    for s_ in (-1, 1):                                                       # cavalletto ad A
        box('PO_Gamba', (s_ * 0.55, 0.0, 2.6), (0.22, 0.22, 5.2), g, coll, root, rot=(0, -s_ * 0.2, 0))
        box('PO_GambaDietro', (0, 0.9, 2.5), (0.2, 0.2, 5.1), g, coll, root, rot=(0.33, 0, 0))
    beam = R['beam'] = empty('PO_Bilanciere', (0, 0, 5.25), root, coll); beam.rotation_mode = 'XYZ'
    box('PO_Trave', (0, 0, 0.0), (0.42, 6.4, 0.55), g, coll, beam)
    hh = empty('PO_TestaCavallo', (0, -3.3, -0.2), beam, coll)
    bm = bmesh.new()                                                         # testa di cavallo: profilo ad arco (davanti curvo) estruso in larghezza
    c_, R_, w = 1.15, 1.5, 0.5; prof = []
    for k in range(13):
        a = -1.0 + 2.0 * k / 12; prof.append((c_ - R_ * math.cos(a), R_ * math.sin(a)))
    prof += [(0.75, R_ * math.sin(1.0)), (0.75, -R_ * math.sin(1.0))]
    f_ = bm.faces.new([bm.verts.new((-w / 2, y, z)) for (y, z) in prof])
    ex = bmesh.ops.extrude_face_region(bm, geom=[f_]); bmesh.ops.translate(bm, vec=(w, 0, 0), verts=[v for v in ex['geom'] if isinstance(v, bmesh.types.BMVert)])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new('PO_Testa'); bm.to_mesh(me); bm.free(); o = bpy.data.objects.new('PO_Testa', me); coll.objects.link(o); o.parent = hh; me.materials.append(g)
    crank = R['crank'] = empty('PO_Manovella', (0, 2.7, 1.25), root, coll); crank.rotation_mode = 'XYZ'
    for s_ in (-1, 1):
        box('PO_Braccio', (s_ * 0.45, 0, 0), (0.12, 2.4, 0.5), fe, coll, crank)
        box('PO_Contrappeso', (s_ * 0.45, 1.0, 0), (0.25, 1.1, 1.4), M['rosso'], coll, crank)
    box('PO_Riduttore', (0, 2.7, 0.75), (1.0, 1.0, 1.0), fe, coll, root)
    box('PO_Biella', (0, 2.9, 3.2), (0.12, 0.12, 4.0), fe, coll, root)
    shape('PO_Testapozzo', 'cyl:1:1', (0, -3.6, 0.6), (0.22, 0.22, 1.2), (0, 0, 0), root, fe, coll)
    shape('PO_Asta', 'cyl:1:1', (0, -3.6, 2.3), (0.04, 0.04, 2.4), (0, 0, 0), root, M['cromo'], coll)
    return R


def torre(coll, M):
    """P2: torre di trivellazione a traliccio (alta 15 m). R['trivella'] scende in z durante la trivellazione."""
    fe, g, ro = M['ferro'], M['giallo'], M['rosso']
    R = {}; root = R['root'] = empty('TO_Root', (0, 0, 0), None, coll); root.rotation_mode = 'XYZ'
    box('TO_Piattaforma', (0, 0, 1.6), (6.0, 6.0, 0.4), fe, coll, root)
    for (sx, sy) in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        box('TO_Pilastro', (sx * 2.6, sy * 2.6, 0.8), (0.3, 0.3, 1.6), fe, coll, root)
    H = 15.0; b0, b1 = 2.3, 0.6
    for (sx, sy) in ((-1, -1), (1, -1), (1, 1), (-1, 1)):                    # quattro gambe inclinate
        p0 = Vector((sx * b0, sy * b0, 1.8)); p1 = Vector((sx * b1, sy * b1, 1.8 + H)); c = (p0 + p1) / 2; d = p1 - p0
        o = box('TO_Gamba', tuple(c), (0.22, 0.22, d.length), ro if True else g, coll, root); o.rotation_mode = 'QUATERNION'; o.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d)
    for k in range(9):                                                        # traversi e diagonali
        z = 1.8 + H * k / 9; z2 = 1.8 + H * (k + 1) / 9; hw = b0 + (b1 - b0) * k / 9; hw2 = b0 + (b1 - b0) * (k + 1) / 9
        for (ax, sx) in (('x', -1), ('x', 1), ('y', -1), ('y', 1)):
            if ax == 'x':
                box('TO_Traverso', (sx * hw, 0, z), (0.12, 2 * hw, 0.12), ro if k % 2 else M['bianco'], coll, root)
                p0 = Vector((sx * hw, -hw, z)); p1 = Vector((sx * hw2, hw2, z2))
            else:
                box('TO_Traverso', (0, sx * hw, z), (2 * hw, 0.12, 0.12), ro if k % 2 else M['bianco'], coll, root)
                p0 = Vector((-hw, sx * hw, z)); p1 = Vector((hw2, sx * hw2, z2))
            d = p1 - p0; o = box('TO_Diagonale', tuple((p0 + p1) / 2), (0.08, 0.08, d.length), fe, coll, root); o.rotation_mode = 'QUATERNION'; o.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d)
    box('TO_Corona', (0, 0, 1.8 + H + 0.3), (1.8, 1.8, 0.6), g, coll, root)
    triv = R['trivella'] = empty('TO_Trivella', (0, 0, 9.0), root, coll)
    box('TO_Bozzello', (0, 0, 0), (0.7, 0.5, 1.0), g, coll, triv)
    shape('TO_Asta', 'cyl:1:1', (0, 0, -3.5), (0.12, 0.12, 6.0), (0, 0, 0), triv, M['cromo'], coll)
    shape('TO_Punta', 'cone', (0, 0, -6.7), (0.25, 0.25, 0.5), (PI, 0, 0), triv, M['ferro'], coll)
    box('TO_Baracca', (3.8, 1.5, 1.0), (2.2, 3.0, 2.0), M['bianco'], coll, root)
    return R


# ======================= CANNONE, GUINZAGLIO, CANNUCCIA, YOGA =======================
def cannone(coll, M, nome='Cannone'):
    R = {}; root = R['root'] = empty(nome, (0, 0, 0), None, coll); root.rotation_mode = 'XYZ'
    canna = R['canna'] = empty(nome + 'Canna', (0, 0, 0.75), root, coll); canna.rotation_mode = 'XYZ'
    shape(nome + 'Tubo', 'cyl:1:1', (0, -0.9, 0), (0.24, 0.24, 2.4), (PI / 2, 0, 0), canna, M['ferro'], coll)
    shape(nome + 'Bocca', 'cyl:1:1', (0, -2.1, 0), (0.3, 0.3, 0.2), (PI / 2, 0, 0), canna, M['ferro'], coll)
    shape(nome + 'Culatta', 'sphere', (0, 0.3, 0), (0.33, 0.33, 0.33), (0, 0, 0), canna, M['ferro'], coll)
    for s_ in (-1, 1):
        shape(nome + 'Ruota', 'cyl:1:1', (s_ * 0.4, 0.1, 0.55), (0.55, 0.55, 0.12), (0, PI / 2, 0), root, M['legno'], coll)
        shape(nome + 'Mozzo', 'cyl:1:1', (s_ * 0.47, 0.1, 0.55), (0.12, 0.12, 0.08), (0, PI / 2, 0), root, M['ferro'], coll)
    box(nome + 'Affusto', (0, 0.7, 0.35), (0.5, 1.6, 0.25), M['legno'], coll, root, rot=(-0.3, 0, 0))
    return R


def collare(coll, M, parent, raggio=0.13, z=0.0):
    """collare rosso con le borchie, figlio di parent (centrato sul collo)."""
    shape('GU_Collare', 'cyl:1:1', (0, 0, z), (raggio, raggio, 0.06), (0, 0, 0), parent, M['collare'], coll)
    for k in range(8):
        a = k * 2 * PI / 8; shape('GU_Borchia', 'sphere', (raggio * math.cos(a), raggio * math.sin(a), z), (0.018, 0.018, 0.018), (0, 0, 0), parent, M['borchia'], coll)
    return shape('GU_Anello', 'sphere', (0, -raggio - 0.01, z - 0.02), (0.025, 0.012, 0.03), (0, 0, 0), parent, M['borchia'], coll)


def guinzaglio(coll, M, nome='Guinzaglio', n=12):
    """corda come curva con n punti: guinzaglio_punti(G, f, a, b, abbassamento) la stende tra due punti del mondo."""
    cu = bpy.data.curves.new(nome, 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = 0.018; cu.bevel_resolution = 3
    sp = cu.splines.new('POLY'); sp.points.add(n - 1)
    o = bpy.data.objects.new(nome, cu); coll.objects.link(o); cu.materials.append(M['corda']); return dict(obj=o, curve=cu, n=n)


def guinzaglio_punti(G, f, a, b, cala=0.25):
    sp = G['curve'].splines[0]; a = Vector(a); b = Vector(b)
    for i, p in enumerate(sp.points):
        u = i / (G['n'] - 1); q = a.lerp(b, u); q.z -= cala * 4 * u * (1 - u); p.co = (q.x, q.y, q.z, 1.0)
        if f is not None: p.keyframe_insert('co', frame=f)


def cannuccia(coll, M, lunghezza=3.0, nome='Cannuccia'):
    """cannuccia a righe con la piega (la tiene il T-rex)."""
    R = {}; root = R['root'] = empty(nome, (0, 0, 0), None, coll); root.rotation_mode = 'XYZ'
    k = 10
    for i in range(k):
        shape(nome + 'Pezzo', 'cyl:1:1', (0, 0, (i + 0.5) * lunghezza / k), (0.09, 0.09, lunghezza / k), (0, 0, 0), root, M['cannuccia'] if i % 2 else M['cannuccia_r'], coll)
    piega = empty(nome + 'Piega', (0, 0, lunghezza), root, coll); piega.rotation_euler = (0.9, 0, 0)
    for i in range(3): shape(nome + 'Punta', 'cyl:1:1', (0, 0, (i + 0.5) * 0.25), (0.09, 0.09, 0.25), (0, 0, 0), piega, M['cannuccia_r'] if i % 2 else M['cannuccia'], coll)
    return R


def tappetino(coll, M, loc, rz=0.0, mat='tappetino'):
    return box('Tappetino', loc, (0.7, 1.9, 0.03), M[mat], coll, rot=(0, 0, rz))


# ======================= DISTRIBUTORE =======================
def distributore(coll, M, tipo='D1', prezzo='800 €/L'):
    """D1: pompa anni '50 rossa col globo e un chiosco; D2: pensilina moderna con due colonnine e il totem del prezzo."""
    R = {}; root = R['root'] = empty('DI_Root', (0, 0, 0), None, coll); root.rotation_mode = 'XYZ'
    F = font()
    if tipo == 'D1':
        for i, x in enumerate((-1.2, 1.2)):
            p = empty('DI_Pompa', (x, 0, 0), root, coll)
            box('DI_Zoccolo', (0, 0, 0.1), (0.9, 0.7, 0.2), M['bianco'], coll, p)
            shape('DI_Corpo', 'cap:0.36:1.6', (0, 0, 1.25), (1.0, 0.75, 1.0), (0, 0, 0), p, M['rosso'], coll)
            shape('DI_Globo', 'sphere', (0, 0, 2.55), (0.36, 0.2, 0.36), (0, 0, 0), p, M['vetro'], coll)
            _txt(coll, 'DI_GloboTesto', 'BENZINA', 0.11, M['rosso'], (0, -0.21, 2.55), parent=p, ext=0.01, fnt=F)
            box('DI_Quadrante', (0, -0.29, 1.55), (0.5, 0.06, 0.42), M['bianco'], coll, p)
            _txt(coll, 'DI_PrezzoPompa', prezzo, 0.1, M['nero'], (0, -0.33, 1.55), parent=p, ext=0.005, fnt=F)
            shape('DI_Pistola', 'cap:0.05:0.18', (0.42, -0.1, 1.3), (1, 1, 1), (0, 0.4, 0), p, M['nero'], coll)
        box('DI_Isola', (0, 0, 0.08), (4.2, 1.4, 0.16), M['bianco'], coll, root)
        ch = empty('DI_Chiosco', (0, 3.2, 0), root, coll)
        box('DI_Muro', (0, 0, 1.4), (5.0, 2.8, 2.8), M['bianco'], coll, ch); box('DI_Tetto', (0, -0.2, 2.95), (5.6, 3.4, 0.3), M['rosso'], coll, ch)
        box('DI_Porta', (-1.2, -1.41, 1.0), (0.9, 0.04, 2.0), M['ferro'], coll, ch); box('DI_Vetrina', (0.9, -1.41, 1.5), (2.2, 0.04, 1.1), M['vetro'], coll, ch)
        _txt(coll, 'DI_Insegna', 'BENZINA', 0.55, M['bianco'], (0, -1.62, 2.95), parent=ch, ext=0.05, fnt=F)
        cart = empty('DI_Cartello', (3.3, 0.4, 0), root, coll)
        box('DI_Palo', (0, 0, 1.6), (0.14, 0.14, 3.2), M['ferro'], coll, cart); box('DI_Tabella', (0, 0, 3.4), (1.9, 0.12, 1.0), M['bianco'], coll, cart)
        R['display'] = _txt(coll, 'DI_Prezzo', prezzo, 0.36, M['rosso'], (0, -0.08, 3.4), parent=cart, ext=0.02, fnt=F)
    else:
        for (x, y) in ((-3.2, -1.5), (3.2, -1.5), (-3.2, 2.5), (3.2, 2.5)): box('DI_Colonna', (x, y, 2.4), (0.35, 0.35, 4.8), M['bianco'], coll, root)
        box('DI_Pensilina', (0, 0.5, 4.95), (8.2, 5.6, 0.5), M['bianco'], coll, root)
        box('DI_Fascia', (0, -2.31, 4.95), (8.2, 0.04, 0.5), M['verde'], coll, root)
        _txt(coll, 'DI_Marchio', 'CARBURANTI', 0.32, M['bianco'], (0, -2.36, 4.95), parent=root, ext=0.02, fnt=F)
        for i, x in enumerate((-1.3, 1.3)):
            p = empty('DI_Colonnina', (x, 0.5, 0), root, coll)
            box('DI_Isola', (0, 0, 0.1), (1.1, 1.8, 0.2), M['ferro'], coll, p)
            box('DI_Corpo', (0, 0, 1.15), (0.85, 0.55, 1.9), M['bianco'], coll, p); box('DI_Fianco', (0, 0, 1.15), (0.87, 0.57, 0.25), M['verde'], coll, p)
            box('DI_Schermo', (0, -0.285, 1.6), (0.6, 0.02, 0.38), M['display'], coll, p)
            _txt(coll, 'DI_SchermoPrezzo', prezzo, 0.1, M['cifre_v'], (0, -0.3, 1.6), parent=p, ext=0.005, fnt=F)
            shape('DI_Pistola', 'cap:0.05:0.18', (0.47, -0.05, 1.2), (1, 1, 1), (0, 0.4, 0), p, M['nero'], coll)
        tot = empty('DI_Totem', (5.4, -1.2, 0), root, coll)
        box('DI_TotemCorpo', (0, 0, 3.0), (1.7, 0.45, 6.0), M['bianco'], coll, tot); box('DI_TotemTesta', (0, 0, 5.6), (1.72, 0.47, 0.8), M['verde'], coll, tot)
        box('DI_TotemSchermo', (0, -0.235, 3.8), (1.45, 0.02, 1.0), M['display'], coll, tot)
        _txt(coll, 'DI_TotemBenzina', 'BENZINA', 0.22, M['bianco'], (0, -0.25, 4.45), parent=tot, ext=0.005, fnt=F)
        R['display'] = _txt(coll, 'DI_Prezzo', prezzo.replace(' €/L', ''), 0.48, M['cifre'], (0, -0.25, 3.75), parent=tot, ext=0.005, fnt=F)
        _txt(coll, 'DI_EuroLitro', '€/L', 0.2, M['cifre'], (0, -0.25, 3.3), parent=tot, ext=0.005, fnt=F)
    return R


# ======================= DESERTO =======================
def deserto(coll, A, raggio=160.0, seme=3, centro=(0.0, 0.0), piatto=16.0):
    """terreno di sabbia con dune morbide (rumore), texture vera di sabbia; il centro (r < 18 m) resta quasi piatto per i personaggi."""
    import random
    rnd = random.Random(seme)
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=220, y_subdivisions=220, size=2 * raggio, location=(centro[0], centro[1], 0))
    o = bpy.context.active_object; o.name = 'Deserto'
    for c in o.users_collection: c.objects.unlink(o)
    coll.objects.link(o)
    onde = [(rnd.uniform(0, 2 * PI), rnd.uniform(0.02, 0.06), rnd.uniform(0, 2 * PI), rnd.uniform(1.5, 4.5)) for _ in range(7)]
    for v in o.data.vertices:
        x, y = v.co.x, v.co.y; r = math.hypot(x, y)
        h = sum(a * math.sin(f_ * (x * math.cos(d) + y * math.sin(d)) + ph) for (d, f_, ph, a) in onde)
        h = (h + 6.0) * min(1.0, max(0.0, (r - piatto) / 30.0)) ** 1.5
        v.co.z = h
    for p in o.data.polygons: p.use_smooth = True
    try: mat = A.materiale('Ground093C', dimensione=4.0, tinta=(1.15, 1.0, 0.82))
    except Exception: mat = material('P29_sabbia', (0.86, 0.7, 0.45), rough=0.9)
    o.data.materials.append(mat)
    return o


def casco(coll, M, nome='Casco'):
    """casco giallo da cantiere sciolto (quello di Cappellone che il T-rex rutta alla fine)."""
    r = empty(nome, (0, 0, 0), None, coll); r.rotation_mode = 'XYZ'
    shape(nome + 'Calotta', 'sphere', (0, 0, 0.12), (0.41, 0.41, 0.27), (0, 0, 0), r, M['giallo'], coll)
    shape(nome + 'Visiera', 'sphere', (0, -0.30, 0.09), (0.30, 0.22, 0.03), (0, 0, 0), r, M['giallo'], coll)
    shape(nome + 'Costola', 'sphere', (0, 0.0, 0.38), (0.06, 0.34, 0.04), (0, 0, 0), r, M['giallo'], coll)
    return r


def bandiera_c(coll, M, nome='BandieraC'):
    """bandiera inventata di Cappellone: una grande C bianca su rosso (nessuna bandiera vera)."""
    r = empty(nome, (0, 0, 0), None, coll); r.rotation_mode = 'XYZ'
    shape(nome + 'Asta', 'cyl:1:1', (0, 0, 1.6), (0.04, 0.04, 3.2), (0, 0, 0), r, M['cromo'], coll)
    tela = box(nome + 'Tela', (0.75, 0, 2.8), (1.4, 0.03, 0.9), M['rosso'], coll, r)
    _txt(coll, nome + 'Lettera', 'C', 0.75, M['bianco'], (0.75, -0.03, 2.8), parent=r, ext=0.01)
    return r
