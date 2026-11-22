"""Video 028 (Il pomodoro da undici euro, copione n. 27A) - audio con la SOUND DESIGN TIMELINE del copione, sui tempi veri della voce.
Le quattro famiglie musicali (Kevin MacLeod, CC-BY 4.0, vanno citati nella descrizione):
  SUSPENSE = «Thief in the Night»   COMICO = «Sneaky Snitch» (tema di Pippo)   EPICO = «Five Armies»   CAOS = «Circus of Freaks»
Effetti della libreria (Kenney, CC0) + effetti costruiti in numpy (gli strumenti sono quelli di audio026.py): monete, cassa, timbri, tacchi di Rospina,
la gola che si gonfia e scoppia, fischietto, ali, picchiata, motorino, ticchettio dei quattro secondi, gnam di Tumbo, violino triste, verso del pellicano.
Uso, dalla cartella del progetto: python scripts/audio028.py"""
import sys, os, subprocess, wave
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import suoni as S
SR = 44100; DUR = 44.6; N = int(DUR * SR); rng = np.random.default_rng(28)

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
# VIDEO 028
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

subprocess.run([S.FFMPEG, '-y', '-loglevel', 'error', '-i', 'audio/voce_t028.mp3', '-ar', str(SR), '-ac', '1', 'audio/voce44_t028.wav'], check=True)
w = wave.open('audio/voce44_t028.wav'); v = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(float) / 32768; v = np.pad(v, (0, max(0, N - len(v))))[:N]
_loc = np.sqrt(lp(v ** 2, int(0.35 * SR))); v = v * lp(np.clip(0.115 / (_loc + 0.03), 0.9, 3.0), int(0.25 * SR))
venv = lp(np.abs(v), int(0.12 * SR)); venv = np.clip(venv / (np.percentile(venv, 95) + 1e-9), 0, 1)

T_POM, T_EURO, T_UNO, T_MUTUO, T_30, T_FISSO, T_PER, T_CAZZO1 = 4.12, 5.32, 6.54, 7.30, 8.68, 9.42, 10.24, 11.08
T_ROSP, T_MIN, T_CARO, T_ESISTE, T_VEDE, T_CART, T_GOLA, T_CANOTTO, T_MONT, T_MERDA = 11.94, 13.04, 15.18, 16.06, 16.96, 17.46, 18.02, 19.60, 20.00, 20.82
T_ALLORA, T_LOGICA, T_ADD, T_PELL, T_MANDA, T_PICCHIA, T_PRESA = 21.64, 22.90, 23.72, 24.38, 25.28, 26.45, 26.95
T_GUA, T_PAGA, T_MOTO, T_INCH, T_ASSOLVE, T_ASS, T_QUATTRO, T_CAZZO2 = 27.62, 29.52, 30.38, 31.50, 33.30, 33.52, 33.96, 34.94
T_TUMBO, T_BAST, T_MANGIA, T_GNAM, T_ORA, T_PIRLA, T_RATE, T_EPELL, T_DOMANDA = 35.56, 36.20, 37.58, 37.92, 38.84, 39.52, 40.32, 41.32, 42.70

SUSP, i_s = traccia('suspense/Thief_in_the_Night', cerca=(5, 60))
COMICO, i_c = traccia('comica/Sneaky_Snitch', inizio=1.0)
EPICO, i_e = traccia('epica/Five_Armies', cerca=(10, 120))
CAOS, i_k = traccia('brainrot/Circus_of_Freaks', cerca=(10, 100))
print('inizi dei brani (s): suspense %.1f comico %.1f epico %.1f caos %.1f' % (i_s, i_c, i_e, i_k))
mus = np.zeros(N); t = np.arange(N) / SR
def strato(x, a, b, g, fi=0.05, fo=0.05, da=0.0):
    s_ = np.zeros(N); stendi(s_, x, a, b, 1.0, fi, fo, da); return s_ * g
