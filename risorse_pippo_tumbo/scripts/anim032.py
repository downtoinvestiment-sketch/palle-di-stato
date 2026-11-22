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
# Video 032 - FRANCESCO CI PROVA, 42,0 s. Si unisce alla testa: templates/head.py + scripts/anim032_body.py -> scripts/anim032.py
# Copione n. 36 v2 (COPIONI.md). Scelte dell'autore: T1 (tostapane Kenney rosso), V2 (Vanessa rosa), P2 (frigorifero cromato).
# Posti: salotto di notte (x = 400: hook e finale), il giardino di Pippo di giorno (case di head.py), Marte (x = -700).
# Tempi da audio/words_t032.json. Luce «cinema». Camera a mano leggera sempre, scossa sugli urli.
# ===================================================================================================================
import props024, props025, props026, props027, props021, props032, posti, luci, random
import pippo2 as pippo
A = kitlook.A
BLEND = os.environ.get('BLEND032', '../t032/pippo_t032.blend')
FONT = bpy.data.fonts.load(A.font('luckiest'))
M25 = props025.mats025(); M32 = props032.mats032()
rnd = random.Random(32)

# ======================= tempi (dalla voce) =======================
T_MA, T_INNAM, T_TOST, T_VANESSA, T_SCRIVE, T_CIAO, T_GHOST = 2.94, 4.40, 6.50, 8.34, 10.56, 11.76, 12.92
T_VOCALE, T_DIECI, T_CENTRI, T_ROSA, T_TOSTA, T_LOGICA = 13.96, 15.48, 16.76, 19.08, 20.72, 22.56
T_MARTE, T_DIMENT, T_TUMBO, T_STORIA, T_SHOCK, T_NOTTE = 24.52, 25.90, 27.68, 29.40, 31.60, 32.22
T_GUARDA, T_LIKE, T_CUORE, T_FIGURA, T_MANDA = 33.56, 35.48, 35.98, 37.90, 39.44
T_LANCIO = 24.95
TOTAL = 42.0; NF = int(TOTAL * FPS)

# fasi: SN salotto di notte, G giardino di giorno, M Marte
FASI = [(0.0, 'SN'), (T_MA, 'G'), (T_DIMENT, 'M'), (T_STORIA, 'G'), (T_SHOCK, 'M'), (T_NOTTE, 'SN')]
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
HX, DX = 400.0, -700.0
FS = Vector((HX + 0.2, 1.95, 0.575))             # Francesco seduto sul divano (faccia verso -Y)
TEL_N = FS + Vector((0.2, -0.3, 0.12))          # il telefono di notte, in piedi davanti a lui, schermo verso Francesco
PH = Vector((HX + 1.25, -0.55, 0.0))             # Pippo di notte, in mezzo alla stanza, guarda il divano
PH2 = Vector((HX + 1.35, 0.9, 0.0))              # Pippo di fianco al divano nella figura di merda (di profilo per la camera)
SVE = Vector((HX - 1.55, 1.95, 0.65))            # sveglia sul tavolino
TAB = Vector((-6.9, 0.2, 0.0))                   # tavolino in giardino
FR_G = TAB + Vector((0, 0, 0.72))                # Francesco sul tavolino (faccia verso -X, cioe' verso Vanessa)
VA = Vector((-10.4, 0.4, 0.0))                   # Vanessa nel giardino della vicina (faccia verso +X)
FG = VA + Vector((-0.35, 1.25, 0.0))             # il frigorifero palestrato accanto a Vanessa nella storia
PG = Vector((-6.0, -0.95, 0.0))                  # Pippo in giardino
TBG = Vector((-7.3, -0.9, 0.0))                # Tumbo in giardino
RZ = Vector((-2.5, -4.5, 0.0))                   # il razzo in giardino
MF = Vector((DX, 0.0, 0.0))                      # Francesco su Marte (sulla sabbia)
MP = Vector((DX + 0.85, 0.45, 0.0)); MT = Vector((DX - 0.5, -0.65, 0.0)); MW = Vector((DX - 1.7, 0.7, 0.0))   # Pippo, Tumbo, l'antenna
MRZ = Vector((DX + 4.5, 7.0, 0.0))               # il razzo atterrato su Marte
FR_YAW_G = -PI / 2; VA_YAW = PI / 2
VOC_LUNG = 14.0

# ======================= set =======================
SAL = props025.salotto(envc, M25, A, x0=HX, font=FONT)
SVG = props026.sveglia(envc, FONT); SVG.location = SVE
TAV = props032.tavolino(envc); TAV.location = TAB
mc = collection('Marte')
SABM = A.materiale('Ground054', dimensione=4.0, tinta=(1.45, 0.62, 0.38))
bpy.ops.mesh.primitive_plane_add(size=700, location=(DX, 150, 0)); MSUOLO = bpy.context.object; MSUOLO.data.materials.append(SABM)
for c_ in MSUOLO.users_collection: c_.objects.unlink(MSUOLO)
mc.objects.link(MSUOLO)
DUNE = props027.dune(mc, DX, SABM)
CIELO_M = props032.cielo_marte(mc, DX)
TERRA = props032.terra(mc, (DX - 60, 260, 120), 14)
for k in range(9):   # sassi rossi
    ball_('Sasso', 1.0, (DX + rnd.uniform(-6, 6), rnd.uniform(-2, 9), 0.0), material('M32_sasso', (0.55, 0.22, 0.12), rough=0.9), mc, sc=(rnd.uniform(0.2, 0.6), rnd.uniform(0.2, 0.5), rnd.uniform(0.12, 0.3)))
