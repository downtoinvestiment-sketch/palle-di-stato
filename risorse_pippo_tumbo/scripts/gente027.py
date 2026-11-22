"""Gente per il video 027: persone da cartone piccole piccole che ballano come Pippo, fatte a mano nello stile della serie
(testa grande, occhi grandi con la lucina, naso, guance, bocca che si apre quando cantano in coro, capelli e vestiti diversi).
Ogni pupazzo ha gli stessi perni di Pippo (root, body, head, shoulderL/R, hipL/R, footL/R), quindi prende gli stessi movimenti
con mocap_pippo.applica(). Ogni parte rigida e' UNA mesh sola con piu' materiali (testa, bocca, busto, braccia, gambe, piedi:
9 oggetti a persona), cosi' centinaia di copie costano poco. Si fanno pochi pupazzi animati (uno per collezione, fuori scena) e
poi centinaia di copie «istanza di collezione»: le copie rimpicciolite rimpiccioliscono anche gli spostamenti, quindi i piedi
non scivolano. Non tocca pippo.py."""
import math, random
import bpy, bmesh
from mathutils import Vector, Quaternion, Matrix, Euler
from common import *

PI = math.pi
ALTEZZA = 2.02                                                              # altezza del pupazzo nella sua collezione (come Pippo senza ciuffo)

# ------------------------------------------------------------------------- colori
P_CHIARA = (0.98, 0.76, 0.60); P_ROSA = (0.95, 0.64, 0.48); P_OLIVA = (0.82, 0.54, 0.36); P_BRUNA = (0.56, 0.34, 0.22); P_SCURA = (0.36, 0.21, 0.14)
C_NERI = (0.035, 0.03, 0.03); C_CASTANI = (0.26, 0.13, 0.05); C_BIONDI = (0.92, 0.68, 0.22); C_ROSSI = (0.72, 0.20, 0.06); C_GRIGI = (0.72, 0.72, 0.75); C_ROSA = (1.0, 0.42, 0.68)
ORO = (1.0, 0.70, 0.16); BIANCO = (0.94, 0.94, 0.94); NERO = (0.03, 0.03, 0.035); JEANS = (0.10, 0.22, 0.52)

# Dodici persone della folla: ognuna con faccia, capelli e vestiti suoi.
LOOK_FOLLA = [
    dict(pelle=P_CHIARA, capelli=C_CASTANI, taglio='corto', tipo='maglietta', maglia=(0.88, 0.10, 0.10), stemma='cerchio', c2=BIANCO, gambe='lunghi', panta=JEANS, scarpe=BIANCO),
    dict(pelle=P_ROSA, capelli=C_BIONDI, taglio='coda', tipo='vestito', maglia=(1.0, 0.78, 0.08), c2=(1.0, 0.45, 0.60), gambe='nude', panta=BIANCO, scarpe=(1.0, 0.40, 0.60), corpo='magro'),
    dict(pelle=P_SCURA, capelli=C_NERI, taglio='cappellino', verso_visiera=-1, c_cappello=(0.10, 0.35, 0.90), tipo='canotta', maglia=(1.0, 0.45, 0.05), c2=BIANCO, gambe='corti', panta=NERO,
         scarpe=(0.85, 0.08, 0.08), extra=('telefono',)),
    dict(pelle=P_BRUNA, capelli=C_NERI, taglio='afro', tipo='felpa', maglia=(0.50, 0.22, 0.80), c2=(0.36, 0.14, 0.62), gambe='lunghi', panta=(0.55, 0.56, 0.60), scarpe=BIANCO, extra=('cuffie',)),
    dict(pelle=P_CHIARA, capelli=C_CASTANI, taglio='pelato', tipo='salopette', maglia=BIANCO, c2=(0.12, 0.48, 0.22), gambe='lunghi', panta=(0.12, 0.48, 0.22), scarpe=(0.40, 0.22, 0.10),
         corpo='tondo', extra=('baffi',)),
    dict(pelle=P_CHIARA, capelli=C_ROSSI, taglio='caschetto', tipo='giacca', maglia=(0.05, 0.60, 0.62), c2=BIANCO, gambe='lunghi', panta=(0.10, 0.10, 0.14), scarpe=(1.0, 0.80, 0.10), extra=('occhiali',)),
    dict(pelle=P_ROSA, capelli=(0.45, 0.24, 0.09), taglio='ciuffi', tipo='maglietta', maglia=BIANCO, stemma='stella', c2=ORO, gambe='corti', panta=(0.10, 0.30, 0.80), scarpe=BIANCO, extra=('luce',), c_luce=(1.0, 0.75, 0.2)),
    dict(pelle=P_OLIVA, capelli=C_ROSA, taglio='codini', tipo='maglietta', maglia=(1.0, 0.50, 0.72), stemma='cuore', c2=BIANCO, gambe='corti', panta=(0.30, 0.45, 0.80), scarpe=(0.55, 0.25, 0.85),
         corpo='magro', extra=('telefono',)),
    dict(pelle=P_OLIVA, capelli=C_NERI, taglio='berretto', c_cappello=(0.10, 0.50, 0.25), tipo='felpa', maglia=(0.85, 0.12, 0.10), c2=(0.60, 0.06, 0.06), gambe='lunghi', panta=NERO,
         scarpe=(0.62, 0.42, 0.20), extra=('barba',)),
    dict(pelle=P_CHIARA, capelli=C_NERI, taglio='lunghi', tipo='maglietta', maglia=(0.45, 0.75, 1.0), stemma='cerchio', c2=(1.0, 0.9, 0.3), gambe='gonna', panta=BIANCO, scarpe=BIANCO,
         corpo='magro', extra=('luce',), c_luce=(1.0, 0.35, 0.75)),
    dict(pelle=P_ROSA, capelli=C_GRIGI, taglio='ricci', tipo='vestito', maglia=(0.62, 0.20, 0.72), c2=BIANCO, gambe='nude', panta=BIANCO, scarpe=(0.25, 0.10, 0.35), corpo='tondo', extra=('collana',)),
    dict(pelle=P_BRUNA, capelli=C_NERI, taglio='cappellino', verso_visiera=1, c_cappello=(0.90, 0.10, 0.10), tipo='righe', maglia=(1.0, 0.85, 0.10), c2=(0.10, 0.25, 0.70), gambe='corti',
         panta=(0.10, 0.25, 0.70), scarpe=(0.10, 0.75, 0.35), extra=('occhiali_sole',)),
]
# Il corpo di ballo: tre facce diverse, stessa divisa bianca e oro di Pippo.
_DIVISA = dict(tipo='divisa', maglia=BIANCO, c2=ORO, stemma='stella', gambe='stivali', panta=BIANCO, scarpe=ORO)
LOOK_BALLO = [
    dict(_DIVISA, pelle=P_OLIVA, capelli=C_NERI, taglio='coda', corpo='magro', sguardo=0.0),
    dict(_DIVISA, pelle=P_SCURA, capelli=C_NERI, taglio='corto', sguardo=0.0),
    dict(_DIVISA, pelle=P_CHIARA, capelli=C_BIONDI, taglio='codini', corpo='magro', sguardo=0.0),
]


