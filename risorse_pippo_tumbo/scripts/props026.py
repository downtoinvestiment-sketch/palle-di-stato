"""Oggetti del video 026 «Tumbo fa HUSS» (copione n. 25). tumbo.py non si tocca: qui ci sono solo pezzi da agganciare alla testa di Tumbo.
- bocca_huss: bocca spalancata (si apre con la scala dell'empty restituito), tre stili: H1 tonda, H2 storta con la lingua, H3 soffio coi denti.
- occhi_giganti: occhi da meme (bianchi enormi, pupille piccole), da mettere al posto di quelli di Tumbo (nascondi_occhi).
- onda_huss: anelli dell'onda sonora (O1 azzurri trasparenti, O2 bianchi da fumetto); si allargano con la scala."""
import math
import bpy
from mathutils import Vector
from common import material, empty, shape
from set004 import ball_
import props024
PI = math.pi


def mats026():
    return {
        'gola': material('M26_gola', (0.25, 0.02, 0.04), rough=0.6),
        'lingua': material('M26_lingua', (1.0, 0.38, 0.45), rough=0.55),
        'denti': material('M26_denti', (0.98, 0.97, 0.93), rough=0.3),
        'bianco': material('M26_occhio', (1, 1, 1), rough=0.25, coat=0.6),
        'pupilla': material('M26_pupilla', (0.02, 0.015, 0.02), rough=0.15),
        'onda1': material('M26_onda1', (0.1, 0.6, 1.0), rough=0.2, emit=(0.05, 0.5, 1.0), emit_strength=1.2),
        'onda2': material('M26_onda2', (1, 1, 1), rough=0.3, emit=(1, 1, 1), emit_strength=3.0),
    }


def bocca_huss(coll, M, head, tipo='H1', nome='BoccaHuss'):
    """bocca aperta sotto il naso di Tumbo (coordinate della testa, Tumbo guarda verso -Y). Scala 0 = chiusa, 1 = spalancata."""
    O = empty(nome, (0, -0.27, -0.12), head, coll)
    if tipo == 'H1':                                                   # bocca tonda di stupore
        ball_(nome + 'Gola', 1.0, (0, -0.05, 0), M['gola'], coll, parent=O, sc=(0.075, 0.03, 0.085))
        ball_(nome + 'Lingua', 1.0, (0, -0.06, -0.05), M['lingua'], coll, parent=O, sc=(0.05, 0.025, 0.03))
    elif tipo == 'H2':                                                 # storta, lingua fuori da un lato
        g = ball_(nome + 'Gola', 1.0, (0.01, -0.05, 0), M['gola'], coll, parent=O, sc=(0.1, 0.03, 0.07)); g.rotation_euler = (0, 0.25, 0)
        l = ball_(nome + 'Lingua', 1.0, (0.06, -0.085, -0.06), M['lingua'], coll, parent=O, sc=(0.045, 0.03, 0.075)); l.rotation_euler = (0.5, -0.4, 0)
    else:                                                              # H3: soffio, bocca larga coi canini
        ball_(nome + 'Gola', 1.0, (0, -0.05, 0), M['gola'], coll, parent=O, sc=(0.12, 0.03, 0.065))
        for s in (-1, 1):
            d = shape(nome + 'Dente', 'cone', (s * 0.06, -0.075, 0.045), (0.016, 0.016, 0.035), parent=O, mat=M['denti'], coll=coll); d.rotation_euler = (PI, 0, 0)
            d2 = shape(nome + 'DenteB', 'cone', (s * 0.045, -0.075, -0.048), (0.013, 0.013, 0.028), parent=O, mat=M['denti'], coll=coll)
        ball_(nome + 'Lingua', 1.0, (0, -0.065, -0.035), M['lingua'], coll, parent=O, sc=(0.06, 0.025, 0.025))
    O.scale = (0.001,) * 3
    return O


def nascondi_occhi(T):
    """nasconde gli occhi originali di Tumbo (per gli occhi giganti)."""
    for nm in 'LR':
        for o in [T['eye' + nm]] + list(T['eye' + nm].children_recursive):
            o.hide_render = True; o.hide_viewport = True


def occhi_giganti(coll, M, head, storti=True, nome='OcchiHuss'):
    """occhi da meme: bianchi enormi che sporgono, pupille piccole che guardano in due direzioni diverse. Restituisce [occhioL, occhioR]."""
    out = []
    for s, nm in ((-1, 'L'), (1, 'R')):
        r = 0.105 if (storti and s > 0) else 0.09
        E = empty(nome + nm, (s * 0.115, -0.235, 0.085), head, coll)
        ball_(nome + 'Bianco' + nm, 1.0, (0, 0, 0), M['bianco'], coll, parent=E, sc=(r, r * 0.8, r))
        px = (0.25 * s if storti else 0.0) * r
        ball_(nome + 'Pupilla' + nm, 1.0, (px, -r * 0.78, 0.1 * r * s if storti else 0.0), M['pupilla'], coll, parent=E, sc=(r * 0.28, r * 0.12, r * 0.28))
        out.append(E)
    return out


