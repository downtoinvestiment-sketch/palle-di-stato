H = props010.mats010()
JX = 200.0; CX = 300.0
bars, board = props010.jail_set(envc, H, JX); props010.court_set(envc, H, CX)
CAGE = (CX - 3.0, 0.6)
cage = props010.cage(envc, H); cage.location = (CAGE[0], CAGE[1], 0)

# ======================= personaggi =======================
P = pippo.build_pippo(chc); Tb = tumbo.build_tumbo(chc, scale=0.75); G = props009.gualtiero(chc, G9); S = props010.sun_char(chc, H); C = props010.cop(chc)
for r in (P['root'], Tb['root'], G['root'], C['root']): r.rotation_mode = 'XYZ'
for R_ in (P, G):
    for nm in 'LR': R_['shoulder' + nm].rotation_mode = 'QUATERNION'
def qdir(d, rest=(0, 0, -1)): return Vector(rest).rotation_difference(Vector(d).normalized())
def bsdf(name): return [n for n in bpy.data.materials[name].node_tree.nodes if n.type == 'BSDF_PRINCIPLED'][0].inputs['Base Color']
RED = (0.95, 0.13, 0.08, 1); SOOT = (0.035, 0.03, 0.03, 1)
SOOT_T = [(39.25, 40.2), (43.25, TOTAL + 1)]
def sooty(t): return any(a <= t < b for a, b in SOOT_T)
for nm, base in (('P_Skin', RED), ('P_SkinD', (0.85, 0.08, 0.05, 1)), ('P_Hoodie', None), ('P_HoodieD', None), ('P_Hair1', None), ('P_Hair2', None)):
    inp = bsdf(nm); base = base or tuple(inp.default_value)
    for f in range(1, NF + 1):
        inp.default_value = SOOT if sooty((f - 1) / FPS) else base; inp.keyframe_insert('default_value', frame=f)

# ======================= oggetti =======================
BED = (-3.6, -1.5); SUNP = (-5.0, 1.0, 5.4); GARD = (-5.0, -1.5)
bed = props010.sunbed(prc, H); bed.location = (BED[0], BED[1], 0)
phone = props010.phone(chc, H, P['shoulderR'])
pcar, lred, lblue = props010.police_car(prc, H, G9); pcar.rotation_euler = (0, 0, PI)
LA = (-5.0, -5.4, 1.5); LB = (SUNP[0], SUNP[1] - 0.9, SUNP[2] - 0.75); LD = (LB[0] - LA[0], LB[1] - LA[1], LB[2] - LA[2]); LL = math.sqrt(sum(v * v for v in LD))
ladder = props010.ext_ladder(prc, H, LL); ladder.location = LA; ladder.rotation_euler = (-math.atan2(LD[1], LD[2]), 0, 0)
wig = props010.wig(chc, H, Tb['head'], s=1.5); gavel = props010.gavel(prc, H, None, (CX + 0.5, 2.75, 1.6))
tie = props010.tie(chc, H, G['root']); case = props010.briefcase(chc, H, G['shoulderR'])
gun = props009.hand_tool(chc, G9, G['shoulderL'], 'gun'); pack = props009.backpack(chc, G9, G['root']); flame = props009.flame(chc, G9, gun, (0, 0, -1.06))
burn = ball_('Ustione', 1.0, (0, 0.20, 0.40), H['burn'], chc, parent=P['body'], sc=(0.20, 0.07, 0.30))
rcloud = props010.raincloud(prc, H); rcloud.location = (GARD[0], GARD[1] + 0.2, 3.35)
fl_l = bpy.data.lights.new('LuceFiamma', 'POINT'); fl_o = bpy.data.objects.new('LuceFiamma', fl_l); prc.objects.link(fl_o); fl_l.color = (1.0, 0.55, 0.2); fl_l.shadow_soft_size = 0.4; fl_o.location = (-8.6, -2.6, 1.9)
flash_l = bpy.data.lights.new('Flash', 'POINT'); flash_o = bpy.data.objects.new('Flash', flash_l); prc.objects.link(flash_o); flash_o.location = (JX, -3.5, 2.6)
stars = []
_sr = np.random.default_rng(5)
for k in range(70):
    an = _sr.uniform(0.15, PI - 0.15); el = _sr.uniform(0.12, 1.2); rr = 160
    stars.append(ball_('Stella', _sr.uniform(0.35, 0.8), (rr * math.cos(an) * math.cos(el), rr * math.sin(an) * math.cos(el), rr * math.sin(el)), H['star'], prc))
