"""Scheda della Castora: le tre versioni (A, B, C) con Pippo per la misura, le viste di lato e da dietro, e le otto espressioni.
Uso: python scheda_castora.py  ->  ../schede/castora_opzioni.jpg   (python scheda_castora.py A: le espressioni con lo stile A)"""
import sys, os, math
QUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, QUI)
import bpy
from mathutils import Vector
from common import *
from render_setup import *
import pippo, castora, set004, luci
OUT = os.path.join(QUI, '..', 'out', 'castora'); SCHEDE = os.path.join(QUI, '..', 'schede'); os.makedirs(OUT, exist_ok=True)
NOMI = list(castora.EMOZIONI); PI = math.pi

def scena(cosa, stile='A'):
    reset_scene(); set004._c.clear(); scene = bpy.context.scene
    C = collection('C'); world(scene, top=(0.62, 0.80, 1.0), bottom=(0.92, 0.90, 0.86), strength=0.35)
    bpy.ops.mesh.primitive_plane_add(size=80); bpy.context.object.data.materials.append(material('ground', (0.42, 0.66, 0.36), rough=0.95))
    KM = castora.mats_castora()
    def cam(loc, tgt, lens, w, h):
        setup_render(scene, w, h, samples=24, fps=24, frames=3); scene.camera = camera('Cam', Vector(loc), Vector(tgt), lens=lens, coll=C)
        luci.cinema(C, Vector(tgt), Vector(loc), distanza=(Vector(loc) - Vector(tgt)).length * 0.7, lato=-1, forza=0.35, nome='Cinema')
    if cosa == 'ufficiale':
        P = pippo.build_pippo(C); P['root'].location = (-2.5, 0.3, 0); pippo.express(P, 1, smile=-0.2, brow=-0.4, eye_scale=1.1)
        for i, (rz, em) in enumerate(((0.0, 'normale'), (0.75, 'saputella'), (PI / 2, 'normale'), (PI, 'normale'))):
            K = castora.castora(C, KM, 'A'); K['root'].location = (-1.0 + i * 1.35, 0, 0); K['root'].rotation_euler = (0, 0, rz); castora.emozione(K, None, em)
        cam((0.3, -11.5, 1.5), (0.3, 0, 1.10), 55, 1800, 1000)
    elif cosa == 'opzioni':
        P = pippo.build_pippo(C); P['root'].location = (-2.35, 0.3, 0); pippo.express(P, 1, smile=-0.2, brow=-0.4, eye_scale=1.1)
        for i, (st, em) in enumerate(zip('ABC', ('normale', 'saputella', 'trionfo'))):
            K = castora.castora(C, KM, st); K['root'].location = ((i - 0.6) * 1.5, 0, 0); K['root'].rotation_euler = (0, 0, (0.6 - i) * 0.15); castora.emozione(K, None, em)
        cam((-0.4, -10.5, 1.55), (-0.4, 0, 1.10), 55, 1800, 1080)
    elif cosa == 'viste':
        for i, (st, rz) in enumerate((('A', 0.9), ('A', PI / 2), ('A', PI), ('B', PI / 2), ('B', PI * 0.8))):
            K = castora.castora(C, KM, st); K['root'].location = ((i - 2) * 1.35, 0, 0); K['root'].rotation_euler = (0, 0, rz)
        cam((0, -11.5, 1.45), (0, 0, 1.10), 60, 1800, 700)
    else:
        for i, nome in enumerate(NOMI):
            K = castora.castora(C, KM, stile); K['root'].location = ((i - 3.5) * 1.12, 0, 0); castora.emozione(K, None, nome)
        cam((0, -17.0, 1.86), (0, 0, 1.80), 68, 2400, 520)
    scene.render.filepath = os.path.join(OUT, cosa + '.png'); bpy.ops.render.render(write_still=True); print('RESA', cosa, flush=True)

def componi():
    from PIL import Image, ImageDraw, ImageFont
    F = os.path.join(QUI, '..', 'assets', 'font', 'LuckiestGuy-Regular.ttf')
    def tit(im, t, xy, size=64, col=(255, 225, 60)):
        ImageDraw.Draw(im).text(xy, t, font=ImageFont.truetype(F, size), fill=col, stroke_width=max(3, size // 11), stroke_fill=(20, 20, 30), anchor='mm')
    o = Image.open(os.path.join(OUT, 'opzioni.png')).convert('RGB')
    v = Image.open(os.path.join(OUT, 'viste.png')).convert('RGB'); f = Image.open(os.path.join(OUT, 'facce.png')).convert('RGB')
    f = f.resize((o.width, int(f.height * o.width / f.width)))
    im = Image.new('RGB', (o.width, o.height + v.height + f.height + 20), (20, 20, 30))
    im.paste(o, (0, 0)); im.paste(v, (0, o.height + 10)); im.paste(f, (0, o.height + v.height + 20))
    tit(im, 'LA CASTORA', (o.width // 2, 60), 90)
    for x, l, d in ((0.395, 'A', 'come da descrizione'), (0.61, 'B', 'coda e naso scuro'), (0.825, 'C', 'castoro vero')):
        tit(im, l, (int(o.width * x), 150), 80); tit(im, d, (int(o.width * x), o.height - 40), 34, (255, 255, 255))
    tit(im, 'Pippo', (int(o.width * 0.115), o.height - 40), 34, (255, 255, 255))
    tit(im, 'A di lato e da dietro', (int(o.width * 0.35), o.height + 45), 34, (255, 255, 255))
    tit(im, 'B: la coda', (int(o.width * 0.80), o.height + 45), 34, (255, 255, 255))
    for i, t in enumerate(NOMI):
        tit(im, t, (int(o.width * (0.0625 + 0.125 * i)), o.height + v.height + 20 + 26), 24, (255, 255, 255))
    im.save(os.path.join(SCHEDE, 'castora_opzioni.jpg'), quality=88); print('SCHEDA FATTA', flush=True)

def componi_ufficiale():
    from PIL import Image, ImageDraw, ImageFont
    F = os.path.join(QUI, '..', 'assets', 'font', 'LuckiestGuy-Regular.ttf')
    def tit(im, t, xy, size=64, col=(255, 225, 60)):
        ImageDraw.Draw(im).text(xy, t, font=ImageFont.truetype(F, size), fill=col, stroke_width=max(3, size // 11), stroke_fill=(20, 20, 30), anchor='mm')
    o = Image.open(os.path.join(OUT, 'ufficiale.png')).convert('RGB'); f = Image.open(os.path.join(OUT, 'facce.png')).convert('RGB')
    f = f.resize((o.width, int(f.height * o.width / f.width)))
    im = Image.new('RGB', (o.width, o.height + f.height + 10), (20, 20, 30)); im.paste(o, (0, 0)); im.paste(f, (0, o.height + 10))
    tit(im, 'LA CASTORA', (o.width // 2, 60), 90)
    for i, t in enumerate(NOMI):
        tit(im, t, (int(o.width * (0.0625 + 0.125 * i)), o.height + 10 + 26), 24, (255, 255, 255))
    im.save(os.path.join(SCHEDE, 'castora_ufficiale.jpg'), quality=88); print('SCHEDA FATTA', flush=True)

if __name__ == '__main__' and 'ufficiale' in sys.argv:
    for c in ('ufficiale', 'facce'): scena(c, 'A')
    componi_ufficiale()
elif __name__ == '__main__':
    st = sys.argv[1] if len(sys.argv) > 1 else 'A'
    for c in ('opzioni', 'viste', 'facce'): scena(c, st)
    componi()
