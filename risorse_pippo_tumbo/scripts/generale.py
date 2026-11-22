"""Il Generale: nuovo politico della serie (22 novembre 2026), chiesto dall'autore: politico ultra di destra, alto 1,90 m,
capelli castano scuro con la forma di quelli di Cappellone (a spazzola), fronte ampia, mascella pronunciata, orecchie grandi,
vestito sempre da generale. Personaggio INVENTATO: faccia, uniforme, gradi e medaglie sono di fantasia (nessuna divisa,
stemma o grado di un esercito vero), non e' e non deve diventare il ritratto di una persona reale.
    import generale as gn
    G = gn.generale(coll, stile='A')            # 'A' uniforme da gala verde oliva, 'B' parata blu notte con fascia, 'C' mimetica col basco
    gn.faccia(G, f, brow=0, brow_lift=0, smile=0, mouth_open=0, look=(0, 0), lid=0)     # stessa bocca a D di Cappellone quando parla
    gn.emozione(G, f, 'severo')                 # una delle EMOZIONI
    gn.gesto(G, f, 'saluto militare')           # uno dei GESTI
    gn.berretto(G, f, True)                     # il berretto si puo' togliere
Fronte -Y, piedi a z = 0. Alto circa 190 cm con Pippo = 175 cm (2,30 unita') -> 2,50 unita' (SCALA sulla radice).
Dizionario: root, body, head, shoulderL/R, hipL/R, browL/R, pupilL/R, lidL/R, mouth_curve, mouth_base, mouth_obj, mouth_open, cap, mats."""
import math, bpy
from mathutils import Vector
from common import material, shape, empty
import set004
PI = math.pi
HC = 1.72                                                                    # centro della testa (prima della scala)
STILI = ('A', 'B', 'C')
FY = -0.36                                                                   # piano della faccia (avanti)
SCALA = 1.078                                                                # alto 2,50 unita' = 190 cm (con Pippo 175 cm = 2,30)


def mats(stile='A'):
    m = lambda n, c, **k: material('GEN_' + n, c, **k)
    M = dict(pelle=m('pelle', (0.93, 0.66, 0.52), rough=0.55), pelle_s=m('pelle_s', (0.84, 0.55, 0.42), rough=0.55), capelli=_brizzolato(), rasato=m('rasato', (0.4, 0.36, 0.34), rough=0.85),
             sopr=m('sopr', (0.1, 0.08, 0.07), rough=0.6), iride=m('iride', (0.36, 0.2, 0.08), rough=0.3), bianco=m('bianco', (0.97, 0.97, 0.97), rough=0.3), nero=m('nero', (0.02, 0.02, 0.02), rough=0.15),
             guancia=m('guancia', (0.95, 0.5, 0.45), rough=0.6), bocca=m('bocca', (0.45, 0.08, 0.08), rough=0.5), dentro=m('dentro', (0.16, 0.01, 0.03), rough=0.5),
             lingua=m('lingua', (0.95, 0.35, 0.40), rough=0.45), oro=m('oro', (1.0, 0.74, 0.2), rough=0.25, metallic=0.9), stivali=m('stivali', (0.03, 0.03, 0.03), rough=0.2),
             camicia=m('camicia', (0.92, 0.9, 0.82), rough=0.6), cravatta=m('cravatta', (0.1, 0.1, 0.08), rough=0.5),
             nastro1=m('nastro1', (0.8, 0.1, 0.1), rough=0.5), nastro2=m('nastro2', (0.1, 0.25, 0.7), rough=0.5), nastro3=m('nastro3', (0.95, 0.75, 0.1), rough=0.5),
             nastro4=m('nastro4', (0.1, 0.5, 0.2), rough=0.5))
    if stile == 'A':
        M.update(giacca=m('giaccaA', (0.27, 0.3, 0.17), rough=0.7), panta=m('pantaA', (0.24, 0.27, 0.15), rough=0.75), riga=m('rigaA', (0.75, 0.1, 0.1), rough=0.5),
                 berr=m('berrA', (0.27, 0.3, 0.17), rough=0.6), visiera=m('visieraA', (0.03, 0.03, 0.03), rough=0.15))
    elif stile == 'B':
        M.update(giacca=m('giaccaB', (0.05, 0.07, 0.16), rough=0.6), panta=m('pantaB', (0.05, 0.07, 0.16), rough=0.65), riga=m('rigaB', (0.8, 0.08, 0.08), rough=0.5),
                 berr=m('berrB', (0.05, 0.07, 0.16), rough=0.6), visiera=m('visieraB', (0.03, 0.03, 0.03), rough=0.15), fascia=m('fasciaB', (0.75, 0.08, 0.1), rough=0.5),
                 cintura=m('cinturaB', (0.97, 0.97, 0.95), rough=0.4))
    else:
        cam = _mimetica(); M.update(giacca=cam, panta=cam, riga=cam,
                 berr=m('berrC', (0.45, 0.06, 0.08), rough=0.9), visiera=m('visieraC', (0.03, 0.03, 0.03), rough=0.15),
                 macchia1=m('macchia1', (0.18, 0.2, 0.1), rough=0.85), macchia2=m('macchia2', (0.5, 0.42, 0.26), rough=0.85), cintura=m('cinturaC', (0.12, 0.1, 0.06), rough=0.6))
    return M


