"""Test 012 - PIPPO E LA ZUCCHINA ELEONORA. Salva ../t012/pippo_t012.blend
Personaggi: Pippo e Tumbo ESISTENTI (pippo.py, tumbo.py) invariati; Gualtiero = nuovo vicino ricorrente (props009.gualtiero)."""
import sys, math, os
sys.path.insert(0, os.path.dirname(__file__))
import bpy, numpy as np
from mathutils import Vector, Euler, Matrix
from common import *
from render_setup import *
import set004, props004, props007, props009, props012, lookdev, pippo, tumbo
from set004 import obj, bx, cyl, ball_, MB

FPS = 24; TOTAL = 40.6; NF = int(TOTAL * FPS)
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

Z12 = props012.mats012(); NK = props012.mats_nuke(); TB = 24.12     # TB = istante dello scoppio
# ======================= personaggi =======================
P = pippo.build_pippo(chc); Tb = tumbo.build_tumbo(chc, scale=0.75); G = props009.gualtiero(chc, G9); Z = props012.zucchina(chc, Z12)
for r in (P['root'], Tb['root'], G['root'], Z['root']): r.rotation_mode = 'XYZ'
for R_ in (P, G):
    for nm in 'LR': R_['shoulder' + nm].rotation_mode = 'QUATERNION'
def qdir(d, rest=(0, 0, -1)): return Vector(rest).rotation_difference(Vector(d).normalized())
def wd(yaw, v):
    """direzione mondo -> locale del personaggio con imbardata yaw."""
    c, s = math.cos(-yaw), math.sin(-yaw); return (c * v[0] - s * v[1], s * v[0] + c * v[1], v[2])

# ======================= oggetti =======================
TAB = (-1.6, -1.5); PL = (-3.15, -1.4); BOMB0 = (1.9, 1.6); ORTO = (-13.5, -3.0); RY = -10.6
tab = props012.table(prc, Z12); tab.location = (TAB[0], TAB[1], 0)
rose = props012.rose(chc, Z12, P['shoulderR'])
bulb = props012.bulb(prc, Z12)
bomb, tapes = props012.bomb(prc, Z12)
pallet = obj('Bancale', set004.box_c(), (BOMB0[0], BOMB0[1], 0.07), (1.1, 1.1, 0.14), M['wood'], prc)
orto = props012.orto(prc, Z12); orto.location = (ORTO[0], ORTO[1], 0)
crater = obj('Cratere', shared_mesh('cyl:1:1'), (ORTO[0], ORTO[1], 0.02), (9.0, 8.0, 0.03), Z12['crater'], prc)
mush, mring = props012.mushroom2(prc, NK); mush.location = (-38.0, -3.0, 0)
flash = ball_('Lampo', 0.7, (4.0, -3.0, 1.1), Z12['flash'], prc)
moto, mface, mwheels, mmouth = props012.moto(prc, Z12); moto.rotation_euler = (0, 0, PI / 2); props012.moto_extras(prc, Z12, moto, mface)
can = obj('Annaffiatoio', set004.box_c(), (0, 0, -0.78), (0.22, 0.3, 0.26), Z12['steel'], chc, parent=G['shoulderR'])
hm = props007.heart_mesh(N)

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
T_EYES, T_MOUTH, T_LEGS, T_RIDE = 27.0, 28.3, 29.2, 31.7
show(tab, [(0.0, T_RIDE)]); show(rose, [(5.9, 12.6), (20.25, 21.9), (24.0, 31.7)])
show(bulb, [(13.2, 14.8)]); pop(bulb, 13.2, 0.25)
show(bomb, [(14.8, 24.0)]); show(pallet, [(14.8, 20.25)])
for k, tp_ in enumerate(tapes): show(tp_, [(17.55 + 0.22 * k, 24.0)]); pop(tp_, 17.55 + 0.22 * k, 0.18)
show(orto, [(0.0, 24.0)]); show(crater, [(24.0, TOTAL)]); show(G['root'], [(0.0, 24.0)])
show(mush, [(TB, TOTAL)]); keys(mush, 'scale', [(TB, (1.2, 1.2, 0.4)), (24.6, (2.7, 2.7, 2.3)), (25.4, (3.4, 3.4, 3.3)), (31.7, (3.7, 3.7, 3.7)), (TOTAL, (3.9, 3.9, 4.0))])
show(flash, [(24.0, 24.3)])
show(Z['eyes'], [(T_EYES, TOTAL)]); pop(Z['eyes'], T_EYES, 0.25); show(Z['mouth'], [(T_MOUTH, TOTAL)]); pop(Z['mouth'], T_MOUTH, 0.25); show(Z['legs'], [(T_LEGS, TOTAL)]); pop(Z['legs'], T_LEGS, 0.25)
show(Z['veil'], [(T_RIDE, TOTAL)]); show(moto, [(T_RIDE, TOTAL)])

