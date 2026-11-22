# ===================================================================================================================
# Video 028 - IL POMODORO DA UNDICI EURO, 44,6 s. Si unisce alla testa: templates/head.py + scripts/anim028_body.py -> scripts/anim028.py
# Copione n. 27A (COPIONI.md), caro vita. Scelte dell'autore (20 novembre 2026): pellicano A classico, M1 mercato, B1 sportello,
# S1 motorino rosso. Rospina (stile 'D') e' la «ministra delle Cose Importantissime», politica inventata. Posti: il mercato sul prato
# a sud della strada (y da -33 a -13), la banca chiusa (x = 500), il giardino di Pippo. Tempi da audio/words_t028.json. Luce «cinema».
# ===================================================================================================================
import props021, props023, props024, props028, luci, random, json, rospina, animali, gente027
import pippo2 as pippo
A = kitlook.A
BLEND = os.environ.get('BLEND028', '../t028/pippo_t028.blend')
F28 = props028.font(); M28 = props028.mats028(A)
rnd = random.Random(28)

# ======================= tempi (dalla voce) =======================
T_POM = 4.12; T_EURO = 5.32; T_UNO = 6.54; T_MUTUO = 7.30; T_30 = 8.68; T_FISSO = 9.42; T_PER = 10.24; T_CAZZO1 = 11.08
T_ROSP = 11.94; T_MIN = 13.04; T_CARO = 15.18; T_ESISTE = 16.06; T_VEDE = 16.96; T_CART = 17.46; T_GOLA = 18.02; T_CANOTTO = 19.60; T_MONT = 20.00; T_MERDA = 20.82
T_ALLORA = 21.64; T_LOGICA = 22.90; T_ADD = 23.72; T_PELL = 24.38; T_MANDA = 25.28; T_PICCHIA = 26.45; T_PRESA = 26.95
T_GUA = 27.62; T_TACC = 28.16; T_PAGA = 29.52; T_MOTO = 30.38
T_INCH = 31.50; T_ASSOLVE = 33.30; T_ASS = 33.52; T_QUATTRO = 33.96; T_CAZZO2 = 34.94
T_TUMBO = 35.56; T_BAST = 36.20; T_MANGIA = 37.58; T_GNAM = 37.92
T_ORA = 38.84; T_PIRLA = 39.52; T_RATE = 40.32; T_EPELL = 41.32; T_DOMANDA = 42.70
TOTAL = 44.6; NF = int(TOTAL * FPS)
FASI = [(0.0, 'MK'), (T_MUTUO, 'BK'), (T_ROSP, 'MK'), (T_ADD, 'GD'), (T_MANDA, 'MK'), (T_TUMBO, 'GD')]
def iv(*codes):
    out = []
    for i, (t0, c) in enumerate(FASI):
        t1 = FASI[i + 1][0] if i + 1 < len(FASI) else TOTAL + 1
        if c in codes:
            if out and abs(out[-1][1] - t0) < 1e-6: out[-1] = (out[-1][0], t1)
            else: out.append((t0, t1))
    return out

# ======================= alberi del mercato (prima del look, cosi' diventano veri) =======================
for (x, y) in ((-13.5, -23.0), (13.0, -26.5), (-12.0, -30.5), (14.0, -18.5), (-15.5, -16.5), (9.5, -31.5)): tree(x, y, rng.uniform(1.1, 1.5))

# ======================= rendering e luce =======================
setup_render(scene, 1080, 1920, samples=4, fps=FPS, frames=NF); scene.frame_end = NF
scene.render.image_settings.color_mode = 'RGB'; scene.render.image_settings.compression = 90
camd = bpy.data.cameras.new('Cam'); cam = bpy.data.objects.new('Cam', camd); cac.objects.link(cam); scene.camera = cam
camd.clip_start = 0.01; camd.clip_end = 3000; camd.sensor_width = 36
tgt = empty('CamTarget', (0, 0, 1), None, cac)
ct = cam.constraints.new('TRACK_TO'); ct.target = tgt; ct.track_axis = 'TRACK_NEGATIVE_Z'; ct.up_axis = 'UP_Y'
camd.dof.use_dof = True; camd.dof.focus_object = tgt
kitlook.upgrade(scene, M, envc, prc, extras=False)
scene.eevee.taa_render_samples = 3
for o in list(bpy.data.objects):                                       # il look pianta alberi-sagoma anche in mezzo al mercato: via quelli tra i banchi
    if o.name.startswith('PT_sagoma') and abs(o.location.x) < 11.5 and -34.0 < o.location.y < -13.0: bpy.data.objects.remove(o)
CIELO = luci.cielo_basso(scene.world, 0.4)
scene.world.use_sun_shadow = False
SUN = luci.sole(prc, (0.25, -0.97), lato=1, energia=4.3)
luci.ombre_pulite(scene, mezza_risoluzione=True)
props021.bagliore(scene, forza=0.25, soglia=1.6)

# ======================= posti =======================
MK0 = Vector((0.0, -22.0, 0.0))                  # il banco del pomodoro (fronte verso sud)
PM = Vector((-0.2, -24.3, 0.0))                  # Pippo davanti al banco
PW = Vector((-1.7, -23.7, 0.0))                  # Pippo che guarda Rospina
RP = Vector((1.5, -23.9, 0.0))                   # Rospina davanti al banco
TAGW = Vector((0.62, -22.42, 1.05 + 0.5 + 0.19)) # il cartellino del prezzo
POMW = Vector((0.0, -22.02, 1.05 + 0.22 + 0.15 + 0.19))   # il pomodoro sul cuscino
VEN = Vector((-0.75, -20.95, 0.0))                 # il fruttivendolo dietro al banco
BRP = Vector((6.4, -21.4, 0.0)); BR_RZ = -0.3    # il banco dei pomodori (quello che il pellicano svaligia)
PD = Vector((3.2, -26.2, 0.0))                   # il leggio di Rospina
GS = Vector((-1.0, -23.95, 0.0))                 # Gualtiero davanti al banco
BX = 500.0; BKP = Vector((BX, -1.45, 0.0))       # la banca: Pippo allo sportello
GPT = Vector((-0.95, 0.9, 0.0))                   # giardino: Pippo che addestra
SGB = Vector((1.55, 1.1, 0.0))                    # lo sgabello del pellicano
GF = Vector((0.0, 0.8, 0.0))                     # giardino, finale: Pippo
PEF = Vector((1.65, 0.75, 0.0))                  # finale: il pellicano
TBF = Vector((-1.45, 0.1, 0.0))                  # finale: Tumbo

# ======================= set =======================
mkc = collection('Mercato'); bkc = collection('Banca'); gdc = collection('Giardino')
try: m_pav = A.materiale('PavingStones070', dimensione=2.0)
except Exception as e: print('pavimento', e); m_pav = material('M28_piazza', (0.6, 0.58, 0.55), rough=0.9)
props028.box('Piazza', (-19.0, -33.0, 0.0), (19.0, -13.2, 0.03), m_pav, mkc)
B0 = props028.bancarella(mkc, M28, F28, 'Banco'); B0['root'].location = MK0
BANCHI = [B0]
for nm, p_, rz, ins, fru, ten, cen in (('BancoL', (-6.4, -21.4), 0.3, 'FORMAGGI NO', ('mela', 'limone', 'arancia', 'pesca'), ('tenda_v', 'tenda_b'), 'mela'),
                                       ('BancoR', (BRP.x, BRP.y), BR_RZ, 'POMODORI', ('zucchina', 'melanzana', 'limone', 'zucchina'), ('tenda_g', 'tenda_b'), 'pom'),
                                       ('BancoL2', (-5.2, -28.6), PI / 2, 'FRUTTA', ('pesca', 'arancia', 'mela', 'limone'), ('tenda_a', 'tenda_b'), 'arancia'),
                                       ('BancoR2', (5.2, -28.6), -PI / 2, 'VERDURA', ('melanzana', 'zucchina', 'zucchina', 'melanzana'), ('tenda_v', 'tenda_g'), 'limone')):
    b_ = props028.bancarella(mkc, M28, F28, nm, insegna=ins if ins != 'FORMAGGI NO' else 'SOLO FRUTTA', speciale=False, frutti=fru, tenda=ten, centro=cen)
    b_['root'].location = (p_[0], p_[1], 0.0); b_['root'].rotation_euler = (0, 0, rz); BANCHI.append(b_)
