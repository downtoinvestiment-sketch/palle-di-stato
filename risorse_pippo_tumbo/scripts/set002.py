"""Set del Test 002: pista a spirale di vetro, vasca trasparente, pedana, studio."""
import bpy, bmesh, math
import numpy as np
from mathutils import Vector
from common import *
from params002 import *

def mesh_obj(name, bm, mat, coll=None, smooth=False, solid=None):
    if smooth:
        for f in bm.faces: f.smooth = True
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me)
    me.materials.append(mat)
    (coll or bpy.context.scene.collection).objects.link(o)
    if solid:
        md = o.modifiers.new('solid', 'SOLIDIFY'); md.thickness = solid; md.offset = 0
    return o

def glass(name, color=(0.80, 0.93, 1.0), alpha=0.20, rough=0.05):
    m = material(name, color, rough=rough, spec=1.0)
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Alpha'].default_value = alpha
    try: m.surface_render_method = 'BLENDED'
    except Exception: m.blend_method = 'BLEND'
    m.use_backface_culling = False
    return m

def strip(bm, secs):
    """secs: lista di (A,B) punti; crea quad fra sezioni consecutive."""
    vs = [(bm.verts.new(a), bm.verts.new(b)) for a, b in secs]
    for (a0, b0), (a1, b1) in zip(vs[:-1], vs[1:]):
        bm.faces.new((a0, a1, b1, b0))
    return vs

def build_track(coll, mats):
    H = 0.27
    phis = np.linspace(PHI0, PHI_END, int((PHI_END - PHI0) / math.radians(2)))
    def hx(rho, phi, dz=0.0):
        return (rho * math.cos(phi), rho * math.sin(phi), helix_z(phi) + dz)
    lipu = np.linspace(0, LIP_LEN, 8)
    def lip(rho_y, u, dz=0.0):
        zl = helix_z(PHI_END) - LIP_SLOPE * u
        return (0.0 - u, rho_y, zl + dz)
    # pavimento
    bm = bmesh.new()
    secs = [((hx(RHO_IN, p)), (hx(RHO_OUT, p))) for p in phis]
    secs += [((lip(RHO_IN, u)), (lip(RHO_OUT, u))) for u in lipu[1:]]
    # per la lip le "rho" sono in y: (x,y) = (-u, rho)
    strip(bm, secs)
    # rampa eroe
    rsecs = []
    for y in np.linspace(RAMP_Y0 + 0.35, 0.0, 14):
        z = Z_TOP + RAMP_DZ * (y / RAMP_Y0)
        rsecs.append(((-RHO_SEP, y, z), (-RHO_OUT, y, z)))
    strip(bm, rsecs)
    floor = mesh_obj('Track_Floor', bm, mats['glass_floor'], coll, solid=0.05)
    # pareti
    def wall(name, rho, mat, rsec=None, ramp_x=None):
        bm = bmesh.new()
        secs = [(hx(rho, p), hx(rho, p, H)) for p in phis]
        secs += [(lip(rho, u), lip(rho, u, H)) for u in lipu[1:]]
        strip(bm, secs)
        return mesh_obj(name, bm, mat, coll, solid=0.035)
    wall('Track_WallIn', RHO_IN, mats['glass'])
    wall('Track_WallOut', RHO_OUT, mats['glass'])
    wall('Track_WallSep', RHO_SEP, mats['glass'])
    # pareti rampa
    for nm, x in (('RampWallIn', -RHO_SEP), ('RampWallOut', -RHO_OUT)):
        bm = bmesh.new()
        rs = []
        for y in np.linspace(RAMP_Y0 + 0.35, 0.0, 14):
            z = Z_TOP + RAMP_DZ * (y / RAMP_Y0)
            rs.append(((x, y, z), (x, y, z + H)))
        strip(bm, rs)
        mesh_obj(nm, bm, mats['glass'], coll, solid=0.035)
    # bordi colorati (tubi sottili) sulle pareti: leggibilità della forma
    # asse centrale + razze
    for ph in np.arange(PHI0, PHI_END, math.radians(50)):
        z = helix_z(ph) - 0.10
        for rho_a, rho_b in ((0.35, RHO_OUT + 0.02),):
            a = Vector((rho_a * math.cos(ph), rho_a * math.sin(ph), z))
            b = Vector((rho_b * math.cos(ph), rho_b * math.sin(ph), z))
            c = (a + b) / 2; L = (b - a).length
            o = shape('Spoke', 'cap:0.035:%f' % max(0.01, L - 0.07), tuple(c), (1, 1, 1),
                      (0, 0, 0), None, mats['frame'], coll)
            o.rotation_euler = (0, 0, 0)
            d = (b - a).normalized()
            o.rotation_mode = 'QUATERNION'; o.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d)
    shape('Pole', 'cyl:0.22:%f' % (Z_TOP + 0.9), (0, 0, (Z_TOP + 0.9) / 2), (1, 1, 1), (0, 0, 0), None,
          mats['frame'], coll)
    return floor