# ======================= pose =======================
DOWN = lambda s: (s * 0.14, 0, -1)
UP = dict(aL=(-0.35, -0.25, 1), aR=(0.35, -0.25, 1))
def MX(t): return -4.0 + 6.5 * (t - T_RIDE)
def MW(t): return (MX(t), RY, 0.03 * abs(math.sin(t * 23)))
def bomb_state(t):
    """posizione e rotazione della bomba."""
    if t < 18.85: return (BOMB0[0], BOMB0[1], 0.14 + 0.85 + 0.02 * abs(math.sin(t * 30)) * (17.5 < t < 18.3)), (0, 0, 0)
    if t < 20.1:
        u = (t - 18.85) / 1.25; x = BOMB0[0] + (ORTO[0] - BOMB0[0]) * u; y = BOMB0[1] + (ORTO[1] - BOMB0[1]) * u; z = 0.99 + (0.55 - 0.99) * u + 30.0 * u * (1 - u)
        return (x, y, z), (0, -PI / 2 - 0.3 + 2.4 * u + (PI - 2.1) * ramp(u, 0.7, 1.0), 0.0)
    return (ORTO[0], ORTO[1], 0.55 + 0.03 * math.sin(t * 40) * (t > 21.9)), (0, PI + 0.12 * math.sin(t * 3), 0)
def pp(t):
    S_ = dict(loc=(PL[0], PL[1], 0), rot=(0, 0, 0.8), aL=DOWN(-1), aR=DOWN(1), hL=0.0, hR=0.0, head=(0, 0, 0))
    yw = 0.8
    if t < 5.9:                                    # innamorato perso
        sway = 0.08 * math.sin(t * 3)
        S_.update(rot=(0.05, sway, yw), aL=wd(yw, (0.25, -0.5, 0.35)), aR=wd(yw, (0.45, -0.45, 0.35)), head=(0, 0.25 * math.sin(t * 3 + 1), 0.35))
    elif t < 9.6:                                  # la rosa
        o = ramp(t, 6.2, 6.6)
        S_.update(rot=(0.18 * o, 0, yw + 0.3), aR=lerp(DOWN(1), wd(yw + 0.3, (1, -0.05, -0.12)), o), aL=(-0.4, 0.35, -0.8), head=(-0.1, 0, 0.1))
    elif t < 12.6:                                 # e grazie...
        k = math.sin(t * 13)
        S_.update(loc=(PL[0], PL[1], 0.04 * abs(k)), rot=(0.1, 0, yw + 0.3), aR=wd(yw + 0.3, (0.9, -0.1, 0.25 + 0.35 * k)), aL=wd(yw + 0.3, (0.5, -0.6, 0.5 - 0.3 * k)), head=(0.05, 0, 0.2))
    elif t < 14.8:                                 # l'idea
        g = ramp(t, 13.2, 13.4)
        S_.update(rot=(0, 0, 0.3), aR=lerp((0.35, -0.6, 0.55), (0.2, -0.3, 1.0), g), aL=(-0.5, -0.15, -0.8), head=(-0.15 * g, 0, 0))
    elif t < 20.25:                                # la bomba in garage, con lo scotch
        yb = 1.25; k = math.sin(t * 19)
        if t < 18.5: S_.update(loc=(BOMB0[0] - 1.05, BOMB0[1] - 0.35, 0), rot=(0.1, 0, yb), aR=wd(yb, (0.9, 0.25, 0.1 + 0.35 * k)), aL=wd(yb, (0.9, -0.1, 0.3 - 0.35 * k)))
        else:
            kick = ramp(t, 18.7, 18.85) * (1 - ramp(t, 18.95, 19.2))
            S_.update(loc=(BOMB0[0] - 1.05, BOMB0[1] - 0.35, 0), rot=(-0.25 * kick, 0, yb + 0.2), hR=-1.5 * kick, head=(-0.3 * ramp(t, 19.0, 19.4), 0, 0.9 * ramp(t, 19.0, 19.4)), **(UP if t > 19.1 else dict(aL=(-0.6, 0.2, -0.7), aR=(0.6, 0.2, -0.7))))
    elif t < 24.0:                                 # per fare colpo
        S_.update(rot=(-0.06, 0.1, yw + 0.3), aR=wd(yw + 0.3, (1, -0.05, -0.1)), aL=(-0.75, -0.2, 0.2), head=(0, 0.15, 0.1))
    elif t < 30.0:                                 # e funziona
        j = 0.03 * math.sin(t * 40) * (1 - ramp(t, 24.0, 25.5)); amaze = ramp(t, 25.4, 25.8)
        S_.update(loc=(PL[0] + j, PL[1], 0), rot=(0, 0, lerp((1.35,), (yw + 0.3,), amaze)[0]), aR=lerp((0.35, -0.5, 0.7), wd(yw + 0.3, (0.9, -0.2, 0.1)), amaze), aL=lerp((-0.55, -0.15, -0.8), (-0.6, -0.4, 0.5), amaze), head=(0, 0, 0.2 * amaze))
    elif t < T_RIDE:                               # dice si'
        k = abs(math.sin((t - 30.3) * 9)) * (t > 30.3)
        S_.update(loc=(PL[0], PL[1], 0.3 * k), rot=(0, 0, yw + 0.3), aR=wd(yw + 0.3, (0.6, -0.3, 0.8)), aL=UP['aL'])
    else:                                          # in moto
        m = MW(t); S_.update(loc=(m[0] - 0.28, RY, 0.30 + m[2]), rot=(0.12, 0, PI / 2), hL=-1.05, hR=-1.05, aL=(-0.28, -1, -0.12), aR=(0.28, -1, -0.12), head=(-0.1, 0, -0.5 * ramp(t, 37.9, 38.3)))
    return S_
