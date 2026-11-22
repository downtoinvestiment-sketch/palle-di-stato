"""Ma che Scienza! ep33 v2 «Cosa succederebbe se una popstar raddoppiasse la sua altezza?» (niente voce, canta Pippo).
Pippo parte da 1,8 m e raddoppia ogni due battute (0,91 s): strada fuori citta' -> stratosfera -> Terra -> Luna -> Sole -> sistema solare -> buco nero.
Quattro scene Blender (una per scala, ognuna con la sua unita' di misura), stesso Pippo e stessa camera:
  Terra   1 = 19 m        (raddoppi 0-14)        Pianeta 1 = 10 km (15-21)
  Spazio  1 = 1.000 km    (22-33)                Sistema 1 = 1 milione di km (34-42, buco nero)
Usa SENZA MODIFICARLI i moduli di /home/claude/ptv/scripts. Tempo sulla linea della canzone: il video parte dal fotogramma 41.
Uso: python3 pop34.py -> pop34.blend, regimi.json, raddoppi.json"""
import sys, os, math, random, json
QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI); sys.path.insert(1, '/home/claude/ptv/scripts')
import bpy, bmesh
from mathutils import Vector, Matrix
from common import *
from render_setup import *
import kitlook, luci, props027pop as props027
sys.modules['props027'] = props027
import citta027 as ct, gente027 as gn, coreo027 as co, mocap_pippo as mp
import pippo2 as pippo
A_ = kitlook.A

FPS = co.FPS; NF = co.NF; B = co.B; kb = co.kb; PI = math.pi
OFF = 40; DUR = 46.0
F0 = OFF + 1; F1 = OFF + int(round(DUR * FPS))
def fv(v): return OFF + 1 + int(round(v * FPS))
def vt(f): return (f - 1 - OFF) / FPS
def sm(x): x = min(1.0, max(0.0, x)); return x * x * (3 - 2 * x)

# ======================= raddoppi: ogni due battute, a partire da 3,6 s (prima c'e' la domanda) =======================
def battuta(v): k = round((v + 1.6667 - co.T0) / co.BATT); return co.T0 + k * co.BATT - 1.6667
D = [None] + [battuta(3.6 + 0.91 * (n - 1)) for n in range(1, 43)]           # D[n] = istante del raddoppio n
H0 = 1.8; NMAX = 42; T_BH = D[42] + 0.40; V_FINE = 44.9                      # buco nero; alla fine torna sulla strada a 1,8 m
def esponente(v):
    """quanti raddoppi (con la virgola durante la crescita)."""
    if v >= V_FINE: return 0.0
    n = sum(1 for k in range(1, 43) if D[k] <= v)
    if n == 0: return 0.0
    u = (v - D[n]) / 0.30
    if u >= 1: return float(n)
    e = sm(u) + 0.10 * math.sin(PI * min(1, u * 1.15)) * u                     # un piccolo «boing»
    return n - 1 + e
def altezza(v): return H0 * 2 ** esponente(v)
def collasso(v):                                                             # 1 -> 0 quando diventa buco nero
    if V_FINE <= v or v < T_BH: return 1.0
    return max(0.0, 1 - sm((v - T_BH) / 0.55))
REGIMI = [('Terra', 19.0), ('Pianeta', 1e4), ('Spazio', 1e6), ('Sistema', 1e9)]
def regime(v):
    if v >= V_FINE or v < D[15]: return 0
    if v < D[22]: return 1
    if v < D[34]: return 2
    return 3
def scala(v):
    r = regime(v); return altezza(v) / REGIMI[r][1] / 2.3 * collasso(v)

# ======================= scene =======================
reset_scene(); S_T = bpy.context.scene; S_T.name = 'Terra'
SCENE = [S_T] + [bpy.data.scenes.new(n) for n, _ in REGIMI[1:]]
for sc in SCENE:
    setup_render(sc, 720, 1280, samples=3, fps=FPS, frames=NF); sc.frame_start = F0; sc.frame_end = F1
    A_.qualita_eevee(preset='veloce', riflessi=False, scena=sc); luci.ombre_pulite(sc, mezza_risoluzione=True); sc.eevee.taa_render_samples = 3
    sc.render.use_motion_blur = False
def coll_in(sc, nome):
    c = bpy.data.collections.new(nome); sc.collection.children.link(c); return c
envc = coll_in(S_T, 'Env'); prc = coll_in(S_T, 'Props'); gec = coll_in(S_T, 'Gente')
chc = bpy.data.collections.new('Characters'); cac = bpy.data.collections.new('Cameras'); lpc = bpy.data.collections.new('LuciPippo')
for sc in SCENE:
    for c in (chc, cac, lpc): sc.collection.children.link(c)
ENV = [envc] + [coll_in(sc, 'Env_' + sc.name) for sc in SCENE[1:]]

# ======================= cieli =======================
def cielo_tramonto(sc):
    w = bpy.data.worlds.new('Cielo_' + sc.name); sc.world = w; w.use_nodes = True; nt = w.node_tree; nt.nodes.clear()
    tc = nt.nodes.new('ShaderNodeTexCoord'); sp = nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(tc.outputs['Object'], sp.inputs[0])
    rp = nt.nodes.new('ShaderNodeValToRGB'); nt.links.new(sp.outputs['Z'], rp.inputs['Fac'])
    E = rp.color_ramp.elements; E[0].position = 0.0; E[0].color = (*ct.ORIZZONTE, 1); E[1].position = 0.62; E[1].color = (0.13, 0.11, 0.40, 1)
    for pos, col in ((0.06, (0.98, 0.36, 0.20)), (0.16, (0.72, 0.26, 0.36)), (0.32, (0.36, 0.18, 0.44))):
        x = E.new(pos); x.color = (*col, 1)
    bg = nt.nodes.new('ShaderNodeBackground'); nt.links.new(rp.outputs['Color'], bg.inputs['Color'])
    out = nt.nodes.new('ShaderNodeOutputWorld'); nt.links.new(bg.outputs['Background'], out.inputs['Surface'])
    luci.cielo_basso(w, 0.42); return w, E
def cielo_stelle(sc, luce=0.04):
    w = bpy.data.worlds.new('Stelle_' + sc.name); sc.world = w; w.use_nodes = True; nt = w.node_tree; N = nt.nodes; L = nt.links; N.clear()
    tc = N.new('ShaderNodeTexCoord'); vo = N.new('ShaderNodeTexVoronoi'); vo.inputs['Scale'].default_value = 260.0; L.new(tc.outputs['Generated'], vo.inputs['Vector'])
    mr = N.new('ShaderNodeMapRange'); mr.inputs['From Min'].default_value = 0.0; mr.inputs['From Max'].default_value = 0.06; mr.inputs['To Min'].default_value = 1.0; mr.inputs['To Max'].default_value = 0.0
    L.new(vo.outputs['Distance'], mr.inputs['Value'])
    nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 60.0; L.new(tc.outputs['Generated'], nz.inputs['Vector'])
    mb = N.new('ShaderNodeMath'); mb.operation = 'MULTIPLY'; L.new(mr.outputs['Result'], mb.inputs[0]); L.new(nz.outputs['Fac'], mb.inputs[1])
    po = N.new('ShaderNodeMath'); po.operation = 'POWER'; po.inputs[1].default_value = 3.0; L.new(mb.outputs['Value'], po.inputs[0])
    vi = N.new('ShaderNodeMath'); vi.operation = 'MULTIPLY'; vi.inputs[1].default_value = 6.0; L.new(po.outputs['Value'], vi.inputs[0])
    via = N.new('ShaderNodeTexNoise'); via.inputs['Scale'].default_value = 2.5; L.new(tc.outputs['Generated'], via.inputs['Vector'])
    vr = N.new('ShaderNodeMapRange'); vr.inputs['From Min'].default_value = 0.55; vr.inputs['From Max'].default_value = 0.8; vr.inputs['To Max'].default_value = 0.035; L.new(via.outputs['Fac'], vr.inputs['Value'])
    ad = N.new('ShaderNodeMath'); ad.operation = 'ADD'; L.new(vi.outputs['Value'], ad.inputs[0]); L.new(vr.outputs['Result'], ad.inputs[1])
    bgv = N.new('ShaderNodeBackground'); bgv.inputs['Color'].default_value = (0.85, 0.9, 1.0, 1); L.new(ad.outputs['Value'], bgv.inputs['Strength'])
    bgl = N.new('ShaderNodeBackground'); bgl.inputs['Color'].default_value = (0.25, 0.3, 0.45, 1); bgl.inputs['Strength'].default_value = luce
    lp = N.new('ShaderNodeLightPath'); mx = N.new('ShaderNodeMixShader'); out = N.new('ShaderNodeOutputWorld')
    L.new(lp.outputs['Is Camera Ray'], mx.inputs['Fac']); L.new(bgl.outputs[0], mx.inputs[1]); L.new(bgv.outputs[0], mx.inputs[2]); L.new(mx.outputs[0], out.inputs['Surface'])
    return w
