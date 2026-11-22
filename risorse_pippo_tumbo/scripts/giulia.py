"""Giulia, la moglie di Gualtiero: grossa, sgraziata, naso lungo a penzoloni che dondola.
Stesso stile di Gualtiero (capsule e sfere). Fronte -Y, piedi a z = 0, alta 2,2 m con i bigodini, larga 1,8 m.
L'autore ha scelto l'aspetto A (17 novembre 2026): e' quello predefinito. B e C restano come travestimenti.

    import giulia
    GM = giulia.mats_giulia()
    J = giulia.giulia(chc, GM, stile='A')      # 'A' bigodini e vestaglia a fiori, 'B' permanente e leopardato,
                                              # 'C' crocchia, occhiali e grembiule
    giulia.giex(J, frame, brow=0.6, mouth=0.4, lid=0.3, look=(0, 0), naso=0.5)
    giulia.mattarello(chc, GM, J)              # mattarello nella mano destra

Dizionario restituito: root, head, belly, shoulderL/R, hipL/R, browL/R, pupilL/R, lidL/R, mouth, lip, tooth, nose.
Le braccia a riposo sono aperte di 25 gradi perche' la pancia e' piu' larga delle spalle."""
import math, bpy
from common import material, shape, empty, shared_mesh
import set004
from set004 import obj, cyl, ball_

PI = math.pi
STILI = ('A', 'B', 'C')


def _fantasia(name, base, punti, scala=7.0, soglia=0.32, rough=0.75, punti2=None):
    """Stoffa a pallini o macchie: colore di base con punti di un altro colore (ed eventualmente di un terzo)."""
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = material(name, base, rough=rough)
    nt = m.node_tree
    b = nt.nodes['Principled BSDF']
    tc = nt.nodes.new('ShaderNodeTexCoord')
    ultimo = None
    for i, (col, sc, so) in enumerate([(punti, scala, soglia)] + ([(punti2, scala * 0.63, soglia * 0.8)] if punti2 else [])):
        vor = nt.nodes.new('ShaderNodeTexVoronoi')
        vor.inputs['Scale'].default_value = sc
        nt.links.new(tc.outputs['Object'], vor.inputs['Vector'])
        meno = nt.nodes.new('ShaderNodeMath')
        meno.operation = 'LESS_THAN'
        meno.inputs[1].default_value = so
        nt.links.new(vor.outputs['Distance'], meno.inputs[0])
        mix = nt.nodes.new('ShaderNodeMix')
        mix.data_type = 'RGBA'
        nt.links.new(meno.outputs[0], mix.inputs[0])
        if ultimo is None:
            mix.inputs[6].default_value = (*base, 1)
        else:
            nt.links.new(ultimo.outputs[2], mix.inputs[6])
        mix.inputs[7].default_value = (*col, 1)
        ultimo = mix
    nt.links.new(ultimo.outputs[2], b.inputs['Base Color'])
    return m


