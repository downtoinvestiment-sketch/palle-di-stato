"""Ma che Scienza! ep33 «E se una popstar diventasse sempre più grande?» (niente voce, canta Pippo).
Pippo popstar (look P3 bianco e oro, microfono) canta la sua canzone e cresce: 2 m -> 20 m -> 200 m -> 2 km -> 10 km, poi torna piccolo.
Usa SENZA MODIFICARLI i moduli di pippo-tumbo-video (/home/claude/ptv/scripts): pippo2, citta027, gente027, coreo027, mocap_pippo, luci.
props027pop.py e' la versione «popstar» di props027 (dal commit 3218be5), copiata qui.
Timeline: tutto e' sulla linea della canzone (fotogramma f = 1 + t * 24). Il video parte dal fotogramma 41 (1,667 s: «Si e' rotta la macchina»).
Unita': 1 = 19 m (la gente e' alta 0,092). Pippo a scala 1 e' alto 2,3 (44 m).
Uso: python3 pop33.py  -> pop33.blend (qui accanto), camere.json"""
import sys, os, math, random, json
QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI); sys.path.insert(1, '/home/claude/ptv/scripts')
import bpy
from mathutils import Vector, Quaternion
from common import *
from render_setup import *
import kitlook, luci, props027pop as props027
sys.modules['props027'] = props027                                      # citta027 importa props027: deve trovare la versione popstar
import citta027 as ct, gente027 as gn, coreo027 as co, mocap_pippo as mp
import pippo2 as pippo
A_ = kitlook.A

FPS = co.FPS; NF = co.NF; B = co.B; kb = co.kb; PI = math.pi
OFF = 40                                                                # fotogrammi tagliati all'inizio (coro)
DUR = 46.0                                                              # durata del video
F0 = OFF + 1; F1 = OFF + int(round(DUR * FPS))                          # fotogrammi da rendere
def fr(t): return max(1, int(round(t * FPS)) + 1)                       # tempo della canzone -> fotogramma
def fv(v): return OFF + 1 + int(round(v * FPS))                         # tempo del video -> fotogramma
def vt(f): return (f - 1 - OFF) / FPS                                   # fotogramma -> tempo del video
def sm(x): x = min(1.0, max(0.0, x)); return x * x * (3 - 2 * x)

reset_scene(); scene = bpy.context.scene
setup_render(scene, 720, 1280, samples=3, fps=FPS, frames=NF); scene.frame_start = F0; scene.frame_end = F1
A_.qualita_eevee(preset='veloce', riflessi=False, scena=scene)
envc = collection('Env'); chc = collection('Characters'); prc = collection('Props'); cac = collection('Cameras'); gec = collection('Gente')

# ======================= cielo: tramonto; in alta quota (10 km) diventa blu scuro =======================
w = bpy.data.worlds.new('World'); scene.world = w; w.use_nodes = True; nt = w.node_tree; nt.nodes.clear()
tc = nt.nodes.new('ShaderNodeTexCoord'); sp = nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(tc.outputs['Object'], sp.inputs[0])
rp = nt.nodes.new('ShaderNodeValToRGB'); nt.links.new(sp.outputs['Z'], rp.inputs['Fac'])
E = rp.color_ramp.elements; E[0].position = 0.0; E[0].color = (*ct.ORIZZONTE, 1); E[1].position = 0.62; E[1].color = (0.13, 0.11, 0.40, 1)
CIELO = [(0.06, (0.98, 0.36, 0.20)), (0.16, (0.72, 0.26, 0.36)), (0.32, (0.36, 0.18, 0.44))]
for pos, col in CIELO:
    x = E.new(pos); x.color = (*col, 1)
bg = nt.nodes.new('ShaderNodeBackground'); bg.inputs['Strength'].default_value = 1.0; nt.links.new(rp.outputs['Color'], bg.inputs['Color'])
out = nt.nodes.new('ShaderNodeOutputWorld'); nt.links.new(bg.outputs['Background'], out.inputs['Surface'])
LUCE_CIELO = luci.cielo_basso(w, 0.42)
ALTO = {0.0: (1.0, 0.45, 0.15), 0.06: (0.75, 0.42, 0.40), 0.16: (0.30, 0.22, 0.45), 0.32: (0.06, 0.06, 0.22), 0.62: (0.01, 0.01, 0.05)}   # stratosfera: blu quasi nero
def cielo_chiave(f, u):
    for el in E:
        p = round(el.position, 2); c0 = (*ct.ORIZZONTE,) if p == 0.0 else next((c for q, c in CIELO if abs(q - p) < 0.005), (0.13, 0.11, 0.40))
        c1 = ALTO.get(p, ALTO[min(ALTO, key=lambda q: abs(q - p))])
        el.color = (*[c0[i] * (1 - u) + c1[i] * u for i in range(3)], 1); el.keyframe_insert('color', frame=f)

