H = props010.mats010(); T11 = props011.mats011()
JX = 200.0; CX = 300.0
bars, board = props010.jail_set(envc, H, JX, 'TORNADO N. 0002', 'FURTO DI CASA'); props010.court_set(envc, H, CX, '(TRANNE PER I TORNADO)')
CAGE = (CX - 3.0, 0.6)
cage = props010.cage(envc, H); cage.location = (CAGE[0], CAGE[1], 0)
HOUSE = (0.0, 9.5)
rub = props011.rubble(envc, set004.house_mats(M, 0, 0, 1)[:3]); rub.location = (HOUSE[0], HOUSE[1], 0)

# ======================= personaggi =======================
P = pippo.build_pippo(chc); Tb = tumbo.build_tumbo(chc, scale=0.75); T = props011.tornado(chc, T11); C = props010.cop(chc)
for r in (P['root'], Tb['root'], C['root']): r.rotation_mode = 'XYZ'
for k_ in ('eyeL', 'eyeR', 'pupilL', 'pupilR', 'browL', 'browR', 'mouth', 'tongue'): T[k_].hide_render = True; T[k_].hide_viewport = True   # il tornado non ha la faccia
for nm_ in 'LR':
    for o_ in [T['shoulder' + nm_]] + list(T['shoulder' + nm_].children): o_.hide_render = True                                  # niente braccia: e' un tornado e basta
T['cuffs'].parent = T['rings'][1]; T['cuffs'].location = (0, -props011.ring_r(1) - 0.12, 0.0); T['cuffs'].scale = (1.5, 1.5, 1.5)
for nm in 'LR': P['shoulder' + nm].rotation_mode = 'QUATERNION'
def qdir(d, rest=(0, 0, -1)): return Vector(rest).rotation_difference(Vector(d).normalized())
for s_ in (-1, 1): obj('AgSopr', set004.box_c(), (s_ * 0.10, -0.25, 0.15), (0.13, 0.03, 0.035), M['dark'], chc, rot=(0, -s_ * 0.45, 0), parent=C['head'])
capparts = [c for c in C['head'].children if c.name.startswith('Ag') and not c.name.startswith('AgSopr')]
ball_('AgCiuffo', 0.05, (0, 0, 0.30), T11['hairc'], chc, parent=C['head'], sc=(1, 1, 2.2))
TOR = (3.2, 5.0)
NCOP = 19; cops = []
for k in range(NCOP):
    a = math.radians(196 + 148 * k / (NCOP - 1)); cc = props010.cop(chc, 'Ag%02d' % k); cc['root'].rotation_mode = 'XYZ'; cc['ang'] = a; cops.append(cc)
CARS = []
for k, (x1, y1, rz, x0) in enumerate([(-6.5, -3.6, PI / 2, -30), (9.5, -3.2, -PI / 2, 34), (-7.5, 1.2, PI / 2, -32), (10.5, 1.5, -PI / 2, 36), (-7.0, -6.8, PI / 2, -34)]):
    pc, a_, b_ = props010.police_car(prc, H, G9); pc.rotation_euler = (0, 0, rz); CARS.append((pc, x0, x1, y1, 15.75 + 0.07 * k, a_, b_))

# ======================= oggetti =======================
PP0 = (-1.2, -1.0); CP0 = (-3.0, -2.6)
phone = props010.phone(chc, H, P['shoulderR']); cphone = props010.phone(chc, H, C['shoulderR'])
pcar, lred, lblue = props010.police_car(prc, H, G9); pcar.rotation_euler = (0, 0, PI / 2)
wig = props010.wig(chc, H, Tb['head'], s=1.5); wig2 = props010.wig(prc, H, None, c=(CX, 3.0, 2.3), s=1.5 * 0.75); gavel = props010.gavel(prc, H, None, (CX + 0.5, 2.75, 1.6))
cap1 = props011.fly_cap(prc, T11); cap2 = props011.fly_cap(prc, T11)
crk = props011.crack(prc, T11); crk.location = (-0.5, -2.3, 0); crk.rotation_euler = (0, 0, 0.15)
flash_l = bpy.data.lights.new('Flash', 'POINT'); flash_o = bpy.data.objects.new('Flash', flash_l); prc.objects.link(flash_o); flash_o.location = (JX, -3.5, 2.6)

def desc(o):
    for c in o.children:
        yield c
        yield from desc(c)
def show(o, intervals):
    for q in ([o] + list(desc(o)) if not isinstance(o, list) else o):
        first = intervals[0][0] <= 0.0
        q.hide_render = not first; q.keyframe_insert('hide_render', frame=1)
        for (a, b) in intervals:
            if a > 0.0: q.hide_render = False; q.keyframe_insert('hide_render', frame=fr(a))
            if b < TOTAL: q.hide_render = True; q.keyframe_insert('hide_render', frame=fr(b))
def pop(o, t, d=0.32, s0=0.0001, over=1.22, s1=1.0):
    b = tuple(o.scale)
    for (tt_, v) in ((t, s0), (t + 0.55 * d, over), (t + d, s1)):
        o.scale = (b[0] * v, b[1] * v, b[2] * v); o.keyframe_insert('scale', frame=fr(tt_))
