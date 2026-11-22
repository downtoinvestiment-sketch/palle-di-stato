"""Scheda di opzioni del video 028 «Il pomodoro da undici euro» (copione n. 27A):
dove si vende il pomodoro (M1 mercato, M2 gioielleria, M3 cassaforte), la banca del mutuo (B1 sportello, B2 direttore), il motorino di Gualtiero (S1 rosso, S2 azzurro, S3 giallo).
Uso:  python scheda028.py M1   (una opzione per processo), poi  python scheda028.py componi
Immagini in ../out/scheda028/, scheda finale in ../schede/scelta028.jpg"""
import sys, os, math
QUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, QUI)
OUT = os.path.join(QUI, '..', 'out', 'scheda028'); SCHEDE = os.path.join(QUI, '..', 'schede'); os.makedirs(OUT, exist_ok=True)
OPZ = ('M1', 'M2', 'M3', 'B1', 'B2', 'S1', 'S2', 'S3')
NOMI = dict(M1='M1  MERCATO', M2='M2  GIOIELLERIA', M3='M3  CASSAFORTE', B1='B1  SPORTELLO', B2='B2  DIRETTORE', S1='S1  ROSSO', S2='S2  AZZURRO', S3='S3  GIALLO')
RIGHE = (('1 · DOVE SI VENDE IL POMODORO', ('M1', 'M2', 'M3')), ('2 · LA BANCA DEL MUTUO', ('B1', 'B2')), ('3 · IL MOTORINO DI GUALTIERO', ('S1', 'S2', 'S3')))
PI = math.pi


def scena(op):
    import bpy
    from mathutils import Vector
    from common import reset_scene, collection, material, shape
    from render_setup import setup_render, world
    import set004, luci, kitlook, props028, pippo2 as pippo
    A = kitlook.A
    reset_scene(); set004._c.clear(); sc = bpy.context.scene; C = collection('C')
    W, H = (1350, 900) if op[0] == 'B' else (900, 900)
    setup_render(sc, W, H, samples=10, fps=24, frames=1); A.qualita_eevee(preset='equilibrato', riflessi=True, scena=sc, risoluzione=(W, H))
    M = props028.mats028(A); F = props028.font()
    cam = bpy.data.objects.new('Cam', bpy.data.cameras.new('Cam')); C.objects.link(cam); sc.camera = cam
    def aim(loc, tgt, lens): cam.location = loc; luci.punta(cam, Vector(tgt)); cam.data.lens = lens
    def tex(aid, dim, riserva):
        try: return A.materiale(aid, dimensione=dim)
        except Exception as e: print('texture mancante', aid, e); return riserva
    def pippo_a(p, rz, emo='sorpreso'):
        P = pippo.build_pippo(C); P['root'].location = p; P['root'].rotation_euler = (0, 0, rz); pippo.emozione(P, 1, emo); return P
    esterno = op[0] in ('S',) or op == 'M1'
    if esterno:
        world(sc, top=(0.30, 0.52, 0.95), bottom=(0.95, 0.86, 0.72), strength=1.0); luci.cielo_basso(sc.world, 0.4)
        props028.box('Suolo', (-30, -30, -0.1), (30, 30, 0), tex('PavingStones070', 2.0, material('suolo28', (0.6, 0.58, 0.55), rough=0.9)), C)
        props028.box('Muro', (-30, 3.2, 0), (30, 3.5, 9), tex('painted_plaster_wall', 3.0, material('muro28', (0.93, 0.78, 0.5), rough=0.9)), C)
    else:
        world(sc, top=(0.05, 0.06, 0.1), bottom=(0.1, 0.09, 0.08), strength=1.0); luci.cielo_basso(sc.world, 0.12)
    if op == 'M1':
        props028.bancarella(C, M, F); pippo_a((-2.75, -1.5, 0), -0.95, 'felice')
        aim((-2.2, -8.6, 2.6), (-0.45, 0, 1.55), 50); luci.sole(C, (-0.25, -1), lato=1, energia=3.2, angolo_alto=38)
    elif op in ('M2', 'M3'):
        props028.box('Pav', (-12, -12, -0.1), (12, 4, 0), material('pav28', (0.16, 0.15, 0.17), rough=0.3, coat=0.4), C)
        props028.box('Fondo', (-12, 2.6, 0), (12, 2.8, 8), material('fondo28', (0.10, 0.09, 0.14), rough=0.8), C)
        G = props028.gioielleria(C, M, F) if op == 'M2' else props028.cassaforte(C, M, F)
        pippo_a((-2.2, -0.9, 0), -1.1, 'felice'); aim((-1.6, -8.4, 2.3), (-0.55, 0, 1.3), 50)
        luci.cinema(C, (0, 0, 1.4), tuple(cam.location), distanza=5.0, forza=0.45, lato=1)
        ld = bpy.data.lights.new('Faretto', 'SPOT'); ld.energy = 520; ld.spot_size = 0.5; ld.spot_blend = 0.35; ld.color = (1.0, 0.9, 0.7); ld.shadow_soft_size = 0.05
        lo = bpy.data.objects.new('Faretto', ld); C.objects.link(lo); lo.location = (0.6, -2.2, 5.5); luci.punta(lo, G['centro'])
    elif op in ('B1', 'B2'):
        G = props028.sportello(C, M, F) if op == 'B1' else props028.scrivania(C, M, F)
        b, _ = props028.banchiere(C); b.location = G['banchiere'] + Vector((0.0, 0, 0.35 if op == 'B2' else 0.0))
        pippo_a(tuple(G['cliente'] + Vector((1.5, 0.2, 0))), 2.45, 'triste'); aim((-3.6, -8.2, 2.7), (0.2, 0, 1.75), 42)
        luci.cinema(C, (0, 0, 1.7), tuple(cam.location), distanza=6.0, forza=0.6, lato=1)
    else:
        col = dict(S1=(0.85, 0.07, 0.05), S2=(0.25, 0.68, 0.82), S3=(1.0, 0.76, 0.06))[op]
        R = props028.motorino(C, M, col); R['root'].rotation_euler = (0, 0, 0.9)
        aim((0.5, -4.3, 1.35), (0, 0, 0.66), 52); luci.sole(C, (0.1, -1), lato=1, energia=3.2, angolo_alto=38)
    sc.view_settings.exposure = -0.3 if esterno else 0.0
    luci.ombre_pulite(sc, mezza_risoluzione=False)
    sc.render.filepath = os.path.join(OUT, op + '.png'); bpy.ops.render.render(write_still=True); print('FATTO', op)


