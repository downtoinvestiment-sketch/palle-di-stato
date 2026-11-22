"""Video 019 «Il doppio gioco»: bombe atomiche con la faccia, carro armato, piscina gonfiabile e sottomarino,
armeria del prete «ARMI BENEDETTE», bombine gemelle con il naso di Giulia.
Ogni oggetto ha due stili (lettere della scheda019): bomba A/B, carro C/D, sottomarino E/F, armeria G/H.
Fronte di tutti gli oggetti: -Y. Le bombe volano lungo +X (punta in +X)."""
import math, bpy, bmesh
from mathutils import Vector
from common import material, empty, shared_mesh
import set004
from set004 import obj, cyl, ball_
from props007 import text_obj
PI = math.pi


def mats019():
    c = lambda n, col, **k: material('P19_' + n, col, **k); M = {}
    M['white'] = c('white', (1, 1, 1), rough=0.35); M['black'] = c('black', (0.015, 0.015, 0.02), rough=0.35)
    M['pink'] = c('pink', (0.95, 0.25, 0.35), rough=0.4); M['tongue'] = c('tongue', (0.85, 0.12, 0.18), rough=0.4)
    # bombe
    M['bombA'] = c('bombA', (0.20, 0.27, 0.22), rough=0.35, metallic=0.4, spec=0.7)       # verde oliva lucido
    M['bombB'] = c('bombB', (0.62, 0.52, 0.12), rough=0.35, metallic=0.4, spec=0.7)       # giallo senape (Fat Man)
    M['byel'] = c('byel', (1.0, 0.78, 0.04), rough=0.45); M['bred'] = c('bred', (0.85, 0.05, 0.04), rough=0.4)
    M['bblue'] = c('bblue', (0.05, 0.25, 0.85), rough=0.4); M['bgreen'] = c('bgreen', (0.10, 0.55, 0.12), rough=0.4)
    M['steel'] = c('steel', (0.70, 0.72, 0.76), rough=0.3, metallic=0.85); M['dark'] = c('dark', (0.10, 0.10, 0.11), rough=0.5, metallic=0.4)
    M['flame'] = c('flame', (1.0, 0.5, 0.05), rough=1.0, emit=(1.0, 0.45, 0.05), emit_strength=6.0)
    M['flag'] = c('flag', (1.0, 0.97, 0.9), rough=0.8)
    # carro
    M['army'] = c('army', (0.12, 0.19, 0.05), rough=0.55, spec=0.4); M['army2'] = c('army2', (0.2, 0.27, 0.09), rough=0.55)
    M['toyR'] = c('toyR', (0.62, 0.02, 0.01), rough=0.3, spec=0.8, coat=0.5); M['toyY'] = c('toyY', (0.95, 0.55, 0.01), rough=0.3, coat=0.5)
    M['toyB'] = c('toyB', (0.01, 0.12, 0.65), rough=0.3, coat=0.5); M['rubber'] = c('rubber', (0.05, 0.05, 0.055), rough=0.85)
    # piscina e sottomarino
    M['poolB'] = c('poolB', (0.05, 0.45, 0.95), rough=0.25, spec=0.9, coat=0.8); M['poolW'] = c('poolW', (0.97, 0.97, 1.0), rough=0.25, coat=0.8)
    M['water'] = c('water', (0.10, 0.55, 0.75), rough=0.05, spec=1.0)
    M['subY'] = c('subY', (0.95, 0.5, 0.0), rough=0.3, spec=0.7, coat=0.4); M['subG'] = c('subG', (0.10, 0.12, 0.14), rough=0.5, metallic=0.3)
    M['glass'] = c('glass', (0.55, 0.85, 1.0), rough=0.05, spec=1.0, emit=(0.4, 0.7, 1.0), emit_strength=0.3)
    # armeria
    M['wood'] = c('wood', (0.25, 0.11, 0.04), rough=0.55); M['wood2'] = c('wood2', (0.28, 0.14, 0.05), rough=0.6)
    M['gold'] = c('gold', (1.0, 0.72, 0.15), rough=0.25, metallic=1.0); M['neon'] = c('neon', (1.0, 0.25, 0.15), rough=0.5, emit=(1.0, 0.2, 0.1), emit_strength=8.0)
    M['neonW'] = c('neonW', (1, 0.95, 0.8), rough=0.5, emit=(1.0, 0.92, 0.7), emit_strength=10.0)
    M['money'] = c('money', (0.35, 0.70, 0.35), rough=0.8); M['paper'] = c('paper', (0.98, 0.97, 0.92), rough=0.8)
    M['wallG'] = c('wallG', (0.55, 0.42, 0.30), rough=0.9); M['wallH'] = c('wallH', (0.95, 0.85, 0.20), rough=0.8)
    M['mint'] = c('mint', (0.20, 0.85, 0.75), rough=0.3, coat=0.5); M['purple'] = c('purple', (0.50, 0.15, 0.85), rough=0.3, coat=0.5)
    return M


def box(name, loc, size, mat, coll, rot=(0, 0, 0), parent=None):
    return obj(name, set004.box_c(), loc, size, mat, coll, rot=rot, parent=parent)


