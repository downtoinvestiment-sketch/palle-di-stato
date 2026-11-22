"""L'Onorevole Cappellone: politico INVENTATO della serie (non e' il ritratto di nessuna persona vera). Testa enorme, capelli biondi a
spazzola (rossi fino al video 030), mento gigante, niente barba, sorriso da manifesto; cambia cappello a seconda di chi ha davanti.
    import cappellone as cp
    C = cp.cappellone(coll)                       # dizionario: root, body, head, shoulderL/R, hipL/R, browL/R, pupilL/R, lidL/R, mouth_*, cappelli
    cp.faccia(C, f, brow=0, brow_lift=0, smile=1, mouth_open=0, look=(0, 0), lid=0)     # f=None: solo la posa
    cp.emozione(C, f, 'comizio')                  # una delle 8 di EMOZIONI
    cp.gesto(C, f, 'promessa')                    # uno dei GESTI (braccia, testa, busto)
    cp.cappello(C, f, 'pompiere')                 # 'niente', 'pompiere', 'cuoco', 'muratore', 'alpino'
Fronte -Y, piedi a z=0, alto 2,15 (testa compresa). Le braccia pendono lungo -Z dai perni delle spalle, come quelle di Pippo."""
import math, bpy
from mathutils import Vector
from common import material, shape, empty
HC = 1.70                                                                    # centro della testa
def mats():
    m = lambda n, c, **k: material('CAP_' + n, c, **k)
    return dict(pelle=m('pelle', (0.95, 0.57, 0.39), rough=0.55), pelle_s=m('pelle_s', (0.86, 0.46, 0.31), rough=0.55), capelli=m('capelli', (1.0, 0.72, 0.18), rough=0.45),
                sopr=m('sopr', (0.62, 0.46, 0.18), rough=0.6), bianco=m('bianco', (0.97, 0.97, 0.97), rough=0.3), nero=m('nero', (0.02, 0.02, 0.02), rough=0.15),
                guancia=m('guancia', (1.0, 0.50, 0.48), rough=0.6), bocca=m('bocca', (0.42, 0.05, 0.07), rough=0.5), dentro=m('dentro', (0.16, 0.01, 0.03), rough=0.5),
                lingua=m('lingua', (0.95, 0.35, 0.40), rough=0.45), giacca=m('giacca', (0.10, 0.20, 0.55), rough=0.7), camicia=m('camicia', (0.95, 0.95, 0.97), rough=0.6),
                cravatta=m('cravatta', (0.85, 0.08, 0.08), rough=0.5), panta=m('panta', (0.08, 0.10, 0.22), rough=0.8), scarpe=m('scarpe', (0.25, 0.12, 0.05), rough=0.35),
                verde=m('verde', (0.05, 0.55, 0.20), rough=0.5), rosso=m('rosso', (0.85, 0.06, 0.06), rough=0.45), giallo=m('giallo', (1.0, 0.78, 0.05), rough=0.4),
                oro=m('oro', (1.0, 0.70, 0.16), rough=0.3, metallic=0.8), alpino=m('alpino', (0.25, 0.36, 0.22), rough=0.8))

# Cappellone e' molto alto: circa 195 cm con Pippo = 175 cm (decisione dell'autore, 22 novembre 2026) -> scala 1,18, alto 2,56 unita'.
SCALA = 1.18

