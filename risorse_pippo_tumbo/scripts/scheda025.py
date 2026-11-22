"""Scheda di opzioni del video 025 «Martina nel water»: Martina lo scarafaggio (B1 cartoon lucida, B2 quasi vera, B3 paffuta),
il bagno di Pippo (W1 piastrelle bianche, W2 bagno della nonna), la ciabatta di Tumbo (C1 pantofola a quadri, C2 ciabatta da piscina).
Uso:  python scheda025.py B1   (una opzione per processo), poi  python scheda025.py componi
Immagini in ../out/scheda025/, scheda finale in ../schede/scelta025.jpg"""
import sys, os, math
QUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, QUI)
import bpy
from mathutils import Vector
from common import *
from render_setup import *
import set004, props024, props025, luci, kitlook
import pippo2
import tumbo
A = kitlook.A
OUT = os.path.join(QUI, '..', 'out', 'scheda025'); SCHEDE = os.path.join(QUI, '..', 'schede'); os.makedirs(OUT, exist_ok=True); os.makedirs(SCHEDE, exist_ok=True)
PI = math.pi
FONT = A.font('luckiest')
OPZ = ('B1', 'B2', 'B3', 'W1', 'W2', 'C1', 'C2')


def guarda(o, x, y):
    dx, dy = x - o.location.x, y - o.location.y; o.rotation_euler = (0, 0, math.atan2(dx, -dy))


def scena(op):
    reset_scene(); set004._c.clear(); scene = bpy.context.scene
    C = collection('C')
    setup_render(scene, 900, 900, samples=8, fps=24, frames=1)
    A.qualita_eevee(preset='equilibrato', riflessi=True, scena=scene, risoluzione=(900, 900)); scene.view_settings.exposure = 0.2
    w = bpy.data.worlds.new('W'); scene.world = w; w.use_nodes = True
    bg = next(n for n in w.node_tree.nodes if n.type == 'BACKGROUND'); bg.inputs['Color'].default_value = (0.75, 0.8, 0.9, 1); bg.inputs['Strength'].default_value = 0.35
    cam = bpy.data.objects.new('Cam', bpy.data.cameras.new('Cam')); C.objects.link(cam); scene.camera = cam; cam.data.clip_start = 0.005
    def aim(loc, tgt, lens):
        cam.location = loc; luci.punta(cam, tgt); cam.data.lens = lens
    font = bpy.data.fonts.load(FONT)
    M = props025.mats025()
    tipo_bagno = op if op[0] == 'W' else 'W1'
    BG = props025.bagno(C, M, A, tipo_bagno, font=font)
    P = pippo2.build_pippo(C); T = tumbo.build_tumbo(C, scale=0.75)
    if op[0] == 'B':                                                   # Martina in primo piano sul pavimento, Pippo e Tumbo dietro
        Mt = props025.scarafaggio(C, M, op, L=0.36); Mt['root'].location = (0.1, -1.25, 0.0); Mt['root'].rotation_euler = (0, 0, 0.45)
        props025.occhiali(C, M, Mt['testa'], (0, -0.02, 0.07), 0.36)
        P['root'].location = (0.75, 0.6, 0); guarda(P['root'], 0.1, -1.25); pippo2.emozione(P, 1, 'arrabbiato')
        T['root'].location = (-0.8, 0.1, 0); guarda(T['root'], 0.1, -1.25); tumbo.tumbo_express(T, 1, tongue=0.5)
        aim((-0.05, -2.15, 0.42), (0.15, -0.9, 0.42), 34)
        cam.data.dof.use_dof = True; cam.data.dof.focus_distance = 1.0; cam.data.dof.aperture_fstop = 4.0
        luci.cinema(C, (0.1, -1.25, 0.2), (-0.05, -2.15, 0.42), distanza=1.6, lato=-1, forza=0.6)
    elif op[0] == 'W':                                                 # il bagno: Pippo chino sul water, Martina nella tazza
        Mt = props025.scarafaggio(C, M, 'B1', L=0.16); wq = BG['water']
        Mt['root'].location = (0, 1.23, wq['quota'] + 0.02); Mt['root'].rotation_euler = (PI, 0, 0.4)
        P['root'].location = (0.15, 0.45, 0); guarda(P['root'], 0, 1.25); P['root'].rotation_euler[0] = 0.45; pippo2.emozione(P, 1, 'sorpreso')
        T['root'].location = (-0.95, 0.2, 0); guarda(T['root'], 0, 1.2)
        P['root'].location = (-0.05, 0.62, 0); guarda(P['root'], 0, 1.25); P['root'].rotation_euler[0] = 0.5
        aim((1.85, -0.9, 1.55), (-0.1, 0.95, 0.85), 24)
        luci.cinema(C, (0.0, 1.0, 1.0), (1.85, -0.9, 1.55), distanza=2.6, lato=-1, forza=0.7)
    else:                                                              # la ciabatta davanti a Tumbo
        Cb = props025.ciabatta(C, M, op, L=0.42); Cb.location = (0.1, -0.85, 0.0); Cb.rotation_euler = (0, 0, 0.6)
        T['root'].location = (-0.45, -0.55, 0); guarda(T['root'], 0.1, -0.85); tumbo.tumbo_express(T, 1, tongue=0.8)
        P['root'].location = (0.8, 0.3, 0); guarda(P['root'], 0.1, -0.85); pippo2.emozione(P, 1, 'furbo')
        aim((0.25, -1.95, 0.6), (0.0, -0.6, 0.4), 32)
        luci.cinema(C, (0.1, -0.85, 0.3), (0.25, -1.95, 0.6), distanza=1.8, lato=-1, forza=0.7)
    L_ = bpy.data.lights.new('Plafoniera', 'AREA'); lo = bpy.data.objects.new('Plafoniera', L_); C.objects.link(lo); lo.location = (0, 0, 3.5); L_.energy = 260; L_.size = 1.6
    luci.ombre_pulite(scene, mezza_risoluzione=False)
    scene.render.filepath = os.path.join(OUT, op + '.png'); bpy.ops.render.render(write_still=True); print('RESA', op, flush=True)


