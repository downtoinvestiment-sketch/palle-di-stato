"""Test 017 (Il bambino non esce) - audio con la SOUND DESIGN TIMELINE (regole in SOUND_DESIGN.md). Esce audio/t017.wav (41.0 s).
Le quattro famiglie musicali di Pippo e Tumbo (Kevin MacLeod, CC-BY 4.0, vanno citate nella descrizione):
  COMICO = «Sneaky Snitch»   SUSPENSE = «Spy Glass»   EPICO = «Strength of the Titans»   CAOS / DOPPI TWIST = «Galactic Rap» (qui e' la musica della discoteca)
Effetti veri della libreria (Kenney, CC0) + effetti costruiti qui: boom cinematografico, bass drop, riser, whoosh, boing, glitch, grilli, colpo d'orchestra, trombetta, tape stop.
Uso, dalla cartella del progetto: python scripts/audio017.py"""
import sys, os, subprocess, wave
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import suoni as S
SR = 44100; DUR = 44.0; N = int(DUR * SR); rng = np.random.default_rng(17)

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
subprocess.run([S.FFMPEG, '-y', '-loglevel', 'error', '-i', 'audio/voce_t017.mp3', '-ar', str(SR), '-ac', '1', 'audio/voce44_t017.wav'], check=True)
w = wave.open('audio/voce44_t017.wav'); v = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(float) / 32768; v = np.pad(v, (0, max(0, N - len(v))))[:N]
_loc = np.sqrt(lp(v ** 2, int(0.35 * SR))); v = v * lp(np.clip(0.115 / (_loc + 0.03), 0.9, 3.0), int(0.25 * SR))     # la voce sussurrata viene alzata
venv = lp(np.abs(v), int(0.12 * SR)); venv = np.clip(venv / (np.percentile(venv, 95) + 1e-9), 0, 1)

# ---------- tempi (gli stessi di anim017.py) ----------
T_HOOK_IN, T_SLAM, T_SIGN0, T_RESTART = 2.72, 3.86, 4.42, 5.58
T_KNOCK, T_OCC, T_BURG, T_HAND, T_GRAB, T_PULL = 9.20, 10.30, 11.32, 13.02, 14.22, 15.34
T_TUMBO, T_T_IN, T_TNT, T_POL, T_COP, T_C_IN, T_NT2 = 16.20, 17.6, 17.86, 19.16, 20.34, 21.25, 21.44
T_POMP, T_TRUCK, T_TR_IN, T_INDOV, T_PIPPO, T_DIVE, T_P_IN = 22.44, 23.82, 25.2, 25.44, 26.62, 27.0, 27.42
T_GIANT, T_WALK, T_STAND, T_KN2, T_SIGN2 = 40.5, 41.35, 42.3, (42.62, 42.87, 43.12), 43.3
T_BLACK, T_DISCO0, T_REVEAL, T_BABIES, T_COPD, T_DJ, T_BOUNCER, T_GUAL, T_LIST, T_END = 27.45, 28.32, 29.56, 31.05, 32.30, 33.60, 35.25, 37.50, 38.70, 39.75

# ---------- musica: le quattro famiglie ----------
def traccia(rel, inizio=None, cerca=(0, 100), finestra=8.0):
    """carica un brano, lo porta allo stesso volume medio; con inizio=None parte dal punto piu' pieno trovato in `cerca` (secondi)."""
    x = S.carica('musica/' + rel, SR)
    if inizio is None:
        h = int(SR * 0.5); r = np.sqrt(lp(x ** 2, int(finestra * SR))[::h]); a, b = int(cerca[0] * 2), min(len(r), int(cerca[1] * 2))
        inizio = max(0.0, (a + int(np.argmax(r[a:b]))) * 0.5 - finestra / 2)
    y = x[int(inizio * SR):]; y = y / (np.sqrt(np.mean(y[:int(20 * SR)] ** 2)) + 1e-9) * 0.1; return y, inizio
