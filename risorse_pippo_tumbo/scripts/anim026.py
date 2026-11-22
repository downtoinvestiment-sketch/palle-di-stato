"""TESTA STANDARD di ogni episodio: mondo, quartiere (casa di Pippo a est, casa di Gualtiero a ovest, staccionata, strada), funzioni house_at / tower_at / tree.
Uso: cat templates/head.py scripts/animNNN_body.py > scripts/animNNN.py  (cambia TOTAL e gli import prima).
Test 026 - TUMBO FA HUSS. Salva ../t026/pippo_t026.blend
Personaggi: Pippo e Tumbo ESISTENTI (pippo.py, tumbo.py) invariati; Gualtiero = nuovo vicino ricorrente (props009.gualtiero)."""
import sys, math, os
sys.path.insert(0, os.path.dirname(__file__))
import bpy, numpy as np
from mathutils import Vector, Euler, Matrix
from common import *
from render_setup import *
import set004, props004, props007, props009, props010, props012, props013, props015, props016b, kitlook, lookdev, pippo, tumbo
from set004 import obj, bx, cyl, ball_, MB

FPS = 24; TOTAL = 38.0; NF = int(TOTAL * FPS)
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
# Video 026 - TUMBO FA HUSS, 38,0 s. Si unisce alla testa: templates/head.py + scripts/anim026_body.py -> scripts/anim026.py
# Copione n. 25 (COPIONI.md). Scelte dell'autore (19 novembre 2026): H2 occhi da meme storti e lingua di lato, O2 anelli bianchi
# da fumetto; la ciabatta C2 di props025 per il finale. Formato nuovo: camera a mano sempre, zoom a pugno sulla faccia a ogni HUSS,
# conta delle notti (1, 7, 30) fino alla conseguenza cosmica (il mare). Posti: salotto (x = 400) di giorno e di notte, quartiere
# di notte (case di head.py), il mare (x = -700), il quartiere allagato di giorno. Tempi da audio/words_t026.json. Luce «cinema».
# ===================================================================================================================
import props025, props026, props021, props024, luci, random
import pippo2 as pippo
A = kitlook.A
BLEND = os.environ.get('BLEND026', '../t026/pippo_t026.blend')
FONT = bpy.data.fonts.load(A.font('luckiest'))
M25 = props025.mats025(); M26 = props026.mats026()
rnd = random.Random(26)

# ======================= tempi (dalla voce) =======================
T_H = [3.24, 13.22, 22.12, 36.10]; HD = 0.72               # i quattro HUSS e quanto resta aperta la bocca
T_MIO = 4.18; T_NOME = 5.28; T_ODIO = 6.42; T_ABBAIA = 8.16; T_CODA = 9.20; T_TELE = 10.28
T_NOTTE = 11.68; T_TRE = 12.42; T_SALTA = 13.75
T_C1 = 14.36; T_ME = 14.96; T_C7 = 15.94; T_GUA = 16.52; T_ROMPI = 17.36; T_C30 = 18.66; T_CITTA = 19.36
T_POI = 20.72; T_FORTE = 22.90; T_MARE = 23.72; T_RITIRA = 24.88; T_TORNA = 26.48
T_CASA = 28.40; T_AUTO = 29.02; T_DIVANO = 29.64; T_CIAB = 31.16; T_ODIO2 = 34.30; T_NERO = 37.10
TOTAL = 38.0; NF = int(TOTAL * FPS)

# fasi (posto + ora): SN salotto di notte, SD salotto di giorno, EN fuori di notte, MN il mare, FD alluvione di giorno
FASI = [(0.0, 'SN'), (T_MIO, 'SD'), (T_NOTTE, 'SN'), (T_GUA, 'EN'), (T_C30, 'SN'), (T_CITTA, 'EN'), (T_MARE, 'MN'), (T_CASA, 'FD')]
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
LUNA = luci._luce(prc, 'Luna', 'SUN', (0, 0, 30), (3, 6, 0), 0.0, (0.55, 0.65, 1.0), False)
luci.ombre_pulite(scene, mezza_risoluzione=True)
props021.bagliore(scene, forza=0.3, soglia=1.5)

# ======================= posti =======================
SX = 400.0; MX = -700.0
TBN0 = Vector((SX, 0.0, 0.0))                    # Tumbo nell'hook
TBD = Vector((SX - 0.6, 0.55, 0.0))              # Tumbo di giorno davanti al divano
TBN = Vector((SX - 0.25, 0.95, 0.0))             # Tumbo di notte ai piedi del divano
PSOF = Vector((SX + 0.2, 2.0, -0.045))           # Pippo seduto sul divano (seduta a 0,575, anca 0,7 sopra la radice)
CAL = Vector((SX - 2.3, 2.43, 1.62))             # calendario sul muro di fondo
SVE = Vector((SX - 1.55, 1.95, 0.65))            # sveglia sul tavolino
TETTO = Vector((0.5, 9.5, 5.86))                 # Tumbo sul colmo del tetto di Pippo
TETTO_P = Vector((-1.7, 9.45, 5.86))             # Pippo sul colmo (casa che galleggia)
GU0 = Vector((-14.0, 3.0, 0.0)); GDIR = Vector((0.907, 0.42, 0.0))   # Gualtiero davanti a casa sua, guarda verso casa di Pippo
WT = 2.4                                         # cima dell'acqua nell'alluvione
SL = Vector((2.0, -8.5, 0.0))                    # la ciabatta di Tumbo che galleggia
CAR = Vector((4.5, -6.5, 0.0)); SOF = Vector((-4.5, -5.0, 0.0))

