"""Test 010 - PIPPO CONTRO GUALTIERO ep. 2: IL PROCESSO AL SOLE. Il Sole (personaggio), polizia, carcere, tribunale."""
import math, bpy
from common import material, shape, empty, shared_mesh
import set004, props004, props009
from set004 import MB, obj, cyl, ball_
from props007 import text_obj
PI = math.pi

def mats010():
    c = lambda n, col, **k: material('S10_' + n, col, **k); M = {}
    M['sun'] = c('sun', (1.0, 0.80, 0.08), rough=0.8, emit=(1.0, 0.72, 0.05), emit_strength=1.3)
    M['ray'] = c('ray', (1.0, 0.55, 0.03), rough=0.8, emit=(1.0, 0.45, 0.02), emit_strength=1.3)
    M['white'] = c('white', (1, 1, 1), rough=0.4, emit=(1, 1, 1), emit_strength=0.5); M['black'] = c('black', (0.02, 0.02, 0.03), rough=0.4)
    M['mouth'] = c('mouth', (0.35, 0.04, 0.05), rough=0.5); M['tongue'] = c('tongue', (1.0, 0.30, 0.45), rough=0.4, emit=(1.0, 0.3, 0.45), emit_strength=0.4)
    M['cheek'] = c('cheek', (1.0, 0.40, 0.25), rough=0.8, emit=(1.0, 0.35, 0.2), emit_strength=0.9)
    M['steel'] = c('steel', (0.72, 0.75, 0.80), rough=0.3, metallic=0.8); M['halo'] = c('halo', (1, 1, 0.6), rough=0.5, emit=(1, 1, 0.5), emit_strength=3.0)
    M['bed'] = c('bed', (0.10, 0.55, 0.95), rough=0.6); M['bedw'] = c('bedw', (0.97, 0.97, 0.97), rough=0.6)
    M['phone'] = c('phone', (0.06, 0.06, 0.08), rough=0.3); M['screen'] = c('screen', (0.3, 0.8, 1.0), rough=0.2, emit=(0.3, 0.8, 1.0), emit_strength=1.5)
    M['polw'] = c('polw', (0.97, 0.97, 0.97), rough=0.3, spec=0.8); M['polb'] = c('polb', (0.05, 0.20, 0.75), rough=0.3, spec=0.8)
    M['lred'] = c('lred', (1, 0.05, 0.05), rough=0.3, emit=(1, 0.05, 0.05), emit_strength=4.0); M['lblue'] = c('lblue', (0.1, 0.3, 1), rough=0.3, emit=(0.1, 0.3, 1), emit_strength=4.0)
    M['wall'] = c('wall', (0.55, 0.60, 0.66), rough=0.9); M['floor'] = c('floor', (0.36, 0.38, 0.42), rough=0.9); M['line'] = c('line', (0.10, 0.11, 0.13), rough=0.8)
    M['board'] = c('board', (0.97, 0.97, 0.95), rough=0.6)
    M['wood'] = c('wood', (0.50, 0.27, 0.11), rough=0.6); M['woodd'] = c('woodd', (0.32, 0.16, 0.06), rough=0.6); M['cwall'] = c('cwall', (0.72, 0.58, 0.38), rough=0.9)
    M['cfloor'] = c('cfloor', (0.62, 0.36, 0.20), rough=0.7); M['gold'] = c('gold', (1.0, 0.75, 0.15), rough=0.3, metallic=0.9)
    M['wig'] = c('wig', (0.96, 0.96, 0.98), rough=0.9); M['tie'] = c('tie', (0.85, 0.05, 0.10), rough=0.6); M['case'] = c('case', (0.22, 0.12, 0.06), rough=0.5)
    M['burn'] = c('burn', (1.0, 0.05, 0.02), rough=0.8, emit=(1.0, 0.05, 0.0), emit_strength=1.6)
    M['cloud'] = c('cloud', (0.45, 0.48, 0.56), rough=1.0); M['rain'] = c('rain', (0.3, 0.6, 1.0), rough=0.1, emit=(0.3, 0.6, 1.0), emit_strength=0.6)
    M['star'] = c('star', (1, 1, 1), rough=1.0, emit=(1, 1, 0.9), emit_strength=4.0); M['copskin'] = None
    return M


