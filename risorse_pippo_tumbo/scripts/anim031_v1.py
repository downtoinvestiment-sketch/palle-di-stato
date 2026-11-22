"""Video 031 - IL NOBEL PER LA PACE (copione n. 33 v3). Salva ../t031/pippo_t031.blend
Scelte dell'autore (schede/scelta031.jpg): B2 bomba d'aereo, U1 ufficio elegante, F1 forno di mattoni.
Posti: ufficio di Cappellone (origine), campo delle bombe nel deserto (x = 300), quartiere con il giardino di Gualtiero e il cortile di Pippo (x = 600), mare (x = 900).
Voce: audio/voce_t031.mp3 (38,2 s), tempi in audio/words_t031.json. Personaggi inventati: Cappellone (biondo, bandiera «C» inventata) e Rospina;
i paesi nominati nella voce non compaiono mai: le bombe cadono su colline vuote (niente bandiere, leader, luoghi o vittime veri).
Uso: python anim031.py"""
import sys, math, os, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from mathutils import Vector
from common import *
from render_setup import *
import set004, props009, kitlook, tumbo, luci, rospina, cappellone as cp
import props029 as P9
import props031 as P
import pippo2 as pippo
from pippo import HEAD_C, HR
A = kitlook.A

FPS = 24; TOTAL = 38.8; NF = int(TOTAL * FPS)
def fr(t): return max(1, int(round(t * FPS)) + 1)
def sm(x): x = min(1.0, max(0.0, x)); return x * x * (3 - 2 * x)
def ramp(t, a, b): return sm((t - a) / (b - a))
def lin01(t, a, b): return min(1.0, max(0.0, (t - a) / (b - a)))
def lerp(a, b, u): return tuple(a[i] + (b[i] - a[i]) * u for i in range(len(a)))
def qdir(d, rest=(0, 0, -1)): return Vector(rest).rotation_difference(Vector(d).normalized())
PI = math.pi

# ======================= tempi (dalla voce) =======================
T_SOGNO, T_VOGLIO, T_NOBEL, T_DARLING, T_E, T_BOMB = 1.72, 2.56, 3.04, 4.06, 4.84, 6.02
T_NAZ = (6.60, 7.70, 8.36, 9.18, 10.04)                       # Venezuela, Iran, Yemen, Somalia, Iraq (solo nella voce)
T_EGU, T_GUAL, T_MA, T_MA2, T_CAZZO = 10.30, 10.84, 12.16, 13.14, 14.12
T_PEACE, T_PEACE2, T_BOOM = 14.86, 15.48, 16.08
T_IO, T_AMICA, T_ELUI, T_ATTACCA, T_CART, T_DATEMI, T_CALCIO = 16.84, 18.04, 18.70, 19.06, 19.96, 20.72, 21.18
T_ALLORA, T_LOGICA, T_TUMBO, T_PIZZA = 21.88, 23.18, 23.90, 25.18
T_BUONA, T_BOMBE, T_CAMB, T_ARIA, T_CADONO, T_CORI, T_PORCA = 25.74, 26.84, 27.08, 27.66, 28.64, 29.60, 30.28
T_NOBEL2, T_VINCE, T_TUMBO2, T_BOMBP, T_PIZZA2, T_MAP, T_TEAM, T_TEAM2 = 31.46, 33.06, 33.32, 33.98, 34.54, 35.30, 36.14, 37.10

reset_scene(); scene = bpy.context.scene
setup_render(scene, 1080, 1920, samples=4, fps=FPS, frames=NF); scene.frame_end = NF
A.qualita_eevee(preset='equilibrato', riflessi=False, scena=scene); scene.view_settings.exposure = -0.1
envc = collection('Env'); chc = collection('Characters'); prc = collection('Props'); cac = collection('Cameras')
world(scene, top=(0.12, 0.36, 0.95), bottom=(1.0, 0.80, 0.55), strength=1.0)
SKY = luci.cielo_basso(scene.world, 0.45)
M = P.mats031(); M9 = P9.mats029(); MS = set004.make_mats()
LUCK = bpy.data.fonts.load(A.font('luckiest'), check_existing=True)
SUN = luci.sole(prc, (-0.15, -1), lato=1, energia=3.6, angolo_alto=38)

camd = bpy.data.cameras.new('Cam'); cam = bpy.data.objects.new('Cam', camd); cac.objects.link(cam); scene.camera = cam
camd.clip_start = 0.05; camd.clip_end = 900; camd.sensor_width = 36
tgt = empty('CamTarget', (0, 0, 1), None, cac)
ct = cam.constraints.new('TRACK_TO'); ct.target = tgt; ct.track_axis = 'TRACK_NEGATIVE_Z'; ct.up_axis = 'UP_Y'
camd.dof.use_dof = True; camd.dof.focus_object = tgt

def m(n, col, **k): return material('T31_' + n, col, **k)
def box(nome, centro, dim, mat, coll=None, parent=None, rot=(0, 0, 0)): return P9.box(nome, centro, dim, mat, coll or prc, parent, rot)
def txt(nome, body, size, mat, loc, rot=(PI / 2, 0, 0), parent=None, ext=0.03, coll=None):
    return P9._txt(coll or prc, nome, body, size, mat, loc, rot, parent, ext, LUCK)
def K(o, f, loc=None, rot=None, scale=None):
    if loc is not None: o.location = loc; o.keyframe_insert('location', frame=f)
    if rot is not None: o.rotation_euler = rot; o.keyframe_insert('rotation_euler', frame=f)
    if scale is not None: o.scale = scale if isinstance(scale, (tuple, list)) else (scale,) * 3; o.keyframe_insert('scale', frame=f)
def tex(aid, dim, riserva, **k):
    try: return A.materiale(aid, dimensione=dim, **k)
    except Exception as e: print('texture mancante', aid, e); return riserva
rnd = random.Random(31)

