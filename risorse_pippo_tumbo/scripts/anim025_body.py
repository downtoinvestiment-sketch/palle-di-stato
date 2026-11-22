# ===================================================================================================================
# Video 025 - MARTINA NEL WATER, 37,4 s. Si unisce alla testa: templates/head.py + scripts/anim025_body.py -> scripts/anim025.py
# Copione n. 22 versione 4 (COPIONI.md). Scelte dell'autore (19 novembre 2026): B1 Martina cartoon, W2 bagno della nonna,
# C2 ciabatta da piscina; elefante E1 grigio (props022). Voce tutta eccitata: stacchi ogni 1-2 s, camera che trema sugli urli.
# Posti: il bagno (x = 300), il salotto (x = 400), il quartiere allagato (case di head.py). Tempi da audio/words_t025.json.
# Indizi nell'hook: il flacone di CRESCITUTTO nel water (Martina gigante), Tumbo che mastica la ciabatta (lo SCIAF),
# il manuale del TANGO sulla mensola (l'elefante). Luce «cinema» (luci.py) in ogni posto.
# ===================================================================================================================
import props025, props022, props021, props024, luci, random
import pippo2 as pippo
A = kitlook.A
BLEND = os.environ.get('BLEND025', '../t025/pippo_t025.blend')
FONT = bpy.data.fonts.load(A.font('luckiest'))
M25 = props025.mats025(); M22 = props022.mats022()
M22['eleG'].node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.27, 0.28, 0.32, 1)
rnd = random.Random(25)

# ======================= tempi (dalla voce) =======================
T_BAGNO = 2.86; T_MART = 3.16; T_SCARA = 4.58          # «trova Martina nel water!» «Martina e' uno scarafaggio!»
T_TIRA = 6.38; T_VORT = 7.0; T_RISALE = 7.76           # «Pippo tira lo sciacquone! Martina risale!»
T_VALIGIA = 8.82; T_TRASF = 9.76; T_STRONZA = 11.08    # «Con la valigia! Si trasferisce da lui, quella stronza!»
T_LOGICA = 12.28                                       # «Allora Pippo fa la cosa piu' logica!»
T_COMPRA = 14.14; T_ELE = 14.56; T_TANGO = 15.04       # «Compra un elefante! E gli insegna il tango!»
T_CASQUE = 16.94; T_BESTIONE = 17.96                   # «Al primo casque', quel bestione del cazzo
T_CADE = 18.38; T_SEDUTO = 18.95                       #  cade sul water!»
T_ESPLODE = 19.94; T_FUORI = 20.8                      # «Esplode tutto, porca puttana!»
T_ALLAGA = 22.12; T_ESCE = 23.66; T_SU = 24.12; T_40 = 25.36   # «Il quartiere si allaga... e dall'acqua esce Martina, alta 40 metri!»
T_TUMBO = 26.14; T_CIAB = 27.46; T_SALTO = 28.56; T_SCIAF = 29.3   # «Ma Tumbo arriva con una ciabatta grande come un palazzo! SCIAF!»
T_TAPPETO = 30.22; T_BALLA = 31.94; T_TEAM = 34.68     # «Ora Martina fa da tappeto in salotto. E Pippo ci balla sopra...» «Team...»
TOTAL = 37.4; NF = int(TOTAL * FPS)

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
props021.bagliore(scene, forza=0.25, soglia=1.6)

# ======================= posti =======================
BX = 300.0; SX = 400.0
WC = Vector((BX, 1.25, 0.0)); QW = 0.43                  # il water e la quota dell'acqua nella tazza
SEAT = Vector((BX, WC.y - 0.27, 0.6))                    # bordo davanti della tavoletta (Martina ci atterra)
GEY = Vector((-1.2, 9.5, 5.2))                           # dove il getto sfonda il tetto di Pippo
CAMINO = Vector((1.755, 10.4, 6.07))                     # cima del camino (Tumbo l'eroe)
TETTO_P = Vector((-1.7, 9.45, 5.86)); TETTO_E = Vector((0.5, 9.5, 5.9 - 0.85))   # Pippo e l'elefante (radice: l'anca sta 0,85 piu' su) sul colmo
MG_X, MG_Y = 0.0, 24.0                                   # Martina gigante esce dietro la casa di Pippo
DIVANO = Vector((SX + 0.0, 2.0, 0.575))                  # dove Martina si sdraia sul divano (la seduta e' a 0,575)
TAP = Vector((SX + 0.3, -0.35, 0.0))                     # Martina-tappeto
LAND = Vector((SX + 0.5, 0.05, 0.0))                     # dove atterra l'elefante

# ======================= set =======================
BG = props025.bagno(envc, M25, A, 'W2', x0=BX, font=FONT, nome='Bagno', chiuso=True)
W = BG['water']
SAL = props025.salotto(envc, M25, A, x0=SX, font=FONT)
ALL, ALLN = props025.allagamento(prc)
VORT = props025.vortice(prc, R=0.198); VORT.scale = (1.0, 1.25, 1.0); VORT.location = (BX, WC.y, QW + 0.003)
G_IN = props025.geyser(prc, R=0.32, nome='GetBagno'); G_IN['root'].location = (BX, WC.y, QW)
G_OUT = props025.geyser(prc, R=1.5, nome='GetTetto'); G_OUT['root'].location = GEY
M_BUCO = material('P25_buco', (0.02, 0.015, 0.012), rough=1.0)
BUCO = ball_('BucoTetto', 1.0, (GEY.x, GEY.y - 0.35, 5.62), M_BUCO, prc, sc=(1.9, 1.4, 0.25)); BUCO.rotation_euler = (0.5, 0, 0)
AUTO = []                                                # auto che galleggiano
for k, (aid, p_, rz) in enumerate((('sedan', (-6.5, -11.4), 12), ('suv', (8.0, -10.0), -25), ('taxi', (-14.0, -12.0), 70), ('hatchback-sports', (15.0, -11.8), 160), ('van', (4.5, -15.5), 95))):
    try: AUTO.append((A.modello('kenney/car-kit/' + aid, posizione=(p_[0], p_[1], 0.02), altezza=2.6 if aid == 'van' else 2.1, rotazione=rz, collezione=prc, appoggia=True), Vector((p_[0], p_[1], 0.02)), rz, k))
    except Exception as e: print('auto', e)

# ======================= personaggi =======================
P = pippo.build_pippo(chc); Tb = tumbo.build_tumbo(chc, scale=0.75)
for r in (P['root'], Tb['root']): r.rotation_mode = 'XYZ'
for nm in 'LR': P['shoulder' + nm].rotation_mode = 'QUATERNION'
LM = 0.16
MT = props025.scarafaggio(chc, M25, 'B1', L=LM, nome='Martina'); MT['root'].rotation_mode = 'XYZ'
props025.occhiali(chc, M25, MT['testa'], (0, -0.15 * LM * 0.85 - 0.006, 0.06 * LM), 0.26, nome='OcchialiM')
RING = props025.ciambella(chc, M25, 0.075, FONT, 'MARTINA', nome='Ciambella'); RING.rotation_mode = 'XYZ'
DRINK = props025.bicchiere(chc, M25, h=0.045, nome='Drink'); DRINK.parent = MT['zampe'][1]; DRINK.location = (0.058 * LM / 0.16, -0.035, -0.045); DRINK.rotation_euler = (PI, 0, 0)
BOTT = props025.bottiglia(chc, M25, FONT, H=0.14); BOTT.rotation_mode = 'XYZ'
def una_valigia(R):
    """il modello ha due valigie: tiene la prima e la rimette al centro della radice."""
    for c in list(R.children_recursive):
        if '_02_' in c.name: bpy.data.objects.remove(c, do_unlink=True)
    bpy.context.view_layer.update()
    pts = [c.matrix_world @ Vector(v) for c in R.children_recursive if c.type == 'MESH' for v in c.bound_box]
    cx = sum(p.x for p in pts) / len(pts); cy = sum(p.y for p in pts) / len(pts); d = R.matrix_world.inverted() @ Vector((cx, cy, R.location.z)) - R.matrix_world.inverted() @ R.location
    for c in R.children: c.location -= Vector((d.x, d.y, 0))