RAZM = posti.razzo(mc, tuple(MRZ), nome='RazzoMarte')
WIFI = props032.antenna_wifi(mc); WIFI['root'].location = MW
STA = bpy.data.objects.get('Staccionata')

# ======================= personaggi e oggetti =======================
P = pippo.build_pippo(chc); Tb = tumbo.build_tumbo(chc, scale=0.75)
for r in (P['root'], Tb['root']): r.rotation_mode = 'XYZ'
for nm in 'LR': P['shoulder' + nm].rotation_mode = 'QUATERNION'
FR = props032.francesco(chc, M32, 'T1', A=A, font=FONT, nome='Francesco'); FR['root'].rotation_mode = 'XYZ'; FR['corpo'].rotation_mode = 'XYZ'
VAN = props032.vanessa(chc, M32, 'V2', A=A, nome='Vanessa'); VAN['root'].rotation_mode = 'XYZ'; VAN['corpo'].rotation_mode = 'XYZ'; VAN['cestello'].rotation_mode = 'XYZ'
FRG = props032.frigorifero(chc, M32, 'P2', A=A, nome='Frigo'); FRG['root'].rotation_mode = 'XYZ'
for nm in 'LR': FRG['braccio' + nm].rotation_mode = 'XYZ'
CHAT = props032.fumetto_chat(prc, M32, FONT); CHAT['root'].rotation_mode = 'XYZ'
GHO = props032.fantasmino(prc); GHO.rotation_mode = 'XYZ'
VOC = props032.vocale(prc, M32, FONT, lung=VOC_LUNG); VOC['root'].rotation_mode = 'XYZ'
ROSA = props032.rosa(chc, nome='Rosa'); ROSAN = props032.rosa(chc, nera=True, nome='RosaNera')
for o in (ROSA, ROSAN): o.parent = FR['pane']; o.location = (0, 0, -0.2)
TEL = props032.telefono(chc); TEL['root'].rotation_mode = 'XYZ'
RAZ = posti.razzo(prc, tuple(RZ), nome='Razzo')
CUORE = empty('CuoreLike', (0, 0, 0), TEL['root'], chc)
mcu = material('M32_cuore', (1.0, 0.05, 0.15), rough=0.3, emit=(1.0, 0.05, 0.15), emit_strength=3.0)
for sx in (-1, 1): shape('CuoreLobo', 'sphere', (sx * 0.017, -0.012, 0.012), scale=(0.022, 0.006, 0.022), parent=CUORE, mat=mcu, coll=chc)
shape('CuorePunta', 'sphere', (0, -0.012, -0.01), scale=(0.028, 0.006, 0.03), rot=(0, PI / 4, 0), parent=CUORE, mat=mcu, coll=chc)
PHL = bpy.data.lights.new('LuceTelefono', 'POINT'); PHL.energy = 6.0; PHL.color = (0.55, 0.7, 1.0); PHL.shadow_soft_size = 0.05; PHL.use_shadow = False
PHO = bpy.data.objects.new('LuceTelefono', PHL); prc.objects.link(PHO); PHO.location = TEL_N + Vector((0, 0.05, 0.03))
STORIA = props032.cornice_storia(cac, cam, FONT, lens=30.0)

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
NIENTE = [(TOTAL + 1, TOTAL + 2)]
# figli prima dei padri
show_only(CHAT['grigie'], [(T_CIAO - 0.3, T_CIAO + 0.45)]); show_only(CHAT['blu'], [(T_CIAO + 0.45, T_VOCALE)])
show_only(CHAT['root'], [(T_CIAO - 0.3, T_VOCALE)])
show_only(ROSA, [(T_ROSA + 0.9, T_TOSTA)]); show_only(ROSAN, [(T_TOSTA, T_LOGICA)])
show_only(CUORE, [(T_CUORE, TOTAL + 1)])
show_only(STORIA['root'], [(T_STORIA, T_SHOCK)])
show_only(GHO, [(T_GHOST, T_VOCALE)])
show_only(VOC['root'], [(T_VOCALE, T_CENTRI)])
show_only(TEL['root'], iv('SN'))
show_only(RAZ, [(T_MARTE, T_DIMENT)])
show_only(SAL['root'], iv('SN')); show_only(SVG, iv('SN'))
for o in list(mc.objects):
    if o.parent is None: show_only(o, iv('M'))