# ======================= UFFICIO DI CAPPELLONE (origine) =======================
U = P.ufficio(envc, M, A, 'U1', (0.0, 0.0))
box('UF_Porta', (2.6, -3.97, 1.1), (1.1, 0.06, 2.2), M['legno'], envc); shape('UF_Maniglia', 'sphere', (2.2, -3.92, 1.05), (0.05, 0.05, 0.05), (0, 0, 0), None, M['oro'], envc)
box('UF_QuadroDav', (-1.6, -3.97, 2.2), (1.4, 0.05, 1.0), M['oro'], envc); box('UF_QuadroDavTela', (-1.6, -3.94, 2.2), (1.2, 0.03, 0.8), M['blu'], envc)
txt('UF_QuadroDavScritta', 'C', 0.55, M['oro'], (-1.6, -3.91, 2.0), rot=(PI / 2, 0, PI), ext=0.01, coll=envc)
for k in range(3): shape('UF_Pianta', 'sphere', (-4.3, -3.3 + 0.2 * k, 1.0 + 0.25 * k), (0.35, 0.35, 0.3), (0, 0, 0), None, m('pianta', (0.1, 0.45, 0.15), rough=0.6), envc)
box('UF_Vaso', (-4.3, -3.2, 0.35), (0.5, 0.5, 0.7), M['oro'], envc)
BTN = P.bottone(prc, M); BTN['root'].location = (0.42, 1.12, 0.885)
CAPO = (0.0, 1.62)                                                         # Cappellone dietro la scrivania
CAPF, ROSF = (0.5, -1.45), (-0.4, -1.6)                                    # davanti alla scrivania (il cartello)
ROSO = (-1.1, 1.8)                                                         # Rospina accanto a lui dietro la scrivania
LUF = luci.cinema(prc, (0.0, 1.4, 1.6), (0.9, -3.4, 1.8), distanza=4.0, lato=1, nome='CinemaUfficio')
lb = bpy.data.lights.new('LuceSchiena', 'AREA'); lb.size = 1.2; lb.energy = 0; lb.color = (1.0, 0.85, 0.65); lb.use_shadow = False
lf = bpy.data.lights.new('LuceDavanti', 'AREA'); lf.size = 2.0; lf.energy = 0; lf.color = (1.0, 0.88, 0.72); lf.use_shadow = True
LDAV = bpy.data.objects.new('LuceDavanti', lf); prc.objects.link(LDAV); LDAV.location = (1.4, -3.4, 2.7); luci.punta(LDAV, (0.0, -1.5, 1.4))
LSCH = bpy.data.objects.new('LuceSchiena', lb); prc.objects.link(LSCH); LSCH.location = (0.4, -0.2, 2.4); luci.punta(LSCH, (ROSF[0], ROSF[1], 1.15))

# ======================= CAMPO DELLE BOMBE (x = 300) =======================
XB = 300.0
P9.deserto(envc, A, raggio=170.0, seme=5, centro=(XB, 0.0), piatto=70.0)
BERS = [(XB - 30 + 15 * k, 42 + 8 * (k % 2), 0.0) for k in range(5)]   # colline vuote dove cadono le bombe
for k, b in enumerate(BERS): shape('Collina', 'sphere', (b[0], b[1] + 8, -6), (16, 12, 10), (0, 0, 0), None, tex('sand_01', 4.0, m('sabbia', (0.85, 0.7, 0.45), rough=0.95)), envc)

# ======================= QUARTIERE (x = 600) =======================
XN = 600.0
box('Prato', (XN, 0, -0.1), (160, 160, 0.2), MS['park'], envc)
intonaco = tex('painted_plaster_wall', 3.0, m('intonaco', (0.95, 0.8, 0.6), rough=0.9), tinta=(1.0, 0.86, 0.62))
tet = tex('roof_tiles', 2.0, m('tegole', (0.75, 0.25, 0.15), rough=0.7))
for (hx, hy, hw, hh, tn) in ((-12, 9, 7, 4.5, (0.85, 0.95, 0.8)), (5, 10, 8, 5.0, (1.0, 0.86, 0.62)), (-26, 14, 6, 4.0, (1.0, 0.8, 0.8)), (20, 14, 6, 4.5, (0.85, 0.9, 1.0)), (-4, 26, 8, 5.5, (1.0, 0.9, 0.7))):
    box('Casa', (XN + hx, hy, hh / 2), (hw, hw * 0.85, hh), intonaco, envc)
    shape('Tetto', 'cone', (XN + hx, hy, hh + 1.1), (hw * 0.75, hw * 0.65, 2.6), (0, 0, PI / 4), None, tet, envc)
    for k in range(2): box('Finestra', (XN + hx - 1.4 + 2.8 * k, hy - hw * 0.425 - 0.03, hh * 0.55), (1.0, 0.06, 1.1), m('vetro_casa', (0.25, 0.4, 0.55), rough=0.15, spec=0.9), envc)
legno_s = tex('weathered_planks', 1.0, m('steccato', (0.6, 0.45, 0.3), rough=0.8))
for k in range(14): box('Steccato', (XN - 5.5, -6 + 1.0 * k, 0.55), (0.1, 0.12, 1.1), legno_s, envc)
box('SteccatoTrave', (XN - 5.5, 0.5, 0.75), (0.08, 14, 0.12), legno_s, envc)
for k in range(8):
    a_ = rnd.uniform(0, 2 * PI); r_ = rnd.uniform(18, 34)
    tr_ = shape('Chioma', 'sphere', (XN + r_ * math.cos(a_), 6 + r_ * abs(math.sin(a_)), 4.5), (2.6, 2.6, 2.8), (0, 0, 0), None, m('chioma', (0.15, 0.45, 0.15), rough=0.8), envc)
    shape('Tronco', 'cyl:1:1', (tr_.location.x, tr_.location.y, 1.5), (0.3, 0.3, 3.0), (0, 0, 0), None, m('tronco', (0.35, 0.22, 0.12), rough=0.9), envc)
GUP = (XN - 12.0, 1.5)                                                      # Gualtiero nel suo giardino
F = P.forno(prc, M, A, 'F1'); F['root'].location = (XN + 4.6, 2.6, 0); F['root'].rotation_euler = (0, 0, 0.35)
box('Tavolo', (XN + 2.4, 0.9, 0.8), (1.5, 0.95, 0.06), tex('wood_table_worn', 1.0, M['legno']), prc)
for (sx, sy) in ((-1, -1), (1, -1), (1, 1), (-1, 1)): box('GambaTavolo', (XN + 2.4 + sx * 0.65, 0.9 + sy * 0.38, 0.39), (0.07, 0.07, 0.78), M['legno'], prc)
PIZ = P.pizza(prc, M, 'Pizza', raggio=0.36); PIZ.location = (XN + 2.25, 0.85, 0.84)
FORNOB = Vector((XN + 4.6, 2.6, 0)) + Vector((math.sin(0.35) * 0.82, -math.cos(0.35) * 0.82, 1.3))   # bocca del forno
PPP = (XN + 1.3, 0.2); TBP = (XN + 3.2, -0.35)                              # Pippo e Tumbo al forno
PODIO = (XN - 2.0, 1.2)
box('Podio', (PODIO[0], PODIO[1], 0.35), (1.3, 1.0, 0.7), M['legno'], prc); box('PodioTop', (PODIO[0], PODIO[1], 0.72), (1.4, 1.1, 0.05), M['oro'], prc)
txt('PodioUno', '1', 0.45, M['oro'], (PODIO[0], PODIO[1] - 0.52, 0.2), ext=0.02)
for s_ in (-1, 1): shape('PaloStriscione', 'cyl:1:1', (PODIO[0] + s_ * 1.9, PODIO[1] + 1.4, 1.5), (0.05, 0.05, 3.0), (0, 0, 0), None, M['grigio'], prc)
box('Striscione', (PODIO[0], PODIO[1] + 1.4, 2.6), (3.8, 0.04, 0.8), M['blu'], prc)
txt('StriscioneScritta', 'NOBEL PER LA PACE', 0.36, M['oro'], (PODIO[0], PODIO[1] + 1.37, 2.48), ext=0.01)
TBPOD = (PODIO[0], PODIO[1], 0.745)

