"""Test 006 - COME UN CARRELLO DELLA SPESA DIVENTA UNA MACCHINA DA CORSA. Salva ../t006/pippo_t006.blend
Personaggi: modelli ESISTENTI (pippo.py, tumbo.py) invariati."""
import sys, math, os
sys.path.insert(0, os.path.dirname(__file__))
import bpy, numpy as np
from mathutils import Vector, Euler, Matrix
from common import *
from render_setup import *
import set004, props004, props005, props006, pippo, tumbo
from set004 import obj, bx, cyl, ball_, MB
from props006 import BW, BL, Z0 as CZ0, Z1 as CZ1, FLOOR, S as CS

FPS = 24; TOTAL = 66.5; NF = int(TOTAL * FPS)
def fr(t): return max(1, int(round(t * FPS)) + 1)
def sm(x): x = min(1.0, max(0.0, x)); return x * x * (3 - 2 * x)
def ramp(t, a, b): return sm((t - a) / (b - a))
def lerp(a, b, u): return tuple(a[i] + (b[i] - a[i]) * u for i in range(len(a)))
def add(a, b): return tuple(a[i] + b[i] for i in range(3))
PI = math.pi

reset_scene(); scene = bpy.context.scene
setup_render(scene, 1080, 1920, samples=16, fps=FPS, frames=NF); scene.frame_end = NF
scene.eevee.shadow_resolution_scale = 0.25
rng = np.random.default_rng(21)
M = set004.make_mats(); Q = props005.mats005(); K = props006.mats006()
envc = collection('Env'); chc = collection('Characters'); prc = collection('Props'); cac = collection('Cameras')

# ======================= mondo =======================
w = bpy.data.worlds.new('World'); scene.world = w; w.use_nodes = True; nt = w.node_tree; nt.nodes.clear()
tc = nt.nodes.new('ShaderNodeTexCoord'); sp = nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(tc.outputs['Generated'], sp.inputs[0])
rp = nt.nodes.new('ShaderNodeValToRGB'); nt.links.new(sp.outputs['Z'], rp.inputs['Fac'])
rp.color_ramp.elements[0].position = 0.0; rp.color_ramp.elements[0].color = (0.46, 0.80, 1.0, 1)
rp.color_ramp.elements[1].position = 0.75; rp.color_ramp.elements[1].color = (0.04, 0.34, 1.0, 1)
bg = nt.nodes.new('ShaderNodeBackground'); bg.inputs['Strength'].default_value = 0.5; nt.links.new(rp.outputs['Color'], bg.inputs['Color'])
bgc = nt.nodes.new('ShaderNodeBackground'); bgc.inputs['Strength'].default_value = 1.0; nt.links.new(rp.outputs['Color'], bgc.inputs['Color'])
lpn = nt.nodes.new('ShaderNodeLightPath'); mxs = nt.nodes.new('ShaderNodeMixShader'); out = nt.nodes.new('ShaderNodeOutputWorld')
nt.links.new(lpn.outputs['Is Camera Ray'], mxs.inputs[0]); nt.links.new(bg.outputs['Background'], mxs.inputs[1]); nt.links.new(bgc.outputs['Background'], mxs.inputs[2])
nt.links.new(mxs.outputs[0], out.inputs['Surface'])
sun = bpy.data.lights.new('Sun', 'SUN'); so = bpy.data.objects.new('Sun', sun); prc.objects.link(so)
so.rotation_euler = (math.radians(52), math.radians(8), math.radians(35)); sun.angle = math.radians(1.2); sun.energy = 4.2; sun.color = (1, 0.95, 0.85)
M['cloudw'] = material('S_cloudw', (1, 1, 1), rough=1.0, emit=(1, 1, 1), emit_strength=0.55)
M['dust'] = material('S_dust', (0.93, 0.88, 0.78), rough=1.0, emit=(0.9, 0.85, 0.75), emit_strength=0.3)
_cr = np.random.default_rng(11)
for k in range(28):
    an = k / 28 * 2 * PI + _cr.uniform(-0.15, 0.15); rr = _cr.uniform(110, 170); s_ = _cr.uniform(4.5, 8.5)
    cw = empty('CloudW', (rr * math.cos(an), 25 + rr * math.sin(an), _cr.uniform(28, 75)), None, prc)
    for (dx, dy, dz, r_) in [(0, 0, 0, 1.5), (1.5, 0.3, -0.2, 1.15), (-1.5, -0.2, -0.25, 1.2), (0.6, -0.5, 0.6, 1.1), (-0.6, 0.5, 0.5, 1.0), (2.6, 0, -0.45, 0.75), (-2.7, 0, -0.5, 0.8)]:
        c_, s2 = math.cos(an + PI / 2), math.sin(an + PI / 2)
        ball_('Puff', r_ * s_, (dx * s_ * c_, dx * s_ * s2 + dy, dz * s_), M['cloudw'], prc, parent=cw, sc=(1, 1, 0.6))

# ======================= terreno: collina con la discesa, incrocio, via =======================
HTOP = 5.3
def HX(x):
    u = min(1.0, max(0.0, (x + 32.0) / 30.0)); s = u * u * u * (u * (6 * u - 15) + 10); return HTOP * (1 - s)
def HXY(x, y):
    f = 1 - sm((abs(y) - 6.5) / 11.0); g = 1 - sm((-47.0 - x) / 13.0); return HX(x) * f * g
def slope(x): return math.atan(-(HX(x + 0.3) - HX(x - 0.3)) / 0.6)       # >0 in discesa verso +X
bx('Ground', (-160, -140, -0.30), (160, 190, -0.02), M['park'], envc)
def gridmesh(name, xs, ys, zf, mat, coll, smooth=True):
    V = [(x, y, zf(x, y)) for x in xs for y in ys]; ny = len(ys)
    F = [(i * ny + j, (i + 1) * ny + j, (i + 1) * ny + j + 1, i * ny + j + 1) for i in range(len(xs) - 1) for j in range(ny - 1)]
    me = bpy.data.meshes.new(name); me.from_pydata(V, [], F); me.materials.append(mat)
    me.polygons.foreach_set('use_smooth', [smooth] * len(F)); me.update()
    o = bpy.data.objects.new(name, me); coll.objects.link(o); return o
gridmesh('Collina', np.linspace(-62, 0.5, 90), np.linspace(-19, 19, 50), lambda x, y: HXY(x, y) - 0.01, M['park'], envc)
gridmesh('StradaCollina', np.linspace(-45, 2.2, 80), np.linspace(-3.0, 3.0, 2), lambda x, y: HX(x) * (1 - sm((-47.0 - x) / 13.0)) + 0.035, M['asphalt'], envc)
for s in (-1, 1):
    gridmesh('Cordolo', np.linspace(-45, 0.6, 80), np.array([s * 3.0, s * 3.35]) if s > 0 else np.array([-3.35, -3.0]), lambda x, y: HX(x) + 0.09, M['sidewalk'], envc)
lm = MB([M['frame'], M['dark']])
for x in np.arange(-43, 0, 3.0):
    lm.box((x, 0, HX(x) + 0.05), (1.3, 0.14, 0.02), 0, rz=0.0)
for i in range(12):                                             # linea di partenza a scacchi
    for j in range(2): lm.box((-31.6 + j * 0.5, -2.75 + i * 0.5, HTOP + 0.045), (0.5, 0.5, 0.02), (i + j) % 2)
lm.build('Segnaletica', envc)
bx('Via', (2.0, -66.0, 0.0), (10.0, 22, 0.04), M['asphalt'], envc)
bx('MarciapiedeE', (10.0, -64, 0.0), (11.5, 22, 0.14), M['sidewalk'], envc)
bx('MarciapiedeO1', (0.6, 3.6, 0.0), (2.0, 22, 0.14), M['sidewalk'], envc); bx('MarciapiedeO2', (0.6, -64, 0.0), (2.0, -3.6, 0.14), M['sidewalk'], envc)
dm = MB([M['frame']])
for y in np.arange(-63, 21, 3.0): dm.box((6.0, y, 0.05), (0.14, 1.3, 0.02), 0)
dm.build('Tratteggio', envc)
# siepe e cassonetto in fondo alla discesa
bx('Siepe', (11.6, -9.0, 0.0), (13.4, 9.0, 2.2), M['hedge'], envc)
hm = MB([M['hedge'], M['flower'][0], M['flower'][1], M['flower'][2]])
for k in range(40):
    y = rng.uniform(-8.8, 8.8); z = rng.uniform(0.3, 2.1); hm.box((11.56, y, z), (0.14, 0.14, 0.14), 1 + k % 3)
