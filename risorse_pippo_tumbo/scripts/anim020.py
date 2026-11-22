"""Video 020 - IL TERZO PERSONAGGIO (promo del contest, copione n. 12). Salva ../t020/pippo_t020.blend
Tutto su un palco col sipario rosso (attorno all'origine). Scelte dell'autore: U cassa misteriosa (schede/scelta_promo.png), palco.
Voce: audio/voce_t020.mp3 (41,6 s), tempi in audio/words_t020.json (scritti qui sotto a mano).
Uso: python anim020.py"""
import sys, math, os, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, bmesh
from mathutils import Vector, Euler, Matrix
from common import *
from render_setup import *
import set004, props007, props009, props014, props019, animali, kitlook, tumbo, luci
import scheda_promo as SP
import pippo2 as pippo                                                                            # Pippo di sempre con le emozioni esagerate (regola dell'autore)
from set004 import obj, bx, cyl, ball_
A = kitlook.A

FPS = 24; TOTAL = 45.2; NF = int(TOTAL * FPS)
def fr(t): return max(1, int(round(t * FPS)) + 1)
def sm(x): x = min(1.0, max(0.0, x)); return x * x * (3 - 2 * x)
def ramp(t, a, b): return sm((t - a) / (b - a))
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def lerp(a, b, u): return tuple(a[i] + (b[i] - a[i]) * u for i in range(len(a)))
def yaw_to(a, b): return math.atan2(b[0] - a[0], -(b[1] - a[1]))
def qdir(d, rest=(0, 0, -1)): return Vector(rest).rotation_difference(Vector(d).normalized())
def fall(t, t0, t1, z0, z1):
    """caduta con gravita' da z0 a z1 tra t0 e t1, poi un piccolo rimbalzo."""
    if t < t0: return z0
    if t < t1: u = (t - t0) / (t1 - t0); return z0 + (z1 - z0) * u * u
    d = t - t1; return z1 + 0.25 * abs(math.sin(d * 9)) * math.exp(-d * 7) * (z0 - z1) * 0.15
PI = math.pi

# ======================= tempi (dalla voce: audio/words_t020.json) =======================
# Versione 2 (con gli insulti): voce accorciata a 44,9 s (tolto 1,2 s di silenzio dopo «Respinto», velocita' 1,075)
T_PIPPO, T_AEREO = 1.28, 3.34                   # «Pippo, quel coglione a pedali col cervello in modalita' aereo»
T_SPOT3, T_MANCA = 4.5, 5.02                    # «In squadra manca qualcuno»
T_MACH, T_DING = 5.96, 7.56                     # «Lo costruisce da solo» (cade la macchina), «Esce un tostapane»
T_RUN = T_DING + 1.75                           # il tostapane e' scappato
T_BRAVO = 9.36                                  # «Bravo, cicciomerda»
T_KICK, T_CHICK, T_CAZ, T_BOOM = 10.40, 10.96, 12.46, 13.06
T_GUAL, T_BAFFI, T_STAMP = 13.98, 16.66, 17.90
T_QUINDI, T_VOI, T_SCIMMIE = 19.10, 21.66, 22.60
T_W = (23.82, 24.38, 25.12, 25.78, 26.42)       # nome, aspetto, carattere, poteri, storia
T_TESTA, T_REGOLE, T_SEGUI, T_LIKE, T_COMM = 27.36, 29.38, 30.30, 31.26, 31.98
T_48, T_PIU, T_UFF = 33.62, 34.74, 35.88
T_GCOMM, T_G2, T_PEZZO, T_NO, T_MUOVI, T_COMMENTA, T_ADESSO = 38.14, 39.78, 40.80, 42.08, 42.68, 43.32, 43.90
T_END = 44.85

reset_scene(); scene = bpy.context.scene
setup_render(scene, 1080, 1920, samples=4, fps=FPS, frames=NF); scene.frame_end = NF
A.qualita_eevee(preset='equilibrato', riflessi=False, scena=scene); scene.view_settings.exposure = -0.15
envc = collection('Env'); chc = collection('Characters'); prc = collection('Props'); cac = collection('Cameras')
scene.world = bpy.data.worlds.new('W'); scene.world.use_nodes = True
_bg = next(n for n in scene.world.node_tree.nodes if n.type == 'BACKGROUND'); _bg.inputs['Color'].default_value = (0.02, 0.02, 0.04, 1); _bg.inputs['Strength'].default_value = 1.0
luci.cielo_basso(scene.world, 0.12)
FONT = A.font('luckiest'); FNT = bpy.data.fonts.load(FONT, check_existing=True)
G9 = props009.mats009(); T14 = props014.mats014(); M7 = props007.mats007()

camd = bpy.data.cameras.new('Cam'); cam = bpy.data.objects.new('Cam', camd); cac.objects.link(cam); scene.camera = cam
camd.clip_start = 0.05; camd.clip_end = 300; camd.sensor_width = 36
tgt = empty('CamTarget', (0, 0, 1), None, cac)
ct = cam.constraints.new('TRACK_TO'); ct.target = tgt; ct.track_axis = 'TRACK_NEGATIVE_Z'; ct.up_axis = 'UP_Y'
camd.dof.use_dof = True; camd.dof.focus_object = tgt

def m(n, col, **k): return material('T20_' + n, col, **k)
def txt(name, body, size, mat, loc, rot=(PI / 2, 0, 0), ext=0.06, parent=None, coll=None):
    cu = bpy.data.curves.new(name, 'FONT'); cu.body = body; cu.size = size; cu.align_x = 'CENTER'; cu.align_y = 'CENTER'; cu.extrude = ext; cu.bevel_depth = ext * 0.25; cu.font = FNT
    o = bpy.data.objects.new(name, cu); o.location = loc; o.rotation_euler = rot; o.parent = parent; (coll or prc).objects.link(o); cu.materials.append(mat); o.rotation_mode = 'XYZ'; return o
def grp(name, loc=(0, 0, 0), coll=None):
    g = empty(name, loc, None, coll or prc); g.rotation_mode = 'XYZ'; return g
def box(name, loc, size, mat, parent=None, rot=(0, 0, 0), coll=None): return props019.box(name, loc, size, mat, coll or prc, rot=rot, parent=parent)

# ======================= palco =======================
XS = 2.1; YS = 0.4                              # il posto vuoto (la cassa)
P0 = (-2.4, 0.4); T0 = (-0.75, 0.15)            # posti di Pippo e Tumbo sotto gli occhi di bue
legno = A.materiale('WoodFloor043', dimensione=2.0, tinta=(1.05, 0.9, 0.75))
box('Palco', (0, -2.0, -0.15), (24, 16, 0.3), legno, coll=envc)
rosso = A.materiale('velour_velvet', dimensione=0.8, tinta=(1.6, 0.25, 0.25))
SP.tenda(envc, rosso, -12, 12, -0.05, 14.0, 4.2, nome='Fondale')
SIPL = SP.tenda(envc, rosso, -4.6, 0.3, -0.05, 9.0, -0.9, pieghe=0.2, prof=0.35, nome='SipSx')     # sipario: chiuso a 0 s, si apre subito
SIPR = SP.tenda(envc, rosso, -0.3, 4.6, -0.05, 9.0, -0.9, pieghe=0.2, prof=0.35, nome='SipDx')
SP.tenda(envc, rosso, -12, -4.6, -0.05, 9.0, -0.9, pieghe=0.2, prof=0.35, nome='QuintaSx'); SP.tenda(envc, rosso, 4.6, 12, -0.05, 9.0, -0.9, pieghe=0.2, prof=0.35, nome='QuintaDx')
oro = m('oro', (0.85, 0.6, 0.18), rough=0.3, metallic=0.9)
SP.tenda(envc, rosso, -12, 12, 5.3, 6.6, -1.05, pieghe=0.5, prof=0.18, nome='Mantovana')
box('Frangia', (0, -1.15, 5.3), (24, 0.12, 0.14), oro, coll=envc)
FASC = SP.mat_emissione('Fascio', (1.0, 0.92, 0.7), forza=1.4, alfa=0.035)
SPOTS = []; CONES = []
for x in (P0[0], T0[0], XS):
    CONES.append(SP.cono_luce(prc, x, FASC))
    l = bpy.data.lights.new('OcchioBue', 'SPOT'); l.energy = 900; l.color = (1.0, 0.9, 0.7); l.spot_size = 0.42; l.spot_blend = 0.25; l.shadow_soft_size = 0.05
    o = bpy.data.objects.new('OcchioBue', l); prc.objects.link(o); o.location = (x, 0.4, 7.4); SPOTS.append(o)
LUCI = luci.cinema(prc, (0.0, 0.0, 1.4), (0.0, -9.0, 2.2), distanza=6.0, lato=1, forza=0.7)
luci.ombre_pulite(scene, mezza_risoluzione=True)

