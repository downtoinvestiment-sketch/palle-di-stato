"""Test 015 - IL PARTO DI ELEONORA: neonati, culle, corridoio, mucca con le ali da fata, nuvola di puzza, maschere antigas."""
import math, bpy, numpy as np
from common import material, shape, empty, shared_mesh
import set004
from set004 import MB, obj, cyl, ball_
from props007 import text_obj
PI = math.pi

def mats015():
    c = lambda n, col, **k: material('P15_' + n, col, **k); M = {}
    M['cow'] = c('cow', (0.97, 0.97, 0.95), rough=0.7); M['spot'] = c('spot', (0.06, 0.06, 0.07), rough=0.7); M['pink'] = c('pink', (1.0, 0.62, 0.70), rough=0.5)
    M['horn'] = c('horn', (0.95, 0.88, 0.70), rough=0.5); M['hoof'] = c('hoof', (0.15, 0.12, 0.1), rough=0.6); M['bell'] = c('bell', (1.0, 0.78, 0.2), rough=0.3, metallic=0.9)
    M['wing'] = c('wing', (1.0, 0.75, 0.95), rough=0.2, emit=(1.0, 0.7, 0.95), emit_strength=1.2); M['wingv'] = c('wingv', (0.8, 0.5, 1.0), rough=0.2, emit=(0.8, 0.5, 1.0), emit_strength=1.6)
    M['stink'] = c('stink', (0.30, 0.70, 0.05), rough=1.0, emit=(0.25, 0.6, 0.03), emit_strength=0.25); M['stinkd'] = c('stinkd', (0.18, 0.50, 0.04), rough=1.0, emit=(0.15, 0.45, 0.03), emit_strength=0.2)
    M['babyskin'] = c('babyskin', (1.0, 0.78, 0.66), rough=0.6); M['diaper'] = c('diaper', (1.0, 1.0, 1.0), rough=0.8); M['black'] = c('black', (0.02, 0.02, 0.03), rough=0.4)
    M['white'] = c('white', (1, 1, 1), rough=0.4); M['crib'] = c('crib', (0.75, 0.90, 1.0), rough=0.5); M['blanket'] = c('blanket', (1.0, 0.85, 0.9), rough=0.9)
    M['cwall'] = c('cwall', (0.50, 0.78, 0.70), rough=0.8); M['cfloor'] = c('cfloor', (0.80, 0.80, 0.78), rough=0.5); M['chair'] = c('chair', (0.2, 0.45, 0.8), rough=0.5); M['metal'] = c('metal', (0.6, 0.62, 0.66), rough=0.3, metallic=0.8)
    M['door'] = c('door', (0.55, 0.75, 0.85), rough=0.5); M['sign'] = c('sign', (1, 1, 1), rough=0.5, emit=(1, 1, 1), emit_strength=0.4); M['red'] = c('red', (0.9, 0.05, 0.05), rough=0.4, emit=(1, 0.05, 0.05), emit_strength=1.5)
    M['bread'] = c('bread', (0.92, 0.75, 0.45), rough=0.8); M['ham'] = c('ham', (0.95, 0.55, 0.6), rough=0.6); M['lettuce'] = c('lettuce', (0.4, 0.8, 0.2), rough=0.6)
    M['mask'] = c('mask', (0.12, 0.13, 0.12), rough=0.6); M['glass'] = c('glass', (0.6, 0.8, 0.9), rough=0.05, spec=1.0); M['paper'] = c('paper', (0.97, 0.96, 0.9), rough=0.8)
    M['scrubs'] = c('scrubs', (0.3, 0.7, 0.6), rough=0.8); M['window'] = c('window', (0.7, 0.9, 1.0), rough=0.1, emit=(0.7, 0.9, 1.0), emit_strength=1.4)
    M['hext'] = c('hext', (0.93, 0.95, 0.96), rough=0.7); M['hroof'] = c('hroof', (0.35, 0.40, 0.45), rough=0.6)
    return M

