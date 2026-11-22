"""Test 009 - PIPPO CONTRO GUALTIERO ep. 1: il vicino Gualtiero (pupazzo ricorrente) e gli oggetti della neve ad agosto."""
import math, bpy
from common import material, shape, empty, shared_mesh
import set004
from set004 import MB, obj, cyl, ball_
from props007 import text_obj
PI = math.pi

def mats009():
    c = lambda n, col, **k: material('G9_' + n, col, **k); M = {}
    M['gskin'] = c('skin', (0.97, 0.56, 0.44), rough=0.6); M['gnose'] = c('nose', (0.95, 0.36, 0.30), rough=0.5); M['ghair'] = c('hair', (0.40, 0.38, 0.36), rough=0.9)
    M['tank'] = c('tank', (0.97, 0.97, 0.95), rough=0.7); M['gshorts'] = c('shorts', (0.20, 0.42, 0.30), rough=0.7); M['sock'] = c('sock', (0.96, 0.96, 0.96), rough=0.8)
    M['slipper'] = c('slipper', (0.50, 0.30, 0.14), rough=0.7); M['strap'] = c('strap', (0.10, 0.30, 0.80), rough=0.6)
    M['white'] = c('white', (1, 1, 1), rough=0.4); M['black'] = c('black', (0.03, 0.03, 0.04), rough=0.5); M['tongue'] = c('tongue', (1.0, 0.35, 0.50), rough=0.4)
    M['mouth'] = c('mouth', (0.30, 0.05, 0.06), rough=0.5)
    M['snow'] = c('snow', (1, 1, 1), rough=0.9, emit=(1, 1, 1), emit_strength=0.35); M['ice'] = c('ice', (0.62, 0.86, 1.0), rough=0.1, spec=0.9, emit=(0.5, 0.8, 1.0), emit_strength=0.25)
    M['puddle'] = c('puddle', (0.25, 0.55, 0.95), rough=0.05, spec=1.0); M['steam'] = c('steam', (1, 1, 1), rough=1.0, emit=(1, 1, 1), emit_strength=0.6)
    M['carrot'] = c('carrot', (1.0, 0.45, 0.05), rough=0.5); M['bucket'] = c('bucket', (0.85, 0.12, 0.10), rough=0.4); M['twig'] = c('twig', (0.35, 0.22, 0.10), rough=0.9)
    M['phon'] = c('phon', (0.95, 0.25, 0.65), rough=0.3); M['steel'] = c('steel', (0.75, 0.78, 0.82), rough=0.3, metallic=0.8); M['hot'] = c('hot', (1.0, 0.6, 0.2), rough=1.0, emit=(1.0, 0.5, 0.1), emit_strength=1.5)
    M['fire1'] = c('fire1', (1.0, 0.20, 0.0), rough=1.0, emit=(1.0, 0.10, 0.0), emit_strength=1.5); M['fire2'] = c('fire2', (1.0, 0.85, 0.2), rough=1.0, emit=(1.0, 0.50, 0.03), emit_strength=2.4)
    M['sun'] = c('sun', (1.0, 0.85, 0.1), rough=1.0, emit=(1.0, 0.80, 0.05), emit_strength=3.0)
    M['freezer'] = c('freezer', (0.93, 0.95, 0.97), rough=0.3); M['rubber'] = c('rubber', (0.08, 0.08, 0.09), rough=0.8); M['coal'] = c('coal', (0.06, 0.06, 0.07), rough=0.9)
    M['pop'] = [c('pop%d' % i, col, rough=0.25, spec=0.8) for i, col in enumerate([(1.0, 0.15, 0.25), (1.0, 0.75, 0.05), (0.15, 0.60, 1.0), (0.35, 0.90, 0.30), (0.75, 0.30, 0.95), (1.0, 0.45, 0.05)])]
    M['stick'] = c('stick', (0.90, 0.78, 0.55), rough=0.8); M['vac'] = c('vac', (0.90, 0.12, 0.10), rough=0.3); M['hose'] = c('hose', (0.45, 0.47, 0.50), rough=0.5)
    M['truck'] = c('truck', (1.0, 0.50, 0.04), rough=0.35); M['truckd'] = c('truckd', (0.22, 0.24, 0.28), rough=0.6); M['bed'] = c('bed', (0.20, 0.45, 0.85), rough=0.5)
    M['glass'] = c('glass', (0.10, 0.25, 0.45), rough=0.05, spec=1.0); M['lamp'] = c('lamp', (1.0, 0.95, 0.6), rough=0.3, emit=(1.0, 0.9, 0.5), emit_strength=2.0)
    M['car'] = c('car', (0.75, 0.10, 0.12), rough=0.25, spec=0.9); M['beanie'] = c('beanie', (0.90, 0.10, 0.12), rough=0.9); M['armchair'] = c('armchair', (0.55, 0.25, 0.60), rough=0.8)
    M['tankg'] = c('tankg', (0.35, 0.42, 0.20), rough=0.5)
    return M


