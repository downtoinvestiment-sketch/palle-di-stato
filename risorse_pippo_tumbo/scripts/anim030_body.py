# ===================================================================================================================
# Video 030 - ROSPINA O CASTORA?, 44,8 s. Si unisce alla testa: templates/head.py + scripts/anim030_body.py -> scripts/anim030.py
# Copione n. 32 v3 (COPIONI.md): i bonus al posto delle riforme e l'opposizione che fa peggio. Scelte dell'autore (21 novembre 2026):
# S1 monopattino classico rosso, D1 diga di tronchi, K3 canotto a papera. Rospina (stile 'D') e la Castora (stile 'A') sono politiche
# inventate. Posti: la piazza col palazzo e il negozio (sul prato a sud della strada), l'autostrada con la diga e il supermercato (x = 300),
# poi la piazza allagata. Tempi da audio/words_t030.json. Senza insulti. Luce «cinema».
# ===================================================================================================================
import props021, props023, props024, props028, props030, luci, random, json, rospina, castora, gente027
import pippo2 as pippo
A = kitlook.A
BLEND = os.environ.get('BLEND030', '../t030/pippo_t030.blend')
F30 = props028.font(); M30 = props030.mats030(props028.mats028(A), A)
rnd = random.Random(30)

# ======================= tempi (dalla voce) =======================
T_BENE = 3.12; T_NO = 5.36; T_MALE = 6.02; T_PREZZI = 7.46; T_TASSE = 8.70; T_RISOLVE = 9.86; T_BONUS = 11.48
T_BMONO = 12.10; T_500 = 13.30; T_IERI = 14.76; T_OGGI = 16.92; T_2000 = 17.26; T_GRAZIE = 18.18; T_TUTTI = 19.44
T_MA = 21.02; T_CAST = 22.92; T_ALLORA = 24.02; T_LOGICA = 25.54; T_DIGA = 25.98; T_AUTO = 27.58; T_CONTRO = 29.00; T_ROSI = 30.30; T_CROLLO = 31.75
T_ACQUA = 32.94; T_VOTA = 34.82; T_RESTA = 36.68; T_PORCA = 38.64; T_FESTA = 39.70; T_BCAN = 41.28; T_DOM = 42.86
TOTAL = 44.8; NF = int(TOTAL * FPS)
FASI = [(0.0, 'SQ'), (T_DIGA, 'HW'), (T_ACQUA, 'FL')]
def iv(*codes):
    out = []
    for i, (t0, c) in enumerate(FASI):
        t1 = FASI[i + 1][0] if i + 1 < len(FASI) else TOTAL + 1
        if c in codes:
            if out and abs(out[-1][1] - t0) < 1e-6: out[-1] = (out[-1][0], t1)
            else: out.append((t0, t1))
    return out

# ======================= l'autostrada (x = 300): alberi, case e palazzi prima del look, cosi' diventano veri =======================
HX = 300.0
for (x, y) in ((-9, -12), (9.5, -20), (-10.5, -30), (10, 6), (-9, 16), (11, 22), (-22, -8), (22, -14), (-30, 4), (27, 9), (-26, 26), (18, 34), (-12, 38), (8, -40), (-16, -44)): tree(HX + x, y, rng.uniform(1.1, 1.6))
for k, x in enumerate(range(-60, 70, 14)): tower_at(HX + x + rng.uniform(-2, 2), 62 + rng.uniform(0, 8), 0.0)
for k, y in enumerate(range(-50, 60, 16)): tower_at(HX + 58 + rng.uniform(0, 6), y, -PI / 2); tower_at(HX - 60 - rng.uniform(0, 6), y, PI / 2)
for k, x in enumerate(range(-44, 50, 11)):
    if abs(x) > 9: house_at(HX + x + rng.uniform(-1, 1), 40 + rng.uniform(0, 3), 0.0, int(rng.integers(0, 6)), int(rng.integers(0, 4)), int(rng.integers(0, 5)), bool(rng.integers(0, 2)))

# ======================= rendering e luce =======================
setup_render(scene, 1080, 1920, samples=3, fps=FPS, frames=NF); scene.frame_end = NF
scene.render.image_settings.color_mode = 'RGB'; scene.render.image_settings.compression = 90
camd = bpy.data.cameras.new('Cam'); cam = bpy.data.objects.new('Cam', camd); cac.objects.link(cam); scene.camera = cam
camd.clip_start = 0.01; camd.clip_end = 3000; camd.sensor_width = 36
tgt = empty('CamTarget', (0, 0, 1), None, cac)
ct = cam.constraints.new('TRACK_TO'); ct.target = tgt; ct.track_axis = 'TRACK_NEGATIVE_Z'; ct.up_axis = 'UP_Y'
camd.dof.use_dof = True; camd.dof.focus_object = tgt
kitlook.upgrade(scene, M, envc, prc, extras=False)
scene.eevee.taa_render_samples = 3
for o in list(bpy.data.objects):                                       # il look pianta alberi-sagoma anche in mezzo alla piazza: via
    if o.name.startswith('PT_sagoma') and abs(o.location.x) < 19.5 and -34.0 < o.location.y < -13.0: bpy.data.objects.remove(o)
CIELO = luci.cielo_basso(scene.world, 0.42)
scene.world.use_sun_shadow = False
SUN = luci.sole(prc, (0.25, -0.97), lato=1, energia=4.3)
luci.ombre_pulite(scene, mezza_risoluzione=True)
props021.bagliore(scene, forza=0.25, soglia=1.6)
scene.view_settings.exposure = 0.02

# ======================= posti =======================
PAL = Vector((6.5, -18.5, 0.0))                  # il palazzo (facciata verso sud)
RB = Vector((6.0, -19.5, 4.3))                   # Rospina sul balcone
CNB = Vector((8.25, -19.45, 4.3))                # il cannone dei bonus sul balcone
NEG = Vector((-11.0, -18.2, 0.0))                # il negozio
MONO = NEG + Vector((-1.4, -2.2, 0.33))          # il monopattino sul piedistallo
TAG = Vector((-11.3, -21.0, 0.0))                # il cartello del prezzo
PS = Vector((2.4, -26.4, 0.0))                   # Pippo sotto il balcone
PS2 = Vector((-2.5, -25.0, 0.0))                 # Pippo in mezzo alla piazza
PSH = Vector((-10.0, -22.6, 0.0))                # Pippo davanti al negozio
CS = Vector((-4.2, -24.0, 0.0))                  # la Castora in piazza
DG = Vector((HX, 0.0, 0.0))                      # la diga
CD = Vector((HX - 2.6, -3.1, 0.0))               # la Castora che la costruisce
SUP = Vector((HX - 17.0, 12.0, 0.0))             # il supermercato (facciata a y = 12, tettoia fino a y = 7,4)
COL = SUP + Vector((-2.1, -4.0, 0.0))            # la colonna rosicchiata
WL = 1.5                                         # livello dell'acqua
D1 = Vector((-2.6, -22.4, 0.0)); D2 = Vector((1.3, -24.8, 0.0))   # il canotto: da dove arriva e dove si ferma (accanto al seggio)
SEG = Vector((3.9, -25.6, 0.0))                  # il seggio galleggiante
CLG = Vector((-0.9, -24.0, 0.0))                 # il tronco della Castora nel finale

# ======================= set =======================
sqc = collection('Piazza'); hwc = collection('Autostrada'); flc = collection('Allagamento')
try: m_pav = A.materiale('PavingStones070', dimensione=2.0)
except Exception as e: print('pavimento', e); m_pav = material('M30_piazza', (0.6, 0.58, 0.55), rough=0.9)
props028.box('Piazza', (-19.0, -33.0, 0.0), (19.0, -13.2, 0.03), m_pav, sqc)
PZ = props030.palazzo(sqc, M30, F30, A); PZ['root'].location = PAL
NG = props030.negozio(sqc, M30, F30); NG['root'].location = NEG
CAN = props030.cannone_bonus(sqc, M30, F30); CAN['root'].location = CNB; CAN['root'].rotation_mode = 'XYZ'; CAN['canna'].rotation_mode = 'XYZ'
SC = props030.monopattino(sqc, M30, 'S1'); SC['root'].rotation_mode = 'XYZ'
TAG300 = props028.cartellino(sqc, M30, F30, testo='300 €', h=1.0, nome='Prezzo300', larg=1.0, alt=0.5); TAG300.rotation_mode = 'XYZ'
TAG2000 = props028.cartellino(sqc, M30, F30, testo='2.000 €', h=1.0, nome='Prezzo2000', larg=1.25, alt=0.5); TAG2000.rotation_mode = 'XYZ'
TAG9000 = props028.cartellino(flc, M30, F30, testo='9.000 €', h=0.9, nome='Prezzo9000', larg=1.25, alt=0.5); TAG9000.rotation_mode = 'XYZ'
props028.festone(sqc, M30, (-15.0, -18.4, 5.7), (-1.2, -19.8, 8.4), n=14, nome='FestoneA', cala=1.2)
for k, (aid, p_, h_, rz) in enumerate((('street_lamp_01', (-16.0, -25.5), 4.6, 0), ('street_lamp_01', (14.5, -27.0), 4.6, 180), ('painted_wooden_bench', (-14.5, -29.0), 1.0, 90), ('painted_wooden_bench', (15.5, -30.5), 1.0, -90))):
    try: A.modello(aid, posizione=(p_[0], p_[1], 0.03), altezza=h_, rotazione=rz, collezione=sqc, max_triangoli=5000)
    except Exception as e: print('arredo', aid, e)
