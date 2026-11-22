"""Test 012 - PIPPO E LA ZUCCHINA ELEONORA: zucchina, tavolino, rosa, bomba, orto, fungo, moto-prete."""
import math, bpy, numpy as np
from common import material, shape, empty, shared_mesh
import set004
from set004 import MB, obj, cyl, ball_
from props007 import text_obj
PI = math.pi

def mats012():
    c = lambda n, col, **k: material('Z12_' + n, col, **k); M = {}
    M['zuc'] = c('zuc', (0.07, 0.30, 0.06), rough=0.35, spec=0.6); M['zucl'] = c('zucl', (0.35, 0.60, 0.20), rough=0.4); M['stem'] = c('stem', (0.45, 0.55, 0.25), rough=0.8)
    M['white'] = c('white', (1, 1, 1), rough=0.4); M['black'] = c('black', (0.02, 0.02, 0.03), rough=0.4); M['lip'] = c('lip', (0.95, 0.10, 0.25), rough=0.3)
    M['shoe'] = c('shoe', (0.95, 0.15, 0.45), rough=0.4); M['veil'] = c('veil', (1, 1, 1), rough=0.9, emit=(1, 1, 1), emit_strength=0.15)
    M['table'] = c('table', (0.55, 0.32, 0.14), rough=0.6); M['cloth'] = c('cloth', (0.95, 0.30, 0.45), rough=0.8); M['tag'] = c('tag', (1.0, 0.95, 0.8), rough=0.7)
    M['rose'] = c('rose', (0.90, 0.03, 0.08), rough=0.5); M['green'] = c('green', (0.10, 0.45, 0.10), rough=0.6)
    M['bulb'] = c('bulb', (1.0, 0.95, 0.4), rough=0.3, emit=(1.0, 0.9, 0.3), emit_strength=4.0); M['steel'] = c('steel', (0.72, 0.75, 0.80), rough=0.3, metallic=0.8)
    M['bomb'] = c('bomb', (0.16, 0.20, 0.18), rough=0.4, metallic=0.5); M['byel'] = c('byel', (1.0, 0.80, 0.05), rough=0.5); M['tape'] = c('tape', (0.75, 0.70, 0.60), rough=0.6)
    M['red'] = c('red', (0.9, 0.08, 0.05), rough=0.4, emit=(1, 0.05, 0.02), emit_strength=2.0)
    M['soil'] = c('soil', (0.22, 0.13, 0.07), rough=1.0); M['cab'] = c('cab', (0.45, 0.75, 0.30), rough=0.7); M['carrot'] = c('carrot', (1.0, 0.45, 0.05), rough=0.5); M['tom'] = c('tom', (0.95, 0.10, 0.06), rough=0.3)
    M['fire'] = c('fire', (1.0, 0.45, 0.05), rough=1.0, emit=(1.0, 0.35, 0.02), emit_strength=3.5); M['fire2'] = c('fire2', (1.0, 0.85, 0.3), rough=1.0, emit=(1.0, 0.8, 0.2), emit_strength=6.0)
    M['smoke'] = c('smoke', (0.30, 0.28, 0.27), rough=1.0); M['flash'] = c('flash', (1, 1, 1), rough=1.0, emit=(1, 1, 1), emit_strength=12.0)
    M['moto'] = c('moto', (0.08, 0.08, 0.10), rough=0.3, spec=0.8); M['chrome'] = c('chrome', (0.85, 0.87, 0.9), rough=0.12, metallic=1.0); M['rubber'] = c('rubber', (0.05, 0.05, 0.06), rough=0.8)
    M['seat'] = c('seat', (0.35, 0.18, 0.08), rough=0.6); M['lamp'] = c('lamp', (1.0, 0.97, 0.8), rough=0.2, emit=(1.0, 0.95, 0.7), emit_strength=1.5); M['collar'] = c('collar', (1, 1, 1), rough=0.5, emit=(1, 1, 1), emit_strength=0.3)
    M['crater'] = c('crater', (0.10, 0.08, 0.07), rough=1.0)
    return M

