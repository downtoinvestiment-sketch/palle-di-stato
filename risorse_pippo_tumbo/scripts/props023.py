"""Video 023 - IL CAROVITA (copione 18C v3): l'Italia in offerta in un supermercato nello spazio.
carrello(coll, tipo): 'kenney' (Mini Shop), 'filo' (carrello vero di filo cromato, maniglia rossa), 'hover' (fantascienza: pannelli luminosi, niente ruote).
mano(coll, tipo): 'alieno' (verde, tre dita lunghe e ventose), 'guanto' (guanto giallo da cucina), 'robot' (metallo a segmenti). Restituisce dict con
  radice e 'dita' (liste di perni da piegare con rotation_euler.x) e 'pollice'.
confezione(coll, tipo, font): 'blister' (scatola trasparente su cartone stampato), 'vaschetta' (vaschetta di polistirolo col film), 'barattolo' (vaso di vetro).
  Misure in metri del quartiere (circa 130 x 130 m): la confezione contiene head.py.
scaffale(coll, font): scaffale gigante del supermercato spaziale con la striscia dei prezzi e altri prodotti.
strappo(coll, centro, raggio): lo strappo nel cielo, bordi di carta frastagliati e dentro lo spazio nero con le stelle."""
import math, random, bpy, bmesh
from mathutils import Vector
from common import material, empty, shape
from set004 import obj, bx, cyl, ball_
PI = math.pi

def tubo(nome, a, b, r, mat, coll, parent=None):
    a = Vector(a); b = Vector(b); d = b - a
    o = cyl(nome, r, d.length, (0, 0, 0), mat, coll, parent=parent)
    o.rotation_mode = 'QUATERNION'; o.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d.normalized()); o.location = (a + b) / 2
    return o

def testo(coll, nome, body, size, mat, loc, rot=(PI / 2, 0, 0), parent=None, font=None, estrudi=0.02):
    cu = bpy.data.curves.new(nome, 'FONT'); cu.body = body; cu.size = size; cu.align_x = 'CENTER'; cu.align_y = 'CENTER'; cu.extrude = estrudi
    if font: cu.font = font
    o = bpy.data.objects.new(nome, cu); o.location = loc; o.rotation_euler = rot; o.parent = parent; coll.objects.link(o); cu.materials.append(mat); return o