# la gente (pupazzi di gente027, non sono personaggi della serie): dodici in piazza, poi in fila al negozio col buono in mano; piu' il negoziante
GENTE = []
FOLLA = [(0.9, -24.6), (6.6, -25.6), (8.4, -24.6), (10.6, -26.4), (0.2, -27.2), (7.6, -27.8), (13.6, -30.4), (11.8, -24.2), (-0.9, -24.8), (9.6, -29.2), (6.4, -30.2), (12.8, -27.6)]
FILA = [(-7.9 + 0.35 * math.sin(k * 1.3), -21.0 - 0.95 * k) for k in range(12)]
for k in range(12):
    col_, R_ = gente027.pupazzo('Persona%d' % k, gente027.LOOK_FOLLA[k % len(gente027.LOOK_FOLLA)]); o = gente027.copia(sqc, col_, FOLLA[k][0], FOLLA[k][1], 0.03, 0.0, altezza=rnd.uniform(1.9, 2.15), nome='PersonaI%d' % k)
    o.rotation_mode = 'XYZ'; R_['shoulderR'].rotation_mode = 'QUATERNION'; R_['shoulderL'].rotation_mode = 'QUATERNION'
    b_ = props030.buono(col_, M30, F30, nome='BuonoP%d' % k); b_.parent = R_['shoulderR']; b_.location = (0.0, -0.06, -0.78); b_.rotation_euler = (PI, 0, 0); b_.scale = (0.75, 0.75, 0.75)
    GENTE.append((o, R_, b_, rnd.random() * 6.28))
NCOL, NR = gente027.pupazzo('Negoziante', gente027.LOOK_FOLLA[4]); NEGO = gente027.copia(sqc, NCOL, NEG.x + 3.4, NEG.y - 1.1, 0.03, 0.35, altezza=2.1, nome='NegozianteI')
for nm in 'LR': NR['shoulder' + nm].rotation_mode = 'QUATERNION'
# oggetti di Pippo in piazza
NUV = props030.nuvola(prc, M30); PORT = props030.portafoglio(chc, M30); BUONO = props030.buono(prc, M30, F30); BUONO.rotation_mode = 'XYZ'
ALATI = [props030.cartellino_alato(prc, M30, F30, testo='€', mat='carta', nome='PrezzoAlato%d' % k) for k in range(5)] + [props030.cartellino_alato(prc, M30, F30, testo='TASSE', mat='bianco', nome='TassaAlata%d' % k) for k in range(4)]
for a_ in ALATI: a_['root'].rotation_mode = 'XYZ'
CORI = []
for k in range(40):
    c_ = props028.box('Coriandolo%d' % k, (-0.07, -0.01, -0.05), (0.07, 0.01, 0.05), M30[('tenda_r', 'tenda_g', 'tenda_a', 'tenda_v', 'carta')[k % 5]], prc); c_.rotation_mode = 'XYZ'
    an = rnd.uniform(0, 6.28); CORI.append((c_, Vector((math.cos(an) * rnd.uniform(0.3, 2.6), -rnd.uniform(1.5, 5.0), rnd.uniform(3.0, 7.5))), rnd.uniform(0, 6.28), rnd.uniform(4, 11)))
# l'autostrada, la diga, le macchine, il supermercato
try: m_prato = bpy.data.objects['Prato'].material_slots[0].material
except Exception: m_prato = material('M30_prato', (0.25, 0.5, 0.15), rough=0.9)
props028.box('PratoAutostrada', (HX - 160, -160, -0.3), (HX + 160, 160, -0.02), m_prato, hwc)
ST = props030.strada(hwc, M30, 240.0, 10.0); ST.location = (HX, 0, 0)
DIGA = props030.diga(hwc, M30, 'D1', 10.0); DIGA['root'].location = DG
AUTO = []
for k, (aid, x, y) in enumerate((('sedan', -2.5, -10.0), ('taxi', 2.5, -12.0), ('suv', -2.4, -17.0), ('sedan', 2.6, -20.0), ('suv', 2.4, -27.5), ('taxi', -2.6, -25.5))):
    try: AUTO.append(A.modello('kenney/car-kit/' + aid, posizione=(HX + x, y, 0.03), altezza=2.1, rotazione=180.0, collezione=hwc, appoggia=True))
    except Exception as e: print('auto', aid, e)
SU = props030.supermercato(hwc, M30, F30); SU['root'].location = SUP; SU['tettoia'].rotation_mode = 'XYZ'
for c_ in SU['colonne']: c_.rotation_mode = 'XYZ'
MEGA = props030.megafono(chc, M30); TRONCHETTO = empty('Tronchetto', (0, 0, 0), None, chc); props030._tronco(chc, M30, 'TronchettoT', (-0.42, 0, 0), (0.42, 0, 0), 0.085, TRONCHETTO)
SCHEGGE = []
for k in range(14):
    s_ = props028.box('Scheggia%d' % k, (-0.06, -0.02, -0.02), (0.06, 0.02, 0.02), M30['taglio'], prc); s_.rotation_mode = 'XYZ'; SCHEGGE.append((s_, rnd.uniform(0, 6.28), rnd.uniform(1.5, 3.5), rnd.uniform(2.0, 4.0), rnd.random()))
# l'allagamento
ACQ = props030.acqua(flc, M30, 220.0, 0.0)
DIN = props030.canotto(flc, M30, 'K3'); DIN['root'].rotation_mode = 'XYZ'
SEGGIO = props030.seggio(flc, M30, F30); SEGGIO.rotation_mode = 'XYZ'
LOGC = empty('TroncoCastora', (0, 0, 0), None, flc); props030._tronco(flc, M30, 'TroncoCastoraT', (-0.9, 0, 0), (0.9, 0, 0), 0.34, LOGC); LOGC.rotation_mode = 'XYZ'
VOLANTI = []
for k in range(5):
    d_ = props030.canotto(flc, M30, 'K1', nome='CanottoBonus%d' % k); d_['root'].rotation_mode = 'XYZ'; an = -1.9 + 0.55 * k
    VOLANTI.append((d_['root'], Vector((6.5 + math.cos(an) * (5.5 + 1.5 * (k % 2)), -26.5 + math.sin(an) * 2.2 - 1.2 * (k % 3), WL)), rnd.uniform(-2, 2)))
SCHEDA = props028.box('SchedaVoto', (-0.16, -0.005, -0.11), (0.16, 0.005, 0.11), M30['bianco'], flc); SCHEDA.rotation_mode = 'XYZ'

# ======================= personaggi =======================
P = pippo.build_pippo(chc); Tb = tumbo.build_tumbo(chc, scale=0.75)
RO = rospina.rospina(chc, rospina.mats_rospina(), stile='D'); CA = castora.castora(chc, castora.mats_castora(), stile='A')
for r in (P['root'], Tb['root'], RO['root'], CA['root']): r.rotation_mode = 'XYZ'
for nm in 'LR': P['shoulder' + nm].rotation_mode = 'QUATERNION'
for nm in ('shoulderL', 'shoulderR', 'hipL', 'hipR', 'head'): RO[nm].rotation_mode = 'XYZ'; CA[nm].rotation_mode = 'XYZ'
PORT['root'].parent = P['body']; PORT['root'].location = (0, -0.62, 0.12); PORT['root'].rotation_euler = (0.5, 0, 0)
MEGA.parent = CA['head']; MEGA.location = (0.14, -0.36, -0.26)
TRONCHETTO.parent = CA['head']; TRONCHETTO.location = (0, -0.42, -0.25)
BAND = props030.bandiera_palestina(chc, M30); BAND['root'].parent = CA['root']; BAND['root'].location = (-0.78, 0.05, 0.0); BAND['telo'].rotation_mode = 'XYZ'   # la Castora se la porta dietro ovunque (richiesta dell'autore)
bpy.context.view_layer.update()
RH = RO['head'].matrix_world.translation.z; KH = CA['head'].matrix_world.translation.z; PZH = 1.78
print('ALTEZZE rospina', round(RH, 2), 'castora', round(KH, 2))

