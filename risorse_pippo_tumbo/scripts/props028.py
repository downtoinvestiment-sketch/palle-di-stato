"""Oggetti del video 028 «Il pomodoro da undici euro» (copione n. 27A, caro vita). In scala con Pippo (alto circa 2,4 m). Fronte -Y.
- mats028(), font(nome): materiali e font (Poppins-Black ha il simbolo dell'euro fatto bene).
- pomodoro(coll, M, r=0.16): origine sotto, a terra. cuscino(coll, M, lato): velluto rosso con le nappe d'oro.
- cartellino(coll, M, fnt, testo='11 €', h=0.55): cartello del prezzo su un bastoncino, origine alla punta in basso.
- Dove si vende il pomodoro (tutti restituiscono dict root, pomodoro, cartellino, centro):
  bancarella(...)  M1 banco del mercato con la tenda a righe e le cassette;
  gioielleria(...) M2 piedistallo di marmo, cuscino, campana di vetro, cordoni rossi;
  cassaforte(...)  M3 cassaforte aperta con il pomodoro dentro.
- La banca: sportello(...) B1 sportello col vetro; scrivania(...) B2 scrivania del direttore con la pila di carte e il timbro.
- timbro(coll, M, fnt), contratto(coll, M, fnt), motorino(coll, M, colore): il motorino di Gualtiero.
- banchiere(coll): un signore in giacca fatto con gente027 (non e' un personaggio della serie)."""
import math, os
import bpy, bmesh
from mathutils import Vector
from common import material, empty, shape
from set004 import obj, box_c, cyl
import props023, props024

PI = math.pi
QUI = os.path.dirname(os.path.abspath(__file__))


def font(nome='Poppins-Black'):
    return bpy.data.fonts.load(os.path.join(QUI, '..', 'assets', 'font', nome + '.ttf'), check_existing=True)


def vetro(nome='M28_vetro', alpha=0.14):
    m = bpy.data.materials.get(nome)
    if m: return m
    m = material(nome, (0.82, 0.94, 1.0), rough=0.04, spec=1.0)
    m.node_tree.nodes['Principled BSDF'].inputs['Alpha'].default_value = alpha
    try: m.surface_render_method = 'BLENDED'
    except Exception: m.blend_method = 'BLEND'
    return m


def mats028(A=None):
    m = material
    M = dict(pom=m('M28_pomodoro', (0.86, 0.035, 0.03), rough=0.2, coat=0.7), verde=m('M28_picciolo', (0.08, 0.42, 0.09), rough=0.6),
             velluto=m('M28_velluto', (0.50, 0.02, 0.09), rough=0.95, spec=0.1), oro=m('M28_oro', (1.0, 0.70, 0.20), rough=0.25, metallic=1.0),
             legno=m('M28_legno', (0.60, 0.40, 0.22), rough=0.7), legno_scuro=m('M28_legno_scuro', (0.22, 0.11, 0.06), rough=0.4, coat=0.4),
             carta=m('M28_cartello', (1.0, 0.90, 0.25), rough=0.7), bianco=m('M28_bianco', (0.96, 0.95, 0.92), rough=0.6),
             nero=m('M28_nero', (0.03, 0.03, 0.035), rough=0.5), rosso=m('M28_rosso', (0.85, 0.06, 0.05), rough=0.5),
             marmo=m('M28_marmo', (0.90, 0.89, 0.86), rough=0.22, coat=0.5), acciaio=m('M28_acciaio', (0.55, 0.58, 0.62), rough=0.35, metallic=1.0),
             ferro=m('M28_ferro', (0.16, 0.18, 0.21), rough=0.45, metallic=0.7), verde_banca=m('M28_verde_banca', (0.04, 0.26, 0.17), rough=0.55),
             tenda_r=m('M28_tenda_rossa', (0.85, 0.10, 0.08), rough=0.8), tenda_b=m('M28_tenda_bianca', (0.97, 0.96, 0.92), rough=0.8),
             telo=m('M28_telo', (0.10, 0.42, 0.22), rough=0.85), arancia=m('M28_arancia', (1.0, 0.45, 0.04), rough=0.45),
             limone=m('M28_limone', (1.0, 0.86, 0.10), rough=0.4), melanzana=m('M28_melanzana', (0.22, 0.05, 0.30), rough=0.25, coat=0.5),
             pesca=m('M28_pesca', (1.0, 0.55, 0.35), rough=0.6), tenda_v=m('M28_tenda_verde', (0.10, 0.50, 0.25), rough=0.8), tenda_g=m('M28_tenda_gialla', (1.0, 0.78, 0.12), rough=0.8),
             tenda_a=m('M28_tenda_azzurra', (0.15, 0.45, 0.85), rough=0.8), lavagna=m('M28_lavagna', (0.05, 0.12, 0.09), rough=0.9), cartone=m('M28_cartone', (0.85, 0.66, 0.36), rough=0.8),
             sacco=m('M28_sacco', (0.95, 0.82, 0.52), rough=0.9), zucchina=m('M28_zucchina', (0.16, 0.45, 0.12), rough=0.5), mela=m('M28_mela', (0.55, 0.78, 0.12), rough=0.35),
             gomma=m('M28_gomma', (0.04, 0.04, 0.045), rough=0.85), pelle=m('M28_pelle_sedia', (0.30, 0.07, 0.05), rough=0.45),
             luce=m('M28_luce', (1.0, 0.85, 0.4), emit=(1.0, 0.8, 0.35), emit_strength=6.0), vetro=vetro(),
             inchiostro=m('M28_inchiostro', (0.75, 0.04, 0.04), rough=0.5), tappeto=m('M28_tappeto', (0.62, 0.04, 0.08), rough=0.95))
    if A is not None:                                              # texture vere dalla libreria, dove ci sono
        for k, aid, d in (('legno', 'brown_planks_03', 1.2),):
            try: M[k] = A.materiale(aid, dimensione=d)
            except Exception as e: print('texture mancante', aid, e)
    return M


