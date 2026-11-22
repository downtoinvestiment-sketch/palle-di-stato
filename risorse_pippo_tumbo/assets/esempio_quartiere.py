"""Esempio: una via di quartiere dove case e alberi sono tutti diversi, costruita solo con la libreria.
Uso:  python esempio_quartiere.py uscita.png [veloce|equilibrato|alto|massimo] [seme]
Cambiando il seme cambia la disposizione di case, alberi e auto.
I personaggi (Pippo, Tumbo, Gualtiero...) si aggiungono poi come in qualunque altra scena."""
import bpy, math, os, random, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pt_assets as A

args = sys.argv[1:]
USCITA = args[0] if args else '/tmp/quartiere.png'
PRESET = args[1] if len(args) > 1 else 'equilibrato'
rnd = random.Random(int(args[2]) if len(args) > 2 else 7)
ROT_CASA = -90   # i modelli Kenney guardano verso -Y: cosi' le facciate danno sulla strada
ROT_LAMP = 0

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = A.qualita_eevee(preset=PRESET, riflessi=False)   # niente superfici lucide: senza riflessi e' il 25% piu' veloce
coll = sc.collection
A.cielo('kloofendal_48d_partly_cloudy_puresky', forza=1.0, rotazione=200)


def piano(nome, x0, x1, y0, y1, z, mat):
    me = bpy.data.meshes.new(nome)
    me.from_pydata([(x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z)], [], [(0, 1, 2, 3)])
    ob = bpy.data.objects.new(nome, me)
    coll.objects.link(ob)
    A.applica(ob, mat)
    A.niente_ombra(ob)
    return ob


# --- terreno: prato, strada, marciapiedi (texture realistiche)
piano('Prato', -120, 120, -60, 160, 0.0, A.materiale('Grass001', dimensione=3.0, tinta=(0.8, 1.1, 0.65)))
piano('Strada', -3.5, 3.5, -60, 160, 0.02, A.materiale('asphalt_02', dimensione=4.0))
marciapiede = A.materiale('PavingStones070', dimensione=2.0)
piano('MarciapiedeSx', -5.3, -3.5, -60, 160, 0.06, marciapiede)
piano('MarciapiedeDx', 3.5, 5.3, -60, 160, 0.06, marciapiede)

# --- case e alberi: 21 tipi di casa e 12 di albero (Kenney), ognuno con misura e posizione un po' diverse
tipi = [f'kenney/city-kit-suburban/building-type-{c}' for c in 'abcdefghijklmnopqrstu']
rnd.shuffle(tipi)
alberi = ['kenney/nature-kit/tree_oak', 'kenney/nature-kit/tree_fat', 'kenney/nature-kit/tree_default',
          'kenney/nature-kit/tree_detailed', 'kenney/nature-kit/tree_cone', 'kenney/nature-kit/tree_blocks',
          'kenney/nature-kit/tree_pineRoundA', 'kenney/nature-kit/tree_pineTallA_detailed',
          'kenney/city-kit-suburban/tree-large', 'kenney/city-kit-suburban/tree-small',
          'kenney/nature-kit/tree_oak_dark', 'kenney/nature-kit/tree_default_dark']
i = 0
for lato in (-1, 1):
    y = -4 + rnd.uniform(0, 4)
    while y < 110:
        A.modello(tipi[i % len(tipi)], posizione=(lato * (11.5 + rnd.uniform(-0.5, 1.5)), y, 0),
                  altezza=rnd.uniform(6.5, 9.0), rotazione=ROT_CASA * lato)
        passo = rnd.uniform(13, 16)
        # un albero nello spazio tra questa casa e la prossima, mai davanti alla facciata
        A.modello(alberi[i % len(alberi)], posizione=(lato * rnd.uniform(7.5, 10), y + passo / 2, 0),
                  altezza=rnd.uniform(5, 8.5), rotazione=rnd.uniform(0, 360))
        i += 1
        y += passo

# --- alberi realistici (sagome) dietro le case e in fondo alla via
veri = ['island_tree_01', 'island_tree_02', 'tree_small_02', 'jacaranda_tree', 'searsia_lucida']
A.bosco_cartonato(veri, 14, area=(-40, -24, -10, 110), altezza=(9, 15), seme=3)
A.bosco_cartonato(veri, 14, area=(24, 40, -10, 110), altezza=(9, 15), seme=5)
A.bosco_cartonato(veri, 10, area=(-30, 30, 118, 140), altezza=(11, 17), seme=8)

# --- auto parcheggiate e lampioni
auto = ['sedan', 'suv', 'taxi', 'van', 'hatchback-sports', 'police', 'truck', 'suv-luxury']
for k, y in enumerate((6, 19, 33, 52, 71)):
    lato = -1 if k % 2 else 1
    A.modello('kenney/car-kit/' + rnd.choice(auto), posizione=(lato * 2.3, y + rnd.uniform(-2, 2), 0.03),
              altezza=1.6, rotazione=0 if lato > 0 else 180)
for y in range(14, 110, 30):
    A.modello('kenney/city-kit-roads/light-curved', posizione=(-4.5, y, 0.06), altezza=5.5, rotazione=ROT_LAMP)
    A.modello('kenney/city-kit-roads/light-curved', posizione=(4.5, y + 15, 0.06), altezza=5.5, rotazione=ROT_LAMP + 180)

# --- camera verticale 9:16, ad altezza d'occhi in mezzo alla via
cam = bpy.data.objects.new('Camera', bpy.data.cameras.new('Camera'))
coll.objects.link(cam)
cam.location = (-2.6, -10, 2.0)
cam.data.lens = 24
bersaglio = bpy.data.objects.new('Bersaglio', None)
coll.objects.link(bersaglio)
bersaglio.location = (4.5, 30, 5.5)
cam.constraints.new('TRACK_TO').target = bersaglio
sc.camera = cam
for o in bpy.data.objects:   # le sagome guardano la camera
    if o.name.startswith('PT_sagoma_') and not o.constraints:
        c = o.constraints.new('LOCKED_TRACK')
        c.target = cam
        c.track_axis = 'TRACK_NEGATIVE_Y'
        c.lock_axis = 'LOCK_Z'

sc.render.filepath = USCITA
t0 = time.time()
bpy.ops.render.render(write_still=True)
print('RENDER SALVATO', USCITA, 'preset', PRESET, '%.0f s' % (time.time() - t0))
