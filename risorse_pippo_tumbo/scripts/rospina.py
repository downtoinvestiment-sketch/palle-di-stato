"""Rospina: personaggio originale della serie (20 novembre 2026). Donna cartoon con la testa da rana: occhi enormi e globulari
in cima alla testa, palpebre teatrali, pupille un po' divergenti, bocca larghissima da rana col rossetto, sacco della gola che si gonfia
quando si scandalizza. Bionda, sempre sorpresa e drammatica, convinta di essere importantissima.
Stesso stile di Giulia e Gualtiero (capsule e sfere). Fronte -Y, piedi a z = 0, alta circa 1,95 m con gli occhi.

    import rospina
    RM = rospina.mats_rospina()
    R = rospina.rospina(chc, RM, stile='A')     # 'A' chignon altissimo e perle, 'B' caschetto con frangia e spalline enormi,
                                               # 'C' ricci a nuvola e boa di piume
    rospina.rex(R, frame, lid=0.2, mouth=0.3, gola=0.0, look=(0, 0), brow=0.0, smile=0.4)

Dizionario restituito: root, head, eyeL/R, pupilL/R, lidL/R, browL/R, mouth, lipU, lipD, gola, shoulderL/R, hipL/R."""
import math, bpy
from common import material, shape, empty
import set004
from set004 import obj

PI = math.pi
STILI = ('A', 'B', 'C', 'D', 'E', 'F')     # D, E, F: capelli alle spalle con la punta all'insu' e blazer (blu = ufficiale, rosso, viola)
EX, EY, EZ, ER = 0.20, -0.09, 0.28, 0.19        # occhi: distanza dal centro, avanti, altezza, raggio


def mats_rospina():
    M = {}
    M['skin_A'] = material('RO_pelle_A', (0.96, 0.72, 0.62), rough=0.55)
    M['skin_B'] = material('RO_pelle_B', (0.62, 0.84, 0.48), rough=0.5)        # verdina: piu' rana
    M['skin_C'] = material('RO_pelle_C', (0.80, 0.86, 0.52), rough=0.5)        # tra rosa e verde
    M['gola'] = material('RO_gola', (0.98, 0.70, 0.62), rough=0.5)
    M['white'] = material('RO_bianco', (0.97, 0.96, 0.92), rough=0.2, coat=0.6)
    M['iris'] = material('RO_iride', (0.45, 0.95, 0.25), rough=0.25)                     # iride verde chiaro da raganella (richiesta dell'autore, 20 novembre 2026; prima dorata)
    M['black'] = material('RO_nero', (0.02, 0.02, 0.025), rough=0.15)
    M['mouth'] = material('RO_bocca', (0.25, 0.03, 0.05), rough=0.6)
    M['lips'] = material('RO_rossetto', (0.85, 0.05, 0.12), rough=0.3, coat=0.4)
    M['blush'] = material('RO_fard', (1.0, 0.45, 0.5), rough=0.7)
    M['fard_leggero'] = material('RO_fard_leggero', (0.98, 0.62, 0.58), rough=0.7)
    M['brow_castano'] = material('RO_sopracciglio_castano', (0.30, 0.17, 0.07), rough=0.6)
    M['hair'] = material('RO_biondo', (0.98, 0.80, 0.36), rough=0.45, coat=0.3)
    M['brow'] = material('RO_sopracciglio', (0.35, 0.22, 0.06), rough=0.6)
    M['ombretto'] = material('RO_ombretto', (0.35, 0.75, 0.95), rough=0.4, coat=0.3)
    M['gold'] = material('RO_oro', (1.0, 0.76, 0.25), rough=0.25, metallic=1.0)
    M['pearl'] = material('RO_perla', (0.98, 0.95, 0.9), rough=0.15, coat=1.0)
    M['dress_A'] = material('RO_vestito_A', (0.10, 0.55, 0.42), rough=0.35, coat=0.3)    # verde smeraldo lucido
    M['dress_B'] = material('RO_vestito_B', (0.95, 0.20, 0.55), rough=0.4)               # tailleur rosa shocking
    M['dress_C'] = material('RO_vestito_C', (0.45, 0.22, 0.70), rough=0.4, coat=0.2)     # viola
    M['dress_D'] = material('RO_blazer_D', (0.03, 0.07, 0.24), rough=0.45)               # blazer blu navy: la versione ufficiale (20 novembre 2026)
    M['dress_E'] = material('RO_blazer_E', (0.80, 0.08, 0.10), rough=0.45)               # blazer rosso
    M['dress_F'] = material('RO_blazer_F', (0.40, 0.20, 0.62), rough=0.45)               # blazer viola
    M['revers'] = material('RO_revers', (0.05, 0.05, 0.07), rough=0.4)
    M['top'] = material('RO_top', (0.98, 0.78, 0.30), rough=0.5)                          # maglia gialla sotto il blazer
    M['ninfea'] = material('RO_ninfea', (1.0, 0.55, 0.75), rough=0.4)
    M['boa'] = material('RO_boa', (1.0, 0.55, 0.78), rough=0.9)
    M['shoe'] = material('RO_scarpa', (0.85, 0.06, 0.10), rough=0.25, coat=0.6)
    return M