for k in range(18): hm.box((12.5 + rng.uniform(-0.7, 0.7), rng.uniform(-8.5, 8.5), 2.25), (0.5, 0.6, 0.2), 0)
hm.build('SiepeFiori', envc)
BIN = (10.95, -1.2)
dump, dlid = props006.dumpster(envc, K); dump.location = (BIN[0], BIN[1], 0.14); dump.rotation_euler = (0, 0, -PI / 2)

# case, palazzi, alberi
def house_at(x, y, rotz, wi, ri, si, two, w=None, d=None):
    w = w or rng.uniform(4.6, 5.6); d = d or rng.uniform(4.0, 4.8)
    mb = MB(set004.house_mats(M, wi, ri, si)); set004.house_geo(mb, w, d, 4.5 if two else 2.9, two, rng); return mb.build('Casa', envc, (x, y, 0), rotz)
for k, y in enumerate(range(-58, 16, 9)): house_at(19.5, y, -PI / 2, int(rng.integers(0, 6)), int(rng.integers(0, 4)), int(rng.integers(0, 5)), bool(rng.integers(0, 2)))
for k, y in enumerate(range(-60, -21, 9)): house_at(-5.5, y, PI / 2, int(rng.integers(0, 6)), int(rng.integers(0, 4)), int(rng.integers(0, 5)), bool(rng.integers(0, 2)))
house_at(-40.5, 8.5, 0.0, 0, 0, 1, True, 5.0, 4.0).location.z = HTOP - 0.02                 # casa di Pippo, in cima
def tower_at(x, y, rz=0.0):
    tw = rng.uniform(3.6, 4.6); ti = int(rng.integers(0, len(M['tower']))); h = rng.uniform(11, 26)
    mb = MB([M['tower'][ti], M['window'], M['frame'], M['concrete'], M['dark'], M['shutter'][int(rng.integers(0, 5))]])
    set004.tower_geo(mb, tw, h, rng); mb.build('Palazzo', envc, (x, y, 0), rz)
for y in range(-90, 26, 11): tower_at(33 + rng.uniform(0, 3), y, -PI / 2)
for y in range(-95, -26, 11): tower_at(-19 - rng.uniform(0, 3), y, PI / 2)
for x in range(-14, 46, 11): tower_at(x, -93 - rng.uniform(0, 3), PI)
for x in range(-66, 46, 12): tower_at(x, 38 + rng.uniform(0, 4), 0.0)
for y in range(-26, 30, 12): tower_at(-76 - rng.uniform(0, 3), y, PI / 2)
def tree(x, y, s=1.0):
    z = HXY(x, y) if x < 0.5 and abs(y) < 19 else 0.0
    cyl('Tronco', 0.16 * s, 1.5 * s, (x, y, z + 0.75 * s), M['bark'], envc)
    for (dx, dy, dz, r) in ((0, 0, 2.1, 0.95), (0.5, 0.1, 1.75, 0.7), (-0.5, -0.1, 1.8, 0.72)):
        ball_('Chioma', r * s, (x + dx * s, y + dy * s, z + dz * s), M['leaf'][int(rng.integers(0, 3))], envc)
for x in np.arange(-44, -3, 5.5):
    tree(x + rng.uniform(-1, 1), 7.5 + rng.uniform(0, 5), rng.uniform(0.9, 1.4))
    if x > -30: tree(x + rng.uniform(-1, 1), -11 - rng.uniform(0, 4), rng.uniform(0.9, 1.4))
for y in range(-34, -18, 5): tree(-1.5 + rng.uniform(-1, 1), y, 1.2)
for k in range(14): tree(rng.uniform(14.5, 16), 18 - k * 6.2 + rng.uniform(-1, 1), rng.uniform(0.9, 1.3))

# garage del vicino in fondo alla via
GX, GY = 6.0, -66.0
gm = MB([M['wall'][3], M['roof'][0], M['dark'], M['frame'], M['stone']])
def g2(p0, p1, mi): gm.b2((p0[0], -66.0 - p1[1], p0[2]), (p1[0], -66.0 - p0[1], p1[2]), mi)      # p = (x, profondita' dentro il garage, z)
g2((3.0, 0, 0), (3.8, 0.25, 3.0), 0); g2((8.2, 0, 0), (9.0, 0.25, 3.0), 0); g2((3.8, 0, 2.4), (8.2, 0.25, 3.0), 0)
g2((3.0, 0, 0), (3.2, 6.5, 3.0), 0); g2((8.8, 0, 0), (9.0, 6.5, 3.0), 0); g2((3.0, 6.3, 0), (9.0, 6.5, 3.0), 0)
g2((2.8, -0.3, 3.0), (9.2, 6.7, 3.22), 1); g2((3.2, 0.25, 0.0), (8.8, 6.3, 0.05), 2)
g2((3.72, -0.04, 0), (3.8, 0.02, 2.48), 3); g2((8.2, -0.04, 0), (8.28, 0.02, 2.48), 3); g2((3.72, -0.04, 2.4), (8.28, 0.02, 2.48), 3)
gm.build('GarageVicino', envc)
bx('Vialetto', (3.0, GY, 0.0), (9.0, -64.0, 0.045), M['asphalt'], envc)
house_at(12.4, -69.6, PI, 3, 0, 0, True, 5.8, 5.0)
panels = []
for c in range(4):
    for r in range(4):
        pn = obj('Pannello', set004.box_c(), (3.8 + 0.55 + c * 1.1, GY - 0.06, 0.3 + r * 0.6), (1.07, 0.06, 0.57), K['belt'], prc); panels.append((c, r, pn))
gl = bpy.data.lights.new('LuceGarage', 'POINT'); gl.energy = 150; gl.color = (1.0, 0.85, 0.6); gl.shadow_soft_size = 0.6
glo = bpy.data.objects.new('LuceGarage', gl); glo.location = (GX, GY - 1.2, 2.5); envc.objects.link(glo)
fl = bpy.data.lights.new('LuceFacciata', 'AREA'); fl.energy = 700; fl.size = 6.0; fl.color = (1.0, 0.95, 0.85)
flo = bpy.data.objects.new('LuceFacciata', fl); flo.location = (6.0, -58.0, 5.0); envc.objects.link(flo)
flc = flo.constraints.new('TRACK_TO'); flt = empty('LuceFacciataT', (6.0, -66.0, 1.2), None, envc); flc.target = flt; flc.track_axis = 'TRACK_NEGATIVE_Z'; flc.up_axis = 'UP_Y'

# ======================= personaggi e oggetti =======================
P = pippo.build_pippo(chc); Tb = tumbo.build_tumbo(chc, scale=0.75)
for r in (P['root'], Tb['root']): r.rotation_mode = 'XYZ'
for nm in 'LR': P['shoulder' + nm].rotation_mode = 'QUATERNION'
def qdir(d, rest=(0, 0, -1)): return Vector(rest).rotation_difference(Vector(d).normalized())
C = props006.cart(prc, K); CR = C['root']; CR.rotation_mode = 'XYZ'
lev, pad = props006.brakes(prc, K, CR)
stg, stframe, stwheel, stws = props006.steering(prc, K, CR)
EN = props006.engine(prc, K, CR)
kit, belts = props006.racekit(prc, K, CR)
helmP = props006.helmet(prc, K, P['head'], 0.36, r=0.50)
helmT = props006.helmet(prc, K, Tb['head'], 0.05, r=0.37, mat='helm2', stripe='dark', front_cut=0.15)
mow, mowen = props006.mower(prc, K); MW = (-39.6, -3.4); mow.location = (MW[0], MW[1], HTOP); mow.rotation_euler = (0, 0, 0.5)
sem, semm = props006.traffic_light(prc, K); sem.location = (-30.2, 3.9, HTOP); sem.rotation_euler = (0, 0, 0.25)
G = props006.granny(chc, K)
peel = empty('Buccia', (0, 0, 0.62), P['head'], prc)
for k in range(3): obj('BucciaP', set004.box_c(), (0.13 * math.cos(k * 2.1), 0.13 * math.sin(k * 2.1), -0.04), (0.10, 0.30, 0.03), K['racey'], prc, rot=(0.5, 0, k * 2.1 + PI / 2), parent=peel)
crown = empty('Foglie', (0, 0, 0.55), P['head'], prc)
for k in range(6): ball_('FogliaT', 0.10, (0.26 * math.cos(k * 1.05), 0.22 * math.sin(k * 1.05), 0.05 * (k % 2)), M['leaf'][k % 3], prc, parent=crown, sc=(1, 1, 0.5))
brokenlev = obj('LevaRotta', set004.box_c(), (0, -0.06, -0.66), (0.05, 0.30, 0.05), K['steel'], prc, parent=P['shoulderR'])
obj('LevaRottaP', set004.box_c(), (0, 0.5, 0), (1.5, 0.25, 1.5), K['pad'], prc, parent=brokenlev)
man = props004.player(chc, 'Neigh', (0.96, 0.96, 0.96), (0.25, 0.25, 0.30), (0.96, 0.42, 0.36), (0.15, 0.10, 0.07), scale=1.0)
man['root'].scale = (0.9, 0.9, 0.9)
mhead = [c for c in man['root'].children if c.name.startswith('Head')][0]
for sx in (-1, 1): obj('Brow', set004.box_c(), (sx * 0.10, -0.25, 0.15), (0.13, 0.03, 0.035), M['dark'], chc, rot=(0, sx * 0.45, 0), parent=mhead)
ball = ball_('Pallone', 0.20, (0.34, -0.66, 1.72), M['ball'], prc, parent=man['root'])
lostw = props006._wheel(prc, K, None, (0, 0, -50), 0.25, 0.14)

