import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
import bpy
from mathutils import Vector
from common import *
from pippo import build_pippo, express
from render_setup import *

OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sc = reset_scene()
setup_render(sc, 900, 1200, samples=16)
world(sc, top=(0.80, 0.90, 1.0), bottom=(0.92, 0.90, 0.88), strength=0.55)
R = build_pippo()
floor = material('A_Floor', (0.62, 0.84, 0.96), rough=0.8, spec=0.1)
bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 0, 0)); fl = bpy.context.object
fl.data.materials.append(floor)
express(R, 1, brow=-0.35, brow_lift=0.1, eye_scale=1.0, smile=0.3, mouth_open=0.0, look=(-0.6, -0.3))
R['head'].rotation_euler = (0, 0.06, -0.12)
for s in ('L', 'R'):
    R[f'shoulder{s}'].rotation_euler = (0, 0.10 if s == 'R' else -0.10, 0)
tgt = Vector((0, 0, 1.12))
area_light('Key', Vector((-2.8, -3.2, 3.4)), tgt, 120, 3.0, (1, 0.97, 0.92))
area_light('Fill', Vector((3.2, -2.5, 1.5)), tgt, 40, 3.0, (0.88, 0.93, 1))
area_light('Rim', Vector((0.5, 3.0, 2.8)), tgt, 70, 2.0, (1, 1, 1))
for name, loc in (('front', Vector((0.0, -5.0, 1.15))), ('three', Vector((2.8, -4.1, 1.25)))):
    cam = camera('Cam_' + name, loc, tgt, lens=55)
    sc.camera = cam
    sc.render.filepath = os.path.join(OUT, 'renders', f'A_pippo_{name}.png')
    bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, 'pippo_phaseA.blend'))
print('DONE A')
