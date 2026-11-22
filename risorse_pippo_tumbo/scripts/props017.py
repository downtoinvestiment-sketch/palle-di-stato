"""Test 017 - IL BAMBINO NON ESCE: porticina con il cartello OCCUPATO, rivista, manina, collare, cappello dell'agente, calendario, biberon,
sala parto con il buco nel muro, discoteca (guscio, pista a mattonelle luminose, console, palla a specchi, corda di velluto),
cuffie per Tumbo, occhiali da sole per Gualtiero, neonato che balla in una mesh sola (leggera, da ripetere 200 volte)."""
import math, random, bpy, bmesh
from mathutils import Vector, Matrix
from common import material, shape, empty, shared_mesh
import set004
from set004 import MB, obj, cyl, ball_, bx
from props007 import text_obj
PI = math.pi

def disco_mat(name):
    """palla a specchi: metallo lucido con tasselli che brillano."""
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (0.85, 0.87, 0.95, 1); b.inputs['Metallic'].default_value = 1.0; b.inputs['Roughness'].default_value = 0.12
    tc = nt.nodes.new('ShaderNodeTexCoord'); vo = nt.nodes.new('ShaderNodeTexVoronoi'); vo.inputs['Scale'].default_value = 9.0
    nt.links.new(tc.outputs['Object'], vo.inputs['Vector'])
    bw = nt.nodes.new('ShaderNodeRGBToBW'); nt.links.new(vo.outputs['Color'], bw.inputs['Color'])
    gt = nt.nodes.new('ShaderNodeMath'); gt.operation = 'GREATER_THAN'; gt.inputs[1].default_value = 0.55; nt.links.new(bw.outputs['Val'], gt.inputs[0])
    mul = nt.nodes.new('ShaderNodeMath'); mul.operation = 'MULTIPLY'; mul.inputs[1].default_value = 1.6; nt.links.new(gt.outputs[0], mul.inputs[0])
    nt.links.new(mul.outputs[0], b.inputs['Emission Strength']); b.inputs['Emission Color'].default_value = (1, 1, 1, 1)
    return m

