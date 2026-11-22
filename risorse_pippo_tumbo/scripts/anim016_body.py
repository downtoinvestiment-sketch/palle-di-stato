from props007 import text_obj
A = props013.mats013(); Z12 = props012.mats012(); H = props010.mats010(); W = props015.mats015(); B = props016b.mats016b()
HX0 = 1000.0; KX0 = 1100.0; HE = (0.0, 6.5)
# via la casa di Pippo: al suo posto l'ospedale
for o in list(envc.objects):
    if o.name.startswith('Casa') and abs(o.location.x) < 0.5 and abs(o.location.y - 9.5) < 0.5: bpy.data.objects.remove(o)
HEX = props015.hospital_ext(envc, W, HE[0], HE[1])
PILLOW = props013.hospital_set(envc, A, HX0)
CR = [(HX0 + 2.4, 0.9), (HX0 + 3.3, 0.9), (HX0 + 4.2, 0.9)]
for k, (x, y) in enumerate(CR[:2]): c_ = props015.crib(envc, W, 'Culla%d' % k); c_.location = (x, y, 0)
splight = props015.corridor(envc, W, KX0)
bx('SoffittoCorridoio', (KX0 - 6.2, -4.2, 3.0), (KX0 + 6.2, 1.8, 3.1), W['white'], envc)
shell = MB([W['cwall'], A['hfloor'], W['white']])
shell.b2((HX0 - 4.1, -7.5, -0.12), (HX0 + 6.6, 3.1, 0.0), 1); shell.b2((HX0 + 4.0, 3.0, 0.0), (HX0 + 6.6, 3.1, 3.3), 0); shell.b2((HX0 + 6.5, -7.5, 0.0), (HX0 + 6.6, 3.1, 3.3), 0)
shell.b2((HX0 - 4.1, -7.6, 0.0), (HX0 + 6.6, -7.5, 3.3), 0); shell.b2((HX0 - 4.1, -7.5, 0.0), (HX0 - 4.0, -4.0, 3.3), 0); shell.b2((HX0 - 4.1, -7.6, 3.2), (HX0 + 6.6, 3.1, 3.3), 2)
shell.b2((HX0 - 4.0, 2.95, 0.0), (HX0 + 6.5, 2.97, 0.12), 2); shell.build('StanzaParto', envc)
DOORP = props016b.door(envc, B, (HX0 + 6.44, -0.6, 0.0), rotz=PI / 2, label='USCITA')
props015.window(envc, W, (HX0 + 0.3, 2.97, 1.85), 1.3, 1.2)

# ======================= personaggi =======================
P = pippo.build_pippo(chc); Tb = tumbo.build_tumbo(chc, scale=0.75); TF = tumbo.build_tumbo(chc, scale=0.75)
Z = props012.zucchina(chc, Z12); Z2 = props012.zucchina(chc, Z12); GU = props009.gualtiero(chc, G9)
BZ1 = props012.zucchina(chc, Z12); BZ1['root'].scale = (0.36, 0.36, 0.36); BZ2 = props012.zucchina(chc, Z12); BZ2['root'].scale = (0.36, 0.36, 0.36)
DOC = props004.player(chc, 'Dottore', (0.30, 0.70, 0.60), (0.30, 0.70, 0.60), (0.96, 0.74, 0.6), (0.2, 0.13, 0.08), scale=1.0)
dhead = [c for c in DOC['root'].children if c.name.startswith('Head')][0]
cyl('DocCuffia', 0.29, 0.12, (0, 0.02, 0.2), W['scrubs'], chc, parent=dhead); ball_('DocMascherina', 1.0, (0, -0.24, -0.08), W['white'], chc, parent=dhead, sc=(0.17, 0.05, 0.1))
for r in (P['root'], Tb['root'], TF['root'], Z['root'], Z2['root'], GU['root'], BZ1['root'], BZ2['root'], DOC['root']): r.rotation_mode = 'XYZ'
for nm in 'LR': P['shoulder' + nm].rotation_mode = 'QUATERNION'
def qdir(d, rest=(0, 0, -1)): return Vector(rest).rotation_difference(Vector(d).normalized())
def yaw_to(a, b): return math.atan2(b[0] - a[0], -(b[1] - a[1]))

