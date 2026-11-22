"""Test 005 - COME UNA TOVAGLIA DIVENTA UN PARACADUTE. Salva ../t005/pippo_t005.blend
Personaggi: modelli ESISTENTI (pippo.py, tumbo.py) invariati."""
import sys, math, os
sys.path.insert(0, os.path.dirname(__file__))
import bpy, numpy as np
from mathutils import Vector, Euler, Matrix
from common import *
from render_setup import *
from params004 import BX, BY
import set004, props004, props005, pippo, tumbo
from set004 import obj, bx, cyl, ball_, MB, WALL, ROOF, SHUT, FRAME, GLASS, DOOR, STONE, CHIM, HEDGE, WOOD

FPS = 24; TOTAL = 46.0; NF = int(TOTAL * FPS)
def fr(t): return max(1, int(round(t * FPS)) + 1)
def sm(x): x = min(1.0, max(0.0, x)); return x * x * (3 - 2 * x)
def ramp(t, a, b): return sm((t - a) / (b - a))
def lerp(a, b, u): return tuple(a[i] + (b[i] - a[i]) * u for i in range(len(a)))
def eb(u): u = min(1.0, max(0.0, u)); c1 = 1.6; return 1 + (c1 + 1) * (u - 1) ** 3 + c1 * (u - 1) ** 2
def add(a, b): return tuple(a[i] + b[i] for i in range(3))
TINY = (0.0001, 0.0001, 0.0001)

reset_scene(); scene = bpy.context.scene
setup_render(scene, 1080, 1920, samples=16, fps=FPS, frames=NF); scene.frame_end = NF
scene.eevee.shadow_resolution_scale = 0.25
rng = np.random.default_rng(11)
M = set004.make_mats(); Q = props005.mats005()
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
for k in range(26):
    an = k / 26 * 2 * math.pi + _cr.uniform(-0.15, 0.15); rr = _cr.uniform(48, 95); s_ = _cr.uniform(2.2, 4.5)
    cw = empty('CloudW', (rr * math.cos(an), rr * math.sin(an), _cr.uniform(14, 60)), None, prc)
    for (dx, dy, dz, r_) in [(0, 0, 0, 1.5), (1.5, 0.3, -0.2, 1.15), (-1.5, -0.2, -0.25, 1.2), (0.6, -0.5, 0.6, 1.1), (-0.6, 0.5, 0.5, 1.0), (2.6, 0, -0.45, 0.75), (-2.7, 0, -0.5, 0.8)]:
        c_, s2 = math.cos(an + math.pi / 2), math.sin(an + math.pi / 2)
        ball_('Puff', r_ * s_, (dx * s_ * c_, dx * s_ * s2 + dy, dz * s_), M['cloudw'], prc, parent=cw, sc=(1, 1, 0.6))

# ======================= ambiente =======================
houses, cinfo = set004.build_city(envc, M, rng)
bx('Lawn', (-BX - .3, -BY - .3, -0.06), (BX + .3, BY + .3, 0.0), M['park'], envc)
def desc(o):
    for c in o.children:
        yield c
        yield from desc(c)
for o in list(envc.objects):
    if o.name.startswith('Tree') and o.parent is None and o.location.y < -3:
        for q in [o] + list(desc(o)): q.hide_render = True

HOUSE = (-4.5, 4.5); RIDGE_Z = 5.9
mb = MB(set004.house_mats(M, 0, 0, 1)); set004.house_geo(mb, 5.0, 4.0, 4.5, True, rng); mb.build('CasaPippo', envc, (HOUSE[0], HOUSE[1], 0), 0.0)

TABLE = (-8.0, -2.5)
tb_ = MB([M['wood'], M['frame']])
tb_.box((0, 0, 0.75), (1.5, 1.5, 0.06), 0)
for sx in (-0.62, 0.62):
    for sy in (-0.62, 0.62): tb_.box((sx, sy, 0.36), (0.09, 0.09, 0.72), 0)
for sy in (-1.15, 1.15):
    tb_.box((0, sy, 0.42), (1.5, 0.32, 0.05), 0)
    for sx in (-0.6, 0.6): tb_.box((sx, sy, 0.2), (0.08, 0.26, 0.40), 0)
tb_.build('Tavolo', envc, (TABLE[0], TABLE[1], 0))
M['plate'] = material('S_plate', (0.98, 0.98, 1.0), rough=0.2, spec=0.7); M['bottle'] = material('S_bottle', (0.1, 0.55, 0.2), rough=0.15, spec=0.9)
M['food'] = material('S_food', (0.95, 0.55, 0.15), rough=0.6)
dishes = []
for (dx, dy, kind) in [(-0.35, -0.3, 'p'), (0.35, 0.3, 'p'), (0.0, 0.05, 'b'), (0.4, -0.35, 'g'), (-0.4, 0.3, 'g')]:
    if kind == 'p':
        d = cyl('Piatto', 0.17, 0.03, (TABLE[0] + dx, TABLE[1] + dy, 0.815), M['plate'], prc); ball_('Cibo', 0.09, (0, 0, 0.05), M['food'], prc, parent=d, sc=(1, 1, 0.6))
    elif kind == 'b': d = cyl('Bottiglia', 0.055, 0.34, (TABLE[0] + dx, TABLE[1] + dy, 0.97), M['bottle'], prc)
    else: d = cyl('Bicchiere', 0.045, 0.12, (TABLE[0] + dx, TABLE[1] + dy, 0.86), M['window'], prc)
    dishes.append(d)

TREE = (0.8, 2.6)
cyl('BigTrunk', 0.32, 3.4, (TREE[0], TREE[1], 1.7), M['bark'], envc)
for k, (dx, dy, dz, r) in enumerate([(0, 0, 4.4, 2.0), (1.2, 0.2, 4.0, 1.4), (-1.2, -0.1, 4.1, 1.5), (0.2, -0.9, 3.9, 1.3), (0, 0.8, 4.2, 1.5), (0.3, 0, 5.4, 1.3)]):
    ball_('BigLeaf', r, (TREE[0] + dx, TREE[1] + dy, dz), M['leaf'][k % 3], envc)

FENCE_X = 4.0
fm = MB([M['frame'], M['hedge'], M['flower'][0], M['flower'][1]])
for yy in np.arange(-7.0, 7.01, 0.20):
    fm.box((FENCE_X, yy, 0.36), (0.04, 0.10, 0.72), 0); fm.box((FENCE_X, yy, 0.74), (0.04, 0.07, 0.08), 0)
for zz in (0.22, 0.52): fm.box((FENCE_X + 0.03, 0, zz), (0.03, 14.1, 0.06), 0)
for k, yy in enumerate(np.arange(-6.2, 6.3, 2.5)):       # aiuole del vicino
    fm.box((FENCE_X + 0.45, yy, 0.22), (0.5, 1.2, 0.44), 1)
    for j in range(5): fm.box((FENCE_X + 0.45 + 0.12 * ((j % 2) * 2 - 1), yy - 0.45 + j * 0.22, 0.48), (0.11, 0.11, 0.11), 2 + (j + k) % 2)
