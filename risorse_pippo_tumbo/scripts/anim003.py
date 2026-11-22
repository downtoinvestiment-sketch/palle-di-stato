"""Test 003 - assemblaggio e animazione: PIPPO TUTTO FARE (campo da calcio). Salva ../t003/pippo_t003.blend"""
import sys, math, os
sys.path.insert(0, os.path.dirname(__file__))
import bpy, numpy as np
from mathutils import Vector
from common import *
from render_setup import *
from params003 import *
import set003, props003, pippo, tumbo
from set003 import obj, bx, cyl, ball_, make_mats, ribbon

W, H_ = 1080, 1920
reset_scene(); scene = bpy.context.scene
setup_render(scene, W, H_, samples=16, fps=FPS, frames=FRAMES)
scene.frame_end = FRAMES
scene.eevee.shadow_resolution_scale = 0.25
rng = np.random.default_rng(11)
M = make_mats()
envc = collection('Env'); fldc = collection('Field'); chc = collection('Characters'); prc = collection('Props'); cac = collection('Cameras')

# ======================= tempi chiave (secondi, dalla trascrizione della voce) =======================
T = dict(goal0=0.5, goal1=2.0, cart0=2.4, cart1=5.6, ball0=5.9, ball1=8.8, doze0=8.95, doze1=11.4, roll0=10.6, roll1=12.3, line0=12.3, line1=13.6,
         sky0=13.0, sky1=15.0, rain0=13.9, rain1=24.9, flood0=15.6, flood1=20.6, drain0=22.0, drain1=24.3,
         tr0=21.8, tr1=22.9, pipe0=22.9, pipe1=23.9, grav0=23.9, grav1=24.6, sand0=24.5, sand1=25.1,
         syn0=25.2, syn1=27.3, seam0=27.5, seam1=28.9, glue0=29.26, glue1=30.2, inf0=30.25, inf1=31.2, l30=31.3, l31=32.7,
         heat0=32.9, heat1=36.3, up0=36.4, up1=37.6, sod0=37.7, sod1=39.3, irr0=38.8, irr1=39.6, l40=39.5, l41=40.2, flag0=39.6, flag1=40.4,
         dusk0=40.4, dusk1=42.4, play0=40.8, play1=42.7, kick=43.25)

# ======================= città + campo =======================
houses, cityinfo = set003.build_city(envc, M, rng)
F = set003.build_field(fldc, M, rng)
strips, strip_x = F['strips'], F['strip_x']
# istante in cui le ruspe passano su ogni striscia (x crescente)
def x_to_t(x): return T['doze0'] + (x + 14.5) / 29.0 * (T['doze1'] - T['doze0'])
strip_t = [x_to_t(0.5 * (a + b)) for (a, b) in strip_x]
for s, o in enumerate(strips):
    o.data.shape_keys.key_blocks['flat'].value = 0.0
    o.data.shape_keys.key_blocks['flat'].keyframe_insert('value', frame=fr(strip_t[s] - 0.25))
    o.data.shape_keys.key_blocks['flat'].value = 1.0
    o.data.shape_keys.key_blocks['flat'].keyframe_insert('value', frame=fr(strip_t[s] + 0.25))
def flat_w(x, t):
    """peso di appiattimento (0 sconnesso, 1 piatto) al punto x e tempo t."""
    s = int(np.clip(np.searchsorted([b for (_, b) in strip_x], x), 0, NSTRIP - 1))
    return float(np.clip((t - (strip_t[s] - 0.25)) / 0.5, 0, 1))

# ======================= porte, righe =======================
GL, GLnet = set003.goal('GoalL', -1, M, fldc); GR, GRnet = set003.goal('GoalR', 1, M, fldc)
GL.location = (-6.45, 0, 0); GR.location = (6.45, 0, 0)
GL.rotation_euler = (0, 0, 0)

def perim(x0, x1, y0, y1): return [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)]
def resample(pts, step=0.12):
    pts = np.asarray(pts, float); out = [pts[0]]
    for a, b in zip(pts[:-1], pts[1:]):
        d = np.linalg.norm(b - a); n = max(1, int(d / step))
        for k in range(1, n + 1): out.append(a + (b - a) * k / n)
    return np.array(out)
def arclen(p): return np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(p, axis=0), axis=1))])

# percorso storto: parte da (-10,-3.6) -> (-10,-6.25) -> (10,-6.25) -> (10,6.25) -> (-10,6.25) -> (-10,-3.6)
route = resample([(-10, -3.6), (-10, -6.25), (10, -6.25), (10, 6.25), (-10, 6.25), (-10, -3.6)])
sarr = arclen(route); Ltot = sarr[-1]
wob = 0.42 * np.sin(sarr * 0.55 + 0.7) + 0.22 * np.sin(sarr * 1.35 + 2.0)
tang = np.gradient(route, axis=0); tang /= (np.linalg.norm(tang, axis=1)[:, None] + 1e-9)
nrm = np.stack([-tang[:, 1], tang[:, 0]], 1)
crooked = route + nrm * wob[:, None]
def route_t(s):  # tempo in cui il carrello e' a lunghezza s
    return T['cart0'] + (T['cart1'] - T['cart0']) * (s / Ltot)
# pezzi per striscia (per l'appiattimento)
def xs_strip(x): return int(np.clip(np.searchsorted([b for (_, b) in strip_x], x), 0, NSTRIP - 1))
pieces = []; start = 0
for i in range(1, len(crooked) + 1):
    if i == len(crooked) or xs_strip(crooked[i, 0]) != xs_strip(crooked[start, 0]):
        seg = crooked[max(start - 1, 0):i]; sa = sarr[max(start - 1, 0)]; sb = sarr[i - 1]
        if len(seg) >= 2: pieces.append((seg, sa, sb, xs_strip(crooked[start, 0])))
        start = i
crooked_objs = []
for k, (seg, sa, sb, sidx) in enumerate(pieces):
    fs = fr(route_t(sa)); du = max(1, int((route_t(sb) - route_t(sa)) * FPS))
    o = ribbon('Crooked%d' % k, seg, 0.22, M['line'], fldc, lambda x, y: float(H(x, y)) + 0.025, flat_z=0.025, build=(fs, du))
    sk = o.data.shape_keys.key_blocks['flat']
    sk.value = 0.0; sk.keyframe_insert('value', frame=fr(strip_t[sidx] - 0.25)); sk.value = 1.0; sk.keyframe_insert('value', frame=fr(strip_t[sidx] + 0.25))
    crooked_objs.append(o)

def straight_lines(tstart, tend, z, name):
    """righe dritte: perimetro, meta' campo, cerchio, aree. Tutte crescono insieme (time-lapse)."""
    objs = []
    paths = [perim(-PX, PX, -PY, PY)[:], [(0, -PY), (0, PY)],
             [(-PX, -3.4), (-PX + 3.8, -3.4), (-PX + 3.8, 3.4), (-PX, 3.4)], [(PX, -3.4), (PX - 3.8, -3.4), (PX - 3.8, 3.4), (PX, 3.4)],
             [(-PX, -1.9), (-PX + 1.3, -1.9), (-PX + 1.3, 1.9), (-PX, 1.9)], [(PX, -1.9), (PX - 1.3, -1.9), (PX - 1.3, 1.9), (PX, 1.9)],
             [(1.8 * math.cos(a), 1.8 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 61)]]
    for i, p in enumerate(paths):
        p = resample(p, 0.12)
        o = ribbon('%s%d' % (name, i), p, 0.2, M['line'], fldc, lambda x, y: z, build=(fr(tstart), max(2, int((tend - tstart) * FPS))))
        objs.append(o)
    # dischetto e punto centrale
    for (px, py, rr) in [(0, 0, 0.22), (-7.2, 0, 0.14), (7.2, 0, 0.14)]:
        d = cyl('%sSpot' % name, rr, 0.01, (px, py, z + 0.005), M['line'], fldc)
        d.scale = (1, 1, 1); d.hide_render = True; d.keyframe_insert('hide_render', frame=1)
        d.hide_render = False; d.keyframe_insert('hide_render', frame=fr(tend))
        objs.append(d)
    return objs
L1 = straight_lines(T['line0'], T['line1'], 0.03, 'L1')       # su terra livellata
L3 = straight_lines(T['l30'], T['l31'], Z_SYN + 0.025, 'L3')   # su sintetico
L4 = straight_lines(T['l40'], T['l41'], Z_GRASS + 0.02, 'L4')  # su erba