def desc(o):
    for c in o.children:
        yield c
        yield from desc(c)
def show(o, intervals):
    for q in [o] + list(desc(o)):
        first = intervals[0][0] <= 0.0
        q.hide_render = not first; q.keyframe_insert('hide_render', frame=1)
        for (a, b) in intervals:
            if a > 0.0: q.hide_render = False; q.keyframe_insert('hide_render', frame=fr(a))
            if b < TOTAL: q.hide_render = True; q.keyframe_insert('hide_render', frame=fr(b))
def pop(o, t, d=0.32, s0=0.0001, over=1.25, s1=1.0):
    b = tuple(o.scale)
    for (tt_, v) in ((t, s0), (t + 0.55 * d, over), (t + d, s1)):
        o.scale = (b[0] * v, b[1] * v, b[2] * v); o.keyframe_insert('scale', frame=fr(tt_))
T_LEV, T_PAD, T_VOL, T_PIA, T_RUO, T_MOT, T_CAT, T_PIG, T_ACC, T_CAS, T_ROL, T_CIN, T_CAST = 22.8, 23.5, 30.6, 31.3, 32.0, 44.45, 45.3, 45.9, 46.5, 52.6, 53.3, 53.9, 55.3
show(lev, [(T_LEV, TOTAL)]); show(pad, [(T_PAD, TOTAL)]); show(stwheel, [(T_VOL, TOTAL)]); show(stframe, [(T_PIA, TOTAL)])
for w_ in stws: show(w_, [(T_RUO, TOTAL)])
show(EN['g'], [(T_MOT, TOTAL)]); show(EN['chain'], [(T_CAT, TOTAL)]); show(EN['spr'], [(T_PIG, TOTAL)]); show(EN['thr'], [(T_ACC, TOTAL)])
show(helmP, [(T_CAS, TOTAL)]); show(kit, [(T_ROL, TOTAL)]); show(belts, [(T_CIN, TOTAL)]); show(helmT, [(T_CAST, TOTAL)])
show(mowen, [(0, 44.4)]); show(peel, [(12.8, 19.9)]); show(crown, [(27.7, 29.2)]); show(brokenlev, [(63.0, TOTAL)])
show(man['root'], [(65.3, TOTAL)]); show(G['root'], [(35.6, 42.7), (60.0, 63.8)]); show(lostw, [(64.85, TOTAL)])
for c_ in C['casters'][:2]: show(c_, [(0, T_RUO)])            # le rotelline davanti spariscono quando arrivano le ruote sterzanti
for c_ in C['casters'][2:]: show(c_, [(0, T_MOT)])
for o_, t_ in ((lev, T_LEV), (pad, T_PAD), (stwheel, T_VOL), (stframe, T_PIA), (EN['g'], T_MOT), (EN['chain'], T_CAT), (EN['spr'], T_PIG), (EN['thr'], T_ACC),
               (helmP, T_CAS), (kit, T_ROL), (belts, T_CIN), (helmT, T_CAST)): pop(o_, t_)
for w_ in stws: pop(w_, T_RUO)

# ======================= movimento del carrello =======================
WS = (-37.0, -0.5); WYAW = 0.6
A1 = (9.6 + 32.0) * 2 / 2.45 ** 2
def curve(s, x0, y0=0.5):
    """rettilineo verso +X da (x0,y0), curva a destra di raggio 4, poi dritto verso -Y lungo x=6. Restituisce (x, y, yaw, frazione di curva)."""
    L1 = 2.0 - x0; R = 4.0; La = R * PI / 2
    if s < L1: return (x0 + s, y0, PI / 2, 0.0)
    if s < L1 + La:
        a = (s - L1) / R; return (2.0 + R * math.sin(a), y0 - R + R * math.cos(a), PI / 2 - a, (s - L1) / La)
    return (6.0, y0 - R - (s - L1 - La), 0.0, 1.0)
def cs(t):
    """stato del carrello: loc, rot (beccheggio, rollio, imbardata), sterzo."""
    S_ = dict(loc=(-46, 6, -30), rot=(0, 0, PI / 2), steer=0.0)
    def onhill(x, y, yaw=PI / 2, extra=0.0): S_.update(loc=(x, y, HX(x) + 0.04), rot=(slope(x) + extra, 0, yaw))
    if t < 4.7: pass
    elif t < 7.4: x = -41.0 + 5.8 * sm((t - 4.7) / 0.9); onhill(x, -0.8)
    elif t < 10.25:
        x = -33.2 + 1.2 * sm((t - 7.4) / 0.4) if t < 7.8 else -32.0 + 0.5 * A1 * (t - 7.8) ** 2
        onhill(x, -1.2 + 0.05 * math.sin(t * 30)); S_['rot'] = (S_['rot'][0], 0.03 * math.sin(t * 27), PI / 2)
    elif t < 19.9:
        tau = t - 10.25; S_.update(loc=(9.6 - 0.35 * (1 - math.exp(-tau * 6)), -1.2, 0.04), rot=(0.12 + 0.3 * math.exp(-tau * 5) * abs(math.cos(tau * 12)), 0, PI / 2))
    elif t < 24.1: S_.update(loc=(WS[0], WS[1], HTOP + 0.04), rot=(0, 0, WYAW + PI))
    elif t < 27.0:
        if t < 25.0: x = -27 + 13.3 * (t - 24.1)
        elif t < 26.4: x = -15 + 11.07 * (t - 25.0)
        else: x = 0.5 + 17.1 * (t - 26.4)
        sk = 0.45 * math.sin((t - 26.4) * 14) if t > 26.4 else 0.0
        onhill(x, 1.5, PI / 2 + sk); S_['rot'] = (S_['rot'][0] + (0.05 if t > 24.6 else 0), 0.03 * math.sin(t * 31), PI / 2 + sk)
    elif t < 29.2:
        tau = t - 27.0; S_.update(loc=(10.75, 1.5, 0.04), rot=(-0.10 - 0.25 * math.exp(-tau * 5) * abs(math.cos(tau * 11)), 0, PI / 2 + 0.2))
    elif t < 33.2: S_.update(loc=(WS[0], WS[1], HTOP + 0.04), rot=(0, 0, WYAW), steer=0.55 * math.sin((t - 32.3) * 9) if 32.3 < t < 33.1 else 0.0)
    elif t < 35.6:
        x, y, yaw, fa = curve(12.0 * (t - 33.2), -12.0); bank = math.sin(PI * fa) if 0 < fa < 1 else 0
        S_.update(loc=(x, y, HX(x) + 0.04), rot=(slope(x) if x < 2 else 0, -0.10 * bank, yaw), steer=-0.6 * bank)
    elif t < 42.7: S_.update(loc=(4.5, -16.0 - 0.9 * (t - 36.0), 0.04 + 0.01 * math.sin(t * 20)), rot=(0, 0, 0))
    elif t < 47.4: S_.update(loc=(WS[0], WS[1], HTOP + 0.04), rot=(0, 0, WYAW + PI))
    elif t < 51.4: S_.update(loc=(5.0 + 0.25 * math.sin(t * 3.0), -4.0 - 11.0 * (t - 47.4), 0.04 + 0.015 * abs(math.sin(t * 25))), rot=(-0.05, 0.02 * math.sin(t * 23), 0.06 * math.cos(t * 3.0)), steer=0.2 * math.cos(t * 3))
    elif t < 58.4: S_.update(loc=(WS[0], WS[1], HTOP + 0.04), rot=(0, 0, WYAW))
    elif t < 60.0:
        tau = max(0.0, t - 58.95); x = -32.0 + 8.0 * tau * tau; onhill(x, 0.5, PI / 2, -0.10 * ramp(t, 58.95, 59.1) * (1 - ramp(t, 59.3, 59.8)))
    elif t < 61.2:
        x, y, yaw, fa = curve(20.0 * (t - 60.0), -6.0); bank = math.sin(PI * fa) if 0 < fa < 1 else 0
        S_.update(loc=(x, y, HX(x) + 0.04), rot=(0, 0.10 * bank, yaw - 0.45 * bank), steer=0.5 * bank)
    elif t < 62.6: S_.update(loc=(5.0, -14.0 - 20.0 * (t - 61.2), 0.04 + 0.015 * abs(math.sin(t * 25))), rot=(-0.04, 0.02 * math.sin(t * 23), 0))
    elif t < 63.8: S_.update(loc=(5.0, -42.0 - 7.0 * (t - 62.6), 0.04 + 0.015 * abs(math.sin(t * 25))), rot=(-0.03, 0.02 * math.sin(t * 23), 0))
    elif t < 64.85: u = (t - 63.8) / 1.05; S_.update(loc=(5.0 + u, -50.0 - 16.0 * u, 0.04), rot=(-0.03, 0.03 * math.sin(t * 25), 0.06))
    else: tau = t - 64.85; S_.update(loc=(6.0, -66.0 - 3.2 * (1 - math.exp(-tau * 7)), 0.04), rot=(0.12 * (1 - math.exp(-tau * 6)), 0.15 * (1 - math.exp(-tau * 6)), 0.3 * (1 - math.exp(-tau * 6))))
    return S_