fm.build('Staccionata', envc)

# casa del vicino (stessa del Test 004, con la finestra ancora rotta)
DX = -13.5
nmb = MB(set004.house_mats(M, 3, 0, 0))
def nb(p0, p1, mi): nmb.b2(p0, p1, mi)
nb((21.5, -1.7, 0.3), (24.5, 1.7, 1.0), WALL); nb((21.5, -1.7, 2.4), (24.5, 1.7, 3.2), WALL); nb((21.44, -1.76, 0), (24.56, 1.76, 0.32), STONE)
nb((21.5, -1.7, 1.0), (24.5, 0.2, 2.4), WALL); nb((21.5, 1.4, 1.0), (24.5, 1.7, 2.4), WALL); nb((22.5, 0.2, 1.0), (24.5, 1.4, 2.4), WALL)
nb((21.5, 0.2, 0.95), (22.5, 1.4, 1.0), WOOD)
nb((21.43, -1.42, 0.3), (21.5, -0.5, 2.12), FRAME); nb((21.40, -1.32, 0.3), (21.47, -0.6, 2.0), DOOR); nb((20.9, -1.5, 0), (21.44, -0.4, 0.3), STONE)
nb((21.36, 0.05, 0.90), (21.5, 1.55, 1.0), FRAME); nb((21.42, 0.08, 2.4), (21.5, 1.52, 2.52), FRAME)
nb((21.42, 0.08, 1.0), (21.5, 0.2, 2.4), FRAME); nb((21.42, 1.4, 1.0), (21.5, 1.52, 2.4), FRAME)
nb((21.38, -0.28, 0.98), (21.46, 0.06, 2.52), SHUT); nb((21.38, 1.54, 0.98), (21.46, 1.88, 2.52), SHUT)
for cx_ in (-1.7, 1.7): nb((21.44, cx_ - 0.06, 0.3), (21.56, cx_ + 0.06, 3.2), FRAME)
nb((20.95, 0.1, 0), (21.35, 1.6, 0.5), HEDGE)
nmb.box((21.47, 1.2, 1.2), (0.03, 0.55, 0.10), WOOD, rx=-0.5)   # assi inchiodate agli angoli
nmb.build('Vicino', envc, (DX, 0, 0))
rmb = MB(set004.house_mats(M, 3, 0, 0)); set004.roof_geo(rmb, 3.4, 3.0, 3.2); rmb.build('VicinoTetto', envc, (23.0 + DX, 0, 0), math.pi / 2)
WIN = (21.5 + DX, 0.8, 1.7)
rl = bpy.data.lights.new('Stanza', 'POINT'); rl.energy = 30; rl.color = (1.0, 0.85, 0.6); rl.shadow_soft_size = 0.5
rlo = bpy.data.objects.new('Stanza', rl); rlo.location = (WIN[0] + 0.7, 0.8, 2.15); envc.objects.link(rlo)

# ======================= personaggi =======================
P = pippo.build_pippo(chc); Tb = tumbo.build_tumbo(chc, scale=0.75)
for r in (P['root'], Tb['root']): r.rotation_mode = 'XYZ'
for nm in 'LR': P['shoulder' + nm].rotation_mode = 'QUATERNION'
def qdir(d, rest=(0, 0, -1)): return Vector(rest).rotation_difference(Vector(d).normalized())
SH = 1.42

# ======================= oggetti di scena =======================
cloth_t = props005.tablecloth(prc, Q, None, (TABLE[0], TABLE[1], 0.79), a=0.75)
cloth1 = props005.tablecloth(prc, Q, P['root'], (0, 0, 1.92))
cloth2 = props005.tablecloth(prc, Q, None, (0, 0, -50))
sheetm = [Q['sheet'], Q['sheet2'], Q['rope'], Q['rope']]
L2, D2, R2, V2 = 2.6, 1.3, 1.9, 0.38
can2c = props005.round_canopy(prc, Q, 'Lenzuolo', sheetm, lambda g, i: g % 2, R=R2, D=D2, nseg=10, vent=V2, L=L2, parent=P['root'], loc=(0, 0, SH), parts='cloth')
can2l = props005.round_canopy(prc, Q, 'LenzuoloFuni', sheetm, lambda g, i: g % 2, R=R2, D=D2, nseg=10, vent=V2, L=L2, parent=P['root'], loc=(0, 0, SH), parts='lines')
PATCH_Z = L2 + D2 * math.cos(math.asin(V2 / R2))
patch = props005.vent_patch(prc, Q['sheet2'], V2, can2c, PATCH_Z)
L3 = 3.2
can3 = props005.round_canopy(prc, Q, 'Cupola', [Q['nyl'][0], Q['nyl'][1], Q['line'], Q['web']], lambda g, i: g % 2, R=2.5, D=1.7, nseg=14, vent=0.42, L=L3, parent=P['root'], loc=(0, 0, SH))
L4 = 3.3
wing, TG = props005.ram_air(prc, Q, parent=P['root'], loc=(0, 0, SH), L=L4)
for kb in wing.data.shape_keys.key_blocks: kb.slider_min = -0.5; kb.slider_max = 1.5
h2 = props005.harness(prc, Q, P['body'], pack=False)
h3 = props005.harness(prc, Q, P['body'], pack=True)
resv = obj('Riserva', set004.box_c(), (0, 0.36, 0.82), (0.36, 0.19, 0.17), Q['packr'], prc, parent=P['body'])
gogP = props005.goggles(prc, Q, P['head'], 0.125, -0.27, 0.50, r=0.10, tilt=-0.45, strap_r=(0.37, 0.33))
gogT = props005.goggles(prc, Q, Tb['head'], 0.105, -0.285, 0.075, r=0.105, strap_r=(0.30, 0.285))
band = props005.bandana(prc, Q, Tb['body'], (0, -0.40, -0.27), rot=(math.pi / 2 - 0.15, 0, 0), w=0.40, h=0.36)
pencil = cyl('Matita', 0.018, 0.34, (0, -0.36, -0.12), Q['toggle'], prc, rot=(0, math.pi / 2, 0), parent=Tb['head'])
# lavagnetta con il voto
CLIP = (-1.55, -1.25)
cb = MB([M['wood'], M['plate'], Q['packr'], M['dark']])
cb.box((0, 0, 0.36), (0.56, 0.04, 0.72), 0); cb.box((0, -0.025, 0.34), (0.48, 0.02, 0.60), 1); cb.box((0, -0.03, 0.68), (0.20, 0.04, 0.06), 3)
cb.box((0, -0.04, 0.20), (0.40, 0.02, 0.07), 2, rz=0.0);
clip = cb.build('Lavagnetta', prc, (CLIP[0], CLIP[1], 0), 0.25); clip.rotation_euler = (-0.28, 0, 0.25)
xa = obj('VotoX1', set004.box_c(), (0, -0.045, 0.24), (0.36, 0.02, 0.07), Q['packr'], prc, rot=(0, 0.785, 0), parent=clip)
xb = obj('VotoX2', set004.box_c(), (0, -0.045, 0.24), (0.36, 0.02, 0.07), Q['packr'], prc, rot=(0, -0.785, 0), parent=clip)
sk = props005.tablecloth(prc, Q, clip, (0, -0.04, 0.50), a=0.11); sk.rotation_euler = (math.pi / 2, 0, 0)
for kbn in ('flat',): sk.data.shape_keys.key_blocks[kbn].value = 1.0
# aereo
pl, prop = props005.plane(prc, Q); pl.scale = (1.6, 1.6, 1.6)
# vicino + pallone
man = props004.player(chc, 'Neigh', (0.96, 0.96, 0.96), (0.25, 0.25, 0.30), (0.96, 0.42, 0.36), (0.15, 0.10, 0.07), scale=1.0)
man['root'].rotation_euler = (0, 0, -math.pi / 2); man['root'].scale = (0.85, 0.85, 0.85)
mhead = [c for c in man['root'].children if c.name.startswith('Head')][0]
for sx in (-1, 1): obj('Brow', set004.box_c(), (sx * 0.10, -0.25, 0.15), (0.13, 0.03, 0.035), M['dark'], chc, rot=(0, sx * 0.45, 0), parent=mhead)
ball = ball_('Pallone', 0.20, (0.34, -0.62, 1.95), M['ball'], prc, parent=man['root'])

