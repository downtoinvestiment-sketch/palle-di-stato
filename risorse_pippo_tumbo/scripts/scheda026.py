"""Scheda di opzioni del video 026 «Tumbo fa HUSS»: la faccia di Tumbo quando fa HUSS (H1 stupore con gli occhi sbarrati,
H2 occhi da meme storti e lingua di lato, H3 soffio coi denti) e l'onda del verso (O1 anelli azzurri, O2 anelli bianchi da fumetto).
Uso:  python scheda026.py H1   (una opzione per processo), poi  python scheda026.py componi
Immagini in ../out/scheda026/, scheda finale in ../schede/scelta026.jpg"""
import sys, os, math
QUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, QUI)
import bpy
from mathutils import Vector
from common import *
from render_setup import *
import set004, props025, props026, luci, kitlook
import tumbo
A = kitlook.A
OUT = os.path.join(QUI, '..', 'out', 'scheda026'); SCHEDE = os.path.join(QUI, '..', 'schede'); os.makedirs(OUT, exist_ok=True); os.makedirs(SCHEDE, exist_ok=True)
PI = math.pi
FONT = A.font('luckiest')
OPZ = ('H1', 'H2', 'H3', 'O1', 'O2')


def scena(op):
    reset_scene(); set004._c.clear(); scene = bpy.context.scene
    C = collection('C')
    setup_render(scene, 900, 900, samples=8, fps=24, frames=1)
    A.qualita_eevee(preset='equilibrato', riflessi=True, scena=scene, risoluzione=(900, 900)); scene.view_settings.exposure = 0.1
    w = bpy.data.worlds.new('W'); scene.world = w; w.use_nodes = True
    bg = next(n for n in w.node_tree.nodes if n.type == 'BACKGROUND'); bg.inputs['Color'].default_value = (0.75, 0.8, 0.9, 1); bg.inputs['Strength'].default_value = 0.25
    cam = bpy.data.objects.new('Cam', bpy.data.cameras.new('Cam')); C.objects.link(cam); scene.camera = cam; cam.data.clip_start = 0.005
    def aim(loc, tgt, lens):
        cam.location = loc; luci.punta(cam, tgt); cam.data.lens = lens
    M25 = props025.mats025(); M = props026.mats026()
    props025.salotto(C, M25, A, x0=0.0, font=bpy.data.fonts.load(FONT))
    T = tumbo.build_tumbo(C, scale=0.75); T['root'].location = (0.0, 0.3, 0.0); T['root'].rotation_euler = (0, 0, 0.25)
    faccia = op if op[0] == 'H' else 'H2'
    B = props026.bocca_huss(C, M, T['head'], faccia); B.scale = (1, 1, 1)
    if faccia == 'H1':
        tumbo.tumbo_express(T, 1, brow=0.9, eye_scale=1.45)
        for nm in 'LR': T['pupil' + nm].scale = (0.45, 1, 0.45)
    elif faccia == 'H2':
        props026.nascondi_occhi(T); props026.occhi_giganti(C, M, T['head'], storti=True); tumbo.tumbo_express(T, 1, brow=0.5)
    else:
        tumbo.tumbo_express(T, 1, brow=-1.0, eye_scale=1.1, eye_open=0.55)
        for o in T['ear' + 'L'], T['ear' + 'R']: o.rotation_euler = (0.7, 0, 0)
    T['head'].rotation_euler = (-0.25, 0, 0.1)
    if op[0] == 'H':
        aim((0.28, -0.75, 0.62), (0.02, 0.0, 0.6), 50)
    else:
        O = props026.onda_huss(C, M, op, n=3); O.location = (-0.12, -0.2, 0.62); O.rotation_euler = (0, 0, 0.25); O.scale = (0.55, 0.55, 0.55)
        aim((1.6, -2.1, 0.95), (0.0, -0.3, 0.6), 30)
    luci.cinema(C, (0.0, 0.1, 0.6), (0.5, -1.6, 0.8), distanza=1.8, lato=-1, forza=0.6)
    luci.ombre_pulite(scene, mezza_risoluzione=False)
    scene.render.filepath = os.path.join(OUT, op + '.png'); bpy.ops.render.render(write_still=True); print('RESA', op, flush=True)


def componi():
    from PIL import Image, ImageDraw, ImageFont
    def tit(im, testo, xy, size=44, col=(255, 225, 60)):
        ImageDraw.Draw(im).text(xy, testo, font=ImageFont.truetype(FONT, size), fill=col, stroke_width=max(3, size // 11), stroke_fill=(20, 20, 30), anchor='mm')
    I = {k: Image.open(os.path.join(OUT, k + '.png')).convert('RGB') for k in OPZ if os.path.exists(os.path.join(OUT, k + '.png'))}
    q = 600
    rows = [(('H1', 'occhi sbarrati'), ('H2', 'occhi da meme'), ('H3', 'soffio coi denti')),
            (('O1', 'onda azzurra'), ('O2', 'onda da fumetto'), None)]
    im = Image.new('RGB', (3 * q + 40, len(rows) * (q + 100)), (20, 20, 30))
    for r_, row in enumerate(rows):
        y = 100 + r_ * (q + 100)
        for i, it in enumerate(row):
            if not it: continue
            k, d = it
            if k in I: im.paste(I[k].resize((q, q), Image.LANCZOS), (i * (q + 20), y)); tit(im, k + '  ' + d, (i * (q + 20) + q // 2, y - 50))
    im.save(os.path.join(SCHEDE, 'scelta026.jpg'), quality=90)
    print('SCHEDA FATTA', flush=True)


if __name__ == '__main__':
    a = sys.argv[-1]
    if a == 'componi': componi()
    else: scena(a)
