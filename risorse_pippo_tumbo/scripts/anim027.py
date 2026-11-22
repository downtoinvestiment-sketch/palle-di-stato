"""TESTA STANDARD di ogni episodio: mondo, quartiere (casa di Pippo a est, casa di Gualtiero a ovest, staccionata, strada), funzioni house_at / tower_at / tree.
Uso: cat templates/head.py scripts/animNNN_body.py > scripts/animNNN.py  (cambia TOTAL e gli import prima).
Test 027 - FRANCESCO IL CACTUS. Salva ../t027/pippo_t027.blend
Personaggi: Pippo e Tumbo ESISTENTI (pippo.py, tumbo.py) invariati; Gualtiero = nuovo vicino ricorrente (props009.gualtiero)."""
import sys, math, os
sys.path.insert(0, os.path.dirname(__file__))
import bpy, numpy as np
from mathutils import Vector, Euler, Matrix
from common import *
from render_setup import *
import set004, props004, props007, props009, props010, props012, props013, props015, props016b, kitlook, lookdev, pippo, tumbo
from set004 import obj, bx, cyl, ball_, MB

FPS = 24; TOTAL = 45.6; NF = int(TOTAL * FPS)
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
# Video 027 - FRANCESCO IL CACTUS, 45,6 s. Si unisce alla testa: templates/head.py + scripts/anim027_body.py -> scripts/anim027.py
# Copione n. 26 (COPIONI.md). Scelte: F1 (cactus tondo con le braccine), M1 mongolfiera arcobaleno, S1 sabbia scura (Ground054).
# Commissario versione B (divisa blu, occhiali a specchio). Camera a mano leggera sempre, scossa sugli urli.
# Posti: salotto (hook, x = 400), il parrucchiere (x = 600), il quartiere (case di head.py), il deserto (x = -700), lo spazio (x = 1200).
# Tempi da audio/words_t027.json. Luce «cinema». Pippo nel finale si tiene con le mani al braccio del cactus (non per la cravatta).
# ===================================================================================================================
import props024, props025, props026, props027, props021, luci, random, commissario
import pippo2 as pippo
A = kitlook.A
BLEND = os.environ.get('BLEND027', '../t027/pippo_t027.blend')
FONT = bpy.data.fonts.load(A.font('luckiest'))
M25 = props025.mats025(); M27 = props027.mats027(); CMM = commissario.mats_commissario()
rnd = random.Random(27)

# ======================= tempi (dalla voce) =======================
T_PORTA, T_CACTUS, T_MACCH, T_SPINE = 3.68, 5.68, 7.32, 8.88
T_GUA, T_PORCO, T_POLIZIA, T_ABBRACCIA, T_VOLA = 11.40, 13.22, 15.16, 16.40, 17.86
T_LOGICA, T_MONGO, T_DESERTO, T_INNAMORA, T_FRANCESCA = 21.44, 23.54, 24.60, 27.02, 29.88
T_TUMBO, T_PIPI, T_CRESCE, T_SPAZIO, T_LUNA, T_APPESO, T_TEAM = 33.14, 35.18, 36.74, 38.00, 39.08, 41.84, 43.18
TOTAL = 45.6; NF = int(TOTAL * FPS)

# fasi: H salotto (hook), B parrucchiere, S quartiere di giorno, D deserto, K spazio
FASI = [(0.0, 'H'), (T_PORTA, 'B'), (T_GUA, 'S'), (T_POLIZIA, 'B'), (T_VOLA, 'S'), (T_LOGICA, 'B'), (T_MONGO, 'S'), (T_DESERTO, 'D'), (T_SPAZIO, 'K')]
def iv(*codes):
    out = []
    for i, (t0, c) in enumerate(FASI):
        t1 = FASI[i + 1][0] if i + 1 < len(FASI) else TOTAL + 1
        if c in codes:
            if out and abs(out[-1][1] - t0) < 1e-6: out[-1] = (out[-1][0], t1)
            else: out.append((t0, t1))
    return out

# ======================= rendering e luce =======================
setup_render(scene, 1080, 1920, samples=4, fps=FPS, frames=NF); scene.frame_end = NF
scene.render.image_settings.color_mode = 'RGB'; scene.render.image_settings.compression = 90
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
SUN = luci.sole(prc, (0.25, -0.97), lato=1, energia=4.5)
luci.ombre_pulite(scene, mezza_risoluzione=True)
props021.bagliore(scene, forza=0.3, soglia=1.5)

# ======================= posti =======================
HX, BX, DX, KX = 400.0, 600.0, -700.0, 1200.0
PH = Vector((HX + 0.6, 0.6, 0.0))                 # Pippo allo specchio nell'hook
CH = Vector((BX, 0.4, 0.0))                       # poltrona del parrucchiere (guarda verso -Y)
FR_B = Vector((BX, 0.36, 0.60))                   # Francesco seduto in poltrona
PB = Vector((BX + 0.95, -0.25, 0.0))              # Pippo accanto alla poltrona
TB_B = Vector((BX + 1.45, -0.55, 0.0))            # Tumbo nel negozio
CM_IN = Vector((BX + 3.0, -1.2, 0.0)); CM_B = Vector((BX + 0.55, -0.42, 0.0))   # il commissario entra e arriva davanti a Francesco
GU0 = Vector((-14.0, 3.0, 0.0)); GDIR = Vector((0.907, 0.42, 0.0))
MG_S = Vector((4.5, -6.5, 0.0))                    # la mongolfiera nel quartiere
MG_D = Vector((DX + 6.5, 31.0, 0.0))              # la mongolfiera atterrata nel deserto
FR_D = Vector((DX + 1.5, 26.0, 0.0))              # Francesco nel vaso sulla sabbia
PD = Vector((DX + 3.3, 27.2, 0.0)); TB_D = Vector((DX + 2.45, 25.7, 0.0))
FCA = Vector((DX - 26.0, 64.0, 0.0)); FCA_H = 60.0   # Francesca, alta come un grattacielo
TIP_K = Vector((KX - 48.0, -5.0, 20.0))           # nello spazio: la punta del braccio di Francesco, dove si tiene Pippo
S_K = 14.0                                        # scala di Francesco nello spazio
ARM_TIP = Vector((0.21, 0.0, 0.20)); CORPO_Z = 0.21   # sotto il braccio destro di F1 (dove si tiene Pippo), nel corpo; quota del corpo nel vaso
ELASTICO = 1.6                                   # l'elastico delle mutande tirato dalla spina alla schiena di Pippo

