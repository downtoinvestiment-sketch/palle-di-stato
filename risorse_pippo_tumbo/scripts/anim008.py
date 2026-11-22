"""Test 008 - PIPPO INSEGNA A VOLARE A SAMANTHA, LA GALLINA. Salva ../t008/pippo_t008.blend
Personaggi: modelli ESISTENTI (pippo.py, tumbo.py) invariati."""
import sys, math, os
sys.path.insert(0, os.path.dirname(__file__))
import bpy, numpy as np
from mathutils import Vector, Euler, Matrix
from common import *
from render_setup import *
import set004, props004, props006, props007, props008, pippo, tumbo
from set004 import obj, bx, cyl, ball_, MB

FPS = 24; TOTAL = 76.5; NF = int(TOTAL * FPS)
def fr(t): return max(1, int(round(t * FPS)) + 1)
def sm(x): x = min(1.0, max(0.0, x)); return x * x * (3 - 2 * x)
def ramp(t, a, b): return sm((t - a) / (b - a))
def lerp(a, b, u): return tuple(a[i] + (b[i] - a[i]) * u for i in range(len(a)))
def add(a, b): return tuple(a[i] + b[i] for i in range(3))
def eb_(u): u = min(1.0, max(0.0, u)); c1 = 1.6; return 1 + (c1 + 1) * (u - 1) ** 3 + c1 * (u - 1) ** 2
PI = math.pi

reset_scene(); scene = bpy.context.scene
setup_render(scene, 1080, 1920, samples=16, fps=FPS, frames=NF); scene.frame_end = NF
scene.eevee.shadow_resolution_scale = 0.25
rng = np.random.default_rng(41)
M = set004.make_mats(); K = props006.mats006(); N = props007.mats007(); H = props008.mats008()
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
sun = bpy.data.lights.new('Sun', 'SUN'); so = bpy.data.objects.new('Sun', sun); prc.objects.link(so)
so.rotation_euler = (math.radians(48), math.radians(6), math.radians(28)); sun.angle = math.radians(1.2); sun.energy = 3.9; sun.color = (1, 0.95, 0.85)
M['cloudw'] = material('S_cloudw', (1, 1, 1), rough=1.0, emit=(1, 1, 1), emit_strength=0.55)
M['dust'] = material('S_dust', (0.93, 0.88, 0.78), rough=1.0, emit=(0.9, 0.85, 0.75), emit_strength=0.3)
_cr = np.random.default_rng(11)
for k in range(26):
    an = k / 26 * 2 * PI + _cr.uniform(-0.15, 0.15); rr = _cr.uniform(90, 150); s_ = _cr.uniform(4.0, 7.5)
    cw = empty('CloudW', (rr * math.cos(an), rr * math.sin(an), _cr.uniform(24, 70)), None, prc)
    for (dx, dy, dz, r_) in [(0, 0, 0, 1.5), (1.5, 0.3, -0.2, 1.15), (-1.5, -0.2, -0.25, 1.2), (0.6, -0.5, 0.6, 1.1), (-0.6, 0.5, 0.5, 1.0), (2.6, 0, -0.45, 0.75), (-2.7, 0, -0.5, 0.8)]:
        c_, s2 = math.cos(an + PI / 2), math.sin(an + PI / 2)
        ball_('Puff', r_ * s_, (dx * s_ * c_, dx * s_ * s2 + dy, dz * s_), M['cloudw'], prc, parent=cw, sc=(1, 1, 0.6))

# ======================= ambiente: il giardino di Pippo =======================
bx('Prato', (-140, -140, -0.30), (140, 140, 0.0), M['park'], envc)
def house_at(x, y, rotz, wi, ri, si, two, w=None, d=None):
    w = w or rng.uniform(4.6, 5.6); d = d or rng.uniform(4.0, 4.8)
    mb = MB(set004.house_mats(M, wi, ri, si)); set004.house_geo(mb, w, d, 4.5 if two else 2.9, two, rng); return mb.build('Casa', envc, (x, y, 0), rotz)
house_at(0.0, 9.5, 0.0, 0, 0, 1, True, 6.5, 4.5)                                                  # casa di Pippo
house_at(-17.5, 3.0, PI / 2, 3, 0, 0, True, 5.6, 4.6)                                              # casa del vicino
for x in range(-34, 44, 9): house_at(x + rng.uniform(-1, 1), 27 + rng.uniform(0, 2), 0.0, int(rng.integers(0, 6)), int(rng.integers(0, 4)), int(rng.integers(0, 5)), bool(rng.integers(0, 2)))
for x in range(-34, 44, 9): house_at(x + rng.uniform(-1, 1), -35 - rng.uniform(0, 2), PI, int(rng.integers(0, 6)), int(rng.integers(0, 4)), int(rng.integers(0, 5)), bool(rng.integers(0, 2)))
for y in range(-18, 20, 9): house_at(21 + rng.uniform(0, 2), y, -PI / 2, int(rng.integers(0, 6)), int(rng.integers(0, 4)), int(rng.integers(0, 5)), bool(rng.integers(0, 2)))
for y in range(-24, -6, 9): house_at(-24 - rng.uniform(0, 2), y, PI / 2, int(rng.integers(0, 6)), int(rng.integers(0, 4)), int(rng.integers(0, 5)), bool(rng.integers(0, 2)))
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
for (x, y) in ((12.5, 5.0), (13.0, -6.5), (-13.0, 9.5), (-12.5, -9.5), (5.5, 15.5), (-7, 16.5), (16, 14), (-30, 14), (30, -14)): tree(x, y, rng.uniform(1.0, 1.5))
HEDGE_X = 7.6
bx('Siepe', (HEDGE_X, -7.0, 0.0), (HEDGE_X + 1.8, 8.0, 2.1), M['hedge'], envc)
fm = MB([M['frame']])
for yy in np.arange(-8.0, 8.01, 0.22): fm.box((-9.2, yy, 0.42), (0.04, 0.10, 0.84), 0); fm.box((-9.2, yy, 0.86), (0.04, 0.07, 0.08), 0)
for zz in (0.25, 0.60): fm.box((-9.23, 0, zz), (0.03, 16.1, 0.06), 0)
fm.build('StaccionataVicino', envc)
STY, STH = 6.15, 4.3
stair, STEPS = props008.stairs(envc, H, -7.0, -2.0, STY, STH)

