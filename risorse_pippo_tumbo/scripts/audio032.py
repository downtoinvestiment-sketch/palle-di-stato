"""Video 032 (Francesco ci prova) - audio con la SOUND DESIGN TIMELINE del copione n. 36, rifatta sui tempi veri della voce.
Le quattro famiglie musicali (Kevin MacLeod, CC-BY 4.0, vanno citati nella descrizione):
  SUSPENSE = «Spy Glass»   COMICO = «Fluffing a Duck»   EPICO = «Heroic Age»   CAOS = «Hall of the Mountain King»
Effetti della libreria (Kenney, CC0) + effetti costruiti in numpy: l'HUSS di Tumbo (fiato, vocale, sibilo, eco) sopra ogni HUSS della voce,
crunch del telecomando, sveglia, fogli del calendario, cani lontani, finestre, risucchio del mare, onda, alluvione, ciabatta che cigola.
Uso, dalla cartella del progetto: python scripts/audio026.py"""
import sys, os, subprocess, wave
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import suoni as S
SR = 44100; DUR = 38.0; N = int(DUR * SR); rng = np.random.default_rng(32)

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
COMICO, i_c = traccia('comica/Scheming_Weasel_faster', inizio=0.5)
EPICO, i_e = traccia('epica/Heroic_Age', cerca=(10, 120))
CAOS, i_k = traccia('brainrot/Hall_of_the_Mountain_King', cerca=(60, 160))

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

def pipi(d):
    t_ = T(d); n = rng.normal(0, 1, len(t_)); return passa_basso(passa_alto(n, 900), 4200) * (0.7 + 0.3 * np.sin(2 * np.pi * 7 * t_)) * np.minimum(1, t_ * 10) * np.minimum(1, (d - t_) * 6)
def bruciatore(d):
    t_ = T(d); n = rng.normal(0, 1, len(t_)); return (passa_basso(n, 500) * 1.6 + passa_basso(passa_alto(n, 1500), 5000) * 0.4) * np.minimum(1, t_ * 12) * np.minimum(1, (d - t_) * 4)
def scricchiolio(d):
    x = np.zeros(int(d * SR))
    for k in range(int(d * 18)):
        s_ = np.tanh(passa_basso(rng.normal(0, 1, int(0.04 * SR)), 1200) * np.exp(-T(0.04) * 60) * 3); i = int(rng.uniform(0, d - 0.05) * SR); x[i:i + len(s_)] += s_ * rng.uniform(0.3, 1)
    return x + passa_basso(rng.normal(0, 1, len(x)), 120) * np.linspace(0.2, 1, len(x))
def tac():
    s_ = np.tanh(passa_alto(rng.normal(0, 1, int(0.05 * SR)), 1800) * np.exp(-T(0.05) * 80) * 3); return s_ + 0.5 * np.sin(2 * np.pi * 900 * T(0.05)) * np.exp(-T(0.05) * 60)


subprocess.run([S.FFMPEG, '-y', '-loglevel', 'error', '-i', 'audio/voce_t032.mp3', '-ar', str(SR), '-ac', '1', 'audio/voce44_t032.wav'], check=True)
w = wave.open('audio/voce44_t032.wav'); v = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(float) / 32768
DUR = 42.0; N = int(DUR * SR); v = np.pad(v, (0, max(0, N - len(v))))[:N]
_loc = np.sqrt(lp(v ** 2, int(0.35 * SR))); v = v * lp(np.clip(0.115 / (_loc + 0.03), 0.9, 3.0), int(0.25 * SR))
venv = lp(np.abs(v), int(0.12 * SR)); venv = np.clip(venv / (np.percentile(venv, 95) + 1e-9), 0, 1)
T_MA, T_INNAM, T_TOST, T_VANESSA, T_SCRIVE, T_CIAO, T_GHOST = 2.94, 4.40, 6.50, 8.34, 10.56, 11.76, 12.92
T_VOCALE, T_DIECI, T_CENTRI, T_ROSA, T_TOSTA, T_LOGICA = 13.96, 15.48, 16.76, 19.08, 20.72, 22.56
T_MARTE, T_DIMENT, T_TUMBO, T_STORIA, T_SHOCK, T_NOTTE = 24.52, 25.90, 27.68, 29.40, 31.60, 32.22
T_GUARDA, T_LIKE, T_CUORE, T_FIGURA, T_MANDA = 33.56, 35.48, 35.98, 37.90, 39.44
T_LANCIO = 24.95; T_PANE = 7.22

