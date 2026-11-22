"""Scheda del video 023 (carovita): il quartiere impacchettato sullo scaffale dello spazio, tre confezioni (G blister, H vaschetta, I barattolo),
e il fotogramma del cielo che si strappa con la mano gigante (L). Uso: python italia023.py  ->  ../t023/opt/italia_*.png (540x960)"""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
src = open(os.path.join(HERE, '../templates/head.py')).read()
exec(compile(src, 'head.py', 'exec'))
import kitlook, luci, props023, set004 as S4
A = kitlook.A
FONT = bpy.data.fonts.load(A.font('luckiest'))
setup_render(scene, 540, 960, samples=4, fps=24, frames=1)
scene.view_settings.exposure = 0.0
camd = bpy.data.cameras.new('Cam'); cam = bpy.data.objects.new('Cam', camd); cac.objects.link(cam); scene.camera = cam; camd.clip_end = 5000
import pippo2 as pippo
P = pippo.build_pippo(chc); P['root'].location = (2.0, -4.5, 0); P['root'].rotation_euler = (0, 0, 0.3)
P['head'].rotation_euler = (-0.45, 0, 0)
for nm in 'LR': P['shoulder' + nm].rotation_mode = 'QUATERNION'
P['shoulderL'].rotation_quaternion = Vector((0, 0, -1)).rotation_difference(Vector((-0.5, -0.3, 0.8))); P['shoulderR'].rotation_quaternion = Vector((0, 0, -1)).rotation_difference(Vector((0.5, -0.3, 0.8)))
pippo.express(P, 1, brow=-1.0, brow_lift=1.0, mouth_open=1.3, smile=-0.8)

# ---------------------------------------------------------------- 1) il cielo che si strappa (si vede dalla strada)
RIP_C = Vector((-2.0, 95.0, 62.0)); CAM_S = Vector((4.6, -11.5, 0.7))
RIP = props023.strappo(prc, tuple(RIP_C), 42.0, verso=tuple((CAM_S - RIP_C).normalized()))
H1 = props023.mano(prc, 'alieno'); H1['radice'].scale = (32,) * 3
_dv = (CAM_S - RIP_C).normalized(); _dir = (_dv + Vector((0, 0, -0.9))).normalized()
H1['radice'].location = RIP_C + _dv * 14; H1['radice'].rotation_mode = 'QUATERNION'; H1['radice'].rotation_quaternion = Vector((0, 0, 1)).rotation_difference(_dir)
props023.piega(H1, 1, 0.25)
L1 = luci.cinema(prc, (2.0, -4.5, 1.6), tuple(CAM_S), distanza=4.0, lato=-1, forza=0.6)
cam.location = CAM_S; luci.punta(cam, (0.5, 20.0, 24.0)); camd.lens = 17
scene.frame_set(1); scene.render.filepath = os.path.abspath('../t023/opt/italia_L_strappo.png'); bpy.ops.render.render(write_still=True); print('FATTO L')
for o in [RIP] + list(RIP.children_recursive) + [H1['radice']] + list(H1['radice'].children_recursive) + list(L1.values()): o.hide_render = True

# ---------------------------------------------------------------- 2) il quartiere impacchettato sullo scaffale dello spazio
for o in list(bpy.data.objects):                                                   # via nuvole e tutto quello che esce dalla confezione
    if o.name.startswith(('CloudW', 'Puff')): bpy.data.objects.remove(o, do_unlink=True)
LIM = (66.0, 72.0)
for o in list(envc.objects) + list(prc.objects):
    if o.type != 'MESH' or o.parent is not None: continue
    if o.data is S4.box0():                                                         # le scatole lunghe (prato, strada, marciapiedi) si accorciano
        x0, x1 = o.location.x, o.location.x + o.scale.x; y0, y1 = o.location.y, o.location.y + o.scale.y
        x0, x1 = max(x0, -LIM[0]), min(x1, LIM[0]); y0, y1 = max(y0, -LIM[1]), min(y1, LIM[1])
        if x1 <= x0 or y1 <= y0: bpy.data.objects.remove(o, do_unlink=True); continue
        o.location.x, o.scale.x, o.location.y, o.scale.y = x0, x1 - x0, y0, y1 - y0
    elif abs(o.location.x) > LIM[0] or abs(o.location.y) > LIM[1]: bpy.data.objects.remove(o, do_unlink=True)
A.cielo('NightSkyHDRI008', forza=0.5, rotazione=40.0, ris='2k'); luci.cielo_basso(scene.world, 0.12)
sunl.energy = 1.2
SC = props023.scaffale(prc, FONT, y=0.0, piani=(0.0, 175.0), prof=118.0)
CONF = {t: props023.confezione(prc, t, FONT) for t in ('blister', 'vaschetta', 'barattolo')}
H2 = props023.mano(prc, 'alieno'); H2['radice'].scale = (55,) * 3; H2['radice'].location = (38.0, -70.0, 128.0); H2['radice'].rotation_euler = (PI - 0.35, 0.0, -0.5)
props023.piega(H2, 1, 0.35)
L2 = luci.cinema(prc, (0, 0, 25), (70, -280, 45), distanza=260.0, lato=1, forza=0.3)
scene.view_settings.exposure = -0.4
for o in SC.children:
    if o.name.startswith('ScaFondo'): o.material_slots[0].material = material('P23_fondoScuro', (0.12, 0.13, 0.16), rough=0.5)
for nm, (lettera, t) in enumerate((('G', 'blister'), ('H', 'vaschetta'), ('I', 'barattolo'))):
    for k, r in CONF.items():
        for o in [r] + list(r.children_recursive): o.hide_render = (k != t)
    cam.location = (70.0, -280.0, 45.0); luci.punta(cam, (2.0, 0.0, 48.0)); camd.lens = 30
    scene.frame_set(1); scene.render.filepath = os.path.abspath('../t023/opt/italia_%s_%s.png' % (lettera, t)); bpy.ops.render.render(write_still=True); print('FATTO', lettera)
