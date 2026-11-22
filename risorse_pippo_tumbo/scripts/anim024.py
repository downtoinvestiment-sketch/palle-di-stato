"""TESTA STANDARD di ogni episodio: mondo, quartiere (casa di Pippo a est, casa di Gualtiero a ovest, staccionata, strada), funzioni house_at / tower_at / tree.
Uso: cat templates/head.py scripts/animNNN_body.py > scripts/animNNN.py  (cambia TOTAL e gli import prima).
Video 024 - MARTINA, IL CONO STRADALE. Salva ../t024/pippo_t024.blend
Personaggi: Pippo e Tumbo ESISTENTI (pippo.py, tumbo.py) invariati; Gualtiero = nuovo vicino ricorrente (props009.gualtiero)."""
import sys, math, os
sys.path.insert(0, os.path.dirname(__file__))
import bpy, numpy as np
from mathutils import Vector, Euler, Matrix
from common import *
from render_setup import *
import set004, props004, props007, props009, props010, props012, props013, props015, props016b, kitlook, lookdev, pippo, tumbo
from set004 import obj, bx, cyl, ball_, MB

FPS = 24; TOTAL = 45.2; NF = int(TOTAL * FPS)
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
# Video 024 - MARTINA, IL CONO STRADALE, 45,2 s. Si unisce alla testa: cat templates/head.py scripts/anim024_body.py > scripts/anim024.py
# Copione n. 21 (COPIONI.md). Scelte dell'autore (18-19 novembre 2026): M1 cono vero col cartellino, S1 semaforo all'italiana,
# R1 rullo compressore, K1 camion della nettezza (Kenney garbage-truck), V2 Italia dallo spazio di notte.
# Posti: il cantiere sulla strada del quartiere (giorno e notte), l'autostrada piena di coni (x = 600), la cartina dell'Italia (x = 1000).
# Indizi: il semaforo lampeggia giallo quando Pippo stringe Martina e di notte la illumina; Martina e' un po' piu' vicina al semaforo
# in ogni scena. Pippo usa le emozioni esagerate di pippo2. Luce «cinema». Tempi presi da audio/words_t024.json.
# ===================================================================================================================
import props024, props021, props023, luci, random
import pippo2 as pippo
A = kitlook.A
BLEND = os.environ.get('BLEND024', '../t024/pippo_t024.blend')
FONT = bpy.data.fonts.load(A.font('luckiest')); FONTS = bpy.data.fonts.load(A.font('anton')); FONTM = bpy.data.fonts.load(A.font('chewy'))
M24 = props024.mats024()
rnd = random.Random(24)

# ======================= tempi (dalla voce) =======================
T_CUT2 = 5.0                                     # record scratch, poi «Martina e' un cono stradale» (5,60)
T_FIORI = 7.45; T_NIENTE = 9.04; T_ECONO = 9.82; T_PORCA = 10.46
T_CHIUDE = 11.62; T_40 = 12.72                   # «Ma il cantiere chiude... dopo 40 anni»
T_BUCA = 14.66; T_MINCH = 16.60                  # notte: «riapre la buca col cucchiaino, quel minchione»
T_COMUNE = 17.62; T_FLAT = 18.75; T_BAST = 19.00 # il rullo arriva e lo spiaccica
T_ALBA = 19.9; T_POP = 20.45; T_SU = 21.0        # il giorno dopo: spiaccicato, si rigonfia, salta in piedi
T_LOGICA = 21.26                                 # «Allora Pippo fa la cosa piu' logica»
T_COMPRA = 24.12; T_SOLA = 25.95                 # «Compra TUTTI i coni d'Italia! Cosi' Martina non resta sola»
T_ITALIA = 27.48; T_MAPPA = 28.3                 # «L'Italia diventa un unico cantiere»
T_NESSUNO = 30.66                                # «Nessuno nota la differenza» (il cartello)
T_MUOVE = 32.98; T_SALTO = 34.38                 # «Poi Martina, finalmente, si muove»
T_BRACCIA = 35.66; T_SCAPPA = 37.40; T_SEMAF = 38.12
T_STRONZA = 38.94; T_TESTA = 40.68; T_TEAM = 42.84; T_ROSSO = 44.0
TOTAL = 45.2; NF = int(TOTAL * FPS)

# ======================= rendering e luce =======================
setup_render(scene, 1080, 1920, samples=4, fps=FPS, frames=NF); scene.frame_end = NF
camd = bpy.data.cameras.new('Cam'); cam = bpy.data.objects.new('Cam', camd); cac.objects.link(cam); scene.camera = cam
camd.clip_start = 0.01; camd.clip_end = 3000; camd.sensor_width = 36
tgt = empty('CamTarget', (0, 0, 1), None, cac)
ct = cam.constraints.new('TRACK_TO'); ct.target = tgt; ct.track_axis = 'TRACK_NEGATIVE_Z'; ct.up_axis = 'UP_Y'
camd.dof.use_dof = True; camd.dof.focus_object = tgt
kitlook.upgrade(scene, M, envc, prc, extras=False)
scene.eevee.taa_render_samples = 4
CIELO = luci.cielo_basso(scene.world, 0.4)
VISTA = scene.world.node_tree.nodes.get('PT_cielo_vista'); V0 = VISTA.inputs['Strength'].default_value if VISTA else 1.0
scene.world.use_sun_shadow = False
SUN = luci.sole(prc, (0.35, -0.94), lato=1, energia=4.5)
LUNA = luci._luce(prc, 'Luna', 'SUN', (0, 0, 30), (3, 6, 0), 0.0, (0.55, 0.65, 1.0), False)
luci.ombre_pulite(scene, mezza_risoluzione=True)
props021.bagliore(scene, forza=0.3, soglia=1.5)
for x in (-6.0, 10.5):                                                  # lampioni vicino al cantiere (accesi di notte)
    A.modello('street_lamp_01', posizione=(x, -8.15, 0.05), altezza=4.2, rotazione=90, collezione=envc)
LAMPS = []
for x in (-6.0, 10.5):
    L_ = bpy.data.lights.new('Lampione', 'POINT'); lo_ = bpy.data.objects.new('Lampione', L_); prc.objects.link(lo_)
    lo_.location = (x, -9.0, 3.9); L_.color = (1.0, 0.72, 0.4); L_.energy = 0.0; L_.shadow_soft_size = 0.3; LAMPS.append(lo_)

# ======================= posti =======================
BUCA = Vector((3.35, -10.95, 0.02))
MART0 = Vector((2.55, -10.1, 0.02)); SEM_A = Vector((2.95, -8.2, 0.05))
DM = (SEM_A - MART0).normalized() * 0.07                                # indizio: a ogni scena Martina e' 7 cm piu' vicina al semaforo
P_A = Vector((1.6, -10.32, 0.02)); T_A = Vector((0.7, -10.85, 0.02)); P_B = Vector((1.5, -10.6, 0.02))
CARTA = Vector((4.65, -9.55, 0.02))
TRUCK_STOP = Vector((11.2, -11.9, 0.02)); TRUCK_IN = Vector((26.0, -11.9, 0.02))
P_N = Vector((2.45, -10.95, 0.02)); T_N = Vector((1.15, -12.1, 0.02)); BUCA_T = Vector((1.2, -11.45, 0.021))
ROLL_Y = -10.95; ROLL_X0 = 16.0; ROLL_V = 11.8
X0 = 600.0; X1 = 1000.0
MART_C = Vector((X0 + 7.6, 29.0, 0.03)); P_C = Vector((X0 + 7.3, 31.5, 0.03)); T_C = Vector((X0 + 6.0, 31.2, 0.03))
SEM_C = Vector((X0 + 8.4, 44.0, 0.03)); CONO2 = Vector((X0 + 8.55, 32.1, 0.03)); CART_C = Vector((X0 + 14.2, 26.4, 0.03))
TAG_TERRA = Vector((X0 + 8.05, 30.7, 0.035))
TAG_GIU = TAG_TERRA + Vector((0, -0.75, -0.075))                         # origine del cartellino quando la carta e' distesa per terra
TAG_MANO = P_C.lerp(CONO2, 0.3) + Vector((0.25, -0.05, 0.6))             # origine del cartellino quando Pippo lo tiene in mano
RADURA = (Vector((X0 + 7.6, 30.6, 0)), 3.0)                              # spiazzo senza coni attorno a Pippo e Martina

def shot_idx(t):
    """indice dell'inquadratura nel quartiere, per spostare Martina verso il semaforo."""
    return sum(1 for a in (T_CUT2, T_FIORI, T_CHIUDE, T_BUCA, T_ALBA) if t >= a)