# ------------------------------------------------------------------ carrelli (lunghi ~1 m, come un carrello vero)
def carrello(coll, tipo='filo', A=None):
    r = empty('Carrello_' + tipo, (0, 0, 0), None, coll)
    if tipo == 'kenney':
        o = A.modello('kenney/mini-shop/shopping-cart', posizione=(0, 0, 0), altezza=1.05, collezione=coll, appoggia=True); o.parent = r; return r
    if tipo == 'filo':
        cr = material('P23_cromo', (0.85, 0.86, 0.88), rough=0.18, metallic=1.0); rosso = material('P23_maniglia', (0.8, 0.05, 0.05), rough=0.4)
        nero = material('P23_gomma', (0.03, 0.03, 0.03), rough=0.7)
        # cestello: fondo stretto davanti (x 0.30), largo dietro (x 0.52), alto 0.45, da z 0.45 a 0.9; davanti y -0.45, dietro y +0.5
        def ang(y, z, lato):
            w = 0.30 + (y + 0.45) / 0.95 * 0.22; wz = w + (z - 0.45) * 0.12; return Vector((lato * wz / 2, y, z))
        for lato in (-1, 1):
            for z in (0.45, 0.9): tubo('CarBordo', ang(-0.45, z, lato), ang(0.5, z, lato), 0.009, cr, coll, r)
            for k in range(9):
                y = -0.45 + 0.95 * k / 8; tubo('CarFiloV', ang(y, 0.45, lato), ang(y, 0.9, lato), 0.004, cr, coll, r)
            for k in range(1, 5):
                z = 0.45 + 0.45 * k / 5; tubo('CarFiloH', ang(-0.45, z, lato), ang(0.5, z, lato), 0.004, cr, coll, r)
        for y in (-0.45, 0.5):
            for z in (0.45, 0.9): tubo('CarTraverso', ang(y, z, -1), ang(y, z, 1), 0.009 if y < 0 else 0.007, cr, coll, r)
            for k in range(1, 8):
                f = k / 8; tubo('CarFiloT', ang(y, 0.45, -1).lerp(ang(y, 0.45, 1), f), ang(y, 0.9, -1).lerp(ang(y, 0.9, 1), f), 0.004, cr, coll, r)
        for k in range(1, 8):
            f = k / 8; tubo('CarFondo', ang(-0.45, 0.45, -1).lerp(ang(-0.45, 0.45, 1), f), ang(0.5, 0.45, -1).lerp(ang(0.5, 0.45, 1), f), 0.004, cr, coll, r)
        for lato in (-1, 1):                                                                         # telaio e ruote
            tubo('CarGamba', (lato * 0.2, -0.4, 0.1), (lato * 0.17, -0.42, 0.45), 0.012, cr, coll, r)
            tubo('CarGamba', (lato * 0.27, 0.45, 0.1), (lato * 0.27, 0.5, 0.45), 0.012, cr, coll, r)
            tubo('CarBase', (lato * 0.2, -0.4, 0.1), (lato * 0.27, 0.45, 0.1), 0.012, cr, coll, r)
            tubo('CarManico', ang(0.5, 0.9, lato), (lato * 0.29, 0.68, 1.02), 0.011, cr, coll, r)
            for y in (-0.4, 0.45):
                w = cyl('CarRuota', 0.05, 0.03, (lato * (0.2 if y < 0 else 0.27), y, 0.05), nero, coll, rot=(0, PI / 2, 0), parent=r)
        tubo('CarManiglia', (-0.3, 0.68, 1.02), (0.3, 0.68, 1.02), 0.02, rosso, coll, r)
        return r
    # hover: pannelli di vetro azzurro con i bordi luminosi, anelli che galleggiano
    vetro = material('P23_vetroHover', (0.3, 0.8, 1.0), rough=0.05, emit=(0.2, 0.7, 1.0), emit_strength=0.4)
    try: vetro.surface_render_method = 'BLENDED'
    except Exception: pass
    vetro.node_tree.nodes['Principled BSDF'].inputs['Alpha'].default_value = 0.35
    neon = material('P23_neonHover', (0.2, 0.9, 1.0), rough=0.3, emit=(0.2, 0.9, 1.0), emit_strength=6.0)
    scuro = material('P23_hoverScuro', (0.08, 0.09, 0.12), rough=0.3, metallic=0.8)
    bx('HovFondo', (-0.32, -0.5, 0.42), (0.32, 0.5, 0.46), scuro, coll).parent = r
    for (p0, p1) in (((-0.32, -0.5, 0.46), (-0.3, 0.5, 0.92)), ((0.3, -0.5, 0.46), (0.32, 0.5, 0.92)), ((-0.32, -0.5, 0.46), (0.32, -0.48, 0.85)), ((-0.32, 0.48, 0.46), (0.32, 0.5, 0.92))):
        o = bx('HovVetro', p0, p1, vetro, coll); o.parent = r
    for (a, b) in (((-0.32, -0.5, 0.92), (-0.32, 0.5, 0.92)), ((0.32, -0.5, 0.92), (0.32, 0.5, 0.92)), ((-0.32, 0.5, 0.92), (0.32, 0.5, 0.92)), ((-0.32, -0.5, 0.85), (0.32, -0.5, 0.85))):
        tubo('HovNeon', a, b, 0.012, neon, coll, r)
    tubo('HovManiglia', (-0.3, 0.62, 1.0), (0.3, 0.62, 1.0), 0.02, neon, coll, r)
    for lato in (-1, 1): tubo('HovBraccio', (lato * 0.3, 0.5, 0.9), (lato * 0.3, 0.62, 1.0), 0.012, scuro, coll, r)
    for y in (-0.3, 0.3):
        t = bpy.data.meshes.new('Anello'); bm = bmesh.new(); bmesh.ops.create_circle(bm, segments=32, radius=0.2); bm.to_mesh(t); bm.free()
        o = obj('HovAnello', shared_ring(), (0, y, 0.22), (0.22, 0.22, 0.22), neon, coll, parent=r)
    l_ = bpy.data.lights.new('HovLuce', 'POINT'); l_.energy = 15; l_.color = (0.3, 0.8, 1.0); l_.use_shadow = False
    lo = bpy.data.objects.new('HovLuce', l_); coll.objects.link(lo); lo.parent = r; lo.location = (0, 0, 0.15)
    return r

