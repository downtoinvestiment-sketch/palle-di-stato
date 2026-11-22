# ===================================================================================================================
# Video 019 - IL DOPPIO GIOCO, 37,5 s. Si unisce alla testa: cat templates/head.py scripts/anim019_body.py > scripts/anim019.py
# Scelte dell'autore (17 novembre 2026): bomba A lunga SENZA faccia (niente occhi sugli oggetti), carro C militare,
# sottomarino F militare GIGANTE che esce da una piscina gonfiabile minuscola, armeria G in legno. Voce: copione 11 versione 1;
# Senza Giulia (richiesta dell'autore delle 14:02): il prete sposa le due bombe e nascono due bombine gemelle col ciuccio.
# Pippo usa SOLO le emozioni esagerate di pippo2. Luce «cinema» (sole basso di lato all'aperto, tre luci nell'armeria).
# Tempi presi da audio/words_t019.json.
# ===================================================================================================================
import props019, giulia, luci, random
import pippo2 as pippo
A = kitlook.A
BLEND = os.environ.get('BLEND019', '../t019/pippo_t019.blend')
FONT = A.font('luckiest')
Q = props019.mats019(); GM = giulia.mats_giulia(); M12 = props012.mats012()

# ======================= tempi (dalla voce) =======================
T_STACC = 2.52; T_BACK = 4.26                   # «sopra una staccionata»; «Tutto e' iniziato» (si torna indietro)
T_THROW = 4.9; T_LAND = 6.3                     # Pippo lancia la pallina, atterra da Gualtiero
T_GUAL = 6.66; T_STAB = 8.14                    # «Gualtiero la buca, con una forchetta»
T_WATER = 9.12; T_SPRAY = 10.2                  # «Pippo risponde con una pistola ad acqua»
T_BAZ = 11.46; T_FIRE = 12.32                   # «Gualtiero con un bazooka»
T_TANK = 13.18                                  # «Pippo compra un carro armato»
T_SUBG = 14.94; T_SUBUP = 16.78                 # «Gualtiero un sottomarino, nella piscina gonfiabile»
T_FINE = 18.42; T_BOMB = 19.48                  # «E alla fine la bomba atomica!»
T_TUTTI = 20.86                                 # «Tutti e due!»
T_MA = 21.96                                    # «Ma chi cazzo gliele vende?»
T_PRETE = 24.64; T_DOPPIO = 25.92               # «Il prete. Fa il doppio gioco.»
T_INC = 27.32; T_TOUCH = 28.1                   # «Le bombe si incontrano.»
T_FA = 28.74                                    # «E il prete fa l'unica cosa che sa fare.»
T_SPOSA = 31.66                                 # «Le sposa!»
T_NOVE = 33.04; T_GEM = 34.56; T_CLOSE = 35.6   # «Nove mesi dopo. Gemelli.»
T_END = 37.0                                    # nero e «pof»

# ======================= rendering e luce =======================
setup_render(scene, 1080, 1920, samples=5, fps=FPS, frames=NF); scene.frame_end = NF

camd = bpy.data.cameras.new('Cam'); cam = bpy.data.objects.new('Cam', camd); cac.objects.link(cam); scene.camera = cam
camd.clip_start = 0.03; camd.clip_end = 1500; camd.sensor_width = 36
tgt = empty('CamTarget', (0, 0, 1), None, cac)
ct = cam.constraints.new('TRACK_TO'); ct.target = tgt; ct.track_axis = 'TRACK_NEGATIVE_Z'; ct.up_axis = 'UP_Y'
camd.dof.use_dof = True; camd.dof.focus_object = tgt

kitlook.upgrade(scene, M, envc, prc, extras=False)
scene.eevee.taa_render_samples = 5
luci.cielo_basso(scene.world, 0.4)
scene.world.use_sun_shadow = False
SUN = luci.sole(prc, (0.35, -0.94), lato=1, energia=4.5)
luci.ombre_pulite(scene, mezza_risoluzione=True)
kitlook.variants('grass_medium_01', 12, (-14.0, -3.0, -7.5, 1.5), (0.14, 0.24), seed=4, coll=envc, shadow=False)
kitlook.variants('dandelion_01', 10, (-14.0, -3.0, -7.5, 1.5), (0.09, 0.15), seed=6, coll=envc, shadow=False)
for x in (-30, 14, 30): A.modello('street_lamp_01', posizione=(x, -8.15, 0.05), altezza=4.2, rotazione=90, collezione=envc)

# ======================= posti =======================
FX_ = -9.2                                       # la staccionata
L_B = 4.4; NOSE = 0.448 * L_B                    # bomba A: punta a 0.448 L dal centro
BOMB_Y, BOMB_Z = -2.0, 6.0
P_HOOK = Vector((-6.5, -4.6, 0)); T_HOOKP = Vector((-5.6, -5.1, 0)); G_HOOK = Vector((-12.3, -4.0, 0))
P_SPOT = Vector((-6.6, -2.4, 0)); T_SPOT = Vector((-5.8, -3.0, 0)); G_SPOT = Vector((-11.9, -2.2, 0))
GY_SPOT = Vector((-13.7, -1.0, 0)); GY_HAND = Vector((-12.8, -1.6, 0))
BALL_LAND = Vector((-11.35, -2.75, 0.14))
POOL_C = Vector((-15.6, -6.4, 0)); G_POOL = Vector((-12.2, -4.2, 0))
TANK_A = Vector((9.0, -5.6, 0)); TANK_B = Vector((-1.5, -5.6, 0)); TANK_YAW = -PI / 2
BP_PAD = Vector((-4.6, -1.0, 1.4)); BG_PAD = Vector((-13.4, -1.0, 1.4))
P_LOOK = Vector((-6.9, -5.3, 0)); T_LOOK = Vector((-6.0, -5.7, 0)); G_LOOK = Vector((-11.6, -4.6, 0))
CRADLE = Vector((-8.0, -3.6, 0)); P_CR = Vector((-7.4, -2.45, 0)); G_CR = Vector((-10.0, -4.3, 0)); GY_END = Vector((-12.6, -2.2, 0))
RX = 600.0                                       # armeria (set lontano)

def qdir(d, rest=(0, 0, -1)): return Vector(rest).rotation_difference(Vector(d).normalized())
def yaw_to(a, b): return math.atan2(b[0] - a[0], -(b[1] - a[1]))
def walk(t, t0, t1, a, b):
    u = ramp(t, t0, t1); return a.lerp(b, u), (0.5 * math.sin(t * 11) if 0.0 < u < 1.0 else 0.0)

