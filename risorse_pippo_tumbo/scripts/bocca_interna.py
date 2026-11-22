"""Interno della bocca uguale per tutti i personaggi (22 novembre 2026, chiesto dall'autore guardando Bialada): arcata di denti
bianchi che segue il bordo di sopra della bocca aperta (circa il 40 % dell'apertura) e lingua rosa in basso, come in bialada.py.
Le bocche (labbra, bordo, interno scuro) restano quelle di ogni personaggio: si cambiano solo denti e lingua.

    import bocca_interna
    bocca_interna.applica(dentro, coll, togli=(vecchi_denti, vecchia_lingua))
dentro = l'oggetto scuro dell'interno della bocca (una sfera scalata: BoccaDentro, RO_Bocca, CA_Bocca...). Denti e lingua
diventano suoi figli, costruiti nelle sue coordinate (sfera di raggio 1), quindi si aprono, si chiudono e si spostano con lui."""
import math, bpy, bmesh


def _lin(c):
    f = lambda x: x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4
    return (f(c[0] / 255), f(c[1] / 255), f(c[2] / 255), 1.0)


def _mat(nome, srgb, rough, coat=0.0):
    m = bpy.data.materials.get(nome)
    if m: return m
    m = bpy.data.materials.new(nome); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = _lin(srgb); b.inputs['Roughness'].default_value = rough
    try: b.inputs['Coat Weight'].default_value = coat
    except KeyError: pass
    return m


def _falce(coll, parent, nome, mat, xw, v0, v1, fuori=0.04, nu=28, nv=6):
    """striscia curva dentro la bocca: x da -xw a xw; per ogni x va dalla quota v0 alla quota v1 (frazioni dell'apertura,
    0 = bordo di sopra, 1 = bordo di sotto) e sta appoggiata davanti alla superficie della sfera."""
    bm = bmesh.new(); vs = []
    for j in range(nv + 1):
        for i in range(nu + 1):
            x = -xw + 2 * xw * i / nu; top = math.sqrt(max(0.0, 1 - x * x))
            v = v0 + (v1 - v0) * j / nv; z = top - 2 * top * v
            y = -math.sqrt(max(0.0, 1 - x * x - z * z)) - fuori
            vs.append(bm.verts.new((x, y, z)))
    for j in range(nv):
        for i in range(nu):
            a = j * (nu + 1) + i
            bm.faces.new((vs[a], vs[a + 1], vs[a + nu + 2], vs[a + nu + 1]))
    me = bpy.data.meshes.new(nome); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    o = bpy.data.objects.new(nome, me); coll.objects.link(o); o.parent = parent; me.materials.append(mat)
    return o


def applica(dentro, coll, togli=(), prefisso=None):
    """mette denti e lingua nuovi dentro 'dentro' e toglie i vecchi oggetti in 'togli'. Restituisce (denti, lingua)."""
    for o in togli:
        if o is not None and o.name in bpy.data.objects: bpy.data.objects.remove(o, do_unlink=True)
    p = prefisso if prefisso is not None else dentro.name.split('_')[0] + '_'
    if dentro.material_slots:                                                    # sfondo dietro i denti: rosso molto scuro (22 nov sera)
        sl = dentro.material_slots[0]; sl.link = 'OBJECT'; sl.material = _mat('BOCCA_interno', (58, 8, 12), 0.6)
    denti = _falce(coll, dentro, p + 'DentiArcata', _mat('BOCCA_denti', (250, 247, 238), 0.3, coat=0.3), 0.77, 0.03, 0.42)
    lingua = _falce(coll, dentro, p + 'LinguaInterna', _mat('BOCCA_lingua', (206, 100, 104), 0.45), 0.55, 0.66, 0.96)
    return denti, lingua


def sfere(ap, coll):
    """per le bocche fatte a sfere (Labbra, BoccaDentro, Lingua, Denti sotto l'empty della bocca aperta)"""
    figli = {o.name.split('.')[0].split('_', 1)[-1]: o for o in ap.children}
    return applica(figli['BoccaDentro'], coll, togli=(figli.get('Lingua'), figli.get('Denti')))
