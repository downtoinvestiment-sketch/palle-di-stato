"""Test 018 - LA MENTE (presentazione di Giulia): oggetti di scena.
Base di super sicurezza (stile 'S' militare o 'T' fantascienza): mura, filo spinato, torretta, porta blindata con la ruota,
fossato con l'acqua, griglia di laser, telecamere, cartello ZONA GIORNALE.
Squalo nello stile degli animali di animali.py (stile 'U' simpatico o 'V' cattivo).
Cranio che si apre come un coperchio con la cabina dentro e Giulia minuscola che guida (stile 'W' vintage o 'X' astronave):
funziona su Gualtiero e su Tumbo SENZA toccare tumbo.py (nasconde la sfera della testa e ne mette una tagliata uguale).
Cassetta della posta con palo e pezzo di marciapiede, lucchetto gigante, giornale, sala di controllo con gli schermi,
cornice da telecamera di sorveglianza (REC) da mettere davanti alla camera.
Tutti gli oggetti guardano verso -Y con rotazione 0, origine a terra."""
import math, bpy, bmesh
from mathutils import Vector, Matrix
from common import material, shape, empty, shared_mesh
import set004
from set004 import MB, obj, cyl, ball_, bx
from props007 import text_obj
PI = math.pi
cap = lambda r, L: 'cap:%g:%g' % (r, L)


def mats018():
    c = lambda n, col, **k: material('P18_' + n, col, **k); M = {}
    M['concrete'] = c('concrete', (0.62, 0.62, 0.60), rough=0.9); M['concreted'] = c('concreted', (0.42, 0.42, 0.41), rough=0.9)
    M['army'] = c('army', (0.30, 0.38, 0.18), rough=0.75); M['armyd'] = c('armyd', (0.20, 0.26, 0.12), rough=0.75)
    M['sand'] = c('sand', (0.74, 0.62, 0.40), rough=0.95); M['wire'] = c('wire', (0.35, 0.36, 0.38), rough=0.35, metallic=0.8)
    M['white'] = c('white', (0.93, 0.95, 0.97), rough=0.25, spec=0.7); M['panel'] = c('panel', (0.70, 0.74, 0.80), rough=0.3, metallic=0.4)
    M['cyan'] = c('cyan', (0.1, 0.85, 1.0), rough=0.3, emit=(0.1, 0.85, 1.0), emit_strength=2.2)
    M['glass'] = set004.glassy('P18_glass', (0.6, 0.85, 1.0), 0.35)
    M['laser'] = c('laser', (1.0, 0.05, 0.03), rough=0.3, emit=(1.0, 0.05, 0.02), emit_strength=6.0)
    M['laserpost'] = c('laserpost', (0.12, 0.12, 0.14), rough=0.4, metallic=0.6)
    M['water'] = c('water', (0.02, 0.18, 0.26), rough=0.06, spec=1.0, coat=1.0, coat_rough=0.02)
    M['curb'] = c('curb', (0.66, 0.64, 0.60), rough=0.85)
    M['steel'] = c('steel', (0.56, 0.58, 0.62), rough=0.3, metallic=0.9); M['steeld'] = c('steeld', (0.30, 0.32, 0.35), rough=0.35, metallic=0.9)
    M['yellow'] = c('yellow', (1.0, 0.78, 0.05), rough=0.5); M['black'] = c('black', (0.03, 0.03, 0.035), rough=0.45)
    M['camw'] = c('camw', (0.95, 0.95, 0.93), rough=0.35); M['lens'] = c('lens', (0.01, 0.01, 0.015), rough=0.05, spec=1.0, coat=1.0)
    M['led'] = c('led', (1.0, 0.05, 0.05), rough=0.3, emit=(1.0, 0.05, 0.03), emit_strength=4.0)
    M['lamp'] = c('lamp', (1.0, 0.95, 0.8), rough=0.3, emit=(1.0, 0.92, 0.75), emit_strength=3.0)
    M['sign'] = c('sign', (0.95, 0.80, 0.05), rough=0.5); M['signtxt'] = c('signtxt', (0.05, 0.05, 0.05), rough=0.5)
    M['red'] = c('red', (0.85, 0.06, 0.05), rough=0.45); M['blue'] = c('blue', (0.10, 0.30, 0.80), rough=0.45)
    M['gold'] = c('gold', (1.0, 0.74, 0.18), rough=0.22, metallic=0.95)
    M['paper'] = c('paper', (0.90, 0.89, 0.84), rough=0.9); M['ink'] = c('ink', (0.08, 0.08, 0.10), rough=0.7)
    M['pave'] = c('pave', (0.70, 0.69, 0.66), rough=0.9)
    # squalo
    M['shark'] = c('shark', (0.12, 0.26, 0.48), rough=0.55, spec=0.35); M['sharkd'] = c('sharkd', (0.05, 0.07, 0.12), rough=0.55, spec=0.35)
    M['belly'] = c('belly', (0.96, 0.96, 0.94), rough=0.6); M['teeth'] = c('teeth', (1.0, 1.0, 0.97), rough=0.25, spec=0.6)
    M['mouth'] = c('mouth', (0.45, 0.05, 0.08), rough=0.6); M['gum'] = c('gum', (0.95, 0.45, 0.55), rough=0.5)
    # cabina dentro la testa
    M['cabwood'] = c('cabwood', (0.42, 0.20, 0.08), rough=0.45); M['velvet'] = c('velvet', (0.70, 0.04, 0.08), rough=0.9)
    M['brass'] = c('brass', (1.0, 0.72, 0.30), rough=0.25, metallic=0.95); M['bulbg'] = c('bulbg', (0.2, 1.0, 0.3), rough=0.3, emit=(0.2, 1.0, 0.3), emit_strength=3.0)
    M['bulbr'] = c('bulbr', (1.0, 0.15, 0.1), rough=0.3, emit=(1.0, 0.15, 0.1), emit_strength=3.0)
    M['cabwall_W'] = c('cabwall_W', (0.55, 0.12, 0.10), rough=0.8); M['cabwall_X'] = c('cabwall_X', (0.08, 0.10, 0.18), rough=0.4)
    M['screen'] = c('screen', (0.2, 0.7, 1.0), rough=0.2, emit=(0.25, 0.75, 1.0), emit_strength=2.4)
    M['screeng'] = c('screeng', (0.3, 1.0, 0.4), rough=0.2, emit=(0.3, 1.0, 0.4), emit_strength=2.0)
    M['bone'] = c('bone', (0.98, 0.95, 0.86), rough=0.5)
    return M


