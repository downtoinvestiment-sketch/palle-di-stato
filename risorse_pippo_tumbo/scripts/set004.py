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


def grid_mat(name, col, dark, pz, px, rough=0.85):
    """colore con righe orizzontali (ogni pz in Z locale) e giunti verticali sfalsati (ogni px in X): doghe / tegole."""
    m = material(name, col, rough=rough, spec=0.15)
    nt = m.node_tree; b = nt.nodes['Principled BSDF']
    tc = nt.nodes.new('ShaderNodeTexCoord'); sp = nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(tc.outputs['Object'], sp.inputs[0])
    def mth(op, a, bv=None):
        n = nt.nodes.new('ShaderNodeMath'); n.operation = op
        if isinstance(a, float): n.inputs[0].default_value = a
        else: nt.links.new(a, n.inputs[0])
        if bv is not None:
            if isinstance(bv, float): n.inputs[1].default_value = bv
            else: nt.links.new(bv, n.inputs[1])
        return n.outputs[0]
    line = None
    if pz > 0:
        zs = mth('DIVIDE', sp.outputs['Z'], float(pz)); fz = mth('FRACT', zs); line = mth('LESS_THAN', fz, 0.14)
        if px > 0:
            row = mth('FLOOR', zs); off = mth('MULTIPLY', row, 0.5); xs = mth('ADD', mth('DIVIDE', mth('ADD', sp.outputs['X'], sp.outputs['Y']), float(px)), off)
            l2 = mth('LESS_THAN', mth('FRACT', xs), 0.10); line = mth('MAXIMUM', line, l2)
    elif px > 0:
        line = mth('LESS_THAN', mth('FRACT', mth('DIVIDE', mth('ADD', sp.outputs['X'], sp.outputs['Y']), float(px))), 0.12)
    mix = nt.nodes.new('ShaderNodeMix'); mix.data_type = 'RGBA'
    mix.inputs[6].default_value = (*col, 1); mix.inputs[7].default_value = (col[0] * dark, col[1] * dark, col[2] * dark, 1)
    nt.links.new(line, mix.inputs[0]); nt.links.new(mix.outputs[2], b.inputs['Base Color'])
    return m

