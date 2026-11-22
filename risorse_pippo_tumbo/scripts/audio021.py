"""Test 021 (L'etciù) - audio con la SOUND DESIGN TIMELINE (regole in SOUND_DESIGN.md, timeline in COPIONI.md n. 14, rifatta sui tempi veri della voce).
Le quattro famiglie musicali di Pippo e Tumbo (Kevin MacLeod, CC-BY 4.0, vanno citate nella descrizione):
  COMICO = «Sneaky Snitch»   SUSPENSE = «Spy Glass»   EPICO = «Strength of the Titans»   CAOS = «Galactic Rap» (qui non serve)
Effetti veri della libreria (Kenney, CC0) + effetti costruiti (gli stessi del 017) + fuoco che crepita, bip della retromarcia, carillon da ascensore.
Uso, dalla cartella del progetto: python scripts/audio021.py"""
import sys, os, subprocess, wave
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import suoni as S
SR = 44100; DUR = 41.5; N = int(DUR * SR); rng = np.random.default_rng(21)

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


def fuoco(d, g_crepitii=1.0):
    """incendio: rombo grave + crepitii secchi a caso"""
    n = int(d * SR); x = passa_basso(rng.normal(0, 1, n), 260) * 2.2 * (0.8 + 0.2 * np.sin(2 * np.pi * 0.7 * T(d)))
    for c in rng.uniform(0, d - 0.05, int(d * 26)):
        k = int(rng.uniform(0.003, 0.012) * SR); i = int(c * SR); x[i:i + k] += rng.normal(0, 1, k)[:n - i] * np.exp(-np.arange(k) / (k / 4))[:n - i] * rng.uniform(0.6, 1.8) * g_crepitii
    return passa_alto(x, 60)
def carillon(d, base=523.25):
    """musichetta da ascensore che esce dalla narice: carillon"""
    note = [0, 4, 7, 12, 11, 7, 4, 2, 0, 4, 7, 9, 7, 4, 2, 0]; x = np.zeros(int(d * SR)); dt = 0.24
    for k in range(int(d / dt)):
        f = base * 2 ** (note[k % len(note)] / 12); tt = T(0.6); s_ = (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(2 * np.pi * 2 * f * tt)) * np.exp(-tt * 6)
        i = int(k * dt * SR); x[i:i + len(s_)] += s_[:len(x) - i]
    return x * 0.5
def vocina(tp, g=0.09):
    """una vocina piccolissima dal naso («sa-lu-te»): tre sillabe acute"""
    for k, (f0, f1, d) in enumerate(((1250, 1500, 0.09), (1400, 1350, 0.08), (1500, 1100, 0.14))):
        tt = T(d); f = np.linspace(f0, f1, len(tt)); s_ = np.sign(osc(f, tt)) * 0.3 + osc(f, tt); s_ = passa_basso(s_, 4000) * np.hanning(len(tt))
        put(fx, tp + k * 0.11, s_, g)

# ---------- voce ----------
subprocess.run([S.FFMPEG, '-y', '-loglevel', 'error', '-i', 'audio/voce_t021.mp3', '-ar', str(SR), '-ac', '1', 'audio/voce44_t021.wav'], check=True)
w = wave.open('audio/voce44_t021.wav'); v = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(float) / 32768; v = np.pad(v, (0, max(0, N - len(v))))[:N]
_loc = np.sqrt(lp(v ** 2, int(0.35 * SR))); v = v * lp(np.clip(0.115 / (_loc + 0.03), 0.9, 3.0), int(0.25 * SR))
venv = lp(np.abs(v), int(0.12 * SR)); venv = np.clip(venv / (np.percentile(venv, 95) + 1e-9), 0, 1)