# ======================= oggetti =======================
BG = props019.bomba(prc, Q, 'A', 'GUALTIERO', FONT, L=L_B, lato=-1)
BP = props019.bomba(prc, Q, 'A', 'PIPPO', FONT, L=L_B, lato=1)
for B_ in (BG, BP):
    B_['root'].rotation_mode = 'XYZ'; B_['flame'] = props019.fiamma(prc, Q, B_['body'], -0.5 * L_B, s=L_B / 4.2)
VEIL = props019.velo(prc, Q, BG['body'], (NOSE * 0.62, 0, BG['R'] * 0.92), s=0.9)
PAPI = props019.papillon(prc, Q, BP['body'], (NOSE * 0.7, 0.0, BP['R'] * 0.98), s=1.1); PAPI.rotation_euler = (0, 0, PI)
TANK = props019.carro(prc, Q, 'C', FONT); TANK['root'].rotation_mode = 'XYZ'
POOL = props019.piscina(prc, Q); POOL['root'].location = tuple(POOL_C)
PERI = props019.periscopio(prc, Q, h=2.2); PERI.location = (POOL_C.x, POOL_C.y, -2.5)
SUB = props019.sottomarino(prc, Q, 'F', FONT); GSUB = 3.6
SUB_ROT = Euler((-0.6, 0, -0.4))
_ax = Vector((0, -1, 0)); _ax.rotate(SUB_ROT); SUB_AX = _ax.copy()                                # direzione della prua
_off = Vector((0, 1.9 * GSUB, 0)); _off.rotate(SUB_ROT)
SUB_FINAL = Vector((POOL_C.x, POOL_C.y, 0.3)) - _off
SUB['root'].scale = (GSUB,) * 3; SUB['root'].rotation_euler = SUB_ROT; SUB['root'].location = tuple(SUB_FINAL)
bpy.context.view_layer.update(); HATCH_W = SUB['hatch'].matrix_world.translation.copy()
ARM = props019.armeria(prc, Q, A, 'G', (RX, 0.0), FONT)
MOTO, MFACE, MWHEELS, MMOUTH = props012.moto(chc, M12); props012.moto_extras(chc, M12, MOTO, MFACE)
MOTO.rotation_mode = 'XYZ'; MMOUTH.scale = (0.08, 0.015, 0.04)
BOOK = props019.libretto(chc, Q, MFACE, (0, -0.45, -0.05), s=1.0)
TOP = ARM['counter_top']
REC_P = props019.scontrino(prc, Q, ARM['root'], (0.95, -1.05, TOP + 0.12), 'PIPPO', FONT, rot=(0.5, 0, 0.3))
REC_G = props019.scontrino(prc, Q, ARM['root'], (1.35, -1.08, TOP + 0.2), 'GUALTIERO', FONT, rot=(0.4, 0, -0.25))
BALL = props019.pallina(prc, Q); BALL.rotation_mode = 'XYZ'
CR = props019.culla(prc, Q, larghezza=2.2); CR.location = tuple(CRADLE); CR.rotation_euler = (0, 0, PI / 2)
TW = []
for k in range(2):
    b_ = props019.bombina(prc, Q, GM, 'A', naso=False, L=0.95, proprietario=('PIPPO', 'GUALTIERO')[k]); b_['root'].rotation_mode = 'XYZ'; TW.append(b_)
# fungo atomico rosa di cuori (dopo il bacio)
MP = dict(M12); MP['smoke'] = material('P19_fungo_rosa', (1.0, 0.55, 0.75), rough=1.0, emit=(1.0, 0.5, 0.7), emit_strength=0.8)
MP['fire'] = material('P19_fungo_fucsia', (1.0, 0.2, 0.5), rough=1.0, emit=(1.0, 0.2, 0.5), emit_strength=2.0)
MP['fire2'] = material('P19_fungo_cuore', (1.0, 0.85, 0.9), rough=1.0, emit=(1.0, 0.8, 0.9), emit_strength=3.0)
MUSH = props012.mushroom(prc, MP); MUSH.location = (FX_, 22.0, 0.0)
# Buio per i neri
bx('Buio', (1998, -2, -2), (2002, 2, 2), material('P19_buio', (0, 0, 0), rough=1.0), envc)

# ======================= personaggi =======================
P = pippo.build_pippo(chc); Tb = tumbo.build_tumbo(chc, scale=0.75); GU = props009.gualtiero(chc, G9)
for r in (P['root'], Tb['root'], GU['root']): r.rotation_mode = 'XYZ'
for nm in 'LR': P['shoulder' + nm].rotation_mode = 'QUATERNION'
for nm in ('shoulderL', 'shoulderR', 'hipL', 'hipR', 'head'): GU[nm].rotation_mode = 'XYZ'
HELMET = ball_('Casco', 1.0, (0, 0.03, 0.74), Q['army'], chc, parent=P['head'], sc=(0.47, 0.47, 0.24))
GOG = empty('Occhialini', (0, -0.42, 0.62), Tb['root'], chc)
for sx in (-1, 1): ball_('Occhialino', 0.09, (sx * 0.14, 0, 0), Q['glass'], chc, parent=GOG, sc=(1, 0.5, 1))
WGUN = props019.pistola_acqua(chc, Q, P['elbowR'], (0, -0.02, -0.1), s=1.2); WGUN.rotation_euler = (0, PI / 2, 0)
SOOT = empty('Fuliggine', (0, 0, 0), P['head'], chc)
for k, (x, y, z, r_) in enumerate(((-0.2, -0.36, 0.28, 0.1), (0.18, -0.37, 0.2, 0.09), (0.02, -0.4, 0.05, 0.08), (-0.3, -0.25, 0.45, 0.12), (0.3, -0.24, 0.5, 0.11))):
    ball_('Nerofumo', r_, (x, y, z), Q['dark'], chc, parent=SOOT, sc=(1, 0.35, 0.8))
FORK = props019.forchetta(chc, Q, GU['shoulderR'], (0, -0.1, -0.78), L=1.5); FORK.rotation_euler = (PI, 0, 0)
BALLG = props019.pallina(chc, Q); BALLG.parent = GU['shoulderL']; BALLG.location = (0, -0.12, -0.82)
BAZ_G = props019.bazooka(chc, Q, GU['root'], (0.3, 0.05, 1.72), s=1.0); BAZ_G.rotation_euler = (0, 0, -PI / 2)

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

