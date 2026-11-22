"""Porta su Pippo i movimenti registrati (BVH del database CMU, in assets/mocap/cmu/: vedi assets/mocap/LEGGIMI.md).

Pippo non ha gomiti ne' ginocchia: braccia e gambe sono pezzi rigidi. Quindi non si copiano le rotazioni delle ossa ma
le DIREZIONI (spalla -> polso, anca -> caviglia), piu' l'inclinazione di busto e testa e la direzione del corpo.
La posizione non si copia: si ricava dal piede d'appoggio, che resta fermo a terra finche' regge il peso (niente
scivolamento per costruzione); nei salti si aggiunge l'altezza vera dei piedi. Non tocca pippo.py.

Uso tipico:
    seq = sequenza([cammino(8, 0.5), clip('05_02', durata=8.0), clip('16_01')], fps=24)
    applica(R, seq, f0=1)            # R = pippo2.build_pippo(); mette le chiavi a ogni fotogramma
"""
import math
import os
import numpy as np
import bpy  # noqa: serve a caricare mathutils
from mathutils import Vector, Matrix, Quaternion

QUI = os.path.dirname(os.path.abspath(__file__))
CMU = os.path.join(QUI, '..', 'assets', 'mocap', 'cmu')
A4 = Matrix(((1, 0, 0, 0), (0, 0, -1, 0), (0, 1, 0, 0), (0, 0, 0, 1)))        # BVH (Y in alto, guarda +Z) -> Blender (Z in alto, guarda -Y)
A4I = A4.inverted()
GIU = Vector((0, 0, -1))
# misure di Pippo (pippo.py): anche, lunghezza anca -> suola. Il lato 'R' di Pippo e' a +X, cioe' la SINISTRA anatomica.
ANCA = {'R': Vector((0.12, 0, 0.70)), 'L': Vector((-0.12, 0, 0.70))}
GAMBA = 0.70
LATI = (('R', 'Left'), ('L', 'Right'))                                          # (lato di Pippo, lato del mocap)
_cache = {}


class Bvh:
    def __init__(self, path):
        tok = open(path).read().split()
        self.names, self.parent, self.offset, self.chan = [], [], [], []
        i = 0; stack = []; cur = -1
        while tok[i] != 'MOTION':
            t = tok[i]
            if t in ('ROOT', 'JOINT'):
                self.names.append(tok[i + 1]); self.parent.append(stack[-1] if stack else -1); self.offset.append(None); self.chan.append([])
                cur = len(self.names) - 1; i += 2
            elif t == 'End':
                cur = -2; i += 2
            elif t == '{':
                stack.append(cur); i += 1
            elif t == '}':
                stack.pop(); i += 1
            elif t == 'OFFSET':
                j = stack[-1]
                if j >= 0 and self.offset[j] is None:
                    self.offset[j] = tuple(float(x) for x in tok[i + 1:i + 4])
                i += 4
            elif t == 'CHANNELS':
                k = int(tok[i + 1]); self.chan[stack[-1]] = tok[i + 2:i + 2 + k]; i += 2 + k
            else:
                i += 1
        i += 1
        self.n = int(tok[i + 1]); self.dt = float(tok[i + 4])
        self.data = np.array(tok[i + 5:], dtype=float).reshape(self.n, -1)
        self._f = {}

    def frame(self, f):
        """Matrici mondo (coordinate di Blender) delle giunture al fotogramma f."""
        f = int(min(max(f, 0), self.n - 1))
        if f in self._f:
            return self._f[f]
        row = self.data[f]; c = 0; W = []
        for j in range(len(self.names)):
            T = Matrix.Translation(self.offset[j]); Rm = Matrix.Identity(4)
            for ch in self.chan[j]:
                v = row[c]; c += 1
                if ch == 'Xposition': T[0][3] = v
                elif ch == 'Yposition': T[1][3] = v
                elif ch == 'Zposition': T[2][3] = v
                else: Rm = Rm @ Matrix.Rotation(math.radians(v), 4, ch[0])
            M = T @ Rm
            W.append(M if self.parent[j] < 0 else W[self.parent[j]] @ M)
        out = {nm: A4 @ W[j] @ A4I for j, nm in enumerate(self.names)}
        self._f[f] = out
        return out