def _torus(name, R, r, mat, coll, parent=None, loc=(0, 0, 0), seg=48, sec=16):
    key = 'p19tor:%g:%g' % (R, r)
    me = bpy.data.meshes.get(key)
    if me is None:
        bm = bmesh.new(); vs = []
        for i in range(seg):
            a = 2 * PI * i / seg; row = []
            for j in range(sec):
                b = 2 * PI * j / sec
                row.append(bm.verts.new(((R + r * math.cos(b)) * math.cos(a), (R + r * math.cos(b)) * math.sin(a), r * math.sin(b))))
            vs.append(row)
        for i in range(seg):
            for j in range(sec):
                bm.faces.new((vs[i][j], vs[(i + 1) % seg][j], vs[(i + 1) % seg][(j + 1) % sec], vs[i][(j + 1) % sec]))
        me = bpy.data.meshes.new(key); bm.to_mesh(me); bm.free()
        for p in me.polygons: p.use_smooth = True
        me.materials.append(None)
    return obj(name, me, loc, (1, 1, 1), mat, coll, parent=parent)


def testo(coll, name, body, size, mat, loc, font=None, parent=None, rot=(PI / 2, 0, 0), spessore=0.02):
    o = text_obj(coll, name, body, size, mat, loc, rot=rot, parent=parent)
    o.data.extrude = spessore
    if font:
        fo = bpy.data.fonts.get(font) or bpy.data.fonts.load(font, check_existing=True); o.data.font = fo
    return o


# ============================== faccia cartoon ==============================
def faccia(coll, M, parent, loc, s=1.0, verso=(0, -1, 0), nome='Faccia'):
    """occhioni e bocca su una superficie che guarda 'verso'. Restituisce dict con eyes, pupils, brows, mouth, smile."""
    f = empty(nome, loc, parent, coll)
    v = Vector(verso).normalized(); f.rotation_euler = (-math.asin(max(-1.0, min(1.0, v.z))), 0, math.atan2(v.x, -v.y))
    F = {'root': f, 'pupils': [], 'brows': [], 'eyes': []}
    for sx in (-1, 1):
        e = ball_(nome + 'Occhio', 1.0, (sx * 0.17 * s, 0, 0.08 * s), M['white'], coll, parent=f, sc=(0.14 * s, 0.07 * s, 0.17 * s)); F['eyes'].append(e)
        F['pupils'].append(ball_(nome + 'Pupilla', 1.0, (sx * 0.15 * s, -0.065 * s, 0.07 * s), M['black'], coll, parent=f, sc=(0.06 * s, 0.03 * s, 0.08 * s)))
        ball_(nome + 'Luce', 1.0, (sx * 0.13 * s, -0.09 * s, 0.11 * s), M['white'], coll, parent=f, sc=(0.02 * s, 0.01 * s, 0.025 * s))
        F['brows'].append(box(nome + 'Ciglio', (sx * 0.17 * s, -0.03 * s, 0.31 * s), (0.2 * s, 0.04 * s, 0.045 * s), M['black'], coll, rot=(0, sx * 0.15, 0), parent=f))
    F['mouth'] = ball_(nome + 'Bocca', 1.0, (0, -0.01 * s, -0.18 * s), M['black'], coll, parent=f, sc=(0.16 * s, 0.05 * s, 0.07 * s))
    F['tongue'] = ball_(nome + 'Lingua', 1.0, (0, -0.04 * s, -0.21 * s), M['tongue'], coll, parent=f, sc=(0.08 * s, 0.03 * s, 0.035 * s))
    return F


