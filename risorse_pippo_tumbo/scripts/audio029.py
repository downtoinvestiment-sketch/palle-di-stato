"""Video 029 (La guerra per il petrolio, copione n. 29C v5) - audio con la SOUND DESIGN TIMELINE (SOUND_DESIGN.md). Esce audio/t029.wav (45,0 s).
Brani (Kevin MacLeod, CC-BY 4.0, da citare nella descrizione), dentro le quattro famiglie:
  EPICO = «Five Armies» (il comizio pomposo, la conquista)   COMICO = «Scheming Weasel (faster)»   SUSPENSE = «Spy Glass» (la grotta)   CAOS = «Hall of the Mountain King» (il T-rex)
Strumenti copiati da audio020.py. Uso, dalla cartella del progetto: python scripts/audio029.py"""
import sys, os, subprocess, wave
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import suoni as S
SR = 44100; DUR = 45.0; N = int(DUR * SR); rng = np.random.default_rng(29)

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
subprocess.run([S.FFMPEG, '-y', '-loglevel', 'error', '-i', 'audio/voce_t029.mp3', '-ar', str(SR), '-ac', '1', 'audio/voce44_t029.wav'], check=True)
w = wave.open('audio/voce44_t029.wav'); v = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(float) / 32768; v = np.pad(v, (0, max(0, N - len(v))))[:N]
_loc = np.sqrt(lp(v ** 2, int(0.35 * SR))); v = v * lp(np.clip(0.115 / (_loc + 0.03), 0.9, 3.0), int(0.25 * SR))     # il sussurro della grotta viene alzato
venv = lp(np.abs(v), int(0.12 * SR)); venv = np.clip(venv / (np.percentile(venv, 95) + 1e-9), 0, 1)

# ---------- tempi (gli stessi di anim029.py) ----------
T_GUERRA, T_IRAN, T_CHE, T_MOTIVO, T_STORTO, T_CANNONI, T_PUNTA = 2.44, 3.70, 4.56, 7.46, 8.40, 9.74, 10.22
T_ACCANTO, T_ROSPINA, T_GUINZ, T_SPASSO = 12.38, 13.34, 14.18, 14.92
T_ALLORA, T_YOGA, T_CONQ, T_TRIV = 18.08, 20.10, 22.30, 23.82
T_MA, T_DINO, T_VIVO, T_CAZZO = 24.66, 26.36, 27.34, 28.48
T_TREX, T_BEVE, T_SUCCO, T_PORGE = 29.36, 31.16, 32.18, 33.20
T_PIENO, T_BENZ, T_800, T_PORCA, T_TEAM, T_END = 35.98, 37.90, 39.50, 40.90, 42.02, 44.5

def traccia(rel, inizio=None, cerca=(0, 100), finestra=8.0):
    x = S.carica('musica/' + rel, SR)
    if inizio is None:
        h = int(SR * 0.5); r = np.sqrt(lp(x ** 2, int(finestra * SR))[::h]); a, b = int(cerca[0] * 2), min(len(r), int(cerca[1] * 2))
        inizio = max(0.0, (a + int(np.argmax(r[a:b]))) * 0.5 - finestra / 2)
    y = x[int(inizio * SR):]; y = y / (np.sqrt(np.mean(y[:int(20 * SR)] ** 2)) + 1e-9) * 0.1; return y, inizio
def stendi(buf, x, t0, t1, g, fi=0.05, fo=0.05, da=0.0):
    seg = np.zeros(N); i0 = int(t0 * SR); s = x[int(da * SR):int(da * SR) + (N - i0)]; seg[i0:i0 + len(s)] = s; buf += seg * env(t0, t1, fi, fo) * g; return seg

