"""Coreografia del video 027: i tempi della canzone (131,88 battute al minuto, prima battuta a 0,06 s), i pezzi di movimento
registrato messi in fila battuta per battuta, i gesti delle braccia sulle parole («mani su, mani giu'», microfono alla bocca
o verso la folla) e la bocca che canta. Niente Blender qui dentro a parte mathutils: si puo' provare in un attimo."""
import math, os, json
import bpy  # noqa: carica mathutils
from mathutils import Vector
import mocap_pippo as mp

QUI = os.path.dirname(os.path.abspath(__file__))
FPS = 24; BPM = 131.88; T0 = 0.060; BATT = 60.0 / BPM; FINE = 48.6
NF = int(round(FINE * FPS))                                                 # 1166 fotogrammi


def B(n):
    """Secondi della battuta n (0 = prima battuta della canzone). Quattro battute = una misura."""
    return T0 + n * BATT


def kb(n):
    """Indice (da 0) del fotogramma della battuta n."""
    return int(round(B(n) * FPS))


def sm(x):
    x = min(1.0, max(0.0, x)); return x * x * (3 - 2 * x)


def finestra(t, a, b, sal=0.26, sce=0.28):
    """1 dentro [a, b], con salita e discesa morbide."""
    return min(sm((t - a) / sal + 1.0) if t < a else 1.0, sm((b - t) / sce + 1.0) if t > b else 1.0) if (a - sal) < t < (b + sce) else 0.0


def clipb(nome, a, b, t0=None, ancora=None, vel=1.0, **kw):
    """Registrazione che copre le battute a..b (anche con la virgola). vel = secondi di registrazione per secondo di video.
    ancora = (istante nella registrazione, battuta): quell'istante cade su quella battuta."""
    n = kb(b) - kb(a); dur = n / FPS
    if ancora is not None:
        t0 = ancora[0] - (ancora[1] - a) * BATT * vel
    return mp.clip(nome, t0=max(0.0, t0), t1=max(0.0, t0) + dur * vel, durata=dur, **kw)


# --------------------------------------------------------------------------- i pezzi, battuta per battuta
# Coordinate: il punto del ritornello (dove Pippo si ferma dopo la camminata) e' l'origine del mondo; la camera sta verso -Y.
# Direzioni: 0 = guarda verso la camera (-Y); +pi/2 = guarda verso +X.
ALZA = 1.5
P_CALCIO = (0.95, 0.40)        # dove si mette per il calcio al grattacielo di destra (battuta 64)
P_PUGNI = (-0.95, 0.35)        # dove si mette per i pugni al grattacielo di sinistra (battute 72-75)
P_CENTRO = (0.0, -0.25)        # dove torna per il pezzo calmo e il finale
P_FINALE = (0.0, -0.30)        # dove torna dopo il calcio volante, per il gran finale


class Coreo:
    def __init__(self):
        self.P = []; self.nomi = []; self.orig = None

    def add(self, nome, pose, **kw):
        self.nomi.append((nome, sum(len(p['pose']) for p in self.P))); self.P.append(mp.pezzo(pose, **kw))

    def seq(self):
        return mp.sequenza(self.P, fps=FPS, fusione=0.25, alza=ALZA)

    def stato(self):
        s = self.seq()[-1]
        return Vector(s['loc']).xy, s['yaw']

    def fissa_origine(self):
        """La posizione attuale diventa l'origine del mondo (il punto del ritornello)."""
        self.orig = self.stato()[0].copy()

    def add_mirato(self, nome, pose, direzione, **kw):
        """Come add, ma gira il pezzo in modo che il suo spostamento vada nella direzione (del mondo) data."""
        prova = mp.sequenza([mp.pezzo(pose, verso=0.0)], fps=FPS, alza=ALZA); d = Vector(prova[-1]['loc']).xy - Vector(prova[0]['loc']).xy
        ang = math.atan2(d.x, -d.y)                                              # dove va quando parte guardando in avanti
        self.add(nome, pose, verso=direzione - ang, **kw)

    def vai(self, nome, a, b, punto, passo_batt=1.0, fusione=0.5):
        """Cammina dalle battute a..b verso il punto (coordinate del mondo), un passo ogni passo_batt battute circa.
        Restituisce la direzione presa."""
        pos, yaw = self.stato(); d = Vector((punto[0] + self.orig.x - pos.x, punto[1] + self.orig.y - pos.y))
        psi = math.atan2(d.x, -d.y); n = kb(b) - kb(a)
        passi = max(1, int(round(d.length / 0.50)))
        dp = (b - a) * BATT / passi
        self.add(nome, mp.cammino(0, dp, n=n, fase=0.5), verso=psi, fusione=fusione)
        return psi