BOMBS_ON = [(0.0, T_BACK), (T_FINE, T_NOVE)]
show_only(VEIL, [(T_SPOSA, T_NOVE)]); show_only(PAPI, [(T_SPOSA, T_NOVE)])
show(BG['root'], BOMBS_ON); show(BP['root'], BOMBS_ON)
show_only(HELMET, [(T_TANK, T_SUBG)]); show_only(GOG, [(T_TANK, T_SUBG)])
show_only(WGUN, [(T_WATER, T_BAZ + 0.9)]); show_only(SOOT, [(T_FIRE + 0.15, T_TANK)])
show_only(FORK, [(T_GUAL, T_WATER + 2.2)]); show_only(BALLG, [(T_GUAL + 0.4, T_WATER + 2.2)])
show_only(BAZ_G, [(T_BAZ + 0.15, T_TANK)])
show(TANK['root'], [(0.0, T_BACK), (T_TANK, T_NOVE)])
show(POOL['root'], [(0.0, T_BACK), (T_SUBG - 0.2, T_NOVE)])
show(PERI, [(T_SUBG, T_SUBUP + 0.1)])
show(SUB['root'], [(0.0, T_BACK), (T_SUBUP, T_NOVE)])
show(BALL, [(T_THROW - 0.6, T_GUAL + 0.4)])
show(CR, [(T_GEM - 0.1, TOTAL)])
for b_ in TW: show(b_['root'], [(T_GEM - 0.1, TOTAL)])
show(MUSH, [(T_SPOSA + 0.15, T_NOVE)])
show_only(BOOK, [(T_FA + 0.9, T_NOVE)])
show(MOTO, [(T_PRETE - 0.1, T_INC), (T_FA, T_NOVE)])
show_only(REC_P, [(T_DOPPIO, T_INC)]); show_only(REC_G, [(T_DOPPIO + 0.12, T_INC)])
# l'armeria si vede solo quando serve (gli oggetti lontani costano lo stesso)
bpy.context.view_layer.update()
for o in list(prc.objects):
    if o.parent is None and abs(o.location.x - RX) < 20 and o.name not in NEVER: show(o, [(T_PRETE - 0.1, T_INC)])
show(ARM['root'], [(T_PRETE - 0.1, T_INC)])
# le tre luci «cinema» dell'armeria: accese solo nell'armeria
LA = luci.cinema(prc, (RX, 0.4, 1.6), (RX + 0.6, -6.4, 1.6), distanza=4.5, lato=1)
for l_ in LA.values():
    e_ = l_.data.energy
    for (t_, v) in ((0.0, 0.0), (T_PRETE - 0.1, e_), (T_INC, 0.0)):
        l_.data.energy = v; l_.data.keyframe_insert('energy', frame=fr(t_))
    for fc in all_fcurves(l_.data):
        for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'

# ======================= bombe =======================
def bombs(t):
    """(locG, rotG, locP, rotP) delle due bombe."""
    hor = lambda gap, dz=0.0: ((FX_ - NOSE - gap / 2, BOMB_Y, BOMB_Z + dz), (0, 0.0, 0), (FX_ + NOSE + gap / 2, BOMB_Y, BOMB_Z - 0.15 + dz), (0, 0.0, PI))
    bob = 0.06 * math.sin(t * 5)
    if t < T_BACK: return hor(1.7 - 0.45 * ramp(t, 0, T_BACK), bob)
    if t < T_TUTTI:                                                                   # decollano in verticale dai due giardini
        u = ramp(t, T_FINE + 0.25, T_TUTTI - 0.05) ** 1.6; z = 8.5 * u
        return (BG_PAD.x, BG_PAD.y, BG_PAD.z + z), (0, -PI / 2, 0), (BP_PAD.x, BP_PAD.y, BP_PAD.z + z), (0, -PI / 2, PI)
    if t < T_INC: return hor(1.0, bob)
    if t < T_SPOSA:
        g = 1.0 * (1 - ramp(t, T_INC + 0.1, T_TOUCH)); return hor(max(0.0, g), bob * (1 - ramp(t, T_INC, T_TOUCH)))
    kiss = 0.35 * math.sin(PI * ramp(t, T_SPOSA - 0.05, T_SPOSA + 0.25))                # si tirano indietro e si danno il bacio
    return hor(kiss)

# ======================= pose =======================
ARMS_DOWN = dict(aL=(-0.14, 0, -1), aR=(0.14, 0, -1))
def braccia(nome, forza=1.0):
    b = pippo.EMOZIONI_FORTI[nome]['braccia']; return {'aL': tuple(Vector((0, 0, -1)).lerp(Vector(b[0]).normalized(), forza)), 'aR': tuple(Vector((0, 0, -1)).lerp(Vector(b[1]).normalized(), forza))}
def tank_pose(t):
    u = ramp(t, T_TANK, T_TANK + 1.2) if t >= T_TANK else 1.0
    return TANK_A.lerp(TANK_B, u), TANK_YAW
def tank_local(t, v):
    l_, y_ = tank_pose(t); w = Vector(v); w.rotate(Euler((0, 0, y_))); return Vector(l_) + w
G_HEAD = lambda: Vector((G_SPOT.x, G_SPOT.y, 1.9))