# ======================= MARE (x = 900) =======================
XM = 900.0
P.mare(envc, (XM, 40.0), raggio=120.0)

# ======================= personaggi =======================
CA = cp.cappellone(chc); CA['root'].rotation_mode = 'XYZ'
for nm in 'LR': CA['shoulder' + nm].rotation_mode = 'QUATERNION'
RO = rospina.rospina(chc, rospina.mats_rospina(), stile='D'); RO['root'].rotation_mode = 'XYZ'
for nm in 'LR': RO['shoulder' + nm].rotation_mode = 'QUATERNION'
PP = pippo.build_pippo(chc); PP['root'].rotation_mode = 'XYZ'
for nm in 'LR': PP['shoulder' + nm].rotation_mode = 'QUATERNION'
Tb = tumbo.build_tumbo(chc, scale=0.75); Tb['root'].rotation_mode = 'XYZ'
M09 = props009.mats009(); GU = props009.gualtiero(chc, M09); GU['root'].rotation_mode = 'XYZ'
CARTELLO = P.cartello(chc, M, 'Cartello'); CARTELLO.parent = RO['root']; CARTELLO.location = (0, 0.25, 1.12); CARTELLO.rotation_euler = (0.08, 0, 0)
CUOCO = P.cappello_cuoco(chc, M, PP['head'], (0, 0, HEAD_C + HR[2] * 0.8), 2.2)
MED_C = P.medaglia(prc, M, 'MedagliaSogno', s=1.5); MED_C.parent = CA['head']
collare = bpy.data.objects['T_Tag'].parent
MED_T = P.medaglia(prc, M, 'MedagliaTumbo', s=0.85); MED_T.parent = collare

# bombe: 5 nel deserto, 1 per Gualtiero, 3 sul mare, 1 sulla pizza
BOMBE = {k: P.bomba(prc, M, 'B2', 'Bomba_' + k)['root'] for k in ('D0', 'D1', 'D2', 'D3', 'D4', 'G', 'M0', 'M1', 'M2', 'Z')}
COR_M = P.coriandoli(prc, 150, 'CorMare', 3); COR_P = P.coriandoli(prc, 70, 'CorPodio', 4); COR_Z = P.coriandoli(prc, 70, 'CorPizza', 5)

# ======================= visibilita' =======================
def desc(o):
    for c in o.children:
        yield c
        yield from desc(c)
def show(o, intervals, figli=True, pulisci=False):
    for q in [o] + (list(desc(o)) if figli else []):
        if pulisci: q.animation_data_clear()
        first = intervals[0][0] <= 0.0
        q.hide_render = not first; q.keyframe_insert('hide_render', frame=1)
        for (a, b) in intervals:
            if a > 0.0: q.hide_render = False; q.keyframe_insert('hide_render', frame=fr(a))
            if b < TOTAL: q.hide_render = True; q.keyframe_insert('hide_render', frame=fr(b))
UFF = [(0.0, T_NAZ[0] - 0.25), (T_PEACE - 0.05, T_ALLORA - 0.05), (T_BOMBP - 0.05, T_MAP - 0.05)]
show(CA['root'], UFF)
show(RO['root'], [(T_IO - 0.05, T_ALLORA - 0.05)])
show(CARTELLO, [(T_ATTACCA + 0.45, T_ALLORA - 0.05)], pulisci=True)
show(MED_C, [(T_SOGNO, T_E - 0.05)], pulisci=True)
show(GU['root'], [(T_EGU - 0.05, T_PEACE - 0.05)])
show(PP['root'], [(T_ALLORA - 0.05, T_BOMBE - 0.05), (T_NOBEL2 - 0.05, T_BOMBP - 0.05), (T_MAP - 0.05, TOTAL)])
show(Tb['root'], [(T_ALLORA - 0.05, T_BOMBE - 0.05), (T_NOBEL2 - 0.05, T_BOMBP - 0.05), (T_MAP - 0.05, TOTAL)])
show(CUOCO, [(T_TUMBO + 0.1, T_BOMBE - 0.05), (T_NOBEL2 - 0.05, T_BOMBP - 0.05), (T_MAP - 0.05, TOTAL)], pulisci=True)
show(MED_T, [(T_NOBEL2 + 0.3, T_BOMBP - 0.05), (T_MAP - 0.05, TOTAL)], pulisci=True)
show(PIZ, [(T_BUONA - 0.05, T_BOMBE - 0.05), (T_MAP - 0.05, TOTAL)])
for k in range(5): show(BOMBE['D%d' % k], [(T_NAZ[k] - 0.7, T_NAZ[k] + 0.02)])
show(BOMBE['G'], [(T_GUAL - 0.55, T_GUAL + 0.18)])
for k in range(3): show(BOMBE['M%d' % k], [(T_BOMBE - 0.05, T_CORI + 0.08 * k)])
show(BOMBE['Z'], [(T_MAP - 0.05, T_TEAM + 0.1)])