# ======================= visibilita' =======================
def desc(o):
    for c in o.children:
        yield c
        yield from desc(c)
NEVER = set()
def show(o, intervals):
    for q in [o] + list(desc(o)):
        if q.name in NEVER: continue
        first = bool(intervals) and intervals[0][0] <= 0.0
        q.hide_render = not first; q.keyframe_insert('hide_render', frame=1)
        for (a, b) in intervals:
            if a > 0.0: q.hide_render = False; q.keyframe_insert('hide_render', frame=fr(a))
            if b < TOTAL: q.hide_render = True; q.keyframe_insert('hide_render', frame=fr(b))
def show_only(o, intervals):
    show(o, intervals)
    for q in [o] + list(desc(o)): NEVER.add(q.name)
END = TOTAL + 1
show_only(TAG300, [(0.0, T_OGGI + 0.12)]); show_only(TAG2000, [(T_OGGI + 0.12, T_DIGA)]); show_only(TAG9000, [(T_ACQUA, END)])
show_only(SC['root'], [(0.0, T_DIGA), (T_ACQUA, END)])
show_only(NUV['root'], [(T_NO, T_TASSE)]); show_only(PORT['root'], [(T_NO, T_PREZZI)])
for a_ in ALATI[:5]: show_only(a_['root'], [(T_PREZZI, T_RISOLVE)])
for a_ in ALATI[5:]: show_only(a_['root'], [(T_TASSE - 0.2, T_RISOLVE)])
show_only(BUONO, [(T_BONUS + 0.3, T_MA)])
for (c_, *_) in CORI: show_only(c_, [(T_BENE, T_NO), (T_BONUS, T_BMONO + 0.6), (T_FESTA, T_DOM)])
for (o, R_, b_, ph) in GENTE: show_only(b_, [(T_BMONO, T_DIGA)]); show_only(o, [(0.0, T_DIGA)])
show_only(NEGO, [(0.0, T_DIGA)])
show_only(MEGA, [(T_CONTRO - 0.4, T_ROSI)]); show_only(TRONCHETTO, [(T_DIGA, T_AUTO), (T_PORCA, END)])
for (s_, *_) in SCHEGGE: show_only(s_, [(T_DIGA, T_AUTO), (T_ROSI, T_CROLLO + 0.3)])
show_only(SCHEDA, [(T_RESTA + 1.0, T_PORCA + 0.5)])
for (d_, *_) in VOLANTI: show_only(d_, [(T_BCAN + 0.15, END)])
for o in list(flc.objects):
    if o.parent is None and o.name not in NEVER: show_only(o, iv('FL'))
for o in list(hwc.objects):
    if o.parent is None and o.name not in NEVER: show(o, iv('HW'))
show_only(P['root'], [(0.0, T_DIGA), (T_VOTA - 0.05, END)])
show_only(Tb['root'], [(0.0, T_DIGA), (T_VOTA - 0.05, END)])
show_only(RO['root'], [(0.0, T_DIGA), (T_ACQUA, END)])
show_only(CA['root'], [(T_CAST - 0.05, T_ACQUA), (T_PORCA, END)])
for cu in bpy.data.curves:
    if cu.rna_type.identifier == 'TextCurve': cu.resolution_u = 4

# ======================= luci di scena =======================
def chiavi(owner, attr, valori):
    for (t_, v) in valori:
        setattr(owner, attr, v); owner.keyframe_insert(attr, frame=fr(t_))
def on_off(lights, intervals):
    for l_ in lights:
        e_ = l_.data.energy; keys = [(0.0, e_ if intervals[0][0] <= 0 else 0.0)]
        for (a, b) in intervals:
            if a > 0: keys += [(a, e_)]
            if b < TOTAL: keys += [(b, 0.0)]
        chiavi(l_.data, 'energy', sorted(keys))
LBAL = luci.cinema(prc, (6.4, -19.5, 6.0), (5.4, -24.0, 6.0), distanza=4.0, lato=1, forza=0.3, nome='CinemaBalcone', riempimento=0.6)
LPP = luci.cinema(prc, (-2.5, -25.0, 1.7), (-2.4, -28.5, 1.7), distanza=3.8, lato=-1, forza=0.25, nome='CinemaPippo', riempimento=0.6)
LNE = luci.cinema(prc, (-10.5, -22.0, 1.6), (-10.0, -25.5, 1.6), distanza=4.0, lato=1, forza=0.25, nome='CinemaNegozio', riempimento=0.6)
LHW = luci.cinema(prc, (HX - 1.5, -2.5, 1.8), (HX - 4.0, -7.5, 1.7), distanza=4.5, lato=1, forza=0.25, nome='CinemaDiga', riempimento=0.6)
LFL = luci.cinema(prc, (0.5, -24.8, 2.6), (1.0, -28.0, 2.8), distanza=4.0, lato=-1, forza=0.25, nome='CinemaCanotto', riempimento=0.6)
on_off(list(LBAL.values()), [(0.0, T_NO), (T_RISOLVE, T_BMONO), (T_FESTA, T_BCAN)]); on_off(list(LPP.values()), [(T_NO, T_IERI), (T_CAST, T_DIGA)])
on_off(list(LNE.values()), [(T_IERI, T_CAST)]); on_off(list(LHW.values()), [(T_DIGA, T_AUTO)]); on_off(list(LFL.values()), [(T_VOTA, T_PORCA), (T_DOM, END)])
LIGHTS = [SUN.data] + [l_.data for d_ in (LBAL, LPP, LNE, LHW, LFL) for l_ in d_.values()]

# ======================= pose =======================
def qdir(d, rest=(0, 0, -1)): return Vector(rest).rotation_difference(Vector(d).normalized())
def yaw_to(a, b): return math.atan2(b[0] - a[0], -(b[1] - a[1]))
def mixv(a, b, u): return tuple(Vector(a).lerp(Vector(b), u))
def braccia(nome, forza=1.0):
    b = pippo.EMOZIONI_FORTI[nome]['braccia']; return {'aL': tuple(Vector((0, 0, -1)).lerp(Vector(b[0]).normalized(), forza)), 'aR': tuple(Vector((0, 0, -1)).lerp(Vector(b[1]).normalized(), forza))}
GIU = dict(aL=(-0.08, 0, -1), aR=(0.08, 0, -1))
PORTA = dict(aL=(-0.28, -0.8, -0.52), aR=(0.28, -0.8, -0.52))
SU_ = dict(aL=(-0.35, -0.3, 0.9), aR=(0.35, -0.3, 0.9))
def arco(t, t0, d, h): return h * math.sin(PI * (t - t0) / d) if t0 <= t < t0 + d else 0.0
def wl(t): return (0.05 + (WL - 0.05) * sm(ramp(t, T_ACQUA, T_VOTA - 0.1))) if t >= T_ACQUA else -1.0
def canotto(t):
    """posizione, rotazione e dondolio del canotto a papera."""
    u = sm(ramp(t, T_VOTA, T_RESTA - 0.1)); p = D1.lerp(D2, u); yaw = yaw_to(D1, D2) * (1 - sm(ramp(t, T_RESTA - 0.8, T_RESTA))) + 0.0
    if t >= T_DOM - 0.6: yaw = 0.9 * sm(ramp(t, T_DOM - 0.6, T_DOM))
    return Vector((p.x, p.y, wl(t) - 0.06 + 0.04 * math.sin(t * 3.1))), yaw, 0.04 * math.sin(t * 2.3), 0.05 * math.sin(t * 2.9 + 1)