def cM(t): s = cs(t); return Matrix.Translation(s['loc']) @ Euler(s['rot'], 'XYZ').to_matrix().to_4x4()
PLOC = Matrix.Translation((0, 0.42, FLOOR)); TLOC = Matrix.Translation((0.0, -0.36, FLOOR + 0.28))
def ride(t, L, dz=0.0, pitch=0.0):
    m = cM(t) @ L @ Matrix.Translation((0, 0, dz)) @ Euler((pitch, 0, 0), 'XYZ').to_matrix().to_4x4()
    l = m.to_translation(); e = m.to_euler('XYZ'); return (l.x, l.y, l.z), (e.x, e.y, e.z)

DOWN = lambda s: (s * 0.14, 0, -1)
WHEEL = lambda s, k=0.0: (-s * 0.30 + k * 0.25, -0.75, -0.30 + s * k * 0.35)        # mani sul volante (k = sterzata)
HOLD = lambda s: (s * 0.45, -0.55, -0.70)                                              # aggrappato al cesto
def pp(t):
    S_ = dict(loc=(0, 0, 0), rot=(0, 0, 0), aL=DOWN(-1), aR=DOWN(1), hL=0.0, hR=0.0, head=(0, 0, 0))
    c = cs(t)
    if t < 4.7:                                    # mima la guida
        k = math.sin(t * 5.0); b = 0.05 * abs(math.sin(t * 9))
        S_.update(loc=(-36.0, -0.3, HTOP + 0.04 + b), rot=(0, 0.12 * k, PI / 2), aL=(-0.28 + 0.2 * k, -0.85, 0.05 + 0.25 * k), aR=(0.28 + 0.2 * k, -0.85, 0.05 - 0.25 * k), head=(0, 0.1 * k, 0.15 * k))
        if t > 3.1: S_.update(aR=lerp((0.28, -0.85, 0.05), (0.35, -0.2, 1.0), ramp(t, 3.1, 3.4)))
    elif t < 7.4:                                  # presenta il carrello
        u = ramp(t, 5.5, 5.9)
        S_.update(loc=(-36.9, 0.5, HTOP + 0.04), rot=(0, 0, 0.9), aR=lerp(DOWN(1), (0.9, -0.5, -0.1), u), aL=lerp(DOWN(-1), (-0.9, -0.2, 0.0), u), head=(0.1 * u, 0, 0))
    elif t < 10.25:                                # giù senza freni
        l, r = ride(t, PLOC); k = ramp(t, 8.6, 8.9)
        S_.update(loc=l, rot=r, aL=lerp((-0.5, 0, 1), (-0.9, -0.3, 0.3 + 0.5 * math.sin(t * 22)), k), aR=lerp((0.5, 0, 1), (0.9, -0.3, 0.3 - 0.5 * math.sin(t * 22)), k))
    elif t < 10.6:                                 # volo nel cassonetto
        u = (t - 10.25) / 0.35; l0, r0 = ride(10.25, PLOC); l1 = (BIN[0] + 0.1, BIN[1], 2.45)
        S_.update(loc=(l0[0] + (l1[0] - l0[0]) * u, l0[1] + (l1[1] - l0[1]) * u, l0[2] + (l1[2] - l0[2]) * u + 1.0 * math.sin(PI * u)), rot=(PI * sm(u), 0, PI / 2), aL=(-0.5, 0, 1), aR=(0.5, 0, 1))
    elif t < 12.8:                                 # gambe all'aria
        k = math.sin(t * 13) * math.exp(-(t - 10.6) * 0.6)
        S_.update(loc=(BIN[0] + 0.1, BIN[1], 2.45 + 0.03 * k), rot=(PI, 0, PI / 2), hL=0.75 * k, hR=-0.75 * k, aL=(-0.5, 0, 1), aR=(0.5, 0, 1))
    elif t < 19.9:                                 # spunta dal cassonetto
        u = eb_(ramp(t, 12.8, 13.25))
        S_.update(loc=(BIN[0] + 0.05, BIN[1], -0.6 + 1.05 * u), rot=(0, 0.05 * math.sin(t * 2.2), -0.75), aL=(-0.75, -0.55, -0.35), aR=(0.75, -0.55, -0.35), head=(0.08 * math.sin(t * 2.2), 0.12 * math.sin(t * 2.2), -0.3 if t > 15.4 else 0.0))
    elif t < 24.1:                                 # officina: freni
        u = ramp(t, 20.6, 20.9)
        S_.update(loc=(-38.6, -1.9, HTOP + 0.04), rot=(0, 0, 0.35), aR=lerp((0.3, -0.6, 0.5), (0.95, 0.1, 0.0), u), aL=(-0.55, -0.45, -0.7), head=(0, 0, -0.35 * u))
    elif t < 27.0:                                 # frena ma non sterza
        l, r = ride(t, PLOC); k = ramp(t, 25.0, 25.2)
        S_.update(loc=l, rot=r, aL=lerp((-0.3, 0.55, -0.75), (-0.8, -0.5, 0.2 + 0.5 * math.sin(t * 24)), k), aR=lerp((0.3, 0.55, -0.75), (0.8, -0.5, 0.2 - 0.5 * math.sin(t * 24)), k))
    elif t < 27.7:                                 # tuffo nella siepe
        u = min(1.0, (t - 27.0) / 0.22); l0, r0 = ride(27.0, PLOC); l1 = (11.0, 1.5, 1.2); k = math.sin(t * 16) * math.exp(-(t - 27.2) * 1.5)
        S_.update(loc=(l0[0] + (l1[0] - l0[0]) * u, l0[1] + (l1[1] - l0[1]) * u, l0[2] + (l1[2] - l0[2]) * u), rot=(PI / 2 * sm(u), 0, PI / 2), hL=0.6 * k, hR=-0.6 * k, aL=(-0.3, 0, 1), aR=(0.3, 0, 1))
    elif t < 29.2:                                 # la testa spunta dalla siepe
        u = eb_(ramp(t, 27.75, 28.15))
        S_.update(loc=(12.45, 1.5, -0.9 + 1.7 * u), rot=(0, 0, -0.85), aL=(-0.6, -0.3, -0.7), aR=(0.6, -0.3, -0.7), head=(0, 0.1 * math.sin(t * 3), 0.2 * math.sin(t * 2)))
    elif t < 33.2:                                 # officina: sterzo
        u = ramp(t, 30.3, 30.6)
        S_.update(loc=(-38.4, -0.9, HTOP + 0.04), rot=(0, 0, 0.5), aR=lerp((0.25, -0.65, 0.55), (0.3, -0.3, 1.0), u), aL=lerp((-0.55, -0.45, -0.7), (-0.95, 0.0, 0.1), ramp(t, 31.9, 32.2)), head=(0, 0, -0.3 * ramp(t, 31.0, 31.3)))
    elif t < 42.7 or 47.4 <= t < 51.4 or 51.4 <= t:   # a bordo
        l, r = ride(t, PLOC); st = c['steer']; S_.update(loc=l, rot=r)
        if t < 35.6: S_.update(aL=WHEEL(-1, st), aR=WHEEL(1, st), head=(0, 0, -0.4 * st))
        elif t < 42.7:                             # a spinta
            S_.update(aL=WHEEL(-1), aR=lerp((0.1, -1, 0.25 + 0.1 * math.sin(t * 8)), WHEEL(1), ramp(t, 38.6, 39.0)))
            S_['head'] = (0.3 * ramp(t, 41.0, 41.4), 0, -1.1 * ramp(t, 38.6, 39.3) * (1 - ramp(t, 40.6, 41.1)))
            S_['loc'] = (l[0], l[1], l[2] + 0.04 * abs(math.sin(t * 7)) * (1 - ramp(t, 38.4, 38.8)))
        elif t < 51.4: S_.update(aL=WHEEL(-1, st), aR=lerp(WHEEL(1, st), (0.45, -0.2, 1.0), ramp(t, 49.4, 49.8)))
        elif t < 58.4: S_.update(aL=WHEEL(-1), aR=lerp(WHEEL(1), (0.9, -0.3, 0.55), ramp(t, 52.9, 53.2) * (1 - ramp(t, 54.2, 54.6))), head=(-0.3 * ramp(t, 52.5, 52.7) * (1 - ramp(t, 53.0, 53.3)), 0, 0))
        elif t < 62.85: S_.update(aL=WHEEL(-1, st), aR=WHEEL(1, st), head=(0, 0, -0.4 * st), rot=(r[0], r[1] , r[2]))
        elif t < 64.85:                            # la leva gli resta in mano
            u = ramp(t, 62.85, 63.0); v = ramp(t, 63.05, 63.3)
            S_.update(aL=WHEEL(-1), aR=lerp(lerp(WHEEL(1), (0.35, 0.6, -0.7), u), (0.30, -0.75, 0.35), v), head=(0, 0, -0.45 * v * (1 - ramp(t, 63.5, 63.7))))
        else: S_.update(aL=(-0.6, 0, 1), aR=(0.6, 0, 1))
    elif t < 44.35:                                # vicino al tosaerba
        k = 0.15 * math.sin(t * 16)
        S_.update(loc=(-40.6, -2.7, HTOP + 0.04), rot=(0, 0, 0.8), aL=(-0.12 + k, -0.9, 0.0), aR=(0.12 - k, -0.9, 0.0), head=(0.15, 0, 0.3))
    else:                                          # officina: motore
        S_.update(loc=(-38.9, -2.3, HTOP + 0.04), rot=(0, 0, 0.35), aR=(0.9, 0.1, 0.1), aL=(-0.55, -0.45, -0.7))
    return S_