# ======================= coreografia: come il video 027, ma al posto di calci e pugni balla sul posto =======================
def coreo33():
    C = co.Coreo(); dp = 2 * co.BATT
    C.add('cammina', mp.cammino(0, dp, n=kb(20), fase=1 - (B(1) - 0.065) / dp), verso=0.0)
    C.fissa_origine()
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
    s = C.seq(); return s, (-C.orig.x, -C.orig.y, 0.0)

M27 = props027.mats027()
R = pippo.build_pippo(chc); props027.look_pop(chc, R, 'P3', M27)
MIC, D_BOCCA, D_PUBBLICO = props027.microfono_in_mano(chc, R, M27)
D_PUBBLICO = Vector((-0.04, -0.90, 0.36))
seq, POSTO = coreo33()
seq = seq[:NF] + [seq[-1]] * max(0, NF - len(seq))
BM, BL = co.braccia(D_BOCCA, D_PUBBLICO)
mp.cinematica(seq, posto=POSTO, braccio_mic=BM, braccio_libero=BL, scala=co.rimbalzo)
print('COREOGRAFIA', mp.controllo(seq), flush=True)
def S(t): return seq[min(NF - 1, max(0, int(round(t * FPS))))]

# ======================= crescita: scala e posto di Pippo nel tempo del video =======================
S2, S20, S200, S2K, S10K = 0.0457, 0.457, 4.57, 45.7, 228.0
A1 = Vector((0.0, -2.6, 0.0)); A2 = Vector((0.0, 27.0, 0.0)); A3 = Vector((0.0, 170.0, 0.0))
SALTI = [(8.79, 9.75, S2, S20), (17.21, 17.95, S20, S200), (24.95, 25.90, S200, S2K), (29.67, 30.60, S2K, S10K), (36.95, 37.75, S10K, S2)]
def scala(v):
    s = S2
    for a, b, s0, s1 in SALTI:
        if v < a: return s
        if v < b:
            u = (v - a) / (b - a); e = sm(u) + 0.06 * math.sin(PI * u) * (u > 0.6) * (1 if s1 > s0 else 0)     # un piccolo «boing» alla fine
            return math.exp(math.log(s0) + (math.log(s1) - math.log(s0)) * e)
        s = s1
    return s
def posto(v):
    if v < 17.0: return A1
    if v < 24.9: return A2
    if v < 37.75: return A3
    return A1
def mondo(v, p):                                                        # punto di Pippo (coordinate del 027) -> mondo
    return posto(v) + scala(v) * Vector(p)
def testa(v): return mondo(v, S(v + OFF / FPS)['testa_m'])
def piedi(v):
    m = S(v + OFF / FPS)['mondo']; return mondo(v, (m.x, m.y, 0.0))
def liscio(fn, v, d=0.5):
    return sum((fn(v + d * (i / 4 - 0.5)) for i in range(5)), Vector((0, 0, 0))) / 5

# ======================= camere (tempo del video) =======================
def _loc_testa(v): return Vector(S(v + OFF / FPS)['testa_m'])
def _loc_piedi(v): m = S(v + OFF / FPS)['mondo']; return Vector((m.x, m.y, 0.0))
def P(v, off, liscia=True):
    b = liscio(_loc_piedi, v, 0.6) if liscia else _loc_piedi(v); s = scala(v); return posto(v) + s * (b + Vector(off))
def H(v): return posto(v) + scala(v) * liscio(_loc_testa, v, 0.35)
def lag(v, d=0.18): return scala(max(0.0, v - d))
def c_cammina(v, u):    return P(v, (0.55, -3.9, 1.55)), P(v, (0, 0, 1.62)), 32
def c_folla(v, u):      return A1 + Vector((0.14 - 0.05 * u, -0.66 + 0.03 * u, 0.098)), P(v, (0, 0, 1.25)), 85
def c_faccia(v, u):     return P(v, (-0.75 + 0.2 * u, -1.9, 1.05)), H(v) + scala(v) * Vector((0, 0, -0.15)), 40
def c_largo2m(v, u):    return A1 + Vector((0.22 - 0.05 * u, -0.56, 0.055)), P(v, (0, 0, 1.6)) + Vector((0, 0, 0.06)), 24
def c_cresce1(v, u):
    t = A1 + Vector((0, 0, 0.06 + 1.0 * (scala(v) - S2) / (S20 - S2) * 0.85))
    return A1 + Vector((0.34, -1.42 - 0.08 * u, 0.085)), t, 24
