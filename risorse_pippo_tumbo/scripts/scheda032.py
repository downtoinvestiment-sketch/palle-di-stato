"""Scheda del video 032 (Francesco ci prova): tre Francesco tostapane (T1, T2, T3) con Pippo per la misura,
due Vanessa lavatrice (V1, V2), due frigoriferi palestrati (P1, P2).
Uso: python scheda032.py  ->  ../schede/scelta032.jpg"""
import sys, os, math
QUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, QUI); sys.path.insert(0, os.path.join(QUI, '..', 'assets'))
import bpy
from mathutils import Vector
from common import *
from render_setup import *
import pippo, props032, set004, luci
import pt_assets as A
OUT = os.path.join(QUI, '..', 'out', 'scheda032'); SCHEDE = os.path.join(QUI, '..', 'schede'); os.makedirs(OUT, exist_ok=True)

def scena(cosa):
    reset_scene(); set004._c.clear(); scene = bpy.context.scene
    C = collection('C'); world(scene, top=(0.62, 0.80, 1.0), bottom=(0.95, 0.88, 0.75), strength=0.4)
    M = props032.mats032(); font = bpy.data.fonts.load(A.font('luckiest'))
    def cam(loc, tgt, lens, w, h, dist=None, forza=0.45):
        setup_render(scene, w, h, samples=24, fps=24, frames=3); c_ = camera('Cam', Vector(loc), Vector(tgt), lens=lens, coll=C); c_.data.clip_end = 400; scene.camera = c_
        luci.cinema(C, Vector(tgt), Vector(loc), distanza=dist or (Vector(loc) - Vector(tgt)).length * 0.7, lato=-1, forza=forza, nome='Cinema')
    bpy.ops.mesh.primitive_plane_add(size=200); bpy.context.object.data.materials.append(material('pav', (0.75, 0.72, 0.68), rough=0.8))
    bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 4, 10), rotation=(math.pi / 2, 0, 0)); bpy.context.object.data.materials.append(material('muro', (0.55, 0.78, 0.82), rough=0.8))
    P = pippo.build_pippo(C); pippo.express(P, 1, smile=0.6, eye_scale=1.1)
    if cosa == 'francesco':
        P['root'].location = (-1.5, 0.4, 0)
        for i, t in enumerate(('T1', 'T2', 'T3')):
            R = props032.francesco(C, M, t, A=A, font=font, nome='Fr' + t); R['root'].location = (-0.55 + 0.75 * i, 0, 0)
        cam((-0.2, -5.0, 0.8), (-0.2, 0, 0.45), 55, 1800, 1000)
    elif cosa == 'vanessa':
        P['root'].location = (-1.9, 0.4, 0)
        for i, t in enumerate(('V1', 'V2')):
            R = props032.vanessa(C, M, t, A=A, nome='Va' + t); R['root'].location = (-0.5 + 1.3 * i, 0, 0)
        cam((-0.3, -6.0, 1.0), (-0.3, 0, 0.55), 50, 1800, 1000)
    else:
        P['root'].location = (-2.1, 0.4, 0)
        for i, t in enumerate(('P1', 'P2')):
            R = props032.frigorifero(C, M, t, A=A, nome='Fg' + t); R['root'].location = (-0.4 + 1.9 * i, 0, 0)
        cam((-0.3, -8.5, 1.3), (-0.3, 0, 0.95), 45, 1800, 1100)
    scene.render.filepath = os.path.join(OUT, cosa + '.png'); bpy.ops.render.render(write_still=True); print('RESA', cosa, flush=True)

def componi():
    from PIL import Image, ImageDraw, ImageFont
    F = os.path.join(QUI, '..', 'assets', 'font', 'LuckiestGuy-Regular.ttf')
    def tit(im, t, xy, size=64, col=(255, 225, 60)):
        ImageDraw.Draw(im).text(xy, t, font=ImageFont.truetype(F, size), fill=col, stroke_width=max(3, size // 11), stroke_fill=(20, 20, 30), anchor='mm')
    ims = [Image.open(os.path.join(OUT, n + '.png')).convert('RGB') for n in ('francesco', 'vanessa', 'frigo')]
    W = ims[0].width; im = Image.new('RGB', (W, sum(i.height for i in ims) + 20), (20, 20, 30))
    y = 0; ys = []
    for i in ims: im.paste(i, (0, y)); ys.append(y); y += i.height + 10
    tit(im, 'FRANCESCO (TOSTAPANE)', (W // 2, 55), 70)
    for x, l in ((0.40, 'T1'), (0.61, 'T2'), (0.82, 'T3')): tit(im, l, (int(W * x), 150), 72)
    tit(im, 'VANESSA (LAVATRICE)', (W // 2, ys[1] + 55), 70)
    for x, l in ((0.45, 'V1'), (0.78, 'V2')): tit(im, l, (int(W * x), ys[1] + 150), 72)
    tit(im, 'IL FRIGORIFERO PALESTRATO', (W // 2, ys[2] + 55), 64)
    for x, l in ((0.45, 'P1'), (0.80, 'P2')): tit(im, l, (int(W * x), ys[2] + 150), 72)
    for yy, h in zip(ys, [i.height for i in ims]): tit(im, 'PIPPO', (int(W * 0.12), yy + h - 40), 36, (255, 255, 255))
    im.save(os.path.join(SCHEDE, 'scelta032.jpg'), quality=86); print('SCHEDA FATTA', flush=True)

if __name__ == '__main__':
    for c in sys.argv[1:] or ('francesco', 'vanessa', 'frigo'): scena(c)
    componi()
