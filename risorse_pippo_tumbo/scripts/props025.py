"""Oggetti del video 025 «Martina nel water» (copione n. 22, versione 4).
- mats025(): materiali.
- scarafaggio(coll, M, tipo='B1', L=0.35, nome='Martina'): Martina, scarafaggio nello stile di Tumbo (ellissoidi, occhioni).
  B1 cartoon lucido con le ciglia, B2 quasi vero (scudo col bordo chiaro, zampe con le spine), B3 paffuta.
  Fronte -Y, origine a terra sotto il corpo. Restituisce dict: root, corpo, testa, occhi [L, R], antenne [L, R] (perni),
  zampe (6 perni: ant/med/post x sinistra/destra), L.
- ciambella(coll, M, R, font, testo='MARTINA'): salvagente col nome. Origine al centro, asse Z.
- ciabatta(coll, M, tipo='C1', L=0.34): C1 pantofola a quadri chiusa, C2 ciabatta da piscina. Punta verso -Y, origine sotto il centro.
- occhiali(coll, M, parent, loc, s): occhiali da sole minuscoli.
- water(coll, M, nome='Water'): water fatto a mano con la tazza aperta e l'acqua; restituisce dict root, acqua (quota), sedile, coperchio.
- bagno(coll, M, A, tipo='W1', x0=0, font=None): bagno di Pippo (pareti piastrellate, pavimento, water, lavandino, vasca, scaffale col manuale
  del tango). W1 piastrelle bianche moderne, W2 bagno della nonna (verde e rosa). Restituisce dict: root, water (dict), centro."""
import math
import bpy
from mathutils import Vector, Matrix
from common import material, empty, shape, shared_mesh
from set004 import obj, cyl, ball_, box_c
import props023, props024

PI = math.pi


def mats025():
    M = {}
    M['occhio'] = material('M25_occhio', (1, 1, 1), rough=0.25)
    M['pupilla'] = material('M25_pupilla', (0.01, 0.01, 0.015), rough=0.1)
    M['luce'] = material('M25_luce', (1, 1, 1), rough=0.1, emit=(1, 1, 1), emit_strength=0.6)
    M['guance'] = material('M25_guance', (1.0, 0.35, 0.45), rough=0.6)
    M['bocca'] = material('M25_bocca', (0.25, 0.03, 0.04), rough=0.5)
    M['lente'] = material('M25_lente', (0.02, 0.02, 0.03), rough=0.05, spec=1.0, coat=1.0)
    M['oro'] = material('M25_oro', (1.0, 0.72, 0.2), rough=0.25, metallic=1.0)
    M['ciambella_r'] = material('M25_ciambella_rossa', (0.95, 0.12, 0.1), rough=0.3, coat=0.4)
    M['ciambella_b'] = material('M25_ciambella_bianca', (0.97, 0.97, 0.95), rough=0.3, coat=0.4)
    M['acqua'] = material('M25_acqua', (0.35, 0.65, 0.8), rough=0.03, spec=0.9, coat=0.6)
    M['ceramica'] = material('M25_ceramica', (0.96, 0.96, 0.95), rough=0.12, coat=0.6, coat_rough=0.05)
    M['cromo'] = material('M25_cromo', (0.85, 0.86, 0.88), rough=0.12, metallic=1.0)
    return M


_TIPI = {
    'B1': dict(corpo=(0.36, 0.13, 0.035), scudo=(0.42, 0.17, 0.05), bordo=None, zampe=(0.12, 0.05, 0.02), occhio=1.15, ciglia=True, guance=True,
               addome=(0.33, 0.54, 0.15), testa=(0.17, 0.15, 0.14), zampa_r=0.02, spine=False, alto=0.26),
    'B2': dict(corpo=(0.17, 0.065, 0.02), scudo=(0.2, 0.08, 0.025), bordo=(0.75, 0.55, 0.3), zampe=(0.1, 0.045, 0.02), occhio=0.85, ciglia=False, guance=False,
               addome=(0.3, 0.6, 0.12), testa=(0.14, 0.13, 0.12), zampa_r=0.016, spine=True, alto=0.22),
    'B3': dict(corpo=(0.55, 0.27, 0.07), scudo=(0.6, 0.32, 0.09), bordo=None, zampe=(0.22, 0.1, 0.04), occhio=1.35, ciglia=True, guance=True,
               addome=(0.4, 0.5, 0.21), testa=(0.21, 0.18, 0.17), zampa_r=0.026, spine=False, alto=0.2),
}


