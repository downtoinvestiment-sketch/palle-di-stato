"""Test 008 - oggetti: Samantha la gallina, televisore col documentario, telecomando, uovo, ciotola, ventilatore industriale, scala esterna, cappellino da allenatore."""
import bpy, bmesh, math, numpy as np
from mathutils import Matrix
from common import *
import set004, props007
from set004 import MB, obj, cyl, ball_
from props007 import _sph, _cone, _bm_obj


def mats008():
    M = {}
    c = lambda n, col, **k: material(n, col, **k)
    M['feather'] = c('H_feather', (0.99, 0.98, 0.95), rough=0.8); M['comb'] = c('H_comb', (0.92, 0.08, 0.10), rough=0.5)
    M['beak'] = c('H_beak', (1.0, 0.62, 0.05), rough=0.5); M['eye'] = c('H_eye', (0.03, 0.03, 0.04), rough=0.3)
    M['card'] = c('H_card', (0.72, 0.52, 0.30), rough=0.9); M['tape'] = c('H_tape', (0.75, 0.75, 0.78), rough=0.4)
    M['tvbody'] = c('H_tvbody', (0.35, 0.22, 0.12), rough=0.6); M['tvdark'] = c('H_tvdark', (0.08, 0.08, 0.10), rough=0.5)
    M['screen'] = c('H_screen', (0.35, 0.70, 1.0), rough=0.3, emit=(0.30, 0.65, 1.0), emit_strength=1.6)
    M['falcon'] = c('H_falcon', (0.25, 0.16, 0.08), rough=0.6, emit=(0.2, 0.12, 0.05), emit_strength=0.4)
    M['crate'] = c('H_crate', (0.80, 0.62, 0.36), rough=0.85); M['egg'] = c('H_egg', (1.0, 0.96, 0.86), rough=0.35, spec=0.6)
    M['bowl'] = c('H_bowl', (0.90, 0.12, 0.12), rough=0.4, spec=0.6); M['kibble'] = c('H_kibble', (0.50, 0.30, 0.14), rough=0.8)
    M['fan'] = c('H_fan', (0.95, 0.75, 0.05), rough=0.4, spec=0.6); M['steel'] = c('H_steel', (0.55, 0.57, 0.62), rough=0.35, metallic=0.8)
    M['blade'] = c('H_blade', (0.20, 0.22, 0.26), rough=0.4); M['wood'] = c('H_wood', (0.72, 0.50, 0.26), rough=0.85); M['wood2'] = c('H_wood2', (0.58, 0.38, 0.19), rough=0.85)
    M['cap'] = c('H_cap', (0.10, 0.35, 0.95), rough=0.5); M['white'] = c('H_white', (0.98, 0.98, 0.98), rough=0.6); M['red'] = c('H_red', (0.92, 0.10, 0.10), rough=0.5)
    M['disc'] = material('H_disc', (0.8, 0.8, 0.85), rough=0.5)
    try:
        M['disc'].surface_render_method = 'BLENDED'; M['disc'].node_tree.nodes['Principled BSDF'].inputs['Alpha'].default_value = 0.25
    except Exception: pass
    return M