def keys(o, prop, pts):
    for (t_, v) in pts: setattr(o, prop, v); o.keyframe_insert(prop, frame=fr(t_))
keys(phouse, 'location', [(0.0, (HOUSE[0], HOUSE[1], 0)), (0.7, (HOUSE[0], HOUSE[1], 0)), (2.5, (HOUSE[0] + 0.5, HOUSE[1] - 0.5, 6.5))])
keys(phouse, 'scale', [(0.0, (1, 1, 1)), (0.7, (1, 1, 1)), (1.6, (0.6, 0.6, 0.7)), (2.5, (0.03, 0.03, 0.03))])
keys(phouse, 'rotation_euler', [(0.0, (0, 0, 0)), (0.7, (0, 0, 0)), (2.5, (0.6, 0.4, 14.0))])
show(phouse, [(0.0, 2.5)]); show(rub, [(2.0, TOTAL)]); keys(rub, 'scale', [(2.0, (1, 1, 0.05)), (2.6, (1, 1, 1))])
show(phone, [(6.2, 7.9), (32.6, 35.6)]); show(cphone, [(13.4, 15.7)])
show(pcar, [(7.9, 21.0)]); show(C['root'], [(8.45, 18.9), (21.5, 24.6), (29.0, 32.6)]); pop(C['root'], 8.45, 0.25)
show(capparts, [(0.0, 9.75), (21.5, 24.6), (29.0, 31.55)]); show(cap1, [(9.75, 11.3)]); show(cap2, [(31.55, 32.6)])
for k, cc in enumerate(cops): show(cc['root'], [(15.95 + 0.035 * k, 18.9)]); pop(cc['root'], 15.95 + 0.035 * k, 0.2)
for (pc, x0, x1, y1, t0, a_, b_) in CARS: show(pc, [(15.7, 18.9)])
show(T['cuffs'], [(18.2, TOTAL)]); pop(T['cuffs'], 18.2, 0.2)
show(board, [(18.9, 21.5)])
keys(bars, 'location', [(28.9, (JX, -0.9, 9.0)), (29.05, (JX, -0.9, 9.0)), (29.2, (JX, -0.9, 0.0)), (29.26, (JX, -0.9, 0.12)), (29.32, (JX, -0.9, 0.0))])
show(wig, [(21.5, 25.25), (27.12, 29.0)]); show(wig2, [(25.25, 27.12)])
keys(wig2, 'location', [(25.25, (CX, 3.0, 2.35)), (25.6, (CX + 0.1, 3.0, 2.9)), (26.6, (CX - 0.1, 3.0, 1.75))]); keys(wig2, 'rotation_euler', [(25.25, (0, 0, 0)), (26.6, (0.3, 0.2, 5.0))])
keys(gavel, 'rotation_euler', [(26.9, (0.3, 0, 0)), (27.25, (0.1, 0, 0)), (27.37, (1.45, 0, 0)), (27.6, (0.3, 0, 0)), (28.1, (0.1, 0, 0)), (28.22, (1.45, 0, 0)), (28.5, (0.5, 0, 0))])
show(crk, [(33.3, 35.6)]); keys(crk, 'scale', [(33.3, (0.05, 1, 1)), (33.9, (1, 1, 1))])