def mats017():
    c = lambda n, col, **k: material('P17_' + n, col, **k); M = {}
    M['wood'] = c('wood', (0.48, 0.25, 0.10), rough=0.45); M['woodd'] = c('woodd', (0.30, 0.15, 0.06), rough=0.5); M['frame'] = c('frame', (0.98, 0.96, 0.90), rough=0.5)
    M['gold'] = c('gold', (1.0, 0.74, 0.20), rough=0.25, metallic=0.9); M['hole'] = c('hole', (0.02, 0.0, 0.03), rough=1.0, emit=(0.7, 0.05, 0.55), emit_strength=0.5)
    M['occ'] = c('occ', (0.85, 0.04, 0.04), rough=0.4, emit=(1.0, 0.04, 0.02), emit_strength=1.3); M['txt'] = c('txt', (1, 1, 1), rough=0.5, emit=(1, 1, 1), emit_strength=1.0)
    M['paper'] = c('paper', (0.86, 0.85, 0.80), rough=0.9); M['ink'] = c('ink', (0.05, 0.05, 0.08), rough=0.6); M['redink'] = c('redink', (0.9, 0.08, 0.06), rough=0.5)
    M['cover'] = c('cover', (0.98, 0.35, 0.55), rough=0.35); M['cover2'] = c('cover2', (1.0, 0.85, 0.2), rough=0.4)
    M['skin'] = [c('skin0', (1.0, 0.78, 0.66), rough=0.6), c('skin1', (0.80, 0.55, 0.40), rough=0.6), c('skin2', (0.50, 0.32, 0.22), rough=0.6)]
    M['diaper'] = [c('diaper0', (0.97, 0.97, 0.97), rough=0.8), c('diaper1', (0.6, 0.85, 1.0), rough=0.8), c('diaper2', (1.0, 0.7, 0.85), rough=0.8)]
    M['paci'] = [c('paci0', (0.1, 0.9, 1.0), rough=0.3, emit=(0.1, 0.9, 1.0), emit_strength=1.4), c('paci1', (1.0, 0.9, 0.1), rough=0.3, emit=(1.0, 0.85, 0.1), emit_strength=1.4),
                 c('paci2', (1.0, 0.2, 0.8), rough=0.3, emit=(1.0, 0.15, 0.8), emit_strength=1.4)]
    M['black'] = c('black', (0.02, 0.02, 0.03), rough=0.3); M['hair'] = c('hair', (0.35, 0.2, 0.08), rough=0.9)
    M['collar'] = c('collar', (0.92, 0.08, 0.14), rough=0.6); M['cap'] = c('cap', (0.05, 0.12, 0.40), rough=0.6)
    M['tile'] = [c('tile%d' % i, col, rough=0.3, emit=col, emit_strength=1.8) for i, col in enumerate([(1.0, 0.1, 0.6), (0.1, 0.8, 1.0), (1.0, 0.8, 0.1), (0.5, 0.2, 1.0)])]
    M['grout'] = c('grout', (0.02, 0.02, 0.03), rough=0.4); M['booth'] = c('booth', (0.07, 0.05, 0.11), rough=0.4)
    M['led'] = c('led', (1, 0.1, 0.7), rough=0.3, emit=(1.0, 0.1, 0.7), emit_strength=1.9); M['ledc'] = c('ledc', (0.1, 0.9, 1.0), rough=0.3, emit=(0.1, 0.9, 1.0), emit_strength=1.9)
    M['vinyl'] = c('vinyl', (0.02, 0.02, 0.02), rough=0.25); M['label'] = c('label', (1.0, 0.3, 0.1), rough=0.5)
    M['screen'] = c('screen', (0.2, 0.6, 1.0), rough=0.2, emit=(0.3, 0.7, 1.0), emit_strength=1.8); M['velvet'] = c('velvet', (0.65, 0.02, 0.08), rough=0.9); M['carpet'] = c('carpet', (0.7, 0.03, 0.06), rough=0.95)
    M['chrome'] = c('chrome', (0.85, 0.87, 0.9), rough=0.15, metallic=1.0); M['lens'] = c('lens', (0.01, 0.01, 0.015), rough=0.08, spec=1.0, coat=1.0)
    M['band'] = c('band', (0.08, 0.08, 0.1), rough=0.4); M['cup'] = c('cup', (0.1, 0.85, 1.0), rough=0.3, emit=(0.1, 0.8, 1.0), emit_strength=1.2)
    M['milk'] = c('milk', (0.97, 0.97, 0.95), rough=0.4); M['nipple'] = c('nipple', (1.0, 0.6, 0.3), rough=0.4)
    M['brick'] = c('brick', (0.72, 0.30, 0.20), rough=0.9); M['blackout'] = c('blackout', (0, 0, 0), rough=1.0)
    M['ball'] = disco_mat('P17_ball')
    return M

def testo(coll, name, body, size, mat, loc, font=None, parent=None, rot=(PI / 2, 0, 0), spessore=0.004):
    """scritta 3D come props007.text_obj, ma con un font della libreria (percorso del file .ttf)."""
    o = text_obj(coll, name, body, size, mat, loc, rot=rot, parent=parent); o.data.extrude = spessore
    if font:
        try: o.data.font = bpy.data.fonts.load(font, check_existing=True)
        except Exception as ex: print('font', ex)
    return o

def torus_mesh(name, R, r, nu=32, nv=12):
    me = bpy.data.meshes.new(name); vs = []; fs = []
    for i in range(nu):
        a = 2 * PI * i / nu
        for j in range(nv):
            b = 2 * PI * j / nv; vs.append(((R + r * math.cos(b)) * math.cos(a), (R + r * math.cos(b)) * math.sin(a), r * math.sin(b)))
    for i in range(nu):
        for j in range(nv): fs.append((i * nv + j, ((i + 1) % nu) * nv + j, ((i + 1) % nu) * nv + (j + 1) % nv, i * nv + (j + 1) % nv))
    me.from_pydata(vs, [], fs); me.update()
    for p in me.polygons: p.use_smooth = True
    return me