# ======================= pose e movimento =======================
def ca_state(t):
    """Cappellone: posizione, yaw, braccia (gesto o direzioni), testa e busto"""
    if t < T_NAZ[0]:
        if t < T_SOGNO: g = 'mani sul cuore'
        elif t < T_VOGLIO: g = 'mani sul cuore'
        elif t < T_E: g = 'comizio' if t < T_DARLING else 'promessa'
        elif t < T_BOMB - 0.15:                                                   # la mano sopra il bottone
            g = ((-0.12, 0, -1), lerp((0.12, 0, -1), (0.3, -0.75, 0.55), ramp(t, T_E, T_E + 0.5)))
        else: g = ((-0.12, 0, -1), lerp((0.3, -0.75, 0.55), (0.25, -0.8, -0.45), ramp(t, T_BOMB - 0.15, T_BOMB)))
        return dict(loc=(CAPO[0], CAPO[1], 0.0), yaw=0.0, g=g)
    if t < T_IO - 0.05:                                                            # «Peace! Peace! Boom!»
        if t < T_BOOM - 0.25: g = ('saluto alla folla' if (t < T_PEACE2) else 'comizio')
        elif t < T_BOOM: g = ((-0.12, 0, -1), lerp((0.3, -0.75, 0.55), (0.25, -0.8, -0.45), ramp(t, T_BOOM - 0.25, T_BOOM)))
        else: g = ((-0.12, 0, -1), (0.25, -0.8, -0.45))
        return dict(loc=(CAPO[0], CAPO[1], 0.0), yaw=0.0, g=g)
    if t < T_ELUI - 0.05:                                                          # Rospina accanto: lui sorride alla camera
        return dict(loc=(CAPO[0], CAPO[1], 0.0), yaw=-0.25, g='riposo')
    if t < T_ALLORA:                                                               # le attacca il cartello sulla schiena
        k = ramp(t, T_ATTACCA - 0.1, T_ATTACCA + 0.35) * (1 - ramp(t, T_CART + 0.1, T_CART + 0.5))
        gL = lerp((-0.12, 0, -1), (-0.95, 0.3, -0.2), k)
        return dict(loc=(CAPF[0], CAPF[1], 0.0), yaw=0.0, g=(gL, (0.55, -0.1, 1.0) if t > T_CART + 0.3 else (0.12, 0, -1)))
    # «Bomb the pizza!»: pugni sul bottone
    hit = abs(math.sin((t - T_BOMBP) * 9.0))
    return dict(loc=(CAPO[0], CAPO[1], 0.0), yaw=0.0, g=((-0.2, -0.5, -0.8), lerp((0.25, -0.8, -0.45), (0.3, -0.75, 0.55), hit)))

def ro_state(t):
    if t < T_ELUI - 0.05: return dict(loc=(ROSO[0], ROSO[1], 0.0), yaw=-0.2, armR=(0.55, -0.7, -0.15), armL=(-0.6, -0.2, -0.75))   # mano sul cuore
    return dict(loc=(ROSF[0], ROSF[1], 0.0), yaw=0.0, armR=(0.18, 0.05, -1), armL=(-0.18, 0.05, -1))

def pp_state(t):
    """Pippo: posizione, yaw, braccia (None = quelle dell'emozione)"""
    if t < T_BOMBE:
        if t < T_BUONA: return dict(loc=(PPP[0], PPP[1], 0.0), yaw=0.15, aL=None, aR=None)
        return dict(loc=(PPP[0] + 0.3, PPP[1] + 0.1, 0.0), yaw=-0.5, aL=(-0.45, -0.75, -0.3), aR=(0.45, -0.75, -0.3))   # presenta la pizza
    if t < T_BOMBP:                                                                # applaude Tumbo sul podio
        c = math.sin(t * 22.0) * 0.18
        return dict(loc=(PODIO[0] + 1.6, PODIO[1] - 0.6, 0.0), yaw=0.75, aL=(0.25 + c, -0.9, 0.2), aR=(-0.25 - c, -0.9, 0.2))
    return dict(loc=(PPP[0], PPP[1], 0.0), yaw=0.15, aL=None, aR=None)

def tb_state(t):
    if t < T_BOMBE:
        hop = 0.25 * abs(math.sin(t * 9)) if T_TUMBO + 0.4 < t < T_BUONA else 0.0
        return dict(loc=(TBP[0], TBP[1], hop), yaw=-0.3 if t < T_BUONA else -1.0, front=-0.4 * (hop > 0), back=0.3 * (hop > 0))
    if t < T_BOMBP:
        return dict(loc=TBPOD, yaw=0.0, front=-0.9 * ramp(t, T_TUMBO2 + 0.2, T_TUMBO2 + 0.5), back=0.0)      # sul podio, poi si alza sulle zampe
    if t < T_TEAM: return dict(loc=(TBP[0], TBP[1], 0.0), yaw=-0.6, front=0.0, back=0.0)
    u = ramp(t, T_TEAM + 0.1, T_TEAM + 0.6)                                        # salta sul tavolo e morde la pizza
    return dict(loc=lerp((TBP[0], TBP[1], 0.0), (XN + 2.85, 0.75, 0.84), u), yaw=-0.6 - 0.8 * u, front=0.0, back=0.0)

def gu_state(t):
    """Gualtiero: guarda in su, l'esplosione lo lancia e ricade a pancia in su, carbonizzato"""
    if t < T_GUAL + 0.15:
        return dict(loc=(GUP[0], GUP[1], 0.0), rot=(0, 0, 0.2), spread=0.25, arms=-2.84 * ramp(t, T_GUAL - 0.4, T_GUAL - 0.1), brow=-1.0, mouth=0.3 + 0.7 * ramp(t, T_GUAL - 0.3, T_GUAL))
    u = lin01(t, T_GUAL + 0.15, T_MA - 0.1)
    z = 9.0 * math.sin(PI * u) if u < 1 else 0.25
    return dict(loc=(GUP[0] + 1.5 * u, GUP[1] - 1.0 * u, z), rot=(-PI / 2 * u if u >= 1 else -4 * PI * u - (PI / 2) * u, 0, 0.2 + 2 * PI * u), arms=-2.84 if u < 1 else 0.0, spread=0.25 if u < 1 else 0.9, brow=-0.6 if u < 1 else 0.6, mouth=1.0 if u < 1 else 0.2)

# emozioni
def keys(lista, fn, R):
    for i, (t_, n_) in enumerate(lista):
        if i: fn(R, fr(t_ - 0.08), lista[i - 1][1])
        fn(R, fr(t_), n_)
EMO_C = [(0.0, 'manifesto'), (T_VOGLIO, 'comizio'), (T_DARLING, 'promessa'), (T_E, 'furbo'), (T_PEACE, 'manifesto'), (T_BOOM, 'furbo'), (T_IO, 'selfie'),
         (T_ELUI, 'furbo'), (T_BOMBP, 'indignato')]
