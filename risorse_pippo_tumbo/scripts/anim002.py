"""Test 002 - assemblaggio scena: set + Pippo + Tumbo (modelli invariati) + palline + camere. Salva ../pippo_t002.blend"""
import sys, math, os
sys.path.insert(0, os.path.dirname(__file__))
import bpy, numpy as np
from mathutils import Vector, Quaternion
from common import *
from render_setup import *
from params002 import *
import pippo, tumbo, set002, story002 as S

W, H = 1080, 1920
reset_scene()
scene = bpy.context.scene
setup_render(scene, W, H, samples=24, fps=FPS, frames=FRAMES)
world(scene, top=(0.80, 0.90, 1.0), bottom=(0.97, 0.93, 0.95), strength=0.40)
scene.render.film_transparent = False

# --- set ------------------------------------------------------------------------
setc = collection('Set'); chc = collection('Characters'); bac = collection('Balls'); cac = collection('Cameras')
st = set002.build_set(setc)
hinge = st['gate']
# cancello: si apre a T_GATE
hinge.rotation_euler = (0, 0, 0); hinge.keyframe_insert('rotation_euler', frame=int(T_GATE * FPS) - 6)
hinge.rotation_euler = (0, -1.35, 0); hinge.keyframe_insert('rotation_euler', frame=int(T_GATE * FPS) + 6)

# --- personaggi -----------------------------------------------------------------
P = pippo.build_pippo(chc); T = tumbo.build_tumbo(chc, scale=S.TUM_SCALE)
def fr(t): return 1 + int(round(t * FPS))
def qdir(d, rest=(0, 0, -1)):
    return Vector(rest).rotation_difference(Vector(d).normalized())

# movimento di radice: keyframe a ogni frame
for o in (P['root'], T['root']): o.rotation_mode = 'XYZ'
for f in range(1, FRAMES + 1):
    t = (f - 1) / FPS
    p, yaw, tilt, ph = S.pippo_state(t)
    P['root'].location = tuple(p); P['root'].rotation_euler = (tilt, 0, 0.0 if yaw is None else yaw)
    P['root'].keyframe_insert('location', frame=f); P['root'].keyframe_insert('rotation_euler', frame=f)
    p, yaw, pitch, ph = S.tumbo_state(t)
    T['root'].location = tuple(p); T['root'].rotation_euler = (pitch, 0, 0.0 if yaw is None else yaw)
    T['root'].keyframe_insert('location', frame=f); T['root'].keyframe_insert('rotation_euler', frame=f)
for o in (P['root'], T['root']): set_interp(o, 'LINEAR')

# braccia di Pippo (quaternioni)
for nm in 'LR':
    P[f'shoulder{nm}'].rotation_mode = 'QUATERNION'
def arm(nm, t, d):
    o = P[f'shoulder{nm}']; o.rotation_quaternion = qdir(d); o.keyframe_insert('rotation_quaternion', frame=fr(t))
hold = tuple(S.ARM_D)
down = (0, 0, -1); sideL = (-0.35, 0, -1)
arm('R', 0.0, hold); arm('R', 0.80, hold); arm('R', 1.30, (0.15, 0.0, -1)); arm('R', 5.5, (0.15, 0, -1))
arm('R', 6.2, (0.55, -0.1, 1)); arm('R', 7.4, (0.45, -0.1, 1)); arm('R', 8.0, (0.15, 0, -1)); arm('R', 9.6, (0.15, 0, -1))
arm('R', 10.0, (0.2, -0.7, 0.5)); arm('R', 11.0, (0.3, 0, 1)); arm('R', 12.0, (0.3, 0, 1))
arm('L', 0.0, (-0.15, -0.2, -1)); arm('L', 1.0, (-0.15, -0.2, -1)); arm('L', 1.5, (-0.3, 0, -1)); arm('L', 5.5, (-0.3, 0, -1))
arm('L', 6.2, (-0.55, -0.1, 1)); arm('L', 7.4, (-0.45, -0.1, 1)); arm('L', 8.0, (-0.3, 0, -1)); arm('L', 9.6, (-0.3, 0, -1))
arm('L', 10.0, (-0.2, -0.7, 0.5)); arm('L', 11.0, (-0.3, 0, 1)); arm('L', 12.0, (-0.3, 0, 1))
# corsa / salto: gambe
def leg(side, t, rx):
    o = P[f'hip{side}']; o.rotation_euler = (rx, 0, 0); o.keyframe_insert('rotation_euler', frame=fr(t))
