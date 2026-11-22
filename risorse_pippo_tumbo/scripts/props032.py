"""Oggetti del video 032 (copione n. 36, Francesco ci prova): Francesco il tostapane (T1, T2, T3), Vanessa la lavatrice (V1, V2),
il frigorifero palestrato (P1, P2). Fronte -Y, base a z = 0. Ogni builder restituisce un dict con root e le parti da animare."""
import math, bpy
from common import material, shape, empty
import set004
from set004 import obj
import props027

PI = math.pi


def mats032():
    M = props027.mats027()
    M['rosso'] = material('M32_rosso', (0.85, 0.08, 0.10), rough=0.25, coat=0.6)
    M['cromo'] = material('M32_cromo', (0.88, 0.89, 0.92), rough=0.12, metallic=1.0)
    M['crema'] = material('M32_crema', (0.95, 0.88, 0.70), rough=0.35, coat=0.4)
    M['menta'] = material('M32_menta', (0.55, 0.88, 0.78), rough=0.35, coat=0.4)
    M['rosa'] = material('M32_rosa', (1.0, 0.62, 0.78), rough=0.3, coat=0.5)
    M['bianco_el'] = material('M32_bianco_elettrodomestico', (0.94, 0.95, 0.96), rough=0.25, coat=0.4)
    M['nero_p'] = material('M32_plastica_nera', (0.04, 0.04, 0.05), rough=0.4)
    M['pane'] = material('M32_pane', (0.93, 0.78, 0.50), rough=0.9)
    M['crosta'] = material('M32_crosta', (0.62, 0.38, 0.16), rough=0.9)
    M['vetro'] = material('M32_oblo', (0.35, 0.65, 0.95), rough=0.05, coat=1.0)
    M['schiuma'] = material('M32_schiuma', (0.98, 0.98, 1.0), rough=0.8)
    M['oro'] = material('M32_oro', (1.0, 0.76, 0.25), rough=0.2, metallic=1.0)
    M['lente'] = material('M32_lente', (0.02, 0.02, 0.03), rough=0.05, coat=1.0)
    M['rossetto'] = material('M32_rossetto', (0.9, 0.05, 0.15), rough=0.3)
    M['muscolo'] = material('M32_muscolo', (0.94, 0.95, 0.96), rough=0.3, coat=0.4)
    return M


def rbox(nome, loc, dim, raggio, mat, coll, parent=None, seg=4):
    """scatola centrata in loc con gli spigoli arrotondati (modificatore Bevel)."""
    me = set004.box_c().copy(); me.name = nome + '_mesh'
    for v in me.vertices: v.co = (v.co.x * dim[0], v.co.y * dim[1], v.co.z * dim[2])
    o = obj(nome, me, loc, (1, 1, 1), mat, coll, parent=parent)
    m = o.modifiers.new('Tondo', 'BEVEL'); m.width = min(raggio, 0.49 * min(dim)); m.segments = seg; m.limit_method = 'NONE'
    o.data.polygons.foreach_set('use_smooth', [True] * len(o.data.polygons))
    return o


def _bbox(root):
    bpy.context.view_layer.update()
    pts = [(o.matrix_world @ __import__('mathutils').Vector(v)) for o in [root] + list(root.children_recursive) if o.type == 'MESH' for v in o.bound_box]
    return [min(p[i] for p in pts) for i in range(3)], [max(p[i] for p in pts) for i in range(3)]


def cartellino(coll, M, parent, loc, larg, font, testo='FRANCESCO', nome='Cartellino'):
    obj(nome, set004.box_c(), loc, (larg, 0.008, larg * 0.24), M['carta'], coll, parent=parent)
    if font is not None:
        import props023
        props023.testo(coll, nome + 'Scritta', testo, larg * 0.16, M['nero'], (loc[0], loc[1] - 0.006, loc[2] - larg * 0.015), parent=parent, font=font, estrudi=0.001)


