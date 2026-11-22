"""Video 020 (Il terzo personaggio, promo del contest) - audio con la SOUND DESIGN TIMELINE (SOUND_DESIGN.md). Esce audio/t020.wav (45.2 s, versione 2 con gli insulti).
Brani di questo video (Kevin MacLeod, CC-BY 4.0, da citare nella descrizione), cambiati dentro le stesse quattro famiglie:
  COMICO = «Monkeys Spinning Monkeys»   SUSPENSE = «Thief in the Night»   EPICO = «Heroic Age»   CAOS = «Circus of Freaks»
Strumenti copiati da audio017.py. Uso, dalla cartella del progetto: python scripts/audio020.py"""
import sys, os, subprocess, wave
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import suoni as S
SR = 44100; DUR = 45.2; N = int(DUR * SR); rng = np.random.default_rng(20)

# ---------- strumenti ----------
def env(a, b, fi=0.1, fo=0.3):
    e = np.zeros(N); i0, i1 = max(0, int(a * SR)), min(N, int(b * SR)); n = i1 - i0
    if n <= 0: return e
    x = np.ones(n); fi_n = max(1, min(n // 2, int(fi * SR))); fo_n = max(1, min(n // 2, int(fo * SR)))
    x[:fi_n] = np.linspace(0, 1, fi_n); x[n - fo_n:] = np.linspace(1, 0, fo_n); e[i0:i1] = x; return e
def ramp(a, b, v0=0.0, v1=1.0):
    t = np.arange(N) / SR; return v0 + (v1 - v0) * np.clip((t - a) / (b - a), 0, 1)
def lp(x, k):
    """media mobile veloce (somma cumulativa), stessa lunghezza dell'ingresso"""
    k = max(1, int(k)); c = np.cumsum(np.concatenate([np.zeros(1), x])); h = k // 2
    i0 = np.clip(np.arange(len(x)) - h, 0, len(x)); i1 = np.clip(np.arange(len(x)) - h + k, 0, len(x)); return (c[i1] - c[i0]) / k
def passa_basso(x, fc, o=4):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); return np.fft.irfft(X / (1 + (f / fc) ** o), len(x))
def passa_alto(x, fc, o=4):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); f[0] = 1e-3; return np.fft.irfft(X / (1 + (fc / f) ** o), len(x))
def put(buf, t0, s, g=1.0):
    i0 = int(t0 * SR)
    if i0 < 0: s = s[-i0:]; i0 = 0
    n = min(len(s), len(buf) - i0)
    if n > 0: buf[i0:i0 + n] += s[:n] * g
def T(d): return np.arange(int(d * SR)) / SR
def osc(f, t): return np.sin(2 * np.pi * np.cumsum(np.broadcast_to(f, t.shape)) / SR)
def saw(f, t): return 2 * ((np.cumsum(np.broadcast_to(f, t.shape)) / SR) % 1.0) - 1

# effetti costruiti
def boom(d=1.8, f0=64, f1=30):
    """impatto cinematografico: sub che scende + botta di rumore + click"""
    t = T(d); f = f1 + (f0 - f1) * np.exp(-t * 5); x = osc(f, t) * np.exp(-t * 2.0) + 0.6 * passa_basso(rng.normal(0, 1, len(t)), 500) * np.exp(-t * 8)
    c = int(0.004 * SR); x[:c] += np.linspace(1.2, 0, c); return np.tanh(x * 1.7)
def bass_drop(d=1.2):
    t = T(d); f = 34 + 150 * np.exp(-t * 2.4); return np.tanh(osc(f, t) * np.minimum(1, t * 60) * np.exp(-t * 1.1) * 1.9)
def riser(d, f0=170, f1=1500):
    t = T(d); u = t / d; n = passa_alto(rng.normal(0, 1, len(t)), 2200) * u ** 2.4 * 0.5
    f = f0 * (f1 / f0) ** u; return n + osc(f, t) * u ** 1.7 * 0.45 + osc(f * 1.5, t) * u ** 2.3 * 0.22