_FRU = {}
def _frutto():
    """sfera leggera (12 x 8) per la frutta delle cassette: sono centinaia, con la sfera normale pesavano un terzo della scena."""
    if 'm' in _FRU and _FRU['m'].name in bpy.data.meshes: return _FRU['m']
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=12, v_segments=8, radius=1.0)
    for f in bm.faces: f.smooth = True
    me = bpy.data.meshes.new('unit_frutto'); bm.to_mesh(me); bm.free(); me.materials.append(None); _FRU['m'] = me; return me
def _fru(nome, loc, scale, rot, parent, mat, coll):
    return obj(nome, _frutto(), loc, scale, mat, coll, rot=rot, parent=parent)


def box(nome, p0, p1, m, coll, parent=None):
    return obj(nome, box_c(), tuple((a + b) / 2 for a, b in zip(p0, p1)), tuple(b - a for a, b in zip(p0, p1)), m, coll, parent=parent)


def pomodoro(coll, M, r=0.16, nome='Pomodoro'):
    O = empty(nome, (0, 0, 0), None, coll)
    shape(nome + 'Polpa', 'sphere', (0, 0, r * 0.84), (r, r, r * 0.84), (0, 0, 0), O, M['pom'], coll)
    for k in range(5):
        a = 2 * PI * k / 5 + 0.3
        shape(nome + 'Foglia%d' % k, 'cone', (0, 0, r * 1.66), (r * 0.16, r * 0.05, r * 0.62), (1.78, 0, a), O, M['verde'], coll)
    props023.tubo(nome + 'Picciolo', (0, 0, r * 1.62), (r * 0.08, 0, r * 1.95), r * 0.045, M['verde'], coll, parent=O)
    return O


def cuscino(coll, M, lato=0.5, nome='Cuscino'):
    O = empty(nome, (0, 0, 0), None, coll)
    props024.scatola_tonda(nome + 'Velluto', lato, lato, lato * 0.34, lato * 0.15, M['velluto'], coll, O, (0, 0, lato * 0.17))
    for sx in (-1, 1):
        for sy in (-1, 1): shape(nome + 'Nappa', 'sphere', (sx * lato * 0.47, sy * lato * 0.47, lato * 0.15), (lato * 0.07,) * 3, (0, 0, 0), O, M['oro'], coll)
    return O


def cartellino(coll, M, fnt, testo='11 €', h=0.55, nome='Cartellino', larg=0.62, alt=0.36):
    O = empty(nome, (0, 0, 0), None, coll)
    props023.tubo(nome + 'Stecco', (0, 0, 0), (0, 0, h), 0.012, M['legno_scuro'], coll, parent=O)
    props024.scatola_tonda(nome + 'Carta', larg, 0.02, alt, 0.04, M['carta'], coll, O, (0, 0, h + alt * 0.42))
    props023.testo(coll, nome + 'Testo', testo, alt * 0.62, M['inchiostro'], (0, -0.014, h + alt * 0.40), parent=O, font=fnt, estrudi=0.004)
    return O


def _cassetta(coll, M, nome, p, frutto, parent, n=3, r=0.085):
    x, y, z = p; w, d, hh = 0.62, 0.46, 0.2
    box(nome + 'Fondo', (x - w / 2, y - d / 2, z), (x + w / 2, y + d / 2, z + 0.02), M['legno'], coll, parent)
    for sx in (-1, 1): box(nome + 'L', (x + sx * w / 2 - 0.012, y - d / 2, z), (x + sx * w / 2 + 0.012, y + d / 2, z + hh), M['legno'], coll, parent)
    for sy in (-1, 1): box(nome + 'F', (x - w / 2, y + sy * d / 2 - 0.012, z), (x + w / 2, y + sy * d / 2 + 0.012, z + hh), M['legno'], coll, parent)
    lungo = frutto in ('zucchina', 'melanzana'); out = []
    for i in range(n):
        for j in range(2 if not lungo else 1):
            for k in range(2 if not lungo else 2):
                if lungo:
                    px = x - w / 2 + (i + 0.5) * w / n; out.append(_fru(nome + 'V', (px, y + (k - 0.5) * 0.04, z + 0.10 + k * 0.10), (r * 0.62, 0.19, r * 0.62), (0.12 * (i - 1), 0, 0.25 * (k - 0.5)), parent, M[frutto], coll))
                else:
                    out.append(_fru(nome + 'V', (x - w / 2 + (i + 0.5) * w / n + 0.03 * k, y - d / 4 + j * d / 2, z + 0.10 + k * 0.125), (r, r, r * 0.95), (0, 0, 0), parent, M[frutto], coll))
    return out


