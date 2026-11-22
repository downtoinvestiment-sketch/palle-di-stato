"""Logo di «Palle di Stato» con i personaggi della serie, come nei video (22 novembre 2026).
Colori del canale: blu notte #0E1B3D (sfondo), rosso #D7263D (fascia), oro #F2B705 (scritte piccole e bordi), bianco #F5F5F0 con contorno nero (titolo).
Uso: python logo_pds.py [A B]  ->  ../schede/logo_pds_A.png (icona tonda, 1080x1080), logo_pds_B.png (copertina 1600x900), ../schede/logo_pds.jpg"""
import sys, os, math
QUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, QUI)
import bpy
from mathutils import Vector
from common import *
from render_setup import *
import kitlook, luci, set004
import generale as gn, cinese as ci, platino as pl, admin_world as aw, cappellone as cp, rospina, bialada as bi
A = kitlook.A
FONT = os.path.join(QUI, '..', 'assets', 'font', 'LuckiestGuy-Regular.ttf')
BLU, ROSSO, ORO, BIANCO, NERO = (0.0055, 0.0116, 0.046), (0.68, 0.019, 0.047), (0.89, 0.47, 0.0), (0.91, 0.91, 0.87), (0.006, 0.006, 0.006)


def testo(C, t, loc, size, col, contorno=True, estr=0.05):
    cu = bpy.data.curves.new('T', 'FONT'); cu.body = t; cu.font = bpy.data.fonts.load(FONT, check_existing=True)
    cu.size = size; cu.extrude = estr; cu.bevel_depth = 0.01; cu.align_x = 'CENTER'; cu.align_y = 'CENTER'
    o = bpy.data.objects.new('Titolo', cu); C.objects.link(o); o.location = loc; o.rotation_euler = (math.pi / 2, 0, 0); cu.materials.append(material('titolo', col, rough=0.35))
    if contorno:
        c2 = cu.copy(); c2.offset = 0.06 * size; c2.extrude = estr * 0.5; c2.materials.clear(); c2.materials.append(material('contorno', NERO, rough=0.5))
        o2 = bpy.data.objects.new('TitoloContorno', c2); C.objects.link(o2); o2.location = Vector(loc) + Vector((0, 0.04, 0)); o2.rotation_euler = (math.pi / 2, 0, 0)
    return o


def scena(W, H):
    reset_scene(); set004._c.clear(); sc = bpy.context.scene; C = collection('C')
    setup_render(sc, W, H, samples=24, fps=24, frames=1); A.qualita_eevee(preset='equilibrato', riflessi=True, scena=sc, risoluzione=(W, H))
    world(sc, top=(0.03, 0.05, 0.14), bottom=(0.02, 0.03, 0.08), strength=2.5)
    shape('Fondo', 'cyl:9:0.1', loc=(0, 6.0, 1.5), rot=(math.pi / 2, 0, 0), mat=material('fondo', (0.012, 0.025, 0.08), rough=0.9), coll=C)
    return sc, C


def personaggi(C, chi):
    R = []
    for fa, x, rz, posa in chi:
        P = fa(C); P['root'].location = (x, 0, 0); P['root'].rotation_euler = (0, 0, rz); posa(P); R.append(P)
    return R


def rendi(sc, nome):
    p = os.path.join(QUI, '..', 'schede', 'logo_pds_%s.png' % nome); sc.render.filepath = p; bpy.ops.render.render(write_still=True); print('LOGO', nome, flush=True); return p