# ======================= strati: acqua, trincee, tubi, ghiaia, sabbia =======================
def grow(o, prop_idx, t0, t1, v0=0.0001, v1=1.0, interp='BEZIER'):
    s = list(o.scale); s[prop_idx] = v0; o.scale = tuple(s); o.keyframe_insert('scale', frame=fr(t0))
    s[prop_idx] = v1; o.scale = tuple(s); o.keyframe_insert('scale', frame=fr(t1))
def hide_at(o, t_hide=None, t_show=None):
    if t_show is not None:
        o.hide_render = True; o.keyframe_insert('hide_render', frame=1); o.hide_render = False; o.keyframe_insert('hide_render', frame=fr(t_show))
    if t_hide is not None:
        if t_show is None: o.hide_render = False; o.keyframe_insert('hide_render', frame=1)
        o.hide_render = True; o.keyframe_insert('hide_render', frame=fr(t_hide))
water = bx('Water', (-BX, -BY, 0.0), (BX, BY, 1.0), M['water'], fldc)
water.scale = (2 * BX, 2 * BY, 0.0001)
for (t, v) in [(1, 0.0001), (T['flood0'], 0.0001), (T['flood1'], WATER_H), (T['drain0'], WATER_H), (T['drain1'], 0.0001)]:
    water.scale = (2 * BX, 2 * BY, v); water.keyframe_insert('scale', frame=fr(t) if t != 1 else 1)
water.hide_render = True; water.keyframe_insert('hide_render', frame=1); water.hide_render = False; water.keyframe_insert('hide_render', frame=fr(T['flood0']) - 1)
water.hide_render = True; water.keyframe_insert('hide_render', frame=fr(T['drain1']) + 1)

trench_ys = [-4.1, 0.0, 4.1]
for i, y in enumerate(trench_ys):
    pts = resample([(-BX + 0.2, y), (BX - 0.2, y)], 0.15)
    ribbon('Trench%d' % i, pts, 0.7, M['dirt_dark'], fldc, lambda x, yy: 0.012, build=(fr(T['tr0']), int((T['tr1'] - T['tr0']) * FPS)))
    pr = empty('PipeRoot%d' % i, (-BX + 0.2, y, 0.06), None, fldc)
    cyl('Pipe%d' % i, 0.17, 2 * BX - 0.4, ((BX - 0.2), 0, 0), M['pipe'], fldc, rot=(0, math.pi / 2, 0), parent=pr)
    pr.scale = (0.0001, 1, 1); pr.keyframe_insert('scale', frame=1); pr.scale = (0.0001, 1, 1); pr.keyframe_insert('scale', frame=fr(T['pipe0']))
    pr.scale = (1, 1, 1); pr.keyframe_insert('scale', frame=fr(T['pipe1']))
# rami trasversali dei tubi (collegano ai bordi)
gravel = bx('Gravel', (-BX, -BY, 0.0), (BX, BY, 1.0), M['gravel'], fldc); grow(gravel, 2, T['grav0'], T['grav1'], 0.0001, Z_GRAVEL)
gravel.hide_render = True; gravel.keyframe_insert('hide_render', frame=1); gravel.hide_render = False; gravel.keyframe_insert('hide_render', frame=fr(T['grav0']) - 1)
sand = bx('Sand', (-BX, -BY, Z_GRAVEL), (BX, BY, Z_GRAVEL + 1.0), M['sand'], fldc); grow(sand, 2, T['sand0'], T['sand1'], 0.0001, Z_SAND - Z_GRAVEL)
sand.hide_render = True; sand.keyframe_insert('hide_render', frame=1); sand.hide_render = False; sand.keyframe_insert('hide_render', frame=fr(T['sand0']) - 1)

# ======================= manto sintetico (8 rotoli) =======================
NS = 8; wS = 2 * BX / NS
syn = []; rolls = []
for i in range(NS):
    x0 = -BX + i * wS
    mat = M['syn1'] if i % 2 == 0 else M['syn2']
    o = bx('Syn%d' % i, (x0, -BY, Z_SAND), (x0 + wS, BY, Z_SYN), mat, fldc)
    t0 = T['syn0'] + i * (T['syn1'] - T['syn0']) / NS * 0.85; t1 = T['syn0'] + (i + 1) * (T['syn1'] - T['syn0']) / NS * 0.85 + 0.15 * (T['syn1'] - T['syn0'])
    o.scale = (wS, 0.0001, Z_SYN - Z_SAND); o.keyframe_insert('scale', frame=1); o.keyframe_insert('scale', frame=fr(t0))
    o.scale = (wS, 2 * BY, Z_SYN - Z_SAND); o.keyframe_insert('scale', frame=fr(t1))
    # srotola al contrario: stesso movimento per il ritiro (36.4-37.6): tempi invertiti
    u0 = T['up0'] + (NS - 1 - i) * (T['up1'] - T['up0']) / NS * 0.85; u1 = u0 + (T['up1'] - T['up0']) * 0.3
    o.scale = (wS, 2 * BY, Z_SYN - Z_SAND); o.keyframe_insert('scale', frame=fr(u0))
    o.scale = (wS, 0.0001, Z_SYN - Z_SAND); o.keyframe_insert('scale', frame=fr(u1))
    o.hide_render = True; o.keyframe_insert('hide_render', frame=1); o.hide_render = False; o.keyframe_insert('hide_render', frame=fr(t0))
    o.hide_render = True; o.keyframe_insert('hide_render', frame=fr(u1) + 1)
    syn.append((o, x0, t0, t1, u0, u1))
    # rotolo
    r = cyl('Roll%d' % i, 0.28, wS - 0.1, (x0 + wS / 2, -BY, Z_SAND + 0.3), M['syn1'] if i % 2 == 0 else M['syn2'], fldc, rot=(0, math.pi / 2, 0))
    rolls.append((r, x0, t0, t1, u0, u1))
for (r, x0, t0, t1, u0, u1) in rolls:
    def kk(t, y, s): 
        r.location = (x0 + wS / 2, y, Z_SAND + 0.02 + 0.28 * s); r.scale = (s, s, 1); r.keyframe_insert('location', frame=fr(t)); r.keyframe_insert('scale', frame=fr(t))
    kk(1 / FPS, -BY, 0.0001); kk(t0 - 1 / FPS, -BY, 0.0001); kk(t0, -BY, 1.0); kk(t1, BY, 0.0001)
    kk(u0, BY, 0.0001); kk(u0 + 0.05, BY, 0.2); kk(u1, -BY, 1.0); kk(u1 + 0.15, -BY, 0.0001)
    # il rotolo e' un cilindro con asse X: scalare x e y insieme
# giunzioni: strisce che si aprono e si richiudono
for (o, x0, t0, t1, u0, u1) in syn:
    i = syn.index((o, x0, t0, t1, u0, u1)); dx = (i - (NS - 1) / 2) * 0.05
    o.location = (x0 + 0, -BY, Z_SAND)
    o.keyframe_insert('location', frame=1)
    o.location = (x0, -BY, Z_SAND); o.keyframe_insert('location', frame=fr(T['seam0']))
    o.location = (x0 + dx * 2.4, -BY, Z_SAND); o.keyframe_insert('location', frame=fr(T['seam1']))
    o.location = (x0 + dx * 2.4, -BY, Z_SAND); o.keyframe_insert('location', frame=fr(T['glue0']))
    o.location = (x0, -BY, Z_SAND); o.keyframe_insert('location', frame=fr(T['glue1']))
# nastro delle giunzioni + intaso
for i in range(1, NS):
    x = -BX + i * wS
    ribbon('Seam%d' % i, resample([(x, -BY + 0.3), (x, BY - 0.3)], 0.2), 0.16, M['dark'], fldc, lambda xx, yy: Z_SYN + 0.006,
           build=(fr(T['glue0']), int((T['glue1'] - T['glue0']) * FPS)))
infill = bx('Infill', (-BX, -BY, Z_SYN), (BX, BY, Z_SYN + 0.015), M['infill'], fldc)
infill.scale = (0.0001, 2 * BY, 0.015)
for (t, v) in [(1, 0.0001), (T['inf0'], 0.0001), (T['inf1'], 2 * BX)]:
    infill.scale = (v, 2 * BY, 0.015); infill.keyframe_insert('scale', frame=fr(t) if t != 1 else 1)
infill.hide_render = True; infill.keyframe_insert('hide_render', frame=1); infill.hide_render = False; infill.keyframe_insert('hide_render', frame=fr(T['inf0']) - 1)
infill.hide_render = True; infill.keyframe_insert('hide_render', frame=fr(T['up1']) + 1)
for Lobjs in (L3,):
    for o in Lobjs: pass