def c_spalle(v, u):     return A1 + Vector((0.62 - 0.12 * u, 1.45, 1.30)), A1 + Vector((-0.05, -1.0, 0.05)), 26
def c_gambe(v, u):      return A1 + Vector((0.24, -0.60 + 0.04 * u, 0.10)), A1 + Vector((0.0, 0.0, 0.17)), 32
def c_mani(v, u):       return P(v, (0.45, -3.5 + 0.3 * u, 1.55)), P(v, (0, 0, 1.45)), 28
def c_skyline(v, u):
    hz = max(0.5, H(v).z * 0.72)
    return Vector((0.65, 6.0 - 0.6 * u, 0.13)), Vector((A2.x, A2.y, hz)), 30
def c_aereo200(v, u):   return Vector((7.5 - 1.0 * u, 2.0 + 1.0 * u, 7.0)), A2 + Vector((0, 0, 4.2)), 24
def c_voce(v, u):       return H(v) + scala(v) * Vector((0.55, -2.5 + 0.25 * u, 0.05)), H(v), 35
def c_cresce2(v, u):    return A3 + lag(v) * Vector((1.6, -7.2, 0.25)) + Vector((0, 0, 1.0)), H(v) * 0.85 + A3 * 0.15 + Vector((0, 0, 0)), 24
def c_nuvole(v, u):     return H(v) + scala(v) * Vector((1.3, -3.0 + 0.3 * u, -0.45)), H(v) + scala(v) * Vector((0, 0, -0.2)), 34
def c_cresce3(v, u):    return A3 + lag(v) * Vector((2.2, -6.6, 1.1)), H(v) * 0.9 + A3 * 0.1, 26
def c_alto(v, u):       return H(v) + scala(v) * Vector((0.9 - 0.15 * u, -3.6, 1.35)), H(v) + scala(v) * Vector((0, 0, -0.35)), 30
def c_tutto(v, u):      return A3 + Vector((950.0 - 60 * u, -1720.0, 200.0)), P(v, (0, 0, 1.12)), 75
def c_rimpicciolisce(v, u): return H(v) + scala(v) * Vector((0.45, -2.7, 0.15)), H(v), 35
def c_piazza(v, u):     return A1 + Vector((-0.14 + 0.04 * u, -0.42, 0.068)), P(v, (0, 0, 1.2)), 28
def c_fine(v, u):       return P(v, (0.55, -3.9, 1.55)), P(v, (0, 0, 1.62)), 32
SHOTS = [(0.0, c_cammina), (2.0, c_folla), (4.2, c_faccia), (6.4, c_largo2m), (8.7, c_cresce1), (11.5, c_spalle), (13.4, c_gambe), (15.2, c_mani),
         (17.0, c_skyline), (19.6, c_aereo200), (22.2, c_voce), (24.9, c_cresce2), (27.4, c_nuvole), (29.6, c_cresce3), (32.2, c_alto),
         (34.6, c_tutto), (36.95, c_rimpicciolisce), (37.75, c_piazza), (41.3, c_fine)]
SCOSSE = [(13.55, 0.010), (14.05, 0.008), (14.6, 0.008)]                # le ginocchia scricchiolano
def trema(v):
    a = sum(amp * math.exp(-(v - t0) * 9.0) for t0, amp in SCOSSE if 0 <= v - t0 < 0.6)
    return Vector((a * math.sin(v * 71.0), a * 0.5 * math.sin(v * 53.0 + 1.0), a * math.sin(v * 89.0 + 2.0)))
def camera(v):
    i = max(j for j, (a, _) in enumerate(SHOTS) if fv(a) <= fv(v)); t0 = SHOTS[i][0]; t1 = SHOTS[i + 1][0] if i + 1 < len(SHOTS) else DUR
    u = min(1.0, max(0.0, (v - t0) / max(0.01, t1 - t0))); pos, mira, lente = SHOTS[i][1](v, u)
    return pos + trema(v), mira, lente
CAM_PATH = [camera(vt(f)) for f in range(F0, F1 + 1)]