# ======================= personaggi =======================
P = pippo.build_pippo(chc); Tb = tumbo.build_tumbo(chc, scale=0.75); GU = props009.gualtiero(chc, G9)
for r in (P['root'], Tb['root'], GU['root']): r.rotation_mode = 'XYZ'
for nm in 'LR': P['shoulder' + nm].rotation_mode = 'QUATERNION'
mnero = m('nero', (0.01, 0.01, 0.012), rough=0.5)
BAFFI = grp('BaffiFinti', coll=chc); BAFFI.parent = GU['head']; BAFFI.location = (0, -0.33, -0.13)        # baffi finti enormi sopra i suoi
for s_ in (-1, 1):
    ball_('Baffo', 1.0, (s_ * 0.17, 0, 0), mnero, chc, parent=BAFFI, sc=(0.2, 0.07, 0.075))
    ball_('Ricciolo', 1.0, (s_ * 0.36, 0, 0.07), mnero, chc, parent=BAFFI, sc=(0.07, 0.06, 0.07))
CART = grp('CartelloIO', coll=chc); CART.parent = GU['root']; CART.location = (0.55, -0.25, 0.0)
box('Asta', (0, 0, 1.0), (0.05, 0.05, 1.6), M7['black'] if 'black' in M7 else mnero, parent=CART, coll=chc)
box('Tavola', (0, -0.03, 1.85), (0.75, 0.04, 0.5), m('cartone', (0.85, 0.66, 0.42), rough=0.9), parent=CART, coll=chc)
txt('IO', 'IO', 0.38, m('rossotesto', (0.85, 0.05, 0.05), rough=0.5), (0, -0.06, 1.83), ext=0.01, parent=CART, coll=chc)
PHONE = grp('Telefono', coll=chc)                                                                 # telefono gigante (da cartone) per il commento di Gualtiero
box('TelCorpo', (0, 0, 0), (0.42, 0.04, 0.78), m('telnero', (0.02, 0.02, 0.025), rough=0.25, spec=0.8), parent=PHONE, coll=chc)
box('TelSchermo', (0, -0.022, 0), (0.37, 0.005, 0.68), m('telschermo', (1, 1, 1), rough=0.5, emit=(0.95, 0.97, 1.0), emit_strength=1.6), parent=PHONE, coll=chc)
mtel = m('teltesto', (0.05, 0.05, 0.08), rough=0.6)
txt('TelNome', '@gualtiero', 0.045, m('telblu', (0.1, 0.35, 0.9), rough=0.6), (-0.06, -0.03, 0.12), ext=0.002, parent=PHONE, coll=chc)
txt('TelTesto', 'GUALTIERO 2', 0.06, mtel, (0.0, -0.03, 0.03), ext=0.002, parent=PHONE, coll=chc)
cuore = props007.heart_mesh(M7)
o_ = bpy.data.objects.new('TelCuore', cuore); chc.objects.link(o_); o_.parent = PHONE; o_.location = (-0.05, -0.03, -0.08); o_.scale = (0.035,) * 3
o_.rotation_euler = (0, 0, 0)
txt('TelUno', '1', 0.06, mtel, (0.03, -0.03, -0.085), ext=0.002, parent=PHONE, coll=chc)

# ======================= cassa misteriosa (scelta U) =======================
CASSA = grp('Cassa', (XS, YS, 0)); wd = A.materiale('weathered_planks', dimensione=0.9)
w_, h_ = 1.7, 1.55
box('Interno', (0, 0, h_ / 2), (w_ - 0.08, w_ - 0.08, h_ - 0.04), m('buio', (0, 0, 0), rough=1.0), parent=CASSA)
for s_ in (-1, 1):
    box('Lato', (s_ * w_ / 2, 0, h_ / 2), (0.08, w_, h_), wd, parent=CASSA); box('Lato', (0, s_ * w_ / 2, h_ / 2), (w_, 0.08, h_), wd, parent=CASSA)
for r_ in (0.83, -0.83): box('Croce', (0, -w_ / 2 - 0.05, h_ / 2), (0.14, 0.04, h_ * 1.25), wd, parent=CASSA, rot=(0, r_, 0))
LID = grp('Coperchio'); LID.parent = CASSA; LID.location = (w_ / 2, 0, h_)                         # cerniera sul lato destro
box('CoperchioAsse', (-w_ / 2 - 0.05, 0, 0.05), (w_ + 0.1, w_ + 0.1, 0.09), wd, parent=LID)
EYES = []
occ = SP.mat_emissione('OcchiBuio', (1.0, 0.95, 0.4), forza=8.0)
for s_ in (-1, 1): EYES.append(ball_('Occhio', 0.09, (-0.1 + s_ * 0.2, -0.55, h_ - 0.06), occ, prc, parent=CASSA, sc=(1, 0.4, 0.7)))
vern = m('vernice', (0.95, 0.85, 0.15), rough=0.6)
txt('CassaDomanda', '?', 0.7, vern, (-0.45, -w_ / 2 - 0.1, 1.05), ext=0.03, parent=CASSA)
viola = m('codaviola', (0.45, 0.1, 0.75), rough=0.4); verde = m('codaverde', (0.35, 0.9, 0.2), rough=0.4)
TAIL = []
for k in range(9): TAIL.append(ball_('Coda', 0.16 - 0.06 * k / 8, (0, 0, 0), viola if k % 2 else verde, prc, parent=CASSA))
QM = SP.punto_domanda(prc, (XS + 0.15, 0.1, 3.1), 0.8); QM.rotation_mode = 'XYZ'
PIED = box('Piedistallo', (XS, YS, 0.5), (2.1, 2.1, 1.0), m('orochiaro', (1.0, 0.68, 0.12), rough=0.3, spec=0.9))                                      # piedistallo d'oro del finale «ufficiale»
CROWN = grp('Corona')
for k in range(7):
    a = k * 2 * PI / 7; box('CoronaPunta', (0.42 * math.cos(a), 0.42 * math.sin(a), 0.3), (0.16, 0.16, 0.35), oro, parent=CROWN, rot=(0, 0, a))
cyl('CoronaBase', 0.47, 0.22, (0, 0, 0.1), oro, prc).parent = CROWN
for k in range(7):
    a = k * 2 * PI / 7; ball_('Gemma', 0.07, (0.49 * math.cos(a), 0.49 * math.sin(a), 0.12), m('gemma', (0.9, 0.05, 0.15), rough=0.1, spec=1.0), prc, parent=CROWN)

# ======================= Macchina dei Personaggi =======================
MX, MY = 0.35, 1.5
MACH = grp('Macchina', (MX, MY, 0))
mmet = m('macchina', (0.05, 0.35, 0.8), rough=0.35, spec=0.6); mgia = m('giallo', (1.0, 0.78, 0.1), rough=0.4); mbuio = m('bocca', (0.02, 0.02, 0.03), rough=0.8)
box('MCorpo', (0, 0, 1.0), (1.7, 1.3, 1.8), mmet, parent=MACH)
cyl('MImbuto', 0.45, 0.6, (0, 0, 2.15), mgia, prc).parent = MACH
box('MBocca', (0, -0.62, 0.38), (0.9, 0.1, 0.6), mbuio, parent=MACH)
box('MScivolo', (0, -0.9, 0.12), (0.9, 0.6, 0.06), mgia, parent=MACH, rot=(-0.25, 0, 0))
CRANK = grp('Manovella'); CRANK.parent = MACH; CRANK.location = (-0.88, 0, 1.25)
box('ManAsse', (-0.12, 0, 0), (0.24, 0.07, 0.07), mgia, parent=CRANK); box('ManBraccio', (-0.24, 0, 0.2), (0.06, 0.06, 0.45), mgia, parent=CRANK); ball_('ManPomo', 0.08, (-0.24, 0, 0.42), m('pomo', (0.9, 0.1, 0.1)), prc, parent=CRANK)
for k, col in enumerate(((1, 0.2, 0.2), (0.2, 1, 0.3), (1, 0.9, 0.2))): ball_('Lucina', 0.07, (-0.45 + 0.45 * k, -0.66, 1.6), m('lucina%d' % k, col, emit=col, emit_strength=2.0), prc, parent=MACH)
txt('MScritta', 'CREA-PERSONAGGI', 0.17, m('scrittam', (1, 1, 1), rough=0.5), (0, -0.66, 1.2), ext=0.01, parent=MACH)
TOAST = grp('Tostapane')
cromo = m('cromo', (0.85, 0.12, 0.12), rough=0.3, spec=0.8)
box('TCorpo', (0, 0, 0.42), (0.62, 0.36, 0.4), cromo, parent=TOAST); box('TFessura', (0, 0, 0.63), (0.42, 0.08, 0.02), mbuio, parent=TOAST)
for s_ in (-1, 1):
    f_ = props014.bread(prc, T14, 'FettaT', toast=True); f_.parent = TOAST; f_.location = (s_ * 0.1, 0, 0.62); f_.scale = (0.3, 0.3, 0.3); f_.rotation_euler = (0, 0, PI / 2)
TLEGS = []
for s_ in (-1, 1):
    lg = grp('TGamba'); lg.parent = TOAST; lg.location = (s_ * 0.16, 0, 0.23); TLEGS.append(lg)
    box('TGambaS', (0, 0, -0.1), (0.04, 0.04, 0.2), mnero, parent=lg); box('TScarpa', (0, -0.04, -0.21), (0.1, 0.16, 0.05), m('scarpa', (0.9, 0.1, 0.1)), parent=lg)
