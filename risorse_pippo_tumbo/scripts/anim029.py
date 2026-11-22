"""Video 029 - LA GUERRA PER IL PETROLIO (copione n. 29C v5). Salva ../t029/pippo_t029.blend
Scelte dell'autore (schede/scelta029.jpg): T1 T-rex verde, P1 pompa a cavallo, D2 distributore moderno.
Posti: deserto (origine), sottosuolo con il lago di petrolio (x = -400), piazza del comizio (x = 300), tetto di Pippo (x = 600), distributore nel deserto (x = 900).
Voce: audio/voce_t029.mp3 (44,2 s), tempi in audio/words_t029.json. Personaggi inventati: Cappellone e Rospina; il paese nominato nella voce non compare mai (niente bandiere, leader o luoghi veri).
Uso: python anim029.py"""
import sys, math, os, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from mathutils import Vector, Matrix, Euler
from common import *
from render_setup import *
import set004, props009, kitlook, tumbo, luci, rospina, cappellone as cp
import props029 as P9
import pippo2 as pippo
from set004 import ball_
A = kitlook.A

FPS = 24; TOTAL = 45.0; NF = int(TOTAL * FPS)
def fr(t): return max(1, int(round(t * FPS)) + 1)
def sm(x): x = min(1.0, max(0.0, x)); return x * x * (3 - 2 * x)
def ramp(t, a, b): return sm((t - a) / (b - a))
def lerp(a, b, u): return tuple(a[i] + (b[i] - a[i]) * u for i in range(len(a)))
def yaw_to(a, b): return math.atan2(b[0] - a[0], -(b[1] - a[1]))
def qdir(d, rest=(0, 0, -1)): return Vector(rest).rotation_difference(Vector(d).normalized())
def jump(t, t0, t1, h): return h * math.sin(math.pi * ramp(t, t0, t1)) if t0 <= t <= t1 else 0.0
PI = math.pi

# ======================= tempi (dalla voce) =======================
T_GUERRA, T_IRAN, T_CHE, T_MOTIVO, T_STORTO, T_CANNONI, T_PUNTA = 2.44, 3.70, 4.56, 7.46, 8.40, 9.74, 10.22
T_ACCANTO, T_ROSPINA, T_GUINZ, T_SPASSO = 12.38, 13.34, 14.18, 14.92
T_ALLORA, T_YOGA = 18.08, 20.10
T_CONQ, T_TRIV = 22.30, 23.82
T_MA, T_DINO, T_VIVO, T_CAZZO = 24.66, 26.36, 27.34, 28.48
T_TREX, T_BEVE, T_SUCCO = 29.36, 31.16, 32.18
T_PORGE = 33.20
T_PIENO, T_BENZ, T_800, T_PORCA, T_TEAM = 35.98, 37.90, 39.50, 40.90, 42.02

reset_scene(); scene = bpy.context.scene
setup_render(scene, 1080, 1920, samples=4, fps=FPS, frames=NF); scene.frame_end = NF
A.qualita_eevee(preset='equilibrato', riflessi=False, scena=scene); scene.view_settings.exposure = -0.1
envc = collection('Env'); chc = collection('Characters'); prc = collection('Props'); cac = collection('Cameras')
world(scene, top=(0.12, 0.36, 0.95), bottom=(1.0, 0.80, 0.55), strength=1.0)
SKY = luci.cielo_basso(scene.world, 0.45)
M = P9.mats029(); MS = set004.make_mats(); FNT = P9.font()
LUCK = bpy.data.fonts.load(A.font('luckiest'), check_existing=True)
SUN = luci.sole(prc, (-0.15, -1), lato=1, energia=3.6, angolo_alto=38)

camd = bpy.data.cameras.new('Cam'); cam = bpy.data.objects.new('Cam', camd); cac.objects.link(cam); scene.camera = cam
camd.clip_start = 0.05; camd.clip_end = 900; camd.sensor_width = 36
tgt = empty('CamTarget', (0, 0, 1), None, cac)
ct = cam.constraints.new('TRACK_TO'); ct.target = tgt; ct.track_axis = 'TRACK_NEGATIVE_Z'; ct.up_axis = 'UP_Y'
camd.dof.use_dof = True; camd.dof.focus_object = tgt

def m(n, col, **k): return material('T29_' + n, col, **k)
def box(nome, centro, dim, mat, coll=None, parent=None, rot=(0, 0, 0)): return P9.box(nome, centro, dim, mat, coll or prc, parent, rot)
def txt(nome, body, size, mat, loc, rot=(PI / 2, 0, 0), parent=None, ext=0.03, fnt=None, coll=None):
    return P9._txt(coll or prc, nome, body, size, mat, loc, rot, parent, ext, fnt or LUCK)
def K(o, f, loc=None, rot=None, scale=None):
    if loc is not None: o.location = loc; o.keyframe_insert('location', frame=f)
    if rot is not None: o.rotation_euler = rot; o.keyframe_insert('rotation_euler', frame=f)
    if scale is not None: o.scale = scale if isinstance(scale, (tuple, list)) else (scale,) * 3; o.keyframe_insert('scale', frame=f)

# ======================= DESERTO (origine) =======================
P9.deserto(envc, A, raggio=170.0, seme=3, piatto=60.0)
GP = P9.pompa(prc, M); GP['root'].location = (0, 10, 0); GP['root'].rotation_euler = (0, 0, PI / 2); GP['root'].scale = (2.2,) * 3   # il pozzo piu' grande
WELL = Vector((7.9, 10.0, 1.2))                                                                      # testa del pozzo (dalla geometria di pompa(), scala 2,2)
rnd = random.Random(29); PUMPS = []
for k in range(28):
    a = rnd.uniform(0.2, PI - 0.2) if k < 22 else rnd.uniform(-PI, PI); r = rnd.uniform(20, 56)
    p = P9.pompa(prc, M); p['root'].location = (r * math.cos(a), 10 + r * math.sin(a), 0); p['root'].rotation_euler = (0, 0, rnd.uniform(0, 2 * PI)); p['root'].scale = (rnd.uniform(1.1, 1.7),) * 3
    PUMPS.append((p, rnd.uniform(0, 2 * PI), rnd.uniform(2.2, 3.4)))
for k, (x, y, rr) in enumerate(((-24, 34, 18.0), (26, 42, 12.0), (-2, 52, 9.0))):                   # pozze di petrolio («un mare di petrolio»)
    o = shape('Pozza', 'sphere', (x, y, 0.02), (rr, rr * 0.7, 0.05), (0, 0, rnd.uniform(0, PI)), None, M['petrolio'], envc)
CANNONS = []
for k in range(6):
    c = P9.cannone(prc, M, 'Cannone%d' % k); c['root'].location = (-7.5 + 3.0 * k, -12.0, 0); c['root'].rotation_euler = (0, 0, PI + rnd.uniform(-0.9, 0.9))
    CANNONS.append((c, c['root'].rotation_euler.z, 0.0 if k % 2 else -0.35))