def _brizzolato():
    """capelli brizzolati: castano scuro con fili grigi (rumore fine)"""
    if 'GEN_brizzolato' in bpy.data.materials: return bpy.data.materials['GEN_brizzolato']
    m = bpy.data.materials.new('GEN_brizzolato'); m.use_nodes = True; nt = m.node_tree; N = nt.nodes; L = nt.links
    tc = N.new('ShaderNodeTexCoord'); nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 90.0; nz.inputs['Detail'].default_value = 4.0
    L.new(tc.outputs['Object'], nz.inputs['Vector'])
    cr = N.new('ShaderNodeValToRGB'); el = cr.color_ramp.elements
    el[0].position = 0.6; el[0].color = (0.035, 0.028, 0.024, 1); el[1].position = 0.78; el[1].color = (0.36, 0.35, 0.34, 1)
    L.new(nz.outputs['Fac'], cr.inputs['Fac']); L.new(cr.outputs['Color'], N['Principled BSDF'].inputs['Base Color']); N['Principled BSDF'].inputs['Roughness'].default_value = 0.6
    return m


def _mimetica():
    """tessuto mimetico da cartone: macchie larghe in quattro colori (rumore procedurale a gradini)"""
    if 'GEN_mimetica' in bpy.data.materials: return bpy.data.materials['GEN_mimetica']
    m = bpy.data.materials.new('GEN_mimetica'); m.use_nodes = True; nt = m.node_tree; N = nt.nodes; L = nt.links
    tc = N.new('ShaderNodeTexCoord'); nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 3.5; nz.inputs['Detail'].default_value = 1.0
    L.new(tc.outputs['Object'], nz.inputs['Vector'])
    cr = N.new('ShaderNodeValToRGB'); cr.color_ramp.interpolation = 'CONSTANT'; el = cr.color_ramp.elements
    el[0].position = 0.0; el[0].color = (0.16, 0.19, 0.09, 1); el[1].position = 0.45; el[1].color = (0.36, 0.37, 0.22, 1)
    e3 = el.new(0.6); e3.color = (0.5, 0.42, 0.26, 1); e4 = el.new(0.72); e4.color = (0.24, 0.17, 0.1, 1)
    L.new(nz.outputs['Fac'], cr.inputs['Fac']); L.new(cr.outputs['Color'], N['Principled BSDF'].inputs['Base Color']); N['Principled BSDF'].inputs['Roughness'].default_value = 0.85
    return m


def _tondo(o, w=0.08, seg=4):
    """smussa un box: angoli tondi (faccia squadrata ma morbida come il resto della serie)"""
    b = o.modifiers.new('Smusso', 'BEVEL'); b.width = w; b.segments = seg; b.limit_method = 'NONE'
    for p in o.data.polygons: p.use_smooth = True
    return o


