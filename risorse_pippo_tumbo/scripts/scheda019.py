"""Scheda di opzioni del video 019 «Il doppio gioco»: bombe (A lunga, B tonda), carro armato (C militare, D giocattolo),
sottomarino nella piscina gonfiabile (E giallo cartoon, F grigio militare), armeria del prete (G legno e armi vere, H pop e blaster).
Uso:  python scheda019.py A   (una opzione per processo: A..H), poi  python scheda019.py componi
Immagini in ../out/scheda019/, schede finali in ../schede/scelta019_*.png"""
import sys, os, math
QUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, QUI)
import bpy
from mathutils import Vector
from common import *
from render_setup import *
import set004, props009, props012, props019, giulia, luci, kitlook
import pippo2
import tumbo
A = kitlook.A
OUT = os.path.join(QUI, '..', 'out', 'scheda019'); SCHEDE = os.path.join(QUI, '..', 'schede'); os.makedirs(OUT, exist_ok=True)
PI = math.pi
FONT = A.font('luckiest')
VERTICALI = 'ABGH'


def staccionata(C, M, x=0.0, y0=-7.0, y1=7.0, h=1.25):
    legno = A.materiale('weathered_planks', dimensione=1.0)
    n = int((y1 - y0) / 0.32)
    for k in range(n):
        y = y0 + k * 0.32
        props019.box('Asse', (x, y, h / 2), (0.06, 0.24, h), legno, C)
        props019.box('AssePunta', (x, y, h), (0.06, 0.17, 0.17), legno, C, rot=(PI / 4, 0, 0))
    for z in (0.35, h - 0.25): props019.box('Traversa', (x + 0.06, (y0 + y1) / 2, z), (0.05, y1 - y0, 0.12), legno, C)


def giulia_cavalcioni(C, GM, bomb_root, top):
    """Giulia seduta a cavalcioni in cima alla bomba, rivolta verso la punta, mattarello alzato."""
    G = giulia.giulia(C, GM, 'A')
    G['root'].parent = bomb_root; G['root'].location = (-0.3, 0, top - 0.42); G['root'].rotation_euler = (0, 0, PI / 2 - 0.55)
    G['hipL'].rotation_euler = (0.9, -0.8, 0); G['hipR'].rotation_euler = (0.9, 0.8, 0)
    G['shoulderR'].rotation_euler = (0, 2.7, 0); G['shoulderL'].rotation_euler = (0.3, -1.0, 0)
    giulia.mattarello(C, GM, G, 'R')
    giulia.giex(G, None, brow=0.7, mouth=0.9, lid=0.0, look=(0.3, 0.2), naso=0.6)
    return G


