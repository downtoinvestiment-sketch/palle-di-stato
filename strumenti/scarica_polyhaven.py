"""Scarica modelli 3D CC0 da Poly Haven (glTF 1k) per le scene satiriche: ufficio, palazzo, vertice, confini, commercio.
Uso: python3 strumenti/scarica_polyhaven.py [id ...]   -> modelli_satira/polyhaven/<id>/<id>_1k.gltf (+ texture)"""
import os, sys, json, urllib.request
QUI = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); OUT = os.path.join(QUI, 'modelli_satira', 'polyhaven')
SCELTI = {
    'ufficio e governo': ['metal_office_desk', 'modern_arm_chair_01', 'ArmChair_01', 'WoodenChair_01', 'office_notepads', 'clipboard', 'classic_laptop',
                          'desk_lamp_arm_01', 'projector_screen', 'stationery_supplies', 'vintage_stapler'],
    'palazzo e vertici': ['dining_table', 'coffee_table_round_01', 'Chandelier_01', 'fancy_picture_frame_01', 'ornate_mirror_01', 'Sofa_01', 'tea_set_01', 'wine_bottles_01'],
    'comunicazione': ['Megaphone_01', 'Television_01', 'Camera_01', 'security_camera_01', 'flood_lights', 'boombox'],
    'soldi e commercio': ['CashRegister_01', 'Barrel_01', 'Barrel_02', 'cardboard_box_01', 'dutch_ship_medium', 'CoffeeCart_01'],
    'confini e strada': ['concrete_road_barrier', 'concrete_road_barrier_02', 'modular_chainlink_fence', 'large_iron_gate', 'binoculars', 'fire_hydrant'],
    'cibo': ['croissant', 'food_apple_01', 'hamburger_buns', 'bananas', 'carrot_cake'],
}
def get(url): return urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'palle-di-stato'}), timeout=120).read()
ids = sys.argv[1:] or [i for l in SCELTI.values() for i in l]
fatti = []
for i in ids:
    d = os.path.join(OUT, i); g = os.path.join(d, i + '_1k.gltf')
    if os.path.exists(g): fatti.append(i); continue
    try:
        f = json.loads(get('https://api.polyhaven.com/files/' + i))['gltf']['1k']['gltf']
        os.makedirs(d, exist_ok=True); open(g, 'wb').write(get(f['url']))
        for rel, v in f.get('include', {}).items():
            p = os.path.join(d, rel); os.makedirs(os.path.dirname(p), exist_ok=True); open(p, 'wb').write(get(v['url']))
        fatti.append(i); print('ok', i, flush=True)
    except Exception as e: print('ERRORE', i, e, flush=True)
json.dump(dict(licenza='CC0 (Poly Haven, polyhaven.com)', gruppi=SCELTI, scaricati=fatti), open(os.path.join(OUT, 'elenco.json'), 'w'), indent=1, ensure_ascii=False)
print(len(fatti), 'modelli')
