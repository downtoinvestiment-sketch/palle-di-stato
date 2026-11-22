"""
pt_assets.py - Libreria di asset gratuiti (CC0) per i video di Pippo e Tumbo.

Fonti: Poly Haven (modelli 3D realistici, texture PBR, cieli HDRI), ambientCG (materiali PBR, cieli, cibo 3D),
Kenney (4.451 modelli cartoon leggerissimi: case, alberi, auto, mobili, cibo...), KayKit (903 modelli cartoon
piu' morbidi: citta', mobili, cucina, personaggi) e NASA (257 modelli veri: astronauta, razzi, rover, satelliti).
Licenza: CC0 (uso commerciale libero, senza obbligo di citazione). I modelli NASA sono senza copyright:
basta non far sembrare che la NASA sponsorizzi il video.

USO DA TERMINALE (senza Blender):
    python pt_assets.py cerca neve                 # cerca per nome / tag / categoria
    python pt_assets.py cerca albero --tipo modello
    python pt_assets.py cerca casa --origine kenney   # solo i modelli cartoon di Kenney
    python pt_assets.py cerca auto --origine kaykit   # modelli cartoon KayKit
    python pt_assets.py cerca razzo --origine nasa    # modelli veri della NASA
    python pt_assets.py effetti fumo                  # immagini per effetti (fumo, esplosioni, schizzi...)
    python pt_assets.py font                          # font per i sottotitoli
    python pt_assets.py scarica fir_tree_01 Ice003 # scarica (o ri-scarica) asset per nome
    python pt_assets.py scarica-tutto              # ricostruisce l'intera libreria (~18 GB)
    python pt_assets.py scarica-tutto --tipo hdri  # solo un tipo: modello | texture | hdri
    python pt_assets.py stato                      # quanti asset sono gia' su disco
    python pt_assets.py aggiorna-catalogo          # rilegge gli elenchi dalle due fonti (nuovi asset)

USO DENTRO BLENDER (negli script delle scene):
    import pt_assets as A
    A.cielo('snowy_forest_path_01', forza=1.0, rotazione=40)        # luce + sfondo realistico
    ghiaccio = A.materiale('Ice003', dimensione=3.0)                # materiale PBR pronto
    A.applica(pavimento, ghiaccio)
    A.modello('fir_tree_01', posizione=(4, 8, 0), altezza=9)        # albero (versione leggera)
    A.sparpaglia('fir_tree_01', 25, area=(-20, 20, 10, 30), altezza=(7, 11))
    A.albero_cartonato('fir_tree_01', posizione=(0, 30, 0), altezza=12)  # sagoma piatta, senza ombra
    A.bosco_cartonato('fir_tree_01', 40, area=(-30, 30, 25, 45))         # bosco di sfondo fatto di sagome
    A.modello('kaykit/city-builder-bits/car_taxi', altezza=1.5)     # modello cartoon KayKit
    A.modello('nasa/astronaut', altezza=1.9, max_triangoli=40000)   # modello vero della NASA
    A.modello('/percorso/mio_modello.glb', altezza=2)               # un file tuo (glb, gltf, fbx, obj)
    A.effetto('esplosione/explosion03', posizione=(0, 0, 1), larghezza=2, animazione=(40, 14))  # botto
    A.font('LuckiestGuy')                   # percorso del file .ttf per i sottotitoli
    A.qualita_eevee(preset='equilibrato')   # 1080x1920, 6 campioni: il miglior rapporto qualita'/tempo
    A.niente_ombra(terreno, fiocchi)        # oggetti che non devono proiettare ombra

La cartella della libreria e' quella in cui si trova questo file, oppure la variabile
d'ambiente PT_ASSETS. Gli asset mancanti vengono scaricati da soli al primo uso.
Questo file basta da solo: se manca catalogo.json.gz lo ricostruisce dalla rete.
"""
import gzip
import hashlib
import json
import math
import os
import random
import re
import sys
import time
import urllib.parse
import urllib.request
import zipfile

QUI = os.path.dirname(os.path.abspath(__file__))
RADICE = os.environ.get('PT_ASSETS', QUI)
_UA = {'User-Agent': 'pippo-tumbo-asset-kit/1.0'}
_CAT = None

# Mappe che servono a un materiale PBR (le altre vengono ignorate per risparmiare spazio)
_ACG_TIENI = ('_Color.', '_NormalGL.', '_Roughness.', '_Displacement.', '_AmbientOcclusion.',
              '_Metalness.', '_Opacity.', '_Emission.', '.obj', '.fbx', '.glb', '.hdr', '.exr')

# Pacchetti 3D di Kenney (kenney.nl, licenza CC0): modelli cartoon leggerissimi, in formato GLB
_KENNEY_PACCHETTI = [
    'mini-characters', 'mini-shop', 'mini-skate', 'city-kit-roads', 'city-kit-industrial',
    'mini-dungeon', 'mini-forest', 'modular-cave-kit', 'factory-kit', 'car-kit', 'platformer-kit',
    'cube-pets', 'modular-dungeon-kit', 'pirate-kit', 'modular-space-kit', 'graveyard-kit',
    'fantasy-town-kit', 'blaster-kit', 'city-kit-commercial', 'blocky-characters', 'city-kit-suburban',
    'minigolf-kit', 'retro-fantasy-kit', 'retro-urban-kit', 'toy-car-kit', 'holiday-kit', 'coaster-kit',
    'train-kit', 'tower-defense-kit', 'prototype-kit', 'mini-arcade', 'food-kit', 'building-kit',
    'brick-kit', 'marble-kit', 'watercraft-kit', 'space-station-kit', 'survival-kit', 'castle-kit',
    'mini-arena', 'modular-buildings', 'hexagon-kit', 'space-kit', 'nature-kit', 'racing-kit',
    'furniture-kit']
_BLOCCHI = {}
_KENNEY_PAROLE = {
    'city-kit-suburban': 'house houses suburban city buildings', 'city-kit-commercial': 'buildings city shop skyscraper',
    'city-kit-industrial': 'buildings factory city', 'city-kit-roads': 'road street city', 'nature-kit': 'nature trees plants rocks',
    'mini-forest': 'nature trees forest', 'car-kit': 'car vehicle', 'toy-car-kit': 'car vehicle toy', 'racing-kit': 'car race road',
    'train-kit': 'train vehicle rail', 'watercraft-kit': 'boat ship vehicle', 'furniture-kit': 'furniture interior house',
    'food-kit': 'food', 'holiday-kit': 'christmas holiday snow', 'graveyard-kit': 'halloween graveyard', 'pirate-kit': 'pirate ship island',
    'castle-kit': 'castle medieval', 'fantasy-town-kit': 'house medieval town buildings', 'building-kit': 'buildings house walls',
    'modular-buildings': 'buildings house city', 'space-kit': 'space rocket astronaut', 'space-station-kit': 'space station',
    'survival-kit': 'camping tools nature', 'factory-kit': 'factory machine conveyor', 'mini-characters': 'characters people',
    'blocky-characters': 'characters people', 'cube-pets': 'animals pets', 'minigolf-kit': 'golf sport', 'mini-skate': 'skate sport',
    'mini-arena': 'arena sport', 'mini-arcade': 'arcade games', 'mini-shop': 'shop market', 'coaster-kit': 'rollercoaster amusement',
    'marble-kit': 'marble track', 'brick-kit': 'bricks toy', 'platformer-kit': 'platform game', 'tower-defense-kit': 'tower game',
    'hexagon-kit': 'hexagon tiles buildings', 'retro-urban-kit': 'city buildings urban', 'retro-fantasy-kit': 'medieval buildings',
    'blaster-kit': 'weapons', 'modular-dungeon-kit': 'dungeon', 'mini-dungeon': 'dungeon', 'modular-cave-kit': 'cave rocks',
    'modular-space-kit': 'space station', 'prototype-kit': 'prototype shapes'}


def _voce_kenney(slug, nome, titolo=None):
    """Voce di catalogo per un modello Kenney."""
    return dict(tipo='modello', origine='kenney', pacchetto=slug,
                nome=f"{nome.replace('-', ' ').replace('_', ' ')} ({titolo or slug.replace('-', ' ').title()})",
                categorie=['kenney', 'cartoon', 'low poly'] + _KENNEY_PAROLE.get(slug, slug.replace('-', ' ')).split(),
                tag=[w for w in re.split(r'[-_]', nome) if w and not w.isdigit() and len(w) > 1],
                file=f'kenney/{slug}/{nome}.glb', fonte=f'https://kenney.nl/assets/{slug}', licenza='CC0', base=True, download=0)


# Pacchetti KayKit (Kay Lousberg, licenza CC0): cartoon piu' morbidi e curati; stanno su GitHub
_KAYKIT_PACCHETTI = {
    'city-builder-bits': ('KayKit-City-Builder-Bits-1.0', 'city buildings'),
    'furniture-bits': ('KayKit-Furniture-Bits-1.0', 'furniture interior house'),
    'restaurant-bits': ('KayKit-Restaurant-Bits-1.0', 'food kitchen restaurant'),
    'prototype-bits': ('KayKit-Prototype-Bits-1.0', 'prototype shapes'),
    'halloween-bits': ('KayKit-Halloween-Bits-1.0', 'halloween graveyard'),
    'space-base-bits': ('KayKit-Space-Base-Bits-1.0', 'space station base'),
    'character-pack-adventures': ('KayKit-Character-Pack-Adventures-1.0', 'characters people weapons medieval'),
    'character-pack-skeletons': ('KayKit-Character-Pack-Skeletons-1.0', 'characters skeleton halloween weapons'),
    'dungeon-remastered': ('KayKit-Dungeon-Remastered-1.0', 'dungeon medieval'),
    'medieval-hexagon-pack': ('KayKit-Medieval-Hexagon-Pack-1.0', 'medieval buildings castle hexagon tiles nature'),
}
# Modelli della NASA (github.com/nasa/NASA-3D-Resources): senza copyright, un file GLB per modello
_NASA_REPO = 'https://github.com/nasa/NASA-3D-Resources'
_NASA_RAW = 'https://raw.githubusercontent.com/nasa/NASA-3D-Resources/master/'
_NASA_PAROLE = {'rocket': ('saturn', 'ares', 'atlas', 'redstone', 'jupiter', 'launch', 'sls', 'titan', 'delta'),
                'astronaut': ('astronaut', 'spacesuit', 'suit', 'glove', 'helmet', 'mobility unit'),
                'rover': ('rover', 'curiosity', 'perseverance', 'opportunity', 'spirit', 'sojourner', 'viper'),
                'shuttle': ('shuttle',), 'telescope': ('telescope', 'hubble', 'webb', 'observatory', 'kepler', 'chandra'),
                'station': ('station', 'skylab', 'mir', 'gateway'), 'tools': ('hammer', 'ratchet', 'tool', 'grease gun'),
                'asteroid': ('asteroid', 'bennu', 'vesta', 'eros', 'itokawa', 'comet'),
                'antenna': ('dish', 'antenna', 'deep space network'), 'helicopter': ('helicopter', 'ingenuity'),
                'robot': ('robonaut', 'robot', 'rassor', 'valkyrie'), 'lander': ('lander', 'lunar module', 'insight', 'phoenix', 'viking')}


def _voce_kaykit(slug, rel):
    """Voce di catalogo per un modello KayKit. rel: percorso del file dentro la cartella del pacchetto."""
    repo, parole = _KAYKIT_PACCHETTI[slug]
    nome = os.path.splitext(os.path.basename(rel))[0]
    return dict(tipo='modello', origine='kaykit', pacchetto=slug,
                nome=f"{nome.replace('_', ' ')} (KayKit {slug.replace('-', ' ').title()})",
                categorie=['kaykit', 'cartoon', 'low poly'] + parole.split() + [x for x in os.path.dirname(rel).split('/') if x],
                tag=[w.lower() for w in re.split(r'[-_]', nome) if w and not w.isdigit() and len(w) > 1]
                + (['house'] if nome.lower().startswith('building') else []),
                file=f'kaykit/{slug}/{rel}', fonte=f'https://github.com/KayKit-Game-Assets/{repo}', licenza='CC0',
                base=True, download=0)