# ======================= set =======================
SAL = props025.salotto(envc, M25, A, x0=SX, font=FONT)
ALL, ALLN = props025.allagamento(prc)
mc = collection('Mare')
MARE = props026.mare(mc, MX)
SCHIUMA = ball_('MareSchiuma', 1.0, (MX, 230, -2), material('M26_schiuma', (0.95, 0.97, 1.0), rough=0.6, emit=(0.8, 0.9, 1.0), emit_strength=1.2), mc, sc=(262, 7, 4))
MARE['onda'].material_slots[0].material = material('M26_onda_mare', (0.08, 0.3, 0.45), rough=0.1, spec=0.9, emit=(0.05, 0.25, 0.4), emit_strength=0.35)
SVG = props026.sveglia(envc, FONT); SVG.location = SVE
CALR, CALN = props026.calendario(envc, FONT); CALR.location = CAL
LUNA_C = props026.luna(prc, (-90, 300, 102), 22, nome='LunaCitta')
SOGLIA = props026.finestre_notte(M['window'])
CASA = bpy.data.objects['Casa']; CASA.rotation_mode = 'XYZ'; CASA0 = CASA.location.copy()
AUTO = []
for k, (aid, p_, rz) in enumerate((('sedan', CAR, 25), ('suv', Vector((10.0, -10.5, 0)), -25), ('taxi', Vector((-11.0, -12.0, 0)), 70))):
    try: AUTO.append((A.modello('kenney/car-kit/' + aid, posizione=(p_.x, p_.y, 0.0), altezza=2.1, rotazione=rz, collezione=prc, appoggia=True), p_, rz, k))
    except Exception as e: print('auto', e)
for a_, _, _, _ in AUTO: a_.rotation_mode = 'XYZ'
DIV = A.modello('kenney/furniture-kit/loungeSofa', posizione=(SOF.x, SOF.y, 0.0), altezza=1.15, rotazione=20.0, collezione=prc, appoggia=True); DIV.rotation_mode = 'XYZ'
DIV_R = DIV.rotation_euler.copy()
TAG = props025.prezzo(prc, M25, FONT, '1000 €', nome='Prezzo'); TAG.rotation_mode = 'XYZ'; TAG.scale = (1.6, 1.6, 1.6)

# ======================= personaggi =======================
P = pippo.build_pippo(chc); Tb = tumbo.build_tumbo(chc, scale=0.75); GU = props009.gualtiero(chc, G9)
for r in (P['root'], Tb['root'], GU['root']): r.rotation_mode = 'XYZ'
for nm in 'LR': P['shoulder' + nm].rotation_mode = 'QUATERNION'
for nm in ('shoulderL', 'shoulderR', 'hipL', 'hipR', 'head'): GU[nm].rotation_mode = 'XYZ'
OCC = props026.occhiaie(chc, P['head'])
BOCCA = props026.bocca_huss(chc, M26, Tb['head'], 'H2')
OCCHI = props026.occhi_giganti(chc, M26, Tb['head'], storti=True)
TELE = props026.telecomando(chc); TELE.parent = Tb['head']; TELE.location = (0.05, -0.36, -0.1); TELE.rotation_euler = (0.2, 0, 0.55)
CS = props025.ciabatta(prc, M25, 'C2', L=1.25, nome='CiabattaZattera'); CS.rotation_mode = 'XYZ'
bpy.context.view_layer.update()
_zs = [(c.matrix_world @ Vector(v)).z for c in [CS] + list(CS.children_recursive) if c.type == 'MESH' for v in c.bound_box]
CS_TOP = max(_zs) - CS.location.z; CS_BOT = min(_zs) - CS.location.z
_su = bpy.data.objects['CiabattaZatteraSuola']; _fa = bpy.data.objects['CiabattaZatteraFascia']
CS_SUOLA = _su.location.z + _su.dimensions.z / 2           # Tumbo sta sulla suola, dietro la fascia
CS_TY = _fa.location.y + _fa.dimensions.y / 2 + 0.2 if _fa.location.y < 0 else _fa.location.y - _fa.dimensions.y / 2 - 0.2
TB_YAW_C = 0.0 if _fa.location.y < 0 else PI
def cs_z(t): return WT - 0.4 * (CS_TOP - CS_BOT) - CS_BOT + 0.035 * math.sin(t * 1.5)   # quota della ciabatta che galleggia
ONDE = []                                        # (onda, inizio, durata, scala finale)
for k, h in enumerate(T_H):
    o = props026.onda_huss(chc, M26, 'O2', n=3, nome='OndaHuss%d' % k); o.parent = Tb['head']; o.location = (0, -0.45, -0.08); ONDE.append((o, h, 0.6, 0.6))
OG = props026.onda_huss(chc, M26, 'O2', n=3, nome='OndaGigante'); OG.parent = Tb['head']; OG.location = (0, -0.45, -0.08)
ANM = [props026.anello_piatto(mc, M26, 'AnelloMare%d' % k) for k in range(3)]
PESCI = []
for k in range(8):
    pz = props026.pesce(mc, k, nome='Pesce%d' % k); pz.rotation_mode = 'XYZ'; pz.scale = (3, 3, 3)
    PESCI.append((pz, Vector((MX + rnd.uniform(-6, 6), rnd.uniform(0.0, 9.0), -5.55)), rnd.uniform(0, 6)))

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
IN_S = iv('SN', 'SD'); OUT = iv('EN', 'FD')
for nm in 'LR': show_only(Tb['eye' + nm], [(0.0, T_H[0])])
for o in OCCHI: show_only(o, [(T_H[0], TOTAL + 1)])
show_only(TELE, [(T_TELE, T_NOTTE)])
for o, h, d, _ in ONDE: show_only(o, [(h, h + d)])
show_only(OG, [(T_H[2], T_MARE)])
show_only(BOCCA, [(T_H[0] - 0.05, T_H[0] + HD + 0.2), (T_H[1] - 0.05, T_H[1] + HD + 0.2), (T_H[2] - 0.05, T_H[2] + HD + 0.2), (T_H[3] - 0.05, TOTAL + 1)])
for o_ in SAL['soffitto']: show_only(o_, IN_S)
show_only(CALN['1'], [(0.0, T_C7)]); show_only(CALN['7'], [(T_C7, T_C30)]); show_only(CALN['30'], [(T_C30, TOTAL + 1)])   # i figli prima del padre
show_only(SAL['root'], IN_S); show_only(SVG, IN_S); show_only(CALR, IN_S)
for o in ANM: show_only(o, [(T_MARE, T_RITIRA)])
show_only(MARE['onda'], [(T_TORNA, T_CASA)]); show_only(SCHIUMA, [(T_TORNA, T_CASA)])
for o in list(mc.objects):
    if o.parent is None and o.name not in NEVER: show_only(o, iv('MN'))
