"""Test 015 - IL PARTO DI ELEONORA. Salva ../t015/pippo_t015.blend
Personaggi: Pippo e Tumbo ESISTENTI (pippo.py, tumbo.py) invariati; Gualtiero = nuovo vicino ricorrente (props009.gualtiero)."""
import sys, math, os
sys.path.insert(0, os.path.dirname(__file__))
import bpy, numpy as np
from mathutils import Vector, Euler, Matrix
from common import *
from render_setup import *
import set004, props004, props007, props009, props010, props012, props013, props015, lookdev, pippo, tumbo
from set004 import obj, bx, cyl, ball_, MB

FPS = 24; TOTAL = 65.8; NF = int(TOTAL * FPS)
def fr(t): return max(1, int(round(t * FPS)) + 1)
def sm(x): x = min(1.0, max(0.0, x)); return x * x * (3 - 2 * x)
def ramp(t, a, b): return sm((t - a) / (b - a))
def lerp(a, b, u): return tuple(a[i] + (b[i] - a[i]) * u for i in range(len(a)))
def add(a, b): return tuple(a[i] + b[i] for i in range(3))
PI = math.pi

reset_scene(); scene = bpy.context.scene
setup_render(scene, 1080, 1920, samples=16, fps=FPS, frames=NF); scene.frame_end = NF
scene.eevee.shadow_resolution_scale = 0.25
rng = np.random.default_rng(41)
M = set004.make_mats(); N = props007.mats007(); G9 = props009.mats009()
envc = collection('Env'); chc = collection('Characters'); prc = collection('Props'); cac = collection('Cameras')

# ======================= mondo =======================
w = bpy.data.worlds.new('World'); scene.world = w; w.use_nodes = True; nt = w.node_tree; nt.nodes.clear()
tc = nt.nodes.new('ShaderNodeTexCoord'); sp = nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(tc.outputs['Generated'], sp.inputs[0])
rp = nt.nodes.new('ShaderNodeValToRGB'); nt.links.new(sp.outputs['Z'], rp.inputs['Fac'])
rp.color_ramp.elements[0].position = 0.0; rp.color_ramp.elements[0].color = (0.46, 0.80, 1.0, 1)
rp.color_ramp.elements[1].position = 0.75; rp.color_ramp.elements[1].color = (0.04, 0.34, 1.0, 1)
bg = nt.nodes.new('ShaderNodeBackground'); bg.inputs['Strength'].default_value = 0.7; nt.links.new(rp.outputs['Color'], bg.inputs['Color'])
bgc = nt.nodes.new('ShaderNodeBackground'); bgc.inputs['Strength'].default_value = 1.0; nt.links.new(rp.outputs['Color'], bgc.inputs['Color'])
lpn = nt.nodes.new('ShaderNodeLightPath'); mxs = nt.nodes.new('ShaderNodeMixShader'); out = nt.nodes.new('ShaderNodeOutputWorld')
nt.links.new(lpn.outputs['Is Camera Ray'], mxs.inputs[0]); nt.links.new(bg.outputs['Background'], mxs.inputs[1]); nt.links.new(bgc.outputs['Background'], mxs.inputs[2])
nt.links.new(mxs.outputs[0], out.inputs['Surface'])
sunl = bpy.data.lights.new('Sun', 'SUN'); so = bpy.data.objects.new('Sun', sunl); prc.objects.link(so)
so.rotation_euler = (math.radians(48), math.radians(6), math.radians(28)); sunl.angle = math.radians(1.2); sunl.energy = 3.9; sunl.color = (1, 0.95, 0.85)
M['cloudw'] = material('S_cloudw', (1, 1, 1), rough=1.0, emit=(1, 1, 1), emit_strength=0.55)
M['dust'] = material('S_dust', (0.93, 0.88, 0.78), rough=1.0, emit=(0.9, 0.85, 0.75), emit_strength=0.3)
_cr = np.random.default_rng(11)
for k in range(26):
    an = k / 26 * 2 * PI + _cr.uniform(-0.15, 0.15); rr = _cr.uniform(90, 150); s_ = _cr.uniform(4.0, 7.5)
    cw = empty('CloudW', (rr * math.cos(an), rr * math.sin(an), _cr.uniform(24, 70)), None, prc)
    for (dx, dy, dz, r_) in [(0, 0, 0, 1.5), (1.5, 0.3, -0.2, 1.15), (-1.5, -0.2, -0.25, 1.2), (0.6, -0.5, 0.6, 1.1), (-0.6, 0.5, 0.5, 1.0), (2.6, 0, -0.45, 0.75), (-2.7, 0, -0.5, 0.8)]:
        c_, s2 = math.cos(an + PI / 2), math.sin(an + PI / 2)
        ball_('Puff', r_ * s_, (dx * s_ * c_, dx * s_ * s2 + dy, dz * s_), M['cloudw'], prc, parent=cw, sc=(1, 1, 0.6))

# ======================= ambiente: i giardini di Pippo (est) e di Gualtiero (ovest), la strada a sud =======================
bx('Prato', (-140, -140, -0.30), (140, 140, 0.0), M['park'], envc)
bx('Strada', (-140, -13.2, 0.0), (140, -8.4, 0.02), M['asphalt'], envc); bx('Marciapiede', (-140, -8.4, 0.0), (140, -7.9, 0.05), M['sidewalk'], envc)
for x in range(-60, 60, 4): bx('Linea', (x, -10.9, 0.02), (x + 1.8, -10.75, 0.025), M['frame'], envc)
def house_at(x, y, rotz, wi, ri, si, two, w=None, d=None):
    w = w or rng.uniform(4.6, 5.6); d = d or rng.uniform(4.0, 4.8)
    mb = MB(set004.house_mats(M, wi, ri, si)); set004.house_geo(mb, w, d, 4.5 if two else 2.9, two, rng); return mb.build('Casa', envc, (x, y, 0), rotz)
house_at(0.0, 9.5, 0.0, 0, 0, 1, True, 6.5, 4.5)                                                  # casa di Pippo
house_at(-17.5, 3.0, PI / 2, 3, 0, 0, True, 5.6, 4.6)                                              # casa di Gualtiero
for x in range(-34, 44, 9): house_at(x + rng.uniform(-1, 1), 27 + rng.uniform(0, 2), 0.0, int(rng.integers(0, 6)), int(rng.integers(0, 4)), int(rng.integers(0, 5)), bool(rng.integers(0, 2)))
for x in range(-34, 44, 9): house_at(x + rng.uniform(-1, 1), -35 - rng.uniform(0, 2), PI, int(rng.integers(0, 6)), int(rng.integers(0, 4)), int(rng.integers(0, 5)), bool(rng.integers(0, 2)))
for y in range(-2, 20, 9): house_at(21 + rng.uniform(0, 2), y, -PI / 2, int(rng.integers(0, 6)), int(rng.integers(0, 4)), int(rng.integers(0, 5)), bool(rng.integers(0, 2)))
house_at(-27, -1.0, PI / 2, 2, 1, 2, True)
def tower_at(x, y, rz=0.0):
    tw = rng.uniform(3.6, 4.6); ti = int(rng.integers(0, len(M['tower']))); h = rng.uniform(11, 26)
    mb = MB([M['tower'][ti], M['window'], M['frame'], M['concrete'], M['dark'], M['shutter'][int(rng.integers(0, 5))]])
    set004.tower_geo(mb, tw, h, rng); mb.build('Palazzo', envc, (x, y, 0), rz)