# ======================= citta' (come nel 027, senza le torri da abbattere) =======================
FACCIATE = 'lamelle,lamelle_blu,lamelle_chiara,lamelle_rosa,mattoni,cemento,pilastri,pilastri_accesi,uffici'.split(',')
MC = ct.mats_citta('C2', A=A_, vere=FACCIATE)
_na = sum(1 for n in MC['nomi'] if n.startswith('lamelle')); _nb = len(MC['nomi']) - _na
MC['pesi'] = [(0.60 / _na) if n.startswith('lamelle') else (0.40 / _nb) for n in MC['nomi']]
PIAZZA = (-1.95, 1.95, -6.10, 0.40)
def niente_isolato(i, j): return -1 <= i <= 1 and -4 <= j <= 0
def altezza(i, j, x, y, rnd):
    ax = abs(x)
    if y > 0.45:
        if ax < 0.55: return rnd.uniform(0.6, 1.1)
        if ax < 1.95: return rnd.uniform(0.8, 1.5)
        if ax < 3.3: return rnd.uniform(0.9, 1.8)
        return rnd.uniform(1.0, 2.2)
    if y > -6.1: return rnd.uniform(1.3, 2.25) if ax < 3.3 else rnd.uniform(1.0, 2.0)
    return rnd.uniform(0.7, 1.5) if ax < 2.0 else rnd.uniform(0.8, 1.8)
CITTA = ct.citta_vera(envc, MC, seme=11, colonne=(-6, 6), righe=(-7, 9), altezza=altezza, origine=(0.0, -0.25),
                      niente_isolato=niente_isolato, vicino=lambda x, y: False)
MC['piazza'] = ct.mat_semplice('M27v_piazza', (0.20, 0.165, 0.17), rough=0.8)
ct._scatole('Piazza', [((PIAZZA[0] + PIAZZA[1]) / 2, (PIAZZA[2] + PIAZZA[3]) / 2, 0.011, PIAZZA[1] - PIAZZA[0], PIAZZA[3] - PIAZZA[2], 0.022)], MC['piazza'], envc, ombra=False)
AUTO_M = ct.modelli_auto(A_, MC)
def strada_ok(asse, c):
    if asse == 'x': return c > 1.2 or c < -6.0
    return abs(c) > 2.6
TRAF = ct.Traffico(envc, AUTO_M, CITTA, seme=5, v=0.42, zona=(-5.0, 5.0, -7.6, 8.6), pieno=0.6, strada_ok=strada_ok)
for f in range(1, NF + 1): TRAF.passo(f)
TRAF.chiavi(NF)
for k in range(NF):
    ct.chiave_impulso(k + 1, impulso=co.impulso(k / FPS), lampo=co.lampo(k / FPS))
print('CITTA pronta', flush=True)

# ======================= campagna attorno alla citta': campi visti dall'alto, foschia =======================
def mat_campi():
    m = bpy.data.materials.new('E33_campi'); m.use_nodes = True; N = m.node_tree.nodes; L = m.node_tree.links; N.clear()
    o = N.new('ShaderNodeOutputMaterial'); b = N.new('ShaderNodeBsdfPrincipled'); b.inputs['Roughness'].default_value = 0.95
    tc_ = N.new('ShaderNodeTexCoord'); vo = N.new('ShaderNodeTexVoronoi'); vo.inputs['Scale'].default_value = 0.06; L.new(tc_.outputs['Object'], vo.inputs['Vector'])
    cr = N.new('ShaderNodeValToRGB'); L.new(vo.outputs['Color'], cr.inputs['Fac']); el = cr.color_ramp.elements; cr.color_ramp.interpolation = 'CONSTANT'
    el[0].color = (0.10, 0.20, 0.05, 1); el[1].position = 0.85; el[1].color = (0.32, 0.26, 0.10, 1)
    for p_, c_ in ((0.2, (0.16, 0.26, 0.06)), (0.4, (0.22, 0.30, 0.08)), (0.55, (0.30, 0.25, 0.11)), (0.7, (0.12, 0.17, 0.05))):
        e_ = el.new(p_); e_.color = (*c_, 1)
    nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 3.0; L.new(tc_.outputs['Object'], nz.inputs['Vector'])
    mx = N.new('ShaderNodeMix'); mx.data_type = 'RGBA'; mx.blend_type = 'MULTIPLY'; mx.inputs['Factor'].default_value = 0.35
    L.new(cr.outputs['Color'], mx.inputs['A']); L.new(nz.outputs['Color'], mx.inputs['B']); L.new(mx.outputs['Result'], b.inputs['Base Color']); L.new(b.outputs['BSDF'], o.inputs['Surface'])
    return ct._foschia(m, d0=40.0, d1=2600.0, mx=0.8)
