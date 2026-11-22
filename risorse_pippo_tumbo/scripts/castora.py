"""La Castora: personaggio originale della serie (20 novembre 2026), chiesto dall'autore come «il castoro».
Donna cartoon con i tratti da castoro: due incisivi enormi che escono dal labbro, orecchie a sventola grandi,
caschetto nero liscio che arriva alle spalle, naso romano molto pronunciato. Blazer blu aperto, camicia bianca, pantaloni blu.
Stesso stile di Rospina, Giulia e Gualtiero (capsule e sfere). Fronte -Y, piedi a z = 0, alta circa 2,15 m.
Personaggio inventato: non e' e non deve diventare il ritratto di una persona reale.

    import castora
    K = castora.castora(chc, castora.mats_castora(), stile='A')   # 'A' come da descrizione, 'B' con coda piatta e naso scuro,
                                                                  # 'C' castoro vero: pelo marrone, muso chiaro, coda
    castora.cex(K, frame, lid=0.2, mouth=0.2, look=(0, 0), brow=0.0, smile=0.4, denti=0.0, orecchie=0.0)
    castora.emozione(K, frame, 'rosicchia')

Dizionario restituito: root, head, eyeL/R, pupilL/R, lidL/R, browL/R, earL/R, mouth, lipU, lipD, denti, angoloL/R,
coda (None nello stile A), shoulderL/R, hipL/R."""
import math, bpy
from common import material, shape, empty
import set004
from set004 import obj

PI = math.pi
STILI = ('A', 'B', 'C')
EX, EY, EZ, ER = 0.13, -0.205, 0.03, 0.10      # occhi: distanza dal centro, avanti, altezza, raggio
MW, MY, MZ = 0.12, -0.262, -0.215                 # bocca: mezza larghezza, avanti, altezza


def mats_castora():
    M = {}
    M['skin_A'] = material('CA_pelle', (0.95, 0.74, 0.62), rough=0.55)
    M['skin_B'] = M['skin_A']
    M['skin_C'] = material('CA_pelo', (0.50, 0.31, 0.17), rough=0.8)
    M['muso'] = material('CA_muso', (0.86, 0.68, 0.48), rough=0.7)
    M['ear_in'] = material('CA_orecchio_dentro', (0.98, 0.58, 0.55), rough=0.6)
    M['white'] = material('CA_bianco', (0.97, 0.96, 0.92), rough=0.2, coat=0.6)
    M['iris'] = material('CA_iride', (0.28, 0.16, 0.07), rough=0.25)
    M['black'] = material('CA_nero', (0.02, 0.02, 0.025), rough=0.15)
    M['mouth'] = material('CA_bocca', (0.25, 0.03, 0.05), rough=0.6)
    M['lips'] = material('CA_labbra', (0.80, 0.30, 0.32), rough=0.4)
    M['teeth'] = material('CA_denti', (1.0, 0.98, 0.90), rough=0.15, coat=0.8)
    M['fard'] = material('CA_fard', (0.98, 0.58, 0.55), rough=0.7)
    M['hair'] = material('CA_capelli', (0.035, 0.035, 0.045), rough=0.5)
    M['nose_dark'] = material('CA_naso_scuro', (0.10, 0.06, 0.05), rough=0.3, coat=0.4)
    M['blazer'] = material('CA_blazer', (0.04, 0.12, 0.42), rough=0.5)        # blu (scelta dell'autore, 20 novembre 2026)
    M['revers'] = material('CA_revers', (0.03, 0.08, 0.30), rough=0.4)
    M['shirt'] = material('CA_camicia', (0.97, 0.97, 0.96), rough=0.5)
    M['pants'] = material('CA_pantaloni', (0.04, 0.12, 0.42), rough=0.55)    # blu come il blazer
    M['button'] = material('CA_bottone', (0.85, 0.85, 0.88), rough=0.25, metallic=1.0)
    M['shoe'] = material('CA_scarpa', (0.05, 0.05, 0.06), rough=0.25, coat=0.6)
    M['tail'] = material('CA_coda', (0.22, 0.13, 0.08), rough=0.75)
    return M