def _curva(nome, pts, r, mat, coll, parent=None):
    cu = bpy.data.curves.new(nome, 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = r; cu.bevel_resolution = 3; cu.use_fill_caps = True
    sp = cu.splines.new('BEZIER'); sp.bezier_points.add(len(pts) - 1)
    for p, q in zip(sp.bezier_points, pts):
        p.co = q; p.handle_left_type = p.handle_right_type = 'AUTO'
    o = bpy.data.objects.new(nome, cu); coll.objects.link(o); o.parent = parent; cu.materials.append(mat)
    return o


def scarafaggio(coll, M, tipo='B1', L=0.35, nome='Martina'):
    T = _TIPI[tipo]; s = L
    mc = material('M25_%s_corpo_%s' % (nome, tipo), T['corpo'], rough=0.22, spec=0.7, coat=0.8, coat_rough=0.08)
    ms = material('M25_%s_scudo_%s' % (nome, tipo), T['scudo'], rough=0.25, spec=0.7, coat=0.7)
    mz = material('M25_%s_zampe_%s' % (nome, tipo), T['zampe'], rough=0.4, coat=0.3)
    R = empty(nome, (0, 0, 0), None, coll); out = {'root': R, 'L': L}
    C = empty(nome + 'Corpo', (0, 0, T['alto'] * s), R, coll); out['corpo'] = C
    ax, ay, az = T['addome']
    ball_(nome + 'Addome', 1.0, (0, 0.12 * s, 0.0), mc, coll, parent=C, sc=(ax * s, ay * s, az * s))
    obj(nome + 'Cucitura', box_c(), (0, 0.12 * s, az * s * 0.97), (0.006 * s, ay * s * 1.6, 0.01 * s), mz, coll, parent=C)
    ball_(nome + 'Pancia', 1.0, (0, 0.12 * s, -0.035 * s), mz, coll, parent=C, sc=(ax * s * 0.85, ay * s * 0.9, az * s * 0.7))
    sc_ = ball_(nome + 'Scudo', 1.0, (0, -0.33 * s, 0.03 * s), ms, coll, parent=C, sc=(0.3 * s, 0.17 * s, 0.1 * s)); sc_.rotation_euler = (-0.25, 0, 0)
    if T['bordo']:
        mb = material('M25_%s_bordo' % nome, T['bordo'], rough=0.35, coat=0.5)
        b_ = ball_(nome + 'BordoScudo', 1.0, (0, -0.33 * s, 0.02 * s), mb, coll, parent=C, sc=(0.32 * s, 0.185 * s, 0.085 * s)); b_.rotation_euler = (-0.25, 0, 0)
    H = empty(nome + 'Testa', (0, -0.47 * s, 0.0), C, coll); out['testa'] = H
    tx, ty, tz = T['testa']
    ball_(nome + 'Capo', 1.0, (0, -0.02 * s, 0.0), ms, coll, parent=H, sc=(tx * s, ty * s, tz * s))
    eyes = []; k = T['occhio']
    for sx in (-1, 1):
        E = empty(nome + 'Occhio', (sx * 0.075 * s * k, -(ty + 0.0) * s * 0.85, 0.06 * s), H, coll); eyes.append(E)
        ball_(nome + 'Bianco', 1.0, (0, 0, 0), M['occhio'], coll, parent=E, sc=(0.068 * s * k, 0.04 * s * k, 0.078 * s * k))
        P_ = empty(nome + 'PupillaE', (0, -0.036 * s * k, 0), E, coll)
        ball_(nome + 'Pupilla', 1.0, (0, 0, 0), M['pupilla'], coll, parent=P_, sc=(0.04 * s * k, 0.018 * s * k, 0.048 * s * k))
        ball_(nome + 'Luce', 1.0, (-0.012 * s * k, -0.016 * s * k, 0.018 * s * k), M['luce'], coll, parent=P_, sc=(0.012 * s * k, 0.007 * s * k, 0.013 * s * k))
        if T['ciglia']:
            for j in (-1, 0, 1):
                a = Vector((j * 0.025 * s * k + sx * 0.012 * s * k, -0.01 * s * k, 0.07 * s * k))
                b = a + Vector(((j + sx) * 0.012 * s * k, -0.012 * s * k, 0.035 * s * k))
                props023.tubo(nome + 'Ciglio', a, b, 0.003 * s * k, M['pupilla'], coll, parent=E)
        if T['guance']:
            ball_(nome + 'Guancia', 1.0, (sx * 0.11 * s * k, -(ty) * s * 0.7, -0.03 * s), M['guance'], coll, parent=H, sc=(0.03 * s, 0.012 * s, 0.02 * s))
    out['occhi'] = eyes
    me = props024.anello(nome + 'Sorriso', 0.035 * s, 0.006 * s, M['bocca'], coll, parent=H, loc=(0, -(ty + 0.004) * s, -0.05 * s))
    me.rotation_euler = (PI / 2, 0, 0); me.scale = (1.0, 0.55, 1.0)
    ant = []
    for sx in (-1, 1):
        A_ = empty(nome + 'Antenna', (sx * 0.04 * s, -(ty + 0.0) * s * 0.75, 0.1 * s), H, coll); ant.append(A_)
        pts = [Vector((0, 0, 0)), Vector((sx * 0.08 * s, -0.18 * s, 0.22 * s)), Vector((sx * 0.22 * s, -0.25 * s, 0.38 * s)), Vector((sx * 0.38 * s, -0.12 * s, 0.46 * s))]
        _curva(nome + 'Filo', pts, 0.006 * s, mz, coll, parent=A_)
    out['antenne'] = ant
    zampe = []
    for j, (yy, out_, fw) in enumerate(((-0.27, 0.36, -0.22), (-0.02, 0.42, 0.0), (0.24, 0.46, 0.3))):
        for sx in (-1, 1):
            Z = empty(nome + 'Zampa', (sx * 0.11 * s, yy * s, -0.04 * s), C, coll); zampe.append(Z)
            k_ = Vector((sx * out_ * 0.62 * s, fw * 0.55 * s, 0.07 * s)); f_ = Vector((sx * out_ * s, fw * s, -T['alto'] * s + 0.006 * s))
            props023.tubo(nome + 'Femore', Vector((0, 0, 0)), k_, T['zampa_r'] * s * 1.2, mz, coll, parent=Z)
            props023.tubo(nome + 'Tibia', k_, f_, T['zampa_r'] * s, mz, coll, parent=Z)
            ball_(nome + 'Ginocchio', T['zampa_r'] * s * 1.3, k_, mz, coll, parent=Z)
            if T['spine']:
                for u in (0.3, 0.55, 0.8):
                    p = k_.lerp(f_, u); d = (f_ - k_).normalized(); n = Vector((sx * 0.6, 0, 0.8)).normalized()
                    props023.tubo(nome + 'Spina', p, p + (n * 0.035 - d * 0.01) * s, 0.004 * s, mz, coll, parent=Z)
    out['zampe'] = zampe
    if tipo == 'B2':
        for sx in (-1, 1): props023.tubo(nome + 'Cerco', Vector((sx * 0.05 * s, 0.6 * s, 0.0)), Vector((sx * 0.1 * s, 0.75 * s, 0.03 * s)), 0.008 * s, mz, coll, parent=C)
    return out


def ciambella(coll, M, R, font, testo='MARTINA', nome='Ciambella'):
    O = empty(nome, (0, 0, 0), None, coll)
    n = 8
    for k in range(n):                                                 # spicchi rossi e bianchi
        a0 = 2 * PI * k / n
        seg = props024.anello(nome + 'Spicchio', R, R * 0.36, M['ciambella_r'] if k % 2 == 0 else M['ciambella_b'], coll, parent=O, seg=40, segr=12)
        me = seg.data; import bmesh
        bm = bmesh.new(); bm.from_mesh(me)
        dele = [f for f in bm.faces if not (a0 <= (math.atan2(f.calc_center_median().y, f.calc_center_median().x) % (2 * PI)) < a0 + 2 * PI / n)]
        bmesh.ops.delete(bm, geom=dele, context='FACES'); bm.to_mesh(me); bm.free()
    r = R * 0.36; beta = math.radians(48); n = len(testo); passo = 0.3
    for k, ch in enumerate(testo):                                     # lettere stampate sul davanti, lungo l'arco (come sui salvagenti)
        a = -PI / 2 + (k - (n - 1) / 2) * passo
        ca, sa, cb, sb = math.cos(a), math.sin(a), math.cos(beta), math.sin(beta)
        pos = Vector(((R + r * cb) * ca, (R + r * cb) * sa, r * sb)) * 1.0
        nz = Vector((cb * ca, cb * sa, sb)); tx = Vector((-sa, ca, 0.0)); ty = nz.cross(tx)
        rotm = Matrix((tx, ty, nz)).transposed()
        L_ = props023.testo(coll, nome + 'Lettera', ch, r * 1.15, M['pupilla'], tuple(pos + nz * 0.002), rot=(0, 0, 0), parent=O, font=font, estrudi=r * 0.05)
        L_.data.align_x = 'CENTER'; L_.data.align_y = 'CENTER'; L_.rotation_euler = rotm.to_euler()
    return O


def ciabatta(coll, M, tipo='C1', L=0.34, nome='Ciabatta'):
    O = empty(nome, (0, 0, 0), None, coll)
    if tipo == 'C1':                                                   # pantofola chiusa a quadri, suola di gomma
        mq = material('M25_quadri', (0.15, 0.25, 0.55), rough=0.9)
        try:
            nt = mq.node_tree; b = nt.nodes['Principled BSDF']
            ch = nt.nodes.new('ShaderNodeTexChecker'); ch.inputs['Scale'].default_value = 16.0
            ch.inputs['Color1'].default_value = (0.06, 0.1, 0.3, 1); ch.inputs['Color2'].default_value = (0.4, 0.05, 0.05, 1)
            nt.links.new(ch.outputs['Color'], b.inputs['Base Color'])
        except Exception as e: print('quadri', e)
        msu = material('M25_suola', (0.25, 0.17, 0.1), rough=0.7)
        props024.scatola_tonda(nome + 'Suola', 0.38 * L, L, 0.07 * L, 0.15 * L, msu, coll, O, (0, 0, 0.035 * L))
        ball_(nome + 'Tomaia', 1.0, (0, -0.14 * L, 0.07 * L), mq, coll, parent=O, sc=(0.205 * L, 0.36 * L, 0.15 * L))
        ball_(nome + 'Apertura', 1.0, (0, 0.08 * L, 0.115 * L), material('M25_fodera', (0.05, 0.04, 0.04), rough=0.9), coll, parent=O, sc=(0.13 * L, 0.16 * L, 0.06 * L))
        props024.anello(nome + 'Bordo', 0.14 * L, 0.03 * L, material('M25_pelo', (0.92, 0.88, 0.8), rough=1.0), coll, parent=O, loc=(0, 0.08 * L, 0.14 * L)).scale = (0.95, 1.15, 0.6)
        ball_(nome + 'Tallone', 1.0, (0, 0.38 * L, 0.08 * L), mq, coll, parent=O, sc=(0.18 * L, 0.1 * L, 0.06 * L))
        ball_(nome + 'Pompon', 1.0, (0, -0.32 * L, 0.18 * L), material('M25_pompon', (0.9, 0.85, 0.75), rough=1.0), coll, parent=O, sc=(0.06 * L, 0.06 * L, 0.05 * L))
    else:                                                              # ciabatta da piscina: suola larga, fascia sola
        mbl = material('M25_ciabatta_blu', (0.05, 0.25, 0.75), rough=0.45, coat=0.3)
        mwh = material('M25_ciabatta_bianca', (0.95, 0.95, 0.95), rough=0.45)
        props024.scatola_tonda(nome + 'Suola', 0.4 * L, L, 0.09 * L, 0.18 * L, mbl, coll, O, (0, 0, 0.045 * L))
        props024.scatola_tonda(nome + 'Sottosuola', 0.41 * L, L * 1.01, 0.025 * L, 0.18 * L, mwh, coll, O, (0, 0, 0.0125 * L))
        f = props024.anello(nome + 'Fascia', 0.21 * L, 0.06 * L, mbl, coll, parent=O, loc=(0, -0.12 * L, 0.09 * L))
        f.rotation_euler = (PI / 2, 0, 0); f.scale = (1.0, 0.75, 1.6)
        for sx in (-1, 1): obj(nome + 'Riga', box_c(), (sx * 0.06 * L, -0.12 * L, 0.2 * L), (0.025 * L, 0.2 * L, 0.01 * L), mwh, coll, parent=O)
    return O


def occhiali(coll, M, parent, loc, s, nome='Occhiali'):
    O = empty(nome, loc, parent, coll)
    for sx in (-1, 1):
        ball_(nome + 'Lente', 1.0, (sx * 0.06 * s, 0, 0), M['lente'], coll, parent=O, sc=(0.05 * s, 0.012 * s, 0.038 * s))
    obj(nome + 'Ponte', box_c(), (0, 0, 0.01 * s), (0.04 * s, 0.01 * s, 0.008 * s), M['pupilla'], coll, parent=O)
    return O


def water(coll, M, nome='Water'):
    """water a scala Pippo (tavoletta a 0,585 m) con la tazza davvero cava (la camera puo' stare dentro): acqua a 0,43 m,
    tavoletta, coperchio alzato, cassetta col pulsante. Restituisce dict root, tazza, acqua, quota, sedile, coperchio, pulsante."""
    O = empty(nome, (0, 0, 0), None, coll)
    prof = [(0.0, 0.0), (0.2, 0.0), (0.22, 0.05), (0.17, 0.2), (0.2, 0.36), (0.3, 0.5), (0.315, 0.545), (0.3, 0.565), (0.27, 0.566),
            (0.252, 0.54), (0.232, 0.5), (0.205, 0.45), (0.172, 0.4), (0.125, 0.345), (0.065, 0.305), (0.0, 0.295)]
    tz = props024.tornio(nome + 'Tazza', prof, coll, [M['ceramica']], seg=64, parent=O); tz.scale = (1.0, 1.25, 1.0)
    acqua = obj(nome + 'Acqua', shared_mesh('cyl:1:1'), (0, 0, 0.43), (0.196, 0.245, 0.004), M['acqua'], coll, parent=O)
    sed = props024.anello(nome + 'Tavoletta', 0.265, 0.033, M['ceramica'], coll, parent=O, loc=(0, 0.0, 0.585), seg=56, segr=10); sed.scale = (1.0, 1.24, 0.6)
    cop = props024.scatola_tonda(nome + 'Coperchio', 0.56, 0.04, 0.66, 0.2, M['ceramica'], coll, O, (0, 0.38, 0.9))
    props024.scatola_tonda(nome + 'Cassetta', 0.58, 0.22, 0.5, 0.05, M['ceramica'], coll, O, (0, 0.52, 0.9))
    pul = cyl(nome + 'Pulsante', 0.05, 0.02, (0, 0.52, 1.16), M['cromo'], coll, parent=O)
    return {'root': O, 'tazza': tz, 'acqua': acqua, 'quota': 0.43, 'sedile': sed, 'coperchio': cop, 'pulsante': pul}


def piastrelle(nome, colore, fuga, lato=0.3):
    """piastrelle quadrate procedurali in coordinate del mondo (non si stirano sulle scatole scalate): lato in metri."""
    m = bpy.data.materials.get(nome)
    if m: return m
    m = material(nome, colore, rough=0.15, coat=0.5, coat_rough=0.08); nt = m.node_tree; b = nt.nodes['Principled BSDF']
    tc = nt.nodes.new('ShaderNodeTexCoord'); br = nt.nodes.new('ShaderNodeTexBrick')
    br.offset = 0.0; br.squash = 1.0; br.inputs['Scale'].default_value = 1.0 / lato
    br.inputs['Brick Width'].default_value = 1.0; br.inputs['Row Height'].default_value = 1.0; br.inputs['Mortar Size'].default_value = 0.02
    br.inputs['Color1'].default_value = (*colore, 1); br.inputs['Color2'].default_value = (*[c * 0.94 for c in colore], 1); br.inputs['Mortar'].default_value = (*fuga, 1)
    # le pareti stanno in piani verticali: si usa x+y come prima coordinata e z come seconda
    sep = nt.nodes.new('ShaderNodeSeparateXYZ'); comb = nt.nodes.new('ShaderNodeCombineXYZ'); add = nt.nodes.new('ShaderNodeMath'); add.operation = 'ADD'
    nt.links.new(tc.outputs['Object'], sep.inputs[0]); nt.links.new(sep.outputs['X'], add.inputs[0]); nt.links.new(sep.outputs['Y'], add.inputs[1])
    nt.links.new(add.outputs[0], comb.inputs['X']); nt.links.new(sep.outputs['Z'], comb.inputs['Y'])
    nt.links.new(comb.outputs[0], br.inputs['Vector']); nt.links.new(br.outputs['Color'], b.inputs['Base Color'])
    return m


def bagno(coll, M, A, tipo='W1', x0=0.0, font=None, nome='Bagno', chiuso=False):
    """bagno di 4 x 3,6 m (in scala Pippo), pareti su tre lati (dietro y=+1,8, ai lati x=±2); water contro il muro di fondo al centro."""
    O = empty(nome, (x0, 0, 0), None, coll)
    if tipo == 'W1':
        mp = piastrelle(nome + 'Muro', (0.93, 0.94, 0.95), (0.62, 0.64, 0.66), 0.3); mf = A.materiale('marble_tiles', dimensione=1.5)
    else:
        mp = piastrelle(nome + 'Muro', (0.42, 0.72, 0.55), (0.9, 0.88, 0.82), 0.22); mf = piastrelle(nome + 'Pav', (0.95, 0.62, 0.68), (0.85, 0.82, 0.78), 0.35)
    def box(n, p0, p1, m):
        o = obj(n, box_c(), ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2, (p0[2] + p1[2]) / 2), (p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]), m, coll, parent=O); return o
    box(nome + 'Pavimento', (-2.0, -2.2, -0.05), (2.0, 1.8, 0.0), mf)
    box(nome + 'Fondo', (-2.0, 1.8, 0.0), (2.0, 1.9, 3.6), mp)
    for sx in (-1, 1): box(nome + 'Lato', (sx * 2.0 - 0.05, -2.2, 0.0), (sx * 2.0 + 0.05, 1.9, 3.6), mp)
    W = water(coll, M, nome + 'Water'); W['root'].parent = O; W['root'].location = (0, 1.25, 0)
    out = {'root': O, 'water': W, 'centro': Vector((x0, 1.25, 0))}
    try:
        s_ = A.modello('kenney/furniture-kit/bathroomSink', posizione=(x0 + 1.25, 1.55, 0), altezza=1.25, collezione=coll, appoggia=True); s_.parent = O; s_.matrix_parent_inverse = O.matrix_world.inverted()
        b_ = A.modello('kenney/furniture-kit/bathtub', posizione=(x0 - 1.35, 0.6, 0), altezza=0.8, rotazione=90.0, collezione=coll, appoggia=True); b_.parent = O; b_.matrix_parent_inverse = O.matrix_world.inverted()
        m_ = A.modello('kenney/furniture-kit/bathroomMirror', posizione=(x0 + 1.25, 1.78, 1.75), altezza=0.9, collezione=coll, appoggia=False); m_.parent = O; m_.matrix_parent_inverse = O.matrix_world.inverted()
    except Exception as e: print('mobili bagno', e)
    mlegno = material('M25_mensola', (0.55, 0.35, 0.2), rough=0.6)
    box(nome + 'Mensola', (-0.9, 1.6, 1.85), (-0.2, 1.8, 1.89), mlegno)
    lib = props024.scatola_tonda(nome + 'Manuale', 0.07, 0.42, 0.55, 0.01, material('M25_libro', (0.8, 0.1, 0.15), rough=0.6), coll, O, (-0.55, 1.68, 2.17))
    if font: props023.testo(coll, nome + 'Titolo', 'TANGO', 0.075, M['occhio'], (-0.55, 1.46, 2.2), rot=(PI / 2, -PI / 2, 0), parent=O, font=font, estrudi=0.004)
    if chiuso:                                                         # soffitto, parete davanti con la porta, plafoniera
        ms = material('M25_soffitto', (0.95, 0.94, 0.9), rough=0.9)
        box(nome + 'Soffitto', (-2.05, -2.3, 3.6), (2.05, 1.9, 3.7), ms)
        box(nome + 'DavantiA', (-2.05, -2.3, 0.0), (-0.5, -2.2, 3.6), mp); box(nome + 'DavantiB', (0.5, -2.3, 0.0), (2.05, -2.2, 3.6), mp)
        box(nome + 'DavantiC', (-0.5, -2.3, 2.35), (0.5, -2.2, 3.6), mp)
        mpl = material('M25_plafoniera', (1, 1, 1), rough=0.3, emit=(1.0, 0.95, 0.85), emit_strength=6.0)
        ball_(nome + 'Plafoniera', 1.0, (0, 0.0, 3.6), mpl, coll, parent=O, sc=(0.32, 0.32, 0.07))
        out['soffitto'] = [o for o in O.children if o.name.startswith(nome + 'Soffitto') or o.name.startswith(nome + 'Davanti') or o.name.startswith(nome + 'Plafoniera')]
    return out


