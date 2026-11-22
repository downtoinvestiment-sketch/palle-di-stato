"""Video 030 (Rospina o Castora?, copione n. 32 v3) - audio con la SOUND DESIGN TIMELINE del copione, sui tempi veri della voce.
Le quattro famiglie musicali (Kevin MacLeod, CC-BY 4.0, vanno citati nella descrizione):
  EPICO = «Heroic Age» (il palazzo, l'entrata della Castora)   COMICO = «Sneaky Snitch» (tema di Pippo)   CAOS = «Hall of the Mountain King» (la diga)   SUSPENSE = «Thief in the Night»
Effetti della libreria (Kenney, CC0) + effetti costruiti in numpy (gli strumenti sono quelli di audio026.py e audio028.py): applausi, pioggia e trombone triste,
ali dei prezzi che volano, rullo di tamburo e cannone dei bonus, cassa, tronchi, clacson, megafono, crollo, acqua che sale, remi, canotti che ammarano.
Uso, dalla cartella del progetto: python scripts/audio030.py"""
import sys, os, subprocess, wave
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import suoni as S
SR = 44100; DUR = 44.8; N = int(DUR * SR); rng = np.random.default_rng(30)

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
def traccia(rel, inizio=None, cerca=(0, 100), finestra=8.0, vel=1.0):
    x = S.carica('musica/' + rel, SR)
    if vel != 1.0: x = np.interp(np.arange(0, len(x), vel), np.arange(len(x)), x)
    if inizio is None:
        h = int(SR * 0.5); r = np.sqrt(lp(x ** 2, int(finestra * SR))[::h]); a, b = int(cerca[0] * 2), min(len(r), int(cerca[1] * 2))
        inizio = max(0.0, (a + int(np.argmax(r[a:b]))) * 0.5 - finestra / 2)
    y = x[int(inizio * SR):]; y = y / (np.sqrt(np.mean(y[:int(20 * SR)] ** 2)) + 1e-9) * 0.1; return y, inizio
def stendi(buf, x, t0, t1, g, fi=0.05, fo=0.05, da=0.0):
    seg = np.zeros(N); i0 = int(t0 * SR); s = x[int(da * SR):int(da * SR) + (N - i0)]; seg[i0:i0 + len(s)] = s; buf += seg * env(t0, t1, fi, fo) * g; return seg

# ---------- suoni nuovi ----------
def eco(x, ritardi=(0.11, 0.23, 0.37, 0.55, 0.8), g0=0.45, decad=0.62, fc=2500):
    y = np.concatenate([x, np.zeros(int(1.4 * SR))]); out = y.copy(); g = g0
    for d in ritardi:
        i = int(d * SR); s_ = passa_basso(y, fc)[:len(y) - i] * g; out[i:] += s_; g *= decad
    return out
def huss(d=0.78, grande=1.0):
    """l'HUSS di Tumbo: fiato «h», vocale gutturale «u», sibilo lungo «ss», con l'eco."""
    t_ = T(d); n = rng.normal(0, 1, len(t_))
    h = passa_basso(passa_alto(n, 600), 2600) * np.exp(-((t_ - 0.04) / 0.035) ** 2) * 1.2
    f = 150 * (1 + 0.25 * np.exp(-t_ * 12)) * (1 - 0.15 * t_ / d)
    u = passa_basso(np.tanh(saw(f * (1 + 0.02 * np.sin(2 * np.pi * 31 * t_)), t_) * 2.2), 1100) * 0.7 + passa_basso(passa_alto(n, 300), 1400) * 0.5
    u *= np.clip((t_ - 0.05) / 0.04, 0, 1) * np.clip((0.36 - t_) / 0.08, 0, 1)
    s = passa_alto(n, 4200) * np.clip((t_ - 0.26) / 0.05, 0, 1) * np.clip((d - t_) / (d - 0.4), 0, 1) ** 1.5 * 1.3
    x = np.tanh((h + u + s) * 1.4)
    return eco(x, g0=0.35 + 0.25 * grande, decad=0.55 + 0.2 * grande, ritardi=tuple(r * (1 + grande) for r in (0.11, 0.23, 0.37, 0.55, 0.8)))