CH = animali.crea('pulcino', prc); CHR = CH['root']; CHR.rotation_mode = 'XYZ'
BCH = grp('BaffiPulcino'); BCH.parent = CH['head']; BCH.location = (0, -0.21, -0.08)
for s_ in (-1, 1): ball_('BaffoP', 1.0, (s_ * 0.08, 0, 0), mnero, prc, parent=BCH, sc=(0.1, 0.03, 0.03)); ball_('RiccioloP', 1.0, (s_ * 0.17, 0, 0.03), mnero, prc, parent=BCH, sc=(0.035, 0.03, 0.035))
FEATH = []
fr_rnd = random.Random(20); mpiuma = m('piuma', (1.0, 0.85, 0.2), rough=0.8)
for k in range(16):
    o = ball_('Piuma', 1.0, (0, 0, -50), mpiuma, prc, sc=(0.05, 0.015, 0.12)); o.rotation_mode = 'XYZ'
    a = fr_rnd.uniform(0, 2 * PI); FEATH.append((o, Vector((math.cos(a) * fr_rnd.uniform(1, 2.6), -abs(math.sin(a)) * fr_rnd.uniform(0.5, 2.0), fr_rnd.uniform(3.0, 5.5))), fr_rnd.uniform(0, 6)))

# ======================= timbro RESPINTO =======================
GX = (0.95, -1.35)
STAMP = grp('Timbro'); mtimb = m('timbrorosso', (0.85, 0.04, 0.05), rough=0.5)
box('TBase', (0, 0, 0.3), (1.9, 1.4, 0.45), m('timbrolegno', (0.45, 0.25, 0.1), rough=0.6), parent=STAMP); box('TGomma', (0, 0, 0.05), (1.9, 1.4, 0.1), mtimb, parent=STAMP)
cyl('TManico', 0.22, 1.3, (0, 0, 1.15), m('manico', (0.7, 0.08, 0.08), rough=0.4), prc).parent = STAMP; ball_('TPomo', 0.4, (0, 0, 1.9), m('manico2', (0.7, 0.08, 0.08), rough=0.4), prc, parent=STAMP)
txt('TScritta', 'RESPINTO', 0.36, m('scrittabianca', (1, 1, 1), rough=0.5), (0, -0.72, 0.31), ext=0.02, parent=STAMP)
INK = txt('Inchiostro', 'RESPINTO', 0.42, mtimb, (GX[0], GX[1] - 0.1, 0.005), rot=(0, 0, 0), ext=0.002)

# ======================= parole, regole, timer, freccia =======================
WCOL = [(1.0, 0.25, 0.3), (0.2, 0.75, 1.0), (1.0, 0.8, 0.1), (0.55, 0.3, 1.0), (0.3, 0.9, 0.35)]
WORDS = [txt('Parola', w, 0.62 if k < 4 else 0.8, m('parola%d' % k, WCOL[k], rough=0.35, emit=WCOL[k], emit_strength=0.25), (0, 0, -50), ext=0.12) for k, w in enumerate(('NOME', 'ASPETTO', 'CARATTERE', 'POTERI', 'STORIA'))]
WPOS = [(-0.95, -1.5), (0.35, -1.6), (-0.2, -1.5), (0.55, -1.55), (0.85, -1.15)]                    # dove cadono (STORIA cade su Tumbo)
REG = txt('Regole', 'REGOLE', 1.0, m('regole', (1.0, 0.82, 0.1), rough=0.3, emit=(1.0, 0.7, 0.05), emit_strength=0.4), (0, -0.6, -50), ext=0.15)
BTN = grp('TastoSegui', (0.2, -1.1, 0))
box('TPiede', (0, 0, 0.2), (1.2, 0.8, 0.4), m('pied', (0.2, 0.2, 0.25), rough=0.4), parent=BTN)
BTOP = grp('TastoSu'); BTOP.parent = BTN; BTOP.location = (0, 0, 0.4)
box('TTasto', (0, 0, 0.18), (1.5, 0.95, 0.36), m('tasto', (0.95, 0.12, 0.25), rough=0.25, spec=0.8), parent=BTOP)
txt('TSegui', 'SEGUI', 0.34, m('bianco', (1, 1, 1), rough=0.4), (0, -0.49, 0.18), ext=0.02, parent=BTOP)
HAM = grp('Martello', (-1.15, -1.1, 0.88))                                                            # martello gigante: perno all'altezza delle mani di Pippo
box('MManico', (0, 0, 0.62), (0.1, 0.1, 1.25), m('legnochiaro', (0.75, 0.5, 0.25), rough=0.6), parent=HAM)
cyl('MTesta', 0.32, 0.95, (0, 0, 1.35), m('testam', (0.35, 0.35, 0.38), rough=0.3, metallic=0.8), prc, rot=(0, PI / 2, 0)).parent = HAM
HEART = bpy.data.objects.new('CuoreLike', cuore); prc.objects.link(HEART); HEART.rotation_mode = 'XYZ'
HEARTP = (0.25, -1.15)
BUB = grp('Nuvoletta', (0.25, -1.4, 0))
mbu = m('nuvoletta', (1, 1, 1), rough=0.4)
box('NCorpo', (0, 0, 1.0), (2.4, 0.35, 1.3), mbu, parent=BUB)
for s_ in (-1, 1):
    for z_ in (0.35, 1.65): cyl('NBordo', 0.18, 0.35, (s_ * 1.2, 0, z_), mbu, prc, rot=(PI / 2, 0, 0)).parent = BUB
box('NBordoL', (0, 0, 1.0), (2.75, 0.35, 0.95), mbu, parent=BUB); box('NBordoA', (0, 0, 1.0), (2.05, 0.35, 1.65), mbu, parent=BUB)
box('NCoda', (-0.75, 0, 0.18), (0.4, 0.3, 0.4), mbu, parent=BUB, rot=(0, 0.75, 0))
DOTS = []
for k in range(3): DOTS.append(ball_('Puntino', 0.15, (-0.5 + 0.5 * k, -0.2, 1.0), m('puntino', (0.25, 0.25, 0.3), rough=0.5), prc, parent=BUB))
BHEART = bpy.data.objects.new('NCuore', cuore); prc.objects.link(BHEART); BHEART.parent = BUB; BHEART.location = (-0.6, -0.2, 0.95); BHEART.scale = (0.32,) * 3
BCNT = txt('NContatore', '9999', 0.5, m('contatore', (0.9, 0.1, 0.2), rough=0.4), (0.35, -0.2, 0.98), ext=0.03, parent=BUB)
mled = m('led', (1.0, 0.1, 0.08), rough=0.4, emit=(1.0, 0.08, 0.05), emit_strength=3.5)
TIMERS = [txt('Timer', s_, 0.95, mled, (0, 1.6, 3.6), ext=0.05) for s_ in ('48:00:00', '47:59:59', '47:59:58', '47:59:57', '47:59:56')]
box('TimerFondo', (0, 1.75, 3.6), (5.3, 0.1, 1.3), m('timerfondo', (0.03, 0.03, 0.04), rough=0.4), coll=prc).name = 'TimerFondo'
TFONDO = bpy.data.objects['TimerFondo']
ARROW = grp('Freccia', (1.15, -1.5, 0)); mfr = m('freccia', (0.85, 0.03, 0.03), rough=0.3, spec=0.7)
box('FAsta', (0, 0, 1.55), (0.42, 0.25, 1.3), mfr, parent=ARROW)
bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=0.62, radius2=0.0, depth=0.75, location=(0, 0, 0.55), rotation=(PI, 0, PI / 4))
ARR = bpy.context.active_object; ARR.name = 'FPunta'; ARR.data.materials.append(mfr); ARR.scale = (1, 0.4, 1)
for c in ARR.users_collection: c.objects.unlink(ARR)
prc.objects.link(ARR); ARR.parent = ARROW
BUSH = A.albero_cartonato('shrub_02', posizione=(-3.05, -1.75, 0), altezza=1.55, collezione=envc)
kitlook.tune_cutouts(1.9)

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
show_only(PHONE, [(T_GCOMM - 0.1, T_NO)]); show_only(CART, [(T_GUAL, T_STAMP + 0.05)])
show_only(BAFFI, [(T_GUAL, TOTAL)])
show_only(BHEART, [(T_PIU - 0.1, T_GCOMM)]); show_only(BCNT, [(T_PIU - 0.1, T_GCOMM)])
for d_ in DOTS: show_only(d_, [(T_COMM, T_PIU - 0.1)])
show(GU['root'], [(T_GUAL - 0.1, T_QUINDI - 0.05), (T_GCOMM - 0.15, T_NO)])
show(MACH, [(T_MACH - 0.05, T_BOOM + 0.04)]); show(TOAST, [(T_DING - 0.05, T_RUN + 0.05)]); show(CHR, [(T_CHICK - 0.05, T_BOOM + 0.04)])
show(STAMP, [(T_STAMP - 0.4, T_STAMP + 1.0)]); show(INK, [(T_STAMP + 0.6, T_QUINDI - 0.05)])
for k, w in enumerate(WORDS): show(w, [(T_W[k] - 0.3, T_W[k + 1] - 0.02 if k < 4 else T_REGOLE - 0.05)])
show(REG, [(T_REGOLE - 0.2, T_SEGUI - 0.05)]); show(BTN, [(T_SEGUI - 0.1, T_LIKE - 0.05)]); show(HAM, [(T_SEGUI - 0.1, T_LIKE - 0.05)])
show(HEART, [(T_LIKE - 0.1, T_LIKE + 0.62)]); show(BUB, [(T_COMM, T_UFF - 0.05)])
for k, o in enumerate(TIMERS): show(o, [(T_48 + 0.85 * k if k else T_48 - 0.1, (T_48 + 0.85 * (k + 1)) if k < 4 else T_GCOMM)])
show(TFONDO, [(T_48 - 0.1, T_GCOMM)])
show(PIED, [(T_UFF - 0.05, T_GCOMM)]); BUSH.hide_render = True; show(CROWN, [(T_UFF + 0.2, T_GCOMM)]); show(ARROW, [(T_COMMENTA - 0.15, TOTAL)])
for o, *_ in FEATH: show(o, [(T_BOOM, T_GUAL)])
show(QM, [(0.0, T_MACH), (T_QUINDI, T_VOI)])