def chicken(coll, M, scale=1.4):
    """Samantha: rivolta a -Y, origine ai piedi. R = dict(root, body, head, wingL, wingR, cardL, cardR)."""
    R = {}
    root = empty('Samantha', (0, 0, 0), None, coll); root.scale = (scale, scale, scale); root.rotation_mode = 'XYZ'; R['root'] = root
    body = empty('SamCorpo', (0, 0, 0), root, coll); R['body'] = body
    bm = bmesh.new()
    _sph(bm, (0, 0.02, 0.24), 0.17, (0.88, 1.2, 0.92), 0)
    _sph(bm, (0, -0.10, 0.30), 0.11, (0.9, 0.9, 1.25), 0)                       # petto/collo
    for k, (x, a) in enumerate(((0, 0.0), (-0.06, -0.25), (0.06, 0.25))):       # coda
        _sph(bm, (x, 0.24, 0.36 + 0.03 * (k == 0)), 0.07, (0.5, 0.9, 1.5), 0)
    for s in (-1, 1):
        _cone(bm, (s * 0.06, 0.02, 0.06), 0.014, 0.018, 0.13, 1, 8)
        _sph(bm, (s * 0.06, -0.02, 0.012), 0.045, (0.9, 1.5, 0.3), 1, 10, 6)
    me = _bm_obj('SamCorpoMesh', bm, [M['feather'], M['beak']], None)
    o = bpy.data.objects.new('SamCorpoM', me); o.parent = body; coll.objects.link(o)
    head = empty('SamTesta', (0, -0.13, 0.43), body, coll); R['head'] = head
    bm = bmesh.new()
    _sph(bm, (0, -0.02, 0.05), 0.085, (1, 1, 1), 0)
    for k, (y, r) in enumerate(((-0.06, 0.03), (-0.015, 0.038), (0.03, 0.03))): _sph(bm, (0, y, 0.135 + 0.01 * (k == 1)), r, (0.5, 1, 1.2), 1, 10, 6)   # cresta
    _sph(bm, (0, -0.085, -0.015), 0.028, (0.6, 0.8, 1.5), 1, 10, 6)                                                                              # bargiglio
    _cone(bm, (0, -0.125, 0.045), 0.032, 0.002, 0.09, 2, 10, Matrix.Rotation(math.pi / 2, 4, 'X'))
    for s in (-1, 1):
        _sph(bm, (s * 0.062, -0.055, 0.075), 0.026, (1, 1, 1), 4, 10, 6); _sph(bm, (s * 0.074, -0.068, 0.078), 0.014, (1, 1, 1), 3, 8, 6)
    me = _bm_obj('SamTestaMesh', bm, [M['feather'], M['comb'], M['beak'], M['eye'], M['white']], None)
    o = bpy.data.objects.new('SamTestaM', me); o.parent = head; coll.objects.link(o)
    for s, nm in ((-1, 'L'), (1, 'R')):
        wg = empty('SamAla' + nm, (s * 0.13, 0.02, 0.30), body, coll); R['wing' + nm] = wg
        bm = bmesh.new(); _sph(bm, (s * 0.15, 0.03, 0), 0.16, (1.0, 0.75, 0.22), 0); _sph(bm, (s * 0.26, 0.07, 0), 0.09, (1.0, 0.9, 0.2), 0)
        me = _bm_obj('SamAlaMesh' + nm, bm, [M['feather']], None); o = bpy.data.objects.new('SamAlaM' + nm, me); o.parent = wg; coll.objects.link(o)
        cb = MB([M['card'], M['tape']])
        cb.box((s * 0.30, 0.04, 0.03), (0.62, 0.34, 0.015), 0); cb.box((s * 0.52, 0.10, 0.03), (0.22, 0.30, 0.015), 0, rz=-s * 0.5)
        cb.box((s * 0.10, 0.04, 0.045), (0.08, 0.36, 0.01), 1)
        c_ = cb.build('SamCartone' + nm, coll); c_.parent = wg; R['card' + nm] = c_
    return R


def tv(coll, M):
    """vecchio televisore su una cassetta, schermo verso -Y. Restituisce (root, falco, [ali del falco])."""
    root = empty('Televisore', (0, 0, 0), None, coll)
    mb = MB([M['crate'], M['tvbody'], M['tvdark'], M['steel'], M['wood2']])
    mb.box((0, 0, 0.25), (0.9, 0.6, 0.5), 0)
    for z in (0.12, 0.38): mb.box((0, -0.305, z), (0.9, 0.02, 0.05), 4)
    mb.box((0, 0, 0.92), (1.05, 0.55, 0.84), 1); mb.box((-0.08, -0.28, 0.94), (0.78, 0.03, 0.66), 2)
    for k in range(2): mb.box((0.42, -0.285, 1.12 - 0.2 * k), (0.09, 0.03, 0.09), 3)
    mb.box((-0.2, 0, 1.62), (0.02, 0.02, 0.6), 3, rx=0.0, rz=0.0); mb.box((0.2, 0, 1.62), (0.02, 0.02, 0.6), 3)
    o = mb.build('TelevisoreCorpo', coll); o.parent = root
    obj('TelevisoreSchermo', set004.box_c(), (-0.08, -0.30, 0.94), (0.70, 0.02, 0.58), M['screen'], coll, parent=root)
    fal = empty('Falco', (-0.08, -0.325, 0.96), root, coll)
    obj('FalcoCorpo', set004.box_c(), (0, 0, 0), (0.10, 0.012, 0.06), M['falcon'], coll, parent=fal)
    obj('FalcoTesta', set004.box_c(), (0.07, 0, 0.02), (0.05, 0.012, 0.045), M['falcon'], coll, parent=fal)
    wings = []
    for s in (-1, 1):
        w = empty('FalcoAla', (0, 0, 0.02), fal, coll); obj('FalcoAlaP', set004.box_c(), (-0.02, 0, 0.10), (0.11, 0.012, 0.20), M['falcon'], coll, parent=w); wings.append(w)
    return root, fal, wings


