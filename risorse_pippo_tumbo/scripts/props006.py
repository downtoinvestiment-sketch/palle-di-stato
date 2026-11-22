"""Test 006 - oggetti: carrello della spesa e i pezzi che lo trasformano in macchina da corsa, caschi, cassonetto, vecchietta col deambulatore."""
import bpy, math, numpy as np
from common import *
import set004, props004
from set004 import MB, obj

S = 1.25          # scala del carrello (a misura di Pippo)
BW, BL = 0.62 * S, 1.05 * S       # larghezza / lunghezza cesto
Z0, Z1 = 0.42 * S, 0.86 * S       # fondo / bordo cesto
FLOOR = Z0 + 0.03


def mats006():
    M = {}
    M['chrome'] = material('K_chrome', (0.82, 0.85, 0.9), rough=0.22, metallic=0.9)
    M['handle'] = material('K_handle', (0.95, 0.12, 0.10), rough=0.4, spec=0.5)
    M['rubber'] = material('K_rubber', (0.05, 0.05, 0.06), rough=0.8)
    M['hub'] = material('K_hub', (0.85, 0.87, 0.9), rough=0.3, metallic=0.8)
    M['pad'] = material('K_pad', (0.95, 0.10, 0.10), rough=0.6)
    M['racered'] = material('K_racered', (0.92, 0.06, 0.06), rough=0.25, spec=0.8)
    M['racewh'] = material('K_racewh', (0.98, 0.98, 0.98), rough=0.25, spec=0.8)
    M['racey'] = material('K_racey', (1.0, 0.80, 0.05), rough=0.3, spec=0.7)
    M['engine'] = material('K_engine', (0.10, 0.55, 0.20), rough=0.4, spec=0.5)
    M['steel'] = material('K_steel', (0.45, 0.47, 0.52), rough=0.35, metallic=0.8)
    M['dark'] = material('K_dark', (0.06, 0.06, 0.08), rough=0.6)
    M['seat'] = material('K_seat', (0.12, 0.12, 0.16), rough=0.7)
    M['belt'] = material('K_belt', (0.10, 0.30, 0.95), rough=0.6)
    M['helm'] = material('K_helm', (0.95, 0.10, 0.10), rough=0.2, spec=0.9)
    M['helm2'] = material('K_helm2', (1.0, 0.80, 0.05), rough=0.2, spec=0.9)
    M['visor'] = material('K_visor', (0.5, 0.85, 1.0), rough=0.05, spec=1.0)
    try:
        M['visor'].surface_render_method = 'BLENDED'; M['visor'].node_tree.nodes['Principled BSDF'].inputs['Alpha'].default_value = 0.35
    except Exception: pass
    M['bin'] = material('K_bin', (0.10, 0.50, 0.22), rough=0.6)
    M['binlid'] = material('K_binlid', (0.95, 0.75, 0.05), rough=0.6)
    M['trash'] = material('K_trash', (0.15, 0.15, 0.18), rough=0.5, spec=0.4)
    M['smoke'] = material('K_smoke', (0.75, 0.75, 0.78), rough=1.0, emit=(0.7, 0.7, 0.72), emit_strength=0.25)
    M['flame'] = material('K_flame', (1.0, 0.55, 0.05), rough=1.0, emit=(1.0, 0.45, 0.02), emit_strength=3.0)
    return M


def _wheel(coll, M, parent, loc, r, w, tyre='rubber'):
    e = empty('Ruota', loc, parent, coll)
    shape('Gomma', 'cyl:%.3f:%.3f' % (r, w), (0, 0, 0), (1, 1, 1), (0, math.pi / 2, 0), e, M[tyre], coll)
    shape('Cerchio', 'cyl:%.3f:%.3f' % (r * 0.55, w * 1.15), (0, 0, 0), (1, 1, 1), (0, math.pi / 2, 0), e, M['hub'], coll)
    return e


