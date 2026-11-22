"""Il commissario: personaggio originale della serie (20 novembre 2026), per il copione n. 26 (Francesco il cactus).
Pancione enorme che tira i bottoni, faccia tonda col doppio mento, naso a patata rosso, baffoni, berretto con la visiera.
La pancia e' un oggetto a parte (R['pancia']): si gonfia e si sgonfia con la scala (gag del palloncino bucato).
Stesso stile di Gualtiero e Rospina (sfere e capsule). Fronte -Y, piedi a z = 0, alto circa 1,85 m col berretto.

    import commissario
    CM = commissario.mats_commissario()
    R = commissario.commissario(chc, CM, stile='A')   # 'A' divisa blu e baffoni neri, 'B' (scelto: il commissario ufficiale) divisa blu e occhiali a specchio,
                                                      # 'C' divisa blu, baffi a manubrio grigi e fischietto
    commissario.cex(R, frame, lid=0.2, mouth=0.1, brow=0.0, smile=0.0, look=(0, 0), pancia=1.0)

Dizionario restituito: root, head, eyeL/R, pupilL/R, lidL/R, browL/R, mouth, pancia, shoulderL/R, hipL/R."""
import math, bpy
from common import material, shape, empty
import set004
from set004 import obj

PI = math.pi
STILI = ('A', 'B', 'C')


def mats_commissario():
    M = {}
    M['skin'] = material('CM_pelle', (0.95, 0.70, 0.58), rough=0.55)
    M['cheek'] = material('CM_guance', (0.98, 0.45, 0.42), rough=0.6)
    M['nose'] = material('CM_naso', (0.95, 0.38, 0.36), rough=0.45)
    M['white'] = material('CM_bianco', (0.97, 0.96, 0.93), rough=0.2, coat=0.5)
    M['black'] = material('CM_nero', (0.02, 0.02, 0.025), rough=0.2)
    M['mouth'] = material('CM_bocca', (0.30, 0.05, 0.06), rough=0.6)
    M['baffi_A'] = material('CM_baffi_neri', (0.06, 0.04, 0.03), rough=0.7)
    M['baffi_B'] = material('CM_baffi_castani', (0.32, 0.18, 0.08), rough=0.7)
    M['baffi_C'] = material('CM_baffi_grigi', (0.62, 0.62, 0.64), rough=0.7)
    M['giacca_A'] = material('CM_giacca_blu', (0.04, 0.08, 0.25), rough=0.5)
    M['giacca_B'] = material('CM_giacca_blu_B', (0.04, 0.08, 0.25), rough=0.5)     # B: divisa blu come gli altri (scelta dell'autore)
    M['giacca_C'] = material('CM_giacca_blu2', (0.06, 0.12, 0.35), rough=0.5)
    M['camicia_A'] = material('CM_camicia_azzurra', (0.62, 0.78, 0.95), rough=0.55)
    M['camicia_B'] = material('CM_camicia_azzurra_B', (0.62, 0.78, 0.95), rough=0.55)
    M['camicia_C'] = material('CM_camicia_bianca', (0.95, 0.95, 0.97), rough=0.55)
    M['gold'] = material('CM_oro', (1.0, 0.76, 0.25), rough=0.25, metallic=1.0)
    M['silver'] = material('CM_argento', (0.85, 0.86, 0.9), rough=0.15, metallic=1.0)
    M['belt'] = material('CM_cintura', (0.04, 0.03, 0.03), rough=0.35, coat=0.4)
    M['shoe'] = material('CM_scarpe', (0.03, 0.03, 0.035), rough=0.2, coat=0.8)
    M['red'] = material('CM_rosso', (0.85, 0.08, 0.08), rough=0.4)
    return M


