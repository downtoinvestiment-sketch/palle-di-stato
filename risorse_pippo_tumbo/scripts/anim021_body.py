# ===================================================================================================================
# Video 021 - L'ETCIU', 41,5 s. Si unisce alla testa: cat templates/head.py scripts/anim021_body.py > scripts/anim021.py
# Scelte dell'autore (17 novembre 2026): sole C «accecante» (props021.sole), camion A ribaltabile con il pepe sopra,
# lampadario H, sacco F, valigie G, quadro L, cuscino M. Quando il sole scende cambia tutto l'ambiente: brucia tutto,
# anche dietro le case lontane; la gente scappa con i capelli e il sedere in fiamme (cartone, niente di crudo).
# Pippo usa le emozioni esagerate di pippo2. Luce «cinema». Tempi presi da audio/words_t021.json.
# ===================================================================================================================
import props021, props017, luci, random
import pippo2 as pippo
A = kitlook.A
BLEND = os.environ.get('BLEND021', '../t021/pippo_t021.blend')
FONTP = A.font('luckiest'); FONT = bpy.data.fonts.load(FONTP)
M17 = props017.mats017()

# ======================= tempi (dalla voce) =======================
T_STARN = 4.12                                   # «ha uno starnuto bloccato del cazzo»
T_TRE = 6.56; T_PORCA = 8.0                      # «Da tre giorni.» «Porca puttana.»
T_SOLL = 9.64; T_NIENTE1 = 11.68                 # solletico con la coda; «niente»
T_PEPE = 12.58; T_BARAT = 13.46; T_SACCO = 14.48 # pepe, barattolo, sacco
T_CAMION = 15.40; T_NIENTE2 = 16.46              # «un CAMION!» «Niente.»
T_LACR = 17.42; T_SCOLA = 18.40                  # «Solo lacrime, scolapasta.»
T_SOLE = 19.46; T_ANZI = 20.74                   # «Allora guarda il sole.» «Anzi,»
T_CORDA = 21.4; T_TIRA1 = 22.62                  # «lo tira giu' con una corda!»
T_IMP = 22.98                                    # «Il quartiere prende fuoco.»: il sole sul tetto, tutto brucia
T_VAC = 23.9                                     # la casa di Gualtiero «IN VACANZA»
T_ETC = 24.60                                    # «ETCIU'!»
T_MA = 26.56; T_NASO = 27.86; T_VEST = 30.0      # «Ma che cazzo... Dal naso esce Gualtiero. In vestaglia.»
T_ABITA = 31.0                                   # «Ci abitava da tre giorni.» (dentro la narice)
T_VEDE = 33.26; T_RIENTRA = 34.54                # «Vede il quartiere in fiamme. E rientra.»
T_TUMBO = 36.44; T_TRAD = 38.78                  # «Tumbo lo segue. Col cuscino. Traditore di merda.»
T_END = 40.5
TOTAL = 41.5; NF = int(TOTAL * FPS)

# ======================= rendering e luce =======================
setup_render(scene, 1080, 1920, samples=4, fps=FPS, frames=NF); scene.frame_end = NF
camd = bpy.data.cameras.new('Cam'); cam = bpy.data.objects.new('Cam', camd); cac.objects.link(cam); scene.camera = cam
camd.clip_start = 0.01; camd.clip_end = 2000; camd.sensor_width = 36
tgt = empty('CamTarget', (0, 0, 1), None, cac)
ct = cam.constraints.new('TRACK_TO'); ct.target = tgt; ct.track_axis = 'TRACK_NEGATIVE_Z'; ct.up_axis = 'UP_Y'
camd.dof.use_dof = True; camd.dof.focus_object = tgt

kitlook.upgrade(scene, M, envc, prc, extras=False)
scene.eevee.taa_render_samples = 4
CIELO = luci.cielo_basso(scene.world, 0.4)
scene.world.use_sun_shadow = False
SUN = luci.sole(prc, (0.35, -0.94), lato=1, energia=4.5)
luci.ombre_pulite(scene, mezza_risoluzione=True)
props021.bagliore(scene, forza=0.3, soglia=1.3)
kitlook.variants('grass_medium_01', 12, (-4.0, 8.0, -7.5, 3.0), (0.14, 0.24), seed=4, coll=envc, shadow=False)
for x in (-22, 14, 32): A.modello('street_lamp_01', posizione=(x, -8.15, 0.05), altezza=4.2, rotazione=90, collezione=envc)

# ======================= posti =======================
P_SPOT = Vector((2.0, -4.5, 0)); T_SPOT = Vector((0.85, -4.9, 0))
HEADZ = 1.5 + 0.215 + 0.27                        # quota del naso di Pippo (circa)
NOSE = Vector((P_SPOT.x, P_SPOT.y - 0.36, 1.5 + 0.215))
SUN_SKY = Vector((-40.0, 190.0, 110.0)); SUN_ROOF = Vector((0.0, 11.0, 10.8)); SUN_R = 5.4
G_HOUSE = Vector((-17.5, 3.0, 0)); CART_VAC = Vector((-13.4, -1.2, 0))
FLAT = Vector((300.0, 0.0, 60.0))
TRUCK_STOP = Vector((P_SPOT.x + 4.4, P_SPOT.y + 0.1, 0)); TRUCK_IN = TRUCK_STOP + Vector((14.0, 0, 0))

# ======================= personaggi =======================
P = pippo.build_pippo(chc); Tb = tumbo.build_tumbo(chc, scale=0.75); GU = props009.gualtiero(chc, G9)
for r in (P['root'], Tb['root'], GU['root']): r.rotation_mode = 'XYZ'
for nm in 'LR': P['shoulder' + nm].rotation_mode = 'QUATERNION'
for nm in ('shoulderL', 'shoulderR', 'hipL', 'hipR', 'head'): GU[nm].rotation_mode = 'XYZ'
NS = props021.naso(chc, P['head'])
VEST = props021.vestaglia(chc, GU)
DOOR = props017.porticina(chc, M17, NS['bulbo'], (0.033, -0.088, -0.03), font=FONT)
DOOR['root'].scale = (0.16,) * 3; DOOR['sign'].location = (0, -0.07, 0.32)
for o in DOOR['sign'].children_recursive:
    if o.type == 'FONT': o.data.body = 'AL COMPLETO'; o.data.size *= 0.82
