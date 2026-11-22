"""Video 031 (Il Nobel per la pace, copione n. 33 v3) - audio con la SOUND DESIGN TIMELINE (SOUND_DESIGN.md). Esce audio/t031.wav (38,8 s).
Brani (Kevin MacLeod, CC-BY 4.0, da citare nella descrizione), dentro le quattro famiglie:
  EPICO = «Heroic Age» (il sogno del Nobel, il Nobel a Tumbo)   CAOS = «Circus of Freaks» (le bombe)   COMICO = «Sneaky Snitch» e «Monkeys Spinning Monkeys» (Rospina, la pizza, il finale)
  SUSPENSE = «Danger Storm» (le bombe a mezz'aria)
Strumenti copiati da audio029.py. Uso, dalla cartella del progetto: python scripts/audio031.py"""
import sys, os, subprocess, wave
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import suoni as S
SR = 44100; DUR = 38.8; N = int(DUR * SR); rng = np.random.default_rng(31)

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
subprocess.run([S.FFMPEG, '-y', '-loglevel', 'error', '-i', 'audio/voce_t031.mp3', '-ar', str(SR), '-ac', '1', 'audio/voce44_t031.wav'], check=True)
w = wave.open('audio/voce44_t031.wav'); v = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(float) / 32768; v = np.pad(v, (0, max(0, N - len(v))))[:N]
_loc = np.sqrt(lp(v ** 2, int(0.35 * SR))); v = v * lp(np.clip(0.115 / (_loc + 0.03), 0.9, 3.0), int(0.25 * SR))     # i sussurri «Ma perche'?» vengono alzati
venv = lp(np.abs(v), int(0.12 * SR)); venv = np.clip(venv / (np.percentile(venv, 95) + 1e-9), 0, 1)

# ---------- tempi (gli stessi di anim031.py) ----------
T_SOGNO, T_VOGLIO, T_NOBEL, T_DARLING, T_E, T_BOMB = 1.72, 2.56, 3.04, 4.06, 4.84, 6.02
T_NAZ = (6.60, 7.70, 8.36, 9.18, 10.04)
T_EGU, T_GUAL, T_MA, T_MA2, T_CAZZO = 10.30, 10.84, 12.16, 13.14, 14.12
T_PEACE, T_PEACE2, T_BOOM = 14.86, 15.48, 16.08
T_IO, T_AMICA, T_ELUI, T_ATTACCA, T_CART, T_DATEMI, T_CALCIO = 16.84, 18.04, 18.70, 19.06, 19.96, 20.72, 21.18
T_ALLORA, T_LOGICA, T_TUMBO, T_PIZZA = 21.88, 23.18, 23.90, 25.18
T_BUONA, T_BOMBE, T_CAMB, T_ARIA, T_CADONO, T_CORI, T_PORCA = 25.74, 26.84, 27.08, 27.66, 28.64, 29.60, 30.28
T_NOBEL2, T_VINCE, T_TUMBO2, T_BOMBP, T_PIZZA2, T_MAP, T_TEAM, T_TEAM2, T_END = 31.46, 33.06, 33.32, 33.98, 34.54, 35.30, 36.14, 37.10, 38.4

def traccia(rel, inizio=None, cerca=(0, 100), finestra=8.0):
    x = S.carica('musica/' + rel, SR)
    if inizio is None:
        h = int(SR * 0.5); r = np.sqrt(lp(x ** 2, int(finestra * SR))[::h]); a, b = int(cerca[0] * 2), min(len(r), int(cerca[1] * 2))
        inizio = max(0.0, (a + int(np.argmax(r[a:b]))) * 0.5 - finestra / 2)
    y = x[int(inizio * SR):]; y = y / (np.sqrt(np.mean(y[:int(20 * SR)] ** 2)) + 1e-9) * 0.1; return y, inizio
def stendi(buf, x, t0, t1, g, fi=0.05, fo=0.05, da=0.0):
    seg = np.zeros(N); i0 = int(t0 * SR); s = x[int(da * SR):int(da * SR) + (N - i0)]; seg[i0:i0 + len(s)] = s; buf += seg * env(t0, t1, fi, fo) * g; return seg