FLAG = P9.bandiera_c(prc, M); FLAG['root'] if False else None
FLAGO = bpy.data.objects['BandieraC']
CAPD = (-3.6, 2.4); ROSD = (-5.4, 3.0)                                                               # Cappellone e Rospina al pozzo
TX0 = Vector((14.0, 15.0, 0.0)); TS = 1.6; TYAW = -0.9                                                # dove esce il T-rex
GEY = bpy.data.curves.new('Geyser', 'CURVE'); GEY.dimensions = '3D'; GEY.bevel_depth = 0.38; GEY.bevel_resolution = 4; GEY.use_fill_caps = True
_sp = GEY.splines.new('BEZIER'); _sp.bezier_points.add(1)
GEYO = bpy.data.objects.new('Geyser', GEY); prc.objects.link(GEYO); GEY.materials.append(M['petrolio'])

# ======================= SOTTOSUOLO (x = -400) =======================
XU = -400.0
def tex(aid, dim, riserva, **k):
    try: return A.materiale(aid, dimensione=dim, **k)
    except Exception as e: print('texture mancante', aid, e); return riserva
rock = tex('Rock029', 3.0, m('roccia', (0.35, 0.25, 0.18), rough=0.9), tinta=(0.6, 0.45, 0.35))
box('GrottaFondo', (XU, 9, 4), (40, 1, 14), rock, envc); box('GrottaTetto', (XU, 0, 10.5), (40, 22, 1), rock, envc)
box('GrottaPavimento', (XU, 0, -2.6), (40, 22, 1), rock, envc)
for s_ in (-1, 1): box('GrottaLato', (XU + s_ * 19.5, 0, 4), (1, 22, 14), rock, envc)
box('GrottaDavanti', (XU, -11.5, 4), (40, 1, 14), rock, envc)
shape('LagoPetrolio', 'cyl:1:1', (XU, 1.0, -0.05), (16, 8, 0.1), (0, 0, 0), None, m('lago', (0.01, 0.01, 0.012), rough=0.5, spec=0.5), envc)
for k in range(9):
    o = shape('Stalattite', 'cone', (XU - 14 + 3.4 * k, rnd.uniform(-4, 7), 9.6), (0.5, 0.5, rnd.uniform(1.2, 2.6)), (PI, 0, 0), None, rock, envc)
BUBBLES = []
for k in range(10): BUBBLES.append((ball_('Bolla', 1.0, (XU, 0, -50), M['petrolio'], prc, sc=(0.25, 0.25, 0.25)), rnd.uniform(-7, 7), rnd.uniform(-1, 4), rnd.uniform(0, 3)))
lu = bpy.data.lights.new('LuceGrotta', 'AREA'); lu.size = 4; lu.energy = 900; lu.color = (1.0, 0.62, 0.3); lu.use_shadow = True
LGR = bpy.data.objects.new('LuceGrotta', lu); prc.objects.link(LGR); LGR.location = (XU - 6, -6, 8); luci.punta(LGR, (XU, 2, 0))
lu2 = bpy.data.lights.new('ControGrotta', 'AREA'); lu2.size = 6; lu2.energy = 500; lu2.color = (0.35, 0.55, 1.0); lu2.use_shadow = False
LGR2 = bpy.data.objects.new('ControGrotta', lu2); prc.objects.link(LGR2); LGR2.location = (XU + 6, 8, 7); luci.punta(LGR2, (XU, 0, 2))

# ======================= PIAZZA DEL COMIZIO (x = 300) =======================
XP = 300.0
piazza = tex('PavingStones070', 2.0, m('piazza', (0.6, 0.58, 0.55), rough=0.9))
box('Piazza', (XP, 0, -0.1), (60, 60, 0.2), piazza, envc)
blu = m('fondale', (0.08, 0.18, 0.55), rough=0.6)
box('Fondale', (XP, 4.0, 3.0), (14, 0.3, 6.0), blu, envc)
for i, (r_, mt) in enumerate(((1.2, (0.05, 0.55, 0.2)), (0.82, (0.97, 0.97, 0.97)), (0.42, (0.85, 0.06, 0.06)))):
    shape('CoccardaGrande', 'cyl:1:1', (XP - 4.2, 3.82 - 0.02 * i, 3.6), (r_, r_, 0.03), (PI / 2, 0, 0), None, m('cocc%d' % i, mt, rough=0.5), envc)
txt('Scritta', 'CAPPELLONE', 0.95, m('scritta', (1, 1, 1), rough=0.4), (XP + 1.5, 3.8, 3.9), coll=envc)
txt('Slogan', 'PROMETTO TUTTO', 0.45, m('slogan', (1.0, 0.78, 0.1), rough=0.4), (XP + 1.5, 3.8, 2.8), coll=envc)
legno = tex('WoodFloor043', 1.0, m('legno', (0.5, 0.32, 0.16), rough=0.6), tinta=(0.9, 0.7, 0.55))
box('Leggio', (XP, -0.2, 0.5), (1.3, 0.8, 1.0), legno, envc)
box('LeggioTop', (XP, -0.25, 1.04), (1.45, 0.95, 0.08), legno, envc, rot=(0.12, 0, 0))
for i, (r_, mt) in enumerate(((0.32, 'cocc0'), (0.22, 'cocc1'), (0.11, 'cocc2'))):
    shape('CoccardaLeggio', 'cyl:1:1', (XP, -0.62 - 0.01 * i, 0.75), (r_, r_, 0.02), (PI / 2, 0, 0), None, bpy.data.materials['T29_' + mt], envc)
for k in range(8):
    a_ = -0.9 + 1.8 * k / 7; mx = XP + 0.55 * math.sin(a_); my = -0.62 + 0.15 * abs(math.sin(a_))
    shape('Asta', 'cyl:1:1', (mx, my, 1.15), (0.012, 0.012, 0.22), (0.3, a_ * 0.3, 0), None, M['ferro'], envc)
    ball_('Microfono', 0.05, (mx + 0.03 * math.sin(a_), my - 0.07, 1.27), m('mic%d' % k, [(0.9, 0.1, 0.1), (0.1, 0.4, 0.9), (0.1, 0.7, 0.2), (1, 0.75, 0.1), (0.1, 0.1, 0.1), (0.95, 0.95, 0.95), (0.6, 0.2, 0.8), (1.0, 0.45, 0.1)][k], rough=0.6), envc, sc=(1, 1, 1.4))
for s_ in (-1, 1): box('Transenna', (XP + s_ * 6.5, -2.5, 0.5), (0.1, 3.0, 1.0), M['ferro'], envc)
CAPP = (XP, 0.55); ROSP = (XP + 1.75, 0.2)                                                           # dietro il leggio / accanto
W0 = (XP + 2.6, -1.6); W1 = (XP - 3.2, -1.6)                                                         # la passeggiata

# ======================= TETTO DI PIPPO (x = 600) =======================
XR = 600.0
box('Prato', (XR, 0, -0.1), (160, 160, 0.2), MS['park'], envc)
intonaco = tex('painted_plaster_wall', 3.0, m('intonaco', (0.95, 0.8, 0.6), rough=0.9), tinta=(1.0, 0.86, 0.62))
box('CasaPippo', (XR, 0, 3.0), (8, 7, 6.0), intonaco, envc)
box('Terrazza', (XR, 0, 6.05), (8.2, 7.2, 0.1), tex('PavingStones070', 1.2, m('terrazza', (0.8, 0.6, 0.5), rough=0.9), tinta=(1.0, 0.8, 0.7)), envc)
for (cx, cy, dx, dy) in ((0, -3.55, 8.2, 0.15), (0, 3.55, 8.2, 0.15), (-4.05, 0, 0.15, 7.2), (4.05, 0, 0.15, 7.2)): box('Parapetto', (XR + cx, cy, 6.45), (dx, dy, 0.7), intonaco, envc)
for k in range(4):
    for z_ in (1.6, 4.4): box('Finestra', (XR - 2.7 + 1.8 * k, -3.52, z_), (1.0, 0.06, 1.2), m('vetro_casa', (0.25, 0.4, 0.55), rough=0.15, spec=0.9), envc)