# ======================= visibilità =======================
def show(o, intervals):
    objs = [o] + list(desc(o)) if not isinstance(o, list) else o
    for q in objs:
        first = intervals[0][0] <= 0.0
        q.hide_render = not first; q.keyframe_insert('hide_render', frame=1)
        for (a, b) in intervals:
            if a > 0.0: q.hide_render = False; q.keyframe_insert('hide_render', frame=fr(a))
            if b < TOTAL: q.hide_render = True; q.keyframe_insert('hide_render', frame=fr(b))
def pop(o, t, d=0.32, s0=0.0001, over=1.22, s1=1.0):
    for (tt_, v) in ((t, s0), (t + 0.55 * d, over), (t + d, s1)):
        o.scale = (v, v, v); o.keyframe_insert('scale', frame=fr(tt_))
show(cloth_t, [(0, 3.05)]); show(cloth1, [(3.05, 5.75)]); show(cloth2, [(5.75, 8.55)])
show(can2c, [(9.8, 20.6)]); show(can2l, [(10.5, 20.6)]); show(patch, [(9.8, 17.7)]); show(h2, [(11.1, 20.6)])
show(can3, [(20.6, 26.15)]); show(h3, [(20.6, TOTAL)]); show(wing, [(26.15, 31.05), (38.12, TOTAL)])
show(resv, [(31.05, TOTAL)]); show(gogP, [(31.05, TOTAL)]); show(gogT, [(33.9, TOTAL)]); show(band, [(36.9, TOTAL)])
show(pencil, [(5.75, 8.55)]); show(clip, [(5.75, 8.55)])
show(man['root'], [(41.85, TOTAL)])
pop(can2c, 9.8); pop(can2l, 10.5); pop(h2, 11.1, s0=1.7, over=0.92); pop(gogT, 33.9, s0=2.2, over=0.9); pop(band, 36.9)
for (t_, v) in ((35.5, 1.0), (35.75, 1.35), (36.0, 1.0), (36.2, 1.3), (36.45, 1.0)):
    resv.scale = (0.36 * v, 0.19 * v, 0.17 * v); resv.keyframe_insert('scale', frame=fr(t_))

# ======================= traiettorie =======================
def BASE2(t): return (-3.0, 0.5, 13.0 - 0.75 * (t - 12.05))
LP2 = SH + L2
def amp2(t):
    if t < 13.15: return 0.0
    if t < 15.9: return 0.95 * ramp(t, 13.15, 13.7)
    if t < 18.0: return 0.95 - 0.35 * (t - 15.9) / 2.1
    return 0.6 * (1 - ramp(t, 18.0, 19.7))
def ang2(t): return amp2(t) * math.sin(2 * math.pi * (t - 13.15) / 1.15) + (0.05 * math.sin(3 * t) if t < 13.15 else 0)
def D3(t):
    u = (t - 20.6) / 2.6; return (-9.5 + 9.9 * u, 1.0 + 0.5 * u, 9.5 - 6.0 * u)
LP3 = SH + L3
def W3(t): return (-2.0, 12 - 5.0 * (t - 26.15), 16 - 1.2 * (t - 26.15))
LP4 = SH + L4
def PLpos(t):
    if t < 3.0: return (-22 + 30 * t, 36, 26)
    if t < 30.0: return (0, 400, 46)
    return (-3, 40 - 7 * (t - 31.05), 46)
DOOR_OFF = (1.95, 0.56, -1.18)
P0F = add(PLpos(37.55), DOOR_OFF)
def FREE(t): tau = t - 37.55; return (P0F[0] + 4 * tau, P0F[1] - 3.5 * tau, P0F[2] + 1.2 * tau - 7 * tau * tau)
P1F = FREE(38.1)
def OPEN(t): tau = t - 38.1; return (P1F[0] + 2.0 * tau, P1F[1] - 1.5 * tau, P1F[2] - 3.2 * tau + 0.9 * tau * tau)
LAND = (6.0, -3.2)
def hang(C, rot, Lp):
    v = Euler(rot, 'XYZ').to_matrix() @ Vector((0, 0, -Lp)); return (C[0] + v.x, C[1] + v.y, C[2] + v.z)
def brakes(t):
    """(sinistra s=-1, destra s=+1) 0..1"""
    if 27.9 <= t < 29.25: return (ramp(t, 28.05, 28.3) * (1 - ramp(t, 28.5, 28.7)), ramp(t, 28.7, 28.9) * (1 - ramp(t, 29.1, 29.25)))
    if 29.25 <= t < 31.05: b = ramp(t, 29.6, 30.2) * (1 - ramp(t, 30.45, 30.7)); return (b, b)
    if 39.15 <= t < 40.35: return (0.0, 0.75)
    if 40.35 <= t < 41.85: b = ramp(t, 40.6, 41.15) * (1 - ramp(t, 41.35, 41.6)); return (b, b)
    return (0.0, 0.0)
def wing_closed(t):
    if t < 26.2: return 1.0
    if t < 26.75: return 1 - eb((t - 26.2) / 0.55)
    if t < 30.45: return 0.0
    if t < 31.05: return 0.75 * ramp(t, 30.45, 31.0)
    if t < 38.15: return 1.0
    if t < 38.65: return 1 - eb((t - 38.15) / 0.5)
    if t < 45.3: return 0.0
    return ramp(t, 45.3, 45.85)
def armw(s, b): return lerp((s * 0.085, 0.16, 0.59), (s * 0.105, 0.10, -0.45), b)
DOWN = lambda s: (s * 0.14, 0, -1)
UPR = lambda s: (-s * 0.10, 0, 1)