EPICO, i_e = traccia('epica/Heroic_Age', cerca=(5, 90))
CAOS, i_k = traccia('brainrot/Circus_of_Freaks', cerca=(10, 120))
COMICO, i_c = traccia('comica/Sneaky_Snitch', inizio=0.3)
COMICO2, i_c2 = traccia('comica/Monkeys_Spinning_Monkeys', inizio=0.2)
SUSPENSE, i_s = traccia('suspense/Danger_Storm', cerca=(5, 80))
print('inizi dei brani (s): epico %.1f, caos %.1f, suspense %.1f' % (i_e, i_k, i_s))
mus = np.zeros(N); t = np.arange(N) / SR
ep = np.zeros(N); stendi(ep, EPICO, 0.0, T_BOMB - 0.05, 1.0, 0.3, 0.05); mus += ep * 0.17                     # il sogno pomposo del Nobel
ca = np.zeros(N); stendi(ca, CAOS, T_BOMB + 0.02, T_MA - 0.02, 1.0, 0.01, 0.02); mus += ca * 0.22               # le bombe, stop secco sul sussurro
co = np.zeros(N); stendi(co, COMICO, T_PEACE - 0.02, T_ALLORA - 0.05, 1.0, 0.02, 0.02)                          # «Peace! Boom!», Rospina, il cartello
co *= 1 - 0.7 * env(T_DATEMI - 0.1, T_DATEMI + 0.45, 0.02, 0.1); mus += co * 0.13                                # micro-pausa sul cartello
co2 = np.zeros(N); stendi(co2, COMICO2, T_ALLORA + 0.25, T_BOMBE - 0.02, 1.0, 0.05, 0.02); mus += co2 * 0.12     # la pizza
su_ = np.zeros(N); stendi(su_, SUSPENSE, T_BOMBE - 0.02, T_CORI - 0.03, 1.0, 0.05, 0.02); mus += su_ * 0.12      # le bombe a mezz'aria
ep2 = np.zeros(N); stendi(ep2, EPICO, T_CORI, T_BOMBP - 0.02, 1.0, 0.02, 0.02, da=25.0); mus += ep2 * 0.2        # coriandoli e Nobel a Tumbo
tape_stop(ep2, T_BOMBP - 0.3, 0.3)
co3 = np.zeros(N); stendi(co3, COMICO2, T_TEAM + 0.02, T_END, 1.0, 0.02, 0.4, da=12.0); mus += co3 * 0.13        # finale coi coriandoli
mus *= (1 - 0.45 * venv) * 2.0

# ---------- effetti ----------
fx = np.zeros(N); big = np.zeros(N)
def sfx(tp, nome, g=1.0, vel=1.0):
    x = S.carica(nome, SR, volume=g)
    if vel != 1.0: x = np.interp(np.arange(0, len(x), vel), np.arange(len(x)), x)
    put(fx, tp, x)
def bip(tp, f, g=0.09, d=0.09): n = int(d * SR); put(fx, tp, np.sin(2 * np.pi * f * T(d)) * np.hanning(n) * g * 2)
def applausi(tp, d, g=0.05):
    tt = T(d); x = np.zeros(len(tt))
    for k in range(int(d * 40)):
        i = rng.integers(0, len(tt) - 800); x[i:i + 800] += passa_alto(rng.normal(0, 1, 800), 1200) * np.exp(-np.arange(800) / 120.0) * rng.uniform(0.4, 1.0)
    put(fx, tp, x * np.minimum(1, tt * 3) * np.minimum(1, (d - tt) * 2) * g)
def fischio_bomba(tp, d=0.6, g=0.12):
    """la bomba che cade: fischio che scende"""
    tt = T(d); f = 2200 * np.exp(-tt / d * 1.3) + 400; put(fx, tp, np.sin(2 * np.pi * np.cumsum(f) / SR) * np.minimum(1, tt * 8) * g)
def frenata(tp, g=0.12):
    d = 0.35; tt = T(d); x = passa_alto(rng.normal(0, 1, len(tt)), 1800) * 0.4 + np.sin(2 * np.pi * np.cumsum(1300 - 600 * tt / d) / SR) * 0.6
    put(fx, tp, x * np.sin(np.pi * tt / d) * g)
def pop(tp, g=0.25):
    d = 0.08; tt = T(d); put(fx, tp, np.sin(2 * np.pi * np.cumsum(900 * np.exp(-tt * 40) + 200) / SR) * np.exp(-tt * 40) * g)
def ding(tp, g=0.2):
    d = 1.2; tt = T(d); put(fx, tp, (np.sin(2 * np.pi * 1568 * tt) + 0.5 * np.sin(2 * np.pi * 3136 * tt)) * np.exp(-tt * 3.5) * g)
def sfrigola(tp, d, g=0.05):
    tt = T(d); put(fx, tp, passa_alto(rng.normal(0, 1, len(tt)), 3000) * (0.6 + 0.4 * rng.random(len(tt)) ** 6) * np.minimum(1, tt * 4) * np.minimum(1, (d - tt) * 4) * g)
