"""Oggetti del video 031 «Il Nobel per la pace» (copione n. 33 v3).
Bombe (B1 nera tonda con la miccia, B2 bomba d'aereo con le alette), bottone rosso, ufficio di Cappellone (U1 ufficio elegante, U2 bunker con la mappa),
forno della pizza (F1 a cupola di mattoni, F2 a legna in metallo), pizza, cappello da cuoco, medaglia, cartello «DATEMI UN CALCIO», mare, coriandoli.
La mappa del bunker e' inventata (macchie di continenti di fantasia, nessun paese vero). Fronte verso -Y, base a z = 0."""
import math, os, random, bpy
from mathutils import Vector
from common import material, shape, empty
import props029 as P9
PI = math.pi
box = P9.box
_txt = P9._txt


def mats031():
    m = lambda n, c, **k: material('P31_' + n, c, **k)
    return dict(
        nero=m('nero', (0.02, 0.02, 0.025), rough=0.25, spec=0.7), miccia=m('miccia', (0.55, 0.42, 0.25), rough=0.8), scintilla=m('scintilla', (1, 0.8, 0.3), emit=(1.0, 0.6, 0.1), emit_strength=8.0),
        militare=m('militare', (0.28, 0.33, 0.22), rough=0.5), grigio=m('grigio', (0.45, 0.47, 0.5), rough=0.4, metallic=0.5), giallo=m('giallo', (1.0, 0.78, 0.08), rough=0.4),
        rosso=m('rosso', (0.85, 0.05, 0.05), rough=0.25, spec=0.8), rosso_s=m('rosso_s', (0.5, 0.03, 0.03), rough=0.4), cromo=m('cromo', (0.85, 0.86, 0.9), rough=0.12, metallic=1.0),
        legno=m('legno', (0.42, 0.24, 0.1), rough=0.45, spec=0.6), legno_c=m('legno_c', (0.72, 0.52, 0.3), rough=0.6), oro=m('oro', (1.0, 0.72, 0.15), rough=0.25, metallic=0.95),
        blu=m('blu', (0.08, 0.16, 0.45), rough=0.6), crema=m('crema', (0.95, 0.9, 0.78), rough=0.8), tappeto=m('tappeto', (0.55, 0.06, 0.08), rough=0.9),
        cemento=m('cemento', (0.36, 0.37, 0.36), rough=0.9), mappa_mare=m('mappa_mare', (0.05, 0.25, 0.45), rough=0.6, emit=(0.04, 0.2, 0.4), emit_strength=0.6),
        mappa_terra=m('mappa_terra', (0.25, 0.65, 0.25), rough=0.6, emit=(0.2, 0.55, 0.2), emit_strength=0.5), luce_rossa=m('luce_rossa', (1, 0.1, 0.05), emit=(1.0, 0.08, 0.03), emit_strength=6.0),
        schermo=m('schermo', (0.1, 0.5, 0.2), emit=(0.15, 0.9, 0.3), emit_strength=1.5), vetro=m('vetro', (0.6, 0.8, 1.0), rough=0.1, emit=(0.6, 0.8, 1.0), emit_strength=1.4),
        mattone=m('mattone', (0.65, 0.3, 0.18), rough=0.85), fuoco=m('fuoco', (1, 0.5, 0.1), emit=(1.0, 0.45, 0.05), emit_strength=10.0), brace=m('brace', (0.1, 0.03, 0.02), rough=0.9),
        impasto=m('impasto', (0.93, 0.78, 0.5), rough=0.7), pomodoro=m('pomodoro', (0.8, 0.1, 0.05), rough=0.4), mozzarella=m('mozzarella', (0.98, 0.96, 0.9), rough=0.5),
        basilico=m('basilico', (0.1, 0.55, 0.15), rough=0.5), bianco=m('bianco', (0.97, 0.97, 0.96), rough=0.4), cartone=m('cartone', (0.86, 0.68, 0.45), rough=0.9),
        nastro=m('nastro', (0.15, 0.35, 0.85), rough=0.4), scotch=m('scotch', (0.9, 0.85, 0.6), rough=0.3),
    )


