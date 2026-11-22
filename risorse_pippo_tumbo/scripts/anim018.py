"""TESTA STANDARD di ogni episodio: mondo, quartiere (casa di Pippo a est, casa di Gualtiero a ovest, staccionata, strada), funzioni house_at / tower_at / tree.
Uso: cat templates/head.py scripts/animNNN_body.py > scripts/animNNN.py  (cambia TOTAL e gli import prima).
Test 018 - LA MENTE (voce con gli insulti). Salva ../t018/pippo_t018.blend
Personaggi: Pippo e Tumbo ESISTENTI (pippo.py, tumbo.py) invariati; Gualtiero = nuovo vicino ricorrente (props009.gualtiero)."""
import sys, math, os
sys.path.insert(0, os.path.dirname(__file__))
import bpy, numpy as np
from mathutils import Vector, Euler, Matrix
from common import *
from render_setup import *
import set004, props004, props007, props009, props010, props012, props013, props015, props016b, kitlook, lookdev, pippo, tumbo
from set004 import obj, bx, cyl, ball_, MB

FPS = 24; TOTAL = 49.5; NF = int(TOTAL * FPS)
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
# Test 018 - LA MENTE (presentazione di Giulia), 48 s. Si unisce alla testa: cat templates/head.py scripts/anim018_body.py > scripts/anim018.py
# Scelte dell'autore (17 novembre 2026): base S militare, squalo Y simpatico, cabina W vintage. Luce «cinema» all'aperto, kitlook.
# Tempi presi da audio/words_t018.json (scritti qui sotto a mano).
# ===================================================================================================================
import props018, giulia, luci, random
import pippo2 as pippo
from props007 import text_obj
A = kitlook.A
BLEND = os.environ.get('BLEND018', '../t018/pippo_t018.blend')
FONT = A.font('luckiest')
Q = props018.mats018(); GM = giulia.mats_giulia()

# ======================= tempi (dalla voce) =======================
T_FLASH = 7.58                                   # «Ogni mattina»: si torna indietro, la base non c'e'
T_LOCK = 10.32; T_CASS = 11.76                    # lucchetto, Gualtiero si porta via la cassetta
T_BUILD = 15.02; T_CAZZO = 16.26                 # «Allora Pippo costruisce una CAZZO di base»
T_CAMS, T_LASER, T_MOAT = 18.24, 18.98, 19.54
T_DANCE, T_BALL = 20.18, 21.54                   # «Gualtiero passa i laser, ballando»
T_DOOR, T_TUMBO = 23.02, 24.12                   # «La porta blindata? Gliela apre Tumbo»
T_ROOM = 25.15                                   # sala di controllo: Pippo si gira, Tumbo e' li' che scodinzola
T_WATCH, T_ZOOM, T_EYES = 26.66, 28.34, 29.26
T_KNOCK = 31.46; T_KK = 32.32                    # «Pippo bussa. Sulla testa.» (toc toc a 31.05)
T_MACHE, T_GIULIA, T_GUIDA = 33.96, 35.20, 37.74
T_KT, T_KTK, T_ALTRA = 39.34, 40.62, 41.70       # bussa su Tumbo, toc toc, «Un'altra Giulia»
T_SELF, T_SELFK, T_OCC = 44.14, 45.00, 45.88
T_FLUSH, T_BLACK = 47.40, 48.85

# ======================= rendering e luce =======================
setup_render(scene, 1080, 1920, samples=5, fps=FPS, frames=NF); scene.frame_end = NF
for o in list(bpy.data.objects):                 # la testa mette alberi a palla, nuvole e sole: li sostituisce kitlook
    pass

BC = Vector((2.0, -0.33, 0.0)); RW = 3.3          # centro della base (la cassetta), raggio delle mura
CAS_XY = (BC.x, BC.y)

# ======================= camera subito (gli effetti si girano verso la camera) =======================
camd = bpy.data.cameras.new('Cam'); cam = bpy.data.objects.new('Cam', camd); cac.objects.link(cam); scene.camera = cam
camd.clip_start = 0.03; camd.clip_end = 1500; camd.sensor_width = 36
tgt = empty('CamTarget', (0, 0, 1), None, cac)
ct = cam.constraints.new('TRACK_TO'); ct.target = tgt; ct.track_axis = 'TRACK_NEGATIVE_Z'; ct.up_axis = 'UP_Y'
camd.dof.use_dof = True; camd.dof.focus_object = tgt

kitlook.upgrade(scene, M, envc, prc, extras=False)
scene.eevee.taa_render_samples = 5
luci.cielo_basso(scene.world, 0.4)
scene.world.use_sun_shadow = False                # le ombre le fa il sole «cinema»: quelle del cielo costano il 20% del tempo e non si vedono
SUN = luci.sole(prc, (-0.55, -0.85), lato=1, energia=4.5)
luci.ombre_pulite(scene, mezza_risoluzione=True)
# dettagli vicini ma fuori dalla base: ciuffi d'erba, fiori, lampioni, panchina
kitlook.variants('grass_medium_01', 10, (-8.5, -6.2, -7.0, 6.0), (0.14, 0.24), seed=4, coll=envc, shadow=False)
kitlook.variants('dandelion_01', 10, (-8.5, -6.0, -7.0, 6.0), (0.09, 0.15), seed=6, coll=envc, shadow=False)
kitlook.variants('celandine_01', 8, (10.0, 13.0, -7.0, 6.0), (0.09, 0.15), seed=8, coll=envc, shadow=False)
kitlook.variants('shrub_02', 4, (5.5, 12.0, 7.4, 8.6), (0.8, 1.3), seed=2, coll=envc)
for x in (-22, -6, 14, 32): A.modello('street_lamp_01', posizione=(x, -8.15, 0.05), altezza=4.2, rotazione=90, collezione=envc)

# ======================= la base (scelta S), lo squalo (Y), la sala di controllo =======================
B = props018.base(prc, Q, 'S', (BC.x, BC.y), Rw=RW, font=FONT)
BROOT = B['root']; BROOT.rotation_mode = 'XYZ'
DOOR_P = Vector((B['door_pos'][0], B['door_pos'][1], 0)); DOOR_D = Vector((B['door_dir'][0], B['door_dir'][1], 0))   # centro della porta, verso l'esterno
CAS2 = props018.cassetta(prc, Q, marciapiede=False); CAS2['root'].location = (BC.x, BC.y, 0.0)
CAS1 = props018.cassetta(prc, Q, marciapiede=True); CAS1['root'].location = (BC.x, BC.y, 0.0)
LOCK = props018.lucchetto(prc, Q, s=0.55)
SQ = props018.squalo(chc, Q, 'Y', 1.05)
FINS = []
for k in range(2):                                # altre due pinne che girano nel fossato («gli squali»)
    fe = empty('PinnaSola%d' % k, (0, 0, 0), None, prc); fe.rotation_mode = 'XYZ'
    props018._pinna('PinnaSolaM%d' % k, [(-0.32, 0.0), (0.22, 0.0), (0.26, 0.14), (0.24, 0.78)], 0.08, prc, fe, Q['shark']); FINS.append(fe)
SALA = props018.sala_controllo(prc, Q, (600.0, 0.0), font=FONT)
RX = 600.0
TOWERCAM = props018.telecamera(prc, Q)            # la telecamera sulla testa di Tumbo (gag della lista)