def _id_nasa(nome):
    return re.sub(r'[^a-z0-9]+', '-', nome.lower()).strip('-')


def _voce_nasa(sid, nel_repo, dimensione=None):
    """Voce di catalogo per un modello NASA. nel_repo: percorso del file .glb dentro il repository."""
    nome = os.path.splitext(os.path.basename(nel_repo))[0]
    testo = (os.path.basename(os.path.dirname(nel_repo)) + ' ' + nome).lower()
    tag = []
    for w in re.split(r'[^a-z0-9]+', testo):
        if len(w) > 1 and w not in tag:
            tag.append(w)
    tag += [k for k, parole in _NASA_PAROLE.items() if k not in tag and any(q in testo for q in parole)]
    return dict(tipo='modello', origine='nasa', nome=f'{nome} (NASA)', categorie=['nasa', 'space', 'realistic'], tag=tag,
                file=f'nasa/{sid}.glb', url=_NASA_RAW + urllib.parse.quote(nel_repo), dimensione=dimensione,
                fonte=_NASA_REPO, licenza='NASA: senza copyright (non far sembrare che la NASA sponsorizzi il video)',
                base=False, download=0)


def _misura_gltf(path):
    """(triangoli, altezza) di un file glTF/GLB letti senza Blender; (None, None) se non si riesce.
    L'altezza e' l'ingombro lungo l'asse verticale del file (Y), con le trasformazioni dei nodi."""
    try:
        with open(path, 'rb') as f:
            if f.read(4) == b'glTF':
                f.read(8)
                lung = int.from_bytes(f.read(4), 'little')
                f.read(4)
                d = json.loads(f.read(lung))
            else:
                f.seek(0)
                d = json.loads(f.read().decode('utf-8'))
        acc, nodi = d.get('accessors', []), d.get('nodes', [])

        def mat(n):
            if 'matrix' in n:
                m = n['matrix']
                return [[m[c * 4 + r] for c in range(4)] for r in range(4)]
            tx, ty, tz = n.get('translation', (0, 0, 0))
            x, y, z, w = n.get('rotation', (0, 0, 0, 1))
            sx, sy, sz = n.get('scale', (1, 1, 1))
            r = [[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                 [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                 [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]]
            return [[r[0][0] * sx, r[0][1] * sy, r[0][2] * sz, tx], [r[1][0] * sx, r[1][1] * sy, r[1][2] * sz, ty],
                    [r[2][0] * sx, r[2][1] * sy, r[2][2] * sz, tz], [0, 0, 0, 1]]

        def per(a, b):
            return [[sum(a[i][k] * b[k][j] for k in range(4)) for j in range(4)] for i in range(4)]

        tri, ys = 0, []
        radici = d.get('scenes', [{}])[d.get('scene', 0)].get('nodes') if d.get('scenes') else None
        if radici is None:
            figli = {c for n in nodi for c in n.get('children', [])}
            radici = [i for i in range(len(nodi)) if i not in figli]
        pila = [(i, [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]) for i in radici]
        while pila:
            i, m0 = pila.pop()
            n = nodi[i]
            m = per(m0, mat(n))
            pila += [(c, m) for c in n.get('children', [])]
            if 'mesh' not in n:
                continue
            for p in d['meshes'][n['mesh']].get('primitives', []):
                if p.get('mode', 4) != 4 or 'POSITION' not in p.get('attributes', {}):
                    continue
                pos = acc[p['attributes']['POSITION']]
                tri += (acc[p['indices']]['count'] if 'indices' in p else pos['count']) // 3
                if 'min' in pos and 'max' in pos:
                    for x in (pos['min'][0], pos['max'][0]):
                        for y in (pos['min'][1], pos['max'][1]):
                            for z in (pos['min'][2], pos['max'][2]):
                                ys.append(m[1][0] * x + m[1][1] * y + m[1][2] * z + m[1][3])
        return tri or None, (round(max(ys) - min(ys), 4) if ys else None)
    except Exception:
        return None, None


# --------------------------------------------------------------------------- catalogo
def catalogo():
    """Indice di tutti gli asset: {id: {tipo, nome, categorie, tag, ...}}.
    Se il file catalogo.json.gz non c'e', viene ricostruito da Poly Haven e ambientCG (circa 1 minuto)."""
    global _CAT
    if _CAT is None:
        p = _file_catalogo()
        if not os.path.exists(p):
            aggiorna_catalogo()
        with gzip.open(_file_catalogo(), 'rt', encoding='utf-8') as f:
            _CAT = json.load(f)
    return _CAT


def _file_catalogo():
    for d in (QUI, RADICE):
        p = os.path.join(d, 'catalogo.json.gz')
        if os.path.exists(p):
            return p
    return os.path.join(RADICE, 'catalogo.json.gz')


def _json(url):
    for i in range(4):
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=_UA), timeout=60))
        except Exception as e:
            err = e
            time.sleep(1 + 2 * i)
    raise IOError(f'Non riesco a leggere {url} ({err})')


# Mappe Poly Haven da tenere, e quanti materiali ambientCG (i piu' scaricati) per famiglia fanno parte della libreria base
_PH_MAPPE = ('Diffuse', 'nor_gl', 'Rough', 'Displacement', 'AO', 'Metal', 'Mask', 'translucent', 'col_01', 'col_02',
             'col_03', 'col1', 'col2', 'coll1', 'coll2', 'col_1', 'col_2', 'diff_png')
_ACG_BASE = {'Ice': 99, 'Snow': 99, 'Grass': 99, 'Moss': 99, 'ScatteredLeaves': 99, 'Lava': 99, 'Ground': 45, 'Bark': 10,
             'Rock': 20, 'Rocks': 10, 'Gravel': 15, 'Asphalt': 15, 'Road': 20, 'PavingStones': 25, 'Bricks': 25, 'Tiles': 30,
             'Wood': 25, 'WoodFloor': 20, 'Planks': 20, 'Metal': 30, 'Fabric': 30, 'Leather': 10, 'Concrete': 20,
             'Marble': 10, 'Plastic': 99, 'Rubber': 99, 'Carpet': 10, 'RoofingTiles': 15, 'Facade': 99, 'Fence': 99,
             'Sign': 10, 'PaintedPlaster': 10, 'PaintedMetal': 10, 'PaintedWood': 10, 'CorrugatedSteel': 8,
             'WoodSiding': 8, 'ThatchedRoof': 99, 'Wallpaper': 99, 'Pizza': 99, 'Candy': 99, 'Cardboard': 99, 'Foam': 99,
             'Sponge': 99, 'Paper': 99, 'Styrofoam': 99, 'Rope': 99, 'Net': 99, 'Wicker': 6, 'Clay': 99, 'Terrazzo': 5,
             'DiamondPlate': 4, 'Rust': 99, 'Porcelain': 99, 'SolarPanel': 99, 'Pathway': 99, 'Foil': 99,
             'ChristmasTreeOrnament': 6, 'Onyx': 3, 'Granite': 5, 'Travertine': 4, 'Plaster': 99, 'Paint': 99,
             'Bamboo': 99, 'Cork': 99, 'SheetMetal': 99, 'MetalPlates': 6, 'Chipboard': 3, 'WoodChips': 99, 'Logs': 99,
             'TreeEnd': 99, 'Shells': 99, 'Leaf': 99, 'Grate': 99, 'Rails': 99, 'Tatami': 3, 'PaintedBricks': 99,
             'GlazedTerracotta': 99, 'Chainmail': 2, 'MetalWalkway': 4, 'Pipe': 99, 'TactilePaving': 3,
             'AcousticFoam': 99, 'OfficeCeiling': 2, 'Ivory': 2}