def coreografia():
    C = Coreo(); dp = 2 * BATT
    C.add('cammina', mp.cammino(0, dp, n=kb(20), fase=1 - (B(1) - 0.065) / dp), verso=0.0)                         # 0-20: un passo ogni due battute, appoggio sulle battute dispari
    C.fissa_origine()
    C.add('fermo1', clipb('143_25', 20, 32, t0=0.05), verso=0.0, fusione=0.35)                                      # «E allora Pippo fa...», «Cosa fa?»
    C.add('twist1', clipb('141_12', 32, 39, t0=0.45), verso=0.0, fusione=0.2)                                       # «Balla!», «mani su, mani giu'»
    C.add('vortice1', clipb('55_01', 39, 44, t0=2.2, vel=1.25), verso=0.0, verso_fine=0.0, fusione=0.2)             # «gira, gira, e poi di piu'»
    C.add('fermo2', clipb('143_25', 44, 52, t0=0.3), verso=0.0, fusione=0.25)                                       # «la cosa piu' logica», «Cosa fa?»
    C.add('salto1', clipb('49_02', 52, 57, ancora=(6.79, 56), vel=0.68), verso=0.0, fusione=0.3)                    # «Balla!» e salto: atterra sulla 56
    C.vai('va_dx', 57, 60.6, P_CALCIO)                                                                             # va dal grattacielo di destra
    C.add('calcio', clipb('143_24', 60.6, 66, ancora=(5.17, 64)), verso=math.pi / 2 + 0.26, fusione=0.25)           # calcio sulla 64
    C.vai('va_sx', 66, 70, P_PUGNI)                                                                                # attraversa verso sinistra
    C.add('pugni', clipb('143_23', 70, 76.6, ancora=(1.04, 72), vel=1.099), verso=-math.pi / 2, fusione=0.3)        # pugni sulle 72, 73, 74, 75
    C.vai('va_centro', 76.6, 79, P_CENTRO)
    C.add('twist2', clipb('141_12', 79, 80, t0=1.0), verso=0.0, fusione=0.2)
    C.add('fermo3', clipb('143_25', 80, 88, t0=0.2), verso=0.0, fusione=0.3)                                        # pezzo calmo, «la cosa piu' logica»
    C.add_mirato('volante', clipb('75_16', 88, 92.2, ancora=(1.95, 91), vel=0.5), math.pi / 2, fusione=0.3)         # finale: calcio volante al rallentatore sulla 91, verso destra
    C.vai('ritorno', 92.2, 96, P_FINALE)                                                                           # torna in mezzo alla piazza
    C.add('twist3', clipb('141_12', 96, 100.4, t0=0.45), verso=0.0, fusione=0.2)                                    # mani su, mani giu' con tutta la piazza
    C.add('salto2', clipb('49_02', 100.4, 105, ancora=(5.5, 104), vel=0.8), verso=0.0, fusione=0.3)                 # salto finale: atterra sulla 104
    n_fin = NF - kb(105)
    C.add('finale', mp.clip('143_25', t0=0.3, t1=0.3 + n_fin / FPS * 0.5, durata=n_fin / FPS), verso=0.0, fusione=0.3)
    return C


def sequenza():
    """Restituisce (fotogrammi pronti per applica, {nome del pezzo: indice di partenza}, posto): con «posto» in applica()
    il punto del ritornello cade nell'origine del mondo."""
    C = coreografia(); seq = C.seq()
    return seq, dict(C.nomi), (-C.orig.x, -C.orig.y, 0.0)