ZERB = obj('ZerbinoGeo', set004.box_c(), (0.0, -0.15, -0.135), (0.34, 0.2, 0.015), material('P21_zerbino', (0.55, 0.38, 0.2), rough=0.95), chc, parent=DOOR['root'])
SUIT = []
for k in range(2):
    s_ = A.modello('vintage_suitcase', posizione=(0, 0, 0), altezza=0.38, collezione=chc, appoggia=True); SUIT.append(s_)
PIL = A.modello('throw_pillows_01', posizione=(0, 0, 0), altezza=0.35, collezione=chc, appoggia=True)
JAR = A.modello('kenney/food-kit/shaker-pepper', posizione=(0, 0, 0), altezza=0.2, collezione=chc, appoggia=True)
SACK = A.modello('kaykit/medieval-hexagon-pack/sack', posizione=(0, 0, 0), altezza=0.75, collezione=chc, appoggia=True)
BOX = bx('Cassa', (T_SPOT.x - 0.45, P_SPOT.y - 0.65, 0), (T_SPOT.x + 0.45, P_SPOT.y + 0.25, 1.05), A.materiale('brown_planks_03', dimensione=1.0), prc)
CAL = props021.calendario3(prc, (P_SPOT.x - 1.25, P_SPOT.y + 0.05, 1.45), font=FONT)
PALO = cyl('PaloCal', 0.05, 1.45, (P_SPOT.x - 1.25, P_SPOT.y + 0.1, 0.72), M['frame'], prc)
TR, TBED, TLOAD = props021.camion_pepe(prc, G9)
HEAP = props021.mucchio_pepe(prc, 1.25); HEAP.location = (P_SPOT.x, P_SPOT.y, -0.05)
ROPE = props021.lazo(prc)
CART = props021.cartello_vacanza(prc, FONT); CART.location = CART_VAC; CART.rotation_euler = (0, 0, -0.5); CART.scale = (1.6,) * 3

# ======================= il sole (scelta C) e l'inferno =======================
SOL = props021.sole(prc, tuple(SUN_SKY), SUN_R, 'C', luce=0.0, forza=6.5, alone=1.6)
SOL['luce'].data.use_shadow = False
DOME = props021.cupola_inferno(prc)
ASH = props021.terra_bruciata(prc)
INF = []                                                                                      # tutto quello che brucia
rnd = random.Random(21)
VICINI = [(-17.5, 3.0, 6.2), (-15.0, 6.0, 0), (9.5, 4.0, 3.8), (10.0, -5.5, 3.0), (-13.0, 9.5, 3.6), (5.5, 15.5, 4.0), (-7, 16.5, 4.0), (16, 14, 3.8),
          (3.4, 7.4, 4.9), (-3.0, 7.5, 4.6), (-7.5, -1.5, 0), (8.5, -2.0, 0), (0.6, -1.6, 0), (6.5, 2.0, 0), (3.9, -1.1, 0), (22.0, 6.0, 5.0), (22.5, -2.0, 4.5), (-27.0, -1.0, 6.0),
          (-21, -6.0, 3.5), (14, -19, 3.5), (-24, -19, 3.5), (-4.5, -15.5, 0), (9.0, -15.0, 0)]
for k, p in enumerate(VICINI):
    INF += props021.rogo(prc, p, rnd.uniform(1.5, 2.3), 100 + k, 900.0 if k < 12 else 0.0, 'Incendio%d' % k)
for x in range(-34, 44, 9):                                                                   # le file di case lontane, davanti e dietro
    INF += props021.rogo(prc, (x + rnd.uniform(-1.5, 1.5), 28.5 + rnd.uniform(0, 2), 5.0), rnd.uniform(2.2, 3.0), 200 + x, 0.0, 'IncN%d' % x, n=3)
    INF += props021.rogo(prc, (x + rnd.uniform(-1.5, 1.5), -36 - rnd.uniform(0, 2), 5.0), rnd.uniform(2.2, 3.0), 300 + x, 0.0, 'IncS%d' % x, n=3)
for x in range(-48, 56, 11):                                                                  # i palazzi in fondo e il fuoco dietro le case lontane
    INF += props021.rogo(prc, (x + 2, 44 + rnd.uniform(0, 3), rnd.uniform(9, 18)), rnd.uniform(3.0, 4.5), 400 + x, 0.0, 'IncP%d' % x, n=3)
    INF += props021.rogo(prc, (x + rnd.uniform(-3, 3), 34 + rnd.uniform(0, 3), 0.0), rnd.uniform(5.0, 7.0), 500 + x, 0.0, 'IncD%d' % x, n=3)
    INF += props021.rogo(prc, (x + 4, -50 - rnd.uniform(0, 3), rnd.uniform(9, 18)), rnd.uniform(3.0, 4.5), 600 + x, 0.0, 'IncPs%d' % x, n=3)
for y in range(-30, 36, 11):
    INF += props021.rogo(prc, (41 + rnd.uniform(0, 2), y, rnd.uniform(8, 16)), rnd.uniform(3.0, 4.0), 700 + y, 0.0, 'IncE%d' % y, n=3)
    INF += props021.rogo(prc, (-43 - rnd.uniform(0, 2), y, rnd.uniform(8, 16)), rnd.uniform(3.0, 4.0), 800 + y, 0.0, 'IncW%d' % y, n=3)
for k, p in enumerate([v for v in VICINI[:12] if abs(v[0]) > 4] + [(x, 30, 6) for x in range(-30, 40, 12)] + [(x, 46, 20) for x in range(-40, 50, 16)]):
    INF.append(A.effetto('fumo_nero/blacksmoke0%d' % (k % 9), posizione=(p[0] + rnd.uniform(-1, 1), p[1] + 0.5, p[2] + 9), larghezza=rnd.uniform(9, 14), opacita=0.8, collezione=prc))
