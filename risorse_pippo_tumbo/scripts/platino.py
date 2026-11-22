"""La Signora Platino (nome provvisorio): nuovo personaggio (22 novembre 2026) chiesto dall'autore, nello stile a pedina della serie.
Politica dall'aria istituzionale: testa ovale slanciata color avorio, zigomi alti, mascella netta, rughe sottili ai lati degli occhi
e pieghe naso-bocca; occhi medio-allungati azzurro-grigio con la palpebra di sopra orizzontale e netta (come il Tirato: sguardo
diretto e composto); sopracciglia sottili e arcuate biondo cenere; naso sottile, dritto e affusolato; labbra sottili, sorriso
istituzionale misurato; capelli biondo platino a calotta voluminosa, corti-medi, pettinati all'indietro con la riga di lato e
un'onda morbida sopra la fronte, orecchie scoperte. Giacca sartoriale sopra una blusa chiara. Personaggio INVENTATO. Alta 165 cm (l'autore, 22 nov). Versione scelta: A (blazer azzurro polvere).
    import platino as pl
    P = pl.platino(coll, stile='A')             # 'A' blazer azzurro polvere, 'B' rosa antico, 'C' blu istituzionale
    pl.faccia(P, f, brow=0, brow_lift=0, smile=0, mouth_open=0, look=(0, 0), lid=0)
    pl.emozione(P, f, 'istituzionale')          # una delle EMOZIONI
    pl.gesto(P, f, 'saluto')                    # uno dei GESTI
Fronte -Y, piedi a z = 0. Pippo = 175 cm (2,30 unita') -> 165 cm = 2,17 unita' (SCALA misurata in scheda_platino.py)."""
import math, bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from common import material, shape, empty
PI = math.pi
HC = 1.72
STILI = ('A', 'B', 'C')
FY = -0.36
SCALA = 0.938                                                                # alto 2,42 unita' = 184 cm (con Pippo 175 cm = 2,30), misurato


def mats(stile='A'):
    m = lambda n, c, **k: material('PLA_' + n, c, **k)
    M = dict(pelle=m('pelle', (0.94, 0.72, 0.58), rough=0.5), pelle_s=m('pelle_s', (0.87, 0.62, 0.5), rough=0.5), ruga=m('ruga', (0.72, 0.5, 0.42), rough=0.7),
             capelli=_platino(), sopr=m('sopr', (0.5, 0.43, 0.33), rough=0.6), iride=m('iride', (0.42, 0.56, 0.68), rough=0.25),
             bianco=m('bianco', (0.97, 0.97, 0.97), rough=0.3), nero=m('nero', (0.02, 0.02, 0.02), rough=0.15), bocca=m('bocca', (0.66, 0.33, 0.33), rough=0.45),
             labbro=m('labbro', (0.78, 0.45, 0.45), rough=0.4), dentro=m('dentro', (0.16, 0.01, 0.03), rough=0.5), lingua=m('lingua', (0.95, 0.35, 0.40), rough=0.45),
             scarpe=m('scarpe', (0.05, 0.04, 0.05), rough=0.2), camicia=m('blusa', (0.96, 0.94, 0.9), rough=0.45), perla=m('perla', (0.95, 0.93, 0.88), rough=0.2))
    if stile == 'A':
        M.update(giacca=m('giaccaA', (0.3, 0.47, 0.72), rough=0.55), panta=m('pantaA', (0.3, 0.47, 0.72), rough=0.6))
    elif stile == 'B':
        M.update(giacca=m('giaccaB', (0.72, 0.38, 0.42), rough=0.55), panta=m('pantaB', (0.72, 0.38, 0.42), rough=0.6))
    else:
        M.update(giacca=m('giaccaC', (0.07, 0.13, 0.36), rough=0.5), panta=m('pantaC', (0.07, 0.13, 0.36), rough=0.55))
    return M