# ---------- tempi (gli stessi di anim021_body.py) ----------
T_STARN, T_TRE, T_PORCA = 4.12, 6.56, 8.0
T_SOLL, T_NIENTE1, T_PEPE, T_BARAT, T_SACCO, T_CAMION, T_NIENTE2, T_LACR, T_SCOLA = 9.64, 11.68, 12.58, 13.46, 14.48, 15.40, 16.46, 17.42, 18.40
T_SOLE, T_ANZI, T_CORDA, T_IMP, T_VAC, T_ETC = 19.46, 20.74, 21.4, 22.98, 23.9, 24.60
T_MA, T_NASO, T_VEST, T_ABITA, T_VEDE, T_RIENTRA, T_TUMBO, T_TRAD, T_END = 26.56, 27.86, 30.0, 31.0, 33.26, 34.54, 36.44, 38.78, 40.5

# ---------- musica: le quattro famiglie ----------
def traccia(rel, inizio=None, cerca=(0, 100), finestra=8.0):
    x = S.carica('musica/' + rel, SR)
    if inizio is None:
        h = int(SR * 0.5); r = np.sqrt(lp(x ** 2, int(finestra * SR))[::h]); a, b = int(cerca[0] * 2), min(len(r), int(cerca[1] * 2))
        inizio = max(0.0, (a + int(np.argmax(r[a:b]))) * 0.5 - finestra / 2)
    y = x[int(inizio * SR):]; y = y / (np.sqrt(np.mean(y[:int(20 * SR)] ** 2)) + 1e-9) * 0.1; return y, inizio
def stendi(buf, x, t0, t1, g, fi=0.05, fo=0.05, da=0.0):
    seg = np.zeros(N); i0 = int(t0 * SR); s = x[int(da * SR):int(da * SR) + (N - i0)]; seg[i0:i0 + len(s)] = s; buf += seg * env(t0, t1, fi, fo) * g; return seg
COMICO, i_c = traccia('comica/Sneaky_Snitch', inizio=2.0)
SUSPENSE, i_s = traccia('suspense/Spy_Glass', cerca=(10, 80))
EPICO, i_e = traccia('epica/Strength_of_the_Titans', cerca=(15, 120))
print('inizi dei brani (s): suspense %.1f, epico %.1f' % (i_s, i_e))
mus = np.zeros(N); t = np.arange(N) / SR
# 0.00 DRAMMATICO solenne: l'epico grave e ovattato, serio come un necrologio; si ferma secco su «Da tre giorni»
ep = np.zeros(N); stendi(ep, EPICO, 0.0, T_TRE - 0.05, 1.0, 0.01, 0.03); mus += passa_basso(ep, 900) * 1.6 * 0.20
# 9.64 COMICO; micro-pausa su ogni «Niente»; accelera col pepe; stop secco su «Allora guarda il sole»
co = np.zeros(N); stendi(co, COMICO, T_SOLL - 0.1, T_SOLE - 0.02, 1.0, 0.3, 0.02)
co *= 1 - env(T_NIENTE1 - 0.03, T_NIENTE1 + 0.65, 0.02, 0.12); co *= 1 - env(T_NIENTE2 - 0.03, T_NIENTE2 + 0.75, 0.02, 0.15)
mus += co * 0.11 * ramp(T_PEPE, T_CAMION, 1.0, 1.35)
# 19.46 bordone che sale (guarda il sole), 20.74 EPICO: il lazo e il sole che scende
bordone = (np.sin(2 * np.pi * 55 * t) + 0.4 * np.sin(2 * np.pi * 82.4 * t)) * (0.6 + 0.4 * np.sin(2 * np.pi * 5 * t)); mus += bordone * env(T_SOLE + 0.1, T_ANZI, 0.5, 0.05) * 0.04
ep2 = np.zeros(N); stendi(ep2, EPICO, T_ANZI - 0.02, T_IMP + 1.35, 1.0, 0.05, 0.25, da=6.0); mus += ep2 * 0.27 * ramp(T_ANZI, T_IMP, 0.9, 1.25)
# 24.1 mezzo secondo di silenzio prima dello starnuto (solo il respiro), poi niente musica fino a «Ma che cazzo»
# 26.56 SUSPENSE: dal naso esce Gualtiero
su_ = np.zeros(N); stendi(su_, SUSPENSE, T_MA - 0.05, T_ABITA, 1.0, 0.3, 0.1); mus += su_ * 0.11
# 31.0 dentro la narice: musichetta da ascensore (carillon)
put(mus, T_ABITA, carillon(T_VEDE - T_ABITA) * env(0, T_VEDE - T_ABITA, 0.2, 0.3)[:int((T_VEDE - T_ABITA) * SR)], 0.05)
# 33.26 suspense di nuovo, si ferma con la porticina che si chiude
su2 = np.zeros(N); stendi(su2, SUSPENSE, T_VEDE - 0.05, T_RIENTRA + 1.0, 1.0, 0.2, 0.02, da=8.0); mus += su2 * 0.10
# 36.44 COMICO piccolo (solo in sottofondo), stop su «Traditore di merda»: la parolaccia nel vuoto
co2 = np.zeros(N); stendi(co2, COMICO, T_TUMBO - 0.05, T_TRAD - 0.05, 1.0, 0.2, 0.02, da=30.0); mus += passa_basso(co2, 1800) * 0.07
mus *= (1 - 0.45 * venv) * 2.1

