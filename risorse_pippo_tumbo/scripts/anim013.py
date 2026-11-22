"""Test 013 - PIPPO E TUMBO IN AEREO. Salva ../t013/pippo_t013.blend
Personaggi: Pippo e Tumbo ESISTENTI (pippo.py, tumbo.py) invariati; Gualtiero = nuovo vicino ricorrente (props009.gualtiero)."""
import sys, math, os
sys.path.insert(0, os.path.dirname(__file__))
import bpy, numpy as np
from mathutils import Vector, Euler, Matrix
from common import *
from render_setup import *
import set004, props004, props007, props009, props010, props012, props013, lookdev, pippo, tumbo
from set004 import obj, bx, cyl, ball_, MB

FPS = 24; TOTAL = 46.0; NF = int(TOTAL * FPS)
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

A = props013.mats013(); Z12 = props012.mats012()
AIR = (500.0, 0.0); CX0 = 800.0; BX0 = 900.0; HX0 = 1000.0; TOWN = (1500.0, 0.0)
props013.airport(envc, A, AIR[0], AIR[1])
term = MB([A['wall'], A['win'], A['blue']]); term.b2((AIR[0] - 60, 44, 0), (AIR[0] + 60, 58, 9), 0)
for k in range(24): term.b2((AIR[0] - 58 + 5 * k, 43.98, 2.5), (AIR[0] - 55 + 5 * k, 44.0, 7.5), 1)
term.b2((AIR[0] + 30, 40, 0), (AIR[0] + 34, 44, 22), 0); term.b2((AIR[0] + 28.5, 38.5, 22), (AIR[0] + 35.5, 45.5, 26), 1)
term.build('Terminal', envc)
for k in range(10): tree(AIR[0] - 50 + 11 * k + rng.uniform(-2, 2), 36 + rng.uniform(-2, 2), 1.4)
CK = props013.cockpit_set(envc, A, CX0)
SEATS, wcdoor = props013.cabin_set(envc, A, BX0)
PILLOW = props013.hospital_set(envc, A, HX0)
HOSP = props013.lowcity(envc, M, A, TOWN[0], TOWN[1], rng)
for k in range(14):                                                                                  # nuvole vicine ai voli
    for (cx, cy, cz) in ((AIR[0] + 60 + 25 * k, 70 + 10 * math.sin(k), 30 + 6 * math.cos(k * 1.7)), (TOWN[0] - 220 + 30 * k, 90 + 8 * math.sin(k * 2.1), 55 + 8 * math.cos(k))):
        cw = empty('CloudW', (cx, cy, cz), None, prc)
        for (dx, dy, dz, r_) in [(0, 0, 0, 1.5), (1.5, 0.3, -0.2, 1.15), (-1.5, -0.2, -0.25, 1.2), (0.6, -0.5, 0.6, 1.1), (-0.6, 0.5, 0.5, 1.0)]: ball_('Puff', r_ * 4, (dx * 4, dy * 4, dz * 4), M['cloudw'], prc, parent=cw, sc=(1, 1, 0.6))

# ======================= personaggi =======================
P = pippo.build_pippo(chc); Tb = tumbo.build_tumbo(chc, scale=0.75); Z = props012.zucchina(chc, Z12)
PL = props004.player(chc, 'Pilota', (0.97, 0.97, 0.98), (0.08, 0.10, 0.25), (0.96, 0.70, 0.55), (0.25, 0.15, 0.08), scale=1.0)
plhead = [c for c in PL['root'].children if c.name.startswith('Head')][0]
plsmile = [c for c in plhead.children if c.name.startswith('Smile')][0]
pleyes = [c for c in plhead.children if c.name.startswith('Eye')]
pltorso = [c for c in PL['root'].children if c.name.startswith('Torso')][0]
for s_ in (-1, 1): obj('PlSopr', set004.box_c(), (s_ * 0.10, -0.25, 0.14), (0.13, 0.03, 0.035), M['dark'], chc, rot=(0, -s_ * 0.2, 0), parent=plhead)
props013.pilot_cap(chc, A, plhead)
obj('PlCravatta', set004.box_c(), (0, -0.25, 1.25), (0.08, 0.03, 0.34), A['blue'], chc, parent=PL['root'])
for r in (P['root'], Tb['root'], Z['root'], PL['root']): r.rotation_mode = 'XYZ'
for nm in 'LR': P['shoulder' + nm].rotation_mode = 'QUATERNION'
def qdir(d, rest=(0, 0, -1)): return Vector(rest).rotation_difference(Vector(d).normalized())
def wd(yaw, v):
    c, s = math.cos(-yaw), math.sin(-yaw); return (c * v[0] - s * v[1], s * v[0] + c * v[1], v[2])