show_only(ALL, iv('FD')); show_only(LUNA_C, iv('EN'))
for a_, _, _, _ in AUTO: show_only(a_, OUT)
show_only(DIV, iv('FD')); show_only(TAG, iv('FD')); show_only(CS, iv('FD'))
show_only(GU['root'], [(T_GUA, T_C30)])
show_only(P['root'], [(T_MIO, T_GUA), (T_CASA, TOTAL + 1)])
show_only(Tb['root'], [(0.0, T_GUA), (T_C30, T_C30 + 0.7), (T_POI - 0.1, T_MARE), (T_CIAB, TOTAL + 1)])
for o in list(envc.objects):
    if o.parent is None and o.name not in NEVER: show(o, OUT)

# ======================= luce per fase =======================
def chiavi(owner, attr, valori):
    for (t_, v) in valori:
        setattr(owner, attr, v); owner.keyframe_insert(attr, frame=fr(t_))
def per_fase(owner, attr, vals, default=0.0):
    chiavi(owner, attr, [(t0, vals.get(c, default)) for (t0, c) in FASI])
per_fase(SUN.data, 'energy', {'FD': 4.6})
per_fase(LUNA.data, 'energy', {'EN': 0.75, 'MN': 0.9, 'SN': 0.0})
per_fase(CIELO.inputs['Strength'], 'default_value', {'SN': 0.02, 'SD': 0.05, 'EN': 0.03, 'MN': 0.035, 'FD': 0.42})
if VISTA: per_fase(VISTA.inputs['Strength'], 'default_value', {'FD': V0})
per_fase(scene.view_settings, 'exposure', {'SN': -0.9, 'SD': 0.15, 'EN': 0.25, 'MN': 0.05, 'FD': 0.25})
chiavi(SOGLIA.outputs[0], 'default_value', [(0.0, 0.0), (T_GUA - 0.04, 0.0), (T_GUA, 0.35), (T_C30 - 0.04, 0.35), (T_C30, 0.0), (T_CITTA - 0.04, 0.0), (T_CITTA, 0.3),
                                            (T_CITTA + 1.0, 1.0), (T_CASA - 0.04, 1.0), (T_CASA, 0.0)])
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
PLAF_S = area('PlafSalotto', (SX, 0.0, 4.1), 420.0, 3.0)
LS = luci.cinema(prc, (SX - 0.2, 0.8, 1.0), (SX - 0.2, -2.6, 1.3), distanza=3.4, lato=-1, forza=0.55, nome='CinemaS')
LSN = luci.cinema(prc, (SX - 0.1, 1.0, 0.8), (SX, -2.4, 1.2), distanza=3.0, lato=-1, forza=0.22, nome='CinemaSN', riempimento=0.4, controluce=1.8)
LUNA_S = area('LunaSalotto', (SX - 3.2, -0.4, 2.4), 260.0, 1.6, (0.45, 0.58, 1.0)); LUNA_S.rotation_euler = (0, -1.1, 0)
for l_ in LSN.values():                                                 # di notte: lampada calda debole, il blu della luna domina
    if 'Chiave' in l_.name: l_.data.energy *= 0.35; l_.data.color = (1.0, 0.72, 0.45)
    if 'Controluce' in l_.name: l_.data.color = (0.45, 0.6, 1.0); l_.data.energy *= 1.3
LG = luci.cinema(prc, GU0 + Vector((0, 0, 1.3)), GU0 + GDIR * 3.0 + Vector((0, 0, 1.5)), distanza=3.5, lato=1, forza=0.5, nome='CinemaG', riempimento=0.5, controluce=1.5)
PORTA = bpy.data.lights.new('LucePorta', 'POINT'); PORTA.energy = 120.0; PORTA.color = (1.0, 0.72, 0.4); PORTA.shadow_soft_size = 0.2
PO = bpy.data.objects.new('LucePorta', PORTA); prc.objects.link(PO); PO.location = GU0 + Vector((-1.2, -0.8, 2.6))
LT = luci.cinema(prc, TETTO + Vector((0, 0, 0.5)), TETTO + Vector((1.5, -4.0, -0.6)), distanza=5.0, lato=-1, forza=0.6, nome='CinemaT', riempimento=0.5, controluce=1.6)
LM = luci.cinema(prc, Vector((MX, 15.0, -3.0)), Vector((MX, -30.0, 4.0)), distanza=26.0, lato=1, forza=0.4, nome='CinemaM', riempimento=0.5, controluce=1.5)
LF = luci.cinema(prc, SL + Vector((0, 0, WT + 0.5)), SL + Vector((0.5, -3.0, WT + 1.0)), distanza=4.0, lato=-1, forza=0.7, nome='CinemaF')
LP = luci.cinema(prc, TETTO_P + Vector((0, 0, 3.0)), TETTO_P + Vector((0.3, -2.5, 3.0)), distanza=3.5, lato=-1, forza=0.6, nome='CinemaP')
on_off([PLAF_S] + list(LS.values()), iv('SD')); on_off(list(LSN.values()) + [LUNA_S], iv('SN'))
on_off(list(LG.values()) + [PO], [(T_GUA, T_C30)]); on_off(list(LT.values()), [(T_CITTA, T_MARE)]); on_off(list(LM.values()), iv('MN'))
on_off(list(LF.values()) + list(LP.values()), iv('FD'))
LIGHTS = [SUN.data, LUNA.data, PLAF_S.data, LUNA_S.data, PORTA] + [l_.data for d_ in (LS, LSN, LG, LT, LM, LF, LP) for l_ in d_.values()]