# ======================= personaggi =======================
P = pippo.build_pippo(chc); Tb = tumbo.build_tumbo(chc, scale=0.75)
for r in (P['root'], Tb['root']): r.rotation_mode = 'XYZ'
for nm in 'LR': P['shoulder' + nm].rotation_mode = 'QUATERNION'
def qdir(d, rest=(0, 0, -1)): return Vector(rest).rotation_difference(Vector(d).normalized())
man = props004.player(chc, 'Neigh', (0.96, 0.96, 0.96), (0.25, 0.25, 0.30), (0.96, 0.42, 0.36), (0.15, 0.10, 0.07), scale=1.0)
mhead = [c for c in man['root'].children if c.name.startswith('Head')][0]
for sx in (-1, 1): obj('Brow', set004.box_c(), (sx * 0.10, -0.25, 0.15), (0.13, 0.03, 0.035), M['dark'], chc, rot=(0, sx * 0.12, 0), parent=mhead)
man['root'].location = (-9.95, -1.0, 0); man['root'].rotation_euler = (0, 0, PI / 2)
for nm in 'LR': man['shoulder' + nm].rotation_euler = (-1.05, 0, 0)
S = props008.chicken(chc, H); SR = S['root']

# ======================= oggetti =======================
cap = props008.cap(prc, H, P['head'])
capf = props008.cap(prc, H, None); capf.location = (0.75, -2.35, 0.0); capf.rotation_euler = (0.3, 0.2, 1.0)
namesign = props007.sign(prc, N, 'SAMANTHA', w=1.25, h=0.36, size=0.19, post=1.05); namesign.location = (0.55, -0.35, 0); namesign.rotation_euler = (0, 0, 0.45)
TVP = (0.4, 2.3)
tvr, falco, fwings = props008.tv(prc, H); tvr.location = (TVP[0], TVP[1], 0)
REM = (0.25, 0.35)
rem = props008.remote(prc, H); rem.location = (REM[0], REM[1], 0.0); rem.rotation_euler = (0, 0, 0.4)
egg = ball_('Uovo', 0.075, (REM[0], REM[1], 0.105), H['egg'], prc, sc=(1, 1, 1.3))
BOWL = (3.0, -1.2)
bowl = props008.bowl(prc, H); bowl.location = (BOWL[0], BOWL[1], 0)
FAN = (-5.7, -1.6)
fanr, blades = props008.fan(prc, H); fanr.location = (FAN[0], FAN[1], 0)
feather = obj('Piuma', set004.box_c(), (0, 0, -40), (0.09, 0.26, 0.012), H['feather'], prc)

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
show(cap, [(7.9, 64.25)]); pop(cap, 7.9); show(capf, [(64.25, TOTAL)])
show(namesign, [(6.9, 9.9)]); pop(namesign, 6.9)
show(tvr, [(10.3, 16.9)]); pop(tvr, 10.3); show(rem, [(10.3, 16.9)]); show(egg, [(15.8, 16.9)]); pop(egg, 15.8, 0.25)
show(bowl, [(30.6, 41.5)]); show(fanr, [(41.5, 51.6)]); pop(fanr, 41.6)
for c_ in (S['cardL'], S['cardR']): show(c_, [(33.5, 41.5)]); pop(c_, 33.5)
show(man['root'], [(16.9, 30.6), (62.2, TOTAL)]); show(feather, [(73.4, TOTAL)])

# ======================= pose =======================
DOWN = lambda s: (s * 0.14, 0, -1)
HUG = dict(aL=(0.25, -0.95, 0.05), aR=(-0.25, -0.95, 0.05)); UP = dict(aL=(-0.2, -0.25, 1), aR=(0.2, -0.25, 1))
def stair_pos(u):
    """u in [0,1] lungo la scala, poi [1,2] sul pianerottolo fino a (0.6)."""
    if u <= 1.0: return (-7.0 + 5.0 * u, STY, STH * u)
    return (-2.0 + 2.6 * min(1.0, u - 1.0), STY, STH)