def scena(op):
    reset_scene(); set004._c.clear(); scene = bpy.context.scene
    C = collection('C')
    W, H = (720, 1280) if op in VERTICALI else (900, 900)
    setup_render(scene, W, H, samples=8, fps=24, frames=1)
    A.qualita_eevee(preset='equilibrato', riflessi=op in 'EFGH', scena=scene, risoluzione=(W, H)); scene.view_settings.exposure = 0.25
    M = props019.mats019(); GM = giulia.mats_giulia(); G9 = props009.mats009()
    cam = bpy.data.objects.new('Cam', bpy.data.cameras.new('Cam')); C.objects.link(cam); scene.camera = cam; cam.data.clip_start = 0.02
    def aim(loc, tgt, lens):
        cam.location = loc; luci.punta(cam, tgt); cam.data.lens = lens
    if op not in 'GH':
        A.cielo('sunflowers_puresky', forza=1.1, rotazione=43.0, ris='4k')
        luci.cielo_basso(scene.world, 0.4)
        grass = A.materiale('Grass001', dimensione=3.0, rilievo=0.8, tinta=(1.05, 1.35, 0.7), ruvidita=1.5)
        g = set004.bx('Prato', (-60, -60, -0.3), (60, 60, 0.0), grass, C); A.niente_ombra(g)
        for k, (x, y, sp) in enumerate(((-14, 16, 'island_tree_01'), (12, 18, 'fir_tree_01'), (-5, 22, 'island_tree_02'), (20, 9, 'pine_tree_01'))):
            try: A.albero_cartonato(sp, posizione=(x, y, 0), altezza=9 + k, collezione=C)
            except Exception as e: print('albero', e)
    if op in 'AB':
        staccionata(C, M, y0=-11.0, y1=9.0)
        L = 4.4
        BG = props019.bomba(C, M, op, 'GUALTIERO', FONT, L=L, lato=-1); BG['root'].location = (-0.45 * L - 0.35, 0, 4.0); BG['root'].rotation_euler = (0, -0.08, 0.12)
        BP = props019.bomba(C, M, op, 'PIPPO', FONT, L=L, lato=1); BP['root'].location = (0.45 * L + 0.35, 0, 3.85); BP['root'].rotation_euler = (0, 0.06, PI - 0.12)
        for B, br in ((BG, 0.5), (BP, 0.5)):
            for b in B['face']['brows']: b.rotation_euler = (0, b.rotation_euler[1] * -3, 0)
            props019.fiamma(C, M, B['body'], -0.5 * L, s=L / 4.2)
        giulia_cavalcioni(C, GM, BG['body'], BG['R'])
        P = pippo2.build_pippo(C); P['root'].location = (1.6, -7.6, 0); P['root'].rotation_euler = (0, 0, 0.45)
        pippo2.emozione(P, 1, 'spaventato')
        T = tumbo.build_tumbo(C, scale=0.75); T['root'].location = (2.9, -8.0, 0); T['root'].rotation_euler = (0, 0, 0.6)
        aim((4.6, -14.5, 1.7), (0.0, 0, 3.7), 22)
        luci.sole(C, (5.2, -14.0), lato=-1)
    elif op in 'CD':
        T = props019.carro(C, M, op, FONT); T['root'].rotation_euler = (0, 0, -0.55); T['turret'].rotation_euler = (0, 0, 0.25)
        bpy.context.view_layer.update()
        hw = T['hatch'].matrix_world.translation
        P = pippo2.build_pippo(C); P['root'].location = (hw.x, hw.y, hw.z - 0.62); P['root'].rotation_euler = (0, 0, 0.66)
        pippo2.emozione(P, 1, 'furbo')
        ball_ = set004.ball_; ball_('Casco', 1.0, (0, 0.03, 0.74), M['army'] if op == 'C' else M['toyY'], C, parent=P['head'], sc=(0.47, 0.47, 0.24))
        tw = T['turret'].matrix_world
        TB = tumbo.build_tumbo(C, scale=0.75); TB['root'].location = tuple(T['root'].matrix_world @ Vector((0.75, -1.75, 1.7))); TB['root'].rotation_euler = (0, 0, 0.5)
        for sx in (-1, 1): ball_('Occhialino', 0.07, tuple(Vector(TB['root'].location) + Vector((sx * 0.11, -0.42, 0.62))), M['glass'], C, sc=(1, 0.5, 1))
        aim((5.0, -6.4, 3.0), (0.0, 0.0, 1.9), 30)
        luci.sole(C, (5.0, -6.4), lato=1)
    elif op in 'EF':
        PS = props019.piscina(C, M)
        S = props019.sottomarino(C, M, op, FONT)
        GS = 3.6                                                                          # sottomarino gigante in una piscina minuscola
        from mathutils import Euler
        rot = Euler((-0.6, 0, 1.5)); off = Vector((0, 1.9 * GS, 0)); off.rotate(rot)            # la poppa dentro la piscina, la prua verso il cielo
        S['root'].scale = (GS, GS, GS); S['root'].rotation_euler = rot; S['root'].location = tuple(Vector((0, 0, 0.3)) - off)
        bpy.context.view_layer.update(); hw = S['hatch'].matrix_world.translation
        Gi = giulia.giulia(C, GM, 'A'); Gi['root'].location = (hw.x, hw.y, hw.z - 0.95); Gi['root'].rotation_euler = (0, 0, -0.35)
        Gi['shoulderR'].rotation_euler = (0, 2.4, 0); Gi['shoulderL'].rotation_euler = (0, -0.6, 0)
        giulia.giex(Gi, None, brow=0.8, mouth=0.6, lid=0.1, look=(0.6, 0.3), naso=0.3)
        props019.cappello_capitano(C, M, Gi['head'], (0, 0.0, 0.42), s=1.25)
        G = props009.gualtiero(C, G9); G['root'].location = (-2.7, -1.0, 0); G['root'].rotation_euler = (0, 0, -0.9)
        props009.gex(G, None, brow=0.5, mouth=0.4)
        P = pippo2.build_pippo(C); P['root'].location = (2.5, -2.4, 0); P['root'].rotation_euler = (0, 0, 0.9)
        pippo2.emozione(P, 1, 'sorpreso')
        T = tumbo.build_tumbo(C, scale=0.75); T['root'].location = (3.2, -1.7, 0); T['root'].rotation_euler = (0, 0, 1.0)
        aim((4.0, -26.0, 2.6), (3.5, 0.0, 5.0), 26)
        luci.sole(C, (9.0, -30.0), lato=1)
    else:
        cx, cy = 600.0, 0.0
        A.cielo('sunflowers_puresky', forza=0.3, rotazione=43.0, ris='1k'); luci.cielo_basso(scene.world, 0.12)
        Ar = props019.armeria(C, M, A, op, (cx, cy), FONT)
        M12 = props012.mats012()
        mr, face, wheels, mouth = props012.moto(C, M12); mr.location = (cx - 0.35, cy + 1.25, 0.35); mr.rotation_euler = (0, 0, 0.25); mr.scale = (1.35, 1.35, 1.35)
        mouth.scale = (0.08, 0.015, 0.04); props012.moto_extras(C, M12, mr, face)
        top = Ar['counter_top']
        props019.scontrino(C, M, Ar['root'], (0.95, -1.05, top + 0.12), 'PIPPO', FONT, rot=(0.5, 0, 0.3))
        props019.scontrino(C, M, Ar['root'], (1.35, -1.08, top + 0.2), 'GUALTIERO', FONT, rot=(0.4, 0, -0.25))
        aim((cx + 0.6, cy - 6.4, 1.6), (cx, cy + 0.9, 1.95), 31)
        luci.cinema(C, (cx, cy + 0.4, 1.6), tuple(cam.location), distanza=4.5, lato=1)
    if op not in 'GH':
        luci.ombre_pulite(scene, mezza_risoluzione=False)
    kitlook.tune_cutouts(1.9)
    scene.render.filepath = os.path.join(OUT, op + '.png'); bpy.ops.render.render(write_still=True); print('RESA', op, flush=True)