mus += strato(SUSP, 0.0, T_POM - 0.16, 0.15, 0.2, 0.02) * ramp(0.0, 3.6, 0.7, 1.3)                 # attesa: l'acquisto piu' costoso della sua vita; micro-pausa prima di «un pomodoro»
mus += strato(COMICO, T_POM + 0.25, T_UNO - 0.03, 0.15, 0.03, 0.02)                                   # il pomodoro, undici euro; stop secco su «uno»
mus += strato(EPICO, T_MUTUO - 0.02, T_ROSP - 0.06, 0.2, 0.03, 0.04) * ramp(T_MUTUO, T_CAZZO1, 0.7, 1.25)   # la banca: musica troppo seria per un pomodoro
mus += strato(COMICO, T_MIN - 0.1, T_VEDE - 0.03, 0.14, 0.2, 0.02, da=7.0)                           # Rospina: il tema comico sotto il comizio
mus += strato(SUSP, T_GOLA, T_MERDA - 0.05, 0.14, 0.15, 0.02, da=10.0) * ramp(T_GOLA, T_CANOTTO, 0.7, 1.4)   # la gola si gonfia
mus += strato(CAOS, T_ADD - 0.02, T_INCH - 0.05, 0.22, 0.02, 0.03) * np.where((t > T_GUA) & (t < T_MOTO), 0.7, 1.0)   # il pellicano, Gualtiero, il motorino
mus += strato(EPICO, T_INCH + 0.25, T_ASS - 0.1, 0.13, 0.15, 0.02, da=14.0)                          # l'inchiesta: serissima
mus += strato(COMICO, T_QUATTRO, T_TUMBO - 0.06, 0.16, 0.03, 0.02, da=15.0)                          # assolta: festa
mus *= (1 - 0.5 * venv) * 2.1

fx = np.zeros(N); big = np.zeros(N)
def sfx(tp, nome, g=1.0, vel=1.0):
    try: x = S.carica(nome, SR, volume=g)
    except Exception as e: print('manca', nome, e); return
    if vel != 1.0: x = np.interp(np.arange(0, len(x), vel), np.arange(len(x)), x)
    put(fx, tp, x)