pas = []
_pr = np.random.default_rng(13); FILL = [i for i in range(len(SEATS)) if not (i in (16, 17, 18, 19) and False)]
pick = [i for i in range(len(SEATS)) if _pr.random() < 0.65 and SEATS[i][0] < BX0 + 4.9]
for n_, i in enumerate(pick):
    sh = tuple(_pr.uniform(0.15, 0.95, 3)); sk = [(0.96, 0.75, 0.6), (0.85, 0.6, 0.45), (0.55, 0.38, 0.25), (0.98, 0.82, 0.7)][n_ % 4]
    R_ = props004.player(chc, 'Pass%02d' % n_, sh, tuple(_pr.uniform(0.1, 0.5, 3)), sk, tuple(_pr.uniform(0.05, 0.6, 3) * np.array([1, 0.8, 0.5])), scale=0.95)
    R_['head'] = [c for c in R_['root'].children if c.name.startswith('Head')][0]; R_['smile'] = [c for c in R_['head'].children if c.name.startswith('Smile')][0]
    R_['root'].rotation_mode = 'XYZ'; R_['seat'] = SEATS[i]; R_['ph'] = _pr.uniform(0, 6); pas.append(R_)

# ======================= oggetti =======================
plane = props013.airplane(prc, A); PLR = plane['root']
pglass = props013.sunglasses(chc, A, P['head']); tglass = props013.sunglasses(chc, A, Tb['head'], y=-0.32, z=0.08, dx=0.11, w=0.17, h=0.13)
plei = props013.lei(chc, A, P['root'], (0, -0.04, 1.40), r=0.30, tilt=0.25); tlei = props013.lei(chc, A, Tb['root'], (0, -0.30, 0.62), r=0.28, tilt=1.0, n=18, s=0.075)
case = props013.suitcase(prc, A)
gel = props013.gelato(chc, A, PL['root'], (0.30, -0.42, 1.18)); gel.scale = (0.62, 0.62, 0.62)
micro = props013.mic(chc, A, P['shoulderL'], (0, 0, -0.62))
phm = {'phone': A['dark'], 'screen': material('A13_callscr', (0.3, 0.9, 0.3), rough=0.2, emit=(0.3, 1.0, 0.4), emit_strength=2.0)}
pphone = props010.phone(chc, phm, P['shoulderR']); zphone = props010.phone(prc, phm, None)
zphone.location = (PILLOW[0] + 0.35, PILLOW[1] - 0.28, PILLOW[2] + 0.55); zphone.rotation_euler = (0, 0, 0.5)
book, book_whole, book_eaten = props013.manual(prc, A); book.location = (CX0 + 0.25, -0.2, 0.86); book.rotation_euler = (0, -0.45, PI / 2)
cart = props013.drinks_cart(prc, A); CART = (BX0 + 3.3, 0.0); cart.location = (CART[0], CART[1], 0)
belly = ball_('ZucPancia', 0.13, (0, -props012.ZR * 0.62, 0.42), Z12['zuc'], chc, parent=Z['root'], sc=(1, 0.9, 1.25))
klights = []
for k, col in enumerate([(1, 0.1, 0.8), (0.1, 0.6, 1), (1, 0.8, 0.1)]):
    l_ = bpy.data.lights.new('LuceKaraoke%d' % k, 'POINT'); o_ = bpy.data.objects.new('LuceKaraoke%d' % k, l_); prc.objects.link(o_); l_.color = col; l_.shadow_soft_size = 0.3
    o_.location = (CX0 - 0.6 + 0.8 * k, (-1) ** k * 1.2, 2.3); klights.append(l_)
def area(name, loc, size, energy, col=(1, 0.97, 0.92)):
    l_ = bpy.data.lights.new(name, 'AREA'); l_.size = size; l_.energy = energy; l_.color = col; o_ = bpy.data.objects.new(name, l_); prc.objects.link(o_); o_.location = loc; return o_