def shared_ring():
    me = bpy.data.meshes.get('P23_anello')
    if me: return me
    me = bpy.data.meshes.new('P23_anello'); bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=False, segments=40, radius1=1.0, radius2=1.0, depth=0.12)
    bm.to_mesh(me); bm.free(); me.materials.append(None); return me

# ------------------------------------------------------------------ mani giganti (palmo ~1 m: si scala con root.scale)
def mano(coll, tipo='alieno'):
    D = dict(dita=[], pollice=None); r = D['radice'] = empty('Mano_' + tipo, (0, 0, 0), None, coll)
    if tipo == 'alieno':
        pelle = material('P23_alieno', (0.25, 0.75, 0.2), rough=0.45, coat=0.4, coat_rough=0.3); ventosa = material('P23_ventosa', (0.55, 0.95, 0.35), rough=0.35)
        unghia = material('P23_unghiaAl', (0.08, 0.12, 0.06), rough=0.25)
        dita = [(-0.27, 1.1), (0.0, 1.25), (0.27, 1.1)]; spess = 0.11; pal = (0.5, 0.26, 0.55)
    elif tipo == 'guanto':
        pelle = material('P23_guanto', (1.0, 0.78, 0.05), rough=0.3, coat=0.6, coat_rough=0.15); ventosa = pelle; unghia = pelle
        dita = [(-0.33, 0.85), (-0.11, 0.95), (0.11, 0.92), (0.33, 0.75)]; spess = 0.12; pal = (0.5, 0.26, 0.52)
    else:
        pelle = material('P23_robot', (0.75, 0.77, 0.8), rough=0.35, metallic=0.6); ventosa = material('P23_giunto', (0.12, 0.12, 0.14), rough=0.35, metallic=0.8)
        unghia = material('P23_luceRobot', (0.2, 0.7, 1.0), emit=(0.2, 0.7, 1.0), emit_strength=5.0)
        dita = [(-0.33, 0.85), (-0.11, 0.95), (0.11, 0.92), (0.33, 0.75)]; spess = 0.1; pal = (0.5, 0.24, 0.5)
    ball_('ManoPalmo', 1.0, (0, 0, 0), pelle, coll, parent=r, sc=pal)
    if tipo == 'guanto':
        shape('ManoPolso', 'cap:0.3:1.3', (0, 0, -1.05), parent=r, mat=pelle, coll=coll)
        shape('ManoRisvolto', 'cyl:0.36:0.18', (0, 0, -1.45), parent=r, mat=pelle, coll=coll)
    elif tipo == 'robot':
        shape('ManoPolso', 'cyl:0.24:1.2', (0, 0, -1.0), parent=r, mat=pelle, coll=coll)
        for z in (-0.55, -0.85, -1.15): shape('ManoAnello', 'cyl:0.27:0.05', (0, 0, z), parent=r, mat=ventosa, coll=coll)
        shape('ManoNucleo', 'sphere', (0, -0.15, 0.0), scale=(0.12, 0.03, 0.12), parent=r, mat=unghia, coll=coll)
    else:
        shape('ManoPolso', 'cap:0.24:1.3', (0, 0, -0.95), parent=r, mat=pelle, coll=coll)
    for k, (x, L) in enumerate(dita):
        catena = []; par = r; z0 = pal[2] * 0.85
        p = empty('Dito%d' % k, (x, 0, z0), par, coll); catena.append(p); seg = L / 3
        for j in range(3):
            if tipo == 'robot': shape('DitoSeg', 'cyl:%g:%g' % (spess * 0.9, seg * 0.8), (0, 0, seg * 0.5), parent=p, mat=pelle, coll=coll); ball_('Giunto', spess, (0, 0, 0), ventosa, coll, parent=p)
            else: shape('DitoSeg', 'cap:%g:%g' % (spess * (1 - 0.1 * j), seg), (0, 0, seg * 0.5), parent=p, mat=pelle, coll=coll)
            if j < 2:
                q = empty('Dito%dF%d' % (k, j), (0, 0, seg), p, coll); catena.append(q); p = q
        if tipo == 'alieno': ball_('Ventosa', spess * 1.35, (0, -0.02, seg), ventosa, coll, parent=p, sc=(1, 0.7, 1))
        elif tipo == 'robot': ball_('Punta', spess * 0.7, (0, 0, seg), unghia, coll, parent=p)
        else: ball_('Punta', spess * 0.95, (0, 0, seg), pelle, coll, parent=p)
        D['dita'].append(catena)
    pp = empty('Pollice', (pal[0] * 0.8, -0.1, -0.1), r, coll); pp.rotation_euler = (0, -0.9, -0.5); catena = [pp]; seg = 0.4; p = pp
    for j in range(2):
        shape('PolliceSeg', 'cap:%g:%g' % (spess * 1.25, seg), (0, 0, seg * 0.5), parent=p, mat=pelle, coll=coll)
        if j < 1: q = empty('PolliceF', (0, 0, seg), p, coll); catena.append(q); p = q
    if tipo == 'alieno': ball_('Ventosa', spess * 1.4, (0, -0.02, seg), ventosa, coll, parent=p, sc=(1, 0.7, 1))
    D['pollice'] = catena
    return D

