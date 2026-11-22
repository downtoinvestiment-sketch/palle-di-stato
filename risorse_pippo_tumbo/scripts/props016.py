"""Test 016 - GUALTIERO E IL METEORITE: ruspa, meteorite con etichetta, autogru, limonata, buco nel muro, macerie, cratere,
fumo e fuoco, negozio di ferramenta, salotto di Pippo con le foto. Gli oggetti realistici arrivano dalla libreria (pt_assets, parametro A)."""
import math, bpy, numpy as np
from common import material, shape, empty, shared_mesh
import set004
from set004 import MB, obj, cyl, ball_, bx
from props007 import text_obj
PI = math.pi

def mats016():
    c = lambda n, col, **k: material('P16_' + n, col, **k); M = {}
    M['dozer'] = c('dozer', (1.0, 0.70, 0.04), rough=0.45); M['dozerd'] = c('dozerd', (0.72, 0.47, 0.03), rough=0.5); M['track'] = c('track', (0.07, 0.07, 0.08), rough=0.8)
    M['steel'] = c('steel', (0.55, 0.57, 0.60), rough=0.35, metallic=0.8); M['glass'] = c('glass', (0.55, 0.80, 0.95), rough=0.05, spec=1.0); M['dark'] = c('dark', (0.03, 0.03, 0.04), rough=0.9)
    M['hole'] = c('hole', (0.012, 0.010, 0.010), rough=1.0); M['brick'] = c('brick', (0.60, 0.24, 0.15), rough=0.9); M['plasterc'] = c('plasterc', (0.88, 0.84, 0.72), rough=0.9)
    M['dust'] = c('dust', (0.86, 0.81, 0.70), rough=1.0, emit=(0.8, 0.75, 0.65), emit_strength=0.25); M['smoke'] = c('smoke', (0.10, 0.09, 0.09), rough=1.0)
    M['fire'] = c('fire', (1.0, 0.42, 0.04), emit=(1.0, 0.38, 0.03), emit_strength=6.0); M['firey'] = c('firey', (1.0, 0.85, 0.2), emit=(1.0, 0.8, 0.15), emit_strength=9.0)
    M['dirt'] = c('dirt', (0.22, 0.14, 0.08), rough=1.0); M['scorch'] = c('scorch', (0.03, 0.025, 0.02), rough=1.0)
    M['crane'] = c('crane', (0.95, 0.22, 0.08), rough=0.45); M['craned'] = c('craned', (0.65, 0.13, 0.05), rough=0.5); M['cable'] = c('cable', (0.08, 0.08, 0.08), rough=0.5)
    M['lemon'] = c('lemon', (1.0, 0.90, 0.25), rough=0.3, emit=(1.0, 0.85, 0.1), emit_strength=0.35); M['straw'] = c('straw', (0.95, 0.15, 0.2), rough=0.4)
    M['label'] = c('label', (0.98, 0.97, 0.90), rough=0.7); M['ink'] = c('ink', (0.04, 0.04, 0.04), rough=0.6); M['tape'] = c('tape', (0.80, 0.62, 0.35), rough=0.6)
    M['sign'] = c('sign', (0.10, 0.28, 0.62), rough=0.5); M['signt'] = c('signt', (1.0, 0.90, 0.2), rough=0.4, emit=(1.0, 0.85, 0.15), emit_strength=0.5)
    M['shopw'] = c('shopw', (0.93, 0.88, 0.78), rough=0.8); M['awn1'] = c('awn1', (0.85, 0.15, 0.15), rough=0.7); M['awn2'] = c('awn2', (0.97, 0.97, 0.95), rough=0.7)
    M['pframe'] = c('pframe', (0.32, 0.18, 0.09), rough=0.6); M['rug'] = c('rug', (0.78, 0.20, 0.24), rough=1.0); M['white'] = c('white', (0.97, 0.97, 0.95), rough=0.6)
    M['tyre'] = c('tyre', (0.05, 0.05, 0.06), rough=0.85); M['light'] = c('light', (1.0, 0.85, 0.3), emit=(1.0, 0.8, 0.2), emit_strength=3.0)
    return M

