"""Scheda del video 023 (carovita): python scheda023.py carrelli | mani  ->  ../t023/opt/scheda_<quale>.png"""
import sys, os, math
QUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, QUI)
import bpy
from common import *
from render_setup import *
import set004, luci, kitlook, props023
A = kitlook.A; PI = math.pi
QUALE = sys.argv[-1]
reset_scene(); scene = bpy.context.scene; C = collection('C')
W, H = 1500, 640
setup_render(scene, W, H, samples=8, fps=24, frames=1)
A.qualita_eevee(preset='equilibrato', riflessi=True, scena=scene, risoluzione=(W, H))
A.cielo('NightSkyHDRI008', forza=0.6, rotazione=0.0, ris='2k') if QUALE == 'mani' else A.cielo('sunflowers_puresky', forza=0.8, rotazione=43.0, ris='2k')
luci.cielo_basso(scene.world, 0.3)
pav = material('Pav', (0.18, 0.18, 0.2), rough=0.6, metallic=0.2); set004.bx('Pav', (-60, -60, -0.3), (60, 60, 0.0), pav, C)
cam = bpy.data.objects.new('Cam', bpy.data.cameras.new('Cam')); C.objects.link(cam); scene.camera = cam
FONT = bpy.data.fonts.load(A.font('luckiest'))
gia = material('Tx', (1, 0.85, 0.3), rough=0.5, emit=(1, 0.8, 0.25), emit_strength=1.5)
if QUALE == 'carrelli':
    for k, (t, x) in enumerate((('kenney', -1.9), ('filo', 0.0), ('hover', 1.9))):
        r = props023.carrello(C, t, A); r.location = (x, 0, 0); r.rotation_euler = (0, 0, -0.6)
        props023.testo(C, 'L', 'ABC'[k], 0.32, gia, (x, -1.0, 0.05), rot=(PI / 2.3, 0, 0), font=FONT)
    cam.location = (0, -6.0, 1.9); luci.punta(cam, (0, 0, 0.55)); cam.data.lens = 36
    luci.cinema(C, (0, 0, 0.6), cam.location, forza=0.35)
else:
    for k, (t, x) in enumerate((('alieno', -3.2), ('guanto', 0.0), ('robot', 3.2))):
        D = props023.mano(C, t); D['radice'].location = (x, 0, 1.9); D['radice'].rotation_euler = (0.35, 0, 0.7)
        props023.piega(D, 1, 0.55)
        props023.testo(C, 'L', 'DEF'[k], 0.5, gia, (x, -1.2, 0.05), rot=(PI / 2.3, 0, 0), font=FONT)
    cam.location = (0, -10.5, 2.6); luci.punta(cam, (0, 0, 2.0)); cam.data.lens = 34
    luci.cinema(C, (0, 0, 2.0), cam.location, forza=0.7)
os.makedirs(os.path.join(QUI, '../t023/opt'), exist_ok=True)
scene.render.filepath = os.path.abspath(os.path.join(QUI, '../t023/opt/scheda_%s.png' % QUALE)); bpy.ops.render.render(write_still=True); print('FATTO', scene.render.filepath)