def aggiorna_catalogo(verboso=True, kenney=True, kaykit=True, nasa=True):
    """Ricostruisce catalogo.json.gz interrogando Poly Haven, ambientCG, Kenney, KayKit e NASA
    (serve la rete, 4-5 minuti). Le misure gia' note (triangoli, altezza) vengono conservate."""
    global _CAT
    import concurrent.futures as cf
    vecchio = {}
    try:
        with gzip.open(_file_catalogo(), 'rt', encoding='utf-8') as f:
            vecchio = json.load(f)
    except Exception:
        pass
    cat = {}
    elenchi = {t: _json(f'https://api.polyhaven.com/assets?t={t}') for t in ('models', 'textures', 'hdris')}
    tutti = [k for t in elenchi for k in elenchi[t]]
    if verboso:
        print(f'Poly Haven: {len(tutti)} asset, leggo gli elenchi dei file...', flush=True)
    with cf.ThreadPoolExecutor(12) as ex:
        meta = dict(zip(tutti, ex.map(lambda k: _json(f'https://api.polyhaven.com/files/{k}'), tutti)))
    comune = lambda a, v: dict(nome=v['name'], categorie=v['categories'], tag=v.get('tags', []),
                               fonte=f'https://polyhaven.com/a/{a}', licenza='CC0', download=v.get('download_count', 0),
                               base=True, origine='polyhaven')
    for a, v in elenchi['models'].items():
        b = meta[a].get('blend', {}).get('1k', {}).get('blend')
        if not b:
            continue
        fn = b['url'].split('/')[-1]
        files = [[b['url'], f'modelli/{a}/{fn}', b['size'], b['md5']]]
        files += [[i['url'], f'modelli/{a}/{rel}', i['size'], i['md5']] for rel, i in b.get('include', {}).items()]
        cat[a] = dict(tipo='modello', poligoni=v.get('polycount'), cartella=f'modelli/{a}', blend=f'modelli/{a}/{fn}',
                      file=files, **comune(a, v))
    for a, v in elenchi['textures'].items():
        mappe, files = {}, []
        for m in meta[a]:
            if m in _PH_MAPPE:
                e = meta[a][m].get('1k', {})
                f = e.get('jpg') or e.get('png')
                if f:
                    rel = f"texture/{a}/{f['url'].split('/')[-1]}"
                    files.append([f['url'], rel, f['size'], f['md5']])
                    mappe[m] = rel
        cat[a] = dict(tipo='texture', dimensioni_mm=v.get('dimensions'), cartella=f'texture/{a}', mappe=mappe,
                      file=files, **comune(a, v))
    hd = elenchi['hdris']
    inverno = [k for k, v in hd.items() if any(t in v.get('tags', []) for t in ('snow', 'winter', 'ice', 'frozen'))]
    top = sorted((k for k, v in hd.items() if 'outdoor' in v['categories']), key=lambda k: -hd[k]['download_count'])[:45]
    in4k = set(inverno + top)
    for a, v in hd.items():
        d = meta[a]['hdri']
        f = d['1k']['hdr']
        fn = f['url'].split('/')[-1]
        e = dict(tipo='hdri', file_1k=f'hdri/1k/{fn}', file=[[f['url'], f'hdri/1k/{fn}', f['size'], f['md5']]], **comune(a, v))
        for r in ('2k', '4k', '8k'):
            if r in d:
                e['url_' + r] = d[r]['hdr']['url']
        if a in in4k and '4k' in d:
            e['file_4k'] = 'hdri/4k/' + d['4k']['hdr']['url'].split('/')[-1]
        cat[a] = e
    # ambientCG
    acg, off = [], 0
    while True:
        d = _json('https://ambientcg.com/api/v2/full_json?limit=250&offset=%d&include=downloadData,tagData,displayData,dimensionsData&sort=Popular' % off)
        acg += d['foundAssets']
        off += 250
        if len(d['foundAssets']) < 250:
            break
    per_famiglia = {}
    for a in acg:
        if a['dataType'] == 'Material':
            per_famiglia.setdefault(re.sub(r'\d+[A-Z]?$', '', a['assetId']), []).append(a)
    base = set()
    for fam, n in _ACG_BASE.items():
        base |= {a['assetId'] for a in sorted(per_famiglia.get(fam, []), key=lambda a: -a['downloadCount'])[:n]}
    for a in acg:
        tipo_acg, aid = a['dataType'], a['assetId']
        if tipo_acg not in ('Material', '3DModel', 'HDRI', 'Decal', 'Atlas', 'PlainTexture') or aid in cat:
            continue
        try:
            dls = {x['attribute']: x for x in a['downloadFolders']['default']['downloadFiletypeCategories']['zip']['downloads']}
        except Exception:
            continue
        attr = {'3DModel': 'LQ-1K-JPG', 'HDRI': '1K'}.get(tipo_acg, '1K-JPG')
        if attr not in dls:
            continue
        fam = re.sub(r'\d+[A-Z]?$', '', aid).lower()
        e = dict(nome=a.get('displayName') or aid, tag=a.get('tags', []), cartella=f'ambientcg/{aid}',
                 zip=dls[attr]['downloadLink'], fonte=a.get('shortLink'), licenza='CC0',
                 download=a.get('downloadCount', 0), origine='ambientcg')
        if tipo_acg == 'HDRI':
            e.update(tipo='hdri', categorie=['hdri', 'sky'] + [t for t in a.get('tags', []) if t in (
                'day', 'night', 'evening', 'morning', 'sunset', 'sunrise', 'overcast', 'clear', 'cloudy', 'indoor', 'outdoor',
                'urban', 'nature', 'studio', 'snow', 'winter', 'desert', 'forest', 'beach', 'city', 'street', 'park', 'field')],
                zip_4k=dls.get('4K', {}).get('downloadLink'), base=True)
        elif tipo_acg == '3DModel':
            e.update(tipo='modello', categorie=[fam], base=True)
        elif tipo_acg == 'Material':
            e.update(tipo='texture', categorie=[fam], base=aid in base)
        else:
            e.update(tipo='texture', categorie=[fam, {'Decal': 'decal', 'Atlas': 'atlas', 'PlainTexture': 'plain'}[tipo_acg]], base=False)
        if a.get('dimensionX'):
            e['dimensioni_mm'] = [a['dimensionX'] * 10, a['dimensionY'] * 10]
        cat[aid] = e
    # Kenney: i pacchetti sono piccoli (180 MB in tutto), si scaricano per leggerne l'elenco
    if kenney:
        if verboso:
            print(f'Kenney: {len(_KENNEY_PACCHETTI)} pacchetti...', flush=True)
        for slug in _KENNEY_PACCHETTI:
            try:
                d = _scarica_kenney(slug)
            except Exception as err:
                print('  pacchetto saltato:', slug, err)
                continue
            for f in sorted(os.listdir(d)):
                if f.lower().endswith('.glb'):
                    cat[f'kenney/{slug}/{f[:-4]}'] = _voce_kenney(slug, f[:-4])
    # KayKit: come Kenney, pacchetti piccoli (70 MB in tutto) scaricati da GitHub
    if kaykit:
        if verboso:
            print(f'KayKit: {len(_KAYKIT_PACCHETTI)} pacchetti...', flush=True)
        for slug in _KAYKIT_PACCHETTI:
            try:
                d = _scarica_kaykit(slug)
            except Exception as err:
                print('  pacchetto saltato:', slug, err)
                cat.update({k: v for k, v in vecchio.items() if v.get('origine') == 'kaykit' and v.get('pacchetto') == slug})
                continue
            for radice, _, files in os.walk(d):
                for f in sorted(files):
                    if f.lower().endswith(('.gltf', '.glb')):
                        rel = os.path.relpath(os.path.join(radice, f), d).replace(os.sep, '/')
                        e = _voce_kaykit(slug, rel)
                        e['triangoli'], e['altezza_m'] = _misura_gltf(os.path.join(radice, f))
                        cat[f'kaykit/{slug}/{os.path.splitext(f)[0]}'] = e
    # NASA: l'elenco dei file si legge dal repository senza scaricarne il contenuto
    if nasa:
        try:
            for sid, nel_repo in _elenco_nasa().items():
                cat['nasa/' + sid] = _voce_nasa(sid, nel_repo)
        except Exception as err:
            print('  NASA: elenco non letto, tengo le voci di prima:', err)
            cat.update({k: v for k, v in vecchio.items() if v.get('origine') == 'nasa'})
    for k, v in cat.items():  # misure e dimensioni gia' note
        for campo in ('triangoli', 'altezza_m', 'dimensione'):
            if v.get(campo) is None and vecchio.get(k, {}).get(campo) is not None:
                v[campo] = vecchio[k][campo]
    os.makedirs(RADICE, exist_ok=True)
    with gzip.open(os.path.join(RADICE, 'catalogo.json.gz'), 'wt', encoding='utf-8') as f:
        json.dump(cat, f, separators=(',', ':'))
    _CAT = cat
    if verboso:
        print(f'Catalogo aggiornato: {len(cat)} asset')
    return cat


def info(aid):
    c = catalogo()
    if aid not in c:
        vicini = [k for k in c if aid.lower() in k.lower()][:8]
        raise KeyError(f"Asset '{aid}' non trovato nel catalogo. Simili: {vicini}")
    return c[aid]


def percorso(rel):
    return os.path.join(RADICE, rel)


_IT = {'neve': 'snow', 'ghiaccio': 'ice', 'albero': 'tree', 'alberi': 'tree', 'erba': 'grass', 'prato': 'grass',
       'fiore': 'flower', 'fiori': 'flower', 'roccia': 'rock', 'rocce': 'rock', 'sasso': 'rock', 'sassi': 'rock',
       'legno': 'wood', 'mattoni': 'brick', 'muro': 'wall', 'strada': 'road', 'asfalto': 'asphalt',
       'sabbia': 'sand', 'terra': 'ground', 'fango': 'mud', 'cemento': 'concrete', 'metallo': 'metal',
       'tessuto': 'fabric', 'pelle': 'leather', 'tetto': 'roof', 'piastrelle': 'tiles', 'marmo': 'marble',
       'cielo': 'sky', 'tramonto': 'sunset', 'alba': 'sunrise', 'notte': 'night', 'nuvoloso': 'overcast',
       'sereno': 'clear', 'inverno': 'winter', 'foresta': 'forest', 'bosco': 'forest', 'citta': 'urban',
       'spiaggia': 'beach', 'mare': 'sea', 'montagna': 'mountain', 'sedia': 'chair', 'tavolo': 'table',
       'divano': 'sofa', 'lampada': 'lamp', 'lampione': 'street lamp', 'cibo': 'food', 'pane': 'bread',
       'frutta': 'fruit', 'mela': 'apple', 'torta': 'cake', 'cespuglio': 'shrub', 'pianta': 'plant',
       'piante': 'plant', 'pino': 'pine', 'abete': 'fir', 'tronco': 'trunk', 'ceppo': 'stump',
       'staccionata': 'fence', 'recinto': 'fence', 'cancello': 'gate', 'barile': 'barrel', 'cassa': 'crate',
       'scala': 'ladder', 'martello': 'hammer', 'attrezzi': 'tools', 'secchio': 'bucket', 'nave': 'ship',
       'ghiaia': 'gravel', 'muschio': 'moss', 'corteccia': 'bark', 'foglie': 'leaves', 'plastica': 'plastic',
       'gomma': 'rubber', 'ruggine': 'rust', 'facciata': 'facade', 'palazzo': 'facade', 'studio': 'studio',
       'casa': 'house', 'case': 'house', 'edificio': 'buildings', 'edifici': 'buildings', 'auto': 'car',
       'macchina': 'car', 'camion': 'truck', 'treno': 'train', 'barca': 'boat', 'mobili': 'furniture',
       'natale': 'christmas', 'animali': 'animals', 'personaggi': 'characters', 'negozio': 'shop',
       'razzo': 'rocket', 'spazio': 'space', 'castello': 'castle', 'pirata': 'pirate', 'fabbrica': 'factory',
       'panchina': 'bench', 'sedie': 'chair', 'pietra': 'stone', 'pietre': 'stone', 'acqua': 'water',
       'fiume': 'river', 'lago': 'lake', 'astronauta': 'astronaut', 'telescopio': 'telescope', 'navicella': 'shuttle',
       'scheletro': 'skeleton', 'cucina': 'kitchen', 'ristorante': 'restaurant', 'elicottero': 'helicopter', 'asteroide': 'asteroid',
       'cavaliere': 'knight', 'mago': 'mage', 'antenna': 'antenna', 'stazione': 'station', 'robot': 'robot', 'campo': 'field', 'parco': 'park', 'interno': 'indoor', 'esterno': 'outdoor', 'pavimento': 'floor', 'parquet': 'wood floor', 'lava': 'lava'}


def cerca(*parole, tipo=None, limite=40, solo_presenti=False, origine=None):
    """Cerca per parole in id, nome, tag e categorie (in inglese; le parole italiane piu' comuni
    vengono tradotte da sole). tipo: 'modello' | 'texture' | 'hdri'. origine: 'polyhaven' | 'ambientcg' | 'kenney' | 'kaykit' | 'nasa'.
    Restituisce [(id, tipo, nome), ...]: prima le corrispondenze esatte, poi le piu' scaricate."""
    query = []
    for p in parole:
        query += _IT.get(p.lower(), p.lower()).split()
    out = []
    for k, v in catalogo().items():
        if tipo and v['tipo'] != tipo:
            continue
        if origine and v.get('origine') != origine:
            continue
        testo = ' '.join([k, v.get('nome', '')] + v.get('tag', []) + v.get('categorie', [])).lower()
        token = set(re.split(r'[^a-z0-9]+', re.sub(r'(?<=[a-z])(?=[A-Z0-9])', ' ', k + ' ' + v.get('nome', '')).lower() + ' ' + testo))
        esatte = sum(1 for q in query if q in token)
        if esatte < len(query) and not all(any(t.startswith(q) for t in token) for q in query):
            continue
        if solo_presenti and not presente(k):
            continue
        out.append((esatte, v.get('download', 0), k, v['tipo'], v.get('nome', '')))
    out.sort(reverse=True)
    return [(k, t, n) for _, _, k, t, n in out[:limite]]


# --------------------------------------------------------------------------- download
def _scarica_file(url, dest, size=None, md5=None, tentativi=5):
    if os.path.exists(dest) and (not size or os.path.getsize(dest) == size):
        return False
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    err = None
    for i in range(tentativi):
        try:
            h = hashlib.md5()
            req = urllib.request.Request(url, headers=_UA)
            with urllib.request.urlopen(req, timeout=180) as r, open(dest + '.part', 'wb') as f:
                while True:
                    b = r.read(1 << 20)
                    if not b:
                        break
                    f.write(b)
                    h.update(b)
            if md5 and h.hexdigest() != md5:
                raise IOError('md5 diverso')
            os.replace(dest + '.part', dest)
            return True
        except Exception as e:  # rete instabile: riprova
            err = e
            time.sleep(2 + 3 * i)
    raise IOError(f'Download fallito: {url} ({err})')


def _estrai_acg(zip_path, cartella):
    os.makedirs(cartella, exist_ok=True)
    with zipfile.ZipFile(zip_path) as z:
        for n in z.namelist():
            base = os.path.basename(n)
            if base and any(t in base for t in _ACG_TIENI):
                with z.open(n) as src, open(os.path.join(cartella, base), 'wb') as dst:
                    dst.write(src.read())