# ======================= oggetti =======================
FT = props016b.firetruck(prc, B, L=2.6); FTR = FT['root']; FTR.rotation_mode = 'XYZ'
PNO = props016b.piano(prc, B); PNO.rotation_mode = 'XYZ'
MEL = props016b.watermelon(chc, B, r=0.3); MEL.rotation_mode = 'XYZ'
sand = props015.sandwich(chc, W, P['root'], (0, -1.1, 0.55)); sand.scale = (8.0, 8.0, 8.0)
chips = props016b.chips_bag(chc, B, Z2['root'], (0.0, -0.2, 0.12), 1.0)
clip = props016b.clipboard(chc, B, DOC['shoulderR'], (0.05, -0.12, -0.72), 'NORMALE'); clip.rotation_euler = (1.2, 0, 0)
stool = cyl('Sgabello', 0.2, 0.75, (HX0 + 1.0, 0.95, 0.375), A['metal'], prc)
alim = empty('Alimenti', (HX0 - 0.15, -0.55, 0.82), None, prc); alim.rotation_euler = (0.2, 0, -0.35)
obj('AlimFoglio', set004.box_c(), (0, 0, 0), (0.42, 0.01, 0.3), B['paper'], prc, parent=alim); text_obj(prc, 'AlimT', 'ALIMENTI', 0.07, B['ink'], (0, -0.012, 0.0), parent=alim)
case_ = empty('ValigettaCocomero', (HX0 + 0.25, -0.15, 0.62), None, prc)
obj('ValCorpo2', set004.box_c(), (0, 0, 0.16), (0.46, 0.12, 0.32), H['case'], prc, parent=case_); obj('ValManico2', set004.box_c(), (0, 0, 0.35), (0.16, 0.03, 0.05), H['line'], prc, parent=case_)
tie_ = empty('CravattaCocomero', (HX0 - 0.7 + 0.25, -0.05 - 0.31, 0.98 + 0.1), None, prc)
obj('CravNodo2', set004.box_c(), (0, 0, 0), (0.07, 0.04, 0.06), H['tie'], prc, parent=tie_); obj('CravPala2', set004.box_c(), (0, -0.03, -0.14), (0.09, 0.025, 0.24), H['tie'], prc, rot=(0.25, 0, 0), parent=tie_)
# scotch sul costume da zucchina (indizio del travestimento)
for sx in (-1, 1): props016b.tape_patch(chc, B, Z['root'], (sx * 0.088, -0.128, 0.752), rot=(0, sx * 0.6, 0), size=(0.085, 0.008, 0.026))
props016b.tape_patch(chc, B, Z['root'], (0.0, -props012.ZR - 0.012, 0.528), size=(0.1, 0.008, 0.026))
belly = ball_('ZucPancia', 1.0, (0, -props012.ZR * 0.62, 0.36), Z12['zuc'], chc, parent=Z['root'], sc=(0.21, 0.19, 0.25))
def area(name, loc, size, energy, col=(1, 0.97, 0.92)):
    l_ = bpy.data.lights.new(name, 'AREA'); l_.size = size; l_.energy = energy; l_.color = col; o_ = bpy.data.objects.new(name, l_); prc.objects.link(o_); o_.location = loc; return o_
area('LuceOspedale', (HX0 + 1.0, -1.8, 3.1), 5.0, 520); area('LuceOspedale2', (HX0 + 3.6, -1.0, 3.1), 3.0, 260); area('LuceCorridoio', (KX0 - 0.5, -0.5, 2.9), 5.0, 420)
sir = bpy.data.lights.new('LuceSirena', 'POINT'); sir.shadow_soft_size = 0.5; siro = bpy.data.objects.new('LuceSirena', sir); prc.objects.link(siro); siro.parent = FTR; siro.location = (0, -0.95, 1.9)

def desc(o):
    for c in o.children:
        yield c
        yield from desc(c)
def show(o, intervals):
    for q in [o] + list(desc(o)):
        if q.name in NEVER: continue
        first = intervals[0][0] <= 0.0
        q.hide_render = not first; q.keyframe_insert('hide_render', frame=1)
        for (a, b) in intervals:
            if a > 0.0: q.hide_render = False; q.keyframe_insert('hide_render', frame=fr(a))
            if b < TOTAL: q.hide_render = True; q.keyframe_insert('hide_render', frame=fr(b))
NEVER = set()
def hide(o):
    """nasconde per sempre: va chiamata PRIMA di show() sul genitore."""
    for q in [o] + list(desc(o)): NEVER.add(q.name); q.hide_render = True; q.keyframe_insert('hide_render', frame=1)
def keys(o, prop, pts):
    for (t_, v) in pts: setattr(o, prop, v); o.keyframe_insert(prop, frame=fr(t_))

# tempi (dalla voce)
T_B1, T_B2, T_B3, T_B4, T_B5 = 13.08, 16.30, 19.78, 29.98, 32.16
T_MASK, T_TUMBO = 41.78, 43.06
T_TURN, T_COST, T_ELE = 47.94, 49.76, 50.96
T_MELON, T_VAF, T_ALIM, T_TEAM = 55.7, 57.82, 59.6, 62.94
BIRTH = (HX0 + 0.75, -0.05, 0.75)

for z_ in (Z, BZ1, BZ2): hide(z_['veil']); hide(z_['legs'])
hide(Z2['veil'])
show(Z['root'], [(0.0, T_MELON + 0.7)])
show(MEL, [(T_MELON, TOTAL)]); show(tie_, [(T_ALIM - 0.1, TOTAL)]); show(case_, [(T_ALIM - 0.1, TOTAL)]); show(alim, [(T_ALIM - 0.1, TOTAL)])
show(BZ1['root'], [(T_B1, TOTAL)])
show(BZ2['root'], [(T_B2, TOTAL)])
show(FTR, [(T_B3, TOTAL)]); show(PNO, [(T_B4, TOTAL)]); show(GU['root'], [(T_B5, 39.0)])
show(DOC['root'], [(0.0, T_TUMBO + 0.35)]); show(Tb['root'], [(T_TUMBO, TOTAL)]); show(stool, [(T_TUMBO, TOTAL)])
show(TF['root'], [(0.0, T_COST + 0.75)]); show(Z2['root'], [(T_COST + 0.15, TOTAL)])
show(sand, [(0.0, TOTAL)]); show(clip, [(0.0, T_MASK)])