def pp(t):
    S_ = dict(loc=Vector((0, 0, -50)), yaw=0.0, lean=0.0, roll=0.0, bend=0.0, head=(0, 0, 0), hL=0.0, hR=0.0, **GIU)
    if t < T_NO:                                                         # sotto il balcone, in mezzo alla folla
        S_.update(loc=PS.copy(), yaw=yaw_to(PS, RB) , head=(-0.45, 0, 0))
    elif t < T_IERI:                                                     # in mezzo alla piazza
        S_.update(loc=PS2.copy(), yaw=0.0)
        if t < T_PREZZI: S_.update(head=(0.25, 0, 0), bend=0.12, **PORTA)                           # il portafoglio vuoto sotto la pioggia
        elif t < T_RISOLVE:                                              # salta per acchiappare i prezzi e le tasse che volano
            j = abs(math.sin((t - T_PREZZI) * 7.0)); S_.update(loc=PS2 + Vector((0, 0, 0.35 * j)), head=(-0.5, 0, 0), aL=(-0.3 - 0.2 * j, -0.2, 0.95), aR=(0.3, -0.2 - 0.3 * j, 0.95))
        elif t < T_BMONO: S_.update(head=(-0.4, 0, 0.5), yaw=0.35)                                   # guarda il balcone
        else:
            k = sm(ramp(t, T_BMONO + 0.2, T_BMONO + 0.9)); S_.update(head=(-0.4 + 0.5 * k, 0, 0), aL=mixv((-0.3, -0.3, 0.9), (-0.3, -0.85, -0.2), k), aR=mixv((0.3, -0.3, 0.9), (0.3, -0.85, -0.2), k))
    elif t < T_CAST:                                                     # al negozio
        S_.update(loc=PSH.copy(), yaw=yaw_to(PSH, MONO), head=(0.1, 0, 0), aL=(-0.3, -0.85, -0.2), aR=(0.3, -0.85, -0.2))
        if t >= T_OGGI: S_.update(**braccia('spaventato', ramp(t, T_OGGI + 0.15, T_OGGI + 0.4)))
        if t >= T_GRAZIE: S_.update(yaw=0.15, head=(0, 0, 0), aL=(-0.3, 0.0, -0.95), aR=(0.3, -0.6, -0.7))
        if t >= T_MA: S_.update(yaw=0.15 + 0.6 * sm(ramp(t, T_MA + 0.2, T_MA + 0.8)), head=(-0.15, 0, -0.2), **braccia('felice', ramp(t, T_MA + 0.6, T_MA + 1.0)))
    elif t < T_DIGA:                                                     # guarda la Castora
        S_.update(loc=CS + Vector((3.3, -0.8, 0)), yaw=-1.0, head=(0, 0, 0.1))
    elif t >= T_VOTA - 0.1:                                              # nel canotto
        c_, yw, pi_, ro_ = canotto(t); d_ = Vector((-math.sin(yw) * 0.35, math.cos(yw) * 0.35, 0))
        row = math.sin((t - T_VOTA) * 7.0) * (1 - ramp(t, T_RESTA - 0.5, T_RESTA - 0.1))
        S_.update(loc=c_ + d_ + Vector((0, 0, -0.72)), yaw=yw, lean=pi_, roll=ro_, aL=(-0.5, -0.5 + 0.3 * row, -0.5), aR=(0.5, -0.5 - 0.3 * row, -0.5), bend=0.1 * row)
        if t >= T_RESTA - 0.1:                                           # «Rospina, resta altri cento anni!»: mani a megafono verso il balcone
            S_.update(yaw=yw + 0.75 * sm(ramp(t, T_RESTA - 0.1, T_RESTA + 0.2)), head=(-0.35, 0, 0), aL=(-0.2, -0.6, 0.65), aR=(0.2, -0.6, 0.65), bend=-0.1)
        if t >= T_PORCA: S_.update(**SU_)
        if t >= T_FESTA: S_.update(yaw=yw + 0.75, head=(-0.4, 0, 0), **GIU)
        if t >= T_BCAN: S_.update(yaw=yw + 0.4, head=(-0.3, 0, 0.3), **braccia('spaventato', ramp(t, T_BCAN + 0.3, T_BCAN + 0.6)))
        if t >= T_DOM:
            k = sm(ramp(t, T_DOM, T_DOM + 0.3)); S_.update(yaw=yw, head=(-0.05, 0, 0.55 * math.sin((t - T_DOM) * 4.2)), aL=mixv((-0.08, 0, -1), (-0.9, -0.25, 0.25), k), aR=mixv((0.08, 0, -1), (0.9, -0.25, 0.25), k))
    return S_

def tp(t):
    S_ = dict(loc=Vector((0, 0, -50)), yaw=0.0, head=(0, 0, 0), tail=(-1.0 + 0.5 * math.sin(t * 20), 0, 0), pitch=0.0, roll=0.0)
    if t < T_NO: S_.update(loc=PS + Vector((1.1, 0.2, 0)), yaw=yaw_to(PS, RB), head=(-0.5, 0, 0))
    elif t < T_IERI: S_.update(loc=PS2 + Vector((1.25, 0.3, 0)), yaw=-0.5, head=(-0.35, 0, 0.4), tail=(-1.0 + 0.2 * math.sin(t * 6), 0, 0))
    elif t < T_CAST: S_.update(loc=PSH + Vector((1.2, 0.3, 0)), yaw=-0.7, head=(-0.2, 0, 0.3))
    elif t < T_DIGA: S_.update(loc=CS + Vector((2.3, -1.4, 0)), yaw=-1.1, head=(-0.3, 0, 0))
    elif t >= T_VOTA - 0.1:
        c_, yw, pi_, ro_ = canotto(t); d_ = Vector((math.sin(yw) * 0.62, -math.cos(yw) * 0.62, 0))
        S_.update(loc=c_ + d_ + Vector((0, 0, 0.14)), yaw=yw, pitch=pi_, roll=ro_, head=(-0.25, 0, 0.3 * math.sin(t * 2.0)))
        if t >= T_PORCA: S_.update(head=(-0.7, 0, 0))                                                # ulula anche lui
        if t >= T_DOM: S_.update(head=(-0.15, 0, -0.5 * math.sin((t - T_DOM) * 4.2)))
    return S_

def rp(t):
    """Rospina sta sempre sul balcone."""
    w = math.sin(t * 9.0)
    S_ = dict(loc=RB.copy(), yaw=0.0, lean=0.0, head=(0.12, 0, 0), sL=(0, 0.12, 0), sR=(-2.7, 0.3 * w, 0.2), hL=0.0, hR=0.0, f=dict(rospina.EMOZIONI['importantissima']))     # saluta la folla
    if t >= T_BENE: S_.update(sR=(-2.9, 0, 0.15), sL=(-2.9, 0, -0.15), head=(-0.1, 0, 0), loc=RB + Vector((0, 0, 0.12 * abs(math.sin((t - T_BENE) * 8)))), f=dict(rospina.EMOZIONI['trionfo'], mouth=0.4 + 0.5 * abs(math.sin(t * 12))))
    if t >= T_RISOLVE:                                                   # al cannone: lo accarezza, poi tira la corda
        k = sm(ramp(t, T_BONUS - 0.35, T_BONUS)); S_.update(loc=RB + Vector((0.9, 0.05, 0)), yaw=-0.4, head=(0, 0, 0.2), sR=(-0.3, -1.4 - 0.8 * k, 0), sL=(-0.4, 0.2, 0), f=dict(rospina.EMOZIONI['falsa modestia']))
        if t >= T_BONUS: S_.update(f=dict(rospina.EMOZIONI['trionfo']), loc=RB + Vector((0.9, 0.05 + 0.25 * (1 - ramp(t, T_BONUS, T_BONUS + 0.4)), 0)))
    if t >= T_ACQUA: S_.update(loc=RB.copy(), yaw=0.0, head=(0.3, 0, -0.3), sR=(0, -0.12, 0), sL=(0, 0.12, 0), f=dict(rospina.EMOZIONI['importantissima']))
    if t >= T_RESTA: S_.update(head=(0.3, 0, -0.45), sR=(-1.2, -0.4, 0), f=dict(rospina.EMOZIONI['falsa modestia']))        # «chi, io?»
    if t >= T_FESTA:
        j = abs(math.sin((t - T_FESTA) * 8.0)); S_.update(loc=RB + Vector((0, 0, 0.2 * j)), head=(-0.15, 0, 0), sR=(-2.9, 0, 0.3), sL=(-2.9, 0, -0.3), f=dict(rospina.EMOZIONI['trionfo']))
    if t >= T_BCAN - 0.3: S_.update(loc=RB + Vector((0.9, 0.05, 0)), yaw=-0.4, head=(0, 0, 0.2), sR=(-0.3, -2.2, 0), sL=(-0.4, 0.2, 0), f=dict(rospina.EMOZIONI['trionfo']))
    if t >= T_DOM: S_.update(loc=RB + Vector((-0.9, 0, 0)), yaw=0.0, head=(0.25, 0, -0.3), sR=(-2.7, 0.3 * w, 0.2), sL=(0, 0.12, 0), f=dict(rospina.EMOZIONI['importantissima']))
    return S_

