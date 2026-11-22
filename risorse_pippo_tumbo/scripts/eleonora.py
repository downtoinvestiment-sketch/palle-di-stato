"""Eleonora con le emozioni (17 novembre 2026). props012.py NON viene toccato: qui si costruisce la zucchina di sempre
e le si aggiungono due sopracciglia sottili, una bocca che sorride o si apre, e un perno per piegare il corpo.
Regola dell'autore (come per Pippo): gli occhi non cambiano mai misura.

    import props012, eleonora
    Z12 = props012.mats012()
    Z = eleonora.zucchina(chc, Z12)               # stesso dizionario di props012.zucchina (eyes, mouth, legs, veil...)
    eleonora.express(Z, frame, brow=0.8, smile=-1, mouth_open=0.3, look=(0, 0), piega=(0, 0), schiaccia=0)
    eleonora.emozione(Z, frame, 'felice')         # una delle EMOZIONI pronte

brow > 0 arrabbiata, < 0 triste/spaventata; brow_lift alza le sopracciglia; smile -1..1; mouth_open 0..1;
look (x, z) sguardo; piega (avanti, di lato) in radianti, il corpo si piega dalla base; schiaccia > 0 si accascia, < 0 si allunga.
Z['mouth'] ora e' un gruppo (bocca nuova), quindi show()/pop() sugli episodi vecchi funzionano uguale."""
import math, bpy
from common import material, shape, empty
import props012, set004
from set004 import obj

EMOZIONI = {
    'normale':    dict(smile=0.3),
    'felice':     dict(smile=1.0, brow_lift=0.4, schiaccia=-0.05),
    'ride':       dict(smile=1.0, mouth_open=0.9, brow_lift=0.6, piega=(-0.12, 0.10)),
    'arrabbiata': dict(brow=1.0, smile=-0.7, mouth_open=0.25, piega=(0.10, 0)),
    'triste':     dict(brow=-1.0, smile=-1.0, look=(0, -0.8), piega=(0.18, 0), schiaccia=0.10),
    'spaventata': dict(brow=-1.0, brow_lift=0.7, mouth_open=0.8, smile=-0.3, piega=(-0.15, 0), look=(0.7, 0)),
    'sorpresa':   dict(brow_lift=1.0, mouth_open=0.6, schiaccia=-0.10),
    'furba':      dict(brow=0.7, smile=0.7, look=(1, 0), piega=(0, 0.15)),
}


