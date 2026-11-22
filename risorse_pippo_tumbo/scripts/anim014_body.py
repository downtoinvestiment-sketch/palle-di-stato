T = props014.mats014()
OV = (-6.0, 1.5); VO = (11.0, 4.0); TW = [(-14.0, 18.0), (-25.0, 18.0)]; BX = -3.0; MCH = (BX, -1.6); KX = 600.0
# pulizia: via alberi sotto il vulcano e case sopra il nastro
for o in list(envc.objects):
    p = o.matrix_world.translation
    if o.name.startswith(('Tronco', 'Chioma')) and math.hypot(p.x - VO[0], p.y - VO[1]) < 7.5: bpy.data.objects.remove(o)
for o in list(envc.objects):
    if o.name.startswith(('Casa', 'Palazzo')):
        bb = [o.matrix_world @ Vector(c) for c in o.bound_box]; xs = [v.x for v in bb]; ys = [v.y for v in bb]
        if min(xs) < BX + 1.0 and max(xs) > BX - 1.0 and max(ys) < -3: bpy.data.objects.remove(o)
melt = [o for o in envc.objects if o.name.startswith('Casa') and o.location.x > 18 and -6 < o.location.y < 20]

oven = props014.oven(prc, T); oven['root'].location = (OV[0], OV[1], 0)
vol = props014.volcano(prc, T); vol['root'].location = (VO[0], VO[1], 0)
towers = []
for k, (x, y) in enumerate(TW): tw = props014.cooling_tower(prc, T, name='Torre%d' % k); tw.location = (x, y, 0); towers.append(tw)
pipes = [props014.pipe(prc, T, (TW[0][0] + 4.0, TW[0][1] - 1.5, 2.6), (8.0, 13.5, 2.6)), props014.pipe(prc, T, (8.0, 13.5, 2.6), (9.6, 8.6, 2.6)),
         props014.pipe(prc, T, (TW[1][0] + 4.0, TW[1][1] - 1.5, 2.6), (TW[0][0] - 4.0, TW[0][1] - 1.5, 2.6))]
belt = props014.conveyor(prc, T, BX, -2.5, -138.0)
mach, rollers = props014.intake(prc, T, MCH[0], MCH[1])
ksign = props014.kitchen(envc, T, KX)
TRK = props009.truck(prc, G9); trk, tbed, tload = TRK

# ======================= personaggi =======================
P = pippo.build_pippo(chc); Tb = tumbo.build_tumbo(chc, scale=0.75)
for r in (P['root'], Tb['root']): r.rotation_mode = 'XYZ'
for nm in 'LR': P['shoulder' + nm].rotation_mode = 'QUATERNION'
def qdir(d, rest=(0, 0, -1)): return Vector(rest).rotation_difference(Vector(d).normalized())