def _mat(tipo, c, **k):
    return material('M27p_%s_%02x%02x%02x' % (tipo, int(min(1, c[0]) * 255), int(min(1, c[1]) * 255), int(min(1, c[2]) * 255)), c, **k)


def _scuro(c, f=0.72):
    return (c[0] * f, c[1] * f, c[2] * f)


# ------------------------------------------------------------------------- un pezzo = una mesh con piu' materiali
class Pezzo:
    """Costruisce una mesh sola mettendo insieme sfere, capsule, coni, scatole e solidi di rotazione. k = scala di tutto il pezzo."""

    def __init__(self, k=1.0):
        self.bm = bmesh.new(); self.mats = []; self.k = k

    def _mi(self, mat):
        if mat not in self.mats:
            self.mats.append(mat)
        return self.mats.index(mat)

    def _nuove(self, verts, mat, liscio=True):
        mi = self._mi(mat)
        for f in {f for v in verts for f in v.link_faces}:
            f.material_index = mi; f.smooth = liscio

    def sfera(self, c, r, mat, rot=None, u=12, v=8):
        k = self.k; r = (r, r, r) if isinstance(r, (int, float)) else r
        M = Matrix.Translation(Vector(c) * k) @ (Euler(rot).to_matrix().to_4x4() if rot else Matrix.Identity(4)) @ Matrix.Diagonal((r[0] * k, r[1] * k, r[2] * k, 1.0))
        self._nuove(bmesh.ops.create_uvsphere(self.bm, u_segments=u, v_segments=v, radius=1.0, matrix=M)['verts'], mat)

    def scatola(self, c, s, mat, rot=None):
        k = self.k
        M = Matrix.Translation(Vector(c) * k) @ (Euler(rot).to_matrix().to_4x4() if rot else Matrix.Identity(4)) @ Matrix.Diagonal((s[0] * k, s[1] * k, s[2] * k, 1.0))
        self._nuove(bmesh.ops.create_cube(self.bm, size=1.0, matrix=M)['verts'], mat, liscio=False)

    def tornio(self, a, b, profilo, mat, u=12, sxy=(1.0, 1.0)):
        """Solido di rotazione attorno all'asse a -> b. profilo = [(t, r), ...]: t = distanza da a lungo l'asse, r = raggio
        (r = 0 chiude con un polo). Un profilo chiuso (ultimo punto = primo) fa un anello."""
        k = self.k; a = Vector(a) * k; b = Vector(b) * k; asse = (b - a).normalized(); q = Vector((0, 0, 1)).rotation_difference(asse)
        anelli = []
        for (t, r) in profilo:
            t *= k; r *= k
            if r <= 1e-9:
                anelli.append([self.bm.verts.new(a + asse * t)])
            else:
                anelli.append([self.bm.verts.new(a + q @ Vector((math.cos(2 * PI * i / u) * r * sxy[0], math.sin(2 * PI * i / u) * r * sxy[1], t))) for i in range(u)])
        for r0, r1 in zip(anelli, anelli[1:]):
            if len(r0) == 1 and len(r1) == 1:
                continue
            for i in range(u):
                j = (i + 1) % u
                if len(r0) == 1: self.bm.faces.new((r0[0], r1[j], r1[i]))
                elif len(r1) == 1: self.bm.faces.new((r0[i], r0[j], r1[0]))
                else: self.bm.faces.new((r0[i], r0[j], r1[j], r1[i]))
        self._nuove([v for an in anelli for v in an], mat)

    def capsula(self, a, b, r0, r1, mat, u=10, sxy=(1.0, 1.0)):
        L = (Vector(b) - Vector(a)).length
        prof = [(-r0, 0.0), (-r0 * 0.78, r0 * 0.62), (-r0 * 0.38, r0 * 0.925), (0.0, r0), (L, r1), (L + r1 * 0.38, r1 * 0.925), (L + r1 * 0.78, r1 * 0.62), (L + r1, 0.0)]
        self.tornio(a, b, prof, mat, u=u, sxy=sxy)

    def cono(self, a, b, r, mat, u=8):
        L = (Vector(b) - Vector(a)).length
        self.tornio(a, b, [(-r * 0.35, 0.0), (0.0, r), (L * 0.5, r * 0.62), (L * 0.88, r * 0.22), (L, 0.0)], mat, u=u)

    def anello(self, c, verso, R, r, mat, u=14):
        """Anello (toro) di raggio R e spessore r attorno a c, con l'asse lungo «verso»."""
        c = Vector(c); v = Vector(verso).normalized()
        self.tornio(c, c + v, [(-r, R), (0.0, R + r), (r, R), (0.0, R - r), (-r, R)], mat, u=u)

    def sagoma(self, punti, c, mat, scala=1.0):
        """Figura piatta (stella, cuore) rivolta in avanti (-Y), fatta a ventaglio attorno a c."""
        k = self.k; c = Vector(c) * k
        cv = self.bm.verts.new(c); vs = [self.bm.verts.new(c + Vector((x * scala * k, 0.0, z * scala * k))) for (x, z) in punti]
        for i in range(len(vs)):
            self.bm.faces.new((cv, vs[i], vs[(i + 1) % len(vs)]))
        self._nuove([cv] + vs, mat, liscio=False)

    def oggetto(self, nome, parent, coll, loc=(0, 0, 0)):
        bmesh.ops.recalc_face_normals(self.bm, faces=self.bm.faces[:])
        me = bpy.data.meshes.new(nome); self.bm.to_mesh(me); self.bm.free()
        for m in self.mats:
            me.materials.append(m)
        o = bpy.data.objects.new(nome, me); o.parent = parent; o.location = loc; coll.objects.link(o); o.visible_shadow = False
        return o


