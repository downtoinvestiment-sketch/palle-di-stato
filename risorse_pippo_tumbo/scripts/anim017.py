"""Test 017 - IL BAMBINO NON ESCE (41 s). Salva ../t017/pippo_t017.blend
Tutto in interni: sala parto (attorno all'origine) e discoteca (x = 200). Niente quartiere: scena vuota, piu' leggera.
Personaggi: Pippo e Tumbo ESISTENTI (pippo.py, tumbo.py) invariati. Eleonora, Gualtiero, agente: quelli degli episodi precedenti.
Scelte dell'autore riusate: G2 camion dei pompieri del kit, H1 cocomero senza faccia, I3 hamburger gigante come «panino», K2 stanza arredata con i mobili del kit.
Uso: python anim017.py   (i tempi vengono da audio/words_t017.json, scritti qui sotto a mano)"""
import sys, math, os, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, numpy as np
from mathutils import Vector, Euler, Matrix
from common import *
from render_setup import *
import set004, props004, props007, props009, props010, props012, props013, props015, props016b, props017, kitlook, tumbo, eleonora, luci
import pippo2 as pippo                                                                            # Pippo di sempre con le emozioni nuove (regola dell'autore)
from set004 import obj, bx, cyl, ball_, MB
from props007 import text_obj
A = kitlook.A

FPS = 24; TOTAL = 44.0; NF = int(TOTAL * FPS)
def fr(t): return max(1, int(round(t * FPS)) + 1)
def sm(x): x = min(1.0, max(0.0, x)); return x * x * (3 - 2 * x)
def ramp(t, a, b): return sm((t - a) / (b - a))
def lerp(a, b, u): return tuple(a[i] + (b[i] - a[i]) * u for i in range(len(a)))
def add(a, b): return tuple(a[i] + b[i] for i in range(3))
PI = math.pi

reset_scene(); scene = bpy.context.scene
setup_render(scene, 1080, 1920, samples=6, fps=FPS, frames=NF); scene.frame_end = NF
A.qualita_eevee(preset='equilibrato', riflessi=False, scena=scene); scene.view_settings.exposure = 0.25
envc = collection('Env'); chc = collection('Characters'); prc = collection('Props'); cac = collection('Cameras')
WORLD = A.cielo('sunflowers_puresky', forza=1.1, rotazione=43.0, ris='4k')
BGN = [n for n in WORLD.node_tree.nodes if n.type == 'BACKGROUND']
# Luci della sala parto. A = la prima versione (tutto dall'alto, piatta). B = sole caldo di lato. C = cinema, piu' contrasto. D = morbida ma calda.
# Cambiano solo le luci della stanza e quanta luce del cielo entra: colori, esposizione e discoteca restano uguali, cosi' i fotogrammi della discoteca non vanno rifatti.
LUCI = os.environ.get('LUCI017', 'C'); BLEND = os.environ.get('BLEND017', '../t017/pippo_t017.blend')      # C = la luce scelta dall'autore (17 novembre 2026)
LCFG = {'A': dict(cielo=1.1, soffitto=0.55, alto=(560, 240, 160), calda=False, key=0, key_soft=0.3, key_col=(1, 0.84, 0.62), fill=0, rim=0, lampada=0),
        'B': dict(cielo=0.34, soffitto=0.30, alto=(130, 200, 0), calda=False, key=2600, key_soft=0.2, key_col=(1.0, 0.84, 0.62), fill=90, rim=300, lampada=60, buco=1200),
        'C': dict(cielo=0.15, soffitto=0.12, alto=(50, 120, 0), calda=False, key=3400, key_soft=0.05, key_col=(1.0, 0.78, 0.5), fill=40, rim=520, lampada=110, buco=900),
        'D': dict(cielo=0.6, soffitto=0.40, alto=(380, 60, 60), calda=True, key=1100, key_soft=0.6, key_col=(1.0, 0.86, 0.68), fill=60, rim=150, lampada=60, buco=500)}[LUCI]
if LUCI != 'A':                                                                                  # il cielo si vede com'e' (dal buco nel muro), ma illumina meno la stanza
    _nt = WORLD.node_tree; _bg = BGN[0]; _out = next(n for n in _nt.nodes if n.type == 'OUTPUT_WORLD')
    _bg2 = _nt.nodes.new('ShaderNodeBackground'); _bg2.inputs['Strength'].default_value = 1.1; _nt.links.new(_bg.inputs['Color'].links[0].from_socket, _bg2.inputs['Color'])
    _lp = _nt.nodes.new('ShaderNodeLightPath'); _mix = _nt.nodes.new('ShaderNodeMixShader')
    _nt.links.new(_lp.outputs['Is Camera Ray'], _mix.inputs['Fac']); _nt.links.new(_bg.outputs['Background'], _mix.inputs[1]); _nt.links.new(_bg2.outputs['Background'], _mix.inputs[2]); _nt.links.new(_mix.outputs['Shader'], _out.inputs['Surface'])
M = set004.make_mats(); G9 = props009.mats009(); H = props010.mats010(); Z12 = props012.mats012(); A13 = props013.mats013(); W = props015.mats015(); B = props016b.mats016b(); Q = props017.mats017()
FONT = A.font('luckiest')
DX = 200.0                                                                                       # centro della discoteca

# camera subito: gli effetti (A.effetto) si girano verso la camera
camd = bpy.data.cameras.new('Cam'); cam = bpy.data.objects.new('Cam', camd); cac.objects.link(cam); scene.camera = cam
camd.clip_start = 0.05; camd.clip_end = 1500; camd.sensor_width = 36
tgt = empty('CamTarget', (0, 0, 1), None, cac)
ct = cam.constraints.new('TRACK_TO'); ct.target = tgt; ct.track_axis = 'TRACK_NEGATIVE_Z'; ct.up_axis = 'UP_Y'
camd.dof.use_dof = True; camd.dof.focus_object = tgt

# ======================= tempi (dalla voce: audio/words_t017.json) =======================
T_SLAM, T_SIGN0 = 3.86, 4.42                    # «e non e' piu' uscito»: la porticina sbatte, esce il cartello
T_RESTART = 5.58                                # «Eleonora deve partorire»
T_KNOCK, T_OCC = 9.20, 10.30                    # «Pippo bussa.» «Occupato.»
T_BURG, T_HAND, T_GRAB, T_PULL = 11.32, 13.02, 14.22, 15.34
T_TUMBO, T_TNT = 16.20, 17.86                   # «Quindi manda dentro Tumbo.» «Tumbo non torna.»
T_POL, T_COP, T_NT2 = 19.16, 20.34, 21.44
T_POMP, T_TRUCK, T_INDOV = 22.44, 23.82, 25.44
T_PIPPO, T_DIVE = 26.62, 27.0
T_BLACK, T_DISCO0 = 27.45, 28.32                # tunnel di luci dentro la porticina (prima era un buio), poi «Ma che cazzo?»
T_GIANT, T_WALK, T_STAND = 40.5, 41.35, 42.3   # finale: la sala parto era dentro un'Eleonora gigante; arriva un Pippo gigante
T_KN2 = (42.62, 42.87, 43.12); T_SIGN2 = 43.3   # tre colpi enormi, poi il cartello OCCUPATO gigante
G = 14.0; XG = -400.0                           # scala e posto del mondo gigante
def MG(p): return (XG + G * p[0], G * p[1], G * p[2])
T_REVEAL, T_BABIES, T_COPD, T_DJ = 29.56, 31.05, 32.30, 33.60
T_BOUNCER, T_GUAL, T_LIST, T_END = 35.25, 37.50, 38.70, 39.75

# ======================= sala parto =======================
mwall = A.materiale('PaintedPlaster017', dimensione=2.6, rilievo=0.5, tinta=(0.78, 1.12, 1.02), nome='PT_parete_ospedale')
mfloor = A.materiale('laminate_floor_02', dimensione=2.4, rilievo=0.6, nome='PT_pavimento_ospedale')
mceil = material('P17_soffitto', (1, 1, 1), rough=0.9, emit=(1.0, 0.98, 0.95), emit_strength=LCFG['soffitto'])
ROOM, PLUG, RUBBLE = props017.stanza(envc, Q, mwall, mfloor, mceil)
BEDX, BEDY = -0.2, 1.3
props016b.kplace(A, 'kenney/furniture-kit/bedSingle', envc, BEDX, BEDY, s=2.3, rot=90)
props016b.kplace(A, 'kenney/furniture-kit/sideTableDrawers', envc, -2.55, 2.55, s=2.3)
props016b.kplace(A, 'kenney/furniture-kit/lampRoundFloor', envc, -3.4, 2.4, s=2.4)
props016b.kplace(A, 'kenney/furniture-kit/pottedPlant', envc, 5.7, 2.3, s=2.4)
props016b.kplace(A, 'kenney/furniture-kit/cabinetTelevision', envc, 3.3, 2.55, s=2.3)
props016b.kplace(A, 'kenney/furniture-kit/televisionModern', envc, 3.3, 2.55, z=0.31 * 2.3, s=2.3)
props016b.kplace(A, 'kenney/furniture-kit/bear', envc, -2.55, 2.5, z=0.38 * 2.3, s=1.4)
props016b.kplace(A, 'kenney/furniture-kit/rugRounded', envc, 1.6, -1.6, z=0.005, s=3.0)
props016b.kplace(A, 'kenney/furniture-kit/loungeChair', envc, -3.1, -0.6, s=2.3, rot=-70)
props015.window(envc, W, (1.1, 2.97, 2.0), 1.4, 1.2)
obj('CroceH1', set004.box_c(), (-3.1, 2.98, 2.5), (0.6, 0.04, 0.18), A13['cross'], envc); obj('CroceH2', set004.box_c(), (-3.1, 2.98, 2.5), (0.18, 0.04, 0.6), A13['cross'], envc)
CAL = props017.calendario(envc, Q, (-0.55, 2.96, 2.0), font=FONT)
for k, (col, dx, dy, h) in enumerate((((1.0, 0.4, 0.65), 0.0, 0.0, 2.3), ((0.35, 0.7, 1.0), 0.34, 0.14, 2.62), ((1.0, 0.82, 0.15), -0.3, 0.2, 2.05))):      # palloncini legati alla testiera
    mp_ = material('P17_pallone%d' % k, col, rough=0.25, spec=0.8)
    ball_('Palloncino', 1.0, (-1.75 + dx, 2.25 + dy, h), mp_, envc, sc=(0.25, 0.25, 0.3)); obj('PalloncinoFilo', set004.box_c(), (-1.75 + dx, 2.25 + dy, (h - 0.3 + 0.75) / 2), (0.008, 0.008, h - 0.3 - 0.75), Q['frame'], envc)
