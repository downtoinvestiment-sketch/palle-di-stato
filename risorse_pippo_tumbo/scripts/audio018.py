"""Test 018 (La mente, presentazione di Giulia) - audio con la SOUND DESIGN TIMELINE (regole in SOUND_DESIGN.md, timeline del copione n. 10). Esce audio/t018.wav (49.5 s, voce con gli insulti).
Le quattro famiglie musicali (Kevin MacLeod, CC-BY 4.0, da citare nella descrizione), con i brani alternativi per variare:
  EPICO = «Five Armies»   COMICO = «Scheming Weasel»   SUSPENSE = «Thief in the Night»   CAOS / DOPPI TWIST = «Hall of the Mountain King»
Effetti: Kenney (CC0), il kit Mixkit dell'autore (audio/sfx/mixkit, licenza libera anche per video monetizzati) e quelli costruiti qui
(boom, bass drop, riser, whoosh, boing, glitch, grilli, colpo d'orchestra, stacco drammatico, tape stop, sciacquone).
Uso, dalla cartella del progetto: python scripts/audio018.py"""
import sys, os, subprocess, wave
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import suoni as S
SR = 44100; DUR = 49.5; N = int(DUR * SR); rng = np.random.default_rng(18)

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

# ---------- voce ----------
subprocess.run([S.FFMPEG, '-y', '-loglevel', 'error', '-i', 'audio/voce_t018.mp3', '-ar', str(SR), '-ac', '1', 'audio/voce44_t018.wav'], check=True)
w = wave.open('audio/voce44_t018.wav'); v = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(float) / 32768; v = np.pad(v, (0, max(0, N - len(v))))[:N]
_loc = np.sqrt(lp(v ** 2, int(0.35 * SR))); v = v * lp(np.clip(0.115 / (_loc + 0.03), 0.9, 3.0), int(0.25 * SR))     # la voce sussurrata viene alzata
venv = lp(np.abs(v), int(0.12 * SR)); venv = np.clip(venv / (np.percentile(venv, 95) + 1e-9), 0, 1)

# ---------- tempi (gli stessi di anim018_body.py) ----------
T_FLASH = 7.58; T_LOCK = 10.32; T_CASS = 11.76; T_BUILD = 15.02; T_CAZZO = 16.26; T_BASE = T_BUILD + 0.25
T_CAMS, T_LASER, T_MOAT = 18.24, 18.98, 19.54; T_DANCE, T_BALL = 20.18, 21.54; T_DOOR, T_TUMBO = 23.02, 24.12
T_ROOM = 25.15; T_WATCH, T_ZOOM, T_EYES = 26.66, 28.34, 29.26; T_KNOCK = 31.46; T_KK = 32.32
T_MACHE, T_GIULIA, T_GUIDA = 33.96, 35.20, 37.74; T_KT, T_KTK, T_ALTRA = 39.34, 40.62, 41.70
T_SELF, T_SELFK, T_OCC = 44.14, 45.00, 45.88; T_FLUSH, T_BLACK = 47.40, 48.85

# ---------- musica ----------
def traccia(rel, inizio=None, cerca=(0, 100), finestra=8.0):
    x = S.carica('musica/' + rel, SR)
    if inizio is None:
        h = int(SR * 0.5); r = np.sqrt(lp(x ** 2, int(finestra * SR))[::h]); a, b = int(cerca[0] * 2), min(len(r), int(cerca[1] * 2))
        inizio = max(0.0, (a + int(np.argmax(r[a:b]))) * 0.5 - finestra / 2)
    y = x[int(inizio * SR):]; y = y / (np.sqrt(np.mean(y[:int(20 * SR)] ** 2)) + 1e-9) * 0.1; return y, inizio
def stendi(buf, x, t0, t1, g, fi=0.05, fo=0.05, da=0.0):
    seg = np.zeros(N); i0 = int(t0 * SR); s = x[int(da * SR):int(da * SR) + (N - i0)]; seg[i0:i0 + len(s)] = s; buf += seg * env(t0, t1, fi, fo) * g; return seg
EPICO, i_e = traccia('epica/Five_Armies', cerca=(10, 120))
COMICO, i_c = traccia('comica/Scheming_Weasel_faster', inizio=1.0)
SUSPENSE, i_s = traccia('suspense/Thief_in_the_Night', cerca=(5, 90))
CAOS, i_k = traccia('brainrot/Hall_of_the_Mountain_King', cerca=(60, 160))
print('inizi dei brani (s): epico %.1f, suspense %.1f, caos %.1f' % (i_e, i_s, i_k))