def cp_(t):
    """la Castora: eroina in piazza, poi la diga, il megafono, le colonne, e nel finale sul tronco."""
    E = castora.EMOZIONI; chew = abs(math.sin(t * 26.0))
    S_ = dict(loc=CS.copy(), yaw=0.15, lean=0.0, head=(-0.08, 0, 0), sL=(0, 0.75, 0), sR=(0, -0.75, 0), hL=0.0, hR=0.0, f=dict(E['trionfo'], mouth=0.3))                      # mani sui fianchi
    if t >= T_ALLORA: S_.update(sR=(-2.8 * sm(ramp(t, T_ALLORA + 0.2, T_ALLORA + 0.5)), 0, 0.15), sL=(0, 0.2, 0), head=(-0.05, 0, 0.1), f=dict(E['saputella']))
    if t >= T_DIGA:                                                      # rosicchia un tronchetto: la diga le cresce alle spalle
        S_.update(loc=CD + Vector((0, 0, 0.03)), yaw=0.35, lean=0.12, head=(0.12 + 0.07 * chew, 0, 0), sL=(-1.5, -0.25, 0), sR=(-1.5, 0.25, 0), f=dict(E['rosicchia'], mouth=0.2 + 0.4 * chew))
    if t >= T_AUTO:                                                      # in cima alla diga
        j = abs(math.sin((t - T_AUTO) * 8.0)) * (1 - ramp(t, T_CONTRO - 0.4, T_CONTRO - 0.2))
        S_.update(loc=DG + Vector((0, 0.0, DIGA['cima'] + 0.05 + 0.2 * j)), yaw=0.0, lean=0.0, head=(-0.1, 0, 0), sL=(-2.9, 0, -0.3), sR=(-2.9, 0, 0.3), f=dict(E['trionfo']))
    if t >= T_CONTRO - 0.3:                                              # il megafono
        b = abs(math.sin((t - T_CONTRO) * 13.0)); S_.update(yaw=0.8, sR=(-2.2, 0, 0.35), sL=(-2.6, 0.5, 0), head=(-0.1 + 0.05 * b, 0, 0), lean=-0.08, f=dict(E['predica'], mouth=0.4 + 0.6 * b))
    if t >= T_ROSI:                                                      # rosicchia la colonna del supermercato
        S_.update(loc=COL + Vector((-1.0, 0, 0.03)), yaw=PI / 2, lean=0.16, head=(0.15 + 0.08 * chew, 0, 0), sL=(-1.2, -0.3, 0), sR=(-1.2, 0.3, 0), f=dict(E['rosicchia'], mouth=0.2 + 0.4 * chew))
    if t >= T_CROLLO - 0.15:                                             # si gira soddisfatta mentre crolla tutto
        k = sm(ramp(t, T_CROLLO - 0.15, T_CROLLO + 0.25)); S_.update(loc=(COL + Vector((-1.0, 0, 0.03))).lerp(COL + Vector((-2.2, -3.2, 0.03)), k), yaw=PI / 2 - 1.2 * k, lean=0.0, head=(-0.1, 0, 0), sL=(0, 0.75, 0), sR=(0, -0.75, 0), f=dict(E['trionfo']))
    if t >= T_PORCA:                                                 # nel finale: sul tronco che galleggia, rosicchia un rametto
        S_.update(loc=CLG + Vector((0, 0, wl(t) + 0.3 + 0.04 * math.sin(t * 2.7))), yaw=0.35, lean=0.03 * math.sin(t * 2.2), head=(0.05 + 0.05 * chew, 0, 0.0), sL=(-1.5, -0.25, 0), sR=(-1.5, 0.25, 0), f=dict(E['rosicchia'], mouth=0.2 + 0.4 * chew))
        if t >= T_DOM + 0.5: S_.update(sR=(-2.8, 0, 0.2), f=dict(E['trionfo']))
    return S_

# ======================= chiavi =======================
def K(o, f, loc=None, rot=None, scale=None):
    if loc is not None: o.location = loc; o.keyframe_insert('location', frame=f)
    if rot is not None: o.rotation_euler = rot; o.keyframe_insert('rotation_euler', frame=f)
    if scale is not None: o.scale = scale if isinstance(scale, (tuple, list)) else (scale,) * 3; o.keyframe_insert('scale', frame=f)
def Q(o, f, d): o.rotation_quaternion = qdir(d); o.keyframe_insert('rotation_quaternion', frame=f)
def tra(t, a, b): return a <= t < b
# i pezzi della diga compaiono uno dopo l'altro
PEZZI = list(DIGA['root'].children); PEZZI.sort(key=lambda o: o.location.z)
PEZ0 = [(o, o.scale.copy()) for o in PEZZI]
for k, (o, s0) in enumerate(PEZ0):
    ta = T_DIGA + 0.1 + (T_AUTO - 0.25 - T_DIGA) * k / max(1, len(PEZ0) - 1)
    o.scale = (0.001,) * 3; o.keyframe_insert('scale', frame=1); o.keyframe_insert('scale', frame=fr(ta)); o.scale = s0 * 1.25; o.keyframe_insert('scale', frame=fr(ta) + 2); o.scale = s0; o.keyframe_insert('scale', frame=fr(ta) + 4)
def cori(t, t0, origine, giu=False):
    """posizioni dei coriandoli t - t0 secondi dopo lo scoppio."""
    out = []; dt = t - t0
    for (c_, v, ph, w) in CORI:
        if giu: p = origine + Vector((v.x * 1.2, v.y * 0.25 + 1.0, 2.5 + (v.z - 5) * 0.3 - 1.1 * dt + 0.2 * math.sin(dt * 3 + ph)))
        else: p = origine + Vector((v.x * dt, v.y * dt, v.z * dt - 4.0 * dt * dt)) if dt >= 0 else Vector((0, 0, -60))
        out.append((c_, p, (w * dt + ph, w * 0.7 * dt, ph)))
    return out