# ============================== bombe ==============================
def bomba(coll, M, stile='A', proprietario='PIPPO', font=None, L=4.2, lato=-1, con_faccia=False):
    """bomba atomica con la faccia: punta verso +X, origine al centro, lunga circa L.
    A: lunga e affusolata (alette e anello in coda). B: tonda e grassa (coda a scatola).
    Bandierina col nome del proprietario sulla coda; fascia blu per Pippo, verde per Gualtiero.
    lato: -1 faccia sul fianco -Y; +1 sul fianco +Y (per la bomba che vola verso -X, ruotata di 180 gradi)."""
    s = L / 4.2; B = {}; g = B['root'] = empty('Bomba' + stile + proprietario[:1], (0, 0, 0), None, coll)
    body = B['body'] = empty('BombaCorpo', (0, 0, 0), g, coll); col = M['bblue'] if proprietario == 'PIPPO' else M['bgreen']
    if stile == 'A':
        R = 0.62 * s
        ball_('BombaScafo', 1.0, (0.2 * s, 0, 0), M['bombA'], coll, parent=body, sc=(1.75 * s, R, R))
        cyl('BombaCoda', 0.32 * s, 1.3 * s, (-1.75 * s, 0, 0), M['bombA'], coll, rot=(0, PI / 2, 0), parent=body)
        cyl('BombaAnello', 0.62 * s, 0.25 * s, (-2.2 * s, 0, 0), M['dark'], coll, rot=(0, PI / 2, 0), parent=body)
        cyl('BombaAnelloVuoto', 0.54 * s, 0.27 * s, (-2.2 * s, 0, 0), M['black'], coll, rot=(0, PI / 2, 0), parent=body)
        for k in range(4):
            a = PI / 2 * k + PI / 4
            box('BombaAletta', (-2.05 * s, 0.32 * s * math.cos(a), 0.32 * s * math.sin(a)), (0.6 * s, 0.05 * s, 0.6 * s), M['dark'], coll, rot=(a - PI / 2, 0, 0), parent=body)
        cyl('BombaFascia', R * 1.02, 0.28 * s, (-0.45 * s, 0, 0), col, coll, rot=(0, PI / 2, 0), parent=body)
        ball_('BombaPunta', 1.0, (1.88 * s, 0, 0), M['bred'], coll, parent=body, sc=(0.14 * s, 0.14 * s, 0.14 * s))
        fz, fx, fs = 0.05 * s, 0.85 * s, 1.35 * s
    else:
        R = 1.0 * s
        ball_('BombaScafo', 1.0, (0.25 * s, 0, 0), M['bombB'], coll, parent=body, sc=(1.45 * s, R, R * 0.97))
        box('BombaCodaScatola', (-1.75 * s, 0, 0), (0.75 * s, 1.15 * s, 1.15 * s), M['dark'], coll, parent=body)
        box('BombaCodaVuoto', (-1.75 * s, 0, 0), (0.77 * s, 1.0 * s, 1.0 * s), M['black'], coll, parent=body)
        for k in range(2):
            box('BombaCodaCroce', (-1.75 * s, 0, 0), (0.7 * s, 1.05 * s, 0.06 * s), M['dark'], coll, rot=(PI / 2 * k + PI / 4, 0, 0), parent=body)
        cyl('BombaCollo', 0.45 * s, 0.6 * s, (-1.2 * s, 0, 0), M['dark'], coll, rot=(0, PI / 2, 0), parent=body)
        cyl('BombaFascia', R * 1.005, 0.3 * s, (-0.35 * s, 0, 0), col, coll, rot=(0, PI / 2, 0), parent=body)
        for k in range(10):                                                                   # bulloni lungo la cucitura
            a = 2 * PI * k / 10
            ball_('BombaBullone', 0.05 * s, (0.25 * s, 1.0 * s * math.cos(a), 0.97 * s * math.sin(a)), M['steel'], coll, parent=body)
        fz, fx, fs = 0.08 * s, 0.85 * s, 1.9 * s
    # faccia sul fianco verso la camera (-Y), vicino alla punta
    # niente faccia sugli oggetti (scelta dell'autore, 17 novembre 2026): resta solo un punto d'appoggio per ciuccio e naso
    B['face'] = {'root': empty('BombaFaccia', (fx, lato * R * 0.93, fz), body, coll), 'pupils': [], 'brows': [], 'eyes': []}
    B['face']['root'].rotation_euler = (0, 0, math.atan2(0.25, -lato))
    if con_faccia:
        B['face'] = faccia(coll, M, body, (fx, lato * R * 0.93, fz), s=fs * 0.55, verso=(0.25, lato, 0), nome='BombaFaccia')
    # bandierina col nome
    asta = cyl('BombaAsta', 0.025 * s, 1.1 * s, (-1.35 * s, 0, R * 0.85 + 0.5 * s), M['steel'], coll, parent=body)
    fl = box('BombaBandiera', (-1.62 * s, 0, R * 0.85 + 0.82 * s), (0.55 * s, 0.03 * s, 0.4 * s), col, coll, parent=body)
    if font:
        testo(coll, 'BombaNome', proprietario[:1], 0.3 * s, M['white'], (-1.62 * s, lato * 0.03 * s, R * 0.85 + 0.8 * s), font, parent=body,
              rot=(PI / 2, 0, 0 if lato < 0 else PI))
    B['R'] = R; B['L'] = L
    return B


def fiamma(coll, M, parent, x, s=1.0):
    f = empty('Fiamma', (x, 0, 0), parent, coll)
    ball_('FiammaCorpo', 1.0, (-0.5 * s, 0, 0), M['flame'], coll, parent=f, sc=(0.7 * s, 0.32 * s, 0.32 * s))
    return f


# ============================== carro armato ==============================
def carro(coll, M, stile='C', font=None):
    """carro armato: fronte -Y (cannone verso -Y), origine a terra. Lungo 5.2, alto 2.4. Botola in cima per Pippo."""
    T = {}; r = T['root'] = empty('Carro' + stile, (0, 0, 0), None, coll)
    hull, hull2, trk = (M['army'], M['army2'], M['rubber']) if stile == 'C' else (M['toyR'], M['toyY'], M['toyB'])
    for sx in (-1, 1):                                                                         # cingoli
        x = sx * 1.45
        box('CarroCingolo', (x, 0, 0.6), (0.75, 4.2, 0.9), trk, coll, parent=r)
        for y in (-2.1, 2.1): cyl('CarroCingoloFine', 0.45, 0.75, (x, y, 0.6), trk, coll, rot=(0, PI / 2, 0), parent=r)
        for k in range(6):
            y = -1.9 + k * 0.76
            cyl('CarroRuota', 0.33, 0.8, (x, y, 0.55), M['steel'] if stile == 'C' else hull2, coll, rot=(0, PI / 2, 0), parent=r)
        box('CarroParafango', (x, 0, 1.1), (0.85, 4.8, 0.1), hull2, coll, parent=r)
    box('CarroScafo', (0, 0, 1.25), (2.3, 4.6, 0.9), hull, coll, parent=r)
    box('CarroMuso', (0, -2.35, 1.1), (2.3, 0.5, 0.6), hull, coll, rot=(0.6, 0, 0), parent=r)
    tur = T['turret'] = empty('CarroTorretta', (0, 0.25, 1.7), r, coll)
    ball_('CarroTorrettaCupola', 1.0, (0, 0, 0.35), hull2 if stile == 'D' else hull, coll, parent=tur, sc=(1.15, 1.3, 0.62))
    gun = T['gun'] = empty('CarroCannone', (0, -1.05, 0.45), tur, coll)
    cyl('CarroCanna', 0.13, 2.6, (0, -1.3, 0), hull2 if stile == 'C' else M['toyB'], coll, rot=(PI / 2, 0, 0), parent=gun)
    cyl('CarroBocca', 0.2, 0.35, (0, -2.6, 0), M['dark'] if stile == 'C' else M['toyR'], coll, rot=(PI / 2, 0, 0), parent=gun)
    T['hatch'] = empty('CarroBotola', (0.35, 0.45, 0.95), tur, coll)
    cyl('CarroBotolaAnello', 0.38, 0.12, (0, 0, 0), M['dark'], coll, parent=T['hatch'])
    cyl('CarroBotolaVuoto', 0.31, 0.14, (0, 0, 0.01), M['black'], coll, parent=T['hatch'])
    lid = box('CarroBotolaCoperchio', (0, 0.42, 0.25), (0.7, 0.06, 0.6), hull, coll, rot=(-0.35, 0, 0), parent=T['hatch'])
    if stile == 'C':
        box('CarroStella', (0, -0.9, 0.1), (0.01, 0.01, 0.01), M['white'], coll, parent=tur)
        for k in range(5):                                                                        # stella bianca sul fianco
            a = 2 * PI * k / 5
            box('CarroStellaPunta', (-1.16, 0.25 + 0.18 * math.sin(a), 1.25 + 0.18 * math.cos(a)), (0.02, 0.09, 0.3), M['white'], coll, rot=(-a, 0, 0), parent=r)
        cyl('CarroAntenna', 0.015, 1.6, (-0.6, 0.8, 1.5), M['dark'], coll, parent=tur)
    else:
        for sx in (-1, 1): ball_('CarroBullone', 0.12, (sx * 1.16, -1.5, 1.35), M['toyY'], coll, parent=r)
        ball_('CarroPomello', 0.14, (-0.6, 0.8, 0.95), M['toyY'], coll, parent=tur)
        if font: testo(coll, 'CarroScritta', 'PIPPO', 0.42, M['toyY'], (-1.17, 0.0, 1.27), font, parent=r, rot=(PI / 2, 0, -PI / 2))
    return T