def bvh(nome):
    """nome = nome del file in assets/mocap/cmu (senza .bvh) oppure percorso completo di un .bvh."""
    if nome not in _cache:
        b = Bvh(nome if os.path.isfile(nome) else os.path.join(CMU, nome + '.bvh'))
        W = b.frame(0)                                                           # scala: gamba del mocap -> gamba di Pippo
        b.gamba = sum((W[a].to_translation() - W[c].to_translation()).length for a, c in (('LeftUpLeg', 'LeftLeg'), ('LeftLeg', 'LeftFoot')))
        b.s = GAMBA / (b.gamba * 1.12)                                           # 1.12: caviglia -> suola
        zs = [min(b.frame(f)['LeftFoot'].to_translation().z, b.frame(f)['RightFoot'].to_translation().z) for f in range(0, b.n, 4)]
        b.z0 = float(np.percentile(zs, 5))                                       # altezza della caviglia quando il piede e' a terra
        P = {k: m.to_translation() for k, m in W.items()}                        # il primo fotogramma dei file cgspeed e' una posa a T: va saltato
        tp = [(P[l + 'Hand'] - P[l + 'Arm']).normalized() for l in ('Left', 'Right')]
        b.primo = 1 if all(abs(v.z) < 0.25 and abs(v.x) > 0.9 for v in tp) else 0
        _cache[nome] = b
    return _cache[nome]


def _posa(b, f):
    """Quello che serve di un fotogramma del mocap, in coordinate di Blender."""
    W = b.frame(f); P = {k: m.to_translation() for k, m in W.items()}
    Rh = W['Hips'].to_3x3(); fw = Rh @ Vector((0, -1, 0))
    yaw = math.atan2(fw.x, -fw.y)
    Rz = Matrix.Rotation(yaw, 3, 'Z'); inv = Rz.transposed()
    Rb = inv @ W['Spine1'].to_3x3()                                             # busto rispetto alla direzione del corpo
    Rt = W['Spine1'].to_3x3().transposed() @ W['Head'].to_3x3()                 # testa rispetto al busto
    p = dict(yaw=yaw, yaw0=yaw, qb=Rb.to_quaternion(), qt=Rt.to_quaternion(), hips=P['Hips'].copy(), gambe={}, braccia={}, h={}, kb=None)
    Rbw = W['Spine1'].to_3x3()
    for lp, lm in LATI:
        p['gambe'][lp] = (inv @ (P[lm + 'Foot'] - P[lm + 'UpLeg'])).normalized()
        p['braccia'][lp] = (Rbw.transposed() @ (P[lm + 'Hand'] - P[lm + 'Arm'])).normalized()
        p['h'][lp] = max(0.0, (P[lm + 'Foot'].z - b.z0) * b.s)
    p['s'] = b.s
    return p


def sm_(x):
    x = min(1.0, max(0.0, x)); return x * x * (3 - 2 * x)


def _mix(a, c, w):
    """Miscela due pose (w = 0 -> a, 1 -> c)."""
    if w <= 0: return a
    if w >= 1: return c
    dy = (c['yaw'] - a['yaw'] + math.pi) % (2 * math.pi) - math.pi
    dy0 = (c['yaw0'] - a['yaw0'] + math.pi) % (2 * math.pi) - math.pi
    ka, kc = a.get('kb'), c.get('kb')
    kb = None if (ka is None and kc is None) else (0.85 if ka is None else ka) * (1 - w) + (0.85 if kc is None else kc) * w
    return dict(yaw=a['yaw'] + dy * w, yaw0=a['yaw0'] + dy0 * w, qb=a['qb'].slerp(c['qb'], w), qt=a['qt'].slerp(c['qt'], w), hips=a['hips'].lerp(c['hips'], w), s=c['s'], kb=kb,
                gambe={k: a['gambe'][k].lerp(c['gambe'][k], w).normalized() for k in 'LR'},
                braccia={k: a['braccia'][k].lerp(c['braccia'][k], w).normalized() for k in 'LR'},
                h={k: a['h'][k] * (1 - w) + c['h'][k] * w for k in 'LR'})