RUBABILI = BANCHI[2]['rubabili']
props028.festone(mkc, M28, (-5.2, -28.6, 3.5), (5.2, -28.6, 3.5), n=14, nome='FestoneA')
props028.festone(mkc, M28, (-6.4, -21.6, 3.5), (-0.2, -22.4, 3.4), n=9, nome='FestoneB'); props028.festone(mkc, M28, (0.2, -22.4, 3.4), (6.4, -21.6, 3.5), n=9, nome='FestoneC')
for k, (aid, p_, h_, rz) in enumerate((('street_lamp_01', (-9.5, -25.0), 4.6, 0), ('street_lamp_01', (9.5, -24.0), 4.6, 180), ('painted_wooden_bench', (-9.8, -28.5), 1.0, 90), ('painted_wooden_bench', (10.0, -29.5), 1.0, -90))):
    try: A.modello(aid, posizione=(p_[0], p_[1], 0.03), altezza=h_, rotazione=rz, collezione=mkc, max_triangoli=5000)
    except Exception as e: print('arredo', aid, e)
# gente del mercato: il fruttivendolo, il venditore di pomodori e sei clienti (pupazzi di gente027, non sono personaggi della serie)
VCOL, VR = gente027.pupazzo('Fruttivendolo', gente027.LOOK_FOLLA[4]); VENO = gente027.copia(mkc, VCOL, VEN.x, VEN.y, 0.03, 0.0, altezza=2.1, nome='FruttivendoloI')
V2COL, V2R = gente027.pupazzo('Pomodoraio', gente027.LOOK_FOLLA[8]); V2P = BRP + Vector((0.9 * math.cos(BR_RZ) - 1.05 * math.sin(BR_RZ), 0.9 * math.sin(BR_RZ) + 1.05 * math.cos(BR_RZ), 0))
V2O = gente027.copia(mkc, V2COL, V2P.x, V2P.y, 0.03, BR_RZ, altezza=2.1, nome='PomodoraioI')
for R_ in (VR, V2R):
    for nm in 'LR': R_['shoulder' + nm].rotation_mode = 'QUATERNION'
for k, (li, x, y, v) in enumerate(((0, -4.2, -25.6, 2.2), (1, 4.1, -30.2, -1.4), (3, -7.6, -23.6, 2.9), (5, 7.9, -23.9, 3.3), (9, -3.6, -30.6, 1.5), (10, 8.6, -27.6, -1.9), (11, -9.0, -19.8, 2.4))):
    c_, _ = gente027.pupazzo('Cliente%d' % k, gente027.LOOK_FOLLA[li]); gente027.copia(mkc, c_, x, y, 0.03, v, altezza=rnd.uniform(1.9, 2.15), nome='ClienteI%d' % k)
PODIO = props028.podio(mkc, M28, F28); PODIO.location = PD; PODIO.scale = (0.85, 0.85, 0.85)
FASC = props028.fascicolo(mkc, M28, F28); FASC.rotation_mode = 'XYZ'; FASC.scale = (0.7, 0.7, 0.7)
ASSOLTA = props028.timbrata(mkc, M28, F28, 'ASSOLTA', 'Assolta', size=0.17); ASSOLTA.rotation_mode = 'XYZ'
QUATTRO = props023.testo(mkc, 'Quattro', '4 SECONDI', 0.26, M28['inchiostro'], (0, 0, 0), font=F28, estrudi=0.02); QUATTRO.rotation_mode = 'XYZ'
MOTO = props028.motorino(mkc, M28, (0.85, 0.07, 0.05)); MOTO['root'].rotation_mode = 'XYZ'
TAGM = props028.cartellino(mkc, M28, F28, testo='1 ZUCCHINA', h=0.3, nome='PrezzoMoto', larg=1.5, alt=0.32); TAGM.rotation_mode = 'XYZ'
ZUC = props028.zucchina(chc, M28)
# la banca
BK = props028.sala_banca(bkc, M28, F28); BK['root'].location = (BX, 0, 0)
BCOL, BR_ = None, None
BANO, BKR = props028.banchiere(bkc); BANO.location = (BX, 1.0, 0.0)
for nm in 'LR': BKR['shoulder' + nm].rotation_mode = 'QUATERNION'
TIMB = BK['timbro']; TIMB.rotation_mode = 'XYZ'; TIMB0 = Vector(TIMB.location)
ST1 = bpy.data.objects['BancaContrattoTimbro']; ST2 = bpy.data.objects['BancaContrattoTimbro2']
# il giardino
LAV = props028.lavagna(gdc, M28, F28); LAV.location = (0.1, 4.3, 0.0)
SGA = props028.sgabello(gdc, M28); SGA.location = SGB
ROT = props028.rotolo(gdc, M28, F28, lung=5.6, alto=1.12); ROT.location = (GF.x, GF.y - 0.62, 0.0)
SACCO = props028.sacco(chc, M28, F28); CUS = props028.cuscino(chc, M28, 0.5, 'CuscinoMano'); TOM2 = props028.pomodoro(chc, M28, 0.2, 'PomodoroMano')
TOMT = props028.pomodoro(prc, M28, 0.15, 'PomodoroLancio'); TOMT.rotation_mode = 'XYZ'

# ======================= personaggi =======================
P = pippo.build_pippo(chc); Tb = tumbo.build_tumbo(chc, scale=0.75); GU = props009.gualtiero(chc, G9)
RO = rospina.rospina(chc, rospina.mats_rospina(), stile='D'); PE = animali.pellicano(chc, tipo='A')
for r in (P['root'], Tb['root'], GU['root'], RO['root'], PE['root']): r.rotation_mode = 'XYZ'
for nm in 'LR': P['shoulder' + nm].rotation_mode = 'QUATERNION'
for nm in ('shoulderL', 'shoulderR', 'hipL', 'hipR', 'head'): GU[nm].rotation_mode = 'XYZ'; RO[nm].rotation_mode = 'XYZ'
RO['gola'].hide_render = False; RO['gola'].hide_viewport = False
SACCO.parent = P['body']; SACCO.location = (0, -0.60, -0.14); SACCO.scale = (0.85, 0.85, 0.85)
CUS.parent = P['body']; CUS.location = (0, -0.62, 0.20); TOM2.parent = CUS; TOM2.location = (0, 0, 0.15)
ZUC.parent = GU['shoulderR']; ZUC.location = (0, -0.02, -0.84); ZUC.rotation_euler = (0, 0, 0)
POUCH = []
for k in range(3):
    o = props028.pomodoro(chc, M28, 0.085, 'PomodoroBecco%d' % k); o.parent = PE['jaw']; o.location = (0.02 * (k - 1), -0.2 - 0.2 * k, 0.03); POUCH.append(o)
