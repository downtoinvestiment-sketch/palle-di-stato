"""Scheda di opzioni del video 022 «Il barattolo di cetriolini»: barattolo (B1 alto a quadretti, B2 tondo dorato),
cetriolino amante di Eleonora (C1 lungo, C2 tozzo coi baffi), elefante (E1 grigio, E2 rosa), razzo (R1 vero NASA, R2 cartoon).
Uso:  python scheda022.py B1   (una opzione per processo), poi  python scheda022.py componi
Immagini in ../out/scheda022/, schede finali in ../schede/scelta022_*.png"""
import sys, os, math
QUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, QUI)
import bpy
from mathutils import Vector
from common import *
from render_setup import *
import set004, props012, props022, eleonora, luci, kitlook
import pippo2
import tumbo
A = kitlook.A
OUT = os.path.join(QUI, '..', 'out', 'scheda022'); SCHEDE = os.path.join(QUI, '..', 'schede'); os.makedirs(OUT, exist_ok=True)
PI = math.pi
FONT = A.font('luckiest')
OPZ = ('B1', 'B2', 'C1', 'C2', 'E1', 'E2', 'R1', 'R2')


def scena(op):
    reset_scene(); set004._c.clear(); scene = bpy.context.scene
    C = collection('C')
    W, H = (720, 1280) if op[0] == 'R' else (900, 900)
    setup_render(scene, W, H, samples=8, fps=24, frames=1)
    A.qualita_eevee(preset='equilibrato', riflessi=op[0] in 'BC', scena=scene, risoluzione=(W, H)); scene.view_settings.exposure = 0.25
    A.cielo('sunflowers_puresky', forza=1.1, rotazione=43.0, ris='4k'); luci.cielo_basso(scene.world, 0.4)
    grass = A.materiale('Grass001', dimensione=3.0, rilievo=0.8, tinta=(1.05, 1.35, 0.7), ruvidita=1.5)
    g = set004.bx('Prato', (-60, -60, -0.3), (60, 60, 0.0), grass, C); A.niente_ombra(g)
    for k, (x, y, sp) in enumerate(((-14, 16, 'island_tree_01'), (12, 18, 'fir_tree_01'), (-5, 22, 'island_tree_02'))):
        try: A.albero_cartonato(sp, posizione=(x, y, 0), altezza=9 + k, collezione=C)
        except Exception as e: print('albero', e)
    M = props022.mats022(); Z12 = props012.mats012()
    cam = bpy.data.objects.new('Cam', bpy.data.cameras.new('Cam')); C.objects.link(cam); scene.camera = cam; cam.data.clip_start = 0.02
    def aim(loc, tgt, lens):
        cam.location = loc; luci.punta(cam, tgt); cam.data.lens = lens
    tavolo = set004.bx('Tavolo', (-0.5, -0.4, 0.0), (0.5, 0.4, 0.75), A.materiale('wood_table_worn', dimensione=1.0), C)
    if op[0] == 'B':
        J = props022.barattolo(C, M, op, H=0.9, font=FONT); J['root'].location = (0, 0, 0.75)
        P = pippo2.build_pippo(C); P['root'].location = (0.95, -0.35, 0); P['root'].rotation_euler = (0, 0, 0.9)
        pippo2.emozione(P, 1, 'arrabbiato')
        T = tumbo.build_tumbo(C, scale=0.75); T['root'].location = (-1.0, -0.6, 0); T['root'].rotation_euler = (0, 0, -0.6)
        aim((0.45, -2.7, 1.6), (0.25, 0, 1.25), 34)
        luci.sole(C, (0.45, -2.7), lato=1)
    elif op[0] == 'C':
        J = props022.barattolo(C, M, 'B1', H=0.9, font=FONT, pieno=False); J['root'].location = (0.1, 0.05, 0.75)
        J['lid'].location = (0.35, -0.15, -0.55); J['lid'].rotation_euler = (0.3, 0.2, 0)
        Ct = props022.cetriolino(C, M, op, H=0.62); Ct['root'].location = (0.1, 0.05, 0.75 + J['h'] - 0.3)
        Ct['shoulderR'].rotation_euler = (0, 2.6, 0); Ct['shoulderL'].rotation_euler = (0, -0.4, 0)
        Z = eleonora.zucchina(C, Z12); Z['root'].location = (-0.85, -0.2, 0.0); Z['root'].rotation_euler = (0, 0, -0.5)
        eleonora.velo(Z, False); eleonora.emozione(Z, 1, 'felice')
        P = pippo2.build_pippo(C); P['root'].location = (1.35, 0.1, 0); P['root'].rotation_euler = (0, 0, 1.3)
        pippo2.emozione(P, 1, 'sorpreso')
        aim((0.25, -2.4, 1.65), (0.1, 0, 1.45), 36)
        luci.sole(C, (0.25, -2.4), lato=1)
    elif op[0] == 'E':
        tavolo.hide_render = True
        J = props022.barattolo(C, M, 'B1', H=0.9, font=FONT); J['root'].location = (0, 0.9, 0)
        E = props022.elefante(C, M, op, H=3.6); E['root'].rotation_euler = (0, 0, 0.45)
        E['body'].rotation_euler = (-0.75, 0, 0)                                                 # seduto: la parte davanti in alto
        bpy.context.view_layer.update()
        rear = E['body'].matrix_world @ Vector((0, 1.6, -0.75))                                   # il sedere
        E['root'].location = (J['root'].location.x - rear.x, J['root'].location.y - rear.y, J['h'] + 0.12 - rear.z)
        for lg in E['legs'][:2]: lg.rotation_euler = (-0.35, 0, 0)                                 # zampe davanti per aria
        for lg in E['legs'][2:]: lg.rotation_euler = (0.45, 0, 0)                                  # zampe dietro in avanti
        for i, sg in enumerate(E['trunk']): sg.rotation_euler = (-0.45, 0, 0)                     # proboscide in su (trionfo)
        P = pippo2.build_pippo(C); P['root'].location = (2.2, -1.2, 0); P['root'].rotation_euler = (0, 0, 0.8)
        pippo2.emozione(P, 1, 'sorpreso')
        T = tumbo.build_tumbo(C, scale=0.75); T['root'].location = (3.0, -0.7, 0); T['root'].rotation_euler = (0, 0, 1.0)
        aim((1.8, -7.4, 2.0), (0.5, 0, 2.0), 30)
        luci.sole(C, (1.8, -7.4), lato=1)
    else:
        tavolo.hide_render = True
        if op == 'R1':
            Rt = A.modello('nasa/saturn-v', posizione=(0, 0, 0), altezza=11.0, collezione=C, max_triangoli=150000)
            top = (0, 0, 11.0)
        else:
            Rz = props022.razzo(C, M, H=7.0); top = tuple(Rz['top'].location)
        J = props022.barattolo(C, M, 'B1', H=1.3, font=FONT); J['root'].location = (top[0], top[1], top[2] + 0.02)
        props022.nastro(C, M, J['root'], J['R'], J['h'])
        P = pippo2.build_pippo(C); P['root'].location = (2.4, -2.4, 0); P['root'].rotation_euler = (0, 0, 0.6)
        pippo2.emozione(P, 1, 'furbo')
        T = tumbo.build_tumbo(C, scale=0.75); T['root'].location = (3.3, -2.0, 0); T['root'].rotation_euler = (0, 0, 0.9)
        aim((2.6, -14.5, 1.6), (0.6, 0, 5.8), 24)
        luci.sole(C, (2.6, -13.5), lato=1)
    luci.ombre_pulite(scene, mezza_risoluzione=False)
    kitlook.tune_cutouts(1.9)
    scene.render.filepath = os.path.join(OUT, op + '.png'); bpy.ops.render.render(write_still=True); print('RESA', op, flush=True)