def stendi(buf, x, t0, t1, g, fi=0.05, fo=0.05, da=0.0):
    """mette il brano x nel buffer da t0 a t1 (prendendolo dal secondo `da` del brano) con volume g"""
    seg = np.zeros(N); i0 = int(t0 * SR); s = x[int(da * SR):int(da * SR) + (N - i0)]; seg[i0:i0 + len(s)] = s; buf += seg * env(t0, t1, fi, fo) * g; return seg
COMICO, i_c = traccia('comica/Sneaky_Snitch', inizio=2.0)
SUSPENSE, i_s = traccia('suspense/Spy_Glass', cerca=(10, 80))
EPICO, i_e = traccia('epica/Strength_of_the_Titans', cerca=(15, 120))
CAOS, i_k = traccia('suspense/Galactic_Rap', inizio=24.0)
print('inizi dei brani (s): suspense %.1f, epico %.1f' % (i_s, i_e))

mus = np.zeros(N)
# 0.00 EPICO subito (il camion e' un evento enorme), poi la musica viene risucchiata con il camion: si ovatta e si abbassa
ep = np.zeros(N); stendi(ep, EPICO, 0.0, T_SLAM, 1.0, 0.005, 0.02)
q = ramp(1.7, T_HOOK_IN + 0.05); mus += ovatta(ep, q) * (0.30 - 0.18 * q)
# 3.86 la porticina sbatte: SILENZIO di musica. Dalla porticina esce solo un basso ovattato (l'indizio della discoteca)
gm = np.roll(np.pad(CAOS, (0, max(0, N - len(CAOS))))[:N], int(3.0 * SR)); dietro = passa_basso(gm, 420) * 2.6
porta = env(T_SLAM + 0.5, T_P_IN, 0.8, 0.1) * 0.035
for (a, b) in ((T_HAND - 0.2, T_PULL + 0.85), (T_TUMBO + 0.4, T_T_IN + 0.2), (T_COP + 0.15, T_C_IN + 0.14), (T_TRUCK - 0.1, T_TR_IN + 0.12), (T_PIPPO + 0.15, T_P_IN + 0.05)): porta += env(a, b, 0.12, 0.04) * 0.10
mus += dietro * porta
# 5.58 COMICO (tema di Pippo), con una micro-pausa su «Occupato» e uno stop secco su «Tumbo non torna»
co = np.zeros(N); stendi(co, COMICO, T_RESTART, T_TNT + 0.02, 1.0, 0.4, 0.02)
co *= 1 - env(T_OCC - 0.05, T_OCC + 0.55, 0.02, 0.15); mus += co * 0.11
# 19.1 SUSPENSE: arriva la polizia; si ferma di colpo su «Non torna»
su_ = np.zeros(N); stendi(su_, SUSPENSE, T_POL - 0.08, T_NT2, 1.0, 0.05, 0.02); mus += su_ * 0.13 * ramp(T_POL, T_C_IN, 0.8, 1.25)
# 22.42 EPICO di nuovo, piu' forte: i pompieri. Viene risucchiato con il camion e si spezza in un glitch
ep2 = np.zeros(N); stendi(ep2, EPICO, T_POMP - 0.04, T_TR_IN + 0.04, 1.0, 0.02, 0.02, da=6.0)
q2 = ramp(T_TR_IN - 0.55, T_TR_IN); mus += ovatta(ep2, q2) * 0.24 * ramp(T_POMP, T_TRUCK, 0.85, 1.15)
# 25.44 «Indovinate»: SILENZIO totale (solo la pagina della rivista)
# 26.62 «Allora entra Pippo»: tensione che sale (riser + bordone), poi buio e silenzio, poi il basso da dentro, poi l'impatto
t = np.arange(N) / SR
bordone = (np.sin(2 * np.pi * 55 * t) + 0.4 * np.sin(2 * np.pi * 82.4 * t)) * (0.6 + 0.4 * np.sin(2 * np.pi * 7 * t)); mus += bordone * env(T_PIPPO - 0.1, T_P_IN, 0.6, 0.02) * 0.05
disco = np.zeros(N); i0 = int(T_BLACK * SR); disco[i0:] = CAOS[:N - i0]
mus += ovatta(disco, 1.0) * env(T_BLACK, T_REVEAL, 0.8, 0.01) * 0.09 * (1 - 0.5 * env(T_DISCO0, T_REVEAL, 0.08, 0.01))                                # nel tunnel la festa si avvicina, poi si sente da dietro la porta
# 29.56 «Una DISCOTECA!»: la porta si apre e la musica del caos esplode
dj = disco * env(T_REVEAL, T_BOUNCER, 0.01, 0.05) * 0.20
dj *= 1 - env(T_DJ - 0.1, T_DJ + 0.2, 0.01, 0.02)                                                 # record scratch: la musica si ferma un attimo...
dj += disco * env(T_DJ + 0.2, T_BOUNCER, 0.01, 0.05) * 0.06                                       # ...e riparte piu' forte con la trombetta
tape_stop(dj, T_BOUNCER - 0.1, 0.55)                                                               # 35.15 il buttafuori: il disco si ferma come un giradischi staccato
mus += dj
mus += ovatta(disco, 1.0) * env(T_BOUNCER + 0.6, T_END, 0.6, 0.02) * 0.06                          # fuori dalla corda la festa si sente da lontano
mus += ovatta(disco, 1.0) * env(T_END + 0.05, T_GIANT + 0.3, 0.02, 0.4) * 0.05                      # porta chiusa, festa dietro la porta
mus += passa_basso(disco, 180) * 3.0 * env(T_GIANT, DUR, 0.3, 0.2) * 0.035                         # nel mondo gigante: la festa si sente appena, da dentro la pancia
ep3 = np.zeros(N); stendi(ep3, EPICO, T_GIANT - 0.05, T_STAND + 0.02, 1.0, 0.25, 0.02, da=20.0); mus += ep3 * 0.30   # rivelazione maestosa, si ferma secca prima dei colpi
mus *= (1 - 0.45 * venv) * 2.1                                                                    # volume generale della musica