MUZ = CNB + Vector((0, -1.3, 0.75 + 1.3))                                # la bocca del cannone (alzo 0,8)
for f in range(1, NF + 1):
    t = (f - 1) / FPS
    s = pp(t)
    K(P['root'], f, tuple(s['loc']), (s['lean'], s['roll'], s['yaw'])); K(P['body'], f, rot=(s['bend'], 0, 0)); K(P['head'], f, rot=s['head'])
    for nm, k_ in (('L', 'aL'), ('R', 'aR')): Q(P['shoulder' + nm], f, s[k_])
    for nm, k_ in (('L', 'hL'), ('R', 'hR')): K(P['hip' + nm], f, rot=(s[k_], 0, 0))
    s = tp(t); K(Tb['root'], f, tuple(s['loc']), (s['pitch'], s['roll'], s['yaw']), 0.75); K(Tb['head'], f, rot=s['head']); K(Tb['tail'], f, rot=s['tail'])
    if t < T_DIGA + 0.1 or t >= T_ACQUA - 0.1:
        s = rp(t)
        K(RO['root'], f, tuple(s['loc']), (s['lean'], 0, s['yaw'])); K(RO['head'], f, rot=s['head'])
        for nm in 'LR': K(RO['shoulder' + nm], f, rot=s['s' + nm]); K(RO['hip' + nm], f, rot=(s['h' + nm], 0, 0))
        rospina.rex(RO, f, **s['f'])
    if t >= T_CAST - 0.2:
        s = cp_(t)
        K(CA['root'], f, tuple(s['loc']), (s['lean'], 0, s['yaw'])); K(CA['head'], f, rot=s['head'])
        for nm in 'LR': K(CA['shoulder' + nm], f, rot=s['s' + nm]); K(CA['hip' + nm], f, rot=(s['h' + nm], 0, 0))
        castora.cex(CA, f, **s['f']); K(BAND['telo'], f, rot=(0, 0.04 * math.sin(t * 7.0), PI + 0.14 * math.sin(t * 5.0)))
    # il cannone: alzo, rinculo
    rin = 0.35 * max(0.0, 1 - (t - T_BONUS) / 0.35) if t >= T_BONUS else 0.0
    if t >= T_BCAN: rin = 0.35 * max(0.0, 1 - (t - T_BCAN) / 0.35)
    K(CAN['root'], f, tuple(CNB + Vector((0, rin, 0)))); K(CAN['canna'], f, rot=(0.8 - 0.25 * rin / 0.35, 0, 0), scale=1.0 + 0.5 * rin)
    # coriandoli: piovono su «benissimo», scoppiano dal cannone su «bonus», piovono quando Rospina festeggia
    if tra(t, T_BENE, T_NO): L_ = cori(t, T_BENE, RB + Vector((0, 0, 3.0)), giu=True)
    elif tra(t, T_BONUS, T_BMONO + 0.6): L_ = cori(t, T_BONUS, MUZ)
    elif tra(t, T_FESTA, T_DOM): L_ = cori(t, T_FESTA, RB + Vector((0, 0, 3.2)), giu=True)
    else: L_ = []
    for (c_, p, r_) in L_: K(c_, f, tuple(p), r_)
    # la nuvoletta personale di Pippo e la mosca del portafoglio
    if tra(t, T_NO - 0.1, T_RISOLVE + 0.1):
        K(NUV['root'], f, tuple(PS2 + Vector((0.05 * math.sin(t * 2), 0.1, 3.35 + 0.05 * math.sin(t * 3)))))
        for (g, x, y, ph) in NUV['gocce']: K(g, f, (x, y, -0.4 - ((t * 1.9 + ph) % 1.0) * 1.3))
        K(PORT['mosca'], f, (0.15 * math.sin(t * 9), 0.1 * math.cos(t * 7), 0.4 + 0.1 * math.sin(t * 13)))
    # i prezzi e le tasse che volano
    if tra(t, T_PREZZI - 0.25, T_RISOLVE + 0.1):
        for k, a_ in enumerate(ALATI):
            tassa = k >= 5; t0 = (T_TASSE - 0.15 + 0.07 * (k - 5)) if tassa else (T_PREZZI + 0.06 * k); dt = max(0.0, t - t0); an = k * 1.4 + 0.5
            p = PS2 + Vector((math.cos(an) * (0.9 + 0.35 * dt), math.sin(an) * 0.5 - 0.3, 1.5 + 0.25 * (k % 3) + (3.4 if tassa else 2.2) * dt + 0.15 * math.sin(t * 9 + k)))
            K(a_['root'], f, tuple(p), (0.15 * math.sin(t * 6 + k), 0.2 * math.sin(t * 5 + k), 0.2 * math.sin(t * 4 + k)))
            for sx, al in zip((-1, 1), a_['ali']): K(al, f, rot=(0, sx * 0.9 * math.sin(t * 26 + k), 0))
    # il buono: esce dal cannone, scende a zig zag nelle mani di Pippo, poi lo porta al negozio
    if tra(t, T_BONUS + 0.2, T_MA + 0.1):
        mano = PS2 + Vector((0.0, -0.62, 1.42))
        if t < T_BMONO + 0.9:
            u = sm(ramp(t, T_BMONO - 0.1, T_BMONO + 0.9)); p = Vector((mano.x + 1.2 * (1 - u) * math.sin(u * 9), mano.y, mano.z + 4.2 * (1 - u))); K(BUONO, f, tuple(p), (0.25 * (1 - u) * math.sin(u * 11), 0, 0.3 * (1 - u) * math.sin(u * 9)), 1.0)
        elif t < T_IERI: K(BUONO, f, tuple(mano), (-0.12, 0, 0), 1.0)
        else:
            yw = yaw_to(PSH, MONO) if t < T_GRAZIE else 0.15; d_ = Vector((math.sin(yw), -math.cos(yw), 0))
            giu_ = ramp(t, T_GRAZIE, T_GRAZIE + 0.25); K(BUONO, f, tuple(PSH + d_ * 0.62 + Vector((0.3 * giu_, 0, 1.42 - 0.75 * giu_))), (-0.12 - 1.2 * giu_, 0, yw), 1.0 - 0.3 * giu_)
    # il monopattino e i cartelli del prezzo
    if t < T_DIGA + 0.1:
        K(SC['root'], f, tuple(MONO), (0, 0, 1.05 + 0.5 * (t - T_IERI) * (1 if tra(t, T_IERI, T_GRAZIE) else 0)), scale=1.3)
        gira = PI * ramp(t, T_OGGI, T_OGGI + 0.12)
        K(TAG300, f, tuple(TAG), (0, 0, -0.1 + gira)); K(TAG2000, f, tuple(TAG), (0, 0, -0.1 + gira + PI), scale=1.0 + 0.35 * (1 - ramp(t, T_OGGI + 0.12, T_OGGI + 0.3)) if t >= T_OGGI + 0.12 else 1.0)
    else:                                                                # nell'allagamento galleggia via col cartello «9.000 €»
        u = ramp(t, T_ACQUA, END); p = Vector((-13.0, -22.0, 0)).lerp(Vector((-3.0, -29.0, 0)), u)
        K(SC['root'], f, (p.x, p.y, wl(t) - 0.1 + 0.04 * math.sin(t * 3)), (0.15 * math.sin(t * 2), 1.2, 0.8 + 0.3 * t)); K(TAG9000, f, (p.x + 0.5, p.y - 0.3, wl(t) - 0.55 + 0.04 * math.sin(t * 3 + 1)), (0.08 * math.sin(t * 2.4), 0.12, 0.2 * math.sin(t * 0.7)))
    # la gente: sotto il balcone ad applaudire, poi in fila al negozio col buono alzato
    for k, (o, R_, b_, ph) in enumerate(GENTE):
        if t < T_IERI:
            K(o, f, (FOLLA[k][0], FOLLA[k][1], 0.03 + 0.06 * abs(math.sin(t * 6 + ph)) * (1 if (t < T_NO or t >= T_BMONO) else 0)), (0, 0, yaw_to(FOLLA[k], RB)))
            cl = math.sin(t * 16 + ph) * (1 if t < T_NO else 0)
            if t < T_BMONO: Q(R_['shoulderR'], f, (0.25 - 0.2 * cl, -0.6, 0.55)); Q(R_['shoulderL'], f, (-0.25 + 0.2 * cl, -0.6, 0.55))
            else: Q(R_['shoulderR'], f, (0.25 + 0.2 * math.sin(t * 9 + ph), -0.3, 0.92)); Q(R_['shoulderL'], f, (-0.1, 0, -1))
        else:
            K(o, f, (FILA[k][0], FILA[k][1], 0.03 + 0.08 * abs(math.sin(t * 7 + ph))), (0, 0, yaw_to(FILA[k], (NEG.x + 2.2, NEG.y)) + 0.25 * math.sin(k)))
            Q(R_['shoulderR'], f, (0.25 + 0.2 * math.sin(t * 9 + ph), -0.3, 0.92)); Q(R_['shoulderL'], f, (-0.1, 0, -1))
    k_ = ramp(t, T_GRAZIE, T_GRAZIE + 0.3); fr_ = math.sin(t * 14)                                   # il negoziante si frega le mani
    Q(NR['shoulderR'], f, mixv((0.1, 0, -1), (-0.25 + 0.06 * fr_, -0.75, 0.1), k_)); Q(NR['shoulderL'], f, mixv((-0.1, 0, -1), (0.25 - 0.06 * fr_, -0.75, 0.1), k_))
    # schegge: quando la Castora rosicchia
    for (s_, an, v, vz, ph) in SCHEGGE:
        if tra(t, T_DIGA, T_AUTO): base = CD + Vector((0.15, -0.5, 1.55)); dt = ((t - T_DIGA) * 2.2 + ph) % 1.0
        elif tra(t, T_ROSI, T_CROLLO + 0.3): base = COL + Vector((-0.4, -0.2, 1.6)); dt = ((t - T_ROSI) * 2.2 + ph) % 1.0
        else: continue
        K(s_, f, tuple(base + Vector((math.cos(an) * v * dt * 0.5, -abs(math.sin(an)) * v * dt * 0.5, vz * dt - 4.5 * dt * dt))), (t * 9 + an, t * 7, an))
    # la colonna rosicchiata cede, la tettoia crolla
    if tra(t, T_ROSI - 0.1, T_ACQUA + 0.1):
        c2 = SU['colonne'][1]; k = sm(ramp(t, T_CROLLO - 0.3, T_CROLLO)); K(c2, f, rot=(0.0, 1.35 * k, 0)); c2.scale = (1, 1, 1);
        kk = ramp(t, T_CROLLO, T_CROLLO + 0.35); bz = 0.06 * math.sin(max(0.0, t - T_CROLLO - 0.35) * 30) * max(0.0, 1 - (t - T_CROLLO - 0.35) / 0.3) if t > T_CROLLO + 0.35 else 0.0
        K(SU['tettoia'], f, rot=(0.62 * kk * kk + bz, 0.12 * kk, 0))
        for j in (0, 2, 3): K(SU['colonne'][j], f, rot=(0.9 * kk * (1 if j != 3 else 0.6), 0.25 * kk * (j - 1.5), 0))
    # l'acqua, il canotto, il seggio, il tronco, la scheda
    if t >= T_ACQUA - 0.1:
        K(ACQ, f, (0, 0, wl(t)))
        c_, yw, pi_, ro_ = canotto(t); K(DIN['root'], f, tuple(c_), (pi_, ro_, yw))
        row = math.sin((t - T_VOTA) * 7.0) * (1 - ramp(t, T_RESTA - 0.5, T_RESTA - 0.1))
        for sx, r_ in zip((-1, 1), DIN['remi']): K(r_, f, rot=(0.5 * row, sx * (0.45 + 0.2 * abs(row)), 0.5 * row * sx))
        K(SEGGIO, f, (SEG.x, SEG.y, wl(t) + 0.03 * math.sin(t * 2.6 + 1)), (0.03 * math.sin(t * 2.1), 0.03 * math.sin(t * 1.7), -0.25))
        K(LOGC, f, (CLG.x, CLG.y, wl(t) + 0.03 * math.sin(t * 2.7)), (0, 0, 0.35))
        u = ramp(t, T_RESTA + 1.0, T_RESTA + 1.5); a_ = Vector((D2.x + 0.4, D2.y + 0.2, wl(t) + 1.6)); b_ = Vector((SEG.x, SEG.y, wl(t) + 1.0)); p = a_.lerp(b_, u); p.z += 0.7 * math.sin(PI * u)
        K(SCHEDA, f, tuple(p), (PI / 2 * u, 0, 0.6), scale=(0.32, 0.01, 0.22) if u < 1 else (0.001, 0.001, 0.001))
        for k, (d_, arrivo, sp) in enumerate(VOLANTI):                    # il bonus canotto: escono dal cannone e ammarano
            t0 = T_BCAN + 0.15 + 0.12 * k; u = ramp(t, t0, t0 + 0.9); p = MUZ.lerp(arrivo, u); p.z += 5.5 * math.sin(PI * u) * (1 - 0.0);
            if u >= 1: p.z = wl(t) - 0.05 + 0.05 * math.sin(t * 3 + k) + 0.25 * math.sin(min(1.0, (t - t0 - 0.9) / 0.3) * PI) * 0
            K(d_, f, tuple(p), (sp * 3 * (1 - u), sp * 2 * (1 - u), k * 1.1), scale=0.2 + 0.5 * u)