tet = tex('roof_tiles', 2.0, m('tegole', (0.75, 0.25, 0.15), rough=0.7))
for (hx, hy, hw, hh) in ((-14, 4, 7, 4.5), (13, 6, 6, 5.0), (-11, -14, 6, 4.0), (16, -12, 7, 4.5), (0, 18, 8, 5.5), (-24, 14, 6, 4.0), (26, 10, 6, 4.0)):
    box('CasaVicina', (XR + hx, hy, hh / 2), (hw, hw * 0.85, hh), intonaco, envc)
    o = shape('TettoVicino', 'cone', (XR + hx, hy, hh + 1.1), (hw * 0.75, hw * 0.65, 2.6), (0, 0, PI / 4), None, tet, envc)
for k in range(10):
    a_ = k * 2 * PI / 10 + 0.3; A.albero_cartonato(('tree_02', 'tree_03', 'tree_04')[k % 3], posizione=(XR + 30 * math.cos(a_), 30 * math.sin(a_), 0), altezza=rnd.uniform(9, 13), collezione=envc) if False else None
P9.tappetino(prc, M, (XR - 1.2, 0.2, 6.12), 0.1, 'tappetino'); P9.tappetino(prc, M, (XR + 1.2, 0.1, 6.12), -0.1, 'tappetino2')
PR = (XR - 1.2, 0.2, 6.13); TR_ = (XR + 1.2, 0.1, 6.13)

# ======================= DISTRIBUTORE (x = 900) =======================
XD = 900.0
P9.deserto(envc, A, raggio=150.0, seme=8, centro=(XD, 0.0), piatto=35.0)
box('Asfalto', (XD, -4, 0.02), (16, 20, 0.04), tex('asphalt_02', 3.0, MS['asphalt']), envc)
D = P9.distributore(prc, M, 'D2')
D['root'].location = (XD, 0, 0)
CAR = props009.car(prc, props009.mats009()); CAR.rotation_mode = 'XYZ'
WHEELS = [c for c in CAR.children if c.name.startswith('MacchinaRuota')]
CARF = (XD, -0.9)                                                                                    # dove si ferma la macchina (tra le colonnine)
TXD = Vector((XD, 4.7, 0.0))

# ======================= personaggi =======================
CA = cp.cappellone(chc); CA['root'].rotation_mode = 'XYZ'
for nm in 'LR': CA['shoulder' + nm].rotation_mode = 'QUATERNION'
RO = rospina.rospina(chc, rospina.mats_rospina(), stile='D'); RO['root'].rotation_mode = 'XYZ'
for nm in 'LR': RO['shoulder' + nm].rotation_mode = 'QUATERNION'
RING = P9.collare(chc, M, RO['root'], raggio=0.125, z=1.47)
LEASH = P9.guinzaglio(chc, M, 'Guinzaglio', n=14)
TR = P9.trex(chc, M, 'T1'); TR['root'].rotation_mode = 'XYZ'
P = pippo.build_pippo(chc); P['root'].rotation_mode = 'XYZ'
for nm in 'LR': P['shoulder' + nm].rotation_mode = 'QUATERNION'
Tb = tumbo.build_tumbo(chc, scale=0.75); Tb['root'].rotation_mode = 'XYZ'
CASCO = P9.casco(prc, M)
STRAW = P9.cannuccia(prc, M, lunghezza=3.0)
def pt(nome, loc, par): return empty(nome, loc, par, chc)
CA_HL = pt('CA_ManoL', (0, 0, -0.62), CA['shoulderL']); CA_HR = pt('CA_ManoR', (0, 0, -0.62), CA['shoulderR'])
RO_HR = pt('RO_ManoR', (0, 0, -0.72), RO['shoulderR'])
TR_CLAW = pt('TR_Artiglio', (0, -0.42, -0.66), TR['armR']); TR_MOUTH = pt('TR_Bocca', (0, -2.35, -0.25), TR['head'])

# ======================= visibilita' =======================
def desc(o):
    for c in o.children:
        yield c
        yield from desc(c)
def show(o, intervals):
    for q in [o] + list(desc(o)):
        first = intervals[0][0] <= 0.0
        q.hide_render = not first; q.keyframe_insert('hide_render', frame=1)
        for (a, b) in intervals:
            if a > 0.0: q.hide_render = False; q.keyframe_insert('hide_render', frame=fr(a))
            if b < TOTAL: q.hide_render = True; q.keyframe_insert('hide_render', frame=fr(b))
show(CA['root'], [(0.0, T_ALLORA), (T_CONQ - 0.1, T_SUCCO + 0.75)])
for g_ in CA['cappelli'].values(): pass
show(RO['root'], [(T_ACCANTO - 0.1, T_ALLORA), (T_CONQ - 0.1, T_PIENO), (T_BENZ - 0.1, TOTAL)])
show(LEASH['obj'], [(T_ACCANTO - 0.1, T_ALLORA), (T_CONQ - 0.1, T_PIENO), (T_BENZ - 0.1, TOTAL)])
show(TR['root'], [(T_MA - 0.1, T_PIENO), (T_BENZ - 0.4, TOTAL)])
show(P['root'], [(T_ALLORA - 0.1, T_CONQ), (T_PIENO - 0.1, TOTAL)]); show(Tb['root'], [(T_ALLORA - 0.1, T_CONQ), (T_PIENO - 0.1, TOTAL)])
show(FLAGO, [(T_CONQ + 0.5, T_PIENO)]); show(GEYO, [(T_TREX + 0.4, T_BEVE)]); show(STRAW['root'], [(T_BEVE + 0.2, T_SUCCO + 0.75)])
show(CASCO, [(T_TEAM + 0.25, TOTAL)]); show(CAR, [(T_PIENO - 0.1, TOTAL)])
for (b_, *_r) in BUBBLES: show(b_, [(T_MA - 0.1, T_TREX)])

