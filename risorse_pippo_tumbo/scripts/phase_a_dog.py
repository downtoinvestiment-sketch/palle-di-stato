import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
import bpy
from mathutils import Vector
from common import *
from pippo import build_pippo, express
from tumbo import build_tumbo, tumbo_express
from render_setup import *
OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sc = reset_scene()
setup_render(sc, 1200, 1200, samples=16)
world(sc, top=(0.80, 0.90, 1.0), bottom=(0.92, 0.90, 0.88), strength=0.55)
P = build_pippo(); T = build_tumbo()
floor = material('A_Floor', (0.62, 0.84, 0.96), rough=0.8, spec=0.1)
bpy.ops.mesh.primitive_plane_add(size=30); bpy.context.object.data.materials.append(floor)
express(P, 1, brow=-0.2, brow_lift=0.1, smile=0.7, mouth_open=0.0, look=(0.4, -0.3))
P['root'].location = (-0.7, 0, 0); P['root'].rotation_euler = (0, 0, -0.35)
T['root'].location = (0.45, -0.1, 0); T['root'].rotation_euler = (0, 0, 0.5)
tumbo_express(T, 1, tongue=0.8, brow=-0.3, look=(0.3, 0.2))
tgt = Vector((0, 0, 0.85))
area_light('Key', Vector((-2.8, -3.2, 3.4)), tgt, 120, 3.0, (1, 0.97, 0.92))
area_light('Fill', Vector((3.2, -2.5, 1.5)), tgt, 40, 3.0, (0.88, 0.93, 1))
area_light('Rim', Vector((0.5, 3.0, 2.8)), tgt, 70, 2.0, (1, 1, 1))
cam = camera('Cam', Vector((0.3, -5.0, 1.1)), tgt, lens=50); sc.camera = cam
sc.render.filepath = os.path.join(OUT, 'renders', 'A_tumbo_con_pippo.png')
bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, 'pippo_tumbo_phaseA.blend'))
