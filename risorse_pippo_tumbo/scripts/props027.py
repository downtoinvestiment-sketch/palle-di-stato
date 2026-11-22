"""Oggetti del video 027 (copione n. 26, Francesco il cactus): Francesco in tre versioni, Francesca gigante, la mongolfiera.
Fronte -Y, base a z = 0."""
import math, bpy
from common import material, shape, empty
import set004
from set004 import obj

PI = math.pi


def mats027():
    M = {}
    M['cactus'] = material('M27_cactus', (0.22, 0.58, 0.20), rough=0.6)
    M['cactus2'] = material('M27_cactus_chiaro', (0.36, 0.70, 0.30), rough=0.6)
    M['spina'] = material('M27_spina', (0.98, 0.95, 0.82), rough=0.4)
    M['vaso'] = material('M27_terracotta', (0.78, 0.36, 0.18), rough=0.8)
    M['terra'] = material('M27_terra', (0.25, 0.16, 0.09), rough=0.95)
    M['bianco'] = material('M27_bianco', (0.97, 0.96, 0.93), rough=0.2, coat=0.5)
    M['nero'] = material('M27_nero', (0.02, 0.02, 0.025), rough=0.2)
    M['guance'] = material('M27_guance', (1.0, 0.5, 0.55), rough=0.6)
    M['bocca'] = material('M27_bocca', (0.3, 0.05, 0.06), rough=0.6)
    M['fiocco'] = material('M27_fiocco', (1.0, 0.42, 0.68), rough=0.4, coat=0.3)
    M['fiore'] = material('M27_fiore', (1.0, 0.30, 0.45), rough=0.4)
    M['carta'] = material('M27_cartellino', (0.98, 0.96, 0.88), rough=0.8)
    M['corda'] = material('M27_corda', (0.55, 0.42, 0.26), rough=0.9)
    M['bruciatore'] = material('M27_bruciatore', (0.5, 0.5, 0.52), rough=0.3, metallic=1.0)
    M['fiamma'] = material('M27_fiamma', (1.0, 0.6, 0.1), rough=0.5, emit=(1.0, 0.55, 0.1), emit_strength=8.0)
    for k, c in enumerate([(0.95, 0.15, 0.15), (1.0, 0.6, 0.05), (1.0, 0.9, 0.15), (0.2, 0.75, 0.25), (0.15, 0.45, 0.95), (0.6, 0.25, 0.85)]):
        M['spicchio%d' % k] = material('M27_spicchio%d' % k, c, rough=0.5)
    M['rossob'] = material('M27_rosso_pallone', (0.9, 0.1, 0.12), rough=0.5)
    M['biancob'] = material('M27_bianco_pallone', (0.96, 0.95, 0.92), rough=0.5)
    return M


def faccina(coll, M, parent, y, z, s=1.0, nome='Faccia'):
    """occhietti con le pupille e boccuccia sorridente, sul davanti (-Y) di un oggetto. Restituisce dict eyeL/R, pupilL/R, mouth."""
    R = {}
    for sx, nm in ((-1, 'L'), (1, 'R')):
        e = R['eye' + nm] = empty(nome + 'Occhio' + nm, (sx * 0.07 * s, y, z), parent, coll)
        shape(nome + 'Bulbo', 'sphere', (0, 0, 0), scale=(0.05 * s, 0.035 * s, 0.06 * s), parent=e, mat=M['bianco'], coll=coll)
        p = R['pupil' + nm] = empty(nome + 'Pup' + nm, (0, 0, 0), e, coll)
        shape(nome + 'Pupilla', 'sphere', (0, -0.03 * s, 0), scale=(0.024 * s, 0.01 * s, 0.03 * s), parent=p, mat=M['nero'], coll=coll)
        shape(nome + 'Luce', 'sphere', (0.008 * s, -0.04 * s, 0.012 * s), scale=(0.007 * s, 0.004 * s, 0.007 * s), parent=p, mat=M['bianco'], coll=coll)
        shape(nome + 'Guancia', 'sphere', (sx * 0.11 * s, y + 0.005, z - 0.07 * s), scale=(0.03 * s, 0.01 * s, 0.02 * s), parent=parent, mat=M['guance'], coll=coll)
    R['mouth'] = shape(nome + 'Bocca', 'sphere', (0, y + 0.005, z - 0.08 * s), scale=(0.035 * s, 0.01 * s, 0.015 * s), parent=parent, mat=M['bocca'], coll=coll)
    return R


