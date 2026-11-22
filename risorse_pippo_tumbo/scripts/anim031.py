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

FPS = 24; TOTAL = 65.8; NF = int(TOTAL * FPS)
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
# Video 031 v2 - IL NOBEL PER LA PACE, 38,8 s. Si unisce alla testa: templates/head.py + scripts/anim031_body.py -> scripts/anim031.py
# Copione n. 33 v3 (COPIONI.md). Scelte dell'autore: B2 bomba d'aereo, U1 ufficio elegante, F1 forno di mattoni (schede/scelta031.jpg).
# v2 (21 novembre 2026, «fallo meglio, e' tutto buggato»): quartiere vero della testa (cortile di Pippo e giardino di Gualtiero con il look
# kitlook), Gualtiero solo sporco di fuliggine, bombe sul mare che cadono davvero (puntano dove vanno), ufficio con la camera che si muove,
# bocche che parlano con la voce (Cappellone, Rospina, Pippo), camera a mano come nel 028.
# Richiesta dell'autore (21 nov, 15:31): un mappamondo dove si vedono le bombe cadere sui paesi nominati (Natural Earth 1:50m, assets/mappe).
# Posti: cortile di Pippo e giardino di Gualtiero (quartiere della testa), ufficio di Cappellone (x = 600), mappamondo nello spazio (x = 1000),
# mare (x = 1400). Personaggi inventati: Cappellone (biondo, bandiera «C» inventata) e Rospina; i paesi nominati nella voce non compaiono.
# ===================================================================================================================
import random, json, subprocess, luci, rospina, cappellone as cp
import props029 as P9
import props031 as P
import pippo2 as pippo
from pippo import HEAD_C, HR
A = kitlook.A
BLEND = os.environ.get('BLEND031', '../t031/pippo_t031.blend')
rnd = random.Random(31)
def qdir(d, rest=(0, 0, -1)): return Vector(rest).rotation_difference(Vector(d).normalized())
def lin01(t, a, b): return min(1.0, max(0.0, (t - a) / (b - a)))
def tra(t, a, b): return a <= t < b
def tc(t): return (fr(t) - 1) / FPS - 0.001                                      # istante dello stacco (primo fotogramma dell'inquadratura)

# ======================= tempi (dalla voce) =======================
T_SOGNO, T_VOGLIO, T_NOBEL, T_DARLING, T_E, T_BOMB = 1.72, 2.56, 3.04, 4.06, 4.84, 6.02
T_NAZ = (6.60, 7.70, 8.36, 9.18, 10.04)                       # Venezuela, Iran, Yemen, Somalia, Iraq (solo nella voce)
T_EGU, T_GUAL, T_MA, T_MA2, T_CAZZO = 10.30, 10.84, 12.16, 13.14, 14.12
T_PEACE, T_PEACE2, T_BOOM = 14.86, 15.48, 16.08
T_IO, T_AMICA, T_ELUI, T_ATTACCA, T_CART, T_DATEMI, T_CALCIO = 16.84, 18.04, 18.70, 19.06, 19.96, 20.72, 21.18
T_ALLORA, T_LOGICA, T_TUMBO, T_PIZZA = 21.88, 23.18, 23.90, 25.18
T_BUONA, T_BOMBE, T_CAMB, T_ARIA, T_CADONO, T_CORI, T_PORCA = 25.74, 26.84, 27.08, 27.66, 28.64, 29.60, 30.28
T_NOBEL2, T_VINCE, T_TUMBO2, T_BOMBP, T_PIZZA2, T_MAP, T_TEAM, T_TEAM2 = 31.46, 33.06, 33.32, 33.98, 34.54, 35.30, 36.14, 37.10
TOTAL = 38.8; NF = int(TOTAL * FPS)
# battute dei personaggi (la bocca si muove con la voce)
BATT_C = [(T_VOGLIO - 0.05, T_E - 0.1), (T_PEACE - 0.05, T_IO - 0.15), (T_BOMBP - 0.05, T_MAP - 0.1)]
BATT_R = [(T_IO - 0.05, T_ELUI - 0.1)]
BATT_P = [(T_TUMBO - 0.05, T_BUONA - 0.1)]
# posti (FASI comandano sole, cielo ed esposizione)
FASI = [(0.0, 'UF'), (tc(T_NAZ[0] - 0.25), 'DS'), (tc(T_EGU), 'QU'), (tc(T_PEACE), 'UF'), (tc(T_ALLORA), 'QU'), (tc(T_BOMBE), 'MR'), (tc(T_NOBEL2), 'QU'), (tc(T_BOMBP), 'UF'), (tc(T_MAP), 'QU')]
def fase(t):
    c = FASI[0][1]
    for (t0, c_) in FASI:
        if t0 <= t: c = c_
    return c
def iv(*codes):
    out = []
    for i, (t0, c) in enumerate(FASI):
        t1 = FASI[i + 1][0] if i + 1 < len(FASI) else TOTAL + 1
        if c in codes:
            if out and abs(out[-1][1] - t0) < 1e-6: out[-1] = (out[-1][0], t1)
            else: out.append((t0, t1))
    return out

# ======================= voce: inviluppo per le bocche =======================
_raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', '../audio/voce_t031.mp3', '-f', 'f32le', '-ac', '1', '-ar', '8000', '-'], capture_output=True, check=True).stdout
VOX = np.frombuffer(_raw, dtype=np.float32)
_h = 8000 // FPS
VENV = np.array([np.sqrt(np.mean(VOX[i * _h:(i + 1) * _h] ** 2)) if i * _h < len(VOX) else 0.0 for i in range(NF + 2)])
VENV = np.clip(VENV / (np.percentile(VENV[VENV > 0], 92) + 1e-9), 0, 1)
def voce(t):
    i = int(t * FPS); return float(VENV[min(len(VENV) - 1, max(0, i))])
def parla(t, batt):
    return any(a <= t < b for a, b in batt)

# ======================= rendering e luce =======================
setup_render(scene, 1080, 1920, samples=4, fps=FPS, frames=NF); scene.frame_end = NF
scene.render.image_settings.color_mode = 'RGB'; scene.render.image_settings.compression = 90
camd = bpy.data.cameras.new('Cam'); cam = bpy.data.objects.new('Cam', camd); cac.objects.link(cam); scene.camera = cam
camd.clip_start = 0.02; camd.clip_end = 3000; camd.sensor_width = 36
tgt = empty('CamTarget', (0, 0, 1), None, cac)
ct = cam.constraints.new('TRACK_TO'); ct.target = tgt; ct.track_axis = 'TRACK_NEGATIVE_Z'; ct.up_axis = 'UP_Y'
camd.dof.use_dof = True; camd.dof.focus_object = tgt
kitlook.upgrade(scene, M, envc, prc, extras=False)
scene.eevee.taa_render_samples = 4
for o in list(bpy.data.objects):                                       # niente alberi-sagoma nel cortile di Pippo e nel giardino di Gualtiero
    if o.name.startswith('PT_sagoma') and -15.0 < o.location.x < 8.0 and -7.5 < o.location.y < 7.0: bpy.data.objects.remove(o)