# ======================= erba naturale (zolle a strisce) =======================
NG = 16; wG = 2 * BX / NG
for i in range(NG):
    x0 = -BX + i * wG
    mat = M['gr1'] if i % 2 == 0 else M['gr2']
    o = bx('Sod%d' % i, (x0, -BY, Z_SAND), (x0 + wG, BY, Z_GRASS), mat, fldc)
    t0 = T['sod0'] + i * (T['sod1'] - T['sod0']) / NG * 0.85; t1 = t0 + (T['sod1'] - T['sod0']) * 0.2
    o.scale = (wG, 0.0001, Z_GRASS - Z_SAND); o.keyframe_insert('scale', frame=1); o.keyframe_insert('scale', frame=fr(t0))
    o.scale = (wG, 2 * BY, Z_GRASS - Z_SAND); o.keyframe_insert('scale', frame=fr(t1))
    o.hide_render = True; o.keyframe_insert('hide_render', frame=1); o.hide_render = False; o.keyframe_insert('hide_render', frame=fr(t0))
    # rotolo di zolla
    r = cyl('SodRoll%d' % i, 0.30, wG - 0.08, (x0 + wG / 2, -BY, Z_SAND + 0.3), mat, fldc, rot=(0, math.pi / 2, 0))
    def kk(t, y, s, r=r, x0=x0):
        r.location = (x0 + wG / 2, y, Z_SAND + 0.02 + 0.30 * s); r.scale = (s, s, 1); r.keyframe_insert('location', frame=fr(t)); r.keyframe_insert('scale', frame=fr(t))
    kk(1 / FPS, -BY, 0.0001); kk(t0 - 1 / FPS, -BY, 0.0001); kk(t0, -BY, 1.0); kk(t1, BY, 0.0001)

# ======================= irrigatori, bandierine, luci =======================
sprs = []
for k, (sx, sy) in enumerate([(-7.0, -3.5), (-7.0, 3.5), (0.0, -3.5), (0.0, 3.5), (7.0, -3.5), (7.0, 3.5)]):
    r, head, sp = props003.sprinkler(prc, M)
    r.location = (sx, sy, Z_GRASS - 0.30); r.hide_render = False
    r.location = (sx, sy, Z_GRASS - 0.34); r.keyframe_insert('location', frame=1); r.keyframe_insert('location', frame=fr(T['irr0'] + 0.12 * k))
    r.location = (sx, sy, Z_GRASS); r.keyframe_insert('location', frame=fr(T['irr0'] + 0.12 * k + 0.35))
    r.hide_render = True; r.keyframe_insert('hide_render', frame=1); r.hide_render = False; r.keyframe_insert('hide_render', frame=fr(T['irr0'] + 0.12 * k) - 1)
    for j, c in enumerate(sp):
        c.hide_render = True; c.keyframe_insert('hide_render', frame=1); c.hide_render = False; c.keyframe_insert('hide_render', frame=fr(T['irr1']))
        for ff in range(fr(T['irr1']), FRAMES + 1, 3):
            c.scale = (0.06, 0.06, 1.3 * (0.85 + 0.15 * math.sin(ff * 0.9 + j))); c.keyframe_insert('scale', frame=ff)
    for ff in range(fr(T['irr1']), FRAMES + 1, 2):
        head.rotation_euler = (0, 0, (ff - fr(T['irr1'])) * 0.35); head.keyframe_insert('rotation_euler', frame=ff)
    sprs.append(r)
for k, (fx, fy) in enumerate([(-PX, -PY), (-PX, PY), (PX, -PY), (PX, PY)]):
    fl = props003.flag(prc, M); fl.location = (fx, fy, Z_GRASS - 1.2); fl.keyframe_insert('location', frame=1)
    fl.location = (fx, fy, Z_GRASS - 1.2); fl.keyframe_insert('location', frame=fr(T['flag0'] + 0.1 * k))
    fl.location = (fx, fy, Z_GRASS); fl.keyframe_insert('location', frame=fr(T['flag0'] + 0.1 * k + 0.4))
    fl.hide_render = True; fl.keyframe_insert('hide_render', frame=1); fl.hide_render = False; fl.keyframe_insert('hide_render', frame=fr(T['flag0'] + 0.1 * k) - 1)
for net in (GLnet, GRnet):
    net.scale = (1, 1, 0.0001); net.keyframe_insert('scale', frame=1); net.keyframe_insert('scale', frame=fr(T['flag0']))
    net.scale = (1, 1, 1); net.keyframe_insert('scale', frame=fr(T['flag1']))
lights = []
for (lx, ly) in [(-12.6, -9.2), (12.6, -9.2), (-12.6, 9.2), (12.6, 9.2)]:
    r, head, lamp = props003.floodlight(prc, M)
    r.location = (lx, ly, 0); r.hide_render = False
    head.rotation_euler = (0, 0, math.atan2(-lx, ly) + math.pi)  # volta il pannello verso il campo
    ang = math.atan2(0 - ly, 0 - lx)
    head.rotation_euler = (0, 0, ang + math.pi / 2)
    sl = bpy.data.lights.new('Flood', 'SPOT'); sl.energy = 0.0; sl.spot_size = math.radians(80); sl.spot_blend = 0.5; sl.shadow_soft_size = 0.5
    so = bpy.data.objects.new('Flood', sl); prc.objects.link(so); so.parent = head
    so.location = (0, 0, 0); so.rotation_euler = (math.radians(60), 0, 0)
    lights.append((so, sl, lamp))
    lamp.material_slots[0].link = 'OBJECT'
for (so, sl, lamp) in lights:
    sl.energy = 0.0; sl.keyframe_insert('energy', frame=fr(T['dusk0'])); sl.energy = 6500.0; sl.keyframe_insert('energy', frame=fr(T['dusk1']))
    sl.energy = 0.0; sl.keyframe_insert('energy', frame=1)
fmat = M['lampfx'].node_tree.nodes['Principled BSDF'].inputs['Emission Strength']
fmat.default_value = 0.0; fmat.keyframe_insert('default_value', frame=1); fmat.keyframe_insert('default_value', frame=fr(T['dusk0']))
fmat.default_value = 25.0; fmat.keyframe_insert('default_value', frame=fr(T['dusk1']))
wmat = M['window'].node_tree.nodes['Principled BSDF'].inputs['Emission Strength']
wmat.default_value = 0.0; wmat.keyframe_insert('default_value', frame=1); wmat.keyframe_insert('default_value', frame=fr(T['dusk0']))
wmat.default_value = 4.0; wmat.keyframe_insert('default_value', frame=fr(T['dusk1']))

# ======================= cielo, sole, nuvole, pioggia, vapore =======================
scene.world = bpy.data.worlds.new('W'); wd = scene.world; wd.use_nodes = True; nt = wd.node_tree
for n in list(nt.nodes): nt.nodes.remove(n)
out = nt.nodes.new('ShaderNodeOutputWorld'); bg = nt.nodes.new('ShaderNodeBackground')
tc = nt.nodes.new('ShaderNodeTexCoord'); sep = nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(tc.outputs['Generated'], sep.inputs['Vector'])
def skyramp(top, bot):
    ramp = nt.nodes.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].color = (*bot, 1); ramp.color_ramp.elements[1].color = (*top, 1)
    ramp.color_ramp.elements[0].position = 0.45; ramp.color_ramp.elements[1].position = 0.62
    nt.links.new(sep.outputs['Z'], ramp.inputs['Fac']); return ramp
day = skyramp((0.30, 0.60, 1.0), (0.90, 0.93, 0.96)); gray = skyramp((0.42, 0.45, 0.50), (0.60, 0.62, 0.65))
dusk = skyramp((0.10, 0.14, 0.32), (0.55, 0.36, 0.38)); heat = skyramp((0.62, 0.78, 0.98), (1.0, 0.92, 0.72))
mx1 = nt.nodes.new('ShaderNodeMix'); mx1.data_type = 'RGBA'; mx2 = nt.nodes.new('ShaderNodeMix'); mx2.data_type = 'RGBA'; mx3 = nt.nodes.new('ShaderNodeMix'); mx3.data_type = 'RGBA'
nt.links.new(day.outputs['Color'], mx1.inputs[6]); nt.links.new(gray.outputs['Color'], mx1.inputs[7])
nt.links.new(mx1.outputs[2], mx2.inputs[6]); nt.links.new(heat.outputs['Color'], mx2.inputs[7])
nt.links.new(mx2.outputs[2], mx3.inputs[6]); nt.links.new(dusk.outputs['Color'], mx3.inputs[7])
nt.links.new(mx3.outputs[2], bg.inputs['Color']); nt.links.new(bg.outputs['Background'], out.inputs['Surface'])
def kfs(sock, pairs, default=None):
    for (t, v) in pairs:
        sock.default_value = v; sock.keyframe_insert('default_value', frame=fr(t) if t > 0 else 1)