bpy.context.view_layer.update()
RO_HZ = RO['head'].matrix_world.translation.z; PE_H = PE['head'].matrix_world.translation.copy(); TB_H = Tb['head'].matrix_world.translation.copy()
PZ = 1.78                                        # centro della testa di Pippo
print('ALTEZZE rospina', round(RO_HZ, 2), 'pellicano', [round(v, 2) for v in PE_H], 'tumbo', [round(v, 2) for v in TB_H])

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
END = TOTAL + 1
show_only(ST1, [(T_30 + 0.08, T_ROSP)]); show_only(ST2, [(T_FISSO + 0.08, T_ROSP)])
show_only(bpy.data.objects['BancaVetro'], [(T_MUTUO, T_PER)])           # nel controcampo il vetro velava tutto: si toglie
show_only(BK['root'], iv('BK')); show_only(BANO, iv('BK'))
show_only(SACCO, [(0.0, T_MUTUO)]); show_only(TOM2, [(T_TUMBO, T_GNAM)]); show_only(CUS, [(T_TUMBO, T_RATE)])
show_only(ZUC, [(T_PAGA, T_INCH)])
for o in POUCH: show_only(o, [(T_PRESA, T_GUA)])
for o in RUBABILI: show_only(o, [(0.0, T_PRESA)])
show_only(TOMT, [(T_ADD + 0.2, T_PELL)])
show_only(MOTO['root'], [(T_GUA, T_INCH)]); show_only(TAGM, [(T_MOTO, T_INCH)])
show_only(FASC, [(T_INCH, T_TUMBO)]); show_only(ASSOLTA, [(T_ASS, T_TUMBO)]); show_only(QUATTRO, [(T_QUATTRO, T_TUMBO)]); show_only(PODIO, [(T_INCH, T_TUMBO)])
show_only(LAV, [(T_ADD, T_MANDA)]); show_only(SGA, [(T_ADD, T_MANDA)]); show_only(ROT, [(T_RATE, END)])
show_only(P['root'], [(0.0, T_MANDA), (T_TUMBO, END)])
show_only(RO['root'], [(T_ROSP, T_ALLORA), (T_INCH, T_TUMBO)])
show_only(GU['root'], [(T_GUA, T_INCH)])
show_only(Tb['root'], [(T_TUMBO, END)])
show_only(PE['root'], [(T_ADD, T_GUA), (T_EPELL - 0.5, END)])
# per fare prima: in banca non si rende il quartiere, e il mercato si rende solo nelle scene del mercato (dal giardino non si vede)
for o in list(mkc.objects):
    if o.parent is None and o.name not in NEVER: show(o, iv('MK'))
for o in list(envc.objects):
    if o.parent is None and o.name not in NEVER: show(o, iv('MK', 'GD'))
for cu in bpy.data.curves:
    if cu.rna_type.identifier == 'TextCurve': cu.resolution_u = 4

# ======================= luce per fase =======================
def chiavi(owner, attr, valori):
    for (t_, v) in valori:
        setattr(owner, attr, v); owner.keyframe_insert(attr, frame=fr(t_))
def per_fase(owner, attr, vals, default=0.0):
    chiavi(owner, attr, [(t0, vals.get(c, default)) for (t0, c) in FASI])
per_fase(SUN.data, 'energy', {'MK': 4.3, 'GD': 4.3})
per_fase(CIELO.inputs['Strength'], 'default_value', {'MK': 0.42, 'GD': 0.42, 'BK': 0.22})
per_fase(scene.view_settings, 'exposure', {'MK': 0.02, 'GD': 0.12, 'BK': -0.1})
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
PLAF = area('PlafBanca', (BX, -2.5, 4.4), 900.0, 5.0)
LB = luci.cinema(prc, (BX, -0.6, 1.6), (BX - 3.0, -5.5, 2.2), distanza=5.0, lato=1, forza=0.55, nome='CinemaB')
LB2 = luci.cinema(prc, (BX, -1.45, 1.7), (BX + 0.6, 1.2, 2.0), distanza=3.5, lato=-1, forza=0.35, nome='CinemaB2')
LN = luci.cinema(prc, (-0.2, -24.3, 1.7), (0.3, -21.5, 2.0), distanza=3.2, lato=1, forza=0.42, nome='CinemaN', controluce=0.6)      # dal banco verso sud: facce in ombra
LR_ = luci.cinema(prc, (1.5, -23.9, 1.6), (1.4, -27.0, 1.6), distanza=3.6, lato=-1, forza=0.22, nome='CinemaR', riempimento=0.6)
LG = luci.cinema(prc, (0.2, 0.8, 1.4), (0.0, -4.8, 1.6), distanza=4.2, lato=-1, forza=0.35, nome='CinemaG', riempimento=0.6)
GLOW = bpy.data.lights.new('LucePomodoro', 'POINT'); GLOW.energy = 55.0; GLOW.color = (1.0, 0.8, 0.35); GLOW.shadow_soft_size = 0.3; GLOW.use_shadow = False
GLO = bpy.data.objects.new('LucePomodoro', GLOW); prc.objects.link(GLO); GLO.location = POMW + Vector((0, -0.75, 0.25))
on_off(list(LB.values()), [(T_MUTUO, T_PER)]); on_off(list(LB2.values()), [(T_PER, T_ROSP)])
LN0 = luci.cinema(prc, (-0.2, -27.2, 1.6), (0.8, -23.5, 1.4), distanza=5.5, lato=1, forza=0.8, nome='CinemaN0', controluce=0.5)
on_off(list(LN0.values()), [(0.0, 1.6)])
on_off(list(LN.values()), [(1.6, T_POM), (T_GUA, T_MOTO)]); on_off(list(LR_.values()), [(T_ROSP, T_ALLORA)]); on_off(list(LG.values()), iv('GD'))
on_off([GLO], [(2.3, T_UNO)])
chiavi(PLAF.data, 'energy', [(0.0, 0.0), (T_MUTUO, 600.0), (T_ROSP, 0.0)])
LIGHTS = [SUN.data, PLAF.data, GLOW] + [l_.data for d_ in (LB, LB2, LN, LN0, LR_, LG) for l_ in d_.values()]

# ======================= pose =======================
def qdir(d, rest=(0, 0, -1)): return Vector(rest).rotation_difference(Vector(d).normalized())
def yaw_to(a, b): return math.atan2(b[0] - a[0], -(b[1] - a[1]))
def mixv(a, b, u): return tuple(Vector(a).lerp(Vector(b), u))
def braccia(nome, forza=1.0):
    b = pippo.EMOZIONI_FORTI[nome]['braccia']; return {'aL': tuple(Vector((0, 0, -1)).lerp(Vector(b[0]).normalized(), forza)), 'aR': tuple(Vector((0, 0, -1)).lerp(Vector(b[1]).normalized(), forza))}
GIU = dict(aL=(-0.08, 0, -1), aR=(0.08, 0, -1))
PORTA = dict(aL=(-0.28, -0.8, -0.52), aR=(0.28, -0.8, -0.52))            # porta qualcosa davanti alla pancia
def jit(t, a=0.02, f=37.0): return a * math.sin(t * f) * math.sin(t * f * 0.71 + 1.3)
def arco(t, t0, d, h): return h * math.sin(PI * (t - t0) / d) if t0 <= t < t0 + d else 0.0