def sun_char(coll, M, R=0.8):
    """il Sole: disco con raggi, faccia, braccine, occhiali, manette, aureola. Fronte -Y, origine al centro."""
    S = {}; r = S['root'] = empty('Sole', (0, 0, 0), None, coll); E = lambda n, loc, par=None: empty(n, loc, par or r, coll)
    ball_('SoleDisco', R, (0, 0, 0), M['sun'], coll, parent=r, sc=(1, 0.42, 1))
    rays = S['rays'] = E('SoleRaggi', (0, 0.05, 0))
    for k in range(12):
        a = 2 * PI * k / 12; shape('SoleRaggio', 'cone', (1.22 * R * math.cos(a), 0, 1.22 * R * math.sin(a)), scale=(0.17 * R, 0.10 * R, 0.42 * R), rot=(0, PI / 2 - a, 0), parent=rays, mat=M['ray'], coll=coll)
    f = -0.33 * R
    for sx, nm in ((-1, 'L'), (1, 'R')):
        S['eye' + nm] = ball_('SoleOcchio', 0.16 * R, (sx * 0.30 * R, f, 0.20 * R), M['white'], coll, parent=r, sc=(1, 0.5, 1.15))
        S['pupil' + nm] = ball_('SolePupilla', 0.07 * R, (sx * 0.30 * R, f - 0.07 * R, 0.19 * R), M['black'], coll, parent=r, sc=(1, 0.5, 1.15))
        S['brow' + nm] = obj('SoleSopracciglio', set004.box_c(), (sx * 0.30 * R, f - 0.04 * R, 0.46 * R), (0.30 * R, 0.05 * R, 0.07 * R), M['black'], coll, parent=r)
        ball_('SoleGuancia', 0.11 * R, (sx * 0.52 * R, f + 0.03 * R, -0.08 * R), M['cheek'], coll, parent=r, sc=(1, 0.4, 0.7))
        sh = S['shoulder' + nm] = E('SoleSpalla' + nm, (sx * 0.86 * R, -0.12 * R, -0.25 * R)); sh.rotation_mode = 'QUATERNION'
        cyl('SoleBraccio', 0.06 * R, 0.55 * R, (0, 0, -0.275 * R), M['ray'], coll, parent=sh); ball_('SoleMano', 0.12 * R, (0, 0, -0.60 * R), M['sun'], coll, parent=sh)
    S['mouth'] = ball_('SoleBocca', 1.0, (0, f - 0.03 * R, -0.22 * R), M['mouth'], coll, parent=r, sc=(0.2 * R, 0.05 * R, 0.06 * R))
    S['tongue'] = ball_('SoleLingua', 1.0, (0, f - 0.08 * R, -0.34 * R), M['tongue'], coll, parent=r, sc=(0.001, 0.001, 0.001))
    g = S['glasses'] = E('SoleOcchiali', (0, f - 0.11 * R, 0.20 * R))
    for sx in (-1, 1): obj('Lente', set004.box_c(), (sx * 0.30 * R, 0, 0), (0.46 * R, 0.05 * R, 0.30 * R), M['black'], coll, parent=g)
    obj('Ponte', set004.box_c(), (0, 0, 0.06 * R), (0.2 * R, 0.04 * R, 0.05 * R), M['black'], coll, parent=g)
    c = S['cuffs'] = E('Manette', (0, -0.62 * R, -0.50 * R))
    for sx in (-1, 1): cyl('Anello', 0.15 * R, 0.07 * R, (sx * 0.17 * R, 0, 0), M['steel'], coll, rot=(PI / 2, 0, 0), parent=c)
    obj('Catena', set004.box_c(), (0, 0, 0), (0.16 * R, 0.04 * R, 0.04 * R), M['steel'], coll, parent=c)
    h = S['halo'] = E('Aureola', (0, -0.1, 1.40 * R))
    for k in range(14):
        a = 2 * PI * k / 14; ball_('AureolaP', 0.07 * R, (0.42 * R * math.cos(a), 0.2 * R * math.sin(a), 0), M['halo'], coll, parent=h)
    S['R'] = R
    return S