# ======================= personaggi =======================
P = pippo.build_pippo(chc); Tb = tumbo.build_tumbo(chc, scale=0.75)
for r in (P['root'], Tb['root']): r.rotation_mode = 'XYZ'
for nm in 'LR': P['shoulder' + nm].rotation_mode = 'QUATERNION'
MT = props024.cono(chc, M24, H=1.2, font=FONT); MT['root'].rotation_mode = 'XYZ'
TAG = MT['tag']; TAG.parent = None; TAG.rotation_mode = 'XYZ'             # il cartellino segue Martina a mano: cosi' puo' cadere
SM = props024.semaforo(chc, M24, H=4.6, nome='SemM'); SM['root'].rotation_mode = 'XYZ'
C2 = props024.cono(prc, M24, H=1.2, font=None, testo=None, nome='ConoQualsiasi'); C2['root'].location = CONO2
MYH = material('P24_caschetto', (1.0, 0.72, 0.0), rough=0.35, coat=0.4)  # caschetto giallo di Tumbo
HAT = empty('Caschetto', (0, 0.02, 0.19), Tb['head'], chc)
ball_('CaschettoCupola', 1.0, (0, 0, 0), MYH, chc, parent=HAT, sc=(0.25, 0.27, 0.19))
obj('CaschettoTesa', shared_mesh('cyl:1:1'), (0, -0.04, -0.02), (0.28, 0.33, 0.022), MYH, chc, rot=(0.14, 0, 0), parent=HAT)

def mazzo(coll):
    R = empty('Mazzo', (0, 0, 0), None, coll)
    shape('MazzoCarta', 'cone', (0, 0, -0.32), (0.15, 0.15, 0.32), parent=R, mat=material('P24_carta_fiori', (0.98, 0.84, 0.9), rough=0.6), coll=coll)
    F = empty('Fiori', (0, 0, -0.32), R, coll); mats = []
    for k, (c, dx, dy, dz) in enumerate((((0.95, 0.05, 0.1), 0, 0, -0.06), ((1.0, 0.75, 0.0), 0.07, 0.02, -0.03), ((0.9, 0.25, 0.6), -0.07, 0.03, -0.03),
                                         ((0.6, 0.2, 0.9), 0.03, -0.06, -0.02), ((0.95, 0.05, 0.1), -0.03, 0.07, -0.02), ((1.0, 0.9, 0.95), 0.0, 0.0, 0.02))):
        m = material('P24_fiore%d' % k, c, rough=0.55); mats.append((m, c))
        ball_('Fiore', 0.09, (dx * 1.7, dy * 1.7, dz * 1.6 - 0.04), m, coll, parent=F)
    for k in range(5):
        a = k * 1.25; ball_('Foglia', 1.0, (0.13 * math.cos(a), 0.13 * math.sin(a), 0.02), material('P24_foglia', (0.15, 0.55, 0.12), rough=0.6), coll, parent=F, sc=(0.045, 0.09, 0.015))
    return R, F, mats
BOUQ, FIORI, FMATS = mazzo(chc); BOUQ.parent = P['elbowR']; BOUQ.location = (0, -0.03, -0.3)
SPOON = empty('Cucchiaino', (0, 0, 0), P['elbowR'], chc); SPOON.location = (0, -0.03, -0.3)
_acc = material('P24_acciaio', (0.85, 0.86, 0.88), rough=0.18, metallic=1.0)
cyl('CucManico', 0.011, 0.2, (0, 0, -0.1), _acc, chc, parent=SPOON); ball_('CucConca', 1.0, (0, 0.0, -0.235), _acc, chc, parent=SPOON, sc=(0.035, 0.012, 0.05))

# ======================= il cantiere (quartiere) =======================
def testo(coll, nome, body, size, mat, loc, rot=(PI / 2, 0, 0), parent=None, font=None, align='CENTER', estrudi=0.012):
    cu = bpy.data.curves.new(nome, 'FONT'); cu.body = body; cu.size = size; cu.align_x = align; cu.align_y = 'CENTER'; cu.extrude = estrudi
    if font: cu.font = font
    o = bpy.data.objects.new(nome, cu); o.location = loc; o.rotation_euler = rot; o.parent = parent; coll.objects.link(o); cu.materials.append(mat); return o

M_NERO_T = material('P24_testo_nero', (0.02, 0.02, 0.025), rough=0.6); M_ROSSO_T = material('P24_testo_rosso', (0.8, 0.02, 0.02), rough=0.5)
M_BLU_P = material('P24_pennarello', (0.05, 0.12, 0.65), rough=0.5); M_TRI = material('P24_rosso_segnale', (0.85, 0.03, 0.02), rough=0.35)
def cartello(coll, loc, versione=1986, nome='CartelloLavori'):
    """cartello del cantiere su due pali: «COMUNE - LAVORI IN CORSO - INIZIO LAVORI: 1986 - FINE LAVORI: ?»; versione 2026: corretto a pennarello."""
    R = empty(nome, loc, None, coll)
    for sx in (-0.85, 0.85): cyl(nome + 'Palo', 0.04, 2.95, (sx, 0.04, 1.47), M24['zincato'], coll, parent=R)
    props024.scatola_tonda(nome + 'Bordo', 2.0, 0.04, 1.42, 0.03, M_TRI, coll, R, (0, 0, 1.72))
    props024.scatola_tonda(nome + 'Pannello', 1.9, 0.05, 1.32, 0.025, M24['bianco'], coll, R, (0, -0.005, 1.72))
    me = bpy.data.meshes.new(nome + 'Tri'); h = 0.62
    me.from_pydata([(-h / 2 / 0.866 * 0.866, 0, 0), (h / 2 / 0.866 * 0.866, 0, 0), (0, 0, h * 0.866)], [], [(0, 1, 2)]); me.update(); me.materials.append(M_TRI)
    tri = bpy.data.objects.new(nome + 'Triangolo', me); coll.objects.link(tri); tri.parent = R; tri.location = (0, -0.03, 2.48)
    me2 = bpy.data.meshes.new(nome + 'Tri2'); h2 = 0.46
    me2.from_pydata([(-h2 / 2, 0, 0), (h2 / 2, 0, 0), (0, 0, h2 * 0.866)], [], [(0, 1, 2)]); me2.update(); me2.materials.append(M24['bianco'])
    t2 = bpy.data.objects.new(nome + 'Triangolo2', me2); coll.objects.link(t2); t2.parent = R; t2.location = (0, -0.035, 2.53)
    testo(coll, nome + 'Esclam', '!', 0.26, M_NERO_T, (0, -0.045, 2.66), parent=R, font=FONTS)
    yy = -0.04
    testo(coll, nome + 'T1', 'COMUNE', 0.12, M_NERO_T, (0, yy, 2.24), parent=R, font=FONTS)
    testo(coll, nome + 'T2', 'LAVORI IN CORSO', 0.2, M_ROSSO_T, (0, yy, 1.98), parent=R, font=FONTS)
    testo(coll, nome + 'T3', 'INIZIO LAVORI:', 0.15, M_NERO_T, (-0.84, yy, 1.66), parent=R, font=FONTS, align='LEFT')
    testo(coll, nome + 'T4', '1986', 0.17, M_NERO_T, (0.28, yy, 1.66), parent=R, font=FONTS, align='LEFT')
    testo(coll, nome + 'T5', 'FINE LAVORI:', 0.15, M_NERO_T, (-0.84, yy, 1.32), parent=R, font=FONTS, align='LEFT')
    if versione == 1986:
        testo(coll, nome + 'T6', '?', 0.17, M_NERO_T, (0.32, yy, 1.32), parent=R, font=FONTS, align='LEFT')
    else:
        obj(nome + 'Barra', set004.box_c(), (0.48, yy - 0.012, 1.67), (0.46, 0.01, 0.035), M_ROSSO_T, coll, rot=(0, 0.12, 0), parent=R)
        testo(coll, nome + 'Anno', '2026', 0.2, M_BLU_P, (0.52, yy - 0.015, 1.86), rot=(PI / 2, 0.08, 0), parent=R, font=FONTM, align='LEFT')
        testo(coll, nome + 'Mai', 'MAI', 0.26, M_BLU_P, (0.3, yy - 0.015, 1.3), rot=(PI / 2, -0.1, 0), parent=R, font=FONTM, align='LEFT')
    return R
CART_A = cartello(prc, CARTA, 1986, 'CartelloA')
CART_B = cartello(prc, CART_C, 2026, 'CartelloC')
def ragnatela(coll, parent, centro, r=0.55, nome='Ragnatela'):
    """ragnatela in un angolo (quarto di cerchio) nel piano XZ, davanti al cartello."""
    mw = material('P24_ragnatela', (0.95, 0.95, 0.95), rough=0.3, emit=(1, 1, 1), emit_strength=0.15)
    R = empty(nome, centro, parent, coll); c = Vector((0, 0, 0))
    angs = [-PI / 2 + k * (PI / 2) / 5 for k in range(6)]
    for a in angs: props023.tubo(nome + 'Raggio', c, Vector((r * math.cos(a), 0, r * math.sin(a))), 0.004, mw, coll, parent=R)
    for j, rr in enumerate((0.15, 0.27, 0.39, 0.5)):
        for a, b in zip(angs[:-1], angs[1:]):
            p1 = Vector((rr * math.cos(a), 0, rr * math.sin(a))); p2 = Vector((rr * math.cos(b), 0, rr * math.sin(b))); mid = (p1 + p2) / 2 * 0.93
            props023.tubo(nome + 'Filo', p1, mid, 0.003, mw, coll, parent=R); props023.tubo(nome + 'Filo', mid, p2, 0.003, mw, coll, parent=R)
    return R