# ============================== piscina gonfiabile e sottomarino ==============================
def piscina(coll, M, R=1.9):
    """piscina gonfiabile a tre anelli bianchi e blu, origine a terra al centro. Acqua a z=0.62."""
    P = {}; r = P['root'] = empty('Piscina', (0, 0, 0), None, coll); rr = 0.17
    for k, m in enumerate((M['poolB'], M['poolW'], M['poolB'])):
        _torus('PiscinaAnello', R, rr, m, coll, parent=r, loc=(0, 0, rr + k * 2 * rr * 0.95))
    cyl('PiscinaFondo', R + 0.05, 0.04, (0, 0, 0.02), M['poolB'], coll, parent=r)
    P['water'] = cyl('PiscinaAcqua', R - 0.02, 0.06, (0, 0, 0.6), M['water'], coll, parent=r)
    ball_('PiscinaValvola', 0.06, (R * 0.7, -R * 0.7, 0.95), M['poolW'], coll, parent=r, sc=(1, 1, 0.6))
    P['R'] = R
    return P


def sottomarino(coll, M, stile='E', font=None):
    """sottomarino: prua verso -Y, origine al centro dello scafo. Lungo 4.6. Torretta con portello per Giulia."""
    S = {}; r = S['root'] = empty('Sottomarino' + stile, (0, 0, 0), None, coll)
    hull = M['subY'] if stile == 'E' else M['subG']; trim = M['bred'] if stile == 'E' else M['dark']
    ball_('SubScafo', 1.0, (0, 0, 0), hull, coll, parent=r, sc=(0.85, 2.3, 0.85))
    tw = S['tower'] = empty('SubTorretta', (0, 0.15, 0.7), r, coll)
    box('SubTorre', (0, 0, 0.45), (0.55, 1.2, 0.9), hull, coll, parent=tw)
    for sy in (-1, 1): cyl('SubTorreFine', 0.275, 0.9, (0, sy * 0.6, 0.45), hull, coll, parent=tw)
    cyl('SubPortello', 0.24, 0.1, (0, -0.1, 0.92), trim, coll, parent=tw)
    S['hatch'] = empty('SubPortelloVuoto', (0, -0.1, 0.92), tw, coll)
    per = S['periscope'] = empty('SubPeriscopio', (0, 0.55, 0.9), tw, coll)
    cyl('SubPeriAsta', 0.05, 1.0, (0, 0, 0.5), M['steel'], coll, parent=per)
    box('SubPeriTesta', (0, -0.08, 1.0), (0.12, 0.28, 0.14), M['steel'], coll, parent=per)
    ball_('SubPeriVetro', 0.05, (0, -0.22, 1.0), M['glass'], coll, parent=per)
    for sx in (-1, 1): box('SubPinnaTorre', (sx * 0.5, -0.1, 0.55), (0.5, 0.3, 0.05), trim, coll, parent=tw)
    # oblò con il bordo
    for k in range(3):
        y = -1.2 + k * 0.85
        cyl('SubOblòBordo', 0.2, 0.08, (-0.79, y, 0.08), M['gold'] if stile == 'E' else M['steel'], coll, rot=(0, PI / 2, 0), parent=r)
        cyl('SubOblò', 0.15, 0.09, (-0.8, y, 0.08), M['glass'], coll, rot=(0, PI / 2, 0), parent=r)
    # coda: elica e timoni
    cyl('SubCono', 0.22, 0.4, (0, 2.35, 0), trim, coll, rot=(PI / 2, 0, 0), parent=r)
    S['prop'] = el = empty('SubElica', (0, 2.6, 0), r, coll)
    for k in range(3): box('SubPala', (0, 0, 0), (0.08, 0.04, 0.75), M['gold'] if stile == 'E' else M['steel'], coll, rot=(0, 2 * PI * k / 3, 0), parent=el)
    box('SubTimone', (0, 2.1, 0), (1.7, 0.4, 0.06), trim, coll, parent=r); box('SubTimoneV', (0, 2.1, 0), (0.06, 0.4, 1.5), trim, coll, parent=r)
    if stile == 'E':
        S['face'] = faccia(coll, M, r, (0, -2.05, 0.2), s=0.95, verso=(0, -1, 0.15), nome='SubFaccia')
    else:
        for k in range(2):                                                                     # tubi lanciasiluri
            cyl('SubTubo', 0.1, 0.1, (k * 0.36 - 0.18, -2.27, -0.15), M['black'], coll, rot=(PI / 2, 0, 0), parent=r)
        if font: testo(coll, 'SubScritta', 'G-1', 0.32, M['white'], (-0.56, -0.05, 1.15), font, parent=tw, rot=(PI / 2, 0, -PI / 2))
    return S


