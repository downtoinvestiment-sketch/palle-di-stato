"""Scheda di opzioni del video 029 «La guerra per il petrolio» (copione n. 29C v5):
il T-rex (T1 verde, T2 marrone, T3 viola con le punte), il pozzo (P1 pompa a cavallo, P2 torre di trivellazione), il distributore (D1 anni '50, D2 moderno).
Uso:  python scheda029.py T1   (una opzione per processo), poi  python scheda029.py componi
Immagini in ../out/scheda029/, scheda finale in ../schede/scelta029.jpg"""
import sys, os, math
QUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, QUI)
OUT = os.path.join(QUI, '..', 'out', 'scheda029'); SCHEDE = os.path.join(QUI, '..', 'schede'); os.makedirs(OUT, exist_ok=True)
OPZ = ('T1', 'T2', 'T3', 'P1', 'P2', 'D1', 'D2')
NOMI = dict(T1='T1  VERDE', T2='T2  MARRONE', T3='T3  VIOLA', P1='P1  POMPA A CAVALLO', P2='P2  TORRE', D1="D1  ANNI '50", D2='D2  MODERNO')
RIGHE = (('1 · IL T-REX', ('T1', 'T2', 'T3')), ('2 · IL POZZO DI PETROLIO', ('P1', 'P2')), ('3 · IL DISTRIBUTORE (IL BENZINAIO E\' IL T-REX)', ('D1', 'D2')))
PI = math.pi


def scena(op):
    import bpy
    from mathutils import Vector
    from common import reset_scene, collection
    from render_setup import setup_render, world
    import set004, luci, kitlook, props029 as P9, pippo2 as pippo, cappellone as cp
    A = kitlook.A
    reset_scene(); set004._c.clear(); sc = bpy.context.scene; C = collection('C')
    W, H = 900, 900
    setup_render(sc, W, H, samples=10, fps=24, frames=1); A.qualita_eevee(preset='equilibrato', riflessi=True, scena=sc, risoluzione=(W, H))
    M = P9.mats029()
    cam = bpy.data.objects.new('Cam', bpy.data.cameras.new('Cam')); C.objects.link(cam); sc.camera = cam; cam.data.clip_end = 600
    def aim(loc, tgt, lens): cam.location = loc; luci.punta(cam, Vector(tgt)); cam.data.lens = lens
    world(sc, top=(0.16, 0.40, 0.95), bottom=(1.0, 0.80, 0.55), strength=1.0); luci.cielo_basso(sc.world, 0.45)
    P9.deserto(C, A)
    def pippo_a(p, rz, emo='sorpreso'):
        P = pippo.build_pippo(C); P['root'].location = p; P['root'].rotation_euler = (0, 0, rz); pippo.emozione(P, 1, emo); return P
    if op[0] == 'T':
        R = P9.trex(C, M, op); R['root'].rotation_euler = (0, 0, -0.45)
        P9.trex_pose(R, 1, jaw=0.75, testa=(0.15, 0, 0.1), collo=-0.1, coda=1.0, braccia=0.8, look=(0.4, -0.3), brow=0.6)
        pippo_a((-4.0, -3.0, 0), -0.6, 'spaventato')
        aim((-4.0, -17.5, 3.6), (-1.2, 0, 4.0), 45); luci.sole(C, (-0.1, -1), lato=1, energia=3.4, angolo_alto=36)
    elif op[0] == 'P':
        R = P9.pompa(C, M) if op == 'P1' else P9.torre(C, M); R['root'].rotation_euler = (0, 0, -0.5 if op == 'P1' else 0.35)
        if op == 'P1': R['beam'].rotation_euler = (0.18, 0, 0)
        Cc = cp.cappellone(C); Cc['root'].location = (-4.2, -3.5, 0); Cc['root'].rotation_euler = (0, 0, -0.4); cp.emozione(Cc, None, 'manifesto'); cp.gesto(Cc, None, 'dito puntato')
        if op == 'P1': aim((-2.8, -15.0, 3.0), (-1.0, 0, 3.0), 45)
        else: aim((-3.5, -28.0, 6.5), (-0.8, 0, 8.0), 42)
        luci.sole(C, (-0.1, -1), lato=1, energia=3.4, angolo_alto=36)
    else:
        D = P9.distributore(C, M, op)
        R = P9.trex(C, M, 'T1'); R['root'].location = (0.0, 6.5, 0) if op == 'D1' else (0.0, 4.6, 0); R['root'].rotation_euler = (0, 0, 0.15)
        P9.berretto(R, 1, True); P9.trex_pose(R, 1, jaw=0.5, testa=(0.2, 0, 0), collo=0.2, braccia=0.3, look=(0, -0.4), brow=-0.3)
        pippo_a((-2.6, -2.6, 0), -0.4, 'spaventato')
        aim((-3.8, -15.5, 3.3), (0.0, 1.5, 3.6), 42); luci.sole(C, (-0.2, -1), lato=1, energia=3.4, angolo_alto=36)
    sc.view_settings.exposure = -0.15
    luci.ombre_pulite(sc, mezza_risoluzione=False)
    sc.render.filepath = os.path.join(OUT, op + '.png'); bpy.ops.render.render(write_still=True); print('RESA', op, flush=True)


def componi():
    from PIL import Image, ImageDraw, ImageFont
    FONT = os.path.join(QUI, '..', 'assets', 'font', 'LuckiestGuy-Regular.ttf')
    if not os.path.exists(FONT):
        import glob; FONT = (glob.glob(os.path.join(QUI, '..', 'assets', 'font', 'Luckiest*')) + glob.glob(os.path.join(QUI, '..', 'assets', 'font', '*.ttf')))[0]
    def t(d, s, xy, size, col=(255, 225, 60), anchor='mm'):
        d.text(xy, s, font=ImageFont.truetype(FONT, size), fill=col, stroke_width=max(3, size // 11), stroke_fill=(20, 20, 30), anchor=anchor)
    w = 600; gap = 16; head = 70; lab = 54
    righe = []
    for titolo, ops in RIGHE:
        ims = []
        for o in ops:
            p = os.path.join(OUT, o + '.png'); im = Image.open(p).convert('RGB') if os.path.exists(p) else Image.new('RGB', (900, 900), (40, 40, 40))
            ims.append(im.resize((w, int(im.height * w / im.width))))
        righe.append((titolo, ops, ims))
    W = 3 * w + 4 * gap; H = sum(head + lab + max(i.height for i in ims) + gap for _, _, ims in righe)
    S = Image.new('RGB', (W, H), (22, 22, 32)); d = ImageDraw.Draw(S); y = 0
    for titolo, ops, ims in righe:
        t(d, titolo, (gap, y + head // 2), 40, (255, 255, 255), 'lm'); y += head
        for k, (o, im) in enumerate(zip(ops, ims)):
            x = gap + k * (w + gap); t(d, NOMI[o], (x + w // 2, y + lab // 2), 34); S.paste(im, (x, y + lab))
        y += lab + max(i.height for i in ims) + gap
    S.save(os.path.join(SCHEDE, 'scelta029.jpg'), quality=88); print('SCHEDA FATTA', flush=True)


if __name__ == '__main__':
    a = sys.argv[-1]
    componi() if a == 'componi' else scena(a)