def pp(t):
    """Pippo: loc, yaw, lean, bend (busto), head, braccia, anche."""
    S_ = dict(loc=Vector((0, 0, -50)), yaw=0.0, lean=0.0, bend=0.0, head=(0, 0, 0), hL=0.0, hR=0.0, **GIU)
    if t < T_MUTUO:                                                      # al mercato col sacco dei soldi
        u = ramp(t, 0.0, 2.3); w = math.sin(t * 9.5) * (1 - ramp(t, 2.0, 2.3))
        p = Vector((-0.2, -30.3, 0)).lerp(PM, u if t < 2.3 else 1.0)
        S_.update(loc=p + Vector((0, 0, 0.04 * abs(w))), yaw=PI, hL=0.5 * w, hR=-0.5 * w, bend=0.06, **PORTA)
        if t >= 2.3: S_.update(head=(-0.12 * ramp(t, 2.3, 2.6), 0, 0), bend=-0.05 * ramp(t, 2.3, 2.7))
        if t >= T_UNO: S_.update(yaw=-0.55, head=(0.0, 0, 0.0), bend=0.0)                                   # guarda il fruttivendolo: «uno?!»
    elif t < T_ROSP:                                                     # in banca
        k = ramp(t, T_PER, T_PER + 0.3)
        S_.update(loc=BKP.copy() + Vector((jit(t, 0.012, 23), 0, 0)), yaw=PI, bend=0.12, head=(0.1 + 0.06 * math.sin(t * 9), 0, 0),
                  aL=mixv((0.22, -0.8, 0.5), (-0.1, -0.5, -0.85), k), aR=mixv((-0.22, -0.8, 0.5), (0.1, -0.5, -0.85), k))
    elif t < T_ALLORA:                                                   # guarda Rospina
        S_.update(loc=PW.copy(), yaw=0.95, head=(0, 0, -0.15))
        if t >= T_GOLA: S_.update(head=(-0.2 * ramp(t, T_GOLA, T_CANOTTO), 0, -0.15), **braccia('sorpreso', ramp(t, T_GOLA + 0.4, T_GOLA + 0.9)))
        if t >= T_MERDA: S_.update(head=(0, 0, -0.15), **braccia('spaventato', 1 - ramp(t, T_MERDA + 0.4, T_MERDA + 0.8)))
    elif t < T_ADD:                                                      # la cosa piu' logica
        k = ramp(t, T_ALLORA + 0.1, T_ALLORA + 0.45)
        S_.update(loc=PW.copy(), yaw=0.0, head=(-0.05, 0, 0.05 * math.sin(t * 5)), aL=(-0.08, 0, -1), aR=mixv((0.08, 0, -1), (0.28, -0.35, 0.9), k))
    elif t < T_MANDA:                                                    # addestra il pellicano: lancia il pomodoro
        k = ramp(t, T_ADD + 0.15, T_ADD + 0.36) * (1 - ramp(t, T_ADD + 0.5, T_ADD + 0.9))
        S_.update(loc=GPT.copy(), yaw=1.25, head=(-0.08, 0, 0), aL=(-0.5, -0.2, 0.6), aR=mixv((0.3, 0.5, 0.3), (0.2, -0.8, 0.55), ramp(t, T_ADD + 0.15, T_ADD + 0.36)))
        if t >= T_PELL: S_.update(**braccia('felice'))
    elif t >= T_TUMBO:                                                   # in giardino: il pomodoro, Tumbo, le rate
        S_.update(loc=GF.copy(), yaw=0.0, bend=0.03, **PORTA)
        if t < T_MANGIA: S_.update(head=(-0.1, 0, 0.0))
        elif t < T_ORA: S_.update(head=(0.15, 0, 0), bend=-0.08 * (1 - ramp(t, T_GNAM + 0.3, T_GNAM + 0.7)))
        elif t < T_RATE: S_.update(head=(0.3, 0, 0), bend=0.14)
        elif t < T_DOMANDA: S_.update(head=(0.22, 0, 0.3 * ramp(t, T_EPELL + 0.2, T_EPELL + 0.6)), bend=0.08, aL=(-0.2, -0.75, -0.45), aR=(0.2, -0.75, -0.45))
        else:
            k = ramp(t, T_DOMANDA, T_DOMANDA + 0.3)
            S_.update(head=(-0.05, 0, 0.12 * math.sin((t - T_DOMANDA) * 4.5)), aL=mixv((-0.2, -0.75, -0.45), (-0.9, -0.25, 0.25), k), aR=mixv((0.2, -0.75, -0.45), (0.9, -0.25, 0.25), k))
    return S_

GOLA0 = Vector(RO['gola'].location)
def gola(t):
    """quanto e' gonfia la gola di Rospina (0..1): sale da «le si gonfia» a «canotto», scoppia su «merda»."""
    if t < T_GOLA: return 0.0
    if t < T_MERDA: return ramp(t, T_GOLA, T_CANOTTO) * (1.0 + 0.05 * math.sin(t * 22))
    return max(0.0, 1.0 - (t - T_MERDA) / 0.22)
def rp(t):
    """Rospina: loc, yaw, lean, head, spalle (euler), anche, faccia (parametri di rex)."""
    S_ = dict(loc=RP.copy(), yaw=0.0, lean=0.0, head=(0, 0, 0), sL=(0, 0.12, 0), sR=(0, -0.12, 0), hL=0.0, hR=0.0, f=dict(rospina.EMOZIONI['importantissima']))
    if t < T_CARO:                                                       # arriva: passo da sfilata, mento in su
        u = ramp(t, T_ROSP, T_MIN + 0.7); w = math.sin((t - T_ROSP) * 10.0) * (1 - ramp(t, T_MIN + 0.5, T_MIN + 0.7))
        p = Vector((6.4, -24.9, 0)).lerp(RP, u); k = ramp(t, T_MIN + 0.6, T_MIN + 1.0)
        S_.update(loc=p + Vector((0, 0, 0.03 * abs(w))), yaw=-PI / 2 * (1 - ramp(t, T_MIN + 0.4, T_MIN + 0.9)) + 0.0, hL=0.5 * w, hR=-0.5 * w, head=(-0.18, 0, 0),
                  sL=(0.5 * w * (1 - k), 0.25 + 1.0 * k, 0), sR=(-0.5 * w * (1 - k), -0.25 - 1.0 * k, 0))
    elif t < T_VEDE:                                                     # «il caro vita non esiste!»: dito in alto
        b = abs(math.sin((t - T_CARO) * 13.0)) if t < T_ESISTE + 0.45 else 0.0
        S_.update(lean=-0.06, head=(-0.1 + 0.05 * b, 0, 0.06 * math.sin(t * 6)), sR=(-2.75 + 0.2 * b, 0, 0.15), sL=(0.1, 0.5, 0), f=dict(rospina.EMOZIONI['comizio'], mouth=0.25 + 0.75 * b))
        if t >= T_ESISTE + 0.45: S_['f'] = dict(rospina.EMOZIONI['importantissima'])
    elif t < T_GOLA:                                                     # vede il cartellino
        k = ramp(t, T_VEDE, T_VEDE + 0.3)
        S_.update(yaw=yaw_to(RP, TAGW) * k, head=(-0.12 * k, 0, 0), sR=(-0.3, -0.3, 0), sL=(-0.3, 0.3, 0),
                  f=dict(rospina.EMOZIONI['scandalizzata'], gola=0.0) if t >= T_CART - 0.1 else dict(rospina.EMOZIONI['importantissima']))
    elif t < T_ALLORA:                                                   # le si gonfia la gola e si alza da terra come un canotto
        g = gola(t); z = 0.42 * min(1.0, g); fl = math.sin(t * 16.0)
        S_.update(yaw=0.2, loc=RP + Vector((0, 0, z + 0.03 * math.sin(t * 5))), lean=-0.25 * min(1.0, g), head=(-0.3 * min(1.0, g), 0, 0),
                  sL=(0.2 * fl, 1.3, 0), sR=(-0.2 * fl, -1.3, 0), hL=0.25 * fl * min(1, g), hR=-0.25 * fl * min(1, g), f=dict(rospina.EMOZIONI['scandalizzata'], gola=0.0, mouth=0.25))
        if t >= T_MERDA + 0.22: S_.update(loc=RP.copy() + Vector((0, 0, arco(t, T_MERDA + 0.22, 0.3, 0.1))), lean=0.1, head=(0.25, 0, 0), sL=(0, 0.15, 0), sR=(0, -0.15, 0), hL=0, hR=0, f=dict(rospina.EMOZIONI['offesa']))
    else:                                                                # l'inchiesta su se stessa
        S_.update(loc=PD + Vector((0, 0.62, 0)), yaw=0.0, sL=(0, 1.75, 0), sR=(-0.5, -0.2, 0), head=(0.05, 0, 0.45), f=dict(rospina.EMOZIONI['furiosa'], look=(-0.9, 0.2)))
        if t >= T_ASS:
            k = ramp(t, T_ASS, T_ASS + 0.2)
            S_.update(head=(-0.12 * k, 0, 0.45 * (1 - k)), sR=(-2.9 * k, -0.25, 0), sL=(0, 1.75, 0), f=dict(rospina.EMOZIONI['trionfo']))
        if t >= T_CAZZO2: S_.update(sL=(0, 2.6, 0), sR=(0, -2.6, 0), head=(-0.2, 0, 0), loc=PD + Vector((0, 0.62, arco(t, T_CAZZO2, 0.3, 0.18))))
    return S_