def baby(coll, M, name='Neonato'):
    """neonato da cartone seduto: origine sotto il pannolino. Fronte -Y."""
    r = empty(name, (0, 0, 0), None, coll)
    ball_(name + 'Pannolino', 1.0, (0, 0, 0.09), M['diaper'], coll, parent=r, sc=(0.13, 0.11, 0.09)); ball_(name + 'Corpo', 1.0, (0, 0, 0.2), M['babyskin'], coll, parent=r, sc=(0.1, 0.09, 0.11))
    h = empty(name + 'Testa', (0, 0, 0.36), r, coll); ball_(name + 'Cranio', 0.14, (0, 0, 0), M['babyskin'], coll, parent=h)
    for sx in (-1, 1):
        ball_(name + 'Occhio', 1.0, (sx * 0.05, -0.125, 0.02), M['black'], coll, parent=h, sc=(0.022, 0.012, 0.026)); ball_(name + 'Orecchio', 0.035, (sx * 0.14, 0, 0), M['babyskin'], coll, parent=h)
        ball_(name + 'Braccino', 1.0, (sx * 0.11, -0.03, 0.22), M['babyskin'], coll, parent=r, sc=(0.035, 0.035, 0.07)); ball_(name + 'Gambetta', 1.0, (sx * 0.06, -0.09, 0.04), M['babyskin'], coll, parent=r, sc=(0.04, 0.07, 0.035))
    ball_(name + 'Ciuffo', 0.03, (0, -0.02, 0.15), M['spot'], coll, parent=h, sc=(1, 1, 1.8)); ball_(name + 'Bocca', 1.0, (0, -0.135, -0.05), M['pink'], coll, parent=h, sc=(0.025, 0.01, 0.012))
    return r, h

def crib(coll, M, name='Culla'):
    """culla: piano a z=0.72. Origine a terra."""
    mb = MB([M['crib'], M['blanket'], M['metal']])
    mb.b2((-0.38, -0.26, 0.6), (0.38, 0.26, 0.72), 1)
    for sx in (-0.38, 0.38):
        for sy in (-0.26, 0.26): mb.box((sx, sy, 0.45), (0.04, 0.04, 0.9), 2)
    for k in range(9): mb.box((-0.36 + 0.09 * k, 0.26, 0.82), (0.025, 0.025, 0.25), 0)
    for sx in (-1, 1): mb.box((sx * 0.38, 0, 0.82), (0.025, 0.5, 0.25), 0)
    mb.b2((-0.4, 0.24, 0.93), (0.4, 0.28, 0.96), 0); mb.b2((-0.38, -0.28, 0.58), (0.38, 0.28, 0.6), 0)
    return mb.build(name, coll)

def corridor(coll, M, x0):
    """corridoio d'ospedale: parete a y=+1.6 con porta 'SALA PARTO' e sedie."""
    mb = MB([M['cwall'], M['cfloor'], M['chair'], M['metal'], M['door']])
    mb.b2((x0 - 6, -4, -0.1), (x0 + 6, 1.6, 0.0), 1); mb.b2((x0 - 6, 1.6, 0), (x0 + 6, 1.7, 3.0), 0); mb.b2((x0 - 6.1, -4, 0), (x0 - 6.0, 1.7, 3.0), 0)
    mb.b2((x0 + 1.4, 1.55, 0), (x0 + 3.0, 1.62, 2.3), 4)
    for k in range(4):
        x = x0 - 2.6 + 0.75 * k; mb.b2((x - 0.3, 1.0, 0.45), (x + 0.3, 1.5, 0.52), 2); mb.b2((x - 0.3, 1.42, 0.52), (x + 0.3, 1.5, 1.05), 2)
        for sx in (-0.25, 0.25): mb.box((x + sx, 1.25, 0.22), (0.04, 0.04, 0.45), 3)
    mb.build('Corridoio', coll)
    sg = empty('CartelloSalaParto', (x0 + 2.2, 1.55, 2.55), None, coll); obj('CartSP', set004.box_c(), (0, 0, 0), (1.5, 0.04, 0.35), M['sign'], coll, parent=sg)
    text_obj(coll, 'CartSPTxt', 'SALA PARTO', 0.18, M['red'], (0, -0.03, -0.06), parent=sg)
    light = obj('LuceRossaSP', set004.box_c(), (x0 + 2.2, 1.55, 2.85), (0.3, 0.06, 0.12), M['red'], coll)
    return light

def sandwich(coll, M, parent, loc):
    g = empty('Panino', loc, parent, coll)
    for (dz, m, s) in ((-0.05, M['bread'], (0.13, 0.09, 0.04)), (0.0, M['lettuce'], (0.14, 0.1, 0.012)), (0.015, M['ham'], (0.14, 0.1, 0.02)), (0.06, M['bread'], (0.13, 0.09, 0.045))):
        ball_('PaninoStrato', 1.0, (0, 0, dz), m, coll, parent=g, sc=s)
    return g