def arco_mesh(name, R, r, a0, a1, nu=24, nv=10):
    """arco nel piano XZ, centrato sull'origine: angolo 0 = +Z."""
    me = bpy.data.meshes.new(name); vs = []; fs = []
    for i in range(nu + 1):
        a = a0 + (a1 - a0) * i / nu
        for j in range(nv):
            b = 2 * PI * j / nv; rr = R + r * math.cos(b); vs.append((rr * math.sin(a), r * math.sin(b) * 1.8, rr * math.cos(a)))
    for i in range(nu):
        for j in range(nv): fs.append((i * nv + j, (i + 1) * nv + j, (i + 1) * nv + (j + 1) % nv, i * nv + (j + 1) % nv))
    me.from_pydata(vs, [], fs); me.update()
    for p in me.polygons: p.use_smooth = True
    return me

# ======================= sala parto =======================
def porticina(coll, M, parent, loc, font=None):
    """porticina sulla pancia di Eleonora, fronte -Y. dict(root, leaf = perno del battente (rotazione Z negativa = si apre in fuori),
    sign = cartello OCCUPATO (scala 0..1), glow = luce che esce quando e' aperta)."""
    D = {}; g = D['root'] = empty('Porticina', loc, parent, coll)
    mb = MB([M['frame'], M['hole'], M['gold']])
    for (p0, p1) in (((-0.122, -0.012, -0.148), (-0.092, 0.09, 0.148)), ((0.092, -0.012, -0.148), (0.122, 0.09, 0.148)), ((-0.122, -0.012, 0.118), (0.122, 0.09, 0.148)), ((-0.122, -0.012, -0.148), (0.122, 0.09, -0.118))): mb.b2(p0, p1, 0)
    mb.b2((-0.092, 0.0, -0.118), (0.092, 0.09, 0.118), 1)                                       # il vano scuro (con un filo di luce viola)
    mb.b2((0.128, -0.022, -0.012), (0.148, -0.01, 0.012), 2)                                    # campanello
    o = mb.build('PorticinaCassa', coll); o.parent = g
    pv = D['leaf'] = empty('PorticinaPerno', (-0.092, -0.016, 0), g, coll)
    ml = MB([M['wood'], M['woodd']]); ml.b2((0.0, -0.01, -0.118), (0.184, 0.008, 0.118), 0)
    for (z0, z1) in ((-0.098, -0.012), (0.012, 0.098)): ml.b2((0.022, -0.015, z0), (0.162, -0.009, z1), 1)
    l = ml.build('PorticinaBattente', coll); l.parent = pv
    ball_('PorticinaPomello', 0.016, (0.155, -0.026, 0.0), M['gold'], coll, parent=pv)
    sg = D['sign'] = empty('CartelloOccupato', (0, -0.02, 0.17), g, coll)
    obj('OccTarga', set004.box_c(), (0, 0, 0.05), (0.30, 0.016, 0.085), M['occ'], coll, parent=sg)
    testo(coll, 'OccTesto', 'OCCUPATO', 0.05, M['txt'], (0, -0.011, 0.048), font=font, parent=sg)
    lg = bpy.data.lights.new('LucePorticina', 'POINT'); lg.color = (1.0, 0.15, 0.8); lg.energy = 0.0; lg.shadow_soft_size = 0.08
    lo = D['glow'] = bpy.data.objects.new('LucePorticina', lg); coll.objects.link(lo); lo.parent = g; lo.location = (0, -0.14, 0)
    return D