area('LuceCockpit', (CX0 + 0.3, 0, 3.2), 3.0, 110); area('LuceCabina', (BX0 + 3.5, 0, 3.0), 6.0, 520); area('LuceOspedale', (HX0 - 0.5, -1.5, 3.4), 3.5, 380)

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
T_ON, T_RING = 18.85, 29.95
show(case, [(0.0, 6.1)]); show(gel, [(7.55, 13.3)]); show(micro, [(19.4, 29.95)]); pop(micro, 19.4, 0.2)
show(pphone, [(T_RING, 31.45)]); show(PL['root'], [(7.55, 14.55)])
show(Z['root'], [(31.4, 36.45)]); show(zphone, [(31.4, 36.45)])
show(book_whole, [(0.0, 39.5)]); show(book_eaten, [(39.5, TOTAL)])
show(cart, [(20.4, 23.9)]); show(CK['kscreen'], [(T_ON, 29.95)]); show(CK['disco'], [(T_ON, 29.95)])
keys(CK['kscreen'], 'scale', [(T_ON, (1, 1, 0.01)), (T_ON + 0.35, (1, 1, 1.1)), (T_ON + 0.45, (1, 1, 1.0))])
keys(CK['disco'], 'location', [(T_ON, (CX0 - 0.5, 0, 4.5)), (T_ON + 0.5, (CX0 - 0.5, 0, 2.55)), (T_ON + 0.62, (CX0 - 0.5, 0, 2.65))])
keys(cart, 'scale', [(20.4, (1, 1, 1)), (21.0, (1, 1, 1)), (21.6, (1, 1, 0.75)), (22.1, (1, 1, 0.75)), (22.7, (0.9, 0.9, 0.45)), (23.2, (0.8, 0.8, 0.45)), (23.75, (0.3, 0.3, 0.05))])
keys(wcdoor, 'rotation_euler', [(13.3, (0, 0, -1.4)), (14.45, (0, 0, -1.4)), (14.6, (0, 0, 0.05)), (14.66, (0, 0, -0.08)), (14.72, (0, 0, 0))])
keys(CK['lever'], 'rotation_euler', [(41.2, (0, 0.5, 0)), (41.55, (0, 0.5, 0)), (41.8, (0, -0.55, 0))])
keys(CK['kbtn'], 'scale', [(18.5, (0.16, 0.16, 0.06)), (18.62, (0.16, 0.16, 0.02)), (18.9, (0.16, 0.16, 0.06))])
show(pglass, [(0.0, TOTAL)]); show(tglass, [(0.0, TOTAL)])

# ======================= pose =======================
DOWN = lambda s: (s * 0.14, 0, -1)
UP = dict(aL=(-0.35, -0.25, 1), aR=(0.35, -0.25, 1))
YX = PI / 2                                                                                          # imbardata per guardare verso +X
SPP = (CX0 - 0.42, 0.65); SPT = (CX0 - 0.42, -0.65)                                                  # sedili cockpit: Pippo a sinistra, Tumbo a destra
SEATED = dict(hL=-PI / 2, hR=-PI / 2)
def walk_air(t):
    """Pippo e Tumbo camminano verso la camera in aeroporto."""
    return (AIR[0] - 2.0, -3.2 - 0.9 * t, 0)
def pp(t):
    S_ = dict(loc=(0, 0, 0), rot=(0, 0, 0), aL=DOWN(-1), aR=DOWN(1), hL=0.0, hR=0.0, head=(0, 0, 0))
    if t < 6.1:                                                                                      # aeroporto
        w = walk_air(min(t, 4.5)); k = math.sin(t * 7.5) * (t < 4.5)
        S_.update(loc=(w[0], w[1], 0.04 * abs(k)), rot=(0, 0, 0.12), hL=0.45 * k, hR=-0.45 * k, aR=(0.35, 0.25, -0.9), aL=(-0.4 - 0.25 * (t > 4.6), -0.3, 0.3 + 0.6 * math.sin(t * 9) * (t > 4.6) * 0.5 + 0.5 * (t > 4.6)), head=(0, 0.12 * math.sin(t * 3), 0))
    elif t < 13.3: S_.update(loc=(BX0 + 5.25, -0.75, -0.03), rot=(0, 0, YX), **SEATED)
    elif t < 14.95:                                                                                  # in cabina: vedono il pilota scappare
        S_.update(loc=(BX0 + 5.25, -0.75, -0.03), rot=(0, 0, YX + 0.6 * ramp(t, 13.5, 13.8)), head=(0, 0, 0.9 * ramp(t, 13.5, 13.8)), aL=(-0.55, -0.3, 0.6), aR=(0.55, -0.3, 0.6), **SEATED)
    elif t < 15.6:                                                                                   # salto nel sedile
        u = (t - 14.95) / 0.65; S_.update(loc=(SPP[0] - 2.2 * (1 - u), SPP[1], 0.9 * math.sin(PI * u) - 0.03 * u), rot=(0, 0, YX), **UP)
    elif t < 20.4 or 24.6 <= t < 26.6 or 29.95 <= t < 31.45 or t >= 36.45:
        S_.update(loc=(SPP[0], SPP[1], -0.03), rot=(0.05, 0, YX), aL=wd(YX, (0.6, -0.15, -0.25)), aR=wd(YX, (0.6, 0.15, -0.25)), **SEATED)
        if 16.9 <= t < 18.85:
            pr = ramp(t, 17.6, 18.0) * (1 - ramp(t, 18.65, 18.85)); S_.update(rot=(0.05 + 0.3 * pr, 0, YX), aL=lerp(wd(YX, (0.6, -0.15, -0.25)), wd(YX, (0.82, -0.25, -0.62)), pr), head=(0.2 * pr, 0, -0.4 * pr))
        if 18.85 <= t < 20.4:
            k = math.sin(t * 10); S_.update(rot=(0, 0.12 * k, YX), aL=wd(YX, (0.5, -0.2, 0.55)), aR=(0.5, -0.3, 0.6 + 0.3 * k), head=(0, 0.2 * k, 0))
        if 24.6 <= t < 26.6: S_.update(aL=wd(YX, (0.75, -0.3, 0.32)), head=(0.05, 0, 0))
        if 29.95 <= t < 31.45: S_.update(aR=(0.12, -0.28, 0.95), head=(0, 0.15, 0))
        if t >= 36.45:
            look = ramp(t, 36.6, 36.9) * (1 - ramp(t, 40.7, 41.0)); pull = ramp(t, 41.2, 41.5)
            S_.update(head=(0, 0, -1.0 * look), aL=lerp(wd(YX, (0.6, -0.15, -0.25)), wd(YX, (0.62, -0.42, -0.42)), pull), rot=(0.05 - 0.15 * ramp(t, 41.55, 41.8), 0, YX))
    else: S_.update(loc=(CX0 - 30, 0, 0))
    return S_
