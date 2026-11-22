"""Scheda delle altezze dei personaggi (22 novembre 2026): Pippo 175 cm come metro, Rospina circa 158 cm, Castora circa 170 cm, il Generale 190 cm, Cappellone circa 195 cm.
Uso: python scheda_altezze.py  -> ../schede/altezze.jpg"""
import sys, os
QUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, QUI)
import bpy
from mathutils import Vector
from common import reset_scene, collection, material
from render_setup import setup_render, world
import set004, luci, kitlook, rospina, cappellone as cp, pippo2, tumbo, props009, castora, generale as gn, props029 as P9
A = kitlook.A
reset_scene(); set004._c.clear(); sc = bpy.context.scene; C = collection('C')
setup_render(sc, 1600, 1000, samples=12, fps=24, frames=1); A.qualita_eevee(preset='equilibrato', riflessi=True, scena=sc, risoluzione=(1600, 1000))
world(sc, top=(0.15, 0.17, 0.22), bottom=(0.15, 0.17, 0.22), strength=0.5); luci.cielo_basso(sc.world, 0.25)
P9.box('Fondo', (0, 2.5, 2), (14, 0.1, 6), material('ALT_fondo', (0.82, 0.8, 0.75), rough=0.9), C)
P9.box('Pav', (0, 0, -0.05), (14, 8, 0.1), material('ALT_pav', (0.5, 0.42, 0.35), rough=0.9), C)
riga = material('ALT_riga', (0.1, 0.1, 0.1), rough=0.9)
RO = rospina.rospina(C, rospina.mats_rospina(), stile='D'); RO['root'].location = (-5.0, 0, 0)
PP = pippo2.build_pippo(C); PP['root'].location = (-1.6, 0, 0)
CS = castora.castora(C, castora.mats_castora(), stile='A'); CS['root'].location = (-3.3, 0, 0)
GU = props009.gualtiero(C, props009.mats009()); GU['root'].location = (1.2, 0, 0)
CA = cp.cappellone(C); CA['root'].location = (5.0, 0, 0)
GN = gn.generale(C, 'A'); GN['root'].location = (3.1, 0, 0)
TB = tumbo.build_tumbo(C, scale=0.75); TB['root'].location = (-0.2, -0.6, 0)
LUCK = bpy.data.fonts.load(A.font('luckiest'), check_existing=True)
for x, h, nome in ((-5.0, 2.075, 'ROSPINA ~158'), (-3.3, 2.234, 'CASTORA ~170'), (-1.6, 2.30, 'PIPPO 175'), (1.2, 2.11, 'GUALTIERO ~160'), (3.1, 2.50, 'GENERALE 190'), (5.0, 2.567, 'CAPPELLONE ~195')):
    o1 = P9.box('Riga', (x, 0.5, h), (1.3, 0.02, 0.025), riga, C)
    o2 = P9._txt(C, 'Nome', nome, 0.17, riga, (x, 0.5, h + 0.16), fnt=LUCK, ext=0.005)
    o1.visible_shadow = o2.visible_shadow = False
cam = bpy.data.objects.new('Cam', bpy.data.cameras.new('Cam')); C.objects.link(cam); sc.camera = cam
cam.location = (0, -14.0, 1.6); luci.punta(cam, Vector((0, 0, 1.4))); cam.data.lens = 38
luci.cinema(C, (0, 0, 1.4), tuple(cam.location), distanza=9.0, lato=1)
luci.ombre_pulite(sc, mezza_risoluzione=False)
sc.render.filepath = os.path.join(QUI, '..', 'schede', 'altezze.png'); bpy.ops.render.render(write_still=True)
from PIL import Image; Image.open(sc.render.filepath).convert('RGB').save(os.path.join(QUI, '..', 'schede', 'altezze.jpg'), quality=90); os.remove(sc.render.filepath); print('FATTA')