mus = np.zeros(N)
# 00.00 EPICO subito: Gualtiero sullo squalo. A 2.9 «per un giornale» la musica si ferma come un giradischi
ep = np.zeros(N); stendi(ep, EPICO, 0.0, 6.7, 1.0, 0.005, 0.02); tape_stop(ep, 6.05, 0.55); mus += ep * 0.26
# 05.4 COMICO (tema delle mosse di Gualtiero), si ferma su «la cassetta» per un attimo
co = np.zeros(N); stendi(co, COMICO, T_FLASH, T_BUILD - 0.05, 1.0, 0.3, 0.05); co *= 1 - env(14.25, 14.85, 0.02, 0.1); mus += co * 0.12
# 12.3 EPICO forte: UNA C***O DI BASE. Cresce fino al fossato, poi si ferma secco
ep2 = np.zeros(N); stendi(ep2, EPICO, T_BUILD - 0.02, T_DANCE - 0.05, 1.0, 0.01, 0.03, da=10.0); mus += ep2 * 0.26 * ramp(T_BUILD, T_MOAT, 0.9, 1.2)
# 18.72 COMICO di nuovo, piu' forte: Gualtiero balla tra i laser; continua sulla porta blindata
co2 = np.zeros(N); stendi(co2, COMICO, T_DANCE, T_ROOM, 1.0, 0.02, 0.03, da=14.0); mus += co2 * 0.15
# 23.25 stop: grilli (Pippo si gira, Tumbo scodinzola). 24.18 SUSPENSE: le telecamere
su_ = np.zeros(N); stendi(su_, SUSPENSE, T_WATCH - 0.05, T_KNOCK, 1.0, 0.25, 0.04); mus += su_ * 0.14 * ramp(T_WATCH, T_KNOCK, 0.85, 1.25)
# 30.32 silenzio: Pippo va a bussare. 34.5 CAOS: «Dentro c'e' GIULIA»
ca = np.zeros(N); stendi(ca, CAOS, T_GIULIA - 0.02, T_KT - 0.15, 1.0, 0.01, 0.03); mus += ca * 0.2
# 38.4 record scratch e vuoto; 41.3 «Un'altra Giulia» lo stacco drammatico; poi il caos riparte piano fino all'ultima riga
ca2 = np.zeros(N); stendi(ca2, CAOS, T_ALTRA + 0.9, T_SELF - 0.05, 1.0, 0.3, 0.3, da=8.0); mus += ovatta(ca2, 0.5) * 0.12
mus *= (1 - 0.45 * venv) * 2.1

# ---------- effetti ----------
fx = np.zeros(N); big = np.zeros(N)
def sfx(tp, nome, g=1.0, vel=1.0):
    x = S.carica(nome, SR, volume=g)
    if vel != 1.0: x = np.interp(np.arange(0, len(x), vel), np.arange(len(x)), x)
    put(fx, tp, x)
def sirena_base(a, b, g=0.05):
    i0, i1 = int(a * SR), min(N, int(b * SR)); tt = np.arange(i1 - i0) / SR
    f = 520 + 380 * ((tt * 1.6) % 1.0); fx[i0:i1] += np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.4 * np.minimum(1, tt * 8) * np.minimum(1, (b - a - tt) * 6) * g
def passo_robot(tp, g=0.5): sfx(tp, 'footstep_grass_00%d' % int(tp * 7 % 5), g * 0.8); put(fx, tp + 0.02, servo(0.18, 700 + 200 * (tp % 1)), g * 0.18)
def toc(tp, g=0.9, sordo=False):
    x = S.carica('impactWood_light_00%d' % int(tp * 3 % 5), SR, volume=g)
    if sordo: x = passa_basso(np.pad(x, (0, 2000)), 900) * 1.6
    put(fx, tp, x)