def _spine(coll, M, parent, cx, cy, cz, rx, ry, rz, n, nome, lung=0.05, seme=0):
    """spine sulla superficie di un ellissoide (punte verso l'esterno)."""
    import random
    rn = random.Random(seme); g = (1 + 5 ** 0.5) / 2
    for i in range(n):
        zz = 1 - 2 * (i + 0.5) / n; r_ = math.sqrt(max(0.0, 1 - zz * zz)); a = 2 * PI * i / g
        nx, ny, nz = r_ * math.cos(a), r_ * math.sin(a), zz
        if nz < -0.7: continue
        p = (cx + rx * nx, cy + ry * ny, cz + rz * nz)
        o = shape(nome, 'cone', p, scale=(0.006, 0.006, lung * rn.uniform(0.7, 1.2)), parent=parent, mat=M['spina'], coll=coll)
        d = __import__('mathutils').Vector((nx / rx, ny / ry, nz / rz)).normalized()
        o.rotation_mode = 'QUATERNION'; o.rotation_quaternion = __import__('mathutils').Vector((0, 0, 1)).rotation_difference(d)


def vaso(coll, M, parent, r=0.18, h=0.22, nome='Vaso', cartellino=None, font=None):
    shape(nome, 'cyl:1:1', (0, 0, h / 2), scale=(r, r, h / 2), parent=parent, mat=M['vaso'], coll=coll)
    shape(nome + 'Bordo', 'cyl:1:1', (0, 0, h - 0.02), scale=(r * 1.12, r * 1.12, 0.035), parent=parent, mat=M['vaso'], coll=coll)
    shape(nome + 'Terra', 'cyl:1:1', (0, 0, h - 0.005), scale=(r * 0.98, r * 0.98, 0.012), parent=parent, mat=M['terra'], coll=coll)
    if cartellino:
        obj(nome + 'Cartellino', set004.box_c(), (0, -r - 0.012, h * 0.45), (r * 1.2, 0.01, h * 0.38), M['carta'], coll, parent=parent)
        if font is not None:
            import props023
            props023.testo(coll, nome + 'Scritta', cartellino, 0.05 * r / 0.18, M['nero'], (0, -r - 0.02, h * 0.45 - 0.02 * r / 0.18), parent=parent, font=font, estrudi=0.002)