def eb_(u): u = min(1.0, max(0.0, u)); c1 = 1.6; return 1 + (c1 + 1) * (u - 1) ** 3 + c1 * (u - 1) ** 2

def walk(t, sp=14.0, am=0.55):
    s = math.sin(t * sp) * am; return dict(FL=s, FR=-s, BL=-s, BR=s)
def tp(t):
    S_ = dict(loc=(0, 0, 0), rot=(0, 0, 0), legs=dict(FL=0, FR=0, BL=0, BR=0), head=(0, 0, 0), tail=-1.0 + 0.5 * math.sin(t * 12))
    if t < 4.7: S_.update(loc=(-34.9, 1.3, HTOP + 0.04), rot=(0, 0, 0.3), head=(-0.2, 0.25 * math.sin(t * 2.5), 0.9))
    elif t < 7.4:
        c = cs(t)['loc']
        if t < 5.65: S_.update(loc=(c[0] - 1.25, -0.8, HTOP + 0.04), rot=(0, 0, PI / 2), legs=walk(t, 20), head=(0.3, 0, 0))
        else: u = ramp(t, 5.7, 6.3); S_.update(loc=(-36.45 + 2.2 * u, -0.8 - 1.4 * u, HTOP + 0.04 + 0.2 * math.sin(PI * u)), rot=(0, 0, PI / 2 - 1.3 * u), legs=walk(t, 18) if u < 1 else dict(FL=0, FR=0, BL=0, BR=0))
    elif t < 15.4:
        j = 0.03 * math.sin(t * 40) * ramp(t, 11.5, 12.5)
        S_.update(loc=(7.9, -3.6, 0.04 + abs(j)), rot=(0, 0, PI / 2 - 0.7), head=(-0.25, 0, 0.0))
    elif t < 19.9:                                 # si rotola dal ridere
        k = math.sin(t * 9)
        S_.update(loc=(8.2 + 0.25 * math.sin(t * 2.2), -3.4, 0.52), rot=(0, PI + 0.6 * math.sin(t * 4.4), 0.7), legs=dict(FL=0.8 * k, FR=-0.8 * k, BL=-0.7 * k, BR=0.7 * k), head=(0.2 * k, 0, 0.3))
    elif t < 24.1 or 29.2 <= t < 33.2 or 42.7 <= t < 47.4 or 51.4 <= t < 54.3:
        S_.update(loc=(-38.5, -3.5, HTOP + 0.04), rot=(0, 0, 0.9), head=(-0.2, 0, -0.5))
        if 42.7 <= t < 47.4: S_.update(loc=(-38.3, -4.2, HTOP - 0.10), legs=dict(FL=-1.3, FR=-1.3, BL=1.3, BR=1.3), head=(0.35, 0, 0.3))    # sfinito a terra
    elif t < 29.2:
        d = ramp(t, 27.0, 27.2); S_.update(loc=(7.6, -3.9, 0.04), rot=(0, 0, PI / 2 - 0.9), head=(-0.2 + 0.75 * d, 0, 0.3))
    elif t < 35.6:
        h = 0.3 * abs(math.sin((t - 34.9) * 10)) if t > 34.9 else 0; S_.update(loc=(0.9, -4.6, 0.18 + h), rot=(0, 0, 0.6), head=(-0.3, 0, 0))
    elif t < 42.7:                                 # spinge il carrello
        c = cs(t)['loc']; k = ramp(t, 41.0, 41.4)
        S_.update(loc=(4.5, c[1] + 1.22 + 0.5 * k, 0.04 - 0.14 * k), rot=(0, 0, 0), legs=walk(t, 26, 0.7) if k < 0.5 else dict(FL=-1.3, FR=-1.3, BL=1.3, BR=1.3), head=(0.35 - 0.1 * k, 0, 0))
    elif 54.3 <= t < 54.7:                         # salta a bordo
        u = (t - 54.3) / 0.4; l1, r1 = ride(54.7, TLOC); l0 = (-38.5, -3.5, HTOP + 0.04)
        S_.update(loc=(l0[0] + (l1[0] - l0[0]) * u, l0[1] + (l1[1] - l0[1]) * u, l0[2] + (l1[2] - l0[2]) * u + 0.8 * math.sin(PI * u)), rot=(0, 0, 0.9 + (r1[2] - 0.9) * u))
    else:                                          # a bordo
        dz = 0.0; j = 0.0; hd = (0.0, 0, 0)
        if 54.7 <= t < 58.4: j = 0.022 * math.sin(t * 55); dz = -0.42 * ramp(t, 56.7, 57.0) * (1 - 0.6 * ramp(t, 57.6, 57.9))
        if t >= 63.25: dz = -0.40 * ramp(t, 63.25, 63.5)
        l, r = ride(t, TLOC, dz); S_.update(loc=(l[0] + j, l[1], l[2]), rot=r, head=(-0.15, 0.1 * math.sin(t * 6), 0), legs=dict(FL=0.3, FR=0.3, BL=0, BR=0))
    return S_
