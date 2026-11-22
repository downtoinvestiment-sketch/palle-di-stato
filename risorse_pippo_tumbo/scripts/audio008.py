"""Test 008 - audio: voce + musichetta sintetica + effetti. Uso: python scripts/audio008.py full|cut -> audio/t008_<ver>.wav"""
import sys, os, numpy as np, subprocess, wave
sys.path.insert(0, os.path.dirname(__file__))
import cut008
VER = sys.argv[1] if len(sys.argv) > 1 else 'full'
SR = 44100; DUR = 76.5; N = int(DUR * SR); rng = np.random.default_rng(8)
t = np.arange(N) / SR
def env(a, b, fi=0.1, fo=0.3):
    e = np.zeros(N); i0, i1 = int(a * SR), min(N, int(b * SR)); n = i1 - i0
    x = np.ones(n); fi_n = min(n // 2, int(fi * SR)); fo_n = min(n // 2, int(fo * SR))
    x[:fi_n] = np.linspace(0, 1, fi_n); x[n - fo_n:] = np.linspace(1, 0, fo_n); e[i0:i1] = x; return e
def lp(x, k): return np.convolve(x, np.ones(k) / k, mode='same')
def put(buf, t0, s):
    i0 = int(t0 * SR); n = min(len(s), len(buf) - i0)
    if n > 0 and i0 >= 0: buf[i0:i0 + n] += s[:n]
def tone(f0, f1, dur, dec=6.0, harm=0.3):
    n = int(dur * SR); tt = np.arange(n) / SR; f = np.linspace(f0, f1, n); ph = 2 * np.pi * np.cumsum(f) / SR
    return (np.sin(ph) + harm * np.sin(2 * ph)) * np.exp(-tt * dec)
def burst(dur, k=8, dec=10.0):
    n = int(dur * SR); tt = np.arange(n) / SR; return lp(rng.normal(0, 1, n), k) * np.exp(-tt * dec)
def hiss(dur, k=3, dec=10.0):
    n = int(dur * SR); tt = np.arange(n) / SR; x = rng.normal(0, 1, n); return (x - lp(x, k)) * np.exp(-tt * dec)
def sweep(fs, dur, g=1.0, vib=0.0, vf=30):
    n = int(dur * SR); tt = np.arange(n) / SR; f = np.interp(tt, np.linspace(0, dur, len(fs)), fs) * (1 + vib * np.sin(2 * np.pi * vf * tt))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.minimum(1, tt * 25) * np.minimum(1, (dur - tt) * 12) * g
subprocess.run(['/usr/local/bin/ffmpeg', '-y', '-loglevel', 'error', '-i', 'audio/voce_t008.mp3', '-ar', str(SR), '-ac', '1', 'audio/voce44_t008.wav'], check=True)
w = wave.open('audio/voce44_t008.wav'); v = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(float) / 32768; v = np.pad(v, (0, max(0, N - len(v))))[:N]
def clip(a, b):
    s = v[int(a * SR):int(b * SR)].copy(); k = int(0.008 * SR); s[:k] *= np.linspace(0, 1, k); s[-k:] *= np.linspace(1, 0, k); return s
if VER == 'cut':                                    # le lezioni rimaste si rinumerano: "Lezione 3" -> "Lezione 1", "Lezione 5" -> "Lezione 2"
    one, two = clip(9.90, 10.52), clip(17.08, 17.78); v = v.copy()
    v *= 1 - env(30.76, 31.51, 0.01, 0.01); put(v, 30.84, one)
    v *= 1 - env(51.72, 52.57, 0.01, 0.01); put(v, 51.80, two)

fx = np.zeros(N)
def pop(tp, g=0.55): put(fx, tp, tone(420, 900, 0.14, 16, 0.2) * g)
def thud(tp, g=1.0): put(fx, tp, tone(95, 45, 0.45, 7, 0.5) * 1.2 * g); put(fx, tp, burst(0.4, 15, 9) * 1.0 * g)
def whoosh(tp, dur=0.5, g=1.8, k=50): put(fx, tp, burst(dur, k, 5) * g * np.hanning(int(dur * SR)))
def cluck(tp, g=0.35, f=560):
    put(fx, tp, sweep([f, f * 1.25, f * 0.8], 0.085, g, 0.06, 70)); put(fx, tp, hiss(0.03, 3, 60) * g * 0.5)
def clucks(tp, n=3, dt=0.17, g=0.3):
    for k in range(n): cluck(tp + dt * k + 0.02 * np.sin(k * 3.1), g * (0.8 + 0.2 * (k % 2)), 540 + 40 * (k % 3))
def squawk(tp, g=0.4): put(fx, tp, sweep([700, 1150, 900, 600], 0.38, g, 0.10, 45))
def whistle(tp, g=0.16): put(fx, tp, sweep([2700, 2800, 2750], 0.45, g, 0.04, 38))
def eagle(tp, g=0.22): put(fx, tp, sweep([2500, 2300, 2000, 1750], 0.9, g, 0.02, 9) * np.exp(-np.arange(int(0.9 * SR)) / SR * 1.5))
def step(tp, g=0.5, f=150): put(fx, tp, tone(f, f * 0.6, 0.06, 40, 0.4) * g); put(fx, tp, burst(0.04, 6, 50) * g * 0.6)
def knock(tp, f=300, g=0.35): put(fx, tp, tone(f, f * 0.85, 0.05, 40, 0.3) * g)
def flap(tp, g=0.9, dur=0.12): put(fx, tp, burst(dur, 25, 14) * g)
def chime(tp, k=0, g=0.08): put(fx, tp, tone(1760 + 260 * (k % 4), 1760 + 260 * (k % 4), 0.35, 8, 0.15) * g)
# --- gancio: la gallina, il trofeo
clucks(0.5, 3); clucks(2.3, 2); clucks(3.2, 2)
whoosh(3.7, 0.5, 1.6); squawk(4.15, 0.35)
for k, f in enumerate((392, 494, 587, 784)): put(fx, 4.35 + 0.11 * k, tone(f, f, 0.8, 3.0, 0.5) * 0.16)
for k in range(6): chime(4.5 + 0.25 * k, k)
pop(6.9); pop(7.9, 0.45); clucks(8.95, 2, 0.15, 0.25)
# --- lezione 1: documentario
whistle(9.95, 0.10); pop(10.3)
fx += lp(rng.normal(0, 1, N), 4) * env(11.0, 16.8, 0.2, 0.2) * 0.012                                     # fruscio della tv
eagle(12.5, 0.12); eagle(13.7, 0.10)
put(fx, 15.15, sweep([300, 380, 520], 0.5, 0.14, 0.05, 20)); put(fx, 15.8, sweep([320, 760], 0.09, 0.5)); put(fx, 15.83, tone(180, 120, 0.12, 20, 0.4) * 0.5)   # sforzo e plop
clucks(16.15, 3, 0.14, 0.3)
# --- lezione 2: rincorsa
whistle(17.15, 0.10)
for k in range(8): flap(17.6 + 0.31 * k, 0.35)
for k in range(28): step(19.25 + 0.16 * k, 0.45, 150 + 20 * (k % 2))
for k in range(27): flap(19.3 + 0.165 * k, 0.5, 0.10)
put(fx, 21.4, hiss(0.25, 5, 10) * 0.6)                                                                    # derapata
cluck(24.1, 0.3, 480); put(fx, 25.45, sweep([240, 200], 0.2, 0.2)); put(fx, 26.85, sweep([330, 420], 0.22, 0.13))
cr = np.zeros(N)                                                                                          # grilli e vento
for k in range(13):
    for j in range(3): put(cr, 28.75 + 0.14 * k + 0.035 * j, tone(4300, 4300, 0.025, 60, 0.1) * 0.05)
fx += cr; fx += lp(rng.normal(0, 1, N), 120) * env(28.6, 30.6, 0.5, 0.5) * 0.9
# --- lezione 3: ali di cartone
whistle(30.9, 0.10); put(fx, 33.3, hiss(0.3, 4, 9) * 0.6); pop(33.5); pop(33.62, 0.45)
whoosh(34.55, 0.4, 1.6); squawk(34.9, 0.3)
for k in range(11): flap(34.9 + 0.09 * k, 0.7, 0.08)
put(fx, 34.9, sweep([500, 900], 1.0, 0.10)); put(fx, 35.9, sweep([1300, 380], 0.5, 0.16))                 # su... e giù
thud(36.4, 0.9); put(fx, 36.4, tone(900, 600, 0.25, 9, 0.6) * 0.3)                                        # ciotola di metallo
for k in range(22): put(fx, 36.45 + rng.uniform(0, 0.8), tone(1500 + rng.uniform(0, 900), 1200, 0.03, 60, 0.2) * 0.14)   # crocchette
squawk(36.65, 0.3); put(fx, 38.55, sweep([150, 110, 95], 0.5, 0.35, 0.25, 28)); put(fx, 39.25, burst(0.25, 30, 9) * 1.2)   # ringhio e sbuffo
# --- lezione 4: il vento
whistle(41.65, 0.10); pop(41.75); put(fx, 43.7, tone(200, 200, 0.06, 30, 0.5) * 0.5)
fr_ = np.interp(t, [43.7, 45.4, 51.4, 51.6], [35, 120, 120, 40]); sawp = (np.cumsum(fr_) / SR) % 1.0
fx += lp(sawp * 2 - 1, 30) * np.interp(t, [43.7, 44.2, 45.4, 49.6, 51.4, 51.6], [0, 0.03, 0.07, 0.05, 0.03, 0])
fx += lp(rng.normal(0, 1, N), 60) * np.interp(t, [43.9, 45.4, 49.5, 51.4, 51.6], [0, 1.4, 1.0, 0.6, 0])
cluck(46.4, 0.28, 500); whoosh(47.6, 0.8, 2.4); put(fx, 48.1, sweep([1500, 1700, 500], 1.15, 0.16))
put(fx, 49.3, burst(0.5, 6, 7) * 1.3); thud(49.3, 0.8)
for k in range(16): flap(49.45 + 0.11 * k * (1 + 0.04 * k), 0.75 * np.exp(-k * 0.13), 0.07)                 # gambe a elica
# --- lezione 5: il tetto
whistle(51.85, 0.10)
for k in range(13): knock(54.25 + 0.115 * k, 220 + 14 * k, 0.4)
for k in range(3): put(fx, 56.12 + 0.235 * k, tone(520 + 130 * k, 520 + 130 * k, 0.16, 12, 0.3) * 0.25)
whoosh(56.82, 0.3, 1.4, 30); cluck(57.35, 0.3)
for k in range(16): knock(57.77 + 0.10 * k, 760 - 26 * k, 0.3)
for k, f in enumerate((392, 370, 349, 262)): put(fx, 58.55 + 0.2 * k, sweep([f, f * 0.97], 0.26 if k < 3 else 0.5, 0.11, 0.03, 6))   # trombone triste
clucks(60.4, 3, 0.2, 0.22)
# --- finale
put(fx, 62.42, tone(1320, 1320, 0.5, 6, 0.2) * 0.12); thud(64.2, 0.6); put(fx, 64.3, burst(0.6, 80, 5) * 1.5); knock(64.5, 500, 0.2)   # si siede, sospira, cappello
cluck(67.0, 0.3, 500); whoosh(68.2, 0.35, 1.5)
for k in range(2): flap(68.6 + 0.4 * k, 1.0, 0.16)
whoosh(69.3, 0.6, 2.0)
for k in range(6): flap(69.35 + 0.28 * k, 1.0 * np.exp(-k * 0.2), 0.16)
for k, f in enumerate((262, 330, 392, 523, 659)): put(fx, 69.4 + 0.14 * k, tone(f, f, 0.9, 2.5, 0.5) * 0.15)
eagle(70.1, 0.2); eagle(71.5, 0.13)
put(fx, 73.45, sweep([1500, 1100, 1250, 900, 1000, 700], 1.2, 0.07)); put(fx, 74.72, tone(900, 1400, 0.06, 30, 0.2) * 0.25)   # la piuma
for k, f in enumerate((196, 131)): put(fx, 75.35 + 0.3 * k, tone(f * 2, f * 2, 0.6, 5, 0.5) * 0.2)
fx = np.tanh(fx * 1.1) * 0.45

# --- montaggio
SG = cut008.segs(VER); TOT = cut008.total(VER); NT = int(TOT * SR)
def cutbuf(x):
    out = []
    for a, b in SG:
        s = x[int(round(a * SR)):int(round(b * SR))].copy(); k = int(0.012 * SR)
        if len(SG) > 1: s[:k] *= np.linspace(0, 1, k); s[-k:] *= np.linspace(1, 0, k)
        out.append(s)
    y = np.concatenate(out); return np.pad(y, (0, max(0, NT - len(y))))[:NT]
vv, ff = cutbuf(v), cutbuf(fx)
bpm = 112; beat = 60 / bpm; chords = [(130.81, 164.81, 196.0), (196.0, 246.94, 293.66), (220.0, 261.63, 329.63), (174.61, 220.0, 261.63)]
m = np.zeros(NT)
def pluck(f, t0, dur=0.5, amp=0.5):
    n = int(dur * SR); tt = np.arange(n) / SR; put(m, t0, amp * (np.sin(2 * np.pi * f * tt) + 0.4 * np.sin(4 * np.pi * f * tt) + 0.2 * np.sin(6 * np.pi * f * tt)) * np.exp(-tt * 7))
for bar in range(int(TOT / (beat * 4)) + 1):
    ch = chords[bar % 4]
    for b in range(8):
        t0 = bar * beat * 4 + b * beat / 2; f = ch[[0, 2, 1, 2, 0, 1, 2, 1][b]] * 2
        pluck(f, t0, 0.4, 0.30 if b % 2 == 0 else 0.22)
    pluck(ch[0] / 2, bar * beat * 4, 0.9, 0.5); pluck(ch[0] / 2, bar * beat * 4 + 2.5 * beat, 0.9, 0.4); pluck(ch[2] / 2, bar * beat * 4 + 3 * beat, 0.5, 0.3)
tt_ = np.arange(NT) / SR
mus = m / np.abs(m).max() * 0.19
sil = cut008.tclip(VER, 28.6, 30.6)                                                                       # "nessuno dice niente": la musica tace
gain = np.interp(tt_, [0, 1, TOT - 1.3, TOT - 1.0, TOT], [0.6, 1, 1, 0.35, 0.0])
if sil: gain *= np.interp(tt_, [sil[0] - 0.2, sil[0], sil[1], sil[1] + 0.3], [1, 0.0, 0.0, 1])
mus *= gain
mix = vv * 1.0 + mus + ff
mix = np.clip(mix / max(1, np.abs(mix).max() / 0.95), -1, 1)
mix[-int(0.15 * SR):] *= np.linspace(1, 0, int(0.15 * SR))
st = np.stack([mix, mix], 1); pcm = (st * 32767).astype(np.int16)
with wave.open('audio/t008_%s.wav' % VER, 'wb') as o:
    o.setnchannels(2); o.setsampwidth(2); o.setframerate(SR); o.writeframes(pcm.tobytes())
print('audio ok', VER, round(TOT, 2), np.abs(vv).max(), np.abs(mus).max(), np.abs(ff).max())