def francesco(coll, M, tipo='F1', A=None, font=None, nome='Francesco'):
    """Francesco nel vaso col cartellino. F1 cactus cartoon tondo con le braccine; F2 cactus a colonna con le braccia a candelabro;
    F3 cactus a palle (fico d'India) con un fiore in testa. Restituisce dict root, corpo (scala per farlo crescere), faccia..."""
    R = {}
    r = R['root'] = empty(nome, (0, 0, 0), None, coll)
    vaso(coll, M, r, cartellino='FRANCESCO', font=font, nome=nome + 'Vaso')
    c = R['corpo'] = empty(nome + 'Corpo', (0, 0, 0.21), r, coll)
    if tipo == 'F1':
        shape(nome + 'Fusto', 'sphere', (0, 0, 0.26), scale=(0.17, 0.16, 0.28), parent=c, mat=M['cactus'], coll=coll)
        for sx in (-1, 1):
            b = empty(nome + 'Braccio', (sx * 0.15, 0, 0.26), c, coll)
            shape(nome + 'BraccioOriz', 'sphere', (sx * 0.06, 0, 0), scale=(0.08, 0.06, 0.06), parent=b, mat=M['cactus'], coll=coll)
            shape(nome + 'BraccioSu', 'sphere', (sx * 0.12, 0, 0.08), scale=(0.055, 0.055, 0.1), parent=b, mat=M['cactus'], coll=coll)
            R['braccio' + ('L' if sx < 0 else 'R')] = b
        _spine(coll, M, c, 0, 0, 0.26, 0.17, 0.16, 0.28, 46, nome + 'Spina', seme=1)
        R.update(faccina(coll, M, c, -0.15, 0.33, 1.0, nome + 'F'))
    elif tipo == 'F2':
        shape(nome + 'Fusto', 'cap:0.12:0.62', (0, 0, 0.33), parent=c, mat=M['cactus'], coll=coll)
        for sx, zb, hb in ((-1, 0.30, 0.22), (1, 0.38, 0.18)):
            shape(nome + 'Gomito', 'sphere', (sx * 0.15, 0, zb), scale=(0.09, 0.07, 0.07), parent=c, mat=M['cactus'], coll=coll)
            shape(nome + 'Ramo', 'cap:0.065:' + str(hb), (sx * 0.22, 0, zb + hb / 2), parent=c, mat=M['cactus'], coll=coll)
        for k in range(8):   # costolature
            a = 2 * PI * k / 8
            shape(nome + 'Costola', 'cap:0.02:0.55', (0.115 * math.cos(a), 0.115 * math.sin(a), 0.33), parent=c, mat=M['cactus2'], coll=coll)
        _spine(coll, M, c, 0, 0, 0.33, 0.13, 0.13, 0.34, 40, nome + 'Spina', seme=2)
        R.update(faccina(coll, M, c, -0.125, 0.45, 0.9, nome + 'F'))
    else:
        shape(nome + 'Pala1', 'sphere', (0, 0, 0.18), scale=(0.16, 0.06, 0.19), parent=c, mat=M['cactus'], coll=coll)
        shape(nome + 'Pala2', 'sphere', (-0.14, 0.01, 0.40), scale=(0.11, 0.05, 0.13), rot=(0, 0.5, 0), parent=c, mat=M['cactus'], coll=coll)
        shape(nome + 'Pala3', 'sphere', (0.13, 0.01, 0.42), scale=(0.10, 0.05, 0.12), rot=(0, -0.5, 0), parent=c, mat=M['cactus'], coll=coll)
        for k in range(5):
            a = 2 * PI * k / 5
            shape(nome + 'Petalo', 'sphere', (-0.14 + 0.035 * math.cos(a), 0.0, 0.55 + 0.035 * math.sin(a)), scale=(0.035, 0.02, 0.035), parent=c, mat=M['fiore'], coll=coll)
        _spine(coll, M, c, 0, 0, 0.18, 0.16, 0.06, 0.19, 30, nome + 'Spina', seme=3)
        R.update(faccina(coll, M, c, -0.055, 0.22, 0.9, nome + 'F'))
    return R


def francesca(coll, M, altezza=60.0, nome='Francesca'):
    """Francesca: cactussa altissima a colonna, col fiocco rosa, le ciglia e il rossetto. Alta 'altezza' metri (base a z = 0)."""
    R = {}
    r = R['root'] = empty(nome, (0, 0, 0), None, coll)
    k_ = altezza / 1.0
    s = empty(nome + 'Scala', (0, 0, 0), r, coll); s.scale = (k_, k_, k_)
    shape(nome + 'Fusto', 'cap:0.12:0.95', (0, 0, 0.5), parent=s, mat=M['cactus2'], coll=coll)
    for sx, zb, hb in ((-1, 0.42, 0.28), (1, 0.55, 0.22)):
        shape(nome + 'Gomito', 'sphere', (sx * 0.15, 0, zb), scale=(0.09, 0.07, 0.07), parent=s, mat=M['cactus2'], coll=coll)
        shape(nome + 'Ramo', 'cap:0.065:' + str(hb), (sx * 0.22, 0, zb + hb / 2), parent=s, mat=M['cactus2'], coll=coll)
    _spine(coll, M, s, 0, 0, 0.5, 0.13, 0.13, 0.5, 70, nome + 'Spina', lung=0.03, seme=4)
    F = faccina(coll, M, s, -0.115, 0.82, 1.0, nome + 'F')
    for sx, nm in ((-1, 'L'), (1, 'R')):   # ciglia lunghe
        for j in (-1, 0, 1):
            obj(nome + 'Ciglio', set004.box_c(), (sx * 0.07 + j * 0.018, -0.15, 0.885), (0.006, 0.006, 0.035), M['nero'], coll, rot=(-0.6, j * 0.3, 0), parent=s)
    F['mouth'].material_slots[0].material = material('M27_rossetto', (0.9, 0.05, 0.15), rough=0.3)
    for sx in (-1, 1):   # il fiocco rosa in testa
        shape(nome + 'Fiocco', 'sphere', (sx * 0.06, 0, 1.07), scale=(0.06, 0.025, 0.04), rot=(0, sx * 0.3, 0), parent=s, mat=M['fiocco'], coll=coll)
    shape(nome + 'FioccoNodo', 'sphere', (0, 0, 1.07), scale=(0.025, 0.025, 0.025), parent=s, mat=M['fiocco'], coll=coll)
    R.update(F)
    return R


