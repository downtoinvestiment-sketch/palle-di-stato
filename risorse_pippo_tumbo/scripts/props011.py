"""Test 011 - PIPPO E IL TORNADO: il Tornado (personaggio), macerie, cappello volante."""
import math, bpy, numpy as np
from common import material, shape, empty, shared_mesh
import set004
from set004 import MB, obj, cyl, ball_
PI = math.pi

def mats011():
    c = lambda n, col, **k: material('T11_' + n, col, **k); M = {}
    M['body'] = [c('body%d' % i, (0.42 + 0.035 * i, 0.46 + 0.035 * i, 0.56 + 0.035 * i), rough=0.9) for i in range(9)]
    M['streak'] = c('streak', (0.93, 0.95, 1.0), rough=0.9, emit=(1, 1, 1), emit_strength=0.25)
    M['white'] = c('white', (1, 1, 1), rough=0.4, emit=(1, 1, 1), emit_strength=0.3); M['black'] = c('black', (0.02, 0.02, 0.03), rough=0.4)
    M['mouth'] = c('mouth', (0.25, 0.03, 0.05), rough=0.5); M['tongue'] = c('tongue', (1.0, 0.30, 0.45), rough=0.4)
    M['steel'] = c('steel', (0.72, 0.75, 0.80), rough=0.3, metallic=0.8); M['crack'] = c('crack', (0.05, 0.04, 0.03), rough=1.0)
    M['paper'] = c('paper', (0.98, 0.98, 0.96), rough=0.8); M['cap'] = c('cap', (0.05, 0.12, 0.40), rough=0.6); M['hairc'] = c('hairc', (0.15, 0.10, 0.06), rough=0.9)
    return M

NR = 9
def ring_r(k): return 0.38 + 0.30 * k
def ring_z(k): return 0.35 + 0.74 * k
def tornado(coll, M):
    """Tornado: 9 anelli che ondeggiano, faccia sull'anello 4, braccine con manette. Origine a terra (punta)."""
    T = {}; r = T['root'] = empty('Tornado', (0, 0, 0), None, coll); T['rings'] = []; T['spin'] = []
    for k in range(NR):
        e = empty('TornAnello%d' % k, (0, 0, ring_z(k)), r, coll); rr = ring_r(k)
        ball_('TornCorpo', 1.0, (0, 0, 0), M['body'][k], coll, parent=e, sc=(rr, rr, 0.52))
        s = empty('TornGiro%d' % k, (0, 0, 0), e, coll)
        for j in range(3):
            a = 2 * PI * j / 3 + k; ball_('TornStriscia', 1.0, (rr * 0.93 * math.cos(a), rr * 0.93 * math.sin(a), 0.05), M['streak'], coll, parent=s, sc=(0.10 + 0.05 * rr, 0.10 + 0.05 * rr, 0.07)).rotation_euler = (0, 0, a + PI / 2)
        T['rings'].append(e); T['spin'].append(s)
    for o in [c for s in T['spin'] for c in s.children]: o.scale = (o.scale[0] * 3.2, o.scale[1], o.scale[2])
    f = T['face'] = empty('TornFaccia', (0, 0, 0.1), T['rings'][4], coll); R = ring_r(4); fy = -R * 0.93
    for sx, nm in ((-1, 'L'), (1, 'R')):
        T['eye' + nm] = ball_('TornOcchio', 1.0, (sx * 0.42, fy, 0.25), M['white'], coll, parent=f, sc=(0.27, 0.12, 0.32))
        T['pupil' + nm] = ball_('TornPupilla', 1.0, (sx * 0.42, fy - 0.10, 0.23), M['black'], coll, parent=f, sc=(0.12, 0.06, 0.15))
        T['brow' + nm] = obj('TornSopr', set004.box_c(), (sx * 0.42, fy - 0.08, 0.68), (0.55, 0.08, 0.12), M['black'], coll, parent=f)
        sh = T['shoulder' + nm] = empty('TornSpalla' + nm, (sx * R * 0.95, -0.35, -0.45), f, coll); sh.rotation_mode = 'QUATERNION'
        cyl('TornBraccio', 0.09, 0.8, (0, 0, -0.4), M['body'][2], coll, parent=sh); ball_('TornMano', 0.18, (0, 0, -0.88), M['body'][6], coll, parent=sh)
    T['mouth'] = ball_('TornBocca', 1.0, (0, fy - 0.02, -0.38), M['mouth'], coll, parent=f, sc=(0.35, 0.08, 0.1))
    T['tongue'] = ball_('TornLingua', 1.0, (0, fy - 0.12, -0.58), M['tongue'], coll, parent=f, sc=(0.001, 0.001, 0.001))
    c = T['cuffs'] = empty('TornManette', (0, fy - 0.75, -0.95), f, coll)
    for sx in (-1, 1): cyl('Anello', 0.24, 0.10, (sx * 0.27, 0, 0), M['steel'], coll, rot=(PI / 2, 0, 0), parent=c)
    obj('Catena', set004.box_c(), (0, 0, 0), (0.26, 0.06, 0.06), M['steel'], coll, parent=c)
    return T