def bancarella(coll, M, fnt, nome='Banco', insegna='FRUTTA E VERDURA', speciale=True, frutti=('arancia', 'melanzana', 'zucchina', 'limone'), tenda=('tenda_r', 'tenda_b'), centro='pom'):
    """M1: banco del mercato largo 3,4 m. Piano a 1,05 m; il pomodoro sta al centro sul cuscino, piu' in alto di tutto il resto."""
    O = empty(nome, (0, 0, 0), None, coll); W, D, H = 1.7, 0.62, 1.05
    box(nome + 'Piano', (-W, -D, H - 0.07), (W, D, H), M['legno'], coll, O)
    box(nome + 'Telo', (-W + 0.02, -D + 0.01, 0.12), (W - 0.02, -D + 0.05, H - 0.07), M['telo'], coll, O)
    for sx in (-1, 1):
        for sy in (-1, 1): props023.tubo(nome + 'Palo', (sx * (W - 0.06), sy * (D - 0.06), 0), (sx * (W - 0.06), sy * (D - 0.06), 3.0), 0.045, M['legno_scuro'], coll, parent=O)
    n = 10; ww = 2 * (W + 0.15) / n
    for i in range(n):                                             # tenda a righe, inclinata verso chi compra
        t = obj(nome + 'Tenda%d' % i, box_c(), (-(W + 0.15) + (i + 0.5) * ww, -0.25, 2.95), (ww * 1.005, 2.1, 0.035), M[tenda[i % 2]], coll, rot=(0.20, 0, 0), parent=O)
        shape(nome + 'Smerlo%d' % i, 'sphere_lo', (-(W + 0.15) + (i + 0.5) * ww, -1.28, 2.71), (ww * 0.5, 0.02, 0.16), (0, 0, 0), O, M[tenda[i % 2]], coll)
    box(nome + 'Insegna', (-1.25, -D - 0.02, 2.12), (1.25, -D + 0.03, 2.50), M['legno_scuro'], coll, O)
    props023.testo(coll, nome + 'InsegnaT', insegna, 0.21, M['carta'], (0, -D - 0.03, 2.31), parent=O, font=fnt, estrudi=0.006)
    for i, (px, fr) in enumerate(zip((-1.28, -0.62, 0.62, 1.28), frutti)): _cassetta(coll, M, nome + 'Cas%d' % i, (px, 0.05, H), fr, O)
    for i, (px, fr) in enumerate(((-1.05, 'mela'), (1.05, 'arancia'))): _cassetta(coll, M, nome + 'CasT%d' % i, (px, -1.05, 0.0), fr, O)
    if not speciale:
        rub = _cassetta(coll, M, nome + 'CasC', (0, 0.05, H), centro, O, r=0.095)
        return dict(root=O, rubabili=rub, centro=Vector((0, 0, H + 0.3)))
    box(nome + 'Rialzo', (-0.3, -0.32, H), (0.3, 0.28, H + 0.22), M['legno_scuro'], coll, O)
    cu = cuscino(coll, M, 0.5, nome + 'Cuscino'); cu.parent = O; cu.location = (0, -0.02, H + 0.22)
    po = pomodoro(coll, M, 0.22, nome + 'Pomodoro'); po.parent = O; po.location = (0, -0.02, H + 0.22 + 0.15)
    ca = cartellino(coll, M, fnt, nome=nome + 'Prezzo', h=0.5, larg=0.8, alt=0.46); ca.parent = O; ca.location = (0.62, -0.42, H); ca.rotation_euler = (0, 0, -0.18)
    return dict(root=O, pomodoro=po, cartellino=ca, centro=Vector((0, 0, H + 0.5)))


def _cupola(coll, M, r, nome, parent, loc):
    prof = [(r * math.cos(a), r * math.sin(a)) for a in [i * (PI / 2) / 12 for i in range(12)]] + [(0.0, r)]
    prof = [(0.0, 0.0)] + prof
    o = props024.tornio(nome, prof, coll, [M['vetro']], seg=48, parent=parent, loc=loc); o.visible_shadow = False
    shape(nome + 'Pomello', 'sphere', (loc[0], loc[1], loc[2] + r + 0.03), (0.05, 0.05, 0.05), (0, 0, 0), parent, M['oro'], coll)
    return o


def _colonnina(coll, M, nome, p, parent, h=1.0):
    x, y = p
    cyl(nome + 'Base', 0.16, 0.04, (x, y, 0.02), M['oro'], coll, parent=parent); props023.tubo(nome + 'Asta', (x, y, 0), (x, y, h), 0.03, M['oro'], coll, parent=parent)
    shape(nome + 'Pomo', 'sphere', (x, y, h + 0.04), (0.065,) * 3, (0, 0, 0), parent, M['oro'], coll)


def _cordone(coll, M, nome, a, b, parent, cala=0.22, n=10, r=0.028):
    a = Vector(a); b = Vector(b); pts = [a.lerp(b, i / n) - Vector((0, 0, cala * 4 * (i / n) * (1 - i / n))) for i in range(n + 1)]
    for i in range(n): props023.tubo(nome + '%d' % i, pts[i], pts[i + 1], r, M['velluto'], coll, parent=parent); shape(nome + 'N%d' % i, 'sphere_lo', pts[i], (r,) * 3, (0, 0, 0), parent, M['velluto'], coll)


def gioielleria(coll, M, fnt, nome='Gioiello'):
    """M2: il pomodoro esposto come un gioiello. Cima del piedistallo a 1,30 m."""
    O = empty(nome, (0, 0, 0), None, coll); H = 1.30
    prof = [(0, 0), (0.50, 0), (0.50, 0.10), (0.42, 0.14), (0.34, 0.20), (0.32, H - 0.22), (0.40, H - 0.16), (0.48, H - 0.10), (0.48, H), (0, H)]
    props024.tornio(nome + 'Piedistallo', prof, coll, [M['marmo']], seg=48, parent=O)
    cu = cuscino(coll, M, 0.56, nome + 'Cuscino'); cu.parent = O; cu.location = (0, 0, H)
    po = pomodoro(coll, M, 0.22, nome + 'Pomodoro'); po.parent = O; po.location = (0, 0, H + 0.17)
    _cupola(coll, M, 0.45, nome + 'Campana', O, (0, 0, H))
    box(nome + 'Tappeto', (-1.5, -2.6, 0.0), (1.5, 1.0, 0.012), M['tappeto'], coll, O)
    for i, sx in enumerate((-1, 1)):
        _colonnina(coll, M, nome + 'Col%dA' % i, (sx * 1.25, -1.15), O); _colonnina(coll, M, nome + 'Col%dB' % i, (sx * 1.25, 0.5), O)
        _cordone(coll, M, nome + 'Cordone%d' % i, (sx * 1.25, -1.15, 0.98), (sx * 1.25, 0.5, 0.98), O)
    _cordone(coll, M, nome + 'CordoneF', (-1.25, -1.15, 0.98), (1.25, -1.15, 0.98), O, cala=0.3, n=14)
    ca = cartellino(coll, M, fnt, nome=nome + 'Prezzo', h=0.0, larg=0.66, alt=0.36); ca.parent = O; ca.location = (0, -0.50, H - 0.55); ca.rotation_euler = (0.0, 0, 0)
    return dict(root=O, pomodoro=po, cartellino=ca, centro=Vector((0, 0, H + 0.2)))


