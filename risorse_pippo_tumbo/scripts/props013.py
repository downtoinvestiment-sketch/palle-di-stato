"""Test 013 - PIPPO E TUMBO IN AEREO: aereo, cabina di pilotaggio, cabina passeggeri, ospedale, città, accessori da vacanza."""
import math, bpy, numpy as np
from common import material, shape, empty, shared_mesh
import set004, props004
from set004 import MB, obj, cyl, ball_
from props007 import text_obj
PI = math.pi

def mats013():
    c = lambda n, col, **k: material('A13_' + n, col, **k); M = {}
    M['body'] = c('body', (0.95, 0.95, 0.97), rough=0.25, spec=0.8); M['stripe'] = c('stripe', (0.95, 0.35, 0.05), rough=0.3); M['blue'] = c('blue', (0.05, 0.25, 0.75), rough=0.3)
    M['win'] = c('win', (0.04, 0.07, 0.12), rough=0.05, spec=1.0); M['metal'] = c('metal', (0.6, 0.62, 0.66), rough=0.3, metallic=0.8); M['dark'] = c('dark', (0.05, 0.05, 0.06), rough=0.5)
    M['white'] = c('white', (1, 1, 1), rough=0.4); M['black'] = c('black', (0.02, 0.02, 0.03), rough=0.3)
    M['lens'] = c('lens', (0.02, 0.02, 0.03), rough=0.05, spec=1.0, metallic=0.3); M['frame'] = c('frame', (0.95, 0.15, 0.4), rough=0.3)
    M['lei'] = [c('lei%d' % i, col, rough=0.6) for i, col in enumerate([(1.0, 0.2, 0.5), (1.0, 0.85, 0.1), (0.2, 0.75, 1.0), (1.0, 0.45, 0.05), (0.7, 0.3, 1.0)])]
    M['case'] = c('case', (0.95, 0.25, 0.2), rough=0.4); M['sticker'] = c('sticker', (1.0, 0.9, 0.2), rough=0.6)
    M['cone'] = c('cone', (0.85, 0.6, 0.3), rough=0.7); M['pist'] = c('pist', (0.55, 0.80, 0.35), rough=0.6); M['straw'] = c('straw', (1.0, 0.55, 0.65), rough=0.6); M['choc'] = c('choc', (0.35, 0.18, 0.08), rough=0.6)
    M['cap'] = c('cap', (0.05, 0.08, 0.25), rough=0.5); M['gold'] = c('gold', (1.0, 0.78, 0.2), rough=0.3, metallic=0.9)
    M['panel'] = c('panel', (0.18, 0.19, 0.22), rough=0.6); M['wall'] = c('wall', (0.85, 0.86, 0.88), rough=0.7); M['floor'] = c('floor', (0.25, 0.27, 0.33), rough=0.9); M['carpet'] = c('carpet', (0.20, 0.25, 0.45), rough=1.0)
    M['seat'] = c('seat', (0.10, 0.20, 0.50), rough=0.7); M['headrest'] = c('headrest', (0.9, 0.9, 0.92), rough=0.7)
    M['btn'] = [c('btn%d' % i, col, rough=0.3, emit=col, emit_strength=3.0) for i, col in enumerate([(1, 0.1, 0.1), (0.1, 1, 0.2), (1, 0.8, 0.1), (0.1, 0.5, 1)])]
    M['screen'] = c('screen', (0.1, 0.3, 0.5), rough=0.2, emit=(0.15, 0.5, 0.9), emit_strength=1.6); M['kara'] = c('kara', (0.9, 0.1, 0.8), rough=0.2, emit=(1.0, 0.2, 0.9), emit_strength=2.5)
    M['disco'] = c('disco', (0.9, 0.9, 0.95), rough=0.05, metallic=1.0); M['winp'] = c('winp', (0.6, 0.85, 1.0), rough=0.2, emit=(0.6, 0.85, 1.0), emit_strength=1.2)
    M['cart'] = c('cart', (0.75, 0.78, 0.82), rough=0.3, metallic=0.7); M['can'] = [c('can%d' % i, col, rough=0.3, metallic=0.5) for i, col in enumerate([(0.9, 0.1, 0.1), (0.1, 0.5, 0.9), (0.95, 0.75, 0.1)])]
    M['book'] = c('book', (0.85, 0.15, 0.10), rough=0.6); M['paper'] = c('paper', (0.96, 0.95, 0.9), rough=0.8)
    M['hwall'] = c('hwall', (0.70, 0.88, 0.80), rough=0.8); M['hfloor'] = c('hfloor', (0.85, 0.85, 0.82), rough=0.6); M['sheet'] = c('sheet', (0.92, 0.95, 1.0), rough=0.8)
    M['monitor'] = c('monitor', (0.05, 0.3, 0.1), rough=0.2, emit=(0.1, 1.0, 0.3), emit_strength=2.0); M['cross'] = c('cross', (1.0, 0.05, 0.05), rough=0.3, emit=(1.0, 0.05, 0.05), emit_strength=2.0)
    M['tarmac'] = c('tarmac', (0.16, 0.16, 0.18), rough=0.85); M['line'] = c('line', (0.95, 0.85, 0.2), rough=0.6); M['rwline'] = c('rwline', (0.95, 0.95, 0.95), rough=0.6)
    M['green'] = c('green', (0.15, 0.80, 0.25), rough=0.7)
    return M