def pp(t):
    """posa di Pippo al tempo t."""
    S = dict(loc=(0, 0, 0), rot=(0, 0, 0), aL=DOWN(-1), aR=DOWN(1), hL=0.0, hR=0.0, head=(0, 0, 0))
    if t < 1.45:                                   # vuole volare: sbatte le braccia
        a = 0.15 + 0.55 * math.sin(t * 13)
        S.update(loc=(-6.5, -1.0, 0.06 * abs(math.sin(t * 13))), aL=(-math.cos(a), 0, math.sin(a)), aR=(math.cos(a), 0, math.sin(a)), head=(-0.35, 0, 0))
    elif t < 3.65:                                 # al tavolo
        S.update(loc=(-6.7, -2.6, 0), rot=(0, 0, -1.15))
        if t < 2.55: S.update(aR=(0.25, -0.75, 0.65), head=(0.15, 0, 0.25 * math.sin(t * 4)))
        elif t < 3.05:
            u = ramp(t, 2.55, 2.8); v = ramp(t, 2.8, 3.05)
            d = lerp(lerp((0.1, -0.4, -0.9), (0.0, -1, -0.15), u), (0.18, 0, 1), v); S.update(aR=d, aL=lerp(DOWN(-1), (-0.18, 0, 1), v), head=(0.2 - 0.4 * v, 0, 0))
        else: S.update(aL=(-0.18, 0, 1), aR=(0.18, 0, 1), head=(-0.2, 0, 0), loc=(-6.7, -2.6, 0.10 * abs(math.sin((t - 3.05) * 10))))
    elif t < 4.45:                                 # sul tetto
        cr = ramp(t, 4.15, 4.4)
        S.update(loc=(HOUSE[0], HOUSE[1], RIDGE_Z - 0.18 * cr), aL=(-0.18, 0, 1), aR=(0.18, 0, 1), head=(-0.15 + 0.3 * cr, 0, 0))
    elif t < 5.75:                                 # salto e caduta a sacco di patate
        tau = t - 4.45; z = RIDGE_Z + 4.0 * tau - 0.5 * 12.84 * tau * tau
        px = 1.5708 * ramp(tau, 0.45, 1.25)
        S.update(loc=(HOUSE[0], HOUSE[1] - 2.9 * tau, max(z, 0.28)), rot=(px, 0, 0), aL=(-0.18, 0, 1), aR=(0.18, 0, 1),
                 hL=0.5 * math.sin(tau * 22), hR=-0.5 * math.sin(tau * 22))
    elif t < 8.55:                                 # steso a terra
        tau = t - 5.75; bz = 0.22 * math.exp(-tau * 7) * abs(math.cos(tau * 16))
        S.update(loc=(HOUSE[0], HOUSE[1] - 2.9 * 1.3, 0.28 + bz), rot=(1.5708, 0, 0), aL=(-1, 0, 0.25), aR=(1, 0, 0.25))
        if t > 7.5: u = ramp(t, 7.5, 7.8) * (1 - ramp(t, 8.3, 8.5)); S.update(aR=lerp((1, 0, 0.25), (0.25 + 0.12 * math.sin(t * 9), 1, 0.1), u))
    elif t < 12.05:                                # di nuovo sul tetto: si costruisce il paracadute
        S.update(loc=(HOUSE[0], HOUSE[1], RIDGE_Z))
        if t < 9.75: S.update(aL=(-0.75, -0.25, -0.6), aR=(0.75, -0.25, -0.6), head=(0, 0, 0.32 * math.sin((t - 8.6) * 9) * (1 - ramp(t, 9.3, 9.6))))
        elif t < 10.55: S.update(aL=(-0.75, -0.25, -0.6), aR=(0.75, -0.25, -0.6), head=(-0.45 * ramp(t, 9.8, 10.0), 0, 0))
        else:
            u = ramp(t, 10.55, 10.85); S.update(aL=lerp((-0.75, -0.25, -0.6), UPR(-1), u), aR=lerp((0.75, -0.25, -0.6), UPR(1), u))
            S.update(head=(-0.45 * (1 - ramp(t, 11.05, 11.25)) + 0.3 * ramp(t, 11.15, 11.4) * (1 - ramp(t, 11.65, 11.85)), 0, 0))
            S['loc'] = (HOUSE[0], HOUSE[1], RIDGE_Z - 0.16 * ramp(t, 11.75, 12.0))
    elif t < 20.6:                                 # lenzuolo: frena, dondola, foro in cima
        a = ang2(t); B = BASE2(t); C = (B[0], B[1], B[2] + LP2)
        S.update(loc=hang(C, (0, a, 0), LP2), rot=(0, a, 0), aL=UPR(-1), aR=UPR(1), hL=0.25 - 0.6 * a, hR=-0.2 - 0.6 * a, head=(0, -0.5 * a, 0))
    elif t < 23.2:                                 # cupola: va dove decide il vento
        a = -0.30 + 0.07 * math.sin(t * 6); B = D3(t); C = (B[0], B[1], B[2] + LP3)
        S.update(loc=hang(C, (0, a, 0), LP3), rot=(0, a, 0), aL=(0.25 + 0.3 * math.sin(t * 9), 0, 1), aR=(0.5 + 0.3 * math.sin(t * 9 + 1), 0, 1),
                 hL=0.7 * math.sin(t * 10), hR=-0.7 * math.sin(t * 10), head=(0, 0.2, 0.35))
    elif t < 26.15:                                # appeso all'albero
        tau = t - 23.2; a = 0.5 * math.exp(-1.6 * tau) * math.cos(2 * math.pi * tau / 0.9); dz = 1.6 * (1 - ramp(tau, 0, 0.22))
        C = (1.1, 1.25, 3.55 + dz)
        S.update(loc=hang(C, (0, a, 0), 3.0), rot=(0, a, 0), aL=UPR(-1), aR=UPR(1), hL=0.2 - 0.5 * a, hR=-0.15 - 0.5 * a)
        if t > 24.9:
            u = ramp(t, 24.9, 25.2); S.update(aL=lerp(UPR(-1), (-0.2, -0.5, -0.8), u), aR=lerp(UPR(1), (0.2, -0.5, -0.8), u), head=(0.1, 0, 0.3 * math.sin((t - 25.0) * 10)))
    elif t < 29.25:                                # ala: celle, comandi
        bl, br = brakes(t); roll = -0.34 * bl + 0.34 * br; B = W3(t); C = (B[0], B[1], B[2] + LP4)
        S.update(loc=hang(C, (0, roll, 0), LP4), rot=(0, roll, 0), aL=armw(-1, bl), aR=armw(1, br), hL=0.2, hR=-0.1, head=(0, 0, -0.3 * bl + 0.3 * br))
    elif t < 31.05:                                # frenata e atterraggio morbido
        bl, br = brakes(t); u = min(1.0, (t - 29.25) / 1.05)
        y = 3.0 - 5.6 * (u - 0.25 * u * u) / 0.75; z = 2.6 * (1 - u) ** 1.6; pitch = -0.24 * bl
        if t < 30.3:
            C = (-2.0, y, z + LP4); S.update(loc=hang(C, (pitch, 0, 0), LP4), rot=(pitch, 0, 0), hL=0.35, hR=-0.1)
        else:
            w_ = ramp(t, 30.3, 30.75); st = math.sin((t - 30.3) * 16) * (1 - w_)
            S.update(loc=(-2.0, -2.6 - 0.8 * w_, 0), hL=0.5 * st, hR=-0.5 * st)
        rel = ramp(t, 30.5, 30.85)
        S.update(aL=lerp(armw(-1, bl), (-0.9, -0.2, 0.75), rel), aR=lerp(armw(1, br), (0.9, -0.2, 0.75), rel))
    elif t < 37.55:                                # sull'aereo
        yaw = math.pi / 2 + math.pi * ramp(t, 35.4, 35.75) - math.pi * ramp(t, 36.5, 36.85); cr = ramp(t, 37.25, 37.5)
        lo = add(PLpos(t), DOOR_OFF)
        S.update(loc=(lo[0], lo[1], lo[2] - 0.14 * cr), rot=(0.22 * cr, 0, yaw), aL=(-0.5, 0.1, -0.85), aR=(0.5, 0.1, -0.85))
        if t < 32.9: S.update(aR=(0.75, -0.2, 0.75 + 0.2 * math.sin(t * 12)))
        elif t < 35.4: S.update(head=(0.38 * ramp(t, 33.0, 33.3), 0, 0))
        elif t < 36.6: S.update(aR=lerp((0.5, 0.1, -0.85), (0.35, 0.55, 0.75), ramp(t, 35.6, 35.85) * (1 - ramp(t, 36.4, 36.6))))
        else: S.update(head=(0.38 * ramp(t, 36.85, 37.0) * (1 - cr), 0, 0))
    elif t < 38.1:                                 # lancio
        tau = t - 37.55
        S.update(loc=FREE(t), rot=(1.25 * ramp(tau, 0.05, 0.4), 0, math.pi / 2), aL=(-1, -0.3, 0.3), aR=(1, -0.3, 0.3), hL=-0.35, hR=-0.5)
    elif t < 39.15:                                # apertura
        tau = t - 38.1; pitch = 1.25 * (1 - ramp(tau, 0.0, 0.28)) + 0.25 * math.exp(-3 * tau) * math.sin(9 * tau)
        u = ramp(tau, 0.1, 0.5)
        S.update(loc=OPEN(t), rot=(pitch, 0, math.pi / 2 * (1 - ramp(tau, 0.35, 0.95))), aL=lerp((-1, -0.3, 0.3), armw(-1, 0), u), aR=lerp((1, -0.3, 0.3), armw(1, 0), u),
                 hL=0.3 * math.sin(tau * 8), hR=-0.3 * math.sin(tau * 8))
    elif t < 40.35:                                # virata
        u = (t - 39.15) / 1.2; th = 2.4 + 5.0 * u; r = 6.5 - 2.5 * u; yaw = math.atan2(-math.sin(th), -math.cos(th))
        C = (5.5 + r * math.cos(th), -1.5 + r * math.sin(th), 20 - 9 * u + LP4); rot = (0, 0.45, yaw)
        S.update(loc=hang(C, rot, LP4), rot=rot, aL=armw(-1, 0), aR=armw(1, 0.75), hL=0.2, hR=-0.1)
    elif t < 41.85:                                # atterraggio perfetto
        bl, br = brakes(t); u = min(1.0, (t - 40.35) / 0.85)
        y = LAND[1] + 5.6 - 5.6 * (u - 0.25 * u * u) / 0.75; z = 2.4 * (1 - u) ** 1.6; pitch = -0.22 * bl
        if u < 1.0:
            C = (LAND[0], y, z + LP4); S.update(loc=hang(C, (pitch, 0, 0), LP4), rot=(pitch, 0, 0), hL=0.35, hR=-0.1)
        else:
            S.update(loc=(LAND[0], LAND[1], -0.07 * math.exp(-(t - 41.2) * 8) * math.cos((t - 41.2) * 14)))
        rel = ramp(t, 41.35, 41.65)
        S.update(aL=lerp(armw(-1, bl), (-0.75, -0.25, -0.6), rel), aR=lerp(armw(1, br), (0.75, -0.25, -0.6), rel))
    else:                                          # nel giardino del vicino
        yaw = 2.68 * ramp(t, 42.2, 42.9)
        S.update(loc=(LAND[0], LAND[1], 0), rot=(0, 0, yaw), aL=(-0.75, -0.25, -0.6), aR=(0.75, -0.25, -0.6))
        if t > 42.9: S.update(aL=DOWN(-1), aR=DOWN(1))
        if t > 44.95: S.update(aR=(0.6 + 0.22 * math.sin(t * 14), -0.25, 0.8))
    return S