def gp(t):
    """vecchietta: loc, yaw, saluto."""
    if 35.6 <= t < 42.7: return (8.0, -19.0 - 2.4 * (t - 39.0), 0.04), 0.0, ramp(t, 40.2, 40.5) * (1 - ramp(t, 41.0, 41.2))
    if 60.0 <= t < 63.8: return (8.0, -26.0 - 0.8 * (t - 61.2), 0.04), 4 * PI * ramp(t, 61.85, 62.7), 0.0
    return (0, -300, 0), 0.0, 0.0

# ======================= chiavi =======================
T_IMP = 64.85; pr = np.random.default_rng(4)
pv = {(c, r): (pr.uniform(-2.5, 2.5), pr.uniform(5, 9), pr.uniform(1, 4), pr.uniform(-8, 8), pr.uniform(-8, 8)) for c in (1, 2) for r in (0, 1, 2)}
TR = Tb['root']
for f in range(1, NF + 1):
    t = (f - 1) / FPS
    c = cs(t); CR.location = c['loc']; CR.rotation_euler = c['rot']; CR.keyframe_insert('location', frame=f); CR.keyframe_insert('rotation_euler', frame=f)
    for wq in stws: wq.rotation_euler = (0, 0, -c['steer'] * 0.7); wq.keyframe_insert('rotation_euler', frame=f)
    stwheel.rotation_euler = (-0.456, 0, -c['steer'] * 2.2); stwheel.keyframe_insert('rotation_euler', frame=f)
    s = pp(t); r = P['root']; r.location = s['loc']; r.rotation_euler = s['rot']; r.keyframe_insert('location', frame=f); r.keyframe_insert('rotation_euler', frame=f)
    for nm, k in (('L', 'aL'), ('R', 'aR')):
        sh = P['shoulder' + nm]; sh.rotation_quaternion = qdir(s[k]); sh.keyframe_insert('rotation_quaternion', frame=f)
    for nm, k in (('L', 'hL'), ('R', 'hR')):
        hp = P['hip' + nm]; hp.rotation_euler = (s[k], 0, 0); hp.keyframe_insert('rotation_euler', frame=f)
    P['head'].rotation_euler = s['head']; P['head'].keyframe_insert('rotation_euler', frame=f)
    q = tp(t); TR.location = q['loc']; TR.rotation_euler = q['rot']; TR.keyframe_insert('location', frame=f); TR.keyframe_insert('rotation_euler', frame=f)
    for k, v in q['legs'].items(): Tb['leg' + k].rotation_euler = (v, 0, 0); Tb['leg' + k].keyframe_insert('rotation_euler', frame=f)
    Tb['head'].rotation_euler = q['head']; Tb['head'].keyframe_insert('rotation_euler', frame=f)
    Tb['tail'].rotation_euler = (q['tail'], 0, 0.5 * math.sin(t * 14)); Tb['tail'].keyframe_insert('rotation_euler', frame=f)
    # vecchietta
    gl_, gy_, gw_ = gp(t); gr = G['root']; gr.location = gl_; gr.rotation_euler = (0, 0, gy_); gr.keyframe_insert('location', frame=f); gr.keyframe_insert('rotation_euler', frame=f)
    k = math.sin(t * 13)
    G['hipL'].rotation_euler = (0.35 * k, 0, 0); G['hipR'].rotation_euler = (-0.35 * k, 0, 0)
    G['shoulderL'].rotation_euler = (-0.75 - 2.2 * gw_ + 0.3 * gw_ * math.sin(t * 20), 0, 0); G['shoulderR'].rotation_euler = (-0.75, 0, 0)
    for nm in ('hipL', 'hipR', 'shoulderL', 'shoulderR'): G[nm].keyframe_insert('rotation_euler', frame=f)
    # motore del tosaerba che salta via
    tau = t - 44.3
    mowen.location = (0, 0.02, 0.28 + (3.5 * tau if tau > 0 else 0.02 * abs(math.sin(t * 30)) * ramp(t, 43.6, 44.0))); mowen.keyframe_insert('location', frame=f)
    # semaforo
    for i_, m_ in enumerate(semm):
        on = (i_ == 0 and 58.3 <= t < 58.65) or (i_ == 1 and 58.65 <= t < 58.95) or (i_ == 2 and 58.95 <= t < 60.2)
        m_.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value = 6.0 if on else 0.0
        m_.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].keyframe_insert('default_value', frame=f)
    # serranda del garage
    for (c_, r_, pn) in panels:
        base = (3.8 + 0.55 + c_ * 1.1, GY - 0.06, 0.3 + r_ * 0.6); tau = t - T_IMP
        if (c_, r_) in pv and tau > 0:
            vx, vy, vz, wx, wz = pv[(c_, r_)]
            pn.location = (base[0] + vx * tau, base[1] - vy * tau * math.exp(-tau), max(0.1, base[2] + vz * tau - 6 * tau * tau)); pn.rotation_euler = (wx * tau, 0, wz * tau)
        else:
            sh_ = 0.04 * math.exp(-tau * 5) * math.sin(tau * 40) if tau > 0 else 0
            pn.location = (base[0], base[1] + sh_, base[2]); pn.rotation_euler = (0, 0, 0)
        pn.keyframe_insert('location', frame=f); pn.keyframe_insert('rotation_euler', frame=f)
    # ruota persa che rotola fuori
    tau = t - 65.0
    lostw.location = (5.2 - 0.3 * tau, GY + 0.3 + 3.2 * tau, 0.29 + 0.25 * abs(math.sin(tau * 9)) * math.exp(-tau * 2)) if tau > 0 else (0, 0, -50); lostw.rotation_euler = (9 * max(tau, 0), 0, 0)
    lostw.keyframe_insert('location', frame=f); lostw.keyframe_insert('rotation_euler', frame=f)
    # vicino
    mx = 8.6 - 2.1 * ramp(t, 65.45, 65.85)
    man['root'].location = (mx, GY - 0.7, 0.05); man['root'].rotation_euler = (0, 0, PI - 0.25); man['root'].keyframe_insert('location', frame=f); man['root'].keyframe_insert('rotation_euler', frame=f)
    man['shoulderL'].rotation_euler = (-0.3, 0, 0.3); man['shoulderR'].rotation_euler = (-1.0, 0, 0)
    ball.location = (0.40, -0.62, 1.22 + 0.30 * abs(math.sin(t * 6.0))); ball.keyframe_insert('location', frame=f)
    # sacchi/coperchio del cassonetto: botta
    tau = t - 10.25
    dlid.rotation_euler = (math.radians(-100) + (0.5 * math.exp(-tau * 4) * math.sin(tau * 14) if tau > 0 else 0), 0, 0); dlid.keyframe_insert('rotation_euler', frame=f)

# espressioni
_lastP = [None, -1.0]; _lastT = [None, -1.0]
def pex(t, **k):
    if _lastP[0] is not None and t - 0.06 > _lastP[1]: pippo.express(P, fr(t - 0.06), **_lastP[0])
    pippo.express(P, fr(t), **k); _lastP[0] = k; _lastP[1] = t
def tex(t, **k):
    if _lastT[0] is not None and t - 0.06 > _lastT[1]: tumbo.tumbo_express(Tb, fr(t - 0.06), **_lastT[0])
    tumbo.tumbo_express(Tb, fr(t), **k); _lastT[0] = k; _lastT[1] = t