kfs(mx1.inputs[0], [(0, 0), (T['sky0'], 0), (T['sky1'], 1), (T['drain1'], 1), (T['sand1'] + 0.3, 0)])
kfs(mx2.inputs[0], [(0, 0), (T['heat0'] - 0.4, 0), (T['heat0'] + 0.5, 1), (T['heat1'], 1), (T['up1'], 0)])
kfs(mx3.inputs[0], [(0, 0), (T['dusk0'], 0), (T['dusk1'], 1)])
kfs(bg.inputs['Strength'], [(0, 0.55), (T['sky0'], 0.55), (T['sky1'], 0.38), (T['drain1'], 0.38), (T['sand1'] + 0.3, 0.55), (T['dusk0'], 0.55), (T['dusk1'], 0.35)])
sun = bpy.data.lights.new('Sun', 'SUN'); so = bpy.data.objects.new('Sun', sun); prc.objects.link(so); so.rotation_euler = (math.radians(52), math.radians(8), math.radians(35))
sun.angle = math.radians(2.5)
def sunkey(t, e, col=None):
    sun.energy = e; sun.keyframe_insert('energy', frame=fr(t) if t > 0 else 1)
    if col: sun.color = col; sun.keyframe_insert('color', frame=fr(t) if t > 0 else 1)
sunkey(0, 2.6, (1, 0.97, 0.92)); sunkey(T['sky0'], 2.6, (1, 0.97, 0.92)); sunkey(T['sky1'], 0.7, (0.8, 0.85, 1)); sunkey(T['drain1'], 0.7, (0.8, 0.85, 1))
sunkey(T['sand1'] + 0.3, 2.6, (1, 0.97, 0.92)); sunkey(T['heat0'], 3.2, (1, 0.9, 0.7)); sunkey(T['heat1'], 3.6, (1, 0.85, 0.6)); sunkey(T['up1'], 2.8, (1, 0.97, 0.92))
sunkey(T['dusk0'], 2.6, (1, 0.97, 0.92)); sunkey(T['dusk1'], 0.25, (0.7, 0.75, 1.0))
# nuvole
for k, (cx, cy, cz, s) in enumerate([(-14, -3, 13, 1.7), (-18, 4, 14, 2.0), (-12, 9, 12.5, 1.5), (-16, -9, 13.5, 1.8)]):
    c = props003.cloud(prc, M, (cx, cy, cz), s)
    c.location = (cx - 25, cy, cz); c.keyframe_insert('location', frame=1); c.keyframe_insert('location', frame=fr(T['sky0'] - 0.4 + 0.2 * k))
    c.location = (cx + 14 - 3 * k, cy, cz); c.keyframe_insert('location', frame=fr(T['sky1'] + 0.5 + 0.2 * k))
    c.location = (cx + 14 - 3 * k, cy, cz); c.keyframe_insert('location', frame=fr(T['sand1']))
    c.location = (cx + 45, cy, cz); c.keyframe_insert('location', frame=fr(T['sand1'] + 3.0))
# pioggia (cicli di caduta)
for k in range(3):
    ro = props003.rain_layer(prc, M, 100 + k)
    ro.location = (0, 0, 0); ro.keyframe_insert('location', frame=1)
    ro.hide_render = True; ro.keyframe_insert('hide_render', frame=1); ro.hide_render = False; ro.keyframe_insert('hide_render', frame=fr(T['rain0']))
    ro.hide_render = True; ro.keyframe_insert('hide_render', frame=fr(T['rain1']))
    ro.location = (0, 0, -3.0 - k * 0.2); ro.keyframe_insert('location', frame=7 + k)
    for fc in all_fcurves(ro):
        if fc.data_path == 'location':
            for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'
            fc.modifiers.new('CYCLES')
# vapore dal sintetico (b4 caldo)
steam = []
for k in range(12):
    o = ball_('Steam', 0.18, (rng.uniform(-6, 6), rng.uniform(-4, 4), Z_SYN), M['rain'], prc, sc=(1, 1, 1))
    o.hide_render = True; o.keyframe_insert('hide_render', frame=1)
    o.hide_render = False; o.keyframe_insert('hide_render', frame=fr(T['heat0'] + 0.3 + 0.1 * k))
    o.hide_render = True; o.keyframe_insert('hide_render', frame=fr(T['up1']))
    for j in range(0, int((T['up1'] - T['heat0']) * FPS), 3):
        ff = fr(T['heat0'] + 0.3) + j; ph = ((j / 3 + k * 2.3) % 9) / 9.0
        o.location = (o.location.x if j == 0 else o.location.x, o.location.y, Z_SYN + 0.1 + 1.3 * ph)
        o.scale = (0.05 + 0.04 * ph,) * 3; o.keyframe_insert('location', frame=ff); o.keyframe_insert('scale', frame=ff)
    steam.append(o)

# ======================= personaggi (modelli ESISTENTI, invariati) =======================
P = pippo.build_pippo(chc); Tb = tumbo.build_tumbo(chc, scale=0.75)
for r in (P['root'], Tb['root']): r.rotation_mode = 'XYZ'
for nm in 'LR': P['shoulder' + nm].rotation_mode = 'QUATERNION'
def qdir(d, rest=(0, 0, -1)): return Vector(rest).rotation_difference(Vector(d).normalized())

def ground(x, y, t):
    w = flat_w(x, t) if t > T['doze0'] - 0.5 else 0.0
    inside = abs(x) < BX and abs(y) < BY
    g = (1 - w) * float(H(x, y)) if inside else 0.0
    # strati
    lay = 0.0
    if inside:
        lay = float(np.interp(t, [T['grav0'], T['grav1'], T['sand0'], T['sand1'], T['syn0'] + 1.0, T['up0'], T['up1'], T['sod1']],
                                  [0, Z_GRAVEL, Z_GRAVEL, Z_SAND, Z_SYN, Z_SYN, Z_SAND, Z_GRASS]))
    return g + lay

def build_track(wps):
    """wps: [(t, x, y, mode, face)]  -> funzione stato(t) = (x, y, yaw, gait amp, phase) """
    ts = [w[0] for w in wps]
    def state_at(t):
        t = min(max(t, ts[0]), ts[-1])
        i = max(0, min(len(wps) - 2, int(np.searchsorted(ts, t, side='right') - 1)))
        a, b = wps[i], wps[i + 1]
        u = (t - a[0]) / max(b[0] - a[0], 1e-6)
        x = a[1] + (b[1] - a[1]) * u; y = a[2] + (b[2] - a[2]) * u
        d = math.hypot(b[1] - a[1], b[2] - a[2]); speed = d / max(b[0] - a[0], 1e-6)
        return x, y, i, speed, (b[1] - a[1], b[2] - a[2])
    return state_at

def yaw_dir(dx, dy): return math.atan2(dx, -dy)

# ======================= tracce dei personaggi =======================
NF = FRAMES
tt = np.array([(f - 1) / FPS for f in range(1, NF + 1)])
def eval_track(wps, override=None):
    """valuta le waypoint a ogni frame -> arrays x,y,yaw,speed"""
    st = build_track(wps); X = np.zeros(NF); Y = np.zeros(NF); YAW = np.zeros(NF); SP = np.zeros(NF); last = 0.0
    for k, t in enumerate(tt):
        if override is not None:
            o = override(t)
        else: o = None
        if o is not None:
            x, y, yaw, sp = o; last = yaw
        else:
            x, y, i, sp, (dx, dy) = st(t)
            if sp > 0.3: yaw = yaw_dir(dx, dy)
            else:
                fp = wps[i][4] if len(wps[i]) > 4 and wps[i][4] is not None else None
                yaw = yaw_dir(fp[0] - x, fp[1] - y) if fp else last
            last = yaw
        X[k], Y[k], YAW[k], SP[k] = x, y, yaw, sp
    return X, Y, YAW, SP

# ---- Pippo
def cart_state(t):
    """posizione del carrello e di Pippo durante il percorso storto"""
    if not (T['cart0'] <= t <= T['cart1']): return None
    s = (t - T['cart0']) / (T['cart1'] - T['cart0']) * Ltot
    i = int(np.clip(np.searchsorted(sarr, s), 1, len(crooked) - 1))
    cp = crooked[i]; hd = tang[i]
    px, py = cp[0] - hd[0] * 1.0, cp[1] - hd[1] * 1.0
    return px, py, yaw_dir(hd[0], hd[1]), Ltot / (T['cart1'] - T['cart0'])