_bs = [(0.21, 0.19, 0.25), (0.19, 0.172, 0.226), (0.172, 0.156, 0.205), (0.15, 0.136, 0.18), (0.13, 0.118, 0.156), (0.11, 0.1, 0.13)]
belly.scale = _bs[0]; belly.keyframe_insert('scale', frame=1)
for i_, tb_ in enumerate((T_B1, T_B2, T_B3, T_B4, T_B5)):
    belly.scale = _bs[i_]; belly.keyframe_insert('scale', frame=fr(tb_ - 0.02)); belly.scale = _bs[i_ + 1]; belly.keyframe_insert('scale', frame=fr(tb_ + 0.12))

# ======================= pose e traiettorie =======================
CH_P = (KX0 - 1.85, 1.22); CH_T = (KX0 - 0.35, 1.22); DOCP = (HX0 + 1.0, 0.95)
SEATED = dict(hL=-PI / 2, hR=-PI / 2)
GLOC = (HX0 + 0.85, -0.05, 0.62); GFLOOR = (HX0 + 1.9, -0.9, 0.0); GDOOR = (HX0 + 6.15, -0.6, 0.0)
FTC = (HX0 + 3.9, -3.3); FTPARK = (HX0 + 5.1, -3.9); PNOP = (HX0 + 0.6, -3.5)
def push(t): return (0.6 < t < 2.8) or (7.74 < t < 9.0) or any(tb - 0.5 < t < tb + 0.15 for tb in (T_B1, T_B2, T_B3, T_B4, T_B5))
def pp(t):
    S_ = dict(loc=(CH_P[0], CH_P[1], -0.12), rot=(0, 0, 0), aL=(-0.35, -0.9, 0.35), aR=(0.35, -0.9, 0.35), head=(0, 0, 0), sw=(0, 0, 0), **SEATED)
    bite = math.sin(t * 5.0) > 0.3
    S_['head'] = (0.15 * bite, 0, 0); S_['sw'] = (0, 0.12 * bite, 0.22 * bite)
    if t >= T_TURN and t < T_VAF:
        y = 0.45 * ramp(t, T_TURN, T_TURN + 0.5); S_.update(rot=(0, 0, y), head=(0, 0, 0.55 * ramp(t, T_TURN, T_TURN + 0.5)), sw=(0, 0, 0))
    if t >= T_VAF:
        S_.update(rot=(0, 0, 0), aL=(-0.7, -0.3, 0.75), aR=(0.7, -0.3, 0.75), head=(-0.15, 0, 0), sw=(0, 0, 0))
    return S_
def sandp(t):
    """posizione locale del panino (figlio di Pippo): morsi, poi cade a terra."""
    s = pp(t)['sw']; base = (0, -1.1, 0.55)
    if t < T_VAF: return (base[0], base[1] + s[1], base[2] + s[2]), (0, 0, 0)
    u = ramp(t, T_VAF + 0.05, T_VAF + 0.45); return (0.1 * u, base[1] - 0.25 * u, base[2] - 0.62 * u * u), (0.0, 0.35 * u, 0.12 * u)
def zp(t):
    sh = 0.03 * math.sin(t * 40) * push(t)
    return dict(loc=(PILLOW[0] + 0.15 + sh, PILLOW[1] - 0.05, 0.62), rot=(-0.12, 0.08 * math.sin(t * 9) * (sh != 0), 0.15))
def melp(t):
    """il cocomero: prima e' il pancione (sotto il costume), poi resta da solo sul letto."""
    z = zp(T_MELON); bl = z['loc']; belly = (bl[0], bl[1] - 0.1, bl[2] + 0.36)
    if t < T_MELON: return belly, (0, 0, 0.15), 0.42
    u = ramp(t, T_MELON, T_MELON + 0.5); final = (PILLOW[0] + 0.25, PILLOW[1] - 0.05, 0.62 + 0.36)
    return lerp(belly, final, u), (0, 0, 0.15 * (1 - u)), 0.42 + 0.58 * u
def zcost(t):
    """il costume da zucchina vola via alla rivelazione."""
    z = zp(t)
    if t < T_MELON: return z['loc'], z['rot']
    u = ramp(t, T_MELON, T_MELON + 0.6); l = z['loc']
    return (l[0] - 0.9 * u, l[1] + 0.6 * u, l[2] + 2.4 * u - 1.2 * u * u), (z['rot'][0] + 2.5 * u, 0, z['rot'][2] + 3.0 * u)
def birthp(t, t0, dest, s1, arc=0.8, d=0.55):
    """nasce: compare sul letto e salta fino a dest. Restituisce (loc, scala)."""
    if t < t0 + 0.25: u = ramp(t, t0, t0 + 0.25); return BIRTH, s1 * (0.0001 + 1.15 * u)
    u = ramp(t, t0 + 0.25, t0 + 0.25 + d); p_ = lerp(BIRTH, dest, u); return (p_[0], p_[1], p_[2] + arc * math.sin(PI * u)), s1
