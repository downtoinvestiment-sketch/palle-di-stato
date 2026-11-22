"""Test 009 - PIPPO CONTRO GUALTIERO, episodio 1: LA NEVE AD AGOSTO. Salva ../t009/pippo_t009.blend
Personaggi: Pippo e Tumbo ESISTENTI (pippo.py, tumbo.py) invariati; Gualtiero = nuovo vicino ricorrente (props009.gualtiero)."""
import sys, math, os
sys.path.insert(0, os.path.dirname(__file__))
import bpy, numpy as np
from mathutils import Vector, Euler, Matrix
from common import *
from render_setup import *
import set004, props007, props009, pippo, tumbo
from set004 import obj, bx, cyl, ball_, MB

FPS = 24; TOTAL = 44.0; NF = int(TOTAL * FPS)
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

# ======================= personaggi =======================
P = pippo.build_pippo(chc); Tb = tumbo.build_tumbo(chc, scale=0.75); G = props009.gualtiero(chc, G9)
for r in (P['root'], Tb['root'], G['root']): r.rotation_mode = 'XYZ'
for R_ in (P, G):
    for nm in 'LR': R_['shoulder' + nm].rotation_mode = 'QUATERNION'
def qdir(d, rest=(0, 0, -1)): return Vector(rest).rotation_difference(Vector(d).normalized())

# ======================= oggetti =======================
SNOWMAN = (-8.15, -1.3)
snowman = props009.snowman(prc, G9); snowman.location = (SNOWMAN[0], SNOWMAN[1], 0)
puddle0 = props009.disc(prc, 'Pozza0', G9['puddle']); puddle0.location = (SNOWMAN[0], SNOWMAN[1], 0.012)
phon = props009.hand_tool(chc, G9, G['shoulderL'], 'phon')
gun = props009.hand_tool(chc, G9, G['shoulderR'], 'gun'); pack = props009.backpack(chc, G9, G['root']); flame = props009.flame(chc, G9, gun, (0, 0, -1.06))
beanie = props009.beanie(prc, G9, P['head'])
sun = props009.sun(prc, G9); sun.location = (-8.2, 20.0, 9.8)
FRZ = (-7.2, -0.5)
frz, lid = props009.freezer(prc, G9); frz.location = (FRZ[0], FRZ[1], 0)
PILE = (-8.45, -0.5)
pile = props009.ice_pile(prc, G9); pile.location = (PILE[0], PILE[1], 0)
puddle1 = props009.disc(prc, 'Pozza1', G9['puddle']); puddle1.location = (PILE[0], PILE[1], 0.012)
BBQ = (-9.75, -0.6)
bbq, bflames = props009.barbecue(prc, G9); bbq.location = (BBQ[0], BBQ[1], 0)
PTS = [(-7.4 + 0.5 * i, -0.4 - 0.5 * j) for j in range(6) for i in range(9)]
pops = props009.popsicle_parts(prc, G9, PTS); sticks = bpy.data.objects['Stecchi']
VAC = (-5.5, 0.5); TUBE = (-4.08, 1.0, 1.38)
vac = props009.vacuum(prc, G9); vac.location = (VAC[0], VAC[1], 0); vac.rotation_euler = (0, 0, 0.4)
tube = props009.cannon_tube(prc, G9)
MOUND = (0.5, 1.0)
mound = props009.heap(prc, G9, 'Cumulo', seed=4); mound.location = (MOUND[0], MOUND[1], 0)
DOOR = (-1.43, 7.2)
hheap = props009.heap(prc, G9, 'Valanga', seed=6); hheap.location = (DOOR[0], DOOR[1] - 0.5, 0)
chair = props009.armchair(prc, G9)
trk, bed, load = props009.truck(prc, G9); trk.rotation_euler = (0, 0, PI / 2)
CAR = (-12.6, -10.5)
car = props009.car(prc, G9); car.location = (CAR[0], CAR[1], 0); car.rotation_euler = (0, 0, PI / 2)
cheap = props009.heap(prc, G9, 'NeveMacchina', n=20, seed=8); cheap.location = (CAR[0] + 0.1, CAR[1], 0)
slipper = obj('CiabattaVolante', set004.box_c(), (0, 0, -40), (0.17, 0.32, 0.06), G9['slipper'], prc)

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
def pop(o, t, d=0.32, s0=0.0001, over=1.22, s1=1.0):
    b = tuple(o.scale)
    for (tt_, v) in ((t, s0), (t + 0.55 * d, over), (t + d, s1)):
        o.scale = (b[0] * v, b[1] * v, b[2] * v); o.keyframe_insert('scale', frame=fr(tt_))
def keys(o, prop, pts):
    for (t_, v) in pts: setattr(o, prop, v); o.keyframe_insert(prop, frame=fr(t_))
show(snowman, [(0.0, 4.6)]); show(puddle0, [(0.0, 4.6)]); show(phon, [(0.0, 4.6)])
keys(snowman, 'scale', [(0.0, (1, 1, 1)), (0.4, (1, 1, 1)), (2.2, (1.05, 1.05, 0.55)), (3.9, (1.1, 1.1, 0.16)), (4.6, (1.1, 1.1, 0.12))])
keys(puddle0, 'scale', [(0.0, (0.05, 0.05, 0.02)), (0.5, (0.3, 0.3, 0.02)), (3.9, (1.25, 1.1, 0.02))])
show(gun, [(37.6, TOTAL)]); show(pack, [(37.6, TOTAL)]); pop(pack, 37.6); pop(gun, 37.6)
show(beanie, [(7.4, TOTAL)]); show(sun, [(8.95, 10.0)]); pop(sun, 8.95, 0.4)
show(frz, [(10.0, 15.1)]); pop(frz, 10.05)
keys(lid, 'rotation_euler', [(10.9, (0, 0, 0)), (11.25, (0, 1.9, 0))]); keys(frz, 'rotation_euler', [(11.35, (0, 0, 0)), (11.95, (0, -1.75, 0)), (12.05, (0, -1.68, 0)), (12.15, (0, -1.75, 0))])
show(pile, [(11.9, 15.1)]); keys(pile, 'scale', [(11.9, (0.2, 0.2, 0.05)), (12.6, (1.15, 1.15, 1.15)), (12.75, (1, 1, 1)), (13.7, (1, 1, 1)), (14.8, (1.25, 1.25, 0.05))])
show(puddle1, [(13.6, 15.1)]); keys(puddle1, 'scale', [(13.6, (0.1, 0.1, 0.02)), (14.9, (1.2, 1.0, 0.02))])
show(bbq, [(13.0, 15.1)]); pop(bbq, 13.0, 0.3)
def lick_time(i, j):
    k = j // 2; x = -7.4 + 0.5 * i; u = (x + 7.7) / 4.6 if k % 2 == 0 else (-3.1 - x) / 4.6
    return 18.35 + 0.65 * k + 0.55 * u