WEB = ragnatela(prc, CART_A, (-0.92, -0.06, 2.4))
TRANS = []
for loc_, rz in (((3.75, -9.42, 0.02), 0.0), ((4.3, -10.75, 0.02), PI / 2)):
    t_ = props024.transenna(prc, M24); t_.location = loc_; t_.rotation_euler = (0, 0, rz); TRANS.append(t_)
M_BUCA = material('P24_buca', (0.018, 0.013, 0.009), rough=0.95); M_TERRA = material('P24_terra', (0.28, 0.19, 0.11), rough=0.95)
M_TOPPA = material('P24_toppa', (0.03, 0.03, 0.033), rough=0.55); M_NUOVO = material('P24_asfalto_nuovo', (0.012, 0.012, 0.014), rough=0.22, spec=0.6)
def buca(coll, nome, loc, rx, ry):
    R = empty(nome, loc, None, coll)
    obj(nome + 'Fondo', shared_mesh('cyl:1:1'), (0, 0, 0.004), (rx, ry, 0.008), M_BUCA, coll, parent=R)
    rim = props024.anello(nome + 'Bordo', 1.0, 0.09, M_TERRA, coll, parent=R, loc=(0, 0, 0.01)); rim.scale = (rx, ry, 1.0)
    for k in range(3):
        a = 0.6 + k * 2.1; ball_(nome + 'Mucchio', 1.0, (math.cos(a) * rx * 1.25, math.sin(a) * ry * 1.25, 0.0), M_TERRA, coll, parent=R, sc=(0.32, 0.26, 0.17))
    return R
B1 = buca(prc, 'Buca', BUCA, 0.85, 0.62)
B2 = buca(prc, 'BucaTumbo', BUCA_T, 0.9, 0.7)
TOPPA = obj('Toppa', shared_mesh('cyl:1:1'), (BUCA.x, BUCA.y, 0.024), (0.9, 0.66, 0.004), M_TOPPA, prc)
NUOVO = obj('AsfaltoNuovo', set004.box0(), (ROLL_X0, -12.25, 0.021), (0.01, 2.6, 0.004), M_NUOVO, prc)
TR = A.modello('kenney/car-kit/garbage-truck', posizione=(0, 0, 0.02), altezza=3.4, rotazione=-90.0, collezione=prc, appoggia=True)
bpy.context.view_layer.update()
TR0 = TR.location.copy()
_vv = [o.matrix_world @ v.co for o in TR.children_recursive if o.type == 'MESH' for v in o.data.vertices]
_zt = max(p.z for p in _vv); _xmin = min(p.x for p in _vv); _xmax = max(p.x for p in _vv); _ymin = min(p.y for p in _vv)
SIGN = empty('CartelloFineLavori', (0, 0, 0), None, prc)
props024.scatola_tonda('FineLavoriBordo', 2.7, 0.08, 0.78, 0.04, M_TRI, prc, SIGN, (0, 0, 0))
props024.scatola_tonda('FineLavoriPannello', 2.56, 0.1, 0.64, 0.03, M24['bianco'], prc, SIGN, (0, 0, 0))
testo(prc, 'FineLavoriTesto', 'FINE LAVORI', 0.38, M_ROSSO_T, (0, -0.06, -0.02), parent=SIGN, font=FONT)
testo(prc, 'FineLavoriTesto2', 'FINE LAVORI', 0.38, M_ROSSO_T, (0, 0.06, -0.02), rot=(PI / 2, 0, PI), parent=SIGN, font=FONT)
for sx in (-0.8, 0.8): cyl('FineLavoriAsta', 0.035, 0.6, (sx, 0, -0.62), M24['scuro'], prc, parent=SIGN)
SIGN.location = (_xmin + 0.3 * (_xmax - _xmin), 0.0, _zt + 0.95)
testo(prc, 'ScrittaComune', 'COMUNE', 0.42, material('P24_scritta_comune', (0.05, 0.25, 0.6), rough=0.5), ((_xmin + _xmax) / 2 + 0.4, _ymin - 0.02, 1.7), parent=None, font=FONTS)
for o_ in (SIGN, bpy.data.objects['ScrittaComune']):
    o_.parent = TR; o_.matrix_parent_inverse = TR.matrix_world.inverted()
RL = props024.rullo(prc, M24); RL['root'].scale = (1.35,) * 3; RL['root'].rotation_mode = 'XYZ'
RLL = bpy.data.lights.new('RulloLuce', 'POINT'); RLO = bpy.data.objects.new('RulloLuce', RLL); prc.objects.link(RLO); RLO.parent = RL['root']; RLO.location = (0.55, 0, 3.3)
RLL.color = (1.0, 0.42, 0.05); RLL.energy = 0.0; RLL.shadow_soft_size = 0.2

# ======================= l'autostrada (x = 600) =======================
GRASS = A.materiale('Grass001', dimensione=3.0, rilievo=0.8, tinta=(1.05, 1.35, 0.7), ruvidita=1.5)
ASF = A.materiale('asphalt_02', dimensione=6.0); CEM = A.materiale('Concrete034', dimensione=2.0)
MET = material('P24_guardrail', (0.62, 0.64, 0.66), rough=0.35, metallic=0.85); LINEA = material('P24_linea', (0.92, 0.92, 0.9), rough=0.6)
AUTS = []                                                                # tutto quello che sta sull'autostrada (per la visibilita')
g_ = bx('PratoAut', (X0 - 420, -380, -0.3), (X0 + 420, 980, 0.0), GRASS, prc); A.niente_ombra(g_); AUTS.append(g_)
AUTS.append(bx('CarreggiataAut', (X0 - 19.5, -380, 0.0), (X0 + 19.5, 980, 0.03), ASF, prc))
AUTS.append(bx('Spartitraffico', (X0 - 0.3, -380, 0.03), (X0 + 0.3, 980, 1.05), CEM, prc))
for s in (-1, 1):
    x = X0 + s * 19.6
    AUTS.append(bx('Guardrail', (x - 0.06, -380, 0.62), (x + 0.06, 980, 0.95), MET, prc))
    for xl in (1.9, 16.9): AUTS.append(bx('LineaBordo', (X0 + s * xl - 0.1, -380, 0.031), (X0 + s * xl + 0.1, 980, 0.035), LINEA, prc))
pts = [(X0 + s * xl, y, 0.033) for s in (-1, 1) for xl in (6.9, 11.9) for y in range(-380, 980, 12)]
NT = props024.nuvola('Trattini', pts, prc); props024.istanze(NT, obj('Trattino', set004.box_c(), (0, 0, 0), (0.2, 4.5, 0.004), LINEA, prc)); AUTS.append(NT)
pts = [(X0 + s * 19.6, y, 0.45) for s in (-1, 1) for y in range(-380, 980, 4)]
NP_ = props024.nuvola('PaliGuard', pts, prc); props024.istanze(NP_, obj('PaloGuard', set004.box_c(), (0, 0, 0), (0.1, 0.12, 0.9), MET, prc)); AUTS.append(NP_)
for k in range(5):                                                         # colline lontane
    AUTS.append(ball_('CollinaAut', 1.0, (X0 + (-1) ** k * rnd.uniform(90, 200), rnd.uniform(520, 820), -10.0), GRASS, prc, sc=(rnd.uniform(90, 140), 70, rnd.uniform(24, 40))))
for k in range(34):
    s = -1 if k % 2 else 1; x = X0 + s * rnd.uniform(26, 75); y = rnd.uniform(-60, 420)
    try: AUTS.append(A.albero_cartonato(rnd.choice(['island_tree_01', 'island_tree_02', 'fir_tree_01', 'pine_tree_01', 'jacaranda_tree']), posizione=(x, y, 0), altezza=rnd.uniform(9, 15), collezione=prc))
    except Exception as e: print('albero', e)
AUTO = []                                                                  # la coda infinita
for k in range(18):
    s = -1 if k % 3 == 0 else 1; lane = rnd.choice((4.4, 9.4, 14.4))
    aid = rnd.choice(['sedan', 'suv', 'taxi', 'van', 'hatchback-sports', 'suv-luxury', 'sedan-sports', 'delivery'])
    h_ = 2.9 if aid in ('van', 'delivery') else 2.25
    p_ = (X0 + s * lane + rnd.uniform(-0.4, 0.4), 105 + k * 7.5 + rnd.uniform(-2, 2), 0.03)
    try: AUTO.append((A.modello('kenney/car-kit/' + aid, posizione=p_, altezza=h_, rotazione=rnd.uniform(-6, 6), collezione=prc, appoggia=True), p_))
    except Exception as e: print('auto', e)