puffs_all = [o for o in bpy.data.objects if o.name.startswith('Puff')]

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
DARK = [(33.9, 40.2), (43.25, TOTAL + 1)]
def dark(t): return any(a <= t < b for a, b in DARK)
show(puffs_all, [(0.0, 33.9), (40.2, 43.25)]); show(stars, [(33.9, 40.2), (43.25, TOTAL)])
show(bed, [(0.0, 5.3)]); show(phone, [(10.6, 12.2), (40.2, 43.25)])
show(pcar, [(12.2, 14.95)]); show(ladder, [(12.7, 14.2)]); show(C['root'], [(12.9, 14.2)])
keys(ladder, 'scale', [(12.7, (1, 1, 0.02)), (13.15, (1, 1, 1.03)), (13.25, (1, 1, 1))])
show(S['glasses'], [(0.0, 13.9)]); show(S['cuffs'], [(13.9, TOTAL)]); pop(S['cuffs'], 13.9, 0.2); show(S['halo'], [(25.6, 27.7)]); pop(S['halo'], 25.6, 0.25)
show(board, [(14.95, 16.15)]); board.location = (JX, 0.0, 0.95)
keys(bars, 'location', [(16.0, (JX, -0.9, 9.0)), (16.2, (JX, -0.9, 9.0)), (16.36, (JX, -0.9, 0.0)), (16.42, (JX, -0.9, 0.12)), (16.48, (JX, -0.9, 0.0))])
show(wig, [(19.9, 33.35)]); show(tie, [(19.9, 33.35)]); show(case, [(19.9, 33.35)]); show(gun, [(36.9, TOTAL)]); show(pack, [(36.9, TOTAL)])
show(burn, [(29.45, 30.8)]); show(rcloud, [(40.2, 43.25)]); pop(rcloud, 40.2, 0.3)
keys(gavel, 'rotation_euler', [(30.8, (0.3, 0, 0)), (31.25, (0.1, 0, 0)), (31.37, (1.45, 0, 0)), (31.6, (0.3, 0, 0)), (32.2, (0.1, 0, 0)), (32.32, (1.45, 0, 0)), (32.55, (0.5, 0, 0))])

# ======================= pose =======================
DOWN = lambda s: (s * 0.14, 0, -1)
UP = dict(aL=(-0.35, -0.25, 1), aR=(0.35, -0.25, 1)); FIST = dict(aL=(-0.55, -0.15, -0.8), aR=(0.55, -0.15, -0.8))
def pp(t):
    S_ = dict(loc=(0, 0, 0), rot=(0, 0, 0), aL=DOWN(-1), aR=DOWN(1), hL=0.0, hR=0.0, head=(0, 0, 0))
    if t < 5.3:                                    # arrostito sulla sdraio
        k = math.sin(t * 17); j = 0.02 * math.sin(t * 41)
        S_.update(loc=(BED[0] - 0.60 + j, BED[1], 0.065), rot=(-0.9, 0, PI / 2), hL=-0.67 + 0.25 * k, hR=-0.67 - 0.25 * k, aL=(-0.6, -0.5 + 0.3 * k, 0.6), aR=(0.6, -0.5 - 0.3 * k, 0.6), head=(0.6, 0, -0.5 + 0.2 * math.sin(t * 6)))
    elif t < 7.6: S_.update(loc=(-8.1 + 0.02 * math.sin(t * 40), -1.5, 0), rot=(0.1, 0, -0.35), head=(0, 0, -0.5), **FIST)
    elif t < 10.6:                                 # team Pippo o team Sole
        S_.update(loc=(GARD[0], GARD[1], 0.06 * abs(math.sin(t * 9))), rot=(0, 0, 0.35), aR=(0.25, 0.25, 1.0), aL=(-0.55, -0.15, -0.8), head=(-0.3, 0, 0))
    elif t < 12.2: S_.update(loc=(GARD[0], GARD[1], 0), rot=(0, 0, 0.0), aR=(0.12, -0.28, 0.95), aL=(-0.6, -0.5, 0.3 + 0.3 * math.sin(t * 14)), head=(0, 0.12, 0))
    elif t < 19.9:                                 # l'arresto
        ch = ramp(t, 13.9, 14.1)
        S_.update(loc=(-7.6, -2.9, 0.15 * ch * abs(math.sin(t * 10))), rot=(0, 0, 0.9), aL=lerp((-0.4, -0.2, -0.85), UP['aL'], ch), aR=lerp((0.3, 0.5, 0.9), UP['aR'], ch), head=(-0.3, 0, 0))
    elif t < 33.35:                                # il tribunale
        if t < 27.7: S_.update(loc=(CX + 2.4, 0.95, 0), rot=(0, 0, 0.3), aR=(0.6, -0.6, -0.3), aL=(-0.5, -0.15, -0.8), head=(0, 0, 0.35))
        elif t < 30.8:
            tr = ramp(t, 29.35, 29.7)
            S_.update(loc=(CX + 1.0, -1.2, 0), rot=(0.12 * tr, 0, PI * tr), aR=lerp((0.3, -0.5, 0.85), (0.75, 0.2, 0.6), tr), aL=lerp((-0.5, -0.15, -0.8), (-0.75, 0.2, 0.6), tr), head=(0, 0, -0.9 * tr))
        else:
            k = abs(math.sin((t - 31.3) * 8)) * (t > 31.3)
            S_.update(loc=(CX + 1.0, -1.2, 0.25 * k), rot=(0, 0, 0.2), head=(-0.15 * (t > 31.3), 0, 0), **(UP if t > 31.3 else FIST))
    elif t < 40.2:                                 # buio
        dk = ramp(t, 33.9, 34.1); hit = ramp(t, 39.0, 39.2); lk = math.sin((t - 34.2) * 2.6) * dk * (1 - ramp(t, 36.9, 37.2))
        S_.update(loc=(-7.5, -1.5, 0.12 * (1 - dk) * abs(math.sin(t * 9))), rot=(-0.12 * hit, 0, -0.45 * ramp(t, 36.9, 37.3)),
                  aL=lerp(lerp(UP['aL'], (-0.4, -0.75, 0.1), dk), (-1, 0, 0.25), hit), aR=lerp(lerp(UP['aR'], (0.4, -0.75, 0.1), dk), (1, 0, 0.25), hit), head=(0, 0, 0.8 * lk - 0.45 * ramp(t, 36.9, 37.3)))
    elif t < 43.25:                                # prossimo episodio: la pioggia
        S_.update(loc=(GARD[0], GARD[1], 0), rot=(0, 0, 0.2), aR=(0.12, -0.28, 0.95), aL=(-0.3, 0.2, 1.0), head=(-0.3, 0.1, 0))
    else: S_.update(loc=(-7.5, -1.5, 0), rot=(0, 0, -0.45 + 0.45 * ramp(t, 44.2, 44.5)), aL=(-1, 0, 0.25 - 1.0 * ramp(t, 43.6, 44.0)), aR=(1, 0, 0.25 - 1.0 * ramp(t, 43.6, 44.0)), head=(0, 0, -0.45 * (1 - ramp(t, 44.2, 44.5))))
    return S_