def cow(coll, M):
    """mucca con le ali da fata: fronte -Y, origine sotto la pancia (zampe fino a z=-0.75). Restituisce dict(root, wings[], legs[], tail, rear)."""
    C = {}; r = C['root'] = empty('Mucca', (0, 0, 0), None, coll)
    ball_('MuccaCorpo', 1.0, (0, 0, 0.35), M['cow'], coll, parent=r, sc=(0.55, 0.9, 0.5))
    rg = np.random.default_rng(6)
    for k in range(7):
        a = rg.uniform(0, 2 * PI); z = rg.uniform(0.15, 0.6); ball_('MuccaMacchia', rg.uniform(0.15, 0.25), (0.52 * math.cos(a) * 0.98, rg.uniform(-0.6, 0.6), z), M['spot'], coll, parent=r, sc=(0.4, 1, 1))
    h = C['head'] = empty('MuccaTesta', (0, -0.95, 0.62), r, coll)
    ball_('MuccaCranio', 1.0, (0, 0, 0), M['cow'], coll, parent=h, sc=(0.3, 0.32, 0.28)); ball_('MuccaMuso', 1.0, (0, -0.28, -0.1), M['pink'], coll, parent=h, sc=(0.24, 0.12, 0.15))
    for sx in (-1, 1):
        ball_('MuccaNarice', 0.03, (sx * 0.08, -0.39, -0.08), M['black'], coll, parent=h); ball_('MuccaOcchio', 1.0, (sx * 0.14, -0.24, 0.1), M['white'], coll, parent=h, sc=(0.07, 0.04, 0.08))
        ball_('MuccaPupilla', 1.0, (sx * 0.14, -0.28, 0.09), M['black'], coll, parent=h, sc=(0.035, 0.02, 0.045)); shape('MuccaCorno', 'cone', (sx * 0.2, -0.02, 0.26), scale=(0.05, 0.05, 0.16), rot=(0, sx * 0.6, 0), parent=h, mat=M['horn'], coll=coll)
        ball_('MuccaOrecchio', 1.0, (sx * 0.3, 0.02, 0.12), M['cow'], coll, parent=h, sc=(0.13, 0.05, 0.06))
    ball_('MuccaCampanaccio', 0.08, (0, -0.82, 0.22), M['bell'], coll, parent=r)
    C['legs'] = []
    for (sx, sy) in ((-0.3, -0.55), (0.3, -0.55), (-0.3, 0.55), (0.3, 0.55)):
        lg = empty('MuccaZampa', (sx, sy, 0.15), r, coll); cyl('MuccaGamba', 0.09, 0.7, (0, 0, -0.35), M['cow'], coll, parent=lg); cyl('MuccaZoccolo', 0.1, 0.1, (0, 0, -0.72), M['hoof'], coll, parent=lg); C['legs'].append(lg)
    ball_('MuccaMammella', 1.0, (0, 0.35, -0.05), M['pink'], coll, parent=r, sc=(0.2, 0.18, 0.12))
    t = C['tail'] = empty('MuccaCoda', (0, 0.88, 0.55), r, coll); cyl('MuccaCodaCil', 0.03, 0.6, (0, 0.05, -0.3), M['cow'], coll, rot=(0.25, 0, 0), parent=t); ball_('MuccaCodaCiuffo', 0.08, (0, 0.13, -0.6), M['spot'], coll, parent=t)
    C['wings'] = []
    for sx in (-1, 1):
        w = empty('AlaFata', (sx * 0.4, -0.1, 0.8), r, coll)
        ball_('AlaFataSu', 1.0, (sx * 0.55, 0, 0.35), M['wing'], coll, parent=w, sc=(0.6, 0.03, 0.42)).rotation_euler = (0, sx * 0.5, 0)
        ball_('AlaFataGiu', 1.0, (sx * 0.4, 0.05, -0.1), M['wingv'], coll, parent=w, sc=(0.38, 0.03, 0.26)).rotation_euler = (0, -sx * 0.4, 0)
        C['wings'].append(w)
    C['rear'] = (0, 0.95, 0.4)
    return C

def stink_cloud(coll, M, name='Puzza', n=14, R=0.9, seed=1):
    """nuvola verde di puzza. Origine al centro."""
    rg = np.random.default_rng(seed); r = empty(name, (0, 0, 0), None, coll)
    ball_(name + 'C', R * 0.7, (0, 0, 0), M['stink'], coll, parent=r)
    for k in range(n):
        a = rg.uniform(0, 2 * PI); b = rg.uniform(-0.6, 0.8); d = R * rg.uniform(0.45, 0.8)
        ball_(name + 'B', R * rg.uniform(0.35, 0.55), (d * math.cos(a) * math.cos(b), d * math.sin(a) * math.cos(b), d * math.sin(b)), M['stink'] if k % 3 else M['stinkd'], coll, parent=r)
    return r

def gas_mask(coll, M, head):
    g = empty('MascheraAntigas', (0, -0.24, -0.02), head, coll)
    ball_('MascFaccia', 1.0, (0, 0, 0.02), M['mask'], coll, parent=g, sc=(0.24, 0.08, 0.22))
    for sx in (-1, 1): cyl('MascLente', 0.065, 0.03, (sx * 0.09, -0.07, 0.07), M['glass'], coll, rot=(PI / 2, 0, 0), parent=g)
    cyl('MascFiltro', 0.08, 0.14, (0, -0.12, -0.08), M['mask'], coll, rot=(PI / 2, 0, 0), parent=g); cyl('MascFiltroGriglia', 0.07, 0.02, (0, -0.2, -0.08), M['metal'], coll, rot=(PI / 2, 0, 0), parent=g)
    return g