COMP = []                                                                                     # la gente che scappa in fiamme: (dati, da, a, partenza, velocita')
for k, (a, b, t0) in enumerate((((-8.0, -6.5), (9.0, -7.0), 0.0), ((7.5, -2.0), (-6.0, -1.0), 0.3), ((-4.0, 2.5), (8.0, 1.5), 0.1), ((9.0, -10.0), (-12.0, -10.5), 0.5),
                                 ((-14.0, -5.5), (-20.0, -1.0), 0.2), ((-18.0, -2.5), (-10.0, -4.5), 0.0), ((-12.0, 6.0), (-14.0, -6.0), 0.4))):
    C_ = props021.comparsa(A, chc, (a[0], a[1], 0), 0.0, seme=k, fase=k * 1.1, nome='Comp%d' % k)
    COMP.append((C_, Vector((a[0], a[1], 0)), Vector((b[0], b[1], 0)), t0))
FLATR = props021.appartamento(A, prc, tuple(FLAT), font=FONT)
# richiesta dell'autore (19:49): uno che prende fuoco passa davanti alla camera per circa 2 secondi, urlando (scena dopo lo starnuto)
T_URLO0, T_URLO1 = T_ETC + 0.22, T_MA
URL = props021.comparsa(A, chc, (0, 0, 0), 0.0, seme=3, fase=0.5, nome='Urlatore'); URL_A = Vector((2.9, -12.0, 0)); URL_B = Vector((7.3, -12.6, 0))

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
AFTER = [(T_IMP, TOTAL + 1)]
for o in INF: show_only(o if o.parent is None else o, AFTER)
show_only(DOME, AFTER); show_only(ASH, AFTER)
for o_ in SOL.get('aloni', []): show_only(o_, [(0.0, T_IMP)])                  # l'alone del sole copriva le fiamme vicine: nell'inferno basta il bagliore
for C_, a, b, t0 in COMP: show_only(C_['radice'], AFTER)
show_only(CART, [(T_IMP, TOTAL + 1)]); show_only(URL['radice'], [(T_URLO0 - 0.05, T_MA)])
show_only(JAR, [(T_PEPE, T_SACCO)]); show_only(SACK, [(T_SACCO, T_CAMION + 0.5)])
show_only(HEAP, [(T_CAMION + 0.45, T_SOLE)])
show_only(TR, [(T_SACCO + 0.3, T_SOLE)])
show_only(BOX, [(T_SOLL - 0.2, T_PEPE)])
show_only(CAL, [(0.0, T_SOLL)]); show_only(PALO, [(0.0, T_SOLL)])
show_only(ROPE, [(T_ANZI + 0.25, T_IMP + 0.05)])
show_only(DOOR['root'], [(T_MA, TOTAL + 1)])
for s_ in SUIT: show_only(s_, [(T_NASO + 0.3, T_RIENTRA + 1.0)])
show_only(PIL, [(T_TUMBO - 0.4, TOTAL + 1)])
show(GU['root'], [(T_NASO + 0.2, T_RIENTRA + 1.0)])
show_only(VEST, [(T_NASO + 0.2, T_RIENTRA + 1.0)])
show(FLATR, [(T_ABITA - 0.1, T_VEDE)])
for o in list(prc.objects):
    if o.parent is None and (o.location - FLAT).length < 8 and o.name not in NEVER: show(o, [(T_ABITA - 0.1, T_VEDE)])

# ======================= il cambio dell'ambiente =======================
SUN.data.energy = 4.5; SUN.data.keyframe_insert('energy', frame=fr(T_IMP - 0.05)); SUN.data.energy = 0.6; SUN.data.keyframe_insert('energy', frame=fr(T_IMP))
SUN.data.color = (1, 0.96, 0.9); SUN.data.keyframe_insert('color', frame=fr(T_IMP - 0.05)); SUN.data.color = (1.0, 0.45, 0.2); SUN.data.keyframe_insert('color', frame=fr(T_IMP))
CIELO.inputs['Strength'].default_value = 0.4; CIELO.inputs['Strength'].keyframe_insert('default_value', frame=fr(T_IMP - 0.05))
CIELO.inputs['Strength'].default_value = 0.06; CIELO.inputs['Strength'].keyframe_insert('default_value', frame=fr(T_IMP))
SOL['luce'].data.energy = 0.0; SOL['luce'].data.keyframe_insert('energy', frame=fr(T_IMP - 0.3))
SOL['luce'].data.energy = 30000.0; SOL['luce'].data.keyframe_insert('energy', frame=fr(T_IMP))
scene.view_settings.exposure = 0.25; scene.view_settings.keyframe_insert('exposure', frame=fr(T_IMP - 0.05))
scene.view_settings.exposure = -0.35; scene.view_settings.keyframe_insert('exposure', frame=fr(T_IMP))

# ======================= pose =======================
def qdir(d, rest=(0, 0, -1)): return Vector(rest).rotation_difference(Vector(d).normalized())
def yaw_to(a, b): return math.atan2(b[0] - a[0], -(b[1] - a[1]))
ARMS_DOWN = dict(aL=(-0.14, 0, -1), aR=(0.14, 0, -1))
def braccia(nome, forza=1.0):
    b = pippo.EMOZIONI_FORTI[nome]['braccia']; return {'aL': tuple(Vector((0, 0, -1)).lerp(Vector(b[0]).normalized(), forza)), 'aR': tuple(Vector((0, 0, -1)).lerp(Vector(b[1]).normalized(), forza))}
def sun_pos(t):
    if t < T_CORDA: return SUN_SKY
    u = ramp(t, T_CORDA, T_IMP); u = u ** 2.2
    p = SUN_SKY.lerp(SUN_ROOF, u); return p
def hand_R(): return P_SPOT + Vector((0.45, -0.2, 2.15))