EPICO, i_e = traccia('epica/Five_Armies', cerca=(5, 90))
COMICO, i_c = traccia('comica/Scheming_Weasel_faster', inizio=0.5)
SUSPENSE, i_s = traccia('suspense/Spy_Glass', cerca=(5, 80))
CAOS, i_k = traccia('brainrot/Hall_of_the_Mountain_King', cerca=(60, 150))
print('inizi dei brani (s): epico %.1f, suspense %.1f, caos %.1f' % (i_e, i_s, i_k))
mus = np.zeros(N); t = np.arange(N) / SR
ep = np.zeros(N); stendi(ep, EPICO, 0.0, T_CHE - 0.05, 1.0, 0.02, 0.1); mus += ep * 0.20                    # il comizio pomposo
co = np.zeros(N); stendi(co, COMICO, T_CHE - 0.05, T_ALLORA - 0.02, 1.0, 0.05, 0.02)                        # la «pura coincidenza», cannoni, guinzaglio
co *= 1 - 0.6 * env(T_STORTO - 0.05, T_STORTO + 0.5, 0.02, 0.1); mus += co * 0.13
mus += (np.sin(2 * np.pi * 110 * t) + 0.6 * np.sin(2 * np.pi * 164.8 * t) + 0.4 * np.sin(2 * np.pi * 220 * t)) * env(T_YOGA, T_CONQ - 0.05, 0.4, 0.2) * 0.025   # bordone zen
ep2 = np.zeros(N); stendi(ep2, EPICO, T_CONQ - 0.02, T_MA - 0.05, 1.0, 0.02, 0.02, da=30.0); mus += ep2 * 0.22  # la conquista, stop secco sul «Ma»
su_ = np.zeros(N); stendi(su_, SUSPENSE, T_MA + 0.6, T_VIVO - 0.02, 1.0, 0.8, 0.02); mus += su_ * 0.10          # la grotta, dopo un silenzio vero
ca = np.zeros(N); stendi(ca, CAOS, T_TREX - 0.02, T_PIENO - 0.05, 1.0, 0.01, 0.2); mus += ca * 0.22             # il T-rex
co2 = np.zeros(N); stendi(co2, COMICO, T_PIENO - 0.02, T_END, 1.0, 0.05, 0.05, da=20.0)
tape_stop(co2, T_PORCA - 0.25, 0.4); mus += co2 * 0.13
mus *= (1 - 0.45 * venv) * 2.0

# ---------- effetti ----------
fx = np.zeros(N); big = np.zeros(N)
def sfx(tp, nome, g=1.0, vel=1.0):
    x = S.carica(nome, SR, volume=g)
    if vel != 1.0: x = np.interp(np.arange(0, len(x), vel), np.arange(len(x)), x)
    put(fx, tp, x)
def bip(tp, f, g=0.09, d=0.09): n = int(d * SR); put(fx, tp, np.sin(2 * np.pi * f * T(d)) * np.hanning(n) * g * 2)
def scatto(tp, g=0.25):
    d = 0.06; tt = T(d); put(fx, tp, passa_alto(rng.normal(0, 1, len(tt)), 2500) * np.exp(-tt * 70) * g)
def applausi(tp, d, g=0.05):
    tt = T(d); x = np.zeros(len(tt))
    for k in range(int(d * 40)):
        i = rng.integers(0, len(tt) - 800); x[i:i + 800] += passa_alto(rng.normal(0, 1, 800), 1200) * np.exp(-np.arange(800) / 120.0) * rng.uniform(0.4, 1.0)
    put(fx, tp, x * np.minimum(1, tt * 3) * np.minimum(1, (d - tt) * 2) * g)
def cigolio(tp, g=0.06, f=900):
    d = 0.35; tt = T(d); put(fx, tp, np.sin(2 * np.pi * np.cumsum(f * (1 + 0.25 * np.sin(2 * np.pi * 7 * tt))) / SR) * np.sin(np.pi * tt / d) ** 2 * g)
def gong(tp, g=0.25):
    d = 3.0; tt = T(d); x = sum(a * np.sin(2 * np.pi * f * tt) for f, a in ((110, 1.0), (176, 0.6), (261, 0.4), (397, 0.25))); put(fx, tp, x * np.exp(-tt * 1.2) * g)
def trivella(tp, d, g=0.12):
    tt = T(d); x = saw(55 + 30 * np.minimum(1, tt * 2), tt) * 0.5 + passa_basso(rng.normal(0, 1, len(tt)), 1500) * (0.6 + 0.4 * np.sin(2 * np.pi * 18 * tt))
    put(fx, tp, x * np.minimum(1, tt * 5) * np.minimum(1, (d - tt) * 5) * g)
def ruggito(tp, d=1.6, g=0.5):
    tt = T(d); f = 70 + 40 * np.sin(np.pi * tt / d); x = saw(f, tt) + 0.6 * saw(f * 1.51, tt) + passa_basso(rng.normal(0, 1, len(tt)), 900) * 1.2
    x = passa_basso(x, 1400) * (1 + 0.4 * np.sin(2 * np.pi * 23 * tt)); put(big, tp, x * np.minimum(1, tt * 8) * np.exp(-np.maximum(0, tt - d * 0.6) * 4) * g)
def russa(tp, d, g=0.08):
    tt = T(d); x = passa_basso(rng.normal(0, 1, len(tt)), 300) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.45 * tt)) ** 2 + 0.3 * saw(40, tt) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.45 * tt)) ** 4
    put(fx, tp, x * g)