def zp(t):
    """Eleonora: loc, rot, scala."""
    top = 0.82
    if t < 25.3: return dict(loc=(TAB[0] - 0.5, TAB[1], top + props012.ZR), rot=(0, PI / 2, 0), sc=1.0)
    if t < T_RIDE:
        u = ramp(t, 25.3, 26.3); hop = 0.22 * abs(math.sin((t - 30.3) * 9)) * (t > 30.3); legs = 0.31 * ramp(t, T_LEGS, T_LEGS + 0.2)
        wob = 0.1 * math.sin(t * 14) * u * (1 - ramp(t, 26.3, 26.8))
        return dict(loc=(TAB[0] - 0.5 * (1 - u), TAB[1], top + props012.ZR * (1 - u) + legs + hop + 0.25 * math.sin(PI * u)), rot=(0, PI / 2 * (1 - u) + wob, -0.5 * ramp(t, 30.0, 30.3)), sc=1.0)
    m = MW(t); return dict(loc=(m[0] - 0.80, RY - 0.24, 1.17 + m[2]), rot=(0.10, 0.06 * math.sin(t * 5), PI / 2 + 0.2 * math.sin(t * 2.0)), sc=1.0)
def tp(t):
    S_ = dict(loc=(-0.5, -2.7, 0), rot=(0, 0, -0.6), head=(0, 0, 0), tail=-1.0 + 0.5 * math.sin(t * 12))
    if t < 14.8: S_.update(head=(0.15 * ramp(t, 9.7, 10.0), 0, 0.5 - 1.0 * ramp(t, 9.7, 10.0)), tail=-0.3)
    elif t < 20.25: S_.update(loc=(0.4, 0.2, 0), rot=(0, 0, 0.9), head=(-0.3, 0, 0))
    elif t < 24.0: S_.update(head=(0, 0, 0.4), tail=-0.3)
    elif t < T_RIDE: S_.update(loc=(-0.5, -2.7, 0.3 * abs(math.sin((t - 24.0) * 12)) * (1 - ramp(t, 24.0, 24.8))), head=(-0.3, 0, 0.3))
    else: m = MW(t); S_.update(loc=(m[0] - 2.9, RY + 0.5, 0.14 * abs(math.sin(t * 18))), rot=(0, 0, PI / 2), head=(-0.2, 0, -0.4))
    return S_
def gp(t):
    S_ = dict(loc=(ORTO[0] + 0.9, ORTO[1] + 1.6, 0), rot=(0.1, 0, 0.3), aL=DOWN(-1), aR=(0.3, -0.8, -0.5), head=(0.2, 0, 0))
    if t > 19.6:
        j = 0.02 * math.sin(t * 45) * (t > 22.0)
        S_.update(loc=(ORTO[0] + 0.9 + j, ORTO[1] + 1.6, 0), rot=(-0.12, 0, -0.5), aL=(-0.5, -0.3, 0.8 * ramp(t, 22.9, 23.2) - 0.5), aR=(0.5, -0.3, 0.8 * ramp(t, 22.9, 23.2) - 0.5), head=(0.25, 0, 0.3))
    return S_