def _srotola(pose):
    """Rende continua la direzione del corpo lungo il pezzo (niente salti di 360 gradi)."""
    for i in range(1, len(pose)):
        d = (pose[i]['yaw'] - pose[i - 1]['yaw'] + math.pi) % (2 * math.pi) - math.pi
        pose[i]['yaw'] = pose[i - 1]['yaw'] + d
    return pose


def clip(nome, f0=None, f1=None, durata=None, fps=24, busto=None, specchio=False, t0=None, t1=None):
    """Un pezzo di registrazione, stirato o stretto per durare «durata» secondi.
    f0..f1 = fotogrammi del file; in alternativa t0..t1 in secondi. La posa a T iniziale viene saltata.
    busto = quanto dell'inclinazione del busto passa a Pippo (0..1; None = quello di applica). specchio = scambia destra e sinistra."""
    b = bvh(nome)
    if t0 is not None: f0 = int(round(t0 / b.dt))
    if t1 is not None: f1 = int(round(t1 / b.dt))
    f0 = b.primo if not f0 else max(f0, b.primo); f1 = b.n - 1 if f1 is None else min(f1, b.n - 1)
    dur = (f1 - f0) * b.dt if durata is None else durata
    n = max(2, int(round(dur * fps)))
    out = [dict(_posa(b, f0 + (f1 - f0) * k / (n - 1))) for k in range(n)]
    for p in out: p['kb'] = busto
    out = _srotola(out)
    return specchia(out) if specchio else out


def specchia(pose):
    """Scambia destra e sinistra (riflessione rispetto al piano che taglia Pippo a meta')."""
    def mv(v): return Vector((-v.x, v.y, v.z))
    def mq(q): return Quaternion((q.w, q.x, -q.y, -q.z))
    out = []
    for p in pose:
        out.append(dict(yaw=-p['yaw'], yaw0=-p['yaw0'], qb=mq(p['qb']), qt=mq(p['qt']), hips=mv(p['hips']), s=p['s'], kb=p.get('kb'),
                        gambe={'L': mv(p['gambe']['R']), 'R': mv(p['gambe']['L'])}, braccia={'L': mv(p['braccia']['R']), 'R': mv(p['braccia']['L'])},
                        h={'L': p['h']['R'], 'R': p['h']['L']}))
    return out


def durata_naturale(nome, t0=None, t1=None):
    b = bvh(nome); a = (t0 or 0.0); c = (b.n - 1) * b.dt if t1 is None else t1
    return c - a


def _passi(b):
    """Fotogrammi in cui cambia il piede d'appoggio nella camminata."""
    out = []; prev = None
    for f in range(b.n):
        p = _posa(b, f); s = 'R' if p['h']['R'] < p['h']['L'] else 'L'
        if prev and s != prev and (not out or f - out[-1] > 20):
            out.append(f)
        prev = s
    return out


def cammino(passi, durata_passo, fps=24, nome='02_01', n=None, fase=0.0):
    """Camminata in avanti, un passo ogni «durata_passo» secondi (per andare a tempo), in ciclo continuo.
    Dura «passi» passi oppure esattamente n fotogrammi. Un piede tocca terra quando (t / durata_passo + fase) e' un numero intero:
    con fase = 1 - t1 / durata_passo il primo appoggio cade all'istante t1."""
    b = bvh(nome); sw = _passi(b)
    a, c = sw[1], sw[3]                                                          # un ciclo intero = due passi
    y0 = sum(_posa(b, f)['yaw'] for f in range(a, c)) / (c - a)
    n = int(round(passi * durata_passo * fps)) if n is None else n; out = []
    for k in range(n):
        ph = ((k / fps / durata_passo + fase) / 2) % 1.0
        p = _posa(b, a + ph * (c - a))
        if ph > 0.88:                                                            # cucitura del ciclo
            p = _mix(p, _posa(b, a), (ph - 0.88) / 0.12)
        p = dict(p); p['yaw'] = ((p['yaw'] - y0 + math.pi) % (2 * math.pi) - math.pi) * 0.6
        out.append(p)
    return out


