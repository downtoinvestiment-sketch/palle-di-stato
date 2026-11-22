"""Test 014 - IL TOAST DI PIPPO: fetta di pane, forno industriale, vulcano, torri di raffreddamento, catena di montaggio, cucina."""
import math, bpy, bmesh, numpy as np
from common import material, shape, empty, shared_mesh
import set004
from set004 import MB, obj, cyl, ball_
from props007 import text_obj
PI = math.pi

def mats014():
    c = lambda n, col, **k: material('T14_' + n, col, **k); M = {}
    M['crust'] = c('crust', (0.62, 0.36, 0.13), rough=0.8); M['crumb'] = c('crumb', (0.97, 0.90, 0.72), rough=0.95)
    M['tcrust'] = c('tcrust', (0.42, 0.20, 0.06), rough=0.7); M['toast'] = c('toast', (0.88, 0.58, 0.22), rough=0.8); M['butter'] = c('butter', (1.0, 0.88, 0.35), rough=0.3, spec=0.8)
    M['steel'] = c('steel', (0.62, 0.65, 0.70), rough=0.25, metallic=0.85); M['steeld'] = c('steeld', (0.30, 0.32, 0.36), rough=0.4, metallic=0.7); M['black'] = c('black', (0.03, 0.03, 0.035), rough=0.5)
    M['glowd'] = c('glowd', (0.35, 0.12, 0.04), rough=0.3, emit=(0.8, 0.25, 0.05), emit_strength=0.4); M['glow'] = c('glow', (1.0, 0.45, 0.08), rough=0.3, emit=(1.0, 0.40, 0.05), emit_strength=6.0)
    M['white'] = c('white', (1, 1, 1), rough=0.4); M['red'] = c('red', (0.9, 0.08, 0.06), rough=0.4); M['yellow'] = c('yellow', (1.0, 0.8, 0.05), rough=0.5)
    M['rock'] = c('rock', (0.22, 0.16, 0.13), rough=1.0); M['rockd'] = c('rockd', (0.12, 0.09, 0.08), rough=1.0)
    M['lava'] = c('lava', (1.0, 0.35, 0.03), rough=0.8, emit=(1.0, 0.28, 0.02), emit_strength=5.0); M['lava2'] = c('lava2', (1.0, 0.75, 0.2), rough=0.8, emit=(1.0, 0.65, 0.12), emit_strength=8.0)
    M['smoke'] = c('smoke', (0.25, 0.23, 0.22), rough=1.0); M['steam'] = c('steam', (1, 1, 1), rough=1.0, emit=(1, 1, 1), emit_strength=0.45)
    M['concrete'] = c('concrete', (0.78, 0.77, 0.74), rough=0.9); M['stripe'] = c('stripe', (0.85, 0.15, 0.1), rough=0.6); M['pipe'] = c('pipe', (0.55, 0.62, 0.70), rough=0.35, metallic=0.6)
    M['belt'] = c('belt', (0.08, 0.08, 0.09), rough=0.8); M['roller'] = c('roller', (0.7, 0.72, 0.75), rough=0.3, metallic=0.7); M['frame'] = c('frame', (0.95, 0.6, 0.05), rough=0.5)
    M['kwall'] = c('kwall', (0.98, 0.93, 0.80), rough=0.8); M['kfloor'] = c('kfloor', (0.55, 0.62, 0.68), rough=0.6); M['counter'] = c('counter', (0.92, 0.92, 0.9), rough=0.4); M['cab'] = c('cab', (0.35, 0.65, 0.75), rough=0.5)
    M['tile'] = c('tile', (0.85, 0.92, 0.95), rough=0.3); M['dash'] = c('dash', (0.1, 0.1, 0.12), rough=0.6)
    return M

def lathe(name, profile, mat, coll, seg=32, loc=(0, 0, 0), cap=False):
    """solido di rivoluzione attorno a Z: profile = [(r, z), ...] dal basso in alto."""
    bm = bmesh.new(); rings = []
    for (r, z) in profile: rings.append([bm.verts.new((r * math.cos(2 * PI * k / seg), r * math.sin(2 * PI * k / seg), z)) for k in range(seg)])
    for i in range(len(rings) - 1):
        for k in range(seg): bm.faces.new((rings[i][k], rings[i][(k + 1) % seg], rings[i + 1][(k + 1) % seg], rings[i + 1][k]))
    if cap: bm.faces.new(list(reversed(rings[0])))
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    o = bpy.data.objects.new(name, me); coll.objects.link(o); o.location = loc; me.materials.append(mat)
    return o