SUSP, i_s = traccia('suspense/Spy_Glass', cerca=(5, 60))
COMICO, i_c = traccia('comica/Fluffing_a_Duck', inizio=1.0)
EPICO, i_e = traccia('epica/Heroic_Age', cerca=(10, 120))
CAOS, i_k = traccia('brainrot/Hall_of_the_Mountain_King', cerca=(60, 160))
print('inizi dei brani (s): suspense %.1f comico %.1f epico %.1f caos %.1f' % (i_s, i_c, i_e, i_k))
mus = np.zeros(N); t = np.arange(N) / SR
def strato(x, a, b, g, fi=0.05, fo=0.05, da=0.0):
    y = np.zeros(N); stendi(y, x, a, b, 1.0, fi, fo, da=da); return y * g
mus += strato(SUSP, 0.0, T_MA - 0.25, 0.15, 0.1, 0.05)                                        # l'urlo alle tre di notte
mus += strato(COMICO, T_MA + 0.15, T_PANE + 0.2, 0.15, 0.05, 0.02)                            # stamattina
mus += strato(COMICO, T_PANE + 0.55, T_GHOST - 0.45, 0.15, 0.02, 0.1, da=4.0)                 # stop secco sul «tostapane», poi riparte
mus += strato(COMICO, T_VOCALE + 0.2, T_LOGICA - 0.25, 0.15, 0.1, 0.1, da=12.0)               # dopo il silenzio del ghostato
mus += strato(EPICO, T_MARTE, T_TUMBO - 0.35, 0.22, 0.02, 0.05)                               # il razzo e Marte
mus += strato(CAOS, T_STORIA - 0.02, T_SHOCK - 0.02, 0.2, 0.02, 0.02)                         # la storia col frigorifero
mus += strato(SUSP, T_NOTTE + 0.3, T_CUORE - 0.05, 0.08, 0.6, 0.02, da=20.0)                  # le tre di notte, piano
mus += strato(CAOS, T_CUORE + 0.45, T_MANDA - 0.1, 0.16, 0.05, 0.1, da=8.0)                    # il panico
mus += strato(COMICO, T_MANDA, DUR, 0.11, 0.3, 0.5, da=25.0)                                  # finale, piano
mus *= (1 - 0.5 * venv) * 2.1

fx = np.zeros(N); big = np.zeros(N)
def sfx(tp, nome, g=1.0):
    try: put(fx, tp, S.carica(nome, SR, volume=g))
    except Exception as e: print('manca', nome, e)
def chiacchiera(d, f0=520):
    """vocale accelerato: sillabe velocissime e acute (voce da criceto)."""
    x = np.zeros(int(d * SR)); tk = 0.0
    while tk < d - 0.06:
        dd = rng.uniform(0.04, 0.08); tt = T(dd); f = f0 * rng.uniform(0.8, 1.35) * (1 + 0.2 * np.sin(2 * np.pi * 9 * tt))
        s_ = passa_basso(np.tanh(saw(f, tt) * 2), 2800) * np.hanning(len(tt)); i = int(tk * SR); x[i:i + len(s_)] += s_[:len(x) - i]; tk += dd + rng.uniform(0.0, 0.03)
    return x
def fantasma(d=0.9):
    tt = T(d); f = 520 * (1 + 0.12 * np.sin(2 * np.pi * 5 * tt)) * (1 - 0.3 * tt / d); return osc(f, tt) * np.hanning(len(tt)) * 0.7 + osc(f * 1.5, tt) * np.hanning(len(tt)) * 0.2