def tornex(T, f, brow=0.6, mouth=0.3, tongue=0.0, look=(0, 0), eye=1.0):
    R = ring_r(4); fy = -R * 0.93
    for sx, nm in ((-1, 'L'), (1, 'R')):
        b = T['brow' + nm]; b.rotation_euler = (0, -sx * brow * 0.5, 0); b.location = (sx * 0.42, fy - 0.08, 0.68 + 0.1 * (eye - 1) - 0.08 * abs(brow))
        b.keyframe_insert('rotation_euler', frame=f); b.keyframe_insert('location', frame=f)
        p = T['pupil' + nm]; p.location = (sx * 0.42 + look[0] * 0.1, fy - 0.10, 0.23 + look[1] * 0.12); p.keyframe_insert('location', frame=f)
        e = T['eye' + nm]; e.scale = (0.27 * eye, 0.12, 0.32 * eye); e.keyframe_insert('scale', frame=f)
    m = T['mouth']; m.scale = (0.35 + 0.1 * mouth, 0.08, 0.08 + 0.38 * mouth); m.keyframe_insert('scale', frame=f)
    t = T['tongue']; t.scale = (0.001,) * 3 if tongue <= 0.01 else (0.2, 0.08, 0.14 + 0.28 * tongue); t.keyframe_insert('scale', frame=f)

def rubble(coll, mats, w=6.5, d=4.5, n=46, seed=2):
    """macerie: scatole sparse (materiali della casa). Origine al centro a terra."""
    rg = np.random.default_rng(seed); mb = MB(mats)
    for k in range(n):
        s = rg.uniform(0.3, 0.9); x = rg.uniform(-w / 2, w / 2); y = rg.uniform(-d / 2, d / 2)
        mb.box((x, y, s * 0.3 * rg.uniform(0.6, 1.6)), (s * rg.uniform(0.6, 1.8), s, s * rg.uniform(0.3, 0.9)), int(rg.integers(0, len(mats))), rx=rg.uniform(-0.4, 0.4), rz=rg.uniform(0, 3))
    mb.box((-w * 0.3, -d * 0.2, 0.9), (0.35, 0.35, 1.8), 0, rx=0.2); mb.box((w * 0.33, d * 0.1, 0.6), (0.3, 0.3, 1.2), 0, rx=-0.3)
    return mb.build('Macerie', coll)

def fly_cap(coll, M):
    g = empty('CappelloVolante', (0, 0, -50), None, coll)
    cyl('CvCalotta', 0.29, 0.14, (0, 0, 0), M['cap'], coll, parent=g); obj('CvVisiera', set004.box_c(), (0, -0.30, -0.06), (0.40, 0.22, 0.03), M['black'], coll, parent=g)
    return g

def crack(coll, M, L=9.0, seed=4):
    rg = np.random.default_rng(seed); mb = MB([M['crack']]); x = -L / 2; y = 0.0
    while x < L / 2:
        dx = rg.uniform(0.5, 0.9); dy = rg.uniform(-0.5, 0.5); a = math.atan2(dy, dx); l = math.hypot(dx, dy)
        mb.box((x + dx / 2, y + dy / 2, 0.012), (l + 0.1, rg.uniform(0.12, 0.3), 0.02), 0, rz=a); x += dx; y += dy
    return mb.build('Crepa', coll)