def _sst(e0, e1, x):
    t = min(1.0, max(0.0, (x - e0) / (e1 - e0))); return t * t * (3 - 2 * t)


def _forma(x, y, z):
    """punto della sfera unitaria -> punto della testa (22 nov: faccia piu' rettangolare, meno tondeggiante, mandibola squadrata,
    guance piatte, mento che sporge)."""
    j = _sst(0.15, -0.65, z)                                                # 0 sopra, 1 nella mandibola
    th = math.atan2(y, x); n = 3.0 + 2.5 * j                                # sezione orizzontale quasi quadrata, di piu' in basso
    q = 1.0 / ((abs(math.cos(th)) ** n + abs(math.sin(th)) ** n) ** (1.0 / n))
    x, y = x * q, y * q
    ph = math.atan2(z, math.hypot(x, y) + 1e-9); m = 3.2                   # profilo verticale rettangolare (lati dritti)
    q2 = 1.0 / ((abs(math.cos(ph)) ** m + abs(math.sin(ph)) ** m) ** (1.0 / m))
    x, y, z = x * q2, y * q2, z * min(q2, 1.25)
    x *= 1.0 + 0.04 * j
    if y < 0: y *= 1.0 - 0.06 * _sst(-0.5, -0.1, z) * (1 - _sst(0.1, 0.35, z))           # guance piatte
    if y < 0: y -= 0.26 * _sst(-0.5, -0.95, z) * min(1.0, -y * 1.6) * (1 - 0.6 * min(1.0, abs(x) * 2.2))   # mento che sporge
    return Vector((x * 0.38, y * 0.37, z * 0.5 + 0.0))


def _testa(coll, parent, M, nome='GEN_Testa'):
    """testa scolpita in un pezzo solo, piu' i capelli corti brizzolati (guscio sottile, sopra piatto) e la rasatura dei lati,
    ricavati dalla stessa forma cosi' aderiscono alla testa (niente effetto berretto)."""
    import bmesh
    def fai(nome_, mat, scala, tieni=None, piatto=None):
        bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=128, v_segments=72, radius=1.0)
        for v in bm.verts:
            p_ = _forma(*v.co) * scala
            if piatto is not None and p_.z > piatto: p_.z = piatto + (p_.z - piatto) * 0.25
            v.co = p_
        if tieni:
            via = [f for f in bm.faces if not tieni(f.calc_center_median())]
            bmesh.ops.delete(bm, geom=via, context='FACES')
        me = bpy.data.meshes.new(nome_); bm.to_mesh(me); bm.free()
        for pl in me.polygons: pl.use_smooth = True
        if not tieni:                                                       # maschera della rasatura (lati e nuca) nei colori dei vertici
            ca = me.color_attributes.new('rasato', 'FLOAT_COLOR', 'POINT')
            for i, v in enumerate(me.vertices):
                x, y, z = v.co
                lato = max(_sst(-0.2, -0.06, y), _sst(0.3, 0.36, abs(x))); alto = _sst(-0.26, -0.12, z) * (1 - _sst(0.36, 0.44, z))
                k = lato * alto; ca.data[i].color = (k, k, k, 1.0)
        o = bpy.data.objects.new(nome_, me); coll.objects.link(o); o.parent = parent; me.materials.append(mat)
        if tieni:
            sol = o.modifiers.new('Spessore', 'SOLIDIFY'); sol.thickness = 0.012; sol.offset = 1.0
        o.modifiers.new('Liscio', 'SUBSURF').levels = 1
        return o
    def attaccatura(c): return 0.36 if c.y < -0.15 else (0.3 if c.y < 0.05 else 0.27)     # dove finiscono i capelli sopra
    t = fai(nome, _pelle_rasata(M), 1.0)
    fai(nome + 'Capelli', M['capelli'], 1.03, tieni=lambda c: c.z > attaccatura(c), piatto=0.5)
    # ciuffi corti e alti sopra, spettinati e un po' in avanti (22 nov, foto di riferimento dell'autore)
    import random; rr = random.Random(7)
    S_ = lambda *a_: shape(*a_)
    shape(nome + 'Volume', 'sphere', (0, 0.0, 0.43), (0.32, 0.3, 0.1), (0, 0, 0), parent, M['capelli'], coll)    # volume sopra
    for k in range(110):
        a = rr.uniform(0, 2 * PI); r = math.sqrt(rr.uniform(0, 1))
        x, y = 0.33 * r * math.cos(a), 0.31 * r * math.sin(a) - 0.01
        alto = 0.06 + 0.035 * (1 - r) + 0.025 * max(0.0, -y / 0.3) + rr.uniform(0, 0.02)   # ciuffi corti, un po' piu' alti al centro e davanti
        o = shape(nome + 'Ciuffo', 'lock', (x, y, 0.47 - 0.12 * r * r), (rr.uniform(0.06, 0.085),) * 2 + (alto,), (rr.uniform(-0.5, 0.2) - 0.5 * r * math.sin(a), 0.5 * r * math.cos(a) + rr.uniform(-0.35, 0.35), -PI / 2 + rr.uniform(-1.2, 1.2)), parent, M['capelli'], coll)
    return t


