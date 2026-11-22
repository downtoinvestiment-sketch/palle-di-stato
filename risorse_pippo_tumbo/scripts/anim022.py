"""TESTA STANDARD di ogni episodio: mondo, quartiere (casa di Pippo a est, casa di Gualtiero a ovest, staccionata, strada), funzioni house_at / tower_at / tree.
Uso: cat templates/head.py scripts/animNNN_body.py > scripts/animNNN.py  (cambia TOTAL e gli import prima).
Test NNN - TITOLO. Salva ../tNNN/pippo_tNNN.blend
Personaggi: Pippo e Tumbo ESISTENTI (pippo.py, tumbo.py) invariati; Gualtiero = nuovo vicino ricorrente (props009.gualtiero)."""
import sys, math, os
sys.path.insert(0, os.path.dirname(__file__))
import bpy, numpy as np
from mathutils import Vector, Euler, Matrix
from common import *
from render_setup import *
import set004, props004, props007, props009, props010, props012, props013, props015, props016b, kitlook, lookdev, pippo, tumbo
from set004 import obj, bx, cyl, ball_, MB

FPS = 24; TOTAL = 49.6; NF = int(TOTAL * FPS)
def fr(t): return max(1, int(round(t * FPS)) + 1)
def sm(x): x = min(1.0, max(0.0, x)); return x * x * (3 - 2 * x)
def ramp(t, a, b): return sm((t - a) / (b - a))
def lerp(a, b, u): return tuple(a[i] + (b[i] - a[i]) * u for i in range(len(a)))
def add(a, b): return tuple(a[i] + b[i] for i in range(3))
PI = math.pi

reset_scene(); scene = bpy.context.scene
setup_render(scene, 1080, 1920, samples=16, fps=FPS, frames=NF); scene.frame_end = NF
scene.eevee.shadow_resolution_scale = 0.25
rng = np.random.default_rng(41)
M = set004.make_mats(); N = props007.mats007(); G9 = props009.mats009()
envc = collection('Env'); chc = collection('Characters'); prc = collection('Props'); cac = collection('Cameras')

# ======================= mondo =======================
w = bpy.data.worlds.new('World'); scene.world = w; w.use_nodes = True; nt = w.node_tree; nt.nodes.clear()
tc = nt.nodes.new('ShaderNodeTexCoord'); sp = nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(tc.outputs['Generated'], sp.inputs[0])
rp = nt.nodes.new('ShaderNodeValToRGB'); nt.links.new(sp.outputs['Z'], rp.inputs['Fac'])
rp.color_ramp.elements[0].position = 0.0; rp.color_ramp.elements[0].color = (0.46, 0.80, 1.0, 1)
rp.color_ramp.elements[1].position = 0.75; rp.color_ramp.elements[1].color = (0.04, 0.34, 1.0, 1)
bg = nt.nodes.new('ShaderNodeBackground'); bg.inputs['Strength'].default_value = 0.7; nt.links.new(rp.outputs['Color'], bg.inputs['Color'])
bgc = nt.nodes.new('ShaderNodeBackground'); bgc.inputs['Strength'].default_value = 1.0; nt.links.new(rp.outputs['Color'], bgc.inputs['Color'])
lpn = nt.nodes.new('ShaderNodeLightPath'); mxs = nt.nodes.new('ShaderNodeMixShader'); out = nt.nodes.new('ShaderNodeOutputWorld')
nt.links.new(lpn.outputs['Is Camera Ray'], mxs.inputs[0]); nt.links.new(bg.outputs['Background'], mxs.inputs[1]); nt.links.new(bgc.outputs['Background'], mxs.inputs[2])
nt.links.new(mxs.outputs[0], out.inputs['Surface'])
sunl = bpy.data.lights.new('Sun', 'SUN'); so = bpy.data.objects.new('Sun', sunl); prc.objects.link(so)
so.rotation_euler = (math.radians(48), math.radians(6), math.radians(28)); sunl.angle = math.radians(1.2); sunl.energy = 3.9; sunl.color = (1, 0.95, 0.85)
M['cloudw'] = material('S_cloudw', (1, 1, 1), rough=1.0, emit=(1, 1, 1), emit_strength=0.55)
M['dust'] = material('S_dust', (0.93, 0.88, 0.78), rough=1.0, emit=(0.9, 0.85, 0.75), emit_strength=0.3)
_cr = np.random.default_rng(11)
for k in range(26):
    an = k / 26 * 2 * PI + _cr.uniform(-0.15, 0.15); rr = _cr.uniform(90, 150); s_ = _cr.uniform(4.0, 7.5)
    cw = empty('CloudW', (rr * math.cos(an), rr * math.sin(an), _cr.uniform(24, 70)), None, prc)
    for (dx, dy, dz, r_) in [(0, 0, 0, 1.5), (1.5, 0.3, -0.2, 1.15), (-1.5, -0.2, -0.25, 1.2), (0.6, -0.5, 0.6, 1.1), (-0.6, 0.5, 0.5, 1.0), (2.6, 0, -0.45, 0.75), (-2.7, 0, -0.5, 0.8)]:
        c_, s2 = math.cos(an + PI / 2), math.sin(an + PI / 2)
        ball_('Puff', r_ * s_, (dx * s_ * c_, dx * s_ * s2 + dy, dz * s_), M['cloudw'], prc, parent=cw, sc=(1, 1, 0.6))

# ======================= ambiente: i giardini di Pippo (est) e di Gualtiero (ovest), la strada a sud =======================
bx('Prato', (-140, -140, -0.30), (140, 140, 0.0), M['park'], envc)
bx('Strada', (-140, -13.2, 0.0), (140, -8.4, 0.02), M['asphalt'], envc); bx('Marciapiede', (-140, -8.4, 0.0), (140, -7.9, 0.05), M['sidewalk'], envc)
for x in range(-60, 60, 4): bx('Linea', (x, -10.9, 0.02), (x + 1.8, -10.75, 0.025), M['frame'], envc)
def house_at(x, y, rotz, wi, ri, si, two, w=None, d=None):
    w = w or rng.uniform(4.6, 5.6); d = d or rng.uniform(4.0, 4.8)
    mb = MB(set004.house_mats(M, wi, ri, si)); set004.house_geo(mb, w, d, 4.5 if two else 2.9, two, rng); return mb.build('Casa', envc, (x, y, 0), rotz)