# ======================= pose =======================
def qdir(d, rest=(0, 0, -1)): return Vector(rest).rotation_difference(Vector(d).normalized())
def yaw_to(a, b): return math.atan2(b[0] - a[0], -(b[1] - a[1]))
def mixv(a, b, u): return tuple(Vector(a).lerp(Vector(b), u))
def braccia(nome, forza=1.0):
    b = pippo.EMOZIONI_FORTI[nome]['braccia']; return {'aL': tuple(Vector((0, 0, -1)).lerp(Vector(b[0]).normalized(), forza)), 'aR': tuple(Vector((0, 0, -1)).lerp(Vector(b[1]).normalized(), forza))}
ARMS_SIT = dict(aL=(-0.3, -0.55, -0.78), aR=(0.3, -0.55, -0.78))
def jit(t, a=0.02, f=37.0): return a * math.sin(t * f) * math.sin(t * f * 0.71 + 1.3)
def huss(t):
    """quanto e' spalancata la bocca (0..1) in questo istante."""
    for h in T_H:
        if h - 0.02 <= t < h + HD + 0.15: return ramp(t, h, h + 0.07) * (1 - ramp(t, h + HD, h + HD + 0.12))
    return 0.0

def casa_m(t):
    """matrice della casa di Pippo che galleggia (dall'alluvione in poi)."""
    if t < T_CASA: return Matrix.Translation(CASA0), (0.0, 0.0, 0.0)
    rot = (0.035 * math.sin(t * 0.9), 0.03 * math.cos(t * 0.7 + 1), 0.06 + 0.02 * math.sin(t * 0.4))
    loc = CASA0 + Vector((0.3 * math.sin(t * 0.3), 0, 1.45 + 0.06 * math.sin(t * 1.3)))
    return Matrix.Translation(loc) @ Euler(rot).to_matrix().to_4x4(), rot

def pp(t):
    """Pippo: loc, yaw, lean, roll (radice), bend (busto), head, braccia, anche."""
    S_ = dict(loc=Vector((0, 0, -50)), yaw=0.0, lean=0.0, roll=0.0, bend=0.0, head=(0, 0, 0), hL=0.0, hR=0.0, **ARMS_SIT)
    if T_MIO <= t < T_GUA:                                              # sul divano
        S_.update(loc=PSOF.copy(), hL=-PI / 2, hR=-PI / 2, bend=0.08, head=(0.12, 0, 0.04 * math.sin(t * 0.7)))
        if T_ODIO <= t < T_NOTTE: S_.update(head=(0.02, 0, 0))                                          # «e l'odio, cazzo»: fisso in camera
        if T_TRE - 0.3 <= t < T_SALTA:                                    # dorme seduto, testa di lato
            S_.update(head=(0.3, 0.3, 0.15), bend=0.12, aL=(-0.2, -0.3, -0.93), aR=(0.25, -0.2, -0.95))
        if T_SALTA <= t < T_C1:                                           # il salto sul divano
            u = ramp(t, T_SALTA, T_SALTA + 0.45); z = 0.75 * math.sin(PI * min(1.0, (t - T_SALTA) / 0.5)) if t < T_SALTA + 0.5 else 0.0
            S_.update(loc=PSOF + Vector((0, -0.1 * u, max(0.0, z))), hL=-PI / 2 + 0.6 * math.sin(PI * min(1, (t - T_SALTA) / 0.5)), hR=-PI / 2 + 0.5 * math.sin(PI * min(1, (t - T_SALTA) / 0.5)),
                      head=(-0.15, 0, 0), **braccia('spaventato'))
        if t >= T_C1: S_.update(head=(0.0, 0, 0), bend=0.02, aL=(-0.3, -0.6, -0.74), aR=(0.3, -0.6, -0.74))  # sveglio, occhi sbarrati
    elif t >= T_CASA:                                                   # sul tetto della casa che galleggia
        Mh, rot = casa_m(t); p = Mh @ (TETTO_P - CASA0)
        S_.update(loc=p, yaw=-0.12, lean=rot[0], roll=rot[1], head=(0.02, 0, 0), aL=(-0.12, 0, -1), aR=(0.12, 0, -1))
    return S_

def tp(t):
    """Tumbo: loc, yaw, head (x, y, z), tail, chew."""
    m = huss(t)
    S_ = dict(loc=TBN0.copy(), yaw=0.0, head=(0, 0, 0), chew=0.0, tail=(-1.05 + 0.03 * math.sin(t * 40), 0, 0), pitch=0.0)
    if t < T_MIO:
        S_.update(loc=TBN0.copy(), yaw=0.0)
    elif t < T_NOTTE:                                                   # di giorno, davanti al divano
        S_.update(loc=TBD.copy(), yaw=yaw_to(TBD, (SX - 0.25, -1.4)))
        if T_NOME <= t < T_ODIO: S_.update(head=(0.0, 0.42 * ramp(t, T_NOME + 0.2, T_NOME + 0.45), 0))   # testa storta: «si chiama Tumbo»
        if T_TELE <= t < T_NOTTE: S_.update(chew=1.0)
    elif t < T_GUA + 0.5:                                               # di notte ai piedi del divano
        S_.update(loc=TBN.copy(), yaw=yaw_to(TBN, (SX - 0.15, -0.3)))
    elif t < T_POI - 0.1:
        S_.update(loc=TBN.copy(), yaw=0.0)
    elif t < T_MARE:                                                    # sul colmo del tetto, la luna dietro
        S_.update(loc=TETTO.copy(), yaw=0.08)
    else:                                                               # sulla ciabatta
        z = cs_z(t) + CS_SUOLA - 0.005
        S_.update(loc=Vector((SL.x, SL.y + CS_TY, z)), yaw=0.03 * math.sin(t * 0.8), pitch=0.03 * math.sin(t * 1.1))
    hx, hy, hz = S_['head']
    S_['head'] = (hx - 0.3 * m + 0.12 * S_['chew'] * math.sin(t * 11), hy + jit(t, 0.06, 41) * m, hz + 0.3 * S_['chew'] * math.sin(t * 8.5))
    S_['m'] = m
    return S_