def tp(t):
    S_ = dict(loc=(0, 0, 0), rot=(0, 0, 0), head=(0, 0, 0), tail=-1.0 + 0.5 * math.sin(t * 12))
    if t < 6.1: w = walk_air(min(t, 4.5)); S_.update(loc=(w[0] + 1.2, w[1] + 0.2, 0.05 * abs(math.sin(t * 11)) * (t < 4.5)), rot=(0, 0, -0.1), head=(-0.2, 0, 0.3 * (3.0 < t < 4.4)))
    elif t < 14.95: S_.update(loc=(BX0 + 5.25, 0.15, 0.48), rot=(0, 0, YX + 0.6 * ramp(t, 13.5, 13.8)), head=(-0.2, 0, 0.7 * ramp(t, 13.5, 13.8)))
    elif t < 15.7: u = (t - 15.05) / 0.65; S_.update(loc=(SPT[0] - 2.0 * (1 - min(1, max(0, u))), SPT[1], 0.55 + 0.9 * math.sin(PI * min(1, max(0, u)))), rot=(0, 0, YX))
    elif t < 20.4 or 24.6 <= t < 26.6 or 29.95 <= t < 31.45 or t >= 36.45:
        S_.update(loc=(SPT[0] + 0.1, SPT[1], 0.62), rot=(-0.25, 0, YX), head=(0.15, 0, 0))
        if 18.85 <= t < 20.4: S_.update(loc=(SPT[0] + 0.1, SPT[1], 0.62 + 0.18 * abs(math.sin(t * 10))), head=(0, 0.3 * math.sin(t * 10), 0))
        if t >= 36.45:
            S_.update(head=(-0.3 * ramp(t, 37.9, 38.2), 0, -0.9 * ramp(t, 37.9, 38.2) * (1 - ramp(t, 40.7, 41.0))))
    elif 20.4 <= t < 24.6:                                                                           # sul carrello, se lo mangia
        z = 1.05 * cart.scale[2] if False else None
        sc = lambda tt: (1.0 if tt < 21.0 else 0.75 if tt < 22.4 else 0.45 if tt < 23.5 else 0.05)
        chomp = abs(math.sin(t * 16)) * (20.9 < t < 23.8)
        h = 1.05 * (1.0 if t < 21.3 else 0.75 if t < 22.4 else 0.45 if t < 23.5 else 0.05) * (1 if t > 20.75 else 0) + (0.9 * math.sin(PI * min(1, max(0, (t - 20.4) / 0.35))) if t < 20.75 else 0)
        S_.update(loc=(CART[0] + 0.05, CART[1], h + 0.02), rot=(0.25 * chomp, 0, YX), head=(0.5 * chomp - 0.1, 0, 0))
    else: S_.update(loc=(CX0 - 30, 4, 0))
    return S_