def pezzo(pose, verso=None, verso_fine=None, fusione=None):
    """Un pezzo con le sue opzioni per sequenza(). verso = direzione del corpo all'inizio del pezzo (radianti, 0 = quella di partenza
    della sequenza; None = continua da dove era arrivato). verso_fine = direzione in cui deve finire (aggiunge una deriva lineare,
    scegliendo il giro piu' corto). fusione = secondi di miscela con il pezzo prima."""
    return dict(pose=pose, verso=verso, verso_fine=verso_fine, fusione=fusione)


def sequenza(pezzi, fps=24, fusione=0.25, alza=1.0):
    """Mette in fila i pezzi (liste di pose, oppure pezzo(...)) fondendo l'inizio di ognuno con la fine del precedente,
    poi calcola la posizione della radice dal piede d'appoggio. Restituisce una lista di fotogrammi pronti per applica()."""
    pose = []; y_inizio = None
    for pz in pezzi:
        opt = pz if isinstance(pz, dict) else dict(pose=pz, verso=None, verso_fine=None, fusione=None)
        pz = _srotola([dict(p) for p in opt['pose']])
        nb = max(1, int((fusione if opt.get('fusione') is None else opt['fusione']) * fps))
        if y_inizio is None: y_inizio = pz[0]['yaw']
        if opt.get('verso') is not None: dy = (y_inizio + opt['verso']) - pz[0]['yaw']
        elif pose: dy = pose[-1]['yaw'] - pz[0]['yaw']                          # continua nella direzione in cui era arrivato
        else: dy = 0.0
        for p in pz: p['yaw'] += dy
        if opt.get('verso_fine') is not None and len(pz) > 1:
            dd = ((y_inizio + opt['verso_fine']) - pz[-1]['yaw'] + math.pi) % (2 * math.pi) - math.pi
            for k, p in enumerate(pz): p['yaw'] += dd * sm_(k / (len(pz) - 1))
        if pose:
            ult = pose[-1]
            for k in range(min(nb, len(pz))):
                pz[k] = _mix(ult, pz[k], (k + 1) / (nb + 1))
        pose += pz
    pose = _srotola(pose)
    y00 = pose[0]['yaw']
    out = []; xy = Vector((0, 0)); piede = None; pianta = None; prev = None
    for p in pose:
        yaw = p['yaw'] - y00; Rz = Matrix.Rotation(yaw, 3, 'Z')
        F = {k: ANCA[k] + GAMBA * p['gambe'][k] for k in 'LR'}                   # suole nel sistema della radice
        hmin = min(p['h'].values()); volo = hmin > 0.05
        if piede is None:
            piede = 'R' if p['h']['R'] <= p['h']['L'] else 'L'; pianta = xy + (Rz @ F[piede]).xy
        altro = 'L' if piede == 'R' else 'R'
        if volo:
            if prev:                                                             # in volo: segue i fianchi del mocap (in scala, girati come la sequenza)
                d = (p['hips'] - prev['hips']) * p['s']; r = Matrix.Rotation(yaw - p['yaw0'], 3, 'Z') @ Vector((d.x, d.y, 0)); xy = xy + r.xy
            pianta = None
        else:
            if pianta is None:                                                   # atterraggio: si pianta il piede piu' basso
                piede = 'R' if p['h']['R'] <= p['h']['L'] else 'L'; pianta = xy + (Rz @ F[piede]).xy
            elif p['h'][altro] + 0.012 < p['h'][piede]:                          # cambio del piede d'appoggio
                xy = pianta - (Rz @ F[piede]).xy
                piede = altro; pianta = xy + (Rz @ F[piede]).xy
            xy = pianta - (Rz @ F[piede]).xy
        z = -min(F['L'].z, F['R'].z) + max(0.0, hmin - 0.03) * alza
        out.append(dict(loc=(xy.x, xy.y, z), yaw=yaw, qb=p['qb'], qt=p['qt'], gambe=p['gambe'], braccia=p['braccia'], piede=piede, volo=volo, kb=p.get('kb')))
        prev = p
    k = 1
    while k < len(out):                                                          # i salti: arco da lancio tra lo stacco e l'atterraggio (niente scatti)
        if out[k]['volo'] and not out[k - 1]['volo']:
            j = k
            while j < len(out) and out[j]['volo']: j += 1
            if j < len(out) and j - k >= 3:
                a = Vector(out[k - 1]['loc']); c = Vector(out[j]['loc']); n = j - k
                H = max(0.0, max(out[q]['loc'][2] - (a.z + (c.z - a.z) * (q - k + 1) / (n + 1)) for q in range(k, j)))
                H = min(H, GRAVITA * ((n + 1) / fps) ** 2 / 8.0)                    # non piu' alto di quanto permette la durata del volo
                for q in range(k, j):
                    u = (q - k + 1) / (n + 1); pq = a.lerp(c, u)
                    out[q]['loc'] = (pq.x, pq.y, pq.z + 4 * H * u * (1 - u))
            k = j
        else:
            k += 1
    return out