pex(0.0, smile=0.9, brow=0.6, mouth_open=0.4); pex(3.1, smile=1.0, brow=0.8, eye_scale=1.1); pex(4.8, smile=0.8, brow_lift=0.4); pex(5.6, smile=1.0, brow=0.3)
pex(7.5, smile=1.0, mouth_open=0.6, brow=0.5); pex(8.7, brow=-0.8, brow_lift=0.7, eye_scale=1.25, mouth_open=1.0); pex(10.3, eye_open=0.08, mouth_open=0.6)
pex(12.8, eye_open=0.45, brow=-0.3, mouth_open=0.15, look=(0.4, 0.3)); pex(15.4, brow=1.0, eye_open=0.7, look=(0.6, -0.4))
pex(20.0, brow=0.6, smile=0.2, look=(0.5, 0)); pex(20.8, smile=0.9, brow=0.5); pex(24.2, smile=0.9, brow=0.6); pex(25.05, brow=-0.8, brow_lift=0.7, eye_scale=1.3, mouth_open=1.0)
pex(27.0, eye_open=0.08, mouth_open=0.8); pex(27.8, brow=1.0, eye_open=0.6, mouth_open=0.1); pex(29.3, brow=0.5, smile=0.1, look=(0.3, 0.5)); pex(30.5, smile=1.0, brow_lift=0.6, eye_scale=1.1)
pex(33.3, smile=0.9, brow=0.7); pex(34.9, smile=1.0, eye_open=0.8); pex(36.0, brow=0.7, mouth_open=0.4); pex(38.7, brow_lift=0.6, eye_scale=1.15, mouth_open=0.4, look=(-0.8, 0))
pex(41.2, brow=1.0, eye_open=0.55, look=(0, -0.5)); pex(42.8, smile=1.0, brow=1.0, eye_open=0.7, look=(-0.4, -0.3)); pex(44.4, smile=1.0, brow=0.6)
pex(47.5, smile=1.0, mouth_open=0.7, brow=0.7, eye_scale=1.1); pex(49.3, smile=1.0, brow=0.9, eye_open=0.8); pex(51.6, smile=0.8, brow=0.5); pex(52.6, brow_lift=0.5, look=(0, 0.7), smile=0.6)
pex(53.4, smile=1.0, brow=0.6); pex(54.8, smile=0.7, look=(0, -0.6)); pex(58.5, brow=1.0, smile=0.6, eye_open=0.8); pex(59.0, smile=1.0, mouth_open=0.6, brow=0.9)
pex(60.1, smile=1.0, brow=1.0, eye_open=0.8); pex(61.3, smile=1.0, mouth_open=0.5, brow=0.8); pex(62.9, brow_lift=0.5, mouth_open=0.2); pex(63.1, brow=-0.6, brow_lift=0.6, eye_scale=1.2, look=(0.6, 0.2), mouth_open=0.3)
pex(63.6, brow=-0.8, brow_lift=0.7, eye_scale=1.3, mouth_open=1.0)
tex(0.0, tongue=0.5); tex(4.8, tongue=0.7); tex(7.5, eye_scale=1.15); tex(10.3, eye_scale=1.35, brow=-0.5); tex(11.5, tongue=0.6, eye_open=0.6, brow=0.4)
tex(15.4, tongue=1.0, eye_open=0.25, brow=0.5); tex(20.0, tongue=0.4); tex(24.2, eye_scale=1.1); tex(27.0, eye_open=0.1); tex(29.3, tongue=0.5); tex(33.3, eye_scale=1.1, tongue=0.3)
tex(34.9, tongue=0.9); tex(36.0, tongue=1.0, eye_open=0.6, brow=-0.4); tex(41.2, tongue=1.0, eye_open=0.15); tex(47.5, tongue=1.0, eye_scale=1.1); tex(51.6, tongue=0.4)
tex(54.8, eye_scale=1.45, brow=-0.8); tex(58.5, eye_scale=1.4, brow=-0.8); tex(60.1, eye_scale=1.5, brow=-0.8); tex(63.3, eye_open=0.05)

# ======================= effetti =======================
def streak(name, sc, mat, t0, t1, fn, parent=None):
    o = obj(name, shared_mesh('sphere_lo'), (0, 0, -80), sc, mat, prc, parent=parent)
    o.hide_render = True; o.keyframe_insert('hide_render', frame=1); o.hide_render = False; o.keyframe_insert('hide_render', frame=fr(t0)); o.hide_render = True; o.keyframe_insert('hide_render', frame=fr(t1))
    for f in range(fr(t0), fr(t1) + 1):
        r_ = fn((f - 1) / FPS); o.location = r_[0]; o.keyframe_insert('location', frame=f)
        if len(r_) > 1: o.scale = r_[1]; o.keyframe_insert('scale', frame=f)
    return o
er = np.random.default_rng(3)
def trail(name, mat, t0, t1, local, n=7, period=0.55, rise=1.2, s0=0.08, s1=0.5, spread=0.25):
    """sbuffi che restano indietro rispetto al carrello (fumo, scintille)."""
    for k in range(n):
        ox, oy = er.uniform(-spread, spread, 2)
        def fn(t, k=k, ox=ox, oy=oy):
            age = ((t / period + k / n) % 1.0) * period; p = cM(t - age) @ Vector(local)
            a = age / period; return ((p.x + ox * a, p.y + oy * a, p.z + rise * a * a), (max(0.001, s0 + (s1 - s0) * a) * (1 - a * a * 0.6),) * 3)
        streak(name, (0.1, 0.1, 0.1), mat, t0, t1, fn)
REAR = (0.33, BL / 2 + 0.75, 0.55)
trail('Fumo', K['smoke'], 47.4, 51.4, REAR); trail('Fumo', K['smoke'], 58.95, 65.0, REAR, n=8)
trail('FumoGomme', K['smoke'], 58.95, 59.6, (0, BL / 2 * 0.82, 0.15), n=6, period=0.35, rise=0.5, s1=0.6)
trail('FumoGomme', K['smoke'], 60.3, 61.0, (0, BL / 2 * 0.82, 0.15), n=6, period=0.35, rise=0.5, s1=0.6)
for sx in (-1, 1): trail('Scintille', K['flame'], 24.3, 27.0, (sx * BW * 0.44, BL / 2 * 0.82, 0.08), n=5, period=0.18, rise=0.35, s0=0.07, s1=0.02, spread=0.3)
def burst(name, mat, t0, dur, c0, n, vmax, sc, grav=4.9, flat=1.0):
    for k in range(n):
        v = np.array([er.uniform(-vmax, vmax), er.uniform(-vmax, vmax), er.uniform(0.3, 1.0) * vmax])
        streak(name, sc, mat, t0, t0 + dur, lambda t, v=v: ((c0[0] + v[0] * (t - t0), c0[1] + v[1] * (t - t0), max(0.05, c0[2] + v[2] * (t - t0) - grav * (t - t0) ** 2)),))
def puffs(t0, c0, n=7, r=1.6, s=0.3, dur=0.8):
    for k in range(n):
        an = k / n * 6.283
        streak('Polvere', (0.1, 0.1, 0.1), M['dust'], t0, t0 + dur, lambda t, an=an: ((c0[0] + (0.3 + r * (t - t0)) * math.cos(an), c0[1] + (0.3 + r * (t - t0)) * math.sin(an) * 0.7, c0[2] + 0.6 * (t - t0)),
                                                                                      (max(0.001, s * math.sin(PI * min(1, (t - t0) / dur))),) * 3))
puffs(10.25, (10.2, -1.2, 0.5)); burst('Rifiuto', K['trash'], 10.25, 1.2, (10.9, -1.2, 1.5), 6, 2.5, (0.12, 0.12, 0.10))
burst('Foglia', M['leaf'][0], 27.0, 1.4, (11.6, 1.5, 1.2), 10, 3.0, (0.16, 0.16, 0.05)); burst('Foglia', M['leaf'][1], 27.0, 1.4, (11.6, 1.5, 1.4), 8, 3.0, (0.14, 0.14, 0.05))
streak('Foglia', (0.10, 0.10, 0.03), M['leaf'][2], 28.55, 29.2, lambda t: ((12.45 - 0.33 - 2.5 * (t - 28.55), 1.6, 2.38 + 1.2 * (t - 28.55) - 4 * (t - 28.55) ** 2),))
puffs(T_IMP, (6.0, GY + 0.2, 0.7), n=9, r=2.6, s=0.30, dur=0.8); puffs(T_IMP + 0.1, (6.0, GY + 0.5, 1.5), n=7, r=1.8, s=0.24, dur=0.7)