def cappello_capitano(coll, M, parent, loc=(0, 0, 0), s=1.0):
    h = empty('Capitano', loc, parent, coll)
    cyl('CapitanoFascia', 0.2 * s, 0.1 * s, (0, 0, 0), M['black'], coll, parent=h)
    ball_('CapitanoCupola', 1.0, (0, 0, 0.08 * s), M['white'], coll, parent=h, sc=(0.25 * s, 0.25 * s, 0.07 * s))
    box('CapitanoVisiera', (0, -0.2 * s, -0.03 * s), (0.28 * s, 0.14 * s, 0.025 * s), M['black'], coll, rot=(0.3, 0, 0), parent=h)
    ball_('CapitanoStemma', 0.04 * s, (0, -0.2 * s, 0.06 * s), M['gold'], coll, parent=h)
    return h


# ============================== armeria del prete ==============================
def _pistola_cartoon(coll, M, parent, loc, mat, s=1.0, rot=(0, 0, 0)):
    g = empty('Pistola', loc, parent, coll); g.rotation_euler = rot
    box('PistolaCanna', (0.18 * s, 0, 0.05 * s), (0.42 * s, 0.07 * s, 0.1 * s), mat, coll, parent=g)
    box('PistolaCalcio', (0, 0, -0.08 * s), (0.1 * s, 0.07 * s, 0.22 * s), M['wood2'], coll, rot=(0, 0.3, 0), parent=g)
    return g


def _fucile_cartoon(coll, M, parent, loc, mat, s=1.0, rot=(0, 0, 0)):
    g = empty('Fucile', loc, parent, coll); g.rotation_euler = rot
    cyl('FucileCanna', 0.03 * s, 1.0 * s, (0.35 * s, 0, 0.03 * s), mat, coll, rot=(0, PI / 2, 0), parent=g)
    box('FucileCalcio', (-0.32 * s, 0, -0.02 * s), (0.5 * s, 0.06 * s, 0.14 * s), M['wood'], coll, rot=(0, -0.12, 0), parent=g)
    return g


def bazooka(coll, M, parent=None, loc=(0, 0, 0), s=1.0, croce=True):
    """bazooka: tubo lungo +X, impugnatura sotto. Adesivo con la croce (indizio del prete)."""
    g = empty('Bazooka', loc, parent, coll)
    cyl('BazookaTubo', 0.13 * s, 1.6 * s, (0, 0, 0), M['army'], coll, rot=(0, PI / 2, 0), parent=g)
    cyl('BazookaBocca', 0.17 * s, 0.22 * s, (0.8 * s, 0, 0), M['dark'], coll, rot=(0, PI / 2, 0), parent=g)
    cyl('BazookaCoda', 0.16 * s, 0.18 * s, (-0.8 * s, 0, 0), M['dark'], coll, rot=(0, PI / 2, 0), parent=g)
    box('BazookaManico', (0.1 * s, 0, -0.2 * s), (0.08 * s, 0.07 * s, 0.24 * s), M['dark'], coll, parent=g)
    box('BazookaMirino', (0.3 * s, 0, 0.16 * s), (0.12 * s, 0.03 * s, 0.1 * s), M['dark'], coll, parent=g)
    if croce:
        box('BazookaAdesivo', (-0.3 * s, -0.125 * s, 0.03 * s), (0.18 * s, 0.01 * s, 0.18 * s), M['white'], coll, parent=g)
        box('BazookaCroceV', (-0.3 * s, -0.132 * s, 0.03 * s), (0.035 * s, 0.01 * s, 0.14 * s), M['bred'], coll, parent=g)
        box('BazookaCroceH', (-0.3 * s, -0.132 * s, 0.06 * s), (0.1 * s, 0.01 * s, 0.035 * s), M['bred'], coll, parent=g)
    return g