VAL = A.modello('vintage_suitcase', posizione=(0, 0, 0), altezza=0.11, collezione=chc, appoggia=True); VAL.rotation_mode = 'XYZ'; una_valigia(VAL)
LG = 30.0
MG = props025.scarafaggio(chc, M25, 'B1', L=LG, nome='MartinaG'); MG['root'].rotation_mode = 'XYZ'
props025.occhiali(chc, M25, MG['testa'], (0, -0.15 * LG * 0.85 - 0.006 * LG / 0.16, 0.06 * LG), 0.26 * LG / 0.16, nome='OcchialiG')
VALG = A.modello('vintage_suitcase', posizione=(0, 0, 0), altezza=7.5, collezione=chc, appoggia=True); VALG.rotation_mode = 'XYZ'; una_valigia(VALG); VALG_S = VALG.scale.copy()
E = props022.elefante(chc, M22, 'E1', H=2.7); ES = 2.7 / 3.6
for o in [E['root'], E['body'], E['head']] + E['legs'] + E['ears'] + E['trunk']: o.rotation_mode = 'XYZ'
ROSA_P = props025.rosa(chc, 0.3, nome='RosaPippo'); ROSA_P.parent = P['head']; ROSA_P.location = (0.02, -0.31, 0.11); ROSA_P.rotation_euler = (0, 0, 0.75)
ROSA_E = props025.rosa(chc, 0.3, nome='RosaEle'); ROSA_E.parent = E['trunk'][5]; ROSA_E.location = (0, -0.03, -0.3 * ES); ROSA_E.rotation_euler = (0, PI / 2, 0.3)
TAG = props025.prezzo(chc, M25, FONT, '9,99 €', nome='Prezzo'); TAG.parent = E['ears'][1]; TAG.location = (0.55 * ES, -0.12, -0.35 * ES); TAG.rotation_mode = 'XYZ'; TAG.scale = (1.8, 1.8, 1.8)
CS = props025.ciabatta(chc, M25, 'C2', L=0.36, nome='CiabattaTumbo'); CS.parent = Tb['head']; CS.location = (0.1, -0.36, -0.13); CS.rotation_euler = (0.15, 0.25, PI / 2 - 0.25)
LGS = 24.0
GSP = empty('PernoCiabattaG', (0, 0, -80), None, prc); GSP.rotation_mode = 'XYZ'
GS = props025.ciabatta(prc, M25, 'C2', L=LGS, nome='CiabattaG'); GS.parent = GSP; GS.location = (0, -LGS / 2, 0)

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
IN_B = [(0.0, T_TRASF), (T_CADE, T_FUORI)]               # bagno
IN_S = [(T_TRASF, T_CADE), (T_TAPPETO, TOTAL + 1)]        # salotto
OUT = [(T_FUORI, T_TAPPETO)]                              # quartiere
show_only(W['acqua'], [(0.0, T_VORT - 0.04), (T_RISALE, T_TRASF), (T_CADE, T_ESPLODE)])
show_only(VORT, [(T_VORT - 0.04, T_RISALE)])
show_only(W['root'], [(0.0, T_TRASF), (T_CADE, T_ESPLODE)])
for o_ in SAL['soffitto']: show_only(o_, [(T_TRASF, T_CADE), (T_BALLA, TOTAL + 1)])
show_only(BG['root'], IN_B); show_only(SAL['root'], IN_S)
show_only(G_IN['root'], [(T_ESPLODE, T_FUORI)]); show_only(G_IN['cima'], [(T_ESPLODE, T_FUORI)])
show_only(G_OUT['root'], [(T_FUORI, T_ALLAGA + 0.9)]); show_only(G_OUT['cima'], [(T_FUORI, T_ALLAGA + 0.9)])
show_only(BUCO, OUT); show_only(ALL, OUT)
for a_, _, _, _ in AUTO: show_only(a_, OUT)
show_only(RING, [(0.0, T_VORT + 0.55)]); show_only(BOTT, [(0.0, T_TRASF)])
show_only(DRINK, [(0.0, T_VORT + 0.55), (T_TRASF, T_CADE)])
show_only(VAL, [(T_VALIGIA - 0.05, T_CADE)])
show_only(MT['root'], [(0.0, T_VORT + 0.62), (T_RISALE, T_CADE)])
show_only(MG['root'], [(T_ESCE, TOTAL + 1)]); show_only(VALG, [(T_ESCE, TOTAL + 1)])
show_only(ROSA_P, [(T_TANGO, T_CADE), (T_BALLA, TOTAL + 1)]); show_only(ROSA_E, [(T_TANGO, T_CADE), (T_BALLA, TOTAL + 1)])
show_only(TAG, [(T_COMPRA - 0.05, T_CADE)])
show_only(E['root'], [(T_COMPRA - 0.05, T_TAPPETO), (T_BALLA, TOTAL + 1)])
show_only(P['root'], [(0.0, T_CADE), (T_ALLAGA, T_TAPPETO), (T_BALLA, TOTAL + 1)])
show_only(Tb['root'], [(0.0, T_TIRA), (T_COMPRA, T_CADE), (T_TUMBO, TOTAL + 1)])
show_only(CS, [(0.0, T_TIRA), (T_COMPRA, T_CADE), (T_TAPPETO, TOTAL + 1)])
show_only(GSP, [(T_TUMBO, T_TAPPETO)])
for o in list(envc.objects):
    if o.parent is None and o.name not in NEVER: show(o, OUT)

# ======================= luce: interni e fuori =======================
def chiavi(sock_owner, attr, valori):
    for (t_, v) in valori:
        setattr(sock_owner, attr, v); sock_owner.keyframe_insert(attr, frame=fr(t_))
def per_posto(owner, attr, dentro, fuori):
    """valore 'dentro' nel bagno e nel salotto, 'fuori' nel quartiere (stacchi secchi)."""
    chiavi(owner, attr, [(0.0, dentro), (T_FUORI - 0.04, dentro), (T_FUORI, fuori), (T_TAPPETO - 0.04, fuori), (T_TAPPETO, dentro)])
per_posto(SUN.data, 'energy', 0.0, 4.6)
per_posto(CIELO.inputs['Strength'], 'default_value', 0.02, 0.42)
if VISTA: per_posto(VISTA.inputs['Strength'], 'default_value', 0.0, V0)
per_posto(scene.view_settings, 'exposure', 0.15, 0.25)
def area(nome, pos, energia, size, colore=(1.0, 0.95, 0.86)):
    l_ = bpy.data.lights.new(nome, 'AREA'); l_.energy = energia; l_.size = size; l_.color = colore; l_.use_shadow = False
    o = bpy.data.objects.new(nome, l_); prc.objects.link(o); o.location = pos; return o
PLAF_B = area('PlafBagno', (BX, 0.0, 3.5), 220.0, 1.6)
PLAF_S = area('PlafSalotto', (SX, 0.0, 4.1), 420.0, 3.0)
LB = luci.cinema(prc, (BX, 0.9, 1.1), (BX + 1.6, -1.6, 1.6), distanza=2.6, lato=-1, forza=0.75, nome='CinemaB')
LS = luci.cinema(prc, (SX + 0.2, 0.3, 1.3), (SX + 0.6, -3.6, 1.8), distanza=3.6, lato=-1, forza=0.55, nome='CinemaS')
LT = luci.cinema(prc, (0.0, 9.5, 6.5), (2.0, -6.0, 3.0), distanza=7.0, lato=-1, forza=0.9, nome='CinemaT', riempimento=0.6)
def on_off(lights, intervals):
    for l_ in lights:
        e_ = l_.data.energy; keys = [(0.0, e_ if intervals[0][0] <= 0 else 0.0)]
        for (a, b) in intervals:
            if a > 0: keys += [(a - 0.04, 0.0), (a, e_)]
            if b < TOTAL: keys += [(b - 0.04, e_), (b, 0.0)]
        chiavi(l_.data, 'energy', sorted(keys))
SU_L = bpy.data.lights.new('LuceWater', 'POINT'); SU_L.energy = 18.0; SU_L.color = (1.0, 0.85, 0.6); SU_L.shadow_soft_size = 0.05; SU_L.use_shadow = False
SU = bpy.data.objects.new('LuceWater', SU_L); prc.objects.link(SU); SU.location = (BX, WC.y - 0.05, QW + 0.06)
on_off([SU], [(0.0, T_BAGNO)])
on_off([PLAF_B] + list(LB.values()), IN_B); on_off([PLAF_S] + list(LS.values()), IN_S); on_off(list(LT.values()), [(T_ALLAGA, T_TAPPETO)])
LIGHTS = [SUN.data, PLAF_B.data, PLAF_S.data, SU_L] + [l_.data for l_ in list(LB.values()) + list(LS.values()) + list(LT.values())]