def sex(S, f, brow=0.0, mouth=0.3, tongue=0.0, look=(0, 0), eye=1.0):
    """brow>0 cattivo, <0 triste/spaventato; mouth 0..1 (aperta); eye = scala degli occhi."""
    R = S['R']; fy = -0.33 * R
    for sx, nm in ((-1, 'L'), (1, 'R')):
        b = S['brow' + nm]; b.rotation_euler = (0, -sx * brow * 0.5, 0); b.location = (sx * 0.30 * R, fy - 0.04 * R, (0.46 + 0.06 * (eye - 1) - 0.05 * abs(brow)) * R)
        b.keyframe_insert('rotation_euler', frame=f); b.keyframe_insert('location', frame=f)
        p = S['pupil' + nm]; p.location = (sx * 0.30 * R + look[0] * 0.06 * R, fy - 0.07 * R, 0.19 * R + look[1] * 0.07 * R); p.keyframe_insert('location', frame=f)
        e = S['eye' + nm]; e.scale = (0.16 * R * eye, 0.08 * R, 0.184 * R * eye); e.keyframe_insert('scale', frame=f)
    m = S['mouth']; m.scale = ((0.2 + 0.06 * mouth) * R, 0.05 * R, (0.05 + 0.2 * mouth) * R); m.keyframe_insert('scale', frame=f)
    t = S['tongue']; t.scale = (0.001,) * 3 if tongue <= 0.01 else (0.11 * R, 0.05 * R, (0.08 + 0.16 * tongue) * R); t.keyframe_insert('scale', frame=f)


def sunbed(coll, M):
    """sdraio lungo X: testa a -X. Origine a terra, ai piedi (+X)."""
    mb = MB([M['bed'], M['bedw']])
    mb.b2((-1.25, -0.36, 0.30), (0.0, 0.36, 0.38), 0)
    for i in range(5): mb.b2((-1.25 + 0.25 * i, -0.36, 0.381), (-1.13 + 0.25 * i, 0.36, 0.385), 1)
    for x in (-1.15, -0.1):
        for y in (-0.30, 0.30): mb.box((x, y, 0.15), (0.06, 0.06, 0.30), 1)
    o = mb.build('Sdraio', coll); mb2 = MB([M['bed'], M['bedw']]); mb2.b2((-0.95, -0.36, 0.0), (0.0, 0.36, 0.08), 0)
    for i in range(4): mb2.b2((-0.95 + 0.25 * i, -0.36, 0.081), (-0.83 + 0.25 * i, 0.36, 0.085), 1)
    b = mb2.build('SdraioSchienale', coll); b.parent = o; b.location = (-1.25, 0, 0.30); b.rotation_euler = (0, 0.67, 0)
    return o

def phone(coll, M, sh):
    g = empty('Telefono', (0, -0.05, -0.74), sh, coll)
    obj('TelCorpo', set004.box_c(), (0, 0, 0), (0.13, 0.03, 0.24), M['phone'], coll, parent=g); obj('TelSchermo', set004.box_c(), (0, -0.017, 0), (0.11, 0.005, 0.20), M['screen'], coll, parent=g)
    return g

def police_car(coll, M, G9):
    m = dict(G9); m['car'] = M['polw']; r = props009.car(coll, m)
    for sx in (-1, 1): obj('PolFascia', set004.box_c(), (sx * 0.856, 0, 0.62), (0.02, 3.2, 0.22), M['polb'], coll, parent=r)
    obj('PolCofano', set004.box_c(), (0, -1.5, 0.905), (1.2, 0.7, 0.02), M['polb'], coll, parent=r)
    obj('PolBarra', set004.box_c(), (0, 0.25, 1.48), (1.0, 0.22, 0.06), M['line'], coll, parent=r)
    lr = obj('PolLuceR', set004.box_c(), (-0.27, 0.25, 1.56), (0.42, 0.20, 0.13), M['lred'], coll, parent=r); lb = obj('PolLuceB', set004.box_c(), (0.27, 0.25, 1.56), (0.42, 0.20, 0.13), M['lblue'], coll, parent=r)
    return r, lr, lb

def cop(coll, name='Agente'):
    R = props004.player(coll, name, (0.08, 0.20, 0.60), (0.05, 0.10, 0.30), (0.95, 0.62, 0.45), (0.15, 0.10, 0.06), scale=1.0)
    head = [c for c in R['root'].children if c.name.startswith('Head')][0]; mc = material('S10_copcap', (0.05, 0.12, 0.40), rough=0.6)
    cyl('AgBerretto', 0.29, 0.14, (0, 0.02, 0.27), mc, coll, parent=head); obj('AgVisiera', set004.box_c(), (0, -0.28, 0.21), (0.40, 0.22, 0.03), material('S10_copvis', (0.02, 0.02, 0.03), rough=0.3), coll, parent=head)
    ball_('AgStemma', 0.05, (0, -0.29, 0.29), material('S10_copbadge', (1.0, 0.8, 0.1), rough=0.3, metallic=0.9), coll, parent=head)
    R['head'] = head; return R