def ftp(t):
    """camion: nasce, salta a terra, gira in tondo con le sirene, poi parcheggia. (loc, yaw, scala)"""
    if t < T_B3 + 0.8:
        l, s = birthp(t, T_B3, (FTC[0] - 1.4, FTC[1], 0.0), 1.0, arc=1.2, d=0.55); return l, -PI / 2 + 0.3, s
    if t < 28.4:
        a = (t - (T_B3 + 0.8)) * 1.35 + PI; return (FTC[0] + 1.4 * math.cos(a), FTC[1] + 1.4 * math.sin(a), 0.03 * abs(math.sin(t * 9))), a + PI, 1.0
    a0 = (28.4 - (T_B3 + 0.8)) * 1.35 + PI; p0 = (FTC[0] + 1.4 * math.cos(a0), FTC[1] + 1.4 * math.sin(a0), 0.0)
    u = ramp(t, 28.4, 29.2); return lerp(p0, (FTPARK[0], FTPARK[1], 0.0), u), (a0 + PI) * (1 - u) + (PI * 0.85) * u, 1.0
def pnop(t):
    l, s = birthp(t, T_B4, (PNOP[0], PNOP[1], 0.0), 1.0, arc=1.0, d=0.5); return l, s
def gup(t):
    """Gualtiero: nasce in piedi sul letto, salta giu', si sistema i baffi, chiede scusa, corre alla porta."""
    if t < T_B5 + 0.3: u = ramp(t, T_B5, T_B5 + 0.3); return dict(loc=GLOC, yaw=-PI / 2, s=0.0001 + 1.1 * u, aL=0.0, aR=0.0, walk=0.0, brow=-0.6)
    if t < 34.2:
        u = ramp(t, 33.0, 33.6); p_ = lerp(GLOC, GFLOOR, u); return dict(loc=(p_[0], p_[1], p_[2] + 0.5 * math.sin(PI * u)), yaw=0.0, s=1.0, aL=0.0, aR=0.0, walk=0.0, brow=-0.6)
    if t < 36.7: k = math.sin(t * 9); return dict(loc=GFLOOR, yaw=0.0, s=1.0, aL=0.0, aR=-2.7 + 0.25 * k, walk=0.0, brow=0.2)
    if t < 37.9: bow = ramp(t, 36.8, 37.2) * (1 - ramp(t, 37.6, 37.9)); return dict(loc=GFLOOR, yaw=0.0, s=1.0, aL=0.0, aR=0.0, walk=0.0, brow=0.4, bow=0.5 * bow)
    u = ramp(t, 37.9, 38.7); p_ = lerp(GFLOOR, GDOOR, u); return dict(loc=p_, yaw=yaw_to(GFLOOR, GDOOR), s=1.0, aL=0.9 * math.sin(t * 22), aR=-0.9 * math.sin(t * 22), walk=math.sin(t * 22), brow=0.4)
def docp(t):
    k = math.sin(t * 8) * push(t)
    S_ = dict(loc=(DOCP[0], DOCP[1], 0), rot=(0.1, 0, yaw_to(DOCP, (HX0 + 0.7, 0.0))), aL=-1.3 + 0.3 * k, aR=-1.3 + 0.3 * k)
    if 23.86 < t < T_MASK: S_.update(rot=(0, 0, yaw_to(DOCP, (HX0 + 1.1, -2.5))), aR=-1.55, aL=-0.4)                # scrive sulla cartella
    if t >= T_MASK: S_.update(rot=(0, 0, yaw_to(DOCP, (HX0 + 0.2, -2.2))), aL=-2.95, aR=-2.95)
    if t >= T_TUMBO: S_.update(collapse=ramp(t, T_TUMBO, T_TUMBO + 0.3))
    return S_
def tfp(t):
    """il finto Tumbo (Eleonora in costume): seduto accanto a Pippo; il costume vola via."""
    S_ = dict(loc=(CH_T[0], CH_T[1], 0.52), rot=(-0.2, 0, 0), head=(0.1, 0, 0.3 * math.sin(t * 2)))
    if t >= T_TURN: S_['head'] = (0.1, 0, -0.5)
    if t >= T_COST:
        u = ramp(t, T_COST, T_COST + 0.7); S_.update(loc=(CH_T[0] + 0.4 * u, CH_T[1] - 0.3 * u, 0.52 + 2.6 * u), rot=(-0.2 + 2.0 * u, 0.0, 2.5 * u))
    return S_