# ======================= chiavi =======================
TR = Tb['root']; ZRt = Z['root']
for f in range(1, NF + 1):
    t = (f - 1) / FPS
    for R_, s in ((P, pp(t)), (G, gp(t))):
        r = R_['root']; r.location = s['loc']; r.rotation_euler = s['rot']; r.keyframe_insert('location', frame=f); r.keyframe_insert('rotation_euler', frame=f)
        for nm, k in (('L', 'aL'), ('R', 'aR')):
            sh = R_['shoulder' + nm]; sh.rotation_quaternion = qdir(s[k]); sh.keyframe_insert('rotation_quaternion', frame=f)
        if R_ is P:
            for nm, k in (('L', 'hL'), ('R', 'hR')):
                hp = R_['hip' + nm]; hp.rotation_euler = (s[k], 0, 0); hp.keyframe_insert('rotation_euler', frame=f)
        R_['head'].rotation_euler = s['head']; R_['head'].keyframe_insert('rotation_euler', frame=f)
    q = tp(t); TR.location = q['loc']; TR.rotation_euler = q['rot']; TR.keyframe_insert('location', frame=f); TR.keyframe_insert('rotation_euler', frame=f)
    Tb['head'].rotation_euler = q['head']; Tb['head'].keyframe_insert('rotation_euler', frame=f)
    Tb['tail'].rotation_euler = (q['tail'], 0, 0.5 * math.sin(t * 14)); Tb['tail'].keyframe_insert('rotation_euler', frame=f)
    z = zp(t); ZRt.location = z['loc']; ZRt.rotation_euler = z['rot']; ZRt.scale = (z['sc'],) * 3; ZRt.keyframe_insert('location', frame=f); ZRt.keyframe_insert('rotation_euler', frame=f); ZRt.keyframe_insert('scale', frame=f)
    if 14.7 < t < 24.1:
        l, e = bomb_state(t); bomb.location = l; bomb.rotation_euler = e; bomb.keyframe_insert('location', frame=f); bomb.keyframe_insert('rotation_euler', frame=f)
    if 13.1 < t < 14.9:
        bulb.location = (PL[0], PL[1] - 0.1, 2.55 + 0.05 * math.sin(t * 6)); bulb.keyframe_insert('location', frame=f)
    if t > T_RIDE - 0.1:
        moto.location = MW(t); moto.keyframe_insert('location', frame=f)
        for w_ in mwheels: w_.rotation_euler = (-(t - T_RIDE) * 6.5 / 0.36, 0, 0); w_.keyframe_insert('rotation_euler', frame=f)
        talk = (33.0 < t < 34.6) or (34.95 < t < 36.7) or (36.9 < t < 37.6)
        mmouth.scale = (0.06, 0.015, 0.02 + 0.05 * abs(math.sin(t * 17)) * talk); mmouth.keyframe_insert('scale', frame=f)
        mface.rotation_euler = (0.12 * math.sin(t * 9) * talk, 0, 0.15 * math.sin(t * 4.5) * talk); mface.keyframe_insert('rotation_euler', frame=f)

_last = {}
def _ex(key, fn, t, k):
    if key in _last and t - 0.06 > _last[key][1]: fn(fr(t - 0.06), **_last[key][0])
    fn(fr(t), **k); _last[key] = (k, t)
