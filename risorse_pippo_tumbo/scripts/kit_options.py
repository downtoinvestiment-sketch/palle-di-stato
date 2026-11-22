"""Test 015 - IL PARTO DI ELEONORA. Salva ../t015/pippo_t015.blend
Personaggi: Pippo e Tumbo ESISTENTI (pippo.py, tumbo.py) invariati; Gualtiero = nuovo vicino ricorrente (props009.gualtiero)."""
import sys, math, os
sys.path.insert(0, os.path.dirname(__file__))
import bpy, numpy as np
from mathutils import Vector, Euler, Matrix
from common import *
from render_setup import *
import set004, props004, props007, props009, props010, props012, props013, props015, kitlook, lookdev, pippo, tumbo
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


# ======================= schede di scelta: alberi, prato, muri, tetti, cielo =======================
import json
WHAT = [a for a in sys.argv if a in ('alberi', 'prato', 'muri', 'tetti', 'cielo')] or ['alberi', 'prato', 'muri', 'tetti', 'cielo']
OUT = os.path.abspath('../t016/opt'); os.makedirs(OUT, exist_ok=True)
P = pippo.build_pippo(chc); Tb = tumbo.build_tumbo(chc, scale=0.75)
for r in (P['root'], Tb['root']): r.rotation_mode = 'XYZ'
for nm in 'LR': P['shoulder' + nm].rotation_mode = 'QUATERNION'
def qdir(d, rest=(0, 0, -1)): return Vector(rest).rotation_difference(Vector(d).normalized())
P['root'].location = (1.0, 0.0, 0); P['shoulderL'].rotation_quaternion = qdir((-0.14, 0, -1)); P['shoulderR'].rotation_quaternion = qdir((0.5, -0.2, 0.8))
pippo.express(P, 1, smile=1.0, mouth_open=0.5)
Tb['root'].location = (0.1, -0.3, 0); tumbo.tumbo_express(Tb, 1, tongue=0.8)
camd = bpy.data.cameras.new('Cam'); cam = bpy.data.objects.new('Cam', camd); cac.objects.link(cam); scene.camera = cam
camd.clip_start = 0.05; camd.clip_end = 1500; camd.sensor_width = 36
tgt = empty('CamTarget', (0.5, 6.5, 2.0), None, cac)
ct = cam.constraints.new('TRACK_TO'); ct.target = tgt; ct.track_axis = 'TRACK_NEGATIVE_Z'; ct.up_axis = 'UP_Y'
kitlook.upgrade(scene, M, envc, prc, trees=False)
A = kitlook.A
for o in list(bpy.data.objects):
    if o.name.startswith(('Tronco', 'Chioma')): bpy.data.objects.remove(o)
try: scene.render.use_motion_blur = False
except Exception: pass
def shot(name, cl, tl, lens=26, w=540, h=960, samples=4):
    cam.location = cl; tgt.location = tl; camd.lens = lens
    scene.render.resolution_x = w; scene.render.resolution_y = h; scene.eevee.taa_render_samples = samples
    scene.render.filepath = os.path.join(OUT, name + '.png'); bpy.ops.render.render(write_still=True); print('TILE', name, flush=True)
def kill(objs):
    for o in objs:
        try:
            for c in list(o.children_recursive): bpy.data.objects.remove(c)
            bpy.data.objects.remove(o)
        except ReferenceError: pass
g = bpy.data.materials.get

if 'alberi' in WHAT:
    opts = [('A1', 'tree_small_02', 6.0), ('A2', 'island_tree_01', 6.5), ('A3', 'island_tree_02', 6.5), ('A4', 'island_tree_03', 6.5), ('A5', 'fir_tree_01', 8.5),
            ('A6', 'quiver_tree_01', 5.0), ('A7', 'jacaranda_tree', 8.0), ('A8', 'pine_tree_01', 8.5), ('A9', 'CARTOON', 4.5)]
    for code, aid, hh in opts:
        before = set(bpy.data.objects)
        try:
            if aid == 'CARTOON':
                for (x, y, s) in ((3.4, 2.0, 1.5), (-5.0, 5.0, 1.4), (9.5, 4.0, 1.3)): tree(x, y, s)
            else:
                for (x, y, s) in ((3.4, 2.0, 1.0), (-5.0, 5.0, 0.9), (9.5, 4.0, 0.85)): A.albero_cartonato(aid, posizione=(x, y, 0), altezza=hh * s, ombra=True, collezione=envc)
                kitlook.tune_cutouts(1.9)
            shot(code, (1.6, -9.5, 1.7), (2.2, 1.0, 3.4), 24)
        except Exception as ex: print('ERR', code, aid, repr(ex)[:200], flush=True)
        kill([o for o in bpy.data.objects if o not in before])