def mongolfiera(coll, M, tipo='M1', nome='Mongolfiera'):
    """mongolfiera alta circa 9 m: pallone a spicchi (M1 arcobaleno, M2 rosso e bianco), corde, bruciatore con la fiamma, cesta di vimini.
    La cesta (1,4 x 1,4 x 1,0 m) sta a z 0..1; restituisce dict root, pallone, fiamma, cesta."""
    R = {}
    r = R['root'] = empty(nome, (0, 0, 0), None, coll)
    vim = material('M27_vimini', (0.62, 0.45, 0.22), rough=0.85)
    c = R['cesta'] = obj(nome + 'Cesta', set004.box_c(), (0, 0, 0.5), (1.4, 1.4, 1.0), vim, coll, parent=r)
    obj(nome + 'Bordo', set004.box_c(), (0, 0, 1.02), (1.5, 1.5, 0.08), material('M27_cuoio', (0.35, 0.2, 0.1), rough=0.6), coll, parent=r)
    p = R['pallone'] = empty(nome + 'Pallone', (0, 0, 5.6), r, coll)
    n = 12
    for k in range(n):
        a = 2 * PI * k / n
        m = M['spicchio%d' % (k % 6)] if tipo == 'M1' else (M['rossob'] if k % 2 else M['biancob'])
        o = shape(nome + 'Spicchio', 'sphere', (0.0, 0.0, 0.0), scale=(1.2, 3.0, 3.4), rot=(0, 0, a), parent=p, mat=m, coll=coll)
        o.location = (1.85 * math.cos(a), 1.85 * math.sin(a), 0)
    shape(nome + 'Cupola', 'sphere', (0, 0, 0.4), scale=(3.0, 3.0, 3.1), parent=p, mat=M['spicchio2'] if tipo == 'M1' else M['rossob'], coll=coll)
    shape(nome + 'Gola', 'cone', (0, 0, -3.1), scale=(1.1, 1.1, 1.0), rot=(PI, 0, 0), parent=p, mat=M['spicchio4'] if tipo == 'M1' else M['biancob'], coll=coll)
    for sx in (-1, 1):
        for sy in (-1, 1):
            o = shape(nome + 'Corda', 'cyl:1:1', (sx * 0.85, sy * 0.85, 1.85), scale=(0.015, 0.015, 0.9), rot=(-sy * 0.2, sx * 0.2, 0), parent=r, mat=M['corda'], coll=coll)
    shape(nome + 'Bruciatore', 'cyl:1:1', (0, 0, 2.3), scale=(0.25, 0.25, 0.12), parent=r, mat=M['bruciatore'], coll=coll)
    R['fiamma'] = shape(nome + 'Fiamma', 'cone', (0, 0, 2.75), scale=(0.16, 0.16, 0.4), parent=r, mat=M['fiamma'], coll=coll)
    return R


# ======================= altri pezzi del video 027 =======================
import random
from mathutils import Vector


def cravatta(coll, body, nome='Cravatta'):
    """cravatta rossa a pois sul petto di Pippo (coordinate del busto di pippo.py: torso raggio 0,24, centro a z 0,36)."""
    m = material('M27_cravatta', (0.85, 0.06, 0.10), rough=0.4)
    R = {}
    R['nodo'] = shape(nome + 'Nodo', 'sphere', (0, -0.228, 0.70), scale=(0.045, 0.03, 0.04), parent=body, mat=m, coll=coll)
    R['lama'] = shape(nome + 'Lama', 'sphere', (0, -0.245, 0.50), scale=(0.055, 0.018, 0.17), rot=(0.12, 0, 0), parent=body, mat=m, coll=coll)
    for k, (x, z) in enumerate(((-0.02, 0.58), (0.02, 0.50), (-0.015, 0.42), (0.015, 0.36))):
        shape(nome + 'Pois', 'sphere', (x, -0.262, z), scale=(0.01, 0.004, 0.01), parent=body, mat=material('M27_pois', (1, 1, 1), rough=0.5), coll=coll)
    return R