def pp(t):
    S_ = dict(loc=(0, 0, 0), yaw=0.0, lean=0.0, head=(0, 0, 0), hL=0.0, hR=0.0, **ARMS_DOWN)
    k = 0.03 * math.sin(t * 30)
    if t < T_BACK:                                                                       # hook: sotto le bombe, mani in testa
        S_.update(loc=tuple(P_HOOK), yaw=yaw_to(P_HOOK, (-4.0, -13.0)), aL=(-0.42 + k, -0.2, 0.9), aR=(0.42 - k, -0.2, 0.9), head=(-0.3, 0, 0))
    elif t < T_WATER:                                                                    # lancia la pallina oltre la staccionata
        y_ = yaw_to(P_SPOT, G_SPOT); wind = ramp(t, T_THROW - 0.5, T_THROW - 0.1); thr = ramp(t, T_THROW - 0.1, T_THROW + 0.12)
        aR = Vector((0.3, 0.6, 0.75)).lerp(Vector((0.1, -1.0, 0.45)), thr) if wind > 0 else Vector((0.14, 0, -1))
        if t > T_THROW + 0.6: aR = Vector((0.14, 0, -1))
        S_.update(loc=tuple(P_SPOT), yaw=y_, aR=tuple(aR), lean=0.15 * thr * (1 - ramp(t, T_THROW + 0.3, T_THROW + 0.6)))
        if t > T_STAB + 0.1: S_.update(**braccia('triste'))
    elif t < T_TANK:                                                                     # pistola ad acqua, poi il bazooka lo annerisce
        y_ = yaw_to(P_SPOT, G_SPOT); aim = ramp(t, T_WATER + 0.3, T_WATER + 0.6)
        S_.update(loc=tuple(P_SPOT), yaw=y_, aR=tuple(Vector((0.14, 0, -1)).lerp(Vector((0.05, -1.0, 0.18)), aim)))
        if t > T_FIRE + 0.1:
            u = ramp(t, T_FIRE + 0.1, T_FIRE + 0.3); S_.update(lean=-0.25 * u, aL=(-0.5, 0.3, 0.6), aR=(0.5, 0.3, 0.6), head=(-0.2, 0, 0))
    elif t < T_SUBG:                                                                     # nel carro armato
        h = tank_local(t, (0.35, 0.7, 2.65)); S_.update(loc=(h.x, h.y, h.z - 0.62), yaw=yaw_to(h, (2.0, -14.0)), aR=(0.4, -0.5, 0.75), aL=(-0.14, 0, -1))
    elif t < T_FINE:                                                                     # guarda il sottomarino dalla staccionata
        S_.update(loc=(-7.6, -3.9, 0), yaw=yaw_to((-7.6, -3.9), SUB_FINAL), head=(-0.25 * ramp(t, T_SUBUP, T_SUBUP + 0.4), 0, 0))
        if t > T_SUBUP + 0.3: S_.update(**braccia('spaventato'))
    elif t < T_MA:                                                                       # lancia la sua bomba: braccia al cielo
        S_.update(loc=tuple(P_LOOK), yaw=yaw_to(P_LOOK, (-6.0, -15.0)), head=(-0.3, 0, 0), aL=(-0.5, -0.1, 0.85), aR=(0.5, -0.1, 0.85))
    elif t < T_PRETE:                                                                    # si gira verso lo spettatore: «Ma chi c***o gliele vende?»
        u = ramp(t, T_MA, T_MA + 0.35); y0 = yaw_to(P_LOOK, (FX_, BOMB_Y)); y1 = yaw_to(P_LOOK, (-6.3, -8.0))
        S_.update(loc=tuple(P_LOOK), yaw=y0 + (y1 - y0) * u, head=(0.05, 0.18 * u, 0), aL=(-0.3, 0.05, -0.95), aR=(0.3, 0.05, -0.95))
    elif t < T_GEM - 0.2:                                                                # sotto le bombe; si copre gli occhi
        cov = ramp(t, T_FA + 0.1, T_FA + 0.4) * (1 - ramp(t, T_SPOSA - 0.1, T_SPOSA + 0.1))
        S_.update(loc=tuple(P_LOOK), yaw=yaw_to(P_LOOK, (-6.0, -15.0)), head=(-0.35 * (1 - cov), 0, 0))
        if cov > 0.5: S_.update(aL=(0.3, -0.75, 0.62), aR=(-0.3, -0.75, 0.62))
        elif t > T_SPOSA: S_.update(**braccia('sorpreso'))
        else: S_.update(aL=(-0.3, -0.2, 0.3), aR=(0.3, -0.2, 0.3))
    else:                                                                                # i gemelli: guarda Gualtiero, poi lo spettatore
        u = ramp(t, T_GEM + 0.6, T_GEM + 0.9)
        y0 = yaw_to(P_CR, G_CR); y1 = yaw_to(P_CR, (-3.5, -3.0))
        S_.update(loc=tuple(P_CR), yaw=y0 + (y1 - y0) * u, **braccia('spaventato', 0.8))
    return S_

JOLTS = [(T_STAB + 0.05, 0.12), (T_FIRE + 0.12, 0.3), (T_SUBUP + 0.3, 0.25), (T_SPOSA + 0.05, 0.2), (T_GEM + 0.5, 0.2)]
def jolt(S_, t):
    for (t0, h) in JOLTS:
        if t0 <= t < t0 + 0.42:
            u = (t - t0) / 0.42; l_ = S_['loc']; S_['loc'] = (l_[0], l_[1], l_[2] + h * math.sin(PI * u)); S_['lean'] = S_['lean'] - 0.12 * math.sin(PI * u)
            S_['head'] = (S_['head'][0] - 0.3 * math.sin(PI * u), S_['head'][1], S_['head'][2] + 0.15 * math.sin(3 * PI * u))
    return S_

def gp(t):
    """Gualtiero: posizione, yaw, spalle (euler), anche, testa, inclinazione."""
    S_ = dict(loc=(0, 0, 0), yaw=0.0, lean=0.0, sL=(0, 0, 0), sR=(0, 0, 0), hL=0.0, hR=0.0, head=(0, 0, 0))
    yP = yaw_to(G_SPOT, P_SPOT)
    if t < T_BACK:
        S_.update(loc=tuple(G_HOOK), yaw=yaw_to(G_HOOK, (-9.0, -14.0)), sL=(-2.8, 0, 0.2), sR=(-2.8, 0, -0.2), head=(-0.3, 0, 0))
    elif t < T_WATER:                                                                    # raccoglie la pallina e la buca con la forchetta, fissando Pippo
        bend = math.sin(PI * ramp(t, T_LAND + 0.15, T_GUAL + 0.45))
        stab = ramp(t, T_STAB - 0.5, T_STAB - 0.2) * (1 - ramp(t, T_STAB, T_STAB + 0.12))
        S_.update(loc=tuple(G_SPOT), yaw=yP, lean=0.45 * bend, sL=(-1.25 * ramp(t, T_GUAL + 0.4, T_GUAL + 0.7), 0, 0), sR=(-1.2 * ramp(t, T_GUAL + 0.5, T_GUAL + 0.9) - 1.2 * stab, 0, 0.15))
    elif t < T_BAZ:                                                                      # l'acqua in faccia
        sp = ramp(t, T_SPRAY + 0.15, T_SPRAY + 0.35)
        S_.update(loc=tuple(G_SPOT), yaw=yP, lean=-0.15 * sp, sL=(-1.3 * sp, 0, -0.5 * sp), sR=(-1.3 * sp, 0, 0.5 * sp), head=(-0.15 * sp, 0, 0))
    elif t < T_TANK:                                                                     # bazooka in spalla, rinculo
        rec = math.sin(PI * ramp(t, T_FIRE, T_FIRE + 0.35))
        S_.update(loc=tuple(G_SPOT), yaw=yP, lean=-0.22 * rec, sR=(-0.4 * ramp(t, T_BAZ + 0.2, T_BAZ + 0.4), 0, 0.9), sL=(-1.2 * ramp(t, T_BAZ, T_BAZ + 0.3), 0, -0.3))
    elif t < T_FINE:                                                                     # accanto alla piscina, fa il saluto militare
        sal = ramp(t, T_SUBG + 0.3, T_SUBG + 0.6)
        S_.update(loc=tuple(G_POOL), yaw=yaw_to(G_POOL, (-6.0, -12.0)), sR=(-2.3 * sal, 0, 0.9 * sal))
    elif t < T_GEM - 0.2:
        S_.update(loc=tuple(G_LOOK), yaw=yaw_to(G_LOOK, (-9.0, -14.0)), head=(-0.3, 0, 0), sL=(-2.7, 0, 0.2), sR=(-2.7, 0, -0.2))
    else:
        S_.update(loc=tuple(G_CR), yaw=yaw_to(G_CR, P_CR) if t < T_GEM + 0.7 else yaw_to(G_CR, (-3.5, -3.0)), sL=(-0.5, 0, -0.4), sR=(-0.5, 0, 0.4))
    return S_