W_T, E_T = cielo_tramonto(S_T)
for sc in SCENE[1:]: cielo_stelle(sc)
CIELO0 = [(round(e.position, 2), tuple(e.color[:3])) for e in E_T]
ALTO = {0.0: (0.55, 0.42, 0.55), 0.06: (0.32, 0.28, 0.50), 0.16: (0.10, 0.10, 0.28), 0.32: (0.02, 0.02, 0.09), 0.62: (0.0, 0.0, 0.01)}
for f in range(1, NF + 1):
    v = vt(f); u = sm((v - D[11]) / (D[15] - D[11])) if v < V_FINE else 0.0
    for e, (p, c0) in zip(E_T, CIELO0):
        c1 = ALTO[min(ALTO, key=lambda q: abs(q - p))]; e.color = (*[c0[i] * (1 - u) + c1[i] * u for i in range(3)], 1); e.keyframe_insert('color', frame=f)

# ======================= Pippo e coreografia (balla sul posto per tutto il video) =======================
def coreo34():
    C = co.Coreo()
    C.add('fermo0', co.clipb('143_25', 0, 12, t0=0.05), verso=0.0)
    C.fissa_origine()
    C.add('twist0', co.clipb('141_12', 12, 20, t0=0.45), verso=0.0, fusione=0.3)
    C.add('fermo1', co.clipb('143_25', 20, 32, t0=0.05), verso=0.0, fusione=0.35)
    C.add('twist1', co.clipb('141_12', 32, 39, t0=0.45), verso=0.0, fusione=0.2)
    C.add('vortice1', co.clipb('55_01', 39, 44, t0=2.2, vel=1.25), verso=0.0, verso_fine=0.0, fusione=0.2)
    C.add('fermo2', co.clipb('143_25', 44, 52, t0=0.3), verso=0.0, fusione=0.25)
    C.add('salto1', co.clipb('49_02', 52, 57, ancora=(6.79, 56), vel=0.68), verso=0.0, fusione=0.3)
    C.add('twistA', co.clipb('141_12', 57, 64, t0=0.45), verso=0.0, fusione=0.25)
    C.add('fermoA', co.clipb('143_25', 64, 72, t0=0.1), verso=0.0, fusione=0.3)
    C.add('vorticeA', co.clipb('55_01', 72, 77, t0=2.2, vel=1.25), verso=0.0, verso_fine=0.0, fusione=0.2)
    C.add('twist2', co.clipb('141_12', 77, 80, t0=1.0), verso=0.0, fusione=0.2)
    C.add('fermo3', co.clipb('143_25', 80, 88, t0=0.2), verso=0.0, fusione=0.3)
    C.add('twistB', co.clipb('141_12', 88, 96, t0=0.45), verso=0.0, fusione=0.25)
    C.add('twist3', co.clipb('141_12', 96, 100.4, t0=0.45), verso=0.0, fusione=0.2)
    C.add('salto2', co.clipb('49_02', 100.4, 105, ancora=(5.5, 104), vel=0.8), verso=0.0, fusione=0.3)
    n_fin = NF - kb(105)
    C.add('finale', mp.clip('143_25', t0=0.3, t1=0.3 + n_fin / FPS * 0.5, durata=n_fin / FPS), verso=0.0, fusione=0.3)
    return C.seq(), (-C.orig.x, -C.orig.y, 0.0)
M27 = props027.mats027()
R = pippo.build_pippo(chc); props027.look_pop(chc, R, 'P3', M27)
MIC, D_BOCCA, D_PUBBLICO = props027.microfono_in_mano(chc, R, M27)
D_PUBBLICO = Vector((-0.04, -0.90, 0.36))
seq, POSTO = coreo34(); seq = seq[:NF] + [dict(seq[-1]) for _ in range(max(0, NF - len(seq)))]
BM, BL = co.braccia(D_BOCCA, D_PUBBLICO)
mp.cinematica(seq, posto=POSTO, braccio_mic=BM, braccio_libero=BL, scala=co.rimbalzo)
print('COREOGRAFIA', mp.controllo(seq), flush=True)
def S(v): return seq[min(NF - 1, max(0, int(round((v + OFF / FPS) * FPS))))]

# posto di Pippo (piedi) in ogni scena
A1 = Vector((0.0, -40.0, 0.0))                                              # sulla strada a sud della citta'
DIR3 = Vector((0.92, 0.39, 0.0)).normalized(); R_TERRA3 = 6.371
def posto(v):
    r = regime(v); s = scala(v) if collasso(v) > 0.999 else altezza(T_BH - 0.01) / REGIMI[3][1] / 2.3
    if r == 0: return A1.copy()
    if r == 1: return Vector((0, 0, 0))
    if r == 2: return DIR3 * (R_TERRA3 + 0.55 * s) + Vector((0, 0, -0.1 * s))
    p = -Vector((0.0, -1.5, 1.15)) * s                                         # Sistema: il Sole sta davanti alla sua pancia
    if collasso(v) < 0.999:                                                   # collassa verso il suo centro
        c = p + Vector((0, 0, 1.15)) * s; return c - Vector((0, 0, 1.15)) * scala(v)
    return p
def centro(v): return posto(v) + Vector((0, 0, 1.15)) * scala(v)
GROW = empty('Crescita', (0, 0, 0), None, chc); R['root'].parent = GROW
for f in range(1, NF + 1):
    v = vt(f); s = max(scala(v), 1e-6); GROW.location = posto(v); GROW.scale = (s, s, s)
    GROW.keyframe_insert('location', frame=f); GROW.keyframe_insert('scale', frame=f)
mp.applica(R, seq, f0=1)
SEGNI = pippo._segni(R)
FACCE = dict(felice=dict(smile=2.0, brow_lift=0.9), ride=dict(smile=1.6, brow_lift=1.0, brow=-0.3), furbo=dict(smile=1.4, look=(1.0, 0.0)),
             triste=dict(brow=-1.6, brow_lift=0.3, smile=-2.0, look=(0.0, -0.6)), sorpreso=dict(brow_lift=1.5, smile=0.0))
T_ = OFF / FPS
TEMPI_FACCIA = [(0.0, 'felice'), (8.05, 'triste'), (8.95, 'furbo'), (10.42, 'felice'), (D[6] + T_, 'sorpreso'), (D[7] + T_, 'ride'), (D[14] + T_, 'sorpreso'),
                (D[15] + T_, 'felice'), (D[23] + T_, 'ride'), (D[28] + T_, 'sorpreso'), (D[29] + T_, 'felice'), (D[32] + T_, 'furbo'), (D[34] + T_, 'ride'),
                (D[41] + T_, 'sorpreso'), (V_FINE + T_, 'felice')]
def faccia(t):
    i = max(j for j, (a, _) in enumerate(TEMPI_FACCIA) if a <= t); a, n1 = TEMPI_FACCIA[i]; n0 = TEMPI_FACCIA[i - 1][1] if i else n1
    w_ = sm((t - a) / 0.18) if i else 1.0; f0, f1 = FACCE[n0], FACCE[n1]; o_ = {}
    for kk in ('smile', 'brow', 'brow_lift'): o_[kk] = f0.get(kk, 0.0) * (1 - w_) + f1.get(kk, 0.0) * w_
    l0, l1 = f0.get('look', (0, 0)), f1.get('look', (0, 0)); o_['look'] = (l0[0] * (1 - w_) + l1[0] * w_, l0[1] * (1 - w_) + l1[1] * w_)
    return o_, (n1 if w_ > 0.5 else n0), ((1 - w_) if n0 == 'furbo' and n1 != 'furbo' else (w_ if n1 == 'furbo' else 0.0))