# ======================= set =======================
SAL = props025.salotto(envc, M25, A, x0=HX, font=FONT)
CALR, CALN = props026.calendario(envc, FONT, numeri=('OGGI',), nome='CalOggi'); CALR.location = (HX + 1.35, 2.43, 1.62)
CALN['OGGI'].scale = (0.5, 0.5, 0.5)
CERCHIO = props024.anello('CalCerchio', 0.13, 0.012, material('M27_pennarello', (0.9, 0.05, 0.05), rough=0.5), envc, seg=48, segr=6)
CERCHIO.parent = CALR; CERCHIO.location = (0, -0.03, -0.16); CERCHIO.rotation_euler = (PI / 2, 0, 0); CERCHIO.scale = (1.5, 1.0, 1.0)
NEG = props027.negozio(envc, BX, FONT)
POLT = A.modello('BarberShopChair_01', posizione=(CH.x, CH.y, 0.0), altezza=1.15, rotazione=0, collezione=envc, appoggia=True)
dc = collection('Deserto')
SAB = A.materiale('Ground054', dimensione=4.0, tinta=(1.1, 1.0, 0.85))
bpy.ops.mesh.primitive_plane_add(size=700, location=(DX, 150, 0)); DSUOLO = bpy.context.object; DSUOLO.data.materials.append(SAB)
for c_ in DSUOLO.users_collection: c_.objects.unlink(DSUOLO)
dc.objects.link(DSUOLO)
DUNE = props027.dune(dc, DX, SAB)
CIELO_D = props027.cielo_deserto(dc, DX)
kc = collection('Spazio')
SPZ = props027.spazio(kc, KX)

# ======================= personaggi e oggetti =======================
P = pippo.build_pippo(chc); Tb = tumbo.build_tumbo(chc, scale=0.75); GU = props009.gualtiero(chc, G9)
CM = commissario.commissario(chc, CMM, 'B')
for r in (P['root'], Tb['root'], GU['root'], CM['root']): r.rotation_mode = 'XYZ'
for nm in 'LR': P['shoulder' + nm].rotation_mode = 'QUATERNION'
for nm in ('shoulderL', 'shoulderR', 'head'): GU[nm].rotation_mode = 'XYZ'
for nm in ('shoulderL', 'shoulderR', 'head'): CM[nm].rotation_mode = 'XYZ'
CRAV = props027.cravatta(chc, P['body'])
M_MUT = material('M27_mutande', (0.97, 0.97, 0.99), rough=0.6)
MUT = shape('MutandeFascia', 'cyl:1:1', (0, 0, 0.02), scale=(0.25, 0.25, 0.035), parent=P['body'], mat=M_MUT, coll=chc)
ELA = obj('MutandeElastico', set004.box_c(), (0, 0, -90), (0.14, 0.03, 1.0), M_MUT, chc); ELA.rotation_mode = 'XYZ'
MAZZO = props027.mazzo_fiori(chc); MAZZO.parent = P['shoulderL']; MAZZO.location = (0, -0.05, -0.6); MAZZO.rotation_euler = (2.0, 0, 0)
FR = props027.francesco(chc, M27, 'F1', font=FONT, nome='Francesco'); FR['root'].rotation_mode = 'XYZ'; FR['corpo'].rotation_mode = 'XYZ'
for nm in 'LR': FR['braccio' + nm].rotation_mode = 'XYZ'
MANT = props027.mantellina(chc, M27); MANT.parent = FR['root']; MANT.location = (0, 0, 0.36)
FRK = props027.francesco(kc, M27, 'F1', font=FONT, nome='FrancescoSpazio')
FRK['root'].scale = (S_K,) * 3; FRK['root'].location = TIP_K - Vector((0, 0, CORPO_Z * S_K)) - ARM_TIP * S_K   # Pippo si tiene sotto il braccio
FCA_R = props027.francesca(dc, M27, altezza=FCA_H); FCA_R['root'].location = FCA; FCA_R['root'].rotation_euler = (0, 0, -0.45)
MG = props027.mongolfiera(prc, M27, 'M1', nome='Mongolfiera'); MG['root'].rotation_mode = 'XYZ'
# la mano del parrucchiere con la macchinetta (entra da destra)
MANO = empty('ManoBarbiere', (0, 0, 0), None, chc); MANO.rotation_mode = 'XYZ'
shape('ManoManica', 'cap:0.06:0.45', (0.25, 0, 0), rot=(0, PI / 2, 0), parent=MANO, mat=material('M27_camice', (0.97, 0.97, 0.98), rough=0.6), coll=chc)
shape('ManoPelle', 'sphere', (0.0, 0, 0), scale=(0.06, 0.05, 0.05), parent=MANO, mat=CMM['skin'], coll=chc)
obj('Macchinetta', set004.box_c(), (-0.08, 0, 0.0), (0.16, 0.05, 0.05), material('M27_macchinetta', (0.2, 0.2, 0.22), rough=0.3), chc, parent=MANO)
obj('MacchinettaLama', set004.box_c(), (-0.17, 0, 0.0), (0.02, 0.055, 0.04), material('M27_lama', (0.85, 0.86, 0.9), rough=0.15, metallic=1.0), chc, parent=MANO)
# spine che volano nel negozio e spine che si piantano in Gualtiero
SPV = []
for k in range(36):
    o = props027.spina_volante(prc, M27, 'SpinaVolante'); o.rotation_mode = 'QUATERNION'
    a = rnd.uniform(0, 2 * PI); el = rnd.uniform(-0.25, 0.6)
    d = Vector((math.cos(a) * math.cos(el), math.sin(a) * math.cos(el), math.sin(el)))
    SPV.append((o, d, rnd.uniform(7, 11), T_SPINE + 0.04 + 0.012 * k))
