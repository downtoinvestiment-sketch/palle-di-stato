"""Scheda della Signora Platino (22 novembre 2026): tre versioni, corpo intero accanto a Pippo, primo piano, tre quarti -> ../schede/platino_versioni.jpg"""
import sys, os, math
QUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, QUI)
import bpy
from mathutils import Vector
from common import *
from render_setup import *
import kitlook, luci, set004, pippo2, platino as gn
A = kitlook.A; W, H = 520, 760; N = [0]
def quadro(stile, cam_pos, mira, lente, pippo=False, posa=None):
    reset_scene(); set004._c.clear(); sc = bpy.context.scene; C = collection('C'); setup_render(sc, W, H, samples=12, fps=24, frames=1); A.qualita_eevee(preset='equilibrato', riflessi=False, scena=sc, risoluzione=(W, H))
    world(sc, top=(0.55, 0.65, 0.9), bottom=(0.9, 0.85, 0.8), strength=1.0); luci.cielo_basso(sc.world, 0.45)
    shape('Suolo', 'cyl:30:0.1', loc=(0, 0, -0.05), mat=material('suolo_g', (0.75, 0.72, 0.68), rough=0.9), coll=C)
    G = gn.platino(C, stile); gn.gesto(G, None, 'riposo')
    if posa: posa(G)
    if pippo:
        P = pippo2.build_pippo(C); P['root'].location = (1.1, 0.3, 0); bpy.context.view_layer.update()
        alto = max((o.matrix_world @ Vector(c)).z for o in C.all_objects if o.name.startswith('PLA_') and o.type in ('MESH', 'CURVE') for c in o.bound_box)
        print('ALTEZZA %.3f unita = %.0f cm' % (alto, alto / 2.30 * 175))
    cam = bpy.data.objects.new('Cam', bpy.data.cameras.new('Cam')); C.objects.link(cam); sc.camera = cam; cam.data.lens = lente; cam.data.sensor_width = 36
    cam.location = cam_pos; luci.punta(cam, Vector(mira))
    luci.cinema(C, mira, cam_pos, distanza=4.0, lato=1); luci.ombre_pulite(sc, mezza_risoluzione=False)
    N[0] += 1; p = '/tmp/pla_%02d.png' % N[0]; sc.render.filepath = p; bpy.ops.render.render(write_still=True); return p
cols = []
for st in (sys.argv[1:] or list(gn.STILI)):
    a = quadro(st, (2.4, -7.2, 1.7), (0.5, 0, 1.3), 40, pippo=True, posa=lambda G: gn.gesto(G, None, 'saluto'))
    b = quadro(st, (0.7, -3.2, 1.8), (0, 0, 1.74), 75, posa=lambda G: (gn.emozione(G, None, 'istituzionale'), gn.gesto(G, None, 'mani giunte')))
    c = quadro(st, (2.6, -2.0, 1.95), (0, 0, 1.77), 65, posa=lambda G: (gn.emozione(G, None, 'composto'), gn.gesto(G, None, 'mano aperta')))
    cols.append((st, a, b, c))
from PIL import Image, ImageDraw, ImageFont
ft = ImageFont.truetype(os.path.join(QUI, '..', 'assets', 'font', 'Bangers-Regular.ttf'), 44)
NOMI = {'A': 'A  AZZURRO POLVERE', 'B': 'B  ROSA ANTICO', 'C': 'C  BLU ISTITUZIONALE'}
foglio = Image.new('RGB', (W * len(cols), H * 3 + 70), (20, 20, 24)); d = ImageDraw.Draw(foglio)
for c, (st, *ps) in enumerate(cols):
    d.text((c * W + 14, 12), NOMI[st], fill=(255, 235, 60), font=ft, stroke_width=4, stroke_fill=(0, 0, 0))
    for r, p in enumerate(ps): foglio.paste(Image.open(p).convert('RGB'), (c * W, 70 + r * H))
foglio.save(os.path.join(QUI, '..', 'schede', 'platino_versioni.jpg'), quality=88); print('SCHEDA', N[0])
