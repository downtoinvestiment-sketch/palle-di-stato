"""Test 021 - L'ETCIU': il sole realistico tirato giu' sul quartiere, il quartiere in fiamme, le comparse che scappano bruciando.
sole(coll, centro, raggio, tipo): tipo 'A' sole vero (granuli, macchie, bordo piu' scuro, corona), 'B' sole che ribolle (piu' rosso, protuberanze ad arco),
'C' sole accecante (nucleo quasi bianco, raggi). Restituisce dict(radice, corpo, corona, materiale, luce).
incendio(coll, posti, scala): fiamme 3D + immagini di fiamme e fumo nero sopra ogni posto. cielo_rosso(world): il cielo diventa arancio e fumoso."""
import math, random, bpy, bmesh
from mathutils import Vector
from common import material, empty
PI = math.pi

def _sfera(nome, r, mat, coll, seg=64, ring=32):
    me = bpy.data.meshes.new(nome); bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=ring, radius=r); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    me.materials.append(mat); o = bpy.data.objects.new(nome, me); coll.objects.link(o); return o

def mat_sole(nome, tipo='A', forza=2.5):
    """superficie del sole: granuli (celle chiare con bordi scuri), celle grandi che ribollono (W del rumore da animare),
    macchie scure, bordo piu' scuro e piu' rosso. La luce cambia con la granulazione: le celle calde brillano di piu'."""
    m = bpy.data.materials.new(nome); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear(); L = nt.links.new
    def N(t, **kw):
        n = nt.nodes.new(t)
        for k, v in kw.items(): setattr(n, k, v)
        return n
    def M_(op, a, b, c=None):
        n = N('ShaderNodeMath', operation=op)
        for i, x in enumerate((a, b, c)):
            if x is None: continue
            if isinstance(x, (int, float)): n.inputs[i].default_value = x
            else: L(x, n.inputs[i])
        return n.outputs[0]
    out = N('ShaderNodeOutputMaterial'); em = N('ShaderNodeEmission'); L(em.outputs[0], out.inputs[0]); tc = N('ShaderNodeTexCoord')
    nz = N('ShaderNodeTexNoise', noise_dimensions='4D', name='PT_ribolle'); nz.inputs['Scale'].default_value = 2.2; nz.inputs['Detail'].default_value = 6; nz.inputs['Roughness'].default_value = 0.55
    L(tc.outputs['Object'], nz.inputs['Vector'])
    wp = N('ShaderNodeTexNoise', noise_dimensions='3D'); wp.inputs['Scale'].default_value = 1.4; wp.inputs['Detail'].default_value = 2; L(tc.outputs['Object'], wp.inputs['Vector'])
    vin = N('ShaderNodeVectorMath', operation='MULTIPLY_ADD'); L(wp.outputs['Color'], vin.inputs[0]); vin.inputs[1].default_value = (0.25, 0.25, 0.25); L(tc.outputs['Object'], vin.inputs[2])
    vo = N('ShaderNodeTexVoronoi', voronoi_dimensions='4D', feature='SMOOTH_F1', name='PT_granuli'); vo.inputs['Scale'].default_value = 7.0; L(vin.outputs[0], vo.inputs['Vector'])
    vo.inputs['Smoothness'].default_value = 0.6
    gran = M_('SUBTRACT', 1.0, M_('MULTIPLY', vo.outputs['Distance'], 1.6))                              # 1 al centro della cella, scuro nei bordi
    gran = M_('POWER', M_('MAXIMUM', gran, 0.0), 1.5)
    v = M_('MULTIPLY_ADD', nz.outputs['Fac'], 0.75, M_('MULTIPLY', gran, 0.35))                             # 0.2..0.9 circa
    sp = N('ShaderNodeTexNoise'); sp.inputs['Scale'].default_value = 0.9; sp.inputs['Detail'].default_value = 4; L(tc.outputs['Object'], sp.inputs['Vector'])
    spr = N('ShaderNodeMapRange'); L(sp.outputs['Fac'], spr.inputs['Value']); spr.inputs['From Min'].default_value = 0.67; spr.inputs['From Max'].default_value = 0.71
    spr.inputs['To Min'].default_value = 0.0; spr.inputs['To Max'].default_value = 0.45 if tipo != 'C' else 0.25
    v = M_('SUBTRACT', v, spr.outputs[0])                                                                   # macchie solari
    lw = N('ShaderNodeLayerWeight'); lw.inputs['Blend'].default_value = 0.5
    limbo = M_('POWER', M_('SUBTRACT', 1.0, lw.outputs['Facing']), 0.55)                                    # 1 al centro, 0 sul bordo
    v = M_('MULTIPLY', v, M_('MULTIPLY_ADD', limbo, 0.55, 0.45))
    rp = N('ShaderNodeValToRGB'); L(v, rp.inputs['Fac']); E = rp.color_ramp.elements
    pal = {'A': [(0.18, (0.25, 0.01, 0.0)), (0.32, (0.8, 0.09, 0.0)), (0.45, (1.0, 0.3, 0.01)), (0.56, (1.0, 0.55, 0.05)), (0.68, (1.0, 0.8, 0.3))],
           'B': [(0.18, (0.20, 0.01, 0.0)), (0.32, (0.65, 0.05, 0.0)), (0.45, (0.95, 0.18, 0.01)), (0.56, (1.0, 0.38, 0.03)), (0.70, (1.0, 0.6, 0.15))],
           'C': [(0.18, (0.7, 0.18, 0.02)), (0.32, (1.0, 0.5, 0.1)), (0.45, (1.0, 0.78, 0.35)), (0.56, (1.0, 0.92, 0.65)), (0.68, (1.0, 1.0, 0.92))]}[tipo]
    E[0].position, E[0].color = pal[0][0], pal[0][1] + (1,); E[1].position, E[1].color = pal[-1][0], pal[-1][1] + (1,)
    for p_, c_ in pal[1:-1]: e_ = E.new(p_); e_.color = c_ + (1,)
    L(rp.outputs['Color'], em.inputs['Color'])
    L(M_('MULTIPLY', M_('POWER', M_('MAXIMUM', v, 0.05), 1.6), forza * 1.5), em.inputs['Strength'])       # le zone calde brillano di piu'
    return m