def rivista(coll, M, parent, loc, rot, font=None):
    """rivista aperta: copertina verso -Y, pagine verso +Y (chi legge). Restituisce (radice, perno della pagina che gira: rotazione Z)."""
    g = empty('Rivista', loc, parent, coll); g.rotation_euler = rot
    mb = MB([M['cover'], M['paper'], M['cover2']])
    for sx in (-1, 1):
        mb.box((sx * 0.058, -0.004 + 0.010, 0.0), (0.118, 0.006, 0.165), 0, rz=sx * 0.2); mb.box((sx * 0.058, 0.004 + 0.010, 0.0), (0.110, 0.005, 0.155), 1, rz=sx * 0.2)
    mb.box((0.058, -0.008 + 0.010, 0.05), (0.10, 0.003, 0.04), 2, rz=0.2)
    o = mb.build('RivistaGeo', coll); o.parent = g
    pg = empty('RivistaPagina', (0, 0.012, 0), g, coll)
    obj('RivistaFoglio', set004.box_c(), (0.054, 0.004, 0), (0.106, 0.002, 0.15), M['paper'], coll, parent=pg)
    t = testo(coll, 'RivistaTitolo', 'ZUCCHINE\nOGGI', 0.02, M['ink'], (0.058, 0.0, 0.05), font=font, parent=g); t.rotation_euler = (PI / 2, 0, 0.2); t.location = (0.058, -0.004, 0.05)
    return g, pg

def manina(coll, M):
    """braccino che esce dalla porticina: si allunga verso -Y dall'origine."""
    g = empty('Manina', (0, 0, 0), None, coll)
    shape('ManinaBraccio', 'cap:0.015:0.2', (0, -0.1, 0), rot=(PI / 2, 0, 0), parent=g, mat=M['skin'][0], coll=coll)
    ball_('ManinaMano', 0.03, (0, -0.22, 0), M['skin'][0], coll, parent=g)
    for dx in (-0.022, 0.0, 0.022): ball_('ManinaDito', 0.012, (dx, -0.248, 0.008), M['skin'][0], coll, parent=g)
    return g

def collare(coll, M):
    g = empty('CollareTumbo', (0, 0, 0), None, coll)
    me = torus_mesh('CollareAnello', 0.15, 0.03); me.materials.append(M['collar']); o = bpy.data.objects.new('CollareAnello', me); coll.objects.link(o); o.parent = g
    ball_('CollareMedaglia', 1.0, (0, -0.185, -0.02), M['gold'], coll, parent=g, sc=(0.045, 0.014, 0.045))
    return g

def cappello(coll, M):
    """berretto dell'agente da solo (quello che resta fuori dalla porticina): fascia nera, cupola larga, visiera, stemma. Origine sotto."""
    g = empty('CappelloAgente', (0, 0, 0), None, coll)
    cyl('CappFascia', 0.25, 0.11, (0, 0.0, 0.055), M['black'], coll, parent=g); cyl('CappCupola', 0.34, 0.06, (0, 0.0, 0.14), M['cap'], coll, parent=g)
    ball_('CappCupolaSu', 1.0, (0, 0, 0.17), M['cap'], coll, parent=g, sc=(0.34, 0.34, 0.06))
    ball_('CappVisiera', 1.0, (0, -0.25, 0.02), M['black'], coll, parent=g, sc=(0.24, 0.2, 0.025)); ball_('CappStemma', 0.06, (0, -0.25, 0.1), M['gold'], coll, parent=g)
    return g

def calendario(coll, M, loc, font=None):
    """calendario a muro con i giorni sbarrati: faccia verso -Y."""
    g = empty('Calendario', loc, None, coll)
    mb = MB([M['paper'], M['redink'], M['ink']])
    mb.b2((-0.38, -0.5, 0.0), (0.38, 0.5, 0.02), 0); mb.b2((-0.38, 0.30, 0.02), (0.38, 0.5, 0.026), 1)
    for r in range(4):
        for c_ in range(6):
            x = -0.29 + c_ * 0.116; y = 0.17 - r * 0.16
            if r == 3 and c_ == 5: mb.box((x, y, 0.024), (0.07, 0.07, 0.004), 1); continue
            for s in (1, -1): mb.box((x, y, 0.024), (0.105, 0.02, 0.004), 2, rz=s * 0.8)
    o = mb.build('CalendarioGeo', coll); o.parent = g; o.rotation_euler = (PI / 2, 0, 0)
    testo(coll, 'CalTesto', 'PARTO', 0.12, M['txt'], (0, -0.03, 0.40), font=font, parent=g)
    return g