def pp(t):
    S_ = dict(loc=tuple(P_SPOT), yaw=0.0, lean=0.0, head=(0, 0, 0), body=(0, 0, 0), **ARMS_DOWN)
    trem = 0.03 * math.sin(t * 38)
    if t < T_TRE:                                                                     # hook: starnuto che non esce, testa all'indietro
        back = 0.35 + 0.08 * math.sin(t * 3.1)
        S_.update(head=(-back - 0.15, trem, 0), lean=-0.14, aL=(-0.3, -0.85, 0.45), aR=(0.3, -0.85, 0.45))
    elif t < T_SOLL:                                                                  # trema; quasi parte e si ritira
        q = math.sin(PI * ramp(t, T_PORCA - 0.7, T_PORCA + 0.1)) if t < T_PORCA + 0.1 else 0.0
        S_.update(head=(-0.25 - 0.35 * q, trem, 0), lean=-0.1 - 0.1 * q, aL=(-0.3, -0.3, -0.6), aR=(0.3, -0.3, -0.6))
    elif t < T_PEPE:                                                                  # la coda di Tumbo nel naso
        S_.update(yaw=0.0, head=(-0.15, 0.05 * math.sin(t * 9), 0), aL=(-0.2, 0, -1), aR=(0.2, 0, -1))
    elif t < T_SACCO:                                                                 # annusa il barattolo
        S_.update(head=(0.1, 0, 0), aR=(-0.15, -0.85, 0.55), aL=(-0.14, 0, -1))
    elif t < T_CAMION + 0.45:                                                         # la faccia nel sacco
        S_.update(head=(0.25, 0, 0), lean=0.2, aL=(-0.35, -0.9, 0.1), aR=(0.35, -0.9, 0.1))
    elif t < T_SOLE:                                                                  # sepolto nel pepe fino al collo: piange
        S_.update(loc=(P_SPOT.x, P_SPOT.y, -0.55), head=(0.05, 0.08 * math.sin(t * 6), 0), aL=(-0.3, 0, -1), aR=(0.3, 0, -1))
    elif t < T_ANZI:                                                                  # guarda il sole: mano sugli occhi
        S_.update(head=(-0.55, 0, 0), aR=(0.1, -0.7, 0.75), aL=(-0.14, 0, -1))
    elif t < T_IMP:                                                                   # lancia il lazo e tira
        thr = ramp(t, T_ANZI, T_ANZI + 0.35)
        pull = ramp(t, T_CORDA, T_CORDA + 0.3)
        S_.update(head=(-0.4, 0, 0), aR=tuple(Vector((0.3, 0.2, 0.95)).lerp(Vector((0.25, -0.35, 0.9)), thr)), aL=tuple(Vector((-0.14, 0, -1)).lerp(Vector((-0.2, -0.4, 0.88)), pull)),
                  lean=0.28 * pull + 0.06 * math.sin(t * 14) * pull)
    elif t < T_ETC - 0.5:                                                             # l'inferno: panico
        S_.update(yaw=0.25 * math.sin(t * 3), **braccia('spaventato'))
    elif t < T_MA:                                                                    # carica... ETCIU'
        if t < T_ETC: u = ramp(t, T_ETC - 0.5, T_ETC); S_.update(head=(-0.6 * u, 0, 0), lean=-0.25 * u, aL=(-0.5, 0.2, 0.5), aR=(0.5, 0.2, 0.5))
        else:
            k_ = ramp(t, T_ETC, T_ETC + 0.08); r_ = ramp(t, T_ETC + 0.5, T_ETC + 1.2)
            S_.update(head=(0.55 * k_ * (1 - r_), 0, 0), lean=0.45 * k_ * (1 - r_), aL=(-0.6, 0.6, -0.3), aR=(0.6, 0.6, -0.3))
            S_['loc'] = (P_SPOT.x, P_SPOT.y + 0.35 * k_, 0.0)
    else:                                                                             # col naso gonfio, guarda in basso il naso (occhi storti)
        S_.update(loc=(P_SPOT.x, P_SPOT.y + 0.35, 0.0), head=(0.12, 0, 0), aL=(-0.14, 0, -1), aR=(0.14, 0, -1))
    return S_

def tp(t):
    """Tumbo: posizione, yaw, scala, zampe davanti alzate (0..1)."""
    if t < T_SOLL: return T_SPOT, yaw_to(T_SPOT, (T_SPOT.x, -12)), 0.75, 1.0 if t < T_TRE else 0.0      # zampe sulle orecchie
    if t < T_PEPE: return Vector((P_SPOT.x - 0.85, P_SPOT.y - 0.2, 1.05)), -PI / 2, 0.75, 0.0              # sulla cassa, sedere verso Pippo
    if t < T_ANZI: return T_SPOT + Vector((-0.8, -0.4, 0)), yaw_to(T_SPOT, (P_SPOT.x, P_SPOT.y)), 0.75, 0.0
    if t < T_ETC: return P_SPOT + Vector((-0.2, 0.75, 0)), yaw_to((P_SPOT.x, P_SPOT.y + 0.75), (P_SPOT.x, P_SPOT.y)), 0.75, 0.0   # tira Pippo per i pantaloni
    if t < T_TUMBO - 0.4:                                                                                     # vola via con lo starnuto
        u = ramp(t, T_ETC, T_ETC + 1.4); a = P_SPOT + Vector((-0.2, 0.75, 0)); b = P_SPOT + Vector((-6, 30, 25))
        p = a.lerp(b, u); p.z += 6 * math.sin(PI * min(u, 0.5)); return p, yaw_to(a, b) + 9 * u, 0.75, 1.0
    u = ramp(t, T_TUMBO - 0.4, T_TUMBO + 0.25); a = DOORW + Vector((0.22, -0.25, 0.55)); n_ = DOORW + Vector((0, -0.02, -0.04))
    if t < T_TUMBO + 0.25: return Vector((a.x, a.y, 3.8)).lerp(a, u), 0.0, 0.4, 0.0
    v = ramp(t, T_TUMBO + 0.25, T_TUMBO + 1.4); p = a.lerp(n_, v); p.z += 0.3 * math.sin(PI * v)
    return p, 0.0, 0.4 * (1 - v) + 0.02 * v, 0.0

