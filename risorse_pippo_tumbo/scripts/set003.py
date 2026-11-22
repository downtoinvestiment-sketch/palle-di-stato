"""Ambiente Test 003: città, letto del campo con 4 stati, porte, attrezzi."""
import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
import bpy, bmesh, numpy as np
from mathutils import Vector
from common import *
from params003 import *

_c = {}
def box0():
    """cubo unitario con origine nell'angolo minimo (scalare = crescere da quell'angolo)."""
    if 'b0' in _c: return _c['b0']
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts: v.co += Vector((.5, .5, .5))
    me = bpy.data.meshes.new('unit_box0'); bm.to_mesh(me); bm.free(); me.materials.append(None); _c['b0'] = me; return me
def box_c():
    if 'bc' in _c: return _c['bc']
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    me = bpy.data.meshes.new('unit_boxc'); bm.to_mesh(me); bm.free(); me.materials.append(None); _c['bc'] = me; return me
def prism():
    """prisma triangolare (tetto a capanna): base 1x1 in xy, colmo lungo y a z=0.5 (centrato in z da -0.5 a 0.5)"""
    if 'pr' in _c: return _c['pr']
    bm = bmesh.new()
    v = [bm.verts.new(p) for p in [(-.5, -.5, -.5), (.5, -.5, -.5), (.5, .5, -.5), (-.5, .5, -.5), (0, -.5, .5), (0, .5, .5)]]
    for f in [(0, 1, 2, 3), (0, 4, 5, 3)[::-1], (1, 2, 5, 4), (0, 1, 4), (3, 5, 2)]:
        try: bm.faces.new([v[i] for i in f])
        except ValueError: pass
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new('unit_prism'); bm.to_mesh(me); bm.free(); me.materials.append(None); _c['pr'] = me; return me

def obj(name, mesh, loc, scale, mat, coll, rot=(0, 0, 0), parent=None):
    o = bpy.data.objects.new(name, mesh); o.location = loc; o.scale = scale; o.rotation_euler = rot; o.parent = parent
    o.material_slots[0].link = 'OBJECT'; o.material_slots[0].material = mat
    coll.objects.link(o); return o
def bx(name, p0, p1, mat, coll):
    """scatola dall'angolo p0 all'angolo p1 (origine in p0)."""
    return obj(name, box0(), p0, (p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]), mat, coll)
def cyl(name, r, h, loc, mat, coll, rot=(0, 0, 0), parent=None):
    return obj(name, shared_mesh('cyl:%g:%g' % (r, h)), loc, (1, 1, 1), mat, coll, rot, parent)
def ball_(name, r, loc, mat, coll, parent=None, sc=(1, 1, 1)):
    return obj(name, shared_mesh('sphere'), loc, (r * sc[0], r * sc[1], r * sc[2]), mat, coll, parent=parent)

def noise_mat(name, c1, c2, scale=6.0, rough=0.9):
    m = material(name, c1, rough=rough, spec=0.1)
    nt = m.node_tree; b = nt.nodes['Principled BSDF']
    tex = nt.nodes.new('ShaderNodeTexNoise'); tex.inputs['Scale'].default_value = scale; tex.inputs['Detail'].default_value = 4
    tc = nt.nodes.new('ShaderNodeTexCoord'); nt.links.new(tc.outputs['Object'], tex.inputs['Vector'])
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color = (*c1, 1); ramp.color_ramp.elements[1].color = (*c2, 1)
    nt.links.new(tex.outputs['Fac'], ramp.inputs['Fac']); nt.links.new(ramp.outputs['Color'], b.inputs['Base Color'])
    return m
def glassy(name, color, alpha, rough=0.1):
    m = material(name, color, rough=rough, spec=0.6)
    m.surface_render_method = 'BLENDED'; m.node_tree.nodes['Principled BSDF'].inputs['Alpha'].default_value = alpha
    return m