props017.testo(envc, 'Striscione', 'BENVENUTO BIMBO', 0.2, material('P17_striscione', (1.0, 0.35, 0.6), rough=0.5), (-1.6, 2.97, 2.82), font=FONT, spessore=0.01)
fl = MB([Q['chrome'], Q['milk'], Q['ledc'], Q['booth'], Q['screen']])                           # flebo e monitor accanto al letto
fl.b2((-1.87, 0.58, 0.0), (-1.83, 0.62, 1.95), 0); fl.b2((-2.05, 0.45, 0.0), (-1.65, 0.75, 0.04), 0); fl.b2((-1.95, 0.585, 1.9), (-1.75, 0.615, 1.93), 0); fl.b2((-1.99, 0.56, 1.5), (-1.87, 0.64, 1.86), 1); fl.b2((-1.94, 0.59, 1.1), (-1.92, 0.61, 1.5), 2)
fl.b2((-2.42, 1.18, 0.0), (-2.36, 1.24, 1.25), 0); fl.b2((-2.62, 1.0, 0.0), (-2.16, 1.42, 0.04), 0); fl.b2((-2.66, 1.12, 1.25), (-2.12, 1.32, 1.68), 3); fl.b2((-2.61, 1.105, 1.3), (-2.17, 1.12, 1.63), 4); fl.build('FleboMonitor', envc)
# fuori dal buco nel muro: prato, strada, alberi veri, due case
mgrass = A.materiale('Grass001', dimensione=3.0, rilievo=0.8, tinta=(1.05, 1.35, 0.7), ruvidita=1.5)
OUT = [bx('PratoFuori', (6.6, -40, -0.3), (70, 40, -0.02), mgrass, envc), bx('StradaFuori', (6.6, -3.6, -0.02), (70, 0.2, 0.0), A.materiale('asphalt_02', dimensione=4.0, rilievo=0.8, tinta=(0.8, 0.8, 0.85)), envc)]
for k, (aid, x, y, h) in enumerate((('island_tree_01', 16, 5.5, 7.5), ('tree_small_02', 13, -9, 6.0), ('island_tree_02', 24, -7.5, 7.0), ('island_tree_03', 21, 9, 5.5), ('island_tree_01', 31, 3.5, 8.0), ('tree_small_02', 34, -5.5, 6.5))):
    OUT.append(A.albero_cartonato(aid, posizione=(x, y, 0), altezza=h, collezione=envc, vista=k))
for k, (c, x, y, r) in enumerate((('c', 27, 12, -90), ('h', 30, -15, -90), ('m', 44, 0, -90))):
    OUT.append(A.modello('kenney/city-kit-suburban/building-type-%s' % c, posizione=(x, y, 0), altezza=7.5, rotazione=r, collezione=envc))
kitlook.tune_cutouts(1.9)

def area(name, loc, size, energy, col=(1, 0.97, 0.92), coll=None):
    l_ = bpy.data.lights.new(name, 'AREA'); l_.size = size; l_.energy = energy; l_.color = col; o_ = bpy.data.objects.new(name, l_); (coll or prc).objects.link(o_); o_.location = loc; return o_
def punta(o, to): o.rotation_euler = (Vector(to) - Vector(o.location)).to_track_quat('-Z', 'Y').to_euler(); return o
_wc = (1.0, 0.9, 0.78) if LCFG['calda'] else (1, 0.97, 0.92)
ROOML = [area('LuceOspedale', (0.6, -1.2, 3.2), 5.0, LCFG['alto'][0], _wc), area('LuceOspedale2', (3.6, -2.4, 3.2), 3.0, LCFG['alto'][1], _wc), area('LuceOspedale3', (-1.0, 1.0, 3.2), 2.5, LCFG['alto'][2], _wc)]
if LCFG['key']:
    # luce principale calda, di lato e dall'alto (come il sole da una finestra): illumina le facce di Pippo e di Eleonora e fa le ombre sul pavimento e sul letto
    _k = bpy.data.lights.new('LuceChiave', 'SPOT'); _k.energy = LCFG['key']; _k.color = LCFG['key_col']; _k.spot_size = 1.25; _k.spot_blend = 0.7; _k.shadow_soft_size = LCFG['key_soft']
    _ko = bpy.data.objects.new('LuceChiave', _k); prc.objects.link(_ko); _ko.location = (3.2, 2.6, 2.75); punta(_ko, (-0.8, 0.8, 0.9)); ROOML.append(_ko)
    ROOML.append(punta(area('LuceRiempimento', (3.6, -2.6, 2.3), 3.0, LCFG['fill'], (0.75, 0.85, 1.0)), (-0.5, 0.5, 1.0)))      # riempimento freddo dal lato della camera
    ROOML.append(punta(area('LuceContro', (-3.5, -1.8, 2.5), 1.5, LCFG['rim'], (0.65, 0.8, 1.0)), (-0.8, 0.8, 1.2)))            # controluce azzurro: stacca i personaggi dal fondo
    _l = bpy.data.lights.new('LuceLampada', 'POINT'); _l.energy = LCFG['lampada']; _l.color = (1.0, 0.7, 0.4); _l.shadow_soft_size = 0.3
    _lo = bpy.data.objects.new('LuceLampada', _l); prc.objects.link(_lo); _lo.location = (-3.4, 2.4, 1.75); ROOML.append(_lo)   # la lampada nell'angolo accesa
    for nm in ('LuceRiempimento', 'LuceContro', 'LuceLampada'): bpy.data.lights[nm].use_shadow = False
    LBUCO = punta(area('LuceBuco', (6.35, -1.7, 2.1), 3.4, LCFG['buco'], (1.0, 0.95, 0.85)), (0.0, -0.9, 0.6))
    LBUCO.data.use_shadow = False; LBUCO.data.use_custom_distance = True; LBUCO.data.cutoff_distance = 5.2                          # senza ombre (a 4 campioni facevano grana) e solo vicino al buco: non deve sbiancare Eleonora                    # la luce del giorno che entra dal buco nel muro (solo quando il muro e' sfondato)

# ======================= personaggi =======================
P = pippo.build_pippo(chc); Tb = tumbo.build_tumbo(chc, scale=0.75)
Z = eleonora.zucchina(chc, Z12); GU = props009.gualtiero(chc, G9); COP = props010.cop(chc, 'Agente')
for r in (P['root'], Tb['root'], Z['root'], GU['root'], COP['root']): r.rotation_mode = 'XYZ'
for nm in 'LR': P['shoulder' + nm].rotation_mode = 'QUATERNION'
def qdir(d, rest=(0, 0, -1)): return Vector(rest).rotation_difference(Vector(d).normalized())
def yaw_to(a, b): return math.atan2(b[0] - a[0], -(b[1] - a[1]))

# Eleonora: seduta sul letto contro il cuscino, girata di tre quarti verso la stanza. La porticina e' sulla pancia.
ELE = (BEDX - 0.72, BEDY, 0.56); EYAW = 0.85; EROT = (-0.10, 0.0, EYAW); ES = 1.3
Z['root'].location = ELE; Z['root'].rotation_euler = EROT; Z['root'].scale = (ES, ES, ES)
ball_('ZucPancia', 1.0, (0, -0.07, 0.29), Z12['zuc'], chc, parent=Z['root'], sc=(0.24, 0.21, 0.24))
D = props017.porticina(chc, Q, Z['root'], (0, -0.285, 0.29), font=FONT)
MAG, MAGP = props017.rivista(chc, Q, Z['root'], (0, -0.2, 0.585), (0.35, 0, 0), font=FONT)
HAND = props017.manina(chc, Q); HAND.parent = D['root']
ZM = Matrix.Translation(ELE) @ Euler(EROT, 'XYZ').to_matrix().to_4x4() @ Matrix.Scale(ES, 4)
DOORW = tuple(ZM @ Vector((0, -0.30, 0.29))); _n = (ZM.to_3x3() @ Vector((0, -1, 0))).normalized(); _n = Vector((_n.x, _n.y, 0)).normalized(); DN = (_n.x, _n.y); DT = (-_n.y, _n.x)       # centro della porticina, normale (in fuori) e tangente
def dw(n=0.0, t=0.0, z=None): return (DOORW[0] + DN[0] * n + DT[0] * t, DOORW[1] + DN[1] * n + DT[1] * t, DOORW[2] if z is None else z)
print('DOORW', [round(v, 3) for v in DOORW], 'DN', [round(v, 3) for v in DN], 'DT', [round(v, 3) for v in DT])

# ======================= oggetti =======================
def wrap(name, r, coll):
    g = empty(name, (0, 0, 0), None, coll); r.parent = g; r.location = (0, 0, 0); g.rotation_mode = 'XYZ'; return g