def gp(t):
    """Gualtiero: taccagno al banco, poi con la zucchina."""
    S_ = dict(loc=GS.copy(), yaw=PI, lean=0.08, head=(0.12, 0, 0.2 * math.sin(t * 7.0)), sR=(-0.2, 0, -0.5), sL=(-0.2, 0, 0.5), hL=0.0, hR=0.0)   # fa di no con la testa
    if T_PAGA <= t < T_MOTO:
        k = ramp(t, T_PAGA, T_PAGA + 0.3); S_.update(yaw=PI + 0.8, head=(-0.15 * k, 0, 0), sR=(-2.5 * k, 0, 0.1), sL=(-0.2, 0, 0.3))
    elif t >= T_MOTO:                                                    # se ne va felice con la zucchina in alto
        w = math.sin((t - T_MOTO) * 11.0); u = ramp(t, T_MOTO, T_INCH)
        S_.update(loc=Vector((-0.55, -24.4, 0)).lerp(Vector((-0.75, -24.9, 0)), u) + Vector((0, 0, 0.05 * abs(w))), yaw=0.55, lean=-0.05, head=(-0.2, 0, 0), sR=(-2.85, 0, 0.1), sL=(0.4 * w, 0, 0.2), hL=0.5 * w, hR=-0.5 * w)
    return S_

def tp(t):
    """Tumbo: punta il pomodoro, salta, lo mangia, poi sta sdraiato sazio."""
    S_ = dict(loc=Vector((0.95, -0.25, 0.0)), yaw=0.0, head=(0, 0, 0), tail=(-1.0 + 0.5 * math.sin(t * 22), 0, 0), pitch=0.0, roll=0.0)
    S_['yaw'] = yaw_to(S_['loc'], GF)
    if t < T_MANGIA:
        S_.update(head=(-0.55, 0, 0.1 * math.sin(t * 6)), loc=Vector((0.95, -0.25, 0)).lerp(Vector((0.84, -0.14, 0)), ramp(t, T_BAST, T_MANGIA - 0.1)))
    elif t < T_GNAM + 0.35:                                              # il salto
        d = T_GNAM + 0.35 - T_MANGIA; u = (t - T_MANGIA) / d
        p = Vector((0.6, 0.05, 0)).lerp(Vector((-0.6, -0.05, 0)), u); p.z = 0.95 * math.sin(PI * u)
        S_.update(loc=p, head=(-0.5 + 0.9 * u, 0, 0), pitch=-0.5 + 1.0 * u)
    elif t < T_RATE:                                                     # mastica
        S_.update(loc=Vector((-0.6, -0.05, 0)), yaw=0.35, head=(0.12 * math.sin(t * 14), 0, 0.2 * math.sin(t * 9)))
    else:
        S_.update(loc=TBF.copy(), yaw=0.5, head=(-0.1, 0, 0.1 * math.sin(t * 3)), tail=(-1.0 + 0.25 * math.sin(t * 8), 0, 0))
    return S_

VOLO = [(-13.0, -34.0, 15.0), (-6.0, -30.0, 14.0), (1.0, -26.5, 12.5), (4.6, -23.5, 9.0)]      # il volo sopra il mercato
BECCATA = Vector((6.03, -22.55, 0.03)); BECC_YAW = 2.84                    # atterra davanti al banco dei pomodori, il becco nella cassetta
def bez(pts, u):
    pts = [Vector(p) for p in pts]
    while len(pts) > 1: pts = [pts[i].lerp(pts[i + 1], u) for i in range(len(pts) - 1)]
    return pts[0]
def pe(t):
    """Pellicano: loc, yaw, pitch, becco (jaw), ali (alzata), zampe, testa."""
    S_ = dict(loc=SGB + Vector((0, 0, 0.6)), yaw=-1.15, pitch=0.0, jaw=0.0, ali=0.25, zampe=0.0, head=(0, 0, 0))
    if t < T_MANDA:                                                      # sullo sgabello: prende al volo
        j = ramp(t, T_PELL - 0.28, T_PELL - 0.1) * (1 - ramp(t, T_PELL, T_PELL + 0.1))
        S_.update(jaw=0.75 * j, head=(-0.25 * j, 0, 0), ali=0.25 + 1.0 * abs(math.sin((t - T_PELL) * 14)) * ramp(t, T_PELL, T_PELL + 0.1), loc=SGB + Vector((0, 0, 0.6 + arco(t, T_PELL, 0.35, 0.25))))
    elif t < T_GUA:
        fl = 0.9 + 0.75 * math.sin(t * 15.0)
        if t < T_PICCHIA:                                                # in volo
            u = (t - T_MANDA) / (T_PICCHIA - T_MANDA); p = bez(VOLO, u); p2 = bez(VOLO, min(1.0, u + 0.02))
            S_.update(loc=p, yaw=yaw_to(p, p2), pitch=0.2, ali=fl, zampe=1.3)
        elif t < T_PRESA:                                                # la picchiata
            u = sm((t - T_PICCHIA) / (T_PRESA - T_PICCHIA)); p = Vector(VOLO[-1]).lerp(BECCATA, u)
            S_.update(loc=p, yaw=BECC_YAW, pitch=0.7 - 0.4 * u, ali=1.45, zampe=1.3 * (1 - u), jaw=0.85 * u)
        else:                                                            # via col bottino
            u = (t - T_PRESA) / (T_GUA - T_PRESA); k = ramp(t, T_PRESA + 0.12, T_PRESA + 0.3); p = BECCATA.lerp(Vector((2.5, -25.0, 6.5)), max(0.0, (u - 0.2) / 0.8) ** 1.2)
            S_.update(loc=p, yaw=BECC_YAW + (yaw_to(BECCATA, Vector((2.5, -25.0, 0))) - BECC_YAW) * k, pitch=0.3 - 0.5 * k, ali=fl, zampe=1.3 * k, jaw=0.45)
    else:                                                                # il finale: atterra accanto a Pippo
        u = ramp(t, T_EPELL - 0.45, T_EPELL + 0.1)
        S_.update(loc=PEF + Vector((1.2 * (1 - u), 0.3 * (1 - u), 0.0 + 3.2 * (1 - u) ** 1.5)), yaw=-0.55, ali=0.25 + (0.9 + 0.6 * math.sin(t * 15)) * (1 - ramp(t, T_EPELL + 0.1, T_EPELL + 0.4)),
                  zampe=0.0, head=(0, 0, -0.35 * ramp(t, T_EPELL + 0.3, T_EPELL + 0.6)))
        if t >= T_DOMANDA: S_.update(jaw=0.55 * abs(math.sin((t - T_DOMANDA) * 7.0)) * (1 - ramp(t, T_DOMANDA + 0.9, T_DOMANDA + 1.1)), head=(-0.1, 0, -0.35))
    return S_