def gualtiero(coll, M):
    """Gualtiero, il vicino: canottiera, pancia, baffi, calzini e ciabatte. Fronte -Y, piedi a z=0."""
    R = {}; r = R['root'] = empty('Gualtiero', (0, 0, 0), None, coll); S = lambda *a, **k: shape(*a, coll=coll, **k)
    S('G_Torso', 'cap:0.27:0.26', (0, 0, 1.13), parent=r, mat=M['tank'])
    R['belly'] = S('G_Pancia', 'sphere', (0, -0.10, 1.00), scale=(0.33, 0.31, 0.30), parent=r, mat=M['tank'])
    S('G_Fianchi', 'cap:0.26:0.06', (0, 0, 0.80), parent=r, mat=M['gshorts']); S('G_Collo', 'cyl:0.10:0.1', (0, 0, 1.52), parent=r, mat=M['gskin'])
    h = R['head'] = empty('G_Head', (0, 0, 1.80), r, coll)
    S('G_Cranio', 'sphere', (0, 0, 0), scale=(0.30, 0.28, 0.31), parent=h, mat=M['gskin']); S('G_Naso', 'sphere', (0, -0.29, 0.0), scale=(0.075, 0.075, 0.07), parent=h, mat=M['gnose'])
    for sx, nm in ((-1, 'L'), (1, 'R')):
        S('G_Ciuffo', 'sphere', (sx * 0.26, 0.07, 0.03), scale=(0.09, 0.15, 0.12), parent=h, mat=M['ghair']); S('G_Orecchio', 'sphere', (sx * 0.30, 0.0, -0.03), scale=(0.05, 0.06, 0.08), parent=h, mat=M['gskin'])
        S('G_Occhio', 'sphere', (sx * 0.115, -0.225, 0.07), scale=(0.08, 0.05, 0.09), parent=h, mat=M['white'])
        R['pupil' + nm] = S('G_Pupilla', 'sphere', (sx * 0.115, -0.268, 0.065), scale=(0.035, 0.02, 0.042), parent=h, mat=M['black'])
        R['brow' + nm] = obj('G_Sopracciglio', set004.box_c(), (sx * 0.115, -0.265, 0.185), (0.17, 0.05, 0.055), M['ghair'], coll, rot=(0, -sx * 0.3, 0), parent=h)
        S('G_Baffo', 'sphere', (sx * 0.08, -0.275, -0.085), scale=(0.105, 0.045, 0.05), rot=(0, sx * 0.3, 0), parent=h, mat=M['ghair'])
    R['mouth'] = S('G_Bocca', 'sphere', (0, -0.262, -0.155), scale=(0.09, 0.03, 0.02), parent=h, mat=M['mouth'])
    R['tongue'] = S('G_Lingua', 'sphere', (0, -0.31, -0.20), scale=(0.001, 0.001, 0.001), parent=h, mat=M['tongue'])
    for nm, sx in (('L', -0.36), ('R', 0.36)):
        sh = R['shoulder' + nm] = empty('G_shoulder' + nm, (sx, 0, 1.40), r, coll)
        S('G_Braccio', 'cap:0.09:0.42', (0, 0, -0.30), parent=sh, mat=M['gskin']); S('G_Mano', 'sphere', (0, 0, -0.66), scale=(0.10, 0.10, 0.10), parent=sh, mat=M['gskin'])
        hp = R['hip' + nm] = empty('G_hip' + nm, (sx * 0.40, 0, 0.80), r, coll)
        S('G_Gamba', 'cap:0.10:0.40', (0, 0, -0.34), parent=hp, mat=M['gskin']); S('G_Calzoncino', 'cap:0.135:0.12', (0, 0, -0.10), parent=hp, mat=M['gshorts'])
        S('G_Calzino', 'cap:0.105:0.14', (0, 0, -0.60), parent=hp, mat=M['sock'])
        obj('G_Ciabatta', set004.box_c(), (0, -0.07, -0.775), (0.17, 0.32, 0.05), M['slipper'], coll, parent=hp); obj('G_Fascia', set004.box_c(), (0, -0.13, -0.725), (0.18, 0.11, 0.08), M['strap'], coll, parent=hp)
    return R

