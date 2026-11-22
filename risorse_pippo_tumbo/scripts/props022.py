"""Video 022 «Il barattolo di cetriolini»: barattolo (B1/B2), cetriolino amante di Eleonora (C1/C2), elefante (E1/E2), razzo cartoon (R2;
R1 e' il razzo NASA del kit). Fronte di tutto: -Y. Gli oggetti non hanno faccia (regola dell'autore); il cetriolino e l'elefante sono personaggi."""
import math, bpy
from common import material, empty
import set004
from set004 import obj, cyl, ball_
from props019 import box, _torus, testo
PI = math.pi


def mats022():
    c = lambda n, col, **k: material('P22_' + n, col, **k); M = {}
    M['glass'] = c('glass', (0.75, 0.9, 0.85), rough=0.05, spec=1.0, coat=1.0)
    M['brine'] = c('brine', (0.75, 0.72, 0.25), rough=0.1, spec=0.8)
    M['pick'] = c('pick', (0.10, 0.30, 0.05), rough=0.45, spec=0.5); M['pick2'] = c('pick2', (0.20, 0.42, 0.08), rough=0.5)
    M['bump'] = c('bump', (0.32, 0.52, 0.14), rough=0.6)
    M['lidR'] = c('lidR', (0.75, 0.05, 0.04), rough=0.35, metallic=0.4); M['lidW'] = c('lidW', (0.95, 0.95, 0.92), rough=0.4)
    M['gold'] = c('gold', (1.0, 0.72, 0.15), rough=0.25, metallic=1.0)
    M['label'] = c('label', (1.0, 0.93, 0.7), rough=0.7); M['ink'] = c('ink', (0.1, 0.25, 0.05), rough=0.6)
    M['white'] = c('white', (1, 1, 1), rough=0.35); M['black'] = c('black', (0.015, 0.015, 0.02), rough=0.35)
    M['lip'] = c('lip', (0.55, 0.05, 0.08), rough=0.4); M['boxer'] = c('boxer', (0.98, 0.95, 0.95), rough=0.6)
    M['heart'] = c('heart', (0.9, 0.05, 0.15), rough=0.5); M['shoe'] = c('shoe', (0.2, 0.1, 0.05), rough=0.4)
    M['eleG'] = c('eleG', (0.45, 0.47, 0.52), rough=0.7); M['eleP'] = c('eleP', (0.95, 0.5, 0.65), rough=0.6)
    M['eleIn'] = c('eleIn', (0.9, 0.6, 0.65), rough=0.6); M['tusk'] = c('tusk', (0.98, 0.95, 0.85), rough=0.4)
    M['rockR'] = c('rockR', (0.75, 0.04, 0.03), rough=0.3, coat=0.5); M['rockW'] = c('rockW', (0.95, 0.95, 0.95), rough=0.3, coat=0.5)
    M['steel'] = c('steel', (0.7, 0.72, 0.76), rough=0.3, metallic=0.85); M['tape'] = c('tape', (0.6, 0.6, 0.62), rough=0.5)
    g = M['glass']; b = g.node_tree.nodes['Principled BSDF']; b.inputs['Alpha'].default_value = 0.13          # vetro: trasparente (blended)
    try: g.surface_render_method = 'BLENDED'
    except Exception: g.blend_method = 'BLEND'
    g.use_backface_culling = False
    M['glassW'] = c('glassW', (0.5, 0.8, 1.0), rough=0.05, emit=(0.4, 0.7, 1.0), emit_strength=0.4)
    return M