HC = pippo.HEAD_C
for k in range(NF):
    t = k / FPS; fa, nome, wf = faccia(t)
    mb = co.bocca(t); pippo.express(R, k + 1, mouth_open=mb, **fa)
    mo_ = R['mouth_open']; sm_ = fa.get('smile', 0.0)
    if mb <= 0.02: mo_.scale = (0.001,) * 3
    else:
        sz_ = 0.3 + 1.1 * mb; hh_ = 0.055 * sz_; zmid = HC - 0.148 - (0.035 * sm_ if sm_ > 0 else 0.03 * sm_)
        mo_.location = (0, -0.279, zmid + hh_ * 0.92 * max(-1.0, min(1.0, sm_ / 0.8))); mo_.scale = (0.5 + 0.5 * mb, 1.0, sz_)
    mo_.keyframe_insert('scale', frame=k + 1); mo_.keyframe_insert('location', frame=k + 1)
    for (s_, nm), b_ in zip(((-1, 'L'), (1, 'R')), (1.4, -0.9)):
        br = R['brow' + nm]
        if wf > 0.001 or (k and faccia((k - 1) / FPS)[2] > 0.001):
            br.rotation_euler = (0, s_ * b_ * 0.45 * wf, 0); br.location.z = HC + 0.215 + 0.07 * max(0.0, -b_) * wf
            br.keyframe_insert('rotation_euler', frame=k + 1); br.keyframe_insert('location', index=2, frame=k + 1)
    if k % 2 == 0:
        for nm, g in SEGNI.items():
            on = (nm == 'guance' and nome in ('felice', 'ride')) or (nm == 'lacrime' and nome == 'triste')
            g.scale = (1, 1, 1) if on else (0.001,) * 3; g.keyframe_insert('scale', frame=k + 1)
print('PIPPO pronto', flush=True)

# ======================= aiuti =======================
def vis(o, nascosto):
    """chiavi di hide_render solo dove cambia (nascosto(v) -> bool)."""
    prima = None
    for f in range(1, NF + 1):
        h = bool(nascosto(vt(f)))
        if h != prima: o.hide_render = h; o.keyframe_insert('hide_render', frame=f); prima = h
def sotto_i_piedi(p, margine=0.0):
    d = (Vector((p[0], p[1], 0)) - A1).length
    return lambda v: regime(v) == 0 and 0.62 * scala(v) + 0.03 > d - margine
def nodo_mat(nome):
    m = bpy.data.materials.new(nome); m.use_nodes = True; N = m.node_tree.nodes; N.clear(); return m, N, m.node_tree.links
def sfera(nome, coll, r, loc=(0, 0, 0), mat=None, seg=128):
    me = bpy.data.meshes.get('E34_sfera%d' % seg)
    if me is None:
        bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=seg // 2, radius=1.0); me = bpy.data.meshes.new('E34_sfera%d' % seg); bm.to_mesh(me); bm.free()
        for p in me.polygons: p.use_smooth = True
    o = bpy.data.objects.new(nome, me); coll.objects.link(o); o.location = loc; o.scale = (r, r, r)
    if mat:
        if not me.materials: me.materials.append(None)
        o.material_slots[0].link = 'OBJECT'; o.material_slots[0].material = mat
    return o
def lontano(m, d0=40.0, d1=2600.0, mx=0.8):
    """foschia sulle lunghe distanze (al posto di quella corta della citta' del 027)."""
    return ct._foschia(m, d0=d0, d1=d1, mx=mx)

# ======================= TERRA: citta' a nord, strada verso sud, campi, alberi, lampioni, auto, nuvole =======================
FACCIATE = 'lamelle,lamelle_blu,lamelle_chiara,lamelle_rosa,mattoni,cemento,pilastri,pilastri_accesi,uffici'.split(',')
MC = ct.mats_citta('C2', A=A_, vere=FACCIATE)
_na = sum(1 for n in MC['nomi'] if n.startswith('lamelle')); _nb = len(MC['nomi']) - _na
MC['pesi'] = [(0.60 / _na) if n.startswith('lamelle') else (0.40 / _nb) for n in MC['nomi']]
def alt_citta(i, j, x, y, rnd):
    ax = abs(x); return rnd.uniform(1.0, 2.4) if ax < 3.3 else rnd.uniform(0.8, 2.0)
CITTA = ct.citta_vera(envc, MC, seme=11, colonne=(-6, 6), righe=(-7, 9), altezza=alt_citta, origine=(0.0, -0.25), vicino=lambda x, y: False)
for k in range(NF): ct.chiave_impulso(k + 1, impulso=co.impulso(k / FPS), lampo=co.lampo(k / FPS))
for m in bpy.data.materials:                                                 # foschia lunga (la citta' resta nitida da vicino)
    if not m.node_tree: continue
    for n in m.node_tree.nodes:
        if n.type == 'MAP_RANGE' and n.inputs['Value'].is_linked and n.inputs['Value'].links[0].from_node.type == 'CAMERA':
            n.inputs['From Min'].default_value = 40.0; n.inputs['From Max'].default_value = 2600.0; n.inputs['To Max'].default_value = 0.8

def mat_campi():
    mappe, _ = A_._mappe('aerial_grass_rock')
    m, N, L = nodo_mat('E34_campi')
    o = N.new('ShaderNodeOutputMaterial'); b = N.new('ShaderNodeBsdfPrincipled'); b.inputs['Roughness'].default_value = 0.95
    tc_ = N.new('ShaderNodeTexCoord'); mpn = N.new('ShaderNodeMapping'); mpn.inputs['Scale'].default_value = (0.6, 0.6, 0.6); L.new(tc_.outputs['Object'], mpn.inputs['Vector'])
    im = N.new('ShaderNodeTexImage'); im.image = bpy.data.images.load(mappe['colore']); L.new(mpn.outputs['Vector'], im.inputs['Vector'])
    vo = N.new('ShaderNodeTexVoronoi'); vo.inputs['Scale'].default_value = 0.09; L.new(tc_.outputs['Object'], vo.inputs['Vector'])
    cr = N.new('ShaderNodeValToRGB'); L.new(vo.outputs['Color'], cr.inputs['Fac']); el = cr.color_ramp.elements; cr.color_ramp.interpolation = 'CONSTANT'
    el[0].color = (0.55, 0.85, 0.40, 1); el[1].position = 0.85; el[1].color = (1.25, 1.0, 0.55, 1)
    for p_, c_ in ((0.25, (0.75, 0.95, 0.45)), (0.45, (1.05, 1.05, 0.55)), (0.6, (0.95, 0.75, 0.45)), (0.72, (0.45, 0.70, 0.35))):
        e_ = el.new(p_); e_.color = (*c_, 1)
    mx = N.new('ShaderNodeMix'); mx.data_type = 'RGBA'; mx.blend_type = 'MULTIPLY'; mx.inputs['Factor'].default_value = 1.0
    L.new(im.outputs['Color'], mx.inputs['A']); L.new(cr.outputs['Color'], mx.inputs['B']); L.new(mx.outputs['Result'], b.inputs['Base Color']); L.new(b.outputs['BSDF'], o.inputs['Surface'])
    return lontano(m)