# Altezze della serie (decise dall'autore il 22 novembre 2026), con Pippo come metro: Pippo 175 cm = 2,30 unita'.
# Rospina e' bassa, circa 158 cm -> 2,08 unita' (scala 0,92); Cappellone e' molto alto, circa 195 cm -> 2,56 unita' (scala 1,18, in cappellone.py).
SCALA = 0.92

def rospina(coll, M, stile='A', scala=SCALA):
    """Costruisce Rospina. stile: 'A' | 'B' | 'C' (vedi in testa al file). scala: altezza (0,92 = circa 158 cm, bassa rispetto agli altri)."""
    assert stile in STILI, stile
    R = {}
    r = R['root'] = empty('Rospina', (0, 0, 0), None, coll)
    S = lambda *a, **k: shape(*a, coll=coll, **k)
    box = set004.box_c()
    blazer = stile in ('D', 'E', 'F')
    sk, ves = M['skin_' + ('A' if blazer else stile)], M['dress_' + stile]

    # ---- corpo a clessidra un po' tozza, vestito lungo al ginocchio
    if blazer:   # pantaloni del tailleur: fianchi e gambe larghe dello stesso colore del blazer
        S('RO_Fianchi', 'sphere', (0, 0.0, 0.82), scale=(0.34, 0.27, 0.20), parent=r, mat=ves)
        S('RO_Falda', 'sphere', (0, 0.0, 0.84), scale=(0.365, 0.30, 0.25), parent=r, mat=ves)     # blazer lungo: scende fino a meta' coscia (richiesta dell'autore, 20 novembre 2026)
        S('RO_OrloGiacca', 'cyl:1:1', (0, 0.0, 0.655), scale=(0.305, 0.25, 0.012), parent=r, mat=M['revers'])
    else:
        S('RO_Gonna', 'sphere', (0, 0.0, 0.70), scale=(0.46, 0.40, 0.36), parent=r, mat=ves)
    S('RO_Vita', 'sphere', (0, 0.0, 1.00), scale=(0.30, 0.25, 0.18), parent=r, mat=ves)
    S('RO_Petto', 'sphere', (0, -0.02, 1.22), scale=(0.37, 0.29, 0.22), parent=r, mat=ves)
    S('RO_Collo', 'cyl:1:1', (0, 0.0, 1.40 if not blazer else 1.46), scale=(0.11, 0.10, 0.08 if not blazer else 0.13), parent=r, mat=sk)
    S('RO_Cintura', 'cyl:1:1', (0, 0.0, 0.96), scale=(0.29, 0.245, 0.03), parent=r, mat=M['gold'])
    S('RO_Fibbia', 'sphere', (0, -0.245, 0.96), scale=(0.06, 0.02, 0.045), parent=r, mat=M['gold'])
    if stile == 'A':                     # collana di perle giganti
        for k in range(11):
            a = PI * (0.08 + 0.84 * k / 10)
            S('RO_Perla', 'sphere', (0.25 * math.cos(a), -0.06 - 0.24 * math.sin(a), 1.38 - 0.07 * math.sin(a)), scale=(0.042,) * 3, parent=r, mat=M['pearl'])
    if stile == 'B':                     # spalline enormi e bottoni d'oro
        for sx in (-1, 1):
            S('RO_Spallina', 'sphere', (sx * 0.38, 0.0, 1.36), scale=(0.17, 0.17, 0.10), parent=r, mat=ves)
        for z in (1.20, 1.08):
            S('RO_Bottone', 'sphere', (0, -0.30, z), scale=(0.03, 0.015, 0.03), parent=r, mat=M['gold'])
    if blazer:                           # revers del blazer, maglia sotto, spilla a ninfea
        obj('RO_Maglia', box, (0, -0.27, 1.27), (0.16, 0.04, 0.22), M['top'], coll, rot=(0.25, 0, 0), parent=r)
        for sx in (-1, 1):
            obj('RO_Revers', box, (sx * 0.12, -0.285, 1.24), (0.09, 0.03, 0.30), M['revers'], coll, rot=(0.25, 0, sx * 0.35), parent=r)
            S('RO_Spallina', 'sphere', (sx * 0.36, 0.0, 1.35), scale=(0.13, 0.15, 0.08), parent=r, mat=ves)
        for z in (1.10, 1.02):
            S('RO_Bottone', 'sphere', (0, -0.285, z), scale=(0.028, 0.014, 0.028), parent=r, mat=M['gold'])
        for k in range(5):
            a = 2 * PI * k / 5
            S('RO_Petalo', 'sphere', (-0.22 + 0.035 * math.cos(a), -0.29, 1.27 + 0.035 * math.sin(a)), scale=(0.03, 0.012, 0.02), parent=r, mat=M['ninfea'])
    if stile == 'C':                     # boa di piume rosa attorno al collo
        for k in range(16):
            a = 2 * PI * k / 16
            S('RO_Boa', 'sphere', (0.24 * math.cos(a), 0.20 * math.sin(a) - 0.02, 1.40 - 0.03 * math.sin(a)), scale=(0.09, 0.09, 0.08), parent=r, mat=M['boa'])
        for k in range(5):
            S('RO_BoaCoda', 'sphere', (0.20 + 0.02 * k, -0.20, 1.32 - 0.12 * k), scale=(0.08, 0.08, 0.075), parent=r, mat=M['boa'])

    # ---- testa: 'rana' (A, B, C) larga e schiacciata con la bocca da rana; 'ovale' (D, E, F) piu' umana, guance morbide,
    #      nasino e bocca umana col sorriso teatrale. Gli occhi da rana in cima alla testa restano in tutte e due.
    ovale = blazer
    G = R['G'] = (dict(es=0.85, ex=0.175, ey=-0.15, ez=0.12, mw=0.11, my=-0.258, mz=-0.235, ang=0.115, angy=-0.24, gola=0.35, gy=-0.08, gz=-0.39, bw=0.18, bt=0.05, lt=0.6)
                  if ovale else dict(lt=1.0, es=1.0, ex=EX, ey=EY, ez=EZ, mw=0.30, my=-0.29, mz=-0.12, ang=0.30, angy=-0.24, gola=1.0, gy=-0.11, gz=-0.25, bw=0.16, bt=0.03))
    h = R['head'] = empty('RO_Head', (0, -0.02, 1.68 if not ovale else 1.84), r, coll)
    if ovale:
        S('RO_Cranio', 'sphere', (0, 0, -0.03), scale=(0.32, 0.29, 0.315), parent=h, mat=sk)
        S('RO_Mento', 'sphere', (0, -0.05, -0.21), scale=(0.23, 0.22, 0.17), parent=h, mat=sk)   # mento tondo
        for sx in (-1, 1): S('RO_Guancia', 'sphere', (sx * 0.15, -0.115, -0.16), scale=(0.12, 0.11, 0.105), parent=h, mat=sk)   # guance morbide, appena accennate
        # naso umano: dorso, punta, ali e narici (niente muso)
        S('RO_NasoDorso', 'sphere', (0, -0.285, -0.065), scale=(0.03, 0.045, 0.085), rot=(0.35, 0, 0), parent=h, mat=sk)
        S('RO_NasoPunta', 'sphere', (0, -0.322, -0.135), scale=(0.04, 0.042, 0.036), parent=h, mat=sk)
        for sx in (-1, 1):
            S('RO_NasoAla', 'sphere', (sx * 0.038, -0.298, -0.142), scale=(0.024, 0.028, 0.024), parent=h, mat=sk)
            S('RO_Narice', 'sphere', (sx * 0.021, -0.318, -0.164), scale=(0.011, 0.008, 0.005), parent=h, mat=M['mouth'])
    else:
        S('RO_Cranio', 'sphere', (0, 0, 0), scale=(0.40, 0.33, 0.25), parent=h, mat=sk)
        S('RO_Mascella', 'sphere', (0, -0.03, -0.13), scale=(0.37, 0.30, 0.15), parent=h, mat=sk)
    R['gola'] = S('RO_Gola', 'sphere', (0, G['gy'], G['gz']), scale=(0.21 * G['gola'], 0.17 * G['gola'], 0.10 * G['gola']), parent=h, mat=M['gola'])
    if ovale: R['gola'].hide_render = R['gola'].hide_viewport = True   # niente sacco della gola sul viso umano
    ex, ey, ez = G['ex'], G['ey'], G['ez']
    for sx, nm in ((-1, 'L'), (1, 'R')):
        S('RO_Torretta', 'sphere', (sx * ex, ey + 0.03, ez - 0.10 * G['es']), scale=(0.18 * G['es'], 0.16 * G['es'], 0.13 * G['es']), parent=h, mat=sk)   # la base dell'occhio
        e = R['eye' + nm] = empty('RO_Occhio' + nm, (sx * ex, ey, ez), h, coll); e.scale = (G['es'],) * 3
        S('RO_Bulbo', 'sphere', (0, 0, 0), scale=(ER, ER * 0.95, ER), parent=e, mat=M['white'])
        p = R['pupil' + nm] = empty('RO_Pup' + nm, (0, 0, 0), e, coll)
        S('RO_Iride', 'sphere', (0, -ER * 0.93, 0), scale=(ER * 0.42, ER * 0.12, ER * 0.42), parent=p, mat=M['iris'])
        S('RO_Pupilla', 'sphere', (0, -ER * 1.0, 0), scale=(ER * 0.22, ER * 0.08, ER * 0.30), parent=p, mat=M['black'])
        S('RO_Luce', 'sphere', (sx * 0.02, -ER * 1.04, 0.03), scale=(0.014, 0.006, 0.014), parent=p, mat=M['white'])
        R['lid' + nm] = S('RO_Palpebra', 'sphere', (0, -0.004, 0.0), scale=(ER * 1.06, ER * 1.03, ER * 0.5), parent=e, mat=M['ombretto'])
        c_ = R['ciglia' + nm] = empty('RO_Ciglia' + nm, (0, -ER, 0), e, coll)
        for j in (-2, -1, 0, 1, 2):
            obj('RO_Ciglio', box, (j * 0.03, -0.004, 0.0), (0.011, 0.011, 0.07), M['black'], coll, rot=(-0.95, j * 0.28, 0), parent=c_)
        R['brow' + nm] = obj('RO_Sopracciglio', box, (sx * ex, ey - 0.04, ez + ER * G['es'] + 0.06), (G['bw'], G['bt'], G['bt']), M['brow_castano'] if ovale else M['brow'], coll, rot=(0, -sx * 0.25, 0), parent=h)
        if ovale:
            S('RO_Fard', 'sphere', (sx * 0.17, -0.212, -0.15), scale=(0.05, 0.012, 0.03), parent=h, mat=M['fard_leggero'])
            S('RO_Orecchino', 'sphere', (sx * 0.31, -0.02, -0.17), scale=(0.055, 0.055, 0.055), parent=h, mat=M['gold'])
        else:
            S('RO_Fard', 'sphere', (sx * 0.26, -0.24, -0.07), scale=(0.08, 0.03, 0.05), parent=h, mat=M['blush'])
            S('RO_Narice', 'sphere', (sx * 0.035, -0.325, 0.02), scale=(0.016, 0.01, 0.012), parent=h, mat=M['black'])
            S('RO_Orecchino', 'sphere', (sx * 0.39, -0.02, -0.16), scale=(0.06, 0.06, 0.06), parent=h, mat=M['gold'])
    # bocca col rossetto: si apre con rex(mouth=), gli angoli salgono con smile (sorriso teatrale)
    mw, my, mz = G['mw'], G['my'], G['mz']
    R['mouth'] = S('RO_Bocca', 'sphere', (0, my + 0.012 * (1 - G['lt']) * 2.5, mz), scale=(mw * (0.9 if G['lt'] < 1 else 1), 0.06 * G['lt'], 0.02), parent=h, mat=M['mouth'])
    R['lipU'] = S('RO_LabbroSu', 'sphere', (0, my - 0.01 * G['lt'], mz + 0.015), scale=(mw * 1.03, 0.05 * G['lt'], 0.022 * G['lt']), parent=h, mat=M['lips'])
    R['lipD'] = S('RO_LabbroGiu', 'sphere', (0, my - 0.005, mz - 0.015), scale=(mw * 0.95, 0.05 * G['lt'], 0.026 * G['lt']), parent=h, mat=M['lips'])
    for sx, nm in ((-1, 'L'), (1, 'R')):
        R['angolo' + nm] = S('RO_Angolo', 'sphere', (sx * G['ang'], G['angy'], mz + 0.01), scale=(0.03 * G['lt'], 0.03 * G['lt'], 0.022 * G['lt']), parent=h, mat=M['lips'])

    # ---- capelli biondi (dietro e sopra la nuca: gli occhi spuntano davanti)
    hair = M['hair']
    if stile == 'A':          # chignon altissimo
        S('RO_Capelli', 'sphere', (0, 0.07, 0.04), scale=(0.415, 0.30, 0.26), parent=h, mat=hair)
        S('RO_Chignon1', 'sphere', (0, 0.12, 0.30), scale=(0.17, 0.16, 0.14), parent=h, mat=hair)
        S('RO_Chignon2', 'sphere', (0, 0.13, 0.48), scale=(0.15, 0.14, 0.13), parent=h, mat=hair)
        S('RO_Chignon3', 'sphere', (0, 0.13, 0.64), scale=(0.11, 0.11, 0.10), parent=h, mat=hair)
        S('RO_Fiocco', 'sphere', (0, 0.06, 0.40), scale=(0.10, 0.03, 0.05), parent=h, mat=M['dress_A'])
    elif stile == 'B':        # caschetto squadrato con frangia dritta (sotto gli occhi, sopra le narici)
        S('RO_Capelli', 'sphere', (0, 0.06, 0.05), scale=(0.43, 0.32, 0.27), parent=h, mat=hair)
        for sx in (-1, 1):
            S('RO_Caschetto', 'sphere', (sx * 0.38, 0.0, -0.10), scale=(0.11, 0.26, 0.22), parent=h, mat=hair)
        obj('RO_Frangia', box, (0, -0.255, 0.13), (0.42, 0.10, 0.06), hair, coll, rot=(0.25, 0, 0), parent=h)
    elif blazer:              # alle spalle, liscia, con la riga di lato e le punte all'insu' (stile anni sessanta)
        S('RO_Capelli', 'sphere', (0, 0.05, 0.02), scale=(0.335, 0.31, 0.37), parent=h, mat=hair)
        S('RO_Ciuffo', 'sphere', (0.10, -0.06, 0.22), scale=(0.22, 0.20, 0.10), parent=h, mat=hair)            # riga di lato: ciuffo gonfio a destra
        for sx in (-1, 1):
            S('RO_Bande', 'sphere', (sx * 0.30, 0.03, -0.15), scale=(0.10, 0.22, 0.25), parent=h, mat=hair)     # lunghezza media: arrivano alle spalle senza scendere sulla schiena (richiesta dell'autore); il taglio resta quello inventato, con le punte all'insu'
            S('RO_Punta', 'sphere', (sx * 0.36, 0.02, -0.38), scale=(0.12, 0.17, 0.06), parent=h, mat=hair)
        S('RO_Nuca', 'sphere', (0, 0.20, -0.14), scale=(0.30, 0.14, 0.25), parent=h, mat=hair)
        S('RO_PuntaDietro', 'sphere', (0, 0.23, -0.38), scale=(0.32, 0.13, 0.06), parent=h, mat=hair)
    else:                     # ricci a nuvola
        S('RO_Capelli', 'sphere', (0, 0.07, 0.05), scale=(0.42, 0.31, 0.27), parent=h, mat=hair)
        for k in range(14):
            a = PI * (-0.15 + 1.3 * k / 13)
            S('RO_Riccio', 'sphere', (0.44 * math.cos(a), 0.10 + 0.05 * math.sin(3 * a), 0.06 + 0.28 * math.sin(a)), scale=(0.13, 0.13, 0.13), parent=h, mat=hair)
        for k in range(6):
            a = 2 * PI * k / 6
            S('RO_RiccioDietro', 'sphere', (0.22 * math.cos(a), 0.26 + 0.06 * math.sin(a), 0.12 + 0.12 * math.sin(a)), scale=(0.14, 0.14, 0.14), parent=h, mat=hair)

    # ---- braccia e gambe, tacchi rossi a punta
    for nm, sx in (('L', -1), ('R', 1)):
        sh = R['shoulder' + nm] = empty('RO_shoulder' + nm, (sx * 0.36, 0, 1.30), r, coll)
        sh.rotation_euler = (0, -sx * 0.30, 0)
        if blazer:                         # maniche lunghe fino al polso, con il polsino
            S('RO_Manica', 'cap:0.105:0.40', (0, 0, -0.25), parent=sh, mat=ves)
            S('RO_Polsino', 'cyl:1:1', (0, 0, -0.505), scale=(0.098, 0.098, 0.02), parent=sh, mat=M['revers'])
        else:
            S('RO_Manica', 'cap:0.11:0.10', (0, 0, -0.08), parent=sh, mat=ves)
            S('RO_Braccio', 'cap:0.085:0.34', (0, 0, -0.30), parent=sh, mat=sk)
        S('RO_Mano', 'sphere', (0, 0, -0.60), scale=(0.09, 0.08, 0.10), parent=sh, mat=sk)
        for j in (-1, 0, 1):   # dita da rana con i polpastrelli tondi
            S('RO_Dito', 'sphere', (j * 0.04, -0.01, -0.70), scale=(0.025, 0.025, 0.035), parent=sh, mat=sk)
        hp = R['hip' + nm] = empty('RO_hip' + nm, (sx * 0.17, 0.0, 0.46), r, coll)
        if blazer:
            S('RO_Pantalone', 'cap:0.105:0.55', (0, 0, -0.03), parent=hp, mat=ves)
            S('RO_Orlo', 'cyl:1:1', (0, 0, -0.37), scale=(0.11, 0.11, 0.025), parent=hp, mat=M['revers'])
        else:
            S('RO_Gamba', 'cap:0.07:0.30', (0, 0, -0.22), parent=hp, mat=sk)
        obj('RO_Scarpa', box, (0, -0.05, -0.44), (0.12, 0.26, 0.06), M['shoe'], coll, parent=hp)
        S('RO_PuntaScarpa', 'sphere', (0, -0.17, -0.44), scale=(0.06, 0.09, 0.035), parent=hp, mat=M['shoe'])
        S('RO_Tacco', 'cyl:1:1', (0, 0.06, -0.46), scale=(0.02, 0.02, 0.05), parent=hp, mat=M['shoe'])
    rex(R, None)
    r.scale = (scala,) * 3                                       # piu' bassa degli altri personaggi
    return R


