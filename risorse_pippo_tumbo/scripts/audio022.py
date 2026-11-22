"""Video 022 (Il barattolo di cetriolini) - audio con la SOUND DESIGN TIMELINE (regole in SOUND_DESIGN.md, timeline del copione n. 15). Esce audio/t022.wav (49.6 s).
Le quattro famiglie musicali (Kevin MacLeod, CC-BY 4.0, da citare nella descrizione), come nel copione:
  EPICO = «Strength of the Titans»   COMICO = «Sneaky Snitch»   SUSPENSE = «Spy Glass»   CAOS = «Galactic Rap»
Effetti: Kenney (CC0), il kit Mixkit (audio/sfx/mixkit) e quelli costruiti qui (boom, bass drop, riser, whoosh, boing, moto del prete,
cingoli, sonar, razzi, sirena, spruzzo, sgonfiata, campane, organo, bacio, carillon, «pof»).
Uso, dalla cartella del progetto: python scripts/audio022.py"""
import sys, os, subprocess, wave
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import suoni as S
SR = 44100; DUR = 49.6; N = int(DUR * SR); rng = np.random.default_rng(22)

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


def sciacquone(d=1.6):
    """lo sciacquone: scroscio d'acqua che gira e scende, gorgoglio, risucchio finale"""
    t = T(d); n = rng.normal(0, 1, len(t)); fc = 2600 * np.exp(-t * 1.1) + 300
    scro = passa_basso(n, 2400) * (0.6 + 0.4 * np.sin(2 * np.pi * (5 - 2 * t / d) * t)) * np.minimum(1, t * 12) * np.exp(-np.maximum(0, t - d * 0.6) * 4)
    gor = np.zeros(len(t))
    for k in range(18):
        tk = rng.uniform(0.1, d - 0.15); f = rng.uniform(250, 650); s_ = osc(f * (1 + 2 * T(0.06)), T(0.06)) * np.hanning(int(0.06 * SR)); i = int(tk * SR); gor[i:i + len(s_)] += s_[:len(gor) - i] * 0.35
    ris = osc(140 + 300 * np.exp(-T(0.4) * 6), T(0.4)) * np.hanning(int(0.4 * SR)) * 0.5; i = int((d - 0.45) * SR); gor[i:i + len(ris)] += ris[:len(gor) - i]
    return (scro * 0.9 + gor) * 0.8
def cigolio(d=1.0, f=420):
    """cigolio metallico (coperchio del cranio, porta blindata)"""
    t = T(d); fr_ = f * (1 + 0.25 * np.sin(2 * np.pi * 1.3 * t) + 0.08 * np.sin(2 * np.pi * 23 * t))
    return (saw(fr_, t) * 0.5 + osc(fr_ * 2.01, t) * 0.3) * np.hanning(len(t)) * (0.6 + 0.4 * (rng.random(len(t)) > 0.5))
def servo(d=0.35, f=900):
    t = T(d); return (saw(f * (1 + 0.2 * t / d), t) * 0.3 + osc(f * 2, t) * 0.2) * np.hanning(len(t))
def sbuffo(d=0.35):
    t = T(d); return passa_alto(rng.normal(0, 1, len(t)), 3000) * np.exp(-t * 7) * np.minimum(1, t * 80)
def vocina(f0=900, d=0.5):
    """due «ciao» minuscoli senza parole (le Giulie che si salutano)"""
    t = T(d); f = f0 * (1 + 0.3 * np.sin(2 * np.pi * 7 * t)) * (1 + 0.2 * (t / d)); return np.tanh(saw(f, t) * 0.6) * passa_basso(np.ones(len(t)), 4000)[:len(t)] * np.hanning(len(t)) * 0.4


# ---------- effetti nuovi del 019 ----------
def moto_rombo(d=1.2, giri=1.0):
    """rombo della moto del prete: due sgasate che sembrano una risata"""
    t = T(d); rpm = 38 + 55 * giri * (np.abs(np.sin(2 * np.pi * 1.6 * t)) ** 2) * np.minimum(1, t * 6)
    x = saw(rpm, t) * 0.6 + saw(rpm * 2.02, t) * 0.25 + passa_basso(rng.normal(0, 1, len(t)), 900) * 0.25
    return np.tanh(passa_basso(x, 1800) * 2.0) * np.minimum(1, t * 20) * np.minimum(1, (d - t) * 6)