def gex(R, f, brow=0.3, mouth=0.25, tongue=0.0, look=(0, 0)):
    """brow>0 arrabbiato, <0 spaventato; mouth 0..1; tongue 0..1."""
    for sx, nm in ((-1, 'L'), (1, 'R')):
        b = R['brow' + nm]; b.rotation_euler = (0, -sx * brow * 0.55, 0); b.keyframe_insert('rotation_euler', frame=f)
        p = R['pupil' + nm]; p.location = (sx * 0.115 + look[0] * 0.03, -0.268, 0.065 + look[1] * 0.03); p.keyframe_insert('location', frame=f)
    m = R['mouth']; m.scale = (0.09 + 0.03 * mouth, 0.03, 0.02 + 0.10 * mouth); m.keyframe_insert('scale', frame=f)
    t = R['tongue']; t.scale = (0.001,) * 3 if tongue <= 0.01 else (0.06, 0.035, 0.05 + 0.08 * tongue); t.keyframe_insert('scale', frame=f)


def hand_tool(coll, M, sh, kind):
    """attrezzo nella mano (figlio della spalla): la canna prosegue il braccio lungo -Z. kind = 'phon' | 'gun'."""
    g = empty('Attrezzo_' + kind, (0, 0, -0.66), sh, coll)
    if kind == 'phon':
        cyl('PhonCanna', 0.10, 0.36, (0, 0, -0.26), M['phon'], coll, parent=g); cyl('PhonBocca', 0.115, 0.06, (0, 0, -0.46), M['steel'], coll, parent=g)
        cyl('PhonRetro', 0.085, 0.05, (0, 0, -0.06), M['black'], coll, parent=g)
    else:
        cyl('LfCanna', 0.045, 0.95, (0, 0, -0.50), M['steel'], coll, parent=g); cyl('LfBocca', 0.07, 0.12, (0, 0, -1.0), M['black'], coll, parent=g)
        cyl('LfCorpo', 0.085, 0.30, (0, 0, -0.14), M['tankg'], coll, parent=g)
    return g

def backpack(coll, M, root):
    g = empty('Bombole', (0, 0.30, 1.18), root, coll)
    for sx in (-1, 1): cyl('Bombola', 0.13, 0.62, (sx * 0.15, 0, 0), M['tankg'], coll, parent=g); ball_('BombolaTesta', 0.13, (sx * 0.15, 0, 0.31), M['tankg'], coll, parent=g)
    obj('BombolaFascia', set004.box_c(), (0, 0, 0.05), (0.60, 0.28, 0.07), M['black'], coll, parent=g)
    return g

def flame(coll, M, parent, loc):
    """fiamma lungo -Z (figlia dell'attrezzo): due gocce emissive. Scala l'empty per accenderla."""
    g = empty('Fiamma', loc, parent, coll)
    ball_('FiammaEst', 1.0, (0, 0, -1.0), M['fire1'], coll, parent=g, sc=(0.34, 0.34, 1.05)); ball_('FiammaInt', 1.0, (0, 0, -0.75), M['fire2'], coll, parent=g, sc=(0.19, 0.19, 0.75))
    return g