# ---------------------------------------------------------------- aereo
def airplane(coll, M, L=16.0, R=1.25):
    """aereo di linea da cartone: muso verso +X, origine a terra sotto il centro (carrello giu'). Restituisce dict(root, gear)."""
    A = {}; r = A['root'] = empty('Aereo', (0, 0, 0), None, coll); zc = 2.3
    body = empty('AereoCorpo', (0, 0, zc), r, coll); A['body'] = body
    shape('Fusoliera', 'cap:%.2f:%.2f' % (R, L - 2 * R), (0, 0, 0), rot=(0, PI / 2, 0), parent=body, mat=M['body'], coll=coll)
    ball_('Muso', 1.0, (L / 2 - R * 0.6, 0, -0.1), M['body'], coll, parent=body, sc=(R * 1.6, R * 0.98, R * 0.9))
    obj('Striscia', set004.box_c(), (0, 0, -0.25), (L * 0.88, 2 * R + 0.02, 0.22), M['stripe'], coll, parent=body)
    obj('StrisciaBlu', set004.box_c(), (0, 0, -0.52), (L * 0.85, 2 * R + 0.015, 0.12), M['blue'], coll, parent=body)
    for k in range(13):
        x = -L / 2 + 2.8 + k * 0.82
        for sy in (-1, 1): ball_('Finestrino', 1.0, (x, sy * R * 0.99, 0.35), M['win'], coll, parent=body, sc=(0.17, 0.05, 0.22))
    for sy in (-1, 1): obj('Parabrezza', set004.box_c(), (L / 2 - 0.75, sy * 0.55, 0.42), (0.75, 0.75, 0.32), M['win'], coll, rot=(0, -0.45, sy * 0.55), parent=body)
    obj('PortaAereo', set004.box_c(), (L / 2 - 2.4, -R * 0.99, 0.0), (0.7, 0.05, 1.5), M['metal'], coll, parent=body)
    mb = MB([M['body'], M['blue'], M['metal']])
    mb.box((0.4, 0, -0.55), (2.6, 13.0, 0.22), 0); mb.box((0.15, 0, -0.55), (2.0, 13.2, 0.18), 0)
    for sy in (-1, 1): mb.box((-0.6, sy * 6.5, -0.15), (0.9, 0.1, 0.8), 1)
    mb.box((-L / 2 + 1.2, 0, 1.8), (2.0, 0.22, 2.8), 1, rx=0.0); mb.box((-L / 2 + 1.0, 0, 0.6), (1.6, 5.2, 0.16), 0)
    w = mb.build('AereoAli', coll); w.parent = body
    for sy in (-1, 1):
        shape('Motore', 'cyl:0.55:1.9', (0.9, sy * 3.2, -1.2), rot=(0, PI / 2, 0), parent=body, mat=M['metal'], coll=coll)
        cyl('MotorePresa', 0.45, 0.05, (1.86, sy * 3.2, -1.2), M['dark'], coll, rot=(0, PI / 2, 0), parent=body)
        obj('MotorePilone', set004.box_c(), (0.8, sy * 3.2, -0.82), (1.2, 0.15, 0.5), M['body'], coll, parent=body)
    text_obj(coll, 'Scritta', 'PIPPO AIR', 0.55, M['blue'], (-0.5, -R - 0.02, 0.62), rot=(PI / 2, 0, 0), parent=body)
    text_obj(coll, 'ScrittaR', 'PIPPO AIR', 0.55, M['blue'], (-0.5, R + 0.02, 0.62), rot=(PI / 2, 0, PI), parent=body)
    g = A['gear'] = empty('Carrello', (0, 0, 0), r, coll)
    for (x, sy) in ((L / 2 - 2.2, 0), (0.2, -1.6), (0.2, 1.6)):
        obj('Gamba', set004.box_c(), (x, sy, 0.85), (0.12, 0.12, 1.3), M['metal'], coll, parent=g); cyl('Ruota', 0.36, 0.28, (x, sy, 0.36), M['dark'], coll, rot=(PI / 2, 0, 0), parent=g)
    return A