def pex(t, **k): _ex('p', lambda f, **kk: pippo.express(P, f, **kk), t, k)
def tex(t, **k): _ex('t', lambda f, **kk: tumbo.tumbo_express(Tb, f, **kk), t, k)
def gx(t, **k): _ex('g', lambda f, **kk: props009.gex(G, f, **kk), t, k)
pex(0.0, smile=1.0, brow_lift=0.7, eye_scale=1.3, eye_open=0.75, mouth_open=0.3, look=(0.6, 0)); pex(6.0, smile=1.0, brow_lift=0.5, eye_scale=1.15, mouth_open=0.5, look=(0.6, 0)); pex(8.3, smile=0.3, brow_lift=0.4, mouth_open=0.2, look=(0.6, 0))
pex(9.7, brow=1.0, mouth_open=0.9, eye_open=0.8, look=(0.6, 0)); pex(12.7, brow=0.3, brow_lift=0.3, eye_open=0.7, look=(0, 0.6)); pex(13.2, brow=1.0, smile=1.0, eye_open=0.65, mouth_open=0.3, look=(0, 0))
pex(14.9, brow=1.0, smile=0.8, eye_open=0.7, look=(0.5, -0.3)); pex(18.9, smile=1.0, mouth_open=0.8, brow_lift=0.5, look=(-0.5, 0.5)); pex(20.3, smile=1.0, brow=0.4, eye_open=0.55, look=(0.6, 0))
pex(24.0, smile=1.0, brow=0.5, eye_open=0.6, mouth_open=0.2, look=(0, 0)); pex(25.4, brow=-0.6, brow_lift=0.9, eye_scale=1.4, mouth_open=0.8, look=(0.6, 0)); pex(30.1, smile=1.0, mouth_open=1.0, brow_lift=0.7, eye_scale=1.3, look=(0.6, 0))
pex(T_RIDE, smile=1.0, mouth_open=0.5, brow_lift=0.4, eye_open=0.8, look=(0, 0)); pex(38.0, smile=1.0, mouth_open=0.3, brow=0.4, look=(0.5, 0))
tex(0.0, eye_open=0.6, brow=0.6); tex(9.8, eye_open=0.5, brow=1.0, look=(0, 0)); tex(18.9, eye_scale=1.3, brow=-0.6); tex(24.0, eye_scale=1.5, brow=-0.8); tex(26.0, eye_scale=1.4, brow=-0.5); tex(T_RIDE, tongue=1.0)
gx(0.0, brow=0.2, mouth=0.1); gx(20.1, brow=-0.6, mouth=0.4, look=(0.6, -0.6)); gx(22.9, brow=-1.0, mouth=1.0, look=(0.6, -0.6))

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
def burst(name, mat, t0, dur, c0, n, vmax, sc, grav=4.9, up=1.0, mesh=None, vx=0.0):
    for k in range(n):
        v = np.array([er.uniform(-vmax, vmax) + vx, er.uniform(-vmax, vmax), er.uniform(0.3, 1.0) * vmax * up])
        streak(name, sc, mat, t0, t0 + dur, lambda t, v=v: ((c0[0] + v[0] * (t - t0), c0[1] + v[1] * (t - t0), max(0.03, c0[2] + v[2] * (t - t0) - grav * (t - t0) ** 2)),), mesh=mesh)
def hearts(t0, t1, cfn, n=6, s=0.09, rise=1.1, sp_=0.7):
    for k in range(n):
        ph = k / n; dx = er.uniform(-0.35, 0.35)
        def fn(t, ph=ph, dx=dx):
            u = ((t - t0) * sp_ + ph) % 1.0; c0 = cfn(t); return ((c0[0] + dx + 0.12 * math.sin(u * 7 + ph * 9), c0[1], c0[2] + rise * u), (max(0.001, s * math.sin(PI * u)),) * 3)
        streak('Cuore', (s, s, s), N['heart'], t0, t1, fn, mesh=hm)
hearts(0.0, 5.9, lambda t: (PL[0] + 0.15, PL[1] - 0.35, 2.05), n=7)
hearts(30.2, T_RIDE, lambda t: (TAB[0] - 0.7, TAB[1] - 0.3, 1.9), n=10, s=0.12, rise=1.6, sp_=1.2)
hearts(T_RIDE, TOTAL, lambda t: (MX(t) - 0.9, RY - 0.2, 2.3), n=6, s=0.1, rise=1.0)
streak('Mosca', (0.02, 0.02, 0.02), Z12['black'], 4.0, 9.6, lambda t: ((TAB[0] + 0.45 * math.cos(t * 5), TAB[1] - 0.15 + 0.2 * math.sin(t * 7), 1.15 + 0.12 * math.sin(t * 9)),))
streak('Petalo', (0.035, 0.035, 0.012), Z12['rose'], 8.5, 9.6, lambda t: ((TAB[0] - 0.75 + 0.1 * math.sin(t * 6), TAB[1] - 0.3, max(0.84, 1.15 - 0.5 * (t - 8.5))),))
for k in range(3):                                                                                  # scintille da officina
    burst('Scintilla', N['spark'], 15.3 + 0.75 * k, 0.45, (BOMB0[0] - 0.3, BOMB0[1] - 0.35, 1.2), 6, 1.5, (0.04, 0.04, 0.04), grav=3.0)
burst('Polvere', M['dust'], 18.85, 0.5, (BOMB0[0], BOMB0[1], 0.3), 8, 2.0, (0.12, 0.12, 0.12), grav=0.5, up=0.3)
for k in range(8):                                                                                  # scia della bomba
    streak('Scia', (0.1, 0.1, 0.1), M['dust'], 18.9, 20.2, lambda t, k=k: (bomb_state(max(18.85, t - 0.06 * (k + 1)))[0], (max(0.001, 0.2 - 0.02 * k),) * 3))