def snowman(coll, M):
    r = empty('Pupazzo', (0, 0, 0), None, coll)
    ball_('PupBase', 0.48, (0, 0, 0.42), M['snow'], coll, parent=r); ball_('PupBusto', 0.34, (0, 0, 1.02), M['snow'], coll, parent=r); ball_('PupTesta', 0.25, (0, 0, 1.46), M['snow'], coll, parent=r)
    shape('PupNaso', 'cone', (0, -0.22, 1.46), scale=(0.05, 0.05, 0.26), rot=(PI / 2, 0, 0), parent=r, mat=M['carrot'], coll=coll)
    for sx in (-1, 1):
        ball_('PupOcchio', 0.04, (sx * 0.09, -0.22, 1.54), M['coal'], coll, parent=r)
        obj('PupBraccio', set004.box_c(), (sx * 0.52, 0, 1.12), (0.5, 0.035, 0.035), M['twig'], coll, rot=(0, -sx * 0.5, 0), parent=r)
    for k in range(3): ball_('PupBottone', 0.035, (0, -0.33, 0.90 + 0.13 * k), M['coal'], coll, parent=r)
    cyl('PupSecchio', 0.17, 0.24, (0, 0, 1.78), M['bucket'], coll, parent=r)
    return r

def disc(coll, name, mat, r=1.0, h=0.02): return obj(name, shared_mesh('cyl:1:1'), (0, 0, 0.012), (r, r, h), mat, coll)

def beanie(coll, M, head, cz=0.61, r=0.43):
    g = empty('Berretto', (0, 0, cz), head, coll)
    ball_('BerrettoCalotta', r, (0, 0, -0.02), M['beanie'], coll, parent=g, sc=(1.0, 1.04, 0.80)); cyl('BerrettoBordo', r * 1.09, 0.13, (0, 0, -0.01), M['snow'], coll, parent=g)
    ball_('BerrettoPompon', 0.13, (0, 0, 0.36), M['snow'], coll, parent=g)
    return g

def sun(coll, M, r=2.0):
    g = empty('Sole', (0, 0, 0), None, coll); ball_('SoleDisco', r, (0, 0, 0), M['sun'], coll, parent=g, sc=(1, 0.3, 1))
    for k in range(10):
        a = 2 * PI * k / 10; obj('SoleRaggio', set004.box_c(), (1.55 * r * math.cos(a), 0, 1.55 * r * math.sin(a)), (0.55 * r, 0.12, 0.16 * r), M['sun'], coll, rot=(0, -a, 0), parent=g)
    return g

def freezer(coll, M):
    """congelatore a pozzetto: origine sullo spigolo basso ovest (ci ruota sopra per rovesciarsi verso -X). Restituisce (root, coperchio)."""
    r = empty('Freezer', (0, 0, 0), None, coll); mb = MB([M['freezer'], M['rubber'], M['ice']])
    mb.b2((0, -0.42, 0.06), (1.3, 0.42, 0.80), 0); mb.b2((0.05, -0.37, 0.80), (1.25, 0.37, 0.82), 2)
    for x in (0.1, 1.2):
        for y in (-0.34, 0.34): mb.box((x, y, 0.03), (0.10, 0.10, 0.06), 1)
    o = mb.build('FreezerCorpo', coll); o.parent = r
    lid = empty('FreezerCoperchio', (1.3, 0, 0.82), r, coll); obj('FreezerLid', set004.box_c(), (-0.65, 0, 0.04), (1.32, 0.86, 0.08), M['freezer'], coll, parent=lid)
    obj('FreezerManiglia', set004.box_c(), (-1.30, 0, 0.02), (0.05, 0.3, 0.05), M['rubber'], coll, parent=lid)
    return r, lid

def ice_pile(coll, M, n=46, seed=5):
    import numpy as np
    rg = np.random.default_rng(seed); mb = MB([M['ice']])
    for k in range(n):
        a = rg.uniform(0, 2 * PI); d = abs(rg.normal(0, 0.28)); z = max(0.06, 0.55 - d * 1.1) * rg.uniform(0.2, 1.0); s = rg.uniform(0.10, 0.17)
        mb.box((d * math.cos(a), d * math.sin(a), z), (s, s, s), 0, rx=rg.uniform(0, 1.5), rz=rg.uniform(0, 1.5))
    return mb.build('Ghiaccio', coll)