# ======================= pose =======================
def qdir(d, rest=(0, 0, -1)): return Vector(rest).rotation_difference(Vector(d).normalized())
def yaw_to(a, b): return math.atan2(b[0] - a[0], -(b[1] - a[1]))
def mixv(a, b, u): return tuple(Vector(a).lerp(Vector(b), u))
def braccia(nome, forza=1.0):
    b = pippo.EMOZIONI_FORTI[nome]['braccia']; return {'aL': tuple(Vector((0, 0, -1)).lerp(Vector(b[0]).normalized(), forza)), 'aR': tuple(Vector((0, 0, -1)).lerp(Vector(b[1]).normalized(), forza))}
ARMS_DOWN = dict(aL=(-0.14, 0, -1), aR=(0.14, 0, -1))
def jit(t, a=0.02, f=37.0): return a * math.sin(t * f) * math.sin(t * f * 0.71 + 1.3)

def tango_x(t, t0, x0, passo=0.42, beat=0.48, n=99):
    """posizione lungo X della coppia: un passo ogni 'beat' secondi, fermo tra un passo e l'altro (tango a scatti)."""
    k = min(n, max(0.0, (t - t0) / beat)); i = int(k); u = sm(min(1.0, (k - i) / 0.55))
    return x0 + passo * (i + u) if i < n else x0 + passo * n

def snap(t, t0, beat=0.48):
    """la testa scatta a destra e a sinistra a ogni passo (±1)."""
    return 1.0 if int(max(0.0, t - t0) / beat) % 2 == 0 else -1.0

Y0T = 0.0; Y0F = TAP.y                                  # linea del tango in salotto e sopra il tappeto
def tango_heads(t, t0):
    """Pippo e l'elefante girano la testa di scatto: verso di noi (camera a -Y) e poi in avanti."""
    k = snap(t, t0); return (-1.05 if k > 0 else 0.3), (1.0 if k > 0 else -0.3)

def pp(t):
    """Pippo: loc, yaw, lean (radice), bend/twist (busto), head, braccia, sc."""
    S_ = dict(loc=Vector((BX, 0.2, 0)), yaw=PI, lean=0.0, bend=0.0, twist=0.0, head=(0, 0, 0), sc=(1, 1, 1), **ARMS_DOWN)
    if t < T_SCARA:                                                   # chino sul water a guardare dentro
        S_.update(loc=Vector((BX - 0.02, 0.22, 0)), bend=0.86 + 0.03 * math.sin(t * 2.0), head=(0.22, 0, 0), aL=(-0.2, -0.55, -0.8), aR=(0.2, -0.55, -0.8))
        if t >= T_BAGNO: S_.update(aR=mixv((0.2, -0.55, -0.8), (0.05, -0.85, -0.45), ramp(t, T_MART - 0.1, T_MART + 0.2)))   # indica dentro
    elif t < T_TIRA:                                                  # si raddrizza (primo piano di Martina)
        S_.update(loc=Vector((BX - 0.02, 0.2, 0)), bend=0.22, head=(0.55, 0, 0), **braccia('sorpreso', 0.6))
    elif t < T_TRASF:                                                 # tira lo sciacquone, poi guarda Martina che risale
        S_.update(loc=Vector((BX + 0.56, 1.18, 0)), yaw=PI, bend=0.22)
        u = ramp(t, T_TIRA, T_TIRA + 0.25); press = math.sin(PI * ramp(t, T_TIRA + 0.25, T_TIRA + 0.55))
        S_.update(aR=mixv((0.14, 0, -1), (0.36, -0.86, -0.25 - 0.18 * press), u), head=(0.25, 0, -0.2))
        if t >= T_RISALE:
            S_.update(yaw=PI + 0.5, bend=0.1, head=(0.3, 0, 0), **braccia('spaventato', 0.8))
    elif t < T_STRONZA:                                               # entra in salotto (dietro, sfocato)
        u = ramp(t, T_TRASF, T_STRONZA); S_.update(loc=Vector((SX - 1.6, -0.2, 0)).lerp(Vector((SX + 0.35, 0.72, 0)), u), yaw=yaw_to((SX - 1.6, -0.2), (SX + 0.35, 0.72)))
    elif t < T_LOGICA:                                                # furioso davanti al divano
        S_.update(loc=Vector((SX + 0.35, 0.72, 0)) + Vector((jit(t, 0.025), 0, 0)), yaw=PI - 0.15, bend=0.18, head=(0.12, jit(t, 0.05, 23), 0), **braccia('arrabbiato'))
    elif t < T_COMPRA:                                                # si gira verso di noi: la cosa piu' logica
        u = ramp(t, T_LOGICA, T_LOGICA + 0.3)
        S_.update(loc=Vector((SX + 0.35, 0.72, 0)), yaw=(PI - 0.15) * (1 - u), head=(0.05, 0, 0.1), aL=(-0.08, 0, -1), aR=mixv((0.14, 0, -1), (0.35, -0.75, 0.55), u))
    elif t < T_TANGO:                                                 # presenta l'elefante: ta-daa
        u = ramp(t, T_ELE + 0.05, T_ELE + 0.3)
        S_.update(loc=Vector((SX - 1.35, -0.55, 0)), yaw=yaw_to((SX - 1.35, -0.55), (SX + 0.5, -4.0)), head=(-0.1, 0, 0.15 * u), **braccia('felice', 0.3 + 0.7 * u))
    elif t < T_CADE:                                                  # tango: di profilo, guarda l'elefante (verso +X)
        cx = tango_x(min(t, T_CASQUE), T_TANGO, SX - 0.8, n=4); hp, he = tango_heads(t, T_TANGO)
        S_.update(loc=Vector((cx - 0.52, Y0T, 0)), yaw=PI / 2, head=(0.0, 0, hp if t < T_CASQUE else 0.0), aL=(-0.35, -0.35, 0.87), aR=(-0.3, -0.9, 0.15), bend=-0.06)
        if t >= T_CASQUE:                                             # il casque': si piega sopra l'elefante, non lo regge
            b = ramp(t, T_CASQUE, T_CASQUE + 0.45); f_ = ramp(t, T_BESTIONE - 0.2, T_BESTIONE + 0.25)
            S_.update(bend=0.55 * b + 0.25 * f_, head=(0.3 * b, jit(t, 0.08, 31) * b, 0), loc=Vector((cx - 0.52 + 0.5 * f_ + jit(t, 0.02 * b), Y0T, 0)),
                      aL=mixv((-0.35, -0.35, 0.87), (-0.2, -0.95, -0.25), b), aR=mixv((-0.3, -0.9, 0.15), (0.2, -0.95, -0.2), b))
            if t >= T_BESTIONE + 0.1: S_.update(**braccia('spaventato'))
    elif t < T_ALLAGA:
        S_.update(loc=Vector((0, 0, -50)))
    elif t < T_TAPPETO:                                               # sul tetto, terrorizzato
        u = ramp(t, T_40, T_40 + 0.3)
        S_.update(loc=TETTO_P + Vector((jit(t, 0.015), 0, 0)), yaw=0.15 + 2.6 * u, head=(-0.35 * u, 0, 0), **braccia('spaventato'))
        if t >= T_TUMBO: S_.update(yaw=0.15 + 2.6, head=(-0.45, 0, 0))
    elif t < T_BALLA:
        S_.update(loc=Vector((0, 0, -50)))
    else:                                                             # tango sopra Martina-tappeto
        cx = tango_x(min(t, T_TEAM), T_BALLA, SX - 0.3, passo=0.4, n=3); hp, he = tango_heads(t, T_BALLA)
        S_.update(loc=Vector((cx - 0.52, Y0F, 0.0)), yaw=PI / 2, head=(0.0, 0, hp if t < T_TEAM else 0.0), aL=(-0.35, -0.35, 0.87), aR=(-0.3, -0.9, 0.15), bend=-0.06)
        if t >= T_TEAM:                                               # stavolta e' l'elefante a fare il casque' a Pippo
            u = ramp(t, T_TEAM, T_TEAM + 0.5)
            S_.update(lean=-0.62 * u, bend=-0.2 * u, head=(-0.3 * u, 0, -0.9 * u), aL=mixv((-0.35, -0.35, 0.87), (-0.95, -0.1, 0.3), u), aR=mixv((-0.3, -0.9, 0.15), (0.6, -0.4, 0.6), u),
                      loc=Vector((cx - 0.52 + 0.2 * u, Y0F, 0.0)))
    return S_

