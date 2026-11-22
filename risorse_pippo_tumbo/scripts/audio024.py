"""Video 024 (Martina, il cono stradale) - audio con la SOUND DESIGN TIMELINE del copione n. 21, rifatta sui tempi veri della voce.
Le quattro famiglie musicali di Pippo e Tumbo, qui con i brani alternativi (Kevin MacLeod, CC-BY 4.0, vanno citati nella descrizione):
  COMICO = «Fluffing a Duck»   SUSPENSE = «Thief in the Night»   EPICO = «Five Armies»   CAOS = «Circus of Freaks»
Effetti della libreria (Kenney, CC0) + effetti costruiti in numpy (violino romantico, record scratch, clacson, rullo, cucchiaino, coni che piovono).
Uso, dalla cartella del progetto: python scripts/audio024.py"""
import sys, os, subprocess, wave
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import suoni as S
SR = 44100; DUR = 45.2; N = int(DUR * SR); rng = np.random.default_rng(24)

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

# ---------- voce ----------
subprocess.run([S.FFMPEG, '-y', '-loglevel', 'error', '-i', 'audio/voce_t024.mp3', '-ar', str(SR), '-ac', '1', 'audio/voce44_t024.wav'], check=True)
w = wave.open('audio/voce44_t024.wav'); v = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(float) / 32768; v = np.pad(v, (0, max(0, N - len(v))))[:N]
_loc = np.sqrt(lp(v ** 2, int(0.35 * SR))); v = v * lp(np.clip(0.115 / (_loc + 0.03), 0.9, 3.0), int(0.25 * SR))
venv = lp(np.abs(v), int(0.12 * SR)); venv = np.clip(venv / (np.percentile(venv, 95) + 1e-9), 0, 1)

# ---------- tempi (gli stessi di anim024_body.py) ----------
T_CUT2, T_FIORI, T_NIENTE, T_ECONO, T_PORCA = 5.0, 7.45, 9.04, 9.82, 10.46
T_CHIUDE, T_40, T_BUCA, T_MINCH, T_COMUNE, T_FLAT, T_BAST = 11.62, 12.72, 14.66, 16.60, 17.62, 18.75, 19.00
T_ALBA, T_POP, T_SU, T_LOGICA = 19.9, 20.45, 21.0, 21.26
T_COMPRA, T_SOLA, T_ITALIA, T_MAPPA, T_NESSUNO = 24.12, 25.95, 27.48, 28.3, 30.66
T_MUOVE, T_SALTO, T_BRACCIA, T_SCAPPA, T_SEMAF = 32.98, 34.38, 35.66, 37.40, 38.12
T_STRONZA, T_TESTA, T_TEAM, T_ROSSO = 38.94, 40.68, 42.84, 44.0
STRETTE = (0.8, 2.3, 3.8)

# ---------- musica: le quattro famiglie ----------
def traccia(rel, inizio=None, cerca=(0, 100), finestra=8.0):
    x = S.carica('musica/' + rel, SR)
    if inizio is None:
        h = int(SR * 0.5); r = np.sqrt(lp(x ** 2, int(finestra * SR))[::h]); a, b = int(cerca[0] * 2), min(len(r), int(cerca[1] * 2))
        inizio = max(0.0, (a + int(np.argmax(r[a:b]))) * 0.5 - finestra / 2)
    y = x[int(inizio * SR):]; y = y / (np.sqrt(np.mean(y[:int(20 * SR)] ** 2)) + 1e-9) * 0.1; return y, inizio
def stendi(buf, x, t0, t1, g, fi=0.05, fo=0.05, da=0.0):
    seg = np.zeros(N); i0 = int(t0 * SR); s = x[int(da * SR):int(da * SR) + (N - i0)]; seg[i0:i0 + len(s)] = s; buf += seg * env(t0, t1, fi, fo) * g; return seg
