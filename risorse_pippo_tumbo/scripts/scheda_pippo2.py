"""Scheda del rebranding di Pippo: capelli (P), occhi (Q), corpo (R). Uso: python scheda_pippo2.py
Rende in ../out/pippo2/ e compone ../schede/pippo2_capelli.png, pippo2_occhi.png, pippo2_corpo.png."""
import sys, os, math
QUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, QUI)
import bpy
from mathutils import Vector
from common import *
from render_setup import *
import pippo2, set004, luci
OUT = os.path.join(QUI, '..', 'out', 'pippo2'); SCHEDE = os.path.join(QUI, '..', 'schede'); os.makedirs(OUT, exist_ok=True)

def scena(nome, varianti, primo_piano):
    reset_scene(); set004._c.clear(); scene = bpy.context.scene
    C = collection('C'); world(scene, top=(0.62, 0.80, 1.0), bottom=(0.92, 0.90, 0.86), strength=0.8)
    bpy.ops.mesh.primitive_plane_add(size=80); bpy.context.object.data.materials.append(material('ground', (0.42, 0.66, 0.36), rough=0.95))
    n = len(varianti); passo = (1.15 if n > 3 else 1.5) if primo_piano else 2.1
    for i, kw in enumerate(varianti):
        P = pippo2.build_pippo(C, **kw); P['root'].location = ((i - (n - 1) / 2) * passo, 0, 0); P['root'].rotation_euler = (0, 0, 0.18)
        pippo2.express(P, 1, smile=0.6, brow=0.1)
    if primo_piano: cam, tgt, lens, w, h = (0, -9.5, 1.85), (0, 0, 1.80), 72, 1920, 620
    else: cam, tgt, lens, w, h = (0, -11, 1.1), (0, 0, 1.0), 60, 1620, 1000
    setup_render(scene, w, h, samples=24, fps=24, frames=3)
    scene.camera = camera('Cam', Vector(cam), Vector(tgt), lens=lens, coll=C)
    luci.cielo_basso(scene.world, 0.4); luci.cinema(C, (0, 0, 1.4), cam, distanza=6, forza=0.35, lato=1); luci.ombre_pulite(scene, mezza_risoluzione=False)
    scene.render.filepath = os.path.join(OUT, nome + '.png'); bpy.ops.render.render(write_still=True); print('RESA', nome, flush=True)

def componi(nome, etichette):
    from PIL import Image, ImageDraw, ImageFont
    F = os.path.join(QUI, '..', 'assets', 'font', 'LuckiestGuy-Regular.ttf')
    im = Image.open(os.path.join(OUT, nome + '.png')).convert('RGB'); d = ImageDraw.Draw(im); n = len(etichette)
    for i, (l, t) in enumerate(etichette):
        x = int(im.width * (i + 0.5) / n)
        d.text((x, 50), l, font=ImageFont.truetype(F, 72), fill=(255, 225, 60), stroke_width=6, stroke_fill=(20, 20, 30), anchor='mm')
        d.text((x, im.height - 36), t, font=ImageFont.truetype(F, 34), fill=(255, 255, 255), stroke_width=4, stroke_fill=(20, 20, 30), anchor='mm')
    im.save(os.path.join(SCHEDE, 'pippo2_' + nome + '.png'))

EMOZIONI = [('normale', dict()), ('felice', dict(smile=1.0, brow_lift=0.3)), ('ride', dict(smile=1.0, mouth_open=1.0, eye_open=0.35, brow_lift=0.5)),
            ('arrabbiato', dict(brow=1.0, smile=-0.8, mouth_open=0.35, eye_open=0.8)), ('triste', dict(brow=-0.9, smile=-1.0, look=(0, -0.8), eye_open=0.85)),
            ('spaventato', dict(brow=-1.0, brow_lift=0.8, mouth_open=0.9, eye_scale=1.25, smile=-0.4)), ('sorpreso', dict(brow_lift=1.0, mouth_open=0.6, eye_scale=1.2)),
            ('furbo', dict(brow=0.6, smile=0.8, eye_open=0.5, look=(1, 0)))]