x0, x1, y0, y1 = -24.0, 24.0, -26.0, 23.0; G_ = 40000.0                  # buco sopra l'asfalto della citta'
campi = [((-G_ + x0) / 2, 0, 0, -G_ - x0 if False else x0 + G_, 2 * G_), ((G_ + x1) / 2, 0, 0, G_ - x1, 2 * G_),
         ((x0 + x1) / 2, (-G_ + y0) / 2, 0, x1 - x0, y0 + G_), ((x0 + x1) / 2, (G_ + y1) / 2, 0, x1 - x0, G_ - y1)]
CAMPI_M = mat_campi()
ct._scatole('Campi', [(cx, cy, 0.001, sx, sy, 0.002) for cx, cy, _, sx, sy in campi], CAMPI_M, envc, ombra=False)

# ======================= nuvole: lastre piatte a 1.500-2.000 m (z 80-105) =======================
def mat_nuvola():
    m = bpy.data.materials.new('E33_nuvola'); m.use_nodes = True; N = m.node_tree.nodes; L = m.node_tree.links; N.clear()
    o = N.new('ShaderNodeOutputMaterial'); tr = N.new('ShaderNodeBsdfTransparent'); em = N.new('ShaderNodeEmission'); mx = N.new('ShaderNodeMixShader')
    tc_ = N.new('ShaderNodeTexCoord'); nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 1.7; nz.inputs['Detail'].default_value = 4.0
    L.new(tc_.outputs['Generated'], nz.inputs['Vector'])
    gr = N.new('ShaderNodeTexGradient'); gr.gradient_type = 'SPHERICAL'; mp_ = N.new('ShaderNodeMapping'); mp_.inputs['Location'].default_value = (-0.5, -0.5, -0.5)
    L.new(tc_.outputs['Generated'], mp_.inputs['Vector']); L.new(mp_.outputs['Vector'], gr.inputs['Vector'])
    g2 = N.new('ShaderNodeMapRange'); g2.inputs['From Min'].default_value = 0.5; g2.inputs['From Max'].default_value = 0.9; L.new(gr.outputs['Fac'], g2.inputs['Value'])
    ma = N.new('ShaderNodeMath'); ma.operation = 'MULTIPLY'; L.new(nz.outputs['Fac'], ma.inputs[0]); L.new(g2.outputs['Result'], ma.inputs[1])
    cr = N.new('ShaderNodeMapRange'); cr.inputs['From Min'].default_value = 0.12; cr.inputs['From Max'].default_value = 0.42; cr.interpolation_type = 'SMOOTHSTEP'; L.new(ma.outputs['Value'], cr.inputs['Value'])
    em.inputs['Color'].default_value = (1.0, 0.80, 0.68, 1); em.inputs['Strength'].default_value = 1.15
    L.new(cr.outputs['Result'], mx.inputs['Fac']); L.new(tr.outputs[0], mx.inputs[1]); L.new(em.outputs[0], mx.inputs[2]); L.new(mx.outputs[0], o.inputs['Surface'])
    m.surface_render_method = 'BLENDED'; return m
NUV_M = mat_nuvola(); rn = random.Random(7)
bpy.ops.mesh.primitive_plane_add(size=1.0); pl = bpy.context.object; NUV_ME = pl.data; bpy.data.objects.remove(pl)
NUV_ME.materials.append(NUV_M); nn = 0
NUVOLE = empty('Nuvole', (0, 0, 0), None, envc)
for f in range(1, NF + 1):                                             # le nuvole ci sono solo attorno al Pippo enorme (sotto terra nel resto del video)
    v = vt(f); NUVOLE.location = (0, 0, 0 if 24.9 <= v < 37.75 else -6000); NUVOLE.keyframe_insert('location', frame=f)
for k in range(260):
    a = rn.uniform(0, 2 * PI); d = 14 + rn.random() ** 1.6 * 900
    cx, cy = A3.x + math.cos(a) * d, A3.y + math.sin(a) * d
    if math.hypot(cx - A3.x, cy - A3.y) < 14: continue
    sx_ = rn.uniform(25, 60) + d * 0.08
    for j in range(2):                                                  # due strati: un po' di spessore
        o = bpy.data.objects.new('Nuvola', NUV_ME); envc.objects.link(o); o.visible_shadow = False; o.parent = NUVOLE
        o.location = (cx + rn.uniform(-6, 6), cy + rn.uniform(-6, 6), rn.uniform(82, 100) + 5 * j); o.scale = (sx_ * rn.uniform(0.8, 1.2), sx_ * rn.uniform(0.5, 0.9), 1); o.rotation_euler = (0, 0, rn.uniform(0, PI)); nn += 1