def window(coll, M, loc, w=1.2, h=1.3, rotz=0.0):
    g = empty('Finestra', loc, None, coll); g.rotation_euler = (0, 0, rotz)
    obj('FinVetro', set004.box_c(), (0, 0, 0), (w, 0.03, h), M['window'], coll, parent=g)
    for (dx, dz, sx, sz) in ((0, h / 2, w + 0.1, 0.08), (0, -h / 2, w + 0.1, 0.08), (w / 2, 0, 0.08, h), (-w / 2, 0, 0.08, h), (0, 0, 0.05, h)): obj('FinTelaio', set004.box_c(), (dx, -0.02, dz), (sx, 0.05, sz), M['white'], coll, parent=g)
    return g

def hospital_ext(coll, M, x, y, W=16.0, D=7.5, H=10.5):
    """facciata dell'ospedale verso -Y (fronte a y). Restituisce dict(win_esc=posizione finestra della fuga)."""
    mb = MB([M['hext'], M['window'], M['white'], M['hroof'], M['door']])
    mb.b2((x - W / 2, y, 0), (x + W / 2, y + D, H), 0); mb.b2((x - W / 2 - 0.2, y - 0.2, H), (x + W / 2 + 0.2, y + D + 0.2, H + 0.4), 3)
    for fl, z in enumerate((3.9, 7.3)):
        for k in range(6):
            xx = x - W / 2 + 1.6 + k * (W - 3.2) / 5; mb.b2((xx - 0.65, y - 0.04, z), (xx + 0.65, y, z + 1.4), 1); mb.b2((xx - 0.75, y - 0.12, z - 0.12), (xx + 0.75, y, z), 2)
    for k in (-2, -1, 1, 2): xx = x + k * 2.6; mb.b2((xx - 0.65, y - 0.04, 1.0), (xx + 0.65, y, 2.4), 1)
    mb.b2((x - 1.3, y - 0.05, 0), (x + 1.3, y, 2.6), 4); mb.b2((x - 1.8, y - 1.6, 2.6), (x + 1.8, y, 2.85), 2)
    mb.build('OspedaleEsterno', coll)
    sg = empty('InsegnaOspedale', (x, y - 0.1, H - 1.0), None, coll); obj('InsTav', set004.box_c(), (0, 0, 0), (6.0, 0.1, 1.0), M['sign'], coll, parent=sg)
    text_obj(coll, 'InsTxt', 'OSPEDALE', 0.62, M['red'], (0.5, -0.07, -0.25), parent=sg)
    obj('InsCroce1', set004.box_c(), (-2.3, -0.07, 0), (0.75, 0.05, 0.22), M['red'], coll, parent=sg); obj('InsCroce2', set004.box_c(), (-2.3, -0.07, 0), (0.22, 0.05, 0.75), M['red'], coll, parent=sg)
    k = 4; xx = x - W / 2 + 1.6 + k * (W - 3.2) / 5
    return dict(win_esc=(xx, y - 0.05, 3.9 + 0.7))

def magnifier(coll, M, parent, loc):
    g = empty('Lente', loc, parent, coll)
    cyl('LenteVetro', 0.13, 0.02, (0, 0, -0.18), M['glass'], coll, rot=(PI / 2, 0, 0), parent=g); cyl('LenteBordo', 0.15, 0.03, (0, 0.01, -0.18), M['spot'], coll, rot=(PI / 2, 0, 0), parent=g)
    cyl('LenteManico', 0.025, 0.2, (0, 0, 0.0), M['spot'], coll, parent=g)
    return g

def torus_mesh(name, R, r, nu=40, nv=14):
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

def cuffs(coll, M, parent, loc, s=1.0):
    c = empty('ManetteAria', loc, parent, coll); tm = torus_mesh('ToroManetta', 0.15 * s, 0.028 * s)
    for sx in (-1, 1):
        o = bpy.data.objects.new('AnelloAria', tm); o.data.materials.append(M['metal']); o.location = (sx * 0.21 * s, 0, 0); o.rotation_euler = (PI / 2, 0, 0); o.parent = c; coll.objects.link(o)
        obj('ChiusuraAria', set004.box_c(), (sx * 0.21 * s, 0, 0.15 * s), (0.05 * s, 0.05 * s, 0.05 * s), M['metal'], coll, parent=c)
    obj('CatenaAria', set004.box_c(), (0, 0, 0.0), (0.14 * s, 0.03 * s, 0.03 * s), M['metal'], coll, parent=c)
    return c
