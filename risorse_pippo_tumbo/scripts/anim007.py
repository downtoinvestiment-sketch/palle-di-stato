"""Test 007 - PIPPO E IL NANO DA GIARDINO DEL VICINO (la guerra della staccionata). Salva ../t007/pippo_t007.blend
Personaggi: modelli ESISTENTI (pippo.py, tumbo.py) invariati."""
import sys, math, os
sys.path.insert(0, os.path.dirname(__file__))
import bpy, numpy as np
from mathutils import Vector, Euler, Matrix
from common import *
from render_setup import *
import set004, props004, props006, props007, pippo, tumbo
from set004 import obj, bx, cyl, ball_, MB

FPS = 24; TOTAL = 68.5; NF = int(TOTAL * FPS)
def fr(t): return max(1, int(round(t * FPS)) + 1)
def sm(x): x = min(1.0, max(0.0, x)); return x * x * (3 - 2 * x)
def ramp(t, a, b): return sm((t - a) / (b - a))
def lerp(a, b, u): return tuple(a[i] + (b[i] - a[i]) * u for i in range(len(a)))
def add(a, b): return tuple(a[i] + b[i] for i in range(3))
def eb_(u): u = min(1.0, max(0.0, u)); c1 = 1.6; return 1 + (c1 + 1) * (u - 1) ** 3 + c1 * (u - 1) ** 2
def face(dx, dy): return math.atan2(dx, -dy)
PI = math.pi

reset_scene(); scene = bpy.context.scene
setup_render(scene, 1080, 1920, samples=16, fps=FPS, frames=NF); scene.frame_end = NF
scene.eevee.shadow_resolution_scale = 0.25
rng = np.random.default_rng(31)
M = set004.make_mats(); K = props006.mats006(); N = props007.mats007()
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

# ======================= ambiente: due giardini =======================
bx('Prato', (-140, -140, -0.30), (140, 140, 0.0), M['park'], envc)
def house_at(x, y, rotz, wi, ri, si, two, w=None, d=None):
    w = w or rng.uniform(4.6, 5.6); d = d or rng.uniform(4.0, 4.8)
    mb = MB(set004.house_mats(M, wi, ri, si)); set004.house_geo(mb, w, d, 4.5 if two else 2.9, two, rng); return mb.build('Casa', envc, (x, y, 0), rotz)
NH = (1.5, 10.0); NW, ND = 6.0, 5.0; DOORX = NH[0] - NW * 0.22; FRONT = NH[1] - ND / 2          # casa del vicino
house_at(NH[0], NH[1], 0.0, 3, 0, 0, True, NW, ND)
house_at(20.5, 10.5, 0.0, 1, 3, 2, False, 5.2, 4.4)                                               # casa della vecchietta (il vicino sbagliato)
house_at(-15.5, -5.0, PI / 2, 0, 0, 1, True, 5.0, 4.0)                                            # casa di Pippo
for x in range(-34, 44, 9): house_at(x + rng.uniform(-1, 1), 27 + rng.uniform(0, 2), 0.0, int(rng.integers(0, 6)), int(rng.integers(0, 4)), int(rng.integers(0, 5)), bool(rng.integers(0, 2)))
for x in range(-34, 44, 9): house_at(x + rng.uniform(-1, 1), -35 - rng.uniform(0, 2), PI, int(rng.integers(0, 6)), int(rng.integers(0, 4)), int(rng.integers(0, 5)), bool(rng.integers(0, 2)))
def tower_at(x, y, rz=0.0):
    tw = rng.uniform(3.6, 4.6); ti = int(rng.integers(0, len(M['tower']))); h = rng.uniform(11, 26)
    mb = MB([M['tower'][ti], M['window'], M['frame'], M['concrete'], M['dark'], M['shutter'][int(rng.integers(0, 5))]])
    set004.tower_geo(mb, tw, h, rng); mb.build('Palazzo', envc, (x, y, 0), rz)
for x in range(-48, 56, 11): tower_at(x, 42 + rng.uniform(0, 4), 0.0); tower_at(x + 4, -50 - rng.uniform(0, 4), PI)
for y in range(-30, 36, 11): tower_at(46 + rng.uniform(0, 3), y, -PI / 2); tower_at(-46 - rng.uniform(0, 3), y, PI / 2)
def tree(x, y, s=1.0):
    cyl('Tronco', 0.16 * s, 1.5 * s, (x, y, 0.75 * s), M['bark'], envc)
    for (dx, dy, dz, r) in ((0, 0, 2.1, 0.95), (0.5, 0.1, 1.75, 0.7), (-0.5, -0.1, 1.8, 0.72)):
        ball_('Chioma', r * s, (x + dx * s, y + dy * s, dz * s), M['leaf'][int(rng.integers(0, 3))], envc)
for (x, y) in ((-9.5, 4.5), (-10.5, -8.5), (11.0, -9.0), (26.0, 3.0), (-22, 12), (30, -12), (-26, -16), (14.5, 17), (-9, 18.5), (36, 14)): tree(x, y, rng.uniform(1.0, 1.5))
# recinto basso della vecchietta e la sua aiuola
pm = MB([M['frame'], M['soil'], M['flower'][0], M['flower'][1], M['flower'][2], M['hedge']])
for yy in np.arange(0.2, 13.0, 0.22): pm.box((12.6, yy, 0.36), (0.04, 0.10, 0.72), 0)
for zz in (0.22, 0.52): pm.box((12.63, 6.6, zz), (0.03, 12.9, 0.06), 0)
BED = (17.5, 3.2)
pm.box((BED[0], BED[1], 0.18), (2.4, 1.6, 0.36), 1)
for k in range(26): pm.box((BED[0] + rng.uniform(-1.05, 1.05), BED[1] + rng.uniform(-0.65, 0.65), 0.44 + rng.uniform(0, 0.12)), (0.13, 0.13, 0.13), 2 + k % 3)
for k in range(8): pm.box((BED[0] + rng.uniform(-1.0, 1.0), BED[1] + rng.uniform(-0.6, 0.6), 0.40), (0.3, 0.3, 0.12), 5)
pm.build('GiardinoNonna', envc)
# piedistallo del nano, porta del vicino, citofono rotto
G0P = (7.0, 2.2)
cyl('Piedistallo', 0.32, 0.25, (G0P[0], G0P[1], 0.125), M['stone'], envc)
obj('PortaBuio', set004.box_c(), (DOORX, FRONT - 0.105, 1.12), (0.68, 0.05, 1.66), M['dark'], envc)
hinge = empty('PortaCardine', (DOORX - 0.34, FRONT - 0.15, 0.3), None, prc)
obj('PortaAnta', set004.box_c(), (0.34, 0, 0.82), (0.68, 0.05, 1.64), M['door'], prc, parent=hinge)
obj('PortaPomello', set004.box_c(), (0.58, -0.04, 0.78), (0.07, 0.05, 0.07), M['stone'], prc, parent=hinge)
obj('CitofonoPlacca', set004.box_c(), (DOORX + 0.62, FRONT - 0.03, 1.45), (0.16, 0.03, 0.24), K['steel'], envc)
cito = empty('Citofono', (DOORX + 0.62, FRONT - 0.07, 1.42), None, prc)
obj('CitofonoFilo', set004.box_c(), (0, 0, -0.16), (0.015, 0.015, 0.32), K['dark'], prc, parent=cito)
obj('CitofonoCassa', set004.box_c(), (0, 0, -0.40), (0.14, 0.05, 0.20), M['frame'], prc, parent=cito)
for k in range(3): obj('CitofonoTasto', set004.box_c(), (0, -0.03, -0.34 - 0.05 * k), (0.07, 0.02, 0.03), K['dark'], prc, parent=cito)