# ------------------------------------------------------------------ Francesco, il tostapane (alto circa 0,32 m)
def francesco(coll, M, tipo='T1', A=None, font=None, nome='Francesco'):
    """T1 tostapane Kenney rosso con la faccina; T2 tostapane cartoon tondo rosso col pane che spunta; T3 tostapane rétro cromato.
    Restituisce root, corpo, leva (scende su Z), pane (sale su Z), e le parti della faccina."""
    R = {}
    r = R['root'] = empty(nome, (0, 0, 0), None, coll)
    c = R['corpo'] = empty(nome + 'Corpo', (0, 0, 0), r, coll)
    W, D, H = 0.36, 0.22, 0.26
    if tipo == 'T1':
        m = A.modello('kenney/furniture-kit/toaster', posizione=(0, 0, 0), altezza=H, collezione=coll, appoggia=True, nome=nome + 'Kenney')
        m.parent = c
        for o in [m] + list(m.children_recursive):
            if o.type == 'MESH':
                for s in o.material_slots:
                    if s.material and sum(s.material.diffuse_color[:3]) > 1.2: s.link = 'OBJECT'; s.material = M['rosso']
        lo, hi = _bbox(m); W, D, H = hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2]
        fy = lo[1] - 0.005
    else:
        mat = M['rosso'] if tipo == 'T2' else M['cromo']
        rbox(nome + 'Scocca', (0, 0, 0.03 + H / 2), (W, D, H), 0.06 if tipo == 'T2' else 0.035, mat, coll, parent=c)
        for sx in (-1, 1):   # piedini
            for sy in (-1, 1):
                shape(nome + 'Piede', 'sphere', (sx * W * 0.36, sy * D * 0.32, 0.02), scale=(0.025, 0.025, 0.02), parent=c, mat=M['nero_p'], coll=coll)
        if tipo == 'T3':   # fascia crema e manopola da rétro
            rbox(nome + 'Fascia', (0, 0, 0.03 + H * 0.22), (W * 1.01, D * 1.01, H * 0.16), 0.02, M['crema'], coll, parent=c)
        H += 0.03; fy = -D / 2 - 0.005
    # le due fessure col pane
    p = R['pane'] = empty(nome + 'Pane', (0, 0, H - 0.06), c, coll)
    for k, x in enumerate((-W * 0.2, W * 0.2)):
        obj(nome + 'Fessura', set004.box_c(), (x, 0, H + 0.002), (0.035, D * 0.62, 0.006), M['nero_p'], coll, parent=c)
        if tipo != 'T1':
            rbox(nome + 'Fetta', (x, 0, 0.09), (0.025, D * 0.55, 0.14), 0.01, M['pane'], coll, parent=p)
            rbox(nome + 'Crosta', (x, 0, 0.16), (0.027, D * 0.57, 0.02), 0.009, M['crosta'], coll, parent=p)
    # la leva sul fianco destro
    l = R['leva'] = empty(nome + 'Leva', (W / 2 + 0.01, 0, H * 0.75), c, coll)
    obj(nome + 'Guida', set004.box_c(), (W / 2 + 0.002, 0, H * 0.5), (0.006, 0.02, H * 0.55), M['nero_p'], coll, parent=c)
    rbox(nome + 'Pomello', (0.025, 0, 0), (0.05, 0.04, 0.025), 0.01, M['nero_p'], coll, parent=l)
    # faccina e cartellino sul davanti
    R.update(props027.faccina(coll, M, c, fy, H * 0.68, 1.0, nome + 'F'))
    cartellino(coll, M, c, (0, fy - 0.004, H * 0.25), W * 0.62, font, nome=nome + 'Cart')
    return R