def bomba(coll, M, tipo='B1', nome='Bomba'):
    """B1: tonda nera con la miccia accesa (raggio 0,5). B2: bomba d'aereo verde militare con le alette (lunga 1,6). Punta/fronte verso -Y."""
    R = {}; r = R['root'] = empty(nome, (0, 0, 0), None, coll); r.rotation_mode = 'XYZ'
    if tipo == 'B1':
        shape(nome + 'Palla', 'sphere', (0, 0, 0), (0.5, 0.5, 0.5), (0, 0, 0), r, M['nero'], coll)
        shape(nome + 'Collo', 'cyl:1:1', (0, 0, 0.5), (0.14, 0.14, 0.16), (0, 0, 0), r, M['grigio'], coll)
        shape(nome + 'Riflesso', 'sphere', (-0.2, -0.32, 0.22), (0.1, 0.05, 0.12), (0, 0, 0.5), r, M['bianco'], coll)
        for k in range(5): shape(nome + 'Miccia', 'cyl:1:1', (0.03 * k, 0, 0.62 + 0.07 * k), (0.03, 0.03, 0.08), (0, 0.3 + 0.12 * k, 0), r, M['miccia'], coll)
        R['scintilla'] = shape(nome + 'Scintilla', 'sphere', (0.16, 0, 0.98), (0.07, 0.07, 0.07), (0, 0, 0), r, M['scintilla'], coll)
    else:
        shape(nome + 'Corpo', 'sphere', (0, 0, 0), (0.36, 0.8, 0.36), (0, 0, 0), r, M['militare'], coll)
        shape(nome + 'Punta', 'sphere', (0, -0.62, 0), (0.18, 0.2, 0.18), (0, 0, 0), r, M['giallo'], coll)
        shape(nome + 'Coda', 'cyl:1:1', (0, 0.85, 0), (0.18, 0.18, 0.5), (PI / 2, 0, 0), r, M['militare'], coll)
        for k in range(4):
            a = PI / 2 * k + PI / 4
            box(nome + 'Aletta', (0.28 * math.cos(a), 1.0, 0.28 * math.sin(a)), (0.05, 0.42, 0.42), M['grigio'], coll, r, rot=(0, a, 0))
        shape(nome + 'Fascia', 'cyl:1:1', (0, -0.25, 0), (0.37, 0.37, 0.1), (PI / 2, 0, 0), r, M['giallo'], coll)
    return R


def bottone(coll, M, nome='Bottone'):
    """bottone rosso gigante su una base di metallo (la cupola si schiaccia: R['tasto'] scala in z)."""
    R = {}; r = R['root'] = empty(nome, (0, 0, 0), None, coll)
    shape(nome + 'Base', 'cyl:1:1', (0, 0, 0.06), (0.32, 0.32, 0.12), (0, 0, 0), r, M['grigio'], coll)
    t = R['tasto'] = empty(nome + 'Tasto', (0, 0, 0.12), r, coll)
    shape(nome + 'Cupola', 'sphere', (0, 0, 0.0), (0.24, 0.24, 0.16), (0, 0, 0), t, M['rosso'], coll)
    _txt(coll, nome + 'Scritta', 'BOOM', 0.07, M['bianco'], (0, -0.33, 0.06), parent=r, ext=0.005)
    return R


