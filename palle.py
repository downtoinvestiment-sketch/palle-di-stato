"""Palle di stato: genera in Blender (bpy) le «countryball» con la bandiera di qualsiasi paese, occhi da cartone ed espressioni.
Le bandiere sono in modelli_satira/bandiere/png/<codice>.png (codici ISO a due lettere, es. it, fr, de, us; vedi paesi.json).

Uso come modulo:
    import palle
    it = palle.palla('it', posizione=(0, 0, 0), espressione='felice')
    palle.espressione(it, 'arrabbiato', frame=48)      # cambia faccia a un fotogramma
    palle.guarda(it, (2, -1, 1), frame=60)              # sposta lo sguardo verso un punto
Prova:  python3 palle.py  -> prova_palle.png (cinque palle in fila)"""
import os, math, bpy
from mathutils import Vector
QUI = os.path.dirname(os.path.abspath(__file__))
BANDIERE = os.path.join(QUI, 'modelli_satira', 'bandiere', 'png')
ESPRESSIONI = {                      # occhi: (scala x, scala z) ; sopracciglia: (angolo, altezza) ; palpebra: 0 aperto -> 1 chiuso
    'normale':    dict(occhi=(1.0, 1.0), ciglia=None, palpebra=0.0),
    'felice':     dict(occhi=(1.05, 0.55), ciglia=None, palpebra=0.0, curva=True),
    'arrabbiato': dict(occhi=(1.0, 0.85), ciglia=(-28, 0.05), palpebra=0.25),
    'triste':     dict(occhi=(0.95, 0.9), ciglia=(24, 0.08), palpebra=0.2),
    'sorpreso':   dict(occhi=(1.25, 1.3), ciglia=(0, 0.07), palpebra=0.0),
    'furbo':      dict(occhi=(1.0, 0.8), ciglia=(-12, 0.04), palpebra=0.5),
    'annoiato':   dict(occhi=(1.0, 1.0), ciglia=None, palpebra=0.55),
}

def _mat_colore(nome, col, emissione=0.0, rough=0.5):
    m = bpy.data.materials.get(nome)
    if m: return m
    m = bpy.data.materials.new(nome); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*col, 1); b.inputs['Roughness'].default_value = rough
    if emissione: b.inputs['Emission Color'].default_value = (*col, 1); b.inputs['Emission Strength'].default_value = emissione
    return m

def _mat_contorno():
    m = bpy.data.materials.get('PDS_contorno')
    if m: return m
    m = bpy.data.materials.new('PDS_contorno'); m.use_nodes = True; N = m.node_tree.nodes; N.clear()
    o = N.new('ShaderNodeOutputMaterial'); e = N.new('ShaderNodeEmission'); e.inputs['Color'].default_value = (0.01, 0.01, 0.01, 1)
    m.node_tree.links.new(e.outputs[0], o.inputs['Surface']); m.use_backface_culling = True; return m

def _mat_bandiera(codice):
    nome = 'PDS_bandiera_' + codice; m = bpy.data.materials.get(nome)
    if m: return m
    m = bpy.data.materials.new(nome); m.use_nodes = True; N = m.node_tree.nodes; L = m.node_tree.links
    b = N['Principled BSDF']; b.inputs['Roughness'].default_value = 0.42; b.inputs['Coat Weight'].default_value = 0.1
    tc = N.new('ShaderNodeTexCoord'); sp = N.new('ShaderNodeSeparateXYZ'); L.new(tc.outputs['Object'], sp.inputs[0])
    # proiezione frontale (come nei disegni delle countryball): x -> larghezza, z -> altezza della bandiera
    mu = N.new('ShaderNodeMath'); mu.operation = 'MULTIPLY_ADD'; mu.inputs[1].default_value = 0.5; mu.inputs[2].default_value = 0.5; L.new(sp.outputs['X'], mu.inputs[0])
    mv = N.new('ShaderNodeMath'); mv.operation = 'MULTIPLY_ADD'; mv.inputs[1].default_value = 0.5; mv.inputs[2].default_value = 0.5; L.new(sp.outputs['Z'], mv.inputs[0])
    cb = N.new('ShaderNodeCombineXYZ'); L.new(mu.outputs[0], cb.inputs['X']); L.new(mv.outputs[0], cb.inputs['Y'])
    im = N.new('ShaderNodeTexImage'); im.extension = 'EXTEND'
    im.image = bpy.data.images.load(os.path.join(BANDIERE, codice + '.png'), check_existing=True)
    L.new(cb.outputs[0], im.inputs['Vector']); L.new(im.outputs['Color'], b.inputs['Base Color']); return m