def whoosh(d=0.45, verso=1):
    t = T(d); n = rng.normal(0, 1, len(t)); u = t / d if verso > 0 else 1 - t / d
    return (passa_basso(n, 600) * 2.2 * (1 - u) + passa_basso(n, 3200) * u) * np.hanning(len(t))
def boing(d=0.55, f=230):
    t = T(d); fr = f * (1 + 0.3 * np.exp(-t * 4) * np.sin(2 * np.pi * 15 * t)) * (1 + 0.3 * np.exp(-t * 3)); return osc(fr, t) * np.exp(-t * 4.5)
def glitch(d=0.4):
    x = np.zeros(int(d * SR)); b = int(0.028 * SR)
    for i in range(0, len(x) - b, b):
        if rng.random() < 0.25: continue
        t = T(b / SR); x[i:i + b] = np.sign(np.sin(2 * np.pi * rng.choice([150, 300, 900, 1800, 3200]) * t))[:b] * rng.uniform(0.4, 1.0)
    return passa_basso(x, 5000) * 0.8
def grilli(d):
    x = np.zeros(int(d * SR))
    for c in np.arange(0.05, d - 0.2, 0.62):
        for k in range(3):
            s_ = np.sin(2 * np.pi * 4400 * T(0.035)) * np.hanning(int(0.035 * SR)); i = int((c + k * 0.06) * SR); x[i:i + len(s_)] += s_[:len(x) - i]
    return x
def colpo_orchestra(root=146.8, d=0.9):
    """accordo di ottoni secco con il sub sotto"""
    t = T(d); x = sum(saw(root * r, t) for r in (1, 1.5, 2, 2.52, 3)) / 4
    x = passa_basso(x, 2600) * np.minimum(1, t * 200) * np.exp(-t * 4.5); y = boom(d, 70, 40)[:len(t)] * 0.7; return np.tanh((x + y) * 1.5)
def stacco_drammatico(root=73.4, d=2.0):
    """accordo minore grave e solenne + rullo di timpani che finisce con un colpo"""
    t = T(d); ch = sum(saw(root * r, t) for r in (1, 1.189, 1.5, 2)) / 3; ch = passa_basso(ch, 800) * np.minimum(1, t * 6) * np.exp(-np.maximum(0, t - 0.5) * 1.6)
    tim = np.zeros(len(t))
    for k, tk in enumerate(np.arange(0, 0.42, 0.045)):
        i = int(tk * SR); s_ = osc(84, T(0.25)) * np.exp(-T(0.25) * 14) * (0.25 + k * 0.06); tim[i:i + len(s_)] += s_[:len(tim) - i]
    big = boom(1.4, 90, 42); i = int(0.45 * SR); tim[i:i + len(big)] += big[:len(tim) - i] * 0.9
    return np.tanh(ch * 1.3 + tim)
def dun(root=55.0, d=0.9):
    t = T(d); return np.tanh((osc(root, t) + 0.5 * osc(root * 2, t) + 0.25 * saw(root, t)) * np.exp(-t * 3.5) * 1.6)
def trombetta():
    """tre colpi di trombetta da stadio (sintetizzata): il secondo colpo di scena"""
    x = np.zeros(int(1.0 * SR))
    for (a, d) in ((0.0, 0.14), (0.2, 0.14), (0.4, 0.55)):
        t = T(d); s = sum(saw(f * (1 + 0.004 * np.sin(2 * np.pi * 6 * t)), t) for f in (466.2, 587.3, 698.5)) / 3
        s = passa_basso(s, 3200) * np.minimum(1, t * 120) * np.minimum(1, (d - t) * 60); i = int(a * SR); x[i:i + len(s)] += s
    return np.tanh(x * 2.2)
def fischietto(d=0.6):
    t = T(d); return osc(2850 * (1 + 0.04 * np.sin(2 * np.pi * 32 * t)), t) * np.minimum(1, t * 40) * np.minimum(1, (d - t) * 20)