burst('Terra', Z12['soil'], 20.1, 0.7, (ORTO[0], ORTO[1], 0.2), 12, 2.5, (0.1, 0.1, 0.1))
VEG = [(Z12['cab'], (0.2, 0.2, 0.16)), (Z12['carrot'], (0.06, 0.06, 0.2)), (Z12['tom'], (0.08, 0.08, 0.08)), (Z12['soil'], (0.15, 0.15, 0.12))]
for k in range(34):                                                                                 # piovono verdure
    m_, s_ = VEG[k % 4]; vx = er.uniform(1.5, 7.5); vy = er.uniform(-2.0, 2.5); vz = er.uniform(9, 16); t0 = 24.05 + er.uniform(0, 0.25)
    streak('Verdura', s_, m_, t0, t0 + 3.6, lambda t, vx=vx, vy=vy, vz=vz, t0=t0: ((ORTO[0] + vx * (t - t0), ORTO[1] + vy * (t - t0), max(0.06, 1.0 + vz * (t - t0) - 4.9 * (t - t0) ** 2)), ) )
for k in range(3):
    pt = (T_EYES, T_MOUTH, T_LEGS)[k]; burst('Scintilla', N['spark'], pt, 0.4, (TAB[0], TAB[1] - 0.2, 0.82 + (0.7, 0.56, 0.0)[k]), 6, 1.2, (0.03, 0.03, 0.03), grav=2.0)
for k in range(10):                                                                                 # brum brum
    ph = k / 10
    def fn(t, ph=ph):
        u = ((t * 1.6 + ph) % 1.0); return ((MX(t) - 1.4 - 1.6 * u, RY + 0.25, 0.45 + 0.5 * u), (max(0.001, 0.05 + 0.2 * u) * (1 - u * 0.5),) * 3)
    streak('Scarico', (0.1, 0.1, 0.1), M['dust'], T_RIDE, TOTAL, fn)
for k in range(5):                                                                                  # barattoli
    streak('Barattolo', (0.07, 0.07, 0.1), Z12['steel'], T_RIDE, TOTAL, lambda t, k=k: ((MX(t) - 1.9 - 0.35 * k, RY - 0.3 + 0.12 * math.sin(k * 2.1), 0.1 + 0.18 * abs(math.sin(t * 15 + k * 1.3))),), mesh=shared_mesh('cyl:1:1'))
for k in range(24):                                                                                 # riso
    ph = er.uniform(0, 1); dy = er.uniform(-1.6, 1.6); dz = er.uniform(1.4, 3.2)
    streak('Riso', (0.03, 0.015, 0.015), Z12['white'], T_RIDE, TOTAL, lambda t, ph=ph, dy=dy, dz=dz: ((MX(t) + 3.0 - 6.0 * ((t * 0.9 + ph) % 1.0), RY + dy, dz - 1.2 * ((t * 0.9 + ph) % 1.0)),))


# ======================= dopo la bomba: scenario nucleare =======================
keep_ = ('Prato', 'Strada', 'Marciapiede', 'Linea')
env_gone = [o for o in envc.objects if not o.name.startswith(keep_)] + [o for o in bpy.data.objects if o.name.startswith(('Puff', 'CloudW'))]
items = [(o.location.x, o.location.y, o.dimensions.x, o.dimensions.y, o.dimensions.z, o.rotation_euler.z) for o in envc.objects if o.name.startswith(('Casa', 'Palazzo'))]
trunks = [(o.location.x, o.location.y) for o in envc.objects if o.name.startswith('Tronco')]
show(env_gone, [(0.0, TB)])
ruin = props012.ruins(prc, NK, items, trunks); show(ruin, [(TB, TOTAL)])
ashg = bx('Cenere', (-140, -140, 0.0), (140, 140, 0.006), NK['ash'], prc); lookdev._tex(NK['ash'], 0.3, 14.0, (0.07, 0.06, 0.055), (0.30, 0.26, 0.22), bump=0.8, rough=1.0); show(ashg, [(TB, TOTAL)])
dome = ball_('CieloNucleare', 320.0, (0, 0, 0), NK['sky'], prc); dome.visible_shadow = False; show(dome, [(TB, TOTAL)])
glow_l = bpy.data.lights.new('Bagliore', 'SUN'); glow_o = bpy.data.objects.new('Bagliore', glow_l); prc.objects.link(glow_o); glow_o.rotation_euler = (math.radians(72), 0, math.radians(-95)); glow_l.color = (1.0, 0.42, 0.12); glow_l.use_shadow = False
keys(mring, 'rotation_euler', [(TB, (0, 0, 0)), (TOTAL, (0, 0, 1.4))])
FIRES = [(-6.0, 7.5, 1.3), (5.0, 8.5, 1.6), (9.0, -3.0, 1.1), (-12.0, 6.0, 1.4), (-16.5, -6.0, 1.2), (2.0, 13.0, 2.0), (-3.5, 9.5, 1.0)] + [(-20.0 + 8.5 * k, (-4.2 if k % 2 else -19.5) + 0.8 * math.sin(k * 1.9), 1.0 + 0.5 * ((k * 7) % 3)) for k in range(9)]
fires = []
for (x, y, s) in FIRES:
    fr_, fl_ = props012.fire(prc, NK, s); fr_.location = (x, y, 0); show(fr_, [(TB, TOTAL)]); fires.append(fl_)