# ======================= chiavi =======================
def K(o, f, loc=None, rot=None, scale=None):
    if loc is not None: o.location = loc; o.keyframe_insert('location', frame=f)
    if rot is not None: o.rotation_euler = rot; o.keyframe_insert('rotation_euler', frame=f)
    if scale is not None: o.scale = scale if isinstance(scale, (tuple, list)) else (scale,) * 3; o.keyframe_insert('scale', frame=f)
def Q(o, f, d): o.rotation_quaternion = qdir(d); o.keyframe_insert('rotation_quaternion', frame=f)
def tra(t, a, b): return a <= t < b
for f in range(1, NF + 1):
    t = (f - 1) / FPS
    s = pp(t)
    K(P['root'], f, tuple(s['loc']), (s['lean'], 0, s['yaw'])); K(P['body'], f, rot=(s['bend'], 0, 0)); K(P['head'], f, rot=s['head'])
    for nm, k_ in (('L', 'aL'), ('R', 'aR')): Q(P['shoulder' + nm], f, s[k_])
    for nm, k_ in (('L', 'hL'), ('R', 'hR')): K(P['hip' + nm], f, rot=(s[k_], 0, 0))
    if tra(t, T_ROSP - 0.1, T_ALLORA + 0.1) or tra(t, T_INCH - 0.1, T_TUMBO + 0.1):
        s = rp(t)
        K(RO['root'], f, tuple(s['loc']), (s['lean'], 0, s['yaw'])); K(RO['head'], f, rot=s['head'])
        for nm in 'LR': K(RO['shoulder' + nm], f, rot=s['s' + nm]); K(RO['hip' + nm], f, rot=(s['h' + nm], 0, 0))
        rospina.rex(RO, f, **s['f'])
        g = gola(t); go = RO['gola']                                      # il canotto: la gola diventa piu' grossa della testa
        go.scale = (0.075 + 0.60 * g, 0.06 + 0.46 * g, 0.035 + 0.36 * g); go.location = (GOLA0.x, GOLA0.y - 0.40 * g, GOLA0.z - 0.38 * g)
        go.keyframe_insert('scale', frame=f); go.keyframe_insert('location', frame=f)
    if tra(t, T_GUA - 0.1, T_INCH + 0.1):
        g = gp(t)
        K(GU['root'], f, tuple(g['loc']), (g['lean'], 0, g['yaw'])); K(GU['shoulderL'], f, rot=g['sL']); K(GU['shoulderR'], f, rot=g['sR']); K(GU['head'], f, rot=g['head'])
        for nm in 'LR': K(GU['hip' + nm], f, rot=(g['h' + nm], 0, 0))
    if t >= T_TUMBO - 0.1:
        s = tp(t)
        K(Tb['root'], f, tuple(s['loc']), (s['pitch'], s['roll'], s['yaw']), 0.75); K(Tb['head'], f, rot=s['head']); K(Tb['tail'], f, rot=s['tail'])
    if tra(t, T_ADD - 0.1, T_GUA + 0.1) or t >= T_EPELL - 0.6:
        s = pe(t)
        K(PE['root'], f, tuple(s['loc']), (s['pitch'], 0, s['yaw'])); K(PE['head'], f, rot=s['head']); K(PE['jaw'], f, rot=(s['jaw'], 0, 0))
        K(PE['wingL'], f, rot=(0, s['ali'], 0)); K(PE['wingR'], f, rot=(0, -s['ali'], 0))
        for g_ in PE['legs']: K(g_, f, rot=(s['zampe'], 0, 0))
    # il pomodoro lanciato a lezione
    if tra(t, T_ADD, T_PELL + 0.05):
        u = max(0.0, min(1.0, (t - (T_ADD + 0.36)) / (T_PELL - 0.06 - (T_ADD + 0.36))))
        a_ = GPT + Vector((0.55, -0.25, 1.75)); b_ = SGB + Vector((-0.86, -0.39, 0.6 + 1.5)); p = a_.lerp(b_, u); p.z += 0.7 * math.sin(PI * u)
        K(TOMT, f, tuple(p), (t * 9, 0, t * 5))
    # fruttivendolo: «uno!» col dito, poi le mani nei capelli quando arriva il motorino; il pomodoraio agita il pugno
    k1 = ramp(t, T_UNO, T_UNO + 0.15) * (1 - ramp(t, T_MUTUO - 0.1, T_MUTUO)); k2 = ramp(t, T_MOTO, T_MOTO + 0.2) * (1 - ramp(t, T_INCH - 0.1, T_INCH))
    Q(VR['shoulderR'], f, mixv(mixv((0.1, 0, -1), (0.25, -0.5, 0.85), k1), (0.5, -0.2, 0.9), k2)); Q(VR['shoulderL'], f, mixv((-0.1, 0, -1), (-0.5, -0.2, 0.9), k2))
    k3 = ramp(t, T_PRESA - 0.2, T_PRESA) * (1 - ramp(t, T_GUA + 0.5, T_GUA + 0.8))
    Q(V2R['shoulderR'], f, mixv((0.1, 0, -1), (0.3 + 0.2 * math.sin(t * 20), -0.3, 0.95), k3)); Q(V2R['shoulderL'], f, (-0.1, 0, -1))
    # banca: il timbro e il braccio del banchiere
    if tra(t, T_MUTUO - 0.1, T_ROSP + 0.1):
        tb = TIMB0 + Vector((0, 0, 0)); c1 = Vector((0.015, -0.245, 1.341)); c2 = Vector((-0.015, 0.1, 1.341))
        def colpo(t0, c):
            if t < t0 - 0.3: return None
            if t < t0: return TIMB0.lerp(c + Vector((0, 0, 0.75)), sm((t - (t0 - 0.3)) / 0.22)) if t < t0 - 0.08 else (c + Vector((0, 0, 0.75))).lerp(c, (t - (t0 - 0.08)) / 0.08)
            if t < t0 + 0.1: return c.copy()
            if t < t0 + 0.4: return c.lerp(TIMB0, sm((t - (t0 + 0.1)) / 0.3))
            return None
        p = colpo(T_30, c1)
        if p is None: p = colpo(T_FISSO, c2)
        if p is None: p = TIMB0.copy()
        K(TIMB, f, tuple(p))
        d = Vector((p.x, p.y - 1.0, p.z + 0.36)) - Vector((-0.31, 0.0, 1.37))
        Q(BKR['shoulderL'], f, tuple(d) if (p - TIMB0).length > 0.02 else (-0.2, -0.5, -0.8)); Q(BKR['shoulderR'], f, (0.15, -0.35, -0.9))
    # l'inchiesta: fascicolo in mano, timbro ASSOLTA, 4 SECONDI
    if tra(t, T_INCH - 0.1, T_TUMBO + 0.1):
        fz = 1.32 + 0.02 * math.sin(t * 4); K(FASC, f, (PD.x - 0.98, PD.y + 0.5, fz), (0, 0.0, 0.12))
        k = 1 - ramp(t, T_ASS, T_ASS + 0.09); K(ASSOLTA, f, (PD.x - 0.98, PD.y + 0.44 - 1.2 * k, fz + 0.36), (0, 0.24, 0.12), scale=1.0 + 2.2 * k)
        k = 1 - ramp(t, T_QUATTRO, T_QUATTRO + 0.12); K(QUATTRO, f, (PD.x - 0.6, PD.y + 0.5, 2.62 + 0.04 * math.sin(t * 9)), (PI / 2, -0.06, 0), scale=0.78 * (1.0 + 0.8 * k))
    # il motorino: accanto a Gualtiero, poi davanti al banco col cartello «= 1 zucchina»
    if tra(t, T_GUA - 0.1, T_INCH + 0.1):
        if t < T_MOTO: K(MOTO['root'], f, (-2.75, -24.5, 0.03), (0, 0.0, -2.6))
        else: K(MOTO['root'], f, (0.85, -23.8, 0.03 + arco(t, T_MOTO, 0.25, 0.12)), (0, 0, 1.45)); K(TAGM, f, (0.8, -24.1, 1.1), (0, 0, 0.06), scale=0.85 * (1.0 + 0.6 * (1 - ramp(t, T_MOTO, T_MOTO + 0.15))))

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
emo(0.0, 'spaventato', 0.45, mouth_open=0.0); emo(2.3, 'sorpreso', 0.8); emo(T_POM, 'felice', 0.6); emo(T_EURO, 'spaventato', 1.0); emo(T_UNO, 'sorpreso', 1.0)
emo(T_MUTUO, 'triste', 0.5, look=(0, 0.3)); emo(T_30, 'spaventato', 1.0); emo(T_PER, 'triste', 1.0)
emo(T_ROSP, 'normale', 1.0); emo(T_GOLA + 0.4, 'sorpreso', 1.0); emo(T_MERDA, 'spaventato', 0.9); emo(T_MERDA + 0.5, 'ride', 0.8)
emo(T_ALLORA, 'furbo', 1.0); emo(T_ADD, 'felice', 0.5); emo(T_PELL, 'felice', 1.0)
emo(T_TUMBO, 'felice', 0.7); emo(T_MANGIA, 'sorpreso', 1.0); emo(T_GNAM, 'spaventato', 1.0); emo(T_ORA, 'triste', 1.0); emo(T_EPELL + 0.3, 'triste', 0.5, look=(0.8, 0)); emo(T_DOMANDA, 'sorpreso', 0.5, mouth_open=0.3)
tex(0.0, tongue=0.0, brow=0.0); tex(T_TUMBO, tongue=0.9, brow=0.4, look=(0, 0.8)); tex(T_MANGIA, tongue=0.0, brow=0.6); tex(T_GNAM + 0.35, tongue=0.6, brow=-0.2); tex(T_RATE, tongue=0.4, brow=-0.3, eye_open=0.45)