def mazzo_fiori(coll, nome='Mazzo'):
    """mazzo di fiori (gambi verso il basso, origine all'impugnatura)."""
    O = empty(nome, (0, 0, 0), None, coll)
    shape(nome + 'Carta', 'cone', (0, 0, 0.08), scale=(0.09, 0.09, 0.16), parent=O, mat=material('M27_carta_fiori', (0.95, 0.9, 0.97), rough=0.7), coll=coll)
    cols = [(1.0, 0.25, 0.35), (1.0, 0.85, 0.2), (0.95, 0.45, 0.85), (1.0, 0.55, 0.2)]
    rn = random.Random(7)
    for k in range(7):
        a = 2 * math.pi * k / 7
        shape(nome + 'Fiore', 'sphere', (0.06 * math.cos(a), 0.06 * math.sin(a), 0.26 + rn.uniform(-0.02, 0.03)), scale=(0.045,) * 3, parent=O, mat=material('M27_fiore%d' % (k % 4), cols[k % 4], rough=0.5), coll=coll)
    return O


def mantellina(coll, M, nome='Mantellina'):
    """mantellina da parrucchiere a righe (un cono aperto verso il basso). Origine al collo."""
    m = material('M27_mantellina', (0.45, 0.75, 0.95), rough=0.5)
    O = empty(nome, (0, 0, 0), None, coll)
    shape(nome, 'cone', (0, 0, -0.14), scale=(0.30, 0.30, 0.20), parent=O, mat=m, coll=coll)
    shape(nome + 'Collo', 'cyl:1:1', (0, 0, 0.0), scale=(0.17, 0.16, 0.02), parent=O, mat=material('M27_bianco_m', (1, 1, 1), rough=0.5), coll=coll)
    return O