# ============================== barattolo ==============================
def barattolo(coll, M, stile='B1', H=0.62, font=None, pieno=True):
    """barattolo di vetro coi cetriolini, origine alla base. B1: alto, coperchio a quadretti rossi e bianchi.
    B2: tondo e panciuto, coperchio dorato, etichetta CETRIOLINI. Il coperchio e' un empty a parte (J['lid']) che si svita."""
    J = {}; r = J['root'] = empty('Barattolo' + stile, (0, 0, 0), None, coll)
    if stile == 'B1': R, h = 0.2 * H / 0.62, H * 0.86
    else: R, h = 0.26 * H / 0.62, H * 0.8
    cyl('BarVetro', R, h, (0, 0, h / 2), M['glass'], coll, parent=r)
    if stile == 'B2':
        ball_('BarPancia', 1.0, (0, 0, h * 0.45), M['glass'], coll, parent=r, sc=(R * 1.12, R * 1.12, h * 0.5))
    if pieno:
        for k in range(7):
            a = 2 * PI * k / 7 + 0.4; rr = R * 0.55
            ball_('BarCetriolino', 1.0, (rr * math.cos(a), rr * math.sin(a), h * 0.42), M['pick2'] if k % 2 else M['pick'], coll, parent=r, sc=(R * 0.22, R * 0.22, h * 0.36))
    J['lid'] = lid = empty('BarCoperchio', (0, 0, h), r, coll)
    if stile == 'B1':
        cyl('BarCoperchioBase', R * 1.06, 0.07 * H, (0, 0, 0.035 * H), M['lidW'], coll, parent=lid)
        for k in range(8):                                                                    # quadretti rossi
            a = 2 * PI * k / 8; box('BarQuadretto', (R * 0.6 * math.cos(a), R * 0.6 * math.sin(a), 0.072 * H), (R * 0.42, R * 0.42, 0.004), M['lidR'], coll, rot=(0, 0, a), parent=lid)
        ball_('BarCoperchioTop', 1.0, (0, 0, 0.07 * H), M['lidR'], coll, parent=lid, sc=(R * 0.35, R * 0.35, 0.02))
    else:
        cyl('BarCoperchioBase', R * 1.08, 0.08 * H, (0, 0, 0.04 * H), M['gold'], coll, parent=lid)
        box('BarEtichetta', (0, -R * 1.1, h * 0.5), (R * 1.5, 0.01, h * 0.38), M['label'], coll, parent=r)
        if font: testo(coll, 'BarScritta', 'CETRIOLINI', 0.06 * H / 0.62, M['ink'], (0, -R * 1.13, h * 0.5), font, parent=r, spessore=0.003)
    J['hand'] = empty('BarManina', (R * 0.6, -R * 0.75, h - 0.02), r, coll)             # indizio: una manina verde che tiene il coperchio
    ball_('BarManinaPalmo', 1.0, (0, 0, 0), M['pick'], coll, parent=J['hand'], sc=(0.03, 0.02, 0.025))
    for k in range(3): cyl('BarDito', 0.008, 0.035, (-0.015 + 0.015 * k, 0, 0.025), M['pick'], coll, parent=J['hand'])
    J['R'] = R; J['h'] = h
    return J


