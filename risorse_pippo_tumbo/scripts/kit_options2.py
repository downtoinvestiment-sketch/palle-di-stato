"""Test 016 - IL SECONDO PARTO DI ELEONORA. Salva ../t016/pippo_t016.blend
Personaggi: Pippo e Tumbo ESISTENTI (pippo.py, tumbo.py) invariati; Gualtiero = nuovo vicino ricorrente (props009.gualtiero)."""
import sys, math, os
sys.path.insert(0, os.path.dirname(__file__))
import bpy, numpy as np
from mathutils import Vector, Euler, Matrix
from common import *
from render_setup import *
import set004, props004, props007, props009, props010, props012, props013, props015, props016b, kitlook, lookdev, pippo, tumbo
from set004 import obj, bx, cyl, ball_, MB

FPS = 24; TOTAL = 0.5; NF = int(TOTAL * FPS)
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


# ======================= schede di scelta con la libreria nuova (modelli cartoon Kenney) =======================
import random
from props007 import text_obj
WHAT = [a for a in sys.argv if a in ('quartiere', 'oggetti', 'stanza')] or ['quartiere', 'oggetti', 'stanza']
OUT = os.path.abspath('../t016/opt2'); os.makedirs(OUT, exist_ok=True)
A13 = props013.mats013(); Z12 = props012.mats012(); W = props015.mats015(); B = props016b.mats016b()
P = pippo.build_pippo(chc); Tb = tumbo.build_tumbo(chc, scale=0.75)
for r in (P['root'], Tb['root']): r.rotation_mode = 'XYZ'
for nm in 'LR': P['shoulder' + nm].rotation_mode = 'QUATERNION'
def qdir(d, rest=(0, 0, -1)): return Vector(rest).rotation_difference(Vector(d).normalized())
def pose(loc, aL=(-0.14, 0, -1), aR=(0.5, -0.2, 0.8), yaw=0.0):
    P['root'].location = loc; P['root'].rotation_euler = (0, 0, yaw); P['shoulderL'].rotation_quaternion = qdir(aL); P['shoulderR'].rotation_quaternion = qdir(aR)
pose((1.0, 0.0, 0)); pippo.express(P, 1, smile=1.0, mouth_open=0.5)
Tb['root'].location = (0.1, -0.3, 0); tumbo.tumbo_express(Tb, 1, tongue=0.8)
camd = bpy.data.cameras.new('Cam'); cam = bpy.data.objects.new('Cam', camd); cac.objects.link(cam); scene.camera = cam
camd.clip_start = 0.05; camd.clip_end = 1500; camd.sensor_width = 36
tgt = empty('CamTarget', (0.5, 6.5, 2.0), None, cac)
ct = cam.constraints.new('TRACK_TO'); ct.target = tgt; ct.track_axis = 'TRACK_NEGATIVE_Z'; ct.up_axis = 'UP_Y'
kitlook.upgrade(scene, M, envc, prc)
A = kitlook.A
try: scene.render.use_motion_blur = False
except Exception: pass
def shot(name, cl, tl, lens=26, w=540, h=960, samples=4):
    cam.location = cl; tgt.location = tl; camd.lens = lens
    scene.render.resolution_x = w; scene.render.resolution_y = h; scene.eevee.taa_render_samples = samples
    scene.render.filepath = os.path.join(OUT, name + '.png'); bpy.ops.render.render(write_still=True); print('TILE', name, flush=True)
def vis(objs, on):
    for o in objs:
        for q in [o] + list(o.children_recursive): q.hide_render = not on
def area(name, loc, size, energy):
    l_ = bpy.data.lights.new(name, 'AREA'); l_.size = size; l_.energy = energy; l_.color = (1, 0.97, 0.92); o_ = bpy.data.objects.new(name, l_); prc.objects.link(o_); o_.location = loc; return o_

if 'quartiere' in WHAT:
    casas = [o for o in bpy.data.objects if o.name.startswith('Casa')]; cut = [o for o in bpy.data.objects if o.name.startswith('PT_sagoma_')]
    rnd = random.Random(5); tipi = ['kenney/city-kit-suburban/building-type-%s' % c for c in 'abcdefghijklmnopqrstu']; rnd.shuffle(tipi)
    KH = [A.modello(tipi[i % len(tipi)], posizione=(o.location.x, o.location.y, 0), scala=rnd.uniform(5.2, 6.0), rotazione=math.degrees(o.rotation_euler.z), collezione=envc) for i, o in enumerate(casas)]
    alberi = ['kenney/nature-kit/tree_oak', 'kenney/nature-kit/tree_fat', 'kenney/nature-kit/tree_default', 'kenney/nature-kit/tree_detailed', 'kenney/nature-kit/tree_cone', 'kenney/nature-kit/tree_blocks',
              'kenney/nature-kit/tree_pineRoundA', 'kenney/city-kit-suburban/tree-large', 'kenney/city-kit-suburban/tree-small', 'kenney/nature-kit/tree_oak_dark', 'kenney/nature-kit/tree_default_dark']
    pos = list(kitlook.TREES) + [(rnd.uniform(-60, 60), rnd.uniform(20.5, 24.0)) for k in range(16)] + [(rnd.uniform(-60, 60), rnd.uniform(-30.0, -26.0)) for k in range(12)]
    KT = [A.modello(alberi[i % len(alberi)], posizione=(x, y, 0), altezza=rnd.uniform(4.5, 7.5), rotazione=rnd.uniform(0, 360), collezione=envc) for i, (x, y) in enumerate(pos)]
    pose((2.5, 0.5, 0)); Tb['root'].location = (1.5, 0.2, 0)
    for code, hk, tk in (('F1', False, False), ('F2', True, False), ('F3', True, True), ('F4', False, True)):
        vis(casas, not hk); vis(KH, hk); vis(cut, not tk); vis(KT, tk)
        shot(code, (7.5, -7.5, 2.3), (-3.0, 9.0, 3.2), 19)
    vis(casas, True); vis(KH, False); vis(cut, True); vis(KT, False)

