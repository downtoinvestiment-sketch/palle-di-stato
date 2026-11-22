"""Scheda dell'Onorevole Cappellone: turnaround, 8 espressioni, gesti, cappelli -> ../schede/cappellone.jpg"""
import sys, os, math
QUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, QUI)
import bpy
from mathutils import Vector
from common import *
from render_setup import *
import kitlook, luci, cappellone as cp
A = kitlook.A; W, H = 420, 560; N = [0]
def quadro(posa, cam_pos, mira, lente=50):
    reset_scene(); sc = bpy.context.scene; C = collection('C'); setup_render(sc, W, H, samples=10, fps=24, frames=1); A.qualita_eevee(preset='veloce', riflessi=False, scena=sc, risoluzione=(W, H))
    world(sc, top=(0.55, 0.65, 0.9), bottom=(0.9, 0.85, 0.8), strength=1.0); luci.cielo_basso(sc.world, 0.5)
    shape('Suolo', 'cyl:30:0.1', loc=(0, 0, -0.05), mat=material('suolo_c', (0.75, 0.72, 0.68), rough=0.9), coll=C)
    R = cp.cappellone(C); cp.faccia(R, None); cp.gesto(R, None, 'riposo'); posa(R)
    cam = bpy.data.objects.new('Cam', bpy.data.cameras.new('Cam')); C.objects.link(cam); sc.camera = cam; cam.data.lens = lente; cam.data.sensor_width = 36
    cam.location = cam_pos; luci.punta(cam, Vector(mira)); d = Vector((cam_pos[0], cam_pos[1], 0)).normalized()
    luci.sole(C, (d.x, d.y), lato=1, energia=3.6, angolo_alto=35); luci.ombre_pulite(sc, mezza_risoluzione=False)
    N[0] += 1; p = '/tmp/capp_%02d.png' % N[0]; sc.render.filepath = p; bpy.ops.render.render(write_still=True); return p
def gira(a): return (4.7 * math.sin(a), -4.7 * math.cos(a), 1.35)
righe = []
righe.append(('TURNAROUND', [(n, quadro(lambda R: None, gira(a), (0, 0, 1.08))) for n, a in (('fronte', 0), ('tre quarti', 0.75), ('lato', math.pi / 2), ('dietro', math.pi))]))
esp = list(cp.EMOZIONI)
for k in (0, 4):
    righe.append(('ESPRESSIONI', [(n, quadro(lambda R, n=n: cp.emozione(R, None, n), (0.5, -3.3, 1.75), (0, 0, 1.62), 60)) for n in esp[k:k + 4]]))
ges = [g for g in cp.GESTI if g != 'riposo']
for k in (0, 4):
    righe.append(('GESTI', [(n, quadro(lambda R, n=n: (cp.gesto(R, None, n), cp.emozione(R, None, 'comizio' if 'comizio' in n or 'pugno' in n else 'manifesto')), gira(0.3), (0, 0, 1.15))) for n in ges[k:k + 4]]))
righe.append(('CAPPELLI', [(n, quadro(lambda R, n=n: cp.cappello(R, None, n), (0.6, -3.9, 1.9), (0, 0, 1.78), 60)) for n in ('pompiere', 'cuoco', 'muratore', 'alpino')]))
from PIL import Image, ImageDraw, ImageFont
ft = ImageFont.truetype(os.path.join(QUI, '..', 'assets', 'font', 'Bangers-Regular.ttf'), 40); fp = ImageFont.truetype(os.path.join(QUI, '..', 'assets', 'font', 'Bangers-Regular.ttf'), 30)
foglio = Image.new('RGB', (W * 4, H * len(righe)), (20, 20, 24)); d = ImageDraw.Draw(foglio)
for r, (tit, qs) in enumerate(righe):
    for c, (n, p) in enumerate(qs):
        foglio.paste(Image.open(p).convert('RGB'), (c * W, r * H)); d.text((c * W + 12, r * H + H - 44), n.upper(), fill=(255, 255, 255), font=fp, stroke_width=4, stroke_fill=(0, 0, 0))
    d.text((12, r * H + 8), tit, fill=(255, 235, 60), font=ft, stroke_width=5, stroke_fill=(0, 0, 0))
foglio.save(os.path.join(QUI, '..', 'schede', 'cappellone.jpg'), quality=90); print('SCHEDA', N[0])