# --- hook: mercato, passi, monete nel sacco; riser e micro-pausa
fo = folla(T_MUTUO); put(fx, 0.0, fo * env(0, T_MUTUO, 0.3, 0.1)[:len(fo)] , 0.05)
for k in range(7): sfx(0.12 + 0.3 * k, 'footstep_concrete_00%d' % (k % 5), 0.35); sfx(0.2 + 0.3 * k, 'handleCoins' if k % 2 else 'handleCoins2', 0.3)
put(fx, 2.3, riser(T_POM - 0.16 - 2.3, 200, 1300), 0.14)
# --- il pomodoro: impatto + coro breve + scintillio; undici euro: cassa; uno: silenzio coi grilli
put(big, T_POM + 0.14, boom(1.2, 70, 34), 0.6); put(big, T_POM + 0.14, colpo_orchestra(196.0, 0.8), 0.45)
for k, f_ in enumerate((2637, 3136, 3951)): put(fx, T_POM + 0.3 + 0.09 * k, ting(f_, 0.4), 0.2)
put(fx, T_EURO + 0.02, whoosh(0.14, 1), 0.3); put(fx, T_EURO + 0.12, cassa(), 0.5)
put(fx, T_UNO - 0.02, record_scratch(0.3), 0.3); gr_ = grilli(T_MUTUO - T_UNO - 0.25); put(fx, T_UNO + 0.2, gr_ * env(0, len(gr_) / SR, 0.05, 0.05)[:len(gr_)], 0.07)
# --- banca: stacco grave, orologio, i due timbri, monete che se ne vanno
put(big, T_MUTUO, dun(49.0, 1.0), 0.5)
for k in range(9): put(fx, T_MUTUO + 0.25 + 0.5 * k, tic(1500 if k % 2 else 1900), 0.12)
for tc in (T_30, T_FISSO): put(fx, tc - 0.2, whoosh(0.2, 1), 0.3); put(big, tc, timbro(), 0.9); sfx(tc, 'impactPunch_heavy_000', 0.35)
put(fx, T_PER + 0.2, fiuuu(0.8, 900, 200), 0.1); sfx(T_CAZZO1 + 0.1, 'handleCoins', 0.4); put(big, T_CAZZO1, dun(41.0, 0.8), 0.45)
# --- Rospina: fanfara, tacchi, microfono che fischia, lo sguardo sul cartellino
put(fx, T_ROSP - 0.04, fanfara(), 0.3)
for k in range(8): put(fx, T_ROSP + 0.25 + 0.21 * k, tacco(1.0), 0.5)
t_ = T(0.35); put(fx, T_CARO - 0.3, np.sin(2 * np.pi * 3100 * t_) * np.hanning(len(t_)), 0.05)                      # il microfono
fo2 = folla(T_VEDE - T_CARO); put(fx, T_CARO, fo2 * env(0, len(fo2) / SR, 0.2, 0.1)[:len(fo2)], 0.035)
put(fx, T_VEDE - 0.03, record_scratch(0.3), 0.3); put(fx, T_CART - 0.05, ting(2100, 0.5), 0.35); put(fx, T_CART - 0.05, cassa(), 0.25)
# --- la gola: si gonfia con uno stridio di gomma, micro-pausa, scoppia e si sgonfia
g1 = gonfia(T_CANOTTO - T_GOLA); put(fx, T_GOLA, g1, 0.22)
for k in range(5): put(fx, T_GOLA + 0.25 + 0.3 * k, cigolio(0.22, 500 + 90 * k, 800 + 120 * k), 0.14)
put(fx, T_MONT + 0.05, riser(T_MERDA - T_MONT - 0.12, 300, 1500), 0.12)
put(big, T_MERDA, pop(0.15), 1.0); put(big, T_MERDA + 0.02, boom(0.9, 80, 40), 0.5); put(fx, T_MERDA + 0.1, pernacchia(0.6), 0.45)
# --- la cosa piu' logica: silenzio, poi la lampadina
put(fx, T_LOGICA - 0.05, ting(2794, 0.5), 0.3); put(fx, T_LOGICA + 0.05, ting(3520, 0.5), 0.22)
# --- il pellicano: fischietto, lancio, presa al volo, ali, picchiata, il furto
tf = T(0.22); put(fx, T_ADD + 0.02, (np.sin(2 * np.pi * 2950 * tf) * (0.6 + 0.4 * np.sign(np.sin(2 * np.pi * 38 * tf)))) * np.hanning(len(tf)), 0.14)
put(fx, T_ADD + 0.34, whoosh(0.3, 1), 0.3); put(fx, T_PELL - 0.04, plop(0.25), 0.5); put(fx, T_PELL + 0.02, verso_pellicano(0.3, 240), 0.3); put(fx, T_PELL + 0.05, boing(0.35, 480), 0.14)
for k in range(8): put(fx, T_MANDA + 0.05 + 0.14 * k, ali(0.13), 0.3)
put(fx, T_PICCHIA - 0.05, fiuuu(T_PRESA - T_PICCHIA, 1700, 320), 0.3)
put(big, T_PRESA, crack(0.3), 0.6); put(fx, T_PRESA, crunch(0.25), 0.5); sfx(T_PRESA + 0.02, 'impactSoft_medium_001', 0.5)
for k in range(4): put(fx, T_PRESA + 0.15 + 0.14 * k, ali(0.13), 0.3)
put(fx, T_PRESA + 0.2, verso_pellicano(0.35, 200), 0.3)
# --- Gualtiero: le monete contate una per una, la zucchina, il motorino
for k in range(4): put(fx, T_GUA + 0.6 + 0.3 * k, ting(1568 + 100 * k, 0.12), 0.1)
put(fx, T_PAGA + 0.3, boing(0.4, 300), 0.16)
mo = motore(0.9, 70.0, 0.6); put(fx, T_MOTO - 0.02, mo * env(0, 0.9, 0.05, 0.3)[:len(mo)], 0.14); put(fx, T_MOTO + 0.28, clacson(0.14, 620), 0.14); put(fx, T_MOTO + 0.48, clacson(0.2, 620), 0.14)
# --- l'inchiesta: stop, colpo grave, quattro tic, timbro ASSOLTA, fanfara
put(fx, T_INCH - 0.05, record_scratch(0.35), 0.35); put(big, T_INCH + 0.12, dun(46.0, 1.0), 0.5)
for k in range(4): put(fx, T_ASSOLVE - 0.92 + 0.23 * k, tic(1700 + 150 * k), 0.3)
put(fx, T_ASS - 0.18, whoosh(0.18, 1), 0.35); put(big, T_ASS, timbro(), 1.0); put(big, T_ASS, boom(1.0, 75, 36), 0.45); sfx(T_ASS, 'impactPunch_heavy_000', 0.4)
put(fx, T_QUATTRO, ting(2637, 0.3), 0.25); put(fx, T_CAZZO2 - 0.08, fanfara((0, 7, 12), 0.1, 523.25, 0.35), 0.26)
# --- Tumbo: silenzio vero, respiro e annusate, micro-pausa, gnam
rs = respiro(T_MANGIA - T_TUMBO - 0.1); put(fx, T_TUMBO + 0.05, rs * env(0, len(rs) / SR, 0.2, 0.05)[:len(rs)], 0.1)
for k in range(4): put(fx, T_BAST + 0.1 + 0.28 * k, passa_alto(rng.normal(0, 1, int(0.09 * SR)), 1800) * np.hanning(int(0.09 * SR)), 0.1)
put(fx, T_MANGIA - 0.02, whoosh(0.3, 1), 0.35); put(fx, T_MANGIA + 0.05, boing(0.3, 420), 0.12)
put(big, T_GNAM, gnam(), 0.9); put(fx, T_GNAM + 0.02, schizzo(0.4, 2400), 0.3); put(big, T_GNAM + 0.36, dun(52.0, 0.7), 0.4)
# --- il finale: violino triste, il rotolo che si srotola, il pellicano atterra, la domanda
vl = violino((0, None, -2, -3, None, -5, -7, None), 0.42, 587.33); put(fx, T_ORA + 0.05, vl * env(0, len(vl) / SR, 0.05, 0.6)[:len(vl)], 0.1)
ro = foglio(1.0); put(fx, T_RATE, ro, 0.3); put(fx, T_RATE + 0.9, plop(0.2), 0.3)
for k in range(3): put(fx, T_EPELL - 0.42 + 0.14 * k, ali(0.13), 0.3)
sfx(T_EPELL + 0.05, 'impactSoft_medium_002', 0.4); put(fx, T_EPELL + 0.2, verso_pellicano(0.4, 190), 0.35)
put(fx, T_DOMANDA - 0.06, record_scratch(0.3), 0.25); put(fx, T_DOMANDA + 0.1, ting(1976, 0.35), 0.25); put(fx, T_DOMANDA + 0.62, ting(2637, 0.35), 0.25)
put(fx, 43.75, verso_pellicano(0.3, 230), 0.3); put(fx, 44.05, boing(0.45, 260), 0.18)