def componi():
    from PIL import Image, ImageDraw, ImageFont
    def tit(im, testo, xy, size=64, col=(255, 225, 60)):
        ImageDraw.Draw(im).text(xy, testo, font=ImageFont.truetype(FONT, size), fill=col, stroke_width=max(3, size // 11), stroke_fill=(20, 20, 30), anchor='mm')
    I = {k: Image.open(os.path.join(OUT, k + '.png')).convert('RGB') for k in 'ABCDEFGH' if os.path.exists(os.path.join(OUT, k + '.png'))}
    w = 720
    for nome, pair in (('bombe', (('A', 'bomba lunga'), ('B', 'bomba tonda'))), ('armeria', (('G', 'legno e armi vere'), ('H', 'pop e blaster')))):
        if not all(k in I for k, _ in pair): continue
        im = Image.new('RGB', (2 * w + 20, 1280 + 120), (20, 20, 30))
        for i, (k, d) in enumerate(pair):
            im.paste(I[k], (i * (w + 20), 120)); tit(im, k + '  ' + d, (i * (w + 20) + w // 2, 60), 56)
        im.save(os.path.join(SCHEDE, 'scelta019_%s.png' % nome))
    rows = [(('C', 'carro militare'), ('D', 'carro giocattolo')), (('E', 'sottomarino giallo'), ('F', 'sottomarino militare'))]
    if all(k in I for r_ in rows for k, _ in r_):
        im = Image.new('RGB', (2 * 900 + 20, 2 * 900 + 20 + 240), (20, 20, 30))
        for r_, pair in enumerate(rows):
            y = 120 + r_ * (900 + 120)
            for i, (k, d) in enumerate(pair):
                im.paste(I[k], (i * 920, y)); tit(im, k + '  ' + d, (i * 920 + 450, y - 60), 56)
        im.save(os.path.join(SCHEDE, 'scelta019_carro_sottomarino.png'))
    print('SCHEDE FATTE', flush=True)


if __name__ == '__main__':
    a = sys.argv[-1]
    if a == 'componi': componi()
    else: scena(a)