def plp(t):
    """pilota."""
    S_ = dict(loc=(0, 0, 0), rot=(0, 0, 0), aL=0.0, aR=0.0, hL=0.0, hR=0.0, head=(0, 0, 0))
    if t < 13.3:
        lick = abs(math.sin(t * 6)) * (t < 11.9); sick = ramp(t, 12.05, 12.3)
        S_.update(loc=(SPP[0] - 0.05, SPP[1], -0.17), rot=(0.05 + 0.15 * sick, 0, YX), aR=-1.55 + 0.3 * sick, aL=-0.3 - 0.9 * sick, hL=-1.45, hR=-1.45, head=(0.3 * lick - 0.1 * sick, 0, -0.45 * lick))
    else:                                                                                            # corre al bagno
        u = ramp(t, 13.35, 14.5); k = math.sin(t * 24)
        S_.update(loc=(BX0 + 6.4 - 7.2 * u, 0.0, 0.05 * abs(k)), rot=(-0.15, 0, -YX), aL=1.0 * k, aR=-1.0 * k - 0.0, hL=0.8 * k, hR=-0.8 * k, head=(-0.2, 0, 0))
    return S_
def zp(t):
    sh = 0.03 * math.sin(t * 40) * (33.6 < t < 36.2)
    return dict(loc=(PILLOW[0] + 0.15 + sh, PILLOW[1] - 0.05, 0.62), rot=(-0.12, 0.08 * math.sin(t * 9) * (33.6 < t < 36.2), 0.15))
def pv(t):
    """aereo: posizione e rotazione."""
    if t < 6.1: return (AIR[0] + 6.0, 9.0, 0), (0, 0, 0), 1.0
    if t < 7.55:
        u = t - 6.1; x = AIR[0] - 35.0 + 9.0 * u + 18.0 * u * u; z = max(0.0, (u - 0.75) * 4.5) ** 1.4
        return (x, 9.0, z), (0, -0.16 * ramp(u, 0.6, 1.0), 0), 1.0 - ramp(u, 1.0, 1.4)
    if t < 42.4: return (TOWN[0] - 400, 0, 60), (0, 0, 0), 0.0
    u = t - 42.4; x = TOWN[0] - 110 + 30.0 * u; z = 42.0 - 5.5 * u
    return (x, HOSP[1] - 10 + 1.2 * u, z), (0.12 * math.sin(u * 1.5), 0.12, 0.03 * u), ramp(u, 0.3, 1.2)

# ======================= chiavi =======================
TR = Tb['root']; ZRt = Z['root']
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
    b_ = 1.0 + 0.3 * ramp(t, 23.4, 23.9); Tb['body'].scale = (b_, b_, 1.0 + 0.15 * ramp(t, 23.4, 23.9)); Tb['body'].keyframe_insert('scale', frame=f)
    if 7.5 < t < 14.6:
        c = plp(t); r = PL['root']; r.location = c['loc']; r.rotation_euler = c['rot']; r.keyframe_insert('location', frame=f); r.keyframe_insert('rotation_euler', frame=f)
        for nm in 'LR':
            PL['shoulder' + nm].rotation_euler = (c['a' + nm], 0, 0); PL['shoulder' + nm].keyframe_insert('rotation_euler', frame=f)
            PL['hip' + nm].rotation_euler = (c['h' + nm], 0, 0); PL['hip' + nm].keyframe_insert('rotation_euler', frame=f)
        plhead.rotation_euler = c['head']; plhead.keyframe_insert('rotation_euler', frame=f)
        sick = ramp(t, 12.05, 12.3); gg = 1 + 0.06 * math.sin(t * 30) * sick * (t < 13.3)
        pltorso.scale = (gg, gg, 1); pltorso.keyframe_insert('scale', frame=f)
        lick = abs(math.sin(t * 6)) * (t < 11.9)
        plsmile.scale = (0.07, 0.025, 0.025 + 0.035 * lick + 0.03 * sick); plsmile.keyframe_insert('scale', frame=f)
        for e_ in pleyes: e_.scale = (0.055 * (1 + 0.5 * sick), 0.03, 0.07 * (1 + 0.6 * sick)); e_.keyframe_insert('scale', frame=f)
    if 31.3 < t < 36.5:
        z = zp(t); ZRt.location = z['loc']; ZRt.rotation_euler = z['rot']; ZRt.keyframe_insert('location', frame=f); ZRt.keyframe_insert('rotation_euler', frame=f)
        talk = (31.5 < t < 33.4) or (33.7 < t < 36.2); Z['mouth'].scale = (0.045, 0.02, 0.022 + 0.05 * abs(math.sin(t * 15)) * talk); Z['mouth'].keyframe_insert('scale', frame=f)
        Z['eyes'].scale = (1.0 + 0.3 * (t > 33.6),) * 3; Z['eyes'].keyframe_insert('scale', frame=f)
    l, e, g = pv(t); PLR.location = l; PLR.rotation_euler = e; PLR.keyframe_insert('location', frame=f); PLR.keyframe_insert('rotation_euler', frame=f)
    plane['gear'].scale = (1, 1, max(0.001, g)); plane['gear'].keyframe_insert('scale', frame=f)
    for R_ in pas:                                                                                   # passeggeri
        x, y = R_['seat']; scared = ramp(t, 26.7, 27.0) * (1 - ramp(t, 29.9, 30.2)); look = ramp(t, 13.45, 13.75)
        k = math.sin(t * 20 + R_['ph']) * scared
        r = R_['root']; r.location = (x - 0.05, y, -0.17 + 0.03 * abs(k)); r.rotation_euler = (0, 0.05 * k, YX); r.keyframe_insert('location', frame=f); r.keyframe_insert('rotation_euler', frame=f)
        for nm, sg in (('L', 1), ('R', -1)):
            R_['shoulder' + nm].rotation_euler = (-0.25 - 2.7 * scared + 0.25 * k * sg, 0, 0); R_['shoulder' + nm].keyframe_insert('rotation_euler', frame=f)
            R_['hip' + nm].rotation_euler = (-1.25, 0, 0); R_['hip' + nm].keyframe_insert('rotation_euler', frame=f)
        R_['head'].rotation_euler = (0.1 * scared, 0.15 * k, 0.6 * look * (1 if y > 0 else -1) * (1 - ramp(t, 15.0, 15.2)) + 0.2 * math.sin(t * 0.7 + R_['ph']) * (1 - scared)); R_['head'].keyframe_insert('rotation_euler', frame=f)
        R_['smile'].scale = (0.07, 0.025, 0.025 + 0.06 * scared); R_['smile'].keyframe_insert('scale', frame=f)
    on = 18.85 <= t < 29.95
    for k_, l_ in enumerate(klights): l_.energy = (260.0 * (0.5 + 0.5 * math.sin(t * 9 + k_ * 2.1)) if on else 0.0); l_.keyframe_insert('energy', frame=f)
    if on: CK['disco'].rotation_euler = (0, 0, t * 2.0); CK['disco'].keyframe_insert('rotation_euler', frame=f)

