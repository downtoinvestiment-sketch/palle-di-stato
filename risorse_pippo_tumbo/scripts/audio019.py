"""Video 019 (Il doppio gioco) - audio con la SOUND DESIGN TIMELINE (regole in SOUND_DESIGN.md, timeline del copione n. 11). Esce audio/t019.wav (37.5 s).
Le quattro famiglie musicali (Kevin MacLeod, CC-BY 4.0, da citare nella descrizione), come nel copione:
  EPICO = «Strength of the Titans»   COMICO = «Monkeys Spinning Monkeys»   SUSPENSE = «Hitman»   CAOS = «Galactic Rap»
Effetti: Kenney (CC0), il kit Mixkit (audio/sfx/mixkit) e quelli costruiti qui (boom, bass drop, riser, whoosh, boing, moto del prete,
cingoli, sonar, razzi, sirena, spruzzo, sgonfiata, campane, organo, bacio, carillon, «pof»).
Uso, dalla cartella del progetto: python scripts/audio019.py"""
import sys, os, subprocess, wave
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import suoni as S
SR = 44100; DUR = 37.5; N = int(DUR * SR); rng = np.random.default_rng(19)

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

# ---------- voce ----------
subprocess.run([S.FFMPEG, '-y', '-loglevel', 'error', '-i', 'audio/voce_t019.mp3', '-ar', str(SR), '-ac', '1', 'audio/voce44_t019.wav'], check=True)
w = wave.open('audio/voce44_t019.wav'); v = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(float) / 32768; v = np.pad(v, (0, max(0, N - len(v))))[:N]
_loc = np.sqrt(lp(v ** 2, int(0.35 * SR))); v = v * lp(np.clip(0.115 / (_loc + 0.03), 0.9, 3.0), int(0.25 * SR))
venv = lp(np.abs(v), int(0.12 * SR)); venv = np.clip(venv / (np.percentile(venv, 95) + 1e-9), 0, 1)

# ---------- tempi (gli stessi di anim019_body.py) ----------
T_STACC = 2.52; T_BACK = 4.26; T_THROW = 4.9; T_LAND = 6.3; T_GUAL = 6.66; T_STAB = 8.14
T_WATER = 9.12; T_SPRAY = 10.2; T_BAZ = 11.46; T_FIRE = 12.32; T_TANK = 13.18; T_SUBG = 14.94; T_SUBUP = 16.78
T_FINE = 18.42; T_BOMB = 19.48; T_TUTTI = 20.86; T_MA = 21.96; T_PRETE = 24.64; T_DOPPIO = 25.92
T_INC = 27.32; T_TOUCH = 28.1; T_FA = 28.74; T_SPOSA = 31.66; T_NOVE = 33.04; T_GEM = 34.56; T_CLOSE = 35.6; T_END = 37.0

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
COMICO, i_c = traccia('comica/Monkeys_Spinning_Monkeys', inizio=0.5)
SUSPENSE, i_s = traccia('suspense/Hitman', cerca=(5, 90))
CAOS, i_k = traccia('suspense/Galactic_Rap', cerca=(20, 120))
print('inizi dei brani (s): epico %.1f, suspense %.1f, caos %.1f' % (i_e, i_s, i_k))

mus = np.zeros(N)
# 00.00 EPICO subito: due bombe atomiche. A 4.1 tape stop: si torna indietro
ep = np.zeros(N); stendi(ep, EPICO, 0.0, 4.9, 1.0, 0.005, 0.02); tape_stop(ep, 4.05, 0.55); mus += ep * 0.24
# 04.3 COMICO basso: la pallina. Si ferma un attimo sulla forchetta, riparte sulla pistola ad acqua, si ferma sul bazooka
co = np.zeros(N); stendi(co, COMICO, T_BACK + 0.15, T_TANK - 0.05, 1.0, 0.3, 0.05); co *= 1 - env(T_STAB - 0.05, T_WATER - 0.1, 0.02, 0.15); co *= 1 - env(T_FIRE - 0.03, T_TANK, 0.01, 0.05)
mus += co * 0.12
# 13.18 EPICO in salita: carro, sottomarino, la bomba atomica (al massimo)
ep2 = np.zeros(N); stendi(ep2, EPICO, T_TANK - 0.02, T_MA - 0.05, 1.0, 0.02, 0.02, da=12.0); mus += ep2 * 0.22 * ramp(T_TANK, T_BOMB, 0.8, 1.35)
# 21.96 record scratch, poi niente. 24.64 stacco drammatico; 25.0 SUSPENSE bassa fino all'incontro
su_ = np.zeros(N); stendi(su_, SUSPENSE, T_PRETE + 0.4, T_INC + 0.6, 1.0, 0.3, 0.6); mus += su_ * 0.12
# 28.74 stop: il prete salta. 31.66 CAOS esplode su «Le sposa!», stop secco su «Nove mesi dopo»
ca = np.zeros(N); stendi(ca, CAOS, T_SPOSA - 0.02, T_NOVE - 0.02, 1.0, 0.01, 0.02); mus += ca * 0.2
mus *= (1 - 0.45 * venv) * 2.1