# ------------------------------------------------------------------ Vanessa, la lavatrice (alta circa 0,75 m)
def vanessa(coll, M, tipo='V1', A=None, nome='Vanessa'):
    """V1 lavatrice Kenney bianca con fiocco, ciglia e rossetto; V2 lavatrice cartoon rosa, tonda, con l'oblò grande.
    Restituisce root, corpo, cestello (gira su Y: centrifuga), e le parti della faccina."""
    R = {}
    r = R['root'] = empty(nome, (0, 0, 0), None, coll)
    c = R['corpo'] = empty(nome + 'Corpo', (0, 0, 0), r, coll)
    if tipo == 'V1':
        m = A.modello('kenney/furniture-kit/washer', posizione=(0, 0, 0), altezza=0.75, collezione=coll, appoggia=True, nome=nome + 'Kenney')
        m.parent = c
        lo, hi = _bbox(m); W, D, H = hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2]; fy = lo[1]
        oz, orad = H * 0.45, W * 0.3
    else:
        W, D, H = 0.62, 0.55, 0.75
        rbox(nome + 'Scocca', (0, 0, H / 2), (W, D, H), 0.09, M['rosa'], coll, parent=c)
        rbox(nome + 'Pannello', (0, -D / 2 + 0.01, H * 0.88), (W * 0.86, 0.03, H * 0.14), 0.02, M['bianco_el'], coll, parent=c)
        fy = -D / 2; oz, orad = H * 0.42, W * 0.36
    # oblò: anello cromato, vetro, cestello con la schiuma che gira
    shape(nome + 'Anello', 'cyl:1:1', (0, fy - 0.012, oz), scale=(orad * 1.12, orad * 1.12, 0.02), rot=(PI / 2, 0, 0), parent=c, mat=M['cromo'], coll=coll)
    cs = R['cestello'] = empty(nome + 'Cestello', (0, fy - 0.02, oz), c, coll)
    shape(nome + 'Acqua', 'cyl:1:1', (0, 0, 0), scale=(orad, orad, 0.01), rot=(PI / 2, 0, 0), parent=cs, mat=M['vetro'], coll=coll)
    for k in range(5):
        a = 2 * PI * k / 5
        shape(nome + 'Bolla', 'sphere', (orad * 0.55 * math.cos(a), -0.012, orad * 0.55 * math.sin(a)), scale=(orad * 0.22, 0.01, orad * 0.18), parent=cs, mat=M['schiuma'], coll=coll)
    # faccina in alto, sopra l'oblò, grande; ciglia, rossetto e fiocco
    s = 2.0
    zf = oz + orad * 1.12 + 0.09
    F = props027.faccina(coll, M, c, fy - 0.01, zf, s, nome + 'F')
    for sx in (-1, 1):
        for j in (-1, 0, 1):
            obj(nome + 'Ciglio', set004.box_c(), (sx * 0.07 * s + j * 0.03, fy - 0.03, zf + 0.06 * s), (0.008, 0.008, 0.045), M['nero'], coll, rot=(-0.6, j * 0.35, 0), parent=c)
    F['mouth'].material_slots[0].material = M['rossetto']
    for sx in (-1, 1):
        shape(nome + 'Fiocco', 'sphere', (sx * 0.09, 0, H + 0.04), scale=(0.1, 0.04, 0.065), rot=(0, sx * 0.3, 0), parent=c, mat=M['fiocco'], coll=coll)
    shape(nome + 'FioccoNodo', 'sphere', (0, 0, H + 0.04), scale=(0.04, 0.04, 0.04), parent=c, mat=M['fiocco'], coll=coll)
    R.update(F)
    return R


