"""Oggetti del video 030 «Rospina o Castora?» (copione n. 32 v3: i bonus al posto delle riforme, la diga dell'opposizione). In scala con Pippo (circa 2,4 m). Fronte -Y.
Usa materiali e attrezzi di props028 (M = props028.mats028(A) + mats030(M, A)).
- monopattino(coll, M, tipo): 'S1' classico rosso, 'S2' elettrico nero e verde acqua, 'S3' elettrico giallo. Lungo 1,5 m, manubrio a 1,45 m, origine a terra al centro. dict root, manubrio, ruote.
- diga(coll, M, tipo, larg): 'D1' tronchi da castoro, 'D2' cemento con lo scarico e i tronchi sopra. Attraversa una strada larga «larg», origine a terra al centro. dict root, cima (altezza).
- strada(coll, M, lung, larg): pezzo di autostrada lungo Y con le righe e i guardrail.
- canotto(coll, M, tipo): 'K1' giallo, 'K2' arancione di salvataggio, 'K3' a papera. Lungo 3 m, origine sul pelo dell'acqua al centro. dict root, remi.
- acqua(coll, M, raggio): piano d'acqua lucido."""
import math, random
import bpy
from mathutils import Vector
from common import material, empty, shape
from set004 import obj, box_c, cyl
import props023, props024, props028
from props028 import box

PI = math.pi


def mats030(M, A=None):
    m = material
    M.update(asfalto=m('M30_asfalto', (0.10, 0.10, 0.11), rough=0.85), riga=m('M30_riga', (0.95, 0.95, 0.9), rough=0.6), guard=m('M30_guardrail', (0.62, 0.65, 0.68), rough=0.4, metallic=0.9),
             corteccia=m('M30_corteccia', (0.30, 0.19, 0.11), rough=0.9), taglio=m('M30_taglio', (0.86, 0.68, 0.42), rough=0.8), fango=m('M30_fango', (0.24, 0.16, 0.10), rough=0.95),
             cemento=m('M30_cemento', (0.62, 0.62, 0.60), rough=0.85), acqua=m('M30_acqua', (0.05, 0.32, 0.55), rough=0.06, spec=1.0, coat=1.0), schiuma=m('M30_schiuma', (0.9, 0.96, 1.0), rough=0.5),
             k_giallo=m('M30_canotto_giallo', (1.0, 0.80, 0.05), rough=0.35, coat=0.5), k_arancio=m('M30_canotto_arancio', (1.0, 0.36, 0.04), rough=0.35, coat=0.5), k_grigio=m('M30_canotto_fondo', (0.25, 0.27, 0.30), rough=0.6),
             becco=m('M30_becco', (1.0, 0.45, 0.05), rough=0.4), s_rosso=m('M30_mono_rosso', (0.85, 0.07, 0.05), rough=0.3, coat=0.6), s_nero=m('M30_mono_nero', (0.05, 0.05, 0.06), rough=0.35, coat=0.5),
             s_acqua=m('M30_mono_verdeacqua', (0.05, 0.85, 0.75), rough=0.3, emit=(0.05, 0.85, 0.75), emit_strength=1.5), s_giallo=m('M30_mono_giallo', (1.0, 0.78, 0.05), rough=0.3, coat=0.6), foglia=m('M30_foglia', (0.16, 0.45, 0.12), rough=0.7))
    if A is not None:
        for k, aid, d in (('corteccia', 'bark_brown_02', 1.0), ('cemento', 'Concrete034', 2.0)):
            try: M[k] = A.materiale(aid, dimensione=d)
            except Exception as e: print('texture mancante', aid, e)
    return M