pw = [(0, -4.7, 0, 'stand', (-12, 0)), (0.5, -4.7, 0, 'walk'), (2.0, -8.25, 0, 'walk'), (2.4, -10.0, -2.6, 'run'), (5.6, -10.0, -2.6, 'stand', (-6, -1.5)),
      (6.0, -10.0, -2.6, 'stand', (-6, -1.5)), (8.0, -9.5, -5.0, 'walk'), (8.7, -9.5, -8.4, 'walk', (-6, -3)), (12.8, -9.5, -8.4, 'stand', (-5, 0)),
      (14.3, -3.5, -3.5, 'walk', (-3.5, -6)), (21.0, -3.5, -3.5, 'stand', (-3.5, -6)), (21.8, -8.0, -4.1, 'run', (-8, 0)), (23.3, -8.0, -4.1, 'stand', (-8, 0)),
      (24.3, -8.0, -8.5, 'walk', (-8, 0)), (28.4, -8.0, -8.5, 'stand', (-3, 0)), (29.2, -2.75, -2.5, 'run', (-2.75, 5)), (30.2, -2.75, 2.5, 'run', (-2.75, 5)),
      (31.2, -2.75, 5.7, 'run', (-2.75, 0)), (36.0, -2.75, 5.7, 'stand', (0, 0)), (40.5, -2.75, 5.7, 'stand', (0, 0)), (42.4, -1.4, 1.3, 'walk', (3, 0)), (45.1, -1.4, 1.3, 'stand', (3, 0))]
PX_, PY_, PYAW, PSP = eval_track(pw, cart_state)
# ---- Tumbo
tw = [(0, 4.95, 0, 'stand', (12, 0)), (0.5, 4.95, 0, 'walk'), (2.0, 8.5, 0, 'walk'), (2.5, 8.5, 3.0, 'run', (0, 3)), (5.3, -6.8, -0.9, 'run', (-6, -1.5)),
      (5.9, -6.9, -1.0, 'stand', (-6, -1.5)), (6.3, -6.9, -1.0, 'stand'), (8.7, -3.0, -8.9, 'run', (-4, -9)), (12.8, -4.0, -8.9, 'stand', (-4, -9)),
      (14.2, -2.2, -2.4, 'walk', (0, -2.4)), (21.0, -2.2, -2.4, 'stand', (-3, -6)), (21.8, -8.0, -3.2, 'run', (-8, 0)), (23.3, -8.0, -3.2, 'stand', (-8, 0)),
      (24.3, -9.0, -8.9, 'walk', (-8, 0)), (26.8, -9.0, -8.9, 'stand', (-8, 0)), (27.2, -9.0, -2.0, 'run', (0, 0)), (28.4, 0.2, 1.4, 'run', (0, 0)),
      (29.4, 0.2, 1.4, 'stand', (0, 6)), (30.4, 2.0, 5.9, 'run', (3, 0)), (32.8, 2.0, 5.9, 'stand', (0, 0)), (33.0, 0.0, 0.0, 'run', (0, 0)), (34.0, 3.0, 2.0, 'run', (4, 0)),
      (35.0, -2.0, -2.0, 'run', (0, 0)), (35.9, -2.0, -2.0, 'run', (0, -6)), (36.6, -3.6, -8.9, 'run', (0, 0)), (40.9, -3.6, -8.9, 'stand', (-3.6, -9.5)),
      (42.0, -0.6, -0.5, 'run', (0, 0)), (42.7, -0.9, -0.7, 'walk', (0, 0)), (43.15, -0.8, -0.2, 'walk', (3, 0)), (43.5, -0.8, -0.2, 'stand', (10, 0)), (45.1, -0.8, -0.2, 'stand', (10, 0))]
TX_, TY_, TYAW, TSP = eval_track(tw)

# ---- palla (fisica semplice sul terreno sconnesso)
def sim_ball():
    p = np.array([-6.0, -1.5, float(H(-6.0, -1.5)) + BALL_R]); v = np.array([0.0, 0.0, 0.0]); out = {}
    dt = 1 / 240.0; t = 0.0; kick = T['ball0']; state = 'rest'; frames = {}
    def gr(x, y): return float(H(x, y)) if (abs(x) < BX and abs(y) < BY) else 0.0
    nsteps = int(T['ball1'] * 240)
    traj = np.zeros((NF, 3)); k = 0
    for n in range(int((T['ball1'] + 1.5) * 240) + 1):
        t = n * dt
        if t >= kick and state == 'rest': v = np.array([4.2, -2.4, 3.4]); state = 'fly'
        if state == 'fly':
            v[2] -= 14.0 * dt; p = p + v * dt
            zg = gr(p[0], p[1]) + BALL_R
            if p[2] < zg:
                p[2] = zg; e = 0.6; eps = 0.03
                gx = (gr(p[0] + eps, p[1]) - gr(p[0] - eps, p[1])) / (2 * eps); gy = (gr(p[0], p[1] + eps) - gr(p[0], p[1] - eps)) / (2 * eps)
                nv = np.array([-gx, -gy, 1.0]); nv /= np.linalg.norm(nv)
                vn = v @ nv
                if vn < 0: v = v - (1 + e) * vn * nv
                v[:2] *= 0.992
            if abs(p[0]) > 9.2 and abs(p[1]) < BY: v[0] = -v[0] * 0.8; p[0] = np.sign(p[0]) * 9.2
            if abs(p[1]) > BY + 2.2: v[:2] *= 0.96
        f = int(round(t * FPS))
        if f < NF and (n % 10 == 0): traj[f] = p
    # riempie frame
    for f in range(NF): 
        if f < int((T['ball1'] + 1.5) * FPS): pass
    return traj
BT = sim_ball()
# chiude la traiettoria: dopo ball1+1.5 resta fermo
last_f = int((T['ball1'] + 1.5) * FPS)
for f in range(NF):
    if f == 0 or BT[f].any() == 0: BT[f] = BT[f - 1] if f > 0 else np.array([-6.0, -1.5, float(H(-6.0, -1.5)) + BALL_R])
# riportiamo la palla a terra al termine (pavimento fuori campo)
BALL_FINAL = BT[last_f - 2].copy(); BALL_FINAL[2] = BALL_R
for f in range(last_f - 6, NF): BT[f] = BALL_FINAL
BALL = BT.copy()
# portata da Tumbo (41.0 -> 42.4) e posizione sul dischetto
def mouth(f):
    return np.array([TX_[f] + math.sin(TYAW[f]) * 0.55, TY_[f] - math.cos(TYAW[f]) * 0.55, 0.35])
for f in range(NF):
    t = tt[f]
    if T['dusk0'] + 0.5 <= t < 42.5:
        a = np.clip((t - 40.9) / 0.4, 0, 1)
        m = mouth(f); m[2] = Z_GRASS + 0.3
        BALL[f] = BALL_FINAL * (1 - a) + m * a
    elif 42.5 <= t < T['kick']:
        BALL[f] = np.array([0.0, 0.0, Z_GRASS + BALL_R])
    elif t >= T['kick']:
        u = (t - T['kick']) / 0.8
        if u < 1: BALL[f] = np.array([0 + 10.5 * u, 0.3 * u, Z_GRASS + BALL_R + 1.6 * u * (1 - u) * 2.0 + 0.5 * u])
        else:
            u2 = min(1.0, (t - T['kick'] - 0.8) / 0.9); BALL[f] = np.array([10.5 + 0.2 * u2, 0.3, max(Z_GRASS + BALL_R, 0.7 * (1 - u2) + Z_GRASS + BALL_R * u2)])
ballobj = ball_('Ball', BALL_R, (0, 0, 0), M['ball'], prc)
ballspin = ballobj
for f in range(NF):
    ballobj.location = tuple(BALL[f]); ballobj.keyframe_insert('location', frame=f + 1)
    sp = 0.0 if f == 0 else float(np.linalg.norm(BALL[f] - BALL[f - 1]))
    ballobj.rotation_euler = (f * 0.0 + sp * 0, 0, 0)
for f in range(1, NF, 2):
    ballobj.rotation_euler = (f * 0.35 if (T['ball0'] * FPS < f < last_f or f > T['kick'] * FPS) else 0.0, f * 0.2 if (T['ball0'] * FPS < f < last_f or f > T['kick'] * FPS) else 0.0, 0.0)
    ballobj.keyframe_insert('rotation_euler', frame=f + 1)
