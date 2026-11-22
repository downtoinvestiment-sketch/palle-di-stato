"""Oggetti del video 027 «Pippo rockstar gigante»: look da rockstar (L1 pelle, L2 glam, L3 punk),
chitarre (G1 saetta, G2 doppio manico), antenna usata come asta del microfono (G3),
citta' in miniatura attorno a Pippo (C1 metropoli di notte, C2 tramonto, C3 neon).
Pippo resta alto 2,3: e' la citta' a essere piccola, cosi' lui e' alto come un grattacielo.
Non tocca pippo.py: tutto e' attaccato da fuori ai pezzi restituiti da pippo2.build_pippo()."""
import math, random
import bpy, bmesh
from common import *
import props024

PI = math.pi


def mats027():
    m = dict(
        pelle=material('M27_pelle', (0.015, 0.015, 0.02), rough=0.32, coat=0.6),
        maglia=material('M27_maglia', (0.92, 0.92, 0.9), rough=0.8),
        metallo=material('M27_metallo', (0.8, 0.8, 0.85), rough=0.18, metallic=1.0),
        rosso=material('M27_rosso', (0.75, 0.03, 0.03), rough=0.45),
        oro=material('M27_oro', (1.0, 0.72, 0.18), rough=0.22, metallic=1.0),
        boa=material('M27_boa', (1.0, 0.25, 0.6), rough=0.9),
        argento=material('M27_argento', (0.85, 0.87, 0.9), rough=0.15, metallic=1.0),
        jeans=material('M27_jeans', (0.10, 0.22, 0.5), rough=0.85),
        nero=material('M27_nero', (0.02, 0.02, 0.02), rough=0.7),
        cresta=material('M27_cresta', (1.0, 0.05, 0.55), rough=0.5, emit=(1.0, 0.05, 0.55), emit_strength=0.6),
        chit_r=material('M27_chit_rossa', (0.85, 0.02, 0.02), rough=0.12, coat=1.0),
        chit_b=material('M27_chit_bianca', (0.95, 0.93, 0.85), rough=0.15, coat=1.0),
        viola=material('M27_viola', (0.35, 0.05, 0.6), rough=0.3, coat=0.5),
        legno=material('M27_legno', (0.20, 0.10, 0.04), rough=0.5),
        faro=material('M27_faro', (1.0, 0.05, 0.02), rough=0.3, emit=(1.0, 0.05, 0.02), emit_strength=12.0),
        asfalto=material('M27_asfalto', (0.03, 0.03, 0.04), rough=0.85),
        bagnato=material('M27_bagnato', (0.02, 0.02, 0.03), rough=0.24),
        tetto=material('M27_tetto', (0.05, 0.05, 0.06), rough=0.8),
        fucsia=material('M27_fucsia', (1.0, 0.04, 0.45), rough=0.25, coat=0.8),
        bianco=material('M27_bianco', (0.95, 0.95, 0.95), rough=0.3, coat=0.6),
        azzurro=material('M27_azzurro', (0.05, 0.55, 1.0), rough=0.3, coat=0.6),
    )
    return m


# --------------------------------------------------------------------------- pezzi di base
def scatola(nome, sx, sy, sz, mat, coll, parent=None, loc=(0, 0, 0), rot=(0, 0, 0), r=None):
    return props024.scatola_tonda(nome, sx, sy, sz, r if r is not None else min(sx, sy, sz) * 0.2, mat, coll, parent=parent, loc=loc, rot=rot)


