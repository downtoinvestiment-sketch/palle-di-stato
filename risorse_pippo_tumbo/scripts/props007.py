"""Test 007 - oggetti: nano da giardino, cuore, staccionata a piani, merli, scale, tappeto elastico, catapulta, palloncini, cartelli."""
import bpy, bmesh, math, numpy as np
from mathutils import Matrix, Vector
from common import *
import set004, props004
from set004 import MB, obj, cyl, ball_


def mats007():
    M = {}
    c = lambda n, col, **k: material(n, col, **k)
    M['hat'] = [c('N_hat%d' % i, col, rough=0.45, spec=0.5) for i, col in enumerate([(0.92, 0.08, 0.08), (0.10, 0.60, 0.20), (0.10, 0.35, 0.95)])]
    M['skin'] = c('N_skin', (0.98, 0.76, 0.62), rough=0.6); M['beard'] = c('N_beard', (0.97, 0.97, 0.95), rough=0.8)
    M['coat'] = [c('N_coat%d' % i, col, rough=0.5) for i, col in enumerate([(0.10, 0.35, 0.90), (0.92, 0.55, 0.08), (0.55, 0.20, 0.75)])]
    M['boot'] = c('N_boot', (0.10, 0.08, 0.07), rough=0.5); M['nose'] = c('N_nose', (0.95, 0.52, 0.45), rough=0.5)
    M['heart'] = c('N_heart', (1.0, 0.10, 0.25), rough=0.4, emit=(1.0, 0.05, 0.2), emit_strength=1.2)
    M['spark'] = c('N_spark', (1.0, 0.9, 0.3), rough=0.4, emit=(1.0, 0.85, 0.2), emit_strength=4.0)
    M['plank'] = [c('N_plank%d' % i, col, rough=0.85) for i, col in enumerate([(0.74, 0.50, 0.26), (0.62, 0.40, 0.20), (0.82, 0.60, 0.34), (0.52, 0.33, 0.17)])]
    M['stonew'] = c('N_stonew', (0.70, 0.68, 0.64), rough=0.9); M['stoned'] = c('N_stoned', (0.52, 0.50, 0.48), rough=0.9)
    M['pagoda'] = c('N_pagoda', (0.80, 0.12, 0.10), rough=0.5); M['flag'] = c('N_flag', (1.0, 0.85, 0.05), rough=0.6)
    M['metal'] = c('N_metal', (0.75, 0.78, 0.82), rough=0.3, metallic=0.8); M['blue'] = c('N_blue', (0.10, 0.35, 0.95), rough=0.4)
    M['black'] = c('N_black', (0.04, 0.04, 0.05), rough=0.7); M['white'] = c('N_white', (0.98, 0.98, 0.98), rough=0.7)
    M['goo'] = c('N_goo', (0.36, 0.22, 0.08), rough=0.35, spec=0.6); M['stink'] = c('N_stink', (0.45, 0.75, 0.15), rough=1.0, emit=(0.4, 0.7, 0.1), emit_strength=0.6)
    M['dirt'] = c('N_dirt', (0.42, 0.27, 0.13), rough=1.0); M['rope'] = c('N_rope', (0.80, 0.68, 0.45), rough=0.9)
    M['bal'] = [c('N_bal%d' % i, col, rough=0.2, spec=0.9) for i, col in enumerate([(1.0, 0.15, 0.2), (1.0, 0.8, 0.05), (0.1, 0.5, 1.0), (0.2, 0.85, 0.3), (0.95, 0.4, 0.9), (1.0, 0.5, 0.05)])]
    M['bubble'] = c('N_bubble', (1, 1, 1), rough=1.0, emit=(1, 1, 1), emit_strength=0.5)
    M['bag'] = c('N_bag', (0.55, 0.12, 0.45), rough=0.5)
    return M


def _bm_obj(name, bm, mats, coll, smooth=True):
    for f in bm.faces: f.smooth = smooth
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for m in mats: me.materials.append(m)
    return me

def _sph(bm, c, r, sc=(1, 1, 1), mi=0, seg=16, rings=10):
    old = set(bm.faces)
    bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=rings, radius=1.0, matrix=Matrix.Translation(c) @ Matrix.Diagonal((r * sc[0], r * sc[1], r * sc[2], 1)))
    for f in bm.faces:
        if f not in old: f.material_index = mi

def _cone(bm, c, r1, r2, h, mi=0, seg=16, rot=None):
    old = set(bm.faces); m = Matrix.Translation(c)
    if rot is not None: m = m @ rot
    bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r1, radius2=r2, depth=h, matrix=m)
    for f in bm.faces:
        if f not in old: f.material_index = mi