def mat_alone(nome, colore=(1.0, 0.45, 0.06), forza=2.0, esponente=3.0):
    """alone del sole su un disco rivolto alla camera: luce che si somma, forte vicino al sole e che si spegne verso il bordo."""
    m = bpy.data.materials.new(nome); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear(); L = nt.links.new
    try: m.surface_render_method = 'BLENDED'
    except Exception: m.blend_method = 'BLEND'
    out = nt.nodes.new('ShaderNodeOutputMaterial'); add = nt.nodes.new('ShaderNodeAddShader'); tr = nt.nodes.new('ShaderNodeBsdfTransparent'); em = nt.nodes.new('ShaderNodeEmission')
    em.inputs['Color'].default_value = colore + (1,)
    tc = nt.nodes.new('ShaderNodeTexCoord'); gr = nt.nodes.new('ShaderNodeTexGradient'); gr.gradient_type = 'SPHERICAL'; L(tc.outputs['Object'], gr.inputs['Vector'])
    pw = nt.nodes.new('ShaderNodeMath'); pw.operation = 'POWER'; L(gr.outputs['Fac'], pw.inputs[0]); pw.inputs[1].default_value = esponente
    mu = nt.nodes.new('ShaderNodeMath'); mu.operation = 'MULTIPLY'; L(pw.outputs[0], mu.inputs[0]); mu.inputs[1].default_value = forza
    L(mu.outputs[0], em.inputs['Strength']); L(tr.outputs[0], add.inputs[0]); L(em.outputs[0], add.inputs[1]); L(add.outputs[0], out.inputs['Surface'])
    return m

def _alone(nome, R, mat, coll):
    """disco quadrato di lato 2R (coordinate oggetto da -1 a 1) che guarda sempre la camera."""
    me = bpy.data.meshes.new(nome); me.from_pydata([(-1, -1, 0), (1, -1, 0), (1, 1, 0), (-1, 1, 0)], [], [(0, 1, 2, 3)]); me.update(); me.materials.append(mat)
    o = bpy.data.objects.new(nome, me); coll.objects.link(o); o.scale = (R, R, R); o.visible_shadow = False
    cam = bpy.context.scene.camera
    if cam:
        c = o.constraints.new('COPY_ROTATION'); c.target = cam
    return o

def sole(coll, centro, raggio, tipo='A', luce=60000.0, forza=None, alone=1.0):
    D = {}; r = D['radice'] = empty('SoleVero', centro, None, coll)
    D['materiale'] = mat_sole('PT_sole_' + tipo, tipo, forza or {'A': 2.6, 'B': 2.4, 'C': 4.0}[tipo])
    c = D['corpo'] = _sfera('SoleCorpo', raggio, D['materiale'], coll); c.parent = r
    col = (1.0, 0.42, 0.05) if tipo != 'C' else (1.0, 0.78, 0.4)
    for k, (s_, f_, e_) in enumerate(((1.45, 5.0 if tipo != 'C' else 8.0, 1.3), (4.0, 1.0 if tipo != 'C' else 1.6, 2.0))):    # alone: dischi rivolti alla camera
        o = _alone('SoleAlone%d' % k, raggio * s_, mat_alone('PT_alone_%s_%d' % (tipo, k), col, f_ * alone, e_), coll); o.parent = r; D['aloni'] = D.get('aloni', []) + [o]
    D['corona'] = o
    if tipo == 'B':                                                                                  # protuberanze: archi di plasma sul bordo
        mp = material('PT_protuberanza', (1.0, 0.4, 0.05), rough=1.0, emit=(1.0, 0.4, 0.05), emit_strength=4.0); rnd = random.Random(4)
        for k in range(7):
            a = rnd.uniform(0, 2 * PI); g = empty('Protuberanza', (0, 0, 0), r, coll); g.rotation_euler = (rnd.uniform(-0.4, 0.4), a, rnd.uniform(-0.3, 0.3))
            me = _arco(raggio * rnd.uniform(0.12, 0.24), raggio * 0.018); me.materials.append(mp); o = bpy.data.objects.new('ProtArco', me); coll.objects.link(o); o.parent = g
            o.location = (0, 0, raggio * 0.98); o.visible_shadow = False
    l_ = bpy.data.lights.new('LuceSole', 'POINT'); l_.energy = luce; l_.color = (1.0, 0.62, 0.28) if tipo != 'C' else (1.0, 0.85, 0.6); l_.shadow_soft_size = raggio * 0.6
    D['luce'] = bpy.data.objects.new('LuceSole', l_); coll.objects.link(D['luce']); D['luce'].parent = r
    return D