# ======================= pose =======================
DOWN = lambda s: (s * 0.14, 0, -1)
UP = dict(aL=(-0.35, -0.25, 1), aR=(0.35, -0.25, 1)); FIST = dict(aL=(-0.55, -0.15, -0.8), aR=(0.55, -0.15, -0.8))
def pp(t):
    S_ = dict(loc=(0, 0, 0), rot=(0, 0, 0), aL=DOWN(-1), aR=DOWN(1), hL=0.0, hR=0.0, head=(0, 0, 0))
    if t < 2.9:                                    # gli mangiano la casa
        k = math.sin(t * 16); tr = ramp(t, 1.9, 2.2)
        S_.update(loc=(-2.2 + 0.03 * math.sin(t * 40), -1.5, 0.05 * abs(k)), rot=(0, 0, -0.3), aL=(-0.5, -0.3, 0.85 + 0.15 * k), aR=(0.5, -0.3, 0.85 - 0.15 * k), head=(0, 0, -1.2 * (1 - tr) * (t > 0.5)))
    elif t < 6.2: S_.update(loc=(PP0[0], PP0[1], 0.05 * abs(math.sin(t * 8))), rot=(0.08, 0, 0.5), aR=(0.5, 0.45, 0.75), aL=(-0.55, -0.15, -0.8), head=(-0.2, 0, 0.3))
    elif t < 7.9: S_.update(loc=(PP0[0], PP0[1], 0), aR=(0.12, -0.28, 0.95), aL=(-0.6, 0.5, 0.5 + 0.2 * math.sin(t * 14)), head=(0, 0.12, 0))
    elif t < 18.9:
        ch = ramp(t, 18.2, 18.4)
        S_.update(loc=(PP0[0], PP0[1], 0.15 * ch * abs(math.sin(t * 10))), rot=(0, 0, 0.6), aR=lerp((0.5, 0.45, 0.75), UP['aR'], ch), aL=lerp((-0.4, -0.2, -0.85), UP['aL'], ch), head=(-0.15, 0, 0.5 * (1 - ch)))
    elif t < 29.0: S_.update(loc=(CX + 1.0, -1.6, 0.03 * abs(math.sin(t * 20)) * (24.9 < t < 26.6)), rot=(0.25 * ramp(t, 24.9, 25.2) * (1 - ramp(t, 26.5, 26.9)), 0, 0.5), head=(0, 0, 0.6 - 1.1 * ramp(t, 22.0, 22.4)),
                             **(UP if t > 27.3 else dict(aL=(-0.6, -0.5, 0.4 * ramp(t, 24.9, 25.2) * (1 - ramp(t, 26.5, 26.9)) - 0.6), aR=(0.5, -0.15, -0.8))))
    elif t < 32.6: S_.update(loc=(JX - 12, -3, 0))
    elif t < 35.6:                                 # il terremoto
        q = ramp(t, 33.3, 33.5); j = 0.05 * math.sin(t * 47) * q
        S_.update(loc=(PP0[0] + j, PP0[1], 0.04 * abs(math.sin(t * 31)) * q), rot=(0, 0.06 * math.sin(t * 29) * q, 0.1), aR=(0.12, -0.28, 0.95), aL=lerp(DOWN(-1), (-0.8, -0.2, 0.3), q), head=(0, 0.12, 0))
    else: S_.update(loc=(JX - 1.7, -2.6, 0), rot=(0, 0, -0.35), aR=(0.55, -0.15, -0.8), aL=(-0.55, -0.15, -0.8), head=(0, 0, -0.5 * (1 - ramp(t, 36.6, 36.9))))
    return S_
def tp(t):
    S_ = dict(loc=(0, 0, 0), rot=(0, 0, 0), head=(0, 0, 0), tail=-1.0 + 0.5 * math.sin(t * 12))
    if t < 2.9: S_.update(loc=(0.2, -2.4, 0), rot=(0, 0, 0.2 + 2.6 * (1 - ramp(t, 1.9, 2.3))), head=(-0.4, 0, 0), tail=-0.2)
    elif t < 18.9: S_.update(loc=(0.3, -2.0, 0), rot=(0, 0, 0.5), head=(-0.45, 0, 0.3), tail=-0.3)
    elif t < 25.25: S_.update(loc=(CX, 3.05, 1.55), head=(0.1 * math.sin(t * 5) * (23.6 < t < 24.4), 0, -0.4 * ramp(t, 22.6, 23.0)), tail=-0.6)
    elif t < 27.0:                                 # vola via il giudice
        u = (t - 25.25) / 1.75; S_.update(loc=(CX + 6.0 * u, 3.05 - 1.5 * u, 1.55 + 1.2 * u + 3.6 * u * u), rot=(9 * u, 4 * u, 6 * u))
    elif t < 29.0:
        u = min(1.0, (t - 27.0) / 0.12); sq = ramp(t, 27.12, 27.2) * (1 - ramp(t, 27.2, 27.4))
        S_.update(loc=(CX, 3.05, 1.55 + 7.0 * (1 - u)), rot=(0, 0, 0.0), head=(0.25 * sq, 0.3, -0.4), tail=-0.2)
    elif t < 35.6: S_.update(loc=(0.3, -2.0, 0.04 * abs(math.sin(t * 33)) * ramp(t, 33.3, 33.5)), rot=(0, 0, 0.5), head=(-0.2, 0, 0.3))
    else: S_.update(loc=(JX - 2.8, -3.2, 0), rot=(0, 0, -0.5), head=(0, 0, -0.3))
    return S_