def gp(t):
    """Gualtiero in canottiera davanti a casa: urla verso casa di Pippo (verso la camera)."""
    yaw = yaw_to(GU0, GU0 + GDIR); f_ = ramp(t, T_ROMPI - 0.1, T_ROMPI + 0.15)
    return dict(loc=GU0 + Vector((jit(t, 0.02, 19), 0, 0)), yaw=yaw, lean=0.12, head=(0.15 * math.sin(t * 17) * 0.4, 0, 0.12 * math.sin(t * 5)),
                sR=(-0.4 - 1.9 * f_ + 0.35 * f_ * math.sin(t * 24), 0, 0.15), sL=(-0.25, 0, -0.55))

# ======================= chiavi =======================
def K(o, f, loc=None, rot=None, scale=None):
    if loc is not None: o.location = loc; o.keyframe_insert('location', frame=f)
    if rot is not None: o.rotation_euler = rot; o.keyframe_insert('rotation_euler', frame=f)
    if scale is not None: o.scale = scale if isinstance(scale, (tuple, list)) else (scale,) * 3; o.keyframe_insert('scale', frame=f)
TELE_POS = []                                                           # dove sta la bocca, per le briciole del telecomando
for f in range(1, NF + 1):
    t = (f - 1) / FPS
    s = pp(t)
    K(P['root'], f, tuple(s['loc']), (s['lean'], s['roll'], s['yaw'])); K(P['body'], f, rot=(s['bend'], 0, 0)); K(P['head'], f, rot=s['head'])
    for nm, k_ in (('L', 'aL'), ('R', 'aR')):
        sh = P['shoulder' + nm]; sh.rotation_quaternion = qdir(s[k_]); sh.keyframe_insert('rotation_quaternion', frame=f)
    for nm, k_ in (('L', 'hL'), ('R', 'hR')): K(P['hip' + nm], f, rot=(s[k_], 0, 0))
    s = tp(t)
    K(Tb['root'], f, tuple(s['loc']), (s['pitch'], 0, s['yaw']), 0.75)
    K(Tb['head'], f, rot=s['head']); K(Tb['tail'], f, rot=s['tail'])
    m = s['m']
    K(BOCCA, f, scale=(max(0.001, 1.35 * m),) * 3)
    for o in OCCHI: K(o, f, scale=(1 + 0.4 * m,) * 3)
    if T_TELE <= t < T_NOTTE: TELE_POS.append((t, s['loc'] + Matrix.Rotation(s['yaw'], 3, 'Z') @ Vector((0, -0.55, 0.45))))
    for o, h, d, sc in ONDE:
        if h - 0.05 <= t < h + d + 0.05: u = max(0.0, min(1.0, (t - h) / d)); K(o, f, scale=(0.1 + sc * u ** 0.8,) * 3)
    if T_H[2] - 0.05 <= t < T_MARE + 0.05:
        u = max(0.0, min(1.0, (t - T_H[2]) / (T_MARE - T_H[2]))); K(OG, f, scale=(0.2 + 60.0 * u ** 1.3,) * 3)
    g = gp(t)
    K(GU['root'], f, tuple(g['loc']), (g['lean'], 0, g['yaw'])); K(GU['shoulderL'], f, rot=g['sL']); K(GU['shoulderR'], f, rot=g['sR']); K(GU['head'], f, rot=g['head'])
    # calendario: il numero nuovo arriva con uno scatto
    for n_, t0 in (('1', T_C1), ('7', T_C7), ('30', T_C30)):
        K(CALN[n_], f, scale=(1.0 + 0.5 * (1 - ramp(t, t0, t0 + 0.12)) if t >= t0 else 1.0,) * 3)
    # la casa che galleggia, l'acqua, le auto, il divano, la ciabatta
    Mh, rot = casa_m(t); K(CASA, f, tuple(Mh.translation), rot)
    K(ALL, f, (0, 0, WT - 0.5)); ALLN.inputs['W'].default_value = t * 0.3; ALLN.inputs['W'].keyframe_insert('default_value', frame=f)
    for a_, p0, rz, k in AUTO:
        K(a_, f, (p0.x + 0.3 * math.sin(t * 0.6 + k), p0.y, WT - 0.8 + 0.06 * math.sin(t * 2.0 + k)), (0.05 * math.sin(t * 1.4 + k), 0.06 * math.cos(t * 1.2 + k), math.radians(rz) + 0.1 * math.sin(t * 0.5 + k)))
    dz = WT - 0.42 + 0.05 * math.sin(t * 1.7)
    K(DIV, f, (SOF.x, SOF.y, dz), (DIV_R.x + 0.04 * math.sin(t * 1.3), DIV_R.y + 0.03 * math.cos(t * 1.1), DIV_R.z + 0.08 * math.sin(t * 0.4)))
    K(TAG, f, (SOF.x + 0.35, SOF.y - 0.62, dz + 1.55), (0.06 * math.sin(t * 2.6), 0, 0.35 + 0.05 * math.sin(t * 1.9)))
    K(CS, f, (SL.x, SL.y, cs_z(t)), (0.03 * math.sin(t * 1.1), 0.02 * math.sin(t * 0.9), 0.03 * math.sin(t * 0.8)))
    # il mare: si ritira, l'onda torna
    if t < T_RITIRA + 0.05: wz = -0.5
    elif t < T_TORNA: wz = -0.5 - 6.5 * ramp(t, T_RITIRA + 0.05, T_RITIRA + 0.55)
    else: wz = -7.0 + 6.5 * ramp(t, T_TORNA + 0.9, T_CASA)
    K(MARE['acqua'], f, (MX, 290.0, wz)); MARE['nodo'].inputs['W'].default_value = t * 0.25; MARE['nodo'].inputs['W'].keyframe_insert('default_value', frame=f)
    u = ramp(t, T_TORNA, T_CASA); oy = 230.0 - 242.0 * (u ** 1.3); oz = -20.0 + 20.0 * min(1.0, u * 1.6)
    K(MARE['onda'], f, (MX, oy, oz)); K(SCHIUMA, f, (MX, oy - 4.0, oz + 18.6))
    for k, an in enumerate(ANM):
        r_ = max(1.0, 25.0 + 260.0 * ramp(t, T_MARE, T_RITIRA + 0.1) - 55.0 * k)
        K(an, f, (MX, 300.0, 30.0), (PI / 2, 0, 0), scale=(r_, r_, r_))
    for pz, p0, ph in PESCI:
        hop = 0.6 * abs(math.sin(t * 6.5 + ph)) if t >= T_RITIRA + 0.7 else 0.0
        K(pz, f, tuple(p0 + Vector((0, 0, hop))), (0, PI / 2 + 0.8 * math.sin(t * 13 + ph), ph))