def tape_stop(x, t0, d=0.6):
    """la musica rallenta fino a fermarsi (come un giradischi staccato)"""
    i0 = int(t0 * SR); n = int(d * SR); seg = x[i0:i0 + 3 * n].copy()
    pos = np.cumsum(np.linspace(1, 0, n)); y = np.interp(pos, np.arange(len(seg)), seg) * np.linspace(1, 0.2, n)
    x[i0:i0 + n] = y; x[i0 + n:] = 0
def ovatta(x, quanto):
    """quanto 0 = pulito, 1 = dietro una porta"""
    return x * (1 - quanto) + passa_basso(x, 420) * 2.4 * quanto


# ---------- voce ----------
subprocess.run([S.FFMPEG, '-y', '-loglevel', 'error', '-i', 'audio/voce_t020.mp3', '-ar', str(SR), '-ac', '1', 'audio/voce44_t020.wav'], check=True)
w = wave.open('audio/voce44_t020.wav'); v = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(float) / 32768; v = np.pad(v, (0, max(0, N - len(v))))[:N]
_loc = np.sqrt(lp(v ** 2, int(0.35 * SR))); v = v * lp(np.clip(0.115 / (_loc + 0.03), 0.9, 3.0), int(0.25 * SR))     # i sussurri vengono alzati
venv = lp(np.abs(v), int(0.12 * SR)); venv = np.clip(venv / (np.percentile(venv, 95) + 1e-9), 0, 1)

# ---------- tempi (gli stessi di anim020.py) ----------
T_PIPPO, T_AEREO, T_SPOT3, T_MANCA, T_MACH, T_DING = 1.28, 3.34, 4.5, 5.02, 5.96, 7.56
T_RUN, T_BRAVO = 7.56 + 1.75, 9.36
T_KICK, T_CHICK, T_CAZ, T_BOOM = 10.40, 10.96, 12.46, 13.06
T_GUAL, T_BAFFI, T_STAMP, T_QUINDI, T_VOI, T_SCIMMIE = 13.98, 16.66, 17.90, 19.10, 21.66, 22.60
T_W = (23.82, 24.38, 25.12, 25.78, 26.42)
T_TESTA, T_REGOLE, T_SEGUI, T_LIKE, T_COMM = 27.36, 29.38, 30.30, 31.26, 31.98
T_48, T_PIU, T_UFF = 33.62, 34.74, 35.88
T_GCOMM, T_G2, T_PEZZO, T_NO, T_MUOVI, T_COMMENTA, T_ADESSO, T_END = 38.14, 39.78, 40.80, 42.08, 42.68, 43.32, 43.90, 44.85

# ---------- musica: le quattro famiglie ----------
def traccia(rel, inizio=None, cerca=(0, 100), finestra=8.0):
    x = S.carica('musica/' + rel, SR)
    if inizio is None:
        h = int(SR * 0.5); r = np.sqrt(lp(x ** 2, int(finestra * SR))[::h]); a, b = int(cerca[0] * 2), min(len(r), int(cerca[1] * 2))
        inizio = max(0.0, (a + int(np.argmax(r[a:b]))) * 0.5 - finestra / 2)
    y = x[int(inizio * SR):]; y = y / (np.sqrt(np.mean(y[:int(20 * SR)] ** 2)) + 1e-9) * 0.1; return y, inizio
def stendi(buf, x, t0, t1, g, fi=0.05, fo=0.05, da=0.0):
    seg = np.zeros(N); i0 = int(t0 * SR); s = x[int(da * SR):int(da * SR) + (N - i0)]; seg[i0:i0 + len(s)] = s; buf += seg * env(t0, t1, fi, fo) * g; return seg
