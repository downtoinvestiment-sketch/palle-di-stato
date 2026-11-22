"""Scheda delle emozioni di Eleonora. Uso: python scheda_eleonora.py -> ../schede/eleonora_emozioni.png"""
import sys, os, math
QUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, QUI)
import bpy
from mathutils import Vector
from common import *
from render_setup import *
import props012, eleonora, set004, luci
from PIL import Image, ImageDraw, ImageFont
OUT = os.path.join(QUI, '..', 'out', 'eleonora'); SCHEDE = os.path.join(QUI, '..', 'schede'); os.makedirs(OUT, exist_ok=True)
reset_scene(); set004._c.clear(); scene = bpy.context.scene
C = collection('C'); world(scene, top=(0.62, 0.80, 1.0), bottom=(0.92, 0.90, 0.86), strength=0.8)
Z12 = props012.mats012(); nomi = list(eleonora.EMOZIONI); H = 1.3          # Eleonora ingrandita come nel 017
for i, n in enumerate(nomi):
    Z = eleonora.zucchina(C, Z12); Z['root'].location = (i * 3.0, 0, 0.32 * H); Z['root'].scale = (H,) * 3
    eleonora.velo(Z, False); eleonora.emozione(Z, None, n)
bpy.ops.mesh.primitive_plane_add(size=200); bpy.context.object.data.materials.append(material('ground', (0.42, 0.66, 0.36), rough=0.95))
setup_render(scene, 800, 900, samples=24, fps=24, frames=3)
cam = camera('Cam', Vector((0, -2.4, 1.35)), Vector((0, 0, 1.22)), lens=75, coll=C); scene.camera = cam
luci.cielo_basso(scene.world, 0.45); luci.sole(C, (0, -1), lato=1, energia=3.0); luci.ombre_pulite(scene, mezza_risoluzione=False)
F = os.path.join(QUI, '..', 'assets', 'font', 'LuckiestGuy-Regular.ttf')
foglio = Image.new('RGB', (800 * 4, 900 * 2), (20, 20, 30))
for i, n in enumerate(nomi):
    cam.location = (i * 3.0, -2.4, 1.35); cam.rotation_euler = (Vector((i * 3.0, 0, 1.22)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
    f = os.path.join(OUT, 'emo_%d.png' % i); scene.render.filepath = f; bpy.ops.render.render(write_still=True)
    im = Image.open(f).convert('RGB'); ImageDraw.Draw(im).text((400, 840), n, font=ImageFont.truetype(F, 64), fill=(255, 225, 60), stroke_width=6, stroke_fill=(20, 20, 30), anchor='mm')
    foglio.paste(im, ((i % 4) * 800, (i // 4) * 900))
foglio.resize((1600, 900)).save(os.path.join(SCHEDE, 'eleonora_emozioni.png')); print('RESA eleonora', flush=True)