def biberon(coll, M, loc, s=1.0, parent=None, k=0):
    g = empty('Biberon', loc, parent, coll); g.scale = (s, s, s)
    cyl('BibCorpo', 0.045, 0.14, (0, 0, 0.07), M['milk'], coll, parent=g); cyl('BibGhiera', 0.048, 0.03, (0, 0, 0.155), M['paci'][k % 3], coll, parent=g)
    ball_('BibTettarella', 1.0, (0, 0, 0.19), M['nipple'], coll, parent=g, sc=(0.025, 0.025, 0.035))
    return g

HY0, HY1, HZ = -4.0, 0.6, 2.9
def stanza(coll, M, mwall, mfloor, mwhite):
    """sala parto: pavimento da (-4.1, -7.5) a (6.6, 3.1), pareti alte 3.3, soffitto. Nella parete est (x = 6.5) c'e' il buco per il camion.
    Restituisce (stanza, tappo che chiude il buco, macerie e mattoni sul bordo)."""
    mb = MB([mwall, mfloor, mwhite])
    mb.b2((-4.1, -7.5, -0.12), (6.6, 3.1, 0.0), 1)
    mb.b2((-4.1, 3.0, 0.0), (6.6, 3.1, 3.3), 0); mb.b2((-4.1, -7.5, 0.0), (-4.0, 3.1, 3.3), 0); mb.b2((-4.1, -7.6, 0.0), (6.6, -7.5, 3.3), 0)
    mb.b2((6.5, -7.5, 0.0), (6.6, HY0, 3.3), 0); mb.b2((6.5, HY1, 0.0), (6.6, 3.0, 3.3), 0); mb.b2((6.5, HY0, HZ), (6.6, HY1, 3.3), 0)
    mb.b2((-4.1, -7.6, 3.3), (6.6, 3.1, 3.4), 2); mb.b2((-4.0, 2.95, 0.0), (6.5, 2.97, 0.12), 2); mb.b2((-3.98, -7.5, 0.0), (-3.96, 3.0, 0.12), 2)
    room = mb.build('SalaParto', coll)
    pl = MB([mwall, mwhite]); pl.b2((6.5, HY0, 0.0), (6.6, HY1, HZ), 0); pl.b2((6.48, HY0, 0.0), (6.5, HY1, 0.12), 1); plug = pl.build('MuroTappo', coll)
    rb = MB([M['brick'], mwall]); rnd = random.Random(3)
    for k in range(34):                                                                          # mattoni sul bordo del buco
        u = rnd.random()
        if k % 3 == 0: p = (6.55, HY0 + (HY1 - HY0) * u, HZ + rnd.uniform(-0.1, 0.1))
        else: p = (6.55, HY0 if k % 3 == 1 else HY1, HZ * u)
        rb.box((p[0] + rnd.uniform(-0.05, 0.05), p[1] + rnd.uniform(-0.12, 0.12), max(0.06, p[2])), (0.16, 0.30, 0.13), 0, rx=rnd.uniform(-0.5, 0.5), rz=rnd.uniform(-0.3, 0.3))
    for k in range(46):                                                                          # macerie a terra, dentro la stanza
        x = 6.3 - abs(rnd.gauss(0, 1.1)); y = rnd.uniform(HY0 + 0.2, HY1 - 0.2)
        if 3.2 < x and -2.9 < y < -0.5: y = HY0 + 0.4 if y < -1.7 else HY1 - 0.4              # lascia libero il passaggio del camion
        rb.box((x, y, rnd.uniform(0.05, 0.1)), (rnd.uniform(0.12, 0.3), rnd.uniform(0.12, 0.3), rnd.uniform(0.08, 0.16)), k % 2, rx=rnd.uniform(-0.4, 0.4), rz=rnd.uniform(0, 3))
    rubble = rb.build('Macerie', coll)
    return room, plug, rubble