house_at(0.0, 9.5, 0.0, 0, 0, 1, True, 6.5, 4.5)                                                  # casa di Pippo
house_at(-17.5, 3.0, PI / 2, 3, 0, 0, True, 5.6, 4.6)                                              # casa di Gualtiero
for x in range(-34, 44, 9): house_at(x + rng.uniform(-1, 1), 27 + rng.uniform(0, 2), 0.0, int(rng.integers(0, 6)), int(rng.integers(0, 4)), int(rng.integers(0, 5)), bool(rng.integers(0, 2)))
for x in range(-34, 44, 9): house_at(x + rng.uniform(-1, 1), -35 - rng.uniform(0, 2), PI, int(rng.integers(0, 6)), int(rng.integers(0, 4)), int(rng.integers(0, 5)), bool(rng.integers(0, 2)))
for y in range(-2, 20, 9): house_at(21 + rng.uniform(0, 2), y, -PI / 2, int(rng.integers(0, 6)), int(rng.integers(0, 4)), int(rng.integers(0, 5)), bool(rng.integers(0, 2)))
house_at(-27, -1.0, PI / 2, 2, 1, 2, True)
def tower_at(x, y, rz=0.0):
    tw = rng.uniform(3.6, 4.6); ti = int(rng.integers(0, len(M['tower']))); h = rng.uniform(11, 26)
    mb = MB([M['tower'][ti], M['window'], M['frame'], M['concrete'], M['dark'], M['shutter'][int(rng.integers(0, 5))]])
    set004.tower_geo(mb, tw, h, rng); mb.build('Palazzo', envc, (x, y, 0), rz)
for x in range(-48, 56, 11): tower_at(x, 42 + rng.uniform(0, 4), 0.0); tower_at(x + 4, -50 - rng.uniform(0, 4), PI)
for y in range(-30, 36, 11): tower_at(40 + rng.uniform(0, 3), y, -PI / 2); tower_at(-42 - rng.uniform(0, 3), y, PI / 2)
def tree(x, y, s=1.0):
    cyl('Tronco', 0.16 * s, 1.5 * s, (x, y, 0.75 * s), M['bark'], envc)
    for (dx, dy, dz, r) in ((0, 0, 2.1, 0.95), (0.5, 0.1, 1.75, 0.7), (-0.5, -0.1, 1.8, 0.72)):
        ball_('Chioma', r * s, (x + dx * s, y + dy * s, dz * s), M['leaf'][int(rng.integers(0, 3))], envc)
for (x, y) in ((9.5, 4.0), (10.0, -5.5), (-13.0, 9.5), (5.5, 15.5), (-7, 16.5), (16, 14), (-30, 14), (-21, -6.0), (14, -19), (-24, -19)): tree(x, y, rng.uniform(1.0, 1.5))
fm = MB([M['frame']])
for yy in np.arange(-7.6, 8.01, 0.22): fm.box((-9.2, yy, 0.42), (0.04, 0.10, 0.84), 0); fm.box((-9.2, yy, 0.86), (0.04, 0.07, 0.08), 0)
for zz in (0.25, 0.60): fm.box((-9.23, 0.2, zz), (0.03, 15.7, 0.06), 0)
fm.build('Staccionata', envc)


# ===================================================================================================================
# Video 022 - IL BARATTOLO DI CETRIOLINI (copione 15, versione 4), 49,6 s. Si unisce alla testa:
#   testa = templates/head.py con TOTAL = 49.6 ; corpo = questo file
# Voce: audio/voce_t022.mp3, tagliata (senza figlio zucchina e senza Luna) e accelerata 1,1x. Parolacce in ogni frase: eccezione
# voluta dall'autore per questo episodio. Scelte dell'autore (17 novembre 2026): barattolo B1 alto a quadretti, cetriolino C1 lungo,
# elefante E1 grigio, razzo R1 vero (Saturn V del kit NASA). Pippo usa SOLO le emozioni esagerate di pippo2. Luce «cinema».
# ===================================================================================================================
import props022, props019, eleonora, luci, random
import pippo2 as pippo
A = kitlook.A
BLEND = os.environ.get('BLEND022', '../t022/pippo_t022.blend')
FONT = A.font('luckiest')
Q = props022.mats022(); Q19 = props019.mats019(); Z12 = props012.mats012()

# ======================= tempi (da audio/words_t022.json) =======================
T_LIFT0 = 4.6                                   # nell'hook il razzo si stacca da terra
T_PERCHE = 7.16                                 # «Perche' quel cazzo di coperchio...» (si torna indietro, in cucina)
T_MANI = 11.46; T_DENTI = 13.70                 # mani; denti di Tumbo
T_MART = 16.76; T_CAMION = 18.44; T_ELEF = 19.62; T_NIENTE = 22.2
T_ALLORA = 23.2; T_RAZZO = 24.28                # «e allora cazzo, RAZZO cazzo!»
T_POI = 25.98; T_SVITA = 28.38; T_SOLO = 29.74  # il barattolo ricade; il coperchio si svita da solo
T_MACHE = 31.34; T_DENTRO = 33.0; T_MUTANDE = 34.92
T_AMANTE = 37.04                                # «E' il cazzo di amante di Eleonora»
T_QUEL = 40.3; T_CHIUDE = 43.02                 # Pippo entra nel barattolo e si chiude dentro
T_STAVOLTA = 44.38; T_FINE = 48.9

# ======================= rendering, camera, luce =======================
setup_render(scene, 1080, 1920, samples=5, fps=FPS, frames=NF); scene.frame_end = NF
camd = bpy.data.cameras.new('Cam'); cam = bpy.data.objects.new('Cam', camd); cac.objects.link(cam); scene.camera = cam
camd.clip_start = 0.03; camd.clip_end = 1500; camd.sensor_width = 36
tgt = empty('CamTarget', (0, 0, 1), None, cac)
ct = cam.constraints.new('TRACK_TO'); ct.target = tgt; ct.track_axis = 'TRACK_NEGATIVE_Z'; ct.up_axis = 'UP_Y'
camd.dof.use_dof = True; camd.dof.focus_object = tgt
kitlook.upgrade(scene, M, envc, prc, extras=False)
scene.eevee.taa_render_samples = 5
luci.cielo_basso(scene.world, 0.4)
scene.world.use_sun_shadow = False
SUN = luci.sole(prc, (0.25, -0.97), lato=1, energia=4.5)
luci.ombre_pulite(scene, mezza_risoluzione=True)
kitlook.variants('grass_medium_01', 12, (-5.0, 4.0, -7.0, 2.0), (0.14, 0.24), seed=4, coll=envc, shadow=False)
kitlook.variants('dandelion_01', 10, (-5.0, 4.0, -7.0, 2.0), (0.09, 0.15), seed=6, coll=envc, shadow=False)