def gp(t):
    """Gualtiero piccolissimo che esce dalla narice: (posizione locale alla porticina, yaw locale, scala)."""
    u = ramp(t, T_NASO + 0.2, T_NASO + 1.2)
    if t < T_VEDE: return (0.0, 0.08 - 0.25 * u, -0.13), 0.0, 1.0
    if t < T_RIENTRA: return (0.0, -0.17, -0.13), -PI / 2 * ramp(t, T_VEDE + 0.1, T_VEDE + 0.4), 1.0
    w = ramp(t, T_RIENTRA, T_RIENTRA + 0.9); return (0.0, -0.17 + 0.3 * w, -0.13), -PI / 2 + 1.5 * PI * ramp(t, T_RIENTRA, T_RIENTRA + 0.25), 1.0

# ======================= chiavi =======================
def K(o, f, loc=None, rot=None, scale=None):
    if loc is not None: o.location = loc; o.keyframe_insert('location', frame=f)
    if rot is not None: o.rotation_euler = rot; o.keyframe_insert('rotation_euler', frame=f)
    if scale is not None: o.scale = scale if isinstance(scale, (tuple, list)) else (scale,) * 3; o.keyframe_insert('scale', frame=f)
GU['root'].parent = DOOR['root']; GSC = 0.13                                              # Gualtiero (alto ~2,1) in scala porticina
for k, s_ in enumerate(SUIT): s_.parent = GU['root']
PIL.parent = Tb['head']; JAR.parent = P['elbowR']
VEST.hide_render = False
for f in range(1, NF + 1):
    t = (f - 1) / FPS
    s = pp(t); K(P['root'], f, s['loc'], (s['lean'], 0, s['yaw'])); K(P['head'], f, rot=s['head'])
    for nm, k_ in (('L', 'aL'), ('R', 'aR')):
        sh = P['shoulder' + nm]; sh.rotation_quaternion = qdir(s[k_]); sh.keyframe_insert('rotation_quaternion', frame=f)
    # naso: narici che si gonfiano sull'insulto; gonfio dopo lo starnuto
    fl = 1.0 + (0.35 * abs(math.sin(t * 7.5)) if t < T_TRE else 0.0) + (0.5 * math.sin(PI * ramp(t, T_PORCA - 0.7, T_PORCA + 0.1)) if T_TRE <= t < T_SOLL else 0.0)
    big = 1.0 + 1.6 * ramp(t, T_ETC + 0.02, T_ETC + 0.3)
    K(NS['bulbo'], f, scale=(big, big, big))
    for n_ in NS['narici']: K(n_, f, scale=(n_['base'][0] * fl, n_['base'][1] * fl, n_['base'][2] * fl))
    # porticina: si apre per Gualtiero, si chiude, si riapre per Tumbo
    op = ramp(t, T_NASO, T_NASO + 0.25) * (1 - ramp(t, T_RIENTRA + 0.85, T_RIENTRA + 1.05)) + ramp(t, T_TUMBO + 0.9, T_TUMBO + 1.05) * (1 - ramp(t, T_TUMBO + 1.45, T_TUMBO + 1.6))
    K(DOOR['leaf'], f, rot=(0, 0, -1.9 * op))
    sg = ramp(t, T_TUMBO + 1.7, T_TUMBO + 1.9); sg = sg * (1 + 0.25 * math.sin(PI * ramp(t, T_TUMBO + 1.9, T_TUMBO + 2.2)))
    K(DOOR['sign'], f, scale=(1.25 * sg if sg > 0 else 0.001,) * 3)

scene.frame_set(fr(T_MA + 1.5)); bpy.context.view_layer.update()
DOORW = DOOR['root'].matrix_world.translation.copy(); print('PORTICINA', tuple(round(v, 3) for v in DOORW))
for f in range(1, NF + 1):
    t = (f - 1) / FPS
    p_, y_, sc_, paw = tp(t); sit = paw if t < T_SOLL else 0.0
    K(Tb['root'], f, tuple(p_ + Vector((0, 0, 0.12 * sit))), (-0.95 * sit, 0, y_), sc_)
    for nm, sd in (('legFL', -1), ('legFR', 1)): K(Tb[nm], f, rot=(-2.5 * paw, 0, sd * 0.5 * paw))
    for nm, sd in (('earL', -1), ('earR', 1)): K(Tb[nm], f, rot=(0.9 * sit, 0, 0))
    wag = 0.6 * math.sin(t * 14)
    if T_SOLL <= t < T_PEPE: K(Tb['tail'], f, rot=(-1.08 + 0.06 * math.sin(t * 23), 0.535 + 0.06 * math.sin(t * 17), 0), scale=(1, 1, 2.1))
    else: K(Tb['tail'], f, rot=(-0.5, 0, wag), scale=(1, 1, 1))
    # Gualtiero
    gl, gy, _ = gp(t); K(GU['root'], f, gl, (0, 0, gy), GSC)
    for k, s_ in enumerate(SUIT):
        sd = -1 if k == 0 else 1; K(s_, f, (sd * 0.62, 0.0, 0.45), (0, 0, PI / 2))
    # il cuscino in bocca a Tumbo
    K(PIL, f, (0, -0.55, -0.12), (0, 0, 0))
    # barattolo e sacco
    K(JAR, f, (0, -0.05, -0.32), (PI, 0, 0))
    K(SACK, f, (P_SPOT.x, P_SPOT.y - 0.5, 1.2), (0.3, 0, 0))
    # camion: arriva in retromarcia, ribalta il cassone
    u = ramp(t, T_SACCO + 0.3, T_CAMION - 0.05); K(TR, f, tuple(TRUCK_IN.lerp(TRUCK_STOP, u)), (0, 0, PI / 2))
    K(TBED, f, rot=(-0.85 * ramp(t, T_CAMION - 0.05, T_CAMION + 0.35), 0, 0))
    K(TLOAD, f, scale=(1.2, 2.1, 1.5 * (1 - ramp(t, T_CAMION + 0.25, T_CAMION + 0.6)) + 0.001))
    hp = ramp(t, T_CAMION + 0.4, T_CAMION + 0.8); K(HEAP, f, scale=(1.0, 1.0, hp * 0.95 + 0.001))
    # il sole e la corda
    K(SOL['radice'], f, tuple(sun_pos(t))); props021.anima_sole(SOL, f, t)
    if T_ANZI + 0.25 <= t < T_IMP + 0.05:
        thr = ramp(t, T_ANZI + 0.25, T_CORDA); a = hand_R(); b = sun_pos(t) + Vector((0, 0, -SUN_R * 0.9))
        props021.tira_corda(ROPE, a, a.lerp(b, thr), f)
    # l'urlatore che attraversa l'inquadratura
    if T_URLO0 - 0.1 <= t <= T_URLO1 + 0.1:
        u = (t - T_URLO0) / (T_URLO1 - T_URLO0); K(URL['radice'], f, tuple(URL_A.lerp(URL_B, u)), (0, 0, yaw_to(URL_A, URL_B) - 0.5)); props021.corri(URL, f, t, 13.0)
    # comparse che corrono
    for C_, a, b, t0 in COMP:
        if t >= T_IMP - 0.1:
            L_ = (b - a).length; u = ((t - T_IMP + t0) * 3.2 / L_) % 1.0; p = a.lerp(b, u)
            K(C_['radice'], f, tuple(p), (0, 0, yaw_to(a, b)))
            props021.corri(C_, f, t)

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
    ex_ = list(e.get('extra', ())) + (['rabbia'] if extra and extra.get('brow') == -1.2 else [])
    for k, g in seg.items():
        g.scale = (1, 1, 1) if (k in ex_ and forza > 0.3) else (0.001,) * 3
        g.keyframe_insert('scale', frame=f)
