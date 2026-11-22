import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import bpy, numpy as np
from mathutils import Vector
from common import *
from render_setup import *
from params003 import *
import set003, props003
reset_scene(); scene = bpy.context.scene
setup_render(scene, 540, 960, samples=12, fps=FPS, frames=FRAMES)
world(scene, top=(0.55, 0.78, 1.0), bottom=(0.95, 0.93, 0.90), strength=0.9)
coll = collection('Env'); M = set003.make_mats(); rng = np.random.default_rng(3)
set003.build_city(coll, M, rng); F = set003.build_field(coll, M, rng)
for s in (-1, 1): set003.goal('Goal', s, M, coll)
props003.cart(coll, M)[0].location = (3, -2, 0)
props003.bulldozer(coll, M).location = (-3, -2.5, 0)
props003.roller(coll, M)[0].location = (-3, 2.5, 0)
props003.player(coll, 'P1', (0.9, 0.15, 0.15), (0.95, 0.95, 0.95), (0.85, 0.65, 0.5), (0.2, 0.12, 0.08)).__getitem__('root').location = (1, 1, 0)
sun = bpy.data.lights.new('Sun', 'SUN'); sun.energy = 3.0; so = bpy.data.objects.new('Sun', sun); so.rotation_euler = (0.9, 0.2, 0.6); bpy.context.scene.collection.objects.link(so)
for nm, loc, tgt in [('A', (0, -13, 9), (0, 0, 0)), ('B', (-14, -5, 3.5), (0, 0, 0.5))]:
    c = camera('Cam' + nm, Vector(loc), Vector(tgt), 32)
    scene.camera = c
    scene.render.filepath = '/home/claude/pippo/t003/env_%s.png' % nm
    bpy.ops.render.render(write_still=True)