for x in range(-48, 56, 11): tower_at(x, 42 + rng.uniform(0, 4), 0.0); tower_at(x + 4, -50 - rng.uniform(0, 4), PI)
for y in range(-30, 36, 11): tower_at(40 + rng.uniform(0, 3), y, -PI / 2); tower_at(-42 - rng.uniform(0, 3), y, PI / 2)
def tree(x, y, s=1.0):
    cyl('Tronco', 0.16 * s, 1.5 * s, (x, y, 0.75 * s), M['bark'], envc)
    for (dx, dy, dz, r) in ((0, 0, 2.1, 0.95), (0.5, 0.1, 1.75, 0.7), (-0.5, -0.1, 1.8, 0.72)):
        ball_('Chioma', r * s, (x + dx * s, y + dy * s, dz * s), M['leaf'][int(rng.integers(0, 3))], envc)
for (x, y) in ((9.5, 4.0), (10.0, -5.5), (-13.0, 9.5), (5.5, 15.5), (-7, 16.5), (16, 14), (-30, 14), (-21, -6.0), (14, -19), (-24, -19)): tree(x, y, rng.uniform(1.0, 1.5))
fm = MB([M['frame']])
for yy in np.arange(-7.6, 8.01, 0.22): fm.box((-9.2, yy, 0.42), (0.04, 0.10, 0.84), 0); fm.box((-9.2, yy, 0.86), (0.04, 0.07, 0.08), 0)
for zz in (0.25, 0.60): fm.box((-9.23, 0.2, zz), (0.03, 15.7, 0.06), 0)
fm.build('Staccionata', envc)

A = props013.mats013(); Z12 = props012.mats012(); H = props010.mats010(); W = props015.mats015()
HX0 = 1000.0; KX0 = 1100.0; JX = 1200.0; HE = (0.0, 6.5)
# via la casa di Pippo: al suo posto l'ospedale
for o in list(envc.objects):
    if o.name.startswith('Casa') and abs(o.location.x) < 0.5 and abs(o.location.y - 9.5) < 0.5: bpy.data.objects.remove(o)
HEX = props015.hospital_ext(envc, W, HE[0], HE[1]); WESC = HEX['win_esc']
PILLOW = props013.hospital_set(envc, A, HX0)
WIN = props015.window(envc, W, (HX0 + 0.3, 2.97, 1.85), 1.3, 1.2)
CR = [(HX0 + 2.4, 0.9), (HX0 + 3.3, 0.9), (HX0 + 4.2, 0.9)]
for k, (x, y) in enumerate(CR): c_ = props015.crib(envc, W, 'Culla%d' % k); c_.location = (x, y, 0)
splight = props015.corridor(envc, W, KX0)
bars, board = props010.jail_set(envc, H, JX, label='ARIA  N. 0001', sub='SCORREGGIA AGGRAVATA'); bars.location = (JX, -60, -60); board.location = (JX, -0.35, 0.72)
shell = MB([W['cwall'], A['hfloor'], W['white']])
shell.b2((HX0 - 4.1, -7.5, -0.12), (HX0 + 6.6, 3.1, 0.0), 1); shell.b2((HX0 + 4.0, 3.0, 0.0), (HX0 + 6.6, 3.1, 3.3), 0); shell.b2((HX0 + 6.5, -7.5, 0.0), (HX0 + 6.6, 3.1, 3.3), 0)
shell.b2((HX0 - 4.1, -7.6, 0.0), (HX0 + 6.6, -7.5, 3.3), 0); shell.b2((HX0 - 4.1, -7.5, 0.0), (HX0 - 4.0, -4.0, 3.3), 0); shell.b2((HX0 - 4.1, -7.6, 3.2), (HX0 + 6.6, 3.1, 3.3), 2)
shell.b2((HX0 - 4.0, 2.95, 0.0), (HX0 + 6.5, 2.97, 0.12), 2); shell.build('StanzaParto', envc)

# ======================= personaggi =======================
P = pippo.build_pippo(chc); Tb = tumbo.build_tumbo(chc, scale=0.75); Z = props012.zucchina(chc, Z12)
BZ = props012.zucchina(chc, Z12); BZ['root'].scale = (0.36, 0.36, 0.36)
BH, BHh = props015.baby(chc, W, 'Neonato'); BH.scale = (1.15, 1.15, 1.15)
PUP = tumbo.build_tumbo(chc, scale=0.42)
DOC = props004.player(chc, 'Dottore', (0.30, 0.70, 0.60), (0.30, 0.70, 0.60), (0.96, 0.74, 0.6), (0.2, 0.13, 0.08), scale=1.0)
dhead = [c for c in DOC['root'].children if c.name.startswith('Head')][0]
cyl('DocCuffia', 0.29, 0.12, (0, 0.02, 0.2), W['scrubs'], chc, parent=dhead); ball_('DocMascherina', 1.0, (0, -0.24, -0.08), W['white'], chc, parent=dhead, sc=(0.17, 0.05, 0.1))
C1 = props010.cop(chc, 'Agente1'); C2 = props010.cop(chc, 'Agente2')
for r in (P['root'], Tb['root'], Z['root'], BZ['root'], BH, PUP['root'], DOC['root'], C1['root'], C2['root']): r.rotation_mode = 'XYZ'
for nm in 'LR': P['shoulder' + nm].rotation_mode = 'QUATERNION'
def qdir(d, rest=(0, 0, -1)): return Vector(rest).rotation_difference(Vector(d).normalized())
def yaw_to(a, b): return math.atan2(b[0] - a[0], -(b[1] - a[1]))

# ======================= oggetti =======================
COW = props015.cow(prc, W); CWR = COW['root']; CWR.rotation_mode = 'XYZ'
belly = ball_('ZucPancia', 0.13, (0, -props012.ZR * 0.62, 0.42), Z12['zuc'], chc, parent=Z['root'], sc=(1, 0.9, 1.25))
sand = props015.sandwich(chc, W, P['shoulderR'], (0.15, -0.25, -1.05)); sand.scale = (6.0, 6.0, 6.0)
bx('SoffittoCorridoio', (KX0 - 6.2, -4.2, 3.0), (KX0 + 6.2, 1.8, 3.1), W['white'], envc)
phm = {'phone': A['dark'], 'screen': material('W15_callscr', (0.3, 0.9, 0.3), rough=0.2, emit=(0.3, 1.0, 0.4), emit_strength=2.0)}
pphone = props010.phone(chc, phm, P['shoulderR'])
lens_ = props015.magnifier(chc, W, C1['shoulderR'], (0, -0.05, -0.72))
masks = [props015.gas_mask(chc, W, C1['head']), props015.gas_mask(chc, W, C2['head'])]
for m_ in masks: m_.location = (0, -0.25, -0.06); m_.scale = (1.05, 1.0, 1.0)
AIRC = props015.stink_cloud(prc, W, 'Aria', n=12, R=0.55, seed=4); AIRC.rotation_mode = 'XYZ'
cuf = props015.cuffs(prc, W, AIRC, (0, 0, 0), 1.5)
airballs = [c for c in AIRC.children if c is not cuf]
FOG = []
_fr = np.random.default_rng(21)
for k in range(8):
    fo = props015.stink_cloud(prc, W, 'Nebbia%d' % k, n=9, R=_fr.uniform(0.32, 0.5), seed=30 + k); FOG.append((fo, (HX0 - 2.5 + 0.95 * k + _fr.uniform(-0.3, 0.3), _fr.uniform(0.0, 2.4), _fr.uniform(2.3, 2.8)), 37.6 + 0.18 * k))