# ---------------------------------------------------------------- accessori
def sunglasses(coll, M, head, y=-0.36, z=0.32, dx=0.13, w=0.27, h=0.22):
    g = empty('Occhiali', (0, y, z), head, coll)
    for sx in (-1, 1): ball_('Lente', 1.0, (sx * dx, 0, 0), M['lens'], coll, parent=g, sc=(w / 2, 0.03, h / 2)); obj('Montatura', set004.box_c(), (sx * dx, 0.005, h * 0.42), (w * 1.05, 0.04, 0.05), M['frame'], coll, parent=g)
    obj('Ponte', set004.box_c(), (0, 0.0, h * 0.3), (dx * 0.6, 0.03, 0.03), M['frame'], coll, parent=g)
    return g

def lei(coll, M, parent, loc, r=0.3, tilt=0.35, n=22, s=0.07):
    g = empty('Collana', loc, parent, coll); g.rotation_euler = (tilt, 0, 0)
    for k in range(n):
        a = 2 * PI * k / n; ball_('Fiore', s, (r * math.cos(a), r * math.sin(a), 0), M['lei'][k % 5], coll, parent=g, sc=(1, 1, 0.7))
    return g

def suitcase(coll, M):
    r = empty('Valigia', (0, 0, 0), None, coll)
    obj('ValCorpo', set004.box_c(), (0, 0, 0.42), (0.55, 0.28, 0.7), M['case'], coll, parent=r); obj('ValManico', set004.box_c(), (0, 0, 0.95), (0.3, 0.04, 0.35), M['metal'], coll, parent=r)
    for k, (x, z) in enumerate(((-0.12, 0.55), (0.14, 0.3), (0.1, 0.62))): ball_('Adesivo', 1.0, (x, -0.145, z), M['sticker'] if k != 1 else M['lei'][2], coll, parent=r, sc=(0.08, 0.01, 0.08))
    for sx in (-0.2, 0.2): cyl('ValRuota', 0.05, 0.04, (sx, 0.1, 0.05), M['dark'], coll, rot=(0, PI / 2, 0), parent=r)
    return r

def gelato(coll, M, parent, loc):
    """gelato gigante: cono verso il basso, tre palline. Origine all'impugnatura."""
    g = empty('Gelato', loc, parent, coll)
    shape('Cono', 'cone', (0, 0, 0.55), scale=(0.2, 0.2, -0.75), parent=g, mat=M['cone'], coll=coll)
    for k, (m, dz) in enumerate(((M['pist'], 0.72), (M['straw'], 1.02), (M['choc'], 1.3))): ball_('Pallina', 0.26 - 0.02 * k, (0.02 * k, 0, dz), m, coll, parent=g)
    return g