# ======================= pose =======================
PC = (MX - 1.45, MY - 0.15)                    # Pippo alla manovella
PF = (-0.5, -1.75); TF = (0.45, -1.9)           # finale, davanti alla camera
P_HAM = (-1.75, -1.0); TJ0 = (-1.15, -1.4)
def pp(t):
    """Pippo: posizione, direzione, braccia (None = quelle dell'emozione), anche, scala-allungamento"""
    S = dict(loc=(P0[0], P0[1], 0.0), yaw=0.25, aL=None, aR=None, hL=0.0, hR=0.0)
    if t < T_MACH - 0.1:                                                                          # hook: guarda il posto vuoto
        S['yaw'] = 0.25 - 0.7 * ramp(t, T_MANCA, T_MANCA + 0.3)
    elif t < T_BOOM + 0.6:                                                                        # alla manovella / calcio / esplosione
        y = yaw_to(PC, (MX, MY)); S.update(loc=(PC[0], PC[1], 0.0), yaw=y)
        if T_BRAVO - 0.1 <= t < T_KICK - 0.1: S['yaw'] = y * (1 - ramp(t, T_BRAVO - 0.1, T_BRAVO + 0.1))      # «Bravo, cicciomerda»: si gira verso la camera, avvilito
        if t < T_DING:
            a = (t - T_MACH) * 9.0; S.update(aR=(0.2 + 0.35 * math.cos(a), -0.9, 0.35 * math.sin(a)), aL=(-0.25, -0.6, 0.3))
        elif T_KICK <= t < T_KICK + 0.7:
            u = math.sin(PI * ramp(t, T_KICK, T_KICK + 0.6)); S.update(hR=-1.2 * u, aL=(-0.7, 0.2, 0.4), aR=(0.7, 0.2, 0.4))
        elif t >= T_BOOM:
            S.update(loc=(PC[0] - 0.7 * ramp(t, T_BOOM, T_BOOM + 0.3), PC[1] - 0.3 * ramp(t, T_BOOM, T_BOOM + 0.3), 0.5 * math.sin(PI * ramp(t, T_BOOM, T_BOOM + 0.35))), yaw=y - 0.5)
    elif t < T_VOI - 0.15:                                                                        # guarda Gualtiero, poi la cassa
        S['yaw'] = yaw_to(P0, GX) if t < T_QUINDI else yaw_to(P0, (XS, YS))
    elif t < T_W[0] - 0.1:                                                                        # LO CREATE VOI: si gira e punta il dito verso la camera
        u = ramp(t, T_VOI - 0.15, T_VOI + 0.1); S.update(yaw=yaw_to(P0, (XS, YS)) * (1 - u) + 0.0 * u, aR=(0.15, -1.0, 0.25 + 0.05 * math.sin(t * 20)) if u > 0.4 else None)
    elif t < T_REGOLE - 0.1:                                                                      # le parole che cadono
        S['yaw'] = 0.2 + 0.3 * math.sin(t * 2.0)
    elif t < T_LIKE - 0.05:                                                                       # REGOLE / martello
        y = yaw_to(P_HAM, (0.2, -1.1)); hit = ramp(t, T_SEGUI + 0.05, T_SEGUI + 0.3)
        S.update(loc=(P_HAM[0], P_HAM[1], 0), yaw=y, aL=lerp((-0.1, -0.5, 0.9), (-0.05, -1.0, 0.0), hit), aR=lerp((0.1, -0.5, 0.9), (0.05, -1.0, 0.0), hit))
    elif t < T_48 - 0.1:                                                                          # like e commenti: fa il tifo
        k = math.sin(t * 14); S.update(loc=(P_HAM[0] - 0.3, P_HAM[1] + 0.2, 0.08 * abs(k)), yaw=0.35, aL=(-0.5, -0.2, 0.9), aR=(0.5, -0.2, 0.9))
    elif t < T_GCOMM - 0.15:                                                                      # timer e cassa ufficiale: guarda in alto
        S.update(loc=(-1.6, -0.6, 0), yaw=yaw_to((-1.6, -0.6), (XS, YS)) if t > T_UFF else 0.3)
    elif t < T_NO - 0.1:
        S.update(loc=(-1.4, 0.5, 0), yaw=yaw_to((-1.4, 0.5), (-3.05, -1.75)))
    else:                                                                                         # NO! COMMENTA ADESSO
        k = 0.06 * math.sin(t * 28); S.update(loc=(PF[0], PF[1], 0.0), yaw=0.08)
        if t >= T_MUOVI - 0.05: S.update(aR=(0.12, -1.0, 0.3 + k), aL=(-0.45, -0.2, 0.85))
    return S

def tb(t):
    """Tumbo: posizione, yaw, scala (x, y, z), zampe davanti 0..1"""
    S = dict(loc=(T0[0], T0[1], 0.0), yaw=0.35, sc=(1, 1, 1), up=0.0)
    if t < T_MACH - 0.1: S['yaw'] = 0.35 - 0.9 * ramp(t, T_MANCA, T_MANCA + 0.3)
    elif t < T_BOOM + 0.5:
        S.update(loc=(MX - 0.9, MY - 1.25, 0.0), yaw=yaw_to((MX - 0.9, MY - 1.25), (MX, MY - 1.2)))
        if t >= T_DING: S['yaw'] = yaw_to((MX - 0.9, MY - 1.25), (4.5, -2.5)) if t < T_RUN else S['yaw']
        if t >= T_BOOM: u = ramp(t, T_BOOM, T_BOOM + 0.35); S.update(loc=(MX - 0.9 - 1.2 * u, MY - 1.25 - 0.4 * u, 0.7 * math.sin(PI * u)))
    elif t < T_W[0] - 0.1: S['yaw'] = yaw_to(T0, GX) if t < T_QUINDI else yaw_to(T0, (XS, YS))
    elif t < T_REGOLE - 0.1:                                                                      # STORIA gli cade addosso
        sq = ramp(t, T_W[4] + 0.12, T_W[4] + 0.18) * (1 - ramp(t, T_TESTA + 0.4, T_TESTA + 0.7))
        S.update(loc=(WPOS[4][0], WPOS[4][1], 0), yaw=0.0, sc=(1 + 0.6 * sq, 1 + 0.4 * sq, 1 - 0.82 * sq))
    elif t < T_LIKE - 0.1: S.update(loc=(TJ0[0], TJ0[1], 0), yaw=yaw_to(TJ0, (0.2, -1.1)))
    elif t < T_48 - 0.1:                                                                          # salta sul cuore del like
        u = ramp(t, T_LIKE, T_LIKE + 0.35); v = ramp(t, T_LIKE + 0.62, T_LIKE + 0.95)
        p = lerp(TJ0, HEARTP, u); p = lerp(p, (HEARTP[0] + 0.9, HEARTP[1] - 0.2), v)
        z = 1.25 * math.sin(PI * u * 0.5) * (1 - v) + 0.55 * math.sin(PI * v)
        if t > T_LIKE + 0.95: z = 0.12 * abs(math.sin(t * 12))
        S.update(loc=(p[0], p[1], z), yaw=yaw_to(TJ0, HEARTP) if v < 0.1 else 0.3)
    elif t < T_GCOMM - 0.15: S.update(loc=(-0.6, -0.9, 0), yaw=yaw_to((-0.6, -0.9), (XS, YS)) if t > T_UFF else 0.0, up=0.6 if t > T_UFF + 0.4 else 0.0)
    elif t < T_NO - 0.1: S.update(loc=(-0.9, 0.4, 0), yaw=yaw_to((-0.9, 0.4), (-3.05, -1.75)))
    else:
        S.update(loc=(TF[0], TF[1], 0.18 * abs(math.sin(t * 10))), yaw=-0.1, up=1.0)
    return S