# ======================= personaggi =======================
P = pippo.build_pippo(chc); Tb = tumbo.build_tumbo(chc, scale=0.75); GU = props009.gualtiero(chc, G9)
for r in (P['root'], Tb['root'], GU['root']): r.rotation_mode = 'XYZ'
for nm in 'LR': P['shoulder' + nm].rotation_mode = 'QUATERNION'
for nm in ('shoulderL', 'shoulderR', 'hipL', 'hipR', 'head'): GU[nm].rotation_mode = 'XYZ'
def qdir(d, rest=(0, 0, -1)): return Vector(rest).rotation_difference(Vector(d).normalized())
def yaw_to(a, b): return math.atan2(b[0] - a[0], -(b[1] - a[1]))
HAT = props018.caschetto(chc, Q, P['head']); MUG = props018.tazza(chc, Q, P['elbowR'])
TOWERCAM.parent = Tb['head']; TOWERCAM.location = (0, 0.02, 0.36); TOWERCAM.scale = (0.8, 0.8, 0.8)
# il cranio di Gualtiero e quello di Tumbo si aprono come un coperchio: dentro, la cabina W e Giulia minuscola
crn = [o for o in GU['head'].children if o.name.startswith('G_Cranio')][0]
KG = props018.cranio(chc, Q, GM, GU['head'], crn, (0.30, 0.28, 0.31), 0.17, G9['gskin'], 'W', figli_coperchio=[GU['browL'], GU['browR']])
th = [o for o in Tb['head'].children if o.name == 'T_Head'][0]
KT = props018.cranio(chc, Q, GM, Tb['head'], th, (0.29, 0.27, 0.27), 0.15, Tb['mats']['fur'] if 'mats' in Tb else th.material_slots[0].material, 'W',
                     giulia_s=0.085, oggetto='osso', figli_coperchio=[Tb['browL'], Tb['browR']])
for K_ in (KG, KT):
    K_['J']['root'].rotation_mode = 'XYZ'
    for nm in ('shoulderL', 'shoulderR'): K_['J'][nm].rotation_mode = 'XYZ'
# il giornale (sempre al contrario in mano a Gualtiero)
GZ_HAND = props018.giornale(chc, Q, font=FONT); GZ_HAND.parent = GU['root']; GZ_HAND.location = (0.16, -0.52, 1.22); GZ_HAND.rotation_euler = (0.15, PI, 0)
GZ_BOX1 = props018.giornale(prc, Q, font=FONT); GZ_BOX1.parent = CAS1['root']; GZ_BOX1.location = (0, -0.16, 1.24); GZ_BOX1.rotation_euler = (0.25, 0, 0); GZ_BOX1.scale = (0.8, 0.8, 0.8)

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
def lights_on(lo, intervals, energy):
    l_ = lo.data
    for (t_, v) in [(0.0, energy if intervals[0][0] <= 0 else 0.0)] + [x for (a, b) in intervals for x in ((a, energy), (b, 0.0))]:
        l_.energy = v; l_.keyframe_insert('energy', frame=fr(t_))
    for fc in all_fcurves(l_):
        for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'

T_BASE = T_BUILD + 0.25
show_only(B['laser_root'], [(0.0, T_FLASH), (T_LASER, T_KNOCK - 0.1)])                                    # i laser: nell'hook, poi dalla lista fino a quando Pippo va a bussare
show_only(LOCK, [(T_LOCK + 0.4, T_CASS + 2.2)])
show_only(GZ_BOX1, [(T_FLASH, T_FLASH + 0.75)])
show_only(HAT, [(T_BUILD - 0.1, T_CAMS + 0.9)]); show_only(MUG, [(T_FLASH, T_LOCK - 0.1)])
show_only(TOWERCAM, [(T_CAMS, T_LASER + 0.4)])
for i, c_ in enumerate(B['cams']): show_only(c_, [(0.0, T_FLASH), (T_CAMS + 0.08 * i, TOTAL)])
show(BROOT, [(0.0, T_FLASH), (T_BASE, TOTAL)])
show(CAS2['root'], [(0.0, T_FLASH), (T_BASE, TOTAL)])
show(CAS1['root'], [(T_FLASH, T_CASS + 2.2)])
for fe in FINS: show(fe, [(T_MOAT - 0.1, T_DANCE)])
show(SQ['root'], [(0.0, T_FLASH), (T_MOAT - 0.1, T_DANCE)])
show_only(GZ_HAND, [(0.0, T_FLASH), (T_FLASH + 0.55, T_CASS - 0.2), (T_DANCE + 2.0, TOTAL)])
lights_on(KG['light'], [(T_MACHE + 0.3, TOTAL)], 0.5); lights_on(KT['light'], [(T_ALTRA - 0.2, TOTAL)], 0.35)

# ======================= posti =======================
HOOK_R = 5.7                                         # lo squalo gira nel fossato (raggio medio)
def on_circle(r, a, z=0.0): return Vector((BC.x + r * math.cos(a), BC.y + r * math.sin(a), z))
WALLTOP = 2.27
P_WALL = on_circle(RW, PI + 0.32, WALLTOP); T_WALL = on_circle(RW, PI + 0.48, WALLTOP)          # Pippo e Tumbo in cima alle mura nell'hook
HOUSE_DOOR = Vector((0.6, 6.7, 0)); P_CAS = Vector((BC.x + 0.75, BC.y - 0.55, 0))                 # Pippo davanti alla cassetta
G_CAS = Vector((BC.x - 0.55, BC.y - 0.35, 0))                                                     # Gualtiero davanti alla cassetta (dentro la base)
G_OUTW = Vector((-9.5, BC.y - 0.5, 0))
P_BUILD = Vector((BC.x + 0.4, BC.y - 7.85, 0)); T_BUILDP = Vector((BC.x + 1.3, BC.y - 7.75, 0))   # sul marciapiede davanti alla base
P_ROOM = Vector((RX - 0.45, -0.35, 0)); T_ROOMP = Vector((RX + 0.55, -0.3, 0))
P_KN = Vector((G_CAS.x + 0.6, G_CAS.y - 0.05, 0)); T_KN = Vector((G_CAS.x + 1.25, G_CAS.y - 0.75, 0))
DOOR_IN = DOOR_P - DOOR_D * 0.9                                                                     # appena dentro la porta
T_DOORP = DOOR_P - DOOR_D * 0.85 + Vector((-DOOR_D.y, DOOR_D.x, 0)) * 0.3                         # Tumbo accanto alla ruota

def sq_path(t):
    """squalo: (posizione, yaw, pinna). Nell'hook porta Gualtiero lungo il fossato; nella lista gira con le altre pinne."""
    if t < T_FLASH:
        a = PI + 0.62 - 0.14 * min(t, 7.5)                       # da sud-ovest verso nord-ovest
        p = on_circle(HOOK_R, a, 0.16 + 0.03 * math.sin(t * 5)); return p, a, 1.0
    a = PI + 0.2 - (t - T_MOAT) * 0.75; p = on_circle(HOOK_R, a, 0.05 + 0.04 * math.sin(t * 6)); return p, a, 1.0

# ======================= pose =======================
ARMS_DOWN = dict(aL=(-0.14, 0, -1), aR=(0.14, 0, -1))
def walk(t, t0, t1, a, b):
    u = ramp(t, t0, t1); return a.lerp(b, u), (0.5 * math.sin(t * 11) if 0.0 < u < 1.0 else 0.0)