def zoom_pugno():
    """lo zoom a pugno sulla faccia: fruscio corto e un colpo basso."""
    w_ = whoosh(0.18, 1) * 0.6; b_ = boom(0.7, 90, 40); x = np.zeros(int(0.9 * SR)); x[:len(w_)] += w_; x[int(0.06 * SR):int(0.06 * SR) + len(b_)] += b_[:len(x) - int(0.06 * SR)]; return x
def respiro(d):
    t_ = T(d); n = passa_basso(passa_alto(rng.normal(0, 1, len(t_)), 300), 1500); return n * (0.5 + 0.5 * np.sin(2 * np.pi * 0.8 * t_)) ** 3
def ronzio(d):
    t_ = T(d); return (np.sin(2 * np.pi * 50 * t_) + 0.5 * np.sin(2 * np.pi * 100 * t_) + 0.2 * passa_basso(rng.normal(0, 1, len(t_)), 300)) * np.minimum(1, t_ * 2)
def crunch(d=0.28):
    x = np.zeros(int(d * SR))
    for k in range(7):
        s_ = np.tanh(passa_alto(rng.normal(0, 1, int(0.03 * SR)), 1500) * np.exp(-T(0.03) * 90) * 3); i = int(rng.uniform(0, d - 0.035) * SR); x[i:i + len(s_)] += s_ * rng.uniform(0.4, 1)
    return x
def foglio(d=0.3):
    t_ = T(d); n = passa_basso(passa_alto(rng.normal(0, 1, len(t_)), 1500), 6000); return n * np.sin(np.pi * t_ / d) ** 2 * (0.6 + 0.4 * np.sin(2 * np.pi * 37 * t_))
def russare(d=0.9):
    t_ = T(d); f = 70 + 15 * np.sin(np.pi * t_ / d); x = passa_basso(np.tanh(saw(f, t_) * 2) * (1 + 0.6 * passa_basso(rng.normal(0, 1, len(t_)), 200)), 700)
    return x * np.sin(np.pi * t_ / d) ** 2
def cigolio(d=0.35, f0=900, f1=1500):
    t_ = T(d); f = f0 + (f1 - f0) * np.sin(np.pi * t_ / d); return passa_basso(np.tanh(saw(f * (1 + 0.05 * np.sin(2 * np.pi * 45 * t_)), t_) * 1.5), 3500) * np.sin(np.pi * t_ / d) * 0.6
def risucchio(d):
    t_ = T(d); n = rng.normal(0, 1, len(t_)); x = passa_basso(n, 400) * 2.0 + passa_basso(passa_alto(n, 800), 2500) * 0.5
    return x * (t_ / d) ** 1.5
def onda(d):
    t_ = T(d); n = rng.normal(0, 1, len(t_)); x = passa_basso(n, 300) * 3.0 + passa_basso(n, 2200) * 0.8
    return np.tanh(x * (0.2 + 0.8 * (t_ / d) ** 2))