def cart(coll, M):
    """carrello della spesa: muso verso -Y, origine a terra al centro. Restituisce dict(root, wheels=[...], casters=[...])."""
    root = empty('Carrello', (0, 0, 0), None, coll)
    mb = MB([M['chrome'], M['handle'], M['rubber']])
    hw, hl = BW / 2, BL / 2; t = 0.018
    # cesto a rete: il davanti è più stretto e più basso (come i carrelli veri)
    def X(y): return hw * (0.84 + 0.16 * (y + hl) / BL)          # semilarghezza lungo Y
    for z in np.linspace(Z0, Z1, 5):                              # correnti orizzontali
        for s in (-1, 1):
            a = (s * X(-hl), -hl, z); b = (s * X(hl), hl, z)
            mb.box(((a[0] + b[0]) / 2, 0, z), (t, BL, t), 0, rz=-s * math.atan2(X(hl) - X(-hl), BL))
        mb.box((0, -hl, z), (2 * X(-hl), t, t), 0); mb.box((0, hl, z), (2 * X(hl), t, t), 0)
    for y in np.linspace(-hl, hl, 12):                            # montanti dei fianchi
        for s in (-1, 1): mb.box((s * X(y), y, (Z0 + Z1) / 2), (t * 0.8, t * 0.8, Z1 - Z0), 0)
    for x in np.linspace(-1, 1, 8):                               # montanti davanti e dietro
        mb.box((x * X(-hl), -hl, (Z0 + Z1) / 2), (t * 0.8, t * 0.8, Z1 - Z0), 0); mb.box((x * X(hl), hl, (Z0 + Z1) / 2), (t * 0.8, t * 0.8, Z1 - Z0), 0)
    for y in np.linspace(-hl, hl, 10): mb.box((0, y, Z0), (2 * X(y), t, t), 0)      # fondo
    for x in np.linspace(-0.8, 0.8, 5): mb.box((x * hw * 0.9, 0, Z0), (t, BL, t), 0)
    # telaio
    for s in (-1, 1):
        mb.box((s * hw * 0.92, 0.05, 0.16 * S), (0.035, BL * 0.95, 0.035), 0)                       # longheroni bassi
        mb.box((s * hw * 0.98, hl - 0.02, 0.62 * S), (0.035, 0.035, 0.95 * S), 0, rx=0.10)             # montanti posteriori
        mb.box((s * hw * 0.98, hl + 0.10, 1.06 * S), (0.035, 0.22, 0.035), 0)                         # bracci del maniglione
        mb.box((s * hw * 0.85, -hl + 0.10, 0.29 * S), (0.03, 0.03, 0.28 * S), 0)                      # puntoni davanti
    mb.box((0, 0.05, 0.16 * S), (BW * 0.9, 0.035, 0.035), 0); mb.box((0, -hl + 0.12, 0.16 * S), (BW * 0.8, 0.035, 0.035), 0)
    mb.box((0, hl + 0.20, 1.06 * S), (BW * 1.02, 0.05, 0.05), 1)                                       # maniglione rosso
    o = mb.build('CarrelloRete', coll); o.parent = root
    R = dict(root=root, casters=[], wheels=[])
    for (sx, sy) in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        c = _wheel(coll, M, root, (sx * hw * 0.88, sy * hl * 0.82, 0.075 * S), 0.075 * S, 0.035)
        obj('Forcella', set004.box_c(), (0, 0, 0.07 * S), (0.05, 0.03, 0.10 * S), M['chrome'], coll, parent=c)
        R['casters'].append(c)
    return R