# ======================= oggetti =======================
pbread = props014.bread(chc, T, 'FettaPippo'); pbread.parent = P['shoulderR']; pbread.location = (0, -0.06, -0.62); pbread.scale = (0.3, 0.3, 0.3); pbread.rotation_euler = (PI, 0, 0)
crumb = ball_('Briciola', 0.035, (0, -0.03, -0.69), T['crust'], chc, parent=P['shoulderR'])
sbread = props014.bread(prc, T, 'FettaNastro'); sbread.scale = (0.6, 0.6, 0.6)
gbread = props014.bread(prc, T, 'FettaGigante'); gbread.scale = (2.8, 2.8, 2.8)
gtoast = props014.bread(prc, T, 'ToastGigante', toast=True); gtoast.scale = (2.8, 2.8, 2.8)

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
HOOK = 5.75
T_OV, T_VO, T_TW, T_BELT, T_TRK = 9.95, 15.0, 23.3, 27.75, 36.5
show(oven['root'], [(0.0, HOOK), (T_OV, TOTAL)]); keys(oven['root'], 'location', [(0.0, (OV[0], OV[1], 0)), (HOOK - 0.04, (OV[0], OV[1], 0)), (HOOK, (OV[0], OV[1], -4.6)), (T_OV, (OV[0], OV[1], -4.6)), (T_OV + 0.9, (OV[0], OV[1], 0.15)), (T_OV + 1.05, (OV[0], OV[1], 0))])
show(oven['dim'], [(T_OV, T_VO + 1.5)]); show(oven['bright'], [(0.0, HOOK), (T_VO + 1.5, TOTAL)])
show(vol['root'], [(0.0, HOOK), (T_VO, TOTAL)]); keys(vol['root'], 'location', [(0.0, (VO[0], VO[1], 0)), (HOOK - 0.04, (VO[0], VO[1], 0)), (HOOK, (VO[0], VO[1], -9.5)), (T_VO, (VO[0], VO[1], -9.5)), (T_VO + 1.4, (VO[0], VO[1], 0.2)), (T_VO + 1.6, (VO[0], VO[1], 0))])
for tw in towers: show(tw, [(0.0, HOOK), (T_TW, TOTAL)]); keys(tw, 'location', [(0.0, (tw.location.x, tw.location.y, 0)), (HOOK - 0.04, (tw.location.x, tw.location.y, 0)), (HOOK, (tw.location.x, tw.location.y, -15.5)), (T_TW, (tw.location.x, tw.location.y, -15.5)), (T_TW + 1.2, (tw.location.x, tw.location.y, 0.3)), (T_TW + 1.35, (tw.location.x, tw.location.y, 0))])
show(pipes, [(0.0, HOOK), (T_TW + 1.5, TOTAL)])
show(belt, [(0.0, HOOK), (T_BELT, TOTAL)]); show(mach, [(0.0, HOOK), (T_BELT, TOTAL)]); pop(mach, T_BELT, 0.3)
keys(belt, 'location', [(0.0, (0, 0, 0)), (HOOK - 0.04, (0, 0, 0)), (HOOK, (0, 0, -1.2)), (T_BELT, (0, 0, -1.2)), (T_BELT + 0.5, (0, 0, 0))])
show(trk, [(T_TRK, 41.6)]); show([tload] + list(desc(tload)) + [o for o in desc(tbed) if o.name.startswith('CamionScritta')], [(TOTAL + 1, TOTAL + 2)]); show(gbread, [(T_TRK, 40.3)]); show(gtoast, [(40.6, 45.15)])
show(sbread, [(29.6, 36.5)]); show(pbread, [(0.0, 29.6)]); show(crumb, [(45.9, TOTAL)])
for o in melt:
    s0 = tuple(o.scale)
    keys(o, 'scale', [(0.0, (s0[0] * 1.25, s0[1] * 1.25, s0[2] * 0.35)), (HOOK - 0.04, (s0[0] * 1.25, s0[1] * 1.25, s0[2] * 0.35)), (HOOK, s0), (20.6, s0), (23.2, (s0[0] * 1.25, s0[1] * 1.25, s0[2] * 0.35))])
door = oven['door']
keys(door, 'rotation_euler', [(0, (0, 0, 0)), (38.3, (0, 0, 0)), (38.6, (0, 0, 1.6)), (40.3, (0, 0, 1.6)), (40.5, (0, 0, 0)), (40.55, (0, 0, 0)), (40.75, (0, 0, 1.6)), (41.8, (0, 0, 1.6)), (42.1, (0, 0, 0))])