# ============================== video 025: oggetti nuovi ==============================
def bottiglia(coll, M, font=None, H=0.14, nome='Crescitutto'):
    """flacone di concime aperto (indizio di Martina gigante): verde, etichetta gialla CRESCITUTTO. Asse Z, origine in basso al centro."""
    O = empty(nome, (0, 0, 0), None, coll)
    mv = material('M25_flacone', (0.1, 0.7, 0.15), rough=0.25, coat=0.6); me_ = material('M25_etichetta', (1.0, 0.85, 0.1), rough=0.5)
    prof = [(0.0, 0.0), (0.33 * H, 0.0), (0.35 * H, 0.04 * H), (0.35 * H, 0.62 * H), (0.3 * H, 0.72 * H), (0.12 * H, 0.82 * H), (0.11 * H, 0.95 * H),
            (0.095 * H, 0.95 * H), (0.0, 0.9 * H)]
    props024.tornio(nome + 'Corpo', prof, coll, [mv, me_], seg=40, parent=O, mat_idx=lambda z: 1 if 0.14 * H < z < 0.56 * H else 0)
    if font:
        t = props023.testo(coll, nome + 'Scritta', 'CRESCI\nTUTTO', 0.13 * H, M['pupilla'], (0, -0.356 * H, 0.35 * H), parent=O, font=font, estrudi=0.004 * H)
        t.data.space_line = 0.85
    mg = material('M25_concime', (0.3, 1.0, 0.2), rough=0.1, emit=(0.3, 1.0, 0.2), emit_strength=1.2)
    ball_(nome + 'Goccia', 1.0, (0, 0.0, 0.97 * H), mg, coll, parent=O, sc=(0.07 * H, 0.07 * H, 0.05 * H))
    return O