def logo_A():
    """icona tonda: tre politici in primo piano dentro l'anello d'oro, titolo sotto"""
    sc, C = scena(1080, 1080)
    personaggi(C, [(lambda C: ci.cinese(C, 'B'), -0.95, 0.35, lambda P: ci.emozione(P, None, 'furbo')),
                   (lambda C: gn.generale(C, 'A'), 0.0, 0.0, lambda P: (gn.emozione(P, None, 'urla'), gn.gesto(P, None, 'dito puntato'))),
                   (lambda C: pl.platino(C, 'A'), 0.95, -0.35, lambda P: pl.emozione(P, None, 'istituzionale'))])
    bpy.ops.mesh.primitive_torus_add(major_radius=1.75, minor_radius=0.07, location=(0, 0.9, 1.75), rotation=(math.pi / 2, 0, 0), major_segments=128)
    bpy.context.object.data.materials.append(material('oro', ORO, rough=0.25, metallic=0.7))
    shape('Fascia', 'cyl:1:1', loc=(0, -0.55, 0.62), rot=(0, math.pi / 2, 0), scale=(0.22, 0.22, 2.5), mat=material('fascia', ROSSO, rough=0.4), coll=C)
    testo(C, 'PALLE DI STATO', (0, -0.75, 0.62), 0.5, BIANCO)
    cam = bpy.data.objects.new('Cam', bpy.data.cameras.new('Cam')); C.objects.link(cam); sc.camera = cam; cam.data.lens = 50
    mira = Vector((0, 0, 1.45)); cam.location = (0, -5.2, 1.6); luci.punta(cam, mira)
    luci.cinema(C, mira, tuple(cam.location), distanza=4.5, lato=1); return rendi(sc, 'A')


def logo_B():
    """copertina: la fila dei politici sul palco, titolo grande con la fascia rossa davanti"""
    sc, C = scena(1600, 900)
    personaggi(C, [(lambda C: rospina.rospina(C, rospina.mats_rospina(), stile='D'), -2.6, 0.3, lambda P: rospina.emozione(P, None, 'importantissima')),
                   (lambda C: ci.cinese(C, 'B'), -1.55, 0.2, lambda P: ci.emozione(P, None, 'furbo')),
                   (lambda C: gn.generale(C, 'A'), -0.5, 0.05, lambda P: (gn.emozione(P, None, 'urla'), gn.gesto(P, None, 'comizio'))),
                   (lambda C: aw.admin_world(C, 'A'), 0.55, -0.05, lambda P: (aw.emozione(P, None, 'serio'), aw.gesto(P, None, 'indica'))),
                   (lambda C: pl.platino(C, 'A'), 1.6, -0.2, lambda P: pl.emozione(P, None, 'istituzionale')),
                   (lambda C: cp.cappellone(C), 2.7, -0.3, lambda P: cp.faccia(P, None, mouth_open=0.6, smile=1.0))])
    shape('Palco', 'cyl:4.5:0.3', loc=(0, 0.5, -0.15), mat=material('palco', (0.02, 0.04, 0.12), rough=0.6), coll=C)
    shape('Fascia', 'cyl:1:1', loc=(0, -1.2, 0.55), rot=(0, math.pi / 2, 0), scale=(0.24, 0.24, 3.4), mat=material('fascia', ROSSO, rough=0.4), coll=C)
    testo(C, 'PALLE DI STATO', (0, -1.45, 0.62), 0.72, BIANCO)
    testo(C, 'LA POLITICA VISTA DA VICINO. TROPPO VICINO.', (0, -1.5, 0.2), 0.2, ORO)
    cam = bpy.data.objects.new('Cam', bpy.data.cameras.new('Cam')); C.objects.link(cam); sc.camera = cam; cam.data.lens = 40
    mira = Vector((0, 0, 1.2)); cam.location = (0, -8.2, 1.6); luci.punta(cam, mira)
    luci.cinema(C, mira, tuple(cam.location), distanza=5.0, lato=1); return rendi(sc, 'B')


fatti = [{'A': logo_A, 'B': logo_B}[k]() for k in (sys.argv[1:] or ['A', 'B'])]
from PIL import Image
ims = [Image.open(p).convert('RGB') for p in fatti]; hh = 720; ims = [im.resize((int(im.width * hh / im.height), hh)) for im in ims]
f = Image.new('RGB', (sum(i.width for i in ims) + 20 * (len(ims) - 1), hh), (20, 20, 24)); x = 0
for im in ims: f.paste(im, (x, 0)); x += im.width + 20
f.save(os.path.join(QUI, '..', 'schede', 'logo_pds.jpg'), quality=90); print('LOGHI OK')