def bulldozer(coll, M):
    """ruspa: lama davanti verso -Y, origine a terra al centro. Restituisce dict(root, blade)."""
    B = {}; r = B['root'] = empty('Ruspa', (0, 0, 0), None, coll)
    mb = MB([M['dozer'], M['dozerd'], M['track'], M['steel'], M['glass'], M['dark'], M['light']])
    mb.b2((-0.78, -1.25, 0.55), (0.78, 1.55, 1.25), 0); mb.b2((-0.66, -1.20, 1.25), (0.66, -0.05, 1.62), 1); mb.b2((-0.62, 0.0, 1.25), (0.62, 1.35, 2.35), 0)
    mb.b2((-0.64, 0.14, 1.62), (0.64, 1.2, 2.2), 4); mb.b2((-0.5, -0.03, 1.62), (0.5, 0.02, 2.2), 4); mb.b2((-0.70, -0.08, 2.35), (0.70, 1.42, 2.47), 1)
    mb.b2((0.35, -0.75, 1.62), (0.47, -0.63, 2.3), 5); mb.b2((-0.45, -1.27, 1.32), (-0.22, -1.24, 1.5), 6); mb.b2((0.22, -1.27, 1.32), (0.45, -1.24, 1.5), 6)
    for sx in (-1, 1):
        x0, x1 = (0.80, 1.18) if sx > 0 else (-1.18, -0.80); mb.b2((x0, -1.3, 0.12), (x1, 1.6, 0.62), 2); mb.b2((x0, -1.5, 0.22), (x1, 1.8, 0.52), 2)
    o = mb.build('RuspaCorpo', coll); o.parent = r
    for sx in (-1, 1):
        for k in range(4): cyl('RuspaRuota', 0.24, 0.42, (sx * 0.99, -1.25 + 0.95 * k, 0.37), M['steel'], coll, rot=(0, PI / 2, 0), parent=r)
    bl = B['blade'] = empty('RuspaLama', (0, -1.55, 0.55), r, coll)
    mbb = MB([M['steel'], M['dozerd']]); mbb.b2((-1.45, -0.42, -0.5), (1.45, -0.30, 0.55), 0); mbb.b2((-1.45, -0.50, -0.5), (1.45, -0.30, -0.36), 0)
    for sx in (-1, 1): mbb.b2((sx * 0.72 - 0.06, -0.32, -0.12), (sx * 0.72 + 0.06, 0.5, 0.02), 1); mbb.b2((sx * 1.45 - 0.05, -0.55, -0.5), (sx * 1.45 + 0.05, -0.30, 0.55), 0)
    ob = mbb.build('RuspaLamaGeo', coll); ob.parent = bl
    return B