def mats_giulia():
    c = lambda n, col, **k: material('GI_' + n, col, **k)
    M = {}
    M['skin'] = c('skin', (0.93, 0.50, 0.40), rough=0.6)
    M['nose'] = c('nose', (0.86, 0.17, 0.17), rough=0.45)
    M['wart'] = c('wart', (0.45, 0.24, 0.16), rough=0.7)
    M['occhiaia'] = c('occhiaia', (0.66, 0.32, 0.42), rough=0.6)
    # Colori pieni di proposito: sotto il sole forte del look del kit i pastello diventano quasi bianchi.
    M['white'] = c('white', (1, 1, 1), rough=0.4)
    M['black'] = c('black', (0.03, 0.03, 0.04), rough=0.5)
    M['brow'] = c('brow', (0.16, 0.11, 0.09), rough=0.9)
    M['mouth'] = c('mouth', (0.28, 0.04, 0.07), rough=0.5)
    M['tooth'] = c('tooth', (0.98, 0.93, 0.70), rough=0.4)
    M['gold'] = c('gold', (1.0, 0.72, 0.15), rough=0.25, metallic=0.9)
    M['pearl'] = c('pearl', (0.97, 0.95, 0.90), rough=0.2, spec=0.9)
    M['stocking'] = c('stocking', (0.60, 0.42, 0.28), rough=0.8)
    M['wood'] = c('wood', (0.82, 0.60, 0.34), rough=0.6)
    M['pink'] = c('pink', (0.95, 0.16, 0.48), rough=0.5)
    M['azure'] = c('azure', (0.08, 0.50, 0.95), rough=0.5)
    M['glass'] = c('glass', (0.75, 0.90, 1.0), rough=0.05, spec=1.0)
    # A: vestaglia a fiori, bigodini
    M['vestito_A'] = _fantasia('GI_vestA', (0.42, 0.22, 0.78), (1.0, 0.72, 0.03), 7.0, 0.30, punti2=(0.95, 0.12, 0.45))
    M['capelli_A'] = c('hairA', (0.40, 0.33, 0.50), rough=0.9)
    M['ombretto_A'] = c('lidA', (0.10, 0.42, 0.95), rough=0.5)
    M['labbra_A'] = c('lipA', (0.85, 0.03, 0.38), rough=0.35)
    M['ciabatta_A'] = c('slipA', (0.95, 0.20, 0.52), rough=0.9)
    # B: leopardato, permanente rossa
    M['vestito_B'] = _fantasia('GI_vestB', (0.85, 0.48, 0.08), (0.10, 0.05, 0.02), 6.0, 0.36, punti2=(0.38, 0.17, 0.04))
    M['capelli_B'] = c('hairB', (0.85, 0.18, 0.02), rough=0.85)
    M['ombretto_B'] = c('lidB', (0.02, 0.62, 0.55), rough=0.5)
    M['labbra_B'] = c('lipB', (0.90, 0.05, 0.10), rough=0.3)
    M['ciabatta_B'] = c('slipB', (0.88, 0.08, 0.12), rough=0.4)
    # C: vestito a pallini, grembiule, golf verde
    M['vestito_C'] = _fantasia('GI_vestC', (0.04, 0.07, 0.30), (0.97, 0.97, 0.97), 8.0, 0.24)
    M['capelli_C'] = c('hairC', (0.48, 0.48, 0.52), rough=0.9)
    M['ombretto_C'] = c('lidC', (0.50, 0.22, 0.75), rough=0.5)
    M['labbra_C'] = c('lipC', (0.80, 0.22, 0.30), rough=0.4)
    M['ciabatta_C'] = c('slipC', (0.50, 0.30, 0.16), rough=0.8)
    M['grembiule'] = c('apron', (0.97, 0.97, 0.94), rough=0.8)
    M['golf'] = c('cardigan', (0.08, 0.38, 0.14), rough=0.9)
    M['occhiali'] = c('frames', (0.75, 0.10, 0.25), rough=0.3)
    return M