# ======================= discoteca =======================
def discoteca(coll, M, mwall, mfloor, x0):
    """guscio della discoteca: pavimento da x0-9 a x0+9 e da y=-9.5 a 7, pareti alte 6.5, soffitto scuro, palco in fondo, tappeto rosso e tende all'ingresso."""
    mb = MB([mwall, mfloor, M['booth'], M['carpet'], M['velvet']])
    mb.b2((x0 - 9, -9.5, -0.12), (x0 + 9, 7.0, 0.0), 1)
    mb.b2((x0 - 9.1, 6.9, 0), (x0 + 9.1, 7.0, 6.5), 0); mb.b2((x0 - 9.1, -9.6, 0), (x0 + 9.1, -9.5, 6.5), 0); mb.b2((x0 - 9.1, -9.5, 0), (x0 - 9.0, 7.0, 6.5), 0); mb.b2((x0 + 9.0, -9.5, 0), (x0 + 9.1, 7.0, 6.5), 0)
    mb.b2((x0 - 9.1, -9.6, 6.5), (x0 + 9.1, 7.0, 6.6), 2)
    mb.b2((x0 - 5.2, 3.4, 0.0), (x0 + 5.2, 6.9, 0.7), 2); mb.b2((x0 - 5.2, 3.38, 0.6), (x0 + 5.2, 3.4, 0.7), 3)
    mb.b2((x0 - 0.9, -9.5, 0.0), (x0 + 0.9, -4.7, 0.012), 3)
    for sx in (-1, 1):
        for k in range(8): mb.b2((x0 + sx * (0.9 + k * 0.42) - 0.17, -9.46 + 0.05 * (k % 2), 0.0), (x0 + sx * (0.9 + k * 0.42) + 0.17, -9.38 + 0.05 * (k % 2), 4.4), 4)
    return mb.build('Discoteca', coll)

def pista(coll, M, cx, cy, nx, ny, lato=0.9, seme=5):
    """pista a mattonelle luminose di quattro colori (M['tile']): una mesh sola."""
    rnd = random.Random(seme); mb = MB(M['tile'] + [M['grout']]); w, d = nx * lato, ny * lato
    mb.b2((cx - w / 2 - 0.12, cy - d / 2 - 0.12, 0.0), (cx + w / 2 + 0.12, cy + d / 2 + 0.12, 0.03), 4)
    for i in range(nx):
        for j in range(ny):
            x = cx - w / 2 + i * lato; y = cy - d / 2 + j * lato
            mb.b2((x + 0.03, y + 0.03, 0.03), (x + lato - 0.03, y + lato - 0.03, 0.045), (i + 2 * j + rnd.randrange(2)) % 4)
    return mb.build('Pista', coll)

def console(coll, M):
    """banco del DJ: fronte -Y, piano a z = 1.0. Restituisce (radice, [piatti])."""
    g = empty('ConsoleDJ', (0, 0, 0), None, coll)
    mb = MB([M['booth'], M['led'], M['ledc'], M['screen'], M['chrome']])
    mb.b2((-1.7, -0.45, 0.0), (1.7, 0.45, 1.0), 0)
    mb.b2((-1.7, -0.47, 0.78), (1.7, -0.45, 0.86), 1); mb.b2((-1.7, -0.47, 0.12), (1.7, -0.45, 0.2), 2)
    for k in range(9): mb.b2((-1.4 + k * 0.35 - 0.11, -0.47, 0.3), (-1.4 + k * 0.35 + 0.11, -0.45, 0.36 + 0.3 * abs(math.sin(k * 1.7 + 0.4))), 1 if k % 2 else 2)
    mb.b2((-0.28, -0.25, 1.0), (0.28, 0.25, 1.06), 4)
    mb.b2((1.2, 0.0, 1.0), (1.62, 0.3, 1.02), 4); mb.box((1.41, 0.32, 1.17), (0.42, 0.02, 0.3), 3, rx=-0.2)
    o = mb.build('ConsoleGeo', coll); o.parent = g; plat = []
    for sx in (-0.72, 0.72):
        p = cyl('Piatto', 0.3, 0.03, (sx, 0.0, 1.03), M['vinyl'], coll, parent=g); cyl('PiattoEtichetta', 0.1, 0.034, (0, 0, 0.0), M['label'], coll, parent=p)
        obj('PiattoTacca', set004.box_c(), (0.2, 0, 0.017), (0.12, 0.02, 0.004), M['chrome'], coll, parent=p); plat.append(p)
    return g, plat

