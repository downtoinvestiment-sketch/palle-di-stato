"""posti.py - posti ricchi costruiti in una scena vuota, senza il quartiere: isola dei pirati, campeggio nel bosco, centro citta'.
Niente mondi piatti: terreno con rilievo, alberi realistici, tanti dettagli vicini, modelli veri dove ci sono, auto grandi.
Come modulo in un episodio:  import posti;  info = posti.isola_pirati(0.0, envc, prc)   ->  dict(h=altezza del terreno, cam=(posizione, mira, lente), luci=[...])
Da terminale, per le schede:  python posti.py N3      (un posto per volta: scrive ../t016/opt3/N3.png)"""
import sys, os, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, numpy as np
from mathutils import Vector
from common import *
from render_setup import *
import set004, kitlook, pippo, tumbo, paesaggi as PS
from set004 import obj, bx, cyl, ball_, MB
from props007 import text_obj
A = kitlook.A; PI = math.pi
MIX = [k[0] for k in kitlook.TREE_MIX]

def _alb(coll, x0, h, aid, x, y, alt, vista=0, near=False):
    o = A.albero_cartonato(aid, posizione=(x0 + x, y, h(x, y) - 0.2), altezza=alt, collezione=coll, vista=vista, ombra=near)
    if (vista + int(x * 7)) % 2: o.scale.x = -1
    return o
def _luce(coll, loc, energy, color, r=0.3):
    l_ = bpy.data.lights.new('PtX', 'POINT'); o_ = bpy.data.objects.new('PtX', l_); coll.objects.link(o_); o_.location = loc; l_.energy = energy; l_.color = color; l_.shadow_soft_size = r; return o_

def bandiera_pirata(coll, loc, alta=5.2, nome='Bandiera'):
    """bandiera nera con teschio e ossa su un palo di legno: guarda verso -Y."""
    r = empty(nome, loc, None, coll); legno = material('S_palo_legno', (0.36, 0.22, 0.1), rough=0.8); nero = material('S_band_nera', (0.02, 0.02, 0.025), rough=0.85); osso = material('S_band_osso', (0.95, 0.94, 0.88), rough=0.6)
    shape(nome + 'Palo', 'cyl:0.07:%g' % alta, (0, 0, alta / 2), parent=r, mat=legno, coll=coll); shape(nome + 'Pomo', 'sphere', (0, 0, alta + 0.05), scale=(0.11, 0.11, 0.11), parent=r, mat=legno, coll=coll)
    t = bx(nome + 'Telo', (0.07, -0.02, alta - 1.25), (1.87, 0.02, alta - 0.1), nero, coll); t.parent = r
    cx, cz = 0.97, alta - 0.62
    shape(nome + 'Cranio', 'sphere', (cx, -0.035, cz + 0.08), scale=(0.2, 0.03, 0.2), parent=r, mat=osso, coll=coll); shape(nome + 'Mascella', 'sphere', (cx, -0.035, cz - 0.1), scale=(0.12, 0.03, 0.1), parent=r, mat=osso, coll=coll)
    for sx in (-1, 1):
        shape(nome + 'Orbita', 'sphere', (cx + sx * 0.075, -0.06, cz + 0.09), scale=(0.05, 0.02, 0.06), parent=r, mat=nero, coll=coll)
        shape(nome + 'Osso', 'cyl:0.035:0.95', (cx, -0.03, cz - 0.05), rot=(0, sx * 0.9, 0), parent=r, mat=osso, coll=coll)
    return r

# ---------------------------------------------------------------------------------------------------- isola dei pirati
def isola_pirati(x0, envc, prc):
    """spiaggia, colli con alberi, scogli, mare, galeone vero, forziere, cannone, botti."""
    h = PS.isola(); Md = lambda *a, **k: PS.modello(A, k.pop('coll', envc), x0, h, *a, **k)
    PS.terreno(envc, x0, A.materiale('sand_01', dimensione=4.0, rilievo=1.0, tinta=(1.15, 1.08, 0.9)), h, xr=(-90, 90), yr=(-25, 130), passo=1.0); PS.mare(envc, x0)
    Md('treasure_chest', 2.5, 0.8, 0.8, rot=-25, tri=12000, coll=prc); Md('cannon_01', -3.0, 1.6, 1.05, rot=205, coll=prc)
    Md('wooden_barrels_01', 4.0, 2.9, 1.15, rot=20, tri=9000); Md('Barrel_01', 4.9, 1.9, 0.95); Md('wooden_crate_01', 3.3, 4.0, 0.6, rot=15); Md('wooden_crate_01', -4.6, 3.4, 0.6, rot=-30)
    for sgn in (-1, 1): shape('Xtesoro', 'cyl:0.07:1.5', (x0 + 1.0, 2.7, h(1.0, 2.7) + 0.04), rot=(PI / 2, 0, sgn * PI / 4), mat=material('S_xrossa', (0.85, 0.05, 0.04), rough=0.6), coll=prc)
    bandiera_pirata(prc, (x0 + 3.4, 5.8, h(3.4, 5.8)))
    Md('namaqualand_boulder_04', -8.6, 6.6, 2.3, rot=40); Md('namaqualand_boulder_03', 9.6, 5.2, 1.8, rot=200); Md('namaqualand_boulder_04', 12.5, 9.5, 2.8, rot=120); Md('namaqualand_boulder_03', -6.2, 2.4, 0.9, rot=75)
    Md('namaqualand_cliff_01', -14.0, 15.0, 6.5, rot=20); Md('namaqualand_cliff_01', 17.0, 15.5, 5.5, rot=200); Md('coast_land_rocks_02', -15.5, -1.5, 1.4, rot=140, tri=20000); Md('coast_rocks_05', 6.4, -2.6, 1.0, rot=30, tri=12000)
    PS.pulisci()
    Md('sand_rocks_small_01', -2.2, 4.6, 0.5, rot=10, tri=12000); Md('sand_rocks_small_01', 6.0, 7.4, 0.5, rot=140, tri=12000); PS.sparsi2(A, envc, x0, h, 'boulder_01', 5, (-11, 11, -3, 10), (0.3, 0.7), 31)
    PS.sparsi(kitlook, envc, x0, h, 'grass_medium_01', 34, (-12, 12, -4, 12), (0.3, 0.55), 32); PS.sparsi2(A, envc, x0, h, 'wild_rooibos_bush', 9, (-13, 13, 3, 14), (0.6, 1.0), 33)
    PS.sparsi(kitlook, envc, x0, h, 'shrub_02', 12, (-18, 18, 7, 20), (0.9, 1.6), 34, shadow=True)
    for k, (xx, yy, hh, nm) in enumerate(((-5.2, 5.0, 6.6, 'island_tree_02'), (5.8, 6.4, 7.2, 'island_tree_01'), (-9.0, 10.5, 6.5, 'island_tree_03'), (8.2, 3.0, 4.6, 'quiver_tree_01'), (-13, 15, 8.0, 'island_tree_01'), (-17, 14, 7.0, 'island_tree_02'), (-11, 19, 7.5, 'island_tree_03'),
                                          (15, 13, 7.5, 'island_tree_01'), (19, 12, 6.5, 'island_tree_02'), (13, 18, 7.0, 'island_tree_03'), (-6.5, 13.5, 6.0, 'island_tree_01'), (10.5, 12.5, 6.5, 'island_tree_02'), (-20, 9, 6.0, 'quiver_tree_01'), (22, 7, 6.0, 'island_tree_01'))):
        _alb(envc, x0, h, nm, xx, yy, hh, vista=k, near=k < 3)
    kitlook.tune_cutouts(1.9)
    Md('dutch_ship_large_01', 2.5, 34.0, 21.0, rot=98, tri=40000, z=-1.2, lato=1024); Md('dutch_ship_medium', 38.0, 80.0, 15.0, rot=60, tri=15000, z=-1.0)
    PS.sparsi(kitlook, envc, x0, h, 'grass_medium_01', 3, (-3.2, -1.6, -5.2, -4.4), (0.5, 0.7), 35, via=())      # primo piano: ciuffi vicino alla camera
    PS.pulisci()
    return dict(h=h, cam=((1.2, -7.5, 2.4), (0.0, 3.0, 2.0), 21), luci=[])