TAND = Matrix.Translation((0, -0.80, 0.90)) @ Euler((-math.pi / 2, 0, 0), 'XYZ').to_matrix().to_4x4()
def walk(t, sp=14.0, am=0.55):
    s = math.sin(t * sp) * am; return dict(FL=s, FR=-s, BL=-s, BR=s)
def tp(t):
    """posa di Tumbo al tempo t."""
    S = dict(loc=(0, 0, 0), rot=(0, 0, 0), legs=dict(FL=0, FR=0, BL=0, BR=0), head=(0, 0, 0), tail=-1.0 + 0.5 * math.sin(t * 12))
    if t >= 31.05:                                 # in tandem
        s = pp(t); m = Matrix.Translation(s['loc']) @ Euler(s['rot'], 'XYZ').to_matrix().to_4x4() @ TAND
        j = 0.03 * math.sin(t * 55) if 34.6 <= t < 35.5 else 0.0
        l = m.to_translation(); e = m.to_euler('XYZ')
        k = 0.35 * math.sin(t * 9)
        S.update(loc=(l.x + j, l.y, l.z + j * 0.5), rot=(e.x, e.y, e.z), legs=dict(FL=0.55 + k, FR=0.55 - k, BL=-0.45 - k, BR=-0.45 + k), head=(1.15, 0, 0.15 * math.sin(t * 3)))
        return S
    if t < 1.45: S.update(loc=(-5.35, -0.75, 0), rot=(0, 0, 0.5), head=(-0.3, 0.25 * math.sin(t * 6), 0.5))
    elif t < 3.65:
        hop = 0.35 * math.sin(math.pi * min(1.0, max(0.0, (t - 2.85) / 0.4))) if t > 2.85 else 0
        S.update(loc=(-8.7, -4.0, hop), rot=(0, 0, 2.6), head=(-0.45, 0, 0.0))
    elif t < 5.75: S.update(loc=(-2.4, -1.4, 0), rot=(0, 0, -2.8), head=(-0.6, 0, 0))
    elif t < 8.55: S.update(loc=(-2.45, -1.35, 0), rot=(0, 0, 0.55), head=(0.25 + 0.12 * math.sin(t * 17), 0, 0.3 + 0.12 * math.cos(t * 17)), tail=-1.0)
    elif t < 23.35: S.update(loc=(-1.5, -1.6, 0), rot=(0, 0, 0.3), head=(-0.55, 0.3 * math.sin(2 * math.pi * (t - 13.15) / 1.15) if 13.15 < t < 19.5 else 0, 0))
    elif t < 26.15:
        u = ramp(t, 23.5, 24.4); x = -2.2 + 2.9 * u; y = -1.6 + 1.1 * u
        S.update(loc=(x, y, 0), rot=(0, 0, math.atan2(2.9, -1.1) * (1 - ramp(t, 24.4, 24.7)) + 0.35 * ramp(t, 24.4, 24.7)), head=(-0.6 * ramp(t, 24.3, 24.6), 0, 0))
        if 23.5 < t < 24.4: S['legs'] = walk(t)
    else:
        u = ramp(t, 30.5, 31.0); hop = 0.25 * abs(math.sin((t - 30.5) * 12)) if t > 30.5 else 0
        S.update(loc=(0.6 - 1.5 * u, -4.2 + 0.7 * u, hop), rot=(0, 0, -1.2), head=(-0.5 * (1 - u), 0, 0))
        if 30.5 < t < 31.0: S['legs'] = walk(t, 22)
    return S