def _arco(R, r, nu=28, nv=8):
    me = bpy.data.meshes.new('Arco'); vs = []; fs = []
    for i in range(nu + 1):
        a = PI * i / nu
        for j in range(nv):
            b = 2 * PI * j / nv; rr = R + r * math.cos(b); vs.append((rr * math.cos(a), r * math.sin(b), rr * math.sin(a) * 1.3))
    for i in range(nu):
        for j in range(nv): fs.append((i * nv + j, (i + 1) * nv + j, (i + 1) * nv + (j + 1) % nv, i * nv + (j + 1) % nv))
    me.from_pydata(vs, [], fs); me.update(); [setattr(p, 'use_smooth', True) for p in me.polygons]; return me

def anima_sole(D, f, t):
    """fa ribollire la superficie (va chiamata per ogni fotogramma)."""
    nt = D['materiale'].node_tree
    for nm in ('PT_ribolle', 'PT_granuli'):
        n = nt.nodes[nm]; n.inputs['W'].default_value = t * (0.35 if nm == 'PT_ribolle' else 0.9); n.inputs['W'].keyframe_insert('default_value', frame=f)
    D['corpo'].rotation_euler = (0, 0, t * 0.03); D['corpo'].keyframe_insert('rotation_euler', frame=f)

def incendio(A, coll, posti, scala=1.0, seme=3):
    """fiamme 3D (cono) + immagini di fiamme + colonne di fumo nero sopra ogni posto (x, y, z). Restituisce la lista degli oggetti."""
    import paesaggi; rnd = random.Random(seme); objs = []
    for k, p in enumerate(posti):
        s = scala * rnd.uniform(0.8, 1.3)
        objs += rogo(coll, p, 1.6 * s, seme * 10 + k, 1100.0, 'Incendio%d' % k)
        o = A.effetto('fumo_nero/blacksmoke0%d' % (k % 9), posizione=(p[0] + rnd.uniform(-1, 1), p[1] + 0.5, p[2] + 7.5 * s), larghezza=9.0 * s, opacita=0.8, collezione=coll); objs.append(o)
    return objs

def cielo_rosso(world, forza_luce=0.5):
    """il cielo della testa (gradiente) diventa arancio sporco in basso e marrone scuro in alto."""
    nt = world.node_tree; rp = next(n for n in nt.nodes if n.type == 'VALTORGB')
    rp.color_ramp.elements[0].color = (1.0, 0.36, 0.08, 1); rp.color_ramp.elements[1].color = (0.18, 0.06, 0.04, 1)
    for n in nt.nodes:
        if n.type == 'BACKGROUND' and not any(l.to_node.type == 'MIX_SHADER' and l.to_socket == l.to_node.inputs[2] for l in n.outputs[0].links): n.inputs['Strength'].default_value = forza_luce