show(sticks, [(15.3, 22.0)])
for n_, hd in enumerate(pops):
    i, j = n_ % 9, n_ // 9; t0 = 15.35 + 0.085 * (i + 1.4 * j); show(hd, [(t0, lick_time(i, j))]); pop(hd, t0, 0.22)
show(vac, [(22.0, 27.9)]); show(tube, [(22.0, 27.9)]); pop(vac, 22.02, 0.3)
show(mound, [(22.9, 27.9)]); keys(mound, 'scale', [(22.9, (0.1, 0.1, 0.05)), (25.6, (1.35, 1.35, 1.0))])
show(hheap, [(27.0, 27.9)]); keys(hheap, 'scale', [(27.0, (0.3, 0.3, 0.2)), (27.5, (1.5, 1.9, 1.5)), (27.9, (1.7, 2.3, 1.6))])
show(chair, [(27.0, 27.9)]); keys(chair, 'location', [(27.0, (DOOR[0], DOOR[1] + 0.6, 0.3)), (27.8, (DOOR[0] + 0.2, DOOR[1] - 2.9, 0.75))]); keys(chair, 'rotation_euler', [(27.0, (0, 0, PI)), (27.8, (-0.25, 0.1, PI + 0.3))])
show(trk, [(27.9, TOTAL)]); show(cheap, [(31.25, TOTAL)])
keys(cheap, 'scale', [(31.25, (0.3, 0.3, 0.1)), (32.3, (1.9, 1.5, 1.5)), (34.6, (2.7, 1.9, 2.5)), (36.4, (2.8, 2.0, 2.65))])
keys(bed, 'rotation_euler', [(30.85, (0, 0, 0)), (31.6, (-0.85, 0, 0)), (31.7, (-0.80, 0, 0)), (31.8, (-0.85, 0, 0))])
keys(load, 'scale', [(31.0, (1.2, 2.1, 1.5)), (32.2, (0.4, 0.5, 0.2)), (32.3, (0.001, 0.001, 0.001))]); keys(load, 'location', [(31.0, (0, -2.15, 0.1)), (32.2, (0, -0.3, 0.1))])
show(slipper, [(35.3, 36.5)])

# ======================= pose =======================
DOWN = lambda s: (s * 0.14, 0, -1)
UP = dict(aL=(-0.35, -0.25, 1), aR=(0.35, -0.25, 1))
def TX(t):
    if t < 30.3: u = max(0.0, (t - 27.9) / 2.4); return -30.0 + 23.5 * (1 - (1 - u) ** 2)
    return -6.5 + 0.12 * math.sin((t - 30.3) * 18) * math.exp(-(t - 30.3) * 6)