show_only(FR['root'], [(0.0, TOTAL + 1)])
show_only(VAN['root'], [(T_VANESSA, T_LOGICA), (T_STORIA, T_SHOCK)])
show_only(FRG['root'], [(T_STORIA, T_SHOCK)])
show_only(P['root'], [(0.0, T_MARTE), (T_DIMENT, T_STORIA), (T_NOTTE, TOTAL + 1)])
show_only(Tb['root'], [(T_MA, T_MARTE), (T_DIMENT, T_STORIA)])
if STA: show_only(STA, NIENTE)
show_only(TAV, iv('G'))
for o in list(envc.objects):
    if o.parent is None and o.name not in NEVER: show(o, iv('G'))

# ======================= luce per fase =======================
def chiavi(owner, attr, valori):
    for (t_, v) in valori:
        setattr(owner, attr, v); owner.keyframe_insert(attr, frame=fr(t_))
def per_fase(owner, attr, vals, default=0.0):
    chiavi(owner, attr, [(t0, vals.get(c, default)) for (t0, c) in FASI])
per_fase(SUN.data, 'energy', {'G': 4.6, 'M': 4.2})
per_fase(SUN.data, 'color', {'G': (1, 0.95, 0.85), 'M': (1.0, 0.78, 0.6)}, default=(1, 0.95, 0.85))
per_fase(CIELO.inputs['Strength'], 'default_value', {'SN': 0.02, 'G': 0.42, 'M': 0.25})
if VISTA: per_fase(VISTA.inputs['Strength'], 'default_value', {'G': V0})
per_fase(scene.view_settings, 'exposure', {'SN': -0.6, 'G': 0.2, 'M': 0.1})
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
LSN = luci.cinema(prc, (HX + 0.4, 0.9, 0.9), (HX + 0.5, -2.4, 1.2), distanza=3.0, lato=-1, forza=0.22, nome='CinemaSN', riempimento=0.4, controluce=1.8)
LUNA_S = area('LunaSalotto', (HX - 3.2, -0.4, 2.4), 260.0, 1.6, (0.45, 0.58, 1.0)); LUNA_S.rotation_euler = (0, -1.1, 0)
for l_ in LSN.values():                                                 # di notte: lampada calda debole, il blu della luna domina
    if 'Chiave' in l_.name: l_.data.energy *= 0.35; l_.data.color = (1.0, 0.72, 0.45)
    if 'Controluce' in l_.name: l_.data.color = (0.45, 0.6, 1.0); l_.data.energy *= 1.3
LG = luci.cinema(prc, FR_G + Vector((-1.6, 0, 0.0)), FR_G + Vector((-1.8, -4.0, 0.6)), distanza=4.0, lato=1, forza=0.55, nome='CinemaG')
LM = luci.cinema(prc, MF + Vector((0.3, 0, 0.6)), MF + Vector((0.6, -3.0, 1.0)), distanza=3.5, lato=-1, forza=0.55, nome='CinemaM')
for l_ in LM.values():
    if 'Chiave' in l_.name: l_.data.color = (1.0, 0.75, 0.55)
on_off(list(LSN.values()) + [LUNA_S, PHO], iv('SN')); on_off(list(LG.values()), iv('G')); on_off(list(LM.values()), iv('M'))
LIGHTS = [SUN.data, LUNA_S.data, PHL] + [l_.data for d_ in (LSN, LG, LM) for l_ in d_.values()]
# gli archi del wifi si accendono uno dopo l'altro quando Tumbo lo trova
for k, inp in enumerate(WIFI['archi']):
    keys = [(0.0, 0.0), (T_TUMBO + 0.35 + 0.18 * k - 0.04, 0.0), (T_TUMBO + 0.35 + 0.18 * k, 4.0)]
    for (t_, v) in keys: inp.default_value = v; inp.keyframe_insert('default_value', frame=fr(t_))
LIGHTS.append(None)

# ======================= pose =======================
def qdir(d, rest=(0, 0, -1)): return Vector(rest).rotation_difference(Vector(d).normalized())
def yaw_to(a, b): return math.atan2(b[0] - a[0], -(b[1] - a[1]))
def braccia(nome, forza=1.0):
    b = pippo.EMOZIONI_FORTI[nome]['braccia']; return {'aL': tuple(Vector((0, 0, -1)).lerp(Vector(b[0]).normalized(), forza)), 'aR': tuple(Vector((0, 0, -1)).lerp(Vector(b[1]).normalized(), forza))}
def jit(t, a=0.02, f=37.0): return a * math.sin(t * f) * math.sin(t * f * 0.71 + 1.3)
URLO = dict(aL=(-0.55, -0.45, 0.55), aR=(0.55, -0.45, 0.55))

