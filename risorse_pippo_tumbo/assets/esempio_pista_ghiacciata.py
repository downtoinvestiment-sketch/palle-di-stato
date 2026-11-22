"""Esempio: set realistico 'pista ghiacciata nel bosco' costruito solo con la libreria.
Uso:  python esempio_pista_ghiacciata.py uscita.png [veloce|equilibrato|alto|massimo]
I personaggi (Pippo, Tumbo...) si aggiungono poi come in qualunque altra scena."""
import bpy, bmesh, math, os, random, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pt_assets as A

args = sys.argv[1:]
USCITA = args[0] if args else '/tmp/pista.png'
PRESET = args[1] if len(args) > 1 else 'equilibrato'

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = A.qualita_eevee(preset=PRESET)      # risoluzione piena 1080x1920, pochi campioni
coll = sc.collection

# --- cielo: luce, ombre del sole e sfondo arrivano tutti dall'HDRI
A.cielo('snowy_field', forza=1.2, rotazione=84)   # rotazione: sposta il sole (qui alle spalle, a sinistra)

# --- terreno innevato con i cumuli attorno alla pista
def griglia(nome, lato, n, quota):
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=n, y_segments=n, size=lato / 2)
    for v in bm.verts:
        v.co.z = quota(v.co.x, v.co.y)
    me = bpy.data.meshes.new(nome); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    ob = bpy.data.objects.new(nome, me); coll.objects.link(ob)
    return ob

RX, RY = 15.0, 10.0   # semiassi della pista
def quota_neve(x, y):
    d = math.sqrt((x / RX) ** 2 + (y / RY) ** 2)
    bordo = 0.55 * math.exp(-((d - 1.12) / 0.10) ** 2)           # cumulo spalato attorno al ghiaccio
    onde = 0.18 * math.sin(x * 0.21 + 1.3) * math.cos(y * 0.17) + 0.07 * math.sin(x * 0.9) * math.sin(y * 0.8)
    return (-0.12 if d < 1.0 else 0.02) + bordo + (onde if d > 1.25 else 0)

neve = griglia('Neve', 160, 220, quota_neve)
A.niente_ombra(neve)                      # il terreno non deve proiettare ombra: tempo risparmiato
A.applica(neve, A.materiale('Snow006', dimensione=3.0, rilievo=1.2))

# --- ghiaccio lucido: i riflessi arrivano da qualita_eevee() + materiale poco ruvido con vernice
bpy.ops.mesh.primitive_circle_add(vertices=96, radius=1, fill_type='NGON', location=(0, 0, 0))
ghiaccio = bpy.context.object; ghiaccio.name = 'Ghiaccio'; ghiaccio.scale = (RX * 1.04, RY * 1.04, 1)
A.applica(ghiaccio, A.materiale('Ice004', dimensione=5.0, rilievo=0.15, ruvidita=0.25, tinta=(1.5, 1.95, 2.4), vernice=1.0))

# --- bosco: sagome sullo sfondo (costo quasi zero) + pochi alberi veri vicino alla tribuna
A.bosco_cartonato('fir_tree_01', 40, area=(-38, 38, 24, 48), altezza=(19, 27), seme=4)
A.bosco_cartonato('fir_tree_01', 6, area=(-36, -22, 0, 20), altezza=(14, 19), seme=9)
A.bosco_cartonato('fir_tree_01', 6, area=(22, 36, 0, 20), altezza=(14, 19), seme=11)
A.sparpaglia('fir_sapling_medium', 3, area=(-24, 24, 16, 21), altezza=(5, 8), seme=3)

# --- tribuna di legno
legno = A.materiale('brown_planks_03', dimensione=2.0)
for i in range(4):
    bpy.ops.mesh.primitive_cube_add(location=(0, 12.6 + i * 0.9, 0.45 + i * 0.45))
    g = bpy.context.object; g.scale = (11, 0.45, 0.45 + i * 0.45); g.location.z = (0.45 + i * 0.45)
    A.applica(g, legno)

# --- oggetti di scena
A.modello('street_lamp_01', posizione=(-6.5, 11.6, 0.15), altezza=4.2)
A.modello('street_lamp_01', posizione=(6.5, 11.6, 0.15), altezza=4.2, rotazione=180)
A.modello('painted_wooden_bench', posizione=(-3.6, 10.9, 0.2), rotazione=8, altezza=0.9)
A.modello('wooden_bucket_01', posizione=(-1.9, 10.8, 0.25), altezza=0.45)
A.modello('tree_stump_01', posizione=(3.2, 10.9, 0.2), altezza=0.6)
A.sparpaglia('boulder_01', 3, area=(4.2, 7.5, 10.4, 11.2), altezza=(0.5, 1.1), seme=2)

# --- fiocchi di neve
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.03)
bpy.ops.object.shade_smooth()
fiocco = bpy.context.object; fiocco.name = 'Fiocco'
mf = bpy.data.materials.new('Fiocco'); mf.use_nodes = True
b = mf.node_tree.nodes['Principled BSDF']; b.inputs['Base Color'].default_value = (1, 1, 1, 1)
b.inputs['Emission Color'].default_value = (1, 1, 1, 1); b.inputs['Emission Strength'].default_value = 0.6
fiocco.data.materials.append(mf)
rnd = random.Random(5)
for i in range(260):
    c = fiocco.copy(); coll.objects.link(c)
    c.location = (rnd.uniform(-14, 14), rnd.uniform(-13, 20), rnd.uniform(0.3, 11)); s = rnd.uniform(0.6, 1.8); c.scale = (s, s, s)
    c.visible_shadow = False

# --- camera verticale 9:16
cam = bpy.data.objects.new('Camera', bpy.data.cameras.new('Camera')); coll.objects.link(cam)
cam.location = (1.2, -8.6, 1.75); cam.data.lens = 24
bersaglio = bpy.data.objects.new('Bersaglio', None); coll.objects.link(bersaglio); bersaglio.location = (0, 7, 3.4)
t = cam.constraints.new('TRACK_TO'); t.target = bersaglio
sc.camera = cam
# la camera va creata PRIMA delle sagome se vuoi che la seguano: qui le giriamo a mano
for o in bpy.data.objects:
    if o.name.startswith('PT_sagoma_') and not o.constraints:
        c = o.constraints.new('LOCKED_TRACK'); c.target = cam; c.track_axis = 'TRACK_NEGATIVE_Y'; c.lock_axis = 'LOCK_Z'
# niente sfocatura: a questa distanza non si vede e costa circa il 10% del tempo
sc.render.filepath = USCITA
t0 = time.time()
bpy.ops.render.render(write_still=True)
print('RENDER SALVATO', USCITA, 'preset', PRESET, '%.0f s' % (time.time() - t0))