TRK = []
for y in (12.0, 58.0):
    TRK.append(A.modello('kenney/car-kit/garbage-truck', posizione=(X0 + 18.0, y, 0.03), altezza=3.4, rotazione=180.0, collezione=prc, appoggia=True))
def cono_mini(nome, seg, k=1.0):
    H = 1.2 * k; r0 = 0.22 * k; r1 = 0.035 * k
    rz = lambda z: r0 + (r1 - r0) * (z - 0.06 * k) / (H - 0.08 * k)
    fa = [(0.56 * k, 0.69 * k), (0.8 * k, 0.89 * k)]
    zs = [0.06 * k + 0.002, fa[0][0], fa[0][1], fa[1][0], fa[1][1], H - 0.03 * k]
    prof = [(0.0, 0.0), (0.27 * k, 0.0), (0.27 * k, 0.055 * k), (r0, 0.06 * k)] + [(rz(z), z) for z in zs] + [(0.02 * k, H - 0.006 * k), (0.0, H)]
    return props024.tornio(nome, prof, prc, [M24['arancio'], M24['bianco'], M24['nero']], seg=seg,
                           mat_idx=lambda z: 2 if z < 0.058 * k else (1 if any(a < z < b for a, b in fa) else 0))
def libero(x, y, auto_r=3.2):
    if (Vector((x, y, 0)) - RADURA[0]).length < RADURA[1]: return False
    if (Vector((x, y, 0)) - CART_C).length < 1.6 or abs(x - X0) < 0.8: return False
    if X0 + 4.5 < x < X0 + 15.6 and 21.0 < y < 28.0: return False          # dove stanno le camere delle scene vicine
    if X0 + 9.6 < x < X0 + 11.8 and 31.8 < y < 35.6: return False
    for _, p_ in AUTO:
        if abs(x - p_[0]) < 1.8 and abs(y - p_[1]) < auto_r: return False
    for t_ in TRK:
        if abs(x - (X0 + 18.0)) < 2.2 and any(abs(y - yy) < 4.5 for yy in (12.0, 58.0)): return False
    return True
CLOUDS = []                                                                # (nuvola, istante della caduta, fine)
SENTIERO = []                                                              # i coni sul sentiero della coppia: spariscono quando Martina scappa
def sul_sentiero(x, y): return X0 + 7.3 < x < X0 + 10.7 and 33.0 < y < 78.0
for (y0, y1, td) in ((-20, 40, 24.25), (40, 110, 24.55), (110, 230, 24.85), (230, 420, 25.15)):
    pts = []
    n = int(2 * 18.4 * (y1 - y0) * 0.5)
    for _ in range(n):
        s = -1 if rnd.random() < 0.5 else 1; x = X0 + s * rnd.uniform(0.85, 19.2); y = rnd.uniform(y0, y1)
        if not libero(x, y): continue
        (SENTIERO if sul_sentiero(x, y) else pts).append((x, y, 0.03))
    N_ = props024.nuvola('ConiAut', pts, prc); props024.istanze(N_, cono_mini('ConoAut', 9, 0.8)); CLOUDS.append((N_, td, TOTAL + 1))
N_ = props024.nuvola('ConiSentiero', SENTIERO, prc); props024.istanze(N_, cono_mini('ConoSentiero', 9, 0.8)); CLOUDS.append((N_, 24.55, T_SCAPPA))
for (y0, y1, td) in ((-60, 260, 25.35), (260, 700, 25.6)):
    pts = []
    for _ in range(int(2 * 180 * (y1 - y0) * 0.055)):
        s = -1 if rnd.random() < 0.5 else 1; pts.append((X0 + s * rnd.uniform(21.5, 200), rnd.uniform(y0, y1), 0.0))
    N_ = props024.nuvola('ConiCampi', pts, prc); props024.istanze(N_, cono_mini('ConoCampo', 6, 0.8)); CLOUDS.append((N_, td, TOTAL + 1))
print('CONI', sum(len(n_.data.vertices) for n_, _, _ in CLOUDS))
SEM_CAVO = obj('Cavo', shared_mesh('cyl:0.045:1'), (0, 0, -50), (1, 1, 1), M24['scuro'], chc); SEM_CAVO.rotation_mode = 'QUATERNION'

# ======================= l'Italia dallo spazio (x = 1000) =======================
IT = props024.italia(prc, scala=0.01, tipo='notte', coni=20000); IT['root'].location = (X1, 0, 0)

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
QUART = [(0.0, T_COMPRA)]; AUTOS = [(T_COMPRA, TOTAL + 1)]
show_only(IT['root'], [(T_MAPPA, T_NESSUNO)])
for n_, td, te in CLOUDS: show_only(n_, [(td - 0.05, te)])
for o in AUTS + [a_ for a_, _ in AUTO] + TRK: show_only(o, AUTOS)
show_only(CART_B, AUTOS); show_only(C2['root'], AUTOS)
show_only(CART_A, [(0.0, T_BUCA)]); show_only(WEB, [(0.0, T_BUCA)])
for t_ in TRANS: show_only(t_, [(0.0, T_BUCA)])
show_only(B1, [(0.0, T_COMUNE + 1.5)]); show_only(B2, [(T_BUCA, T_COMUNE + 1.5)])
show_only(TOPPA, [(T_BUCA, T_COMPRA)]); show_only(NUOVO, [(T_COMUNE, T_COMPRA)])
show_only(TR, [(T_CHIUDE, T_BUCA)])
show_only(RL['root'], [(T_COMUNE - 0.1, T_ALBA)])
show_only(BOUQ, [(T_FIORI, T_CHIUDE)]); show_only(SPOON, [(T_BUCA, T_FLAT)])
show_only(SEM_CAVO, [(T_SEMAF, TOTAL + 1)])
for o in list(envc.objects):
    if o.parent is None and o.name not in NEVER: show(o, QUART)

# ======================= luce: notte, spazio, giorno =======================
def chiavi(sock_owner, attr, valori, idx=None):
    for (t_, v) in valori:
        setattr(sock_owner, attr, v); sock_owner.keyframe_insert(attr, frame=fr(t_))
NOTTE0, NOTTE1, SP0, SP1 = T_BUCA, T_ALBA, T_MAPPA, T_NESSUNO
def giorno_notte(owner, attr, giorno, notte, spazio):
    chiavi(owner, attr, [(0.0, giorno), (NOTTE0 - 0.04, giorno), (NOTTE0, notte), (NOTTE1 - 0.04, notte), (NOTTE1, giorno), (SP0 - 0.04, giorno), (SP0, spazio), (SP1 - 0.04, spazio), (SP1, giorno)])
giorno_notte(SUN.data, 'energy', 4.5, 0.0, 0.0)
giorno_notte(LUNA.data, 'energy', 0.0, 0.7, 0.25)
giorno_notte(CIELO.inputs['Strength'], 'default_value', 0.4, 0.025, 0.0)
if VISTA: giorno_notte(VISTA.inputs['Strength'], 'default_value', V0, 0.02, 0.0)
giorno_notte(scene.view_settings, 'exposure', 0.25, 0.15, 0.0)
for lo_ in LAMPS: giorno_notte(lo_.data, 'energy', 0.0, 450.0, 0.0)

# ======================= pose =======================
def qdir(d, rest=(0, 0, -1)): return Vector(rest).rotation_difference(Vector(d).normalized())
def yaw_to(a, b): return math.atan2(b[0] - a[0], -(b[1] - a[1]))
ARMS_DOWN = dict(aL=(-0.14, 0, -1), aR=(0.14, 0, -1))
def braccia(nome, forza=1.0):
    b = pippo.EMOZIONI_FORTI[nome]['braccia']; return {'aL': tuple(Vector((0, 0, -1)).lerp(Vector(b[0]).normalized(), forza)), 'aR': tuple(Vector((0, 0, -1)).lerp(Vector(b[1]).normalized(), forza))}
def mixv(a, b, u): return tuple(Vector(a).lerp(Vector(b), u))
def stretta(t):
    """tre strette nell'hook (il semaforo lampeggia giallo a ognuna)."""
    return max(math.sin(PI * min(1.0, max(0.0, (t - a) / 0.5))) for a in (0.8, 2.3, 3.8))
STRETTE = [(0.8, 1.3), (2.3, 2.8), (3.8, 4.3)]

def salti(t, tappe):
    """tappe = [(t0, t1, da, a, altezza)]: posizione e schiacciamento (1 = normale) di chi saltella."""
    pos = Vector(tappe[0][2]); sq = 1.0
    for (a, b, p0, p1, h) in tappe:
        if t < a: break
        if t >= b: pos = Vector(p1); continue
        u = (t - a) / (b - a); pos = Vector(p0).lerp(Vector(p1), u); pos.z += h * 4 * u * (1 - u)
        sq = 1.0 + 0.18 * math.sin(PI * u) if 0.1 < u < 0.9 else 0.82
        return pos, sq
    for (a, b, p0, p1, h) in tappe:                                   # schiacciata appena atterrata
        if b <= t < b + 0.12: sq = 0.82 + 0.18 * (t - b) / 0.12
    return pos, sq

