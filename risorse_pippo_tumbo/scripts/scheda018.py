"""Scheda di opzioni del video 018 «La mente»: base (S militare, T fantascienza), squalo (U simpatico, V cattivo),
cabina dentro la testa (W vintage, X astronave). Pippo e Tumbo accanto per la scala.
Uso:  python scheda018.py S   (una opzione per processo: S T U V W X), poi  python scheda018.py componi
Immagini in ../out/scheda018/, scheda finale in ../schede/scelta018.png"""
import sys, os, math
QUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, QUI)
import bpy
from mathutils import Vector
from common import *
from render_setup import *
import set004, props009, props018, giulia, luci, kitlook
import pippo2 as pippo
import tumbo
A = kitlook.A
OUT = os.path.join(QUI, '..', 'out', 'scheda018'); SCHEDE = os.path.join(QUI, '..', 'schede'); os.makedirs(OUT, exist_ok=True)
PI = math.pi
FONT = A.font('luckiest')


def scena(op):
    reset_scene(); set004._c.clear(); scene = bpy.context.scene
    C = collection('C')
    W, H = (720, 1280) if op in 'STYZ' else (900, 900)
    setup_render(scene, W, H, samples=8, fps=24, frames=1)
    A.qualita_eevee(preset='equilibrato', riflessi=op in 'UV', scena=scene, risoluzione=(W, H)); scene.view_settings.exposure = 0.25
    A.cielo('sunflowers_puresky', forza=1.1, rotazione=43.0, ris='4k')
    luci.cielo_basso(scene.world, 0.4)
    grass = A.materiale('Grass001', dimensione=3.0, rilievo=0.8, tinta=(1.05, 1.35, 0.7), ruvidita=1.5)
    g = set004.bx('Prato', (-60, -60, -0.3), (60, 60, 0.0), grass, C); A.niente_ombra(g)
    M = props018.mats018(); G9 = props009.mats009(); GM = giulia.mats_giulia()
    cam = bpy.data.objects.new('Cam', bpy.data.cameras.new('Cam')); C.objects.link(cam); scene.camera = cam; cam.data.clip_start = 0.02
    def aim(loc, tgt, lens):
        cam.location = loc; luci.punta(cam, tgt); cam.data.lens = lens
    if op in 'ST':
        B = props018.base(C, M, op, (0, 0), font=FONT)
        cs = props018.cassetta(C, M); cs['root'].location = (0, 0, 0)
        gz = props018.giornale(C, M, font=FONT); gz.location = (0, -0.1, 1.42); gz.rotation_euler = (0.2, 0, 0.3)
        P = pippo.build_pippo(C); P['root'].location = (1.5, -1.6, 0); P['root'].rotation_euler = (0, 0, -0.5)
        T = tumbo.build_tumbo(C, scale=0.75); T['root'].location = (2.2, -2.2, 0); T['root'].rotation_euler = (0, 0, -0.7)
        sq = props018.squalo(C, M, 'U', 1.0); sq['root'].location = (-5.9, -2.0, 0.0); sq['root'].rotation_euler = (0, 0, -0.35)
        aim((-15.5, -9.0, 8.8), (-0.8, 0.2, 1.2), 30)
        luci.sole(C, (-15.5, -9.0), lato=-1)
    elif op in 'UV':
        props018.anello(C, 'Acqua', 0, 3.4, 0.0, 0.035, M['water'])
        props018.anello(C, 'Bordo', 3.4, 3.8, 0.0, 0.14, M['curb'])
        sq = props018.squalo(C, M, op, 1.0); sq['root'].location = (0.3, 0.6, 0.22); sq['root'].rotation_euler = (0, 0, 0.55); sq['body'].rotation_euler = (-0.22, 0, 0)
        sq['jaw'].rotation_euler = (0.6, 0, 0)
        P = pippo.build_pippo(C); P['root'].location = (2.6, 3.4, 0.0); P['root'].rotation_euler = (0, 0, 2.4)
        T = tumbo.build_tumbo(C, scale=0.75); T['root'].location = (3.6, 2.6, 0); T['root'].rotation_euler = (0, 0, 2.2)
        aim((3.6, -4.4, 1.9), (1.0, 0.9, 0.6), 36)
        luci.sole(C, (4.2, -5.6), lato=1)
    elif op in 'YZ':
        B = props018.base(C, M, 'S', (0, 0), font=FONT)
        cs = props018.cassetta(C, M)
        # squalo di traverso nel fossato (lato ovest-sud-ovest, punta verso il centro), Gualtiero in piedi sopra come su un surf
        a = PI + 0.45; rm = 6.0; sp = Vector((rm * math.cos(a), rm * math.sin(a))); hd = Vector((-math.cos(a), -math.sin(a)))
        rz = math.atan2(-hd.x, hd.y) + PI if False else math.atan2(hd.x, -hd.y)
        sq = props018.squalo(C, M, op, 1.2); sq['root'].location = (sp.x, sp.y, 0.2); sq['root'].rotation_euler = (0, 0, rz)
        sq['jaw'].rotation_euler = (0.55, 0, 0); sq['body'].rotation_euler = (-0.1, 0, 0)
        G = props009.gualtiero(C, G9); G['root'].location = (sp.x - hd.x * 0.45, sp.y - hd.y * 0.45, 0.6); G['root'].rotation_euler = (0, 0, rz - 1.25)
        for nm in ('shoulderL', 'shoulderR'): G[nm].rotation_euler = (0, (-1 if nm[-1] == 'L' else 1) * 1.2, 0)
        G['hipL'].rotation_euler = (0.3, 0, 0); G['hipR'].rotation_euler = (-0.3, 0, 0)
        props009.gex(G, None, brow=-0.1, mouth=0.0)
        gz = props018.giornale(C, M, font=FONT); gz.parent = G['shoulderR']; gz.location = (0, -0.1, -0.78); gz.rotation_euler = (0, PI / 2, PI)
        pp = Vector((hd.y, -hd.x))                                        # di lato rispetto alla direzione dello squalo
        P = pippo.build_pippo(C); P['root'].location = tuple(sp - pp * 3.3 + hd * 0.6) + (0,); P['root'].rotation_euler = (0, 0, rz + PI / 2)
        T = tumbo.build_tumbo(C, scale=0.75); T['root'].location = tuple(sp - pp * 3.4 + hd * 1.5) + (0,); T['root'].rotation_euler = (0, 0, rz + PI / 2)
        cp = sp + pp * 7.5 + hd * 0.8
        aim((cp.x, cp.y, 2.2), (sp.x - pp.x * 0.5, sp.y - pp.y * 0.5, 0.9), 34)
        luci.sole(C, (cp.x - sp.x, cp.y - sp.y), lato=1)
    else:
        G = props009.gualtiero(C, G9); G['root'].location = (0, 0, 0)
        props009.gex(G, None, brow=-0.2, mouth=0.05)
        crn = [o for o in G['head'].children if o.name.startswith('G_Cranio')][0]
        K = props018.cranio(C, M, GM, G['head'], crn, (0.30, 0.28, 0.31), 0.17, G9['gskin'], op, figli_coperchio=[G['browL'], G['browR']])
        K['hinge'].rotation_euler = (-1.95, 0, 0)
        giulia.giex(K['J'], None, brow=0.6, mouth=0.35, lid=0.25, look=(0.6, 0.6), naso=0.4)
        aim((0.3, -0.85, 2.5), (0, 0.0, 1.84), 55)
        luci.sole(C, (0.55, -0.95), lato=1)
    if op in 'WX':
        L = luci.cinema(C, (0, 0, 1.8), tuple(cam.location), distanza=2.5, lato=1)
    else:
        luci.ombre_pulite(scene, mezza_risoluzione=False)
    kitlook.tune_cutouts(1.9)
    scene.render.filepath = os.path.join(OUT, op + '.png'); bpy.ops.render.render(write_still=True); print('RESA', op, flush=True)