ROSSO = set()
def emo(t, nome, forza=1.0, **extra):
    if _emo_last[0] and t - 0.06 > _emo_last[0][2]: _emo_key(fr(t - 0.06), _emo_last[0][0], _emo_last[0][1], _emo_last[0][3])
    _emo_key(fr(t), nome, forza, extra); _emo_last[0] = (nome, forza, t, extra)
def tex(t, **k): _ex('t', lambda f, **kk: tumbo.tumbo_express(Tb, f, **kk), t, k)
def gx(t, **k): _ex('g', lambda f, **kk: props009.gex(GU, f, **kk), t, k)
TRATT = dict(brow=-1.2, brow_lift=1.3, mouth_open=1.0, smile=-1.4)                        # lo starnuto trattenuto
emo(0.0, 'spaventato', 1.0, **TRATT); emo(T_TRE, 'triste', 0.7); emo(T_PORCA - 0.6, 'spaventato', 1.0, **TRATT); emo(T_PORCA + 0.15, 'arrabbiato', 0.8)
emo(T_SOLL, 'spaventato', 0.9, **TRATT); emo(T_NIENTE1, 'triste', 0.8)
emo(T_PEPE, 'spaventato', 0.9, **TRATT); emo(T_BARAT + 0.3, 'triste', 0.6); emo(T_SACCO, 'spaventato', 0.8)
emo(T_CAMION + 0.4, 'sorpreso'); emo(T_NIENTE2, 'triste', 1.0); emo(T_SCOLA, 'triste', 1.0)
emo(T_SOLE, 'arrabbiato', 0.6); emo(T_ANZI, 'furbo'); emo(T_CORDA, 'arrabbiato', 1.0)
emo(T_IMP, 'spaventato'); emo(T_ETC - 0.5, 'spaventato', 1.0, **TRATT); emo(T_ETC, 'sorpreso', 1.0, mouth_open=1.8)
emo(T_ETC + 0.8, 'felice', 0.8); emo(T_MA, 'sorpreso', 0.8, look=(0, -1)); emo(T_NASO + 0.4, 'spaventato', 0.8, look=(0, -1))
emo(T_ABITA + 2.0, 'sorpreso', 0.5, look=(0, -1)); emo(T_TUMBO + 0.3, 'sorpreso', 0.7, look=(0.6, -0.6)); emo(T_TRAD, 'triste', 1.0)
tex(0.0, brow=-0.5, eye_open=0.3); tex(T_TRE, brow=0.0, eye_open=1.0); tex(T_SOLL, brow=0.3, eye_open=0.55); tex(T_PEPE, eye_open=1.0, brow=0.0)
tex(T_ETC, eye_scale=1.3); tex(T_TUMBO, eye_scale=1.0, brow=-0.4)
gx(0.0, brow=0.2, mouth=0.25); gx(T_VEST, brow=0.5, mouth=0.1); gx(T_VEDE + 0.2, brow=-0.8, mouth=0.9); gx(T_RIENTRA, brow=0.6, mouth=0.0)

# ======================= effetti =======================
FXC = prc
def fx(name, pos, w, t0, dur, **k): return A.effetto(name, posizione=tuple(pos), larghezza=w, animazione=(fr(t0), int(dur * FPS)), collezione=FXC, **k)
HEADW = Vector((P_SPOT.x, P_SPOT.y, HEADZ))
for k in range(3): fx('sbuffo_bianco/whitepuff%02d' % (k * 4), HEADW + Vector((0, -0.6, -0.25)), 0.5, T_PORCA - 0.1 + 0.06 * k, 0.4, colore=(1, 1, 1), opacita=0.7)
for t_ in (T_BARAT + 0.15, T_SACCO + 0.25):
    for k in range(4): fx('particelle/dirt_0%d' % (k % 3 + 1), HEADW + Vector((0.2 * (k - 1.5), -0.6, -0.2)), 0.45, t_ + 0.05 * k, 0.5, colore=(0.1, 0.08, 0.06), opacita=0.9)
for k in range(10): fx('particelle/dirt_0%d' % (k % 3 + 1), (P_SPOT.x + random.Random(k).uniform(-1, 1), P_SPOT.y, 2.2 + 0.2 * k), 1.2, T_CAMION + 0.15 + 0.03 * k, 0.5, colore=(0.08, 0.06, 0.05))
TEARS = []                                                                                  # lacrime a fontana
mt = material('P21_lacrima', (0.45, 0.8, 1.0), rough=0.05, spec=1.0, emit=(0.3, 0.6, 1.0), emit_strength=0.6)
for k in range(24): TEARS.append(ball_('Lacrima', 0.035, (0, 0, -50), mt, prc))
for f in range(fr(T_NIENTE2) - 1, fr(T_SOLE) + 3):
    t = (f - 1) / FPS
    for k, d_ in enumerate(TEARS):
        u = ((t * 1.6) + k / 24.0) % 1.0; sd = -1 if k % 2 else 1; on = T_LACR - 0.2 <= t < T_SOLE
        e0 = Vector((P_SPOT.x + 0.13 * sd, P_SPOT.y - 0.27, HEADZ - 0.55 + 0.08)); p = e0 + Vector((sd * 0.9 * u, -0.25 * u, 0.6 * math.sin(PI * u) - 0.9 * u * u))
        d_.location = tuple(p) if on else (0, 0, -50); d_.keyframe_insert('location', frame=f)