CIELO = luci.cielo_basso(scene.world, 0.4)
scene.world.use_sun_shadow = False
SUN = luci.sole(prc, (0.25, -0.97), lato=1, energia=4.3)
luci.ombre_pulite(scene, mezza_risoluzione=True)
EXP0 = scene.view_settings.exposure
MP = P.mats031(); M9 = P9.mats029()
LUCK = bpy.data.fonts.load(A.font('luckiest'), check_existing=True)
def box(nome, centro, dim, mat, coll=None, parent=None, rot=(0, 0, 0)): return P9.box(nome, centro, dim, mat, coll or prc, parent, rot)
def txt(nome, body, size, mat, loc, rot=(PI / 2, 0, 0), parent=None, ext=0.03, coll=None):
    return P9._txt(coll or prc, nome, body, size, mat, loc, rot, parent, ext, LUCK)
def tex(aid, dim, riserva, **k):
    try: return A.materiale(aid, dimensione=dim, **k)
    except Exception as e: print('texture mancante', aid, e); return riserva
def K(o, f, loc=None, rot=None, scale=None):
    if loc is not None: o.location = loc; o.keyframe_insert('location', frame=f)
    if rot is not None: o.rotation_euler = rot; o.keyframe_insert('rotation_euler', frame=f)
    if scale is not None: o.scale = scale if isinstance(scale, (tuple, list)) else (scale,) * 3; o.keyframe_insert('scale', frame=f)
def KQ(o, f, d, rest=(0, -1, 0)):
    o.rotation_mode = 'QUATERNION'; o.rotation_quaternion = Vector(rest).rotation_difference(Vector(d).normalized()); o.keyframe_insert('rotation_quaternion', frame=f)
def Q(sh, f, d): sh.rotation_quaternion = qdir(d); sh.keyframe_insert('rotation_quaternion', frame=f)

# ======================= cortile di Pippo e giardino di Gualtiero (quartiere della testa) =======================
qc = collection('Cortile')
F_ = P.forno(qc, MP, A, 'F1'); F_['root'].location = (3.6, 4.5, 0); F_['root'].rotation_euler = (0, 0, 0.3)
FORNOB = Vector((3.6, 4.5, 0)) + Vector((math.sin(0.3) * 0.82, -math.cos(0.3) * 0.82, 1.3))     # bocca del forno
TAV = Vector((1.7, 2.6, 0.0))
m_tav = tex('wood_table_worn', 1.0, MP['legno'])
box('Tavolo', (TAV.x, TAV.y, 0.8), (1.5, 0.95, 0.06), m_tav, qc)
for (sx, sy) in ((-1, -1), (1, -1), (1, 1), (-1, 1)): box('GambaTavolo', (TAV.x + sx * 0.65, TAV.y + sy * 0.38, 0.39), (0.07, 0.07, 0.78), MP['legno'], qc)
box('Tovaglia', (TAV.x, TAV.y, 0.835), (1.2, 0.8, 0.01), material('T31_tovaglia', (0.85, 0.12, 0.12), rough=0.8), qc)
PIZ = P.pizza(qc, MP, 'Pizza', raggio=0.36); PIZON = (TAV.x - 0.2, TAV.y - 0.05, 0.845)
PPP = Vector((0.55, 1.75, 0.0)); TBP = Vector((2.9, 1.35, 0.0))              # Pippo e Tumbo al forno
PODIO = Vector((-3.6, 3.0, 0.0))
box('Podio', (PODIO.x, PODIO.y, 0.35), (1.3, 1.0, 0.7), MP['legno'], qc); box('PodioTop', (PODIO.x, PODIO.y, 0.72), (1.4, 1.1, 0.05), MP['oro'], qc)
txt('PodioUno', '1', 0.45, MP['oro'], (PODIO.x, PODIO.y - 0.52, 0.2), ext=0.02, coll=qc)
for s_ in (-1, 1): shape('PaloStriscione', 'cyl:1:1', (PODIO.x + s_ * 1.9, PODIO.y + 1.4, 1.5), (0.05, 0.05, 3.0), (0, 0, 0), None, MP['grigio'], qc)
box('Striscione', (PODIO.x, PODIO.y + 1.4, 2.6), (3.8, 0.04, 0.8), MP['blu'], qc)
txt('StriscioneScritta', 'NOBEL PER LA PACE', 0.36, MP['oro'], (PODIO.x, PODIO.y + 1.37, 2.48), ext=0.01, coll=qc)
TBPOD = Vector((PODIO.x, PODIO.y, 0.745))
PAPL = Vector((-1.7, 2.2, 0.0))                                             # Pippo che applaude
GUP = Vector((-12.6, 0.6, 0.0))                                             # Gualtiero nel suo giardino (casa a x = -17,5)
GULY = GUP + Vector((1.2, -0.9, 0.0))                                       # dove ricade
HEADG = GULY + Vector((-1.8 * math.sin(0.6), 1.8 * math.cos(0.6), 0.35))     # la sua testa quando e' a terra
TAVZ = Vector((TAV.x + 0.35, TAV.y + 0.1, 0.0))                              # dove si pianta la bomba finale

# ======================= ufficio di Cappellone (x = 600) =======================
XO = 600.0; ufc = collection('Ufficio')
U = P.ufficio(ufc, MP, A, 'U1', (XO, 0.0), bandiera='USA')                       # bandiera americana: richiesta dell'autore per la satira
box('UF_Porta', (XO + 2.6, -3.97, 1.1), (1.1, 0.06, 2.2), MP['legno'], ufc); shape('UF_Maniglia', 'sphere', (XO + 2.2, -3.92, 1.05), (0.05, 0.05, 0.05), (0, 0, 0), None, MP['oro'], ufc)
box('UF_QuadroDav', (XO - 1.6, -3.97, 2.2), (1.4, 0.05, 1.0), MP['oro'], ufc); box('UF_QuadroDavTela', (XO - 1.6, -3.94, 2.2), (1.2, 0.03, 0.8), MP['blu'], ufc)
txt('UF_QuadroDavScritta', 'C', 0.55, MP['oro'], (XO - 1.6, -3.91, 2.0), rot=(PI / 2, 0, PI), ext=0.01, coll=ufc)
for k in range(3): shape('UF_Pianta', 'sphere', (XO - 4.3, -3.3 + 0.2 * k, 1.0 + 0.25 * k), (0.35, 0.35, 0.3), (0, 0, 0), None, material('T31_pianta', (0.1, 0.45, 0.15), rough=0.6), ufc)
box('UF_Vaso', (XO - 4.3, -3.2, 0.35), (0.5, 0.5, 0.7), MP['oro'], ufc)
BTN = P.bottone(prc, MP); BTN['root'].location = (XO + 0.42, 1.12, 0.885); BT = Vector(BTN['root'].location)
CAPO = Vector((XO, 1.62, 0.0)); CAPF = Vector((XO + 0.5, -1.45, 0.0)); ROSF = Vector((XO - 0.4, -1.6, 0.0)); ROSO = Vector((XO - 1.1, 1.8, 0.0))
LUF = luci.cinema(prc, (XO, 1.4, 1.6), (XO + 0.9, -3.4, 1.8), distanza=4.0, lato=1, nome='CinemaUfficio')
LUF['chiave'].data.energy *= 0.82; LUF['chiave'].data.color = (1.0, 0.78, 0.55)      # luce calda di Cappellone (approvata)
lf = bpy.data.lights.new('LuceDavanti', 'AREA'); lf.size = 2.0; lf.energy = 0; lf.color = (1.0, 0.88, 0.72)
LDAV = bpy.data.objects.new('LuceDavanti', lf); prc.objects.link(LDAV); LDAV.location = (XO + 1.4, -3.4, 2.7); luci.punta(LDAV, (XO, -1.5, 1.4))
lb = bpy.data.lights.new('LuceSchiena', 'AREA'); lb.size = 1.2; lb.energy = 0; lb.color = (1.0, 0.85, 0.65); lb.use_shadow = False
LSCH = bpy.data.objects.new('LuceSchiena', lb); prc.objects.link(LSCH); LSCH.location = (XO + 0.4, -0.2, 2.4); luci.punta(LSCH, (ROSF.x, ROSF.y, 1.15))
UFL = [LUF[k] for k in LUF if hasattr(LUF[k], 'data') and getattr(LUF[k], 'type', '') == 'LIGHT']