CARCLOUD = props015.stink_cloud(prc, W, 'NubeAuto', n=16, R=2.0, seed=9)
cars = []
for k in range(6):
    r_, lr_, lb_ = props010.police_car(prc, H, G9); r_.rotation_mode = 'XYZ'; cars.append((r_, lr_, lb_))
def area(name, loc, size, energy, col=(1, 0.97, 0.92)):
    l_ = bpy.data.lights.new(name, 'AREA'); l_.size = size; l_.energy = energy; l_.color = col; o_ = bpy.data.objects.new(name, l_); prc.objects.link(o_); o_.location = loc; return o_
area('LuceOspedale', (HX0 + 1.0, -1.8, 3.1), 5.0, 520); area('LuceOspedale2', (HX0 + 3.6, -1.0, 3.1), 3.0, 260); area('LuceCorridoio', (KX0 - 0.5, -0.5, 3.0), 5.0, 420); area('LuceCarcere', (JX, -2.5, 3.4), 4.0, 380)
flash_l = bpy.data.lights.new('Flash', 'POINT'); flash_o = bpy.data.objects.new('Flash', flash_l); prc.objects.link(flash_o); flash_o.location = (JX, -3.5, 2.6)
grn = bpy.data.lights.new('LuceVerde', 'POINT'); grn.color = (0.4, 1.0, 0.2); grn.shadow_soft_size = 2.0; gro = bpy.data.objects.new('LuceVerde', grn); prc.objects.link(gro); gro.location = (HX0 + 1.5, -1.0, 2.6)

def desc(o):
    for c in o.children:
        yield c
        yield from desc(c)
def show(o, intervals):
    for q in ([o] + list(desc(o)) if not isinstance(o, list) else o):
        first = intervals[0][0] <= 0.0
        q.hide_render = not first; q.keyframe_insert('hide_render', frame=1)
        for (a, b) in intervals:
            if a > 0.0: q.hide_render = False; q.keyframe_insert('hide_render', frame=fr(a))
            if b < TOTAL: q.hide_render = True; q.keyframe_insert('hide_render', frame=fr(b))
def hide(o):
    for q in [o] + list(desc(o)): q.hide_render = True; q.keyframe_insert('hide_render', frame=1)
def pop(o, t, d=0.32, s0=0.0001, over=1.22, s1=1.0, pre=False):
    b = tuple(o.scale)
    if pre:
        for tt_ in (0.0, t - 0.05): o.keyframe_insert('scale', frame=fr(tt_))
    for (tt_, v) in ((t, s0), (t + 0.55 * d, over), (t + d, s1)):
        o.scale = (b[0] * v, b[1] * v, b[2] * v); o.keyframe_insert('scale', frame=fr(tt_))
def keys(o, prop, pts):
    for (t_, v) in pts: setattr(o, prop, v); o.keyframe_insert(prop, frame=fr(t_))

T_Z1, T_Z2, T_Z3 = 15.94, 19.56, 24.94
show(Z['root'], [(0.0, TOTAL)]); hide(Z['veil']); hide(Z['legs'])
show(belly, [(4.72, 24.94)]); keys(belly, 'scale', [(15.9, (0.13, 0.117, 0.1625)), (15.96, (0.104, 0.0975, 0.13)), (19.5, (0.104, 0.0975, 0.13)), (19.58, (0.078, 0.0715, 0.104))])
show(BZ['root'], [(0.0, 4.72), (T_Z1, TOTAL)]); hide(BZ['veil']); hide(BZ['legs']); pop(BZ['root'], T_Z1, 0.3, pre=True)
show(BH, [(0.0, 4.72), (T_Z2, TOTAL)]); pop(BH, T_Z2, 0.3, pre=True)
show(PUP['root'], [(0.0, 4.72), (T_Z3, TOTAL)]); pop(PUP['root'], T_Z3, 0.3, pre=True)
show(DOC['root'], [(10.4, 25.8)])
show(sand, [(7.1, 10.4)]); show(pphone, [(44.9, 47.3)])
show(C1['root'], [(49.5, 54.6), (58.0, 61.1)]); show(C2['root'], [(49.5, 54.6)]); show(lens_, [(49.5, 51.2)])
for m_ in masks: show(m_, [(51.66, TOTAL)]); pop(m_, 51.66, 0.25)
show(cuf, [(53.9, 59.8)]); pop(cuf, 53.9, 0.22)
for b_ in airballs: hide(b_)
AIRC.hide_render = True; AIRC.keyframe_insert('hide_render', frame=1)
for (fo, p_, t0) in FOG: show(fo, [(t0, 54.6)]); fo.location = p_; pop(fo, t0, 1.2, over=1.1)
show(CWR, [(33.7, 37.6)]); show(CARCLOUD, [(62.2, TOTAL)]); pop(CARCLOUD, 62.2, 0.9, over=1.15)
for k, (r_, lr_, lb_) in enumerate(cars): show(r_, [(47.3, 49.5), (58.0, TOTAL)] if k < 2 else [(63.8, TOTAL)])
keys(flash_l, 'energy', [(0.0, 0.0), (55.15, 0.0), (55.2, 4000.0), (55.4, 0.0), (56.85, 0.0), (56.9, 4000.0), (57.1, 0.0)])
keys(grn, 'energy', [(0.0, 0.0), (37.5, 0.0), (39.0, 300.0), (54.6, 300.0), (54.62, 0.0)])