for f in range(fr(TB), NF + 1):
    t = (f - 1) / FPS
    for i_, fl_ in enumerate(fires):
        for j_, (fo, k) in enumerate(fl_):
            s = FIRES[i_][2]; q = 1 + 0.3 * math.sin(t * 21 + i_ * 2.3 + j_ * 1.7) + 0.2 * math.sin(t * 37 + j_ + i_)
            fo.scale = (0.34 * s * k, 0.34 * s * k, 1.5 * s * k * q); fo.rotation_euler = (0.1 * math.sin(t * 13 + j_ + i_), 0.12 * math.sin(t * 17 + i_), 0); fo.keyframe_insert('scale', frame=f); fo.keyframe_insert('rotation_euler', frame=f)
for k in range(30):                                                                                 # onda d'urto dal punto dello scoppio
    a_ = 2 * PI * k / 30
    streak('OndaUrto', (0.6, 0.6, 0.6), NK['wave'], TB, 25.4, lambda t, a_=a_: ((ORTO[0] + (2.0 + 26.0 * (t - TB)) * math.cos(a_), ORTO[1] + (2.0 + 26.0 * (t - TB)) * math.sin(a_), 0.5), (0.35 + 0.5 * (t - TB),) * 3))
def near(t): return (-1.5, -1.5) if t < T_RIDE else (MX(t) + 1.0, RY)
for k in range(44):                                                                                 # braci che salgono
    ph = er.uniform(0, 1); dx = er.uniform(-7, 7); dy = er.uniform(-2.5, 7); sp_ = er.uniform(0.25, 0.5); wob = er.uniform(0, 6)
    streak('Brace', (0.03, 0.03, 0.03), NK['ember'], TB, TOTAL, lambda t, ph=ph, dx=dx, dy=dy, sp_=sp_, wob=wob: ((near(t)[0] + dx + 0.4 * math.sin(t * 2 + wob), near(t)[1] + dy, 0.2 + 4.5 * ((t * sp_ + ph) % 1.0)),))
for k in range(70):                                                                                 # cenere che cade
    ph = er.uniform(0, 1); dx = er.uniform(-7, 7); dy = er.uniform(-3, 6); sp_ = er.uniform(0.12, 0.22); wob = er.uniform(0, 6); s = er.uniform(0.02, 0.045)
    streak('Fiocco', (s, s, s * 0.3), NK['flake'], TB, TOTAL, lambda t, ph=ph, dx=dx, dy=dy, sp_=sp_, wob=wob: ((near(t)[0] + dx + 0.3 * math.sin(t * 1.5 + wob), near(t)[1] + dy + 0.2 * math.cos(t * 1.2 + wob), 5.0 * (1 - ((t * sp_ + ph) % 1.0))),))