def componi():
    from PIL import Image, ImageDraw, ImageFont
    def tit(im, testo, xy, size=44, col=(255, 225, 60)):
        ImageDraw.Draw(im).text(xy, testo, font=ImageFont.truetype(FONT, size), fill=col, stroke_width=max(3, size // 11), stroke_fill=(20, 20, 30), anchor='mm')
    I = {k: Image.open(os.path.join(OUT, k + '.png')).convert('RGB') for k in OPZ if os.path.exists(os.path.join(OUT, k + '.png'))}
    q = 600
    rows = [(('B1', 'Martina cartoon'), ('B2', 'Martina quasi vera'), ('B3', 'Martina paffuta')),
            (('W1', 'bagno bianco'), ('W2', 'bagno della nonna'), None),
            (('C1', 'pantofola a quadri'), ('C2', 'ciabatta da piscina'), None)]
    im = Image.new('RGB', (3 * q + 40, len(rows) * (q + 100)), (20, 20, 30))
    for r_, row in enumerate(rows):
        y = 100 + r_ * (q + 100)
        for i, it in enumerate(row):
            if not it: continue
            k, d = it
            if k in I: im.paste(I[k].resize((q, q), Image.LANCZOS), (i * (q + 20), y)); tit(im, k + '  ' + d, (i * (q + 20) + q // 2, y - 50))
    im.save(os.path.join(SCHEDE, 'scelta025.jpg'), quality=90)
    print('SCHEDA FATTA', flush=True)


if __name__ == '__main__':
    a = sys.argv[-1]
    if a == 'componi': componi()
    else: scena(a)
