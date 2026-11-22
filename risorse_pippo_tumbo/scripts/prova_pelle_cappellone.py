"""Prova pelle di Cappellone: primo piano con luce cinema. Uso: python prova_pelle_cappellone.py prima|dopo  -> ../out/prova_pelle/<nome>.png"""
import sys, os
QUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, QUI)
OUT = os.path.join(QUI, '..', 'out', 'prova_pelle'); os.makedirs(OUT, exist_ok=True)
import bpy
from mathutils import Vector
from common import reset_scene, collection
from render_setup import setup_render, world
import set004, luci, kitlook, cappellone as cp
v = sys.argv[-1]; A = kitlook.A
reset_scene(); set004._c.clear(); sc = bpy.context.scene; C = collection('C')
setup_render(sc, 900, 1100, samples=12, fps=24, frames=1); A.qualita_eevee(preset='equilibrato', riflessi=True, scena=sc, risoluzione=(900, 1100))
world(sc, top=(0.12, 0.13, 0.16), bottom=(0.12, 0.13, 0.16), strength=0.35); luci.cielo_basso(sc.world, 0.1)
from props029 import box
from common import material
box('Fondo', (0, 3, 2), (12, 0.1, 6), material('PP_fondo', (0.55, 0.45, 0.38), rough=0.9), C)
box('Pav', (0, 0, -0.05), (12, 12, 0.1), material('PP_pav', (0.35, 0.25, 0.2), rough=0.9), C)
Cc = cp.cappellone(C); cp.emozione(Cc, None, 'manifesto')
M = Cc['mats']
if v == 'dopo':
    M['pelle'].node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.95, 0.57, 0.39, 1)
    M['pelle_s'].node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.86, 0.46, 0.31, 1)
cam = bpy.data.objects.new('Cam', bpy.data.cameras.new('Cam')); C.objects.link(cam); sc.camera = cam
cam.location = (0.9, -4.2, 1.85); luci.punta(cam, Vector((0, 0, 1.6))); cam.data.lens = 50
L = luci.cinema(C, (0, 0, 1.6), tuple(cam.location), distanza=4.0, lato=1)
if v == 'dopo':
    L['chiave'].data.energy *= 0.82; L['chiave'].data.color = (1.0, 0.78, 0.55)
    sc.view_settings.exposure = -0.35
    try: sc.view_settings.white_balance_temperature = 8000; sc.view_settings.use_white_balance = True
    except Exception: pass
else:
    sc.view_settings.exposure = -0.15
luci.ombre_pulite(sc, mezza_risoluzione=False)
sc.render.filepath = os.path.join(OUT, v + '.png'); bpy.ops.render.render(write_still=True); print('RESA', v, flush=True)