def cingoli(d):
    t = T(d); x = passa_basso(rng.normal(0, 1, len(t)), 140) * 3.0 + 0.4 * saw(32 + 3 * np.sin(t * 2), t)
    cl = np.zeros(len(t))
    for tk in np.arange(0, d - 0.05, 0.11):
        i = int(tk * SR); s_ = passa_alto(rng.normal(0, 1, int(0.03 * SR)), 1500) * np.hanning(int(0.03 * SR)); cl[i:i + len(s_)] += s_[:len(cl) - i] * 0.5
    return np.tanh((x + cl) * 0.8) * np.minimum(1, t * 3) * np.minimum(1, (d - t) * 3)
def sonar(f=1250, d=1.2):
    t = T(d); return osc(f, t) * np.exp(-t * 3.2) * np.minimum(1, t * 300)
def razzo(d):
    t = T(d); x = passa_basso(rng.normal(0, 1, len(t)), 420) * 2.5 + passa_alto(rng.normal(0, 1, len(t)), 3000) * 0.25
    return np.tanh(x * np.minimum(1, t * 2.5)) * np.minimum(1, (d - t) * 4)
def sirena(d, g=1.0):
    t = T(d); f = 600 + 350 * np.sin(2 * np.pi * 0.55 * t); return osc(f, t) * 0.5 * np.minimum(1, t * 4) * np.minimum(1, (d - t) * 4) * g
def spruzzo(d):
    t = T(d); n = passa_alto(rng.normal(0, 1, len(t)), 1800) * (0.7 + 0.3 * np.sin(2 * np.pi * 9 * t)); return n * np.minimum(1, t * 30) * np.minimum(1, (d - t) * 10) * 0.6
def sgonfiata(d=0.9):
    """pfffff della pallina bucata: aria che esce e fischia scendendo"""
    t = T(d); n = passa_alto(rng.normal(0, 1, len(t)), 2500) * np.exp(-t * 1.5); w = osc(900 * np.exp(-t * 1.6) + 120, t) * 0.25 * np.exp(-t * 2)
    return (n * 0.7 + w) * np.minimum(1, t * 40)
def campane(d=1.6):
    x = np.zeros(int(d * SR))
    for k, (tk, f) in enumerate(((0.0, 784), (0.18, 988), (0.36, 1175), (0.54, 988), (0.72, 1568), (0.9, 1175))):
        t = T(d - tk); s_ = (osc(f, t) + 0.5 * osc(f * 2.76, t) + 0.3 * osc(f * 5.4, t)) * np.exp(-t * 3.0); i = int(tk * SR); x[i:i + len(s_)] += s_[:len(x) - i] * 0.35
    return x
def organo(root=130.8, d=1.6):
    t = T(d); x = sum(osc(root * r, t) * a for r, a in ((1, 1), (2, 0.6), (3, 0.3), (4, 0.25), (1.5, 0.5), (1.26, 0.4)))
    return x / 3 * np.minimum(1, t * 8) * np.minimum(1, (d - t) * 3)
def bacio(d=0.22):
    t = T(d); return (passa_alto(rng.normal(0, 1, len(t)), 1200) * np.exp(-t * 40) + osc(520 * np.exp(-t * 8), t) * np.exp(-t * 18)) * 0.8
def carillon(d, inceppa=None):
    note = [1047, 1319, 1568, 1319, 1175, 1397, 1760, 1397, 1047, 1319, 1568, 2093]
    x = np.zeros(int(d * SR)); k = 0
    for tk in np.arange(0, d - 0.05, 0.3):
        if inceppa is not None and tk > inceppa: break
        t = T(min(0.8, d - tk)); f = note[k % len(note)]; s_ = (osc(f, t) + 0.3 * osc(f * 3.0, t)) * np.exp(-t * 4.5)
        i = int(tk * SR); x[i:i + len(s_)] += s_[:len(x) - i] * 0.35; k += 1
    return x
def pof(d=0.35):
    t = T(d); return (passa_basso(rng.normal(0, 1, len(t)), 700) * 1.8 + osc(140 * np.exp(-t * 6), t)) * np.exp(-t * 14) * np.minimum(1, t * 400)
def fischio_bomba(d, f0=1800, f1=500):
    t = T(d); u = t / d; return osc(f0 * (f1 / f0) ** u, t) * np.minimum(1, t * 6) * 0.5
def yeehaw():
    """«iiih-ha» da rodeo, sintetico e senza parole"""
    t = T(0.75); f = np.where(t < 0.35, 650 + 900 * t / 0.35, 900 - 500 * (t - 0.35) / 0.4); return np.tanh(saw(f, t) * 0.8) * np.hanning(len(t)) * 0.35