# ======================= effetti =======================
FXC = prc
def fx(name, pos, w, t0, dur, **k):
    try: return A.effetto(name, posizione=tuple(pos), larghezza=w, animazione=(fr(t0), int(dur * FPS)), collezione=FXC, **k)
    except Exception as e: print('effetto', name, e)
fx('emoticon/cash', TAGW + Vector((0.45, -0.1, 0.42)), 0.42, T_EURO + 0.1, 0.9)
fx('emoticon/exclamations', PM + Vector((0.35, 0.3, 2.45)), 0.45, T_UNO, 0.7)
fx('emoticon/drops', BKP + Vector((-0.4, -0.1, 2.3)), 0.4, T_30 + 0.05, 0.7)
fx('emoticon/cash', BKP + Vector((0.4, 0.4, 2.45)), 0.45, T_PER + 0.2, 1.2)
fx('emoticon/exclamation', RP + Vector((0.3, 0.3, RO_HZ + 0.75)), 0.4, T_CART - 0.05, 0.5)
fx('emoticon/swirl', RP + Vector((0.45, -0.2, RO_HZ + 0.6)), 0.5, T_MERDA + 0.2, 0.8)
fx('emoticon/idea', PW + Vector((0.3, -0.1, 2.5)), 0.5, T_LOGICA - 0.1, 0.8)
fx('emoticon/stars', SGB + Vector((-0.6, -0.4, 2.3)), 0.5, T_PELL, 0.8)
fx('emoticon/anger', V2P + Vector((0.2, -0.6, 2.4)), 0.5, T_PRESA + 0.1, 0.6)
fx('emoticon/hearts', Vector((-0.3, -24.9, 2.75)), 0.45, T_MOTO + 0.25, 0.8)
fx('emoticon/stars', PD + Vector((0.6, 0.4, RO_HZ + 0.8)), 0.5, T_CAZZO2, 0.6)
fx('emoticon/exclamations', GF + Vector((0.35, -0.3, 2.45)), 0.45, T_GNAM, 0.7)
fx('emoticon/heartbroken', GF + Vector((0.4, -0.3, 2.45)), 0.45, T_PIRLA, 0.8)
fx('emoticon/question', GF + Vector((0.0, -0.3, 2.6)), 0.55, T_DOMANDA + 0.1, 1.6)
for k in range(5): fx('schizzi/splat%02d' % (k * 4 + 1), GF + Vector((rnd.uniform(-0.3, 0.3), -0.75, 0.95 + rnd.uniform(0.0, 0.5))), rnd.uniform(0.25, 0.5), T_GNAM + 0.02 * k, 0.4, colore=(0.9, 0.08, 0.05), opacita=0.95)