def ep(t):
    """elefante: loc, yaw, theta (beccheggio del corpo: 0 a quattro zampe, -1.35 in piedi), anca ('piedi', 'seduto' o None),
    hz (altezza dell'anca da seduto), dietro (angolo nel mondo delle zampe dietro), fl/fr (zampe davanti: rotazione x, y),
    testa (beccheggio, girata), prob (curva della proboscide), orecchie (apertura), rot (rollio), sc."""
    S_ = dict(loc=Vector((0, 0, -60)), yaw=0.0, theta=0.0, anca=None, hz=0.85, dietro=0.0, dietro_y=0.0, fl=(0.0, 0.0), fr=(0.0, 0.0), testa=(0.0, 0.0), prob=0.18, orecchie=0.0, rot=(0, 0), sc=(1, 1, 1))
    if T_COMPRA - 0.05 <= t < T_TANGO:                                # cade dal cielo in salotto, barrisce
        z = max(0.0, 7.0 * (1 - ramp(t, T_COMPRA, T_ELE) ** 2)) if t < T_ELE else 0.0
        sq = 1.0 - 0.22 * math.sin(PI * ramp(t, T_ELE, T_ELE + 0.22)) if t >= T_ELE else 1.0
        trumpet = ramp(t, T_ELE + 0.12, T_ELE + 0.35)
        S_.update(loc=LAND + Vector((0, 0, z)), yaw=0.35, sc=(1 / math.sqrt(sq), 1 / math.sqrt(sq), sq), orecchie=0.5 * trumpet + 0.3 * math.sin(t * 9) * trumpet,
                  prob=0.18 - 0.55 * trumpet, testa=(-0.35 * trumpet, 0.0), fl=(0.25 if t < T_ELE else 0.0, 0.0), fr=(0.25 if t < T_ELE else 0.0, 0.0))
    elif T_TANGO <= t < T_CADE:                                       # tango in piedi, di profilo verso -X (Pippo davanti)
        cx = tango_x(min(t, T_CASQUE), T_TANGO, SX - 0.8, n=4); hp, he = tango_heads(t, T_TANGO)
        th = -1.35; dx = 0.0; dz = 0.0
        if t >= T_CASQUE:
            th = -1.35 - 0.85 * ramp(t, T_CASQUE, T_CASQUE + 0.45) - 0.35 * ramp(t, T_CASQUE + 0.6, T_BESTIONE) - 1.0 * ramp(t, T_BESTIONE, T_BESTIONE + 0.3)
            u = ramp(t, T_BESTIONE + 0.05, T_CADE); dx = 2.4 * u * u; dz = -0.7 * u
        S_.update(loc=Vector((cx + 0.55 + dx, Y0T, dz)), yaw=-PI / 2, theta=th, anca='piedi', dietro=0.0, fl=(0.42, -0.15), fr=(-1.0, -0.2), testa=(1.3, he if t < T_CASQUE else 0.0),
                  prob=-0.25, orecchie=0.25)
    elif T_CADE <= t < T_ESPLODE:                                     # in bagno: piomba dall'alto e si siede sul water
        z = 4.2 * (1 - ramp(t, T_CADE, T_SEDUTO) ** 2) if t < T_SEDUTO else 0.0
        sq = 1.0 - 0.18 * math.sin(PI * ramp(t, T_SEDUTO, T_SEDUTO + 0.2)) if t >= T_SEDUTO else 1.0
        up_ = (1 - ramp(t, T_SEDUTO, T_SEDUTO + 0.25)) if t >= T_SEDUTO - 0.4 else 1.0
        S_.update(loc=Vector((BX, WC.y - 0.3, z)), yaw=0.0, theta=-1.15, anca='seduto', hz=0.8, dietro=-0.3, dietro_y=0.3, fl=(-0.9 * up_ + 0.25 * (1 - up_), 0.3), fr=(-0.9 * up_ + 0.25 * (1 - up_), -0.3),
                  testa=(1.05, 0.0), prob=-0.6 * up_ + 0.1 * (1 - up_), orecchie=0.6 + 0.4 * (1 - up_), sc=(1 / math.sqrt(sq), 1 / math.sqrt(sq), sq))   # sulla tavoletta, zampe giu' ai lati della tazza
    elif T_ESPLODE <= t < T_FUORI:                                    # il getto lo spara su, attraverso il soffitto
        u = ramp(t, T_ESPLODE + 0.05, T_ESPLODE + 0.5)
        S_.update(loc=Vector((BX, WC.y - 0.45, 5.5 * u * u + 0.8 * u)), yaw=0.6 * u, theta=-1.25 - 0.6 * u, anca='seduto', dietro=-1.35, fl=(-1.3, 0.5), fr=(-1.3, -0.5), testa=(1.05, 0.0), prob=-0.9, orecchie=1.0)
    elif T_FUORI <= t < T_ALLAGA + 0.55:                              # in cima al getto, che gira
        top = gey_top(t)
        S_.update(loc=Vector((GEY.x, GEY.y, top + 0.9)), yaw=t * 3.5, theta=-1.25 + 0.4 * math.sin(t * 5), anca='seduto', dietro=-1.35 + 0.5 * math.sin(t * 13), fl=(-1.3 + 0.5 * math.sin(t * 11), 0.4), fr=(-1.3 + 0.5 * math.cos(t * 12), -0.4),
                  testa=(1.05, 0.0), prob=-0.9 + 0.3 * math.sin(t * 7), orecchie=1.0)
    elif T_ALLAGA + 0.55 <= t < T_TAPPETO:                            # seduto sul colmo del tetto accanto a Pippo
        u = ramp(t, T_ALLAGA + 0.55, T_ALLAGA + 0.95); a = Vector((GEY.x, GEY.y, gey_top(T_ALLAGA + 0.55) + 0.9)); p = a.lerp(TETTO_E, u); p.z += 2.5 * math.sin(PI * u)
        look = ramp(t, T_40 + 0.05, T_40 + 0.35)
        S_.update(loc=p + Vector((jit(t, 0.012), 0, 0)), yaw=(1 - u) * 6.0 + 2.7 * look, theta=-1.25, anca='seduto', dietro=-1.35, fl=(-0.9, 0.3), fr=(-0.9, -0.3), testa=(1.05 - 0.4 * look, 0.0), prob=-0.6, orecchie=0.8)
    elif t >= T_BALLA:                                                # tango sopra il tappeto; poi il casque' a Pippo
        cx = tango_x(min(t, T_TEAM), T_BALLA, SX - 0.3, passo=0.4, n=3); hp, he = tango_heads(t, T_BALLA)
        th = -1.35; fl = 0.42; tz = he
        if t >= T_TEAM: u = ramp(t, T_TEAM, T_TEAM + 0.5); th = -1.35 + 0.42 * u; fl = 0.42 + 0.35 * u; tz = 0.5 * u
        S_.update(loc=Vector((cx + 0.55, Y0F, 0.0)), yaw=-PI / 2, theta=th, anca='piedi', dietro=0.0, fl=(fl, -0.15), fr=(-1.0, -0.2), testa=(1.3, tz), prob=-0.25, orecchie=0.25)
    return S_

def gey_top(t):
    """altezza della cima del getto sul tetto (mondo)."""
    up = ramp(t, T_FUORI, T_FUORI + 0.55); down = ramp(t, T_ALLAGA, T_ALLAGA + 0.9)
    return GEY.z + 0.2 + 24.0 * (sm(up) ** 0.7) * (1 - down) + 0.6 * math.sin(t * 9) * up * (1 - down)