def brakes(coll, M, root):
    """freni: (leve sul maniglione con i cavi, pattini rossi sulle ruote dietro) come due oggetti."""
    hw, hl = BW / 2, BL / 2; ml = MB([M['steel'], M['pad'], M['dark'], M['racey']]); mp = MB([M['steel'], M['pad'], M['dark']])
    for s in (-1, 1):
        ml.box((s * hw * 0.62, hl + 0.16, 1.00 * S), (0.06, 0.32, 0.05), 3, rx=0.25)        # leva
        ml.box((s * hw * 0.62, hl + 0.05, 1.03 * S), (0.06, 0.06, 0.07), 1)                  # perno
        ml.box((s * hw * 1.02, hl + 0.01, 0.56 * S), (0.014, 0.014, 0.86 * S), 2, rx=0.10)   # cavo
        mp.box((s * hw * 0.88, hl * 0.82 + 0.11 * S, 0.11 * S), (0.11, 0.06, 0.13), 1)       # pattino
        mp.box((s * hw * 0.88, hl * 0.82 + 0.16 * S, 0.16 * S), (0.04, 0.10, 0.04), 0)
    lev = ml.build('FreniLeve', coll); lev.parent = root; pad = mp.build('FreniPattini', coll); pad.parent = root
    return lev, pad


def steering(coll, M, root):
    """sterzo: volante, piantone e assale anteriore con ruote grosse. Restituisce (gruppo, volante, [ruote])."""
    hw, hl = BW / 2, BL / 2
    g = empty('Sterzo', (0, 0, 0), root, coll)
    mb = MB([M['steel'], M['dark']])
    mb.box((0, -hl - 0.05, 0.17 * S), (BW * 1.35, 0.06, 0.06), 0)                             # assale davanti
    mb.box((0, -0.34, 0.955), (0.05, 0.05, 1.66), 0, rx=-0.456)                               # piantone
    o = mb.build('SterzoTelaio', coll); o.parent = g
    wheel = empty('Volante', (0, 0.025, 1.70), g, coll); wheel.rotation_mode = 'ZXY'; wheel.rotation_euler = (-0.456, 0, 0)
    shape('VolanteCorona', 'cyl:0.19:0.035', (0, 0, 0), (1, 1, 1), (0, 0, 0), wheel, M['dark'], coll)
    shape('VolanteMozzo', 'cyl:0.06:0.06', (0, 0, 0), (1, 1, 1), (0, 0, 0), wheel, M['racered'], coll)
    obj('VolanteRazza', set004.box_c(), (0, 0, 0.01), (0.36, 0.04, 0.02), M['steel'], coll, parent=wheel)
    ws = [_wheel(coll, M, g, (s * BW * 0.70, -hl - 0.05, 0.17 * S), 0.17 * S, 0.10) for s in (-1, 1)]
    return g, o, wheel, ws


def engine(coll, M, root):
    """motore del tosaerba dietro, catena, marmitta, assale e ruote posteriori grosse. Restituisce (gruppo, [ruote], marmitta)."""
    hw, hl = BW / 2, BL / 2
    g = empty('Motore', (0, 0, 0), root, coll)
    mb = MB([M['engine'], M['steel'], M['dark'], M['racered'], M['racey']])
    y0 = hl + 0.02; z0 = 0.34 * S
    mb.box((0, y0 + 0.10, z0), (0.40, 0.34, 0.26), 0)                    # blocco
    mb.box((0, y0 + 0.10, z0 + 0.19), (0.30, 0.26, 0.12), 3)             # coperchio rosso
    mb.box((0.10, y0 + 0.10, z0 + 0.30), (0.10, 0.10, 0.10), 4)          # tappo
    for k in range(4): mb.box((-0.23, y0 + 0.10, z0 - 0.09 + k * 0.06), (0.07, 0.30, 0.02), 1)   # alette
    mb.box((0.26, y0 + 0.22, z0 + 0.02), (0.12, 0.08, 0.08), 1)          # collettore
    mb.box((0, hl * 0.82, 0.20 * S), (BW * 1.45, 0.06, 0.06), 1)         # assale dietro
    mb.box((0, y0 + 0.10, z0 - 0.17), (0.50, 0.42, 0.04), 1)             # piastra
    o = mb.build('MotoreBlocco', coll); o.parent = g
    ex = shape('Marmitta', 'cyl:0.045:0.5', (0.33, y0 + 0.42, z0 + 0.02), (1, 1, 1), (math.pi / 2 - 0.25, 0, 0), g, M['steel'], coll)
    ws = [_wheel(coll, M, g, (s * BW * 0.78, hl * 0.82, 0.20 * S), 0.20 * S, 0.14) for s in (-1, 1)]
    chain = obj('Catena', set004.box_c(), (-0.30, y0 - 0.03, 0.30 * S), (0.035, 0.40, 0.06), M['dark'], coll, rot=(0.50, 0, 0), parent=root)
    spr = shape('Pignone', 'cyl:0.12:0.03', (-0.30, hl * 0.82, 0.20 * S), (1, 1, 1), (0, math.pi / 2, 0), root, M['racey'], coll)
    thr = obj('Acceleratore', set004.box_c(), (0.24, 0.06, 1.74), (0.05, 0.05, 0.20), M['racey'], coll, rot=(-0.456, 0, 0), parent=root)
    return dict(g=g, wheels=ws, ex=ex, chain=chain, spr=spr, thr=thr)


