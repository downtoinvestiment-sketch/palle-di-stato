"""Scheda di opzioni del video 031 «Il Nobel per la pace» (copione n. 33 v3):
la bomba (B1 nera tonda con la miccia, B2 bomba d'aereo), l'ufficio di Cappellone (U1 elegante, U2 bunker con la mappa), il forno della pizza (F1 mattoni, F2 metallo).
Uso:  python scheda031.py B1   (una opzione per processo), poi  python scheda031.py componi
Immagini in ../out/scheda031/, scheda finale in ../schede/scelta031.jpg"""
import sys, os, math
QUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, QUI)
OUT = os.path.join(QUI, '..', 'out', 'scheda031'); SCHEDE = os.path.join(QUI, '..', 'schede'); os.makedirs(OUT, exist_ok=True)
OPZ = ('B1', 'B2', 'U1', 'U2', 'F1', 'F2')
NOMI = dict(B1='B1  TONDA CON MICCIA', B2="B2  BOMBA D'AEREO", U1='U1  UFFICIO ELEGANTE', U2='U2  BUNKER CON MAPPA', F1='F1  FORNO DI MATTONI', F2='F2  FORNO DI FERRO')
RIGHE = (('1 · LE BOMBE (A MEZZ\'ARIA DIVENTANO CORIANDOLI)', ('B1', 'B2')), ('2 · L\'UFFICIO DI CAPPELLONE', ('U1', 'U2')), ('3 · IL FORNO DELLA PIZZA', ('F1', 'F2')))
PI = math.pi


def scena(op):
    import bpy
    from mathutils import Vector
    from common import reset_scene, collection
    from render_setup import setup_render, world
    import set004, luci, kitlook, props031 as P, pippo2 as pippo, cappellone as cp, tumbo
    A = kitlook.A
    reset_scene(); set004._c.clear(); sc = bpy.context.scene; C = collection('C')
    W, H = 900, 900
    setup_render(sc, W, H, samples=10, fps=24, frames=1); A.qualita_eevee(preset='equilibrato', riflessi=True, scena=sc, risoluzione=(W, H))
    M = P.mats031()
    cam = bpy.data.objects.new('Cam', bpy.data.cameras.new('Cam')); C.objects.link(cam); sc.camera = cam; cam.data.clip_end = 600
    def aim(loc, tgt, lens): cam.location = loc; luci.punta(cam, Vector(tgt)); cam.data.lens = lens
    if op[0] == 'B':
        world(sc, top=(0.16, 0.40, 0.95), bottom=(1.0, 0.80, 0.55), strength=1.0); luci.cielo_basso(sc.world, 0.45)
        P.mare(C, raggio=120)
        for k, (x, z, rz, rx) in enumerate(((-1.6, 6.0, 0.4, -0.9), (1.4, 7.4, -0.5, -1.1), (0.2, 4.6, 0.1, -0.7))):
            R = P.bomba(C, M, op, 'Bomba%d' % k); R['root'].location = (x, 4 + k, z); R['root'].rotation_euler = (rx if op == 'B2' else 0.3, 0.2 * k, rz)
        cor = P.coriandoli(C, 90)
        import random; rnd = random.Random(5)
        for o, a, b, c, d in cor:
            o.location = (rnd.uniform(-4, 4), rnd.uniform(2, 9), rnd.uniform(1.5, 9)); o.rotation_euler = (a, b * 3, c)
        aim((0.0, -11.0, 3.5), (0.0, 4.5, 5.4), 38); luci.sole(C, (-0.2, -1), lato=1, energia=3.4, angolo_alto=36)
    elif op[0] == 'U':
        world(sc, top=(0.1, 0.1, 0.12), bottom=(0.1, 0.1, 0.12), strength=0.3)
        U = P.ufficio(C, M, A, op)
        Cc = cp.cappellone(C); Cc['root'].location = (0, 1.6, 0); Cc['root'].rotation_euler = (0, 0, 0); cp.emozione(Cc, None, 'manifesto'); cp.gesto(Cc, None, 'dito puntato'); cp.cappello(Cc, None, 'niente')
        B = P.bottone(C, M); B['root'].location = U['bottone_pos']
        aim((1.6, -3.6, 2.2), (0.0, 1.2, 1.5), 28)
        luci.cinema(C, (0.0, 1.6, 1.8), tuple(cam.location), distanza=4.0, lato=1); luci.cielo_basso(sc.world, 0.1)
    else:
        world(sc, top=(0.16, 0.40, 0.95), bottom=(1.0, 0.80, 0.55), strength=1.0); luci.cielo_basso(sc.world, 0.45)
        import props029 as P9; P9.deserto(C, A, piatto=True) if 'piatto' in P9.deserto.__code__.co_varnames else P9.deserto(C, A)
        F = P.forno(C, M, A, op); F['root'].location = (0.6, 1.5, 0); F['root'].rotation_euler = (0, 0, 0.25)
        Pp = pippo.build_pippo(C); Pp['root'].location = (-1.6, -0.6, 0); Pp['root'].rotation_euler = (0, 0, -0.5); pippo.emozione(Pp, 1, 'felice')
        from pippo import HEAD_C, HR; P.cappello_cuoco(C, M, Pp['head'], (0, 0, HEAD_C + HR[2] * 0.8), 2.2)
        T = tumbo.build_tumbo(C, scale=0.75); T['root'].location = (-0.2, -1.6, 0); T['root'].rotation_euler = (0, 0, -0.3)
        pz = P.pizza(C, M, raggio=0.45); pz.location = (-0.75, -1.25, 1.25); pz.rotation_euler = (0.25, 0, 0)
        aim((-0.8, -9.5, 2.6), (-0.2, 0.0, 1.5), 36); luci.sole(C, (-0.2, -1), lato=1, energia=3.4, angolo_alto=36)
    sc.view_settings.exposure = -0.15
    luci.ombre_pulite(sc, mezza_risoluzione=False)
    sc.render.filepath = os.path.join(OUT, op + '.png'); bpy.ops.render.render(write_still=True); print('RESA', op, flush=True)