# ======================= chiavi =======================
DH0 = tuple(dhead.location)
BZ1D = (CR[0][0], CR[0][1] - 0.02, 0.72); BZ2D = (CR[1][0], CR[1][1] - 0.02, 0.72)
for f in range(1, NF + 1):
    t = (f - 1) / FPS
    s = pp(t); r = P['root']; r.location = s['loc']; r.rotation_euler = s['rot']; r.keyframe_insert('location', frame=f); r.keyframe_insert('rotation_euler', frame=f)
    for nm, k in (('L', 'aL'), ('R', 'aR')):
        sh = P['shoulder' + nm]; sh.rotation_quaternion = qdir(s[k]); sh.keyframe_insert('rotation_quaternion', frame=f)
    for nm, k in (('L', 'hL'), ('R', 'hR')):
        hp = P['hip' + nm]; hp.rotation_euler = (s[k], 0, 0); hp.keyframe_insert('rotation_euler', frame=f)
    P['head'].rotation_euler = s['head']; P['head'].keyframe_insert('rotation_euler', frame=f)
    l, e = sandp(t); sand.location = l; sand.rotation_euler = e; sand.keyframe_insert('location', frame=f); sand.keyframe_insert('rotation_euler', frame=f)
    z = zp(t); ZR_ = Z['root']
    lz, ez_ = zcost(t); ZR_.location = lz; ZR_.rotation_euler = ez_; ZR_.keyframe_insert('location', frame=f); ZR_.keyframe_insert('rotation_euler', frame=f)
    talk = push(t)
    Z['mouth'].scale = (0.045, 0.02, 0.022 + 0.05 * abs(math.sin(t * 12)) * talk); Z['mouth'].keyframe_insert('scale', frame=f)
    Z['eyes'].scale = (1.25 if talk and math.sin(t * 6) > 0 else 1.0, 1.0, 1.0); Z['eyes'].keyframe_insert('scale', frame=f)
    lm, em, sm_ = melp(t); MEL.location = lm; MEL.rotation_euler = em; MEL.scale = (sm_,) * 3
    for p_ in ('location', 'rotation_euler', 'scale'): MEL.keyframe_insert(p_, frame=f)
    for (BZ, t0, dest) in ((BZ1, T_B1, BZ1D), (BZ2, T_B2, BZ2D)):
        if t0 - 0.05 < t < t0 + 1.0:
            l, sc = birthp(t, t0, dest, 0.36, arc=0.7, d=0.5); BZ['root'].location = l; BZ['root'].scale = (sc,) * 3
            BZ['root'].keyframe_insert('location', frame=f); BZ['root'].keyframe_insert('scale', frame=f)
        if t0 - 0.05 < t:
            BZ['root'].rotation_euler = (0, 0, 0.15 * math.sin(t * 2 + t0)); BZ['root'].keyframe_insert('rotation_euler', frame=f)
    if t > T_B3 - 0.05:
        l, yw, sc = ftp(t); FTR.location = l; FTR.rotation_euler = (0, 0, yw); FTR.scale = (sc,) * 3
        for p_ in ('location', 'rotation_euler', 'scale'): FTR.keyframe_insert(p_, frame=f)
        blink = int(t * 6) % 2 == 0; lr_, lb_ = FT['lights']
        lr_.scale = (0.3, 0.18, 0.12 if blink else 0.02); lb_.scale = (0.3, 0.18, 0.02 if blink else 0.12); lr_.keyframe_insert('scale', frame=f); lb_.keyframe_insert('scale', frame=f)
        sir.color = (1.0, 0.1, 0.05) if blink else (0.1, 0.3, 1.0); sir.energy = 35.0; sir.keyframe_insert('color', frame=f); sir.keyframe_insert('energy', frame=f)
    if T_B4 - 0.05 < t < T_B4 + 1.2:
        l, sc = pnop(t); PNO.location = l; PNO.scale = (sc,) * 3; PNO.rotation_euler = (0, 0, 0.25)
        for p_ in ('location', 'rotation_euler', 'scale'): PNO.keyframe_insert(p_, frame=f)
    if T_B5 - 0.05 < t < 39.1:
        g = gup(t); r = GU['root']; r.location = g['loc']; r.rotation_euler = (g.get('bow', 0.0), 0, g['yaw']); r.scale = (g['s'],) * 3
        for p_ in ('location', 'rotation_euler', 'scale'): r.keyframe_insert(p_, frame=f)
        for nm, k in (('L', 'aL'), ('R', 'aR')): GU['shoulder' + nm].rotation_euler = (g[k], 0, 0); GU['shoulder' + nm].keyframe_insert('rotation_euler', frame=f)
        for nm, sg in (('L', 1), ('R', -1)): GU['hip' + nm].rotation_euler = (0.6 * sg * g['walk'], 0, 0); GU['hip' + nm].keyframe_insert('rotation_euler', frame=f)
    if t < T_TUMBO + 0.4:
        d = docp(t); r = DOC['root']; r.location = d['loc']; r.rotation_euler = d['rot']; cl = d.get('collapse', 0.0)
        r.scale = (1.0 + 0.3 * cl, 1.0 + 0.3 * cl, max(0.05, 1.0 - 0.95 * cl))
        for p_ in ('location', 'rotation_euler', 'scale'): r.keyframe_insert(p_, frame=f)
        for nm in 'LR': DOC['shoulder' + nm].rotation_euler = (d['a' + nm], 0, 0); DOC['shoulder' + nm].keyframe_insert('rotation_euler', frame=f)
        if t >= T_MASK - 0.1:
            u = ramp(t, T_MASK, T_MASK + 0.45); dhead.location = (DH0[0], DH0[1], DH0[2] + 0.42 * u); dhead.keyframe_insert('location', frame=f)
    if t >= T_TUMBO - 0.1:
        r = Tb['root']; r.location = (DOCP[0], DOCP[1], 0.75); r.rotation_euler = (0, 0, yaw_to(DOCP, (HX0 + 0.2, -2.2)))
        r.keyframe_insert('location', frame=f); r.keyframe_insert('rotation_euler', frame=f)
        Tb['tail'].rotation_euler = (-1.0, 0, 0.6 * math.sin(t * 14)); Tb['tail'].keyframe_insert('rotation_euler', frame=f)
    if t < T_COST + 0.8:
        q = tfp(t); r = TF['root']; r.location = q['loc']; r.rotation_euler = q['rot']; r.keyframe_insert('location', frame=f); r.keyframe_insert('rotation_euler', frame=f)
        TF['head'].rotation_euler = q['head']; TF['head'].keyframe_insert('rotation_euler', frame=f)
        TF['tail'].rotation_euler = (-1.0 + 0.5 * math.sin(t * 12), 0, 0.5 * math.sin(t * 14)); TF['tail'].keyframe_insert('rotation_euler', frame=f)
    if t >= T_COST:
        r = Z2['root']; r.location = (CH_T[0], CH_T[1] - 0.05, 0.52); r.rotation_euler = (0, 0, 0.05 * math.sin(t * 3)); r.scale = (min(1.0, 0.0001 + ramp(t, T_COST + 0.15, T_COST + 0.45) * 1.0),) * 3
        for p_ in ('location', 'rotation_euler', 'scale'): r.keyframe_insert(p_, frame=f)
        munch = t > T_ELE and math.sin(t * 14) > 0
        Z2['mouth'].scale = (0.045, 0.02, 0.07 if munch else 0.022); Z2['mouth'].keyframe_insert('scale', frame=f)
    if t >= 38.0:
        op = ramp(t, 38.4, 38.7) * (1 - ramp(t, 39.0, 39.3)); DOORP.rotation_euler = (0, 0, -1.4 * op); DOORP.keyframe_insert('rotation_euler', frame=f)
    elif f == 1: DOORP.keyframe_insert('rotation_euler', frame=f)