def racekit(coll, M, root):
    """allestimento corsa: roll-bar, fiancate rosse, muso, alettone, numero 1, cinture."""
    hw, hl = BW / 2, BL / 2
    mb = MB([M['racered'], M['racewh'], M['racey'], M['dark'], M['belt'], M['steel']])
    for s in (-1, 1):
        mb.box((s * (hw + 0.012), 0.02, (Z0 + Z1) / 2), (0.02, BL * 0.98, (Z1 - Z0) * 0.92), 0, rz=-s * 0.045)   # fiancate
        mb.box((s * (hw + 0.026), 0.10, (Z0 + Z1) / 2), (0.01, 0.34, 0.30), 1)                               # tabella porta numero
        mb.box((s * (hw + 0.034), 0.10, (Z0 + Z1) / 2), (0.01, 0.06, 0.22), 3)                               # "1"
        mb.box((s * (hw + 0.026), -0.30, (Z0 + Z1) / 2 + 0.02), (0.01, 0.36, 0.07), 2)                        # striscia gialla
        mb.box((s * hw * 0.80, hl - 0.06, 1.40 * S), (0.055, 0.055, 0.95 * S), 2, rx=0.0)                      # roll-bar: montanti
        mb.box((s * hw * 0.62, hl + 0.30, 1.22 * S), (0.05, 0.05, 0.30), 5)                                  # supporti alettone
    mb.box((0, hl - 0.06, 1.87 * S), (BW * 0.86, 0.055, 0.055), 2)                                            # roll-bar: traversa
    mb.box((0, -hl - 0.02, (Z0 + Z1) / 2 - 0.02), (BW * 0.86, 0.03, (Z1 - Z0) * 0.9), 0)                      # frontale
    mb.box((0, -hl - 0.16, Z0 + 0.06), (BW * 0.80, 0.30, 0.10), 0, rx=0.25)                                    # muso
    mb.box((0, -hl - 0.30, Z0 - 0.03), (BW * 1.25, 0.14, 0.03), 1)                                             # spoiler davanti
    mb.box((0, hl + 0.34, 1.36 * S), (BW * 1.45, 0.30, 0.035), 0, rx=-0.16)                                    # alettone
    for s in (-1, 1): mb.box((s * BW * 0.72, hl + 0.34, 1.36 * S), (0.02, 0.34, 0.16), 1)
    mb.box((0, 0.46, FLOOR + 0.42), (0.46, 0.08, 0.84), 3)                                                    # schienale
    o = mb.build('KitCorsa', coll); o.parent = root
    bm = MB([M['belt'], M['hub']])
    for s in (-1, 1): bm.box((s * 0.13, 0.20, 1.62), (0.06, 0.03, 0.60), 0, rx=0.05)
    bm.box((0, 0.185, 1.42), (0.34, 0.03, 0.06), 0); bm.box((0, 0.17, 1.42), (0.09, 0.03, 0.09), 1)
    belts = bm.build('Cinture', coll); belts.parent = root
    return o, belts