if 'prato' in WHAT:
    prato = bpy.data.objects['Prato']; base = prato.material_slots[0].material
    lookdev._tex(g('S_park'), 0.22, 26.0, (0.10, 0.30, 0.05), (0.30, 0.58, 0.11), bump=1.0, rough=0.95, fine=0.9)
    for code, aid in (('B1', 'Grass001'), ('B2', 'Grass002'), ('B3', 'Grass003'), ('B4', 'Grass004'), ('B5', 'Grass005'), ('B6', 'CARTOON')):
        try:
            prato.material_slots[0].material = g('S_park') if aid == 'CARTOON' else A.materiale(aid, dimensione=3.0, rilievo=0.8, tinta=(1.05, 1.35, 0.7), ruvidita=1.5, nome='OPT_' + aid)
            shot(code, (2.6, -4.6, 1.0), (0.6, 0.2, 0.75), 30)
        except Exception as ex: print('ERR', code, aid, repr(ex)[:200], flush=True)
    prato.material_slots[0].material = base

def swap(cur_name, options, cam_a, cam_b, lens, col, gain, sat, dim):
    cur = g(cur_name); orig = cur
    for code, aid, tinted, d_ in options:
        try:
            if aid == 'CARTOON':
                new = g('S_' + cur_name[3:])
                if 'wall' in cur_name: lookdev._var(new, 0.07, 1.5, 0.12)
                else: lookdev._var(new, 0.22, 2.5, 0.9, bands=3.3)
            else: new = A.materiale(aid, dimensione=d_ or dim, rilievo=0.8, tinta=kitlook._k(col, gain, sat) if tinted else None, nome='OPT_' + code)
            cur.user_remap(new); cur = new
            shot(code, cam_a, cam_b, lens)
        except Exception as ex: print('ERR', code, aid, repr(ex)[:200], flush=True)
    cur.user_remap(orig)

if 'muri' in WHAT:
    swap('PT_wall0', [('C1', 'Plaster001', True, 2.4), ('C2', 'PaintedPlaster017', True, 2.4), ('C3', 'painted_plaster_wall', True, 2.4), ('C4', 'PaintedBricks001', True, 1.6),
                      ('C5', 'red_brick', False, 1.4), ('C6', 'WoodSiding008', True, 2.0), ('C7', 'rustic_stone_wall_02', False, 2.0), ('C8', 'CARTOON', False, None)],
         (5.2, -0.6, 1.5), (0.4, 6.6, 2.1), 26, kitlook.WALLC[0], 1.15, 1.9, 2.4)
if 'tetti' in WHAT:
    swap('PT_roof0', [('D1', 'grey_roof_tiles_02', True, 1.6), ('D2', 'clay_roof_tiles_02', False, 1.6), ('D3', 'ceramic_roof_01', False, 1.6), ('D4', 'roof_slates_03', False, 1.6),
                      ('D5', 'RoofingTiles013A', False, 1.6), ('D6', 'roof_09', False, 1.6), ('D7', 'CARTOON', False, None)],
         (7.5, -5.0, 6.8), (0.0, 8.8, 4.2), 32, kitlook.ROOFC[0], 2.2, 1.0, 1.6)

if 'cielo' in WHAT:
    kitlook.add_trees(envc); kitlook.tune_cutouts(1.9)
    def sun_theta(aid):
        v = A.scarica(aid); img = bpy.data.images.load(A.percorso(v['file_1k']), check_existing=True); w_, h_ = img.size
        px = np.array(img.pixels[:], dtype=np.float32).reshape(h_, w_, 4); lum = px[:, :, :3].sum(axis=2); lum[: h_ // 2] = 0   # solo la meta' alta (righe dal basso)
        col = np.argmax(lum.max(axis=0)); return ((col + 0.5) / w_ - 0.5) * 2 * PI
    th0 = sun_theta('kloofendal_48d_partly_cloudy_puresky'); info = {}
    for code, aid in (('E1', 'kloofendal_48d_partly_cloudy_puresky'), ('E2', 'sunflowers_puresky'), ('E3', 'kloofendal_43d_clear_puresky'), ('E4', 'autumn_field_puresky'),
                      ('E5', 'kloppenheim_06_puresky'), ('E6', 'belfast_sunset_puresky')):
        try:
            th = sun_theta(aid); rot = 45.0 + math.degrees(th0 - th); info[code] = (aid, rot)
            A.cielo(aid, forza=1.1, rotazione=rot, ris='2k')
            shot(code, (4.6, -5.5, 1.5), (0.8, 4.0, 3.0), 22)
        except Exception as ex: print('ERR', code, aid, repr(ex)[:200], flush=True)
    json.dump(info, open(os.path.join(OUT, 'cieli.json'), 'w'))
print('FINE')