# ======================= pose =======================
DOWN = lambda s: (s * 0.14, 0, -1)
PPX = (HX0 + 3.3, -1.9); TBP = (HX0 + 0.9, -2.6); CH_P = (KX0 - 1.1, 1.22); CH_T = (KX0 - 0.35, 1.22)
YT = 2 * PI + yaw_to(PPX, TBP)
SEATED = dict(hL=-PI / 2, hR=-PI / 2)
def far(t): return dict(loc=(HX0 - 40, 0, 0), rot=(0, 0, 0), aL=DOWN(-1), aR=DOWN(1), hL=0.0, hR=0.0, head=(0, 0, 0))
def pp(t):
    S_ = dict(loc=(PPX[0], PPX[1], 0), rot=(0, 0, PI), aL=DOWN(-1), aR=DOWN(1), hL=0.0, hR=0.0, head=(0, 0, 0))
    if t < 4.72:                                                                                      # aggancio: le tre culle
        k = math.sin(t * 22) * 0.04; S_.update(aL=(-0.55, -0.25, 0.75), aR=(0.55, -0.25, 0.75), rot=(-0.06, k, PI), head=(-0.1, 0, 0))
    elif t < 7.1: return far(t)
    elif t < 10.4:                                                                                     # corridoio col panino
        bite = (math.sin((t - 7.1) * 4.2) > 0.2)
        S_.update(loc=(CH_P[0], CH_P[1], -0.12), rot=(0, 0, 0), aL=(-0.2, -0.6, -0.5), aR=(0.25, -0.8, 0.35) if bite else (0.25, -0.6, -0.6), head=(0.08 * bite, 0, 0), **SEATED)
    elif t < 14.5: return far(t)
    elif t < 25.8:
        if 21.2 <= t < 22.9: k = math.sin(t * 12); S_.update(aL=(-0.5, 0.0, 0.85 + 0.1 * k), aR=(0.5, 0.0, 0.85 - 0.1 * k), loc=(PPX[0], PPX[1], 0.12 * abs(k)))
        if t >= 24.94: S_.update(aL=(-0.55, -0.3, 0.7), aR=(0.55, -0.3, 0.7), rot=(-0.1, 0, PI))
    elif t < 37.5:                                                                                     # si gira lentamente e guarda Tumbo
        y = lerp((PI,), (YT,), ramp(t, 26.44, 27.9))[0]
        if t >= 32.3: y = YT - 1.3 * ramp(t, 32.5, 33.0)
        S_.update(rot=(0, 0, y), head=(0.0, 0, 0))
        if t >= 32.3: S_.update(aL=(-0.5, -0.4, 0.4), aR=(0.5, -0.4, 0.4))
    elif t < 41.12:                                                                                    # puzza: si tappa il naso, barcolla
        k = math.sin(t * 6) * ramp(t, 39.6, 40.2)
        S_.update(rot=(0, 0.12 * k, 0.2 * k), aR=(0.0, -0.75, 0.6), aL=(-0.3, -0.3, -0.7))
    elif t < 44.4:                                                                                     # sviene e si riprende
        fall = ramp(t, 41.12, 41.5) * (1 - ramp(t, 43.76, 44.35))
        S_.update(rot=(-PI / 2 * fall, 0, 0), loc=(PPX[0], PPX[1], 0.5 * fall), aL=(-0.9, 0, -0.4), aR=(0.9, 0, -0.4))
    elif t < 47.3: S_.update(rot=(0, 0, 0), aR=(0.12, -0.28, 0.95) if t >= 44.9 else DOWN(1), aL=(-0.4, -0.3, -0.6))
    elif t < 54.6: S_.update(loc=(HX0 + 3.9, -1.6, 0), rot=(0, 0, -0.5), aR=(0.0, -0.75, 0.6))
    else: return far(t)
    return S_
def tp(t):
    S_ = dict(loc=(TBP[0], TBP[1], 0), rot=(0, 0, yaw_to(TBP, PPX)), head=(0, 0, 0), tail=-1.0 + 0.5 * math.sin(t * 12))
    if t < 4.72: S_.update(head=(0, 0, 0.6))
    elif t < 7.1: S_.update(loc=(HX0 - 40, 3, 0))
    elif t < 10.4: S_.update(loc=(CH_T[0], CH_T[1], 0.52), rot=(-0.2, 0, 0), head=(0.1, 0, 0.3 * math.sin(t * 2)))
    elif t < 14.5: S_.update(loc=(HX0 - 40, 3, 0))
    elif t < 32.3:
        S_.update(rot=(0, 0, yaw_to(TBP, CR[1])))
        if 27.8 <= t < 30.3: S_.update(head=(-0.25, 0, -0.8 + 0.1 * math.sin(t * 5)))               # fischietta guardando altrove
        if t >= 30.3: S_.update(rot=(0, 0, yaw_to(TBP, PPX)), head=(0.15, 0, 0), loc=(TBP[0], TBP[1], 0.03 * abs(math.sin(t * 40))))
    elif t < 33.15:                                                                                    # corre e salta dalla finestra
        a = (TBP[0], TBP[1], 0.0); b = (HX0 + 0.6, -1.0, 0.0); c = (HX0 + 0.3, 3.15, 1.75)
        if t < 32.7:
            u = ramp(t, 32.3, 32.7); p_ = lerp(a, b, u); S_.update(loc=(p_[0], p_[1], 0.06 * abs(math.sin(t * 30))), rot=(0, 0, yaw_to(a, b)))
        else:
            u = (t - 32.7) / 0.45; p_ = lerp(b, c, u); S_.update(loc=(p_[0], p_[1], p_[2] + 1.0 * math.sin(PI * u)), rot=(-0.5, 0, yaw_to(b, c)))
    elif t < 33.78: S_.update(loc=(HX0 - 40, 3, 0))
    elif t < 37.6:                                                                                     # fuori: sulla mucca
        if t < 34.3:
            u = (t - 33.78) / 0.52; a = (WESC[0], WESC[1] + 0.2, WESC[2] - 0.4); b = add(cowp(34.3)[0], (0, 0.1, 0.8))
            p_ = lerp(a, b, u); S_.update(loc=(p_[0], p_[1], p_[2] + 0.6 * math.sin(PI * u)), rot=(-0.3, 0, 0))
        else:
            l, yw = cowp(t); c_, s_ = math.cos(yw), math.sin(yw); ox, oy = 0.0, 0.15
            S_.update(loc=(l[0] + ox * c_ - oy * s_, l[1] + ox * s_ + oy * c_, l[2] + 0.8 + 0.04 * math.sin(t * 20)), rot=(0, 0, yw), head=(-0.3, 0, 0))
    else: S_.update(loc=(HX0 - 40, 3, 0))
    return S_
def cowp(t):
    """mucca: posizione (origine pancia) e imbardata."""
    p0 = (WESC[0], WESC[1] - 2.1, WESC[2] - 0.75); bob = 0.15 * math.sin(t * 5)
    if t < 35.66: return (p0[0], p0[1], p0[2] + bob), 0.0
    u = (t - 35.66); goal = (30.0, -6.0, 22.0); k = min(1.0, u / 1.8) ** 1.6
    yw = 1.18 * ramp(t, 35.66, 35.95)
    return lerp((p0[0], p0[1], p0[2] + bob), goal, k), yw
def zp(t):
    sh = 0.03 * math.sin(t * 40) * (10.5 < t < 14.4 or T_Z1 - 0.3 < t < T_Z1 + 0.2 or T_Z2 - 0.3 < t < T_Z2 + 0.2 or T_Z3 - 0.3 < t < T_Z3 + 0.2)
    return dict(loc=(PILLOW[0] + 0.15 + sh, PILLOW[1] - 0.05, 0.62), rot=(-0.12, 0.08 * math.sin(t * 9) * (sh != 0), 0.15))