def pilot_cap(coll, M, head):
    g = empty('CappelloPilota', (0, 0.02, 0.24), head, coll)
    cyl('CapCalotta', 0.30, 0.16, (0, 0, 0.02), M['cap'], coll, parent=g); obj('CapVisiera', set004.box_c(), (0, -0.28, -0.03), (0.42, 0.22, 0.03), M['black'], coll, parent=g)
    obj('CapFascia', set004.box_c(), (0, -0.29, 0.04), (0.3, 0.02, 0.05), M['gold'], coll, parent=g); ball_('CapStemma', 0.05, (0, -0.30, 0.1), M['gold'], coll, parent=g)
    return g

def mic(coll, M, parent, loc):
    g = empty('Microfono', loc, parent, coll)
    cyl('MicManico', 0.035, 0.26, (0, 0, -0.1), M['dark'], coll, parent=g); ball_('MicTesta', 0.07, (0, 0, -0.27), M['metal'], coll, parent=g)
    return g

def manual(coll, M):
    """manuale di volo, morsicato: due stadi (intero/mangiato)."""
    r = empty('Manuale', (0, 0, 0), None, coll)
    whole = empty('ManualeIntero', (0, 0, 0), r, coll); obj('MnCopertina', set004.box_c(), (0, 0, 0), (0.36, 0.05, 0.48), M['book'], coll, parent=whole)
    obj('MnPagine', set004.box_c(), (0.0, -0.002, 0), (0.33, 0.055, 0.45), M['paper'], coll, parent=whole)
    text_obj(coll, 'MnTitolo', 'COME\nSI VOLA', 0.06, M['white'], (0, -0.03, 0.06), parent=whole)
    eaten = empty('ManualeMangiato', (0, 0, 0), r, coll)
    obj('MnResto', set004.box_c(), (-0.06, 0, -0.1), (0.24, 0.05, 0.28), M['book'], coll, parent=eaten)
    obj('MnRestoPagine', set004.box_c(), (-0.06, -0.003, -0.1), (0.22, 0.052, 0.26), M['paper'], coll, parent=eaten)
    for k in range(7):
        a = PI * 0.15 + k * PI * 0.12; ball_('MnMorso', 0.035, (0.06 + 0.13 * math.cos(a) - 0.12, -0.01, 0.03 + 0.13 * math.sin(a) - 0.12), M['paper'], coll, parent=eaten, sc=(1, 0.6, 1))
    text_obj(coll, 'MnTitolo2', 'COME', 0.05, M['white'], (-0.1, -0.03, -0.05), parent=eaten)
    return r, whole, eaten