def tor(t):
    """Tornado: loc, scala, ampiezza dell'ondeggiamento, velocità, braccia."""
    Q = dict(loc=(TOR[0], TOR[1], 0), sc=1.0, wob=0.14, aL=(-0.8, -0.3, -0.5), aR=(0.8, -0.3, -0.5), lean=0.0)
    CUF = dict(aL=(0.75, -0.6, -0.3), aR=(-0.75, -0.6, -0.3))
    if t < 2.9:
        u = ramp(t, 0.0, 0.6); v = ramp(t, 2.3, 2.9)
        Q.update(loc=(lerp((7.0,), (HOUSE[0] + 0.6,), u)[0] + (TOR[0] - HOUSE[0] - 0.6) * v, lerp((14.0,), (HOUSE[1] - 0.3,), u)[0] + (TOR[1] - HOUSE[1] + 0.3) * v, 0), sc=1.15 - 0.15 * v, wob=0.2)
    elif t < 18.9:
        w = math.sin(t * 9)
        if t < 6.2: Q.update(aL=(-0.9, -0.2, 0.45 + 0.3 * w), aR=(0.9, -0.2, 0.45 - 0.3 * w))
        if 9.4 < t < 11.3: Q.update(aR=(-0.2, -1, 0.1), aL=(-0.9, -0.2, 0.3))
        if 15.9 < t < 18.2: Q.update(aL=(-0.6, -0.3, 0.9), aR=(0.6, -0.3, 0.9), wob=0.07)
        if t >= 18.2: Q.update(wob=0.05, **CUF)
        Q['loc'] = (TOR[0] + 0.25 * math.sin(t * 1.1), TOR[1] + 0.2 * math.cos(t * 0.9), 0)
    elif t < 21.5: Q.update(loc=(JX + 0.5 * math.sin(t * 7.3), 0.7, 0.1 * abs(math.sin(t * 11))), sc=0.42, wob=0.3, **CUF)
    elif t < 29.0:
        blow = ramp(t, 24.9, 25.2) * (1 - ramp(t, 26.4, 26.9)); sad = ramp(t, 27.4, 28.4)
        Q.update(loc=(CAGE[0], CAGE[1], 0.12), sc=0.40 + 0.06 * blow - 0.06 * sad, wob=0.08 + 0.3 * blow, lean=0.3 * blow, **CUF)
    elif t < 35.6: Q.update(loc=(JX + 0.6 * math.sin(t * 2.2), 0.6, 0), sc=0.46, wob=0.12, lean=0.15 * math.cos(t * 2.2), **CUF)
    else: Q.update(loc=(JX + 0.9, 0.6, 0), sc=0.40, wob=0.1, **CUF)
    return Q
def cp(t):
    S_ = dict(loc=(CP0[0], CP0[1], 0), rot=(0, 0, 0.5), aL=0.0, aR=0.0, head=(0, 0, 0))
    if t < 9.3: S_.update(aR=-1.3 * ramp(t, 8.7, 9.0))                                              # "ci penso io"
    elif t < 11.3: g = ramp(t, 9.75, 9.95); S_.update(aR=-1.3 * (1 - g) - 2.9 * g, aL=-2.9 * g, head=(-0.4 * g, 0, 0.3))
    elif t < 13.4: S_.update(loc=(CP0[0] + 0.012 * math.sin(t * 50), CP0[1], 0), rot=(0.06, 0, 0.3), aL=-0.25, aR=-0.25)
    elif t < 15.7: S_.update(rot=(0, 0, 0.3), aR=-2.75, aL=-0.9 - 0.3 * math.sin(t * 12))
    elif t < 18.9: S_.update(rot=(0, 0, 0.9), aR=-1.5, aL=-0.2)
    elif t < 24.6: S_.update(loc=(CX + 2.4, 0.95, 0), rot=(0, 0, 0.3), aR=-1.4 * ramp(t, 22.0, 22.3), head=(0, 0, 0.4))
    else:
        g = ramp(t, 31.55, 31.75); S_.update(loc=(JX + 2.1, -2.2, 0), rot=(0, 0, -0.5), aR=-2.9 * g, aL=-2.9 * g, head=(-0.4 * g, 0, -0.3))
    return S_
def cap_path(t, t0, p0, p1, dur=1.4):
    u = min(1.0, max(0.0, (t - t0) / dur)); r = 0.9 * math.sin(PI * u)
    return (p0[0] + (p1[0] - p0[0]) * u + r * math.cos(u * 14), p0[1] + (p1[1] - p0[1]) * u + r * math.sin(u * 14), p0[2] + (p1[2] - p0[2]) * u + 0.8 * math.sin(PI * u)), (u * 9, u * 5, u * 20)