# ======================= pose e movimento =======================
def cp_state(t):
    """Cappellone: posizione, yaw, gesto (nome di cp.GESTI o tupla di direzioni), passo (fase o None), scala"""
    if t < T_ALLORA:
        if t < T_SPASSO - 0.1:
            g = 'saluto alla folla' if t < T_GUERRA else ('pugno sul tavolo' if t < T_IRAN + 0.6 else ('comizio' if t < T_MOTIVO else ('dito puntato' if t < T_ACCANTO else 'mani sul cuore')))
            return dict(loc=(CAPP[0], CAPP[1], 0.0), yaw=0.0 if t < T_ACCANTO else 0.35, g=g, walk=None, sc=1.0)
        u = ramp(t, T_SPASSO, T_ALLORA - 0.15); p = lerp(W0, W1, u)
        return dict(loc=(p[0], p[1], 0.0), yaw=-PI / 2, g=((-0.15, -0.4, -0.9), (0.6, -0.7, -0.1)), walk=t * 9.0, sc=1.0)
    if t < T_TREX:                                                                                   # al pozzo: pianta la bandiera
        g = 'saluto alla folla' if t < T_MA else 'non sono stato io'
        return dict(loc=(CAPD[0], CAPD[1], 0.0), yaw=-0.25, g=g, walk=None, sc=1.0)
    if t < T_BEVE:                                                                                   # scappa
        u = ramp(t, T_TREX + 0.2, T_BEVE); return dict(loc=(CAPD[0] - 3.0 * u, CAPD[1] - 2.0 * u, 0.0), yaw=PI * 0.75, g=((-0.5, 0.2, 0.8), (0.5, 0.2, 0.8)), walk=t * 14.0, sc=1.0)
    # in mano al T-rex: lo segue l'artiglio (calcolato al secondo giro), si svuota come un succo
    sq = ramp(t, T_BEVE + 0.5, T_SUCCO + 0.6)
    return dict(loc=None, yaw=0.0, g=((-0.6, -0.2, 0.7), (0.6, -0.2, 0.7)), walk=t * 20.0, sc=(1 - 0.75 * sq, 1 - 0.75 * sq, 1 - 0.15 * sq) if sq < 0.98 else (0.001,) * 3)

def ro_state(t):
    """Rospina: posizione, yaw, saltello"""
    if t < T_ALLORA:
        if t < T_SPASSO - 0.1: return dict(loc=(ROSP[0], ROSP[1], 0.0), yaw=-0.25, hop=0.0, armR=None)
        u = ramp(t, T_SPASSO, T_ALLORA - 0.15); p = lerp((W0[0] + 1.35, W0[1] - 0.2), (W1[0] + 1.35, W1[1] - 0.2), u)
        return dict(loc=(p[0], p[1], 0.18 * abs(math.sin(t * 9.0))), yaw=-PI / 2, hop=1.0, armR=None)
    if t < T_PIENO:
        if t < T_PORGE: return dict(loc=(ROSD[0], ROSD[1], 0.0), yaw=-0.3 if t < T_TREX else yaw_to(ROSD, (TX0.x, TX0.y)), hop=0.0, armR=None)
        return dict(loc=(ROSD[0] + 4.25 * ramp(t, T_PORGE, T_PORGE + 1.0), ROSD[1] + 2.65 * ramp(t, T_PORGE, T_PORGE + 1.0), 0.06 * abs(math.sin(t * 12)) * (1 - ramp(t, T_PORGE + 0.9, T_PORGE + 1.0))), yaw=yaw_to(ROSD, (TX0.x, TX0.y)), hop=0.0, armR=(0.15, -0.6, 0.8))
    return dict(loc=(XD + 2.6, 1.4, 0.0), yaw=-0.35, hop=0.0, armR=None)

def tr_state(t):
    """T-rex: root, yaw, scala, posa (dizionario per P9.trex_pose)"""
    if t < T_TREX - 0.05:                                                                            # addormentato nel petrolio
        z = -3.6; lid = 1.0 if t < T_VIVO + 0.15 else 1.0 - ramp(t, T_VIVO + 0.15, T_VIVO + 0.45)
        jaw = 0.1 + 0.9 * ramp(t, T_CAZZO - 0.15, T_CAZZO + 0.1)
        return dict(loc=(XU + 1.0, 3.0, z + 0.1 * math.sin(t * 1.5) + 1.2 * ramp(t, T_CAZZO - 0.2, T_CAZZO + 0.3)), yaw=0.35, sc=1.0,
                    pose=dict(jaw=jaw, testa=(0.1 - 0.3 * ramp(t, T_CAZZO - 0.15, T_CAZZO + 0.2), 0, 0), collo=0.3, lid=lid, brow=0.8 * ramp(t, T_VIVO + 0.3, T_VIVO + 0.6), coda=t * 0.8, look=(0, 0)))
    if t < T_PIENO:                                                                                  # esce dal deserto, beve, prende il guinzaglio
        z = -15.0 + 15.0 * ramp(t, T_TREX, T_TREX + 0.55) + 0.6 * math.sin(PI * ramp(t, T_TREX + 0.5, T_TREX + 0.8))
        if t < T_BEVE: pose = dict(jaw=0.95, testa=(-0.15, 0, 0), collo=-0.1, braccia=1.0, coda=t * 4, brow=0.9, look=(0, 0.3))
        elif t < T_PORGE: pose = dict(jaw=0.25 + 0.15 * math.sin(t * 18) * (1 if t > T_BEVE + 0.5 else 0), testa=(0.55, 0, 0), collo=0.45, braccia=0.15, coda=t * 2, brow=-0.2, look=(0, -0.7))
        else: pose = dict(jaw=0.55, testa=(0.6, 0, -0.35), collo=0.5, braccia=0.2, coda=t * 2, brow=-0.6, look=(-0.4, -0.8))
        return dict(loc=(TX0.x, TX0.y, z), yaw=TYAW, sc=TS, pose=pose)
    # benzinaio: spunta da dietro la pensilina, poi rutta il casco
    z = -6.0 + 6.0 * ramp(t, T_BENZ - 0.35, T_BENZ + 0.25)
    burp = math.sin(PI * ramp(t, T_TEAM + 0.1, T_TEAM + 0.6))
    pose = dict(jaw=0.35 + 0.6 * burp, testa=(0.25 - 0.3 * burp, 0, 0), collo=0.15, braccia=0.25, coda=t * 2, brow=-0.4 if t < T_800 else 0.5, look=(-0.5, -0.6))
    return dict(loc=(TXD.x, TXD.y, z), yaw=0.12, sc=1.0, pose=pose)

def pp_state(t):
    """Pippo: posizione, yaw, braccia, anche (rot x, rot y sinistra; rot x destra)"""
    if t < T_CONQ:
        if t < T_YOGA - 0.1: return dict(loc=PR, yaw=0.2, aL=None, aR=None, hL=(0, 0), hR=0.0)
        k = ramp(t, T_YOGA, T_YOGA + 0.5)                                                            # albero: braccia su, una gamba di lato
        return dict(loc=(PR[0], PR[1], PR[2] + 0.05 * math.sin(t * 2.0)), yaw=0.15, aL=lerp((-0.3, 0, -1), (-0.12, 0, 1), k), aR=lerp((0.3, 0, -1), (0.12, 0, 1), k), hL=(0.0, -0.85 * k), hR=0.0)
    if t < T_BENZ - 0.2:                                                                             # spinge la macchina
        u = ramp(t, T_PIENO, T_BENZ - 0.4); cy = -13.0 + (CARF[1] + 13.0) * u
        return dict(loc=(CARF[0] - 0.35, cy - 2.55, 0.0), yaw=PI, aL=(-0.12, -1.0, 0.1), aR=(0.12, -1.0, 0.1), hL=(0.45 * math.sin(t * 8), 0), hR=-0.45 * math.sin(t * 8))
    return dict(loc=(CARF[0] - 0.9, CARF[1] - 2.9, 0.0), yaw=0.15 if t < T_800 + 0.3 else yaw_to((CARF[0] - 0.9, CARF[1] - 2.9), (XD + 5.4, -1.2)) * (1 - ramp(t, T_PORCA, T_PORCA + 0.3)) + 0.1, aL=None, aR=None, hL=(0, 0), hR=0.0)