for k in range(70):                                                     # anello fitto all'altezza della testa del Pippo da 2 km
    a = rn.uniform(0, 2 * PI); d = rn.uniform(16, 110); sx_ = rn.uniform(18, 40)
    o = bpy.data.objects.new('Nuvola', NUV_ME); envc.objects.link(o); o.visible_shadow = False; o.parent = NUVOLE
    o.location = (A3.x + math.cos(a) * d, A3.y + math.sin(a) * d, rn.uniform(86, 99)); o.scale = (sx_, sx_ * rn.uniform(0.5, 0.9), 1); o.rotation_euler = (0, 0, rn.uniform(0, PI)); nn += 1
print('NUVOLE', nn, flush=True)

# ======================= Pippo: movimento, scala, faccia =======================
GROW = empty('Crescita', (0, 0, 0), None, chc); R['root'].parent = GROW
for f in range(1, NF + 1):
    v = vt(f); GROW.location = posto(v); s = scala(v); GROW.scale = (s, s, s)
    GROW.keyframe_insert('location', frame=f); GROW.keyframe_insert('scale', frame=f)
mp.applica(R, seq, f0=1)
SEGNI = pippo._segni(R)
FACCE = dict(felice=dict(smile=2.0, brow_lift=0.9), ride=dict(smile=1.6, brow_lift=1.0, brow=-0.3), furbo=dict(smile=1.4, look=(1.0, 0.0)),
             triste=dict(brow=-1.6, brow_lift=0.3, smile=-2.0, look=(0.0, -0.6)), sorpreso=dict(brow_lift=1.5, smile=0.0))
T_ = OFF / FPS                                                          # tempo del video -> tempo della canzone: + T_
TEMPI_FACCIA = [(0.0, 'felice'), (8.05, 'triste'), (8.95, 'furbo'), (10.42, 'felice'), (13.55 + T_, 'sorpreso'), (14.5 + T_, 'triste'), (15.1 + T_, 'ride'),
                (17.9, 'ride'), (19.0 + T_, 'sorpreso'), (19.9 + T_, 'felice'), (24.5, 'ride'), (25.0 + T_, 'sorpreso'), (25.9 + T_, 'ride'),
                (29.67 + T_, 'sorpreso'), (30.6 + T_, 'felice'), (32.4 + T_, 'triste'), (33.4 + T_, 'furbo'), (36.95 + T_, 'sorpreso'), (37.9 + T_, 'ride'), (B(104), 'felice')]
def faccia(t):
    i = max(j for j, (a, _) in enumerate(TEMPI_FACCIA) if a <= t); a, n1 = TEMPI_FACCIA[i]; n0 = TEMPI_FACCIA[i - 1][1] if i else n1
    w_ = sm((t - a) / 0.18) if i else 1.0; f0, f1 = FACCE[n0], FACCE[n1]; o_ = {}
    for kk in ('smile', 'brow', 'brow_lift'):
        o_[kk] = f0.get(kk, 0.0) * (1 - w_) + f1.get(kk, 0.0) * w_
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

# ======================= infrasuoni: anelli lenti che escono dalla bocca (200 m) =======================
ANELLO_M = bpy.data.materials.new('E33_anello'); ANELLO_M.use_nodes = True; N_ = ANELLO_M.node_tree.nodes; L_ = ANELLO_M.node_tree.links; N_.clear()
o_ = N_.new('ShaderNodeOutputMaterial'); tr_ = N_.new('ShaderNodeBsdfTransparent'); em_ = N_.new('ShaderNodeEmission'); mx_ = N_.new('ShaderNodeMixShader'); oi_ = N_.new('ShaderNodeObjectInfo')
em_.inputs['Color'].default_value = (0.55, 0.9, 1.0, 1); em_.inputs['Strength'].default_value = 3.0
L_.new(oi_.outputs['Alpha'], mx_.inputs['Fac']); L_.new(tr_.outputs[0], mx_.inputs[1]); L_.new(em_.outputs[0], mx_.inputs[2]); L_.new(mx_.outputs[0], o_.inputs['Surface'])
ANELLO_M.surface_render_method = 'BLENDED'
ANELLI = []
for i in range(5):
    bpy.ops.mesh.primitive_torus_add(major_radius=1.0, minor_radius=0.025, major_segments=64, minor_segments=8); o = bpy.context.object
    o.name = 'Infrasuono%d' % i; o.data.materials.append(ANELLO_M); o.visible_shadow = False; o.rotation_euler = (PI / 2, 0, 0)
    for c in o.users_collection: c.objects.unlink(o)
    prc.objects.link(o); ANELLI.append(o)