SPG = []
for k in range(55):
    o = props027.spina_volante(prc, M27, 'SpinaGualtiero', lung=0.16); o.rotation_mode = 'QUATERNION'
    if k < 12:   # testa
        th = rnd.uniform(-1.2, 1.2); ph = rnd.uniform(-0.3, 1.2); c_ = Vector((0, 0, 1.8)); rr = Vector((0.28, 0.26, 0.28))
    else:        # busto e pancia
        th = rnd.uniform(-1.4, 1.4); ph = rnd.uniform(-0.8, 0.8); c_ = Vector((0, -0.05, 1.15)); rr = Vector((0.40, 0.36, 0.45))
    n = Vector((math.sin(th) * math.cos(ph), -math.cos(th) * math.cos(ph), math.sin(ph)))
    SPG.append((o, c_, rr, n, T_GUA + 0.15 + (T_PORCO + 0.6 - T_GUA - 0.15) * (k / 55.0) ** 0.8))
GOCCE = [props027.goccia(prc) for k in range(26)]
TRAIL_T = [T_VOLA + 0.25 * k for k in range(13)]

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
# figli prima dei padri
show_only(MUT, [(T_CRESCE, TOTAL + 1)]); show_only(ELA, [(T_CRESCE, TOTAL + 1)]); show_only(MAZZO, [(0.0, T_PORTA)]); show_only(MANT, iv('B'))
show_only(CALR, iv('H')); show_only(SAL['root'], iv('H'))
show_only(NEG['root'], iv('B')); show_only(POLT, iv('B'))
for o in list(dc.objects):
    if o.parent is None: show_only(o, iv('D'))
for o in list(kc.objects):
    if o.parent is None: show_only(o, iv('K'))
show_only(MANO, [(T_MACCH, T_SPINE + 0.6)])
for o, d, v, t0 in SPV: show_only(o, [(t0, T_GUA)])
for o, c_, rr, n, t0 in SPG: show_only(o, [(t0 - 0.15, T_POLIZIA)])
for o in GOCCE: show_only(o, [(T_PIPI + 0.15, T_CRESCE)])
show_only(MG['root'], [(T_MONGO, T_SPAZIO)])
show_only(FR['root'], [(T_PORTA, T_GUA), (T_POLIZIA, T_VOLA), (T_LOGICA, T_SPAZIO)])
show_only(P['root'], [(0.0, T_GUA), (T_POLIZIA, T_VOLA), (T_LOGICA, TOTAL + 1)])
show_only(Tb['root'], [(T_PORTA, T_GUA), (T_LOGICA, T_SPAZIO)])
show_only(GU['root'], [(T_GUA, T_POLIZIA)])
show_only(CM['root'], [(T_POLIZIA, T_LOGICA)])
for o in list(envc.objects):
    if o.parent is None and o.name not in NEVER: show(o, iv('S'))

# ======================= luce per fase =======================
def chiavi(owner, attr, valori):
    for (t_, v) in valori:
        setattr(owner, attr, v); owner.keyframe_insert(attr, frame=fr(t_))
def per_fase(owner, attr, vals, default=0.0):
    chiavi(owner, attr, [(t0, vals.get(c, default)) for (t0, c) in FASI])
per_fase(SUN.data, 'energy', {'S': 4.6, 'D': 5.2, 'K': 3.5})
per_fase(CIELO.inputs['Strength'], 'default_value', {'H': 0.05, 'B': 0.05, 'S': 0.42, 'D': 0.55, 'K': 0.0})
if VISTA: per_fase(VISTA.inputs['Strength'], 'default_value', {'S': V0})
per_fase(scene.view_settings, 'exposure', {'H': 0.15, 'B': 0.15, 'S': 0.2, 'D': 0.0, 'K': 0.8})
def area(nome, pos, energia, size, colore=(1.0, 0.95, 0.86)):
    l_ = bpy.data.lights.new(nome, 'AREA'); l_.energy = energia; l_.size = size; l_.color = colore; l_.use_shadow = False
    o = bpy.data.objects.new(nome, l_); prc.objects.link(o); o.location = pos; return o
def on_off(lights, intervals):
    for l_ in lights:
        e_ = l_.data.energy; keys = [(0.0, e_ if intervals[0][0] <= 0 else 0.0)]
        for (a, b) in intervals:
            if a > 0: keys += [(a, e_)]
            if b < TOTAL: keys += [(b, 0.0)]
        chiavi(l_.data, 'energy', sorted(keys))
PLAF_H = area('PlafSalotto', (HX, 0.0, 4.1), 380.0, 3.0)
LH = luci.cinema(prc, PH + Vector((0, 0, 1.3)), Vector((HX + 0.6, -1.3, 1.45)), distanza=3.0, lato=-1, forza=0.55, nome='CinemaH')
PLAF_B = area('PlafNegozio', (BX, 0.0, 2.95), 420.0, 3.5)
LB = luci.cinema(prc, Vector((BX + 0.3, 0.0, 1.0)), Vector((BX + 0.4, -3.0, 1.4)), distanza=3.4, lato=-1, forza=0.6, nome='CinemaB')
LG = luci.cinema(prc, GU0 + Vector((0, 0, 1.3)), GU0 + GDIR * 3.0 + Vector((0, 0, 1.5)), distanza=3.5, lato=1, forza=0.5, nome='CinemaG')
LD = luci.cinema(prc, FR_D + Vector((0, 0, 0.6)), FR_D + Vector((0.6, -2.5, 0.8)), distanza=3.0, lato=-1, forza=0.5, nome='CinemaD')
LK = luci.cinema(prc, TIP_K - Vector((0, 0, 0.6)), TIP_K + Vector((0.6, -3.0, -0.4)), distanza=3.5, lato=-1, forza=0.7, nome='CinemaK')
on_off([PLAF_H] + list(LH.values()), iv('H')); on_off([PLAF_B] + list(LB.values()), iv('B'))
on_off(list(LG.values()), [(T_GUA, T_POLIZIA)]); on_off(list(LD.values()), iv('D')); on_off(list(LK.values()), iv('K'))
LIGHTS = [SUN.data, PLAF_H.data, PLAF_B.data] + [l_.data for d_ in (LH, LB, LG, LD, LK) for l_ in d_.values()]

# ======================= pose =======================
def qdir(d, rest=(0, 0, -1)): return Vector(rest).rotation_difference(Vector(d).normalized())
def yaw_to(a, b): return math.atan2(b[0] - a[0], -(b[1] - a[1]))
def braccia(nome, forza=1.0):
    b = pippo.EMOZIONI_FORTI[nome]['braccia']; return {'aL': tuple(Vector((0, 0, -1)).lerp(Vector(b[0]).normalized(), forza)), 'aR': tuple(Vector((0, 0, -1)).lerp(Vector(b[1]).normalized(), forza))}