def gnome_mesh(M, hat=0, coat=0):
    """nano da giardino alto ~0.8, rivolto a -Y, origine ai piedi."""
    bm = bmesh.new()
    for s in (-1, 1): _sph(bm, (s * 0.075, -0.03, 0.05), 0.075, (1, 1.4, 0.75), 4)
    _sph(bm, (0, 0, 0.26), 0.18, (1, 0.95, 1.2), 3)
    _sph(bm, (0, 0, 0.26), 0.185, (1.02, 0.97, 0.18), 4)                 # cintura
    _sph(bm, (0, -0.015, 0.50), 0.13, (1, 1, 1), 1)
    _sph(bm, (0, -0.075, 0.42), 0.125, (1.0, 0.65, 1.25), 2)             # barba
    _sph(bm, (0, -0.14, 0.50), 0.04, (1, 1, 1), 5)
    for s in (-1, 1): _sph(bm, (s * 0.05, -0.118, 0.535), 0.02, (1, 1, 1), 4, 8, 6)
    _cone(bm, (0, 0.0, 0.74), 0.15, 0.012, 0.42, 0)
    for s in (-1, 1): _sph(bm, (s * 0.19, -0.03, 0.27), 0.055, (0.8, 0.8, 1.6), 3)
    return _bm_obj('NanoMesh%d%d' % (hat, coat), bm, [M['hat'][hat], M['skin'], M['beard'], M['coat'][coat], M['boot'], M['nose']], None)

def heart_mesh(M):
    bm = bmesh.new()
    for s in (-1, 1): _sph(bm, (s * 0.48, 0, 0.30), 0.62, (1, 0.55, 1), 0)
    _cone(bm, (0, 0, -0.42), 0.0, 1.06, 1.35, 0, 20)
    for v in bm.verts:
        if v.co.z < 0.25: v.co.y *= 0.55
    return _bm_obj('CuoreMesh', bm, [M['heart']], None)


def fence_tier(coll, M, x0, x1, h, seed, name='Staccionata', axis='x'):
    """un piano di staccionata di assi (lungo X, spessore su Y), origine alla base. Assi storte e di colori diversi."""
    r = np.random.default_rng(seed); mb = MB(M['plank'] + [M['metal']])
    x = x0
    while x < x1:
        w = r.uniform(0.24, 0.32); hh = h + r.uniform(-0.05, 0.12)
        mb.box((x + w / 2, 0, hh / 2), (w - 0.02, 0.06, hh), int(r.integers(0, 4)), rz=0.0)
        if r.random() < 0.5: mb.box((x + w / 2, -0.035, hh * r.uniform(0.2, 0.9)), (0.035, 0.02, 0.035), 4)       # chiodi
        x += w
    for z in (0.25 * h, 0.80 * h): mb.box(((x0 + x1) / 2, 0.05, z), (x1 - x0, 0.05, 0.14), 3)
    return mb.build(name, coll)

def battlements(coll, M, x0, x1, z):
    """merli di pietra, due torrette a pagoda e bandiera: la 'muraglia cinese'. Restituisce [oggetti] (origine a quota z)."""
    mb = MB([M['stonew'], M['stoned']])
    mb.box(((x0 + x1) / 2, 0, 0.4), (x1 - x0, 0.7, 0.8), 0)
    for k, x in enumerate(np.arange(x0 + 0.4, x1, 1.3)): mb.box((x, 0, 1.1), (0.7, 0.72, 0.6), k % 2)
    for z_ in (0.25, 0.55): mb.box(((x0 + x1) / 2, -0.36, z_), (x1 - x0, 0.02, 0.03), 1)
    wall = mb.build('Merli', coll); wall.location = (0, 0, z)
    outs = [wall]
    for xc in (x0 + 2.2, x1 - 2.2):
        tb = MB([M['stonew'], M['stoned'], M['pagoda'], M['flag'], M['black']])
        tb.box((0, 0, 1.3), (1.9, 1.5, 2.6), 0); tb.box((0, -0.76, 1.5), (0.5, 0.04, 0.8), 4)
        for k, (w_, z_) in enumerate(((2.9, 2.75), (2.2, 3.15), (1.3, 3.5))): tb.box((0, 0, z_), (w_, w_ * 0.8, 0.22), 2)
        tb.box((0, 0, 4.3), (0.06, 0.06, 1.6), 4); tb.box((0.38, 0, 4.8), (0.7, 0.03, 0.45), 3)
        t = tb.build('Torretta', coll); t.location = (xc, 0, z); outs.append(t)
    return outs


def ladder(coll, M, L, name='Scala'):
    mb = MB([M['plank'][2], M['plank'][1]])
    for s in (-1, 1): mb.box((s * 0.26, 0, L / 2), (0.07, 0.06, L), 0)
    for z in np.arange(0.3, L - 0.1, 0.32): mb.box((0, 0, z), (0.52, 0.05, 0.05), 1)
    return mb.build(name, coll)