def _scarica_kenney(slug):
    """Scarica ed estrae un pacchetto Kenney (solo i modelli GLB e le loro texture)."""
    import threading
    import http.cookiejar
    dest = percorso('kenney/' + slug)
    blocco = _BLOCCHI.setdefault(slug, threading.Lock())
    with blocco:
        if os.path.isdir(dest) and any(f.endswith('.glb') for f in os.listdir(dest)):
            return dest
        pagina = 'https://kenney.nl/assets/' + slug
        op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
        op.addheaders = [('User-Agent', _UA['User-Agent'])]
        err = None
        for i in range(4):
            try:
                op.open(pagina, timeout=40).read()  # il sito chiede di passare dalla pagina del pacchetto
                rq = urllib.request.Request('https://kenney.nl/download-link/' + ('assets/' + slug).encode().hex(),
                                            headers={'Referer': pagina})
                url = json.load(op.open(rq, timeout=40))['url']
                dati = op.open(urllib.request.Request(url, headers={'Referer': pagina}), timeout=300).read()
                break
            except Exception as e:
                err = e
                time.sleep(2 + 3 * i)
        else:
            raise IOError(f'Download del pacchetto Kenney {slug} fallito ({err})')
        import io
        with zipfile.ZipFile(io.BytesIO(dati)) as z:
            nomi = z.namelist()
            glb = [n for n in nomi if n.lower().endswith('.glb')]
            if not glb:
                raise IOError(f'Il pacchetto Kenney {slug} non contiene modelli GLB')
            cartella = os.path.dirname(glb[0])
            for n in nomi:
                if n.startswith(cartella + '/') and not n.endswith('/'):
                    out = os.path.join(dest, n[len(cartella) + 1:])
                    os.makedirs(os.path.dirname(out), exist_ok=True)
                    with open(out, 'wb') as f:
                        f.write(z.read(n))
            for n in nomi:
                if 'license' in n.lower():
                    with open(os.path.join(dest, 'License.txt'), 'wb') as f:
                        f.write(z.read(n))
        time.sleep(0.5)  # con calma: il sito e' gratuito e vive di donazioni
        return dest


def _scarica_kaykit(slug):
    """Scarica un pacchetto KayKit da GitHub e ne tiene solo i modelli glTF con le loro texture."""
    import io
    import shutil
    import subprocess
    import tempfile
    import threading
    repo = _KAYKIT_PACCHETTI[slug][0]
    dest = percorso('kaykit/' + slug)
    blocco = _BLOCCHI.setdefault('kaykit', threading.Lock())  # un pacchetto alla volta: GitHub limita i download insieme
    with blocco:
        if os.path.isdir(dest) and any(f.lower().endswith(('.gltf', '.glb')) for _, _, fs in os.walk(dest) for f in fs):
            return dest
        url = f'https://github.com/KayKit-Game-Assets/{repo}'
        tmp = tempfile.mkdtemp(prefix='kaykit_')
        try:
            src = os.path.join(tmp, 'repo')
            try:
                subprocess.run(['git', 'clone', '-q', '--depth', '1', url, src], check=True, timeout=900,
                               env=dict(os.environ, GIT_LFS_SKIP_SMUDGE='1'), capture_output=True)
            except Exception:  # senza git (o git bloccato): archivio zip
                shutil.rmtree(src, ignore_errors=True)
                rq = urllib.request.Request(url + '/archive/refs/heads/main.zip', headers=_UA)
                with zipfile.ZipFile(io.BytesIO(urllib.request.urlopen(rq, timeout=300).read())) as z:
                    z.extractall(src)
            n = 0
            for radice, _, files in os.walk(src):
                parti = radice.replace(os.sep, '/').split('/')
                if '.git' in parti or 'gltf' not in parti:
                    continue
                i = len(parti) - 1 - parti[::-1].index('gltf')
                sotto = (['personaggi'] if parti[i - 1].lower() == 'characters' else []) + parti[i + 1:]
                for f in files:
                    if f.endswith('.import'):
                        continue
                    out = os.path.join(dest, *sotto, f)
                    os.makedirs(os.path.dirname(out), exist_ok=True)
                    shutil.copy2(os.path.join(radice, f), out)
                    n += 1
            if not n:
                raise IOError(f'Il pacchetto KayKit {slug} non contiene modelli glTF')
            for radice, _, files in os.walk(src):
                if 'LICENSE.txt' in files:
                    shutil.copy2(os.path.join(radice, 'LICENSE.txt'), os.path.join(dest, 'LICENSE.txt'))
                    break
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        return dest


def _elenco_nasa():
    """{id: percorso nel repository} di tutti i modelli .glb della NASA (clona solo l'indice, pochi secondi)."""
    import shutil
    import subprocess
    import tempfile
    tmp = tempfile.mkdtemp(prefix='nasa_')
    try:
        subprocess.run(['git', 'clone', '-q', '--depth', '1', '--filter=blob:none', '--no-checkout', _NASA_REPO, tmp],
                       check=True, timeout=600, env=dict(os.environ, GIT_LFS_SKIP_SMUDGE='1'), capture_output=True)
        righe = subprocess.run(['git', '-C', tmp, '-c', 'core.quotepath=off', 'ls-tree', '-r', 'HEAD', '--name-only'],
                               check=True, capture_output=True, text=True).stdout.splitlines()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    out = {}
    for r in sorted(righe):
        if r.lower().endswith('.glb'):
            sid = _id_nasa(os.path.splitext(os.path.basename(r))[0])
            if sid in out:
                sid = _id_nasa(os.path.basename(os.path.dirname(r))) + '-' + sid
            out[sid] = r
    return out


def presente(aid):
    """True se i file base dell'asset sono gia' su disco."""
    v = info(aid)
    if isinstance(v.get('file'), str):  # Kenney, KayKit, NASA: un file per modello
        return os.path.exists(percorso(v['file']))
    if v.get('zip'):
        d = percorso(v['cartella'])
        return os.path.isdir(d) and any(f.endswith(('.jpg', '.png', '.obj', '.hdr', '.exr')) for f in os.listdir(d))
    return all(os.path.exists(percorso(rel)) for _, rel, _, _ in v.get('file', []))


def scarica(aid, verboso=False):
    """Si assicura che l'asset sia su disco (scarica solo quello che manca). Restituisce l'info."""
    v = info(aid)
    if v.get('origine') == 'kenney':
        if not presente(aid):
            _scarica_kenney(v['pacchetto'])
            if verboso:
                print('scaricato pacchetto Kenney', v['pacchetto'])
    elif v.get('origine') == 'kaykit':
        if not presente(aid):
            _scarica_kaykit(v['pacchetto'])
            if verboso:
                print('scaricato pacchetto KayKit', v['pacchetto'])
    elif v.get('url'):  # un solo file (modelli NASA)
        if not presente(aid):
            _scarica_file(v['url'], percorso(v['file']), v.get('dimensione'))
            if verboso:
                print('scaricato', v['file'])
    elif v.get('zip'):
        if not presente(aid):
            tmp = percorso(os.path.join('_zip_acg', os.path.basename(v['cartella']) + '.zip'))
            _scarica_file(v['zip'], tmp)
            _estrai_acg(tmp, percorso(v['cartella']))
            os.remove(tmp)
            if verboso:
                print('scaricato', aid)
    else:
        for url, rel, size, md5 in v.get('file', []):
            if _scarica_file(url, percorso(rel), size, md5) and verboso:
                print('scaricato', rel)
    return v


def scarica_hdri(aid, ris='4k'):
    """Scarica un cielo HDRI a risoluzione piu' alta (2k, 4k, 8k) per usarlo come sfondo nitido."""
    v = info(aid)
    url = v.get('url_' + ris)
    if not url:
        raise KeyError(f'{aid}: risoluzione {ris} non disponibile')
    rel = f'hdri/{ris}/' + url.split('/')[-1]
    _scarica_file(url, percorso(rel))
    return percorso(rel)


def scarica_tutto(tipo=None, thread=10):
    """Ricostruisce la libreria (tutti gli asset segnati 'base' nel catalogo)."""
    import concurrent.futures as cf
    ids = [k for k, v in catalogo().items() if v.get('base') and (not tipo or v['tipo'] == tipo)]
    fatti, errori = [0], []

    def uno(k):
        try:
            scarica(k)
            v = info(k)
            if v.get('file_4k') and not os.path.exists(percorso(v['file_4k'])):
                scarica_hdri(k, '4k')
        except Exception as e:
            errori.append((k, repr(e)))
        fatti[0] += 1
        if fatti[0] % 100 == 0:
            print(f'{fatti[0]}/{len(ids)}', flush=True)

    with cf.ThreadPoolExecutor(thread) as ex:
        list(ex.map(uno, ids))
    print(f'Fatto: {len(ids) - len(errori)}/{len(ids)} asset. Errori: {len(errori)}')
    for e in errori[:20]:
        print('  ', e)
    return errori


# --------------------------------------------------------------------------- Blender
def _bpy():
    import bpy
    return bpy


def cielo(aid, forza=1.0, rotazione=0.0, ris='auto', sfondo=True, colore_sfondo=(0.5, 0.7, 1.0),
          ombre_sole=True, scena=None):
    """Imposta il cielo HDRI come luce (e sfondo) della scena.
    rotazione: gradi attorno alla verticale (sposta il sole). ris: 'auto' usa il 4k se c'e', altrimenti 1k.
    sfondo=False: l'HDRI illumina ma la camera vede un colore piatto (stile cartoon).
    ombre_sole=True: in Eevee il sole dell'HDRI proietta ombre nette (non serve una lampada Sun)."""
    bpy = _bpy()
    v = scarica(aid)
    if v['tipo'] != 'hdri':
        raise ValueError(f'{aid} non e\' un HDRI')
    if v.get('zip'):  # cielo ambientCG: sta in uno zip (1K di base, 4K a richiesta)
        d = percorso(v['cartella'])
        if ris == '4k' and v.get('zip_4k') and not any('4K' in f for f in os.listdir(d)):
            tmp = percorso(os.path.join('_zip_acg', aid + '_4K.zip'))
            _scarica_file(v['zip_4k'], tmp)
            _estrai_acg(tmp, d)
            os.remove(tmp)
        cand = sorted(f for f in os.listdir(d) if f.lower().endswith(('.hdr', '.exr')))
        scelta = [f for f in cand if '4K' in f] if ris in ('auto', '4k') else []
        p = os.path.join(d, (scelta or [f for f in cand if '1K' in f] or cand)[0])
    else:
        p = percorso(v['file_1k'])
        if ris == 'auto':
            if v.get('file_4k') and os.path.exists(percorso(v['file_4k'])):
                p = percorso(v['file_4k'])
        elif ris != '1k':
            p = scarica_hdri(aid, ris)
    scena = scena or bpy.context.scene
    w = bpy.data.worlds.new('Cielo_' + aid)
    w.use_nodes = True
    nt = w.node_tree
    nt.nodes.clear()
    tc = nt.nodes.new('ShaderNodeTexCoord')
    mp = nt.nodes.new('ShaderNodeMapping')
    mp.inputs['Rotation'].default_value[2] = math.radians(rotazione)
    env = nt.nodes.new('ShaderNodeTexEnvironment')
    env.image = bpy.data.images.load(p, check_existing=True)
    bg = nt.nodes.new('ShaderNodeBackground')
    bg.inputs['Strength'].default_value = forza
    out = nt.nodes.new('ShaderNodeOutputWorld')
    nt.links.new(tc.outputs['Generated'], mp.inputs['Vector'])
    nt.links.new(mp.outputs['Vector'], env.inputs['Vector'])
    nt.links.new(env.outputs['Color'], bg.inputs['Color'])
    if sfondo:
        nt.links.new(bg.outputs['Background'], out.inputs['Surface'])
    else:
        lp = nt.nodes.new('ShaderNodeLightPath')
        bg2 = nt.nodes.new('ShaderNodeBackground')
        bg2.inputs['Color'].default_value = (*colore_sfondo, 1.0)
        mix = nt.nodes.new('ShaderNodeMixShader')
        nt.links.new(lp.outputs['Is Camera Ray'], mix.inputs['Fac'])
        nt.links.new(bg.outputs['Background'], mix.inputs[1])
        nt.links.new(bg2.outputs['Background'], mix.inputs[2])
        nt.links.new(mix.outputs['Shader'], out.inputs['Surface'])
    if ombre_sole:
        try:  # Eevee (Blender 4.2+): estrae il sole dall'HDRI e gli fa proiettare ombre
            w.use_sun_shadow = True
            w.sun_threshold = 10.0
            w.sun_angle = math.radians(1.5)
            w.sun_shadow_maximum_resolution = 0.02  # 2 cm: stesso aspetto del default (1 mm), render piu' rapido
        except Exception:
            pass
    scena.world = w
    return w