# ======================= mappamondo nello spazio (x = 1000): le bombe cadono sui paesi nominati =======================
XG = Vector((1000.0, 0.0, 0.0)); RG = 5.0; glc = collection('Mappamondo')
P.mondo_texture('../assets/mappe/mondo_t031.png', evidenzia=list(P.PAESI))
GLOBO = P.mappamondo(glc, RG, '../assets/mappe/mondo_t031.png'); GLOBO.location = XG
STEL = P.cielo_stellato(glc, tuple(XG)); STEL.visible_shadow = False
for o in glc.objects:
    if o.name.startswith('Stella'): o.visible_shadow = False
NAZ = ('Venezuela', 'Iran', 'Yemen', 'Somalia', 'Iraq')
ROT_V = P.rot_davanti(-66.0, 8.0); ROT_M = P.rot_davanti(47.0, 21.0)
def rot_globo(t):
    u = ramp(t, T_NAZ[0] + 0.3, T_NAZ[1] - 0.2)
    r = lerp(ROT_V, ROT_M, u)
    return (r[0], 0.0, r[2])
def mondo_xyz(lon, lat, t, h=0.0):
    return XG + Euler(rot_globo(t), 'ZXY').to_matrix() @ P.punto(lon, lat, RG + h)
IMPATTI = [mondo_xyz(*P.PAESI[n], T_NAZ[k], 0.1) for k, n in enumerate(NAZ)]
ETI = []
for k, n in enumerate(NAZ):
    dx, dz = ((0.0, 0.6), (0.85, 0.55), (-0.95, 0.0), (0.85, -0.4), (-0.85, 0.55))[k]
    e = txt('Etichetta' + n, n.upper(), 0.36, MP['rosso'], tuple(IMPATTI[k] + Vector((dx, -1.0, dz))), ext=0.03, coll=glc); e.rotation_mode = 'XYZ'; ETI.append(e)
# ======================= mare (x = 1400) =======================
XM = 1400.0; mrc = collection('Mare')
P.mare(mrc, (XM, 40.0), raggio=120.0)

# ======================= personaggi =======================
CA = cp.cappellone(chc); CA['root'].rotation_mode = 'XYZ'
for nm in 'LR': CA['shoulder' + nm].rotation_mode = 'QUATERNION'
RO = rospina.rospina(chc, rospina.mats_rospina(), stile='D'); RO['root'].rotation_mode = 'XYZ'
for nm in 'LR': RO['shoulder' + nm].rotation_mode = 'QUATERNION'
PP = pippo.build_pippo(chc); PP['root'].rotation_mode = 'XYZ'; P_ = PP
for nm in 'LR': PP['shoulder' + nm].rotation_mode = 'QUATERNION'
Tb = tumbo.build_tumbo(chc, scale=0.75); Tb['root'].rotation_mode = 'XYZ'
GU = props009.gualtiero(chc, G9); GU['root'].rotation_mode = 'XYZ'
CARTELLO = P.cartello2(chc, MP, 'Cartello'); CARTELLO.parent = RO['root']; CARTELLO.location = (0, 0.3, 1.08); CARTELLO.rotation_euler = (0.1, 0.06, 0)
CUOCO = P.cappello_cuoco(chc, MP, PP['head'], (0, 0, HEAD_C + HR[2] * 0.8), 2.2)
MED_C = P.medaglia(prc, MP, 'MedagliaSogno', s=1.5); MED_C.parent = CA['head']
collare = bpy.data.objects['T_Tag'].parent
MED_T = P.medaglia(prc, MP, 'MedagliaTumbo', s=0.85); MED_T.parent = collare
# fuliggine su Gualtiero (macchie grigie, non tutto nero)
m_ful = material('T31_fuliggine', (0.16, 0.15, 0.14), rough=0.95)
FUL = []
for (p_, s_, par) in (((0.15, -0.27, 0.07), (0.08, 0.04, 0.06), GU['head']), ((-0.14, -0.27, -0.05), (0.07, 0.04, 0.05), GU['head']), ((0.03, -0.2, 0.25), (0.1, 0.05, 0.05), GU['head']),
                      ((0.12, -0.4, 1.08), (0.1, 0.03, 0.08), GU['root']), ((-0.14, -0.38, 0.9), (0.08, 0.03, 0.07), GU['root']), ((0.0, -0.41, 0.98), (0.06, 0.03, 0.05), GU['root'])):
    o = shape('Fuliggine', 'sphere', p_, s_, (0, 0, 0), par, m_ful, chc); FUL.append(o)
# bombe: 5 nel deserto, 1 per Gualtiero, 3 sul mare, 1 sulla pizza
BOMBE = {k: P.bomba(prc, MP, 'B2', 'Bomba_' + k)['root'] for k in ('D0', 'D1', 'D2', 'D3', 'D4', 'G', 'M0', 'M1', 'M2', 'Z')}
for k in range(5): BOMBE['D%d' % k].parent = GLOBO
COR_M = P.coriandoli(prc, 150, 'CorMare', 3); COR_P = P.coriandoli(prc, 70, 'CorPodio', 4); COR_Z = P.coriandoli(prc, 80, 'CorPizza', 5)
for (o, *_r) in COR_M: o.scale = tuple(v * 3.0 for v in o.scale)

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
UFF = iv('UF'); QUA = iv('QU')
show(CA['root'], UFF)
show(RO['root'], [(tc(T_IO), tc(T_ALLORA))])
show(CARTELLO, [(T_ATTACCA + 0.45, tc(T_ALLORA))], pulisci=True)
show(MED_C, [(T_SOGNO, tc(T_E))], pulisci=True)
show(GU['root'], [(tc(T_EGU), tc(T_PEACE))])
for o in FUL: show(o, [(T_GUAL + 0.15, tc(T_PEACE))], figli=False, pulisci=True)
PPV = [(tc(T_ALLORA), tc(T_BOMBE)), (tc(T_NOBEL2), tc(T_BOMBP)), (tc(T_MAP), TOTAL)]
show(PP['root'], PPV); show(Tb['root'], PPV)
show(CUOCO, [(T_TUMBO + 0.1, tc(T_BOMBE)), (tc(T_NOBEL2), tc(T_BOMBP)), (tc(T_MAP), TOTAL)], pulisci=True)
show(MED_T, [(T_NOBEL2 + 0.3, tc(T_BOMBP)), (tc(T_MAP), TOTAL)], pulisci=True)
show(PIZ, [(tc(T_BUONA), tc(T_BOMBE)), (tc(T_MAP), TOTAL)])
for k in range(5): show(BOMBE['D%d' % k], [(T_NAZ[k] - 0.75, T_NAZ[k] + 0.02)])
show(BOMBE['G'], [(T_GUAL - 0.55, T_GUAL + 0.16)])
for k in range(3): show(BOMBE['M%d' % k], [(tc(T_BOMBE), T_CORI + 0.07 * k)])
show(BOMBE['Z'], [(tc(T_MAP), T_TEAM + 0.02)])
for k, e in enumerate(ETI): show(e, [(T_NAZ[k], T_NAZ[0] + 0.3 if k == 0 else T_EGU)], figli=False)