# ======================= staccionata a piani =======================
TH = 2.4; X0, X1 = -12.0, 12.3
tiers = [props007.fence_tier(prc, N, X0, X1, TH, 5 + k) for k in range(4)]
for k, t_ in enumerate(tiers): t_.location = (0.04 * (k % 2), 0.02 * k, k * TH - 0.02 * k)
merli = props007.battlements(prc, N, X0, X1, 4 * TH - 0.1)
tierN = props007.fence_tier(prc, N, 12.7, 19.2, TH, 77, name='StaccionataFinale'); tierN.rotation_euler = (0, 0, PI / 2); tierN.location = (-3.4, 0, 0)
T_F1, T_F2, T_F3, T_F4, T_MER, T_FN = 16.5, 20.1, 24.8, 25.0, 28.3, 67.3

# ======================= personaggi =======================
P = pippo.build_pippo(chc); Tb = tumbo.build_tumbo(chc, scale=0.75)
for r in (P['root'], Tb['root']): r.rotation_mode = 'XYZ'
for nm in 'LR': P['shoulder' + nm].rotation_mode = 'QUATERNION'
def qdir(d, rest=(0, 0, -1)): return Vector(rest).rotation_difference(Vector(d).normalized())
man = props004.player(chc, 'Neigh', (0.96, 0.96, 0.96), (0.25, 0.25, 0.30), (0.96, 0.42, 0.36), (0.15, 0.10, 0.07), scale=1.0)
mhead = [c for c in man['root'].children if c.name.startswith('Head')][0]
for sx in (-1, 1): obj('Brow', set004.box_c(), (sx * 0.10, -0.25, 0.15), (0.13, 0.03, 0.035), M['dark'], chc, rot=(0, sx * 0.45, 0), parent=mhead)
hammer = empty('Martello', (0, 0, -0.66), man['shoulderR'], prc)
obj('MartelloManico', set004.box_c(), (0, -0.18, 0), (0.04, 0.42, 0.04), N['plank'][3], prc, parent=hammer); obj('MartelloTesta', set004.box_c(), (0, -0.40, 0), (0.09, 0.10, 0.22), K['steel'], prc, parent=hammer)
G = props006.granny(chc, K)
bag = obj('Borsetta', set004.box_c(), (0, -0.05, -0.80), (0.30, 0.12, 0.26), N['bag'], prc, parent=G['shoulderR'])

# ======================= oggetti di scena =======================
gm0 = props007.gnome_mesh(N, 0, 0); hm = props007.heart_mesh(N)
G0 = bpy.data.objects.new('Gianfranco', gm0); prc.objects.link(G0); G0.scale = (1.35, 1.35, 1.35); G0.rotation_mode = 'XYZ'
gmeshes = [props007.gnome_mesh(N, h, c) for (h, c) in ((0, 0), (1, 1), (2, 2), (0, 1), (1, 0))]
army = []
for i in range(20):
    for j in range(10):
        g = bpy.data.objects.new('Nano', gmeshes[int(rng.integers(0, 5))]); prc.objects.link(g)
        g.location = (-3.0 + i * 0.56 + rng.uniform(-0.05, 0.05), 13.4 + j * 0.56 + rng.uniform(-0.05, 0.05), 0); g.rotation_euler = (0, 0, PI / 2 + rng.uniform(-0.35, 0.35))
        s_ = rng.uniform(0.9, 1.2); g.scale = (s_, s_, s_); army.append(g)
namesign = props007.sign(prc, N, 'GIANFRANCO', w=1.35, h=0.36, size=0.19, post=0.55); namesign.location = (7.95, 1.95, 0); namesign.rotation_euler = (0, 0, -0.2)
L1, TH1 = 2.75, -0.38; L2, TH2 = 5.3, -0.347
lad1 = props007.ladder(prc, N, L1, 'Scala1'); lad1.location = (7.0, -1.1, 0); lad1.rotation_euler = (TH1, 0, 0)
lad2 = props007.ladder(prc, N, L2, 'Scala2'); lad2.location = (7.0, -1.9, 0)
lad3 = props007.ladder(prc, N, L1, 'Scala3'); lad3.location = (-4.45, 15.6, 0); lad3.rotation_euler = (TH1, 0, -PI / 2)
TRP = (4.0, -2.6)
tramp, tmat, ttorn = props007.trampoline(prc, N); tramp.location = (TRP[0], TRP[1], 0)
CAT = (-5.5, -6.0); LAND = (BED[0], BED[1], 1.75); CYAW = face(LAND[0] - CAT[0], LAND[1] - CAT[1])
cat, catarm = props007.catapult(prc, N); cat.location = (CAT[0], CAT[1], 0); cat.rotation_euler = (0, 0, CYAW)
BAL = (-2.5, -1.7)
balroot, bals, balstr = props007.balloons(prc, N, P['root'], (0.36, 0, 1.93))
NAIL = (BAL[0] + 1.0, -0.07, 2 * TH - 0.1)
obj('Chiodo', set004.box_c(), (NAIL[0], -0.10, NAIL[2]), (0.05, 0.14, 0.05), K['steel'], prc)
em = MB([N['white'], N['bal'][0]]); em.b2((-0.19, -0.015, 0), (0.19, 0.015, 1.0), 0)
for k in range(4): em.b2((-0.10 + 0.07 * k, -0.02, 0.3 + 0.12 * k), (-0.06 + 0.07 * k, 0.02, 0.36 + 0.12 * k), 1)      # cuoricini sulle mutande
elast = em.build('Mutande', prc); elast.location = NAIL
waist = empty('Vita', (0, 0.22, 0.80), P['root'], prc)
ec = elast.constraints.new('TRACK_TO'); ec.target = waist; ec.track_axis = 'TRACK_Z'; ec.up_axis = 'UP_Y'
shovel = empty('Pala', (0, 0, -0.60), P['shoulderR'], prc)
obj('PalaManico', set004.box_c(), (0, -0.25, 0), (0.04, 1.1, 0.04), N['plank'][2], prc, parent=shovel); obj('PalaLama', set004.box_c(), (0, -0.92, 0), (0.26, 0.32, 0.03), K['steel'], prc, parent=shovel)
HOLE = (2.0, -0.75)
hole = cyl('Buca', 0.5, 0.02, (HOLE[0], HOLE[1], 0.012), M['dark'], prc); mound = ball_('Mucchio', 0.6, (HOLE[0] + 1.0, HOLE[1] - 0.5, 0.0), N['dirt'], prc, sc=(1, 0.8, 0.5))
SEP = (3.2, 3.2)
cyl('FossaBordo', 0.62, 0.05, (SEP[0], SEP[1], 0.025), M['concrete'], envc); cyl('FossaBuco', 0.5, 0.02, (SEP[0], SEP[1], 0.055), M['dark'], envc)
lid = cyl('FossaTappo', 0.52, 0.07, (SEP[0], SEP[1], 0.09), M['stone'], prc); lid.rotation_mode = 'XYZ'
sepsign = props007.sign(prc, N, 'FOSSA BIOLOGICA', w=1.7, h=0.34, size=0.15, post=0.75); sepsign.location = (4.3, 4.4, 0); sepsign.rotation_euler = (0, 0, 0.75)
goo = empty('Liquame', (0, 0, 0), P['head'], prc)
for (x, y, z, r, sc) in ((0.0, -0.05, 0.62, 0.16, (1.3, 1.2, 0.5)), (0.2, -0.22, 0.38, 0.09, (1, 0.6, 1.3)), (-0.24, -0.12, 0.2, 0.10, (0.8, 0.8, 1.4)), (0.1, 0.25, 0.45, 0.13, (1.2, 1, 0.8))):
    ball_('LiquameG', r, (x, y, z), N['goo'], prc, parent=goo, sc=sc)