def build_pool(coll, mats):
    cx, cy = POOL_C
    # parete trasparente
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=False, segments=96, radius1=POOL_R, radius2=POOL_R, depth=POOL_H)
    for v in bm.verts: v.co.z += POOL_H / 2 + POOL_FLOOR
    wall = mesh_obj('Pool_Wall', bm, mats['glass_pool'], coll, smooth=True, solid=0.05)
    wall.location = (cx, cy, 0)
    # base e bordo
    shape('Pool_Base', 'cyl:%f:%f' % (POOL_R + 0.20, POOL_FLOOR), (cx, cy, POOL_FLOOR / 2), (1, 1, 1), (0, 0, 0), None, mats['white'], coll)
    base = bpy.data.objects['Pool_Base']; base.scale = (1, 1, 1)
    # disco interno (pavimento vasca) chiaro
    bm = bmesh.new()
    bmesh.ops.create_circle(bm, cap_ends=True, segments=96, radius=POOL_R)
    fl = mesh_obj('Pool_Floor', bm, mats['pool_floor'], coll)
    fl.location = (cx, cy, POOL_FLOOR)
    # bordo superiore
    bpy.ops.mesh.primitive_torus_add(major_radius=POOL_R + 0.02, minor_radius=0.05, major_segments=96,
                                     minor_segments=12, location=(cx, cy, POOL_FLOOR + POOL_H))
    rim = bpy.context.object; rim.name = 'Pool_Rim'; rim.data.materials.append(mats['white'])
    for p in rim.data.polygons: p.use_smooth = True
    for c in rim.users_collection: c.objects.unlink(rim)
    coll.objects.link(rim)
    bpy.ops.mesh.primitive_torus_add(major_radius=POOL_R + 0.02, minor_radius=0.05, major_segments=96,
                                     minor_segments=12, location=(cx, cy, POOL_FLOOR + 0.02))
    r2 = bpy.context.object; r2.name = 'Pool_RimBase'; r2.data.materials.append(mats['white'])
    for p in r2.data.polygons: p.use_smooth = True
    for c in r2.users_collection: c.objects.unlink(r2)
    coll.objects.link(r2)

def build_platform(coll, mats):
    cx, cy = PLAT_C
    top = PLAT_Z
    shape('Plat_Pillar', 'cyl:0.55:%f' % (top - 0.2), (cx, cy, (top - 0.2) / 2), (1, 1, 1), (0, 0, 0), None, mats['white'], coll)
    shape('Plat_Top', 'cyl:%f:0.20' % PLAT_R, (cx, cy, top - 0.10), (1, 1, 1), (0, 0, 0), None, mats['plat'], coll)
    shape('Plat_Foot', 'cyl:0.95:0.20', (cx, cy, 0.10), (1, 1, 1), (0, 0, 0), None, mats['plat'], coll)

def build_gate(coll, mats):
    """Cancello trasparente alla fine della lip (trattiene le file); ruota attorno alla cerniera superiore."""
    zl = helix_z(PHI_END) - LIP_SLOPE * LIP_LEN
    y0, y1 = RHO_IN + 0.02, RHO_SEP - 0.02
    hinge = empty('Gate_Hinge', (-LIP_LEN - 0.04, (y0 + y1) / 2, zl + 0.40), None, coll)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= 0.04; v.co.y *= (y1 - y0); v.co.z *= 0.40; v.co.z -= 0.20
    g = mesh_obj('Gate', bm, mats['glass_gate'], coll)
    g.parent = hinge
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= 0.06; v.co.y *= (y1 - y0 + 0.1); v.co.z *= 0.04
    top = mesh_obj('GateBar', bm, mats['frame'], coll); top.parent = hinge
    return hinge

def make_mats():
    M = {}
    M['glass'] = glass('G_Glass', (0.78, 0.92, 1.0), 0.28)
    M['glass_floor'] = glass('G_GlassFloor', (0.85, 0.95, 1.0), 0.40)
    M['glass_gate'] = glass('G_GlassGate', (1.0, 0.75, 0.80), 0.35)
    M['glass_pool'] = glass('G_GlassPool', (0.80, 0.94, 1.0), 0.16)
    M['frame'] = material('S_Frame', (0.97, 0.97, 1.0), rough=0.45, spec=0.5)
    M['white'] = material('S_White', (0.98, 0.98, 1.0), rough=0.5, spec=0.4)
    M['plat'] = material('S_Plat', (0.30, 0.55, 1.0), rough=0.55, spec=0.4)
    M['pool_floor'] = material('S_PoolFloor', (0.90, 0.95, 1.0), rough=0.6, spec=0.2)
    M['floor'] = material('S_Floor', (0.98, 0.96, 1.0), rough=0.85, spec=0.05)
    return M

def build_set(coll=None):
    coll = coll or collection('Set')
    M = make_mats()
    bpy.ops.mesh.primitive_plane_add(size=80, location=(0, 0, 0))
    fl = bpy.context.object; fl.name = 'Studio_Floor'; fl.data.materials.append(M['floor'])
    for c in fl.users_collection: c.objects.unlink(fl)
    coll.objects.link(fl)
    build_track(coll, M); build_pool(coll, M); build_platform(coll, M)
    hinge = build_gate(coll, M)
    return {'mats': M, 'gate': hinge}
