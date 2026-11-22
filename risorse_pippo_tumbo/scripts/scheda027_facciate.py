"""Scheda di scelta delle facciate vere dei palazzi (foto CC0 da ambientCG) per il video 027.
Uso: python scheda027_facciate.py  ->  ../schede/scelta027_facciate.jpg  (ogni gruppo ha il suo numero)."""
import sys, os, math, random
QUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, QUI)
import bpy, bmesh
from mathutils import Vector
from common import *
from render_setup import *
import kitlook, luci, citta027 as ct
A = kitlook.A
W, H = 1600, 1000
def riga(nomi, primo, uscita):
    reset_scene(); scene = bpy.context.scene; C = collection('C')
    setup_render(scene, W, H, samples=8, fps=24, frames=1); A.qualita_eevee(preset='veloce', riflessi=False, scena=scene, risoluzione=(W, H))
    world(scene, top=(0.30, 0.25, 0.55), bottom=(1.0, 0.55, 0.25), strength=1.0); luci.cielo_basso(scene.world, 0.42)
    ct._foschia = lambda m, *a, **k: m                                # nella scheda niente foschia: i colori si devono vedere come sono
    MC = ct.mats_citta('C2', A=A, vere=nomi)
    ct._scatole('Suolo', [(0, 0, -0.05, 60, 60, 0.1)], MC['asfalto'], C, ombra=False)
    rnd = random.Random(5); punti = []
    for i, nome in enumerate(nomi):
        mi = MC['nomi'].index(nome); x = -2.25 + i * 1.5
        for (dx, dy, sx, sy, h) in ((0.0, 0.0, 0.50, 0.50, 2.3), (-0.52, -0.30, 0.42, 0.40, 0.95), (0.50, -0.45, 0.40, 0.44, 0.50)):
            p = ct.palazzo_singolo(C, MC, x + dx, dy, sx, sy, h, mi=mi, seme=3 + i, nome='T', livelli=(h > 2))
            p['o'].rotation_euler = (0, 0, 0.45)
        punti.append((primo + i, Vector((x, 0, 2.42))))
    ct.chiave_impulso(1, impulso=1.0, lampo=0.0)
    cam = bpy.data.objects.new('Cam', bpy.data.cameras.new('Cam')); C.objects.link(cam); scene.camera = cam; cam.data.lens = 62; cam.data.sensor_width = 36
    cam.location = (0.4, -10.5, 1.6); luci.punta(cam, Vector((0, 0, 1.25)))
    luci.sole(C, (0, -1), lato=1, energia=4.2, angolo_alto=23); luci.ombre_pulite(scene, mezza_risoluzione=True)
    scene.render.filepath = uscita; bpy.ops.render.render(write_still=True)
    from bpy_extras.object_utils import world_to_camera_view
    bpy.context.view_layer.update()
    return [(n, world_to_camera_view(scene, cam, p)) for n, p in punti]
NOMI = [d['nome'] for d in ct.FACCIATE_VERE]
from PIL import Image, ImageDraw, ImageFont
font = ImageFont.truetype(os.path.join(QUI, '..', 'assets', 'font', 'Bangers-Regular.ttf'), 84)
foglio = Image.new('RGB', (W, H * 2), (20, 20, 24))
for r in range(2):
    et = riga(NOMI[r * 4:r * 4 + 4], 1 + r * 4, '/tmp/facciate_%d.png' % r)
    im = Image.open('/tmp/facciate_%d.png' % r).convert('RGB'); d = ImageDraw.Draw(im)
    for n, p in et:
        d.text((p.x * W - 22, (1 - p.y) * H - 96), str(n), fill=(255, 235, 60), font=font, stroke_width=6, stroke_fill=(0, 0, 0))
    foglio.paste(im, (0, r * H))
os.makedirs(os.path.join(QUI, '..', 'schede'), exist_ok=True)
foglio.save(os.path.join(QUI, '..', 'schede', 'scelta027_facciate.jpg'), quality=90); print('SCHEDA FATTA')