def tb_state(t):
    if t < T_CONQ:
        k = ramp(t, T_YOGA + 0.2, T_YOGA + 0.6)                                                      # il cane a testa in giu', davvero
        return dict(loc=(TR_[0], TR_[1], TR_[2] + 0.12 * k), yaw=-0.25, rot=(0.42 * k, 0, 0), front=-0.9 * k, back=0.35 * k)
    if t < T_BENZ - 0.2:
        u = ramp(t, T_PIENO, T_BENZ - 0.4); cy = -13.0 + (CARF[1] + 13.0) * u
        return dict(loc=(CARF[0] + 0.45, cy - 2.35, 0.0), yaw=PI, rot=(-0.15, 0, 0), front=-0.5 + 0.4 * math.sin(t * 10), back=0.3 * math.sin(t * 10))
    faint = ramp(t, T_PORCA + 0.05, T_PORCA + 0.35)
    return dict(loc=(CARF[0] + 0.3, CARF[1] - 3.2, 0.25 * faint), yaw=-0.2, rot=(0, PI / 2 * faint, 0), front=-1.3 * faint, back=1.2 * faint)

# emozioni
EMO_P = [(T_ALLORA - 0.1, 'furbo'), (T_YOGA, 'felice'), (T_PIENO, 'normale'), (T_BENZ + 0.3, 'sorpreso'), (T_800 + 0.2, 'spaventato'), (T_PORCA, 'arrabbiato'), (T_TEAM + 1.2, 'sorpreso')]
for i, (t_, n_) in enumerate(EMO_P):
    if i: pippo.emozione(P, fr(t_ - 0.08), EMO_P[i - 1][1])
    pippo.emozione(P, fr(t_), n_)
def emo_p(t):
    e = EMO_P[0][1]
    for (t_, n_) in EMO_P:
        if t_ <= t: e = n_
    return e
EMO_C = [(0.0, 'manifesto'), (T_GUERRA, 'comizio'), (T_IRAN + 0.6, 'furbo'), (T_MOTIVO, 'indignato'), (T_ACCANTO, 'promessa'), (T_SPASSO, 'manifesto'),
         (T_CONQ, 'comizio'), (T_MA, 'furbo'), (T_TREX, 'colto in fallo'), (T_BEVE, 'piagnisteo')]
for i, (t_, n_) in enumerate(EMO_C):
    if i: cp.emozione(CA, fr(t_ - 0.08), EMO_C[i - 1][1])
    cp.emozione(CA, fr(t_), n_)
cp.cappello(CA, 1, 'niente'); cp.cappello(CA, fr(T_CONQ - 0.15), 'niente'); cp.cappello(CA, fr(T_CONQ - 0.1), 'muratore')
EMO_R = [(0.0, 'importantissima'), (T_SPASSO, 'trionfo'), (T_CONQ, 'importantissima'), (T_TREX, 'scandalizzata'), (T_PORGE, 'falsa modestia'), (T_BENZ, 'importantissima'), (T_800, 'trionfo')]
for i, (t_, n_) in enumerate(EMO_R):
    if i: rospina.emozione(RO, fr(t_ - 0.08), EMO_R[i - 1][1])
    rospina.emozione(RO, fr(t_), n_)
for (t_, k) in ((T_ALLORA, dict(tongue=0.6)), (T_YOGA + 0.3, dict(eye_open=0.15, tongue=0.2)), (T_PIENO, dict(tongue=1.0, eye_scale=1.1)), (T_800 + 0.2, dict(brow=-1.0, eye_scale=1.3)), (T_PORCA + 0.1, dict(eye_open=0.05, tongue=1.0))):
    tumbo.tumbo_express(Tb, fr(t_), **k)

# chiavi fotogramma per fotogramma
for f in range(1, NF + 1):
    t = (f - 1) / FPS
    c = cp_state(t)
    if c['loc'] is not None: K(CA['root'], f, c['loc'], (0, 0, c['yaw']), c['sc'])
    else: K(CA['root'], f, rot=(0, 0, 0.1 * math.sin(t * 25)), scale=c['sc'])
    g = c['g']
    if isinstance(g, str): l_, r_, th, bd = cp.GESTI[g]
    else: l_, r_ = g; th, bd = (0, 0, 0), (0, 0)
    for nm, d in (('L', l_), ('R', r_)):
        sh = CA['shoulder' + nm]; dd = d
        if c['walk'] is not None and isinstance(g, tuple) and t < T_ALLORA and nm == 'R': dd = (d[0], d[1] + 0.15 * math.sin(c['walk']), d[2])
        sh.rotation_quaternion = qdir(dd); sh.keyframe_insert('rotation_quaternion', frame=f)
    K(CA['head'], f, rot=th); K(CA['body'], f, rot=(bd[0], bd[1], 0))
    sw = 0.45 * math.sin(c['walk']) if c['walk'] is not None else 0.0
    K(CA['hipL'], f, rot=(sw, 0, 0)); K(CA['hipR'], f, rot=(-sw, 0, 0))
    r = ro_state(t); K(RO['root'], f, r['loc'], (0, 0, r['yaw']))
    sw = 0.5 * math.sin(t * 9.0) if r['hop'] else 0.0
    K(RO['hipL'], f, rot=(sw, 0, 0)); K(RO['hipR'], f, rot=(-sw, 0, 0))
    for nm, d in (('L', (-0.18, 0.05, -1)), ('R', r['armR'] or (0.18, 0.05, -1))):
        sh = RO['shoulder' + nm]; sh.rotation_quaternion = qdir(d); sh.keyframe_insert('rotation_quaternion', frame=f)
    x = tr_state(t); K(TR['root'], f, x['loc'], (0, 0, x['yaw']), x['sc']); P9.trex_pose(TR, f, **x['pose'])
    p = pp_state(t); K(P['root'], f, p['loc'], (0, 0, p['yaw']))
    eb = pippo.EMOZIONI_FORTI[emo_p(t)]['braccia']
    for nm, k_, d in (('L', 'aL', eb[0]), ('R', 'aR', eb[1])):
        sh = P['shoulder' + nm]; sh.rotation_quaternion = qdir(p[k_] if p[k_] is not None else d); sh.keyframe_insert('rotation_quaternion', frame=f)
    K(P['hipL'], f, rot=(p['hL'][0], p['hL'][1], 0)); K(P['hipR'], f, rot=(p['hR'], 0, 0))
    b = tb_state(t); K(Tb['root'], f, b['loc'], (b['rot'][0], b['rot'][1], b['yaw']))
    K(Tb['tail'], f, rot=(-1.0 + 0.3 * math.sin(t * 9), 0, 0.7 * math.sin(t * 15)))
    for nm in 'LR': K(Tb['legF' + nm], f, rot=(b['front'], 0, 0)); K(Tb['legB' + nm], f, rot=(b['back'], 0, 0))
    # pozzi: il piu' grande comincia a pompare forte quando Cappellone trivella
    sp_ = 1.4 + 6.0 * ramp(t, T_TRIV, T_TRIV + 0.4); ph = t * sp_
    K(GP['beam'], f, rot=(0.22 * math.sin(ph), 0, 0)); K(GP['crank'], f, rot=(ph, 0, 0))
    K(GP['root'], f, loc=(0.06 * math.sin(t * 60) * ramp(t, T_TRIV, T_TRIV + 0.3), 10, 0))
    for (pq, ph0, spd) in PUMPS: K(pq['beam'], f, rot=(0.22 * math.sin(t * spd + ph0), 0, 0)); K(pq['crank'], f, rot=(t * spd + ph0, 0, 0))
    # cannoni: tutti girati a caso, poi si voltano insieme verso il pozzo piu' grande
    u = ramp(t, T_PUNTA, T_PUNTA + 0.5)
    for (cn, yaw0, el0) in CANNONS:
        y1 = yaw_to(tuple(cn['root'].location)[:2], (WELL.x, WELL.y)) + 0.0
        K(cn['root'], f, rot=(0, 0, yaw0 + (y1 - yaw0) * u)); K(cn['canna'], f, rot=(el0 + (-0.32 - el0) * u - 0.05 * math.sin(PI * ramp(t, T_PUNTA + 0.45, T_PUNTA + 0.7)), 0, 0))
    # bandiera piantata
    fz = 4.0 * (1 - ramp(t, T_CONQ + 0.5, T_CONQ + 0.85)); K(FLAGO, f, loc=(CAPD[0] + 2.0, CAPD[1] + 1.2, fz), rot=(0, 0, 0.2 + 0.05 * math.sin(t * 6)))
    # geyser di petrolio: dal pozzo alla bocca del T-rex
    # bolle nel lago sotterraneo
    for (bo, bx_, by_, ph0) in BUBBLES:
        q = ((t + ph0) % 2.0) / 2.0; K(bo, f, loc=(XU + bx_, by_, -0.2 + 0.5 * q), scale=(0.15 + 0.25 * math.sin(PI * q),) * 3)
    # macchina spinta, ruote che saltano via sul «porca puttana»
    if t >= T_PIENO - 0.1:
        u = ramp(t, T_PIENO, T_BENZ - 0.4); K(CAR, f, loc=(CARF[0], -13.0 + (CARF[1] + 13.0) * u, -0.1 * ramp(t, T_PORCA + 0.05, T_PORCA + 0.2)), rot=(0, 0, PI))
    for i, w in enumerate(WHEELS):
        if not hasattr(w, '_p0'): pass
    # sole e cielo: spenti nella grotta
    inside = 1.0 if T_MA - 0.05 <= t < T_TREX - 0.05 else 0.0
    SUN.data.energy = 3.6 * (1 - inside); SUN.data.keyframe_insert('energy', frame=f)
    SKY.inputs['Strength'].default_value = 0.45 * (1 - inside) + 0.02 * inside; SKY.inputs['Strength'].keyframe_insert('default_value', frame=f)
    for L_ in (LGR, LGR2): L_.data.energy = (900 if L_ is LGR else 500) * inside; L_.data.keyframe_insert('energy', frame=f)