def huss_piccolo(f0=440, dur=0.27):
    """l'HUSS di Tumbo come nel video di riferimento: vocina piccola e secca, senza eco.
    0-25 ms «h» soffiato chiaro (3-6 kHz), 25-80 ms vocale corta a 370-500 Hz con formanti a 1,3 e 2 kHz, poi «ss» fino a 0,27 s (6,5-9 kHz)."""
    from scipy.signal import butter, sosfilt
    def bp(x, lo, hi, o=2): return sosfilt(butter(o, [lo, hi], btype='band', fs=SR, output='sos'), x)
    n = int(dur * SR); t_ = np.arange(n) / SR; nz = rng.normal(0, 1, n)
    h = bp(nz, 3000, 6200) * np.exp(-((t_ - 0.012) / 0.012) ** 2) * 0.9
    f = f0 * (0.85 + 0.3 * np.sin(np.pi * np.clip((t_ - 0.015) / 0.08, 0, 1))) * (1 + 0.03 * np.sin(2 * np.pi * 28 * t_))   # sale e scende, come nel riferimento
    ph = np.cumsum(f) / SR; gl = (2 * (ph % 1) - 1) ** 3 + 0.25 * nz * 0.3
    vo = bp(gl, 1100, 1600) * 1.4 + bp(gl, 1800, 2300) * 1.0 + bp(gl, 300, 600) * 0.6
    vo *= np.clip((t_ - 0.018) / 0.01, 0, 1) * np.clip((0.085 - t_) / 0.02, 0, 1)
    ss = bp(nz, 6500, 9200, 3) * np.clip((t_ - 0.075) / 0.02, 0, 1) * np.clip((dur - t_) / 0.12, 0, 1) ** 1.3 * 0.75
    x = h + vo / (np.abs(vo).max() + 1e-9) * 1.3 + ss / (np.abs(ss).max() + 1e-9) * 0.5
    return np.tanh(x * 1.2)


# ======================================================================================================================
# attrezzi nati col video 028
# ======================================================================================================================
def pernacchia(d=0.55):
    """la gola che si sgonfia: pernacchia che scende."""
    t_ = T(d); f = 150 * (60 / 150) ** (t_ / d) * (1 + 0.12 * np.sin(2 * np.pi * 27 * t_)); x = np.tanh(saw(f, t_) * 3) * (0.6 + 0.4 * np.sign(osc(31, t_)))
    return passa_basso(x, 1500) * np.minimum(1, t_ * 60) * np.clip((d - t_) / 0.12, 0, 1)
def pop(d=0.12):
    t_ = T(d); return osc(900 * np.exp(-t_ * 30) + 120, t_) * np.exp(-t_ * 28) + passa_alto(rng.normal(0, 1, len(t_)), 2500) * np.exp(-t_ * 60) * 0.7
def cassa():
    """ka-ching del registratore di cassa: scatto, campanello, cassetto."""
    x = np.zeros(int(0.9 * SR)); put(x, 0.0, crack(0.12), 0.5); put(x, 0.07, ting(2350, 0.5), 0.9); put(x, 0.09, ting(3520, 0.45), 0.6); put(x, 0.22, passa_basso(rng.normal(0, 1, int(0.12 * SR)), 900) * np.hanning(int(0.12 * SR)), 0.5); return x
def timbro():
    t_ = T(0.35); return np.tanh((osc(95 * np.exp(-t_ * 9) + 45, t_) * np.exp(-t_ * 9) * 1.6 + passa_basso(rng.normal(0, 1, len(t_)), 1800) * np.exp(-t_ * 40) * 1.2) * 1.5)
def fanfara(note=(0, 4, 7, 12), dt=0.13, base=392.0, lunga=0.45):
    """trombe pompose per l'arrivo della ministra."""
    x = np.zeros(int((len(note) * dt + lunga + 0.4) * SR))
    for k, n_ in enumerate(note):
        d = lunga if k == len(note) - 1 else dt * 0.95; t_ = T(d); f = base * 2 ** (n_ / 12) * (1 + 0.012 * np.sin(2 * np.pi * 6 * t_) * (t_ > 0.15))
        s_ = passa_basso(saw(f, t_) + 0.5 * saw(f * 1.005, t_), 2600) * np.minimum(1, t_ * 60) * np.minimum(1, (d - t_) * 25); put(x, k * dt, s_, 0.6)
    return x
def ali(d=0.16):
    t_ = T(d); return passa_basso(rng.normal(0, 1, len(t_)), 700) * np.hanning(len(t_)) * 1.6
