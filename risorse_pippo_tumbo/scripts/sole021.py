"""Scheda del sole realistico per il video 021: il quartiere in fiamme con il sole incastrato sul tetto di Pippo, tre tipi di sole.
Uso: python sole021.py A   (oppure B, C) -> ../t021/opt/sole_A.png  (540x960)"""
import sys, os
TIPO = sys.argv[-1] if sys.argv[-1] in ('A', 'B', 'C') else 'A'
HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
src = open(os.path.join(HERE, '../templates/head.py')).read()
exec(compile(src, 'head.py', 'exec'))
import kitlook, props021, luci, paesaggi
A = kitlook.A
scene.view_settings.exposure = 0.0
camd = bpy.data.cameras.new('Cam'); cam = bpy.data.objects.new('Cam', camd); cac.objects.link(cam); scene.camera = cam
cam.location = (3.6, -12.5, 1.3); camd.lens = 22; camd.clip_end = 900
luci.punta(cam, (0.0, 4.0, 6.2))
props021.bagliore(scene)
props021.cielo_rosso(scene.world, 0.45); props021.quartiere_bruciato(M, scene)
S = props021.sole(prc, (0.0, 11.0, 10.8), 5.4, TIPO)
props021.anima_sole(S, 1, 0.0)
sunl.color = (1.0, 0.55, 0.25); sunl.energy = 3.0; so.rotation_euler = (math.radians(62), 0, math.radians(180))
posti = [(-17.5, 3.0, 6.0), (-8.0, 27.0, 5.5), (10.0, 27.5, 5.0), (22.0, 6.0, 5.0), (22.5, -2.0, 4.0), (-27.0, -1.0, 6.0), (9.5, 4.0, 2.4), (-13.0, 9.5, 2.4), (5.5, 15.5, 2.6), (-7, 16.5, 2.6), (16, 14, 2.4), (-30, 14, 2.4), (3.6, 7.3, 4.6), (-3.2, 7.4, 4.4), (-7.5, -1.5, 0), (8.0, -2.5, 0), (-12.5, 4.0, 0)]
props021.incendio(A, prc, posti, 1.3)
import pippo2 as pippo, tumbo
P = pippo.build_pippo(chc); P['root'].location = (1.6, -4.0, 0); P['root'].rotation_euler = (0, 0, 0.25)
for nm in 'LR': P['shoulder' + nm].rotation_mode = 'QUATERNION'
from mathutils import Vector as V
P['shoulderL'].rotation_quaternion = V((0, 0, -1)).rotation_difference(V((-0.45, -0.3, 0.85))); P['shoulderR'].rotation_quaternion = V((0, 0, -1)).rotation_difference(V((0.45, -0.3, 0.85)))
pippo.express(P, 1, brow=-1.0, brow_lift=1.0, mouth_open=1.0, smile=-0.8)
Tb = tumbo.build_tumbo(chc, scale=0.75); Tb['root'].location = (-0.6, -4.6, 0); Tb['root'].rotation_euler = (0, 0, -0.5)
L = luci.cinema(prc, (1.0, -4.2, 1.1), (3.6, -12.5, 1.5), lato=-1, forza=0.45)
for k, (x, y, rz, fa) in enumerate(((-3.8, -5.0, -1.4, 0.0), (5.6, -6.2, 1.3, 1.3), (-2.0, 1.5, -1.6, 2.1), (4.6, 2.5, 1.5, 0.7), (-6.5, -2.5, -1.2, 2.8))):
    C_ = props021.comparsa(A, chc, (x, y, 0), rz, seme=k, fase=fa, nome='Comp%d' % k); props021.corri(C_, 1, 0.0)
setup_render(scene, 540, 960, samples=4, fps=24, frames=1); scene.frame_set(1)
os.makedirs('../t021/opt', exist_ok=True); scene.render.filepath = os.path.abspath('../t021/opt/sole_%s.png' % TIPO)
bpy.ops.render.render(write_still=True); print('FATTO', scene.render.filepath)