# ------------------------------------------------------------------ comparse che scappano in fiamme (cartone: capelli e sedere in fiamme, faccia nera di fuliggine)
from common import shape
PELLI = [(0.95, 0.72, 0.55), (0.78, 0.53, 0.36), (0.55, 0.36, 0.24), (0.98, 0.8, 0.66)]
MAGLIE = [(0.85, 0.15, 0.15), (0.15, 0.45, 0.85), (0.2, 0.65, 0.3), (0.9, 0.75, 0.15), (0.6, 0.25, 0.7), (0.95, 0.5, 0.15)]
def comparsa(A, coll, pos, rotz=0.0, seme=0, fuoco=True, fase=0.0, nome='Comparsa'):
    """omino cartone che corre urlando con le braccia in alto. Guarda verso -Y con rotz = 0. fase sposta il passo di corsa."""
    rnd = random.Random(seme); pelle = PELLI[seme % len(PELLI)]; mag = MAGLIE[seme % len(MAGLIE)]
    sporco = tuple(c * 0.55 for c in pelle)
    mp = material('PC_pelle%d' % seme, sporco, rough=0.6); mm = material('PC_maglia%d' % seme, mag, rough=0.7)
    mpa = material('PC_pant%d' % seme, (0.12, 0.15, 0.28) if seme % 2 else (0.35, 0.28, 0.2), rough=0.8)
    mb = material('PC_bianco', (1, 1, 1), rough=0.3); mn = material('PC_nero', (0.02, 0.02, 0.02), rough=0.4); mr = material('PC_bocca', (0.35, 0.02, 0.03), rough=0.5)
    r = empty(nome, pos, None, coll); r.rotation_euler = (0, 0, rotz); s = rnd.uniform(0.9, 1.08); r.scale = (s, s, s)
    corpo = empty(nome + 'Corpo', (0, 0, 0), r, coll); corpo.rotation_euler = (-0.25, 0, 0)            # piegato in avanti: corre
    shape(nome + 'Busto', 'cap:0.30:0.45', (0, 0, 1.25), parent=corpo, mat=mm, coll=coll)
    shape(nome + 'Testa', 'sphere', (0, 0, 1.95), scale=(0.33, 0.31, 0.35), parent=corpo, mat=mp, coll=coll)
    for sx in (-1, 1):
        shape(nome + 'Occhio', 'sphere', (0.12 * sx, -0.26, 2.02), scale=(0.1, 0.06, 0.13), parent=corpo, mat=mb, coll=coll)
        shape(nome + 'Pupilla', 'sphere', (0.12 * sx, -0.32, 2.0), scale=(0.035, 0.02, 0.04), parent=corpo, mat=mn, coll=coll)
        shape(nome + 'Ciglio', 'cyl:0.02:0.18', (0.13 * sx, -0.28, 2.18), rot=(0, PI / 2, -0.5 * sx), parent=corpo, mat=mn, coll=coll)   # sopracciglia in panico
    shape(nome + 'Bocca', 'sphere', (0, -0.27, 1.8), scale=(0.11, 0.05, 0.12), parent=corpo, mat=mr, coll=coll)                        # urla
    D = dict(radice=r, corpo=corpo, gambe=[], braccia=[], fiamme=[])
    for sx in (-1, 1):
        sp = empty(nome + 'Spalla', (0.36 * sx, 0, 1.55), corpo, coll); sp.rotation_euler = (rnd.uniform(-0.3, 0.3), 0, 0)
        shape(nome + 'Braccio', 'cap:0.08:0.5', (0, 0, 0.33), parent=sp, mat=mm, coll=coll); shape(nome + 'Mano', 'sphere', (0, 0, 0.7), scale=(0.11,) * 3, parent=sp, mat=mp, coll=coll)
        sp.rotation_euler[1] = 0.45 * sx; D['braccia'].append(sp)
        an = empty(nome + 'Anca', (0.15 * sx, 0, 0.92), r, coll)
        shape(nome + 'Gamba', 'cap:0.11:0.55', (0, 0, -0.42), parent=an, mat=mpa, coll=coll); shape(nome + 'Scarpa', 'sphere', (0, -0.08, -0.86), scale=(0.12, 0.2, 0.09), parent=an, mat=mn, coll=coll)
        D['gambe'].append(an)
    D['fase'] = fase
    if fuoco:
        D['fiamme'] += rogo(coll, (0, 0.05, 2.22), 0.6, seme * 3 + 1, 120.0, nome + 'FuocoTesta', corpo, forza=1.6, guarda=False)
        D['fiamme'] += rogo(coll, (0.18, 0.3, 0.95), 0.42, seme * 3 + 2, 0.0, nome + 'FuocoSedere', r, forza=1.6, guarda=False)
        pass                                                                                     # niente fumo sopra le comparse: copriva le loro fiamme
    return D

def paesaggi_fuoco(coll, loc, scala, luce, nome):
    import paesaggi
    r_, l_ = paesaggi.fuoco(coll, loc, scala, luce, nome); l_.data.use_shadow = False; return r_, l_

def corri(D, f, t, velocita=10.0):
    """passo di corsa (gambe e braccia che si agitano) al tempo t."""
    ph = t * velocita + D['fase']
    for i, g in enumerate(D['gambe']):
        g.rotation_euler = (math.sin(ph + PI * i) * 0.9, 0, 0); g.keyframe_insert('rotation_euler', frame=f)
    for i, b in enumerate(D['braccia']):
        b.rotation_euler[0] = math.sin(ph * 1.3 + PI * i) * 0.5; b.keyframe_insert('rotation_euler', frame=f)
    D['corpo'].location = (0, 0, abs(math.sin(ph)) * 0.18); D['corpo'].keyframe_insert('location', frame=f)

def quartiere_bruciato(M, scene):
    """prato bruciacchiato, chiome scure, niente nuvole bianche."""
    for o in list(bpy.data.objects):
        if o.name.startswith('CloudW') or o.name.startswith('Puff'): bpy.data.objects.remove(o, do_unlink=True)
    def tinta(m, c, k=1.0):
        if not m or not m.use_nodes: return
        b = m.node_tree.nodes.get('Principled BSDF')
        if b: b.inputs['Base Color'].default_value = c + (1,)
    pk = M.get('park')
    if pk:
        for n in pk.node_tree.nodes:
            if n.type == 'VALTORGB':
                n.color_ramp.elements[0].color = (0.13, 0.10, 0.05, 1); n.color_ramp.elements[1].color = (0.09, 0.07, 0.04, 1)
    for m in (M.get('leaf') or []): tinta(m, (0.12, 0.1, 0.05))

def bagliore(scene, forza=0.35, soglia=1.2, dimensione=0.5):
    """bagliore vero attorno a sole e fiamme (compositor, Glare 'Bloom')."""
    ng = bpy.data.node_groups.new('Comp021', 'CompositorNodeTree'); scene.compositing_node_group = ng
    rl = ng.nodes.new('CompositorNodeRLayers'); g = ng.nodes.new('CompositorNodeGlare')
    ng.interface.new_socket('Image', in_out='OUTPUT', socket_type='NodeSocketColor'); go = ng.nodes.new('NodeGroupOutput')
    try: g.inputs['Type'].default_value = 'Bloom'
    except Exception: g.inputs['Type'].default_value = 'Fog Glow'
    g.inputs['Threshold'].default_value = soglia; g.inputs['Strength'].default_value = forza; g.inputs['Size'].default_value = dimensione; g.inputs['Saturation'].default_value = 1.0
    ng.links.new(rl.outputs['Image'], g.inputs['Image']); ng.links.new(g.outputs[0], go.inputs[0])
    return g