def make_mats():
    M = {}
    M['soil'] = noise_mat('S_soil', (0.50, 0.34, 0.20), (0.40, 0.45, 0.18), 5.0)
    M['dirt_dark'] = material('S_dirtdark', (0.30, 0.20, 0.12), rough=1.0, spec=0.05)
    M['gravel'] = noise_mat('S_gravel', (0.52, 0.52, 0.54), (0.74, 0.74, 0.76), 40.0)
    M['sand'] = material('S_sand', (0.93, 0.80, 0.52), rough=0.95, spec=0.05)
    M['syn1'] = material('S_syn1', (0.18, 0.66, 0.24), rough=0.9, spec=0.1)
    M['syn2'] = material('S_syn2', (0.14, 0.58, 0.20), rough=0.9, spec=0.1)
    M['infill'] = noise_mat('S_infill', (0.10, 0.45, 0.16), (0.10, 0.12, 0.10), 60.0)
    M['gr1'] = material('S_gr1', (0.20, 0.72, 0.22), rough=0.95, spec=0.05)
    M['gr2'] = material('S_gr2', (0.12, 0.58, 0.16), rough=0.95, spec=0.05)
    M['line'] = material('S_line', (1, 1, 1), rough=0.8, spec=0.1)
    M['water'] = glassy('S_water', (0.18, 0.46, 0.80), 0.66, 0.05)
    M['concrete'] = material('S_concrete', (0.78, 0.78, 0.80), rough=0.9)
    M['white'] = material('S_white', (0.97, 0.97, 0.97), rough=0.5, spec=0.3)
    M['pipe'] = material('S_pipe', (0.95, 0.45, 0.10), rough=0.5)
    M['yellow'] = material('S_yellow', (1.0, 0.76, 0.10), rough=0.5)
    M['dark'] = material('S_dark', (0.12, 0.12, 0.14), rough=0.7)
    M['steel'] = material('S_steel', (0.65, 0.68, 0.72), rough=0.35, metallic=0.5)
    M['red'] = material('S_red', (0.85, 0.12, 0.12), rough=0.5)
    M['net'] = material('S_net', (1, 1, 1), rough=0.8)
    M['asphalt'] = material('S_asphalt', (0.26, 0.27, 0.30), rough=0.95, spec=0.05)
    M['sidewalk'] = material('S_sidewalk', (0.82, 0.80, 0.76), rough=0.9)
    M['park'] = material('S_park', (0.46, 0.72, 0.36), rough=0.95)
    M['roof'] = [material('S_roof%d' % i, c, rough=0.8) for i, c in enumerate([(0.62, 0.22, 0.16), (0.30, 0.34, 0.50), (0.45, 0.30, 0.22)])]
    M['wall'] = [material('S_wall%d' % i, c, rough=0.9) for i, c in enumerate([(0.96, 0.88, 0.70), (0.93, 0.78, 0.74), (0.78, 0.88, 0.94), (0.92, 0.92, 0.80), (0.98, 0.95, 0.90), (0.80, 0.90, 0.78)])]
    M['window'] = material('S_window', (0.55, 0.78, 0.95), rough=0.15, spec=0.8, emit=(1.0, 0.85, 0.5), emit_strength=0.0)
    M['door'] = material('S_door', (0.18, 0.30, 0.65), rough=0.6)
    M['leaf'] = [material('S_leaf%d' % i, c, rough=0.9) for i, c in enumerate([(0.24, 0.55, 0.22), (0.30, 0.62, 0.26), (0.20, 0.48, 0.24)])]
    M['bark'] = material('S_bark', (0.38, 0.26, 0.16), rough=0.95)
    M['ball'] = material('S_ball', (0.97, 0.97, 0.97), rough=0.35, spec=0.6, coat=0.6)
    nt = M['ball'].node_tree; b = nt.nodes['Principled BSDF']
    vor = nt.nodes.new('ShaderNodeTexVoronoi'); vor.inputs['Scale'].default_value = 3.2
    tc = nt.nodes.new('ShaderNodeTexCoord'); nt.links.new(tc.outputs['Object'], vor.inputs['Vector'])
    rp = nt.nodes.new('ShaderNodeValToRGB'); rp.color_ramp.elements[0].position = 0.80; rp.color_ramp.elements[1].position = 0.84
    rp.color_ramp.elements[0].color = (0.05, 0.05, 0.06, 1); rp.color_ramp.elements[1].color = (0.98, 0.98, 0.98, 1)
    nt.links.new(vor.outputs['Distance'], rp.inputs['Fac']); nt.links.new(rp.outputs['Color'], b.inputs['Base Color'])
    M['cloud'] = material('S_cloud', (0.40, 0.42, 0.48), rough=1.0)
    M['rain'] = glassy('S_rain', (0.75, 0.85, 1.0), 0.55, 0.1)
    M['lampfx'] = material('S_lampfx', (1, 1, 0.85), rough=0.4, emit=(1.0, 0.95, 0.75), emit_strength=0.0)
    for i, c in enumerate([(0.9, 0.15, 0.15), (0.15, 0.35, 0.9), (0.95, 0.75, 0.1), (0.95, 0.95, 0.95), (0.15, 0.65, 0.35), (0.6, 0.2, 0.7), (0.95, 0.5, 0.1)]):
        M['car%d' % i] = material('S_car%d' % i, c, rough=0.3, spec=0.6, coat=0.5)
    return M