COMICO, i_c = traccia('comica/Monkeys_Spinning_Monkeys', inizio=1.0)
SUSPENSE, i_s = traccia('suspense/Thief_in_the_Night', cerca=(5, 60))
EPICO, i_e = traccia('epica/Heroic_Age', cerca=(10, 120))
CAOS, i_k = traccia('brainrot/Circus_of_Freaks', cerca=(5, 90))
print('inizi dei brani (s): suspense %.1f, epico %.1f, caos %.1f' % (i_s, i_e, i_k))
mus = np.zeros(N); t = np.arange(N) / SR
# 0.9 COMICO: la squadra; stop secco quando il pulcino si gonfia
co = np.zeros(N); stendi(co, COMICO, 0.9, T_CAZ, 1.0, 0.15, 0.02); co *= 1 - 0.8 * env(T_BRAVO, T_KICK, 0.05, 0.1); mus += co * 0.12
# 10.86 tensione: bordone che trema mentre il pulcino si gonfia; 11.6 BOOM e silenzio
mus += (np.sin(2 * np.pi * 55 * t) + 0.5 * np.sin(2 * np.pi * 58.3 * t)) * env(T_CAZ, T_BOOM, 0.1, 0.01) * 0.05
# 12.68 SUSPENSE: Gualtiero in punta di piedi; si ferma di colpo sul timbro
su_ = np.zeros(N); stendi(su_, SUSPENSE, T_GUAL - 0.05, T_STAMP - 0.02, 1.0, 0.3, 0.02); mus += su_ * 0.13
# 17.94 «Quindi il terzo personaggio...»: silenzio vero, poi bordone che sale verso il colpo di scena
mus += (np.sin(2 * np.pi * 49 * t) + 0.4 * np.sin(2 * np.pi * 73.4 * t)) * (0.6 + 0.4 * np.sin(2 * np.pi * 6 * t)) * env(18.6, T_VOI - 0.02, 1.2, 0.02) * 0.05
# 20.98 EPICO esplode: LO CREATE VOI
ep = np.zeros(N); stendi(ep, EPICO, T_VOI - 0.02, T_W[0] - 0.1, 1.0, 0.01, 0.25); mus += ep * 0.30
# 22.0 CAOS sotto la voce: parole, regole, like, commenti; tape stop sul timer
ca = np.zeros(N); stendi(ca, CAOS, T_W[0] - 0.25, T_48 + 0.2, 1.0, 0.2, 0.02)
ca *= 1 - 0.55 * env(T_REGOLE - 0.06, T_REGOLE + 0.3, 0.02, 0.05)                                  # «REGOLE»: buco di un attimo per il colpo d'orchestra
tape_stop(ca, T_48 - 0.25, 0.5); mus += ca * 0.16
# 34.2 EPICO pieno: DIVENTA UN PERSONAGGIO UFFICIALE
ep2 = np.zeros(N); stendi(ep2, EPICO, T_UFF - 0.02, T_GCOMM - 0.05, 1.0, 0.01, 0.15, da=12.0); mus += ep2 * 0.28
# 39.0 CAOS a tutto volume per la CTA, poi stop netto
ca2 = np.zeros(N); stendi(ca2, CAOS, T_NO - 0.02, T_END, 1.0, 0.01, 0.02, da=20.0); mus += ca2 * 0.26
mus *= (1 - 0.45 * venv) * 2.0

# ---------- effetti ----------
fx = np.zeros(N); big = np.zeros(N)
def sfx(tp, nome, g=1.0, vel=1.0):
    x = S.carica(nome, SR, volume=g)
    if vel != 1.0: x = np.interp(np.arange(0, len(x), vel), np.arange(len(x)), x)
    put(fx, tp, x)
def bip(tp, f, g=0.09, d=0.09): n = int(d * SR); put(fx, tp, np.sin(2 * np.pi * f * T(d)) * np.hanning(n) * g * 2)
def ding(tp, g=0.3):
    d = 1.2; tt = T(d); put(fx, tp, (np.sin(2 * np.pi * 1568 * tt) + 0.5 * np.sin(2 * np.pi * 3136 * tt) + 0.25 * np.sin(2 * np.pi * 4704 * tt)) * np.exp(-tt * 4) * g)
def cip(tp, g=0.12):
    for k in range(2):
        d = 0.09; tt = T(d); put(fx, tp + 0.13 * k, np.sin(2 * np.pi * (3200 + 1600 * tt / d) * tt) * np.hanning(len(tt)) * g)