def braccia(nome, forza=1.0):
    """le braccia dell'emozione del catalogo (direzioni locali, come in pp)."""
    b = pippo.EMOZIONI_FORTI[nome]['braccia']; return {'aL': tuple(Vector((0, 0, -1)).lerp(Vector(b[0]).normalized(), forza)), 'aR': tuple(Vector((0, 0, -1)).lerp(Vector(b[1]).normalized(), forza))}

def pp(t):
    """Pippo: posizione, yaw, inclinazione, braccia (direzioni locali), testa, anche."""
    S_ = dict(loc=(0, 0, 0), yaw=0.0, lean=0.0, head=(0, 0, 0), hL=0.0, hR=0.0, **ARMS_DOWN)
    k = 0.03 * math.sin(t * 30)
    if t < T_FLASH:                                                                     # hook: sulle mura, mani sulla testa
        y_ = yaw_to(P_WALL, sq_path(t)[0])
        S_.update(loc=tuple(P_WALL), yaw=y_, aL=(-0.42 + k, -0.2, 0.9), aR=(0.42 - k, -0.2, 0.9), head=(-0.15, 0, 0))
    elif t < T_LOCK - 0.1:                                                              # esce di casa con la tazza
        p, w = walk(t, T_FLASH + 0.3, T_LOCK - 0.4, HOUSE_DOOR, P_CAS); y_ = yaw_to(HOUSE_DOOR, P_CAS) if w else yaw_to(P_CAS, G_OUTW)
        S_.update(loc=tuple(p), yaw=y_, hL=0.4 * w, hR=-0.4 * w, aR=(0.25, -0.8, 0.3), aL=(-0.14, 0.15 * w, -1), head=(0, 0, -0.5 * ramp(t, 7.2, 7.6)))
    elif t < T_CASS:                                                                    # chiude il lucchetto, soddisfatto
        y_ = yaw_to(P_CAS, CAS_XY); u = ramp(t, T_LOCK, T_LOCK + 0.5); sn = ramp(t, T_LOCK + 0.5, T_LOCK + 0.65)
        S_.update(loc=tuple(P_CAS), yaw=y_, lean=0.15 * u * (1 - sn), aR=(0.05, -1.0, 0.25 - 0.3 * sn), aL=(-0.05, -1.0, 0.25 - 0.3 * sn) if sn < 1 else (-0.45, -0.3, 0.8),
                  head=(0.1, 0, 0) if sn < 1 else (-0.1, 0, 0))
    elif t < T_BUILD - 0.1:                                                             # Gualtiero si porta via la cassetta: Pippo resta con le mani sospese
        gx_ = gp(t)['loc']; y_ = yaw_to(P_CAS, gx_)
        S_.update(loc=tuple(P_CAS), yaw=yaw_to(P_CAS, CAS_XY), head=(0, 0, max(-1.2, min(1.2, y_ - yaw_to(P_CAS, CAS_XY)))), aL=(-0.3, -0.9, 0.2), aR=(0.3, -0.9, 0.2))
        if t > T_CASS + 1.35: S_.update(**braccia('arrabbiato'))
    elif t < T_CAMS:                                                                    # costruisce la base: col caschetto, braccia al cielo sulla parolaccia
        up = ramp(t, T_CAZZO, T_CAZZO + 0.3)
        S_.update(loc=tuple(P_BUILD), yaw=PI + 0.15, aL=(-0.5, -0.1 * up, 0.85 * up - 0.4 * (1 - up)), aR=(0.5, -0.1 * up, 0.85 * up - 0.4 * (1 - up)), head=(-0.2 * up, 0, 0))
    elif t < T_ROOM:                                                                    # (fuori campo) poi in sala di controllo
        S_.update(loc=tuple(P_ROOM), yaw=PI, aL=(-0.2, -0.9, -0.2), aR=(0.2, -0.9, -0.2))
    elif t < T_KNOCK - 0.25:                                                            # sala di controllo: si gira verso Tumbo, poi guarda gli schermi
        tr = ramp(t, T_ROOM, T_ROOM + 0.25) * (1 - ramp(t, T_WATCH - 0.1, T_WATCH + 0.2)); lean = 0.18 * ramp(t, T_ZOOM - 0.4, T_ZOOM)
        S_.update(loc=tuple(P_ROOM), yaw=PI, lean=lean, head=(0, 0, -1.1 * tr), aL=(-0.2, -0.95, -0.25), aR=(0.2, -0.95, -0.25))
    elif t < T_KT - 0.1:                                                                # va da Gualtiero e bussa sulla sua testa
        y_ = yaw_to(P_KN, G_CAS); kn = 0.12 * math.sin((t - T_KK) * 26) if T_KK < t < T_KK + 0.6 else 0.0
        up = ramp(t, T_KNOCK, T_KNOCK + 0.5) * (1 - ramp(t, T_MACHE - 0.3, T_MACHE)); look = ramp(t, T_MACHE, T_MACHE + 0.4)
        S_.update(loc=tuple(P_KN), yaw=y_, aR=(-0.3, -0.5, 0.81 + kn) if up > 0.5 else (0.14, 0, -1), lean=-0.08 * look, head=(-0.35 * look, 0, 0))
        if T_GIULIA - 0.1 < t: S_.update(**braccia('spaventato'))
    elif t < T_SELF - 0.1:                                                              # si gira lentamente verso Tumbo e bussa sulla sua testa
        y0 = yaw_to(P_KN, G_CAS); y1 = yaw_to(P_KN, T_KN); u = ramp(t, T_KT, T_KT + 0.9)
        kn = 0.12 * math.sin((t - T_KTK) * 26) if T_KTK < t < T_KTK + 0.6 else 0.0; dn = ramp(t, T_KT + 0.8, T_KT + 1.2) * (1 - ramp(t, T_ALTRA - 0.6, T_ALTRA - 0.3))
        S_.update(loc=tuple(P_KN), yaw=y0 + (y1 - y0) * u, lean=0.45 * dn, aR=(0.0, -0.75, -0.55 + kn) if dn > 0.3 else (0.14, 0, -1), head=(0.25 * dn, 0, 0))
        if T_ALTRA - 0.1 < t: S_.update(**braccia('spaventato'))
    else:                                                                               # bussa sulla propria testa: niente si apre. «Occupato.»
        kn = 0.1 * math.sin((t - T_SELFK) * 24) if T_SELFK < t < T_SELFK + 0.6 else 0.0; up = ramp(t, T_SELF, T_SELF + 0.45) * (1 - ramp(t, T_OCC + 0.35, T_OCC + 0.7))
        S_.update(loc=tuple(P_KN), yaw=yaw_to(P_KN, (P_KN.x + 0.6, P_KN.y - 3.0)), aR=(-0.35, -0.12, 0.93 + kn) if up > 0.5 else (0.14, 0, -1), head=(-0.05, 0, 0))
    return S_