# ======================= pose =======================
PRESS0, PRESS1 = (0.3, -0.75, 0.55), (0.25, -0.8, -0.45)                    # braccio destro sopra il bottone / sul bottone
def ca_state(t):
    """Cappellone: posizione, yaw, braccia (gesto o direzioni)"""
    if t < T_NAZ[0]:
        if t < T_VOGLIO: g = 'riposo' if t < T_SOGNO else 'mani sul cuore'
        elif t < T_E: g = 'comizio' if t < T_DARLING else 'promessa'
        elif t < T_BOMB - 0.15: g = ((-0.12, 0, -1), lerp((0.12, 0, -1), PRESS0, ramp(t, T_E, T_E + 0.5)))
        else: g = ((-0.12, 0, -1), lerp(PRESS0, PRESS1, ramp(t, T_BOMB - 0.15, T_BOMB)))
        return dict(loc=(CAPO.x, CAPO.y, 0.0), yaw=0.0, g=g)
    if t < tc(T_IO):                                                            # «Peace! Peace! Boom!»
        if t < T_BOOM - 0.25: g = ('saluto alla folla' if t < T_PEACE2 else 'comizio')
        else: g = ((-0.12, 0, -1), lerp(PRESS0, PRESS1, ramp(t, T_BOOM - 0.25, T_BOOM)))
        return dict(loc=(CAPO.x, CAPO.y, 0.0), yaw=0.0, g=g)
    if t < tc(T_ELUI): return dict(loc=(CAPO.x, CAPO.y, 0.0), yaw=-0.25, g='riposo')
    if t < T_ALLORA:                                                               # le attacca il cartello sulla schiena
        k = ramp(t, T_ATTACCA - 0.1, T_ATTACCA + 0.35) * (1 - ramp(t, T_CART + 0.1, T_CART + 0.5))
        gL = lerp((-0.12, 0, -1), (-0.95, 0.3, -0.2), k)
        return dict(loc=(CAPF.x, CAPF.y, 0.0), yaw=0.0, g=(gL, (0.55, -0.1, 1.0) if t > T_CART + 0.3 else (0.12, 0, -1)))
    hit = abs(math.sin((t - T_BOMBP) * 9.0))                                       # «Bomb the pizza!»: pugni sul bottone
    return dict(loc=(CAPO.x, CAPO.y, 0.0), yaw=0.0, g=((-0.2, -0.5, -0.8), lerp(PRESS1, PRESS0, hit)))
def ro_state(t):
    if t < tc(T_ELUI): return dict(loc=(ROSO.x, ROSO.y, 0.0), yaw=-0.2, armR=(0.55, -0.7, -0.15), armL=(-0.6, -0.2, -0.75))
    return dict(loc=(ROSF.x, ROSF.y, 0.0), yaw=0.0, armR=(0.18, 0.05, -1), armL=(-0.18, 0.05, -1))
def pp_state(t):
    if t < T_BOMBE:
        if t < T_BUONA: return dict(loc=tuple(PPP), yaw=0.2, aL=None, aR=None)
        return dict(loc=tuple(PPP + Vector((0.3, 0.1, 0))), yaw=-0.5, aL=(-0.45, -0.75, -0.3), aR=(0.45, -0.75, -0.3))
    if t < T_BOMBP:
        c = math.sin(t * 22.0) * 0.18
        return dict(loc=tuple(PAPL), yaw=0.95, aL=(0.25 + c, -0.9, 0.2), aR=(-0.25 - c, -0.9, 0.2))
    return dict(loc=tuple(PPP), yaw=0.2, aL=None, aR=None)
def tb_state(t):
    if t < T_BOMBE:
        hop = 0.25 * abs(math.sin(t * 9)) if T_TUMBO + 0.4 < t < T_BUONA else 0.0
        return dict(loc=(TBP.x, TBP.y, hop), yaw=-0.3 if t < T_BUONA else -1.0, front=-0.4 * (hop > 0), back=0.3 * (hop > 0))
    if t < T_BOMBP: return dict(loc=tuple(TBPOD), yaw=0.0, front=-0.9 * ramp(t, T_TUMBO2 + 0.2, T_TUMBO2 + 0.5), back=0.0)
    if t < T_TEAM: return dict(loc=(TBP.x, TBP.y, 0.0), yaw=-0.6, front=0.0, back=0.0)
    u = ramp(t, T_TEAM + 0.1, T_TEAM + 0.6)
    return dict(loc=lerp((TBP.x, TBP.y, 0.0), (TAV.x + 0.15, TAV.y - 0.15, 0.84), u), yaw=-0.6 - 0.8 * u, front=0.0, back=0.0)
def gu_state(t):
    if t < T_GUAL + 0.15:
        return dict(loc=tuple(GUP), rot=(0, 0, 0.6), arms=-2.84 * ramp(t, T_GUAL - 0.4, T_GUAL - 0.1), spread=0.25)
    u = lin01(t, T_GUAL + 0.15, T_MA - 0.1)
    p = GUP.lerp(GULY, u); z = 7.0 * math.sin(PI * u) if u < 1 else 0.25
    rx = -4 * PI * u - (PI / 2) * u if u < 1 else -PI / 2
    return dict(loc=(p.x, p.y, z), rot=(rx, 0, 0.6 + 2 * PI * u if u < 1 else 0.6), arms=-2.84 if u < 1 else 0.0, spread=0.25 if u < 1 else 0.9)

# ======================= emozioni (con le bocche che parlano) =======================
EMO_C = [(0.0, 'manifesto'), (T_VOGLIO, 'comizio'), (T_DARLING, 'promessa'), (T_E, 'furbo'), (T_PEACE, 'manifesto'), (T_BOOM, 'furbo'), (T_IO, 'selfie'), (T_ELUI, 'furbo'), (T_BOMBP, 'indignato')]
EMO_R = [(0.0, 'importantissima'), (T_AMICA, 'trionfo'), (T_ELUI, 'falsa modestia'), (T_DATEMI, 'importantissima')]
EMO_P = [(0.0, 'furbo'), (T_TUMBO, 'felice'), (T_BUONA, 'ride'), (T_NOBEL2, 'felice'), (T_MAP, 'sorpreso'), (T_TEAM + 0.15, 'ride')]
def quale(lista, t):
    e = lista[0][1]
    for (t_, n_) in lista:
        if t_ <= t: e = n_
    return e
def _emo_key(f, nome, forza, extra=None):
    e = pippo.EMOZIONI_FORTI[nome]
    fa = {k: (tuple(x * forza for x in v) if isinstance(v, tuple) else v * forza) for k, v in e['faccia'].items()}
    if extra: fa.update(extra)
    pippo.express(PP, f, **fa)
    if 'sopracciglia' in e:
        for (s_, nm), b in zip(((-1, 'L'), (1, 'R')), e['sopracciglia']):
            br = PP['brow' + nm]; br.rotation_euler = (0, s_ * b * 0.45 * forza, 0); br.keyframe_insert('rotation_euler', frame=f)
    seg = pippo._segni(PP); ex_ = list(e.get('extra', ()))
    for k, g in seg.items():
        g.scale = (1, 1, 1) if (k in ex_ and forza > 0.3) else (0.001,) * 3; g.keyframe_insert('scale', frame=f)
