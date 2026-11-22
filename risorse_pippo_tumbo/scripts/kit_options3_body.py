
# ======================= schede di scelta 3: altre cose del pacchetto (oggetti, cose enormi, posti nuovi, animali) =======================
import random
WHAT = [a for a in sys.argv if a in ('cose', 'enormi', 'posti', 'animali')] or ['cose', 'enormi', 'posti', 'animali']
ONLY = [a for a in sys.argv if len(a) in (2, 3) and a[0] in 'LMNO' and a[1:].isdigit()]
FORCE = 'force' in sys.argv
OUT = os.path.abspath('../t016/opt3'); os.makedirs(OUT, exist_ok=True)
P = pippo.build_pippo(chc); Tb = tumbo.build_tumbo(chc, scale=0.75)
for r in (P['root'], Tb['root']): r.rotation_mode = 'XYZ'
for nm in 'LR': P['shoulder' + nm].rotation_mode = 'QUATERNION'
def qdir(d, rest=(0, 0, -1)): return Vector(rest).rotation_difference(Vector(d).normalized())
def pose(loc, aL=(-0.14, 0, -1), aR=(0.5, -0.2, 0.8), yaw=0.0):
    P['root'].location = loc; P['root'].rotation_euler = (0, 0, yaw); P['shoulderL'].rotation_quaternion = qdir(aL); P['shoulderR'].rotation_quaternion = qdir(aR)
pose((1.0, 0.0, 0)); pippo.express(P, 1, smile=1.0, mouth_open=0.5)
Tb['root'].location = (0.1, -0.3, 0); tumbo.tumbo_express(Tb, 1, tongue=0.8)
camd = bpy.data.cameras.new('Cam'); cam = bpy.data.objects.new('Cam', camd); cac.objects.link(cam); scene.camera = cam
camd.clip_start = 0.05; camd.clip_end = 1500; camd.sensor_width = 36
tgt = empty('CamTarget', (0.5, 6.5, 2.0), None, cac)
ct = cam.constraints.new('TRACK_TO'); ct.target = tgt; ct.track_axis = 'TRACK_NEGATIVE_Z'; ct.up_axis = 'UP_Y'
kitlook.upgrade(scene, M, envc, prc)
A = kitlook.A
try: scene.render.use_motion_blur = False
except Exception: pass
EXPO = scene.view_settings.exposure
def shot(name, cl, tl, lens=26, w=540, h=960, samples=4):
    cam.location = cl; tgt.location = tl; camd.lens = lens
    scene.render.resolution_x = w; scene.render.resolution_y = h; scene.eevee.taa_render_samples = samples
    scene.render.filepath = os.path.join(OUT, name + '.png'); bpy.ops.render.render(write_still=True); print('TILE', name, flush=True)
def vis(objs, on):
    for o in objs:
        for q in [o] + list(o.children_recursive): q.hide_render = not on
def want(code):
    if ONLY and code not in ONLY: return False
    return FORCE or bool(ONLY) or not os.path.exists(os.path.join(OUT, code + '.png'))
def K(aid, x, y, z=0.0, h=None, w=None, s=None, rot=0.0, rx=0.0, coll=None, center=True):
    """modello del kit: h = altezza in metri, w = lato piu' lungo in pianta, s = scala fissa; (x, y) = centro della base."""
    r = A.modello('kenney/' + aid, collezione=coll or prc); r.rotation_mode = 'XYZ'; r.location = (0, 0, 0); r.scale = (1, 1, 1)
    r.rotation_euler = (math.radians(rx), 0, math.radians(rot)); bpy.context.view_layer.update()
    def bb():
        pts = [o.matrix_world @ Vector(c) for o in list(r.children_recursive) if o.type == 'MESH' for c in o.bound_box]
        return [min(p[i] for p in pts) for i in range(3)], [max(p[i] for p in pts) for i in range(3)]
    mn, mx = bb()
    if h: s = h / max(1e-6, mx[2] - mn[2])
    elif w: s = w / max(1e-6, max(mx[0] - mn[0], mx[1] - mn[1]))
    s = s or 1.0; r.scale = (s, s, s); bpy.context.view_layer.update(); mn, mx = bb()
    r.location = (x - (mn[0] + mx[0]) / 2, y - (mn[1] + mx[1]) / 2, z - mn[2]) if center else (x, y, z)
    bpy.context.view_layer.update(); return r, (mx[0] - mn[0], mx[1] - mn[1], mx[2] - mn[2])
def stack(aids, x, y, s, rot=0.0, coll=None):
    z = 0.0
    for a in aids:
        r, d = K(a, x, y, z=z, s=s, rot=rot, coll=coll); z += d[2]
    return z
def sunlamp(energy, rot=(52, 0, 28), color=(1, 1, 1)):
    l_ = bpy.data.lights.new('SunX', 'SUN'); o_ = bpy.data.objects.new('SunX', l_); prc.objects.link(o_)
    o_.rotation_euler = tuple(math.radians(a) for a in rot); l_.energy = energy; l_.color = color; l_.angle = math.radians(2.0); return o_
def point(loc, energy, color, r=0.3):
    l_ = bpy.data.lights.new('PtX', 'POINT'); o_ = bpy.data.objects.new('PtX', l_); prc.objects.link(o_); o_.location = loc; l_.energy = energy; l_.color = color; l_.shadow_soft_size = r; return o_
def ground(x0, aid, dim, tinta=(1, 1, 1), y0=-150, y1=150, z=0.0, half=150, ril=0.8):
    o = bx('Terra', (x0 - half, y0, z - 0.3), (x0 + half, y1, z), M['park'], envc); kitlook.setmat(o, A.materiale(aid, dimensione=dim, rilievo=ril, tinta=tinta)); A.niente_ombra(o); return o