# Altezza (decisa dall'autore il 22 novembre 2026): circa 170 cm con Pippo = 175 cm (2,30 unita') -> 2,23 unita', scala 0,995.
SCALA = 0.995

def castora(coll, M, stile='A', scala=SCALA):
    """Costruisce la Castora. stile: 'A' | 'B' | 'C' (vedi in testa al file). scala: altezza (0,995 = circa 170 cm)."""
    assert stile in STILI, stile
    K = {'stile': stile}
    r = K['root'] = empty('Castora', (0, 0, 0), None, coll)
    S = lambda *a, **k: shape(*a, coll=coll, **k)
    box = set004.box_c()
    sk, bl, pa = M['skin_' + stile], M['blazer'], M['pants']

    # ---- corpo: pantaloni bianchi, blazer lungo, camicia bianca col colletto
    S('CA_Fianchi', 'sphere', (0, 0.0, 0.80), scale=(0.33, 0.26, 0.20), parent=r, mat=pa)
    S('CA_Falda', 'sphere', (0, 0.0, 0.90), scale=(0.355, 0.29, 0.20), parent=r, mat=bl)
    S('CA_Vita', 'sphere', (0, 0.0, 1.02), scale=(0.31, 0.255, 0.18), parent=r, mat=bl)
    S('CA_Petto', 'sphere', (0, -0.01, 1.22), scale=(0.36, 0.28, 0.22), parent=r, mat=bl)
    S('CA_Collo', 'cyl:1:1', (0, 0.0, 1.46), scale=(0.105, 0.10, 0.13), parent=r, mat=sk)
    # blazer aperto (richiesta dell'autore): la camicia si vede dal collo all'orlo, le due falde restano ai lati
    S('CA_CamiciaPetto', 'sphere', (0, -0.075, 1.22), scale=(0.255, 0.255, 0.215), parent=r, mat=M['shirt'])
    S('CA_CamiciaVita', 'sphere', (0, -0.075, 1.02), scale=(0.235, 0.235, 0.19), parent=r, mat=M['shirt'])
    for sx in (-1, 1):
        obj('CA_Revers', box, (sx * 0.235, -0.215, 1.24), (0.07, 0.03, 0.30), M['revers'], coll, rot=(0.18, 0, sx * 0.12), parent=r)
        obj('CA_FaldaAperta', box, (sx * 0.25, -0.195, 0.95), (0.07, 0.03, 0.30), M['revers'], coll, rot=(-0.05, 0, -sx * 0.10), parent=r)
        obj('CA_Colletto', box, (sx * 0.075, -0.20, 1.415), (0.11, 0.035, 0.06), M['shirt'], coll, rot=(0.5, 0, -sx * 0.55), parent=r)
        S('CA_Spallina', 'sphere', (sx * 0.35, 0.0, 1.35), scale=(0.13, 0.15, 0.08), parent=r, mat=bl)
    for z in (1.30, 1.18, 1.06, 0.94):
        S('CA_BottoneCamicia', 'sphere', (0, -0.075 - (0.255 * math.sqrt(max(0.0, 1 - ((z - 1.22) / 0.215) ** 2)) if z > 1.12 else 0.235 * math.sqrt(max(0.0, 1 - ((z - 1.02) / 0.19) ** 2))) - 0.004, z), scale=(0.014, 0.008, 0.014), parent=r, mat=M['button'])

    # ---- coda piatta da castoro (stili B e C): esce da sotto il blazer, dietro
    K['coda'] = None
    if stile in ('B', 'C'):
        c = K['coda'] = empty('CA_Coda', (0, 0.22, 0.78), r, coll); c.rotation_euler = (-0.55, 0, 0)
        S('CA_CodaPala', 'sphere', (0, 0.34, 0), scale=(0.21, 0.36, 0.045), parent=c, mat=M['tail'])
        for i in range(4):
            for j in (-1, 0, 1):
                S('CA_Squama', 'sphere', (j * 0.10, 0.14 + i * 0.13, 0.036), scale=(0.04, 0.05, 0.012), parent=c, mat=M['revers'])

    # ---- testa: ovale, guance piene, incisivi enormi, orecchie a sventola
    h = K['head'] = empty('CA_Head', (0, -0.02, 1.84), r, coll)
    S('CA_Cranio', 'sphere', (0, 0, -0.03), scale=(0.32, 0.29, 0.315), parent=h, mat=sk)
    S('CA_Mento', 'sphere', (0, -0.05, -0.22), scale=(0.225, 0.215, 0.16), parent=h, mat=sk)
    cheek = M['muso'] if stile == 'C' else sk
    for sx in (-1, 1):
        S('CA_Guancia', 'sphere', (sx * 0.125, -0.145, -0.165), scale=(0.125, 0.12, 0.105), parent=h, mat=cheek)
        if stile != 'C':
            S('CA_Fard', 'sphere', (sx * 0.185, -0.218, -0.13), scale=(0.05, 0.012, 0.03), parent=h, mat=M['fard'])
    naso = M['nose_dark'] if stile in ('B', 'C') else sk
    if stile == 'A':
        S('CA_NasoDorso', 'sphere', (0, -0.335, -0.03), scale=(0.04, 0.06, 0.118), rot=(-0.6, 0, 0), parent=h, mat=sk)       # dorso unico, lungo, dalla fronte alla punta
        S('CA_NasoGobba', 'sphere', (0, -0.372, -0.025), scale=(0.034, 0.036, 0.055), rot=(-0.6, 0, 0), parent=h, mat=sk)   # la gobba del naso romano
        S('CA_NasoPunta', 'sphere', (0, -0.398, -0.118), scale=(0.048, 0.05, 0.044), parent=h, mat=sk)
        for sx in (-1, 1):
            S('CA_NasoAla', 'sphere', (sx * 0.04, -0.352, -0.128), scale=(0.03, 0.045, 0.03), parent=h, mat=sk)
            S('CA_Narice', 'sphere', (sx * 0.024, -0.388, -0.155), scale=(0.012, 0.016, 0.006), parent=h, mat=M['mouth'])
    else:
        S('CA_NasoPunta', 'sphere', (0, -0.318, -0.115), scale=(0.05, 0.045, 0.04), parent=h, mat=naso)

    for sx, nm in ((-1, 'L'), (1, 'R')):
        # orecchie a sventola: dischi grandi aperti verso fuori, perno alla base per farle muovere
        e = K['ear' + nm] = empty('CA_Orecchio' + nm, (sx * 0.29, 0.0, 0.0), h, coll); e.rotation_euler = (0, 0, sx * 0.45)
        S('CA_OrecchioFuori', 'sphere', (sx * 0.15, 0, 0.02), scale=(0.15, 0.045, 0.125), parent=e, mat=sk)
        S('CA_OrecchioDentro', 'sphere', (sx * 0.155, -0.03, 0.02), scale=(0.10, 0.025, 0.085), parent=e, mat=M['ear_in'])
        # occhi
        o = K['eye' + nm] = empty('CA_Occhio' + nm, (sx * EX, EY, EZ), h, coll)
        S('CA_Bulbo', 'sphere', (0, 0, 0), scale=(ER, ER * 0.9, ER * 1.1), parent=o, mat=M['white'])
        p = K['pupil' + nm] = empty('CA_Pup' + nm, (0, 0, 0), o, coll)
        S('CA_Iride', 'sphere', (0, -ER * 0.84, 0), scale=(ER * 0.50, ER * 0.14, ER * 0.56), parent=p, mat=M['iris'])
        S('CA_Pupilla', 'sphere', (0, -ER * 0.93, 0), scale=(ER * 0.28, ER * 0.09, ER * 0.32), parent=p, mat=M['black'])
        S('CA_Luce', 'sphere', (sx * 0.012, -ER * 1.0, 0.022), scale=(0.011, 0.005, 0.011), parent=p, mat=M['white'])
        K['lid' + nm] = S('CA_Palpebra', 'sphere', (0, -0.004, 0.0), scale=(ER * 1.07, ER * 0.98, ER * 0.5), parent=o, mat=sk)
        K['brow' + nm] = obj('CA_Sopracciglio', box, (sx * EX, EY - 0.075, EZ + 0.135), (0.13, 0.035, 0.032), M['hair'], coll, rot=(0, -sx * 0.15, 0), parent=h)
        K['angolo' + nm] = S('CA_Angolo', 'sphere', (sx * MW, MY + 0.02, MZ + 0.01), scale=(0.022, 0.022, 0.018), parent=h, mat=M['lips'])

    # bocca: labbro di sopra corto, cosi' i due incisivi restano sempre fuori
    K['mouth'] = S('CA_Bocca', 'sphere', (0, MY + 0.02, MZ), scale=(MW * 0.9, 0.04, 0.02), parent=h, mat=M['mouth'])
    K['lipU'] = S('CA_LabbroSu', 'sphere', (0, MY, MZ + 0.018), scale=(MW * 1.0, 0.035, 0.016), parent=h, mat=M['lips'])
    K['lipD'] = S('CA_LabbroGiu', 'sphere', (0, MY + 0.012, MZ - 0.02), scale=(MW * 0.85, 0.035, 0.018), parent=h, mat=M['lips'])
    d = K['denti'] = empty('CA_Denti', (0, MY - 0.022, MZ + 0.012), h, coll); d.rotation_euler = (0.22, 0, 0)
    for sx in (-1, 1):
        obj('CA_Incisivo', box, (sx * 0.031, 0, -0.04), (0.056, 0.03, 0.075), M['teeth'], coll, parent=d)
        S('CA_IncisivoPunta', 'sphere', (sx * 0.031, 0, -0.076), scale=(0.028, 0.015, 0.014), parent=d, mat=M['teeth'])

    # ---- caschetto nero liscio alle spalle, riga in mezzo, punte dritte; le orecchie spuntano fuori
    hair = M['hair']
    S('CA_Capelli', 'sphere', (0, 0.05, 0.03), scale=(0.335, 0.31, 0.36), parent=h, mat=hair)
    for sx in (-1, 1):
        S('CA_Banda', 'sphere', (sx * 0.265, 0.035, -0.17), scale=(0.095, 0.215, 0.30), parent=h, mat=hair)
    S('CA_Nuca', 'sphere', (0, 0.19, -0.17), scale=(0.30, 0.14, 0.30), parent=h, mat=hair)
    S('CA_Frangia', 'sphere', (0, -0.15, 0.215), scale=(0.275, 0.17, 0.10), rot=(0.25, 0, 0), parent=h, mat=hair)   # frangia piena e dritta

    # ---- braccia (maniche del blazer, polsino della camicia) e gambe (pantaloni bianchi larghi)
    for nm, sx in (('L', -1), ('R', 1)):
        sh = K['shoulder' + nm] = empty('CA_shoulder' + nm, (sx * 0.35, 0, 1.30), r, coll)
        sh.rotation_euler = (0, -sx * 0.28, 0)
        S('CA_Manica', 'cap:0.105:0.40', (0, 0, -0.25), parent=sh, mat=bl)
        S('CA_Polsino', 'cyl:1:1', (0, 0, -0.505), scale=(0.098, 0.098, 0.022), parent=sh, mat=M['shirt'])
        S('CA_Mano', 'sphere', (0, 0, -0.60), scale=(0.09, 0.08, 0.10), parent=sh, mat=sk)
        hp = K['hip' + nm] = empty('CA_hip' + nm, (sx * 0.17, 0.0, 0.46), r, coll)
        S('CA_Pantalone', 'cap:0.115:0.55', (0, 0, -0.03), parent=hp, mat=pa)
        S('CA_Orlo', 'cyl:1:1', (0, 0, -0.37), scale=(0.125, 0.125, 0.03), parent=hp, mat=pa)
        obj('CA_Scarpa', box, (0, -0.05, -0.44), (0.13, 0.27, 0.06), M['shoe'], coll, parent=hp)
        S('CA_PuntaScarpa', 'sphere', (0, -0.17, -0.44), scale=(0.065, 0.09, 0.035), parent=hp, mat=M['shoe'])
    cex(K, None)
    r.scale = (scala,) * 3                                       # circa 170 cm
    return K