def carp(k, t):
    """auto della polizia: posizione, imbardata, luci accese."""
    YL = -10.8
    if k < 2:
        xe = -1.5 - 5.5 * k
        if t < 50: u = ramp(t, 47.3, 48.7); x = xe - 40 * (1 - u) ** 2 if t < 48.7 else xe; return (x, YL, 0.0), PI / 2, (-0.05 * math.sin(PI * ramp(t, 48.6, 48.9))), True
        if k == 1: return (xe, YL, 0.0), PI / 2, 0.0, True
        if t < 60.3: return (xe, YL, 0.0), PI / 2, 0.0, True
        d = t - 60.3; x = xe + 4.5 * d * d if d < 1.0 else xe + 4.5 + 9.0 * (d - 1.0)
        if t >= 62.22:
            x = xe + 4.5 + 9.0 * (62.22 - 61.3); fl = t - 62.22
            return (x + 1.2 * ramp(t, 62.22, 62.6), YL + 0.6 * math.sin(fl * 9) * math.exp(-fl * 2), 0.6 * math.sin(PI * min(1, fl / 0.45)) * (fl < 0.45)), PI / 2 + 0.5 * math.sin(fl * 7) * math.exp(-fl * 1.5), 0.15 * math.sin(fl * 18) * math.exp(-fl * 2.5), True
        return (x, YL, 0.0), PI / 2, 0.0, True
    side = 1 if k % 2 == 0 else -1; xe = (13.5 - 3.4 * (k // 4)) if side > 0 else (27.0 + 3.4 * (k // 4))
    xe = {2: 4.5, 3: 20.5, 4: 0.5, 5: 24.5}[k]; yl = -12.2 if side > 0 else -9.4
    u = ramp(t, 63.88 + 0.25 * (k - 2), 65.1 + 0.2 * (k - 2)); x = xe - side * 40 * (1 - u) ** 2
    return (x, yl, 0.0), (PI / 2 if side > 0 else -PI / 2), 0.0, True
def airp(t):
    if t < 54.6: return (HX0 + 1.3, -1.45, 1.35 + 0.08 * math.sin(t * 3)), (0, 0, 0.3 * math.sin(t * 1.3)), 1.0
    if t < 58.0: return (JX, 0.6, 1.5 + 0.05 * math.sin(t * 3)), (0, 0, 0.1 * math.sin(t * 2)), 1.5
    u = ramp(t, 58.0, 59.6); a = (-1.2, -6.2, 1.3); b = (-1.5, -10.4, 1.25)
    return lerp(a, b, u), (0, 0, 0), 1.0 - 0.95 * ramp(t, 59.6, 59.8)
def c1p(t):
    if t < 54.6:
        lunge = ramp(t, 53.5, 53.9) * (1 - ramp(t, 54.2, 54.5))
        return dict(loc=(HX0 + 0.6 + 0.3 * lunge, -2.2, 0), rot=(0.15 * lunge, 0, yaw_to((HX0 + 0.6, -2.2), (HX0 + 1.3, -1.45)) if t > 52.7 else 0.4 * math.sin(t * 2.5) + PI * 0.9), aL=-1.4 * (t > 52.7) - 0.2, aR=-1.5 if t < 51.2 else -1.4 * (t > 52.7) - 0.2, leg=0.0, head=(0.15, 0, 0))
    u = ramp(t, 58.0, 59.6); k = math.sin(t * 12) * (58.0 < t < 59.6)
    p_ = lerp((-0.4, -6.0, 0), (-0.6, -9.0, 0), u)
    return dict(loc=p_, rot=(0, 0, yaw_to((-0.4, -6.0), (-0.6, -9.0))), aL=-1.3, aR=-1.3, leg=0.5 * k, head=(0, 0, 0))
def c2p(t):
    lunge = ramp(t, 53.6, 54.0) * (1 - ramp(t, 54.3, 54.55))
    sniff = 0.2 * math.sin(t * 9) * (49.5 < t < 51.1)
    return dict(loc=(HX0 + 2.4 - 0.3 * lunge, -1.6, 0), rot=(0.15 * lunge + 0.1, 0, yaw_to((HX0 + 2.4, -1.6), (HX0 + 1.3, -1.45)) if t > 52.7 else PI + 0.5 * math.sin(t * 1.7)), aL=-1.4 * (t > 52.7) - 0.15, aR=-1.4 * (t > 52.7) - 0.15, leg=0.0, head=(0.2 + sniff, 0, 0))

# ======================= chiavi =======================
TR = Tb['root']; ZRt = Z['root']
BZ['root'].location = (CR[0][0], CR[0][1] - 0.02, 0.72); BH.location = (CR[1][0], CR[1][1], 0.72); PUP['root'].location = (CR[2][0], CR[2][1] + 0.02, 0.72)
for f in range(1, NF + 1):
    t = (f - 1) / FPS
    s = pp(t); r = P['root']; r.location = s['loc']; r.rotation_euler = s['rot']; r.keyframe_insert('location', frame=f); r.keyframe_insert('rotation_euler', frame=f)
    for nm, k in (('L', 'aL'), ('R', 'aR')):
        sh = P['shoulder' + nm]; sh.rotation_quaternion = qdir(s[k]); sh.keyframe_insert('rotation_quaternion', frame=f)
    for nm, k in (('L', 'hL'), ('R', 'hR')):
        hp = P['hip' + nm]; hp.rotation_euler = (s[k], 0, 0); hp.keyframe_insert('rotation_euler', frame=f)
    P['head'].rotation_euler = s['head']; P['head'].keyframe_insert('rotation_euler', frame=f)
    q = tp(t); TR.location = q['loc']; TR.rotation_euler = q['rot']; TR.keyframe_insert('location', frame=f); TR.keyframe_insert('rotation_euler', frame=f)
    Tb['head'].rotation_euler = q['head']; Tb['head'].keyframe_insert('rotation_euler', frame=f)
    Tb['tail'].rotation_euler = (q['tail'], 0, 0.5 * math.sin(t * 14)); Tb['tail'].keyframe_insert('rotation_euler', frame=f)
    z = zp(t); ZRt.location = z['loc']; ZRt.rotation_euler = z['rot']; ZRt.keyframe_insert('location', frame=f); ZRt.keyframe_insert('rotation_euler', frame=f)
    push = (10.6 < t < 14.4); talk = push or (T_Z1 - 0.3 < t < T_Z1 + 0.3) or (T_Z2 - 0.3 < t < T_Z2 + 0.3) or (T_Z3 - 0.3 < t < T_Z3 + 0.3)
    Z['mouth'].scale = (0.045, 0.02, 0.022 + 0.05 * abs(math.sin(t * 12)) * talk); Z['mouth'].keyframe_insert('scale', frame=f)
    Z['eyes'].scale = (1.25 if push and math.sin(t * 6) > 0 else 1.0, 1.0, 1.0); Z['eyes'].keyframe_insert('scale', frame=f)
    PUP['tail'].rotation_euler = (-1.0, 0, 0.8 * math.sin(t * 16)); PUP['tail'].keyframe_insert('rotation_euler', frame=f)
    BZ['root'].rotation_euler = (0, 0, 0.15 * math.sin(t * 2)); BZ['root'].keyframe_insert('rotation_euler', frame=f)
    BHh.rotation_euler = (0, 0.15 * math.sin(t * 2.3), 0); BHh.keyframe_insert('rotation_euler', frame=f)
    if 10.3 < t < 25.9:                                                                                # dottore ai piedi del letto
        k = math.sin(t * 8) * (10.6 < t < 14.4); r = DOC['root']; r.location = (HX0 + 1.55, -0.1, 0); r.rotation_euler = (0.1, 0, -PI / 2); r.keyframe_insert('location', frame=f); r.keyframe_insert('rotation_euler', frame=f)
        for nm in 'LR': DOC['shoulder' + nm].rotation_euler = (-1.3 + 0.3 * k, 0, 0); DOC['shoulder' + nm].keyframe_insert('rotation_euler', frame=f)
    if 33.6 < t < 37.7:
        l, yw = cowp(t); CWR.location = l; CWR.rotation_euler = (0.15 * ramp(t, 35.66, 36.0), 0, yw); CWR.keyframe_insert('location', frame=f); CWR.keyframe_insert('rotation_euler', frame=f)
        for sx, w_ in zip((-1, 1), COW['wings']): w_.rotation_euler = (0, sx * 0.55 * math.sin(t * 32), 0); w_.keyframe_insert('rotation_euler', frame=f)
        for j, lg in enumerate(COW['legs']): lg.rotation_euler = (0.35 * math.sin(t * 6 + j), 0, 0); lg.keyframe_insert('rotation_euler', frame=f)
        COW['tail'].rotation_euler = (0.4 * math.sin(t * 9), 0, 0.5 * math.sin(t * 7)); COW['tail'].keyframe_insert('rotation_euler', frame=f)
    for (C_, fn, a_, b_) in ((C1, c1p, 49.4, 61.2), (C2, c2p, 49.4, 54.7)):
        if a_ < t < b_:
            c = fn(t); r = C_['root']; r.location = c['loc']; r.rotation_euler = c['rot']; r.keyframe_insert('location', frame=f); r.keyframe_insert('rotation_euler', frame=f)
            for nm, sg in (('L', 1), ('R', -1)):
                C_['shoulder' + nm].rotation_euler = (c['a' + nm], 0, 0); C_['shoulder' + nm].keyframe_insert('rotation_euler', frame=f)
                C_['hip' + nm].rotation_euler = (sg * c['leg'], 0, 0); C_['hip' + nm].keyframe_insert('rotation_euler', frame=f)
            C_['head'].rotation_euler = c['head']; C_['head'].keyframe_insert('rotation_euler', frame=f)
    if 52.6 < t < 59.9:
        l, e, sc = airp(t); AIRC.location = l; AIRC.rotation_euler = e; AIRC.scale = (sc,) * 3
        for p_ in ('location', 'rotation_euler', 'scale'): AIRC.keyframe_insert(p_, frame=f)
    for k_, (r_, lr_, lb_) in enumerate(cars):
        l, yw, pitch, on = carp(k_, t); r_.location = l; r_.rotation_euler = (pitch, 0, yw); r_.keyframe_insert('location', frame=f); r_.keyframe_insert('rotation_euler', frame=f)
        blink = int(t * 6 + k_) % 2 == 0
        lr_.scale = (0.42, 0.20, 0.13 if blink else 0.02); lb_.scale = (0.42, 0.20, 0.02 if blink else 0.13); lr_.keyframe_insert('scale', frame=f); lb_.keyframe_insert('scale', frame=f)
    if t >= 62.1:
        l = carp(0, t)[0]; CARCLOUD.location = (l[0], l[1], 1.2 + 0.3 * ramp(t, 62.2, 63.5)); CARCLOUD.keyframe_insert('location', frame=f)

_last = {}
def _ex(key, fn, t, k):
    if key in _last and t - 0.06 > _last[key][1]: fn(fr(t - 0.06), **_last[key][0])
    fn(fr(t), **k); _last[key] = (k, t)
def pex(t, **k): _ex('p', lambda f, **kk: pippo.express(P, f, **kk), t, k)
def tex(t, **k): _ex('t', lambda f, **kk: tumbo.tumbo_express(Tb, f, **kk), t, k)
pex(0.0, brow=-0.7, brow_lift=0.9, eye_scale=1.4, mouth_open=1.0); pex(4.72, smile=0.6, mouth_open=0.2)
for k in range(8): pex(7.1 + 0.37 * k, smile=0.8, mouth_open=0.7 if k % 2 else 0.1)
pex(14.5, brow_lift=0.5, mouth_open=0.2, smile=0.3); pex(16.0, smile=0.6, brow_lift=0.4, mouth_open=0.3); pex(19.6, brow_lift=0.6, eye_scale=1.1, mouth_open=0.3)
pex(21.2, smile=1.0, mouth_open=0.8, brow=0.3); pex(23.3, smile=0.5, mouth_open=0.2); pex(24.94, brow=-0.7, brow_lift=0.9, eye_scale=1.45, mouth_open=1.0)
pex(26.4, brow=0.9, eye_open=0.55, mouth_open=0.0, smile=-0.5); pex(29.8, brow=1.0, eye_open=0.5, smile=-0.8, mouth_open=0.3)
pex(32.4, brow=-0.6, brow_lift=0.8, eye_scale=1.3, mouth_open=0.9); pex(37.6, brow=-0.4, eye_open=0.7, mouth_open=0.0, smile=-0.6)
pex(39.7, brow=-0.5, eye_open=0.35, mouth_open=0.6, look=(0.6, 0.3)); pex(40.5, eye_open=0.3, mouth_open=0.7, look=(-0.6, -0.3)); pex(41.2, eye_open=0.05, mouth_open=0.9)
pex(43.76, eye_open=0.5, brow_lift=0.5, mouth_open=0.3); pex(44.4, brow=1.0, eye_open=0.85, mouth_open=0.4, smile=-0.3); pex(45.3, brow=1.0, mouth_open=0.9)
pex(49.5, brow=0.6, eye_open=0.7, smile=-0.6); pex(53.9, smile=1.0, brow=0.6, mouth_open=0.6)
tex(0.0, tongue=0.0, brow=-0.3, look=(0.5, 0)); tex(7.1, tongue=0.8); tex(14.5, tongue=0.6); tex(27.8, tongue=0.0, brow=0.3, eye_open=0.6, look=(-0.6, 0.4))
tex(30.3, eye_scale=1.5, brow=-0.8, tongue=0.0, look=(0, 0)); tex(32.3, eye_scale=1.3, brow=-0.6); tex(34.3, tongue=1.0, eye_scale=1.2, brow=0.6)
tumbo.tumbo_express(PUP, 1, tongue=1.0)

# ======================= effetti =======================
def streak(name, sc, mat, t0, t1, fn, parent=None, mesh=None, rot=None):
    o = obj(name, mesh or shared_mesh('sphere_lo'), (0, 0, -80), sc, mat, prc, parent=parent)
    if rot: o.rotation_euler = rot
    o.hide_render = True; o.keyframe_insert('hide_render', frame=1); o.hide_render = False; o.keyframe_insert('hide_render', frame=fr(t0))
    if t1 < TOTAL: o.hide_render = True; o.keyframe_insert('hide_render', frame=fr(t1))
    for f in range(fr(t0), min(NF, fr(t1)) + 1):
        r_ = fn((f - 1) / FPS); o.location = r_[0]; o.keyframe_insert('location', frame=f)
        if len(r_) > 1: o.scale = r_[1]; o.keyframe_insert('scale', frame=f)
        if len(r_) > 2: o.rotation_euler = r_[2]; o.keyframe_insert('rotation_euler', frame=f)
    return o
er = np.random.default_rng(3)
def burst(name, mat, t0, dur, c0, n, vmax, sc, grav=4.9, up=1.0, mesh=None, vy=None):
    for k in range(n):
        v = np.array([er.uniform(-vmax, vmax), er.uniform(-vmax, vmax) if vy is None else er.uniform(*vy), er.uniform(0.3, 1.0) * vmax * up])
        streak(name, sc, mat, t0, t0 + dur, lambda t, v=v: ((c0[0] + v[0] * (t - t0), c0[1] + v[1] * (t - t0), max(0.03, c0[2] + v[2] * (t - t0) - grav * (t - t0) ** 2)),), mesh=mesh)
for k in range(5):                                                                                      # sudore di Eleonora
    ph = k / 5; streak('Sudore', (0.025, 0.025, 0.04), W['glass'], 10.6, 14.4, lambda t, ph=ph: ((PILLOW[0] + 0.15 + 0.14 * math.cos(ph * 6.28), -0.2, 1.55 - 0.6 * ((t * 1.3 + ph) % 1.0)),))
for k in range(10):                                                                                     # cuoricini per la zucchina bellissima
    ph = k / 10; streak('Cuore', (0.06, 0.06, 0.06), Z12['lip'], 16.8, 18.1, lambda t, ph=ph: ((CR[0][0] + 0.5 * math.cos(ph * 6.28 + t), CR[0][1] - 0.2, 1.1 + 0.9 * ((t - 16.8) / 1.3) + 0.1 * math.sin(ph * 9)),))
burst('Coriandolo', W['bell'], 21.2, 1.5, (CR[1][0], CR[1][1], 2.0), 18, 1.6, (0.03, 0.03, 0.03), grav=1.5)
for k in range(5):                                                                                      # sudore di Tumbo
    ph = k / 5; streak('GocciaTumbo', (0.03, 0.03, 0.05), W['glass'], 30.3, 32.3, lambda t, ph=ph: ((TBP[0] + 0.25 * math.cos(ph * 6.28), TBP[1] - 0.25, 1.05 - 0.6 * ((t * 1.6 + ph) % 1.0)),))
burst('Vetro', W['glass'], 33.08, 0.8, (HX0 + 0.3, 3.0, 1.85), 16, 1.6, (0.06, 0.02, 0.06), grav=3.0, vy=(0.5, 2.0))
burst('VetroFuori', W['glass'], 33.78, 1.0, (WESC[0], WESC[1] - 0.1, WESC[2]), 16, 1.8, (0.07, 0.02, 0.07), grav=4.0, vy=(-2.5, -0.5))
for k in range(16):                                                                                     # scorregge della mucca in volo
    t0 = 35.9 + 0.11 * k
    def fp(t, t0=t0):
        l, yw = cowp(t0); u = t - t0; d = 0.95 + 0.6 * u
        return ((l[0] - d * math.sin(yw), l[1] + d * math.cos(yw), l[2] + 0.4 + 0.3 * u), (0.25 + 0.9 * u,) * 3)
    streak('Scorreggia', (0.3, 0.3, 0.3), W['stink'] if k % 2 else W['stinkd'], t0, min(TOTAL, t0 + 1.4), fp)
for k in range(10):                                                                                     # puzza che entra dalla finestra
    ph = k / 10; streak('PuzzaEntra', (0.4, 0.4, 0.4), W['stink'], 37.5, 39.6, lambda t, ph=ph: ((HX0 + 0.3 + 0.6 * math.sin(ph * 9), 2.9 - 3.5 * ((t * 0.7 + ph) % 1.0), 1.85 - 0.4 * ((t * 0.7 + ph) % 1.0)), (0.3 + 0.6 * ((t * 0.7 + ph) % 1.0),) * 3))
for k in range(5):                                                                                      # stelline sopra Pippo svenuto
    ph = k / 5; streak('Stellina', (0.07, 0.07, 0.07), W['bell'], 41.5, 43.8, lambda t, ph=ph: ((PPX[0] + 0.45 * math.cos(t * 5 + ph * 6.28), PPX[1] + 2.25 + 0.45 * math.sin(t * 5 + ph * 6.28), 0.85),))
burst('PuzzaAuto', W['stink'], 62.22, 1.4, (11.3, -10.8, 1.3), 20, 3.5, (0.35, 0.35, 0.35), grav=0.8, up=0.6)

# ======================= camera =======================
def Z0(t): return (0, 0, 0)
def CW(t): return cowp(t)[0]
def CAR0(t): return carp(0, t)[0]
PZ = lambda x, y, z: (x, y, z)
SHOTS = [  # t0, t1, sub cam, p0, p1, sub mira, a0, a1, lente, f
    (0.0, 1.6, Z0, (HX0 + 4.6, -3.6, 1.95), (HX0 + 4.45, -3.1, 1.85), Z0, (HX0 + 3.3, 0.9, 0.95), (HX0 + 3.3, 0.9, 0.95), 34, 6),
    (1.6, 3.0, Z0, (HX0 + 4.2, -0.55, 1.05), (HX0 + 4.2, -0.35, 1.02), Z0, (CR[2][0], CR[2][1], 0.9), (CR[2][0], CR[2][1], 0.9), 45, 4),
    (3.0, 4.72, Z0, (HX0 + 3.3, 0.25, 1.9), (HX0 + 3.3, 0.0, 1.88), Z0, (PPX[0], PPX[1], 1.75), (PPX[0], PPX[1], 1.75), 35, 4),
    (4.72, 7.1, Z0, (-3.0, -14.0, 1.8), (-2.0, -12.5, 2.3), Z0, (0.0, 6.5, 4.6), (0.0, 6.5, 5.1), 24, 16),
    (7.1, 10.4, Z0, (KX0 - 0.3, -3.0, 1.4), (KX0 - 0.35, -2.7, 1.4), Z0, (KX0 - 0.3, 1.2, 1.15), (KX0 - 0.3, 1.2, 1.2), 20, 7),
    (10.4, 11.6, Z0, (HX0 + 0.3, -4.6, 1.8), (HX0 + 0.2, -4.3, 1.8), Z0, (HX0 - 0.2, 0.0, 1.0), (HX0 - 0.2, 0.0, 1.0), 26, 8),
    (11.6, 13.1, Z0, (HX0 + 0.4, -2.4, 1.35), (HX0 + 0.35, -2.25, 1.35), Z0, (PILLOW[0] + 0.15, 0.0, 1.15), (PILLOW[0] + 0.15, 0.0, 1.15), 38, 5),
    (13.1, 14.5, Z0, (HX0 - 0.35, -1.4, 1.35), (HX0 - 0.4, -1.2, 1.35), Z0, (PILLOW[0] + 0.15, -0.05, 1.25), (PILLOW[0] + 0.15, -0.05, 1.25), 45, 4),
    (14.5, 18.1, Z0, (CR[0][0] - 0.1, -1.0, 1.4), (CR[0][0] - 0.05, -0.8, 1.35), Z0, (CR[0][0], CR[0][1], 0.95), (CR[0][0], CR[0][1], 0.95), 36, 5),
    (18.1, 20.9, Z0, (CR[1][0] - 0.3, -0.5, 1.35), (CR[1][0] - 0.25, -0.35, 1.3), Z0, (CR[1][0], CR[1][1], 0.95), (CR[1][0], CR[1][1], 0.95), 40, 4),
    (20.9, 23.3, Z0, (PPX[0], 0.2, 1.9), (PPX[0], 0.0, 1.9), Z0, (PPX[0], PPX[1], 1.4), (PPX[0], PPX[1], 1.45), 28, 5),
    (23.3, 25.8, Z0, (CR[2][0] - 0.2, -0.45, 1.2), (CR[2][0] - 0.15, -0.25, 1.15), Z0, (CR[2][0], CR[2][1], 0.9), (CR[2][0], CR[2][1], 0.9), 42, 4),
    (25.8, 27.9, Z0, (PPX[0], 0.25, 1.85), (PPX[0], 0.1, 1.85), Z0, (PPX[0], PPX[1], 1.75), (PPX[0], PPX[1], 1.75), 40, 4),
    (27.9, 30.3, Z0, (HX0 + 2.6, -2.1, 1.6), (HX0 + 2.5, -2.15, 1.55), Z0, (TBP[0], TBP[1], 0.5), (TBP[0], TBP[1], 0.5), 40, 5),
    (30.3, 32.3, Z0, (HX0 + 2.3, -2.25, 0.85), (HX0 + 2.2, -2.27, 0.83), Z0, (TBP[0], TBP[1], 0.6), (TBP[0], TBP[1], 0.6), 50, 4),
    (32.3, 33.78, Z0, (HX0 + 2.6, -5.2, 1.7), (HX0 + 2.5, -5.0, 1.75), Z0, (HX0 + 0.5, 0.3, 1.25), (HX0 + 0.4, 0.6, 1.4), 22, 8),
    (33.78, 35.6, Z0, (WESC[0] - 3.5, WESC[1] - 10.5, WESC[2] - 0.2), (WESC[0] - 3.2, WESC[1] - 10.0, WESC[2]), Z0, (WESC[0], WESC[1] - 1.4, WESC[2] - 0.2), (WESC[0], WESC[1] - 1.5, WESC[2] - 0.1), 28, 10),
    (35.6, 37.5, Z0, (-2.0, -15.0, 3.0), (0.0, -15.0, 5.0), CW, (0, 0, 0.5), (0, 0, 0.5), 26, 16),
    (37.5, 39.6, Z0, (HX0 + 1.5, -5.0, 1.9), (HX0 + 1.5, -4.6, 1.9), Z0, (HX0 + 1.2, 0.5, 1.4), (HX0 + 1.2, 0.5, 1.4), 22, 8),
    (39.6, 41.9, Z0, (PPX[0], -5.3, 1.5), (PPX[0], -5.0, 1.4), Z0, (PPX[0], PPX[1], 1.25), (PPX[0], PPX[1] + 0.6, 0.7), 30, 6),
    (41.9, 43.7, Z0, (PPX[0] + 1.6, -3.9, 2.8), (PPX[0] + 1.5, -3.8, 2.7), Z0, (PPX[0], PPX[1] + 1.1, 0.4), (PPX[0], PPX[1] + 1.1, 0.4), 30, 6),
    (43.7, 47.3, Z0, (PPX[0], -4.5, 1.6), (PPX[0], -4.0, 1.65), Z0, (PPX[0], PPX[1], 1.5), (PPX[0], PPX[1], 1.55), 30, 6),
    (47.3, 49.5, Z0, (-12.0, -19.0, 1.6), (-10.0, -18.5, 1.8), Z0, (-3.0, -10.8, 1.2), (-2.0, -10.6, 1.5), 24, 14),
    (49.5, 51.1, Z0, (HX0 + 2.6, 1.9, 1.6), (HX0 + 2.5, 1.7, 1.6), Z0, (HX0 + 1.3, -2.3, 1.3), (HX0 + 1.3, -2.3, 1.3), 24, 8),
    (51.1, 52.74, Z0, (HX0 + 1.5, 1.0, 1.85), (HX0 + 1.5, 0.8, 1.85), Z0, (HX0 + 1.5, -2.0, 1.75), (HX0 + 1.5, -2.0, 1.75), 26, 6),
    (52.74, 54.6, Z0, (HX0 + 1.4, 1.4, 1.6), (HX0 + 1.4, 1.2, 1.6), Z0, (HX0 + 1.4, -1.9, 1.3), (HX0 + 1.4, -1.9, 1.3), 26, 6),
    (54.6, 56.1, Z0, (JX, -5.6, 1.6), (JX, -5.4, 1.6), Z0, (JX, 0.6, 1.4), (JX, 0.6, 1.4), 40, 8),
    (56.1, 58.0, Z0, (JX + 0.6, -3.8, 1.5), (JX + 0.55, -3.6, 1.5), Z0, (JX, 0.6, 1.3), (JX, 0.6, 1.3), 45, 6),
    (58.0, 61.1, Z0, (-7.0, -16.5, 1.7), (-6.0, -16.2, 1.8), Z0, (-1.5, -9.0, 1.2), (1.0, -9.6, 1.2), 28, 12),
    (61.1, 63.8, CAR0, (-2.5, -8.0, 2.2), (-3.0, -8.5, 2.6), CAR0, (1.0, 0.0, 0.8), (0.0, 0.0, 1.2), 30, 12),
    (63.8, TOTAL, Z0, (8.0, -24.5, 6.0), (8.2, -24.0, 6.2), Z0, (13.0, -10.8, 1.0), (13.0, -10.8, 1.0), 28, 16),
]
camd = bpy.data.cameras.new('Cam'); cam = bpy.data.objects.new('Cam', camd); cac.objects.link(cam); scene.camera = cam
camd.clip_start = 0.05; camd.clip_end = 1500; camd.sensor_width = 36
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
for o in bpy.data.objects: lin(o)
set_interp(camd, 'CONSTANT')
lookdev.upgrade(scene, 720, 1280, samples=12, world=0.36, sun_e=6.5, exposure=-0.1)
os.makedirs('../t015', exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath('../t015/pippo_t015.blend')); print('SAVED')