def palla_specchi(coll, M, r=0.55):
    g = empty('PallaSpecchi', (0, 0, 0), None, coll)
    me = bpy.data.meshes.new('PallaSpecchiGeo'); bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=28, v_segments=16, radius=r); bm.to_mesh(me); bm.free()
    me.materials.append(M['ball']); o = bpy.data.objects.new('PallaSpecchiGeo', me); coll.objects.link(o); o.parent = g
    cyl('PallaFilo', 0.012, 2.4, (0, 0, r + 1.2), M['chrome'], coll, parent=g)
    return g

def corda(coll, M, x0, x1, y):
    """corda di velluto tra due paletti dorati."""
    g = empty('CordaVelluto', (0, 0, 0), None, coll)
    for x in (x0, x1):
        cyl('Paletto', 0.035, 1.0, (x, y, 0.5), M['gold'], coll, parent=g); cyl('PalettoBase', 0.16, 0.04, (x, y, 0.02), M['gold'], coll, parent=g); ball_('PalettoPomo', 0.06, (x, y, 1.03), M['gold'], coll, parent=g)
    n = 18
    for k in range(n + 1):
        u = k / n; ball_('CordaNodo', 0.042, (x0 + (x1 - x0) * u, y, 0.95 - 0.28 * math.sin(PI * u)), M['velvet'], coll, parent=g)
    return g

def cuffie(coll, M, head, R=0.305):
    """cuffie da DJ sulla testa di Tumbo."""
    g = empty('Cuffie', (0, 0.02, 0.0), head, coll)
    me = arco_mesh('CuffieArco', R, 0.022, -1.45, 1.45); me.materials.append(M['band']); o = bpy.data.objects.new('CuffieArco', me); coll.objects.link(o); o.parent = g
    for sx in (-1, 1):
        ball_('CuffiaPad', 1.0, (sx * (R - 0.01), 0, 0.03), M['band'], coll, parent=g, sc=(0.06, 0.12, 0.13)); ball_('CuffiaLuce', 1.0, (sx * (R + 0.035), 0, 0.03), M['cup'], coll, parent=g, sc=(0.03, 0.085, 0.09))
    return g

def occhiali(coll, M, head):
    """occhiali da sole e auricolare per Gualtiero buttafuori."""
    g = empty('OcchialiDaSole', (0, 0, 0), head, coll)
    for sx in (-1, 1):
        ball_('OccLente', 1.0, (sx * 0.118, -0.266, 0.07), M['lens'], coll, parent=g, sc=(0.108, 0.034, 0.084))
        obj('OccAsta', set004.box_c(), (sx * 0.25, -0.11, 0.085), (0.02, 0.32, 0.025), M['lens'], coll, parent=g)
    obj('OccPonte', set004.box_c(), (0, -0.288, 0.09), (0.08, 0.02, 0.022), M['lens'], coll, parent=g)
    ball_('Auricolare', 0.035, (0.31, -0.02, -0.03), M['frame'], coll, parent=g)
    return g

def _ico(bm, c, s, mi, sub=2, rot=None):
    vs = bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=1.0)['verts']
    for v in vs:
        p = Vector((v.co.x * s[0], v.co.y * s[1], v.co.z * s[2]))
        if rot is not None: p = rot @ p
        v.co = p + Vector(c)
    for f in set(f for v in vs for f in v.link_faces): f.material_index = mi; f.smooth = True