x0, x1, y0, y1 = -19.0, 19.0, -21.0, 22.5; G_ = 60000.0
_asf = CITTA['suolo']; _asf.scale = ((x1 - x0) / 90.0 + 0.004, (y1 - y0) / 90.0 + 0.004, 1.0); _asf.location = ((x0 + x1) / 2, (y0 + y1) / 2, 0.0)
CAMPI = [((-G_ + x0) / 2, 0, x0 + G_, 2 * G_), ((G_ + x1) / 2, 0, G_ - x1, 2 * G_), ((x0 + x1) / 2, (-G_ + y0) / 2, x1 - x0, y0 + G_), ((x0 + x1) / 2, (G_ + y1) / 2, x1 - x0, G_ - y1)]
ct._scatole('Campi', [(cx, cy, 0.001, sx, sy, 0.002) for cx, cy, sx, sy in CAMPI], mat_campi(), envc, ombra=False)
def mat_asfalto():
    mappe, _ = A_._mappe('asphalt_02'); m, N, L = nodo_mat('E34_asfalto')
    o = N.new('ShaderNodeOutputMaterial'); b = N.new('ShaderNodeBsdfPrincipled'); b.inputs['Roughness'].default_value = 0.8
    tc_ = N.new('ShaderNodeTexCoord'); mpn = N.new('ShaderNodeMapping'); mpn.inputs['Scale'].default_value = (5.0, 5.0, 5.0); L.new(tc_.outputs['Object'], mpn.inputs['Vector'])
    im = N.new('ShaderNodeTexImage'); im.image = bpy.data.images.load(mappe['colore']); L.new(mpn.outputs['Vector'], im.inputs['Vector'])
    br = N.new('ShaderNodeBrightContrast'); br.inputs['Bright'].default_value = -0.15; L.new(im.outputs['Color'], br.inputs['Color']); L.new(br.outputs['Color'], b.inputs['Base Color'])
    L.new(b.outputs['BSDF'], o.inputs['Surface']); return lontano(m)
LARGA = 1.0; Y_STRADA = -19.0
ct._scatole('Strada', [(0.0, (Y_STRADA - 30000) / 2, 0.004, LARGA, 30000 + Y_STRADA, 0.008)], mat_asfalto(), envc, ombra=False)
RIGHE_M = lontano(material('E34_righe', (0.95, 0.93, 0.85), rough=0.6))
righe = [(s_ * 0.47, (Y_STRADA - 400) / 2, 0.009, 0.02, 400 + Y_STRADA, 0.002) for s_ in (-1, 1)]
y = Y_STRADA - 0.1
while y > -420:
    for xc in (-0.24, 0.0, 0.24): righe.append((xc, y, 0.009, 0.018 if xc else 0.024, 0.14, 0.002))
    y -= 0.32
ct._scatole('Righe', righe, RIGHE_M, envc, ombra=False)
# lampioni, alberi, auto: spariscono quando finiscono sotto le scarpe (non si vede: c'e' sopra il piede)
PALO_M = lontano(material('E34_palo', (0.12, 0.12, 0.13), rough=0.5)); LUCE_M = material('E34_lampada', (1.0, 0.85, 0.55), emit=(1.0, 0.8, 0.45), emit_strength=6.0)
def mesh_lampione():
    bm = bmesh.new()
    for (cx, cy, cz, sx, sy, sz) in ((0, 0, 0.23, 0.014, 0.014, 0.46), (0.07, 0, 0.455, 0.15, 0.012, 0.012), (0.14, 0, 0.445, 0.05, 0.03, 0.012)):
        r = bmesh.ops.create_cube(bm, size=1.0)
        for vv in r['verts']: vv.co = Vector((cx + vv.co.x * sx, cy + vv.co.y * sy, cz + vv.co.z * sz))
    me = bpy.data.meshes.new('E34_lampione'); bm.to_mesh(me); me.materials.append(PALO_M); me.materials.append(LUCE_M)
    for p in me.polygons:
        if p.center.x > 0.12: p.material_index = 1
    return me
ME_L = mesh_lampione(); nprop = 0
for k in range(110):
    yl = Y_STRADA - 0.6 - k * 1.1
    for s_ in (-1, 1):
        o = bpy.data.objects.new('Lampione', ME_L); envc.objects.link(o); o.location = (s_ * 0.62, yl, 0); o.rotation_euler = (0, 0, 0 if s_ < 0 else PI)
        vis(o, sotto_i_piedi(o.location)); nprop += 1
TRONCO_M = lontano(material('E34_tronco', (0.20, 0.13, 0.08), rough=0.9)); CHIOMA_M = lontano(material('E34_chioma', (0.10, 0.24, 0.07), rough=0.9))
def mesh_albero():
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=0.025, radius2=0.02, depth=0.18, matrix=Matrix.Translation((0, 0, 0.09)))
    n0 = len(bm.faces)
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.16, matrix=Matrix.Translation((0, 0, 0.32)))
    me = bpy.data.meshes.new('E34_albero'); bm.to_mesh(me); me.materials.append(TRONCO_M); me.materials.append(CHIOMA_M)
    for i, p in enumerate(me.polygons):
        p.material_index = 0 if i < n0 else 1; p.use_smooth = i >= n0
    return me
ME_A = mesh_albero(); ra = random.Random(3)
for k in range(700):
    a = ra.uniform(0, 2 * PI); d = 1.2 + ra.random() ** 1.5 * 70
    p = A1 + Vector((math.cos(a) * d, math.sin(a) * d, 0))
    if abs(p.x) < 0.95 or p.y > -23: continue
    o = bpy.data.objects.new('Albero', ME_A); envc.objects.link(o); o.location = p; sc_ = ra.uniform(0.7, 1.4); o.scale = (sc_, sc_, sc_ * ra.uniform(0.9, 1.2)); o.rotation_euler = (0, 0, ra.uniform(0, PI))
    vis(o, sotto_i_piedi(p)); nprop += 1
AUTO_M = ct.modelli_auto(A_, MC); rc = random.Random(8)
for k in range(46):
    yy = rc.uniform(-23.0, -90.0)
    if abs(yy - A1.y) < 0.45: continue
    xx = rc.choice((-0.36, -0.12, 0.12, 0.36)); o = bpy.data.objects.new('Auto', rc.choice(AUTO_M)); envc.objects.link(o)
    o.location = (xx, yy, 0.008); o.rotation_euler = (0, 0, 0 if xx > 0 else PI); vis(o, sotto_i_piedi(o.location)); nprop += 1
print('PROP', nprop, flush=True)
# fan sul bordo della strada (spariscono appena Pippo supera i 100 m: sono gia' puntini)
def seq_gente(variante):
    att = mp.clip('49_02', t0=8.04 + 0.25 * variante, t1=8.04 + 0.25 * variante + NF / FPS * 1.1, durata=NF / FPS) if variante % 2 == 0 else mp.clip('143_25', t0=0.2, t1=5.2, durata=NF / FPS)
    return mp.sequenza([mp.pezzo(att, verso=0.0)], fps=FPS, alza=1.3)
GM, GL = co.braccia(D_BOCCA, D_PUBBLICO, per_folla=True)
PUP = []
for v_, look in enumerate(gn.LOOK_FOLLA[:6]):
    sg = seq_gente(v_); mp.cinematica(sg, braccio_mic=GM, braccio_libero=GL)
    col, Rp = gn.pupazzo('Fan%d' % v_, look); mp.applica(Rp, sg, f0=1, con_scala=False); gn.canta(Rp, NF, FPS, co.bocca_folla); PUP.append(col)
rf = random.Random(5); FAN = []
for k in range(16):
    s_ = -1 if k % 2 else 1; p = A1 + Vector((s_ * rf.uniform(0.62, 1.3), rf.uniform(-0.7, 0.7), 0))
    if any((p - q).length < 0.11 for q in FAN): continue
    FAN.append(p); o = gn.copia(gec, PUP[k % len(PUP)], p.x, p.y, z=0.0, verso=math.atan2(-(p.x - A1.x), (p.y - A1.y)), altezza=rf.uniform(0.084, 0.096))
    vis(o, lambda v: regime(v) == 0 and altezza(v) > 100)
# ombra morbida sotto i piedi (Pippo non deve sembrare sospeso)
def mat_ombra():
    m, N, L = nodo_mat('E34_ombra'); o = N.new('ShaderNodeOutputMaterial'); tr = N.new('ShaderNodeBsdfTransparent'); dk = N.new('ShaderNodeEmission'); dk.inputs['Color'].default_value = (0, 0, 0, 1)
    tc_ = N.new('ShaderNodeTexCoord'); gr = N.new('ShaderNodeTexGradient'); gr.gradient_type = 'SPHERICAL'; L.new(tc_.outputs['Object'], gr.inputs['Vector'])
    mr = N.new('ShaderNodeMapRange'); mr.inputs['To Max'].default_value = 0.55; L.new(gr.outputs['Fac'], mr.inputs['Value'])
    mx = N.new('ShaderNodeMixShader'); L.new(mr.outputs['Result'], mx.inputs['Fac']); L.new(tr.outputs[0], mx.inputs[1]); L.new(dk.outputs[0], mx.inputs[2]); L.new(mx.outputs[0], o.inputs['Surface'])
    m.surface_render_method = 'BLENDED'; return m