# --------------------------------------------------------------------------- gesti delle braccia
SU = [(16.12, 17.18), (B(96) + 0.02, B(98) - 0.02)]                          # «mani su»: tutte e due le braccia in alto
GIU = [(17.26, 17.95), (B(98) + 0.04, B(100) - 0.10)]                         # «mani giu'»: giu' di colpo
CANTA = [(1.62, 8.95), (8.98, 12.30), (14.32, 15.02), (19.62, 22.15), (24.50, 25.08), (36.55, 39.95)]      # microfono alla bocca
FOLLA = [(12.42, 14.22), (15.06, 15.80), (22.22, 24.38)]                     # microfono teso verso la folla che risponde
ORECCHIO = [(12.55, 14.15), (22.35, 24.30)]                                  # mano libera all'orecchio: «non vi sento»
DITO = [(9.05, 10.30)]                                                       # «E allora Pippo fa...»: dito in alto
APERTO = [(10.50, 12.25), (21.35, 22.15)]                                    # «la cosa piu' logica!»: braccio largo
SCHIAFFO = [(7.58, 8.15)]                                                    # manata all'antenna («il wifi non c'e'»)
VITTORIA = [(B(104) - 0.10, FINE + 1.0)]                                     # posa finale: braccia a V
GIRA = [(17.98, 19.70)]                                 # «gira, gira»: braccia larghe mentre gira su se stesso
D_SU = {'L': Vector((-0.22, -0.10, 1.0)), 'R': Vector((0.22, -0.10, 1.0))}
D_GIU = {'L': Vector((-0.25, -0.12, -1.0)), 'R': Vector((0.25, -0.12, -1.0))}
D_V = {'L': Vector((-0.62, -0.05, 1.0)), 'R': Vector((0.62, -0.05, 1.0))}
D_GIRA = {'L': Vector((-1.0, 0.0, 0.10)), 'R': Vector((1.0, 0.0, 0.10))}
D_ORECCHIO = Vector((-0.30, -0.25, 1.0)); D_DITO = Vector((-0.04, -0.80, 0.85)); D_APERTO = Vector((-1.0, -0.25, 0.55)); D_SCHIAFFO = Vector((-1.0, -0.05, 0.12))
FERMO = [(20, 32), (44, 52), (80, 88)]                                       # battute in cui Pippo sta fermo sul posto: la gente balla con i pugni in aria
D_BALLO_SU = {'L': Vector((-0.30, -0.30, 1.0)), 'R': Vector((0.30, -0.30, 1.0))}; D_BALLO_GIU = {'L': Vector((-0.55, -0.45, -0.60)), 'R': Vector((0.55, -0.45, -0.60))}
CORO = [0.06, 0.50, 0.94, 1.28]                                              # attacchi delle sillabe della folla: «Pippo! Pippo! Pippo! Hey!» ...


def _w(t, lista, **kw):
    return max([finestra(t, a, b, **kw) for a, b in lista] or [0.0])


def coro(t):
    """Colpetto (0..1) sulle sillabe che canta la folla: serve per i pugni in aria della gente e per le finestre che lampeggiano."""
    v = 0.0
    for a in CORO:
        if a - 0.05 <= t < a + 0.40:
            v = max(v, sm((t - a + 0.05) / 0.07) * math.exp(-max(0.0, t - a) * 5.5))
    return v


def braccia(d_bocca, d_pubblico, per_folla=False):
    """Restituisce (braccio_mic, braccio_libero) per mocap_pippo.cinematica. per_folla=True: solo i gesti che fa anche la gente
    (pugni in aria quando canta, mani su, mani giu', braccia larghe nel giro, braccia a V alla fine)."""
    def uno(lato):
        def f(k):
            t = k / FPS; d = Vector((0, 0, -1)); w = 0.0
            def metti(dd, ww):
                nonlocal d, w
                if ww > 0.001:
                    d = (d * (1 - ww) + Vector(dd).normalized() * ww) if w > 0.001 else Vector(dd).normalized(); w = max(w, ww)
            if per_folla:
                n = (t - T0) / BATT; wg = 0.9 * max(finestra(t, B(a_), B(b_), sal=0.30, sce=0.30) for a_, b_ in FERMO)
                if wg > 0.001:                                               # un pugno in aria a battuta, una volta per braccio
                    u = (0.5 - 0.5 * math.cos(math.pi * (n + (1 if lato == 'R' else 0)))) ** 1.5
                    metti(D_BALLO_GIU[lato].lerp(D_BALLO_SU[lato], u), wg)
                metti(D_SU[lato], 0.9 * coro(t))
            elif lato == 'R':
                metti(d_bocca, _w(t, CANTA)); metti(d_pubblico, _w(t, FOLLA))
            else:
                metti(D_SCHIAFFO, _w(t, SCHIAFFO, sal=0.16, sce=0.30)); metti(D_DITO, _w(t, DITO)); metti(D_APERTO, _w(t, APERTO, sal=0.20))
                metti(D_ORECCHIO, _w(t, ORECCHIO))
            metti(D_GIRA[lato], 0.9 * _w(t, GIRA, sal=0.25, sce=0.25))
            metti(D_SU[lato], _w(t, SU, sal=0.24, sce=0.10)); metti(D_GIU[lato], _w(t, GIU, sal=0.15, sce=0.30)); metti(D_V[lato], _w(t, VITTORIA, sal=0.18))
            return d, min(1.0, w)
        return f
    return uno('R'), uno('L')