def ext_ladder(coll, M, L):
    """scala lungo +Z dall'origine (si allunga scalando Z)."""
    mb = MB([M['steel']])
    for s in (-1, 1): mb.box((s * 0.28, 0, L / 2), (0.07, 0.07, L), 0)
    z = 0.3
    while z < L - 0.1: mb.box((0, 0, z), (0.56, 0.05, 0.05), 0); z += 0.4
    return mb.build('ScalaPolizia', coll)

def jail_set(coll, M, x0, label='SOLE  N. 0001', sub='USTIONI AGGRAVATE'):
    """parete con righe d'altezza + pavimento; restituisce (sbarre, cartello)."""
    mb = MB([M['wall'], M['floor'], M['line']])
    mb.b2((x0 - 20, 2.0, 0), (x0 + 20, 2.4, 16), 0); mb.b2((x0 - 20, -16, -0.2), (x0 + 20, 2.0, 0), 1)
    for k in range(1, 16): mb.b2((x0 - 3.2, 1.97, 0.5 * k), (x0 + (3.2 if k % 2 == 0 else -2.2), 2.0, 0.5 * k + (0.05 if k % 2 == 0 else 0.03)), 2)
    mb.build('Carcere', coll)
    bb = MB([M['steel']])
    x = -4.2
    while x <= 4.21: bb.box((x, 0, 3.0), (0.09, 0.09, 6.0), 0); x += 0.42
    for z in (0.06, 2.6, 5.9): bb.box((0, 0, z), (8.6, 0.12, 0.12), 0)
    bars = bb.build('Sbarre', coll)
    board = empty('Cartello', (0, 0, 0), None, coll); obj('CartelloTav', set004.box_c(), (0, 0, 0), (1.25, 0.04, 0.50), M['board'], coll, parent=board)
    text_obj(coll, 'CartelloTxt', label, 0.17, M['line'], (0, -0.025, 0.08), parent=board); text_obj(coll, 'CartelloTxt2', sub, 0.095, M['line'], (0, -0.025, -0.12), parent=board)
    return bars, board

def court_set(coll, M, x0, motto2='(TRANNE PER IL SOLE)'):
    """tribunale: parete, pavimento, banco del giudice (piano a z=1.55), gabbia dell'imputato a sinistra. Restituisce sbarre della gabbia."""
    mb = MB([M['cwall'], M['cfloor'], M['wood'], M['woodd'], M['gold']])
    mb.b2((x0 - 20, 5.0, 0), (x0 + 20, 5.4, 16), 0); mb.b2((x0 - 20, -16, -0.2), (x0 + 20, 5.0, 0), 1)
    mb.b2((x0 - 20, 4.95, 0), (x0 + 20, 5.0, 2.2), 2); mb.b2((x0 - 20, 4.93, 2.2), (x0 + 20, 5.0, 2.32), 3)
    mb.b2((x0 - 1.7, 2.3, 0), (x0 + 1.7, 3.9, 1.45), 2); mb.b2((x0 - 1.85, 2.2, 1.45), (x0 + 1.85, 4.0, 1.55), 3); mb.b2((x0 - 1.3, 2.27, 0.25), (x0 + 1.3, 2.3, 1.2), 3)
    mb.b2((x0 - 0.45, 2.24, 0.5), (x0 + 0.45, 2.27, 0.95), 4)
    for sx in (1,): mb.b2((x0 + sx * 2.4 - 0.9, -0.2, 0), (x0 + sx * 2.4 + 0.9, 0.35, 0.95), 2); mb.b2((x0 + sx * 2.4 - 1.0, -0.3, 0.95), (x0 + sx * 2.4 + 1.0, 0.45, 1.03), 3)
    for sx in (-1, 1):
        for k in range(7): mb.b2((x0 + sx * 6.0 - 0.1, 4.6, 0), (x0 + sx * 6.0 + 0.1, 4.95, 9.0), 3)
    mb.build('Tribunale', coll)
    text_obj(coll, 'Motto', 'LA LEGGE È UGUALE PER TUTTI', 0.42, M['woodd'], (x0, 4.9, 3.75))
    text_obj(coll, 'Motto2', motto2, 0.26, M['woodd'], (x0, 4.9, 3.25))
    return None