def _contorno(o, spessore):
    s = o.modifiers.new('Contorno', 'SOLIDIFY'); s.thickness = spessore; s.offset = 1.0; s.use_flip_normals = True; s.material_offset = 1
    o.data.materials.append(_mat_contorno())

def _sfera(nome, r, coll, seg=64):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=seg // 2, radius=r); o = bpy.context.object; o.name = nome
    for c in o.users_collection: c.objects.unlink(o)
    coll.objects.link(o); bpy.ops.object.shade_smooth() if bpy.context.view_layer.objects.get(o.name) else None
    for p in o.data.polygons: p.use_smooth = True
    return o

def palla(codice, posizione=(0, 0, 0), raggio=1.0, espressione='normale', pupille=False, coll=None, nome=None, verso=0.0):
    """Crea una palla con la bandiera <codice>. posizione = punto a terra; verso = rotazione (0 = guarda verso -Y)."""
    coll = coll or bpy.context.scene.collection; nome = nome or 'Palla_' + codice.upper()
    root = bpy.data.objects.new(nome, None); coll.objects.link(root); root.location = posizione; root.rotation_euler.z = verso
    corpo = _sfera(nome + '_corpo', raggio, coll); corpo.parent = root; corpo.location = (0, 0, raggio)
    corpo.data.materials.append(_mat_bandiera(codice)); _contorno(corpo, 0.035 * raggio)
    bianco = _mat_colore('PDS_bianco', (0.95, 0.95, 0.95), rough=0.3); nero = _mat_colore('PDS_nero', (0.01, 0.01, 0.01), rough=0.4)
    occhi = {}
    for lato, sx in (('L', -1), ('R', 1)):
        pivot = bpy.data.objects.new(nome + '_occhio' + lato, None); coll.objects.link(pivot); pivot.parent = corpo
        d = Vector((sx * 0.34, -0.9, 0.16)).normalized() * raggio * 0.985; pivot.location = d
        pivot.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
        o = _sfera(nome + '_bianco' + lato, 0.21 * raggio, coll, 32); o.parent = pivot; o.scale = (1.0, 1.25, 0.32)
        o.data.materials.append(bianco); _contorno(o, 0.022 * raggio)
        pu = None
        if pupille:
            pu = _sfera(nome + '_pupilla' + lato, 0.075 * raggio, coll, 24); pu.parent = pivot; pu.location = (0, 0, 0.06 * raggio); pu.scale = (1, 1, 0.35); pu.data.materials.append(nero)
        bpy.ops.mesh.primitive_cube_add(size=1.0); ci = bpy.context.object; ci.name = nome + '_ciglio' + lato
        for c in ci.users_collection: c.objects.unlink(ci)
        coll.objects.link(ci); ci.parent = pivot; ci.scale = (0.36 * raggio, 0.07 * raggio, 0.03 * raggio); ci.data.materials.append(nero)
        occhi[lato] = dict(pivot=pivot, bianco=o, pupilla=pu, ciglio=ci, sx=sx)
    root['pds'] = dict(raggio=raggio); root['_occhi'] = [occhi[k]['pivot'].name for k in 'LR']
    _OCCHI[root.name] = occhi
    espressione_imposta(root, espressione)
    return root