class MB:
    """accumula scatole/prismi in un'unica mesh multi-materiale (coordinate locali reali)."""
    def __init__(self, mats):
        self.mats = mats; self.v = []; self.f = []; self.mi = []
    def box(self, c, s, mi, rx=0.0, rz=0.0):
        n = len(self.v); hx, hy, hz = s[0] / 2, s[1] / 2, s[2] / 2
        cr, sr = math.cos(rx), math.sin(rx); cz, sz = math.cos(rz), math.sin(rz)
        for (x, y, z) in [(-hx, -hy, -hz), (hx, -hy, -hz), (hx, hy, -hz), (-hx, hy, -hz), (-hx, -hy, hz), (hx, -hy, hz), (hx, hy, hz), (-hx, hy, hz)]:
            y, z = y * cr - z * sr, y * sr + z * cr
            x, y = x * cz - y * sz, x * sz + y * cz
            self.v.append((c[0] + x, c[1] + y, c[2] + z))
        for q in [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]:
            self.f.append(tuple(n + i for i in q)); self.mi.append(mi)
    def b2(self, p0, p1, mi):
        self.box(((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2, (p0[2] + p1[2]) / 2), (abs(p1[0] - p0[0]), abs(p1[1] - p0[1]), abs(p1[2] - p0[2])), mi)
    def gable(self, x0, x1, y0, y1, z, rh, mi):
        """prisma con colmo lungo X."""
        n = len(self.v); ym = (y0 + y1) / 2
        self.v += [(x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z), (x0, ym, z + rh), (x1, ym, z + rh)]
        for q in [(0, 1, 5, 4), (2, 3, 4, 5), (0, 4, 3), (1, 2, 5)]:
            self.f.append(tuple(n + i for i in q)); self.mi.append(mi)
    def build(self, name, coll, loc=(0, 0, 0), rotz=0.0):
        me = bpy.data.meshes.new(name); me.from_pydata(self.v, [], self.f)
        for m in self.mats: me.materials.append(m)
        me.polygons.foreach_set('material_index', self.mi); me.update()
        o = bpy.data.objects.new(name, me); o.location = loc; o.rotation_euler = (0, 0, rotz); coll.objects.link(o); return o

# indici materiali casa
WALL, ROOF, SHUT, FRAME, GLASS, DOOR, STONE, CHIM, HEDGE, WOOD, FL1, FL2, DARK, PATH = range(14)
def house_mats(M, wi, ri, si):
    return [M['wall'][wi], M['roof'][ri], M['shutter'][si], M['frame'], M['window'], M['door'], M['stone'], M['chim'], M['hedge'], M['wood'], M['flower'][si % 3], M['flower'][(si + 1) % 3], M['dark'], M['sidewalk']]

def window_geo(mb, cx, y, cz, ww=0.62, wh=0.78, face=-1, shutters=True, flowerbox=False, axis='x'):
    """finestra su una parete: axis='x' parete a y costante (larghezza lungo x), axis='y' parete a x costante."""
    def B(u, dpt, z, su, sd, sz, mi):
        if axis == 'x': mb.box((cx + u, y + face * dpt, z), (su, sd, sz), mi)
        else: mb.box((y + face * dpt, cx + u, z), (sd, su, sz), mi)
    B(0, 0.03, cz, ww + 0.16, 0.08, wh + 0.16, FRAME)
    B(0, 0.06, cz, ww, 0.06, wh, GLASS)
    B(0, 0.085, cz, 0.045, 0.03, wh, FRAME); B(0, 0.085, cz, ww, 0.03, 0.045, FRAME)
    B(0, 0.09, cz - wh / 2 - 0.10, ww + 0.26, 0.18, 0.06, FRAME)
    if shutters:
        for sgn in (-1, 1):
            B(sgn * (ww / 2 + 0.21), 0.04, cz, 0.24, 0.06, wh + 0.10, SHUT)
    if flowerbox:
        B(0, 0.17, cz - wh / 2 - 0.02, ww + 0.1, 0.16, 0.14, WOOD)
        for k in range(5):
            B((k - 2) * ww / 5, 0.17, cz - wh / 2 + 0.10, 0.11, 0.12, 0.11, FL1 if k % 2 else FL2)

def roof_geo(mb, w, d, h, rh=1.25, ov=0.34):
    """tetto a due falde con colmo lungo X, gronde sporgenti, timpani nel colore del muro, camino."""
    mb.gable(-w / 2, w / 2, -d / 2, d / 2, h, rh, WALL)
    a = math.atan2(rh, d / 2); L = math.hypot(rh, d / 2) + ov + 0.06; th = 0.12
    for sgn in (-1, 1):
        # falda: centro a metà tra gronda e colmo, spostato lungo la normale
        ey = sgn * (d / 2 + ov * math.cos(a)); ez = h - ov * math.sin(a)
        cy = (ey + 0) / 2; cz = (ez + h + rh) / 2
        ny, nz = sgn * math.sin(a), math.cos(a)
        mb.box((0, cy + ny * th / 2, cz + nz * th / 2), (w + 2 * ov, L, th), ROOF, rx=-sgn * a)
        mb.box((0, ey, ez - 0.02), (w + 2 * ov + 0.04, 0.07, 0.16), FRAME)   # frontalino di gronda
    mb.box((0, 0, h + rh + 0.10), (w + 2 * ov, 0.2, 0.10), CHIM)             # colmo
    mb.box((w * 0.27, d * 0.2, h + rh * 0.75), (0.38, 0.38, 1.1), CHIM); mb.box((w * 0.27, d * 0.2, h + rh * 0.75 + 0.58), (0.50, 0.50, 0.10), STONE)

def house_geo(mb, w, d, h, two, rng):
    fy = -d / 2
    mb.box((0, 0, 0.16), (w + 0.12, d + 0.12, 0.32), STONE)                  # zoccolo
    mb.box((0, 0, h / 2 + 0.16), (w, d, h - 0.32), WALL)
    for sx in (-1, 1): mb.box((sx * w / 2, fy, h / 2 + 0.16), (0.12, 0.12, h - 0.32), FRAME); mb.box((sx * w / 2, -fy, h / 2 + 0.16), (0.12, 0.12, h - 0.32), FRAME)
    if two: mb.box((0, 0, 2.42), (w + 0.06, d + 0.06, 0.10), FRAME)           # marcapiano
    roof_geo(mb, w, d, h)
    # porta con cornice, pomello, tettoia e gradini
    dx = -w * 0.22
    mb.box((dx, fy - 0.03, 1.16), (0.84, 0.08, 1.80), FRAME); mb.box((dx, fy - 0.06, 1.12), (0.66, 0.08, 1.64), DOOR)
    mb.box((dx, fy - 0.10, 1.55), (0.36, 0.03, 0.36), GLASS); mb.box((dx + 0.24, fy - 0.11, 1.05), (0.07, 0.05, 0.07), STONE)
    mb.box((dx, fy - 0.38, 2.22), (1.25, 0.80, 0.08), ROOF, rx=0.28)
    for sx in (-0.52, 0.52): mb.box((dx + sx, fy - 0.68, 1.22), (0.07, 0.07, 1.80), FRAME)
    mb.box((dx, fy - 0.42, 0.24), (1.25, 0.80, 0.16), STONE); mb.box((dx, fy - 0.92, 0.10), (1.25, 0.30, 0.16), STONE)
    mb.box((dx, fy - 1.25, 0.03), (0.7, 0.9, 0.06), PATH)
    # finestre: facciata, piano alto, fianchi, retro
    window_geo(mb, w * 0.24, fy, 1.45, flowerbox=True)
    if two:
        window_geo(mb, -w * 0.24, fy, 3.35); window_geo(mb, w * 0.24, fy, 3.35, flowerbox=True)
    else:
        mb.box((0, fy - 0.02, h + 0.55), (0.42, 0.06, 0.42), FRAME); mb.box((0, fy - 0.05, h + 0.55), (0.30, 0.06, 0.30), GLASS)
    for zz in ([1.45, 3.35] if two else [1.45]):
        for sx in (-1, 1):
            window_geo(mb, 0.0, sx * w / 2, zz, face=sx, shutters=False, axis='y')
        window_geo(mb, -w * 0.24, -fy, zz, face=1); window_geo(mb, w * 0.24, -fy, zz, face=1)
    # giardino: siepe, staccionata bianca, cespuglio fiorito, cassetta postale
    gy = fy - 1.62; half = min(w / 2 + 0.25, 1.72)
    for xx in np.arange(-half, half + 0.01, 0.19):
        if abs(xx - dx) < 0.42: continue
        mb.box((xx, gy, 0.30), (0.09, 0.04, 0.56), FRAME); mb.box((xx, gy, 0.60), (0.065, 0.04, 0.07), FRAME)
    for (xa, xb) in ((-half, dx - 0.42), (dx + 0.42, half)):
        for zz in (0.20, 0.44): mb.box(((xa + xb) / 2, gy + 0.03, zz), (xb - xa, 0.03, 0.06), FRAME)
    mb.box((w * 0.24, fy - 0.30, 0.42), (w * 0.42, 0.42, 0.40), HEDGE); mb.box((w * 0.24, fy - 0.30, 0.66), (w * 0.34, 0.30, 0.10), HEDGE)
    for k in range(4): mb.box((w * 0.24 + (k - 1.5) * 0.22, fy - 0.50, 0.60 + 0.05 * (k % 2)), (0.10, 0.10, 0.10), FL1 if k % 2 else FL2)
    mb.box((dx + 0.75, gy + 0.12, 0.45), (0.06, 0.06, 0.9), WOOD); mb.box((dx + 0.75, gy + 0.12, 0.95), (0.22, 0.32, 0.2), DOOR)

def tower_geo(mb, tw, h, rng):
    """palazzo: 0 muro, 1 vetro, 2 bianco, 3 cemento, 4 scuro, 5 accento."""
    hw = tw / 2
    mb.box((0, 0, 0.7), (tw + 0.1, tw + 0.1, 1.4), 3); mb.box((0, 0, h / 2 + 0.7), (tw, tw, h - 1.4), 0)
    mb.box((0, -hw - 0.02, 0.75), (1.0, 0.06, 1.3), 1); mb.box((0, -hw - 0.3, 1.5), (1.6, 0.6, 0.08), 5)
    nfl = int((h - 1.6) / 1.5)
    for k in range(nfl):
        z = 2.3 + k * 1.5
        mb.box((0, 0, z - 0.72), (tw + 0.10, tw + 0.10, 0.09), 2)
        for sgn in (-1, 1):
            for wx in (-hw * 0.56, hw * 0.56):
                mb.box((wx, sgn * (hw + 0.01), z), (hw * 0.62, 0.06, 0.82), 2); mb.box((wx, sgn * (hw + 0.03), z), (hw * 0.62 - 0.12, 0.06, 0.70), 1)
                mb.box((wx, sgn * (hw + 0.05), z), (0.04, 0.04, 0.70), 2)
                mb.box((sgn * (hw + 0.01), wx, z), (0.06, hw * 0.62, 0.82), 2); mb.box((sgn * (hw + 0.03), wx, z), (0.06, hw * 0.62 - 0.12, 0.70), 1)
        if k % 2 == 0:   # balconi sul fronte
            bx_ = hw * 0.56 * (1 if (k // 2) % 2 else -1)
            mb.box((bx_, -hw - 0.30, z - 0.50), (hw * 0.8, 0.6, 0.07), 3); mb.box((bx_, -hw - 0.58, z - 0.22), (hw * 0.8, 0.04, 0.5), 5)
    mb.box((0, 0, h + 0.14), (tw + 0.16, tw + 0.16, 0.28), 2); mb.box((hw * 0.3, hw * 0.2, h + 0.6), (1.0, 0.8, 0.7), 3); mb.box((-hw * 0.4, -hw * 0.3, h + 0.45), (0.5, 0.5, 0.4), 4)

def make_mats():
    M = {}
    M['soil'] = noise_mat('S_soil', (0.68, 0.40, 0.15), (0.74, 0.70, 0.22), 5.0)
    M['dirt_dark'] = material('S_dirtdark', (0.30, 0.20, 0.12), rough=1.0, spec=0.05)
    M['gravel'] = noise_mat('S_gravel', (0.52, 0.52, 0.54), (0.74, 0.74, 0.76), 40.0)
    M['sand'] = material('S_sand', (0.93, 0.80, 0.52), rough=0.95, spec=0.05)
    M['syn1'] = material('S_syn1', (0.10, 0.62, 0.16), rough=0.9, spec=0.1)
    M['syn2'] = material('S_syn2', (0.07, 0.50, 0.12), rough=0.9, spec=0.1)
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
    M['asphalt'] = material('S_asphalt', (0.20, 0.21, 0.25), rough=0.95, spec=0.05)
    M['sidewalk'] = material('S_sidewalk', (0.82, 0.80, 0.76), rough=0.9)
    M['park'] = material('S_park', (0.40, 0.74, 0.28), rough=0.95)
    _nt = M['park'].node_tree; _b = _nt.nodes['Principled BSDF']
    _g = _nt.nodes.new('ShaderNodeNewGeometry'); _sx = _nt.nodes.new('ShaderNodeSeparateXYZ'); _nt.links.new(_g.outputs['Position'], _sx.inputs[0])
    _d = _nt.nodes.new('ShaderNodeMath'); _d.operation = 'DIVIDE'; _d.inputs[1].default_value = 2.4; _nt.links.new(_sx.outputs['Y'], _d.inputs[0])
    _f = _nt.nodes.new('ShaderNodeMath'); _f.operation = 'FLOOR'; _nt.links.new(_d.outputs[0], _f.inputs[0])
    _m = _nt.nodes.new('ShaderNodeMath'); _m.operation = 'MODULO'; _m.inputs[1].default_value = 2.0; _nt.links.new(_f.outputs[0], _m.inputs[0])
    _r = _nt.nodes.new('ShaderNodeValToRGB'); _r.color_ramp.interpolation = 'CONSTANT'
    _r.color_ramp.elements[0].position = 0.0; _r.color_ramp.elements[1].position = 0.5
    _r.color_ramp.elements[0].color = (0.42, 0.86, 0.22, 1); _r.color_ramp.elements[1].color = (0.26, 0.72, 0.14, 1)
    _nt.links.new(_m.outputs[0], _r.inputs[0]); _nt.links.new(_r.outputs['Color'], _b.inputs['Base Color'])
    M['frame'] = material('S_frame', (0.97, 0.97, 0.95), rough=0.6)
    M['shutter'] = [material('S_shut%d' % i, c, rough=0.6) for i, c in enumerate([(0.15, 0.6, 0.85), (0.9, 0.7, 0.15), (0.2, 0.7, 0.35), (0.7, 0.35, 0.85), (0.85, 0.25, 0.25)])]
    M['carc'] = [material('S_car%d' % i, c, rough=0.35, spec=0.6) for i, c in enumerate([(0.85, 0.15, 0.15), (0.15, 0.4, 0.85), (0.95, 0.85, 0.2), (0.9, 0.9, 0.92), (0.15, 0.6, 0.35)])]
    M['tyre'] = material('S_tyre', (0.06, 0.06, 0.07), rough=0.8)
    M['chim'] = material('S_chim', (0.55, 0.30, 0.25), rough=0.9)
    M['roof'] = [grid_mat('S_roof%d' % i, c, 0.62, 0.20, 0.26) for i, c in enumerate([(0.86, 0.22, 0.12), (0.92, 0.36, 0.14), (0.70, 0.16, 0.14), (0.22, 0.36, 0.62)])]
    M['wall'] = [grid_mat('S_wall%d' % i, c, 0.88, 0.24, 0.0) for i, c in enumerate([(1.0, 0.86, 0.42), (1.0, 0.62, 0.50), (0.50, 0.80, 1.0), (0.98, 0.96, 0.90), (0.98, 0.95, 0.88), (0.55, 0.90, 0.62)])]
    M['tower'] = [material('S_tower%d' % i, c, rough=0.85) for i, c in enumerate([(0.95, 0.52, 0.30), (0.98, 0.80, 0.36), (0.30, 0.66, 0.80), (0.96, 0.94, 0.90), (0.90, 0.42, 0.42), (0.52, 0.76, 0.50)])]
    M['hedge'] = noise_mat('S_hedge', (0.10, 0.50, 0.14), (0.22, 0.70, 0.20), 9.0)
    M['stone'] = noise_mat('S_stone', (0.62, 0.60, 0.58), (0.80, 0.78, 0.74), 14.0)
    M['wood'] = grid_mat('S_wood', (0.62, 0.38, 0.18), 0.8, 0.0, 0.16)
    M['flower'] = [material('S_flower%d' % i, c, rough=0.6) for i, c in enumerate([(1.0, 0.25, 0.35), (1.0, 0.85, 0.15), (0.95, 0.45, 0.95)])]
    M['window'] = material('S_window', (0.30, 0.66, 1.0), rough=0.12, spec=0.9, emit=(1.0, 0.85, 0.5), emit_strength=0.0)
    M['door'] = material('S_door', (0.80, 0.16, 0.14), rough=0.5)
    M['leaf'] = [material('S_leaf%d' % i, c, rough=0.9) for i, c in enumerate([(0.16, 0.62, 0.16), (0.28, 0.74, 0.20), (0.12, 0.52, 0.18)])]
    M['bark'] = material('S_bark', (0.38, 0.26, 0.16), rough=0.95)
    M['ball'] = material('S_ball', (0.97, 0.97, 0.97), rough=0.35, spec=0.6, coat=0.6)
    nt = M['ball'].node_tree; b = nt.nodes['Principled BSDF']
    vor = nt.nodes.new('ShaderNodeTexVoronoi'); vor.inputs['Scale'].default_value = 3.2
    tc = nt.nodes.new('ShaderNodeTexCoord'); nt.links.new(tc.outputs['Object'], vor.inputs['Vector'])
    rp = nt.nodes.new('ShaderNodeValToRGB'); rp.color_ramp.elements[0].position = 0.30; rp.color_ramp.elements[1].position = 0.34
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
        rotz += math.pi
        wi = int(rng.integers(0, len(M['wall']))); ri = int(rng.integers(0, len(M['roof']))); si = int(rng.integers(0, len(M['shutter'])))
        two = h > 3.4; h = 4.5 if two else 2.9
        mb = MB(house_mats(M, wi, ri, si))
        house_geo(mb, w, d, h, two, rng)
        o = mb.build('House', coll, (x, y, 0), rotz); houses.append(o); return o
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
    for (cxp, cyp, rz) in [(-6, -cy_ + 0.9, 0), (3, -cy_ + 0.9, 0), (-9, cy_ - 0.9, math.pi), (7, cy_ - 0.9, math.pi), (-cx_ + 0.9, -4, math.pi / 2), (cx_ - 0.9, 5, -math.pi / 2), (cx_ - 0.9, -6, -math.pi / 2)]:
        ci = int(rng.integers(0, len(M['carc'])))
        car = empty('Car', (cxp, cyp, 0), None, coll)
        obj('CarB', box_c(), (0, 0, 0.32), (1.9, 0.9, 0.42), M['carc'][ci], coll, parent=car)
        obj('CarT', box_c(), (-0.1, 0, 0.7), (1.0, 0.8, 0.36), M['carc'][ci], coll, parent=car)
        obj('CarW', box_c(), (-0.1, 0, 0.72), (1.02, 0.82, 0.22), M['window'], coll, parent=car)
        for (wx, wy) in ((-0.6, 0.45), (0.6, 0.45), (-0.6, -0.45), (0.6, -0.45)):
            obj('Tyre', shared_mesh('cyl:0.2:0.14'), (wx, wy, 0.2), (1, 1, 1), M['tyre'], coll, parent=car).rotation_euler = (math.pi / 2, 0, 0)
        car.rotation_euler = (0, 0, rz)
    ty = hy + 8
    for k in range(-nx_ - 2, nx_ + 3):
        x = k * 4.2
        h = rng.uniform(7, 16)
        tw = rng.uniform(3.4, 4.4); ti = int(rng.integers(0, len(M['tower'])))
        mb = MB([M['tower'][ti], M['window'], M['frame'], M['concrete'], M['dark'], M['shutter'][int(rng.integers(0, 5))]])
        tower_geo(mb, tw, h, rng)
        mb.build('Tower', coll, (x, ty + rng.uniform(0, 3), 0), math.pi)
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