def componi():
    from PIL import Image, ImageDraw, ImageFont
    F = FONT
    def tit(im, testo, xy, size=64, col=(255, 225, 60)):
        ImageDraw.Draw(im).text(xy, testo, font=ImageFont.truetype(F, size), fill=col, stroke_width=max(3, size // 11), stroke_fill=(20, 20, 30), anchor='mm')
    I = {k: Image.open(os.path.join(OUT, k + '.png')).convert('RGB') for k in 'STUVWX'}
    # base: due verticali affiancate
    w = 720; im = Image.new('RGB', (2 * w + 20, 1280 + 120), (20, 20, 30))
    for i, (k, d) in enumerate((('S', 'militare'), ('T', 'fantascienza'))):
        im.paste(I[k], (i * (w + 20), 120)); tit(im, k + '  ' + d, (i * (w + 20) + w // 2, 60), 64)
    im.save(os.path.join(SCHEDE, 'scelta018_base.png'))
    im = Image.new('RGB', (2 * 900 + 20, 2 * 900 + 20 + 240), (20, 20, 30))
    if all(os.path.exists(os.path.join(OUT, k + '.png')) for k in 'YZ'):
        w = 720; im2 = Image.new('RGB', (2 * w + 20, 1280 + 120), (20, 20, 30))
        for i, (k, d) in enumerate((('Y', 'squalo simpatico'), ('Z', 'squalo cattivo'))):
            im2.paste(Image.open(os.path.join(OUT, k + '.png')).convert('RGB'), (i * (w + 20), 120)); tit(im2, k + '  ' + d, (i * (w + 20) + w // 2, 60), 64)
        im2.save(os.path.join(SCHEDE, 'scelta018_squalo2.png'))
    rows = [(('U', 'squalo simpatico'), ('V', 'squalo cattivo')), (('W', 'cabina vintage'), ('X', 'cabina astronave'))]
    for r_, pair in enumerate(rows):
        y = 120 + r_ * (900 + 120)
        for i, (k, d) in enumerate(pair):
            im.paste(I[k], (i * 920, y)); tit(im, k + '  ' + d, (i * 920 + 450, y - 60), 60)
    im.save(os.path.join(SCHEDE, 'scelta018_squalo_cabina.png'))
    print('SCHEDE FATTE', flush=True)


if __name__ == '__main__':
    a = sys.argv[-1]
    if a == 'componi': componi()
    else: scena(a)