_last = {}
def _ex(key, fn, t, k):
    if key in _last and t - 0.06 > _last[key][1]: fn(fr(t - 0.06), **_last[key][0])
    fn(fr(t), **k); _last[key] = (k, t)
def pex(t, **k): _ex('p', lambda f, **kk: pippo.express(P, f, **kk), t, k)
def tex(t, **k): _ex('t', lambda f, **kk: tumbo.tumbo_express(Tb, f, **kk), t, k)
pex(0.0, smile=1.0, brow_lift=0.4, mouth_open=0.3); pex(13.4, brow=-0.6, brow_lift=0.8, eye_scale=1.3, mouth_open=0.7); pex(15.0, smile=1.0, brow=0.8, mouth_open=0.5)
pex(17.5, smile=1.0, brow=0.6, eye_open=0.8); pex(18.9, smile=1.0, mouth_open=1.0, brow_lift=0.5); pex(24.7, smile=1.0, mouth_open=0.7, brow=0.4)
pex(30.0, brow_lift=0.6, eye_scale=1.2, mouth_open=0.3); pex(36.5, brow=-0.4, brow_lift=0.6, eye_scale=1.25, mouth_open=0.2, look=(-0.7, 0)); pex(39.5, brow=-0.7, brow_lift=0.7, eye_scale=1.35, mouth_open=0.6, look=(-0.6, -0.3))
pex(41.0, brow=1.0, mouth_open=0.8, eye_open=0.8, look=(0, 0))
tex(0.0, tongue=1.0); tex(13.4, eye_scale=1.35, brow=-0.6); tex(15.0, tongue=0.8); tex(18.9, tongue=1.0, eye_scale=1.2); tex(20.5, tongue=0.0, eye_scale=1.2, brow=0.6); tex(23.9, tongue=1.0, eye_open=0.6)
tex(36.5, eye_open=0.8); tex(37.9, eye_open=0.7, brow=-0.3, look=(0.4, -0.6)); tex(39.6, tongue=0.8, eye_open=0.6, look=(0, 0)); tex(41.0, eye_scale=1.4, brow=-0.7)

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
def burst(name, mat, t0, dur, c0, n, vmax, sc, grav=4.9, up=1.0, mesh=None):
    for k in range(n):
        v = np.array([er.uniform(-vmax, vmax), er.uniform(-vmax, vmax), er.uniform(0.3, 1.0) * vmax * up])
        streak(name, sc, mat, t0, t0 + dur, lambda t, v=v: ((c0[0] + v[0] * (t - t0), c0[1] + v[1] * (t - t0), max(0.03, c0[2] + v[2] * (t - t0) - grav * (t - t0) ** 2)),), mesh=mesh)