def pp(t):
    """Pippo: loc, yaw, lean, head, braccia."""
    S_ = dict(loc=Vector((0, 0, -50)), yaw=0.0, lean=0.0, head=(0, 0, 0), aL=(-0.15, 0, -1), aR=(0.15, 0, -1))
    if t < T_MA:                                        # hook: urla verso il divano alle tre di notte
        S_.update(loc=PH + Vector((0, 0, 0.02 * abs(math.sin(t * 11)))), yaw=yaw_to(PH, FS), lean=-0.08, head=(0.12, 0, 0), **URLO)
    elif t < T_MARTE:                                   # in giardino: guarda Francesco, poi la camera nella cosa piu' logica
        if T_VOCALE <= t < T_CENTRI: S_.update(loc=Vector((-7.7, -0.7, 0.0)), yaw=yaw_to((-7.7, -0.7), FR_G))
        elif t >= T_LOGICA: S_.update(loc=PG.copy(), yaw=yaw_to(PG, (PG.x + 0.15, -3.0)), head=(0.05, 0.12, 0), aL=(-0.3, -0.3, -0.9), aR=(0.4, -0.6, 0.3))
        else:
            S_.update(loc=PG.copy(), yaw=yaw_to(PG, FR_G), head=(-0.2, 0, 0))
            if T_GHOST <= t < T_VOCALE: S_.update(**braccia('sorpreso', 0.8))
            elif T_TOSTA <= t: S_.update(**braccia('spaventato', 0.7))
    elif T_DIMENT <= t < T_STORIA:                      # su Marte
        S_.update(loc=MP.copy(), yaw=yaw_to(MP, (MP.x + 0.3, -3.0)) if t < T_TUMBO else yaw_to(MP, MW), **braccia('felice', 0.7))
    elif t >= T_NOTTE:                                  # di notte: arriva e urla nella figura di merda
        if t < T_FIGURA: S_.update(loc=PH + Vector((0.6, -0.4, 0)), yaw=yaw_to(PH, FS), aL=(-0.2, -0.2, -0.95), aR=(0.2, -0.2, -0.95))
        elif t < T_MANDA: S_.update(loc=PH2 + Vector((0, 0, 0.02 * abs(math.sin(t * 11)))), yaw=yaw_to(PH2, FS), lean=-0.08, head=(0.12, 0, 0), **URLO)
        else: S_.update(loc=PH.copy(), yaw=yaw_to(PH, FS), head=(0.25, 0, 0), aR=(0.05, -0.85, 0.75), aL=(-0.2, 0, -1))   # mano sulla faccia
    return S_

def tp(t):
    """Tumbo: loc, yaw, head."""
    S_ = dict(loc=Vector((0, 0, -50)), yaw=0.0, head=(0, 0, 0), tail=(-0.5, 0, 0.6 * math.sin(t * 14)))
    if T_VOCALE <= t < T_CENTRI: S_.update(loc=Vector((-5.6, -2.0, 0.0)), yaw=yaw_to((-5.6, -2.0), FR_G))
    elif T_MA <= t < T_MARTE: S_.update(loc=TBG.copy(), yaw=yaw_to(TBG, FR_G), head=(0.25, 0, 0))
    elif T_DIMENT <= t < T_STORIA:
        if t < T_TUMBO: S_.update(loc=MT.copy(), yaw=yaw_to(MT, (MT.x, -3.0)))
        else:
            u = sm(ramp(t, T_TUMBO, T_TUMBO + 0.5)); dst = MW + Vector((0.45, -0.35, 0)); p = MT.lerp(dst, u)
            S_.update(loc=p + Vector((0, 0, 0.05 * abs(math.sin(t * 14)) * (1 - u))), yaw=yaw_to(MT, dst) if u < 0.9 else yaw_to(dst, (dst.x + 0.3, -3.0)), head=(-0.3 if u >= 0.9 else 0.0, 0, 0),
                     tail=(-0.5, 0, 0.9 * math.sin(t * 22)))
    return S_

def frp(t):
    """Francesco: loc, yaw, scossa, leva (0 su, 1 giu'), pane (quanto spunta)."""
    if t < T_MA or t >= T_NOTTE: loc, yaw = FS.copy(), 0.0
    elif t < T_MARTE: loc, yaw = FR_G.copy(), FR_YAW_G
    elif T_DIMENT <= t < T_STORIA or T_SHOCK <= t < T_NOTTE: loc, yaw = MF.copy(), yaw_to(MF, (MF.x - 0.1, -3.0))
    else: loc, yaw = Vector((0, 0, -60)), 0.0
    sc_ = 0.0
    if T_INNAM <= t < T_TOST: loc = loc + Vector((0, 0, 0.03 * abs(math.sin(t * 9))))          # saltella innamorato
    if T_GHOST <= t < T_VOCALE or T_SHOCK <= t < T_NOTTE: sc_ = 0.012                             # gelato / sconvolto
    if t >= T_CUORE + 0.3: sc_ = 0.02 * (1.0 if t < T_MANDA else 0.6)                           # panico
    loc = loc + Vector((sc_ * math.sin(t * 71), sc_ * math.cos(t * 63) * 0.5, 0))
    leva = 0.0
    if T_SCRIVE <= t < T_GHOST: leva = 0.6 + 0.4 * abs(math.sin(t * 12))                          # scrive col pomello
    if T_TOSTA - 0.25 <= t < T_TOSTA + 0.2: leva = 1.0
    pane = 0.0
    if T_ROSA + 0.9 <= t < T_LOGICA: pane = sm(ramp(t, T_ROSA + 0.9, T_ROSA + 1.2)) * (1 - 0.6 * ramp(t, T_TOSTA - 0.25, T_TOSTA - 0.05)) + 0.6 * ramp(t, T_TOSTA, T_TOSTA + 0.12)
    return dict(loc=loc, yaw=yaw, leva=leva, pane=pane)

