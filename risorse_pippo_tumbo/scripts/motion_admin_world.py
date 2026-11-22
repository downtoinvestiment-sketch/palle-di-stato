"""Prova di movimento di Admin World (22 novembre 2026): respira, parla, comizio col pugno, annuisce -> ../out/admin_world_motion.mp4
Uso: python motion_admin_world.py [fotogramma_inizio fotogramma_fine]  (rende i PNG in /tmp/adm_motion/, poi ffmpeg)"""
import sys, os
QUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, QUI)
import bpy
from mathutils import Vector
from common import *
from render_setup import *
import kitlook, luci, set004, admin_world as aw
A = kitlook.A; W, H = 540, 960
reset_scene(); set004._c.clear(); sc = bpy.context.scene; C = collection('C')
f = 1; FINE = 144
setup_render(sc, W, H, samples=8, fps=24, frames=FINE); A.qualita_eevee(preset='equilibrato', riflessi=False, scena=sc, risoluzione=(W, H))
world(sc, top=(0.55, 0.65, 0.9), bottom=(0.9, 0.85, 0.8), strength=1.0); luci.cielo_basso(sc.world, 0.45)
shape('Suolo', 'cyl:30:0.1', loc=(0, 0, -0.05), mat=material('suolo_g', (0.55, 0.56, 0.6), rough=0.9), coll=C)
G = aw.admin_world(C, 'A'); aw.gesto(G, 1, 'riposo')
f = aw.motion(G, 1, 'respira', 24); f = aw.motion(G, f, 'parla', 48); aw.gesto(G, f, 'riposo'); f = aw.motion(G, f, 'comizio', 48); aw.gesto(G, f, 'riposo'); f = aw.motion(G, f, 'annuisce', 24)
cam = bpy.data.objects.new('Cam', bpy.data.cameras.new('Cam')); C.objects.link(cam); sc.camera = cam; cam.data.lens = 50; cam.data.sensor_width = 36
mira = Vector((0, 0, 1.55)); cam.location = (0.6, -4.6, 1.75); luci.punta(cam, mira)
luci.cinema(C, mira, tuple(cam.location), distanza=4.0, lato=1); luci.ombre_pulite(sc, mezza_risoluzione=False)
a, b = (int(sys.argv[1]), int(sys.argv[2])) if len(sys.argv) > 2 else (1, FINE)
os.makedirs('/tmp/adm_motion', exist_ok=True)
fatti = [int(n[:4]) for n in os.listdir('/tmp/adm_motion') if n.endswith('.png')]
a = max([a] + [x + 1 for x in fatti if a <= x <= b])                     # riprende da dove si era fermato
sc.frame_start, sc.frame_end = a, b; sc.render.filepath = '/tmp/adm_motion/####'; sc.render.image_settings.file_format = 'PNG'
bpy.ops.render.render(animation=True)
print('MOTION', a, b)