# ======================= posti =======================
PAD = Vector((6.5, 1.5, 0.0)); R_H = 11.0                   # il Saturn V nel giardino di Pippo
TABLE = Vector((-1.0, -2.0, 0.0)); TAB_H = 0.75              # tavolino per il martello
JAR_G = Vector((-2.5, -3.6, 0.0))                            # barattolo sul prato (camion, elefante)
JAR_L = Vector((-1.0, -3.0, 0.0))                            # dove ricade dallo spazio
P_HOOK = Vector((3.6, -3.6, 0)); T_HOOKP = Vector((4.5, -4.0, 0))
P_L = Vector((0.35, -2.35, 0)); T_LP = Vector((0.45, -3.7, 0)); ELE = Vector((1.45, -1.25, 0))
KX = 600.0; KJ = Vector((KX, 0.4, 0.9))                       # cucina (set lontano): barattolo sul tavolo
P_K = Vector((KX, 1.2, 0)); T_K = Vector((KX + 0.95, 1.05, 0))

def qdir(d, rest=(0, 0, -1)): return Vector(rest).rotation_difference(Vector(d).normalized())
def yaw_to(a, b): return math.atan2(b[0] - a[0], -(b[1] - a[1]))
def walk(t, t0, t1, a, b):
    u = ramp(t, t0, t1); return a.lerp(b, u), (0.5 * math.sin(t * 11) if 0.0 < u < 1.0 else 0.0)

# ======================= cucina =======================
KIT = empty('Cucina', (KX, 0, 0), None, prc)
try: kw = A.materiale('Wallpaper002A', dimensione=1.6)
except Exception: kw = material('P22_muro', (0.85, 0.8, 0.6), rough=0.9)
try: kf = A.materiale('Tiles074', dimensione=1.2)
except Exception: kf = material('P22_pav', (0.8, 0.8, 0.8), rough=0.5)
for nm, p0, p1, m_ in (('KPav', (-4, -4, -0.1), (4, 3, 0.0), kf), ('KMuro', (-4, 2.6, 0), (4, 2.8, 3.2), kw), ('KMuroS', (-4.2, -4, 0), (-4.0, 3, 3.2), kw),
                       ('KMuroD', (4.0, -4, 0), (4.2, 3, 3.2), kw), ('KSoffitto', (-4.2, -4, 3.2), (4.2, 3, 3.3), material('P22_soff', (0.95, 0.95, 0.92), rough=1.0))):
    o = set004.bx(nm, (KX + p0[0], p0[1], p0[2]), (KX + p1[0], p1[1], p1[2]), m_, prc); o.parent = None
KT_ = set004.bx('KTavolo', (KX - 0.75, -0.15, 0.0), (KX + 0.75, 0.95, 0.9), A.materiale('wood_table_worn', dimensione=1.0), prc)
KCOUNTER = set004.bx('KBancone', (KX - 3.6, 2.0, 0.0), (KX + 3.6, 2.6, 0.95), material('P22_banco', (0.55, 0.75, 0.85), rough=0.5), prc)
KOBJ = []
for aid, x, h in (('kenney/furniture-kit/kitchenFridgeLarge', -3.0, 2.3), ('kenney/furniture-kit/kitchenStove', 1.2, 1.0), ('kenney/furniture-kit/kitchenSink', -1.0, 1.0)):
    try: KOBJ.append(props016b.kplace(A, aid, prc, KX + x, 2.3, s=2.6, rot=180))
    except Exception as e: print('cucina', aid, e)

# ======================= oggetti =======================
def jar(nome, pieno=True):
    J = props022.barattolo(prc, Q, 'B1', H=0.9, font=FONT, pieno=pieno); J['root'].name = nome; J['root'].rotation_mode = 'XYZ'; J['lid'].rotation_mode = 'XYZ'; return J
JK = jar('BarattoloCucina'); JK['root'].location = tuple(KJ)
JG = jar('BarattoloGiardino'); JR = jar('BarattoloRazzo'); JL = jar('BarattoloCaduto')
JH = JK['h']
TAB = set004.bx('TavoloGiardino', (TABLE.x - 0.5, TABLE.y - 0.4, 0), (TABLE.x + 0.5, TABLE.y + 0.4, TAB_H), A.materiale('wood_table_worn', dimensione=1.0), prc)
TAPE = props022.nastro(prc, Q, JR['root'], JR['R'], JR['h'])
ROCKET = A.modello('nasa/saturn-v', posizione=tuple(PAD), altezza=R_H, collezione=prc, max_triangoli=150000); ROCKET.rotation_mode = 'XYZ'
R0 = Vector(ROCKET.location)
FLAME = ball_('FiammaRazzo', 1.0, (0, 0, -50), material('P22_fiamma', (1.0, 0.5, 0.05), rough=1.0, emit=(1.0, 0.45, 0.05), emit_strength=8.0), prc, sc=(0.9, 0.9, 2.4))
TRUCK = A.modello('kenney/car-kit/truck', posizione=(0, 0, 0), altezza=3.2, collezione=prc, appoggia=True); TRUCK.rotation_mode = 'XYZ'
EL = props022.elefante(chc, Q, 'E1', H=3.6); EL['root'].rotation_mode = 'XYZ'
EL['body'].rotation_euler = (-0.75, 0, 0)
for lg in EL['legs'][:2]: lg.rotation_euler = (-0.35, 0, 0)
for lg in EL['legs'][2:]: lg.rotation_euler = (0.45, 0, 0)
for sg in EL['trunk']: sg.rotation_mode = 'XYZ'
EL_YAW = 0.45
EL['root'].location = (0, 0, 0); EL['root'].rotation_euler = (0, 0, EL_YAW); bpy.context.view_layer.update()
EL_REAR = EL['body'].matrix_world @ Vector((0, 1.6, -0.75))             # il sedere, con la radice nell'origine
EL_SIT = Vector((JAR_G.x - EL_REAR.x, JAR_G.y - EL_REAR.y, JH + 0.12 - EL_REAR.z))
CT = props022.cetriolino(chc, Q, 'C1', H=0.62); CT['root'].rotation_mode = 'XYZ'
ZE = eleonora.zucchina(chc, Z12); ZE['root'].rotation_mode = 'XYZ'; eleonora.velo(ZE, False)
HAMMER = empty('Martello', (0, 0, 0), None, chc)
cyl('MartelloManico', 0.03, 0.55, (0, 0, -0.2), material('P22_legno', (0.45, 0.25, 0.1), rough=0.6), chc, parent=HAMMER)
props019.box('MartelloTesta', (0, 0, -0.5), (0.3, 0.12, 0.12), Q['steel'], chc, parent=HAMMER)
REMOTE = empty('Telecomando', (0, 0, 0), None, chc)
props019.box('TelecomandoCorpo', (0, 0, -0.1), (0.1, 0.05, 0.2), Q19['dark'], chc, parent=REMOTE)
ball_('TelecomandoBottone', 0.035, (0, -0.03, -0.05), Q19['bred'], chc, parent=REMOTE)
bx('Buio', (1998, -2, -2), (2002, 2, 2), material('P22_buio', (0, 0, 0), rough=1.0), envc)