# ======================= chiavi =======================
def K(o, f, loc=None, rot=None, scale=None):
    if loc is not None: o.location = loc; o.keyframe_insert('location', frame=f)
    if rot is not None: o.rotation_euler = rot; o.keyframe_insert('rotation_euler', frame=f)
    if scale is not None: o.scale = scale if isinstance(scale, (tuple, list)) else (scale,) * 3; o.keyframe_insert('scale', frame=f)
LV0 = FR['leva'].location.copy(); PN0 = FR['pane'].location.copy()
VOC_DIR = 0.0       # il vocale parte da Francesco e attraversa il giardino verso est (+X), sopra le teste
VOC0 = FR_G + Vector((0.25, 0.0, 1.15))
for f in range(1, NF + 1):
    t = (f - 1) / FPS
    s = pp(t)
    K(P['root'], f, tuple(s['loc']), (s['lean'], 0, s['yaw'])); K(P['head'], f, rot=s['head'])
    for nm, k_ in (('L', 'aL'), ('R', 'aR')):
        sh = P['shoulder' + nm]; sh.rotation_quaternion = qdir(s[k_]); sh.keyframe_insert('rotation_quaternion', frame=f)
    s = tp(t)
    K(Tb['root'], f, tuple(s['loc']), (0, 0, s['yaw']), 0.75); K(Tb['head'], f, rot=s['head']); K(Tb['tail'], f, rot=s['tail'])
    q = frp(t)
    K(FR['root'], f, tuple(q['loc']), (0, 0, q['yaw']))
    for nm in 'LR':
        p_ = FR['pupil' + nm]; lk = (0.0, 0.0)
        if T_INNAM <= t < T_GHOST and t >= T_VANESSA: lk = (0.0, 0.3)
        if T_NOTTE <= t < T_FIGURA: lk = (0.0, -0.3)
        K(p_, f, loc=(lk[0] * 0.02, 0, lk[1] * 0.02))
        e_ = FR['eye' + nm]
        big = 1.35 if (T_GHOST <= t < T_VOCALE or T_SHOCK <= t < T_NOTTE or t >= T_CUORE + 0.2) else 1.0
        K(e_, f, scale=(big, big, big))
    om = 0.015 + (0.035 if (T_GHOST <= t < T_VOCALE or T_SHOCK <= t < T_NOTTE or t >= T_CUORE + 0.2) else 0.0)
    K(FR['mouth'], f, scale=(0.035, 0.01, om))
    # Vanessa: si gira dall'altra parte nel ghostato, centrifuga dalla vergogna
    yv = VA_YAW + PI * sm(ramp(t, T_GHOST, T_GHOST + 0.35)) * (1 - sm(ramp(t, T_CENTRI - 0.3, T_CENTRI)))
    vloc = VA.copy()
    if T_CENTRI <= t < T_ROSA: vloc = vloc + Vector((0.03 * math.sin(t * 57), 0.03 * math.cos(t * 49), 0.02 * abs(math.sin(t * 40))))
    if T_STORIA <= t < T_SHOCK: yv = VA_YAW - 0.35
    K(VAN['root'], f, tuple(vloc), (0, 0, yv))
    spin = 0.0
    if T_CENTRI <= t < T_ROSA: spin = (t - T_CENTRI) * 25.0
    K(VAN['cestello'], f, rot=(0, spin, 0))
    for nm in 'LR':
        g_ = 1.0 + (1.8 if T_CENTRI <= t < T_ROSA else (0.8 if T_STORIA <= t < T_SHOCK else 0.0))
        K(VAN['pupil' + nm], f, loc=(0, 0, -0.025 if T_CENTRI <= t < T_ROSA else 0.0))
    # frigorifero palestrato: fa i bicipiti
    fl = sm(0.5 + 0.5 * math.sin(t * 6.0))
    K(FRG['root'], f, tuple(FG), (0, 0, VA_YAW - 0.35))
    K(FRG['braccioL'], f, rot=(0, -0.25 * fl, 0)); K(FRG['braccioR'], f, rot=(0, 0.25 * fl, 0))
    # la nuvoletta del messaggio sopra Francesco (verso la camera, a sud)
    pop = sm(ramp(t, T_CIAO - 0.3, T_CIAO - 0.05))
    K(CHAT['root'], f, tuple(FR_G + Vector((0.05, -0.2, 0.62))), (0, 0, -0.25), (max(0.01, pop),) * 3)
    # il fantasmino del ghostato: esce da Vanessa e vola verso la camera
    u = (t - T_GHOST) / (T_VOCALE - T_GHOST)
    gp = VA + Vector((0.2, 0, 0.9)) + Vector((1.6 * u, -0.9 * u, 0.35 * u + 0.06 * math.sin(t * 12)))
    K(GHO, f, tuple(gp), (0, 0.15 * math.sin(t * 9), VA_YAW - 0.6), (max(0.01, sm(min(1, u * 4))) * 1.1,) * 3)
    # il vocale: si allunga da Francesco verso la strada
    lv = max(0.01, sm(ramp(t, T_VOCALE + 0.3, T_CENTRI - 0.25)))
    K(VOC['root'], f, tuple(VOC0), (0, 0, VOC_DIR))
    K(VOC['scala'], f, scale=(lv, 1, 1))
    # la leva e il pane (la rosa)
    K(FR['leva'], f, loc=(LV0.x, LV0.y, LV0.z - 0.12 * q['leva']))
    K(FR['pane'], f, loc=(PN0.x, PN0.y, PN0.z + 0.32 * q['pane']))
    # il razzo parte dal giardino
    if T_MARTE <= t < T_DIMENT + 0.05:
        ur = max(0.0, t - T_LANCIO); K(RAZ, f, tuple(RZ + Vector((0.02 * math.sin(t * 60) if t < T_LANCIO else 0, 0, 22.0 * ur * ur))))
    # il telefono di notte: le foto scorrono, poi il like
    K(TEL['root'], f, tuple(TEL_N), (-0.25, 0, PI + 0.45), 0.75)
    sc_ = 0.0
    if T_GUARDA <= t < T_CUORE: sc_ = 0.085 * ((t - T_GUARDA) * 1.6 % 1.0) if t < T_LIKE else 0.0
    K(TEL['foto'], f, loc=(0, -0.009, sc_))
    cs = sm(ramp(t, T_CUORE, T_CUORE + 0.15)) * (1.0 + 0.25 * math.sin(max(0, t - T_CUORE) * 18) * math.exp(-max(0, t - T_CUORE) * 3))
    K(CUORE, f, loc=(0, -0.012, 0.0), scale=(max(0.01, cs * 1.0),) * 3)

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
emo(0.0, 'arrabbiato', 1.0); emo(T_MA, 'felice', 0.8); emo(T_GHOST, 'sorpreso', 1.0); emo(T_VOCALE, 'normale', 1.0, eye_open=0.6)
emo(T_TOSTA, 'spaventato', 0.8); emo(T_LOGICA, 'furbo', 1.0); emo(T_DIMENT, 'felice', 1.0); emo(T_NOTTE, 'normale', 1.0, eye_open=0.45)
emo(T_FIGURA, 'arrabbiato', 1.0); emo(T_MANDA, 'triste', 0.8)
tex(0.0, tongue=0.6, brow=0.2); tex(T_GHOST, tongue=0.0, brow=-0.4, eye_scale=1.25); tex(T_VOCALE, tongue=0.6, brow=0.2); tex(T_TUMBO, tongue=0.9, brow=0.5, eye_scale=1.15)