def jit(t, a=0.02, f=37.0): return a * math.sin(t * f) * math.sin(t * f * 0.71 + 1.3)

def crescita(t):
    """scala del corpo di Francesco quando cresce nel deserto."""
    if t < T_CRESCE: return 1.0
    u = min(1.0, (t - T_CRESCE) / (T_SPAZIO - T_CRESCE)); return 4.5 * (120.0 / 4.5) ** (u ** 1.3)
def punta_braccio(t):
    s = crescita(t); return FR_D + Vector((0, 0, CORPO_Z)) + ARM_TIP * s
def gancio(t):
    """la spina a cui sono agganciate le mutande di Pippo (sotto il braccio di Francesco)."""
    return (punta_braccio(t) if t < T_SPAZIO else TIP_K) - Vector((0, 0, 0.12))

def pp(t):
    """Pippo: loc, yaw, lean, head, braccia."""
    S_ = dict(loc=Vector((0, 0, -50)), yaw=0.0, lean=0.0, head=(0, 0, 0), aL=(-0.15, 0, -1), aR=(0.15, 0, -1))
    if t < T_PORTA:                                    # allo specchio: si sistema la cravatta
        S_.update(loc=PH.copy(), aR=(-0.35, -0.75, 0.45 + 0.08 * math.sin(t * 9)), aL=(-0.2, -0.6, -0.75), head=(-0.08, 0.05 * math.sin(t * 2), 0))
    elif t < T_GUA:                                    # dal parrucchiere
        S_.update(loc=PB.copy(), yaw=yaw_to(PB, (BX - 0.2, -3.0)), aL=(-0.5, -0.5, -0.65), aR=(0.15, 0, -1))
        if t >= T_SPINE: S_.update(**braccia('spaventato'), lean=-0.1)
    elif T_POLIZIA <= t < T_VOLA:
        S_.update(loc=PB.copy(), yaw=yaw_to(PB, CM_B), **braccia('sorpreso', 0.8))
    elif T_LOGICA <= t < T_MONGO:                      # «la cosa piu' logica»: guarda in camera
        S_.update(loc=PB.copy(), yaw=yaw_to(PB, (BX + 0.6, -2.0)), head=(0.05, 0.12, 0), aL=(-0.3, -0.3, -0.9), aR=(0.4, -0.6, 0.3))
    elif T_MONGO <= t < T_DESERTO:                     # nella cesta
        b = mg_loc(t); S_.update(loc=b + Vector((-0.25, 0.0, 0.12)), yaw=yaw_to(MG_S, (12.0, -8.0)), **braccia('felice', 0.8))
    elif T_DESERTO <= t < T_INNAMORA:
        b = mg_loc(t); S_.update(loc=b + Vector((-0.25, 0.0, 0.12)), yaw=0.6, **braccia('felice', 0.8))
    elif T_INNAMORA <= t < T_CRESCE:                   # sulla sabbia accanto a Francesco
        S_.update(loc=PD.copy(), yaw=yaw_to(PD, FCA) if t >= T_FRANCESCA else yaw_to(PD, (DX + 1.0, 22.0)), head=(-0.35 if t >= T_FRANCESCA else 0.0, 0, 0))
        if t >= T_FRANCESCA: S_.update(**braccia('sorpreso', 0.9))
    else:                                              # appeso per le mutande a una spina del braccio di Francesco
        sw = 0.08 * math.sin(t * 1.6)
        S_.update(loc=gancio(t) - Vector((0, 0.24, 0.72)) - Vector((0, 0, ELASTICO)) + Vector((sw * 0.4, 0, 0)), yaw=0.05 * math.sin(t * 0.9), lean=0.12 + sw * 0.3,
                  aL=(-0.15 + 0.1 * math.sin(t * 2.1), 0.05, -1), aR=(0.15 - 0.1 * math.sin(t * 2.3), 0.05, -1), head=(-0.25 if t < T_SPAZIO else 0.04, 0, 0))
    return S_

def mg_loc(t):
    """posizione della cesta della mongolfiera."""
    if t < T_DESERTO:
        return MG_S + Vector((0, 0, 0.0 if t < T_DESERTO - 0.45 else 3.0 * ramp(t, T_DESERTO - 0.45, T_DESERTO)))
    if t < T_INNAMORA - 0.6:
        u = (t - T_DESERTO) / (T_INNAMORA - 0.6 - T_DESERTO)
        return Vector((DX - 4.0 + 3.0 * math.sin(u * 2.0), -40.0 + 70.0 * u, 26.0 - 4.0 * u + 0.6 * math.sin(t * 1.3)))
    u = ramp(t, T_INNAMORA - 0.6, T_INNAMORA); return MG_D.lerp(Vector((DX - 4.0, 30.0, 22.0)), 1 - u) if u < 1 else MG_D.copy()

def tp(t):
    """Tumbo: loc, yaw, roll (per la pipi'), head."""
    S_ = dict(loc=Vector((0, 0, -50)), yaw=0.0, roll=0.0, head=(0, 0, 0), tail=(-0.5, 0, 0.6 * math.sin(t * 14)), zampa=0.0)
    if T_PORTA <= t < T_GUA: S_.update(loc=TB_B.copy(), yaw=yaw_to(TB_B, FR_B))
    elif T_LOGICA <= t < T_MONGO: S_.update(loc=TB_B.copy(), yaw=yaw_to(TB_B, (BX + 0.5, -2.5)))
    elif T_MONGO <= t < T_INNAMORA: b = mg_loc(t); S_.update(loc=b + Vector((0.35, 0.1, 0.55)), yaw=0.5)
    elif T_INNAMORA <= t < T_PIPI: S_.update(loc=TB_D.copy(), yaw=yaw_to(TB_D, (DX + 1.0, 22.0)) if t < T_TUMBO else yaw_to(TB_D, FR_D), head=(0.3 if t >= T_TUMBO + 0.6 else 0.0, 0, 0))
    elif t < T_SPAZIO:   # di schiena verso il vaso, la pipi'
        d_ = FR_D - TB_D; y_ = math.atan2(d_.y, d_.x)   # il fianco destro (+X di Tumbo) verso il vaso
        S_.update(loc=TB_D + Vector((0, 0, 0.0)), yaw=y_, roll=0.08 * ramp(t, T_PIPI, T_PIPI + 0.15), tail=(-0.9, 0, 0), zampa=ramp(t, T_PIPI - 0.1, T_PIPI + 0.12))
    return S_