# ---------- effetti ----------
fx = np.zeros(N); big = np.zeros(N)
def sfx(tp, nome, g=1.0, vel=1.0):
    x = S.carica(nome, SR, volume=g)
    if vel != 1.0: x = np.interp(np.arange(0, len(x), vel), np.arange(len(x)), x)
    put(fx, tp, x)
def sirena(a, b, g=0.06, su=0.0):
    i0, i1 = int(a * SR), min(N, int(b * SR)); tt = np.arange(i1 - i0) / SR; u = tt / max(1e-6, (b - a))
    f = np.where((tt * 2.6) % 1.0 < 0.5, 650.0, 870.0) * (1 + su * u ** 2); amp = np.minimum(1, tt * 8) * np.minimum(1, (b - a - tt) * 6) * (1 - 0.75 * u ** 2)
    fx[i0:i1] += np.sin(2 * np.pi * np.cumsum(f) / SR) * amp * g
def risucchio(tp, k=2, g=0.5): sfx(tp - 0.45, 'phaseJump%d' % k, g)
def plop(tp, g=0.9, k=2): sfx(tp, 'drop_00%d' % k, g)
def sbatte(tp, k=4, g=0.9): sfx(tp, 'doorClose_%d' % k, g); sfx(tp, 'impactWood_heavy_00%d' % (k % 5), g * 0.45)
def apre(tp, k=1, g=0.6): sfx(tp, 'doorOpen_%d' % k, g)
def passi(tp, n, dt, nome, g=0.55):
    for k in range(n): sfx(tp + k * dt, '%s_00%d' % (nome, k % 5), g)