def gp(t):
    S_ = dict(loc=(0, 0, 0), rot=(0, 0, 0), aL=DOWN(-1), aR=DOWN(1), hL=0.0, hR=0.0, head=(0, 0, 0), belly=1.0)
    if t < 5.3: S_.update(loc=(-10.6, 1.2, 0), rot=(0, 0, PI / 2 + 0.3))
    elif t < 7.6:                                  # ride del gambero
        b = 0.06 * abs(math.sin(t * 13))
        S_.update(loc=(-10.3, -1.5, b), rot=(-0.12, 0, 0.35), aR=(0.75, -0.6, 0.1), aL=(0.3, -0.75, -0.55), head=(-0.25, 0, 0.5), belly=1.0 + 0.08 * math.sin(t * 26))
    elif t < 19.9: S_.update(loc=(-10.6, 1.2, 0), rot=(0, 0, PI / 2 + 0.3))
    elif t < 33.35:                                # l'avvocato
        talk = ramp(t, 24.9, 25.3) * (1 - ramp(t, 27.5, 27.9)); obj_ = ramp(t, 29.6, 29.9) * (1 - ramp(t, 30.6, 30.8)); lost = (t > 31.3)
        aL = lerp(lerp((-0.3, -0.5, -0.8), (-0.95, -0.25, 0.25 + 0.12 * math.sin(t * 9)), talk), (-0.3, -0.4, 1.0), obj_)
        if lost: aL = (-0.5, -0.3, 0.85)
        S_.update(loc=(CX - 1.2, -0.6, 0.04 * abs(math.sin(t * 8)) * talk), rot=(0, 0, 0.25 - 0.5 * talk), aL=aL, aR=(0.18, -0.1, -1) if not lost else (0.5, -0.3, 0.85), head=(-0.1 * talk - 0.25 * lost, 0, 0.5 * talk))
    else:                                          # per fare luce...
        fire = ramp(t, 38.9, 39.1) * (1 - ramp(t, 40.0, 40.2)) if t < 43.25 else 0.0; aim = ramp(t, 37.5, 37.9)
        S_.update(loc=(-10.3, -1.5, 0), rot=(-0.08 * fire, 0, PI / 2 - 0.25), aL=lerp((-0.2, -0.5, -0.85), (-0.05, -1, 0.06), aim), aR=(0.5, -0.1, -0.85), head=(-0.1, 0, -0.5 * (t > 44.2)), belly=1.0 + 0.06 * math.sin(t * 24) * (t > 43.4))
    return S_