# ---------- effetti ----------
fx = np.zeros(N); big = np.zeros(N)
def sfx(tp, nome, g=1.0, vel=1.0):
    x = S.carica(nome, SR, volume=g)
    if vel != 1.0: x = np.interp(np.arange(0, len(x), vel), np.arange(len(x)), x)
    put(fx, tp, x)

# 00.00 HOOK: fischio delle bombe e razzi, riser; colpo d'orchestra sulla staccionata
put(fx, 0.0, razzo(4.1), 0.35); put(fx, 0.0, fischio_bomba(4.0, 1600, 700), 0.12); put(fx, 0.2, riser(3.8, 150, 1000), 0.12)
put(big, T_STACC - 0.02, colpo_orchestra(110), 0.45)
# 04.26 si torna indietro: whoosh al contrario
put(fx, T_BACK - 0.2, whoosh(0.5, -1), 0.5); sfx(T_BACK, 'mk_Vacuum_swoosh_transition', 0.4)
# la pallina: lancio, volo, rimbalzi
put(fx, T_THROW, whoosh(0.4, 1), 0.35); put(fx, T_LAND, boing(0.4, 260), 0.35); put(fx, T_LAND + 0.35, boing(0.3, 300), 0.22)
# 08.14 la forchetta: stop, «tic» metallico, sgonfiata, trombone
sfx(T_STAB - 0.02, 'impactMetal_light_001', 0.8); put(fx, T_STAB + 0.05, sgonfiata(0.95), 0.6); sfx(T_STAB + 1.0, 'mk_Trombone_disappoint', 0.3)
# indizio: a ogni consegna, un rombo di moto lontano (fuori campo)
for tp in (9.0, T_BAZ - 0.25, T_TANK - 0.2, T_SUBG - 0.15): put(fx, tp, passa_basso(moto_rombo(0.9, 0.7), 700), 0.18)
# 10.2 pistola ad acqua: spruzzo, schizzo in faccia
put(fx, T_SPRAY, spruzzo(T_BAZ - 0.2 - T_SPRAY), 0.45); sfx(T_SPRAY + 0.3, 'mk_Funny_cartoon_fast_splat', 0.4)
# 11.46 il bazooka: clac del caricamento; 12.32 colpo grave + boom corto + tono di fallimento
sfx(T_BAZ + 0.35, 'metalClick', 0.7); put(big, T_FIRE, boom(1.4, 70, 32), 0.75); sfx(T_FIRE + 0.02, 'mk_Dramatic_metal_explosion_impact', 0.5)
sfx(T_FIRE + 0.7, 'mk_Funny_fail_low_tone', 0.35)
# 13.18 carro armato: cingoli; il cannone gira (servo)
put(fx, T_TANK, cingoli(1.6), 0.6); put(fx, T_TANK + 1.0, servo(0.6, 300), 0.2)
# 14.94 sottomarino: bip del periscopio, onda; 16.78 esce dalla piscina: colpo d'orchestra, onda enorme, corno grave
for k in range(3): put(fx, T_SUBG + 0.5 + k * 0.6, sonar(1250 - 80 * k), 0.22)
put(fx, T_SUBUP - 0.05, passa_basso(rng.normal(0, 1, int(1.6 * SR)), 1100) * np.hanning(int(1.6 * SR)), 0.8)
put(big, T_SUBUP + 0.05, colpo_orchestra(73.4), 0.55); put(fx, T_SUBUP + 0.4, dun(41, 1.2), 0.5)
# 18.42 LA BOMBA ATOMICA: sirena, razzi, impatto su «atomica»
put(fx, T_FINE, sirena(T_MA - T_FINE - 0.1), 0.12); put(fx, T_FINE + 0.25, razzo(T_MA - T_FINE - 0.3), 0.55)
put(big, T_BOMB, colpo_orchestra(98), 0.55); put(big, T_BOMB + 0.02, bass_drop(1.0), 0.4)
# 20.86 Tutti e due: le due bombe si mettono in posizione una davanti all'altra
put(fx, T_TUTTI + 0.02, whoosh(0.45, 1), 0.45); sfx(T_TUTTI + 0.3, 'mk_Short_bass_hit', 0.45)
# 21.96 record scratch, poi silenzio vero
sfx(T_MA - 0.12, 'mk_Record_player_vinyl_scratch', 0.8)
# 24.64 IL PRETE: stacco drammatico, la moto ride (sgasata), registratore di cassa
put(big, T_PRETE - 0.05, stacco_drammatico(73.4, 2.0), 0.42); put(fx, T_PRETE + 0.5, moto_rombo(1.2, 1.0), 0.35)
for k in range(8): sfx(T_PRETE + 0.6 + k * 0.13, 'bookFlip%d' % (k % 3 + 1), 0.35)                  # conta le banconote
put(fx, T_DOPPIO - 0.1, campane(0.5)[:int(0.4 * SR)], 0.4); sfx(T_DOPPIO - 0.12, 'impactWood_light_002', 0.7)   # cassetto, «din»
for k in range(2): sfx(T_DOPPIO + 0.12 * k, 'mk_Hard_pop_click', 0.5)
# 27.32 le bombe si incontrano: battito del cuore, «ding» quando si toccano
for k in range(2): sfx(T_INC + 0.05 + 0.4 * k, 'mk_Deep_heartbeat_impact', 0.5)
sfx(T_TOUCH, 'mk_Magic_sparkle_whoosh', 0.45)
# 28.74 il prete salta in cielo: sgasata e whoosh; 29.9 l'organo, una nota lunga
put(fx, T_FA + 0.05, moto_rombo(1.0, 1.2), 0.4); sfx(T_FA + 0.25, 'mk_Air_zoom_vacuum', 0.45)
put(fx, T_FA + 1.2, organo(130.8, T_SPOSA - T_FA - 1.25), 0.25)
# 31.66 LE SPOSA: bass drop, campane a festa, il bacio, coriandoli
put(big, T_SPOSA - 0.02, bass_drop(1.2), 0.6); put(fx, T_SPOSA + 0.05, bacio(), 0.8); put(fx, T_SPOSA + 0.15, campane(1.6), 0.5)
sfx(T_SPOSA + 0.3, 'mk_Silly_pop_cluster', 0.45)
# 33.04 «Nove mesi dopo» su nero: silenzio. 34.3 carillon e tic tac delle bombine; si inceppa prima del primo piano
put(fx, T_GEM - 0.3, carillon(T_END - T_GEM + 0.3, inceppa=T_CLOSE - T_GEM + 0.1), 0.45)
sfx(T_GEM, 'mk_Tick_tock_clock_close_up', 0.35)
for k in range(2): put(fx, T_CLOSE + 0.3 + 0.35 * k, np.sin(2 * np.pi * (1500 + 300 * k) * T(0.07)) * np.hanning(int(0.07 * SR)), 0.12)   # bip-bip delle bombine
put(fx, T_END + 0.05, pof(), 0.8)                                                                      # «pof» su nero

# ---------- mix con limitatore ----------
out = v * 1.0 + mus + np.tanh(fx * 1.1) * 0.45 + big * 0.5
h = 256; pk = np.abs(out[:N // h * h]).reshape(-1, h).max(1)
g = np.minimum(1.0, 0.95 / np.maximum(pk, 1e-6)); g = np.minimum(g, np.concatenate([g[1:], g[-1:]])); g = np.convolve(g, np.ones(9) / 9, mode='same')
gg = np.interp(np.arange(N), np.arange(len(g)) * h + h / 2, g); out = np.clip(out * gg, -0.99, 0.99)
ww = wave.open('audio/t019.wav', 'w'); ww.setnchannels(1); ww.setsampwidth(2); ww.setframerate(SR); ww.writeframes((out * 32767).astype(np.int16).tobytes()); ww.close()
print('audio/t019.wav', DUR, 's  riduzione massima del limitatore %.2f' % float(gg.min()))