def ufficio(coll, M, A, tipo='U1', C=(0.0, 0.0), bandiera='C'):
    """ufficio di Cappellone attorno a C, stanza 10 x 8 x 4 m chiusa; la scrivania e' a (C, y = 0.6) col bottone sopra (R['bottone_pos'])."""
    X, Y = C; R = {}
    if tipo == 'U1':
        muro, pav = M['crema'], M['tappeto']
        try: pav = A.materiale('WoodFloor043', dimensione=1.5, tinta=(0.8, 0.55, 0.4))
        except Exception: pass
    else:
        muro, pav = M['cemento'], M['cemento']
        try: muro = A.materiale('concrete_wall_008', dimensione=3.0, tinta=(0.7, 0.7, 0.72)); pav = A.materiale('concrete_floor_02', dimensione=3.0)
        except Exception: pass
    box('UF_Pavimento', (X, Y, -0.05), (10, 8, 0.1), pav, coll)
    box('UF_Soffitto', (X, Y, 4.05), (10, 8, 0.1), muro, coll)
    box('UF_Fondo', (X, Y + 4.05, 2), (10, 0.1, 4), muro, coll)
    for s_ in (-1, 1): box('UF_Lato', (X + s_ * 5.05, Y, 2), (0.1, 8, 4), muro, coll)
    box('UF_Davanti', (X, Y - 4.05, 2), (10, 0.1, 4), muro, coll)
    # scrivania
    if tipo == 'U1':
        box('UF_Scrivania', (X, Y + 0.6, 0.42), (2.6, 1.2, 0.84), M['legno'], coll); box('UF_Piano', (X, Y + 0.6, 0.86), (2.75, 1.32, 0.05), M['legno'], coll)
        box('UF_Pannello', (X, Y - 0.02, 0.45), (2.4, 0.04, 0.7), M['legno_c'], coll)
        for i, x in enumerate((-3.2, 3.2)):                                                       # finestre luminose con tende
            box('UF_Finestra', (X + x, Y + 3.98, 2.0), (1.6, 0.04, 2.2), M['vetro'], coll)
            for s_ in (-1, 1): box('UF_Tenda', (X + x + s_ * 0.95, Y + 3.9, 2.0), (0.4, 0.1, 2.6), M['rosso_s'], coll)
        if bandiera == 'USA':
            png = bandiera_usa_texture(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets', 'mappe', 'bandiera_usa.png'))
            b = bandiera_usa(coll, M, png, 'UF_Bandiera')
        else: b = P9.bandiera_c(coll, P9.mats029(), 'UF_Bandiera')
        b.location = (X - 1.7, Y + 3.3, 0); b.rotation_euler = (0, 0, 0.3)
        box('UF_Quadro', (X + 0.1, Y + 3.98, 2.4), (1.6, 0.05, 1.1), M['oro'], coll); box('UF_QuadroTela', (X + 0.1, Y + 3.95, 2.4), (1.4, 0.03, 0.9), M['blu'], coll)
        _txt(coll, 'UF_QuadroScritta', 'PACE', 0.38, M['oro'], (X + 0.1, Y + 3.92, 2.38), ext=0.01)
        box('UF_Tappeto', (X, Y - 0.6, 0.005), (5.0, 3.5, 0.01), M['tappeto'], coll)
    else:
        box('UF_Tavolo', (X, Y + 0.6, 0.45), (3.0, 1.4, 0.9), M['grigio'], coll)
        mp = empty('UF_Mappa', (X, Y + 3.96, 2.3), None, coll)
        box('UF_MappaMare', (0, 0, 0), (7.0, 0.04, 2.8), M['mappa_mare'], coll, mp)
        rnd = random.Random(31)
        for k in range(7):                                                                         # continenti di fantasia
            cx, cz = rnd.uniform(-2.8, 2.8), rnd.uniform(-1.0, 1.0)
            for j in range(4): shape('UF_Terra', 'sphere', (cx + rnd.uniform(-0.4, 0.4), -0.03, cz + rnd.uniform(-0.3, 0.3)), (rnd.uniform(0.25, 0.55), 0.01, rnd.uniform(0.15, 0.35)), (0, 0, 0), mp, M['mappa_terra'], coll)
        for k in range(6): shape('UF_Bersaglio', 'sphere', (rnd.uniform(-3, 3), -0.05, rnd.uniform(-1.1, 1.1)), (0.07, 0.01, 0.07), (0, 0, 0), mp, M['luce_rossa'], coll)
        for k, x in enumerate((-4.2, 4.2)):
            for j in range(3): box('UF_Schermo', (X + x, Y + 2.5 - 1.4 * j, 2.2), (0.05, 1.1, 0.7), M['schermo'], coll)
        for k in range(4): shape('UF_LuceRossa', 'sphere', (X - 3.6 + 2.4 * k, Y + 3.9, 3.8), (0.12, 0.12, 0.12), (0, 0, 0), None, M['luce_rossa'], coll)
    R['bottone_pos'] = (X + 0.45, Y + 0.45, 0.885 if tipo == 'U1' else 0.905)
    return R


def forno(coll, M, A, tipo='F1'):
    """F1: forno a cupola di mattoni con la bocca e il fuoco. F2: forno a legna in metallo nero su gambe, col camino."""
    R = {}; r = R['root'] = empty('Forno', (0, 0, 0), None, coll); r.rotation_mode = 'XYZ'
    if tipo == 'F1':
        try: mt = A.materiale('red_brick_03', dimensione=1.0)
        except Exception: mt = M['mattone']
        box('FO_Base', (0, 0, 0.5), (2.2, 2.2, 1.0), mt, coll, r)
        box('FO_Piano', (0, 0, 1.03), (2.3, 2.3, 0.08), M['cemento'], coll, r)
        shape('FO_Cupola', 'sphere', (0, 0.1, 1.05), (0.95, 0.95, 0.85), (0, 0, 0), r, mt, coll)
        shape('FO_Bocca', 'sphere', (0, -0.82, 1.35), (0.42, 0.12, 0.3), (0, 0, 0), r, M['brace'], coll)
        R['fuoco'] = shape('FO_Fuoco', 'sphere', (0, -0.55, 1.25), (0.3, 0.2, 0.18), (0, 0, 0), r, M['fuoco'], coll)
        shape('FO_Camino', 'cyl:1:1', (0, 0.35, 2.05), (0.14, 0.14, 0.5), (0, 0, 0), r, M['cemento'], coll)
    else:
        for (sx, sy) in ((-1, -1), (1, -1), (1, 1), (-1, 1)): box('FO_Gamba', (sx * 0.5, sy * 0.45, 0.45), (0.06, 0.06, 0.9), M['nero'], coll, r)
        shape('FO_Corpo', 'cyl:1:1', (0, 0.0, 1.35), (0.6, 0.6, 1.3), (PI / 2, 0, 0), r, M['nero'], coll)
        box('FO_Sotto', (0, 0, 1.0), (1.2, 1.3, 0.3), M['nero'], coll, r)
        shape('FO_Sportello', 'cyl:1:1', (0, -0.66, 1.35), (0.5, 0.5, 0.04), (PI / 2, 0, 0), r, M['grigio'], coll)
        R['fuoco'] = shape('FO_Fuoco', 'sphere', (0, -0.69, 1.3), (0.3, 0.02, 0.2), (0, 0, 0), r, M['fuoco'], coll)
        shape('FO_Camino', 'cyl:1:1', (0, 0.3, 2.4), (0.11, 0.11, 1.2), (0, 0, 0), r, M['nero'], coll)
        shape('FO_Termometro', 'cyl:1:1', (0.35, -0.6, 1.8), (0.09, 0.09, 0.03), (PI / 2, 0, 0), r, M['bianco'], coll)
    return R


def pizza(coll, M, nome='Pizza', raggio=0.5):
    r = empty(nome, (0, 0, 0), None, coll); r.rotation_mode = 'XYZ'
    shape(nome + 'Base', 'cyl:1:1', (0, 0, 0.02), (raggio, raggio, 0.04), (0, 0, 0), r, M['impasto'], coll)
    shape(nome + 'Bordo', 'cyl:1:1', (0, 0, 0.035), (raggio * 1.02, raggio * 1.02, 0.05), (0, 0, 0), r, M['impasto'], coll)
    shape(nome + 'Sugo', 'cyl:1:1', (0, 0, 0.055), (raggio * 0.88, raggio * 0.88, 0.02), (0, 0, 0), r, M['pomodoro'], coll)
    rnd = random.Random(7)
    for k in range(9):
        a, d = rnd.uniform(0, 2 * PI), rnd.uniform(0.1, 0.7) * raggio
        shape(nome + 'Mozzarella', 'sphere', (d * math.cos(a), d * math.sin(a), 0.07), (0.09 * raggio * 2, 0.08 * raggio * 2, 0.02), (0, 0, a), r, M['mozzarella'], coll)
    for k in range(5):
        a, d = rnd.uniform(0, 2 * PI), rnd.uniform(0.2, 0.6) * raggio
        shape(nome + 'Basilico', 'sphere', (d * math.cos(a), d * math.sin(a), 0.085), (0.05 * raggio * 2, 0.03 * raggio * 2, 0.01), (0, 0, a), r, M['basilico'], coll)
    return r


def cappello_cuoco(coll, M, parent, loc=(0, 0, 0), s=1.0):
    c = empty('CappelloCuoco', loc, parent, coll)
    shape('CuocoFascia', 'cyl:1:1', (0, 0, 0.06 * s), (0.17 * s, 0.17 * s, 0.12 * s), (0, 0, 0), c, M['bianco'], coll)
    for k in range(5):
        a = k * 2 * PI / 5; shape('CuocoSbuffo', 'sphere', (0.09 * s * math.cos(a), 0.09 * s * math.sin(a), 0.22 * s), (0.12 * s, 0.12 * s, 0.12 * s), (0, 0, 0), c, M['bianco'], coll)
    shape('CuocoTop', 'sphere', (0, 0, 0.27 * s), (0.15 * s, 0.15 * s, 0.1 * s), (0, 0, 0), c, M['bianco'], coll)
    return c


def medaglia(coll, M, nome='Medaglia', s=1.0):
    r = empty(nome, (0, 0, 0), None, coll); r.rotation_mode = 'XYZ'
    shape(nome + 'Disco', 'cyl:1:1', (0, 0, 0), (0.16 * s, 0.16 * s, 0.03 * s), (PI / 2, 0, 0), r, M['oro'], coll)
    _txt(coll, nome + 'Scritta', 'PACE', 0.07 * s, M['legno'], (0, -0.02 * s, 0), parent=r, ext=0.004 * s)
    for s_ in (-1, 1): box(nome + 'Nastro', (s_ * 0.08 * s, 0.0, 0.25 * s), (0.08 * s, 0.01, 0.4 * s), M['nastro'], coll, r, rot=(0, s_ * 0.35, 0))
    return r


def cartello(coll, M, nome='Cartello', testo='DATEMI\nUN CALCIO'):
    r = empty(nome, (0, 0, 0), None, coll); r.rotation_mode = 'XYZ'
    box(nome + 'Cartone', (0, 0, 0), (0.42, 0.01, 0.3), M['cartone'], coll, r)
    o = _txt(coll, nome + 'Testo', testo, 0.075, M['rosso'], (0, 0.008, 0), rot=(PI / 2, 0, PI), parent=r, ext=0.003)
    o.data.space_line = 0.85
    for s_ in (-1, 1): box(nome + 'Scotch', (s_ * 0.17, 0.006, 0.13), (0.1, 0.004, 0.035), M['scotch'], coll, r, rot=(0, s_ * 0.5, 0))
    return r


def mare(coll, C=(0.0, 0.0), raggio=200.0):
    """mare con le onde (rumore) e un materiale blu lucido."""
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=200, y_subdivisions=200, size=2 * raggio, location=(C[0], C[1], 0))
    o = bpy.context.active_object; o.name = 'Mare'
    for c in o.users_collection: c.objects.unlink(o)
    coll.objects.link(o)
    for v in o.data.vertices:
        x, y = v.co.x, v.co.y
        v.co.z = 0.18 * math.sin(0.35 * x + 0.2 * y) + 0.1 * math.sin(0.7 * y - 0.4 * x + 1.3) + 0.05 * math.sin(1.7 * x + 2.1)
    for p in o.data.polygons: p.use_smooth = True
    o.data.materials.append(material('P31_mare', (0.02, 0.18, 0.32), rough=0.12, spec=0.8, coat=0.5))
    return o