# ---------------------------------------------------------------------------------------------------- campeggio nel bosco
def campeggio(x0, envc, prc):
    """radura tra le colline: abeti e pini veri, sottobosco, fuoco acceso, tende, ceppo con l'ascia, lanterna."""
    base = PS.colline(amp=6.0, rx=10.5, ry=9.5, cy=3.0, bordo=18.0, lontano=12.0, fase=13.0)
    def h(x, y):
        q = math.exp(-(((x + 10.5) / 6.5) ** 2 + ((y - 14.5) / 4.0) ** 2) * 1.2); return base(x, y) * (1 - q) - 1.3 * q
    Md = lambda *a, **k: PS.modello(A, k.pop('coll', envc), x0, h, *a, **k)
    PS.terreno(envc, x0, A.materiale('Grass001', dimensione=3.0, rilievo=0.8, tinta=(0.7, 1.0, 0.5), ruvidita=1.5), h, passo=1.0, xr=(-80, 80), yr=(-25, 150)); PS.mare(envc, x0, z=-0.45, colore=(0.04, 0.26, 0.36), nome='Lago')
    me = bpy.data.meshes.new('Radura'); n_ = 40                                                 # terra battuta attorno al fuoco
    me.from_pydata([(x0 + 0.4, 2.6, 0.02)] + [(x0 + 0.4 + 3.6 * math.cos(i / n_ * 2 * PI) * (1 + 0.12 * math.sin(i * 1.7)), 2.6 + 3.0 * math.sin(i / n_ * 2 * PI) * (1 + 0.12 * math.cos(i * 2.3)), 0.02) for i in range(n_)], [], [(0, i + 1, (i + 1) % n_ + 1) for i in range(n_)]); me.update()
    ro = bpy.data.objects.new('Radura', me); envc.objects.link(ro); me.materials.append(A.materiale('forrest_ground_01', dimensione=3.0, rilievo=1.0)); ro.visible_shadow = False
    lago = ((-10.5, 14.5, 7.5),); PS.bosco(A, envc, x0, h, ('fir_tree_01', 'pine_tree_01', 'island_tree_01', 'fir_tree_01', 'tree_small_02'), 190, r0=11.0, r1=85.0, alt=(9.0, 15.0), seme=61, ombra_vicini=6, evita=lago)
    PS.bosco(A, envc, x0, h, ('fir_sapling_medium', 'pine_sapling_medium', 'fir_sapling'), 34, r0=9.5, r1=24.0, alt=(1.6, 3.4), seme=62, evita=lago)
    _alb(envc, x0, h, 'fir_tree_01', -8.2, 3.5, 12.5, vista=1, near=True); _alb(envc, x0, h, 'pine_tree_01', 8.6, 4.6, 13.0, vista=2, near=True)
    kitlook.tune_cutouts(1.9)
    PS.sparsi(kitlook, envc, x0, h, 'fern_02', 40, (-11, 11, -5, 12), (0.45, 0.85), 63, via=((0.7, 0.0, 1.6), (0.4, 2.6, 3.4))); PS.sparsi(kitlook, envc, x0, h, 'grass_medium_01', 80, (-12, 12, -6, 13), (0.22, 0.45), 64, via=((0.7, 0.0, 1.2), (0.4, 2.6, 3.0)))
    PS.sparsi(kitlook, envc, x0, h, 'dandelion_01', 18, (-9, 9, -4, 10), (0.12, 0.2), 65, via=((0.4, 2.6, 3.0),)); PS.sparsi(kitlook, envc, x0, h, 'shrub_02', 26, (-16, 16, 6, 18), (0.9, 2.0), 66, shadow=True, via=((0.4, 2.6, 5.5), (-10.5, 14.5, 6.5)))
    PS.sparsi2(A, envc, x0, h, 'boulder_01', 4, (-9, 9, 6, 11), (0.6, 1.3), 67); Md('rock_moss_set_01', -7.6, 7.2, 1.9, rot=30, tri=9000)
    Md('stone_fire_pit', 0.4, 2.6, 0.45, coll=prc); fu, pf = PS.fuoco(prc, (x0 + 0.4, 2.6, 0.12), 1.0, 900)
    Md('dead_tree_trunk', -1.9, 2.3, 0.5, rot=75, tri=8000, coll=prc); Md('tree_stump_01', 2.6, 1.7, 0.6, tri=7000, coll=prc); Md('wooden_axe', 2.95, 1.45, 0.75, rot=40, coll=prc)
    Md('folding_wooden_stool', 2.0, 3.5, 0.5, rot=200, coll=prc); Md('Lantern_01', 2.6, 1.7, 0.36, tri=6000, z=0.6, coll=prc); pl = _luce(prc, (x0 + 2.6, 1.6, 0.85), 60, (1.0, 0.75, 0.4), 0.1)
    Md('old_military_crate', 3.6, 4.6, 0.42, rot=20, tri=6000, coll=prc)
    lam = material('S_lucina', (1.0, 0.8, 0.4), rough=0.4, emit=(1.0, 0.7, 0.3), emit_strength=7.0); pal = material('S_palo_camp', (0.3, 0.19, 0.09), rough=0.8); fil = material('S_filo_camp', (0.05, 0.05, 0.05), rough=0.6)
    appigli = ((-4.3, 5.4, 1.75), (-1.6, 7.6, 3.3), (3.2, 8.0, 3.3), (4.9, 6.2, 1.75))                                     # lucine appese tra le tende e due pali
    for (px_, py_) in ((-1.6, 7.6), (3.2, 8.0)): shape('PaloLucine', 'cyl:0.06:3.4', (x0 + px_, py_, h(px_, py_) + 1.7), mat=pal, coll=envc)
    for i in range(3):
        (ax, ay, az), (bx2, by2, bz) = appigli[i], appigli[i + 1]; n_l = 7 if i == 1 else 5
        for j in range(1, n_l):
            t = j / n_l; sag = 0.5 * math.sin(t * PI); shape('Lucina', 'sphere_lo', (x0 + ax + (bx2 - ax) * t, ay + (by2 - ay) * t, h(0, 3) + az + (bz - az) * t - sag), scale=(0.075, 0.075, 0.09), mat=lam, coll=envc).visible_shadow = False
    PS.kenney(A, 'car-kit/van', prc, x0 + 6.6, 10.6, z=h(6.6, 10.6), h=3.1, rot=-155); Md('wooden_picnic_table', -4.4, 3.2, 0.85, rot=25, coll=prc)
    PS.tenda(envc, (x0 - 4.3, 5.4, h(-4.3, 5.4)), rot=math.radians(28), colore=(0.95, 0.42, 0.06), nome='TendaA'); PS.tenda(envc, (x0 + 4.9, 6.2, h(4.9, 6.2)), rot=math.radians(-32), colore=(0.1, 0.5, 0.75), nome='TendaB')
    PS.sparsi(kitlook, envc, x0, h, 'fern_02', 3, (-3.4, -1.8, -5.3, -4.5), (0.7, 0.9), 68, via=())
    PS.pulisci()
    return dict(h=h, cam=((1.2, -7.5, 2.4), (0.0, 3.0, 1.8), 21), luci=[pf, pl], pippo=(-1.4, 0.4), tumbo=(-2.5, 0.1))