def gp(t):
    """Gualtiero: posizione, yaw, scala z"""
    if t < T_GCOMM - 0.2:
        u = ramp(t, T_GUAL, T_GUAL + 1.6); x = 5.6 + (GX[0] - 5.6) * u
        tip = 0.05 * abs(math.sin(t * 10)) * (1 - ramp(t, T_GUAL + 1.5, T_GUAL + 1.7))
        flat = ramp(t, T_STAMP - 0.02, T_STAMP + 0.04)
        return (x, GX[1], tip * (1 - flat)), yaw_to((5.6, GX[1]), GX) * (1 - ramp(t, T_GUAL + 1.4, T_GUAL + 1.8)), 1 - 0.8 * flat
    return (-3.05, -1.45, 0.0), 0.35, 1.0

# ======================= chiavi =======================
def K(o, f, loc=None, rot=None, scale=None):
    if loc is not None: o.location = loc; o.keyframe_insert('location', frame=f)
    if rot is not None: o.rotation_euler = rot; o.keyframe_insert('rotation_euler', frame=f)
    if scale is not None: o.scale = scale if isinstance(scale, (tuple, list)) else (scale,) * 3; o.keyframe_insert('scale', frame=f)

# emozioni esagerate di Pippo (solo quelle di pippo2.EMOZIONI_FORTI)
EMO = [(0.0, 'sorpreso'), (T_PIPPO, 'felice'), (T_AEREO, 'sorpreso'), (T_MANCA, 'triste'), (T_MACH, 'furbo'), (T_DING, 'felice'), (T_DING + 1.0, 'sorpreso'), (T_BRAVO, 'triste'), (T_KICK, 'arrabbiato'), (T_CHICK + 0.1, 'felice'),
       (T_CAZ, 'spaventato'), (T_BOOM + 0.1, 'spaventato'), (T_GUAL + 0.4, 'arrabbiato'), (T_STAMP + 0.05, 'ride'), (T_QUINDI, 'furbo'), (T_VOI - 0.1, 'felice'),
       (T_W[0], 'sorpreso'), (T_W[4] + 0.15, 'spaventato'), (T_TESTA, 'ride'), (T_REGOLE, 'furbo'), (T_SEGUI + 0.3, 'felice'), (T_LIKE + 0.65, 'ride'), (T_COMM + 0.7, 'sorpreso'),
       (T_48, 'normale'), (T_UFF, 'felice'), (T_GCOMM, 'arrabbiato'), (T_G2 + 0.2, 'spaventato'), (T_NO, 'arrabbiato'), (T_MUOVI, 'arrabbiato'), (T_ADESSO, 'arrabbiato')]
def emo_at(t):
    e = EMO[0][1]
    for (t_, n_) in EMO:
        if t_ <= t: e = n_
    return e
for i, (t_, n_) in enumerate(EMO):
    if i: pippo.emozione(P, fr(t_ - 0.08), EMO[i - 1][1])
    pippo.emozione(P, fr(t_), n_)
REAZ = [(0.05, 0.14), (T_MANCA, -0.1), (T_DING + 0.05, 0.14), (T_BOOM, 0.2), (T_STAMP + 0.05, 0.12), (T_VOI, 0.18), (T_W[4] + 0.15, -0.14), (T_SEGUI + 0.3, 0.14), (T_UFF, 0.14), (T_G2 + 0.2, -0.12), (T_NO, 0.2), (T_ADESSO, 0.18)]

for f in range(1, NF + 1):
    t = (f - 1) / FPS
    s = pp(t); sq = sum(a_ * math.sin(PI * min(1.0, (t - e_) / 0.3) * 1.5) * math.exp(-(t - e_) * 4.0) for (e_, a_) in REAZ if 0.0 <= t - e_ < 0.9)
    K(P['root'], f, s['loc'], (0, 0, s['yaw']), (1 - 0.5 * sq, 1 - 0.5 * sq, 1 + sq))
    eb = pippo.EMOZIONI_FORTI[emo_at(t)]['braccia']
    for nm, k, d in (('L', 'aL', eb[0]), ('R', 'aR', eb[1])):
        sh = P['shoulder' + nm]; sh.rotation_quaternion = qdir(s[k] if s[k] is not None else d); sh.keyframe_insert('rotation_quaternion', frame=f)
        K(P['hip' + nm], f, rot=(s['h' + nm], 0, 0))
    b = tb(t); K(Tb['root'], f, b['loc'], (-0.5 * b['up'], 0, b['yaw']), tuple(0.75 * v for v in b['sc']))
    K(Tb['tail'], f, rot=(-1.0 + 0.3 * math.sin(t * 9), 0, 0.7 * math.sin(t * 15)))
    for nm, sg in (('L', 1), ('R', -1)): K(Tb['legF' + nm], f, rot=(b['up'] * (-1.2 + 0.35 * sg * math.sin(t * 14)), 0, 0))
    g, gy, gz = gp(t); K(GU['root'], f, g, (0, 0, gy), (1 + 0.5 * (1 - gz), 1 + 0.5 * (1 - gz), gz))
    if t < T_GCOMM - 0.2:
        K(GU['shoulderR'], f, rot=(-0.4, 0, 0.3)); K(GU['shoulderL'], f, rot=(0.3 * math.sin(t * 10), 0, -0.1)); K(GU['head'], f, rot=(0, 0, 0.15 * math.sin(t * 3)))
    else:
        tap = 0.15 * math.sin(t * 30) if t < T_G2 else 0.0
        K(GU['shoulderR'], f, rot=(-1.25 + tap, 0, 0.45)); K(GU['shoulderL'], f, rot=(-1.15, 0, -0.5)); K(GU['head'], f, rot=(0.35, 0, 0.0))
    # telefono davanti alle mani di Gualtiero
    K(PHONE, f, (-3.0, -2.05, 1.3), (0.35, 0, 0.35))
    # sipario
    o_ = ramp(t, 0.15, 0.75); K(SIPL, f, loc=(-4.4 * o_, 0, 0)); K(SIPR, f, loc=(4.4 * o_, 0, 0))
    # occhi di bue: si accendono uno alla volta; nel finale «ufficiale» resta solo quello della cassa
    for i, (sp_, cn_) in enumerate(zip(SPOTS, CONES)):
        on = 1.0 if t >= (0.35, 0.55, T_SPOT3)[i] else 0.0
        if T_UFF <= t < T_GCOMM: on = 0.25 if i < 2 else 2.0
        sp_.data.energy = 650.0 * on; sp_.data.keyframe_insert('energy', frame=f); K(cn_, f, scale=(1, 1, 1) if on > 0 else (0.001,) * 3)
    # cassa: coperchio che respira, occhi che sbattono, coda che dondola; nel finale sale sul piedistallo
    lift = ramp(t, T_UFF, T_UFF + 0.5) if t < T_GCOMM else 0.0
    peek = 0.18 + 0.08 * math.sin(t * 2.3) + 0.25 * ramp(t, T_QUINDI, T_VOI - 0.2) * (1 - ramp(t, T_VOI, T_VOI + 0.3)) + 0.35 * lift
    K(CASSA, f, loc=(XS, YS, 1.0 * lift + 0.06 * abs(math.sin(t * 6)) * (1 if (T_MANCA < t < T_MANCA + 1.0) else 0)))
    K(LID, f, rot=(0, -peek - 0.2 * max(0.0, math.sin(t * 17)) * (1 if T_MANCA < t < T_MANCA + 0.6 else 0), 0))
    blink = 0.08 if (t % 2.7) < 0.12 else 1.0
    for e_ in EYES: K(e_, f, scale=(0.09, 0.036, 0.063 * blink * (1.5 if T_UFF < t < T_GCOMM else 1.0)))
    for k_, tb_ in enumerate(TAIL):
        u_ = k_ / 8.0; x_ = w_ / 2 + 0.05 + 0.65 * u_; z_ = 0.55 + 0.9 * math.sin(u_ * 2.6) + 0.12 * math.sin(t * 5 + k_ * 0.7) * u_
        K(tb_, f, loc=(x_ + 0.08 * math.sin(t * 4 + k_) * u_, 0.2, z_))
    K(PIED, f, loc=(XS, YS, 0.5 * lift if lift > 0 else -0.6), scale=(1, 1, max(0.001, lift)))
    cr = ramp(t, T_UFF + 0.25, T_UFF + 0.7); K(CROWN, f, loc=(XS - 0.15, YS, 1.0 + h_ + 0.25 + 4.0 * (1 - cr) + 0.1 * math.sin(t * 3)), rot=(0, 0.12, t * 0.8))
    K(QM, f, loc=(XS + 0.15, 0.1, 3.1 + 0.12 * math.sin(t * 3)), rot=(PI / 2, 0, 0.25 * math.sin(t * 2)))
    # macchina: cade dall'alto, trema quando la manovella gira e quando prende il calcio
    mz = fall(t, T_MACH - 0.35, T_MACH, 7.0, 0.0); shake = (0.04 * math.sin(t * 50) if T_MACH < t < T_DING else 0.0) + (0.08 * math.sin(t * 60) * (1 - ramp(t, T_KICK + 0.3, T_KICK + 0.9)) if t > T_KICK + 0.25 else 0.0)
    msq = 0.25 * math.exp(-(t - T_MACH) * 8) * math.sin((t - T_MACH) * 30) if t >= T_MACH else 0.0
    K(MACH, f, loc=(MX + shake, MY, mz), scale=(1 + msq * 0.5, 1 + msq * 0.5, 1 - msq))
    K(CRANK, f, rot=((t - T_MACH) * 9.0 if T_MACH < t < T_DING else 0.0, 0, 0))
    # tostapane con le gambe: esce dallo scivolo e scappa via
    if t < T_DING + 0.35: tp = (MX, MY - 0.75, 0.0); ty = 0.0
    else:
        u = ramp(t, T_DING + 0.35, T_RUN); tp = lerp((MX, MY - 0.95, 0.0), (5.0, -2.6, 0.0), u); ty = yaw_to((MX, MY - 0.95), (5.0, -2.6))
    pop_ = math.sin(PI * ramp(t, T_DING - 0.05, T_DING + 0.35)) * 0.5
    K(TOAST, f, loc=(tp[0], tp[1], tp[2] + pop_ + 0.04 * abs(math.sin(t * 22))), rot=(0, 0.1 * math.sin(t * 22), ty))
    for k_, lg in enumerate(TLEGS): K(lg, f, rot=(0.8 * math.sin(t * 22 + PI * k_), 0, 0))
    # pulcino con i baffi: esce, guarda in camera, si gonfia ed esplode
    cu = ramp(t, T_CHICK - 0.05, T_CHICK + 0.3); swell = ramp(t, T_CAZ, T_BOOM)
    K(CHR, f, loc=(MX + 0.05, MY - 1.3 * cu, 0.3 * math.sin(PI * cu) + 0.03 * swell * math.sin(t * 70)), rot=(0, 0, 0.0), scale=(1.0 + 1.1 * swell,) * 3)
    for (o, v, ph) in FEATH:
        d = t - T_BOOM
        if d < 0: K(o, f, loc=(MX, MY - 1.3, -50))
        else:
            dd = min(d, 1.6); p0 = Vector((MX, MY - 1.3, 0.7)); vv = v * (1 - math.exp(-dd * 3)) / 3 * 2.2
            K(o, f, loc=(p0.x + vv.x + 0.15 * math.sin(d * 5 + ph), p0.y + vv.y, max(0.02, p0.z + vv.z - 1.1 * d * d)), rot=(math.sin(d * 4 + ph), d * 3 + ph, math.cos(d * 3 + ph)))
    # timbro RESPINTO: cade su Gualtiero, resta un attimo, risale
    sz = fall(t, T_STAMP - 0.3, T_STAMP, 7.0, 0.4) if t < T_STAMP + 0.55 else 0.4 + 7.0 * ramp(t, T_STAMP + 0.55, T_STAMP + 0.95)
    K(STAMP, f, loc=(GX[0], GX[1], sz))
    # parole che cadono
    for k_, w in enumerate(WORDS):
        x_, y_ = WPOS[k_]; zz = fall(t, T_W[k_] - 0.25, T_W[k_] + 0.08, 6.0, 0.55 if k_ < 4 else 0.45)
        if k_ == 4 and t > T_TESTA + 0.35: zz = 0.45 + 2.0 * ramp(t, T_TESTA + 0.35, T_TESTA + 0.8); x_ += 1.6 * ramp(t, T_TESTA + 0.35, T_TESTA + 0.8)
        K(w, f, loc=(x_, y_, zz), rot=(PI / 2, 0, 0.12 * (1 if k_ % 2 else -1)))
    K(REG, f, loc=(0.0, -0.9, fall(t, T_REGOLE - 0.2, T_REGOLE + 0.05, 7.0, 2.55)), scale=1.0 + 0.25 * math.exp(-max(0.0, t - T_REGOLE - 0.05) * 10))
    # tasto SEGUI e martello
    hit = ramp(t, T_SEGUI + 0.05, T_SEGUI + 0.3)
    K(HAM, f, rot=(0, 1.72 * hit - 0.25 * (1 - hit), 0))
    K(BTOP, f, scale=(1, 1, 1 - 0.45 * ramp(t, T_SEGUI + 0.26, T_SEGUI + 0.31)))
    # cuore del like: Tumbo ci salta sopra, si schiaccia e scoppia
    hs = 1.0 - 0.35 * ramp(t, T_LIKE + 0.33, T_LIKE + 0.4) + 0.6 * ramp(t, T_LIKE + 0.45, T_LIKE + 0.55)
    K(HEART, f, loc=(HEARTP[0], HEARTP[1], 0.48 * hs), rot=(0, 0, 0.1 * math.sin(t * 4)), scale=(0.75 * hs, 0.75 * (2 - hs if hs < 1 else 1), 0.75 * hs))
    # nuvoletta dei commenti: cade dal cielo
    bz = fall(t, T_COMM + 0.25, T_COMM + 0.7, 8.0, 0.0); bsq = 0.2 * math.exp(-max(0.0, t - T_COMM - 0.7) * 8) * math.sin(max(0.0, t - T_COMM - 0.7) * 30)
    K(BUB, f, loc=(0.25, -1.4, bz) if t < T_48 - 0.1 else (0.2, -2.6, 0.0), scale=(1 + bsq * 0.5, 1, 1 - bsq), rot=(0, 0, 0.0 if t < T_48 - 0.1 else -0.25))
    for k_, d_ in enumerate(DOTS): K(d_, f, scale=(0.15 * (1 + 0.4 * max(0.0, math.sin(t * 9 - k_ * 1.2))),) * 3)
    K(BHEART, f, scale=(0.32 * (1 + 0.15 * abs(math.sin(t * 8))),) * 3)
    # timer: pulsa ogni secondo
    for o in TIMERS: K(o, f, scale=1.0 + 0.08 * math.exp(-((t - T_48) % 0.85) * 9))
    # freccia finale: rimbalza verso il basso
    K(ARROW, f, loc=(1.15, -1.5, 0.2 * abs(math.sin(t * 9)) + 4.0 * (1 - ramp(t, T_COMMENTA - 0.15, T_COMMENTA + 0.1))))