def commissario(coll, M, stile='A'):
    assert stile in STILI, stile
    R = {}
    r = R['root'] = empty('Commissario', (0, 0, 0), None, coll)
    S = lambda *a, **k: shape(*a, coll=coll, **k)
    box = set004.box_c()
    gia, cam, baf = M['giacca_' + stile], M['camicia_' + stile], M['baffi_' + stile]

    # ---- gambe corte, scarpe lucide
    for nm, sx in (('L', -1), ('R', 1)):
        hp = R['hip' + nm] = empty('CM_hip' + nm, (sx * 0.17, 0.0, 0.52), r, coll)
        S('CM_Gamba', 'cap:0.11:0.42', (0, 0, -0.18), parent=hp, mat=gia)
        obj('CM_Scarpa', box, (0, -0.06, -0.48), (0.16, 0.30, 0.09), M['shoe'], coll, parent=hp)
        S('CM_PuntaScarpa', 'sphere', (0, -0.20, -0.48), scale=(0.08, 0.08, 0.05), parent=hp, mat=M['shoe'])
    # ---- il pancione (si gonfia e si sgonfia): camicia tirata, bottoni che stanno per saltare, cintura sotto
    p = R['pancia'] = empty('CM_Pancia', (0, -0.04, 0.92), r, coll)
    S('CM_Panciona', 'sphere', (0, 0, 0), scale=(0.50, 0.50, 0.44), parent=p, mat=cam)
    for k, z in enumerate((0.26, 0.10, -0.06, -0.22)):
        S('CM_Bottone', 'sphere', (0, -0.5 * math.sqrt(max(0.0, 1 - (z / 0.44) ** 2)) - 0.005, z), scale=(0.028, 0.012, 0.028), parent=p, mat=M['white'])
    S('CM_Ombelico', 'sphere', (0.0, -0.47, -0.02), scale=(0.02, 0.01, 0.012), parent=p, mat=M['mouth'])   # spunta tra due bottoni
    S('CM_Cintura', 'cyl:1:1', (0, 0, -0.30), scale=(0.44, 0.44, 0.045), parent=p, mat=M['belt'])
    obj('CM_Fibbia', box, (0, -0.44, -0.30), (0.10, 0.02, 0.07), M['silver'], coll, parent=p)
    # giacca aperta ai lati della pancia
    for sx in (-1, 1):
        S('CM_Falda', 'sphere', (sx * 0.38, 0.02, 0.98), scale=(0.18, 0.40, 0.36), parent=r, mat=gia)
    S('CM_Petto', 'sphere', (0, 0.0, 1.30), scale=(0.42, 0.33, 0.24), parent=r, mat=gia)
    S('CM_Colletto', 'cyl:1:1', (0, 0.0, 1.47), scale=(0.15, 0.14, 0.05), parent=r, mat=cam)
    obj('CM_Cravatta', box, (0, -0.33, 1.32), (0.07, 0.02, 0.18), gia, coll, rot=(0.15, 0, 0), parent=r)
    # distintivo e mostrine (inventati: una stella d'oro)
    for k in range(5):
        a = PI / 2 + 2 * PI * k / 5
        S('CM_Stella', 'cone', (-0.20 + 0.035 * math.cos(a), -0.33, 1.34 + 0.035 * math.sin(a)), scale=(0.018, 0.018, 0.035), rot=(PI / 2, 0, a - PI / 2), parent=r, mat=M['gold'])
    S('CM_StellaCentro', 'sphere', (-0.20, -0.335, 1.34), scale=(0.025, 0.01, 0.025), parent=r, mat=M['gold'])
    for sx in (-1, 1):
        obj('CM_Spallina', box, (sx * 0.34, 0.0, 1.47), (0.18, 0.12, 0.03), gia, coll, parent=r)
        S('CM_SpallinaBottone', 'sphere', (sx * 0.27, -0.03, 1.49), scale=(0.022, 0.022, 0.015), parent=r, mat=M['gold'])
    if stile == 'C':   # fischietto con la catenella
        S('CM_Fischietto', 'cyl:1:1', (0.18, -0.34, 1.20), scale=(0.025, 0.025, 0.06), rot=(PI / 2, 0, 0.3), parent=r, mat=M['silver'])
        for k in range(6):
            S('CM_Catenella', 'sphere', (0.18 - 0.02 * k, -0.33, 1.23 + 0.04 * k), scale=(0.008,) * 3, parent=r, mat=M['silver'])

    # ---- testa tonda col doppio mento
    h = R['head'] = empty('CM_Head', (0, -0.03, 1.74), r, coll)
    S('CM_Cranio', 'sphere', (0, 0, 0), scale=(0.29, 0.27, 0.29), parent=h, mat=M['skin'])
    S('CM_DoppioMento', 'sphere', (0, -0.05, -0.22), scale=(0.25, 0.21, 0.11), parent=h, mat=M['skin'])
    for sx in (-1, 1):
        S('CM_Guancia', 'sphere', (sx * 0.17, -0.18, -0.06), scale=(0.10, 0.09, 0.09), parent=h, mat=M['cheek'])
        S('CM_Orecchio', 'sphere', (sx * 0.29, 0.0, 0.0), scale=(0.05, 0.07, 0.09), parent=h, mat=M['skin'])
    S('CM_Naso', 'sphere', (0, -0.29, -0.02), scale=(0.075, 0.07, 0.065), parent=h, mat=M['nose'])
    for sx, nm in ((-1, 'L'), (1, 'R')):
        e = R['eye' + nm] = empty('CM_Occhio' + nm, (sx * 0.10, -0.235, 0.08), h, coll)
        S('CM_Bulbo', 'sphere', (0, 0, 0), scale=(0.062, 0.05, 0.07), parent=e, mat=M['white'])
        pp = R['pupil' + nm] = empty('CM_Pup' + nm, (0, 0, 0), e, coll)
        S('CM_Pupilla', 'sphere', (0, -0.048, 0), scale=(0.028, 0.012, 0.034), parent=pp, mat=M['black'])
        S('CM_Luce', 'sphere', (0.01, -0.058, 0.014), scale=(0.008, 0.004, 0.008), parent=pp, mat=M['white'])
        R['lid' + nm] = S('CM_Palpebra', 'sphere', (0, -0.003, 0.0), scale=(0.066, 0.054, 0.035), parent=e, mat=M['skin'])
        R['brow' + nm] = obj('CM_Sopracciglio', box, (sx * 0.10, -0.25, 0.19), (0.11, 0.035, 0.035), baf, coll, rot=(0, -sx * 0.1, 0), parent=h)
        if stile == 'B':   # occhiali a specchio
            S('CM_Lente', 'sphere', (sx * 0.10, -0.27, 0.08), scale=(0.08, 0.02, 0.06), parent=h, mat=M['silver'])
    if stile == 'B':
        obj('CM_Ponte', box, (0, -0.285, 0.10), (0.06, 0.01, 0.01), M['black'], coll, parent=h)
    # bocca e baffi
    R['mouth'] = S('CM_Bocca', 'sphere', (0, -0.255, -0.13), scale=(0.09, 0.04, 0.018), parent=h, mat=M['mouth'])
    if stile == 'C':   # baffi a manubrio
        for sx in (-1, 1):
            S('CM_Baffo', 'sphere', (sx * 0.08, -0.29, -0.075), scale=(0.08, 0.03, 0.025), rot=(0, sx * 0.25, 0), parent=h, mat=baf)
            S('CM_BaffoPunta', 'sphere', (sx * 0.165, -0.27, -0.035), scale=(0.025, 0.02, 0.04), rot=(0, -sx * 0.5, 0), parent=h, mat=baf)
    else:              # baffoni a spazzola
        S('CM_Baffoni', 'sphere', (0, -0.29, -0.08), scale=(0.15, 0.045, 0.04), parent=h, mat=baf)
    # ---- berretto con la visiera
    S('CM_Berretto', 'cyl:1:1', (0, 0.02, 0.24), scale=(0.27, 0.28, 0.07), rot=(-0.1, 0, 0), parent=h, mat=gia)
    S('CM_BerrettoTop', 'cyl:1:1', (0, 0.03, 0.32), scale=(0.31, 0.32, 0.03), rot=(-0.12, 0, 0), parent=h, mat=gia)
    S('CM_Fascia', 'cyl:1:1', (0, 0.02, 0.19), scale=(0.275, 0.285, 0.03), rot=(-0.1, 0, 0), parent=h, mat=M['belt'])
    obj('CM_Visiera', box, (0, -0.30, 0.17), (0.34, 0.16, 0.02), M['belt'], coll, rot=(0.3, 0, 0), parent=h)
    S('CM_Fregio', 'sphere', (0, -0.29, 0.25), scale=(0.04, 0.012, 0.035), parent=h, mat=M['gold'])

    # ---- braccia corte e grosse
    for nm, sx in (('L', -1), ('R', 1)):
        sh = R['shoulder' + nm] = empty('CM_shoulder' + nm, (sx * 0.42, 0, 1.36), r, coll)
        sh.rotation_euler = (0, -sx * 0.45, 0)
        S('CM_Braccio', 'cap:0.10:0.42', (0, 0, -0.24), parent=sh, mat=gia)
        S('CM_Polsino', 'cyl:1:1', (0, 0, -0.48), scale=(0.085, 0.085, 0.03), parent=sh, mat=cam)
        S('CM_Mano', 'sphere', (0, 0, -0.57), scale=(0.09, 0.08, 0.10), parent=sh, mat=M['skin'])
    cex(R, None)
    return R