V_INF = (21.4, 24.9); PER = 1.6
for i, o in enumerate(ANELLI):
    for f in range(1, NF + 1):
        v = vt(f)
        if V_INF[0] <= v < V_INF[1]:
            q = ((v - V_INF[0]) / PER - i / len(ANELLI)) % 1.0; s = scala(v); hp = testa(v) + s * Vector((0, -0.32, -0.12))
            r = s * (0.35 + 5.0 * q); o.location = hp; o.scale = (r, r, r * 1.6); o.color = (1, 1, 1, 0.85 * (1 - q) ** 1.5 * min(1.0, q * 8))
        else:
            o.scale = (0.001,) * 3; o.color = (1, 1, 1, 0.0)
        o.keyframe_insert('location', frame=f); o.keyframe_insert('scale', frame=f); o.keyframe_insert('color', frame=f)

# ======================= gente in piazza: un cerchio attorno a Pippo (mai sotto i suoi piedi, mai davanti alla camera) =======================
def seq_gente(variante, specchio):
    k20 = kb(20) + 4
    if variante % 3 == 2: att = mp.clip('143_25', t0=0.2, t1=5.2, durata=k20 / FPS)
    else: att = mp.clip('49_02', t0=8.04 + 0.25 * (variante % 3), t1=8.04 + 0.25 * (variante % 3) + k20 / FPS * 1.1, durata=k20 / FPS)
    a = mp.sequenza([mp.pezzo(att, verso=0.0)], fps=FPS, alza=1.3)
    o2 = [dict(x) for x in a]
    for k in range(k20, NF):
        s = seq[k]; o2.append(dict(loc=(0.0, 0.0, s['mondo'].z), yaw=s['yaw_m'], qb=s['qb'], qt=s['qt'], gambe=s['gambe'], braccia=s['braccia'], piede=s['piede'], volo=s['volo'], kb=s.get('kb')))
    nb = 10; u0 = o2[k20 - 1]
    for i in range(nb):
        w_ = (i + 1) / (nb + 1); c = o2[k20 + i]
        o2[k20 + i] = dict(loc=tuple(Vector(u0['loc']).lerp(Vector(c['loc']), w_)), yaw=u0['yaw'] * (1 - w_) + c['yaw'] * w_, qb=u0['qb'].slerp(c['qb'], w_), qt=u0['qt'].slerp(c['qt'], w_),
                           gambe={q: u0['gambe'][q].lerp(c['gambe'][q], w_).normalized() for q in 'LR'}, braccia={q: u0['braccia'][q].lerp(c['braccia'][q], w_).normalized() for q in 'LR'},
                           piede=c['piede'], volo=c['volo'], kb=c.get('kb'))
    return gn.specchia_seq(o2) if specchio else o2
GM, GL = co.braccia(D_BOCCA, D_PUBBLICO, per_folla=True)
SEQ_G = []
for m in range(3):
    sg = seq_gente(m, specchio=True); mp.cinematica(sg, braccio_mic=GM, braccio_libero=GL); SEQ_G.append(sg)
PUP = []
for v_, look in enumerate(gn.LOOK_FOLLA):
    col, Rp = gn.pupazzo('Gente%d' % v_, look); mp.applica(Rp, SEQ_G[v_ % 3], f0=1, con_scala=False); gn.canta(Rp, NF, FPS, co.bocca_folla); PUP.append(col)
CAM_BASSE = [c[0] for c in CAM_PATH if c[0].z < 0.5 and (c[0] - A1).length < 3.0]
def dist_segm(x, y, a, b):
    ax, ay, bx, by = a.x, a.y, b.x, b.y; dx, dy = bx - ax, by - ay; L2 = dx * dx + dy * dy or 1e-9
    u = max(0.0, min(1.0, ((x - ax) * dx + (y - ay) * dy) / L2)); return math.hypot(x - ax - u * dx, y - ay - u * dy)