big *= (1 - 0.6 * venv)
out = v * 1.0 + mus + np.tanh(fx * 1.1) * 0.45 * (1 - 0.3 * venv) + big * 0.5
out *= np.where(t >= DUR - 0.35, np.clip(1 - (t - DUR + 0.35) / 0.3, 0, 1), 1.0)
h = 256; pk = np.abs(out[:N // h * h]).reshape(-1, h).max(1)
g = np.minimum(1.0, 0.95 / np.maximum(pk, 1e-6)); g = np.minimum(g, np.concatenate([g[1:], g[-1:]])); g = np.convolve(g, np.ones(9) / 9, mode='same')
gg = np.interp(np.arange(N), np.arange(len(g)) * h + h / 2, g); out = np.clip(out * gg, -0.99, 0.99)
ww = wave.open('audio/t028.wav', 'w'); ww.setnchannels(1); ww.setsampwidth(2); ww.setframerate(SR); ww.writeframes((out * 32767).astype(np.int16).tobytes()); ww.close()
def rms(x, a, b): return float(np.sqrt(np.mean(x[int(a * SR):int(b * SR)] ** 2)))
print('audio/t028.wav', DUR, 's  riduzione massima del limitatore %.2f' % float(gg.min()))
for nome, a, b in (('hook', 0, 4.1), ('pomodoro', 4.1, 7.3), ('banca', 7.3, 11.9), ('rospina', 11.9, 18.0), ('gola', 18.0, 21.6), ('logica', 21.6, 23.7), ('pellicano', 23.7, 27.6), ('gualtiero', 27.6, 31.5),
                   ('inchiesta', 31.5, 35.5), ('tumbo', 35.5, 38.8), ('finale', 38.8, 44.6)):
    print('%-10s voce %.3f  musica %.3f  effetti %.3f  impatti %.3f' % (nome, rms(v, a, b), rms(mus, a, b), rms(np.tanh(fx * 1.1) * 0.45, a, b), rms(big * 0.5, a, b)))