SIT = (0.0, -1.6)
def pp(t):
    S_ = dict(loc=(0, 0, 0), rot=(0, 0, 0), aL=DOWN(-1), aR=DOWN(1), hL=0.0, hR=0.0, head=(0, 0, 0))
    if t < 6.0:                                    # trova la gallina e decide che è un'aquila
        u = ramp(t, 3.7, 4.3)
        S_.update(loc=(-0.3, -1.4, 0), rot=(0.38 * (1 - u), 0, PI / 2 - 1.15 * u), aL=lerp((-0.75, -0.25, -0.6), UP['aL'], u), aR=lerp((0.75, -0.25, -0.6), UP['aR'], u), head=(-0.25 * u, 0.15 * math.sin(t * 2.5) * (1 - u), 0))
    elif t < 9.9:                                  # la battezza
        u = ramp(t, 8.6, 8.9); S_.update(loc=(-0.3, -1.4, 0), rot=(0, 0, 0.35), aR=lerp((0.9, -0.3, -0.2), (0.3, -0.2, 1.0), u), aL=(-0.75, -0.25, -0.6), head=(-0.2 * u, 0, -0.3 * (1 - u)))
    elif t < 16.9:                                 # lezione 1: il documentario
        u = ramp(t, 15.9, 16.3)
        S_.update(loc=(-1.15, 1.7, 0), rot=(0, 0, PI / 2 - 0.5), aR=lerp((0.5, -0.8, 0.35 + 0.08 * math.sin(t * 6)), (-0.25, -0.6, 0.8), u), aL=(-0.75, -0.25, -0.6), head=(0.3 * ramp(t, 14.7, 15.0), 0, 0.4 * ramp(t, 14.7, 15.0)))
    elif t < 30.6:                                 # lezione 2: la rincorsa
        if t < 19.2: k = math.sin(t * 5); S_.update(loc=(-6.0, -2.2, 0), rot=(0, 0.2 * k, 0.3), aL=(-0.9, 0, 0.5 * k), aR=(0.9, 0, -0.5 * k))
        elif t < 23.7:
            if t < 21.4: x = -6.0 + 12.0 * (t - 19.2) / 2.2; yaw = PI / 2
            elif t < 21.65: x = 6.0; yaw = PI / 2 + PI * (t - 21.4) / 0.25
            else: x = 6.0 - 7.5 * (t - 21.65) / 2.05; yaw = -PI / 2
            a = 0.2 + 0.85 * math.sin(t * 22); k = math.sin(t * 20)
            S_.update(loc=(x, -2.2, 0.08 * abs(k)), rot=(0.15, 0, yaw), aL=(-math.cos(a), 0, math.sin(a)), aR=(math.cos(a), 0, math.sin(a)), hL=0.8 * k, hR=-0.8 * k)
        else:
            b = 0.05 * abs(math.sin(t * 9)) * (1 - ramp(t, 27.5, 28.8))
            hz = 0.5 * ramp(t, 24.0, 24.3) - 0.2 * ramp(t, 25.3, 25.6) - 1.1 * ramp(t, 26.6, 26.9) + 0.8 * ramp(t, 28.6, 28.9)
            S_.update(loc=(-1.5, -2.2, b), rot=(0.12, 0, 0.0), aL=(-0.35, -0.2, -0.9), aR=(0.35, -0.2, -0.9), head=(0.1, 0, hz))
    elif t < 41.5:                                 # lezione 3: le ali di cartone
        u = ramp(t, 34.6, 34.85); v = ramp(t, 34.9, 35.05)
        S_.update(loc=(0.6, -1.2, 0), rot=(0, 0, 0.5 + (PI / 2 - 0.5) * ramp(t, 34.3, 34.7)), aL=lerp(lerp(HUG['aL'], UP['aL'], u), (-0.2, -1, 0.2), v), aR=lerp(lerp(HUG['aR'], UP['aR'], u), (0.2, -1, 0.2), v))
        if t > 36.4: d = ramp(t, 36.4, 36.7); S_.update(aL=lerp((-0.2, -1, 0.2), (-0.3, 0.3, -0.9), d), aR=lerp((0.2, -1, 0.2), (0.3, 0.3, -0.9), d), head=(0.15, 0, 0.3 * math.sin(t * 2.5)))
    elif t < 51.6:                                 # lezione 4: il vento
        if t < 47.6:
            j = 0.03 * math.sin(t * 40) * ramp(t, 44.2, 45.5)
            S_.update(loc=(-2.0 + j, -1.6, 0), rot=(0.18 * ramp(t, 44.2, 45.5), 0, -PI / 2), aR=lerp((0.3, -0.9, 0.2), (0.3, -0.3, 1.0), ramp(t, 45.0, 45.3)), aL=(-0.5, -0.4, -0.7))
        elif t < 49.3:
            u = (t - 47.6) / 1.7; f = max(0.0, (t - 48.1) / 1.2)
            x = -2.0 + 0.6 * ramp(t, 47.6, 48.1) + (HEDGE_X - 0.6 + 1.4) * f; z = 4 * 1.9 * f * (1 - f) + 1.3 * f
            S_.update(loc=(x, -1.6, z), rot=(0.18 - 14.0 * f, 0, -PI / 2), aL=(-1, 0, 0.3 * math.sin(t * 30)), aR=(1, 0, -0.3 * math.sin(t * 30)), hL=0.6 * math.sin(t * 25), hR=-0.6 * math.sin(t * 25))
        else:                                      # piantato nella siepe, gambe a elica
            ph = (t - 49.3) * 9.0 * math.exp(-(t - 49.3) * 0.35)
            S_.update(loc=(HEDGE_X - 0.75, -1.6, 1.25), rot=(PI / 2, 0, PI / 2), hL=ph, hR=ph + PI, aL=(-0.3, 0, 1), aR=(0.3, 0, 1))
    elif t < 62.2:                                 # lezione 5: il lancio dal tetto
        if t < 54.2: S_.update(loc=(-7.6, STY, 0), rot=(0, 0, PI / 2), **HUG)
        elif t < 56.1:
            u = (t - 54.2) / 1.3; l = stair_pos(min(2.0, u * 1.0 if u <= 1 else 1.0 + (t - 55.5) / 0.45)); k = math.sin(t * 18)
            S_.update(loc=(l[0], l[1] - 0.05, l[2] + 0.04 * abs(k)), rot=(0, 0, PI / 2 * (1 - ramp(t, 55.9, 56.1))), hL=0.5 * k, hR=-0.5 * k, **HUG)
        else:
            pump = abs(math.sin((t - 56.1) * PI / 0.233)) if t < 56.8 else 0; out_ = ramp(t, 56.8, 57.05)
            S_.update(loc=(0.6, STY - 0.25, STH), aL=lerp(lerp(HUG['aL'], (0.2, -0.8, 0.5), pump), (-0.2, -1, 0.05), out_), aR=lerp(lerp(HUG['aR'], (-0.2, -0.8, 0.5), pump), (0.2, -1, 0.05), out_),
                      head=(0.25 * ramp(t, 58.0, 58.4), 0, -1.2 * ramp(t, 57.5, 57.9)))
            if t > 59.4: d = ramp(t, 59.4, 59.8); S_.update(aL=lerp((-0.2, -1, 0.05), DOWN(-1), d), aR=lerp((0.2, -1, 0.05), DOWN(1), d))
    else:                                          # si arrende e si siede
        sit = ramp(t, 63.7, 64.2); up = ramp(t, 68.3, 68.7)
        S_.update(loc=(SIT[0], SIT[1], -0.58 * sit), rot=(0.28 * sit * (1 - 0.8 * up), 0, PI / 2), hL=-PI / 2 * sit, hR=-PI / 2 * sit, aL=lerp(DOWN(-1), (-0.35, -0.5, -0.8), sit), aR=lerp(DOWN(1), (0.35, -0.5, -0.8), sit))
        hy = 0.35 * sit * (1 - ramp(t, 66.9, 67.3)) - 0.55 * ramp(t, 69.3, 70.0) + 0.55 * ramp(t, 72.6, 72.9)
        S_['head'] = (hy, 0, 2.3 * ramp(t, 69.8, 70.5) * (1 - ramp(t, 72.4, 72.8)) - 0.5 * ramp(t, 72.9, 73.2))
    return S_