# ---------- effetti ----------
fx = np.zeros(N); big = np.zeros(N)
def sfx(tp, nome, g=1.0, vel=1.0):
    x = S.carica(nome, SR, volume=g)
    if vel != 1.0: x = np.interp(np.arange(0, len(x), vel), np.arange(len(x)), x)
    put(fx, tp, x)
def plop(tp, g=0.9, k=2): sfx(tp, 'drop_00%d' % k, g)
def passi(tp, n, dt, nome, g=0.55, vel=1.0):
    for k in range(n): sfx(tp + k * dt, '%s_00%d' % (nome, k % 5), g, vel)
def bip(tp, f, g=0.09, d=0.09): n = int(d * SR); put(fx, tp, np.sin(2 * np.pi * f * T(d)) * np.hanning(n) * g * 2)
def respiro(a, b, g=0.25):
    """«ah... ah...»: respiro trattenuto che sale"""
    d = b - a; tt = T(d); n_ = passa_basso(rng.normal(0, 1, len(tt)), 1800) * (tt / d) ** 1.5; put(fx, a, n_ * (0.6 + 0.4 * np.sin(2 * np.pi * 2.2 * tt)), g)
# 00.00 hook: colpo grave, respiro trattenuto, le narici che fischiano a ogni insulto
put(big, 0.0, dun(55, 1.0), 0.45); respiro(0.3, 4.0, 0.18)
for k, tp in enumerate((1.04, 2.36, 3.1, 5.52)): put(fx, tp, osc(1700 + 300 * k, T(0.12)) * np.hanning(int(0.12 * SR)), 0.035)
# 06.56 il quasi-starnuto che si ritira (whoosh al contrario) e «porca puttana» nel vuoto
respiro(T_PORCA - 0.9, T_PORCA - 0.1, 0.28); put(fx, T_PORCA - 0.15, whoosh(0.5, -1), 0.5); sfx(T_PORCA + 0.3, 'impactSoft_medium_000', 0.4)
# 09.64 la coda: sbuffo e frustata
for k in range(4): put(fx, T_SOLL + 0.3 + 0.45 * k, whoosh(0.22, 1), 0.25)
put(fx, T_NIENTE1 - 0.15, boing(0.4, 180), 0.15)
# 12.58 pepe: barattolo (scosse), sacco (tonfo), camion (retromarcia e scarico)
for k in range(5): put(fx, T_PEPE + 0.5 + 0.09 * k, passa_alto(rng.normal(0, 1, int(0.05 * SR)), 3000) * np.hanning(int(0.05 * SR)), 0.35)
sfx(T_SACCO + 0.05, 'impactSoft_heavy_000', 0.8); sfx(T_SACCO + 0.1, 'cloth2', 0.6)
for k in range(4): bip(T_SACCO + 0.35 + 0.15 * k, 1050, 0.06, 0.08)
put(big, T_CAMION + 0.3, boom(1.4, 70, 34), 0.45); put(fx, T_CAMION + 0.3, lp(rng.normal(0, 1, int(1.1 * SR)), 25) * np.exp(-T(1.1) * 2.5), 1.6)
for k in range(6): sfx(T_CAMION + 0.35 + 0.1 * k, 'impactMining_00%d' % (k % 5), 0.5)
vocina(T_NIENTE2 + 0.55, 0.08)                                                                          # «salute» dal naso (indizio)
for k in range(6): plop(T_LACR + 0.1 + 0.27 * k, 0.35, 1 + k % 3)                                      # lacrime a fontana
# 20.74 il lazo che gira, la corda tesa, il riser del sole che scende
for k in range(4): put(fx, T_ANZI + 0.05 + 0.14 * k, whoosh(0.16, 1), 0.35)
sfx(T_CORDA + 0.05, 'creak2', 0.7); sfx(T_CORDA + 0.6, 'creak1', 0.6)
put(fx, T_CORDA, riser(T_IMP - T_CORDA, 120, 1600), 0.35)
# 22.98 il sole sul tetto: BOOM, bass drop, colpo d'orchestra, vampata, poi il fuoco che crepita fino alla fine
put(big, T_IMP, boom(1.2, 60, 26), 0.6); put(big, T_IMP - 0.02, bass_drop(1.3), 0.5); put(big, T_IMP, colpo_orchestra(98.0, 1.2), 0.3)
put(fx, T_IMP, lp(rng.normal(0, 1, int(1.6 * SR)), 12) * np.exp(-T(1.6) * 1.5), 1.0)
for k, dt in enumerate((0.1, 0.25, 0.45, 0.7)): sfx(T_IMP + dt, 'impactMining_00%d' % k, 0.6)
F_ = fuoco(DUR - T_IMP); fu = np.zeros(N); put(fu, T_IMP, F_); fu *= (1 - 0.6 * venv)
# 24.1 silenzio, respiro... ETCIU' gigante con eco e vento
respiro(T_ETC - 0.55, T_ETC - 0.02, 0.4)
put(big, T_ETC, boom(1.8, 80, 30), 0.8); put(fx, T_ETC, whoosh(1.4, -1), 0.8)
for k in range(3): put(fx, T_ETC + 0.3 + 0.3 * k, passa_basso(whoosh(0.5, 1), 1200), 0.3 / (k + 1))
# 26.56 glitch, porticina minuscola, passetti e rotelle di valigia
put(fx, T_MA, glitch(0.3), 0.2)
sfx(T_NASO, 'doorOpen_1', 0.5, vel=2.2); passi(T_NASO + 0.3, 6, 0.14, 'footstep_wood', 0.25, vel=2.0)
rot = passa_alto(rng.normal(0, 1, int(1.0 * SR)), 2500) * (0.6 + 0.4 * np.sign(np.sin(2 * np.pi * 18 * T(1.0)))); put(fx, T_NASO + 0.35, rot * np.hanning(len(rot)), 0.08)
sfx(T_VEST + 0.1, 'cloth1', 0.5, vel=1.6)
# 33.26 vede le fiamme: piccolo colpo; rientra: passetti, la porticina si chiude
put(big, T_VEDE + 0.2, dun(82.4, 0.6), 0.25)
passi(T_RIENTRA + 0.05, 5, 0.12, 'footstep_wood', 0.25, vel=2.0); sfx(T_RIENTRA + 0.95, 'doorClose_1', 0.6, vel=2.0)
# 36.44 Tumbo: passi, cuscino, porticina; il cartello AL COMPLETO
passi(T_TUMBO - 0.2, 4, 0.1, 'footstep_carpet', 0.5); sfx(T_TUMBO + 0.5, 'cloth2', 0.5); put(fx, T_TUMBO + 0.9, boing(0.4, 400), 0.12)
sfx(T_TUMBO + 0.95, 'doorOpen_2', 0.45, vel=2.0); sfx(T_TUMBO + 1.5, 'doorClose_2', 0.6, vel=2.0)
sfx(T_TUMBO + 1.75, 'switch_005', 0.8); sfx(T_TUMBO + 1.8, 'error_004', 0.4)
put(fx, T_END, boom(0.5, 70, 40), 0.2)
# 24.82 (richiesta dell'autore) uno in fiamme attraversa l'inquadratura URLANDO: «AAAAH» da cartone, con l'effetto Doppler
def urlo(d=1.7):
    tt = T(d); u = tt / d
    f0 = 330 * (1 + 0.18 * np.sin(np.pi * np.clip(u * 1.4, 0, 1))) * (1.08 - 0.16 * u) * (1 + 0.035 * np.sin(2 * np.pi * 7.5 * tt))
    src = saw(f0, tt) + 0.4 * rng.normal(0, 1, len(tt)) * 0.15
    X = np.fft.rfft(src); fr_ = np.fft.rfftfreq(len(src), 1 / SR); H = np.zeros_like(fr_)
    for (fc, bw, g) in ((800, 110, 1.0), (1180, 130, 0.7), (2600, 220, 0.25), (3400, 300, 0.12)): H += g / (1 + ((fr_ - fc) / bw) ** 2)
    y = np.fft.irfft(X * H, len(src)); y = y / (np.max(np.abs(y)) + 1e-9)
    amp = np.minimum(1, tt * 12) * np.minimum(1, (d - tt) * 5) * (0.55 + 0.45 * np.sin(np.pi * u))
    return np.tanh(y * amp * 1.6)