# ruote: saltano via dal fotogramma del «porca puttana»
for i, w in enumerate(WHEELS):
    p0 = tuple(w.location); sx = 1 if p0[0] > 0 else -1
    for f in range(1, NF + 1):
        t = (f - 1) / FPS; d = max(0.0, t - T_PORCA - 0.05)
        w.location = (p0[0] + sx * 2.2 * min(d, 0.8) * (1 if d > 0 else 0), p0[1] + (0.6 if p0[1] > 0 else -0.6) * min(d, 0.8), p0[2] + max(-0.0, 3.0 * d - 6.0 * d * d)) if d > 0 else p0
        w.keyframe_insert('location', frame=f)

# casco ruttato: dalla bocca del T-rex alla testa di Pippo
pippo_testa = Vector((CARF[0] - 0.9, CARF[1] - 2.9, 2.28))

# ======================= effetti =======================
def fx(name, pos, w, t0, dur, **k): return A.effetto(name, posizione=pos, larghezza=w, animazione=(fr(t0), int(dur * FPS)), collezione=prc, **k)
for k, t_ in enumerate((0.3, 0.9, 1.4, 2.0, 2.5, 3.0, 3.7, 4.1)): fx('lampo/flash0%d' % (1 + k % 5), (XP - 2.5 + 0.8 * k, -4.5 - 0.3 * (k % 3), 1.5 + 0.4 * (k % 2)), 1.0, t_, 0.12, luce=3.0)
fx('emoticon/anger', (CAPP[0] + 0.5, CAPP[1], 2.55), 0.5, T_STORTO + 0.1, 1.0)
fx('emoticon/exclamations', (CAPP[0] - 0.5, CAPP[1], 2.6), 0.55, T_GUERRA + 0.1, 0.9)
fx('emoticon/hearts', (ROSP[0], ROSP[1], 2.35), 0.45, T_GUINZ + 0.3, 1.2)
fx('emoticon/idea', (PR[0], PR[1], PR[2] + 2.5), 0.45, T_ALLORA + 0.3, 1.2)
fx('emoticon/sleeps', (TR_[0] + 0.2, TR_[1], TR_[2] + 1.4), 0.45, T_YOGA + 0.6, 1.5)
fx('sbuffo_bianco/whitepuff03', (CAPD[0] + 2.0, CAPD[1] + 1.2, 0.3), 1.6, T_CONQ + 0.85, 0.5, colore=(0.95, 0.8, 0.55))
for k in range(5): fx('emoticon/sleep' if k % 2 else 'emoticon/sleeps', (XU + 0.5 + 0.5 * k, 0.0, 4.6 + 0.6 * k), 0.8, T_MA + 0.3 * k, 1.6)
fx('emoticon/exclamation', (XU - 1.0, -2.0, 7.0), 1.2, T_VIVO + 0.45, 0.8)
for k in range(4): fx('sbuffo_bianco/whitepuff%02d' % (2 * k), (TX0.x - 3 + 2 * k, TX0.y - 2.0, 1.0 + 0.6 * k), 9.0, T_TREX + 0.05 * k, 1.0, colore=(0.92, 0.75, 0.5), opacita=0.9)
for k in range(6): fx('schizzi/splat0%d' % (k % 5), (WELL.x - 2 + 0.8 * k, WELL.y - 1.0, 2 + 1.6 * k), 2.0, T_TREX + 0.5 + 0.1 * k, 0.6, colore=(0.03, 0.03, 0.035))
fx('emoticon/drops', (CAPD[0], CAPD[1], 2.6), 0.5, T_TREX + 0.2, 0.8)
fx('emoticon/drop', (TX0.x - 1.0, TX0.y - 5.0, 9.5), 1.2, T_SUCCO + 0.2, 0.7)
fx('emoticon/hearts', (ROSD[0] + 1.0, ROSD[1] + 0.6, 2.45), 0.5, T_PORGE + 0.3, 1.2)
fx('emoticon/cash', (XD + 5.4, -1.6, 5.8), 1.2, T_800 + 0.05, 1.3)
fx('emoticon/exclamations', (CARF[0] - 0.9, CARF[1] - 2.9, 2.75), 0.55, T_800 + 0.2, 0.9)
fx('emoticon/stars', (CARF[0] + 0.3, CARF[1] - 3.2, 0.9), 0.6, T_PORCA + 0.3, 1.2)
fx('sbuffo_bianco/whitepuff05', (CARF[0], CARF[1], 0.3), 2.5, T_PORCA + 0.05, 0.5, colore=(0.8, 0.75, 0.7))
fx('sbuffo_bianco/whitepuff01', (TXD.x - 0.2, TXD.y - 3.3, 6.3), 2.0, T_TEAM + 0.2, 0.6, colore=(0.75, 0.9, 0.6))
fx('emoticon/question', (CARF[0] - 0.9, CARF[1] - 2.9, 3.1), 0.5, T_TEAM + 1.3, 1.5)