# ======================= effetti =======================
FXC = prc
def fx(name, pos, w, t0, dur, **k): return A.effetto(name, posizione=tuple(pos), larghezza=w, animazione=(fr(t0), int(dur * FPS)), collezione=FXC, **k)
fx('emoticon/hearts', FR_G + Vector((0.0, 0.0, 0.5)), 0.35, T_INNAM + 0.2, 2.0)
fx('emoticon/hearts', VA + Vector((0.0, 0.0, 1.15)), 0.4, T_VANESSA + 0.3, 1.6)
fx('emoticon/dots3', FR_G + Vector((0.0, 0.0, 0.5)), 0.3, T_SCRIVE + 0.2, 1.0)
fx('emoticon/drops', VA + Vector((0.1, 0.0, 1.0)), 0.35, T_CENTRI + 0.3, 1.8)
for k in range(5): fx('fumo_nero/blacksmoke%02d' % (k + 3), FR_G + Vector((0, 0, 0.4 + 0.08 * k)), 0.35, T_TOSTA + 0.05 + 0.12 * k, 0.9)
for k in range(10): fx('sbuffo_bianco/whitepuff%02d' % (k % 8 + 1), RZ + Vector((rnd.uniform(-1.5, 1.5), rnd.uniform(-1.0, 1.0), 0.3)), 2.6, T_LANCIO + 0.05 * k, 0.8)
fx('emoticon/hearts', VA + Vector((-0.2, 0.6, 1.2)), 0.5, T_STORIA + 0.4, 1.6)
fx('emoticon/heartbroken', MF + Vector((0.0, 0.0, 0.55)), 0.35, T_SHOCK + 0.05, 0.6)
fx('emoticon/exclamations', FS + Vector((0.0, 0.0, 0.55)), 0.3, T_CUORE + 0.35, 1.2)
for k in range(6): fx('fumo_nero/blacksmoke%02d' % (k + 1), FS + Vector((rnd.uniform(-0.08, 0.08), 0, 0.33 + 0.05 * k)), 0.32, T_FIGURA + 0.2 * k, 1.0)
for k in range(6): fx('fumo_nero/blacksmoke%02d' % (k + 2), FS + Vector((rnd.uniform(-0.08, 0.08), 0, 0.33 + 0.05 * k)), 0.32, T_MANDA + 0.25 * k, 1.0)