JOLTS = [(0.05, 0.12), (T_CASS + 0.75, 0.22), (T_MACHE + 1.15, 0.22), (T_GIULIA, 0.34), (T_ALTRA, 0.3), (T_OCC + 0.12, 0.18), (T_FLUSH + 0.1, 0.3)]
def jolt(S_, t):
    """salto e scatto all'indietro di Pippo quando si spaventa (emozioni esagerate)"""
    for (t0, h) in JOLTS:
        if t0 <= t < t0 + 0.42:
            u = (t - t0) / 0.42; l_ = S_['loc']; S_['loc'] = (l_[0], l_[1], l_[2] + h * math.sin(PI * u)); S_['lean'] = S_['lean'] - 0.12 * math.sin(PI * u)
            S_['head'] = (S_['head'][0] - 0.3 * math.sin(PI * u), S_['head'][1], S_['head'][2] + 0.15 * math.sin(3 * PI * u))
    return S_
_pp_raw = None

def gp(t):
    """Gualtiero: posizione, yaw, braccia (rotazioni euler delle spalle), anche, testa, inclinazione."""
    S_ = dict(loc=(0, 0, 0), yaw=0.0, lean=0.0, sL=(0, 0, 0), sR=(0, 0, 0), hL=0.0, hR=0.0, head=(0, 0, 0))
    jerk = lambda x, step=0.18: math.floor(x / step) * step                             # movimenti a scatti, da robot
    if t < T_FLASH:                                                                     # hook: in piedi sullo squalo come su un surf
        p, a, _ = sq_path(t); back = Vector((math.sin(a), -math.cos(a), 0)) * -0.28
        S_.update(loc=(p.x + back.x, p.y + back.y, p.z + 0.27), yaw=a + 1.35, sL=(0, -1.15, 0), sR=(-1.1, 0, -0.25), hL=0.32, hR=-0.32)
    elif t < T_CASS:                                                                    # prende il giornale dalla cassetta e se ne va a scatti
        tj = jerk(t, 0.12)
        if tj < T_FLASH + 0.6:
            S_.update(loc=tuple(G_CAS + Vector((-0.1, -0.1, 0))), yaw=yaw_to(G_CAS, CAS_XY), sR=(-1.25, 0, 0))
        else:
            p, w = walk(tj, T_FLASH + 0.6, T_FLASH + 3.6, G_CAS, G_OUTW); S_.update(loc=tuple(p), yaw=yaw_to(G_CAS, G_OUTW), hL=0.45 * w, hR=-0.45 * w, sR=(-1.1, 0, -0.25), sL=(0.4 * w, 0, 0))
    elif t < T_BUILD:                                                                   # torna e si porta via la cassetta sotto il braccio
        tj = jerk(t, 0.12)
        if tj < T_CASS + 0.45: p, w = walk(tj, T_CASS - 0.3, T_CASS + 0.4, G_CAS + Vector((-1.5, 0, 0)), G_CAS); S_.update(loc=tuple(p), yaw=yaw_to(G_CAS, CAS_XY), hL=0.45 * w, hR=-0.45 * w)
        else:
            p, w = walk(tj, T_CASS + 0.75, T_BUILD, G_CAS, G_OUTW); S_.update(loc=tuple(p), yaw=yaw_to(G_CAS, G_OUTW), hL=0.45 * w, hR=-0.45 * w, sL=(0, 0, -0.9), sR=(0.3 * w, 0, 0))
    elif t < T_DANCE:
        S_.update(loc=(G_OUTW.x, G_OUTW.y, 0))
    elif t < T_DOOR:                                                                    # balla in mezzo ai laser (vista dalla telecamera)
        u = ramp(t, T_DANCE, T_DOOR - 0.15); x0 = BC.x - 1.9; p = Vector((x0 + (G_CAS.x - x0) * u, BC.y - 0.35 + 0.25 * math.sin(t * 3), 0))
        ph = t * 9.0; limbo = 0.5 * ramp(t, T_DANCE + 0.9, T_DANCE + 1.2) * (1 - ramp(t, T_DANCE + 1.6, T_DANCE + 1.9))
        S_.update(loc=(p.x, p.y, -0.35 * limbo), yaw=-PI / 2 + 0.6 * math.sin(t * 4.5), lean=-0.9 * limbo,
                  sL=(-2.3 + 0.6 * math.sin(ph), 0, 0.3), sR=(-2.3 + 0.6 * math.sin(ph + PI), 0, -0.3), hL=0.5 * math.sin(ph), hR=-0.5 * math.sin(ph), head=(0, 0.25 * math.sin(ph * 0.5), 0))
    elif t < T_ROOM:                                                                    # entra dalla porta blindata che gli apre Tumbo
        p, w = walk(t, T_TUMBO + 0.35, T_ROOM + 0.3, DOOR_P + DOOR_D * 1.0 - Vector((-DOOR_D.y, DOOR_D.x, 0)) * 0.75, DOOR_IN - DOOR_D * 0.6)
        S_.update(loc=tuple(p), yaw=yaw_to(DOOR_P + DOOR_D, DOOR_IN), hL=0.45 * w, hR=-0.45 * w, sR=(0.3 * w, 0, 0), sL=(-0.3 * w, 0, 0))
    else:                                                                               # davanti alla cassetta, fermo, occhi spalancati, giornale al contrario
        guida = ramp(t, T_GUIDA, T_GUIDA + 0.25) * (1 - ramp(t, T_KT - 0.3, T_KT))
        wave = 0.35 * math.sin((t - T_GUIDA) * 10) * guida
        S_.update(loc=tuple(G_CAS), yaw=yaw_to(G_CAS, (G_CAS.x + 0.4, G_CAS.y - 3.0)), sR=(-1.1, 0, -0.25), sL=(-2.7 * guida, 0, wave))
    return S_

def tp(t):
    """Tumbo: (posizione, yaw, ritto 0..1)."""
    if t < T_FLASH: return T_WALL, yaw_to(T_WALL, sq_path(t)[0]), 0.0
    if t < T_BUILD:
        p, w = walk(t, T_FLASH + 0.5, T_LOCK - 0.3, HOUSE_DOOR + Vector((0.8, 0, 0)), P_CAS + Vector((0.7, -0.6, 0))); return p, yaw_to(p, CAS_XY) if w == 0 else yaw_to(HOUSE_DOOR, P_CAS), 0.0
    if t < T_DOOR - 0.2: return T_BUILDP, PI + 0.4, 0.0
    if t < T_ROOM: return T_DOORP, yaw_to(T_DOORP, DOOR_P), 1.0 * ramp(t, T_DOOR, T_DOOR + 0.2)
    if t < T_KNOCK - 0.2: return T_ROOMP, PI - 0.3 * ramp(t, T_ROOM, T_ROOM + 0.3), 0.0
    return T_KN, yaw_to(T_KN, P_KN) - 0.3 * ramp(t, T_KT, T_KT + 0.5), 0.0

# ======================= chiavi =======================
def K(o, f, loc=None, rot=None, scale=None):
    if loc is not None: o.location = loc; o.keyframe_insert('location', frame=f)
    if rot is not None: o.rotation_euler = rot; o.keyframe_insert('rotation_euler', frame=f)
    if scale is not None: o.scale = scale if isinstance(scale, (tuple, list)) else (scale,) * 3; o.keyframe_insert('scale', frame=f)