def mtp(t):
    """Martina piccola: loc, rot (eulero), testa (beccheggio), antenne (oscillazione), zampe (agitazione), sc."""
    bob = 0.004 * math.sin(t * 3.1)
    S_ = dict(loc=Vector((BX - 0.01, WC.y + 0.02, QW + 0.085 + bob)), rot=(PI, 0, 0.25), testa=2.0, ant=0.25 * math.sin(t * 4), zam=0.15, sc=1.0, wave=0.0)
    if t < T_BAGNO: S_.update(loc=Vector((BX - 0.08, WC.y - 0.1, QW + 0.085 + bob)))         # di lato: la camera e' nel water
    if t < T_VORT:
        if T_MART <= t < T_SCARA:
            up = 0.11 * ramp(t, T_MART, T_MART + 0.2) * (1 - ramp(t, T_SCARA - 0.2, T_SCARA)); S_.update(wave=1.0, loc=S_['loc'] + Vector((0, 0, up)))
        if t >= T_SCARA: S_.update(wave=0.6 * math.sin(PI * ramp(t, T_SCARA + 0.7, T_TIRA)))
    elif t < T_RISALE:                                                # risucchiata dal vortice
        u = ramp(t, T_VORT, T_RISALE - 0.18); r = 0.11 * (1 - u); a = 0.25 + 28 * u * (1 + u)
        S_.update(loc=Vector((BX + r * math.cos(a), WC.y + 1.25 * r * math.sin(a), QW + 0.085 - 0.2 * u ** 1.5)), rot=(PI, 0, a + 1.0), sc=1.0 - 0.5 * u, zam=0.6)
    elif t < T_VALIGIA:                                               # salta fuori e atterra sul bordo della tavoletta
        u = ramp(t, T_RISALE, T_RISALE + 0.55); a = Vector((BX, WC.y, QW - 0.05)); b = SEAT + Vector((0, 0, 0.018))
        p = a.lerp(b, u); p.z += 0.45 * math.sin(PI * u)
        flip = PI * (1 - sm(u))
        S_.update(loc=p, rot=(flip, 0, 0.0), testa=0.0, zam=0.4 * (1 - u), wave=0.0)
    elif t < T_TRASF:                                                 # in posa sul bordo con la valigia
        S_.update(loc=SEAT + Vector((0, 0, 0.018)), rot=(0.12 * math.sin(PI * ramp(t, T_VALIGIA, T_VALIGIA + 0.3)), 0, -0.2), testa=-0.35, zam=0.05, ant=0.35 * math.sin(t * 6))
    elif t < T_COMPRA:                                                # sdraiata sul divano di Pippo, a pancia in su
        S_.update(loc=DIVANO + Vector((0, 0, 0.07)), rot=(PI + 0.35, 0, 0.2), testa=2.2, zam=0.05, ant=0.2 * math.sin(t * 3))
    else:                                                             # l'elefante atterra: fa un balzo sul divano
        u = ramp(t, T_ELE, T_ELE + 0.45); S_.update(loc=DIVANO + Vector((0, 0, 0.07 + 0.5 * math.sin(PI * u))), rot=(PI + 0.35 + 2 * PI * sm(u), 0, 0.2), testa=2.2, zam=0.5 * math.sin(PI * u), ant=0.2)
    return S_

def mgp(t):
    """Martina gigante: loc, rot, sc (della radice), testa, zampe (agitazione), schiacciata (0..1)."""
    up = ramp(t, T_SU, T_SU + 0.95); z = -32.0 + 51.0 * (1 - (1 - up) ** 2.4) + 1.2 * math.sin(PI * ramp(t, T_SU + 0.9, T_SU + 1.5))
    S_ = dict(loc=Vector((MG_X, MG_Y - 9.0, z)), rot=(-PI / 2, 0, 0.0), sc=(1, 1, 1), testa=1.35 + 0.15 * math.sin(t * 2.5), zam=1.0, roar=ramp(t, T_40 - 0.1, T_40 + 0.15) * (1 - ramp(t, T_40 + 0.9, T_40 + 1.3)))
    if t >= T_SCIAF:                                                  # SCIAF: schiacciata nell'acqua
        u = ramp(t, T_SCIAF, T_SCIAF + 0.18)
        S_.update(sc=(1.0 + 0.6 * u, 1.0 - 0.88 * u, 1.0 + 0.4 * u), loc=Vector((MG_X, MG_Y - 9.0, 19.0 - 14.9 * u)), zam=0.2)
    if t >= T_TAPPETO:                                                # ora e' il tappeto del salotto
        k = 2.3 / LG
        S_.update(loc=TAP + Vector((0, 0, 0.004)), rot=(0, 0, 0.18), sc=(k * 1.25, k * 1.25, k * 0.05), testa=0.0, zam=0.0, roar=0.0)
    return S_

def tp(t):
    """Tumbo: loc, yaw, beccheggio, mastica (scuote la testa), zampe davanti (applauso)."""
    S_ = dict(loc=Vector((BX + 0.6, 0.75, 0)), yaw=yaw_to((BX + 0.6, 0.75), (BX + 1.6, -0.9)), pitch=0.0, chew=1.0, clap=0.0)
    if T_COMPRA <= t < T_CADE:
        S_.update(loc=Vector((SX - 2.3, 1.1, 0)), yaw=yaw_to((SX - 2.3, 1.1), (SX, -1.0)), chew=0.6)
    elif T_TUMBO <= t < T_SALTO:                                      # l'eroe sul camino
        u = ramp(t, T_CIAB, T_CIAB + 0.4)
        S_.update(loc=CAMINO.copy(), yaw=yaw_to(CAMINO, (2.6, 4.0)) * (1 - u) + PI * u, chew=0.0)
    elif T_SALTO <= t < T_TAPPETO:                                    # il salto e lo SCIAF
        a = CAMINO; b = Vector((MG_X + 0.3, MG_Y - 13.5, 47.0)); c = Vector((MG_X + 0.3, MG_Y - 13.5, 5.6))
        if t < T_SCIAF - 0.06:
            u = ramp(t, T_SALTO, T_SCIAF - 0.06); p = a.lerp(b, u); p.z = a.z + (b.z - a.z) * (1 - (1 - u) ** 2)
        else:
            u = ramp(t, T_SCIAF - 0.06, T_SCIAF + 0.2); p = b.lerp(c, u)
        S_.update(loc=p, yaw=PI, pitch=-0.3, chew=0.0)
    elif t >= T_TAPPETO:                                              # in salotto, con la ciabatta in bocca; poi applaude
        S_.update(loc=Vector((SX + 0.0, -1.45, 0)), yaw=yaw_to((SX, -1.45), (SX + 0.45, -3.2)), chew=0.4)
        if t >= T_TEAM: S_.update(pitch=-0.95 * ramp(t, T_TEAM, T_TEAM + 0.25), clap=1.0, chew=0.0, loc=Vector((SX + 0.0, -1.45, 0.18 * ramp(t, T_TEAM, T_TEAM + 0.25))))
    return S_

def gs_pose(t, tl, tyaw, tpitch):
    """ciabatta gigante: perno (in bocca a Tumbo) e beccheggio. -pi/2 = in piedi con la suola verso Martina; 0 = suola in giu'."""
    m = Vector((0, -0.555, 0.4575)); mw = Matrix.Rotation(tyaw, 3, 'Z') @ Matrix.Rotation(tpitch, 3, 'X') @ m
    piv = tl + mw
    if t < T_SALTO: th = -PI / 2 + 0.03 * math.sin(t * 3)
    elif t < T_SCIAF - 0.06: th = -PI / 2 - 0.7 * ramp(t, T_SALTO, T_SCIAF - 0.3)              # la carica, all'indietro sopra la testa
    else: th = (-PI / 2 - 0.7) * (1 - ramp(t, T_SCIAF - 0.06, T_SCIAF + 0.02))                  # giu' di colpo
    return piv, th

# ======================= chiavi =======================
def K(o, f, loc=None, rot=None, scale=None):
    if loc is not None: o.location = loc; o.keyframe_insert('location', frame=f)
    if rot is not None: o.rotation_euler = rot; o.keyframe_insert('rotation_euler', frame=f)
    if scale is not None: o.scale = scale if isinstance(scale, (tuple, list)) else (scale,) * 3; o.keyframe_insert('scale', frame=f)
ES_HIP = Vector((0, 1.05 * ES, -0.55 * ES)); ES_LEG = 1.18 * ES
def ele_keys(f, s):
    th = s['theta']; R_ = Matrix.Rotation(th, 3, 'X')
    if s['anca'] == 'piedi': hip0 = Vector((0, 0.0, ES_LEG))                      # anca sopra i piedi (in piedi)
    elif s['anca'] == 'seduto': hip0 = Vector((0, 0.0, s['hz']))                  # anca sulla tavoletta (o sul colmo del tetto)
    else: hip0 = Vector((0, 1.05 * ES, 1.2 * ES))
    body = hip0 - R_ @ ES_HIP if s['anca'] else Vector((0, 0, 1.75 * ES))
    K(E['root'], f, tuple(s['loc']), (s['rot'][0], s['rot'][1], s['yaw']), s['sc'])
    K(E['body'], f, tuple(body), (th, 0, 0))
    for i, lg in enumerate(E['legs']):
        back = i in (1, 3)
        if back: K(lg, f, rot=(s['dietro'] - th, s['dietro_y'] * (1 if i == 1 else -1), 0))
        else: K(lg, f, rot=(*(s['fl'] if i == 0 else s['fr']), 0))
    K(E['head'], f, rot=(s['testa'][0], 0, s['testa'][1]))
    for k, sg in enumerate(E['trunk']): K(sg, f, rot=(s['prob'] if k else 0.18, 0, 0))
    for k, ea in enumerate(E['ears']):
        sx = -1 if k == 0 else 1; K(ea, f, rot=(0, 0, sx * (0.35 + 0.6 * s['orecchie'])))