def giulia(coll, M, stile='A'):
    """Costruisce Giulia. stile: 'A' | 'B' | 'C' (vedi in testa al file)."""
    assert stile in STILI, stile
    EX = 0.125   # distanza degli occhi dal centro
    R = {}
    r = R['root'] = empty('Giulia', (0, 0, 0), None, coll)
    S = lambda *a, **k: shape(*a, coll=coll, **k)
    box = set004.box_c()
    ves, cap, lab = M['vestito_' + stile], M['capelli_' + stile], M['labbra_' + stile]
    manica = M['golf'] if stile == 'C' else ves

    # ---- corpo a pera
    R['belly'] = S('GI_Pancia', 'sphere', (0, -0.03, 0.86), scale=(0.62, 0.55, 0.50), parent=r, mat=ves)
    S('GI_Petto', 'sphere', (0, -0.02, 1.24), scale=(0.47, 0.40, 0.30), parent=r, mat=manica)
    S('GI_Sedere', 'sphere', (0, 0.17, 0.74), scale=(0.53, 0.42, 0.38), parent=r, mat=ves)
    S('GI_Gonna', 'sphere', (0, 0.0, 0.57), scale=(0.60, 0.54, 0.22), parent=r, mat=ves)
    S('GI_Orlo', 'cyl:1:1', (0, 0.0, 0.455), scale=(0.555, 0.50, 0.035), parent=r, mat=M['white'])
    S('GI_Colletto', 'sphere', (0, -0.04, 1.50), scale=(0.27, 0.24, 0.07), parent=r, mat=M['white'] if stile != 'B' else ves)
    if stile == 'A':
        for z in (1.13, 0.95, 0.77):  # bottoni della vestaglia, appoggiati sulla pancia
            y = -0.03 - 0.55 * math.sqrt(1 - ((z - 0.86) / 0.50) ** 2)
            S('GI_Bottone', 'sphere', (0, y - 0.004, z), scale=(0.035, 0.02, 0.035), parent=r, mat=M['white'])
    if stile == 'B':
        for k in range(11):  # collana di perle
            a = PI * (0.08 + 0.84 * k / 10)
            S('GI_Perla', 'sphere', (0.31 * math.cos(a), -0.05 - 0.30 * math.sin(a), 1.47 - 0.06 * math.sin(a)), scale=(0.035,) * 3, parent=r, mat=M['pearl'])
    if stile == 'C':
        S('GI_Grembiule', 'sphere', (0, -0.085, 0.80), scale=(0.53, 0.565, 0.47), parent=r, mat=M['grembiule'])
        S('GI_Pettorina', 'sphere', (0, -0.075, 1.20), scale=(0.30, 0.385, 0.28), parent=r, mat=M['grembiule'])
        obj('GI_Tasca', box, (0, -0.655, 0.80), (0.26, 0.02, 0.17), M['vestito_C'], coll, rot=(-0.05, 0, 0), parent=r)

    # ---- testa
    h = R['head'] = empty('GI_Head', (0, -0.02, 1.76), r, coll)
    S('GI_Cranio', 'sphere', (0, 0, 0), scale=(0.34, 0.31, 0.31), parent=h, mat=M['skin'])
    S('GI_Mento', 'sphere', (0, -0.06, -0.31), scale=(0.28, 0.25, 0.13), parent=h, mat=M['skin'])      # doppio mento
    for sx, nm in ((-1, 'L'), (1, 'R')):
        S('GI_Guancia', 'sphere', (sx * 0.215, -0.09, -0.12), scale=(0.15, 0.16, 0.16), parent=h, mat=M['skin'])
        S('GI_Orecchio', 'sphere', (sx * 0.335, 0.0, -0.02), scale=(0.05, 0.06, 0.08), parent=h, mat=M['skin'])
        S('GI_Orecchino', 'sphere', (sx * 0.35, -0.01, -0.14), scale=(0.05, 0.05, 0.05), parent=h, mat=M['pearl'] if stile == 'C' else M['gold'])
        S('GI_Occhio', 'sphere', (sx * EX, -0.262, 0.085), scale=(0.085, 0.048, 0.090), parent=h, mat=M['white'])
        S('GI_Occhiaia', 'sphere', (sx * EX, -0.262, 0.035), scale=(0.088, 0.046, 0.075), parent=h, mat=M['occhiaia'])
        R['pupil' + nm] = S('GI_Pupilla', 'sphere', (sx * EX, -0.305, 0.078), scale=(0.034, 0.018, 0.040), parent=h, mat=M['black'])
        # palpebra pesante con l'ombretto: scende con giex(lid=)
        lid = R['lid' + nm] = S('GI_Palpebra', 'sphere', (sx * EX, -0.262, 0.13), scale=(0.093, 0.057, 0.097), parent=h, mat=M['ombretto_' + stile])
        for j in (-1, 0, 1):
            obj('GI_Ciglia', box, (j * 0.42, -0.93, -0.50), (0.10, 0.12, 0.55), M['black'], coll, rot=(1.15, 0, -j * 0.45), parent=lid)
        R['brow' + nm] = obj('GI_Sopracciglio', box, (sx * EX, -0.278, 0.225), (0.22, 0.05, 0.062), M['brow'], coll, rot=(0, -sx * 0.25, sx * 0.40), parent=h)
    obj('GI_Monociglio', box, (0, -0.300, 0.205), (0.09, 0.045, 0.05), M['brow'], coll, parent=h)

    # naso lungo a penzoloni: tre pezzi su un perno, cosi' dondola (giex naso=)
    n = R['nose'] = empty('GI_Naso', (0, -0.295, 0.075), h, coll)
    S('GI_NasoRadice', 'sphere', (0, -0.030, -0.030), scale=(0.070, 0.080, 0.095), parent=n, mat=M['skin'])
    S('GI_NasoMezzo', 'sphere', (0, -0.085, -0.130), scale=(0.074, 0.086, 0.120), parent=n, mat=M['skin'])
    S('GI_NasoPunta', 'sphere', (0, -0.120, -0.245), scale=(0.090, 0.095, 0.105), parent=n, mat=M['nose'])
    for sx in (-1, 1):
        S('GI_Narice', 'sphere', (sx * 0.036, -0.135, -0.336), scale=(0.022, 0.022, 0.014), parent=n, mat=M['mouth'])
    S('GI_Porro', 'sphere', (0.070, -0.155, -0.200), scale=(0.030, 0.030, 0.030), parent=n, mat=M['wart'])
    obj('GI_PeloPorro', box, (0.098, -0.170, -0.175), (0.007, 0.007, 0.075), M['black'], coll, rot=(0, 0.9, 0), parent=n)

    # bocca: labbra con il rossetto, un dente storto
    S('GI_LabbroSu', 'sphere', (0, -0.305, -0.175), scale=(0.215, 0.060, 0.040), parent=h, mat=lab)
    R['mouth'] = S('GI_Bocca', 'sphere', (0, -0.305, -0.212), scale=(0.170, 0.045, 0.020), parent=h, mat=M['mouth'])
    R['lip'] = S('GI_LabbroGiu', 'sphere', (0, -0.300, -0.248), scale=(0.200, 0.066, 0.050), parent=h, mat=lab)
    R['tooth'] = obj('GI_Dente', box, (0.125, -0.350, -0.214), (0.046, 0.022, 0.062), M['tooth'], coll, rot=(0, 0.25, 0), parent=h)
    S('GI_Neo', 'sphere', (-0.235, -0.250, -0.110), scale=(0.028, 0.028, 0.028), parent=h, mat=M['wart'])
    obj('GI_PeloNeo', box, (-0.255, -0.275, -0.100), (0.007, 0.007, 0.06), M['black'], coll, rot=(1.0, -0.5, 0), parent=h)

    # ---- capelli
    if stile == 'A':      # bigodini rosa e azzurri sopra i capelli sbiaditi
        S('GI_Capelli', 'sphere', (0, 0.055, 0.075), scale=(0.352, 0.318, 0.305), parent=h, mat=cap)
        big = [(-0.20, -0.16, 0.285), (0.0, -0.20, 0.335), (0.20, -0.16, 0.285), (-0.13, 0.02, 0.385), (0.13, 0.02, 0.385),
               (-0.20, 0.20, 0.29), (0.0, 0.23, 0.33), (0.20, 0.20, 0.29)]
        for i, p in enumerate(big):
            S('GI_Bigodino', 'cyl:0.058:0.17', p, rot=(0, PI / 2, 0.25 * (-1 if p[0] < 0 else (1 if p[0] > 0 else 0))), parent=h, mat=M['pink'] if i % 2 == 0 else M['azure'])
    elif stile == 'B':    # permanente rossa a torre
        S('GI_Capelli', 'sphere', (0, 0.07, 0.14), scale=(0.40, 0.36, 0.33), parent=h, mat=cap)
        S('GI_Torre1', 'sphere', (0, 0.03, 0.42), scale=(0.31, 0.29, 0.25), parent=h, mat=cap)
        S('GI_Torre2', 'sphere', (0, 0.02, 0.63), scale=(0.23, 0.22, 0.20), parent=h, mat=cap)
        S('GI_Torre3', 'sphere', (0, 0.01, 0.79), scale=(0.14, 0.14, 0.13), parent=h, mat=cap)
        for k in range(9):   # riccioli sulla fronte
            a = PI * (0.06 + 0.88 * k / 8)
            S('GI_Ricciolo', 'sphere', (0.345 * math.cos(a), 0.02 - 0.30 * math.sin(a), 0.235 + 0.035 * math.sin(a)), scale=(0.10, 0.10, 0.10), parent=h, mat=cap)
    else:                 # crocchia grigia con lo spillone, occhiali a gatto
        S('GI_Capelli', 'sphere', (0, 0.055, 0.075), scale=(0.352, 0.318, 0.305), parent=h, mat=cap)
        S('GI_Crocchia', 'sphere', (0, 0.20, 0.34), scale=(0.15, 0.15, 0.14), parent=h, mat=cap)
        S('GI_Spillone', 'cyl:0.012:0.42', (0, 0.20, 0.36), rot=(0, 1.1, 0.4), parent=h, mat=M['wood'])
        for sx in (-1, 1):
            g = empty('GI_Lente', (sx * 0.115, -0.335, 0.085), h, coll)
            obj('GI_LenteVetro', box, (0, 0.004, 0), (0.17, 0.006, 0.12), M['glass'], coll, parent=g)
            obj('GI_MontSu', box, (0, 0, 0.065), (0.20, 0.022, 0.028), M['occhiali'], coll, rot=(0, -sx * 0.18, 0), parent=g)
            obj('GI_MontGiu', box, (0, 0, -0.062), (0.17, 0.02, 0.018), M['occhiali'], coll, parent=g)
            obj('GI_MontLato', box, (sx * 0.092, 0, 0.005), (0.018, 0.02, 0.13), M['occhiali'], coll, parent=g)
            obj('GI_MontNaso', box, (-sx * 0.088, 0, 0.0), (0.018, 0.02, 0.12), M['occhiali'], coll, parent=g)
            obj('GI_Punta', box, (sx * 0.118, 0, 0.088), (0.06, 0.022, 0.03), M['occhiali'], coll, rot=(0, -sx * 0.6, 0), parent=g)
            obj('GI_Stanghetta', box, (sx * 0.235, 0.165, 0.02), (0.016, 0.34, 0.016), M['occhiali'], coll, parent=h)

    # ---- braccia e gambe
    for nm, sx in (('L', -1), ('R', 1)):
        sh = R['shoulder' + nm] = empty('GI_shoulder' + nm, (sx * 0.47, 0, 1.36), r, coll)
        sh.rotation_euler = (0, -sx * 0.44, 0)
        S('GI_Manica', 'cap:0.155:0.10', (0, 0, -0.10), parent=sh, mat=manica)
        S('GI_Braccio', 'cap:0.125:0.34', (0, 0, -0.30), parent=sh, mat=manica if stile == 'C' else M['skin'])
        S('GI_Mano', 'sphere', (0, 0, -0.62), scale=(0.12, 0.12, 0.12), parent=sh, mat=M['skin'])
        hp = R['hip' + nm] = empty('GI_hip' + nm, (sx * 0.23, 0.02, 0.50), r, coll)
        S('GI_Gamba', 'cap:0.12:0.20', (0, 0, -0.22), parent=hp, mat=M['skin'])
        S('GI_Calza', 'sphere', (0, 0, -0.36), scale=(0.14, 0.14, 0.055), parent=hp, mat=M['stocking'])   # calza arrotolata
        obj('GI_Ciabatta', box, (0, -0.07, -0.465), (0.21, 0.36, 0.07), M['ciabatta_' + stile], coll, parent=hp)
        S('GI_PuntaCiabatta', 'sphere', (0, -0.16, -0.43), scale=(0.115, 0.14, 0.075), parent=hp, mat=M['ciabatta_' + stile])
        if stile == 'A':
            S('GI_Pompon', 'sphere', (0, -0.20, -0.35), scale=(0.065,) * 3, parent=hp, mat=M['white'])
    giex(R, None)
    return R


