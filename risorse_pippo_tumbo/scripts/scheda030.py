"""Scheda di opzioni del video 030 «Rospina o Castora?» (copione n. 32 v3):
il monopattino del bonus (S1 classico rosso, S2 elettrico nero, S3 elettrico giallo), la diga della Castora (D1 tronchi, D2 cemento), il canotto (K1 giallo, K2 arancione, K3 papera).
Uso:  python scheda030.py S1   (una opzione per processo), poi  python scheda030.py componi  ->  ../schede/scelta030.jpg"""
import sys, os, math
QUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, QUI)
OUT = os.path.join(QUI, '..', 'out', 'scheda030'); SCHEDE = os.path.join(QUI, '..', 'schede'); os.makedirs(OUT, exist_ok=True)
NOMI = dict(S1='S1  CLASSICO', S2='S2  ELETTRICO NERO', S3='S3  ELETTRICO GIALLO', D1='D1  TRONCHI', D2='D2  CEMENTO', K1='K1  GIALLO', K2='K2  ARANCIONE', K3='K3  PAPERA')
RIGHE = (('1 · IL MONOPATTINO DEL BONUS', ('S1', 'S2', 'S3')), ('2 · LA DIGA DELLA CASTORA', ('D1', 'D2')), ('3 · IL CANOTTO', ('K1', 'K2', 'K3')))
PI = math.pi


def scena(op):
    import bpy
    from mathutils import Vector
    from common import reset_scene, collection, material
    from render_setup import setup_render, world
    import set004, luci, kitlook, props028, props030, castora, pippo2 as pippo, tumbo
    A = kitlook.A
    reset_scene(); set004._c.clear(); sc = bpy.context.scene; C = collection('C')
    W, H = (1350, 900) if op[0] == 'D' else (900, 900)
    setup_render(sc, W, H, samples=10, fps=24, frames=1); A.qualita_eevee(preset='equilibrato', riflessi=True, scena=sc, risoluzione=(W, H))
    M = props030.mats030(props028.mats028(A), A); F = props028.font()
    cam = bpy.data.objects.new('Cam', bpy.data.cameras.new('Cam')); C.objects.link(cam); sc.camera = cam
    def aim(loc, tgt, lens): cam.location = loc; luci.punta(cam, Vector(tgt)); cam.data.lens = lens
    def tex(aid, dim, riserva):
        try: return A.materiale(aid, dimensione=dim)
        except Exception as e: print('texture mancante', aid, e); return riserva
    world(sc, top=(0.30, 0.52, 0.95), bottom=(0.95, 0.86, 0.72), strength=1.0); luci.cielo_basso(sc.world, 0.4)
    if op[0] == 'S':
        props028.box('Suolo', (-30, -30, -0.1), (30, 30, 0), tex('PavingStones070', 2.0, material('suolo30', (0.6, 0.58, 0.55), rough=0.9)), C)
        props028.box('Muro', (-30, 3.2, 0), (30, 3.5, 9), tex('painted_plaster_wall', 3.0, material('muro30', (0.93, 0.78, 0.5), rough=0.9)), C)
        R = props030.monopattino(C, M, op); R['root'].rotation_euler = (0, 0, 1.05)
        t = props028.cartellino(C, M, F, testo='2.000 €', h=0.9, nome='Prezzo', larg=1.0, alt=0.4); t.location = (0.75, -0.5, 0)
        P = pippo.build_pippo(C); P['root'].location = (-1.35, 0.5, 0); P['root'].rotation_euler = (0, 0, -0.5); pippo.emozione(P, 1, 'sorpreso')
        aim((0.2, -5.6, 1.5), (-0.25, 0, 1.05), 50); luci.sole(C, (0.1, -1), lato=1, energia=3.2, angolo_alto=38)
    elif op[0] == 'D':
        props028.box('Prato', (-80, -80, -0.2), (80, 80, -0.04), tex('Grass004', 3.0, material('prato30', (0.25, 0.5, 0.15), rough=0.9)), C)
        props030.strada(C, M, 80.0, 10.0); props030.diga(C, M, op, 10.0)
        K = castora.castora(C, castora.mats_castora(), stile='A'); K['root'].location = (-1.6, -3.2, 0.02); K['root'].rotation_euler = (0, 0, -0.35); castora.emozione(K, 1, 'trionfo')
        P = pippo.build_pippo(C); P['root'].location = (2.4, -4.2, 0.02); P['root'].rotation_euler = (0, 0, 2.6); pippo.emozione(P, 1, 'spaventato')
        aim((-5.5, -14.5, 2.6), (0.0, 0.0, 1.9), 30); luci.sole(C, (-0.3, -1), lato=1, energia=3.2, angolo_alto=40)
    else:
        props030.acqua(C, M, 80.0, 0.0)
        R = props030.canotto(C, M, op); R['root'].rotation_euler = (0, 0, 0.75); R['root'].location = (0, 0, -0.06)
        P = pippo.build_pippo(C); P['root'].parent = R['root']; P['root'].location = (0, 0.35, -0.75); P['root'].rotation_euler = (0, 0, 0); pippo.emozione(P, 1, 'felice')
        T = tumbo.build_tumbo(C, scale=0.75); T['root'].parent = R['root']; T['root'].location = (0, -0.6, 0.1)
        aim((-1.2, -7.0, 2.6), (0, 0, 0.75), 45); luci.sole(C, (-0.2, -1), lato=1, energia=3.2, angolo_alto=38)
    sc.view_settings.exposure = -0.3
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
    im.save(os.path.join(SCHEDE, 'scelta030.jpg'), quality=90); print('SCHEDA')


if __name__ == '__main__':
    a = sys.argv[1] if len(sys.argv) > 1 else 'componi'
    componi() if a == 'componi' else scena(a)