# ======================= camera =======================
SHOTS = [  # t0, t1, camera da, a, mira da, a, lente, diaframma
    (0.0, T_GUERRA - 0.05, (XP - 0.6, -6.4, 1.9), (XP - 0.5, -5.6, 1.85), (XP, 0.4, 1.7), (XP, 0.4, 1.75), 32, 5),                 # 01 il comizio
    (T_GUERRA - 0.05, T_CHE - 0.05, (XP + 0.25, -2.6, 1.85), (XP + 0.2, -2.1, 1.85), (XP, CAPP[1], 1.8), (XP, CAPP[1], 1.85), 38, 3),  # 02 «dichiara guerra»
    (T_CHE - 0.05, T_MOTIVO - 0.05, (-12, -40, 24), (-8, -30, 16), (-4, 22, 0), (-4, 20, 2), 26, 16),                            # 03 il deserto pieno di pozzi
    (T_MOTIVO - 0.05, T_CANNONI - 0.05, (XP - 0.3, -2.9, 1.7), (XP - 0.25, -2.4, 1.75), (XP, CAPP[1], 1.75), (XP, CAPP[1], 1.8), 36, 3),   # 04 «ci hanno guardato storto»
    (T_CANNONI - 0.05, T_ACCANTO - 0.05, (-2.0, -19.0, 2.2), (2.0, -18.2, 2.4), (0.0, -11.0, 1.0), (3.0, 4.0, 4.0), 28, 10),     # 05 i cannoni si voltano verso il pozzo
    (T_ACCANTO - 0.05, T_SPASSO - 0.05, (XP + 0.2, -5.4, 1.7), (XP + 1.0, -4.6, 1.5), (XP + 0.4, 0.4, 1.5), (XP + 1.6, 0.2, 1.2), 30, 5),   # 06 Rospina al guinzaglio
    (T_SPASSO - 0.05, T_ALLORA - 0.05, (W0[0] + 0.7, -8.2, 1.4), (W1[0] + 0.7, -8.2, 1.4), (W0[0] + 0.65, -1.6, 1.15), (W1[0] + 0.65, -1.6, 1.15), 26, 6),  # 07 a spasso come un barboncino
    (T_ALLORA - 0.05, T_YOGA - 0.05, (PR[0] + 0.3, -3.4, PR[2] + 1.8), (PR[0] + 0.25, -2.9, PR[2] + 1.75), (PR[0], PR[1], PR[2] + 1.55), (PR[0], PR[1], PR[2] + 1.6), 34, 3),   # 08 Pippo sul tetto
    (T_YOGA - 0.05, T_CONQ - 0.05, (XR - 0.8, -6.8, 7.9), (XR - 0.3, -6.2, 7.8), (XR, 0.1, 6.95), (XR, 0.1, 6.95), 28, 6),         # 09 yoga
    (T_CONQ - 0.05, T_MA - 0.05, (-6.6, -5.2, 1.9), (-5.9, -4.5, 2.2), (-3.2, 3.0, 1.7), (-2.4, 3.5, 2.6), 26, 7),                 # 10 conquista e trivella
    (T_MA - 0.05, T_VIVO - 0.05, (XU - 1.2, -6.8, 4.4), (XU - 1.4, -5.0, 3.9), (XU + 1.7, 0.9, 2.6), (XU + 1.7, 0.9, 2.8), 26, 6),  # 11 il petrolio e' fatto di dinosauri
    (T_VIVO - 0.05, T_TREX - 0.05, (XU + 1.0, -2.4, 3.5), (XU + 1.15, -1.75, 3.45), (XU + 1.53, -0.27, 3.2), (XU + 1.53, -0.27, 3.25), 34, 3),   # 12 l'occhio si apre
    (T_TREX - 0.05, T_BEVE - 0.05, (-2.0, -10.0, 2.2), (-1.4, -9.0, 3.4), (9.5, 13.0, 5.5), (9.5, 13.0, 8.5), 22, 14),           # 13 il T-rex esce e beve il petrolio
    (T_BEVE - 0.05, T_PORGE - 0.05, (19.2, 0.4, 6.9), (18.5, 1.2, 7.1), (9.5, 11.4, 6.9), (9.5, 11.4, 7.1), 32, 8),               # 14 si beve Cappellone
    (T_PORGE - 0.05, T_PIENO - 0.05, (2.8, -6.2, 1.8), (3.0, -5.6, 2.0), (3.3, 9.5, 3.0), (3.5, 9.5, 3.6), 18, 9),   # 15 porge il guinzaglio
    (T_PIENO - 0.05, T_BENZ - 0.05, (XD - 7.0, -16.0, 2.2), (XD - 6.0, -14.0, 2.0), (XD, -8.0, 1.0), (XD, -2.0, 1.2), 28, 9),    # 16 spingono la macchina
    (T_BENZ - 0.05, T_800 - 0.05, (XD - 3.5, -13.0, 2.0), (XD - 3.2, -12.0, 2.1), (XD, 1.5, 4.0), (XD, 1.5, 4.4), 28, 10),       # 17 il benzinaio e' il T-rex
    (T_800 - 0.05, T_PORCA - 0.05, (XD + 2.6, -5.2, 3.4), (XD + 2.9, -4.6, 3.6), (XD + 5.4, -1.45, 3.7), (XD + 5.4, -1.45, 3.75), 36, 4),   # 18 800 euro al litro
    (T_PORCA - 0.05, T_TEAM - 0.05, (XD - 2.8, -8.0, 1.6), (XD - 2.6, -7.5, 1.6), (CARF[0] - 0.4, CARF[1] - 2.7, 1.1), (CARF[0] - 0.4, CARF[1] - 2.7, 1.1), 30, 5),   # 19 porca puttana
    (T_TEAM - 0.05, TOTAL + 0.1, (XD - 3.0, -11.5, 2.6), (XD - 2.6, -10.6, 2.5), (XD - 0.3, -2.0, 3.0), (CARF[0] - 0.9, CARF[1] - 2.9, 2.0), 28, 8),   # 20 il rutto: il casco sulla testa di Pippo
]
SCOSSE = [(T_GUERRA, 0.05), (T_PUNTA + 0.5, 0.06), (T_TRIV, 0.08), (T_CAZZO, 0.12), (T_TREX, 0.25), (T_PORCA, 0.1), (T_TEAM + 0.2, 0.06)]
PUGNI = [(T_IRAN, 0.3), (T_STORTO, 0.2), (T_GUINZ, 0.3), (T_DINO, 0.15), (T_CAZZO, 0.35), (T_SUCCO, 0.2), (T_BENZ + 0.6, 0.25), (T_800 + 0.3, 0.3), (T_PORCA, 0.2)]
for f in range(1, NF + 1):
    t = (f - 1) / FPS
    s_ = next((s for s in SHOTS if s[0] <= t < s[1]), SHOTS[-1]); u = (t - s_[0]) / (s_[1] - s_[0])
    cam.location = lerp(s_[2], s_[3], u); tgt.location = lerp(s_[4], s_[5], u); camd.lens = s_[6]; camd.dof.aperture_fstop = s_[7]
    for (e_, a_) in SCOSSE:
        d_ = t - e_
        if 0 <= d_ < 0.8: k_ = a_ * math.exp(-d_ * 6); cam.location = (cam.location.x + k_ * math.sin(d_ * 67), cam.location.y + k_ * math.sin(d_ * 53 + 1), cam.location.z + k_ * math.sin(d_ * 71 + 2))
    pg = [(e_, a_) for (e_, a_) in PUGNI if s_[0] <= e_ <= t < s_[1]]
    if pg: e_, a_ = pg[-1]; camd.lens = camd.lens * (1 + a_ * (1 - math.exp(-(t - e_) * 16)))
    cam.keyframe_insert('location', frame=f); tgt.keyframe_insert('location', frame=f); camd.keyframe_insert('lens', frame=f); camd.dof.keyframe_insert('aperture_fstop', frame=f)