goob = empty('LiquameCorpo', (0, 0, 0), P['body'], prc)
for (x, y, z, r, sc) in ((0.12, -0.2, 0.45, 0.11, (1, 0.6, 1.5)), (-0.15, -0.19, 0.2, 0.09, (1, 0.6, 1.4)), (0.0, 0.2, 0.5, 0.13, (1.4, 0.6, 1.2))):
    ball_('LiquameG', r, (x, y, z), N['goo'], prc, parent=goob, sc=sc)
bub = empty('Sogno', (2.0, -1.2, 2.3), None, prc)
for (x, z, r) in ((0, 0, 0.75), (0.7, 0.1, 0.55), (-0.7, 0.05, 0.55), (0.3, 0.5, 0.5), (-0.35, 0.45, 0.5)): ball_('SognoN', r, (x, 0.3, z), N['bubble'], prc, parent=bub, sc=(1, 0.3, 1))
for k, (y, z, r) in enumerate(((-0.6, -1.5, 0.10), (-0.4, -1.2, 0.15), (-0.2, -0.9, 0.2))): ball_('SognoB', r, (0, y, z), N['bubble'], prc, parent=bub)
gd = bpy.data.objects.new('NanoSogno', gm0); prc.objects.link(gd); gd.parent = bub; gd.location = (0, -0.05, -0.38); gd.scale = (1.1, 1.1, 1.1)

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
def reshow(o, intervals):
    for q in [o] + list(desc(o)): q.animation_data_clear()
    show(o, intervals)
def grow(o, t, d=0.35):
    """la staccionata cresce da terra (solo in altezza) con un rimbalzo."""
    for (tt_, v) in ((t, 0.0001), (t + 0.6 * d, 1.15), (t + d, 1.0)):
        o.scale = (1, 1, v); o.keyframe_insert('scale', frame=fr(tt_))
for t_, tm in zip(tiers, (T_F1, T_F2, T_F3, T_F4)): show(t_, [(tm, TOTAL)]); grow(t_, tm)
for k, o_ in enumerate(merli): show(o_, [(T_MER + 0.15 * k, TOTAL)]); pop(o_, T_MER + 0.15 * k)
show(tierN, [(T_FN, TOTAL)]); grow(tierN, T_FN, 0.3)
show(namesign, [(11.3, 16.4)]); pop(namesign, 11.3)
show(lad1, [(17.9, 21.5)]); pop(lad1, 17.9); show(lad2, [(22.15, 30.85)]); pop(lad2, 22.15); show(lad3, [(67.85, TOTAL)]); pop(lad3, 67.85, 0.2)
show(tramp, [(31.3, 42.3)]); reshow(tmat, [(31.3, 33.2)]); reshow(ttorn, [(33.2, 42.3)]); pop(tramp, 31.3)
show(cat, [(42.3, 46.55)]); pop(cat, 42.3, 0.25)
show(balroot, [(46.75, 49.7)]); pop(balroot, 46.75); show(elast, [(48.6, 51.5)])
show(shovel, [(51.5, 52.2)]); show(hole, [(51.75, TOTAL)]); show(mound, [(51.75, TOTAL)]); pop(mound, 51.75)
show(goo, [(52.9, TOTAL)]); show(goob, [(52.9, TOTAL)]); show(bub, [(8.45, 9.45)]); pop(bub, 8.5, 0.3)
show(army, [(61.85, TOTAL)]); show(man['root'], [(12.75, 21.5), (28.7, 30.85), (59.5, 63.0)]); show(G['root'], [(43.4, 46.55)])
reshow(hammer, [(16.4, 21.5)])
for k, b_ in enumerate(bals):
    if k in (2, 5):
        tp_ = 47.9 if k == 2 else 48.25
        for (tt_, v) in ((tp_ - 0.04, 1.0), (tp_, 1.6), (tp_ + 0.05, 0.0001)): b_.scale = (0.30 * v, 0.30 * v, 0.36 * v); b_.keyframe_insert('scale', frame=fr(tt_))

# ======================= pose =======================
DOWN = lambda s: (s * 0.14, 0, -1)
def lad_pose(base, th, d, off=0.2):
    u = (0, -math.sin(th), math.cos(th)); n = (0, -math.cos(th), -math.sin(th))
    return (base[0], base[1] + u[1] * d + n[1] * off, base[2] + u[2] * d + n[2] * off), (-th, 0, PI)
def th2(t): return TH2 + 1.8 * ((t - 25.2) / 0.65) ** 2 if t > 25.2 else TH2
TH2END = TH2 + 1.8
def cat_tip(a):
    c, s = math.cos(CYAW), math.sin(CYAW); ly = -0.2 + 2.6 * math.cos(a); lz = 1.45 + 2.6 * math.sin(a)
    return (CAT[0] - s * ly, CAT[1] + c * ly, lz)
def cat_ang(t): return -0.22 if t < 43.6 else -0.22 + 2.2 * min(1.0, (t - 43.6) / 0.12)
P0F = cat_tip(1.0)
def flight(t):
    u = min(1.0, max(0.0, (t - 43.66) / 0.79)); return (P0F[0] + (LAND[0] - P0F[0]) * u, P0F[1] + (LAND[1] - P0F[1]) * u, P0F[2] + (LAND[2] - P0F[2]) * u + 4 * 13.0 * u * (1 - u))
def jump_z(t):
    for (a, b, h) in ((31.7, 32.1, 1.2), (32.1, 32.6, 2.8), (32.6, 33.2, 5.0)):
        if a <= t < b: u = (t - a) / (b - a); return 0.9 + 4 * h * u * (1 - u), u, h
    return 0.9, 0.0, 0.0
def bal_z(t): return 3.9 * sm((t - 47.0) / 1.3) - 0.9 * ramp(t, 48.2, 48.6)
def hang_z(t): tau = t - 48.6; return 2.35 + 0.55 * math.exp(-1.3 * tau) * math.cos(8.5 * tau)