for side in 'LR':
    leg(side, 0, 0); leg(side, S.PIP_RUN0, 0)
for k, t in enumerate(np.arange(S.PIP_RUN0, S.PIP_JUMP, 0.1)):
    leg('L', t, 0.7 * math.sin(k * 3.1)); leg('R', t, -0.7 * math.sin(k * 3.1))
leg('L', S.PIP_JUMP + 0.05, -0.5); leg('R', S.PIP_JUMP + 0.05, 0.4)
leg('L', S.PIP_JUMP + 0.9, 0.0); leg('R', S.PIP_JUMP + 0.9, 0.0)
# espressioni Pippo (frame chiave)
def pex(t, **k): pippo.express(P, fr(t), **k)
pex(0.0, brow=0.5, eye_scale=1.05, smile=0.2); pex(0.8, brow=0.6, smile=0.3, look=(-0.2, 0.0))
pex(1.5, brow=-0.3, brow_lift=1, smile=0.8, mouth_open=0.4, look=(0.3, -0.3)); pex(4.0, brow=-0.3, brow_lift=1, smile=1.0, mouth_open=0.5, look=(0.4, -0.6))
pex(6.0, brow=-0.5, brow_lift=1.2, smile=1.0, mouth_open=0.9, eye_scale=1.1, look=(0.3, -0.6)); pex(8.0, smile=1.0, mouth_open=0.5, look=(0, -0.3))
pex(9.5, brow=0.5, smile=1.0, mouth_open=0.3); pex(10.2, brow=-0.5, mouth_open=1.0, smile=0.6, eye_scale=1.1); pex(11.4, smile=1.0, mouth_open=0.4, brow_lift=0.6)
pex(12.0, smile=1.0, mouth_open=0.3, brow_lift=0.6)
# Tumbo: zampe + lingua
def tleg(t, a):
    for tag, ph in (('FL', 0), ('BR', 0), ('FR', 1), ('BL', 1)):
        o = T['leg' + tag]; o.rotation_euler = (a * (1 if ph == 0 else -1), 0, 0); o.keyframe_insert('rotation_euler', frame=fr(t))
tleg(0, 0); tleg(S.TUM_RUN0, 0)
for k, t in enumerate(np.arange(S.TUM_RUN0, S.TUM_JUMP, 0.08)):
    tleg(t, 0.8 * math.sin(k * 2.6))
tleg(S.TUM_JUMP + 0.05, -0.9); tleg(S.TUM_JUMP + 0.5, 0.0); tleg(S.TUM_JUMP + 1.5, 0.0)
tail = T['tail']
for k, t in enumerate(np.arange(0, 12.01, 0.25)):
    tail.rotation_euler = (-1.0, 0, 0.55 * math.sin(k * 2.2)); tail.keyframe_insert('rotation_euler', frame=fr(t))
def tex(t, **k): tumbo.tumbo_express(T, fr(t), **k)
tex(0, tongue=0.0, brow=0.2); tex(2.0, tongue=0.3, look=(0.3, 0.2)); tex(5.0, tongue=0.6, brow=0.3, look=(0.2, 0.2))
tex(8.2, tongue=1.0, brow=0.5, eye_scale=1.1); tex(10.0, tongue=1.0); tex(12.0, tongue=1.0)

# --- palline --------------------------------------------------------------------
d = np.load(os.path.join(os.path.dirname(__file__), '..', 'cache', 'balls.npz'))
pos, colr = d['pos'], d['color']
N = pos.shape[0]
bmats = [material(f'B_{i}', RAINBOW[i], rough=0.12, spec=0.8, coat=1.0, coat_rough=0.03) for i in range(7)]
me = shared_mesh('sphere')
for i in range(N):
    o = bpy.data.objects.new(f'Ball{i:02d}', me)
    o.scale = (BALL_R,) * 3
    bac.objects.link(o)
    if not me.materials: me.materials.append(bmats[0])
    o.material_slots[0].link = 'OBJECT'; o.material_slots[0].material = bmats[int(colr[i]) % 7]
    for f in range(1, FRAMES + 1):
        o.location = tuple(pos[i, f - 1]); o.keyframe_insert('location', frame=f)
    set_interp(o, 'LINEAR')