# ======================= chiavi =======================
TR = Tb['root']; TRo = T['root']
for f in range(1, NF + 1):
    t = (f - 1) / FPS
    s = pp(t); r = P['root']; r.location = s['loc']; r.rotation_euler = s['rot']; r.keyframe_insert('location', frame=f); r.keyframe_insert('rotation_euler', frame=f)
    for nm, k in (('L', 'aL'), ('R', 'aR')):
        sh = P['shoulder' + nm]; sh.rotation_quaternion = qdir(s[k]); sh.keyframe_insert('rotation_quaternion', frame=f)
    for nm, k in (('L', 'hL'), ('R', 'hR')):
        hp = P['hip' + nm]; hp.rotation_euler = (s[k], 0, 0); hp.keyframe_insert('rotation_euler', frame=f)
    P['head'].rotation_euler = s['head']; P['head'].keyframe_insert('rotation_euler', frame=f)
    q = tp(t); TR.location = q['loc']; TR.rotation_euler = q['rot']; TR.keyframe_insert('location', frame=f); TR.keyframe_insert('rotation_euler', frame=f)
    Tb['head'].rotation_euler = q['head']; Tb['head'].keyframe_insert('rotation_euler', frame=f)
    Tb['tail'].rotation_euler = (q['tail'], 0, 0.5 * math.sin(t * 14)); Tb['tail'].keyframe_insert('rotation_euler', frame=f)
    Q = tor(t); TRo.location = Q['loc']; TRo.scale = (Q['sc'],) * 3; TRo.keyframe_insert('location', frame=f); TRo.keyframe_insert('scale', frame=f)
    for k in range(props011.NR):
        e = T['rings'][k]; a = Q['wob'] * k * 0.55
        e.location = (a * math.sin(t * 6.5 + k * 0.75) + Q['lean'] * k, a * 0.6 * math.cos(t * 6.5 + k * 0.75), props011.ring_z(k)); e.keyframe_insert('location', frame=f)
        sp_ = T['spin'][k]; sp_.rotation_euler = (0, 0, t * (9.0 + 0.6 * k)); sp_.keyframe_insert('rotation_euler', frame=f)
    for nm, k in (('L', 'aL'), ('R', 'aR')):
        sh = T['shoulder' + nm]; sh.rotation_quaternion = qdir(Q[k]); sh.keyframe_insert('rotation_quaternion', frame=f)
    c = cp(t); r = C['root']; r.location = c['loc']; r.rotation_euler = c['rot']; r.keyframe_insert('location', frame=f); r.keyframe_insert('rotation_euler', frame=f)
    C['shoulderL'].rotation_euler = (c['aL'], 0, 0); C['shoulderR'].rotation_euler = (c['aR'], 0, 0); C['head'].rotation_euler = c['head']
    for o in (C['shoulderL'], C['shoulderR'], C['head']): o.keyframe_insert('rotation_euler', frame=f)
    if 7.8 < t < 9.3:
        u = ramp(t, 7.9, 8.4); pcar.location = (-30.0 + (CP0[0] - 2.4 + 30.0) * (1 - (1 - u) ** 2), CP0[1] + 0.9, 0); pcar.keyframe_insert('location', frame=f)
    on = int(t * 7) % 2
    for (a_, b_) in [(lred, lblue)] + [(x[5], x[6]) for x in CARS]:
        if 7.8 < t < 19.0: a_.scale = (0.42, 0.20, 0.13 if on else 0.02); b_.scale = (0.42, 0.20, 0.02 if on else 0.13); a_.keyframe_insert('scale', frame=f); b_.keyframe_insert('scale', frame=f)
    if 9.6 < t < 11.4:
        l, e = cap_path(t, 9.75, (CP0[0], CP0[1], 2.15), (TOR[0], TOR[1], 6.3)); cap1.location = l; cap1.rotation_euler = e; cap1.keyframe_insert('location', frame=f); cap1.keyframe_insert('rotation_euler', frame=f)
    if 31.4 < t < 32.7:
        l, e = cap_path(t, 31.55, (JX + 2.1, -2.2, 2.15), (JX + 0.5, 0.2, 3.6), 1.0); cap2.location = l; cap2.rotation_euler = e; cap2.keyframe_insert('location', frame=f); cap2.keyframe_insert('rotation_euler', frame=f)
    if 15.6 < t < 19.0:
        for (pc, x0, x1, y1, t0, a_, b_) in CARS:
            u = ramp(t, t0, t0 + 0.55); pc.location = (x0 + (x1 - x0) * (1 - (1 - u) ** 2), y1, 0); pc.keyframe_insert('location', frame=f)
        rush = ramp(t, 17.0, 17.7); rad = 5.0 - 2.3 * rush
        for k, cc in enumerate(cops):
            a = cc['ang']; x = TOR[0] + rad * math.cos(a) * 1.25; y = TOR[1] + rad * math.sin(a); run = math.sin(t * 22 + k) * rush * (1 - ramp(t, 17.7, 17.9))
            r = cc['root']; r.location = (x, y, 0.06 * abs(run)); r.rotation_euler = (0.15 * rush, 0, math.atan2(TOR[0] - x, -(TOR[1] - y))); r.keyframe_insert('location', frame=f); r.keyframe_insert('rotation_euler', frame=f)
            for nm, sg in (('L', 1), ('R', -1)):
                cc['shoulder' + nm].rotation_euler = (-1.4 - 0.9 * rush, 0, 0); cc['shoulder' + nm].keyframe_insert('rotation_euler', frame=f)
                cc['hip' + nm].rotation_euler = (sg * 0.7 * run, 0, 0); cc['hip' + nm].keyframe_insert('rotation_euler', frame=f)
    if 18.8 < t < 21.6:                                                                             # il cartello non sta fermo
        Ql = tor(t)['loc']; board.location = (Ql[0], -0.05, 0.75 + Ql[2]); board.rotation_euler = (0, 0.5 * math.sin(t * 9), 0.4 * math.sin(t * 7.3)); board.keyframe_insert('location', frame=f); board.keyframe_insert('rotation_euler', frame=f)
    flash_l.energy = 12000.0 if (19.5 <= t < 19.6 or 20.55 <= t < 20.65) else 0.0; flash_l.keyframe_insert('energy', frame=f)

_last = {}
def _ex(key, fn, t, k):
    if key in _last and t - 0.06 > _last[key][1]: fn(fr(t - 0.06), **_last[key][0])
    fn(fr(t), **k); _last[key] = (k, t)