def rimbalzo(k, forza=1.0):
    """Schiaccia e allunga a tempo (scala della radice): un colpetto a ogni battuta, piu' forte dove la cassa batte in quattro."""
    t = k / FPS; n = (t - T0) / BATT; fr = n - math.floor(n)
    a = 0.030 if (56 <= n < 68 or 72 <= n < 80 or 92 <= n < 100.3) else (0.018 if 20 <= n < 56 or 80 <= n < 88 else 0.0)
    if n < 0 or n > 104.6: a = 0.0
    z = 1.0 - a * forza * math.exp(-fr * 5.0) * (1 - math.exp(-fr * 40.0)) * 2.2
    s = 1.0 / math.sqrt(z)
    return (s, s, z)


# --------------------------------------------------------------------------- bocca: sillabe dalle parole della canzone
VOCALI = dict(a=1.0, e=0.62, i=0.34, o=0.85, u=0.45)
PAROLE = [                                                                    # (inizio, fine, parola) rilevati sulla registrazione; tra parentesi le risposte della folla
    (1.72, 2.06, 'Si'), (2.08, 2.24, 'è'), (2.26, 2.64, 'rotta'), (2.66, 2.88, 'la'), (2.90, 3.50, 'macchina'),
    (3.66, 3.90, 'è'), (3.92, 4.38, 'finito'), (4.40, 4.58, 'il'), (4.60, 5.20, 'caffè'),
    (5.52, 5.94, 'il'), (5.96, 6.44, 'capo'), (6.46, 6.62, 'mi'), (6.64, 7.10, 'cerca'),
    (7.52, 7.62, 'il'), (7.64, 7.86, 'wifi'), (7.88, 8.38, 'non'), (8.40, 8.90, "c'è"),
    (8.96, 9.14, 'E'), (9.16, 9.50, 'allora'), (9.52, 9.95, 'Pippo'), (9.97, 10.40, 'fa'),
    (10.46, 10.82, 'la'), (10.84, 11.12, 'cosa'), (11.14, 11.26, 'più'), (11.28, 12.10, 'logica'),
    (12.52, 13.14, '(Cosa'), (13.16, 13.60, 'fa?'), (13.70, 13.84, 'Cosa'), (13.86, 14.20, 'fa?)'),
    (14.42, 15.00, 'Balla!'), (15.14, 15.70, '(Balla!)'),
    (16.06, 16.62, 'Mani'), (16.64, 17.10, 'su,'), (17.24, 17.54, 'mani'), (17.56, 17.90, 'giù,'),
    (17.94, 18.40, 'gira,'), (18.50, 18.84, 'gira,'), (18.88, 19.00, 'e'), (19.02, 19.20, 'poi'), (19.22, 19.42, 'di'), (19.44, 19.72, 'più!'),
    (19.76, 20.30, 'Pippo'), (20.32, 20.62, 'fa'), (20.64, 20.80, 'la'), (20.82, 21.14, 'cosa'), (21.16, 21.58, 'più'), (21.60, 22.14, 'logica!'),
    (22.24, 22.66, '(Cosa'), (22.68, 23.00, 'fa?'), (23.02, 23.08, 'Cosa'), (23.10, 23.42, 'fa?'), (23.44, 23.56, 'Cosa'), (23.58, 24.00, 'fa?)'),
    (24.62, 25.10, 'Balla!'),
    (31.34, 31.42, 'La'), (31.44, 31.62, 'cosa'), (31.64, 31.84, 'più'), (31.86, 32.52, 'logica!'),          # misura 17 (la cassa tace): stessa frase della 21, quattro misure prima
    (38.62, 38.70, 'La'), (38.72, 38.90, 'cosa'), (38.92, 39.12, 'più'), (39.14, 39.80, 'logica!'),
]