def cex(K, f, lid=0.2, mouth=0.15, look=(0.0, 0.0), brow=0.0, smile=0.35, denti=0.0, orecchie=0.0):
    """Faccia della Castora al fotogramma f (f=None: senza chiavi).
    lid 0 = occhi spalancati, 1 = chiusi; mouth 0..1; look = (x, y); brow > 0 arrabbiata, < 0 sopracciglia alte;
    smile -1..1 angoli della bocca; denti 0..1 = gli incisivi si spingono in fuori; orecchie -1..1 = si chiudono / si spalancano."""
    def k(o, prop):
        if f is not None: o.keyframe_insert(prop, frame=f)
    for sx, nm in ((-1, 'L'), (1, 'R')):
        p = K['pupil' + nm]; p.rotation_euler = (look[1] * 0.45, 0, -look[0] * 0.6); k(p, 'rotation_euler')
        ld = max(-0.1, lid); l = K['lid' + nm]; zs = ER * (0.50 + 0.70 * ld); zc = ER * 0.95 * (1 - ld)
        l.scale = (ER * 1.07, ER * 0.98, zs); l.location = (0, -0.004, zc); k(l, 'scale'); k(l, 'location')
        b = K['brow' + nm]
        b.location = (sx * EX, EY - 0.075, EZ + 0.135 + 0.04 * min(1, max(0, -brow)) - 0.035 * max(0, brow)); k(b, 'location')
        b.rotation_euler = (0, -sx * (0.15 + 0.5 * brow), 0); k(b, 'rotation_euler')
        a = K['angolo' + nm]; a.location = (sx * MW, MY + 0.02, MZ + 0.01 + 0.045 * smile); k(a, 'location')
        e = K['ear' + nm]; e.rotation_euler = (0, sx * 0.12 * orecchie, sx * (0.45 - 0.30 * orecchie)); k(e, 'rotation_euler')
    m = K['mouth']; m.scale = (MW * 0.9, 0.04, 0.02 + 0.10 * mouth); m.location = (0, MY + 0.02, MZ - 0.05 * mouth); k(m, 'scale'); k(m, 'location')
    K['lipD'].location = (0, MY + 0.012, MZ - 0.02 - 0.125 * mouth); k(K['lipD'], 'location')
    d = K['denti']; d.rotation_euler = (0.22 + 0.45 * denti, 0, 0); d.scale = (1 + 0.15 * denti,) * 3; k(d, 'rotation_euler'); k(d, 'scale')