# ---------------------------------------------------------------------------------------------------- centro citta'
def citta(x0, envc, prc, M=None, seme=7):
    """strada tra palazzi fitti: marciapiedi con lampioni, alberi, panchine, idrante, semafori, strisce, traffico di auto grandi."""
    M = M or set004.make_mats(); rnd = random.Random(seme); rng = np.random.default_rng(seme); h = lambda x, y: 0.0
    asf = A.materiale('asphalt_02', dimensione=4.0, rilievo=0.8, tinta=(0.8, 0.8, 0.85)); lastre = A.materiale('PavingStones070', dimensione=2.0, rilievo=0.8); cem = A.materiale('Concrete034', dimensione=3.0, rilievo=0.6)
    torri = [A.materiale('PaintedPlaster017', dimensione=3.0, rilievo=0.5, tinta=kitlook._k(c, 1.15, 1.7), nome='PT_torre%d' % i) for i, c in enumerate(kitlook.TOWERC)]
    o = bx('StradaC', (x0 - 150, -150, -0.3), (x0 + 150, 190, 0.0), M['park'], envc); kitlook.setmat(o, asf); A.niente_ombra(o)
    for sx in (-1, 1):
        o = bx('MarciapC', (x0 + sx * 9.0 - 2.5, -40, 0.0), (x0 + sx * 9.0 + 2.5, 150, 0.16), M['park'], envc); kitlook.setmat(o, lastre)
        o = bx('CordoloC', (x0 + sx * 6.5 - 0.12, -40, 0.0), (x0 + sx * 6.5 + 0.12, 150, 0.18), M['park'], envc); kitlook.setmat(o, cem)
    for yy in range(-20, 120, 4):
        if not (-3.5 < yy < 3.5): bx('LineaC', (x0 - 0.08, yy, 0.0), (x0 + 0.08, yy + 2.0, 0.012), M['frame'], envc)
    PS.strisce(envc, x0, -1.4, mezza=6.3, lunghe=3.4); bx('StopC', (x0 + 0.3, 3.0, 0.0), (x0 + 6.2, 3.35, 0.012), M['frame'], envc)
    def torre(x, y, rz, tw, hh):
        mb = MB([torri[int(rng.integers(0, len(torri)))], M['window'], M['frame'], cem, M['dark'], M['shutter'][int(rng.integers(0, 5))]]); set004.tower_geo(mb, tw, hh, rng); return mb.build('PalazzoC', envc, (x, y, 0), rz)
    tende = [material('S_tendaC%d' % i, c, rough=0.8) for i, c in enumerate(((0.85, 0.1, 0.08), (0.1, 0.5, 0.25), (0.1, 0.35, 0.8), (0.95, 0.7, 0.1)))]
    for sx in (-1, 1):
        yy = -12.0; k = 0
        while yy < 96:
            tw = rnd.uniform(5.0, 6.6); hh = rnd.uniform(13, 30) if yy < 60 else rnd.uniform(24, 44)
            torre(x0 + sx * (11.5 + tw / 2), yy + tw / 2, PI / 2 if sx < 0 else -PI / 2, tw, hh)
            if k % 2 == 0 and yy < 50: bx('TendaNegozio', (x0 + sx * 11.5 - (1.6 if sx > 0 else 0), yy + tw / 2 - 1.6, 2.9), (x0 + sx * 11.5 + (0 if sx > 0 else 1.6), yy + tw / 2 + 1.6, 3.02), tende[k // 2 % 4], envc)
            yy += tw + rnd.uniform(0.0, 0.5); k += 1
    for k in range(7): torre(x0 - 30 + k * 10.0 + rnd.uniform(-1, 1), 108 + rnd.uniform(0, 8), 0.0, rnd.uniform(7, 9), rnd.uniform(34, 58))
    lamp = A.sparpaglia('street_lamp_01', 10, (0, 1, 0, 1), altezza=5.4, collezione=envc); i = 0
    for yy in (2, 15, 28, 41, 54):
        for sx in (-1, 1):
            lamp[i].location = (x0 + sx * 7.2, yy + (3 if sx > 0 else 0), 0.16); lamp[i].scale = lamp[0].scale; lamp[i].rotation_euler = (0, 0, PI / 2 if sx < 0 else -PI / 2); i += 1
            t = A.albero_cartonato(MIX[(yy + sx) % len(MIX)], posizione=(x0 + sx * 9.6, yy + 6.5, 0.16), altezza=rnd.uniform(5.0, 6.5), collezione=envc, vista=yy, ombra=yy < 20)
    PS.alleggerisci(lamp[0]); kitlook.tune_cutouts(1.9)
    Md = lambda *a, **k: PS.modello(A, k.pop('coll', prc), x0, h, *a, **k)
    Md('fire_hydrant', 7.1, 6.6, 0.95, tri=6000, z=0.16); Md('metal_trash_can', -7.2, 4.2, 1.05, z=0.16); Md('painted_wooden_bench', -10.2, 8.5, 1.0, rot=90, z=0.16); Md('painted_wooden_bench', 10.2, 12.5, 1.0, rot=-90, z=0.16)
    Md('concrete_road_barrier', 4.6, -0.6, 0.95, rot=15); Md('concrete_road_barrier', 5.4, 1.6, 0.95, rot=80)
    Kn = lambda aid, x, y, **k: PS.kenney(A, aid, prc, x0 + x, y, **k)
    Kn('car-kit/cone', 3.4, 0.2, h=0.75); Kn('car-kit/cone', 3.9, 2.2, h=0.75); Kn('car-kit/cone', 4.4, -1.6, h=0.75)
    PS.semaforo(prc, (x0 + 6.9, 4.4, 0.16), rot=0.0, acceso='rosso'); PS.semaforo(prc, (x0 - 6.9, -2.0, 0.16), rot=PI, acceso='verde')
    # auto grandi (l'autore: "le macchine dovrebbero essere piu' grandi"): un'auto normale e' alta 2,1-2,5 m accanto a Pippo
    Kn('car-kit/taxi', -2.6, 9.5, h=2.2, rot=0); Kn('car-kit/police', 2.7, 14.5, h=2.2, rot=180); Kn('car-kit/van', -2.7, 21.0, h=3.0, rot=0); Kn('car-kit/garbage-truck', 2.8, 27.0, h=3.6, rot=180)
    Kn('car-kit/suv', -2.6, 34.0, h=2.5, rot=0); Kn('car-kit/sedan-sports', 2.7, 40.0, h=2.1, rot=180); Kn('car-kit/truck', -2.7, 48.0, h=3.3, rot=0)
    Kn('car-kit/hatchback-sports', -5.4, 14.0, h=2.1, rot=0); Kn('car-kit/sedan', 5.4, 20.0, h=2.2, rot=180); Kn('car-kit/delivery', 5.4, 33.0, h=3.0, rot=180); Kn('car-kit/suv-luxury', -5.4, 27.0, h=2.5, rot=0)
    PS.pulisci()
    return dict(h=h, cam=((0.9, -7.5, 2.3), (0.0, 6.0, 3.8), 20), luci=[])

# ---------------------------------------------------------------------------------------------------- aiuti comuni
_C = {}
def mats():
    if 'M' not in _C: _C['M'] = set004.make_mats()
    return _C['M']
def T(aid, dim, ril=0.8, tinta=None, **k):
    """materiale realistico dalla libreria, creato una volta sola."""
    key = (aid, dim, tinta, tuple(sorted(k.items())))
    if key not in _C: _C[key] = A.materiale(aid, dimensione=dim, rilievo=ril, tinta=tinta, **k)
    return _C[key]
def _casa(coll, loc, rotz, w, d, two, muro, tetto, seme=1, si=0, alto=None):
    """casa con finestre, porta e comignolo (stessa geometria del quartiere) con muro e tetto a scelta."""
    M = mats(); ms = set004.house_mats(M, 0, 0, si); ms[0] = muro; ms[1] = tetto; mb = MB(ms)
    set004.house_geo(mb, w, d, alto or (4.5 if two else 2.9), two, np.random.default_rng(seme)); return mb.build('Casa', coll, loc, rotz)
def _sentiero(coll, x0, h, pts, largo, mat, dz=0.03, nome='Sentiero'):
    """striscia (vialetto, strada) che segue il terreno lungo i punti (x, y)."""
    v = []
    for i, (x, y) in enumerate(pts):
        j = min(i, len(pts) - 2); dx, dy = pts[j + 1][0] - pts[j][0], pts[j + 1][1] - pts[j][1]; n = math.hypot(dx, dy) or 1.0
        for sg in (-1, 1):
            xx = x - sg * dy / n * largo / 2; yy = y + sg * dx / n * largo / 2; v.append((x0 + xx, yy, h(xx, yy) + dz))
    me = bpy.data.meshes.new(nome); me.from_pydata(v, [], [(2 * i, 2 * i + 1, 2 * i + 3, 2 * i + 2) for i in range(len(pts) - 1)]); me.update()
    o = bpy.data.objects.new(nome, me); coll.objects.link(o); me.materials.append(mat); o.visible_shadow = False; return o
def _disco(coll, cx, cy, z, rx, ry, mat, nome='Disco', n=48, mosso=0.1):
    me = bpy.data.meshes.new(nome); me.from_pydata([(cx, cy, z)] + [(cx + rx * math.cos(i / n * 2 * PI) * (1 + mosso * math.sin(i * 1.7)), cy + ry * math.sin(i / n * 2 * PI) * (1 + mosso * math.cos(i * 2.3)), z) for i in range(n)], [], [(0, i + 1, (i + 1) % n + 1) for i in range(n)]); me.update()
    o = bpy.data.objects.new(nome, me); coll.objects.link(o); me.materials.append(mat); o.visible_shadow = False; return o
def _fiocchi(coll, x0, n=260, seme=3, area=(-12, 12, -6, 24), zr=(0.3, 10.0)):
    m = material('S_fiocco', (1, 1, 1), rough=0.6, emit=(1, 1, 1), emit_strength=1.0); rnd = random.Random(seme)
    for i in range(n):
        s = rnd.uniform(0.025, 0.05); o = shape('Fiocco', 'sphere_lo', (x0 + rnd.uniform(area[0], area[1]), rnd.uniform(area[2], area[3]), rnd.uniform(*zr)), scale=(s, s, s), mat=m, coll=coll); o.visible_shadow = False
def _stelle(coll, x0, n=280, seme=5):
    m = material('S_stella', (1, 1, 1), rough=1.0, emit=(1, 1, 1), emit_strength=7.0); rnd = random.Random(seme)
    for i in range(n):
        az = rnd.uniform(-1.3, 1.3); el = rnd.uniform(0.05, 1.4); s = rnd.uniform(0.7, 2.0)
        o = shape('Stella', 'sphere_lo', (x0 + 900 * math.cos(el) * math.sin(az), 900 * math.cos(el) * math.cos(az), 900 * math.sin(el)), scale=(s, s, s), mat=m, coll=coll); o.visible_shadow = False
def _zucca(coll, loc, s=0.4, rot=0.0):
    """zucca di Halloween con la faccia accesa, verso -Y."""
    r = empty('Zucca', loc, None, coll); r.rotation_euler = (0, 0, rot); ar = material('S_zucca', (1.0, 0.4, 0.03), rough=0.5); gl = material('S_zucca_luce', (1.0, 0.8, 0.2), rough=0.5, emit=(1.0, 0.65, 0.1), emit_strength=5.0); ve = material('S_zucca_picciolo', (0.2, 0.4, 0.1), rough=0.7)
    for i in range(6): shape('ZuccaSpicchio', 'sphere', (0, 0, s * 0.8), scale=(s, s * 0.55, s * 0.8), rot=(0, 0, i / 6 * PI), parent=r, mat=ar, coll=coll)
    shape('ZuccaPicciolo', 'cyl:0.04:0.16', (0, 0, s * 1.62), parent=r, mat=ve, coll=coll)
    for sx in (-1, 1): shape('ZuccaOcchio', 'cone', (sx * s * 0.34, -s * 0.97, s * 0.82), scale=(s * 0.17, s * 0.06, s * 0.22), parent=r, mat=gl, coll=coll)
    shape('ZuccaBocca', 'sphere', (0, -s * 0.98, s * 0.48), scale=(s * 0.42, s * 0.07, s * 0.1), parent=r, mat=gl, coll=coll); return r
def _lampione(coll, x0, x, y, z, luci, alt=5.2, energia=250.0):
    o = PS.alleggerisci(A.modello('street_lamp_01', posizione=(x0 + x, y, z), altezza=alt, collezione=coll)); luci.append(_luce(coll, (x0 + x, y - 0.2, z + alt * 0.86), energia, (1.0, 0.8, 0.5), 0.3)); return o

# ---------------------------------------------------------------------------------------------------- cimitero
def cimitero(x0, envc, prc):
    """cimitero al crepuscolo: lapidi di pietra, mausoleo, statua, cancellata, vialetto di ciottoli, lanterne e zucche accese, fantasma, luna."""
    import animali
    h = PS.colline(amp=5.0, rx=12.0, ry=11.0, cy=5.0, bordo=18.0, lontano=9.0, fase=31.0); rnd = random.Random(1); Md = lambda *a, **k: PS.modello(A, k.pop('coll', envc), x0, h, *a, **k); luci = []
    PS.terreno(envc, x0, T('Grass001', 3.0, tinta=(0.55, 0.8, 0.5), ruvidita=1.5), h)
    pietre = [T('granite_wall', 1.6, 1.0, tinta=(1.7, 1.7, 1.75)), T('castle_wall_slates', 1.4, 1.0, tinta=(1.6, 1.6, 1.65))]; scuro = material('S_cim_scuro', (0.04, 0.04, 0.05), rough=0.6); ferro = material('S_cim_ferro', (0.03, 0.035, 0.04), rough=0.45, metallic=0.6)
    _sentiero(envc, x0, h, [(0.5 * math.sin(y * 0.25), y) for y in np.arange(-9, 11.6, 0.8)], 2.4, T('cobblestone_floor_04', 2.0, 1.2))
    def lapide(x, y, tipo, rz):
        mb = MB([pietre[tipo % 2]])
        if tipo == 0: mb.box((0, 0, 0.45), (0.7, 0.16, 0.9), 0); mb.box((0, 0, 0.96), (0.56, 0.16, 0.14), 0); mb.box((0, 0, 1.08), (0.36, 0.16, 0.1), 0)
        elif tipo == 1: mb.box((0, 0, 0.12), (0.62, 0.32, 0.24), 0); mb.box((0, 0, 0.84), (0.17, 0.15, 1.3), 0); mb.box((0, 0, 1.08), (0.66, 0.15, 0.17), 0)
        elif tipo == 2: mb.box((0, 0, 0.15), (0.62, 0.62, 0.3), 0); mb.box((0, 0, 1.0), (0.36, 0.36, 1.5), 0); mb.box((0, 0, 1.85), (0.24, 0.24, 0.25), 0)
        elif tipo == 3: mb.box((0, 0.6, 0.14), (0.84, 1.7, 0.28), 0); mb.box((0, -0.2, 0.5), (0.76, 0.16, 0.95), 0); mb.box((0, -0.2, 1.02), (0.5, 0.16, 0.12), 0)
        else: mb.box((0, 0, 0.36), (1.05, 0.18, 0.72), 0); mb.box((0, 0, 0.78), (0.82, 0.18, 0.14), 0)
        o = mb.build('Lapide', envc, (x0 + x, y, h(x, y) - 0.06), rz); o.rotation_euler.x = rnd.uniform(-0.07, 0.07); o.rotation_euler.y = rnd.uniform(-0.08, 0.08)
        if tipo in (0, 4): text_obj(envc, 'RIP', 'RIP', 0.2, scuro, (0, -0.095, 0.5), parent=o)
        return o
    k = 0
    for yy in (2.4, 4.6, 6.8, 9.0, 11.2):
        for xx in (-7.4, -5.6, -3.9, -2.3, 2.5, 4.1, 5.8, 7.6):
            if abs(xx) < 3.2 and yy > 10: continue
            if abs(xx) > 4.6 + yy * 0.35: continue
            lapide(xx + rnd.uniform(-0.25, 0.25), yy + rnd.uniform(-0.3, 0.3), k % 5, rnd.uniform(-0.2, 0.2)); k += 1
    z0 = h(0, 14); mb = MB([pietre[0], pietre[1], scuro])                                      # mausoleo in fondo al vialetto
    mb.box((0, 0, 0.2), (5.4, 4.4, 0.4), 1); mb.box((0, 0.2, 1.9), (4.2, 3.4, 3.0), 0); mb.box((0, -1.53, 1.5), (1.2, 0.1, 2.2), 2); mb.gable(-2.6, 2.6, -2.1, 2.1, 3.4, 1.2, 1)
    for sx in (-1, 1): mb.box((sx * 1.55, -1.8, 1.8), (0.42, 0.42, 2.8), 1)
    mb.box((0, 0, 5.05), (0.16, 0.14, 0.9), 0); mb.box((0, 0, 5.15), (0.56, 0.14, 0.16), 0); mb.build('Mausoleo', envc, (x0, 14.0, z0))
    bx('Piedistallo', (x0 - 6.4, 10.6, h(-5.8, 11.2) - 0.1), (x0 - 5.2, 11.8, h(-5.8, 11.2) + 0.9), pietre[1], envc); Md('gothic_statue', -5.8, 11.2, 2.3, rot=20, tri=14000, z=h(-5.8, 11.2) + 0.9)
    def palo(x, y):
        z = h(x, y); shape('Cancellata', 'cyl:0.03:1.7', (x0 + x, y, z + 0.8), mat=ferro, coll=envc); shape('CancellataPunta', 'cone', (x0 + x, y, z + 1.65), scale=(0.055, 0.055, 0.2), mat=ferro, coll=envc)
    for xx in np.arange(-13.5, 13.6, 0.45):
        palo(xx, 17.5)
        for zz in (0.35, 1.4): shape('Traversa', 'cyl:0.022:0.46', (x0 + xx + 0.22, 17.5, h(xx, 17.5) + zz), rot=(0, PI / 2, 0), mat=ferro, coll=envc)
    for sx in (-1, 1):
        for yy in np.arange(1.8, 17.5, 0.45):
            palo(sx * 13.5, yy)
            for zz in (0.35, 1.4): shape('Traversa', 'cyl:0.022:0.46', (x0 + sx * 13.5, yy + 0.22, h(sx * 13.5, yy) + zz), rot=(PI / 2, 0, 0), mat=ferro, coll=envc)
        bx('Pilastro', (x0 + sx * 3.3 - 0.35, 0.3, -0.1), (x0 + sx * 3.3 + 0.35, 1.0, 2.5), pietre[1], envc); bx('PilastroCapo', (x0 + sx * 3.3 - 0.45, 0.2, 2.5), (x0 + sx * 3.3 + 0.45, 1.1, 2.7), pietre[0], envc)
        shape('LumePilastro', 'sphere', (x0 + sx * 3.3, 0.65, 2.95), scale=(0.24, 0.24, 0.28), mat=material('S_lume', (1.0, 0.8, 0.4), rough=0.4, emit=(1.0, 0.7, 0.3), emit_strength=6.0), coll=envc); luci.append(_luce(prc, (x0 + sx * 3.3, 0.2, 3.0), 350, (1.0, 0.7, 0.35), 0.25))
    for (xx, yy) in ((-4.3, 3.4), (5.6, 6.1), (-7.0, 7.4), (2.4, 9.6)):
        Md('Lantern_01', xx, yy, 0.42, tri=5000, coll=prc); luci.append(_luce(prc, (x0 + xx, yy - 0.1, h(xx, yy) + 0.4), 90, (1.0, 0.65, 0.3), 0.1))
    _zucca(prc, (x0 + 2.5, 0.6, h(2.5, 0.6)), 0.42, -0.3); _zucca(prc, (x0 - 2.3, 1.2, h(-2.3, 1.2)), 0.34, 0.35); _zucca(prc, (x0 + 4.2, 3.2, h(4.2, 3.2)), 0.28, -0.1)
    gh = animali.fantasma(prc, 1.25); gh['root'].location = (x0 - 3.2, 4.6, h(-3.2, 4.6) + 0.45); gh['root'].rotation_euler = (0, 0, 0.35)
    PS.bosco(A, envc, x0, h, ('pine_tree_01', 'fir_tree_01', 'island_tree_03', 'pine_tree_01'), 80, r0=15.0, r1=70.0, alt=(9.0, 14.0), seme=11, cy=6.0)
    _alb(envc, x0, h, 'island_tree_03', -10.6, 6.2, 7.5, vista=0, near=True); _alb(envc, x0, h, 'pine_tree_01', 10.8, 8.0, 12.0, vista=1, near=True); _alb(envc, x0, h, 'island_tree_02', 8.6, 13.5, 8.0, vista=2)
    kitlook.tune_cutouts(1.5)
    via = ((0.7, 0.0, 1.5),); PS.sparsi(kitlook, envc, x0, h, 'grass_medium_01', 50, (-12, 12, -5, 15), (0.25, 0.5), 12, via=via); PS.sparsi(kitlook, envc, x0, h, 'fern_02', 16, (-12, 12, -3, 15), (0.4, 0.7), 13, via=via)
    PS.sparsi(kitlook, envc, x0, h, 'shrub_02', 10, (-13, 13, 9, 17), (0.9, 1.6), 14, shadow=True, via=((0, 14, 4.0),))
    shape('Luna', 'sphere', (x0 - 150, 620, 300), scale=(34, 34, 34), mat=material('S_luna', (1.0, 0.97, 0.85), rough=1.0, emit=(1.0, 0.95, 0.8), emit_strength=2.2), coll=envc).visible_shadow = False
    luci.append(_luce(prc, (x0 + 2.5, -4.0, 3.2), 900, (1.0, 0.86, 0.75), 1.2)); PS.pulisci()
    return dict(h=h, cam=((1.2, -7.5, 2.4), (0.0, 4.5, 2.5), 21), luci=luci, cielo=('qwantani_dusk_2_puresky', 0.5, 200.0, {}), esposizione=0.45)

# ---------------------------------------------------------------------------------------------------- luna
def _terra_mat():
    m = bpy.data.materials.new('S_terra'); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']; tc = nt.nodes.new('ShaderNodeTexCoord')
    n1 = nt.nodes.new('ShaderNodeTexNoise'); n1.inputs['Scale'].default_value = 2.3; n1.inputs['Detail'].default_value = 7.0; nt.links.new(tc.outputs['Object'], n1.inputs['Vector'])
    r1 = nt.nodes.new('ShaderNodeValToRGB'); e = r1.color_ramp.elements; e[0].position = 0.0; e[0].color = (0.01, 0.06, 0.35, 1); e[1].position = 0.52; e[1].color = (0.02, 0.16, 0.6, 1)
    for pos, col in ((0.55, (0.08, 0.38, 0.1, 1)), (0.75, (0.4, 0.33, 0.15, 1))): q = e.new(pos); q.color = col
    nt.links.new(n1.outputs['Fac'], r1.inputs['Fac'])
    n2 = nt.nodes.new('ShaderNodeTexNoise'); n2.inputs['Scale'].default_value = 4.0; n2.inputs['Detail'].default_value = 9.0; n2.inputs['Distortion'].default_value = 1.2; nt.links.new(tc.outputs['Object'], n2.inputs['Vector'])
    r2 = nt.nodes.new('ShaderNodeValToRGB'); r2.color_ramp.elements[0].position = 0.52; r2.color_ramp.elements[1].position = 0.68; nt.links.new(n2.outputs['Fac'], r2.inputs['Fac'])
    mx = nt.nodes.new('ShaderNodeMixRGB'); mx.inputs['Color2'].default_value = (1, 1, 1, 1); nt.links.new(r2.outputs['Color'], mx.inputs['Fac']); nt.links.new(r1.outputs['Color'], mx.inputs['Color1'])
    nt.links.new(mx.outputs['Color'], b.inputs['Base Color']); nt.links.new(mx.outputs['Color'], b.inputs['Emission Color']); b.inputs['Emission Strength'].default_value = 1.6; b.inputs['Roughness'].default_value = 1.0; return m
def razzo(coll, loc, nome='Razzo'):
    """razzo a mano: corpo bianco lucido, punta e pinne rosse, oblo'. Alto circa 7 m, origine a terra."""
    r = empty(nome, loc, None, coll); bianco = material('S_razzo_b', (0.95, 0.95, 0.96), rough=0.25, coat=0.6); rosso = material('S_razzo_r', (0.85, 0.07, 0.05), rough=0.3, coat=0.6); vetro = material('S_razzo_v', (0.1, 0.35, 0.6), rough=0.05, spec=1.0); sc = material('S_razzo_s', (0.08, 0.08, 0.09), rough=0.5, metallic=0.7)
    shape(nome + 'Corpo', 'cyl:0.95:4.4', (0, 0, 3.0), parent=r, mat=bianco, coll=coll); shape(nome + 'Punta', 'cone', (0, 0, 5.2), scale=(0.95, 0.95, 2.0), parent=r, mat=rosso, coll=coll); shape(nome + 'Pomo', 'sphere', (0, 0, 7.2), scale=(0.22, 0.22, 0.26), parent=r, mat=rosso, coll=coll)
    shape(nome + 'Fascia', 'cyl:0.97:0.35', (0, 0, 2.2), parent=r, mat=rosso, coll=coll); shape(nome + 'Ugello', 'cone', (0, 0, 0.82), scale=(0.75, 0.75, -0.7), parent=r, mat=sc, coll=coll)
    mb = MB([rosso])
    for k in range(3): a = k / 3 * 2 * PI + PI / 6; mb.box((1.25 * math.cos(a), 1.25 * math.sin(a), 1.25), (1.3, 0.14, 2.3), 0, rz=a)
    f = mb.build(nome + 'Pinne', coll); f.parent = r
    shape(nome + 'Oblo', 'sphere', (0, -0.93, 3.9), scale=(0.34, 0.08, 0.34), parent=r, mat=vetro, coll=coll); shape(nome + 'ObloBordo', 'cyl:0.42:0.08', (0, -0.92, 3.9), rot=(PI / 2, 0, 0), parent=r, mat=sc, coll=coll); return r
def luna(x0, envc, prc):
    """superficie lunare con crateri veri nel terreno, rocce, base a cupole, razzo, bandiera, la Terra nel cielo nero pieno di stelle."""
    base = PS.colline(amp=4.0, rx=12.0, ry=10.0, cy=3.0, bordo=22.0, lontano=15.0, fase=7.0); luci = []
    crateri = ((-5.8, 6.8, 2.8, 0.75), (6.8, 9.5, 3.6, 0.95), (-9.0, 0.2, 1.9, 0.45), (0.5, 17.5, 5.0, 1.2), (-15, 15, 5.5, 1.3), (16, 19, 4.5, 1.1), (5.0, 1.6, 1.6, 0.35), (-22, 30, 8, 1.8), (20, 40, 9, 2.0))
    def h(x, y):
        z = base(x, y)
        for cx, cy, R, D in crateri:
            d = math.hypot(x - cx, y - cy) / R
            if d < 1.7: z += -D * (1 - PS.sm(d)) + 0.38 * D * math.exp(-((d - 1.0) / 0.2) ** 2)
        return z
    Md = lambda *a, **k: PS.modello(A, k.pop('coll', envc), x0, h, *a, **k)
    PS.terreno(envc, x0, T('moon_01', 6.0, 1.4), h, xr=(-75, 75), yr=(-22, 150), passo=1.0)
    Md('moon_rock_01', -7.6, 3.6, 1.5, rot=30); Md('moon_rock_05', 9.2, 4.4, 2.0, rot=100); Md('moon_rock_03', -3.4, 9.6, 1.1); Md('moon_rock_02', 11.5, 11.0, 2.6, rot=200); Md('moon_rock_04', -12.0, 9.0, 2.2, rot=60)
    PS.sparsi2(A, envc, x0, h, 'moon_rock_02', 8, (-11, 11, -4, 13), (0.25, 0.8), 21); PS.sparsi2(A, envc, x0, h, 'moon_rock_06', 9, (-11, 11, -4, 13), (0.15, 0.5), 22); PS.sparsi2(A, envc, x0, h, 'moon_rock_07', 10, (-16, 16, 6, 24), (0.4, 1.3), 23)
    cup = material('S_base_b', (0.93, 0.94, 0.96), rough=0.3, coat=0.5); fin = material('S_base_f', (1.0, 0.8, 0.4), rough=0.3, emit=(1.0, 0.75, 0.35), emit_strength=5.0); gr = material('S_base_g', (0.35, 0.37, 0.4), rough=0.5, metallic=0.5)
    for (bx_, by_, rr) in ((-4.6, 12.6, 3.3), (-9.2, 14.2, 2.2)):
        zc = h(bx_, by_); shape('Cupola', 'sphere', (x0 + bx_, by_, zc), scale=(rr, rr, rr * 0.8), mat=cup, coll=envc); shape('CupolaAnello', 'cyl:1:0.5', (x0 + bx_, by_, zc + 0.2), scale=(rr * 1.02, rr * 1.02, 1), mat=gr, coll=envc)
        for k in range(5): a = -PI / 2 + (k - 2) * 0.42; shape('CupolaFinestra', 'sphere', (x0 + bx_ + rr * 0.93 * math.cos(a), by_ + rr * 0.93 * math.sin(a), zc + rr * 0.3), scale=(0.26, 0.26, 0.3), mat=fin, coll=envc)
    shape('Tunnel', 'cap:0.8:3.2', (x0 - 7.0, 13.4, h(-7.0, 13.4) + 0.5), rot=(0, PI / 2, 0.34), mat=gr, coll=envc); shape('Porta', 'cyl:1.0:0.5', (x0 - 4.6, 12.6 - 3.2, h(-4.6, 9.4) + 0.9), rot=(PI / 2, 0, 0), mat=gr, coll=envc)
    shape('Antenna', 'cyl:0.05:3.0', (x0 - 4.6, 12.6, h(-4.6, 12.6) + 3.9), mat=gr, coll=envc); shape('AntennaLuce', 'sphere', (x0 - 4.6, 12.6, h(-4.6, 12.6) + 5.45), scale=(0.14, 0.14, 0.14), mat=material('S_base_r', (1, 0.1, 0.05), emit=(1, 0.1, 0.05), emit_strength=8.0), coll=envc)
    razzo(envc, (x0 + 5.0, 13.5, h(5.0, 13.5) - 0.1))
    shape('AstaBandiera', 'cyl:0.035:2.6', (x0 + 3.2, 3.6, h(3.2, 3.6) + 1.3), mat=gr, coll=prc); bx('Bandiera', (x0 + 3.24, 3.58, h(3.2, 3.6) + 1.75), (x0 + 4.5, 3.62, h(3.2, 3.6) + 2.55), material('S_band_arancio', (1.0, 0.45, 0.05), rough=0.7), prc)
    PS.kenney(A, 'space-kit/rover', prc, x0 - 3.4, 2.4, z=h(-3.4, 2.4), h=2.0, rot=35)
    shape('Terra', 'sphere', (x0 + 75, 560, 290), scale=(58, 58, 58), mat=_terra_mat(), coll=envc).visible_shadow = False; _stelle(envc, x0)
    PS.pulisci()
    return dict(h=h, cam=((1.2, -7.5, 2.3), (0.3, 4.0, 2.9), 21), luci=luci, cielo=('qwantani_night_puresky', 0.10, 0.0, dict(sfondo=False, colore_sfondo=(0.0, 0.0, 0.004))), sole=(4.2, (55, 0, 40), (1.0, 0.98, 0.95)))

# ---------------------------------------------------------------------------------------------------- neve
def neve(x0, envc, prc):
    """paesaggio di neve: colline bianche, abeti fitti, lago ghiacciato, baita con le finestre accese, pupazzo di neve, slitta, lampione, fiocchi che cadono."""
    import animali
    h = PS.colline(amp=6.0, rx=12.0, ry=10.5, cy=3.5, bordo=18.0, lontano=11.0, fase=52.0); rnd = random.Random(5); Md = lambda *a, **k: PS.modello(A, k.pop('coll', envc), x0, h, *a, **k); luci = []
    PS.terreno(envc, x0, T('Snow006', 3.0, 1.2), h)
    _disco(envc, x0 - 8.2, 9.0, 0.03, 5.2, 3.4, A.materiale('Ice004', dimensione=5.0, ruvidita=0.25, tinta=(1.5, 1.95, 2.4), vernice=1.0), 'Lago')
    PS.bosco(A, envc, x0, h, ('fir_tree_01', 'pine_tree_01', 'fir_tree_01'), 150, r0=13.0, r1=85.0, alt=(9.0, 15.0), seme=51, cy=4.0, evita=((-8.2, 9.0, 6.5), (6.4, 10.0, 4.5)))
    PS.bosco(A, envc, x0, h, ('fir_sapling_medium', 'fir_sapling', 'pine_sapling_medium'), 26, r0=10.5, r1=24.0, alt=(1.4, 3.2), seme=52, cy=4.0, evita=((-8.2, 9.0, 5.5), (6.4, 10.0, 4.0)))
    _alb(envc, x0, h, 'fir_tree_01', -11.0, 3.2, 12.0, vista=1, near=True); _alb(envc, x0, h, 'fir_tree_01', 11.2, 5.0, 12.5, vista=0, near=True)
    kitlook.tune_cutouts(1.9)
    M = mats(); M['window'].node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value = 3.0
    _casa(envc, (x0 + 6.4, 10.2, h(6.4, 10.2)), -0.35, 5.6, 4.4, False, T('brown_planks_03', 1.6, 1.0), T('Snow006', 3.0, 1.2), seme=3, si=4)
    luci.append(_luce(prc, (x0 + 5.6, 7.6, 1.9), 220, (1.0, 0.7, 0.35), 0.3))
    for k, (dx, dy, dz, s) in enumerate(((0, 0, 0, 0.3), (0.2, 0.1, 0.55, 0.42), (0.5, 0.15, 1.3, 0.6))): shape('Fumo', 'sphere', (x0 + 7.9 + dx, 10.4 + dy, h(6.4, 10.2) + 4.3 + dz), scale=(s, s, s), mat=material('S_fumo', (0.8, 0.8, 0.82), rough=1.0), coll=envc).visible_shadow = False
    pn = animali.pupazzo_neve(prc, 1.15); pn['root'].location = (x0 - 3.0, 2.4, h(-3.0, 2.4)); pn['root'].rotation_euler = (0, 0, 0.4)
    mb = MB([material('S_slitta_r', (0.8, 0.08, 0.06), rough=0.4), T('brown_planks_03', 1.0, 1.0)])                       # slitta
    for sx in (-1, 1): mb.box((sx * 0.28, 0, 0.05), (0.05, 1.5, 0.06), 0); mb.box((sx * 0.28, -0.3, 0.17), (0.04, 0.05, 0.22), 0); mb.box((sx * 0.28, 0.4, 0.17), (0.04, 0.05, 0.22), 0)
    for k in range(4): mb.box((-0.2 + k * 0.133, 0.05, 0.3), (0.12, 1.25, 0.03), 1)
    mb.build('Slitta', prc, (x0 + 2.9, 1.3, h(2.9, 1.3)), -0.5)
    Md('dead_tree_trunk', 3.2, 6.2, 0.5, rot=60, tri=8000, coll=prc); Md('tree_stump_01', 2.6, 7.4, 0.6, tri=7000, coll=prc); Md('wooden_axe', 2.9, 7.2, 0.75, rot=40, coll=prc)
    _lampione(envc, x0, -1.2, 6.0, h(-1.2, 6.0), luci, 4.6, 320)
    pal = material('S_paletto', (0.36, 0.22, 0.1), rough=0.8); bianco = T('Snow006', 3.0, 1.2)
    for k in range(9):
        xx = 9.5 - k * 1.5; yy = -1.2 + 0.25 * math.sin(k); shape('Paletto', 'cyl:0.07:1.1', (x0 + xx, yy, h(xx, yy) + 0.5), mat=pal, coll=envc); shape('PalettoNeve', 'sphere', (x0 + xx, yy, h(xx, yy) + 1.08), scale=(0.11, 0.11, 0.07), mat=bianco, coll=envc)
        if xx > 2.2: shape('Staggia', 'cyl:0.035:1.5', (x0 + xx - 0.75, -1.2 + 0.25 * math.sin(k + 0.5), h(xx, yy) + 0.7), rot=(0, PI / 2, 0), mat=pal, coll=envc)
    PS.sparsi2(A, envc, x0, h, 'boulder_01', 5, (-10, 10, 0, 12), (0.5, 1.1), 53)
    _fiocchi(envc, x0); PS.pulisci()
    return dict(h=h, cam=((1.2, -7.5, 2.4), (0.0, 3.5, 2.2), 21), luci=luci, cielo=('snowy_field', 1.2, 84.0, {}))
# ---------------------------------------------------------------------------------------------------- castello
def castello(x0, envc, prc):
    """castello di pietra su un'altura in fondo a una strada di ciottoli; ai suoi piedi un accampamento: tende, banco del mercato, pozzo, botti, torce, balle di fieno."""
    base = PS.colline(amp=5.0, rx=12.0, ry=10.0, cy=3.0, bordo=18.0, lontano=10.0, fase=77.0); rnd = random.Random(4); luci = []
    def h(x, y):
        p = PS.sm(1.0 - (math.hypot(x, y - 29.0) - 13.0) / 7.0); return base(x, y) * (1 - p) + 4.0 * p
    Md = lambda *a, **k: PS.modello(A, k.pop('coll', envc), x0, h, *a, **k)
    PS.terreno(envc, x0, T('Grass001', 3.0, tinta=(1.0, 1.3, 0.68), ruvidita=1.5), h)
    pietra = T('castle_brick_01', 2.4, 1.0); pietra2 = T('medieval_blocks_02', 2.2, 1.0); scuro = material('S_cast_scuro', (0.03, 0.03, 0.035), rough=0.7); legno = T('brown_planks_03', 1.4, 1.0)
    tetto = T('grey_roof_tiles_02', 1.6, 1.2, tinta=kitlook._k((0.86, 0.22, 0.12), 2.2)); rosso = material('S_cast_rosso', (0.8, 0.06, 0.05), rough=0.7); giallo = material('S_cast_giallo', (1.0, 0.78, 0.1), rough=0.6)
    _sentiero(envc, x0, h, [(0.6 * math.sin(y * 0.22), y) for y in np.arange(-9, 20.2, 0.8)], 2.8, T('cobblestone_floor_04', 2.0, 1.2))
    cx, cy, z0 = x0, 29.0, 3.8; mb = MB([pietra, pietra2, scuro, legno, rosso])
    for sx in (-1, 1):
        mb.box((sx * 5.8, -8, 3.2), (6.4, 1.2, 6.4), 0); mb.box((sx * 9, 0, 3.2), (1.2, 16, 6.4), 0); mb.box((sx * 5.8, -8.66, 3.9), (1.1, 0.08, 3.4), 4)
        for k in range(4): mb.box((sx * (3.4 + k * 1.6), -8, 6.8), (0.8, 1.3, 0.8), 0)
        for k in range(10): mb.box((sx * 9, -7.2 + k * 1.6, 6.8), (1.3, 0.8, 0.8), 0)
        mb.box((sx * 2.4, -8.3, 9.0), (0.9, 2.3, 0.9), 1)
    mb.box((0, 8, 3.2), (18, 1.2, 6.4), 0); mb.box((0, -8.2, 4.2), (5.6, 2.2, 8.4), 1); mb.box((0, -9.32, 1.9), (2.6, 0.1, 3.8), 2); mb.box((0, -8.3, 9.0), (0.9, 2.3, 0.9), 1)
    mb.box((0, 2, 7.0), (6.5, 6.5, 14.0), 1); mb.box((0, -1.27, 9.5), (0.5, 0.06, 1.4), 2); mb.box((-1.6, -1.27, 5.5), (0.5, 0.06, 1.4), 2); mb.box((1.6, -1.27, 5.5), (0.5, 0.06, 1.4), 2)
    for k in range(4):
        for sx in (-1, 1): mb.box((sx * 3.0, -0.9 + k * 1.95, 14.4), (0.8, 0.9, 0.8), 1); mb.box((-2.4 + k * 1.6 if sx < 0 else -2.4 + k * 1.6, 2 + sx * 3.0, 14.4), (0.9, 0.8, 0.8), 1)
    mb.box((0, -11.6, 0.25), (2.9, 4.6, 0.22), 3); mb.build('Castello', envc, (cx, cy, z0))
    shape('Arco', 'cyl:1.3:0.12', (cx, cy - 9.32, z0 + 3.8), rot=(PI / 2, 0, 0), mat=scuro, coll=envc)
    for sx in (-1, 1):
        for sy in (-1, 1):
            shape('Torre', 'cyl:2.3:10.4', (cx + sx * 9, cy + sy * 8, z0 + 5.0), mat=pietra2, coll=envc); shape('TorreTetto', 'cone', (cx + sx * 9, cy + sy * 8, z0 + 10.2), scale=(2.9, 2.9, 4.0), mat=tetto, coll=envc)
            shape('TorreAsta', 'cyl:0.05:2.2', (cx + sx * 9, cy + sy * 8, z0 + 15.1), mat=scuro, coll=envc); bx('TorreBandiera', (cx + sx * 9 + 0.05, cy + sy * 8 - 0.02, z0 + 15.3), (cx + sx * 9 + 1.5, cy + sy * 8 + 0.02, z0 + 16.1), rosso if sy < 0 else giallo, envc)
        shape('Stemma', 'sphere', (cx + sx * 5.8, cy - 8.72, z0 + 4.4), scale=(0.34, 0.04, 0.34), mat=giallo, coll=envc)
    shape('MastioAsta', 'cyl:0.07:3.4', (cx, cy + 2, z0 + 16.0), mat=scuro, coll=envc); bx('MastioBandiera', (cx + 0.07, cy + 1.97, z0 + 16.2), (cx + 2.6, cy + 2.03, z0 + 17.6), rosso, envc)
    PS.tenda(envc, (x0 - 5.2, 5.8, h(-5.2, 5.8)), rot=math.radians(32), colore=(0.82, 0.1, 0.08), nome='TendaR'); PS.tenda(envc, (x0 + 5.6, 6.6, h(5.6, 6.6)), rot=math.radians(-36), colore=(0.97, 0.78, 0.15), nome='TendaG')
    bianco = material('S_cast_bianco', (0.95, 0.94, 0.9), rough=0.8); mb = MB([legno, rosso, bianco])                                   # banco del mercato
    mb.box((0, 0, 0.82), (2.4, 1.0, 0.08), 0)
    for sx in (-1, 1):
        for sy in (-1, 1): mb.box((sx * 1.1, sy * 0.42, 1.15), (0.08, 0.08, 2.3), 0)
    for k in range(7): mb.box((-1.14 + k * 0.38, 0.0, 2.34), (0.38, 1.5, 0.05), 1 + k % 2, rx=0.22)
    mb.build('Banco', prc, (x0 + 4.3, 2.4, h(4.3, 2.4)), -0.25)
    for k, (aid, dx) in enumerate((('food-kit/bread', -0.7), ('food-kit/cheese', -0.25), ('food-kit/apple', 0.2), ('food-kit/fish', 0.65))): PS.kenney(A, aid, prc, x0 + 4.3 + dx * 0.97, 2.4 - dx * 0.25, z=h(4.3, 2.4) + 0.86, w=0.36)
    shape('Pozzo', 'cyl:0.85:0.95', (x0 - 4.4, 1.5, h(-4.4, 1.5) + 0.45), mat=pietra2, coll=prc); shape('PozzoBuio', 'cyl:0.66:0.04', (x0 - 4.4, 1.5, h(-4.4, 1.5) + 0.93), mat=scuro, coll=prc)
    mb = MB([legno])
    for sx in (-1, 1): mb.box((sx * 0.78, 0, 1.45), (0.1, 0.1, 2.2), 0)
    mb.box((0, 0, 2.0), (1.6, 0.08, 0.08), 0); mb.gable(-1.05, 1.05, -0.75, 0.75, 2.5, 0.55, 0); mb.build('PozzoTetto', prc, (x0 - 4.4, 1.5, h(-4.4, 1.5)))
    Md('wooden_bucket_01', -3.3, 1.0, 0.45, coll=prc); PS.sparsi2(A, prc, x0, h, 'wine_barrel_01', 4, (5.6, 7.4, 1.0, 3.6), (0.9, 1.0), 41); Md('wine_barrel_01', 2.6, 3.9, 1.0, rot=30, coll=prc); Md('wooden_crate_02', 6.2, 4.4, 0.55, rot=20, coll=prc); Md('kite_shield', -3.6, 5.0, 1.1, rot=30, tri=6000, coll=prc)
    fieno = T('reed_roof_03', 1.0, 1.0)
    for k, (xx, yy, zz) in enumerate(((-6.8, 3.2, 0.55), (-7.9, 3.5, 0.55), (-7.35, 3.35, 1.5))): shape('Fieno', 'cyl:0.55:1.1', (x0 + xx, yy, h(xx, yy) + zz), rot=(PI / 2, 0, 0.3), mat=fieno, coll=prc)
    for (xx, yy) in ((-2.1, 2.8), (2.1, 5.0), (-2.2, 8.2), (2.3, 10.6)):
        shape('TorciaPalo', 'cyl:0.06:1.9', (x0 + xx, yy, h(xx, yy) + 0.95), mat=scuro, coll=prc); f_, l_ = PS.fuoco(prc, (x0 + xx, yy, h(xx, yy) + 1.85), 0.42, 90.0, 'Torcia'); luci.append(l_)
    for a0, a1, sd in ((PI * 0.60, PI + 0.3, 41), (-0.3, PI * 0.40, 42)): PS.bosco(A, envc, x0, h, MIX, 55, r0=14.0, r1=75.0, alt=(5.5, 9.0), seme=sd, a0=a0, a1=a1, evita=((0, 29, 17),))
    _alb(envc, x0, h, MIX[0], -10.5, 5.0, 7.6, vista=0, near=True); _alb(envc, x0, h, MIX[2], 10.8, 3.2, 7.0, vista=1, near=True)
    kitlook.tune_cutouts(1.9)
    Md('mountainside', -62.0, 100.0, 48.0, rot=20, tri=12000); Md('mountainside', 66.0, 112.0, 56.0, rot=200, tri=12000)
    via = ((0.7, 0.0, 1.5), (4.3, 2.4, 1.8), (-4.4, 1.5, 1.4)); PS.sparsi(kitlook, envc, x0, h, 'grass_medium_01', 60, (-12, 12, -5, 13), (0.22, 0.42), 43, via=via); PS.sparsi(kitlook, envc, x0, h, 'dandelion_01', 24, (-11, 11, -4, 12), (0.12, 0.2), 44, via=via)
    PS.sparsi(kitlook, envc, x0, h, 'shrub_02', 14, (-16, 16, 8, 18), (0.9, 1.6), 45, shadow=True, via=((0, 14, 3.5),))
    PS.pulisci()
    return dict(h=h, cam=((1.2, -7.5, 2.3), (0.0, 8.0, 5.6), 21), luci=luci)

# ---------------------------------------------------------------------------------------------------- porto
def faro(coll, loc, alto=17.0, nome='Faro'):
    """faro a fasce bianche e rosse con la lanterna accesa."""
    r = empty(nome, loc, None, coll); b = material('S_faro_b', (0.95, 0.95, 0.93), rough=0.6); ro = material('S_faro_r', (0.82, 0.08, 0.06), rough=0.6); sc = material('S_faro_s', (0.07, 0.07, 0.08), rough=0.5); lu = material('S_faro_l', (1.0, 0.9, 0.5), rough=0.2, emit=(1.0, 0.85, 0.4), emit_strength=9.0)
    n = 5; hs = alto * 0.78 / n
    for k in range(n): rr = 2.2 - k * 0.2; shape('%sFascia%d' % (nome, k), 'cyl:1:1', (0, 0, hs * (k + 0.5)), scale=(rr, rr, hs), parent=r, mat=(ro if k % 2 else b), coll=coll)
    z = hs * n; shape(nome + 'Ballatoio', 'cyl:1.9:0.25', (0, 0, z + 0.1), parent=r, mat=sc, coll=coll); shape(nome + 'Lanterna', 'cyl:1.05:1.7', (0, 0, z + 1.05), parent=r, mat=lu, coll=coll); shape(nome + 'Cupola', 'cone', (0, 0, z + 1.9), scale=(1.3, 1.3, 1.5), parent=r, mat=ro, coll=coll); return r
def porto(x0, envc, prc):
    """porto antico: banchina di ciottoli, pontile di legno, galeone ormeggiato, altre navi, case colorate, magazzino, botti e casse, lampioni, faro sullo scoglio."""
    h = lambda x, y: 0.0; rnd = random.Random(8); luci = []; Md = lambda *a, **k: PS.modello(A, k.pop('coll', envc), x0, h, *a, **k)
    bx('Banchina', (x0 - 150, -80, -3.0), (x0 + 150, 9.6, 0.0), T('cobblestone_floor_04', 2.4, 1.2), envc); bx('BanchinaBordo', (x0 - 150, 9.1, 0.0), (x0 + 150, 9.62, 0.14), T('granite_wall', 1.6, 1.0), envc); PS.mare(envc, x0, z=-1.1, colore=(0.02, 0.27, 0.42))
    legno = T('brown_planks_03', 1.2, 1.0); legno2 = material('S_porto_legno', (0.2, 0.12, 0.06), rough=0.8); ferro = material('S_porto_ferro', (0.05, 0.05, 0.06), rough=0.5, metallic=0.6)
    mb = MB([legno, legno2])
    for k in range(30): mb.box((0, 9.9 + k * 0.52, -0.02), (3.4, 0.47, 0.1), 0)
    for sx in (-1, 1):
        mb.box((sx * 1.62, 17.6, -0.12), (0.16, 15.8, 0.16), 1)
        for k in range(6): mb.box((sx * 1.62, 10.4 + k * 3.0, -0.9), (0.3, 0.3, 3.0), 1)
    mb.build('Pontile', envc, (x0, 0, 0))
    for xx in range(-18, 19, 4):
        if abs(xx) > 2: shape('Bitta', 'cyl:0.19:0.6', (x0 + xx, 8.7, 0.3), mat=ferro, coll=envc); shape('BittaCapo', 'sphere', (x0 + xx, 8.7, 0.62), scale=(0.25, 0.25, 0.12), mat=ferro, coll=envc)
    Md('dutch_ship_large_02', 9.6, 23.0, 27.0, rot=0, tri=40000, z=-2.1, lato=1024); Md('ship_pinnace', -16.5, 38.0, 22.0, rot=22, tri=30000, z=-2.1); Md('dutch_ship_medium', 30.0, 100.0, 15.0, rot=70, tri=15000, z=-1.9)
    PS.pulisci()
    PS.sparsi2(A, prc, x0, h, 'wine_barrel_01', 6, (2.6, 7.0, 3.2, 8.0), (0.9, 1.0), 81); Md('wine_barrel_01', -3.8, 5.8, 1.0, rot=20, coll=prc); Md('wine_barrel_01', -4.8, 5.2, 1.0, rot=80, coll=prc)
    Md('wooden_crate_02', 4.4, 1.9, 0.55, rot=15, coll=prc); Md('wooden_crate_02', 4.5, 2.0, 0.55, rot=40, z=0.55, coll=prc); Md('wooden_crate_02', 5.9, 1.6, 0.55, rot=-10, coll=prc); Md('old_military_crate', -3.0, 3.6, 0.42, rot=20, tri=6000, coll=prc); Md('wooden_bucket_01', -2.2, 6.6, 0.45, coll=prc)
    shape('PaloSalvagente', 'cyl:0.06:1.5', (x0 - 2.6, 8.5, 0.75), mat=legno2, coll=prc); Md('lifebuoy', -2.6, 8.36, 0.8, z=0.75, coll=prc)
    _lampione(envc, x0, -6.2, 7.8, 0.0, luci, 5.0, 60); _lampione(envc, x0, 6.6, 7.8, 0.0, luci, 5.0, 60)
    tegole = T('grey_roof_tiles_02', 1.6, 1.2, tinta=kitlook._k((0.86, 0.22, 0.12), 2.2))
    for k, (yy, col) in enumerate(((-4.4, (1.0, 0.78, 0.3)), (1.1, (0.95, 0.5, 0.45)), (6.6, (0.45, 0.72, 0.95)))):
        _casa(envc, (x0 - 12.2, yy, 0), PI / 2, 5.3, 4.8, True, T('Plaster001', 2.4, tinta=kitlook._k(col, 1.15, 1.9)), tegole, seme=k + 2, si=k)
    _casa(envc, (x0 + 13.0, 2.6, 0), -PI / 2, 7.2, 5.6, False, T('brown_planks_03', 1.8, 1.0), tegole, seme=9, si=3, alto=3.8)
    Md('rock_face_01', -40.0, 74.0, 11.0, rot=30, z=-3.0); faro(envc, (x0 - 40.0, 74.0, 6.2), 18.0)
    PS.pulisci()
    return dict(h=h, cam=((1.0, -7.5, 2.4), (0.6, 6.0, 4.0), 21), luci=luci)

# ---------------------------------------------------------------------------------------------------- ferrovia
def ferrovia(x0, envc, prc):
    """stazione di campagna: banchina con pensilina, cartello, orologio, panchina; due binari veri con traversine e ghiaia, treno merci e treno veloce, pali della luce, colline e alberi."""
    base = PS.colline(amp=6.0, rx=75.0, ry=14.5, cy=3.0, bordo=16.0, lontano=10.0, fase=91.0); rnd = random.Random(9); luci = []
    h = lambda x, y: 0.4 if (-3.0 <= y <= 6.0 and abs(x) <= 18.0) else base(x, y)
    Md = lambda *a, **k: PS.modello(A, k.pop('coll', envc), x0, h, *a, **k)
    PS.terreno(envc, x0, T('Grass001', 3.0, tinta=(1.0, 1.3, 0.68), ruvidita=1.5), base, xr=(-120, 120), yr=(-30, 190))
    cem = T('Concrete034', 3.0, 0.6); ghiaia = T('gravel_floor', 2.0, 1.2); trav = material('S_fer_trav', (0.16, 0.1, 0.06), rough=0.85); acc = material('S_fer_acc', (0.55, 0.56, 0.6), rough=0.3, metallic=0.9); giallo = material('S_fer_giallo', (1.0, 0.8, 0.05), rough=0.6); scuro = material('S_fer_scuro', (0.06, 0.07, 0.08), rough=0.5)
    bx('BanchinaF', (x0 - 18, -3.0, 0.0), (x0 + 18, 6.0, 0.4), T('PavingStones070', 2.0, 0.8), envc); bx('BanchinaBordoF', (x0 - 18, 5.7, 0.0), (x0 + 18, 6.02, 0.42), cem, envc); bx('LineaGialla', (x0 - 18, 5.3, 0.4), (x0 + 18, 5.55, 0.41), giallo, envc)
    def binario(yc):
        bx('Massicciata', (x0 - 115, yc - 1.75, 0.0), (x0 + 115, yc + 1.75, 0.2), ghiaia, envc)
        for xx in np.arange(-62, 62, 0.66): bx('Traversina', (x0 + xx, yc - 1.3, 0.2), (x0 + xx + 0.27, yc + 1.3, 0.32), trav, envc)
        for sg in (-1, 1): bx('Rotaia', (x0 - 115, yc + sg * 0.85 - 0.045, 0.32), (x0 + 115, yc + sg * 0.85 + 0.045, 0.47), acc, envc)
    binario(8.3); binario(12.9); sc = 4.4 / 1.66
    def convoglio(nomi, x_testa, yc):
        xx = x_testa
        for nm in nomi:
            r, d = PS.kenney(A, 'train-kit/' + nm, prc, x0, yc, z=0.32, s=sc, rot=90); r.location.x += xx - d[0] / 2; xx -= d[0] + 0.25
    convoglio(('train-locomotive-a', 'train-carriage-coal', 'train-carriage-box', 'train-carriage-tank', 'train-carriage-lumber', 'train-carriage-flatbed'), 8.6, 8.3)
    convoglio(('train-electric-bullet-a', 'train-electric-bullet-b', 'train-electric-bullet-b', 'train-electric-bullet-c'), 24.0, 12.9)
    _casa(envc, (x0 - 8.4, 2.4, 0.4), PI / 2, 5.0, 4.6, False, T('red_brick', 1.4, 1.0), T('grey_roof_tiles_02', 1.6, 1.2, tinta=kitlook._k((0.86, 0.22, 0.12), 2.2)), seme=5, si=1, alto=3.3)
    blu = material('S_fer_blu', (0.05, 0.2, 0.6), rough=0.5); bianco = material('S_fer_bianco', (0.96, 0.96, 0.94), rough=0.6, emit=(1, 1, 1), emit_strength=0.3)
    mb = MB([scuro, blu])
    for sx in (-1, 1): mb.box((sx * 1.9, 0, 1.4), (0.1, 0.1, 2.8), 0)
    mb.box((0, 0, 2.6), (4.2, 0.1, 0.8), 1); cart = mb.build('Cartello', prc, (x0 - 2.9, 4.7, 0.4)); text_obj(prc, 'NomeStazione', 'PIPPOPOLI', 0.5, bianco, (0, -0.06, 2.6), parent=cart)
    mb = MB([scuro, T('corrugated_iron', 1.5, 1.0)])                                                                                    # pensilina
    for xx in (3.0, 6.0, 9.0):
        for yy in (2.0, 5.0): mb.box((xx, yy, 1.75), (0.14, 0.14, 3.5), 0)
        mb.box((xx, 3.5, 3.45), (0.12, 3.6, 0.14), 0)
    mb.box((6.0, 3.5, 3.62), (7.6, 4.4, 0.14), 1, rx=0.06); mb.build('Pensilina', envc, (x0, 0, 0.4))
    Md('painted_wooden_bench', 4.6, 3.4, 1.0, rot=0, coll=prc); Md('metal_trash_can', 3.4, 2.4, 1.0, coll=prc)
    val = [material('S_valigia%d' % i, c, rough=0.6) for i, c in enumerate(((0.75, 0.12, 0.1), (0.15, 0.35, 0.6), (0.55, 0.36, 0.16)))]; mb = MB(val + [scuro])                 # valigie in primo piano
    for i, (vx, vy, w_, d_, h_) in enumerate(((2.3, -0.6, 0.75, 0.3, 0.55), (2.95, -0.9, 0.6, 0.28, 0.85), (2.45, -0.55, 0.5, 0.26, 0.36))):
        zc = 0.55 + h_ / 2 if i == 2 else h_ / 2; mb.box((vx, vy, zc), (w_, d_, h_), i, rz=0.3 * (i - 1)); mb.box((vx, vy, zc + h_ / 2 + 0.03), (0.18, 0.05, 0.05), 3, rz=0.3 * (i - 1))
    mb.build('Valigie', prc, (x0, 0, 0.4)); Md('wooden_crate_02', -3.4, -1.4, 0.55, rot=20, coll=prc); Md('wooden_crate_02', -3.3, -1.3, 0.55, rot=50, z=0.95, coll=prc)
    shape('OrologioPalo', 'cyl:0.07:3.0', (x0 + 1.9, 4.9, 1.9), mat=scuro, coll=prc); shape('OrologioCassa', 'cyl:0.5:0.2', (x0 + 1.9, 4.9, 3.7), rot=(PI / 2, 0, 0), mat=scuro, coll=prc); shape('OrologioQuadrante', 'cyl:0.43:0.22', (x0 + 1.9, 4.9, 3.7), rot=(PI / 2, 0, 0), mat=bianco, coll=prc)
    shape('Lancetta1', 'cyl:0.025:0.34', (x0 + 1.9, 4.78, 3.84), mat=scuro, coll=prc); shape('Lancetta2', 'cyl:0.025:0.24', (x0 + 2.0, 4.78, 3.74), rot=(0, 1.1, 0), mat=scuro, coll=prc)
    _lampione(envc, x0, -5.2, 5.0, 0.4, luci, 4.6, 40); _lampione(envc, x0, 10.4, 5.0, 0.4, luci, 4.6, 40)
    PS.semaforo(prc, (x0 - 0.9, 6.5, 0.0), rot=0.0, acceso='verde')
    for xx in range(-63, 64, 9):
        shape('PaloLuce', 'cyl:0.13:7.4', (x0 + xx, 15.6, base(xx, 15.6) + 3.7), mat=trav, coll=envc); shape('PaloTraversa', 'cyl:0.07:2.0', (x0 + xx, 15.6, base(xx, 15.6) + 6.9), rot=(PI / 2, 0, 0), mat=trav, coll=envc)
    for dy in (-0.9, 0.0, 0.9): shape('Filo', 'cyl:0.012:130', (x0, 15.6 + dy, 7.0), rot=(0, PI / 2, 0), mat=scuro, coll=envc).visible_shadow = False
    PS.bosco(A, envc, x0, base, MIX, 120, r0=19.5, r1=85.0, alt=(5.5, 9.0), seme=91, cy=6.0, a0=0.5, a1=PI - 0.5); PS.bosco(A, envc, x0, base, MIX, 30, r0=30.0, r1=70.0, alt=(5.5, 9.0), seme=92, cy=22.0, a0=-0.1, a1=PI + 0.1, rx=1.6, ry=0.5)
    kitlook.tune_cutouts(1.9)
    PS.sparsi(kitlook, envc, x0, base, 'grass_medium_01', 40, (-12, 12, -6.5, -3.2), (0.25, 0.45), 93, via=()); PS.sparsi(kitlook, envc, x0, base, 'dandelion_01', 16, (-10, 10, -6.5, -3.2), (0.12, 0.2), 94, via=())
    PS.sparsi(kitlook, envc, x0, base, 'shrub_02', 12, (-30, 30, 15.5, 20), (0.9, 1.7), 95, shadow=True, via=())
    PS.pulisci()
    return dict(h=h, cam=((1.2, -7.5, 2.7), (0.4, 5.5, 3.2), 21), luci=luci)

POSTI = {'N1': cimitero, 'N2': luna, 'N3': isola_pirati, 'N4': castello, 'N5': neve, 'N6': campeggio, 'N7': citta, 'N8': porto, 'N9': ferrovia}

if __name__ == '__main__':
    codes = [a for a in sys.argv if a in POSTI]; OUT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../t016/opt3')); os.makedirs(OUT, exist_ok=True)
    scene = reset_scene(); setup_render(scene, 1080, 1920, samples=16, fps=24, frames=1)
    envc = collection('Env'); chc = collection('Characters'); prc = collection('Props'); cac = collection('Cameras')
    A.qualita_eevee(preset='equilibrato', riflessi=False, scena=scene); scene.view_settings.exposure = 0.25
    try: scene.render.use_motion_blur = False
    except Exception: pass
    A.cielo('sunflowers_puresky', forza=1.1, rotazione=43.0, ris='4k')
    P = pippo.build_pippo(chc); Tb = tumbo.build_tumbo(chc, scale=0.75)
    for r in (P['root'], Tb['root']): r.rotation_mode = 'XYZ'
    for nm in 'LR': P['shoulder' + nm].rotation_mode = 'QUATERNION'
    qd = lambda d: Vector((0, 0, -1)).rotation_difference(Vector(d).normalized())
    P['shoulderL'].rotation_quaternion = qd((-0.14, 0, -1)); P['shoulderR'].rotation_quaternion = qd((0.5, -0.2, 0.8)); pippo.express(P, 1, smile=1.0, mouth_open=0.5); tumbo.tumbo_express(Tb, 1, tongue=0.8)
    camd = bpy.data.cameras.new('Cam'); cam = bpy.data.objects.new('Cam', camd); cac.objects.link(cam); scene.camera = cam; camd.clip_start = 0.05; camd.clip_end = 1500; camd.sensor_width = 36
    tgt = empty('CamTarget', (0, 3, 2), None, cac); ct = cam.constraints.new('TRACK_TO'); ct.target = tgt; ct.track_axis = 'TRACK_NEGATIVE_Z'; ct.up_axis = 'UP_Y'
    for i, code in enumerate(codes):
        x0 = 400.0 * i; print('COSTRUISCO', code, 'MB', PS.rss(), flush=True)
        info = POSTI[code](x0, envc, prc); h = info['h']; cl, tl, lens = info['cam']
        px, py = info.get('pippo', (0.7, 0.0)); tx, ty = info.get('tumbo', (-0.5, -0.3)); P['root'].location = (x0 + px, py, h(px, py)); Tb['root'].location = (x0 + tx, ty, h(tx, ty))
        cam.location = (x0 + cl[0], cl[1], cl[2]); tgt.location = (x0 + tl[0], tl[1], tl[2]); camd.lens = lens
        if info.get('cielo'): aid, fo, ro, op = info['cielo']; A.cielo(aid, forza=fo, rotazione=ro, ris='1k', **op)
        if info.get('sole'):
            en, rt, col = info['sole']; l_ = bpy.data.lights.new('Sole', 'SUN'); so = bpy.data.objects.new('Sole', l_); prc.objects.link(so); so.rotation_euler = tuple(math.radians(v) for v in rt); l_.energy = en; l_.color = col; l_.angle = math.radians(1.5)
        scene.view_settings.exposure = info.get('esposizione', 0.25)
        scene.render.resolution_x = 540; scene.render.resolution_y = 960; scene.eevee.taa_render_samples = 4
        print('PRONTO', code, 'MB', PS.rss(), 'oggetti', len(bpy.data.objects), 'immagini', len(bpy.data.images), flush=True)
        scene.render.filepath = os.path.join(OUT, code + '.png'); bpy.ops.render.render(write_still=True); print('TILE', code, 'MB', PS.rss(), flush=True)
    print('FINE')