def pex(t, **k): _ex('p', lambda f, **kk: pippo.express(P, f, **kk), t, k)
def tex(t, **k): _ex('t', lambda f, **kk: tumbo.tumbo_express(Tb, f, **kk), t, k)
def nx(t, **k): _ex('n', lambda f, **kk: props011.tornex(T, f, **kk), t, k)
pex(0.0, brow=-0.8, brow_lift=0.8, eye_scale=1.35, mouth_open=1.0); pex(2.95, brow=1.0, mouth_open=0.7, look=(0.5, 0.5)); pex(6.25, brow=1.0, mouth_open=0.6, eye_open=0.8); pex(7.95, smile=0.7, brow=0.8, look=(-0.6, 0))
pex(9.8, brow=-0.5, brow_lift=0.6, eye_scale=1.25, mouth_open=0.5, look=(0, 0.6)); pex(13.5, brow=0.5, smile=0.3, look=(-0.6, 0)); pex(15.9, smile=0.9, brow_lift=0.6, eye_scale=1.2, mouth_open=0.6); pex(18.2, smile=1.0, mouth_open=0.9, brow_lift=0.6)
pex(18.95, brow=1.0, eye_open=0.7, look=(-0.6, 0)); pex(24.95, brow=-0.8, brow_lift=0.8, eye_scale=1.3, mouth_open=1.0, look=(0.4, 0.6)); pex(27.35, smile=1.0, mouth_open=0.9, brow_lift=0.6)
pex(32.65, brow=1.0, mouth_open=0.5, eye_open=0.8); pex(33.35, brow=-0.8, brow_lift=0.8, eye_scale=1.35, mouth_open=0.9); pex(35.65, brow=1.0, smile=0.8, eye_open=0.7, look=(0.6, 0)); pex(36.7, smile=1.0, brow=0.6, mouth_open=0.4, look=(0, 0))
tex(0.0, eye_scale=1.4, brow=-0.7); tex(2.95, brow=1.0, eye_open=0.7); tex(15.9, tongue=0.7); tex(18.95, brow=0.8, eye_open=0.75); tex(23.6, brow=1.0, eye_open=0.8, tongue=0.3); tex(24.95, eye_scale=1.5, brow=-0.8)
tex(27.1, brow=1.0, eye_open=0.6); tex(29.0, tongue=0.5); tex(33.35, eye_scale=1.4, brow=-0.7); tex(35.65, tongue=0.6)
nx(0.0, brow=1.0, mouth=1.0, eye=1.1); nx(2.5, brow=0.6, mouth=0.15); nx(2.95, brow=0.8, mouth=0.8, tongue=1.0); nx(6.25, brow=0.7, mouth=0.4); nx(8.5, brow=0.3, mouth=0.2, look=(-0.8, -0.6))
nx(9.5, brow=0.9, mouth=0.9, look=(-0.8, -0.6)); nx(10.3, brow=0.5, mouth=0.7, tongue=0.8, look=(-0.6, -0.5)); nx(13.4, brow=0.6, mouth=0.3); nx(15.9, brow=-0.7, mouth=0.6, eye=1.3, look=(0, -0.7))
nx(18.2, brow=-1.0, mouth=1.0, eye=1.4); nx(18.95, brow=0.9, mouth=0.1, eye=0.9); nx(19.5, brow=0.9, mouth=0.1, eye=0.5); nx(19.65, brow=0.8, mouth=0.6, tongue=0.7); nx(21.55, brow=0.5, mouth=0.1, look=(0.7, 0.3))
nx(24.9, brow=1.0, mouth=1.0, eye=1.1, look=(0.8, 0.3)); nx(26.7, brow=0.6, mouth=0.4, tongue=0.6, look=(0.6, 0.4)); nx(27.37, brow=-1.0, mouth=1.0, eye=1.4); nx(28.4, brow=-1.0, mouth=0.15, eye=1.1, look=(0, -0.7))
nx(29.3, brow=-0.9, mouth=0.1, eye=1.0, look=(0, -0.6)); nx(31.5, brow=0.3, mouth=0.5, look=(0.8, 0)); nx(35.65, brow=-0.6, mouth=0.1, look=(-0.8, 0)); nx(36.9, brow=0.7, mouth=0.6, tongue=1.0, look=(-0.8, 0))

# ======================= effetti =======================
def streak(name, sc, mat, t0, t1, fn, parent=None, mesh=None, rot=None):
    o = obj(name, mesh or shared_mesh('sphere_lo'), (0, 0, -80), sc, mat, prc, parent=parent)
    if rot: o.rotation_euler = rot
    o.hide_render = True; o.keyframe_insert('hide_render', frame=1); o.hide_render = False; o.keyframe_insert('hide_render', frame=fr(t0))
    if t1 < TOTAL: o.hide_render = True; o.keyframe_insert('hide_render', frame=fr(t1))
    for f in range(fr(t0), min(NF, fr(t1)) + 1):
        r_ = fn((f - 1) / FPS); o.location = r_[0]; o.keyframe_insert('location', frame=f)
        if len(r_) > 1: o.scale = r_[1]; o.keyframe_insert('scale', frame=f)
        if len(r_) > 2: o.rotation_euler = r_[2]; o.keyframe_insert('rotation_euler', frame=f)
    return o