STELLA = [(math.sin(PI * i / 5) * (1.0 if i % 2 == 0 else 0.42), math.cos(PI * i / 5) * (1.0 if i % 2 == 0 else 0.42)) for i in range(10)]
CUORE = [(16 * math.sin(t) ** 3 / 17.0, (13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)) / 17.0 + 0.15) for t in [2 * PI * i / 18 for i in range(18)]]
BUSTI = dict(
    normale=([(-0.02, 0.0), (0.0, 0.13), (0.06, 0.185), (0.20, 0.215), (0.44, 0.21), (0.60, 0.195), (0.68, 0.14), (0.72, 0.0)], (1.0, 0.80)),
    magro=([(-0.02, 0.0), (0.0, 0.12), (0.06, 0.165), (0.20, 0.185), (0.44, 0.185), (0.60, 0.18), (0.68, 0.13), (0.72, 0.0)], (1.0, 0.78)),
    tondo=([(-0.03, 0.0), (0.0, 0.16), (0.07, 0.24), (0.22, 0.29), (0.40, 0.28), (0.58, 0.215), (0.68, 0.145), (0.72, 0.0)], (1.0, 0.94)),
)


def _raggio(prof, t):
    for (t0, r0), (t1, r1) in zip(prof, prof[1:]):
        if t0 <= t <= t1:
            return r0 + (r1 - r0) * (t - t0) / max(t1 - t0, 1e-9)
    return prof[-1][1]