def bip(tp, f, g=0.09, d=0.09): n = int(d * SR); put(fx, tp, np.sin(2 * np.pi * f * T(d)) * np.hanning(n) * g * 2)

# 00.00 HOOK: colpo d'orchestra + sirena subito; il camion vola dentro la porticina con un whoosh e un pop
put(big, 0.0, colpo_orchestra(146.8), 0.55); sirena(0.0, T_HOOK_IN, 0.07, su=0.9)
put(fx, T_HOOK_IN - 0.5, whoosh(0.55, 1), 0.5); plop(T_HOOK_IN, 1.0); put(fx, T_HOOK_IN + 0.02, boing(0.5, 300), 0.18)
put(big, T_SLAM, boom(0.9, 75, 45), 0.4); sbatte(T_SLAM, 4, 1.0); sfx(T_SIGN0, 'switch_005', 0.9); sfx(T_SIGN0 + 0.03, 'tick_002', 0.7)
# sala parto
sfx(7.6, 'bookFlip2', 0.5)
for k in range(3): sfx(T_KNOCK + 0.05 + 0.24 * k, 'impactWood_medium_00%d' % k, 0.85)
sfx(T_OCC, 'switch_005', 0.9); sfx(T_OCC + 0.04, 'error_004', 0.45)
sfx(T_BURG - 0.25, 'creak2', 0.4); sfx(T_BURG, 'impactSoft_heavy_000', 0.6)
apre(T_HAND - 0.2, 1); put(fx, T_HAND + 0.05, boing(0.6, 260), 0.3); sfx(T_GRAB, 'impactSoft_medium_001', 0.75)
put(fx, T_PULL, whoosh(0.6, 1), 0.45); plop(T_PULL + 0.68, 1.0, 3); sbatte(T_PULL + 0.85, 2, 0.85)
passi(T_TUMBO + 0.27, 4, 0.09, 'footstep_carpet', 0.6); apre(T_TUMBO + 0.4, 2, 0.6); risucchio(T_T_IN, 1, 0.45); plop(T_T_IN, 0.9, 1); sbatte(T_T_IN + 0.2, 1, 0.85)
put(fx, T_TNT + 0.15, grilli(1.15), 0.10)                                                         # 17.9 silenzio comico con i grilli
put(fx, T_TNT + 0.4, lp(rng.normal(0, 1, int(0.3 * SR)), 40) * np.hanning(int(0.3 * SR)), 1.0); sfx(T_TNT + 0.93, 'impactPlate_light_002', 0.55); sfx(T_TNT + 0.96, 'metalClick', 0.6)
for k, f in enumerate((941, 1336, 1209)): bip(T_POL - 0.2 + 0.11 * k, f)
passi(T_COP - 0.12, 5, 0.1, 'footstep_concrete', 0.55); apre(T_COP + 0.15, 1, 0.6)
put(fx, T_COP + 0.3, riser(T_C_IN - T_COP - 0.3, 250, 1100), 0.16); put(fx, T_C_IN - 0.35, whoosh(0.4, 1), 0.5); plop(T_C_IN, 0.9, 2); sbatte(T_C_IN + 0.14, 3, 0.85)
put(big, T_NT2 + 0.02, dun(55, 0.9), 0.45); sfx(T_C_IN + 0.5, 'impactSoft_medium_003', 0.7)   # 21.44 «Non torna»: un solo colpo grave
for k, f in enumerate((1209, 1477, 1336, 1477)): bip(T_POMP - 0.3 + 0.08 * k, f * 1.1, 0.1, 0.06)
# 23.82 il camion sfonda il muro: IMPATTO CINEMATOGRAFICO
sirena(T_TRUCK - 0.35, T_TR_IN, 0.08, su=0.9)
put(big, T_TRUCK + 0.02, boom(2.0, 60, 28), 0.85); put(big, T_TRUCK + 0.02, colpo_orchestra(110), 0.45)
sfx(T_TRUCK + 0.03, 'impactPunch_heavy_002', 0.9); put(fx, T_TRUCK + 0.03, lp(rng.normal(0, 1, int(0.9 * SR)), 30) * np.exp(-T(0.9) * 5), 1.5)
for k, dt in enumerate((0.08, 0.2, 0.33, 0.5, 0.7)): sfx(T_TRUCK + dt, 'impactMining_00%d' % (k % 5), 0.7 - 0.1 * k)
put(fx, T_TR_IN - 0.5, whoosh(0.55, 1), 0.55); put(fx, T_TR_IN, glitch(0.35), 0.28); plop(T_TR_IN + 0.02, 1.0, 4); sbatte(T_TR_IN + 0.14, 4, 0.7)
sfx(T_INDOV + 0.05, 'bookFlip1', 0.9)
# 26.62 allora entra Pippo: riser, tuffo, buio e silenzio
sfx(T_PIPPO, 'cloth1', 0.6); sfx(T_PIPPO + 0.2, 'cloth2', 0.6); apre(T_PIPPO + 0.15, 2, 0.6)
put(fx, T_PIPPO, riser(T_P_IN - T_PIPPO, 160, 1600), 0.3); put(fx, T_DIVE, whoosh(T_P_IN - T_DIVE, 1), 0.5); plop(T_P_IN, 1.0, 3); sbatte(T_P_IN + 0.03, 2, 0.9)
# 27.45 TUNNEL di luci: fischio a scivolo che scende, un «vuup» a ogni anello, atterraggio con un boing
_t = T(0.85); put(fx, T_BLACK, osc(1500 * (0.28 ** (_t / 0.85)) * (1 + 0.03 * np.sin(2 * np.pi * 9 * _t)), _t) * np.minimum(1, _t * 30) * np.minimum(1, (0.85 - _t) * 12), 0.22)
for k in range(7):
    v_ = whoosh(0.13, 1); put(fx, T_BLACK + 0.04 + k * 0.12, passa_alto(v_, 900 + 150 * k), 0.55)