# ======================= chiavi dei personaggi =======================
TR = Tb['root']
for f in range(1, NF + 1):
    t = (f - 1) / FPS
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
    # aereo
    pl.location = PLpos(t); pl.rotation_euler = (0, 0, math.pi / 2 if t < 3.0 else 0); pl.keyframe_insert('location', frame=f); pl.keyframe_insert('rotation_euler', frame=f)
    prop.rotation_euler = (0, t * 37.0, 0); prop.keyframe_insert('rotation_euler', frame=f)
    # chiavi di forma
    def sk_(o, name, v): kb = o.data.shape_keys.key_blocks[name]; kb.value = v; kb.keyframe_insert('value', frame=f)
    sk_(cloth1, 'inv', ramp(t, 4.8, 5.1))
    sk_(wing, 'closed', wing_closed(t)); bl, br = brakes(t); sk_(wing, 'brakeL', bl); sk_(wing, 'brakeR', br)
    sk_(can3, 'closed', 0.0 if t < 23.2 else 0.32)
    # tovaglia sul tavolo: lo strappo
    u = ramp(t, 2.8, 3.05); sk_(cloth_t, 'flat', 1 - 0.7 * u)
    cloth_t.location = lerp((TABLE[0], TABLE[1], 0.79), (-6.85, -2.7, 1.9), u); cloth_t.scale = (1 - 0.45 * u,) * 3
    cloth_t.keyframe_insert('location', frame=f); cloth_t.keyframe_insert('scale', frame=f)
    for i, d in enumerate(dishes):
        tau = t - 2.82 - 0.02 * i; base = d.get('z0', None)
        if base is None: d['z0'] = d.location.z; base = d.location.z
        hop = 0.10 * math.exp(-tau * 5) * abs(math.sin(tau * 14)) if tau > 0 else 0
        d.location.z = base - (0.012 if tau > 0 else 0) + hop; d.rotation_euler = (d.rotation_euler.x, 0.25 * math.exp(-tau * 4) * math.sin(tau * 20) if tau > 0 else 0, 0)
        d.keyframe_insert('location', frame=f); d.keyframe_insert('rotation_euler', frame=f)
    # tovaglia che plana su Pippo
    tau = t - 5.8; u = ramp(t, 5.8, 6.9)
    sk_(cloth2, 'flat', 0.35 + 0.25 * u)
    cloth2.location = (HOUSE[0] + 0.7 * math.sin(tau * 5) * (1 - u), -0.15, 3.0 - 2.5 * u) if t >= 5.75 else (0, 0, -50)
    cloth2.rotation_euler = (0, 0.35 * math.sin(tau * 5) * (1 - u), 0.4); cloth2.keyframe_insert('location', frame=f); cloth2.keyframe_insert('rotation_euler', frame=f)
    # toppa del foro
    tau = t - 17.0
    patch.location = (0.9 * tau, -0.6 * tau, PATCH_Z + 4.5 * tau - 5 * tau * tau) if tau > 0 else (0, 0, PATCH_Z)
    patch.rotation_euler = (5 * tau, 7 * tau, 0) if tau > 0 else (0, 0, 0); patch.keyframe_insert('location', frame=f); patch.keyframe_insert('rotation_euler', frame=f)
    # ala che si affloscia sul finale
    wing.location = (0, 0, SH - 2.6 * ramp(t, 45.35, 45.9)); wing.keyframe_insert('location', frame=f)
    # vicino: spunta dalla finestra e palleggia minaccioso
    mz = -0.9 + 1.18 * ramp(t, 42.3, 42.75)
    man['root'].location = (WIN[0] + 0.28, 0.8, mz); man['root'].keyframe_insert('location', frame=f)
    man['shoulderL'].rotation_euler = (-1.25, 0, 0.25); man['shoulderR'].rotation_euler = (-1.6, 0, 0)
    for nm in 'LR': man['shoulder' + nm].keyframe_insert('rotation_euler', frame=f)
    ball.location = (0.34, -0.66, 1.72 + 0.40 * abs(math.sin(t * 5.0))); ball.rotation_euler = (t * 3, 0, 0)
    ball.keyframe_insert('location', frame=f); ball.keyframe_insert('rotation_euler', frame=f)

# espressioni
_lastP = [None, -1.0]; _lastT = [None, -1.0]
def pex(t, **k):
    if _lastP[0] is not None and t - 0.06 > _lastP[1]: pippo.express(P, fr(t - 0.06), **_lastP[0])
    pippo.express(P, fr(t), **k); _lastP[0] = k; _lastP[1] = t
def tex(t, **k):
    if _lastT[0] is not None and t - 0.06 > _lastT[1]: tumbo.tumbo_express(Tb, fr(t - 0.06), **_lastT[0])
    tumbo.tumbo_express(Tb, fr(t), **k); _lastT[0] = k; _lastT[1] = t