def tromba_elefante(d=0.9):
    """barrito sintetico: tromba che sale e gracchia"""
    t = T(d); f = 300 + 500 * np.minimum(1, t / 0.25) - 150 * np.maximum(0, t - 0.5)
    return np.tanh(saw(f * (1 + 0.03 * np.sin(2 * np.pi * 28 * t)), t) * 1.5) * np.minimum(1, t * 30) * np.minimum(1, (d - t) * 6) * 0.5
def fischio_caduta(d, f0=2200, f1=400):
    t = T(d); return osc(f0 * (f1 / f0) ** (t / d), t) * 0.5 * np.minimum(1, t * 10)
def clacson(d=0.5):
    t = T(d); return np.tanh((saw(340, t) + saw(427, t)) * 0.8) * np.minimum(1, t * 50) * np.minimum(1, (d - t) * 30) * 0.5
def motore(d):
    t = T(d); return np.tanh((saw(55 + 8 * np.sin(t * 7), t) * 0.6 + passa_basso(rng.normal(0, 1, len(t)), 300) * 0.8) * 1.2) * np.minimum(1, t * 4) * np.minimum(1, (d - t) * 4)
def cigolio_vetro(d=0.5, f=1800):
    t = T(d); fr_ = f * (1 + 0.15 * np.sin(2 * np.pi * 9 * t)); return (osc(fr_, t) * 0.4 + osc(fr_ * 1.5, t) * 0.2) * np.hanning(len(t))
def violino(d=2.5, f=659.3):
    t = T(d); x = sum(saw(f * r * (1 + 0.006 * np.sin(2 * np.pi * 5.5 * t)), t) * a for r, a in ((1, 1), (1.26, 0.6), (1.5, 0.5)))
    return passa_basso(x, 3000) / 3 * np.minimum(1, t * 3) * np.minimum(1, (d - t) * 2)
def conto_rovescia():
    x = np.zeros(int(3.0 * SR))
    for k in range(4): s_ = osc(880 if k < 3 else 1320, T(0.12)) * np.hanning(int(0.12 * SR)); i = int(k * 0.8 * SR); x[i:i + len(s_)] += s_ * 0.5
    return x

# ---------- voce ----------
subprocess.run([S.FFMPEG, '-y', '-loglevel', 'error', '-i', 'audio/voce_t022.mp3', '-ar', str(SR), '-ac', '1', 'audio/voce44_t022.wav'], check=True)
w = wave.open('audio/voce44_t022.wav'); v = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(float) / 32768; v = np.pad(v, (0, max(0, N - len(v))))[:N]
_loc = np.sqrt(lp(v ** 2, int(0.35 * SR))); v = v * lp(np.clip(0.115 / (_loc + 0.03), 0.9, 3.0), int(0.25 * SR))
venv = lp(np.abs(v), int(0.12 * SR)); venv = np.clip(venv / (np.percentile(venv, 95) + 1e-9), 0, 1)

# ---------- tempi (gli stessi di anim022_body.py) ----------
T_LIFT0 = 4.6; T_PERCHE = 7.16; T_MANI = 11.46; T_DENTI = 13.70; T_MART = 16.76; T_CAMION = 18.44; T_ELEF = 19.62; T_NIENTE = 22.2
T_ALLORA = 23.2; T_RAZZO = 24.28; T_POI = 25.98; T_SVITA = 28.38; T_SOLO = 29.74; T_MACHE = 31.34; T_DENTRO = 33.0; T_MUTANDE = 34.92
T_AMANTE = 37.04; T_QUEL = 40.3; T_CHIUDE = 43.02; T_STAVOLTA = 44.38; T_FINE = 48.9

# ---------- musica ----------
def traccia(rel, inizio=None, cerca=(0, 100), finestra=8.0):
    x = S.carica('musica/' + rel, SR)
    if inizio is None:
        h = int(SR * 0.5); r = np.sqrt(lp(x ** 2, int(finestra * SR))[::h]); a, b = int(cerca[0] * 2), min(len(r), int(cerca[1] * 2))
        inizio = max(0.0, (a + int(np.argmax(r[a:b]))) * 0.5 - finestra / 2)
    y = x[int(inizio * SR):]; y = y / (np.sqrt(np.mean(y[:int(20 * SR)] ** 2)) + 1e-9) * 0.1; return y, inizio
def stendi(buf, x, t0, t1, g, fi=0.05, fo=0.05, da=0.0):
    seg = np.zeros(N); i0 = int(t0 * SR); s = x[int(da * SR):int(da * SR) + (N - i0)]; seg[i0:i0 + len(s)] = s; buf += seg * env(t0, t1, fi, fo) * g; return seg