def _sillabe(parola):
    p = ''.join(c for c in parola.lower() if c.isalpha() or c in 'àèéìòù')
    p = p.replace('à', 'a').replace('è', 'e').replace('é', 'e').replace('ì', 'i').replace('ò', 'o').replace('ù', 'u')
    v = [c for c in p if c in VOCALI]
    out = []                                                                  # dittonghi: «più», «poi» contano una sillaba sola
    for i, c in enumerate(v):
        if out and p.count('i' + c) and c != 'i' and i > 0 and v[i - 1] == 'i' and len(v) <= 3 and p in ('piu', 'poi'):
            out[-1] = c; continue
        out.append(c)
    return out or ['a']


def _di_folla():
    out = []; dentro = False
    for _a, _b, w in PAROLE:
        dentro = dentro or w.startswith('(')
        out.append(dentro)
        if w.endswith(')'): dentro = False
    return out
DI_FOLLA = _di_folla()                                                       # per ogni parola: True se la canta la folla (tutto quello che sta tra parentesi)


def bocca(t):
    """Apertura della bocca di Pippo (0..1,5) all'istante t: una sillaba alla volta dove canta lui, sorriso quando risponde la folla,
    «Pip-po-po-po» a tempo dove la cassa batte in quattro."""
    for (a, b, w), df in zip(PAROLE, DI_FOLLA):
        if a - 0.03 <= t <= b + 0.04:
            if df:
                return 0.0                                                    # risponde la folla: lui sorride a bocca chiusa
            sl = _sillabe(w); u = min(0.999, max(0.0, (t - a) / max(0.05, b - a))); i = int(u * len(sl)); fr = u * len(sl) - i
            return 0.15 + 1.25 * VOCALI[sl[i]] * math.sin(math.pi * min(1.0, fr * 1.15 + 0.05)) ** 0.6
    n = (t - T0) / BATT
    if (56 <= n < 68) or (72 <= n < 84):                                      # «Pip-po-po-po, Pip-po-po!»: sette sillabe sulle crome 1-7 della misura (rilevato sulla registrazione);
        m = (n % 4) * 2; i = int(m); fr = m - i                               # sull'uno della misura dopo risponde la folla («Hey!») e lui sorride
        if i == 0: return 0.0
        return 0.15 + (0.45 if i in (1, 5) else 1.05) * math.sin(math.pi * min(1.0, fr * 1.15 + 0.05)) ** 0.6
    if 88 <= n < 104:
        return 0.55 + 0.25 * math.sin(2 * math.pi * n)                        # finale strumentale: ride a bocca aperta
    if n >= 104: return 1.3
    return 0.0                                                                # non canta: bocca chiusa (0 = il pezzo della bocca aperta sparisce, resta il sorriso)


for (_a, _b, _w_), _df in zip(PAROLE, DI_FOLLA):                             # gli attacchi delle parole della folla, per coro()
    if _df: CORO.append(_a)
HEY = [B(n_) for n_ in (60, 64, 68, 76, 80, 84)]                             # «Hey!» della folla: sull'uno, dopo ogni «Pip-po-po-po, Pip-po-po!»
CORO += HEY