# --- luci -----------------------------------------------------------------------
area_light('Key', (6, -8, 12), Vector((-1.5, 1.5, 3)), 700, 6, (1.0, 0.97, 0.92), setc)
area_light('Fill', (-9, -4, 6), Vector((-1.5, 1.5, 3)), 220, 8, (0.85, 0.92, 1.0), setc)
area_light('Rim', (-2, 8, 9), Vector((-2, 2, 3)), 250, 5, (1, 1, 1), setc)
area_light('Top', (-3.45, 1.65, 9), Vector((-3.45, 1.65, 0)), 260, 4, (1, 1, 1), setc)

# --- camere ---------------------------------------------------------------------
def focus(name, kfs):
    e = empty(name, kfs[0][1], None, cac)
    for t, p in kfs:
        e.location = p; e.keyframe_insert('location', frame=fr(t))
    return e
def cam(name, kfs, tgt, lens):
    c = camera(name, kfs[0][1], Vector((0, 0, 0)), lens, cac)
    tc = c.constraints.new('TRACK_TO'); tc.target = tgt; tc.track_axis = 'TRACK_NEGATIVE_Z'; tc.up_axis = 'UP_Y'
    for t, p in kfs:
        c.location = p; c.keyframe_insert('location', frame=fr(t))
    return c
fh = empty('Focus_hero', (0, 0, 0), None, cac)
hp_ = pos[N - 1]
for f in range(1, FRAMES + 1):
    fh.location = tuple(hp_[f - 1]); fh.keyframe_insert('location', frame=f)
def sm(x): x = min(1, max(0, x)); return x * x * (3 - 2 * x)
def camkeys(c, fn, t0, t1):
    for f in range(fr(t0), fr(t1) + 1):
        c.location = fn((f - 1) / FPS, hp_[f - 1]); c.keyframe_insert('location', frame=f)
def mkcam(name, tgt, lens):
    c = camera(name, Vector((0, 0, 0)), Vector((0, 0, -1)), lens, cac)
    tc = c.constraints.new('TRACK_TO'); tc.target = tgt; tc.track_axis = 'TRACK_NEGATIVE_Z'; tc.up_axis = 'UP_Y'
    return c
cams = {}
c1 = mkcam('C1_hook', fh, 40); cams['C1'] = c1
camkeys(c1, lambda t, b: np.array(b) + (1 - sm(t / 2.0)) * np.array([0.7, -2.55, 0.75]) + sm(t / 2.0) * np.array([1.3, 1.5, 0.7]), 0.0, 2.0)
c2 = mkcam('C2_track', fh, 40); cams['C2'] = c2
camkeys(c2, lambda t, b: np.array([5.4 * math.cos(0.35 * math.atan2(b[1], b[0]) - 0.9), 5.4 * math.sin(0.35 * math.atan2(b[1], b[0]) - 0.9), b[2] + 1.2]), 2.0, 5.0)
f3 = focus('Focus_pool', [(5.0, (-3.0, 1.8, 2.6)), (6.5, (-3.45, 1.9, 1.2)), (8.0, (-3.45, 1.65, 1.0))])
c3 = mkcam('C3_cascade', f3, 36); cams['C3'] = c3
for t, p in [(5.0, (-5.9, -2.8, 2.4)), (8.0, (-5.3, -1.3, 2.8))]:
    c3.location = p; c3.keyframe_insert('location', frame=fr(t))
f4 = focus('Focus_leap', [(8.0, (-3.2, 2.7, 3.2)), (10.0, (-3.2, 2.5, 3.0))])
c4 = mkcam('C4_leap', f4, 28); cams['C4'] = c4
for t, p in [(8.0, (2.6, 2.7, 3.4)), (10.0, (2.0, 2.2, 3.0))]:
    c4.location = p; c4.keyframe_insert('location', frame=fr(t))
f5 = focus('Focus_end', [(10.0, (-3.45, 1.65, 0.8)), (12.0, (-3.45, 1.7, 0.9))])
c5 = mkcam('C5_top', f5, 42); cams['C5'] = c5
for t, p in [(10.0, (-3.45, -0.6, 6.4)), (12.0, (-3.45, -1.4, 4.6))]:
    c5.location = p; c5.keyframe_insert('location', frame=fr(t))
for c in cams.values(): set_interp(c, 'BEZIER')
cuts = [(0.0, 'C1'), (2.0, 'C2'), (5.0, 'C3'), (8.0, 'C4'), (10.0, 'C5')]
for t, k in cuts:
    m = scene.timeline_markers.new(k, frame=fr(t)); m.camera = cams[k]
scene.camera = cams['C1']
out = os.path.join(os.path.dirname(__file__), '..', 'pippo_t002.blend')
bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(out))
print('saved', out)