set_interp(ballobj, 'LINEAR')

# ======================= applica movimenti a Pippo e Tumbo =======================
def zg(x, y, t): return ground(x, y, t)
# finestre braccia di Pippo (nome, t0, t1)
ARM_WIN = [('push', 0.55, 2.0), ('cart', T['cart0'], T['cart1']), ('cheer', 5.7, 6.1), ('head', 6.4, 8.8), ('cheer', 11.8, 13.4), ('shield', 13.8, 15.4), ('down2', 16.2, 21.0),
           ('dig', 21.9, 23.3), ('push', 29.26, 30.2), ('cheer', 31.4, 32.8), ('wipe', 33.2, 36.0), ('point', 36.5, 39.0), ('cheer', 39.6, 40.6), ('cheer', 43.2, 45.1)]
def arm_vecs(name, t):
    if name == 'push': return (0.12, -1.0, -0.15), (-0.12, -1.0, -0.15)
    if name == 'cart': return (0.0, -0.83, -0.56), (0.0, -0.83, -0.56)
    if name == 'cheer': 
        w = math.sin(t * 9) * 0.15; return (-0.45, -0.1 + w, 1.0), (0.45, -0.1 - w, 1.0)
    if name == 'head': return (-0.5, -0.45, 0.8), (0.5, -0.45, 0.8)
    if name == 'shield': return (-0.5, -0.5, 0.75), (0.5, -0.5, 0.75)
    if name == 'down2': return (-0.45, -0.1, -1.0), (0.45, -0.1, -1.0)
    if name == 'dig':
        w = math.sin(t * 11); return (0.05, -0.8 - 0.2 * w, -0.5 + 0.3 * w), (-0.05, -0.8 - 0.2 * w, -0.5 + 0.3 * w)
    if name == 'wipe': return (-0.25, -0.1, -1.0), (0.2, -0.6 + 0.05 * math.sin(t * 6), 0.8)
    if name == 'point': return (-0.25, -0.1, -1.0), (0.25, -1.0, 0.1)
    return (-0.1, 0, -1.0), (0.1, 0, -1.0)
def arm_pose(t, phase, amp):
    """combina la posa di default (oscillazione con la camminata) con la finestra attiva"""
    base = ((-0.12, 0.0 + 0.5 * amp * math.sin(phase), -1.0), (0.12, 0.0 - 0.5 * amp * math.sin(phase), -1.0))
    wsum = 0.0; vl = np.zeros(3); vr = np.zeros(3)
    for (nm, t0, t1) in ARM_WIN:
        w = float(np.clip(min(t - t0, t1 - t) / 0.25, 0, 1))
        if w > 0:
            a, b = arm_vecs(nm, t); vl += w * np.array(a); vr += w * np.array(b); wsum += w
    wsum = min(wsum, 1.0)
    return (np.array(base[0]) * (1 - wsum) + vl, np.array(base[1]) * (1 - wsum) + vr)
phP = 0.0; phT = 0.0
for f in range(NF):
    t = tt[f]
    # Pippo
    x, y, yaw, sp = PX_[f], PY_[f], PYAW[f], PSP[f]
    P['root'].location = (x, y, zg(x, y, t)); P['root'].rotation_euler = (0, 0, yaw)
    P['root'].keyframe_insert('location', frame=f + 1); P['root'].keyframe_insert('rotation_euler', frame=f + 1)
    stride = min(1.2 + 0.12 * sp, 3.2); amp = min(sp / 4.0, 1.0) * 0.95
    if f > 0: phP += math.hypot(x - PX_[f - 1], y - PY_[f - 1]) / stride * math.pi
    amp = amp if sp > 0.3 else 0.0
    P['hipL'].rotation_euler = (amp * math.sin(phP), 0, 0); P['hipR'].rotation_euler = (-amp * math.sin(phP), 0, 0)
    P['hipL'].keyframe_insert('rotation_euler', frame=f + 1); P['hipR'].keyframe_insert('rotation_euler', frame=f + 1)
    vl, vr = arm_pose(t, phP + math.pi, amp)
    P['shoulderL'].rotation_quaternion = qdir(tuple(vl)); P['shoulderR'].rotation_quaternion = qdir(tuple(vr))
    P['shoulderL'].keyframe_insert('rotation_quaternion', frame=f + 1); P['shoulderR'].keyframe_insert('rotation_quaternion', frame=f + 1)
    # Tumbo
    x, y, yaw, sp = TX_[f], TY_[f], TYAW[f], TSP[f]
    pitch = 0.0; zextra = 0.0
    if T['seam0'] + 0.7 <= t < T['seam1'] + 0.9: u = (t - T['seam0'] - 0.7) / 1.1; pitch = 1.1 * math.sin(math.pi * min(u, 1)) ; zextra = 0.25 * math.sin(math.pi * min(u, 1))
    if T['heat0'] + 0.1 <= t < T['heat1'] - 0.4: zextra = abs(math.sin(t * 7.5)) * 0.45
    Tb['root'].location = (x, y, zg(x, y, t) + zextra); Tb['root'].rotation_euler = (pitch, 0, yaw)
    Tb['root'].keyframe_insert('location', frame=f + 1); Tb['root'].keyframe_insert('rotation_euler', frame=f + 1)
    stride = min(0.9 + 0.1 * sp, 2.4); amp = (min(sp / 3.0, 1.0) * 0.9 if sp > 0.3 else 0.0)
    if T['heat0'] + 0.1 <= t < T['heat1'] - 0.4: amp = 0.7; phT += 0.55
    if f > 0: phT += math.hypot(x - TX_[f - 1], y - TY_[f - 1]) / stride * math.pi
    for tag, sgn in (('FL', 1), ('BR', 1), ('FR', -1), ('BL', -1)):
        Tb['leg' + tag].rotation_euler = (sgn * amp * math.sin(phT), 0, 0); Tb['leg' + tag].keyframe_insert('rotation_euler', frame=f + 1)
    # calcio finale di Tumbo
    if T['kick'] - 0.12 < t < T['kick'] + 0.2:
        Tb['legFR'].rotation_euler = (-1.1 if t > T['kick'] - 0.03 else 0.7, 0, 0); Tb['legFR'].keyframe_insert('rotation_euler', frame=f + 1)
    Tb['tail'].rotation_euler = (-1.0, 0, 0.55 * math.sin(t * 9)); Tb['tail'].keyframe_insert('rotation_euler', frame=f + 1)
for ob in (P['root'], Tb['root']): set_interp(ob, 'LINEAR')
for nm in ('hipL', 'hipR', 'shoulderL', 'shoulderR'): set_interp(P[nm], 'LINEAR')
for tag in ('FL', 'BR', 'FR', 'BL'): set_interp(Tb['leg' + tag], 'LINEAR')

# espressioni
def pex(t, **k): pippo.express(P, fr(t), **k)
pex(0, brow=0.5, smile=0.4, eye_scale=1.05); pex(2.0, brow=0.3, smile=0.5); pex(5.6, brow=-0.4, brow_lift=1, smile=1.0, mouth_open=0.5, eye_scale=1.1)
pex(6.4, brow=0.9, smile=-0.3, mouth_open=0.3, eye_scale=1.15, look=(0.3, -0.2)); pex(8.7, brow=0.8, smile=-0.2, mouth_open=0.1)
pex(11.2, brow=0.2, smile=0.8); pex(12.8, brow=-0.5, brow_lift=1, smile=1.0, mouth_open=0.5); pex(14.0, brow=0.3, smile=0.0, look=(0, 0.6), eye_scale=1.1)
pex(16.5, brow=0.9, smile=-0.5, mouth_open=0.4, eye_scale=1.15, look=(0, -0.7)); pex(21.4, brow=0.7, smile=-0.2); pex(22.5, brow=-0.2, smile=0.7, mouth_open=0.3)
pex(24.7, brow=-0.5, brow_lift=1, smile=1.0, mouth_open=0.4); pex(27.6, brow=0.8, smile=-0.3, mouth_open=0.3, eye_scale=1.1); pex(30.0, brow=0.0, smile=0.8)
pex(32.0, brow=-0.5, brow_lift=1, smile=1.0, mouth_open=0.5); pex(34.0, brow=0.6, smile=-0.2, mouth_open=0.4, eye_scale=1.1); pex(38.0, brow=-0.3, smile=0.8)
pex(42.6, brow=-0.4, brow_lift=1, smile=1.0, mouth_open=0.4); pex(43.6, brow=-0.6, brow_lift=1.2, smile=1.0, mouth_open=1.0, eye_scale=1.1); pex(45.0, smile=1.0, mouth_open=0.5)
def tex(t, **k): tumbo.tumbo_express(Tb, fr(t), **k)
tex(0, tongue=0.0, brow=0.2); tex(2.0, tongue=0.5, brow=0.3, eye_scale=1.1); tex(6.2, tongue=0.8, brow=0.4, eye_scale=1.1); tex(8.7, tongue=0.4, brow=0.7, eye_scale=1.2)
tex(14.0, tongue=0.0, brow=0.7, eye_scale=1.15); tex(17.0, tongue=0.0, brow=0.9, eye_scale=1.2); tex(22.0, tongue=0.7, brow=0.3); tex(27.8, tongue=0.3, brow=0.8, eye_scale=1.2)
tex(29.6, tongue=0.8, brow=0.3); tex(33.5, tongue=1.0, brow=0.9, eye_scale=1.25); tex(37.0, tongue=0.8, brow=0.3); tex(43.6, tongue=1.0, brow=0.4); tex(45.0, tongue=1.0, brow=0.3)