def componi():
    from PIL import Image, ImageDraw, ImageFont
    def tit(im, testo, xy, size=56, col=(255, 225, 60)):
        ImageDraw.Draw(im).text(xy, testo, font=ImageFont.truetype(FONT, size), fill=col, stroke_width=max(3, size // 11), stroke_fill=(20, 20, 30), anchor='mm')
    I = {k: Image.open(os.path.join(OUT, k + '.png')).convert('RGB') for k in OPZ if os.path.exists(os.path.join(OUT, k + '.png'))}
    rows = [(('B1', 'barattolo alto'), ('B2', 'barattolo tondo')), (('C1', 'cetriolino lungo'), ('C2', 'cetriolino coi baffi')), (('E1', 'elefante grigio'), ('E2', 'elefante rosa'))]
    im = Image.new('RGB', (2 * 900 + 20, 3 * (900 + 120)), (20, 20, 30))
    for r_, pair in enumerate(rows):
        y = 120 + r_ * (900 + 120)
        for i, (k, d) in enumerate(pair):
            if k in I: im.paste(I[k], (i * 920, y)); tit(im, k + '  ' + d, (i * 920 + 450, y - 60))
    im.save(os.path.join(SCHEDE, 'scelta022_oggetti.png'))
    w = 720; im = Image.new('RGB', (2 * w + 20, 1280 + 120), (20, 20, 30))
    for i, (k, d) in enumerate((('R1', 'razzo vero'), ('R2', 'razzo cartoon'))):
        if k in I: im.paste(I[k], (i * (w + 20), 120)); tit(im, k + '  ' + d, (i * (w + 20) + w // 2, 60))
    im.save(os.path.join(SCHEDE, 'scelta022_razzo.png'))
    print('SCHEDE FATTE', flush=True)


if __name__ == '__main__':
    a = sys.argv[-1]
    if a == 'componi': componi()
    else: scena(a)