# ---------------------------------------------------------------- set interni
def cockpit_set(coll, M, x0):
    """cabina di pilotaggio aperta in alto: guarda verso +X. Sedili a (x0-0.3, ±0.65). Restituisce dict."""
    C = {}; mb = MB([M['wall'], M['floor'], M['panel'], M['seat'], M['dark'], M['headrest']])
    mb.b2((x0 - 3.2, -1.9, -0.1), (x0 + 1.8, 1.9, 0.0), 1)                                   # pavimento
    mb.b2((x0 - 3.2, -2.0, 0.0), (x0 + 1.8, -1.9, 2.9), 0); mb.b2((x0 - 3.2, 1.9, 0.0), (x0 + 1.8, 2.0, 2.9), 0)   # pareti
    mb.b2((x0 - 3.3, -1.9, 0.0), (x0 - 3.2, 1.9, 2.9), 0)                                    # parete di fondo
    mb.b2((x0 - 3.25, -0.5, 0.0), (x0 - 3.18, 0.5, 2.1), 4)                                  # porta
    mb.b2((x0 + 0.7, -1.9, 0.0), (x0 + 1.5, 1.9, 0.75), 2); mb.b2((x0 + 0.55, -1.9, 0.75), (x0 + 1.6, 1.9, 0.82), 2)   # cruscotto
    mb.b2((x0 + 1.5, -1.9, 0.82), (x0 + 1.8, 1.9, 0.9), 0)   # bordo del parabrezza
    for sy in (-0.65, 0.65):                                                                 # sedili
        mb.b2((x0 - 0.75, sy - 0.32, 0.0), (x0 - 0.05, sy + 0.32, 0.55), 3); mb.b2((x0 - 0.85, sy - 0.34, 0.55), (x0 - 0.65, sy + 0.34, 1.75), 3); mb.b2((x0 - 0.86, sy - 0.2, 1.55), (x0 - 0.8, sy + 0.2, 1.75), 5)
    mb.b2((x0 - 0.2, -0.18, 0.0), (x0 + 0.65, 0.18, 0.62), 2)                                # consolle centrale
    o = mb.build('Cockpit', coll)
    rg = np.random.default_rng(4)
    for k in range(34):                                                                      # pulsanti e lucine
        y = rg.uniform(-1.7, 1.7); z = rg.uniform(0.3, 0.7); m = M['btn'][int(rg.integers(0, 4))]
        obj('Pulsante', set004.box_c(), (x0 + 0.69, y, z), (0.02, 0.06, 0.05), m, coll)
    for k, (y, z) in enumerate(((-1.0, 0.85), (-0.35, 0.85), (0.35, 0.85), (1.0, 0.85))): obj('Schermo', set004.box_c(), (x0 + 0.685, y, 0.5), (0.02, 0.42, 0.3), M['screen'], coll)
    C['yokes'] = []
    for sy in (-0.65, 0.65):
        y_ = empty('Cloche', (x0 + 0.45, sy, 0.78), None, coll); obj('ClocheAsta', set004.box_c(), (0.0, 0, -0.15), (0.06, 0.06, 0.3), M['dark'], coll, parent=y_)
        obj('ClocheVolante', set004.box_c(), (0, 0, 0.02), (0.05, 0.42, 0.06), M['dark'], coll, parent=y_); C['yokes'].append(y_)
    lev = C['lever'] = empty('Leva', (x0 + 0.2, 0, 0.62), None, coll)
    obj('LevaAsta', set004.box_c(), (0, 0, 0.18), (0.04, 0.04, 0.36), M['metal'], coll, parent=lev); ball_('LevaPomo', 0.07, (0, 0, 0.38), M['btn'][0], coll, parent=lev)
    kb = C['kbtn'] = obj('TastoKaraoke', set004.box_c(), (x0 + 0.42, 0.08, 0.64), (0.16, 0.16, 0.06), M['kara'], coll)
    ks = C['kscreen'] = empty('SchermoKaraoke', (x0 - 3.1, 0, 1.55), None, coll)
    obj('KaraTv', set004.box_c(), (0, 0, 0.42), (0.06, 1.6, 0.9), M['dark'], coll, parent=ks); obj('KaraTvSchermo', set004.box_c(), (0.035, 0, 0.42), (0.02, 1.5, 0.8), M['kara'], coll, parent=ks)
    text_obj(coll, 'KaraTxt', 'KARAOKE', 0.26, M['white'], (0.05, 0, 0.5), rot=(PI / 2, 0, PI / 2), parent=ks)
    text_obj(coll, 'KaraTxt2', '(pilota automatico)', 0.09, M['white'], (0.05, 0, 0.24), rot=(PI / 2, 0, PI / 2), parent=ks)
    d = C['disco'] = empty('PallaDisco', (x0 - 0.5, 0, 2.6), None, coll)
    ball_('DiscoPalla', 0.32, (0, 0, 0), M['disco'], coll, parent=d); obj('DiscoFilo', set004.box_c(), (0, 0, 1.0), (0.02, 0.02, 2.0), M['dark'], coll, parent=d)
    for k in range(18):
        a = 2 * PI * k / 18; obj('DiscoTessera', set004.box_c(), (0.32 * math.cos(a), 0.32 * math.sin(a), 0.1 * ((k % 3) - 1)), (0.05, 0.08, 0.08), M['disco'], coll, rot=(0, 0, a), parent=d)
    return C

