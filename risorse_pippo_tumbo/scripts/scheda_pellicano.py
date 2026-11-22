"""Scheda del pellicano (copione n. 27A): tre versioni da scegliere -> ../schede/scelta_pellicano.jpg"""
import sys, os, math
QUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, QUI)
import bpy
from mathutils import Vector
from common import *
from render_setup import *
import animali, set004, luci, kitlook, pippo2 as pippo
W, H = 1800, 1000
reset_scene(); set004._c.clear(); sc = bpy.context.scene; C = collection('C'); setup_render(sc, W, H, samples=12, fps=24, frames=1)
kitlook.A.qualita_eevee(preset='veloce', riflessi=False, scena=sc, risoluzione=(W, H)); world(sc, top=(0.45, 0.65, 0.95), bottom=(0.9, 0.88, 0.8), strength=1.0); luci.cielo_basso(sc.world, 0.5)
shape('Suolo', 'cyl:40:0.1', loc=(0, 0, -0.05), mat=material('suolo_p', (0.55, 0.75, 0.45), rough=0.95), coll=C)
P = pippo.build_pippo(C); P['root'].location = (-3.7, 0.2, 0); P['root'].rotation_euler = (0, 0, 0.25); pippo.express(P, 1, smile=1.2, brow_lift=0.6)
pom = material('pomodoro', (0.9, 0.08, 0.05), rough=0.35); verde = material('picciolo', (0.1, 0.5, 0.12), rough=0.6)
for i, (t, aperto) in enumerate((('A', 0.0), ('B', 0.6), ('C', 0.0))):
    R = animali.pellicano(C, tipo=t); R['root'].location = (-1.9 + i * 2.0, 0, 0); R['root'].rotation_euler = (0, 0, 1.15 - 0.2 * i)
    R['jaw'].rotation_euler = (aperto, 0, 0)
    if t == 'B':
        R['wingL'].rotation_euler = (0, 1.5, 0); R['wingR'].rotation_euler = (0, -1.5, 0)
        o = shape('Pomodoro', 'sphere', (0, -0.55, 0.075), (0.10, 0.10, 0.09), (0, 0, 0), R['jaw'], pom, C); shape('Picciolo', 'sphere', (0, -0.55, 0.16), (0.035, 0.035, 0.012), (0, 0, 0), R['jaw'], verde, C)
cam = bpy.data.objects.new('Cam', bpy.data.cameras.new('Cam')); C.objects.link(cam); sc.camera = cam; cam.data.lens = 45; cam.location = (0.2, -10.2, 1.5); luci.punta(cam, Vector((-0.2, 0, 1.0)))
luci.sole(C, (0, -1), lato=1, energia=3.8, angolo_alto=35); luci.ombre_pulite(sc, mezza_risoluzione=False)
sc.render.filepath = '/tmp/pellicano.png'; bpy.ops.render.render(write_still=True)
from PIL import Image, ImageDraw, ImageFont
from bpy_extras.object_utils import world_to_camera_view
im = Image.open('/tmp/pellicano.png').convert('RGB'); d = ImageDraw.Draw(im); f = ImageFont.truetype(os.path.join(QUI, '..', 'assets', 'font', 'Bangers-Regular.ttf'), 64)
for i, n in enumerate(('A  classico', 'B  ladro', 'C  rosa')):
    p = world_to_camera_view(sc, cam, Vector((-1.9 + i * 2.0, 0, 2.2))); d.text((p.x * W - 110, (1 - p.y) * H - 40), n, fill=(255, 235, 60), font=f, stroke_width=5, stroke_fill=(0, 0, 0))
im.save(os.path.join(QUI, '..', 'schede', 'scelta_pellicano.jpg'), quality=90); print('SCHEDA')