def remote(coll, M):
    mb = MB([M['tvdark'], M['red'], M['white']])
    mb.box((0, 0, 0.02), (0.09, 0.26, 0.04), 0); mb.box((0, -0.09, 0.045), (0.035, 0.035, 0.012), 1)
    for k in range(6): mb.box((-0.02 + 0.04 * (k % 2), -0.03 + 0.04 * (k // 2), 0.045), (0.022, 0.022, 0.01), 2)
    return mb.build('Telecomando', coll)


def bowl(coll, M):
    """ciotola rossa di Tumbo con le crocchette. Restituisce root."""
    root = empty('Ciotola', (0, 0, 0), None, coll)
    cyl('CiotolaBase', 0.30, 0.16, (0, 0, 0.08), M['bowl'], coll, parent=root); cyl('CiotolaBordo', 0.33, 0.04, (0, 0, 0.16), M['bowl'], coll, parent=root)
    cyl('CiotolaCibo', 0.27, 0.03, (0, 0, 0.175), M['kibble'], coll, parent=root)
    obj('CiotolaOsso', set004.box_c(), (0, -0.305, 0.08), (0.16, 0.02, 0.05), M['white'], coll, parent=root)
    return root


def fan(coll, M, R=0.85):
    """ventilatore industriale: soffia verso +X. Restituisce (root, pale)."""
    root = empty('Ventilatore', (0, 0, 0), None, coll)
    mb = MB([M['fan'], M['steel'], M['tvdark']])
    for s in (-1, 1): mb.box((0, s * 0.55, 0.55), (0.10, 0.08, 1.1), 0, rx=-s * 0.22); mb.box((0, s * 0.72, 0.05), (0.9, 0.12, 0.10), 0)
    n = 20
    for k in range(n):                                             # gabbia: due anelli e raggi
        a = 2 * math.pi * (k + 0.5) / n
        for x in (-0.16, 0.16): mb.box((x, R * math.cos(a), 1.15 + R * math.sin(a)), (0.05, 2 * math.pi * R / n * 1.05, 0.05), 0, rx=a + math.pi / 2)
        if k % 2 == 0: mb.box((0.18, 0.5 * R * math.cos(a), 1.15 + 0.5 * R * math.sin(a)), (0.02, R, 0.02), 1, rx=a)
    for k in range(8):
        a = 2 * math.pi * k / 8; mb.box((0, R * math.cos(a), 1.15 + R * math.sin(a)), (0.34, 0.04, 0.04), 0, rx=a)
    mb.box((-0.22, 0, 1.15), (0.26, 0.30, 0.30), 2); mb.box((-0.42, 0, 0.85), (0.14, 0.22, 0.34), 0)
    o = mb.build('VentilatoreGabbia', coll); o.parent = root
    blades = empty('VentilatorePale', (0.0, 0, 1.15), root, coll)
    for k in range(4): obj('Pala', set004.box_c(), (0, 0.38 * math.cos(k * math.pi / 2), 0.38 * math.sin(k * math.pi / 2)), (0.03, 0.72, 0.22), M['blade'], coll, rot=(k * math.pi / 2 + 0.0, 0.35, 0), parent=blades)
    shape('VentilatoreDisco', 'cyl:%.2f:0.02' % (R * 0.93), (0.02, 0, 0), (1, 1, 1), (0, math.pi / 2, 0), blades, M['disc'], coll)
    return root, blades


def stairs(coll, M, x0, x1, y, H, width=1.1, n=16):
    """scala esterna di legno che sale lungo X da (x0, y, 0) a (x1, y, H), con pianerottolo e ringhiera. Restituisce (oggetto, lista dei gradini (x, z))."""
    mb = MB([M['wood'], M['wood2'], M['white']]); steps = []
    for k in range(n):
        x = x0 + (x1 - x0) * (k + 0.5) / n; z = H * (k + 1) / n
        mb.box((x, y, z - 0.03), ((x1 - x0) / n + 0.04, width, 0.06), k % 2); steps.append((x, z))
        if k % 3 == 0: mb.box((x, y + width / 2 - 0.03, z / 2), (0.08, 0.08, z), 1); mb.box((x, y - width / 2 + 0.03, z / 2), (0.08, 0.08, z), 1)
    L = math.hypot(x1 - x0, H); ang = math.atan2(H, x1 - x0)
    for s in (-1, 1):
        for k in range(0, n + 1, 2):
            x = x0 + (x1 - x0) * k / n; z = H * k / n; mb.box((x, y + s * (width / 2 - 0.03), z + 0.5), (0.05, 0.05, 1.0), 2)
    # pianerottolo
    px0, px1 = x1, x1 + 3.2
    mb.box(((px0 + px1) / 2, y, H - 0.04), (px1 - px0, width + 0.5, 0.08), 0)
    for x in (px0 + 0.1, px1 - 0.1):
        for s in (-1, 1): mb.box((x, y + s * (width / 2 + 0.15), H / 2), (0.10, 0.10, H), 1)
    for x in np.arange(px0 + 0.1, px1, 0.5): mb.box((x, y + width / 2 + 0.2, H + 0.5), (0.05, 0.05, 1.0), 2)
    mb.box(((px0 + px1) / 2, y + width / 2 + 0.2, H + 1.0), (px1 - px0, 0.07, 0.07), 2)
    o = mb.build('ScalaEsterna', coll)
    for s in (-1, 1):
        obj('Corrimano', set004.box_c(), ((x0 + x1) / 2, y + s * (width / 2 - 0.03), H / 2 + 1.0), (0.07, 0.07, L), M['white'], coll, rot=(0, math.pi / 2 - ang, 0))
    return o, steps


def cap(coll, M, head, cz=0.52, r=0.42):
    """cappellino da allenatore con visiera, figlio della testa di Pippo."""
    root = empty('Cappellino', (0, 0.0, cz), head, coll)
    nu, nv = 20, 8; V = []; F = []
    for i in range(nv + 1):
        th = (math.pi / 2) * i / nv
        for k in range(nu): ph = 2 * math.pi * k / nu; V.append((r * math.sin(th) * math.cos(ph), r * math.sin(th) * math.sin(ph) * 1.05, 0.62 * r * math.cos(th)))
    for i in range(nv):
        for k in range(nu): F.append((i * nu + k, (i + 1) * nu + k, (i + 1) * nu + (k + 1) % nu, i * nu + (k + 1) % nu))
    me = bpy.data.meshes.new('CappellinoM'); me.from_pydata(V, [], F); me.materials.append(M['cap']); me.polygons.foreach_set('use_smooth', [True] * len(F)); me.update()
    o = bpy.data.objects.new('CappellinoCalotta', me); o.parent = root; coll.objects.link(o)
    obj('CappellinoVisiera', set004.box_c(), (0, -r - 0.10, 0.02), (0.50, 0.36, 0.03), M['cap'], coll, rot=(-0.12, 0, 0), parent=root)
    obj('CappellinoBottone', set004.box_c(), (0, 0, 0.62 * r), (0.06, 0.06, 0.03), M['white'], coll, parent=root)
    return root
