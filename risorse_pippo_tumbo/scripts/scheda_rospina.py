"""Scheda di Rospina: le tre versioni (A, B, C) con Pippo per la misura, e quattro facce della versione A.
Uso: python scheda_rospina.py  ->  ../schede/rospina_opzioni.jpg"""
import sys, os, math
QUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, QUI)
import bpy
from mathutils import Vector
from common import *
from render_setup import *
import pippo, rospina, set004, luci
OUT = os.path.join(QUI, '..', 'out', 'rospina'); SCHEDE = os.path.join(QUI, '..', 'schede'); os.makedirs(OUT, exist_ok=True)

def scena(cosa):
    reset_scene(); set004._c.clear(); scene = bpy.context.scene
    C = collection('C'); world(scene, top=(0.62, 0.80, 1.0), bottom=(0.92, 0.90, 0.86), strength=0.35)
    bpy.ops.mesh.primitive_plane_add(size=80); bpy.context.object.data.materials.append(material('ground', (0.42, 0.66, 0.36), rough=0.95))
    RM = rospina.mats_rospina()
    def cam(loc, tgt, lens, w, h):
        setup_render(scene, w, h, samples=24, fps=24, frames=3); scene.camera = camera('Cam', Vector(loc), Vector(tgt), lens=lens, coll=C)
        luci.cinema(C, Vector(tgt), Vector(loc), distanza=(Vector(loc) - Vector(tgt)).length * 0.7, lato=-1, forza=0.35, nome='Cinema')
    if cosa == 'opzioni':
        P = pippo.build_pippo(C); P['root'].location = (-2.35, 0.3, 0); pippo.express(P, 1, smile=-0.2, brow=-0.4, eye_scale=1.1)
        for i, (st, fx) in enumerate(zip(('D', 'E', 'F'), (dict(lid=0.15, mouth=0.2, smile=0.5), dict(lid=-0.2, mouth=0.6, gola=0.8, brow=-0.8, smile=-0.2), dict(lid=0.45, mouth=0.05, smile=0.7, brow=0.2)))):
            R = rospina.rospina(C, RM, st); R['root'].location = ((i - 0.6) * 1.5, 0, 0); R['root'].rotation_euler = (0, 0, (0.6 - i) * 0.15); rospina.rex(R, None, **fx)
        cam((-0.4, -10.5, 1.55), (-0.4, 0, 1.05), 55, 1800, 1080)
    else:
        facce = [dict(lid=0.2, mouth=0.15, smile=0.5), dict(lid=-0.35, mouth=0.9, gola=1.0, brow=-1.0, smile=-0.3),
                 dict(lid=0.5, mouth=0.4, brow=1.0, smile=-0.8, diverge=0.0), dict(lid=0.6, mouth=0.0, smile=0.9, brow=0.3, look=(0.6, 0.2))]
        for i, fx in enumerate(facce):
            R = rospina.rospina(C, RM, 'D'); R['root'].location = ((i - 1.5) * 1.25, 0, 0); rospina.rex(R, None, **fx)
        cam((0, -12.5, 1.90), (0, 0, 1.78), 85, 1800, 600)
    scene.render.filepath = os.path.join(OUT, cosa + '.png'); bpy.ops.render.render(write_still=True); print('RESA', cosa, flush=True)

def componi():
    from PIL import Image, ImageDraw, ImageFont
    F = os.path.join(QUI, '..', 'assets', 'font', 'LuckiestGuy-Regular.ttf')
    def tit(im, t, xy, size=64, col=(255, 225, 60)):
        ImageDraw.Draw(im).text(xy, t, font=ImageFont.truetype(F, size), fill=col, stroke_width=max(3, size // 11), stroke_fill=(20, 20, 30), anchor='mm')
    o = Image.open(os.path.join(OUT, 'opzioni.png')).convert('RGB'); f = Image.open(os.path.join(OUT, 'facce.png')).convert('RGB')
    f = f.resize((o.width, int(f.height * o.width / f.width)))
    im = Image.new('RGB', (o.width, o.height + f.height + 10), (20, 20, 30)); im.paste(o, (0, 0)); im.paste(f, (0, o.height + 10))
    tit(im, 'ROSPINA', (o.width // 2, 60), 90)
    for x, l, d in ((0.395, 'D', 'blazer blu navy'), (0.61, 'E', 'blazer rosso'), (0.825, 'F', 'blazer viola')):
        tit(im, l, (int(o.width * x), 150), 80); tit(im, d, (int(o.width * x), o.height - 40), 34, (255, 255, 255))
    tit(im, 'Pippo', (int(o.width * 0.115), o.height - 40), 34, (255, 255, 255))
    for i, t in enumerate(['normale', 'scandalizzata', 'arrabbiata', 'si sente importante']):
        tit(im, t, (int(o.width * (0.125 + 0.25 * i)), o.height + 10 + 36), 32, (255, 255, 255))
    im.save(os.path.join(SCHEDE, 'rospina_blazer.jpg'), quality=88); print('SCHEDA FATTA', flush=True)

if __name__ == '__main__':
    for c in ('opzioni', 'facce'): scena(c)
    componi()