def cabin_set(coll, M, x0, rows=5):
    """cabina passeggeri lungo X, guardando verso +X (cockpit). Corridoio a y=0. Porta WC in fondo (x0-0.6). Restituisce (sedili [(x, y)], porta)."""
    mb = MB([M['wall'], M['carpet'], M['seat'], M['headrest'], M['winp'], M['dark']])
    L = rows * 1.05 + 2.2
    mb.b2((x0 - 1.0, -2.2, -0.1), (x0 + L, 2.2, 0.0), 1)
    for sy in (-1, 1):
        mb.b2((x0 - 1.0, sy * 2.2, 0.0), (x0 + L, sy * 2.3, 2.6), 0)
        for k in range(rows + 1): mb.b2((x0 + 0.9 + k * 1.05, sy * 2.19 - sy * 0.01, 1.15), (x0 + 1.25 + k * 1.05, sy * 2.2, 1.55), 4)
    mb.b2((x0 - 1.1, -2.2, 0.0), (x0 - 1.0, 2.2, 2.6), 0)
    seats = []
    for k in range(rows):
        x = x0 + 1.0 + k * 1.05
        for sy in (-1, 1):
            for j in range(2):
                y = sy * (0.75 + 0.6 * j); seats.append((x, y))
                mb.b2((x - 0.25, y - 0.27, 0.0), (x + 0.25, y + 0.27, 0.48), 2); mb.b2((x - 0.42, y - 0.29, 0.3), (x - 0.25, y + 0.29, 1.35), 2); mb.b2((x - 0.43, y - 0.2, 1.15), (x - 0.4, y + 0.2, 1.35), 3)
    mb.build('Cabina', coll)
    door = empty('PortaWC', (x0 - 0.95, 0.5, 0), None, coll)
    obj('PortaWCAnta', set004.box_c(), (0, -0.5, 1.05), (0.06, 1.0, 2.1), M['metal'], coll, parent=door)
    text_obj(coll, 'WC', 'WC', 0.3, M['dark'], (0.04, -0.5, 1.7), rot=(PI / 2, 0, PI / 2), parent=door)
    return seats, door

def drinks_cart(coll, M):
    r = empty('Carrello', (0, 0, 0), None, coll)
    obj('CarCorpo', set004.box_c(), (0, 0, 0.55), (0.75, 0.42, 0.95), M['cart'], coll, parent=r)
    rg = np.random.default_rng(2)
    for k in range(9): cyl('Lattina', 0.05, 0.14, (rg.uniform(-0.3, 0.3), rg.uniform(-0.15, 0.15), 1.1), M['can'][k % 3], coll, parent=r)
    for sx in (-0.3, 0.3):
        for sy in (-0.16, 0.16): cyl('CarRuota', 0.05, 0.04, (sx, sy, 0.05), M['dark'], coll, rot=(0, PI / 2, 0), parent=r)
    return r

def hospital_set(coll, M, x0):
    """stanza d'ospedale: letto con il cuscino verso -Y? No: letto lungo X, testata a -X. Restituisce posizione del cuscino."""
    mb = MB([M['hwall'], M['hfloor'], M['sheet'], M['metal'], M['dark']])
    mb.b2((x0 - 4, -4, -0.1), (x0 + 4, 3, 0.0), 1); mb.b2((x0 - 4, 3.0, 0.0), (x0 + 4, 3.1, 3.2), 0); mb.b2((x0 - 4.1, -4, 0.0), (x0 - 4.0, 3.1, 3.2), 0)
    mb.b2((x0 - 1.1, -0.55, 0.45), (x0 + 1.1, 0.55, 0.62), 2); mb.b2((x0 - 1.2, -0.6, 0.0), (x0 - 1.1, 0.6, 1.1), 3); mb.b2((x0 + 1.1, -0.6, 0.0), (x0 + 1.2, 0.6, 0.8), 3)
    for sx in (-1.0, 1.0):
        for sy in (-0.5, 0.5): mb.box((x0 + sx, sy, 0.22), (0.05, 0.05, 0.45), 3)
    mb.b2((x0 - 0.95, -0.4, 0.62), (x0 - 0.45, 0.4, 0.75), 2)                                 # cuscino
    mb.b2((x0 - 2.2, 1.8, 0.0), (x0 - 2.1, 1.9, 1.8), 3); mb.b2((x0 - 2.5, 1.6, 1.8), (x0 - 1.8, 1.7, 2.3), 4)   # monitor
    mb.build('Ospedale', coll)
    obj('MonitorSchermo', set004.box_c(), (x0 - 2.15, 1.59, 2.05), (0.62, 0.02, 0.42), M['monitor'], coll)
    obj('CroceH1', set004.box_c(), (x0, 2.98, 2.4), (0.6, 0.04, 0.18), M['cross'], coll); obj('CroceH2', set004.box_c(), (x0, 2.98, 2.4), (0.18, 0.04, 0.6), M['cross'], coll)
    return (x0 - 0.7, 0.0, 0.75)