def lin(idb):
    for fc in all_fcurves(idb):
        kind = 'CONSTANT' if 'hide' in fc.data_path else 'LINEAR'
        for kp in fc.keyframe_points: kp.interpolation = kind
for o in bpy.data.objects: lin(o)
for l_ in bpy.data.lights: lin(l_)
for cu in bpy.data.curves: lin(cu)
lin(scene.world.node_tree)
set_interp(camd, 'CONSTANT')
luci.ombre_pulite(scene, mezza_risoluzione=True)
scene.render.use_motion_blur = False
os.makedirs('../t029', exist_ok=True)
import json; json.dump([[round(s[0], 3), round(min(s[1], TOTAL), 3)] for s in SHOTS], open('../t029/shots.json', 'w'))
scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath('../t029/pippo_t029.blend')); print('SAVED', len(bpy.data.objects), 'oggetti')

# ======================= secondo giro (sul file riaperto: durante la costruzione le posizioni lette con frame_set restavano indietro) =======================
bpy.ops.wm.open_mainfile(filepath=os.path.abspath('../t029/pippo_t029.blend')); scene = bpy.context.scene
O = bpy.data.objects
CA_ROOT, CA_HEAD, CA_HL, RO_HR, TR_CLAW, TR_MOUTH, RING, CASCO = (O[n] for n in ('CAP_Root', 'CAP_Head', 'CA_ManoL', 'RO_ManoR', 'TR_Artiglio', 'TR_Bocca', 'GU_Anello', 'Casco'))
STRAWR = O['Cannuccia']; GEY = bpy.data.curves['Geyser']; _sp = GEY.splines[0]
LEASH = dict(obj=O['Guinzaglio'], curve=bpy.data.curves['Guinzaglio'], n=14)
def wpos(o): return o.matrix_world.translation.copy()
def K(o, f, loc=None, rot=None, scale=None):
    if loc is not None: o.location = loc; o.keyframe_insert('location', frame=f)
    if rot is not None: o.rotation_euler = rot; o.keyframe_insert('rotation_euler', frame=f)
    if scale is not None: o.scale = scale if isinstance(scale, (tuple, list)) else (scale,) * 3; o.keyframe_insert('scale', frame=f)
pippo_testa = Vector((CARF[0] - 0.9, CARF[1] - 2.9, 2.28))
claw_fix = {}
for f in range(1, NF + 1):
    t = (f - 1) / FPS
    if t >= T_BEVE:
        scene.frame_set(f); c_ = wpos(TR_MOUTH); claw_fix[f] = c_
FR_ = Vector((math.sin(TYAW), -math.cos(TYAW), 0.0))
for f, c_ in claw_fix.items(): K(CA_ROOT, f, loc=(c_.x + 2.4 * FR_.x, c_.y + 2.4 * FR_.y, c_.z - 2.5))           # davanti alla bocca, sotto la cannuccia
for f in range(1, NF + 1):
    t = (f - 1) / FPS
    leash_on = (T_ACCANTO - 0.1 <= t < T_ALLORA) or (T_CONQ - 0.1 <= t < T_PIENO) or (t >= T_BENZ - 0.1)
    need = leash_on or (T_TREX + 0.35 <= t < T_SUCCO + 0.8) or t >= T_TEAM + 0.2
    if not need: continue
    scene.frame_set(f)
    if leash_on:
        a = wpos(RING)
        if t < T_TREX: b = wpos(CA_HL)
        elif t < T_PORGE + 0.6: b = wpos(RO_HR) if t >= T_TREX + 0.3 else wpos(CA_HL)
        else: b = wpos(TR_CLAW)
        P9.guinzaglio_punti(LEASH, f, a, b, cala=0.35 if (b - a).length > 1.5 else 0.15)
    if T_BEVE + 0.15 <= t < T_SUCCO + 0.8:                                                            # cannuccia dalla bocca alla testa di Cappellone
        mo = wpos(TR_MOUTH); hd = wpos(CA_HEAD) + Vector((0, 0, 0.35)); d = mo - hd
        STRAWR.location = hd; STRAWR.rotation_mode = 'QUATERNION'; STRAWR.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d)
        STRAWR.scale = (1, 1, max(0.3, d.length / 3.2)); STRAWR.keyframe_insert('location', frame=f); STRAWR.keyframe_insert('rotation_quaternion', frame=f); STRAWR.keyframe_insert('scale', frame=f)
    if T_TREX + 0.35 <= t < T_BEVE:                                                                   # geyser
        mo = wpos(TR_MOUTH); p0, p1 = _sp.bezier_points
        p0.co = WELL; p0.handle_left = WELL - Vector((0, 0, 1)); p0.handle_right = WELL + Vector((0, 0, 9))
        p1.co = mo; p1.handle_left = mo + Vector((1.5, 0, 4)); p1.handle_right = mo - Vector((1.5, 0, 4))
        for q in (p0, p1):
            for at in ('co', 'handle_left', 'handle_right'): q.keyframe_insert(at, frame=f)
        GEY.bevel_factor_end = ramp(t, T_TREX + 0.35, T_TREX + 0.75); GEY.keyframe_insert('bevel_factor_end', frame=f)
    if t >= T_TEAM + 0.2:                                                                             # casco ruttato
        mo = wpos(TR_MOUTH); u = ramp(t, T_TEAM + 0.3, T_TEAM + 1.15)
        p = mo.lerp(pippo_testa, u); p.z += 3.0 * math.sin(PI * u) * (1 - u * 0.3)
        K(CASCO, f, loc=tuple(p), rot=(6.0 * u * (1 - u) * 3, 0, 9.0 * u), scale=0.45 + 0.55 * u)
for o in (CA_ROOT, STRAWR, CASCO, LEASH['obj']):
    for fc in all_fcurves(o):
        for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT' if 'hide' in fc.data_path else 'LINEAR'
for cu in (GEY, LEASH['curve']):
    for fc in all_fcurves(cu):
        for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'
scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath('../t029/pippo_t029.blend')); print('SAVED fase 2', flush=True)