# ------------------------------------------------------------------ il frigorifero palestrato (alto circa 1,7 m)
def braccio(coll, M, parent, sx, spalla, nome):
    """braccio enorme a forma di bicipite gonfio: spalla, bicipite, avambraccio e pugno. Restituisce l'empty della spalla."""
    b = empty(nome, spalla, parent, coll)
    shape(nome + 'Spalla', 'sphere', (0, 0, 0), scale=(0.16, 0.15, 0.16), parent=b, mat=M['muscolo'], coll=coll)
    shape(nome + 'Bicipite', 'sphere', (sx * 0.2, 0, -0.05), scale=(0.2, 0.15, 0.15), parent=b, mat=M['muscolo'], coll=coll)
    shape(nome + 'Avambraccio', 'cap:0.09:0.2', (sx * 0.36, 0, 0.12), rot=(0, sx * 0.15, 0), parent=b, mat=M['muscolo'], coll=coll)
    shape(nome + 'Pugno', 'sphere', (sx * 0.37, -0.01, 0.32), scale=(0.11, 0.1, 0.1), parent=b, mat=M['muscolo'], coll=coll)
    return b


def frigorifero(coll, M, tipo='P1', A=None, nome='Frigo'):
    """P1 frigorifero Kenney con le braccia enormi in posa da bicipite, occhiali da sole e catena d'oro;
    P2 frigorifero cartoon cromato e tondo, stessa posa. Restituisce root, corpo, bracci L/R."""
    R = {}
    r = R['root'] = empty(nome, (0, 0, 0), None, coll)
    c = R['corpo'] = empty(nome + 'Corpo', (0, 0, 0), r, coll)
    if tipo == 'P1':
        m = A.modello('kenney/furniture-kit/kitchenFridge', posizione=(0, 0, 0), altezza=1.7, collezione=coll, appoggia=True, nome=nome + 'Kenney')
        m.parent = c
        lo, hi = _bbox(m); W, D, H = hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2]; fy = lo[1]
    else:
        W, D, H = 0.75, 0.7, 1.7
        rbox(nome + 'Scocca', (0, 0, H / 2), (W, D, H), 0.12, M['cromo'], coll, parent=c)
        obj(nome + 'Fuga', set004.box_c(), (0, -D / 2 - 0.002, H * 0.62), (W * 0.92, 0.01, 0.012), M['nero_p'], coll, parent=c)
        rbox(nome + 'Maniglia', (W * 0.36, -D / 2 - 0.03, H * 0.45), (0.03, 0.04, 0.35), 0.012, M['nero_p'], coll, parent=c)
        fy = -D / 2
    for sx, nm in ((-1, 'L'), (1, 'R')):
        R['braccio' + nm] = braccio(coll, M, c, sx, (sx * (W / 2 + 0.05), 0, H * 0.7), nome + 'Braccio' + nm)
    zf = H * 0.84
    F = props027.faccina(coll, M, c, fy - 0.01, zf, 1.8, nome + 'F')
    for sx in (-1, 1):   # occhiali da sole sopra gli occhi
        rbox(nome + 'Lente', (sx * 0.13, fy - 0.07, zf + 0.01), (0.2, 0.02, 0.11), 0.03, M['lente'], coll, parent=c)
    obj(nome + 'Ponte', set004.box_c(), (0, fy - 0.07, zf + 0.04), (0.08, 0.015, 0.015), M['nero_p'], coll, parent=c)
    for k in range(13):   # catena d'oro sul petto
        a = PI * (0.15 + 0.7 * k / 12)
        shape(nome + 'Anello', 'sphere', (0.22 * math.cos(a), fy - 0.02, H * 0.66 - 0.16 * math.sin(a)), scale=(0.025, 0.012, 0.018), parent=c, mat=M['oro'], coll=coll)
    R.update(F)
    return R


# ------------------------------------------------------------------ oggetti di scena
def tavolino(coll, nome='Tavolino', h=0.72):
    """tavolino da giardino di legno, piano 0,9 x 0,7 a quota h. Origine a terra."""
    r = empty(nome, (0, 0, 0), None, coll); leg = material('M32_legno', (0.62, 0.40, 0.22), rough=0.7)
    rbox(nome + 'Piano', (0, 0, h - 0.025), (0.9, 0.7, 0.05), 0.015, leg, coll, parent=r)
    for sx in (-1, 1):
        for sy in (-1, 1):
            obj(nome + 'Gamba', set004.box_c(), (sx * 0.38, sy * 0.28, (h - 0.05) / 2), (0.05, 0.05, h - 0.05), leg, coll, parent=r)
    return r