# Campioni per preset, misurati sulla scena di esempio a 1080x1920 (secondi per fotogramma, render senza scheda video):
# veloce 14 s, equilibrato 19 s, alto 25 s, massimo 58 s. Il vecchio metodo (540x960 a 16 campioni, poi ingrandito)
# costava 29 s ed era meno nitido di tutti e quattro.
PRESET = {'veloce': 4, 'equilibrato': 6, 'alto': 8, 'massimo': 16}


def qualita_eevee(campioni=None, riflessi=True, scena=None, preset='equilibrato', risoluzione=(1080, 1920)):
    """Impostazioni Eevee con il miglior rapporto qualita'/tempo trovato con le misure.
    preset: 'veloce' (4 campioni), 'equilibrato' (6), 'alto' (8), 'massimo' (16). campioni: numero a mano.
    risoluzione: va tenuta PIENA (1080x1920). Renderizzare a 540x960 e ingrandire fa risparmiare poco
    (il tempo dipende soprattutto dai campioni) e sfoca tutto: meglio pochi campioni a risoluzione piena.
    riflessi=True: ghiaccio, acqua e pavimenti lucidi riflettono alberi e personaggi; serve un materiale
    poco ruvido: materiale(..., ruvidita=0.25, vernice=1.0). Se nella scena non c'e' niente di lucido
    metti riflessi=False: circa il 25% di tempo in meno.
    Nota: non usare le sonde di riflesso piane insieme a questo metodo, nel render senza scheda video
    spengono i riflessi."""
    bpy = _bpy()
    sc = scena or bpy.context.scene
    sc.render.engine = 'BLENDER_EEVEE' if 'BLENDER_EEVEE' in [e.identifier for e in sc.render.bl_rna.properties['engine'].enum_items] else 'BLENDER_EEVEE_NEXT'
    if risoluzione:
        sc.render.resolution_x, sc.render.resolution_y = risoluzione
        sc.render.resolution_percentage = 100
    sc.eevee.taa_render_samples = int(campioni) if campioni else PRESET[preset]
    for k, val in (('use_raytracing', riflessi), ('ray_tracing_method', 'SCREEN'), ('use_shadows', True),
                   ('use_fast_gi', True), ('fast_gi_resolution', '4')):
        try:
            setattr(sc.eevee, k, val)
        except Exception:
            pass
    try:
        sc.eevee.ray_tracing_options.resolution_scale = '2'
    except Exception:
        pass
    try:
        sc.view_settings.view_transform = 'AgX'
        sc.view_settings.look = 'AgX - Medium High Contrast'
    except Exception:
        pass
    return sc


def niente_ombra(*oggetti):
    """Toglie la proiezione dell'ombra a oggetti che non ne hanno bisogno (terreno piatto, fiocchi di neve,
    particelle, sfondi). L'oggetto resta illuminato e riceve le ombre degli altri. Insieme al limite di
    risoluzione delle ombre messo da cielo() vale circa il 10% di tempo. Accetta oggetti o liste di oggetti."""
    for o in oggetti:
        for x in (o if isinstance(o, (list, tuple)) else [o]):
            for y in [x] + list(getattr(x, 'children_recursive', [])):
                if hasattr(y, 'visible_shadow'):
                    y.visible_shadow = False


def _mappe(aid):
    """{ruolo: percorso} per una texture Poly Haven o un materiale ambientCG."""
    v = scarica(aid)
    m = {}
    if v.get('zip'):
        d = percorso(v['cartella'])
        ruoli = {'_Color.': 'colore', '_NormalGL.': 'normale', '_Roughness.': 'ruvidita',
                 '_Displacement.': 'rilievo', '_AmbientOcclusion.': 'ao', '_Metalness.': 'metallo',
                 '_Opacity.': 'alfa', '_Emission.': 'emissione'}
        for f in sorted(os.listdir(d)):
            for chiave, ruolo in ruoli.items():
                if chiave in f:
                    m[ruolo] = os.path.join(d, f)
    else:
        ruoli = {'Diffuse': 'colore', 'diff_png': 'colore', 'nor_gl': 'normale', 'Rough': 'ruvidita',
                 'Displacement': 'rilievo', 'AO': 'ao', 'Metal': 'metallo', 'Mask': 'alfa'}
        mp = v.get('mappe', {})
        for chiave, ruolo in ruoli.items():
            if chiave in mp and ruolo not in m:
                m[ruolo] = percorso(mp[chiave])
        if 'colore' not in m:  # alcune texture hanno piu' varianti di colore (col_01, col_02...)
            for chiave in sorted(mp):
                if chiave.lower().startswith('col'):
                    m['colore'] = percorso(mp[chiave])
                    break
    return m, v


def materiale(aid, dimensione=None, rilievo=1.0, proiezione='box', ruvidita=1.0, tinta=None,
              vernice=0.0, spostamento=False, nome=None):
    """Crea un materiale PBR realistico da una texture (Poly Haven o ambientCG).
    dimensione: lato in metri di una ripetizione della texture (default: misura reale, se nota, o 2 m).
    proiezione: 'box' funziona anche su oggetti SENZA UV (quelli creati da script); 'uv' usa le UV.
    rilievo: intensita' del rilievo (normal map). ruvidita: <1 piu' lucido, >1 piu' opaco.
    tinta: (r, g, b) che moltiplica il colore (valori sopra 1 schiariscono).
    vernice: 0-1, strato lucido trasparente sopra il materiale (ghiaccio, pavimenti bagnati, auto). spostamento=True: rilievo vero (solo Cycles, mesh fitta)."""
    bpy = _bpy()
    mappe, v = _mappe(aid)
    if dimensione is None:
        dm = v.get('dimensioni_mm') or []
        dimensione = (dm[0] / 1000.0) if dm and dm[0] else 2.0
    mat = bpy.data.materials.new(nome or 'PT_' + aid)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    tc = nt.nodes.new('ShaderNodeTexCoord')
    mp = nt.nodes.new('ShaderNodeMapping')
    s = 1.0 / max(dimensione, 1e-6)
    mp.inputs['Scale'].default_value = (s, s, s)
    if proiezione == 'box':
        # coordinate dell'oggetto moltiplicate per la sua scala: la texture mantiene la misura reale
        # anche su oggetti scalati (un cubo allungato, un piano ingrandito) e non scivola quando si muovono
        sc_attr = nt.nodes.new('ShaderNodeAttribute')
        sc_attr.attribute_type = 'OBJECT'
        sc_attr.attribute_name = 'scale'
        molt = nt.nodes.new('ShaderNodeVectorMath')
        molt.operation = 'MULTIPLY'
        nt.links.new(tc.outputs['Object'], molt.inputs[0])
        nt.links.new(sc_attr.outputs['Vector'], molt.inputs[1])
        nt.links.new(molt.outputs['Vector'], mp.inputs['Vector'])
    else:
        nt.links.new(tc.outputs['UV'], mp.inputs['Vector'])

    def img(ruolo, colore=False):
        if ruolo not in mappe:
            return None
        n = nt.nodes.new('ShaderNodeTexImage')
        n.image = bpy.data.images.load(mappe[ruolo], check_existing=True)
        if not colore:
            n.image.colorspace_settings.name = 'Non-Color'
        if proiezione == 'box':
            n.projection = 'BOX'
            n.projection_blend = 0.25
        nt.links.new(mp.outputs['Vector'], n.inputs['Vector'])
        return n

    c = img('colore', True)
    if c:
        sorgente = c.outputs['Color']
        ao = img('ao')
        if ao:
            mx = nt.nodes.new('ShaderNodeMix')
            mx.data_type = 'RGBA'
            mx.blend_type = 'MULTIPLY'
            mx.inputs['Factor'].default_value = 0.6
            nt.links.new(sorgente, mx.inputs['A'])
            nt.links.new(ao.outputs['Color'], mx.inputs['B'])
            sorgente = mx.outputs['Result']
        if tinta:
            mt = nt.nodes.new('ShaderNodeMix')
            mt.data_type = 'RGBA'
            mt.blend_type = 'MULTIPLY'
            mt.inputs['Factor'].default_value = 1.0
            mt.clamp_result = True
            mt.inputs['B'].default_value = (*tinta, 1.0)
            nt.links.new(sorgente, mt.inputs['A'])
            sorgente = mt.outputs['Result']
        nt.links.new(sorgente, bsdf.inputs['Base Color'])
    r = img('ruvidita')
    if r:
        if ruvidita != 1.0:
            mm = nt.nodes.new('ShaderNodeMath')
            mm.operation = 'MULTIPLY'
            mm.use_clamp = True
            mm.inputs[1].default_value = ruvidita
            nt.links.new(r.outputs['Color'], mm.inputs[0])
            nt.links.new(mm.outputs['Value'], bsdf.inputs['Roughness'])
        else:
            nt.links.new(r.outputs['Color'], bsdf.inputs['Roughness'])
    else:
        bsdf.inputs['Roughness'].default_value = min(1.0, 0.5 * ruvidita)
    m = img('metallo')
    if m:
        nt.links.new(m.outputs['Color'], bsdf.inputs['Metallic'])
    n = img('normale')
    if n and rilievo > 0:
        nm = nt.nodes.new('ShaderNodeNormalMap')
        nm.inputs['Strength'].default_value = rilievo
        nt.links.new(n.outputs['Color'], nm.inputs['Color'])
        nt.links.new(nm.outputs['Normal'], bsdf.inputs['Normal'])
    a = img('alfa')
    if a:
        nt.links.new(a.outputs['Color'], bsdf.inputs['Alpha'])
    e = img('emissione', True)
    if e:
        nt.links.new(e.outputs['Color'], bsdf.inputs['Emission Color'])
        bsdf.inputs['Emission Strength'].default_value = 1.0
    if vernice > 0:
        bsdf.inputs['Coat Weight'].default_value = vernice
        bsdf.inputs['Coat Roughness'].default_value = 0.03
    if spostamento:
        d = img('rilievo')
        if d:
            dn = nt.nodes.new('ShaderNodeDisplacement')
            dn.inputs['Scale'].default_value = 0.05 * dimensione
            dn.inputs['Midlevel'].default_value = 0.5
            nt.links.new(d.outputs['Color'], dn.inputs['Height'])
            nt.links.new(dn.outputs['Displacement'], out.inputs['Displacement'])
            try:
                mat.displacement_method = 'BOTH'
            except Exception:
                pass
    return mat


def applica(oggetto, mat):
    """Assegna il materiale a un oggetto (sostituisce quelli presenti)."""
    oggetto.data.materials.clear()
    oggetto.data.materials.append(mat)
    return oggetto


def _scegli_collezione(aid, nomi_collezioni, lod):
    """Decide quale collezione del .blend caricare. Molti alberi e rocce contengono piu' versioni
    (LOD0 = pesantissima, LOD2 = leggera) piu' i pezzi usati per costruirle."""
    livelli = {}
    for c in nomi_collezioni:
        mt = re.fullmatch(re.escape(aid) + r'_LOD(\d)', c)
        if mt:
            livelli[int(mt.group(1))] = c
    if livelli:
        if lod == 'leggero':
            n = max(livelli)
        elif lod == 'pesante':
            n = min(livelli)
        else:
            n = min(livelli, key=lambda x: abs(x - int(lod)))
        return livelli[n]
    for nome in (aid + '_static', aid):
        if nome in nomi_collezioni:
            return nome
    return None