# ======================= personaggi =======================
P = pippo.build_pippo(chc); Tb = tumbo.build_tumbo(chc, scale=0.75)
for r in (P['root'], Tb['root']): r.rotation_mode = 'XYZ'
for nm in 'LR': P['shoulder' + nm].rotation_mode = 'QUATERNION'
HAMMER.parent = P['elbowR']; HAMMER.location = (0, 0, -0.1); HAMMER.rotation_euler = (0, 0, 0)
REMOTE.parent = P['elbowR']; REMOTE.location = (0, 0, -0.08)
HELMET = ball_('Casco', 1.0, (0, 0.03, 0.74), Q['rockW'], chc, parent=P['head'], sc=(0.47, 0.47, 0.24))
GOG = empty('Occhialini', (0, -0.42, 0.62), Tb['root'], chc)
for sx in (-1, 1): ball_('Occhialino', 0.09, (sx * 0.14, 0, 0), Q['glassW'], chc, parent=GOG, sc=(1, 0.5, 1))

# ======================= visibilita' =======================
def desc(o):
    for c in o.children:
        yield c
        yield from desc(c)
NEVER = set()
def show(o, intervals):
    for q in [o] + list(desc(o)):
        if q.name in NEVER: continue
        first = intervals[0][0] <= 0.0
        q.hide_render = not first; q.keyframe_insert('hide_render', frame=1)
        for (a, b) in intervals:
            if a > 0.0: q.hide_render = False; q.keyframe_insert('hide_render', frame=fr(a))
            if b < TOTAL: q.hide_render = True; q.keyframe_insert('hide_render', frame=fr(b))
def show_only(o, intervals):
    show(o, intervals)
    for q in [o] + list(desc(o)): NEVER.add(q.name)
show_only(JK['hand'], [(8.15, 8.55), (12.15, 12.5)])                     # indizio: la manina verde che tiene il coperchio
for J_ in (JG, JR, JL): show_only(J_['hand'], [(TOTAL + 1, TOTAL + 2)])
show_only(HAMMER, [(T_MART, T_CAMION)]); show_only(REMOTE, [(0.0, T_PERCHE), (T_ALLORA, T_POI)])
show_only(HELMET, [(0.0, T_PERCHE), (T_ALLORA, T_POI)]); show_only(GOG, [(0.0, T_PERCHE), (T_ALLORA, T_POI)])
show(JK['root'], [(T_PERCHE, T_MART)])
show(JG['root'], [(T_MART, T_ALLORA)])
show(JR['root'], [(0.0, T_PERCHE), (T_ALLORA, T_POI)])
show(JL['root'], [(T_POI, TOTAL)])
show(TAB, [(T_MART, T_CAMION)])
show(ROCKET, [(0.0, T_PERCHE), (T_ALLORA, T_POI)])
show(FLAME, [(T_LIFT0 - 0.6, T_PERCHE), (T_RAZZO - 0.5, T_POI)])
show(TRUCK, [(T_CAMION, T_ELEF)])
show(EL['root'], [(T_ELEF, T_ALLORA)])
show(CT['root'], [(T_DENTRO - 0.1, TOTAL)])
show(ZE['root'], [(T_AMANTE, TOTAL)])
bpy.context.view_layer.update()
for o in list(prc.objects):                                                             # la cucina si vede solo quando serve
    if o.parent is None and abs(o.matrix_world.translation.x - KX) < 20 and o.name not in NEVER and o not in (JK['root'],): show(o, [(T_PERCHE - 0.05, T_MART)])
LK = luci.cinema(prc, (KX, 0.6, 1.3), (KX + 0.4, -2.6, 1.6), distanza=4.0, lato=1)
for l_ in LK.values():
    e_ = l_.data.energy
    for (t_, v) in ((0.0, 0.0), (T_PERCHE - 0.05, e_), (T_MART, 0.0)):
        l_.data.energy = v; l_.data.keyframe_insert('energy', frame=fr(t_))

# ======================= traiettorie =======================
def rocket_z(t):
    if t < T_PERCHE: t0 = T_LIFT0
    elif t >= T_ALLORA: t0 = T_RAZZO
    else: return 0.0
    if t < t0: return 0.02 * math.sin(t * 60) * ramp(t, t0 - 0.6, t0)          # vibra prima del decollo
    return 0.5 * 7.0 * (t - t0) ** 2
def jarL_z(t):
    """il barattolo che ricade: cade dal cielo e si pianta nel prato (un rimbalzo)"""
    if t < T_POI: return 30.0
    u = (t - T_POI) / 0.4
    if u < 1: return 30.0 * (1 - u) ** 2
    return 0.25 * max(0.0, math.sin(PI * (t - T_POI - 0.4) / 0.3)) if t < T_POI + 0.7 else 0.0
def ct_pose(t):
    """cetriolino: (posizione, yaw, spalla L, spalla R, gamba)"""
    base = Vector((JL['root'].location.x, JL['root'].location.y, 0))
    if t < T_DENTRO + 0.4:
        u = ramp(t, T_DENTRO - 0.1, T_DENTRO + 0.4); p = Vector((JAR_L.x, JAR_L.y, 0.05 + 0.42 * u)); return p, 0.0, (0, -0.3, 0), (0, 0.3, 0), 0.0
    if t < T_MUTANDE - 0.3:
        st = ramp(t, T_DENTRO + 0.6, T_DENTRO + 1.0) * (1 - ramp(t, T_MUTANDE - 0.8, T_MUTANDE - 0.4))
        return Vector((JAR_L.x, JAR_L.y, 0.47)), 0.0, (0, -2.7 * st, 0), (0, 2.7 * st, 0), 0.0
    if t < T_MUTANDE + 0.3:                                                                 # salta fuori dal barattolo
        u = ramp(t, T_MUTANDE - 0.3, T_MUTANDE + 0.3); a = Vector((JAR_L.x, JAR_L.y, 0.47)); b = Vector((JAR_L.x + 0.6, JAR_L.y - 0.35, 0.0))
        p = a.lerp(b, u); p.z += 0.7 * math.sin(PI * u); return p, 0.0, (0, -1.4, 0), (0, 1.4, 0), 0.0
    out = Vector((JAR_L.x + 0.6, JAR_L.y - 0.35, 0.0))
    if t < T_AMANTE + 0.5:                                                                  # posa da seduttore: mano sul fianco, ammicca
        return out, 0.25, (0, -0.6, 0.0), (0, 1.0 + 0.3 * math.sin(t * 4), 0), 0.0
    dest = ELE + Vector((-0.42, -0.1, 0))
    p, w = walk(t, T_AMANTE + 0.5, T_AMANTE + 2.2, out, dest)
    return p, yaw_to(out, dest) if w else yaw_to(dest, ELE), (0, -0.5, 0), (0, 0.5, 0), w

