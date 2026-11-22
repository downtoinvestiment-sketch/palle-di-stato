"""Scelte dell'autore (16 nov 2026): A2 albero largo, B1 prato folto, C5 mattoni rossi, D1 tegole colorate, E2 cielo con nuvole grandi.
kitlook.py - veste le scene di Pippo e Tumbo con la libreria asset (assets/pt_assets.py):
cielo HDRI, prato / asfalto / intonaco / tegole / legno con texture vere, alberi a sagoma, cespugli, fiori, lampioni.
Uso (dopo aver creato la camera):  kitlook.upgrade(scene, M, envc, prc)"""
import sys, os, math, random, bpy
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'assets')))
import pt_assets as A

WALLC = [(1.0, 0.86, 0.42), (1.0, 0.62, 0.50), (0.50, 0.80, 1.0), (0.98, 0.96, 0.90), (0.98, 0.95, 0.88), (0.55, 0.90, 0.62)]
ROOFC = [(0.86, 0.22, 0.12), (0.92, 0.36, 0.14), (0.70, 0.16, 0.14), (0.22, 0.36, 0.62)]
TOWERC = [(0.95, 0.52, 0.30), (0.98, 0.80, 0.36), (0.30, 0.66, 0.80), (0.96, 0.94, 0.90), (0.90, 0.42, 0.42), (0.52, 0.76, 0.50)]
def _k(c, g, sat=1.0): return tuple(min(2.5, (x ** sat) * g) for x in c)
# muri per indice di casa: 0 = casa di Pippo (mattoni rossi, scelta C5), 3 = casa di Gualtiero (intonaco chiaro)
WALLMAT = [('red_brick', 1.4, None), ('Plaster001', 2.4, _k((1.0, 0.62, 0.50), 1.15, 1.9)), ('PaintedPlaster017', 2.4, _k((0.50, 0.80, 1.0), 1.15, 1.9)),
           ('painted_plaster_wall', 2.4, (1.25, 1.2, 1.05)), ('rustic_stone_wall_02', 2.0, None), ('Plaster001', 2.4, _k((0.55, 0.90, 0.62), 1.15, 1.9))]
TREES = ((9.5, 4.0), (10.0, -5.5), (-13.0, 9.5), (5.5, 15.5), (-7, 16.5), (16, 14), (-30, 14), (-21, -6.0), (14, -19), (-24, -19))


def setmat(o, mat):
    """per gli oggetti creati con set004.obj/bx (mesh condivisa, materiale sull'oggetto): MAI A.applica."""
    o.material_slots[0].material = mat

def remap(old, new):
    if old is not None and old is not new: old.user_remap(new)

def variants(aid, n, area, height, seed=1, coll=None, shadow=True, z=0.0, keep=None):
    """sparge n esemplari scegliendo a caso tra le varianti del modello (ciuffi d'erba, fiori, cespugli)."""
    rnd = random.Random(seed); out = []; bases = {}
    for i in range(n):
        v = rnd.randrange(0, 6) if keep is None else rnd.choice(keep)
        if v not in bases:
            bases[v] = A.modello(aid, variante=v, collezione=coll, nome='PT_%s_v%d' % (aid, v)); r = bases[v]
            kids = list(r.children_recursive); bases[v] = (r, kids, A._altezza(kids) or 1.0); used = True
        else:
            r0, kids, h0 = bases[v]; r = bpy.data.objects.new('PT_%s_%03d' % (aid, i), None); (coll or bpy.context.scene.collection).objects.link(r); cp = {}
            for o in kids:
                c = o.copy(); (coll or bpy.context.scene.collection).objects.link(c); cp[o] = c
            for o, c in cp.items(): c.parent = cp.get(o.parent, r)
        h0 = bases[v][2]; hh = rnd.uniform(*height) if isinstance(height, (tuple, list)) else height
        s = hh / h0; r.scale = (s, s, s); r.rotation_euler[2] = rnd.uniform(0, 6.283)
        r.location = (rnd.uniform(area[0], area[1]), rnd.uniform(area[2], area[3]), z)
        if not shadow: A.niente_ombra(r)
        out.append(r)
    return out

def tune_cutouts(gain=1.9, sat=1.25):
    """sagome: foglie piu' chiare e verdi (le foto sono scure rispetto ai personaggi)."""
    for m in bpy.data.materials:
        if m.name.startswith('PT_sagoma_') and m.node_tree and not m.node_tree.nodes.get('PT_hsv'):
            nt = m.node_tree; b = nt.nodes.get('Principled BSDF'); tx = next(n for n in nt.nodes if n.type == 'TEX_IMAGE')
            hs = nt.nodes.new('ShaderNodeHueSaturation'); hs.name = 'PT_hsv'; hs.inputs['Saturation'].default_value = sat; hs.inputs['Value'].default_value = gain
            nt.links.new(tx.outputs['Color'], hs.inputs['Color']); nt.links.new(hs.outputs['Color'], b.inputs['Base Color'])

TREE_MIX = (('island_tree_01', 5.8, 7.6), ('tree_small_02', 4.8, 6.2), ('island_tree_02', 5.5, 7.2), ('island_tree_01', 6.2, 8.0), ('island_tree_03', 4.5, 5.8), ('tree_small_02', 5.5, 7.0))

