"""Test 016 - IL SECONDO PARTO: cocomero (senza faccia), camion dei pompieri, pianoforte, busta di patatine, cartella clinica, porta, scotch."""
import math, bpy, numpy as np
from common import material, shape, empty, shared_mesh
import set004
from set004 import MB, obj, cyl, ball_, bx
from props007 import text_obj
PI = math.pi

def mats016b():
    c = lambda n, col, **k: material('P16b_' + n, col, **k); M = {}
    M['red'] = c('red', (0.85, 0.06, 0.04), rough=0.35); M['redd'] = c('redd', (0.55, 0.04, 0.03), rough=0.45); M['chrome'] = c('chrome', (0.8, 0.82, 0.85), rough=0.2, metallic=0.9)
    M['white'] = c('white', (0.96, 0.96, 0.94), rough=0.5); M['yellow'] = c('yellow', (1.0, 0.82, 0.1), rough=0.4); M['tyre'] = c('tyre', (0.04, 0.04, 0.05), rough=0.85)
    M['glass'] = c('glass', (0.4, 0.6, 0.75), rough=0.05, spec=1.0); M['sirr'] = c('sirr', (1.0, 0.1, 0.05), rough=0.3, emit=(1.0, 0.08, 0.04), emit_strength=8.0)
    M['sirb'] = c('sirb', (0.1, 0.3, 1.0), rough=0.3, emit=(0.1, 0.3, 1.0), emit_strength=8.0)
    M['piano'] = c('piano', (0.02, 0.02, 0.025), rough=0.12, coat=1.0); M['keyw'] = c('keyw', (0.97, 0.96, 0.92), rough=0.3); M['keyb'] = c('keyb', (0.02, 0.02, 0.02), rough=0.3)
    M['gold'] = c('gold', (1.0, 0.75, 0.25), rough=0.25, metallic=0.9)
    M['foil'] = c('foil', (1.0, 0.78, 0.08), rough=0.25, metallic=0.6); M['foilr'] = c('foilr', (0.9, 0.12, 0.08), rough=0.3); M['chip'] = c('chip', (0.98, 0.80, 0.35), rough=0.6)
    M['board'] = c('board', (0.55, 0.36, 0.18), rough=0.6); M['paper'] = c('paper', (0.98, 0.97, 0.93), rough=0.8); M['ink'] = c('ink', (0.05, 0.05, 0.08), rough=0.6)
    M['door'] = c('door', (0.55, 0.75, 0.85), rough=0.5); M['sign'] = c('sign', (0.1, 0.6, 0.25), rough=0.4, emit=(0.1, 0.8, 0.3), emit_strength=1.2)
    M['tape'] = c('tape', (0.85, 0.72, 0.45), rough=0.35, spec=0.6); M['card'] = c('card', (0.72, 0.56, 0.36), rough=0.9)
    M['melon'] = melon_mat('P16b_melon')
    return M