def bicchiere(coll, M, h=0.06, nome='Drink'):
    """bicchiere da cocktail con cannuccia e ombrellino, origine sotto il fondo."""
    O = empty(nome, (0, 0, 0), None, coll)
    mv = material('M25_vetro_drink2', (0.75, 0.9, 1.0), rough=0.05, spec=1.0, coat=1.0, emit=(0.3, 0.5, 0.6), emit_strength=0.1)
    ml = material('M25_succo', (1.0, 0.45, 0.05), rough=0.15, emit=(1.0, 0.4, 0.05), emit_strength=0.4)
    props024.tornio(nome + 'Vetro', [(0, 0), (0.2 * h, 0), (0.22 * h, 0.05 * h), (0.32 * h, h), (0.3 * h, h * 0.99)], coll, [mv], seg=24, parent=O)
    props024.tornio(nome + 'Succo', [(0, 0.06 * h), (0.21 * h, 0.06 * h), (0.29 * h, 0.85 * h), (0.0, 0.85 * h)], coll, [ml], seg=24, parent=O)
    props023.tubo(nome + 'Cannuccia', Vector((0.05 * h, 0, 0.3 * h)), Vector((0.12 * h, 0.02 * h, 1.45 * h)), 0.025 * h, material('M25_cannuccia', (0.95, 0.1, 0.4), rough=0.4), coll, parent=O)
    props023.tubo(nome + 'Stecco', Vector((-0.08 * h, 0, 0.7 * h)), Vector((-0.2 * h, 0, 1.5 * h)), 0.012 * h, material('M25_stecco', (0.9, 0.8, 0.6), rough=0.6), coll, parent=O)
    u = shape(nome + 'Ombrellino', 'cone', (-0.2 * h, 0, 1.42 * h), (0.45 * h, 0.45 * h, 0.18 * h), parent=O, mat=material('M25_ombrellino', (0.2, 0.75, 0.95), rough=0.5), coll=coll)
    return O