gsprev = None
for f in range(1, NF + 1):
    t = (f - 1) / FPS
    # Pippo
    s = pp(t)
    K(P['root'], f, tuple(s['loc']), (s['lean'], 0, s['yaw']), s['sc']); K(P['body'], f, rot=(s['bend'], 0, s['twist'])); K(P['head'], f, rot=s['head'])
    for nm, k_ in (('L', 'aL'), ('R', 'aR')):
        sh = P['shoulder' + nm]; sh.rotation_quaternion = qdir(s[k_]); sh.keyframe_insert('rotation_quaternion', frame=f)
    # Tumbo
    s = tp(t)
    K(Tb['root'], f, tuple(s['loc']), (s['pitch'], 0, s['yaw']), 0.75)
    K(Tb['head'], f, rot=(0.1 * s['chew'] * math.sin(t * 9), 0, 0.35 * s['chew'] * math.sin(t * 7.5)))
    cl = s['clap'] * math.sin(t * 2 * PI * 3.0)
    K(Tb['legFL'], f, rot=(-1.2 * s['clap'], 0, -0.5 * s['clap'] + 0.45 * cl)); K(Tb['legFR'], f, rot=(-1.2 * s['clap'], 0, 0.5 * s['clap'] - 0.45 * cl))
    K(Tb['tail'], f, rot=(-0.5, 0, 0.6 * math.sin(t * 14)))
    if T_TUMBO <= t < T_TAPPETO:                                      # la ciabatta gigante in bocca
        piv, th = gs_pose(t, s['loc'], s['yaw'], s['pitch'])
        K(GSP, f, tuple(piv), (th, 0, PI))
    # Martina piccola
    s = mtp(t)
    K(MT['root'], f, tuple(s['loc']), s['rot'], s['sc'])
    K(MT['testa'], f, rot=(s['testa'], 0, 0))
    for k, a_ in enumerate(MT['antenne']): K(a_, f, rot=(s['ant'] * (1 if k else -1), 0, 0.2 * math.sin(t * 5 + k)))
    for k, z_ in enumerate(MT['zampe']):
        w = s['wave'] * (0.6 * math.sin(t * 14)) if k == 0 else 0.0
        K(z_, f, rot=(s['zam'] * math.sin(t * 17 + k * 1.7) + w, 0, (0.9 * s['wave'] if k == 0 else 0.0)))
    if t < T_VORT + 0.6:                                              # la ciambella sotto di lei, il flacone accanto
        K(RING, f, (s['loc'].x, s['loc'].y, max(s['loc'].z - 0.078, QW - 0.2)), (0.0, 0.0, s['rot'][2] - 0.25), (1, 1, 1))
    bp_ = Vector((BX - 0.1, WC.y - 0.2, 0)) if t < T_BAGNO else Vector((BX + 0.12, WC.y + 0.1, 0))
    K(BOTT, f, (bp_.x, bp_.y, QW - 0.035 + 0.006 * math.sin(t * 2.3 + 1)), (-0.55 + 0.04 * math.sin(t * 1.7), 0.15, 0.12))
    if t < T_TRASF: K(VAL, f, tuple(SEAT + Vector((0.075, -0.035, 0.0))), (0, 0, -0.35))
    else:
        u = ramp(t, T_ELE, T_ELE + 0.45) if t >= T_ELE else 0.0
        K(VAL, f, tuple(DIVANO + Vector((0.3, -0.18, 0.35 * math.sin(PI * u)))), (0, 0, 0.3 + 1.5 * u))
    # Martina gigante
    if t >= T_ESCE - 0.1:
        s = mgp(t)
        K(MG['root'], f, tuple(s['loc']), s['rot'], s['sc'])
        K(MG['testa'], f, rot=(s['testa'] + 0.12 * s['roar'] * math.sin(t * 30), 0, 0.15 * math.sin(t * 1.9)))
        for k, a_ in enumerate(MG['antenne']): K(a_, f, rot=(0.25 * math.sin(t * 2.2 + k), 0, 0.3 * math.sin(t * 1.7 + 2 * k)))
        for k, z_ in enumerate(MG['zampe']):
            sx = -1 if k % 2 == 0 else 1
            if t < T_TAPPETO: K(z_, f, rot=(0.35 * s['zam'] * math.sin(t * 4.5 + k * 1.3), -sx * 0.45, 0.2 * math.sin(t * 3 + k)))
            else: K(z_, f, rot=(0, 0, 0))
        if t >= T_TAPPETO:                                            # occhiolino con l'antenna
            w_ = math.sin(PI * ramp(t, 31.0, 31.6)) + math.sin(PI * ramp(t, T_TEAM + 0.6, T_TEAM + 1.3))
            K(MG['antenne'][1], f, rot=(0, 0, 0.9 * w_ * math.sin(t * 16)))
        if t < T_SCIAF:                                               # la valigia gigante appesa alla zampa davanti destra
            Mr = Matrix.Translation(s['loc']) @ Euler(s['rot']).to_matrix().to_4x4() @ Matrix.Diagonal((*s['sc'], 1.0))
            zr = (0.35 * s['zam'] * math.sin(t * 4.5 + 1.3), -0.45, 0.2 * math.sin(t * 3 + 1))
            Ml = Matrix.Translation((0.11 * LG, -0.27 * LG, 0.26 * LG - 0.04 * LG)) @ Euler(zr).to_matrix().to_4x4()
            foot = Mr @ Ml @ Vector((0.36 * LG, -0.22 * LG, -0.254 * LG))
            K(VALG, f, tuple(foot + Vector((0, 0, -7.2))), (0.12 * math.sin(t * 2), 0.0, 0.25), tuple(VALG_S))
        elif t < T_TAPPETO: K(VALG, f, (MG_X + 17.0, MG_Y - 6.0, max(-6.0, 6.0 - 40 * (t - T_SCIAF))), (0.2, 0.15, 0.3), tuple(VALG_S))
        else: K(VALG, f, tuple(TAP + Vector((1.45, 0.55, 0.0))), (0, 0, -0.5), (VALG_S.x * 0.11, VALG_S.y * 0.11, VALG_S.z * 0.012))
    # elefante
    ele_keys(f, ep(t))
    # acqua: alluvione e getti
    wz = -0.5 + 2.25 * sm(ramp(t, T_FUORI + 0.35, T_ALLAGA + 1.2))
    K(ALL, f, (0, 0, wz))
    ALLN.inputs['W'].default_value = t * 0.35; ALLN.inputs['W'].keyframe_insert('default_value', frame=f)
    if T_ESPLODE - 0.05 <= t < T_FUORI:
        h = 0.05 + 6.0 * ramp(t, T_ESPLODE, T_ESPLODE + 0.35)
        K(G_IN['root'], f, scale=(1, 1, h)); K(G_IN['cima'], f, (BX, WC.y, QW + h)); K(G_IN['scorre'], f, (0, 0, -t * 6.0))
    if T_FUORI - 0.05 <= t < T_ALLAGA + 1.0:
        top = gey_top(t); K(G_OUT['root'], f, scale=(1, 1, max(0.05, top - GEY.z))); K(G_OUT['cima'], f, (GEY.x, GEY.y, top)); K(G_OUT['scorre'], f, (0, 0, -t * 14.0))
    for a_, p0, rz, k in AUTO:
        fl_ = max(0.0, wz + 0.5 - 0.65); K(a_, f, (p0.x + 0.6 * math.sin(t * 0.7 + k), p0.y, p0.z + max(0.0, wz - 0.75) + 0.06 * math.sin(t * 2.2 + k)), (0.06 * math.sin(t * 1.6 + k), 0.05 * math.cos(t * 1.3 + k), math.radians(rz) + 0.15 * math.sin(t * 0.5 + k) * min(1.0, fl_)))
    K(VORT, f, rot=(0, 0, -t * 16.0))
    if T_CADE <= t < T_ESPLODE:                                        # il water schiacciato dal bestione
        sq = 1.0 - 0.3 * ramp(t, T_SEDUTO, T_SEDUTO + 0.12)
        K(W['root'], f, scale=(1 + 0.2 * (1 - sq), 1 + 0.2 * (1 - sq), sq))
    elif t < T_CADE: K(W['root'], f, scale=(1, 1, 1))
    pz = -0.012 * math.sin(PI * ramp(t, T_TIRA + 0.25, T_TIRA + 0.55)) if T_TIRA <= t < T_VORT else 0.0
    K(W['pulsante'], f, (0, 0.52, 1.16 + pz))