def bread(coll, M, name='Fetta', toast=False):
    """fetta di pane in piedi: larga 1, alta ~1, spessa 0.13, faccia verso -Y. Origine alla base."""
    g = empty(name, (0, 0, 0), None, coll); cr = M['tcrust'] if toast else M['crust']; cm = M['toast'] if toast else M['crumb']
    obj(name + 'Crosta', set004.box_c(), (0, 0, 0.36), (1.0, 0.13, 0.72), cr, coll, parent=g)
    for sx in (-0.26, 0.26): cyl(name + 'Lobo', 0.27, 0.13, (sx, 0, 0.72), cr, coll, rot=(PI / 2, 0, 0), parent=g)
    for sy in (-1, 1):
        obj(name + 'Mollica', set004.box_c(), (0, sy * 0.068, 0.37), (0.88, 0.01, 0.66), cm, coll, parent=g)
        for sx in (-0.25, 0.25): cyl(name + 'MollicaLobo', 0.215, 0.01, (sx, sy * 0.068, 0.72), cm, coll, rot=(PI / 2, 0, 0), parent=g)
    if toast:
        for k in range(3): obj(name + 'Griglia', set004.box_c(), (0, -0.075, 0.2 + 0.25 * k), (0.84, 0.006, 0.05), M['tcrust'], coll, parent=g)
        obj(name + 'Burro', set004.box_c(), (0.05, -0.085, 0.55), (0.28, 0.03, 0.2), M['butter'], coll, rot=(0, 0.15, 0), parent=g)
    return g

def oven(coll, M, W=5.0, D=4.0, H=4.2):
    """forno industriale: fronte -Y, origine a terra al centro. Restituisce dict(root, door, dim, bright, needle, chimney)."""
    O = {}; r = O['root'] = empty('Forno', (0, 0, 0), None, coll)
    mb = MB([M['steel'], M['steeld'], M['black'], M['stripe'], M['yellow']])
    mb.b2((-W / 2, -D / 2, 0), (W / 2, D / 2, H), 0); mb.b2((-W / 2 - 0.05, -D / 2 - 0.05, 0), (W / 2 + 0.05, D / 2 + 0.05, 0.35), 1)
    mb.b2((-W / 2, -D / 2 - 0.02, H - 0.45), (W / 2, -D / 2 + 0.1, H - 0.3), 3)
    for sx in (-1, 1): mb.b2((sx * W / 2 - 0.25, -D / 2 - 0.3, 0), (sx * W / 2 + 0.25, -D / 2 + 0.3, 0.2), 2)
    mb.b2((W / 2 - 0.2, -0.4, H), (W / 2 - 1.0, 0.4, H + 1.6), 1)                                 # camino
    o = mb.build('FornoCorpo', coll); o.parent = r
    d = O['door'] = empty('FornoPorta', (-W * 0.38, -D / 2 - 0.02, 0.45), r, coll)             # cerniera a sinistra
    obj('PortaAnta', set004.box_c(), (W * 0.38, -0.06, 1.45), (W * 0.76, 0.12, 2.9), M['steeld'], coll, parent=d)
    O['dim'] = obj('PortaVetroSpento', set004.box_c(), (W * 0.38, -0.125, 1.55), (W * 0.55, 0.02, 1.6), M['glowd'], coll, parent=d)
    O['bright'] = obj('PortaVetroAcceso', set004.box_c(), (W * 0.38, -0.13, 1.55), (W * 0.55, 0.02, 1.6), M['glow'], coll, parent=d)
    obj('PortaManiglia', set004.box_c(), (W * 0.38, -0.16, 2.55), (W * 0.5, 0.08, 0.1), M['black'], coll, parent=d)
    ty = empty('Termometro', (W * 0.36, -D / 2 - 0.05, H - 1.1), r, coll)
    cyl('TermDisco', 0.42, 0.06, (0, 0, 0), M['white'], coll, rot=(PI / 2, 0, 0), parent=ty); cyl('TermBordo', 0.46, 0.04, (0, 0.02, 0), M['black'], coll, rot=(PI / 2, 0, 0), parent=ty)
    for k in range(5):
        a = PI * (0.85 - 0.425 * k); obj('TermTacca', set004.box_c(), (0.33 * math.cos(a), -0.04, 0.33 * math.sin(a)), (0.03, 0.01, 0.1), M['red'] if k == 4 else M['black'], coll, rot=(0, PI / 2 - a, 0), parent=ty)
    n = O['needle'] = empty('TermAgo', (0, -0.05, 0), ty, coll); obj('Ago', set004.box_c(), (0, 0, 0.15), (0.03, 0.01, 0.3), M['red'], coll, parent=n)
    O['chimney'] = (W / 2 - 0.6, 0, H + 1.6)
    return O