def rosa(coll, L=0.3, nome='Rosa'):
    """rosa rossa: gambo lungo X (si tiene tra i denti o nella proboscide), fiore all'estremita' +X. Origine a meta' gambo."""
    O = empty(nome, (0, 0, 0), None, coll)
    mv = material('M25_gambo', (0.1, 0.45, 0.08), rough=0.6); mr = material('M25_petali', (0.85, 0.02, 0.07), rough=0.45, coat=0.3)
    props023.tubo(nome + 'Gambo', Vector((-L / 2, 0, 0)), Vector((L / 2, 0, 0)), 0.006, mv, coll, parent=O)
    F = empty(nome + 'Fiore', (L / 2 + 0.03, 0, 0), O, coll)
    ball_(nome + 'Bocciolo', 1.0, (0, 0, 0), mr, coll, parent=F, sc=(0.035, 0.03, 0.03))
    for k in range(6):
        a = k * PI / 3
        p = ball_(nome + 'Petalo', 1.0, (0.005, 0.028 * math.cos(a), 0.028 * math.sin(a)), mr, coll, parent=F, sc=(0.03, 0.022, 0.022))
    for sx in (-0.08, 0.04):
        ball_(nome + 'Foglia', 1.0, (sx, 0.0, 0.018), mv, coll, parent=O, sc=(0.03, 0.012, 0.012))
    return O