er = np.random.default_rng(3)
def burst(name, mat, t0, dur, c0, n, vmax, sc, grav=4.9, up=1.0, mesh=None):
    for k in range(n):
        v = np.array([er.uniform(-vmax, vmax), er.uniform(-vmax, vmax), er.uniform(0.3, 1.0) * vmax * up])
        streak(name, sc, mat, t0, t0 + dur, lambda t, v=v: ((c0[0] + v[0] * (t - t0), c0[1] + v[1] * (t - t0), max(0.03, c0[2] + v[2] * (t - t0) - grav * (t - t0) ** 2)),), mesh=mesh)
HM = set004.house_mats(M, 0, 0, 1)
def orbit(t0, t1, n, mats, smin=0.15, smax=0.5, scale_fn=lambda t: 1.0):
    """detriti che girano attorno al tornado."""
    for k in range(n):
        h = er.uniform(0.15, 0.95); ph = er.uniform(0, 6.28); sp_ = er.uniform(3.5, 6.0); s = er.uniform(smin, smax); m = mats[int(er.integers(0, len(mats)))]; ax = er.uniform(0.5, 1.6)
        def fn(t, h=h, ph=ph, sp_=sp_, s=s, ax=ax):
            Q = tor(t); sc = Q['sc']; kk = h * 8; rr = (props011.ring_r(kk) + 0.5) * sc; a = ph + t * sp_
            return ((Q['loc'][0] + rr * math.cos(a) + Q['lean'] * kk * sc, Q['loc'][1] + rr * math.sin(a), Q['loc'][2] + props011.ring_z(kk) * sc), (s * ax * sc * scale_fn(t), s * sc * scale_fn(t), s * 0.6 * sc * scale_fn(t)), (t * 3 + ph, t * 2, a))
        streak('Detrito', (s, s, s), m, t0, t1, fn, mesh=set004.box_c())
orbit(0.9, 18.9, 22, HM[:3] + [M['wood']], scale_fn=lambda t: ramp(t, 0.9, 2.4))
orbit(29.3, TOTAL, 9, [T11['paper']], 0.25, 0.45)
burst('Polvere', M['dust'], 2.3, 0.9, (HOUSE[0], HOUSE[1] - 2.0, 0.3), 14, 3.5, (0.35, 0.35, 0.35), grav=0.5, up=0.4)
burst('Polvere', M['dust'], 8.4, 0.5, (CP0[0] - 1.0, CP0[1] + 0.2, 0.15), 7, 2.0, (0.15, 0.15, 0.15), grav=0.5, up=0.3)
for k in range(12):                                                                                 # vento sul poliziotto
    ph = k / 12; dz = er.uniform(1.2, 2.6); dy = er.uniform(-0.5, 0.5)
    streak('Vento', (0.5, 0.02, 0.02), M['cloudw'], 9.4, 11.3, lambda t, ph=ph, dz=dz, dy=dy: ((TOR[0] - 1.5 - 6.0 * ((t * 1.6 + ph) % 1.0), TOR[1] - 3.0 - 5.2 * ((t * 1.6 + ph) % 1.0) + dy, dz),), rot=(0, 0, 0.72))
for k in range(16):                                                                                 # vento in tribunale
    ph = k / 16; dz = er.uniform(1.0, 3.2); dy = er.uniform(-0.4, 0.4)
    streak('Vento', (0.6, 0.025, 0.025), M['cloudw'], 24.9, 26.8, lambda t, ph=ph, dz=dz, dy=dy: ((CAGE[0] + 1.3 + 7.0 * ((t * 1.7 + ph) % 1.0), CAGE[1] + 1.2 + dy + 1.2 * ((t * 1.7 + ph) % 1.0), dz + 0.8 * ((t * 1.7 + ph) % 1.0)),))
burst('Foglio', T11['paper'], 24.95, 1.6, (CX + 2.4, 0.2, 1.1), 12, 2.6, (0.2, 0.14, 0.01), grav=0.6, mesh=set004.box_c())
for bt in (27.37, 28.22): burst('Scintilla', N['spark'], bt, 0.45, (CX + 0.5, 2.3, 1.62), 7, 1.4, (0.05, 0.05, 0.05), grav=3.0)
burst('Polvere', M['dust'], 27.12, 0.5, (CX, 3.1, 1.6), 8, 1.2, (0.07, 0.07, 0.07), grav=0.5, up=0.4)
burst('Polvere', M['dust'], 29.2, 0.6, (JX, -1.0, 0.1), 10, 2.2, (0.14, 0.14, 0.14), grav=1.0, up=0.3)
burst('Scintilla', N['spark'], 18.2, 0.6, (TOR[0], TOR[1] - 2.6, 2.6), 10, 2.0, (0.08, 0.08, 0.08), grav=2.0)
burst('Polvere', M['dust'], 33.35, 1.0, (-0.5, -2.0, 0.1), 10, 2.0, (0.09, 0.09, 0.09), grav=0.6, up=0.4)