# 00.00 HOOK: colpo d'orchestra, onde, sirena d'allarme della base
put(big, 0.0, colpo_orchestra(110), 0.55); sirena_base(0.0, 4.1, 0.05); put(big, 4.2, colpo_orchestra(146.8), 0.35); sfx(0.05, 'mk_Cinematic_whoosh_fast_transition', 0.5)
for k in range(10): put(fx, 0.2 + k * 0.6, passa_basso(rng.normal(0, 1, int(0.5 * SR)), 900) * np.hanning(int(0.5 * SR)), 0.35)        # onde del fossato
put(fx, 1.2, sbuffo(0.3), 0.25)
sfx(6.1, 'bookFlip2', 0.7)                                                                           # «per un giornale»: fruscio
put(fx, 4.5, sbuffo(0.3), 0.22)
# 05.4 ogni mattina: passi a scatti con il servo (indizio), sportello della cassetta
sfx(T_FLASH + 0.05, 'mk_Fast_small_sweep_transition', 0.45)
sfx(T_FLASH + 0.15, 'metalClick', 0.6); sfx(T_FLASH + 0.5, 'bookFlip1', 0.6)
for k in range(10): passo_robot(T_FLASH + 0.75 + k * 0.28, 0.55)
put(fx, T_FLASH + 0.9, sbuffo(0.3), 0.2)
# 08.34 il lucchetto: clac soddisfatto
sfx(T_LOCK + 0.62, 'mk_Hard_pop_click', 0.8); sfx(T_LOCK + 0.64, 'impactMetal_light_002', 0.6)
# 10.08 si porta via la cassetta: strappo del palo e del marciapiede, poi passi a scatti
for k in range(3): passo_robot(T_CASS - 0.3 + k * 0.25, 0.5)
sfx(T_CASS + 0.75, 'impactMining_002', 0.9); sfx(T_CASS + 0.78, 'impactPlank_medium_003', 0.7); put(big, T_CASS + 0.75, dun(62, 0.6), 0.3)
for k in range(5): passo_robot(T_CASS + 1.0 + k * 0.26, 0.5)
sfx(14.3, 'mk_Trombone_disappoint', 0.35)
# 12.3 UNA C***O DI BASE: transizione orchestrale, martellate, trapano, le mura salgono con un boom
sfx(T_BUILD - 0.1, 'mk_Epic_orchestra_transition', 0.45)
for k in range(6): sfx(T_BUILD + 0.1 + k * 0.16, 'impactMetal_medium_00%d' % (k % 5), 0.55)
put(fx, T_BASE, lp(rng.normal(0, 1, int(1.2 * SR)), 25) * np.minimum(1, T(1.2) * 4) * np.exp(-T(1.2) * 1.5), 1.6)      # rombo delle mura che salgono
put(big, T_BASE + 1.05, boom(1.6, 62, 30), 0.65); sfx(T_BASE + 1.05, 'impactPunch_heavy_002', 0.7)
put(big, T_CAZZO, colpo_orchestra(146.8), 0.4)
# 15.76 telecamere: quattro clic con il servo; 16.62 laser: zap; 17.14 fossato: onde e pinne
for k in range(5): sfx(T_CAMS + 0.08 * k, 'mk_Hard_pop_click', 0.5); put(fx, T_CAMS + 0.08 * k + 0.05, servo(0.2, 1200 + 150 * k), 0.12)
sfx(T_LASER, 'laserLarge_001', 0.6); sfx(T_LASER + 0.05, 'forceField_002', 0.45)
put(fx, T_MOAT - 0.05, whoosh(0.5, 1), 0.4)
for k in range(3): put(fx, T_MOAT + 0.1 + k * 0.45, passa_basso(rng.normal(0, 1, int(0.4 * SR)), 1200) * np.hanning(int(0.4 * SR)), 0.4)
sfx(T_MOAT + 0.9, 'mk_Funny_cartoon_fast_splat', 0.35)
# 18.6 si passa alla telecamera: bip. 18.72 il ballo: ronzio dei laser, scricchiolii a tempo
put(fx, T_DANCE - 0.1, np.sin(2 * np.pi * 1800 * T(0.08)) * np.hanning(int(0.08 * SR)), 0.12)
put(fx, T_DANCE, np.sin(2 * np.pi * 120 * T(T_DOOR - T_DANCE)) * 0.5 * (0.6 + 0.4 * np.sin(2 * np.pi * 3 * T(T_DOOR - T_DANCE))), 0.05)
for k in range(8): sfx(T_DANCE + 0.15 + k * 0.33, 'footstep_grass_00%d' % (k % 5), 0.45)
sfx(T_BALL - 0.05, 'mk_Boing_hit_sound', 0.4)
# 21.62 la porta blindata: Tumbo gira la ruota (cigolio), la porta si apre, vapore dall'orecchio
put(fx, T_DOOR + 0.1, cigolio(0.9, 260), 0.25); put(fx, T_TUMBO - 0.4, sbuffo(0.3), 0.25); put(fx, T_TUMBO + 0.2, sbuffo(0.3), 0.25)
sfx(T_TUMBO + 0.15, 'doorOpen_001', 0.8); put(big, T_TUMBO + 0.2, dun(48, 0.8), 0.3)
for k in range(4): passo_robot(T_TUMBO + 0.4 + k * 0.27, 0.45)
# 23.25 sala di controllo: stop, grilli; Tumbo scodinzola
sfx(T_ROOM + 0.05, 'mk_Summer_crickets_loop', 0.18)
# 24.18 le telecamere: ronzio dei computer; 26.66 zoom a scatti; vapore
sfx(T_WATCH, 'computerNoise_001', 0.12)
for k in range(3): sfx(T_ZOOM + 0.33 * k, 'mk_Quick_zoom_impact', 0.45 - 0.05 * k)
put(fx, T_EYES + 0.3, sbuffo(0.35), 0.3); put(fx, T_EYES + 1.3, sbuffo(0.35), 0.3)
put(fx, T_EYES, riser(T_KNOCK - T_EYES, 180, 900), 0.10)
# 30.32 Pippo va a bussare: silenzio vero, poi toc toc
for k in range(4): sfx(T_KNOCK + 0.1 + k * 0.22, 'footstep_grass_00%d' % k, 0.45)
toc(T_KK); toc(T_KK + 0.24)
put(fx, T_KNOCK + 1.5, sbuffo(0.3), 0.25)
# 33.0 «Ma che c***o»: il coperchio cigola. 34.5 «Dentro c'e' GIULIA»: bass drop + colpo d'orchestra + il caos
put(fx, T_MACHE + 0.12, cigolio(1.25, 380), 0.3)
put(big, T_GIULIA - 0.04, bass_drop(1.2), 0.6); put(big, T_GIULIA, colpo_orchestra(98), 0.5)
for k, dt in enumerate((0.3, 1.0, 1.7)): put(fx, T_GIULIA + dt, boing(0.5, 300 + 40 * k), 0.22)        # il naso che dondola
for k in range(6): put(fx, T_GIULIA + 0.2 + k * 0.4, np.sin(2 * np.pi * 2200 * T(0.04)) * np.hanning(int(0.04 * SR)), 0.06)   # bip della cabina
# 37.24 «che GUIDA Gualtiero»: il mattarello fa da cloche, il braccio di Gualtiero si alza a scatti
for k in range(6): put(fx, T_GUIDA + 0.05 + k * 0.17, servo(0.12, 800 + 120 * (k % 3)), 0.18)
sfx(T_GUIDA + 0.2, 'mk_Cartoon_toy_whistle', 0.35)
# 38.4 record scratch: si gira verso Tumbo. Vuoto. toc toc su Tumbo
sfx(T_KT - 0.2, 'mk_Record_player_vinyl_scratch', 0.8)
toc(T_KTK, 0.8); toc(T_KTK + 0.24, 0.8)
put(fx, T_ALTRA - 0.35, cigolio(0.6, 520), 0.25)
# 41.3 «Un'altra Giulia»: stacco drammatico, esageratamente serio
put(big, T_ALTRA - 0.3, stacco_drammatico(73.4, 2.0), 0.42)
# 42.4 le due Giulie si salutano con due vocine; poi silenzio totale
put(fx, T_ALTRA + 0.8, vocina(950, 0.4), 0.35); put(fx, T_ALTRA + 1.15, vocina(1150, 0.4), 0.35)
# 43.65 il terzo toc toc, piu' sordo. «Occupato.» Poi lo sciacquone dentro la testa di Pippo
toc(T_SELFK, 0.9, True); toc(T_SELFK + 0.26, 0.9, True)
put(fx, T_FLUSH, ovatta(sciacquone(1.6), 0.35), 1.0)
sfx(T_BLACK + 0.05, 'switch_005', 0.8)