for k in range(8):                                                                                   # gocce di gelato
    ph = k / 8; streak('GocciaGelato', (0.04, 0.04, 0.06), A['pist'], 8.0, 12.0, lambda t, ph=ph: ((SPP[0] + 0.45, SPP[1] + 0.3, 1.4 - 1.3 * ((t * 0.9 + ph) % 1.0)),))
for k in range(6):                                                                                   # brontolio della pancia
    ph = k / 6; streak('Spirale', (0.05, 0.05, 0.05), A['pist'], 12.1, 13.3, lambda t, ph=ph: ((SPP[0] + 0.25 + 0.35 * math.cos(t * 9 + ph * 6.28), SPP[1] + 0.35 * math.sin(t * 9 + ph * 6.28), 0.95 + 0.25 * ph),))
for k in range(3): burst('Lattina', A['can'][k], 21.0 + 0.9 * k, 0.9, (CART[0], CART[1], 1.1), 4, 1.8, (0.05, 0.05, 0.07), mesh=shared_mesh('cyl:1:1'))
for k in range(16):                                                                                  # note musicali del karaoke
    ph = k / 16; streak('Nota', (0.06, 0.02, 0.06), A['kara'] if k % 2 else A['btn'][2], T_ON, 29.95, lambda t, ph=ph: ((CX0 + 0.3 + 0.8 * math.sin(t * 2 + ph * 9), 1.4 * math.cos(t * 1.6 + ph * 7), 1.2 + 1.6 * ((t * 0.5 + ph) % 1.0)),))
for k in range(8):                                                                                   # vibrazione del telefono
    ph = k / 8; streak('Squillo', (0.03, 0.03, 0.03), A['btn'][1], T_RING, 31.45, lambda t, ph=ph: ((SPP[0] + 0.1, SPP[1] - 0.3 - 0.25 * ((t * 2 + ph) % 1.0), 1.75 + 0.15 * math.sin(ph * 6.28)),))
for k in range(10):                                                                                  # scia dei motori nel finale
    ph = k / 10
    def fn(t, ph=ph):
        l, e, g = pv(t); u = (t * 2.2 + ph) % 1.0
        return ((l[0] + 0.9 - 4.0 - 10 * u, l[1] + ((-1) ** k) * 3.2, l[2] + 2.3 - 1.2), (0.35 + 0.8 * u,) * 3)
    streak('ScieMotore', (0.4, 0.4, 0.4), M['cloudw'], 42.4, TOTAL, fn)