# ======================= camera =======================
def Z0(t): return (0, 0, 0)
def SHK(t): q = ramp(t, 33.3, 33.5); return (0.07 * math.sin(t * 53) * q, 0, 0.06 * math.sin(t * 41) * q)
SHOTS = [  # t0, t1, sub cam, p0, p1, sub mira, a0, a1, lente, f
    (0.0, 2.95, Z0, (-1.3, -6.8, 1.0), (-1.2, -6.2, 1.0), Z0, (-0.5, 4.0, 3.2), (-0.4, 4.0, 3.2), 24, 11),
    (2.95, 6.2, Z0, (-0.6, -6.4, 1.0), (-0.5, -6.0, 1.0), Z0, (0.7, 1.5, 3.0), (0.7, 1.5, 3.0), 24, 11),
    (6.2, 7.9, Z0, (-0.4, -4.4, 1.6), (-0.5, -4.1, 1.6), Z0, (-1.15, -1.0, 1.6), (-1.15, -1.0, 1.6), 40, 6),
    (7.9, 9.3, Z0, (-3.2, -9.4, 1.4), (-3.1, -9.0, 1.4), Z0, (-3.3, -1.6, 1.2), (-3.1, -1.6, 1.25), 28, 8),
    (9.3, 11.3, Z0, (-3.9, -7.0, 1.0), (-3.8, -6.6, 1.0), Z0, (-1.3, -0.5, 2.9), (-1.1, -0.3, 3.1), 24, 11),
    (11.3, 13.4, Z0, (-2.3, -5.6, 1.7), (-2.4, -5.2, 1.7), Z0, (CP0[0], CP0[1], 1.72), (CP0[0], CP0[1], 1.72), 55, 6),
    (13.4, 15.7, Z0, (-1.9, -6.6, 1.5), (-2.0, -6.2, 1.5), Z0, (CP0[0], CP0[1], 1.5), (CP0[0], CP0[1], 1.5), 40, 6),
    (15.7, 17.0, Z0, (1.6, -13.5, 6.0), (1.7, -12.5, 5.6), Z0, (2.2, 2.0, 2.2), (2.2, 2.0, 2.2), 24, 11),
    (17.0, 18.9, Z0, (1.0, -9.5, 1.5), (1.4, -8.5, 1.5), Z0, (2.6, 3.0, 2.9), (2.8, 3.0, 2.9), 24, 11),
    (18.9, 21.5, Z0, (JX, -6.8, 1.5), (JX, -6.4, 1.5), Z0, (JX, 0.6, 1.45), (JX, 0.6, 1.45), 35, 8),
    (21.5, 23.5, Z0, (CX - 0.45, -9.0, 1.6), (CX - 0.45, -8.5, 1.6), Z0, (CX - 0.45, 1.5, 1.75), (CX - 0.45, 1.5, 1.75), 26, 11),
    (23.5, 24.75, Z0, (CX + 0.2, -0.45, 2.25), (CX + 0.2, -0.3, 2.25), Z0, (CX + 0.05, 3.0, 2.05), (CX + 0.05, 3.0, 2.05), 35, 8),
    (24.75, 27.0, Z0, (CX - 0.2, -8.6, 1.6), (CX + 0.2, -8.2, 1.6), Z0, (CX - 0.2, 1.5, 2.6), (CX + 0.8, 1.5, 3.4), 24, 11),
    (27.0, 29.0, Z0, (CX + 0.2, -0.45, 2.25), (CX + 0.2, -0.3, 2.25), Z0, (CX + 0.15, 3.0, 2.0), (CX + 0.15, 3.0, 2.0), 35, 8),
    (29.0, 32.6, Z0, (JX + 1.0, -7.4, 1.4), (JX + 0.9, -6.4, 1.5), Z0, (JX + 0.9, 0.3, 1.5), (JX + 0.9, 0.3, 1.5), 30, 8),
    (32.6, 35.6, SHK, (0.6, -6.6, 1.4), (0.5, -6.2, 1.4), Z0, (-0.6, -0.8, 1.35), (-0.6, -0.8, 1.35), 28, 8),
    (35.6, 38.4, Z0, (JX - 0.5, -8.6, 1.4), (JX - 0.5, -7.9, 1.4), Z0, (JX - 0.4, -0.6, 1.5), (JX - 0.4, -0.6, 1.5), 30, 8),
]
camd = bpy.data.cameras.new('Cam'); cam = bpy.data.objects.new('Cam', camd); cac.objects.link(cam); scene.camera = cam
camd.clip_start = 0.1; camd.clip_end = 900; camd.sensor_width = 36
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
set_interp(camd, 'CONSTANT'); set_interp(flash_l, 'CONSTANT')
os.makedirs('../t011', exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath('../t011/pippo_t011.blend')); print('SAVED')