def coriandoli(coll, n=60, nome='Coriandolo', seme=3):
    """n coriandoli colorati (quadratini sottili), nascosti a z = -50: si muovono con le chiavi."""
    rnd = random.Random(seme); cols = [(1, 0.2, 0.3), (0.2, 0.7, 1.0), (1, 0.85, 0.1), (0.4, 0.95, 0.35), (0.85, 0.35, 1.0), (1.0, 0.55, 0.1)]
    mats = [material('P31_cor%d' % i, c, rough=0.4, emit=c, emit_strength=0.3) for i, c in enumerate(cols)]
    out = []
    for k in range(n):
        o = shape(nome, 'sphere_lo', (0, 0, -50), (0.08, 0.004, 0.06), (0, 0, 0), None, mats[k % len(mats)], coll); o.rotation_mode = 'XYZ'
        out.append((o, rnd.uniform(0, 2 * PI), rnd.uniform(0.5, 1.0), rnd.uniform(0, 2 * PI), rnd.uniform(-1, 1)))
    return out


# ======================= mappamondo (video 031 v2, richiesta dell'autore: «un mappamondo dove si vedono le bombe cadere in quei paesi») =======================
MONDO = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets', 'mappe', 'mondo50m.geojson')   # Natural Earth 1:50m, pubblico dominio
PAESI = {'Venezuela': (-66.0, 7.5), 'Iran': (53.5, 32.5), 'Yemen': (47.5, 15.6), 'Somalia': (46.0, 6.0), 'Iraq': (43.8, 33.0)}   # (lon, lat) dove cade la bomba


