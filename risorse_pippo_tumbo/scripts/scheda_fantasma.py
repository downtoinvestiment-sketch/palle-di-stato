"""Scheda del nuovo personaggio, il Fantasma (22 novembre 2026): tre versioni (A telo e scarpe lucide, B con cravatta e spilla, C con la giacca),
corpo intero accanto a Pippo e primo piano degli occhi -> ../schede/fantasma_versioni.jpg"""
import sys, os
QUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, QUI)
import bpy
from mathutils import Vector
from common import *
from render_setup import *
import kitlook, luci, set004, pippo2, fantasma as fa
A = kitlook.A; W, H = 520, 760; N = [0]
def quadro(stile, cam_pos, mira, lente, pippo=False, posa=None):
    reset_scene(); set004._c.clear(); sc = bpy.context.scene; C = collection('C'); setup_render(sc, W, H, samples=12, fps=24, frames=1); A.qualita_eevee(preset='equilibrato', riflessi=False, scena=sc, risoluzione=(W, H))
    world(sc, top=(0.55, 0.65, 0.9), bottom=(0.9, 0.85, 0.8), strength=1.0); luci.cielo_basso(sc.world, 0.45)
    shape('Suolo', 'cyl:30:0.1', loc=(0, 0, -0.05), mat=material('suolo_f', (0.62, 0.6, 0.57), rough=0.9), coll=C)
    F = fa.fantasma(C, stile)
    if posa: posa(F)
    if pippo: P = pippo2.build_pippo(C); P['root'].location = (1.1, 0, 0)
    cam = bpy.data.objects.new('Cam', bpy.data.cameras.new('Cam')); C.objects.link(cam); sc.camera = cam; cam.data.lens = lente
    cam.location = cam_pos; luci.punta(cam, Vector(mira)); luci.cinema(C, mira, cam_pos, distanza=4.0, lato=1); luci.ombre_pulite(sc, mezza_risoluzione=False)
    N[0] += 1; p = '/tmp/fan_%02d.png' % N[0]; sc.render.filepath = p; bpy.ops.render.render(write_still=True); return p
cols = []
for st in (sys.argv[1:] or ['A', 'B', 'C']):
    a = quadro(st, (0.55, -7.6, 1.5), (0.55, 0, 1.2), 40, pippo=True, posa=lambda F: fa.gesto(F, None, 'saluto'))
    b = quadro(st, (0.5, -3.0, 2.0), (0, 0, 1.8), 60, posa=lambda F: (fa.emozione(F, None, 'furbo'), fa.gesto(F, None, 'comizio')))
    c = quadro(st, (-0.6, -2.4, 1.95), (0, 0, 1.85), 70, posa=lambda F: (fa.emozione(F, None, 'sorpreso'), fa.gesto(F, None, 'non sono stato io')))
    cols.append((st, a, b, c))
from PIL import Image, ImageDraw, ImageFont
ft = ImageFont.truetype(os.path.join(QUI, '..', 'assets', 'font', 'Bangers-Regular.ttf'), 44)
NOMI = {'A': 'A  TELO E PANTALONI', 'B': 'B  CRAVATTA E SPILLA', 'C': 'C  GIACCA SOPRA IL TELO'}
foglio = Image.new('RGB', (W * len(cols), H * 3 + 70), (20, 20, 24)); d = ImageDraw.Draw(foglio)
for c, (st, *ps) in enumerate(cols):
    d.text((c * W + 14, 12), NOMI[st], fill=(255, 235, 60), font=ft, stroke_width=4, stroke_fill=(0, 0, 0))
    for r, p in enumerate(ps): foglio.paste(Image.open(p).convert('RGB'), (c * W, 70 + r * H))
foglio.save(os.path.join(QUI, '..', 'schede', 'fantasma_versioni.jpg'), quality=88); print('SCHEDA', N[0])