ZL = 1.0; ZR = 0.115
def zucchina(coll, M):
    """Eleonora: zucchina lunga ZL, asse +Z, origine alla base. Occhi/bocca/gambe/velo si accendono a parte. Fronte -Y."""
    Z = {}; r = Z['root'] = empty('Eleonora', (0, 0, 0), None, coll)
    shape('ZucCorpo', 'cap:%.3f:%.3f' % (ZR, ZL - 2 * ZR), (0, 0, ZL / 2), parent=r, mat=M['zuc'], coll=coll)
    for k in range(6):
        a = 2 * PI * k / 6 + 0.3; obj('ZucRiga', set004.box_c(), (ZR * 0.97 * math.cos(a), ZR * 0.97 * math.sin(a), ZL / 2), (0.012, 0.035, ZL * 0.72), M['zucl'], coll, rot=(0, 0, a), parent=r)
    cyl('ZucPicciolo', 0.035, 0.09, (0, 0, ZL + 0.03), M['stem'], coll, parent=r); ball_('ZucFiore', 0.03, (0, 0, 0.0), M['byel'], coll, parent=r)
    f = -ZR; ez = ZL * 0.70; Z['eyes'] = e = empty('ZucOcchi', (0, 0, 0), r, coll)
    for sx in (-1, 1):
        ball_('ZucOcchio', 1.0, (sx * 0.055, f + 0.005, ez), M['white'], coll, parent=e, sc=(0.05, 0.03, 0.062)); ball_('ZucPupilla', 1.0, (sx * 0.055, f - 0.02, ez - 0.004), M['black'], coll, parent=e, sc=(0.024, 0.014, 0.03))
        for j in (-1, 0, 1): obj('ZucCiglia', set004.box_c(), (sx * 0.055 + j * 0.028, f - 0.012, ez + 0.07), (0.008, 0.008, 0.04), M['black'], coll, rot=(0, j * 0.45, 0), parent=e)
    Z['mouth'] = ball_('ZucBocca', 1.0, (0, f - 0.002, ZL * 0.56), M['lip'], coll, parent=r, sc=(0.045, 0.02, 0.022))
    Z['legs'] = lg = empty('ZucGambe', (0, 0, 0), r, coll)
    for sx in (-1, 1): cyl('ZucGamba', 0.018, 0.32, (sx * 0.05, 0, -0.14), M['zuc'], coll, parent=lg); ball_('ZucScarpa', 1.0, (sx * 0.05, -0.03, -0.31), M['shoe'], coll, parent=lg, sc=(0.04, 0.07, 0.03))
    Z['veil'] = v = empty('ZucVelo', (0, 0, ZL), r, coll)
    ball_('VeloTop', 1.0, (0, 0.02, 0.0), M['veil'], coll, parent=v, sc=(0.16, 0.16, 0.06))
    obj('VeloDietro', set004.box_c(), (0, 0.17, -0.30), (0.34, 0.02, 0.62), M['veil'], coll, rot=(-0.3, 0, 0), parent=v)
    return Z

def table(coll, M, name='ELEONORA'):
    """tavolino con cuscino e cartellino: piano a z=0.80."""
    r = empty('Tavolino', (0, 0, 0), None, coll); mb = MB([M['table'], M['cloth'], M['tag']])
    mb.b2((-0.75, -0.32, 0.72), (0.75, 0.32, 0.78), 0); mb.b2((-0.62, -0.20, 0.78), (0.62, 0.20, 0.82), 1)
    for sx in (-0.65, 0.65):
        for sy in (-0.24, 0.24): mb.box((sx, sy, 0.36), (0.07, 0.07, 0.72), 0)
    mb.box((0, -0.34, 0.62), (0.62, 0.02, 0.16), 2)
    o = mb.build('TavolinoCorpo', coll); o.parent = r
    text_obj(coll, 'TavolinoNome', name, 0.085, M['black'], (0, -0.352, 0.59), parent=r)
    return r