# ======================= espressioni di Pippo e Tumbo =======================
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
        g.scale = (1, 1, 1) if (k in ex_ and forza > 0.3) else (0.001,) * 3; g.keyframe_insert('scale', frame=f)
def emo(t, nome, forza=1.0, **extra):
    if _emo_last[0] and t - 0.06 > _emo_last[0][2]: _emo_key(fr(t - 0.06), _emo_last[0][0], _emo_last[0][1], _emo_last[0][3])
    _emo_key(fr(t), nome, forza, extra); _emo_last[0] = (nome, forza, t, extra)
def tex(t, **k): _ex('t', lambda f, **kk: tumbo.tumbo_express(Tb, f, **kk), t, k)
emo(0.0, 'normale', 1.0); emo(T_NO, 'triste', 1.0); emo(T_PREZZI, 'spaventato', 0.8); emo(T_RISOLVE, 'sorpreso', 0.6); emo(T_BMONO + 0.5, 'felice', 1.0)
emo(T_IERI, 'felice', 0.8); emo(T_OGGI + 0.12, 'spaventato', 1.0); emo(T_GRAZIE, 'arrabbiato', 1.0); emo(T_MA + 0.3, 'felice', 0.8); emo(T_CAST, 'sorpreso', 0.7)
emo(T_VOTA - 0.1, 'triste', 0.6); emo(T_RESTA, 'spaventato', 0.9, mouth_open=1.0); emo(T_FESTA, 'triste', 0.8); emo(T_BCAN + 0.3, 'spaventato', 1.0); emo(T_DOM, 'sorpreso', 0.5, mouth_open=0.3)
tex(0.0, tongue=0.4, brow=0.0); tex(T_NO, tongue=0.0, brow=-0.4); tex(T_BMONO + 0.5, tongue=0.7, brow=0.2); tex(T_OGGI + 0.12, tongue=0.0, brow=-0.5); tex(T_VOTA, tongue=0.0, brow=-0.4); tex(T_DOM, tongue=0.5, brow=0.0)

# ======================= effetti =======================
def fx(name, pos, w, t0, dur, **k):
    try: return A.effetto(name, posizione=tuple(pos), larghezza=w, animazione=(fr(t0), int(dur * FPS)), collezione=prc, **k)
    except Exception as e: print('effetto', name, e)
fx('emoticon/hearts', RB + Vector((0.9, -0.4, RH + 0.7)), 0.5, T_BENE + 0.2, 1.2)
fx('emoticon/drops', PS2 + Vector((0.5, -0.3, 2.3)), 0.4, T_MALE, 0.8)
fx('emoticon/cash', PS2 + Vector((0.6, -0.4, 2.6)), 0.5, T_500, 1.0)
fx('emoticon/exclamations', PSH + Vector((0.4, -0.3, 2.5)), 0.5, T_2000, 0.7)
fx('emoticon/anger', PSH + Vector((0.45, -0.3, 2.45)), 0.5, T_GRAZIE + 0.1, 1.0)
fx('emoticon/idea', CS + Vector((0.5, -0.2, KH + 0.75)), 0.5, T_LOGICA - 0.2, 0.6)
for k, au in enumerate(AUTO[:3]): fx('emoticon/anger', Vector(au.location) + Vector((0, 0, 2.6)), 0.7, T_AUTO + 0.2 + 0.25 * k, 0.9)
fx('emoticon/exclamations', D2 + Vector((0.5, 0.2, WL + 2.6)), 0.5, T_PORCA, 0.8)
fx('emoticon/stars', RB + Vector((-0.8, -0.4, RH + 0.75)), 0.5, T_FESTA + 0.2, 1.0)
fx('emoticon/question', D2 + Vector((0.0, 0.2, WL + 2.75)), 0.6, T_DOM + 0.1, 1.6)
for k in range(6):
    try: fx('sbuffo_bianco/whitepuff%02d' % (k * 3), COL + Vector((rnd.uniform(-3, 5), -0.6, rnd.uniform(0.6, 3.0))), rnd.uniform(2.0, 3.5), T_CROLLO + 0.3 + 0.03 * k, 0.9, opacita=0.8)
    except Exception: pass