def monopattino(coll, M, tipo='S1', nome='Monopattino'):
    O = empty(nome, (0, 0, 0), None, coll); el = tipo != 'S1'; mc = M[dict(S1='s_rosso', S2='s_nero', S3='s_giallo')[tipo]]; rr = 0.13 if el else 0.10
    ruote = []
    for k, y in enumerate((-0.62, 0.62)):
        r = empty(nome + 'Ruota%d' % k, (0, y, rr), O, coll); ruote.append(r)
        cyl(nome + 'Gomma%d' % k, rr, 0.07 if el else 0.045, (0, 0, 0), M['gomma'], coll, rot=(0, PI / 2, 0), parent=r); cyl(nome + 'Mozzo%d' % k, rr * 0.5, 0.08 if el else 0.05, (0, 0, 0), M['acciaio'] if not el else M['s_acqua' if tipo == 'S2' else 'acciaio'], coll, rot=(0, PI / 2, 0), parent=r)
    props024.scatola_tonda(nome + 'Pedana', 0.24 if el else 0.17, 0.98, 0.09 if el else 0.04, 0.02, mc, coll, O, (0, 0.02, rr + (0.02 if el else 0.03)))
    box(nome + 'Grip', (-0.09 if el else -0.06, -0.38, rr + (0.065 if el else 0.05)), (0.09 if el else 0.06, 0.42, rr + (0.075 if el else 0.058)), M['gomma'], coll, O)
    shape(nome + 'Parafango', 'sphere', (0, 0.62, rr + 0.06), (0.06, 0.2, 0.09), (0, 0, 0), O, mc, coll)
    man = empty(nome + 'Manubrio', (0, -0.60, rr + 0.1), O, coll)
    props023.tubo(nome + 'Forcella', (0, 0.02, -0.08), (0, -0.02, 0.2), 0.035 if el else 0.025, mc, coll, parent=man)
    props023.tubo(nome + 'Piantone', (0, -0.02, 0.2), (0, 0.06, 1.25), 0.03 if el else 0.02, M['acciaio'] if not el else mc, coll, parent=man)
    cyl(nome + 'Barra', 0.02, 0.56, (0, 0.06, 1.25), M['acciaio'], coll, rot=(0, PI / 2, 0), parent=man)
    for sx in (-1, 1): cyl(nome + 'Manopola', 0.03, 0.15, (sx * 0.24, 0.06, 1.25), M['gomma'], coll, rot=(0, PI / 2, 0), parent=man)
    if el:
        props024.scatola_tonda(nome + 'Schermo', 0.12, 0.05, 0.08, 0.015, M['s_nero'], coll, man, (0, 0.04, 1.31)); box(nome + 'SchermoLuce', (-0.045, 0.012, 1.285), (0.045, 0.016, 1.335), M['s_acqua'], coll, man)
        shape(nome + 'Faro', 'sphere', (0, -0.03, 1.05), (0.05, 0.03, 0.05), (0, 0, 0), man, M['luce'], coll)
        if tipo == 'S2':
            for sx in (-1, 1): box(nome + 'Led', (sx * 0.121, -0.4, rr + 0.03), (sx * 0.125, 0.45, rr + 0.045), M['s_acqua'], coll, O)
        shape(nome + 'Stop', 'sphere', (0, 0.80, rr + 0.1), (0.04, 0.02, 0.025), (0, 0, 0), O, M['rosso'], coll)
    else:
        shape(nome + 'Campanello', 'sphere', (0.14, 0.03, 1.3), (0.045, 0.045, 0.035), (0, 0, 0), man, M['acciaio'], coll)
    return dict(root=O, manubrio=man, ruote=ruote)


def strada(coll, M, lung=60.0, larg=10.0, nome='Autostrada'):
    O = empty(nome, (0, 0, 0), None, coll)
    box(nome + 'Asfalto', (-larg / 2, -lung / 2, -0.05), (larg / 2, lung / 2, 0.02), M['asfalto'], coll, O)
    n = int(lung / 4)
    for k in range(n):
        for x in (-larg / 6, larg / 6): box(nome + 'Riga', (x - 0.08, -lung / 2 + k * 4 + 0.6, 0.02), (x + 0.08, -lung / 2 + k * 4 + 2.6, 0.03), M['riga'], coll, O)
    for sx in (-1, 1):
        box(nome + 'Bordo', (sx * (larg / 2 - 0.35) - 0.07, -lung / 2, 0.02), (sx * (larg / 2 - 0.35) + 0.07, lung / 2, 0.03), M['riga'], coll, O)
        box(nome + 'Lama', (sx * (larg / 2 + 0.15) - 0.03, -lung / 2, 0.55), (sx * (larg / 2 + 0.15) + 0.03, lung / 2, 0.85), M['guard'], coll, O)
        for k in range(int(lung / 3) + 1): box(nome + 'Paletto', (sx * (larg / 2 + 0.2) - 0.05, -lung / 2 + k * 3 - 0.05, 0), (sx * (larg / 2 + 0.2) + 0.05, -lung / 2 + k * 3 + 0.05, 0.8), M['guard'], coll, O)
    return O


def _tronco(coll, M, nome, a, b, r, parent):
    a = Vector(a); b = Vector(b); props023.tubo(nome, a, b, r, M['corteccia'], coll, parent=parent)
    d = (b - a).normalized()
    for k, p in enumerate((a, b)):
        e = empty(nome + 'T%d' % k, tuple(p), parent, coll); e.rotation_mode = 'QUATERNION'; e.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d)
        cyl(nome + 'Taglio%d' % k, r * 0.93, 0.03, (0, 0, 0), M['taglio'], coll, parent=e)