def _q_da(d):
    return GIU.rotation_difference(Vector(d).normalized())


GRAVITA = 13.0                                                               # «gravita'» da cartone per l'altezza dei salti (unita' al secondo quadrato)
SPALLA = {'R': Vector((0.31, 0, 0.65)), 'L': Vector((-0.31, 0, 0.65))}           # spalle nel sistema del busto (perno a z 0.70)
BRACCIO = 0.51


def _libera(d, lato):
    """Sposta la direzione del braccio quel tanto che basta perche' il polso non entri nel busto o nella testa."""
    sp = SPALLA[lato]; d = Vector(d).normalized()
    for _ in range(3):
        w = sp + BRACCIO * d
        if -0.15 < w.z < 0.70:                                                    # busto: cilindro di raggio 0.27 (+ la mano)
            r = math.hypot(w.x, w.y)
            if r < 0.37:
                if r < 1e-4: w.x, w.y = sp.x * 0.3, -0.35
                else: w.x *= 0.37 / r; w.y *= 0.37 / r
        v = w - Vector((0, 0, 1.07))                                              # testa: sfera di raggio 0.36 (+ la mano)
        if v.length < 0.47: w = Vector((0, 0, 1.07)) + v.normalized() * 0.47
        d = (w - sp).normalized()
    return d


def cinematica(seq, posto=(0, 0, 0), giro=0.0, braccio_mic=None, braccio_libero=None, busto=0.85, testa=0.7, scala=None, passo_max=0.75):
    """Calcola, senza toccare Blender, tutto quello che serve di ogni fotogramma: posizione e direzione nel mondo, rotazioni di
    busto e testa, direzioni finali delle braccia (con i gesti e senza entrare nel corpo) e le posizioni nel mondo di suole e polsi.
    braccio_mic(k) / braccio_libero(k) -> (direzione, peso) per il braccio a +X ('R') e per l'altro ('L'), nel sistema del busto.
    scala(k) -> (sx, sy, sz) della radice. Scrive in ogni fotogramma: mondo, yaw_m, scala, qb_, qt_, bracci, suole, polsi, testa_m."""
    G = Matrix.Rotation(giro, 3, 'Z'); idq = Quaternion(); extra = {'R': braccio_mic, 'L': braccio_libero}
    for k, s in enumerate(seq):
        v = G @ Vector(s['loc']); base = Vector((posto[0] + v.x, posto[1] + v.y, posto[2] + v.z))
        sc = Vector(scala(k)) if scala else Vector((1, 1, 1)); kb_ = busto if s.get('kb') is None else s['kb']
        qb = idq.slerp(s['qb'], kb_); qt = idq.slerp(s['qt'], testa)
        Rz = Matrix.Rotation(giro + s['yaw'], 3, 'Z'); Mb = qb.to_matrix(); S3 = Matrix.Diagonal(sc)
        s['mondo'] = base; s['yaw_m'] = giro + s['yaw']; s['scala'] = sc; s['qb_'] = qb; s['qt_'] = qt
        s['suole'] = {}; s['polsi'] = {}; s['bracci'] = {}
        s['testa_m'] = base + Rz @ (S3 @ (Vector((0, 0, 0.70)) + Mb @ Vector((0, 0, 1.07))))
        for lp in 'LR':
            s['suole'][lp] = base + Rz @ (S3 @ (ANCA[lp] + GAMBA * s['gambe'][lp]))
            d = Vector(s['braccia'][lp])
            if extra[lp]:
                dm, w = extra[lp](k)
                if w > 0: d = d.lerp(Vector(dm).normalized(), w).normalized()
            d = _libera(d, lp)
            if k and passo_max:                                                  # non piu' di «passo_max» radianti per fotogramma
                pr = seq[k - 1]['bracci'][lp]; an = pr.angle(d)
                if an > passo_max: d = pr.slerp(d, passo_max / an).normalized()
            s['bracci'][lp] = d
            s['polsi'][lp] = base + Rz @ (S3 @ (Vector((0, 0, 0.70)) + Mb @ (SPALLA[lp] + BRACCIO * d)))
    return seq