def centrifuga(d):
    tt = T(d); f = 35 + 90 * np.minimum(1, tt / (d * 0.6)); x = osc(f, tt) * 0.8 + passa_basso(rng.normal(0, 1, len(tt)), 400) * 1.2
    for tk in np.arange(0.1, d, 0.18): i = int(tk * SR); s_ = np.tanh(passa_basso(rng.normal(0, 1, int(0.03 * SR)), 900) * np.exp(-T(0.03) * 60) * 3); x[i:i + len(s_)] += s_[:len(x) - i] * 0.6
    return x * np.minimum(1, tt * 4) * np.minimum(1, (d - tt) * 6)
def sfrigolio(d):
    tt = T(d); n = passa_alto(rng.normal(0, 1, len(tt)), 2500); return n * (0.5 + 0.5 * (rng.random(len(tt)) > 0.97)) * np.minimum(1, tt * 20) * np.minimum(1, (d - tt) * 3)
def razzo_rombo(d):
    tt = T(d); n = rng.normal(0, 1, len(tt)); return np.tanh((passa_basso(n, 250) * 3 + passa_basso(n, 1500)) * np.minimum(1, tt * 3) * np.minimum(1, (d - tt) * 2))
def swipe(d=0.18):
    tt = T(d); return passa_basso(passa_alto(rng.normal(0, 1, len(tt)), 1200), 5000) * np.hanning(len(tt))
def allarme(d):
    tt = T(d); f = np.where((tt % 0.4) < 0.2, 880, 660); return passa_basso(np.sign(osc(f, tt)) * 0.4, 2000) * np.minimum(1, tt * 20)
def rewind(d=0.45):
    tt = T(d); f = 300 + 2400 * (tt / d) ** 2; return passa_basso(np.tanh(saw(f, tt) * 2), 4000) * np.hanning(len(tt)) * 0.6 + whoosh(d, -1)[:len(tt)] * 0.5