def verso_pellicano(d=0.4, f=210):
    t_ = T(d); x = np.tanh(saw(f * (1 + 0.25 * np.exp(-t_ * 10)) * (1 + 0.03 * np.sin(2 * np.pi * 40 * t_)), t_) * 2.5)
    return passa_basso(passa_alto(x, 300), 2200) * np.minimum(1, t_ * 50) * np.clip((d - t_) / 0.08, 0, 1)
def tic(f=1900):
    t_ = T(0.03); return np.sin(2 * np.pi * f * t_) * np.exp(-t_ * 150)
def gnam():
    x = np.zeros(int(0.7 * SR)); put(x, 0.0, crunch(0.2), 0.9); put(x, 0.22, plop(0.2), 0.7); t_ = T(0.22); put(x, 0.42, osc(190 * (1 - 0.5 * t_ / 0.22), t_) * np.hanning(len(t_)), 0.6); return x
def folla(d):
    """brusio del mercato."""
    t_ = T(d); n = rng.normal(0, 1, len(t_)); x = passa_basso(passa_alto(n, 250), 1100) * (0.6 + 0.4 * passa_basso(np.abs(rng.normal(0, 1, len(t_))), 3) / 0.03)
    return x / (np.abs(x).max() + 1e-9)


# ======================================================================================================================
# VIDEO 030
# ======================================================================================================================
def trombone_triste():
    """ua-ua-ua-uaaa: quattro note che scendono."""
    x = np.zeros(int(1.9 * SR))
    for k, (n_, d) in enumerate(((0, 0.3), (-1, 0.3), (-2, 0.3), (-3, 0.85))):
        t_ = T(d); f = 233.0 * 2 ** (n_ / 12) * (1 - 0.03 * (t_ / d) * (k == 3)) * (1 + 0.02 * np.sin(2 * np.pi * 5.5 * t_)); s_ = passa_basso(saw(f, t_), 900 + 500 * np.exp(-t_ * 6).mean()) * np.minimum(1, t_ * 40) * np.minimum(1, (d - t_) * 14)
        put(x, 0.32 * k, s_, 0.6)
    return x
def pioggia(d):
    t_ = T(d); return passa_alto(rng.normal(0, 1, len(t_)), 3500) * 0.5 + passa_basso(passa_alto(rng.normal(0, 1, len(t_)), 800), 2500) * 0.4
def cannonata():
    x = np.zeros(int(1.6 * SR)); put(x, 0.0, boom(1.4, 90, 32), 1.0); t_ = T(0.5); put(x, 0.0, passa_basso(rng.normal(0, 1, len(t_)), 1400) * np.exp(-t_ * 9), 0.8); put(x, 0.03, pop(0.15), 0.6); return x
def tronco_giu(f=95):
    t_ = T(0.22); return np.tanh((osc(f * np.exp(-t_ * 6) + 40, t_) * np.exp(-t_ * 14) * 1.5 + passa_basso(rng.normal(0, 1, len(t_)), 900) * np.exp(-t_ * 45)) * 1.3)
def megafono_voce(d):
    """bla bla nasale e distorto nel megafono."""
    t_ = T(d); f = 310 * (1 + 0.25 * np.sign(np.sin(2 * np.pi * 5.5 * t_))) * (1 + 0.04 * np.sin(2 * np.pi * 31 * t_)); x = np.tanh(saw(f, t_) * 4) * (0.5 + 0.5 * np.abs(np.sin(2 * np.pi * 6.5 * t_)))
    return passa_basso(passa_alto(x, 700), 2600) * np.minimum(1, t_ * 30) * np.clip((d - t_) / 0.08, 0, 1)
def crollo():
    x = np.zeros(int(2.0 * SR)); put(x, 0.0, crack(0.4), 0.9); put(x, 0.12, boom(1.6, 70, 28), 1.0); t_ = T(1.4); put(x, 0.15, passa_basso(rng.normal(0, 1, len(t_)), 700) * np.exp(-t_ * 3.2), 0.9)
    for k in range(7): put(x, 0.3 + 0.13 * k + 0.05 * rng.random(), tronco_giu(70 + 20 * rng.random()), 0.5)
    return x