for f in range(1, NF + 1, 2):
    t = (f - 1) / FPS
    # Cappellone
    if any(a - 0.2 <= t < b + 0.2 for a, b in UFF):
        e = dict(cp.EMOZIONI[quale(EMO_C, t)])
        if parla(t, BATT_C): e['mouth_open'] = 0.1 + 0.85 * voce(t)
        cp.faccia(CA, f, **e)
    # Rospina
    if T_IO - 0.3 <= t < T_ALLORA + 0.1:
        e = dict(rospina.EMOZIONI[quale(EMO_R, t)])
        if parla(t, BATT_R): e['mouth'] = 0.1 + 0.9 * voce(t)
        rospina.rex(RO, f, **e)
    # Pippo
    if any(a - 0.2 <= t < b + 0.2 for a, b in PPV):
        nome = quale(EMO_P, t); ex = None
        if parla(t, BATT_P): nome = 'felice'; ex = dict(mouth_open=0.1 + 0.8 * voce(t), smile=0.5)
        _emo_key(f, nome, 1.0 if not parla(t, BATT_P) else 0.7, ex)
for (t_, k) in ((T_ALLORA, dict(tongue=0.4)), (T_TUMBO + 0.3, dict(tongue=1.0, eye_scale=1.15)), (T_NOBEL2, dict(tongue=0.2)), (T_TUMBO2, dict(tongue=1.0, eye_scale=1.2, brow=-0.4)),
                (T_MAP, dict(brow=-1.0, eye_scale=1.3)), (T_TEAM + 0.3, dict(tongue=1.0, eye_open=0.2))):
    tumbo.tumbo_express(Tb, fr(t_), **k)
props009.gex(GU, fr(T_EGU), brow=-0.8, mouth=0.4, look=(0, 1)); props009.gex(GU, fr(T_GUAL), brow=-1.0, mouth=1.0, look=(0, 1)); props009.gex(GU, fr(T_MA - 0.1), brow=0.8, mouth=0.15, look=(0, 0))
props009.gex(GU, fr(T_MA2), brow=1.2, mouth=0.6, look=(0.6, 0))

# ======================= chiavi fotogramma per fotogramma =======================
for f in range(1, NF + 1):
    t = (f - 1) / FPS
    c = ca_state(t); K(CA['root'], f, c['loc'], (0, 0, c['yaw']))
    g = c['g']
    if isinstance(g, str): l_, r_, th, bd = cp.GESTI[g]
    else: l_, r_ = g; th, bd = (0, 0, 0), (0, 0)
    talk = parla(t, BATT_C)
    th = (th[0] + (0.06 * math.sin(t * 13) * voce(t) if talk else 0.0), th[1], th[2] + (0.05 * math.sin(t * 7) if talk else 0.0))
    Q(CA['shoulderL'], f, l_); Q(CA['shoulderR'], f, r_)
    K(CA['head'], f, rot=th); K(CA['body'], f, rot=(bd[0], bd[1], 0))
    r = ro_state(t); K(RO['root'], f, r['loc'], (0, 0, r['yaw'])); Q(RO['shoulderL'], f, r['armL']); Q(RO['shoulderR'], f, r['armR'])
    p = pp_state(t); K(PP['root'], f, p['loc'], (0, 0, p['yaw']))
    eb = pippo.EMOZIONI_FORTI[quale(EMO_P, t)]['braccia']
    if parla(t, BATT_P): eb = ((-0.5, -0.4, 0.75), (0.5, -0.4, 0.75))                 # «Tumbo, oggi facciamo la pizza!» a braccia alzate
    Q(PP['shoulderL'], f, p['aL'] if p['aL'] is not None else eb[0]); Q(PP['shoulderR'], f, p['aR'] if p['aR'] is not None else eb[1])
    b = tb_state(t); K(Tb['root'], f, b['loc'], (0, 0, b['yaw']))
    K(Tb['tail'], f, rot=(-1.0 + 0.3 * math.sin(t * 9), 0, 0.7 * math.sin(t * 15)))
    for nm in 'LR': K(Tb['legF' + nm], f, rot=(b['front'], 0, 0)); K(Tb['legB' + nm], f, rot=(b['back'], 0, 0))
    gq = gu_state(t); K(GU['root'], f, gq['loc'], gq['rot'])
    for nm, sx in (('L', -1), ('R', 1)): K(GU['shoulder' + nm], f, rot=(gq['arms'], 0, -sx * gq['spread']))
    # bottone che si schiaccia
    pr_ = 0.0
    for tp in (T_BOMB, T_BOOM): pr_ = max(pr_, 1.0 - lin01(abs(t - tp - 0.05), 0.0, 0.18))
    if t >= T_BOMBP: pr_ = max(pr_, max(0.0, -math.cos((t - T_BOMBP) * 18.0)))
    K(BTN['tasto'], f, scale=(1, 1, 1 - 0.6 * pr_))
    K(MED_C, f, loc=(0, 0, 0.8 + 0.05 * math.sin(t * 4)), rot=(0, 0, t * 2.5), scale=0.001 + 0.999 * ramp(t, T_SOGNO, T_SOGNO + 0.35))
    u = ramp(t, T_NOBEL2 + 0.3, T_TUMBO2); K(MED_T, f, loc=(0, -0.05 - 0.07 * u, 4.0 * (1 - u) - 0.36 * u), rot=(0.85, 0, 6 * (1 - u)))
    K(CARTELLO, f, scale=1.1 * (0.001 + 0.999 * ramp(t, T_ATTACCA + 0.45, T_ATTACCA + 0.6)))
    K(CUOCO, f, scale=0.001 + 0.999 * ramp(t, T_TUMBO + 0.1, T_TUMBO + 0.3))
    # pizza: esce dal forno e atterra sul tavolo; alla fine Tumbo se la mangia
    u = ramp(t, T_BUONA, T_BUONA + 0.5); pz = lerp(tuple(FORNOB), PIZON, u); pz = (pz[0], pz[1], pz[2] + 0.5 * math.sin(PI * u))
    K(PIZ, f, loc=pz, rot=(0, 0, 3 * u), scale=1.0 - 0.6 * ramp(t, T_TEAM + 0.7, T_TEAM2 + 0.5))
    # bombe nel deserto: cadono di traverso sulle colline vuote, puntando dove vanno
    K(GLOBO, f, rot=rot_globo(t))
    for k in range(5):                                                         # le bombe scendono sul paese (figlie del mappamondo)
        u = lin01(t, T_NAZ[k] - 0.75, T_NAZ[k]); n_ = P.punto(*P.PAESI[NAZ[k]])
        side = Vector((0, 0, 1)).cross(n_).normalized()
        pos = n_ * (RG + 0.45 + 7.0 * (1 - u) ** 1.5) + side * 2.5 * (1 - u)
        o = BOMBE['D%d' % k]; K(o, f, loc=tuple(pos), scale=0.8); KQ(o, f, -n_ - side * 0.35 * (1 - u))
        K(ETI[k], f, scale=0.001 + 0.999 * ramp(t, T_NAZ[k] + 0.05, T_NAZ[k] + 0.2) * (1.0 + 0.25 * math.exp(-max(0.0, t - T_NAZ[k] - 0.2) * 8)))
    # bomba di Gualtiero
    u = lin01(t, T_GUAL - 0.55, T_GUAL + 0.12); p0 = GUP + Vector((5.0, 3.0, 20.0)); p1 = GUP + Vector((0.5, 0.2, 0.6))
    K(BOMBE['G'], f, loc=tuple(p0.lerp(p1, u)), scale=1.3); KQ(BOMBE['G'], f, p1 - p0)
    # bombe sul mare: volano, frenano, si girano (cambiano idea), poi puntano giu' e cadono in mare: coriandoli a pelo d'acqua
    for k in range(3):
        bo = BOMBE['M%d' % k]; y0 = 14 + 3 * k; z0 = 12 + 2.5 * k; xs = XM - 7 + 4 * k
        if t < T_CAMB + 0.1:
            u = lin01(t, T_BOMBE - 0.05, T_CAMB + 0.1); x = XM - 30 + (xs - (XM - 30)) * (1 - (1 - u) ** 2); pos = Vector((x, y0, z0)); d = Vector((1, 0, -0.05))
        elif t < T_CADONO:
            a = PI * ramp(t, T_CAMB + 0.15 + 0.1 * k, T_ARIA + 0.1 * k)                 # si gira di mezzo giro
            pos = Vector((xs + 0.4 * math.sin(a), y0 - 0.8 * math.sin(a), z0 + 0.25 * math.sin(t * 6 + k))); d = Vector((math.cos(a), -math.sin(a) * 0.6, 0.0))
            d = d + Vector((0, 0, 0.12 * math.sin(t * 20 + k))) * (T_CAMB < t < T_ARIA + 0.3)
        else:
            u = lin01(t, T_CADONO, T_CORI + 0.07 * k); pos = Vector((xs - 1.5 * u, y0, z0 - (z0 - 1.6) * u * u)); d = Vector((-1, 0, 0)).lerp(Vector((-0.15, 0, -1)), ramp(t, T_CADONO, T_CADONO + 0.35))
        K(bo, f, loc=tuple(pos), scale=2.0); KQ(bo, f, d)
    # bomba sulla pizza: cade, si pianta nel tavolo accanto alla pizza (trema), poi esplode in coriandoli
    u = lin01(t, T_MAP - 0.05, T_MAP + 0.45); p1 = TAVZ + Vector((0, 0, 0.84 + 0.55)); p0 = p1 + Vector((2.5, 1.5, 16))
    tr_ = 0.06 * math.sin((t - T_MAP - 0.45) * 40) * math.exp(-(t - T_MAP - 0.45) * 3) if u >= 1 else 0.0
    K(BOMBE['Z'], f, loc=tuple(p0.lerp(p1, u)), scale=0.7); KQ(BOMBE['Z'], f, (p1 - p0) + Vector((tr_ * 20, 0, 0)))
    # sole, cielo, esposizione e luci per posto
    ph = fase(t); office = ph == 'UF'
    SUN.data.energy = 0.0 if office else 4.3; SUN.data.keyframe_insert('energy', frame=f)
    CIELO.inputs['Strength'].default_value = 0.06 if office else 0.4; CIELO.inputs['Strength'].keyframe_insert('default_value', frame=f)
    scene.view_settings.exposure = (EXP0 - 0.35) if office else EXP0; scene.view_settings.keyframe_insert('exposure', frame=f)
    LSCH.data.energy = 60 if T_CART - 0.1 <= t < T_ALLORA else 0; LSCH.data.keyframe_insert('energy', frame=f)
    LDAV.data.energy = 220 if T_ELUI - 0.1 <= t < T_ALLORA else 0; LDAV.data.keyframe_insert('energy', frame=f)

