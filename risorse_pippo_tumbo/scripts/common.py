"""Helper condivisi per il progetto PIPPO SATISFYING TEST 001 (Blender 5.x)."""
import bpy, bmesh, math, random
from mathutils import Vector, Euler

_cache = {}

def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    _cache.clear()
    return bpy.context.scene

def collection(name, parent=None):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
        (parent or bpy.context.scene.collection).children.link(c)
    return c

def _link(o, coll):
    (coll or bpy.context.scene.collection).objects.link(o)

def shared_mesh(kind):
    """Mesh unitarie condivise (sfera, cono) -> tutte le istanze usano gli stessi dati."""
    if kind in _cache and _cache[kind].name in bpy.data.meshes:
        return _cache[kind]
    bm = bmesh.new()
    if kind.startswith('cap:'):          # capsula: raggio, lunghezza del tratto cilindrico (asse Z)
        _, r, L = kind.split(':'); r = float(r); L = float(L)
        bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=20, radius=r)
        for v in bm.verts:
            v.co.z += L / 2 if v.co.z > 1e-6 else (-L / 2 if v.co.z < -1e-6 else 0)
    elif kind.startswith('cyl:'):        # cilindro con basi piatte, centrato, asse Z
        _, r, h = kind.split(':'); r = float(r); h = float(h)
        bmesh.ops.create_cone(bm, cap_ends=True, segments=64, radius1=r, radius2=r, depth=h)
    elif kind == 'lock':                 # ciocca a goccia incurvata: base z=0, punta z~1.5
        bmesh.ops.create_uvsphere(bm, u_segments=20, v_segments=12, radius=1.0)
        for v in bm.verts:
            t = (v.co.z + 1) / 2
            k = 1 - 0.62 * t
            v.co.x = v.co.x * k + 0.55 * t * t
            v.co.y *= k
            v.co.z = t * 1.6 - 0.1
    elif kind == 'sphere':
        bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=16, radius=1.0)
    elif kind == 'sphere_lo':
        bmesh.ops.create_uvsphere(bm, u_segments=20, v_segments=12, radius=1.0)
    elif kind == 'cone':   # base z=0 raggio 1, punta z=1 raggio 0.22 (punta stondata dallo shading)
        bmesh.ops.create_cone(bm, cap_ends=True, segments=20, radius1=1.0, radius2=0.22, depth=1.0)
        for v in bm.verts:
            v.co.z += 0.5
    for f in bm.faces:
        f.smooth = not (kind.startswith('cyl:') and abs(f.normal.z) > 0.5)
    me = bpy.data.meshes.new('unit_' + kind)
    bm.to_mesh(me); bm.free()
    me.materials.append(None)
    _cache[kind] = me
    return me

def material(name, color, rough=0.5, metallic=0.0, spec=0.5, coat=0.0, coat_rough=0.1,
             emit=None, emit_strength=0.0):
    m = bpy.data.materials.get(name)
    if m: return m
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*color[:3], 1)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metallic
    b.inputs['Specular IOR Level'].default_value = spec
    b.inputs['Coat Weight'].default_value = coat
    b.inputs['Coat Roughness'].default_value = coat_rough
    if emit is not None:
        b.inputs['Emission Color'].default_value = (*emit[:3], 1)
        b.inputs['Emission Strength'].default_value = emit_strength
    return m

def empty(name, loc=(0, 0, 0), parent=None, coll=None, size=0.08):
    o = bpy.data.objects.new(name, None)
    o.empty_display_type = 'PLAIN_AXES'
    o.empty_display_size = size
    o.location = loc
    o.parent = parent
    _link(o, coll)
    return o

def shape(name, kind, loc=(0, 0, 0), scale=(1, 1, 1), rot=(0, 0, 0), parent=None, mat=None, coll=None):
    o = bpy.data.objects.new(name, shared_mesh(kind))
    o.location = loc
    o.scale = scale
    o.rotation_euler = rot
    o.parent = parent
    if mat:
        o.material_slots[0].link = 'OBJECT'
        o.material_slots[0].material = mat
    _link(o, coll)
    return o

def key(o, prop, value, frame, index=-1, interp=None):
    setattr(o, prop, value)
    o.keyframe_insert(prop, index=index, frame=frame)

def all_fcurves(obj_or_data):
    """Compatibile con le Action a livelli di Blender 4.4+/5.x."""
    ad = getattr(obj_or_data, 'animation_data', None)
    if not ad or not ad.action: return []
    out = []
    for layer in ad.action.layers:
        for strip in layer.strips:
            for cb in strip.channelbags:
                out.extend(cb.fcurves)
    return out

def set_interp(obj, kind='BEZIER'):
    for fc in all_fcurves(obj):
        for kp in fc.keyframe_points:
            kp.interpolation = kind