def tp(t):
    """Tumbo: (posizione, yaw, ritto 0..1)."""
    if t < T_BACK: return T_HOOKP, yaw_to(T_HOOKP, (FX_, BOMB_Y)), 0.0
    if t < T_WATER:
        p, w = walk(t, T_THROW + 0.1, T_LAND, T_SPOT, Vector((FX_ + 0.45, -2.9, 0))); return p, yaw_to(T_SPOT, (FX_, -2.9)), 0.6 * ramp(t, T_LAND, T_LAND + 0.2)
    if t < T_TANK: return T_SPOT, yaw_to(T_SPOT, G_SPOT), 0.0
    if t < T_SUBG: return tank_local(t, (0.75, -1.75, 1.7)), yaw_to(tank_local(t, (0, 0, 0)), (2.0, -14.0)), 0.0
    if t < T_FINE: return Vector((-6.9, -4.5, 0)), yaw_to((-6.9, -4.5), SUB_FINAL), 0.0
    if t < T_GEM - 0.2: return T_LOOK, yaw_to(T_LOOK, (-6.0, -15.0)), 0.0
    return Vector((-7.1, -5.3, 0)), yaw_to((-7.1, -5.3), CRADLE), 0.0

# ======================= chiavi =======================
def K(o, f, loc=None, rot=None, scale=None):
    if loc is not None: o.location = loc; o.keyframe_insert('location', frame=f)
    if rot is not None: o.rotation_euler = rot; o.keyframe_insert('rotation_euler', frame=f)
    if scale is not None: o.scale = scale if isinstance(scale, (tuple, list)) else (scale,) * 3; o.keyframe_insert('scale', frame=f)
def ball_pos(t):
    if t < T_THROW: return Vector((P_SPOT.x - 0.25, P_SPOT.y - 0.15, 1.5))
    u = ramp(t, T_THROW, T_LAND) if t < T_LAND else 1.0
    a = Vector((P_SPOT.x - 0.4, P_SPOT.y, 1.7)); b = BALL_LAND
    p = a.lerp(b, u); p.z += 3.2 * math.sin(PI * u)
    if t > T_LAND: p.z += 0.4 * abs(math.sin((t - T_LAND) * 9)) * max(0.0, 1 - (t - T_LAND) * 3)
    return p
for f in range(1, NF + 1):
    t = (f - 1) / FPS
    s = jolt(pp(t), t); K(P['root'], f, s['loc'], (s['lean'], 0, s['yaw']))
    for nm, k_ in (('L', 'aL'), ('R', 'aR')):
        sh = P['shoulder' + nm]; sh.rotation_quaternion = qdir(s[k_]); sh.keyframe_insert('rotation_quaternion', frame=f)
        K(P['hip' + nm], f, rot=(s['h' + nm], 0, 0))
    K(P['head'], f, rot=s['head'])
    g = gp(t); K(GU['root'], f, g['loc'], (g['lean'], 0, g['yaw']))
    K(GU['shoulderL'], f, rot=g['sL']); K(GU['shoulderR'], f, rot=g['sR']); K(GU['hipL'], f, rot=(g['hL'], 0, 0)); K(GU['hipR'], f, rot=(g['hR'], 0, 0)); K(GU['head'], f, rot=g['head'])
    l, yw, up = tp(t); K(Tb['root'], f, tuple(l), (-0.55 * up, 0, yw), 0.75)
    K(Tb['tail'], f, rot=(-1.0 + 0.2 * math.sin(t * 9), 0, 0.5 * math.sin(t * 12)))
    # bombe e fiamme
    lg, rg, lp, rp = bombs(t); K(BG['root'], f, lg, rg); K(BP['root'], f, lp, rp)
    for B_ in (BG, BP): K(B_['flame'], f, scale=(1.0 + 0.25 * math.sin(t * 40 + (0 if B_ is BG else 1.3)), 1, 1))
    # pallina: lanciata, poi in mano a Gualtiero (bucata: si sgonfia)
    K(BALL, f, tuple(ball_pos(t)), (t * 8, 0, 0))
    df = ramp(t, T_STAB + 0.05, T_STAB + 0.6); K(BALLG, f, scale=(1.0 + 0.3 * df, 1.0 + 0.3 * df, max(0.2, 1.0 - 0.8 * df)))
    # carro armato
    tl_, ty_ = tank_pose(t); K(TANK['root'], f, tuple(tl_), (0, 0, ty_))
    K(TANK['turret'], f, rot=(0, 0, 0.35 * math.sin(PI * ramp(t, T_TANK + 1.0, T_TANK + 1.7))))
    # periscopio, poi il sottomarino gigante che esce dalla piscina
    pe = ramp(t, T_SUBG + 0.4, T_SUBG + 1.0); K(PERI, f, (POOL_C.x, POOL_C.y, -2.5 + 2.4 * pe), (0, 0, 0.6 * math.sin(max(0.0, t - T_SUBG - 1.0) * 2.5)))
    su = ramp(t, T_SUBUP, T_SUBUP + 0.55) if t >= T_SUBUP else 1.0
    ov = 0.35 * math.sin(PI * ramp(t, T_SUBUP + 0.45, T_SUBUP + 0.85)) if t >= T_SUBUP else 0.0
    K(SUB['root'], f, tuple(SUB_FINAL - SUB_AX * (16.0 * (1 - su) - ov)))
    K(SUB['prop'], f, rot=(0, t * 9, 0))
    # moto-prete: in armeria conta i soldi; poi salta in cielo tra le due bombe
    if t < T_FA:
        K(MOTO, f, (RX - 0.35, 1.25, 0.35), (0, 0, 0.25 + 0.05 * math.sin(t * 7)), 1.35)
    else:
        u = ramp(t, T_FA + 0.1, T_FA + 1.1); a = Vector((FX_ + 1.5, -7.0, 0.0)); b = Vector((FX_, BOMB_Y - 1.6, BOMB_Z + 1.9))
        p = a.lerp(b, u); p.z += 2.5 * math.sin(PI * u); p.z += 0.08 * math.sin(t * 6) * ramp(t, T_FA + 1.1, T_FA + 1.4)
        K(MOTO, f, tuple(p), (-0.35 * math.sin(PI * u), 0, 0.0), 1.35)
    for w_ in MWHEELS: K(w_, f, rot=(t * 10 if t >= T_FA else 0.0, 0, 0))
    K(MMOUTH, f, scale=(0.08, 0.015, 0.04 + 0.03 * abs(math.sin(t * 14))) if T_PRETE < t < T_INC or T_SPOSA - 0.6 < t < T_SPOSA + 0.3 else (0.08, 0.015, 0.04))
    for k_, mn in enumerate(ARM['money']): K(mn, f, rot=(0, 0, 0.15 * k_ + (0.6 * math.sin(t * 16 + k_) if T_PRETE < t < T_DOPPIO else 0.0)))
    K(ARM['drawer'], f, (1.1, -0.88 - 0.38 * ramp(t, T_DOPPIO - 0.15, T_DOPPIO), TOP - 0.25))
    for k_, rc in enumerate((REC_P, REC_G)):
        u = ramp(t, T_DOPPIO + 0.12 * k_, T_DOPPIO + 0.12 * k_ + 0.18); K(rc, f, scale=max(0.01, u * (1 + 0.3 * math.sin(PI * u))))
    # fungo rosa dopo il bacio
    mu = ramp(t, T_SPOSA + 0.15, T_SPOSA + 1.3); K(MUSH, f, scale=max(0.01, 0.85 * mu))
    # culla: le bombine dondolano
    for k_, b_ in enumerate(TW):
        y_ = CRADLE.y + (-0.55 if k_ == 0 else 0.55); rk = 0.12 * math.sin(t * 5 + k_ * 1.4)
        K(b_['root'], f, (CRADLE.x, y_, 0.92), (rk - 0.7, 0, PI / 2))
    K(CR, f, rot=(0.03 * math.sin(t * 5), 0, PI / 2))