def piega(D, f, quanto):
    """chiude la mano (0 aperta, 1 pugno) e mette la chiave al fotogramma f."""
    for catena in D['dita']:
        for p in catena: p.rotation_euler = (-1.1 * quanto, 0, 0); p.keyframe_insert('rotation_euler', frame=f)
    for j, p in enumerate(D['pollice']):
        base = (0, -0.9, -0.5) if j == 0 else (0, 0, 0); p.rotation_euler = (base[0] - 0.6 * quanto, base[1] + 0.5 * quanto * (j == 0), base[2]); p.keyframe_insert('rotation_euler', frame=f)

# ------------------------------------------------------------------ confezioni dell'Italia (in metri di quartiere)
def confezione(coll, tipo='blister', font=None, centro=(0, 0, 0)):
    cx, cy, cz = centro; r = empty('Confezione_' + tipo, centro, None, coll)
    rosso = material('P23_rosso', (0.85, 0.05, 0.05), rough=0.5); bianco = material('P23_bianco', (1, 1, 1), rough=0.5)
    giallo = material('P23_giallo', (1.0, 0.85, 0.05), rough=0.5); verde = material('P23_verde', (0.0, 0.55, 0.25), rough=0.5)
    def plastica(nome, alpha=0.12, rough=0.05):
        m = material(nome, (0.9, 0.95, 1.0), rough=rough, spec=0.8)
        try: m.surface_render_method = 'BLENDED'
        except Exception: pass
        b = m.node_tree.nodes['Principled BSDF']; b.inputs['Alpha'].default_value = alpha
        try: b.inputs['Coat Weight'].default_value = 0.8
        except Exception: pass
        return m
    if tipo == 'blister':
        W, Dp, H = 66.0, 72.0, 48.0
        bx('BliCartone', (-W - 6, -Dp - 6, -2.0), (W + 6, Dp + 6, -0.05), material('P23_cartone', (0.82, 0.12, 0.1), rough=0.8), coll).parent = r
        me = bpy.data.meshes.new('BliCupola'); bm = bmesh.new(); bmesh.ops.create_cube(bm, size=2.0)
        bmesh.ops.bevel(bm, geom=[e for e in bm.edges], offset=0.18, segments=4, affect='EDGES')
        for v in bm.verts: v.co.x *= W; v.co.y *= Dp; v.co.z = (v.co.z + 1) * 0.5 * H
        bm.to_mesh(me); bm.free(); [setattr(p, 'use_smooth', True) for p in me.polygons]; me.materials.append(plastica('P23_blister'))
        o = bpy.data.objects.new('BliCupola', me); coll.objects.link(o); o.parent = r; o.visible_shadow = False
        # etichetta davanti, sul cartone che sale (come i giocattoli)
        bx('BliTesta', (-W - 6, Dp + 2, -2), (W + 6, Dp + 6, 60), material('P23_cartone', (0.82, 0.12, 0.1), rough=0.8), coll).parent = r
        testo(coll, 'BliTitolo', 'ITALIA', 22, giallo, (0, -Dp - 9, 64), font=font, parent=r, estrudi=1.0)
        stella = shape('BliStella', 'cyl:16:1.5', (W - 8, -Dp - 6, 50), rot=(PI / 2, 0, 0), parent=r, mat=giallo, coll=coll)
        testo(coll, 'BliPrezzo', '2,99 €', 7, rosso, (W - 8, -Dp - 7.8, 52), font=font, parent=r, estrudi=0.4)
        testo(coll, 'BliOfferta', 'OFFERTA', 4, rosso, (W - 8, -Dp - 7.8, 44), font=font, parent=r, estrudi=0.3)
        testo(coll, 'BliSotto', 'CON PIPPO INCLUSO', 5, bianco, (0, -Dp - 9, 52), font=font, parent=r, estrudi=0.4)
    elif tipo == 'vaschetta':
        W, Dp = 72.0, 78.0
        po = material('P23_polistirolo', (0.95, 0.95, 0.92), rough=0.9)
        me = bpy.data.meshes.new('Vaschetta'); bm = bmesh.new(); bmesh.ops.create_cube(bm, size=2.0)
        bmesh.ops.bevel(bm, geom=[e for e in bm.edges], offset=0.12, segments=3, affect='EDGES')
        for v in bm.verts: v.co.x *= W; v.co.y *= Dp; v.co.z = (v.co.z - 1) * 0.5 * 8.0
        bm.to_mesh(me); bm.free(); me.materials.append(po); o = bpy.data.objects.new('Vaschetta', me); coll.objects.link(o); o.parent = r
        film = plastica('P23_film', 0.08, 0.2)
        nt = film.node_tree; nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 0.08; bp = nt.nodes.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = 0.3
        nt.links.new(nz.outputs['Fac'], bp.inputs['Height']); nt.links.new(bp.outputs['Normal'], nt.nodes['Principled BSDF'].inputs['Normal'])
        me = bpy.data.meshes.new('Film'); bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=48, v_segments=24, radius=1.0)
        for v in bm.verts:
            if v.co.z < 0: v.co.z = 0
            v.co.x *= W * 1.02; v.co.y *= Dp * 1.02; v.co.z *= 46
        bm.to_mesh(me); bm.free(); [setattr(p, 'use_smooth', True) for p in me.polygons]; me.materials.append(film)
        o = bpy.data.objects.new('Film', me); coll.objects.link(o); o.parent = r; o.visible_shadow = False
        et = bx('VasEtichetta', (W * 0.25, -Dp - 0.5, 4), (W * 0.95, -Dp + 0.5, 32), bianco, coll); et.parent = r; et.rotation_euler = (-0.25, 0, 0)
        testo(coll, 'VasT1', 'ITALIA', 6, material('P23_nero', (0.02, 0.02, 0.02), rough=0.5), (W * 0.6, -Dp - 1.2, 26), font=font, parent=r, estrudi=0.2)
        testo(coll, 'VasT2', '€/kg  2,99', 4, rosso, (W * 0.6, -Dp - 1.2, 18), font=font, parent=r, estrudi=0.2)
        testo(coll, 'VasT3', 'DA CONSUMARSI ENTRO IERI', 2.2, material('P23_nero', (0.02, 0.02, 0.02), rough=0.5), (W * 0.6, -Dp - 1.2, 10), font=font, parent=r, estrudi=0.1)
    else:
        R, H = 82.0, 70.0
        vetro = plastica('P23_vetro', 0.1, 0.02)
        me = bpy.data.meshes.new('Barattolo'); bm = bmesh.new()
        bmesh.ops.create_cone(bm, cap_ends=True, segments=64, radius1=R, radius2=R, depth=H)
        for v in bm.verts: v.co.z += H / 2
        bm.to_mesh(me); bm.free(); [setattr(p, 'use_smooth', True) for p in me.polygons]; me.materials.append(vetro)
        o = bpy.data.objects.new('Barattolo', me); coll.objects.link(o); o.parent = r; o.visible_shadow = False
        oro = material('P23_coperchio', (0.95, 0.7, 0.2), rough=0.25, metallic=1.0)
        cyl('Coperchio', R * 0.93, 9.0, (0, 0, H + 4.5), oro, coll, parent=r)
        me = bpy.data.meshes.new('Etichetta'); bm = bmesh.new()
        bmesh.ops.create_cone(bm, cap_ends=False, segments=64, radius1=R * 1.01, radius2=R * 1.01, depth=16)
        bm.to_mesh(me); bm.free(); me.materials.append(material('P23_etiBar', (0.95, 0.9, 0.75), rough=0.6))
        o = bpy.data.objects.new('EtiBarattolo', me); coll.objects.link(o); o.parent = r; o.location = (0, 0, 16)
        testo(coll, 'BarT1', "ITALIA SOTT'OLIO", 7, rosso, (0, -R - 1.5, 18), font=font, parent=r, estrudi=0.3)
        testo(coll, 'BarT2', 'OFFERTA 2,99 €', 4.5, verde, (0, -R - 1.5, 11), font=font, parent=r, estrudi=0.3)
    return r