keys(EMO_C, cp.emozione, CA)
cp.cappello(CA, 1, 'niente')
EMO_R = [(0.0, 'importantissima'), (T_AMICA, 'comizio'), (T_ELUI, 'falsa modestia'), (T_DATEMI, 'importantissima')]
keys(EMO_R, rospina.emozione, RO)
EMO_P = [(T_ALLORA - 0.1, 'furbo'), (T_TUMBO, 'felice'), (T_BUONA, 'ride'), (T_NOBEL2, 'felice'), (T_MAP, 'sorpreso'), (T_TEAM + 0.15, 'ride')]
keys(EMO_P, pippo.emozione, PP)
def emo_p(t):
    e = EMO_P[0][1]
    for (t_, n_) in EMO_P:
        if t_ <= t: e = n_
    return e
for (t_, k) in ((T_ALLORA, dict(tongue=0.4)), (T_TUMBO + 0.3, dict(tongue=1.0, eye_scale=1.15)), (T_NOBEL2, dict(tongue=0.2)), (T_TUMBO2, dict(tongue=1.0, eye_scale=1.2, brow=-0.4)),
                (T_MAP, dict(brow=-1.0, eye_scale=1.3)), (T_TEAM + 0.3, dict(tongue=1.0, eye_open=0.2))):
    tumbo.tumbo_express(Tb, fr(t_), **k)

# chiavi fotogramma per fotogramma
for f in range(1, NF + 1):
    t = (f - 1) / FPS
    c = ca_state(t); K(CA['root'], f, c['loc'], (0, 0, c['yaw']))
    g = c['g']
    if isinstance(g, str): l_, r_, th, bd = cp.GESTI[g]
    else: l_, r_ = g; th, bd = (0, 0, 0), (0, 0)
    for nm, d in (('L', l_), ('R', r_)):
        sh = CA['shoulder' + nm]; sh.rotation_quaternion = qdir(d); sh.keyframe_insert('rotation_quaternion', frame=f)
    K(CA['head'], f, rot=th); K(CA['body'], f, rot=(bd[0], bd[1], 0))
    r = ro_state(t); K(RO['root'], f, r['loc'], (0, 0, r['yaw']))
    for nm, d in (('L', r['armL']), ('R', r['armR'])):
        sh = RO['shoulder' + nm]; sh.rotation_quaternion = qdir(d); sh.keyframe_insert('rotation_quaternion', frame=f)
    p = pp_state(t); K(PP['root'], f, p['loc'], (0, 0, p['yaw']))
    eb = pippo.EMOZIONI_FORTI[emo_p(t)]['braccia']
    for nm, k_, d in (('L', 'aL', eb[0]), ('R', 'aR', eb[1])):
        sh = PP['shoulder' + nm]; sh.rotation_quaternion = qdir(p[k_] if p[k_] is not None else d); sh.keyframe_insert('rotation_quaternion', frame=f)
    b = tb_state(t); K(Tb['root'], f, b['loc'], (0, 0, b['yaw']))
    K(Tb['tail'], f, rot=(-1.0 + 0.3 * math.sin(t * 9), 0, 0.7 * math.sin(t * 15)))
    for nm in 'LR': K(Tb['legF' + nm], f, rot=(b['front'], 0, 0)); K(Tb['legB' + nm], f, rot=(b['back'], 0, 0))
    gq = gu_state(t); K(GU['root'], f, gq['loc'], gq['rot'])
    for nm, sx in (('L', -1), ('R', 1)): K(GU['shoulder' + nm], f, rot=(gq['arms'], 0, -sx * gq['spread']))
    # bottone: si schiaccia sotto la mano
    pr_ = 0.0
    for tp in (T_BOMB, T_BOOM): pr_ = max(pr_, 1.0 - lin01(abs(t - tp - 0.05), 0.0, 0.18))
    if t >= T_BOMBP: pr_ = max(pr_, max(0.0, -math.cos((t - T_BOMBP) * 18.0)))
    K(BTN['tasto'], f, scale=(1, 1, 1 - 0.6 * pr_))
    # medaglia del sogno sopra la testa di Cappellone
    K(MED_C, f, loc=(0, 0, 0.8 + 0.05 * math.sin(t * 4)), rot=(0, 0, t * 2.5), scale=1.0 - 0.999 * (1 - ramp(t, T_SOGNO, T_SOGNO + 0.35)))
    # medaglia di Tumbo: scende dal cielo sul collare
    u = ramp(t, T_NOBEL2 + 0.3, T_TUMBO2)
    K(MED_T, f, loc=(0, -0.05 - 0.07 * u, 4.0 * (1 - u) - 0.36 * u), rot=(0.85, 0, 6 * (1 - u)))
    # cartello: compare con un colpo
    K(CARTELLO, f, scale=1.25 * (0.001 + 0.999 * ramp(t, T_ATTACCA + 0.45, T_ATTACCA + 0.6)))
    # cappello da cuoco
    K(CUOCO, f, scale=0.001 + 0.999 * ramp(t, T_TUMBO + 0.1, T_TUMBO + 0.3))
    # pizza: esce dal forno e atterra sul tavolo; alla fine Tumbo se la mangia
    u = ramp(t, T_BUONA, T_BUONA + 0.5)
    pz = lerp(tuple(FORNOB), (XN + 2.25, 0.85, 0.84), u); pz = (pz[0], pz[1], pz[2] + 0.5 * math.sin(PI * u))
    K(PIZ, f, loc=pz, rot=(0, 0, 3 * u), scale=1.0 - 0.6 * ramp(t, T_TEAM + 0.7, T_TEAM2 + 0.5))
    # bombe nel deserto: cadono a turno sulle colline vuote
    for k in range(5):
        u = lin01(t, T_NAZ[k] - 0.7, T_NAZ[k]); b_ = BERS[k]
        K(BOMBE['D%d' % k], f, loc=(b_[0] - 6 * (1 - u), b_[1], 45 * (1 - u) + 1.0), rot=(PI / 2 - 0.35 * (1 - u), 0, PI / 2 * 0), scale=4.0)
    # bomba di Gualtiero
    u = lin01(t, T_GUAL - 0.55, T_GUAL + 0.15)
    K(BOMBE['G'], f, loc=(GUP[0] + 2.0 - 1.4 * u, GUP[1] + 1.0 - 0.6 * u, 22 * (1 - u) + 0.5), rot=(PI / 2 - 0.25, 0, 0), scale=1.4)
    # bombe sul mare: volano, frenano, cambiano idea (si girano), cadono e diventano coriandoli
    for k in range(3):
        bo = BOMBE['M%d' % k]; y0 = 14 + 3 * k; z0 = 12 + 2.5 * k
        if t < T_CAMB: x = XM - 26 + 18 * (t - T_BOMBE) / (T_CAMB - T_BOMBE) + 4 * k; yaw = PI / 2; pitch = 0.0; z = z0
        elif t < T_CADONO:
            br = lin01(t, T_CAMB, T_CAMB + 0.3); x = XM - 8 + 4 * k + 1.5 * br; z = z0 + 0.3 * math.sin(t * 6 + k)
            yaw = PI / 2 + PI * ramp(t, T_CAMB + 0.2 + 0.12 * k, T_ARIA + 0.12 * k); pitch = 0.0
        else:
            u = lin01(t, T_CADONO, T_CORI + 0.08 * k); x = XM - 6.5 + 4 * k; z = z0 - (z0 - 3.5) * u * u; yaw = 3 * PI / 2; pitch = 1.3 * ramp(t, T_CADONO, T_CADONO + 0.3)
        wob = 0.15 * math.sin(t * 20 + k) * (T_CAMB < t < T_ARIA + 0.3)
        bo.rotation_mode = 'ZXY'
        K(bo, f, loc=(x, y0, z), rot=(pitch + wob, 0, yaw), scale=2.2)
    # bomba sulla pizza: cade, si pianta accanto alla pizza, poi esplode in coriandoli
    u = lin01(t, T_MAP - 0.05, T_MAP + 0.45)
    K(BOMBE['Z'], f, loc=(XN + 2.75, 1.0, 0.84 + 0.62 + 18 * (1 - u) ** 2), rot=(PI / 2 - 0.12, 0, 0.3), scale=(0.75 + 0.15 * max(0.0, math.sin((t - T_MAP - 0.45) * 30)) * (t < T_TEAM)) if u >= 1 else 0.75)
    # sole e cielo spenti in ufficio; esposizione e luce calda di Cappellone
    office = any(a_ <= t < b_ for (a_, b_) in UFF)
    SUN.data.energy = 3.6 * (0 if office else 1); SUN.data.keyframe_insert('energy', frame=f)
    SKY.inputs['Strength'].default_value = 0.08 if office else 0.45; SKY.inputs['Strength'].keyframe_insert('default_value', frame=f)
    scene.view_settings.exposure = -0.35 if office else -0.1; scene.view_settings.keyframe_insert('exposure', frame=f)
    LSCH.data.energy = 60 if T_CART - 0.1 <= t < T_ALLORA else 0; LSCH.data.keyframe_insert('energy', frame=f)
    LDAV.data.energy = 220 if T_ELUI - 0.1 <= t < T_ALLORA else 0; LDAV.data.keyframe_insert('energy', frame=f)