def _pelle_rasata(M):
    """pelle della testa con la rasatura quasi a zero sui lati e sulla nuca, sfumata (niente bordo a scalini)"""
    if 'GEN_testa' in bpy.data.materials: return bpy.data.materials['GEN_testa']
    m = bpy.data.materials.new('GEN_testa'); m.use_nodes = True; nt = m.node_tree; N = nt.nodes; L = nt.links
    bs = N['Principled BSDF']; bs.inputs['Roughness'].default_value = 0.55
    tc = N.new('ShaderNodeTexCoord'); at = N.new('ShaderNodeAttribute'); at.attribute_name = 'rasato'
    def op(o, a, b):
        n = N.new('ShaderNodeMath'); n.operation = o; L.new(a, n.inputs[0])
        if isinstance(b, float): n.inputs[1].default_value = b
        else: L.new(b, n.inputs[1])
        return n.outputs[0]
    mask = at.outputs['Fac']
    nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 60.0; L.new(tc.outputs['Object'], nz.inputs['Vector'])
    fac = op('MULTIPLY', op('POWER', mask, 0.5), op('ADD', op('MULTIPLY', nz.outputs['Fac'], 0.2), 0.75))
    mx = N.new('ShaderNodeMixRGB'); L.new(fac, mx.inputs['Fac'])
    mx.inputs['Color1'].default_value = M['pelle'].node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value[:]
    mx.inputs['Color2'].default_value = (0.1, 0.085, 0.08, 1)
    L.new(mx.outputs['Color'], bs.inputs['Base Color'])
    return m