ROOF = 2.55
def pp(t):
    S_ = dict(loc=(0, 0, 0), rot=(0, 0, 0), aL=DOWN(-1), aR=DOWN(1), hL=0.0, hR=0.0, head=(0, 0, 0))
    if t < 4.6:                                    # gli sciolgono il pupazzo
        j = 0.03 * math.sin(t * 38); q = ramp(t, 2.8, 3.1)
        S_.update(loc=(-7.25 + j, 0.45, 0), rot=(0, 0, -0.54 - 0.5 * q), aL=lerp((-0.5, -0.3, 0.85), (-0.4, -0.2, -0.8), q), aR=lerp((0.5, -0.3, 0.85), (0.1, -1, 0.2 + 0.08 * math.sin(t * 16)), q), head=(0, 0, 0.45 * q))
    elif t < 7.4:                                  # faccia a faccia
        S_.update(loc=(-8.1, -1.5, 0.03 * abs(math.sin(t * 7))), rot=(0.1, 0, -0.35), aL=(-0.55, -0.15, -0.8), aR=(0.55, -0.15, -0.8), head=(0, 0, -0.5 * (1 - ramp(t, 6.2, 6.5))))
    elif t < 10.0:                                 # vuole la neve. ad agosto
        d = ramp(t, 9.0, 9.4)
        S_.update(loc=(-4.5, -1.5, 0), aL=lerp((0.3, -0.9, 0.05), DOWN(-1), d), aR=lerp((-0.3, -0.9, 0.05), DOWN(1), d), head=(-0.3 + 0.6 * d, 0.12 * math.sin(t * 2.5) * (1 - d), 0), rot=(0.12 * d, 0, 0))
    elif t < 15.1:                                 # il freezer
        push = ramp(t, 11.3, 11.6) * (1 - ramp(t, 12.0, 12.3)); win = ramp(t, 12.3, 12.6) * (1 - ramp(t, 13.2, 13.5)); sad = ramp(t, 14.0, 14.4)
        aL = lerp(lerp((-0.3, -0.85, -0.45), UP['aL'], win), (-0.5, -0.3, 0.85), sad); aR = lerp(lerp((0.3, -0.85, -0.45), UP['aR'], win), (0.5, -0.3, 0.85), sad)
        S_.update(loc=(-6.55, 0.55 - 0.25 * push, 0.12 * win * abs(math.sin(t * 12))), rot=(0.3 * push, 0, -0.5 * ramp(t, 13.2, 13.6)), aL=aL, aR=aR, head=(0, 0, -0.55 * ramp(t, 13.2, 13.6)))
    elif t < 22.0:                                 # i ghiaccioli
        bend = ramp(t, 15.3, 15.6) * (1 - ramp(t, 16.3, 16.6)); tada = ramp(t, 16.6, 16.9) * (1 - ramp(t, 18.25, 18.45)); shock = ramp(t, 18.25, 18.5)
        gx = gp(t)['loc'][0]
        aL = lerp(lerp(lerp(DOWN(-1), (-0.2, -0.6, -0.8), bend), (-0.9, -0.2, 0.35), tada), (-0.5, -0.3, 0.85), shock); aR = lerp(lerp(lerp(DOWN(1), (0.2, -0.6, -0.8), bend), (0.9, -0.2, 0.35), tada), (0.5, -0.3, 0.85), shock)
        S_.update(loc=(-5.5 + 0.03 * math.sin(t * 40) * shock, 0.4, 0), rot=(0.5 * bend, 0, 0), aL=aL, aR=aR, head=(0.25 * shock, 0, max(-1.0, min(1.0, (gx + 5.5) * 0.35)) * shock))
    elif t < 27.9:                                 # il cannone sparaneve
        lost = ramp(t, 25.6, 25.9); j = 0.02 * math.sin(t * 45) * (1 - lost) * ramp(t, 22.6, 22.9)
        S_.update(loc=(-4.6 - j, 1.0, 0), rot=(-0.08 * (1 - lost), 0, PI / 2), aL=lerp((-0.12, -0.85, 0.35), (-0.55, -0.3, 0.8), lost), aR=lerp((0.12, -0.85, 0.35), (0.55, -0.3, 0.8), lost), head=(0.1 * ramp(t, 26.0, 26.4), 0, 0.4 * ramp(t, 26.0, 26.4)))
    elif t < 39.8:                                 # sul tetto del camion
        go = ramp(t, 30.9, 31.3); k = abs(math.sin(t * 9)) * go * (1 - ramp(t, 38.9, 39.1)); sc = ramp(t, 38.9, 39.1)
        S_.update(loc=(TX(t) + 2.2, -10.25, ROOF + 0.18 * k), rot=(0.1 * (1 - go), 0, 0.95 - 1.9 * sc * 0),
                  aL=lerp(lerp((-0.5, -0.2, -0.8), UP['aL'], go), (-0.5, -0.25, -0.8), sc), aR=lerp(lerp((0.15, -1, 0.25), UP['aR'], go), (0.5, -0.25, -0.8), sc), head=(0, 0, -0.9 * sc))
    else:                                          # team Pippo?
        pt = ramp(t, 41.6, 41.9)
        S_.update(loc=(-8.1, -1.5, 0), rot=(0, 0, -0.25 + 0.25 * pt), aL=(-0.55, -0.15, -0.8), aR=lerp((0.55, -0.15, -0.8), (0.05, -1, 0.12), pt), head=(0, 0, -0.45 * (1 - ramp(t, 40.4, 40.7))))
    return S_

def gp(t):
    S_ = dict(loc=(0, 0, 0), rot=(0, 0, 0), aL=DOWN(-1), aR=DOWN(1), hL=0.0, hR=0.0, head=(0, 0, 0), belly=1.0)
    if t < 4.6:                                    # il phon
        lg = ramp(t, 2.3, 2.6); b = 0.05 * abs(math.sin(t * 13)) * lg
        S_.update(loc=(-9.95, -1.0, b), rot=(0.22 - 0.1 * lg, 0, PI / 2), aL=(0.1 + 0.08 * math.sin(t * 5), -1, -0.12), aR=(0.5, -0.1, -0.85), head=(-0.1 - 0.25 * lg, 0, -0.35 * lg))
    elif t < 7.4: S_.update(loc=(-10.3, -1.5, 0), rot=(-0.08, 0, 0.35), aL=(-0.55, -0.15, -0.8), aR=(0.55, -0.15, -0.8), head=(-0.1, 0, 0.5 * (1 - ramp(t, 6.2, 6.5))))
    elif t < 13.0: S_.update(loc=(-10.6, 1.2, 0), rot=(0, 0, PI / 2 + 0.3))
    elif t < 15.1:                                 # il barbecue
        lg = ramp(t, 13.9, 14.2); b = 0.05 * abs(math.sin(t * 13)) * lg
        S_.update(loc=(-10.5, -0.6, b), rot=(0.1 - 0.15 * lg, 0, PI / 2), aL=lerp((-0.1, -0.9, -0.4), (-0.4, -0.3, 0.9), lg), aR=lerp((0.1, -0.9, -0.4), (0.4, -0.3, 0.9), lg), head=(-0.2 * lg, 0, -0.4 * lg))
    elif t < 18.2: S_.update(loc=(-9.95, -0.6, 0), rot=(0.15 * ramp(t, 17.0, 17.4), 0, PI / 2), head=(0, 0, -0.3))
    elif t < 20.3:                                 # li lecca tutti
        k = math.sin(t * 30); bl = 1.0 + 0.55 * ramp(t, 18.4, 20.2)
        if t < 18.35: u = (t - 18.2) / 0.15; loc = (-9.95 + 2.25 * u, -0.6 - 0.05 * u, 0.9 * math.sin(PI * u)); yaw = PI / 2
        else:
            q = (t - 18.35) / 0.65; kk = min(2, int(q)); u = min(1.0, (q - kk) * 0.65 / 0.55); y = -0.65 - 1.0 * kk
            if u >= 1.0 and kk < 2: y -= 1.0 * ((q - kk) * 0.65 - 0.55) / 0.10
            x = -7.7 + 4.6 * u if kk % 2 == 0 else -3.1 - 4.6 * u; loc = (x, y, 0.04 * abs(k)); yaw = PI / 2 if kk % 2 == 0 else -PI / 2
        S_.update(loc=loc, rot=(0.85, 0, yaw), aL=(-0.5, 0.5, -0.4), aR=(0.5, 0.5, -0.4), hL=0.9 * k - 0.7, hR=-0.9 * k - 0.7, head=(-0.55, 0, 0), belly=bl)
    elif t < 22.0:                                 # sazio
        u = ramp(t, 20.3, 20.6); pat = 0.12 * math.sin(t * 14)
        S_.update(loc=(-3.1 - 0.1 * u, -2.65 - 0.15 * u, 0), rot=(0.85 - 0.97 * u, 0, PI / 2 - (PI / 2 - 0.55) * u), aL=(0.3, -0.75, -0.55 + pat), aR=(-0.3, -0.75, -0.55 - pat), head=(-0.55 * (1 - u) - 0.15 * u, 0, 0), belly=1.55)
    elif t < 24.3: S_.update(loc=(-10.4, 2.4, 0), rot=(0, 0, PI / 2))
    elif t < 27.9:                                 # gira il tubo
        u = ramp(t, 24.3, 25.3); k = math.sin(t * 16) * (1 - u) * (t > 24.3)
        S_.update(loc=lerp((-8.6, 2.6, 0), (-4.45, 1.95, 0), u), rot=(0.15, 0, lerp((PI / 2,), (0.6,), u)[0] + 0.45 * ramp(t, 25.6, 26.2)), hL=0.6 * k, hR=-0.6 * k,
                  aL=lerp((-0.3, -0.5, -0.8), (-0.12, -1, 0.05), ramp(t, 25.2, 25.5)), aR=lerp((0.3, -0.5, -0.8), (0.12, -1, 0.05), ramp(t, 25.2, 25.5)), head=(-0.15 * ramp(t, 26.3, 26.6), 0, 0))
    elif t < 33.0:                                 # arriva il camion
        no = ramp(t, 31.0, 31.4)
        S_.update(loc=(-11.3, -7.4, 0), rot=(0, 0, 0.9), aL=lerp(DOWN(-1), (-0.5, -0.3, 0.85), no), aR=lerp(DOWN(1), (0.5, -0.3, 0.85), no), head=(-0.2 * no, 0, 0.3))
    elif t < 39.8:                                 # la macchina sepolta, poi il lanciafiamme
        arm = ramp(t, 37.6, 37.9); rage = (1 - ramp(t, 36.3, 36.6)); b = 0.22 * abs(math.sin(t * 11)) * rage; fl = ramp(t, 38.5, 38.7)
        sh = 0.25 * math.sin(t * 20) * rage
        S_.update(loc=(-12.3, -13.05, b), rot=(-0.1 * fl, 0, 0.25 + 0.5 * arm), aL=lerp(lerp((-0.5, -0.1, -0.85), (-0.45, -0.3, 0.85 + sh), rage), (-0.5, -0.15, -0.8), arm), aR=lerp(lerp((0.5, -0.1, -0.85), (0.45, -0.3, 0.85 - sh), rage), (0.5, -0.8, 0.12 + 0.3 * fl), arm),
                  head=(-0.3 * rage - 0.1 * fl, 0, 0), hL=0.3 * math.sin(t * 22) * rage, hR=-0.3 * math.sin(t * 22) * rage)
    else: S_.update(loc=(-10.35, -1.5, 0), rot=(-0.06, 0, 0.3), aL=(-0.55, -0.15, -0.8), aR=(0.3, -0.35, 0.9), head=(-0.08, 0, 0.45 * (1 - ramp(t, 40.4, 40.7))))
    return S_