def cassaforte(coll, M, fnt, nome='Cassaforte', aperta=1.9):
    """M3: cassaforte su un basamento, sportello aperto (aperta = angolo in radianti), dentro il pomodoro illuminato."""
    O = empty(nome, (0, 0, 0), None, coll); w, d, z0, z1, s = 0.75, 0.6, 0.55, 2.05, 0.09
    box(nome + 'Basamento', (-w - 0.08, -d - 0.05, 0), (w + 0.08, d + 0.05, z0), M['ferro'], coll, O)
    box(nome + 'Retro', (-w, d - s, z0), (w, d, z1), M['acciaio'], coll, O); box(nome + 'Sopra', (-w, -d, z1 - s), (w, d, z1), M['acciaio'], coll, O); box(nome + 'Sotto', (-w, -d, z0), (w, d, z0 + s), M['acciaio'], coll, O)
    for sx in (-1, 1): box(nome + 'Lato', (sx * w - (s if sx > 0 else 0), -d, z0), (sx * w + (s if sx < 0 else 0), d, z1), M['acciaio'], coll, O)
    box(nome + 'Luce', (-w + s, d - s - 0.02, z0 + s), (w - s, d - s, z1 - s), M['luce'], coll, O)
    box(nome + 'Ripiano', (-w + s, -d + 0.1, z0 + 0.42), (w - s, d - s, z0 + 0.46), M['ferro'], coll, O)
    cu = cuscino(coll, M, 0.5, nome + 'Cuscino'); cu.parent = O; cu.location = (0, -0.05, z0 + 0.46)
    po = pomodoro(coll, M, 0.22, nome + 'Pomodoro'); po.parent = O; po.location = (0, -0.05, z0 + 0.46 + 0.15)
    P = empty(nome + 'Sportello', (-w, -d, (z0 + z1) / 2), O, coll); P.rotation_euler = (0, 0, -aperta)
    box(nome + 'Porta', (0, -0.13, -(z1 - z0) / 2), (2 * w, 0, (z1 - z0) / 2), M['ferro'], coll, P)
    R_ = empty(nome + 'Ruota', (w, -0.17, 0.05), P, coll); R_.rotation_euler = (PI / 2, 0, 0)
    props024.anello(nome + 'Volante', 0.26, 0.028, M['oro'], coll, parent=R_)
    for k in range(3): props023.tubo(nome + 'Raggio%d' % k, (-0.26 * math.cos(k * PI / 3), -0.26 * math.sin(k * PI / 3), 0), (0.26 * math.cos(k * PI / 3), 0.26 * math.sin(k * PI / 3), 0), 0.02, M['oro'], coll, parent=R_)
    cyl(nome + 'Mozzo', 0.07, 0.08, (0, 0, 0), M['oro'], coll, parent=R_)
    for k in range(3): cyl(nome + 'Perno%d' % k, 0.05, 0.14, (2 * w + 0.02, -0.065, -0.5 + 0.5 * k), M['acciaio'], coll, rot=(0, PI / 2, 0), parent=P)
    ca = cartellino(coll, M, fnt, nome=nome + 'Prezzo', h=0.0, larg=0.66, alt=0.36); ca.parent = O; ca.location = (0.25, -d - 0.07, z0 - 0.42)
    return dict(root=O, pomodoro=po, cartellino=ca, sportello=P, centro=Vector((0, 0, 1.3)))


def banchiere(coll, nome='Banchiere', altezza=2.1):
    import gente027
    look = dict(pelle=gente027.P_CHIARA, capelli=gente027.C_GRIGI, taglio='pelato', tipo='giacca', maglia=(0.16, 0.17, 0.22), c2=gente027.BIANCO, gambe='lunghi', panta=(0.12, 0.12, 0.16),
                scarpe=gente027.NERO, extra=('occhiali', 'baffi'))
    col, R = gente027.pupazzo(nome + 'Modello', look)
    return gente027.copia(coll, col, 0, 0, altezza=altezza, nome=nome), R


def _parete(coll, M, nome, parent, scritta, fnt, larg=7.0, y=1.6, H=4.6, mat='verde_banca'):
    box(nome + 'Parete', (-larg, y, 0), (larg, y + 0.1, H), M[mat], coll, parent)
    box(nome + 'Zoccolo', (-larg, y - 0.03, 0), (larg, y, 1.0), M['legno_scuro'], coll, parent)
    box(nome + 'Cornice', (-larg, y - 0.05, 1.0), (larg, y, 1.08), M['oro'], coll, parent)
    props023.testo(coll, nome + 'Scritta', scritta, 0.62, M['oro'], (0, y - 0.03, H - 0.9), parent=parent, font=fnt, estrudi=0.02)
    box(nome + 'Pavimento', (-larg, -9.0, -0.05), (larg, y, 0.0), material('M28_pav_banca', (0.42, 0.36, 0.30), rough=0.3, coat=0.4), coll, parent)


def timbro(coll, M, fnt, nome='Timbro', testo='MUTUO'):
    """timbro grosso da ufficio: origine sotto la gomma."""
    O = empty(nome, (0, 0, 0), None, coll)
    props024.scatola_tonda(nome + 'Gomma', 0.34, 0.2, 0.05, 0.015, M['inchiostro'], coll, O, (0, 0, 0.025))
    props024.scatola_tonda(nome + 'Blocco', 0.38, 0.24, 0.10, 0.03, M['legno_scuro'], coll, O, (0, 0, 0.10))
    props023.tubo(nome + 'Manico', (0, 0, 0.14), (0, 0, 0.33), 0.04, M['legno_scuro'], coll, parent=O); shape(nome + 'Pomo', 'sphere', (0, 0, 0.36), (0.085, 0.085, 0.07), (0, 0, 0), O, M['legno_scuro'], coll)
    return O


def contratto(coll, M, fnt, nome='Contratto', timbrato=True):
    """foglio del mutuo steso sul piano (origine al centro, testo leggibile da -Y guardando dall'alto)."""
    O = empty(nome, (0, 0, 0), None, coll)
    box(nome + 'Foglio', (-0.3, -0.42, 0), (0.3, 0.42, 0.006), M['bianco'], coll, O)
    props023.testo(coll, nome + 'Titolo', 'MUTUO', 0.13, M['nero'], (0, 0.28, 0.008), rot=(0, 0, 0), parent=O, font=fnt, estrudi=0.001)
    for k in range(5): box(nome + 'Riga%d' % k, (-0.22, 0.13 - k * 0.07, 0.006), (0.22 - 0.06 * (k % 2), 0.15 - k * 0.07, 0.008), M['acciaio'], coll, O)
    if timbrato:
        t = props023.testo(coll, nome + 'Timbro', '30 ANNI', 0.11, M['inchiostro'], (0.02, -0.26, 0.009), rot=(0, 0, 0.22), parent=O, font=fnt, estrudi=0.001)
        t2 = props023.testo(coll, nome + 'Timbro2', 'TASSO FISSO', 0.062, M['inchiostro'], (-0.02, 0.2, 0.009), rot=(0, 0, -0.16), parent=O, font=fnt, estrudi=0.001)
    return O