def pM(t): s = pp(t); return Matrix.Translation(s['loc']) @ Euler(s['rot'], 'XYZ').to_matrix().to_4x4()
def carried(t, off, pitch=0.0):
    m = pM(t) @ Matrix.Translation(off) @ Euler((pitch, 0, 0), 'XYZ').to_matrix().to_4x4(); l = m.to_translation(); e = m.to_euler('XYZ'); return (l.x, l.y, l.z), (e.x, e.y, e.z)
REST = -1.15
def fly_pos(t): tau = t - 69.3; return (1.4 - 2.0 * tau - 2.5 * tau * tau, -1.6 + 0.25 * tau, 0.25 + 2.4 * tau + 0.9 * tau * tau)
def ck(t):
    """Samantha: loc, rot, ala (angolo), testa (beccheggio, rollio, imbardata)."""
    C = dict(loc=(0, 0, 0), rot=(0, 0, 0), wing=REST, head=(0, 0, 0))
    peck = lambda sp=7.0: (0.9 * max(0.0, math.sin(t * sp)) ** 2, 0, 0)
    if t < 3.75: C.update(loc=(0.9, -1.4, 0), rot=(0, 0, -PI / 2 + 0.5), head=peck())
    elif t < 6.0:
        u = ramp(t, 3.75, 4.35); l, r = carried(t, (0, -0.25, 2.25)); l0 = (0.9, -1.4, 0)
        C.update(loc=lerp(l0, l, u), rot=(0, 0, lerp((-PI / 2 + 0.5,), (r[2],), u)[0]), wing=REST + (REST * -1 + 0.15) * ramp(t, 4.4, 4.8), head=(0, 0.35 * math.sin(t * 5), 0))
    elif t < 9.9: C.update(loc=(0.9, -1.6, 0), rot=(0, 0, 0.3), head=(0, 0.4 * math.sin(t * 2.2), 0.3 * math.sin(t * 1.3)))
    elif t < 16.9:
        back = ramp(t, 14.7, 15.0); fwd = ramp(t, 15.8, 16.15); sq = ramp(t, 15.15, 15.35) * (1 - ramp(t, 15.65, 15.8))
        C.update(loc=(0.28, 0.75 - 0.42 * back + 0.62 * fwd, -0.07 * sq + 0.04 * abs(math.sin(t * 20)) * (back * (1 - back) * 4 + fwd * (1 - fwd) * 4)), rot=(0, 0.1 * math.sin(t * 30) * sq, PI), head=(0, 0.35 * math.sin(t * 1.8) * (1 - back), 0),
                 wing=REST + 0.3 * sq * abs(math.sin(t * 25)))
    elif t < 30.6:
        px = pp(t)['loc'][0]; C.update(loc=(0.2, -0.6, 0), rot=(0, 0, 0), head=(0, 0, max(-1.2, min(1.2, -math.atan2(px - 0.2, 1.6)))) if t < 28.6 else peck(5))
    elif t < 34.9:
        ov = ramp(t, 34.6, 34.85); l, r = carried(t, lerp((0, -0.45, 0.66), (0, -0.25, 2.25), ov))
        C.update(loc=l, rot=(0, 0, r[2]), head=(0, 0.3 * math.sin(t * 4), 0), wing=REST + 1.6 * ramp(t, 33.5, 33.8))
    elif t < 36.4:
        l0, r0 = carried(34.9, (0, -0.25, 2.25))
        if t < 35.9: u = (t - 34.9) / 1.0; C.update(loc=(l0[0] + 0.5 + 1.0 * u, -1.2, 2.1 - 0.25 * u + 0.08 * math.sin(t * 30)), rot=(-0.15, 0, PI / 2), wing=0.05 + 0.75 * math.sin(t * 38))
        else: u = (t - 35.9) / 0.5; C.update(loc=(l0[0] + 1.5 + (BOWL[0] - l0[0] - 1.5) * u, -1.2, 1.85 - 1.3 * u * u), rot=(2.3 * u, 0, PI / 2), wing=0.3)
    elif t < 41.5:
        k = math.sin(t * 17) * math.exp(-(t - 36.4) * 0.5)
        C.update(loc=(BOWL[0] + 0.05, -1.2, 0.86), rot=(2.75, 0.25 * k, PI / 2), wing=0.2 + 0.5 * k)
    elif t < 51.6:
        wv = ramp(t, 44.2, 45.5); C.update(loc=(-3.6, -1.6, 0), rot=(-0.12 * wv, 0, -PI / 2), wing=REST + 0.12 * wv * math.sin(t * 45), head=(0, 0, -2.4 * ramp(t, 48.3, 48.8)))
    elif t < 57.3:
        pump = abs(math.sin((t - 56.1) * PI / 0.233)) if 56.1 <= t < 56.8 else 0; out_ = ramp(t, 56.8, 57.05)
        l, r = carried(t, lerp(lerp((0, -0.45, 0.66), (0, -0.42, 1.25), pump), (0, -0.80, 1.05), out_))
        C.update(loc=l, rot=(0, 0, r[2]), head=(0, 0.3 * math.sin(t * 4), 0))
    elif t < 59.4:
        if t < 57.45: u = (t - 57.3) / 0.15; C.update(loc=(0.6 - 0.5 * u, STY - 1.05 + 1.0 * u, STH + 1.05 * (1 - u) + 0.3 * math.sin(PI * u)), rot=(0, 0, -PI / 2 * u))
        elif t < 57.75: u = (t - 57.45) / 0.30; C.update(loc=(0.1 - 1.95 * u, STY, STH + 0.05 * abs(math.sin(t * 30))), rot=(0, 0.12 * math.sin(t * 30), -PI / 2))
        else:
            q = (t - 57.75) / 0.10; k = min(15, int(q)); u = q - k if k < 15 or q < 16 else 1.0
            a = STEPS[15 - k]; b = STEPS[15 - k - 1] if k < 15 else (-7.5, 0.0)
            C.update(loc=(a[0] + (b[0] - a[0]) * u, STY, a[1] + (b[1] - a[1]) * u + 0.22 * math.sin(PI * u)), rot=(0, 0, -PI / 2), wing=REST + 0.5 * math.sin(PI * u))
    elif t < 62.2: u = ramp(t, 59.5, 60.5); C.update(loc=(-7.5 - 0.6 * u, STY - 1.6 * u, 0), rot=(0, 0, -PI / 2 + 1.4 * u), head=peck(8))
    elif t < 69.3:
        op = ramp(t, 68.2, 68.5); fl = math.sin((t - 68.5) * 2 * PI / 0.4) if t > 68.5 else 0
        C.update(loc=(1.4, -1.6, 0.06 * abs(fl) * (t > 68.5)), rot=(-0.1 * op, 0, -PI / 2), wing=REST + (0.25 - REST) * op + 0.6 * fl, head=peck() if t < 66.8 else (0, 0.45 * (1 - op), 0))
    else:
        tau = t - 69.3; fl = math.sin(tau * 2 * PI / (0.28 if tau < 1.6 else 0.9)); glide = ramp(t, 70.9, 71.3)
        C.update(loc=fly_pos(t), rot=(-0.28 + 0.2 * glide, 0.12 * math.sin(tau * 1.3) * glide, -PI / 2), wing=0.15 + (0.7 - 0.45 * glide) * fl)
    return C