def pp(t):
    S_ = dict(loc=(0, 0, 0), rot=(0, 0, 0), aL=DOWN(-1), aR=DOWN(1), hL=0.0, hR=0.0, head=(0, 0, 0))
    CLASP = dict(aL=(0.30, -0.8, 0.30), aR=(-0.30, -0.8, 0.30)); HUG = dict(aL=(0.25, -0.95, 0.05), aR=(-0.25, -0.95, 0.05))
    if t < 7.2:                                    # innamorato
        k = math.sin(t * 2.6); hop = 0.12 * abs(math.sin((t - 4.3) * 9)) if 4.3 < t < 5.0 else 0
        S_.update(loc=(6.2, -0.9, hop), rot=(0, 0.07 * k, face(0.8, 3.1)), head=(0.05, 0.16 * k, 0), **CLASP)
    elif t < 8.4:                                  # lo vuole
        j = 0.05 * math.sin(t * 45)
        S_.update(loc=(6.25, 1.25, 0), rot=(0.12, 0, face(0.75, 0.95)), aL=(-0.12 + j, -1, 0.12), aR=(0.12 - j, -1, 0.12 + j))
    elif t < 9.45:                                 # lo sogna
        S_.update(loc=(2.0, -3.2, 0.26), rot=(-PI / 2, 0, 0), aL=(-0.25, -1, 0.1 * math.sin(t * 5)), aR=(0.25, -1, -0.1 * math.sin(t * 5)))
    elif t < 16.4:                                 # gli dà un nome e lo abbraccia
        u = ramp(t, 11.6, 11.9); k = math.sin(t * 11) * (1 - u)
        S_.update(loc=(6.05 + 0.42 * u, 2.15, 0), rot=(0, 0.14 * u, PI / 2), aL=lerp((-0.6, -0.4, -0.7), HUG['aL'], u), aR=lerp((0.3, -0.7, 0.45 + 0.35 * k), HUG['aR'], u), head=(0, 0.25 * u, 0.9 * ramp(t, 13.4, 13.8)))
    elif t < 17.75:                                # sbattuto fuori
        u = min(1.0, (t - 16.4) / 0.45)
        S_.update(loc=(6.4, -0.3 - 1.4 * u, 2.6 * (1 - u) + 1.2 * math.sin(PI * u)), rot=(-2 * PI * (1 - sm(u)), 0, PI), aR=(0.3, -0.3, 1.0) if t > 17.0 else DOWN(1))
        if t > 17.0: S_['aR'] = (0.3 + 0.2 * math.sin(t * 20), -0.3, 1.0)
    elif t < 21.5:                                 # prima scala
        d = 1.25 * ramp(t, 18.2, 18.9) * (1 - ramp(t, 20.1, 20.35)); k = math.sin(t * 16) if 18.2 < t < 18.9 else 0
        if t < 18.2 or t > 20.4: S_.update(loc=(7.0, -1.55, 0), rot=(0, 0, PI))
        else: l, r = lad_pose((7.0, -1.1, 0), TH1, d); S_.update(loc=l, rot=r)
        S_.update(aL=(-0.2, -0.55, 0.8 + 0.2 * k), aR=(0.2, -0.55, 0.8 - 0.2 * k), hL=0.4 * k, hR=-0.4 * k)
        if 18.9 <= t < 20.1: S_.update(aL=(-0.5, -0.8, -0.25), aR=(0.5, -0.8, -0.25))
    elif t < 25.85:                                # seconda scala, che poi cade all'indietro
        d = 3.6 * ramp(t, 22.4, 23.3); k = math.sin(t * 18) if 22.4 < t < 23.3 else 0
        if t < 22.4: S_.update(loc=(7.0, -2.45, 0), rot=(0, 0, PI))
        else: l, r = lad_pose((7.0, -1.9, 0), th2(t), d); S_.update(loc=l, rot=r)
        S_.update(aL=(-0.2, -0.55, 0.8 + 0.2 * k), aR=(0.2, -0.55, 0.8 - 0.2 * k), hL=0.4 * k, hR=-0.4 * k, head=(-0.6 * ramp(t, 24.8, 25.1), 0, 0))
        if t > 25.2: S_.update(aL=(-0.9, 0, 0.5 + 0.4 * math.sin(t * 30)), aR=(0.9, 0, 0.5 - 0.4 * math.sin(t * 30)))
    elif t < 30.85:                                # steso sotto la muraglia
        l, r = lad_pose((7.0, -1.9, 0), TH2END, 3.6); u = ramp(t, 27.4, 27.8) * (1 - ramp(t, 28.9, 29.2))
        S_.update(loc=(l[0], l[1], 0.28), rot=r, aL=(-1, 0, 0.2), aR=lerp((1, 0, 0.2), (0.25, -1, 0.1 * math.sin(t * 9)), u))
    elif t < 31.7:                                 # tappeto elastico
        u = ramp(t, 31.42, 31.7); k = ramp(t, 31.0, 31.15) * (1 - ramp(t, 31.3, 31.4))
        S_.update(loc=(2.6 + (TRP[0] - 2.6) * u, -2.9 + (TRP[1] + 2.9) * u, 0.9 * u + 0.9 * math.sin(PI * u)), aL=lerp(DOWN(-1), (0.3, -0.8, 0.3), k), aR=lerp(DOWN(1), (-0.3, -0.8, 0.3), k))
    elif t < 33.2:                                 # tre salti
        z, u, h = jump_z(t); flip = 2 * PI * sm(u) if h > 4 else 0
        S_.update(loc=(TRP[0], TRP[1], z), rot=(flip, 0, 0), aL=(-0.5, 0, 1), aR=(0.5, 0, 1), hL=0.3 * math.sin(u * PI), hR=-0.3 * math.sin(u * PI))
    elif t < 42.3:                                 # piantato nel prato come un paletto
        z = 0.9 - 2.38 * min(1.0, (t - 33.2) / 0.13)
        S_.update(loc=(TRP[0], TRP[1], z), aL=DOWN(-1), aR=DOWN(1), head=(0, 0.08 * math.sin(t * 2.5), 0.5 * ramp(t, 38.2, 38.6)))
    elif t < 43.66:                                # in catapulta
        tp_ = cat_tip(cat_ang(t)); S_.update(loc=(tp_[0], tp_[1], tp_[2] + 0.06), rot=(0, 0, CYAW), aL=(-1, -0.2, 0.3), aR=(1, -0.2, 0.3))
    elif t < 44.45:
        u = (t - 43.66) / 0.79; S_.update(loc=flight(t), rot=(4 * PI * u, 0, CYAW), aL=(-1, 0, 0.6), aR=(1, 0, 0.6))
    elif t < 46.55:                                # piantato nell'aiuola del vicino sbagliato
        k = math.sin(t * 15)
        S_.update(loc=(LAND[0], LAND[1], LAND[2] + 0.04 * k), rot=(PI, 0, 0.4), hL=0.7 * k, hR=-0.7 * k, aL=(-0.5, 0, 1), aR=(0.5, 0, 1))
    elif t < 48.6:                                 # palloncini
        z = bal_z(t); k = math.sin(t * 12)
        S_.update(loc=(BAL[0], BAL[1] + 1.25 * ramp(t, 48.2, 48.6), z), rot=(0, 0.1 * math.sin(t * 3), 0), aR=(0.0, 0, 1), aL=(-0.9, -0.2, 0.2 + 0.4 * k), hL=0.5 * k * (z > 0.1), hR=-0.5 * k * (z > 0.1))
    elif t < 51.5:                                 # appeso per le mutande
        tau = t - 48.6; k = math.sin(t * 13) * math.exp(-tau * 0.9)
        S_.update(loc=(BAL[0], -0.62, hang_z(t)), rot=(-0.45, 0, PI + 0.35 * math.sin(tau * 2.2)), aL=(-0.5, -0.6 + 0.3 * k, -0.6), aR=(0.5, -0.6 - 0.3 * k, -0.6), hL=0.3 + 0.5 * k, hR=0.3 - 0.5 * k, head=(0.2, 0, 2.2 * ramp(t, 49.6, 50.0)))
    elif t < 52.5:                                 # tunnel
        k = math.sin(t * 22); u = ramp(t, 52.15, 52.45)
        S_.update(loc=(HOLE[0], -1.5 + 0.75 * u, -2.3 * u * u), rot=(0.25 + 1.9 * u, 0, PI), aR=(0.15, -0.75, -0.2 + 0.6 * k), aL=(-0.3, -0.7, -0.5))
    elif t < 56.3:                                 # sbuca dalla fossa biologica
        u = eb_(ramp(t, 52.9, 53.3))
        S_.update(loc=(SEP[0], SEP[1], -2.3 + 1.32 * u), rot=(0, 0, 0.81), head=(0.05 * math.sin(t * 3), 0.06 * math.sin(t * 2.1), 0))
    elif t < 61.85:                                # bussa alla porta
        u = ramp(t, 56.3, 57.3); k = math.sin(t * 14) * (1 - u)
        kn = max(0.0, math.sin((t - 57.55) * 2 * PI / 0.3)) if 57.55 < t < 58.45 else 0
        S_.update(loc=(DOORX - 0.3, 5.0 + 1.55 * u, 0.18 * ramp(t, 56.9, 57.2)), rot=(0, 0, PI * (1 - ramp(t, 61.3, 61.6))), hL=0.5 * k, hR=-0.5 * k, aR=lerp(DOWN(1), (0.1, -1, 0.3 + 0.25 * kn), ramp(t, 57.35, 57.55) * (1 - ramp(t, 58.5, 58.8))))
        if t > 60.95: v = ramp(t, 60.95, 61.2); S_.update(aL=lerp(DOWN(-1), (0.22, -0.95, 0.1), v), aR=lerp(DOWN(1), (-0.22, -0.95, 0.1), v), head=(0.25 * v, 0, 0))
    else:                                          # e adesso vuole anche gli altri
        d = ramp(t, 65.0, 65.35); k = math.sin(t * 16) * ramp(t, 65.6, 65.9)
        S_.update(loc=(-5.0 + 0.45 * ramp(t, 65.8, 66.6), 15.6, 0), rot=(0.12 * ramp(t, 65.6, 66.0), 0, PI / 2), aL=lerp((0.22, -0.95, 0.1), (0.12 + 0.12 * k, -0.9, 0.05), d), aR=lerp((-0.22, -0.95, 0.1), (-0.12 - 0.12 * k, -0.9, 0.05), d))
        if t > 67.3:
            v = ramp(t, 67.95, 68.25); l, r = lad_pose((0, 0, 0), TH1, 1.25 * v)       # sale sulla scala contro la nuova staccionata (verso +X)
            S_.update(loc=(-4.45 + l[1], 15.6, l[2]), rot=(-TH1 * v, 0, PI / 2), aL=(-0.5, -0.8, -0.25), aR=(0.5, -0.8, -0.25))
    return S_