def sportello(coll, M, fnt, nome='Sportello'):
    """B1: sportello della banca col vetro. Il banchiere sta dietro (y > 0), Pippo davanti (y < -0.6)."""
    O = empty(nome, (0, 0, 0), None, coll); _parete(coll, M, nome, O, 'BANCA', fnt)
    box(nome + 'Banco', (-2.3, -0.35, 0), (2.3, 0.35, 1.25), M['legno_scuro'], coll, O); box(nome + 'Piano', (-2.4, -0.48, 1.25), (2.4, 0.42, 1.33), M['marmo'], coll, O)
    for sx in (-1, 1): box(nome + 'Montante', (sx * 1.25 - 0.04, -0.06, 1.33), (sx * 1.25 + 0.04, 0.02, 3.0), M['oro'], coll, O)
    box(nome + 'Traversa', (-1.29, -0.06, 2.96), (1.29, 0.02, 3.04), M['oro'], coll, O)
    v = box(nome + 'Vetro', (-1.21, -0.03, 1.55), (1.21, -0.01, 2.96), M['vetro'], coll, O); v.visible_shadow = False
    box(nome + 'Targa', (-0.55, -0.50, 0.72), (0.55, -0.35, 1.05), M['oro'], coll, O)
    props023.testo(coll, nome + 'TargaT', 'MUTUI', 0.2, M['nero'], (0, -0.51, 0.885), parent=O, font=fnt, estrudi=0.004)
    cyl(nome + 'Campanello', 0.07, 0.05, (1.7, -0.2, 1.36), M['oro'], coll, parent=O); shape(nome + 'CampanelloS', 'sphere', (1.7, -0.2, 1.38), (0.07, 0.07, 0.055), (0, 0, 0), O, M['oro'], coll)
    co = contratto(coll, M, fnt, nome + 'Contratto'); co.parent = O; co.location = (0.0, -0.05, 1.335); co.scale = (0.75, 0.75, 1)
    ti = timbro(coll, M, fnt, nome + 'Timbro'); ti.parent = O; ti.location = (-0.85, 0.05, 1.335)
    return dict(root=O, contratto=co, timbro=ti, banchiere=Vector((0, 1.0, 0)), cliente=Vector((0, -1.5, 0)), centro=Vector((0, 0, 1.7)))


def scrivania(coll, M, fnt, nome='Direttore'):
    """B2: scrivania enorme del direttore, pila di carte piu' alta di Pippo, poltrona di pelle."""
    O = empty(nome, (0, 0, 0), None, coll); _parete(coll, M, nome, O, 'BANCA', fnt, mat='verde_banca')
    box(nome + 'Piano', (-2.1, -0.75, 1.15), (2.1, 0.75, 1.27), M['legno_scuro'], coll, O)
    for sx in (-1, 1): box(nome + 'Fianco', (sx * 1.95 - 0.1, -0.68, 0), (sx * 1.95 + 0.1, 0.68, 1.15), M['legno_scuro'], coll, O)
    box(nome + 'Fronte', (-1.95, -0.66, 0.1), (1.95, -0.6, 1.15), M['legno'], coll, O)
    box(nome + 'Bordo', (-2.1, -0.76, 1.13), (2.1, -0.74, 1.27), M['oro'], coll, O)
    import random; rnd = random.Random(28)
    for k in range(46):                                            # la pila di carte
        obj(nome + 'Carta%d' % k, box_c(), (-1.35 + rnd.uniform(-0.03, 0.03), 0.1 + rnd.uniform(-0.03, 0.03), 1.27 + 0.02 + k * 0.04), (0.6, 0.84, 0.036), M['bianco'], coll, rot=(0, 0, rnd.uniform(-0.2, 0.2)), parent=O)
    box(nome + 'Targhetta', (0.55, -0.62, 1.27), (1.55, -0.5, 1.50), M['oro'], coll, O)
    props023.testo(coll, nome + 'TarghettaT', 'DIRETTORE', 0.12, M['nero'], (1.05, -0.63, 1.385), parent=O, font=fnt, estrudi=0.004)
    props024.scatola_tonda(nome + 'Schienale', 1.3, 0.25, 2.3, 0.1, M['pelle'], coll, O, (0, 1.2, 1.75))
    for i in range(3):
        for j in range(4): shape(nome + 'Bottone', 'sphere', (-0.4 + i * 0.4, 1.06, 1.3 + j * 0.42), (0.04, 0.03, 0.04), (0, 0, 0), O, M['oro'], coll)
    co = contratto(coll, M, fnt, nome + 'Contratto'); co.parent = O; co.location = (0.0, -0.2, 1.272)
    ti = timbro(coll, M, fnt, nome + 'Timbro'); ti.parent = O; ti.location = (0.75, 0.1, 1.272); ti.scale = (1.4, 1.4, 1.4)
    return dict(root=O, contratto=co, timbro=ti, banchiere=Vector((0, 0.75, 0)), cliente=Vector((0, -1.9, 0)), centro=Vector((0, 0, 1.7)))