def helmet(coll, M, head, cz, r=0.50, mat='helm', stripe='racewh', front_cut=0.20, scale=(1.0, 1.06, 0.96)):
    """casco aperto (calotta): copre capelli e nuca, lascia libero il viso (verso -Y). Figlio della testa, centrato in (0,0.03,cz)."""
    nu, nv = 24, 14; V = []; F = []; MI = []
    def keep(x, y, z): return z > (front_cut if y < -0.12 * r else -0.62 * r) - (0.25 * r if abs(x) > 0.75 * r and y < 0 else 0)
    idx = {}
    for i in range(nv + 1):
        th = math.pi * i / nv
        for k in range(nu):
            ph = 2 * math.pi * k / nu; x = r * math.sin(th) * math.cos(ph); y = r * math.sin(th) * math.sin(ph); z = r * math.cos(th)
            idx[(i, k)] = len(V); V.append((x * scale[0], y * scale[1], z * scale[2]))
    for i in range(nv):
        for k in range(nu):
            q = [(i, k), (i + 1, k), (i + 1, (k + 1) % nu), (i, (k + 1) % nu)]
            c = np.mean([V[idx[a]] for a in q], axis=0)
            if not keep(c[0] / scale[0], c[1] / scale[1], c[2] / scale[2]): continue
            F.append(tuple(idx[a] for a in q)); MI.append(1 if abs(c[0]) < 0.10 * r else 0)
    me = bpy.data.meshes.new('Casco'); me.from_pydata(V, [], F); me.materials.append(M[mat]); me.materials.append(M[stripe])
    me.polygons.foreach_set('material_index', MI); me.polygons.foreach_set('use_smooth', [True] * len(F)); me.update()
    o = bpy.data.objects.new('Casco', me); o.parent = head; o.location = (0, 0.03, cz); coll.objects.link(o)
    sol = o.modifiers.new('Spessore', 'SOLIDIFY'); sol.thickness = 0.035; sol.offset = 1.0
    return o


def dumpster(coll, M):
    """cassonetto verde con coperchio giallo aperto e sacchi neri."""
    root = empty('Cassonetto', (0, 0, 0), None, coll)
    mb = MB([M['bin'], M['binlid'], M['dark'], M['steel']])
    mb.box((0, 0, 0.72), (1.9, 1.15, 1.1), 0); mb.box((0, 0, 1.29), (2.0, 1.25, 0.06), 0)
    for s in (-1, 1):
        mb.box((s * 0.75, 0, 0.09), (0.12, 0.12, 0.18), 2); mb.box((s * 1.0, -0.2, 0.9), (0.06, 0.5, 0.08), 3)
    for k in range(3): mb.box((-0.6 + 0.6 * k, -0.585, 0.72), (0.06, 0.02, 0.9), 0)
    o = mb.build('CassonettoCorpo', coll); o.parent = root
    lid = empty('Coperchio', (0, 0.62, 1.32), root, coll)
    obj('CoperchioP', set004.box_c(), (0, -0.62, 0.03), (2.0, 1.25, 0.06), M['binlid'], coll, parent=lid)
    lid.rotation_euler = (math.radians(-100), 0, 0)
    for (x, y, r) in ((-0.5, -0.1, 0.36), (0.3, 0.1, 0.42), (0.75, -0.2, 0.3)):
        set004.ball_('Sacco', r, (x, y, 1.25), M['trash'], coll, parent=root, sc=(1, 1, 0.8))
    return root, lid