def default_sky(): A.cielo('sunflowers_puresky', forza=1.1, rotazione=43.0, ris='4k'); scene.view_settings.exposure = EXPO

# ---------------------------------------------------------------- inquadratura quadrata per gli oggetti: Pippo e Tumbo a sinistra, la cosa a destra
PX, TX = -1.2, -2.1
def park(r, d, x_left=0.4, y_front=0.0):
    r.location.x += x_left + d[0] / 2; r.location.y += y_front + d[1] / 2; bpy.context.view_layer.update()
def frame(code, dx, dz, left=-2.7, x_left=0.4, ycen=0.2, lens=46, res=640):
    right = x_left + dx; cx = (left + right) / 2; Wn = (right - left) + 0.5; Hn = max(dz, 1.8) + 1.1
    dist = max(Wn, Hn) / (36.0 / lens); zc = max(dz, 1.8) * 0.5 + 0.05
    shot(code, (cx + 0.05 * dist, ycen - dist, zc + 0.07 * dist), (cx, ycen, zc), lens, w=res, h=res)
def stand(): pose((PX, 0.2, 0)); Tb['root'].location = (TX, -0.2, 0)

# ---------------------------------------------------------------- L: cose che possono comparire (o nascere)
if 'cose' in WHAT:
    stand()
    LS = [('L1', 'car-kit/ambulance', dict(h=2.7, rot=-35)), ('L2', 'car-kit/tractor', dict(h=2.6, rot=-35)), ('L3', 'car-kit/kart-oobi', dict(h=1.35, rot=-35)),
          ('L4', 'furniture-kit/bathtub', dict(h=0.85, rot=-25)), ('L5', 'furniture-kit/toilet', dict(h=1.05, rot=-25)), ('L6', 'furniture-kit/kitchenFridgeLarge', dict(h=2.2, rot=-20)),
          ('L7', 'food-kit/cake-birthday', dict(h=1.4)), ('L8', 'food-kit/donut-sprinkles', dict(w=1.9, rx=72, rot=-15)), ('L9', 'food-kit/turkey', dict(h=1.2, rot=-30))]
    for code, aid, kw in LS:
        if not want(code): continue
        k, d = K(aid, 0, 0, **kw); park(k, d); print(code, aid, [round(v, 2) for v in d])
        frame(code, d[0], d[2]); vis([k], False)

# ---------------------------------------------------------------- O: animali fatti a mano nello stile di Tumbo (animali.py), non i modelli a cubo
if 'animali' in WHAT:
    stand(); import animali
    OS = [('O1', 'mucca'), ('O2', 'elefante'), ('O3', 'pinguino'), ('O4', 'giraffa'), ('O5', 'maiale'), ('O6', 'leone'), ('O7', 'scimmia'), ('O8', 'pulcino'), ('O9', 'granchio')]
    for code, nm in OS:
        if not want(code): continue
        an = animali.crea(nm, prc); r = an['root']; r.rotation_euler = (0, 0, math.radians(-28)); bpy.context.view_layer.update()
        pts = [o.matrix_world @ Vector(c) for o in r.children_recursive if o.type == 'MESH' for c in o.bound_box]
        mn = [min(q[i] for q in pts) for i in range(3)]; mx = [max(q[i] for q in pts) for i in range(3)]; d = (mx[0] - mn[0], mx[1] - mn[1], mx[2] - mn[2])
        r.location = (0.4 - mn[0], -0.1 - mn[1], -mn[2]); bpy.context.view_layer.update(); print(code, nm, [round(v, 2) for v in d])
        frame(code, d[0], d[2]); vis([r], False)

# ---------------------------------------------------------------- M: cose enormi in giardino
if 'enormi' in WHAT:
    stand()
    giardino = [o for o in bpy.data.objects if o.parent is None and o.name.startswith('PT_') and -0.6 < o.location.x < 18 and -3 < o.location.y < 9.3]
    vis(giardino, False)
    MS = [('M1', 'pirate-kit/ship-pirate-large', dict(h=7.0, rot=70)), ('M2', 'watercraft-kit/ship-ocean-liner', dict(w=11.0, rot=70)), ('M3', 'train-kit/train-locomotive-a', dict(h=3.4, rot=60)),
          ('M4', 'ROCKET', {}), ('M5', 'space-kit/meteor_detailed', dict(h=3.4)), ('M6', 'castle-kit/siege-catapult', dict(h=3.2, rot=-40)),
          ('M7', 'pirate-kit/cannon', dict(h=1.7, rot=-50)), ('M8', 'graveyard-kit/coffin', dict(w=2.4, rot=-30)), ('M9', 'holiday-kit/snowman-hat', dict(h=3.2, rot=-15))]
    for code, aid, kw in MS:
        if not want(code): continue
        if aid == 'ROCKET':
            n0 = set(bpy.data.objects); top = stack(['space-kit/rocket_baseA', 'space-kit/rocket_fuelA', 'space-kit/rocket_topA'], 2.4, 1.8, 2.6); f_, fd = K('space-kit/rocket_finsA', 2.4, 1.8, s=2.6)
            ks = [o for o in bpy.data.objects if o not in n0 and o.parent is None]; d = (max(fd[0], 3.0), 3.0, top); print(code, 'rocket', [round(v, 2) for v in d])
        else:
            k, d = K(aid, 0, 0, **kw); park(k, d, y_front=0.6); ks = [k]; print(code, aid, [round(v, 2) for v in d])
        frame(code, d[0], d[2]); vis(ks, False)
    vis(giardino, True)