# ------------------------------------------------------------------------- le parti
def _testa(L, M):
    """Testa (perno head). Restituisce (pezzo testa, pezzo bocca, posizione della bocca)."""
    kt = L.get('testa', 1.0); T = Pezzo(kt); pelle, cap = M['pelle'], M['capelli']; sg = L.get('sguardo', 0.018)
    T.sfera((0, 0, 0.24), (0.27, 0.25, 0.26), pelle, u=18, v=12)
    for s in (-1, 1):
        T.sfera((s * 0.262, 0.012, 0.225), (0.045, 0.032, 0.062), pelle, u=8, v=6)                                   # orecchie
        T.sfera((s * 0.102, -0.212, 0.275), (0.076, 0.036, 0.092), M['bianco'], u=12, v=8)                           # occhi
        T.sfera((s * 0.098, -0.240, 0.270 + sg), (0.043, 0.020, 0.054), M['pupilla'], u=10, v=6)
        T.sfera((s * 0.098 + 0.016, -0.257, 0.292 + sg), (0.013, 0.008, 0.015), M['bianco'], u=6, v=4)               # lucina
        T.capsula((s * 0.158, -0.214, 0.392), (s * 0.052, -0.232, 0.408), 0.013, 0.015, M['sopracciglia'], u=6)
        T.sfera((s * 0.172, -0.176, 0.178), (0.050, 0.022, 0.034), M['guancia'], u=8, v=6)
    T.sfera((0, -0.252, 0.212), (0.040, 0.040, 0.035), M['naso'], u=10, v=6)
    tg = L.get('taglio', 'corto'); calotta = lambda: T.sfera((0, 0.03, 0.305), (0.283, 0.272, 0.222), cap, u=16, v=10)
    def frangia(larga=True):
        for (x, z, rx) in ((-0.115, 0.415, 0.092), (0.0, 0.432, 0.105), (0.115, 0.415, 0.092)) if larga else ((-0.06, 0.425, 0.17),):
            T.sfera((x, -0.19, z), (rx, 0.064, 0.056), cap, u=10, v=6)
    def nuca():
        T.sfera((0, 0.10, 0.21), (0.262, 0.20, 0.16), cap, u=12, v=8)
    if tg == 'corto':
        calotta(); frangia()
    elif tg == 'ciuffi':                                                                                              # punte in su, come Pippo
        calotta()
        for d in ((0, -0.55, 0.83), (-0.45, -0.32, 0.83), (0.45, -0.32, 0.83), (-0.62, 0.18, 0.76), (0.62, 0.18, 0.76), (0, 0.10, 1.0), (-0.32, 0.6, 0.72), (0.32, 0.6, 0.72), (0, 0.85, 0.5),
                  (-0.22, -0.72, 0.62), (0.22, -0.72, 0.62)):
            d = Vector(d).normalized(); base = Vector((0, 0.03, 0.305)) + Vector((d.x * 0.26, d.y * 0.25, d.z * 0.205))
            T.cono(base, base + d * 0.20, 0.085, cap)
    elif tg == 'caschetto':
        T.sfera((0, 0.085, 0.235), (0.305, 0.255, 0.285), cap, u=16, v=10); T.sfera((0, -0.165, 0.405), (0.215, 0.105, 0.075), cap, u=12, v=6)
    elif tg == 'coda':
        calotta(); frangia(False)
        T.sfera((0, 0.275, 0.40), 0.062, M['c2'], u=8, v=6); T.capsula((0, 0.31, 0.40), (0, 0.43, 0.08), 0.080, 0.032, cap)
    elif tg == 'codini':
        calotta(); frangia()
        for s in (-1, 1):
            T.sfera((s * 0.235, 0.10, 0.455), 0.118, cap, u=12, v=8); T.sfera((s * 0.185, 0.085, 0.405), 0.045, M['c2'], u=8, v=6)
    elif tg == 'afro':
        T.sfera((0, 0.06, 0.39), (0.345, 0.315, 0.285), cap, u=18, v=12)
        for a in range(7):
            an = PI * (0.08 + a * 0.14)
            T.sfera((math.cos(an) * 0.30, 0.10, 0.40 + math.sin(an) * 0.24), 0.105, cap, u=8, v=6)
    elif tg == 'ricci':
        calotta(); rr = random.Random(3)
        for a in range(16):
            d = Vector((rr.uniform(-1, 1), rr.uniform(-0.75, 1), rr.uniform(0.1, 1))).normalized()
            T.sfera(Vector((0, 0.03, 0.305)) + Vector((d.x * 0.265, d.y * 0.255, d.z * 0.21)), 0.082, cap, u=8, v=6)
    elif tg == 'lunghi':
        calotta()
        for s in (-1, 1):
            T.sfera((s * 0.105, -0.185, 0.412), (0.125, 0.07, 0.07), cap, u=10, v=6); T.capsula((s * 0.252, 0.02, 0.26), (s * 0.245, -0.01, -0.13), 0.062, 0.040, cap)
        T.sfera((0, 0.165, 0.03), (0.265, 0.12, 0.33), cap, u=14, v=10)
    elif tg == 'pelato':
        T.sfera((0, 0.07, 0.20), (0.274, 0.235, 0.105), cap, u=14, v=8)                                              # la corona di capelli dietro
    elif tg == 'cappellino':
        cc = M['cappello']; vv = L.get('verso_visiera', 1); nuca()
        T.sfera((0, 0.0, 0.315), (0.287, 0.277, 0.215), cc, u=16, v=10)
        T.sfera((0, -0.30 * vv, 0.378), (0.175, 0.16, 0.022), cc, rot=(0.16 * vv, 0, 0), u=12, v=6); T.sfera((0, 0, 0.532), 0.03, M['c2'], u=6, v=4)
    elif tg == 'berretto':
        cc = M['cappello']; nuca()
        T.sfera((0, 0.02, 0.335), (0.292, 0.282, 0.245), cc, u=16, v=10); T.sfera((0, 0.02, 0.37), (0.303, 0.294, 0.062), M['cappello_s'], u=16, v=6); T.sfera((0, 0.02, 0.615), 0.075, M['bianco'], u=8, v=6)
    ex = L.get('extra', ())
    if 'baffi' in ex:
        for s in (-1, 1):
            T.capsula((s * 0.012, -0.262, 0.178), (s * 0.095, -0.238, 0.160), 0.026, 0.014, cap, u=6)
    if 'barba' in ex:
        T.sfera((0, -0.075, -0.012), (0.212, 0.165, 0.098), cap, u=14, v=8)                                          # barba sotto la bocca (la bocca resta scoperta)
        for s in (-1, 1):
            T.capsula((s * 0.010, -0.262, 0.180), (s * 0.090, -0.240, 0.165), 0.022, 0.012, cap, u=6)
    if 'occhiali' in ex or 'occhiali_sole' in ex:
        mo = M['montatura']
        for s in (-1, 1):
            T.anello((s * 0.102, -0.252, 0.275), (0, -1, 0), 0.082, 0.011, mo)
            T.capsula((s * 0.185, -0.235, 0.285), (s * 0.268, 0.0, 0.275), 0.009, 0.009, mo, u=6)
            if 'occhiali_sole' in ex:
                T.sfera((s * 0.102, -0.252, 0.275), (0.080, 0.014, 0.080), M['lente'], u=12, v=6)
        T.capsula((-0.03, -0.262, 0.285), (0.03, -0.262, 0.285), 0.009, 0.009, mo, u=6)
    if 'cuffie' in ex:
        pts = [Vector((0.30 * math.cos(a), 0.02, 0.24 + 0.30 * math.sin(a))) for a in [PI * x / 8 for x in range(9)]]
        for p0, p1 in zip(pts, pts[1:]):
            T.capsula(p0, p1, 0.022, 0.022, M['oro'], u=6)
        for s in (-1, 1):
            T.sfera((s * 0.288, 0.02, 0.235), (0.052, 0.092, 0.105), M['oro'], u=10, v=6)
    B = Pezzo(kt)
    B.sfera((0, 0, 0), (0.085, 0.026, 0.058), M['bocca'], u=12, v=8); B.sfera((0, -0.006, -0.027), (0.050, 0.026, 0.024), M['lingua'], u=8, v=6); B.sfera((0, -0.004, 0.036), (0.066, 0.025, 0.016), M['bianco'], u=8, v=4)
    return T, B, Vector((0, -0.229, 0.122)) * kt