def spunta(coll, mat, parent, loc, s=1.0, nome='Spunta'):
    """segno di spunta (V) fatto di due listelli, sul piano XZ (faccia verso -Y)."""
    obj(nome + 'A', set004.box_c(), (loc[0] - 0.018 * s, loc[1], loc[2] - 0.008 * s), (0.012 * s, 0.006, 0.04 * s), mat, coll, rot=(0, 0.75, 0), parent=parent)
    obj(nome + 'B', set004.box_c(), (loc[0] + 0.012 * s, loc[1], loc[2] + 0.008 * s), (0.012 * s, 0.006, 0.075 * s), mat, coll, rot=(0, -0.6, 0), parent=parent)


def fumetto_chat(coll, M, font, testo='CIAO BELLA', nome='Chat'):
    """nuvoletta del messaggio (bianca, angoli tondi) con il testo e le due spunte, faccia verso -Y, centro all'origine.
    Restituisce root e spunte (empty: grigie -> blu scambiando la visibilita' di 'grigie' e 'blu')."""
    import props023
    R = {}
    r = R['root'] = empty(nome, (0, 0, 0), None, coll)
    verde = material('M32_chat', (0.86, 0.98, 0.78), rough=0.4)
    rbox(nome + 'Fondo', (0, 0, 0), (0.62, 0.03, 0.2), 0.06, verde, coll, parent=r)
    shape(nome + 'Coda', 'cone', (0.24, 0, -0.1), scale=(0.05, 0.015, 0.09), rot=(PI, 0.5, 0), parent=r, mat=verde, coll=coll)
    props023.testo(coll, nome + 'Testo', testo, 0.085, M['nero'], (-0.05, -0.02, 0.0), parent=r, font=font, estrudi=0.002)
    grigio = material('M32_spunta_grigia', (0.55, 0.58, 0.6), rough=0.5); blu = material('M32_spunta_blu', (0.1, 0.55, 1.0), rough=0.4, emit=(0.1, 0.5, 1.0), emit_strength=1.5)
    for k_, mt in (('grigie', grigio), ('blu', blu)):
        e = R[k_] = empty(nome + k_, (0, 0, 0), r, coll)
        spunta(coll, mt, e, (0.21, -0.022, -0.05), 0.8, nome + k_ + '1'); spunta(coll, mt, e, (0.245, -0.022, -0.05), 0.8, nome + k_ + '2')
    return R


def fantasmino(coll, nome='Fantasma'):
    """fantasmino bianco da cartone (alto 0,5 m) con gli occhi neri e la bocca a O. Faccia verso -Y, origine al centro."""
    r = empty(nome, (0, 0, 0), None, coll); b = material('M32_fantasma', (0.97, 0.98, 1.0), rough=0.5, emit=(0.8, 0.85, 1.0), emit_strength=0.6)
    n = material('M32_fantasma_occhi', (0.02, 0.02, 0.03), rough=0.3)
    shape(nome + 'Testa', 'sphere', (0, 0, 0.1), scale=(0.17, 0.15, 0.2), parent=r, mat=b, coll=coll)
    shape(nome + 'Corpo', 'cyl:1:1', (0, 0, -0.06), scale=(0.17, 0.15, 0.16), parent=r, mat=b, coll=coll)
    for k in range(5):
        shape(nome + 'Lembo', 'sphere', (-0.13 + 0.065 * k, 0, -0.15), scale=(0.04, 0.04, 0.06), parent=r, mat=b, coll=coll)
    for sx in (-1, 1): shape(nome + 'Occhio', 'sphere', (sx * 0.055, -0.13, 0.14), scale=(0.025, 0.02, 0.04), parent=r, mat=n, coll=coll)
    shape(nome + 'Bocca', 'sphere', (0, -0.14, 0.05), scale=(0.035, 0.02, 0.045), parent=r, mat=n, coll=coll)
    for sx in (-1, 1): shape(nome + 'Braccio', 'sphere', (sx * 0.19, 0, 0.0), scale=(0.07, 0.035, 0.03), rot=(0, sx * 0.5, 0), parent=r, mat=b, coll=coll)
    return r


