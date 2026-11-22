"""Scheda di opzioni del video 024 «Martina, il cono stradale»:
Martina (M1 cono vero, M2 cono con gli occhi, M3 cono cartoon del kit), semaforo (S1 fatto a mano all'italiana, S2 KayKit, S3 Kenney),
rullo compressore (R1 normale, R2 gigante), camion del Comune (K1 nettezza urbana, K2 pianale coi coni, K3 furgone),
l'Italia coperta di coni (V1 plastico di giorno, V2 dallo spazio di notte).
Uso:  python scheda024.py M1   (una opzione per processo), poi  python scheda024.py componi
Immagini in ../out/scheda024/, schede finali in ../schede/scelta024_*.png"""
import sys, os, math
QUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, QUI)
import bpy
from mathutils import Vector
from common import *
from render_setup import *
import set004, props007, props021, props024, luci, kitlook
import pippo2
import tumbo
A = kitlook.A
OUT = os.path.join(QUI, '..', 'out', 'scheda024'); SCHEDE = os.path.join(QUI, '..', 'schede'); os.makedirs(OUT, exist_ok=True)
PI = math.pi
FONT = A.font('luckiest')
OPZ = ('M1', 'M2', 'M3', 'S1', 'S2', 'S3', 'R1', 'R2', 'K1', 'K2', 'K3', 'V1', 'V2')
KENNEY_CONO = 'kenney/city-kit-roads/construction-cone'
HM, HS = 1.2, 4.6                                                      # Martina e il semaforo, in proporzione a Pippo (alto circa 2,6 m)


def guarda(o, x, y):
    """ruota il personaggio (fronte -Y) verso il punto (x, y)."""
    dx, dy = x - o.location.x, y - o.location.y; o.rotation_euler = (0, 0, math.atan2(dx, -dy))


def cuori(C, M7, centro, n=3, s=0.12):
    me = props007.heart_mesh(M7)
    for i in range(n):
        a = (i - (n - 1) / 2) * 0.55
        o = bpy.data.objects.new('Cuore', me); C.objects.link(o)
        o.location = (centro[0] + math.sin(a) * 0.42, centro[1], centro[2] + math.cos(a) * 0.2); o.scale = (s * (1.15 if i == 1 else 0.85),) * 3; o.rotation_euler = (0, a * 0.5, 0)


def cono_kenney(C, M, font, H=0.9, x=0.0, y=0.0):
    r = A.modello(KENNEY_CONO, posizione=(x, y, 0.0), altezza=H, collezione=C, appoggia=True)
    bpy.context.view_layer.update()
    vv = [o.matrix_world @ v.co for o in r.children_recursive if o.type == 'MESH' for v in o.data.vertices]
    k = H / 0.9
    def rz(z):
        rr = [math.hypot(p.x - x, p.y - y) for p in vv if abs(p.z - z) < 0.04 * H]
        return max(rr) if rr else 0.1 * H
    T = props024.cartellino(C, props024.mats024(), None, rz, k, 0.0, font, 'MARTINA', 'MartinaK', zl=0.66 * H)
    T.location = (x, y, 0.0)
    return r


def strada(C):
    grass = A.materiale('Grass001', dimensione=3.0, rilievo=0.8, tinta=(1.05, 1.35, 0.7), ruvidita=1.5)
    g = set004.bx('Prato', (-80, -80, -0.3), (80, 80, 0.0), grass, C); A.niente_ombra(g)
    asf = A.materiale('asphalt_02', dimensione=4.0)
    set004.bx('Asfalto', (-80, -30.0, 0.0), (80, 3.2, 0.012), asf, C)
    marc = A.materiale('Concrete034', dimensione=2.0)
    set004.bx('Marciapiede', (-80, 3.2, 0.0), (80, 5.0, 0.15), marc, C)
    for k, (x, y, sp) in enumerate(((-16, 22, 'island_tree_01'), (13, 24, 'fir_tree_01'), (-4, 28, 'island_tree_02'), (24, 30, 'pine_tree_01'))):
        try: A.albero_cartonato(sp, posizione=(x, y, 0), altezza=9 + k, collezione=C)
        except Exception as e: print('albero', e)
    M = props024.mats024()
    for x, ry in ((-3.0, 0.15), (3.1, -0.2), (-6.5, 0.0)):             # transenne del cantiere sul fondo
        t = props024.transenna(C, M); t.location = (x, 2.4, 0.012); t.rotation_euler = (0, 0, ry)


def pippo_tumbo(C, pp, tp, guardo, emo='felice', tumbo_lingua=1.0):
    P = pippo2.build_pippo(C); P['root'].location = (pp[0], pp[1], 0.012); guarda(P['root'], *guardo); pippo2.emozione(P, 1, emo)
    T = tumbo.build_tumbo(C, scale=0.75); T['root'].location = (tp[0], tp[1], 0.012); guarda(T['root'], *guardo)
    tumbo.tumbo_express(T, 1, tongue=tumbo_lingua)
    return P, T