# ------------------------------------------------------------------ fiamme realistiche: lingue di fuoco procedurali su un piano che guarda sempre la camera
def _drv(sock, espr):
    d = sock.driver_add('default_value').driver; d.type = 'SCRIPTED'; d.expression = espr

def mat_fiamma(nome, seme=0.0, forza=4.0):
    m = bpy.data.materials.get(nome)
    if m: return m
    m = bpy.data.materials.new(nome); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear(); L = nt.links.new
    try: m.surface_render_method = 'BLENDED'
    except Exception: m.blend_method = 'BLEND'
    def N(t, **kw):
        n = nt.nodes.new(t)
        for k, v in kw.items(): setattr(n, k, v)
        return n
    def M_(op, a, b=None, c=None):
        n = N('ShaderNodeMath', operation=op)
        for i, x in enumerate((a, b, c)):
            if x is None: continue
            if isinstance(x, (int, float)): n.inputs[i].default_value = x
            else: L(x, n.inputs[i])
        return n.outputs[0]
    tc = N('ShaderNodeTexCoord'); sx = N('ShaderNodeSeparateXYZ'); L(tc.outputs['UV'], sx.inputs[0])
    u, v = sx.outputs['X'], sx.outputs['Y']; x = M_('MULTIPLY', M_('SUBTRACT', u, 0.5), 2.0)
    cb = N('ShaderNodeCombineXYZ'); L(M_('MULTIPLY', x, 1.6), cb.inputs['X']); L(M_('MULTIPLY', v, 2.2), cb.inputs['Y']); cb.inputs['Z'].default_value = seme
    of = N('ShaderNodeCombineXYZ'); _drv(of.inputs['Y'], 'frame/24*-2.4')
    vec = N('ShaderNodeVectorMath', operation='ADD'); L(cb.outputs[0], vec.inputs[0]); L(of.outputs[0], vec.inputs[1])
    nz = N('ShaderNodeTexNoise', noise_dimensions='4D'); nz.inputs['Scale'].default_value = 2.3; nz.inputs['Detail'].default_value = 5; nz.inputs['Roughness'].default_value = 0.6
    L(vec.outputs[0], nz.inputs['Vector']); _drv(nz.inputs['W'], 'frame/24*0.8')
    # sagoma a goccia: larga in basso, a punta in alto; il rumore la sfrangia di piu' verso l'alto
    larg = M_('ADD', M_('MULTIPLY', M_('POWER', M_('MAXIMUM', M_('SUBTRACT', 1.0, v), 0.0), 0.8), 0.85), 0.04)
    forma = M_('SUBTRACT', 1.0, M_('POWER', M_('DIVIDE', M_('ABSOLUTE', x), larg), 2.0))
    forma = M_('MULTIPLY', forma, M_('MINIMUM', M_('MULTIPLY', v, 6.0), 1.0))                               # base sfumata
    f = M_('ADD', M_('MULTIPLY', forma, M_('SUBTRACT', 1.0, M_('MULTIPLY', v, 0.55))), M_('MULTIPLY', M_('SUBTRACT', nz.outputs['Fac'], 0.5), M_('ADD', M_('MULTIPLY', v, 1.6), 0.3)))
    rp = N('ShaderNodeValToRGB'); L(f, rp.inputs['Fac']); E = rp.color_ramp.elements
    E[0].position, E[0].color = 0.1, (0.35, 0.02, 0.0, 1); E[1].position, E[1].color = 0.85, (1.0, 0.95, 0.75, 1)
    for p_, c_ in ((0.25, (0.9, 0.12, 0.0)), (0.42, (1.0, 0.36, 0.02)), (0.6, (1.0, 0.65, 0.12))): e_ = E.new(p_); e_.color = c_ + (1,)
    al = N('ShaderNodeMapRange'); L(f, al.inputs['Value']); al.inputs['From Min'].default_value = 0.1; al.inputs['From Max'].default_value = 0.3
    em = N('ShaderNodeEmission'); L(rp.outputs['Color'], em.inputs['Color']); L(M_('MULTIPLY', M_('ADD', f, 0.3), forza), em.inputs['Strength'])
    tr = N('ShaderNodeBsdfTransparent'); mx = N('ShaderNodeMixShader'); L(al.outputs[0], mx.inputs[0]); L(tr.outputs[0], mx.inputs[1]); L(em.outputs[0], mx.inputs[2])
    out = N('ShaderNodeOutputMaterial'); L(mx.outputs[0], out.inputs['Surface'])
    return m