def rose(coll, M, sh):
    """rosa nella mano (figlia della spalla): stelo lungo il braccio."""
    g = empty('Rosa', (0, -0.05, -0.66), sh, coll)
    cyl('RosaStelo', 0.012, 0.42, (0, 0, -0.21), M['green'], coll, parent=g)
    for k, (dx, dy, s) in enumerate([(0, 0, 0.07), (0.035, 0.01, 0.055), (-0.03, 0.02, 0.055), (0.0, -0.035, 0.05)]): ball_('RosaPetalo', s, (dx, dy, -0.45), M['rose'], coll, parent=g)
    ball_('RosaFoglia', 1.0, (0.04, 0, -0.22), M['green'], coll, parent=g, sc=(0.05, 0.01, 0.025))
    return g

def bulb(coll, M):
    g = empty('Lampadina', (0, 0, -50), None, coll); ball_('LampVetro', 0.16, (0, 0, 0.1), M['bulb'], coll, parent=g); cyl('LampAttacco', 0.07, 0.11, (0, 0, -0.07), M['steel'], coll, parent=g)
    return g

def bomb(coll, M):
    """bomba atomica da cartone: asse +Z (punta in alto), origine al centro. Lunga ~1.5."""
    g = empty('Bomba', (0, 0, 0), None, coll)
    ball_('BombaCorpo', 1.0, (0, 0, 0.1), M['bomb'], coll, parent=g, sc=(0.36, 0.36, 0.62)); cyl('BombaCoda', 0.16, 0.5, (0, 0, -0.6), M['bomb'], coll, parent=g)
    for k in range(4):
        a = PI / 2 * k + PI / 4; obj('BombaAletta', set004.box_c(), (0.2 * math.cos(a), 0.2 * math.sin(a), -0.72), (0.3, 0.03, 0.34), M['byel'], coll, rot=(0, 0, a), parent=g)
    cyl('BombaFascia', 0.365, 0.14, (0, 0, 0.12), M['byel'], coll, parent=g); ball_('BombaPunta', 0.1, (0, 0, 0.7), M['red'], coll, parent=g)
    for k in range(3):                                                                      # simbolo a tre spicchi
        a = 2 * PI * k / 3; ball_('BombaSpicchio', 1.0, (0.1 * math.cos(a), -0.345, 0.38 + 0.1 * math.sin(a)), M['byel'], coll, parent=g, sc=(0.055, 0.015, 0.055))
    tapes = []
    for k, (z, rz) in enumerate([(0.42, 0.3), (-0.12, -0.25), (-0.36, 0.15)]):
        tapes.append(cyl('BombaScotch', 0.37 - 0.13 * (k == 2) - 0.02 * (k == 1), 0.07, (0, 0, z), M['tape'], coll, rot=(0.12 * (k - 1), rz * 0.3, 0), parent=g))
    return g, tapes

def orto(coll, M, w=5.0, d=4.0, seed=3):
    """orto del vicino: aiuole con cavoli, carote, pomodori. Origine al centro."""
    rg = np.random.default_rng(seed); r = empty('Orto', (0, 0, 0), None, coll); mb = MB([M['soil'], M['table']])
    for i in range(4): mb.b2((-w / 2, -d / 2 + i * d / 4 + 0.12, 0), (w / 2, -d / 2 + (i + 1) * d / 4 - 0.12, 0.10), 0)
    o = mb.build('OrtoTerra', coll); o.parent = r
    for i in range(4):
        y = -d / 2 + (i + 0.5) * d / 4
        for j in range(7):
            x = -w / 2 + 0.4 + j * (w - 0.8) / 6
            if i % 3 == 0: ball_('Cavolo', 0.2, (x, y, 0.24), M['cab'], coll, parent=r, sc=(1, 1, 0.8))
            elif i % 3 == 1:
                shape('Carota', 'cone', (x, y, 0.08), scale=(0.05, 0.05, 0.16), parent=r, mat=M['carrot'], coll=coll); ball_('CarotaCiuffo', 0.08, (x, y, 0.3), M['green'], coll, parent=r, sc=(0.6, 0.6, 1.2))
            else:
                obj('PomPalo', set004.box_c(), (x, y, 0.45), (0.03, 0.03, 0.9), M['table'], coll, parent=r); ball_('PomChioma', 0.2, (x, y, 0.6), M['green'], coll, parent=r)
                for (dx, dz) in ((0.14, 0.5), (-0.13, 0.66)): ball_('Pomodoro', 0.07, (x + dx, y - 0.12, dz), M['tom'], coll, parent=r)
    return r