if 'oggetti' in WHAT:
    pose((-0.9, 0.3, 0)); Tb['root'].location = (-1.9, 0.0, 0)
    FT = props016b.firetruck(prc, B, L=2.6); FT['root'].location = (1.6, 0.4, 0); FT['root'].rotation_euler = (0, 0, -0.6)
    shot('G1', (2.2, -6.2, 1.9), (0.5, 0.2, 0.95), 28); vis([FT['root']], False)
    k = A.modello('kenney/car-kit/firetruck', posizione=(1.6, 0.4, 0), altezza=1.75, rotazione=-35, collezione=prc)
    shot('G2', (2.2, -6.2, 1.9), (0.5, 0.2, 0.95), 28); vis([k], False)
    mel = props016b.watermelon(prc, B, r=0.3); mel.location = (0.5, -0.2, 0.37)
    shot('H1', (0.4, -4.2, 1.3), (-0.2, 0.0, 0.95), 32); vis([mel], False)
    k = A.modello('kenney/food-kit/watermelon', posizione=(0.5, -0.2, 0), altezza=0.75, collezione=prc)
    shot('H2', (0.4, -4.2, 1.3), (-0.2, 0.0, 0.95), 32); vis([k], False)
    pose((0.0, 0.3, 0), aL=(-0.45, -0.9, 0.1), aR=(0.45, -0.9, 0.1)); Tb['root'].location = (1.8, 0.2, 0)
    sand = props015.sandwich(prc, W, None, (0.0, -0.75, 0.85)); sand.scale = (8.0, 8.0, 8.0)
    shot('I1', (1.6, -5.6, 1.6), (0.2, 0.0, 1.15), 28); vis([sand], False)
    k = A.modello('kenney/food-kit/sandwich', posizione=(0.0, -0.75, 0.25), altezza=1.2, rotazione=20, collezione=prc)
    shot('I2', (1.6, -5.6, 1.6), (0.2, 0.0, 1.15), 28); vis([k], False)
    k = A.modello('kenney/food-kit/burger-double', posizione=(0.0, -0.8, 0.0), altezza=1.7, collezione=prc)
    shot('I3', (1.6, -5.6, 1.6), (0.2, 0.0, 1.15), 28); vis([k], False)

if 'stanza' in WHAT:
    def people(x0, ztop):
        Zz = props012.zucchina(chc, Z12); vis([Zz['veil'], Zz['legs']], False); Zz['root'].location = (x0 - 0.55, -0.05, ztop); Zz['root'].rotation_euler = (-0.12, 0, 0.15)
        ball_('ZucPancia', 1.0, (0, -props012.ZR * 0.62, 0.36), Z12['zuc'], chc, parent=Zz['root'], sc=(0.21, 0.19, 0.25))
        D = props004.player(chc, 'Dottore%d' % int(x0), (0.30, 0.70, 0.60), (0.30, 0.70, 0.60), (0.96, 0.74, 0.6), (0.2, 0.13, 0.08), scale=1.0); D['root'].location = (x0 + 1.0, 0.95, 0); D['root'].rotation_euler = (0, 0, 1.2)
        c_ = props015.crib(envc, W, 'CullaK%d' % int(x0)); c_.location = (x0 + 2.4, 0.9, 0)
        area('LuceK%d' % int(x0), (x0 + 1.0, -1.8, 3.1), 5.0, 520); area('LuceK2%d' % int(x0), (x0 + 3.6, -1.0, 3.1), 3.0, 260)
    # K1: stanza attuale
    x0 = 1000.0; pil = props013.hospital_set(envc, A13, x0); props016b.room_shell(envc, A13, W, x0); people(x0, 0.62)
    shot('K1', (x0 + 1.9, -4.6, 1.75), (x0 + 0.3, 0.3, 1.1), 24)
    # K2: stanza arredata con i mobili cartoon
    x0 = 1300.0; props016b.room_shell(envc, A13, W, x0)
    bed, bd = props016b.kplace(A, 'kenney/furniture-kit/bedSingle', envc, x0, 0.0, s=2.3, rot=90); print('BED', bd)
    props016b.kplace(A, 'kenney/furniture-kit/sideTableDrawers', envc, x0 - 1.9, 0.9, s=2.3)
    props016b.kplace(A, 'kenney/furniture-kit/lampRoundFloor', envc, x0 - 2.9, 2.3, s=2.4)
    props016b.kplace(A, 'kenney/furniture-kit/pottedPlant', envc, x0 + 5.6, 2.3, s=2.4)
    props016b.kplace(A, 'kenney/furniture-kit/cabinetTelevision', envc, x0 - 2.0, 2.55, s=2.3)
    props016b.kplace(A, 'kenney/furniture-kit/televisionModern', envc, x0 - 2.0, 2.55, z=0.31 * 2.3, s=2.3)
    props016b.kplace(A, 'kenney/furniture-kit/bear', envc, x0 - 1.9, 0.9, z=0.38 * 2.3, s=1.4)
    props016b.kplace(A, 'kenney/furniture-kit/rugRounded', envc, x0 + 2.6, -2.2, z=0.005, s=2.6)
    props016b.kplace(A, 'kenney/furniture-kit/loungeChair', envc, x0 + 4.6, 2.3, s=2.3)
    people(x0, 0.62)
    shot('K2', (x0 + 1.9, -4.6, 1.75), (x0 + 0.3, 0.3, 1.1), 24)
print('FINE')