def tp(t):
    S_ = dict(loc=(0, 0, 0), rot=(0, 0, 0), legs=dict(FL=0, FR=0, BL=0, BR=0), head=(0, 0, 0), tail=-1.0 + 0.5 * math.sin(t * 12))
    if t < 9.9: S_.update(loc=(2.5, -2.5, 0), rot=(0, 0, -1.0), head=(-0.2, 0.25 * math.sin(t * 1.8), 0.3))
    elif t < 16.9: S_.update(loc=(2.3, 0.4, 0), rot=(0, 0, PI - 0.5), head=(-0.25, 0, 0.9 * ramp(t, 15.0, 15.4)))
    elif t < 30.6:
        px = pp(t)['loc'][0]; S_.update(loc=(1.7, -0.7, 0), rot=(0, 0, 0.0), head=(-0.1, 0, max(-1.1, min(1.1, -math.atan2(px - 1.7, 1.5))) if t < 28.6 else 0.0))
    elif t < 41.5:
        st = ramp(t, 36.4, 36.55) * (1 - ramp(t, 36.9, 37.2)); off = ramp(t, 38.6, 39.2)
        S_.update(loc=(4.0 + 0.4 * st + 0.3 * off, -0.9 - 0.2 * off, 0.3 * st), rot=(0, 0, -PI / 2 - 0.3 + 2.4 * off), head=(0.35 * (1 - off) - 0.55 * off, 0, -0.5 * (1 - off)), tail=-1.0 if off < 0.5 else -0.2)
    elif t < 51.6: S_.update(loc=(-4.3, -3.7, 0), rot=(0, 0, 2.2), head=(-0.2, 0, 0.6 - 2.2 * ramp(t, 48.2, 48.9)))
    elif t < 62.2: S_.update(loc=(-4.6, 2.6, 0), rot=(0, 0, PI - 0.4), head=(-0.65 * (1 - ramp(t, 58.6, 59.2)), 0, -0.8 * ramp(t, 58.6, 59.2)))
    else: S_.update(loc=(-0.95, -2.55, 0), rot=(0, 0, PI / 2 - 0.5 - 0.9 * ramp(t, 73.0, 73.5)), head=(-0.5 * ramp(t, 69.4, 70.0) * (1 - ramp(t, 72.6, 73.0)), 0, 1.6 * ramp(t, 69.9, 70.6) * (1 - ramp(t, 72.6, 73.0))))
    return S_