def mushroom(coll, M):
    """fungo atomico: origine a terra, alto ~14 (scalare l'empty)."""
    r = empty('Fungo', (0, 0, 0), None, coll)
    cyl('FungoGambo', 1.3, 8.0, (0, 0, 4.0), M['smoke'], coll, parent=r); ball_('FungoBase', 1.0, (0, 0, 0.4), M['smoke'], coll, parent=r, sc=(4.5, 4.5, 1.2))
    ball_('FungoCappello', 1.0, (0, 0, 10.0), M['fire'], coll, parent=r, sc=(5.5, 5.5, 3.0)); ball_('FungoCuore', 1.0, (0, 0, 9.4), M['fire2'], coll, parent=r, sc=(3.6, 3.6, 2.0))
    for k in range(9):
        a = 2 * PI * k / 9; ball_('FungoSbuffo', 1.0, (4.6 * math.cos(a), 4.6 * math.sin(a), 9.2), M['smoke'] if k % 2 else M['fire'], coll, parent=r, sc=(2.0, 2.0, 1.5))
    ball_('FungoAnello', 1.0, (0, 0, 6.2), M['smoke'], coll, parent=r, sc=(3.0, 3.0, 0.5))
    return r

def moto(coll, M):
    """moto-prete: fronte -Y, origine a terra sotto il centro. Sella a z~0.85. Restituisce (root, faro[empty per la 'faccia'], ruote)."""
    r = empty('Moto', (0, 0, 0), None, coll); wheels = []
    for y in (-0.85, 0.85):
        w = empty('MotoRuota', (0, y, 0.36), r, coll); cyl('MotoGomma', 0.36, 0.16, (0, 0, 0), M['rubber'], coll, rot=(0, PI / 2, 0), parent=w); cyl('MotoCerchio', 0.2, 0.17, (0, 0, 0), M['chrome'], coll, rot=(0, PI / 2, 0), parent=w)
        obj('MotoRaggio', set004.box_c(), (0, 0, 0), (0.18, 0.5, 0.05), M['chrome'], coll, parent=w); wheels.append(w)
    mb = MB([M['moto'], M['chrome'], M['seat']])
    mb.box((0, -0.15, 0.78), (0.34, 0.75, 0.30), 0); mb.box((0, 0.45, 0.82), (0.36, 0.80, 0.12), 2); mb.box((0, 0.0, 0.5), (0.26, 0.9, 0.3), 1)
    mb.box((0, -0.72, 0.75), (0.07, 0.07, 0.85), 1, rx=-0.35); mb.box((0, -0.62, 1.2), (0.85, 0.05, 0.05), 1)
    for sx in (-1, 1): mb.box((sx * 0.2, 0.75, 0.42), (0.09, 0.9, 0.09), 1); mb.box((sx * 0.42, -0.62, 1.2), (0.14, 0.07, 0.07), 0)
    mb.box((0, 0.95, 0.72), (0.3, 0.5, 0.06), 0)
    o = mb.build('MotoCorpo', coll); o.parent = r
    face = empty('MotoFaccia', (0, -0.85, 1.08), r, coll)
    ball_('MotoFaro', 0.19, (0, 0, 0), M['lamp'], coll, parent=face, sc=(1, 0.6, 1))
    for sx in (-1, 1): ball_('MotoOcchio', 1.0, (sx * 0.07, -0.105, 0.04), M['black'], coll, parent=face, sc=(0.028, 0.015, 0.045))
    mouth = ball_('MotoBocca', 1.0, (0, -0.105, -0.07), M['black'], coll, parent=face, sc=(0.06, 0.015, 0.02))
    cyl('MotoColletto', 0.2, 0.07, (0, 0.02, -0.2), M['moto'], coll, parent=face); obj('MotoCollarino', set004.box_c(), (0, -0.19, -0.2), (0.1, 0.03, 0.065), M['collar'], coll, parent=face)
    cyl('MotoCappelloTesa', 0.27, 0.025, (0, 0.0, 0.19), M['moto'], coll, parent=face); ball_('MotoCappello', 1.0, (0, 0, 0.23), M['moto'], coll, parent=face, sc=(0.15, 0.15, 0.09))
    return r, face, wheels, mouth


