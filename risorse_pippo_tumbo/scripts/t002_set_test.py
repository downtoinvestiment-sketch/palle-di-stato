import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
import bpy
from mathutils import Vector
from common import *
from render_setup import *
from set002 import *
sc = reset_scene()
setup_render(sc, 540, 960, samples=8)
world(sc, top=(0.80, 0.86, 1.0), bottom=(0.93, 0.92, 0.97), strength=0.45)
S = build_set()
area_light('Key', Vector((-5, -6, 11)), Vector((-1, 1, 2.5)), 320, 6, (1, 0.97, 0.92))
area_light('Fill', Vector((7, -5, 5)), Vector((0, 1, 2.5)), 90, 6, (0.9, 0.93, 1))
cam = camera('Cam', Vector((1.0, -9.5, 4.6)), Vector((-1.2, 1.6, 3.1)), lens=45); sc.camera = cam
sc.render.filepath = '/home/claude/pippo/renders/T002_set.png'
bpy.ops.render.render(write_still=True)
print("OK")