# ======================= camera =======================
def Z0(t): return (0, 0, 0)
def MC(t): return (MX(t), RY, 0)
def BW(t): l = bomb_state(t)[0]; return (l[0] * 0.5, 0, l[2] * 0.35)
def SH2(t): q = 1 - ramp(t, 24.3, 25.3); return (0.09 * math.sin(t * 57) * q, 0, 0.08 * math.sin(t * 43) * q)
SHOTS = [  # t0, t1, sub cam, p0, p1, sub mira, a0, a1, lente, f
    (0.0, 2.25, Z0, (-1.5, -4.6, 1.6), (-1.6, -4.2, 1.6), Z0, (PL[0] + 0.05, PL[1], 1.62), (PL[0] + 0.05, PL[1], 1.62), 38, 5),
    (2.25, 4.0, Z0, (-1.9, -6.6, 1.2), (-2.0, -6.0, 1.2), Z0, (-2.35, -1.5, 1.15), (-2.35, -1.5, 1.15), 32, 6),
    (4.0, 5.9, Z0, (-1.1, -4.9, 1.2), (-1.2, -4.5, 1.2), Z0, (TAB[0], TAB[1], 0.82), (TAB[0], TAB[1], 0.82), 45, 5),
    (5.9, 8.1, Z0, (-2.0, -5.6, 1.25), (-2.1, -5.2, 1.25), Z0, (-2.35, -1.5, 1.1), (-2.35, -1.5, 1.1), 36, 6),
    (8.1, 9.6, Z0, (-1.9, -4.6, 1.15), (-1.9, -4.2, 1.15), Z0, (TAB[0] - 0.2, TAB[1], 0.88), (TAB[0] - 0.2, TAB[1], 0.88), 50, 5),
    (9.6, 12.6, Z0, (-1.8, -5.8, 1.3), (-1.9, -5.4, 1.3), Z0, (-2.2, -1.6, 1.1), (-2.2, -1.6, 1.1), 34, 6),
    (12.6, 14.8, Z0, (-2.5, -4.6, 1.7), (-2.6, -4.2, 1.7), Z0, (PL[0], PL[1], 2.0), (PL[0], PL[1], 2.0), 45, 5),
    (14.8, 18.5, Z0, (0.1, -3.4, 1.3), (0.3, -2.9, 1.3), Z0, (1.4, 1.4, 1.15), (1.4, 1.4, 1.15), 32, 6),
    (18.5, 20.25, Z0, (-4.5, -15.5, 1.6), (-5.0, -15.0, 1.6), BW, (-3.0, 0.5, 2.2), (-3.0, 0.5, 2.2), 32, 11),
    (20.25, 21.9, Z0, (-2.0, -5.4, 1.25), (-2.1, -5.1, 1.25), Z0, (-2.35, -1.5, 1.15), (-2.35, -1.5, 1.15), 38, 6),
    (21.9, 24.0, Z0, (-10.6, -7.4, 1.3), (-11.0, -6.6, 1.3), Z0, (-13.7, -2.6, 0.95), (-13.7, -2.6, 0.95), 30, 6),
    (24.0, 25.3, SH2, (4.0, -3.0, 1.1), (3.6, -2.9, 1.1), Z0, (-8.0, -1.7, 4.6), (-8.0, -1.7, 6.6), 24, 11),
    (25.3, 26.8, Z0, (-1.0, -4.6, 1.3), (-1.1, -4.2, 1.3), Z0, (TAB[0], TAB[1], 1.25), (TAB[0], TAB[1], 1.3), 42, 5),
    (26.8, 30.0, Z0, (-1.2, -4.3, 1.4), (-1.3, -3.9, 1.4), Z0, (TAB[0], TAB[1], 1.38), (TAB[0], TAB[1], 1.45), 45, 5),
    (30.0, T_RIDE, Z0, (-1.9, -6.0, 1.3), (-2.0, -5.6, 1.3), Z0, (-2.35, -1.5, 1.35), (-2.35, -1.5, 1.35), 34, 6),
    (T_RIDE, 34.7, MC, (0.7, -5.4, 1.25), (0.2, -5.0, 1.25), MC, (-0.35, 0, 1.3), (-0.35, 0, 1.3), 32, 8),
    (34.7, 37.8, MC, (3.1, -1.6, 1.0), (2.8, -1.4, 1.05), MC, (0.45, -0.05, 1.4), (0.45, -0.05, 1.4), 32, 8),
    (37.8, 40.7, MC, (4.8, -1.2, 0.9), (6.0, -1.5, 1.0), MC, (-2.0, 0.6, 2.9), (-2.0, 0.6, 3.2), 28, 11),
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
lookdev.upgrade(scene, 720, 1280, samples=12, world=0.36, sun_e=6.5, exposure=-0.1)       # nuovo aspetto: luci e ombre, prato con texture
for f in range(1, NF + 1):                                                                 # luce: giorno sereno prima, bagliore arancione dopo lo scoppio
    t = (f - 1) / FPS; nk = t >= TB
    sunl.energy = 3.3 if nk else 6.5; sunl.color = (1.0, 0.62, 0.38) if nk else (1.0, 0.93, 0.80); bg.inputs['Strength'].default_value = 0.15 if nk else 0.36; glow_l.energy = 2.4 if nk else 0.0
    sunl.keyframe_insert('energy', frame=f); sunl.keyframe_insert('color', frame=f); bg.inputs['Strength'].keyframe_insert('default_value', frame=f); glow_l.keyframe_insert('energy', frame=f)
os.makedirs('../t012', exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath('../t012/pippo_t012.blend')); print('SAVED')