JG, JT = KG['J'], KT['J']
for f in range(1, NF + 1):
    t = (f - 1) / FPS
    s = jolt(pp(t), t); K(P['root'], f, s['loc'], (s['lean'], 0, s['yaw']))
    for nm, k_ in (('L', 'aL'), ('R', 'aR')):
        sh = P['shoulder' + nm]; sh.rotation_quaternion = qdir(s[k_]); sh.keyframe_insert('rotation_quaternion', frame=f)
        K(P['hip' + nm], f, rot=(s['h' + nm], 0, 0))
    K(P['head'], f, rot=s['head'])
    g = gp(t); K(GU['root'], f, g['loc'], (g['lean'], 0, g['yaw']))
    K(GU['shoulderL'], f, rot=g['sL']); K(GU['shoulderR'], f, rot=g['sR']); K(GU['hipL'], f, rot=(g['hL'], 0, 0)); K(GU['hipR'], f, rot=(g['hR'], 0, 0)); K(GU['head'], f, rot=g['head'])
    l, yw, up = tp(t); K(Tb['root'], f, tuple(l), (-0.55 * up, 0, yw), 0.75)
    wag = 0.6 * math.sin(t * 14) if (T_ROOM < t < T_WATCH or T_KNOCK < t) else 0.25 * math.sin(t * 6)
    K(Tb['tail'], f, rot=(-1.0 + 0.2 * math.sin(t * 9), 0, wag))
    for nm, sg in (('L', 1), ('R', -1)): K(Tb['legF' + nm], f, rot=(up * (-1.3 + (0.35 * sg * math.sin(t * 8) if T_DOOR < t < T_TUMBO + 0.4 else 0.0)), 0, 0))
    # squalo e pinne
    p, a, _ = sq_path(t); K(SQ['root'], f, tuple(p), (0, 0, a)); K(SQ['tail'], f, rot=(0, 0, 0.35 * math.sin(t * 7)))
    K(SQ['jaw'], f, rot=(0.15 + 0.35 * max(0.0, math.sin(t * 3.0)), 0, 0))
    for k_, fe in enumerate(FINS):
        a2 = a + 2.1 * (k_ + 1); K(fe, f, tuple(on_circle(HOOK_R + (0.5 if k_ else -0.6), a2, 0.02)), (0, 0, a2))
    # base: le mura salgono dal prato, la torretta, poi telecamere e laser saltano fuori
    if t >= T_FLASH:
        u = ramp(t, T_BASE, T_BASE + 1.1); ov = 1.0 + 0.08 * math.sin(PI * ramp(t, T_BASE + 0.8, T_BASE + 1.4))
        K(BROOT, f, scale=(1.0, 1.0, max(0.01, u * ov)))
    else: K(BROOT, f, scale=1.0)
    K(B['tower'], f, scale=(1.0, 1.0, max(0.01, ramp(t, T_BASE + 0.7, T_BASE + 1.3))) if t >= T_FLASH else 1.0)
    for i, c_ in enumerate(B['cams']):
        u = ramp(t, T_CAMS + 0.08 * i, T_CAMS + 0.08 * i + 0.2) if t >= T_FLASH else 1.0; K(c_, f, scale=max(0.01, u * (1 + 0.25 * math.sin(PI * u))))
    u = ramp(t, T_CAMS, T_CAMS + 0.2); K(TOWERCAM, f, scale=0.8 * max(0.01, u * (1 + 0.3 * math.sin(PI * u))))
    K(B['laser_root'], f, scale=(1.0, 1.0, max(0.01, ramp(t, T_LASER, T_LASER + 0.15))) if t >= T_FLASH else 1.0)
    # porta blindata: Tumbo gira la ruota, la porta si apre verso l'interno
    op = ramp(t, T_TUMBO + 0.15, T_TUMBO + 0.65) * (1 - ramp(t, T_ROOM + 0.4, T_ROOM + 0.8)) if t < T_KNOCK else 0.0
    K(B['door'], f, rot=(0, 0, B['door'].rotation_euler.z if f == 1 else DOORZ0 - 1.6 * op)) if f > 1 else None
    if f == 1: DOORZ0 = B['door'].rotation_euler.z; K(B['door'], f, rot=(0, 0, DOORZ0))
    K(B['wheel'], f, rot=(0, 2.5 * ramp(t, T_DOOR, T_TUMBO + 0.2), 0))
    # cassetta: sportello aperto quando Gualtiero prende il giornale; poi va via sotto il suo braccio
    if T_FLASH <= t < T_BUILD:
        if t < T_CASS + 0.75: K(CAS1['root'], f, (BC.x, BC.y, 0.0), (0, 0, 0))
        else:
            gl = gp(t)['loc']; yw_ = gp(t)['yaw']; off = Vector((-0.55, 0.0, 0.72)); off.rotate(Euler((0, 0, yw_))); K(CAS1['root'], f, (gl[0] + off.x, gl[1] + off.y, gl[2] + 0.72), (PI / 2 - 0.2, 0, yw_ + PI / 2))
        K(CAS1['door'], f, rot=(1.6 * ramp(t, T_FLASH - 0.1, T_FLASH + 0.2) * (1 - ramp(t, T_FLASH + 0.8, T_FLASH + 1.0)), 0, 0))
    if f == 1: K(CAS1['root'], f, (BC.x, BC.y, 0.0), (0, 0, 0))
    # lucchetto sullo sportello della cassetta
    if f == 1: LOCK.parent = CAS1['root']; LOCK.location = (0, -0.31, 1.0)
    sn = ramp(t, T_LOCK + 0.4, T_LOCK + 0.65); K(LOCK, f, loc=(0, -0.31 - 0.3 * (1 - sn), 1.0 + 0.1 * (1 - sn)), rot=(0, 0, 0))
    # il cranio di Gualtiero si apre (all'indietro), poi quello di Tumbo
    og = ramp(t, T_MACHE + 0.15, T_MACHE + 1.3); ogs = og + 0.06 * math.sin(PI * ramp(t, T_MACHE + 1.1, T_MACHE + 1.5))
    K(KG['hinge'], f, rot=(-1.95 * ogs, 0, 0))
    ot = ramp(t, T_ALTRA - 0.35, T_ALTRA + 0.25); K(KT['hinge'], f, rot=(-1.95 * ot, 0, 0))
    # Giulia nella testa di Gualtiero: si gira, saluta, guida col mattarello; quella di Tumbo saluta l'altra
    lookup = ramp(t, T_GIULIA - 0.2, T_GIULIA + 0.3)
    K(JG['root'], f, rot=(-0.25 * lookup, 0, 0.0))
    wav = math.sin((t - T_GIULIA) * 12) * ramp(t, T_GIULIA + 0.2, T_GIULIA + 0.4) * (1 - ramp(t, T_GUIDA - 0.2, T_GUIDA))
    steer = math.sin((t - T_GUIDA) * 10) * ramp(t, T_GUIDA, T_GUIDA + 0.2) * (1 - ramp(t, T_KT - 0.3, T_KT))
    hi = ramp(t, T_ALTRA + 0.7, T_ALTRA + 0.9)
    wv_on = ramp(t, T_GIULIA + 0.1, T_GIULIA + 0.3) * (1 - ramp(t, T_GUIDA - 0.2, T_GUIDA))
    K(JG['shoulderL'], f, rot=(-1.05 - 1.9 * max(wv_on, hi), 0, -0.1 - 0.35 * wav - 0.3 * math.sin(t * 12) * hi))
    K(JG['shoulderR'], f, rot=(-1.05 - 0.25 * steer, 0, 0.1 + 0.3 * steer))
    K(JT['shoulderL'], f, rot=(-1.05 - 1.9 * hi, 0, -0.1 + 0.3 * math.sin(t * 12) * hi))
    K(JT['root'], f, rot=(-0.2 * ramp(t, T_ALTRA, T_ALTRA + 0.4), 0, 0))