# ======================= cocci, tegole e schizzi =======================
M_COCCIO = M25['ceramica']; M_TEGOLA = bpy.data.materials.get('PT_roof0') or material('P25_tegola', (0.55, 0.2, 0.12), rough=0.8)
def detriti(n, centro, t0, v0, mat, sc, coll, nome, g=9.8, vis=(0, 0)):
    out_ = []
    for k in range(n):
        o = obj(nome, set004.box_c() if 'Tegola' in nome else shared_mesh('sphere'), (0, 0, -90), sc, mat, coll); o.rotation_mode = 'XYZ'
        a = rnd.uniform(0, 2 * PI); v = Vector((math.cos(a) * rnd.uniform(0.4, 1.0), math.sin(a) * rnd.uniform(0.4, 1.0), rnd.uniform(0.8, 1.4))) * v0
        spin = Vector((rnd.uniform(-9, 9), rnd.uniform(-9, 9), rnd.uniform(-9, 9)))
        for f in range(max(1, fr(t0) - 1), min(NF, fr(t0 + 1.2)) + 1):
            tt = (f - 1) / FPS - t0
            if tt < 0: K(o, f, (0, 0, -90)); continue
            p = Vector(centro) + v * tt + Vector((0, 0, -0.5 * g * tt * tt))
            K(o, f, tuple(p), tuple(spin * tt))
        show_only(o, [(t0, min(TOTAL + 1, t0 + 1.2))]); out_.append(o)
    return out_
detriti(14, (BX, WC.y, 0.5), T_ESPLODE, 4.0, M_COCCIO, (0.07, 0.05, 0.04), prc, 'Coccio')
detriti(16, (GEY.x, GEY.y, 6.0), T_FUORI + 0.05, 9.0, M_TEGOLA, (0.5, 0.3, 0.06), prc, 'Tegola')

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
emo(0.0, 'sorpreso', 1.0); emo(2.2, 'ride', 0.7); emo(T_BAGNO, 'sorpreso', 1.0); emo(T_SCARA, 'sorpreso', 0.8)
emo(T_TIRA, 'arrabbiato', 0.8); emo(T_RISALE, 'spaventato', 1.0); emo(T_VALIGIA, 'sorpreso', 1.0); emo(T_STRONZA, 'arrabbiato', 1.0)
emo(T_LOGICA + 0.15, 'furbo', 1.0); emo(T_ELE + 0.05, 'felice', 1.0); emo(T_TANGO, 'normale', 1.0, smile=0.9, brow=0.5)
emo(T_CASQUE + 0.35, 'spaventato', 0.8); emo(T_BESTIONE, 'spaventato', 1.0); emo(T_ALLAGA, 'spaventato', 1.0); emo(T_TUMBO, 'sorpreso', 1.0)
emo(T_BALLA, 'normale', 1.0, smile=0.9, brow=0.5); emo(T_TEAM + 0.3, 'felice', 1.0)
tex(0.0, tongue=0.0, brow=-0.3); tex(T_COMPRA, tongue=0.6, eye_scale=1.15); tex(T_TUMBO, tongue=0.0, brow=0.9, eye_scale=1.0); tex(T_TAPPETO, tongue=0.0, brow=0.0); tex(T_TEAM, tongue=0.8, eye_scale=1.1)

# ======================= effetti =======================
FXC = prc
def fx(name, pos, w, t0, dur, **k): return A.effetto(name, posizione=tuple(pos), larghezza=w, animazione=(fr(t0), int(dur * FPS)), collezione=FXC, **k)
ACQ = (0.75, 0.9, 1.0)
fx('emoticon/swirl', (BX + 0.3, 0.75, 2.05), 0.35, 2.3, 0.9)                                                  # «uno in ferie»
fx('emoticon/exclamation', (BX + 0.3, 0.85, 1.95), 0.3, T_MART, 0.8)
for k in range(3): fx('schizzi/splat%02d' % (k * 7), (BX + rnd.uniform(-0.1, 0.1), WC.y + rnd.uniform(-0.1, 0.1), QW + 0.08), 0.22, T_RISALE + 0.02 * k, 0.45, colore=ACQ, opacita=0.9)
fx('emoticon/star', SEAT + Vector((0.1, -0.05, 0.16)), 0.12, T_VALIGIA, 0.6)
fx('emoticon/anger', (SX + 0.75, 0.62, 2.35), 0.35, T_STRONZA + 0.1, 1.0)
fx('emoticon/idea', (SX + 0.6, 0.72, 2.45), 0.32, T_LOGICA + 0.3, 1.2)
for k in range(4): fx('sbuffo_bianco/whitepuff%02d' % (k * 2), LAND + Vector((-1.4 + 0.9 * k, -0.9, 0.3)), 1.6, T_ELE + 0.02 * k, 0.6, colore=(0.85, 0.8, 0.72), opacita=0.7)
for k in range(4): fx('sbuffo_bianco/whitepuff%02d' % (k * 2 + 1), LAND + Vector((-1.2 + 0.8 * k, -0.4, 4.05)), 1.5, T_ELE - 0.2 + 0.02 * k, 0.55, colore=(0.92, 0.9, 0.86), opacita=0.8)   # sfonda il soffitto
for k in range(5): fx('emoticon/music', (SX - 1.2 + 0.6 * k, -0.1, 3.2 + 0.25 * (k % 2)), 0.3, T_TANGO + 0.3 * k, 0.9)
fx('emoticon/exclamations', (SX + 0.6, -0.5, 2.6), 0.4, T_CASQUE + 0.6, 0.8)
for k in range(4): fx('sbuffo_bianco/whitepuff%02d' % (k + 3), (BX - 1.0 + 0.65 * k, WC.y - 0.2, 3.45), 1.3, T_CADE + 0.15 + 0.03 * k, 0.6, colore=(0.9, 0.88, 0.85), opacita=0.75)
for k in range(3): fx('sbuffo_bianco/whitepuff%02d' % (k + 5), (BX - 0.5 + 0.5 * k, WC.y - 0.4, 0.4), 1.0, T_SEDUTO, 0.5, colore=(0.9, 0.9, 0.9), opacita=0.6)
for k in range(8): fx('schizzi/splat%02d' % (k * 3 + 1), (BX + rnd.uniform(-1.2, 1.2), WC.y + rnd.uniform(-1.0, 0.2), rnd.uniform(0.6, 2.8)), rnd.uniform(0.5, 1.0), T_ESPLODE + 0.03 * k, 0.5, colore=ACQ, opacita=0.95)
for k in range(10): fx('schizzi/splat%02d' % (k * 2 + 2), (GEY.x + rnd.uniform(-5, 5), GEY.y + rnd.uniform(-4, 3), rnd.uniform(6, 22)), rnd.uniform(2.0, 4.0), T_FUORI + 0.05 * k, 0.6, colore=ACQ, opacita=0.9)
for k in range(12): fx('schizzi/splat%02d' % (k * 2 + 1), (rnd.uniform(-22, 22), rnd.uniform(-16, 18), rnd.uniform(0.5, 3.0)), rnd.uniform(2.0, 3.5), T_ALLAGA + 0.08 * k, 0.6, colore=ACQ, opacita=0.85)
for k in range(8): fx('sbuffo_bianco/whitepuff%02d' % (k % 8), (MG_X + rnd.uniform(-9, 9), MG_Y + rnd.uniform(-6, 0), 1.6), 2.4, T_ESCE + 0.06 * k, 0.5, colore=ACQ, opacita=0.7)
for k in range(14): fx('schizzi/splat%02d' % (k * 2), (MG_X + rnd.uniform(-12, 12), MG_Y - 7 + rnd.uniform(-2, 3), rnd.uniform(2, 16)), rnd.uniform(3.0, 6.0), T_SU + 0.05 * k, 0.7, colore=ACQ, opacita=0.9)
for k in range(26): fx('schizzi/splat%02d' % ((k * 3) % 30), (MG_X + rnd.uniform(-24, 24), MG_Y - 4 + rnd.uniform(-6, 8), rnd.uniform(2, 22)), rnd.uniform(6.0, 12.0), T_SCIAF + 0.02 * k, 0.9, colore=ACQ, opacita=0.95)
for k in range(8): fx('sbuffo_bianco/whitepuff%02d' % (k % 8), (MG_X + rnd.uniform(-18, 18), MG_Y - 4 + rnd.uniform(-4, 6), 3.0), 9.0, T_SCIAF + 0.04 * k, 0.8, colore=ACQ, opacita=0.8)
fx('emoticon/heart', TAP + Vector((-0.6, -0.4, 2.9)), 0.35, T_TEAM + 0.4, 1.0)
fx('emoticon/hearts', TAP + Vector((0.5, -0.5, 3.1)), 0.4, T_TEAM + 0.8, 1.2)