def applica(R, seq, f0=1, con_scala=True, **kw):
    """Mette le chiavi su Pippo (o su un pupazzo con gli stessi perni), un fotogramma alla volta.
    Se la sequenza non e' ancora passata da cinematica() la calcola con gli argomenti dati (posto, giro, braccio_mic, ...)."""
    if 'mondo' not in seq[0] or kw:
        cinematica(seq, **kw)
    prevq = {}
    def cont(nome, q):
        if nome in prevq and prevq[nome].dot(q) < 0: q = -q
        prevq[nome] = q; return q
    for nm in ('hipL', 'hipR', 'footL', 'footR', 'shoulderL', 'shoulderR', 'body', 'head'):
        R[nm].rotation_mode = 'QUATERNION'
    for k, s in enumerate(seq):
        f = f0 + k
        R['root'].location = s['mondo']; R['root'].rotation_euler = (0, 0, s['yaw_m'])
        R['root'].keyframe_insert('location', frame=f); R['root'].keyframe_insert('rotation_euler', frame=f)
        if con_scala and (s['scala'] - Vector((1, 1, 1))).length > 1e-6 or (con_scala and k and (seq[k - 1]['scala'] - Vector((1, 1, 1))).length > 1e-6):
            R['root'].scale = s['scala']; R['root'].keyframe_insert('scale', frame=f)
        R['body'].rotation_quaternion = cont('body', s['qb_']); R['body'].keyframe_insert('rotation_quaternion', frame=f)
        R['head'].rotation_quaternion = cont('head', s['qt_']); R['head'].keyframe_insert('rotation_quaternion', frame=f)
        for lp in 'LR':
            q = cont('hip' + lp, _q_da(s['gambe'][lp]))
            R['hip' + lp].rotation_quaternion = q; R['hip' + lp].keyframe_insert('rotation_quaternion', frame=f)
            R['foot' + lp].rotation_quaternion = cont('foot' + lp, q.inverted()); R['foot' + lp].keyframe_insert('rotation_quaternion', frame=f)
            R['shoulder' + lp].rotation_quaternion = cont('sh' + lp, _q_da(s['bracci'][lp])); R['shoulder' + lp].keyframe_insert('rotation_quaternion', frame=f)
    return f0 + len(seq) - 1


def controllo(seq):
    """Numeri per verificare il movimento: scivolamento massimo del piede d'appoggio e altezza minima delle suole."""
    slip = 0.0; zmin = 9.0; prev = None
    for s in seq:
        Rz = Matrix.Rotation(s['yaw'], 3, 'Z'); base = Vector(s['loc'])
        W = {k: base + Rz @ (ANCA[k] + GAMBA * s['gambe'][k]) for k in 'LR'}
        zmin = min(zmin, W['L'].z, W['R'].z)
        if prev and prev[1] == s['piede'] and not s['volo'] and not prev[2]:
            slip = max(slip, (W[s['piede']].xy - prev[0][s['piede']].xy).length)
        prev = (W, s['piede'], s['volo'])
    return dict(scivolamento_max=round(slip, 5), suola_minima=round(zmin, 4), fotogrammi=len(seq),
                percorso=round((Vector(seq[-1]['loc']).xy - Vector(seq[0]['loc']).xy).length, 2))