def walk(t, sp=14.0, am=0.55):
    s = math.sin(t * sp) * am; return dict(FL=s, FR=-s, BL=-s, BR=s)
def tp(t):
    S_ = dict(loc=(0, 0, 0), rot=(0, 0, 0), legs=dict(FL=0, FR=0, BL=0, BR=0), head=(0, 0, 0), tail=-1.0 + 0.5 * math.sin(t * 12))
    if t < 17.75: S_.update(loc=(4.2, -2.6, 0), rot=(0, 0, 2.2), head=(-0.15, 0.2 * math.sin(t * 1.7), 0.3))
    elif t < 25.85: S_.update(loc=(4.9, -3.6, 0), rot=(0, 0, 2.6), head=(-0.55 * ramp(t, 18.3, 19.0), 0, 0.2))
    elif t < 30.85: S_.update(loc=(5.6, -4.6, 0), rot=(0, 0, 2.2), head=(-0.6 * (1 - ramp(t, 29.0, 29.3)), 0, 0.8 * ramp(t, 29.0, 29.3)))
    elif t < 37.2:
        h = 0.25 * abs(math.sin(t * 9)) if t > 33.5 else 0; S_.update(loc=(2.3, -3.7, h), rot=(0, 0, 1.2), head=(-0.5 * (1 - ramp(t, 33.2, 33.4)), 0, 0))
    elif t < 42.3:                                 # si rotola dal ridere
        k = math.sin(t * 9)
        S_.update(loc=(2.9 + 0.25 * math.sin(t * 2.2), -3.5, 0.48), rot=(0, PI + 0.6 * math.sin(t * 4.4), 0.7), legs=dict(FL=0.8 * k, FR=-0.8 * k, BL=-0.7 * k, BR=0.7 * k), head=(0.2 * k, 0, 0.3))
    elif t < 46.55:
        c, s = math.cos(CYAW), math.sin(CYAW); d = ramp(t, 43.45, 43.58)
        S_.update(loc=(CAT[0] - s * 3.0 + c * 0.9, CAT[1] + c * 3.0 + s * 0.9, 0), rot=(0, 0, CYAW + 1.2), head=(0.5 * d - 0.6 * ramp(t, 43.7, 44.0), 0, 0))
    elif t < 51.5:
        h = 0.3 * abs(math.sin(t * 10)) if t > 48.8 else 0; S_.update(loc=(-1.1, -3.6, h), rot=(0, 0, 2.6), head=(-0.6, 0, 0))
    elif t < 56.3: S_.update(loc=(3.5, -2.4, 0), rot=(0, 0, 2.5), head=(0.25 * ramp(t, 52.2, 52.5), 0.3 * math.sin(t * 3), 0))
    elif t < 63.7: S_.update(loc=(-2.0, -4.0, 0), rot=(0, 0, 0.5))
    else: S_.update(loc=(-5.9, 14.5, 0), rot=(0, 0, PI / 2 + 0.4), head=(0.0, 0.25 * math.sin(t * 2), 0.9 * ramp(t, 65.6, 66.0)))
    return S_
def mp(t):
    """vicino: loc, yaw, spalle (L, R)."""
    if t < 16.4:
        u = sm((t - 13.0) / 2.0); k = math.sin(t * 15)
        return (DOORX + (5.9 - DOORX) * u, 7.0 + (2.9 - 7.0) * u, 0.32 * (1 - ramp(t, 13.2, 13.7))), face(5.9 - DOORX, 2.9 - 7.0) * ramp(t, 12.9, 13.3), (-2.2 - 0.5 * k, -2.2 + 0.5 * k), 0.5 * math.sin(t * 13) * (0 < u < 1)
    if t < 21.5:
        up = ramp(t, 19.75, 19.95) * (1 - ramp(t, 20.08, 20.14)); turn = ramp(t, 20.5, 20.9); k = math.sin(t * 18) * turn
        return (5.2, 0.9, 0), PI * turn, (-0.3 - 1.0 * turn - 0.3 * k, -0.8 - 2.2 * up - 0.5 * turn + 0.3 * k), 0.0
    if t < 31.0: return (0.0, 0.05, 4 * TH + 0.7), 0.0, (-1.3, -1.3), 0.0
    if t < 63.5:
        nose = ramp(t, 60.1, 60.35) * (1 - ramp(t, 60.8, 61.0)); give = ramp(t, 60.9, 61.1)
        return (DOORX + 0.12, FRONT - 0.2, 0.32), 0.0, (-0.2 - 1.0 * give * (1 - ramp(t, 61.4, 61.7)), -0.2 - 2.4 * nose - 1.0 * give * (1 - ramp(t, 61.4, 61.7))), 0.0
    return (0, 0, -40), 0.0, (0, 0), 0.0