# lampo bianco agli impatti (davanti alla camera)
M_LAMPO = material('P25_lampo', (1, 1, 1), rough=1.0, emit=(1, 1, 1), emit_strength=8.0)
LAMPO = obj('Lampo', shared_mesh('cyl:1:1'), (0, 0, -0.05), (0.2, 0.2, 0.001), M_LAMPO, cac, rot=(0, 0, 0), parent=cam)
show_only(LAMPO, [(T_ESPLODE, T_ESPLODE + 0.09), (T_SCIAF, T_SCIAF + 0.09)])

# ======================= camera =======================
SHOTS = [  # t0, t1, camera da, a, mira da, a, lente, diaframma
    (0.0, T_BAGNO, (BX + 0.06, 1.37, 0.455), (BX + 0.06, 1.36, 0.452), (BX, 0.95, 1.42), (BX, 0.95, 1.45), 14, 8.0),                  # 01 dentro il water: la faccia di Pippo
    (T_BAGNO, T_SCARA, (BX + 1.6, -0.9, 1.25), (BX + 1.5, -0.8, 1.22), (BX - 0.2, 0.9, 0.9), (BX - 0.2, 0.9, 0.9), 22, 8.0),           # 02 il bagno: indizi
    (T_SCARA, T_TIRA, (BX - 0.02, 0.74, 0.98), (BX - 0.02, 0.82, 0.92), (BX, WC.y + 0.03, QW + 0.08), (BX, WC.y + 0.03, QW + 0.08), 46, 5.0),  # 03 Martina nel water
    (T_TIRA, T_VORT, (BX - 0.85, 0.3, 1.55), (BX - 0.8, 0.35, 1.52), (BX + 0.2, 1.55, 1.15), (BX + 0.2, 1.55, 1.15), 26, 6.0),         # 04a lo sciacquone
    (T_VORT, T_RISALE, (BX, WC.y - 0.03, 1.32), (BX, WC.y - 0.02, 1.12), (BX, WC.y, QW), (BX, WC.y, QW), 30, 8.0),                     # 04b il vortice dall'alto
    (T_RISALE, T_VALIGIA, (BX + 0.05, 0.38, 0.78), (BX + 0.05, 0.42, 0.78), (BX, 1.05, 0.72), (BX, 1.05, 0.72), 30, 5.0),                # 05 risale
    (T_VALIGIA, T_TRASF, (BX + 0.22, 0.5, 0.7), (BX + 0.2, 0.55, 0.7), (BX + 0.02, SEAT.y, 0.66), (BX + 0.02, SEAT.y, 0.66), 45, 3.2),  # 06 con la valigia
    (T_TRASF, T_STRONZA, (SX + 0.5, 1.2, 0.68), (SX + 0.46, 1.27, 0.67), (SX + 0.03, 1.98, 0.66), (SX + 0.03, 1.98, 0.66), 35, 4.0),   # 07 sul divano
    (T_STRONZA, T_LOGICA, (SX + 1.6, 1.0, 1.1), (SX + 1.55, 1.02, 1.12), (SX + 0.25, 1.15, 1.25), (SX + 0.25, 1.15, 1.28), 16, 8.0),         # 08 quella stronza
    (T_LOGICA, T_COMPRA, (SX + 0.35, -1.4, 1.75), (SX + 0.35, -1.1, 1.75), (SX + 0.35, 0.72, 1.72), (SX + 0.35, 0.72, 1.75), 40, 3.2),  # 09 la cosa piu' logica
    (T_COMPRA, T_TANGO, (SX - 0.2, -5.6, 1.9), (SX - 0.2, -5.3, 1.9), (SX - 0.2, 0.2, 1.75), (SX - 0.2, 0.2, 1.75), 21, 11),              # 10 compra un elefante
    (T_TANGO, T_CASQUE, (SX + 0.0, -4.2, 1.9), (SX + 0.4, -4.1, 1.9), (SX - 0.05, 0.0, 1.75), (SX + 0.35, 0.0, 1.75), 22, 9),          # 11 il tango
    (T_CASQUE, T_CADE, (SX + 1.1, -4.0, 1.6), (SX + 1.2, -3.9, 1.6), (SX + 1.4, 0.0, 1.45), (SX + 1.7, 0.0, 1.35), 18, 9),                # 12 il casque'
    (T_CADE, T_ESPLODE, (BX + 0.9, -2.05, 1.25), (BX + 0.85, -2.0, 1.27), (BX, 1.0, 1.25), (BX, 1.0, 1.3), 16, 9),                       # 13 cade sul water
    (T_ESPLODE, T_FUORI, (BX + 0.9, -1.2, 0.45), (BX + 0.9, -1.2, 0.5), (BX, WC.y, 2.0), (BX, WC.y, 2.2), 17, 12),                      # 14 esplode
    (T_FUORI, T_ALLAGA, (6.5, -15.5, 2.2), (6.5, -15.0, 2.6), (-0.5, 9.5, 17.0), (-0.5, 9.5, 21.0), 22, 22),                           # 15 il getto dal tetto
    (T_ALLAGA, T_ESCE, (30.0, -32.0, 21.0), (28.0, -30.0, 19.0), (0.0, 4.0, 1.0), (0.0, 5.0, 1.5), 24, 22),                            # 16 il quartiere si allaga
    (T_ESCE, T_TUMBO, (3.0, -7.5, 2.3), (3.0, -7.0, 2.4), (-0.4, 13.0, 9.5), (-0.4, 15.0, 15.0), 18, 22),                               # 17-18 esce Martina, 40 metri
    (T_TUMBO, T_CIAB, (2.9, 9.0, 6.0), (2.85, 9.05, 5.95), (CAMINO.x, CAMINO.y, 6.9), (CAMINO.x, CAMINO.y, 7.4), 28, 8),               # 19 Tumbo sul camino
    (T_CIAB, 28.85, (9.0, -46.0, 13.0), (8.5, -44.0, 13.0), (0.5, 14.0, 20.0), (0.5, 14.0, 20.0), 22, 22),                              # 20 la ciabatta grande come un palazzo
    (28.85, T_TAPPETO, (-14.0, 1.0, 3.2), (-13.5, 1.5, 3.3), (0.0, 20.0, 20.0), (0.0, 20.0, 12.0), 16, 22),                          # 21 SCIAF
    (T_TAPPETO, T_BALLA, (SX + 0.3, -1.6, 4.4), (SX + 0.3, -1.3, 4.2), (TAP.x, TAP.y + 0.1, 0.0), (TAP.x, TAP.y + 0.1, 0.0), 24, 11),  # 22 Martina tappeto
    (T_BALLA, T_TEAM, (SX + 0.4, -5.2, 2.2), (SX + 0.6, -5.0, 2.15), (SX + 0.3, -0.35, 1.6), (SX + 0.6, -0.35, 1.6), 22, 11),          # 23 il tango sopra di lei
    (T_TEAM, TOTAL + 0.1, (SX + 0.5, -3.8, 1.6), (SX + 0.5, -3.65, 1.6), (SX + 0.55, -0.35, 1.3), (SX + 0.55, -0.35, 1.3), 20, 7),     # 24 il casque' finale
]
SHAKES = [(T_ELE, 0.06, 0.45), (T_STRONZA, 0.025, 0.5), (T_SEDUTO, 0.05, 0.5), (T_ESPLODE, 0.06, 0.7), (T_FUORI, 0.25, 0.9), (T_40, 0.18, 0.8), (T_SCIAF, 0.9, 1.0), (T_BESTIONE + 0.2, 0.04, 0.4)]
for f in range(1, NF + 1):
    t = (f - 1) / FPS
    s_ = next((s for s in SHOTS if s[0] <= t < s[1]), SHOTS[-1]); u = sm((t - s_[0]) / (s_[1] - s_[0]))
    cl = Vector(lerp(s_[2], s_[3], u)); tl = Vector(lerp(s_[4], s_[5], u))
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
for d in LIGHTS + [scene.world.node_tree, bpy.data.materials['M25_alluvione'].node_tree]: lin(d)
for d in LIGHTS + [scene.world.node_tree]:
    for fc in all_fcurves(d):
        for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'
set_interp(camd, 'CONSTANT')
for nm in ('Cam', 'CamTarget'):
    for fc in all_fcurves(bpy.data.objects[nm]):
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
