"""Schede di Giulia: le tre versioni (A, B, C), le viste, le facce e la foto con Pippo e Gualtiero.
Uso:  python scheda_giulia.py [stile]      (stile = A, B o C per viste e facce; se manca, A)
Rende quattro immagini in ../out/giulia/ e compone ../schede/giulia_opzioni.png, giulia_viste.png, giulia_famiglia.png."""
import sys, os, math
QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
import bpy
from mathutils import Vector
from common import *
from render_setup import *
import pippo, tumbo, props009, giulia, set004

STILE = sys.argv[-1] if sys.argv[-1] in giulia.STILI else 'A'
OUT = os.path.join(QUI, '..', 'out', 'giulia'); SCHEDE = os.path.join(QUI, '..', 'schede')
os.makedirs(OUT, exist_ok=True)


def scena(cosa):
    reset_scene(); set004._c.clear(); scene = bpy.context.scene   # anche le mesh in memoria di set004 vanno azzerate
    C = collection('C'); world(scene, top=(0.62, 0.80, 1.0), bottom=(0.92, 0.90, 0.86), strength=0.75)
    sl = bpy.data.lights.new('Sun', 'SUN'); so = bpy.data.objects.new('Sun', sl); C.objects.link(so)
    so.rotation_euler = (math.radians(52), 0, math.radians(28)); sl.energy = 2.3; sl.angle = 0.25
    area_light('Fill', Vector((-5, -6, 3)), Vector((0, 0, 1.2)), 120, 5, coll=C)
    bpy.ops.mesh.primitive_plane_add(size=80); bpy.context.object.data.materials.append(material('ground', (0.42, 0.66, 0.36), rough=0.95))
    GM = giulia.mats_giulia(); G9 = props009.mats009()

    def cam(loc, tgt, lens, w, h):
        setup_render(scene, w, h, samples=24, fps=24, frames=3)
        scene.camera = camera('Cam', Vector(loc), Vector(tgt), lens=lens, coll=C)

    if cosa == 'opzioni':
        for i, st in enumerate(giulia.STILI):
            J = giulia.giulia(C, GM, st); J['root'].location = ((i - 1) * 1.55, 0, 0); J['root'].rotation_euler = (0, 0, (1 - i) * 0.12)
            giulia.giex(J, None, brow=(0.5, 0.2, 0.7)[i], mouth=(0.15, 0.5, 0.05)[i], lid=(0.5, 0.35, 0.55)[i])
        cam((0, -10.5, 1.5), (0, 0, 1.02), 60, 1620, 1080)
    elif cosa == 'famiglia':
        P = pippo.build_pippo(C); P['root'].location = (-2.05, 0, 0); pippo.express(P, 1, smile=-0.3, brow=-0.5, eye_scale=1.15)
        T = tumbo.build_tumbo(C, scale=0.75); T['root'].location = (-2.9, -0.5, 0)
        G = props009.gualtiero(C, G9); G['root'].location = (-0.55, 0, 0); props009.gex(G, 1, brow=-0.6, mouth=0.2)
        J = giulia.giulia(C, GM, STILE); J['root'].location = (0.95, 0, 0)
        giulia.giex(J, None, brow=0.9, mouth=0.35, lid=0.3, look=(-1, 0), naso=-0.6)
        giulia.mattarello(C, GM, J).rotation_euler = (0, 0, math.pi / 2); J['shoulderR'].rotation_euler = (0, -2.35, 0)
        cam((-0.7, -11, 1.6), (-0.7, 0, 1.05), 60, 1620, 1080)
    elif cosa == 'viste':
        for i, rz in enumerate((0.0, 0.75, math.pi / 2, math.pi)):
            J = giulia.giulia(C, GM, STILE); J['root'].location = ((i - 1.5) * 1.6, 0, 0); J['root'].rotation_euler = (0, 0, rz)
        cam((0, -13, 1.5), (0, 0, 1.02), 60, 1920, 1000)
    elif cosa == 'facce':
        facce = [dict(brow=0.4, mouth=0.1, lid=0.5), dict(brow=1.0, mouth=0.7, lid=0.15, naso=0.8),
                 dict(brow=-0.8, mouth=0.9, lid=0.0, naso=-0.5), dict(brow=0.0, mouth=0.0, lid=0.95)]
        for i, fx in enumerate(facce):
            J = giulia.giulia(C, GM, STILE); J['root'].location = ((i - 1.5) * 1.5, 0, 0); giulia.giex(J, None, **fx)
        cam((0, -15, 1.80), (0, 0, 1.66), 85, 1920, 600)
    scene.render.filepath = os.path.join(OUT, cosa + '.png'); bpy.ops.render.render(write_still=True); print('RESA', cosa, flush=True)


def componi():
    from PIL import Image, ImageDraw, ImageFont
    F = os.path.join(QUI, '..', 'assets', 'font', 'LuckiestGuy-Regular.ttf')

    def tit(im, testo, xy, size=64, col=(255, 225, 60)):
        ImageDraw.Draw(im).text(xy, testo, font=ImageFont.truetype(F, size), fill=col, stroke_width=max(3, size // 11), stroke_fill=(20, 20, 30), anchor='mm')

    o = Image.open(os.path.join(OUT, 'opzioni.png')).convert('RGB'); o = o.crop((120, 90, o.width - 120, o.height - 200))
    for i, (l, d) in enumerate([('A', 'bigodini e vestaglia'), ('B', 'permanente e leopardato'), ('C', 'crocchia e grembiule')]):
        x = int(o.width * (0.168 + 0.333 * i)); tit(o, l, (x, 60), 96); tit(o, d, (x, o.height - 48), 34, (255, 255, 255))
    o.save(os.path.join(SCHEDE, 'giulia_opzioni.png'))
    v = Image.open(os.path.join(OUT, 'viste.png')).convert('RGB'); f = Image.open(os.path.join(OUT, 'facce.png')).convert('RGB')
    v = v.crop((60, 120, v.width - 60, v.height - 170)); f = f.resize((v.width, int(f.height * v.width / f.width)))
    im = Image.new('RGB', (v.width, v.height + f.height + 12), (20, 20, 30)); im.paste(v, (0, 0)); im.paste(f, (0, v.height + 12))
    for i, t in enumerate(['davanti', 'di tre quarti', 'di lato', 'dietro']): tit(im, t, (int(v.width * (0.14 + 0.245 * i)), 40), 40, (255, 255, 255))
    for i, t in enumerate(['normale', 'arrabbiata', 'spaventata', 'dorme']): tit(im, t, (int(v.width * (0.14 + 0.24 * i)), v.height + 12 + 40), 40, (255, 255, 255))
    im.save(os.path.join(SCHEDE, 'giulia_viste.png'))
    fa = Image.open(os.path.join(OUT, 'famiglia.png')).convert('RGB'); fa = fa.crop((40, 150, fa.width - 40, fa.height - 170))
    tit(fa, 'GIULIA', (int(fa.width * 0.775), 50), 70); tit(fa, 'Gualtiero', (int(fa.width * 0.52), 70), 40, (255, 255, 255)); tit(fa, 'Pippo', (int(fa.width * 0.285), 70), 40, (255, 255, 255))
    fa.save(os.path.join(SCHEDE, 'giulia_famiglia.png'))
    print('SCHEDE FATTE', flush=True)


if __name__ == '__main__':
    for cosa in ('opzioni', 'viste', 'facce', 'famiglia'):
        scena(cosa)
    componi()