def _platino():
    """biondo platino / cenere chiaro, sfumato, con le onde morbide della piega"""
    if 'PLA_capelli' in bpy.data.materials: return bpy.data.materials['PLA_capelli']
    m = bpy.data.materials.new('PLA_capelli'); m.use_nodes = True; nt = m.node_tree; N = nt.nodes; L = nt.links
    bs = N['Principled BSDF']; bs.inputs['Roughness'].default_value = 0.4
    nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 5.0; cr = N.new('ShaderNodeValToRGB'); el = cr.color_ramp.elements
    el[0].position = 0.3; el[0].color = (0.42, 0.36, 0.24, 1); el[1].position = 0.75; el[1].color = (0.72, 0.65, 0.48, 1)
    tc = N.new('ShaderNodeTexCoord'); wv = N.new('ShaderNodeTexWave'); wv.bands_direction = 'X'; wv.inputs['Scale'].default_value = 14.0
    wv.inputs['Distortion'].default_value = 3.0; L.new(tc.outputs['Object'], wv.inputs['Vector']); L.new(tc.outputs['Object'], nz.inputs['Vector'])
    L.new(nz.outputs['Fac'], cr.inputs['Fac']); L.new(cr.outputs['Color'], bs.inputs['Base Color'])
    bp = N.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = 0.5; L.new(wv.outputs['Fac'], bp.inputs['Height']); L.new(bp.outputs['Normal'], bs.inputs['Normal'])
    return m


def _sst(e0, e1, x):
    t = min(1.0, max(0.0, (x - e0) / (e1 - e0))); return t * t * (3 - 2 * t)


def _campana(z, c, w):
    return math.exp(-((z - c) / w) ** 2)


def _forma(x, y, z):
    """sfera unitaria -> testa: ovale allungato, zigomi delineati, guance appena scavate sotto, mascella netta, mento definito"""
    th = math.atan2(y, x); n = 2.35 + 0.5 * _sst(-0.3, -0.8, z)
    q = 1.0 / ((abs(math.cos(th)) ** n + abs(math.sin(th)) ** n) ** (1.0 / n)); x, y = x * q, y * q
    x *= 1.0 + 0.07 * _campana(z, 0.08, 0.16) - 0.05 * _campana(z, -0.25, 0.15) + 0.02 * _campana(z, -0.55, 0.12)   # zigomi alti, guance, mascella netta
    x *= 1.0 - 0.22 * _sst(-0.6, -1.0, z)                                   # ovale: si stringe verso il mento
    if y < 0: y -= 0.07 * _sst(-0.7, -0.95, z) * min(1.0, -y * 1.5) * (1 - min(1.0, abs(x) * 2.5))   # mento definito
    return Vector((x * 0.34, y * 0.35, z * 0.55))


def _attaccatura(c):
    """attaccatura bassa e aderente (22 nov sera): fronte normale, i lati scendono intorno alle orecchie, bassa dietro"""
    davanti = _sst(-0.05, -0.25, c.y)
    fronte = 0.28 - 0.06 * min(1.0, (c.x / 0.26) ** 2) - 0.075 * math.exp(-((c.x - 0.1) / 0.09) ** 2)   # arco morbido (niente punte sulle tempie); a destra l'onda scende un po' sulla fronte
    return fronte * davanti - 0.26 * _sst(0.05, 0.3, c.y)


def _orecchio(c): return abs(c.x) > 0.26 and -0.09 < c.y < 0.13 and c.z < 0.15    # le orecchie restano scoperte