def negozio(coll, x0, font, nome='Negozio'):
    """il parrucchiere: stanza 6 x 5 x 3 m attorno a (x0, 0); muro di fondo a y = 2,5 con lo specchio; vetrina a sinistra (x = x0 - 3)
    col manifesto VOLI IN MONGOLFIERA; porta a destra. Restituisce dict root, poltrona (radice del modello)."""
    import props023
    R = {}
    O = R['root'] = empty(nome, (0, 0, 0), None, coll)   # i pezzi hanno gia' le coordinate del mondo
    box = set004.box_c()
    pav = material('M27_pavimento', (0.95, 0.95, 0.95), rough=0.35)
    nero = material('M27_scacco', (0.08, 0.08, 0.09), rough=0.35)
    obj(nome + 'Pavimento', box, (x0, 0, -0.05), (6.4, 6.0, 0.1), pav, coll, parent=O)
    for i in range(-3, 3):
        for j in range(-3, 3):
            if (i + j) % 2: obj(nome + 'Scacco', box, (x0 + i + 0.5, j + 0.5, 0.002), (1.0, 1.0, 0.005), nero, coll, parent=O)
    muro = material('M27_muro', (0.55, 0.80, 0.82), rough=0.8)
    obj(nome + 'MuroFondo', box, (x0, 2.55, 1.5), (6.4, 0.1, 3.0), muro, coll, parent=O)
    obj(nome + 'MuroDx', box, (x0 + 3.15, 0, 1.5), (0.1, 6.0, 3.0), muro, coll, parent=O)
    obj(nome + 'MuroSxBasso', box, (x0 - 3.15, 0, 0.35), (0.1, 6.0, 0.7), muro, coll, parent=O)
    obj(nome + 'MuroSxAlto', box, (x0 - 3.15, 0, 2.75), (0.1, 6.0, 0.5), muro, coll, parent=O)
    obj(nome + 'Vetro', box, (x0 - 3.15, 0, 1.6), (0.02, 6.0, 1.8), material('M27_vetro', (0.75, 0.9, 1.0), rough=0.05), coll, parent=O)
    obj(nome + 'Soffitto', box, (x0, 0, 3.05), (6.4, 6.0, 0.1), material('M27_soffitto', (0.97, 0.96, 0.92), rough=0.9), coll, parent=O)
    # manifesto sul muro di fondo, a sinistra dello specchio
    obj(nome + 'Manifesto', box, (x0 - 1.9, 2.49, 1.7), (1.0, 0.02, 1.3), material('M27_manifesto', (1.0, 0.8, 0.35), rough=0.7), coll, parent=O)
    for k, t in enumerate(('VOLI IN', 'MONGOLFIERA', 'NEL DESERTO')):
        props023.testo(coll, nome + 'Scritta', t, 0.11, material('M27_scritta', (0.6, 0.1, 0.1), rough=0.6), (x0 - 1.9, 2.475, 2.1 - 0.17 * k - 0.05), parent=O, font=font, estrudi=0.002)
    for k in range(6):   # una mongolfierina disegnata
        a = 2 * math.pi * k / 6
        shape(nome + 'Disegno', 'sphere', (x0 - 1.9 + 0.12 * math.cos(a) * 0.0 + (k - 2.5) * 0.06, 2.475, 1.35), scale=(0.035, 0.005, 0.16), parent=O, mat=material('M27_disegno%d' % k, [(0.95, 0.15, 0.15), (1, 0.6, 0.05), (1, 0.9, 0.15), (0.2, 0.75, 0.25), (0.15, 0.45, 0.95), (0.6, 0.25, 0.85)][k], rough=0.5), coll=coll)
    obj(nome + 'Specchio', box, (x0, 2.48, 1.55), (1.3, 0.03, 1.2), material('M27_specchio', (0.85, 0.9, 0.95), rough=0.03, metallic=1.0), coll, parent=O)
    obj(nome + 'Cornice', box, (x0, 2.49, 1.55), (1.45, 0.03, 1.35), material('M27_cornice', (0.75, 0.55, 0.2), rough=0.4, metallic=0.6), coll, parent=O)
    obj(nome + 'Mensola', box, (x0, 2.35, 0.95), (1.6, 0.3, 0.06), material('M27_mensola', (0.97, 0.97, 0.97), rough=0.4), coll, parent=O)
    for k, c in enumerate([(0.2, 0.5, 0.95), (0.95, 0.3, 0.5), (0.3, 0.85, 0.5)]):
        shape(nome + 'Flacone', 'cyl:1:1', (x0 - 0.5 + 0.35 * k, 2.35, 1.08), scale=(0.05, 0.05, 0.08), parent=O, mat=material('M27_flacone%d' % k, c, rough=0.3), coll=coll)
    # palo da barbiere sul muro destro
    shape(nome + 'Palo', 'cyl:1:1', (x0 + 3.0, 1.5, 1.6), scale=(0.08, 0.08, 0.5), parent=O, mat=material('M27_palo', (0.95, 0.95, 0.95), rough=0.3), coll=coll)
    for k in range(4):
        o = shape(nome + 'PaloRiga', 'cyl:1:1', (x0 + 3.0, 1.5, 1.25 + 0.22 * k), scale=(0.082, 0.082, 0.05), rot=(0.4, 0, 0), parent=O, mat=material('M27_palo_rosso', (0.85, 0.08, 0.1), rough=0.3), coll=coll)
    return R


def spina_volante(coll, M, nome='SpinaVolante', lung=0.12):
    """una spina da lanciare (punta verso +Z locale)."""
    return shape(nome, 'cone', (0, 0, 0), scale=(0.012, 0.012, lung), mat=M['spina'], coll=coll)


def goccia(coll, nome='Pipi'):
    return shape(nome, 'sphere', (0, 0, -90), scale=(0.025,) * 3, mat=material('M27_pipi', (1.0, 0.85, 0.15), rough=0.1, coat=0.8), coll=coll)