OMBRA_M = mat_ombra()
bpy.ops.mesh.primitive_circle_add(vertices=48, radius=1.0, fill_type='NGON'); o = bpy.context.object; ME_O = o.data; bpy.data.objects.remove(o); ME_O.materials.append(OMBRA_M)
OMB = bpy.data.objects.new('OmbraPiedi', ME_O); envc.objects.link(OMB); OMB.visible_shadow = False
for f in range(1, NF + 1):
    v = vt(f); s = scala(v) if regime(v) == 0 else 0.0001; OMB.location = A1 + Vector((0, 0, 0.0095)); OMB.scale = (0.42 * s, 0.30 * s, 1); OMB.keyframe_insert('location', frame=f); OMB.keyframe_insert('scale', frame=f)
# nuvole a 1-2 km (z 55-105)
def mat_nuvola(nome='E34_nuvola', col=(1.0, 0.82, 0.70), forza=1.15):
    m, N, L = nodo_mat(nome)
    o = N.new('ShaderNodeOutputMaterial'); tr = N.new('ShaderNodeBsdfTransparent'); em = N.new('ShaderNodeEmission'); mx = N.new('ShaderNodeMixShader')
    tc_ = N.new('ShaderNodeTexCoord'); nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 1.7; nz.inputs['Detail'].default_value = 4.0; L.new(tc_.outputs['Generated'], nz.inputs['Vector'])
    gr = N.new('ShaderNodeTexGradient'); gr.gradient_type = 'SPHERICAL'; mp_ = N.new('ShaderNodeMapping'); mp_.inputs['Location'].default_value = (-0.5, -0.5, -0.5)
    L.new(tc_.outputs['Generated'], mp_.inputs['Vector']); L.new(mp_.outputs['Vector'], gr.inputs['Vector'])
    g2 = N.new('ShaderNodeMapRange'); g2.inputs['From Min'].default_value = 0.5; g2.inputs['From Max'].default_value = 0.9; L.new(gr.outputs['Fac'], g2.inputs['Value'])
    ma = N.new('ShaderNodeMath'); ma.operation = 'MULTIPLY'; L.new(nz.outputs['Fac'], ma.inputs[0]); L.new(g2.outputs['Result'], ma.inputs[1])
    cr = N.new('ShaderNodeMapRange'); cr.inputs['From Min'].default_value = 0.12; cr.inputs['From Max'].default_value = 0.42; cr.interpolation_type = 'SMOOTHSTEP'; L.new(ma.outputs['Value'], cr.inputs['Value'])
    em.inputs['Color'].default_value = (*col, 1); em.inputs['Strength'].default_value = forza
    L.new(cr.outputs['Result'], mx.inputs['Fac']); L.new(tr.outputs[0], mx.inputs[1]); L.new(em.outputs[0], mx.inputs[2]); L.new(mx.outputs[0], o.inputs['Surface'])
    m.surface_render_method = 'BLENDED'; return m
SOLE_T = luci.sole(prc, (0.0, -1.0), lato=1, energia=4.2, angolo_alto=23)
print('TERRA pronta', flush=True)

# ======================= materiali dello spazio =======================
def mat_terra():
    m, N, L = nodo_mat('E34_terra'); o = N.new('ShaderNodeOutputMaterial'); b = N.new('ShaderNodeBsdfPrincipled')
    tc_ = N.new('ShaderNodeTexCoord'); nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 1.4; nz.inputs['Detail'].default_value = 14.0; nz.inputs['Roughness'].default_value = 0.62
    L.new(tc_.outputs['Object'], nz.inputs['Vector'])
    cr = N.new('ShaderNodeValToRGB'); L.new(nz.outputs['Fac'], cr.inputs['Fac']); el = cr.color_ramp.elements
    el[0].position = 0.40; el[0].color = (0.005, 0.03, 0.12, 1); el[1].position = 0.75; el[1].color = (0.42, 0.40, 0.38, 1)
    for p_, c_ in ((0.515, (0.02, 0.10, 0.26)), (0.53, (0.55, 0.50, 0.34)), (0.545, (0.10, 0.25, 0.06)), (0.60, (0.18, 0.28, 0.08)), (0.66, (0.36, 0.28, 0.14))):
        e_ = el.new(p_); e_.color = (*c_, 1)
    sp = N.new('ShaderNodeSeparateXYZ'); L.new(tc_.outputs['Object'], sp.inputs[0]); ab = N.new('ShaderNodeMath'); ab.operation = 'ABSOLUTE'; L.new(sp.outputs['Z'], ab.inputs[0])
    gh = N.new('ShaderNodeMapRange'); gh.inputs['From Min'].default_value = 0.86; gh.inputs['From Max'].default_value = 0.9; L.new(ab.outputs['Value'], gh.inputs['Value'])
    mx = N.new('ShaderNodeMix'); mx.data_type = 'RGBA'; L.new(gh.outputs['Result'], mx.inputs['Factor']); L.new(cr.outputs['Color'], mx.inputs['A']); mx.inputs['B'].default_value = (0.9, 0.93, 0.97, 1)
    L.new(mx.outputs['Result'], b.inputs['Base Color'])
    rr = N.new('ShaderNodeMapRange'); rr.inputs['From Min'].default_value = 0.515; rr.inputs['From Max'].default_value = 0.53; rr.inputs['To Min'].default_value = 0.5; rr.inputs['To Max'].default_value = 0.9
    b.inputs['Specular IOR Level'].default_value = 0.12; L.new(nz.outputs['Fac'], rr.inputs['Value']); L.new(rr.outputs['Result'], b.inputs['Roughness']); L.new(b.outputs['BSDF'], o.inputs['Surface']); return m
def mat_nuvole_terra():
    m, N, L = nodo_mat('E34_nuvole_terra'); o = N.new('ShaderNodeOutputMaterial'); tr = N.new('ShaderNodeBsdfTransparent'); b = N.new('ShaderNodeBsdfDiffuse'); b.inputs['Color'].default_value = (0.95, 0.95, 0.97, 1)
    tc_ = N.new('ShaderNodeTexCoord'); nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 3.2; nz.inputs['Detail'].default_value = 10.0; nz.inputs['Distortion'].default_value = 0.6
    L.new(tc_.outputs['Object'], nz.inputs['Vector']); mr = N.new('ShaderNodeMapRange'); mr.inputs['From Min'].default_value = 0.57; mr.inputs['From Max'].default_value = 0.72; mr.inputs['To Max'].default_value = 0.9
    L.new(nz.outputs['Fac'], mr.inputs['Value']); mx = N.new('ShaderNodeMixShader'); L.new(mr.outputs['Result'], mx.inputs['Fac']); L.new(tr.outputs[0], mx.inputs[1]); L.new(b.outputs[0], mx.inputs[2]); L.new(mx.outputs[0], o.inputs['Surface'])
    m.surface_render_method = 'BLENDED'; return m
def mat_alone(nome, col, forza=2.0, esp=3.0):
    m, N, L = nodo_mat(nome); o = N.new('ShaderNodeOutputMaterial'); tr = N.new('ShaderNodeBsdfTransparent'); em = N.new('ShaderNodeEmission'); em.inputs['Color'].default_value = (*col, 1); em.inputs['Strength'].default_value = forza
    lw = N.new('ShaderNodeLayerWeight'); lw.inputs['Blend'].default_value = 0.5
    pw = N.new('ShaderNodeMath'); pw.operation = 'POWER'; pw.inputs[1].default_value = esp; L.new(lw.outputs['Facing'], pw.inputs[0])
    mx = N.new('ShaderNodeMixShader'); L.new(pw.outputs['Value'], mx.inputs['Fac']); L.new(tr.outputs[0], mx.inputs[1]); L.new(em.outputs[0], mx.inputs[2]); L.new(mx.outputs[0], o.inputs['Surface'])
    m.surface_render_method = 'BLENDED'; m.use_backface_culling = True; return m