pex(0.0, smile=0.7, brow_lift=0.5, look=(0, 0.6), eye_open=1.1)
pex(1.5, brow=0.3, smile=0.2, look=(-0.5, -0.3)); pex(2.6, smile=0.9, brow=0.6); pex(3.7, smile=0.9, brow=0.7)
pex(4.5, smile=0.7, mouth_open=0.6, brow=0.5); pex(4.95, brow=-0.8, brow_lift=0.7, eye_scale=1.25, mouth_open=1.0)
pex(5.75, eye_open=0.08, mouth_open=0.2); pex(8.6, brow=0.9, eye_open=0.8); pex(9.9, brow_lift=0.6, look=(0, 0.7), mouth_open=0.4)
pex(11.2, smile=1.0, brow=0.4); pex(12.1, smile=0.9, eye_open=1.1); pex(13.3, brow=-0.7, brow_lift=0.6, eye_scale=1.22, mouth_open=0.9)
pex(16.0, brow=-0.6, brow_lift=0.5, eye_scale=1.15, mouth_open=0.5); pex(18.4, smile=0.6, brow_lift=0.3); pex(19.5, smile=1.0)
pex(20.7, brow=-0.5, brow_lift=0.4, look=(0.8, 0), mouth_open=0.5, eye_scale=1.1); pex(23.2, eye_open=0.08, mouth_open=0.8)
pex(23.9, brow=1.0, eye_open=0.7); pex(25.0, brow=1.0, eye_open=0.65, look=(0, -0.4))
pex(26.2, smile=0.9, brow=0.6, eye_scale=1.1, mouth_open=0.3); pex(28.0, smile=0.5, brow=0.8); pex(29.3, smile=0.8, brow=0.4); pex(30.4, smile=1.0, eye_open=0.85)
pex(31.1, smile=0.8, brow=0.5); pex(33.0, smile=0.9, look=(0, -0.6)); pex(34.6, smile=0.3, look=(0, -0.6), brow_lift=0.4); pex(35.5, smile=1.0, brow=0.7)
pex(36.9, smile=0.8, look=(0, -0.5)); pex(37.5, mouth_open=0.8, brow_lift=0.5, eye_scale=1.1); pex(38.2, mouth_open=1.0, eye_scale=1.2, brow_lift=0.6)
pex(38.7, smile=1.0, mouth_open=0.4); pex(39.2, smile=1.0, brow=0.6); pex(40.4, smile=0.9, brow=0.4); pex(41.3, smile=1.0, eye_open=0.35)
pex(42.3, eye_open=1.2, eye_scale=1.15, brow=-0.6, brow_lift=0.6, mouth_open=0.3); pex(45.0, smile=0.9, brow=-0.7, brow_lift=0.5)
tex(0.0, tongue=0.6); tex(1.5, tongue=0.9, look=(0.5, 0.2)); tex(2.9, eye_scale=1.3, brow=-0.6); tex(5.75, eye_scale=1.25)
tex(7.1, brow=0.7, eye_open=0.8); tex(8.6, tongue=0.5); tex(23.4, tongue=0.8, look=(0, 0.6)); tex(31.05, tongue=0.7)
tex(33.9, eye_scale=1.15, tongue=0.9); tex(34.6, eye_scale=1.45, brow=-0.8); tex(36.9, tongue=0.6, eye_scale=1.1); tex(37.55, eye_scale=1.5, brow=-0.8)
tex(38.6, tongue=1.0, eye_scale=1.1); tex(42.3, eye_scale=1.3, brow=-0.5); tex(45.0, tongue=0.5)

# ======================= effetti =======================
def streak(name, sc, mat, parent, t0, t1, fn):
    o = obj(name, shared_mesh('sphere_lo'), (0, 0, -80), sc, mat, prc, parent=parent)
    o.hide_render = True; o.keyframe_insert('hide_render', frame=1); o.hide_render = False; o.keyframe_insert('hide_render', frame=fr(t0)); o.hide_render = True; o.keyframe_insert('hide_render', frame=fr(t1))
    for f in range(fr(t0), fr(t1) + 1):
        r_ = fn((f - 1) / FPS)
        o.location = r_[0]; o.keyframe_insert('location', frame=f)
        if len(r_) > 1: o.scale = r_[1]; o.keyframe_insert('scale', frame=f)
    return o
er = np.random.default_rng(3)
for k in range(7):                                  # polvere all'impatto
    an = k / 7 * 6.283; c0 = (HOUSE[0], -0.4, 0.12)
    streak('Polvere', (0.1, 0.1, 0.1), M['dust'], None, 5.75, 6.5,
           lambda t, an=an: ((c0[0] + (0.3 + 1.6 * (t - 5.75)) * math.cos(an), c0[1] + (0.3 + 1.3 * (t - 5.75)) * math.sin(an) * 0.7, 0.15 + 0.5 * (t - 5.75)),
                             (max(0.001, 0.17 * math.sin(math.pi * min(1, (t - 5.75) / 0.75))),) * 3))
for k in range(7):                                  # aria che sfoga dal foro
    ph = k / 7; ox, oy = er.uniform(-0.2, 0.2, 2)
    streak('Aria', (0.045, 0.045, 0.4), M['cloudw'], can2c, 17.3, 20.6,
           lambda t, ph=ph, ox=ox, oy=oy: ((ox, oy, 1.6 + 4.6 * ((t * 1.5 + ph) % 1.0)),))
for k in range(12):                                 # vento
    ph = er.uniform(0, 8); dy = er.uniform(-2.0, 0.3); dz = er.uniform(-0.5, 6.0)
    streak('Vento', (0.7, 0.025, 0.025), M['cloudw'], None, 20.6, 23.2,
           lambda t, ph=ph, dy=dy, dz=dz: ((D3(t)[0] - 5 + ((t * 11 + ph) % 10), D3(t)[1] + dy, D3(t)[2] + dz),))
for k in range(12):                                 # foglie
    v = np.array([er.uniform(-3, 3), er.uniform(-3.5, -0.5), er.uniform(1, 5)])
    streak('Foglia', (0.16, 0.16, 0.05), M['leaf'][k % 3], None, 23.2, 24.6,
           lambda t, v=v: ((1.0 + v[0] * (t - 23.2), 1.5 + v[1] * (t - 23.2), max(0.05, 4.0 + v[2] * (t - 23.2) - 4.9 * (t - 23.2) ** 2)),))
for k in range(9):                                  # aria che entra nelle celle
    ph = k / 9; x = (k - 4) * 0.55
    streak('AriaCella', (0.05, 0.5, 0.05), M['cloudw'], wing, 26.6, 28.0,
           lambda t, ph=ph, x=x: ((x, -3.6 + 2.7 * ((t * 1.8 + ph) % 1.0), L4 - 0.1 - 0.06 * abs(x)),))

# ======================= camera =======================
def PW(t): return pp(t)['loc']
def PCH(t):
    s = pp(t); v = Euler(s['rot'], 'XYZ').to_matrix() @ Vector((0, 0, 1.25)); return (s['loc'][0] + v.x, s['loc'][1] + v.y, s['loc'][2] + v.z)