def motorino(coll, M, colore=(0.85, 0.08, 0.06), nome='Motorino'):
    """Il motorino di Gualtiero, fatto a mano. Lungo 1,9 m, muso verso -Y, origine a terra sotto il centro. Restituisce dict root, ruote, manubrio."""
    O = empty(nome, (0, 0, 0), None, coll); mc = material('M28_moto_%d_%d_%d' % tuple(int(c * 255) for c in colore), colore, rough=0.25, coat=0.8)
    ruote = []
    for k, y in enumerate((-0.68, 0.62)):
        r = empty(nome + 'Ruota%d' % k, (0, y, 0.27), O, coll); ruote.append(r)
        cyl(nome + 'Gomma%d' % k, 0.27, 0.13, (0, 0, 0), M['gomma'], coll, rot=(0, PI / 2, 0), parent=r); cyl(nome + 'Cerchio%d' % k, 0.15, 0.14, (0, 0, 0), M['acciaio'], coll, rot=(0, PI / 2, 0), parent=r)
    props024.scatola_tonda(nome + 'Scocca', 0.44, 0.92, 0.46, 0.14, mc, coll, O, (0, 0.42, 0.56))
    shape(nome + 'Coda', 'sphere', (0, 0.80, 0.58), (0.22, 0.20, 0.22), (0, 0, 0), O, mc, coll)
    for sx in (-1, 1): props023.tubo(nome + 'Forcella', (sx * 0.09, -0.68, 0.27), (sx * 0.09, -0.60, 0.95), 0.022, M['acciaio'], coll, parent=O)
    props024.scatola_tonda(nome + 'Sella', 0.34, 0.74, 0.13, 0.05, M['nero'], coll, O, (0, 0.36, 0.86))
    props024.scatola_tonda(nome + 'Pedana', 0.42, 0.62, 0.07, 0.03, mc, coll, O, (0, -0.22, 0.30))
    props024.scatola_tonda(nome + 'Scudo', 0.56, 0.12, 0.86, 0.06, mc, coll, O, (0, -0.56, 0.72), rot=(-0.20, 0, 0))
    shape(nome + 'Parafango', 'sphere', (0, -0.68, 0.44), (0.11, 0.32, 0.17), (0, 0, 0), O, mc, coll)
    man = empty(nome + 'Manubrio', (0, -0.58, 1.12), O, coll)
    props023.tubo(nome + 'Piantone', (0, 0.02, -0.12), (0, 0.06, 0.2), 0.035, M['acciaio'], coll, parent=man)
    cyl(nome + 'Barra', 0.028, 0.86, (0, 0.06, 0.2), M['acciaio'], coll, rot=(0, PI / 2, 0), parent=man)
    for sx in (-1, 1):
        cyl(nome + 'Manopola', 0.04, 0.2, (sx * 0.38, 0.06, 0.2), M['gomma'], coll, rot=(0, PI / 2, 0), parent=man)
        props023.tubo(nome + 'AstaSpecchio', (sx * 0.26, 0.06, 0.2), (sx * 0.34, 0.04, 0.44), 0.012, M['acciaio'], coll, parent=man)
        shape(nome + 'Specchio', 'sphere', (sx * 0.35, 0.03, 0.47), (0.075, 0.02, 0.06), (0, 0, 0), man, M['acciaio'], coll)
    shape(nome + 'FaroCassa', 'sphere', (0, -0.02, 0.10), (0.13, 0.12, 0.12), (0, 0, 0), man, mc, coll)
    shape(nome + 'Faro', 'sphere', (0, -0.10, 0.10), (0.095, 0.05, 0.095), (0, 0, 0), man, M['luce'], coll)
    props023.tubo(nome + 'Marmitta', (0.24, 0.35, 0.3), (0.24, 0.98, 0.34), 0.05, M['acciaio'], coll, parent=O)
    box(nome + 'Targa', (-0.11, 0.875, 0.5), (0.11, 0.89, 0.66), M['bianco'], coll, O)
    shape(nome + 'Stop', 'sphere', (0, 0.87, 0.74), (0.07, 0.03, 0.045), (0, 0, 0), O, M['rosso'], coll)
    return dict(root=O, ruote=ruote, manubrio=man)


# ------------------------------------------------------------------ oggetti delle singole scene
def sacco(coll, M, fnt, nome='Sacco'):
    """sacco dei soldi col simbolo dell'euro: origine sotto."""
    O = empty(nome, (0, 0, 0), None, coll)
    shape(nome + 'Pancia', 'sphere', (0, 0, 0.33), (0.36, 0.33, 0.35), (0, 0, 0), O, M['sacco'], coll)
    shape(nome + 'Collo', 'cone', (0, 0, 0.56), (0.17, 0.17, 0.22), (0, 0, 0), O, M['sacco'], coll)
    shape(nome + 'Bocca', 'sphere', (0, 0, 0.80), (0.16, 0.16, 0.06), (0, 0, 0), O, M['sacco'], coll)
    props024.anello(nome + 'Corda', 0.10, 0.02, M['legno_scuro'], coll, parent=O, loc=(0, 0, 0.72))
    props023.testo(coll, nome + 'Euro', '€', 0.36, M['verde_banca'], (0, -0.335, 0.34), parent=O, font=fnt, estrudi=0.01)
    return O


def podio(coll, M, fnt, nome='Podio', scritta='COSE IMPORTANTISSIME'):
    """leggio da comizio: chi parla sta dietro (y > 0.45), fronte -Y."""
    O = empty(nome, (0, 0, 0), None, coll)
    props024.scatola_tonda(nome + 'Corpo', 1.0, 0.5, 1.15, 0.05, M['legno_scuro'], coll, O, (0, 0, 0.575))
    obj(nome + 'Piano', box_c(), (0, 0.02, 1.2), (1.1, 0.62, 0.06), M['legno_scuro'], coll, rot=(0.25, 0, 0), parent=O)
    box(nome + 'Targa', (-0.42, -0.262, 0.62), (0.42, -0.25, 0.98), M['oro'], coll, O)
    props023.testo(coll, nome + 'T1', 'MINISTERO DELLE', 0.07, M['nero'], (0, -0.268, 0.88), parent=O, font=fnt, estrudi=0.003)
    props023.testo(coll, nome + 'T2', scritta.split(' ')[0], 0.10, M['nero'], (0, -0.268, 0.78), parent=O, font=fnt, estrudi=0.003)
    props023.testo(coll, nome + 'T3', ' '.join(scritta.split(' ')[1:]), 0.075, M['nero'], (0, -0.268, 0.68), parent=O, font=fnt, estrudi=0.003)
    for sx in (-1, 1):
        props023.tubo(nome + 'Asta', (sx * 0.22, -0.1, 1.2), (sx * 0.14, -0.2, 1.52), 0.012, M['nero'], coll, parent=O)
        shape(nome + 'Mic', 'sphere', (sx * 0.14, -0.2, 1.54), (0.045, 0.045, 0.055), (0, 0, 0), O, M['ferro'], coll)
    return O