# ======================= camera =======================
def Z0(t): return (0, 0, 0)
def PV(t): return pv(t)[0]
SHOTS = [  # t0, t1, sub cam, p0, p1, sub mira, a0, a1, lente, f
    (0.0, 3.0, Z0, (AIR[0] - 1.0, -12.5, 1.4), (AIR[0] - 1.0, -12.0, 1.4), Z0, (AIR[0] - 1.2, -4.0, 1.5), (AIR[0] - 1.2, -5.5, 1.3), 30, 6),
    (3.0, 4.3, Z0, (AIR[0] - 0.4, -9.6, 0.6), (AIR[0] - 0.4, -9.4, 0.6), Z0, (AIR[0] - 0.8, -6.6, 0.55), (AIR[0] - 0.8, -6.9, 0.55), 45, 4),
    (4.3, 6.1, Z0, (AIR[0] - 0.5, -12.0, 1.3), (AIR[0] - 0.5, -11.4, 1.35), Z0, (AIR[0] - 1.4, -7.3, 1.2), (AIR[0] - 1.4, -7.3, 1.2), 30, 6),
    (6.1, 7.55, Z0, (AIR[0] - 6.0, -12.0, 1.4), (AIR[0] - 4.0, -12.0, 1.6), PV, (0, 0, 2.5), (0, 0, 3.5), 26, 11),
    (7.55, 10.2, Z0, (CX0 + 2.3, 0.95, 1.55), (CX0 + 2.2, 0.95, 1.55), Z0, (SPP[0] + 0.15, SPP[1] - 0.05, 1.4), (SPP[0] + 0.15, SPP[1] - 0.05, 1.45), 35, 5),
    (10.2, 12.0, Z0, (CX0 + 1.9, 0.8, 1.55), (CX0 + 1.85, 0.8, 1.55), Z0, (SPP[0] + 0.2, SPP[1] - 0.05, 1.55), (SPP[0] + 0.2, SPP[1] - 0.05, 1.57), 45, 5),
    (12.0, 13.3, Z0, (CX0 + 1.75, 0.7, 1.55), (CX0 + 1.7, 0.7, 1.55), Z0, (SPP[0] + 0.05, SPP[1] - 0.02, 1.55), (SPP[0] + 0.05, SPP[1] - 0.02, 1.55), 55, 4),
    (13.3, 14.95, Z0, (BX0 + 7.0, -0.3, 1.75), (BX0 + 6.9, -0.25, 1.75), Z0, (BX0 + 1.0, 0.0, 1.0), (BX0 + 0.5, 0.0, 1.0), 26, 8),
    (14.95, 16.9, Z0, (CX0 + 3.0, 0.0, 1.55), (CX0 + 2.9, 0.0, 1.55), Z0, (CX0 - 0.45, 0.0, 1.1), (CX0 - 0.45, 0.0, 1.1), 22, 8),
    (16.9, 18.85, Z0, (CX0 + 2.0, 0.45, 1.4), (CX0 + 1.95, 0.45, 1.4), Z0, (CX0 + 0.15, 0.3, 0.92), (CX0 + 0.15, 0.3, 0.92), 24, 6),
    (18.85, 20.4, Z0, (CX0 + 3.3, 0.0, 1.75), (CX0 + 3.2, 0.0, 1.8), Z0, (CX0 - 1.0, 0.0, 1.35), (CX0 - 1.0, 0.0, 1.45), 20, 8),
    (20.4, 24.6, Z0, (BX0 + 5.6, -0.25, 1.6), (BX0 + 5.4, -0.2, 1.5), Z0, (CART[0], CART[1], 1.2), (CART[0], CART[1], 0.7), 34, 6),
    (24.6, 26.6, Z0, (CX0 + 1.9, 0.85, 1.6), (CX0 + 1.85, 0.85, 1.6), Z0, (SPP[0] + 0.05, SPP[1] - 0.05, 1.5), (SPP[0] + 0.05, SPP[1] - 0.05, 1.5), 40, 5),
    (26.6, 29.95, Z0, (BX0 + 7.0, 0.0, 1.95), (BX0 + 6.8, 0.0, 1.9), Z0, (BX0 + 2.5, 0.0, 1.35), (BX0 + 2.5, 0.0, 1.35), 22, 8),
    (29.95, 31.45, Z0, (CX0 + 1.65, 0.55, 1.7), (CX0 + 1.6, 0.55, 1.7), Z0, (SPP[0] + 0.05, SPP[1] - 0.12, 1.68), (SPP[0] + 0.05, SPP[1] - 0.12, 1.68), 42, 4),
    (31.45, 33.6, Z0, (HX0 - 0.2, -3.6, 1.4), (HX0 - 0.3, -3.3, 1.4), Z0, (PILLOW[0] + 0.2, 0.0, 1.05), (PILLOW[0] + 0.2, 0.0, 1.05), 34, 5),
    (33.6, 36.45, Z0, (HX0 - 0.4, -2.0, 1.25), (HX0 - 0.45, -1.8, 1.25), Z0, (PILLOW[0] + 0.15, 0.0, 1.2), (PILLOW[0] + 0.15, 0.0, 1.2), 45, 4),
    (36.45, 37.9, Z0, (CX0 + 3.0, 0.0, 1.55), (CX0 + 2.95, 0.0, 1.55), Z0, (CX0 - 0.4, 0.0, 1.15), (CX0 - 0.4, 0.0, 1.15), 24, 6),
    (37.9, 39.5, Z0, (CX0 + 1.9, -0.5, 1.3), (CX0 + 1.85, -0.5, 1.3), Z0, (CX0 - 0.15, -0.45, 1.0), (CX0 - 0.15, -0.45, 1.0), 30, 5),
    (39.5, 40.9, Z0, (CX0 + 0.95, -0.35, 1.38), (CX0 + 0.93, -0.35, 1.37), Z0, (CX0 + 0.25, -0.2, 0.9), (CX0 + 0.25, -0.2, 0.9), 50, 5),
    (40.9, 42.4, Z0, (CX0 + 1.8, 0.75, 1.45), (CX0 + 1.75, 0.75, 1.45), Z0, (CX0 + 0.15, 0.25, 0.95), (CX0 + 0.15, 0.25, 0.95), 30, 6),
    (42.4, 46.1, PV, (-4.0, -26.0, 3.0), (-2.0, -26.0, 3.5), PV, (6.0, 0.0, -2.5), (9.0, 0.0, -4.0), 30, 22),
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
for l_ in klights: set_interp(l_, 'CONSTANT')
lookdev.upgrade(scene, 720, 1280, samples=12, world=0.36, sun_e=6.5, exposure=-0.1)
os.makedirs('../t013', exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath('../t013/pippo_t013.blend')); print('SAVED')