def tp(t):
    S_ = dict(loc=(0, 0, 0), rot=(0, 0, 0), head=(0, 0, 0), tail=-1.0 + 0.5 * math.sin(t * 12))
    if t < 5.3: S_.update(loc=(-2.6, -2.5, 0), rot=(0, 0, 0.9), head=(-0.1, 0, 0.2))
    elif t < 7.6: S_.update(loc=(-7.0, -2.6, 0), rot=(0, 0, -0.5), head=(0.1, 0, -0.2), tail=-0.3)
    elif t < 12.2: S_.update(loc=(-3.6, -2.4, 0), rot=(0, 0, 0.4), head=(-0.5, 0, 0.3))
    elif t < 19.9: S_.update(loc=(-6.7, -3.6, 0), rot=(0, 0, 0.9), head=(-0.5, 0, 0))
    elif t < 33.35: S_.update(loc=(CX, 3.05, 1.55), rot=(0, 0, 0), head=(0.2 * ramp(t, 31.3, 31.4) * (1 - ramp(t, 31.5, 31.7)), 0, 0.35 * math.sin(t * 0.9)), tail=-0.6)
    elif t < 40.2: S_.update(loc=(-6.4, -2.4, 0), rot=(0, 0, -0.3), head=(0, 0, -0.5 * ramp(t, 36.9, 37.3)), tail=-0.3)
    elif t < 43.25: S_.update(loc=(-3.5, -2.3, 0), rot=(0, 0, 0.5), head=(-0.5, 0, 0.4))
    else: S_.update(loc=(-6.4, -2.4, 0), rot=(0, 0, -0.3), head=(0, 0, -0.4), tail=-0.3)
    return S_

def sp(t):
    """il Sole: loc, rollio, braccia."""
    Q = dict(loc=SUNP, roll=0.06 * math.sin(t * 2.2), aL=(-0.75, -0.2, -0.6), aR=(0.75, -0.2, -0.6), spin=t * 0.5)
    CUF = dict(aL=(0.8, -0.55, -0.35), aR=(-0.8, -0.55, -0.35))
    if t < 12.2:
        b = 0.12 * math.sin(t * 2.5); w = math.sin(t * 10)
        Q.update(loc=(SUNP[0], SUNP[1], SUNP[2] + b))
        if 7.6 <= t < 10.6: Q.update(aL=(-0.9, -0.1, 0.5 + 0.3 * w), aR=(0.9, -0.1, 0.5 - 0.3 * w), roll=0.15 * math.sin(t * 5))
    elif t < 14.95:
        sh = 0.05 * math.sin(t * 45) * ramp(t, 13.3, 13.9)
        Q.update(loc=(SUNP[0] + sh, SUNP[1], SUNP[2]), roll=0.0)
        if t >= 13.9: Q.update(**CUF)
        else: Q.update(aL=(-0.8, -0.2, 0.6 * ramp(t, 12.7, 13.0)), aR=(0.8, -0.2, 0.6 * ramp(t, 12.7, 13.0)))
    elif t < 19.9:
        Q.update(loc=(JX, 0.6, 1.75 - 0.08 * ramp(t, 17.0, 19.0)), roll=0.0, spin=0.0, aL=(0.45, -0.5, -0.75), aR=(-0.45, -0.5, -0.75))
        if t >= 16.15: Q.update(**CUF)
    else:
        jump = 0.25 * ramp(t, 31.3, 31.45) * (1 - ramp(t, 31.5, 32.0)); droop = 0.25 * ramp(t, 32.3, 33.0)
        Q.update(loc=(CAGE[0], CAGE[1], 1.9 + jump - droop), roll=0.08 * math.sin(t * 3) * (25.2 < t < 27.7), spin=0.0, **CUF)
    return Q
def cp(t):
    """l'agente sulla scala: u lungo la scala."""
    u = 0.86 * ramp(t, 13.2, 13.85); k = math.sin(t * 30) * (13.2 < t < 13.85)
    return dict(loc=(LA[0], LA[1] + LD[1] * u - 0.25, LA[2] + LD[2] * u - 0.55), rot=(0.55, 0, PI), arm=-2.3 + 0.4 * k, leg=0.5 * k)