def generale(coll, stile='A', M=None, scala=SCALA):
    assert stile in STILI, stile
    M = M or mats(stile); R = {'mats': M, 'stile': stile}
    S = lambda n, k, loc, sc=(1, 1, 1), par=None, mat=None, rot=(0, 0, 0): shape('GEN_' + n, k, loc, sc, rot, par, mat, coll)
    E = lambda n, loc, par: empty('GEN_' + n, loc, par, coll)
    def B(n, loc, dim, par, mat, w=0.06, rot=(0, 0, 0)):
        o = set004.obj('GEN_' + n, set004.box_c(), loc, dim, mat, coll, parent=par); o.rotation_euler = rot
        o.data = o.data.copy(); return _tondo(o, w)
    root = R['root'] = E('Root', (0, 0, 0), None); root.scale = (scala,) * 3; body = R['body'] = E('Body', (0, 0, 0.66), root)
    # busto dritto, spalle larghe (posa da militare)
    S('Busto', 'cap:0.27:0.34', (0, 0, 0.32), (1.12, 0.92, 1.0), body, M['giacca'])
    S('Collo', 'cyl:0.11:0.14', (0, 0, 0.72), par=body, mat=M['pelle'])
    S('Colletto', 'cyl:0.135:0.07', (0, 0, 0.66), par=body, mat=M['giacca'])
    for s_ in (-1, 1): S('Mostrina', 'sphere', (s_ * 0.07, -0.115, 0.665), (0.045, 0.015, 0.03), body, M['riga'], rot=(0, 0, 0))
    if stile in ('A', 'B'):
        S('Camicia', 'sphere', (0, -0.245, 0.55), (0.07, 0.04, 0.09), body, M['camicia']); S('Cravatta', 'sphere', (0, -0.27, 0.5), (0.03, 0.02, 0.09), body, M['cravatta'])
        for r_ in range(4):
            for s_ in (-1, 1): S('Bottone', 'sphere', (s_ * 0.09, -0.285 + 0.01 * abs(r_ - 1.5), 0.44 - 0.12 * r_), (0.028, 0.015, 0.028), body, M['oro'])
        for i in range(3):                                                    # medagliere di fantasia sul petto
            for j in range(3):
                S('Nastrino', 'sphere', (-0.2 + 0.06 * j, -0.275, 0.5 - 0.045 * i), (0.028, 0.012, 0.018), body, M['nastro%d' % (1 + (i + j) % 4)])
        for k in range(2):
            S('Medaglia', 'cyl:1:1', (-0.17 + 0.06 * k, -0.28, 0.33), (0.03, 0.03, 0.008), body, M['oro'], rot=(PI / 2, 0, 0))
            S('NastroMed', 'sphere', (-0.17 + 0.06 * k, -0.278, 0.37), (0.018, 0.01, 0.03), body, M['nastro%d' % (k + 1)])
        S('Cintura', 'cyl:0.3:0.06', (0, -0.005, 0.05), (1.04, 0.96, 1), body, M.get('cintura', M['giacca'])); S('Fibbia', 'sphere', (0, -0.29, 0.05), (0.05, 0.015, 0.035), body, M['oro'])
        if stile == 'B': S('Fascia', 'cyl:1:1', (0.03, -0.01, 0.32), (0.31, 0.27, 0.05), body, M['fascia'], rot=(0, 0.7, 0))
    else:
        S('Cintura', 'cyl:0.3:0.07', (0, -0.005, 0.06), (1.04, 0.96, 1), body, M['cintura']); S('Fibbia', 'sphere', (0, -0.29, 0.06), (0.045, 0.015, 0.035), body, M['oro'])
        for s_ in (-1, 1): S('Tasca', 'sphere', (s_ * 0.13, -0.27, 0.45), (0.08, 0.02, 0.07), body, M['giacca'])
    # testa: squadrata, fronte ampia, mascella larga, orecchie grandi
    head = R['head'] = E('Head', (0, 0, HC - 0.66), body)
    # testa da persona (22 nov, l'autore: «faccia troppo squadrata, rendilo una persona con la mascella pronunciata»): cranio tondo con la fronte ampia,
    # mascella larga e squadrata che sporge, mento forte
    _testa(coll, head, M)                                                   # testa in un pezzo solo, capelli corti e lati rasati che aderiscono
    S('NasoPonte', 'sphere', (0, FY - 0.035, 0.0), (0.045, 0.06, 0.12), head, M['pelle'], rot=(0.35, 0, 0))   # naso lungo, poco a pallina
    S('NasoPunta', 'sphere', (0, FY - 0.08, -0.095), (0.048, 0.06, 0.065), head, M['pelle_s'])
    for s_ in (-1, 1): S('Narice', 'sphere', (s_ * 0.04, FY - 0.06, -0.105), (0.03, 0.035, 0.025), head, M['pelle_s'])
    for s_, nm in ((-1, 'L'), (1, 'R')):
        S('Orecchio', 'sphere', (s_ * 0.42, 0.03, 0.0), (0.06, 0.11, 0.16), head, M['pelle']); S('OrecchioDentro', 'sphere', (s_ * 0.435, 0.0, 0.0), (0.02, 0.065, 0.1), head, M['pelle_s'])
        eye = E('Eye' + nm, (s_ * 0.15, FY + 0.005, 0.07), head); S('Occhio', 'sphere', (0, 0, 0), (0.09, 0.045, 0.085), eye, M['bianco'])
        pu = R['pupil' + nm] = E('Sguardo' + nm, (0, -0.04, 0), eye)                        # iride marrone e pupilla si muovono insieme
        S('Iride', 'sphere', (0, 0.006, 0), (0.05, 0.016, 0.055), pu, M['iride']); S('Pupilla', 'sphere', (0, 0, 0), (0.026, 0.018, 0.03), pu, M['nero']); S('Luce', 'sphere_lo', (0.015, -0.055, 0.02), (0.012, 0.007, 0.014), eye, M['bianco'])
        R['lid' + nm] = S('Palpebra', 'sphere', (0, -0.012, 0.09), (0.1, 0.06, 0.001), eye, M['pelle'])
        b = R['brow' + nm] = E('Brow' + nm, (s_ * 0.15, FY - 0.03, 0.19), head); S('Sopracciglio', 'sphere', (0, 0, 0), (0.15, 0.05, 0.055), b, M['sopr'])          # sopracciglia marcate
    # capelli castano scuro a spazzola, stessa forma di quelli di Cappellone
    # taglio militare (22 nov): sopra corti e piatti, brizzolati; ai lati e dietro rasati quasi a zero
    # bocca: curva (come Cappellone) + bocca aperta a D col bordo
    cu = bpy.data.curves.new('GEN_BoccaCurva', 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = 0.018; cu.bevel_resolution = 4; cu.use_fill_caps = True
    sp = cu.splines.new('BEZIER'); sp.bezier_points.add(2); base = [(-0.13, FY - 0.0, -0.19), (0, FY - 0.028, -0.2), (0.13, FY - 0.0, -0.19)]
    for bp, co in zip(sp.bezier_points, base): bp.co = co; bp.handle_left_type = bp.handle_right_type = 'AUTO'
    mo = bpy.data.objects.new('GEN_Bocca', cu); mo.parent = head; coll.objects.link(mo); mo.data.materials.append(M['bocca'])
    R['mouth_curve'] = cu; R['mouth_base'] = base; R['mouth_obj'] = mo
    ap = R['mouth_open'] = E('BoccaAperta', (0, FY - 0.015, -0.2), head)
    S('Labbra', 'sphere', (0, 0.008, 0), (0.15, 0.03, 0.105), ap, M['bocca']); S('BoccaDentro', 'sphere', (0, 0, 0), (0.13, 0.035, 0.088), ap, M['dentro'])
    S('Lingua', 'sphere', (0, -0.01, -0.045), (0.08, 0.026, 0.035), ap, M['lingua']); S('Denti', 'sphere', (0, -0.012, 0.055), (0.11, 0.028, 0.026), ap, M['bianco'])
    ap.scale = (0.001,) * 3
    # berretto: da generale (A, B) o basco (C)
    cap = R['cap'] = E('Berretto', (0, 0, 0), head)
    if stile in ('A', 'B'):
        S('Cupola', 'cyl:0.44:0.12', (0, 0.02, 0.63), (1.0, 1.0, 1.0), cap, M['berr']); S('Fascia', 'cyl:0.37:0.11', (0, 0.02, 0.53), par=cap, mat=M['riga'])
        S('Visiera', 'sphere', (0, -0.33, 0.48), (0.28, 0.16, 0.025), cap, M['visiera'], rot=(-0.25, 0, 0))
        S('Fregio', 'sphere', (0, -0.385, 0.6), (0.07, 0.015, 0.06), cap, M['oro']); S('Cordone', 'cyl:1:1', (0, -0.37, 0.535), (0.012, 0.012, 0.22), cap, M['oro'], rot=(0, PI / 2, 0))
        for k in range(5): S('Ricamo', 'sphere', (-0.2 + 0.1 * k, -0.3 + 0.02 * abs(k - 2), 0.485), (0.04, 0.012, 0.01), cap, M['oro'], rot=(-0.25, 0, 0))
    else:
        S('Basco', 'sphere', (0.08, 0.04, 0.6), (0.43, 0.42, 0.11), cap, M['berr'], rot=(0, 0.18, 0)); S('BascoBordo', 'cyl:0.37:0.05', (0, 0.04, 0.53), par=cap, mat=M['cintura'])
        S('Fregio', 'sphere', (-0.18, -0.32, 0.57), (0.05, 0.015, 0.05), cap, M['oro'])
    # braccia con le spalline (gradi: stelle di fantasia), gambe con la riga, stivali
    for s_, nm in ((-1, 'L'), (1, 'R')):
        sh = R['shoulder' + nm] = E('Shoulder' + nm, (s_ * 0.37, 0, 0.6), body)
        S('Manica', 'cap:0.09:0.42', (0, 0, -0.26), par=sh, mat=M['giacca']); S('Polsino', 'cyl:0.085:0.05', (0, 0, -0.53), par=sh, mat=M['riga'] if stile != 'C' else M['giacca'])
        S('Mano', 'sphere', (0, 0, -0.64), (0.105, 0.1, 0.115), sh, M['pelle'])
        sp_ = E('Spalla' + nm, (s_ * 0.37, 0, 0.6), body)                     # le spalline stanno sul busto, non girano col braccio
        if stile != 'C':
            S('Spallina', 'sphere', (s_ * 0.02, 0, 0.04), (0.14, 0.12, 0.04), sp_, M['oro'])
            for k in range(7): S('Frangia', 'cyl:0.012:0.08', (s_ * 0.13, -0.09 + 0.03 * k, -0.01), par=sp_, mat=M['oro'])          # frangia d'oro sul bordo esterno
            for k in range(3): S('Stella', 'sphere', (s_ * 0.02 + (-0.06 + 0.06 * k), 0.0, 0.08), (0.022, 0.022, 0.01), sp_, M['bianco'] if stile == 'B' else M['nero'])
        else:
            for k in range(2): S('Stella', 'sphere', (s_ * 0.02 + (-0.03 + 0.06 * k), 0.0, 0.04), (0.02, 0.02, 0.008), sp_, M['nero'])
        hp = R['hip' + nm] = E('Hip' + nm, (s_ * 0.14, 0, 0.66), root)
        S('Gamba', 'cap:0.11:0.38', (0, 0, -0.29), par=hp, mat=M['panta'])
        if stile != 'C': S('Bande', 'cyl:1:1', (s_ * 0.105, 0, -0.26), (0.012, 0.03, 0.42), hp, M['riga'], rot=(0, 0, 0))
        S('Stivale', 'cap:0.12:0.14', (0, 0, -0.5), par=hp, mat=M['stivali']); S('Punta', 'sphere', (0, -0.08, -0.6), (0.12, 0.2, 0.07), hp, M['stivali'])
    head.scale = (0.88,) * 3                                                # faccia piu' piccola rispetto al corpo (22 nov)
    berretto(R, None, False)                                                # senza berretto di solito (22 nov): si puo' rimettere con berretto(G, f, True)
    emozione(R, None, 'severo'); return R                                    # di solito ha lo sguardo severo


def _k(o, prop, f):
    if f is not None: o.keyframe_insert(prop, frame=f)


def faccia(R, f, brow=0.0, brow_lift=0.0, smile=0.0, mouth_open=0.0, look=(0.0, 0.0), lid=0.0):
    """brow > 0 arrabbiato, < 0 preoccupato; brow_lift alza; smile -1..2; mouth_open 0..1,5; look (x, z); lid 0 aperto .. 1 chiuso."""
    for s_, nm in ((-1, 'L'), (1, 'R')):
        b = R['brow' + nm]; b.rotation_euler = (0, -s_ * brow * 0.5, 0); b.location = (s_ * 0.15, FY - 0.03, 0.19 + 0.06 * brow_lift - 0.025 * max(0, brow)); _k(b, 'rotation_euler', f); _k(b, 'location', f)
        p = R['pupil' + nm]; p.location = (look[0] * 0.04, -0.04, look[1] * 0.04); _k(p, 'location', f)
        l = R['lid' + nm]; l.scale = (0.1, 0.06, 0.001 + 0.1 * lid); l.location = (0, -0.012, 0.09 - 0.09 * lid); _k(l, 'scale', f); _k(l, 'location', f)
    cu = R['mouth_curve']
    for i, bp in enumerate(cu.splines[0].bezier_points):
        x, y, z = R['mouth_base'][i]; z = (z - 0.04 * smile) if i == 1 else (z + 0.045 * smile)
        bp.co = (x * (1 + 0.22 * max(0, smile)), y, z); bp.handle_left_type = bp.handle_right_type = 'AUTO'
        if f is not None: bp.keyframe_insert('co', frame=f)
    ap = R['mouth_open']; mo = R['mouth_obj']
    if mouth_open <= 0.02: ap.scale = (0.001,) * 3; mo.scale = (1, 1, 1)
    else:
        sz = 0.3 + 0.9 * mouth_open
        ap.location = (0, FY - 0.015, -0.205 - 0.01 * smile); ap.scale = (0.62 + 0.3 * mouth_open + 0.08 * max(0.0, smile), 1.0, sz * (1.0 - 0.08 * max(0.0, smile))); mo.scale = (0.001,) * 3
    _k(ap, 'scale', f); _k(ap, 'location', f); _k(mo, 'scale', f)


EMOZIONI = {
    'severo': dict(smile=-0.4, brow=1.2, lid=0.3), 'comizio': dict(smile=0.2, mouth_open=1.3, brow=1.2, brow_lift=0.2), 'urla': dict(smile=-0.8, mouth_open=1.5, brow=1.7),
    'ghigno': dict(smile=1.2, brow=0.7, lid=0.4, look=(-0.8, 0)), 'fiero': dict(smile=0.8, brow_lift=0.5, lid=0.3, look=(0, 0.4)), 'offeso': dict(smile=-1.4, brow=-0.8, brow_lift=0.8, mouth_open=0.3),
    'sorpreso': dict(smile=-0.2, mouth_open=1.0, brow=-0.6, brow_lift=1.2), 'ride': dict(smile=1.8, mouth_open=1.1, brow_lift=0.8, lid=0.6),
}
def emozione(R, f, nome): faccia(R, f, **EMOZIONI[nome])

GESTI = {                                                                    # braccio sinistro, braccio destro (direzioni), testa (rot x, y, z), busto (rot x, y)
    'attenti': ((-0.06, 0, -1), (0.06, 0, -1), (-0.05, 0, 0), (-0.04, 0)), 'riposo': ((-0.15, 0.1, -1), (0.15, 0.1, -1), (0, 0, 0), (0, 0)),
    'saluto militare': ((-0.06, 0, -1), (-0.35, -0.55, 0.75), (-0.05, 0, 0), (-0.04, 0)), 'dito puntato': ((-0.12, 0, -1), (0.2, -1.0, 0.15), (0.05, 0, 0.1), (0.12, 0)),
    'comizio': ((-0.75, -0.25, 0.7), (0.75, -0.25, 0.7), (-0.2, 0, 0), (-0.08, 0)), 'pugno sul tavolo': ((-0.2, -0.5, -0.8), (0.15, -0.6, 0.75), (0.15, 0, 0), (0.18, 0)),
    'mani sui fianchi': ((-0.85, 0.15, -0.45), (0.85, 0.15, -0.45), (-0.1, 0, 0), (-0.06, 0)), 'binocolo': ((0.35, -0.85, 0.45), (-0.35, -0.85, 0.45), (-0.05, 0, 0), (0.05, 0)),
}
def gesto(R, f, nome):
    l, r, t, b = GESTI[nome]
    for nm, d in (('L', l), ('R', r)):
        sh = R['shoulder' + nm]; sh.rotation_mode = 'QUATERNION'; sh.rotation_quaternion = Vector((0, 0, -1)).rotation_difference(Vector(d).normalized()); _k(sh, 'rotation_quaternion', f)
    R['head'].rotation_euler = t; _k(R['head'], 'rotation_euler', f); R['body'].rotation_euler = (b[0], b[1], 0); _k(R['body'], 'rotation_euler', f)


def berretto(R, f, on=True):
    R['cap'].scale = (1, 1, 1) if on else (0.001,) * 3; _k(R['cap'], 'scale', f)