# ======================= macchine =======================
def drive(root, x_from, x_to, t0, t1, y, z_fun=None, scale=None, wheels=None):
    for f in range(NF):
        t = tt[f]; u = float(np.clip((t - t0) / (t1 - t0), 0, 1)); x = x_from + (x_to - x_from) * u
        root.location = (x, y, z_fun(x, y, t) if z_fun else 0.0); root.keyframe_insert('location', frame=f + 1)
    set_interp(root, 'LINEAR')
for y in (-4.7, -1.6, 1.6, 4.7):
    d = props003.bulldozer(prc, M); d.scale = (1, 1.5, 1); drive(d, -14.5, 14.5, T['doze0'], T['doze1'], y, lambda x, yy, t: ground(x, yy, t) * 0 + (float(H(x, yy)) * (1 - flat_w(x, t)) if abs(x) < BX else 0.0))
    d.rotation_euler = (0, 0, 0)
for y in (-4.7, -1.6, 1.6, 4.7):
    r, drum, rear = props003.roller(prc, M); r.scale = (1, 2.0, 1); drive(r, -16.0, 16.0, T['roll0'], T['roll1'], y)
    for f in range(0, NF, 3):
        drum.rotation_euler = (math.pi / 2, f * 0.5, 0); drum.keyframe_insert('rotation_euler', frame=f + 1)
br = props003.brush_machine(prc, M); br.scale = (1, 3.6, 1); drive(br, -15.0, 15.0, T['inf0'], T['inf1'], 0.0, lambda x, y, t: Z_SYN)
cartroot, cwheels = props003.cart(prc, M)
for f in range(NF):
    t = tt[f]
    cs = None
    if T['cart0'] <= t <= T['cart1']:
        s = (t - T['cart0']) / (T['cart1'] - T['cart0']) * Ltot; i = int(np.clip(np.searchsorted(sarr, s), 1, len(crooked) - 1))
        p = crooked[i]; hd = tang[i]; cs = (p[0], p[1], yaw_dir(hd[0], hd[1]))
    elif t < T['cart0']: cs = (-10.0, -3.6, yaw_dir(0, -1))
    else: cs = (crooked[-1][0], crooked[-1][1], yaw_dir(0, -1))
    cartroot.location = (cs[0], cs[1], ground(cs[0], cs[1], t) if t < T['cart1'] else ground(cs[0], cs[1], t)); cartroot.rotation_euler = (0, 0, cs[2])
    cartroot.keyframe_insert('location', frame=f + 1); cartroot.keyframe_insert('rotation_euler', frame=f + 1)
set_interp(cartroot, 'LINEAR')
# il carrello e' parcheggiato accanto a Pippo; poi sparisce dopo l'uso: lo fa tornare nel parco
cartroot.hide_render = False; cartroot.keyframe_insert('hide_render', frame=1)

# ======================= giocatori (spettatori in divisa che entrano in campo) =======================
playersets = []
kits = [((0.88, 0.13, 0.13), (0.96, 0.96, 0.96)), ((0.15, 0.35, 0.88), (0.96, 0.96, 0.96))]
skins = [(0.95, 0.76, 0.62), (0.72, 0.5, 0.36), (0.55, 0.36, 0.24), (0.9, 0.7, 0.55)]
hairs = [(0.1, 0.07, 0.05), (0.35, 0.2, 0.08), (0.8, 0.65, 0.2), (0.05, 0.05, 0.06)]
sidewalk_y = BY + 1.7
spots = [(-6, -sidewalk_y), (-2, -sidewalk_y), (3, -sidewalk_y), (7, -sidewalk_y), (-7, sidewalk_y), (-3, sidewalk_y), (2, sidewalk_y), (6, sidewalk_y)]
field_pos = [(-7.5, -4.5), (-6.0, 3.8), (-7.5, 1.5), (-3.5, 4.6), (3.5, 4.2), (6.0, 3.5), (8.0, -4.2), (1.5, 5.0)]
for k in range(8):
    kit = kits[0 if k < 4 else 1]
    Pl = props003.player(chc, 'Pl%d' % k, kit[0], kit[1], skins[k % 4], hairs[(k + 1) % 4], scale=1.0)
    playersets.append(Pl)
    sx, sy = spots[k]; fx, fy = field_pos[k]
    ph = 0.0; lastyaw = yaw_dir(0, 1 if sy < 0 else -1)
    for f in range(NF):
        t = tt[f]
        u = float(np.clip((t - (T['play0'] + 0.08 * k)) / 1.9, 0, 1))
        x = sx + (fx - sx) * u; y = sy + (fy - sy) * u
        moving = 0 < u < 1
        yaw = yaw_dir(fx - sx, fy - sy) if moving else (yaw_dir(0 - x, 0 - y) if u >= 1 else lastyaw)
        if u >= 1: lastyaw = yaw
        Pl['root'].location = (x, y, ground(x, y, t) if abs(x) < BX and abs(y) < BY else 0.0); Pl['root'].rotation_euler = (0, 0, yaw)
        Pl['root'].keyframe_insert('location', frame=f + 1); Pl['root'].keyframe_insert('rotation_euler', frame=f + 1)
        dist = math.hypot(fx - sx, fy - sy) / 1.9
        if moving: ph += dist / 1.1 / FPS * math.pi
        amp = 0.9 if moving else 0.0
        Pl['hipL'].rotation_euler = (amp * math.sin(ph), 0, 0); Pl['hipR'].rotation_euler = (-amp * math.sin(ph), 0, 0)
        Pl['hipL'].keyframe_insert('rotation_euler', frame=f + 1); Pl['hipR'].keyframe_insert('rotation_euler', frame=f + 1)
        cheer = t > T['kick'] + 0.7; hands = 16.2 < t < 21.0
        for nm, sg in (('L', -1), ('R', 1)):
            sh = Pl['shoulder' + nm]
            if cheer: sh.rotation_euler = (math.pi * 0.95 + 0.25 * math.sin(t * 9 + k), sg * 0.3, 0)
            elif hands: sh.rotation_euler = (math.pi * 0.8, sg * 0.3, 0)
            else: sh.rotation_euler = (-amp * 0.5 * math.sin(ph) * sg, sg * 0.08, 0)
            sh.keyframe_insert('rotation_euler', frame=f + 1)
        if cheer: Pl['root'].location = (x, y, ground(x, y, t) + abs(math.sin(t * 7 + k)) * 0.35); Pl['root'].keyframe_insert('location', frame=f + 1)
    set_interp(Pl['root'], 'LINEAR')
    for nm in ('hipL', 'hipR', 'shoulderL', 'shoulderR'): set_interp(Pl[nm], 'LINEAR')

# ======================= camere =======================
def smooth(a, n):
    k = np.ones(n) / n; pad = n // 2
    ap = np.pad(a, ((pad, pad), (0, 0)), mode='edge')
    return np.stack([np.convolve(ap[:, i], k, mode='valid')[:len(a)] for i in range(a.shape[1])], 1)