# coriandoli
def coriandoli(lista, centri, t0, t1, raggio, caduta, seme):
    rr = random.Random(seme)
    par = [(centri[i % len(centri)], Vector((rr.uniform(-1, 1), rr.uniform(-1, 1), rr.uniform(-0.1, 1))).normalized() * rr.uniform(0.4, 1.0) * raggio, rr.uniform(0.6, 1.4)) for i in range(len(lista))]
    for (o, *_r) in lista: K(o, 1, loc=(0, 0, -50))
    for f in range(1, NF + 1):
        t = (f - 1) / FPS
        on = t0 <= t < t1
        if not (t0 - 2 / FPS <= t < t1 + 2 / FPS): continue
        for (o, a, b, c, d), (cc, v, sp) in zip(lista, par):
            if not on: K(o, f, loc=(0, 0, -50)); continue
            u = t - t0; e = 1 - math.exp(-u * 5)
            K(o, f, loc=(cc[0] + v.x * e + 0.3 * math.sin(u * 3 + a), cc[1] + v.y * e + 0.3 * math.cos(u * 2.5 + c), max(caduta[1], cc[2] + v.z * e - caduta[0] * u * sp)), rot=(a + u * 6 * b, c + u * 5, d + u * 4))
coriandoli(COR_M, [(XM - 7 + 4 * k - 1.5, 14 + 3 * k, 1.6) for k in range(3)], T_CORI, T_NOBEL2, 7.0, (1.0, 0.05), 11)
coriandoli(COR_P, [(PODIO.x, PODIO.y - 0.5, 4.5)], T_TUMBO2, T_BOMBP, 3.0, (0.9, 0.02), 12)
coriandoli(COR_Z, [(TAVZ.x, TAVZ.y, 1.5)], T_TEAM, TOTAL + 0.1, 3.2, (0.8, 0.02), 13)

# ======================= effetti =======================
def fx(name, pos, w, t0, dur, **k):
    try: return A.effetto(name, posizione=tuple(pos), larghezza=w, animazione=(fr(t0), int(dur * FPS)), collezione=prc, **k)
    except Exception as e: print('effetto', name, e)
fx('emoticon/hearts', CAPO + Vector((-0.5, 0, 2.45)), 0.5, T_SOGNO + 0.2, 1.0)
fx('emoticon/idea', CAPO + Vector((0.55, 0, 2.55)), 0.5, T_E + 0.3, 0.9)
fx('lampo/flash02', BT + Vector((0, -0.2, 0.3)), 0.5, T_BOMB + 0.03, 0.15, luce=1.5)
for k in range(5):
    q_ = IMPATTI[k] + Vector((0, -0.4, 0))
    dur = (0.3, 0.3) if k == 0 else (0.75, 1.6)                                  # il Venezuela sparisce quando il mappamondo gira
    fx('esplosione/explosion0%d' % (k % 4), q_, 1.7, T_NAZ[k], dur[0], luce=3.0)
    if k: fx('fumo_nero/blacksmoke%02d' % (2 * k), q_ + Vector((0, 0.1, 0.5)), 1.6, T_NAZ[k] + 0.3, dur[1], opacita=0.8)
    fx('lampo/flash0%d' % (k % 4), q_, 2.4, T_NAZ[k], 0.15, luce=2.0)