# ============================== cetriolino ==============================
def cetriolino(coll, M, stile='C1', H=0.45):
    """l'amante di Eleonora: cetriolino con braccia, gambe, mutande a cuori. Asse +Z, origine ai piedi, fronte -Y.
    C1: lungo, verde scuro, sopracciglia. C2: tozzo, bitorzoli grossi e baffi. Restituisce dict con root, corpo, shoulderL/R, hipL/R, eyes, pupils, mouth."""
    C = {}; r = C['root'] = empty('Cetriolino' + stile, (0, 0, 0), None, coll)
    legL = 0.16 * H / 0.45; s = H / 0.45
    R_ = 0.075 * s if stile == 'C1' else 0.11 * s; L_ = (H - legL) if stile == 'C1' else (H - legL) * 0.82
    corpo = C['corpo'] = empty('CetCorpo', (0, 0, legL), r, coll)
    ball_('CetBuccia', 1.0, (0, 0, L_ / 2), M['pick'], coll, parent=corpo, sc=(R_, R_ * 0.95, L_ / 2))
    import random
    rnd = random.Random(4 if stile == 'C1' else 9)
    for k in range(18 if stile == 'C1' else 26):                                             # bitorzoli
        a = rnd.uniform(0, 2 * PI); z = rnd.uniform(0.1, 0.9) * L_; rr = R_ * math.sqrt(max(0.05, 1 - ((z - L_ / 2) / (L_ / 2)) ** 2))
        if abs((a - 1.5 * PI + PI) % (2 * PI) - PI) < 0.75 and z > 0.5 * L_: continue           # niente bitorzoli sulla faccia
        ball_('CetBitorzolo', (0.012 if stile == 'C1' else 0.02) * s, (rr * math.cos(a), rr * math.sin(a), z), M['bump'], coll, parent=corpo)
    cyl('CetPicciolo', 0.012 * s, 0.04 * s, (0, 0, L_ + 0.015 * s), M['bump'], coll, parent=corpo)
    # mutande a cuori
    mz = 0.12 * L_
    cyl('CetMutande', R_ * 1.07, 0.16 * L_, (0, 0, mz + 0.06 * L_), M['boxer'], coll, parent=corpo)
    for k in range(6):
        a = 2 * PI * k / 6 + 0.25
        for sx in (-1, 1): ball_('CetCuore', 0.011 * s, (R_ * 1.08 * math.cos(a) + sx * 0.007 * s, R_ * 1.08 * math.sin(a), mz + 0.07 * L_ + 0.004 * s), M['heart'], coll, parent=corpo)
        box('CetCuorePunta', (R_ * 1.08 * math.cos(a), R_ * 1.08 * math.sin(a), mz + 0.07 * L_ - 0.007 * s), (0.013 * s, 0.013 * s, 0.013 * s), M['heart'], coll, rot=(0, PI / 4, a), parent=corpo)
    # occhi e bocca
    ez = 0.74 * L_; fy = -R_ * 0.92
    C['eyes'] = e = empty('CetOcchi', (0, fy, ez), corpo, coll); C['pupils'] = []
    for sx in (-1, 1):
        ball_('CetOcchio', 1.0, (sx * 0.028 * s, 0, 0), M['white'], coll, parent=e, sc=(0.026 * s, 0.016 * s, 0.032 * s))
        C['pupils'].append(ball_('CetPupilla', 1.0, (sx * 0.026 * s, -0.012 * s, -0.004 * s), M['black'], coll, parent=e, sc=(0.012 * s, 0.008 * s, 0.016 * s)))
        if stile == 'C1': box('CetCiglio', (sx * 0.03 * s, -0.005 * s, 0.045 * s), (0.04 * s, 0.008 * s, 0.01 * s), M['black'], coll, rot=(0, -sx * 0.25, 0), parent=e)
    C['mouth'] = ball_('CetBocca', 1.0, (0, fy - 0.004 * s, 0.6 * L_), M['lip'], coll, parent=corpo, sc=(0.03 * s, 0.01 * s, 0.012 * s))
    if stile == 'C2':                                                                         # baffi da seduttore
        for sx in (-1, 1): ball_('CetBaffo', 1.0, (sx * 0.03 * s, fy - 0.012 * s, 0.655 * L_), M['black'], coll, parent=corpo, sc=(0.035 * s, 0.01 * s, 0.01 * s))
    # braccia e gambe
    for sx, nm in ((-1, 'L'), (1, 'R')):
        sh = C['shoulder' + nm] = empty('CetSpalla' + nm, (sx * R_ * 0.95, 0, 0.5 * L_), corpo, coll)
        cyl('CetBraccio', 0.009 * s, 0.17 * s, (0, 0, -0.085 * s), M['pick'], coll, parent=sh)
        ball_('CetMano', 0.02 * s, (0, 0, -0.175 * s), M['pick'], coll, parent=sh)
        hp = C['hip' + nm] = empty('CetAnca' + nm, (sx * 0.03 * s, 0, legL), r, coll)
        cyl('CetGamba', 0.01 * s, legL, (0, 0, -legL / 2), M['pick'], coll, parent=hp)
        ball_('CetScarpa', 1.0, (0, -0.015 * s, -legL + 0.008 * s), M['shoe'], coll, parent=hp, sc=(0.022 * s, 0.035 * s, 0.014 * s))
    for nm in ('shoulderL', 'shoulderR', 'hipL', 'hipR'): C[nm].rotation_mode = 'XYZ'
    C['shoulderL'].rotation_euler = (0, 0, 0); C['shoulderR'].rotation_euler = (0, 0, 0)
    C['H'] = H
    return C