def cmp_(t):
    """il commissario: loc, yaw, pancia, rot (quando vola)."""
    S_ = dict(loc=Vector((0, 0, -50)), yaw=0.0, pancia=1.0, rot=(0, 0, 0), sL=(0, 0.45, 0), sR=(0, -0.45, 0))
    if T_POLIZIA <= t < T_ABBRACCIA:
        u = sm(ramp(t, T_POLIZIA, T_ABBRACCIA - 0.2)); p = CM_IN.lerp(CM_B, u) + Vector((0, 0, 0.04 * abs(math.sin(t * 9))))
        S_.update(loc=p, yaw=yaw_to(CM_IN, CM_B) if u < 0.95 else yaw_to(CM_B, FR_B))
    elif T_ABBRACCIA <= t < T_VOLA:
        S_.update(loc=CM_B.copy(), yaw=yaw_to(CM_B, FR_B), pancia=1.0 + 0.4 * ramp(t, T_ABBRACCIA + 0.3, T_VOLA - 0.2), sL=(-1.2, 0.3, 0), sR=(-1.2, -0.3, 0))
    elif T_VOLA <= t < T_LOGICA:   # vola via come un palloncino bucato, sopra il quartiere
        u = (t - T_VOLA) / (T_LOGICA - T_VOLA)
        p = Vector((10.0 - 34.0 * u + 6.0 * math.sin(u * 17), -6.0 + 14.0 * u + 4.0 * math.sin(u * 11), 2.0 + 30.0 * u ** 0.8 + 3.0 * math.sin(u * 23)))
        S_.update(loc=p, yaw=t * 9.0, rot=(math.sin(t * 13) * 1.2, math.cos(t * 11) * 0.9, 0), pancia=max(0.45, 1.4 - 1.0 * u), sL=(0, 1.4, 0), sR=(0, -1.4, 0))
    return S_

# ======================= chiavi =======================
def K(o, f, loc=None, rot=None, scale=None):
    if loc is not None: o.location = loc; o.keyframe_insert('location', frame=f)
    if rot is not None: o.rotation_euler = rot; o.keyframe_insert('rotation_euler', frame=f)
    if scale is not None: o.scale = scale if isinstance(scale, (tuple, list)) else (scale,) * 3; o.keyframe_insert('scale', frame=f)