COMICO, i_c = traccia('comica/Fluffing_a_Duck', inizio=1.0)
SUSPENSE, i_s = traccia('suspense/Thief_in_the_Night', cerca=(5, 60))
EPICO, i_e = traccia('epica/Five_Armies', cerca=(10, 120))
CAOS, i_k = traccia('brainrot/Circus_of_Freaks', cerca=(5, 60))
print('inizi dei brani (s): comico %.1f suspense %.1f epico %.1f caos %.1f' % (i_c, i_s, i_e, i_k))
mus = np.zeros(N); t = np.arange(N) / SR
# 0.00 violino da film d'amore sotto l'insulto (solo effetto, niente base); stop secco col record scratch
VI = violino([7, 5, 4, 7, 12, 11, 9, 7, 5], 0.55); put(mus, 0.05, VI * env(0, len(VI) / SR, 0.3, 0.1)[:len(VI)], 0.07)
mus *= 1 - env(T_CUT2 - 0.02, DUR, 0.01, 0.01)
# 7.45 COMICO basso; micro-pausa su «Niente»
co = np.zeros(N); stendi(co, COMICO, T_FIORI - 0.05, T_CHIUDE - 0.02, 1.0, 0.25, 0.03)
co *= 1 - env(T_NIENTE - 0.03, T_NIENTE + 0.7, 0.02, 0.12); mus += co * 0.09
# 11.62 SUSPENSE: il camion del Comune; stop sul colpo di «dopo 40 anni»
su_ = np.zeros(N); stendi(su_, SUSPENSE, T_CHIUDE - 0.02, T_40 + 0.05, 1.0, 0.1, 0.02); mus += su_ * 0.10
# 14.66 notte: SUSPENSE bassissima e ovattata
su2 = np.zeros(N); stendi(su2, SUSPENSE, T_BUCA, T_FLAT - 0.05, 1.0, 0.4, 0.05, da=10.0); mus += passa_basso(su2, 1200) * 0.08
# 21.26 bordone che sale: «Allora Pippo fa la cosa piu' logica»
bordone = (np.sin(2 * np.pi * 55 * t) + 0.4 * np.sin(2 * np.pi * 82.4 * t)) * (0.6 + 0.4 * np.sin(2 * np.pi * 5 * t)); mus += bordone * env(T_LOGICA - 0.2, T_COMPRA, 0.4, 0.03) * 0.045
# 24.12 EPICO a pieno; si allarga sulla camera che sale; stop secco prima di «Nessuno nota la differenza»
ep = np.zeros(N); stendi(ep, EPICO, T_COMPRA - 0.02, T_NESSUNO - 0.55, 1.0, 0.02, 0.05); mus += ep * 0.25 * ramp(T_COMPRA, T_MAPPA, 1.0, 1.3)
# 35.66 torna il violino del primo secondo (il cambio di musica), si strozza a 37,0
VI2 = violino([7, 9, 12, 11, 12], 0.42); vb = np.zeros(N); put(vb, T_BRACCIA, VI2, 0.08); tape_stop(vb, T_SCAPPA - 0.45, 0.4); mus += vb
# 37.40 CAOS: scappa col semaforo; tape stop su «E quella testa di cazzo»
ka = np.zeros(N); stendi(ka, CAOS, T_SCAPPA - 0.02, DUR, 1.0, 0.02, 0.05); tape_stop(ka, T_TESTA - 0.05, 0.55); mus += ka * 0.22
# 41.5 COMICO ridotto a uno xilofono triste, fino alla fine
XI = xilofono([7, 4, 0, None, 2, 4, 2, -1, 0, None, None, -5], 0.33); put(mus, 41.55, XI, 0.06)
mus *= (1 - 0.45 * venv) * 2.1

# ---------- effetti ----------
fx = np.zeros(N); big = np.zeros(N)
def sfx(tp, nome, g=1.0, vel=1.0):
    x = S.carica(nome, SR, volume=g)
    if vel != 1.0: x = np.interp(np.arange(0, len(x), vel), np.arange(len(x)), x)
    put(fx, tp, x)