T_URLO0 = T_ETC + 0.22
put(fx, T_URLO0 - 0.05, urlo(T_MA - T_URLO0 - 0.02), 0.9)
for k in range(5): put(fx, T_IMP + 0.4 + 0.25 * k, passa_basso(urlo(0.9), 2200), 0.16)              # urla lontane nell'inferno (sotto la voce)


# ---------- mix con limitatore ----------
big *= (1 - 0.45 * venv)
out = v * 1.0 + mus + np.tanh(fx * 1.1) * 0.45 * (1 - 0.3 * venv) + big * 0.5 + fu * 0.09
out *= np.where(t >= T_END + 0.6, np.clip(1 - (t - T_END - 0.6) / 0.3, 0, 1), 1.0)
h = 256; pk = np.abs(out[:N // h * h]).reshape(-1, h).max(1)
g = np.minimum(1.0, 0.95 / np.maximum(pk, 1e-6)); g = np.minimum(g, np.concatenate([g[1:], g[-1:]])); g = np.convolve(g, np.ones(9) / 9, mode='same')
gg = np.interp(np.arange(N), np.arange(len(g)) * h + h / 2, g); out = np.clip(out * gg, -0.99, 0.99)
ww = wave.open('audio/t021.wav', 'w'); ww.setnchannels(1); ww.setsampwidth(2); ww.setframerate(SR); ww.writeframes((out * 32767).astype(np.int16).tobytes()); ww.close()
def rms(x, a, b): return float(np.sqrt(np.mean(x[int(a * SR):int(b * SR)] ** 2)))
print('audio/t021.wav', DUR, 's  riduzione massima del limitatore %.2f' % float(gg.min()))
for nome, a, b in (('hook', 0, 4), ('coda', 9.7, 12.5), ('camion', 15.4, 16.4), ('lazo', 20.8, 22.9), ('fuoco', 23.0, 24.5), ('naso', 27.9, 31.0), ('appart.', 31, 33.2), ('finale', 36.4, 40.4)):
    print('%-8s voce %.3f  musica %.3f  effetti %.3f  impatti %.3f  fuoco %.3f' % (nome, rms(v, a, b), rms(mus, a, b), rms(np.tanh(fx * 1.1) * 0.45, a, b), rms(big * 0.5, a, b), rms(fu * 0.09, a, b)))