# ======================= camera =======================
def segui(t, kind):
    if kind == 'rz': return RZ + Vector((0, 0, 3.5 + 22.0 * max(0.0, t - T_LANCIO) ** 2 * 0.85))
    return None
F = FR_G; V = VA; L = TEL_N
FZ = 0.17   # altezza della faccia di Francesco sopra la base
SHOTS = [  # t0, t1, camera da, a, mira da, a, lente, diaframma, mano, segui
    (0.0, T_MA, (PH.x - 0.85, PH.y + 2.0, 1.3), (PH.x - 0.7, PH.y + 1.65, 1.32), (PH.x, PH.y, 1.3), (PH.x, PH.y, 1.35), 30, 3.0, 1.6, None),                     # 01 l'urlo
    (T_MA, T_TOST, (F.x - 1.3, F.y - 0.95, F.z + 0.4), (F.x - 1.15, F.y - 0.85, F.z + 0.38), (F.x, F.y, F.z + 0.22), (F.x, F.y, F.z + 0.22), 32, 5.0, 0.8, None),  # 02 stamattina: si e' innamorato
    (T_TOST, T_VANESSA, (F.x - 0.62, F.y - 0.12, F.z + 0.2), (F.x - 0.52, F.y - 0.1, F.z + 0.2), (F.x, F.y, F.z + FZ), (F.x, F.y, F.z + FZ), 40, 3.0, 0.6, None),  # 03 e' un tostapane
    (T_VANESSA, T_SCRIVE, (F.x + 0.35, F.y - 0.55, F.z + 0.35), (F.x + 0.2, F.y - 0.45, F.z + 0.3), (V.x, V.y, 0.65), (V.x, V.y, 0.62), 40, 6.0, 0.7, None),   # 04 Vanessa (dalle spalle di Francesco)
    (T_SCRIVE, T_GHOST, (F.x - 0.5, F.y - 1.9, F.z + 0.55), (F.x - 0.45, F.y - 1.6, F.z + 0.5), (F.x - 0.05, F.y, F.z + 0.42), (F.x - 0.05, F.y, F.z + 0.45), 35, 4.0, 0.7, None),  # 05 ciao bella
    (T_GHOST, T_VOCALE, (V.x + 2.3, V.y - 1.6, 1.1), (V.x + 2.0, V.y - 1.4, 1.15), (V.x + 0.5, V.y - 0.2, 0.9), (V.x + 0.7, V.y - 0.3, 1.05), 28, 6.0, 1.4, None),  # 06 ghostato
    (T_VOCALE, T_CENTRI, (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), 26, 64, 0.6, 'voc'),          # 07 il vocale di dieci minuti
    (T_CENTRI, T_ROSA, (V.x + 1.35, V.y - 0.35, 0.75), (V.x + 1.2, V.y - 0.3, 0.72), (V.x, V.y, 0.5), (V.x, V.y, 0.5), 35, 4.0, 1.5, None),                 # 08 centrifuga dalla vergogna
    (T_ROSA, T_TOSTA, (F.x - 0.85, F.y - 0.45, F.z + 0.3), (F.x - 0.75, F.y - 0.4, F.z + 0.3), (F.x, F.y, F.z + 0.3), (F.x, F.y, F.z + 0.32), 38, 3.0, 0.6, None),   # 09 la rosa
    (T_TOSTA, T_LOGICA, (F.x - 0.95, F.y + 0.45, F.z + 0.3), (F.x - 0.85, F.y + 0.4, F.z + 0.3), (F.x, F.y, F.z + 0.25), (F.x, F.y, F.z + 0.27), 38, 3.0, 1.3, None),   # 10 la tosta
    (T_LOGICA, T_MARTE, (PG.x + 0.18, PG.y - 1.9, 1.5), (PG.x + 0.16, PG.y - 1.7, 1.5), (PG.x, PG.y, 1.45), (PG.x, PG.y, 1.45), 40, 3.0, 0.7, None),         # 11 la cosa piu' logica
    (T_MARTE, T_DIMENT, (RZ.x + 4.0, RZ.y - 10.0, 1.2), (RZ.x + 3.8, RZ.y - 9.5, 1.3), (RZ.x, RZ.y, 4.0), (RZ.x, RZ.y, 8.0), 22, 22, 1.2, 'rz'),            # 12 lo porta su Marte
    (T_DIMENT, T_TUMBO, (DX + 0.5, -4.4, 1.0), (DX + 0.4, -4.0, 1.05), (DX + 0.2, 0.5, 0.75), (DX + 0.2, 0.5, 0.8), 28, 8.0, 0.7, None),                 # 13 Marte
    (T_TUMBO, T_STORIA, (MW.x + 1.6, MW.y - 2.3, 0.9), (MW.x + 1.5, MW.y - 2.1, 0.95), (MW.x + 0.2, MW.y - 0.2, 1.1), (MW.x + 0.15, MW.y - 0.2, 1.3), 28, 5.0, 0.8, None),  # 14 Tumbo trova il wifi
    (T_STORIA, T_SHOCK, (V.x + 3.3, V.y + 0.55, 1.2), (V.x + 3.0, V.y + 0.55, 1.2), (V.x, V.y + 0.6, 0.85), (V.x, V.y + 0.6, 0.85), 30, 64.0, 0.6, None),    # 15 la storia col frigorifero
    (T_SHOCK, T_NOTTE, (MF.x + 0.1, MF.y - 0.75, 0.22), (MF.x + 0.08, MF.y - 0.62, 0.22), (MF.x, MF.y, FZ), (MF.x, MF.y, FZ), 38, 3.0, 1.6, None),            # 16 Francesco sconvolto
    (T_NOTTE, T_GUARDA, (SVE.x + 0.12, SVE.y - 0.75, 0.82), (SVE.x + 0.1, SVE.y - 0.6, 0.8), (SVE.x, SVE.y, 0.72), (SVE.x, SVE.y, 0.72), 45, 2.8, 0.4, None),    # 17 le tre di notte
    (T_GUARDA, T_LIKE, (FS.x - 0.25, FS.y - 1.1, FS.z + 0.3), (FS.x - 0.22, FS.y - 0.95, FS.z + 0.28), (FS.x, FS.y, FS.z + FZ), (FS.x, FS.y, FS.z + FZ), 40, 2.8, 0.5, None),  # 18 guarda le foto
    (T_LIKE, T_CUORE + 0.9, (L.x + 0.17, L.y + 0.3, L.z + 0.2), (L.x + 0.15, L.y + 0.26, L.z + 0.17), (L.x, L.y, L.z), (L.x, L.y, L.z), 40, 2.8, 0.4, None),   # 19 il like (lo schermo)
    (T_CUORE + 0.9, T_FIGURA, (FS.x - 0.3, FS.y - 0.85, FS.z + 0.22), (FS.x - 0.27, FS.y - 0.75, FS.z + 0.2), (FS.x, FS.y, FS.z + FZ), (FS.x, FS.y, FS.z + FZ), 40, 2.8, 1.4, None),   # 20 panico
    (T_FIGURA, T_MANDA, (HX + 0.3, -2.4, 1.2), (HX + 0.33, -2.2, 1.2), (HX + 1.0, 1.0, 0.95), (HX + 1.0, 1.0, 0.95), 26, 6.0, 1.4, None),                   # 21 che figura di merda
    (T_MANDA, TOTAL + 0.1, (FS.x - 0.3, FS.y - 0.95, FS.z + 0.2), (FS.x - 0.26, FS.y - 0.75, FS.z + 0.2), (FS.x, FS.y, FS.z + FZ), (FS.x, FS.y, FS.z + FZ), 40, 2.8, 0.6, None),  # 22 mandalo a un Francesco
]
SHAKES = [(0.0, 0.02, 1.0), (T_TOST, 0.01, 0.4), (T_GHOST, 0.02, 0.5), (T_DIECI, 0.015, 0.5), (T_TOSTA, 0.025, 0.6), (T_LANCIO, 0.03, 0.9), (T_SHOCK, 0.02, 0.5), (T_CUORE, 0.02, 0.6), (T_FIGURA, 0.025, 0.9)]
def hn(t, s): return 0.6 * math.sin(t * 1.7 + s) + 0.3 * math.sin(t * 3.3 + 2.1 * s) + 0.12 * math.sin(t * 7.9 + 3.7 * s)
for f in range(1, NF + 1):
    t = (f - 1) / FPS
    s_ = next((s for s in SHOTS if s[0] <= t < s[1]), SHOTS[-1]); u = sm((t - s_[0]) / (s_[1] - s_[0]))
    cl = Vector(lerp(s_[2], s_[3], u)); tl = Vector(lerp(s_[4], s_[5], u))
    if s_[9] == 'voc':
        lv_ = max(0.01, sm(ramp(t, T_VOCALE + 0.3, T_CENTRI - 0.25))); tip = VOC0.x + lv_ * VOC_LUNG
        tl = Vector((max(VOC0.x + 0.6, tip - 0.8), VOC0.y, VOC0.z - 0.15)); cl = tl + Vector((0.35, -2.9, 0.1))
    elif s_[9]: tl = segui(t, s_[9])
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
for d in [l_ for l_ in LIGHTS if l_ is not None] + [scene.world.node_tree]:
    for fc in all_fcurves(d):
        for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'
for mt in bpy.data.materials:
    if mt.name.startswith('M32_arco') and mt.node_tree:
        for fc in all_fcurves(mt.node_tree):
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