EPICO, i_e = traccia('epica/Strength_of_the_Titans', cerca=(10, 120))
COMICO, i_c = traccia('comica/Sneaky_Snitch', inizio=0.5)
SUSPENSE, i_s = traccia('suspense/Spy_Glass', cerca=(5, 90))
CAOS, i_k = traccia('suspense/Galactic_Rap', cerca=(20, 120))
print('inizi dei brani (s): epico %.1f, suspense %.1f, caos %.1f' % (i_e, i_s, i_k))

mus = np.zeros(N)
# 00.00 EPICO subito: il razzo col barattolo. 7.0 tape stop: si torna indietro
ep = np.zeros(N); stendi(ep, EPICO, 0.0, 7.8, 1.0, 0.005, 0.02); tape_stop(ep, T_PERCHE - 0.15, 0.55); mus += ep * 0.22
# 07.3 COMICO basso: il barattolo che non si apre, sempre piu' veloce. Si ferma su «niente»
co = np.zeros(N); stendi(co, COMICO, T_PERCHE + 0.15, T_NIENTE - 0.02, 1.0, 0.3, 0.03); mus += co * 0.12 * ramp(T_PERCHE, T_NIENTE, 0.9, 1.3)
# 23.2 EPICO al massimo: RAZZO. Si ferma quando il barattolo ricade
ep2 = np.zeros(N); stendi(ep2, EPICO, T_ALLORA - 0.02, T_POI + 0.4, 1.0, 0.02, 0.05, da=12.0); mus += ep2 * 0.26
# 28.38 SUSPENSE: il coperchio si svita da solo. Record scratch su «Ma che cazzo»
su_ = np.zeros(N); stendi(su_, SUSPENSE, T_SVITA - 0.1, T_MACHE - 0.05, 1.0, 0.4, 0.02); mus += su_ * 0.13
# 33.0 suspense piu' bassa sul cetriolino; 37.0 CAOS sull'amante, stop secco quando il coperchio si chiude
su2 = np.zeros(N); stendi(su2, SUSPENSE, T_DENTRO, T_AMANTE - 0.05, 1.0, 0.2, 0.05, da=6.0); mus += su2 * 0.1
ca = np.zeros(N); stendi(ca, CAOS, T_AMANTE + 0.5, T_CHIUDE + 0.4, 1.0, 0.02, 0.02); mus += ca * 0.18
mus *= (1 - 0.45 * venv) * 2.1

# ---------- effetti ----------
fx = np.zeros(N); big = np.zeros(N)
def sfx(tp, nome, g=1.0, vel=1.0):
    x = S.carica(nome, SR, volume=g)
    if vel != 1.0: x = np.interp(np.arange(0, len(x), vel), np.arange(len(x)), x)
    put(fx, tp, x)