def pp(t):
    S_ = dict(loc=(0, 0, 0), yaw=0.0, lean=0.0, head=(0, 0, 0), hL=0.0, hR=0.0, aL=(-0.14, 0, -1), aR=(0.14, 0, -1), sc=1.0)
    k = 0.04 * math.sin(t * 34)
    if t < T_PERCHE or T_ALLORA <= t < T_POI:                                               # col telecomando, guarda il razzo
        up = -0.35 * ramp(t, T_LIFT0 if t < T_PERCHE else T_RAZZO, (T_LIFT0 if t < T_PERCHE else T_RAZZO) + 1.2)
        press = 0.2 * ramp(t, T_LIFT0 - 0.4 if t < T_PERCHE else T_RAZZO - 0.4, T_LIFT0 - 0.2 if t < T_PERCHE else T_RAZZO - 0.2)
        S_.update(loc=tuple(P_HOOK), yaw=yaw_to(P_HOOK, (PAD.x - 2.0, PAD.y - 6.0)), aR=(0.15, -0.9, 0.3 - press), aL=(-0.5, -0.2, 0.75), head=(up, 0, 0))
    elif t < T_MART:                                                                        # cucina: stringe il barattolo
        y_ = yaw_to(P_K, KJ)
        if t < T_DENTI:
            S_.update(loc=tuple(P_K), yaw=y_, lean=0.03 * math.sin(t * 20), aL=(-0.22 + k, -0.85, -0.4), aR=(0.22 - k, -0.85, -0.4), head=(-0.12, 0, 0.05 * math.sin(t * 17)))
        else:                                                                               # fa girare il barattolo con Tumbo attaccato
            S_.update(loc=tuple(P_K), yaw=y_, lean=0.0, head=(-0.1, 0, 0), aL=(-0.22, -0.85, -0.4 + 0.1 * math.sin(t * 25)), aR=(0.22, -0.85, -0.4 - 0.1 * math.sin(t * 25)))
    elif t < T_CAMION:                                                                      # martellate
        ph = ((t - T_MART - 0.1) * 3.2) % 1.0; sw = math.sin(PI * min(1.0, ph * 1.4))
        S_.update(loc=(TABLE.x + 0.15, TABLE.y + 0.75, 0), yaw=PI * 0 + yaw_to((TABLE.x + 0.15, TABLE.y + 0.75), TABLE), aR=tuple(Vector((0.1, -0.85, -0.45)).lerp(Vector((0.15, -0.2, 0.95)), sw)), lean=0.1)
    elif t < T_ALLORA:                                                                      # guarda il camion e l'elefante, braccia ai capelli
        p_ = Vector((JAR_G.x + 2.6, JAR_G.y + 1.4, 0))
        S_.update(loc=tuple(p_), yaw=yaw_to(p_, JAR_G), aL=(-0.42 + k, -0.2, 0.9), aR=(0.42 - k, -0.2, 0.9))
        if t > T_NIENTE: S_.update(aL=(-0.5, 0.0, -0.8), aR=(0.5, 0.0, -0.8), head=(0.25, 0, 0))
    elif t < T_QUEL:                                                                        # il barattolo ricade; il coperchio; il cetriolino; Eleonora
        look = JAR_L if t < T_AMANTE + 0.3 else ELE
        S_.update(loc=tuple(P_L), yaw=yaw_to(P_L, look), head=(0.15 if T_SVITA < t < T_MACHE else 0.0, 0, 0))
        if T_MACHE < t < T_AMANTE: S_.update(aL=(-0.85, -0.25, 0.45), aR=(0.85, -0.25, 0.45))
    else:                                                                                   # entra nel barattolo e si chiude dentro
        inside = Vector((JAR_L.x, JAR_L.y, 0.06)); w0 = Vector((JAR_L.x + 0.75, JAR_L.y + 0.2, 0))
        if t < T_QUEL + 0.6: p_, w = walk(t, T_QUEL, T_QUEL + 0.6, P_L, w0); S_.update(loc=tuple(p_), yaw=yaw_to(P_L, JAR_L), hL=0.4 * w, hR=-0.4 * w)
        else:
            u = ramp(t, T_QUEL + 0.6, T_QUEL + 1.3); p_ = w0.lerp(inside, u); p_.z += 1.6 * math.sin(PI * u)
            S_.update(loc=tuple(p_), yaw=yaw_to(w0, (JAR_L.x, JAR_L.y - 3.0)) if u > 0.5 else yaw_to(w0, JAR_L), sc=1.0 - 0.72 * u)
            if u >= 1.0: S_.update(aL=(0.6, -0.6, 0.1), aR=(-0.6, -0.6, 0.1), yaw=yaw_to(JAR_L, (JAR_L.x + 0.3, JAR_L.y - 3.0)))   # braccia conserte
    return S_

def tp(t):
    """Tumbo: (posizione, yaw, ritto, pitch extra)"""
    if t < T_PERCHE or T_ALLORA <= t < T_POI: return T_HOOKP, yaw_to(T_HOOKP, PAD), 0.0, 0.0
    if t < T_DENTI: return T_K, yaw_to(T_K, KJ), 0.0, 0.0
    if t < T_MART:                                                                          # attaccato al coperchio coi denti, gira come un'elica
        a = (t - T_DENTI) * 9.0 * ramp(t, T_DENTI + 0.4, T_DENTI + 0.9); d = Vector((math.cos(a), math.sin(a), 0))
        p = Vector((KJ.x, KJ.y, KJ.z + JH + 0.05)) + d * 0.62; p.z -= 0.25
        if t < T_DENTI + 0.4: p = T_K.lerp(p, ramp(t, T_DENTI, T_DENTI + 0.4))
        return p, yaw_to(p, KJ), 0.0, 0.0
    if t < T_CAMION: return Vector((TABLE.x + 1.1, TABLE.y + 0.2, 0)), yaw_to((TABLE.x + 1.1, TABLE.y + 0.2), TABLE), 0.0, 0.0
    if t < T_ALLORA: return Vector((JAR_G.x + 3.3, JAR_G.y + 0.6, 0)), yaw_to((JAR_G.x + 3.3, JAR_G.y + 0.6), JAR_G), 0.0, 0.0
    if t < T_STAVOLTA: return T_LP, yaw_to(T_LP, JAR_L), 0.0, 0.0
    bite = Vector((JAR_L.x + 0.32, JAR_L.y - 0.2, 0.0))                                      # in piedi sul barattolo, morde il coperchio
    return bite, yaw_to(bite, JAR_L), ramp(t, T_STAVOLTA, T_STAVOLTA + 0.3), 0.0