# ------------------------------------------------------------------ lo scaffale gigante nello spazio
def scaffale(coll, font=None, x0=-260.0, x1=260.0, y=0.0, piani=(0.0, 130.0), prof=110.0):
    metallo = material('P23_scaffale', (0.82, 0.83, 0.86), rough=0.35, metallic=0.9); bianco = material('P23_bianco', (1, 1, 1), rough=0.5)
    giallo = material('P23_giallo', (1.0, 0.85, 0.05), rough=0.5); rosso = material('P23_rosso', (0.85, 0.05, 0.05), rough=0.5)
    r = empty('Scaffale', (0, 0, 0), None, coll)
    for z in piani:
        bx('ScaPiano', (x0, y - prof, z - 4.0), (x1, y + prof, z - 2.0), metallo, coll).parent = r
        bx('ScaPrezzi', (x0, y - prof - 1.2, z - 9.0), (x1, y - prof, z - 2.0), bianco, coll).parent = r
    for x in (x0, x1): bx('ScaMontante', (x - 3, y + prof - 4, piani[0] - 60), (x + 3, y + prof + 2, piani[-1] + 140), metallo, coll).parent = r
    bx('ScaFondo', (x0, y + prof, piani[0] - 60), (x1, y + prof + 2, piani[-1] + 140), material('P23_fondoSca', (0.75, 0.76, 0.8), rough=0.5), coll).parent = r
    # il cartellino dell'Italia sulla striscia e altri prodotti sui lati
    bx('ScaCartellino', (-22, y - prof - 1.6, piani[0] - 9.5), (22, y - prof - 1.2, piani[0] - 1.5), giallo, coll).parent = r
    testo(coll, 'ScaPrezzo', 'ITALIA  2,99 €', 4.5, rosso, (0, y - prof - 1.9, piani[0] - 5.5), font=font, parent=r, estrudi=0.2)
    prodotti = [('LUNA', 9.99, (0.85, 0.85, 0.8)), ('MARTE', 1.49, (0.8, 0.3, 0.1)), ('SATURNO', 4.50, (0.9, 0.75, 0.4)), ('PLUTONE', 0.10, (0.6, 0.65, 0.85))]
    for k, (nome, pr, col) in enumerate(prodotti):
        x = (-170 if k % 2 == 0 else 170) + (0 if k < 2 else 0); z = piani[0] if k < 2 else piani[1]
        if k >= 2: x = -150 + 300 * (k - 2)
        sc = bx('Scatola' + nome, (x - 40, y - 60, z - 2), (x + 40, y + 60, z + 95), material('P23_sc' + nome, col, rough=0.6), coll); sc.parent = r
        testo(coll, 'ScaT' + nome, nome, 13, bianco, (x, y - 61.5, z + 60), font=font, parent=r, estrudi=0.8)
        testo(coll, 'ScaP' + nome, ('%.2f €' % pr).replace('.', ','), 4.5, rosso, (x, y - prof - 1.9, z - 5.5), font=font, parent=r, estrudi=0.2)
    return r