def prezzo(coll, M, font, testo='9,99 €', nome='Prezzo'):
    """cartellino del prezzo appeso a un filo (origine in cima al filo), faccia verso -Y."""
    O = empty(nome, (0, 0, 0), None, coll)
    props023.tubo(nome + 'Filo', Vector((0, 0, 0)), Vector((0, 0, -0.25)), 0.004, M['pupilla'], coll, parent=O)
    props024.scatola_tonda(nome + 'Carta', 0.42, 0.01, 0.22, 0.03, material('M25_carta_prezzo', (1.0, 0.97, 0.88), rough=0.7), coll, O, (0, 0, -0.36))
    if font: props023.testo(coll, nome + 'Testo', testo, 0.12, material('M25_rosso_prezzo', (0.85, 0.05, 0.05), rough=0.5), (0, -0.008, -0.365), parent=O, font=font, estrudi=0.003)
    return O


def mat_vortice(nome='M25_vortice'):
    m = bpy.data.materials.get(nome)
    if m: return m
    m = material(nome, (0.3, 0.6, 0.78), rough=0.05, spec=0.9, coat=0.5); nt = m.node_tree; b = nt.nodes['Principled BSDF']
    tc = nt.nodes.new('ShaderNodeTexCoord'); sp = nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(tc.outputs['Object'], sp.inputs[0])
    at = nt.nodes.new('ShaderNodeMath'); at.operation = 'ARCTAN2'; nt.links.new(sp.outputs['Y'], at.inputs[0]); nt.links.new(sp.outputs['X'], at.inputs[1])
    cb = nt.nodes.new('ShaderNodeCombineXYZ'); nt.links.new(sp.outputs['X'], cb.inputs['X']); nt.links.new(sp.outputs['Y'], cb.inputs['Y'])
    ln = nt.nodes.new('ShaderNodeVectorMath'); ln.operation = 'LENGTH'; nt.links.new(cb.outputs[0], ln.inputs[0])
    m1 = nt.nodes.new('ShaderNodeMath'); m1.operation = 'MULTIPLY'; m1.inputs[1].default_value = 3.0 / (2 * PI); nt.links.new(at.outputs[0], m1.inputs[0])
    m2 = nt.nodes.new('ShaderNodeMath'); m2.operation = 'MULTIPLY'; m2.inputs[1].default_value = 14.0; nt.links.new(ln.outputs['Value'], m2.inputs[0])
    ad = nt.nodes.new('ShaderNodeMath'); ad.operation = 'ADD'; nt.links.new(m1.outputs[0], ad.inputs[0]); nt.links.new(m2.outputs[0], ad.inputs[1])
    fr_ = nt.nodes.new('ShaderNodeMath'); fr_.operation = 'FRACT'; nt.links.new(ad.outputs[0], fr_.inputs[0])
    rp = nt.nodes.new('ShaderNodeValToRGB'); rp.color_ramp.interpolation = 'EASE'
    rp.color_ramp.elements[0].position = 0.35; rp.color_ramp.elements[0].color = (0.18, 0.45, 0.62, 1)
    rp.color_ramp.elements[1].position = 0.75; rp.color_ramp.elements[1].color = (0.92, 0.97, 1.0, 1)
    nt.links.new(fr_.outputs[0], rp.inputs['Fac']); nt.links.new(rp.outputs['Color'], b.inputs['Base Color'])
    b.inputs['Emission Color'].default_value = (0.5, 0.7, 0.85, 1); b.inputs['Emission Strength'].default_value = 0.25
    return m


def vortice(coll, R=0.2, P=0.16, nome='Vortice'):
    """imbuto d'acqua che gira (lo sciacquone): bordo largo R in alto a z=0, fondo a -P. Si fa girare con rotation_euler.z."""
    prof = [(R, 0.0), (R * 0.82, -0.012), (R * 0.62, -0.03), (R * 0.42, -0.06), (R * 0.26, -0.095), (R * 0.13, -0.13), (R * 0.05, -P + 0.01), (0.0, -P)]
    return props024.tornio(nome, prof, coll, [mat_vortice()], seg=56)