# ======================= chiavi =======================
def K(o, f, loc=None, rot=None, scale=None):
    if loc is not None: o.location = loc; o.keyframe_insert('location', frame=f)
    if rot is not None: o.rotation_euler = rot; o.keyframe_insert('rotation_euler', frame=f)
    if scale is not None: o.scale = scale if isinstance(scale, (tuple, list)) else (scale,) * 3; o.keyframe_insert('scale', frame=f)
LID0 = tuple(JL['lid'].location)
for f in range(1, NF + 1):
    t = (f - 1) / FPS
    s = pp(t); K(P['root'], f, s['loc'], (s['lean'], 0, s['yaw']), s['sc'])
    for nm, k_ in (('L', 'aL'), ('R', 'aR')):
        sh = P['shoulder' + nm]; sh.rotation_quaternion = qdir(s[k_]); sh.keyframe_insert('rotation_quaternion', frame=f)
        K(P['hip' + nm], f, rot=(s['h' + nm], 0, 0))
    K(P['head'], f, rot=s['head'])
    l, yw, up, pt = tp(t); K(Tb['root'], f, tuple(l), (-0.55 * up + pt, 0, yw), 0.75)
    K(Tb['tail'], f, rot=(-1.0 + 0.2 * math.sin(t * 9), 0, 0.5 * math.sin(t * 12)))
    shake = 0.12 * math.sin(t * 30) if t >= T_STAVOLTA else 0.0
    K(Tb['head'], f, rot=(0, shake, 0))
    # razzo, fiamma, barattolo in cima
    rz = rocket_z(t); K(ROCKET, f, (R0.x, R0.y, R0.z + rz))
    K(FLAME, f, (PAD.x, PAD.y, rz - 1.6), scale=(0.9, 0.9, 2.4 * (1.0 + 0.2 * math.sin(t * 50))))
    K(JR['root'], f, (PAD.x, PAD.y, rz + R_H + 0.02))
    # barattolo in giardino: sul tavolino, poi sul prato
    K(JG['root'], f, (TABLE.x, TABLE.y, TAB_H) if t < T_CAMION else tuple(JAR_G), rot=(0, 0, 0.04 * math.sin(t * 40) if T_MART < t < T_CAMION else 0.0))
    # barattolo in cucina: trema quando Pippo stringe, gira quando Tumbo fa l'elica
    spin = (t - T_DENTI) * 9.0 * ramp(t, T_DENTI + 0.4, T_DENTI + 0.9) if T_DENTI < t < T_MART else 0.0
    K(JK['root'], f, rot=(0, 0, 0.03 * math.sin(t * 45) if t < T_DENTI else 0.0))
    K(JK['lid'], f, rot=(0, 0, spin))
    # barattolo caduto: il coperchio si svita da solo, poi torna e si avvita (Pippo si chiude dentro)
    K(JL['root'], f, (JAR_L.x, JAR_L.y, jarL_z(t)))
    sv = ramp(t, T_SVITA, T_SOLO + 0.1); off_ = ramp(t, T_SOLO + 0.1, T_SOLO + 0.5); back = ramp(t, T_CHIUDE - 0.8, T_CHIUDE + 0.3)
    lid_ground = Vector((-0.6, -0.25, -JH + 0.03))
    lp = Vector(LID0) + Vector((0, 0, 0.12 * sv)); lp = lp.lerp(Vector(LID0) + lid_ground, off_); lp = lp.lerp(Vector(LID0), back)
    lp2 = lp.copy(); lp2.z += 0.5 * math.sin(PI * off_) * (1 - back) + 0.5 * math.sin(PI * back)
    K(JL['lid'], f, tuple(lp2), (1.2 * off_ * (1 - back), 0, -8.0 * sv + 8.0 * back))
    # camion che passa sopra il barattolo e rimbalza
    if T_CAMION - 0.1 <= t < T_ELEF + 0.1:
        u = ramp(t, T_CAMION, T_ELEF - 0.1); x = -8.5 + 17.0 * u; bump = 0.6 * max(0.0, math.cos((x - JAR_G.x) / 1.3 * PI / 2)) if abs(x - JAR_G.x) < 1.3 else 0.0
        K(TRUCK, f, (x, JAR_G.y, bump), (0.0, -0.25 * bump, PI / 2))
    elif f == 1: K(TRUCK, f, (-30, JAR_G.y, 0), (0, 0, PI / 2))
    # elefante che piove dal cielo e si siede sul barattolo
    if t >= T_ELEF - 0.1:
        u = ramp(t, T_ELEF, T_ELEF + 0.5); bo = 0.2 * abs(math.sin((t - T_ELEF - 0.5) * 9)) * max(0.0, 1 - (t - T_ELEF - 0.5) * 1.5) if t > T_ELEF + 0.5 else 0.0
        K(EL['root'], f, (EL_SIT.x, EL_SIT.y, EL_SIT.z + 8.0 * (1 - u) ** 2 + bo), (0, 0, EL_YAW))
        for i, sg in enumerate(EL['trunk']): K(sg, f, rot=(-0.45 + 0.15 * math.sin(t * 3 + i * 0.6), 0, 0))
        for i, ea in enumerate(EL['ears']): K(ea, f, rot=(0, 0, (1 if i else -1) * (0.35 + 0.2 * math.sin(t * 6))))
    elif f == 1: K(EL['root'], f, (EL_SIT.x, EL_SIT.y, EL_SIT.z + 8), (0, 0, EL_YAW))
    # cetriolino
    p_, y_, sL, sR, w = ct_pose(t); K(CT['root'], f, tuple(p_), (0, 0, y_), 1.0 if t >= T_DENTRO - 0.1 else 0.01)
    K(CT['shoulderL'], f, rot=sL); K(CT['shoulderR'], f, rot=sR)
    K(CT['hipL'], f, rot=(0.6 * w, 0, 0)); K(CT['hipR'], f, rot=(-0.6 * w, 0, 0))
    # Eleonora
    K(ZE['root'], f, tuple(ELE), (0, 0, yaw_to(ELE, CT['root'].location if t > T_AMANTE else JAR_L)))

# ======================= espressioni =======================
_last = {}
def _ex(key, fn, t, k):
    if key in _last and t - 0.06 > _last[key][1]: fn(fr(t - 0.06), **_last[key][0])
    fn(fr(t), **k); _last[key] = (k, t)