for k in range(6): fx('esplosione/explosion0%d' % (k % 8), Vector((rnd.uniform(-12, 12), rnd.uniform(-2, 20), 2 + rnd.uniform(0, 4))), 8, T_IMP + 0.05 * k, 0.8)
for k in range(8):                                                                          # lo starnuto: vento verso la camera
    fx('sbuffo_bianco/whitepuff%02d' % (k * 2), HEADW + Vector((0.3 * (k - 4), -1.0 - 0.8 * k, -0.3)), 1.5 + 0.4 * k, T_ETC + 0.02 * k, 0.6, colore=(0.95, 0.95, 0.9), opacita=0.75)
for k in range(5): fx('emoticon/drops', HEADW + Vector((0.4 * (k - 2), -0.7, 0.1)), 0.4, T_ETC + 0.05, 0.6)
fx('emoticon/question', HEADW + Vector((0.5, -0.2, 0.55)), 0.3, T_MA + 0.2, 1.2)
fx('emoticon/exclamations', DOORW + Vector((0, -0.2, 0.12)), 0.06, T_VEDE + 0.25, 0.8)

# ======================= luce «cinema» su Pippo =======================
LC = luci.cinema(prc, (P_SPOT.x, P_SPOT.y, 1.6), (P_SPOT.x + 0.4, P_SPOT.y - 4.0, 1.6), distanza=3.5, lato=-1, forza=0.8)
LF = luci.cinema(prc, tuple(FLAT), tuple(FLAT + Vector((0, -5, 0.5))), distanza=3.0, lato=1, forza=0.5, nome='Flat')
for l_ in LF.values():
    e_ = l_.data.energy
    for (t_, v) in ((0.0, 0.0), (T_ABITA - 0.1, e_), (T_VEDE, 0.0)):
        l_.data.energy = v; l_.data.keyframe_insert('energy', frame=fr(t_))

