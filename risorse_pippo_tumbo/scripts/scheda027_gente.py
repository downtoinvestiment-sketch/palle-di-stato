"""Scheda delle persone nuove del video 027 (fatte a mano): la folla (12 persone) e il corpo di ballo (3), davanti e di spalle.
Uso: python scheda027_gente.py  ->  ../schede/scelta027_gente.jpg"""
import sys, os, math
QUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, QUI)
import bpy
from mathutils import Vector
from common import *
from render_setup import *
import kitlook, luci, gente027 as gn
A = kitlook.A
W, H = 1600, 640
def striscia(quali, uscita, dietro=False):
    reset_scene(); scene = bpy.context.scene; C = collection('C')
    setup_render(scene, W, H, samples=12, fps=24, frames=1); A.qualita_eevee(preset='veloce', riflessi=False, scena=scene, risoluzione=(W, H))
    world(scene, top=(0.30, 0.25, 0.55), bottom=(1.0, 0.55, 0.25), strength=1.0); luci.cielo_basso(scene.world, 0.42)
    shape('Suolo', 'cyl:40:0.1', loc=(0, 0, -0.05), mat=material('suolo', (0.20, 0.19, 0.24), rough=0.9), coll=C)
    n = len(quali); passo = 0.95
    for i, (look, nome) in enumerate(quali):
        col, R = gn.pupazzo('P%d' % i, look)
        for o in col.objects:
            C.objects.link(o)
            if o.type == 'MESH': o.visible_shadow = True
        R['root'].location = ((i - (n - 1) / 2) * passo, 0, 0); R['root'].rotation_euler = (0, 0, (math.pi if dietro else 0) + (0.25 if i % 2 else -0.25))
        su = (i % 3 == 0) or ('telefono' in look.get('extra', ())) or ('luce' in look.get('extra', ()))
        R['shoulderL'].rotation_euler = (-0.25, 2.55, 0) if su else (0.15, 0.32, 0); R['shoulderR'].rotation_euler = (-0.25, -2.45, 0) if i % 4 == 1 else (-0.25, -0.30, 0)
        R['hipL'].rotation_euler = (0.10, 0.06, 0); R['hipR'].rotation_euler = (-0.10, -0.06, 0); R['footL'].rotation_euler = (-0.10, -0.06, 0); R['footR'].rotation_euler = (0.10, 0.06, 0)
        R['bocca'].scale = (1.0, 1.0, 0.25 + 0.75 * ((i * 37) % 10) / 10.0); R['head'].rotation_euler = (0.0, 0.06 if i % 2 else -0.06, 0)
    cam = bpy.data.objects.new('Cam', bpy.data.cameras.new('Cam')); C.objects.link(cam); scene.camera = cam; cam.data.lens = 70; cam.data.sensor_width = 36
    cam.location = (0.0, -15.5 * n / 6.0, 1.45); luci.punta(cam, Vector((0, 0, 1.08)))
    luci.sole(C, (0, -1), lato=1, energia=4.2, angolo_alto=23); luci.ombre_pulite(scene, mezza_risoluzione=False)
    scene.render.filepath = uscita; bpy.ops.render.render(write_still=True)
F = [(l, 'F%d' % (i + 1)) for i, l in enumerate(gn.LOOK_FOLLA)]; Bl = [(l, 'B%d' % (i + 1)) for i, l in enumerate(gn.LOOK_BALLO)]
striscia(F[:6], '/tmp/gente_0.png'); striscia(F[6:], '/tmp/gente_1.png'); striscia(Bl + [F[3], F[9], F[2]], '/tmp/gente_2.png'); striscia(F[:3] + Bl, '/tmp/gente_3.png', dietro=True)
from PIL import Image, ImageDraw, ImageFont
font = ImageFont.truetype(os.path.join(QUI, '..', 'assets', 'font', 'Bangers-Regular.ttf'), 54)
foglio = Image.new('RGB', (W, H * 4), (20, 20, 24)); d = ImageDraw.Draw(foglio)
for r, tit in enumerate(('LA FOLLA', 'LA FOLLA', 'CORPO DI BALLO (bianco e oro) + folla', 'DI SPALLE')):
    foglio.paste(Image.open('/tmp/gente_%d.png' % r).convert('RGB'), (0, r * H))
    d.text((24, r * H + 14), tit, fill=(255, 235, 60), font=font, stroke_width=5, stroke_fill=(0, 0, 0))
foglio.save(os.path.join(QUI, '..', 'schede', 'scelta027_gente.jpg'), quality=90); print('SCHEDA FATTA')