# espressioni di Tumbo e Gualtiero
def tex(t, **k): tumbo.tumbo_express(Tb, fr(t), **k)
for (t_, k) in ((0.0, dict(tongue=0.8, eye_scale=1.1)), (T_MANCA, dict(tongue=0.0, brow=-0.6, look=(0.7, 0))), (T_DING, dict(tongue=1.0, eye_scale=1.2)), (T_BOOM, dict(brow=-0.8, eye_scale=1.3)),
                (T_STAMP, dict(tongue=1.0, eye_scale=1.1)), (T_VOI, dict(tongue=1.0, eye_scale=1.25, brow=0.4)), (T_W[4] + 0.15, dict(brow=-1.0, eye_open=0.2)), (T_TESTA + 0.6, dict(tongue=1.0, eye_scale=1.2)),
                (T_UFF, dict(tongue=0.8, eye_scale=1.3, look=(0.5, 0.5))), (T_GCOMM, dict(brow=0.9, tongue=0.0)), (T_NO, dict(brow=1.0, tongue=0.0, eye_scale=1.2))):
    tex(t_, **k)
def gx(t, **k): props009.gex(GU, fr(t), **k)
for (t_, k) in ((0.0, dict(brow=0.6, mouth=0.1)), (T_BAFFI, dict(brow=0.9, mouth=0.4)), (T_STAMP + 0.05, dict(brow=-0.9, mouth=0.9)), (T_GCOMM, dict(brow=1.0, mouth=0.5, look=(0.3, -0.6))), (T_G2, dict(brow=1.0, mouth=0.8)), (T_PEZZO, dict(brow=1.0, mouth=0.25, look=(0.0, -0.2))), (T_PEZZO + 0.5, dict(brow=1.0, mouth=0.9))):
    gx(t_, **k)