def fiamma(coll, pos, altezza=3.0, seme=0, parent=None, forza=4.0, nome='Fiamma', guarda=True):
    """una lingua di fuoco alta 'altezza' con la base in pos. guarda=True: gira attorno a Z per guardare la camera;
    guarda=False: due piani incrociati, senza vincoli (per le fiamme attaccate a chi corre)."""
    w = altezza * 0.62
    vs = [(-w / 2, 0, 0), (w / 2, 0, 0), (w / 2, 0, altezza), (-w / 2, 0, altezza)]; fs = [(0, 1, 2, 3)]
    if not guarda: vs += [(0, -w / 2, 0), (0, w / 2, 0), (0, w / 2, altezza), (0, -w / 2, altezza)]; fs.append((4, 5, 6, 7))
    me = bpy.data.meshes.new(nome); me.from_pydata(vs, [], fs)
    uv = me.uv_layers.new()
    for i, co in enumerate(((0, 0), (1, 0), (1, 1), (0, 1)) * len(fs)): uv.data[i].uv = co
    me.update(); me.materials.append(mat_fiamma('PF_fiamma%d_%.1f' % (seme % 5, forza), seme % 5 * 3.7, forza))
    o = bpy.data.objects.new(nome, me); coll.objects.link(o); o.visible_shadow = False
    if parent: o.parent = parent
    o.location = pos
    cam = bpy.context.scene.camera
    if cam and guarda:
        c = o.constraints.new('LOCKED_TRACK'); c.target = cam; c.track_axis = 'TRACK_NEGATIVE_Y'; c.lock_axis = 'LOCK_Z'
    return o

def rogo(coll, pos, scala=1.0, seme=0, luce=900.0, nome='Rogo', parent=None, n=5, forza=4.0, guarda=True):
    """gruppo di fiamme (una grande e alcune piccole intorno) con una luce calda che non fa ombre."""
    rnd = random.Random(seme); r = empty(nome, pos, parent, coll); out = [r]
    for k in range(n):
        dx = 0 if k == 0 else rnd.uniform(-0.55, 0.55) * scala; h = (1.0 if k == 0 else rnd.uniform(0.45, 0.8)) * 2.6 * scala
        out.append(fiamma(coll, (dx, rnd.uniform(-0.2, 0.2) * scala, 0), h, seme * 5 + k, r, forza=forza, nome=nome + 'F', guarda=guarda))
    if luce:
        l_ = bpy.data.lights.new(nome + 'Luce', 'POINT'); l_.energy = luce * scala; l_.color = (1.0, 0.45, 0.12); l_.shadow_soft_size = 0.5 * scala; l_.use_shadow = False
        lo = bpy.data.objects.new(nome + 'Luce', l_); coll.objects.link(lo); lo.parent = r; lo.location = (0, -0.4 * scala, 1.0 * scala); out.append(lo)
    return out

# ------------------------------------------------------------------ pezzi del video 021
from set004 import obj, bx, cyl, ball_, MB
import set004

def naso(coll, head, pelle=(1.0, 0.55, 0.48)):
    """naso di Pippo per questo episodio (lo starnuto): bulbo + due narici scure, fronte -Y. 'bulbo' si gonfia (scala)."""
    D = {}; r = D['root'] = empty('Naso', (0, -0.29, 0.215), head, coll)
    mp = material('P21_naso', pelle, rough=0.5); mn = material('P21_narice', (0.12, 0.02, 0.03), rough=0.8)
    D['bulbo'] = b = empty('NasoBulbo', (0, 0, 0), r, coll)
    ball_('NasoPalla', 0.085, (0, -0.02, 0), mp, coll, parent=b, sc=(1.0, 0.95, 0.85))
    D['narici'] = []
    for sx in (-1, 1):
        n_ = ball_('Narice', 0.022, (sx * 0.032, -0.045, -0.04), mn, coll, parent=b, sc=(1.0, 0.8, 0.55)); n_['base'] = tuple(n_.scale); D['narici'].append(n_)
    return D

def camion_pepe(coll, M9):
    """il camion ribaltabile del video 019/009 con il carico di pepe nero e la scritta PEPE. Restituisce (root, cassone, carico)."""
    pepe = material('P21_pepe', (0.018, 0.015, 0.013), rough=0.9, spec=0.15)
    M = dict(M9); M['snow'] = pepe
    r, bed, load = set004_truck(coll, M)
    for o in bed.children_recursive:
        if o.type == 'FONT': o.data.body = 'PEPE'; o.data.size = 0.7
    return r, bed, load

def set004_truck(coll, M):
    import props009; return props009.truck(coll, M)

def mucchio_pepe(coll, r=1.6, seme=5):
    import props009
    pepe = material('P21_pepe', (0.018, 0.015, 0.013), rough=0.9, spec=0.15)
    return props009.heap(coll, {'snow': pepe}, 'MucchioPepe', n=22, seed=seme, r=r)

def vestaglia(coll, G, colore=(0.55, 0.08, 0.14)):
    """vestaglia di velluto con la cintura dorata, sopra la canottiera di Gualtiero (figlia della radice)."""
    mv = material('P21_vestaglia', colore, rough=0.75); mb_ = material('P21_cintura', (0.95, 0.8, 0.3), rough=0.5)
    g = empty('Vestaglia', (0, 0, 0), G['root'], coll)
    ball_('VestCorpo', 1.0, (0, -0.06, 1.02), mv, coll, parent=g, sc=(0.37, 0.35, 0.5))
    ball_('VestGonna', 1.0, (0, -0.04, 0.72), mv, coll, parent=g, sc=(0.34, 0.31, 0.3))
    cyl('VestCintura', 0.36, 0.06, (0, -0.07, 0.95), mb_, coll, parent=g)
    for sx in (-1, 1): ball_('VestBavero', 1.0, (sx * 0.13, -0.3, 1.32), mv, coll, parent=g, sc=(0.08, 0.05, 0.16))
    return g