def gonfia(tp, d):
    tt = T(d); f = 180 * (6 ** (tt / d)); put(fx, tp, osc(f, tt) * 0.25 * (tt / d) + passa_basso(rng.normal(0, 1, len(tt)), 900) * 0.15 * (tt / d) ** 2)
# 00.00 HOOK: record scratch + sipario + colpo d'orchestra; i tre occhi di bue
sfx(0.0, 'scratch_003', 1.0); put(fx, 0.12, whoosh(0.7, 1), 0.55); put(big, 0.05, colpo_orchestra(146.8), 0.5)
for tp in (0.35, 0.55, T_SPOT3): sfx(tp, 'switch_005', 0.9); put(big, tp, dun(65, 0.5), 0.25)
put(fx, T_PIPPO - 0.05, whoosh(0.3, 1), 0.45)                                                      # «quel coglione a pedali»: stacco sul primo piano
for k, f_ in enumerate((880, 660, 440)): bip(T_AEREO + 0.35 + 0.12 * k, f_, 0.07, 0.1)             # «modalita' aereo»: il cervello si spegne
put(fx, T_MANCA, whoosh(0.3, 1), 0.4)
# 4.12 la macchina cade, manovella, ding
put(fx, T_MACH - 0.4, whoosh(0.4, 1), 0.5); put(big, T_MACH, boom(0.8, 75, 40), 0.45); sfx(T_MACH, 'impactMetal_heavy_001', 0.8); put(fx, T_MACH + 0.03, boing(0.6, 160), 0.3)
for k in range(16): sfx(T_MACH + 0.25 + k * 0.11, 'click_00%d' % (1 + k % 4), 0.5)
ding(T_DING, 0.3); sfx(T_DING + 0.05, 'drop_002', 0.8)
for k in range(13): sfx(T_DING + 0.4 + k * 0.1, 'footstep_carpet_00%d' % (k % 5), 0.45, vel=1.8)
def trombone_triste(tp, g=0.2):
    """wah wah wah waaah: la sconfitta di Pippo"""
    for k, (f0, d) in enumerate(((311, 0.32), (293, 0.32), (277, 0.32), (262, 0.9))):
        tt = T(d); f = f0 * (1 + 0.012 * np.sin(2 * np.pi * 5.5 * tt)) * (1 - (0.04 * tt / d if k == 3 else 0)); x = sum(saw(f * r, tt) for r in (1, 2)) / 2
        put(fx, tp + 0.34 * k, passa_basso(x, 1100) * np.minimum(1, tt * 25) * np.minimum(1, (d - tt) * 10) * (0.6 + 0.4 * np.sin(np.pi * np.minimum(1, tt / 0.3))), g)
trombone_triste(T_BRAVO + 0.05)
# 8.28 calcio, pulcino, si gonfia, BOOM
sfx(T_KICK + 0.25, 'impactPunch_heavy_001', 0.8); sfx(T_KICK + 0.27, 'impactMetal_heavy_002', 0.6); put(fx, T_KICK + 0.27, boing(0.5, 200), 0.25)
sfx(T_CHICK, 'drop_003', 0.7); cip(T_CHICK + 0.35); cip(T_CHICK + 0.9, 0.1)
gonfia(T_CAZ, T_BOOM - T_CAZ)
put(big, T_BOOM, boom(2.0, 60, 26), 0.9); put(big, T_BOOM, colpo_orchestra(110), 0.35); sfx(T_BOOM + 0.02, 'explosionCrunch_002', 0.9)
put(fx, T_BOOM + 0.6, grilli(1.0), 0.07)
# 12.68 Gualtiero in punta di piedi; il timbro
for k in range(7): sfx(T_GUAL + 0.1 + k * 0.23, 'footstep_carpet_00%d' % (k % 5), 0.35, vel=1.4)
put(fx, T_STAMP - 0.33, whoosh(0.33, 1), 0.6); put(big, T_STAMP, dun(50, 1.0), 0.5); put(big, T_STAMP, boom(1.0, 70, 35), 0.45)
sfx(T_STAMP + 0.01, 'impactWood_heavy_003', 0.9); put(fx, T_STAMP + 0.05, boing(0.7, 120), 0.3); sfx(17.2, 'impactSoft_heavy_001', 0.5)
# 17.94 silenzio, poi riser verso LO CREATE VOI
put(fx, 18.7, riser(T_VOI - 18.7, 140, 1700), 0.28)
put(big, T_VOI - 0.02, bass_drop(1.3), 0.55); put(fx, T_VOI, whoosh(0.35, 1), 0.6); put(big, T_VOI, boom(1.2, 70, 35), 0.35)
put(fx, T_SCIMMIE - 0.05, whoosh(0.3, 1), 0.45)                                                   # «branco di scimmie»: il pubblico
for k in range(7):
    d = 0.16; tt = T(d); f0 = 520 + 90 * (k % 3); put(fx, T_SCIMMIE + 0.25 + 0.13 * k, np.sin(2 * np.pi * np.cumsum(f0 * (1 + 0.6 * tt / d)) / SR) * np.hanning(len(tt)), 0.06)