def tp(t):
    S_ = dict(loc=(0, 0, 0), rot=(0, 0, 0), head=(0, 0, 0), tail=-1.0 + 0.5 * math.sin(t * 12))
    if t < 4.6: S_.update(loc=(-6.4, 1.2, 0), rot=(0, 0, -0.5), head=(0.25, 0, -0.3), tail=-0.2)
    elif t < 7.4: S_.update(loc=(-8.35, -3.0, 0), rot=(0, 0, -0.3), head=(0.1, 0, -0.2), tail=-0.3)
    elif t < 10.0: S_.update(loc=(-3.4, -1.9, 0), rot=(0, 0, 0.3), head=(-0.25 + 0.5 * ramp(t, 9.0, 9.4), 0, 0.4))
    elif t < 15.1: S_.update(loc=(-5.5, 1.1, 0), rot=(0, 0, -0.5), head=(0, 0, -0.5 * ramp(t, 13.2, 13.6)))
    elif t < 22.0: S_.update(loc=(-4.4, 0.6, 0), rot=(0, 0, -0.2), head=(0.15, 0, 0))
    elif t < 27.0: S_.update(loc=(0.6, 1.7, 0.35 * abs(math.sin(t * 6)) * ramp(t, 23.2, 23.6)), rot=(0, 0, -0.9), head=(-0.5, 0, 0))
    elif t < 27.9: u = (t - 27.0) / 0.8; S_.update(loc=(DOOR[0] + 0.2 * u, DOOR[1] + 0.55 - 3.5 * u, 0.72 + 0.45 * u), rot=(-0.25 * u, 0, 0.1), head=(-0.2, 0, 0))
    elif t < 39.8: S_.update(loc=(TX(t) + 2.25, -11.15, ROOF + 0.12 * abs(math.sin(t * 10)) * ramp(t, 30.9, 31.3) * (1 - ramp(t, 38.9, 39.1))), rot=(0, 0, 0.6), head=(-0.2, 0, -0.9 * ramp(t, 38.9, 39.1)))
    else: S_.update(loc=(-8.35, -3.0, 0), rot=(0, 0, -0.2), head=(0, 0, 0))
    return S_

def tube_dir(t):
    """azimut ed elevazione del cannone."""
    return 0.87 * ramp(t, 25.6, 26.2), math.radians(50) + 0.03 * math.sin(t * 40)