def g0(t):
    """Gianfranco: loc, rot."""
    home = (G0P[0], G0P[1], 0.25)
    if t < 60.75: return home, (0, 0, 0)
    if t < 61.0: return (DOORX + 0.12, FRONT - 0.5, 1.25), (0, 0, 0)
    if t < 61.85:
        u = ramp(t, 61.0, 61.25); v = ramp(t, 61.3, 61.6); a = PI * (1 - v)
        return (DOORX + 0.12 - 0.42 * u + 0.33 * math.sin(a) * u - 0.0, 6.55 + (FRONT - 0.5 - 6.55) * (1 - u) - 0.33 * math.cos(a) * u * 1.0 + 0.0, 1.25 - 0.6 * u), (0, 0, 0)
    if t < 65.0: return (-5.0 + 0.32, 15.6, 0.65), (0, 0, PI / 2)
    u = ramp(t, 65.0, 65.35); return (-4.68 + 0.25 * u, 15.6 - 0.75 * u, 0.65 * (1 - u)), (0, 0, PI / 2)

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
    for k, v in q['legs'].items(): Tb['leg' + k].rotation_euler = (v, 0, 0); Tb['leg' + k].keyframe_insert('rotation_euler', frame=f)
    Tb['head'].rotation_euler = q['head']; Tb['head'].keyframe_insert('rotation_euler', frame=f)
    Tb['tail'].rotation_euler = (q['tail'], 0, 0.5 * math.sin(t * 14)); Tb['tail'].keyframe_insert('rotation_euler', frame=f)
    ml, my, msh, mwk = mp(t); mr = man['root']; mr.location = ml; mr.rotation_euler = (0, 0, my); mr.keyframe_insert('location', frame=f); mr.keyframe_insert('rotation_euler', frame=f)
    man['shoulderL'].rotation_euler = (msh[0], 0, 0.2); man['shoulderR'].rotation_euler = (msh[1], 0, -0.2); man['hipL'].rotation_euler = (mwk, 0, 0); man['hipR'].rotation_euler = (-mwk, 0, 0)
    for nm in ('shoulderL', 'shoulderR', 'hipL', 'hipR'): man[nm].keyframe_insert('rotation_euler', frame=f)
    # vecchietta che mena con la borsetta
    G['root'].location = (BED[0] - 1.25, BED[1] + 0.2, 0); G['root'].rotation_euler = (0, 0, PI / 2 + 0.2)
    G['shoulderR'].rotation_euler = (-1.9 + 1.3 * abs(math.sin((t - 44.6) * 9)) if t > 44.6 else -0.75, 0, 0); G['shoulderR'].keyframe_insert('rotation_euler', frame=f)
    # Gianfranco
    gl, gr = g0(t); G0.location = gl; G0.rotation_euler = gr; G0.keyframe_insert('location', frame=f); G0.keyframe_insert('rotation_euler', frame=f)
    # porta e citofono
    op = ramp(t, 12.75, 13.0) * (1 - ramp(t, 16.2, 16.4)) + ramp(t, 59.55, 59.9) * (1 - ramp(t, 63.2, 63.5))
    hinge.rotation_euler = (0, 0, -1.75 * op); hinge.keyframe_insert('rotation_euler', frame=f)
    cito.rotation_euler = (0, 0.45 * math.sin(t * 4.0), 0); cito.keyframe_insert('rotation_euler', frame=f)
    # scala lunga che cade
    lad2.rotation_euler = (th2(t) if t < 25.85 else TH2END, 0, 0); lad2.keyframe_insert('rotation_euler', frame=f)
    # catapulta
    catarm.rotation_euler = (cat_ang(t), 0, 0); catarm.keyframe_insert('rotation_euler', frame=f)
    # palloncini che scappano
    tau = t - 48.65; balroot.location = (0.36, 0, 1.93 + (9 * tau if tau > 0 else 0)); balroot.keyframe_insert('location', frame=f)
    # mutande elastiche
    wv = Vector(s['loc']) + Euler(s['rot'], 'XYZ').to_matrix() @ Vector((0, 0.22, 0.80)); elast.scale = (1, 1, max(0.05, (Vector(NAIL) - wv).length)); elast.keyframe_insert('scale', frame=f)
    # tappo della fossa in testa
    if 52.9 <= t < 56.3: hv = Vector(s['loc']) + Vector((0, 0, 2.18)); lid.location = hv; lid.rotation_euler = (0.25, 0.1 * math.sin(t * 3), 0)
    else: lid.location = (SEP[0], SEP[1], 0.09); lid.rotation_euler = (0, 0, 0)
    lid.keyframe_insert('location', frame=f); lid.keyframe_insert('rotation_euler', frame=f)
    # tappeto: il telaio trema
    tramp.rotation_euler = (0.04 * math.exp(-(t - 33.2) * 4) * math.sin((t - 33.2) * 40) if t > 33.2 else 0, 0, 0); tramp.keyframe_insert('rotation_euler', frame=f)

_lastP = [None, -1.0]; _lastT = [None, -1.0]
def pex(t, **k):
    if _lastP[0] is not None and t - 0.06 > _lastP[1]: pippo.express(P, fr(t - 0.06), **_lastP[0])
    pippo.express(P, fr(t), **k); _lastP[0] = k; _lastP[1] = t
def tex(t, **k):
    if _lastT[0] is not None and t - 0.06 > _lastT[1]: tumbo.tumbo_express(Tb, fr(t - 0.06), **_lastT[0])
    tumbo.tumbo_express(Tb, fr(t), **k); _lastT[0] = k; _lastT[1] = t
pex(0.0, smile=1.0, brow_lift=0.6, eye_scale=1.2, mouth_open=0.3); pex(7.3, smile=0.8, brow_lift=0.7, eye_scale=1.3, mouth_open=0.6); pex(8.45, eye_open=0.05, smile=1.0)
pex(9.5, smile=1.0, eye_scale=1.1); pex(11.7, smile=1.0, eye_open=0.25); pex(13.5, eye_open=1.1, brow_lift=0.5, mouth_open=0.3); pex(16.45, eye_open=0.1, mouth_open=0.7)
pex(17.0, brow=1.0, eye_open=0.75); pex(18.3, smile=0.7, brow=0.7); pex(19.0, smile=1.0, eye_scale=1.2, brow_lift=0.5); pex(20.1, brow=-0.6, brow_lift=0.6, eye_scale=1.2, mouth_open=0.5)
pex(21.6, brow=1.0, eye_open=0.7); pex(23.3, smile=0.9, brow=0.6); pex(24.8, brow_lift=0.7, eye_scale=1.25, mouth_open=0.6, look=(0, 0.8)); pex(25.25, brow=-0.8, brow_lift=0.7, eye_scale=1.3, mouth_open=1.0)
pex(25.9, eye_open=0.08, mouth_open=0.4); pex(30.9, brow=1.0, smile=0.4, eye_open=0.8); pex(31.75, smile=1.0, mouth_open=0.6, brow=0.5); pex(33.2, brow=-0.8, brow_lift=0.7, eye_scale=1.3, mouth_open=1.0)
pex(34.5, brow=1.0, eye_open=0.55, mouth_open=0.0); pex(38.3, brow=1.0, eye_open=0.5, look=(-0.8, -0.2)); pex(42.4, smile=0.9, brow=0.8); pex(43.62, brow=-0.8, brow_lift=0.7, eye_scale=1.3, mouth_open=1.0)
pex(44.5, eye_open=0.08); pex(46.6, smile=0.9, brow=0.6); pex(47.2, smile=1.0, mouth_open=0.5, brow_lift=0.4); pex(47.95, brow=-0.6, brow_lift=0.6, eye_scale=1.2, mouth_open=0.4, look=(0, 0.7))
pex(48.7, brow=-0.8, brow_lift=0.7, eye_scale=1.3, mouth_open=1.0); pex(49.6, brow=1.0, eye_open=0.5, mouth_open=0.0); pex(51.55, brow=1.0, smile=0.5, eye_open=0.8)
pex(52.9, eye_open=0.3, brow=-0.4, mouth_open=0.2); pex(54.1, brow=1.0, eye_open=0.45, mouth_open=0.1, look=(0.3, 0.3)); pex(56.4, brow=0.8, eye_open=0.7); pex(59.6, smile=0.7, brow_lift=0.6, eye_scale=1.15)
pex(61.0, smile=1.0, eye_scale=1.3, brow_lift=0.7, mouth_open=0.5); pex(63.8, smile=1.0, eye_open=0.3); pex(64.3, eye_scale=1.35, brow_lift=0.8, mouth_open=0.7, eye_open=1.2); pex(65.6, smile=1.0, brow=1.0, eye_open=0.75)
pex(68.0, smile=1.0, brow=1.0, eye_scale=1.1)
tex(0.0, tongue=0.4); tex(8.45, eye_open=0.5); tex(12.8, eye_scale=1.2); tex(16.5, eye_scale=1.3, brow=-0.5); tex(18.3, tongue=0.5); tex(20.1, eye_scale=1.2); tex(25.3, eye_scale=1.4, brow=-0.6)
tex(26.0, tongue=0.3, eye_open=0.8); tex(31.0, tongue=0.6); tex(33.2, eye_scale=1.4); tex(33.6, tongue=0.8, eye_open=0.6, brow=0.4); tex(37.2, tongue=1.0, eye_open=0.25, brow=0.5)
tex(42.4, tongue=0.5); tex(43.62, eye_scale=1.4); tex(46.6, tongue=0.6); tex(48.8, tongue=1.0, eye_open=0.3, brow=0.5); tex(51.6, tongue=0.4); tex(52.9, eye_scale=1.3, brow=-0.5); tex(63.8, eye_open=0.6, brow=0.6)

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
def hearts(t0, t1, c0, n=6, sz=0.11, rise=1.6, spread=0.5, facing=0.0):
    for k in range(n):
        ph = k / n; ox = er.uniform(-spread, spread); oy = er.uniform(-spread, spread) * 0.5
        def fn(t, ph=ph, ox=ox, oy=oy):
            a = ((t - t0) * 0.55 + ph) % 1.0; c = c0(t) if callable(c0) else c0
            s = sz * math.sin(PI * a) * 1.3; return ((c[0] + ox * (0.4 + a), c[1] + oy, c[2] + rise * a), (max(0.001, s),) * 3)
        streak('Cuore', (sz, sz, sz), N['heart'], t0, t1, fn, mesh=hm, rot=(0, 0, facing))
