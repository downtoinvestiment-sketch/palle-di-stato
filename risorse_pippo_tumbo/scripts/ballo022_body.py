# ===================================================================================================================
# Prova di animazione per il video 022 (la maledizione di Giulia): Pippo maledetto balla tutto il giorno,
# avanti e indietro col bacino. Il corpo balla da solo, la faccia e' disperata (contrasto comico).
# Si unisce alla testa: cat templates/head.py scripts/ballo022_body.py > scripts/ballo022.py
# Variabile BALLO022 = percorso del .blend in uscita.
# ===================================================================================================================
import luci, random
import pippo2 as pippo
A = kitlook.A
BLEND = os.environ.get('BALLO022', '../t022/ballo022.blend')
TOTAL = 6.0; NF = int(TOTAL * FPS)
setup_render(scene, 1080, 1920, samples=4, fps=FPS, frames=NF); scene.frame_end = NF
camd = bpy.data.cameras.new('Cam'); cam = bpy.data.objects.new('Cam', camd); cac.objects.link(cam); scene.camera = cam
camd.clip_start = 0.05; camd.clip_end = 2000; camd.sensor_width = 36
tgt = empty('CamTarget', (0, 0, 1), None, cac)
ct = cam.constraints.new('TRACK_TO'); ct.target = tgt; ct.track_axis = 'TRACK_NEGATIVE_Z'; ct.up_axis = 'UP_Y'
camd.dof.use_dof = True; camd.dof.focus_object = tgt
kitlook.upgrade(scene, M, envc, prc, extras=False)
CIELO = luci.cielo_basso(scene.world, 0.4); scene.world.use_sun_shadow = False
SUN = luci.sole(prc, (0.35, -0.94), lato=1, energia=4.5)
luci.ombre_pulite(scene, mezza_risoluzione=True)

P_SPOT = Vector((2.0, -4.5, 0))
P = pippo.build_pippo(chc); P['root'].rotation_mode = 'XYZ'
for nm in 'LR': P['shoulder' + nm].rotation_mode = 'QUATERNION'
LC = luci.cinema(prc, (P_SPOT.x, P_SPOT.y, 1.2), (P_SPOT.x + 0.4, P_SPOT.y - 4.0, 1.4), distanza=3.5, lato=-1, forza=0.8)

def qdir(d): return Vector((0, 0, -1)).rotation_difference(Vector(d).normalized())
BPM = 124.0; B = BPM / 60.0                      # battute al secondo
LEG = 0.7
def ballo(t):
    """un colpo di bacino per battuta, tutto con curve morbide (niente spigoli): avanti piu' deciso, indietro piu' dolce.
    Restituisce anche 'up' (0..1): le braccia salgono e scendono piano ogni 4 battute."""
    ph = t * B
    s = math.sin(2 * math.pi * ph) + 0.28 * math.sin(4 * math.pi * ph - 0.6)     # due armoniche: la spinta in avanti e' piu' secca, ma resta liscia
    s /= 1.15
    d = 0.24 * s
    bounce = 0.04 * (0.5 - 0.5 * math.cos(4 * math.pi * ph))                     # due piccoli rimbalzi per battuta, morbidi
    sway = 0.07 * math.sin(math.pi * ph * 0.5)
    up = 0.5 - 0.5 * math.cos(math.pi * ph / 4.0)                                 # sale in 4 battute, scende in 4
    up = up * up * (3 - 2 * up)
    return s, d, bounce, sway, up
for f in range(1, NF + 1):
    t = (f - 1) / FPS
    s, d, bounce, sway, up = ballo(t)
    root = P['root']; root.location = (P_SPOT.x + sway, P_SPOT.y - d, -bounce); root.rotation_euler = (0, 0, 0.12 * math.sin(math.pi * t * B * 0.5))
    root.keyframe_insert('location', frame=f); root.keyframe_insert('rotation_euler', frame=f)
    a = math.atan2(d, LEG)                         # le gambe restano coi piedi a terra
    for nm, sd in (('hipL', -1), ('hipR', 1)):
        h_ = P[nm]; h_.rotation_euler = (a + 0.08 * bounce / 0.04, 0, sd * 0.12); h_.keyframe_insert('rotation_euler', frame=f)
    b = P['body']; b.rotation_euler = (-0.62 * s, 0.05 * math.sin(math.pi * t * B), 0); b.keyframe_insert('rotation_euler', frame=f)
    h = P['head']; h.rotation_euler = (0.25 * s + 0.1, 0, 0.08 * math.sin(math.pi * t * B * 0.5)); h.keyframe_insert('rotation_euler', frame=f)
    # braccia: tirano indietro i gomiti a ogni colpo (come chi spinge), poi su in alto ogni 4 battute
    for nm, sd in (('L', -1), ('R', 1)):
        sp = 0.5 + 0.5 * s
        giu = Vector((0.5 * sd, -0.7 + 1.2 * sp * 0.8, -0.35 + 0.12 * sp)); su = Vector((0.35 * sd, -0.15 + 0.1 * s, 0.9))
        dirv = tuple(giu.lerp(su, up))
        sh = P['shoulder' + nm]; sh.rotation_quaternion = qdir(dirv); sh.keyframe_insert('rotation_quaternion', frame=f)