def melon_mat(name):
    """buccia di cocomero: strisce verdi scure e chiare lungo l'asse, un po' mosse."""
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']
    tc = nt.nodes.new('ShaderNodeTexCoord'); wv = nt.nodes.new('ShaderNodeTexWave'); wv.wave_type = 'BANDS'; wv.bands_direction = 'X'
    wv.inputs['Scale'].default_value = 2.5; wv.inputs['Distortion'].default_value = 3.0; wv.inputs['Detail'].default_value = 3.0
    sep = nt.nodes.new('ShaderNodeSeparateXYZ'); ang = nt.nodes.new('ShaderNodeMath'); ang.operation = 'ARCTAN2'
    comb = nt.nodes.new('ShaderNodeCombineXYZ'); mul = nt.nodes.new('ShaderNodeMath'); mul.operation = 'MULTIPLY'; mul.inputs[1].default_value = 1.6
    nt.links.new(tc.outputs['Object'], sep.inputs[0]); nt.links.new(sep.outputs['Y'], ang.inputs[0]); nt.links.new(sep.outputs['X'], ang.inputs[1])
    nt.links.new(ang.outputs[0], mul.inputs[0]); nt.links.new(mul.outputs[0], comb.inputs['X']); nt.links.new(sep.outputs['Z'], comb.inputs['Y'])
    nt.links.new(comb.outputs[0], wv.inputs['Vector'])
    rp = nt.nodes.new('ShaderNodeValToRGB'); rp.color_ramp.elements[0].position = 0.46; rp.color_ramp.elements[0].color = (0.015, 0.09, 0.015, 1)
    rp.color_ramp.elements[1].position = 0.54; rp.color_ramp.elements[1].color = (0.36, 0.70, 0.18, 1)
    nt.links.new(wv.outputs['Fac'], rp.inputs['Fac']); nt.links.new(rp.outputs['Color'], b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = 0.28
    try: b.inputs['Coat Weight'].default_value = 0.4
    except Exception: pass
    return m

def watermelon(coll, M, r=0.3, name='Cocomero'):
    """cocomero liscio, senza faccia: origine al centro, asse lungo Z."""
    g = empty(name, (0, 0, 0), None, coll)
    o = ball_(name + 'Buccia', 1.0, (0, 0, 0), M['melon'], coll, parent=g, sc=(r, r, r * 1.25))
    ball_(name + 'Picciolo', 0.03, (0, 0, r * 1.24), M['board'], coll, parent=g, sc=(1, 1, 1.4))
    return g

def firetruck(coll, M, L=2.6):
    """camion dei pompieri: muso verso -Y, origine a terra. Restituisce dict(root, lights=[(rossa, blu)], ladder)."""
    F = {}; r = F['root'] = empty('CamionPompieri', (0, 0, 0), None, coll); s = L / 2.6
    mb = MB([M['red'], M['redd'], M['chrome'], M['white'], M['glass'], M['yellow'], M['tyre']])
    mb.b2((-0.55 * s, -1.3 * s, 0.25 * s), (0.55 * s, 1.3 * s, 0.95 * s), 0); mb.b2((-0.55 * s, -1.3 * s, 0.95 * s), (0.55 * s, -0.55 * s, 1.5 * s), 0)
    mb.b2((-0.5 * s, -1.32 * s, 1.05 * s), (0.5 * s, -1.28 * s, 1.4 * s), 4); mb.b2((-0.57 * s, -1.2 * s, 1.05 * s), (0.57 * s, -0.7 * s, 1.4 * s), 4)
    mb.b2((-0.57 * s, -1.31 * s, 0.6 * s), (0.57 * s, 1.31 * s, 0.68 * s), 3); mb.b2((-0.56 * s, -1.34 * s, 0.3 * s), (0.56 * s, -1.3 * s, 0.5 * s), 2)
    mb.b2((-0.5 * s, -0.45 * s, 0.95 * s), (0.5 * s, 1.25 * s, 1.0 * s), 1)
    for k in range(5): mb.b2((-0.56 * s, -0.4 * s + k * 0.33 * s, 0.3 * s), (-0.555 * s, -0.25 * s + k * 0.33 * s, 0.9 * s), 1)
    o = mb.build('CamionCorpo', coll); o.parent = r
    for sx in (-1, 1):
        for y in (-0.85, 0.75): cyl('CamionRuota', 0.26 * s, 0.22 * s, (sx * 0.5 * s, y * s, 0.26 * s), M['tyre'], coll, rot=(0, PI / 2, 0), parent=r)
    ld = F['ladder'] = empty('CamionScala', (0, 1.1 * s, 1.05 * s), r, coll)
    ms = MB([M['chrome']])
    for sx in (-0.18, 0.18): ms.b2((sx * s - 0.025 * s, -1.6 * s, 0), (sx * s + 0.025 * s, 0.0, 0.05 * s), 0)
    for k in range(9): ms.b2((-0.18 * s, -1.55 * s + k * 0.18 * s, 0), (0.18 * s, -1.53 * s + k * 0.18 * s, 0.04 * s), 0)
    ol = ms.build('CamionScalaGeo', coll); ol.parent = ld
    F['lights'] = []
    lr = obj('CamionSirR', set004.box_c(), (-0.2 * s, -0.95 * s, 1.56 * s), (0.3 * s, 0.18 * s, 0.12 * s), M['sirr'], coll, parent=r)
    lb = obj('CamionSirB', set004.box_c(), (0.2 * s, -0.95 * s, 1.56 * s), (0.3 * s, 0.18 * s, 0.12 * s), M['sirb'], coll, parent=r)
    F['lights'] = (lr, lb)
    return F

def piano(coll, M):
    """pianoforte verticale: tastiera verso -Y, origine a terra."""
    r = empty('Pianoforte', (0, 0, 0), None, coll)
    mb = MB([M['piano'], M['keyw'], M['keyb'], M['gold']])
    mb.b2((-0.75, -0.05, 0.0), (0.75, 0.35, 1.3), 0); mb.b2((-0.75, -0.42, 0.68), (0.75, -0.05, 0.74), 0); mb.b2((-0.75, -0.42, 0.0), (-0.68, -0.05, 0.74), 0); mb.b2((0.68, -0.42, 0.0), (0.75, -0.05, 0.74), 0)
    mb.b2((-0.68, -0.40, 0.74), (0.68, -0.12, 0.78), 1)
    for k in range(36):
        if k % 7 in (2, 6): continue
        x = -0.66 + k * 0.037; mb.b2((x, -0.30, 0.78), (x + 0.02, -0.12, 0.81), 2)
    mb.b2((-0.75, -0.08, 0.95), (0.75, -0.05, 1.25), 0); mb.b2((-0.3, -0.1, 1.05), (0.3, -0.08, 1.12), 3)
    mb.b2((-0.5, -0.45, 0.05), (-0.42, -0.25, 0.1), 3); mb.b2((0.42, -0.45, 0.05), (0.5, -0.25, 0.1), 3)
    o = mb.build('PianoGeo', coll); o.parent = r
    return r

def chips_bag(coll, M, parent=None, loc=(0, 0, 0), s=1.0):
    g = empty('Patatine', loc, parent, coll); g.scale = (s, s, s)
    obj('PatBusta', set004.box_c(), (0, 0, 0.16), (0.24, 0.10, 0.32), M['foil'], coll, parent=g); obj('PatBanda', set004.box_c(), (0, -0.052, 0.18), (0.25, 0.01, 0.1), M['foilr'], coll, parent=g)
    for k, (dx, dz) in enumerate(((-0.05, 0.33), (0.04, 0.35), (0.0, 0.37))): ball_('PatChip', 1.0, (dx, 0, dz), M['chip'], coll, parent=g, sc=(0.05, 0.012, 0.035))
    return g

def clipboard(coll, M, parent=None, loc=(0, 0, 0), word='NORMALE'):
    """cartella clinica: faccia scritta verso -Y."""
    g = empty('Cartella', loc, parent, coll)
    obj('CartTavola', set004.box_c(), (0, 0, 0), (0.30, 0.02, 0.40), M['board'], coll, parent=g); obj('CartFoglio', set004.box_c(), (0, -0.012, -0.02), (0.26, 0.005, 0.33), M['paper'], coll, parent=g)
    obj('CartMolla', set004.box_c(), (0, -0.02, 0.18), (0.12, 0.02, 0.04), M['chrome'], coll, parent=g)
    for k in range(3): obj('CartRiga', set004.box_c(), (0, -0.016, 0.1 - 0.05 * k), (0.2, 0.003, 0.008), M['ink'], coll, parent=g)
    text_obj(coll, 'CartScritta', word, 0.055, M['ink'], (0, -0.02, -0.08), parent=g)
    return g

def door(coll, M, loc, rotz=0.0, label='USCITA'):
    """porta su una parete: pivot del battente sul lato sinistro. Restituisce il pivot (ruota su Z per aprire)."""
    g = empty('PortaTelaio', loc, None, coll); g.rotation_euler = (0, 0, rotz)
    mb = MB([M['white']]); mb.b2((-0.62, -0.06, 0), (-0.55, 0.06, 2.25), 0); mb.b2((0.55, -0.06, 0), (0.62, 0.06, 2.25), 0); mb.b2((-0.62, -0.06, 2.18), (0.62, 0.06, 2.25), 0)
    o = mb.build('PortaCornice', coll); o.parent = g
    pv = empty('PortaPivot', (-0.55, 0, 0), g, coll)
    obj('PortaBattente', set004.box_c(), (0.55, 0, 1.09), (1.1, 0.05, 2.18), M['door'], coll, parent=pv); ball_('PortaManiglia', 0.035, (1.0, -0.05, 1.05), M['chrome'], coll, parent=pv)
    sg = obj('PortaInsegna', set004.box_c(), (0, -0.04, 2.45), (0.7, 0.03, 0.22), M['sign'], coll, parent=g)
    text_obj(coll, 'PortaInsegnaT', label, 0.13, M['white'], (0, -0.065, 2.41), parent=g)
    return pv

def tape_patch(coll, M, parent, loc, rot=(0, 0, 0), size=(0.14, 0.01, 0.035)):
    return obj('Scotch', set004.box_c(), loc, size, M['tape'], coll, rot=rot, parent=parent)

def room_shell(coll, A13, W15, x0):
    """sala parto vuota (senza letto): pavimento, pareti, soffitto, croce rossa. Si arreda con i modelli della libreria."""
    mb = MB([W15['cwall'], A13['hfloor'], W15['white']])
    mb.b2((x0 - 4.1, -7.5, -0.12), (x0 + 6.6, 3.1, 0.0), 1); mb.b2((x0 - 4.0, 3.0, 0.0), (x0 + 6.6, 3.1, 3.3), 0); mb.b2((x0 - 4.1, -7.5, 0.0), (x0 - 4.0, 3.1, 3.3), 0)
    mb.b2((x0 + 6.5, -7.5, 0.0), (x0 + 6.6, 3.1, 3.3), 0); mb.b2((x0 - 4.1, -7.6, 0.0), (x0 + 6.6, -7.5, 3.3), 0); mb.b2((x0 - 4.1, -7.6, 3.2), (x0 + 6.6, 3.1, 3.3), 2)
    mb.b2((x0 - 4.0, 2.95, 0.0), (x0 + 6.5, 2.97, 0.12), 2)
    o = mb.build('StanzaParto', coll)
    obj('CroceH1', set004.box_c(), (x0 + 1.6, 2.98, 2.5), (0.6, 0.04, 0.18), A13['cross'], coll); obj('CroceH2', set004.box_c(), (x0 + 1.6, 2.98, 2.5), (0.18, 0.04, 0.6), A13['cross'], coll)
    return o

def corridor_shell(coll, W15, x0):
    """corridoio vuoto (senza sedie): pavimento, pareti, soffitto, porta 'SALA PARTO'."""
    mb = MB([W15['cwall'], W15['cfloor'], W15['white'], W15['door']])
    mb.b2((x0 - 6, -4, -0.1), (x0 + 6, 1.6, 0.0), 1); mb.b2((x0 - 6, 1.6, 0), (x0 + 6, 1.7, 3.0), 0); mb.b2((x0 - 6.1, -4, 0), (x0 - 6.0, 1.7, 3.0), 0)
    mb.b2((x0 + 1.4, 1.55, 0), (x0 + 3.0, 1.62, 2.3), 3); mb.b2((x0 - 6.2, -4.2, 3.0), (x0 + 6.2, 1.8, 3.1), 2); mb.b2((x0 - 6, 1.56, 0), (x0 + 6, 1.6, 0.12), 2)
    mb.build('Corridoio', coll)
    sg = empty('CartelloSalaParto', (x0 + 2.2, 1.55, 2.55), None, coll); obj('CartSP', set004.box_c(), (0, 0, 0), (1.5, 0.04, 0.35), W15['sign'], coll, parent=sg)
    text_obj(coll, 'CartSPTxt', 'SALA PARTO', 0.18, W15['red'], (0, -0.03, -0.06), parent=sg)
    obj('LuceRossaSP', set004.box_c(), (x0 + 2.2, 1.55, 2.85), (0.3, 0.06, 0.12), W15['red'], coll)

def kplace(A, aid, coll, x, y, z=0.0, s=2.3, rot=0.0, center=True, name=None):
    """mette un modello Kenney con scala fissa; center=True: (x, y) e' il centro della sua base (i mobili Kenney hanno l'origine in un angolo)."""
    from mathutils import Vector
    r = A.modello(aid, collezione=coll, nome=name); r.scale = (s, s, s); r.rotation_euler[2] = math.radians(rot); r.location = (0, 0, 0)
    bpy.context.view_layer.update(); pts = [o.matrix_world @ Vector(c) for o in r.children_recursive if o.type == 'MESH' for c in o.bound_box]
    mn = [min(p[i] for p in pts) for i in range(3)]; mx = [max(p[i] for p in pts) for i in range(3)]
    if center: r.location = (x - (mn[0] + mx[0]) / 2, y - (mn[1] + mx[1]) / 2, z - mn[2])
    else: r.location = (x, y, z)
    bpy.context.view_layer.update()
    return r, (mx[0] - mn[0], mx[1] - mn[1], mx[2] - mn[2])