fx('emoticon/alert', GUP + Vector((0, 0, 2.6)), 0.6, T_EGU + 0.05, 0.6)
fx('esplosione/explosion05', GUP + Vector((0.5, -0.3, 1.6)), 5.0, T_GUAL + 0.1, 0.6, luce=6.0)
fx('fumo_nero/blacksmoke12', GUP + Vector((0.8, 0, 2.3)), 5.5, T_GUAL + 0.3, 1.5, opacita=0.85)
fx('fumo_nero/blacksmoke03', HEADG + Vector((-0.2, 0.3, 0.25)), 0.6, T_MA, 2.6, opacita=0.55)   # i capelli che fumano
fx('emoticon/stars', HEADG + Vector((0.0, 0.0, 0.8)), 0.3, T_MA, 1.0)
fx('lampo/flash04', BT + Vector((0, -0.2, 0.3)), 0.5, T_BOOM + 0.03, 0.15, luce=1.5)
fx('emoticon/hearts', ROSO + Vector((0, 0, 2.35)), 0.5, T_AMICA, 0.8)
fx('emoticon/laugh', CAPF + Vector((0.3, 0, 2.5)), 0.5, T_CART + 0.3, 1.2)
fx('emoticon/idea', PPP + Vector((0, 0, 2.6)), 0.55, T_ALLORA + 0.25, 1.4)
fx('sbuffo_bianco/whitepuff02', PPP + Vector((0, -0.2, 2.45)), 0.9, T_TUMBO + 0.05, 0.4, colore=(1, 1, 1))
fx('emoticon/hearts', Vector(PIZON) + Vector((0, 0, 0.55)), 0.5, T_BUONA + 0.5, 1.2)
fx('sbuffo_bianco/whitepuff04', Vector(PIZON) + Vector((0, 0, 0.65)), 0.8, T_BUONA + 0.4, 1.0, colore=(1.0, 0.85, 0.55), opacita=0.6)
for k in range(3):
    xs = XM - 7 + 4 * k
    fx('emoticon/question', (xs, 14 + 3 * k, 12 + 2.5 * k + 1.6), 1.4, T_CAMB + 0.25, 1.0)
    fx('emoticon/heart', (xs, 14 + 3 * k, 12 + 2.5 * k + 1.6), 1.4, T_ARIA + 0.15, 0.85)
    fx('lampo/flash0%d' % k, (xs - 1.5, 14 + 3 * k, 1.8), 4.0, T_CORI + 0.07 * k, 0.2, luce=4.0)
    fx('sbuffo_bianco/whitepuff%02d' % (k + 1), (xs - 1.5, 14 + 3 * k, 1.0), 4.0, T_CORI + 0.07 * k, 0.6, colore=(0.85, 0.95, 1.0), opacita=0.8)
fx('emoticon/stars', TBPOD + Vector((0.55, 0, 1.25)), 0.4, T_TUMBO2 + 0.1, 1.5)
fx('emoticon/exclamations', PPP + Vector((0, 0, 2.65)), 0.55, T_MAP + 0.45, 0.9)
fx('lampo/flash03', TAVZ + Vector((0, 0, 1.5)), 2.5, T_TEAM, 0.2, luce=3.0)
fx('emoticon/hearts', Vector((TAV.x + 0.15, TAV.y - 0.15, 1.6)), 0.55, T_TEAM + 0.9, 1.6)