def goccia(tp, g=0.06):
    d = 0.25; tt = T(d); f = 1400 * np.exp(-tt * 6) + 500; put(fx, tp, np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 18) * g)
    put(fx, tp + 0.18, np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 18) * g * 0.3)
def geyser(tp, d, g=0.15):
    tt = T(d); put(fx, tp, passa_basso(rng.normal(0, 1, len(tt)), 700) * np.minimum(1, tt * 6) * np.minimum(1, (d - tt) * 3) * g)
def slurp(tp, d, g=0.18):
    tt = T(d); f = 350 + 250 * np.sin(2 * np.pi * 9 * tt) + 200 * tt / d
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 11 * tt))) * 0.6 + passa_alto(rng.normal(0, 1, len(tt)), 2000) * 0.3
    put(fx, tp, x * np.minimum(1, tt * 10) * np.minimum(1, (d - tt) * 10) * g)
def rutto(tp, d=1.1, g=0.45):
    tt = T(d); f = 85 - 20 * tt / d + 6 * np.sin(2 * np.pi * 30 * tt); x = saw(f, tt) + 0.5 * saw(f * 2.02, tt)
    put(big, tp, passa_basso(x, 900) * (1 + 0.6 * np.sin(2 * np.pi * 13 * tt)) * np.minimum(1, tt * 12) * np.exp(-np.maximum(0, tt - 0.7) * 6) * g)
def squittio(tp, g=0.12):
    d = 0.22; tt = T(d); put(fx, tp, np.sin(2 * np.pi * np.cumsum(1500 + 900 * np.sin(np.pi * tt / d)) / SR) * np.hanning(len(tt)) * g)
def kaching(tp, g=0.3):
    d = 1.0; tt = T(d); put(fx, tp, (np.sin(2 * np.pi * 2093 * tt) + 0.6 * np.sin(2 * np.pi * 2637 * tt)) * np.exp(-tt * 5) * g); sfx(tp + 0.05, 'handleCoins', 0.8)