def _carica_blend(aid, path, lod='leggero'):
    """Aggiunge al file corrente gli oggetti 'giusti' del .blend e li restituisce (non ancora in scena)."""
    bpy = _bpy()
    with bpy.data.libraries.load(path, link=False) as (src, dst):
        coll = _scegli_collezione(aid, list(src.collections), lod)
        if coll:
            dst.collections = [coll]
        else:
            dst.objects = list(src.objects)
    if coll:
        c = dst.collections[0]
        objs = list(c.all_objects)
        for sub in list(c.children_recursive) + [c]:
            bpy.data.collections.remove(sub)
    else:
        objs = [o for o in dst.objects if o is not None]
    buoni = []
    for o in objs:
        if o.type in ('MESH', 'CURVE', 'EMPTY', 'ARMATURE') and not o.name.startswith('wdg_'):
            buoni.append(o)
        else:
            bpy.data.objects.remove(o)
    return buoni


def _triangoli(objs):
    return sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in objs if o.type == 'MESH')


def modello(aid, posizione=(0, 0, 0), rotazione=0.0, scala=1.0, altezza=None, lod='leggero',
            max_triangoli=None, variante=None, collezione=None, nome=None, veloce=True, appoggia=None):
    """Aggiunge un modello 3D alla scena e restituisce l'oggetto radice (un Empty che lo contiene).
    altezza: se indicata (metri), il modello viene scalato per avere quell'altezza.
    lod: 'leggero' (default), 'pesante' oppure 0/1/2 - conta solo per i modelli che hanno piu' versioni.
    max_triangoli: se indicato, semplifica la geometria fino a quel numero circa.
    variante: per i modelli con piu' esemplari (es. 3 abeti) scegli quale: 0, 1, 2... (default: tutti).
    veloce=True: i materiali trasparenti 'blended' (vetri di lampioni, bottiglie) diventano 'dithered',
    molto piu' rapidi in Eevee (misurato: due lampioni con vetro blended costavano +14 s a fotogramma).
    appoggia: vale per i modelli in un solo file (Kenney, KayKit, NASA, file tuoi). True = il modello viene
    centrato su 'posizione' e appoggiato a terra; 'terra' = solo appoggiato; False = lasciato com'e'.
    Se non lo indichi: True per NASA e file tuoi (hanno l'origine dove capita), 'terra' per KayKit,
    False per Kenney (i pezzi sono fatti per incastrarsi)."""
    bpy = _bpy()
    if aid.lower().endswith(('.glb', '.gltf', '.fbx', '.obj')) and os.path.exists(aid):  # un file tuo
        return _modello_glb(os.path.splitext(os.path.basename(aid))[0], {'file': os.path.abspath(aid)},
                            posizione, rotazione, scala, altezza, collezione, nome, max_triangoli, appoggia)
    v = scarica(aid)
    if v.get('file', '') and isinstance(v['file'], str) and v['file'].lower().endswith(('.glb', '.gltf')):
        return _modello_glb(aid, v, posizione, rotazione, scala, altezza, collezione, nome, max_triangoli, appoggia)
    if v.get('zip'):
        return _modello_obj(aid, v, posizione, rotazione, scala, altezza, collezione, nome)
    objs = _carica_blend(aid, percorso(v['blend']), lod)
    if variante is not None:
        top = sorted([o for o in objs if o.parent is None and o.type == 'MESH'], key=lambda o: o.name)
        if len(top) > 1:
            tieni = top[variante % len(top)]
            figli = set(tieni.children_recursive) | {tieni}
            for o in objs:
                if o not in figli:
                    bpy.data.objects.remove(o)
            objs = list(figli)
            tieni.location.x = 0.0
            tieni.location.y = 0.0
    dest = collezione or bpy.context.scene.collection
    for o in objs:
        dest.objects.link(o)
    radice = bpy.data.objects.new(nome or 'PT_' + aid, None)
    dest.objects.link(radice)
    for o in objs:
        if o.parent is None:
            o.parent = radice
    bpy.context.view_layer.update()
    if veloce:
        for o in objs:
            for sl in getattr(o, 'material_slots', []):
                m = sl.material
                if m and getattr(m, 'surface_render_method', '') == 'BLENDED':
                    m.surface_render_method = 'DITHERED'
    if max_triangoli:
        tot = _triangoli(objs)
        if tot > max_triangoli:
            for o in objs:
                if o.type == 'MESH':
                    md = o.modifiers.new('PT_semplifica', 'DECIMATE')
                    md.ratio = max(0.01, max_triangoli / tot)
    if altezza:
        h = _altezza(objs)
        if h > 1e-6:
            scala = scala * altezza / h
    radice.scale = (scala, scala, scala)
    radice.rotation_euler[2] = math.radians(rotazione)
    radice.location = posizione
    return radice


def _altezza(objs):
    from mathutils import Vector
    zs = []
    for o in objs:
        if o.type == 'MESH':
            zs += [(o.matrix_world @ Vector(c)).z for c in o.bound_box]
    return (max(zs) - min(zs)) if zs else 0.0


def _ha_draco(path):
    """True se il file GLB usa la compressione Draco (quasi tutti i modelli NASA)."""
    try:
        with open(path, 'rb') as f:
            if f.read(4) != b'glTF':
                return False
            f.read(8)
            lung = int.from_bytes(f.read(4), 'little')
            f.read(4)
            return b'KHR_draco_mesh_compression' in f.read(lung)
    except Exception:
        return False


def _togli_draco(src, dst):
    """Riscrive un file GLB compresso con Draco in un GLB normale (stessa geometria, materiali e texture).
    Serve perche' al modulo bpy installato con pip manca il pezzo che legge Draco. Usa il pacchetto DracoPy
    (se manca prova a installarlo da solo)."""
    import struct
    import numpy as np
    try:
        import DracoPy
    except ImportError:
        import subprocess
        for extra in ([], ['--break-system-packages']):
            if subprocess.run([sys.executable, '-m', 'pip', 'install', '-q'] + extra + ['DracoPy'], capture_output=True).returncode == 0:
                break
        import DracoPy
    with open(src, 'rb') as f:
        b = f.read()
    lj = struct.unpack('<I', b[12:16])[0]
    j = json.loads(b[20:20 + lj])
    lb = struct.unpack('<I', b[20 + lj:24 + lj])[0]
    dati = memoryview(b)[28 + lj:28 + lj + lb]
    viste, acc = j.get('bufferViews', []), j.get('accessors', [])
    if len(j.get('buffers', [])) != 1 or any(v.get('buffer', 0) != 0 for v in viste):
        raise IOError('file GLB con piu\' di un blocco dati: non gestito')
    tipi = {5120: np.int8, 5121: np.uint8, 5122: np.int16, 5123: np.uint16, 5125: np.uint32, 5126: np.float32}
    draco = set()
    for m in j.get('meshes', []):
        for pr in m.get('primitives', []):
            e = pr.get('extensions', {}).get('KHR_draco_mesh_compression')
            if e:
                draco.add(e['bufferView'])
    nuovo, nuove, mappa = bytearray(), [], {}

    def aggiungi(blocco, vista):
        while len(nuovo) % 4:
            nuovo.append(0)
        vista = dict(vista, buffer=0, byteOffset=len(nuovo), byteLength=len(blocco))
        nuovo.extend(blocco)
        nuove.append(vista)
        return len(nuove) - 1

    for i, v in enumerate(viste):  # le viste normali (texture, altri dati) restano come sono
        if i not in draco:
            o = v.get('byteOffset', 0)
            mappa[i] = aggiungi(dati[o:o + v['byteLength']], {k: x for k, x in v.items() if k not in ('byteOffset', 'byteLength')})
    fatti = {}
    for m in j.get('meshes', []):
        for pr in m.get('primitives', []):
            e = pr.get('extensions', {}).get('KHR_draco_mesh_compression')
            if not e:
                continue
            if e['bufferView'] not in fatti:
                v = viste[e['bufferView']]
                o = v.get('byteOffset', 0)
                fatti[e['bufferView']] = DracoPy.decode(bytes(dati[o:o + v['byteLength']]))
            mesh = fatti[e['bufferView']]
            if 'indices' in pr and 'bufferView' not in acc[pr['indices']]:
                a = acc[pr['indices']]
                facce = np.asarray(mesh.faces).reshape(-1)
                if a.get('componentType') == 5123 and facce.size and facce.max() > 65535:
                    a['componentType'] = 5125
                a.update(bufferView=-1 - aggiungi(facce.astype(tipi[a.get('componentType', 5125)]).tobytes(), {'target': 34963}),
                         byteOffset=0, count=int(facce.size))
            for nome, uid in e.get('attributes', {}).items():
                if nome not in pr.get('attributes', {}):
                    continue
                a = acc[pr['attributes'][nome]]
                if 'bufferView' in a:
                    continue
                d = np.asarray(mesh.get_attribute_by_unique_id(uid)['data'])
                t = tipi[a.get('componentType', 5126)]
                if d.dtype.kind == 'f' and np.dtype(t).kind != 'f' and a.get('normalized'):
                    d = np.clip(d, 0, 1) * np.iinfo(t).max
                d = np.ascontiguousarray(d.astype(t))
                a.update(bufferView=-1 - aggiungi(d.tobytes(), {'target': 34962}), byteOffset=0, count=int(d.shape[0]))
            del pr['extensions']['KHR_draco_mesh_compression']
            if not pr['extensions']:
                del pr['extensions']
    for a in acc:  # i numeri delle viste sono cambiati: quelli nuovi erano segnati in negativo
        if 'bufferView' in a:
            a['bufferView'] = -1 - a['bufferView'] if a['bufferView'] < 0 else mappa[a['bufferView']]
        for k in ('indices', 'values'):
            if 'sparse' in a and 'bufferView' in a['sparse'].get(k, {}):
                a['sparse'][k]['bufferView'] = mappa[a['sparse'][k]['bufferView']]
    for im in j.get('images', []):
        if 'bufferView' in im:
            im['bufferView'] = mappa[im['bufferView']]
    j['bufferViews'] = nuove
    for k in ('extensionsUsed', 'extensionsRequired'):
        if k in j:
            j[k] = [x for x in j[k] if x != 'KHR_draco_mesh_compression']
            if not j[k]:
                del j[k]
    while len(nuovo) % 4:
        nuovo.append(0)
    j['buffers'] = [{'byteLength': len(nuovo)}]
    testo = json.dumps(j, separators=(',', ':')).encode('utf-8')
    testo += b' ' * (-len(testo) % 4)
    os.makedirs(os.path.dirname(dst) or '.', exist_ok=True)
    with open(dst + '.part', 'wb') as f:
        f.write(struct.pack('<4sII', b'glTF', 2, 12 + 8 + len(testo) + 8 + len(nuovo)))
        f.write(struct.pack('<I4s', len(testo), b'JSON') + testo)
        f.write(struct.pack('<I4s', len(nuovo), b'BIN\x00') + bytes(nuovo))
    os.replace(dst + '.part', dst)
    return dst


def _blender_legge_draco():
    """True se questo Blender sa aprire i file compressi con Draco (al modulo bpy di pip manca il pezzo)."""
    try:
        from io_scene_gltf2.io.com.library import dll_path
        p = dll_path('bf_intern_draco_bridge', 'Draco')
        return bool(p) and os.path.exists(str(p))
    except Exception:
        return None  # non si sa: si prova, e se va male si converte