def rex(R, f, lid=0.25, mouth=0.15, gola=0.0, look=(0.0, 0.0), brow=0.0, smile=0.3, diverge=0.18):
    """Faccia di Rospina al fotogramma f (f=None: senza chiavi).
    lid 0 = occhi spalancati, 1 = chiusi; mouth 0..1; gola 0..1 = il sacco della gola si gonfia; look = (x, y);
    brow > 0 arrabbiata, < 0 scandalizzata (sopracciglia alte); smile -1..1 angoli della bocca; diverge = pupille storte verso fuori."""
    G = R['G']
    def k(o, prop):
        if f is not None: o.keyframe_insert(prop, frame=f)
    for sx, nm in ((-1, 'L'), (1, 'R')):
        p = R['pupil' + nm]
        p.rotation_euler = (look[1] * 0.45, 0, -(look[0] + sx * diverge) * 0.6); k(p, 'rotation_euler')
        lid = max(-0.08, lid); l = R['lid' + nm]; zs = ER * (0.45 + 0.62 * lid); zc = ER * 0.78 * (1 - lid)       # calotta che scende sull'occhio
        l.scale = (ER * 1.06, ER * 1.03, zs); l.location = (0, -0.004, zc); k(l, 'scale'); k(l, 'location')
        zb = max(-ER * 0.98, zc - zs); c_ = R['ciglia' + nm]; c_.location = (0, -math.sqrt(max(0.0, (ER * 1.03) ** 2 - zb ** 2)), zb); k(c_, 'location')
        b = R['brow' + nm]
        b.location = (sx * G['ex'], G['ey'] - 0.04, G['ez'] + ER * G['es'] + 0.06 + (0.05 if brow < 0 else 0.0) * min(1, -brow) - 0.03 * max(0, brow)); k(b, 'location')
        b.rotation_euler = (0, -sx * (0.25 + 0.5 * brow), 0); k(b, 'rotation_euler')
        a = R['angolo' + nm]
        a.location = (sx * G['ang'], G['angy'], G['mz'] + 0.01 + 0.05 * smile); k(a, 'location')
    m = R['mouth']; m.scale = (G['mw'] * (0.9 if G['lt'] < 1 else 1), 0.06 * G['lt'], 0.02 + 0.11 * mouth * G['lt']); m.location = (0, G['my'] + 0.012 * (1 - G['lt']) * 2.5, G['mz'] - 0.05 * mouth * G['lt']); k(m, 'scale'); k(m, 'location')
    R['lipD'].location = (0, G['my'] - 0.005, G['mz'] - 0.015 - 0.13 * mouth * G['lt']); k(R['lipD'], 'location')
    g = R['gola']; s_ = G['gola'] + 1.3 * gola; g.scale = (0.21 * s_, 0.17 * s_, 0.10 * s_); g.location = (0, G['gy'] - 0.08 * gola, G['gz'] - 0.06 * gola)
    k(g, 'scale'); k(g, 'location')