# ======================= briciole del telecomando =======================
M_BRI = material('M26_briciole', (0.03, 0.03, 0.035), rough=0.4)
def briciole(n, centro, t0, v0, coll, nome='Briciola', g=9.8):
    for k in range(n):
        o = obj(nome, set004.box_c(), (0, 0, -90), (0.025, 0.02, 0.012), M_BRI if k % 3 else bpy.data.materials['M26_tasto%d' % (k % 4)], coll); o.rotation_mode = 'XYZ'
        a = rnd.uniform(0, 2 * PI); v = Vector((math.cos(a) * rnd.uniform(0.3, 1.0), math.sin(a) * rnd.uniform(0.3, 1.0) - 0.6, rnd.uniform(0.5, 1.2))) * v0
        spin = Vector((rnd.uniform(-12, 12), rnd.uniform(-12, 12), rnd.uniform(-12, 12)))
        for f in range(max(1, fr(t0) - 1), min(NF, fr(t0 + 0.8)) + 1):
            tt = (f - 1) / FPS - t0
            if tt < 0: K(o, f, (0, 0, -90)); continue
            p = Vector(centro) + v * tt + Vector((0, 0, -0.5 * g * tt * tt)); p.z = max(0.005, p.z)
            K(o, f, tuple(p), tuple(spin * tt))
        show_only(o, [(t0, min(TOTAL + 1, t0 + 0.8))])
for tc in (10.62, 10.98, 11.3):
    pos = min(TELE_POS, key=lambda q: abs(q[0] - tc))[1]
    briciole(7, pos, tc, 1.3, prc)

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
    seg = pippo._segni(P)
    ex_ = list(e.get('extra', ()))
    for k, g in seg.items():
        g.scale = (1, 1, 1) if (k in ex_ and forza > 0.3) else (0.001,) * 3
        g.keyframe_insert('scale', frame=f)
def emo(t, nome, forza=1.0, **extra):
    if _emo_last[0] and t - 0.06 > _emo_last[0][2]: _emo_key(fr(t - 0.06), _emo_last[0][0], _emo_last[0][1], _emo_last[0][3])
    _emo_key(fr(t), nome, forza, extra); _emo_last[0] = (nome, forza, t, extra)
def tex(t, **k): _ex('t', lambda f, **kk: tumbo.tumbo_express(Tb, f, **kk), t, k)
emo(0.0, 'normale', 1.0, eye_open=0.55); emo(T_ODIO, 'arrabbiato', 0.35, eye_open=0.5); emo(T_ABBAIA, 'normale', 1.0, eye_open=0.55)
emo(T_TRE - 0.3, 'normale', 1.0, eye_open=0.0, mouth_open=0.25); emo(T_SALTA, 'spaventato', 1.0); emo(T_C1, 'sorpreso', 0.7, eye_open=1.2)
emo(T_CASA, 'normale', 1.0, eye_open=0.5); emo(T_ODIO2, 'arrabbiato', 0.3, eye_open=0.45)
tex(0.0, tongue=0.0, brow=0.0); tex(T_H[0], tongue=0.0, brow=0.5); tex(T_MIO, tongue=0.7, brow=0.3); tex(T_ABBAIA, tongue=0.0, brow=0.0); tex(T_CODA, tongue=0.7, brow=0.3)
tex(T_TELE, tongue=0.0, brow=0.2); tex(T_NOTTE, tongue=0.0, brow=-0.2); tex(T_CIAB, tongue=0.8, brow=0.3); tex(T_H[3], tongue=0.0, brow=0.5)

# ======================= effetti =======================
FXC = prc
def fx(name, pos, w, t0, dur, **k): return A.effetto(name, posizione=tuple(pos), larghezza=w, animazione=(fr(t0), int(dur * FPS)), collezione=FXC, **k)
fx('emoticon/sleeps', PSOF + Vector((0.35, -0.2, 1.95)), 0.35, T_TRE, 0.8)
fx('emoticon/exclamations', PSOF + Vector((0.3, -0.3, 2.3)), 0.4, T_SALTA + 0.1, 0.6)
fx('emoticon/anger', GU0 + Vector((0.3, 0.3, 2.15)), 0.4, T_GUA + 0.2, 1.0)
fx('emoticon/anger', GU0 + Vector((-0.3, 0.1, 2.25)), 0.45, T_ROMPI + 0.1, 1.1)
fx('emoticon/question', TBD + Vector((0.15, -0.3, 0.95)), 0.22, T_NOME + 0.35, 0.9)
for k in range(10): fx('schizzi/splat%02d' % (k * 3), (MX + rnd.uniform(-14, 14), -24 + rnd.uniform(-3, 2), rnd.uniform(2, 9)), rnd.uniform(3.0, 6.0), T_CASA - 0.45 + 0.03 * k, 0.5, colore=(0.75, 0.9, 1.0), opacita=0.95)
for k in range(6): fx('schizzi/splat%02d' % (k * 4 + 1), (SL.x + rnd.uniform(-1.2, 1.2), SL.y + rnd.uniform(-0.8, 0.8), WT + rnd.uniform(0.2, 0.8)), rnd.uniform(0.4, 0.8), T_H[3] + 0.04 * k, 0.5, colore=(0.75, 0.9, 1.0), opacita=0.9)

# nero finale (davanti alla camera)
NERO = obj('Nero', shared_mesh('cyl:1:1'), (0, 0, -0.05), (0.3, 0.3, 0.001), props026.mat_nero(), cac, rot=(0, 0, 0), parent=cam)
show_only(NERO, [(T_NERO, TOTAL + 1)])