def add_trees(envc, kinds=TREE_MIX, background=True):
    """alberi veri (sagome fotografiche) al posto di quelli a palla: specie, altezze e verso mescolati
    (l'autore: "non fare tutto uguale"; A2 = island_tree_01 resta il piu' frequente). Restituisce gli oggetti creati."""
    for o in list(bpy.data.objects):
        if o.name.startswith(('Tronco', 'Chioma')): bpy.data.objects.remove(o)
    rnd = random.Random(7); out = []
    def one(x, y, near):
        aid, h0, h1 = kinds[rnd.randrange(len(kinds))]
        o = A.albero_cartonato(aid, posizione=(x, y, 0), altezza=rnd.uniform(h0, h1), ombra=near, collezione=envc)
        if rnd.random() < 0.5: o.scale.x = -1
        out.append(o)
    for (x, y) in TREES: one(x, y, abs(x) < 18 and abs(y) < 18)
    if background:
        for k in range(16): one(rnd.uniform(-60, 60), rnd.uniform(20.5, 24.0), False)
        for k in range(12): one(rnd.uniform(-60, 60), rnd.uniform(-30.0, -26.0), False)
    return out

def upgrade(scene, M, envc, prc, sky='sunflowers_puresky', sky_rot=43.0, sky_force=1.1, preset='equilibrato',
            trees=True, extras=True, exposure=0.25, keep_sun=0.0, grass_dim=3.0, tree_gain=1.9):
    sc = A.qualita_eevee(preset=preset, riflessi=False, scena=scene)
    scene.view_settings.exposure = exposure
    try: scene.render.use_motion_blur = True; scene.render.motion_blur_shutter = 0.1
    except Exception: pass
    # --- cielo: luce, ombre e sfondo
    try: A.scarica_hdri(sky, '4k')
    except Exception as ex: print('4k', ex)
    A.cielo(sky, forza=sky_force, rotazione=sky_rot, ris='4k')
    for o in list(bpy.data.objects):
        if o.name.startswith(('CloudW', 'Puff')): bpy.data.objects.remove(o)
    sun = bpy.data.objects.get('Sun')
    if sun:
        if keep_sun > 0: sun.data.energy = keep_sun
        else: bpy.data.objects.remove(sun)
    # --- materiali veri al posto dei colori piatti
    g = bpy.data.materials.get
    remap(g('S_park'), A.materiale('Grass001', dimensione=grass_dim, rilievo=0.8, tinta=(1.05, 1.35, 0.7), ruvidita=1.5))
    remap(g('S_asphalt'), A.materiale('asphalt_02', dimensione=4.0, rilievo=0.8, tinta=(0.8, 0.8, 0.85)))
    remap(g('S_sidewalk'), A.materiale('PavingStones070', dimensione=2.0, rilievo=0.8))
    remap(g('S_stone'), A.materiale('PavingStones036', dimensione=1.5, rilievo=1.0))
    remap(g('S_chim'), A.materiale('red_brick', dimensione=1.2, rilievo=1.0))
    remap(g('S_wood'), A.materiale('brown_planks_03', dimensione=1.6))
    remap(g('S_hedge'), A.materiale('Grass004', dimensione=1.2, rilievo=1.5, tinta=(0.75, 1.3, 0.55), ruvidita=1.5, nome='PT_hedge'))
    remap(g('S_concrete'), A.materiale('Concrete034', dimensione=3.0, rilievo=0.6))
    for i, (aid, dim, tint) in enumerate(WALLMAT):                  # ogni casa un muro diverso (l'autore: "non fare le case tutte uguali")
        remap(g('S_wall%d' % i), A.materiale(aid, dimensione=dim, rilievo=0.8, tinta=tint, nome='PT_wall%d' % i))
    for i, c in enumerate(ROOFC): remap(g('S_roof%d' % i), A.materiale('grey_roof_tiles_02', dimensione=1.6, rilievo=1.2, tinta=_k(c, 2.2), nome='PT_roof%d' % i))
    for i, c in enumerate(TOWERC): remap(g('S_tower%d' % i), A.materiale('PaintedPlaster017', dimensione=3.0, rilievo=0.5, tinta=_k(c, 1.15, 1.7), nome='PT_tower%d' % i))
    prato = bpy.data.objects.get('Prato')
    if prato: A.niente_ombra(prato)
    # --- alberi veri (sagome fotografiche) al posto di quelli a palla
    if trees:
        add_trees(envc)
    tune_cutouts(tree_gain)
    # --- dettagli vicini: cespugli, ciuffi d'erba, fiori, lampioni, panchina
    if extras:
        variants('shrub_02', 5, (4.5, 12.0, 6.0, 8.5), (0.8, 1.3), seed=2, coll=envc)
        variants('grass_medium_01', 14, (-8.5, 12.0, -7.0, 6.0), (0.14, 0.24), seed=4, coll=envc, shadow=False)
        variants('dandelion_01', 14, (-8.5, 12.0, -7.0, 6.0), (0.09, 0.15), seed=6, coll=envc, shadow=False)
        variants('celandine_01', 10, (-8.5, 12.0, -7.0, 6.0), (0.09, 0.15), seed=8, coll=envc, shadow=False)
        for x in (-22, -4, 14, 32): A.modello('street_lamp_01', posizione=(x, -8.15, 0.05), altezza=4.2, rotazione=90, collezione=envc)
        A.modello('painted_wooden_bench', posizione=(6.0, -7.4, 0.0), rotazione=180, altezza=0.9, collezione=envc)
    return sc