def mondo_texture(out_png, evidenzia=(), W=4096, H=2048):
    """texture equirettangolare da cartone: mare blu, terre verdi con i confini, i paesi in `evidenzia` color sabbia, griglia leggera."""
    import json
    from PIL import Image, ImageDraw
    d = json.load(open(MONDO))
    im = Image.new('RGB', (W, H), (38, 118, 205)); dr = ImageDraw.Draw(im)
    for k in range(1, 12): dr.line([(0, k * H // 12), (W, k * H // 12)], fill=(62, 140, 222), width=3)
    for k in range(1, 24): dr.line([(k * W // 24, 0), (k * W // 24, H)], fill=(62, 140, 222), width=3)
    def xy(c): return ((c[0] + 180.0) / 360.0 * W, (90.0 - c[1]) / 180.0 * H)
    for f in d['features']:
        g = f['geometry']; nome = f['properties']['NAME']
        polys = g['coordinates'] if g['type'] == 'MultiPolygon' else [g['coordinates']]
        col = (240, 196, 92) if nome in evidenzia else (112, 192, 88)
        for poly in polys:
            ring = [xy(c) for c in poly[0]]
            if len(ring) > 2: dr.polygon(ring, fill=col, outline=(44, 96, 44))
            dr.line(ring + [ring[0]], fill=(44, 96, 44), width=3)
    im.save(out_png); return out_png


def mappamondo(coll, raggio, png, nome='Mappamondo'):
    """sfera con la texture equirettangolare calcolata dalle coordinate dell'oggetto: il punto (lon, lat) sta a
    (cos lat cos lon, cos lat sin lon, sin lat). Restituisce la radice (rotation_mode 'ZXY': z = -90 - lon, x = lat porta (lon, lat) davanti a -Y)."""
    r = empty(nome, (0, 0, 0), None, coll); r.rotation_mode = 'ZXY'
    bpy.ops.mesh.primitive_uv_sphere_add(segments=160, ring_count=80, radius=raggio, location=(0, 0, 0))
    s = bpy.context.active_object; s.name = nome + 'Sfera'
    for c in s.users_collection: c.objects.unlink(s)
    coll.objects.link(s); s.parent = r
    for p in s.data.polygons: p.use_smooth = True
    m = bpy.data.materials.new('P31_mondo'); m.use_nodes = True; nt = m.node_tree; N = nt.nodes; L = nt.links
    bsdf = N['Principled BSDF']; bsdf.inputs['Roughness'].default_value = 0.45
    tc = N.new('ShaderNodeTexCoord'); sp = N.new('ShaderNodeSeparateXYZ'); L.new(tc.outputs['Object'], sp.inputs[0])
    nv = N.new('ShaderNodeVectorMath'); nv.operation = 'NORMALIZE'; L.new(tc.outputs['Object'], nv.inputs[0]); sp2 = N.new('ShaderNodeSeparateXYZ'); L.new(nv.outputs[0], sp2.inputs[0])
    at = N.new('ShaderNodeMath'); at.operation = 'ARCTAN2'; L.new(sp2.outputs['Y'], at.inputs[0]); L.new(sp2.outputs['X'], at.inputs[1])
    u = N.new('ShaderNodeMath'); u.operation = 'MULTIPLY_ADD'; L.new(at.outputs[0], u.inputs[0]); u.inputs[1].default_value = 1 / (2 * PI); u.inputs[2].default_value = 0.5
    asn = N.new('ShaderNodeMath'); asn.operation = 'ARCSINE'; L.new(sp2.outputs['Z'], asn.inputs[0])
    v = N.new('ShaderNodeMath'); v.operation = 'MULTIPLY_ADD'; L.new(asn.outputs[0], v.inputs[0]); v.inputs[1].default_value = 1 / PI; v.inputs[2].default_value = 0.5
    cb = N.new('ShaderNodeCombineXYZ'); L.new(u.outputs[0], cb.inputs['X']); L.new(v.outputs[0], cb.inputs['Y'])
    img = N.new('ShaderNodeTexImage'); img.image = bpy.data.images.load(os.path.abspath(png)); img.extension = 'EXTEND'; img.interpolation = 'Cubic'
    L.new(cb.outputs[0], img.inputs['Vector']); L.new(img.outputs['Color'], bsdf.inputs['Base Color'])
    s.data.materials.append(m)
    # atmosfera: guscio azzurro trasparente appena piu' grande
    bpy.ops.mesh.primitive_uv_sphere_add(segments=96, ring_count=48, radius=raggio * 1.025, location=(0, 0, 0))
    a = bpy.context.active_object; a.name = nome + 'Aria'
    for c in a.users_collection: c.objects.unlink(a)
    coll.objects.link(a); a.parent = r
    for p in a.data.polygons: p.use_smooth = True
    ma = bpy.data.materials.new('P31_aria'); ma.use_nodes = True; na = ma.node_tree.nodes; la = ma.node_tree.links; na.clear()
    lw = na.new('ShaderNodeLayerWeight'); lw.inputs['Blend'].default_value = 0.12
    em = na.new('ShaderNodeEmission'); em.inputs['Color'].default_value = (0.45, 0.75, 1.0, 1); em.inputs['Strength'].default_value = 0.9
    tr = na.new('ShaderNodeBsdfTransparent'); mx = na.new('ShaderNodeMixShader'); out = na.new('ShaderNodeOutputMaterial')
    la.new(lw.outputs['Facing'], mx.inputs[0]); la.new(tr.outputs[0], mx.inputs[1]); la.new(em.outputs[0], mx.inputs[2]); la.new(mx.outputs[0], out.inputs['Surface'])
    try: ma.surface_render_method = 'BLENDED'
    except Exception: pass
    a.data.materials.append(ma)
    return r


def punto(lon, lat, r=1.0):
    lo, la = math.radians(lon), math.radians(lat)
    return Vector((math.cos(la) * math.cos(lo), math.cos(la) * math.sin(lo), math.sin(la))) * r


def rot_davanti(lon, lat):
    """rotazione (x, y, z) in ordine 'ZXY' che porta (lon, lat) davanti alla camera (verso -Y)"""
    return (math.radians(lat), 0.0, math.radians(-90.0 - lon))


def cielo_stellato(coll, centro, raggio=220.0, n=400, seme=9):
    rr = random.Random(seme)
    m = material('P31_spazio', (0.0, 0.0, 0.0), rough=1.0, emit=(0.01, 0.02, 0.06), emit_strength=1.0)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, radius=raggio, location=centro)
    o = bpy.context.active_object; o.name = 'Spazio'
    for c in o.users_collection: c.objects.unlink(o)
    coll.objects.link(o); o.data.materials.append(m)
    ms = material('P31_stella', (1, 1, 1), emit=(1.0, 0.97, 0.9), emit_strength=6.0)
    for k in range(n):
        v = Vector((rr.uniform(-1, 1), rr.uniform(-1, 1), rr.uniform(-1, 1))).normalized() * raggio * 0.95
        s = rr.uniform(0.15, 0.45); shape('Stella', 'sphere_lo', tuple(Vector(centro) + v), (s, s, s), (0, 0, 0), None, ms, coll)
    return o


def cartello2(coll, M, nome='Cartello2'):
    """cartello «DATEMI UN CALCIO» v2 (l'autore voleva un cartello migliore): cartone piu' grande con il bordo strappato,
    scritta nera da pennarello su due righe separate (niente righe che si sovrappongono), freccia verso il sedere, due strisce di scotch.
    Il fronte guarda +Y (si legge da dietro chi lo porta sulla schiena)."""
    r = empty(nome, (0, 0, 0), None, coll); r.rotation_mode = 'XYZ'
    box(nome + 'Cartone', (0, 0, 0), (0.5, 0.012, 0.36), M['cartone'], coll, r)
    rr = random.Random(4)
    for k in range(9):                                                         # bordo strappato
        x = -0.25 + 0.0625 * k; box(nome + 'Strappo', (x, 0.0, 0.18 + rr.uniform(0.0, 0.012)), (0.05, 0.013, 0.02), M['cartone'], coll, r, rot=(0, rr.uniform(-0.4, 0.4), 0))
    nero = material('P31_pennarello', (0.03, 0.03, 0.03), rough=0.6)
    for i, (riga, sz, z) in enumerate((('DATEMI', 0.11, 0.075), ('UN CALCIO', 0.085, -0.045))):
        _txt(coll, nome + 'Riga%d' % i, riga, sz, nero, (0, 0.009, z), rot=(PI / 2, 0, PI), parent=r, ext=0.002)
    box(nome + 'Freccia', (0.0, 0.009, -0.125), (0.025, 0.003, 0.06), nero, coll, r)
    shape(nome + 'Punta', 'cone', (0.0, 0.009, -0.165), (0.04, 0.004, 0.03), (0, PI, 0), r, nero, coll)
    for s_ in (-1, 1): box(nome + 'Scotch', (s_ * 0.2, 0.009, 0.16), (0.13, 0.004, 0.04), M['scotch'], coll, r, rot=(0, s_ * 0.6, 0))
    return r


def bandiera_usa_texture(out_png, W=1900, H=1000):
    from PIL import Image, ImageDraw
    im = Image.new('RGB', (W, H), (255, 255, 255)); d = ImageDraw.Draw(im)
    sh = H / 13.0
    for k in range(13):
        if k % 2 == 0: d.rectangle([0, k * sh, W, (k + 1) * sh], fill=(178, 34, 52))
    cw, chh = W * 0.4, sh * 7; d.rectangle([0, 0, cw, chh], fill=(60, 59, 110))
    def stella(cx, cy, R):
        pts = []
        for i in range(10):
            a = -PI / 2 + i * PI / 5; rr = R if i % 2 == 0 else R * 0.382; pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
        d.polygon(pts, fill=(255, 255, 255))
    for row in range(9):
        n = 6 if row % 2 == 0 else 5
        for c in range(n):
            x = cw / 12.0 * (2 * c + 1 + (row % 2)); y = chh / 10.0 * (row + 1); stella(x, y, sh * 0.31)
    im.save(out_png); return out_png


def bandiera_usa(coll, M, png, nome='BandieraUSA'):
    """bandiera degli Stati Uniti sull'asta (chiesta dall'autore per la satira, 21 novembre 2026): tela ondulata 1,4 x 0,74."""
    r = empty(nome, (0, 0, 0), None, coll); r.rotation_mode = 'XYZ'
    shape(nome + 'Asta', 'cyl:1:1', (0, 0, 1.6), (0.035, 0.035, 3.2), (0, 0, 0), r, M['cromo'], coll)
    shape(nome + 'Pomo', 'sphere', (0, 0, 3.24), (0.07, 0.07, 0.07), (0, 0, 0), r, M['oro'], coll)
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=40, y_subdivisions=20, size=1.0, location=(0, 0, 0))
    t = bpy.context.active_object; t.name = nome + 'Tela'
    for c in t.users_collection: c.objects.unlink(t)
    coll.objects.link(t); t.parent = r
    for v in t.data.vertices:
        u = v.co.x + 0.5; w = v.co.y + 0.5                                     # u lungo la tela (0 all'asta), w in altezza
        v.co.x, v.co.z, v.co.y = 0.04 + 1.4 * u, 2.45 + 0.74 * w - 0.08 * u * u, 0.07 * u * math.sin(u * 7.0 + w * 1.5)
    for p in t.data.polygons: p.use_smooth = True
    m = bpy.data.materials.new('P31_bandiera_usa'); m.use_nodes = True; nt = m.node_tree
    img = nt.nodes.new('ShaderNodeTexImage'); img.image = bpy.data.images.load(os.path.abspath(png))
    nt.links.new(img.outputs['Color'], nt.nodes['Principled BSDF'].inputs['Base Color']); nt.nodes['Principled BSDF'].inputs['Roughness'].default_value = 0.8
    t.data.materials.append(m)
    return r
