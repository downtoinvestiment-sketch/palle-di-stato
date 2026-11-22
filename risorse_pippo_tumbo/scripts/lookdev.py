"""Look 2.0: luci morbide, GI/AO, materiali procedurali, fili d'erba, 1080x1920. upgrade(scene) si applica a una scena gia' costruita."""
import bpy, bmesh, math, numpy as np

def _bsdf(m): return next((n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
def _tex(m, scale_big, scale_fine, c0, c1, bump=0.3, rough=None, bands=None, fine=0.45):
    """colore = miscela di due toni su rumore grande + fine; rilievo dal rumore fine (o a fasce per le tegole)."""
    nt = m.node_tree; b = _bsdf(m)
    if b is None: return
    N = nt.nodes.new; L = nt.links.new
    geo = N('ShaderNodeNewGeometry'); n1 = N('ShaderNodeTexNoise'); n1.inputs['Scale'].default_value = scale_big; n1.inputs['Detail'].default_value = 4
    n2 = N('ShaderNodeTexNoise'); n2.inputs['Scale'].default_value = scale_fine; n2.inputs['Detail'].default_value = 6
    L(geo.outputs['Position'], n1.inputs['Vector']); L(geo.outputs['Position'], n2.inputs['Vector'])
    mixf = N('ShaderNodeMath'); mixf.operation = 'ADD'; mixf.use_clamp = True; mul = N('ShaderNodeMath'); mul.operation = 'MULTIPLY'; mul.inputs[1].default_value = fine
    L(n2.outputs['Fac'], mul.inputs[0]); L(n1.outputs['Fac'], mixf.inputs[0]); L(mul.outputs[0], mixf.inputs[1])
    ramp = N('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].position = 0.45 + 0.25 * (fine > 0.6); ramp.color_ramp.elements[0].color = (*c0, 1); ramp.color_ramp.elements[1].position = 0.95 + 0.35 * (fine > 0.6); ramp.color_ramp.elements[1].color = (*c1, 1)
    L(mixf.outputs[0], ramp.inputs['Fac']); L(ramp.outputs['Color'], b.inputs['Base Color'])
    bp = N('ShaderNodeBump'); bp.inputs['Strength'].default_value = bump
    if bands:
        sep = N('ShaderNodeSeparateXYZ'); L(geo.outputs['Position'], sep.inputs[0]); w = N('ShaderNodeMath'); w.operation = 'MULTIPLY'; w.inputs[1].default_value = bands; fr = N('ShaderNodeMath'); fr.operation = 'FRACT'
        L(sep.outputs['Z'], w.inputs[0]); L(w.outputs[0], fr.inputs[0]); L(fr.outputs[0], bp.inputs['Height'])
    else: L(n2.outputs['Fac'], bp.inputs['Height'])
    L(bp.outputs['Normal'], b.inputs['Normal'])
    if rough is not None: b.inputs['Roughness'].default_value = rough
def _var(m, amt=0.12, scale=3.0, bump=0.15, bands=None):
    b = _bsdf(m)
    if b is None: return
    c = np.array(b.inputs['Base Color'].default_value[:3]); _tex(m, scale, scale * 9, tuple(c * (1 - amt)), tuple(np.clip(c * (1 + amt * 0.6), 0, 1)), bump, bands=bands)

def grass_blades(coll, x0, x1, y0, y1, dens=260, seed=1, skip=None):
    rg = np.random.default_rng(seed); n = int((x1 - x0) * (y1 - y0) * dens); bm = bmesh.new()
    xs = rg.uniform(x0, x1, n); ys = rg.uniform(y0, y1, n); hs = rg.uniform(0.05, 0.14, n); an = rg.uniform(0, math.pi, n); ln = rg.uniform(-0.05, 0.05, (n, 2))
    for i in range(n):
        if skip and skip(xs[i], ys[i]): continue
        w = 0.016; dx, dy = math.cos(an[i]) * w, math.sin(an[i]) * w
        v = [bm.verts.new((xs[i] - dx, ys[i] - dy, 0)), bm.verts.new((xs[i] + dx, ys[i] + dy, 0)), bm.verts.new((xs[i] + ln[i, 0], ys[i] + ln[i, 1], hs[i]))]
        f = bm.faces.new(v); f.material_index = i % 3
    me = bpy.data.meshes.new('FiliErba'); bm.to_mesh(me); bm.free(); o = bpy.data.objects.new('FiliErba', me); coll.objects.link(o)
    for k, c in enumerate([(0.20, 0.50, 0.08), (0.30, 0.62, 0.12), (0.14, 0.40, 0.06)]):
        m = bpy.data.materials.new('L2_blade%d' % k); m.use_nodes = True; b = _bsdf(m); b.inputs['Base Color'].default_value = (*c, 1); b.inputs['Roughness'].default_value = 0.8; me.materials.append(m)
    return o

def upgrade(scene, w=1080, h=1920, samples=24, blades=None, exposure=-0.15, rt=True, look='AgX - High Contrast', world=0.5, sun_e=5.5):
    r = scene.render; r.resolution_x = w; r.resolution_y = h; r.resolution_percentage = 100
    e = scene.eevee; e.taa_render_samples = samples; e.shadow_resolution_scale = 1.0; e.use_shadows = True; e.shadow_ray_count = 2; e.shadow_step_count = 6
    e.use_raytracing = rt; e.use_fast_gi = rt
    try: e.fast_gi_method = 'GLOBAL_ILLUMINATION'; e.fast_gi_distance = 4.0
    except Exception as ex: print('gi', ex)
    try: r.use_motion_blur = True; r.motion_blur_shutter = 0.1
    except Exception as ex: print('mb', ex)
    try: scene.view_settings.view_transform = 'AgX'; scene.view_settings.look = look
    except Exception as ex: print('view', ex)
    scene.view_settings.exposure = exposure
    sun = bpy.data.lights.get('Sun')
    if sun: sun.angle = math.radians(2.0); sun.energy = sun_e; sun.color = (1.0, 0.93, 0.80); sun.use_shadow_jitter = True
    for n in scene.world.node_tree.nodes:
        if n.type == 'BACKGROUND' and abs(n.inputs['Strength'].default_value - 0.7) < 0.01: n.inputs['Strength'].default_value = world
    M = bpy.data.materials; g = M.get
    if g('S_park'): _tex(g('S_park'), 0.22, 26.0, (0.10, 0.30, 0.05), (0.30, 0.58, 0.11), bump=1.0, rough=0.95, fine=0.9)
    if g('S_asphalt'): _tex(g('S_asphalt'), 0.6, 30.0, (0.035, 0.035, 0.04), (0.11, 0.11, 0.12), bump=0.6, rough=0.8)
    for nm in ('S_sidewalk', 'S_concrete', 'S_stone'):
        if g(nm): _var(g(nm), 0.15, 2.0, 0.35)
    for m in M:
        if m.name.startswith('S_wall') or m.name.startswith('S_tower'): _var(m, 0.07, 1.5, 0.12)
        elif m.name.startswith('S_roof'): _var(m, 0.22, 2.5, 0.9, bands=3.3)
        elif m.name.startswith('S_leaf') or m.name == 'S_hedge': _var(m, 0.35, 2.2, 1.0)
        elif m.name in ('S_wood', 'S_bark', 'S_frame'): _var(m, 0.15, 6.0, 0.4)
        elif m.name == 'S_window':
            b = _bsdf(m); b.inputs['Roughness'].default_value = 0.05
    if blades:
        coll = bpy.data.collections.get('Env') or scene.collection; grass_blades(coll, *blades)
