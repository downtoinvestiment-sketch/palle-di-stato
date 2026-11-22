"""Video 025 (Martina nel water) - audio con la SOUND DESIGN TIMELINE del copione n. 22 v4, rifatta sui tempi veri della voce.
Le famiglie musicali di Pippo e Tumbo (Kevin MacLeod, CC-BY 4.0, vanno citati nella descrizione):
  COMICO = «Scheming Weasel (faster)»   EPICO = «Heroic Age»   CAOS = «Hall of the Mountain King»
Effetti della libreria (Kenney, CC0) + effetti costruiti in numpy (sciacquone, schizzi, bolle, frase di tango a fisarmonica,
barrito, getto, alluvione, ruggito da scarafaggio gigante, SCIAF, applauso).
Uso, dalla cartella del progetto: python scripts/audio025.py"""
import sys, os, subprocess, wave
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import suoni as S
SR = 44100; DUR = 37.4; N = int(DUR * SR); rng = np.random.default_rng(25)

# ---------- strumenti (gli stessi del 021) ----------
def env(a, b, fi=0.1, fo=0.3):
    e = np.zeros(N); i0, i1 = max(0, int(a * SR)), min(N, int(b * SR)); n = i1 - i0
    if n <= 0: return e
    x = np.ones(n); fi_n = max(1, min(n // 2, int(fi * SR))); fo_n = max(1, min(n // 2, int(fo * SR)))
    x[:fi_n] = np.linspace(0, 1, fi_n); x[n - fo_n:] = np.linspace(1, 0, fo_n); e[i0:i1] = x; return e
def ramp(a, b, v0=0.0, v1=1.0):
    t = np.arange(N) / SR; return v0 + (v1 - v0) * np.clip((t - a) / (b - a), 0, 1)
def lp(x, k):
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
def boom(d=1.8, f0=64, f1=30):
    t = T(d); f = f1 + (f0 - f1) * np.exp(-t * 5); x = osc(f, t) * np.exp(-t * 2.0) + 0.6 * passa_basso(rng.normal(0, 1, len(t)), 500) * np.exp(-t * 8)
    c = int(0.004 * SR); x[:c] += np.linspace(1.2, 0, c); return np.tanh(x * 1.7)
def riser(d, f0=170, f1=1500):
    t = T(d); u = t / d; n = passa_alto(rng.normal(0, 1, len(t)), 2200) * u ** 2.4 * 0.5
    f = f0 * (f1 / f0) ** u; return n + osc(f, t) * u ** 1.7 * 0.45 + osc(f * 1.5, t) * u ** 2.3 * 0.22
def whoosh(d=0.45, verso=1):
    t = T(d); n = rng.normal(0, 1, len(t)); u = t / d if verso > 0 else 1 - t / d
    return (passa_basso(n, 600) * 2.2 * (1 - u) + passa_basso(n, 3200) * u) * np.hanning(len(t))
def boing(d=0.55, f=230):
    t = T(d); fr = f * (1 + 0.3 * np.exp(-t * 4) * np.sin(2 * np.pi * 15 * t)) * (1 + 0.3 * np.exp(-t * 3)); return osc(fr, t) * np.exp(-t * 4.5)
def grilli(d):
    x = np.zeros(int(d * SR))
    for c in np.arange(0.05, d - 0.2, 0.62):
        for k in range(3):
            s_ = np.sin(2 * np.pi * 4400 * T(0.035)) * np.hanning(int(0.035 * SR)); i = int((c + k * 0.06) * SR); x[i:i + len(s_)] += s_[:len(x) - i]
    return x
def colpo_orchestra(root=146.8, d=0.9):
    t = T(d); x = sum(saw(root * r, t) for r in (1, 1.5, 2, 2.52, 3)) / 4
    x = passa_basso(x, 2600) * np.minimum(1, t * 200) * np.exp(-t * 4.5); y = boom(d, 70, 40)[:len(t)] * 0.7; return np.tanh((x + y) * 1.5)
def dun(root=55.0, d=0.9):
    t = T(d); return np.tanh((osc(root, t) + 0.5 * osc(root * 2, t) + 0.25 * saw(root, t)) * np.exp(-t * 3.5) * 1.6)
def tape_stop(x, t0, d=0.6):
    i0 = int(t0 * SR); n = int(d * SR); seg = x[i0:i0 + 3 * n].copy()
    if len(seg) < 3 * n: seg = np.pad(seg, (0, 3 * n - len(seg)))
    pos = np.cumsum(np.linspace(1, 0, n)); y = np.interp(pos, np.arange(len(seg)), seg) * np.linspace(1, 0.2, n)
    x[i0:i0 + n] = y[:len(x) - i0]; x[i0 + n:] = 0

# ---------- effetti nuovi ----------
def violino(note, dur_nota=0.55, base=659.25):
    """melodia da film d'amore: sega con vibrato, filtrata, con un po' di riverbero."""
    x = np.zeros(int((len(note) * dur_nota + 1.2) * SR))
    for k, n_ in enumerate(note):
        if n_ is None: continue
        d = dur_nota * 1.35; tt = T(d); f = base * 2 ** (n_ / 12) * (1 + 0.006 * np.sin(2 * np.pi * 5.6 * tt) * np.minimum(1, tt * 3))
        s_ = (saw(f, tt) * 0.6 + saw(f * 2.002, tt) * 0.15) * np.minimum(1, tt * 7) * np.minimum(1, (d - tt) * 5)
        i = int(k * dur_nota * SR); x[i:i + len(s_)] += passa_basso(s_, 3400)[:len(x) - i]
    rv = np.zeros_like(x)
    for dl, g in ((0.031, 0.5), (0.047, 0.4), (0.071, 0.3), (0.113, 0.22)):
        k = int(dl * SR); rv[k:] += x[:-k] * g
    return passa_alto(x + rv * 0.6, 180)
def record_scratch(d=0.42):
    tt = T(d); f = 900 * np.exp(-tt * 6) + 120 + 300 * np.sin(2 * np.pi * 14 * tt) * np.exp(-tt * 4)
    s_ = np.sign(osc(f, tt)) * 0.5 + passa_alto(rng.normal(0, 1, len(tt)), 1500) * 0.6
    return np.tanh(passa_basso(s_, 4500) * np.minimum(1, tt * 80) * np.exp(-tt * 3) * 1.6)
def fiuuu(d=0.7, f0=1500, f1=260):
    tt = T(d); u = tt / d; f = f0 * (f1 / f0) ** u * (1 + 0.04 * np.sin(2 * np.pi * 9 * tt) * (1 - u)); return osc(f, tt) * np.hanning(len(tt))
def clacson(d=0.45, f=420):
    tt = T(d); s_ = (np.sign(osc(f, tt)) + np.sign(osc(f * 1.26, tt))) * 0.5
    return passa_basso(s_, 2400) * np.minimum(1, tt * 60) * np.minimum(1, (d - tt) * 30)
def bip(tp, freq, g=0.09, d=0.09): n = int(d * SR); put(fx, tp, np.sin(2 * np.pi * freq * T(d)) * np.hanning(n) * g * 2)
def motore(d, f=42.0, rumore=1.0):
    tt = T(d); x = (osc(f * (1 + 0.03 * np.sin(2 * np.pi * 0.9 * tt)), tt) + 0.5 * np.sign(osc(f * 2, tt)) * 0.4)
    x = x * (0.75 + 0.25 * np.sin(2 * np.pi * f / 3 * tt)) + passa_basso(rng.normal(0, 1, len(tt)), 300) * 1.4 * rumore
    return passa_basso(x, 900)
def ting(f=2900.0, d=0.22):
    tt = T(d); return sum(np.sin(2 * np.pi * f * r * tt) * np.exp(-tt * (18 + 8 * k)) / (k + 1) for k, r in enumerate((1.0, 1.47, 2.13, 2.9)))
def cinguettio(d=0.16, f0=2600, f1=4100):
    tt = T(d); return osc(np.linspace(f0, f1, len(tt)), tt) * np.hanning(len(tt))
def gonfia(d=0.5):
    tt = T(d); u = tt / d; return osc(320 * (1400 / 320) ** u, tt) * (0.3 + 0.7 * u) * 0.6 + passa_alto(rng.normal(0, 1, len(tt)), 2500) * 0.25 * np.hanning(len(tt))
def xilofono(note, dt=0.3, base=523.25):
    x = np.zeros(int((len(note) * dt + 1.0) * SR))
    for k, n_ in enumerate(note):
        if n_ is None: continue
        f = base * 2 ** (n_ / 12); tt = T(0.7); s_ = (np.sin(2 * np.pi * f * tt) + 0.25 * np.sin(2 * np.pi * 3.93 * f * tt) * np.exp(-tt * 30)) * np.exp(-tt * 7)
        i = int(k * dt * SR); x[i:i + len(s_)] += s_[:len(x) - i]
    return x
def crack(d=0.35):
    tt = T(d); return passa_alto(rng.normal(0, 1, len(tt)), 1800) * np.exp(-tt * 14) + osc(180 * np.exp(-tt * 5), tt) * np.exp(-tt * 9) * 0.6


# ---------- effetti del 025 ----------
def record_scratch(d=0.42):
    tt = T(d); f = 900 * np.exp(-tt * 6) + 120 + 300 * np.sin(2 * np.pi * 14 * tt) * np.exp(-tt * 4)
    s_ = np.sign(osc(f, tt)) * 0.5 + passa_alto(rng.normal(0, 1, len(tt)), 1500) * 0.6
    return np.tanh(passa_basso(s_, 4500) * np.minimum(1, tt * 80) * np.exp(-tt * 3) * 1.6)
def ting(f=2900.0, d=0.22):
    tt = T(d); return sum(np.sin(2 * np.pi * f * r * tt) * np.exp(-tt * (18 + 8 * k)) / (k + 1) for k, r in enumerate((1.0, 1.47, 2.13, 2.9)))
def crack(d=0.35):
    tt = T(d); return passa_alto(rng.normal(0, 1, len(tt)), 1800) * np.exp(-tt * 14) + osc(180 * np.exp(-tt * 5), tt) * np.exp(-tt * 9) * 0.6
def fischio(d, f0=2200, f1=400):
    tt = T(d); return osc(f0 * (f1 / f0) ** (tt / d), tt) * 0.5 * np.minimum(1, tt * 10) * np.minimum(1, (d - tt) * 20)
def sciacquone(d=1.6):
    """scroscio d'acqua che gira e scende, gorgoglio, risucchio finale"""
    t_ = T(d); n = rng.normal(0, 1, len(t_))
    scro = passa_basso(n, 2400) * (0.6 + 0.4 * np.sin(2 * np.pi * (5 - 2 * t_ / d) * t_)) * np.minimum(1, t_ * 12) * np.exp(-np.maximum(0, t_ - d * 0.6) * 4)
    gor = np.zeros(len(t_))
    for k in range(22):
        tk = rng.uniform(0.1, d - 0.15); f = rng.uniform(250, 650); s_ = osc(f * (1 + 2 * T(0.06)), T(0.06)) * np.hanning(int(0.06 * SR)); i = int(tk * SR); gor[i:i + len(s_)] += s_[:len(gor) - i] * 0.35
    ris = osc(140 + 300 * np.exp(-T(0.4) * 6), T(0.4)) * np.hanning(int(0.4 * SR)) * 0.5; i = int((d - 0.45) * SR); gor[i:i + len(ris)] += ris[:len(gor) - i]
    return (scro * 0.9 + gor) * 0.8
def bolle(d, n=14, f0=220, f1=700):
    x = np.zeros(int(d * SR))
    for k in range(n):
        tk = rng.uniform(0, max(0.01, d - 0.1)); f = rng.uniform(f0, f1); dd = rng.uniform(0.04, 0.09)
        s_ = osc(f * (1 + 3 * T(dd) / dd), T(dd)) * np.hanning(int(dd * SR)); i = int(tk * SR); x[i:i + len(s_)] += s_[:len(x) - i] * rng.uniform(0.4, 1.0)
    return x
def sciabordio(d):
    t_ = T(d); n = passa_basso(rng.normal(0, 1, len(t_)), 900); return n * (0.5 + 0.5 * np.sin(2 * np.pi * 0.9 * t_) ** 2) * 1.5
def cannuccia(d=0.5):
    """risucchio con la cannuccia: gorgoglio che sale"""
    t_ = T(d); f = 300 + 500 * t_ / d; return (np.sign(osc(f * (1 + 0.3 * np.sin(2 * np.pi * 38 * t_)), t_)) * 0.3 + passa_alto(rng.normal(0, 1, len(t_)), 1800) * 0.4) * np.hanning(len(t_)) * 0.5
def schizzo(d=0.6, fc=2600):
    t_ = T(d); return passa_basso(passa_alto(rng.normal(0, 1, len(t_)), 350), fc) * np.exp(-t_ * 6) * np.minimum(1, t_ * 200) * 1.2
def plop(d=0.25):
    t_ = T(d); return osc(900 * np.exp(-t_ * 18) + 160, t_) * np.exp(-t_ * 14) + passa_basso(rng.normal(0, 1, len(t_)), 1200) * np.exp(-t_ * 30) * 0.3
def rotelline(d):
    t_ = T(d); x = passa_basso(rng.normal(0, 1, len(t_)), 1500) * 0.4
    for tk in np.arange(0, d, 0.07): i = int(tk * SR); s_ = passa_alto(rng.normal(0, 1, int(0.012 * SR)), 2500) * np.hanning(int(0.012 * SR)); x[i:i + len(s_)] += s_[:len(x) - i] * 0.6
    return x * np.minimum(1, t_ * 10) * np.minimum(1, (d - t_) * 10)
def rullo_tamburo(d):
    x = np.zeros(int(d * SR)); tk = 0.0; k = 0
    while tk < d - 0.05:
        s_ = passa_alto(rng.normal(0, 1, int(0.04 * SR)), 900) * np.exp(-T(0.04) * 60) * (0.35 + 0.65 * tk / d); i = int(tk * SR); x[i:i + len(s_)] += s_[:len(x) - i]
        tk += max(0.035, 0.09 - 0.05 * tk / d); k += 1
    return x
def barrito(d=1.0):
    t_ = T(d); f = 300 + 520 * np.minimum(1, t_ / 0.22) - 160 * np.maximum(0, t_ - 0.5)
    return np.tanh(saw(f * (1 + 0.035 * np.sin(2 * np.pi * 27 * t_)), t_) * 1.6 + 0.3 * saw(f * 1.5, t_)) * np.minimum(1, t_ * 30) * np.minimum(1, (d - t_) * 6) * 0.5
NOTE = {'A3': 220.0, 'C4': 261.63, 'D4': 293.66, 'E4': 329.63, 'F4': 349.23, 'G#4': 415.3, 'A4': 440.0, 'B4': 493.88, 'C5': 523.25, 'D5': 587.33, 'E5': 659.25, 'F5': 698.46}
def bandoneon(f, d):
    t_ = T(d); v = 1 + 0.004 * np.sin(2 * np.pi * 6 * t_)
    x = saw(f * v, t_) * 0.5 + saw(f * 1.004 * v, t_) * 0.35 + np.sign(osc(f * 2 * v, t_)) * 0.12
    return passa_basso(x, 2600) * np.minimum(1, t_ * 25) * np.minimum(1, (d - t_) * 18)
def tango(battuta=0.48, volte=1):
    """frase di tango a fisarmonica (melodia nostra) con il basso marcato a ogni battuta: «tan-go»"""
    mel = [('E5', 0, 0.75), ('F5', 0.75, 0.25), ('E5', 1.0, 0.5), ('D5', 1.5, 0.5), ('C5', 2.0, 0.75), ('B4', 2.75, 0.25), ('A4', 3.0, 0.5), ('G#4', 3.5, 0.5),
           ('A4', 4.0, 0.75), ('B4', 4.75, 0.25), ('C5', 5.0, 0.5), ('E5', 5.5, 0.5), ('A4', 6.0, 1.5)]
    bas = ['A3', 'A3', 'E4', 'E4', 'A3', 'A3', 'E4', 'E4']
    L = 8 * battuta; x = np.zeros(int((L * volte + 1.0) * SR))
    for v_ in range(volte):
        o = v_ * L
        for n_, b0, bd in mel:
            s_ = bandoneon(NOTE[n_], bd * battuta * 0.95); i = int((o + b0 * battuta) * SR); x[i:i + len(s_)] += s_[:len(x) - i] * 0.55
        for k, n_ in enumerate(bas):
            s_ = bandoneon(NOTE[n_] / 2, battuta * 0.35) * (1.0 if k % 2 == 0 else 0.7); i = int((o + k * battuta) * SR); x[i:i + len(s_)] += s_[:len(x) - i] * 0.5
    return x
def getto(d):
    """il getto d'acqua: ruggito di rumore con un rombo sotto"""
    t_ = T(d); n = rng.normal(0, 1, len(t_)); x = passa_basso(n, 1800) * 1.2 + passa_basso(n, 160) * 3.0
    return np.tanh(x * (0.6 + 0.4 * np.sin(2 * np.pi * 3.3 * t_)) * np.minimum(1, t_ * 15) * 0.9)
def alluvione(d):
    t_ = T(d); n = rng.normal(0, 1, len(t_)); return passa_basso(n, 700) * 2.2 * (0.7 + 0.3 * np.sin(2 * np.pi * 0.4 * t_))
def ruggito(d=1.4, f=58.0):
    """ruggito da scarafaggio gigante: sibilo abbassato e un ringhio sotto"""
    t_ = T(d); sib = passa_basso(passa_alto(rng.normal(0, 1, len(t_)), 700), 2600) * (0.6 + 0.4 * np.sin(2 * np.pi * 9 * t_))
    gr = np.tanh(saw(f * (1 + 0.15 * np.sin(2 * np.pi * 6 * t_)) * (1 + 0.3 * np.exp(-t_ * 2)), t_) * 2.0) * (0.7 + 0.3 * np.sin(2 * np.pi * 13 * t_))
    return (sib * 0.8 + passa_basso(gr, 900) * 0.9) * np.minimum(1, t_ * 8) * np.minimum(1, (d - t_) * 3)
def sciaf():
    """lo SCIAF: schiaffo enorme (rumore secco), botto e onda"""
    s_ = np.tanh(passa_alto(rng.normal(0, 1, int(0.12 * SR)), 600) * np.exp(-T(0.12) * 35) * 3.0)
    x = np.zeros(int(2.4 * SR)); x[:len(s_)] += s_; b = boom(2.2, 75, 28); x[:len(b)] += b * 0.9
    w = schizzo(2.0, 1800) * 1.4; x[int(0.05 * SR):int(0.05 * SR) + len(w)] += w[:len(x) - int(0.05 * SR)]; return np.tanh(x * 1.2)
def sirena(d, f1=650, f2=880):
    t_ = T(d); f = np.where((t_ % 1.0) < 0.5, f1, f2); return passa_basso(np.sign(osc(f, t_)) * 0.4, 1600) * np.hanning(len(t_))
def applauso(d, densita=60):
    x = np.zeros(int(d * SR))
    for _ in range(int(d * densita)):
        tk = rng.uniform(0, d - 0.03); s_ = passa_alto(rng.normal(0, 1, int(0.02 * SR)), 1200) * np.exp(-T(0.02) * 160); i = int(tk * SR); x[i:i + len(s_)] += s_[:len(x) - i] * rng.uniform(0.3, 1.0)
    return x * np.hanning(len(x)) ** 0.3
def bau(f0=520, d=0.22):
    """abbaio di Tumbo, sintetico"""
    t_ = T(d); f = f0 * (1 + 0.5 * np.exp(-t_ * 25)) * (1 - 0.3 * t_ / d)
    x = np.tanh(saw(f, t_) * 2.0); x = passa_basso(passa_alto(x, 400), 2500) * np.minimum(1, t_ * 120) * np.exp(-t_ * 9); return x * 0.8
def tacco(g=1.0):
    s_ = passa_alto(rng.normal(0, 1, int(0.025 * SR)), 1800) * np.exp(-T(0.025) * 140); return s_ * g

# ---------- voce ----------
subprocess.run([S.FFMPEG, '-y', '-loglevel', 'error', '-i', 'audio/voce_t025.mp3', '-ar', str(SR), '-ac', '1', 'audio/voce44_t025.wav'], check=True)
w = wave.open('audio/voce44_t025.wav'); v = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(float) / 32768; v = np.pad(v, (0, max(0, N - len(v))))[:N]
_loc = np.sqrt(lp(v ** 2, int(0.35 * SR))); v = v * lp(np.clip(0.115 / (_loc + 0.03), 0.9, 3.0), int(0.25 * SR))
venv = lp(np.abs(v), int(0.12 * SR)); venv = np.clip(venv / (np.percentile(venv, 95) + 1e-9), 0, 1)

# ---------- tempi (gli stessi di anim025_body.py) ----------
T_BAGNO, T_MART, T_SCARA, T_TIRA, T_VORT, T_RISALE = 2.86, 3.16, 4.58, 6.38, 7.0, 7.76
T_VALIGIA, T_TRASF, T_STRONZA, T_LOGICA = 8.82, 9.76, 11.08, 12.28
T_COMPRA, T_ELE, T_TANGO, T_CASQUE, T_BESTIONE, T_CADE, T_SEDUTO = 14.14, 14.56, 15.04, 16.94, 17.96, 18.38, 18.95
T_ESPLODE, T_FUORI, T_ALLAGA, T_ESCE, T_SU, T_40 = 19.94, 20.8, 22.12, 23.66, 24.12, 25.36
T_TUMBO, T_CIAB, T_SALTO, T_SCIAF, T_TAPPETO, T_BALLA, T_TEAM = 26.14, 27.46, 28.56, 29.3, 30.22, 31.94, 34.68

# ---------- musica ----------
def traccia(rel, inizio=None, cerca=(0, 100), finestra=8.0, vel=1.0):
    x = S.carica('musica/' + rel, SR)
    if vel != 1.0: x = np.interp(np.arange(0, len(x), vel), np.arange(len(x)), x)
    if inizio is None:
        h = int(SR * 0.5); r = np.sqrt(lp(x ** 2, int(finestra * SR))[::h]); a, b = int(cerca[0] * 2), min(len(r), int(cerca[1] * 2))
        inizio = max(0.0, (a + int(np.argmax(r[a:b]))) * 0.5 - finestra / 2)
    y = x[int(inizio * SR):]; y = y / (np.sqrt(np.mean(y[:int(20 * SR)] ** 2)) + 1e-9) * 0.1; return y, inizio
def stendi(buf, x, t0, t1, g, fi=0.05, fo=0.05, da=0.0):
    seg = np.zeros(N); i0 = int(t0 * SR); s = x[int(da * SR):int(da * SR) + (N - i0)]; seg[i0:i0 + len(s)] = s; buf += seg * env(t0, t1, fi, fo) * g; return seg
COMICO, i_c = traccia('comica/Scheming_Weasel_faster', inizio=0.5)
EPICO, i_e = traccia('epica/Heroic_Age', cerca=(10, 120))
CAOS, i_k = traccia('brainrot/Hall_of_the_Mountain_King', cerca=(60, 160))
CAOS_G, _ = traccia('brainrot/Hall_of_the_Mountain_King', inizio=i_k + 3.5, vel=0.84)    # piu' grave e lento: Martina gigante
print('inizi dei brani (s): comico %.1f epico %.1f caos %.1f' % (i_c, i_e, i_k))
mus = np.zeros(N); t = np.arange(N) / SR
# 0.0 COMICO veloce da subito; 4.40 stop secco col record scratch su «Martina e' uno scarafaggio!»
co = np.zeros(N); stendi(co, COMICO, 0.0, 4.40, 1.0, 0.01, 0.02); mus += co * 0.2
# 6.38 COMICO di nuovo, pieno, con lo sciacquone; 11.74 micro-pausa
co2 = np.zeros(N); stendi(co2, COMICO, T_TIRA - 0.05, 11.74, 1.0, 0.03, 0.03, da=6.0); mus += co2 * 0.19
# 11.95 bordone che sale sotto «Allora Pippo fa la cosa piu' logica!»
bordone = (np.sin(2 * np.pi * 55 * t) + 0.4 * np.sin(2 * np.pi * 82.4 * t)) * (0.6 + 0.4 * np.sin(2 * np.pi * 6 * t)); mus += bordone * env(11.95, T_COMPRA, 0.3, 0.02) * 0.05
# 14.14 EPICO a pieno; dal tango si abbassa e lascia posto alla fisarmonica
ep = np.zeros(N); stendi(ep, EPICO, T_COMPRA - 0.02, T_ESPLODE - 0.05, 1.0, 0.02, 0.05); mus += ep * 0.25 * ramp(T_TANGO - 0.1, T_TANGO + 0.3, 1.0, 0.35)
TG = tango(0.48, 1); put(mus, T_TANGO, TG[:int((T_CASQUE - T_TANGO + 0.3) * SR)] * env(0, T_CASQUE - T_TANGO + 0.3, 0.01, 0.25)[:int((T_CASQUE - T_TANGO + 0.3) * SR)], 0.11)
# 19.94 CAOS: esplode tutto; 23.20 stop di 0,3 s sui puntini di «si allaga...»
ka = np.zeros(N); stendi(ka, CAOS, T_ESPLODE - 0.02, 23.2, 1.0, 0.01, 0.03); mus += ka * 0.24
# 23.55 il CAOS riparte piu' grave: Martina gigante
kg = np.zeros(N); stendi(kg, CAOS_G, 23.55, T_TUMBO - 0.05, 1.0, 0.05, 0.05); mus += kg * 0.25
# 26.14 EPICO per l'eroe Tumbo; 28.95 stop di 0,3 s, fischio della ciabatta che cala
ep2 = np.zeros(N); stendi(ep2, EPICO, T_TUMBO - 0.02, 28.95, 1.0, 0.02, 0.02, da=25.0); mus += ep2 * 0.26
# 30.22 COMICO veloce e la frase di tango di nuovo, fino alla fine
co3 = np.zeros(N); stendi(co3, COMICO, T_TAPPETO, DUR, 1.0, 0.02, 0.4, da=14.0); mus += co3 * 0.10
TG2 = tango(0.48, 1); put(mus, T_BALLA - 0.02, TG2 * env(0, len(TG2) / SR, 0.01, 0.3)[:len(TG2)], 0.12)
mus *= (1 - 0.45 * venv) * 2.1

# ---------- effetti ----------
fx = np.zeros(N); big = np.zeros(N)
def sfx(tp, nome, g=1.0, vel=1.0):
    x = S.carica(nome, SR, volume=g)
    if vel != 1.0: x = np.interp(np.arange(0, len(x), vel), np.arange(len(x)), x)
    put(fx, tp, x)
# 0.0 sciabordio nel water, la cannuccia che risucchia (evento sonoro nei primi 2 s)
sb = sciabordio(T_TIRA); put(fx, 0.0, sb * env(0, T_TIRA, 0.05, 0.3)[:len(sb)], 0.05)
put(fx, 0.35, cannuccia(0.5), 0.22); put(fx, 5.15, cannuccia(0.55), 0.25)
put(fx, 2.35, boing(0.3, 330), 0.12)                                          # «uno in ferie»
for k in range(3): put(fx, T_MART + 0.05 + 0.18 * k, plop(0.15), 0.14)           # le antenne che spuntano
# 4.40 record scratch
put(fx, 4.36, record_scratch(0.42), 0.55)
# 6.38 il pulsante, lo sciacquone enorme, il vortice, il «plop» di Martina che sparisce
sfx(T_TIRA + 0.3, 'metalClick', 0.7); put(fx, T_TIRA + 0.35, sciacquone(1.6), 0.55); put(fx, 7.48, plop(0.3), 0.4)
# 7.76 risale: schizzo e boing; 8.82 la valigia: tin; 9.76 le rotelline e il cuscino
put(fx, T_RISALE, schizzo(0.6), 0.35); put(fx, T_RISALE + 0.02, boing(0.5, 260), 0.2); sfx(T_RISALE + 0.55, 'impactSoft_medium_001', 0.4)
put(fx, T_VALIGIA, ting(2600), 0.22); put(fx, T_VALIGIA + 0.12, ting(3400), 0.15)
put(fx, T_TRASF - 0.1, whoosh(0.3, 1), 0.3); sfx(T_TRASF + 0.05, 'impactSoft_medium_002', 0.35); put(fx, T_TRASF + 0.3, cannuccia(0.45), 0.18)
# 11.08 colpo comico su «quella stronza!»
sfx(T_STRONZA + 0.05, 'impactPunch_heavy_000', 0.45); put(fx, T_STRONZA + 0.1, boing(0.45, 190), 0.16)
# 11.95 rullo di tamburi che sale fino all'elefante
put(fx, 11.95, rullo_tamburo(T_COMPRA - 11.95), 0.22); put(fx, 12.6, riser(T_COMPRA - 12.6, 140, 1400), 0.18)
# 14.14 colpo d'orchestra; 14.56 l'elefante atterra (fischio, tonfo enorme), barrito
put(big, T_COMPRA, colpo_orchestra(146.8, 0.9), 0.45); put(fx, T_COMPRA + 0.02, fischio(0.42, 1900, 500), 0.15)
put(big, T_ELE, boom(1.4, 60, 28), 0.7); sfx(T_ELE, 'impactSoft_heavy_002', 0.9); put(fx, T_ELE + 0.3, barrito(1.0), 0.45)
# 15.04 i tacchi del tango, a ogni passo
for k in range(4): put(fx, T_TANGO + 0.48 * k + 0.02, tacco(), 0.35); put(fx, T_TANGO + 0.48 * k + 0.26, tacco(0.7), 0.25)
# 16.94 il casque': cigolio di sforzo, poi giu' all'indietro
put(fx, T_CASQUE + 0.4, fischio(1.0, 500, 260), 0.08); put(fx, T_BESTIONE, whoosh(0.45, -1), 0.45); put(big, T_BESTIONE + 0.35, boom(0.8, 55, 30), 0.35)
# 18.38 sfonda il soffitto del bagno e piomba sul water: crollo, tonfo, ceramica che scricchiola
sfx(T_CADE + 0.1, 'impactWood_heavy_003', 0.6); sfx(T_CADE + 0.16, 'impactPlank_medium_002', 0.4); put(fx, T_CADE + 0.05, fischio(0.5, 1800, 600), 0.12)
put(big, T_SEDUTO, boom(1.2, 62, 30), 0.65); sfx(T_SEDUTO, 'impactPlate_heavy_001', 0.7); put(fx, T_SEDUTO + 0.25, crack(0.35), 0.35); put(fx, T_SEDUTO + 0.6, crack(0.25), 0.25)
# 19.94 ESPLODE: botto, getto, cocci di ceramica
put(big, T_ESPLODE, boom(1.8, 70, 26), 0.8); put(fx, T_ESPLODE, schizzo(1.2, 3000), 0.5)
for k in range(6): sfx(T_ESPLODE + 0.1 + 0.07 * k, 'impactGlass_heavy_00%d' % (k % 5), 0.35)
gt = getto(T_ALLAGA + 0.8 - T_ESPLODE); put(fx, T_ESPLODE + 0.05, gt * env(0, len(gt) / SR, 0.05, 0.6)[:len(gt)], 0.35)
# 20.8 fuori: il getto sfonda il tetto, tegole che piovono, sirene lontane
put(big, T_FUORI, boom(1.4, 66, 30), 0.55)
for k in range(8): sfx(T_FUORI + 0.5 + 0.13 * k, 'impactWood_light_00%d' % (k % 5), 0.25)
sr_ = sirena(4.5); put(fx, 21.3, sr_, 0.035)
# 22.12 l'alluvione: acqua che scroscia, schizzi
al = alluvione(T_TAPPETO - 22.0); put(fx, 22.0, al * env(0, len(al) / SR, 0.4, 0.3)[:len(al)], 0.18)
for k in range(6): put(fx, 22.2 + 0.18 * k, schizzo(0.5, 2200), 0.12)
# 23.20 silenzio vero (0,3 s), poi le bolle; 24.12 Martina esce: onda e ruggito; 25.36 di nuovo
put(fx, 23.55, bolle(0.6, 16), 0.3)
put(big, T_SU, boom(1.6, 50, 24), 0.5); put(fx, T_SU, schizzo(1.4, 1600), 0.4); put(fx, T_SU + 0.35, ruggito(1.3), 0.28)
put(fx, T_40 - 0.05, ruggito(1.1, 52), 0.32); put(big, T_40, boom(0.9, 45, 25), 0.3)
# 26.14 Tumbo: abbaio eroico; 28.56 il salto (whoosh); 28.95 fischio della ciabatta che cala; 29.3 SCIAF
put(fx, T_TUMBO + 0.3, bau(560), 0.4); put(fx, T_TUMBO + 0.62, bau(520), 0.35)
put(fx, T_SALTO, whoosh(0.5, 1), 0.5); put(fx, 28.95, fischio(0.35, 2400, 700), 0.22)
put(big, T_SCIAF - 0.02, sciaf(), 0.75)
for k in range(8): put(fx, T_SCIAF + 0.4 + 0.15 * k, schizzo(0.4, 2400), 0.12)
# 30.22 salotto: un «plof» del tappeto; 31.94 i tacchi sul tappeto; 34.68 accordo finale e applauso di Tumbo
put(fx, T_TAPPETO + 0.05, plop(0.3), 0.25); put(fx, 31.1, boing(0.3, 420), 0.12)
for k in range(5): put(fx, T_BALLA + 0.48 * k + 0.02, tacco(0.6), 0.25)
FIN = sum(bandoneon(NOTE[n_], 1.4) for n_ in ('A3', 'C4', 'E4', 'A4')); put(mus, T_TEAM + 0.05, FIN * env(0, 1.4, 0.01, 0.5)[:len(FIN)], 0.06)
put(fx, T_TEAM + 0.3, applauso(2.4, 40), 0.25); put(fx, T_TEAM + 0.25, bau(600, 0.18), 0.3)

# ---------- mix con limitatore ----------
big *= (1 - 0.45 * venv)
out = v * 1.0 + mus + np.tanh(fx * 1.1) * 0.45 * (1 - 0.3 * venv) + big * 0.5
out *= np.where(t >= DUR - 0.35, np.clip(1 - (t - DUR + 0.35) / 0.3, 0, 1), 1.0)
h = 256; pk = np.abs(out[:N // h * h]).reshape(-1, h).max(1)
g = np.minimum(1.0, 0.95 / np.maximum(pk, 1e-6)); g = np.minimum(g, np.concatenate([g[1:], g[-1:]])); g = np.convolve(g, np.ones(9) / 9, mode='same')
gg = np.interp(np.arange(N), np.arange(len(g)) * h + h / 2, g); out = np.clip(out * gg, -0.99, 0.99)
ww = wave.open('audio/t025.wav', 'w'); ww.setnchannels(1); ww.setsampwidth(2); ww.setframerate(SR); ww.writeframes((out * 32767).astype(np.int16).tobytes()); ww.close()
def rms(x, a, b): return float(np.sqrt(np.mean(x[int(a * SR):int(b * SR)] ** 2)))
print('audio/t025.wav', DUR, 's  riduzione massima del limitatore %.2f' % float(gg.min()))
for nome, a, b in (('hook', 0, 4.4), ('sciacquone', 6.4, 9.7), ('logica', 12.0, 14.1), ('elefante', 14.1, 16.9), ('esplode', 19.9, 22.1), ('gigante', 23.6, 26.1), ('sciaf', 29.2, 30.2), ('finale', 30.2, 37.0)):
    print('%-10s voce %.3f  musica %.3f  effetti %.3f  impatti %.3f' % (nome, rms(v, a, b), rms(mus, a, b), rms(np.tanh(fx * 1.1) * 0.45, a, b), rms(big * 0.5, a, b)))