# ======================= camera =======================
def CW(t): return cs(t)['loc']
def GW(t): return gp(t)[0]
def Z0(t): return (0, 0, 0)
H = HTOP
SHOTS = [  # t0, t1, sub cam, p0, p1, sub mira, a0, a1, lente, f
    (0.0, 4.7, Z0, (-32.4, -1.6, H + 1.2), (-33.3, -1.2, H + 1.3), Z0, (-36.0, -0.3, H + 1.42), (-36.0, -0.3, H + 1.5), 35, 2.8),
    (4.7, 7.4, Z0, (-32.6, -4.6, H + 1.25), (-33.0, -4.0, H + 1.15), Z0, (-35.6, -0.3, H + 0.95), (-35.8, -0.2, H + 1.0), 30, 5),
    (7.4, 9.5, CW, (1.5, -5.6, 1.5), (3.0, -4.6, 1.1), CW, (0.6, 0, 1.3), (0.8, 0, 1.3), 28, 8),
    (9.5, 11.0, Z0, (6.6, -8.0, 1.8), (7.0, -7.4, 1.7), Z0, (9.9, -1.2, 1.3), (10.2, -1.2, 1.4), 28, 8),
    (11.0, 12.8, Z0, (7.6, -4.6, 1.7), (7.9, -4.2, 1.75), Z0, (10.95, -1.2, 1.95), (10.95, -1.2, 1.95), 40, 5),
    (12.8, 15.4, Z0, (8.2, -4.6, 1.8), (8.6, -4.2, 1.85), Z0, (10.95, -1.2, 1.78), (10.95, -1.2, 1.8), 45, 4),
    (15.4, 19.9, Z0, (6.4, -5.7, 0.5), (6.8, -5.2, 0.45), Z0, (8.5, -3.2, 0.6), (8.5, -3.2, 0.6), 35, 4),
    (19.9, 22.4, Z0, (-34.2, -5.6, H + 1.2), (-34.7, -5.0, H + 1.2), Z0, (-37.9, -1.3, H + 1.0), (-37.9, -1.3, H + 1.0), 28, 6),
    (22.4, 23.3, Z0, (-35.0, -3.4, H + 2.0), (-35.2, -3.2, H + 1.9), Z0, (-36.52, -1.21, H + 1.2), (-36.52, -1.21, H + 1.2), 42, 5),
    (23.3, 24.1, Z0, (-35.3, -3.2, H + 0.5), (-35.5, -3.0, H + 0.45), Z0, (-36.7, -0.95, H + 0.16), (-36.7, -0.95, H + 0.16), 45, 5),
    (24.1, 25.0, CW, (2.0, -5.6, 1.2), (3.2, -4.6, 1.0), CW, (0.5, 0, 1.3), (0.5, 0, 1.3), 30, 8),
    (25.0, 26.4, CW, (4.4, -1.0, 2.0), (3.7, -0.7, 2.0), CW, (0, 0, 1.95), (0, 0, 1.95), 40, 4),
    (26.4, 27.7, Z0, (6.0, -7.0, 1.9), (6.5, -6.4, 1.8), Z0, (10.4, 1.2, 1.2), (10.6, 1.3, 1.2), 28, 8),
    (27.7, 29.2, Z0, (9.6, -1.9, 2.5), (9.9, -1.6, 2.55), Z0, (12.3, 1.5, 2.45), (12.3, 1.5, 2.45), 45, 4),
    (29.2, 33.2, Z0, (-34.9, -4.8, H + 1.3), (-35.3, -4.0, H + 1.35), Z0, (-37.3, -1.0, H + 1.1), (-37.2, -1.0, H + 1.05), 30, 5),
    (33.2, 35.6, Z0, (13.5, -13.0, 6.5), (12.5, -12.0, 6.0), CW, (0, -0.5, 0.8), (0, -0.5, 0.8), 50, 8),
    (35.6, 38.0, Z0, (10.6, -15.0, 0.9), (10.3, -16.2, 0.9), CW, (-0.4, 0.5, 1.1), (-0.4, 0.5, 1.1), 28, 8),
    (38.0, 40.0, Z0, (11.2, -18.2, 1.3), (11.2, -19.4, 1.3), Z0, (6.2, -18.2, 1.1), (6.0, -20.6, 1.1), 26, 8),
    (40.0, 41.2, GW, (2.4, -2.6, 1.2), (2.2, -2.4, 1.2), GW, (0, 0, 1.25), (0, 0, 1.25), 45, 4),
    (41.2, 42.7, CW, (-0.6, -3.4, 1.95), (-0.4, -2.9, 1.95), CW, (0, -0.3, 2.0), (0, -0.3, 2.0), 40, 4),
    (42.7, 44.35, Z0, (-37.4, -6.4, H + 1.0), (-37.8, -6.0, H + 0.95), Z0, (-39.7, -3.2, H + 0.75), (-39.7, -3.2, H + 0.75), 32, 5),
    (44.35, 45.2, Z0, (-35.0, -3.6, H + 1.25), (-35.2, -3.3, H + 1.15), Z0, (-36.6, -1.15, H + 0.6), (-36.6, -1.15, H + 0.6), 40, 5),
    (45.2, 46.35, Z0, (-34.2, -1.5, H + 0.8), (-34.4, -1.4, H + 0.75), Z0, (-36.4, -0.85, H + 0.38), (-36.4, -0.85, H + 0.38), 38, 5),
    (46.35, 47.4, Z0, (-36.0, -1.95, H + 2.4), (-36.1, -1.85, H + 2.35), Z0, (-37.05, -0.55, H + 1.72), (-37.05, -0.55, H + 1.72), 45, 5),
    (47.4, 49.2, CW, (5.5, -2.5, 1.2), (4.8, -3.6, 1.0), CW, (0, -0.6, 1.3), (0, -0.6, 1.3), 28, 8),
    (49.2, 51.4, CW, (-0.7, -4.6, 1.8), (-0.4, -3.8, 1.9), CW, (0, -0.2, 1.8), (0, -0.2, 1.85), 38, 4),
    (51.4, 54.7, Z0, (-34.8, -4.5, H + 1.5), (-35.3, -3.8, H + 1.6), Z0, (-37.0, -0.6, H + 1.35), (-37.0, -0.6, H + 1.5), 32, 6),
    (54.7, 58.4, Z0, (-35.3, -3.1, H + 1.45), (-35.6, -2.7, H + 1.45), Z0, (-36.8, -0.8, H + 1.32), (-36.8, -0.8, H + 1.32), 50, 4),
    (58.4, 60.0, Z0, (-29.4, -5.0, H + 0.9), (-28.6, -5.0, H + 0.7), CW, (1.2, 0, 1.3), (0.8, 0, 1.3), 28, 8),
    (60.0, 61.2, Z0, (13.0, -12.5, 5.5), (12.5, -12.0, 5.0), CW, (0, 0, 0.8), (0, 0, 0.8), 55, 8),
    (61.2, 62.6, Z0, (12.6, -25.0, 1.5), (12.4, -25.6, 1.5), Z0, (7.4, -26.6, 1.1), (7.4, -26.9, 1.1), 28, 8),
    (62.6, 63.8, CW, (-0.6, -3.8, 2.05), (-0.4, -3.1, 2.05), CW, (0, -0.2, 2.0), (0, -0.2, 2.0), 40, 4),
    (63.8, 65.3, Z0, (12.6, -53.5, 2.5), (11.8, -54.8, 2.3), Z0, (6.2, -65.2, 1.3), (6.2, -65.6, 1.3), 28, 8),
    (65.3, 66.6, Z0, (5.0, -60.3, 1.4), (5.2, -61.2, 1.4), Z0, (6.0, -66.0, 1.25), (6.1, -66.0, 1.3), 35, 6),
]
camd = bpy.data.cameras.new('Cam'); cam = bpy.data.objects.new('Cam', camd); cac.objects.link(cam); scene.camera = cam
camd.clip_start = 0.1; camd.clip_end = 900; camd.sensor_width = 36
tgt = empty('CamTarget', (0, 0, 1), None, cac)
ct = cam.constraints.new('TRACK_TO'); ct.target = tgt; ct.track_axis = 'TRACK_NEGATIVE_Z'; ct.up_axis = 'UP_Y'
camd.dof.use_dof = True; camd.dof.focus_object = tgt
for f in range(1, NF + 1):
    t = (f - 1) / FPS
    s_ = next((s for s in SHOTS if s[0] <= t < s[1]), SHOTS[-1]); u = (t - s_[0]) / (s_[1] - s_[0])
    cam.location = add(s_[2](t), lerp(s_[3], s_[4], u)); tgt.location = add(s_[5](t), lerp(s_[6], s_[7], u))
    camd.lens = s_[8]; camd.dof.aperture_fstop = s_[9]
    cam.keyframe_insert('location', frame=f); tgt.keyframe_insert('location', frame=f); camd.keyframe_insert('lens', frame=f); camd.dof.keyframe_insert('aperture_fstop', frame=f)

def lin(idb):
    for fc in all_fcurves(idb):
        kind = 'CONSTANT' if 'hide' in fc.data_path else 'LINEAR'
        for kp in fc.keyframe_points: kp.interpolation = kind
for o in bpy.data.objects:
    lin(o)
    if o.type == 'MESH' and o.data.shape_keys: lin(o.data.shape_keys)
for m_ in semm: lin(m_.node_tree)
set_interp(camd, 'CONSTANT')
os.makedirs('../t006', exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath('../t006/pippo_t006.blend')); print('SAVED')