def cex(R, f, lid=0.2, mouth=0.1, brow=0.0, smile=0.0, look=(0.0, 0.0), pancia=1.0):
    """Faccia del commissario al fotogramma f (f=None: senza chiavi). lid 0 aperti, 1 chiusi; mouth 0..1; brow > 0 arrabbiato,
    < 0 sorpreso; smile -1..1; look = (x, y); pancia = scala del pancione (1 normale, 1.4 gonfio, 0.3 sgonfio)."""
    def k(o, prop):
        if f is not None: o.keyframe_insert(prop, frame=f)
    for sx, nm in ((-1, 'L'), (1, 'R')):
        pp = R['pupil' + nm]; pp.location = (look[0] * 0.025, 0, look[1] * 0.025); k(pp, 'location')
        l = R['lid' + nm]; l.location = (0, -0.003, 0.07 * (1 - lid) - 0.005); l.scale = (0.066, 0.054, 0.03 + 0.045 * lid); k(l, 'location'); k(l, 'scale')
        b = R['brow' + nm]; b.location = (sx * 0.10, -0.25, 0.19 + 0.05 * max(0.0, -brow) - 0.02 * max(0.0, brow)); k(b, 'location')
        b.rotation_euler = (0, -sx * (0.1 + 0.45 * brow), 0); k(b, 'rotation_euler')
    m = R['mouth']; m.scale = (0.09 * (1 + 0.25 * smile - 0.3 * mouth), 0.04, 0.018 + 0.07 * mouth); m.location = (0, -0.255, -0.13 - 0.03 * mouth + 0.01 * smile)
    k(m, 'scale'); k(m, 'location')
    P = R['pancia']; P.scale = (pancia, pancia, 0.6 + 0.4 * pancia); k(P, 'scale')