for k in range(6): sfx(T_VOI + 0.3 + 0.17 * k, 'laser%d' % (1 + k % 5), 0.18)
# 22.22 le cinque parole: un suono diverso per ciascuna
put(fx, T_W[0] + 0.06, boing(0.5, 260), 0.35); sfx(T_W[0] + 0.06, 'impactSoft_heavy_000', 0.6)
put(big, T_W[1] + 0.06, trombetta(), 0.22)
sfx(T_W[2] + 0.06, 'drop_004', 0.9); sfx(T_W[2] + 0.07, 'impactWood_heavy_001', 0.6)
put(fx, T_W[3] + 0.06, fischietto(0.4), 0.07); sfx(T_W[3] + 0.06, 'impactSoft_heavy_002', 0.6)
put(big, T_W[4] + 0.08, boom(0.8, 70, 40), 0.4); sfx(T_W[4] + 0.1, 'impactPunch_heavy_003', 0.8); put(fx, T_W[4] + 0.15, boing(0.7, 140), 0.25)
put(fx, T_TESTA - 0.05, whoosh(0.3, 1), 0.4); put(fx, T_TESTA + 0.6, grilli(1.2), 0.07)
d_ = 0.12; tt_ = T(d_); put(fx, T_TESTA + 0.75, np.sin(2 * np.pi * 2600 * tt_) * np.hanning(len(tt_)), 0.08); sfx(T_TESTA + 1.0, 'impactSoft_medium_001', 0.5)   # squittio del criceto, poi tonfo
# 27.58 REGOLE, SEGUI, LIKE, COMMENTI
put(big, T_REGOLE - 0.02, colpo_orchestra(130.8), 0.45); sfx(T_REGOLE + 0.05, 'impactPlate_heavy_001', 0.6)
put(fx, T_SEGUI + 0.05, whoosh(0.25, 1), 0.5); sfx(T_SEGUI + 0.3, 'impactPlate_heavy_003', 0.9); put(big, T_SEGUI + 0.3, boom(0.7, 75, 40), 0.35); put(fx, T_SEGUI + 0.32, boing(0.6, 240), 0.3)
sfx(T_SEGUI + 0.45, 'confirmation_002', 0.5)
put(fx, T_LIKE + 0.05, boing(0.45, 330), 0.25); sfx(T_LIKE + 0.35, 'impactSoft_medium_001', 0.7); sfx(T_LIKE + 0.5, 'drop_001', 1.0); sfx(T_LIKE + 0.52, 'powerUp2', 0.35)
put(fx, T_COMM + 0.2, whoosh(0.5, 1), 0.55); put(big, T_COMM + 0.7, boom(0.9, 65, 35), 0.45); sfx(T_COMM + 0.7, 'impactSoft_heavy_003', 0.8)
for k in range(5): bip(T_COMM + 0.95 + 0.14 * k, 900 + 200 * (k % 3), 0.04, 0.05)          # qualcuno sta scrivendo...
# 31.64 timer: tic-tac; il contatore dei like
for k in range(4): sfx(T_48 + 0.85 * k, 'tick_002', 0.9); bip(T_48 + 0.85 * k + 0.42, 600, 0.05, 0.05)
for k in range(10): sfx(T_PIU + 0.2 + 0.06 * k, 'click_00%d' % (1 + k % 4), 0.35)
# 34.2 DIVENTA UFFICIALE: colpo d'orchestra, corona, fuochi
put(big, T_UFF - 0.02, colpo_orchestra(146.8, 1.2), 0.55); put(big, T_UFF, boom(1.4, 70, 32), 0.4)
put(fx, T_UFF + 0.25, whoosh(0.4, 1), 0.35); sfx(T_UFF + 0.7, 'impactBell_heavy_001', 0.5)
for k in range(8): sfx(T_UFF + 0.35 + 0.15 * k, 'laser%d' % (1 + k % 5), 0.15)
# 36.28 Gualtiero: grilli, tap tap, notifica, stacco drammatico
put(fx, T_GCOMM, grilli(1.5), 0.08)
for k in range(9): sfx(T_GCOMM + 0.15 + 0.13 * k, 'click_00%d' % (1 + k % 4), 0.3)
put(big, T_G2 - 0.45, stacco_drammatico(73.4, 1.8), 0.45); bip(T_G2, 1320, 0.08, 0.08); bip(T_G2 + 0.1, 1760, 0.08, 0.1)
put(fx, T_PEZZO - 0.05, whoosh(0.25, 1), 0.4); sfx(T_PEZZO + 0.6, 'scratch_001', 0.6)
# 39.0 CTA: glitch, boom, zoom a scatti, boom finale, pop
put(fx, T_NO - 0.05, glitch(0.3), 0.3); put(big, T_NO, boom(1.2, 70, 34), 0.55)
for tp in (T_MUOVI, T_COMMENTA): put(fx, tp - 0.05, whoosh(0.25, 1), 0.5); put(big, tp, dun(60, 0.4), 0.3)
put(big, T_ADESSO, boom(1.6, 64, 28), 0.85); put(big, T_ADESSO, colpo_orchestra(98.0, 0.9), 0.4)
sfx(T_END + 0.05, 'drop_002', 1.0)

