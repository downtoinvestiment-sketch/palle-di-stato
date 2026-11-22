"""Scheda degli oggetti del video 021 «L'etciù».
Uso: python scheda021.py camion  -> camion che scarica il pepe (A, B, C)
     python scheda021.py oggetti -> pepe, sacco, valigia, lampadario, cornice, cuscino (con lettere)
Immagini in ../t021/opt/"""
import sys, os, math
QUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, QUI)
import bpy
from common import *
from render_setup import *
import set004, props009, luci, kitlook
A = kitlook.A; PI = math.pi
QUALE = sys.argv[-1]
reset_scene(); scene = bpy.context.scene; C = collection('C')
W, H = (1200, 520) if QUALE == 'camion' else (1400, 760)
setup_render(scene, W, H, samples=8, fps=24, frames=1)
A.qualita_eevee(preset='equilibrato', riflessi=False, scena=scene, risoluzione=(W, H))
A.cielo('sunflowers_puresky', forza=1.0, rotazione=43.0, ris='2k'); luci.cielo_basso(scene.world, 0.35)
pav = material('Pav', (0.22, 0.2, 0.19), rough=0.9); set004.bx('Pav', (-40, -40, -0.3), (40, 40, 0.0), pav, C)
cam = bpy.data.objects.new('Cam', bpy.data.cameras.new('Cam')); C.objects.link(cam); scene.camera = cam
FONT = bpy.data.fonts.load(A.font('luckiest'))
def etichetta(t, loc, size=0.7):
    cu = bpy.data.curves.new('T', 'FONT'); cu.body = t; cu.font = FONT; cu.size = size; cu.align_x = 'CENTER'; cu.extrude = 0.03
    o = bpy.data.objects.new('T', cu); C.objects.link(o); o.location = loc; o.rotation_euler = (PI / 2, 0, 0)
    o.data.materials.append(material('Tx', (1, 0.85, 0.3), rough=0.5, emit=(1, 0.8, 0.25), emit_strength=1.5))
if QUALE == 'camion':
    M9 = props009.mats009()
    t = props009.truck(C, M9)[0]; t.location = (-7.5, 0, 0); t.rotation_euler = (0, 0, -0.5)
    A.modello('kenney/retro-urban-kit/truck-grey-cargo', posizione=(0, 0, 0), rotazione=-30, altezza=3.2, collezione=C, appoggia=True)
    A.modello('kenney/toy-car-kit/vehicle-truck', posizione=(7.5, 0, 0), rotazione=-30, altezza=3.2, collezione=C, appoggia=True)
    for x, l in ((-7.5, 'A'), (0, 'B'), (7.5, 'C')): etichetta(l, (x, -3.2, 0.1), 1.2)
    cam.location = (0, -22, 6); luci.punta(cam, (0, 0, 1.5)); cam.data.lens = 40
    luci.cinema(C, (0, 0, 1.5), cam.location, forza=1.2)
else:
    voci = [('D', 'kenney/food-kit/shaker-pepper', 1.0), ('E', 'kenney/food-kit/pepper-mill', 1.0), ('F', 'kaykit/medieval-hexagon-pack/sack', 0.9),
            ('G', 'vintage_suitcase', 0.6), ('H', 'Chandelier_01', 1.1), ('I', 'Chandelier_03', 1.1), ('L', 'fancy_picture_frame_01', 0.9), ('M', 'throw_pillows_01', 0.7)]
    for k, (l, aid, h) in enumerate(voci):
        x = (k % 4 - 1.5) * 2.6; z = 2.4 if k < 4 else 0.3
        try:
            if aid.startswith('Chandelier'): o = A.modello(aid, posizione=(x, 0, z + 1.7), scala=1.0, collezione=C, appoggia=False)
            else: o = A.modello(aid, posizione=(x, 0, z), altezza=h, collezione=C, appoggia=True)
        except Exception as e: print('ERRORE', aid, e)
        etichetta(l, (x - 0.95, -0.8, z + 0.05), 0.4)
        set004.bx('Mensola', (x - 1.1, -0.7, z - 0.08), (x + 1.1, 0.7, z), material('Mens', (0.5, 0.35, 0.22), rough=0.7), C)
    cam.location = (0, -11, 3.0); luci.punta(cam, (0, 0, 1.6)); cam.data.lens = 34
    luci.cinema(C, (0, 0, 1.4), cam.location, forza=0.7)
scene.render.filepath = os.path.abspath(os.path.join(QUI, '../t021/opt/scheda_%s.png' % QUALE)); bpy.ops.render.render(write_still=True); print('FATTO', scene.render.filepath)