def _testa(coll, parent, M, nome='PLA_Testa'):
    import bmesh
    def fai(nome_, mat, scala, tieni=None, spessore=0.0, gonfia=False):
        bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=128, v_segments=72, radius=1.0); bm.verts.index_update()
        base = {}
        for v in bm.verts:
            p_ = base[v.index] = _forma(*v.co)
            if gonfia:                                                      # volume naturale sopra, sollevato davanti, ordinato
                d = p_.z - _attaccatura(p_)                                     # distanza dall'attaccatura: sul bordo i capelli aderiscono alla testa
                lati = 1 - _sst(-0.05, -0.25, p_.y)                             # lati e nuca: volume morbido anche vicino all'attaccatura
                k = 1.0 + 0.22 * _sst(0.0, 0.24, d) + 0.08 * lati * _sst(0.0, 0.07, d); q_ = Vector((p_.x * k, p_.y * k, p_.z + 0.06 * _sst(0.05, 0.3, d)))
                n_ = q_.normalized() if q_.length > 0 else Vector((0, 0, 1))
                q_ += n_ * 0.012 * math.sin(p_.x * 38 + p_.y * 6) * _sst(0.0, 0.1, d)      # ciocche morbide pettinate all'indietro
                riga = math.exp(-((p_.x + 0.11) / 0.022) ** 2) * _sst(0.3, 0.45, p_.z) * _sst(0.2, -0.1, p_.y)   # riga di lato (a sinistra)
                q_ -= n_ * 0.055 * riga
                fr = _sst(0.02, 0.12, d) * (1 - _sst(0.15, 0.3, d)) * _sst(-0.1, -0.3, p_.y) * _sst(-0.12, 0.05, p_.x)   # ciuffo compatto sollevato sulla fronte
                q_.z += 0.05 * fr
                onda = math.exp(-((p_.x - 0.1) / 0.1) ** 2) * _sst(-0.1, -0.3, p_.y) * (1 - _sst(0.0, 0.12, d))   # l'onda che scende di lato: morbida e gonfia
                q_ += n_ * 0.025 * onda
                p_ = q_
            v.co = p_ * scala
        if tieni:
            via = [f for f in bm.faces if not tieni(sum((base[vv.index] for vv in f.verts), Vector()) / len(f.verts))]
            bmesh.ops.delete(bm, geom=via, context='FACES')
            bv = [v for v in bm.verts if v.is_boundary]                     # bordo liscio: niente scalini sulla fronte
            for _ in range(12):
                nuovo = {}
                for v in bv:
                    vic = [e.other_vert(v) for e in v.link_edges if e.is_boundary]
                    if len(vic) == 2: nuovo[v] = v.co * 0.4 + (vic[0].co + vic[1].co) * 0.3
                for v, c in nuovo.items(): v.co = c
        me = bpy.data.meshes.new(nome_); bm.to_mesh(me); bm.free()
        for pl in me.polygons: pl.use_smooth = True
        o = bpy.data.objects.new(nome_, me); coll.objects.link(o); o.parent = parent; me.materials.append(mat)
        if spessore:
            sol = o.modifiers.new('Spessore', 'SOLIDIFY'); sol.thickness = spessore; sol.offset = 1.0
        o.modifiers.new('Liscio', 'SUBSURF').levels = 2
        return o
    t = fai(nome, M['pelle'], 1.0)
    fai(nome + 'Capelli', M['capelli'], 1.008, tieni=lambda c: c.z > _attaccatura(c) and not _orecchio(c), spessore=0.022, gonfia=True)
    me = t.data; bvh = BVHTree.FromPolygons([v.co for v in me.vertices], [p.vertices[:] for p in me.polygons])
    return t, bvh


def _sulla_faccia(bvh, x, z, fuori=0.006):
    hit = bvh.ray_cast(Vector((x, -1.0, z)), Vector((0, 1, 0)))
    y = hit[0].y if hit[0] is not None else FY
    return (x, y - fuori, z)


