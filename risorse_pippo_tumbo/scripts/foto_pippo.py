"""Foto di Pippo (e Tumbo) per i quadri del salotto: ../t016/foto_pippo_N.png"""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from mathutils import Vector
from common import *
from render_setup import *
import pippo, tumbo
PI = math.pi
reset_scene(); scene = bpy.context.scene; setup_render(scene, 512, 512, samples=16, fps=24, frames=3)
chc = collection('C')
w = bpy.data.worlds.new('W'); scene.world = w; w.use_nodes = True; bg = w.node_tree.nodes['Background']; bg.inputs['Strength'].default_value = 1.0
sl = bpy.data.lights.new('Sun', 'SUN'); so = bpy.data.objects.new('Sun', sl); chc.objects.link(so); so.rotation_euler = (math.radians(55), 0, math.radians(25)); sl.energy = 3.0
P = pippo.build_pippo(chc); Tb = tumbo.build_tumbo(chc, scale=0.75)
for nm in 'LR': P['shoulder' + nm].rotation_mode = 'QUATERNION'
def qdir(d, rest=(0, 0, -1)): return Vector(rest).rotation_difference(Vector(d).normalized())
cam = bpy.data.objects.new('Cam', bpy.data.cameras.new('Cam')); chc.objects.link(cam); scene.camera = cam
tgt = bpy.data.objects.new('T', None); chc.objects.link(tgt); c = cam.constraints.new('TRACK_TO'); c.target = tgt
os.makedirs('../t016', exist_ok=True)
shots = [((0.35, 0.65, 1.0), (0.0, -2.0, 1.75), (0, 0, 1.72), 50, dict(smile=1.0, mouth_open=0.6), ((-0.14, 0, -1), (0.14, 0, -1)), (5, 5, 0)),
         ((1.0, 0.8, 0.25), (0.3, -4.2, 1.2), (-0.25, 0, 1.0), 40, dict(smile=1.0, mouth_open=0.3), ((-0.14, 0, -1), (0.6, -0.2, 0.75)), (-0.9, -0.3, 0)),
         ((1.0, 0.55, 0.65), (0.0, -3.6, 1.5), (0, 0, 1.35), 40, dict(smile=1.0, mouth_open=0.9, brow=0.3), ((-0.55, -0.2, 0.8), (0.55, -0.2, 0.8)), (5, 5, 0))]
for i, (col, cl, tl, lens, ex, arms, tpos) in enumerate(shots):
    bg.inputs['Color'].default_value = (*col, 1); cam.location = cl; tgt.location = tl; cam.data.lens = lens
    pippo.express(P, 1, **ex); P['shoulderL'].rotation_quaternion = qdir(arms[0]); P['shoulderR'].rotation_quaternion = qdir(arms[1])
    Tb['root'].location = tpos; tumbo.tumbo_express(Tb, 1, tongue=0.8)
    scene.frame_set(1); scene.render.filepath = os.path.abspath('../t016/foto_pippo_%d.png' % i); bpy.ops.render.render(write_still=True); print('FOTO', i)