def componi():
    from PIL import Image, ImageDraw, ImageFont
    f1 = ImageFont.truetype(os.path.join(QUI, '..', 'assets', 'font', 'Bangers-Regular.ttf'), 56); f2 = ImageFont.truetype(os.path.join(QUI, '..', 'assets', 'font', 'Bangers-Regular.ttf'), 50)
    LW, TH, HH = 1800, 600, 84; im = Image.new('RGB', (LW, len(RIGHE) * (TH + HH)), (22, 22, 28)); d = ImageDraw.Draw(im); y = 0
    for titolo, ops in RIGHE:
        d.text((24, y + 12), titolo, fill=(255, 255, 255), font=f1); y += HH; w = LW // len(ops)
        for i, op in enumerate(ops):
            t = Image.open(os.path.join(OUT, op + '.png')).convert('RGB'); k = max(w / t.width, TH / t.height); t = t.resize((round(t.width * k), round(t.height * k)), Image.LANCZOS)
            x0 = (t.width - w) // 2; y0 = (t.height - TH) // 2; im.paste(t.crop((x0, y0, x0 + w, y0 + TH)), (i * w, y))
            d.rectangle((i * w, y, (i + 1) * w - 1, y + TH - 1), outline=(22, 22, 28), width=4)
            d.text((i * w + 22, y + 14), NOMI[op], fill=(255, 235, 60), font=f2, stroke_width=5, stroke_fill=(0, 0, 0))
        y += TH
    im.save(os.path.join(SCHEDE, 'scelta028.jpg'), quality=90); print('SCHEDA')


if __name__ == '__main__':
    a = sys.argv[1] if len(sys.argv) > 1 else 'componi'
    componi() if a == 'componi' else scena(a)