def onda_huss(coll, M, tipo='O1', n=3, nome='OndaHuss'):
    """anelli concentrici verticali (asse Y) che partono dalla bocca: si allargano con la scala del root e si spengono."""
    O = empty(nome, (0, 0, 0), None, coll)
    m = M['onda1'] if tipo == 'O1' else M['onda2']
    for k in range(n):
        R = 1.0 + 0.45 * k
        a = props024.anello(nome + 'Anello%d' % k, R, 0.03 if tipo == 'O1' else 0.05, m, coll, parent=O, loc=(0, -0.15 * k, 0), seg=64, segr=8)
        a.rotation_euler = (PI / 2, 0, 0)
    return O


# ======================= pezzi del video 026 =======================
import props023, props025
from set004 import obj, box_c


def occhiaie(coll, head, nome='Occhiaie'):
    """occhiaie viola sotto gli occhi di Pippo (coordinate della testa di pippo.py: occhi a (±0.127, -0.272, 0.315))."""
    m = material('M26_occhiaie', (0.32, 0.16, 0.36), rough=0.8)
    out = []
    for s in (-1, 1):
        o = ball_(nome + ('L' if s < 0 else 'R'), 1.0, (s * 0.127, -0.29, 0.168), m, coll, parent=head, sc=(0.072, 0.02, 0.02)); o.rotation_euler = (0.3, 0, -s * 0.12); out.append(o)
    return out