GXP = (-10.3, -1.5)
# ======================= chiavi =======================
TR = Tb['root']
for f in range(1, NF + 1):
    t = (f - 1) / FPS
    for R_, s in ((P, pp(t)), (G, gp(t))):
        r = R_['root']; r.location = s['loc']; r.rotation_euler = s['rot']; r.keyframe_insert('location', frame=f); r.keyframe_insert('rotation_euler', frame=f)
        for nm, k in (('L', 'aL'), ('R', 'aR')):
            sh = R_['shoulder' + nm]; sh.rotation_quaternion = qdir(s[k]); sh.keyframe_insert('rotation_quaternion', frame=f)
        for nm, k in (('L', 'hL'), ('R', 'hR')):
            hp = R_['hip' + nm]; hp.rotation_euler = (s[k], 0, 0); hp.keyframe_insert('rotation_euler', frame=f)
        R_['head'].rotation_euler = s['head']; R_['head'].keyframe_insert('rotation_euler', frame=f)
    b = gp(t)['belly']; G['belly'].scale = (0.33 * b, 0.31 * b, 0.30 * b); G['belly'].keyframe_insert('scale', frame=f)
    q = tp(t); TR.location = q['loc']; TR.rotation_euler = q['rot']; TR.keyframe_insert('location', frame=f); TR.keyframe_insert('rotation_euler', frame=f)
    Tb['head'].rotation_euler = q['head']; Tb['head'].keyframe_insert('rotation_euler', frame=f)
    Tb['tail'].rotation_euler = (q['tail'], 0, 0.5 * math.sin(t * 14)); Tb['tail'].keyframe_insert('rotation_euler', frame=f)
    s = sp(t); r = S['root']; r.location = s['loc']; r.rotation_euler = (0, s['roll'], 0); r.keyframe_insert('location', frame=f); r.keyframe_insert('rotation_euler', frame=f)
    for nm, k in (('L', 'aL'), ('R', 'aR')):
        sh = S['shoulder' + nm]; sh.rotation_quaternion = qdir(s[k]); sh.keyframe_insert('rotation_quaternion', frame=f)
    S['rays'].rotation_euler = (0, s['spin'], 0); S['rays'].keyframe_insert('rotation_euler', frame=f)
    if 12.1 < t < 15.0:
        c = cp(t); r = C['root']; r.location = c['loc']; r.rotation_euler = c['rot']; r.keyframe_insert('location', frame=f); r.keyframe_insert('rotation_euler', frame=f)
        for nm, sg in (('L', 1), ('R', -1)):
            C['shoulder' + nm].rotation_euler = (c['arm'] * (1 if sg > 0 else 0.92), 0, 0); C['shoulder' + nm].keyframe_insert('rotation_euler', frame=f)
            C['hip' + nm].rotation_euler = (sg * c['leg'], 0, 0); C['hip' + nm].keyframe_insert('rotation_euler', frame=f)
        u = ramp(t, 12.2, 12.65); pcar.location = (LA[0], -15.0 + (LA[1] - 0.1 + 15.0) * (1 - (1 - u) ** 2), 0); pcar.keyframe_insert('location', frame=f)
        on = int(t * 7) % 2
        lred.scale = (0.42, 0.20, 0.13 if on else 0.02); lblue.scale = (0.42, 0.20, 0.02 if on else 0.13); lred.keyframe_insert('scale', frame=f); lblue.keyframe_insert('scale', frame=f)
    # luce: giorno / buio, fiamma, flash
    d = dark(t); sunl.energy = 0.10 if d else 3.9; bg.inputs['Strength'].default_value = 0.035 if d else 0.7; bgc.inputs['Strength'].default_value = 0.03 if d else 1.0
    sunl.keyframe_insert('energy', frame=f); bg.inputs['Strength'].keyframe_insert('default_value', frame=f); bgc.inputs['Strength'].keyframe_insert('default_value', frame=f)
    fk = 1 + 0.2 * math.sin(t * 31) + 0.12 * math.sin(t * 47)
    if t < 38.95: fs_, fe = 0.001, 0.0
    elif t < 40.2: fs_, fe = 0.6 * ramp(t, 38.95, 39.15) * fk, 2600.0 * ramp(t, 38.95, 39.1) * fk
    elif t < 43.25: fs_, fe = 0.001, 0.0
    else: fs_, fe = 0.15 * fk, 700.0 * fk
    flame.scale = (fs_, fs_, fs_ * 1.25); flame.keyframe_insert('scale', frame=f); fl_l.energy = fe; fl_l.keyframe_insert('energy', frame=f)
    flash_l.energy = 60000.0 if 15.52 <= t < 15.62 else 0.0; flash_l.keyframe_insert('energy', frame=f)

_last = {}
def _ex(key, fn, t, k):
    if key in _last and t - 0.06 > _last[key][1]: fn(fr(t - 0.06), **_last[key][0])
    fn(fr(t), **k); _last[key] = (k, t)