def mat_luna():
    m, N, L = nodo_mat('E34_luna'); o = N.new('ShaderNodeOutputMaterial'); b = N.new('ShaderNodeBsdfPrincipled'); b.inputs['Roughness'].default_value = 1.0
    tc_ = N.new('ShaderNodeTexCoord'); nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 3.0; nz.inputs['Detail'].default_value = 10.0; L.new(tc_.outputs['Object'], nz.inputs['Vector'])
    vo = N.new('ShaderNodeTexVoronoi'); vo.inputs['Scale'].default_value = 7.0; L.new(tc_.outputs['Object'], vo.inputs['Vector'])
    cv = N.new('ShaderNodeMapRange'); cv.inputs['From Min'].default_value = 0.05; cv.inputs['From Max'].default_value = 0.35; cv.inputs['To Min'].default_value = 0.55; L.new(vo.outputs['Distance'], cv.inputs['Value'])
    mu = N.new('ShaderNodeMath'); mu.operation = 'MULTIPLY'; L.new(nz.outputs['Fac'], mu.inputs[0]); L.new(cv.outputs['Result'], mu.inputs[1])
    cr = N.new('ShaderNodeValToRGB'); L.new(mu.outputs['Value'], cr.inputs['Fac']); cr.color_ramp.elements[0].color = (0.10, 0.10, 0.10, 1); cr.color_ramp.elements[1].position = 0.6; cr.color_ramp.elements[1].color = (0.75, 0.74, 0.72, 1)
    L.new(cr.outputs['Color'], b.inputs['Base Color']); L.new(b.outputs['BSDF'], o.inputs['Surface']); return m
def mat_sole():
    m, N, L = nodo_mat('E34_sole'); o = N.new('ShaderNodeOutputMaterial'); em = N.new('ShaderNodeEmission'); em.inputs['Strength'].default_value = 7.0
    tc_ = N.new('ShaderNodeTexCoord'); nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 9.0; nz.inputs['Detail'].default_value = 8.0; L.new(tc_.outputs['Object'], nz.inputs['Vector'])
    cr = N.new('ShaderNodeValToRGB'); L.new(nz.outputs['Fac'], cr.inputs['Fac']); cr.color_ramp.elements[0].position = 0.35; cr.color_ramp.elements[0].color = (1.0, 0.35, 0.05, 1)
    cr.color_ramp.elements[1].position = 0.7; cr.color_ramp.elements[1].color = (1.0, 0.92, 0.6, 1); L.new(cr.outputs['Color'], em.inputs['Color']); L.new(em.outputs[0], o.inputs['Surface']); return m
def mat_piatto(nome, col, forza=1.5):
    return material(nome, col, emit=col, emit_strength=forza)
M_TERRA = mat_terra(); M_NUVT = mat_nuvole_terra(); M_ATM = mat_alone('E34_atmosfera', (0.30, 0.60, 1.0), 2.2, 2.5); M_LUNA = mat_luna(); M_SOLE = mat_sole(); M_CORONA = mat_alone('E34_corona', (1.0, 0.55, 0.15), 4.0, 1.6)
def terra(coll, r, loc):
    t = sfera('Terra', coll, r, loc, M_TERRA, seg=384); t.rotation_euler = (PI / 2, 0, 0.6)
    n = sfera('NuvoleTerra', coll, r * 1.0012, loc, M_NUVT, seg=192); n.rotation_euler = (PI / 2 + 0.3, 0.2, 0); n.visible_shadow = False
    a = sfera('Atmosfera', coll, r * 1.03, loc, M_ATM, seg=128); a.visible_shadow = False
    return t
def sole_lampada(coll, da, energia=3.5, nome='SoleSpazio'):
    l = bpy.data.lights.new(nome, 'SUN'); l.energy = energia; l.color = (1.0, 0.96, 0.9); l.angle = math.radians(0.6); o = bpy.data.objects.new(nome, l); coll.objects.link(o)
    o.rotation_euler = (-Vector(da)).to_track_quat('-Z', 'Y').to_euler(); return o

# ======================= PIANETA (1 = 10 km): Pippo in piedi sopra la Terra =======================
E2 = ENV[1]; R_T2 = 637.1
terra(E2, R_T2, (0, 0, -R_T2)); sole_lampada(E2, (-0.55, -0.7, 0.45), 4.5)
OMB2 = bpy.data.objects.new('OmbraPiedi2', ME_O); E2.objects.link(OMB2); OMB2.visible_shadow = False
for f in range(1, NF + 1):
    v = vt(f); s = scala(v) if regime(v) == 1 else 0.0001; OMB2.location = (0, 0, 0.004 * max(1, s)); OMB2.scale = (0.42 * s, 0.30 * s, 1); OMB2.keyframe_insert('location', frame=f); OMB2.keyframe_insert('scale', frame=f)

# ======================= SPAZIO (1 = 1.000 km): Terra vicino ai piedi, Luna, Sole =======================
E3 = ENV[2]
terra(E3, R_TERRA3, (0, 0, 0))
LUNA = sfera('Luna', E3, 1.737 * 7, Vector((-175, -70, 330)).normalized() * 384.4, M_LUNA, seg=96)
SOLE3 = sfera('Sole', E3, 696.0, (-4400.0, 1200.0, 1200.0), M_SOLE, seg=128); SOLE3.visible_shadow = False
c3 = sfera('Corona', E3, 696.0 * 1.25, SOLE3.location, M_CORONA, seg=96); c3.visible_shadow = False
sole_lampada(E3, (-0.6, -0.6, 0.5), 4.5)
SOLE3_LONTANO = Vector((-60000.0, 90000.0, 0.0))

# ======================= SISTEMA (1 = 1 milione di km): Sole, orbite, pianeti, buco nero =======================
E4 = ENV[3]
SOLE4 = sfera('Sole', E4, 0.696, (0, 0, 0), M_SOLE, seg=64); SOLE4.visible_shadow = False
C4 = sfera('Corona', E4, 0.696 * 3, (0, 0, 0), M_CORONA, seg=64); C4.visible_shadow = False
L4 = bpy.data.lights.new('LuceSole', 'POINT'); L4.color = (1.0, 0.92, 0.8); L4.shadow_soft_size = 0.7; L4.use_shadow = False
LO4 = bpy.data.objects.new('LuceSole', L4); E4.objects.link(LO4)
PIANETI = [('Mercurio', 57.9, (0.6, 0.55, 0.5), 1.0), ('Venere', 108.2, (0.95, 0.8, 0.5), 1.4), ('Terra', 149.6, (0.3, 0.6, 1.0), 1.4), ('Marte', 227.9, (0.95, 0.4, 0.2), 1.1),
           ('Giove', 778.5, (0.9, 0.75, 0.55), 2.6), ('Saturno', 1432.0, (0.95, 0.85, 0.6), 2.3), ('Urano', 2867.0, (0.6, 0.9, 0.95), 1.8), ('Nettuno', 4515.0, (0.35, 0.5, 1.0), 1.8)]
ORB_M = mat_piatto('E34_orbita', (0.55, 0.75, 1.0), 1.4); ORB_M.surface_render_method = 'BLENDED'
ORBITE = []; PALLINI = []; rp_ = random.Random(2)
for nome, r, col, dim in PIANETI:
    cu = bpy.data.curves.new('Orbita_' + nome, 'CURVE'); cu.dimensions = '3D'; sp_ = cu.splines.new('POLY'); npt = 256; sp_.points.add(npt - 1)
    for i in range(npt): a_ = 2 * PI * i / npt; sp_.points[i].co = (math.cos(a_) * r, math.sin(a_) * r, 0, 1)
    sp_.use_cyclic_u = True; cu.bevel_depth = 0.01; cu.bevel_resolution = 1; cu.materials.append(ORB_M)
    o = bpy.data.objects.new('Orbita_' + nome, cu); E4.objects.link(o); o.visible_shadow = False; ORBITE.append((o, r))
    a = rp_.uniform(0, 2 * PI); p = sfera(nome, E4, 1.0, (math.cos(a) * r, math.sin(a) * r, 0), mat_piatto('E34_p_' + nome, col, 2.0), seg=32); p.visible_shadow = False; PALLINI.append((p, dim))