# ======================= espressioni =======================
_last = {}
def _ex(key, fn, t, k):
    if key in _last and t - 0.06 > _last[key][1]: fn(fr(t - 0.06), **_last[key][0])
    fn(fr(t), **k); _last[key] = (k, t)
# Pippo usa SOLO le emozioni esagerate di pippo2 (pippo2.EMOZIONI_FORTI, regola dell'autore: «bisogna usare solo quelle anche nei prossimi video»).
# Faccia, sopracciglia, busto e segni da cartone vengono dal catalogo; braccia e testa restano alla coreografia (pp), che nei momenti di
# spavento usa le braccia del catalogo. Gli occhi non cambiano mai misura.
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
    """emozione esagerata del catalogo al tempo t (la precedente resta fino a 0,06 s prima)."""
    if _emo_last[0] and t - 0.06 > _emo_last[0][2]: _emo_key(fr(t - 0.06), _emo_last[0][0], _emo_last[0][1])
    _emo_key(fr(t), nome, forza); _emo_last[0] = (nome, forza, t)
def tex(t, **k): _ex('t', lambda f, **kk: tumbo.tumbo_express(Tb, f, **kk), t, k)
def gx(t, **k): _ex('g', lambda f, **kk: props009.gex(GU, f, **kk), t, k)
def jex(t, J, key, **k): _ex(key, lambda f, **kk: giulia.giex(J, f, **kk), t, k)
emo(0.0, 'spaventato'); emo(T_FLASH, 'normale'); emo(T_FLASH + 1.85, 'sorpreso', 0.8)
emo(T_LOCK + 0.1, 'furbo'); emo(T_LOCK + 0.7, 'felice')
emo(T_CASS + 0.6, 'sorpreso'); emo(T_CASS + 1.35, 'arrabbiato')
emo(T_BUILD, 'furbo'); emo(T_CAZZO, 'ride'); emo(T_CAMS - 0.1, 'felice')
emo(T_ROOM, 'sorpreso', 0.8); emo(T_ROOM + 0.35, 'furbo', 0.9); emo(T_WATCH, 'arrabbiato', 0.6); emo(T_ZOOM, 'arrabbiato', 0.9)
emo(T_KNOCK, 'arrabbiato', 0.5); emo(T_MACHE, 'sorpreso')
for k_ in range(7): emo(T_GIULIA + 0.12 * k_, 'spaventato', 1.0 if k_ % 2 == 0 else 0.75)          # la bocca che trema
emo(T_KT, 'sorpreso', 0.6)
for k_ in range(5): emo(T_ALTRA + 0.12 * k_, 'spaventato', 1.0 if k_ % 2 == 0 else 0.75)
emo(T_SELF, 'triste', 0.6); emo(T_OCC + 0.15, 'sorpreso'); emo(T_FLUSH + 0.25, 'spaventato')
gx(0.0, brow=0.0, mouth=0.0, look=(0, 0)); gx(T_GUIDA, brow=0.0, mouth=0.3, look=(0.6, 0)); gx(T_KT, brow=0.0, mouth=0.0, look=(0, 0))
tex(0.0, eye_open=1.0, tongue=0.0); tex(T_FLASH, tongue=0.8)
tex(T_DOOR - 0.1, tongue=0.0, eye_scale=1.15, look=(0, 0)); tex(T_ROOM, tongue=1.0, eye_scale=1.0); tex(T_KNOCK, tongue=0.0)
tex(T_KT + 0.5, tongue=0.0, brow=-0.3); tex(T_ALTRA + 0.3, tongue=1.0)
jex(0.0, JG, 'jg', brow=0.5, mouth=0.1, lid=0.4, look=(0, 0.3)); jex(T_GIULIA + 0.2, JG, 'jg', brow=0.2, mouth=0.6, lid=0.2, look=(0, 1.0), naso=0.6)
jex(T_GIULIA + 0.9, JG, 'jg', brow=0.2, mouth=0.6, lid=0.2, look=(0, 1.0), naso=-0.6); jex(T_GIULIA + 1.6, JG, 'jg', brow=0.2, mouth=0.6, lid=0.2, look=(0, 1.0), naso=0.5)
jex(T_GUIDA, JG, 'jg', brow=0.8, mouth=0.4, lid=0.3, look=(0, 0), naso=-0.3); jex(T_ALTRA + 0.7, JG, 'jg', brow=0.1, mouth=0.7, lid=0.2, look=(1.0, 0.2), naso=0.5)
jex(0.0, JT, 'jt', brow=0.3, mouth=0.2, lid=0.3); jex(T_ALTRA + 0.2, JT, 'jt', brow=0.2, mouth=0.7, lid=0.2, look=(0, 1.0), naso=-0.5); jex(T_ALTRA + 0.8, JT, 'jt', brow=0.1, mouth=0.7, lid=0.2, look=(-1.0, 0.2), naso=0.6)

# ======================= effetti =======================
FXC = prc
def fx(name, pos, w, t0, dur, **k): return A.effetto(name, posizione=pos, larghezza=w, animazione=(fr(t0), int(dur * FPS)), collezione=FXC, **k)
def gear(t):
    """posizione dell'orecchio di Gualtiero al tempo t (per il vapore)."""
    g = gp(t); o = Vector((0.33, 0.0, 1.78)); o.rotate(Euler((0, 0, g['yaw']))); return (g['loc'][0] + o.x, g['loc'][1] + o.y, g['loc'][2] + o.z)
for t_ in (1.5, 4.5, T_FLASH + 0.9, T_CASS + 0.6, T_DANCE + 1.3, T_EYES + 0.3, T_EYES + 1.3, T_KNOCK + 1.5):                                          # vapore dall'orecchio di Gualtiero (indizio)
    fx('sbuffo_bianco/whitepuff%02d' % (int(t_ * 3) % 24), gear(t_), 0.22, t_, 0.6, opacita=0.75)
for t_ in (T_TUMBO - 0.4, T_TUMBO + 0.2):                                                         # ... e da quello di Tumbo, quando apre la porta
    fx('sbuffo_bianco/whitepuff05', (T_DOORP.x, T_DOORP.y, 1.05), 0.2, t_, 0.6, opacita=0.75)
for k in range(9):                                                                                 # la base sale dal prato: polvere tutto attorno
    a_ = k * 2 * PI / 9; p_ = on_circle(RW + 0.4, a_, 0.6)
    fx('sbuffo_bianco/whitepuff%02d' % (k * 2), tuple(p_), 2.4, T_BASE + 0.05 * k, 1.0, colore=(0.92, 0.88, 0.8), opacita=0.85)