def pex(t, **k): _ex('p', lambda f, **kk: pippo.express(P, f, **kk), t, k)
def tex(t, **k): _ex('t', lambda f, **kk: tumbo.tumbo_express(Tb, f, **kk), t, k)
def gx(t, **k): _ex('g', lambda f, **kk: props009.gex(G, f, **kk), t, k)
def sx(t, **k): _ex('s', lambda f, **kk: props010.sex(S, f, **kk), t, k)
pex(0.0, brow=-0.8, brow_lift=0.8, eye_scale=1.3, mouth_open=1.0); pex(5.35, brow=1.0, eye_open=0.65, mouth_open=0.1, look=(-0.6, 0)); pex(7.65, brow=1.0, mouth_open=0.8, look=(0, 0.6))
pex(10.65, brow=1.0, mouth_open=0.6, eye_open=0.8); pex(12.25, brow=0.8, smile=0.6, look=(0.3, 0.6)); pex(13.9, smile=1.0, mouth_open=0.8, brow_lift=0.5)
pex(19.9, brow=1.0, eye_open=0.7, look=(-0.6, 0)); pex(27.75, brow=0.9, mouth_open=0.5, smile=0.3); pex(29.4, brow=-0.6, brow_lift=0.5, eye_open=0.5, mouth_open=0.4)
pex(31.3, smile=1.0, mouth_open=0.9, brow_lift=0.6, eye_scale=1.1); pex(33.4, smile=1.0, mouth_open=0.6, brow_lift=0.5); pex(33.95, brow=-0.6, brow_lift=0.7, eye_scale=1.35, mouth_open=0.3)
pex(37.0, brow=-0.4, brow_lift=0.6, eye_scale=1.3, mouth_open=0.2, look=(-0.7, 0)); pex(39.0, brow=-0.8, brow_lift=0.9, eye_scale=1.45, mouth_open=1.0); pex(40.25, brow=1.0, mouth_open=0.6, look=(0, 0.6))
pex(43.3, brow=0.0, brow_lift=0.2, eye_scale=1.35, eye_open=1.0, mouth_open=0.0, look=(0, 0)); pex(44.3, brow=1.0, eye_open=0.6, mouth_open=0.0)
tex(0.0, tongue=1.0); tex(5.35, brow=1.0, eye_open=0.6); tex(7.65, tongue=0.7, look=(0, 0.5)); tex(19.9, brow=0.8, eye_open=0.75); tex(31.3, brow=1.0, eye_scale=1.2); tex(33.4, tongue=0.6)
tex(33.95, eye_scale=1.4, brow=-0.6); tex(39.0, eye_scale=1.45, brow=-0.7); tex(40.25, tongue=0.4, look=(0, 0.5)); tex(43.3, eye_scale=1.3, brow=-0.3)
gx(0.0, brow=0.4, mouth=0.2); gx(5.35, brow=-0.3, mouth=1.0); gx(7.65, brow=0.4, mouth=0.2); gx(19.9, brow=0.9, mouth=0.1); gx(22.6, brow=1.0, mouth=0.25, look=(0.4, 0)); gx(24.95, brow=0.3, mouth=0.9)
gx(27.6, brow=0.8, mouth=0.15); gx(29.6, brow=-0.6, mouth=1.0, look=(0.7, 0)); gx(31.3, brow=-0.9, mouth=1.0, look=(0, 0.4)); gx(33.4, brow=0.6, mouth=0.1); gx(37.5, brow=1.0, mouth=0.5)
gx(38.95, brow=1.0, mouth=1.0); gx(43.3, brow=1.0, mouth=0.9); gx(44.3, brow=0.8, mouth=0.6)
sx(0.0, brow=0.6, mouth=0.5); sx(7.65, brow=0.7, mouth=0.8, tongue=1.0); sx(10.65, brow=0.5, mouth=0.4); sx(12.3, brow=-0.5, mouth=0.5, eye=1.2, look=(0, -0.8)); sx(13.9, brow=-0.9, mouth=1.0, eye=1.4, look=(0, -0.6))
sx(14.96, brow=0.9, mouth=0.05, eye=0.9); sx(15.55, brow=0.9, mouth=0.05, eye=0.6); sx(15.7, brow=0.9, mouth=0.05, eye=0.9); sx(16.38, brow=-0.8, mouth=0.6, eye=1.3); sx(17.1, brow=-0.9, mouth=0.1, eye=1.1, look=(0, -0.6))
sx(19.9, brow=-0.6, mouth=0.1, eye=1.0, look=(0.6, 0)); sx(25.6, brow=-0.3, mouth=0.2, eye=1.35, look=(0, 0.7)); sx(27.7, brow=-0.5, mouth=0.1, look=(0.7, 0)); sx(29.6, brow=-0.8, mouth=0.5, eye=1.2, look=(0.8, 0))
sx(31.3, brow=-1.0, mouth=1.0, eye=1.45); sx(32.4, brow=-1.0, mouth=0.3, eye=1.1, look=(0, -0.7))

# ======================= effetti =======================
def streak(name, sc, mat, t0, t1, fn, parent=None, mesh=None, rot=None):
    o = obj(name, mesh or shared_mesh('sphere_lo'), (0, 0, -80), sc, mat, prc, parent=parent)
    if rot: o.rotation_euler = rot
    o.hide_render = True; o.keyframe_insert('hide_render', frame=1); o.hide_render = False; o.keyframe_insert('hide_render', frame=fr(t0))
    if t1 < TOTAL: o.hide_render = True; o.keyframe_insert('hide_render', frame=fr(t1))
    for f in range(fr(t0), min(NF, fr(t1)) + 1):
        r_ = fn((f - 1) / FPS); o.location = r_[0]; o.keyframe_insert('location', frame=f)
        if len(r_) > 1: o.scale = r_[1]; o.keyframe_insert('scale', frame=f)
    return o