def mat_luna():
    m = bpy.data.materials.get('M27_luna')
    if m: return m
    m = material('M27_luna', (0.62, 0.62, 0.64), rough=0.9); nt = m.node_tree; b = nt.nodes['Principled BSDF']
    nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 0.6; nz.inputs['Detail'].default_value = 8
    vo = nt.nodes.new('ShaderNodeTexVoronoi'); vo.inputs['Scale'].default_value = 0.35
    rp = nt.nodes.new('ShaderNodeValToRGB'); rp.color_ramp.elements[0].color = (0.32, 0.32, 0.34, 1); rp.color_ramp.elements[1].color = (0.82, 0.82, 0.84, 1)
    nt.links.new(nz.outputs['Fac'], rp.inputs['Fac']); nt.links.new(rp.outputs['Color'], b.inputs['Base Color'])
    bm = nt.nodes.new('ShaderNodeBump'); bm.inputs['Strength'].default_value = 0.6
    mx = nt.nodes.new('ShaderNodeMath'); mx.operation = 'MULTIPLY'; nt.links.new(nz.outputs['Fac'], mx.inputs[0]); nt.links.new(vo.outputs['Distance'], mx.inputs[1])
    nt.links.new(mx.outputs[0], bm.inputs['Height']); nt.links.new(bm.outputs['Normal'], b.inputs['Normal'])
    return m


def spazio(coll, x0, nome='Spazio'):
    """la luna (raggio 40) e le stelle attorno a (x0, 0, 0). Restituisce dict luna, stelle (lista)."""
    R = {}
    R['luna'] = shape(nome + 'Luna', 'sphere', (x0, 30.0, 0.0), scale=(40, 40, 40), mat=mat_luna(), coll=coll)
    md = R['luna'].modifiers.new('liscia', 'SUBSURF'); md.levels = md.render_levels = 2
    st = material('M27_stella', (1, 1, 1), rough=0.5, emit=(1, 0.97, 0.9), emit_strength=12.0)
    rn = random.Random(27); R['stelle'] = []
    for k in range(260):
        th = rn.uniform(0, 2 * math.pi); ph = math.acos(rn.uniform(-0.6, 1.0)); d = rn.uniform(250, 320)
        p = (x0 + d * math.sin(ph) * math.cos(th), d * math.sin(ph) * math.sin(th) * 0.6 + 120, d * math.cos(ph) * 0.9)
        R['stelle'].append(shape(nome + 'Stella', 'sphere', p, scale=(rn.uniform(0.25, 0.7),) * 3, mat=st, coll=coll))
    return R


def dune(coll, x0, mat, nome='Duna'):
    rn = random.Random(11); out = []
    for k in range(22):
        p = (x0 + rn.uniform(-160, 160), rn.uniform(15, 260), -rn.uniform(3, 8))
        out.append(shape(nome, 'sphere', p, scale=(rn.uniform(18, 40), rn.uniform(14, 30), rn.uniform(6, 12)), mat=mat, coll=coll))
    return out


def cielo_deserto(coll, x0, nome='CieloDeserto'):
    """cupola di cielo azzurro (emissiva) attorno al deserto: il mondo della scena e' scuro fuori dal quartiere."""
    m = bpy.data.materials.get('M27_cielo')
    if not m:
        m = material('M27_cielo', (0.45, 0.68, 0.95), rough=1.0, emit=(0.42, 0.66, 1.0), emit_strength=1.1)
        nt = m.node_tree; b = nt.nodes['Principled BSDF']
        ge = nt.nodes.new('ShaderNodeNewGeometry'); sp = nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(ge.outputs['Normal'], sp.inputs[0])
        rp = nt.nodes.new('ShaderNodeValToRGB'); rp.color_ramp.elements[0].position = 0.0; rp.color_ramp.elements[0].color = (0.95, 0.85, 0.65, 1)
        rp.color_ramp.elements[1].position = 0.5; rp.color_ramp.elements[1].color = (0.30, 0.55, 0.95, 1)
        mp = nt.nodes.new('ShaderNodeMapRange'); mp.inputs['From Min'].default_value = 0.0; mp.inputs['From Max'].default_value = -1.0
        nt.links.new(sp.outputs['Z'], mp.inputs['Value']); nt.links.new(mp.outputs['Result'], rp.inputs['Fac'])
        nt.links.new(rp.outputs['Color'], b.inputs['Emission Color']); nt.links.new(rp.outputs['Color'], b.inputs['Base Color'])
    return shape(nome, 'sphere', (x0, 100.0, 0.0), scale=(900, 900, 600), mat=m, coll=coll)