# ======================= espressioni =======================
_last = {}
def _ex(key, fn, t, k):
    if key in _last and t - 0.06 > _last[key][1]: fn(fr(t - 0.06), **_last[key][0])
    fn(fr(t), **k); _last[key] = (k, t)
_emo_last = [None]
def _emo_key(f, nome, forza):
    e = pippo.EMOZIONI_FORTI[nome]
    fa = {k: (tuple(x * forza for x in v) if isinstance(v, tuple) else v * forza) for k, v in e['faccia'].items()}
    pippo.express(P, f, **fa)
    if 'sopracciglia' in e:
        for (s_, nm), b in zip(((-1, 'L'), (1, 'R')), e['sopracciglia']):
            br = P['brow' + nm]; br.rotation_euler = (0, s_ * b * 0.45 * forza, 0); br.location.z = pippo.HEAD_C + 0.215 + 0.07 * max(0.0, -b) * forza
            br.keyframe_insert('rotation_euler', frame=f); br.keyframe_insert('location', index=2, frame=f)
    bx_, by_ = e.get('busto', (0, 0)); P['body'].rotation_euler = (bx_ * forza, by_ * forza, 0); P['body'].keyframe_insert('rotation_euler', frame=f)
    seg = pippo._segni(P)
    for k, g in seg.items():
        g.scale = (1, 1, 1) if (k in e.get('extra', ()) and forza > 0.3) else (0.001,) * 3
        g.keyframe_insert('scale', frame=f)
def emo(t, nome, forza=1.0):
    if _emo_last[0] and t - 0.06 > _emo_last[0][2]: _emo_key(fr(t - 0.06), _emo_last[0][0], _emo_last[0][1])
    _emo_key(fr(t), nome, forza); _emo_last[0] = (nome, forza, t)
def tex(t, **k): _ex('t', lambda f, **kk: tumbo.tumbo_express(Tb, f, **kk), t, k)
def gx(t, **k): _ex('g', lambda f, **kk: props009.gex(GU, f, **kk), t, k)
def jex(t, J, key, **k): _ex(key, lambda f, **kk: giulia.giex(J, f, **kk), t, k)
for k_ in range(7): emo(0.12 * k_, 'spaventato', 1.0 if k_ % 2 == 0 else 0.75)
emo(T_BACK, 'normale'); emo(T_THROW - 0.4, 'felice'); emo(T_LAND, 'normale')
emo(T_STAB - 0.4, 'sorpreso', 0.7); emo(T_STAB + 0.1, 'triste')
emo(T_WATER + 0.2, 'furbo'); emo(T_SPRAY, 'ride'); emo(T_BAZ + 0.1, 'sorpreso')
emo(T_FIRE + 0.12, 'spaventato'); emo(T_FIRE + 0.6, 'arrabbiato')
emo(T_TANK + 0.2, 'furbo'); emo(T_SUBG, 'sorpreso', 0.7); emo(T_SUBUP + 0.3, 'spaventato')
emo(T_FINE, 'arrabbiato', 0.8); emo(T_BOMB, 'ride'); emo(T_TUTTI, 'spaventato')
emo(T_MA + 0.2, 'furbo', 0.8); emo(T_MA + 1.0, 'arrabbiato', 0.6)
emo(T_INC, 'sorpreso'); emo(T_FA + 0.1, 'spaventato', 0.8); emo(T_SPOSA + 0.05, 'sorpreso'); emo(T_SPOSA + 0.7, 'felice')
emo(T_GEM - 0.2, 'sorpreso'); emo(T_GEM + 0.5, 'spaventato')
gx(0.0, brow=-0.5, mouth=0.7); gx(T_BACK, brow=0.0, mouth=0.0); gx(T_GUAL + 0.6, brow=0.8, mouth=0.05); gx(T_SPRAY + 0.2, brow=-0.4, mouth=0.6)
gx(T_BAZ + 0.4, brow=0.9, mouth=0.4); gx(T_SUBG, brow=0.6, mouth=0.3); gx(T_FINE, brow=0.7, mouth=0.8); gx(T_INC, brow=-0.4, mouth=0.6)
gx(T_GEM - 0.2, brow=-0.6, mouth=0.4)
tex(0.0, eye_open=1.0, tongue=0.0, eye_scale=1.15); tex(T_BACK, tongue=0.8, eye_scale=1.0); tex(T_STAB + 0.1, tongue=0.0, brow=-0.3)
tex(T_TANK, tongue=1.0, brow=0.0); tex(T_SUBUP, tongue=0.0, eye_scale=1.15); tex(T_FINE, eye_scale=1.0, tongue=0.8); tex(T_GEM, tongue=0.0, brow=-0.3)