def build_city(coll, M, rng):
    """Strade, marciapiedi e quartiere di casette tutto attorno al campo."""
    # terreno parco + anelli
    for (a, b, c, d) in [(-70, -70, 70, -BY - .3), (-70, BY + .3, 70, 70), (-70, -BY - .3, -BX - .3, BY + .3), (BX + .3, -BY - .3, 70, BY + .3)]:
        bx('Park', (a, b, -0.06), (c, d, 0.0), M['park'], coll)
    def ring(name, r0x, r0y, r1x, r1y, z, mat):
        for (a, b, c, d) in [(-r1x, -r1y, r1x, -r0y), (-r1x, r0y, r1x, r1y), (-r1x, -r0y, -r0x, r0y), (r0x, -r0y, r1x, r0y)]:
            bx(name, (a, b, z), (c, d, z + 0.05), mat, coll)
    s1x, s1y = BX + 2.2, BY + 1.9
    ring('Sidewalk1', s1x, s1y, s1x + 1.4, s1y + 1.4, -0.02, M['sidewalk'])
    rx0, ry0 = s1x + 1.4, s1y + 1.4
    ring('Road', rx0, ry0, rx0 + 3.8, ry0 + 3.8, -0.03, M['asphalt'])
    ring('Sidewalk2', rx0 + 3.8, ry0 + 3.8, rx0 + 5.2, ry0 + 5.2, -0.02, M['sidewalk'])
    cx_, cy_ = rx0 + 1.9, ry0 + 1.9
    for k in range(int(-cx_ / 1.5), int(cx_ / 1.5) + 1):
        x = k * 1.5
        bx('Dash', (x - 0.4, -cy_ - .05, 0.01), (x + 0.4, -cy_ + .05, 0.012), M['white'], coll)
        bx('Dash', (x - 0.4, cy_ - .05, 0.01), (x + 0.4, cy_ + .05, 0.012), M['white'], coll)
    for k in range(int(-cy_ / 1.5), int(cy_ / 1.5) + 1):
        y = k * 1.5
        bx('Dash', (-cx_ - .05, y - 0.4, 0.01), (-cx_ + .05, y + 0.4, 0.012), M['white'], coll)
        bx('Dash', (cx_ - .05, y - 0.4, 0.01), (cx_ + .05, y + 0.4, 0.012), M['white'], coll)
    houses = []
    def house(x, y, w, d, h, rotz):
        wi = rng.integers(0, len(M['wall'])); ri = rng.integers(0, len(M['roof']))
        root = empty('House', (x, y, 0), None, coll)
        obj('Body', box_c(), (0, 0, h / 2), (w, d, h), M['wall'][wi], coll, parent=root)
        obj('Roof', prism(), (0, 0, h + 0.45), (w + 0.3, d + 0.3, 0.9), M['roof'][ri], coll, parent=root)
        obj('Door', box_c(), (0, -d / 2 - 0.02, 0.55), (0.55, 0.06, 1.1), M['door'], coll, parent=root)
        nwin = max(1, int(w // 1.6))
        for j in range(nwin):
            wx = (j - (nwin - 1) / 2) * 1.5
            if abs(wx) < 0.5 and nwin % 2 == 1: continue
            obj('Win', box_c(), (wx, -d / 2 - 0.02, 1.4), (0.55, 0.06, 0.6), M['window'], coll, parent=root)
            if h > 2.6: obj('Win', box_c(), (wx, -d / 2 - 0.02, 2.5), (0.55, 0.06, 0.6), M['window'], coll, parent=root)
        root.rotation_euler = (0, 0, rotz); houses.append(root); return root
    hy = ry0 + 5.2 + 3.2; hx = rx0 + 5.2 + 3.2
    nx_ = int((hx + 6) / 3.6); ny_ = int((hy + 2) / 3.8)
    for k in range(-nx_, nx_ + 1):
        x = k * 3.6 + rng.uniform(-.2, .2)
        house(x, hy + rng.uniform(-.4, .4), rng.uniform(2.4, 3.2), 3.0, rng.uniform(2.6, 4.2), math.pi)
        house(x, -hy + rng.uniform(-.4, .4), rng.uniform(2.4, 3.2), 3.0, rng.uniform(2.6, 4.2), 0)
    for k in range(-ny_, ny_ + 1):
        y = k * 3.8
        house(hx + rng.uniform(-.3, .3), y, 3.0, rng.uniform(2.4, 3.0), rng.uniform(2.6, 4.0), math.pi / 2)
        house(-hx + rng.uniform(-.3, .3), y, 3.0, rng.uniform(2.4, 3.0), rng.uniform(2.6, 4.0), -math.pi / 2)
    ty = hy + 8
    for k in range(-nx_ - 2, nx_ + 3):
        x = k * 4.2
        h = rng.uniform(7, 16)
        root = empty('Tower', (x, ty + rng.uniform(0, 3), 0), None, coll)
        obj('Body', box_c(), (0, 0, h / 2), (3.4, 3.4, h), M['wall'][rng.integers(0, 6)], coll, parent=root)
        for zz in np.arange(1.2, h - .5, 1.6):
            for wx in (-1.0, 0.0, 1.0):
                obj('Win', box_c(), (wx, -1.72, zz), (0.55, 0.06, 0.7), M['window'], coll, parent=root)
    def tree(x, y, s=1.0):
        t = empty('Tree', (x, y, 0), None, coll)
        obj('Trunk', shared_mesh('cyl:0.14:1.2'), (0, 0, 0.6 * s), (s, s, s), M['bark'], coll, parent=t)
        for (dx, dy, dz, r) in [(0, 0, 1.7, 0.75), (0.35, 0.1, 1.5, 0.5), (-0.3, -0.1, 1.55, 0.55)]:
            ball_('Leaf', r * s, (dx * s, dy * s, dz * s), M['leaf'][rng.integers(0, 3)], coll, parent=t)
        return t
    ty1 = BY + 1.0; tx1 = BX + 1.0
    for k in range(int(-tx1 / 1.9), int(tx1 / 1.9) + 1):
        tree(k * 1.9 + .3, ty1, rng.uniform(.9, 1.2)); tree(k * 1.9 + .3, -ty1, rng.uniform(.9, 1.2))
    for k in range(int(-ty1 / 1.8), int(ty1 / 1.8) + 1):
        tree(tx1, k * 1.8, rng.uniform(.9, 1.2)); tree(-tx1, k * 1.8, rng.uniform(.9, 1.2))
    return houses, dict(cx=cx_, cy=cy_)

def build_field(coll, M, rng):
    """Letto campo, cordoli, 6 strisce di terreno sconnesso (con shape key 'flat'). Ritorna dict di handle."""
    F = {}
    for (name, p0, p1) in [('CurbN', (-BX - .3, BY, -0.5), (BX + .3, BY + .3, CURB_H)), ('CurbS', (-BX - .3, -BY - .3, -0.5), (BX + .3, -BY, CURB_H)),
                           ('CurbW', (-BX - .3, -BY, -0.5), (-BX, BY, CURB_H)), ('CurbE', (BX, -BY, -0.5), (BX + .3, BY, CURB_H))]:
        bx(name, p0, p1, M['concrete'], coll)
    bx('Bed', (-BX, -BY, -0.5), (BX, BY, -0.02), M['dirt_dark'], coll)
    # strisce di terreno
    strips = []
    nx_total = int(2 * BX / 0.1); ny = int(2 * BY / 0.1)
    per = nx_total // NSTRIP
    xs_all = np.linspace(-BX, BX, nx_total + 1)
    ys = np.linspace(-BY, BY, ny + 1)
    for s in range(NSTRIP):
        i0 = s * per; i1 = (s + 1) * per if s < NSTRIP - 1 else nx_total
        xs = xs_all[i0:i1 + 1]
        bm = bmesh.new()
        grid = [[bm.verts.new((x, y, float(H(x, y)))) for y in ys] for x in xs]
        for i in range(len(xs) - 1):
            for j in range(len(ys) - 1):
                bm.faces.new((grid[i][j], grid[i + 1][j], grid[i + 1][j + 1], grid[i][j + 1]))
        for f in bm.faces: f.smooth = True
        me = bpy.data.meshes.new('strip%d' % s); bm.to_mesh(me); bm.free(); me.materials.append(None)
        o = bpy.data.objects.new('Soil%d' % s, me); o.material_slots[0].link = 'OBJECT'; o.material_slots[0].material = M['soil']
        coll.objects.link(o)
        o.shape_key_add(name='Basis'); sk = o.shape_key_add(name='flat')
        for v, kv in zip(me.vertices, sk.data):
            kv.co = (v.co.x, v.co.y, 0.0)
        strips.append(o)
    F['strips'] = strips; F['strip_x'] = [(xs_all[s * per], xs_all[min((s + 1) * per, nx_total)]) for s in range(NSTRIP)]
    return F

def ribbon(name, pts, width, mat, coll, zfun, flat_z=None, build=None):
    """Nastro bianco lungo una polilinea; (zfun(x,y) = quota). Se flat_z: shape key 'flat'. build=(frame_start, duration)."""
    pts = np.asarray(pts); n = len(pts)
    bm = bmesh.new()
    left = []; right = []
    for i in range(n):
        d = pts[min(i + 1, n - 1)] - pts[max(i - 1, 0)]; d = d / (np.linalg.norm(d) + 1e-9)
        nx_, ny_ = -d[1], d[0]
        for sgn, lst in ((1, left), (-1, right)):
            x = pts[i][0] + sgn * nx_ * width / 2; y = pts[i][1] + sgn * ny_ * width / 2
            lst.append(bm.verts.new((x, y, float(zfun(x, y)))))
    for i in range(n - 1):
        bm.faces.new((left[i], right[i], right[i + 1], left[i + 1]))
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); me.materials.append(None)
    o = bpy.data.objects.new(name, me); o.material_slots[0].link = 'OBJECT'; o.material_slots[0].material = mat; coll.objects.link(o)
    if flat_z is not None:
        o.shape_key_add(name='Basis'); sk = o.shape_key_add(name='flat')
        for v, kv in zip(me.vertices, sk.data): kv.co = (v.co.x, v.co.y, flat_z)
    if build:
        m = o.modifiers.new('Build', 'BUILD'); m.frame_start = build[0]; m.frame_duration = max(1, build[1])
    return o

def goal(name, side, M, coll):
    """porta: side=+1 (x=+PX) o -1. Ritorna root; la rete e' un oggetto separato (net) per animarla."""
    root = empty(name, (side * PX, 0, 0), None, coll)
    h = GOAL_H; w = GOAL_W; d = GOAL_D * side
    for yy in (-w / 2, w / 2):
        obj('Post', shared_mesh('cyl:0.07:%g' % (h + 0.3)), (0, yy, (h - 0.3) / 2), (1, 1, 1), M['white'], coll, parent=root)
        obj('BackPost', shared_mesh('cyl:0.05:%g' % (h + 0.3)), (d, yy, (h - 0.3) / 2), (1, 1, 1), M['white'], coll, parent=root)
        obj('Stay', shared_mesh('cyl:0.04:%g' % d), (d / 2, yy, h), (1, 1, 1), M['white'], coll, rot=(0, math.pi / 2, 0), parent=root)
    obj('Crossbar', shared_mesh('cyl:0.07:%g' % w), (0, 0, h), (1, 1, 1), M['white'], coll, rot=(math.pi / 2, 0, 0), parent=root)
    obj('BackBar', shared_mesh('cyl:0.05:%g' % w), (d, 0, h), (1, 1, 1), M['white'], coll, rot=(math.pi / 2, 0, 0), parent=root)
    net = empty(name + '_netroot', (0, 0, 0), root, coll)
    n1 = obj('Net', box_c(), (d / 2, 0, (h - 0.3) / 2 + 0.0), (abs(d), w, h + 0.3), M['net'], coll, parent=net)
    md = n1.modifiers.new('Wire', 'WIREFRAME'); md.thickness = 0.02; md.use_replace = True
    net.scale = (1, 1, 0.001)
    return root, net