PP = np.stack([PX_, PY_, np.zeros(NF)], 1); TT_ = np.stack([TX_, TY_, np.zeros(NF)], 1)
PPs = smooth(PP, 25); TTs = smooth(TT_, 25); BALLs = smooth(BALL, 29)
def V(*a): return np.array(a, float)
def L(a, b, u): return np.array(a, float) * (1 - u) + np.array(b, float) * u
def sh(t0, t1, fn): return (t0, t1, fn)
def doz_x(t): return -14.5 + 29.0 * float(np.clip((t - T['doze0']) / (T['doze1'] - T['doze0']), 0, 1))
def rol_x(t): return -16.0 + 32.0 * float(np.clip((t - T['roll0']) / (T['roll1'] - T['roll0']), 0, 1))
def _fwd(YAW): return np.stack([np.sin(YAW), -np.cos(YAW)], 1)
FWP = smooth(_fwd(PYAW), 37); FWT = smooth(_fwd(TYAW), 37)
FWP /= np.linalg.norm(FWP, axis=1, keepdims=True) + 1e-9; FWT /= np.linalg.norm(FWT, axis=1, keepdims=True) + 1e-9
def hero(t0, t1, who, d0, d1, e, z0, z1, tz, lens, front=1.0):
    base = PPs if who == 'P' else TTs; fw = FWP if who == 'P' else FWT
    fa, fb = fr(t0) - 1, min(fr(t1) - 1, NF - 1); fm = (fa + fb) // 2
    def cand(f, fr_, sg, d):
        sd = np.array([-fw[f][1], fw[f][0]])
        return base[f][:2] + fw[f] * d * fr_ + sd * e * sg
    def okp(c): return c[1] < 5.8 and c[1] > -9.5 and abs(c[0]) < 16.5
    choice = None
    for fr_, sg in ((front, 1), (front, -1), (-front, 1), (-front, -1)):
        if all(okp(cand(f, fr_, sg, d0)) for f in (fa, fm, fb)): choice = (fr_, sg); break
    if choice is None: choice = (front, 1)
    def fn(f, t, u):
        d = d0 + (d1 - d0) * u; c = cand(f, choice[0], choice[1], d)
        c = np.array([np.clip(c[0], -16.5, 16.5), np.clip(c[1], -9.5, 5.8)]); z = z0 + (z1 - z0) * u
        return V(c[0], c[1], z), base[f] + V(0, 0, tz), lens
    return sh(t0, t1, fn)
SHOTS = [
    hero(0, 1.5, 'P', 4.5, 3.5, 1.2, 1.4, 1.3, 1.1, 35),
    hero(1.5, 2.4, 'T', 2.6, 2.2, 0.8, 0.6, 0.6, 0.4, 35),
    hero(2.4, 4.0, 'P', 4.2, 4.2, 1.5, 1.2, 1.2, 1.0, 32),
    sh(4.0, 5.6, lambda f, t, u: (PPs[f] + V(-5, -7, 7), PPs[f] + V(2, 3, 0), 32)),
    hero(5.6, 6.4, 'P', 2.6, 2.3, 0.5, 1.5, 1.5, 1.5, 40),
    sh(6.4, 7.6, lambda f, t, u: (BALLs[f] + V(5, -6, 2.5), BALLs[f], 32)),
    hero(7.6, 8.9, 'T', 3.0, 3.0, 1.2, 0.7, 0.7, 0.4, 35),
    sh(8.9, 10.6, lambda f, t, u: (V(PPs[f][0] - 1.2, PPs[f][1] - 2.0, 1.8), V(doz_x(t), PPs[f][1] * 0.3, 0.9), 30)),
    sh(10.6, 12.3, lambda f, t, u: (L((0, -8, 9), (0, -9, 8), u) + V(rol_x(t) * 0.3, 0, 0), V(rol_x(t), 0, 0), 32)),
    hero(12.3, 13.6, 'P', 3.4, 3.4, 1.0, 1.3, 1.3, 1.2, 35),
    hero(13.6, 15.0, 'P', 5.0, 5.0, 0.8, 0.8, 0.8, 1.8, 30),
    hero(15.0, 16.8, 'T', 2.4, 2.4, 0.8, 0.5, 0.5, 0.4, 35),
    hero(16.8, 19.0, 'P', 3.8, 3.8, 1.2, 0.7, 0.9, 1.1, 32),
    sh(19.0, 21.7, lambda f, t, u: (L((-12, -12, 9), (-8, -13, 8.5), u), V(0, 0, 0), 30)),
    hero(21.7, 23.3, 'P', 3.6, 3.6, 1.5, 1.1, 1.1, 0.9, 35),
    hero(23.3, 24.3, 'T', 3.0, 3.0, 1.0, 0.8, 0.8, 0.4, 35),
    hero(24.3, 25.1, 'P', 3.2, 3.2, 1.0, 1.3, 1.3, 1.3, 38),
    sh(25.1, 27.2, lambda f, t, u: (L((-12, -5.8, 1.0), (-3, -5.8, 1.2), u), L((-4, 0, 0.2), (6, 0, 0.2), u), 30)),
    hero(27.2, 29.2, 'T', 2.8, 2.8, 1.2, 0.7, 0.7, 0.4, 35),
    hero(29.2, 30.2, 'P', 3.6, 3.6, 1.5, 1.1, 1.1, 1.0, 35),
    hero(30.2, 31.3, 'P', 4.0, 4.0, 2.0, 1.6, 1.6, 1.0, 32),
    hero(31.3, 32.8, 'P', 3.4, 3.4, 0.8, 1.3, 1.3, 1.3, 38),
    hero(32.8, 34.6, 'T', 2.2, 2.2, 0.6, 0.5, 0.5, 0.35, 35),
    hero(34.6, 36.3, 'P', 3.2, 3.2, 0.8, 1.4, 1.4, 1.3, 38),
    hero(36.3, 38.3, 'P', 3.8, 3.8, 1.6, 1.2, 1.2, 1.1, 32),
    sh(38.3, 40.4, lambda f, t, u: (L((-14, -12, 8), (0, -13, 8.5), u), L((-4, 0, 0), (4, 0, 0), u), 30)),
    hero(40.4, 41.8, 'T', 3.2, 3.2, 1.2, 0.8, 0.8, 0.4, 35),
    sh(41.8, 43.25, lambda f, t, u: (V(-0.5, -3.8, 0.9), V(0, 0, 0.5), 35)),
    sh(43.25, 44.1, lambda f, t, u: (V(BALL[f][0] - 3.5, -5.5, 1.3), BALL[f] + V(1.0, 0, 0.3), 28)),
    hero(44.1, 46.0, 'P', 4.8, 4.8, 1.5, 1.2, 1.2, 1.0, 32),
]
cam = camera('Cam', Vector((0, -10, 5)), Vector((0, 0, 0)), 30, scene.collection)
tgt = bpy.data.objects.new('CamTarget', None); scene.collection.objects.link(tgt)
tc = cam.constraints.new('TRACK_TO'); tc.target = tgt; tc.track_axis = 'TRACK_NEGATIVE_Z'; tc.up_axis = 'UP_Y'
scene.camera = cam
for f in range(NF):
    t = tt[f]
    s = next((s for s in SHOTS if s[0] <= t < s[1]), SHOTS[-1])
    u = (t - s[0]) / (s[1] - s[0])
    pos, tg, lens = s[2](f, t, u)
    cam.location = tuple(pos); tgt.location = tuple(tg); cam.data.lens = lens
    cam.keyframe_insert('location', frame=f + 1); tgt.keyframe_insert('location', frame=f + 1); cam.data.keyframe_insert('lens', frame=f + 1)
for ob in (cam, tgt, cam.data): set_interp(ob, 'LINEAR')


# ---- pulizia: alberi lato camera, giocatori prima dell'ingresso, nastri/linee dopo il sintetico
def desc(o):
    for c in o.children:
        yield c
        yield from desc(c)
def hide_perm(o):
    for q in [o] + list(desc(o)): q.hide_render = True
for o in list(bpy.data.objects):
    if o.name.startswith('Tree') and o.parent is None and o.location.y < -3: hide_perm(o)
def hide_from_to(o, fa, fb=None):
    for q in [o] + list(desc(o)):
        if getattr(q, 'type', '') in ('EMPTY', 'MESH'):
            q.hide_render = False; q.keyframe_insert('hide_render', frame=1)
            q.hide_render = True; q.keyframe_insert('hide_render', frame=fa)
            if fb: q.hide_render = False; q.keyframe_insert('hide_render', frame=fb)
for o in list(bpy.data.objects):
    if o.name.startswith('Seam') and o.type == 'MESH': hide_from_to(o, fr(T['up0']))
for o in L3: hide_from_to(o, fr(T['up0']))
for Pl in playersets:
    for q in [Pl['root']] + list(desc(Pl['root'])):
        q.hide_render = True; q.keyframe_insert('hide_render', frame=1)
        q.hide_render = False; q.keyframe_insert('hide_render', frame=fr(T['play0'] - 0.1))

os.makedirs('../t003', exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath('../t003/pippo_t003.blend'))
print('SAVED')