def _sopracciglio(coll, parent, mat, bvh, lato):
    """sopracciglio folto e appena arcuato verso il centro: curva sulla fronte, piu' spessa dentro, sottile in fondo"""
    bx, by, bz = parent.location
    cu = bpy.data.curves.new('PLA_Sopracciglio', 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = 0.015; cu.bevel_resolution = 3; cu.use_fill_caps = True
    pts = [(0.04, -0.004, 0.8), (0.09, 0.016, 1.0), (0.145, 0.019, 0.9), (0.2, -0.004, 0.55)]     # x dal centro, z, spessore: arco continuo e morbido
    sp = cu.splines.new('BEZIER'); sp.bezier_points.add(len(pts) - 1)
    for bp, (x, z, r) in zip(sp.bezier_points, pts):
        y = _sulla_faccia(bvh, lato * x, bz + z, 0.012)[1]
        bp.co = (lato * x - bx, y - by, z); bp.radius = r; bp.handle_left_type = bp.handle_right_type = 'AUTO'
    o = bpy.data.objects.new('PLA_Sopracciglio', cu); o.parent = parent; coll.objects.link(o); cu.materials.append(mat)
    o.scale = (1, 1, 1.0); return o


def _ruga(coll, parent, M, bvh, nome, punti, spessore=0.006, fuori=0.005):
    cu = bpy.data.curves.new(nome, 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = spessore; cu.bevel_resolution = 3; cu.use_fill_caps = True
    sp = cu.splines.new('BEZIER'); sp.bezier_points.add(len(punti) - 1)
    for bp, (x, z) in zip(sp.bezier_points, punti): bp.co = _sulla_faccia(bvh, x, z, fuori); bp.handle_left_type = bp.handle_right_type = 'AUTO'
    sp.bezier_points[0].radius = sp.bezier_points[-1].radius = 0.25
    o = bpy.data.objects.new(nome, cu); o.parent = parent; coll.objects.link(o); cu.materials.append(M['ruga']); return o


def platino(coll, stile='A', M=None, scala=SCALA):
    assert stile in STILI, stile
    M = M or mats(stile); R = {'mats': M, 'stile': stile}
    S = lambda n, k, loc, sc=(1, 1, 1), par=None, mat=None, rot=(0, 0, 0): shape('PLA_' + n, k, loc, sc, rot, par, mat, coll)
    E = lambda n, loc, par: empty('PLA_' + n, loc, par, coll)
    root = R['root'] = E('Root', (0, 0, 0), None); root.scale = (scala,) * 3; body = R['body'] = E('Body', (0, 0, 0.66), root)
    # busto snello: giacca sartoriale sopra una blusa chiara a girocollo, filo di perle
    S('Busto', 'cap:0.24:0.34', (0, 0, 0.32), (1.04, 0.86, 1.0), body, M['giacca'])
    S('Collo', 'cyl:0.085:0.14', (0, 0, 0.72), par=body, mat=M['pelle'])
    S('Blusa', 'sphere', (0, -0.19, 0.52), (0.12, 0.04, 0.17), body, M['camicia']); S('Girocollo', 'cyl:0.1:0.05', (0, 0, 0.665), par=body, mat=M['camicia'])
    for k in range(13):                                                       # filo di perle
        a = -PI / 2 + (k - 6) * 0.16; S('Perla', 'sphere', (math.cos(a) * 0.105, math.sin(a) * 0.1 - 0.01, 0.63 - 0.015 * math.cos((k - 6) * 0.25) ** 8), (0.013,) * 3, body, M['perla'])
    for s_ in (-1, 1): S('Bavero', 'sphere', (s_ * 0.1, -0.205, 0.47), (0.05, 0.03, 0.19), body, M['giacca'], rot=(0, s_ * 0.3, 0))
    S('Bottone', 'sphere', (0.0, -0.25, 0.25), (0.02, 0.012, 0.02), body, M['giacca'])
    # testa
    head = R['head'] = E('Head', (0, 0, HC - 0.66), body)
    _, bvh = _testa(coll, head, M)
    S('NasoPonte', 'sphere', _sulla_faccia(bvh, 0, -0.01, 0.005), (0.03, 0.045, 0.11), head, M['pelle'], rot=(0.12, 0, 0))   # naso sottile e dritto
    S('NasoPunta', 'sphere', _sulla_faccia(bvh, 0, -0.095, 0.04), (0.026, 0.045, 0.025), head, M['pelle_s'], rot=(-0.45, 0, 0))   # punta affusolata
    for s_ in (-1, 1): S('Narice', 'sphere', _sulla_faccia(bvh, s_ * 0.038, -0.115, 0.012), (0.02, 0.024, 0.015), head, M['pelle_s'])
    for s_, nm in ((-1, 'L'), (1, 'R')):
        S('Orecchio', 'sphere', (s_ * 0.35, 0.03, 0.0), (0.045, 0.075, 0.115), head, M['pelle']); S('OrecchioDentro', 'sphere', (s_ * 0.364, 0.0, 0.0), (0.016, 0.045, 0.075), head, M['pelle_s'])
        S('Orecchino', 'sphere', (s_ * 0.36, -0.01, -0.1), (0.018,) * 3, head, M['perla'])
        eye = E('Eye' + nm, _sulla_faccia(bvh, s_ * 0.135, 0.07, fuori=-0.022), head)
        S('Occhio', 'sphere', (0, 0, 0), (0.08, 0.04, 0.054), eye, M['bianco'])                                      # occhi medio-allungati
        pu = R['pupil' + nm] = E('Sguardo' + nm, (0, -0.035, 0), eye)
        S('Iride', 'sphere', (0, 0.006, 0), (0.038, 0.014, 0.042), pu, M['iride']); S('Pupilla', 'sphere', (0, 0.0, 0), (0.017, 0.014, 0.019), pu, M['nero'])   # azzurro-grigio chiaro
        S('Luce', 'sphere_lo', (s_ * -0.012, -0.05, 0.016), (0.01, 0.006, 0.01), eye, M['bianco'])
        R['lid' + nm] = S('Palpebra', 'sphere', (0, -0.01, 0.057), (0.088, 0.05, 0.001), eye, M['pelle'])   # palpebra di sopra orizzontale e netta
        S('PalpebraSotto', 'sphere', (0, -0.012, -0.052), (0.086, 0.048, 0.02), eye, M['pelle'])
        R['piega' + nm] = S('Piega', 'sphere', (0, -0.024, 0.045), (0.088, 0.02, 0.004), eye, M['ruga'])             # bordo netto della palpebra
        b = R['brow' + nm] = E('Brow' + nm, _sulla_faccia(bvh, s_ * 0.14, 0.17, fuori=0.008), head)
        _sopracciglio(coll, b, M['sopr'], bvh, s_); R['browbase' + nm] = tuple(b.location)
        # rughe d'espressione: zampe di gallina all'angolo degli occhi, lievi pieghe naso-bocca
        for k in range(3): _ruga(coll, head, M, bvh, 'PLA_Zampa', [(s_ * 0.23, 0.09 - 0.025 * k), (s_ * 0.262, 0.1 - 0.03 * k)], 0.0028)
        R['cheek' + nm] = S('Guancia', 'sphere', _sulla_faccia(bvh, s_ * 0.16, -0.1, -0.07), (0.07, 0.04, 0.045), head, M['pelle']); R['cheekbase' + nm] = tuple(R['cheek' + nm].location)
        _ruga(coll, head, M, bvh, 'PLA_RugaNasoBocca', [(s_ * 0.065, -0.09), (s_ * 0.1, -0.16), (s_ * 0.125, -0.23)], 0.0042)
    # bocca: labbra ben disegnate e simmetriche (curva + labbro di sotto), bocca a D col bordo quando parla
    my = _sulla_faccia(bvh, 0, -0.2, 0.004)[1]
    cu = bpy.data.curves.new('PLA_BoccaCurva', 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = 0.012; cu.bevel_resolution = 4; cu.use_fill_caps = True
    sp = cu.splines.new('BEZIER'); sp.bezier_points.add(2); base = [(-0.1, my + 0.025, -0.19), (0, my - 0.0, -0.2), (0.1, my + 0.025, -0.19)]
    for bp, co in zip(sp.bezier_points, base): bp.co = co; bp.handle_left_type = bp.handle_right_type = 'AUTO'
    mo = bpy.data.objects.new('PLA_Bocca', cu); mo.parent = head; coll.objects.link(mo); mo.data.materials.append(M['bocca'])
    S('LabbroSotto', 'sphere', (0, my + 0.006, -0.217), (0.06, 0.014, 0.012), mo, M['labbro'])                      # sparisce con la curva quando parla
    S('LabbroSopra', 'sphere', (0, my + 0.008, -0.19), (0.068, 0.01, 0.007), mo, M['labbro'])
    R['mouth_curve'] = cu; R['mouth_base'] = base; R['mouth_obj'] = mo; R['mouth_y'] = my
    ap = R['mouth_open'] = E('BoccaAperta', (0, my + 0.005, -0.21), head)
    S('Labbra', 'sphere', (0, 0.008, 0), (0.12, 0.03, 0.08), ap, M['labbro']); S('BoccaDentro', 'sphere', (0, 0, 0), (0.104, 0.035, 0.066), ap, M['dentro'])
    import bocca_interna; bocca_interna.sfere(ap, coll)                    # denti e lingua uguali per tutti (22 nov sera, come Bialada)
    ap.scale = (0.001,) * 3
    # braccia, gambe, scarpe lucide
    for s_, nm in ((-1, 'L'), (1, 'R')):
        sh = R['shoulder' + nm] = E('Shoulder' + nm, (s_ * 0.31, 0, 0.6), body)
        S('Manica', 'cap:0.08:0.42', (0, 0, -0.26), par=sh, mat=M['giacca']); S('Polsino', 'cyl:0.068:0.04', (0, 0, -0.54), par=sh, mat=M['camicia'])
        S('Mano', 'sphere', (0, 0, -0.63), (0.088, 0.084, 0.098), sh, M['pelle'])
        hp = R['hip' + nm] = E('Hip' + nm, (s_ * 0.12, 0, 0.66), root)
        S('Gamba', 'cap:0.095:0.4', (0, 0, -0.31), par=hp, mat=M['panta'])
        S('Scarpa', 'sphere', (0, -0.06, -0.6), (0.085, 0.17, 0.06), hp, M['scarpe']); S('Tacco', 'cyl:0.05:0.06', (0, 0.06, -0.615), par=hp, mat=M['scarpe'])
    head.scale = (0.88,) * 3
    emozione(R, None, 'istituzionale'); return R


def _k(o, prop, f):
    if f is not None: o.keyframe_insert(prop, frame=f)


def faccia(R, f, brow=0.0, brow_lift=0.0, smile=0.0, mouth_open=0.0, look=(0.0, 0.0), lid=0.0):
    """brow > 0 arrabbiato, < 0 preoccupato; brow_lift alza; smile -1..2; mouth_open 0..1,5; look (x, z); lid 0 aperto .. 1 chiuso."""
    for s_, nm in ((-1, 'L'), (1, 'R')):
        b = R['brow' + nm]; bx, by, bz = R['browbase' + nm]
        b.rotation_euler = (0, -s_ * brow * 0.45, 0); b.location = (bx, by, bz + 0.05 * brow_lift - 0.02 * max(0, brow)); _k(b, 'rotation_euler', f); _k(b, 'location', f)
        p = R['pupil' + nm]; p.location = (look[0] * 0.03, -0.035, look[1] * 0.02); _k(p, 'location', f)
        l = R['lid' + nm]; l.scale = (0.088, 0.05, 0.001 + 0.06 * lid); l.location = (0, -0.01, 0.057 - 0.057 * lid)
        pg = R['piega' + nm]; pg.location = (0, -0.024, 0.057 - 0.117 * lid + 0.003); _k(pg, 'location', f); _k(l, 'scale', f); _k(l, 'location', f)
        c = R['cheek' + nm]; cx, cy, cz = R['cheekbase' + nm]; c.location = (cx, cy - 0.006 * max(0.0, smile), cz + 0.025 * max(0.0, smile)); _k(c, 'location', f)   # le guance salgono verso gli zigomi
    cu = R['mouth_curve']
    for i, bp in enumerate(cu.splines[0].bezier_points):
        x, y, z = R['mouth_base'][i]; z = (z - 0.03 * smile) if i == 1 else (z + 0.035 * smile)
        bp.co = (x * (1 + 0.3 * max(0, smile)), y, z); bp.handle_left_type = bp.handle_right_type = 'AUTO'
        if f is not None: bp.keyframe_insert('co', frame=f)
    ap = R['mouth_open']; mo = R['mouth_obj']
    if mouth_open <= 0.02: ap.scale = (0.001,) * 3; mo.scale = (1, 1, 1)
    else:
        sz = 0.3 + 0.6 * mouth_open                                          # bocca aperta piu' piccola e bassa: non tocca il naso
        ap.location = (0, R['mouth_y'] + 0.005, -0.215 - 0.012 * mouth_open - 0.01 * smile); ap.scale = (0.6 + 0.25 * mouth_open + 0.1 * max(0.0, smile), 1.0, sz * (1.0 - 0.08 * max(0.0, smile))); mo.scale = (0.001,) * 3
    _k(ap, 'scale', f); _k(ap, 'location', f); _k(mo, 'scale', f)


EMOZIONI = {
    'istituzionale': dict(smile=0.7, lid=0.08), 'composto': dict(smile=0.3, lid=0.12), 'sorriso misurato': dict(smile=1.1, lid=0.38, brow_lift=0.1), 'arringa': dict(smile=0.1, mouth_open=1.0, brow=0.5, brow_lift=0.3),
    'attento': dict(smile=0.0, brow=0.4, lid=0.25, look=(0.3, 0)), 'preoccupato': dict(smile=-0.6, brow=-0.8, brow_lift=0.6), 'sorpreso': dict(smile=-0.2, mouth_open=0.9, brow=-0.5, brow_lift=1.2),
    'ride': dict(smile=1.6, mouth_open=1.0, brow_lift=0.5, lid=0.45), 'furbo': dict(smile=0.8, brow=0.5, lid=0.4, look=(-0.8, 0)), 'arrabbiato': dict(smile=-0.9, brow=1.4, lid=0.2),
}
def emozione(R, f, nome): faccia(R, f, **EMOZIONI[nome])

GESTI = {                                                                    # braccio sinistro, braccio destro (direzioni), testa (rot x, y, z), busto (rot x, y)
    'riposo': ((-0.1, 0.05, -1), (0.1, 0.05, -1), (0, 0, 0), (0, 0)), 'saluto': ((-0.1, 0.05, -1), (0.45, -0.25, 0.85), (0, -0.08, 0), (0, 0)),
    'arringa': ((-0.12, 0.05, -1), (0.4, -0.85, 0.25), (-0.06, 0, 0.05), (-0.03, 0)), 'mani giunte': ((0.3, -0.85, -0.3), (-0.3, -0.85, -0.3), (0.05, 0, 0), (0.03, 0)),
    'mano sul cuore': ((-0.1, 0.05, -1), (-0.6, -0.75, 0.1), (-0.05, 0, 0), (0, 0)), 'dito alzato': ((-0.1, 0.05, -1), (0.35, -0.4, 0.85), (-0.05, 0, 0), (0, 0)),
    'mani in tasca': ((-0.2, 0.1, -1), (0.2, 0.1, -1), (0, 0, 0), (-0.03, 0)), 'mano aperta': ((-0.1, 0.05, -1), (0.55, -0.65, -0.15), (0, -0.05, 0.05), (0, 0.04)),
}
def gesto(R, f, nome):
    l, r, t, b = GESTI[nome]
    for nm, d in (('L', l), ('R', r)):
        sh = R['shoulder' + nm]; sh.rotation_mode = 'QUATERNION'; sh.rotation_quaternion = Vector((0, 0, -1)).rotation_difference(Vector(d).normalized()); _k(sh, 'rotation_quaternion', f)
    R['head'].rotation_euler = t; _k(R['head'], 'rotation_euler', f); R['body'].rotation_euler = (b[0], b[1], 0); _k(R['body'], 'rotation_euler', f)