for k in range(5): fx('particelle/star_0%d' % (k % 4 + 1), tuple(on_circle(0.9, k * 1.25, 1.0 + 0.2 * k)), 0.5, T_LASER + 0.02 * k, 0.4, colore=(1.0, 0.3, 0.2), luce=2.0)
fx('emoticon/question', (P_ROOM.x, P_ROOM.y, 2.35), 0.4, T_ROOM + 0.3, 0.8)
fx('emoticon/exclamations', (P_KN.x, P_KN.y, 2.45), 0.45, T_GIULIA + 0.05, 0.8)
fx('particelle/star_04', (G_CAS.x, G_CAS.y, 2.15), 0.35, T_GIULIA - 0.1, 0.45, colore=(1.0, 0.9, 0.4), luce=2.0)
for k in range(4): fx('sbuffo_bianco/whitepuff1%d' % k, tuple(sq_path(0.4 + k * 0.7)[0] + Vector((0, 0, 0.1))), 0.8, 0.4 + k * 0.7, 0.5, opacita=0.6)

# ======================= camera =======================
def gpos(t, dz=0.0): g = gp(t)['loc']; return (g[0], g[1], g[2] + dz)
def ppos(t, dz=0.0): p_ = pp(t)['loc']; return (p_[0], p_[1], p_[2] + dz)
HOOKC = on_circle(HOOK_R + 4.6, PI + 0.42, 1.25)
TOPG = (G_CAS.x, G_CAS.y, 1.97); TOPT = None
bpy.context.view_layer.update()
TBH = Tb['head'].matrix_world.translation.copy()
def tumbo_head(t):
    l, yw, up = tp(t); hl = Vector((0, -0.42, 0.28 + 0.0)) * 0.75; hl.rotate(Euler((0, 0, yw))); return Vector(l) + hl + Vector((0, 0, 0.5 * 0.75 + 0.0))
CCTV1 = on_circle(RW - 0.75, -PI * 0.3, 2.8); CCTV2 = on_circle(RW - 0.75, -PI * 0.42, 2.8)
RC = Vector((RX, 0, 0))
D_IN = DOOR_P + DOOR_D * 2.6 + Vector((-DOOR_D.y, DOOR_D.x, 0)) * 1.7
SHOTS = [  # t0, t1, camera da, a, mira da, a, lente, diaframma, cornice REC
    (0.0, 3.0, tuple(HOOKC + Vector((0, 0, 1.4))), tuple(HOOKC + Vector((0, 0, 0.7))), tuple(on_circle(HOOK_R, PI + 0.45, 1.3)), tuple(on_circle(HOOK_R, PI + 0.15, 1.2)), 26, 9, False),
    (3.0, 6.05, None, None, None, None, 32, 5, False),                                                                                                               # 01b sullo squalo, piu' vicino     # 01 hook: Gualtiero sullo squalo
    (6.05, T_FLASH, None, None, None, None, 50, 3.5, False),                                                                                                           # 02 il giornale (segue Gualtiero)
    (T_FLASH, T_LOCK - 0.15, (BC.x + 3.4, BC.y - 5.6, 1.9), (BC.x + 3.0, BC.y - 5.2, 1.85), (BC.x - 0.4, BC.y + 0.4, 1.0), (BC.x - 0.9, BC.y + 0.2, 1.0), 28, 8, False),  # 03 ogni mattina
    (T_LOCK - 0.15, T_CASS, (BC.x + 0.9, BC.y - 1.75, 1.45), (BC.x + 0.85, BC.y - 1.65, 1.4), (BC.x + 0.05, BC.y - 0.25, 1.1), (BC.x + 0.05, BC.y - 0.25, 1.1), 40, 4, False),  # 04 il lucchetto
    (T_CASS, T_BUILD, (BC.x + 2.6, BC.y - 4.4, 1.6), (BC.x + 2.2, BC.y - 4.6, 1.6), (BC.x - 0.6, BC.y + 0.2, 1.0), (BC.x - 2.6, BC.y, 1.0), 28, 8, False),            # 05 si porta via la cassetta
    (T_BUILD, T_CAMS, (BC.x - 10.5, BC.y - 15.0, 8.0), (BC.x - 9.0, BC.y - 14.0, 6.2), (BC.x, BC.y - 1.5, 0.8), (BC.x, BC.y - 1.0, 1.2), 24, 11, False),              # 06 UNA CAZZO DI BASE
    (T_CAMS, T_LASER, (T_BUILDP.x - 0.35, T_BUILDP.y + 1.55, 1.0), (T_BUILDP.x - 0.3, T_BUILDP.y + 1.4, 0.98), (T_BUILDP.x, T_BUILDP.y, 0.75), (T_BUILDP.x, T_BUILDP.y, 0.78), 38, 4, False),  # 07 telecamere (anche su Tumbo)
    (T_LASER, T_MOAT, (BC.x + 1.75, BC.y - 1.95, 1.9), (BC.x + 1.65, BC.y - 1.85, 1.85), (BC.x, BC.y, 0.85), (BC.x, BC.y, 0.85), 26, 8, False),                              # 08 laser
    (T_MOAT, T_DANCE, None, None, None, None, 26, 9, False),  # 09 il fossato con gli squali
    (T_DANCE, T_DOOR, tuple(CCTV1), tuple(CCTV1), (BC.x - 1.0, BC.y - 0.3, 0.75), (BC.x - 0.5, BC.y - 0.3, 0.8), 30, 64, True),                                            # 10 ballando (telecamera)
    (T_DOOR, T_ROOM, tuple(D_IN + Vector((0, 0, 1.3))), tuple(D_IN + Vector((0, 0, 1.25)) - DOOR_D * 0.2), tuple(DOOR_P - DOOR_D * 0.8 + Vector((0, 0, 0.85))), tuple(DOOR_P - DOOR_D * 0.8 + Vector((0, 0, 0.85))), 26, 7, False),  # 11 la porta blindata, Tumbo
    (T_ROOM, T_WATCH, (RX + 0.05, 1.4, 1.6), (RX + 0.05, 1.35, 1.6), (RX + 0.15, -0.33, 1.15), (RX + 0.15, -0.33, 1.15), 20, 5, False),                                  # 12 sala: Pippo si gira, Tumbo scodinzola
    (T_WATCH, T_ZOOM, (RX - 1.9, -1.9, 2.3), (RX - 1.7, -1.6, 2.25), (RX + 0.3, 1.6, 1.65), (RX + 0.3, 1.6, 1.65), 22, 8, False),                                        # 13 riguarda le telecamere
    (T_ZOOM, T_EYES, tuple(CCTV2), tuple(CCTV2), (G_CAS.x, G_CAS.y, 1.55), (G_CAS.x, G_CAS.y, 1.75), 28, 64, True),                                                       # 14 zoom (telecamera)
    (T_EYES, T_KNOCK, tuple(CCTV2), tuple(CCTV2), (G_CAS.x, G_CAS.y, 1.86), (G_CAS.x, G_CAS.y, 1.86), 150, 64, True),                                                     # 15 non sbatte mai le palpebre
    (T_KNOCK, T_MACHE, (G_CAS.x + 0.55, G_CAS.y - 2.2, 1.75), (G_CAS.x + 0.5, G_CAS.y - 2.0, 1.8), (G_CAS.x + 0.35, G_CAS.y, 1.65), (G_CAS.x + 0.3, G_CAS.y, 1.75), 34, 6, False),  # 16 Pippo bussa
    (T_MACHE, T_GIULIA, (G_CAS.x + 0.15, G_CAS.y - 1.35, 2.25), (G_CAS.x + 0.12, G_CAS.y - 1.2, 2.3), (G_CAS.x, G_CAS.y, 1.95), (G_CAS.x, G_CAS.y, 1.95), 45, 4, False),  # 17 Ma che cazzo... si apre
    (T_GIULIA, T_GUIDA, (G_CAS.x + 0.1, G_CAS.y - 0.42, 2.42), (G_CAS.x + 0.08, G_CAS.y - 0.36, 2.36), (G_CAS.x, G_CAS.y - 0.01, 1.83), (G_CAS.x, G_CAS.y, 1.83), 42, 2.8, False),  # 18 dentro c'e' GIULIA
    (T_GUIDA, T_KT, (G_CAS.x + 1.3, G_CAS.y - 2.25, 1.95), (G_CAS.x + 1.25, G_CAS.y - 2.15, 1.95), (G_CAS.x + 0.3, G_CAS.y, 1.55), (G_CAS.x + 0.3, G_CAS.y, 1.6), 34, 6, False),  # 19 che guida Gualtiero
    (T_KT, T_ALTRA - 0.4, (BC.x + 1.25, BC.y - 2.45, 1.2), (BC.x + 1.2, BC.y - 2.35, 1.2), ((P_KN.x + T_KN.x) / 2, (P_KN.y + T_KN.y) / 2, 0.9), ((P_KN.x + T_KN.x) / 2, (P_KN.y + T_KN.y) / 2, 0.9), 30, 6, False),  # 20 bussa su Tumbo
    (T_ALTRA - 0.4, T_SELF, None, None, None, None, 42, 2.8, False),                                                                                                    # 21 un'altra Giulia (dall'alto sulla testa di Tumbo)
    (T_SELF, T_BLACK, (P_KN.x + 0.45, P_KN.y - 2.1, 1.85), (P_KN.x + 0.43, P_KN.y - 1.95, 1.85), (P_KN.x, P_KN.y, 1.75), (P_KN.x, P_KN.y, 1.78), 40, 4, False),           # 22 Occupato
    (T_BLACK, TOTAL + 0.1, (2000, 0, 0), (2000, 0, 0), (2000, 1, 0), (2000, 1, 0), 30, 8, False),                                                                        # 23 nero
]
REC = props018.cornice_rec(cac, Q, cam, font=FONT, nome='CAM 3')
scene.frame_set(fr(T_ALTRA)); bpy.context.view_layer.update(); TBHEAD = Tb['head'].matrix_world.translation.copy(); scene.frame_set(1)
recs = [(s[0], s[1]) for s in SHOTS if s[8]]
show(REC, recs)
bx('Buio', (1998, -2, -2), (2002, 2, 2), material('P18_buio', (0, 0, 0), rough=1.0), envc)
for f in range(1, NF + 1):
    t = (f - 1) / FPS
    s_ = next((s for s in SHOTS if s[0] <= t < s[1]), SHOTS[-1]); u = (t - s_[0]) / (s_[1] - s_[0])
    if s_[2] is None and s_[0] == 3.0:                                          # sullo squalo: la camera lo segue di tre quarti
        gg = gp(t); yw_ = gg['yaw']; fw = Vector((math.sin(yw_), -math.cos(yw_), 0)); sd = Vector((math.cos(yw_), math.sin(yw_), 0))
        g = Vector(gpos(t, 0.9)); cl = g + fw * 3.4 + sd * 1.2 + Vector((0, 0, 0.55)); tl = g
    elif s_[2] is None and s_[0] == 6.05:                                         # il giornale in mano a Gualtiero, segue lo squalo
        gg = gp(t); yw_ = gg['yaw']; fw = Vector((math.sin(yw_), -math.cos(yw_), 0)); sd = Vector((math.cos(yw_), math.sin(yw_), 0))
        g = Vector(gpos(t, 1.45)); cl = g + fw * 1.75 + sd * 0.35 + Vector((0, 0, 0.15)); tl = g + sd * 0.12
    elif s_[2] is None and s_[0] == T_MOAT:                                     # il fossato: la camera segue lo squalo dal bordo
        p_, a_, _ = sq_path(t); cl = on_circle(HOOK_R + 2.4, a_ - 0.45, 0.75); tl = p_ + Vector((0, 0, 0.3))
    elif s_[2] is None:                                                         # dall'alto sulla testa di Tumbo
        th_ = TBHEAD; yw_ = tp(t)[1]; fw = Vector((math.sin(yw_), -math.cos(yw_), 0)); sd = Vector((math.cos(yw_), math.sin(yw_), 0))
        cl = th_ - sd * 0.42 + fw * 0.22 + Vector((0, 0, 0.5)); tl = th_ + Vector((0, 0, 0.02))
    else:
        cl = Vector(lerp(s_[2], s_[3], u)); tl = Vector(lerp(s_[4], s_[5], u))
    lens = s_[6]
    if s_[0] == T_ZOOM: lens = (28, 55, 95)[min(2, int((t - T_ZOOM) / 0.33))]                     # zoom a scatti della telecamera di sorveglianza
    cam.location = cl; tgt.location = tl; camd.lens = lens; camd.dof.aperture_fstop = s_[7]
    REC.scale = (35.0 / lens,) * 3; REC.location = (0, 0, -0.6 * 35.0 / lens * 0 - 0.6); REC.keyframe_insert('scale', frame=f)
    cam.keyframe_insert('location', frame=f); tgt.keyframe_insert('location', frame=f); camd.keyframe_insert('lens', frame=f); camd.dof.keyframe_insert('aperture_fstop', frame=f)