def vocale(coll, M, font, lung=14.0, nome='Vocale'):
    """messaggio vocale lunghissimo: barra verde chiara lunga 'lung' lungo +X locale, alta 0,32 m, faccia verso -Y locale,
    col tasto play all'inizio, l'onda della voce e la durata 10:00 in fondo. Origine all'inizio della barra.
    Restituisce root e scala (empty da scalare su X per farla allungare)."""
    import props023, random as _r
    R = {}
    r = R['root'] = empty(nome, (0, 0, 0), None, coll)
    s = R['scala'] = empty(nome + 'Scala', (0, 0, 0), r, coll)
    verde = material('M32_vocale', (0.45, 0.88, 0.4), rough=0.4); onda = material('M32_onda', (0.05, 0.3, 0.12), rough=0.4)
    rbox(nome + 'Fondo', (lung / 2, 0, 0), (lung, 0.04, 0.42), 0.15, verde, coll, parent=s)
    shape(nome + 'Play', 'cone', (0.2, -0.03, 0), scale=(0.07, 0.01, 0.12), rot=(0, -PI / 2, 0), parent=s, mat=onda, coll=coll)
    rn = _r.Random(32)
    x = 0.4
    while x < lung - 0.9:
        h = 0.04 + 0.18 * abs(math.sin(x * 2.3)) * rn.uniform(0.5, 1.0)
        obj(nome + 'Onda', set004.box_c(), (x, -0.025, 0), (0.035, 0.01, h), onda, coll, parent=s); x += 0.07
    props023.testo(coll, nome + 'Durata', '10:00', 0.13, M['nero'], (lung - 0.45, -0.03, -0.02), parent=s, font=font, estrudi=0.003)
    return R


def rosa(coll, nera=False, nome='Rosa'):
    """rosa col gambo, alta 0,32 m, origine alla base del gambo. nera=True: bruciata."""
    r = empty(nome, (0, 0, 0), None, coll)
    g = material('M32_gambo_nero' if nera else 'M32_gambo', (0.05, 0.05, 0.04) if nera else (0.15, 0.5, 0.15), rough=0.6)
    p = material('M32_petali_neri' if nera else 'M32_petali', (0.04, 0.03, 0.03) if nera else (0.85, 0.04, 0.1), rough=0.5 if not nera else 0.95)
    shape(nome + 'Gambo', 'cyl:1:1', (0, 0, 0.12), scale=(0.008, 0.008, 0.24), parent=r, mat=g, coll=coll)
    shape(nome + 'Foglia', 'sphere', (0.03, 0, 0.12), scale=(0.035, 0.008, 0.015), rot=(0, -0.5, 0), parent=r, mat=g, coll=coll)
    for k in range(7):
        a = 2 * PI * k / 7
        shape(nome + 'Petalo', 'sphere', (0.022 * math.cos(a), 0.022 * math.sin(a), 0.27), scale=(0.035, 0.035, 0.045), parent=r, mat=p, coll=coll)
    shape(nome + 'Cuore', 'sphere', (0, 0, 0.29), scale=(0.03, 0.03, 0.04), parent=r, mat=p, coll=coll)
    return r