# ======================= camera =======================
NOSEW = DOORW + Vector((-0.05, 0.05, 0.02))                                                    # il naso gonfio (dopo lo starnuto)
SHOTS = [  # t0, t1, camera da, a, mira da, a, lente, diaframma
    (0.0, T_STARN, (P_SPOT.x + 0.15, P_SPOT.y - 1.5, 1.75), (P_SPOT.x + 0.35, P_SPOT.y - 3.2, 1.45), tuple(HEADW), tuple(HEADW + Vector((0, 0, 0.4))), 32, 3.0),  # 01 primo piano che si allarga
    (T_STARN, T_TRE, (P_SPOT.x + 2.6, P_SPOT.y - 7.0, 0.8), (P_SPOT.x + 2.3, P_SPOT.y - 6.6, 0.85), (P_SPOT.x - 0.4, P_SPOT.y + 3, 3.4), (P_SPOT.x - 0.4, P_SPOT.y + 3, 3.6), 22, 9),  # 02 con Tumbo e la casa
    (T_TRE, T_PORCA - 0.3, (P_SPOT.x - 1.05, P_SPOT.y - 1.35, 1.5), (P_SPOT.x - 1.1, P_SPOT.y - 1.2, 1.5), (P_SPOT.x - 1.25, P_SPOT.y, 1.45), (P_SPOT.x - 1.25, P_SPOT.y, 1.45), 42, 2.4),  # 03 calendario
    (T_PORCA - 0.3, T_SOLL, (P_SPOT.x + 0.25, P_SPOT.y - 2.0, 1.75), (P_SPOT.x + 0.2, P_SPOT.y - 1.8, 1.75), tuple(HEADW), tuple(HEADW), 36, 3.0),  # 04 porca...
    (T_SOLL, T_PEPE, (P_SPOT.x - 2.3, P_SPOT.y - 1.6, 1.85), (P_SPOT.x - 2.1, P_SPOT.y - 1.4, 1.85), (P_SPOT.x - 0.5, P_SPOT.y - 0.2, 1.7), (P_SPOT.x - 0.5, P_SPOT.y - 0.2, 1.7), 30, 4.0),  # 05 la coda
    (T_PEPE, T_SACCO, (P_SPOT.x + 0.6, P_SPOT.y - 2.3, 1.75), (P_SPOT.x + 0.45, P_SPOT.y - 2.0, 1.75), tuple(HEADW + Vector((0, 0, -0.1))), tuple(HEADW + Vector((0, 0, -0.1))), 34, 3.5),  # 06 barattolo
    (T_SACCO, T_CAMION, (P_SPOT.x + 1.3, P_SPOT.y - 3.6, 1.6), (P_SPOT.x + 1.2, P_SPOT.y - 3.3, 1.6), (P_SPOT.x + 0.2, P_SPOT.y, 1.5), (P_SPOT.x + 0.2, P_SPOT.y, 1.5), 28, 5),  # 07 sacco
    (T_CAMION, T_NIENTE2, (P_SPOT.x - 3.2, P_SPOT.y - 10.5, 1.3), (P_SPOT.x - 3.4, P_SPOT.y - 10.0, 1.4), (P_SPOT.x + 2.2, P_SPOT.y, 1.8), (P_SPOT.x + 2.0, P_SPOT.y, 1.6), 20, 12),  # 08 CAMION
    (T_NIENTE2, T_SOLE, (P_SPOT.x + 0.5, P_SPOT.y - 3.0, 1.75), (P_SPOT.x + 0.4, P_SPOT.y - 2.6, 1.7), (P_SPOT.x, P_SPOT.y, 1.15), (P_SPOT.x, P_SPOT.y, 1.25), 30, 4),  # 09 lacrime
    (T_SOLE, T_ANZI, (P_SPOT.x + 0.9, P_SPOT.y - 2.4, 0.7), (P_SPOT.x + 0.8, P_SPOT.y - 2.3, 0.7), tuple(HEADW), tuple(HEADW + Vector((-2, 12, 9))), 24, 6),  # 10 guarda il sole
    (T_ANZI, T_IMP, (P_SPOT.x + 4.5, P_SPOT.y - 12.0, 0.9), (P_SPOT.x + 4.0, P_SPOT.y - 11.5, 1.0), (P_SPOT.x - 3, P_SPOT.y + 20, 16), (0.0, 6.0, 7.0), 18, 14),  # 11 il lazo
    (T_IMP, T_VAC, (3.6, -12.5, 1.3), (3.2, -12.9, 1.35), (0.0, 4.0, 6.2), (0.0, 4.0, 6.0), 22, 14),   # 12 il quartiere prende fuoco
    (T_VAC, T_ETC - 0.25, (-9.8, -7.0, 1.6), (-10.2, -6.8, 1.65), (-16.0, 2.0, 2.6), (-16.0, 2.0, 2.4), 26, 12),   # 13 IN VACANZA
    (T_ETC - 0.25, T_URLO0, (P_SPOT.x + 0.2, P_SPOT.y - 2.5, 1.7), (P_SPOT.x + 0.2, P_SPOT.y - 2.9, 1.7), tuple(HEADW), tuple(HEADW), 30, 4),  # 14 ETCIU'
    (T_URLO0, T_MA, (P_SPOT.x + 3.0, P_SPOT.y - 10.0, 0.45), (P_SPOT.x + 2.6, P_SPOT.y - 10.6, 0.5), (P_SPOT.x - 1, P_SPOT.y + 6, 4.5), (P_SPOT.x - 3, P_SPOT.y + 14, 9.0), 20, 14),  # 15 dopo lo starnuto
    (T_MA, T_ABITA, tuple(DOORW + Vector((0.08, -0.62, 0.06))), tuple(DOORW + Vector((0.1, -0.55, 0.02))), tuple(DOORW + Vector((-0.04, 0, 0.02))), tuple(DOORW + Vector((0, 0, -0.02))), 50, 2.8),  # 16 dal naso esce Gualtiero
    (T_ABITA, T_VEDE, tuple(FLAT + Vector((0.5, -2.6, 0.5))), tuple(FLAT + Vector((0.2, -2.0, 0.35))), tuple(FLAT + Vector((0, 1.5, 0.4))), tuple(FLAT + Vector((0, 1.8, 0.5))), 16, 6),  # 17 l'appartamento
    (T_VEDE, T_TUMBO - 0.5, tuple(DOORW + Vector((0.5, -0.14, 0.01))), tuple(DOORW + Vector((0.46, -0.16, 0.0))), tuple(DOORW + Vector((-0.4, -0.12, -0.05))), tuple(DOORW + Vector((-0.4, -0.12, -0.05))), 32, 4.5),  # 18 vede il quartiere in fiamme
    (T_TUMBO - 0.5, T_END, tuple(DOORW + Vector((0.0, -1.5, 0.12))), tuple(DOORW + Vector((0.0, -1.5, 0.12))), tuple(DOORW + Vector((-0.05, 0, 0.12))), tuple(DOORW + Vector((-0.05, 0, 0.12))), 34, 3.5),  # 19 Tumbo lo segue
    (T_END, TOTAL + 0.1, (2000, 0, 0), (2000, 0, 0), (2000, 1, 0), (2000, 1, 0), 30, 8),                     # 20 nero
]
SHAKES = [(T_CAMION + 0.35, 0.08, 0.6), (T_IMP, 0.35, 0.9), (T_ETC, 0.18, 0.7)]
for f in range(1, NF + 1):
    t = (f - 1) / FPS
    s_ = next((s for s in SHOTS if s[0] <= t < s[1]), SHOTS[-1]); u = sm((t - s_[0]) / (s_[1] - s_[0]))
    cl = Vector(lerp(s_[2], s_[3], u)); tl = Vector(lerp(s_[4], s_[5], u))
    if s_[0] == T_ANZI: tl = Vector(lerp(tl, sun_pos(t), 0.6))                              # segue il sole che scende
    for (t0, a_, d_) in SHAKES:
        if t0 <= t < t0 + d_:
            k = a_ * (1 - (t - t0) / d_); cl = cl + Vector((k * math.sin(t * 61), 0, k * 0.7 * math.sin(t * 47)))
    cam.location = cl; tgt.location = tl; camd.lens = s_[6]; camd.dof.aperture_fstop = s_[7]
    cam.keyframe_insert('location', frame=f); tgt.keyframe_insert('location', frame=f); camd.keyframe_insert('lens', frame=f); camd.dof.keyframe_insert('aperture_fstop', frame=f)

def lin(idb):
    for fc in all_fcurves(idb):
        kind = 'CONSTANT' if 'hide' in fc.data_path else 'LINEAR'
        for kp in fc.keyframe_points: kp.interpolation = kind
for o in bpy.data.objects: lin(o)
for d in (SUN.data, SOL['luce'].data, scene.world.node_tree): lin(d)
set_interp(camd, 'CONSTANT')
for nm in ('Cam', 'CamTarget'):
    for fc in all_fcurves(bpy.data.objects[nm]):
        for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'
for l_ in LF.values():
    for fc in all_fcurves(l_.data):
        for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'
try: scene.render.use_motion_blur = True; scene.render.motion_blur_shutter = 0.06
except Exception: pass
os.makedirs(os.path.dirname(os.path.abspath(BLEND)), exist_ok=True)
import json; json.dump([[round(s[0], 3), round(min(s[1], TOTAL), 3)] for s in SHOTS], open(os.path.join(os.path.dirname(os.path.abspath(BLEND)), 'shots.json'), 'w'))
bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(BLEND)); print('SAVED', BLEND, len(bpy.data.objects), 'oggetti')