def fascicolo(coll, M, fnt, nome='Fascicolo', righe=('INCHIESTA', 'SU ROSPINA')):
    """cartella in piedi (origine in basso al centro), faccia verso -Y."""
    O = empty(nome, (0, 0, 0), None, coll)
    props024.scatola_tonda(nome + 'Cartella', 0.78, 0.05, 0.98, 0.02, M['cartone'], coll, O, (0, 0, 0.49))
    box(nome + 'Linguetta', (0.1, -0.02, 0.98), (0.36, 0.02, 1.05), M['cartone'], coll, O)
    box(nome + 'Etichetta', (-0.32, -0.032, 0.52), (0.32, -0.024, 0.86), M['bianco'], coll, O)
    props023.testo(coll, nome + 'T1', righe[0], 0.105, M['nero'], (0, -0.036, 0.75), parent=O, font=fnt, estrudi=0.002)
    props023.testo(coll, nome + 'T2', righe[1], 0.075, M['nero'], (0, -0.036, 0.62), parent=O, font=fnt, estrudi=0.002)
    return O


def timbrata(coll, M, fnt, testo='ASSOLTA', nome='Timbrata', size=0.2):
    """scritta rossa da timbro con la cornice (origine al centro, faccia verso -Y)."""
    O = empty(nome, (0, 0, 0), None, coll); w = 0.62 * size * len(testo) + 0.12; h = size * 1.35
    props023.testo(coll, nome + 'T', testo, size, M['inchiostro'], (0, 0, 0), parent=O, font=fnt, estrudi=0.006)
    for z in (-h / 2, h / 2): box(nome + 'O', (-w / 2, -0.006, z - 0.012), (w / 2, 0.006, z + 0.012), M['inchiostro'], coll, O)
    for x in (-w / 2, w / 2): box(nome + 'V', (x - 0.012, -0.006, -h / 2), (x + 0.012, 0.006, h / 2), M['inchiostro'], coll, O)
    return O


def sgabello(coll, M, nome='Sgabello', h=0.6):
    O = empty(nome, (0, 0, 0), None, coll)
    props024.tornio(nome + 'Corpo', [(0, 0), (0.55, 0), (0.55, 0.04), (0.36, h - 0.05), (0.40, h - 0.04), (0.40, h), (0, h)], coll, [M['rosso'], M['oro']], seg=40, mat_idx=lambda z: 1 if (z < 0.05 or z > h - 0.06) else 0, parent=O)
    for k in range(6):
        a = k * PI / 3; shape(nome + 'Stella', 'sphere', (0.455 * math.cos(a), 0.455 * math.sin(a), h * 0.48), (0.06, 0.06, 0.06), (0, 0, 0), O, M['carta'], coll)
    return O


def lavagna(coll, M, fnt, righe=('LEZIONE 1', 'RUBARE'), nome='Lavagna'):
    """lavagna sul cavalletto, faccia verso -Y, origine a terra."""
    O = empty(nome, (0, 0, 0), None, coll)
    box(nome + 'Cornice', (-0.95, -0.03, 0.95), (0.95, 0.03, 2.25), M['legno'], coll, O); box(nome + 'Nero', (-0.87, -0.04, 1.03), (0.87, -0.02, 2.17), M['lavagna'], coll, O)
    for sx in (-1, 1): props023.tubo(nome + 'Gamba', (sx * 0.8, 0.0, 2.2), (sx * 0.95, 0.25 * 0, 0), 0.035, M['legno'], coll, parent=O)
    props023.tubo(nome + 'GambaD', (0, 0.03, 2.1), (0, 0.9, 0), 0.035, M['legno'], coll, parent=O)
    props023.testo(coll, nome + 'T1', righe[0], 0.2, M['bianco'], (0, -0.045, 1.9), parent=O, font=fnt, estrudi=0.002)
    props023.testo(coll, nome + 'T2', righe[1], 0.3, M['carta'], (0.0, -0.045, 1.52), parent=O, font=fnt, estrudi=0.002)
    p = pomodoro(coll, M, 0.1, nome + 'Pom'); p.parent = O; p.location = (-0.5, -0.05, 1.08); p.scale = (1, 0.15, 1)
    props023.tubo(nome + 'Freccia', (-0.3, -0.045, 1.2), (0.35, -0.045, 1.2), 0.018, M['bianco'], coll, parent=O)
    shape(nome + 'Punta', 'cone', (0.35, -0.045, 1.2), (0.06, 0.02, 0.14), (0, PI / 2, 0), O, M['bianco'], coll)
    return O


def rotolo(coll, M, fnt, lung=5.0, nome='Rotolo', alto=1.3):
    """contratto lunghissimo: scende da (0, 0, alto) fino a terra e si srotola verso -Y per «lung» metri. Origine a terra sotto il capo alto."""
    O = empty(nome, (0, 0, 0), None, coll); w = 0.56
    box(nome + 'Giu', (-w / 2, -0.004, 0.0), (w / 2, 0.004, alto), M['bianco'], coll, O)
    box(nome + 'Terra', (-w / 2, -lung, 0.0), (w / 2, 0.0, 0.012), M['bianco'], coll, O)
    cyl(nome + 'Rullo', 0.09, w + 0.04, (0, -lung, 0.09), M['bianco'], coll, rot=(0, PI / 2, 0), parent=O)
    props023.testo(coll, nome + 'Titolo', 'MUTUO', 0.13, M['nero'], (0, -0.007, alto - 0.18), parent=O, font=fnt, estrudi=0.001)
    for k in range(6): box(nome + 'RigaG%d' % k, (-0.2, -0.007, alto - 0.42 - k * 0.12), (0.2 - 0.07 * (k % 2), -0.004, alto - 0.40 - k * 0.12), M['acciaio'], coll, O)
    n = int(lung / 0.62)
    for k in range(n):
        y = -0.35 - k * 0.62
        props023.testo(coll, nome + 'Rata%d' % k, 'RATA %d' % (k + 1), 0.1, M['nero'], (0, y, 0.014), rot=(0, 0, 0), parent=O, font=fnt, estrudi=0.001)
        for j in range(3): box(nome + 'Riga%d_%d' % (k, j), (-0.2, y - 0.14 - j * 0.08, 0.012), (0.2 - 0.06 * (j % 2), y - 0.125 - j * 0.08, 0.014), M['acciaio'], coll, O)
    t = timbrata(coll, M, fnt, '30 ANNI', nome + 'Timbro', size=0.11); t.parent = O; t.location = (0.02, -0.012, alto - 1.02); t.rotation_euler = (0, 0.2, 0)
    return O