# la faccia: disperata, stremata, lacrime; ogni tanto un sorriso forzato quando il bacino va avanti
def emo_key(f, nome, forza=1.0, **extra):
    e = pippo.EMOZIONI_FORTI[nome]
    fa = {k: (tuple(x * forza for x in v) if isinstance(v, tuple) else v * forza) for k, v in e['faccia'].items()}; fa.update(extra)
    pippo.express(P, f, **fa)
    if 'sopracciglia' in e:
        for (s_, nm), bb in zip(((-1, 'L'), (1, 'R')), e['sopracciglia']):
            br = P['brow' + nm]; br.rotation_euler = (0, s_ * bb * 0.45 * forza, 0); br.keyframe_insert('rotation_euler', frame=f)
    seg = pippo._segni(P)
    for k, g in seg.items():
        g.scale = (1, 1, 1) if k in e.get('extra', ()) else (0.001,) * 3; g.keyframe_insert('scale', frame=f)
emo_key(1, 'triste', 1.0, mouth_open=0.8)
emo_key(fr(2.6), 'triste', 1.0, mouth_open=0.8); emo_key(fr(2.75), 'spaventato', 1.0)
emo_key(fr(3.6), 'spaventato', 1.0); emo_key(fr(3.75), 'triste', 1.0, mouth_open=1.0)
# la maledizione: scintille viola attorno al bacino che pulsano a tempo
for k in range(int(TOTAL * B)):
    tb = k / B
    for j in range(3):
        A.effetto('particelle/magic_0%d' % (1 + (k + j) % 5), posizione=(P_SPOT.x + 0.45 * (j - 1), P_SPOT.y - 0.45, 0.7 + 0.15 * j), larghezza=0.7,
                  colore=(0.7, 0.25, 1.0), luce=2.5, animazione=(fr(tb), 8), collezione=prc)
lv = bpy.data.lights.new('LuceMaledizione', 'POINT'); lv.energy = 60; lv.color = (0.7, 0.3, 1.0); lv.use_shadow = False
lo = bpy.data.objects.new('LuceMaledizione', lv); prc.objects.link(lo); lo.location = (P_SPOT.x, P_SPOT.y - 0.6, 0.8)
for f in range(1, NF + 1):
    t = (f - 1) / FPS; s, *_ = ballo(t); lv.energy = 70 + 40 * s; lv.keyframe_insert('energy', frame=f)
# camera: mezzo busto di tre quarti, poi di profilo (si vede bene l'avanti e indietro), poi largo
SHOTS = [(0.0, 2.0, (P_SPOT.x + 2.9, P_SPOT.y - 2.6, 1.15), (P_SPOT.x + 2.6, P_SPOT.y - 2.4, 1.15), (P_SPOT.x, P_SPOT.y, 1.05), 30, 4),
         (2.0, 4.0, (P_SPOT.x + 3.6, P_SPOT.y - 0.3, 1.0), (P_SPOT.x + 3.4, P_SPOT.y - 0.5, 1.0), (P_SPOT.x, P_SPOT.y - 0.1, 0.95), 32, 5),
         (4.0, TOTAL + 0.1, (P_SPOT.x - 2.2, P_SPOT.y - 4.2, 0.6), (P_SPOT.x - 2.0, P_SPOT.y - 3.8, 0.65), (P_SPOT.x, P_SPOT.y + 0.5, 1.3), 24, 8)]
for f in range(1, NF + 1):
    t = (f - 1) / FPS; s_ = next(x for x in SHOTS if x[0] <= t < x[1]); u = sm((t - s_[0]) / (s_[1] - s_[0]))
    cam.location = lerp(s_[2], s_[3], u); tgt.location = s_[4]; camd.lens = s_[5]; camd.dof.aperture_fstop = s_[6]
    cam.keyframe_insert('location', frame=f); tgt.keyframe_insert('location', frame=f); camd.keyframe_insert('lens', frame=f); camd.dof.keyframe_insert('aperture_fstop', frame=f)
for o in bpy.data.objects:
    for fc in all_fcurves(o):
        for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT' if ('hide' in fc.data_path or o.name in ('Cam', 'CamTarget')) else 'LINEAR'
scene.render.use_motion_blur = True; scene.render.motion_blur_shutter = 0.5      # mosso: piu' fluido (sugli stacchi si rifa' con rifai_tagli.py)
os.makedirs(os.path.dirname(os.path.abspath(BLEND)), exist_ok=True)
import json; json.dump([[s[0], min(s[1], TOTAL)] for s in SHOTS], open(os.path.join(os.path.dirname(os.path.abspath(BLEND)), 'shots.json'), 'w'))
bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(BLEND)); print('SAVED', BLEND)