def airport(coll, M, x0, y0):
    mb = MB([M['tarmac'], M['line'], M['rwline'], M['green']])
    mb.b2((x0 - 160, y0 - 70, -0.05), (x0 + 220, y0 + 80, 0.02), 3)
    mb.b2((x0 - 150, y0 + 2, 0.02), (x0 + 210, y0 + 16, 0.03), 0); mb.b2((x0 - 20, y0 - 14, 0.02), (x0 + 25, y0 + 2, 0.03), 0)
    for k in range(40): mb.b2((x0 - 140 + 9 * k, y0 + 8.85, 0.03), (x0 - 135 + 9 * k, y0 + 9.15, 0.035), 2)
    mb.b2((x0 - 20, y0 - 3.1, 0.03), (x0 + 25, y0 - 2.9, 0.035), 1)
    return mb.build('Aeroporto', coll)

def lowcity(coll, Mset, M, x0, y0, rng):
    """citta' di case basse (niente grattacieli), ospedale con croce rossa al centro. Restituisce la posizione dell'ospedale."""
    mb = MB([M['tarmac'], M['green']]); mb.b2((x0 - 280, y0 - 160, -0.05), (x0 + 240, y0 + 160, 0.0), 1)
    for k in range(-8, 9): mb.b2((x0 - 280, y0 + k * 16 - 2.0, 0.0), (x0 + 240, y0 + k * 16 + 2.0, 0.02), 0)
    for k in range(-14, 13): mb.b2((x0 + k * 18 - 2.0, y0 - 160, 0.0), (x0 + k * 18 + 2.0, y0 + 160, 0.02), 0)
    mb.build('CittaSuolo', coll)
    hx, hy = x0 + 20, y0 + 8
    for i in range(-14, 12):
        for j in range(-8, 8):
            x = x0 + i * 18 + 9; y = y0 + j * 16 + 8
            if abs(x - hx) < 20 and abs(y - hy) < 18: continue
            for (dx, dy) in ((-4, -3.5), (4, 3.5)):
                if rng.random() < 0.15: continue
                mbh = MB(set004.house_mats(Mset, int(rng.integers(0, 6)), int(rng.integers(0, 4)), int(rng.integers(0, 5))))
                two = bool(rng.integers(0, 2)); set004.house_geo(mbh, rng.uniform(4.6, 5.8), rng.uniform(4.0, 4.8), 4.5 if two else 2.9, two, rng)
                mbh.build('CasaCitta', coll, (x + dx, y + dy, 0), [0, PI / 2, PI, -PI / 2][int(rng.integers(0, 4))])
    hb = MB([M['wall'], M['win']])
    hb.b2((hx - 9, hy - 7, 0), (hx + 9, hy + 7, 9), 0)
    for k in range(3):
        for j in range(7): hb.b2((hx - 7.5 + j * 2.3, hy - 7.02, 1.5 + k * 2.4), (hx - 6.3 + j * 2.3, hy - 6.98, 2.8 + k * 2.4), 1)
    hb.build('OspedaleEdificio', coll)
    obj('OspCroce1', set004.box_c(), (hx, hy - 7.1, 11.0), (4.0, 0.3, 1.2), M['cross'], coll); obj('OspCroce2', set004.box_c(), (hx, hy - 7.1, 11.0), (1.2, 0.3, 4.0), M['cross'], coll)
    obj('OspTettoCroce1', set004.box_c(), (hx, hy, 9.06), (6.0, 1.6, 0.1), M['cross'], coll); obj('OspTettoCroce2', set004.box_c(), (hx, hy, 9.06), (1.6, 6.0, 0.1), M['cross'], coll)
    return (hx, hy)