def _busto(L, M):
    """Busto (perno body): maglia, collo, spalle e i dettagli del vestito."""
    prof, sxy = BUSTI[L.get('corpo', 'normale')]; P = Pezzo(); tipo = L.get('tipo', 'maglietta'); mg, c2 = M['maglia'], M['c2']
    yf = lambda z, extra=0.006: -(_raggio(prof, z) * sxy[1] + extra)
    P.tornio((0, 0, 0), (0, 0, 1), prof, mg, u=16, sxy=sxy)
    P.tornio((0, 0, 0.66), (0, 0, 1), [(0.0, 0.078), (0.18, 0.074)], M['pelle'], u=10)                               # collo
    manica = M['pelle'] if tipo == 'canotta' else mg
    for s in (-1, 1):
        P.sfera((s * 0.248, 0, 0.615), (0.092, 0.085, 0.088), manica, u=10, v=6)
    def fascia(z0, z1, mat, piu=0.005):
        P.tornio((0, 0, 0), (0, 0, 1), [(z0, _raggio(prof, z0) + piu), ((z0 + z1) / 2, _raggio(prof, (z0 + z1) / 2) + piu * 1.4), (z1, _raggio(prof, z1) + piu)], mat, u=16, sxy=sxy)
    def vita(mat, z=0.10):
        P.tornio((0, 0, 0), (0, 0, 1), [(-0.025, 0.0), (0.0, _raggio(prof, 0.0) + 0.006), (z * 0.5, _raggio(prof, z * 0.5) + 0.006), (z, _raggio(prof, z) + 0.006)], mat, u=16, sxy=sxy)
    def stemma(z=0.44, r=0.075):
        st = L.get('stemma')
        if st == 'stella': P.sagoma(STELLA, (0, yf(z, 0.012), z), c2, scala=r * 1.15)
        elif st == 'cuore': P.sagoma(CUORE, (0, yf(z, 0.012), z - 0.01), c2, scala=r * 1.05)
        elif st == 'cerchio': P.sfera((0, yf(z, -0.004), z), (r, 0.016, r), c2, u=12, v=6)
    def colletto(mat):
        P.anello((0, 0, 0.705), (0, 0, 1), 0.098, 0.022, mat, u=12)
    def gonna(z0, z1, r1, mat):
        P.tornio((0, 0, 0), (0, 0, 1), [(z1, r1 * 0.985), (z1 + 0.012, r1), (z0, _raggio(prof, z0) + 0.008), (z0 + 0.03, _raggio(prof, z0 + 0.03) + 0.004)], mat, u=16, sxy=(1.0, max(sxy[1], 0.88)))
    if tipo == 'maglietta':
        vita(M['panta']); colletto(M['maglia_s']); stemma()
    elif tipo == 'righe':
        vita(M['panta']); colletto(c2); fascia(0.20, 0.27, c2); fascia(0.36, 0.43, c2); fascia(0.52, 0.58, c2)
    elif tipo == 'canotta':
        vita(M['panta']); colletto(c2); fascia(0.34, 0.42, c2)
    elif tipo == 'felpa':
        vita(M['panta'], 0.06); fascia(0.06, 0.11, c2)
        P.sfera((0, 0.135, 0.70), (0.185, 0.115, 0.115), c2, u=12, v=8)                                              # cappuccio
        P.sfera((0, yf(0.24, -0.004), 0.24), (0.125, 0.03, 0.062), c2, u=10, v=6)                                    # tascone
        for s in (-1, 1):
            P.capsula((s * 0.035, yf(0.62, 0.004), 0.64), (s * 0.045, yf(0.50, 0.008), 0.50), 0.008, 0.008, M['bianco'], u=6)
    elif tipo == 'giacca':
        vita(M['panta']); P.sfera((0, yf(0.38, -0.012), 0.38), (0.082, 0.03, 0.27), c2, u=10, v=8)                   # la maglia sotto
        for s in (-1, 1):
            P.sfera((s * 0.075, yf(0.62, -0.002), 0.635), (0.06, 0.025, 0.085), M['maglia_s'], rot=(0, s * 0.5, 0), u=8, v=6)
    elif tipo == 'salopette':
        vita(M['panta'], 0.26); P.scatola((0, yf(0.38, 0.0), 0.37), (0.20, 0.03, 0.20), M['panta'])
        for s in (-1, 1):
            P.capsula((s * 0.075, yf(0.46, 0.004), 0.46), (s * 0.10, yf(0.66, 0.008) + 0.03, 0.69), 0.02, 0.02, M['panta'], u=6)
            P.sfera((s * 0.075, yf(0.45, 0.012), 0.45), (0.022, 0.012, 0.022), M['oro'], u=6, v=4)
    elif tipo == 'vestito':
        gonna(0.22, -0.20, 0.335, mg); fascia(0.20, 0.26, c2); colletto(c2)
        if 'collana' in L.get('extra', ()):
            for a in range(9):
                an = PI * (1.12 + a * 0.095)
                P.sfera((math.cos(an) * 0.115, math.sin(an) * 0.115 * 0.8 - 0.02, 0.665 - 0.03 * math.sin(PI * a / 8)), 0.02, M['bianco'], u=6, v=4)
    elif tipo == 'divisa':                                                                                            # il corpo di ballo: bianco e oro
        vita(M['panta'], 0.08); fascia(0.08, 0.135, c2, 0.008); colletto(c2); stemma(0.42, 0.085)
        for s in (-1, 1):
            P.sfera((s * 0.262, 0, 0.675), (0.085, 0.07, 0.035), c2, u=10, v=6)                                      # spalline
    if L.get('gambe') == 'gonna':
        gonna(0.11, -0.17, 0.30, M['panta'])
    return P