def componi():
    from PIL import Image, ImageDraw, ImageFont
    import glob
    FONT = (glob.glob(os.path.join(QUI, '..', 'assets', 'font', 'Luckiest*')) + glob.glob(os.path.join(QUI, '..', 'assets', 'font', '*.ttf')))[0]
    def t(d, s, xy, size, col=(255, 225, 60), anchor='mm'):
        d.text(xy, s, font=ImageFont.truetype(FONT, size), fill=col, stroke_width=max(3, size // 11), stroke_fill=(20, 20, 30), anchor=anchor)
    w = 700; gap = 16; head = 70; lab = 54
    righe = []
    for titolo, ops in RIGHE:
        ims = []
        for o in ops:
            p = os.path.join(OUT, o + '.png'); im = Image.open(p).convert('RGB') if os.path.exists(p) else Image.new('RGB', (900, 900), (40, 40, 40))
            ims.append(im.resize((w, int(im.height * w / im.width))))
        righe.append((titolo, ops, ims))
    W = 2 * w + 3 * gap; H = sum(head + lab + max(i.height for i in ims) + gap for _, _, ims in righe)
    S = Image.new('RGB', (W, H), (22, 22, 32)); d = ImageDraw.Draw(S); y = 0
    for titolo, ops, ims in righe:
        t(d, titolo, (gap, y + head // 2), 36, (255, 255, 255), 'lm'); y += head
        for k, (o, im) in enumerate(zip(ops, ims)):
            x = gap + k * (w + gap); t(d, NOMI[o], (x + w // 2, y + lab // 2), 34); S.paste(im, (x, y + lab))
        y += lab + max(i.height for i in ims) + gap
    S.save(os.path.join(SCHEDE, 'scelta031.jpg'), quality=88); print('SCHEDA FATTA', flush=True)


if __name__ == '__main__':
    a = sys.argv[-1]
    componi() if a == 'componi' else scena(a)