subprocess.run([S.FFMPEG, '-y', '-loglevel', 'error', '-i', 'audio/voce_t030.mp3', '-ar', str(SR), '-ac', '1', 'audio/voce44_t030.wav'], check=True)
w = wave.open('audio/voce44_t030.wav'); v = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(float) / 32768; v = np.pad(v, (0, max(0, N - len(v))))[:N]
_loc = np.sqrt(lp(v ** 2, int(0.35 * SR))); v = v * lp(np.clip(0.115 / (_loc + 0.03), 0.9, 3.0), int(0.25 * SR))
venv = lp(np.abs(v), int(0.12 * SR)); venv = np.clip(venv / (np.percentile(venv, 95) + 1e-9), 0, 1)

T_BENE, T_NO, T_MALE, T_PREZZI, T_TASSE, T_RISOLVE, T_BONUS = 3.12, 5.36, 6.02, 7.46, 8.70, 9.86, 11.48
T_BMONO, T_500, T_IERI, T_OGGI, T_2000, T_GRAZIE, T_TUTTI = 12.10, 13.30, 14.76, 16.92, 17.26, 18.18, 19.44
T_MA, T_CAST, T_ALLORA, T_LOGICA, T_DIGA, T_AUTO, T_CONTRO, T_ROSI, T_CROLLO = 21.02, 22.92, 24.02, 25.54, 25.98, 27.58, 29.00, 30.30, 31.75
T_ACQUA, T_VOTA, T_RESTA, T_PORCA, T_FESTA, T_BCAN, T_DOM = 32.94, 34.82, 36.68, 38.64, 39.70, 41.28, 42.86

EPICO, i_e = traccia('epica/Heroic_Age', cerca=(5, 90))
COMICO, i_c = traccia('comica/Sneaky_Snitch', inizio=1.0)
CAOS, i_k = traccia('brainrot/Hall_of_the_Mountain_King', cerca=(60, 150))
SUSP, i_s = traccia('suspense/Thief_in_the_Night', cerca=(5, 60))
print('inizi dei brani (s): epico %.1f comico %.1f caos %.1f suspense %.1f' % (i_e, i_c, i_k, i_s))
mus = np.zeros(N); t = np.arange(N) / SR
def strato(x, a, b, g, fi=0.05, fo=0.05, da=0.0):
    s_ = np.zeros(N); stendi(s_, x, a, b, 1.0, fi, fo, da); return s_ * g
def rms(x, a, b): return float(np.sqrt(np.mean(x[int(a * SR):int(b * SR)] ** 2)))
mus += strato(EPICO, 0.0, T_NO - 0.06, 0.2, 0.15, 0.02)                                               # il palazzo: da cinque anni comanda Rospina, e va tutto benissimo
mus += strato(COMICO, T_PREZZI - 0.1, T_BONUS - 0.25, 0.13, 0.1, 0.02)                                # i prezzi e le tasse volano
mus += strato(COMICO, T_BMONO, T_OGGI - 0.05, 0.16, 0.03, 0.02, da=9.0)                               # il bonus monopattino, tutto contento
mus += strato(SUSP, T_GRAZIE, T_MA - 0.05, 0.13, 0.05, 0.03)                                          # e grazie al cazzo
mus += strato(EPICO, T_CAST - 0.05, T_ALLORA - 0.05, 0.24, 0.02, 0.03, da=12.0)                       # l'entrata da eroina della Castora
mus += strato(CAOS, T_DIGA - 0.02, T_CROLLO - 0.02, 0.22, 0.02, 0.02) * ramp(T_DIGA, T_CROLLO, 0.8, 1.3)   # la diga, il megafono, le colonne: sempre peggio
mus += strato(SUSP, T_VOTA, T_RESTA - 0.05, 0.12, 0.2, 0.03, da=14.0)                                 # in canotto verso il seggio
mus += strato(EPICO, T_FESTA, T_DOM - 0.06, 0.2, 0.03, 0.02, da=20.0)                                 # Rospina festeggia
mus *= (1 - 0.5 * venv) * 2.1