# luce calda di Cappellone (approvata): chiave all'82% e piu' calda
LUF['chiave'].data.energy *= 0.82; LUF['chiave'].data.color = (1.0, 0.78, 0.55)

# Gualtiero carbonizzato: pelle e canottiera diventano nere dall'esplosione
for key, nero in (('gskin', (0.12, 0.1, 0.09, 1)), ('tank', (0.15, 0.15, 0.15, 1)), ('ghair', (0.05, 0.05, 0.05, 1))):
    mt = M09.get(key)
    if not mt: continue
    bc = mt.node_tree.nodes['Principled BSDF'].inputs['Base Color']; c0 = tuple(bc.default_value)
    bc.default_value = c0; bc.keyframe_insert('default_value', frame=fr(T_GUAL + 0.12)); bc.default_value = nero; bc.keyframe_insert('default_value', frame=fr(T_GUAL + 0.18))
for key in ('pupil', 'mouth'): pass
props009.gex(GU, fr(T_EGU), brow=-0.8, mouth=0.4, look=(0, 1)); props009.gex(GU, fr(T_GUAL), brow=-1.0, mouth=1.0, look=(0, 1)); props009.gex(GU, fr(T_MA - 0.1), brow=0.8, mouth=0.15, look=(0, 0))

# coriandoli: tre esplosioni colorate (le bombe sul mare, il podio di Tumbo, la bomba sulla pizza)
def coriandoli(lista, centri, t0, t1, raggio, caduta, seme):
    rr = random.Random(seme)
    par = [(centri[i % len(centri)], Vector((rr.uniform(-1, 1), rr.uniform(-1, 1), rr.uniform(-0.2, 1))).normalized() * rr.uniform(0.4, 1.0) * raggio, rr.uniform(0.6, 1.4)) for i in range(len(lista))]
    for f in range(1, NF + 1):
        t = (f - 1) / FPS
        on = t0 <= t < t1; was = t0 - 2 / FPS <= t < t1 + 2 / FPS
        if not was: continue
        for (o, a, b, c, d), (cc, v, sp) in zip(lista, par):
            if not on: K(o, f, loc=(0, 0, -50)); continue
            u = t - t0; e = 1 - math.exp(-u * 5)
            K(o, f, loc=(cc[0] + v.x * e + 0.3 * math.sin(u * 3 + a), cc[1] + v.y * e + 0.3 * math.cos(u * 2.5 + c), max(caduta[1], cc[2] + v.z * e - caduta[0] * u * sp)), rot=(a + u * 6 * b, c + u * 5, d + u * 4))
for (o, *_r) in COR_M + COR_P + COR_Z: K(o, 1, loc=(0, 0, -50))
for (o, *_r) in COR_M: o.scale = tuple(v * 4.0 for v in o.scale)
coriandoli(COR_M, [(XM - 6.5 + 4 * k, 14 + 3 * k, 3.5) for k in range(3)], T_CORI, T_NOBEL2, 6.0, (1.0, 0.05), 11)
coriandoli(COR_P, [(PODIO[0], PODIO[1] - 0.5, 4.5)], T_TUMBO2, T_BOMBP, 3.0, (0.9, 0.02), 12)
coriandoli(COR_Z, [(XN + 2.75, 1.0, 1.6)], T_TEAM, TOTAL + 0.1, 3.0, (0.8, 0.02), 13)

# ======================= effetti =======================
def fx(name, pos, w, t0, dur, **k): return A.effetto(name, posizione=pos, larghezza=w, animazione=(fr(t0), int(dur * FPS)), collezione=prc, **k)
fx('emoticon/hearts', (CAPO[0] - 0.5, CAPO[1], 2.45), 0.5, T_SOGNO + 0.2, 1.0)
fx('emoticon/idea', (CAPO[0] + 0.55, CAPO[1], 2.55), 0.5, T_E + 0.3, 0.9)
fx('lampo/flash02', (BTN['root'].location.x, 0.9, 1.2), 0.6, T_BOMB + 0.05, 0.15, luce=2.0)
for k in range(5):
    b_ = BERS[k]
    fx('esplosione/explosion0%d' % (k % 4), (b_[0], b_[1] - 2, 7), 18.0, T_NAZ[k], 0.75, luce=8.0)
    fx('fumo_nero/blacksmoke%02d' % (2 * k), (b_[0], b_[1] + 2, 12), 20.0, T_NAZ[k] + 0.3, 1.6, opacita=0.85)