def calendario3(coll, loc, font=None):
    """calendario a muro: solo tre giorni sbarrati. Faccia verso -Y."""
    import props017
    M = props017.mats017(); g = empty('Calendario3', loc, None, coll)
    mb = MB([M['paper'], M['redink'], M['ink']])
    mb.b2((-0.38, -0.5, 0.0), (0.38, 0.5, 0.02), 0); mb.b2((-0.38, 0.30, 0.02), (0.38, 0.5, 0.026), 1)
    for r in range(4):
        for c_ in range(6):
            x = -0.29 + c_ * 0.116; y = 0.17 - r * 0.16; k = r * 6 + c_
            if k in (14, 15, 16):
                for s_ in (1, -1): mb.box((x, y, 0.024), (0.105, 0.022, 0.004), 1, rz=s_ * 0.8)
            else: mb.box((x, y, 0.024), (0.05, 0.05, 0.004), 2)
    o = mb.build('Calendario3Geo', coll); o.parent = g; o.rotation_euler = (PI / 2, 0, 0)
    props017.testo(coll, 'CalTesto', 'NOVEMBRE', 0.1, M['txt'], (0, -0.03, 0.40), font=font, parent=g)
    return g

def cartello_vacanza(coll, font=None, testo='IN VACANZA'):
    """cartello di legno su paletto, scritta verso -Y, origine a terra."""
    import props007
    r = empty('CartelloVacanza', (0, 0, 0), None, coll)
    legno = material('P21_legno', (0.55, 0.36, 0.18), rough=0.7); bianco = material('P21_bianco', (1, 1, 1), rough=0.4)
    obj('CVPalo', set004.box_c(), (0, 0.04, 0.6), (0.1, 0.08, 1.2), legno, coll, parent=r)
    obj('CVTavola', set004.box_c(), (0, 0, 1.35), (1.6, 0.06, 0.5), legno, coll, parent=r)
    t = props007.text_obj(coll, 'CVTesto', testo, 0.26, bianco, (0, -0.04, 1.35), parent=r)
    if font: t.data.font = font
    return r

def appartamento(A, coll, centro, font=None):
    """la casa di Gualtiero dentro la narice di Pippo: una grotta rosa con parquet, lampadario H, quadro L, poltrona,
    calendario con tre giorni sbarrati, valigie aperte. Fronte (apertura) verso -Y."""
    import props009, props017
    cx, cy, cz = centro; r = empty('Appartamento', centro, None, coll)
    rosa = material('P21_mucosa', (0.85, 0.42, 0.42), rough=0.55, coat=0.6, coat_rough=0.2)
    parq = A.materiale('brown_planks_03', dimensione=1.2) if hasattr(A, 'materiale') else material('P21_parq', (0.5, 0.3, 0.15))
    me = bpy.data.meshes.new('Grotta'); bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=48, v_segments=24, radius=3.2)
    for v in bm.verts:
        v.co.z *= 0.75
        if v.co.z < -0.6: v.co.z = -0.6
    bmesh.ops.reverse_faces(bm, faces=bm.faces); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    me.materials.append(rosa); o = bpy.data.objects.new('Grotta', me); coll.objects.link(o); o.parent = r; o.scale = (1.25, 1.0, 1.0)
    pav = bx('Parquet', (cx - 3.4, cy - 2.9, cz - 0.62), (cx + 3.4, cy + 2.9, cz - 0.6), parq, coll)
    try: A.modello('Chandelier_01', posizione=(cx, cy + 0.4, cz + 2.25), scala=1.0, collezione=coll, appoggia=False)
    except Exception as e: print('lampadario', e)
    try:
        q = A.modello('fancy_picture_frame_01', posizione=(cx - 1.2, cy + 2.55, cz + 0.6), altezza=0.9, collezione=coll, appoggia=True); q.rotation_euler = (0, 0, 0)
    except Exception as e: print('quadro', e)
    try: A.modello('vintage_suitcase', posizione=(cx + 1.7, cy + 0.6, cz - 0.6), altezza=0.45, rotazione=-30, collezione=coll, appoggia='terra')
    except Exception as e: print('valigia', e)
    M9 = props009.mats009(); pol = props009.armchair(coll, M9)
    pol = pol[0] if isinstance(pol, tuple) else pol
    pol.location = (cx + 1.0, cy + 1.3, cz - 0.6); pol.rotation_euler = (0, 0, PI + 0.4); pol.scale = (0.8,) * 3
    cal = calendario3(coll, (cx + 0.6, cy + 2.6, cz + 0.85), font=font); cal.scale = (0.7,) * 3
    tap = material('P21_tappeto', (0.15, 0.3, 0.55), rough=0.9); cyl('Tappeto', 1.3, 0.02, (cx, cy + 0.2, cz - 0.59), tap, coll)
    for (dx, dy) in ((-0.5, -0.4), (-0.25, -0.5)):
        ciab = material('P21_ciabatta', (0.5, 0.3, 0.14), rough=0.7); ball_('Ciabatta', 0.12, (cx + dx, cy + dy, cz - 0.56), ciab, coll, sc=(0.6, 1.2, 0.35))
    l_ = bpy.data.lights.new('LuceLampadario', 'POINT'); l_.energy = 120; l_.color = (1.0, 0.78, 0.5); l_.shadow_soft_size = 0.3
    lo = bpy.data.objects.new('LuceLampadario', l_); coll.objects.link(lo); lo.location = (cx, cy + 0.4, cz + 1.4)
    return r

