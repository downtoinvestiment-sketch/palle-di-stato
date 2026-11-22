"""Le emozioni di Admin World (versione A): primo piano per ognuna delle EMOZIONI -> ../schede/admin_world_emozioni.jpg"""
import sys, os
QUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, QUI)
import bpy
from mathutils import Vector
from common import *
from render_setup import *
import kitlook, luci, set004, admin_world as av
A = kitlook.A; W, H = 520, 600
reset_scene(); set004._c.clear(); sc = bpy.context.scene; C = collection('C'); setup_render(sc, W, H, samples=12, fps=24, frames=1); A.qualita_eevee(preset='equilibrato', riflessi=False, scena=sc, risoluzione=(W, H))
world(sc, top=(0.55, 0.65, 0.9), bottom=(0.9, 0.85, 0.8), strength=1.0); luci.cielo_basso(sc.world, 0.45)
shape('Suolo', 'cyl:30:0.1', loc=(0, 0, -0.05), mat=material('suolo_g', (0.75, 0.72, 0.68), rough=0.9), coll=C)
G = av.admin_world(C, 'A'); av.gesto(G, None, 'riposo')
cam = bpy.data.objects.new('Cam', bpy.data.cameras.new('Cam')); C.objects.link(cam); sc.camera = cam; cam.data.lens = 85; cam.data.sensor_width = 36
mira = (0, 0, 1.9); cam.location = (0.5, -3.1, 2.0); luci.punta(cam, Vector(mira))
luci.cinema(C, mira, tuple(cam.location), distanza=4.0, lato=1); luci.ombre_pulite(sc, mezza_risoluzione=False)
NOMI = list(av.EMOZIONI); FILE = []
for i, nome in enumerate(NOMI):
    av.emozione(G, None, nome); bpy.context.view_layer.update()
    p = '/tmp/adm_emo_%02d.png' % i; sc.render.filepath = p; bpy.ops.render.render(write_still=True); FILE.append((nome, p))
from PIL import Image, ImageDraw, ImageFont
ft = ImageFont.truetype(os.path.join(QUI, '..', 'assets', 'font', 'Bangers-Regular.ttf'), 40)
col = 4; righe = (len(FILE) + col - 1) // col
foglio = Image.new('RGB', (W * col, H * righe), (20, 20, 24)); d = ImageDraw.Draw(foglio)
for k, (nome, p) in enumerate(FILE):
    x, y = (k % col) * W, (k // col) * H; foglio.paste(Image.open(p).convert('RGB'), (x, y))
    d.text((x + 14, y + 10), nome.upper(), fill=(255, 235, 60), font=ft, stroke_width=4, stroke_fill=(0, 0, 0))
foglio.save(os.path.join(QUI, '..', 'schede', 'admin_world_emozioni.jpg'), quality=88); print('EMOZIONI', len(FILE))