def telecomando(coll, nome='Telecomando'):
    """telecomando nero con i tasti colorati (lungo l'asse Y, tasti verso +Z)."""
    O = empty(nome, (0, 0, 0), None, coll)
    obj(nome + 'Corpo', box_c(), (0, 0, 0), (0.055, 0.2, 0.022), material('M26_tele', (0.03, 0.03, 0.035), rough=0.4), coll, parent=O)
    cols = [(0.9, 0.1, 0.1), (0.1, 0.7, 0.2), (0.95, 0.8, 0.1), (0.15, 0.35, 0.95)]
    for i in range(8):
        c = cols[i % 4] if i < 4 else (0.6, 0.6, 0.62)
        ball_(nome + 'Tasto', 1.0, ((-0.012 if i % 2 else 0.012), -0.06 + 0.022 * (i // 2), 0.012), material('M26_tasto%d' % (i if i < 4 else 9), c, rough=0.5), coll, parent=O, sc=(0.008, 0.008, 0.004))
    return O


def sveglia(coll, font, nome='Sveglia'):
    """sveglia digitale nera che segna 3:00 (rosso acceso). Faccia verso -Y, appoggiata a z=0."""
    O = empty(nome, (0, 0, 0), None, coll)
    obj(nome + 'Corpo', box_c(), (0, 0, 0.065), (0.24, 0.09, 0.13), material('M26_sveglia', (0.05, 0.05, 0.06), rough=0.35), coll, parent=O)
    obj(nome + 'Vetro', box_c(), (0, -0.046, 0.067), (0.2, 0.004, 0.09), material('M26_display', (0.01, 0.0, 0.0), rough=0.1), coll, parent=O)
    props023.testo(coll, nome + 'Ore', '3:00', 0.075, material('M26_led', (1, 0.05, 0.03), rough=0.3, emit=(1.0, 0.06, 0.03), emit_strength=6.0), (0, -0.05, 0.04), parent=O, font=font, estrudi=0.001)
    return O


def calendario(coll, font, numeri=('1', '7', '30'), nome='Calendario'):
    """calendario da muro (faccia verso -Y, centro all'origine): striscia rossa NOTTE e un numero grosso per ogni foglio.
    Restituisce (root, {numero: oggetto del numero})."""
    O = empty(nome, (0, 0, 0), None, coll)
    obj(nome + 'Foglio', box_c(), (0, 0, 0), (0.46, 0.012, 0.6), material('M26_carta_cal', (0.98, 0.97, 0.93), rough=0.8), coll, parent=O)
    obj(nome + 'Testata', box_c(), (0, -0.004, 0.24), (0.46, 0.012, 0.13), material('M26_rosso_cal', (0.85, 0.08, 0.06), rough=0.6), coll, parent=O)
    for s in (-1, 1): ball_(nome + 'Anello', 1.0, (s * 0.12, -0.01, 0.3), material('M26_metallo', (0.7, 0.7, 0.72), rough=0.3, metallic=1.0), coll, parent=O, sc=(0.012, 0.012, 0.03))
    props023.testo(coll, nome + 'Notte', 'NOTTE', 0.08, material('M26_bianco_cal', (1, 1, 1), rough=0.5), (0, -0.012, 0.21), parent=O, font=font, estrudi=0.002)
    nums = {}
    for n in numeri:
        e = empty(nome + 'N' + n, (0, -0.008, -0.07), O, coll)
        props023.testo(coll, nome + 'Num' + n, n, 0.3, material('M26_nero_cal', (0.04, 0.04, 0.05), rough=0.6), (0, 0, -0.11), parent=e, font=font, estrudi=0.004)
        nums[n] = e
    return O, nums


def finestre_notte(mw, picco=5.0):
    """accende le finestre a caso (per casa e per finestra) con una soglia: restituisce il nodo Valore da animare (0 tutte spente, 1 tutte accese)."""
    nt = mw.node_tree; b = nt.nodes['Principled BSDF']
    ge = nt.nodes.new('ShaderNodeNewGeometry'); nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 0.45; nz.inputs['Detail'].default_value = 0.0
    nt.links.new(ge.outputs['Position'], nz.inputs['Vector'])
    v = nt.nodes.new('ShaderNodeValue'); v.outputs[0].default_value = 0.0; v.name = 'SogliaFinestre'
    rp = nt.nodes.new('ShaderNodeMapRange'); rp.inputs['From Min'].default_value = 0.3; rp.inputs['From Max'].default_value = 0.7
    nt.links.new(nz.outputs['Fac'], rp.inputs['Value'])
    sb = nt.nodes.new('ShaderNodeMath'); sb.operation = 'SUBTRACT'; nt.links.new(v.outputs[0], sb.inputs[0]); nt.links.new(rp.outputs['Result'], sb.inputs[1])
    ml = nt.nodes.new('ShaderNodeMath'); ml.operation = 'MULTIPLY'; ml.use_clamp = True; ml.inputs[1].default_value = 25.0; nt.links.new(sb.outputs[0], ml.inputs[0])
    pk = nt.nodes.new('ShaderNodeMath'); pk.operation = 'MULTIPLY'; pk.inputs[1].default_value = picco; nt.links.new(ml.outputs[0], pk.inputs[0])
    nt.links.new(pk.outputs[0], b.inputs['Emission Strength'])
    return v


def mat_mare(nome='M26_mare'):
    m = bpy.data.materials.get(nome)
    if m: return m, m.node_tree.nodes['RumoreMare']
    m = material(nome, (0.03, 0.12, 0.22), rough=0.04, spec=0.9); nt = m.node_tree; b = nt.nodes['Principled BSDF']
    ge = nt.nodes.new('ShaderNodeNewGeometry'); mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (0.25, 0.25, 0.25)
    nt.links.new(ge.outputs['Position'], mp.inputs['Vector'])
    nz = nt.nodes.new('ShaderNodeTexNoise'); nz.name = 'RumoreMare'; nz.noise_dimensions = '4D'; nz.inputs['Scale'].default_value = 1.0; nz.inputs['Detail'].default_value = 6
    nt.links.new(mp.outputs['Vector'], nz.inputs['Vector'])
    bm = nt.nodes.new('ShaderNodeBump'); bm.inputs['Strength'].default_value = 0.6; bm.inputs['Distance'].default_value = 0.5
    nt.links.new(nz.outputs['Fac'], bm.inputs['Height']); nt.links.new(bm.outputs['Normal'], b.inputs['Normal'])
    rp = nt.nodes.new('ShaderNodeValToRGB'); rp.color_ramp.elements[0].position = 0.5; rp.color_ramp.elements[0].color = (0.02, 0.08, 0.17, 1)
    rp.color_ramp.elements[1].position = 0.75; rp.color_ramp.elements[1].color = (0.2, 0.42, 0.55, 1)
    nt.links.new(nz.outputs['Fac'], rp.inputs['Fac']); nt.links.new(rp.outputs['Color'], b.inputs['Base Color'])
    return m, nz


def mare(coll, MX, nome='Mare'):
    """il mare di notte attorno a x = MX: spiaggia (y < -22) che scende al fondale (z = -6), acqua (box, cima a z = 0 con location.z = -0.5),
    faro su uno scoglio, luna, scogli e alghe sul fondale. Restituisce dict acqua, nodo (rumore), onda (l'onda gigante), fondo."""
    O = empty(nome, (MX, 0, 0), None, coll); R = {}
    mw, nz = mat_mare(); R['nodo'] = nz
    sab = material('M26_sabbia', (0.36, 0.3, 0.21), rough=0.95); sab2 = material('M26_fondale', (0.24, 0.21, 0.16), rough=0.95)
    obj(nome + 'Spiaggia', box_c(), (MX, -71.0, -3.1), (900, 98, 7.0), sab, coll)
    r_ = obj(nome + 'Rampa', box_c(), (MX, -12.0, -2.9), (900, 21.5, 0.8), sab, coll, rot=(-0.31, 0, 0))
    obj(nome + 'Fondale', box_c(), (MX, 300.0, -6.5), (900, 610, 1.0), sab2, coll)
    R['acqua'] = obj(nome + 'Acqua', box_c(), (MX, 290.0, -0.5), (900, 600, 1.0), mw, coll)
    R['onda'] = ball_(nome + 'Onda', 1.0, (MX, 230.0, -20.0), mw, coll, sc=(260, 14, 20))
    sc_ = material('M26_scoglio', (0.22, 0.22, 0.25), rough=0.9); alga = material('M26_alga', (0.15, 0.45, 0.18), rough=0.8)
    import random; rn = random.Random(26)
    for k in range(18):
        ball_(nome + 'Sasso', 1.0, (MX + rn.uniform(-30, 30), rn.uniform(0, 60), -6.0), sc_, coll, sc=(rn.uniform(0.4, 1.6), rn.uniform(0.4, 1.4), rn.uniform(0.3, 0.9)))
    for k in range(30):
        a = shape(nome + 'Alga', 'cone', (MX + rn.uniform(-25, 25), rn.uniform(-1, 45), -5.9), (0.12, 0.12, rn.uniform(0.5, 1.3)), mat=alga, coll=coll); a.rotation_euler = (rn.uniform(-0.3, 0.3), rn.uniform(-0.3, 0.3), 0)
    # faro sullo scoglio, a destra
    FX, FY = MX + 38.0, 70.0
    ball_(nome + 'Scoglio', 1.0, (FX, FY, -2.0), sc_, coll, sc=(9, 8, 5))
    bia = material('M26_faro_b', (0.95, 0.95, 0.92), rough=0.5); ros = material('M26_faro_r', (0.8, 0.08, 0.06), rough=0.5)
    for k in range(5):
        shape(nome + 'FaroT', 'cyl:1:1', (FX, FY, 2.6 + 2.6 * k + 1.3), (1.9 - 0.12 * k, 1.9 - 0.12 * k, 1.3), mat=ros if k % 2 else bia, coll=coll)
    luce = material('M26_faro_luce', (1, 0.9, 0.5), rough=0.3, emit=(1.0, 0.85, 0.4), emit_strength=25.0)
    shape(nome + 'FaroLuce', 'cyl:1:1', (FX, FY, 16.6), (1.25, 1.25, 0.8), mat=luce, coll=coll)
    shape(nome + 'FaroTetto', 'cone', (FX, FY, 18.2), (1.5, 1.5, 0.8), mat=ros, coll=coll)
    R['luna'] = ball_(nome + 'Luna', 1.0, (MX - 70, 520, 95), material('M26_luna', (1, 0.97, 0.85), rough=0.9, emit=(1.0, 0.96, 0.82), emit_strength=6.0), coll, sc=(26, 26, 26))
    R['root'] = O
    return R


def luna(coll, pos, r, nome='Luna'):
    return ball_(nome, 1.0, pos, material('M26_luna', (1, 0.97, 0.85), rough=0.9, emit=(1.0, 0.96, 0.82), emit_strength=6.0), coll, sc=(r, r, r))


def pesce(coll, k, nome='Pesce'):
    """pesciolino arancione (muso verso -Y), da far sbattere sul fondale."""
    cols = [(1.0, 0.45, 0.05), (0.95, 0.8, 0.1), (0.2, 0.55, 0.95), (0.95, 0.3, 0.5)]
    m = material('M26_pesce%d' % (k % 4), cols[k % 4], rough=0.4, coat=0.5)
    O = empty(nome, (0, 0, 0), None, coll)
    ball_(nome + 'Corpo', 1.0, (0, 0, 0), m, coll, parent=O, sc=(0.1, 0.3, 0.17))
    c = shape(nome + 'Coda', 'cone', (0, 0.34, 0), (0.02, 0.14, 0.14), parent=O, mat=m, coll=coll); c.rotation_euler = (PI / 2, 0, 0)
    for s in (-1, 1):
        ball_(nome + 'Occhio', 1.0, (s * 0.07, -0.16, 0.05), material('M26_occhio', (1, 1, 1), rough=0.25), coll, parent=O, sc=(0.04, 0.04, 0.04))
        ball_(nome + 'Pup', 1.0, (s * 0.095, -0.17, 0.05), material('M26_pupilla', (0.02, 0.015, 0.02), rough=0.15), coll, parent=O, sc=(0.02, 0.02, 0.02))
    return O


def anello_piatto(coll, M, nome, r=0.006):
    """anello orizzontale bianco (raggio 1, da scalare uniforme)."""
    return props024.anello(nome, 1.0, r, M['onda2'], coll, seg=160, segr=8)


def mat_nero(nome='M26_nero'):
    return material(nome, (0, 0, 0), rough=1.0)