_emo_last = [None]
def _emo_key(f, nome, forza):
    e = pippo.EMOZIONI_FORTI[nome]
    fa = {k: (tuple(x * forza for x in v) if isinstance(v, tuple) else v * forza) for k, v in e['faccia'].items()}
    pippo.express(P, f, **fa)
    if 'sopracciglia' in e:
        for (s_, nm), b in zip(((-1, 'L'), (1, 'R')), e['sopracciglia']):
            br = P['brow' + nm]; br.rotation_euler = (0, s_ * b * 0.45 * forza, 0); br.location.z = pippo.HEAD_C + 0.215 + 0.07 * max(0.0, -b) * forza
            br.keyframe_insert('rotation_euler', frame=f); br.keyframe_insert('location', index=2, frame=f)
    bx_, by_ = e.get('busto', (0, 0)); P['body'].rotation_euler = (bx_ * forza, by_ * forza, 0); P['body'].keyframe_insert('rotation_euler', frame=f)
    seg = pippo._segni(P)
    for k, g in seg.items():
        g.scale = (1, 1, 1) if (k in e.get('extra', ()) and forza > 0.3) else (0.001,) * 3
        g.keyframe_insert('scale', frame=f)
def emo(t, nome, forza=1.0):
    if _emo_last[0] and t - 0.06 > _emo_last[0][2]: _emo_key(fr(t - 0.06), _emo_last[0][0], _emo_last[0][1])
    _emo_key(fr(t), nome, forza); _emo_last[0] = (nome, forza, t)
def tex(t, **k): _ex('t', lambda f, **kk: tumbo.tumbo_express(Tb, f, **kk), t, k)
def zex(t, nome):
    if 'z' in _last and t - 0.06 > _last['z'][1]: eleonora.emozione(ZE, fr(t - 0.06), _last['z'][0])
    eleonora.emozione(ZE, fr(t), nome); _last['z'] = (nome, t)
emo(0.0, 'furbo'); emo(T_LIFT0, 'ride'); emo(T_PERCHE, 'arrabbiato'); emo(T_MANI, 'arrabbiato', 1.0); emo(T_DENTI, 'sorpreso', 0.7)
emo(T_MART, 'arrabbiato'); emo(T_CAMION, 'spaventato'); emo(T_ELEF + 0.5, 'sorpreso'); emo(T_NIENTE, 'triste')
emo(T_ALLORA, 'furbo'); emo(T_RAZZO, 'ride'); emo(T_POI + 0.4, 'arrabbiato', 0.8); emo(T_SVITA, 'sorpreso', 0.6)
emo(T_MACHE, 'sorpreso'); emo(T_AMANTE + 0.3, 'spaventato'); emo(T_AMANTE + 1.6, 'triste')
emo(T_QUEL, 'arrabbiato'); emo(T_STAVOLTA, 'arrabbiato', 0.7)
tex(0.0, tongue=0.8); tex(T_PERCHE, tongue=0.0); tex(T_DENTI, tongue=0.0, eye_scale=1.15); tex(T_MART, eye_scale=1.0, tongue=0.6)
tex(T_ELEF, tongue=0.0, eye_scale=1.15); tex(T_ALLORA, eye_scale=1.0, tongue=0.8); tex(T_MACHE, tongue=0.0, eye_scale=1.15); tex(T_STAVOLTA, eye_scale=1.0, brow=0.6)
zex(0.0, 'normale'); zex(T_AMANTE + 0.2, 'felice'); zex(T_AMANTE + 1.2, 'furba'); zex(T_QUEL, 'ride')

# ======================= effetti =======================
FXC = prc
def fx(name, pos, w, t0, dur, **k): return A.effetto(name, posizione=tuple(pos), larghezza=w, animazione=(fr(t0), int(dur * FPS)), collezione=FXC, **k)
for t0 in (T_LIFT0, T_RAZZO):
    for k in range(10): fx('sbuffo_bianco/whitepuff%02d' % (k * 2), (PAD.x + 2.0 * math.cos(k * 0.63), PAD.y + 2.0 * math.sin(k * 0.63), 0.8), 4.0, t0 - 0.3 + 0.08 * k, 1.6, colore=(0.9, 0.86, 0.8), opacita=0.9)
for k in range(4): fx('particelle/star_0%d' % (k + 1), (TABLE.x, TABLE.y - 0.1, TAB_H + 0.9), 0.45, T_MART + 0.25 + k / 3.2, 0.3, colore=(1, 0.9, 0.4), luce=2.0)
fx('sbuffo_bianco/whitepuff04', (JAR_G.x, JAR_G.y, 0.5), 1.6, T_CAMION + 0.5, 0.6, opacita=0.8)
for k in range(5): fx('sbuffo_bianco/whitepuff%02d' % (k * 3), (JAR_G.x + 1.6 * math.cos(k * 1.25), JAR_G.y + 1.6 * math.sin(k * 1.25), 0.5), 2.5, T_ELEF + 0.45, 0.9, opacita=0.85)
for k in range(5): fx('sbuffo_bianco/whitepuff%02d' % (k * 4 + 1), (JAR_L.x + 1.0 * math.cos(k * 1.25), JAR_L.y + 0.6 + 0.5 * math.sin(k * 1.25), 0.25), 0.9, T_POI + 0.4, 0.5, colore=(0.75, 0.62, 0.45), opacita=0.7)
fx('emoticon/question', (P_L.x, P_L.y, 2.6), 0.4, T_MACHE + 0.1, 1.0)
fx('emoticon/hearts', (ELE.x - 0.2, ELE.y - 0.1, 1.55), 0.7, T_AMANTE + 0.4, 1.5)
fx('emoticon/heartbroken', (P_L.x, P_L.y, 2.6), 0.45, T_AMANTE + 1.5, 1.2)
fx('emoticon/exclamations', (P_K.x, P_K.y, 2.55), 0.45, T_DENTI + 0.1, 0.7)