def scotch(tp, g=0.15):
    d = 0.3; tt = T(d); put(fx, tp, passa_alto(rng.normal(0, 1, len(tt)), 1500) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 45 * tt))) * np.exp(-tt * 6) * g)

# 0.00 il sogno: campanellino magico, la medaglia appare
put(fx, T_SOGNO - 0.05, riser(0.3, 600, 2000), 0.12); ding(T_SOGNO + 0.05, 0.18)
sfx(T_NOBEL - 0.02, 'impactBell_heavy_000', 0.5)
# 4.84 la mano sopra il bottone: dun; 6.02 CLICK, la musica epica si stacca, caos
put(big, T_E + 0.05, dun(55, 0.8), 0.3)
sfx(T_BOMB, 'click_003', 1.0); put(big, T_BOMB + 0.02, dun(45, 0.6), 0.4)
for k, tn in enumerate(T_NAZ):
    fischio_bomba(tn - 0.65, 0.62, 0.1)
    put(big, tn + 0.03, boom(1.4, 62 - 4 * k, 28), 0.42); sfx(tn + 0.02, 'explosionCrunch_00%d' % (k % 5), 0.7)
put(fx, T_NAZ[0] + 0.3, whoosh(0.7, 1), 0.4)                                                          # il mappamondo gira dal Venezuela al Medio Oriente
# 10.30 «E Gualtiero!»: fischio, boom grosso, lui vola via (whoosh), ricade (tonfo)
fischio_bomba(T_GUAL - 0.55, 0.65, 0.13); put(big, T_GUAL + 0.12, boom(2.0, 70, 26), 0.6); sfx(T_GUAL + 0.14, 'lowFrequency_explosion_001', 0.8)
put(fx, T_GUAL + 0.3, whoosh(0.8, 1), 0.4); sfx(T_MA - 0.12, 'impactSoft_heavy_001', 0.8); put(fx, T_MA - 0.08, boing(0.5, 160), 0.2)
# 12.16 «Ma perche'?»: silenzio vero (solo un grillo); 13.14 «MA PERCHE', CAZZO?!»: colpo d'orchestra
put(fx, T_MA + 0.1, grilli(0.9), 0.02)
put(big, T_MA2 - 0.02, colpo_orchestra(98.0, 1.0), 0.4); put(big, T_MA2, boom(0.9, 60, 32), 0.35)
# 14.86 «Peace! Peace! Boom!»: due «bling», poi il pugno sul bottone e un boom lontano
ding(T_PEACE + 0.05, 0.12); ding(T_PEACE2 + 0.05, 0.12)
sfx(T_BOOM - 0.02, 'click_003', 1.0); put(big, T_BOOM + 0.25, ovatta(boom(1.8, 55, 25), 0.7)[:int(1.8 * SR)], 0.3)
# 16.84 Rospina: tacchi; 19.06 lo scotch del cartello; 20.72 «Datemi un calcio»: record scratch e boing
for k in range(4): sfx(T_IO - 0.6 + 0.15 * k, 'footstep_concrete_00%d' % (k % 5), 0.35, vel=1.3)
scotch(T_ATTACCA + 0.4); sfx(T_ATTACCA + 0.48, 'impactSoft_medium_000', 0.5)
sfx(T_DATEMI - 0.12, 'scratch_003', 0.7); put(fx, T_CALCIO + 0.05, boing(0.5, 210), 0.25)
# 21.88 la cosa piu' logica: whoosh; 23.90 il cappello da cuoco: pop; il forno che crepita
put(fx, T_ALLORA - 0.1, whoosh(0.4, 1), 0.4); pop(T_TUMBO + 0.12, 0.3); sfrigola(T_ALLORA + 0.2, T_BOMBE - T_ALLORA - 0.3, 0.04)
for k in range(3): bip(T_TUMBO + 0.6 + 0.3 * k, 880 + 220 * k, 0.03, 0.07)                                        # Tumbo che saltella
# 25.74 la pizza esce dal forno: whoosh e «ding» da forno; un «mmmh» di cori (accordo dolce)
put(fx, T_BUONA - 0.05, whoosh(0.5, 1), 0.35); ding(T_BUONA + 0.5, 0.2)
tt = T(1.2); put(fx, T_BUONA + 0.55, sum(np.sin(2 * np.pi * f * tt) for f in (523, 659, 784)) * np.sin(np.pi * tt / 1.2) ** 2 * 0.03)
# 26.84 le bombe in volo, 27.08 frenano e si girano; 27.66 sospese; 28.64 cadono (fischio + riser); 29.60 POP coriandoli + trombette
put(fx, T_BOMBE - 0.1, whoosh(0.4, 1), 0.45)
for k in range(3): frenata(T_CAMB + 0.05 * k, 0.12)
for k in range(3): put(fx, T_ARIA + 0.2 + 0.12 * k, boing(0.4, 260 + 50 * k), 0.15)
fischio_bomba(T_CADONO, T_CORI - T_CADONO, 0.1); put(fx, T_CADONO, riser(T_CORI - T_CADONO, 200, 1400), 0.18)
for k in range(3): pop(T_CORI + 0.08 * k, 0.4); sfx(T_CORI + 0.08 * k, 'impactPlate_light_00%d' % k, 0.4)
put(big, T_CORI, trombetta(), 0.28); applausi(T_CORI + 0.1, 1.6, 0.05)
put(big, T_PORCA, dun(65, 0.6), 0.25)
# 31.46 il Nobel per la pace...: rullo di tamburi; 33.32 Tumbo: colpo d'orchestra, applausi, trombetta
tt = T(T_TUMBO2 - T_NOBEL2 - 0.5); put(fx, T_NOBEL2 + 0.4, passa_basso(rng.normal(0, 1, len(tt)), 900) * (0.6 + 0.4 * np.sign(np.sin(2 * np.pi * 14 * tt))) * np.minimum(1, tt) * 0.12)
put(big, T_TUMBO2 - 0.02, colpo_orchestra(130.8, 1.0), 0.45); applausi(T_TUMBO2, T_BOMBP - T_TUMBO2, 0.07); put(big, T_TUMBO2 + 0.1, trombetta(), 0.2)
# 33.98 «Bomb the pizza!»: la musica si ferma (tape stop), pugni sul bottone
for k in range(3): sfx(T_BOMBP + 0.17 + 0.35 * k, 'click_003', 0.9); put(big, T_BOMBP + 0.19 + 0.35 * k, dun(50, 0.4), 0.25)
# 35.30 «Ma perche'?»: fischio della bomba che cade, si pianta nel tavolo (tonfo + boing tremolante)
fischio_bomba(T_MAP - 0.05, 0.5, 0.11); sfx(T_MAP + 0.45, 'impactWood_heavy_002', 0.9); put(fx, T_MAP + 0.5, boing(0.6, 140), 0.25)
# 36.14 POP coriandoli: trombette, Tumbo che mangia la pizza
for k in range(2): pop(T_TEAM + 0.05 * k, 0.45)
put(big, T_TEAM, trombetta(), 0.3); sfx(T_TEAM + 0.75, 'drop_002', 0.6)
for k in range(4): put(fx, T_TEAM + 0.9 + 0.22 * k, np.sin(2 * np.pi * 300 * T(0.06)) * np.hanning(int(0.06 * SR)), 0.05)       # morsi
sfx(T_END - 0.05, 'drop_001', 0.9)