def testo(coll, name, body, size, mat, loc, font=None, parent=None, rot=(PI / 2, 0, 0), spessore=0.01):
    o = text_obj(coll, name, body, size, mat, loc, rot=rot, parent=parent); o.data.extrude = spessore
    if font:
        try: o.data.font = bpy.data.fonts.load(font, check_existing=True)
        except Exception as ex: print('font', ex)
    return o


def _mesh_obj(name, bm, mat, coll, parent=None, smooth=True):
    me = bpy.data.meshes.new(name)
    for f in bm.faces: f.smooth = smooth
    bm.to_mesh(me); bm.free(); me.materials.append(mat)
    o = bpy.data.objects.new(name, me); o.parent = parent; coll.objects.link(o); return o


def anello(coll, name, r0, r1, z0, z1, mat, center=(0, 0), seg=96, parent=None):
    """anello piatto (corona circolare) da r0 a r1, spesso da z0 a z1."""
    bm = bmesh.new(); vs = []
    for i in range(seg):
        a = 2 * PI * i / seg; ca, sa = math.cos(a), math.sin(a)
        vs.append([bm.verts.new((center[0] + r * ca, center[1] + r * sa, z)) for (r, z) in ((r0, z0), (r1, z0), (r1, z1), (r0, z1))])
    for i in range(seg):
        a, b = vs[i], vs[(i + 1) % seg]
        for k in range(4): bm.faces.new((a[k], b[k], b[(k + 1) % 4], a[(k + 1) % 4]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = _mesh_obj(name, bm, mat, coll, parent, smooth=False); return o


# ============================================================================================ la base
def base(coll, M, stile='S', C=(0.0, 0.0), Rw=3.6, font=None, porta_ang=PI):
    """Base di super sicurezza attorno a un centro C. Mura a ottagono di raggio Rw con la porta blindata all'angolo porta_ang
    (PI = lato ovest, verso la casa di Gualtiero). Fossato ad anello attorno alle mura. Torretta accanto alla porta.
    Restituisce dict(root, door, wheel, lasers[], laser_root, cams[], water, sign, tower, door_pos, door_dir)."""
    R = {'cams': [], 'lasers': []}; root = R['root'] = empty('Base', (C[0], C[1], 0), None, coll)
    mil = stile == 'S'
    wall = M['concrete'] if mil else M['white']; walld = M['concreted'] if mil else M['panel']
    H = 2.15; T = 0.38; n = 8; gap = 0.95          # mezza larghezza del varco della porta
    mb = MB([wall, walld, M['cyan'], M['yellow'], M['black']])
    for i in range(n):
        a0 = porta_ang + PI / n + 2 * PI * i / n; a1 = a0 + 2 * PI / n
        p0 = Vector((Rw * math.cos(a0), Rw * math.sin(a0))); p1 = Vector((Rw * math.cos(a1), Rw * math.sin(a1)))
        segs = [(p0, p1)]
        if i == n - 1:                                              # il lato della porta: due mezzi muri con il varco in mezzo
            m = (p0 + p1) / 2; d = (p1 - p0).normalized(); segs = [(p0, m - d * gap), (m + d * gap, p1)]
        for (q0, q1) in segs:
            L = (q1 - q0).length; cc = (q0 + q1) / 2; rz = math.atan2(q1.y - q0.y, q1.x - q0.x)
            mb.box((cc.x, cc.y, H / 2), (L + T * 0.6, T, H), 0, rz=rz)
            mb.box((cc.x, cc.y, H + 0.06), (L + T * 0.8, T + 0.1, 0.12), 1, rz=rz)                       # cimasa
            if mil:
                mb.box((cc.x, cc.y, 0.45), (L + T * 0.62, T + 0.02, 0.10), 3, rz=rz)                      # fascia gialla
            else:
                mb.box((cc.x, cc.y, H * 0.62), (L + T * 0.62, T + 0.03, 0.07), 2, rz=rz)                  # striscia luminosa
    wo = mb.build('BaseMura', coll); wo.parent = root
    # porta blindata nel varco
    am = porta_ang + PI / n + 2 * PI * (n - 1) / n + PI / n         # angolo del centro del lato con la porta
    dp = Vector((Rw * math.cos(am) * math.cos(PI / n), Rw * math.sin(am) * math.cos(PI / n)))
    R['door_pos'] = (C[0] + dp.x, C[1] + dp.y); R['door_dir'] = (math.cos(am), math.sin(am))        # dir = verso l'esterno
    dr = empty('PortaCardine', (dp.x - math.sin(am) * gap * -1, dp.y + math.cos(am) * gap * -1, 0), root, coll)
    dr.rotation_euler = (0, 0, am + PI / 2); dr.rotation_mode = 'XYZ'; R['door'] = dr
    leaf = MB([M['steel'], M['steeld'], M['yellow'], M['black']])
    leaf.b2((0.0, -0.09, 0.0), (2 * gap, 0.09, H - 0.05), 0)
    for k in range(5): leaf.b2((0.08, -0.11, 0.12 + k * 0.4), (2 * gap - 0.08, 0.11, 0.2 + k * 0.4), 1)              # rinforzi
    for k in range(6): leaf.box((0.25 + k * 0.28, -0.115, 0.12), (0.14, 0.02, 0.1), 2 + k % 2)                     # strisce di pericolo
    lo = leaf.build('PortaBlindata', coll); lo.parent = dr
    wh = empty('PortaRuota', (gap, -0.16, 1.1), dr, coll); wh.rotation_mode = 'XYZ'; R['wheel'] = wh
    import props017
    tor = bpy.data.meshes.get('P18_ruota') or props017.torus_mesh('P18_ruota', 0.32, 0.035)
    if not tor.materials: tor.materials.append(None)
    to = bpy.data.objects.new('RuotaAnello', tor); coll.objects.link(to); to.parent = wh; to.rotation_euler = (PI / 2, 0, 0)
    to.material_slots[0].link = 'OBJECT'; to.material_slots[0].material = M['steel'] if mil else M['cyan']
    for k in range(3): obj('RuotaRaggio', set004.box_c(), (0, 0, 0), (0.62, 0.04, 0.04), M['steeld'], coll, rot=(0, k * PI / 3, 0), parent=wh)
    cyl('RuotaMozzo', 0.07, 0.08, (0, 0, 0), M['steeld'], coll, rot=(PI / 2, 0, 0), parent=wh)
    # torretta accanto alla porta, appena dentro le mura
    ta = am + 0.55; tp = Vector((math.cos(ta), math.sin(ta))) * (Rw - 0.9)
    tw = R['tower'] = empty('Torretta', (tp.x, tp.y, 0), root, coll)
    if mil:
        for sx in (-1, 1):
            for sy in (-1, 1): obj('TorrGamba', set004.box_c(), (sx * 0.55, sy * 0.55, 1.9), (0.14, 0.14, 3.8), M['armyd'], coll, parent=tw)
        obj('TorrCabina', set004.box_c(), (0, 0, 4.25), (1.6, 1.6, 0.9), M['army'], coll, parent=tw)
        obj('TorrFinestra', set004.box_c(), (0, 0, 4.35), (1.62, 1.62, 0.35), M['black'], coll, parent=tw)
        obj('TorrTetto', set004.prism(), (0, 0, 4.95), (1.9, 1.9, 0.5), M['armyd'], coll, parent=tw)
        fa = empty('Faro', (0.0, -0.85, 4.1), tw, coll); cyl('FaroCorpo', 0.18, 0.3, (0, 0, 0), M['steeld'], coll, rot=(PI / 2, 0, 0), parent=fa)
        cyl('FaroVetro', 0.16, 0.02, (0, -0.16, 0), M['lamp'], coll, rot=(PI / 2, 0, 0), parent=fa)
        for k in range(10):                                           # sacchi di sabbia accanto alla porta
            a = am + (0.20 + 0.035 * (k % 5)) * (1 if k < 5 else -1); z = 0.13 + 0.24 * (k // 5 % 2)
            p = Vector((math.cos(a), math.sin(a))) * (Rw + 0.55)
            ball_('Sacco', 1.0, (p.x, p.y, z * 0.8), M['sand'], coll, parent=root, sc=(0.3, 0.2, 0.14))
    else:
        cyl('TorrFusto', 0.32, 3.8, (0, 0, 1.9), M['white'], coll, parent=tw); cyl('TorrAnello', 0.36, 0.08, (0, 0, 2.6), M['cyan'], coll, parent=tw)
        ball_('TorrCupola', 0.95, (0, 0, 4.25), M['glass'], coll, parent=tw, sc=(1, 1, 0.75)); cyl('TorrPiatto', 1.0, 0.18, (0, 0, 3.85), M['panel'], coll, parent=tw)
        cyl('TorrBordo', 1.02, 0.05, (0, 0, 3.97), M['cyan'], coll, parent=tw)
        fa = empty('Faro', (0.0, 0.0, 4.25), tw, coll); ball_('FaroOcchio', 0.3, (0, 0, 0), M['cyan'], coll, parent=fa)
    R['faro'] = fa
    # filo spinato (militare) / antenne (fantascienza) sopra le mura
    for i in range(n):
        a0 = porta_ang + PI / n + 2 * PI * i / n; a1 = a0 + 2 * PI / n
        p0 = Vector((Rw * math.cos(a0), Rw * math.sin(a0))); p1 = Vector((Rw * math.cos(a1), Rw * math.sin(a1))); L = (p1 - p0).length
        for k in range(int(L / 0.32)):
            if i == n - 1 and abs((k + 0.5) / int(L / 0.32) - 0.5) * L < gap + 0.2: continue
            p = p0.lerp(p1, (k + 0.5) / int(L / 0.32)); rz = math.atan2(p1.y - p0.y, p1.x - p0.x)
            if mil:
                o = bpy.data.objects.new('FiloSpinato', tor); coll.objects.link(o); o.parent = root
                o.location = (p.x, p.y, H + 0.42); o.scale = (0.75, 0.75, 0.75); o.rotation_euler = (PI / 2 + 0.25 * (k % 2), 0, rz + PI / 2)
                o.material_slots[0].link = 'OBJECT'; o.material_slots[0].material = M['wire']
            elif k % 4 == 0:
                cyl('Antenna', 0.02, 0.6, (p.x, p.y, H + 0.42), M['panel'], coll, parent=root); ball_('AntennaLuce', 0.05, (p.x, p.y, H + 0.74), M['cyan'], coll, parent=root)
    # fossato
    R['water'] = anello(coll, 'FossatoAcqua', Rw + 0.9, Rw + 3.9, 0.0, 0.035, M['water'], parent=root)
    anello(coll, 'FossatoBordoIn', Rw + 0.6, Rw + 0.9, 0.0, 0.14, M['curb'] if mil else M['panel'], parent=root)
    anello(coll, 'FossatoBordoOut', Rw + 3.9, Rw + 4.2, 0.0, 0.14, M['curb'] if mil else M['panel'], parent=root)
    # cartello ZONA GIORNALE sopra la porta
    sg = R['sign'] = empty('CartelloZona', (dp.x * 1.02, dp.y * 1.02, H + 0.75), root, coll); sg.rotation_euler = (0, 0, am + PI / 2)
    obj('CartelloTavola', set004.box_c(), (0, 0, 0), (2.5, 0.08, 0.6), M['sign'] if mil else M['white'], coll, parent=sg)
    for sx in (-1, 1): obj('CartelloPalo', set004.box_c(), (sx * 0.9, 0.05, -0.4), (0.07, 0.07, 0.6), M['steeld'], coll, parent=sg)
    testo(coll, 'CartelloScritta', 'ZONA GIORNALE', 0.32, M['signtxt'] if mil else M['cyan'], (0, -0.05, -0.12), font=font, parent=sg).data.align_x = 'CENTER'
    # griglia di laser attorno alla cassetta (al centro)
    lr = R['laser_root'] = empty('Laser', (0, 0, 0), root, coll); S = 1.25
    for sx in (-1, 1):
        for sy in (-1, 1):
            cyl('LaserPalo', 0.05, 1.7, (sx * S, sy * S, 0.85), M['laserpost'], coll, parent=lr); ball_('LaserTesta', 0.07, (sx * S, sy * S, 1.72), M['laser'], coll, parent=lr)
    k = 0
    for side in range(4):
        a = side * PI / 2; d = Vector((math.cos(a), math.sin(a))); t = Vector((-d.y, d.x))
        for j, z in enumerate((0.25, 0.55, 0.85, 1.15, 1.45)):
            p = d * S; zz = z + (0.08 if side % 2 else 0)
            o = obj('LaserRaggio', shared_mesh('cyl:1:1'), (p.x, p.y, zz), (0.012, 0.012, 2 * S), M['laser'], coll, rot=(PI / 2, 0, a + PI / 2 + PI / 2), parent=lr)
            o.rotation_euler = (PI / 2, 0, math.atan2(t.y, t.x) + PI / 2); R['lasers'].append(o); k += 1
        for sgn in (-1, 1):                                            # due raggi in diagonale per lato
            p = d * S; L = math.hypot(2 * S, 1.2)
            o = obj('LaserDiag', shared_mesh('cyl:1:1'), (p.x, p.y, 0.85), (0.012, 0.012, L), M['laser'], coll, parent=lr)
            o.rotation_euler = (PI / 2 + sgn * math.atan2(1.2, 2 * S), 0, math.atan2(t.y, t.x) + PI / 2); R['lasers'].append(o)
    # telecamere sulle mura (girate verso il centro)
    for i in range(0, n, 2):
        a = porta_ang + PI / n + 2 * PI * i / n + 0.2
        p = Vector((math.cos(a), math.sin(a))) * (Rw - 0.25)
        cm = telecamera(coll, M, root); cm.location = (p.x, p.y, H + 0.25); cm.rotation_euler = (0.35, 0, a + PI / 2); R['cams'].append(cm)
    return R


def telecamera(coll, M, parent=None):
    """telecamera di sorveglianza: corpo bianco, obiettivo nero, lucina rossa. Guarda verso -Y."""
    g = empty('Telecamera', (0, 0, 0), parent, coll); g.rotation_mode = 'XYZ'
    obj('TeleCorpo', set004.box_c(), (0, -0.05, 0), (0.18, 0.42, 0.18), M['camw'], coll, parent=g)
    obj('TeleTettuccio', set004.box_c(), (0, -0.08, 0.11), (0.24, 0.5, 0.03), M['camw'], coll, parent=g)
    cyl('TeleObiettivo', 0.065, 0.04, (0, -0.27, 0), M['lens'], coll, rot=(PI / 2, 0, 0), parent=g)
    ball_('TeleLed', 0.022, (0.06, -0.26, 0.06), M['led'], coll, parent=g)
    obj('TeleStaffa', set004.box_c(), (0, 0.18, -0.08), (0.05, 0.05, 0.2), M['steeld'], coll, parent=g)
    return g


# ============================================================================================ lo squalo
def _loft(name, prof, coll, parent, mats, belly_z=-0.25, seg=28):
    """corpo a fuso: prof = [(y, rx, rz, zc)] sezioni ellittiche lungo Y. Facce di sotto (normale verso il basso) col secondo materiale."""
    bm = bmesh.new(); rings = []
    for (y, rx, rz, zc) in prof:
        rings.append([bm.verts.new((rx * math.cos(2 * PI * i / seg), y, zc + rz * math.sin(2 * PI * i / seg))) for i in range(seg)])
    for a_, b_ in zip(rings, rings[1:]):
        for i in range(seg): bm.faces.new((a_[i], a_[(i + 1) % seg], b_[(i + 1) % seg], b_[i]))
    for rg, yy in ((rings[0], prof[0][0]), (rings[-1], prof[-1][0])):
        c = bm.verts.new((0, yy, sum(v.co.z for v in rg) / seg))
        for i in range(seg):
            try: bm.faces.new((rg[i], rg[(i + 1) % seg], c))
            except ValueError: pass
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for f in bm.faces:
        f.material_index = 1 if f.calc_center_median().z < belly_z else 0
    me = bpy.data.meshes.new(name)
    for f in bm.faces: f.smooth = True
    bm.to_mesh(me); bm.free()
    for m in mats: me.materials.append(m)
    o = bpy.data.objects.new(name, me); o.parent = parent; coll.objects.link(o); return o


def _pinna(name, pts, th, coll, parent, mat):
    """pinna piatta: poligono pts [(y, z)] nel piano YZ, spessa th (lungo X), bordi arrotondati dallo smooth."""
    bm = bmesh.new(); n = len(pts)
    f0 = [bm.verts.new((-th / 2, y, z)) for (y, z) in pts]; f1 = [bm.verts.new((th / 2, y, z)) for (y, z) in pts]
    bm.faces.new(f0[::-1]); bm.faces.new(f1)
    for i in range(n): bm.faces.new((f0[i], f0[(i + 1) % n], f1[(i + 1) % n], f1[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); me.materials.append(mat)
    o = bpy.data.objects.new(name, me); o.parent = parent; coll.objects.link(o); return o


def squalo(coll, M, stile='Y', scale=1.0):
    """Squalo cartoon riconoscibile: muso a punta, pinna dorsale a triangolo all'indietro, coda a mezzaluna, pancia bianca,
    bocca larga sotto il muso con i denti, occhi come Tumbo. Lungo 2,2 m (scale=1), largo 0,8 m: sta nel fossato.
    stile 'Y' grigio-azzurro simpatico, 'Z' scuro con le sopracciglia cattive e il sorriso pieno di denti.
    Nuota verso -Y. Origine a pelo d'acqua (z = 0). Restituisce dict(root, body, tail, jaw, fin, head)."""
    import animali
    S, E, AM = animali._kit(coll, 'Sq_')
    R = {}; root = R['root'] = E('Root', (0, 0, 0), None); root.scale = (scale,) * 3; root.rotation_mode = 'XYZ'
    top = M['shark'] if stile == 'Y' else M['sharkd']
    body = R['body'] = E('Body', (0, 0, 0.0), root); body.rotation_mode = 'XYZ'
    prof = [(-1.05, 0.02, 0.02, 0.06), (-1.0, 0.12, 0.10, 0.05), (-0.88, 0.24, 0.20, 0.03), (-0.7, 0.33, 0.28, 0.02), (-0.45, 0.40, 0.33, 0.0),
            (-0.15, 0.41, 0.34, 0.0), (0.15, 0.36, 0.30, 0.0), (0.42, 0.26, 0.22, 0.01), (0.66, 0.15, 0.13, 0.02), (0.82, 0.08, 0.08, 0.03), (0.9, 0.05, 0.05, 0.03)]
    _loft('SqCorpo', prof, coll, body, [top, M['belly']], belly_z=-0.12)
    fin = R['fin'] = E('Pinna', (0, -0.3, 0.29), body)
    _pinna('SqDorsale', [(-0.32, 0.0), (0.22, 0.0), (0.26, 0.14), (0.24, 0.78)], 0.08, coll, fin, top)
    for s_ in (-1, 1):
        pl = E('PinnaLat%d' % s_, (s_ * 0.33, -0.38, -0.14), body); pl.rotation_euler = (0, s_ * 1.25, 0)
        _pinna('SqPett%d' % s_, [(-0.18, 0.0), (0.12, 0.0), (0.22, -0.05), (0.1, -0.5)], 0.05, coll, pl, top)
    tail = R['tail'] = E('Coda', (0, 0.86, 0.03), body); tail.rotation_mode = 'XYZ'
    _pinna('SqCoda', [(-0.1, 0.0), (0.02, 0.1), (0.38, 0.7), (0.2, 0.68), (0.1, 0.16), (0.3, -0.42), (0.14, -0.42), (-0.04, -0.06)], 0.06, coll, tail, top)
    head = R['head'] = E('Testa', (0, -0.75, 0.0), body)
    jaw = R['jaw'] = E('Bocca', (0, -0.08, -0.12), head); jaw.rotation_mode = 'XYZ'
    big = stile == 'Z'
    S('BoccaDentro', 'sphere', (0, 0.0, 0), (0.25 if big else 0.21, 0.14, 0.07), jaw, M['mouth'])
    nt = 11 if big else 9
    for k in range(nt):
        a = -1.05 + k * 2.1 / (nt - 1); x = (0.24 if big else 0.2) * math.sin(a); y = -0.13 * math.cos(a) + 0.01
        S('Dente%d' % k, 'cone', (x, y, 0.045), (0.026, 0.026, 0.06 if big else 0.05), jaw, M['teeth'], rot=(PI, 0, 0))
        S('DenteGiu%d' % k, 'cone', (x * 0.95, y * 0.95, -0.045), (0.022, 0.022, 0.045), jaw, M['teeth'])
    animali._eyes(R, S, E, head, AM, 0.2, -0.16, 0.13, 1.05 if not big else 0.9, brow=M['sharkd'] if big else None)
    for nm in 'LR':
        e = R['eye' + nm]; e.rotation_euler = (0, 0, (-0.55 if nm == 'L' else 0.55))
    if big:
        for nm, s_ in (('L', -1), ('R', 1)): R['brow' + nm].rotation_euler = (0, s_ * 0.5, s_ * -0.5); R['brow' + nm].location.z -= 0.03
    for s_ in (-1, 1):
        for k in range(3): S('Branchia%d%d' % (s_, k), 'sphere', (s_ * 0.36, -0.52 + k * 0.08, -0.02), (0.012, 0.01, 0.12), body, M['sharkd'] if not big else M['black'], rot=(0, 0, s_ * 0.5))
    return R


# ============================================================================================ il cranio che si apre
def _sfera_tagliata(name, sc, zc, coll, parent, mat_out, mat_in, sopra):
    """meta' (sopra o sotto il piano z = zc, in coordinate locali gia' scalate) di un ellissoide sc = (rx, ry, rz), con il guscio interno."""
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=40, v_segments=24, radius=1.0)
    for v in bm.verts: v.co = Vector((v.co.x * sc[0], v.co.y * sc[1], v.co.z * sc[2]))
    geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
    res = bmesh.ops.bisect_plane(bm, geom=geom, plane_co=(0, 0, zc), plane_no=(0, 0, 1), clear_outer=sopra is False, clear_inner=sopra is True)
    # guscio interno: copia rimpicciolita con le normali girate
    inner = bmesh.ops.duplicate(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:])
    iv = [e for e in inner['geom'] if isinstance(e, bmesh.types.BMVert)]; ifc = [e for e in inner['geom'] if isinstance(e, bmesh.types.BMFace)]
    for v in iv: v.co = Vector((v.co.x * 0.94, v.co.y * 0.94, zc + (v.co.z - zc) * 0.94))
    bmesh.ops.reverse_faces(bm, faces=ifc)
    for f in ifc: f.material_index = 1
    # bordo: unisce i due anelli aperti
    def ring(vs): return sorted([v for v in vs if abs(v.co.z - zc) < 1e-4], key=lambda v: math.atan2(v.co.y, v.co.x))
    ro = ring([v for v in bm.verts if v not in set(iv)]); ri = ring(iv)
    if len(ro) == len(ri) and len(ro) > 3:
        for i in range(len(ro)):
            try: f = bm.faces.new((ro[i], ro[(i + 1) % len(ro)], ri[(i + 1) % len(ri)], ri[i])); f.material_index = 0
            except ValueError: pass
    me = bpy.data.meshes.new(name)
    for f in bm.faces: f.smooth = True
    bm.to_mesh(me); bm.free(); me.materials.append(mat_out); me.materials.append(mat_in)
    o = bpy.data.objects.new(name, me); o.parent = parent; coll.objects.link(o); return o


def cranio(coll, M, GM, head, sfera, sc, zc, pelle, stile='W', giulia_s=0.1, oggetto='mattarello', figli_coperchio=(), luce=0.6):
    """Sostituisce la sfera `sfera` (figlia di `head`, centrata in 0) con due meta': sotto fissa, sopra un coperchio
    incernierato dietro (asse X, cerniera a y = +sc[1]). Dentro: cabina e Giulia minuscola seduta che guida.
    figli_coperchio: oggetti della testa da attaccare al coperchio (sopracciglia, ciuffi in alto).
    Restituisce dict(hinge, lid, bottom, cabin, J, light). Per aprire: hinge.rotation_euler.x = -1.9 (all'indietro)."""
    import giulia
    sfera.hide_render = True; sfera.hide_viewport = True
    inside = M['cabwall_' + stile]
    bot = _sfera_tagliata('CranioSotto', sc, zc, coll, head, pelle, inside, sopra=False)
    hinge = empty('CranioCerniera', (0, sc[1] * 0.92, zc), head, coll); hinge.rotation_mode = 'XYZ'
    lid = _sfera_tagliata('CranioCoperchio', sc, zc, coll, hinge, pelle, inside, sopra=True); lid.location = (0, -sc[1] * 0.92, -zc)
    bpy.context.view_layer.update()
    for o in figli_coperchio:
        mw = o.matrix_world.copy(); o.parent = lid; o.matrix_world = mw
    cab = empty('Cabina', (0, 0, 0), head, coll)
    rfl = math.sqrt(max(0.0, 1 - (0.0 / sc[2]) ** 2)) * min(sc[0], sc[1]) * 0.9
    zf = -sc[2] * 0.05
    rf = math.sqrt(max(0.0, 1 - (zf / sc[2]) ** 2)) * min(sc[0], sc[1]) * 0.9
    cyl('CabPavimento', rf, 0.01, (0, 0, zf), M['cabwood'] if stile == 'W' else M['panel'], coll, parent=cab)
    s = giulia_s
    # sedile dietro, cruscotto davanti (dietro gli occhi)
    if stile == 'W':
        k_ = giulia_s / 0.1
        obj('CabSedile', set004.box_c(), (0, 0.06 * k_, zf + 0.035 * k_), (0.14 * k_, 0.1 * k_, 0.07 * k_), M['velvet'], coll, parent=cab)
        obj('CabSchienale', set004.box_c(), (0, 0.118 * k_, zf + 0.07 * k_ + 1.08 * giulia_s), (0.15 * k_, 0.025 * k_, 2.16 * giulia_s), M['velvet'], coll, parent=cab)   # piu' alto della testa con i bigodini, ma dentro il cranio chiuso
        obj('CabCruscotto', set004.box_c(), (0, -0.12, zf + 0.05), (0.26, 0.06, 0.1), M['cabwood'], coll, rot=(0.4, 0, 0), parent=cab)
        for k in range(5): ball_('CabLucina', 0.008, (-0.08 + k * 0.04, -0.15, zf + 0.105), M['bulbg'] if k % 2 else M['bulbr'], coll, parent=cab)
        for sx in (-1, 1):
            cyl('CabLeva', 0.004, 0.08, (sx * 0.07, -0.06, zf + 0.06), M['brass'], coll, rot=(0.3, 0, 0), parent=cab)
            ball_('CabPomello', 0.012, (sx * 0.07, -0.072, zf + 0.098), M['velvet'], coll, parent=cab)
        for sx in (-1, 1): cyl('CabTubo', 0.006, 0.18, (sx * 0.15, 0.0, zf + 0.09), M['brass'], coll, rot=(0, 0, 0), parent=cab)
    else:
        obj('CabSedile', set004.box_c(), (0, 0.06, zf + 0.04), (0.1, 0.08, 0.05), M['white'], coll, parent=cab)
        obj('CabSchienale', set004.box_c(), (0, 0.105, zf + 0.12), (0.1, 0.025, 0.15), M['white'], coll, parent=cab)
        obj('CabCruscotto', set004.box_c(), (0, -0.12, zf + 0.05), (0.26, 0.05, 0.1), M['panel'], coll, rot=(0.4, 0, 0), parent=cab)
        obj('CabSchermo', set004.box_c(), (0, -0.14, zf + 0.105), (0.18, 0.006, 0.05), M['screen'], coll, rot=(0.4, 0, 0), parent=cab)
        for sx in (-1, 1): obj('CabSchermoLat', set004.box_c(), (sx * 0.14, -0.06, zf + 0.09), (0.006, 0.07, 0.05), M['screen'], coll, rot=(0, 0, sx * 0.3), parent=cab)
        cyl('CabCloche', 0.005, 0.07, (0, -0.06, zf + 0.06), M['steeld'], coll, parent=cab)
    # Giulia minuscola seduta
    # seduta davvero: il sedere sul cuscino, la schiena contro lo schienale, le gambe in avanti, le braccia avanti sulla cloche
    J = giulia.giulia(coll, GM, 'A'); r = J['root']; r.parent = cab; r.scale = (s, s, s); r.rotation_mode = 'XYZ'
    r.location = (0, 0.06 * s / 0.1 - 0.17 * s, zf + 0.07 * s / 0.1 - 0.36 * s)
    for nm, sx in (('hipL', -1), ('hipR', 1)): J[nm].rotation_mode = 'XYZ'; J[nm].rotation_euler = (-1.3, 0, sx * 0.12)
    for nm, sx in (('shoulderL', -1), ('shoulderR', 1)): J[nm].rotation_mode = 'XYZ'; J[nm].rotation_euler = (-1.05, 0, sx * 0.1)
    if oggetto == 'mattarello':
        mt = giulia.mattarello(coll, GM, J); mt.rotation_euler = (1.05, 0, 0); J['tool'] = mt
    else:
        g = empty('GI_Osso', (0, -0.05, -0.62), J['shoulderR'], coll); g.rotation_euler = (1.05, 0, 0)
        cyl('OssoFusto', 0.035, 0.4, (0, -0.2, 0), M['bone'], coll, rot=(PI / 2, 0, 0), parent=g)
        for yy in (0.0, -0.4):
            for sx in (-1, 1): ball_('OssoTesta', 0.055, (sx * 0.04, -0.2 + yy + 0.2, 0), M['bone'], coll, parent=g)
        J['tool'] = g
    # luce dentro la testa (accesa solo quando il coperchio e' aperto)
    l = bpy.data.lights.new('CabLuce', 'POINT'); l.energy = luce; l.color = (1.0, 0.85, 0.6) if stile == 'W' else (0.6, 0.85, 1.0); l.shadow_soft_size = 0.02; l.use_shadow = False
    lo = bpy.data.objects.new('CabLuce', l); coll.objects.link(lo); lo.parent = cab; lo.location = (0, -0.05, zc + 0.05)
    return dict(hinge=hinge, lid=lid, bottom=bot, cabin=cab, J=J, light=lo)


# ============================================================================================ oggetti piccoli
def giornale(coll, M, font=None, parent=None):
    """giornale piegato (0,34 x 0,25), testata LA GAZZETTA. Piatto nel piano XZ, guarda verso -Y."""
    g = empty('Giornale', (0, 0, 0), parent, coll); g.rotation_mode = 'XYZ'
    obj('GiornaleCarta', set004.box_c(), (0, 0, 0), (0.36, 0.025, 0.26), M['paper'], coll, parent=g)
    t = testo(coll, 'GiornaleTestata', 'LA GAZZETTA', 0.05, M['ink'], (0, -0.014, 0.075), font=font, parent=g, spessore=0.001); t.data.align_x = 'CENTER'
    for k in range(4):
        obj('GiornaleRiga', set004.box_c(), (-0.07 + (k % 2) * 0.15, -0.0135, 0.02 - (k // 2) * 0.07), (0.13, 0.002, 0.05), M['ink'], coll, parent=g)
    return g


def cassetta(coll, M, marciapiede=True):
    """cassetta della posta su palo, bandierina rossa. Restituisce dict(root, door, flag, paper_slot)."""
    R = {}; r = R['root'] = empty('Cassetta', (0, 0, 0), None, coll); r.rotation_mode = 'XYZ'
    cyl('CassPalo', 0.05, 1.05, (0, 0, 0.52), M['steeld'], coll, parent=r)
    obj('CassCorpo', set004.box_c(), (0, 0, 1.18), (0.34, 0.55, 0.26), M['blue'], coll, parent=r)
    cyl('CassTetto', 0.17, 0.55, (0, 0, 1.31), M['blue'], coll, rot=(PI / 2, 0, 0), parent=r)
    d = R['door'] = empty('CassSportello', (0, -0.28, 1.05), r, coll); d.rotation_mode = 'XYZ'
    obj('CassSportelloT', set004.box_c(), (0, -0.005, 0.15), (0.34, 0.01, 0.3), M['blue'], coll, parent=d)
    f = R['flag'] = empty('CassBandiera', (0.18, 0.1, 1.2), r, coll); f.rotation_mode = 'XYZ'
    obj('CassAsta', set004.box_c(), (0.01, 0, 0.12), (0.02, 0.03, 0.26), M['red'], coll, parent=f); obj('CassBand', set004.box_c(), (0.01, -0.07, 0.22), (0.02, 0.14, 0.09), M['red'], coll, parent=f)
    if marciapiede:
        R['pave'] = obj('CassMarciapiede', set004.box_c(), (0, 0, -0.06), (0.75, 0.6, 0.14), M['pave'], coll, parent=r)
    return R


def lucchetto(coll, M, s=1.0):
    g = empty('Lucchetto', (0, 0, 0), None, coll); g.rotation_mode = 'XYZ'; g.scale = (s, s, s)
    obj('LuccCorpo', set004.box_c(), (0, 0, 0), (0.42, 0.18, 0.36), M['gold'], coll, parent=g)
    import props017
    tor = bpy.data.meshes.get('P18_arco') or props017.torus_mesh('P18_arco', 0.15, 0.04)
    if not tor.materials: tor.materials.append(None)
    a = bpy.data.objects.new('LuccArco', tor); coll.objects.link(a); a.parent = g; a.location = (0, 0, 0.2); a.rotation_euler = (PI / 2, 0, 0); a.scale = (1, 1.4, 1)
    a.material_slots[0].link = 'OBJECT'; a.material_slots[0].material = M['steel']
    cyl('LuccBuco', 0.04, 0.02, (0, -0.095, -0.03), M['black'], coll, rot=(PI / 2, 0, 0), parent=g)
    return g


def sala_controllo(coll, M, C=(600.0, 0.0), font=None):
    """stanzetta con la scrivania e nove schermi (tre per tre) sulla parete di fondo (y = C.y + 1.6). Il pubblico sta a -Y."""
    x, y = C; mb = MB([M['concreted'], M['panel'], M['black'], M['steeld']])
    mb.b2((x - 3, y - 3, -0.1), (x + 3, y + 2.2, 0.0), 0)                                   # pavimento
    mb.b2((x - 3, y + 1.9, 0), (x + 3, y + 2.1, 3.0), 1)                                    # parete di fondo
    for sx in (-1, 1): mb.b2((x + sx * 3 - 0.1, y - 3, 0), (x + sx * 3 + 0.1, y + 2.1, 3.0), 1)
    mb.b2((x - 3.1, y - 3, 3.0), (x + 3.1, y + 2.2, 3.15), 1)                              # soffitto
    mb.b2((x - 3.1, y - 3.2, 0), (x + 3.1, y - 3.0, 3.0), 1)                               # parete davanti
    mb.b2((x - 2.2, y + 0.8, 0.72), (x + 2.2, y + 1.6, 0.8), 3)                            # scrivania
    for sx in (-1, 1): mb.b2((x + sx * 2.1 - 0.05, y + 0.85, 0), (x + sx * 2.1 + 0.05, y + 1.55, 0.72), 3)
    mb.b2((x - 2.15, y + 1.75, 0.95), (x + 2.15, y + 1.9, 2.75), 2)                         # cornice degli schermi
    mb.build('SalaControllo', coll)
    scr = []
    def feed(k):
        m = bpy.data.materials.new('P18_feed%d' % k); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']
        tc = nt.nodes.new('ShaderNodeTexCoord'); nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 3.0 + k; nz.inputs['Detail'].default_value = 6
        mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Location'].default_value = (k * 1.7, k * 0.3, 0)
        nt.links.new(tc.outputs['Object'], mp.inputs['Vector']); nt.links.new(mp.outputs['Vector'], nz.inputs['Vector'])
        cr = nt.nodes.new('ShaderNodeValToRGB'); cr.color_ramp.elements[0].color = (0.02, 0.06, 0.05, 1); cr.color_ramp.elements[1].color = (0.35, 0.75, 0.55, 1)
        nt.links.new(nz.outputs['Fac'], cr.inputs['Fac']); nt.links.new(cr.outputs['Color'], b.inputs['Emission Color']); b.inputs['Emission Strength'].default_value = 0.9
        b.inputs['Base Color'].default_value = (0, 0, 0, 1); return m
    FEEDS = [feed(k) for k in range(3)]
    for i in range(3):
        for j in range(3):
            o = obj('Schermo', set004.box_c(), (x - 1.42 + i * 1.42, y + 1.74, 1.25 + j * 0.6), (1.3, 0.02, 0.54), FEEDS[(i + 2 * j) % 3], coll)
            scr.append(o)
    for k in range(5): obj('Tastiera', set004.box_c(), (x - 1.6 + k * 0.8, y + 1.1, 0.82), (0.5, 0.18, 0.03), M['black'], coll)
    ball_('LedSala', 0.05, (x + 2.0, y + 1.2, 0.86), M['led'], coll)
    return scr


def cornice_rec(coll, M, cam, font=None, nome='CAM 3', dist=0.6, lens=35.0, sensor=36.0, aspect=(1080, 1920)):
    """cornice da telecamera di sorveglianza appiccicata alla camera: angoli bianchi, REC con il pallino rosso, nome della telecamera.
    Va mostrata solo nelle inquadrature «sullo schermo». Restituisce l'empty da accendere e spegnere."""
    g = empty('CorniceREC', (0, 0, -dist), cam, coll)
    w = sensor / lens * dist; h = w * aspect[1] / aspect[0]            # sensore adattato in larghezza (sensor_fit AUTO in verticale -> altezza)
    w, h = w * aspect[0] / aspect[1], w                                # in verticale Blender adatta il sensore all'altezza
    mw = material('P18_rec_bianco', (1, 1, 1), rough=0.5, emit=(1, 1, 1), emit_strength=1.2)
    t = 0.004 * dist / 0.6; L = 0.06 * dist / 0.6; mx, my = w / 2 * 0.86, h / 2 * 0.9
    for sx in (-1, 1):
        for sy in (-1, 1):
            obj('RecAngoloH', set004.box_c(), (sx * (mx - L / 2), sy * my, 0), (L, t, 0.0005), mw, coll, parent=g)
            obj('RecAngoloV', set004.box_c(), (sx * mx, sy * (my - L / 2), 0), (t, L, 0.0005), mw, coll, parent=g)
    ball_('RecPallino', 0.012 * dist / 0.6, (-mx + 0.03 * dist / 0.6, my - 0.035 * dist / 0.6, 0), M['led'], coll, parent=g)
    a = testo(coll, 'RecScritta', 'REC', 0.028 * dist / 0.6, mw, (-mx + 0.05 * dist / 0.6, my - 0.046 * dist / 0.6, 0), font=font, parent=g, rot=(0, 0, 0), spessore=0)
    b = testo(coll, 'RecNome', nome, 0.026 * dist / 0.6, mw, (mx - 0.14 * dist / 0.6, -my + 0.025 * dist / 0.6, 0), font=font, parent=g, rot=(0, 0, 0), spessore=0)
    return g


def caschetto(coll, M, head, z=0.55):
    """caschetto giallo da cantiere sulla testa di Pippo (figlio della testa, HEAD_C = 0.27)."""
    g = empty('Caschetto', (0, 0, z), head, coll)
    ball_('CaschettoCalotta', 1.0, (0, 0, 0), M['yellow'], coll, parent=g, sc=(0.39, 0.36, 0.25))
    cyl('CaschettoTesa', 0.44, 0.03, (0, -0.04, -0.03), M['yellow'], coll, parent=g)
    obj('CaschettoCresta', set004.box_c(), (0, 0, 0.2), (0.06, 0.5, 0.06), M['yellow'], coll, parent=g)
    return g


def tazza(coll, M, parent, loc=(0, -0.08, -0.1)):
    g = empty('Tazza', loc, parent, coll)
    cyl('TazzaCorpo', 0.06, 0.12, (0, 0, 0), M['white'], coll, parent=g); cyl('TazzaCaffe', 0.052, 0.005, (0, 0, 0.058), M['cabwood'], coll, parent=g)
    return g