# ======================= camera =======================
def tz(): return cs_z(0.0) + CS_SUOLA
PS_Z = 1.455                                                           # testa di Pippo seduto
SHOTS = [  # t0, t1, camera da, a, mira da, a, lente, diaframma, pugno (zoom a ogni HUSS), mano (tremolio)
    (0.0, T_H[0], (SX + 0.5, -3.0, 0.95), (SX + 0.25, -1.9, 0.75), (SX, 0.0, 0.55), (SX, 0.0, 0.57), 32, 4.0, 1.0, 0.8),                                # 01 di notte: un cane fermo
    (T_H[0], T_MIO, (SX + 0.15, -1.85, 0.64), (SX + 0.14, -1.8, 0.64), (SX, -0.5, 0.58), (SX, -0.5, 0.58), 40, 4.0, 1.85, 1.6),                             # 02 HUSS
    (T_MIO, T_NOME, (SX - 0.2, -1.5, 0.85), (SX - 0.25, -1.3, 0.82), (SX - 0.45, 0.9, 0.7), (SX - 0.45, 0.9, 0.72), 30, 6.0, 1.0, 1.0),                # 03 il mio lo fa
    (T_NOME, T_ODIO, (SX - 0.28, -1.22, 0.62), (SX - 0.29, -1.12, 0.62), (SX - 0.51, 0.06, 0.58), (SX - 0.51, 0.06, 0.58), 50, 3.0, 1.0, 1.0),               # 04 si chiama Tumbo
    (T_ODIO, T_ABBAIA, (SX + 0.25, 0.35, PS_Z - 0.05), (SX + 0.24, 0.5, PS_Z - 0.04), (SX + 0.2, 2.0, PS_Z - 0.05), (SX + 0.2, 2.0, PS_Z - 0.05), 32, 3.0, 1.0, 1.0),  # 05 e l'odio, cazzo
    (T_ABBAIA, T_CODA, (SX - 0.3, -1.12, 0.58), (SX - 0.31, -1.0, 0.58), (SX - 0.51, 0.06, 0.58), (SX - 0.51, 0.06, 0.58), 55, 3.0, 1.0, 0.4),          # 06 non abbaia
    (T_CODA, T_TELE, (SX - 1.95, 1.3, 0.42), (SX - 1.85, 1.3, 0.44), (SX - 0.62, 0.7, 0.45), (SX - 0.62, 0.7, 0.45), 35, 4.0, 1.0, 0.7),             # 07 non scodinzola
    (T_TELE, T_NOTTE, (SX - 0.2, -1.15, 0.52), (SX - 0.22, -1.05, 0.52), (SX - 0.51, 0.06, 0.5), (SX - 0.51, 0.06, 0.5), 50, 3.0, 1.0, 1.2),               # 08 i telecomandi
    (T_NOTTE, T_TRE, (SX - 1.5, 1.25, 0.8), (SX - 1.52, 1.35, 0.78), (SVE.x, SVE.y, SVE.z + 0.07), (SVE.x, SVE.y, SVE.z + 0.07), 40, 2.8, 1.0, 0.6),  # 09 alle tre
    (T_TRE, T_H[1], (SX + 0.1, -2.2, 1.05), (SX + 0.05, -1.9, 1.0), (SX, 1.4, 0.85), (SX, 1.4, 0.85), 28, 5.0, 1.0, 0.6),                               # 10 dorme, Tumbo lo guarda
    (T_H[1], T_SALTA, (SX - 0.1, -0.85, 0.63), (SX - 0.1, -0.8, 0.63), (SX - 0.21, 0.45, 0.58), (SX - 0.21, 0.45, 0.58), 38, 4.0, 1.85, 1.6),          # 11 HUSS
    (T_SALTA, T_C1, (SX + 0.2, -2.5, 1.3), (SX + 0.2, -2.4, 1.3), (SX + 0.2, 1.7, 1.35), (SX + 0.2, 1.7, 1.4), 24, 6.0, 1.0, 1.8),                     # 12 il salto
    (T_C1, T_ME, (CAL.x, 1.45, CAL.z), (CAL.x, 1.75, CAL.z), tuple(CAL), tuple(CAL), 40, 4.0, 1.0, 1.0),                                              # 13 notte 1
    (T_ME, T_C7, (SX + 0.28, 0.35, PS_Z - 0.03), (SX + 0.26, 0.5, PS_Z - 0.02), (SX + 0.2, 2.0, PS_Z - 0.05), (SX + 0.2, 2.0, PS_Z - 0.05), 32, 3.0, 1.0, 1.2),      # 14 ha svegliato me
    (T_C7, T_GUA, (CAL.x, 1.45, CAL.z), (CAL.x, 1.75, CAL.z), tuple(CAL), tuple(CAL), 40, 4.0, 1.0, 1.0),                                             # 15 notte 7
    (T_GUA, T_C30, tuple(GU0 + GDIR * 3.0 + Vector((0, 0, 1.75))), tuple(GU0 + GDIR * 2.4 + Vector((0, 0, 1.72))), tuple(GU0 + Vector((0, 0, 1.68))), tuple(GU0 + Vector((0, 0, 1.72))), 30, 4.0, 1.0, 1.4),  # 16 Gualtiero
    (T_C30, T_CITTA, (CAL.x, 1.45, CAL.z), (CAL.x, 1.75, CAL.z), tuple(CAL), tuple(CAL), 40, 4.0, 1.0, 1.0),                                          # 17 notte 30
    (T_CITTA, T_POI, (-28.0, -42.0, 24.0), (-24.0, -40.0, 22.0), (0.0, 6.0, 2.0), (2.0, 6.0, 2.0), 22, 22, 1.0, 0.8),                                  # 18 tutta la citta'
    (T_POI, T_H[2], (1.6, 6.0, 5.2), (1.3, 6.6, 5.4), (0.5, 9.5, 6.35), (0.5, 9.5, 6.4), 30, 8.0, 1.0, 0.8),                                          # 19 sul tetto
    (T_H[2], T_FORTE, (0.62, 7.6, 6.5), (0.61, 7.65, 6.5), (0.54, 9.0, 6.41), (0.54, 9.0, 6.41), 38, 6.0, 1.85, 1.6),                                     # 20 HUSS
    (T_FORTE, T_MARE, (12.0, -30.0, 30.0), (20.0, -55.0, 55.0), (0.0, 9.5, 8.0), (0.0, 9.5, 10.0), 22, 22, 1.0, 1.2),                                 # 21 cosi' forte
    (T_MARE, T_RITIRA, (MX, -30.0, 3.2), (MX, -29.0, 3.3), (MX, 200.0, 10.0), (MX, 200.0, 10.0), 20, 22, 1.0, 0.8),                                    # 22 fino al mare
    (T_RITIRA, T_TORNA, (MX + 2.5, -15.0, 3.2), (MX + 2.0, -13.0, 2.6), (MX, 5.0, -5.0), (MX, 4.0, -5.3), 24, 22, 1.0, 0.6),                         # 23 il mare si ritira
    (T_TORNA, T_CASA, (MX, -27.0, 3.0), (MX, -28.0, 2.6), (MX, 60.0, 6.0), (MX, 30.0, 10.0), 22, 22, 1.0, 1.4),                                        # 24 e torna tutto insieme
    (T_CASA, T_AUTO, (13.0, -12.0, 7.0), (12.0, -11.0, 6.8), (0.0, 9.5, 5.0), (0.0, 9.5, 5.0), 26, 22, 1.0, 0.8),                                      # 25 casa mia
    (T_AUTO, T_DIVANO, (8.5, -11.5, 3.6), (8.1, -11.0, 3.5), (CAR.x, CAR.y, 2.7), (CAR.x, CAR.y, 2.7), 32, 16, 1.0, 0.8),                              # 26 la macchina
    (T_DIVANO, T_CIAB, (-2.6, -8.8, 3.3), (-2.8, -8.4, 3.25), (SOF.x, SOF.y, 2.95), (SOF.x, SOF.y, 2.95), 35, 11, 1.0, 0.8),                           # 27 il divano da mille euro
    (T_CIAB, T_ODIO2, (SL.x - 1.32, SL.y - 1.88, tz() + 0.75), (SL.x + 1.32, SL.y - 1.88, tz() + 0.75), (SL.x, SL.y + CS_TY, tz() + 0.35), (SL.x, SL.y + CS_TY, tz() + 0.35), 35, 6.0, 1.0, 0.9),  # 28 sopravvissuto su una ciabatta
    (T_ODIO2, T_H[3], (-1.45, 7.6, 8.7), (-1.47, 7.75, 8.72), (-1.7, 9.45, 8.78), (-1.7, 9.45, 8.78), 45, 4.0, 1.0, 0.7),                              # 29 l'odio, cazzo
    (T_H[3], TOTAL + 0.1, (SL.x + 0.12, SL.y + CS_TY - 1.85, tz() + 0.62), (SL.x + 0.11, SL.y + CS_TY - 1.8, tz() + 0.62), (SL.x, SL.y + CS_TY - 0.5, tz() + 0.55), (SL.x, SL.y + CS_TY - 0.5, tz() + 0.55), 38, 4.0, 1.85, 1.6),  # 30 HUSS
]
SHAKES = [(h, 0.035, 0.6) for h in T_H] + [(T_SALTA, 0.02, 0.4), (T_ROMPI, 0.02, 0.5), (T_TORNA + 0.8, 0.03, 1.1), (T_TORNA + 1.4, 0.06, 0.55)]
def hn(t, s): return 0.6 * math.sin(t * 1.7 + s) + 0.3 * math.sin(t * 3.3 + 2.1 * s) + 0.12 * math.sin(t * 7.9 + 3.7 * s)
for f in range(1, NF + 1):
    t = (f - 1) / FPS
    s_ = next((s for s in SHOTS if s[0] <= t < s[1]), SHOTS[-1]); u = sm((t - s_[0]) / (s_[1] - s_[0]))
    cl = Vector(lerp(s_[2], s_[3], u)); tl = Vector(lerp(s_[4], s_[5], u))
    if s_[0] == T_ODIO2:                                               # Pippo sulla casa che galleggia: la camera va con lui
        hp = pp(t)['loc'] + Vector((0, 0, 1.42)); cl = hp + Vector((0.25, -1.8 + 0.15 * u, -0.08)); tl = hp
    d = (tl - cl).length
    cl = cl + Vector((hn(t, 1), 0.5 * hn(t, 2), hn(t, 3))) * s_[9] * d * 0.02; tl = tl + Vector((hn(t, 4), 0, hn(t, 5))) * s_[9] * d * 0.008
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
for d in [bpy.data.materials['M25_alluvione'].node_tree, bpy.data.materials['M26_mare'].node_tree, M['window'].node_tree]: lin(d)
for d in LIGHTS + [scene.world.node_tree]:
    for fc in all_fcurves(d):
        for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'
set_interp(camd, 'CONSTANT')
for nm in ('Cam', 'CamTarget'):
    for fc in all_fcurves(bpy.data.objects[nm]):
        for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'
for fc in all_fcurves(scene):                                          # esposizione: stacchi secchi tra un posto e l'altro
    for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'
try: scene.render.use_motion_blur = True; scene.render.motion_blur_shutter = 0.06
except Exception: pass
os.makedirs(os.path.dirname(os.path.abspath(BLEND)), exist_ok=True)
import json; json.dump([[round(s[0], 3), round(min(s[1], TOTAL), 3)] for s in SHOTS], open(os.path.join(os.path.dirname(os.path.abspath(BLEND)), 'shots.json'), 'w'))
print('CS', CS_TOP, CS_BOT, 'GU', [round(x, 2) for x in GU['head'].matrix_world.translation])
bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(BLEND)); print('SAVED', BLEND, len(bpy.data.objects), 'oggetti')
