"""Scheda delle otto espressioni di Rospina (versione ufficiale 'D') -> ../schede/rospina_espressioni.jpg"""
import sys, os
QUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, QUI)
import bpy
from mathutils import Vector
from common import *
from render_setup import *
import rospina, set004, luci, kitlook
W, H = 420, 520; out = []
for i, nome in enumerate(rospina.EMOZIONI):
    reset_scene(); set004._c.clear(); sc = bpy.context.scene; C = collection('C'); setup_render(sc, W, H, samples=12, fps=24, frames=1)
    kitlook.A.qualita_eevee(preset='veloce', riflessi=False, scena=sc, risoluzione=(W, H)); world(sc, top=(0.55, 0.65, 0.9), bottom=(0.9, 0.85, 0.8), strength=1.0); luci.cielo_basso(sc.world, 0.5)
    shape('Suolo', 'cyl:30:0.1', loc=(0, 0, -0.05), mat=material('suolo_c', (0.75, 0.72, 0.68), rough=0.9), coll=C)
    R = rospina.rospina(C, rospina.mats_rospina(), 'D'); R['root'].rotation_euler = (0, 0, 0.18 if i % 2 else -0.18); rospina.emozione(R, None, nome)
    cam = bpy.data.objects.new('Cam', bpy.data.cameras.new('Cam')); C.objects.link(cam); sc.camera = cam; cam.data.lens = 60; cam.location = (0.3, -3.6, 1.85); luci.punta(cam, Vector((0, 0, 1.72)))
    luci.sole(C, (0, -1), lato=1, energia=3.6, angolo_alto=35); luci.ombre_pulite(sc, mezza_risoluzione=False)
    p = '/tmp/rosp_e%d.png' % i; sc.render.filepath = p; bpy.ops.render.render(write_still=True); out.append((nome, p))
from PIL import Image, ImageDraw, ImageFont
fp = ImageFont.truetype(os.path.join(QUI, '..', 'assets', 'font', 'Bangers-Regular.ttf'), 34)
foglio = Image.new('RGB', (W * 4, H * 2)); d = ImageDraw.Draw(foglio)
for i, (n, p) in enumerate(out):
    foglio.paste(Image.open(p).convert('RGB'), ((i % 4) * W, (i // 4) * H)); d.text(((i % 4) * W + 12, (i // 4) * H + H - 48), n.upper(), fill=(255, 235, 60), font=fp, stroke_width=4, stroke_fill=(0, 0, 0))
foglio.save(os.path.join(QUI, '..', 'schede', 'rospina_espressioni.jpg'), quality=90); print('SCHEDA', len(out))