# ======================= scenario dopo la bomba =======================
def mats_nuke():
    c = lambda n, col, **k: material('NK_' + n, col, **k); M = {}
    M['char'] = c('char', (0.07, 0.065, 0.06), rough=1.0); M['brick'] = c('brick', (0.20, 0.13, 0.10), rough=1.0); M['conc'] = c('conc', (0.26, 0.25, 0.24), rough=1.0)
    M['ash'] = c('ash', (0.20, 0.18, 0.16), rough=1.0)
    M['smoke'] = c('smoke', (0.16, 0.13, 0.12), rough=1.0, emit=(1.0, 0.30, 0.05), emit_strength=0.10); M['smoked'] = c('smoked', (0.07, 0.06, 0.06), rough=1.0)
    M['glow'] = c('glow', (1.0, 0.30, 0.03), rough=1.0, emit=(1.0, 0.16, 0.01), emit_strength=1.6); M['core'] = c('core', (1.0, 0.6, 0.15), rough=1.0, emit=(1.0, 0.42, 0.06), emit_strength=2.4)
    M['ember'] = c('ember', (1.0, 0.5, 0.1), rough=1.0, emit=(1.0, 0.4, 0.05), emit_strength=8.0); M['flake'] = c('flake', (0.55, 0.53, 0.5), rough=1.0)
    M['wave'] = c('wave', (0.45, 0.36, 0.30), rough=1.0)
    m = bpy.data.materials.new('NK_sky'); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear(); N = nt.nodes.new; L = nt.links.new
    geo = N('ShaderNodeNewGeometry'); sep = N('ShaderNodeSeparateXYZ'); mr = N('ShaderNodeMapRange'); mr.inputs['From Min'].default_value = -10; mr.inputs['From Max'].default_value = 230
    ramp = N('ShaderNodeValToRGB'); el = ramp.color_ramp.elements; el[0].position = 0.0; el[0].color = (1.0, 0.42, 0.10, 1); el[1].position = 1.0; el[1].color = (0.05, 0.035, 0.04, 1)
    e2 = el.new(0.22); e2.color = (0.55, 0.20, 0.08, 1); e3 = el.new(0.5); e3.color = (0.20, 0.10, 0.08, 1)
    em = N('ShaderNodeEmission'); em.inputs['Strength'].default_value = 1.0; out = N('ShaderNodeOutputMaterial')
    L(geo.outputs['Position'], sep.inputs[0]); L(sep.outputs['Z'], mr.inputs['Value']); L(mr.outputs['Result'], ramp.inputs['Fac']); L(ramp.outputs['Color'], em.inputs['Color']); L(em.outputs[0], out.inputs['Surface'])
    M['sky'] = m
    return M