# luci della sala di controllo (luce «cinema» con i due personaggi davanti agli schermi)
LR = luci.cinema(prc, (RX, -0.3, 1.3), (RX + 0.1, -2.6, 1.55), distanza=3.0, nome='Sala', lato=1)
for o in LR.values(): show(o, [(T_ROOM - 0.05, T_ZOOM)])
SUN.data.energy = 4.5; SUN.data.keyframe_insert('energy', frame=1)
for (t_, v) in ((T_ROOM, 0.6), (T_ZOOM, 4.5)): SUN.data.energy = v; SUN.data.keyframe_insert('energy', frame=fr(t_))

# alleggerisci: la sala di controllo si vede solo quando serve
bpy.context.view_layer.update()
for o in list(prc.objects):
    if o.parent is None and o.name.startswith(('SalaControllo', 'Schermo', 'Tastiera', 'LedSala')): show(o, [(T_ROOM - 0.05, T_ZOOM)])

def lin(idb):
    for fc in all_fcurves(idb):
        kind = 'CONSTANT' if 'hide' in fc.data_path else 'LINEAR'
        for kp in fc.keyframe_points: kp.interpolation = kind
for o in bpy.data.objects: lin(o)
for l_ in bpy.data.lights: lin(l_)
set_interp(camd, 'CONSTANT')
for nm in ('Cam', 'CamTarget'):
    for fc in all_fcurves(bpy.data.objects[nm]):
        for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'
try: scene.render.use_motion_blur = True; scene.render.motion_blur_shutter = 0.06
except Exception: pass
os.makedirs(os.path.dirname(os.path.abspath(BLEND)), exist_ok=True)
import json; json.dump([[round(s[0], 3), round(min(s[1], TOTAL), 3)] for s in SHOTS], open(os.path.join(os.path.dirname(os.path.abspath(BLEND)), 'shots.json'), 'w'))
bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(BLEND)); print('SAVED', BLEND, len(bpy.data.objects), 'oggetti')