GXP = (-12.3, -13.05)
# ======================= chiavi =======================
TR = Tb['root']; GR = G['root']
for f in range(1, NF + 1):
    t = (f - 1) / FPS
    for R_, s in ((P, pp(t)), (G, gp(t))):
        r = R_['root']; r.location = s['loc']; r.rotation_euler = s['rot']; r.keyframe_insert('location', frame=f); r.keyframe_insert('rotation_euler', frame=f)
        for nm, k in (('L', 'aL'), ('R', 'aR')):
            sh = R_['shoulder' + nm]; sh.rotation_quaternion = qdir(s[k]); sh.keyframe_insert('rotation_quaternion', frame=f)
        for nm, k in (('L', 'hL'), ('R', 'hR')):
            hp = R_['hip' + nm]; hp.rotation_euler = (s[k], 0, 0); hp.keyframe_insert('rotation_euler', frame=f)
        R_['head'].rotation_euler = s['head']; R_['head'].keyframe_insert('rotation_euler', frame=f)
    b = gp(t)['belly']; G['belly'].scale = (0.33 * b, 0.31 * b, 0.30 * b); G['belly'].keyframe_insert('scale', frame=f)
    q = tp(t); TR.location = q['loc']; TR.rotation_euler = q['rot']; TR.keyframe_insert('location', frame=f); TR.keyframe_insert('rotation_euler', frame=f)
    Tb['head'].rotation_euler = q['head']; Tb['head'].keyframe_insert('rotation_euler', frame=f)
    Tb['tail'].rotation_euler = (q['tail'], 0, 0.5 * math.sin(t * 14)); Tb['tail'].keyframe_insert('rotation_euler', frame=f)
    if 12.9 < t < 15.2:                                                                              # fiamme del barbecue
        on = ramp(t, 13.55, 13.85)
        for k, (fo, s) in enumerate(bflames):
            fl = 1 + 0.25 * math.sin(t * 23 + k * 1.7) + 0.15 * math.sin(t * 37 + k)
            fo.scale = (0.17 * s * (0.2 + 1.5 * on), 0.17 * s * (0.2 + 1.5 * on), 0.9 * s * (0.15 + 1.9 * on) * fl); fo.rotation_euler = (0, 0.55 * on + 0.1 * math.sin(t * 17 + k), 0)
            fo.keyframe_insert('scale', frame=f); fo.keyframe_insert('rotation_euler', frame=f)
    if 21.9 < t < 28.0:                                                                              # cannone
        az, el = tube_dir(t); tube.location = TUBE; tube.rotation_euler = (0, PI / 2 - el, az); tube.keyframe_insert('location', frame=f); tube.keyframe_insert('rotation_euler', frame=f)
    if 27.8 < t:                                                                                     # camion
        trk.location = (TX(t), -10.5, 0); trk.keyframe_insert('location', frame=f)
    if 37.5 < t:                                                                                     # fiamma
        fl = 1 + 0.2 * math.sin(t * 31) + 0.12 * math.sin(t * 47)
        s_ = 0.001 if t < 38.55 else (1.3 * ramp(t, 38.55, 38.75) * fl if t < 39.8 else 0.32 * fl)
        flame.scale = (s_, s_, s_ * (1.25 if t < 39.8 else 1.0)); flame.keyframe_insert('scale', frame=f)
    if 35.2 < t < 36.6:                                                                              # la ciabatta
        u = t - 35.3; slipper.location = (GXP[0] + 0.3 + 1.6 * u, GXP[1] - 0.2 - 1.0 * u, max(0.04, 0.3 + 5.0 * u - 5.5 * u * u)); slipper.rotation_euler = (9 * u, 3 * u, 0)
        slipper.keyframe_insert('location', frame=f); slipper.keyframe_insert('rotation_euler', frame=f)

_lastP = [None, -1.0]; _lastT = [None, -1.0]; _lastG = [None, -1.0]
def pex(t, **k):
    if _lastP[0] is not None and t - 0.06 > _lastP[1]: pippo.express(P, fr(t - 0.06), **_lastP[0])
    pippo.express(P, fr(t), **k); _lastP[0] = k; _lastP[1] = t
def tex(t, **k):
    if _lastT[0] is not None and t - 0.06 > _lastT[1]: tumbo.tumbo_express(Tb, fr(t - 0.06), **_lastT[0])
    tumbo.tumbo_express(Tb, fr(t), **k); _lastT[0] = k; _lastT[1] = t
def gx(t, **k):
    if _lastG[0] is not None and t - 0.06 > _lastG[1]: props009.gex(G, fr(t - 0.06), **_lastG[0])
    props009.gex(G, fr(t), **k); _lastG[0] = k; _lastG[1] = t