up = Vector((0, 0, 1))
for f in range(1, NF + 1):
    t = (f - 1) / FPS
    s = pp(t)
    K(P['root'], f, tuple(s['loc']), (s['lean'], 0, s['yaw'])); K(P['head'], f, rot=s['head'])
    for nm, k_ in (('L', 'aL'), ('R', 'aR')):
        sh = P['shoulder' + nm]; sh.rotation_quaternion = qdir(s[k_]); sh.keyframe_insert('rotation_quaternion', frame=f)
    if t >= T_CRESCE - 0.05:                           # l'elastico dalla schiena di Pippo alla spina
        sp_ = pp(t); a_ = sp_['loc'] + Matrix.Rotation(sp_['yaw'], 3, 'Z') @ Vector((0, 0.24, 0.72)); b_ = gancio(t); m_ = (a_ + b_) / 2; l_ = (b_ - a_).length
        q_ = Vector((0, 0, 1)).rotation_difference((b_ - a_).normalized()).to_euler()
        K(ELA, f, tuple(m_), tuple(q_), (0.2, 0.03, max(0.05, l_)))
    s = tp(t)
    K(Tb['root'], f, tuple(s['loc']), (0, s['roll'], s['yaw']), 0.75); K(Tb['head'], f, rot=s['head']); K(Tb['tail'], f, rot=s['tail'])
    K(Tb['legBR'], f, rot=(0.2 * s['zampa'], -1.35 * s['zampa'], 0))
    c = cmp_(t)
    K(CM['root'], f, tuple(c['loc']), (c['rot'][0], c['rot'][1], c['yaw'])); K(CM['shoulderL'], f, rot=c['sL']); K(CM['shoulderR'], f, rot=c['sR'])
    commissario.cex(CM, f, lid=0.2 if t < T_ABBRACCIA else -0.1, mouth=0.1 if t < T_ABBRACCIA else 0.9, brow=0.3 if t < T_ABBRACCIA else -1.0, pancia=c['pancia'])
    g_ = yaw_to(GU0, GU0 + GDIR)
    K(GU['root'], f, tuple(GU0 + Vector((jit(t, 0.015, 23) if t > T_GUA + 0.2 else 0, 0, 0))), (0, 0, g_))
    K(GU['shoulderL'], f, rot=(0, 0.25 + 0.6 * ramp(t, T_PORCO, T_PORCO + 0.3), 0)); K(GU['shoulderR'], f, rot=(0, -0.25 - 0.6 * ramp(t, T_PORCO, T_PORCO + 0.3), 0))
    # Francesco: dove sta, le braccia (abbraccio), la crescita
    if t < T_INNAMORA: fl, fyaw = FR_B, 0.0
    elif t < T_SPAZIO: fl, fyaw = FR_D, 0.0
    else: fl, fyaw = Vector((0, 0, -60)), 0.0
    if T_MONGO <= t < T_INNAMORA:
        fl = mg_loc(t) + Vector((0.3, -0.45, 1.06)); fyaw = 0.4
    K(FR['root'], f, tuple(fl), (0, 0, fyaw))
    ab = ramp(t, T_ABBRACCIA, T_ABBRACCIA + 0.3) * (1 - ramp(t, T_VOLA - 0.2, T_VOLA))
    K(FR['braccioL'], f, rot=(0, 0, -0.9 * ab + 0.15 * math.sin(t * 3)))
    K(FR['braccioR'], f, rot=(0, 0, 0.9 * ab - 0.15 * math.sin(t * 3)))
    sc_ = crescita(t)
    K(FR['corpo'], f, scale=(sc_,) * 3, rot=(0, 0, 0.05 * math.sin(t * 2.2) if t < T_CRESCE else 0.0))
    for nm in 'LR':
        p_ = FR['pupil' + nm]
        lk = (0.0, 0.0)
        if T_FRANCESCA <= t < T_CRESCE: lk = (-0.5, 0.6)
        elif T_ABBRACCIA <= t < T_VOLA: lk = (0.4, 0.0)
        elif T_LOGICA <= t < T_MONGO: lk = (0.5, 0.1)
        K(p_, f, loc=(lk[0] * 0.02, 0, lk[1] * 0.02))
    K(FR['mouth'], f, scale=(0.035, 0.01, 0.015 + (0.03 if T_SPINE <= t < T_GUA or T_FRANCESCA <= t < T_TUMBO else 0.0)))
    # la mano del parrucchiere con la macchinetta
    u = sm(ramp(t, T_MACCH, T_SPINE - 0.15))
    K(MANO, f, tuple(FR_B + Vector((1.4 - 1.12 * u, -0.25, 0.55)) + Vector((0.006 * math.sin(t * 70), 0, 0.006 * math.cos(t * 83)))), (0, 0, -0.25))
    # spine che volano nel negozio
    for o, d, v, t0 in SPV:
        if t0 - 0.05 <= t < T_GUA + 0.05:
            tt = max(0.0, t - t0); p = FR_B + Vector((0, 0, 0.45)) + d * min(v * tt, 2.6)
            p.x = max(BX - 3.05, min(BX + 3.05, p.x)); p.y = max(-2.9, min(2.45, p.y)); p.z = max(0.02, min(2.95, p.z))
            o.location = p; o.keyframe_insert('location', frame=f)
            if t <= t0 + 0.02: o.rotation_quaternion = up.rotation_difference(d); o.keyframe_insert('rotation_quaternion', frame=f)
    # spine che arrivano su Gualtiero (da destra) e restano piantate
    for o, c_, rr, n, t0 in SPG:
        if t0 - 0.2 <= t < T_POLIZIA + 0.05:
            gq = Matrix.Rotation(g_, 3, 'Z')
            tip = GU0 + gq @ Vector((c_.x + rr.x * n.x * 0.92, c_.y + rr.y * n.y * 0.92, c_.z + rr.z * n.z * 0.92))
            dirn = (gq @ n).normalized()
            src = tip + Vector((5.0, -1.5, 0.6)); w_ = sm(ramp(t, t0 - 0.15, t0))
            o.location = src.lerp(tip, w_); o.keyframe_insert('location', frame=f)
            o.rotation_quaternion = up.rotation_difference(dirn); o.keyframe_insert('rotation_quaternion', frame=f)
    # mongolfiera: si gonfia nel quartiere, vola sul deserto, atterra
    if T_MONGO - 0.05 <= t < T_SPAZIO + 0.05:
        K(MG['root'], f, tuple(mg_loc(t)), (0, 0, 0.3 + 0.1 * math.sin(t * 0.7)))
        K(MG['pallone'], f, scale=(max(0.05, sm(ramp(t, T_MONGO, T_MONGO + 0.6))),) * 3)
        K(MG['fiamma'], f, scale=(0.16, 0.16, 0.4 * (1.4 if T_MONGO <= t < T_INNAMORA else 0.3) * (1 + 0.25 * math.sin(t * 31))))
    # la pipi' di Tumbo: un arco di gocce dal sedere di Tumbo al vaso
    if T_PIPI <= t < T_CRESCE:
        d_ = FR_D - TB_D; y_ = math.atan2(d_.y, d_.x); a_ = TB_D + Matrix.Rotation(y_, 3, 'Z') @ Vector((0.13, 0.16, 0.28)); b_ = FR_D + Vector((0.1, -0.08, 0.16))
        for k, o in enumerate(GOCCE):
            q = ((t - T_PIPI) * 2.2 + k / len(GOCCE)) % 1.0
            p = a_.lerp(b_, q) + Vector((0, 0, 0.35 * 4 * q * (1 - q)))
            K(o, f, tuple(p))
    else:
        for o in GOCCE: K(o, f, (0, 0, -90))

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
    else:
        for nm in 'LR':
            br = P['brow' + nm]; br.rotation_euler = (0, 0, 0); br.keyframe_insert('rotation_euler', frame=f)
    seg = pippo._segni(P); ex_ = list(e.get('extra', ()))
    for k, g in seg.items():
        g.scale = (1, 1, 1) if (k in ex_ and forza > 0.3) else (0.001,) * 3
        g.keyframe_insert('scale', frame=f)
def emo(t, nome, forza=1.0, **extra):
    if _emo_last[0] and t - 0.06 > _emo_last[0][2]: _emo_key(fr(t - 0.06), _emo_last[0][0], _emo_last[0][1], _emo_last[0][3])
    _emo_key(fr(t), nome, forza, extra); _emo_last[0] = (nome, forza, t, extra)
def tex(t, **k): _ex('t', lambda f, **kk: tumbo.tumbo_express(Tb, f, **kk), t, k)
emo(0.0, 'felice', 0.7); emo(T_PORTA, 'felice', 1.0); emo(T_SPINE, 'spaventato', 1.0); emo(T_POLIZIA, 'sorpreso', 0.8)
emo(T_LOGICA, 'felice', 0.6, eye_open=0.6); emo(T_MONGO, 'felice', 1.0); emo(T_FRANCESCA, 'sorpreso', 1.0)
emo(T_CRESCE, 'spaventato', 1.0); emo(T_SPAZIO, 'normale', 1.0, eye_open=0.55); emo(T_TEAM, 'normale', 1.0, eye_open=0.5)
tex(0.0, tongue=0.6, brow=0.2); tex(T_SPINE, tongue=0.0, brow=-0.5, eye_scale=1.3); tex(T_LOGICA, tongue=0.7, brow=0.3); tex(T_TUMBO, tongue=0.2, brow=0.6)
tex(T_PIPI, tongue=0.8, brow=0.4, eye_open=0.4)