def _braccio(L, M, lato):
    """Braccio (perno shoulder), steso in giu'. lato = 'L' o 'R': gli oggetti in mano stanno nella mano sinistra (quella libera)."""
    P = Pezzo(); tipo = L.get('tipo', 'maglietta'); pelle, mg = M['pelle'], M['maglia']
    if tipo in ('felpa', 'giacca', 'divisa'):
        P.capsula((0, 0, 0), (0, 0, -0.455), 0.070, 0.060, mg); P.capsula((0, 0, -0.425), (0, 0, -0.468), 0.066, 0.066, M['c2'], u=10)
    elif tipo == 'canotta':
        P.capsula((0, 0, 0), (0, 0, -0.47), 0.062, 0.050, pelle)
    else:
        P.capsula((0, 0, 0), (0, 0, -0.205), 0.073, 0.070, mg); P.capsula((0, 0, -0.17), (0, 0, -0.47), 0.058, 0.050, pelle)
    P.sfera((0, 0, -0.545), (0.070, 0.066, 0.082), pelle, u=10, v=8); P.sfera((0, -0.058, -0.52), 0.028, pelle, u=6, v=4)
    ex = L.get('extra', ())
    if lato == 'L' and 'telefono' in ex:
        P.scatola((0, -0.012, -0.70), (0.108, 0.018, 0.195), M['nero']); P.scatola((0, -0.012, -0.70), (0.092, 0.022, 0.170), M['schermo'])
    if lato == 'L' and 'luce' in ex:
        P.capsula((0, 0, -0.53), (0, 0, -0.62), 0.028, 0.028, M['nero'], u=6); P.capsula((0, 0, -0.63), (0, 0, -0.98), 0.024, 0.024, M['luce'], u=8)
    if lato == 'R' and tipo in ('maglietta', 'righe', 'canotta') and L.get('corpo') != 'tondo':
        P.capsula((0, 0, -0.445), (0, 0, -0.462), 0.056, 0.056, M['oro'], u=8)                                       # braccialetto
    return P