# ---------------------------------------------------------------- N: posti nuovi (ognuno costruito lontano dal quartiere)
if 'posti' in WHAT:
    def here(x0, dx=0.7): pose((x0 + dx, 0.0, 0)); Tb['root'].location = (x0 + dx - 1.2, -0.3, 0)
    def albero(aid, x, y, h, vista=0, near=False):
        o = A.albero_cartonato(aid, posizione=(x, y, 0), altezza=h, collezione=envc, vista=vista, ombra=near)
        if (vista + int(x * 7)) % 2: o.scale.x = -1
        return o
    MIX = [k[0] for k in kitlook.TREE_MIX]
    import paesaggi as PS
    def Mdl(x0, h, aid, x, y, alt, rot=0.0, tri=None, z=None, coll=None):
        return A.modello(aid, posizione=(x0 + x, y, h(x, y) if z is None else z), altezza=alt, rotazione=rot, max_triangoli=tri, collezione=coll or envc)
    def sparsi(x0, h, aid, n, area, alt, seed, shadow=False, keep=None, via=((0.7, 0.0, 1.6),)):
        """ciuffi, cespugli e sassi sparsi sul terreno, lontani dai punti 'via' (x, y, raggio)."""
        out = kitlook.variants(aid, n, (x0 + area[0], x0 + area[1], area[2], area[3]), alt, seed=seed, coll=envc, shadow=shadow, keep=keep); rr = random.Random(seed + 99)
        for o in out:
            for _ in range(8):
                if all(math.hypot(o.location.x - x0 - vx, o.location.y - vy) > vr for vx, vy, vr in via): break
                o.location.x = x0 + rr.uniform(area[0], area[1]); o.location.y = rr.uniform(area[2], area[3])
        return PS.posa(out, x0, h)
    def sparsi2(x0, h, aid, n, area, alt, seed, tri=None):
        return PS.posa(A.sparpaglia(aid, n, (x0 + area[0], x0 + area[1], area[2], area[3]), altezza=alt, seme=seed, max_triangoli=tri, collezione=envc), x0, h)
    def alb(x0, h, aid, x, y, alt, vista=0, near=False):
        o = albero(aid, x0 + x, y, alt, vista=vista, near=near); o.location.z = h(x, y) - 0.2; return o
    def cam_n(code, x0, cl=(1.2, -7.5, 2.5), tl=(0.0, 3.0, 1.5), lens=21): shot(code, (x0 + cl[0], cl[1], cl[2]), (x0 + tl[0], tl[1], tl[2]), lens)

    if want('N1'):                                                          # cimitero al crepuscolo
        x0 = 2000.0; rnd = random.Random(1); here(x0); ground(x0, 'Grass001', 3.0, (0.55, 0.85, 0.6)); g = 'graveyard-kit/'
        A.cielo('qwantani_dusk_2_puresky', forza=0.45, rotazione=200.0, ris='1k')
        tipi = ['gravestone-cross', 'gravestone-round', 'gravestone-bevel', 'gravestone-broken', 'gravestone-decorative', 'gravestone-wide', 'gravestone-roof', 'cross-wood', 'cross-column', 'gravestone-cross-large']
        i = 0
        for yy in (3.2, 5.8, 8.4):
            for xx in (-7.2, -4.8, -2.4, 0.0, 2.4, 4.8, 7.2):
                if yy > 7 and xx > 3: continue
                K(g + tipi[i % len(tipi)], x0 + xx + rnd.uniform(-0.3, 0.3), yy + rnd.uniform(-0.3, 0.3), s=2.0, rot=rnd.uniform(-10, 10), coll=envc); i += 1
        K(g + 'crypt-large', x0 + 5.8, 9.6, s=2.6, coll=envc); K(g + 'crypt-large-roof', x0 + 5.8, 9.6, z=0, s=2.6, coll=envc)
        for k in range(13): K(g + 'iron-fence', x0 - 12 + k * 2.0, 11.6, s=2.0, coll=envc)
        for k, (xx, yy, hh) in enumerate(((-9, 13.5, 9.0), (-5, 14.5, 10.5), (0, 14, 9.5), (4.5, 15, 10.0), (9.5, 13.5, 9.0), (-10.5, 6, 8.5), (10.5, 5, 9.0), (13, 10, 9.5), (-13, 12, 10.0), (2, 18, 12.0), (-3, 19, 12.0), (7, 19, 11.5))):
            albero(('fir_tree_01', 'pine_tree_01')[k % 2], x0 + xx, yy, hh, vista=k)
        kitlook.tune_cutouts(1.9)
        K(g + 'lightpost-single', x0 - 3.6, 1.6, s=2.0, coll=envc); K(g + 'lightpost-single', x0 + 3.9, 4.4, s=2.0, coll=envc)
        K(g + 'pumpkin-carved', x0 + 2.4, 0.4, s=2.0, rot=-20); K(g + 'pumpkin-tall-carved', x0 - 2.2, 1.0, s=2.0, rot=20)
        K(g + 'coffin', x0 + 2.9, 1.9, s=2.0, rot=25); K(g + 'shovel-dirt', x0 - 1.4, 2.2, s=2.0)
        K(g + 'character-ghost', x0 - 2.7, 3.6, z=0.5, h=1.7, rot=15)
        pl = [point((x0 - 3.6, 1.4, 2.3), 260, (1.0, 0.7, 0.3)), point((x0 + 3.9, 4.2, 2.3), 260, (1.0, 0.7, 0.3))]
        cam_n('N1', x0); [bpy.data.objects.remove(o) for o in pl]; default_sky()

    if want('N2'):                                                          # spazio
        x0 = 2400.0; rnd = random.Random(2); here(x0); ground(x0, 'moon_01', 7.0, (1, 1, 1), ril=1.2); s_ = 'space-kit/'
        A.cielo('qwantani_night_puresky', forza=0.12, rotazione=0.0, ris='1k'); sl = sunlamp(3.6, (58, 0, 35), (0.92, 0.95, 1.0))
        for (xx, yy, ss) in ((-3.5, 1.2, 3.0), (4.6, 3.6, 4.0), (-6.5, 6.5, 3.5), (1.5, 5.2, 2.6), (8, 8, 4)): K(s_ + ('craterLarge' if ss > 3 else 'crater'), x0 + xx, yy, s=ss, coll=envc)
        K(s_ + 'rock_crystalsLargeA', x0 - 4.8, 4.6, s=3.0, coll=envc); K(s_ + 'rock_crystalsLargeB', x0 + 5.6, 6.4, s=3.0, coll=envc); K(s_ + 'rock_crystals', x0 + 3.2, 0.6, s=2.2, coll=envc)
        K(s_ + 'rock_largeA', x0 - 7.5, 9.5, s=4.0, coll=envc); K(s_ + 'rock_largeB', x0 + 8.5, 3.5, s=3.5, coll=envc); K(s_ + 'meteor_detailed', x0 + 2.6, 2.8, h=1.3, coll=envc)
        K(s_ + 'hangar_roundGlass', x0 - 3.6, 10.5, s=4.0, coll=envc); K(s_ + 'hangar_largeA', x0 + 5.5, 12.0, s=4.0, coll=envc)
        stack([s_ + 'rocket_baseA', s_ + 'rocket_fuelA', s_ + 'rocket_topA'], x0 + 1.2, 8.6, 2.6); K(s_ + 'rocket_finsA', x0 + 1.2, 8.6, s=2.6)
        K(s_ + 'rover', x0 - 2.6, 2.4, h=1.2, rot=30); K(s_ + 'satelliteDish_large', x0 + 8.0, 9.5, s=3.0, coll=envc)
        K(s_ + 'alien', x0 + 2.3, 0.9, h=1.3, rot=-25); K(s_ + 'astronautA', x0 - 3.6, 3.6, h=1.7, rot=20); K(s_ + 'craft_speederA', x0 - 2.0, 6.0, z=4.6, h=1.3, rot=-60)
        cam_n('N2', x0); bpy.data.objects.remove(sl); default_sky()

    if want('N3'):                                                          # isola dei pirati: spiaggia, colli, mare, galeone vero
        x0 = 2800.0; rnd = random.Random(3); here(x0); h = PS.isola()
        PS.terreno(envc, x0, A.materiale('sand_01', dimensione=4.0, rilievo=1.0, tinta=(1.15, 1.08, 0.9)), h, xr=(-90, 90), yr=(-25, 130), passo=1.0); PS.mare(envc, x0)
        Mdl(x0, h, 'treasure_chest', 2.5, 0.8, 0.8, rot=-25, tri=20000, coll=prc); Mdl(x0, h, 'cannon_01', -3.0, 1.6, 1.05, rot=205, tri=15000, coll=prc)
        Mdl(x0, h, 'wooden_barrels_01', 4.0, 2.9, 1.15, rot=20, tri=12000); Mdl(x0, h, 'Barrel_01', 4.9, 1.9, 0.95); Mdl(x0, h, 'wooden_crate_01', 3.3, 4.0, 0.6, rot=15); Mdl(x0, h, 'wooden_crate_01', -4.6, 3.4, 0.6, rot=-30)
        for sgn in (-1, 1): shape('Xtesoro', 'cyl:0.07:1.5', (x0 + 1.0, 2.7, h(1.0, 2.7) + 0.04), rot=(PI / 2, 0, sgn * PI / 4), mat=material('S_xrossa', (0.85, 0.05, 0.04), rough=0.6), coll=prc)
        K('pirate-kit/flag-pirate-high', x0 + 3.2, 5.6, z=h(3.2, 5.6), h=5.2)
        Mdl(x0, h, 'coast_rocks_01', -9.5, 6.5, 3.4, rot=40, tri=14000); Mdl(x0, h, 'coast_rocks_02', 10.5, 5.0, 3.0, rot=200, tri=14000); Mdl(x0, h, 'coast_land_rocks_02', 6.8, 9.0, 1.7, tri=12000); Mdl(x0, h, 'coast_rocks_01', -16, -2.0, 2.6, rot=140, tri=14000)
        sparsi2(x0, h, 'sand_rocks_small_01', 6, (-8, 8, -3, 9), (0.25, 0.5), 31, tri=5000)
        sparsi(x0, h, 'grass_medium_01', 34, (-12, 12, -4, 12), (0.3, 0.55), 32); sparsi2(x0, h, 'wild_rooibos_bush', 9, (-13, 13, 3, 14), (0.6, 1.0), 33); sparsi(x0, h, 'shrub_02', 12, (-18, 18, 7, 20), (0.9, 1.6), 34, shadow=True)
        for k, (xx, yy, hh, nm) in enumerate(((-5.2, 5.0, 6.6, 'island_tree_02'), (5.8, 6.4, 7.2, 'island_tree_01'), (-9.0, 10.5, 6.5, 'island_tree_03'), (8.2, 3.0, 4.6, 'quiver_tree_01'), (-13, 15, 8.0, 'island_tree_01'), (-17, 14, 7.0, 'island_tree_02'), (-11, 19, 7.5, 'island_tree_03'), (15, 13, 7.5, 'island_tree_01'), (19, 12, 6.5, 'island_tree_02'), (13, 17, 7.0, 'island_tree_03'), (-2.5, 12.5, 6.0, 'island_tree_01'), (2.0, 16, 6.5, 'island_tree_02'), (-20, 9, 6.0, 'quiver_tree_01'), (22, 7, 6.0, 'island_tree_01'))):
            alb(x0, h, nm, xx, yy, hh, vista=k, near=k < 3)
        kitlook.tune_cutouts(1.9)
        Mdl(x0, h, 'dutch_ship_large_01', 4.0, 40.0, 19.0, rot=100, tri=40000, z=-1.2); Mdl(x0, h, 'dutch_ship_medium', -34.0, 78.0, 15.0, rot=60, tri=25000, z=-1.0)
        sparsi(x0, h, 'grass_medium_01', 3, (-3.2, -1.6, -5.2, -4.4), (0.5, 0.7), 35, via=())      # primo piano: ciuffi vicino alla camera
        cam_n('N3', x0, cl=(1.2, -7.5, 2.4), tl=(0.0, 3.0, 1.7))

    if want('N4'):                                                          # castello
        x0 = 3200.0; rnd = random.Random(4); here(x0); ground(x0, 'Grass001', 3.0, (1.05, 1.35, 0.7)); c_ = 'castle-kit/'; s = 3.6
        for dx in (-2, -1, 1, 2): K(c_ + 'wall', x0 + dx * s, 9.0, s=s, coll=envc)
        K(c_ + 'wall-doorway', x0, 9.0, s=s, coll=envc); K(c_ + 'gate', x0, 9.0, s=s, coll=envc)
        for dx in (-3, 3): stack([c_ + 'tower-square-base', c_ + 'tower-square-mid', c_ + 'tower-square-top-roof-high'], x0 + dx * s, 9.0, s, coll=envc)
        stack([c_ + 'tower-square-base', c_ + 'tower-square-mid-windows', c_ + 'tower-square-mid', c_ + 'tower-square-top-roof-high-windows'], x0, 15.0, 4.6, coll=envc)
        K(c_ + 'siege-catapult', x0 - 3.4, 3.0, h=2.4, rot=160); K(c_ + 'siege-ballista', x0 + 3.6, 2.4, h=1.6, rot=200); K(c_ + 'siege-tower', x0 + 7.0, 5.0, h=6.5, rot=180, coll=envc)
        K(c_ + 'flag-banner-long', x0 - 1.0 * s, 8.6, z=2.6, s=s * 0.8, coll=envc); K(c_ + 'flag-banner-long', x0 + 1.0 * s, 8.6, z=2.6, s=s * 0.8, coll=envc)
        for k, (xx, yy, hh) in enumerate(((-8.5, 4.5, 7.2), (-6.5, 1.0, 5.2), (9.8, 1.5, 5.6), (-11, 8, 7.6), (12, 8.5, 7.6))): albero(MIX[k % len(MIX)], x0 + xx, yy, hh, vista=k, near=k < 3)
        K(c_ + 'rocks-large', x0 + 5.6, 0.8, h=1.2, coll=envc); K(c_ + 'rocks-small', x0 - 1.8, 1.8, h=0.5, coll=envc)
        cam_n('N4', x0, tl=(0.0, 4.0, 3.0))

    if want('N5'):                                                          # neve e Natale
        x0 = 3600.0; rnd = random.Random(5); here(x0); ground(x0, 'snow_02', 5.0, (2.6, 2.6, 2.75)); h_ = 'holiday-kit/'
        A.cielo('snowy_field', forza=1.2, rotazione=84.0, ris='1k')
        albero('fir_tree_01', x0 + 3.6, 4.8, 6.4, vista=0, near=True)                    # albero di Natale: abete vero con palline e stella
        pal = [material('S_pal%d' % i, c, rough=0.25, emit=c, emit_strength=1.6) for i, c in enumerate(((1.0, 0.1, 0.1), (1.0, 0.75, 0.1), (0.15, 0.4, 1.0), (1.0, 1.0, 1.0)))]
        for i in range(18):
            zz = rnd.uniform(1.3, 5.3); hw = 1.25 * (1 - zz / 6.4) + 0.1; ball_('Pallina', 0.11, (x0 + 3.6 + rnd.uniform(-hw, hw), 4.55, zz), pal[i % 4], prc)
        ball_('Stella', 0.2, (x0 + 3.6, 4.55, 6.35), pal[1], prc, sc=(1, 0.5, 1))
        for k in range(16):
            xx = rnd.uniform(-14, 14); yy = rnd.uniform(8.5, 17); albero(('fir_tree_01', 'pine_tree_01', 'fir_tree_01')[k % 3], x0 + xx, yy, rnd.uniform(7, 12), vista=k)
        albero('fir_tree_01', x0 - 7.5, 4.5, 8.0, vista=1, near=True); albero('pine_tree_01', x0 + 8.5, 2.5, 7.5, vista=2, near=True)
        kitlook.tune_cutouts(1.9)
        K(h_ + 'snowman-hat', x0 - 2.7, 2.2, h=2.0, rot=20); K(h_ + 'snowman', x0 - 4.9, 4.6, h=1.7, rot=30)
        for (xx, yy, hh, nm) in ((2.2, 3.6, 0.8, 'present-a-cube'), (3.2, 3.2, 0.6, 'present-b-round'), (4.4, 3.5, 0.7, 'present-a-rectangle'), (5.0, 4.2, 0.9, 'present-b-cube'), (2.8, 4.1, 0.5, 'present-a-round')): K(h_ + nm, x0 + xx, yy, h=hh, rot=rnd.uniform(0, 90))
        K(h_ + 'reindeer', x0 + 2.5, 1.2, h=1.8, rot=-40); K(h_ + 'sled-long', x0 + 4.6, 1.5, h=0.6, rot=-30)
        K(h_ + 'candy-cane-red', x0 - 1.2, 3.6, h=1.7); K(h_ + 'candy-cane-green', x0 + 0.9, 4.2, h=1.7); K(h_ + 'nutcracker', x0 - 6.2, 2.2, h=1.8, rot=25)
        K(h_ + 'train-locomotive', x0 - 1.9, -1.5, h=0.6, rot=75); K(h_ + 'train-wagon', x0 - 2.9, -1.25, h=0.5, rot=75)
        K(h_ + 'gingerbread-man', x0 + 1.9, -0.6, h=1.0, rot=-15); K(h_ + 'lantern', x0 - 1.0, 1.2, h=0.6)
        cam_n('N5', x0); default_sky()

    if want('N6'):                                                          # campeggio nel bosco: colline, abeti e pini veri, sottobosco, fuoco
        x0 = 4000.0; rnd = random.Random(6); here(x0); h = PS.colline(amp=6.0, rx=10.5, ry=9.5, cy=3.0, bordo=18.0, lontano=10.0, fase=13.0)
        PS.terreno(envc, x0, A.materiale('Grass001', dimensione=3.0, rilievo=0.8, tinta=(0.9, 1.2, 0.62), ruvidita=1.5), h)
        me = bpy.data.meshes.new('Radura'); n_ = 40                                                 # radura di terra attorno al fuoco
        me.from_pydata([(x0 + 0.4, 2.6, 0.02)] + [(x0 + 0.4 + 3.6 * math.cos(i / n_ * 2 * PI) * (1 + 0.12 * math.sin(i * 1.7)), 2.6 + 3.0 * math.sin(i / n_ * 2 * PI) * (1 + 0.12 * math.cos(i * 2.3)), 0.02) for i in range(n_)], [], [(0, i + 1, (i + 1) % n_ + 1) for i in range(n_)]); me.update()
        ro = bpy.data.objects.new('Radura', me); envc.objects.link(ro); me.materials.append(A.materiale('forrest_ground_01', dimensione=3.0, rilievo=1.0)); ro.visible_shadow = False
        PS.bosco(A, envc, x0, h, ('fir_tree_01', 'pine_tree_01', 'fir_tree_01'), 90, r0=11.5, r1=55.0, alt=(10.0, 16.0), seme=61, ombra_vicini=6)
        PS.bosco(A, envc, x0, h, ('fir_sapling_medium', 'pine_sapling_medium', 'fir_sapling'), 22, r0=9.5, r1=22.0, alt=(1.6, 3.4), seme=62)
        alb(x0, h, 'fir_tree_01', -8.2, 3.5, 12.5, vista=1, near=True); alb(x0, h, 'pine_tree_01', 8.6, 4.6, 13.0, vista=2, near=True)
        kitlook.tune_cutouts(1.9)
        sparsi(x0, h, 'fern_02', 22, (-10, 10, -4, 11), (0.45, 0.8), 63, via=((0.7, 0.0, 1.6), (0.4, 2.6, 3.4))); sparsi(x0, h, 'grass_medium_01', 46, (-11, 11, -5, 12), (0.22, 0.42), 64, via=((0.7, 0.0, 1.2), (0.4, 2.6, 3.0)))
        sparsi(x0, h, 'dandelion_01', 18, (-9, 9, -4, 10), (0.12, 0.2), 65, via=((0.4, 2.6, 3.0),)); sparsi(x0, h, 'shrub_02', 12, (-14, 14, 6, 16), (0.9, 1.6), 66, shadow=True, via=((0.4, 2.6, 5.5),))
        sparsi2(x0, h, 'boulder_01', 4, (-9, 9, 6, 11), (0.6, 1.3), 67); Mdl(x0, h, 'rock_moss_set_01', -7.6, 7.2, 1.9, rot=30, tri=14000)
        Mdl(x0, h, 'stone_fire_pit', 0.4, 2.6, 0.45, coll=prc); fu, pf = PS.fuoco(prc, (x0 + 0.4, 2.6, 0.12), 1.0, 900)
        Mdl(x0, h, 'dead_tree_trunk', -1.9, 2.3, 0.5, rot=75, tri=12000, coll=prc); Mdl(x0, h, 'tree_stump_01', 2.6, 1.7, 0.6, tri=10000, coll=prc); Mdl(x0, h, 'wooden_axe', 2.95, 1.45, 0.75, rot=40, coll=prc)
        Mdl(x0, h, 'folding_wooden_stool', 2.0, 3.5, 0.5, rot=200, coll=prc); Mdl(x0, h, 'Lantern_01', 2.6, 1.7, 0.36, tri=8000, z=0.6, coll=prc); pl = point((x0 + 2.6, 1.6, 0.85), 60, (1.0, 0.75, 0.4), 0.1)
        Mdl(x0, h, 'old_military_crate', 3.6, 4.6, 0.42, rot=20, tri=8000, coll=prc)
        PS.tenda(envc, (x0 - 4.3, 5.4, h(-4.3, 5.4)), rot=math.radians(28), colore=(0.95, 0.42, 0.06), nome='TendaA'); PS.tenda(envc, (x0 + 4.9, 6.2, h(4.9, 6.2)), rot=math.radians(-32), colore=(0.1, 0.5, 0.75), nome='TendaB')
        sparsi(x0, h, 'fern_02', 3, (-3.4, -1.8, -5.3, -4.5), (0.7, 0.9), 68, via=())
        cam_n('N6', x0, cl=(1.2, -7.5, 2.4), tl=(0.0, 3.0, 1.8)); [bpy.data.objects.remove(o) for o in (pf, pl)]

    if want('N7'):                                                          # centro citta': palazzi fitti, marciapiedi arredati, auto grandi
        x0 = 4400.0; rnd = random.Random(7); here(x0); g_ = bpy.data.materials.get
        asf = A.materiale('asphalt_02', dimensione=4.0, rilievo=0.8, tinta=(0.8, 0.8, 0.85)); lastre = A.materiale('PavingStones070', dimensione=2.0, rilievo=0.8); cem = A.materiale('Concrete034', dimensione=3.0, rilievo=0.6)
        o = bx('StradaC', (x0 - 150, -150, -0.3), (x0 + 150, 190, 0.0), M['park'], envc); kitlook.setmat(o, asf); A.niente_ombra(o)
        for sx in (-1, 1):
            o = bx('MarciapC', (x0 + sx * 9.0 - 2.5, -40, 0.0), (x0 + sx * 9.0 + 2.5, 150, 0.16), M['park'], envc); kitlook.setmat(o, lastre)
            o = bx('CordoloC', (x0 + sx * 6.5 - 0.12, -40, 0.0), (x0 + sx * 6.5 + 0.12, 150, 0.18), M['park'], envc); kitlook.setmat(o, cem)
        for yy in range(-20, 120, 4):
            if not (-3.5 < yy < 3.5): bx('LineaC', (x0 - 0.08, yy, 0.0), (x0 + 0.08, yy + 2.0, 0.012), M['frame'], envc)
        PS.strisce(envc, x0, -1.4, mezza=6.3, lunghe=3.4); bx('StopC', (x0 + 0.3, 3.0, 0.0), (x0 + 6.2, 3.35, 0.012), M['frame'], envc)
        torri = [g_('PT_tower%d' % i) or M['tower'][i] for i in range(len(M['tower']))]
        def torre(x, y, rz, tw, hh):
            mb = MB([torri[int(rng.integers(0, len(torri)))], M['window'], M['frame'], cem, M['dark'], M['shutter'][int(rng.integers(0, 5))]]); set004.tower_geo(mb, tw, hh, rng); return mb.build('PalazzoC', envc, (x, y, 0), rz)
        tende = [material('S_tendaC%d' % i, c, rough=0.8) for i, c in enumerate(((0.85, 0.1, 0.08), (0.1, 0.5, 0.25), (0.1, 0.35, 0.8), (0.95, 0.7, 0.1)))]
        for sx in (-1, 1):
            yy = -12.0; k = 0
            while yy < 96:
                tw = rnd.uniform(5.0, 6.6); hh = rnd.uniform(13, 30) if yy < 60 else rnd.uniform(24, 44)
                torre(x0 + sx * (11.5 + tw / 2), yy + tw / 2, PI / 2 if sx < 0 else -PI / 2, tw, hh)
                if k % 2 == 0 and yy < 50: bx('TendaNegozio', (x0 + sx * 11.5 - (1.6 if sx > 0 else 0), yy + tw / 2 - 1.6, 2.9), (x0 + sx * 11.5 + (0 if sx > 0 else 1.6), yy + tw / 2 + 1.6, 3.02), tende[k // 2 % 4], envc)
                yy += tw + rnd.uniform(0.0, 0.5); k += 1
        for k in range(7): torre(x0 - 30 + k * 10.0 + rnd.uniform(-1, 1), 108 + rnd.uniform(0, 8), 0.0, rnd.uniform(7, 9), rnd.uniform(34, 58))
        for yy in (2, 15, 28, 41, 54):
            for sx in (-1, 1):
                A.modello('street_lamp_01', posizione=(x0 + sx * 7.2, yy + (3 if sx > 0 else 0), 0.16), altezza=5.4, rotazione=90 if sx < 0 else -90, collezione=envc)
                o = albero(MIX[(yy + sx) % len(MIX)], x0 + sx * 9.6, yy + 6.5, rnd.uniform(5.0, 6.5), vista=yy, near=yy < 20); o.location.z = 0.16
        kitlook.tune_cutouts(1.9)
        A.modello('fire_hydrant', posizione=(x0 + 7.1, 6.6, 0.16), altezza=0.95, max_triangoli=8000, collezione=prc); A.modello('metal_trash_can', posizione=(x0 - 7.2, 4.2, 0.16), altezza=1.05, collezione=prc)
        A.modello('painted_wooden_bench', posizione=(x0 - 10.2, 8.5, 0.16), altezza=1.0, rotazione=90, collezione=prc); A.modello('painted_wooden_bench', posizione=(x0 + 10.2, 12.5, 0.16), altezza=1.0, rotazione=-90, collezione=prc)
        A.modello('concrete_road_barrier', posizione=(x0 + 4.6, -0.6, 0), altezza=0.95, rotazione=15, collezione=prc); A.modello('concrete_road_barrier', posizione=(x0 + 5.4, 1.6, 0), altezza=0.95, rotazione=80, collezione=prc)
        K('car-kit/cone', x0 + 3.4, 0.2, h=0.75); K('car-kit/cone', x0 + 3.9, 2.2, h=0.75); K('car-kit/cone', x0 + 4.4, -1.6, h=0.75)
        PS.semaforo(prc, (x0 + 6.9, 4.4, 0.16), rot=0.0, acceso='rosso'); PS.semaforo(prc, (x0 - 6.9, -2.0, 0.16), rot=PI, acceso='verde')
        # auto piu' grandi (l'autore: "le macchine dovrebbero essere piu' grandi")
        K('car-kit/taxi', x0 - 2.6, 9.5, h=2.2, rot=0); K('car-kit/police', x0 + 2.7, 14.5, h=2.2, rot=180); K('car-kit/van', x0 - 2.7, 21.0, h=3.0, rot=0); K('car-kit/garbage-truck', x0 + 2.8, 27.0, h=3.6, rot=180)
        K('car-kit/suv', x0 - 2.6, 34.0, h=2.5, rot=0); K('car-kit/sedan-sports', x0 + 2.7, 40.0, h=2.1, rot=180); K('car-kit/truck', x0 - 2.7, 48.0, h=3.3, rot=0)
        K('car-kit/hatchback-sports', x0 - 5.4, 14.0, h=2.1, rot=0); K('car-kit/sedan', x0 + 5.4, 20.0, h=2.2, rot=180); K('car-kit/delivery', x0 + 5.4, 33.0, h=3.0, rot=180); K('car-kit/suv-luxury', x0 - 5.4, 27.0, h=2.5, rot=0)
        cam_n('N7', x0, cl=(0.9, -7.5, 2.3), tl=(0.0, 6.0, 3.8), lens=20)

    if want('N8'):                                                          # porto
        x0 = 4800.0; rnd = random.Random(8); here(x0); w_ = 'watercraft-kit/'
        ground(x0, 'Concrete034', 3.0, (1, 1, 1), y1=8.0)
        sea = bx('Mare8', (x0 - 150, 8.0, -1.2), (x0 + 150, 150, -0.6), M['park'], envc); kitlook.setmat(sea, material('S_sea8', (0.02, 0.30, 0.52), rough=0.08)); A.niente_ombra(sea)
        K(w_ + 'ship-ocean-liner', x0 + 2.0, 30.0, z=-0.6, w=46.0, rot=90, coll=envc); K(w_ + 'ship-cargo-a', x0 - 13.0, 16.0, z=-0.6, w=20.0, rot=80, coll=envc)
        K(w_ + 'boat-tug-a', x0 + 6.5, 12.5, z=-0.6, w=7.0, rot=110); K(w_ + 'boat-speed-a', x0 - 2.5, 10.8, z=-0.6, w=4.5, rot=60); K(w_ + 'buoy', x0 + 1.5, 11.5, z=-0.6, h=1.6); K(w_ + 'buoy-flag', x0 + 11, 15, z=-0.6, h=2.2)
        for (xx, yy, zz, nm, rr) in ((-5.0, 4.0, 0, 'a', 10), (-5.0, 4.0, 2.6, 'b', 14), (-7.6, 6.0, 0, 'c', 0), (5.4, 5.0, 0, 'b', -8), (5.4, 5.0, 2.6, 'c', -12), (5.4, 5.0, 5.2, 'a', -6), (8.2, 3.0, 0, 'a', 80)):
            K(w_ + 'cargo-container-' + nm, x0 + xx, yy, z=zz, h=2.6, rot=rr, coll=envc)
        K(w_ + 'cargo-pile-a', x0 - 3.0, 1.8, h=1.4, rot=20); K(w_ + 'cargo-pile-b', x0 + 3.0, 1.4, h=1.4, rot=-25)
        cam_n('N8', x0, tl=(0.0, 4.0, 2.4))

    if want('N9'):                                                          # ferrovia
        x0 = 5200.0; rnd = random.Random(9); here(x0); ground(x0, 'Grass001', 3.0, (1.05, 1.35, 0.7)); t_ = 'train-kit/'
        r0, d0 = K(t_ + 'railroad-straight', x0, 5.0, s=1.0); print('RAIL', [round(v, 3) for v in d0]); bpy.data.objects.remove(r0, do_unlink=True)
        sc = 3.4 / 1.66; step = max(d0[0], d0[1]) * sc; along_x = d0[0] >= d0[1]
        for yy in (6.5, 11.5):
            for k in range(-9, 10): K(t_ + 'railroad-straight', x0 + k * step, yy, s=sc, rot=0 if along_x else 90, coll=envc)
        xx = x0 - 5.5
        for nm in ('train-locomotive-a', 'train-carriage-coal', 'train-carriage-box', 'train-carriage-tank', 'train-carriage-lumber'):
            r, d = K(t_ + nm, xx + 3.0, 6.5, s=sc, rot=90); xx += max(d[0], d[1]) + 0.25
        xx = x0 - 12.0
        for nm in ('train-electric-bullet-a', 'train-electric-bullet-b', 'train-electric-bullet-b', 'train-electric-bullet-c'):
            r, d = K(t_ + nm, xx + 3.0, 11.5, s=sc, rot=90); xx += max(d[0], d[1]) + 0.2
        for k in range(14): albero(MIX[k % len(MIX)], x0 + rnd.uniform(-16, 16), rnd.uniform(15, 22), rnd.uniform(6, 9), vista=k)
        K('car-kit/cone', x0 + 2.2, 0.8, h=0.6); K('survival-kit/signpost', x0 - 2.6, 1.4, h=1.7, rot=20)
        cam_n('N9', x0, cl=(1.2, -8.5, 3.6), tl=(0.0, 5.0, 1.6))
print('FINE')