# 00.00 il comizio: applausi, flash, colpo d'orchestra sulla guerra
applausi(0.0, 2.3, 0.06)
for t_ in (0.3, 0.9, 1.4, 2.0, 2.5, 3.0, 3.7, 4.1): scatto(t_)
put(big, T_GUERRA - 0.02, colpo_orchestra(98.0, 1.0), 0.5); sfx(T_GUERRA + 0.05, 'impactWood_heavy_002', 0.9); put(big, T_GUERRA + 0.05, dun(55, 0.8), 0.35)
put(fx, T_IRAN - 0.08, whoosh(0.3, 1), 0.45)
# 4.56 il deserto: le pompe che cigolano a tempo
put(fx, T_CHE - 0.1, whoosh(0.5, 1), 0.4)
for k in range(9): cigolio(T_CHE + 0.15 + 0.33 * k, 0.05, 800 + 140 * (k % 3))
# 7.46 «ci hanno guardato storto»
sfx(T_STORTO - 0.05, 'scratch_003', 0.8); put(fx, T_STORTO + 0.3, boing(0.5, 200), 0.25)
# 9.74 i cannoni: cigolano, poi si girano tutti insieme
for k in range(6): sfx(T_PUNTA + 0.05 * k, 'creak%d' % (1 + k % 3), 0.5)
for k in range(6): sfx(T_PUNTA + 0.5 + 0.03 * k, 'impactMetal_medium_00%d' % (k % 5), 0.6)
bip(T_PUNTA + 0.75, 1760, 0.06, 0.12)
# 12.38 Rospina al guinzaglio: campanellino, squittio da giocattolo per cani; 14.92 a spasso: tacchi
for k in range(3): bip(T_ACCANTO + 0.6 + 0.12 * k, 2600 + 300 * k, 0.03, 0.08)
squittio(T_GUINZ + 0.25); squittio(T_GUINZ + 0.5, 0.1)
for k in range(12): sfx(T_SPASSO + 0.1 + 0.25 * k, 'footstep_concrete_00%d' % (k % 5), 0.35, vel=1.3)
# 18.08 la cosa più logica: record scratch; 20.10 lo yoga: gong
sfx(T_ALLORA - 0.05, 'scratch_001', 0.7)
gong(T_YOGA + 0.1)
# 22.30 la conquista: bandiera piantata; 23.82 trivella e pompa che impazzisce
sfx(T_CONQ + 0.85, 'impactWood_heavy_001', 0.8); put(big, T_CONQ + 0.85, dun(60, 0.5), 0.25)
trivella(T_TRIV, T_MA - T_TRIV - 0.02)
for k in range(5): cigolio(T_TRIV + 0.15 * k, 0.07, 1200)
# 24.66 «Ma il petrolio...»: silenzio vero, poi la grotta (gocce, il T-rex che russa)
for t_ in (25.0, 25.9, 26.7): goccia(t_)
russa(25.2, T_VIVO - 25.2)
# 27.34 l'occhio si apre: stacco drammatico; 28.48 «cazzo»: ruggito
put(big, T_VIVO - 0.4, stacco_drammatico(65.4, 1.6), 0.45)
ruggito(T_CAZZO - 0.05, 1.3, 0.5); put(big, T_CAZZO, boom(1.0, 60, 30), 0.4)
# 29.36 esce dal deserto: terremoto, boom, geyser di petrolio
put(big, T_TREX - 0.05, boom(2.2, 55, 24), 0.85); put(fx, T_TREX - 0.4, riser(0.4, 200, 900), 0.2); ruggito(T_TREX + 0.5, 1.4, 0.35)
geyser(T_TREX + 0.4, T_BEVE - T_TREX - 0.4)
# 31.16 si beve Cappellone: slurp lungo, «pop» finale
slurp(T_BEVE + 0.5, T_SUCCO + 0.55 - T_BEVE - 0.5); sfx(T_SUCCO + 0.6, 'drop_002', 1.0)
# 33.20 Rospina porge il guinzaglio: campanellino
for k in range(3): bip(T_PORGE + 0.4 + 0.12 * k, 2600 + 300 * k, 0.03, 0.08)
# 35.98 al distributore: la macchina spinta (ruote che strisciano)
for k in range(7): sfx(T_PIENO + 0.2 + 0.25 * k, 'footstep_concrete_00%d' % (k % 5), 0.3)
# 37.90 spunta il T-rex benzinaio; 39.50 «800 euro»: registratore di cassa
put(fx, T_BENZ - 0.2, whoosh(0.4, 1), 0.4); put(big, T_BENZ + 0.2, dun(50, 0.8), 0.3)
kaching(T_800 + 0.05)
# 40.90 «porca puttana»: ruote che saltano, Tumbo che sviene
put(big, T_PORCA + 0.05, boom(0.7, 80, 40), 0.35)
for k in range(4): put(fx, T_PORCA + 0.15 + 0.12 * k, boing(0.45, 180 + 40 * k), 0.22)
sfx(T_PORCA + 0.35, 'impactSoft_heavy_001', 0.6)
# 42.02 il rutto del T-rex, il casco vola e atterra sulla testa di Pippo
rutto(T_TEAM + 0.1, 1.0, 0.5); put(fx, T_TEAM + 0.35, whoosh(0.7, 1), 0.35); sfx(T_TEAM + 1.15, 'impactPlate_light_000', 0.9); put(fx, T_TEAM + 1.17, boing(0.5, 300), 0.25)
sfx(T_END + 0.1, 'drop_001', 0.9)

# ---------- mix con limitatore ----------
out = v * 1.0 + mus + np.tanh(fx * 1.1) * 0.45 + big * 0.5
out *= env(0, T_END + 0.45, 0.002, 0.04)
h = 256; pk = np.abs(out[:N // h * h]).reshape(-1, h).max(1)
g = np.minimum(1.0, 0.95 / np.maximum(pk, 1e-6)); g = np.minimum(g, np.concatenate([g[1:], g[-1:]])); g = np.convolve(g, np.ones(9) / 9, mode='same')
gg = np.interp(np.arange(N), np.arange(len(g)) * h + h / 2, g); out = np.clip(out * gg, -0.99, 0.99)
ww = wave.open('audio/t029.wav', 'w'); ww.setnchannels(1); ww.setsampwidth(2); ww.setframerate(SR); ww.writeframes((out * 32767).astype(np.int16).tobytes()); ww.close()
def rms(x, a, b): return float(np.sqrt(np.mean(x[int(a * SR):int(b * SR)] ** 2)))
print('audio/t029.wav', DUR, 's  riduzione massima del limitatore %.2f' % float(gg.min()))
for nome, a, b in (('comizio', 0, 4.5), ('deserto', 4.6, 7.4), ('cannoni', 9.7, 12.3), ('guinzaglio', 12.4, 18.0), ('yoga', 18.1, 22.2), ('conquista', 22.3, 24.6), ('grotta', 24.7, 27.3), ('trex', 29.4, 35.9), ('benzina', 36.0, 44.5)):
    print('%-10s voce %.3f  musica %.3f  effetti %.3f  impatti %.3f' % (nome, rms(v, a, b), rms(mus, a, b), rms(np.tanh(fx * 1.1) * 0.45, a, b), rms(big * 0.5, a, b)))