# ======================= camera =======================
JLp = lambda dx, dy, z: (JAR_L.x + dx, JAR_L.y + dy, z)
CTO = (JAR_L.x + 0.6, JAR_L.y - 0.35)
SHOTS = [  # t0, t1, camera da, a, mira da, a, lente, diaframma, segue il razzo
    (0.0, 3.6, (3.2, -9.0, 0.9), (3.4, -8.4, 1.0), (PAD.x - 0.6, PAD.y, 6.0), (PAD.x - 0.6, PAD.y, 6.6), 22, 14, False),         # 01 il razzo col barattolo in cima
    (3.6, T_PERCHE, (1.0, -16.0, 1.2), (1.0, -15.5, 1.4), None, None, 22, 22, True),                                            # 02 decollo
    (T_PERCHE, 9.4, (KX + 1.2, -2.5, 2.05), (KX + 1.05, -2.2, 2.05), (KX - 0.05, 0.8, 1.6), (KX - 0.05, 0.8, 1.6), 30, 6, False),            # 03 cucina: non si apre
    (9.4, T_MANI, (KX + 0.55, -1.15, 2.05), (KX + 0.5, -1.0, 2.0), (KX, 0.4, 1.66), (KX, 0.4, 1.66), 40, 3, False),                # 04 il coperchio
    (T_MANI, T_DENTI, (KX - 1.0, -1.6, 2.1), (KX - 0.85, -1.4, 2.05), (KX, 0.9, 1.8), (KX, 0.9, 1.8), 34, 5, False),          # 05 con le mani
    (T_DENTI, T_MART, (KX + 0.6, -2.8, 2.15), (KX + 0.5, -2.5, 2.1), (KX, 0.5, 1.55), (KX, 0.5, 1.55), 28, 7, False),             # 06 Tumbo elica
    (T_MART, T_CAMION, (TABLE.x + 0.6, TABLE.y - 3.0, 1.45), (TABLE.x + 0.5, TABLE.y - 2.7, 1.45), (TABLE.x, TABLE.y, 1.25), (TABLE.x, TABLE.y, 1.25), 30, 6, False),  # 07 martello
    (T_CAMION, T_ELEF, (JAR_G.x + 0.4, JAR_G.y - 5.0, 0.45), (JAR_G.x + 0.4, JAR_G.y - 4.8, 0.45), (JAR_G.x, JAR_G.y, 0.9), (JAR_G.x, JAR_G.y, 0.9), 22, 10, False),  # 08 camion
    (T_ELEF, T_NIENTE, (JAR_G.x - 5.2, JAR_G.y + 2.6, 1.3), (JAR_G.x - 4.8, JAR_G.y + 2.4, 1.35), (JAR_G.x, JAR_G.y + 0.4, 2.0), (JAR_G.x, JAR_G.y + 0.4, 1.7), 26, 12, False),  # 09 elefante
    (T_NIENTE, T_ALLORA, (JAR_G.x + 0.35, JAR_G.y - 2.2, 0.5), (JAR_G.x + 0.3, JAR_G.y - 2.0, 0.5), (JAR_G.x, JAR_G.y, 0.55), (JAR_G.x, JAR_G.y, 0.55), 32, 4, False),  # 10 niente
    (T_ALLORA, T_POI, (1.0, -16.0, 1.2), (1.0, -15.5, 1.4), None, None, 22, 22, True),                                          # 11 RAZZO
    (T_POI, T_SVITA, JLp(1.6, -6.0, 1.3), JLp(1.4, -5.6, 1.3), JLp(0.3, 0, 1.6), JLp(0.3, 0, 0.9), 26, 8, False),               # 12 ricade intatto
    (T_SVITA, T_MACHE, JLp(0.3, -1.7, 1.2), JLp(0.25, -1.5, 1.15), JLp(0, 0, 0.88), JLp(0, 0, 0.9), 40, 3, False),               # 13 si svita da solo
    (T_MACHE, T_DENTRO - 0.1, (P_L.x + 0.3, P_L.y - 2.5, 1.95), (P_L.x + 0.28, P_L.y - 2.3, 1.95), (P_L.x, P_L.y, 1.85), (P_L.x, P_L.y, 1.85), 38, 4, False),  # 14 ma che...
    (T_DENTRO - 0.1, T_MUTANDE - 0.3, JLp(0.15, -1.9, 1.05), JLp(0.12, -1.7, 1.05), JLp(0, 0, 0.95), JLp(0, 0, 1.0), 36, 3, False),  # 15 il cetriolino
    (T_MUTANDE - 0.3, T_AMANTE, (CTO[0] + 0.1, CTO[1] - 1.0, 0.3), (CTO[0] + 0.1, CTO[1] - 0.9, 0.28), (CTO[0], CTO[1], 0.22), (CTO[0], CTO[1], 0.2), 38, 3, False),  # 16 in mutande
    (T_AMANTE, T_QUEL, (3.4, -5.0, 1.15), (3.2, -4.7, 1.15), (0.8, -1.7, 0.7), (0.9, -1.6, 0.7), 30, 5, False),                 # 17 l'amante di Eleonora
    (T_QUEL, T_STAVOLTA, JLp(1.3, -4.4, 1.5), JLp(1.1, -4.0, 1.4), JLp(0.3, 0, 1.0), JLp(0.1, 0, 0.7), 30, 6, False),            # 18 si chiude dentro
    (T_STAVOLTA, T_FINE, JLp(0.45, -1.9, 0.95), JLp(0.35, -1.55, 0.9), JLp(0.05, 0, 0.6), JLp(0.05, 0, 0.6), 34, 3, False),        # 19 nessuno lo apre
    (T_FINE, TOTAL + 0.1, (2000, 0, 0), (2000, 0, 0), (2000, 1, 0), (2000, 1, 0), 30, 8, False),                                 # 20 nero
]
for f in range(1, NF + 1):
    t = (f - 1) / FPS
    s_ = next((s for s in SHOTS if s[0] <= t < s[1]), SHOTS[-1]); u = sm((t - s_[0]) / (s_[1] - s_[0]))
    cl = Vector(lerp(s_[2], s_[3], u))
    if s_[8]: tl = Vector((PAD.x, PAD.y, min(28.0, 6.0 + rocket_z(t))))
    else: tl = Vector(lerp(s_[4], s_[5], u))
    if s_[0] in (T_ELEF, T_POI) and t < s_[0] + 0.6:                                        # scossone sul tonfo
        sh_ = 0.08 * math.sin(t * 50) * ramp(t, s_[0] + 0.35, s_[0] + 0.45); cl = cl + Vector((sh_, 0, sh_))
    cam.location = cl; tgt.location = tl; camd.lens = s_[6]; camd.dof.aperture_fstop = s_[7]
    cam.keyframe_insert('location', frame=f); tgt.keyframe_insert('location', frame=f); camd.keyframe_insert('lens', frame=f); camd.dof.keyframe_insert('aperture_fstop', frame=f)

def lin(idb):
    for fc in all_fcurves(idb):
        kind = 'CONSTANT' if 'hide' in fc.data_path else 'LINEAR'
        for kp in fc.keyframe_points: kp.interpolation = kind
for o in bpy.data.objects: lin(o)
set_interp(camd, 'CONSTANT')
for nm in ('Cam', 'CamTarget'):
    for fc in all_fcurves(bpy.data.objects[nm]):
        for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'
for l_ in LK.values():
    for fc in all_fcurves(l_.data):
        for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'
try: scene.render.use_motion_blur = True; scene.render.motion_blur_shutter = 0.06
except Exception: pass
os.makedirs(os.path.dirname(os.path.abspath(BLEND)), exist_ok=True)
import json; json.dump([[round(s[0], 3), round(min(s[1], TOTAL), 3)] for s in SHOTS], open(os.path.join(os.path.dirname(os.path.abspath(BLEND)), 'shots.json'), 'w'))
bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(BLEND)); print('SAVED', BLEND, len(bpy.data.objects), 'oggetti')