fx = np.zeros(N); big = np.zeros(N)
def sfx(tp, nome, g=1.0, vel=1.0):
    try: x = S.carica(nome, SR, volume=g)
    except Exception as e: print('manca', nome, e); return
    if vel != 1.0: x = np.interp(np.arange(0, len(x), vel), np.arange(len(x)), x)
    put(fx, tp, x)
# --- il palazzo: la folla applaude; «benissimo»: coriandoli e ovazione; poi stop secco
ap = applauso(T_NO, 70); put(fx, 0.0, ap * env(0, T_NO, 0.3, 0.05)[:len(ap)], 0.1)
put(fx, 0.05, fanfara((0, 4, 7, 12), 0.14, 392.0, 0.5), 0.12)
for k in range(5): put(fx, T_BENE + 0.1 + 0.12 * k, pop(0.1), 0.25)
put(fx, T_BENE + 0.82, ting(2637, 0.4), 0.22)
# --- «No. Va tutto male.»: record scratch, pioggia, trombone triste, tuono
put(fx, T_NO - 0.08, record_scratch(0.35), 0.4)
pg = pioggia(T_PREZZI - T_NO + 1.2); put(fx, T_NO + 0.1, pg * env(0, len(pg) / SR, 0.1, 0.8)[:len(pg)], 0.06)
put(fx, T_NO + 0.3, trombone_triste(), 0.3); put(big, T_MALE + 0.05, boom(1.6, 55, 28), 0.5)
# --- i prezzi volano, le tasse pure: ali e fischi che salgono
for k in range(7): put(fx, T_PREZZI + 0.05 + 0.15 * k, ali(0.12), 0.25)
put(fx, T_PREZZI + 0.1, fiuuu(0.9, 500, 1900), 0.12)
for k in range(7): put(fx, T_TASSE + 0.0 + 0.13 * k, ali(0.11), 0.28)
put(fx, T_TASSE + 0.05, fiuuu(0.9, 600, 2400), 0.14)
# --- il cannone dei bonus: rullo di tamburo, miccia, botto, coriandoli
ru = rullo_tamburo(T_BONUS - T_RISOLVE - 0.2); put(fx, T_RISOLVE + 0.1, ru * ramp(0, len(ru) / SR, 0.4, 1.0)[:len(ru)], 0.22)
put(fx, T_BONUS - 0.75, riser(0.7, 400, 2200), 0.1)
put(big, T_BONUS, cannonata(), 0.6)
for k in range(8): put(fx, T_BONUS + 0.12 + 0.07 * k, pop(0.09), 0.2)
put(fx, T_BONUS + 0.15, fanfara((0, 7, 12), 0.1, 523.25, 0.3), 0.2)
# --- il buono scende, la cassa su «cinquecento euro»
put(fx, T_BMONO + 0.1, fiuuu(0.8, 1700, 700), 0.1); put(fx, T_BMONO + 0.9, plop(0.2), 0.4); put(fx, T_500 + 0.05, cassa(), 0.5); put(fx, T_500 + 0.0, whoosh(0.14, 1), 0.3)
# --- ieri 300: campanello della porta; oggi 2.000: il cartello gira, colpo
put(fx, T_IERI + 0.05, ting(1568, 0.5), 0.2); put(fx, T_IERI + 0.25, ting(2093, 0.5), 0.16)
put(fx, T_OGGI - 0.03, record_scratch(0.3), 0.35); put(fx, T_OGGI + 0.02, whoosh(0.14, 1), 0.35); put(big, T_2000, dun(46.0, 1.0), 0.6); put(big, T_2000, crack(0.25), 0.4); put(fx, T_2000 + 0.1, cassa(), 0.45)
# --- grazie al cazzo: il bonus ce l'hanno tutti (tante casse, brusio)
put(big, T_GRAZIE + 0.66, dun(52.0, 0.7), 0.4)
fo = folla(T_MA - T_TUTTI); put(fx, T_TUTTI, fo * env(0, len(fo) / SR, 0.1, 0.15)[:len(fo)], 0.07)
for k in range(6): put(fx, T_TUTTI + 0.1 + 0.2 * k, cassa(), 0.2)
# --- ma per fortuna c'e' l'opposizione: silenzio, coro di speranza; la Castora: colpo d'orchestra, scintilla sui denti
put(fx, T_MA + 0.1, riser(T_CAST - T_MA - 0.25, 300, 900), 0.08)
for k, f_ in enumerate((523.25, 659.25, 783.99)): t_ = T(1.5); put(fx, T_MA + 0.3, osc(f_, t_) * np.hanning(len(t_)), 0.05)
put(big, T_CAST + 0.1, colpo_orchestra(196.0, 0.9), 0.6); put(big, T_CAST + 0.1, boom(1.0, 70, 36), 0.4); put(fx, T_CAST + 0.5, ting(3520, 0.5), 0.3)
# --- la cosa piu' logica: silenzio, lampadina
put(fx, T_LOGICA - 0.05, ting(2794, 0.5), 0.3); put(fx, T_LOGICA + 0.05, ting(3520, 0.5), 0.22)
# --- la diga: rosicchia, i tronchi cadono uno dopo l'altro; in autostrada: frenata e clacson
for k in range(12): put(fx, T_DIGA + 0.05 + 0.09 * k, crunch(0.08), 0.18)
for k in range(11): put(fx, T_DIGA + 0.25 + 0.115 * k, tronco_giu(85 + 6 * k), 0.26)
put(fx, T_AUTO - 0.25, fischio(0.45, 2600, 1400), 0.14); put(big, T_AUTO + 0.12, crack(0.3), 0.5)
for k, (dt_, f_) in enumerate(((0.3, 420), (0.55, 520), (0.72, 380), (0.95, 470), (1.12, 420))): put(fx, T_AUTO + dt_, clacson(0.22 + 0.1 * (k % 2), f_), 0.12)
# --- contro i prezzi alti: fischio del megafono e bla bla; poi rosicchia la colonna; crollo
t_ = T(0.3); put(fx, T_CONTRO - 0.32, np.sin(2 * np.pi * 3300 * t_) * np.hanning(len(t_)), 0.05)
put(fx, T_CONTRO + 0.0, megafono_voce(1.15), 0.06)
for k in range(15): put(fx, T_ROSI + 0.05 + 0.085 * k, crunch(0.08), 0.2)
put(fx, T_CROLLO - 0.35, cigolio(0.35, 300, 140), 0.3); put(big, T_CROLLO, crollo(), 0.6)
# --- il paese finisce sott'acqua: stop della musica, l'acqua sale, bolle
al = alluvione(T_VOTA - T_ACQUA + 0.4); put(fx, T_ACQUA, al * env(0, len(al) / SR, 0.2, 0.5)[:len(al)], 0.3)
bo = bolle(1.6); put(fx, T_ACQUA + 0.3, bo, 0.25)
sc_ = sciabordio(DUR - T_VOTA); put(fx, T_VOTA, sc_ * env(0, len(sc_) / SR, 0.3, 0.3)[:len(sc_)], 0.07)
# --- in canotto: remate; la papera; il voto; «porca puttana» con l'eco e Tumbo che ulula
for k in range(5): put(fx, T_VOTA + 0.15 + 0.36 * k, schizzo(0.3, 1800), 0.2)
put(fx, T_VOTA + 0.5, verso_pellicano(0.18, 520), 0.16); put(fx, T_VOTA + 0.75, verso_pellicano(0.18, 520), 0.16)
put(fx, T_RESTA + 1.05, whoosh(0.3, 1), 0.25); put(fx, T_RESTA + 1.5, plop(0.2), 0.4)
put(big, T_PORCA + 0.24, dun(49.0, 0.9), 0.5)
for k in range(3): t_ = T(0.5); put(fx, T_PORCA + 0.5 + 0.0 * k, np.zeros(1), 0.0)
t_ = T(0.9); ul = osc(430 * (1 + 0.35 * np.sin(np.pi * t_ / 0.9)), t_) * np.hanning(len(t_)); put(fx, T_PORCA + 0.35, passa_basso(np.tanh(ul * 2), 1800), 0.14)
# --- Rospina festeggia: applausi finti, coriandoli; bonus canotto: cannonata, fischi, cinque ammaraggi
ap2 = applauso(T_BCAN - T_FESTA, 40); put(fx, T_FESTA, ap2 * env(0, len(ap2) / SR, 0.1, 0.1)[:len(ap2)], 0.07)
for k in range(5): put(fx, T_FESTA + 0.1 + 0.12 * k, pop(0.1), 0.22)
put(fx, T_BCAN - 0.5, riser(0.45, 500, 2300), 0.1); put(big, T_BCAN, cannonata(), 0.6)
for k in range(5):
    put(fx, T_BCAN + 0.2 + 0.12 * k, fiuuu(0.8, 1500 - 100 * k, 420), 0.1); put(fx, T_BCAN + 1.05 + 0.12 * k, schizzo(0.5, 1600), 0.35); put(fx, T_BCAN + 1.05 + 0.12 * k, plop(0.25), 0.3)