# hook: ronzio dello schermo e ticchettio
put(fx, 0.0, ronzio(T_MA - 0.1) * env(0, T_MA - 0.1, 0.1, 0.3)[:int((T_MA - 0.1) * SR)], 0.06)
for k in range(4): put(fx, 0.15 + 0.7 * k, ting(3200, 0.05), 0.05)
put(fx, T_MA - 0.25, rewind(0.45), 0.35)                                                      # si riavvolge a stamattina
put(fx, T_INNAM + 0.2, violino([0, 4, 7, 12], 0.4), 0.12)                                     # innamorato
for k in range(5): put(fx, T_INNAM + 0.3 + 0.25 * k, boing(0.25, 600 + 60 * k), 0.06)
put(fx, T_PANE + 0.2, record_scratch(0.4), 0.45)
put(fx, T_VANESSA + 0.3, boing(0.6, 330), 0.12); put(fx, T_VANESSA + 0.5, violino([7, 5, 4], 0.35), 0.08)
for k in range(8): put(fx, T_SCRIVE + 0.25 + 0.13 * k, tac(), 0.12)                           # scrive col pomello
put(fx, T_CIAO + 0.3, ting(2400, 0.25), 0.18)                                                 # messaggio inviato
put(fx, T_GHOST - 0.15, ting(4200, 0.06), 0.15); put(fx, T_GHOST - 0.02, ting(4200, 0.06), 0.15)   # le due spunte blu, nel silenzio
put(fx, T_GHOST + 0.1, fantasma(0.9), 0.14); put(big, T_GHOST + 0.05, boom(0.6, 80, 40), 0.25)
put(fx, T_VOCALE + 0.3, chiacchiera(T_CENTRI - T_VOCALE - 0.4), 0.07)                         # il vocale lunghissimo
put(big, T_DIECI + 0.05, boom(0.8, 70, 35), 0.25); put(fx, T_DIECI + 0.05, boing(0.7, 200), 0.15)
put(fx, T_CENTRI + 0.1, centrifuga(T_ROSA - T_CENTRI - 0.1), 0.22)
put(fx, T_ROSA + 0.9, boing(0.3, 900), 0.1); put(fx, T_ROSA + 0.95, violino([12, 11, 7], 0.25), 0.07)
put(fx, T_TOSTA - 0.25, tac(), 0.4); put(fx, T_TOSTA + 0.02, ting(2900, 0.4), 0.3); put(fx, T_TOSTA + 0.05, sfrigolio(1.2), 0.12)   # clac, dlin, sfrigola
put(big, T_TOSTA + 0.02, boom(0.5, 90, 45), 0.2)
put(fx, T_LOGICA - 0.1, rullo_tamburo(T_MARTE - T_LOGICA), 0.2)
put(fx, T_MARTE, riser(T_LANCIO - T_MARTE + 0.1), 0.12); put(big, T_LANCIO, boom(1.4, 55, 25), 0.45); put(fx, T_LANCIO, razzo_rombo(T_DIMENT - T_LANCIO), 0.3)
put(fx, T_DIMENT, whoosh(0.6, 1), 0.3)
for k in range(3): put(fx, T_TUMBO + 0.35 + 0.18 * k, ting(1800 + 500 * k, 0.15), 0.18)     # il wifi si accende
put(fx, T_TUMBO + 0.1, passa_basso(bau(560), 2200), 0.12)
put(big, T_SHOCK, crack(0.5), 0.5); put(big, T_SHOCK + 0.02, boom(0.8, 70, 35), 0.3)
for k in range(5): put(fx, 0.0 + T_NOTTE + 0.2 + 0.7 * k, ting(3200, 0.05), 0.04)
for k in range(6): put(fx, T_GUARDA + 0.15 + 0.3 * k, swipe(0.16), 0.12)                    # scorre le foto
put(fx, T_CUORE, ting(1900, 0.35), 0.3); put(fx, T_CUORE + 0.02, plop(0.25), 0.25)            # il like
put(fx, T_CUORE + 0.45, allarme(T_FIGURA - T_CUORE - 0.5), 0.08)
put(big, T_FIGURA, boom(1.0, 60, 30), 0.35); put(fx, T_FIGURA + 0.1, sfrigolio(1.5), 0.1)
put(fx, T_MANDA + 0.2, sfrigolio(1.8), 0.08)
big *= (1 - 0.5 * venv)
out = v * 1.0 + mus + np.tanh(fx * 1.1) * 0.45 * (1 - 0.3 * venv) + big * 0.5
out *= np.where(t >= DUR - 0.35, np.clip(1 - (t - DUR + 0.35) / 0.3, 0, 1), 1.0)
h = 256; pk = np.abs(out[:N // h * h]).reshape(-1, h).max(1)
g = np.minimum(1.0, 0.95 / np.maximum(pk, 1e-6)); g = np.minimum(g, np.concatenate([g[1:], g[-1:]])); g = np.convolve(g, np.ones(9) / 9, mode='same')
gg = np.interp(np.arange(N), np.arange(len(g)) * h + h / 2, g); out = np.clip(out * gg, -0.99, 0.99)
ww = wave.open('audio/t032.wav', 'w'); ww.setnchannels(1); ww.setsampwidth(2); ww.setframerate(SR); ww.writeframes((out * 32767).astype(np.int16).tobytes()); ww.close()
def rms(x, a, b): return float(np.sqrt(np.mean(x[int(a * SR):int(b * SR)] ** 2)))
print('audio/t032.wav', DUR, 's  riduzione massima del limitatore %.2f' % float(gg.min()))
for nome, a, b in (('hook', 0, 2.9), ('giardino', 3.0, 22.5), ('marte', 22.6, 29.3), ('storia', 29.4, 32.2), ('notte', 32.3, 42.0)):
    print('%-12s voce %.3f  musica %.3f  effetti %.3f  impatti %.3f' % (nome, rms(v, a, b), rms(mus, a, b), rms(np.tanh(fx * 1.1) * 0.45, a, b), rms(big * 0.5, a, b)))