def granny(coll, M):
    """vecchietta col deambulatore (pupazzo semplice come gli altri abitanti)."""
    R = props004.player(coll, 'Nonna', (0.75, 0.35, 0.75), (0.45, 0.25, 0.45), (0.98, 0.80, 0.70), (0.85, 0.85, 0.88), scale=0.82)
    head = [c for c in R['root'].children if c.name.startswith('Head')][0]
    set004.ball_('Chignon', 0.11, (0, 0.14, 0.30), material('K_hairg', (0.85, 0.85, 0.88), rough=0.8), coll, parent=head)
    for s in (-1, 1): shape('Lente', 'cyl:0.07:0.02', (s * 0.09, -0.245, 0.06), (1, 1, 1), (math.pi / 2, 0, 0), head, M['dark'], coll)
    mb = MB([M['chrome'], M['rubber']])
    for s in (-1, 1):
        for y in (-0.62, -0.28): mb.box((s * 0.30, y, 0.47), (0.03, 0.03, 0.94), 0); mb.box((s * 0.30, y, 0.03), (0.05, 0.05, 0.06), 1)
        mb.box((s * 0.30, -0.45, 0.93), (0.03, 0.40, 0.03), 0); mb.box((s * 0.30, -0.45, 0.45), (0.03, 0.34, 0.03), 0)
    mb.box((0, -0.62, 0.70), (0.60, 0.03, 0.03), 0)
    w = mb.build('Deambulatore', coll); w.parent = R['root']
    for nm in 'LR': R['shoulder' + nm].rotation_euler = (-0.75, 0, 0)
    return R


def mower(coll, M):
    """tosaerba rosso con il motore (staccabile) sopra. Restituisce (root, motore)."""
    root = empty('Tosaerba', (0, 0, 0), None, coll)
    mb = MB([M['racered'], M['steel'], M['dark']])
    mb.box((0, 0, 0.20), (0.62, 0.90, 0.16), 0); mb.box((0, -0.40, 0.14), (0.66, 0.14, 0.10), 2)
    for s in (-1, 1):
        mb.box((s * 0.24, 0.62, 0.62), (0.03, 0.03, 1.0), 1, rx=0.6)
        for y in (-0.32, 0.32): mb.box((s * 0.36, y, 0.10), (0.07, 0.20, 0.20), 2)
    mb.box((0, 0.90, 1.03), (0.56, 0.04, 0.04), 2)
    o = mb.build('TosaerbaCorpo', coll); o.parent = root
    eb = MB([M['engine'], M['racered'], M['racey'], M['steel']])
    eb.box((0, 0, 0.13), (0.40, 0.34, 0.26), 0); eb.box((0, 0, 0.32), (0.30, 0.26, 0.12), 1); eb.box((0.10, 0, 0.43), (0.10, 0.10, 0.10), 2)
    for k in range(4): eb.box((-0.23, 0, 0.04 + k * 0.06), (0.07, 0.30, 0.02), 3)
    en = eb.build('TosaerbaMotore', coll); en.parent = root; en.location = (0, 0.02, 0.28)
    return root, en


def traffic_light(coll, M):
    """semaforo di partenza: restituisce (root, [materiale rosso, giallo, verde])."""
    root = empty('Semaforo', (0, 0, 0), None, coll)
    obj('SemPalo', set004.box_c(), (0, 0, 1.3), (0.10, 0.10, 2.6), M['steel'], coll, parent=root)
    obj('SemCassa', set004.box_c(), (0, 0, 2.95), (0.34, 0.26, 0.95), M['dark'], coll, parent=root)
    mats = []
    for k, c in enumerate(((1.0, 0.05, 0.05), (1.0, 0.75, 0.0), (0.1, 1.0, 0.2))):
        m = material('K_sem%d' % k, (c[0] * 0.10, c[1] * 0.10, c[2] * 0.10), rough=0.4, emit=c, emit_strength=0.0)
        shape('SemLuce', 'cyl:0.11:0.06', (0, -0.13, 3.24 - k * 0.29), (1, 1, 1), (math.pi / 2, 0, 0), root, m, coll); mats.append(m)
    return root, mats