def _gamba(L, M):
    """Gamba (perno hip), stesa in giu' fino alla caviglia (-0.62)."""
    P = Pezzo(); g = L.get('gambe', 'lunghi'); pelle, pt = M['pelle'], M['panta']
    if g == 'lunghi':
        P.capsula((0, 0, -0.02), (0, 0, -0.57), 0.100, 0.075, pt)
    elif g == 'stivali':
        P.capsula((0, 0, -0.02), (0, 0, -0.57), 0.098, 0.072, pt); P.capsula((0, 0, -0.38), (0, 0, -0.57), 0.086, 0.080, M['scarpe'])
    elif g == 'corti':
        P.capsula((0, 0, -0.02), (0, 0, -0.24), 0.105, 0.100, pt); P.capsula((0, 0, -0.20), (0, 0, -0.57), 0.072, 0.058, pelle); P.capsula((0, 0, -0.49), (0, 0, -0.57), 0.064, 0.064, M['bianco'])
    else:                                                                                                             # nude (sotto il vestito) o gonna
        P.capsula((0, 0, -0.02), (0, 0, -0.57), 0.078, 0.058, pelle)
        if g == 'gonna':
            P.capsula((0, 0, -0.47), (0, 0, -0.57), 0.064, 0.064, M['bianco'])
    return P


def _piede(L, M):
    P = Pezzo()
    P.sfera((0, -0.045, -0.02), (0.092, 0.160, 0.062), M['scarpe'], u=12, v=8); P.sfera((0, -0.045, -0.054), (0.099, 0.168, 0.030), M['suola'], u=12, v=6)
    return P


def materiali(L):
    pelle = L['pelle']; cap = L['capelli']; mg = L.get('maglia', BIANCO); c2 = L.get('c2', BIANCO); cl = L.get('c_luce', (1.0, 0.8, 0.3)); cc = L.get('c_cappello', mg)
    guancia = tuple(pelle[i] * 0.55 + (1.0, 0.36, 0.38)[i] * 0.45 for i in range(3))
    oro = material('M27p_oro', ORO, rough=0.28, metallic=0.85, emit=(1.0, 0.62, 0.12), emit_strength=0.25)
    return dict(
        pelle=_mat('pelle', pelle, rough=0.55), naso=_mat('pelle', _scuro(pelle, 0.88), rough=0.55), guancia=_mat('guancia', guancia, rough=0.6),
        capelli=_mat('capelli', cap, rough=0.45), sopracciglia=_mat('capelli', _scuro(cap, 0.55) if sum(cap) > 0.4 else (0.02, 0.02, 0.02), rough=0.6),
        bianco=_mat('bianco', (0.96, 0.96, 0.96), rough=0.35), pupilla=material('M27p_pupilla', (0.015, 0.012, 0.012), rough=0.15),
        bocca=material('M27p_bocca', (0.16, 0.015, 0.03), rough=0.5), lingua=material('M27p_lingua', (0.95, 0.35, 0.40), rough=0.45),
        maglia=(oro if mg == ORO else _mat('stoffa', mg, rough=0.8)), maglia_s=_mat('stoffa', _scuro(mg), rough=0.8), c2=(oro if c2 == ORO else _mat('stoffa', c2, rough=0.7)),
        panta=_mat('stoffa', L.get('panta', JEANS), rough=0.85), scarpe=(oro if L.get('scarpe') == ORO else _mat('scarpe', L.get('scarpe', BIANCO), rough=0.5)),
        suola=_mat('scarpe', (0.92, 0.92, 0.92) if sum(L.get('scarpe', BIANCO)) < 2.4 else (0.25, 0.25, 0.28), rough=0.6),
        cappello=_mat('stoffa', cc, rough=0.7), cappello_s=_mat('stoffa', _scuro(cc, 1.25), rough=0.7), oro=oro,
        montatura=material('M27p_montatura', (0.03, 0.03, 0.04), rough=0.3), lente=material('M27p_lente', (0.02, 0.02, 0.03), rough=0.08, coat=1.0),
        nero=material('M27p_nero', (0.02, 0.02, 0.025), rough=0.35),
        schermo=material('M27p_schermo', (0.7, 0.85, 1.0), rough=0.3, emit=(0.65, 0.85, 1.0), emit_strength=5.0),
        luce=material('M27p_luce_%02x%02x%02x' % tuple(int(min(1, x) * 255) for x in cl), cl, rough=0.4, emit=cl, emit_strength=7.0),
    )