# 00.00 HOOK: conto alla rovescia, il razzo vibra, decollo
put(fx, 0.3, conto_rovescia(), 0.35); put(fx, 1.0, riser(T_LIFT0 - 1.0, 150, 900), 0.12)
put(fx, T_LIFT0 - 0.6, razzo(T_PERCHE - T_LIFT0 + 0.4), 0.6); put(big, T_LIFT0, boom(1.8, 55, 28), 0.5)
# 07.16 si torna indietro
put(fx, T_PERCHE - 0.2, whoosh(0.5, -1), 0.5); sfx(T_PERCHE, 'mk_Vacuum_swoosh_transition', 0.35)
# cucina: sforzo sul vetro, il cigolio minuscolo del coperchio tenuto da dentro (indizio)
for k in range(5): put(fx, T_PERCHE + 0.6 + k * 0.7, cigolio_vetro(0.35, 1500 + 150 * k), 0.12)
put(fx, 8.2, cigolio_vetro(0.3, 2600), 0.16); put(fx, 12.2, cigolio_vetro(0.3, 2700), 0.16)
# 13.7 i denti di Tumbo; l'elica
sfx(T_DENTI + 0.3, 'mk_Soft_quick_punch', 0.5)
for k in range(8): put(fx, T_DENTI + 0.6 + k * 0.33, whoosh(0.3, 1), 0.3)
# 16.76 martellate sul vetro (tink, il vetro resiste)
for k in range(4): sfx(T_MART + 0.25 + k / 3.2, 'impactMetal_medium_00%d' % (k % 5), 0.55); put(fx, T_MART + 0.27 + k / 3.2, osc(3100, T(0.25)) * np.exp(-T(0.25) * 14), 0.15)
# 18.44 il camion: motore, clacson, sobbalzo sul barattolo
put(fx, T_CAMION - 0.1, motore(1.3), 0.5); put(fx, T_CAMION + 0.1, clacson(0.45), 0.4); put(big, T_CAMION + 0.55, dun(55, 0.6), 0.35)
# 19.62 l'elefante piove dal cielo: fischio, tonfo enorme, boing, barrito
put(fx, T_ELEF - 0.3, fischio_caduta(0.75), 0.35); put(big, T_ELEF + 0.48, boom(1.6, 60, 28), 0.7); put(fx, T_ELEF + 0.6, boing(0.6, 160), 0.35)
put(fx, T_ELEF + 1.2, tromba_elefante(0.9), 0.5)
# 22.2 «niente»: stop, tink del barattolo intatto
put(fx, T_NIENTE + 0.1, osc(3300, T(0.4)) * np.exp(-T(0.4) * 9), 0.2)
# 23.2 RAZZO: colpo d'orchestra, decollo
put(fx, T_RAZZO - 0.6, razzo(T_POI - T_RAZZO + 0.4), 0.6); put(big, T_RAZZO, colpo_orchestra(98), 0.55); put(big, T_RAZZO + 0.02, boom(1.6, 55, 28), 0.45)
# 25.98 il barattolo ricade: fischio e tonfo nel prato; poi silenzio
put(fx, T_POI - 0.05, fischio_caduta(0.45, 1800, 500), 0.35); put(big, T_POI + 0.4, boom(0.9, 75, 40), 0.5); sfx(T_POI + 0.42, 'impactPunch_heavy_002', 0.5)
# 28.38 il coperchio si svita da solo: cigolio lungo e battito
put(fx, T_SVITA + 0.05, cigolio(1.4, 340), 0.3); sfx(T_SVITA + 0.3, 'mk_Deep_heartbeat_impact', 0.45); sfx(T_SOLO + 0.15, 'impactMetal_light_002', 0.6)
# 31.34 «Ma che cazzo»: record scratch. 33.0 il cetriolino esce e si stiracchia
sfx(T_MACHE - 0.15, 'mk_Record_player_vinyl_scratch', 0.7); sfx(T_DENTRO + 0.1, 'mk_Long_pop', 0.5); put(fx, T_DENTRO + 0.7, vocina(500, 0.7), 0.3)
# 34.9 salta fuori: boing; mutande a cuori: fischio d'ammirazione
put(fx, T_MUTANDE - 0.25, boing(0.45, 330), 0.3); put(fx, T_MUTANDE + 0.4, fischio_bomba(0.6, 900, 1900), 0.18)
# 37.04 l'amante di Eleonora: stacco drammatico, violino romantico, poi il caos
put(big, T_AMANTE - 0.05, stacco_drammatico(73.4, 1.6), 0.4); put(fx, T_AMANTE + 0.4, violino(2.6), 0.12)
# 40.3 Pippo entra nel barattolo: salto, rimpicciolisce (whoosh che sale), il coperchio torna e si avvita: tre giri
put(fx, T_QUEL + 0.6, whoosh(0.6, 1), 0.4); put(fx, T_QUEL + 0.7, riser(0.6, 400, 1600), 0.12)
for k in range(3): put(fx, T_CHIUDE - 0.6 + k * 0.3, cigolio_vetro(0.25, 1200 - 100 * k), 0.25)
sfx(T_CHIUDE + 0.3, 'mk_Hard_pop_click', 0.6)
# 44.38 Tumbo morde il coperchio: denti sul vetro, poi niente
for k in range(6): put(fx, T_STAVOLTA + 0.2 + k * 0.45, cigolio_vetro(0.2, 3000 + 200 * (k % 2)), 0.12)
put(fx, T_FINE + 0.05, pof(), 0.5)

# ---------- mix con limitatore ----------
out = v * 1.0 + mus + np.tanh(fx * 1.1) * 0.45 + big * 0.5
h = 256; pk = np.abs(out[:N // h * h]).reshape(-1, h).max(1)
g = np.minimum(1.0, 0.95 / np.maximum(pk, 1e-6)); g = np.minimum(g, np.concatenate([g[1:], g[-1:]])); g = np.convolve(g, np.ones(9) / 9, mode='same')
gg = np.interp(np.arange(N), np.arange(len(g)) * h + h / 2, g); out = np.clip(out * gg, -0.99, 0.99)
ww = wave.open('audio/t022.wav', 'w'); ww.setnchannels(1); ww.setsampwidth(2); ww.setframerate(SR); ww.writeframes((out * 32767).astype(np.int16).tobytes()); ww.close()
print('audio/t022.wav', DUR, 's  riduzione massima del limitatore %.2f' % float(gg.min()))