# 0.0 i cuori fanno pop; il semaforo fa clic quando lampeggia giallo (indizio sonoro)
for k, tp in enumerate((0.15, 0.55, 1.1)): put(fx, tp, boing(0.25, 520 + 90 * k), 0.12)
for tp in STRETTE: sfx(tp, 'switch_005', 0.25); sfx(tp + 0.5, 'switch_006', 0.18)
# 5.0 record scratch, poi silenzio; i cuori cadono come sassi
put(fx, T_CUT2 - 0.04, record_scratch(0.42), 0.55)
for k in range(3): sfx(T_CUT2 + 0.3 + 0.07 * k, 'impactWood_heavy_00%d' % k, 0.45)
# 7.45 fruscio dei fiori, «fiuuu» quando appassiscono; clacson sul «porca puttana»
sfx(T_FIORI + 0.1, 'cloth1', 0.5); put(fx, T_NIENTE + 0.05, fiuuu(0.75), 0.22)
put(fx, T_PORCA + 0.4, clacson(0.32, 430), 0.35); put(fx, T_PORCA + 0.78, clacson(0.5, 400), 0.35); sfx(T_PORCA + 0.36, 'impactPunch_medium_000', 0.4)
# 11.62 il camion: motore, retromarcia, freno; «dopo 40 anni»: un solo colpo grave e la polvere
put(fx, T_CHIUDE, motore(1.3, 38) * np.hanning(int(1.3 * SR)), 0.28)
for k in range(4): bip(T_CHIUDE + 0.3 + 0.18 * k, 1050, 0.06, 0.09)
sfx(T_40 - 0.2, 'creak1', 0.4); put(big, T_40, dun(55, 1.0), 0.55)
# 14.66 notte: grilli, il lampeggiante che ticchetta, il cucchiaino «tin tin», la terra che vola
gr = grilli(T_FLAT - T_BUCA); put(fx, T_BUCA, gr * env(0, len(gr) / SR, 0.3, 0.2)[:len(gr)], 0.04)
for tb in np.arange(T_BUCA, T_ALBA, 1.0): sfx(tb + 0.01, 'tick_001', 0.25)
for k, tp in enumerate(np.arange(T_BUCA + 0.4, T_COMUNE, 0.31)): put(fx, tp, ting(2900 + 120 * (k % 3)), 0.09)
for k, tp in enumerate(np.arange(T_BUCA + 0.5, T_COMUNE - 0.3, 0.42)): sfx(tp, 'impactMining_00%d' % (k % 5), 0.16)
# 17.62 il rullo: motore che si avvicina, lampeggiante; 18.75 SQUISH, boom, uccellini
rl = motore(T_ALBA - T_COMUNE + 0.3, 33, 1.3); put(fx, T_COMUNE - 0.3, rl * np.minimum(1, T(len(rl) / SR) * 1.2)[:len(rl)] * np.linspace(1, 0.3, len(rl)), 0.45)
put(big, T_FLAT, boom(1.0, 70, 32), 0.55); sfx(T_FLAT, 'impactSoft_heavy_001', 0.9); put(fx, T_FLAT + 0.05, boing(0.6, 140), 0.25)
for k in range(5): put(fx, T_FLAT + 0.35 + 0.18 * k, cinguettio(0.13, 2500 + 200 * (k % 2), 4000), 0.07)
# 19.9 il giorno dopo: un passero; 20.45 si rigonfia (fischio che sale) e POP
put(fx, T_ALBA + 0.15, cinguettio(0.12, 3000, 3600), 0.05); put(fx, T_POP, gonfia(0.5), 0.25); sfx(T_POP + 0.5, 'drop_002', 0.7); put(fx, T_SU, whoosh(0.25, 1), 0.3)
# 21.0 micro-pausa, poi il riser
put(fx, T_LOGICA, riser(T_COMPRA - T_LOGICA, 120, 1500), 0.3)
# 24.12 COLPO D'ORCHESTRA; i coni piovono: toc di plastica a pioggia; clacson in coro
put(big, T_COMPRA, colpo_orchestra(146.8, 1.0), 0.45); put(big, T_COMPRA, boom(1.0, 66, 32), 0.4)
for k in range(70):
    tp = 24.25 + 0.55 + rng.uniform(0, 1.6); put(fx, tp, passa_alto(rng.normal(0, 1, int(0.03 * SR)), 900) * np.exp(-T(0.03) * 90), 0.12 * rng.uniform(0.5, 1.0))