def trampoline(coll, M, R=1.45, H=0.9):
    """restituisce (root, telo, telo strappato)."""
    root = empty('Tappeto', (0, 0, 0), None, coll)
    mb = MB([M['blue'], M['metal'], M['white']])
    n = 18
    for k in range(n):
        a = 2 * math.pi * (k + 0.5) / n; mb.box((R * math.sin(a), -R * math.cos(a), H), (2 * math.pi * R / n * 1.04, 0.22, 0.10), 0, rz=a)
        if k % 3 == 0: mb.box((R * math.sin(a), -R * math.cos(a), H / 2), (0.07, 0.07, H), 1)
    for k in range(24):
        a = 2 * math.pi * k / 24; mb.box((1.27 * math.sin(a), -1.27 * math.cos(a), H), (0.03, 0.16, 0.03), 2, rz=a)
    fr_ = mb.build('TappetoTelaio', coll); fr_.parent = root
    mat = cyl('TappetoTelo', 1.22, 0.025, (0, 0, H), M['black'], coll, parent=root)
    tb = MB([M['black']])
    for k in range(9):
        a = 2 * math.pi * k / 9; tb.box((0.86 * math.sin(a), -0.86 * math.cos(a), H - 0.2), (0.82, 0.78, 0.02), 0, rx=0.55, rz=a)
    torn = tb.build('TappetoStrappato', coll); torn.parent = root
    return root, mat, torn


def catapult(coll, M):
    """catapulta di legno: avanti = -Y. Restituisce (root, braccio); il braccio ruota su X attorno al perno (0,0,1.45), punta a +Y lunga 2.6."""
    root = empty('Catapulta', (0, 0, 0), None, coll)
    mb = MB([M['plank'][0], M['plank'][3], M['metal'], M['rope']])
    for s in (-1, 1):
        mb.box((s * 0.7, 0, 0.14), (0.20, 3.2, 0.20), 0); mb.box((s * 0.7, -0.2, 0.85), (0.18, 0.18, 1.5), 1)
        mb.box((s * 0.7, 0.45, 0.75), (0.12, 0.12, 1.6), 0, rx=-0.75)
        for y in (-1.2, 1.2): mb.box((s * 0.82, y, 0.22), (0.10, 0.44, 0.44), 1)
    for y in (-1.5, 1.5): mb.box((0, y, 0.14), (1.6, 0.18, 0.18), 1)
    mb.box((0, -0.2, 1.45), (1.7, 0.10, 0.10), 2); mb.box((0, -0.55, 1.75), (1.5, 0.16, 0.16), 1)
    o = mb.build('CatapultaTelaio', coll); o.parent = root
    am = MB([M['plank'][2], M['stoned'], M['plank'][3]])
    am.box((0, 1.1, 0), (0.16, 3.0, 0.14), 0); am.box((0, -0.45, -0.1), (0.5, 0.5, 0.5), 1)
    am.box((0, 2.6, 0.02), (0.75, 0.75, 0.06), 2)
    for s in (-1, 1): am.box((s * 0.37, 2.6, 0.12), (0.05, 0.75, 0.2), 2); am.box((0, 2.6 + s * 0.37, 0.12), (0.75, 0.05, 0.2), 2)
    arm = am.build('CatapultaBraccio', coll); arm.parent = root; arm.location = (0, -0.2, 1.45)
    return root, arm


def balloons(coll, M, parent, loc, n=7, seed=2):
    """mazzo di palloncini: restituisce (root, [palloncini])."""
    r = np.random.default_rng(seed); root = empty('Palloncini', loc, parent, coll); outs = []
    sm_ = MB([M['white']])
    for k in range(n):
        a = 2 * math.pi * k / n; rad = 0.45 if k else 0.0
        p = (rad * math.cos(a) + r.uniform(-0.08, 0.08), rad * math.sin(a) * 0.7, 1.5 + (0.45 if k == 0 else r.uniform(-0.15, 0.2)))
        b = ball_('Palloncino', 0.30, p, M['bal'][k % 6], coll, parent=root, sc=(1, 1, 1.2)); outs.append(b)
        L = math.sqrt(p[0] ** 2 + p[1] ** 2 + (p[2] - 0.3) ** 2); v = (p[0] / L, p[1] / L, (p[2] - 0.3) / L)
        sm_.box((p[0] / 2, p[1] / 2, (p[2] - 0.3) / 2), (0.012, 0.012, L), 0, rx=math.acos(v[2]), rz=math.atan2(v[0], -v[1]))
    st = sm_.build('PalloncinoFili', coll); st.parent = root
    return root, outs, st


def text_obj(coll, name, body, size, mat, loc, rot=(math.pi / 2, 0, 0), parent=None):
    cu = bpy.data.curves.new(name, 'FONT'); cu.body = body; cu.size = size; cu.align_x = 'CENTER'; cu.align_y = 'CENTER'; cu.extrude = 0.004
    o = bpy.data.objects.new(name, cu); o.location = loc; o.rotation_euler = rot; o.parent = parent; coll.objects.link(o)
    cu.materials.append(mat); return o

def sign(coll, M, body, w=1.2, h=0.34, size=0.17, post=0.9):
    """cartello di legno su paletto, scritta verso -Y. Origine a terra."""
    root = empty('Cartello', (0, 0, 0), None, coll)
    mb = MB([M['plank'][2], M['plank'][3]])
    mb.box((0, 0.03, post / 2), (0.07, 0.05, post), 1); mb.box((0, 0, post + h / 2 - 0.05), (w, 0.05, h), 0)
    o = mb.build('CartelloLegno', coll); o.parent = root
    text_obj(coll, 'CartelloTesto', body, size, M['black'], (0, -0.032, post + h / 2 - 0.05), parent=root)
    return root