def barbecue(coll, M):
    """restituisce (root, [fiamme])."""
    r = empty('Barbecue', (0, 0, 0), None, coll)
    ball_('BbqVasca', 0.36, (0, 0, 0.78), M['coal'], coll, parent=r, sc=(1, 1, 0.55)); cyl('BbqGriglia', 0.35, 0.03, (0, 0, 0.82), M['steel'], coll, parent=r)
    for k in range(3):
        a = 2 * PI * k / 3 + 0.5; obj('BbqGamba', set004.box_c(), (0.24 * math.cos(a), 0.24 * math.sin(a), 0.36), (0.035, 0.035, 0.74), M['steel'], coll, parent=r)
    fl = []
    for k, (dx, dy, s, m) in enumerate([(0, 0, 1.0, 'fire1'), (0.14, 0.08, 0.7, 'fire1'), (-0.13, -0.06, 0.75, 'fire1'), (0.02, -0.03, 0.6, 'fire2'), (-0.05, 0.10, 0.45, 'fire2')]):
        f = shape('BbqFiamma', 'cone', (dx, dy, 0.84), scale=(0.17 * s, 0.17 * s, 0.9 * s), parent=r, mat=M[m], coll=coll); fl.append((f, s))
    return r, fl

def popsicle_parts(coll, M, pts):
    """stecchi (una mesh sola) + teste (un oggetto per ghiacciolo). pts = [(x, y)] -> lista di oggetti testa."""
    mb = MB([M['stick']])
    for (x, y) in pts: mb.box((x, y, 0.11), (0.03, 0.012, 0.22), 0)
    mb.build('Stecchi', coll); heads = []
    for k, (x, y) in enumerate(pts):
        heads.append(shape('Ghiacciolo', 'cap:0.075:0.13', (x, y, 0.33), scale=(1, 0.55, 1), mat=M['pop'][(k * 7 + k // 9) % 6], coll=coll))
    return heads

def vacuum(coll, M):
    r = empty('Aspirapolvere', (0, 0, 0), None, coll)
    shape('AspCorpo', 'cap:0.24:0.42', (0, 0, 0.30), rot=(0, PI / 2, 0), parent=r, mat=M['vac'], coll=coll); cyl('AspTappo', 0.10, 0.08, (0, 0, 0.56), M['hose'], coll, parent=r)
    for sx in (-1, 1):
        for sy in (-1, 1): cyl('AspRuota', 0.09, 0.05, (sx * 0.25, sy * 0.24, 0.09), M['rubber'], coll, rot=(PI / 2, 0, 0), parent=r)
    obj('AspManico', set004.box_c(), (0, 0, 0.58), (0.36, 0.05, 0.04), M['rubber'], coll, parent=r)
    return r

def cannon_tube(coll, M, L=1.3):
    """tubo-cannone: origine all'impugnatura, asse +Z verso la bocca."""
    r = empty('Cannone', (0, 0, 0), None, coll)
    cyl('CannoneTubo', 0.10, L, (0, 0, L / 2), M['hose'], coll, parent=r); shape('CannoneBocca', 'cone', (0, 0, L + 0.22), scale=(0.24, 0.24, 0.26), rot=(PI, 0, 0), parent=r, mat=M['vac'], coll=coll)
    cyl('CannoneAnello', 0.125, 0.08, (0, 0, 0.25), M['vac'], coll, parent=r)
    return r

def armchair(coll, M):
    mb = MB([M['armchair'], M['rubber']])
    mb.b2((-0.45, -0.40, 0.12), (0.45, 0.40, 0.42), 0); mb.b2((-0.45, 0.25, 0.42), (0.45, 0.45, 1.0), 0)
    for sx in (-1, 1): mb.b2((sx * 0.45, -0.40, 0.12), (sx * 0.62, 0.45, 0.66), 0)
    for sx in (-0.4, 0.4):
        for sy in (-0.3, 0.35): mb.box((sx, sy, 0.06), (0.08, 0.08, 0.12), 1)
    return mb.build('Poltrona', coll)

def heap(coll, M, name='Mucchio', n=16, seed=3, r=1.0, mat='snow'):
    """mucchio bianco bitorzoluto, origine a terra, raggio ~r, altezza ~0.75 r."""
    import numpy as np
    rg = np.random.default_rng(seed); g = empty(name, (0, 0, 0), None, coll)
    ball_(name + 'C', 0.72 * r, (0, 0, 0.12 * r), M[mat], coll, parent=g, sc=(1, 1, 0.95))
    for k in range(n):
        a = 2 * PI * k / n + rg.uniform(-0.2, 0.2); d = rg.uniform(0.35, 0.72) * r; s = rg.uniform(0.26, 0.42) * r
        ball_(name + 'B', s, (d * math.cos(a), d * math.sin(a), rg.uniform(0.05, 0.38) * r * (1 - d / r) * 2), M[mat], coll, parent=g)
    return g

def truck(coll, M):
    """camion ribaltabile: fronte -Y, lungo 6.4. Restituisce (root, cassone[perno posteriore], carico)."""
    r = empty('Camion', (0, 0, 0), None, coll); mb = MB([M['truck'], M['truckd'], M['glass'], M['lamp'], M['steel']])
    mb.b2((-1.0, -3.0, 0.45), (1.0, 3.2, 0.80), 1)                                              # telaio
    mb.b2((-1.15, -3.2, 0.60), (1.15, -1.25, 2.55), 0)                                          # cabina
    mb.b2((-1.02, -3.23, 1.50), (1.02, -3.18, 2.35), 2)                                         # parabrezza
    for sx in (-1, 1): mb.b2((sx * 1.13, -2.95, 1.55), (sx * 1.17, -1.75, 2.30), 2); mb.b2((sx * 0.65, -3.26, 0.80), (sx * 1.0, -3.18, 1.02), 3)
    mb.b2((-1.2, -3.32, 0.45), (1.2, -3.18, 0.72), 4); mb.b2((-0.7, -3.25, 1.08), (0.7, -3.19, 1.38), 1)   # paraurti, griglia
    mb.b2((0.95, -1.5, 2.55), (1.05, -1.4, 3.3), 4)                                              # scarico
    o = mb.build('CamionCorpo', coll); o.parent = r
    for y in (-2.35, 1.45, 2.6):
        for sx in (-1, 1): cyl('CamionRuota', 0.52, 0.34, (sx * 1.0, y, 0.52), M['rubber'], coll, rot=(0, PI / 2, 0), parent=r); cyl('CamionCerchio', 0.24, 0.36, (sx * 1.0, y, 0.52), M['steel'], coll, rot=(0, PI / 2, 0), parent=r)
    bed = empty('CamionCassone', (0, 3.2, 0.90), r, coll); mbb = MB([M['bed'], M['truckd']])
    mbb.b2((-1.25, -4.3, 0.0), (1.25, 0.0, 0.10), 1); mbb.b2((-1.25, -4.3, 0.0), (1.25, -4.2, 1.25), 0)
    for sx in (-1, 1): mbb.b2((sx * 1.25, -4.3, 0.0), (sx * 1.17, 0.0, 1.05), 0)
    ob = mbb.build('CamionSponde', coll); ob.parent = bed
    for sx in (-1, 1): text_obj(coll, 'CamionScritta', 'POLISTIROLO', 0.42, M['white'], (sx * 1.262, -2.15, 0.55), rot=(PI / 2, 0, sx * PI / 2), parent=bed)
    load = heap(coll, M, 'Carico', n=14, seed=9, r=1.0); load.parent = bed; load.location = (0, -2.15, 0.1); load.scale = (1.2, 2.1, 1.5)
    return r, bed, load

def car(coll, M):
    """utilitaria: fronte -Y."""
    r = empty('Macchina', (0, 0, 0), None, coll); mb = MB([M['car'], M['glass'], M['lamp'], M['steel']])
    mb.b2((-0.85, -2.0, 0.30), (0.85, 2.0, 0.90), 0); mb.b2((-0.76, -0.75, 0.90), (0.76, 1.25, 1.45), 0)
    mb.b2((-0.70, -0.80, 0.95), (0.70, -0.74, 1.40), 1); mb.b2((-0.70, 1.24, 0.95), (0.70, 1.30, 1.40), 1)
    for sx in (-1, 1): mb.b2((sx * 0.74, -0.65, 0.97), (sx * 0.78, 1.15, 1.38), 1); mb.b2((sx * 0.45, -2.04, 0.62), (sx * 0.78, -1.98, 0.80), 2)
    mb.b2((-0.9, -2.08, 0.28), (0.9, -1.96, 0.45), 3)
    o = mb.build('MacchinaCorpo', coll); o.parent = r
    for y in (-1.25, 1.3):
        for sx in (-1, 1): cyl('MacchinaRuota', 0.33, 0.22, (sx * 0.80, y, 0.33), M['rubber'], coll, rot=(0, PI / 2, 0), parent=r)
    return r