# ======================= effetti =======================
def fx(name, pos, w, t0, dur, **k): return A.effetto(name, posizione=pos, larghezza=w, animazione=(fr(t0), int(dur * FPS)), collezione=prc, **k)
fx('sbuffo_bianco/whitepuff03', (MX, MY - 0.6, 0.3), 2.6, T_MACH, 0.5, opacita=0.8)                 # la macchina atterra
fx('particelle/star_04', (MX, MY - 1.2, 0.8), 0.9, T_DING, 0.4, luce=2.0, colore=(1, 0.9, 0.3))      # ding
fx('emoticon/exclamation', (PC[0], PC[1], 2.45), 0.45, T_DING + 0.1, 0.8)
fx('lampo/flash02', (MX, MY - 1.3, 0.9), 4.5, T_BOOM - 0.02, 0.25, luce=3.0)                         # esplosione del pulcino
fx('esplosione/explosion03', (MX, MY - 1.3, 1.0), 4.2, T_BOOM, 0.75, luce=1.6)
fx('esplosione/explosion05', (MX + 0.6, MY - 1.0, 1.6), 3.0, T_BOOM + 0.08, 0.7, luce=1.4)
for k in range(3): fx('fumo_nero/blacksmoke%02d' % (k * 5), (MX - 0.6 + 0.6 * k, MY - 1.1, 1.0 + 0.5 * k), 2.6, T_BOOM + 0.2 + 0.1 * k, 1.2, opacita=0.85)
fx('fumo_nero/blacksmoke10', (PC[0] - 0.7, PC[1] - 0.3, 1.7), 1.4, T_BOOM + 0.3, 1.0, opacita=0.8)
fx('sbuffo_bianco/whitepuff06', (GX[0], GX[1], 0.4), 3.2, T_STAMP, 0.6, opacita=0.9)                 # timbro
fx('emoticon/stars', (GX[0] + 0.2, GX[1], 0.9), 0.7, T_STAMP + 0.6, 0.6)
for k in range(5): fx('particelle/star_0%d' % (k + 1), (XS - 0.9 + 0.45 * k, YS - 1.0, 2.6 + 0.3 * (k % 2)), 0.8, T_VOI + 0.04 * k, 0.9, luce=2.2, colore=WCOL[k])   # LO CREATE VOI
for k in range(6): fx('particelle/magic_0%d' % (k % 5 + 1), (-3.0 + 1.2 * k, -0.8, 3.2 + 0.5 * (k % 2)), 1.2, T_VOI + 0.05 * k, 1.0, luce=2.0, colore=WCOL[k % 5])
for k_ in range(5): fx('sbuffo_bianco/whitepuff%02d' % (k_ * 2), (WPOS[k_][0], WPOS[k_][1], 0.25), 1.6, T_W[k_] + 0.08, 0.45, opacita=0.8)
fx('sbuffo_bianco/whitepuff04', (0.0, -0.9, 2.5), 3.0, T_REGOLE + 0.05, 0.5, opacita=0.6)
fx('lampo/flash05', (0.2, -1.6, 0.9), 1.1, T_SEGUI + 0.3, 0.15, luce=1.6); fx('emoticon/stars', (0.2, -1.4, 1.3), 0.9, T_SEGUI + 0.32, 0.7)
for k in range(5): fx('emoticon/heart', (HEARTP[0] - 0.8 + 0.4 * k, HEARTP[1] - 0.3, 0.8 + 0.35 * (k % 3)), 0.55, T_LIKE + 0.5 + 0.03 * k, 0.8)
fx('sbuffo_bianco/whitepuff08', (0.25, -1.4, 0.2), 3.6, T_COMM + 0.7, 0.55, opacita=0.85)
for k in range(8): fx('particelle/star_0%d' % (k % 8 + 1), (XS - 1.2 + 0.35 * k, YS - 0.9, 2.2 + 0.6 * math.sin(k)), 0.7, T_UFF + 0.3 + 0.05 * k, 1.4, luce=2.4, colore=WCOL[k % 5])
fx('luci/circle_a_streaks', (XS, YS + 0.3, 2.2), 4.2, T_UFF + 0.2, 1.7, colore=(1.0, 0.8, 0.3), luce=1.4, opacita=0.7) if 'luci/circle_a_streaks' else None
fx('emoticon/anger', (-3.05, -1.45, 2.35), 0.45, T_G2 + 0.15, 0.8)
fx('emoticon/exclamations', (PF[0], PF[1], 2.5), 0.55, T_NO, 0.7); fx('emoticon/anger', (PF[0] + 0.35, PF[1], 2.3), 0.4, T_ADESSO, 0.9)

fx('emoticon/swirl', (P0[0], P0[1], 2.35), 0.5, T_AEREO, 1.0); fx('emoticon/sleep', (P0[0] + 0.3, P0[1], 2.6), 0.35, T_AEREO + 0.3, 0.8)
fx('emoticon/dots3', (PC[0], PC[1], 2.35), 0.45, T_BRAVO + 0.3, 0.9)

# ======================= il pubblico: un branco di scimmie col telefono =======================
AUD = grp('Pubblico', coll=envc); SEAT = m('poltrona', (0.55, 0.04, 0.06), rough=0.7); TELM = m('telpubblico', (0.6, 0.8, 1.0), emit=(0.6, 0.8, 1.0), emit_strength=2.5)
_ar = random.Random(7)
for r_, y_ in enumerate((-6.0, -7.1, -8.2)):
    for c_ in range(6):
        x_ = -2.9 + c_ * 1.16 + (0.3 if r_ % 2 else 0.0); z_ = 0.35 * r_
        box('Poltrona', (x_, y_ - 0.25, z_ + 0.25), (0.95, 0.7, 0.5), SEAT, parent=AUD, coll=envc); box('Schienale', (x_, y_ - 0.6, z_ + 0.75), (0.95, 0.15, 0.9), SEAT, parent=AUD, coll=envc)
        if r_: box('Gradino', (x_, y_ - 0.2, z_ / 2), (1.16, 1.1, z_), m('gradino', (0.08, 0.06, 0.06), rough=0.8), parent=AUD, coll=envc)
        A_ = animali.crea('scimmia', chc); rt = A_['root']; rt.parent = AUD; rt.location = (x_, y_ - 0.2, z_ + 0.5); rt.rotation_euler = (0, 0, PI + _ar.uniform(-0.3, 0.3))
        box('TelScimmia', (x_ + 0.02, y_ + 0.12, z_ + 0.95), (0.14, 0.02, 0.24), TELM, parent=AUD, coll=envc)
la_ = bpy.data.lights.new('LucePubblico', 'AREA'); la_.size = 6.0; la_.energy = 600; la_.color = (1.0, 0.85, 0.7); la_.use_shadow = False
LAUD = bpy.data.objects.new('LucePubblico', la_); envc.objects.link(LAUD); LAUD.location = (0.0, -4.0, 4.5); luci.punta(LAUD, (0.0, -7.0, 0.8))
show(AUD, [(T_SCIMMIE - 0.1, T_W[0]), (T_TESTA - 0.1, T_REGOLE)]); show(LAUD, [(T_SCIMMIE - 0.1, T_W[0]), (T_TESTA - 0.1, T_REGOLE)])
for k in range(6): fx('emoticon/' + ('swirl', 'question', 'dots3', 'sleep', 'question', 'swirl')[k], (-2.3 + 0.95 * k, -6.8 + 0.4 * (k % 2), 2.15 + 0.3 * (k % 3)), 0.5, T_TESTA + 0.2 + 0.12 * k, 1.4)