def cupola_inferno(coll, raggio=600.0):
    """cielo dell'inferno: una cupola che copre il cielo vero (arancio in basso, marrone fumoso in alto, nuvole di fumo)."""
    m = bpy.data.materials.new('P21_cupola'); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear(); L = nt.links.new
    tc = nt.nodes.new('ShaderNodeTexCoord'); sx = nt.nodes.new('ShaderNodeSeparateXYZ'); L(tc.outputs['Object'], sx.inputs[0])
    dv = nt.nodes.new('ShaderNodeMath'); dv.operation = 'DIVIDE'; L(sx.outputs['Z'], dv.inputs[0]); dv.inputs[1].default_value = raggio * 0.5
    nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 3.0; nz.inputs['Detail'].default_value = 8; L(tc.outputs['Generated'], nz.inputs['Vector'])
    ad = nt.nodes.new('ShaderNodeMath'); ad.operation = 'MULTIPLY_ADD'; L(nz.outputs['Fac'], ad.inputs[0]); ad.inputs[1].default_value = 0.35; L(dv.outputs[0], ad.inputs[2])
    rp = nt.nodes.new('ShaderNodeValToRGB'); L(ad.outputs[0], rp.inputs['Fac']); E = rp.color_ramp.elements
    E[0].position, E[0].color = 0.12, (1.0, 0.32, 0.05, 1); E[1].position, E[1].color = 0.7, (0.06, 0.03, 0.025, 1)
    e_ = E.new(0.3); e_.color = (0.55, 0.12, 0.03, 1); e_ = E.new(0.45); e_.color = (0.22, 0.07, 0.04, 1)
    em = nt.nodes.new('ShaderNodeEmission'); L(rp.outputs['Color'], em.inputs['Color']); em.inputs['Strength'].default_value = 1.0
    out = nt.nodes.new('ShaderNodeOutputMaterial'); L(em.outputs[0], out.inputs['Surface'])
    me = bpy.data.meshes.new('CupolaInferno'); bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=48, v_segments=24, radius=raggio); bm.to_mesh(me); bm.free()
    me.materials.append(m); o = bpy.data.objects.new('CupolaInferno', me); coll.objects.link(o)
    o.visible_shadow = False; o.visible_diffuse = False; o.visible_glossy = False
    return o

def terra_bruciata(coll, A=None):
    """prato bruciato con le braci che pulsano: piano appena sopra il prato (la strada resta sopra)."""
    m = bpy.data.materials.new('P21_cenere'); m.use_nodes = True; nt = m.node_tree; L = nt.links.new
    b = nt.nodes['Principled BSDF']; b.inputs['Base Color'].default_value = (0.05, 0.04, 0.035, 1); b.inputs['Roughness'].default_value = 0.95
    tc = nt.nodes.new('ShaderNodeTexCoord'); vo = nt.nodes.new('ShaderNodeTexVoronoi'); vo.inputs['Scale'].default_value = 1.6; L(tc.outputs['Object'], vo.inputs['Vector'])
    nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 0.35; L(tc.outputs['Object'], nz.inputs['Vector'])
    mr = nt.nodes.new('ShaderNodeMapRange'); L(vo.outputs['Distance'], mr.inputs['Value']); mr.inputs['From Min'].default_value = 0.02; mr.inputs['From Max'].default_value = 0.09
    mr.inputs['To Min'].default_value = 1.0; mr.inputs['To Max'].default_value = 0.0
    mu = nt.nodes.new('ShaderNodeMath'); mu.operation = 'MULTIPLY'; L(mr.outputs[0], mu.inputs[0]); L(nz.outputs['Fac'], mu.inputs[1])
    mu2 = nt.nodes.new('ShaderNodeMath'); mu2.operation = 'MULTIPLY'; L(mu.outputs[0], mu2.inputs[0]); mu2.inputs[1].default_value = 6.0
    b.inputs['Emission Color'].default_value = (1.0, 0.3, 0.03, 1); L(mu2.outputs[0], b.inputs['Emission Strength'])
    o = bx('TerraBruciata', (-140, -140, 0.004), (140, 140, 0.008), m, coll); o.visible_shadow = False
    return o

def lazo(coll):
    """corda: un cilindro lungo 1 lungo Z, da allungare tra due punti con tira_corda()."""
    mc = material('P21_corda', (0.78, 0.6, 0.32), rough=0.9)
    o = cyl('Corda', 0.035, 1.0, (0, 0, 0.5), mc, coll); g = empty('CordaPerno', (0, 0, 0), None, coll); o.parent = g; return g

def tira_corda(g, a, b, f):
    from mathutils import Vector
    a = Vector(a); b = Vector(b); d = b - a
    g.location = a; g.rotation_mode = 'QUATERNION'; g.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d.normalized()); g.scale = (1, 1, max(0.001, d.length))
    g.keyframe_insert('location', frame=f); g.keyframe_insert('rotation_quaternion', frame=f); g.keyframe_insert('scale', frame=f)