def burst(name, mat, t0, dur, c0, n, vmax, sc, grav=4.9):
    for k in range(n):
        v = np.array([er.uniform(-vmax, vmax), er.uniform(-vmax, vmax), er.uniform(0.3, 1.0) * vmax])
        streak(name, sc, mat, t0, t0 + dur, lambda t, v=v: ((c0[0] + v[0] * (t - t0), c0[1] + v[1] * (t - t0), max(0.05, c0[2] + v[2] * (t - t0) - grav * (t - t0) ** 2)),))
def puffs(t0, c0, n=7, r=1.6, s=0.15, dur=0.6):
    for k in range(n):
        an = k / n * 6.283
        streak('Polvere', (0.1, 0.1, 0.1), M['dust'], t0, t0 + dur, lambda t, an=an: ((c0[0] + (0.3 + r * (t - t0)) * math.cos(an), c0[1] + (0.3 + r * (t - t0)) * math.sin(an) * 0.7, c0[2] + 0.6 * (t - t0)),
                                                                                      (max(0.001, s * math.sin(PI * min(1, (t - t0) / dur))),) * 3))
def headpos(t, dz=1.95):
    s = pp(t); v = Euler(s['rot'], 'XYZ').to_matrix() @ Vector((0, 0, dz)); return (s['loc'][0] + v.x, s['loc'][1] + v.y, s['loc'][2] + v.z)
hearts(0.3, 7.2, lambda t: headpos(t, 2.1), n=6, facing=face(0.8, 3.1) + PI)
hearts(5.2, 7.2, (G0P[0], G0P[1], 1.4), n=5, sz=0.09, rise=1.2)
hearts(8.5, 9.45, (2.0, -1.5, 2.9), n=4, sz=0.10, rise=0.8)
hearts(11.7, 16.4, (6.7, 2.2, 1.9), n=6, facing=0.0)
hearts(61.1, 61.85, (DOORX - 0.2, FRONT - 0.9, 1.9), n=7, sz=0.12, rise=1.4, facing=0.0)
hearts(64.3, 67.2, lambda t: headpos(t, 2.1), n=7, sz=0.12, facing=-PI / 2)
for k in range(7):                                  # il nano che brilla
    a = k * 0.9; p = (G0P[0] + 0.55 * math.cos(a), G0P[1] - 0.25 + 0.1 * math.sin(a * 3), 0.55 + 0.75 * ((k * 0.37) % 1.0))
    for (a_, b_) in ((5.2, 7.2), (29.2, 30.85)):
        streak('Luccichio', (0.05, 0.05, 0.05), N['spark'], a_, b_, lambda t, p=p, k=k: (p, (max(0.001, 0.028 * abs(math.sin(t * 5 + k * 1.3)) ** 3),) * 3))
puffs(16.5, (6.5, -0.3, 0.3)); puffs(20.1, (7.0, -0.2, 2.5), s=0.18); puffs(24.8, (7.0, -0.3, 5.0), s=0.2); puffs(25.85, (7.0, -5.0, 0.3), n=8, s=0.28)
puffs(28.3, (0, -0.6, 9.8), n=9, r=3.0, s=0.4, dur=0.9)
puffs(33.3, (TRP[0], TRP[1], 0.2), n=8, s=0.26); burst('Zolla', N['dirt'], 33.25, 1.0, (TRP[0], TRP[1], 0.2), 8, 2.5, (0.10, 0.10, 0.07))
puffs(44.45, (BED[0], BED[1], 0.6), n=8, s=0.28); burst('Fiore', M['flower'][0], 44.45, 1.2, (BED[0], BED[1], 0.6), 8, 3.0, (0.08, 0.08, 0.08)); burst('Fiore', M['flower'][1], 44.45, 1.2, (BED[0], BED[1], 0.6), 8, 3.0, (0.08, 0.08, 0.08))
for k in (2, 5): burst('Scoppio', N['bal'][k], 47.9 if k == 2 else 48.25, 0.5, add(headpos(47.9 if k == 2 else 48.25, 3.6), (0.2 * (k - 3), 0, 0)), 6, 2.5, (0.05, 0.05, 0.02))
for k in range(14):                                 # terra che vola dalla buca
    v = np.array([er.uniform(-1.2, 1.2), er.uniform(-4.5, -1.5), er.uniform(2.0, 4.5)]); t0_ = 51.6 + 0.045 * k
    streak('Terra', (0.09, 0.09, 0.07), N['dirt'], t0_, t0_ + 0.9, lambda t, v=v, t0_=t0_: ((HOLE[0] + v[0] * (t - t0_), HOLE[1] - 0.3 + v[1] * (t - t0_), max(0.05, 0.3 + v[2] * (t - t0_) - 6 * (t - t0_) ** 2)),))
burst('Schizzo', N['goo'], 52.95, 1.0, (SEP[0], SEP[1], 0.3), 12, 2.4, (0.08, 0.08, 0.06))
for k in range(4):                                  # mosche e puzza
    ph = k * 1.57
    streak('Mosca', (0.035, 0.035, 0.035), N['black'], 53.4, TOTAL, lambda t, ph=ph, k=k: (add(headpos(t, 2.05), (0.55 * math.cos(t * (7 + k) + ph), 0.45 * math.sin(t * (7 + k) + ph), 0.25 * math.sin(t * 11 + ph))),))