def lastra(nome, pts, sp, mat, coll, parent=None, loc=(0, 0, 0), rot=(0, 0, 0)):
    """Poligono piano (nel piano XZ) con spessore sp lungo Y."""
    bm = bmesh.new()
    a = [bm.verts.new((x, -sp / 2, z)) for x, z in pts]
    b = [bm.verts.new((x, sp / 2, z)) for x, z in pts]
    n = len(pts)
    bm.faces.new(a); bm.faces.new(list(reversed(b)))
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((a[j], a[i], b[i], b[j]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(nome); bm.to_mesh(me); bm.free(); me.materials.append(mat)
    o = bpy.data.objects.new(nome, me); o.location = loc; o.rotation_euler = rot; o.parent = parent
    coll.objects.link(o)
    return o


# --------------------------------------------------------------------------- look da rockstar
def _giacca(coll, R, mat, davanti, maniche=True, nome='Giacca'):
    b = R['body']
    shape(nome, 'cap:0.262:0.44', loc=(0, 0, 0.36), parent=b, mat=mat, coll=coll)
    shape(nome + 'Maglia', 'sphere', loc=(0, -0.205, 0.42), scale=(0.10, 0.07, 0.27), parent=b, mat=davanti, coll=coll)
    for s in (-1, 1):                                                   # risvolti
        scatola(nome + 'Risvolto', 0.10, 0.03, 0.30, mat, coll, parent=b, loc=(s * 0.115, -0.245, 0.52), rot=(0.12, s * 0.35, s * 0.25))
    props024.anello(nome + 'Colletto', 0.15, 0.04, mat, coll, parent=b, loc=(0, 0.01, 0.76))
    if maniche:
        for nm in 'LR':
            shape(nome + 'Manica' + nm, 'cap:0.088:0.30', loc=(0, 0, -0.23), parent=R['shoulder' + nm], mat=mat, coll=coll)


def look(coll, R, tipo, M):
    """Veste Pippo da rockstar. L1 pelle nera e borchie, L2 glam oro con boa, L3 punk con cresta."""
    b, h = R['body'], R['head']
    if tipo == 'L1':
        _giacca(coll, R, M['pelle'], M['maglia'])
        for s in (-1, 1):
            for i in range(4):                                          # borchie sulle spalle
                shape('Borchia', 'cone', loc=(s * (0.17 + 0.035 * i), -0.02, 0.70 - 0.02 * i), scale=(0.02, 0.02, 0.05), rot=(0, s * 0.5, 0), parent=b, mat=M['metallo'], coll=coll)
        props024.anello('Bandana', 0.262, 0.04, M['rosso'], coll, parent=h, loc=(0, 0.0, 0.50))
        for k, rz in ((0, 0.5), (1, -0.5)):                             # i due lembi del nodo
            scatola('BandanaLembo', 0.05, 0.02, 0.17, M['rosso'], coll, parent=h, loc=(0.05 - 0.10 * k, 0.29, 0.42), rot=(-0.5, 0, rz))
        for nm in 'LR':
            props024.anello('Polsino' + nm, 0.092, 0.022, M['metallo'], coll, parent=R['shoulder' + nm], loc=(0, 0, -0.42))
    elif tipo == 'L2':
        _giacca(coll, R, M['oro'], M['nero'])
        for s in (-1, 1):                                               # spalline a punta
            shape('Spallina', 'cone', loc=(s * 0.22, 0, 0.70), scale=(0.11, 0.11, 0.26), rot=(0, s * 1.15, 0), parent=b, mat=M['oro'], coll=coll)
        for i in range(14):                                             # boa di piume attorno al collo
            a = 2 * PI * i / 14
            shape('Boa', 'sphere', loc=(0.21 * math.sin(a), -0.02 + 0.20 * math.cos(a), 0.74 + 0.02 * math.sin(3 * a)), scale=(0.085,) * 3, parent=b, mat=M['boa'], coll=coll)
        for s in (-1, 1):
            for i in range(4):
                shape('BoaCoda', 'sphere', loc=(s * (0.13 + 0.01 * i), -0.25, 0.64 - 0.09 * i), scale=(0.07,) * 3, parent=b, mat=M['boa'], coll=coll)
        for nm in 'LR':                                                 # stivali d'argento
            shape('Stivale' + nm, 'cap:0.128:0.22', loc=(0, 0, -0.43), parent=R['hip' + nm], mat=M['argento'], coll=coll)
    elif tipo == 'L3':
        _giacca(coll, R, M['jeans'], M['nero'], maniche=False)
        for s in (-1, 1):
            for i in range(5):                                          # punte sulle spalle
                a = -0.9 + 0.45 * i
                shape('Punta', 'cone', loc=(s * 0.25, 0.14 * math.sin(a), 0.66 + 0.05 * math.cos(a)), scale=(0.03, 0.03, 0.13), rot=(-a * 0.6, s * 0.9, 0), parent=b, mat=M['metallo'], coll=coll)
        for o in R['hair']:
            o.scale = (0, 0, 0)                                         # via i ciuffi: c'e' la cresta
        for i in range(8):                                              # cresta lungo la testa, dalla fronte alla nuca
            a = math.radians(-48 + 17 * i)
            hh = 0.42 + 0.16 * math.sin(PI * i / 7)
            shape('Cresta', 'cone', loc=(0, 0.30 * math.sin(a), 0.27 + 0.31 * math.cos(a)), scale=(0.095, 0.085, hh), rot=(-a, 0, 0), parent=h, mat=M['cresta'], coll=coll)
        for nm in 'LR':
            props024.anello('Bracciale' + nm, 0.085, 0.028, M['nero'], coll, parent=R['shoulder' + nm], loc=(0, 0, -0.40))
            for i in range(6):
                a = 2 * PI * i / 6
                shape('BraccialePunta', 'cone', loc=(0.10 * math.cos(a), 0.10 * math.sin(a), -0.40), scale=(0.018, 0.018, 0.05), rot=(-math.sin(a) * PI / 2, math.cos(a) * PI / 2, 0), parent=R['shoulder' + nm], mat=M['metallo'], coll=coll)
        props024.anello('Catena', 0.13, 0.012, M['metallo'], coll, parent=b, loc=(0.17, -0.20, 0.10))


# --------------------------------------------------------------------------- chitarre e antenna
def chitarra(coll, tipo, M, parent=None, nome='Chitarra'):
    """Chitarra nel piano XZ (manico lungo +X). G1 a saetta rossa, G2 bianca a doppio manico."""
    G = empty(nome, parent=parent, coll=coll)
    if tipo == 'G1':
        pts = [(-0.30, 0.03), (-0.10, 0.19), (0.00, 0.08), (0.20, 0.20), (0.12, 0.04), (0.24, -0.13), (0.03, -0.07), (-0.10, -0.22), (-0.13, -0.06)]
        lastra(nome + 'Corpo', pts, 0.045, M['chit_r'], coll, parent=G)
        manici = (0.0,)
    else:
        pts = [(0.27 * math.cos(a) * (1.0 + 0.12 * math.cos(2 * a)), 0.21 * math.sin(a)) for a in [2 * PI * i / 20 for i in range(20)]]
        lastra(nome + 'Corpo', pts, 0.045, M['chit_b'], coll, parent=G)
        lastra(nome + 'Battipenna', [(-0.14, -0.10), (0.12, -0.12), (0.16, 0.0), (0.02, 0.06), (-0.12, 0.04)], 0.05, M['viola'], coll, parent=G)
        manici = (0.075, -0.075)
    for z in manici:
        scatola(nome + 'Manico', 0.62, 0.03, 0.045, M['legno'], coll, parent=G, loc=(0.50, 0, z))
        scatola(nome + 'Paletta', 0.13, 0.03, 0.075, M['nero'], coll, parent=G, loc=(0.86, 0, z + 0.012), rot=(0, -0.2, 0))
        for i in range(2):
            scatola(nome + 'Pickup', 0.035, 0.012, 0.085, M['nero'], coll, parent=G, loc=(0.02 + 0.09 * i, -0.03, z))
        scatola(nome + 'Corde', 0.80, 0.004, 0.022, M['metallo'], coll, parent=G, loc=(0.42, -0.021, z), r=0.001)
    for i in range(2):
        shape(nome + 'Manopola', 'cyl:0.018:0.02', loc=(-0.12 - 0.05 * i, -0.03, -0.09), rot=(PI / 2, 0, 0), parent=G, mat=M['metallo'], coll=coll)
    return G


def tracolla(coll, R, M):
    o = props024.anello('Tracolla', 0.31, 0.014, M['nero'], coll, parent=R['body'], loc=(0, 0.0, 0.40))
    o.rotation_euler = (0, 0.85, 0)
    return o


def antenna(coll, M, H=1.55, nome='Antenna'):
    """Traliccio della TV usato come asta del microfono: in cima il microfono e la luce rossa."""
    G = empty(nome, coll=coll)
    for sx in (-1, 1):
        for sy in (-1, 1):
            shape(nome + 'Montante', 'cyl:0.008:%.3f' % H, loc=(sx * 0.035, sy * 0.035, H / 2), parent=G, mat=M['metallo'], coll=coll)
    n = 9
    for i in range(n + 1):
        z = H * i / n
        scatola(nome + 'Traversa', 0.086, 0.086, 0.008, M['metallo'], coll, parent=G, loc=(0, 0, z), r=0.002)
        if i < n:
            for k, (dx, dy, rx, ry) in enumerate(((0, -0.035, 0, 1), (0, 0.035, 0, -1), (-0.035, 0, 1, 0), (0.035, 0, -1, 0))):
                d = math.atan2(0.07, H / n) * (1 if i % 2 else -1)
                shape(nome + 'Diagonale', 'cyl:0.004:%.3f' % (math.hypot(0.07, H / n)), loc=(dx, dy, z + H / n / 2), rot=(rx * d, ry * d, 0), parent=G, mat=M['metallo'], coll=coll)
    shape(nome + 'Punta', 'cyl:0.006:0.22', loc=(0, 0, H + 0.11), parent=G, mat=M['metallo'], coll=coll)
    shape(nome + 'Luce', 'sphere', loc=(0, 0, H + 0.24), scale=(0.022,) * 3, parent=G, mat=M['faro'], coll=coll)
    shape(nome + 'Microfono', 'sphere', loc=(0, -0.05, H + 0.04), scale=(0.065, 0.065, 0.075), parent=G, mat=M['nero'], coll=coll)
    props024.anello(nome + 'MicAnello', 0.066, 0.008, M['argento'], coll, parent=G, loc=(0, -0.05, H + 0.04))
    return G


# --------------------------------------------------------------------------- citta' in miniatura
def mat_finestre(nome, muro, vetro, acceso, soglia=0.55, forza=5.0, w=0.07, h=0.095):
    """Facciata con finestre: griglia sulle UV (in unita' di scena), una parte accesa a caso, diversa per ogni palazzo."""
    if nome in bpy.data.materials:
        return bpy.data.materials[nome]
    m = bpy.data.materials.new(nome); m.use_nodes = True
    nt = m.node_tree; N, L = nt.nodes, nt.links
    b = N['Principled BSDF']; b.inputs['Roughness'].default_value = 0.3
    tc = N.new('ShaderNodeTexCoord'); oi = N.new('ShaderNodeObjectInfo')
    mx = N.new('ShaderNodeMath'); mx.operation = 'MULTIPLY'; mx.inputs[1].default_value = 53.0
    my = N.new('ShaderNodeMath'); my.operation = 'MULTIPLY'; my.inputs[1].default_value = 17.0
    cb = N.new('ShaderNodeCombineXYZ'); ad = N.new('ShaderNodeVectorMath'); ad.operation = 'ADD'
    L.new(oi.outputs['Random'], mx.inputs[0]); L.new(oi.outputs['Random'], my.inputs[0])
    L.new(mx.outputs[0], cb.inputs['X']); L.new(my.outputs[0], cb.inputs['Y'])
    L.new(tc.outputs['UV'], ad.inputs[0]); L.new(cb.outputs[0], ad.inputs[1])
    br = N.new('ShaderNodeTexBrick'); br.offset = 0.0; br.squash = 1.0
    br.inputs['Color1'].default_value = (0, 0, 0, 1); br.inputs['Color2'].default_value = (1, 1, 1, 1); br.inputs['Mortar'].default_value = (0, 0, 0, 1)
    br.inputs['Scale'].default_value = 1.0; br.inputs['Mortar Size'].default_value = 0.014; br.inputs['Mortar Smooth'].default_value = 0.0
    br.inputs['Bias'].default_value = 0.0; br.inputs['Brick Width'].default_value = w; br.inputs['Row Height'].default_value = h
    L.new(ad.outputs[0], br.inputs['Vector'])
    rp = N.new('ShaderNodeValToRGB'); rp.color_ramp.interpolation = 'CONSTANT'
    rp.color_ramp.elements[0].position = 0.0; rp.color_ramp.elements[0].color = (0, 0, 0, 1)
    rp.color_ramp.elements[1].position = soglia; rp.color_ramp.elements[1].color = (1, 1, 1, 1)
    L.new(br.outputs['Color'], rp.inputs['Fac'])
    es = N.new('ShaderNodeMath'); es.operation = 'MULTIPLY'; es.inputs[1].default_value = forza
    L.new(rp.outputs['Color'], es.inputs[0]); L.new(es.outputs[0], b.inputs['Emission Strength'])
    b.inputs['Emission Color'].default_value = (*acceso, 1)
    mixn = N.new('ShaderNodeMix'); mixn.data_type = 'RGBA'
    mixn.inputs[6].default_value = (*vetro, 1); mixn.inputs[7].default_value = (*muro, 1)
    L.new(br.outputs['Fac'], mixn.inputs[0]); L.new(mixn.outputs[2], b.inputs['Base Color'])
    return m


def palazzo(nome, sx, sy, h, mat, tetto, coll, loc=(0, 0, 0)):
    bm = bmesh.new(); uv = bm.loops.layers.uv.new()
    x, y = sx / 2, sy / 2
    v = [bm.verts.new(p) for p in ((-x, -y, 0), (x, -y, 0), (x, y, 0), (-x, y, 0), (-x, -y, h), (x, -y, h), (x, y, h), (-x, y, h))]
    for a, b_, c, d, w in ((0, 1, 5, 4, sx), (1, 2, 6, 5, sy), (2, 3, 7, 6, sx), (3, 0, 4, 7, sy)):
        f = bm.faces.new((v[a], v[b_], v[c], v[d]))
        for l, q in zip(f.loops, ((0, 0), (w, 0), (w, h), (0, h))):
            l[uv].uv = q
    f = bm.faces.new((v[4], v[5], v[6], v[7])); f.material_index = 1
    for l in f.loops:
        l[uv].uv = (0, 0)
    me = bpy.data.meshes.new(nome); bm.to_mesh(me); bm.free(); me.materials.append(mat); me.materials.append(tetto)
    o = bpy.data.objects.new(nome, me); o.location = loc; coll.objects.link(o)
    return o


STILI_CITTA = {
    # muri (uno o piu'), vetro, luce delle finestre, soglia (piu' alta = meno finestre accese), forza
    'C1': dict(muri=((0.03, 0.05, 0.10), (0.05, 0.07, 0.12), (0.02, 0.03, 0.06)), vetro=(0.01, 0.02, 0.05), luci=((1.0, 0.78, 0.40), (0.55, 0.8, 1.0)), soglia=0.6, forza=2.6),
    'C2': dict(muri=((0.80, 0.45, 0.30), (0.85, 0.65, 0.40), (0.60, 0.35, 0.35), (0.75, 0.70, 0.60)), vetro=(0.10, 0.07, 0.10), luci=((1.0, 0.70, 0.30),), soglia=0.8, forza=2.2),
    'C3': dict(muri=((0.02, 0.02, 0.04), (0.04, 0.02, 0.06)), vetro=(0.01, 0.01, 0.02), luci=((1.0, 0.15, 0.7), (0.1, 0.9, 1.0), (1.0, 0.85, 0.2)), soglia=0.66, forza=3.2),
}


def citta(coll, tipo, M, seme=7, piazza=1.05, passo=0.78):
    """Palazzi piccoli attorno all'origine (dove sta Pippo). Davanti (y negativo) sono piu' bassi, cosi' non lo coprono."""
    rnd = random.Random(seme); S = STILI_CITTA[tipo]
    mats = [mat_finestre('M27_%s_%d_%d' % (tipo, i, j), mu, S['vetro'], lu, S['soglia'], S['forza'])
            for i, mu in enumerate(S['muri']) for j, lu in enumerate(S['luci'])]
    out = []
    for ix in range(-7, 8):
        for iy in range(-4, 10):
            x, y = ix * passo, iy * passo
            if math.hypot(x, y) < piazza or (y < -0.3 and abs(x + y * 0.18) < 1.15):   # la piazza di Pippo e il viale verso la camera
                continue
            if rnd.random() < 0.08:
                continue
            sx, sy = rnd.uniform(0.38, 0.6), rnd.uniform(0.38, 0.6)
            alto = rnd.uniform(0.7, 1.5) if y < -0.5 else rnd.uniform(1.0, 2.3)
            if rnd.random() < 0.12 and y > 0.5:
                alto *= 1.25
            o = palazzo('Palazzo', sx, sy, alto, rnd.choice(mats), M['tetto'], coll, loc=(x + rnd.uniform(-0.07, 0.07), y + rnd.uniform(-0.07, 0.07), 0))
            out.append(o)
            if tipo == 'C3' and rnd.random() < 0.45:                        # insegne al neon
                col = rnd.choice(((1.0, 0.1, 0.6), (0.1, 0.9, 1.0), (1.0, 0.8, 0.1), (0.3, 1.0, 0.3)))
                mn = material('M27_neon_%d' % int(col[0] * 9 + col[1] * 90 + col[2] * 900), col, emit=col, emit_strength=14.0)
                zz = rnd.uniform(0.35, alto * 0.8)
                scatola('Insegna', sx * 0.7, 0.02, rnd.uniform(0.08, 0.22), mn, coll, loc=(o.location.x, o.location.y - sy / 2 - 0.012, zz), r=0.004)
    scatola('Strada', 40, 40, 0.1, M['bagnato'] if tipo == 'C3' else M['asfalto'], coll, loc=(0, 0, -0.05), r=0.01)
    return out


# --------------------------------------------------------------------------- video 027: popstar (richiesta dell'autore, 20 nov 2026) e microfono
def stella(nome, r, mat, coll, parent=None, loc=(0, 0, 0), rot=(0, 0, 0), sp=0.02):
    pts = [((r if i % 2 == 0 else r * 0.42) * math.sin(PI * i / 5), (r if i % 2 == 0 else r * 0.42) * math.cos(PI * i / 5)) for i in range(10)]
    return lastra(nome, pts, sp, mat, coll, parent=parent, loc=loc, rot=rot)


def _pantaloni(coll, R, mat, nome='Pantaloni'):
    for nm in 'LR':
        shape(nome + nm, 'cap:0.118:0.40', loc=(0, 0, -0.31), parent=R['hip' + nm], mat=mat, coll=coll)


def look_pop(coll, R, tipo, M):
    """Veste Pippo da popstar. P1 paillettes d'argento, P2 tuta fucsia con le stelle, P3 completo bianco e oro."""
    b = R['body']
    if tipo == 'P1':
        pa = material('M27_paillettes', (0.80, 0.82, 0.90), rough=0.42, metallic=0.9, emit=(0.6, 0.7, 1.0), emit_strength=0.25)
        _giacca(coll, R, pa, M['fucsia'])
        stella('StellaPetto', 0.075, M['oro'], coll, parent=b, loc=(0.13, -0.262, 0.60), rot=(0, 0.2, 0))
        for nm in 'LR':
            shape('Stivale' + nm, 'cap:0.128:0.22', loc=(0, 0, -0.43), parent=R['hip' + nm], mat=M['bianco'], coll=coll)
            props024.anello('Polsino' + nm, 0.092, 0.024, M['fucsia'], coll, parent=R['shoulder' + nm], loc=(0, 0, -0.42))
    elif tipo == 'P2':
        _giacca(coll, R, M['fucsia'], M['fucsia']); _pantaloni(coll, R, M['fucsia'])
        props024.anello('Cintura', 0.268, 0.03, M['oro'], coll, parent=b, loc=(0, 0, 0.12))
        for k, (x, z, r_) in enumerate(((0.0, 0.50, 0.085), (-0.14, 0.33, 0.05), (0.15, 0.30, 0.045))):
            stella('Stella%d' % k, r_, M['oro'], coll, parent=b, loc=(x, -0.268 + 0.02 * abs(x) * 4, z))
        for nm in 'LR':
            stella('StellaGamba' + nm, 0.05, M['oro'], coll, parent=R['hip' + nm], loc=(0, -0.122, -0.30))
    elif tipo == 'P3':
        _giacca(coll, R, M['bianco'], M['oro']); _pantaloni(coll, R, M['bianco'])
        props024.anello('Collana', 0.17, 0.014, M['oro'], coll, parent=b, loc=(0, -0.03, 0.70))
        stella('Medaglia', 0.07, M['oro'], coll, parent=b, loc=(0, -0.275, 0.56))
        for nm in 'LR':
            shape('Stivale' + nm, 'cap:0.128:0.20', loc=(0, 0, -0.45), parent=R['hip' + nm], mat=M['oro'], coll=coll)
            props024.anello('Polsino' + nm, 0.092, 0.024, M['oro'], coll, parent=R['shoulder' + nm], loc=(0, 0, -0.42))
        for s in (-1, 1):
            shape('Spallina', 'sphere', loc=(s * 0.27, 0, 0.70), scale=(0.09, 0.09, 0.05), parent=b, mat=M['oro'], coll=coll)


def microfono(coll, M, parent=None, nome='Microfono'):
    """Microfono a mano: manico lungo Z (centro nell'origine), testa d'argento in alto."""
    G = empty(nome, parent=parent, coll=coll)
    shape(nome + 'Manico', 'cyl:0.027:0.22', parent=G, mat=M['nero'], coll=coll)
    shape(nome + 'Testa', 'sphere', loc=(0, 0, 0.15), scale=(0.062, 0.062, 0.07), parent=G, mat=M['metallo'], coll=coll)
    props024.anello(nome + 'Anello', 0.05, 0.011, M['oro'], coll, parent=G, loc=(0, 0, 0.105))
    return G


def impugna_microfono(coll, R, M):
    """Microfono davanti alla bocca (figlio del busto) + direzione del braccio destro (lato +X) che porta la mano sul manico."""
    from mathutils import Vector
    G = microfono(coll, M, parent=R['body']); G.location = (0.0, -0.37, 0.80); G.rotation_euler = (-0.45, 0, 0)
    d = Vector((0.03 - 0.31, -0.42, 1.40 - 1.35)).normalized()                 # direzione del braccio: dalla spalla al fondo del manico
    return G, d


def braccio(R, lato, d, f=None):
    """Punta il braccio (lato 'L' o 'R') nella direzione d, come fa pippo2.emozione (rotazione QUATERNION); con f mette la chiave."""
    from mathutils import Vector
    sh = R['shoulder' + lato]; sh.rotation_mode = 'QUATERNION'
    sh.rotation_quaternion = Vector((0, 0, -1)).rotation_difference(Vector(d).normalized())
    if f is not None:
        sh.keyframe_insert('rotation_quaternion', frame=f)


def microfono_in_mano(coll, R, M):
    """Microfono figlio del polso destro di Pippo (+X): segue la mano in ogni movimento.
    Restituisce (microfono, direzione del braccio che lo porta alla bocca, direzione che lo tende verso il pubblico)."""
    from mathutils import Vector, Matrix, Euler
    d = Vector((0.03 - 0.31, -0.42, 1.40 - 1.35)).normalized()
    braccio(R, 'R', d); bpy.context.view_layer.update()
    G = microfono(coll, M)
    W = R['body'].matrix_world @ Matrix.Translation((0.0, -0.37, 0.80)) @ Euler((-0.45, 0, 0)).to_matrix().to_4x4()
    G.parent = R['elbowR']; G.matrix_parent_inverse = Matrix.Identity(4); G.matrix_basis = R['elbowR'].matrix_world.inverted() @ W
    return G, d, Vector((0.22, -0.86, 0.38)).normalized()