fx('emoticon/alert', (GUP[0], GUP[1], 2.6), 0.6, T_EGU + 0.05, 0.6)
fx('esplosione/explosion05', (GUP[0] + 0.6, GUP[1] - 0.4, 1.8), 5.5, T_GUAL + 0.12, 0.6, luce=6.0)
fx('fumo_nero/blacksmoke12', (GUP[0] + 1.0, GUP[1], 2.5), 6.0, T_GUAL + 0.3, 1.6, opacita=0.9)
fx('emoticon/stars', (GUP[0] + 0.9, GUP[1] + 1.1, 1.25), 0.3, T_MA, 0.95)
fx('fumo_nero/blacksmoke03', (GUP[0] + 1.5, GUP[1] + 0.2, 0.9), 1.0, T_MA, 2.6, opacita=0.5)
fx('lampo/flash04', (BTN['root'].location.x, 0.9, 1.2), 0.6, T_BOOM + 0.05, 0.15, luce=2.0)
fx('emoticon/hearts', (ROSO[0], ROSO[1], 2.35), 0.5, T_AMICA, 0.8)
fx('emoticon/laugh', (CAPF[0] + 0.3, CAPF[1], 2.5), 0.5, T_CART + 0.3, 1.2)
fx('emoticon/idea', (PPP[0], PPP[1], 2.6), 0.55, T_ALLORA + 0.25, 1.4)
fx('sbuffo_bianco/whitepuff02', (PPP[0], PPP[1] - 0.2, 2.45), 0.9, T_TUMBO + 0.05, 0.4, colore=(1, 1, 1))
fx('emoticon/hearts', (XN + 2.25, 0.85, 1.4), 0.6, T_BUONA + 0.5, 1.2)
fx('sbuffo_bianco/whitepuff04', (XN + 2.25, 0.85, 1.5), 0.9, T_BUONA + 0.4, 1.0, colore=(1.0, 0.85, 0.55), opacita=0.6)
for k in range(3):
    fx('emoticon/question', (XM - 6.5 + 4 * k, 14 + 3 * k, 12 + 2.5 * k + 1.6), 1.4, T_CAMB + 0.25, 1.2)
    fx('emoticon/heart', (XM - 6.5 + 4 * k, 14 + 3 * k, 12 + 2.5 * k + 1.6), 1.4, T_ARIA + 0.2, 0.9)
    fx('lampo/flash0%d' % k, (XM - 6.5 + 4 * k, 14 + 3 * k, 3.5), 5.0, T_CORI + 0.08 * k, 0.2, luce=4.0)
fx('emoticon/stars', (TBPOD[0] + 0.55, TBPOD[1], 2.0), 0.4, T_TUMBO2 + 0.1, 1.5)
fx('emoticon/exclamations', (PPP[0], PPP[1], 2.65), 0.55, T_MAP + 0.45, 0.9)
fx('lampo/flash03', (XN + 2.75, 1.0, 1.6), 2.5, T_TEAM, 0.2, luce=3.0)
fx('emoticon/hearts', (XN + 2.85, 0.75, 1.6), 0.6, T_TEAM + 0.9, 1.6)