def cappellone(coll, M=None, scala=SCALA):
    M = M or mats(); R = {'mats': M}; S = lambda n, k, loc, sc=(1, 1, 1), par=None, mat=None, rot=(0, 0, 0): shape('CAP_' + n, k, loc, sc, rot, par, mat, coll)
    E = lambda n, loc, par: empty('CAP_' + n, loc, par, coll)
    root = R['root'] = E('Root', (0, 0, 0), None); root.scale = (scala,) * 3; body = R['body'] = E('Body', (0, 0, 0.62), root)
    S('Busto', 'cap:0.27:0.30', (0, 0, 0.30), par=body, mat=M['giacca']); S('Pancia', 'sphere', (0, -0.06, 0.22), (0.29, 0.27, 0.26), body, M['giacca'])
    S('Camicia', 'sphere', (0, -0.215, 0.36), (0.10, 0.07, 0.24), body, M['camicia']); S('Cravatta', 'sphere', (0, -0.275, 0.32), (0.04, 0.025, 0.19), body, M['cravatta'])
    S('Nodo', 'sphere', (0, -0.262, 0.53), (0.05, 0.035, 0.04), body, M['cravatta']); S('Collo', 'cyl:0.10:0.14', (0, 0, 0.66), par=body, mat=M['pelle'])
    for i, (r, mt) in enumerate(((0.085, 'verde'), (0.058, 'bianco'), (0.030, 'rosso'))):          # coccarda tricolore sul petto
        S('Coccarda', 'sphere', (0.15, -0.262 - 0.006 * i, 0.44), (r, 0.012, r), body, M[mt])
    head = R['head'] = E('Head', (0, 0, HC - 0.62), body)
    S('Testa', 'sphere', (0, 0, 0), (0.44, 0.40, 0.42), head, M['pelle']); S('Mento', 'sphere', (0, -0.14, -0.33), (0.27, 0.23, 0.19), head, M['pelle'])
    S('Capelli', 'cyl:0.33:0.20', (0, 0.06, 0.37), par=head, mat=M['capelli']); S('CapelliLati', 'sphere', (0, 0.10, 0.22), (0.445, 0.36, 0.22), head, M['capelli'])
    S('Naso', 'sphere', (0, -0.44, -0.05), (0.075, 0.13, 0.07), head, M['pelle_s'])
    for s_, nm in ((-1, 'L'), (1, 'R')):
        S('Orecchio', 'sphere', (s_ * 0.44, 0.02, -0.02), (0.06, 0.05, 0.10), head, M['pelle']); S('Guancia', 'sphere', (s_ * 0.27, -0.29, -0.13), (0.075, 0.03, 0.05), head, M['guancia'])
        eye = E('Eye' + nm, (s_ * 0.16, -0.345, 0.10), head); S('Occhio', 'sphere', (0, 0, 0), (0.115, 0.06, 0.13), eye, M['bianco'])
        R['pupil' + nm] = S('Pupilla', 'sphere', (0, -0.05, 0), (0.05, 0.022, 0.06), eye, M['nero']); S('Luce', 'sphere_lo', (0.02, -0.07, 0.03), (0.015, 0.008, 0.017), eye, M['bianco'])
        R['lid' + nm] = S('Palpebra', 'sphere', (0, -0.012, 0.135), (0.125, 0.07, 0.001), eye, M['pelle'])
        b = R['brow' + nm] = E('Brow' + nm, (s_ * 0.16, -0.37, 0.30), head); S('Sopracciglio', 'sphere', (0, 0, 0), (0.14, 0.045, 0.05), b, M['sopr'])
    cu = bpy.data.curves.new('CAP_BoccaCurva', 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = 0.02; cu.bevel_resolution = 4; cu.use_fill_caps = True
    sp = cu.splines.new('BEZIER'); sp.bezier_points.add(2); base = [(-0.16, -0.345, -0.24), (0, -0.385, -0.26), (0.16, -0.345, -0.24)]
    for bp, co in zip(sp.bezier_points, base): bp.co = co; bp.handle_left_type = bp.handle_right_type = 'AUTO'
    mo = bpy.data.objects.new('CAP_Bocca', cu); mo.parent = head; coll.objects.link(mo); mo.data.materials.append(M['bocca']); R['mouth_curve'] = cu; R['mouth_base'] = base; R['mouth_obj'] = mo
    ap = R['mouth_open'] = E('BoccaAperta', (0, -0.36, -0.26), head)
    S('Labbra', 'sphere', (0, 0.008, 0.0), (0.172, 0.034, 0.122), ap, M['bocca'])        # bordo rosso attorno alla bocca aperta (la curva sparisce quando parla)
    S('BoccaDentro', 'sphere', (0, 0, 0), (0.15, 0.04, 0.10), ap, M['dentro']); S('Lingua', 'sphere', (0, -0.012, -0.05), (0.09, 0.03, 0.04), ap, M['lingua']); S('Denti', 'sphere', (0, -0.014, 0.062), (0.125, 0.032, 0.03), ap, M['bianco'])
    ap.scale = (0.001,) * 3
    for s_, nm in ((-1, 'L'), (1, 'R')):
        sh = R['shoulder' + nm] = E('Shoulder' + nm, (s_ * 0.34, 0, 0.56), body)
        S('Manica', 'cap:0.085:0.40', (0, 0, -0.24), par=sh, mat=M['giacca']); S('Polsino', 'cyl:0.075:0.04', (0, 0, -0.50), par=sh, mat=M['camicia']); S('Mano', 'sphere', (0, 0, -0.60), (0.105, 0.10, 0.11), sh, M['pelle'])
        hp = R['hip' + nm] = E('Hip' + nm, (s_ * 0.13, 0, 0.62), root)
        S('Gamba', 'cap:0.105:0.36', (0, 0, -0.27), par=hp, mat=M['panta']); S('Scarpa', 'sphere', (0, -0.07, -0.555), (0.11, 0.20, 0.07), hp, M['scarpe'])
    # cappelli: uno alla volta, figli della testa
    K = R['cappelli'] = {}
    def gruppo(n): g = E('Cappello_' + n, (0, 0, 0), head); g.scale = (0.001,) * 3; K[n] = g; return g
    g = gruppo('pompiere'); S('Elmo', 'sphere', (0, 0.02, 0.33), (0.40, 0.40, 0.26), g, M['rosso']); S('Tesa', 'sphere', (0, 0.10, 0.27), (0.46, 0.50, 0.035), g, M['rosso']); S('Cresta', 'sphere', (0, 0.02, 0.58), (0.05, 0.30, 0.06), g, M['oro']); S('Stemma', 'sphere', (0, -0.385, 0.40), (0.08, 0.02, 0.09), g, M['oro'])
    g = gruppo('cuoco'); S('Fascia', 'cyl:0.34:0.20', (0, 0.02, 0.46), par=g, mat=M['bianco']); S('Sbuffo', 'sphere', (0, 0.02, 0.74), (0.44, 0.44, 0.24), g, M['bianco'])
    g = gruppo('muratore'); S('Casco', 'sphere', (0, 0.02, 0.34), (0.41, 0.41, 0.27), g, M['giallo']); S('Visiera', 'sphere', (0, -0.30, 0.31), (0.30, 0.22, 0.03), g, M['giallo']); S('Costola', 'sphere', (0, 0.02, 0.60), (0.06, 0.34, 0.04), g, M['giallo'])
    g = gruppo('alpino'); S('Cupola', 'cone', (0, 0.02, 0.34), (0.36, 0.36, 0.40), g, M['alpino']); S('Falda', 'sphere', (0, 0.02, 0.36), (0.50, 0.50, 0.035), g, M['alpino']); S('Penna', 'sphere', (-0.30, 0.02, 0.66), (0.025, 0.05, 0.34), g, M['nero'], rot=(0, -0.25, 0)); S('Nappina', 'sphere', (-0.30, 0.02, 0.42), (0.05, 0.05, 0.05), g, M['rosso'])
    return R

def _k(o, prop, f):
    if f is not None: o.keyframe_insert(prop, frame=f)
def faccia(R, f, brow=0.0, brow_lift=0.0, smile=1.0, mouth_open=0.0, look=(0.0, 0.0), lid=0.0):
    """brow > 0 arrabbiato, < 0 preoccupato; brow_lift alza; smile -1..2; mouth_open 0..1,5; look (x, z); lid 0 aperto .. 1 chiuso."""
    for s_, nm in ((-1, 'L'), (1, 'R')):
        b = R['brow' + nm]; b.rotation_euler = (0, s_ * brow * 0.6, 0); b.location = (s_ * 0.16, -0.385, 0.27 + 0.09 * brow_lift - 0.03 * max(0, brow)); _k(b, 'rotation_euler', f); _k(b, 'location', f)
        p = R['pupil' + nm]; p.location = (look[0] * 0.05, -0.05, look[1] * 0.055); _k(p, 'location', f)
        l = R['lid' + nm]; l.scale = (0.125, 0.07, 0.001 + 0.14 * lid); l.location = (0, -0.012, 0.135 - 0.13 * lid); _k(l, 'scale', f); _k(l, 'location', f)
    cu = R['mouth_curve']
    for i, bp in enumerate(cu.splines[0].bezier_points):
        x, y, z = R['mouth_base'][i]; z = (z - 0.05 * smile) if i == 1 else (z + 0.055 * smile)
        bp.co = (x * (1 + 0.28 * max(0, smile)), y, z); bp.handle_left_type = bp.handle_right_type = 'AUTO'
        if f is not None: bp.keyframe_insert('co', frame=f)
    ap = R['mouth_open']; mo = R.get('mouth_obj')
    if mouth_open <= 0.02:
        ap.scale = (0.001,) * 3
        if mo: mo.scale = (1, 1, 1)
    else:                                                    # bocca aperta (21 nov 2026, v2): la curva del sorriso sparisce e resta la bocca a D col bordo rosso,
        sz = 0.3 + 0.9 * mouth_open                          # cosi' la riga non taglia piu' la bocca a V; il sorriso la allarga e ne alza gli angoli
        ap.location = (0, -0.355, -0.27 - 0.012 * smile); ap.scale = (0.62 + 0.3 * mouth_open + 0.08 * max(0.0, smile), 1.0, sz * (1.0 - 0.08 * max(0.0, smile)))
        if mo: mo.scale = (0.001,) * 3
    _k(ap, 'scale', f); _k(ap, 'location', f)
    if mo: _k(mo, 'scale', f)

EMOZIONI = {                                                                 # le 8 della scheda
    'manifesto': dict(smile=2.0, brow_lift=0.5), 'comizio': dict(smile=0.6, mouth_open=1.4, brow=0.9, brow_lift=0.3), 'promessa': dict(smile=1.6, mouth_open=0.5, brow_lift=1.0, lid=0.25),
    'indignato': dict(smile=-1.5, mouth_open=0.9, brow=1.6), 'colto in fallo': dict(smile=-0.4, mouth_open=1.2, brow=-1.2, brow_lift=1.1, look=(0.9, 0.0)),
    'furbo': dict(smile=1.3, brow=0.5, lid=0.45, look=(-1.0, 0.0)), 'piagnisteo': dict(smile=-2.0, mouth_open=0.4, brow=-1.6, brow_lift=0.4, look=(0, -0.7)), 'selfie': dict(smile=2.0, mouth_open=1.0, brow_lift=1.0, lid=0.9),
}
def emozione(R, f, nome): faccia(R, f, **EMOZIONI[nome])

GESTI = {                                                                    # braccio sinistro, braccio destro (direzioni), testa (rot x, y, z), busto (rot x, y)
    'riposo': ((-0.12, 0, -1), (0.12, 0, -1), (0, 0, 0), (0, 0)), 'promessa': ((-0.1, -0.2, -1), (0.25, -0.75, 0.45), (-0.1, 0, 0), (-0.05, 0)), 'comizio': ((-0.75, -0.2, 0.75), (0.75, -0.2, 0.75), (-0.2, 0, 0), (-0.1, 0)),
    'dito puntato': ((-0.15, 0, -1), (0.2, -1.0, 0.12), (0.05, 0, 0.1), (0.14, 0)), 'mani sul cuore': ((0.55, -0.7, -0.15), (-0.55, -0.7, -0.15), (0.12, 0, 0.1), (0.06, 0)), 'stretta di mano': ((-0.12, 0, -1), (0.1, -1.0, -0.35), (0, 0, 0), (0.12, 0)),
    'non sono stato io': ((-0.9, -0.35, -0.1), (0.9, -0.35, -0.1), (0, 0, -0.2), (-0.08, 0)), 'saluto alla folla': ((-0.12, 0, -1), (0.55, -0.1, 1.0), (-0.1, 0, 0.12), (0, 0.06)), 'pugno sul tavolo': ((-0.2, -0.5, -0.8), (0.15, -0.6, 0.75), (0.15, 0, 0), (0.18, 0)),
}
def gesto(R, f, nome):
    l, r, t, b = GESTI[nome]
    for nm, d in (('L', l), ('R', r)):
        sh = R['shoulder' + nm]; sh.rotation_mode = 'QUATERNION'; sh.rotation_quaternion = Vector((0, 0, -1)).rotation_difference(Vector(d).normalized()); _k(sh, 'rotation_quaternion', f)
    R['head'].rotation_euler = t; _k(R['head'], 'rotation_euler', f); R['body'].rotation_euler = (b[0], b[1], 0); _k(R['body'], 'rotation_euler', f)

def cappello(R, f, tipo='niente'):
    for n, g in R['cappelli'].items():
        g.scale = (1, 1, 1) if n == tipo else (0.001,) * 3; _k(g, 'scale', f)


def luce_calda(scena, luci_cinema=None, esposizione=-0.35, temperatura=8000):
    """Look approvato dall'autore il 21 nov 2026 per Cappellone: luce un po' piu' bassa e piu' calda.
    luci_cinema = il dizionario restituito da luci.cinema (chiave abbassata all'82% e scaldata)."""
    if luci_cinema:
        k = luci_cinema['chiave'].data; k.energy *= 0.82; k.color = (1.0, 0.78, 0.55)
    scena.view_settings.exposure = esposizione
    try: scena.view_settings.use_white_balance = True; scena.view_settings.white_balance_temperature = temperatura
    except Exception: pass