def cage(coll, M, w=2.6, h=3.4):
    """gabbia dell'imputato: origine a terra al centro, sbarre davanti e ai lati."""
    mb = MB([M['steel'], M['woodd']])
    x = -w / 2
    while x <= w / 2 + 0.01: mb.box((x, -0.9, h / 2), (0.07, 0.07, h), 0); x += 0.37
    for y in (-0.5, -0.1, 0.3, 0.7):
        for sx in (-1, 1): mb.box((sx * w / 2, y, h / 2), (0.07, 0.07, h), 0)
    mb.b2((-w / 2 - 0.06, -0.96, 0), (w / 2 + 0.06, 0.8, 0.10), 1); mb.b2((-w / 2 - 0.06, -0.96, h), (w / 2 + 0.06, 0.8, h + 0.10), 1)
    return mb.build('Gabbia', coll)

def wig(coll, M, head, c=(0, 0.02, 0.22), s=1.0):
    g = empty('Parrucca', c, head, coll)
    ball_('ParrTop', 0.19 * s, (0, 0, 0.02), M['wig'], coll, parent=g, sc=(1.1, 1.0, 0.7))
    for sx in (-1, 1):
        for k in range(3): ball_('ParrRiccio', 0.085 * s, (sx * (0.19 + 0.01 * k) * s, 0.02, (-0.06 - 0.12 * k) * s), M['wig'], coll, parent=g)
    return g

def gavel(coll, M, parent, loc):
    """martelletto: perno all'impugnatura, manico lungo +Z."""
    g = empty('Martelletto', loc, parent, coll)
    cyl('MartManico', 0.025, 0.42, (0, 0, 0.21), M['woodd'], coll, parent=g); cyl('MartTesta', 0.075, 0.24, (0, 0, 0.44), M['wood'], coll, rot=(PI / 2, 0, 0), parent=g)
    return g

def tie(coll, M, root):
    g = empty('Cravatta', (0, -0.385, 1.33), root, coll)
    obj('CravNodo', set004.box_c(), (0, 0, 0), (0.09, 0.05, 0.08), M['tie'], coll, parent=g); obj('CravPala', set004.box_c(), (0, -0.045, -0.21), (0.11, 0.03, 0.36), M['tie'], coll, rot=(0.25, 0, 0), parent=g)
    return g

def briefcase(coll, M, sh):
    g = empty('Valigetta', (0, 0, -0.80), sh, coll)
    obj('ValCorpo', set004.box_c(), (0, 0, -0.14), (0.46, 0.12, 0.32), M['case'], coll, parent=g); obj('ValManico', set004.box_c(), (0, 0, 0.05), (0.16, 0.03, 0.05), M['line'], coll, parent=g)
    obj('ValFibbia', set004.box_c(), (0, -0.062, -0.05), (0.07, 0.01, 0.05), M['gold'], coll, parent=g)
    return g

def raincloud(coll, M):
    r = empty('Nuvola', (0, 0, 0), None, coll)
    for (dx, dz, s) in ((0, 0, 0.55), (0.55, -0.05, 0.42), (-0.55, -0.05, 0.44), (0.25, 0.25, 0.42), (-0.25, 0.22, 0.4), (0.95, -0.12, 0.28), (-0.98, -0.12, 0.3)):
        ball_('NuvolaP', s, (dx, 0, dz), M['cloud'], coll, parent=r, sc=(1, 0.8, 0.8))
    for sx in (-1, 1):
        ball_('NuvOcchio', 0.10, (sx * 0.2, -0.42, 0.05), M['white'], coll, parent=r, sc=(1, 0.5, 1.2)); ball_('NuvPupilla', 0.045, (sx * 0.2, -0.47, 0.02), M['black'], coll, parent=r)
        obj('NuvSopr', set004.box_c(), (sx * 0.2, -0.45, 0.21), (0.2, 0.04, 0.05), M['black'], coll, rot=(0, -sx * 0.45, 0), parent=r)
    ball_('NuvBocca', 1.0, (0, -0.44, -0.17), M['mouth'], coll, parent=r, sc=(0.14, 0.04, 0.05))
    return r