def diga(coll, M, tipo='D1', larg=10.0, nome='Diga', seme=30):
    """La diga della Castora di traverso sull'autostrada. D1: tutta tronchi rosicchiati (a punta), rami e fango. D2: muro di cemento con lo scarico, tronchi in cima."""
    O = empty(nome, (0, 0, 0), None, coll); rnd = random.Random(seme); W = larg / 2 + 0.9
    if tipo == 'D1':
        H = 3.3; n = 0
        for strato in range(7):
            z = 0.28 + strato * 0.46; prof = 1.5 * (1 - strato / 8.0)
            for j in range(3 - strato // 3):
                y = (j - (2 - strato // 3) / 2) * prof * 0.75 + rnd.uniform(-0.15, 0.15); L = rnd.uniform(0.5, 0.95) * W; cx = rnd.uniform(-(W - L), W - L); r = rnd.uniform(0.2, 0.3)
                a = (cx - L, y + rnd.uniform(-0.5, 0.5), z + rnd.uniform(-0.08, 0.08)); b = (cx + L, y + rnd.uniform(-0.5, 0.5), z + rnd.uniform(-0.08, 0.08)); _tronco(coll, M, nome + 'Tr%d' % n, a, b, r, O); n += 1
        for k in range(16):                                                 # pali rosicchiati a punta, piantati storti
            x = rnd.uniform(-W, W); y = rnd.choice((-1, 1)) * rnd.uniform(0.9, 1.6); h = rnd.uniform(1.6, 3.4); r = rnd.uniform(0.12, 0.2); inc = Vector((rnd.uniform(-0.25, 0.25), -0.35 * (1 if y > 0 else -1), 1)).normalized()
            a = Vector((x, y, 0)); b = a + inc * h; props023.tubo(nome + 'Palo%d' % k, a, b, r, M['corteccia'], coll, parent=O)
            e = empty(nome + 'PuntaE%d' % k, tuple(b), O, coll); e.rotation_mode = 'QUATERNION'; e.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(inc)
            shape(nome + 'Punta%d' % k, 'cone', (0, 0, 0), (r, r, r * 2.2), (0, 0, 0), e, M['taglio'], coll)
        for k in range(14):
            x = rnd.uniform(-W, W); z = rnd.uniform(0.2, 2.6); shape(nome + 'Fango%d' % k, 'sphere', (x, rnd.uniform(-0.9, 0.9) * (1 - z / 4), z), (rnd.uniform(0.3, 0.6), rnd.uniform(0.3, 0.5), rnd.uniform(0.2, 0.35)), (0, 0, 0), O, M['fango'], coll)
        for k in range(12):
            x = rnd.uniform(-W, W); a = Vector((x, rnd.uniform(-0.6, 0.6), rnd.uniform(1.8, 3.0))); b = a + Vector((rnd.uniform(-0.8, 0.8), rnd.uniform(-0.8, 0.8), rnd.uniform(0.5, 1.1)))
            props023.tubo(nome + 'Ramo%d' % k, a, b, 0.035, M['corteccia'], coll, parent=O); shape(nome + 'Foglie%d' % k, 'sphere', tuple(b), (0.22, 0.22, 0.16), (0, 0, 0), O, M['foglia'], coll)
    else:
        H = 3.6
        for k in range(8):                                                  # muro a gradoni, piu' largo sotto
            box(nome + 'Muro%d' % k, (-W, -1.3 + 0.13 * k, k * 0.45), (W, 1.3 - 0.13 * k, (k + 1) * 0.45), M['cemento'], coll, O)
        box(nome + 'Cima', (-W, -0.42, 3.6), (W, 0.42, 3.75), M['cemento'], coll, O)
        for sx in (-1, 0, 1):
            e = empty(nome + 'ScaricoE%d' % sx, (sx * W * 0.5, -1.0, 1.35), O, coll); e.rotation_euler = (PI / 2, 0, 0)
            cyl(nome + 'Scarico%d' % sx, 0.42, 0.5, (0, 0, 0), M['ferro'], coll, parent=e); cyl(nome + 'ScaricoBuio%d' % sx, 0.34, 0.52, (0, 0, 0), M['nero'], coll, parent=e)
            shape(nome + 'Getto%d' % sx, 'sphere', (sx * W * 0.5, -1.7, 0.65), (0.3, 0.6, 0.75), (0.5, 0, 0), O, M['acqua'], coll); shape(nome + 'Schiuma%d' % sx, 'sphere', (sx * W * 0.5, -2.2, 0.08), (0.7, 0.55, 0.12), (0, 0, 0), O, M['schiuma'], coll)
        for k in range(5):
            x = -W + (k + 0.5) * 2 * W / 5; _tronco(coll, M, nome + 'TrC%d' % k, (x - 1.3, rnd.uniform(-0.3, 0.3), 3.98), (x + 1.3, rnd.uniform(-0.3, 0.3), 3.98 + rnd.uniform(-0.05, 0.25)), 0.22, O)
        box(nome + 'Cartello', (-1.6, -1.34, 2.3), (1.6, -1.28, 3.1), M['carta'], coll, O)
        props023.testo(coll, nome + 'CartelloT', 'DIGA', 0.55, M['nero'], (0, -1.35, 2.7), parent=O, font=props028.font(), estrudi=0.01)
    return dict(root=O, cima=H)


def canotto(coll, M, tipo='K1', nome='Canotto'):
    """canotto gonfiabile: anello ovale (lungo 3 m, largo 1,9), fondo, corda, due remi. K3 ha testa e coda da papera."""
    O = empty(nome, (0, 0, 0), None, coll); mc = M['k_arancio' if tipo == 'K2' else 'k_giallo']
    a = props024.anello(nome + 'Tubo', 0.68, 0.27, mc, coll, parent=O, loc=(0, 0, 0.2), seg=48, segr=12); a.scale = (1.0, 1.75, 1.0)
    f = cyl(nome + 'Fondo', 0.72, 0.06, (0, 0, 0.06), M['k_grigio'], coll, parent=O); f.scale = (1.0, 1.75, 1.0)
    c = props024.anello(nome + 'Corda', 0.94, 0.018, M['bianco'], coll, parent=O, loc=(0, 0, 0.28), seg=48, segr=6); c.scale = (1.0, 1.48, 1.0)
    if tipo == 'K2':
        for k in range(8):
            an = k * PI / 4; e = empty(nome + 'FasciaE%d' % k, (0.68 * math.cos(an), 0.68 * 1.75 * math.sin(an), 0.2), O, coll); e.rotation_euler = (PI / 2, 0, an + PI / 2)
            props024.anello(nome + 'Fascia%d' % k, 0.275, 0.022, M['bianco'], coll, parent=e, seg=20, segr=6)
    if tipo == 'K3':
        shape(nome + 'Collo', 'sphere', (0, -1.25, 0.75), (0.2, 0.22, 0.55), (0.15, 0, 0), O, mc, coll); shape(nome + 'Testa', 'sphere', (0, -1.38, 1.3), (0.34, 0.34, 0.32), (0, 0, 0), O, mc, coll)
        shape(nome + 'Becco', 'sphere', (0, -1.72, 1.24), (0.2, 0.22, 0.07), (0, 0, 0), O, M['becco'], coll)
        for sx in (-1, 1): shape(nome + 'Occhio', 'sphere', (sx * 0.2, -1.6, 1.42), (0.085, 0.07, 0.1), (0, 0, 0), O, M['bianco'], coll); shape(nome + 'Pupilla', 'sphere', (sx * 0.22, -1.655, 1.42), (0.045, 0.03, 0.055), (0, 0, 0), O, M['nero'], coll)
        shape(nome + 'Coda', 'cone', (0, 1.3, 0.3), (0.3, 0.14, 0.6), (-0.9, 0, 0), O, mc, coll)
    remi = []
    for sx in (-1, 1):
        r = empty(nome + 'Remo%d' % (0 if sx < 0 else 1), (sx * 0.9, 0.1, 0.45), O, coll); r.rotation_euler = (0, sx * 0.5, 0); remi.append(r)
        props023.tubo(nome + 'Asta', (-sx * 0.5, 0, 0), (sx * 1.0, 0, 0), 0.025, M['legno'], coll, parent=r); shape(nome + 'Pala', 'sphere', (sx * 1.15, 0, 0), (0.24, 0.035, 0.13), (0, 0, 0), r, M['rosso'], coll)
    return dict(root=O, remi=remi)


def acqua(coll, M, raggio=80.0, z=0.0, nome='Acqua'):
    return box(nome, (-raggio, -raggio, z - 0.5), (raggio, raggio, z), M['acqua'], coll)


# ------------------------------------------------------------------ i posti e gli oggetti delle scene
def _tenda(coll, M, nome, x0, x1, y, z, parent, n=8, cols=('tenda_r', 'tenda_b'), sporge=1.1):
    ww = (x1 - x0) / n
    for i in range(n): obj(nome + '%d' % i, box_c(), (x0 + (i + 0.5) * ww, y - sporge * 0.48, z - 0.12), (ww * 1.005, sporge, 0.04), M[cols[i % 2]], coll, rot=(0.25, 0, 0), parent=parent)


def palazzo(coll, M, fnt, A=None, nome='Palazzo', striscione=('ROSPINA', 'ANNO 5')):
    """Il palazzo da cui comanda Rospina. Origine a terra al centro della facciata (la facciata e' a y = 0, il palazzo va verso +Y).
    Balcone a 4,3 m (piano da x -2,8 a 2,8, sporge fino a y -1,7). dict root, balcone (punto sul piano), striscione."""
    O = empty(nome, (0, 0, 0), None, coll); mm = M['marmo']; mu = M.get('muro_palazzo') or material('M30_muro_palazzo', (0.93, 0.86, 0.70), rough=0.8)
    if A is not None:
        try: mu = A.materiale('painted_plaster_wall', dimensione=4.0)
        except Exception as e: print('texture', e)
    box(nome + 'Corpo', (-7.5, 0, 0), (7.5, 4.5, 9.2), mu, coll, O); box(nome + 'Zoccolo', (-7.6, -0.08, 0), (7.6, 4.5, 1.0), mm, coll, O)
    for x in (-6.6, -4.2, 4.2, 6.6):
        cyl(nome + 'Colonna', 0.38, 8.2, (x, -0.7, 4.1 + 0.0), mm, coll, parent=O); box(nome + 'Base', (x - 0.55, -1.25, 0), (x + 0.55, -0.15, 0.3), mm, coll, O); box(nome + 'Capitello', (x - 0.55, -1.25, 8.2), (x + 0.55, -0.15, 8.5), mm, coll, O)
    box(nome + 'Cornicione', (-8.0, -1.4, 8.5), (8.0, 4.7, 9.2), mm, coll, O)
    for k in range(6): box(nome + 'Timpano%d' % k, (-8.0 + k * 1.33, -1.3, 9.2 + k * 0.38), (8.0 - k * 1.33, 4.6, 9.2 + (k + 1) * 0.38), mm, coll, O)
    box(nome + 'Portone', (-1.3, -0.06, 0), (1.3, 0.1, 3.3), M['legno_scuro'], coll, O); box(nome + 'PortoneCornice', (-1.5, -0.04, 0), (1.5, 0.05, 3.5), M['oro'], coll, O)
    for k in range(3): box(nome + 'Gradino%d' % k, (-2.4 + 0.3 * k, -1.5 + 0.4 * k, 0), (2.4 - 0.3 * k, 0, 0.14 * (k + 1)), mm, coll, O)
    box(nome + 'Balcone', (-2.8, -1.7, 4.08), (2.8, 0, 4.3), mm, coll, O)
    for sx in (-1, 1): box(nome + 'Mensola', (sx * 2.2 - 0.2, -1.5, 3.6), (sx * 2.2 + 0.2, 0, 4.08), mm, coll, O)
    box(nome + 'PortaBalcone', (-1.1, -0.06, 4.3), (1.1, 0.1, 7.3), M['legno_scuro'], coll, O); box(nome + 'PortaBalconeC', (-1.3, -0.04, 4.3), (1.3, 0.05, 7.5), M['oro'], coll, O)
    for k in range(15):
        x = -2.7 + k * (5.4 / 14); cyl(nome + 'Pilastrino', 0.07, 0.85, (x, -1.6, 4.3 + 0.425), mm, coll, parent=O)
    for sx in (-1, 1):
        for k in range(4): cyl(nome + 'PilastrinoL', 0.07, 0.85, (sx * 2.7, -1.6 + 0.4 * (k + 1), 4.725), mm, coll, parent=O)
        box(nome + 'CorrimanoL', (sx * 2.7 - 0.1, -1.7, 5.15), (sx * 2.7 + 0.1, 0, 5.27), mm, coll, O)
    box(nome + 'Corrimano', (-2.8, -1.7, 5.15), (2.8, -1.5, 5.27), mm, coll, O)
    for sx in (-1, 1):
        for z in (1.7, 5.3):
            box(nome + 'Finestra', (sx * 5.4 - 0.75, -0.05, z), (sx * 5.4 + 0.75, 0.05, z + 2.0), material('M30_finestra', (0.25, 0.45, 0.65), rough=0.1, spec=1.0), coll, O); box(nome + 'FinestraC', (sx * 5.4 - 0.9, -0.03, z - 0.15), (sx * 5.4 + 0.9, 0.03, z + 2.15), mm, coll, O)
    S_ = empty(nome + 'Striscione', (0, -1.74, 4.05), O, coll)
    box(nome + 'Telo', (-2.1, -0.02, -2.6), (2.1, 0.0, 0.0), M['velluto'], coll, S_); box(nome + 'TeloBordo', (-2.1, -0.03, -2.72), (2.1, 0.0, -2.6), M['oro'], coll, S_)
    props023.testo(coll, nome + 'StrT1', striscione[0], 0.42, M['oro'], (0, -0.03, -0.55), parent=S_, font=fnt, estrudi=0.01)
    props023.testo(coll, nome + 'StrT2', striscione[1], 0.78, M['oro'], (0, -0.03, -1.6), parent=S_, font=fnt, estrudi=0.01)
    for sx in (-1, 1):
        props023.tubo(nome + 'Asta', (sx * 6.0, 1.5, 11.0), (sx * 6.0, 1.5, 14.0), 0.05, M['acciaio'], coll, parent=O); box(nome + 'Bandiera', (sx * 6.0, 1.48, 12.9), (sx * 6.0 + 1.6, 1.52, 13.9), M['verde_banca'], coll, O)
    return dict(root=O, balcone=Vector((0, -0.85, 4.3)), striscione=S_)


def negozio(coll, M, fnt, nome='Negozio', insegna='MONOPATTINI'):
    """Il negozio dei monopattini: largo 8, facciata a y = 0. dict root, piedistallo (punto dove sta il monopattino, fuori dalla vetrina), porta."""
    O = empty(nome, (0, 0, 0), None, coll); mu = material('M30_muro_negozio', (0.45, 0.72, 0.85), rough=0.8)
    box(nome + 'Corpo', (-4, 0, 0), (4, 4.5, 5.6), mu, coll, O); box(nome + 'Tetto', (-4.2, -0.2, 5.6), (4.2, 4.7, 5.9), M['legno_scuro'], coll, O)
    v = box(nome + 'Vetrina', (-3.3, -0.04, 0.8), (0.5, 0.0, 3.4), M['vetro'], coll, O); v.visible_shadow = False
    box(nome + 'VetrinaBuio', (-3.3, 0.02, 0.8), (0.5, 0.1, 3.4), material('M30_vetrina_dentro', (0.12, 0.16, 0.22), rough=0.4), coll, O)
    for (a, b) in (((-3.45, -0.08, 0.65), (0.65, 0.05, 0.8)), ((-3.45, -0.08, 3.4), (0.65, 0.05, 3.55)), ((-3.45, -0.08, 0.65), (-3.3, 0.05, 3.55)), ((0.5, -0.08, 0.65), (0.65, 0.05, 3.55))): box(nome + 'Infisso', a, b, M['bianco'], coll, O)
    box(nome + 'Porta', (1.4, -0.05, 0), (3.0, 0.08, 3.2), M['legno_scuro'], coll, O); shape(nome + 'Maniglia', 'sphere', (1.65, -0.1, 1.5), (0.07, 0.07, 0.07), (0, 0, 0), O, M['oro'], coll)
    _tenda(coll, M, nome + 'Tenda', -3.8, 3.8, 0.0, 4.1, O, n=10, cols=('tenda_r', 'tenda_b'))
    box(nome + 'Insegna', (-3.4, -0.25, 4.45), (3.4, -0.12, 5.45), M['legno_scuro'], coll, O)
    props023.testo(coll, nome + 'InsegnaT', insegna, 0.6, M['carta'], (0, -0.27, 4.95), parent=O, font=fnt, estrudi=0.02)
    cyl(nome + 'Piedistallo', 1.0, 0.3, (-1.4, -2.2, 0.15), M['rosso'], coll, parent=O); cyl(nome + 'PiedistalloOro', 1.03, 0.06, (-1.4, -2.2, 0.3), M['oro'], coll, parent=O)
    return dict(root=O, piedistallo=Vector((-1.4, -2.2, 0.33)), porta=Vector((2.2, -0.6, 0)))


def supermercato(coll, M, fnt, nome='Super'):
    """Supermercato con la tettoia su quattro colonne (facciata a y = 0, tettoia verso -Y). dict root, tettoia (perno sul muro: rotation_euler.x > 0 la fa crollare in avanti), colonne."""
    O = empty(nome, (0, 0, 0), None, coll)
    box(nome + 'Corpo', (-7, 0, 0), (7, 9, 6.2), M['bianco'], coll, O); box(nome + 'Fascia', (-7.05, -0.05, 5.0), (7.05, 9.05, 6.2), M['rosso'], coll, O)
    v = box(nome + 'Vetrata', (-5.5, -0.04, 0.2), (5.5, 0.0, 3.6), M['vetro'], coll, O); v.visible_shadow = False
    box(nome + 'VetrataBuio', (-5.5, 0.02, 0.2), (5.5, 0.1, 3.6), material('M30_super_dentro', (0.75, 0.82, 0.7), rough=0.5), coll, O)
    for k in range(5): box(nome + 'Montante', (-5.5 + k * 2.75 - 0.06, -0.07, 0.2), (-5.5 + k * 2.75 + 0.06, 0.02, 3.6), M['acciaio'], coll, O)
    T_ = empty(nome + 'Tettoia', (0, 0, 4.45), O, coll)
    box(nome + 'TettoiaPiano', (-7.4, -4.6, -0.25), (7.4, 0, 0.25), M['rosso'], coll, T_); box(nome + 'TettoiaInsegna', (-6.0, -4.75, 0.25), (6.0, -4.5, 1.75), M['bianco'], coll, T_)
    props023.testo(coll, nome + 'InsegnaT', 'SUPERMERCATO', 0.85, M['rosso'], (0, -4.78, 1.0), parent=T_, font=fnt, estrudi=0.02)
    colonne = []
    for k, x in enumerate((-6.2, -2.1, 2.1, 6.2)):
        c = empty(nome + 'Colonna%d' % k, (x, -4.0, 0), O, coll); cyl(nome + 'ColonnaC%d' % k, 0.36, 4.2, (0, 0, 2.1), M['cemento'], coll, parent=c); cyl(nome + 'ColonnaB%d' % k, 0.5, 0.25, (0, 0, 0.125), M['cemento'], coll, parent=c); colonne.append(c)
    return dict(root=O, tettoia=T_, colonne=colonne)


def cannone_bonus(coll, M, fnt, nome='CannoneBonus'):
    """Il cannone spara-bonus di Rospina: dict root, canna (perno: rotation_euler.x = alzo, 0 = verso l'alto, 0.9 = in avanti e in alto), bocca (distanza della bocca dal perno)."""
    O = empty(nome, (0, 0, 0), None, coll)
    for sx in (-1, 1): cyl(nome + 'Ruota', 0.42, 0.12, (sx * 0.5, 0, 0.42), M['legno_scuro'], coll, rot=(0, PI / 2, 0), parent=O); cyl(nome + 'Mozzo', 0.12, 0.16, (sx * 0.5, 0, 0.42), M['oro'], coll, rot=(0, PI / 2, 0), parent=O)
    box(nome + 'Affusto', (-0.36, -0.5, 0.35), (0.36, 0.6, 0.6), M['legno_scuro'], coll, O)
    C_ = empty(nome + 'Canna', (0, 0, 0.75), O, coll)
    props024.tornio(nome + 'Tubo', [(0, -0.35), (0.3, -0.35), (0.4, -0.2), (0.4, 0.2), (0.34, 0.5), (0.32, 1.6), (0.4, 1.62), (0.42, 1.78), (0.3, 1.8), (0.28, 0.2), (0, 0.2)], coll, [M['rosso'], M['oro']], seg=40, mat_idx=lambda z: 1 if (z > 1.58 or -0.25 < z < -0.15) else 0, parent=C_)
    for k in range(5):
        a = k * 2 * PI / 5; shape(nome + 'Stella%d' % k, 'sphere', (0.345 * math.cos(a), 0.345 * math.sin(a), 0.9), (0.07, 0.07, 0.07), (0, 0, 0), C_, M['carta'], coll)
    return dict(root=O, canna=C_, bocca=1.8)


def buono(coll, M, fnt, righe=('BONUS', 'MONOPATTINO', '500 €'), nome='Buono'):
    """il buono del bonus: cartoncino 0,95 x 0,6, faccia verso -Y, origine al centro."""
    O = empty(nome, (0, 0, 0), None, coll); vb = material('M30_buono_verde', (0.10, 0.55, 0.25), rough=0.6)
    props024.scatola_tonda(nome + 'Bordo', 0.95, 0.02, 0.6, 0.05, vb, coll, O, (0, 0, 0)); props024.scatola_tonda(nome + 'Carta', 0.85, 0.024, 0.5, 0.04, M['carta'], coll, O, (0, 0, 0))
    props023.testo(coll, nome + 'T1', righe[0], 0.15, vb, (0, -0.015, 0.14), parent=O, font=fnt, estrudi=0.003)
    props023.testo(coll, nome + 'T2', righe[1], 0.075, M['nero'], (0, -0.015, 0.01), parent=O, font=fnt, estrudi=0.003)
    props023.testo(coll, nome + 'T3', righe[2], 0.15, M['inchiostro'], (0, -0.015, -0.14), parent=O, font=fnt, estrudi=0.003)
    return O


def cartellino_alato(coll, M, fnt, testo='€', mat='carta', nome='Alato'):
    """cartellino con le ali (i prezzi e le tasse che volano): dict root, ali (due perni, rotation_euler.y = battito)."""
    O = empty(nome, (0, 0, 0), None, coll)
    props024.scatola_tonda(nome + 'Carta', 0.62, 0.02, 0.4, 0.04, M[mat], coll, O, (0, 0, 0))
    props023.testo(coll, nome + 'T', testo, 0.2 if len(testo) > 2 else 0.28, M['inchiostro'], (0, -0.014, 0), parent=O, font=fnt, estrudi=0.003)
    ali = []
    for sx in (-1, 1):
        a = empty(nome + 'Ala%d' % (0 if sx < 0 else 1), (sx * 0.3, 0.01, 0.08), O, coll); ali.append(a)
        shape(nome + 'Piuma', 'sphere', (sx * 0.26, 0, 0.04), (0.28, 0.02, 0.13), (0, 0, 0), a, M['bianco'], coll); shape(nome + 'Piuma2', 'sphere', (sx * 0.2, 0, -0.07), (0.2, 0.02, 0.09), (0, 0, 0), a, M['bianco'], coll)
    return dict(root=O, ali=ali)


def portafoglio(coll, M, nome='Portafoglio'):
    """portafoglio aperto e vuoto, con la mosca: origine alla piega, si apre verso l'alto."""
    O = empty(nome, (0, 0, 0), None, coll); pe = material('M30_pelle_portafoglio', (0.32, 0.17, 0.08), rough=0.6)
    for sx in (-1, 1):
        e = empty(nome + 'Lembo%d' % sx, (0, 0, 0), O, coll); e.rotation_euler = (0, sx * 0.9, 0)
        props024.scatola_tonda(nome + 'Pelle', 0.36, 0.5, 0.03, 0.012, pe, coll, e, (sx * 0.19, 0, 0)); box(nome + 'Fodera', (sx * 0.03 if sx > 0 else -0.34, -0.22, 0.016), (0.34 if sx > 0 else -0.03, 0.22, 0.02), M['nero'], coll, e)
    m = empty(nome + 'Mosca', (0, 0, 0.45), O, coll); shape(nome + 'MoscaC', 'sphere', (0, 0, 0), (0.035, 0.05, 0.03), (0, 0, 0), m, M['nero'], coll)
    for sx in (-1, 1): shape(nome + 'MoscaA', 'sphere', (sx * 0.04, 0, 0.03), (0.045, 0.02, 0.008), (0, 0, 0), m, M['bianco'], coll)
    return dict(root=O, mosca=m)


def nuvola(coll, M, nome='Nuvola', gocce=14, seme=5):
    """nuvoletta grigia personale con la pioggia: dict root, gocce (lista di (oggetto, x, y, fase))."""
    O = empty(nome, (0, 0, 0), None, coll); gr = material('M30_nuvola', (0.42, 0.44, 0.50), rough=0.9); rnd = random.Random(seme)
    for (x, z, r) in ((0, 0, 0.5), (-0.5, -0.05, 0.38), (0.5, -0.05, 0.4), (-0.22, 0.25, 0.4), (0.25, 0.22, 0.36)): shape(nome + 'Sbuffo', 'sphere', (x, 0, z), (r, r * 0.8, r * 0.75), (0, 0, 0), O, gr, coll)
    G = []
    for k in range(gocce):
        x = rnd.uniform(-0.7, 0.7); y = rnd.uniform(-0.3, 0.3); g = shape(nome + 'Goccia%d' % k, 'sphere', (x, y, -0.5), (0.025, 0.025, 0.09), (0, 0, 0), O, M['acqua'], coll); G.append((g, x, y, rnd.random()))
    return dict(root=O, gocce=G)


def megafono(coll, M, nome='Megafono'):
    """megafono: origine all'impugnatura, la tromba guarda verso -Y."""
    O = empty(nome, (0, 0, 0), None, coll)
    shape(nome + 'Tromba', 'cone', (0, -0.62, 0.12), (0.3, 0.3, 0.62), (-PI / 2, 0, 0), O, M['bianco'], coll); cyl(nome + 'Bordo', 0.31, 0.05, (0, -0.62, 0.12), M['rosso'], coll, rot=(PI / 2, 0, 0), parent=O)
    cyl(nome + 'Corpo', 0.1, 0.3, (0, 0.1, 0.12), M['rosso'], coll, rot=(PI / 2, 0, 0), parent=O); box(nome + 'Manico', (-0.035, 0.0, -0.2), (0.035, 0.08, 0.05), M['nero'], coll, O)
    return O


def seggio(coll, M, fnt, nome='Seggio'):
    """il seggio galleggiante: zattera di tronchi, urna col buco, cartello. Origine sul pelo dell'acqua."""
    O = empty(nome, (0, 0, 0), None, coll)
    for k in range(4): _tronco(coll, M, nome + 'Tr%d' % k, (-1.1, -0.6 + k * 0.4, 0.02), (1.1, -0.6 + k * 0.4, 0.02), 0.2, O)
    props024.scatola_tonda(nome + 'Urna', 0.9, 0.7, 0.8, 0.05, M['bianco'], coll, O, (0, 0, 0.62)); box(nome + 'Fessura', (-0.25, -0.03, 1.02), (0.25, 0.03, 1.03), M['nero'], coll, O)
    props023.testo(coll, nome + 'UrnaT', 'VOTA', 0.26, M['inchiostro'], (0, -0.36, 0.62), parent=O, font=fnt, estrudi=0.004)
    props023.tubo(nome + 'Palo', (0.85, 0.3, 0.1), (0.85, 0.3, 2.6), 0.04, M['legno_scuro'], coll, parent=O)
    box(nome + 'Cartello', (0.1, 0.27, 2.0), (1.6, 0.31, 2.7), M['carta'], coll, O); props023.testo(coll, nome + 'CartelloT', 'SEGGIO', 0.3, M['nero'], (0.85, 0.26, 2.35), parent=O, font=fnt, estrudi=0.004)
    return O


def bandiera_palestina(coll, M, nome='Bandiera', asta=3.0, lung=1.3, alt=0.7):
    """Bandiera della Palestina su un'asta (richiesta dell'autore per la Castora: satira sui politici che la sventolano a ogni occasione).
    Tre fasce orizzontali nera, bianca e verde, triangolo rosso dalla parte dell'asta. Origine a terra, il telo sventola verso -X.
    La bandiera e' un oggetto di scena del personaggio: non va mai rovinata, rosicchiata o derisa. dict root, telo (perno in cima all'asta: rotation_euler.z = sventolio)."""
    import bmesh
    O = empty(nome, (0, 0, 0), None, coll)
    props023.tubo(nome + 'Asta', (0, 0, 0), (0, 0, asta + 0.06), 0.022, M['legno_scuro'], coll, parent=O); shape(nome + 'Pomo', 'sphere', (0, 0, asta + 0.09), (0.04, 0.04, 0.04), (0, 0, 0), O, M['oro'], coll)
    T_ = empty(nome + 'Telo', (0, 0, asta), O, coll); h = alt / 3
    verde = material('M30_bandiera_verde', (0.0, 0.42, 0.20), rough=0.7); rosso = material('M30_bandiera_rosso', (0.80, 0.04, 0.06), rough=0.7)
    for k, m in enumerate((M['nero'], M['bianco'], verde)): box(nome + 'Fascia%d' % k, (-lung, -0.005, -(k + 1) * h), (0, 0.005, -k * h), m, coll, T_)
    bm = bmesh.new(); a = lung * 0.36
    vs = [bm.verts.new(p) for p in ((0, -0.008, 0), (0, -0.008, -alt), (-a, -0.008, -alt / 2), (0, 0.008, 0), (0, 0.008, -alt), (-a, 0.008, -alt / 2))]
    for f in ((0, 1, 2), (5, 4, 3), (0, 2, 5, 3), (2, 1, 4, 5), (1, 0, 3, 4)): bm.faces.new([vs[i] for i in f])
    bm.normal_update(); me = bpy.data.meshes.new(nome + 'Triangolo'); bm.to_mesh(me); bm.free(); me.materials.append(rosso)
    o = bpy.data.objects.new(nome + 'Triangolo', me); coll.objects.link(o); o.parent = T_
    return dict(root=O, telo=T_)