# ======================= camera =======================
SHOTS = [  # t0, t1, camera da, a, mira da, a, lente, diaframma, pugno, mano
    (0.0, T_BENE, (1.0, -32.6, 1.5), (1.7, -30.8, 2.2), (6.3, -19.6, 4.6), (6.2, -19.6, 5.3), 24, 8.0, 1.0, 0.8),                                      # 01 da cinque anni comanda Rospina
    (T_BENE, T_NO, (5.0, -24.2, 6.3), (5.2, -23.6, 6.3), (6.0, -19.5, 4.3 + RH), (6.0, -19.5, 4.3 + RH), 40, 4.5, 1.0, 0.8),                             # 02 e va tutto benissimo
    (T_NO, T_MALE, (-2.2, -29.2, 1.8), (-2.2, -29.0, 1.8), (-2.5, -25.0, 1.9), (-2.5, -25.0, 1.9), 30, 5.0, 1.0, 0.7),                                # 03 no
    (T_MALE, T_PREZZI, (-2.3, -27.6, 1.75), (-2.3, -27.3, 1.75), (-2.5, -25.0, PZH - 0.05), (-2.5, -25.0, PZH - 0.05), 42, 3.5, 1.25, 0.7),            # 04 va tutto male
    (T_PREZZI, T_TASSE, (-1.6, -29.4, 1.0), (-1.7, -29.0, 1.0), (-2.5, -25.0, 2.5), (-2.5, -25.0, 3.3), 26, 7.0, 1.0, 1.0),                            # 05 i prezzi volano
    (T_TASSE, T_RISOLVE, (-2.1, -26.9, 0.8), (-2.1, -26.8, 0.8), (-2.5, -25.0, 4.6), (-2.5, -25.0, 5.6), 22, 9.0, 1.0, 1.0),                           # 06 le tasse pure (dall'alto)
    (T_RISOLVE, T_BMONO, (2.4, -24.2, 5.7), (2.7, -23.9, 5.8), (7.4, -19.7, 5.8), (7.4, -19.8, 5.95), 30, 6.0, 1.0, 1.0),                             # 07 Rospina risolve tutto con un bonus
    (T_BMONO, T_500, (-5.0, -28.2, 1.6), (-4.8, -27.9, 1.6), (-2.5, -25.2, 3.0), (-2.5, -25.2, 1.75), 30, 6.0, 1.0, 0.8),                              # 08 bonus monopattino
    (T_500, T_IERI, (-2.35, -27.2, 1.5), (-2.35, -27.0, 1.5), (-2.5, -25.62, 1.46), (-2.5, -25.62, 1.46), 45, 4.5, 1.3, 0.8),                          # 09 cinquecento euro
    (T_IERI, T_OGGI, (-11.2, -25.6, 1.5), (-11.4, -24.9, 1.45), (-11.9, -20.6, 1.0), (-11.9, -20.6, 1.0), 32, 5.6, 1.0, 0.7),                          # 10 ieri costava trecento
    (T_OGGI, T_GRAZIE, (-11.2, -23.6, 1.3), (-11.2, -23.5, 1.3), (-11.3, -21.0, 1.25), (-11.3, -21.0, 1.25), 36, 5.6, 1.35, 1.2),                      # 11 oggi duemila
    (T_GRAZIE, T_TUTTI, (-9.8, -25.0, 1.75), (-9.8, -24.7, 1.75), (-10.0, -22.6, PZH), (-10.0, -22.6, PZH), 42, 3.5, 1.0, 0.6),                        # 12 e grazie al cazzo
    (T_TUTTI, T_MA, (-2.8, -31.6, 4.8), (-3.1, -31.2, 4.6), (-8.3, -24.5, 1.3), (-8.3, -24.5, 1.3), 24, 8.0, 1.0, 0.9),                                # 13 il bonus ce l'hanno tutti
    (T_MA, T_CAST, (-8.6, -25.4, 1.7), (-8.9, -25.0, 1.72), (-10.0, -22.6, PZH - 0.05), (-10.0, -22.6, PZH - 0.05), 40, 3.5, 1.0, 0.6),                # 14 ma per fortuna c'e' l'opposizione
    (T_CAST, T_ALLORA, (-4.9, -26.9, 0.55), (-4.8, -26.7, 0.6), (-4.2, -24.0, 1.45), (-4.2, -24.0, 1.5), 26, 7.0, 1.25, 0.9),                          # 15 la Castora
    (T_ALLORA, T_DIGA, (-3.7, -26.5, KH - 0.1), (-3.75, -26.2, KH - 0.08), (-4.15, -24.0, KH + 0.02), (-4.15, -24.0, KH + 0.02), 45, 4.0, 1.0, 0.6),   # 16 la cosa piu' logica
    (T_DIGA, T_AUTO, (HX - 4.4, -7.4, 1.6), (HX - 4.1, -6.9, 1.7), (HX - 1.9, -2.0, 1.6), (HX - 1.6, -1.6, 1.9), 28, 7.0, 1.0, 1.0),                   # 17 costruisce una diga
    (T_AUTO, T_CONTRO, (HX + 7.5, -27.0, 7.0), (HX + 7.0, -25.5, 6.6), (HX, -5.0, 1.8), (HX, -4.5, 2.0), 26, 9.0, 1.0, 0.9),                           # 18 in autostrada
    (T_CONTRO, T_ROSI, (HX - 2.2, -6.2, 3.2), (HX - 2.1, -5.9, 3.3), (HX + 0.1, 0.0, 3.3 + KH - 0.1), (HX + 0.1, 0.0, 3.3 + KH - 0.1), 35, 6.0, 1.0, 0.9),   # 19 contro i prezzi alti
    (T_ROSI, T_CROLLO - 0.2, (COL.x + 1.9, COL.y - 3.4, 1.6), (COL.x + 1.7, COL.y - 3.1, 1.6), (COL.x - 0.5, COL.y, 1.6), (COL.x - 0.5, COL.y, 1.6), 35, 5.6, 1.0, 0.9),   # 20 rosicchia le colonne
    (T_CROLLO - 0.2, T_ACQUA, (SUP.x + 1.5, SUP.y - 17.5, 2.0), (SUP.x + 1.2, SUP.y - 17.0, 2.0), (SUP.x, SUP.y - 3.0, 3.2), (SUP.x, SUP.y - 3.0, 2.8), 24, 9.0, 1.0, 1.4),   # 21 il crollo
    (T_ACQUA, T_VOTA, (3.5, -10.5, 6.5), (3.0, -9.5, 6.8), (0.0, 8.0, 2.2), (0.0, 8.0, 2.0), 24, 9.0, 1.0, 0.8),                                       # 22 il paese finisce sott'acqua
    (T_VOTA, T_RESTA, (0.2, -31.4, 3.0), (0.6, -30.6, 2.9), (-6.0, -26.6, 2.3), (0.2, -24.9, 2.4), 30, 7.0, 1.0, 0.8),                               # 23 Pippo va a votare in canotto
    (T_RESTA, T_PORCA, (3.2, -27.1, 2.8), (3.0, -26.8, 2.8), (1.35, -24.5, WL + 1.02), (1.35, -24.5, WL + 1.02), 40, 4.0, 1.0, 0.7),                   # 24 Rospina, resta altri cento anni
    (T_PORCA, T_FESTA, (-1.6, -30.8, 2.9), (-1.4, -30.4, 2.9), (3.9, -21.0, 3.6), (3.9, -21.0, 3.7), 24, 9.0, 1.0, 1.0),                               # 25 porca puttana
    (T_FESTA, T_BCAN, (5.0, -24.0, 6.4), (5.2, -23.6, 6.4), (6.0, -19.5, 4.3 + RH + 0.05), (6.0, -19.5, 4.3 + RH + 0.05), 40, 4.5, 1.0, 0.9),          # 26 Rospina festeggia
    (T_BCAN, T_DOM, (-3.0, -32.5, 3.2), (-2.6, -32.0, 3.2), (4.5, -23.0, 4.6), (4.5, -23.5, 4.0), 22, 9.0, 1.0, 1.2),                                  # 27 con un bonus canotto
    (T_DOM, TOTAL + 0.1, (1.0, -31.4, 3.2), (1.0, -31.0, 3.2), (1.2, -24.0, 3.5), (1.2, -24.0, 3.5), 20, 9.0, 1.0, 0.6),                               # 28 Rospina o Castora?
]
SHAKES = [(T_BONUS, 0.03, 0.4), (T_2000, 0.02, 0.35), (T_CAST, 0.015, 0.3), (T_CROLLO + 0.3, 0.035, 0.5), (T_BCAN, 0.03, 0.4)]
def hn(t, s): return 0.6 * math.sin(t * 1.7 + s) + 0.3 * math.sin(t * 3.3 + 2.1 * s) + 0.12 * math.sin(t * 7.9 + 3.7 * s)
for f in range(1, NF + 1):
    t = (f - 1) / FPS
    s_ = next((s for s in SHOTS if s[0] <= t < s[1]), SHOTS[-1]); u = sm((t - s_[0]) / (s_[1] - s_[0]))
    cl = Vector(lerp(s_[2], s_[3], u)); tl = Vector(lerp(s_[4], s_[5], u))
    if s_[0] == T_VOTA: tl = canotto(t)[0] + Vector((0, 0, 0.95))             # segue il canotto
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
for d in LIGHTS:
    for fc in all_fcurves(d):
        for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'
set_interp(camd, 'CONSTANT')
for nm in ('Cam', 'CamTarget'):
    for fc in all_fcurves(bpy.data.objects[nm]):
        for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'
try: scene.render.use_motion_blur = True; scene.render.motion_blur_shutter = 0.06
except Exception: pass
os.makedirs(os.path.dirname(os.path.abspath(BLEND)), exist_ok=True)
json.dump([[round(s[0], 3), round(min(s[1], TOTAL), 3)] for s in SHOTS], open(os.path.join(os.path.dirname(os.path.abspath(BLEND)), 'shots.json'), 'w'))
bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(BLEND)); print('SAVED', BLEND, len(bpy.data.objects), 'oggetti')