TRUCK_H = 2.6
TRUCK = wrap('Camion', A.modello('kenney/car-kit/firetruck', altezza=TRUCK_H, collezione=prc), prc)
def satura(root, sat=1.9, val=0.75):
    """i modelli del kit sono color pastello: sotto le luci della stanza il rosso diventa rosa. Aumenta la saturazione."""
    for o in root.children_recursive:
        if o.type != 'MESH': continue
        for m in o.data.materials:
            if not m or not m.node_tree or m.node_tree.nodes.get('PT_sat'): continue
            nt = m.node_tree; b = next((n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED'), None)
            if not b: continue
            hs = nt.nodes.new('ShaderNodeHueSaturation'); hs.name = 'PT_sat'; hs.inputs['Saturation'].default_value = sat; hs.inputs['Value'].default_value = val; inp = b.inputs['Base Color']
            if inp.is_linked: nt.links.new(inp.links[0].from_socket, hs.inputs['Color'])
            else: hs.inputs['Color'].default_value = inp.default_value
            nt.links.new(hs.outputs['Color'], inp)
satura(TRUCK)
sir = bpy.data.lights.new('LuceSirena', 'POINT'); sir.shadow_soft_size = 0.5; siro = bpy.data.objects.new('LuceSirena', sir); prc.objects.link(siro); siro.parent = TRUCK; siro.location = (0, -1.2, TRUCK_H + 0.3)
BURG_H = 0.85
BURGER = wrap('Panino', A.modello('kenney/food-kit/burger-double', altezza=BURG_H, collezione=prc), prc)
MEGA = A.modello('Megaphone_01', altezza=0.42, max_triangoli=4000, collezione=chc); MEGA.parent = COP['head']; MEGA.location = (0.12, -0.52, -0.12); MEGA.rotation_euler = (0, 0, PI / 2)
HAT = props017.cappello(prc, Q); HAT.rotation_mode = 'XYZ'
COLLAR = props017.collare(prc, Q); COLLAR.rotation_mode = 'XYZ'
PHONE = props010.phone(chc, H, P['shoulderR'])
MEL = props016b.watermelon(prc, B, r=0.3)
CLIP = props017.lista(chc, Q, GU['shoulderR'], (0.0, -0.16, -0.74), font=FONT); CLIP.rotation_euler = (1.35, 0, 0)
CART = props017.carrello(prc, Q)
SUN = props017.occhiali(chc, Q, GU['head'])
PHONES = props017.cuffie(chc, Q, Tb['head'])
COPHAT = [c for c in COP['head'].children if c.name.startswith(('AgBerretto', 'AgVisiera', 'AgStemma'))]
bx('Buio', (398, -2, -2), (402, 2, 2), Q['blackout'], envc)

# ======================= discoteca =======================
mdwall = A.materiale('PaintedPlaster017', dimensione=3.0, rilievo=0.5, tinta=(0.22, 0.10, 0.36), nome='PT_parete_disco')
mdfloor = material('P17_dfloor', (0.03, 0.025, 0.05), rough=0.25, spec=0.8)
props017.discoteca(envc, Q, mdwall, mdfloor, DX)
props017.pista(envc, Q, DX, -1.0, 10, 7, 0.9)
CON, PLAT = props017.console(envc, Q); CON.location = (DX, 4.1, 0.7)
BALL = props017.palla_specchi(envc, Q); BALL.location = (DX, -1.0, 4.4); BALL.rotation_mode = 'XYZ'
props017.corda(envc, Q, DX - 0.85, DX + 0.85, -6.2)
props016b.door(envc, B, (DX, -9.36, 0.0), rotz=PI, label='USCITA')
for sx in (-1, 1):
    props016b.kplace(A, 'kenney/furniture-kit/speaker', envc, DX + sx * 3.1, 4.3, z=0.7, s=3.6)
    props016b.kplace(A, 'kenney/furniture-kit/speaker', envc, DX + sx * 4.3, 4.6, z=0.7, s=2.6)
    props016b.kplace(A, 'kenney/furniture-kit/speakerSmall', envc, DX + sx * 3.1, 4.3, z=0.7 + 0.636 * 3.6, s=3.0)
# bancone del bar con i biberon, sgabelli, il cocomero senza faccia
bar = MB([Q['booth'], Q['wood'], Q['ledc']]); bar.b2((DX - 8.6, -4.0, 0.0), (DX - 7.5, 2.4, 1.05), 0); bar.b2((DX - 8.7, -4.1, 1.05), (DX - 7.4, 2.5, 1.12), 1); bar.b2((DX - 7.5, -4.0, 0.5), (DX - 7.48, 2.4, 0.58), 2); bar.build('Bancone', envc)
for k in range(9): props017.biberon(envc, Q, (DX - 8.0 + 0.25 * (k % 2), -3.5 + k * 0.7, 1.12), s=1.6, k=k)
for k, y in enumerate((-2.8, -1.0, 0.8)): props016b.kplace(A, 'kenney/furniture-kit/stoolBar', envc, DX - 6.9, y, s=1.9)
MELD = (DX - 6.9, -1.0, 0.83)
props017.biberon(envc, Q, (DX - 7.6, -1.0, 1.12), s=2.0, k=2)
props016b.kplace(A, 'kaykit/furniture-bits/table_medium_long', envc, DX + 6.9, -5.0, s=0.9)
BURGD = (DX + 6.9, -5.0, 0.72)
TRUCKD = (DX + 6.4, 0.9, 0.0); TRUCKDYAW = 0.55
FF = []
for k, (x, y) in enumerate(((DX + 4.9, -2.6), (DX + 5.6, 3.3))):
    f_ = props004.player(chc, 'Pompiere%d' % k, (0.85, 0.12, 0.08), (0.2, 0.2, 0.25), (0.96, 0.74, 0.6), (0.2, 0.13, 0.08), scale=1.0); f_['root'].location = (x, y, 0); f_['root'].rotation_mode = 'XYZ'
    hd = [c for c in f_['root'].children if c.name.startswith('Head')][0]; ball_('Elmetto', 1.0, (0, 0.0, 0.14), B['yellow'], chc, parent=hd, sc=(0.33, 0.33, 0.24)); obj('ElmettoTesa', set004.box_c(), (0, -0.2, 0.08), (0.5, 0.34, 0.04), B['yellow'], chc, parent=hd)
    FF.append(f_)
DL = [area('DiscoMagenta', (DX - 3.4, -1.2, 6.2), 5.0, 1500, (1.0, 0.12, 0.75), envc), area('DiscoCiano', (DX + 3.4, -1.0, 6.2), 5.0, 1500, (0.1, 0.75, 1.0), envc),
      area('DiscoDJ', (DX, 2.9, 4.4), 2.0, 260, (1.0, 0.85, 0.6), envc), area('DiscoIngresso', (DX, -7.0, 4.2), 2.2, 330, (1.0, 0.9, 0.8), envc), area('DiscoBar', (DX - 7.0, -1.0, 4.0), 2.5, 380, (0.6, 0.8, 1.0), envc)]
DL[2].rotation_euler = (0.6, 0, 0); DL[3].rotation_euler = (0.25, 0, 0)
DL.append(area('DiscoFronte', (DX, 3.1, 2.6), 4.0, 420, (1.0, 0.8, 0.75), envc)); DL[-1].rotation_euler = (-0.95, 0, 0)

# 200 neonati sulla pista: sei mesh (tre colori, braccia su o giu') ripetute; ballano con un ciclo che si ripete da solo
BM = [props017.neonato_mesh('Neonato%d%d' % (k, a), [Q['skin'][k], Q['diaper'][k], Q['black'], Q['paci'][k], Q['hair']], braccia_su=bool(a)) for k in range(3) for a in range(2)]
brnd = random.Random(17); BABIES = []; COPD = (DX + 2.3, -0.5)
for i in range(18):
    for j in range(12):
        x = DX - 4.25 + i * 0.5 + brnd.uniform(-0.09, 0.09); y = -4.0 + j * 0.52 + brnd.uniform(-0.09, 0.09)
        if math.hypot(x - COPD[0], y - COPD[1]) < 0.75 or len(BABIES) >= 200: continue
        o = bpy.data.objects.new('Neonato', BM[brnd.randrange(6)]); chc.objects.link(o); s = brnd.uniform(0.92, 1.12); o.scale = (s, s, s)
        BABIES.append((o, (x, y, 0.045), PI + brnd.uniform(-0.5, 0.5), brnd.randrange(12), brnd.uniform(0.07, 0.16)))
print('NEONATI', len(BABIES))

# ======================= tunnel di luci (dentro la porticina, al posto del buio) =======================
TUN_X, TUN_Z, TUN_Y0, TUN_Y1 = 300.0, 50.0, 0.0, 34.0
_tc = [(1.0, 0.1, 0.7), (0.1, 0.85, 1.0), (1.0, 0.8, 0.1), (0.55, 0.2, 1.0)]
_tm = []
for k_, col in enumerate(_tc):
    me = props017.torus_mesh('AnelloTunnel%d' % k_, 2.4, 0.09, 40, 8); me.materials.append(material('P17_anello%d' % k_, col, rough=0.3, emit=col, emit_strength=2.6)); _tm.append(me)
for k_ in range(30):
    o = bpy.data.objects.new('AnelloTunnel', _tm[k_ % 4]); envc.objects.link(o); o.location = (TUN_X, -4 + k_ * 2.4, TUN_Z + 1.0); o.rotation_euler = (PI / 2, 0, k_ * 0.4)
_tw = MB([material('P17_tunnel', (0.04, 0.0, 0.07), rough=0.6, emit=(0.25, 0.02, 0.35), emit_strength=0.25)])
for (a_, b_) in (((-3.2, -8, -2.4), (-3.0, 70, 4.6)), ((3.0, -8, -2.4), (3.2, 70, 4.6)), ((-3.2, -8, -2.6), (3.2, 70, -2.4)), ((-3.2, -8, 4.4), (3.2, 70, 4.6))):
    _tw.b2((TUN_X + a_[0], a_[1], TUN_Z + 1 + a_[2] - 1), (TUN_X + b_[0], b_[1], TUN_Z + 1 + b_[2] - 1), 0)
_tw.build('PareteTunnel', envc)
LTUN = bpy.data.lights.new('LuceTunnel', 'POINT'); LTUN.energy = 260; LTUN.shadow_soft_size = 0.4; LTUN.use_shadow = False
LTUNO = bpy.data.objects.new('LuceTunnel', LTUN); envc.objects.link(LTUNO); LTUNO.location = (TUN_X, 0, TUN_Z + 2)

# ======================= mondo gigante: la sala parto era dentro un'Eleonora gigante =======================
mbig = A.materiale('Grass001', dimensione=3.0, rilievo=0.8, tinta=(1.05, 1.35, 0.7), ruvidita=1.5, nome='PT_prato_gigante')
bx('PratoGigante', (XG - 260, -260, -0.3), (XG + 260, 260, 0.0), mbig, envc)
props016b.kplace(A, 'kenney/furniture-kit/bedSingle', envc, *MG((BEDX, BEDY, 0))[:2], s=2.3 * G, rot=90)
Z2 = eleonora.zucchina(chc, Z12); Z2['root'].rotation_mode = 'XYZ'; Z2['root'].location = MG(ELE); Z2['root'].rotation_euler = EROT; Z2['root'].scale = (ES * G,) * 3
ball_('ZucPanciaG', 1.0, (0, -0.07, 0.29), Z12['zuc'], chc, parent=Z2['root'], sc=(0.24, 0.21, 0.24))
D2 = props017.porticina(chc, Q, Z2['root'], (0, -0.285, 0.29), font=FONT)
MAG2, MAGP2 = props017.rivista(chc, Q, Z2['root'], (0, -0.2, 0.585), (0.35, 0, 0), font=FONT)
_rnd = random.Random(40)
for k_ in range(26):                                                                              # alberi veri e case: danno la misura (Eleonora e' alta piu' di 20 metri)
    a_ = _rnd.uniform(0, 2 * PI); r_ = _rnd.uniform(38, 120); x_, y_ = XG + r_ * math.cos(a_), r_ * math.sin(a_)
    if math.hypot(x_ - MG(dw(3.4, 1.2))[0], y_ - MG(dw(3.4, 1.2))[1]) < 30: continue             # lascia libera la vista della camera
    A.albero_cartonato(['island_tree_01', 'tree_small_02', 'island_tree_02', 'island_tree_03', 'fir_tree_01'][k_ % 5], posizione=(x_, y_, 0), altezza=_rnd.uniform(7, 12), collezione=envc, vista=k_)
for k_, (c_, a_, r_) in enumerate((('c', 2.2, 55), ('h', 2.9, 62), ('m', 3.6, 70), ('c', 4.4, 58), ('h', 5.4, 66))):
    A.modello('kenney/city-kit-suburban/building-type-%s' % c_, posizione=(XG + r_ * math.cos(a_), r_ * math.sin(a_), 0), altezza=7.5, rotazione=math.degrees(a_) + 90, collezione=envc)
for k_, (aid_, n_, t_, rot_) in enumerate((('kenney/car-kit/sedan', 1.25, -0.95, 30), ('kenney/car-kit/taxi', 2.1, 0.55, -60), ('kenney/car-kit/van', 1.65, 1.35, 100), ('kenney/car-kit/police', 2.6, -0.2, 10))):
    A.modello(aid_, posizione=MG(dw(n_, t_, 0)), altezza=1.6 if 'van' not in aid_ else 2.2, rotazione=rot_, collezione=envc)
for k_, (n_, t_, h_) in enumerate(((1.0, -1.55, 8.0), (2.3, 1.9, 9.5), (1.5, 2.35, 7.0))):
    A.albero_cartonato(['island_tree_02', 'tree_small_02', 'island_tree_01'][k_], posizione=MG(dw(n_, t_, 0)), altezza=h_, collezione=envc, vista=k_ + 30)
kitlook.tune_cutouts(1.9)
SOLE = luci.sole(prc, (DN[0], DN[1]), lato=1, energia=4.2, angolo_alto=38, nome='SoleGigante')

# pulviscolo nella luce della sala parto: duecento granelli caldi (una mesh sola)
import bmesh
_bm = bmesh.new(); _r = random.Random(9)
for k_ in range(140):
    c_ = Vector((_r.uniform(-1.6, 3.4), _r.uniform(-2.6, 2.4), _r.uniform(0.4, 2.8))); vs_ = bmesh.ops.create_icosphere(_bm, subdivisions=1, radius=_r.uniform(0.0025, 0.005))['verts']
    for v_ in vs_: v_.co += c_ - Vector((0.9, -0.1, 1.6))
_dme = bpy.data.meshes.new('Pulviscolo'); _bm.to_mesh(_dme); _bm.free(); _dme.materials.append(material('P17_pulviscolo', (1, 0.9, 0.7), rough=0.5, emit=(1.0, 0.85, 0.6), emit_strength=0.5))
DUST = bpy.data.objects.new('Pulviscolo', _dme); envc.objects.link(DUST); DUST.location = (0.9, -0.1, 1.6); DUST.rotation_mode = 'XYZ'

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
def hide(o):
    """nasconde per sempre: va chiamata PRIMA di show() sul genitore."""
    for q in [o] + list(desc(o)): NEVER.add(q.name); q.hide_render = True; q.keyframe_insert('hide_render', frame=1)
hide(Z['veil']); hide(Z['legs']); hide(Z2['veil']); hide(Z2['legs'])
def show_only(o, intervals):
    """come show(), ma dopo blocca l'oggetto: lo show() del genitore non lo tocca piu' (va chiamata PRIMA di quella del genitore)."""
    show(o, intervals)
    for q in [o] + list(desc(o)): NEVER.add(q.name)
T_T_IN, T_C_IN, T_TR_IN, T_P_IN = 17.6, 21.25, 25.2, 27.42                                       # quando Tumbo, l'agente, il camion e Pippo spariscono nella porticina
T_HOOK_IN = 2.72                                                                                 # il camion dell'hook sparisce nella porticina
for h_ in COPHAT: show_only(h_, [(T_COP - 0.15, T_C_IN - 0.25)])                                 # il berretto resta fuori; in discoteca l'agente balla senza
show_only(PHONES, [(T_DISCO0, T_END)]); show_only(CLIP, [(T_LIST - 0.2, T_END)])
show_only(PHONE, [(T_POL - 0.1, T_COP - 0.15), (T_POMP - 0.1, T_TRUCK - 0.2)])
show(HAT, [(0.0, T_RESTART), (T_C_IN - 0.25, TOTAL)])
show(COLLAR, [(0.0, T_RESTART), (T_TNT + 0.4, TOTAL)])
show(HAND, [(T_HAND - 0.05, T_PULL + 0.75)])
show(Tb['root'], [(T_RESTART, T_T_IN), (T_DISCO0, T_END)])
show(COP['root'], [(T_COP - 0.15, T_C_IN), (T_DISCO0, T_END)])
show(TRUCK, [(0.0, T_HOOK_IN), (T_TRUCK - 0.25, T_TR_IN), (T_DISCO0, T_END)])
show(BURGER, [(T_BURG - 0.25, T_PULL + 0.72), (T_DISCO0, T_END)]); show(CART, [(T_BURG - 0.25, T_TUMBO - 0.15)])
show(P['root'], [(0.0, TOTAL)])
show(GU['root'], [(T_BOUNCER, T_END)])
show(PLUG, [(T_RESTART, T_TRUCK)]); show(RUBBLE, [(0.0, T_RESTART), (T_TRUCK, TOTAL)])
if LCFG['key']: show(LBUCO, [(0.0, T_RESTART), (T_TRUCK, T_BLACK), (T_END, TOTAL)])

# ======================= pose =======================
P_DOOR = dw(0.4, -0.95)[:2]                                                                     # il posto di Pippo: per terra, di fianco alla porticina (la camera lo vede di tre quarti)
P_PH = dw(1.5, -0.8)[:2]; P_AWAY = dw(1.6, -2.3)[:2]; P_SIT = dw(0.75, -0.35)[:2]; P_DISCO = (DX, -7.5)
CAM_PH = dw(4.1, -0.3, 1.6)
BURG = dw(0.98)[:2] + (0.57,); T_SIT = dw(1.35, -0.75)[:2]; T_RUN = dw(1.1, -0.2)[:2]; HAT_REST = dw(1.45, 0.25)[:2] + (0.0,); COLLAR_REST = dw(0.95, -0.55)[:2] + (0.04,)
COP0 = dw(4.3, -0.5)[:2]; COP1 = dw(1.9, -0.15)[:2]; TR0 = (5.3, -1.9); TROUT = (10.5, -1.75)
G_POS = (DX + 0.1, -5.75); TB_DJ = (DX, 4.9, 1.45)
ARMS_DOWN = dict(aL=(-0.14, 0, -1), aR=(0.14, 0, -1))
CART.location = (BURG[0], BURG[1], 0.0); CART.rotation_euler = (0, 0, EYAW)
def head_to(p, yaw, c, lim=1.3):
    """rotazione Z della testa per guardare il punto c stando in p con il corpo girato di yaw."""
    fx_, fy_ = math.sin(yaw), -math.cos(yaw); dx, dy = c[0] - p[0], c[1] - p[1]; a_ = math.atan2(fx_ * dy - fy_ * dx, fx_ * dx + fy_ * dy); return max(-lim, min(lim, a_))

def suck(t, t0, t1, p0, h, hop=0.0):
    """risucchio nella porticina: da p0 (a terra, scala 1) al centro della porticina (scala quasi zero). Restituisce (posizione, scala)."""
    u = min(1.0, max(0.0, (t - t0) / (t1 - t0))); e = u * u * (3 - 2 * u); s = max(0.02, 1 - e ** 1.7)                    # resta grande a lungo, rimpicciolisce solo vicino alla porticina
    q = (DOORW[0] + DN[0] * 0.03, DOORW[1] + DN[1] * 0.03, DOORW[2] - 0.5 * h * s)
    p = lerp((p0[0], p0[1], p0[2] if len(p0) > 2 else 0.0), q, e)
    return (p[0], p[1], p[2] + hop * math.sin(PI * u)), s

def pp(t):
    """Pippo: posizione, inclinazione in avanti, direzione, scala, braccia, testa, anche."""
    YD = yaw_to(P_DOOR, DOORW); YB = yaw_to(P_DOOR, BURG)
    S_ = dict(loc=(P_DOOR[0], P_DOOR[1], 0.0), lean=0.0, yaw=YD, s=1.0, head=(0, 0, 0), hL=0.0, hR=0.0, **ARMS_DOWN)
    tap = 0.25 * max(0.0, math.sin(t * 9.0))
    if t < 3.3:                                                                                   # hook: mani sulla testa mentre il camion gli entra nella moglie
        k = 0.03 * math.sin(t * 30)
        S_.update(yaw=YD + 0.5 * (1 - ramp(t, 0.3, 2.0)), aL=(-0.42 + k, -0.2, 0.9), aR=(0.42 - k, -0.2, 0.9), head=(-0.1, 0, 0), lean=0.1 * ramp(t, 2.0, 2.8))
    elif t < T_RESTART:                                                                           # si sporge sulla porticina che sbatte, poi guarda in camera
        u = ramp(t, 4.6, 4.9)
        S_.update(lean=0.42 - 0.2 * u, aL=(-0.3, -0.5, -0.8), aR=(0.3, -0.5, -0.8), head=(-0.2 * u, 0, u * head_to(P_DOOR, YD, dw(1.6, 1.1))))
    elif t < 8.7:                                                                                 # aspetta: guarda il polso, batte il piede
        S_.update(aL=(-0.05, -0.85, 0.42), head=(0.32, 0, 0.12), hR=-tap)
    elif t < T_BURG - 0.25:                                                                       # bussa
        u = ramp(t, 8.7, 9.1); kn = 0.16 * math.sin((t - T_KNOCK) * 26) if T_KNOCK < t < T_KNOCK + 0.72 else 0.0; back = ramp(t, T_OCC, T_OCC + 0.2)
        S_.update(lean=0.32 * u - 0.42 * back, aR=(0.1, -1.0, -0.2 + kn) if back < 0.5 else (0.45, -0.3, 0.85), aL=ARMS_DOWN['aL'] if back < 0.5 else (-0.45, -0.3, 0.85))
    elif t < T_TUMBO - 0.15:                                                                      # il panino: lo spinge verso la porticina, poi resta a mani vuote
        gone = ramp(t, T_PULL + 0.45, T_PULL + 0.7)
        S_.update(yaw=YB + (YD - YB) * gone, lean=0.16 * (1 - gone), aL=lerp((-0.3, -1.0, -0.12), (-0.5, -0.7, 0.35), gone), aR=lerp((0.3, -1.0, -0.12), (0.5, -0.7, 0.35), gone))
    elif t < T_TNT - 0.1:                                                                         # manda dentro Tumbo: indica la porticina
        S_.update(aR=(0.08, -1.0, 0.0 + 0.06 * math.sin(t * 14)), aL=(-0.5, 0.0, -0.85), head=(0, 0, head_to(P_DOOR, YD, T_SIT) * (1 - ramp(t, T_TUMBO + 0.3, T_TUMBO + 0.6))))
    elif t < T_POL - 0.1:                                                                         # Tumbo non torna: braccia conserte, batte il piede, poi guarda il collare per terra
        dn = ramp(t, T_TNT + 0.6, T_TNT + 0.85)
        S_.update(aL=(-0.62, 0.12, -0.75), aR=(0.62, 0.12, -0.75), hR=-tap * (1 - dn), head=(0.45 * dn, 0, dn * head_to(P_DOOR, YD, COLLAR_REST)))
    elif t < T_COP - 0.15:                                                                        # al telefono con la polizia (dietro, Eleonora legge)
        y_ = yaw_to(P_PH, CAM_PH); S_.update(loc=(P_PH[0], P_PH[1], 0), yaw=y_ + 0.25, aR=(0.5, -0.62, 0.6), aL=(-0.55, -0.35 + 0.2 * math.sin(t * 11), 0.1), head=(0.0, 0, -0.2))
    elif t < T_NT2 - 0.15:                                                                        # fa strada all'agente
        S_.update(aR=(0.3, -0.95, 0.05), aL=(-0.3, -0.95, 0.05), head=(0, 0, head_to(P_DOOR, YD, COP1) * (1 - ramp(t, T_COP + 0.3, T_COP + 0.6))))
    elif t < T_POMP - 0.1:                                                                        # non torna: mano sulla faccia
        S_.update(aR=(-0.12, -0.7, 0.66), head=(0.28, 0, 0))
    elif t < T_TRUCK - 0.2:                                                                       # al telefono con i pompieri, urlando
        k = 0.25 * math.sin(t * 16); y_ = yaw_to(P_PH, CAM_PH)
        S_.update(loc=(P_PH[0], P_PH[1], 0), yaw=y_ - 0.15, aR=(0.5, -0.62, 0.6), aL=(-0.75, -0.3, 0.55 + k), head=(-0.12, 0, 0.1), lean=0.1)
    elif t < T_PIPPO - 0.25:                                                                      # il camion sfonda il muro: Pippo salta di lato
        k = 0.03 * math.sin(t * 30); j = 0.3 * abs(math.sin((t - T_TRUCK) * 7)) * (1 - ramp(t, T_TRUCK, T_TRUCK + 1.0)); u = ramp(t, T_TRUCK + 0.5, T_TRUCK + 1.3)
        S_.update(loc=(P_AWAY[0], P_AWAY[1], j) if t < T_INDOV - 0.14 else (P_DOOR[0], P_DOOR[1], 0), yaw=yaw_to(P_AWAY, (6.0, -1.7)) * (1 - u) + yaw_to(P_AWAY, DOORW) * u if t < T_INDOV - 0.14 else YD,
                  aL=(-0.42 + k, -0.2, 0.9), aR=(0.42 - k, -0.2, 0.9))
    elif t < T_BLACK:                                                                             # allora entra Pippo: si rimbocca le maniche e si tuffa nella porticina
        if t < T_DIVE: u = ramp(t, T_PIPPO - 0.25, T_DIVE); S_.update(lean=0.3 * u, aL=(-0.3, -0.9, 0.35 * u), aR=(0.3, -0.9, 0.35 * u))
        else:
            l, s = suck(t, T_DIVE, T_P_IN, P_DOOR, 1.9, hop=0.3); u = ramp(t, T_DIVE, T_P_IN); S_.update(loc=l, s=s, lean=0.3 + 1.0 * u, aL=(-0.2, -0.6, 0.8), aR=(0.2, -0.6, 0.8))
    elif t < T_DISCO0:                                                                            # nel tunnel di luci: vola all'indietro, braccia in alto, gambe che scalciano
        u = (t - T_BLACK) / (T_DISCO0 - T_BLACK); y = TUN_Y0 + (TUN_Y1 - TUN_Y0) * u
        S_.update(loc=(TUN_X, y, TUN_Z + 0.12 * math.sin(t * 13)), yaw=PI + 0.35 * math.sin(t * 7), lean=-0.3, hL=0.6 * math.sin(t * 19), hR=-0.6 * math.sin(t * 19),
                  aL=(-0.55, -0.25, 0.8 + 0.15 * math.sin(t * 23)), aR=(0.55, -0.25, 0.8 - 0.15 * math.sin(t * 23)), head=(-0.2, 0, 0))
    elif t < T_END:                                                                               # in discoteca, davanti alla corda di velluto
        drop = ramp(t, T_LIST + 0.35, T_LIST + 0.7)
        S_.update(loc=(P_DISCO[0], P_DISCO[1], 0), yaw=PI, aL=lerp((-0.3, -0.25, -0.9), (-0.14, 0.05, -1), drop), aR=lerp((0.3, -0.25, -0.9), (0.14, 0.05, -1), drop), head=(0.3 * drop, 0, 0.25 * math.sin(t * 2.2) * (1 - ramp(t, T_BOUNCER, T_BOUNCER + 0.3))))
    elif t < T_WALK:                                                                              # cacciato: fuori dalla porticina chiusa, a testa bassa
        S_.update(yaw=yaw_to(P_DOOR, dw(2.4, 1.65)) - 0.25, head=(0.38, 0, 0.0), aL=(-0.1, 0.08, -1), aR=(0.1, 0.08, -1))
    elif t < T_STAND:                                                                             # il Pippo gigante arriva camminando verso la porticina gigante
        u = ramp(t, T_WALK, T_STAND - 0.05); p0 = dw(1.2, -3.2)[:2]; p = lerp(p0, P_DOOR, u); st = math.sin((t - T_WALK) * 11)
        S_.update(loc=MG((p[0], p[1], 0.04 * abs(st))), s=G, yaw=yaw_to(p0, P_DOOR), hL=0.45 * st, hR=-0.45 * st, aL=(-0.15, 0.35 * st, -1), aR=(0.15, -0.35 * st, -1))
    else:                                                                                         # bussa tre volte, poi esce il cartello: stupore
        kn = sum(0.2 * math.sin(min(1.0, max(0.0, (t - k_) / 0.16)) * PI) for k_ in T_KN2); back = ramp(t, T_SIGN2, T_SIGN2 + 0.15)
        S_.update(loc=MG((P_DOOR[0], P_DOOR[1], 0)), s=G, lean=0.3 * (1 - back) - 0.3 * back, aR=(0.1, -1.0, -0.2 + kn) if back < 0.5 else (0.45, -0.3, 0.85), aL=ARMS_DOWN['aL'] if back < 0.5 else (-0.45, -0.3, 0.85))
    return S_

def tbp(t):
    """Tumbo: (posizione, yaw, scala, zampe davanti alzate 0..1)"""
    if t < T_TUMBO + 0.25: return (T_SIT[0], T_SIT[1], 0.0), yaw_to(T_SIT, DOORW), 1.0, 0.0
    if t < T_DISCO0:
        if t < T_TUMBO + 0.55:
            u = ramp(t, T_TUMBO + 0.25, T_TUMBO + 0.55); p = lerp(T_SIT, T_RUN, u); return (p[0], p[1], 0.12 * abs(math.sin(u * PI * 2))), yaw_to(T_SIT, DOORW), 1.0, 0.0
        l, s = suck(t, T_TUMBO + 0.55, T_T_IN, T_RUN, 0.75, hop=0.45); return l, yaw_to(T_SIT, DOORW), s, 0.0
    bob = 0.05 * abs(math.sin((t - T_DISCO0) * PI * 2.0))
    return (TB_DJ[0], TB_DJ[1], TB_DJ[2] + bob), 0.0, 1.25, 1.0

def copp(t):
    """agente: (posizione, yaw, scala, passo -1..1, ballo 0/1)"""
    if t < T_DISCO0:
        if t < T_COP + 0.3:
            u = ramp(t, T_COP - 0.15, T_COP + 0.3); p = lerp(COP0, COP1, u); return (p[0], p[1], 0.0), yaw_to(COP0, COP1), 1.0, math.sin(t * 20), 0
        l, s = suck(t, T_COP + 0.3, T_C_IN, COP1, 1.9, hop=0.3); return l, yaw_to(COP1, DOORW), s, math.sin(t * 20), 0
    j = abs(math.sin((t - T_DISCO0) * PI * 2.0)); return (COPD[0], COPD[1], 0.045 + 0.16 * j), 0.25 * math.sin((t - T_DISCO0) * PI * 1.0), 1.0, 0.0, 1

def trp(t):
    """camion: (posizione, yaw, scala)"""
    if t < T_HOOK_IN + 0.1: l, s = suck(t, -0.5, T_HOOK_IN, TR0, TRUCK_H); return l, yaw_to(TR0, DOORW), s
    if t < T_DISCO0:
        if t < T_TRUCK + 0.15: u = (t - (T_TRUCK - 0.25)) / 0.4; p = lerp(TROUT, TR0, min(1.0, max(0.0, u))); return (p[0], p[1], 0.0), yaw_to(TROUT, TR0), 1.0
        l, s = suck(t, T_TRUCK + 0.15, T_TR_IN, TR0, TRUCK_H); return l, yaw_to(TR0, DOORW), s
    return TRUCKD, TRUCKDYAW, 1.0

def burgp(t):
    """panino: (posizione, scala xyz, yaw)"""
    if t < T_DISCO0:
        if t < T_PULL: gr = 0.03 * ramp(t, T_GRAB, T_GRAB + 0.2) * math.sin(t * 40) * (1 - ramp(t, T_GRAB + 0.5, T_GRAB + 0.7)); return (BURG[0] + gr * DN[0], BURG[1] + gr * DN[1], BURG[2]), (1, 1, 1), EYAW
        u = ramp(t, T_PULL, T_PULL + 0.7); e = u * u; q = (DOORW[0], DOORW[1], DOORW[2] - 0.04)
        sq = max(0.03, 1 - 0.97 * u); st = 1.0 + 0.9 * math.sin(PI * u)                         # si schiaccia e si allunga verso la porticina, come gomma
        p = lerp(BURG, q, e); return p, (sq, sq * st if u < 0.98 else sq, sq), EYAW
    return BURGD, (1.25, 1.25, 1.25), 0.4

def door_open(t):
    """apertura del battente (0 chiuso, 1 spalancato)."""
    o = 1.0 - ramp(t, T_SLAM - 0.12, T_SLAM) if t < T_RESTART else 0.0
    for (a, b) in ((T_HAND - 0.25, T_PULL + 0.78), (T_TUMBO + 0.4, T_T_IN + 0.15), (T_COP + 0.15, T_C_IN + 0.12), (T_TRUCK - 0.1, T_TR_IN + 0.12), (T_PIPPO + 0.15, T_P_IN + 0.05)):
        if a <= t <= b + 0.12: o = max(o, ramp(t, a, a + 0.14) * (1 - ramp(t, b, b + 0.1)))
    return o
def sign_on(t):
    if t < T_RESTART: u = (t - T_SIGN0) / 0.22
    else: u = (t - T_OCC) / 0.22
    if u <= 0: return 0.0001
    return 1.0 + 0.35 * math.sin(min(1.0, u) * PI) if u < 1 else 1.0
FLIPS = (7.6, 13.6, 18.5, 21.8, T_INDOV + 0.05, 30.0, T_END + 0.55)
def page(t):
    a = 0.25
    for tf in FLIPS:
        if tf <= t < tf + 0.4: a = 0.25 + 2.64 * ramp(t, tf, tf + 0.36)
    return a

# ======================= chiavi =======================
def K(o, f, loc=None, rot=None, scale=None):
    if loc is not None: o.location = loc; o.keyframe_insert('location', frame=f)
    if rot is not None: o.rotation_euler = rot; o.keyframe_insert('rotation_euler', frame=f)
    if scale is not None: o.scale = scale if isinstance(scale, (tuple, list)) else (scale,) * 3; o.keyframe_insert('scale', frame=f)
GSH = {nm: GU['shoulder' + nm] for nm in 'LR'}
# reazioni di Pippo: allungamento (>0) o schiacciamento (<0) per mezzo secondo. Anticipazione: si schiaccia prima di tuffarsi
REAZIONI = [(0.05, 0.12), (T_SLAM, -0.1), (T_OCC, 0.14), (T_PULL + 0.5, 0.14), (T_TNT + 0.7, 0.1), (T_NT2, -0.12), (T_TRUCK, 0.18), (T_DIVE - 0.3, -0.14),
            (T_DISCO0, 0.16), (T_BOUNCER + 0.2, 0.08), (T_LIST + 0.35, -0.16), (T_END, -0.1), (T_SIGN2, 0.16)]
for f in range(1, NF + 1):
    t = (f - 1) / FPS
    s = pp(t); sq = sum(a_ * math.sin(PI * min(1.0, (t - e_) / 0.3) * 1.5) * math.exp(-(t - e_) * 4.0) for (e_, a_) in REAZIONI if 0.0 <= t - e_ < 0.9)
    K(P['root'], f, s['loc'], (s['lean'], 0, s['yaw']), (s['s'] * (1 - 0.5 * sq), s['s'] * (1 - 0.5 * sq), s['s'] * (1 + sq)))
    for nm, k in (('L', 'aL'), ('R', 'aR')):
        sh = P['shoulder' + nm]; sh.rotation_quaternion = qdir(s[k]); sh.keyframe_insert('rotation_quaternion', frame=f)
        K(P['hip' + nm], f, rot=(s['h' + nm], 0, 0))
    K(P['head'], f, rot=s['head'])
    # Tumbo
    l, yw, sc, up = tbp(t); K(Tb['root'], f, l, (0.0 if up < 0.5 else -0.55, 0, yw), 0.75 * sc)
    K(Tb['tail'], f, rot=(-1.0 + 0.3 * math.sin(t * 9), 0, 0.6 * math.sin(t * 14)))
    scr = math.sin((t - T_DISCO0) * PI * 4.0)
    for nm, sg in (('L', 1), ('R', -1)): K(Tb['legF' + nm], f, rot=(up * (-1.25 + 0.3 * sg * scr), 0, 0))
    K(Tb['head'], f, rot=(up * 0.18 * math.sin((t - T_DISCO0) * PI * 2.0), 0, up * 0.3 * math.sin((t - T_DISCO0) * PI * 1.0)))
    # agente
    l, yw, sc, wk, dance = copp(t); K(COP['root'], f, l, (0, 0, yw), sc)
    for nm, sg in (('L', 1), ('R', -1)):
        K(COP['hip' + nm], f, rot=(0.6 * sg * wk, 0, 0))
        arm = (-2.25, 0, 0) if (nm == 'R' and not dance) else ((-2.6 + 0.5 * sg * math.sin((t - T_DISCO0) * PI * 2.0), 0, 0) if dance else (0.7 * sg * wk, 0, 0))
        K(COP['shoulder' + nm], f, rot=arm)
    # camion
    l, yw, sc = trp(t); K(TRUCK, f, l, (0, 0, yw), sc)
    blink = int(t * 6) % 2 == 0; sir.color = (1.0, 0.1, 0.05) if blink else (0.1, 0.3, 1.0); sir.energy = 60.0 * sc * sc if t < T_DISCO0 else 220.0
    sir.keyframe_insert('color', frame=f); sir.keyframe_insert('energy', frame=f)
    # panino
    l, sc, yw = burgp(t); K(BURGER, f, l, (0, 0, yw), tuple(BURG_H / 0.85 * v for v in sc))
    # porticina, cartello, luce, rivista, manina
    op = door_open(t); K(D['leaf'], f, rot=(0, 0, -1.95 * op)); K(D['sign'], f, scale=sign_on(t))
    D['glow'].data.energy = 9.0 * op; D['glow'].data.keyframe_insert('energy', frame=f)
    K(MAGP, f, rot=(0, 0, page(t)))
    out = ramp(t, T_HAND, T_HAND + 0.5) * (1 - ramp(t, T_PULL, T_PULL + 0.5)); wv = 0.25 * math.sin(t * 12) * (1 - ramp(t, T_GRAB - 0.1, T_GRAB + 0.1))
    K(HAND, f, loc=(0, 0.26 - 0.30 * out, 0.0), rot=(0, 0, wv), scale=(1.0, 1.0 + 0.75 * out, 1.0))
    # collare e berretto: volano fuori dalla porticina e restano li'
    if t < T_RESTART or t >= T_TNT + 1.0: K(COLLAR, f, COLLAR_REST, (0, 0, 0.6))
    elif t >= T_TNT + 0.38:
        u = ramp(t, T_TNT + 0.4, T_TNT + 0.95); p = lerp(dw(0.1), COLLAR_REST, u); K(COLLAR, f, (p[0], p[1], p[2] + 0.6 * math.sin(PI * u)), (2.0 * (1 - u) * 6, 0, 0.6))
    if t < T_RESTART or t >= T_C_IN + 0.6: K(HAT, f, HAT_REST, (0.0, 0.06 * math.sin(t * 7) * max(0.0, 1 - (t - T_C_IN - 0.6) / 1.2) if t >= T_C_IN else 0.0, 0.5))
    elif t >= T_C_IN - 0.27:
        u = ramp(t, T_C_IN - 0.25, T_C_IN + 0.55); p = lerp(dw(0.12), HAT_REST, u); K(HAT, f, (p[0], p[1], p[2] + 0.35 * math.sin(PI * u)), (0.0, 3.0 * (1 - u), 0.5 + 4 * (1 - u)))
    # Gualtiero buttafuori: braccia conserte, poi mostra la lista e fa no con la testa
    if t >= T_BOUNCER - 0.1:
        u = ramp(t, T_LIST - 0.15, T_LIST + 0.2); no = 0.4 * math.sin((t - T_LIST) * 9.0) * ramp(t, T_LIST + 0.15, T_LIST + 0.3)
        K(GU['root'], f, (G_POS[0], G_POS[1], 0), (0, 0, 0)); K(GU['head'], f, rot=(0.08, 0, no))
        K(GSH['L'], f, rot=(-0.95, 0, 0.85)); K(GSH['R'], f, rot=(-0.95 - 0.55 * u, 0, -0.85 + 0.75 * u))
    for k, f_ in enumerate(FF):
        j = abs(math.sin((t - T_DISCO0) * PI * 2.0 + k)); K(f_['root'], f, (f_['root'].location.x, f_['root'].location.y, 0.14 * j), (0, 0, PI + (0.9 if k else -0.7)))
        for nm, sg in (('L', 1), ('R', -1)): K(f_['shoulder' + nm], f, rot=(-2.7 + 0.4 * sg * math.sin((t - T_DISCO0) * PI * 2.0), 0, 0))
    K(BALL, f, rot=(0, 0, t * 0.9))
    if T_BLACK - 0.1 <= t < T_DISCO0 + 0.1:
        u_ = (t - T_BLACK) / (T_DISCO0 - T_BLACK); K(LTUNO, f, (TUN_X + 0.4, TUN_Y0 + (TUN_Y1 - TUN_Y0) * u_ + 1.3, TUN_Z + 2.0)); LTUN.color = _tc[int(t * 12) % 4]; LTUN.keyframe_insert('color', frame=f)
    K(DUST, f, (0.9 + 0.08 * math.sin(t * 0.5), -0.1 + 0.06 * math.cos(t * 0.4), 1.6 + 0.05 * math.sin(t * 0.7)), (0, 0, t * 0.05))
    K(D2['sign'], f, scale=(0.0001 if t < T_SIGN2 else (1.0 + 0.35 * math.sin(min(1.0, (t - T_SIGN2) / 0.22) * PI))))
    K(MAGP2, f, rot=(0, 0, 0.25 + 2.64 * ramp(t, T_GIANT + 0.55, T_GIANT + 0.9)))
    SOLE.data.energy = 0.0 if t < T_GIANT - 0.05 else 4.2; SOLE.data.keyframe_insert('energy', frame=f)
    for k, p_ in enumerate(PLAT): K(p_, f, rot=(0, 0, t * 3.4 * (1 if k else -1) + 0.6 * math.sin(t * 9)))
MEL.location = MELD; BURGER.rotation_mode = 'XYZ'

# neonati: ogni neonato ha un rimbalzo e una torsione su un ciclo di 12 fotogrammi che si ripete (modificatore CYCLES)
for (o, p, yw, ph, amp) in BABIES:
    o.rotation_mode = 'XYZ'
    for (df, dz, dr) in ((0, 0.0, -0.3), (6, amp, 0.0), (12, 0.0, 0.3), (18, amp, 0.0), (24, 0.0, -0.3)):
        o.location = (p[0], p[1], p[2] + dz); o.rotation_euler = (0, 0, yw + dr); o.keyframe_insert('location', frame=1 + ph + df); o.keyframe_insert('rotation_euler', frame=1 + ph + df)
    for fc in all_fcurves(o): fc.modifiers.new('CYCLES')
    o.hide_render = True; o.keyframe_insert('hide_render', frame=1); o.hide_render = False; o.keyframe_insert('hide_render', frame=fr(T_DISCO0)); o.hide_render = True; o.keyframe_insert('hide_render', frame=fr(T_END))

# mattonelle della pista: i quattro colori si accendono a turno
for i, m in enumerate(Q['tile']):
    b = m.node_tree.nodes['Principled BSDF']
    for k in range(int((T_END - T_DISCO0) * 2) + 2):
        b.inputs['Emission Strength'].default_value = 1.3 if (k + i) % 4 < 2 else 0.2; b.inputs['Emission Strength'].keyframe_insert('default_value', frame=fr(T_DISCO0 + k * 0.5))
    for fc in all_fcurves(m.node_tree):
        for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'
# il cielo si spegne in discoteca (in Eevee la luce del cielo entra anche nelle stanze chiuse)
for n in BGN:
    for (t_, v) in ((0.0, LCFG['cielo']), (T_BLACK - 0.05, LCFG['cielo']), (T_BLACK, 0.015), (T_END - 0.05, 0.015), (T_END, LCFG['cielo']), (T_GIANT - 0.05, LCFG['cielo']), (T_GIANT, 0.9)):
        n.inputs['Strength'].default_value = v; n.inputs['Strength'].keyframe_insert('default_value', frame=fr(t_))
for fc in all_fcurves(WORLD.node_tree):
    for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'

# ======================= espressioni =======================
_last = {}
def _ex(key, fn, t, k):
    if key in _last and t - 0.06 > _last[key][1]: fn(fr(t - 0.06), **_last[key][0])
    fn(fr(t), **k); _last[key] = (k, t)
def pex(t, **k): _ex('p', lambda f, **kk: pippo.express(P, f, **kk), t, k)
def tex(t, **k): _ex('t', lambda f, **kk: tumbo.tumbo_express(Tb, f, **kk), t, k)
def gx(t, **k): _ex('g', lambda f, **kk: props009.gex(GU, f, **kk), t, k)
# espressioni ESAGERATE nei momenti importanti (stupore, panico, soddisfazione, confusione), con una mezza espressione opposta prima (anticipazione)
STUPORE = dict(brow=-1.0, brow_lift=1.0, mouth_open=1.0, smile=-0.2); PANICO = dict(brow=-1.0, brow_lift=1.0, mouth_open=1.0, smile=-0.8, look=(0.5, 0.3))
SODDISFATTO = dict(brow=0.7, smile=1.0, mouth_open=0.35, brow_lift=0.3); CONFUSO = dict(brow=-0.6, brow_lift=0.7, smile=-0.5, mouth_open=0.2, look=(0.7, 0.5))
FURBO = dict(brow=0.9, smile=0.9, look=(0.6, 0)); DELUSO = dict(brow=-1.0, smile=-1.0, look=(0, -0.8)); NEUTRO = dict(brow=0.2, smile=0.0)
pex(0.0, **PANICO); pex(1.6, **dict(PANICO, look=(0.8, -0.2))); pex(2.75, **STUPORE)
pex(T_SLAM - 0.02, brow=0.8, smile=-0.8, mouth_open=0.0); pex(T_SLAM + 0.35, **CONFUSO); pex(4.6, **STUPORE)
pex(T_RESTART, brow=0.4, smile=-0.4, look=(0, -0.4)); pex(7.4, brow=0.5, smile=-0.6, look=(-0.6, 0.6))
pex(8.85, **SODDISFATTO); pex(T_OCC - 0.1, smile=0.9, brow=0.6); pex(T_OCC + 0.04, **STUPORE); pex(T_OCC + 0.7, **CONFUSO)
pex(T_BURG - 0.2, **dict(SODDISFATTO, smile=1.0, mouth_open=0.6)); pex(T_GRAB, **CONFUSO); pex(T_PULL + 0.45, **PANICO); pex(T_PULL + 0.9, **DELUSO)
pex(T_TUMBO - 0.1, **FURBO); pex(T_TNT - 0.05, brow=0.3, smile=0.2, look=(0.3, -0.3)); pex(T_TNT + 0.7, **CONFUSO)
for k in range(8): pex(T_POL - 0.05 + 0.14 * k, brow=0.9, smile=-0.2, mouth_open=1.0 if k % 2 == 0 else 0.2)
pex(T_COP - 0.1, **SODDISFATTO); pex(T_NT2 - 0.05, **DELUSO)
for k in range(9): pex(T_POMP - 0.05 + 0.13 * k, brow=1.0, smile=-0.6, mouth_open=1.0 if k % 2 == 0 else 0.35)
pex(T_TRUCK - 0.15, **PANICO); pex(T_INDOV, **CONFUSO); pex(T_PIPPO - 0.2, brow=1.0, smile=-0.3, mouth_open=0.0); pex(T_DIVE - 0.3, brow=1.0, smile=0.4, mouth_open=0.0)
pex(T_DIVE, **dict(PANICO, smile=0.2)); pex(T_BLACK, **PANICO); pex(T_DISCO0, **STUPORE); pex(T_REVEAL, **dict(STUPORE, smile=0.6))
pex(T_BOUNCER + 0.2, **dict(SODDISFATTO, brow_lift=0.8, mouth_open=0.5)); pex(T_LIST + 0.35, **DELUSO); pex(T_END, **DELUSO)
pex(T_STAND, **SODDISFATTO); pex(T_SIGN2 - 0.05, smile=0.9, brow=0.6); pex(T_SIGN2 + 0.05, **STUPORE)
tex(T_RESTART, tongue=0.0, eye_open=0.6); tex(7.2, tongue=1.0, eye_open=0.1); tex(8.2, tongue=0.0, eye_open=0.7); tex(T_TUMBO + 0.2, tongue=0.9, eye_scale=1.15, brow=0.3)
tex(T_DISCO0, tongue=1.0, eye_scale=1.2, brow=0.5)
gx(T_BOUNCER, brow=0.7, mouth=0.1); gx(T_LIST, brow=0.9, mouth=0.35)
# Eleonora: impassibile, legge; solo un sorrisetto furbo quando la porticina si chiude e alla fine. Mai piega/schiaccia: la porticina e' attaccata al corpo
def zx(Zr, t, **k): eleonora.express(Zr, fr(t), **k)
for (t_, k) in ((0.0, dict(smile=0.3)), (T_SLAM + 0.15, dict(smile=0.9, brow=0.6, look=(0.8, 0))), (T_RESTART, dict(smile=0.3, look=(0, -0.6))), (T_INDOV - 0.1, dict(smile=0.3, look=(0, -0.6))),
                (T_INDOV + 0.1, dict(smile=0.9, brow=0.7, look=(0.9, 0))), (T_PIPPO, dict(smile=0.3, look=(0, -0.6))), (T_END + 0.2, dict(smile=0.9, brow=0.7, look=(0.9, 0)))):
    zx(Z, t_, **k)
for (t_, k) in ((0.0, dict(smile=0.3, look=(0, -0.6))), (T_KN2[0], dict(smile=0.3, look=(0, -0.6))), (T_KN2[0] + 0.1, dict(brow=0.8, smile=-0.6, look=(0.8, 0))), (T_SIGN2, dict(smile=0.9, brow=0.7, look=(0.9, 0)))):
    zx(Z2, t_, **k)

# ======================= effetti (immagini della libreria: sbuffi, stelline, fumetti, fasci di luce) =======================
FXC = prc
def fx(name, pos, w, t0, dur, **k): return A.effetto(name, posizione=pos, larghezza=w, animazione=(fr(t0), int(dur * FPS)), collezione=FXC, **k)
HEADP = lambda p, dz=2.3: (p[0], p[1], dz)
# risucchi nella porticina: lampo viola e stelline
for (t_, big) in ((T_HOOK_IN - 0.1, 0.9), (T_PULL + 0.6, 0.5), (T_T_IN - 0.1, 0.5), (T_C_IN - 0.1, 0.6), (T_TR_IN - 0.1, 0.9), (T_P_IN - 0.08, 0.7)):
    fx('particelle/magic_05', dw(0.12), big, t_, 0.4, colore=(1.0, 0.35, 0.9), luce=2.2); fx('particelle/twirl_01', dw(0.1), big * 0.9, t_ - 0.15, 0.45, colore=(0.5, 0.9, 1.0), luce=1.6)
# la porticina che sbatte
for t_ in (T_SLAM, T_PULL + 0.9, T_T_IN + 0.27, T_C_IN + 0.24): fx('sbuffo_bianco/whitepuff03', dw(0.1, 0.0, DOORW[2] - 0.12), 0.34, t_, 0.4, opacita=0.8)
# note musicali che scappano dalla porticina (indizio)
for (t_, dx) in ((T_HAND + 0.35, 0.42), (T_TUMBO + 0.75, 0.42), (T_COP + 0.5, 0.42), (T_END + 0.2, 0.42)): fx('emoticon/music', dw(0.3, dx, DOORW[2] - 0.02), 0.24, t_, 0.9)
# fumetti sopra la testa di Pippo
fx('emoticon/question', dw(0.75, -0.35, 2.02), 0.36, T_OCC + 0.12, 0.8)
fx('emoticon/dots3', (P_DOOR[0], P_DOOR[1], 2.3), 0.42, T_TNT + 0.05, 0.75)
fx('emoticon/exclamations', (P_AWAY[0], P_AWAY[1], 2.55), 0.5, T_TRUCK + 0.1, 0.9)
# il camion sfonda il muro: polvere e calcinacci
for k, (dy, dz, w_, dt) in enumerate(((-1.2, 1.0, 3.2, 0.0), (0.6, 1.6, 3.6, 0.04), (-0.2, 2.2, 3.0, 0.1), (-2.0, 0.8, 2.6, 0.12), (1.2, 0.7, 2.4, 0.16))):
    fx('sbuffo_bianco/whitepuff%02d' % (k * 3), (6.2, -1.7 + dy, dz), w_, T_TRUCK - 0.12 + dt, 0.9, colore=(0.95, 0.9, 0.82), opacita=0.9)
fx('particelle/dirt_02', (5.6, -1.7, 1.4), 3.4, T_TRUCK - 0.05, 0.6, colore=(0.75, 0.45, 0.3)); fx('particelle/dirt_02', (5.2, -0.9, 0.9), 2.4, T_TRUCK + 0.05, 0.55, colore=(0.8, 0.78, 0.7))
A.effetto('sbuffo_bianco/whitepuff07', posizione=(6.4, -2.6, 0.5), larghezza=1.8, colore=(0.95, 0.9, 0.82), opacita=0.35, collezione=FXC).name = 'PolvereHook'
show(bpy.data.objects['PolvereHook'], [(0.0, 3.3)])
# discoteca: fasci di luce dal soffitto, bagliori, stelline sulla palla a specchi, croce rossa del buttafuori
DISCOFX = []
for k, (x, y, col, rot) in enumerate(((-3.6, 0.5, (1.0, 0.2, 0.8), 12), (-1.3, 2.2, (0.2, 0.9, 1.0), -8), (1.4, 2.0, (1.0, 0.85, 0.2), 9), (3.7, 0.4, (0.6, 0.3, 1.0), -14), (-2.4, -3.0, (0.2, 0.9, 1.0), 6), (2.6, -3.1, (1.0, 0.2, 0.8), -6))):
    DISCOFX.append(A.effetto('particelle/flare_01', posizione=(DX + x, y, 6.2), larghezza=2.0, colore=col, luce=2.0, opacita=0.9, collezione=FXC))
for k in range(10):
    a = k * 0.63; DISCOFX.append(A.effetto('particelle/star_0%d' % (1 if k % 2 else 8), posizione=(DX + 0.75 * math.cos(a), -1.0 + 0.75 * math.sin(a), 4.4 + 0.45 * math.sin(a * 2.3)), larghezza=0.5, luce=2.0, collezione=FXC))
DISCOFX.append(A.effetto('luci/circle_a_streaks', posizione=(DX, 6.6, 3.6), larghezza=4.2, colore=(1.0, 0.25, 0.85), luce=1.2, opacita=0.7, collezione=FXC))
for o in DISCOFX: show(o, [(T_DISCO0, T_END)])

fx('emoticon/music', (TB_DJ[0] + 0.75, TB_DJ[1] - 0.3, 2.9), 0.36, T_DJ + 0.2, 1.2)

# ======================= camera =======================
EHEAD = tuple(ZM @ Vector((0, -0.1, 0.68)))
def gz(z, n=0.0, t=0.0): return dw(n, t, z)
def trk(t):                                                                                     # il camion dell'hook e quello vero: la camera gli sta dietro
    return trp(t)[0]
SCOSSE = [(0.0, 0.035), (T_SLAM, 0.03), (T_TRUCK + 0.02, 0.09), (T_REVEAL, 0.06), (T_DJ + 0.2, 0.05), (T_GUAL - 0.1, 0.03)] + [(k_, 0.03 * G) for k_ in T_KN2]
PUGNI = [(T_OCC + 0.02, 0.15), (T_TNT + 0.65, 0.12), (T_NT2, 0.1), (T_DISCO0 + 0.05, 0.12), (T_LIST + 0.3, 0.14), (T_SIGN2, 0.15)]
SHOTS = [  # t0, t1, camera da, a, mira da, a, lente, diaframma
    (0.0, 3.3, (6.1, -4.1, 2.7), (1.7, -1.0, 1.4), (4.2, -1.3, 1.0), dw(0.0, 0.0, 1.0), 24, 9),                      # 01 hook: dietro al camion che entra nella zucchina
    (3.3, T_RESTART, gz(1.4, 2.5, 1.7), gz(1.35, 2.3, 1.55), gz(1.18, 0.15, -0.3), gz(1.2, 0.15, -0.35), 40, 5),         # 02 la porticina sbatte, OCCUPATO, Pippo guarda in camera
    (T_RESTART, 9.0, gz(1.55, 4.3, 2.4), gz(1.45, 3.9, 2.2), gz(0.95, 0.5, -0.4), gz(0.95, 0.5, -0.4), 34, 8),            # 03 Eleonora deve partorire
    (9.0, 11.1, gz(1.35, 2.5, 1.75), gz(1.32, 2.3, 1.6), gz(1.2, 0.2, -0.35), gz(1.22, 0.2, -0.35), 38, 5),           # 04 Pippo bussa. Occupato.
    (11.1, 12.9, gz(1.4, 2.7, 2.5), gz(1.35, 2.5, 2.3), gz(1.05, 0.45, -0.3), gz(1.05, 0.45, -0.3), 34, 6),             # 05 il panino
    (12.9, 16.05, gz(1.15, 0.45, 2.7), gz(1.1, 0.4, 2.5), gz(1.0, 0.36, 0.0), gz(0.98, 0.3, 0.0), 38, 5),             # 06 la manina prende il panino
    (16.05, 17.75, gz(1.4, 3.4, 2.4), gz(1.35, 3.1, 2.2), gz(0.85, 0.7, -0.35), gz(0.9, 0.4, -0.3), 32, 7),             # 07 manda dentro Tumbo
    (17.75, 19.05, gz(1.3, 2.0, 1.4), gz(1.25, 1.9, 1.3), gz(1.2, 0.25, -0.5), gz(1.0, 0.35, -0.45), 38, 5),            # 08 Tumbo non torna
    (19.05, 20.2, CAM_PH, gz(1.6, 3.9, -0.3), (P_PH[0] + 0.25, P_PH[1] + 0.3, 1.5), (P_PH[0] + 0.25, P_PH[1] + 0.3, 1.5), 34, 5),                 # 09 chiama la polizia (dietro Eleonora legge)
    (20.2, 21.3, gz(1.5, 4.2, 2.7), gz(1.45, 3.9, 2.5), gz(1.0, 1.2, -0.3), gz(1.0, 0.5, -0.3), 28, 8),                 # 10 entra un agente
    (21.3, 22.35, gz(1.75, 3.2, 1.1), gz(1.7, 3.0, 1.0), gz(0.3, 1.1, 0.2), gz(0.3, 1.1, 0.2), 36, 6),          # 11 non torna: resta il berretto
    (22.35, 23.6, gz(1.66, 3.7, -0.45), gz(1.66, 3.45, -0.5), (P_PH[0], P_PH[1], 1.62), (P_PH[0], P_PH[1], 1.62), 46, 4),  # 12 chiama i pompieri
    (23.6, 24.45, (-0.2, -1.0, 1.35), (-0.4, -0.9, 1.35), (6.3, -1.7, 1.5), (5.0, -1.6, 1.3), 24, 9),                   # 13 il camion sfonda il muro
    (24.45, 25.3, (4.9, -3.7, 2.4), (2.1, -1.7, 1.5), (3.0, -0.8, 0.9), dw(0.0, 0.0, 1.0), 26, 9),                  # 14 entra tutto il camion
    (25.3, 26.4, gz(1.4, 2.1, 0.35), gz(1.4, 1.9, 0.3), (EHEAD[0], EHEAD[1], EHEAD[2] - 0.22), (EHEAD[0], EHEAD[1], EHEAD[2] - 0.2), 55, 4),  # 15 Indovinate: Eleonora gira pagina
    (26.4, T_BLACK, gz(1.3, 2.7, 2.3), gz(1.25, 2.4, 2.1), gz(1.0, 0.35, -0.3), gz(0.95, 0.3, -0.2), 34, 6),            # 16 allora entra Pippo
    (T_BLACK, T_DISCO0, (TUN_X + 0.35, TUN_Y0 + 2.3, TUN_Z + 1.35), (TUN_X + 0.35, TUN_Y1 + 2.3, TUN_Z + 1.35), (TUN_X, TUN_Y0, TUN_Z + 1.0), (TUN_X, TUN_Y1, TUN_Z + 1.0), 20, 11),                                     # 17 buio
    (T_DISCO0, T_REVEAL, (DX + 0.6, -5.2, 1.66), (DX + 0.5, -5.5, 1.66), (DX, -7.5, 1.6), (DX, -7.5, 1.6), 36, 4),  # 18 Ma che cazzo?
    (T_REVEAL, T_BABIES, (DX - 0.7, -9.1, 2.2), (DX - 0.4, -8.9, 3.3), (DX, -1.0, 1.3), (DX, -0.5, 1.0), 18, 11),       # 19 una discoteca
    (T_BABIES, T_COPD, (DX + 0.7, 2.95, 0.42), (DX + 0.4, 2.85, 0.42), (DX - 0.2, -0.5, 0.32), (DX - 0.4, -0.5, 0.32), 26, 6),  # 20 duecento neonati
    (T_COPD, T_DJ, (COPD[0] - 0.6, COPD[1] - 3.2, 1.25), (COPD[0] - 0.5, COPD[1] - 2.9, 1.25), (COPD[0], COPD[1], 1.2), (COPD[0], COPD[1], 1.25), 34, 6),  # 21 il poliziotto balla
    (T_DJ, T_BOUNCER, (DX + 0.7, 1.3, 2.7), (DX + 0.5, 2.2, 2.6), (TB_DJ[0], TB_DJ[1] - 0.3, 2.0), (TB_DJ[0], TB_DJ[1] - 0.3, 2.05), 38, 6),  # 22 il DJ e' Tumbo
    (T_BOUNCER, T_GUAL, (DX + 0.95, -7.5, 0.5), (DX + 0.9, -7.5, 0.7), (G_POS[0], G_POS[1], 0.25), (G_POS[0], G_POS[1], 1.25), 28, 7),  # 23 all'ingresso, il buttafuori
    (T_GUAL, T_LIST, (G_POS[0] + 0.3, G_POS[1] - 1.7, 1.82), (G_POS[0] + 0.25, G_POS[1] - 1.5, 1.82), (G_POS[0], G_POS[1], 1.8), (G_POS[0], G_POS[1], 1.8), 55, 4),  # 24 Gualtiero
    (T_LIST, T_END, (DX + 0.3, -7.35, 1.78), (DX + 0.32, -7.25, 1.78), (DX + 0.4, -6.3, 1.66), (DX + 0.42, -6.3, 1.64), 30, 8),  # 25 Pippo non e' in lista
    (T_END, T_GIANT, gz(1.4, 2.5, 1.7), gz(1.37, 2.35, 1.6), gz(1.18, 0.15, -0.3), gz(1.2, 0.15, -0.32), 40, 5),
    (T_GIANT, T_STAND, MG(dw(0.9, 0.1, 1.0)), MG(dw(4.6, 1.9, 1.75)), MG(dw(0.0, 0.0, 0.98)), MG(dw(0.0, -0.3, 0.95)), 40, 11),   # la camera si allontana: era tutto dentro un'Eleonora gigante
    (T_STAND, TOTAL + 0.1, MG(gz(1.35, 2.5, 1.75)), MG(gz(1.32, 2.3, 1.6)), MG(gz(1.2, 0.2, -0.35)), MG(gz(1.22, 0.2, -0.35)), 38, 11),   # il Pippo gigante bussa: stessa inquadratura di «Pippo bussa»    # 26 finale: OCCUPATO
]
for f in range(1, NF + 1):
    t = (f - 1) / FPS
    s_ = next((s for s in SHOTS if s[0] <= t < s[1]), SHOTS[-1]); u = (t - s_[0]) / (s_[1] - s_[0])
    if s_[0] == T_GIANT: u = u * u * (3 - 2 * u)                                                 # parte piano, accelera, si ferma piano: niente scia sfocata all'inizio                                                  # allontanamento che parte veloce e rallenta
    cam.location = lerp(s_[2], s_[3], u); tgt.location = lerp(s_[4], s_[5], u); camd.lens = s_[6] if s_[0] != T_GIANT else 40 - 12 * u; camd.dof.aperture_fstop = s_[7]
    if s_[6] >= 36 and s_[0] < T_GIANT: camd.dof.aperture_fstop = min(s_[7], 2.2)                 # primi piani: sfondo piu' sfocato
    for (e_, a_) in SCOSSE:                                                                       # la camera trema sugli impatti
        d_ = t - e_
        if 0 <= d_ < 0.7: k_ = a_ * math.exp(-d_ * 7); cam.location = (cam.location.x + k_ * math.sin(d_ * 67), cam.location.y + k_ * math.sin(d_ * 53 + 1), cam.location.z + k_ * math.sin(d_ * 71 + 2))
    for (e_, a_) in PUGNI:                                                                        # zoom secco sulle reazioni, dentro la stessa inquadratura
        if s_[0] <= e_ <= t < s_[1]: camd.lens = camd.lens * (1 + a_ * (1 - math.exp(-(t - e_) * 16)))
    cam.keyframe_insert('location', frame=f); tgt.keyframe_insert('location', frame=f); camd.keyframe_insert('lens', frame=f); camd.dof.keyframe_insert('aperture_fstop', frame=f)

# alleggerisci il render: nella sala parto spegni tutto quello che sta in discoteca (oggetti e luci), e viceversa. Ombre a meta' risoluzione (non si vede la differenza).
bpy.context.view_layer.update()
def centro_x(o):
    if o.type == 'MESH' and o.data and len(o.data.vertices): return sum((o.matrix_world @ Vector(c)).x for c in o.bound_box) / 8
    xs = [centro_x(c) for c in desc(o) if c.type == 'MESH' and c.data and len(c.data.vertices)]                   # un vuoto all'origine con i figli lontani (la corda di velluto)
    return sum(xs) / len(xs) if xs else o.matrix_world.translation.x
GIA = set(q.name for q in bpy.data.objects if q.animation_data and q.animation_data.action and any('hide_render' in fc.data_path for fc in all_fcurves(q)))
for o in list(envc.objects) + list(prc.objects) + [f_['root'] for f_ in FF] + [MEL]:
    if o.parent is not None or o.name in GIA or o.name in NEVER or o in (cam, tgt): continue
    x = centro_x(o)
    if 300 < x: continue
    show(o, [(T_BLACK, T_END)] if x > 100 else [(0.0, T_BLACK), (T_END, TOTAL)])
scene.eevee.shadow_resolution_scale = 0.5
if LUCI != 'A': bpy.data.lights['LuceOspedale'].use_shadow = False; scene.eevee.shadow_ray_count = 2      # con poca luce ambiente le ombre morbide fanno grana a 4 campioni: ombre nette dalla luce principale, due raggi
for nm in ('DiscoCiano', 'DiscoBar', 'DiscoFronte', 'LuceOspedale2', 'LuceOspedale3'): bpy.data.lights[nm].use_shadow = False      # luci di riempimento: senza ombre il render e' piu' svelto

def lin(idb):
    for fc in all_fcurves(idb):
        kind = 'CONSTANT' if 'hide' in fc.data_path else 'LINEAR'
        for kp in fc.keyframe_points: kp.interpolation = kind
for o in bpy.data.objects: lin(o)
for l_ in bpy.data.lights: lin(l_)
set_interp(camd, 'CONSTANT')
try: scene.render.use_motion_blur = True; scene.render.motion_blur_shutter = 0.06
except Exception: pass
os.makedirs('../t017', exist_ok=True)
import json; json.dump([[round(s[0], 3), round(min(s[1], TOTAL), 3)] for s in SHOTS], open('../t017/shots.json', 'w'))
bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(BLEND)); print('SAVED', LUCI, BLEND, len(bpy.data.objects), 'oggetti')