_last = {}
def _ex(key, fn, t, k):
    if key in _last and t - 0.06 > _last[key][1]: fn(fr(t - 0.06), **_last[key][0])
    fn(fr(t), **k); _last[key] = (k, t)
def pex(t, **k): _ex('p', lambda f, **kk: pippo.express(P, f, **kk), t, k)
def tex(t, **k): _ex('t', lambda f, **kk: tumbo.tumbo_express(Tb, f, **kk), t, k)
def tfx(t, **k): _ex('tf', lambda f, **kk: tumbo.tumbo_express(TF, f, **kk), t, k)
def gx(t, **k): _ex('g', lambda f, **kk: props009.gex(GU, f, **kk), t, k)
pex(0.0, smile=0.8, mouth_open=0.6)
for k in range(10): pex(9.0 + 0.3 * k, smile=0.8, mouth_open=0.75 if k % 2 else 0.1)
pex(T_TURN, brow=0.5, eye_open=0.8, mouth_open=0.3); pex(T_ELE, brow=-0.7, brow_lift=0.9, eye_scale=1.45, mouth_open=1.0)
pex(T_VAF, brow=-0.6, brow_lift=0.9, eye_scale=1.4, mouth_open=1.0, smile=-0.4)
tfx(0.0, tongue=0.8); tfx(T_TURN, tongue=0.0, eye_scale=1.3, brow=-0.5)
tex(T_TUMBO, tongue=1.0, eye_scale=1.25, brow=0.4)
gx(T_B5, brow=-0.6, mouth=0.8); gx(34.5, brow=0.2, mouth=0.2); gx(36.74, brow=0.5, mouth=0.6); gx(37.9, brow=-0.4, mouth=0.9)

# ======================= effetti =======================
def streak(name, sc, mat, t0, t1, fn, parent=None, mesh=None):
    o = obj(name, mesh or shared_mesh('sphere_lo'), (0, 0, -80), sc, mat, prc, parent=parent)
    o.hide_render = True; o.keyframe_insert('hide_render', frame=1); o.hide_render = False; o.keyframe_insert('hide_render', frame=fr(t0))
    if t1 < TOTAL: o.hide_render = True; o.keyframe_insert('hide_render', frame=fr(t1))
    for f in range(fr(t0), min(NF, fr(t1)) + 1):
        r_ = fn((f - 1) / FPS); o.location = r_[0]; o.keyframe_insert('location', frame=f)
        if len(r_) > 1: o.scale = r_[1]; o.keyframe_insert('scale', frame=f)
    return o