# Le otto espressioni della scheda (schede/rospina_espressioni.jpg): rospina.emozione(R, f, 'scandalizzata')
EMOZIONI = {
    'importantissima': dict(lid=0.35, mouth=0.05, smile=0.6, brow=0.2),
    'scandalizzata': dict(lid=-0.35, mouth=0.9, gola=1.0, brow=-1.0, smile=-0.3),
    'comizio': dict(lid=0.1, mouth=1.0, gola=0.4, brow=0.9, smile=0.1, diverge=0.05),
    'furiosa': dict(lid=0.3, mouth=0.6, gola=0.7, brow=1.4, smile=-1.0, diverge=0.0),
    'falsa modestia': dict(lid=0.6, mouth=0.0, smile=0.9, brow=-0.3, look=(0.6, -0.3)),
    'colta in fallo': dict(lid=-0.3, mouth=0.35, brow=-0.8, smile=-0.6, look=(-0.9, 0.0), diverge=0.3),
    'offesa': dict(lid=0.75, mouth=0.0, gola=0.5, brow=0.6, smile=-0.9, look=(0.8, 0.3)),
    'trionfo': dict(lid=0.15, mouth=0.75, brow=-0.5, smile=1.0, gola=0.2),
}
def emozione(R, f, nome):
    rex(R, f, **EMOZIONI[nome])