def mart_pos(t):
    """Martina: posizione, yaw, schiacciamento."""
    if t < T_COMPRA: return MART0 + DM * shot_idx(t), 0.0, 1.0
    if t < T_SALTO: return MART_C, 0.0, 1.0
    p1 = MART_C + Vector((0.15, 1.0, 0)); p2 = MART_C + Vector((0.7, 2.4, 0)); p3 = MART_C + Vector((0.6, 4.6, 0)); p4 = Vector((X0 + 8.6, 36.6, 0.03))
    tappe = [(T_SALTO, T_SALTO + 0.42, MART_C, MART_C, 0.55),
             (T_BRACCIA + 0.25, T_BRACCIA + 0.7, MART_C, MART_C + Vector((0.07, 0.5, 0)), 0.45), (T_BRACCIA + 0.85, T_BRACCIA + 1.3, MART_C + Vector((0.07, 0.5, 0)), p1, 0.45),
             (T_SCAPPA, T_SCAPPA + 0.35, p1, p2, 0.6), (T_SCAPPA + 0.38, T_SCAPPA + 0.7, p2, p3, 0.7), (T_SCAPPA + 0.73, T_SEMAF + 0.1, p3, p4, 0.8)]
    t_ = T_SEMAF + 0.1; prev = p4
    while t_ < TOTAL + 0.5:                                           # via insieme, verso nord, saltando sopra i coni
        nxt = prev + Vector((0.05 * math.sin(t_ * 3), 1.6, 0)); tappe.append((t_, t_ + 0.42, prev, nxt, 1.35)); prev = nxt; t_ += 0.46
    p, sq = salti(t, tappe)
    return p, 0.0, sq

def sem_pos(t):
    """semaforo: posizione, yaw (le luci verso -Y con yaw 0), inclinazione."""
    if t < T_COMPRA: return SEM_A, 0.0, 0.0
    if t < T_BRACCIA: return SEM_C, 0.0, 0.0
    a = SEM_C; b = Vector((X0 + 9.4, 37.2, 0.03)); tappe = []; t_ = T_BRACCIA; n = 5
    for k in range(n):
        p0 = a.lerp(b, k / n); p1 = a.lerp(b, (k + 1) / n); tappe.append((t_, t_ + 0.4, p0, p1, 1.1)); t_ += 0.48
    prev = b; t_ = max(t_, T_SEMAF + 0.1)
    while t_ < TOTAL + 0.5:
        nxt = prev + Vector((-0.04 * math.sin(t_ * 2), 1.6, 0)); tappe.append((t_, t_ + 0.42, prev, nxt, 1.0)); prev = nxt; t_ += 0.46
    p, sq = salti(t, tappe)
    tilt = 0.12 * math.sin(t * 6.5) if t >= T_BRACCIA else 0.0
    return p, 0.0, tilt

def pp(t):
    S_ = dict(loc=P_A, yaw=yaw_to(P_A, MART0), lean=0.0, head=(0, 0, 0), sc=(1, 1, 1), rx=0.0, **ARMS_DOWN)
    if t < T_CUT2:                                                    # hook: abbraccia Martina, la stringe tre volte
        q = stretta(t)
        S_.update(lean=0.3 + 0.06 * q, head=(0.05, -0.22 - 0.05 * q, -1.05), aL=(0.22 + 0.12 * q, -0.9, -0.16), aR=(-0.22 - 0.12 * q, -0.9, -0.16))
    elif t < T_FIORI:                                                 # fa un passo indietro: «e' un cono»
        S_.update(loc=P_A + Vector((-0.75, -0.35, 0)), head=(0.15, 0, 0))
    elif t < T_CHIUDE:                                                # i fiori
        S_.update(loc=P_B, yaw=yaw_to(P_B, MART0 + DM * 2), head=(0.18, 0, 0))
        if t < T_NIENTE + 0.1: S_.update(aR=(0.08, -0.95, 0.12))
        elif t < T_ECONO: S_.update(aR=mixv((0.08, -0.95, 0.12), (0.12, -0.5, -0.8), ramp(t, T_NIENTE + 0.1, T_NIENTE + 0.6)), head=(0.4, 0, 0))
        else: S_.update(lean=0.12, head=(0.1, 0, 0), aR=(0.3, 0.2, -1), aL=(-0.3, 0.2, -1))
    elif t < T_BUCA:                                                  # arriva il camion del Comune
        S_.update(loc=P_B, yaw=yaw_to(P_B, (8, -12)) * ramp(t, T_CHIUDE, T_CHIUDE + 0.4) + yaw_to(P_B, MART0) * (1 - ramp(t, T_CHIUDE, T_CHIUDE + 0.4)), **braccia('spaventato', 0.7))
    elif t < T_FLAT:                                                  # di notte scava col cucchiaino
        dig = math.sin(t * 2 * PI * 3.2)
        if t < T_COMUNE + 0.25:
            S_.update(loc=P_N, yaw=yaw_to(P_N, BUCA), lean=0.72, head=(-0.25, 0, 0), aR=(0.1, -0.75 + 0.25 * dig, -0.62 - 0.25 * dig), aL=(-0.05, -0.55, -0.85))
        else:
            S_.update(loc=P_N, yaw=yaw_to(P_N, BUCA), lean=0.25, head=(-0.35, 0, 0), **braccia('spaventato'))
    elif t < T_SU:                                                    # spiaccicato sulla strada, poi si rigonfia
        g = ramp(t, T_POP, T_POP + 0.32); ov = 0.18 * math.sin(PI * ramp(t, T_POP + 0.2, T_SU))
        th = 0.07 + 0.93 * g + ov; w = 1.28 - 0.28 * g
        S_.update(loc=P_N, yaw=PI / 2, rx=-PI / 2, sc=(w, th, w), aL=(-0.8, 0, -0.6), aR=(0.8, 0, -0.6))
    elif t < T_LOGICA:                                                # salta in piedi
        u = ramp(t, T_SU, T_SU + 0.2); S_.update(loc=P_N, yaw=PI / 2 * (1 - u), rx=-PI / 2 * (1 - u), sc=(1, 1, 1 + 0.1 * math.sin(PI * u)))
    elif t < T_COMPRA:                                                # «Allora Pippo fa la cosa piu' logica»
        S_.update(loc=P_N, yaw=0.0, head=(0.05, 0, 0.08))
    elif t < T_MUOVE:                                                 # sull'autostrada, fiero
        if t < T_SOLA: S_.update(loc=P_C, yaw=0.0, **braccia('felice', 0.9))
        else: S_.update(loc=P_C, yaw=0.0, lean=0.12, head=(0.3, 0, 0), aL=(0.1, -0.7, -0.6), aR=(-0.1, -0.7, -0.6))
    elif t < T_BRACCIA:
        S_.update(loc=P_C, yaw=0.0, head=(0.32, 0, 0))
    elif t < T_SCAPPA + 0.25:                                         # apre le braccia
        S_.update(loc=P_C, yaw=0.0, head=(0.2, 0, 0), aL=(-0.88, -0.4, 0.12), aR=(0.88, -0.4, 0.12))
    elif t < T_TEAM:                                                  # si gira a guardarla andare via
        u = ramp(t, T_SCAPPA + 0.25, T_SEMAF + 0.4)
        S_.update(loc=P_C, yaw=-2.95 * u, head=(0.05, 0, 0), aL=mixv((-0.88, -0.4, 0.12), (-0.14, 0, -1), ramp(t, T_STRONZA, T_STRONZA + 0.5)),
                  aR=mixv((0.88, -0.4, 0.12), (0.14, 0, -1), ramp(t, T_STRONZA, T_STRONZA + 0.5)))
        if t >= T_STRONZA: S_.update(**braccia('arrabbiato', 1.0 - ramp(t, T_TESTA, T_TESTA + 0.4)))
    else:                                                             # raccoglie il cartellino e lo appende a un cono qualsiasi
        y_tag = yaw_to(P_C, TAG_TERRA); y_c2 = yaw_to(P_C, CONO2)
        u1 = ramp(t, T_TEAM, T_TEAM + 0.3); bend = math.sin(PI * ramp(t, T_TEAM + 0.25, T_TEAM + 0.85))
        u2 = ramp(t, T_TEAM + 0.85, T_TEAM + 1.15); step = ramp(t, T_TEAM + 0.95, T_TEAM + 1.25)
        yaw = (-2.95) * (1 - u1) + y_tag * u1; yaw = yaw * (1 - u2) + y_c2 * u2
        loc = P_C.lerp(CONO2, 0.32 * step)
        hug = ramp(t, T_ROSSO - 0.1, T_ROSSO + 0.25)
        S_.update(loc=loc, yaw=yaw, lean=0.55 * bend + 0.3 * hug, head=(0.3 * bend + 0.2 * hug, -0.3 * hug, 0),
                  aL=mixv(mixv((-0.14, 0, -1), (0.0, -0.8, -0.6), bend), (0.22, -0.9, -0.42), hug), aR=mixv(mixv((0.14, 0, -1), (0.1, -0.9, -0.4), bend), (-0.22, -0.9, -0.42), hug))
    return S_