pex(0.0, brow=-0.8, brow_lift=0.8, eye_scale=1.3, mouth_open=1.0); pex(2.9, brow=1.0, mouth_open=0.8, eye_scale=1.1); pex(4.7, brow=1.0, eye_open=0.6, mouth_open=0.0, look=(-0.6, 0)); pex(6.3, brow=1.0, eye_open=0.7, look=(0, 0))
pex(7.5, smile=1.0, brow_lift=0.5, eye_open=0.5, look=(0, 0.6)); pex(9.0, brow=-0.6, brow_lift=0.3, eye_open=0.6, mouth_open=0.3, look=(0, 0.5)); pex(10.1, smile=0.9, brow=0.8)
pex(11.3, brow=1.0, mouth_open=0.4, eye_open=0.7); pex(12.3, smile=1.0, mouth_open=0.7, brow_lift=0.5); pex(13.3, brow=-0.7, brow_lift=0.7, eye_scale=1.25, mouth_open=0.7, look=(-0.7, 0)); pex(14.3, brow=-0.8, brow_lift=0.5, mouth_open=1.0, eye_open=0.6)
pex(15.2, smile=0.8, brow=0.8, look=(0, -0.5)); pex(16.7, smile=1.0, mouth_open=0.5, brow_lift=0.5); pex(18.3, brow=-0.8, brow_lift=0.8, eye_scale=1.3, mouth_open=1.0, look=(0, -0.4)); pex(20.5, brow=1.0, eye_open=0.6, mouth_open=0.2)
pex(22.1, smile=1.0, brow=0.9, mouth_open=0.5); pex(25.6, brow=-0.8, brow_lift=0.8, eye_scale=1.3, mouth_open=0.9); pex(28.0, smile=1.0, brow=1.0, eye_open=0.8); pex(31.0, smile=1.0, mouth_open=0.9, brow_lift=0.6, eye_scale=1.1)
pex(38.9, brow=-0.8, brow_lift=0.9, eye_scale=1.35, mouth_open=0.6, look=(-0.7, -0.3)); pex(39.85, brow=1.0, eye_open=0.65, smile=0.4, look=(-0.6, 0)); pex(40.5, brow=1.0, eye_open=0.7, smile=0.6, look=(0, 0)); pex(41.7, smile=1.0, mouth_open=0.5, brow=0.6)
tex(0.0, eye_scale=1.3, brow=-0.6); tex(4.7, brow=1.0, eye_open=0.6); tex(7.5, tongue=0.9); tex(13.3, eye_scale=1.3, brow=-0.5); tex(15.2, tongue=0.8, look=(0, -0.4)); tex(18.3, eye_scale=1.4, brow=-0.6)
tex(22.1, tongue=0.9, look=(0, 0.5)); tex(27.0, eye_scale=1.4, brow=-0.6); tex(28.0, tongue=0.5); tex(38.9, eye_scale=1.4, brow=-0.7); tex(39.85, brow=1.0, eye_open=0.6); tex(41.7, tongue=0.6)
gx(0.0, brow=1.0, mouth=0.5); gx(2.4, brow=0.8, mouth=1.0); gx(4.7, brow=1.0, mouth=0.05, look=(0.7, 0)); gx(6.3, brow=1.0, mouth=0.15, look=(0, 0)); gx(7.5, brow=0.5, mouth=0.1)
gx(13.1, brow=1.0, mouth=0.4); gx(13.9, brow=0.8, mouth=1.0); gx(15.2, brow=0.6, mouth=0.1); gx(17.2, brow=0.9, mouth=0.4, tongue=0.5); gx(18.25, brow=0.9, mouth=0.9, tongue=1.0)
gx(20.4, brow=-0.2, mouth=0.3, tongue=0.6); gx(21.15, brow=-0.5, mouth=1.0, tongue=0.0); gx(21.6, brow=0.6, mouth=0.4); gx(22.1, brow=0.8, mouth=0.1); gx(25.3, brow=1.0, mouth=0.7); gx(26.3, brow=0.8, mouth=1.0)
gx(28.0, brow=-0.3, mouth=0.2, look=(0.5, 0.2)); gx(31.0, brow=-0.9, mouth=1.0, look=(0, 0.5)); gx(33.1, brow=1.0, mouth=1.0, look=(0, 0.6)); gx(36.5, brow=1.0, mouth=0.05, look=(0, 0)); gx(37.6, brow=1.0, mouth=0.6)
gx(38.6, brow=1.0, mouth=1.0); gx(39.85, brow=1.0, mouth=0.5, look=(0.7, 0)); gx(40.5, brow=1.0, mouth=0.6, look=(0, 0))

# ======================= effetti =======================
def streak(name, sc, mat, t0, t1, fn, parent=None, mesh=None, rot=None):
    o = obj(name, mesh or shared_mesh('sphere_lo'), (0, 0, -80), sc, mat, prc, parent=parent)
    if rot: o.rotation_euler = rot
    o.hide_render = True; o.keyframe_insert('hide_render', frame=1); o.hide_render = False; o.keyframe_insert('hide_render', frame=fr(t0))
    if t1 < TOTAL: o.hide_render = True; o.keyframe_insert('hide_render', frame=fr(t1))
    for f in range(fr(t0), min(NF, fr(t1)) + 1):
        r_ = fn((f - 1) / FPS); o.location = r_[0]; o.keyframe_insert('location', frame=f)
        if len(r_) > 1: o.scale = r_[1]; o.keyframe_insert('scale', frame=f)
    return o
er = np.random.default_rng(3)
def burst(name, mat, t0, dur, c0, n, vmax, sc, grav=4.9, up=1.0, vx=0.0, mesh=None):
    for k in range(n):
        v = np.array([er.uniform(-vmax, vmax) + vx, er.uniform(-vmax, vmax), er.uniform(0.3, 1.0) * vmax * up])
        streak(name, sc, mat, t0, t0 + dur, lambda t, v=v: ((c0[0] + v[0] * (t - t0), c0[1] + v[1] * (t - t0), max(0.03, c0[2] + v[2] * (t - t0) - grav * (t - t0) ** 2)),), mesh=mesh)
def steam(t0, t1, c0, n=6, s=0.16, rise=1.3):
    for k in range(n):
        ph = k / n; dx = er.uniform(-0.3, 0.3); dy = er.uniform(-0.3, 0.3)
        def fn(t, ph=ph, dx=dx, dy=dy):
            u = ((t - t0) * 0.9 + ph) % 1.0; return ((c0[0] + dx + 0.15 * math.sin(u * 6 + ph * 9), c0[1] + dy, c0[2] + rise * u), (max(0.001, s * math.sin(PI * u)),) * 3)
        streak('Vapore', (s, s, s), G9['steam'], t0, t1, fn)
# aria calda del phon e vapore del pupazzo
for k in range(10):
    ph = k / 10; dy = er.uniform(-0.22, 0.22); dz = er.uniform(-0.25, 0.25)
    streak('AriaCalda', (0.16, 0.02, 0.02), G9['hot'], 0.0, 4.5, lambda t, ph=ph, dy=dy, dz=dz: ((-8.85 + 0.75 * ((t * 2.6 + ph) % 1.0), -1.27 + dy * ((t * 2.6 + ph) % 1.0), 1.22 + dz * ((t * 2.6 + ph) % 1.0) - 0.25 * ((t * 2.6 + ph) % 1.0)),))
steam(0.3, 4.5, (SNOWMAN[0], SNOWMAN[1], 1.0), n=7, s=0.17, rise=1.6)
# il sogno: fiocchi sopra la testa, poi il sole
for k in range(7):
    a0 = 2 * PI * k / 7
    def fn(t, a0=a0):
        dr = ramp(t, 9.0, 9.4); a = a0 + t * 1.2
        return ((-4.5 + 0.75 * math.cos(a), -1.6, 2.75 + 0.3 * math.sin(a) - 1.2 * dr), (max(0.001, 0.11 * ramp(t, 7.55 + 0.05 * (a0 * 7 / (2 * PI)), 7.8 + 0.05 * (a0 * 7 / (2 * PI))) * (1 - dr)),) * 3)
    streak('Fiocco', (0.11, 0.11, 0.11), G9['snow'], 7.5, 9.5, fn)