def zucchina(coll, M):
    Z = props012.zucchina(coll, M)
    ZR, ZL = props012.ZR, props012.ZL
    r = Z['root']
    corpo = Z['corpo'] = empty('ZucPerno', (0, 0, 0), r, coll)          # tutto passa da qui: piega e schiaccia
    for o in list(r.children):
        if o is not corpo:
            o.parent = corpo
    f = -ZR; ez = ZL * 0.70
    pup = [o for o in Z['eyes'].children if o.name.startswith('ZucPupilla')]
    pup.sort(key=lambda o: o.location.x)
    Z['pupille'] = [(o, tuple(o.location)) for o in pup]
    nero = M['black']
    for s, nm in ((-1, 'L'), (1, 'R')):
        b = Z['brow' + nm] = empty('ZucSopracciglio' + nm, (s * 0.057, f + 0.004, ez + 0.135), Z['eyes'], coll)
        obj('ZucSopraccMesh', set004.box_c(), (0, 0, 0), (0.058, 0.012, 0.013), nero, coll, parent=b)
    # bocca nuova: una curva con il rossetto e l'interno scuro che si apre
    vecchia = Z['mouth']; vecchia.hide_render = vecchia.hide_viewport = True; vecchia.scale = (0.001,) * 3
    bocca = empty('ZucBoccaNuova', (0, f - 0.003, ZL * 0.56), corpo, coll)
    cu = bpy.data.curves.new('ZucBoccaCurva', 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = 0.009; cu.bevel_resolution = 4; cu.use_fill_caps = True
    sp = cu.splines.new('BEZIER'); sp.bezier_points.add(2)
    base = [(-0.045, 0.006, 0.0), (0.0, -0.004, -0.006), (0.045, 0.006, 0.0)]
    for bp, co in zip(sp.bezier_points, base):
        bp.co = co; bp.handle_left_type = bp.handle_right_type = 'AUTO'
    mo = bpy.data.objects.new('ZucBoccaLinea', cu); mo.parent = bocca; coll.objects.link(mo); cu.materials.append(M['lip'])
    aperta = empty('ZucBoccaAperta', (0, 0.0, -0.012), bocca, coll)
    shape('ZucBoccaLabbra', 'sphere', (0, 0.004, 0), (0.044, 0.012, 0.036), (0, 0, 0), aperta, M['lip'], coll)   # bordo col rossetto
    shape('ZucBoccaDentro', 'sphere', (0, 0, 0), (0.036, 0.012, 0.028), (0, 0, 0), aperta, material('Z12_dentro', (0.30, 0.03, 0.06), rough=0.7), coll)
    shape('ZucLingua', 'sphere', (0, -0.004, -0.014), (0.022, 0.008, 0.010), (0, 0, 0), aperta, material('Z12_lingua', (0.95, 0.35, 0.42), rough=0.6), coll)
    aperta.scale = (0.001,) * 3
    Z['mouth'] = bocca; Z['mouth_line'] = mo; Z['mouth_curve'] = cu; Z['mouth_base'] = base; Z['mouth_open'] = aperta
    express(Z, None, **EMOZIONI['normale'])
    return Z


def velo(Z, acceso):
    """Mostra o nasconde il velo da sposa (anche i pezzi figli)."""
    for o in [Z['veil']] + list(Z['veil'].children_recursive):
        o.hide_render = o.hide_viewport = not acceso


def express(Z, f, brow=0.0, brow_lift=0.0, smile=0.0, mouth_open=0.0, look=(0.0, 0.0), piega=(0.0, 0.0), schiaccia=0.0):
    """Chiavi al fotogramma f (f=None: solo la posa). Gli occhi non cambiano misura."""
    def k(o, prop):
        if f is not None:
            o.keyframe_insert(prop, frame=f)
    for o, (x, y, z) in Z['pupille']:
        o.location = (x + look[0] * 0.016, y, z + look[1] * 0.02); k(o, 'location')
    for s, nm in ((-1, 'L'), (1, 'R')):
        b = Z['brow' + nm]
        b.rotation_euler = (0, -s * brow * 0.55, 0)        # brow > 0: punte interne in giu' (arrabbiata)
        b.location.z = props012.ZL * 0.70 + 0.135 + 0.03 * brow_lift + (0.008 if brow < 0 else -0.008 * brow)
        k(b, 'rotation_euler'); k(b, 'location')
    for i, bp in enumerate(Z['mouth_curve'].splines[0].bezier_points):
        x, y, z = Z['mouth_base'][i]
        z = z - 0.014 * smile if i == 1 else z + 0.016 * smile
        bp.co = (x * (1 + 0.25 * max(0.0, smile)), y, z); bp.handle_left_type = bp.handle_right_type = 'AUTO'
        if f is not None:
            bp.keyframe_insert('co', frame=f)
    ln = Z['mouth_line']; ln.scale = (1, 1, 1) if mouth_open <= 0.01 else (0.001,) * 3; k(ln, 'scale')   # bocca aperta: sparisce la riga
    a = Z['mouth_open']; a.scale = (0.001,) * 3 if mouth_open <= 0.01 else (0.7 + 0.5 * mouth_open, 1.0, 0.35 + 1.0 * mouth_open); k(a, 'scale')
    c = Z['corpo']; c.rotation_euler = (piega[0], piega[1], 0); c.scale = (1 + 0.5 * schiaccia, 1 + 0.5 * schiaccia, 1 - schiaccia)
    k(c, 'rotation_euler'); k(c, 'scale')


def emozione(Z, f, nome):
    express(Z, f, **EMOZIONI[nome])