def tp(t):
    """Tumbo: posizione, yaw, beccheggio (positivo = muso in giu'), zampe che scavano (0..1)."""
    if t < T_FIORI: return T_A, yaw_to(T_A, MART0), 0.0, 0.0
    if t < T_CHIUDE:
        p = Vector((3.25, -10.55, 0.02)); return p, yaw_to(p, MART0), 0.32, 0.0                   # annusa Martina
    if t < T_BUCA:
        p = Vector((3.25, -10.55, 0.02)); return p, yaw_to(p, (8, -12)), 0.0, 0.0
    if t < T_COMUNE + 0.55: return T_N, yaw_to(T_N, BUCA_T), 0.35, 1.0                             # scava una buca enorme
    if t < T_COMPRA:                                                                               # salta via prima del rullo
        u = ramp(t, T_COMUNE + 0.55, T_COMUNE + 1.0); a = T_N; b = Vector((0.6, -13.6, 0.02)); p = a.lerp(b, u); p.z += 1.2 * math.sin(PI * u)
        return p, yaw_to(a, b), 0.0, 0.0
    return T_C, 0.2, 0.0, 0.0

def sem_luci(t):
    """colore acceso del semaforo al tempo t."""
    if t < T_CUT2: return 'giallo' if any(a <= t < b for a, b in STRETTE) else 'rosso'
    if t < T_BUCA: return 'rosso'
    if t < T_ALBA: return 'giallo' if (t * 1.0) % 1.0 < 0.5 else None                            # di notte lampeggia
    if t < T_COMPRA: return 'rosso'
    if t < T_STRONZA + 0.3: return 'giallo' if (t * 1.2) % 1.0 < 0.5 else None                   # sull'autostrada: lampeggia, la sta aspettando
    if t < T_TESTA: return 'giallo' if any(a <= t < a + 0.22 for a in (T_STRONZA + 0.45, T_STRONZA + 0.95)) else None   # l'occhiolino a Pippo
    if t < T_ROSSO: return None if t < T_TESTA + 0.6 else 'verde'
    return 'rosso'

# ======================= chiavi =======================
def K(o, f, loc=None, rot=None, scale=None):
    if loc is not None: o.location = loc; o.keyframe_insert('location', frame=f)
    if rot is not None: o.rotation_euler = rot; o.keyframe_insert('rotation_euler', frame=f)
    if scale is not None: o.scale = scale if isinstance(scale, (tuple, list)) else (scale,) * 3; o.keyframe_insert('scale', frame=f)
_last_luce = [None]
for f in range(1, NF + 1):
    t = (f - 1) / FPS
    s = pp(t); K(P['root'], f, tuple(s['loc']), (s['lean'] + s['rx'], 0, s['yaw']), s['sc']); K(P['head'], f, rot=s['head'])
    for nm, k_ in (('L', 'aL'), ('R', 'aR')):
        sh = P['shoulder' + nm]; sh.rotation_quaternion = qdir(s[k_]); sh.keyframe_insert('rotation_quaternion', frame=f)
    # Tumbo
    p_, y_, pitch, dig = tp(t)
    K(Tb['root'], f, tuple(p_), (pitch, 0, y_), 0.75)
    for nm, sd in (('legFL', 0), ('legFR', 1)): K(Tb[nm], f, rot=((0.9 * math.sin(t * 2 * PI * 4.5 + sd * PI)) * dig, 0, 0))
    K(Tb['tail'], f, rot=(-0.5, 0, 0.6 * math.sin(t * 14)))
    # Martina e il suo cartellino
    mp, my, msq = mart_pos(t)
    K(MT['root'], f, tuple(mp), (0, 0, my), (1.0 / math.sqrt(msq), 1.0 / math.sqrt(msq), msq))
    if t < T_SCAPPA + 0.35: K(TAG, f, tuple(mp), (0, 0, my), (1.0 / math.sqrt(msq), 1.0 / math.sqrt(msq), msq))
    elif t < T_TEAM + 0.5:                                           # cade a terra: il cartellino resta disteso sull'asfalto
        u = ramp(t, T_SCAPPA + 0.35, T_SCAPPA + 0.75); a = mart_pos(T_SCAPPA + 0.35)[0]
        p = a.lerp(TAG_GIU, u); K(TAG, f, tuple(p), (-PI / 2 * u, 0, 0.4 * u), (1, 1, 1))
    elif t < T_TEAM + 1.25:                                          # in mano a Pippo
        u = ramp(t, T_TEAM + 0.5, T_TEAM + 1.2)
        p = TAG_GIU.lerp(TAG_MANO, u); K(TAG, f, tuple(p), (-PI / 2 * (1 - u), 0, 0.4 * (1 - u)), (1, 1, 1))
    else: K(TAG, f, tuple(CONO2), (0, 0, 0), (1, 1, 1))              # appeso al cono qualsiasi
    # semaforo
    sp, sy, tilt = sem_pos(t); K(SM['root'], f, tuple(sp), (tilt, 0, sy))
    c_ = sem_luci(t)
    if c_ != _last_luce[0]:
        if f > 1: props024.accendi(SM, _last_luce[0], frame=f - 1, luce=150.0 if T_BUCA <= t < T_ALBA else 35.0)
        props024.accendi(SM, c_, frame=f, luce=150.0 if T_BUCA <= t < T_ALBA else 35.0); _last_luce[0] = c_
    # il cavo tra il semaforo e Martina, come mano nella mano
    if t >= T_SEMAF:
        a = sp + Vector((0, 0, 2.2)); b = mp + Vector((0, 0, 1.12 * msq)); d = b - a
        SEM_CAVO.location = (a + b) / 2; SEM_CAVO.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d.normalized()); SEM_CAVO.scale = (1, 1, d.length)
        for pth in ('location', 'rotation_quaternion', 'scale'): SEM_CAVO.keyframe_insert(pth, frame=f)
    # camion del Comune
    u = ramp(t, T_CHIUDE, T_40 - 0.15); K(TR, f, tuple(TR0 + TRUCK_IN.lerp(TRUCK_STOP, u)))
    # rullo compressore: arriva da est e passa sopra a tutto
    xr = ROLL_X0 - max(0.0, t - T_COMUNE) * ROLL_V
    K(RL['root'], f, (xr, ROLL_Y, 0.02)); K(RL['tamburo'], f, rot=(PI / 2, -(ROLL_X0 - xr) / (0.7 * 1.35), 0))
    K(NUOVO, f, (min(ROLL_X0, xr - 1.6), -12.25, 0.021), (max(0.01, ROLL_X0 - xr + 1.6), 2.6, 0.004))
    # buche: Pippo riapre la sua, Tumbo ne scava una enorme, il rullo le chiude
    dig1 = 0.12 + 0.88 * ramp(t, T_BUCA + 0.2, T_COMUNE) if t >= T_BUCA else 1.0
    if t >= T_BUCA and xr < BUCA.x + 1.2: dig1 = 0.001
    dig2 = (0.1 + 1.0 * ramp(t, T_BUCA + 0.2, T_COMUNE - 0.4)) if t >= T_BUCA else 0.001
    if xr < BUCA_T.x + 1.2: dig2 = 0.001
    K(B1, f, scale=(dig1, dig1, 1.0)); K(B2, f, scale=(dig2, dig2, 1.0))
    # i fiori appassiscono
    dr = ramp(t, T_NIENTE, T_NIENTE + 0.5); K(FIORI, f, rot=(1.5 * dr, 0, 0))
    # le nuvole di coni piovono dal cielo
    for n_, td, te in CLOUDS:
        u = (t - td) / 0.55
        z = 22.0 if u < 0 else (22.0 * (1 - u * u) if u < 1 else 0.6 * math.sin(PI * min(1.0, (t - td - 0.55) / 0.25)))
        K(n_, f, (0, 0, z))
for k, (m, c) in enumerate(FMATS):                                    # i fiori diventano marroni
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*c, 1); b.inputs['Base Color'].keyframe_insert('default_value', frame=fr(T_NIENTE))
    b.inputs['Base Color'].default_value = (0.25, 0.16, 0.08, 1); b.inputs['Base Color'].keyframe_insert('default_value', frame=fr(T_NIENTE + 0.5))
for f in range(1, NF + 1):                                            # lampeggiante del rullo
    t = (f - 1) / FPS
    if T_COMUNE - 0.2 <= t < T_ALBA + 0.1:
        RLL.energy = 260.0 if (t * 2.4) % 1.0 < 0.5 else 0.0; RLL.keyframe_insert('energy', frame=f)

# ======================= cuori =======================
HM = props007.heart_mesh(N)
CUORI = []
for k in range(3):
    o = bpy.data.objects.new('Cuore', HM); chc.objects.link(o); o.rotation_mode = 'XYZ'; CUORI.append(o)