def bocca_folla(t):
    """Apertura della bocca della gente (0..1): sorriso aperto di base; una sillaba alla volta dove risponde la folla
    («Pippo! Pippo! Pippo! Hey!», «Cosa fa?», «Balla!»); «Pip-po-po-po» insieme a lui dove la cassa batte in quattro."""
    for (a, b, w), df in zip(PAROLE, DI_FOLLA):
        if df and a - 0.03 <= t <= b + 0.04:
            sl = _sillabe(w); u = min(0.999, max(0.0, (t - a) / max(0.05, b - a))); i = int(u * len(sl)); fr = u * len(sl) - i
            return 0.25 + 0.75 * VOCALI[sl[i]] * math.sin(math.pi * min(1.0, fr * 1.15 + 0.05)) ** 0.6
    n = (t - T0) / BATT; base = 0.38
    if (56 <= n < 68) or (72 <= n < 84):                                      # cantano «Pip-po-po-po» insieme a lui, piu' piano
        m = (n % 4) * 2; i = int(m); fr = m - i
        if i > 0: base = 0.25 + 0.45 * math.sin(math.pi * fr) ** 0.7
    if n >= 104: base = 1.0
    return max(base, 0.25 + 0.75 * coro(t))                                   # «Pippo! Pippo! Pippo! Hey!» all'inizio e gli «Hey!» dopo ogni «Pip-po-po»


FOLLA_CANTA = [(0.0, 1.5), (12.50, 14.22), (15.10, 15.75), (22.22, 24.05), (25.10, 25.45)]     # quando risponde la folla: le finestre lampeggiano


def lampo(t):
    """Quanto lampeggiano TUTTE le finestre (0..1): sulle sillabe della folla, sull'atterraggio della 56 e sul colpo finale."""
    v = coro(t)
    for a, k in ((B(56), 4.0), (B(104), 1.6)):
        if a <= t: v = max(v, math.exp(-(t - a) * k))
    return v


def impulso(t):
    """Quanto brillano le finestre accese (1 = normale): battono a tempo, si spengono quando Pippo abbatte l'antenna («il wifi non c'e'»),
    si riaccendono di colpo su «la cosa piu' logica!»."""
    n = (t - T0) / BATT; fr = n - math.floor(n)
    v = 1.0 + (0.9 if n >= 56 else 0.45) * math.exp(-fr * 5.0)
    if 8.02 <= t < 10.46:                                                     # buio: prima sfarfalla, poi niente
        v = (0.25 + 0.75 * (math.sin(t * 90) > 0.2)) * 0.6 if t < 8.35 else 0.04
    elif 10.46 <= t < 12.0:
        v = 1.0 + 2.2 * math.exp(-(t - 10.46) * 3.0)
    return v


# --------------------------------------------------------------------------- dove arrivano mani e piedi nei colpi
def punti_colpo(seq):
    """I punti che contano per mettere i bersagli (dopo mocap_pippo.cinematica): lista di dict(nome, k, t, arto, x, y, z, cx, cy)."""
    out = []
    def reg(nome, k, arto):
        s = seq[k]; p = s['polsi'][arto[1]] if arto[0] == 'p' else s['suole'][arto[1]]
        out.append(dict(nome=nome, k=k, t=round(k / FPS, 2), arto=arto, x=round(p.x, 3), y=round(p.y, 3), z=round(p.z, 3),
                        cx=round(s['mondo'].x, 3), cy=round(s['mondo'].y, 3)))
    def lontano(k0, k1, arti, zmin=0.0, lato=0):
        best = None
        for k in range(k0, k1):
            s = seq[k]
            for a in arti:
                p = s['polsi'][a[1]] if a[0] == 'p' else s['suole'][a[1]]
                if lato and (p.x - s['mondo'].x) * lato < 0.45: continue
                d = (p.xy - s['mondo'].xy).length
                if p.z >= zmin and (best is None or d > best[0]): best = (d, k, a)
        return best
    reg('manata', int(round(7.86 * FPS)), 'pL')
    reg('aperto', int(round(10.80 * FPS)), 'pL')
    r = lontano(int(17.98 * FPS), int(18.55 * FPS), ['pL', 'pR'], zmin=1.0, lato=1)                 # primo passaggio di una mano a destra nel giro
    if r: reg('giro_dx', r[1], r[2])
    r = lontano(kb(63.3), kb(64.8), ['sL', 'sR'], zmin=0.25); reg('calcio', r[1], r[2])
    for n in (72, 73, 74, 75):
        r = lontano(kb(n - 0.35), kb(n + 0.35), ['pL']); reg('pugno%d' % n, r[1], r[2])
    r = lontano(kb(90.2), kb(91.8), ['sL', 'sR'], zmin=0.3); reg('volante', r[1], r[2])
    return out