for k in range(8): sfx(24.85 + 0.2 * k, 'impactPlate_light_00%d' % (k % 5), 0.25)
for k, (tp, f) in enumerate(((T_SOLA - 0.3, 410), (T_SOLA + 0.1, 470), (T_SOLA + 0.45, 380), (T_SOLA + 0.7, 520), (T_SOLA + 1.0, 440))): put(fx, tp, clacson(0.4, f), 0.12)
# 27.48 la camera sale: whoosh e vento
put(fx, T_ITALIA, whoosh(0.9, 1), 0.7); put(fx, T_MAPPA, passa_basso(rng.normal(0, 1, int(2.0 * SR)), 400) * np.hanning(int(2.0 * SR)), 0.35)
# 30.1 silenzio vero: «Nessuno nota la differenza» nel vuoto
# 34.38 il primo movimento di Martina: un solo «toc» di plastica
put(fx, T_SALTO - 0.02, boing(0.3, 300), 0.1); sfx(T_SALTO + 0.4, 'impactPlank_medium_000', 0.55)
# 35.66 cuori pop; 37.0 tic tic del lampeggiante, micro-pausa
for k in range(3): put(fx, T_BRACCIA + 0.05 + 0.25 * k, boing(0.25, 560 + 80 * k), 0.1)
for k in range(2): sfx(T_SCAPPA - 0.45 + 0.22 * k, 'switch_005', 0.3)
# 37.40 saltelli «toc toc toc» e whoosh; 38.0 il cuore che si spezza
put(fx, T_SCAPPA, whoosh(0.4, 1), 0.4)
for tp in list(np.arange(T_SCAPPA + 0.35, T_SEMAF + 0.15, 0.36)) + list(np.arange(T_SEMAF + 0.52, T_TESTA, 0.46)): sfx(tp, 'impactPlank_medium_00%d' % rng.integers(0, 5), 0.3)
put(fx, T_SCAPPA + 0.6, crack(0.35), 0.35)
# 38.94 l'occhiolino: due clic gialli; 41.34 colpo comico su «testa di cazzo»
for k in range(2): sfx(T_STRONZA + 0.45 + 0.5 * k, 'switch_006', 0.3)
sfx(41.34, 'impactPunch_heavy_000', 0.45); put(fx, 41.38, boing(0.45, 200), 0.18)
# 44.0 il clic del semaforo che diventa rosso; chiusura
sfx(T_ROSSO, 'switch_007', 0.6); put(big, T_ROSSO + 0.05, dun(49, 0.9), 0.25)

# ---------- mix con limitatore ----------
big *= (1 - 0.45 * venv)
out = v * 1.0 + mus + np.tanh(fx * 1.1) * 0.45 * (1 - 0.3 * venv) + big * 0.5
out *= np.where(t >= DUR - 0.35, np.clip(1 - (t - DUR + 0.35) / 0.3, 0, 1), 1.0)
h = 256; pk = np.abs(out[:N // h * h]).reshape(-1, h).max(1)
g = np.minimum(1.0, 0.95 / np.maximum(pk, 1e-6)); g = np.minimum(g, np.concatenate([g[1:], g[-1:]])); g = np.convolve(g, np.ones(9) / 9, mode='same')
gg = np.interp(np.arange(N), np.arange(len(g)) * h + h / 2, g); out = np.clip(out * gg, -0.99, 0.99)
ww = wave.open('audio/t024.wav', 'w'); ww.setnchannels(1); ww.setsampwidth(2); ww.setframerate(SR); ww.writeframes((out * 32767).astype(np.int16).tobytes()); ww.close()
def rms(x, a, b): return float(np.sqrt(np.mean(x[int(a * SR):int(b * SR)] ** 2)))
print('audio/t024.wav', DUR, 's  riduzione massima del limitatore %.2f' % float(gg.min()))
for nome, a, b in (('hook', 0, 4.9), ('fiori', 7.5, 11.5), ('camion', 11.6, 14.6), ('notte', 14.7, 19.8), ('logica', 21.3, 24.1), ('coni', 24.1, 27.4), ('mappa', 28.3, 30.6), ('scappa', 37.4, 40.6), ('finale', 41.5, 45.0)):
    print('%-8s voce %.3f  musica %.3f  effetti %.3f  impatti %.3f' % (nome, rms(v, a, b), rms(mus, a, b), rms(np.tanh(fx * 1.1) * 0.45, a, b), rms(big * 0.5, a, b)))