# ======================= camera =======================
RH = RO_HZ
SHOTS = [  # t0, t1, camera da, a, mira da, a, lente, diaframma, pugno, mano
    (0.0, 2.3, (0.9, -27.0, 1.25), (0.6, -22.95, 1.5), (-0.2, -30.0, 1.45), (-0.2, -24.3, 1.6), 28, 5.6, 1.0, 1.0),                                   # 01 Pippo arriva col sacco dei soldi
    (2.3, T_POM, (0.35, -22.5, 1.95), (0.3, -22.7, 1.93), (-0.2, -24.3, PZ), (-0.2, -24.3, PZ), 42, 3.2, 1.0, 0.6),                                    # 02 la luce d'oro sulla faccia
    (T_POM, T_EURO, (-0.55, -23.85, 1.78), (-0.5, -23.7, 1.76), tuple(POMW), tuple(POMW), 40, 4.0, 1.25, 0.8),                                          # 03 un pomodoro
    (T_EURO, T_UNO, (0.5, -23.95, 1.74), (0.52, -23.9, 1.74), tuple(TAGW), tuple(TAGW), 24, 5.0, 1.25, 1.2),                                             # 04 undici euro
    (T_UNO, T_MUTUO, (-3.2, -26.6, 1.7), (-3.0, -26.3, 1.7), (0.0, -22.9, 1.5), (0.0, -22.9, 1.5), 28, 7.0, 1.0, 0.8),                             # 05 uno
    (T_MUTUO, T_30, (BX - 3.3, -5.6, 2.3), (BX - 3.0, -5.2, 2.25), (BX + 0.15, -0.4, 1.7), (BX + 0.15, -0.4, 1.7), 28, 6.0, 1.0, 0.7),                 # 06 la banca
    (T_30, T_PER, (BX + 0.95, -0.8, 2.15), (BX + 0.9, -0.75, 2.1), (BX, -0.08, 1.36), (BX, -0.08, 1.36), 35, 5.0, 1.0, 1.4),                           # 07 il timbro
    (T_PER, T_ROSP, (BX + 0.7, 0.75, 1.95), (BX + 0.65, 0.6, 1.93), (BX, -1.45, PZ - 0.05), (BX, -1.45, PZ - 0.05), 35, 4.0, 1.0, 0.9),                # 08 per un pomodoro del cazzo
    (T_ROSP, T_CARO, (1.7, -29.2, 1.3), (1.6, -27.8, 1.5), (4.4, -24.4, 1.3), (1.5, -23.9, 1.4), 38, 8.0, 1.0, 0.8),                                   # 09 arriva Rospina
    (T_CARO, T_VEDE, (1.75, -26.2, RH - 0.25), (1.7, -25.9, RH - 0.22), (1.5, -23.9, RH + 0.02), (1.5, -23.9, RH + 0.02), 40, 5.6, 1.0, 0.9),          # 10 il caro vita non esiste
    (T_VEDE, T_GOLA, (1.3, -25.7, 1.95), (1.3, -25.45, 1.95), tuple(TAGW), tuple(TAGW), 40, 8.0, 1.0, 0.8),                                 # 11 vede il cartellino
    (T_GOLA, T_MONT, (1.6, -26.6, RH - 0.1), (1.6, -26.9, RH + 0.1), (1.5, -23.9, RH - 0.3), (1.5, -23.9, RH - 0.05), 32, 6.0, 1.0, 1.0),              # 12 la gola come un canotto
    (T_MONT, T_ALLORA, (-3.6, -27.4, 1.5), (-3.4, -27.2, 1.5), (0.5, -23.8, 1.8), (0.5, -23.8, 1.7), 36, 7.0, 1.0, 1.0),                              # 13 quella montata
    (T_ALLORA, T_ADD, (-1.55, -26.3, PZ - 0.05), (-1.6, -25.6, PZ - 0.03), (-1.7, -23.7, PZ), (-1.7, -23.7, PZ), 40, 3.2, 1.0, 0.6),                   # 14 la cosa piu' logica
    (T_ADD, T_MANDA, (0.3, -4.1, 1.5), (0.3, -3.8, 1.5), (0.3, 1.0, 1.4), (0.3, 1.0, 1.4), 23, 7.0, 1.0, 0.8),                                        # 15 addestra un pellicano
    (T_MANDA, T_PICCHIA, (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), 32, 11, 1.0, 1.2),                                                              # 16 in volo (la camera lo segue)
    (T_PICCHIA, T_GUA, (2.9, -24.3, 1.3), (3.0, -24.1, 1.3), (5.7, -22.3, 1.9), (5.5, -22.5, 1.7), 24, 8.0, 1.0, 1.4),                                # 17 la picchiata sui pomodori
    (T_GUA, T_PAGA, (-0.8, -22.8, 1.9), (-0.82, -22.9, 1.88), (-1.0, -23.95, 1.8), (-1.0, -23.95, 1.8), 28, 3.5, 1.0, 0.7),                          # 18 Gualtiero taccagno
    (T_PAGA, T_MOTO, (-3.35, -22.6, 1.9), (-3.25, -22.7, 1.92), (-1.15, -24.0, 1.92), (-1.15, -24.0, 1.98), 38, 4.0, 1.0, 0.8),                             # 19 una zucchina
    (T_MOTO, T_INCH, (-0.2, -28.4, 1.5), (-0.2, -28.1, 1.5), (0.0, -24.0, 1.3), (0.0, -24.0, 1.3), 28, 7.0, 1.0, 0.9),                                 # 20 col motorino
    (T_INCH, T_ASSOLVE, (2.6, -29.8, 1.95), (2.65, -29.5, 1.95), (2.75, -25.6, 1.75), (2.75, -25.6, 1.75), 45, 6.0, 1.0, 0.7),                             # 21 l'inchiesta su se stessa
    (T_ASSOLVE, T_TUMBO, (2.55, -29.2, 1.8), (2.6, -29.0, 1.85), (2.62, -25.6, 1.9), (2.62, -25.6, 1.92), 26, 6.0, 1.15, 1.2),                           # 22 assolta in quattro secondi
    (T_TUMBO, T_MANGIA, (-0.4, 0.25, 0.85), (-0.34, 0.28, 0.88), (0.8, -0.12, 0.42), (0.72, -0.05, 0.44), 30, 3.5, 1.0, 0.7),                               # 23 Tumbo punta il pomodoro
    (T_MANGIA, T_ORA, (-1.7, -3.3, 1.25), (-1.6, -3.1, 1.25), (0.0, 0.5, 1.2), (0.0, 0.5, 1.2), 32, 6.0, 1.0, 1.4),                                    # 24 lo mangia
    (T_ORA, T_RATE, (0.15, -1.9, PZ - 0.1), (0.13, -1.6, PZ - 0.08), (0.0, 0.8, PZ - 0.02), (0.0, 0.8, PZ - 0.02), 40, 3.2, 1.0, 0.6),                 # 25 quel pirla
    (T_RATE, T_DOMANDA, (-1.9, -6.6, 1.0), (-0.6, -6.2, 1.25), (0.0, -1.5, 0.8), (0.5, 0.2, 1.2), 26, 8.0, 1.0, 0.8),                                  # 26 trent'anni di rate e un pellicano
    (T_DOMANDA, TOTAL + 0.1, (0.35, -5.6, 1.5), (0.35, -5.0, 1.5), (0.35, 0.6, 1.3), (0.35, 0.6, 1.3), 30, 8.0, 1.0, 0.6),                             # 27 mutuo o pellicano?
]
SHAKES = [(T_POM, 0.015, 0.3), (T_EURO, 0.02, 0.35), (T_30, 0.035, 0.35), (T_FISSO, 0.035, 0.35), (T_MERDA, 0.018, 0.4), (T_PRESA, 0.03, 0.4), (T_MOTO, 0.02, 0.3), (T_ASS, 0.035, 0.4), (T_GNAM, 0.03, 0.45)]
def hn(t, s): return 0.6 * math.sin(t * 1.7 + s) + 0.3 * math.sin(t * 3.3 + 2.1 * s) + 0.12 * math.sin(t * 7.9 + 3.7 * s)
for f in range(1, NF + 1):
    t = (f - 1) / FPS
    s_ = next((s for s in SHOTS if s[0] <= t < s[1]), SHOTS[-1]); u = sm((t - s_[0]) / (s_[1] - s_[0]))
    cl = Vector(lerp(s_[2], s_[3], u)); tl = Vector(lerp(s_[4], s_[5], u))
    if s_[0] == T_MANDA:                                               # in volo col pellicano: la camera gli sta davanti e sotto
        pl = pe(t); tl = pl['loc'] + Vector((0, 0, 1.0)); d_ = Vector((math.sin(pl['yaw']), -math.cos(pl['yaw']), 0)); cl = pl['loc'] + d_ * 2.4 + Vector((d_.y * 5.2, -d_.x * 5.2, 1.3))
    if s_[0] == T_ROSP: tl = rp(t)['loc'] + Vector((0, 0, 1.45))               # segue Rospina che arriva
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
json.dump([[round(s[0], 3), round(min(s[1], TOTAL), 3)] for s in SHOTS], open(os.path.join(os.path.dirname(os.path.abspath(BLEND)), 'shots.json'), 'w'))
bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(BLEND)); print('SAVED', BLEND, len(bpy.data.objects), 'oggetti')