# ======================= effetti =======================
FXC = prc
def fx(name, pos, w, t0, dur, **k): return A.effetto(name, posizione=tuple(pos), larghezza=w, animazione=(fr(t0), int(dur * FPS)), collezione=FXC, **k)
fx('emoticon/anger', GU0 + Vector((0.35, 0.3, 2.3)), 0.45, T_PORCO + 0.2, 1.4)
fx('emoticon/hearts', FR_D + Vector((0.0, -0.2, 1.05)), 0.45, T_FRANCESCA + 0.6, 2.2)
fx('emoticon/exclamation', CM_B + Vector((0.0, -0.2, 2.15)), 0.35, T_ABBRACCIA + 0.4, 1.0)
for k, tt in enumerate(TRAIL_T):
    c = cmp_(tt + 0.01); fx('sbuffo_bianco/whitepuff%02d' % (k % 8 + 1), c['loc'] + Vector((0, 0, 0.6)), 1.4, tt, 0.6)
for k in range(5): fx('schizzi/splat%02d' % (k * 5 + 2), FR_D + Vector((rnd.uniform(-0.2, 0.25), -0.15, rnd.uniform(0.05, 0.3))), 0.25, T_PIPI + 0.3 + 0.2 * k, 0.4, colore=(1.0, 0.9, 0.3), opacita=0.9)
for k in range(8): fx('sbuffo_bianco/whitepuff%02d' % (k + 1), FR_D + Vector((rnd.uniform(-1.5, 1.5), rnd.uniform(-1.0, 1.0), 0.3)), 1.8, T_CRESCE + 0.04 * k, 0.6)

# ======================= camera =======================
def segui(t, kind):
    if kind == 'cm': return cmp_(t)['loc'] + Vector((0, 0, 1.1))
    if kind == 'mg': return mg_loc(t) + Vector((0, 0, 3.5))
    if kind == 'tip': return punta_braccio(t)
    return None