er = np.random.default_rng(3)
def burst(name, mat, t0, dur, c0, n, vmax, sc, grav=4.9, up=1.0, mesh=None):
    for k in range(n):
        v = np.array([er.uniform(-vmax, vmax), er.uniform(-vmax, vmax), er.uniform(0.3, 1.0) * vmax * up])
        streak(name, sc, mat, t0, t0 + dur, lambda t, v=v: ((c0[0] + v[0] * (t - t0), c0[1] + v[1] * (t - t0), max(0.03, c0[2] + v[2] * (t - t0) - grav * (t - t0) ** 2)),), mesh=mesh)
def steam(t0, t1, cfn, n=6, s=0.16, rise=1.3, mat=None, sp_=0.9):
    for k in range(n):
        ph = k / n; dx = er.uniform(-0.3, 0.3); dy = er.uniform(-0.2, 0.2)
        def fn(t, ph=ph, dx=dx, dy=dy):
            u = ((t - t0) * sp_ + ph) % 1.0; c0 = cfn(t); return ((c0[0] + dx + 0.15 * math.sin(u * 6 + ph * 9), c0[1] + dy, c0[2] + rise * u), (max(0.001, s * math.sin(PI * u)),) * 3)
        streak('Vapore', (s, s, s), mat or G9['steam'], t0, t1, fn)
steam(0.0, 5.3, lambda t: (BED[0] - 1.25, BED[1] + 0.45, 0.9), n=9, s=0.12, rise=1.5)
steam(5.3, 7.6, lambda t: (-8.1, -1.5, 2.0), n=4, s=0.12, rise=0.9); steam(7.6, 12.2, lambda t: (GARD[0], GARD[1], 2.0), n=4, s=0.12, rise=0.9)
steam(29.5, 30.8, lambda t: (CX + 1.0, -1.45, 1.2), n=7, s=0.15, rise=1.3, sp_=1.4)
steam(39.3, 40.2, lambda t: (-7.5, -1.5, 1.9), n=6, s=0.16, rise=1.2, mat=N['stink'], sp_=1.5); steam(43.25, TOTAL, lambda t: (-7.5, -1.5, 1.9), n=6, s=0.14, rise=1.2, mat=N['stink'])
for k in range(8):                                                                                  # raggi cattivi dal sole a Pippo
    ph = k / 8
    def fn(t, ph=ph):
        u = ((t * 1.3 + ph) % 1.0); a = (BED[0] - 1.2, BED[1], 1.1)
        return ((SUNP[0] + (a[0] - SUNP[0]) * u, SUNP[1] - 0.5 + (a[1] - SUNP[1] + 0.5) * u, SUNP[2] - 0.6 + (a[2] - SUNP[2] + 0.6) * u), (0.07, 0.07, 0.07))
    streak('RaggioCattivo', (0.07, 0.07, 0.07), H['ray'], 0.0, 5.3, fn)
burst('Scintilla', N['spark'], 13.9, 0.6, (SUNP[0], SUNP[1] - 0.7, SUNP[2] - 0.45), 8, 1.6, (0.06, 0.06, 0.06), grav=2.0)
burst('Polvere', M['dust'], 16.36, 0.6, (JX, -1.0, 0.1), 10, 2.2, (0.14, 0.14, 0.14), grav=1.0, up=0.3)
for bt in (31.37, 32.32): burst('Scintilla', N['spark'], bt, 0.45, (CX + 0.5, 2.3, 1.62), 7, 1.4, (0.05, 0.05, 0.05), grav=3.0)
for k in range(18):                                                                                 # pioggia personale
    ph = er.uniform(0, 1); dx = er.uniform(-0.85, 0.85); dy = er.uniform(-0.3, 0.3)
    streak('Goccia', (0.02, 0.02, 0.11), H['rain'], 40.2, 43.25, lambda t, ph=ph, dx=dx, dy=dy: ((GARD[0] + dx, GARD[1] + 0.2 + dy, 3.0 - 2.9 * ((t * 1.7 + ph) % 1.0)),))