def neonato_mesh(name, mats, braccia_su=False):
    """neonato seduto con il ciuccio, in una mesh sola e leggera (circa 1.500 triangoli). mats = [pelle, pannolino, nero, ciuccio, capelli].
    Fronte -Y, origine sotto il pannolino, alto 0.56."""
    bm = bmesh.new()
    _ico(bm, (0, 0, 0.09), (0.13, 0.11, 0.09), 1); _ico(bm, (0, 0, 0.2), (0.10, 0.09, 0.11), 0); _ico(bm, (0, 0, 0.36), (0.14, 0.14, 0.14), 0, sub=3)
    for sx in (-1, 1):
        _ico(bm, (sx * 0.05, -0.125, 0.38), (0.022, 0.012, 0.026), 2); _ico(bm, (sx * 0.14, 0, 0.36), (0.035, 0.035, 0.035), 0)
        if braccia_su: _ico(bm, (sx * 0.14, -0.02, 0.31), (0.033, 0.033, 0.085), 0, rot=Matrix.Rotation(sx * 0.5, 3, 'Y'))
        else: _ico(bm, (sx * 0.11, -0.03, 0.22), (0.035, 0.035, 0.07), 0)
        _ico(bm, (sx * 0.06, -0.09, 0.04), (0.04, 0.07, 0.035), 0)
    _ico(bm, (0, -0.02, 0.51), (0.03, 0.03, 0.054), 4); _ico(bm, (0, -0.142, 0.31), (0.036, 0.014, 0.036), 3); _ico(bm, (0, -0.16, 0.31), (0.015, 0.012, 0.015), 3)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for m in mats: me.materials.append(m)
    return me

def lista(coll, M, parent, loc, font=None):
    """la lista del buttafuori: tutti dentro, Pippo no. Faccia scritta verso -Y, come props016b.clipboard."""
    g = empty('ListaBTF', loc, parent, coll)
    mb = MB([M['wood'], M['paper'], M['chrome'], M['redink'], material('P17_ok', (0.1, 0.7, 0.2), rough=0.5)])
    mb.b2((-0.2, -0.01, -0.27), (0.2, 0.01, 0.27), 0); mb.b2((-0.18, -0.016, -0.25), (0.18, -0.01, 0.2), 1); mb.b2((-0.07, -0.03, 0.2), (0.07, -0.01, 0.25), 2)
    for k in range(4): mb.b2((0.11, -0.02, 0.085 - k * 0.062 - 0.016), (0.145, -0.016, 0.085 - k * 0.062 + 0.016), 4)      # spunte verdi
    o = mb.build('ListaGeo', coll); o.parent = g
    xs = MB([M['redink']])                                                                                             # PIPPO: riga rossa sopra il nome e croce nella casella (costruite in piano, poi alzate)
    xs.box((-0.035, 0.0, 0.0), (0.24, 0.007, 0.004), 0)
    for s_ in (1, -1): xs.box((0.128, 0.0, 0.0), (0.075, 0.014, 0.004), 0, rz=s_ * 0.8)
    x = xs.build('ListaCroce', coll); x.parent = g; x.rotation_euler = (PI / 2, 0, 0); x.location = (0, -0.026, -0.152)
    testo(coll, 'ListaTitolo', 'LISTA', 0.062, M['ink'], (0, -0.018, 0.145), font=font, parent=g)
    for k, nome in enumerate(('TUMBO', 'AGENTE', 'POMPIERI', '200 NEONATI')): testo(coll, 'ListaNome%d' % k, nome, 0.034, M['ink'], (-0.035, -0.018, 0.085 - k * 0.062), font=font, parent=g)
    testo(coll, 'ListaPippo', 'PIPPO', 0.044, M['ink'], (-0.035, -0.018, -0.17), font=font, parent=g)
    return g

def carrello(coll, M):
    """carrello d'ospedale con il vassoio a z = 0.57 (ci sta sopra il panino). Origine a terra."""
    g = empty('Carrello', (0, 0, 0), None, coll); mb = MB([M['chrome'], M['frame']])
    mb.b2((-0.42, -0.42, 0.53), (0.42, 0.42, 0.57), 1); mb.b2((-0.03, -0.03, 0.06), (0.03, 0.03, 0.53), 0); mb.b2((-0.3, -0.04, 0.03), (0.3, 0.04, 0.07), 0); mb.b2((-0.04, -0.3, 0.03), (0.04, 0.3, 0.07), 0)
    o = mb.build('CarrelloGeo', coll); o.parent = g
    for (x, y) in ((-0.28, 0), (0.28, 0), (0, -0.28), (0, 0.28)): ball_('CarrelloRuota', 0.035, (x, y, 0.035), M['black'], coll, parent=g)
    return g