_OCCHI = {}
def espressione_imposta(root, nome, frame=None):
    """Imposta l'espressione (vedi ESPRESSIONI). Con frame, mette le chiavi a quel fotogramma."""
    e = ESPRESSIONI[nome]; r = root['pds']['raggio']
    for lato, oc in _OCCHI[root.name].items():
        sx = oc['sx']; ex, ez = e['occhi']
        a = e.get('palpebra', 0.0); hz = 1.25 * ez * (1.0 - 0.6 * a)                    # palpebra: l'occhio si schiaccia dall'alto
        oc['bianco'].scale = (1.0 * ex, hz, 0.32); oc['bianco'].location = (0, -0.21 * r * (1.25 * ez - hz) * 0.8, 0)
        if oc['pupilla']: oc['pupilla'].location.y = oc['bianco'].location.y
        top = oc['bianco'].location.y + 0.21 * r * hz
        if e.get('ciglia'):
            ang, h = e['ciglia']; oc['ciglio'].location = (0, top + 0.04 * r + h * r, 0.05 * r); oc['ciglio'].rotation_euler = (0, 0, math.radians(ang) * -sx); oc['ciglio'].hide_render = False
        elif a > 0:
            oc['ciglio'].location = (0, top, 0.06 * r); oc['ciglio'].rotation_euler = (0, 0, 0); oc['ciglio'].hide_render = False
        else:
            oc['ciglio'].location = (0, top, 0.05 * r); oc['ciglio'].rotation_euler = (0, 0, 0); oc['ciglio'].hide_render = True
        if frame is not None:
            oc['bianco'].keyframe_insert('scale', frame=frame); oc['bianco'].keyframe_insert('location', frame=frame)
            for p in ('location', 'rotation_euler', 'hide_render'): oc['ciglio'].keyframe_insert(p, frame=frame)
espressione = espressione_imposta

def guarda(root, punto, frame=None):
    """Sposta le pupille (se ci sono) verso un punto del mondo."""
    r = root['pds']['raggio']
    for oc in _OCCHI[root.name].values():
        if not oc['pupilla']: continue
        d = oc['pivot'].matrix_world.inverted() @ Vector(punto); d.z = 0; d = d.normalized() * min(0.09 * r, d.length) if d.length else d
        oc['pupilla'].location = (d.x, d.y, 0.06 * r)
        if frame is not None: oc['pupilla'].keyframe_insert('location', frame=frame)

if __name__ == '__main__':
    bpy.ops.wm.read_factory_settings(use_empty=True); sc = bpy.context.scene
    sc.render.engine = 'BLENDER_EEVEE'; sc.view_settings.view_transform = 'Standard'; sc.render.resolution_x, sc.render.resolution_y = 1600, 700; sc.eevee.taa_render_samples = 16
    w = bpy.data.worlds.new('W'); sc.world = w; w.use_nodes = True; w.node_tree.nodes['Background'].inputs[0].default_value = (0.55, 0.7, 0.9, 1); w.node_tree.nodes['Background'].inputs[1].default_value = 0.45
    bpy.ops.mesh.primitive_plane_add(size=40); pl = bpy.context.object; pl.data.materials.append(_mat_colore('PDS_pavimento', (0.35, 0.5, 0.25), rough=0.9))
    for i, (c, e) in enumerate((('it', 'felice'), ('fr', 'furbo'), ('de', 'normale'), ('gb', 'annoiato'), ('us', 'sorpreso'))):
        palla(c, posizione=((i - 2) * 2.4, 0, 0), espressione=e, pupille=True)
    s = bpy.data.lights.new('Sole', 'SUN'); s.energy = 3.5; so = bpy.data.objects.new('Sole', s); sc.collection.objects.link(so); so.rotation_euler = (math.radians(50), math.radians(10), math.radians(-35))
    cd = bpy.data.cameras.new('Cam'); cam = bpy.data.objects.new('Cam', cd); sc.collection.objects.link(cam); sc.camera = cam
    cam.location = (0, -16, 3.0); cam.rotation_euler = (Vector((0, 0, 1.0)) - cam.location).to_track_quat('-Z', 'Y').to_euler(); cd.lens = 42
    sc.render.filepath = os.path.join(QUI, 'prova_palle.png'); bpy.ops.render.render(write_still=True); print('FATTO', sc.render.filepath)