# ======================= camera (a mano, come nel 028) =======================
SHOTS = [  # t0, t1, camera da, a, mira da, a, lente, diaframma, pugno, mano
    (0.0, T_SOGNO, (XO + 1.4, -2.6, 2.1), (XO + 0.7, -1.0, 1.95), (XO, 1.5, 1.7), (XO, 1.6, 1.85), 28, 5.0, 1.0, 0.6),                                          # 01 l'ufficio, la camera entra
    (T_SOGNO, T_VOGLIO, (XO + 0.5, -0.9, 2.1), (XO + 0.45, -0.6, 2.15), (XO, CAPO.y, 2.35), (XO, CAPO.y, 2.4), 30, 3.0, 1.0, 0.5),                            # 02 sogna il Nobel
    (T_VOGLIO, T_E, (XO + 0.35, -0.3, 1.8), (XO + 0.3, 0.05, 1.8), (XO, CAPO.y, 1.75), (XO, CAPO.y, 1.78), 34, 2.4, 1.0, 0.6),                               # 03 «Voglio il Nobel»
    (T_E, T_NAZ[0] - 0.25, (XO + 1.75, 0.15, 1.45), (XO + 1.6, 0.3, 1.4), (XO + 0.25, 1.2, 1.3), (XO + 0.3, 1.15, 1.15), 32, 3.5, 1.2, 0.6),           # 04 la mano sul bottone (di lato)
    (T_NAZ[0] - 0.25, T_NAZ[1] - 0.25, (XG.x + 1.5, -19.5, 1.5), (XG.x + 0.8, -16.5, 0.8), (XG.x, 0, 0.3), (XG.x, 0, 0.2), 35, 30, 1.0, 0.4),                             # 05 bombe 1
    (T_NAZ[1] - 0.25, T_EGU, (XG.x - 0.5, -15.5, 1.1), (XG.x + 0.3, -13.8, 0.8), (XG.x, 0, 0.3), (XG.x + 0.2, 0, 0.2), 35, 30, 1.0, 0.4),                                        # 06 bombe 2
    (T_EGU, T_GUAL + 0.1, (GUP.x + 2.2, GUP.y - 4.2, 1.2), (GUP.x + 2.0, GUP.y - 3.7, 1.1), (GUP.x, GUP.y, 1.9), (GUP.x, GUP.y, 2.7), 26, 6.0, 1.0, 0.8),   # 07 Gualtiero guarda in su
    (T_GUAL + 0.1, T_MA, (GUP.x + 6.5, GUP.y - 9.5, 2.8), (GUP.x + 6.0, GUP.y - 8.8, 4.2), (GUP.x, GUP.y, 2.5), (GULY.x, GULY.y, 4.0), 24, 12, 1.0, 1.2),   # 08 esplosione
    (T_MA, T_MA2, (GULY.x + 2.4, GULY.y - 1.4, 2.7), (GULY.x + 2.2, GULY.y - 1.1, 2.4), (GULY.x - 0.5, GULY.y + 0.75, 0.4), (GULY.x - 0.55, GULY.y + 0.8, 0.4), 30, 4, 1.0, 0.4),   # 09 «Ma perche'?»
    (T_MA2, T_PEACE, (HEADG.x + 0.55, HEADG.y - 0.8, 1.55), (HEADG.x + 0.5, HEADG.y - 0.7, 1.45), (HEADG.x, HEADG.y, 0.5), (HEADG.x, HEADG.y, 0.5), 30, 2.4, 1.35, 1.0),   # 10 «MA PERCHE', CAZZO?!»
    (T_PEACE, T_IO, (XO + 0.9, -1.9, 1.85), (XO + 0.6, -1.4, 1.8), (XO, CAPO.y, 1.6), (XO + 0.1, CAPO.y, 1.5), 30, 3.0, 1.0, 0.6),                          # 11 «Peace! Peace! Boom!»
    (T_IO, T_ELUI, (XO - 0.2, -2.4, 1.75), (XO - 0.35, -1.9, 1.75), (ROSO.x + 0.4, ROSO.y, 1.6), (ROSO.x + 0.2, ROSO.y, 1.65), 30, 3.0, 1.0, 0.6),        # 12 Rospina «la sua migliore amica»
    (T_ELUI, T_CART, (XO + 0.15, -3.8, 1.6), (XO + 0.1, -3.55, 1.6), (XO + 0.05, -1.5, 1.35), (XO + 0.05, -1.5, 1.4), 20, 4.0, 1.0, 0.6),                 # 13 le attacca il cartello
    (T_CART, T_ALLORA, (XO - 0.15, 0.55, 1.55), (XO - 0.25, 0.1, 1.4), (ROSF.x, ROSF.y + 0.25, 1.2), (ROSF.x, ROSF.y + 0.25, 1.15), 32, 3.0, 1.0, 0.5),   # 14 «Datemi un calcio»
    (T_ALLORA, T_TUMBO, (-1.6, -4.4, 1.9), (-1.0, -3.8, 1.85), (1.6, 2.6, 1.3), (1.4, 2.4, 1.35), 26, 6.0, 1.0, 0.8),                                     # 15 Pippo fa la cosa piu' logica
    (T_TUMBO, T_BUONA, (PPP.x + 0.9, PPP.y - 2.3, 1.9), (PPP.x + 0.85, PPP.y - 1.9, 1.85), (PPP.x, PPP.y, 1.95), (PPP.x, PPP.y, 1.95), 32, 3.0, 1.0, 0.6),   # 16 «Tumbo, oggi facciamo la pizza!»
    (T_BUONA, T_BOMBE, (TAV.x - 0.6, TAV.y - 2.6, 1.75), (TAV.x - 0.5, TAV.y - 2.2, 1.65), (TAV.x + 0.7, TAV.y + 0.8, 1.05), (TAV.x + 0.3, TAV.y + 0.4, 0.95), 24, 5.0, 1.0, 0.6),   # 17 la pizza esce dal forno
    (T_BOMBE, T_CADONO, (XM - 12, -5, 9.5), (XM - 7, -4, 10.5), (XM - 12, 18, 13.5), (XM - 3, 18, 14.0), 26, 12, 1.0, 0.8),                                # 18 le bombe cambiano idea
    (T_CADONO, T_NOBEL2, (XM - 3, -7, 4.5), (XM - 2.5, -6, 3.5), (XM - 3, 18, 11), (XM - 3, 18, 3.0), 24, 12, 1.0, 0.9),                                    # 19 cadono in mare: coriandoli
    (T_NOBEL2, T_VINCE, (PODIO.x - 0.6, PODIO.y - 6.6, 2.4), (PODIO.x - 0.3, PODIO.y - 5.6, 2.2), (PODIO.x, PODIO.y, 1.6), (PODIO.x, PODIO.y, 1.4), 28, 6.0, 1.0, 0.7),   # 20 il Nobel per la pace...
    (T_VINCE, T_BOMBP, (PODIO.x + 0.3, PODIO.y - 2.6, 1.5), (PODIO.x + 0.25, PODIO.y - 2.2, 1.45), (TBPOD.x, TBPOD.y, 1.15), (TBPOD.x, TBPOD.y, 1.2), 32, 3.0, 1.25, 0.6),   # 21 ...lo vince Tumbo
    (T_BOMBP, T_MAP, (XO + 0.45, -0.9, 1.7), (XO + 0.4, -0.5, 1.7), (XO + 0.1, CAPO.y, 1.5), (XO + 0.1, CAPO.y, 1.55), 30, 2.4, 1.2, 1.2),                  # 22 «Bomb the pizza!»
    (T_MAP, T_TEAM, (TAV.x - 1.6, TAV.y - 3.6, 1.6), (TAV.x - 1.4, TAV.y - 3.2, 1.6), (TAV.x, TAV.y, 1.3), (TAV.x + 0.1, TAV.y, 1.15), 28, 4.0, 1.0, 0.7),     # 23 la bomba sul tavolo
    (T_TEAM, TOTAL + 0.1, (TAV.x - 1.2, TAV.y - 4.6, 2.0), (TAV.x - 1.6, TAV.y - 5.8, 2.3), (TAV.x - 0.3, TAV.y - 0.5, 1.3), (TAV.x - 0.4, TAV.y - 0.5, 1.4), 28, 6.0, 1.0, 0.6),   # 24 coriandoli: Team Tumbo o team Cappellone?
]
SHAKES = [(T_BOMB, 0.01, 0.3), (T_NAZ[0], 0.008, 0.4), (T_NAZ[1], 0.008, 0.4), (T_NAZ[2], 0.008, 0.4), (T_NAZ[3], 0.008, 0.4), (T_NAZ[4], 0.01, 0.4), (T_GUAL + 0.1, 0.03, 0.6),
          (T_MA2, 0.012, 0.4), (T_BOOM, 0.012, 0.4), (T_DATEMI, 0.008, 0.3), (T_CORI, 0.01, 0.5), (T_TUMBO2, 0.008, 0.3), (T_BOMBP, 0.012, 0.6), (T_MAP + 0.45, 0.015, 0.4), (T_TEAM, 0.012, 0.5)]
def hn(t, s): return 0.6 * math.sin(t * 1.7 + s) + 0.3 * math.sin(t * 3.3 + 2.1 * s) + 0.12 * math.sin(t * 7.9 + 3.7 * s)
for f in range(1, NF + 1):
    t = (f - 1) / FPS
    s_ = next((s for s in SHOTS if fr(s[0]) <= f < fr(s[1])), SHOTS[-1]); u = sm(max(0.0, (t - s_[0]) / (s_[1] - s_[0])))
    cl = Vector(lerp(s_[2], s_[3], u)); tl = Vector(lerp(s_[4], s_[5], u))
    d = (tl - cl).length
    cl = cl + Vector((hn(t, 1), 0.5 * hn(t, 2), hn(t, 3))) * s_[9] * d * 0.012; tl = tl + Vector((hn(t, 4), 0, hn(t, 5))) * s_[9] * d * 0.005
    for (t0, a_, d_) in SHAKES:
        if t0 <= t < t0 + d_:
            k = a_ * d * (1 - (t - t0) / d_); cl = cl + Vector((k * math.sin(t * 61), 0, k * 0.7 * math.sin(t * 47)))
    lens = s_[6] * (1 + (s_[8] - 1) * sm(min(1.0, (t - s_[0]) / 0.09)))
    cam.location = cl; tgt.location = tl; camd.lens = lens; camd.dof.aperture_fstop = s_[7]
    cam.keyframe_insert('location', frame=f); tgt.keyframe_insert('location', frame=f); camd.keyframe_insert('lens', frame=f); camd.dof.keyframe_insert('aperture_fstop', frame=f)

kitlook.tune_cutouts(1.9)
def lin(idb):
    for fc in all_fcurves(idb):
        kind = 'CONSTANT' if 'hide' in fc.data_path else 'LINEAR'
        for kp in fc.keyframe_points: kp.interpolation = kind
for o in bpy.data.objects: lin(o)
for d in [SUN.data, LSCH.data, LDAV.data, scene.world.node_tree]:
    for fc in all_fcurves(d):
        for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'
set_interp(camd, 'CONSTANT')
for nm in ('Cam', 'CamTarget'):
    for fc in all_fcurves(bpy.data.objects[nm]):
        for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'
for fc in all_fcurves(scene):
    for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'
try: scene.render.use_motion_blur = True; scene.render.motion_blur_shutter = 0.06
except Exception: pass
os.makedirs(os.path.dirname(os.path.abspath(BLEND)), exist_ok=True)
json.dump([[round(s[0], 3), round(min(s[1], TOTAL), 3)] for s in SHOTS], open(os.path.join(os.path.dirname(os.path.abspath(BLEND)), 'shots.json'), 'w'))
bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(BLEND)); print('SAVED', BLEND, len(bpy.data.objects), 'oggetti')