rg = random.Random(4); GXY = []; tent = 0
while len(GXY) < 150 and tent < 60000:
    tent += 1; x = rg.uniform(PIAZZA[0] + 0.06, PIAZZA[1] - 0.06); y = rg.uniform(PIAZZA[2] + 0.06, PIAZZA[3] - 0.06)
    r = math.hypot(x - A1.x, y - A1.y)
    if r < 0.42 or r > 1.9: continue
    if any((x - a) ** 2 + (y - b) ** 2 < 0.105 ** 2 for a, b in GXY): continue
    if any((x - c.x) ** 2 + (y - c.y) ** 2 < 0.13 ** 2 for c in CAM_BASSE): continue
    if any(dist_segm(x, y, c, A1) < 0.075 for c in CAM_BASSE[::6]): continue
    GXY.append((x, y))
for i, (x, y) in enumerate(GXY):
    gn.copia(gec, PUP[i % len(PUP)], x, y, z=0.022, verso=math.atan2(-(x - A1.x), (y - A1.y)), altezza=rg.uniform(0.084, 0.096))
print('GENTE', len(GXY), flush=True)

# ======================= luci: sole basso di lato, cielo debole, controluce azzurro e riempimento che seguono Pippo (scalati) =======================
SOLE = luci.sole(prc, (0.0, -1.0), lato=1, energia=4.2, angolo_alto=23)
SEGUE = empty('SeguePippo', (0, 0, 0), None, prc); cl = SEGUE.constraints.new('COPY_LOCATION'); cl.target = R['root']
cs = SEGUE.constraints.new('COPY_SCALE'); cs.target = GROW
def luce_area(nome, pos, verso, watt, lato, colore):
    l = bpy.data.lights.new(nome, 'AREA'); l.energy = watt; l.size = lato; l.color = colore; l.use_shadow = False
    o = bpy.data.objects.new(nome, l); prc.objects.link(o); o.parent = SEGUE; o.location = pos; luci.punta(o, verso)
    for f in range(1, NF + 1):
        l.energy = watt * scala(vt(f)) ** 2; l.keyframe_insert('energy', frame=f)
    return o
luce_area('Controluce', (-2.4, 3.2, 3.4), (0, 0, 1.4), 900, 2.0, luci.AZZURRA)
luce_area('Riempimento', (-2.6, -4.2, 1.6), (0, 0, 1.3), 110, 4.0, luci.FREDDA)
luci.ombre_pulite(scene, mezza_risoluzione=True); scene.eevee.taa_render_samples = 3
for f in range(1, NF + 1):                                              # in stratosfera il cielo diventa blu scuro
    v = vt(f); u = sm((v - 29.9) / 1.0) * (1 - sm((v - 36.95) / 0.6)); cielo_chiave(f, u)

# ======================= camera =======================
camd = bpy.data.cameras.new('Cam'); cam = bpy.data.objects.new('Cam', camd); cac.objects.link(cam); scene.camera = cam
camd.sensor_fit = 'AUTO'; camd.sensor_width = 36
for f in range(F0, F1 + 1):
    pos, mira, lente = CAM_PATH[f - F0]; d = (mira - pos).length
    cam.location = pos; cam.rotation_euler = (mira - pos).to_track_quat('-Z', 'Y').to_euler()
    cam.keyframe_insert('location', frame=f); cam.keyframe_insert('rotation_euler', frame=f)
    camd.lens = lente; camd.keyframe_insert('lens', frame=f)
    camd.clip_start = max(0.0015, min(1.5, d * 0.012)); camd.clip_end = max(60.0, d * 40 + 3000); camd.keyframe_insert('clip_start', frame=f); camd.keyframe_insert('clip_end', frame=f)

def lin(idb):
    for fc in all_fcurves(idb):
        kind = 'CONSTANT' if 'hide' in fc.data_path else 'LINEAR'
        for kp in fc.keyframe_points: kp.interpolation = kind
for o in bpy.data.objects: lin(o)
for kk in bpy.data.shape_keys: lin(kk)
for g in bpy.data.node_groups: lin(g)
for l in bpy.data.lights: lin(l)
lin(w); set_interp(camd, 'CONSTANT')
scene.render.use_motion_blur = False
json.dump([[a, SHOTS[i + 1][0] if i + 1 < len(SHOTS) else DUR, fn.__name__] for i, (a, fn) in enumerate(SHOTS)], open(os.path.join(QUI, 'camere.json'), 'w'))
BLEND = os.path.join(QUI, 'pop33.blend')
bpy.ops.wm.save_as_mainfile(filepath=BLEND); print('SAVED', BLEND, len(bpy.data.objects), 'oggetti', flush=True)