def antenna_wifi(coll, nome='Wifi'):
    """palo con l'antenna e i tre archi del wifi (emissivi, da accendere uno dopo l'altro). Alto 2,2 m, archi verso -Y.
    Restituisce root e archi (lista dei materiali da accendere: input Emission Strength)."""
    import props024
    R = {}
    r = R['root'] = empty(nome, (0, 0, 0), None, coll)
    pm = material('M32_palo', (0.6, 0.6, 0.62), rough=0.3, metallic=1.0)
    shape(nome + 'Palo', 'cyl:1:1', (0, 0, 1.0), scale=(0.035, 0.035, 2.0), parent=r, mat=pm, coll=coll)
    shape(nome + 'Pallino', 'sphere', (0, 0, 2.05), scale=(0.07, 0.07, 0.07), parent=r, mat=pm, coll=coll)
    R['archi'] = []
    for k in range(3):
        m = material('M32_arco%d' % k, (0.3, 0.8, 1.0), rough=0.4, emit=(0.3, 0.85, 1.0), emit_strength=0.0)
        a = props024.anello(nome + 'Arco%d' % k, 0.18 + 0.14 * k, 0.025, m, coll, seg=48, segr=6)
        a.parent = r; a.location = (0, 0, 2.05); a.rotation_euler = (PI / 2, 0, 0)
        R['archi'].append(m.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'])
    return R


def telefono(coll, nome='Telefono'):
    """telefono grande (0,13 x 0,26 m) con lo schermo acceso verso -Y locale; nello schermo una foto rosa di Vanessa.
    Restituisce root, schermo (materiale) e foto (root della foto, da far scorrere su Z)."""
    R = {}
    r = R['root'] = empty(nome, (0, 0, 0), None, coll)
    rbox(nome + 'Corpo', (0, 0, 0), (0.13, 0.012, 0.26), 0.015, material('M32_telefono', (0.04, 0.04, 0.05), rough=0.3), coll, parent=r)
    sc = material('M32_schermo', (0.15, 0.18, 0.25), rough=0.2, emit=(0.5, 0.65, 1.0), emit_strength=0.35)
    obj(nome + 'Schermo', set004.box_c(), (0, -0.007, 0), (0.118, 0.002, 0.242), sc, coll, parent=r)
    f = R['foto'] = empty(nome + 'Foto', (0, -0.009, 0), r, coll)
    for k, z in enumerate((0.0, -0.085)):
        obj(nome + 'Foto%d' % k, set004.box_c(), (0, 0, z), (0.1, 0.002, 0.07), material('M32_foto%d' % k, (1.0, 0.55, 0.72) if k == 0 else (0.85, 0.75, 1.0), rough=0.5, emit=(1.0, 0.5, 0.7) if k == 0 else (0.8, 0.7, 1.0), emit_strength=0.45), coll, parent=f)
        shape(nome + 'Obl%d' % k, 'cyl:1:1', (0, -0.002, z - 0.008), scale=(0.022, 0.022, 0.002), rot=(PI / 2, 0, 0), parent=f, mat=material('M32_foto_oblo', (0.4, 0.7, 1.0), rough=0.3, emit=(0.4, 0.7, 1.0), emit_strength=0.45), coll=coll)
    R['schermo'] = sc
    return R


def cornice_storia(coll, cam, font, nome='Storia', lens=30.0):
    """cornice da «storia» incollata alla camera: barre di avanzamento in alto, pallino col nome VANESSA, bordi scuri ai lati.
    Calcolata per un sensore di 36 mm e la lente 'lens', a 0,5 m dalla camera (formato 9:16)."""
    import props023
    R = {}
    d = 0.5; hw = d * 18.0 / lens * (1080 / 1920) * 1.0; hh = d * 18.0 / lens * 1.0
    # in un sensore verticale la larghezza del sensore (36 mm) segue il lato lungo: altezza = 36 mm, larghezza = 36 * 9/16
    r = R['root'] = empty(nome, (0, 0, -d), cam, coll)
    bianco = material('M32_storia_barra', (1, 1, 1), rough=0.5, emit=(1, 1, 1), emit_strength=2.0)
    grigio = material('M32_storia_barra_vuota', (0.5, 0.5, 0.5), rough=0.5, emit=(0.6, 0.6, 0.6), emit_strength=0.8)
    for k in range(3):
        x0 = -hw * 0.92 + k * hw * 0.62
        obj(nome + 'Vuota', set004.box_c(), (x0 + hw * 0.28, hh * 0.93, 0), (hw * 0.56, hh * 0.014, 0.0005), grigio, coll, parent=r)
    R['barra'] = obj(nome + 'Piena', set004.box_c(), (-hw * 0.92 + hw * 0.62 * 1, hh * 0.93, 0.0003), (hw * 0.56, hh * 0.015, 0.0005), bianco, coll, parent=r)
    rosa_ = material('M32_storia_avatar', (1.0, 0.62, 0.78), rough=0.5, emit=(1.0, 0.55, 0.75), emit_strength=1.5)
    shape(nome + 'Avatar', 'cyl:1:1', (-hw * 0.82, hh * 0.86, 0), scale=(hh * 0.035, hh * 0.035, 0.0005), rot=(PI / 2, 0, 0), parent=r, mat=rosa_, coll=coll)
    t = props023.testo(coll, nome + 'Nome', 'VANESSA', hh * 0.055, bianco, (-hw * 0.5, hh * 0.86, 0), rot=(0, 0, 0), parent=r, font=font, estrudi=0.0)
    return R


def cielo_marte(coll, x0, nome='CieloMarte'):
    """cupola di cielo color salmone (emissiva) attorno a Marte."""
    m = material('M32_cielo_marte', (0.85, 0.55, 0.4), rough=1.0, emit=(0.9, 0.55, 0.38), emit_strength=0.9)
    nt = m.node_tree; b = nt.nodes['Principled BSDF']
    ge = nt.nodes.new('ShaderNodeNewGeometry'); sp = nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(ge.outputs['Normal'], sp.inputs[0])
    rp = nt.nodes.new('ShaderNodeValToRGB'); rp.color_ramp.elements[0].position = 0.0; rp.color_ramp.elements[0].color = (0.98, 0.7, 0.5, 1)
    rp.color_ramp.elements[1].position = 0.5; rp.color_ramp.elements[1].color = (0.55, 0.3, 0.25, 1)
    mp = nt.nodes.new('ShaderNodeMapRange'); mp.inputs['From Min'].default_value = 0.0; mp.inputs['From Max'].default_value = -1.0
    nt.links.new(sp.outputs['Z'], mp.inputs['Value']); nt.links.new(mp.outputs['Result'], rp.inputs['Fac'])
    nt.links.new(rp.outputs['Color'], b.inputs['Emission Color']); nt.links.new(rp.outputs['Color'], b.inputs['Base Color'])
    return shape(nome, 'sphere', (x0, 100.0, 0.0), scale=(900, 900, 600), mat=m, coll=coll)


def terra(coll, pos, r, nome='Terra'):
    """la Terra piccola nel cielo di Marte: sfera blu con due macchie verdi."""
    o = empty(nome, pos, None, coll)
    shape(nome + 'Mare', 'sphere', (0, 0, 0), scale=(r, r, r), parent=o, mat=material('M32_terra_mare', (0.15, 0.4, 0.95), rough=0.5, emit=(0.15, 0.4, 0.95), emit_strength=1.5), coll=coll)
    for (dx, dz, s_) in ((-0.3, 0.25, 0.45), (0.35, -0.2, 0.4)):
        shape(nome + 'Isola', 'sphere', (dx * r, -0.75 * r, dz * r), scale=(s_ * r, 0.3 * r, s_ * 0.7 * r), parent=o, mat=material('M32_terra_verde', (0.2, 0.7, 0.25), rough=0.6, emit=(0.2, 0.7, 0.25), emit_strength=1.2), coll=coll)
    return o