er = np.random.default_rng(16)
def burst(name, mat, t0, dur, c0, n, vmax, sc, grav=4.9, up=1.0):
    for k in range(n):
        v = np.array([er.uniform(-vmax, vmax), er.uniform(-vmax, vmax), er.uniform(0.3, 1.0) * vmax * up])
        streak(name, sc, mat, t0, t0 + dur, lambda t, v=v: ((c0[0] + v[0] * (t - t0), c0[1] + v[1] * (t - t0), max(0.03, c0[2] + v[2] * (t - t0) - grav * (t - t0) ** 2)),))
for tb in (T_B1, T_B2, T_B3, T_B4, T_B5): burst('Coriandolo', B['yellow'], tb, 1.1, (BIRTH[0], BIRTH[1], BIRTH[2] + 0.4), 10, 1.5, (0.03, 0.03, 0.03), grav=2.0)
for k in range(5):
    ph = k / 5; streak('Sudore', (0.025, 0.025, 0.04), W['glass'], 0.3, 3.0, lambda t, ph=ph: ((PILLOW[0] + 0.15 + 0.14 * math.cos(ph * 6.28), -0.2, 1.55 - 0.6 * ((t * 1.3 + ph) % 1.0)),))
for k in range(8):                                                                                         # patatine verso la bocca di Eleonora
    t0 = T_ELE + 0.25 * k
    streak('PatatinaVolo', (0.05, 0.012, 0.035), B['chip'], t0, t0 + 0.25, lambda t, t0=t0: ((CH_T[0], CH_T[1] - 0.25, 0.75 + 0.6 * ramp(t, t0, t0 + 0.25)),))
burst('Briciole', B['chip'], T_ELE + 0.5, 1.2, (CH_T[0], CH_T[1] - 0.2, 1.3), 12, 1.0, (0.03, 0.01, 0.02), grav=3.5)