def volcano(coll, M, R=6.0, H=9.0):
    """vulcano: lathe con cratere e colate. Origine a terra al centro. Restituisce dict(root, crater)."""
    V = {}; r = V['root'] = empty('Vulcano', (0, 0, 0), None, coll)
    prof = [(R, 0), (R * 0.82, H * 0.18), (R * 0.58, H * 0.48), (R * 0.36, H * 0.82), (R * 0.26, H), (R * 0.22, H * 0.96), (R * 0.16, H * 0.86)]
    o = lathe('VulcanoCorpo', prof, M['rock'], coll, seg=40); o.parent = r
    V['crater'] = cyl('Cratere', R * 0.18, 0.08, (0, 0, H * 0.88), M['lava2'], coll, parent=r)
    rg = np.random.default_rng(3)
    for k in range(6):                                                                  # colate di lava lungo i fianchi
        a = 2 * PI * k / 6 + rg.uniform(-0.3, 0.3); L_ = rg.uniform(0.55, 0.9)
        for j in range(6):
            u = j / 6 * L_; rr = R * (0.24 + 0.72 * u); z = H * (0.96 - 0.95 * u) * (1 - 0.04 * j) ; w = 0.55 - 0.05 * j
            obj('Colata', set004.box_c(), (rr * math.cos(a), rr * math.sin(a), max(0.1, z - 0.15)), (w, 1.4, 0.3), M['lava'], coll, rot=(0, 0.65, a), parent=r)
    for k in range(10):
        a = rg.uniform(0, 2 * PI); rr = R * rg.uniform(0.5, 0.95); ball_('Masso', rg.uniform(0.3, 0.7), (rr * math.cos(a), rr * math.sin(a), H * (1 - rr / R) * 0.9), M['rockd'], coll, parent=r)
    return V

def cooling_tower(coll, M, R=4.5, H=15.0, name='Torre'):
    prof = [(R, 0), (R * 0.9, H * 0.25), (R * 0.74, H * 0.55), (R * 0.68, H * 0.72), (R * 0.72, H * 0.88), (R * 0.8, H)]
    o = lathe(name, prof, M['concrete'], coll, seg=36)
    inner = lathe(name + 'Dentro', [(r_ * 0.96, z) for (r_, z) in prof], M['concrete'], coll, seg=36); inner.parent = o
    for z in (H * 0.92,): obj(name + 'Fascia', set004.box_c(), (0, 0, z), (0.1, 0.1, 0.1), M['stripe'], coll, parent=o).hide_render = True
    ring = lathe(name + 'Anello', [(R * 0.79, H * 0.86), (R * 0.81, H * 0.86), (R * 0.81, H * 0.93), (R * 0.79, H * 0.93)], M['stripe'], coll, seg=36); ring.parent = o
    return o

def pipe(coll, M, p0, p1, r=0.45, name='Tubo'):
    p0, p1 = np.array(p0, float), np.array(p1, float); d = p1 - p0; L = float(np.linalg.norm(d)); c = (p0 + p1) / 2
    yaw = math.atan2(d[1], d[0]); pitch = math.atan2(math.hypot(d[0], d[1]), d[2])
    o = cyl(name, r, L, tuple(c), M['pipe'], coll, rot=(0, pitch, yaw))
    for k in range(int(L / 4)):
        u = (k + 0.5) / int(L / 4); q = p0 + d * u; cyl(name + 'Flangia', r * 1.18, 0.18, tuple(q), M['steeld'], coll, rot=(0, pitch, yaw))
    return o

def conveyor(coll, M, x, y0, y1, z=0.9, w=1.0):
    """nastro trasportatore lungo Y da y0 a y1 (y1 < y0), piano a quota z. Una mesh sola."""
    mb = MB([M['belt'], M['frame'], M['roller']]); L = y0 - y1
    mb.b2((x - w / 2, y1, z - 0.06), (x + w / 2, y0, z), 0)
    for sx in (-1, 1): mb.b2((x + sx * (w / 2 + 0.02), y1, z - 0.22), (x + sx * (w / 2 + 0.1), y0, z + 0.08), 1)
    y = y0 - 1.0
    while y > y1:
        for sx in (-1, 1): mb.box((x + sx * (w / 2 + 0.06), y, (z - 0.2) / 2), (0.08, 0.08, z - 0.2), 1)
        y -= 3.0
    return mb.build('Nastro', coll)