# ======================= pose =======================
DOWN = lambda s: (s * 0.14, 0, -1)
UP = dict(aL=(-0.35, -0.25, 1), aR=(0.35, -0.25, 1)); SHRUG = dict(aL=(-0.75, -0.3, -0.2), aR=(0.75, -0.3, -0.2))
HOLD = (0.45, -0.75, -0.25)                                                                           # braccio destro che mostra la fetta
G0 = (-0.6, -3.0)
def pp(t):
    S_ = dict(loc=(G0[0], G0[1], 0), rot=(0, 0, 0), aL=DOWN(-1), aR=HOLD, hL=0.0, hR=0.0, head=(0, 0, 0))
    if t < 2.55: S_.update(loc=(2.5, -3.5, 0), rot=(0, 0, -0.54), head=(0.05, 0.08 * math.sin(t * 2), 0))
    elif t < HOOK: S_.update(rot=(0, 0, 0.15), head=(0.05, 0.08 * math.sin(t * 2), 0))
    elif t < T_OV:                                                                                    # cucina
        turn = ramp(t, 8.3, 8.7) * (1 - ramp(t, 9.4, 9.8))
        S_.update(loc=(KX + 0.3, 0.2, 0), rot=(0, 0, PI * turn), head=(0, 0, 0), **(SHRUG if t > 9.0 else {}))
        if t <= 9.0: S_.update(aR=HOLD)
    elif t < 12.8: S_.update(loc=(-1.0, -3.6, 0), rot=(0, 0, -0.7), aL=(-0.4, -0.3, 0.8 * ramp(t, 11.2, 11.5)), head=(0.0, 0, -0.3))
    elif t < 14.9:                                                                                    # non scalda: mano nel forno
        S_.update(loc=(-4.3, -1.6, 0), rot=(0, 0, -0.35), head=(0.15, 0, 0.3), **(dict(aL=(-0.2, -1, 0.15)) if t < 14.0 else SHRUG))
    elif t < 19.7:                                                                                    # il vulcano
        jump = ramp(t, 17.3, 17.5) * (1 - ramp(t, 17.6, 17.9))
        S_.update(loc=(1.0, -3.2, 0.5 * jump), rot=(0, 0, -0.9), head=(-0.35, 0, 0), **(UP if t > 17.3 else {}))
    elif t < 23.3:                                                                                    # troppo caldo
        k = math.sin(t * 14); S_.update(loc=(1.0, -3.2, 0), rot=(0.08, 0, 0.2), aL=(-0.5, -0.3, 0.6 + 0.3 * k), aR=(0.5, -0.3, 0.6 - 0.3 * k), head=(0.05, 0, 0))
    elif t < 27.75: S_.update(loc=(-0.5, -4.2, 0), rot=(0, 0, 0.6), aR=(0.3, -0.5, 0.9 * ramp(t, 24.8, 25.1)), head=(-0.35, 0, 0.4))
    elif t < 36.5:
        if t < 32.3: S_.update(loc=(-0.8, -2.9, 0), rot=(0, 0, 0.4), aR=(0.35, -0.6, 0.6) if t < 29.6 else DOWN(1))
        else:
            fp = ramp(t, 35.0, 35.3); S_.update(loc=(-0.8, -2.9, 0), rot=(0, 0, 0.35 + 0.6 * ramp(t, 34.2, 34.5)), aR=lerp(DOWN(1), (0.15, -0.7, 0.75), fp), head=(0.25 * fp, 0, -0.5 * ramp(t, 34.2, 34.5) * (1 - fp)))
    elif t < 45.9:
        S_.update(loc=(2.6, -4.2, 0), rot=(0, 0, -0.75), aR=DOWN(1), head=(0, 0, 0.0))
        if 40.6 < t < 44.4: S_.update(**UP)
        if t > 44.5: S_.update(aL=(-0.5, -0.3, 0.85 * ramp(t, 44.6, 44.8)), aR=(0.5, -0.3, 0.85 * ramp(t, 44.6, 44.8)))
    else: S_.update(loc=(-1.6, -3.6, 0), rot=(0, 0, 0.1), aR=(-0.15, -0.9, 0.3), head=(0.12, 0, 0))
    return S_