def mushroom2(coll, M):
    """fungo atomico grande: origine a terra, alto ~14 unita' (da scalare). Restituisce (root, anello del cappello che rotola)."""
    r = empty('Fungo2', (0, 0, 0), None, coll); rg = np.random.default_rng(7)
    for k in range(9):                                                                   # gambo a sbuffi, piu' largo in basso
        z = 0.6 + k * 0.95; rr = 1.9 - 0.09 * k + 0.25 * math.sin(k * 1.7); ball_('FgGambo', 1.0, (0.15 * math.sin(k * 2.1), 0.15 * math.cos(k * 1.3), z), M['smoke'] if k % 3 else M['smoked'], coll, parent=r, sc=(rr, rr, 0.85))
    ball_('FgFuocoGambo', 1.0, (0, 0, 4.5), M['glow'], coll, parent=r, sc=(1.25, 1.25, 4.3))
    for k in range(16):                                                                  # nube alla base
        a = 2 * PI * k / 16; d = rg.uniform(2.6, 5.2); s = rg.uniform(1.0, 1.9); ball_('FgBase', s, (d * math.cos(a), d * math.sin(a), 0.5 * s), M['smoke'] if k % 2 else M['smoked'], coll, parent=r, sc=(1.2, 1.2, 0.7))
    ball_('FgCappello', 1.0, (0, 0, 10.6), M['smoke'], coll, parent=r, sc=(5.6, 5.6, 2.7)); ball_('FgCappelloAlto', 1.0, (0, 0, 12.0), M['smoked'], coll, parent=r, sc=(3.6, 3.6, 1.9))
    ball_('FgCuore', 1.0, (0, 0, 9.5), M['core'], coll, parent=r, sc=(3.9, 3.9, 1.5)); ball_('FgSotto', 1.0, (0, 0, 9.2), M['glow'], coll, parent=r, sc=(4.9, 4.9, 1.2))
    ring = empty('FgRotolo', (0, 0, 9.9), r, coll)
    for k in range(18):
        a = 2 * PI * k / 18; s = rg.uniform(1.5, 2.1); ball_('FgSbuffo', s, (5.3 * math.cos(a), 5.3 * math.sin(a), rg.uniform(-0.4, 0.4)), M['glow'] if k % 4 == 0 else (M['smoke'] if k % 2 else M['smoked']), coll, parent=ring, sc=(1, 1, 0.8))
    for k in range(12):                                                                  # anello di condensa
        a = 2 * PI * k / 12; ball_('FgAnello', 0.8, (3.4 * math.cos(a), 3.4 * math.sin(a), 6.6), M['wave'], coll, parent=r, sc=(1.5, 1.5, 0.35))
    return r, ring