def intake(coll, M, x, y, z=0.9):
    """la 'macchina' all'ingresso del forno: tramoggia con due rulli giganti e un varco in mezzo. Restituisce (root, [rulli])."""
    r = empty('Macchina', (x, y, 0), None, coll); mb = MB([M['frame'], M['steeld'], M['yellow'], M['black']])
    for sx in (-1, 1): mb.b2((sx * 1.0, -0.9, 0), (sx * 1.25, 0.9, 2.4), 0)
    mb.b2((-1.25, 0.9, 0), (1.25, 1.1, 2.4), 1)
    for k in range(6): mb.b2((-1.25 + 0.42 * k, -0.92, 2.15), (-1.04 + 0.42 * k, -0.9, 2.4), 2 + (k % 2))
    o = mb.build('MacchinaCorpo', coll); o.parent = r
    rollers = []
    for sy in (-0.45, 0.45):
        rl = empty('Rullo', (0, sy, 1.3), r, coll); cyl('RulloCil', 0.42, 2.0, (0, 0, 0), M['roller'], coll, rot=(0, PI / 2, 0), parent=rl)
        for k in range(6): obj('RulloDente', set004.box_c(), (0, 0.42 * math.cos(k * PI / 3), 0.42 * math.sin(k * PI / 3)), (1.9, 0.08, 0.08), M['steeld'], coll, rot=(k * PI / 3, 0, 0), parent=rl)
        rollers.append(rl)
    text_obj(coll, 'MacchinaScritta', 'TOAST-O-MATIC', 0.2, M['black'], (0, -0.93, 1.95), parent=r)
    return r, rollers

def kitchen(coll, M, x0):
    """cucina: parete a y=+2, bancone lungo la parete con lo spazio vuoto del tostapane al centro."""
    mb = MB([M['kwall'], M['kfloor'], M['counter'], M['cab'], M['tile'], M['steel'], M['dash']])
    mb.b2((x0 - 5, -5, -0.1), (x0 + 5, 2.3, 0.0), 1); mb.b2((x0 - 5, 2.3, 0), (x0 + 5, 2.4, 3.2), 0); mb.b2((x0 - 5.1, -5, 0), (x0 - 5, 2.4, 3.2), 0)
    mb.b2((x0 - 4, 1.6, 0), (x0 + 4, 2.3, 0.88), 3); mb.b2((x0 - 4.05, 1.55, 0.88), (x0 + 4.05, 2.3, 0.95), 2)
    mb.b2((x0 - 4, 2.28, 0.95), (x0 + 4, 2.3, 1.7), 4)
    for k in range(7): mb.b2((x0 - 3.7 + 1.15 * k, 1.58, 0.15), (x0 - 2.75 + 1.15 * k, 1.6, 0.8), 2)
    mb.b2((x0 + 2.6, 1.7, 0.94), (x0 + 3.6, 2.2, 0.96), 5)                                    # lavello
    mb.b2((x0 - 4.9, 1.0, 0), (x0 - 4.0, 2.3, 2.1), 2)                                       # frigo
    mb.b2((x0 - 4.0, 1.4, 0.0), (x0 - 3.99, 2.2, 2.1), 6)
    for k in range(12):                                                                      # sagoma tratteggiata del tostapane mancante
        u = k / 12; a = 2 * PI * u; px = 0.38 * math.cos(a); py = 0.22 * math.sin(a)
        mb.box((x0 + px, 1.95 + py, 0.955), (0.07, 0.03, 0.005), 6, rz=a + PI / 2)
    mb.build('Cucina', coll)
    sign = empty('CartelloTostapane', (x0, 2.27, 1.35), None, coll)
    obj('CartTav', set004.box_c(), (0, 0, 0), (1.3, 0.03, 0.42), M['white'], coll, parent=sign)
    text_obj(coll, 'CartTxt', 'TOSTAPANE ?', 0.17, M['red'], (0, -0.02, -0.06), parent=sign)
    obj('Presa', set004.box_c(), (x0 + 0.6, 2.27, 1.1), (0.14, 0.02, 0.2), M['white'], coll)
    return sign