# Le otto espressioni della scheda (schede/castora_opzioni.jpg): castora.emozione(K, f, 'rosicchia')
EMOZIONI = {
    'normale': dict(lid=0.2, mouth=0.1, smile=0.4),
    'saputella': dict(lid=0.55, mouth=0.0, smile=0.8, brow=-0.4, look=(0.5, 0.3)),
    'predica': dict(lid=0.1, mouth=0.9, brow=0.6, smile=0.0, denti=0.3, orecchie=0.4),
    'furiosa': dict(lid=0.3, mouth=0.5, brow=1.4, smile=-1.0, denti=0.8, orecchie=-0.6),
    'scandalizzata': dict(lid=-0.1, mouth=1.0, brow=-1.0, smile=-0.3, orecchie=1.0),
    'colta in fallo': dict(lid=-0.1, mouth=0.25, brow=-0.8, smile=-0.6, look=(-0.9, 0.0), orecchie=0.8),
    'rosicchia': dict(lid=0.45, mouth=0.35, brow=0.3, smile=0.5, denti=1.0, look=(0.0, -0.6)),
    'trionfo': dict(lid=0.15, mouth=0.75, brow=-0.5, smile=1.0, denti=0.4, orecchie=0.6),
}
def emozione(K, f, nome):
    cex(K, f, **EMOZIONI[nome])