# ======================= chiavi =======================
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
    Tb['head'].rotation_euler = q['head']; Tb['head'].keyframe_insert('rotation_euler', frame=f)
    Tb['tail'].rotation_euler = (q['tail'], 0, 0.5 * math.sin(t * 14) * (0 if 38.6 < t < 41.5 else 1)); Tb['tail'].keyframe_insert('rotation_euler', frame=f)
    c = ck(t); SR.location = c['loc']; SR.rotation_euler = c['rot']; SR.keyframe_insert('location', frame=f); SR.keyframe_insert('rotation_euler', frame=f)
    S['wingL'].rotation_euler = (0, c['wing'], 0); S['wingR'].rotation_euler = (0, -c['wing'], 0); S['head'].rotation_euler = c['head']
    for nm in ('wingL', 'wingR', 'head'): S[nm].keyframe_insert('rotation_euler', frame=f)
    # vicino: segue Pippo con la testa
    px, py = s['loc'][0], s['loc'][1]; mhead.rotation_euler = (0, 0, max(-1.0, min(1.0, -math.atan2(py + 1.0, px + 9.95))) if t < 62 else 0.0); mhead.keyframe_insert('rotation_euler', frame=f)
    # documentario: il falco plana sullo schermo
    falco.location = (-0.08 + 0.22 * math.sin(t * 1.3), -0.325, 0.96 + 0.10 * math.sin(t * 2.1)); falco.keyframe_insert('location', frame=f)
    for sgn, w_ in zip((-1, 1), fwings): w_.rotation_euler = (0, sgn * (1.1 + 0.45 * math.sin(t * 9)), 0); w_.keyframe_insert('rotation_euler', frame=f)
    # ventilatore
    spd = ramp(t, 43.7, 45.4); blades.rotation_euler = (55.0 * max(0.0, t - 43.7) * (0.3 + 0.7 * spd), 0, 0); blades.keyframe_insert('rotation_euler', frame=f)
    # piuma che cade sul naso
    u = ramp(t, 73.4, 74.7); hp_ = (0.47, -1.84, 1.13)
    feather.location = (hp_[0] + 0.5 * math.sin(t * 4) * (1 - u), hp_[1], hp_[2] + 3.2 * (1 - u)); feather.rotation_euler = (0.4 * math.sin(t * 5) * (1 - u), 0.6 * math.sin(t * 4) * (1 - u), t * 2 * (1 - u))
    feather.keyframe_insert('location', frame=f); feather.keyframe_insert('rotation_euler', frame=f)

_lastP = [None, -1.0]; _lastT = [None, -1.0]
def pex(t, **k):
    if _lastP[0] is not None and t - 0.06 > _lastP[1]: pippo.express(P, fr(t - 0.06), **_lastP[0])
    pippo.express(P, fr(t), **k); _lastP[0] = k; _lastP[1] = t
def tex(t, **k):
    if _lastT[0] is not None and t - 0.06 > _lastT[1]: tumbo.tumbo_express(Tb, fr(t - 0.06), **_lastT[0])
    tumbo.tumbo_express(Tb, fr(t), **k); _lastT[0] = k; _lastT[1] = t
pex(0.0, brow_lift=0.6, eye_scale=1.15, mouth_open=0.3, look=(0.5, -0.5)); pex(3.8, smile=1.0, brow=0.8, eye_scale=1.2, mouth_open=0.6); pex(6.6, smile=0.9, brow=0.5)
pex(8.7, smile=1.0, brow=0.8, look=(0, 0.6)); pex(10.0, smile=0.8, brow=0.6); pex(12.2, smile=1.0, brow_lift=0.4, look=(0.6, 0)); pex(14.8, brow_lift=0.5, mouth_open=0.3, look=(0.4, -0.6))
pex(16.0, brow=1.0, eye_open=0.3); pex(17.2, smile=0.9, brow=0.9); pex(19.3, smile=1.0, mouth_open=0.8, brow=0.7); pex(23.8, mouth_open=0.7, brow_lift=0.3, eye_open=0.8)
pex(26.7, mouth_open=0.2, brow_lift=0.5, eye_scale=1.1); pex(28.9, mouth_open=0.0, brow_lift=0.2, eye_open=1.0, look=(0, 0)); pex(30.9, smile=0.9, brow=0.8)
pex(33.5, smile=1.0, brow=0.6, look=(0, -0.5)); pex(34.9, smile=1.0, mouth_open=0.7, brow_lift=0.6, eye_scale=1.2); pex(36.4, brow=-0.7, brow_lift=0.6, eye_open=0.4, mouth_open=0.5)
pex(38.4, brow=-0.5, brow_lift=0.5, smile=0.4, look=(0.7, -0.3)); pex(41.7, smile=0.9, brow=0.9); pex(45.0, smile=1.0, brow=0.6, mouth_open=0.4); pex(46.2, brow_lift=0.5, mouth_open=0.2, eye_scale=1.1)
pex(47.6, brow=-0.8, brow_lift=0.7, eye_scale=1.3, mouth_open=1.0); pex(49.3, eye_open=0.08); pex(51.9, smile=0.7, brow=1.0); pex(56.1, smile=0.9, brow=1.0, eye_open=0.8)
pex(56.85, eye_open=0.05, smile=0.6, brow_lift=0.4); pex(57.6, eye_open=1.0, brow_lift=0.4, mouth_open=0.0, look=(-0.8, -0.3)); pex(59.5, brow=1.0, eye_open=0.6, look=(-0.6, -0.6))
pex(62.4, brow=-0.5, brow_lift=0.3, eye_open=0.7); pex(64.3, eye_open=0.4, brow=-0.6, brow_lift=0.2, mouth_open=0.1, look=(0, -0.6)); pex(67.0, eye_open=0.8, look=(0.5, -0.2), brow_lift=0.3)
pex(68.4, eye_scale=1.25, eye_open=1.2, brow_lift=0.8, mouth_open=0.5); pex(69.4, eye_scale=1.35, brow_lift=0.9, mouth_open=1.0, look=(0, 0.7)); pex(72.9, brow=1.0, eye_open=0.55, mouth_open=0.0, look=(0, 0))
tex(0.0, tongue=0.5); tex(3.9, eye_scale=1.2); tex(10.0, tongue=0.3); tex(15.9, eye_scale=1.3); tex(17.2, tongue=0.6); tex(28.9, eye_open=1.0, eye_scale=1.1)
tex(31.0, tongue=0.7, look=(-0.4, -0.3)); tex(36.4, eye_scale=1.45, brow=-0.6); tex(38.5, brow=1.0, eye_open=0.5); tex(39.3, brow=1.0, eye_open=0.12)
tex(41.7, tongue=0.3); tex(48.2, eye_scale=1.3); tex(51.9, tongue=0.4); tex(58.0, eye_scale=1.2); tex(62.4, tongue=0.2, eye_open=0.8); tex(69.4, eye_scale=1.4); tex(73.2, eye_open=0.7, brow=0.5)