def Z0(t): return (0, 0, 0)
JP = PLpos(37.55)
SHOTS = [  # t0, t1, sub cam, p0, p1, sub mira, a0, a1, lente, f
    (0.0, 1.45, Z0, (-5.4, -4.6, 0.9), (-5.7, -4.2, 1.0), Z0, (-6.3, -1.0, 1.35), (-6.3, -1.0, 1.45), 30, 2.8),
    (1.45, 3.65, Z0, (-7.3, -7.9, 1.8), (-7.5, -7.3, 1.65), Z0, (-7.6, -2.5, 1.0), (-7.5, -2.5, 1.1), 30, 5.0),
    (3.65, 5.0, Z0, (-1.0, -5.5, 3.0), (-1.2, -5.2, 3.0), PW, (0, 0, 1.4), (0, 0, 1.2), 52, 8),
    (5.0, 5.75, Z0, (0.6, -3.2, 1.7), (0.4, -3.2, 1.2), PW, (0, -0.4, 0.9), (0, -0.6, 0.4), 30, 8),
    (5.75, 7.05, Z0, (-2.5, -3.5, 0.6), (-2.9, -3.1, 0.5), Z0, (-4.5, -0.4, 0.5), (-4.5, -0.4, 0.4), 35, 4),
    (7.05, 8.55, Z0, (-1.5, -3.5, 0.6), (-1.7, -3.2, 0.52), Z0, (-2.0, -1.3, 0.42), (-2.0, -1.3, 0.42), 40, 2.8),
    (8.55, 12.05, Z0, (-2.6, -1.0, 6.4), (-3.0, -0.6, 6.6), Z0, (-4.5, 4.5, 8.3), (-4.5, 4.5, 8.6), 28, 8),
    (12.05, 13.15, Z0, (-0.5, -12.5, 9.0), (-0.8, -12.0, 9.0), PW, (0, 0, 3.0), (0, 0, 3.0), 50, 8),
    (13.15, 14.5, Z0, (-3.0, -14.5, 10.0), (-3.0, -14.0, 9.5), BASE2, (0, 0, 2.4), (0, 0, 2.4), 42, 8),
    (14.5, 15.9, PCH, (0.7, -3.1, 0.25), (0.5, -2.8, 0.25), PCH, (0, 0, 0.42), (0, 0, 0.42), 35, 4),
    (15.9, 17.95, BASE2, (0.5, -2.2, 9.4), (0.3, -1.5, 8.4), BASE2, (0, 0, 4.9), (0, 0, 5.0), 30, 8),
    (17.95, 20.6, Z0, (1.6, -12.5, 7.0), (0.8, -11.0, 7.0), BASE2, (0, 0, 2.8), (0, 0, 2.8), 48, 8),
    (20.6, 23.2, Z0, (-4.0, -14.5, 5.0), (-3.0, -13.5, 4.5), PW, (0.6, 0, 2.4), (0.6, 0, 2.4), 45, 8),
    (23.2, 25.0, Z0, (2.4, -7.8, 1.4), (2.0, -7.0, 1.5), Z0, (1.0, 1.8, 3.1), (1.0, 1.8, 2.9), 26, 8),
    (25.0, 26.15, Z0, (1.9, -2.4, 2.1), (1.7, -2.0, 2.15), PW, (0, 0, 1.45), (0, 0, 1.45), 40, 2.8),
    (26.15, 26.9, PW, (2.6, -7.2, -1.0), (2.2, -6.6, -0.6), PW, (0, 0, 3.0), (0, 0, 3.1), 28, 8),
    (26.9, 27.95, PW, (1.8, -5.2, 5.7), (1.0, -4.4, 5.5), PW, (0, -0.5, 4.6), (0, -0.5, 4.6), 35, 8),
    (27.95, 29.25, PW, (1.0, -3.6, 1.9), (0.6, -3.1, 2.0), PW, (0, 0, 1.78), (0, 0, 1.78), 38, 4),
    (29.25, 31.05, Z0, (1.9, -6.2, 0.7), (1.3, -6.4, 0.9), PW, (0, 0, 2.3), (0, 0, 1.9), 24, 8),
    (31.05, 32.95, PLpos, (11, -14, -3.5), (8.5, -9.5, -2.5), PLpos, (0.6, 0, 0), (0.9, 0, -0.2), 35, 8),
    (32.95, 34.6, PLpos, (6.6, -0.9, -0.1), (5.6, -0.4, -0.2), PLpos, (2.3, 0.56, -0.15), (2.4, 0.56, -0.2), 40, 4),
    (34.6, 35.45, PLpos, (4.5, 0.15, 0.15), (4.3, 0.2, 0.15), PLpos, (2.35, 0.56, 0.02), (2.35, 0.56, 0.02), 50, 4),
    (35.45, 36.85, PLpos, (5.4, -0.7, 0.0), (4.9, -0.3, 0.0), PLpos, (2.0, 0.56, -0.05), (2.0, 0.56, -0.05), 42, 4),
    (36.85, 37.55, PLpos, (4.5, 1.1, -0.05), (4.3, 1.0, -0.05), PLpos, (2.4, 0.56, -0.12), (2.4, 0.56, -0.12), 50, 4),
    (37.55, 38.1, Z0, add(JP, (10, -9, -4.5)), add(JP, (10, -9, -4.5)), PW, (0, 0, 0.8), (0, 0, 0.8), 30, 8),
    (38.1, 39.15, PW, (3.0, -6.2, -2.6), (2.4, -5.6, -1.6), PW, (0, 0, 2.9), (0, 0, 3.0), 28, 8),
    (39.15, 40.35, PW, (0.5, -2.0, 13.5), (0.5, -2.0, 11.5), PW, (0, 0, 2.5), (0, 0, 2.5), 28, 8),
    (40.35, 41.85, Z0, (7.7, -6.1, 0.55), (7.4, -5.8, 0.7), PW, (0, 0, 1.15), (0, 0, 1.15), 35, 4),
    (41.85, 43.45, Z0, (2.2, -5.6, 2.1), (2.6, -5.2, 2.0), Z0, (7.0, -1.1, 1.6), (7.0, -1.0, 1.6), 26, 8),
    (43.45, 44.95, Z0, (5.4, 0.2, 1.5), (5.9, 0.45, 1.6), Z0, (8.2, 0.8, 1.85), (8.2, 0.8, 1.9), 50, 8),
    (44.95, 46.1, Z0, (7.5, -1.2, 1.35), (7.4, -1.3, 1.4), Z0, (6.0, -3.2, 1.3), (6.0, -3.2, 1.3), 35, 5),
]
camd = bpy.data.cameras.new('Cam'); cam = bpy.data.objects.new('Cam', camd); cac.objects.link(cam); scene.camera = cam
camd.clip_start = 0.1; camd.clip_end = 700; camd.sensor_width = 36
tgt = empty('CamTarget', (0, 0, 1), None, cac)
c = cam.constraints.new('TRACK_TO'); c.target = tgt; c.track_axis = 'TRACK_NEGATIVE_Z'; c.up_axis = 'UP_Y'
camd.dof.use_dof = True; camd.dof.focus_object = tgt
for f in range(1, NF + 1):
    t = (f - 1) / FPS
    s_ = next((s for s in SHOTS if s[0] <= t < s[1]), SHOTS[-1]); u = (t - s_[0]) / (s_[1] - s_[0])
    cam.location = add(s_[2](t), lerp(s_[3], s_[4], u)); tgt.location = add(s_[5](t), lerp(s_[6], s_[7], u))
    camd.lens = s_[8]; camd.dof.aperture_fstop = s_[9]
    cam.keyframe_insert('location', frame=f); tgt.keyframe_insert('location', frame=f); camd.keyframe_insert('lens', frame=f); camd.dof.keyframe_insert('aperture_fstop', frame=f)

# interpolazione: lineare ovunque (pose campionate a ogni fotogramma), costante per la visibilita'
def lin(idb):
    for fc in all_fcurves(idb):
        kind = 'CONSTANT' if 'hide' in fc.data_path else 'LINEAR'
        for kp in fc.keyframe_points: kp.interpolation = kind
for o in bpy.data.objects:
    lin(o)
    if o.type == 'MESH' and o.data.shape_keys: lin(o.data.shape_keys)
set_interp(camd, 'CONSTANT')
os.makedirs('../t005', exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath('../t005/pippo_t005.blend')); print('SAVED')