def _modello_glb(aid, v, posizione, rotazione, scala, altezza, collezione, nome, max_triangoli=None, appoggia=None):
    """Modelli in un solo file (Kenney, KayKit, NASA, oppure un file tuo glb/gltf/fbx/obj).
    Le misure sono le piu' varie (una casa Kenney e' alta 1, l'astronauta NASA 74): usa sempre altezza=.
    I modelli NASA possono avere molti triangoli: con max_triangoli vengono semplificati."""
    bpy = _bpy()
    prima = set(bpy.data.objects)
    azioni_prima = set(bpy.data.actions)
    file = percorso(v['file'])
    est = file.lower().rsplit('.', 1)[-1]
    if est == 'fbx':
        bpy.ops.import_scene.fbx(filepath=file)
    elif est == 'obj':
        bpy.ops.wm.obj_import(filepath=file)
    else:
        def normale(f):  # modello compresso con Draco: lo si riscrive normale, una volta sola
            dentro = os.path.abspath(f).startswith(os.path.abspath(RADICE) + os.sep)
            return _togli_draco(f, f if dentro else percorso(os.path.join('_cache', os.path.basename(f))))
        if est == 'glb' and _ha_draco(file) and _blender_legge_draco() is False:
            file = normale(file)
        try:
            bpy.ops.import_scene.gltf(filepath=file)
        except Exception:
            if not _ha_draco(file):
                raise
            for o in [o for o in bpy.data.objects if o not in prima]:
                bpy.data.objects.remove(o)
            file = normale(file)
            bpy.ops.import_scene.gltf(filepath=file)
    objs = [o for o in bpy.data.objects if o not in prima]
    # l'importatore crea una sfera di servizio per disegnare le ossa: non deve finire nel render
    aiuti = [o for o in objs if any(c.name.startswith('glTF_not_exported') for c in o.users_collection)]
    for o in aiuti:
        o.hide_render = o.hide_viewport = True
    objs = [o for o in objs if o not in aiuti]
    # personaggi con spade e scudi tutti insieme in mano (KayKit): partono a mani vuote, vedi accessori()
    for o in objs:
        if o.parent_type == 'BONE' and 'handslot' in o.parent_bone.lower():
            o.hide_render = o.hide_viewport = True
    visibili = [o for o in objs if not o.hide_render]
    if max_triangoli:
        tot = _triangoli(objs)
        if tot > max_triangoli:
            for o in objs:
                if o.type == 'MESH':
                    o.modifiers.new('PT_semplifica', 'DECIMATE').ratio = max(0.01, max_triangoli / tot)
    dest = collezione or bpy.context.scene.collection
    for o in objs:
        for c in list(o.users_collection):
            if c != dest:
                c.objects.unlink(o)
        if dest not in o.users_collection:
            dest.objects.link(o)
        o.select_set(False)
        for sl in getattr(o, 'material_slots', []):
            if sl.material and getattr(sl.material, 'surface_render_method', '') == 'BLENDED':
                sl.material.surface_render_method = 'DITHERED'
    radice = bpy.data.objects.new(nome or 'PT_' + aid.split('/')[-1], None)
    dest.objects.link(radice)
    for o in objs:
        if o.parent is None:
            o.parent = radice
    nuove = {a.name.split('.')[0]: a.name for a in bpy.data.actions if a not in azioni_prima}
    if nuove:  # personaggi animati: le animazioni si scelgono con anima(); di partenza la posa di riposo
        radice['pt_azioni'] = json.dumps(nuove)
        for riposo in ('Idle', 'idle', 'Unarmed_Idle', 'static'):
            if riposo in nuove:
                anima(radice, riposo)
                break
    bpy.context.view_layer.update()
    if appoggia is None:
        appoggia = {'kenney': False, 'kaykit': 'terra'}.get(v.get('origine'), True)
    if appoggia:
        from mathutils import Vector
        pts = [o.matrix_world @ Vector(c) for o in visibili if o.type == 'MESH' for c in o.bound_box]
        if pts:
            xs, ys, zs = [q.x for q in pts], [q.y for q in pts], [q.z for q in pts]
            sposta = Vector(((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, min(zs))) if appoggia is True else Vector((0, 0, min(zs)))
            for o in objs:
                if o.parent == radice:
                    o.location -= sposta
            bpy.context.view_layer.update()
    if altezza:
        h = _altezza(visibili)
        if h > 1e-6:
            scala = scala * altezza / h
    radice.scale = (scala, scala, scala)
    radice.rotation_euler[2] = math.radians(rotazione)
    radice.location = posizione
    return radice


def accessori(radice, *nomi):
    """Oggetti in mano ai personaggi KayKit (spade, scudi, balestre...): di partenza sono nascosti.
    Senza nomi restituisce l'elenco di quelli che il personaggio ha. Con uno o piu' nomi mostra quelli
    e nasconde gli altri:  A.accessori(cavaliere, '1H_Sword', 'Round_Shield')"""
    slot = [o for o in radice.children_recursive if o.parent_type == 'BONE' and 'handslot' in o.parent_bone.lower()]
    if not nomi:
        return sorted(o.name.split('.')[0] for o in slot)
    for o in slot:
        o.hide_render = o.hide_viewport = o.name.split('.')[0] not in nomi
    return [o for o in slot if not o.hide_render]


def animazioni(radice):
    """Nomi delle animazioni gia' pronte di un personaggio. KayKit (76-95): Idle, Walking_A, Running_A, Cheer,
    Sit_Floor_Idle, Lie_Idle, Throw, Jump_Full_Short, Death_A... Kenney mini-characters (32): idle, walk,
    sprint, jump, sit, die, emote-yes, emote-no, pick-up..."""
    return sorted(json.loads(radice.get('pt_azioni', '{}')))


def anima(radice, nome, inizio=1, ripeti=1, velocita=1.0):
    """Fa partire un'animazione pronta del personaggio dal fotogramma 'inizio'.
    ripeti: quante volte di fila (camminata, corsa). velocita: 1 = normale, 0.5 = al rallentatore.
    Chiamandola piu' volte con 'inizio' diversi le animazioni si susseguono (l'ultima posa resta ferma
    finche' non parte la successiva):  A.anima(r, 'Walking_A', 1, ripeti=4); A.anima(r, 'Cheer', 97)
    Le durate vengono convertite ai fotogrammi al secondo della scena quando il personaggio viene caricato:
    imposta scene.render.fps prima di chiamare modello()."""
    bpy = _bpy()
    nomi = json.loads(radice.get('pt_azioni', '{}'))
    if nome not in nomi:
        raise KeyError(f"Animazione '{nome}' non trovata. Disponibili: {sorted(nomi)}")
    az = bpy.data.actions[nomi[nome]]
    rig = next((o for o in radice.children_recursive if o.type == 'ARMATURE'), None)
    if rig is None:
        raise IOError('Questo modello non ha uno scheletro da animare')
    ad = rig.animation_data or rig.animation_data_create()
    ad.action = None
    for t in ad.nla_tracks:  # l'importatore mette tutte le animazioni una sopra l'altra: si spengono
        if not t.name.startswith('PT_'):
            t.mute = True
    traccia = ad.nla_tracks.new()
    traccia.name = 'PT_' + nome
    striscia = traccia.strips.new(nome, int(inizio), az)
    try:
        if getattr(az, 'slots', None) and getattr(striscia, 'action_slot', None) is None:
            striscia.action_slot = az.slots[0]
    except Exception:
        pass
    striscia.repeat = max(1, ripeti)
    striscia.scale = 1.0 / max(0.01, velocita)
    striscia.extrapolation = 'HOLD_FORWARD' if len(ad.nla_tracks) > 1 else 'HOLD'
    return striscia


def _modello_obj(aid, v, posizione, rotazione, scala, altezza, collezione, nome):
    """Modelli ambientCG (cibo): file .obj + texture."""
    bpy = _bpy()
    d = percorso(v['cartella'])
    obj = [f for f in os.listdir(d) if f.lower().endswith('.obj')]
    if not obj:
        raise IOError(f'{aid}: nessun file .obj nella cartella')
    prima = set(bpy.data.objects)
    bpy.ops.wm.obj_import(filepath=os.path.join(d, obj[0]))
    objs = [o for o in bpy.data.objects if o not in prima]
    mat = materiale(aid, proiezione='uv')
    radice = bpy.data.objects.new(nome or 'PT_' + aid, None)
    dest = collezione or bpy.context.scene.collection
    dest.objects.link(radice)
    for o in objs:
        if o.type == 'MESH':
            applica(o, mat)
        o.parent = radice
    bpy.context.view_layer.update()
    if altezza:
        h = _altezza(objs)
        if h > 1e-6:
            scala = scala * altezza / h
    radice.scale = (scala, scala, scala)
    radice.rotation_euler[2] = math.radians(rotazione)
    radice.location = posizione
    return radice


def sparpaglia(aid, quanti, area, altezza=None, scala=(0.85, 1.15), seme=1, lod='leggero',
               max_triangoli=None, z=0.0, collezione=None):
    """Sparge copie di un modello in un rettangolo area=(xmin, xmax, ymin, ymax): bosco, sassi, cespugli.
    Le copie condividono la stessa geometria (costano poca memoria).
    altezza: numero oppure (min, max) in metri."""
    bpy = _bpy()
    rnd = random.Random(seme)
    dest = collezione or bpy.context.scene.collection
    base = modello(aid, lod=lod, max_triangoli=max_triangoli, collezione=dest, nome=f'PT_{aid}_base')
    figli = list(base.children_recursive)
    h0 = _altezza(figli) or 1.0
    radici = []
    for i in range(quanti):
        if i == 0:
            r = base
        else:
            r = bpy.data.objects.new(f'PT_{aid}_{i:03d}', None)
            dest.objects.link(r)
            copie = {}
            for o in figli:
                c = o.copy()  # copia collegata: stessa mesh
                dest.objects.link(c)
                copie[o] = c
            for o, c in copie.items():
                c.parent = copie.get(o.parent, r)
        if altezza is None:
            s = rnd.uniform(*scala)
        else:
            a = rnd.uniform(*altezza) if isinstance(altezza, (tuple, list)) else altezza * rnd.uniform(*scala)
            s = a / h0
        r.scale = (s, s, s)
        r.rotation_euler[2] = rnd.uniform(0, 2 * math.pi)
        r.location = (rnd.uniform(area[0], area[1]), rnd.uniform(area[2], area[3]), z)
        radici.append(r)
    return radici


def albero_cartonato(aid, posizione=(0, 0, 0), altezza=10.0, rotazione=0.0, verso_camera=True,
                     collezione=None, vista=0, ombra=False):
    """Sagoma piatta con la foto dell'albero (sfondo trasparente): realistica da lontano.
    Ideale per riempire lo sfondo. Le immagini stanno in alberi_cartonati/ .
    ombra=False (default): la sagoma non proietta ombra e costa pochissimo. Con ombra=True il render
    rallenta molto (misurato: 52 sagome con ombra raddoppiano il tempo per fotogramma): usalo solo per
    le poche sagome vicine dove l'ombra a terra si vede."""
    bpy = _bpy()
    d = percorso('alberi_cartonati')
    cand = sorted(f for f in os.listdir(d) if re.fullmatch(re.escape(aid) + r'_\d+(_a\d+)?\.(webp|png)', f))
    if not cand:
        raise IOError(f'Nessuna sagoma per {aid} in alberi_cartonati/')
    img = bpy.data.images.load(os.path.join(d, cand[vista % len(cand)]), check_existing=True)
    w = altezza * img.size[0] / img.size[1]
    me = bpy.data.meshes.new('PT_sagoma_' + aid)
    me.from_pydata([(-w / 2, 0, 0), (w / 2, 0, 0), (w / 2, 0, altezza), (-w / 2, 0, altezza)], [], [(0, 1, 2, 3)])
    uv = me.uv_layers.new()
    for i, co in enumerate([(0, 0), (1, 0), (1, 1), (0, 1)]):
        uv.data[i].uv = co
    ob = bpy.data.objects.new('PT_sagoma_' + aid, me)
    (collezione or bpy.context.scene.collection).objects.link(ob)
    mat = bpy.data.materials.get('PT_sagoma_' + cand[vista % len(cand)])
    if not mat:
        mat = bpy.data.materials.new('PT_sagoma_' + cand[vista % len(cand)])
        mat.use_nodes = True
        nt = mat.node_tree
        bsdf = nt.nodes.get('Principled BSDF')
        tex = nt.nodes.new('ShaderNodeTexImage')
        tex.image = img
        nt.links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
        nt.links.new(tex.outputs['Alpha'], bsdf.inputs['Alpha'])
        bsdf.inputs['Roughness'].default_value = 0.9
        try:
            mat.surface_render_method = 'DITHERED'
        except Exception:
            pass
    me.materials.append(mat)
    ob.location = posizione
    ob.rotation_euler[2] = math.radians(rotazione)
    ob.visible_shadow = bool(ombra)
    if verso_camera and bpy.context.scene.camera:
        con = ob.constraints.new('LOCKED_TRACK')
        con.target = bpy.context.scene.camera
        con.track_axis = 'TRACK_NEGATIVE_Y'
        con.lock_axis = 'LOCK_Z'
    return ob


def bosco_cartonato(ids, quanti, area, altezza=(10, 16), seme=1, z=0.0, collezione=None, ombra=False):
    """Riempie un rettangolo area=(xmin, xmax, ymin, ymax) di sagome d'albero: uno sfondo di bosco
    realistico che non pesa sul render. ids: un nome o una lista di nomi (es. ['fir_tree_01'])."""
    if isinstance(ids, str):
        ids = [ids]
    d = percorso('alberi_cartonati')
    viste = [(a, i) for a in ids for i, f in enumerate(sorted(f for f in os.listdir(d) if re.fullmatch(re.escape(a) + r'_\d+(_a\d+)?\.(webp|png)', f)))]
    if not viste:
        raise IOError(f'Nessuna sagoma per {ids} in alberi_cartonati/')
    rnd = random.Random(seme)
    out = []
    for _ in range(quanti):
        a, i = rnd.choice(viste)
        ob = albero_cartonato(a, posizione=(rnd.uniform(area[0], area[1]), rnd.uniform(area[2], area[3]), z),
                              altezza=rnd.uniform(*altezza), vista=i, collezione=collezione, ombra=ombra)
        if rnd.random() < 0.5:
            ob.scale.x = -1  # specchiata, per variare
        out.append(ob)
    return out


# --------------------------------------------------------------------------- effetti e font
_IT_EFFETTI = {'stella': 'star', 'stelle': 'star', 'scintilla': 'spark', 'scintille': 'spark', 'fuoco': 'fire',
               'fiamma': 'flame', 'luce': 'light|luci/', 'bagliore': 'luci/circle|flare', 'finestra': 'window', 'cono': 'cone',
               'faro': 'cone', 'anello': 'ring', 'raggi': 'streaks', 'acqua': 'water', 'magia': 'magic', 'fumo': 'smoke', 'sporco': 'dirt', 'cerchio': 'circle',
               'cuore': 'heart', 'botto': 'esplosione', 'scoppio': 'esplosione', 'macchia': 'schizzi', 'schizzo': 'schizzi',
               'scoreggia': 'puzza', 'faccina': 'emoticon', 'faccine': 'emoticon', 'nuvola': 'cloud', 'soldi': 'cash',
               'rabbia': 'anger', 'sonno': 'sleep', 'idea': 'idea', 'domanda': 'question', 'goccia': 'drop'}


def effetti(*parole):
    """Nomi degli effetti disponibili (immagini con sfondo trasparente in effetti/), es. 'esplosione/explosion03'.
    Con una o piu' parole filtra l'elenco: effetti('fumo'), effetti('stella'), effetti('emoticon'), effetti('luce').
    Gruppi: particelle, esplosione, lampo, puzza, sbuffo_bianco, fumo_nero, schizzi, emoticon, luci."""
    d = percorso('effetti')
    out = []
    if os.path.isdir(d):
        for g in sorted(os.listdir(d)):
            if os.path.isdir(os.path.join(d, g)):
                out += [f'{g}/{f[:-4]}' for f in sorted(os.listdir(os.path.join(d, g))) if f.lower().endswith('.png')]
    for q in parole:
        q = q.lower()
        alt = _IT_EFFETTI.get(q, q).split('|')
        out = [n for n in out if q in n.lower() or any(x in n.lower() for x in alt)]
    return out


def effetto(nome, posizione=(0, 0, 0), larghezza=1.0, colore=None, luce=1.0, opacita=1.0, rotazione=0.0,
            verso_camera=True, animazione=None, sfumato=True, collezione=None):
    """Immagine piatta che brilla di luce propria: fumo, botto, schizzo, stellina, emoticon sopra la testa.
    nome: 'gruppo/file' (vedi effetti()) oppure il percorso di un PNG tuo con sfondo trasparente.
    larghezza: metri. colore: (r, g, b) per tingere le immagini chiare (particelle, sbuffi bianchi).
    luce: quanto brilla (1 = colori pieni, di piu' = abbagliante). opacita: 0-1.
    rotazione: gradi, gira l'immagine su se stessa. verso_camera: resta sempre rivolta alla camera.
    animazione=(fotogramma, durata): compare a quel fotogramma, si allarga e svanisce in 'durata' fotogrammi.
    sfumato=True: bordi morbidi (fumo, luci); False: granuloso ma un po' piu' rapido.
    Non proietta ombra. Restituisce l'oggetto: si puo' spostare e animare come gli altri."""
    bpy = _bpy()
    file = nome if os.path.exists(nome) else percorso(os.path.join('effetti', nome + '.png'))
    if not os.path.exists(file):
        raise IOError(f"Effetto '{nome}' non trovato. Simili: {effetti(nome.split('/')[-1][:4])[:8]}")
    img = bpy.data.images.load(file, check_existing=True)
    w, h = larghezza / 2, larghezza * img.size[1] / max(1, img.size[0]) / 2
    a = math.radians(rotazione)
    ca, sa = math.cos(a), math.sin(a)
    me = bpy.data.meshes.new('PT_effetto')
    me.from_pydata([(x * ca - y * sa, x * sa + y * ca, 0) for x, y in ((-w, -h), (w, -h), (w, h), (-w, h))], [], [(0, 1, 2, 3)])
    uv = me.uv_layers.new()
    for i, co in enumerate([(0, 0), (1, 0), (1, 1), (0, 1)]):
        uv.data[i].uv = co
    chiave = 'PT_effetto_%s_%s_%.2f_%d' % (os.path.basename(file), colore and tuple(round(c, 3) for c in colore), luce, sfumato)
    mat = bpy.data.materials.get(chiave)
    if not mat:
        mat = bpy.data.materials.new(chiave)
        mat.use_nodes = True
        nt = mat.node_tree
        nt.nodes.clear()
        tex = nt.nodes.new('ShaderNodeTexImage')
        tex.image = img
        if img.size[0] <= 64:
            tex.interpolation = 'Closest'  # pixel art (emoticon): niente sfocatura
        emi = nt.nodes.new('ShaderNodeEmission')
        emi.inputs['Strength'].default_value = luce
        if colore:
            tinta = nt.nodes.new('ShaderNodeMix')
            tinta.data_type = 'RGBA'
            tinta.blend_type = 'MULTIPLY'
            tinta.inputs[0].default_value = 1.0
            nt.links.new(tex.outputs['Color'], tinta.inputs[6])
            tinta.inputs[7].default_value = (colore[0], colore[1], colore[2], 1.0)
            nt.links.new(tinta.outputs[2], emi.inputs['Color'])
        else:
            nt.links.new(tex.outputs['Color'], emi.inputs['Color'])
        ogg = nt.nodes.new('ShaderNodeObjectInfo')  # l'opacita' sta nel colore dell'oggetto: un materiale per tutti
        alfa = nt.nodes.new('ShaderNodeMath')
        alfa.operation = 'MULTIPLY'
        nt.links.new(tex.outputs['Alpha'], alfa.inputs[0])
        nt.links.new(ogg.outputs['Alpha'], alfa.inputs[1])
        trasp = nt.nodes.new('ShaderNodeBsdfTransparent')
        mix = nt.nodes.new('ShaderNodeMixShader')
        nt.links.new(alfa.outputs[0], mix.inputs[0])
        nt.links.new(trasp.outputs[0], mix.inputs[1])
        nt.links.new(emi.outputs[0], mix.inputs[2])
        usc = nt.nodes.new('ShaderNodeOutputMaterial')
        nt.links.new(mix.outputs[0], usc.inputs['Surface'])
        try:
            mat.surface_render_method = 'BLENDED' if sfumato else 'DITHERED'
        except Exception:
            pass
    me.materials.append(mat)
    ob = bpy.data.objects.new('PT_effetto_' + os.path.splitext(os.path.basename(file))[0], me)
    (collezione or bpy.context.scene.collection).objects.link(ob)
    ob.location = posizione
    ob.color = (1, 1, 1, opacita)
    ob.visible_shadow = False
    cam = bpy.context.scene.camera
    if verso_camera and cam:
        con = ob.constraints.new('COPY_ROTATION')
        con.target = cam
    else:
        ob.rotation_euler = (math.radians(90), 0, 0)  # in piedi, rivolta verso -Y
    if animazione:
        f0, durata = animazione
        durata = max(2, int(durata))
        for f, sc, al in ((f0 - 1, 0.0, opacita), (f0, 0.35, opacita), (f0 + round(durata * 0.45), 1.0, opacita),
                          (f0 + durata, 1.2, 0.0), (f0 + durata + 1, 0.0, 0.0)):
            ob.scale = (sc, sc, sc)
            ob.color = (1, 1, 1, al)
            ob.keyframe_insert('scale', frame=f)
            ob.keyframe_insert('color', frame=f)
    return ob


def font(nome=None):
    """Senza argomenti: elenco dei font per i sottotitoli (cartella font/).
    Con un nome, anche parziale (font('luckiest'), font('bangers')): percorso del file .ttf da dare a PIL o a Blender.
    Tutti liberi anche per uso commerciale (CC0 oppure SIL Open Font License / Apache)."""
    d = percorso('font')
    files = sorted(f for f in os.listdir(d) if f.lower().endswith(('.ttf', '.otf'))) if os.path.isdir(d) else []
    if nome is None:
        return [os.path.splitext(f)[0] for f in files]
    q = re.sub(r'[^a-z0-9]', '', nome.lower())
    for f in files:
        if re.sub(r'[^a-z0-9]', '', f.lower()).startswith(q):
            return os.path.join(d, f)
    for f in files:
        if q in re.sub(r'[^a-z0-9]', '', f.lower()):
            return os.path.join(d, f)
    raise IOError(f"Font '{nome}' non trovato. Disponibili: {[os.path.splitext(f)[0] for f in files]}")


# --------------------------------------------------------------------------- terminale
def _main(argv):
    if not argv or argv[0] in ('-h', '--help', 'aiuto'):
        print(__doc__)
        return
    cmd, resto = argv[0], argv[1:]
    tipo = None
    if '--tipo' in resto:
        i = resto.index('--tipo')
        tipo = resto[i + 1]
        resto = resto[:i] + resto[i + 2:]
    origine = None
    if '--origine' in resto:
        i = resto.index('--origine')
        origine = resto[i + 1]
        resto = resto[:i] + resto[i + 2:]
    if cmd == 'cerca':
        for k, t, n in cerca(*resto, tipo=tipo, limite=60, origine=origine):
            print(f"{'*' if presente(k) else ' '} {t:8s} {k:38s} {n}")
        print("(* = gia' su disco)")
    elif cmd == 'scarica':
        for k in resto:
            scarica(k, verboso=True)
            print('ok', k, '->', percorso(info(k).get('cartella', info(k).get('file_1k', ''))))
    elif cmd == 'scarica-tutto':
        scarica_tutto(tipo)
    elif cmd == 'effetti':
        nomi = effetti(*resto)
        print('\n'.join(nomi))
        print(f'({len(nomi)} effetti)')
    elif cmd == 'font':
        print('\n'.join(font()))
    elif cmd == 'aggiorna-catalogo':
        aggiorna_catalogo()
    elif cmd == 'stato':
        from collections import Counter
        tot, ok = Counter(), Counter()
        for k, v in catalogo().items():
            tot[v['tipo']] += 1
            if presente(k):
                ok[v['tipo']] += 1
        for t in tot:
            print(f'{t:8s} {ok[t]:5d} su disco / {tot[t]:5d} in catalogo')
    else:
        print('Comando sconosciuto:', cmd)
        print(__doc__)


if __name__ == '__main__':
    try:
        _main(sys.argv[1:])
    except BrokenPipeError:
        pass