def mat_getto(nome='M25_getto'):
    m = bpy.data.materials.get(nome)
    if m: return m
    m = material(nome, (0.72, 0.88, 1.0), rough=0.12, spec=0.8, coat=0.5, emit=(0.55, 0.78, 1.0), emit_strength=0.45); nt = m.node_tree; b = nt.nodes['Principled BSDF']
    ge = nt.nodes.new('ShaderNodeNewGeometry'); nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 0.6; nz.inputs['Detail'].default_value = 6
    nt.links.new(ge.outputs['Position'], nz.inputs['Vector'])
    rp = nt.nodes.new('ShaderNodeValToRGB'); rp.color_ramp.elements[0].position = 0.42; rp.color_ramp.elements[0].color = (0.35, 0.65, 0.9, 1)
    rp.color_ramp.elements[1].position = 0.62; rp.color_ramp.elements[1].color = (0.97, 0.99, 1.0, 1)
    nt.links.new(nz.outputs['Fac'], rp.inputs['Fac']); nt.links.new(rp.outputs['Color'], b.inputs['Base Color'])
    bm = nt.nodes.new('ShaderNodeBump'); bm.inputs['Strength'].default_value = 0.6; nt.links.new(nz.outputs['Fac'], bm.inputs['Height']); nt.links.new(bm.outputs['Normal'], b.inputs['Normal'])
    return m


def geyser(coll, R=1.0, nome='Geyser', anelli=40):
    """colonna d'acqua alta 1 (si allunga con scale.z del root), con l'acqua che sale (modificatore Displace guidato da un empty
    da spostare in su) e la spuma in cima (empty 'cima' da mettere in cima alla colonna). Restituisce dict root, colonna, scorre, cima."""
    O = empty(nome, (0, 0, 0), None, coll)
    prof = [(0.0, 0.0)] + [(R * (1.0 + 0.25 * (1 - k / anelli) ** 3), k / anelli) for k in range(anelli + 1)] + [(0.0, 1.0)]
    col = props024.tornio(nome + 'Colonna', prof, coll, [mat_getto()], seg=36, parent=O)
    sc = empty(nome + 'Scorre', (0, 0, 0), None, coll)
    tx = bpy.data.textures.new(nome + 'Turbolenza', 'CLOUDS'); tx.noise_scale = 0.9 * R; tx.noise_depth = 2
    md = col.modifiers.new('Turbolenza', 'DISPLACE'); md.texture = tx; md.texture_coords = 'OBJECT'; md.texture_coords_object = sc; md.strength = 0.55 * R; md.mid_level = 0.5
    C = empty(nome + 'Cima', (0, 0, 0), None, coll); ms = material('M25_spuma', (0.97, 0.99, 1.0), rough=0.4, emit=(0.8, 0.9, 1.0), emit_strength=0.5)
    for k in range(9):
        a = k * 2 * PI / 9
        ball_(nome + 'Spuma', 1.0, (1.05 * R * math.cos(a), 1.05 * R * math.sin(a), 0.2 * R * math.sin(3 * a)), ms, coll, parent=C, sc=(0.55 * R, 0.55 * R, 0.42 * R))
    ball_(nome + 'SpumaC', 1.0, (0, 0, 0.2 * R), ms, coll, parent=C, sc=(1.1 * R, 1.1 * R, 0.5 * R))
    return {'root': O, 'colonna': col, 'scorre': sc, 'cima': C}


def allagamento(coll, x0=-140, x1=140, y0=-140, y1=140, nome='Alluvione'):
    """piano d'acqua torbida con le increspature (da alzare con location.z). Restituisce (oggetto, nodo del rumore: chiave su inputs['W'])."""
    m = material('M25_alluvione', (0.13, 0.3, 0.33), rough=0.05, spec=0.8); nt = m.node_tree; b = nt.nodes['Principled BSDF']
    ge = nt.nodes.new('ShaderNodeNewGeometry'); mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (0.45, 0.45, 0.45)
    nt.links.new(ge.outputs['Position'], mp.inputs['Vector'])
    nz = nt.nodes.new('ShaderNodeTexNoise'); nz.noise_dimensions = '4D'; nz.inputs['Scale'].default_value = 1.2; nz.inputs['Detail'].default_value = 5
    nt.links.new(mp.outputs['Vector'], nz.inputs['Vector'])
    bm = nt.nodes.new('ShaderNodeBump'); bm.inputs['Strength'].default_value = 0.45; bm.inputs['Distance'].default_value = 0.4
    nt.links.new(nz.outputs['Fac'], bm.inputs['Height']); nt.links.new(bm.outputs['Normal'], b.inputs['Normal'])
    rp = nt.nodes.new('ShaderNodeValToRGB'); rp.color_ramp.elements[0].position = 0.45; rp.color_ramp.elements[0].color = (0.1, 0.26, 0.3, 1)
    rp.color_ramp.elements[1].position = 0.72; rp.color_ramp.elements[1].color = (0.42, 0.6, 0.6, 1)
    nt.links.new(nz.outputs['Fac'], rp.inputs['Fac']); nt.links.new(rp.outputs['Color'], b.inputs['Base Color'])
    o = obj(nome, box_c(), ((x0 + x1) / 2, (y0 + y1) / 2, -0.5), (x1 - x0, y1 - y0, 1.0), m, coll)
    return o, nz