for k in range(4):
    ph = k / 4
    streak('Puzza', (0.05, 0.05, 0.22), N['stink'], 53.4, 61.8, lambda t, ph=ph, k=k: (add(headpos(t, 2.3), (0.35 * (k - 1.5) + 0.12 * math.sin(t * 6 + k), 0, 0.9 * ((t * 0.6 + ph) % 1.0))), (0.05, 0.05, 0.22 * math.sin(PI * ((t * 0.6 + ph) % 1.0)) + 0.001)))

# ======================= camera =======================
def PW(t): return pp(t)['loc']
def MW(t): return mp(t)[0]
def Z0(t): return (0, 0, 0)
SHOTS = [  # t0, t1, sub cam, p0, p1, sub mira, a0, a1, lente, f
    (0.0, 5.2, Z0, (5.9, 4.3, 1.15), (6.0, 3.7, 1.25), Z0, (6.2, -0.9, 1.55), (6.2, -0.9, 1.62), 48, 2.8),
    (5.2, 7.2, Z0, (7.35, -0.4, 0.75), (7.25, 0.4, 0.8), Z0, (7.0, 2.2, 0.85), (7.0, 2.2, 0.85), 50, 4),
    (7.2, 8.4, Z0, (9.8, 0.3, 1.25), (9.4, 0.5, 1.2), Z0, (6.7, 1.8, 1.0), (6.7, 1.8, 1.0), 35, 5),
    (8.4, 9.45, Z0, (4.2, -7.2, 3.4), (4.0, -6.8, 3.3), Z0, (2.0, -2.0, 1.4), (2.0, -1.9, 1.5), 30, 8),
    (9.45, 12.7, Z0, (7.5, -2.6, 1.0), (7.4, -2.0, 1.0), Z0, (7.35, 2.1, 0.85), (7.3, 2.1, 0.9), 30, 5),
    (12.7, 15.2, Z0, (9.0, -0.4, 1.3), (8.8, -0.2, 1.3), MW, (0.6, 0, 1.3), (0.6, 0, 1.3), 30, 8),
    (15.2, 16.4, Z0, (1.7, 5.5, 1.35), (1.6, 5.7, 1.3), Z0, (DOORX + 0.5, FRONT, 1.2), (DOORX + 0.5, FRONT, 1.15), 50, 4),
    (16.4, 17.75, Z0, (-1.5, -8.5, 2.0), (-1.0, -8.0, 1.9), Z0, (4.5, 0, 1.5), (4.8, 0, 1.4), 26, 8),
    (17.75, 18.75, Z0, (4.4, -5.4, 1.2), (4.6, -5.0, 1.3), Z0, (7.0, -0.5, 1.5), (7.0, -0.5, 1.8), 30, 8),
    (18.75, 21.5, Z0, (5.0, 4.2, 1.4), (5.1, 3.9, 1.5), Z0, (6.1, 0, 2.2), (6.1, 0, 2.5), 30, 8),
    (21.5, 23.55, Z0, (3.2, -7.8, 1.1), (3.4, -7.4, 1.2), Z0, (7.0, -0.6, 2.6), (7.0, -0.6, 3.6), 26, 8),
    (23.55, 25.85, Z0, (3.4, -7.4, 1.2), (3.6, -8.6, 1.4), PW, (0, 0.6, 1.6), (0, 0.6, 1.2), 24, 8),
    (25.85, 29.2, Z0, (-5.0, -15.0, 2.2), (-8.0, -23.0, 6.5), Z0, (2.5, 0, 4.2), (1.5, 0, 5.6), 22, 8),
    (29.2, 30.85, Z0, (6.2, 0.55, 0.75), (6.45, 0.9, 0.8), Z0, (7.0, 2.2, 0.82), (7.0, 2.2, 0.85), 50, 4),
    (30.85, 31.7, Z0, (4.7, -7.4, 1.3), (4.6, -7.0, 1.3), Z0, (3.5, -2.7, 1.2), (3.8, -2.6, 1.3), 30, 8),
    (31.7, 34.45, Z0, (4.3, -9.8, 1.6), (4.2, -9.2, 1.5), PW, (0, 0, 1.2), (0, 0, 1.2), 24, 8),
    (34.45, 37.2, Z0, (3.5, -5.0, 0.42), (3.6, -4.7, 0.38), Z0, (4.0, -2.6, 0.36), (4.0, -2.6, 0.36), 40, 4),
    (37.2, 42.3, Z0, (2.0, -5.9, 0.42), (2.3, -5.5, 0.4), Z0, (3.35, -3.1, 0.42), (3.35, -3.1, 0.42), 35, 4),
    (42.3, 43.6, Z0, (-2.0, -11.8, 1.6), (-2.4, -11.4, 1.6), Z0, (-6.5, -6.2, 1.3), (-6.5, -6.2, 1.5), 28, 8),
    (43.6, 44.45, Z0, (3.0, -24.0, 2.5), (5.0, -24.0, 2.5), PW, (2.0, 0, -1.0), (0, 0, 0), 20, 8),
    (44.45, 46.55, Z0, (15.6, -2.4, 1.4), (16.0, -1.8, 1.4), Z0, (17.0, 3.2, 1.15), (17.0, 3.2, 1.15), 35, 5),
    (46.55, 48.6, Z0, (-2.5, -9.6, 1.5), (-2.5, -9.2, 1.6), PW, (0, 0, 2.6), (0, 0, 2.4), 26, 8),
    (48.6, 51.5, Z0, (-1.6, -6.9, 2.2), (-1.8, -6.2, 2.5), Z0, (-2.1, -0.5, 3.5), (-2.1, -0.5, 3.5), 32, 6),
    (51.5, 52.5, Z0, (4.6, -5.2, 1.0), (4.4, -4.8, 0.95), Z0, (2.2, -1.0, 0.75), (2.1, -0.9, 0.65), 30, 8),
    (52.5, 54.0, Z0, (5.9, 0.7, 1.05), (5.6, 1.0, 1.0), Z0, (3.4, 3.3, 0.55), (3.3, 3.3, 0.65), 35, 5),
    (54.0, 56.3, Z0, (4.75, 1.75, 0.75), (4.55, 1.95, 0.7), Z0, (3.2, 3.2, 0.75), (3.2, 3.2, 0.78), 50, 4),
    (56.3, 59.4, Z0, (2.6, 3.4, 1.9), (2.2, 3.8, 2.0), Z0, (DOORX - 0.1, 6.8, 1.3), (DOORX - 0.1, 7.0, 1.35), 35, 5),
    (59.4, 60.75, Z0, (1.0, 3.5, 2.5), (0.9, 3.8, 2.5), Z0, (DOORX, FRONT - 0.3, 1.5), (DOORX, FRONT - 0.3, 1.5), 40, 5),
    (60.75, 61.85, Z0, (0.8, 4.2, 2.9), (0.7, 4.4, 2.8), Z0, (DOORX - 0.05, FRONT - 0.6, 1.3), (DOORX - 0.05, FRONT - 0.6, 1.35), 40, 5),
    (61.85, 63.7, Z0, (1.7, 8.6, 9.0), (1.7, 6.0, 15.5), Z0, (2.2, 15.6, 0.3), (2.2, 15.9, 0.3), 24, 8),
    (63.7, 67.25, Z0, (1.0, 16.1, 0.5), (0.3, 16.0, 0.55), Z0, (-5.0, 15.6, 1.4), (-4.8, 15.6, 1.45), 35, 5),
    (67.25, 68.6, Z0, (0.3, 16.0, 0.55), (0.6, 16.1, 0.7), Z0, (-3.6, 15.6, 1.9), (-3.6, 15.6, 2.3), 35, 5),
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
os.makedirs('../t007', exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath('../t007/pippo_t007.blend')); print('SAVED')