def tp(t):
    S_ = dict(loc=(0.6, -3.4, 0), rot=(0, 0, 0.2), head=(0, 0, 0), tail=-1.0 + 0.5 * math.sin(t * 12))
    if t < 2.55: S_.update(loc=(3.5, -4.2, 0), rot=(0, 0, -0.4), head=(-0.3, 0, -0.6), tail=-0.4)
    elif t < HOOK: S_.update(loc=(0.6, -3.4, 0), head=(-0.3, 0, -0.6), tail=-0.4)
    elif t < T_OV: S_.update(loc=(KX + 1.5, -0.4, 0), rot=(0, 0, -0.3), head=(-0.4, 0, 0.5))
    elif t < 17.3: S_.update(loc=(0.4, -3.9, 0), rot=(0, 0, -0.5), head=(-0.3, 0, -0.3))
    elif t < 19.7:                                                                                    # scappa
        u = ramp(t, 17.4, 19.0); k = math.sin(t * 22)
        S_.update(loc=(0.4 - 10.0 * u, -3.9 - 2.0 * u, 0.05 * abs(k)), rot=(0, 0, PI / 2 + 0.3), head=(0, 0, 0))
    elif t < 36.5: S_.update(loc=(-1.5, -4.4, 0), rot=(0, 0, 0.3), head=(-0.3, 0, 0.2))
    elif t < 44.5: S_.update(loc=(-2.4, -4.8, 0), rot=(0, 0, -1.4 if t > 40.7 else 0.3), head=(-0.4 * (t > 40.7), 0, 0), tail=-0.2)
    elif t < 45.2:
        u = (t - 44.5) / 0.7; S_.update(loc=(-2.4 - 3.4 * u, -4.8 + 1.2 * u, 3.2 * math.sin(PI * u)), rot=(-0.3, 0, PI / 2 + 0.3))
    else: S_.update(loc=(-0.2, -4.4, 0), rot=(0, 0, -0.4), head=(-0.2, 0, 0.3), tail=-0.4)
    return S_
def trk_pos(t):
    u = ramp(t, T_TRK, 38.2); y = -28.0 + 20.5 * (1 - (1 - u) ** 2)
    if t > 39.6: v = (t - 39.6) / 1.6; y -= 22.0 * v * v
    return (0.0, y, 0)
def gbread_pos(t):
    """fetta gigante: sul camion, poi in volo verso il forno, poi dentro."""
    tr = trk_pos(min(t, 38.3)); onbed = (tr[0], tr[1] - 1.05, 1.0)
    if t < 38.6: return onbed, (0, 0, 0)
    door = (OV[0], OV[1] - 2.3, 0.5)
    if t < 39.7:
        u = (t - 38.6) / 1.1; return (onbed[0] + (door[0] - onbed[0]) * u, onbed[1] + (door[1] - onbed[1]) * u, onbed[2] + (door[2] - onbed[2]) * u + 4.0 * math.sin(PI * u)), (0, 0, 0.6 * math.sin(PI * u))
    u = ramp(t, 39.7, 40.2); return (door[0], door[1] + 2.4 * u, door[2]), (0, 0, 0)
def gtoast_pos(t):
    u = ramp(t, 40.75, 41.6); return (OV[0], OV[1] + 0.2 - 4.9 * u, 0.5 * (1 - u)), (0, 0, 0)
def sbread_pos(t):
    if t < 34.1: u = (t - 29.6) / 4.5; y = -60.0 + (MCH[1] - 1.0 + 60.0) * u; return (BX, y, 0.9), (0, 0, 0)
    if t < 34.6: u = (t - 34.1) / 0.5; return (BX, MCH[1] - 1.0 + 1.0 * u, 0.9 + 0.5 * math.sin(PI * u * 0.5)), (0, 0, 0)
    u = min(1.0, (t - 34.6) / 0.55); return (BX, MCH[1], max(0.03, 1.3 - 1.27 * u * u)), (1.4 * u, 0.3 * u, 0)