def carta_parati(nome, c1, c2, passo=0.2):
    """carta da parati a righe verticali, in coordinate del mondo (non si stira sulle scatole scalate)."""
    m = bpy.data.materials.get(nome)
    if m: return m
    m = material(nome, c1, rough=0.85); nt = m.node_tree; b = nt.nodes['Principled BSDF']
    ge = nt.nodes.new('ShaderNodeNewGeometry'); sp = nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(ge.outputs['Position'], sp.inputs[0])
    ad = nt.nodes.new('ShaderNodeMath'); ad.operation = 'ADD'; nt.links.new(sp.outputs['X'], ad.inputs[0]); nt.links.new(sp.outputs['Y'], ad.inputs[1])
    dv = nt.nodes.new('ShaderNodeMath'); dv.operation = 'DIVIDE'; dv.inputs[1].default_value = passo; nt.links.new(ad.outputs[0], dv.inputs[0])
    fr_ = nt.nodes.new('ShaderNodeMath'); fr_.operation = 'FRACT'; nt.links.new(dv.outputs[0], fr_.inputs[0])
    rp = nt.nodes.new('ShaderNodeValToRGB'); rp.color_ramp.interpolation = 'CONSTANT'
    rp.color_ramp.elements[0].position = 0.0; rp.color_ramp.elements[0].color = (*c1, 1)
    rp.color_ramp.elements[1].position = 0.55; rp.color_ramp.elements[1].color = (*c2, 1)
    nt.links.new(fr_.outputs[0], rp.inputs['Fac']); nt.links.new(rp.outputs['Color'], b.inputs['Base Color'])
    return m


def salotto(coll, M, A, x0=0.0, font=None, nome='Salotto', H=4.2):
    """salotto di Pippo, 7 x 5,7 m: pavimento di legno, carta da parati a righe, battiscopa, divano contro il muro di fondo (y=+2,5),
    mobile con la TV sulla destra, lampada, pianta, quadro, porta a sinistra. Davanti (y=-3,2) e' aperto per la camera.
    Restituisce dict root, divano (Vector della seduta), centro, oggetti (lista di quelli da nascondere)."""
    O = empty(nome, (x0, 0, 0), None, coll)
    def box(n, p0, p1, m):
        return obj(n, box_c(), ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2, (p0[2] + p1[2]) / 2), (p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]), m, coll, parent=O)
    try: mfl = A.materiale('laminate_floor_02', dimensione=1.4)
    except Exception: mfl = material('M25_legno', (0.55, 0.36, 0.2), rough=0.5)
    mw = carta_parati('M25_carta_parati', (0.96, 0.84, 0.55), (0.9, 0.62, 0.42), 0.24)
    mb = material('M25_battiscopa', (0.97, 0.96, 0.92), rough=0.5)
    box(nome + 'Pavimento', (-3.5, -8.0, -0.05), (3.5, 2.5, 0.0), mfl)          # lungo davanti: le camere larghe stanno fuori dalla stanza
    box(nome + 'Fondo', (-3.62, 2.5, 0.0), (3.62, 2.62, H), mw); box(nome + 'Destra', (3.5, -3.2, 0.0), (3.62, 2.5, H), mw)
    box(nome + 'SxA', (-3.62, 0.2, 0.0), (-3.5, 2.5, H), mw); box(nome + 'SxB', (-3.62, -3.2, 0.0), (-3.5, -1.0, H), mw)
    box(nome + 'SxC', (-3.62, -1.0, 2.6), (-3.5, 0.2, H), mw)
    box(nome + 'BattiscopaF', (-3.5, 2.44, 0.0), (3.5, 2.5, 0.14), mb); box(nome + 'BattiscopaD', (3.44, -3.2, 0.0), (3.5, 2.5, 0.14), mb)
    for p0, p1 in (((-3.56, -1.08, 0.0), (-3.44, -0.92, 2.68)), ((-3.56, 0.12, 0.0), (-3.44, 0.28, 2.68)), ((-3.56, -1.08, 2.6), (-3.44, 0.28, 2.72))):
        box(nome + 'Stipite', p0, p1, mb)
    def kn(aid, pos, h, rot=0.0):
        try:
            o = A.modello('kenney/furniture-kit/' + aid, posizione=(x0 + pos[0], pos[1], pos[2]), altezza=h, rotazione=rot, collezione=coll, appoggia=True)
            o.parent = O; o.matrix_parent_inverse = O.matrix_world.inverted(); return o
        except Exception as e: print('salotto', aid, e)
    kn('loungeSofa', (0.2, 1.95, 0.0), 1.15)
    kn('cabinetTelevision', (3.1, 0.2, 0.0), 0.75, -90.0)
    kn('televisionModern', (3.15, 0.2, 0.75), 0.9, -90.0)
    kn('lampRoundFloor', (2.7, 2.05, 0.0), 2.1)
    kn('pottedPlant', (-2.8, 2.0, 0.0), 1.5)
    kn('sideTable', (-1.55, 2.0, 0.0), 0.65)
    mq = material('M25_cornice', (0.35, 0.2, 0.08), rough=0.5); mt = material('M25_tela', (0.25, 0.55, 0.85), rough=0.8)
    box(nome + 'Cornice', (-0.85, 2.44, 1.75), (1.25, 2.5, 2.95), mq); box(nome + 'Tela', (-0.75, 2.43, 1.85), (1.15, 2.45, 2.85), mt)
    ms = material('M25_sole_quadro', (1.0, 0.85, 0.2), rough=0.6); ball_(nome + 'SoleQuadro', 1.0, (0.65, 2.425, 2.55), ms, coll, parent=O, sc=(0.16, 0.01, 0.16))
    mg = material('M25_prato_quadro', (0.25, 0.65, 0.2), rough=0.8); box(nome + 'PratoQuadro', (-0.75, 2.42, 1.85), (1.15, 2.425, 2.15), mg)
    msf = material('M25_soffitto_sal', (0.96, 0.95, 0.92), rough=0.9)
    sof = box(nome + 'Soffitto', (-3.62, -3.3, H), (3.62, 2.62, H + 0.1), msf)
    mpl = material('M25_plafoniera_sal', (1, 1, 1), rough=0.3, emit=(1.0, 0.95, 0.85), emit_strength=5.0)
    lamp = ball_(nome + 'Lampadario', 1.0, (0.2, -0.3, H), mpl, coll, parent=O, sc=(0.45, 0.45, 0.09))
    return {'root': O, 'divano': Vector((x0 + 0.2, 1.85, 0.575)), 'centro': Vector((x0, 0, 0)), 'soffitto': [sof, lamp]}