# ======================= camera =======================
WIDE = ((0.0, -9.6, 2.0), (0.0, -9.0, 1.95), (0.0, 0.4, 2.2), (0.0, 0.4, 2.15), 24, 9)
SHOTS = [  # t0, t1, camera da, a, mira da, a, lente, diaframma
    (0.0, T_PIPPO - 0.05, (0.0, -8.0, 1.8), (0.0, -7.4, 1.75), (0.0, 0.4, 1.8), (0.0, 0.4, 1.7), 22, 10),                   # 01 sipario e squadra
    (T_PIPPO - 0.05, T_SPOT3 - 0.05, (P0[0] + 0.15, -3.0, 1.75), (P0[0] + 0.12, -2.2, 1.72), (P0[0], P0[1], 1.55), (P0[0], P0[1], 1.62), 34, 3),   # 01b «quel coglione a pedali»: primo piano di Pippo
    (T_SPOT3 - 0.05, T_MANCA, (0.0, -7.6, 1.8), (0.0, -7.2, 1.75), (0.0, 0.4, 1.7), (0.0, 0.4, 1.7), 22, 10),                # 01c si accende il terzo occhio di bue
    (T_MANCA, T_MACH - 0.1, (XS - 0.5, -4.4, 2.3), (XS - 0.4, -3.8, 2.25), (XS, YS, 1.35), (XS, YS, 1.4), 28, 5),               # 02 manca qualcuno: zoom sulla cassa
    (T_MACH - 0.1, T_DING, (MX - 1.2, -4.6, 2.3), (MX - 1.0, -4.3, 2.2), (MX - 0.6, MY - 0.4, 1.2), (MX - 0.6, MY - 0.4, 1.2), 26, 7),   # 03 la macchina cade, manovella
    (T_DING, T_BRAVO - 0.05, (MX + 1.9, -2.9, 0.9), (MX + 3.0, -3.9, 0.8), (MX + 0.2, MY - 0.9, 0.45), (4.2, -2.2, 0.35), 28, 5),       # 04 il tostapane scappa
    (T_BRAVO - 0.05, T_KICK - 0.05, (PC[0] + 0.2, PC[1] - 2.3, 1.7), (PC[0] + 0.18, PC[1] - 1.9, 1.7), (PC[0], PC[1], 1.55), (PC[0], PC[1], 1.6), 34, 3),   # 04b «Bravo, cicciomerda»
    (T_KICK - 0.05, T_CAZ, (MX - 0.4, -2.6, 1.4), (MX - 0.3, -2.3, 1.2), (MX - 0.3, MY - 0.6, 0.9), (MX, MY - 1.2, 0.5), 30, 6),     # 05 calcio, esce il pulcino
    (T_CAZ, T_BOOM + 0.05, (MX, -2.6, 0.75), (MX, -2.2, 0.7), (MX + 0.05, MY - 1.3, 0.6), (MX + 0.05, MY - 1.3, 0.65), 36, 3),   # 06 primo piano: si gonfia
    (T_BOOM + 0.05, T_GUAL - 0.05, (MX - 1.0, -5.2, 1.9), (MX - 0.9, -5.6, 2.1), (MX - 0.7, MY - 0.8, 1.2), (MX - 0.7, MY - 0.8, 1.2), 24, 9),   # 07 esplosione, piume
    (T_GUAL - 0.05, T_STAMP - 0.35, (1.9, -5.8, 1.7), (1.7, -5.3, 1.7), (GX[0] + 0.4, GX[1], 1.45), (GX[0] + 0.25, GX[1], 1.45), 26, 6),      # 08 entra Gualtiero
    (T_STAMP - 0.35, T_QUINDI - 0.05, (GX[0] - 0.6, -5.8, 2.6), (GX[0] - 0.5, -5.5, 2.4), (GX[0], GX[1], 1.4), (GX[0], GX[1], 0.6), 26, 8),   # 09 timbro
    (T_QUINDI - 0.05, T_VOI - 0.05, (XS - 0.3, -6.6, 2.3), (XS - 0.15, -4.0, 2.25), (XS, YS, 1.35), (XS, YS, 1.45), 30, 4),     # 10 lenta spinta sulla cassa
    (T_VOI - 0.05, T_SCIMMIE - 0.05, (P0[0] + 0.1, -4.4, 1.6), (P0[0] + 0.1, -2.2, 1.75), (P0[0], P0[1], 1.5), (P0[0] + 0.05, P0[1] - 0.4, 1.65), 30, 6),   # 11 LO CREATE VOI: zoom sul dito
    (T_SCIMMIE - 0.05, T_W[0] - 0.05, (0.0, -2.6, 2.3), (0.0, -3.0, 2.2), (0.0, -7.0, 1.0), (0.0, -7.0, 1.0), 24, 9),    # 11b «branco di scimmie»: il pubblico
    (T_W[0] - 0.05, T_W[1] - 0.05, (-0.6, -5.4, 1.2), (-0.6, -5.2, 1.2), (-0.6, -1.2, 0.9), (-0.6, -1.2, 0.9), 26, 6),       # 12 NOME
    (T_W[1] - 0.05, T_W[2] - 0.05, (1.4, -5.0, 0.6), (1.3, -4.8, 0.6), (0.3, -1.4, 0.8), (0.3, -1.4, 0.8), 26, 6),            # 13 ASPETTO
    (T_W[2] - 0.05, T_W[3] - 0.05, (-1.4, -5.0, 2.2), (-1.3, -4.8, 2.1), (-0.2, -1.4, 0.7), (-0.2, -1.4, 0.7), 26, 6),        # 14 CARATTERE
    (T_W[3] - 0.05, T_W[4] - 0.05, (0.5, -4.6, 0.4), (0.5, -4.4, 0.4), (0.5, -1.4, 0.8), (0.5, -1.4, 0.8), 26, 6),            # 15 POTERI
    (T_W[4] - 0.05, T_TESTA - 0.05, (0.9, -4.2, 1.2), (0.9, -4.0, 1.15), (0.85, -1.15, 0.6), (0.85, -1.15, 0.6), 28, 5),      # 16 STORIA su Tumbo
    (T_TESTA - 0.05, T_REGOLE - 0.1, (0.6, -2.9, 2.0), (0.5, -3.3, 1.9), (0.0, -6.8, 1.1), (0.0, -6.8, 1.15), 28, 8),        # 17 «il criceto morto in testa»: di nuovo le scimmie
    (T_REGOLE - 0.1, T_SEGUI - 0.05, (0.0, -7.0, 1.5), (0.0, -6.6, 1.5), (0.0, -0.9, 2.3), (0.0, -0.9, 2.4), 26, 9),          # 18 REGOLE
    (T_SEGUI - 0.05, T_LIKE - 0.05, (-0.5, -4.3, 1.5), (-0.45, -4.0, 1.4), (-0.55, -1.1, 1.0), (-0.45, -1.1, 0.85), 26, 7),     # 19 SEGUI
    (T_LIKE - 0.05, T_COMM - 0.05, (0.9, -4.4, 0.9), (0.85, -4.1, 0.9), (-0.3, -1.2, 0.8), (0.4, -1.2, 0.7), 26, 7),          # 20 LIKE
    (T_COMM - 0.05, T_48 - 0.1, (0.25, -6.3, 1.0), (0.25, -6.0, 1.0), (0.25, -1.4, 1.6), (0.25, -1.4, 1.1), 26, 8),           # 21 COMMENTI
    (T_48 - 0.1, T_UFF - 0.05, (0.2, -6.6, 0.55), (0.2, -6.2, 0.6), (0.0, 1.0, 3.4), (0.0, 1.0, 3.2), 22, 10),                # 22 timer e nuvoletta
    (T_UFF - 0.05, T_GCOMM - 0.1, (XS - 2.2, -4.6, 0.5), (XS + 1.4, -4.8, 0.6), (XS, YS, 2.0), (XS, YS, 2.3), 24, 7),         # 23 diventa ufficiale: dal basso, giro
    (T_GCOMM - 0.1, T_G2 - 0.05, (-2.3, -4.0, 1.75), (-2.4, -3.7, 1.75), (-3.0, -1.6, 1.6), (-3.0, -1.6, 1.65), 30, 5),       # 24 Gualtiero dietro il cespuglio
    (T_G2 - 0.05, T_PEZZO - 0.05, (-2.72, -2.85, 1.58), (-2.74, -2.78, 1.56), (-3.0, -2.05, 1.3), (-3.0, -2.05, 1.3), 34, 3),  # 25 il telefono: «GUALTIERO 2»
    (T_PEZZO - 0.05, T_NO - 0.05, (-2.75, -3.1, 2.05), (-2.78, -2.8, 2.05), (-3.05, -1.45, 1.95), (-3.05, -1.45, 1.95), 40, 3),   # 25b «pezzo di merda»: ghigno di Gualtiero
    (T_NO - 0.05, TOTAL + 0.1, (0.1, -6.0, 1.5), (0.1, -5.4, 1.45), (0.15, -1.7, 1.3), (0.15, -1.7, 1.25), 24, 6),            # 26 NO! COMMENTA ADESSO
]
SCOSSE = [(0.0, 0.05), (T_MACH, 0.06), (T_BOOM, 0.14), (T_STAMP, 0.12), (T_VOI, 0.06), (T_W[4] + 0.1, 0.06), (T_REGOLE + 0.05, 0.06), (T_SEGUI + 0.3, 0.08), (T_COMM + 0.7, 0.08),
          (T_UFF, 0.05), (T_G2, 0.04), (T_NO, 0.08), (T_COMMENTA, 0.06), (T_ADESSO, 0.1)]
PUGNI = [(T_MANCA, 0.25), (T_DING, 0.12), (T_CAZ + 0.05, 0.3), (T_STAMP + 0.05, 0.15), (T_VOI, 0.5), (T_TESTA + 0.1, 0.12), (T_G2, 0.25), (T_PEZZO + 0.2, 0.12), (T_NO, 0.2), (T_MUOVI, 0.15), (T_COMMENTA, 0.15), (T_ADESSO, 0.35)]
for f in range(1, NF + 1):
    t = (f - 1) / FPS
    s_ = next((s for s in SHOTS if s[0] <= t < s[1]), SHOTS[-1]); u = (t - s_[0]) / (s_[1] - s_[0])
    if s_[0] == T_VOI - 0.05: u = 1 - (1 - min(1.0, u * 1.6)) ** 3                                 # zoom violento sul dito: velocissimo e poi fermo
    cam.location = lerp(s_[2], s_[3], u); tgt.location = lerp(s_[4], s_[5], u); camd.lens = s_[6]; camd.dof.aperture_fstop = s_[7]
    for (e_, a_) in SCOSSE:
        d_ = t - e_
        if 0 <= d_ < 0.7: k_ = a_ * math.exp(-d_ * 7); cam.location = (cam.location.x + k_ * math.sin(d_ * 67), cam.location.y + k_ * math.sin(d_ * 53 + 1), cam.location.z + k_ * math.sin(d_ * 71 + 2))
    pg = [(e_, a_) for (e_, a_) in PUGNI if s_[0] <= e_ <= t < s_[1]]                              # zoom secco: vale solo l'ultimo (non si sommano)
    if pg: e_, a_ = pg[-1]; camd.lens = camd.lens * (1 + a_ * (1 - math.exp(-(t - e_) * 16)))
    cam.keyframe_insert('location', frame=f); tgt.keyframe_insert('location', frame=f); camd.keyframe_insert('lens', frame=f); camd.dof.keyframe_insert('aperture_fstop', frame=f)

def lin(idb):
    for fc in all_fcurves(idb):
        kind = 'CONSTANT' if 'hide' in fc.data_path else 'LINEAR'
        for kp in fc.keyframe_points: kp.interpolation = kind
for o in bpy.data.objects: lin(o)
for l_ in bpy.data.lights: lin(l_)
set_interp(camd, 'CONSTANT')
for nm in ('CinemaRiempimento', 'CinemaControluce'): bpy.data.lights[nm].use_shadow = False
try: scene.render.use_motion_blur = True; scene.render.motion_blur_shutter = 0.06
except Exception: pass
os.makedirs('../t020', exist_ok=True)
import json; json.dump([[round(s[0], 3), round(min(s[1], TOTAL), 3)] for s in SHOTS], open('../t020/shots.json', 'w'))
bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath('../t020/pippo_t020.blend')); print('SAVED', len(bpy.data.objects), 'oggetti')