put(fx, T_DISCO0 - 0.06, boing(0.45, 180), 0.22); sfx(T_DISCO0 - 0.05, 'impactSoft_heavy_001', 0.7)
# 29.56 «Una DISCOTECA!»: BASS DROP + boom + la musica esplode
put(big, T_REVEAL - 0.02, bass_drop(1.3), 0.7); put(big, T_REVEAL, boom(1.6, 70, 32), 0.6); put(fx, T_REVEAL, passa_alto(rng.normal(0, 1, int(1.2 * SR)), 5000) * np.exp(-T(1.2) * 3), 0.25)
for k, dt in enumerate((0.1, 0.35, 0.55, 0.8, 1.0)): sfx(T_BABIES + dt, 'pepSound%d' % (1 + k % 5), 0.3, vel=1.5)     # i neonati ridono
put(fx, T_COPD + 0.1, fischietto(0.5), 0.07)                                                      # il fischietto del poliziotto
# 33.60 «E il DJ e' TUMBO!»: secondo twist. Record scratch, un attimo di vuoto, trombetta e boom
sfx(T_DJ - 0.12, 'scratch_003', 1.0); put(big, T_DJ + 0.2, trombetta(), 0.32); put(big, T_DJ + 0.2, boom(1.2, 80, 38), 0.5); sfx(T_DJ + 0.9, 'scratch_001', 0.6)
# 35.25 il buttafuori: il disco si ferma (tape stop), passi pesanti
for dt in (0.45, 1.0): put(fx, T_BOUNCER + dt, passa_basso(np.pad(S.carica('impactPunch_heavy_000', SR), (0, SR // 2)), 300), 2.0)
# 37.50 «Gualtiero»: stacco DRAMMATICO, esageratamente serio
put(big, T_GUAL - 0.3, stacco_drammatico(73.4, 2.2), 0.42)
sfx(T_LIST + 0.05, 'bookPlace1', 0.8); sfx(T_LIST + 0.6, 'error_005', 0.5)
# 39.75 la porticina si chiude in faccia a Pippo; il cartello torna su OCCUPATO; Eleonora gira pagina
put(big, T_END, boom(0.8, 80, 45), 0.35); sbatte(T_END, 4, 1.1); sfx(T_END + 0.08, 'switch_005', 0.8)
# 40.5 FINALE: la sala parto era dentro un'Eleonora gigante. Whoosh lungo che si allontana, uccellini, la pagina gigante
put(fx, T_GIANT - 0.1, whoosh(1.2, -1), 0.6)
for k in range(9):
    c_ = T_GIANT + 0.4 + k * 0.33 + 0.07 * np.sin(k * 3.1); f_ = 3200 + 500 * np.sin(k * 1.7); tt_ = T(0.09); put(fx, c_, np.sin(2 * np.pi * (f_ + 1800 * tt_ / 0.09) * tt_) * np.hanning(len(tt_)), 0.05)
sfx(T_GIANT + 0.6, 'bookFlip3', 0.9, vel=0.55)
for k in range(4): put(big, T_WALK + 0.1 + k * 0.285, boom(0.5, 55, 32), 0.32)                   # passi del Pippo gigante
# 42.3 silenzio (la musica si ferma), poi tre colpi ENORMI sulla porticina gigante, poi OCCUPATO
for k_ in T_KN2:
    sfx(k_, 'impactWood_heavy_002', 1.0, vel=0.5); put(big, k_, boom(0.9, 70, 34), 0.55)
put(big, T_SIGN2, colpo_orchestra(98.0, 1.2), 0.5); sfx(T_SIGN2, 'switch_005', 1.0, vel=0.6); sfx(T_SIGN2 + 0.05, 'error_004', 0.6, vel=0.7)

# ---------- mix con limitatore ----------
out = v * 1.0 + mus + np.tanh(fx * 1.1) * 0.45 + big * 0.5
h = 256; pk = np.abs(out[:N // h * h]).reshape(-1, h).max(1)
g = np.minimum(1.0, 0.95 / np.maximum(pk, 1e-6)); g = np.minimum(g, np.concatenate([g[1:], g[-1:]])); g = np.convolve(g, np.ones(9) / 9, mode='same')
gg = np.interp(np.arange(N), np.arange(len(g)) * h + h / 2, g); out = np.clip(out * gg, -0.99, 0.99)
ww = wave.open('audio/t017.wav', 'w'); ww.setnchannels(1); ww.setsampwidth(2); ww.setframerate(SR); ww.writeframes((out * 32767).astype(np.int16).tobytes()); ww.close()
def rms(x, a, b): return float(np.sqrt(np.mean(x[int(a * SR):int(b * SR)] ** 2)))
print('audio/t017.wav', DUR, 's  riduzione massima del limitatore %.2f' % float(gg.min()))
for nome, a, b in (('hook', 0, 2.7), ('sala parto', 6, 10), ('polizia', 19.2, 21.2), ('pompieri', 22.5, 23.8), ('ma che', 28.35, 29.5), ('discoteca', 29.6, 33.5), ('dopo DJ', 33.8, 35.2), ('buttafuori', 35.8, 39.7), ('tunnel', 27.45, 28.3), ('gigante', 40.5, 42.3), ('colpi', 42.6, 44.0)):
    print('%-11s voce %.3f  musica %.3f  effetti %.3f  impatti %.3f' % (nome, rms(v, a, b), rms(mus, a, b), rms(np.tanh(fx * 1.1) * 0.45, a, b), rms(big * 0.5, a, b)))
_b = gg < 0.8; print('limitatore sotto 0.8 per %.2f s; punti:' % (_b.sum() / SR), sorted(set(np.round(np.nonzero(_b)[0][::2000] / SR, 1).tolist()))[:20])