def ruins(coll, M, items, trunks, seed=5):
    """macerie al posto di case/palazzi: items = [(x, y, w, d, h, rotz)], trunks = [(x, y)]. Una mesh sola."""
    rg = np.random.default_rng(seed); mb = MB([M['char'], M['brick'], M['conc']])
    def P(x, y, lx, ly, rz): c, s = math.cos(rz), math.sin(rz); return (x + c * lx - s * ly, y + s * lx + c * ly)
    for (x, y, w, d, h, rz) in items:
        tall = h > 8; n = 9 if tall else 7
        for k in range(n):                                                               # monconi di muro lungo il perimetro
            side = k % 4; u = rg.uniform(-0.5, 0.5); L = rg.uniform(0.8, 2.0)
            lx, ly = ((u * w, -d / 2), (w / 2, u * d), (u * w, d / 2), (-w / 2, u * d))[side]; px, py = P(x, y, lx, ly, rz)
            hh = rg.uniform(0.5, 2.8) * (2.6 if tall else 1.0); mb.box((px, py, hh / 2), (L if side % 2 == 0 else 0.28, 0.28 if side % 2 == 0 else L, hh), int(rg.integers(0, 3)), rx=rg.uniform(-0.12, 0.12), rz=rz + rg.uniform(-0.1, 0.1))
        if tall:                                                                         # scheletro del palazzo
            for sx in (-1, 1):
                for sy in (-1, 1):
                    hh = rg.uniform(0.25, 0.7) * h; px, py = P(x, y, sx * w * 0.42, sy * d * 0.42, rz); mb.box((px, py, hh / 2), (0.45, 0.45, hh), 2, rx=rg.uniform(-0.05, 0.05), rz=rz)
            for k in range(2): mb.box((x + rg.uniform(-0.5, 0.5), y + rg.uniform(-0.5, 0.5), 2.8 + 3.0 * k), (w * 0.9, d * 0.9, 0.22), 2, rx=rg.uniform(-0.2, 0.2), rz=rz + rg.uniform(-0.1, 0.1))
        for k in range(10 if tall else 7):                                               # macerie a terra
            s = rg.uniform(0.35, 1.0); px, py = P(x, y, rg.uniform(-0.7, 0.7) * w, rg.uniform(-0.7, 0.7) * d, rz); mb.box((px, py, s * 0.25), (s * rg.uniform(0.7, 1.8), s, s * 0.5), int(rg.integers(0, 3)), rx=rg.uniform(-0.4, 0.4), rz=rg.uniform(0, 3))
    for (x, y) in trunks:
        hh = rg.uniform(1.4, 2.6); mb.box((x, y, hh / 2), (0.16, 0.16, hh), 0, rx=rg.uniform(-0.15, 0.15), rz=rg.uniform(0, 3))
        for k in range(2): mb.box((x + rg.uniform(-0.2, 0.2), y, hh * rg.uniform(0.6, 0.95)), (0.7, 0.07, 0.07), 0, rx=0.0, rz=rg.uniform(0, 3))
    return mb.build('Rovine', coll)

def fire(coll, M, s=1.0):
    """focolaio: fiamme (da scalare a ogni fotogramma) + colonna di fumo. Restituisce (root, [fiamme])."""
    r = empty('Fuoco', (0, 0, 0), None, coll); fl = []
    for (dx, dy, k, m) in ((0, 0, 1.0, 'glow'), (0.35, 0.1, 0.7, 'glow'), (-0.3, -0.15, 0.75, 'glow'), (0.05, -0.05, 0.6, 'core')):
        fl.append((shape('FuocoFiamma', 'cone', (dx * s, dy * s, 0.0), scale=(0.34 * s * k, 0.34 * s * k, 1.5 * s * k), parent=r, mat=M[m], coll=coll), k))
    for k in range(4): ball_('FuocoFumo', (0.28 + 0.12 * k) * s, (0.3 * k * s, 0.1 * k * s, (1.6 + 0.8 * k) * s), M['smoke'], coll, parent=r)
    return r, fl

def moto_extras(coll, M, moto_root, face):
    """rifiniture della moto: serbatoio tondo, parafanghi, colletto da prete ben visibile, targa OGGI SPOSI."""
    ball_('MotoSerbatoio', 1.0, (0, -0.2, 0.98), M['moto'], coll, parent=moto_root, sc=(0.24, 0.42, 0.2))
    for y in (-0.85, 0.85): ball_('MotoParafango', 1.0, (0, y, 0.5), M['moto'], coll, parent=moto_root, sc=(0.12, 0.46, 0.32))
    cyl('MotoColletto2', 0.235, 0.10, (0, 0.0, -0.215), M['moto'], coll, parent=face); obj('MotoCollarino2', set004.box_c(), (0, -0.225, -0.215), (0.15, 0.04, 0.085), M['collar'], coll, parent=face)
    sign = empty('MotoTarga', (0, 1.33, 0.92), moto_root, coll); obj('TargaTav', set004.box_c(), (0, 0, 0), (0.9, 0.04, 0.4), M['collar'], coll, parent=sign)
    text_obj(coll, 'TargaTxt', 'OGGI SPOSI', 0.14, M['black'], (0, 0.025, -0.04), rot=(PI / 2, 0, PI), parent=sign)
    return sign