# ============================== elefante ==============================
def elefante(coll, M, stile='E1', H=3.6):
    """elefante cartoon nello stile di Tumbo (capsule ed ellissoidi, occhioni). Fronte -Y, origine a terra.
    E1 grigio, E2 rosa. Restituisce dict con root, body, head, trunk (lista di segmenti), legs, ears."""
    E = {}; r = E['root'] = empty('Elefante' + stile, (0, 0, 0), None, coll); s = H / 3.6
    sk = M['eleG'] if stile == 'E1' else M['eleP']
    body = E['body'] = empty('EleCorpo', (0, 0, 1.75 * s), r, coll)
    ball_('EleBusto', 1.0, (0, 0.2 * s, 0), sk, coll, parent=body, sc=(1.15 * s, 1.55 * s, 1.0 * s))
    E['legs'] = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            lg = empty('EleZampa', (sx * 0.62 * s, sy * 0.85 * s + 0.2 * s, -0.55 * s), body, coll); E['legs'].append(lg)
            cyl('EleZampaCil', 0.33 * s, 1.25 * s, (0, 0, -0.55 * s), sk, coll, parent=lg)
            cyl('EleUnghie', 0.34 * s, 0.1 * s, (0, 0, -1.13 * s), M['tusk'], coll, parent=lg)
    head = E['head'] = empty('EleTesta', (0, -1.35 * s, 0.75 * s), body, coll)
    ball_('EleCranio', 1.0, (0, 0, 0), sk, coll, parent=head, sc=(0.85 * s, 0.8 * s, 0.8 * s))
    E['ears'] = []
    for sx in (-1, 1):
        ea = empty('EleOrecchio', (sx * 0.75 * s, 0.25 * s, 0.1 * s), head, coll); ea.rotation_euler = (0, 0, sx * 0.35); E['ears'].append(ea)
        ball_('EleOrecchioEst', 1.0, (sx * 0.35 * s, 0, 0), sk, coll, parent=ea, sc=(0.55 * s, 0.08 * s, 0.7 * s))
        ball_('EleOrecchioInt', 1.0, (sx * 0.33 * s, -0.04 * s, 0), M['eleIn'], coll, parent=ea, sc=(0.42 * s, 0.06 * s, 0.55 * s))
        ball_('EleOcchio', 1.0, (sx * 0.3 * s, -0.68 * s, 0.22 * s), M['white'], coll, parent=head, sc=(0.17 * s, 0.1 * s, 0.2 * s))
        ball_('ElePupilla', 1.0, (sx * 0.28 * s, -0.77 * s, 0.2 * s), M['black'], coll, parent=head, sc=(0.08 * s, 0.04 * s, 0.1 * s))
        box('EleCiglio', (sx * 0.3 * s, -0.7 * s, 0.47 * s), (0.25 * s, 0.05 * s, 0.05 * s), M['black'], coll, rot=(0, sx * 0.2, 0), parent=head)
        tk = empty('EleZanna', (sx * 0.28 * s, -0.62 * s, -0.35 * s), head, coll); tk.rotation_euler = (-0.6, 0, 0)
        cyl('EleZannaCil', 0.06 * s, 0.45 * s, (0, 0, -0.2 * s), M['tusk'], coll, parent=tk)
    E['trunk'] = []; par = head; loc = (0, -0.72 * s, -0.15 * s)
    for k in range(6):                                                                          # proboscide a segmenti (si puo' animare)
        seg = empty('EleProboscide%d' % k, loc, par, coll); seg.rotation_euler = (0.18, 0, 0); E['trunk'].append(seg)
        rr = (0.2 - 0.022 * k) * s; cyl('EleProbCil', rr, 0.3 * s, (0, 0, -0.15 * s), sk, coll, parent=seg); ball_('EleProbGiunto', rr, (0, 0, 0), sk, coll, parent=seg)
        par = seg; loc = (0, 0, -0.3 * s)
    cyl('EleCoda', 0.04 * s, 0.6 * s, (0, 1.75 * s, -0.1 * s), sk, coll, rot=(0.5, 0, 0), parent=body)
    return E


# ============================== razzo cartoon ==============================
def razzo(coll, M, H=7.0):
    """razzo cartoon rosso e bianco, origine a terra, punta in alto. In cima una piattaforma per il barattolo (J['top'])."""
    Rz = {}; r = Rz['root'] = empty('Razzo', (0, 0, 0), None, coll); s = H / 7.0; R = 0.55 * s
    for k in range(5):
        cyl('RazzoFascia', R, 1.0 * s, (0, 0, 1.2 * s + k * 1.0 * s), M['rockR'] if k % 2 else M['rockW'], coll, parent=r)
    ball_('RazzoOgiva', 1.0, (0, 0, 5.7 * s), M['rockR'], coll, parent=r, sc=(R, R, 1.0 * s))
    for k in range(4):
        a = PI / 2 * k
        box('RazzoAletta', (math.cos(a) * R * 1.4, math.sin(a) * R * 1.4, 1.1 * s), (0.9 * s, 0.08 * s, 1.2 * s), M['rockR'], coll, rot=(0, 0, a), parent=r)
    cyl('RazzoUgello', R * 0.6, 0.5 * s, (0, 0, 0.45 * s), M['steel'], coll, parent=r)
    for k in range(2): cyl('RazzoOblo', 0.17 * s, 0.05 * s, (0, -R, 3.4 * s + k * 0.7 * s), M['glassW'], coll, rot=(PI / 2, 0, 0), parent=r)
    Rz['top'] = empty('RazzoCima', (0, 0, 6.55 * s), r, coll)
    cyl('RazzoPiatto', 0.3 * s, 0.06 * s, (0, 0, 0), M['steel'], coll, parent=Rz['top'])
    return Rz


def nastro(coll, M, parent, R, h):
    """nastro adesivo grigio attorno al barattolo legato al razzo (giri storti)."""
    g = empty('Nastro', (0, 0, 0), parent, coll)
    for k, (z, t) in enumerate(((0.25, 0.25), (0.6, -0.2), (0.8, 0.1))):
        cyl('NastroGiro', R * 1.03, 0.04, (0, 0, h * z), M['tape'], coll, rot=(t, 0.15 * k, 0), parent=g)
    return g