for k in range(5):
    def fn(t, k=k):
        u = ((t - 9.2) * 1.4 + k / 5) % 1.0; sx = -1 if k % 2 else 1
        return ((-4.5 + sx * (0.42 + 0.1 * u), -1.85, 1.75 - 0.7 * u), (0.035, 0.035, 0.06))
    streak('Sudore', (0.035, 0.035, 0.06), G9['puddle'], 9.2, 10.0, fn)
# cubetti di ghiaccio dal freezer, vapore del barbecue
burst('Cubetto', G9['ice'], 11.75, 1.0, (-7.85, -0.5, 0.55), 22, 1.4, (0.13, 0.13, 0.13), grav=5.5, up=0.9, vx=-1.3, mesh=set004.box_c())
steam(13.7, 15.1, (PILE[0], PILE[1], 0.3), n=7, s=0.2, rise=1.8)
# Gualtiero corre: polvere; rutto
for k in range(8): streak('Polvere', (0.1, 0.1, 0.1), M['dust'], 18.4 + 0.22 * k, 18.4 + 0.22 * k + 0.5, lambda t, t0=18.4 + 0.22 * k, p0=gp(18.4 + 0.22 * k)['loc']: ((p0[0], p0[1] - 0.3, 0.15 + 0.5 * (t - t0)), (max(0.001, 0.22 * math.sin(PI * min(1, (t - t0) / 0.5))),) * 3))
streak('Rutto', (0.1, 0.1, 0.1), N['stink'], 21.15, 21.9, lambda t: ((-3.05 + 0.5 * (t - 21.15), -3.15 - 0.6 * (t - 21.15), 1.62 + 0.25 * (t - 21.15)), (max(0.001, 0.05 + 0.25 * (t - 21.15)),) * 3))
# getto di neve del cannone
MUZ = 1.5; GJ = 5.9
for k in range(40):
    ph = k / 40; T = 1.35; sp = er.uniform(-0.06, 0.06); sv = er.uniform(0.93, 1.07); sz = er.uniform(0.05, 0.085)
    def fn(t, ph=ph, sp=sp, sv=sv, sz=sz):
        tau = ((t / T + ph) % 1.0) * T; tl = t - tau
        if tl < 22.55 or tl > 27.85: return ((0, 0, -80), (sz,) * 3)
        az, el = tube_dir(tl); az += sp; v = (5.2 + 1.8 * ramp(tl, 25.8, 26.2)) * sv
        m = (TUBE[0] + MUZ * math.cos(el) * math.cos(az), TUBE[1] + MUZ * math.cos(el) * math.sin(az), TUBE[2] + MUZ * math.sin(el))
        p = (m[0] + v * math.cos(el) * math.cos(az) * tau, m[1] + v * math.cos(el) * math.sin(az) * tau, m[2] + v * math.sin(el) * tau - 0.5 * GJ * tau * tau)
        if p[1] > 7.15 or p[2] < 0.03: return ((0, 0, -80), (sz,) * 3)
        return (p, (sz * (1 + 0.8 * tau),) * 3)
    streak('Neve', (0.07, 0.07, 0.07), G9['snow'], 22.55, 27.9, fn)
for k in range(7):                                                                                  # tubo flessibile
    u = (k + 0.5) / 7
    streak('Flessibile', (0.07, 0.07, 0.07), G9['hose'], 22.0, 27.9, lambda t, u=u: ((VAC[0] + (TUBE[0] - VAC[0]) * u, VAC[1] + (TUBE[1] - VAC[1]) * u, 0.56 + (TUBE[2] - 0.56) * u - 0.55 * math.sin(PI * u)),))
# nevica in salotto: sbuffi dalle finestre e dal camino
for (x, z) in ((-2.3, 1.6), (1.6, 1.6), (-1.9, 3.7), (1.9, 3.7), (0.0, 3.7)):
    burst('NeveCasa', G9['snow'], 27.0 + er.uniform(0, 0.25), 0.9, (x, 7.1, z), 7, 1.0, (0.12, 0.12, 0.12), grav=2.0, up=0.6, vx=0.0)
burst('NeveCasa', G9['snow'], 27.05, 0.85, (DOOR[0], DOOR[1] - 0.3, 1.0), 12, 1.6, (0.14, 0.14, 0.14), grav=3.0)
# il camion: polvere all'arrivo, polistirolo che scivola, palle sulla macchina
for k in range(6): streak('Polvere', (0.1, 0.1, 0.1), M['dust'], 30.2, 30.9, lambda t, k=k: ((-4.3 - 1.0 * k + 0.6 * (t - 30.2), -11.9, 0.12 + 0.4 * (t - 30.2)), (max(0.001, 0.15 * math.sin(PI * (t - 30.2) / 0.7)),) * 3))
for k in range(26):
    t0 = 31.1 + er.uniform(0, 1.0); y0 = er.uniform(-0.9, 0.9); s = er.uniform(0.16, 0.30); x1 = er.uniform(-13.8, -10.9)
    def fn(t, t0=t0, y0=y0, s=s, x1=x1):
        u = min(1.0, max(0.0, (t - t0) / 0.7)); return ((-9.6 + (x1 + 9.6) * u, -10.5 + y0, 2.3 + 1.6 * math.sin(PI * u) * 0.7 - 1.2 * u), (s,) * 3)
    streak('Polistirolo', (s, s, s), G9['snow'], t0, t0 + 0.7, fn)
for k in range(30):
    t0 = 33.0 + er.uniform(0, 3.2); x0 = er.uniform(-14.4, -10.8); y0 = er.uniform(-11.6, -9.6); s = er.uniform(0.14, 0.26)
    streak('Polistirolo', (s, s, s), G9['snow'], t0, t0 + 0.6, lambda t, t0=t0, x0=x0, y0=y0: ((x0, y0, 7.0 - 9.0 * (t - t0)),))