for f in range(1, NF + 1):
    t = (f - 1) / FPS
    for k, o in enumerate(CUORI):
        if t < T_CUT2:                                                # girano attorno alla testa di Pippo e pulsano
            a = t * 1.8 + k * 2.1; c = Vector((P_A.x + 0.45, P_A.y - 0.1, 2.75))
            p = c + Vector((0.5 * math.cos(a), 0.25 * math.sin(a), 0.15 * math.sin(a * 1.7))); s_ = 0.15 * (1 + 0.15 * math.sin(t * 9 + k))
            K(o, f, tuple(p), (0, 0.3 * math.sin(a), 0), s_)
        elif t < T_FIORI:                                             # cadono come sassi attorno a Martina
            u = ramp(t, T_CUT2, T_CUT2 + 0.35); m0 = MART0 + DM
            p0 = Vector((m0.x - 0.45 + 0.45 * k, m0.y - 0.35, 1.9 + 0.2 * k)); p1 = Vector((m0.x - 0.5 + 0.5 * k, m0.y - 0.5, 0.1))
            K(o, f, tuple(p0.lerp(p1, u * u)), (PI / 2 * u, 0.4 * k, 0), 0.15)
        elif T_BRACCIA <= t < T_SCAPPA + 0.4:                         # tornano quando apre le braccia
            a = t * 2.2 + k * 2.1; c = P_C + Vector((0, -0.2, 2.8))
            K(o, f, tuple(c + Vector((0.55 * math.cos(a), 0.25 * math.sin(a), 0.12 * math.sin(a * 1.5)))), (0, 0.3 * math.sin(a), 0), 0.16)
        elif t >= T_SEMAF + 0.2:                                      # ora girano sopra la coppia nuova
            a = t * 2.0 + k * 2.1; c = (sem_pos(t)[0] + mart_pos(t)[0]) / 2 + Vector((0, 0, 2.5))
            K(o, f, tuple(c + Vector((0.5 * math.cos(a), 0.25 * math.sin(a), 0.12 * math.sin(a * 1.5)))), (0, 0.3 * math.sin(a), 0), 0.17)
        else: K(o, f, (0, 0, -60), scale=0.15)

# ======================= espressioni =======================
_last = {}
def _ex(key, fn, t, k):
    if key in _last and t - 0.06 > _last[key][1]: fn(fr(t - 0.06), **_last[key][0])
    fn(fr(t), **k); _last[key] = (k, t)
_emo_last = [None]
def _emo_key(f, nome, forza, extra=None):
    e = pippo.EMOZIONI_FORTI[nome]
    fa = {k: (tuple(x * forza for x in v) if isinstance(v, tuple) else v * forza) for k, v in e['faccia'].items()}
    if extra: fa.update(extra)
    pippo.express(P, f, **fa)
    if 'sopracciglia' in e:
        for (s_, nm), b in zip(((-1, 'L'), (1, 'R')), e['sopracciglia']):
            br = P['brow' + nm]; br.rotation_euler = (0, s_ * b * 0.45 * forza, 0); br.keyframe_insert('rotation_euler', frame=f)
    seg = pippo._segni(P)
    ex_ = list(e.get('extra', ()))
    for k, g in seg.items():
        g.scale = (1, 1, 1) if (k in ex_ and forza > 0.3) else (0.001,) * 3
        g.keyframe_insert('scale', frame=f)
def emo(t, nome, forza=1.0, **extra):
    if _emo_last[0] and t - 0.06 > _emo_last[0][2]: _emo_key(fr(t - 0.06), _emo_last[0][0], _emo_last[0][1], _emo_last[0][3])
    _emo_key(fr(t), nome, forza, extra); _emo_last[0] = (nome, forza, t, extra)
def tex(t, **k): _ex('t', lambda f, **kk: tumbo.tumbo_express(Tb, f, **kk), t, k)
emo(0.0, 'felice', 1.0); emo(T_CUT2, 'sorpreso', 0.8); emo(T_FIORI, 'felice', 0.8); emo(T_NIENTE + 0.1, 'triste', 0.9); emo(T_ECONO, 'arrabbiato', 1.0)
emo(T_CHIUDE + 0.2, 'spaventato', 0.8); emo(T_40, 'sorpreso', 1.0); emo(T_BUCA, 'arrabbiato', 0.7); emo(T_COMUNE + 0.3, 'spaventato', 1.0)
emo(T_POP, 'sorpreso', 0.8); emo(T_LOGICA, 'furbo', 1.0); emo(T_COMPRA, 'felice', 1.0); emo(T_SOLA, 'felice', 0.6)
emo(T_SALTO + 0.12, 'sorpreso', 1.0); emo(T_BRACCIA, 'felice', 1.0); emo(T_SCAPPA + 0.35, 'sorpreso', 1.0); emo(T_SEMAF + 0.25, 'triste', 1.0)
emo(T_STRONZA, 'arrabbiato', 1.0); emo(T_TESTA, 'triste', 0.9); emo(T_ROSSO, 'felice', 0.7)
tex(0.0, tongue=0.6); tex(T_FIORI, tongue=0.0, brow=-0.2); tex(T_BUCA, tongue=0.9, eye_scale=1.1); tex(T_COMUNE + 0.4, tongue=0.0, eye_scale=1.35, brow=0.4)
tex(T_COMPRA, tongue=0.7, eye_scale=1.0, brow=0.0); tex(T_SCAPPA, tongue=0.0, brow=-0.5)

# ======================= effetti =======================
FXC = prc
def fx(name, pos, w, t0, dur, **k): return A.effetto(name, posizione=tuple(pos), larghezza=w, animazione=(fr(t0), int(dur * FPS)), collezione=FXC, **k)
for k in range(3): fx('sbuffo_bianco/whitepuff%02d' % (k * 2), TRUCK_STOP + Vector((-2.6 + 0.6 * k, -0.4, 0.4)), 1.4, T_40 - 0.2 + 0.05 * k, 0.6, colore=(0.85, 0.8, 0.72), opacita=0.7)
fx('sbuffo_bianco/whitepuff03', CARTA + Vector((0, -0.2, 2.0)), 1.6, T_40 + 0.1, 0.9, colore=(0.85, 0.8, 0.72), opacita=0.5)
for k in range(16):                                                   # terra che vola dalle zampe di Tumbo
    fx('particelle/dirt_0%d' % (k % 3 + 1), BUCA_T + Vector((rnd.uniform(-0.6, 0.6), rnd.uniform(-0.3, 0.4), 0.5 + rnd.uniform(0, 0.8))), 0.6, T_BUCA + 0.3 + 0.18 * k, 0.4, colore=(0.2, 0.13, 0.07), opacita=0.9)