def giex(R, f, brow=0.4, mouth=0.15, lid=0.45, look=(0, 0), naso=0.0):
    """Faccia di Giulia al fotogramma f (f=None: imposta senza chiavi).
    brow > 0 arrabbiata, < 0 spaventata; mouth 0..1; lid 0 = occhi spalancati, 1 = chiusi;
    look = (x, y) direzione dello sguardo; naso -1..1 = il naso dondola a sinistra o a destra."""
    def k(o, prop):
        if f is not None:
            o.keyframe_insert(prop, frame=f)
    for sx, nm in ((-1, 'L'), (1, 'R')):
        b = R['brow' + nm]
        b.rotation_euler = (0, -sx * brow * 0.55, sx * 0.40)      # girato per seguire la curva della fronte
        b.location = (sx * 0.125, -0.278, 0.225 + (0.04 if brow < 0 else -0.018 * brow))
        k(b, 'rotation_euler'); k(b, 'location')
        p = R['pupil' + nm]
        p.location = (sx * 0.125 + look[0] * 0.032, -0.305, 0.078 + look[1] * 0.030)
        k(p, 'location')
        l = R['lid' + nm]
        l.location = (sx * 0.125, -0.262, 0.085 + 0.10 * (1 - lid))
        k(l, 'location')
    m = R['mouth']
    m.scale = (0.170 + 0.02 * mouth, 0.045, 0.020 + 0.065 * mouth)
    m.location = (0, -0.305, -0.212 - 0.04 * mouth)
    k(m, 'scale'); k(m, 'location')
    lp = R['lip']
    lp.location = (0, -0.300, -0.248 - 0.085 * mouth)
    k(lp, 'location')
    n = R['nose']
    n.rotation_euler = (0, naso * 0.55, 0)
    k(n, 'rotation_euler')


def mattarello(coll, M, R, lato='R'):
    """Mattarello stretto nella mano (figlio della spalla): punta in avanti, verso -Y."""
    g = empty('GI_Mattarello', (0, -0.05, -0.62), R['shoulder' + lato], coll)
    cyl('GI_MattCorpo', 0.062, 0.52, (0, -0.20, 0), M['wood'], coll, rot=(PI / 2, 0, 0), parent=g)
    for s in (-1, 1):
        cyl('GI_MattManico', 0.026, 0.14, (0, -0.20 + s * 0.33, 0), M['wood'], coll, rot=(PI / 2, 0, 0), parent=g)
    return g