# ======================= camera =======================
BT = tuple(BTN['root'].location)
SHOTS = [  # t0, t1, camera da, a, mira da, a, lente, diaframma
    (0.0, T_SOGNO - 0.05, (1.8, -3.6, 2.4), (1.1, -2.2, 2.0), (0.0, 1.4, 1.55), (0.0, 1.5, 1.65), 26, 6),                       # 01 l'ufficio
    (T_SOGNO - 0.05, T_VOGLIO - 0.05, (0.5, -0.9, 2.1), (0.45, -0.5, 2.15), (0.0, CAPO[1], 2.35), (0.0, CAPO[1], 2.4), 30, 3),  # 02 sogna il Nobel
    (T_VOGLIO - 0.05, T_E - 0.05, (0.35, -0.3, 1.8), (0.3, 0.05, 1.8), (0.0, CAPO[1], 1.75), (0.0, CAPO[1], 1.78), 34, 2.4),    # 03 «Voglio il Nobel»
    (T_E - 0.05, T_BOMB - 0.2, (1.6, -1.6, 1.6), (1.4, -1.2, 1.55), (0.2, 1.3, 1.25), (0.3, 1.2, 1.15), 30, 3),                # 04 la mano sopra il bottone
    (T_BOMB - 0.2, T_NAZ[0] - 0.25, (BT[0] + 0.35, BT[1] - 0.75, BT[2] + 0.45), (BT[0] + 0.3, BT[1] - 0.6, BT[2] + 0.4), BT, BT, 38, 2),   # 05 bottone
    (T_NAZ[0] - 0.25, T_NAZ[2] - 0.05, (XB - 26, -12, 4), (XB - 16, -11, 4.5), (XB - 26, 44, 7), (XB - 10, 44, 8), 26, 22),   # 06 bombe sulle colline 1
    (T_NAZ[2] - 0.05, T_EGU - 0.05, (XB - 6, -11, 4.5), (XB + 10, -10, 5.0), (XB - 2, 44, 8), (XB + 28, 44, 8), 26, 22),       # 07 bombe sulle colline 2
    (T_EGU - 0.05, T_GUAL + 0.1, (GUP[0] - 0.6, GUP[1] - 4.6, 1.2), (GUP[0] - 0.5, GUP[1] - 4.0, 1.1), (GUP[0], GUP[1], 1.9), (GUP[0], GUP[1], 2.6), 26, 6),   # 08 Gualtiero guarda in su
    (T_GUAL + 0.1, T_MA - 0.05, (GUP[0] - 2.0, GUP[1] - 11.0, 3.0), (GUP[0] - 1.6, GUP[1] - 10.0, 4.5), (GUP[0], GUP[1], 2.5), (GUP[0] + 1.0, GUP[1], 5.0), 24, 12),   # 09 esplosione
    (T_MA - 0.05, T_MA2 - 0.05, (GUP[0] + 2.9, GUP[1] - 2.0, 2.9), (GUP[0] + 2.7, GUP[1] - 1.7, 2.6), (GUP[0] + 1.3, GUP[1] - 0.1, 0.4), (GUP[0] + 1.25, GUP[1] + 0.05, 0.4), 30, 4),   # 10 «Ma perche'?»
    (T_MA2 - 0.05, T_PEACE - 0.05, (GUP[0] + 1.9, GUP[1] - 0.3, 1.7), (GUP[0] + 1.85, GUP[1] - 0.2, 1.55), (GUP[0] + 1.14, GUP[1] + 0.76, 0.5), (GUP[0] + 1.14, GUP[1] + 0.76, 0.5), 30, 2.4),   # 11 «MA PERCHE', CAZZO?!»
    (T_PEACE - 0.05, T_IO - 0.05, (0.9, -1.9, 1.85), (0.6, -1.4, 1.8), (0.0, CAPO[1], 1.6), (0.1, CAPO[1], 1.5), 30, 3),           # 12 «Peace! Peace! Boom!»
    (T_IO - 0.05, T_ELUI - 0.05, (-0.2, -2.4, 1.75), (-0.35, -1.9, 1.75), (ROSO[0] + 0.4, ROSO[1], 1.6), (ROSO[0] + 0.2, ROSO[1], 1.65), 30, 3),   # 13 Rospina «la sua migliore amica»
    (T_ELUI - 0.05, T_CART - 0.05, (0.15, -3.8, 1.6), (0.1, -3.6, 1.6), (0.05, -1.5, 1.35), (0.05, -1.5, 1.4), 20, 4),               # 14 le attacca il cartello
    (T_CART - 0.05, T_ALLORA - 0.05, (-0.15, 0.55, 1.55), (-0.25, 0.1, 1.4), (ROSF[0], ROSF[1] + 0.25, 1.2), (ROSF[0], ROSF[1] + 0.25, 1.15), 32, 3),   # 15 «Datemi un calcio»
    (T_ALLORA - 0.05, T_TUMBO - 0.05, (XN + 0.0, -5.6, 2.0), (XN + 0.6, -5.0, 1.9), (XN + 2.4, 1.0, 1.2), (XN + 2.2, 0.8, 1.3), 28, 6),   # 16 Pippo fa la cosa piu' logica
    (T_TUMBO - 0.05, T_BUONA - 0.05, (XN + 1.6, -2.5, 1.9), (XN + 1.65, -2.1, 1.85), (PPP[0], PPP[1], 1.9), (PPP[0], PPP[1], 1.9), 34, 3),   # 17 «Tumbo, oggi facciamo la pizza!»
    (T_BUONA - 0.05, T_BOMBE - 0.05, (XN + 2.3, -2.0, 1.8), (XN + 2.2, -1.6, 1.6), (XN + 3.6, 1.8, 1.2), (XN + 2.4, 0.85, 0.95), 28, 3),     # 18 la pizza esce dal forno
    (T_BOMBE - 0.05, T_CADONO - 0.05, (XM - 11, -6, 9), (XM - 7, -4, 10), (XM - 9, 18, 13.5), (XM - 3, 18, 14.5), 28, 12),             # 19 le bombe cambiano idea
    (T_CADONO - 0.05, T_NOBEL2 - 0.05, (XM - 3, -6, 5), (XM - 2.5, -5, 4), (XM - 2, 18, 10), (XM - 2, 18, 3.5), 26, 12),               # 20 coriandoli nel mare
    (T_NOBEL2 - 0.05, T_VINCE - 0.05, (PODIO[0] - 0.5, PODIO[1] - 6.5, 2.4), (PODIO[0] - 0.2, PODIO[1] - 5.6, 2.2), (PODIO[0], PODIO[1], 1.6), (PODIO[0], PODIO[1], 1.4), 28, 6),   # 21 il Nobel per la pace...
    (T_VINCE - 0.05, T_BOMBP - 0.05, (PODIO[0] + 0.3, PODIO[1] - 2.6, 1.5), (PODIO[0] + 0.25, PODIO[1] - 2.2, 1.45), (TBPOD[0], TBPOD[1], 1.15), (TBPOD[0], TBPOD[1], 1.2), 32, 3),   # 22 ...lo vince Tumbo
    (T_BOMBP - 0.05, T_MAP - 0.05, (0.45, -0.9, 1.7), (0.4, -0.5, 1.7), (0.1, CAPO[1], 1.5), (0.1, CAPO[1], 1.55), 30, 2.4),        # 23 «Bomb the pizza!»
    (T_MAP - 0.05, T_TEAM - 0.05, (XN + 0.6, -3.4, 1.7), (XN + 0.8, -3.0, 1.7), (XN + 2.4, 0.9, 1.4), (XN + 2.5, 0.9, 1.2), 28, 4),   # 24 la bomba sulla pizza
    (T_TEAM - 0.05, TOTAL + 0.1, (XN + 0.9, -4.4, 2.0), (XN + 0.6, -5.6, 2.3), (XN + 2.3, 0.6, 1.3), (XN + 2.2, 0.5, 1.4), 28, 6),   # 25 coriandoli: Team Tumbo o team Cappellone?
]
SCOSSE = [(T_BOMB, 0.03), (T_NAZ[0], 0.25), (T_NAZ[1], 0.25), (T_NAZ[2], 0.25), (T_NAZ[3], 0.25), (T_NAZ[4], 0.3), (T_GUAL + 0.12, 0.3), (T_MA2, 0.06), (T_BOOM, 0.05), (T_CORI, 0.12), (T_TEAM, 0.08)]
PUGNI = [(T_NOBEL, 0.12), (T_GUAL, 0.25), (T_MA2, 0.35), (T_PEACE2, 0.1), (T_BOOM, 0.2), (T_AMICA, 0.15), (T_DATEMI, 0.25), (T_PIZZA, 0.2), (T_CAMB, 0.15), (T_TUMBO2, 0.3), (T_BOMBP, 0.25), (T_MAP + 0.45, 0.2)]
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
for mt in bpy.data.materials:
    if mt.node_tree: lin(mt.node_tree)
lin(scene.world.node_tree); lin(scene)
set_interp(camd, 'CONSTANT')
luci.ombre_pulite(scene, mezza_risoluzione=True)
scene.render.use_motion_blur = False
os.makedirs('../t031', exist_ok=True)
import json; json.dump([[round(s[0], 3), round(min(s[1], TOTAL), 3)] for s in SHOTS], open('../t031/shots.json', 'w'))
scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath('../t031/pippo_t031.blend')); print('SAVED', len(bpy.data.objects), 'oggetti', flush=True)
