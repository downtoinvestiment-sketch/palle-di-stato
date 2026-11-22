"""Scheda del video 027 (Francesco il cactus): tre Francesco (F1, F2, F3) con Pippo per la misura, il parrucchiere
(poltrona da barbiere della libreria), due mongolfiere (M1, M2) su due sabbie (S1, S2) con Francesca alta come un grattacielo.
Uso: python scheda027.py  ->  ../schede/scelta027.jpg"""
import sys, os, math
QUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, QUI); sys.path.insert(0, os.path.join(QUI, '..', 'assets'))
import bpy
from mathutils import Vector
from common import *
from render_setup import *
import pippo, props027, set004, luci
import pt_assets as A
OUT = os.path.join(QUI, '..', 'out', 'scheda027'); SCHEDE = os.path.join(QUI, '..', 'schede'); os.makedirs(OUT, exist_ok=True)

def scena(cosa):
    reset_scene(); set004._c.clear(); scene = bpy.context.scene
    C = collection('C'); world(scene, top=(0.62, 0.80, 1.0), bottom=(0.95, 0.88, 0.75), strength=0.4)
    M = props027.mats027(); font = bpy.data.fonts.load(A.font('luckiest'))
    def cam(loc, tgt, lens, w, h, dist=None, forza=0.45):
        setup_render(scene, w, h, samples=24, fps=24, frames=3); c_ = camera('Cam', Vector(loc), Vector(tgt), lens=lens, coll=C); c_.data.clip_end = 400; scene.camera = c_
        luci.cinema(C, Vector(tgt), Vector(loc), distanza=dist or (Vector(loc) - Vector(tgt)).length * 0.7, lato=-1, forza=forza, nome='Cinema')
    def suolo(mat, size=200, loc=(0, 0, 0)):
        bpy.ops.mesh.primitive_plane_add(size=size, location=loc); bpy.context.object.data.materials.append(mat)
    if cosa == 'francesco':
        suolo(material('pav', (0.75, 0.72, 0.68), rough=0.8))
        P = pippo.build_pippo(C); P['root'].location = (-1.75, 0.4, 0); pippo.express(P, 1, smile=0.6, eye_scale=1.1)
        for i, t in enumerate(('F1', 'F2', 'F3')):
            R = props027.francesco(C, M, t, font=font, nome='Fr' + t); R['root'].location = (-0.55 + 0.95 * i, 0, 0)
        cam((-0.3, -6.2, 1.05), (-0.3, 0, 0.6), 55, 1800, 1000)
    elif cosa == 'parrucchiere':
        suolo(material('piastrelle', (0.92, 0.9, 0.86), rough=0.4))
        bpy.ops.mesh.primitive_plane_add(size=8, location=(0, 1.6, 2), rotation=(math.pi / 2, 0, 0)); bpy.context.object.data.materials.append(material('muro', (0.55, 0.78, 0.82), rough=0.8))
        ch = A.modello('BarberShopChair_01', posizione=(0, 0, 0), altezza=1.15, rotazione=0, collezione=C, appoggia=True)
        bpy.context.view_layer.update()
        top = max((o.matrix_world @ Vector(v)).z for o in ch.children_recursive if o.type == 'MESH' for v in o.bound_box)
        R = props027.francesco(C, M, 'F1', font=font, nome='FrP'); R['root'].location = (0, -0.12, 0.60)
        try: A.modello('kenney/furniture-kit/bathroomMirror', posizione=(0, 1.55, 1.2), altezza=1.0, rotazione=180, collezione=C)
        except Exception as e: print('specchio', e)
        cam((1.6, -3.0, 1.5), (0, 0, 0.9), 40, 1800, 1000)
    else:
        for (aid, x0) in (('Ground054', -60), ('sandy_gravel_02', 60)):
            mt = A.materiale(aid, dimensione=4.0, tinta=(1.1, 1.0, 0.85))
            bpy.ops.mesh.primitive_plane_add(size=120, location=(x0, 40, 0)); bpy.context.object.data.materials.append(mt)
        for i, t in enumerate(('M1', 'M2')):
            Rm = props027.mongolfiera(C, M, t, nome='Mg' + t); Rm['root'].location = (-7 + 14 * i, 6, 0)
        F = props027.francesca(C, M, altezza=34.0); F['root'].location = (0, 40, 0)
        cam((0, -30, 7), (0, 14, 12), 30, 1800, 1100, dist=30, forza=1.2)
    scene.render.filepath = os.path.join(OUT, cosa + '.png'); bpy.ops.render.render(write_still=True); print('RESA', cosa, flush=True)

def componi():
    from PIL import Image, ImageDraw, ImageFont
    F = os.path.join(QUI, '..', 'assets', 'font', 'LuckiestGuy-Regular.ttf')
    def tit(im, t, xy, size=64, col=(255, 225, 60)):
        ImageDraw.Draw(im).text(xy, t, font=ImageFont.truetype(F, size), fill=col, stroke_width=max(3, size // 11), stroke_fill=(20, 20, 30), anchor='mm')
    a = Image.open(os.path.join(OUT, 'francesco.png')).convert('RGB'); b = Image.open(os.path.join(OUT, 'parrucchiere.png')).convert('RGB'); c = Image.open(os.path.join(OUT, 'mongolfiere.png')).convert('RGB')
    W = a.width; im = Image.new('RGB', (W, a.height + b.height + c.height + 20), (20, 20, 30))
    im.paste(a, (0, 0)); im.paste(b, (0, a.height + 10)); im.paste(c, (0, a.height + b.height + 20))
    tit(im, 'FRANCESCO', (W // 2, 55), 80)
    for x, l in ((0.37, 'F1'), (0.585, 'F2'), (0.795, 'F3')): tit(im, l, (int(W * x), 150), 72)
    tit(im, 'PIPPO', (int(W * 0.13), a.height - 40), 36, (255, 255, 255))
    tit(im, 'IL PARRUCCHIERE', (W // 2, a.height + 10 + 55), 64)
    y0 = a.height + b.height + 20
    tit(im, 'MONGOLFIERA E DESERTO', (W // 2, y0 + 55), 64)
    tit(im, 'M1 + S1', (int(W * 0.2), y0 + c.height - 50), 56); tit(im, 'M2 + S2', (int(W * 0.8), y0 + c.height - 50), 56)
    tit(im, 'FRANCESCA', (W // 2, y0 + 140), 48, (255, 150, 200))
    im.save(os.path.join(SCHEDE, 'scelta027.jpg'), quality=86); print('SCHEDA FATTA', flush=True)

if __name__ == '__main__':
    for c in sys.argv[1:] or ('francesco', 'parrucchiere', 'mongolfiere'): scena(c)
    componi()