PHZ = 1.42
SHOTS = [  # t0, t1, camera da, a, mira da, a, lente, diaframma, mano, segui
    (0.0, T_PORTA, (PH.x + 0.1, -2.3, 1.5), (PH.x + 0.05, -1.8, 1.48), (PH.x, PH.y, 1.35), (PH.x, PH.y, 1.38), 35, 4.0, 0.6, None),          # 01 l'appuntamento
    (T_PORTA, T_CACTUS, (BX + 0.6, -3.4, 1.4), (BX + 0.5, -3.1, 1.35), (BX + 0.4, 0.0, 0.9), (BX + 0.4, 0.0, 0.9), 26, 6.0, 0.8, None),         # 02 dal parrucchiere
    (T_CACTUS, T_MACCH, (BX + 0.05, -0.9, 1.05), (BX + 0.04, -0.8, 1.05), (BX, 0.36, 1.0), (BX, 0.36, 1.0), 45, 3.0, 0.8, None),             # 03 Francesco e' un cactus
    (T_MACCH, T_SPINE, (BX - 0.75, -0.85, 1.15), (BX - 0.7, -0.8, 1.12), (BX + 0.25, 0.3, 1.05), (BX + 0.15, 0.3, 1.05), 40, 3.0, 1.0, None),   # 04 la macchinetta
    (T_SPINE, T_GUA, (BX + 0.4, -3.3, 1.5), (BX + 0.3, -3.5, 1.5), (BX + 0.2, 0.2, 1.1), (BX + 0.2, 0.2, 1.1), 22, 8.0, 1.8, None),          # 05 le spine come proiettili
    (T_GUA, T_PORCO, tuple(GU0 + GDIR * 3.4 + Vector((0, 0, 1.75))), tuple(GU0 + GDIR * 3.0 + Vector((0, 0, 1.72))), tuple(GU0 + Vector((0, 0, 1.45))), tuple(GU0 + Vector((0, 0, 1.45))), 30, 4.0, 1.0, None),  # 06 Gualtiero
    (T_PORCO, T_POLIZIA, tuple(GU0 + GDIR * 2.6 + Vector((0, 0, 1.75))), tuple(GU0 + GDIR * 2.2 + Vector((0, 0, 1.75))), tuple(GU0 + Vector((0, 0, 1.5))), tuple(GU0 + Vector((0, 0, 1.55))), 32, 4.0, 1.4, None),  # 07 porcospino
    (T_POLIZIA, T_ABBRACCIA, (BX - 0.2, -3.4, 1.4), (BX - 0.1, -3.2, 1.4), (BX + 1.2, -0.6, 1.1), (BX + 0.5, -0.3, 1.1), 26, 6.0, 0.8, None),   # 08 arriva la polizia
    (T_ABBRACCIA, T_VOLA, (BX - 0.9, -2.1, 1.3), (BX - 0.8, -1.9, 1.3), (BX + 0.3, 0.0, 1.05), (BX + 0.3, 0.0, 1.1), 32, 5.0, 1.2, None),       # 09 l'abbraccio
    (T_VOLA, T_LOGICA, (14.0, -16.0, 4.0), (12.0, -18.0, 6.0), (10.0, -6.0, 3.0), (10.0, -6.0, 3.0), 26, 22, 1.0, 'cm'),                          # 10 vola via
    (T_LOGICA, T_MONGO, (BX + 1.25, -2.2, 1.5), (BX + 1.22, -2.0, 1.5), (PB.x, PB.y, 1.45), (PB.x, PB.y, 1.45), 40, 3.0, 0.7, None),        # 11 la cosa piu' logica
    (T_MONGO, T_DESERTO, (10.5, -15.5, 1.6), (10.0, -15.0, 1.8), (MG_S.x, MG_S.y, 3.0), (MG_S.x, MG_S.y, 5.0), 22, 22, 1.2, None),               # 12 compra una mongolfiera
    (T_DESERTO, T_INNAMORA, (DX + 30.0, -35.0, 24.0), (DX + 30.0, 20.0, 22.0), (DX, -30.0, 28.0), (DX, 20.0, 26.0), 30, 22, 0.8, 'mg'),       # 13 nel deserto
    (T_INNAMORA, T_FRANCESCA, (FR_D.x + 0.25, 23.9, 0.8), (FR_D.x + 0.2, 24.2, 0.75), (FR_D.x, FR_D.y, 0.55), (FR_D.x, FR_D.y, 0.6), 35, 4.0, 0.8, None),  # 14 si innamora
    (T_FRANCESCA, T_TUMBO, (FR_D.x + 2.0, 22.8, 0.45), (FR_D.x + 2.1, 22.6, 0.4), (FR_D.x, FR_D.y, 0.8), (FCA.x, FCA.y, FCA_H * 0.86), 20, 22, 1.0, None),  # 15 Francesca (dal basso)
    (T_TUMBO, T_PIPI, (FR_D.x + 1.9, 23.6, 0.55), (FR_D.x + 1.8, 23.8, 0.5), (FR_D.x + 0.6, FR_D.y, 0.35), (FR_D.x + 0.6, FR_D.y, 0.35), 32, 4.0, 0.8, None),  # 16 Tumbo
    (T_PIPI, T_CRESCE, (FR_D.x + 1.3, 24.3, 0.32), (FR_D.x + 1.25, 24.4, 0.32), (FR_D.x + 0.5, FR_D.y, 0.25), (FR_D.x + 0.5, FR_D.y, 0.25), 32, 4.0, 0.6, None),  # 17 la pipi'
    (T_CRESCE, T_SPAZIO, (FR_D.x + 16.0, 8.0, 1.0), (FR_D.x + 30.0, -10.0, 1.5), (FR_D.x, FR_D.y, 1.0), (FR_D.x, FR_D.y, 1.0), 22, 22, 1.6, 'tip'),  # 18 cresce fino alla luna
    (T_SPAZIO, T_LUNA, (KX - 38.0, -46.0, 20.0), (KX - 39.0, -44.0, 20.5), (KX - 41.0, 10.0, 15.0), (KX - 42.0, 10.0, 15.5), 22, 22, 0.6, None),  # 19 lo spazio
    (T_LUNA, T_APPESO, (TIP_K.x + 1.4, TIP_K.y - 3.0, TIP_K.z - 0.3), (TIP_K.x + 1.3, TIP_K.y - 2.7, TIP_K.z - 0.3), (TIP_K.x, TIP_K.y, TIP_K.z - 0.6), (TIP_K.x, TIP_K.y, TIP_K.z - 0.6), 35, 4.0, 0.5, None),  # 20 sulla luna
    (T_APPESO, T_TEAM, (TIP_K.x - 12.0, TIP_K.y - 11.0, TIP_K.z - 3.0), (TIP_K.x - 11.0, TIP_K.y - 10.5, TIP_K.z - 3.0), (TIP_K.x + 4.0, TIP_K.y + 5.0, TIP_K.z - 3.0), (TIP_K.x + 4.0, TIP_K.y + 5.0, TIP_K.z - 3.0), 24, 22, 0.5, None),  # 21 appeso a un cactus
    (T_TEAM, TOTAL + 0.1, (TIP_K.x + 0.75, TIP_K.y - 1.85, TIP_K.z - 0.25), (TIP_K.x + 0.7, TIP_K.y - 1.65, TIP_K.z - 0.25), (TIP_K.x, TIP_K.y, TIP_K.z - 0.45), (TIP_K.x, TIP_K.y, TIP_K.z - 0.45), 40, 3.0, 0.4, None),  # 22 team Pippo o team Francesco
]
SHAKES = [(T_SPINE, 0.03, 0.8), (T_PORCO, 0.015, 0.5), (T_VOLA, 0.02, 0.5), (T_MONGO, 0.02, 0.6), (T_FRANCESCA, 0.01, 0.6), (T_CRESCE, 0.03, 1.2)]
def hn(t, s): return 0.6 * math.sin(t * 1.7 + s) + 0.3 * math.sin(t * 3.3 + 2.1 * s) + 0.12 * math.sin(t * 7.9 + 3.7 * s)
for f in range(1, NF + 1):
    t = (f - 1) / FPS
    s_ = next((s for s in SHOTS if s[0] <= t < s[1]), SHOTS[-1]); u = sm((t - s_[0]) / (s_[1] - s_[0]))
    cl = Vector(lerp(s_[2], s_[3], u)); tl = Vector(lerp(s_[4], s_[5], u))
    if s_[9]: tl = segui(t, s_[9])
    if s_[0] in (T_LUNA, T_TEAM): hp = pp(t)['loc'] + Vector((0, 0, PHZ)); tl = hp; cl = hp + (Vector(lerp(s_[2], s_[3], u)) - Vector(s_[4]))
    d = (tl - cl).length
    cl = cl + Vector((hn(t, 1), 0.5 * hn(t, 2), hn(t, 3))) * s_[8] * d * 0.015; tl = tl + Vector((hn(t, 4), 0, hn(t, 5))) * s_[8] * d * 0.006
    for (t0, a_, d_) in SHAKES:
        if t0 <= t < t0 + d_:
            k = a_ * d * (1 - (t - t0) / d_); cl = cl + Vector((k * math.sin(t * 61), 0, k * 0.7 * math.sin(t * 47)))
    cam.location = cl; tgt.location = tl; camd.lens = s_[6]; camd.dof.aperture_fstop = s_[7]
    cam.keyframe_insert('location', frame=f); tgt.keyframe_insert('location', frame=f); camd.keyframe_insert('lens', frame=f); camd.dof.keyframe_insert('aperture_fstop', frame=f)

kitlook.tune_cutouts(1.9)
def lin(idb):
    for fc in all_fcurves(idb):
        kind = 'CONSTANT' if 'hide' in fc.data_path else 'LINEAR'
        for kp in fc.keyframe_points: kp.interpolation = kind
for o in bpy.data.objects: lin(o)
for d in LIGHTS + [scene.world.node_tree]:
    for fc in all_fcurves(d):
        for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'
for fc in all_fcurves(scene):
    for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'
set_interp(camd, 'CONSTANT')
for nm in ('Cam', 'CamTarget'):
    for fc in all_fcurves(bpy.data.objects[nm]):
        for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'
try: scene.render.use_motion_blur = True; scene.render.motion_blur_shutter = 0.06
except Exception: pass
os.makedirs(os.path.dirname(os.path.abspath(BLEND)), exist_ok=True)
import json; json.dump([[round(s[0], 3), round(min(s[1], TOTAL), 3)] for s in SHOTS], open(os.path.join(os.path.dirname(os.path.abspath(BLEND)), 'shots.json'), 'w'))
bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(BLEND)); print('SAVED', BLEND, len(bpy.data.objects), 'oggetti')