# ---------- mix con limitatore ----------
out = v * 1.0 + mus + np.tanh(fx * 1.1) * 0.45 + big * 0.5
h = 256; pk = np.abs(out[:N // h * h]).reshape(-1, h).max(1)
g = np.minimum(1.0, 0.95 / np.maximum(pk, 1e-6)); g = np.minimum(g, np.concatenate([g[1:], g[-1:]])); g = np.convolve(g, np.ones(9) / 9, mode='same')
gg = np.interp(np.arange(N), np.arange(len(g)) * h + h / 2, g); out = np.clip(out * gg, -0.99, 0.99)
ww = wave.open('audio/t018.wav', 'w'); ww.setnchannels(1); ww.setsampwidth(2); ww.setframerate(SR); ww.writeframes((out * 32767).astype(np.int16).tobytes()); ww.close()
def rms(x, a, b): return float(np.sqrt(np.mean(x[int(a * SR):int(b * SR)] ** 2)))
print('audio/t018.wav', DUR, 's  riduzione massima del limitatore %.2f' % float(gg.min()))
for nome, a, b in (('hook', 0, 6.0), ('ogni mattina', 7.6, 11.7), ('base', 15.0, 18.2), ('ballo', 20.2, 23.0), ('telecamere', 26.6, 31.4), ('giulia', 35.2, 39.3), ('finale', 44, 48.5)):
    print('%-12s voce %.3f  musica %.3f  effetti %.3f  impatti %.3f' % (nome, rms(v, a, b), rms(mus, a, b), rms(np.tanh(fx * 1.1) * 0.45, a, b), rms(big * 0.5, a, b)))