# --- la domanda: stop, due campanelli (Rospina grave, Castora acuta), rosicchiata, papera
put(fx, T_DOM - 0.06, record_scratch(0.3), 0.25); put(fx, T_DOM + 0.05, ting(1976, 0.35), 0.25); put(fx, T_DOM + 0.72, ting(2637, 0.35), 0.25)
for k in range(4): put(fx, 43.95 + 0.085 * k, crunch(0.08), 0.3)
put(fx, 44.35, verso_pellicano(0.2, 520), 0.2)

big *= (1 - 0.6 * venv)
out = v * 1.0 + mus + np.tanh(fx * 1.1) * 0.45 * (1 - 0.3 * venv) + big * 0.5
out *= np.where(t >= DUR - 0.35, np.clip(1 - (t - DUR + 0.35) / 0.3, 0, 1), 1.0)
h = 256; pk = np.abs(out[:N // h * h]).reshape(-1, h).max(1)
g = np.minimum(1.0, 0.95 / np.maximum(pk, 1e-6)); g = np.minimum(g, np.concatenate([g[1:], g[-1:]])); g = np.convolve(g, np.ones(9) / 9, mode='same')
gg = np.interp(np.arange(N), np.arange(len(g)) * h + h / 2, g); out = np.clip(out * gg, -0.99, 0.99)
ww = wave.open('audio/t030.wav', 'w'); ww.setnchannels(1); ww.setsampwidth(2); ww.setframerate(SR); ww.writeframes((out * 32767).astype(np.int16).tobytes()); ww.close()
print('audio/t030.wav', DUR, 's  riduzione massima del limitatore %.2f a %.2f s; sotto 0.8 per %.2f s' % (float(gg.min()), float(np.argmin(gg)) / SR, float((gg < 0.8).sum()) / SR))
for nome, a, b in (('palazzo', 0, 5.3), ('male', 5.3, 9.8), ('cannone', 9.8, 14.7), ('negozio', 14.7, 21.0), ('castora', 21.0, 25.9), ('diga', 25.9, 32.9), ('acqua', 32.9, 39.7), ('festa', 39.7, 42.8), ('finale', 42.8, 44.8)):
    print('%-9s voce %.3f  musica %.3f  effetti %.3f  impatti %.3f' % (nome, rms(v, a, b), rms(mus, a, b), rms(np.tanh(fx * 1.1) * 0.45, a, b), rms(big * 0.5, a, b)))