# ======================= chiavi =======================
TR = Tb['root']
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
    fat = ramp(t, 44.95, 45.2); Tb['body'].scale = (1 + 0.5 * fat, 1 + 0.5 * fat, 1 + 0.25 * fat); Tb['body'].keyframe_insert('scale', frame=f)
    # ago del termometro
    if t < HOOK or t > T_VO + 1.4: b = 1.35 * PI + 0.12 * math.sin(t * 23)
    else: b = -0.3 * PI + 0.05 * math.sin(t * 9) * (12.8 < t < 14.9)
    oven['needle'].rotation_euler = (0, b, 0); oven['needle'].keyframe_insert('rotation_euler', frame=f)
    # tremito del vulcano mentre sale
    if T_VO < t < T_VO + 1.7: vol['root'].rotation_euler = (0.02 * math.sin(t * 41), 0.02 * math.sin(t * 37), 0); vol['root'].keyframe_insert('rotation_euler', frame=f)
    if T_TRK - 0.1 < t:
        l = trk_pos(t); trk.location = l; trk.rotation_euler = (0, 0, PI); trk.keyframe_insert('location', frame=f); trk.keyframe_insert('rotation_euler', frame=f)
    if T_TRK - 0.1 < t < 40.4:
        l, e = gbread_pos(t); gbread.location = l; gbread.rotation_euler = e; gbread.keyframe_insert('location', frame=f); gbread.keyframe_insert('rotation_euler', frame=f)
    if 40.5 < t < 45.3:
        l, e = gtoast_pos(t); gtoast.location = l; gtoast.rotation_euler = e; gtoast.keyframe_insert('location', frame=f); gtoast.keyframe_insert('rotation_euler', frame=f)
        eat = ramp(t, 44.8, 45.12); s_ = 2.8 * (1 - eat) + 0.001; gtoast.scale = (s_, s_, s_); gtoast.keyframe_insert('scale', frame=f)
    if 29.5 < t < 36.6:
        l, e = sbread_pos(t); sbread.location = l; sbread.rotation_euler = e; sbread.keyframe_insert('location', frame=f); sbread.keyframe_insert('rotation_euler', frame=f)
    if t < HOOK or 34.0 < t < 36.6:
        for k_, rl in enumerate(rollers): rl.rotation_euler = ((1 if k_ else -1) * t * 6.0, 0, 0); rl.keyframe_insert('rotation_euler', frame=f)

_last = {}
def _ex(key, fn, t, k):
    if key in _last and t - 0.06 > _last[key][1]: fn(fr(t - 0.06), **_last[key][0])
    fn(fr(t), **k); _last[key] = (k, t)
def pex(t, **k): _ex('p', lambda f, **kk: pippo.express(P, f, **kk), t, k)
def tex(t, **k): _ex('t', lambda f, **kk: tumbo.tumbo_express(Tb, f, **kk), t, k)
pex(0.0, brow=1.0, eye_open=0.65, mouth_open=0.0); pex(HOOK + 0.1, smile=0.8, brow_lift=0.4, look=(0, -0.3)); pex(8.4, brow=-0.5, brow_lift=0.6, eye_scale=1.2, mouth_open=0.5)
pex(T_OV + 0.1, smile=1.0, brow=0.8, mouth_open=0.4); pex(13.0, brow=0.6, eye_open=0.7, mouth_open=0.1); pex(T_VO + 0.1, smile=1.0, brow=0.9, mouth_open=0.6)
pex(17.4, brow=-0.8, brow_lift=0.9, eye_scale=1.35, mouth_open=1.0); pex(19.8, brow=-0.6, brow_lift=0.5, eye_open=0.6, mouth_open=0.7); pex(T_TW + 0.1, smile=1.0, brow=0.8, mouth_open=0.4)
pex(T_BELT + 0.1, smile=1.0, brow=0.7, mouth_open=0.5); pex(32.4, brow=1.0, eye_open=0.6, mouth_open=0.0); pex(35.0, brow=-0.5, brow_lift=0.6, eye_open=0.4, mouth_open=0.4)
pex(T_TRK + 0.1, smile=1.0, brow=0.9, mouth_open=0.4); pex(40.8, smile=1.0, mouth_open=0.9, brow_lift=0.6, eye_scale=1.2); pex(44.6, brow=-0.8, brow_lift=0.9, eye_scale=1.4, mouth_open=1.0)
pex(45.95, brow=1.0, eye_open=0.55, mouth_open=0.0, look=(0, -0.4)); pex(47.8, brow=1.0, eye_open=0.6, mouth_open=0.0, look=(0, 0))
tex(0.0, eye_open=0.7, brow=0.4); tex(HOOK + 0.1, tongue=0.6); tex(17.4, eye_scale=1.45, brow=-0.8); tex(19.8, tongue=0.4); tex(40.7, tongue=1.0, eye_scale=1.3); tex(45.2, eye_open=0.6, tongue=0.8)