# ---------- mix con limitatore ----------
out = v * 1.0 + mus + np.tanh(fx * 1.1) * 0.45 + big * 0.5
out *= env(0, T_END + 0.25, 0.002, 0.04)
h = 256; pk = np.abs(out[:N // h * h]).reshape(-1, h).max(1)
g = np.minimum(1.0, 0.95 / np.maximum(pk, 1e-6)); g = np.minimum(g, np.concatenate([g[1:], g[-1:]])); g = np.convolve(g, np.ones(9) / 9, mode='same')
gg = np.interp(np.arange(N), np.arange(len(g)) * h + h / 2, g); out = np.clip(out * gg, -0.99, 0.99)
ww = wave.open('audio/t020.wav', 'w'); ww.setnchannels(1); ww.setsampwidth(2); ww.setframerate(SR); ww.writeframes((out * 32767).astype(np.int16).tobytes()); ww.close()
def rms(x, a, b): return float(np.sqrt(np.mean(x[int(a * SR):int(b * SR)] ** 2)))
print('audio/t020.wav', DUR, 's  riduzione massima del limitatore %.2f' % float(gg.min()))
for nome, a, b in (('hook', 0, 4.4), ('macchina', 6.0, 9.3), ('bravo', 9.36, 10.4), ('gualtiero', 14.0, 17.8), ('quindi', 19.1, 21.6), ('voi', 21.7, 23.8), ('parole', 23.8, 29.3), ('regole', 29.4, 33.5), ('timer', 33.7, 35.8), ('ufficiale', 35.9, 38.1), ('cta', 42.1, 44.8)):
    print('%-10s voce %.3f  musica %.3f  effetti %.3f  impatti %.3f' % (nome, rms(v, a, b), rms(mus, a, b), rms(np.tanh(fx * 1.1) * 0.45, a, b), rms(big * 0.5, a, b)))