def mat_disco():
    m, N, L = nodo_mat('E34_disco'); o = N.new('ShaderNodeOutputMaterial'); tr = N.new('ShaderNodeBsdfTransparent'); em = N.new('ShaderNodeEmission'); em.inputs['Strength'].default_value = 5.0
    tc_ = N.new('ShaderNodeTexCoord'); vl = N.new('ShaderNodeVectorMath'); vl.operation = 'LENGTH'; L.new(tc_.outputs['Object'], vl.inputs[0])
    cr = N.new('ShaderNodeValToRGB'); rm = N.new('ShaderNodeMapRange'); rm.inputs['From Min'].default_value = 1.0; rm.inputs['From Max'].default_value = 3.2; L.new(vl.outputs['Value'], rm.inputs['Value']); L.new(rm.outputs['Result'], cr.inputs['Fac'])
    el = cr.color_ramp.elements; el[0].color = (1.0, 0.95, 0.85, 1); el[1].color = (0.6, 0.08, 0.02, 1); e_ = el.new(0.35); e_.color = (1.0, 0.55, 0.15, 1)
    nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 3.0; nz.inputs['Detail'].default_value = 6.0; nz.inputs['Distortion'].default_value = 2.0; L.new(tc_.outputs['Object'], nz.inputs['Vector'])
    al = N.new('ShaderNodeMapRange'); al.inputs['From Min'].default_value = 3.2; al.inputs['From Max'].default_value = 1.0; L.new(vl.outputs['Value'], al.inputs['Value'])
    mu = N.new('ShaderNodeMath'); mu.operation = 'MULTIPLY'; L.new(al.outputs['Result'], mu.inputs[0]); L.new(nz.outputs['Fac'], mu.inputs[1])
    m2 = N.new('ShaderNodeMath'); m2.operation = 'MULTIPLY'; m2.inputs[1].default_value = 1.8; L.new(mu.outputs['Value'], m2.inputs[0])
    L.new(cr.outputs['Color'], em.inputs['Color']); mx = N.new('ShaderNodeMixShader'); L.new(m2.outputs['Value'], mx.inputs['Fac']); L.new(tr.outputs[0], mx.inputs[1]); L.new(em.outputs[0], mx.inputs[2]); L.new(mx.outputs[0], o.inputs['Surface'])
    m.surface_render_method = 'BLENDED'; return m
def anello(nome, r0, r1, coll, mat):
    bm = bmesh.new(); n = 128
    for i in range(n):
        a0, a1 = 2 * PI * i / n, 2 * PI * (i + 1) / n
        vs = [bm.verts.new((math.cos(a) * r, math.sin(a) * r, 0)) for a, r in ((a0, r0), (a1, r0), (a1, r1), (a0, r1))]; bm.faces.new(vs)
    me = bpy.data.meshes.new(nome); bm.to_mesh(me); me.materials.append(mat); o = bpy.data.objects.new(nome, me); coll.objects.link(o); o.visible_shadow = False; return o
M_DISCO = mat_disco()
NERO, _N, _L = nodo_mat('E34_nero'); _o = _N.new('ShaderNodeOutputMaterial'); _e = _N.new('ShaderNodeEmission'); _e.inputs['Color'].default_value = (0, 0, 0, 1); _L.new(_e.outputs[0], _o.inputs['Surface'])
BH = empty('BucoNero', (0, 0, 0), None, E4)
BHS = sfera('Orizzonte', E4, 1.0, (0, 0, 0), NERO, seg=96); BHS.parent = BH; BHS.visible_shadow = False
DISCO = anello('Disco', 1.15, 3.2, E4, M_DISCO); DISCO.parent = BH; DISCO.rotation_euler = (math.radians(8), 0, 0)
ANELLO_F = anello('AnelloLuce', 1.0, 1.22, E4, M_DISCO); ANELLO_F.parent = BH
tc = ANELLO_F.constraints.new('DAMPED_TRACK'); tc.track_axis = 'TRACK_Z'
GLOW = sfera('Bagliore', E4, 2.6, (0, 0, 0), mat_alone('E34_bagliore', (1.0, 0.5, 0.15), 0.45, 5.0), seg=64); GLOW.parent = BH; GLOW.visible_shadow = False
print('SPAZIO pronto', flush=True)

# ======================= luci che seguono Pippo (scalate) =======================
SEGUE = empty('SeguePippo', (0, 0, 0), None, lpc); cl = SEGUE.constraints.new('COPY_LOCATION'); cl.target = R['root']; cs = SEGUE.constraints.new('COPY_SCALE'); cs.target = GROW
def luce_area(nome, pos, verso, watt, lato, colore):
    l = bpy.data.lights.new(nome, 'AREA'); l.energy = watt; l.size = lato; l.color = colore; l.use_shadow = False
    o = bpy.data.objects.new(nome, l); lpc.objects.link(o); o.parent = SEGUE; o.location = pos; luci.punta(o, verso)
    for f in range(1, NF + 1): l.energy = watt * max(scala(vt(f)), 1e-6) ** 2; l.keyframe_insert('energy', frame=f)
luce_area('Controluce', (-2.4, 3.2, 3.4), (0, 0, 1.4), 900, 2.0, luci.AZZURRA)
luce_area('Riempimento', (-2.6, -4.2, 1.6), (0, 0, 1.3), 110, 4.0, luci.FREDDA)

# ======================= camere =======================
def lag_s(v, d=0.12):
    """scala per la camera: insegue quella di Pippo con un po' di ritardo (cosi' si vede che cresce)."""
    r = regime(v); vv = max(v - d, 0.0)
    if regime(vv) != r: vv = v
    return altezza(vv) / REGIMI[r][1] / 2.3 if v < T_BH or v >= V_FINE else altezza(T_BH - 0.01) / REGIMI[3][1] / 2.3
def C(v): return posto(v) + Vector((0, 0, 1.15)) * lag_s(v)
def _loc_piedi(v): m = S(v)['mondo']; return Vector((m.x, m.y, 0.0))
def loc_liscia(v, d=0.6): return sum((_loc_piedi(v + d * (i / 4 - 0.5)) for i in range(5)), Vector((0, 0, 0))) / 5
def shot(off, su=0.38, lente=30, giro=0.0, d=0.12, k=1.3):
    def fn(v, u):
        s = lag_s(v, d); o = Matrix.Rotation(giro * (u - 0.5), 3, 'Z') @ (Vector(off) * k)
        c = posto(v) + (loc_liscia(v) + Vector((0, 0, 1.15))) * s
        return c + s * o, c + s * Vector((0, 0, su)), lente
    return fn
def bh_raggio(v): return 0.0 if v < T_BH else 0.8 * altezza(T_BH - 0.01) / REGIMI[3][1] * sm((v - T_BH) / 0.6)
BH_C = None
def bh_shot(off, lente=30, giro=0.4):
    def fn(v, u):
        rb = 0.8 * altezza(T_BH - 0.01) / REGIMI[3][1]; c = BH_C; o = Matrix.Rotation(giro * (u - 0.5), 3, 'Z') @ Vector(off)
        return c + rb * o, c + rb * Vector((0, 0, 0.0)), lente
    return fn
