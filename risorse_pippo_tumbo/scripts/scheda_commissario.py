"""Scheda del commissario (copione n. 26): le tre versioni con Pippo per la misura, e quattro facce della versione B (scelta).
Uso: python scheda_commissario.py  ->  ../schede/commissario_opzioni.jpg"""
import sys, os, math
QUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, QUI)
import bpy
from mathutils import Vector
from common import *
from render_setup import *
import pippo, commissario, set004, luci
OUT = os.path.join(QUI, '..', 'out', 'commissario'); SCHEDE = os.path.join(QUI, '..', 'schede'); os.makedirs(OUT, exist_ok=True)

def scena(cosa):
    reset_scene(); set004._c.clear(); scene = bpy.context.scene
    C = collection('C'); world(scene, top=(0.62, 0.80, 1.0), bottom=(0.92, 0.90, 0.86), strength=0.35)
    bpy.ops.mesh.primitive_plane_add(size=80); bpy.context.object.data.materials.append(material('ground', (0.42, 0.66, 0.36), rough=0.95))
    RM = commissario.mats_commissario()
    def cam(loc, tgt, lens, w, h):
        setup_render(scene, w, h, samples=24, fps=24, frames=3); scene.camera = camera('Cam', Vector(loc), Vector(tgt), lens=lens, coll=C)
        luci.cinema(C, Vector(tgt), Vector(loc), distanza=(Vector(loc) - Vector(tgt)).length * 0.7, lato=-1, forza=0.35, nome='Cinema')
    if cosa == 'opzioni':
        P = pippo.build_pippo(C); P['root'].location = (-2.35, 0.3, 0); pippo.express(P, 1, smile=-0.2, brow=-0.4, eye_scale=1.1)
        for i, (st, fx) in enumerate(zip(('A', 'B', 'C'), (dict(brow=0.6, mouth=0.15, smile=-0.3), dict(brow=0.2, smile=0.4), dict(brow=-0.6, mouth=0.5)))):
            R = commissario.commissario(C, RM, st); R['root'].location = ((i - 0.6) * 1.6, 0, 0); R['root'].rotation_euler = (0, 0, (0.6 - i) * 0.15); commissario.cex(R, None, **fx)
        cam((-0.4, -10.5, 1.55), (-0.4, 0, 1.05), 55, 1800, 1080)
    else:
        facce = [dict(lid=0.2, mouth=0.05), dict(lid=0.35, brow=1.0, mouth=0.35, smile=-0.6), dict(lid=-0.1, brow=-1.0, mouth=0.8, pancia=1.35), dict(lid=0.0, brow=-0.8, mouth=0.9, pancia=0.45, look=(0, 0.8))]
        for i, fx in enumerate(facce):
            R = commissario.commissario(C, RM, 'B'); R['root'].location = ((i - 1.5) * 1.35, 0, 0); commissario.cex(R, None, **fx)
        cam((0, -14.0, 1.55), (0, 0, 1.35), 70, 1800, 900)
    scene.render.filepath = os.path.join(OUT, cosa + '.png'); bpy.ops.render.render(write_still=True); print('RESA', cosa, flush=True)

def componi():
    from PIL import Image, ImageDraw, ImageFont
    F = os.path.join(QUI, '..', 'assets', 'font', 'LuckiestGuy-Regular.ttf')
    def tit(im, t, xy, size=64, col=(255, 225, 60)):
        ImageDraw.Draw(im).text(xy, t, font=ImageFont.truetype(F, size), fill=col, stroke_width=max(3, size // 11), stroke_fill=(20, 20, 30), anchor='mm')
    o = Image.open(os.path.join(OUT, 'opzioni.png')).convert('RGB'); f = Image.open(os.path.join(OUT, 'facce.png')).convert('RGB')
    f = f.resize((o.width, int(f.height * o.width / f.width)))
    im = Image.new('RGB', (o.width, o.height + f.height + 10), (20, 20, 30)); im.paste(o, (0, 0)); im.paste(f, (0, o.height + 10))
    tit(im, 'IL COMMISSARIO', (o.width // 2, 60), 90)
    for x, l, d in ((0.395, 'A', 'blu e baffoni'), (0.61, 'B', 'blu e occhiali'), (0.825, 'C', 'baffi e fischietto')):
        tit(im, l, (int(o.width * x), 150), 80); tit(im, d, (int(o.width * x), o.height - 40), 34, (255, 255, 255))
    tit(im, 'Pippo', (int(o.width * 0.115), o.height - 40), 34, (255, 255, 255))
    for i, t in enumerate(['normale', 'arrabbiato', 'abbracciato: si gonfia', 'bucato: si sgonfia']):
        tit(im, t, (int(o.width * (0.125 + 0.25 * i)), o.height + 10 + 36), 32, (255, 255, 255))
    im.save(os.path.join(SCHEDE, 'commissario_opzioni.jpg'), quality=88); print('SCHEDA FATTA', flush=True)

if __name__ == '__main__':
    for c in ('opzioni', 'facce'): scena(c)
    componi()