for k in range(3): fx('sbuffo_bianco/whitepuff%02d' % (k + 4), P_N + Vector((-1.0 + k, -0.3, 0.3)), 1.8, T_FLAT - 0.05 + 0.04 * k, 0.6, colore=(0.7, 0.7, 0.75), opacita=0.6)
fx('emoticon/stars', P_N + Vector((-1.3, -0.2, 0.55)), 0.9, T_FLAT + 0.2, 1.0)
fx('emoticon/swirl', P_N + Vector((-2.2, -0.2, 0.5)), 0.6, T_FLAT + 0.3, 0.9)
fx('sbuffo_bianco/whitepuff01', P_N + Vector((-1.0, 0, 0.3)), 1.2, T_POP + 0.25, 0.4, opacita=0.6)
for k in range(10):                                                   # i coni che atterrano
    td = CLOUDS[min(k // 3, 3)][1]
    fx('sbuffo_bianco/whitepuff%02d' % (k % 8), (X0 + rnd.choice((-1, 1)) * rnd.uniform(3, 17), rnd.uniform(5, 80), 0.4), 3.0, td + 0.55, 0.5, colore=(0.85, 0.82, 0.75), opacita=0.6)
fx('sbuffo_bianco/whitepuff02', MART_C + Vector((0, -0.2, 0.15)), 0.7, T_SALTO + 0.42, 0.4, opacita=0.6)
fx('emoticon/exclamation', P_C + Vector((0.4, -0.3, 3.0)), 0.45, T_SALTO + 0.15, 0.9)
fx('emoticon/heartbroken', P_C + Vector((0.0, -0.3, 3.0)), 0.6, T_SCAPPA + 0.6, 1.4)
fx('emoticon/heart', CONO2 + Vector((-0.4, -0.3, 2.6)), 0.35, T_ROSSO + 0.3, 0.9)

# ======================= luce «cinema» =======================
LCA = luci.cinema(prc, (P_A.x + 0.4, P_A.y, 1.5), (P_A.x + 0.6, P_A.y - 4.0, 1.6), distanza=3.5, lato=-1, forza=0.8, nome='CinemaA')
LCC = luci.cinema(prc, (P_C.x, P_C.y - 1.0, 1.4), (P_C.x, P_C.y - 5.5, 1.6), distanza=4.0, lato=-1, forza=0.85, nome='CinemaC')
for l_ in LCA.values():
    e_ = l_.data.energy
    chiavi(l_.data, 'energy', [(0.0, e_), (T_BUCA - 0.04, e_), (T_BUCA, e_ * 0.35), (T_ALBA - 0.04, e_ * 0.35), (T_ALBA, e_), (T_COMPRA - 0.04, e_), (T_COMPRA, 0.0)])
for l_ in LCC.values():
    e_ = l_.data.energy
    chiavi(l_.data, 'energy', [(0.0, 0.0), (T_COMPRA - 0.04, 0.0), (T_COMPRA, e_), (T_MAPPA - 0.04, e_), (T_MAPPA, 0.0), (T_NESSUNO - 0.04, 0.0), (T_NESSUNO, e_)])

# ======================= camera =======================
SHOTS = [  # t0, t1, camera da, a, mira da, a, lente, diaframma
    (0.0, T_CUT2, (2.25, -14.7, 1.5), (2.2, -14.1, 1.55), (2.2, -10.1, 1.65), (2.2, -10.1, 1.75), 34, 4.0),                         # 01 hook: l'abbraccio
    (T_CUT2, T_FIORI, (2.62, -12.45, 0.8), (2.62, -12.25, 0.82), (2.62, -10.03, 0.72), (2.62, -10.03, 0.72), 40, 3.0),               # 02 e' un cono
    (T_FIORI, T_CHIUDE, (3.9, -13.6, 1.5), (3.75, -13.3, 1.5), (2.1, -10.25, 1.3), (2.1, -10.25, 1.3), 30, 5.0),                    # 03 i fiori
    (T_CHIUDE, T_40, (-2.6, -17.6, 2.4), (-2.4, -17.1, 2.4), (4.6, -10.6, 1.6), (4.8, -10.6, 1.6), 22, 11),                          # 04a il camion del Comune
    (T_40, T_BUCA, (4.65, -12.8, 1.9), (4.65, -12.35, 1.9), (4.65, -9.55, 1.95), (4.65, -9.55, 1.95), 26, 5.0),                     # 04b il cartello del 1986
    (T_BUCA, T_COMUNE, (0.8, -14.3, 1.35), (1.0, -13.9, 1.3), (2.2, -10.95, 0.6), (2.2, -10.95, 0.6), 28, 4.0),                      # 05a notte: il cucchiaino
    (T_COMUNE, T_ALBA, (-2.2, -15.6, 1.0), (-2.0, -15.3, 1.05), (3.6, -10.9, 1.5), (2.2, -10.9, 1.3), 22, 8),                        # 05b il rullo
    (T_ALBA, T_LOGICA, (1.0, -11.9, 6.4), (1.0, -11.7, 5.9), (1.0, -10.9, 0.0), (1.0, -10.9, 0.0), 30, 8),                           # 06a spiaccicato
    (T_LOGICA, T_COMPRA, (2.45, -13.4, 1.95), (2.45, -12.9, 1.95), (2.45, -10.95, 2.0), (2.45, -10.95, 2.05), 38, 2.8),              # 06b la cosa piu' logica
    (T_COMPRA, T_SOLA, (X0 + 16, -14, 6.8), (X0 + 15, -11, 6.2), (X0 + 7, 48, 0.6), (X0 + 7.5, 42, 0.9), 24, 16),                    # 07a piovono coni
    (T_SOLA, T_ITALIA, (X0 + 7.7, 24.9, 1.5), (X0 + 7.7, 25.5, 1.5), (X0 + 7.6, 30.0, 1.15), (X0 + 7.6, 30.0, 1.2), 30, 5.6),        # 07b non resta sola
    (T_ITALIA, T_MAPPA, (X0 + 8, 22, 3.0), (X0 + 8, 6, 70), (X0 + 8, 32, 0.5), (X0 + 8, 110, 0.0), 24, 22),                           # 08a la camera sale
    (T_MAPPA, T_NESSUNO, (X1 + 0.05, -0.75, 1.1), (X1 + 0.3, -6.6, 13.0), (X1 + 0.0, -0.12, 0.09), (X1 + 0.2, 0.2, 0.0), 30, 22),     # 08b l'Italia dallo spazio
    (T_NESSUNO, T_MUOVE, (X0 + 14.2, 23.15, 1.95), (X0 + 14.2, 23.6, 1.95), (X0 + 14.2, 26.4, 1.95), (X0 + 14.2, 26.4, 1.95), 26, 5),   # 09 il cartello corretto
    (T_MUOVE, T_BRACCIA, (X0 + 7.7, 26.5, 0.95), (X0 + 7.7, 26.7, 0.95), (X0 + 7.6, 29.0, 0.75), (X0 + 7.6, 29.0, 0.8), 38, 2.8),   # 10 si muove
    (T_BRACCIA, T_SCAPPA, (X0 + 6.2, 26.2, 1.8), (X0 + 6.3, 26.6, 1.8), (X0 + 7.5, 30.6, 1.5), (X0 + 7.5, 30.6, 1.5), 28, 5),       # 11 apre le braccia
    (T_SCAPPA, T_STRONZA, (X0 + 10.8, 23.6, 2.7), (X0 + 10.9, 24.1, 2.7), (X0 + 8.0, 34.0, 1.5), (X0 + 8.4, 37.0, 1.6), 26, 8),      # 12 scappa col semaforo
    (T_STRONZA, T_TESTA, (X0 + 11.2, 33.0, 4.6), (X0 + 11.2, 34.3, 4.6), (0, 0, 0), (0, 0, 0), 38, 4),                               # 13a l'occhiolino (mira sulla coppia)
    (T_TESTA, T_TEAM, (X0 + 7.0, 25.2, 2.3), (X0 + 7.0, 24.0, 2.7), (X0 + 7.6, 40, 1.8), (X0 + 7.6, 42, 1.8), 24, 11),              # 13b solo tra i coni
    (T_TEAM, TOTAL + 0.1, (X0 + 6.9, 26.2, 1.95), (X0 + 7.0, 26.6, 1.95), (X0 + 8.6, 38.0, 2.1), (X0 + 8.6, 38.0, 2.1), 28, 6),     # 14 finale
]
SHAKES = [(T_FLAT, 0.22, 0.6), (T_40 - 0.15, 0.06, 0.4)]
for f in range(1, NF + 1):
    t = (f - 1) / FPS
    s_ = next((s for s in SHOTS if s[0] <= t < s[1]), SHOTS[-1]); u = sm((t - s_[0]) / (s_[1] - s_[0]))
    if s_[0] == T_ITALIA: u = ((t - s_[0]) / (s_[1] - s_[0])) ** 1.6
    cl = Vector(lerp(s_[2], s_[3], u)); tl = Vector(lerp(s_[4], s_[5], u))
    if s_[0] == T_STRONZA: tl = (sem_pos(t)[0] + mart_pos(t)[0]) / 2 + Vector((0, 0, 1.7))
    for (t0, a_, d_) in SHAKES:
        if t0 <= t < t0 + d_:
            k = a_ * (1 - (t - t0) / d_); cl = cl + Vector((k * math.sin(t * 61), 0, k * 0.7 * math.sin(t * 47)))
    cam.location = cl; tgt.location = tl; camd.lens = s_[6]; camd.dof.aperture_fstop = s_[7]
    cam.keyframe_insert('location', frame=f); tgt.keyframe_insert('location', frame=f); camd.keyframe_insert('lens', frame=f); camd.dof.keyframe_insert('aperture_fstop', frame=f)

kitlook.tune_cutouts(1.9)
def lin(idb):
    for fc in all_fcurves(idb):
        kind = 'CONSTANT' if 'hide' in fc.data_path else 'LINEAR'
        for kp in fc.keyframe_points: kp.interpolation = kind
for o in bpy.data.objects: lin(o)
for d in [SUN.data, LUNA.data, RLL, scene.world.node_tree] + [lo_.data for lo_ in LAMPS] + [l_.data for l_ in list(LCA.values()) + list(LCC.values())]: lin(d)
for nm in SM['lampade']:
    lin(SM['lampade'][nm][1].node_tree); lin(SM['lampade'][nm][3].data)
for m, c in FMATS: lin(m.node_tree)
set_interp(camd, 'CONSTANT')
for nm in ('Cam', 'CamTarget'):
    for fc in all_fcurves(bpy.data.objects[nm]):
        for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'
for idb in [SM['lampade'][nm][1].node_tree for nm in SM['lampade']] + [SM['lampade'][nm][3].data for nm in SM['lampade']] + [RLL]:
    for fc in all_fcurves(idb):
        for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'
try:
    for fc in scene.animation_data.action.fcurves:
        for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'
except Exception: pass
try: scene.render.use_motion_blur = True; scene.render.motion_blur_shutter = 0.06
except Exception: pass
os.makedirs(os.path.dirname(os.path.abspath(BLEND)), exist_ok=True)
import json; json.dump([[round(s[0], 3), round(min(s[1], TOTAL), 3)] for s in SHOTS], open(os.path.join(os.path.dirname(os.path.abspath(BLEND)), 'shots.json'), 'w'))
bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(BLEND)); print('SAVED', BLEND, len(bpy.data.objects), 'oggetti')