# nevica su tutto il quartiere
for k in range(150):
    x0 = er.uniform(-18, 1); y0 = er.uniform(-18, 3); ph = er.uniform(0, 1); spd = er.uniform(0.16, 0.26); s = er.uniform(0.045, 0.085); wob = er.uniform(0, 6)
    def fn(t, x0=x0, y0=y0, ph=ph, spd=spd, s=s, wob=wob):
        u = ((t - 31.2) * spd + ph) % 1.0
        return ((x0 + 0.35 * math.sin(t * 1.7 + wob), y0 + 0.25 * math.cos(t * 1.3 + wob), 9.5 * (1 - u)), (s * min(1.0, (t - 31.2) / 0.8 + 0.001),) * 3)
    streak('FioccoP', (s, s, s), G9['snow'], 31.2, TOTAL, fn)
for k in range(48):                                                                                 # chiazze bianche a terra
    x0 = er.uniform(-17.5, 0.5); y0 = er.uniform(-15.5, 3.0); r_ = er.uniform(0.5, 1.3); t0 = 31.6 + er.uniform(0, 3.0)
    o = obj('Chiazza', shared_mesh('sphere_lo'), (x0, y0, 0.01), (r_, r_ * er.uniform(0.6, 1.0), 0.05), G9['snow'], prc); o.rotation_euler = (0, 0, er.uniform(0, 3))
    show(o, [(t0, TOTAL)]); pop(o, t0, 0.5, over=1.05)

# ======================= camera =======================
def Z0(t): return (0, 0, 0)
def GW(t): return gp(t)['loc']
def TK(t): return (TX(t), 0, 0)
SHOTS = [  # t0, t1, sub cam, p0, p1, sub mira, a0, a1, lente, f
    (0.0, 1.5, Z0, (-6.7, -3.5, 1.35), (-6.9, -3.3, 1.35), Z0, (-9.2, -1.2, 1.3), (-9.2, -1.2, 1.3), 40, 5),
    (1.5, 4.6, Z0, (-5.5, -5.0, 1.25), (-5.7, -4.6, 1.25), Z0, (-8.45, -0.6, 1.0), (-8.45, -0.6, 1.0), 29, 6),
    (4.6, 7.4, Z0, (-9.2, -6.9, 1.3), (-9.2, -6.2, 1.3), Z0, (-9.2, -1.5, 1.25), (-9.2, -1.5, 1.25), 32, 6),
    (7.4, 10.0, Z0, (-4.3, -5.8, 1.3), (-4.3, -5.4, 1.3), Z0, (-4.5, -1.5, 1.9), (-4.5, -1.5, 1.95), 30, 6),
    (10.0, 13.0, Z0, (-5.2, -4.7, 1.3), (-5.4, -4.3, 1.3), Z0, (-7.3, -0.3, 0.95), (-7.6, -0.3, 0.9), 28, 6),
    (13.0, 15.1, Z0, (-6.2, -4.3, 1.3), (-6.4, -4.0, 1.3), Z0, (-9.0, -0.5, 1.05), (-9.0, -0.5, 1.05), 30, 6),
    (15.1, 18.2, Z0, (-2.4, -7.2, 2.9), (-2.8, -6.8, 2.7), Z0, (-5.5, -1.3, 0.55), (-5.5, -1.3, 0.55), 28, 8),
    (18.2, 20.4, Z0, (-5.4, -7.8, 2.3), (-5.4, -7.6, 2.2), GW, (0, 0, 0), (0, 0, 0), 26, 8),
    (20.4, 22.0, Z0, (-1.8, -5.3, 1.5), (-1.9, -5.1, 1.5), Z0, (-3.2, -2.8, 1.42), (-3.2, -2.8, 1.45), 40, 5),
    (22.0, 25.3, Z0, (-2.9, -5.1, 1.4), (-3.0, -4.8, 1.4), Z0, (-2.9, 1.0, 2.1), (-2.9, 1.0, 2.1), 24, 8),
    (25.3, 27.0, Z0, (-0.9, -2.3, 1.5), (-1.1, -2.1, 1.5), Z0, (-4.5, 1.4, 1.4), (-4.4, 1.5, 1.45), 35, 6),
    (27.0, 27.9, Z0, (-2.3, -0.2, 1.5), (-2.2, 0.3, 1.5), Z0, (-1.3, 7.0, 1.7), (-1.3, 7.0, 1.6), 24, 8),
    (27.9, 30.8, Z0, (-1.2, -15.6, 1.3), (-1.6, -15.2, 1.3), TK, (1.4, -10.5, 2.3), (1.4, -10.5, 2.3), 28, 8),
    (30.8, 33.0, Z0, (-3.5, -19.5, 4.5), (-4.0, -19.0, 4.3), Z0, (-9.0, -10.3, 2.3), (-9.3, -10.3, 2.2), 24, 8),
    (33.0, 36.5, Z0, (-10.9, -17.9, 1.4), (-11.1, -17.4, 1.4), Z0, (-12.4, -12.2, 1.45), (-12.4, -12.2, 1.5), 30, 6),
    (36.5, 38.5, Z0, (-11.3, -16.2, 0.9), (-11.4, -15.8, 0.9), Z0, (-12.25, -13.05, 1.7), (-12.2, -13.05, 1.8), 32, 6),
    (38.5, 39.0, Z0, (-9.8, -19.4, 1.2), (-9.8, -19.2, 1.2), Z0, (-10.2, -13.2, 2.4), (-10.2, -13.2, 2.4), 24, 8),
    (39.0, 39.8, Z0, (-2.6, -14.2, 3.3), (-2.7, -14.0, 3.3), Z0, (-4.3, -10.7, 3.7), (-4.3, -10.7, 3.7), 40, 6),
    (39.8, 44.1, Z0, (-9.2, -6.9, 1.3), (-9.2, -6.3, 1.3), Z0, (-9.2, -1.5, 1.3), (-9.2, -1.5, 1.3), 32, 6),
]
def GWz(t):
    g = gp(t)['loc']; return (g[0] * 0.55 - 2.6, -1.6, 0.7)
SHOTS[7] = (18.2, 20.4, Z0, (-5.4, -7.8, 2.3), (-5.4, -7.6, 2.2), GWz, (0, 0, 0), (0, 0, 0), 26, 8)
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
for o in bpy.data.objects: lin(o)
set_interp(camd, 'CONSTANT')
os.makedirs('../t009', exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath('../t009/pippo_t009.blend')); print('SAVED')