# ======================= effetti =======================
def streak(name, sc, mat, t0, t1, fn, parent=None, mesh=None, rot=None):
    o = obj(name, mesh or shared_mesh('sphere_lo'), (0, 0, -80), sc, mat, prc, parent=parent)
    if rot: o.rotation_euler = rot
    o.hide_render = True; o.keyframe_insert('hide_render', frame=1)
    for (a, b) in (t0 if isinstance(t0, list) else [(t0, t1)]):
        o.hide_render = False; o.keyframe_insert('hide_render', frame=fr(a))
        if b < TOTAL: o.hide_render = True; o.keyframe_insert('hide_render', frame=fr(b))
        for f in range(fr(a), min(NF, fr(b)) + 1):
            r_ = fn((f - 1) / FPS); o.location = r_[0]; o.keyframe_insert('location', frame=f)
            if len(r_) > 1: o.scale = r_[1]; o.keyframe_insert('scale', frame=f)
    return o
er = np.random.default_rng(3)
ERUPT = [(0.0, HOOK), (16.4, TOTAL)]
VT = (VO[0], VO[1], 7.9)
for k in range(22):                                                                                   # lapilli
    ph = er.uniform(0, 1); vx, vy, vz = er.uniform(-3.5, 3.5), er.uniform(-3.5, 3.5), er.uniform(9, 14); s = er.uniform(0.15, 0.35)
    def fn(t, ph=ph, vx=vx, vy=vy, vz=vz):
        tau = ((t * 0.5 + ph) % 1.0) * 2.0; return ((VT[0] + vx * tau, VT[1] + vy * tau, max(-1.0, VT[2] + vz * tau - 4.9 * tau * tau)),)
    streak('Lapillo', (s, s, s), T['lava2'] if k % 3 == 0 else T['lava'], ERUPT, None, fn)
for k in range(12):                                                                                   # colonna di fumo
    ph = k / 12; dx, dy = er.uniform(-1.2, 1.2), er.uniform(-1.2, 1.2)
    streak('Fumo', (1, 1, 1), T['smoke'], ERUPT, None, lambda t, ph=ph, dx=dx, dy=dy: ((VT[0] + dx + 3.0 * ((t * 0.18 + ph) % 1.0), VT[1] + dy, VT[2] + 1.0 + 16.0 * ((t * 0.18 + ph) % 1.0)), (1.2 + 3.0 * ((t * 0.18 + ph) % 1.0),) * 3))
for tw in TW:                                                                                         # vapore delle torri
    for k in range(9):
        ph = k / 9; dx, dy = er.uniform(-1.5, 1.5), er.uniform(-1.5, 1.5)
        streak('Vapore', (1, 1, 1), T['steam'], [(0.0, HOOK), (T_TW + 1.3, TOTAL)], None, lambda t, ph=ph, dx=dx, dy=dy, tw=tw: ((tw[0] + dx + 2.0 * ((t * 0.22 + ph) % 1.0), tw[1] + dy, 15.0 + 9.0 * ((t * 0.22 + ph) % 1.0)), (1.6 + 2.6 * ((t * 0.22 + ph) % 1.0),) * 3))
for k in range(6):                                                                                    # fumo dal camino del forno
    ph = k / 6; c = (OV[0] + oven['chimney'][0], OV[1], oven['chimney'][2])
    streak('FumoCamino', (1, 1, 1), T['smoke'], [(0.0, HOOK), (T_VO + 1.5, TOTAL)], None, lambda t, ph=ph, c=c: ((c[0] + 0.8 * ((t * 0.4 + ph) % 1.0), c[1], c[2] + 3.0 * ((t * 0.4 + ph) % 1.0)), (0.3 + 0.8 * ((t * 0.4 + ph) % 1.0),) * 3))
for k in range(10):                                                                                   # pozze di lava sotto le case fuse
    if not melt: break
    o_ = melt[k % len(melt)]; x, y = o_.location.x + er.uniform(-2.5, 2.5), o_.location.y + er.uniform(-3, 3)
    p_ = obj('PozzaLava', shared_mesh('sphere_lo'), (x, y, 0.02), (er.uniform(0.8, 1.6), er.uniform(0.8, 1.6), 0.05), T['lava'], prc); show(p_, [(0.0, HOOK), (21.0, TOTAL)])