# ======================= effetti =======================
def streak(name, sc, mat, t0, t1, fn, parent=None, mesh=None, rot=None):
    o = obj(name, mesh or shared_mesh('sphere_lo'), (0, 0, -80), sc, mat, prc, parent=parent)
    if rot: o.rotation_euler = rot
    o.hide_render = True; o.keyframe_insert('hide_render', frame=1); o.hide_render = False; o.keyframe_insert('hide_render', frame=fr(t0)); o.hide_render = True; o.keyframe_insert('hide_render', frame=fr(t1))
    for f in range(fr(t0), fr(t1) + 1):
        r_ = fn((f - 1) / FPS); o.location = r_[0]; o.keyframe_insert('location', frame=f)
        if len(r_) > 1: o.scale = r_[1]; o.keyframe_insert('scale', frame=f)
    return o
er = np.random.default_rng(3)
def burst(name, mat, t0, dur, c0, n, vmax, sc, grav=4.9, up=1.0):
    for k in range(n):
        v = np.array([er.uniform(-vmax, vmax), er.uniform(-vmax, vmax), er.uniform(0.3, 1.0) * vmax * up])
        streak(name, sc, mat, t0, t0 + dur, lambda t, v=v: ((c0[0] + v[0] * (t - t0), c0[1] + v[1] * (t - t0), max(0.03, c0[2] + v[2] * (t - t0) - grav * (t - t0) ** 2)),))
def puffs(t0, c0, n=7, r=1.6, s=0.15, dur=0.6):
    for k in range(n):
        an = k / n * 6.283
        streak('Polvere', (0.1, 0.1, 0.1), M['dust'], t0, t0 + dur, lambda t, an=an: ((c0[0] + (0.3 + r * (t - t0)) * math.cos(an), c0[1] + (0.3 + r * (t - t0)) * math.sin(an) * 0.7, c0[2] + 0.6 * (t - t0)),
                                                                                      (max(0.001, s * math.sin(PI * min(1, (t - t0) / dur))),) * 3))
for k in range(9):                                  # raggi di gloria attorno alla gallina-aquila
    a = k / 9 * 2 * PI
    streak('Raggio', (0.03, 0.03, 0.03), N['spark'], 4.4, 6.0, lambda t, a=a: ((-0.3 + (0.75 + 0.2 * math.sin(t * 6 + a)) * math.cos(a), -1.75, 2.55 + (0.75 + 0.2 * math.sin(t * 6 + a)) * math.sin(a)), (0.05 + 0.03 * math.sin(t * 8 + a),) * 3))
burst('Crocchetta', H['kibble'], 36.4, 1.1, (BOWL[0], BOWL[1], 0.3), 14, 2.6, (0.045, 0.045, 0.035))
burst('PiumaB', H['feather'], 36.4, 1.2, (BOWL[0], BOWL[1], 0.5), 6, 1.8, (0.05, 0.11, 0.01), grav=1.5)
for k in range(16):                                 # vento del ventilatore
    ph = er.uniform(0, 1); dy = er.uniform(-0.75, 0.75); dz = er.uniform(0.35, 1.95)
    streak('Vento', (0.55, 0.02, 0.02), M['cloudw'], 44.0, 51.6, lambda t, ph=ph, dy=dy, dz=dz: ((FAN[0] + 0.5 + 13.0 * ((t * 1.25 + ph) % 1.0), FAN[1] + dy * (1 + 0.6 * ((t * 1.25 + ph) % 1.0)), dz), (0.55 * ramp(t, 44.0, 45.4) + 0.001, 0.02, 0.02)))
burst('Foglia', M['leaf'][0], 49.3, 1.3, (HEDGE_X, -1.6, 1.3), 10, 3.0, (0.15, 0.15, 0.05)); burst('Foglia', M['leaf'][1], 49.3, 1.3, (HEDGE_X, -1.6, 1.5), 8, 3.0, (0.13, 0.13, 0.05))
puffs(64.2, (SIT[0], SIT[1], 0.1), s=0.12); burst('PiumaB', H['feather'], 69.3, 1.6, (1.4, -1.6, 0.5), 8, 1.6, (0.05, 0.11, 0.01), grav=1.2)
streak('Rotolante', (0.22, 0.22, 0.22), M['leaf'][2], 28.7, 30.6, lambda t: ((6.5 - 6.5 * (t - 28.7), -3.6, 0.22 + 0.12 * abs(math.sin(t * 9))),))