def festone(coll, M, a, b, n=12, nome='Festone', cala=0.5):
    """bandierine colorate tra due punti."""
    a = Vector(a); b = Vector(b); O = empty(nome, (0, 0, 0), None, coll); col = ('tenda_r', 'tenda_g', 'tenda_a', 'tenda_v', 'tenda_b')
    pts = [a.lerp(b, i / n) - Vector((0, 0, cala * 4 * (i / n) * (1 - i / n))) for i in range(n + 1)]
    yaw = math.atan2(b.y - a.y, b.x - a.x)
    for i in range(n):
        props023.tubo(nome + 'Filo%d' % i, pts[i], pts[i + 1], 0.008, M['nero'], coll, parent=O)
        m = (pts[i] + pts[i + 1]) / 2
        shape(nome + 'Bandiera%d' % i, 'cone', (m.x, m.y, m.z), (0.16, 0.012, 0.36), (PI, 0, yaw), O, M[col[i % len(col)]], coll)
    return O


def zucchina(coll, M, nome='Zucchina', L=0.5):
    """una zucchina vera (non Eleonora): lunga L lungo Z, origine al centro."""
    O = empty(nome, (0, 0, 0), None, coll)
    shape(nome + 'Corpo', 'sphere', (0, 0, 0), (L * 0.15, L * 0.15, L * 0.5), (0, 0, 0), O, M['zucchina'], coll)
    shape(nome + 'Picciolo', 'cone', (0, 0, L * 0.46), (L * 0.06, L * 0.06, L * 0.14), (0, 0, 0), O, M['verde'], coll)
    return O


def sala_banca(coll, M, fnt, nome='Banca'):
    """La banca chiusa attorno allo sportello B1: pareti, soffitto, colonnine col cordone, orologio. Restituisce il dict dello sportello piu' 'soffitto'."""
    G = sportello(coll, M, fnt, nome); O = G['root']; L, H, Y0, Y1 = 7.0, 4.6, -9.0, 1.6
    for sx in (-1, 1): box(nome + 'ParLato', (sx * L - (0.1 if sx > 0 else 0), Y0, 0), (sx * L + (0.1 if sx < 0 else 0), Y1, H), M['verde_banca'], coll, O)
    box(nome + 'ParFronte', (-L, Y0 - 0.1, 0), (L, Y0, H), M['verde_banca'], coll, O)
    box(nome + 'ZoccoloF', (-L, Y0, 0), (L, Y0 + 0.03, 1.0), M['legno_scuro'], coll, O); box(nome + 'CorniceF', (-L, Y0, 1.0), (L, Y0 + 0.05, 1.08), M['oro'], coll, O)
    box(nome + 'Porta', (-0.9, Y0, 0), (0.9, Y0 + 0.06, 2.9), M['legno_scuro'], coll, O); shape(nome + 'Maniglia', 'sphere', (0.65, Y0 + 0.1, 1.3), (0.07, 0.07, 0.07), (0, 0, 0), O, M['oro'], coll)
    props023.testo(coll, nome + 'Uscita', 'USCITA', 0.22, M['oro'], (0, Y0 + 0.07, 3.25), rot=(PI / 2, 0, PI), parent=O, font=fnt, estrudi=0.01)
    G['soffitto'] = box(nome + 'Soffitto', (-L, Y0, H), (L, Y1, H + 0.1), M['bianco'], coll, O)
    for i, sx in enumerate((-1, 1)):
        _colonnina(coll, M, nome + 'Col%dA' % i, (sx * 2.2, -1.6), O); _colonnina(coll, M, nome + 'Col%dB' % i, (sx * 2.2, -4.6), O)
        _cordone(coll, M, nome + 'Cordone%d' % i, (sx * 2.2, -1.6, 0.98), (sx * 2.2, -4.6, 0.98), O, n=12)
    C_ = empty(nome + 'Orologio', (3.4, Y1 - 0.06, 3.1), O, coll); C_.rotation_euler = (PI / 2, 0, 0)
    cyl(nome + 'OroQ', 0.5, 0.06, (0, 0, 0), M['bianco'], coll, parent=C_); props024.anello(nome + 'OroB', 0.5, 0.045, M['oro'], coll, parent=C_)
    props023.tubo(nome + 'LancettaO', (0, 0, 0.04), (0.0, 0.26, 0.04), 0.022, M['nero'], coll, parent=C_); props023.tubo(nome + 'LancettaM', (0, 0, 0.04), (0.36, -0.1, 0.04), 0.016, M['nero'], coll, parent=C_)
    box(nome + 'Quadro', (-4.6, Y1 - 0.06, 1.9), (-2.6, Y1 - 0.02, 3.3), M['oro'], coll, O); box(nome + 'QuadroF', (-4.5, Y1 - 0.075, 2.0), (-2.7, Y1 - 0.05, 3.2), M['bianco'], coll, O)
    props023.testo(coll, nome + 'QuadroT1', 'MUTUI', 0.32, M['verde_banca'], (-3.6, Y1 - 0.08, 2.85), parent=O, font=fnt, estrudi=0.004)
    props023.testo(coll, nome + 'QuadroT2', 'FINO A', 0.16, M['nero'], (-3.6, Y1 - 0.08, 2.52), parent=O, font=fnt, estrudi=0.004)
    props023.testo(coll, nome + 'QuadroT3', '300 ANNI', 0.26, M['inchiostro'], (-3.6, Y1 - 0.08, 2.22), parent=O, font=fnt, estrudi=0.004)
    return G