def meteor(coll, M, A, size=2.6):
    """meteorite: masso vero della libreria + alone di fuoco + etichetta di spedizione. Origine al centro. Restituisce dict(root, rock, flames, label)."""
    R = {}; r = R['root'] = empty('Meteorite', (0, 0, 0), None, coll)
    rock = R['rock'] = A.modello('boulder_01', altezza=size, collezione=coll); rock.parent = r; rock.location = (0, 0, -size * 0.5)
    for o in rock.children_recursive:
        if o.type == 'MESH':
            for sl in o.material_slots:
                m = sl.material
                if m and m.node_tree and not m.node_tree.nodes.get('PT_dark'):
                    b = next((n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
                    if b: b.inputs['Emission Color'].default_value = (1.0, 0.25, 0.02, 1); b.inputs['Emission Strength'].default_value = 0.35; b.name = 'PT_dark'
    fl = R['flames'] = empty('MeteoFiamme', (0, 0, 0), r, coll); rg = np.random.default_rng(3)
    for k in range(22):
        t = k / 21.0; s = size * (0.75 - 0.5 * t) * rg.uniform(0.8, 1.15)
        ball_('MeteoFuoco', 1.0, (rg.uniform(-0.25, 0.25) * size * t, rg.uniform(-0.25, 0.25) * size * t, size * (0.25 + 2.6 * t)), M['fire'] if k % 3 else M['firey'], coll, parent=fl, sc=(s * 0.6, s * 0.6, s * 0.85))
    lb = R['label'] = empty('MeteoEtichetta', (0, -size * 0.52, -0.1), r, coll)
    obj('EtichettaCarta', set004.box_c(), (0, 0, 0), (1.5, 0.03, 0.8), M['label'], coll, parent=lb); obj('EtichettaNastro', set004.box_c(), (0, 0.005, 0.32), (1.7, 0.03, 0.14), M['tape'], coll, parent=lb)
    text_obj(coll, 'EtichettaT1', 'PER: GUALTIERO', 0.15, M['ink'], (0, -0.03, 0.05), parent=lb); text_obj(coll, 'EtichettaT2', 'CONSEGNA IN GIORNATA', 0.095, M['ink'], (0, -0.03, -0.2), parent=lb)
    return R

def crane(coll, M, boom=13.0):
    """autogru: muso verso -Y, origine a terra. turret ruota su Z, boom si alza su X (0 = orizzontale verso +Y). Restituisce dict(root, turret, boom, boom_len, pivot_h)."""
    C = {}; r = C['root'] = empty('Gru', (0, 0, 0), None, coll)
    mb = MB([M['crane'], M['craned'], M['glass'], M['dark'], M['steel'], M['light']])
    mb.b2((-1.15, -3.4, 0.55), (1.15, 3.2, 1.25), 0); mb.b2((-1.1, -3.4, 1.25), (1.1, -1.9, 2.35), 0); mb.b2((-1.12, -3.25, 1.6), (1.12, -2.05, 2.2), 2); mb.b2((-0.95, -3.43, 1.6), (0.95, -3.38, 2.2), 2)
    mb.b2((-1.2, -3.5, 0.45), (1.2, -3.35, 0.7), 3)
    for sx in (-1, 1): mb.b2((sx * 1.15 - 0.1, -0.2, 0.3), (sx * 1.15 + 0.1, 0.2, 0.6), 4); mb.b2((sx * 0.8 - 0.14, -3.44, 0.85), (sx * 0.8 + 0.14, -3.40, 1.05), 5)
    o = mb.build('GruCarro', coll); o.parent = r
    for sx in (-1, 1):
        for y in (-2.5, -0.3, 1.0, 2.4): cyl('GruRuota', 0.5, 0.4, (sx * 1.0, y, 0.5), M['tyre'], coll, rot=(0, PI / 2, 0), parent=r)
    tu = C['turret'] = empty('GruTorretta', (0, 0.9, 1.25), r, coll)
    mt = MB([M['craned'], M['crane'], M['glass'], M['steel']]); mt.b2((-0.9, -1.0, 0.0), (0.9, 1.3, 0.9), 1); mt.b2((-0.95, 1.3, 0.0), (0.95, 2.1, 0.8), 0); mt.b2((-1.0, -1.15, 0.2), (-0.2, -0.2, 1.6), 1); mt.b2((-1.02, -1.0, 0.75), (-0.18, -0.3, 1.45), 2)
    ot = mt.build('GruTorrettaGeo', coll); ot.parent = tu
    bo = C['boom'] = empty('GruBraccio', (0.3, 0.0, 1.1), tu, coll)
    mbm = MB([M['crane'], M['steel']]); mbm.b2((-0.28, -0.6, -0.28), (0.28, boom * 0.55, 0.28), 0); mbm.b2((-0.2, boom * 0.5, -0.2), (0.2, boom, 0.2), 1); mbm.b2((-0.3, boom - 0.25, -0.35), (0.3, boom + 0.1, 0.25), 0)
    obm = mbm.build('GruBraccioGeo', coll); obm.parent = bo
    C['boom_len'] = boom; C['pivot'] = (0.3, 0.9, 2.35)
    return C

def lemonade(coll, M, parent=None, loc=(0, 0, 0), s=1.0):
    g = empty('Limonata', loc, parent, coll); g.scale = (s, s, s)
    cyl('LimBicchiere', 0.062, 0.17, (0, 0, 0.085), M['glass'], coll, parent=g); cyl('LimSucco', 0.054, 0.13, (0, 0, 0.075), M['lemon'], coll, parent=g)
    cyl('LimCannuccia', 0.008, 0.26, (0.02, 0, 0.16), M['straw'], coll, rot=(0, 0.25, 0), parent=g); ball_('LimFetta', 1.0, (-0.06, 0, 0.17), M['lemon'], coll, parent=g, sc=(0.012, 0.045, 0.045))
    return g

def hole(coll, M, w=2.4, h=2.0, seed=1, n=13):
    """buco frastagliato da mettere davanti a un muro (piano XZ, guarda verso -Y). Origine al centro."""
    rg = np.random.default_rng(seed); g = empty('Buco', (0, 0, 0), None, coll)
    ball_('BucoC', 1.0, (0, 0, 0), M['hole'], coll, parent=g, sc=(w * 0.42, 0.015, h * 0.42))
    for k in range(n):
        a = 2 * PI * k / n + rg.uniform(-0.2, 0.2); rr = rg.uniform(0.18, 0.3)
        ball_('BucoB', 1.0, (w * 0.36 * math.cos(a), 0, h * 0.36 * math.sin(a)), M['hole'], coll, parent=g, sc=(w * rr, 0.015, h * rr * rg.uniform(0.7, 1.1)))
    return g

def rubble(coll, mats, n=40, R=1.6, seed=1, size=(0.18, 0.42), heap=0.7):
    """mucchio di macerie (mattoni e pezzi di intonaco). Origine a terra al centro."""
    rg = np.random.default_rng(seed); g = empty('Macerie', (0, 0, 0), None, coll)
    for k in range(n):
        d = R * math.sqrt(rg.uniform(0, 1)); a = rg.uniform(0, 2 * PI); z = heap * max(0.0, 1 - d / R) * rg.uniform(0.2, 1.0) + 0.06
        sz = rg.uniform(*size)
        obj('Maceria', set004.box_c(), (d * math.cos(a), d * math.sin(a), z), (sz, sz * rg.uniform(0.4, 0.7), sz * rg.uniform(0.3, 0.6)), mats[int(rg.integers(0, len(mats)))], coll,
            rot=(rg.uniform(-0.6, 0.6), rg.uniform(-0.6, 0.6), rg.uniform(0, PI)), parent=g)
    return g

def crater(coll, M, R=4.5, seed=2):
    """cratere: disco bruciato, anello di terra smossa, crepe. Origine a terra al centro."""
    rg = np.random.default_rng(seed); g = empty('Cratere', (0, 0, 0), None, coll)
    cyl('CratereBruciato', R * 1.45, 0.02, (0, 0, 0.012), M['scorch'], coll, parent=g); cyl('CratereFondo', R * 0.8, 0.03, (0, 0, 0.02), M['hole'], coll, parent=g)
    for k in range(34):
        a = 2 * PI * k / 34 + rg.uniform(-0.08, 0.08); rr = R * rg.uniform(0.85, 1.05); s = rg.uniform(0.5, 0.95)
        ball_('CratereTerra', 1.0, (rr * math.cos(a), rr * math.sin(a), 0.1), M['dirt'], coll, parent=g, sc=(s * 1.2, s * 1.2, s * 0.7))
    for k in range(9):
        a = rg.uniform(0, 2 * PI); L = rg.uniform(1.5, 3.5)
        obj('CratereCrepa', set004.box_c(), ((R * 1.3 + L / 2) * math.cos(a), (R * 1.3 + L / 2) * math.sin(a), 0.016), (L, 0.09, 0.01), M['scorch'], coll, rot=(0, 0, a), parent=g)
    return g

def smoke_column(coll, M, n=14, h=9.0, r0=0.9, seed=4, name='Fumo'):
    rg = np.random.default_rng(seed); g = empty(name, (0, 0, 0), None, coll); balls = []
    for k in range(n):
        t = k / (n - 1); balls.append(ball_(name + 'B', r0 * (0.7 + 1.5 * t) * rg.uniform(0.85, 1.15), (rg.uniform(-0.4, 0.4) * (0.5 + t), rg.uniform(-0.4, 0.4) * (0.5 + t), 0.6 + h * t), M['smoke'], coll, parent=g))
    return g, balls

def flames(coll, M, n=7, R=1.2, seed=5, name='Fiamme'):
    rg = np.random.default_rng(seed); g = empty(name, (0, 0, 0), None, coll); fl = []
    for k in range(n):
        a = rg.uniform(0, 2 * PI); d = R * rg.uniform(0, 1); s = rg.uniform(0.25, 0.5)
        f = shape(name + 'F', 'cone', (d * math.cos(a), d * math.sin(a), s * 1.1), scale=(s, s, s * 2.2), parent=g, mat=M['fire'] if k % 2 else M['firey'], coll=coll); fl.append(f)
    return g, fl

def ferramenta_set(coll, M, x0, A):
    """negozio di ferramenta: facciata verso -Y a y=3, insegna, vetrina con i martelli veri, porta, tenda a strisce, marciapiede. Restituisce la posizione della porta."""
    mb = MB([M['shopw'], M['dark'], M['glass'], M['sign'], M['awn1'], M['awn2'], M['steel'], M['white']])
    mb.b2((x0 - 5.5, 3.0, 0.0), (x0 + 5.5, 3.5, 5.4), 0); mb.b2((x0 + 1.7, 2.94, 0.0), (x0 + 2.9, 3.0, 2.35), 1); mb.b2((x0 - 3.9, 2.9, 0.85), (x0 + 0.9, 3.0, 2.55), 2)
    mb.b2((x0 - 4.0, 2.86, 0.75), (x0 + 1.0, 2.94, 0.85), 7); mb.b2((x0 - 4.0, 2.86, 2.55), (x0 + 1.0, 2.94, 2.65), 7); mb.b2((x0 - 4.3, 2.84, 3.45), (x0 + 4.3, 3.0, 4.75), 3)
    for k in range(12):
        xa = x0 - 4.2 + k * 0.7; mb.b2((xa, 2.0, 2.78 + 0.0), (xa + 0.7, 3.0, 2.86), 4 if k % 2 else 5); mb.b2((xa, 1.96, 2.62), (xa + 0.7, 2.02, 2.86), 4 if k % 2 else 5)
    mb.b2((x0 - 3.8, 2.3, 0.0), (x0 + 0.8, 2.9, 0.85), 0); mb.b2((x0 + 1.55, 2.9, 2.35), (x0 + 3.05, 3.0, 2.47), 7)
    mb.build('Ferramenta', coll)
    bx('FerramentaTerra', (x0 - 30, -30, -0.12), (x0 + 30, 3.0, 0.0), bpy.data.materials.get('PT_PavingStones070') or M['shopw'], coll)
    text_obj(coll, 'FerramentaInsegna', 'FERRAMENTA', 0.86, M['signt'], (x0, 2.8, 3.78))
    for k, (aid, hh) in enumerate((('cross_pein_hammer', 0.55), ('sledgehammer_01', 1.2), ('wooden_hammer_01', 0.55), ('cross_pein_hammer', 0.7), ('sledgehammer_01', 1.35))):
        A.modello(aid, posizione=(x0 - 3.3 + k * 0.95, 2.55, 0.86), altezza=hh, rotazione=20 * k, collezione=coll)
    return (x0 + 2.3, 2.9)

def photo_frame(coll, M, path, loc, w=0.8, h=1.0, rotz=0.0, name='Foto'):
    """quadro con una foto (immagine su file): guarda verso -Y."""
    g = empty(name, loc, None, coll); g.rotation_euler = (0, 0, rotz)
    obj(name + 'Cornice', set004.box_c(), (0, 0, 0), (w + 0.12, 0.05, h + 0.12), M['pframe'], coll, parent=g)
    me = bpy.data.meshes.new(name + 'Img'); me.from_pydata([(-w / 2, 0, -h / 2), (w / 2, 0, -h / 2), (w / 2, 0, h / 2), (-w / 2, 0, h / 2)], [], [(0, 1, 2, 3)])
    uv = me.uv_layers.new()
    for i, co in enumerate([(0, 0), (1, 0), (1, 1), (0, 1)]): uv.data[i].uv = co
    ob = bpy.data.objects.new(name + 'Img', me); coll.objects.link(ob); ob.parent = g; ob.location = (0, -0.03, 0)
    mt = bpy.data.materials.new(name + 'Mat'); mt.use_nodes = True; nt = mt.node_tree; b = nt.nodes.get('Principled BSDF'); tx = nt.nodes.new('ShaderNodeTexImage'); tx.image = bpy.data.images.load(path, check_existing=True)
    nt.links.new(tx.outputs['Color'], b.inputs['Base Color']); nt.links.new(tx.outputs['Color'], b.inputs['Emission Color']); b.inputs['Emission Strength'].default_value = 0.35; b.inputs['Roughness'].default_value = 0.4
    me.materials.append(mt)
    return g

def salotto_set(coll, M, x0, A, photos=()):
    """salotto di Pippo: pavimento di legno, pareti, divano vero, tappeto, foto di Pippo alle pareti, porta sulla parete sinistra.
    Stanza da x0-3.5 a x0+3.5, y da -3 a 2.5 (parete di fondo). Restituisce dict(sofa=(x,y), door=(x,y), seat_z)."""
    fl = bx('SalottoPavimento', (x0 - 3.5, -3.2, -0.1), (x0 + 3.5, 2.5, 0.0), A.materiale('WoodFloor043', dimensione=1.6, nome='PT_salotto_pav'), coll)
    wall = A.materiale('Plaster001', dimensione=2.4, rilievo=0.5, tinta=(1.2, 1.05, 0.8), nome='PT_salotto_muro')
    bx('SalottoFondo', (x0 - 3.6, 2.5, 0.0), (x0 + 3.6, 2.62, 3.1), wall, coll); bx('SalottoDx', (x0 + 3.5, -3.2, 0.0), (x0 + 3.62, 2.5, 3.1), wall, coll)
    bx('SalottoSxA', (x0 - 3.62, 0.2, 0.0), (x0 - 3.5, 2.5, 3.1), wall, coll); bx('SalottoSxB', (x0 - 3.62, -3.2, 0.0), (x0 - 3.5, -1.0, 3.1), wall, coll); bx('SalottoSxC', (x0 - 3.62, -1.0, 2.25), (x0 - 3.5, 0.2, 3.1), wall, coll)
    bx('SalottoBattiscopa', (x0 - 3.5, 2.44, 0.0), (x0 + 3.5, 2.5, 0.14), M['white'], coll)
    obj('SalottoTappeto', set004.box_c(), (x0 + 0.2, 0.3, 0.012), (3.4, 2.2, 0.02), M['rug'], coll)
    sofa = A.modello('sofa_03', posizione=(x0 + 0.2, 1.75, 0.0), altezza=1.0, rotazione=0, collezione=coll)
    for k, p in enumerate(photos[:3]): photo_frame(coll, M, p, (x0 - 1.9 + 2.1 * k, 2.42, 2.05), 0.95, 0.95, name='FotoPippo%d' % k)
    return dict(sofa=(x0 + 0.2, 1.75), door=(x0 - 3.5, -0.4), root=sofa)