# ======================= camera =======================
def PW(t): return pp(t)['loc']
def CK(t): return ck(t)['loc']
def Z0(t): return (0, 0, 0)
def PX(t): return (pp(t)['loc'][0] * 0.65, 0, 0)
SHOTS = [  # t0, t1, sub cam, p0, p1, sub mira, a0, a1, lente, f
    (0.0, 3.7, Z0, (2.7, -4.5, 0.7), (2.4, -4.1, 0.75), Z0, (0.25, -1.4, 0.8), (0.3, -1.4, 0.8), 35, 4),
    (3.7, 6.0, Z0, (1.3, -5.2, 0.9), (1.0, -4.6, 1.0), Z0, (-0.3, -1.4, 1.9), (-0.3, -1.4, 2.1), 28, 8),
    (6.0, 9.9, Z0, (2.6, -4.9, 0.85), (2.2, -4.5, 0.95), Z0, (0.55, -1.5, 1.0), (0.5, -1.5, 1.05), 30, 5),
    (9.9, 12.1, Z0, (2.2, -3.9, 1.25), (1.8, -3.4, 1.25), Z0, (0.1, 1.6, 0.95), (0.1, 1.6, 0.95), 28, 6),
    (12.1, 14.6, Z0, (0.95, -1.5, 0.75), (0.85, -1.1, 0.75), Z0, (0.33, 2.2, 0.92), (0.33, 2.2, 0.92), 40, 5),
    (14.6, 16.9, Z0, (2.4, -0.3, 0.38), (2.2, -0.15, 0.36), Z0, (0.3, 0.55, 0.3), (0.3, 0.55, 0.28), 45, 4),
    (16.9, 19.2, Z0, (-3.2, -7.2, 1.4), (-3.5, -6.8, 1.4), Z0, (-5.6, -2.2, 1.3), (-5.6, -2.2, 1.3), 35, 5),
    (19.2, 23.7, PX, (0.0, -7.6, 1.3), (0.0, -7.2, 1.3), PW, (0, 0, 1.1), (0, 0, 1.1), 28, 8),
    (23.7, 25.1, Z0, (0.75, -3.3, 0.55), (0.7, -3.1, 0.55), Z0, (0.2, -0.6, 0.55), (0.2, -0.6, 0.55), 50, 4),
    (25.1, 26.5, Z0, (2.3, -3.3, 0.5), (2.25, -3.1, 0.5), Z0, (1.7, -0.7, 0.45), (1.7, -0.7, 0.45), 50, 4),
    (26.5, 28.6, Z0, (-5.9, -2.7, 1.5), (-6.1, -2.6, 1.5), Z0, (-9.95, -1.0, 1.3), (-9.95, -1.0, 1.3), 42, 4),
    (28.6, 30.6, Z0, (0.1, -7.6, 1.3), (0.1, -7.6, 1.3), Z0, (0.1, -1.8, 0.95), (0.1, -1.8, 0.95), 24, 8),
    (30.6, 33.0, Z0, (2.7, -4.8, 1.25), (2.4, -4.4, 1.25), Z0, (0.6, -1.3, 1.2), (0.6, -1.3, 1.2), 35, 5),
    (33.0, 34.8, Z0, (2.5, -4.3, 1.2), (2.4, -4.1, 1.25), Z0, (0.7, -1.6, 1.05), (0.7, -1.6, 1.3), 40, 5),
    (34.8, 36.5, Z0, (1.7, -6.8, 1.2), (1.9, -6.4, 1.1), Z0, (1.6, -1.2, 1.2), (2.0, -1.2, 0.9), 28, 8),
    (36.5, 38.3, Z0, (4.2, -3.5, 0.55), (4.0, -3.3, 0.5), Z0, (3.0, -1.2, 0.5), (3.0, -1.2, 0.5), 40, 5),
    (38.3, 41.5, Z0, (5.4, -3.2, 0.5), (5.2, -3.0, 0.5), Z0, (3.9, -1.0, 0.5), (3.9, -1.0, 0.5), 40, 5),
    (41.5, 43.5, Z0, (-3.5, -8.4, 1.4), (-3.6, -8.0, 1.4), Z0, (-3.8, -1.6, 1.0), (-3.8, -1.6, 1.0), 28, 6),
    (43.5, 46.0, Z0, (-3.6, -4.4, 1.2), (-3.8, -4.1, 1.2), Z0, (-5.5, -1.6, 1.15), (-5.5, -1.6, 1.15), 35, 5),
    (46.0, 47.5, Z0, (-4.9, -3.7, 0.5), (-4.8, -3.5, 0.5), Z0, (-3.6, -1.6, 0.5), (-3.6, -1.6, 0.5), 50, 4),
    (47.5, 49.4, Z0, (1.8, -9.0, 1.6), (2.6, -9.0, 1.6), PW, (0.6, 0, 1.0), (0, 0, 0.6), 32, 8),
    (49.4, 51.6, Z0, (4.4, -3.6, 1.3), (4.6, -3.4, 1.3), Z0, (7.25, -1.6, 1.25), (7.25, -1.6, 1.25), 45, 5),
    (51.6, 54.1, Z0, (-4.6, -6.2, 1.6), (-4.2, -5.2, 1.8), Z0, (-3.2, STY, 2.5), (-3.2, STY, 2.7), 24, 8),
    (54.1, 56.0, Z0, (-4.2, -2.8, 2.4), (-3.4, -2.6, 2.8), PW, (0, 0, 1.3), (0, 0, 1.3), 35, 8),
    (56.0, 57.4, Z0, (1.9, 1.2, 2.6), (1.7, 1.5, 2.7), Z0, (0.6, STY - 0.4, 5.5), (0.6, STY - 0.4, 5.6), 35, 8),
    (57.4, 59.3, CK, (-0.6, -4.6, 0.5), (-0.6, -4.2, 0.5), CK, (0, 0, 0.35), (0, 0, 0.35), 35, 8),
    (59.3, 62.2, Z0, (-6.6, 2.4, 0.45), (-6.8, 2.5, 0.42), Z0, (-7.8, 5.6, 0.5), (-8.1, 4.6, 0.45), 30, 5),
    (62.2, 63.3, Z0, (3.6, -5.6, 1.3), (3.4, -5.3, 1.25), Z0, (0.0, -1.6, 1.2), (0.0, -1.6, 1.15), 35, 5),
    (63.3, 66.8, Z0, (3.3, -4.7, 0.9), (3.0, -4.3, 0.85), Z0, (0.15, -1.6, 0.85), (0.15, -1.6, 0.72), 40, 4),
    (66.8, 69.3, Z0, (0.9, -6.0, 0.7), (0.85, -5.5, 0.7), Z0, (0.7, -1.6, 0.72), (0.7, -1.6, 0.8), 35, 5),
    (69.3, 70.8, Z0, (4.8, -3.6, 0.6), (4.6, -3.4, 0.7), CK, (0.6, 0, 0.2), (2.0, 0, -0.6), 24, 8),
    (70.8, 72.8, CK, (-5.5, -3.2, 0.3), (-4.5, -2.6, 0.5), CK, (0, 0, 0.35), (0, 0, 0.35), 40, 8),
    (72.8, 76.6, Z0, (2.8, -3.8, 0.85), (2.5, -3.5, 0.85), Z0, (0.0, -1.75, 0.92), (0.0, -1.75, 0.95), 45, 4),
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
for o in bpy.data.objects: lin(o)
set_interp(camd, 'CONSTANT')
os.makedirs('../t008', exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath('../t008/pippo_t008.blend')); print('SAVED')
