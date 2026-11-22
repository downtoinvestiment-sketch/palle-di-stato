"""Test 005 - prova look: le 4 fasi del paracadute + aereo. Salva ../t005/look005.blend"""
import sys, math, os
sys.path.insert(0, os.path.dirname(__file__))
import bpy, numpy as np
from mathutils import Vector
from common import *
from render_setup import *
from params004 import *
import set004, props004, props005, pippo, tumbo
reset_scene(); scene = bpy.context.scene
setup_render(scene, 540, 960, samples=8, fps=24, frames=5); scene.eevee.shadow_resolution_scale = 0.25
rng = np.random.default_rng(11)
M = set004.make_mats(); Q = props005.mats005()
envc = collection('Env'); chc = collection('Characters'); prc = collection('Props')
set004.build_city(envc, M, rng); set004.bx('Lawn', (-BX - .3, -BY - .3, -0.06), (BX + .3, BY + .3, 0.0), M['park'], envc)
world(scene, top=(0.05, 0.36, 1.0), bottom=(0.50, 0.82, 1.0), strength=0.8)
sun = bpy.data.lights.new('Sun', 'SUN'); so = bpy.data.objects.new('Sun', sun); prc.objects.link(so); so.rotation_euler = (math.radians(52), math.radians(8), math.radians(35)); sun.energy = 4.2; sun.angle = math.radians(1.2)
M['cloudw'] = material('S_cloudw', (1, 1, 1), rough=1.0, emit=(1, 1, 1), emit_strength=0.55)
for k in range(18):
    an = k / 18 * 2 * math.pi + rng.uniform(-0.15, 0.15); rr = rng.uniform(48, 85); s_ = rng.uniform(2.2, 4.5)
    cw = empty('CloudW', (rr * math.cos(an), rr * math.sin(an), rng.uniform(15, 34)), None, prc)
    for (dx, dy, dz, r_) in [(0, 0, 0, 1.5), (1.5, 0.3, -0.2, 1.15), (-1.5, -0.2, -0.25, 1.2), (0.6, -0.5, 0.6, 1.1), (-0.6, 0.5, 0.5, 1.0), (2.6, 0, -0.45, 0.75)]:
        c_, s2 = math.cos(an + math.pi / 2), math.sin(an + math.pi / 2)
        set004.ball_('Puff', r_ * s_, (dx * s_ * c_, dx * s_ * s2 + dy, dz * s_), M['cloudw'], prc, parent=cw, sc=(1, 1, 0.6))
def qdir(d, rest=(0, 0, -1)): return Vector(rest).rotation_difference(Vector(d).normalized())
SH = 1.42
def mk(i, arms):
    P = pippo.build_pippo(chc)
    for nm, s in (('L', -1), ('R', 1)):
        P['shoulder' + nm].rotation_mode = 'QUATERNION'; P['shoulder' + nm].rotation_quaternion = qdir((s * arms[0], arms[1], arms[2]))
    P['hipL'].rotation_euler = (0.25, 0, 0); P['hipR'].rotation_euler = (-0.2, 0, 0)
    r = P['root']
    for f in range(1, 6):
        r.location = (0, 0, 6.0) if f == i else (0, 0, -500); r.keyframe_insert('location', frame=f)
    return P
P1 = mk(1, (0.18, 0, 1)); props005.tablecloth(prc, Q, P1['root'], (0, 0, 1.92)); pippo.express(P1, 1, brow_lift=0.6, eye_open=1.2, mouth_open=0.6)
P2 = mk(2, (-0.10, 0, 1)); props005.harness(prc, Q, P2['body'], pack=False)
c2 = props005.round_canopy(prc, Q, 'Lenzuolo', [Q['sheet'], Q['sheet2'], Q['rope'], Q['rope']], lambda g, i: g % 2, R=1.9, D=1.3, nseg=10, vent=0.38, L=2.6, parent=P2['root'], loc=(0, 0, SH))
props005.vent_patch(prc, Q['sheet2'], 0.38, c2, 2.6 + 1.3 * math.cos(math.asin(0.38 / 1.9)))
P3 = mk(3, (-0.10, 0, 1)); props005.harness(prc, Q, P3['body'])
props005.round_canopy(prc, Q, 'Cupola', [Q['nyl'][0], Q['nyl'][1], Q['line'], Q['web']], lambda g, i: g % 2, R=2.5, D=1.7, nseg=14, vent=0.42, L=3.2, parent=P3['root'], loc=(0, 0, SH))
P4 = mk(4, (0.14, 0.26, 1)); props005.harness(prc, Q, P4['body'], reserve=True)
props005.ram_air(prc, Q, parent=P4['root'], loc=(0, 0, SH))
props005.goggles(prc, Q, P4['head'], 0.125, -0.27, 0.50, r=0.10, tilt=-0.45, strap_r=(0.37, 0.33))
Tb = tumbo.build_tumbo(chc, scale=0.75); Tb['root'].parent = P4['root']; Tb['root'].location = (0, -0.78, 0.92); Tb['root'].rotation_euler = (-math.pi / 2, 0, 0)
Tb['head'].rotation_euler = (1.15, 0, 0); tumbo.tumbo_express(Tb, 1, tongue=0.8, eye_scale=1.1)
props005.goggles(prc, Q, Tb['head'], 0.105, -0.285, 0.075, r=0.105, strap_r=(0.30, 0.285))
for k in 'FL FR BL BR'.split(): Tb['leg' + k].rotation_euler = (0.5 if k[0] == 'F' else -0.4, 0, 0)
pl, prop = props005.plane(prc, Q); pl.rotation_euler = (0, math.radians(-8), math.radians(-35))
for f in range(1, 6):
    pl.location = (0, 0, 9.0) if f == 5 else (-14, 30, 20); pl.keyframe_insert('location', frame=f)
cam = bpy.data.cameras.new('Cam'); co = bpy.data.objects.new('Cam', cam); prc.objects.link(co); scene.camera = co; cam.lens = 30; cam.clip_end = 400
tg = empty('CamT', (0, 0, 8.6), None, prc); c = co.constraints.new('TRACK_TO'); c.target = tg; c.track_axis = 'TRACK_NEGATIVE_Z'; c.up_axis = 'UP_Y'
for f, (cp, tp) in enumerate([((2.5, -7.5, 6.6), (0, 0, 8.3)), ((3, -10, 6.5), (0, 0, 9.0)), ((3.5, -12, 6.3), (0, 0, 9.4)), ((3.2, -11.5, 6.8), (0, 0, 9.3)), ((12, -15, 6.5), (0, 0, 9.0))], 1):
    co.location = cp; co.keyframe_insert('location', frame=f); tg.location = tp; tg.keyframe_insert('location', frame=f)
os.makedirs('../t005', exist_ok=True); bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath('../t005/look005.blend')); print('SAVED')