for k in range(8):                                                                                    # sudore
    ph = k / 8; sx = -1 if k % 2 else 1
    streak('Sudore', (0.035, 0.035, 0.06), G9['puddle'], 19.7, 23.3, lambda t, ph=ph, sx=sx: ((1.0 + sx * 0.38, -3.45, 1.95 - 0.8 * ((t * 1.3 + ph) % 1.0)),))
def burst(name, mat, t0, dur, c0, n, vmax, sc, grav=4.9, up=1.0):
    for k in range(n):
        v = np.array([er.uniform(-vmax, vmax), er.uniform(-vmax, vmax), er.uniform(0.3, 1.0) * vmax * up])
        streak(name, sc, mat, t0, t0 + dur, lambda t, v=v: ((c0[0] + v[0] * (t - t0), c0[1] + v[1] * (t - t0), max(0.03, c0[2] + v[2] * (t - t0) - grav * (t - t0) ** 2)),))
burst('Polvere', M['dust'], T_OV + 0.8, 0.8, (OV[0], OV[1] - 2.0, 0.2), 10, 2.5, (0.25, 0.25, 0.25), grav=0.5, up=0.4)
burst('Polvere', M['dust'], T_VO + 1.2, 1.0, (VO[0], VO[1] - 5.5, 0.3), 14, 3.0, (0.4, 0.4, 0.4), grav=0.5, up=0.4)
burst('Briciole', T['crust'], 44.95, 1.0, (OV[0], -3.0, 1.6), 30, 3.5, (0.07, 0.07, 0.05))
burst('Briciole', T['toast'], 44.95, 1.0, (OV[0], -3.0, 1.6), 20, 3.0, (0.06, 0.06, 0.04))
for k in range(8):                                                                                    # vapore del toast
    ph = k / 8; dx = er.uniform(-1.0, 1.0)
    streak('VaporeToast', (0.3, 0.3, 0.3), T['steam'], 41.4, 44.9, lambda t, ph=ph, dx=dx: ((OV[0] + dx, -3.2, 2.9 + 1.8 * ((t * 0.6 + ph) % 1.0)), (max(0.001, 0.35 * math.sin(PI * ((t * 0.6 + ph) % 1.0))),) * 3))
for k in range(7):                                                                                    # luccichii
    a = 2 * PI * k / 7
    streak('Luccichio', (0.08, 0.08, 0.08), N['spark'], 41.6, 44.4, lambda t, a=a: ((OV[0] + 1.9 * math.cos(a + t), -3.6, 1.5 + 1.6 * math.sin(a + t)), (0.06 + 0.04 * math.sin(t * 8 + a),) * 3))