# ---------- mix con limitatore ----------
out = v * 1.0 + mus + np.tanh(fx * 1.1) * 0.45 + big * 0.5
out *= env(0, T_END + 0.35, 0.002, 0.04)
h = 256; pk = np.abs(out[:N // h * h]).reshape(-1, h).max(1)
g = np.minimum(1.0, 0.95 / np.maximum(pk, 1e-6)); g = np.minimum(g, np.concatenate([g[1:], g[-1:]])); g = np.convolve(g, np.ones(9) / 9, mode='same')
gg = np.interp(np.arange(N), np.arange(len(g)) * h + h / 2, g); out = np.clip(out * gg, -0.99, 0.99)
ww = wave.open('audio/t031.wav', 'w'); ww.setnchannels(1); ww.setsampwidth(2); ww.setframerate(SR); ww.writeframes((out * 32767).astype(np.int16).tobytes()); ww.close()
def rms(x, a, b): return float(np.sqrt(np.mean(x[int(a * SR):int(b * SR)] ** 2)))
print('audio/t031.wav', DUR, 's  riduzione massima del limitatore %.2f' % float(gg.min()))
for nome, a, b in (('sogno', 0, 6.0), ('bombe', 6.0, 10.3), ('gualtiero', 10.3, 12.1), ('perche', 12.1, 14.8), ('peace', 14.8, 16.8), ('rospina', 16.8, 21.8), ('pizza', 21.9, 26.8), ('mezzaria', 26.8, 31.4), ('nobel', 31.4, 34.0), ('finale', 34.0, 38.4)):
    print('%-10s voce %.3f  musica %.3f  effetti %.3f  impatti %.3f' % (nome, rms(v, a, b), rms(mus, a, b), rms(np.tanh(fx * 1.1) * 0.45, a, b), rms(big * 0.5, a, b)))