# ======================= effetti =======================
FXC = prc
def fx(name, pos, w, t0, dur, **k): return A.effetto(name, posizione=tuple(pos), larghezza=w, animazione=(fr(t0), int(dur * FPS)), collezione=FXC, **k)
# acqua: goccioline lungo un arco dalla pistola alla faccia di Gualtiero
WATER = []
a_w = Vector((P_SPOT.x - 0.85, P_SPOT.y + 0.05, 1.45)); b_w = Vector((G_SPOT.x + 0.15, G_SPOT.y, 1.85))
for k in range(16):
    d_ = ball_('Goccia', 0.07, (0, 0, -50), Q['water'], prc, sc=(1.3, 1, 1)); WATER.append(d_)
for f in range(fr(T_SPRAY) - 1, fr(T_BAZ) + 1):
    t = (f - 1) / FPS
    for k, d_ in enumerate(WATER):
        u = ((t * 2.4) + k / 16.0) % 1.0
        on = T_SPRAY <= t < T_BAZ - 0.15
        p = a_w.lerp(b_w, u); p.z += 0.7 * math.sin(PI * u)
        d_.location = tuple(p) if on else (0, 0, -50); d_.keyframe_insert('location', frame=f)
for t_ in (T_SPRAY + 0.3, T_SPRAY + 0.7): fx('emoticon/drops', (G_SPOT.x, G_SPOT.y, 2.35), 0.5, t_, 0.5)
fx('esplosione/explosion03', (P_SPOT.x, P_SPOT.y, 1.2), 3.2, T_FIRE + 0.08, 0.7)
for k in range(5): fx('fumo_nero/blacksmoke%02d' % (k * 2), (P_SPOT.x + 0.2 * (k - 2), P_SPOT.y, 2.2 + 0.15 * k), 0.8, T_FIRE + 0.35 + 0.12 * k, 0.8, opacita=0.8)
for k in range(5): fx('sbuffo_bianco/whitepuff%02d' % (k * 3), (TANK_B.x + 2.6 - 0.4 * k, TANK_B.y + 0.3, 0.4), 1.4, T_TANK + 0.2 + 0.2 * k, 0.8, colore=(0.85, 0.8, 0.7), opacita=0.8)
for k in range(9):                                                                                      # il sottomarino esce dalla piscina: schizzi
    a_ = 2 * PI * k / 9; p_ = POOL_C + Vector((2.2 * math.cos(a_), 2.2 * math.sin(a_), 0.8))
    fx('sbuffo_bianco/whitepuff%02d' % (k * 2), p_, 2.4, T_SUBUP + 0.03 * k, 0.9, colore=(0.75, 0.9, 1.0), opacita=0.9)
for B_pad in (BG_PAD, BP_PAD):                                                                          # il decollo delle bombe
    for k in range(6): fx('sbuffo_bianco/whitepuff%02d' % (k * 3 + 1), B_pad + Vector((0.5 * (k - 2.5), 0, -1.0)), 2.6, T_FINE + 0.2 + 0.08 * k, 1.2, colore=(0.85, 0.82, 0.78), opacita=0.9)
fx('emoticon/hearts', (FX_, BOMB_Y + 0.4, BOMB_Z + 1.5), 1.2, T_TOUCH + 0.05, 0.9)
fx('emoticon/hearts', (FX_ + 1.6, BOMB_Y + 0.6, BOMB_Z + 2.8), 1.6, T_SPOSA + 0.1, 1.2)
rnd = random.Random(7)
for k in range(26):                                                                                     # coriandoli
    p_ = (FX_ + rnd.uniform(-4, 4), BOMB_Y - 1.0 + rnd.uniform(-1, 1), BOMB_Z + rnd.uniform(-1.5, 3.0))
    fx('particelle/star_0%d' % (k % 9 + 1), p_, 0.35, T_SPOSA + rnd.uniform(0, 0.9), 0.8, colore=random.Random(k).choice(((1, 0.3, 0.6), (1, 0.9, 0.2), (0.3, 0.8, 1), (0.6, 1, 0.4))), luce=2.0)
fx('emoticon/question', (P_LOOK.x + 0.55, P_LOOK.y, 2.5), 0.26, T_MA + 0.4, 1.0)
fx('emoticon/drop', (P_CR.x + 0.25, P_CR.y, 2.35), 0.35, T_GEM + 0.55, 1.2)
fx('emoticon/exclamations', (P_SPOT.x, P_SPOT.y, 2.6), 0.45, T_STAB + 0.05, 0.7)