# ======================= camera =======================
def Z0(t): return (0, 0, 0)
def SB(t): return sbread_pos(t)[0]
def SHK(t): q = ramp(t, T_VO, T_VO + 0.2) * (1 - ramp(t, T_VO + 1.4, T_VO + 1.7)); return (0.08 * math.sin(t * 51) * q, 0, 0.07 * math.sin(t * 43) * q)
SHOTS = [  # t0, t1, sub cam, p0, p1, sub mira, a0, a1, lente, f
    (0.0, 2.55, Z0, (-0.5, -8.6, 1.45), (-0.4, -8.2, 1.45), Z0, (3.6, -2.0, 2.7), (3.6, -2.0, 2.7), 24, 8),
    (2.55, HOOK, Z0, (1.5, -19.0, 4.5), (1.3, -17.5, 4.3), Z0, (-1.0, 6.0, 5.0), (-1.0, 6.0, 5.0), 22, 11),
    (HOOK, 8.3, Z0, (KX + 0.6, -4.0, 1.5), (KX + 0.55, -3.7, 1.5), Z0, (KX + 0.4, 0.3, 1.45), (KX + 0.4, 0.3, 1.45), 32, 5),
    (8.3, T_OV, Z0, (KX + 0.8, -2.0, 1.55), (KX + 0.75, -1.8, 1.5), Z0, (KX + 0.15, 1.6, 1.2), (KX + 0.15, 1.6, 1.15), 32, 5),
    (T_OV, 12.8, Z0, (1.8, -11.0, 2.0), (1.6, -10.4, 2.0), Z0, (-3.8, 0.5, 2.3), (-3.8, 0.5, 2.3), 24, 11),
    (12.8, T_VO, Z0, (-1.8, -5.6, 2.2), (-1.9, -5.3, 2.2), Z0, (-4.2, -0.8, 2.4), (-4.2, -0.8, 2.4), 32, 6),
    (T_VO, 17.3, SHK, (0.5, -12.5, 2.0), (0.8, -12.0, 2.0), Z0, (9.0, 3.0, 4.5), (9.0, 3.0, 4.5), 22, 11),
    (17.3, 19.7, Z0, (3.0, -8.5, 0.8), (3.2, -8.0, 0.8), Z0, (5.0, 0.0, 4.5), (5.0, 0.0, 4.6), 20, 11),
    (19.7, 21.4, Z0, (1.9, -6.3, 1.65), (1.85, -6.0, 1.65), Z0, (1.0, -3.2, 1.75), (1.0, -3.2, 1.75), 42, 5),
    (21.4, T_TW, Z0, (14.5, -9.5, 2.5), (14.3, -9.0, 2.5), Z0, (21.5, 4.0, 1.6), (21.5, 4.0, 1.6), 26, 11),
    (T_TW, T_BELT, Z0, (1.0, -11.0, 2.2), (0.6, -10.4, 2.4), Z0, (-14.0, 13.0, 7.5), (-14.0, 13.0, 8.0), 22, 11),
    (T_BELT, 29.6, Z0, (5.0, 4.0, 18.0), (5.0, 2.0, 19.0), Z0, (-3.0, -55.0, 0.0), (-3.0, -60.0, 0.0), 24, 22),
    (29.6, 32.3, SB, (1.6, -1.6, 0.75), (1.6, -1.6, 0.75), SB, (0, 0.15, 0.3), (0, 0.15, 0.3), 30, 6),
    (32.3, 34.1, Z0, (0.7, -6.6, 1.6), (0.65, -6.3, 1.6), Z0, (-1.2, -2.4, 1.5), (-1.2, -2.4, 1.5), 36, 5),
    (34.1, T_TRK, Z0, (-0.3, -5.2, 1.6), (-0.4, -5.0, 1.55), Z0, (-2.6, -1.6, 1.0), (-2.6, -1.6, 0.8), 30, 6),
    (T_TRK, 40.6, Z0, (6.5, -15.0, 3.0), (6.0, -14.0, 3.0), Z0, (-2.0, -5.0, 2.0), (-3.5, -2.5, 2.0), 24, 11),
    (40.6, 44.4, Z0, (1.8, -11.5, 2.0), (1.6, -11.0, 2.0), Z0, (-5.0, -3.0, 1.9), (-5.0, -3.0, 1.9), 28, 8),
    (44.4, 45.9, Z0, (1.5, -12.0, 1.8), (1.4, -11.8, 1.8), Z0, (-4.0, -3.5, 1.6), (-4.0, -3.5, 1.6), 24, 11),
    (45.9, 49.9, Z0, (-0.9, -6.4, 1.6), (-0.95, -6.1, 1.6), Z0, (-1.7, -3.6, 1.6), (-1.7, -3.6, 1.55), 40, 5),
]
camd = bpy.data.cameras.new('Cam'); cam = bpy.data.objects.new('Cam', camd); cac.objects.link(cam); scene.camera = cam
camd.clip_start = 0.05; camd.clip_end = 900; camd.sensor_width = 36
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
set_interp(camd, 'CONSTANT')
for o in melt:
    for fc in all_fcurves(o):
        for kp in fc.keyframe_points:
            if abs(kp.co[0] - fr(HOOK)) <= 1: kp.interpolation = 'CONSTANT'
lookdev.upgrade(scene, 720, 1280, samples=12, world=0.36, sun_e=6.5, exposure=-0.1)
area_ = bpy.data.lights.new('LuceCucina', 'AREA'); area_.size = 4.0; area_.energy = 300; ao = bpy.data.objects.new('LuceCucina', area_); prc.objects.link(ao); ao.location = (KX, -1.5, 3.4)
os.makedirs('../t014', exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath('../t014/pippo_t014.blend')); print('SAVED')