# ======================= camera =======================
def Z0(t): return (0, 0, 0)
PZ = (PILLOW[0] + 0.15, -0.05)
SHOTS = [  # t0, t1, sub cam, p0, p1, sub mira, a0, a1, lente, f
    (0.0, 2.84, Z0, (HX0 + 0.35, -2.3, 1.35), (HX0 + 0.3, -2.0, 1.35), Z0, (PZ[0], 0.0, 1.15), (PZ[0], 0.0, 1.15), 36, 5),
    (2.84, 4.8, Z0, (HX0 + 1.6, -5.4, 1.8), (HX0 + 1.4, -4.8, 1.75), Z0, (HX0 + 0.2, 0.0, 1.0), (HX0 + 0.2, 0.0, 1.0), 24, 9),
    (4.8, 6.72, Z0, (HX0 + 0.25, -1.6, 1.15), (HX0 + 0.05, -1.15, 1.08), Z0, (PZ[0], -0.2, 1.0), (PZ[0], -0.2, 1.02), 45, 4),
    (6.72, 7.74, Z0, (-3.0, -14.0, 1.8), (-2.4, -13.0, 2.2), Z0, (0.0, 6.5, 4.6), (0.0, 6.5, 5.0), 24, 16),
    (7.74, 9.08, Z0, (HX0 + 2.0, -2.6, 1.6), (HX0 + 1.9, -2.4, 1.55), Z0, (HX0 + 0.3, 0.0, 1.0), (HX0 + 0.3, 0.0, 1.0), 30, 6),
    (9.08, 12.08, Z0, (KX0 - 1.1, -3.3, 1.5), (KX0 - 1.1, -2.9, 1.5), Z0, (KX0 - 1.1, 1.2, 1.2), (KX0 - 1.1, 1.2, 1.25), 20, 8),
    (12.08, 15.1, Z0, (HX0 + 3.4, -2.3, 1.55), (HX0 + 3.3, -2.1, 1.5), Z0, (HX0 + 1.2, 0.2, 0.95), (CR[0][0] - 0.3, 0.7, 0.9), 26, 6),
    (15.1, 18.54, Z0, (HX0 + 3.9, -2.2, 1.55), (HX0 + 3.8, -2.0, 1.5), Z0, (HX0 + 1.4, 0.2, 0.95), (CR[1][0] - 0.3, 0.7, 0.9), 26, 6),
    (18.54, 23.86, Z0, (HX0 + 3.8, -7.2, 2.9), (HX0 + 3.6, -7.1, 2.85), Z0, (HX0 + 2.8, -1.4, 0.8), (HX0 + 3.4, -2.6, 0.7), 18, 12),
    (23.86, 27.54, Z0, (HX0 + 1.35, -1.7, 1.6), (HX0 + 1.3, -1.45, 1.6), Z0, (DOCP[0] + 0.15, DOCP[1], 1.5), (DOCP[0] + 0.2, DOCP[1], 1.45), 36, 4),
    (27.54, 28.74, Z0, (HX0 + 0.2, -3.6, 1.6), (HX0 + 0.1, -3.9, 1.6), Z0, (HX0 + 2.8, -1.6, 1.0), (HX0 + 3.6, -2.6, 0.9), 24, 10),
    (28.74, 31.24, Z0, (HX0 + 3.4, -5.4, 1.7), (HX0 + 3.2, -5.2, 1.65), Z0, (HX0 + 1.0, -1.6, 0.9), (PNOP[0], PNOP[1], 0.75), 26, 10),
    (31.24, 34.52, Z0, (HX0 + 1.1, -3.6, 1.6), (HX0 + 1.2, -3.4, 1.6), Z0, (HX0 + 1.0, -0.1, 1.5), (GFLOOR[0], GFLOOR[1], 1.4), 28, 7),
    (34.52, 39.38, Z0, (HX0 + 3.0, -6.4, 1.7), (HX0 + 3.2, -6.0, 1.7), Z0, (HX0 + 2.2, -0.8, 1.3), (HX0 + 4.6, -0.6, 1.2), 22, 12),
    (39.38, 41.2, Z0, (HX0 + 1.3, -1.6, 1.6), (HX0 + 1.25, -1.3, 1.6), Z0, (DOCP[0], DOCP[1], 1.65), (DOCP[0], DOCP[1], 1.7), 38, 4),
    (41.2, 44.16, Z0, (HX0 + 1.4, -1.9, 1.5), (HX0 + 1.35, -1.7, 1.45), Z0, (DOCP[0], DOCP[1], 1.4), (DOCP[0], DOCP[1], 1.2), 34, 5),
    (44.16, 47.5, Z0, (KX0 - 1.1, -3.3, 1.5), (KX0 - 1.0, -3.0, 1.5), Z0, (KX0 - 1.1, 1.2, 1.2), (KX0 - 1.0, 1.2, 1.2), 20, 8),
    (47.5, 50.96, Z0, (KX0 + 0.4, -1.6, 1.35), (KX0 + 0.35, -1.4, 1.35), Z0, (KX0 - 0.9, 1.2, 1.1), (CH_T[0], 1.2, 1.2), 28, 5),
    (50.96, 53.26, Z0, (CH_T[0] + 0.1, -0.6, 1.15), (CH_T[0] + 0.1, -0.45, 1.15), Z0, (CH_T[0], CH_T[1], 1.0), (CH_T[0], CH_T[1], 1.0), 34, 4),
    (53.26, 55.16, Z0, (HX0 + 0.25, -1.9, 1.3), (HX0 + 0.1, -1.4, 1.2), Z0, (PZ[0], -0.1, 1.05), (PZ[0], -0.1, 1.05), 38, 4),
    (55.16, 57.82, Z0, (HX0 + 0.6, -2.6, 1.5), (HX0 + 0.55, -2.4, 1.45), Z0, (PZ[0], -0.05, 1.05), (PZ[0] + 0.1, -0.05, 1.0), 32, 6),
    (57.82, 59.6, Z0, (KX0 - 1.4, -2.6, 1.45), (KX0 - 1.4, -2.3, 1.45), Z0, (CH_P[0], 1.1, 1.2), (CH_P[0], 1.0, 1.0), 26, 6),
    (59.6, 62.94, Z0, (HX0 + 0.2, -1.9, 1.2), (HX0 + 0.25, -1.6, 1.15), Z0, (HX0 - 0.35, -0.2, 0.95), (HX0 - 0.35, -0.2, 0.95), 34, 4),
    (62.94, TOTAL, Z0, (HX0 + 2.4, -7.3, 2.6), (HX0 + 2.4, -7.1, 2.7), Z0, (HX0 + 2.3, -1.2, 0.8), (HX0 + 2.3, -1.2, 0.8), 15, 14),
]
camd = bpy.data.cameras.new('Cam'); cam = bpy.data.objects.new('Cam', camd); cac.objects.link(cam); scene.camera = cam
camd.clip_start = 0.05; camd.clip_end = 1500; camd.sensor_width = 36
tgt = empty('CamTarget', (0, 0, 1), None, cac)
ct = cam.constraints.new('TRACK_TO'); ct.target = tgt; ct.track_axis = 'TRACK_NEGATIVE_Z'; ct.up_axis = 'UP_Y'
camd.dof.use_dof = True; camd.dof.focus_object = tgt
for f in range(1, NF + 1):
    t = (f - 1) / FPS
    s_ = next((s for s in SHOTS if s[0] <= t < s[1]), SHOTS[-1]); u = (t - s_[0]) / (s_[1] - s_[0])
    cam.location = add(s_[2](t), lerp(s_[3], s_[4], u)); tgt.location = add(s_[5](t), lerp(s_[6], s_[7], u))
    camd.lens = s_[8]; camd.dof.aperture_fstop = s_[9]
    cam.keyframe_insert('location', frame=f); tgt.keyframe_insert('location', frame=f); camd.keyframe_insert('lens', frame=f); camd.dof.keyframe_insert('aperture_fstop', frame=f)

def lin(idb):
    for fc in all_fcurves(idb):
        kind = 'CONSTANT' if 'hide' in fc.data_path else 'LINEAR'
        for kp in fc.keyframe_points: kp.interpolation = kind
for o in bpy.data.objects: lin(o)
for l_ in bpy.data.lights: lin(l_)
set_interp(camd, 'CONSTANT')
kitlook.upgrade(scene, M, envc, prc)
try: scene.render.motion_blur_shutter = 0.06
except Exception: pass
os.makedirs('../t016', exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath('../t016/pippo_t016.blend')); print('SAVED')