def pistola_acqua(coll, M, parent=None, loc=(0, 0, 0), s=1.0):
    """pistola ad acqua giocattolo: canna verso +X, serbatoio trasparente sopra."""
    g = empty('PistolaAcqua', loc, parent, coll)
    ball_('PAcquaCorpo', 1.0, (0, 0, 0), M['toyY'], coll, parent=g, sc=(0.28 * s, 0.07 * s, 0.09 * s))
    cyl('PAcquaCanna', 0.035 * s, 0.3 * s, (0.35 * s, 0, 0.02 * s), M['toyR'], coll, rot=(0, PI / 2, 0), parent=g)
    ball_('PAcquaSerbatoio', 1.0, (-0.05 * s, 0, 0.13 * s), M['glass'], coll, parent=g, sc=(0.15 * s, 0.08 * s, 0.09 * s))
    box('PAcquaManico', (-0.12 * s, 0, -0.14 * s), (0.08 * s, 0.06 * s, 0.2 * s), M['toyB'], coll, rot=(0, 0.35, 0), parent=g)
    return g


def armeria(coll, M, A, stile='G', C=(600.0, 0.0), font=None):
    """interno dell'armeria del prete: bancone davanti (verso -Y), scaffali alle spalle, insegna in alto.
    G: legno scuro, armi vere (modelli Poly Haven) e croci dorate. H: colori pop, blaster Kenney e neon.
    Restituisce dict con root, counter_top (z del bancone), drawer (cassetto degli scontrini), money."""
    cx, cy = C; Ar = {}; r = Ar['root'] = empty('Armeria' + stile, (cx, cy, 0), None, coll)
    wall = M['wallG'] if stile == 'G' else M['wallH']
    try:
        wall = A.materiale('weathered_brown_planks' if stile == 'G' else 'Wallpaper001A', dimensione=2.0, tinta=None if stile == 'G' else (1.3, 1.1, 0.5))
    except Exception as e:
        print('muro: materiale non trovato', e)
    floor = M['wood2']
    try: floor = A.materiale('WoodFloor043' if stile == 'G' else 'Tiles074', dimensione=2.5)
    except Exception as e: print('pavimento', e)
    box('ArmPavimento', (0, 0, -0.05), (9, 8, 0.1), floor, coll, parent=r)
    box('ArmMuro', (0, 2.6, 2.2), (9, 0.2, 4.6), wall, coll, parent=r)
    for sx in (-1, 1): box('ArmMuroLato', (sx * 4.5, 0, 2.2), (0.2, 6, 4.6), wall, coll, parent=r)
    # bancone
    top = 1.05; Ar['counter_top'] = top
    legno = M['wood']
    if stile == 'G':
        try: legno = A.materiale('wood_table_worn', dimensione=1.2, tinta=(0.55, 0.45, 0.4))
        except Exception as e: print('bancone', e)
    box('ArmBancone', (0, -0.4, top / 2), (3.6, 0.9, top), legno if stile == 'G' else M['mint'], coll, parent=r)
    box('ArmBanconePiano', (0, -0.4, top + 0.03), (3.8, 1.0, 0.06), M['wood2'] if stile == 'G' else M['purple'], coll, parent=r)
    Ar['drawer'] = empty('ArmCassetto', (1.1, -0.88, top - 0.25), r, coll)
    box('ArmCassettoFronte', (0, 0, 0), (0.7, 0.06, 0.3), M['wood2'] if stile == 'G' else M['toyY'], coll, parent=Ar['drawer'])
    ball_('ArmCassettoPomo', 0.04, (0, -0.05, 0), M['gold'], coll, parent=Ar['drawer'])
    # croce sul bancone (davanti)
    box('ArmCroceV', (-0.9, -0.86, 0.55), (0.12, 0.03, 0.6), M['gold'], coll, parent=r)
    box('ArmCroceH', (-0.9, -0.86, 0.66), (0.4, 0.03, 0.12), M['gold'], coll, parent=r)
    # registratore di cassa e soldi
    try:
        cr = A.modello('CashRegister_01', posizione=(cx + 1.2, cy - 0.35, top + 0.06), altezza=0.38, collezione=coll)
        cr.rotation_euler = (0, 0, PI); cr.parent = r; cr.location = (1.2, -0.35, top + 0.06)
    except Exception as e: print('cassa', e)
    Ar['money'] = []
    for k in range(4):
        Ar['money'].append(box('ArmBanconote', (-0.3 + 0.03 * k, -0.45, top + 0.07 + 0.025 * k), (0.32, 0.16, 0.02), M['money'], coll, rot=(0, 0, 0.15 * k), parent=r))
    # scaffali con le armi
    for row, z in enumerate((1.35, 2.15, 2.95)):
        box('ArmMensola', (0, 2.35, z), (7.6, 0.4, 0.06), M['wood2'] if stile == 'G' else M['purple'], coll, parent=r)
    guns = []
    if stile == 'G':
        try:
            for k, (aid, h) in enumerate((('service_pistol', 0.18), ('bolt_action_rifle_7_62', 0.22), ('service_pistol', 0.18), ('bolt_action_rifle_7_62', 0.22))):
                x = -2.7 + k * 1.8
                g = A.modello(aid, posizione=(cx + x, cy + 2.3, 1.45), altezza=h, collezione=coll); g.rotation_euler = (0, 0, 0); guns.append(g)
        except Exception as e: print('armi vere', e)
        try:
            cn = A.modello('cannon_01', posizione=(cx - 3.1, cy + 1.2, 0), altezza=1.1, collezione=coll); cn.rotation_euler = (0, 0, -PI / 2 + 0.4)
        except Exception as e: print('cannone', e)
        try:
            for k, (x, y) in enumerate(((3.3, 1.4), (3.4, 0.4))):
                A.modello('old_military_crate', posizione=(cx + x, cy + y, 0), altezza=0.6 + 0.1 * k, collezione=coll)
        except Exception as e: print('casse', e)
        for k in range(5):                                                                     # fucili appesi sul muro, a raggiera
            _fucile_cartoon(coll, M, r, (-2.8 + k * 1.4, 2.42, 3.6), M['dark'], s=1.0, rot=(PI / 2 * 0, 0.0, 0))
        for k in range(6): _pistola_cartoon(coll, M, r, (-3.0 + k * 1.2, 2.3, 2.27), M['dark'], s=1.1)
        for k in range(4): bazooka(coll, M, r, (-2.6 + k * 1.75, 2.3, 3.12), s=0.8)
    else:
        kb = ['kenney/blaster-kit/blaster-%s' % ch for ch in 'abcdefghijklmnopqr']
        for k in range(12):
            z = (1.38, 2.18, 2.98)[k // 4] + 0.02; x = -2.8 + (k % 4) * 1.85
            try:
                g = A.modello(kb[k], posizione=(cx + x, cy + 2.3, z), altezza=0.32, collezione=coll, appoggia=True); g.rotation_euler = (0, 0, PI / 2); guns.append(g)
            except Exception as e: print('blaster', kb[k], e); break
        try:
            for k, (x, y) in enumerate(((3.3, 1.4), (3.3, 0.5))):
                A.modello('kenney/blaster-kit/crate-medium' if k else 'kenney/blaster-kit/crate-wide', posizione=(cx + x, cy + y, 0), altezza=0.7, collezione=coll, appoggia=True)
        except Exception as e: print('casse', e)
        bazooka(coll, M, r, (-3.3, 1.0, 1.0), s=1.1)
    Ar['guns'] = guns
    # insegna
    sg = Ar['sign'] = empty('ArmInsegna', (0, 2.4, 3.95), r, coll)
    box('ArmInsegnaTavola', (0, -0.05, 0), (5.4, 0.12, 0.85), M['wood2'] if stile == 'G' else M['black'], coll, parent=sg)
    if font:
        testo(coll, 'ArmInsegnaTesto', 'ARMI BENEDETTE', 0.52, M['gold'] if stile == 'G' else M['neon'], (0.25, -0.14, -0.02), font, parent=sg, spessore=0.04)
    box('ArmInsegnaCroceV', (-2.35, -0.14, 0), (0.1, 0.05, 0.6), M['gold'] if stile == 'G' else M['neonW'], coll, parent=sg)
    box('ArmInsegnaCroceH', (-2.35, -0.14, 0.1), (0.36, 0.05, 0.1), M['gold'] if stile == 'G' else M['neonW'], coll, parent=sg)
    box('ArmSoffitto', (0, 0, 4.55), (9, 8, 0.1), material('P19_soffitto', (0.05, 0.035, 0.03), rough=1.0, spec=0.0), coll, parent=r)
    for sx in (-1, 1):                                                                         # due lampade ai lati dell'insegna
        ball_('ArmLampada', 0.13, (sx * 3.4, 2.0, 3.95), M['neonW'], coll, parent=r)
        cyl('ArmLampadaFilo', 0.01, 0.55, (sx * 3.4, 2.0, 4.3), M['black'], coll, parent=r)
    return Ar


def scontrino(coll, M, parent, loc, nome, font=None, rot=(0, 0, 0)):
    g = empty('Scontrino' + nome, loc, parent, coll); g.rotation_euler = rot
    box('ScontrinoCarta', (0, 0, 0), (0.42, 0.01, 0.6), M['paper'], coll, parent=g)
    if font: testo(coll, 'ScontrinoNome', nome, 0.075, M['black'], (0, -0.012, 0.2), font, parent=g, spessore=0.002)
    for k in range(4): box('ScontrinoRiga', (0, -0.008, 0.06 - k * 0.09), (0.3, 0.004, 0.025), M['black'], coll, parent=g)
    return g


# ============================== bombine gemelle ==============================
def bombina(coll, M, GM, stile='A', naso=True, L=1.0, proprietario='PIPPO'):
    """bombina neonata: stessa forma della bomba scelta, lunga L, senza occhi, col ciuccio e il naso di Giulia.
    Punta verso +X come la bomba; faccia verso -Y."""
    B = bomba(coll, M, stile, proprietario, None, L=L); body = B['body']; s = L / 4.2
    f = B['face']['root']; R = B['R']; k = R / 0.15                                            # misure assolute, proporzionate alla bombina
    c = empty('Ciuccio', (0, -0.02 * k, -0.07 * k), f, coll)
    cyl('CiuccioScudo', 0.055 * k, 0.012 * k, (0, 0, 0), M['pink'], coll, rot=(PI / 2, 0, 0), parent=c)
    _torus('CiuccioAnello', 0.032 * k, 0.008 * k, M['pink'], coll, parent=c, loc=(0, -0.02 * k, -0.012 * k)).rotation_euler = (PI / 2, 0, 0)
    if naso:
        n = B['nose'] = empty('NasoGiulia', (0, -0.03 * k, 0.03 * k), f, coll)
        sk = GM['nose']
        ball_('NasoBase', 1.0, (0, -0.01 * k, 0), sk, coll, parent=n, sc=(0.04 * k, 0.045 * k, 0.04 * k))
        ball_('NasoLungo', 1.0, (0, -0.045 * k, -0.05 * k), sk, coll, parent=n, sc=(0.034 * k, 0.04 * k, 0.085 * k))
        ball_('NasoPunta', 1.0, (0, -0.06 * k, -0.13 * k), sk, coll, parent=n, sc=(0.045 * k, 0.045 * k, 0.045 * k))
        ball_('NasoPorro', 1.0, (0.03 * k, -0.095 * k, -0.1 * k), GM['wart'], coll, parent=n, sc=(0.012 * k, 0.012 * k, 0.012 * k))
    return B


def culla(coll, M, larghezza=2.2):
    """culla doppia di legno, origine a terra, apertura in alto."""
    r = empty('Culla', (0, 0, 0), None, coll); w = larghezza
    box('CullaFondo', (0, 0, 0.55), (w, 0.9, 0.08), M['wood'], coll, parent=r)
    for sy in (-1, 1):
        for k in range(12):
            x = -w / 2 + 0.05 + k * (w - 0.1) / 11
            cyl('CullaSbarra', 0.025, 0.55, (x, sy * 0.43, 0.85), M['paper'], coll, parent=r)
        box('CullaCorrimano', (0, sy * 0.43, 1.13), (w + 0.1, 0.07, 0.07), M['wood'], coll, parent=r)
    for sx in (-1, 1):
        box('CullaTestata', (sx * w / 2, 0, 0.75), (0.08, 0.95, 0.85), M['wood'], coll, parent=r)
        for sy in (-1, 1): cyl('CullaGamba', 0.04, 0.55, (sx * (w / 2 - 0.05), sy * 0.4, 0.27), M['wood2'], coll, parent=r)
    box('CullaMaterasso', (0, 0, 0.64), (w - 0.1, 0.82, 0.12), M['poolW'], coll, parent=r)
    return r


# ============================== piccoli oggetti delle gag ==============================
def forchetta(coll, M, parent=None, loc=(0, 0, 0), L=1.1):
    """forchetta gigante: manico dall'origine verso +Z, rebbi in cima."""
    g = empty('Forchetta', loc, parent, coll)
    cyl('ForchettaManico', 0.045, L * 0.62, (0, 0, L * 0.31), M['steel'], coll, parent=g)
    box('ForchettaCollo', (0, 0, L * 0.66), (0.3, 0.045, 0.12), M['steel'], coll, parent=g)
    for k in range(4):
        box('ForchettaRebbio', (-0.11 + 0.073 * k, 0, L * 0.84), (0.035, 0.035, L * 0.32), M['steel'], coll, parent=g)
    return g


def pallina(coll, M, r=0.14):
    g = empty('Pallina', (0, 0, 0), None, coll)
    ball_('PallinaGomma', r, (0, 0, 0), M['bred'], coll, parent=g)
    _torus('PallinaStriscia', r * 0.98, r * 0.12, M['byel'], coll, parent=g)
    return g


def velo(coll, M, parent, loc=(0, 0, 0), s=1.0):
    """velo da sposa: coroncina di fiori e telo bianco che scende dietro."""
    g = empty('Velo', loc, parent, coll); w = material('P19_velo', (1, 1, 1), rough=0.9, emit=(1, 1, 1), emit_strength=0.25)
    _torus('VeloCorona', 0.32 * s, 0.05 * s, w, coll, parent=g)
    for k in range(8):
        a = 2 * PI * k / 8; ball_('VeloFiore', 0.06 * s, (0.32 * s * math.cos(a), 0.32 * s * math.sin(a), 0.05 * s), M['pink'], coll, parent=g)
    ball_('VeloTelo', 1.0, (0, 0.35 * s, -0.45 * s), w, coll, parent=g, sc=(0.42 * s, 0.25 * s, 0.7 * s))
    return g


def papillon(coll, M, parent, loc=(0, 0, 0), s=1.0):
    g = empty('Papillon', loc, parent, coll)
    for sx in (-1, 1): ball_('PapillonAla', 1.0, (sx * 0.17 * s, 0, 0), M['black'], coll, parent=g, sc=(0.17 * s, 0.05 * s, 0.12 * s))
    ball_('PapillonNodo', 0.06 * s, (0, -0.02 * s, 0), M['black'], coll, parent=g)
    return g


def libretto(coll, M, parent=None, loc=(0, 0, 0), s=1.0):
    """libretto del matrimonio aperto (pagine verso -Y), croce dorata sul dorso."""
    g = empty('Libretto', loc, parent, coll)
    for sx in (-1, 1):
        box('LibrettoCopertina', (sx * 0.13 * s, 0.01 * s, 0), (0.26 * s, 0.02 * s, 0.34 * s), M['black'], coll, rot=(0, 0, -sx * 0.25), parent=g)
        box('LibrettoPagine', (sx * 0.12 * s, -0.01 * s, 0), (0.23 * s, 0.03 * s, 0.31 * s), M['paper'], coll, rot=(0, 0, -sx * 0.25), parent=g)
    box('LibrettoCroce', (0, 0.03 * s, 0.05 * s), (0.03 * s, 0.01 * s, 0.12 * s), M['gold'], coll, parent=g)
    return g


def periscopio(coll, M, h=2.4):
    """periscopio da solo (prima che emerga il sottomarino gigante): origine alla base, oculare verso -Y."""
    g = empty('Periscopio', (0, 0, 0), None, coll)
    cyl('PeriscopioAsta', 0.12, h, (0, 0, h / 2), M['subG'], coll, parent=g)
    box('PeriscopioTesta', (0, -0.15, h), (0.28, 0.6, 0.32), M['subG'], coll, parent=g)
    ball_('PeriscopioVetro', 0.11, (0, -0.46, h), M['glass'], coll, parent=g)
    return g