SHOTS = [(0.0, shot((1.1, -4.6, -0.05), 1.3, 30, 0.25)), (D[1] - 0.05, shot((1.1, -4.6, -0.05), 0.42, 30, 0.15)), (D[2] + 0.45, shot((3.8, -2.4, 0.1), 0.40, 30, 0.2)), (D[5] + 0.45, shot((-1.4, -3.9, -0.55), 0.55, 24, 0.2)),
         (D[8] + 0.45, shot((1.2, -3.6, 1.4), 0.30, 30, 0.25)), (D[11] + 0.45, shot((0.6, -4.2, 0.35), 0.40, 30, 0.2)),
         (D[15], shot((3.6, -2.6, 0.15), 0.42, 32, 0.25)), (D[18] + 0.45, shot((0.8, -4.6, 1.6), 0.30, 30, 0.2)),
         (D[22], shot((-0.4, -4.8, 0.5), 0.35, 30, 0.2)), (D[26] + 0.45, shot((-0.5, -4.4, 0.2), 0.55, 30, 0.2)), (D[29] + 0.50, 'sole'),
         (D[32] + 0.45, 'sole'),
         (D[34], shot((0.4, -3.4, 2.6), 0.10, 30, 0.25)), (D[38] + 0.45, shot((1.0, -4.4, 3.2), 0.0, 30, 0.2)),
         (T_BH - 0.02, None), (V_FINE, shot((1.1, -4.6, -0.05), 1.05, 30, 0.25))]
V_SOLE = D[29] + 0.50
BH_SHOT_A = bh_shot((0.5, -7.5, 1.6), 30, 0.5)
def camera(v):
    i = max(j for j, (a, _) in enumerate(SHOTS) if fv(a) <= fv(v)); t0 = SHOTS[i][0]; t1 = SHOTS[i + 1][0] if i + 1 < len(SHOTS) else DUR
    u = min(1.0, max(0.0, (v - t0) / max(0.01, t1 - t0))); fn = SHOTS[i][1] or BH_SHOT_A
    if fn == 'luna': return luna_shot(v, u)
    if fn == 'sole': return sole_shot(v, u)
    return fn(v, u)
def luna_shot(v, u):
    s = lag_s(v); c = posto(v) + (loc_liscia(v) + Vector((0, 0, 1.15))) * s; Hh = c + Vector((0, 0, 0.75)) * s; M = Vector(LUNA.location)
    dmh = (Hh - M).normalized()
    return M - dmh * 40.0 + Vector((8.0 - 3.0 * u, 0.0, 6.0)), Hh, 30
def sole_pos(v):
    s = lag_s(v); c = posto(v) + Vector((0, 0, 1.15)) * s
    return c + Vector((-(1.0 * s + 696 * 1.25), 0.2 * s, 0.1 * s))
def sole_shot(v, u):
    s = lag_s(v); c = posto(v) + (loc_liscia(v) + Vector((0, 0, 1.15))) * s; P_ = sole_pos(v); m = (c + P_) / 2
    span = abs(c.x - P_.x) + 696 * 1.3 + 0.7 * s; dist = span * 30 / 20.25 * 1.05
    return m + Vector((0.05 * dist * (u - 0.5), -dist, 0.12 * dist)), m, 30

# buco nero: al centro di Pippo nell'istante del collasso
BH_C = posto(T_BH - 0.01) + Vector((0, 0, 1.15)) * (altezza(T_BH - 0.01) / REGIMI[3][1] / 2.3)
BH.location = BH_C
for f in range(1, NF + 1):
    v = vt(f); rb = bh_raggio(v) if regime(v) == 3 else 0.0
    BH.scale = (max(rb, 1e-4),) * 3; BH.keyframe_insert('scale', frame=f)
    DISCO.rotation_euler = (math.radians(8), 0, v * 0.9); DISCO.keyframe_insert('rotation_euler', frame=f)
CAM_PATH = [camera(vt(f)) for f in range(F0, F1 + 1)]
for f in range(1, NF + 1):
    v = vt(f); p_ = sole_pos(v) if (regime(v) == 2 and v >= V_SOLE) else SOLE3_LONTANO
    for o in (SOLE3, c3): o.location = p_; o.keyframe_insert('location', frame=f)
CAM_T = [c[0] for i, c in enumerate(CAM_PATH) if regime(vt(F0 + i)) == 0]
bpy.ops.mesh.primitive_plane_add(size=1.0); pl = bpy.context.object; NUV_ME = pl.data; bpy.data.objects.remove(pl); NUV_ME.materials.append(mat_nuvola())
rn = random.Random(7)
for k in range(260):
    a = rn.uniform(0, 2 * PI); d = 12 + rn.random() ** 1.5 * 1500
    cx, cy = A1.x + math.cos(a) * d, A1.y + math.sin(a) * d; sx_ = rn.uniform(25, 60) + d * 0.06
    if any(abs(c.z - 79) < 30 and math.hypot(c.x - cx, c.y - cy) < sx_ * 0.75 + 6 for c in CAM_T): continue
    for j in range(2):
        o = bpy.data.objects.new('Nuvola', NUV_ME); envc.objects.link(o); o.visible_shadow = False
        o.location = (cx + rn.uniform(-5, 5), cy + rn.uniform(-5, 5), rn.uniform(58, 100) + 4 * j); o.scale = (sx_ * rn.uniform(0.8, 1.2), sx_ * rn.uniform(0.5, 0.9), 1); o.rotation_euler = (0, 0, rn.uniform(0, PI))
camd = bpy.data.cameras.new('Cam'); cam = bpy.data.objects.new('Cam', camd); cac.objects.link(cam); camd.sensor_fit = 'AUTO'; camd.sensor_width = 36
for sc in SCENE: sc.camera = cam
tc.target = cam
for f in range(F0, F1 + 1):
    pos, mira, lente = CAM_PATH[f - F0]; d = (mira - pos).length
    cam.location = pos; cam.rotation_euler = (mira - pos).to_track_quat('-Z', 'Y').to_euler(); cam.keyframe_insert('location', frame=f); cam.keyframe_insert('rotation_euler', frame=f)
    camd.lens = lente; camd.keyframe_insert('lens', frame=f)
    camd.clip_start = max(0.0015, d * 0.01); camd.clip_end = max(80.0, d * 60 + 4000); camd.keyframe_insert('clip_start', frame=f); camd.keyframe_insert('clip_end', frame=f)
    v = vt(f)
    if regime(v) == 3:                                                       # sistema solare: Sole, orbite e pianeti sempre visibili (misura legata alla distanza)
        dc = (pos - Vector((0, 0, 0))).length
        rb = bh_raggio(v); dentro = lambda q: rb > 0 and (Vector(q) - BH_C).length < rb * 1.02
        rs = max(0.696, dc * 0.0035) if not dentro((0, 0, 0)) else 1e-4; SOLE4.scale = (rs,) * 3; C4.scale = (rs * 3,) * 3
        for o, r in ORBITE:
            o.data.bevel_depth = dc * 0.0011; o.data.keyframe_insert('bevel_depth', frame=f)
        for p, dim in PALLINI:
            rr = dc * 0.0028 * dim if not dentro(p.location) else 1e-4; p.scale = (rr,) * 3
        L4.energy = 140.0 * max(scala(v), 1e-3) ** 2
        for o in [SOLE4, C4] + [p for p, _ in PALLINI]: o.keyframe_insert('scale', frame=f)
        L4.keyframe_insert('energy', frame=f)

def lin(idb):
    for fc in all_fcurves(idb):
        kind = 'CONSTANT' if 'hide' in fc.data_path else 'LINEAR'
        for kp in fc.keyframe_points: kp.interpolation = kind
for o in bpy.data.objects: lin(o)
for kk in bpy.data.shape_keys: lin(kk)
for g in bpy.data.node_groups: lin(g)
for l in bpy.data.lights: lin(l)
for cu in bpy.data.curves: lin(cu)
lin(W_T); set_interp(camd, 'CONSTANT')
reg = []
for f in range(F0, F1 + 1):
    n = SCENE[regime(vt(f))].name
    if not reg or reg[-1][2] != n: reg.append([f, f, n])
    else: reg[-1][1] = f
json.dump(reg, open(os.path.join(QUI, 'regimi.json'), 'w'))
json.dump(dict(D=D[1:], T_BH=T_BH, V_FINE=V_FINE, shots=[a for a, _ in SHOTS]), open(os.path.join(QUI, 'raddoppi.json'), 'w'))
bpy.context.window_manager and None
BLEND = os.path.join(QUI, 'pop34.blend')
bpy.ops.wm.save_as_mainfile(filepath=BLEND); print('SAVED', BLEND, len(bpy.data.objects), 'oggetti', reg, flush=True)