# ======================= camera =======================
def Z0(t): return (0, 0, 0)
SHOTS = [  # t0, t1, sub cam, p0, p1, sub mira, a0, a1, lente, f
    (0.0, 2.75, Z0, (-2.6, -4.3, 2.3), (-2.9, -4.0, 2.2), Z0, (-4.7, -1.5, 1.0), (-4.7, -1.5, 1.0), 32, 6),
    (2.75, 5.3, Z0, (-5.0, -4.2, 1.6), (-5.0, -3.7, 1.6), Z0, (SUNP[0], SUNP[1], SUNP[2] - 0.1), (SUNP[0], SUNP[1], SUNP[2] - 0.1), 55, 8),
    (5.3, 7.6, Z0, (-9.2, -6.9, 1.3), (-9.2, -6.3, 1.3), Z0, (-9.2, -1.5, 1.25), (-9.2, -1.5, 1.25), 26, 6),
    (7.6, 10.6, Z0, (-5.7, -7.6, 0.8), (-5.6, -7.2, 0.8), Z0, (-5.0, -0.3, 3.2), (-5.0, -0.3, 3.2), 24, 11),
    (10.6, 12.2, Z0, (-4.3, -4.6, 1.6), (-4.4, -4.3, 1.6), Z0, (-4.95, -1.5, 1.6), (-4.95, -1.5, 1.6), 42, 6),
    (12.2, 14.2, Z0, (-10.8, -9.3, 1.3), (-10.5, -8.9, 1.3), Z0, (-5.3, -1.9, 3.1), (-5.3, -1.9, 3.3), 24, 11),
    (14.2, 14.95, Z0, (-5.0, -4.2, 2.6), (-5.0, -3.9, 2.6), Z0, (SUNP[0], SUNP[1], SUNP[2] - 0.25), (SUNP[0], SUNP[1], SUNP[2] - 0.25), 55, 8),
    (14.95, 16.15, Z0, (JX, -5.6, 1.6), (JX, -5.4, 1.6), Z0, (JX, 0.6, 1.5), (JX, 0.6, 1.5), 40, 8),
    (16.15, 19.9, Z0, (JX + 0.9, -8.0, 1.4), (JX + 0.5, -6.0, 1.5), Z0, (JX, 0.6, 1.7), (JX, 0.6, 1.7), 35, 8),
    (19.9, 22.5, Z0, (CX - 0.45, -9.0, 1.6), (CX - 0.45, -8.3, 1.6), Z0, (CX - 0.45, 1.5, 1.75), (CX - 0.45, 1.5, 1.75), 26, 11),
    (22.5, 24.6, Z0, (CX - 0.6, -4.3, 1.6), (CX - 0.7, -4.0, 1.6), Z0, (CX - 1.2, -0.6, 1.55), (CX - 1.2, -0.6, 1.55), 48, 6),
    (24.6, 27.7, Z0, (CX - 1.8, -7.0, 1.7), (CX - 1.9, -6.6, 1.7), Z0, (CX - 2.15, 0.0, 1.95), (CX - 2.15, 0.0, 1.95), 32, 8),
    (27.7, 30.8, Z0, (CX + 1.3, -5.6, 1.3), (CX + 1.2, -5.2, 1.3), Z0, (CX + 1.0, -1.2, 1.25), (CX + 1.0, -1.2, 1.25), 38, 6),
    (30.8, 32.1, Z0, (CX + 0.2, -0.45, 2.25), (CX + 0.2, -0.3, 2.25), Z0, (CX + 0.15, 3.0, 2.0), (CX + 0.15, 3.0, 2.0), 35, 8),
    (32.1, 33.35, Z0, (CX - 2.5, -5.0, 1.9), (CX - 2.6, -4.6, 1.9), Z0, (CAGE[0], CAGE[1], 1.8), (CAGE[0], CAGE[1], 1.75), 42, 8),
    (33.35, 36.9, Z0, (-6.6, -8.4, 1.5), (-6.8, -7.8, 1.5), Z0, (-7.2, -1.8, 1.15), (-7.2, -1.8, 1.15), 28, 8),
    (36.9, 40.2, Z0, (-8.9, -7.0, 1.3), (-8.9, -6.5, 1.3), Z0, (-8.9, -1.5, 1.3), (-8.9, -1.5, 1.3), 25, 8),
    (40.2, 43.25, Z0, (-4.0, -6.8, 1.1), (-4.1, -6.4, 1.1), Z0, (-4.95, -1.4, 2.25), (-4.95, -1.4, 2.25), 28, 8),
    (43.25, 45.9, Z0, (-8.9, -6.6, 1.3), (-8.9, -6.0, 1.3), Z0, (-8.9, -1.5, 1.3), (-8.9, -1.5, 1.3), 25, 8),
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
set_interp(camd, 'CONSTANT')
for idb in [sunl, fl_l, flash_l, w.node_tree] + [bpy.data.materials[n].node_tree for n in ('P_Skin', 'P_SkinD', 'P_Hoodie', 'P_HoodieD', 'P_Hair1', 'P_Hair2')]:
    try: set_interp(idb, 'CONSTANT')
    except Exception as e: print('interp', idb.name, e)
os.makedirs('../t010', exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath('../t010/pippo_t010.blend')); print('SAVED')