# ------------------------------------------------------------------ lo strappo nel cielo
def strappo(coll, centro, raggio, verso=(0, -1, 0), seme=7):
    """un buco frastagliato nel cielo: disco di spazio nero con stelle e un bordo di carta bianca strappata. Fronte verso 'verso'."""
    rnd = random.Random(seme); r = empty('Strappo', centro, None, coll)
    spazio = bpy.data.materials.new('P23_spazio'); spazio.use_nodes = True; nt = spazio.node_tree; nt.nodes.clear(); L = nt.links.new
    tc = nt.nodes.new('ShaderNodeTexCoord'); vo = nt.nodes.new('ShaderNodeTexVoronoi'); vo.inputs['Scale'].default_value = 60.0; L(tc.outputs['Generated'], vo.inputs['Vector'])
    mr = nt.nodes.new('ShaderNodeMapRange'); L(vo.outputs['Distance'], mr.inputs['Value']); mr.inputs['From Min'].default_value = 0.0; mr.inputs['From Max'].default_value = 0.05
    mr.inputs['To Min'].default_value = 6.0; mr.inputs['To Max'].default_value = 0.0
    em = nt.nodes.new('ShaderNodeEmission'); em.inputs['Color'].default_value = (0.9, 0.95, 1.0, 1); L(mr.outputs[0], em.inputs['Strength'])
    bg = nt.nodes.new('ShaderNodeEmission'); bg.inputs['Color'].default_value = (0.01, 0.0, 0.03, 1); bg.inputs['Strength'].default_value = 1.0
    ad = nt.nodes.new('ShaderNodeAddShader'); L(em.outputs[0], ad.inputs[0]); L(bg.outputs[0], ad.inputs[1])
    out = nt.nodes.new('ShaderNodeOutputMaterial'); L(ad.outputs[0], out.inputs['Surface'])
    carta = material('P23_carta', (0.92, 0.95, 1.0), rough=0.9, emit=(0.75, 0.85, 1.0), emit_strength=0.6)
    n = 46; pts = []
    for k in range(n):
        a = 2 * PI * k / n; rr = raggio * (0.78 + 0.32 * rnd.random()) * (1.0 if k % 2 else 0.86); pts.append((rr * math.cos(a), 0.0, rr * 0.75 * math.sin(a)))
    me = bpy.data.meshes.new('Buco'); me.from_pydata([(0, 0, 0)] + pts, [], [(0, 1 + k, 1 + (k + 1) % n) for k in range(n)]); me.update(); me.materials.append(spazio)
    o = bpy.data.objects.new('Buco', me); coll.objects.link(o); o.parent = r; o.visible_shadow = False
    vs = []; fs = []
    for k, p in enumerate(pts):                                                                       # bordo: brandelli di carta che pendono verso l'esterno
        p = Vector(p); d = p.normalized(); w = raggio * rnd.uniform(0.06, 0.16)
        vs += [tuple(p * 0.98), tuple(p + d * w + Vector((0, -raggio * 0.02, 0))), tuple(Vector(pts[(k + 1) % n]) + Vector(pts[(k + 1) % n]).normalized() * w * 0.6)]
        fs.append((3 * k, 3 * k + 1, 3 * k + 2))
    me2 = bpy.data.meshes.new('BordoStrappo'); me2.from_pydata(vs, [], fs); me2.update(); me2.materials.append(carta)
    o2 = bpy.data.objects.new('BordoStrappo', me2); coll.objects.link(o2); o2.parent = r; o2.location = (0, -0.5, 0)
    v = Vector(verso).normalized(); r.rotation_mode = 'QUATERNION'; r.rotation_quaternion = Vector((0, -1, 0)).rotation_difference(v)
    return r