def emozioni(nome_file='pippo2_emozioni.png', **pezzi):
    """Otto primi piani, uno per emozione, composti in una griglia 2x4."""
    from PIL import Image, ImageDraw, ImageFont
    reset_scene(); set004._c.clear(); scene = bpy.context.scene
    C = collection('C'); world(scene, top=(0.62, 0.80, 1.0), bottom=(0.92, 0.90, 0.86), strength=0.8)
    P0 = []
    for i, (nome, ex) in enumerate(EMOZIONI):
        P = pippo2.build_pippo(C, **pezzi); P['root'].location = (i * 4.0, 0, 0); P['root'].rotation_euler = (0, 0, 0.2); pippo2.express(P, 1, **ex)
    setup_render(scene, 800, 820, samples=24, fps=24, frames=3)
    cam = camera('Cam', Vector((0, -4.2, 1.95)), Vector((0, 0, 1.80)), lens=85, coll=C); scene.camera = cam
    luci.cielo_basso(scene.world, 0.45); luci.sole(C, (0, -1), lato=1, energia=3.0); luci.ombre_pulite(scene, mezza_risoluzione=False)
    F = os.path.join(QUI, '..', 'assets', 'font', 'LuckiestGuy-Regular.ttf')
    foglio = Image.new('RGB', (800 * 4, 820 * 2), (20, 20, 30))
    for i, (nome, ex) in enumerate(EMOZIONI):
        cam.location = (i * 4.0, -4.2, 1.95); cam.rotation_euler = (Vector((i * 4.0, 0, 1.80)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
        f = os.path.join(OUT, 'emo_%d.png' % i); scene.render.filepath = f; bpy.ops.render.render(write_still=True)
        im = Image.open(f).convert('RGB'); d = ImageDraw.Draw(im)
        d.text((400, 760), nome, font=ImageFont.truetype(F, 64), fill=(255, 225, 60), stroke_width=6, stroke_fill=(20, 20, 30), anchor='mm')
        foglio.paste(im, ((i % 4) * 800, (i // 4) * 820))
    foglio.resize((1600, 820)).save(os.path.join(SCHEDE, nome_file)); print('RESA emozioni', flush=True)


def esagerate():
    """Le emozioni esagerate (pippo2.emozione): mezzo busto, per vedere anche braccia e posa."""
    from PIL import Image, ImageDraw, ImageFont
    reset_scene(); set004._c.clear(); scene = bpy.context.scene
    C = collection('C'); world(scene, top=(0.62, 0.80, 1.0), bottom=(0.92, 0.90, 0.86), strength=0.8)
    nomi = list(pippo2.EMOZIONI_FORTI)
    for i, n in enumerate(nomi):
        P = pippo2.build_pippo(C); P['root'].location = (i * 4.0, 0, 0); P['root'].rotation_euler = (0, 0, 0.25); pippo2.emozione(P, 1, n)
    setup_render(scene, 800, 900, samples=24, fps=24, frames=3)
    cam = camera('Cam', Vector((0, -3.7, 1.85)), Vector((0, 0, 1.55)), lens=50, coll=C); scene.camera = cam
    luci.cielo_basso(scene.world, 0.45); luci.sole(C, (0, -1), lato=1, energia=3.0); luci.ombre_pulite(scene, mezza_risoluzione=False)
    F = os.path.join(QUI, '..', 'assets', 'font', 'LuckiestGuy-Regular.ttf')
    foglio = Image.new('RGB', (800 * 4, 900 * 2), (20, 20, 30))
    for i, n in enumerate(nomi):
        cam.location = (i * 4.0, -3.7, 1.85); cam.rotation_euler = (Vector((i * 4.0, 0, 1.55)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
        f = os.path.join(OUT, 'forte_%d.png' % i); scene.render.filepath = f; bpy.ops.render.render(write_still=True)
        im = Image.open(f).convert('RGB'); ImageDraw.Draw(im).text((400, 850), n, font=ImageFont.truetype(F, 64), fill=(255, 225, 60), stroke_width=6, stroke_fill=(20, 20, 30), anchor='mm')
        foglio.paste(im, ((i % 4) * 800, (i // 4) * 900))
    foglio.resize((1600, 900)).save(os.path.join(SCHEDE, 'pippo_emozioni_esagerate.png')); print('RESA esagerate', flush=True)


if __name__ == '__main__':
    cosa = sys.argv[-1]
    if cosa in ('capelli', 'tutto'):
        scena('capelli', [dict(capelli=c, occhi='Q0') for c in ('P0',)] + [dict()], True)
        componi('capelli', [('Prima', 'Pippo di adesso'), ('Dopo', 'Pippo nuovo')])
    if cosa in ('occhi', 'tutto'):
        scena('occhi', [dict(occhi=c) for c in ('Q0', 'Q4', 'Q5')], True)
        componi('occhi', [('Q0', 'di prima'), ('Q4', 'come Gualtiero'), ('Q5', 'come Gualtiero, piu grandi')])
    if cosa in ('emozioni', 'tutto'):
        emozioni()
    if cosa == 'esagerate':
        esagerate()
    if cosa == 'emozioni_vecchio':
        emozioni('pippo_vecchio_emozioni.png', capelli='P0', occhi='Q0', corpo='R0')
    if cosa in ('corpo', 'tutto'):
        scena('corpo', [dict(corpo=c) for c in ('R0', 'R1', 'R2')], False)
        componi('corpo', [('R0', 'di prima'), ('R1', 'spalle e fianchi'), ('R2', 'piu larghi')])