def scena(op):
    reset_scene(); set004._c.clear(); scene = bpy.context.scene
    C = collection('C')
    vert = op[0] == 'V'
    W, H = (720, 1280) if vert else (900, 900)
    setup_render(scene, W, H, samples=8, fps=24, frames=1)
    A.qualita_eevee(preset='equilibrato', riflessi=True, scena=scene, risoluzione=(W, H)); scene.view_settings.exposure = 0.25
    cam = bpy.data.objects.new('Cam', bpy.data.cameras.new('Cam')); C.objects.link(cam); scene.camera = cam; cam.data.clip_start = 0.02; cam.data.clip_end = 2000
    def aim(loc, tgt, lens):
        cam.location = loc; luci.punta(cam, tgt); cam.data.lens = lens
    font = bpy.data.fonts.load(FONT)
    M = props024.mats024(); M7 = props007.mats007()
    if not vert:
        A.cielo('sunflowers_puresky', forza=1.1, rotazione=43.0, ris='4k'); luci.cielo_basso(scene.world, 0.4)
        strada(C)
    if op[0] == 'M':
        if op == 'M3': cono_kenney(C, M, font, H=HM)
        else: Mt = props024.cono(C, M, H=HM, occhi=(op == 'M2'), font=font)
        P, T = pippo_tumbo(C, (1.1, -0.45), (-1.05, -0.35), (0, 0), 'felice')
        guarda(P['root'], 0.0, -2.5); guarda(T['root'], 0.0, 0.0)
        cuori(C, M7, (1.35, -0.7, 2.5), s=0.14)
        aim((0.2, -3.9, 1.35), (0.1, 0, 1.12), 32); luci.sole(C, (0.2, -3.9), lato=1)
    elif op[0] == 'S':
        if op == 'S1':
            S = props024.semaforo(C, M, H=HS); S['root'].location = (0.25, 0.6, 0.012); props024.accendi(S, 'giallo')
        elif op == 'S2': A.modello('kaykit/city-builder-bits/trafficlight_A', posizione=(0.25, 0.6, 0.012), altezza=HS, collezione=C, appoggia=True)
        else: A.modello('kenney/city-kit-roads/traffic-light', posizione=(0.25, 0.6, 0.012), altezza=HS, rotazione=90.0, collezione=C, appoggia=True)
        Mt = props024.cono(C, M, H=HM, font=font); Mt['root'].location = (-0.65, 0.3, 0.012); Mt['root'].rotation_euler = (0, 0, -0.3)
        P, T = pippo_tumbo(C, (1.75, -0.9), (-1.9, -0.8), (0, 0.4), 'arrabbiato', 0.4); guarda(P['root'], -1.2, -3.5)
        aim((0.35, -5.6, 2.1), (0.0, 0, 2.3), 27); luci.sole(C, (0.35, -5.6), lato=1)
    elif op[0] == 'R':
        Rr = props024.rullo(C, M); s = 1.35 if op == 'R1' else 3.2
        Rr['root'].scale = (s,) * 3; Rr['root'].location = (0.6 * s, 0.2, 0.012); Rr['root'].rotation_euler = (0, 0, -0.32)
        px = 0.6 * s - 2.3 * s - 1.2
        P, T = pippo_tumbo(C, (px, -0.9), (px + 0.9, -2.0), (0.6 * s, 0.2), 'spaventato', 0.0); guarda(P['root'], px - 6.0, -9.0)
        if op == 'R1': aim((-7.6, -7.4, 2.3), (-1.2, 0, 2.0), 32); luci.sole(C, (-7.6, -7.4), lato=1)
        else: aim((-14.5, -14.5, 4.4), (-2.6, 0, 4.6), 32); luci.sole(C, (-14.5, -14.5), lato=1)
    elif op[0] == 'K':
        aid = {'K1': 'kenney/car-kit/garbage-truck', 'K2': 'kenney/car-kit/truck-flat', 'K3': 'kenney/car-kit/delivery'}[op]
        G = bpy.data.objects.new('GruppoCamion', None); C.objects.link(G)
        try: Tk = A.modello(aid, posizione=(0.0, 0.0, 0.012), altezza=3.4, collezione=C, appoggia=True)
        except Exception as e:
            print('camion', e); Tk = A.modello('kenney/car-kit/truck', posizione=(0.0, 0.0, 0.012), altezza=3.4, collezione=C, appoggia=True)
        bpy.context.view_layer.update()
        vv = [o.matrix_world @ v.co for o in Tk.children_recursive if o.type == 'MESH' for v in o.data.vertices]
        y0, y1 = min(p.y for p in vv), max(p.y for p in vv); x0, x1 = min(p.x for p in vv), max(p.x for p in vv); L = y1 - y0
        kids = [Tk]
        if op == 'K2':                                                 # pianale carico di coni: quota misurata sui vertici del cassone
            dietro = [p for p in vv if p.y > y0 + 0.62 * L and abs(p.x - (x0 + x1) / 2) < 0.3 * (x1 - x0)]
            zp = max(p.z for p in dietro) if dietro else 1.2
            for i in range(9):
                c = props024.cono(C, M, H=0.6, font=None, testo=None, nome='ConoCarico', seg=24)
                u, v = (i % 3) - 1, (i // 3)
                c['root'].location = ((x0 + x1) / 2 + u * 0.42 * (x1 - x0) / 1.4, y0 + 0.62 * L + 0.25 + v * 0.3 * L / 1.2 * 0.5, zp); kids.append(c['root'])
        for o in kids: o.parent = G
        G.location = (0.4, 0.6, 0.0); G.rotation_euler = (0, 0, math.radians(-62))
        P, T = pippo_tumbo(C, (3.7, -1.5), (4.6, -2.3), (0.4, 0.6), 'sorpreso', 0.6); guarda(P['root'], 2.0, -9.0)
        aim((1.4, -11.8, 3.1), (1.0, 0, 1.7), 30); luci.sole(C, (1.4, -11.8), lato=1)
    else:                                                              # l'Italia
        notte = op == 'V2'
        world = scene.world or bpy.data.worlds.new('W'); scene.world = world; world.use_nodes = True
        bg = next(n for n in world.node_tree.nodes if n.type == 'BACKGROUND')
        if notte:
            bg.inputs['Color'].default_value = (0.0005, 0.0008, 0.002, 1); bg.inputs['Strength'].default_value = 1.0
            I = props024.italia(C, scala=0.01, tipo='notte', coni=20000)
            props021.bagliore(scene, forza=0.35, soglia=1.6, dimensione=0.35)
            luci._luce(C, 'Luna', 'SUN', (0, 0, 20), (3, 6, 0), 0.25, (0.55, 0.65, 1.0), False)
            scene.view_settings.exposure = 0.0
            aim((0.2, -6.4, 13.2), (0.2, 0.2, 0.0), 30)
        else:
            A.cielo('sunflowers_puresky', forza=1.1, rotazione=43.0, ris='4k'); luci.cielo_basso(scene.world, 0.4)
            I = props024.italia(C, scala=0.01, tipo='giorno', coni=45000)
            aim((0.4, -8.6, 11.6), (0.25, 0.2, 0.0), 32); luci.sole(C, (0.4, -9.2), lato=1, energia=4.0, angolo_alto=40)
    luci.ombre_pulite(scene, mezza_risoluzione=False)
    kitlook.tune_cutouts(1.9)
    scene.render.filepath = os.path.join(OUT, op + '.png'); bpy.ops.render.render(write_still=True); print('RESA', op, flush=True)


def componi():
    from PIL import Image, ImageDraw, ImageFont
    def tit(im, testo, xy, size=54, col=(255, 225, 60)):
        ImageDraw.Draw(im).text(xy, testo, font=ImageFont.truetype(FONT, size), fill=col, stroke_width=max(3, size // 11), stroke_fill=(20, 20, 30), anchor='mm')
    I = {k: Image.open(os.path.join(OUT, k + '.png')).convert('RGB') for k in OPZ if os.path.exists(os.path.join(OUT, k + '.png'))}
    q = 600                                                            # riquadri da 600 px: tre per riga stanno su un telefono
    rows = [(('M1', 'cono vero'), ('M2', 'cono con gli occhi'), ('M3', 'cono cartoon')),
            (('S1', 'semaforo italiano'), ('S2', 'semaforo morbido'), ('S3', 'semaforo cubetto')),
            (('R1', 'rullo normale'), ('R2', 'rullo gigante'), None),
            (('K1', 'camion nettezza'), ('K2', 'pianale coi coni'), ('K3', 'furgone'))]
    im = Image.new('RGB', (3 * q + 40, len(rows) * (q + 100)), (20, 20, 30))
    for r_, row in enumerate(rows):
        y = 100 + r_ * (q + 100)
        for i, it in enumerate(row):
            if not it: continue
            k, d = it
            if k in I: im.paste(I[k].resize((q, q), Image.LANCZOS), (i * (q + 20), y)); tit(im, k + '  ' + d, (i * (q + 20) + q // 2, y - 50), size=44)
    im.save(os.path.join(SCHEDE, 'scelta024_oggetti.png'), quality=92)
    w = 720; im = Image.new('RGB', (2 * w + 20, 1280 + 110), (20, 20, 30))
    for i, (k, d) in enumerate((('V1', 'Italia di giorno'), ('V2', 'Italia dallo spazio'))):
        if k in I: im.paste(I[k], (i * (w + 20), 110)); tit(im, k + '  ' + d, (i * (w + 20) + w // 2, 55))
    im.save(os.path.join(SCHEDE, 'scelta024_italia.png'), quality=92)
    print('SCHEDE FATTE', flush=True)


if __name__ == '__main__':
    a = sys.argv[-1]
    if a == 'componi': componi()
    else: scena(a)