# ======================= camera =======================
BC_ = Vector((FX_, BOMB_Y, BOMB_Z))
def bpos(t): return Vector(bombs(t)[0])
SHOTS = [  # t0, t1, camera da, a, mira da, a, lente, diaframma
    (0.0, T_STACC, (FX_ + 3.0, BOMB_Y - 12.6, 4.4), (FX_ + 2.4, BOMB_Y - 11.4, 4.6), (FX_, BOMB_Y, 6.4), (FX_, BOMB_Y, 6.3), 26, 12),            # 01 due bombe atomiche
    (T_STACC, T_BACK, (-3.8, -15.5, 1.3), (-4.0, -15.0, 1.4), (FX_ + 0.6, -2.0, 3.5), (FX_ + 0.6, -2.0, 3.6), 22, 14),                         # 02 sopra una staccionata
    (T_BACK, T_GUAL, (-4.6, -9.6, 1.7), (-5.0, -9.4, 1.7), (P_SPOT.x - 1.2, P_SPOT.y, 1.5), (FX_ - 1.5, -2.4, 1.6), 24, 10),                   # 03 la pallina
    (T_GUAL, T_WATER, (-8.3, -5.6, 1.75), (-8.5, -5.2, 1.75), (G_SPOT.x, G_SPOT.y, 1.45), (G_SPOT.x, G_SPOT.y, 1.65), 32, 6),                  # 04 la forchetta
    (T_WATER, T_BAZ, (-5.2, -7.0, 1.55), (-5.4, -6.8, 1.6), (FX_ + 0.6, -2.3, 1.6), (FX_ + 0.2, -2.3, 1.6), 24, 9),                           # 05 pistola ad acqua
    (T_BAZ, T_FIRE, (-10.0, -6.6, 1.7), (-10.2, -6.3, 1.7), (G_SPOT.x, G_SPOT.y, 1.6), (G_SPOT.x, G_SPOT.y, 1.65), 32, 6),                     # 06 il bazooka
    (T_FIRE, T_TANK, (-5.0, -5.9, 1.55), (-5.0, -5.6, 1.6), (P_SPOT.x, P_SPOT.y, 1.4), (P_SPOT.x, P_SPOT.y, 1.5), 30, 6),                      # 07 Pippo annerito
    (T_TANK, T_SUBG, (1.5, -11.6, 0.7), (1.2, -11.1, 0.75), (1.5, -5.6, 1.8), (-1.3, -5.6, 2.1), 24, 10),                                  # 08 carro armato
    (T_SUBG, T_SUBUP, (-10.6, -10.0, 1.5), (-10.8, -9.7, 1.5), (POOL_C.x + 0.6, POOL_C.y, 1.1), (POOL_C.x + 0.6, POOL_C.y, 1.5), 30, 9),      # 09 periscopio nella piscina
    (T_SUBUP, T_FINE, (-5.5, -15.5, 1.1), (-6.0, -15.0, 1.3), (-16.0, -8.5, 3.8), (-16.0, -8.5, 5.0), 22, 18),                                # 10 sottomarino gigante
    (T_FINE, T_TUTTI, (FX_ + 1.0, -15.5, 1.4), (FX_ + 1.0, -14.5, 1.8), (FX_, -1.0, 3.5), (FX_, -1.0, 8.0), 22, 16),                          # 11 la bomba atomica (decollo)
    (T_TUTTI, T_MA, (FX_ + 1.2, BOMB_Y - 11.5, 5.2), (FX_ + 0.9, BOMB_Y - 10.8, 5.4), (FX_, BOMB_Y, 6.0), (FX_, BOMB_Y, 6.1), 28, 11),  # 12 tutti e due
    (T_MA, T_PRETE, (P_LOOK.x + 0.35, P_LOOK.y - 2.6, 1.95), (P_LOOK.x + 0.3, P_LOOK.y - 2.25, 1.95), (P_LOOK.x, P_LOOK.y, 1.85), (P_LOOK.x, P_LOOK.y, 1.88), 38, 4),  # 13 Ma chi...
    (T_PRETE, T_INC, (RX + 0.6, -5.6, 1.7), (RX + 0.3, -3.9, 1.8), (RX, 0.9, 1.95), (RX - 0.2, 1.0, 1.8), 31, 6),                            # 14 il prete
    (T_INC, T_FA, (FX_, BOMB_Y - 11.0, 6.0), (FX_, BOMB_Y - 10.0, 6.0), tuple(BC_), tuple(BC_), 35, 11),                                     # 15 le bombe si incontrano
    (T_FA, T_SPOSA, (FX_ + 2.6, -17.0, 1.6), (FX_ + 2.3, -16.2, 1.8), (FX_, -2.0, 4.4), (FX_, -2.0, 6.6), 24, 14),                            # 16 il prete salta in cielo
    (T_SPOSA, T_NOVE, (FX_, BOMB_Y - 10.5, 6.4), (FX_, BOMB_Y - 12.5, 7.4), (FX_, BOMB_Y, 6.9), (FX_, BOMB_Y, 8.2), 30, 11),                   # 17 LE SPOSA
    (T_NOVE, T_GEM - 0.1, (2000, 0, 0), (2000, 0, 0), (2000, 1, 0), (2000, 1, 0), 30, 8),                                                     # 18 nove mesi dopo (nero)
    (T_GEM - 0.1, T_CLOSE, (-3.3, -3.75, 2.15), (-3.7, -3.75, 2.1), (CRADLE.x - 0.9, CRADLE.y, 1.15), (CRADLE.x - 0.9, CRADLE.y, 1.1), 26, 8),  # 19 gemelli
    (T_CLOSE, T_END, (CRADLE.x + 1.7, CRADLE.y, 3.1), (CRADLE.x + 1.35, CRADLE.y, 2.85), (CRADLE.x, CRADLE.y, 0.85), (CRADLE.x, CRADLE.y, 0.85), 22, 4),  # 20 primo piano sui gemelli
    (T_END, TOTAL + 0.1, (2000, 0, 0), (2000, 0, 0), (2000, 1, 0), (2000, 1, 0), 30, 8),                                                       # 21 nero, «pof»
]
for f in range(1, NF + 1):
    t = (f - 1) / FPS
    s_ = next((s for s in SHOTS if s[0] <= t < s[1]), SHOTS[-1]); u = sm((t - s_[0]) / (s_[1] - s_[0]))
    cl = Vector(lerp(s_[2], s_[3], u)); tl = Vector(lerp(s_[4], s_[5], u))
    if s_[0] == T_BACK and t > T_THROW: tl = tl.lerp(ball_pos(t), 0.5)                    # segue la pallina
    if s_[0] == T_SPOSA:                                                                   # scossone sul bacio
        sh_ = 0.12 * math.sin(t * 47) * (1 - ramp(t, T_SPOSA, T_SPOSA + 0.6)); cl = cl + Vector((sh_, 0, sh_ * 0.6))
    if s_[0] == T_FIRE:
        sh_ = 0.1 * math.sin(t * 53) * (1 - ramp(t, T_FIRE, T_FIRE + 0.5)); cl = cl + Vector((sh_, 0, sh_))
    cam.location = cl; tgt.location = tl; camd.lens = s_[6]; camd.dof.aperture_fstop = s_[7]
    cam.keyframe_insert('location', frame=f); tgt.keyframe_insert('location', frame=f); camd.keyframe_insert('lens', frame=f); camd.dof.keyframe_insert('aperture_fstop', frame=f)

def lin(idb):
    for fc in all_fcurves(idb):
        kind = 'CONSTANT' if 'hide' in fc.data_path else 'LINEAR'
        for kp in fc.keyframe_points: kp.interpolation = kind
for o in bpy.data.objects: lin(o)
set_interp(camd, 'CONSTANT')
for nm in ('Cam', 'CamTarget'):
    for fc in all_fcurves(bpy.data.objects[nm]):
        for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'
for l_ in LA.values():
    for fc in all_fcurves(l_.data):
        for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'
try: scene.render.use_motion_blur = True; scene.render.motion_blur_shutter = 0.06
except Exception: pass
os.makedirs(os.path.dirname(os.path.abspath(BLEND)), exist_ok=True)
import json; json.dump([[round(s[0], 3), round(min(s[1], TOTAL), 3)] for s in SHOTS], open(os.path.join(os.path.dirname(os.path.abspath(BLEND)), 'shots.json'), 'w'))
bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(BLEND)); print('SAVED', BLEND, len(bpy.data.objects), 'oggetti')