def pupazzo(nome, look):
    """Costruisce una persona in una collezione sua, NON collegata alla scena (serve solo come modello per le istanze).
    look = un dizionario di LOOK_FOLLA o LOOK_BALLO. Restituisce (collezione, R) con R = perni come quelli di Pippo, piu' 'bocca'."""
    col = bpy.data.collections.new(nome); M = materiali(look)
    E = lambda n, loc, par: empty(n, loc, par, col)
    root = E(nome + '_Root', (0, 0, 0), None); body = E(nome + '_Body', (0, 0, 0.70), root); head = E(nome + '_Head', (0, 0, 0.80), body)
    T, B, pb = _testa(look, M)
    T.oggetto('G_Testa', head, col); bocca = B.oggetto('G_Bocca', head, col, loc=pb)
    _busto(look, M).oggetto('G_Busto', body, col)
    R = dict(root=root, body=body, head=head, bocca=bocca)
    for s_, nm in ((-1, 'L'), (1, 'R')):
        sh = E(nome + '_Shoulder' + nm, (s_ * 0.30, 0, 0.62), body); _braccio(look, M, nm).oggetto('G_Braccio' + nm, sh, col)
        hp = E(nome + '_Hip' + nm, (s_ * 0.115, 0, 0.70), root); _gamba(look, M).oggetto('G_Gamba' + nm, hp, col)
        ft = E(nome + '_Foot' + nm, (0, 0, -0.62), hp); _piede(look, M).oggetto('G_Piede' + nm, ft, col)
        R['shoulder' + nm] = sh; R['hip' + nm] = hp; R['foot' + nm] = ft
    return col, R


def canta(R, nf, fps, quanto, f0=1):
    """Apre e chiude la bocca: quanto(t) -> 0 (sorriso chiuso) .. 1 (bocca spalancata)."""
    b = R['bocca']; prima = None
    for k in range(nf):
        a = max(0.0, min(1.0, quanto(k / fps))); v = (round(1.14 - 0.24 * a, 3), 1.0, round(0.20 + 0.95 * a, 3))
        if v != prima or k == nf - 1:
            if prima is not None and k and v != prima:
                b.scale = prima; b.keyframe_insert('scale', frame=f0 + k - 1)
            b.scale = v; b.keyframe_insert('scale', frame=f0 + k); prima = v


def copia(coll, col_pupazzo, x, y, z=0.0, verso=0.0, altezza=0.072, nome='Gente'):
    """Una persona: istanza della collezione del pupazzo, alta «altezza», girata di «verso» (0 = guarda verso -Y)."""
    o = bpy.data.objects.new(nome, None); o.instance_type = 'COLLECTION'; o.instance_collection = col_pupazzo
    o.empty_display_size = 0.01; k = altezza / ALTEZZA
    o.location = (x, y, z); o.rotation_euler = (0, 0, verso); o.scale = (k, k, k); coll.objects.link(o)
    return o


def specchia_seq(seq):
    """Specchia una sequenza gia' passata da mocap_pippo.sequenza(): chi sta di fronte a Pippo lo imita come in uno specchio."""
    def mv(v): return Vector((-v.x, v.y, v.z))
    def mq(q): return Quaternion((q.w, q.x, -q.y, -q.z))
    out = []
    for s in seq:
        out.append(dict(loc=(-s['loc'][0], s['loc'][1], s['loc'][2]), yaw=-s['yaw'], qb=mq(s['qb']), qt=mq(s['qt']), kb=s.get('kb'),
                        gambe={'L': mv(s['gambe']['R']), 'R': mv(s['gambe']['L'])}, braccia={'L': mv(s['braccia']['R']), 'R': mv(s['braccia']['L'])},
                        piede='L' if s['piede'] == 'R' else 'R', volo=s['volo']))
    return out
