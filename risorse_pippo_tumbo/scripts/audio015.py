"""Test 015 (il parto di Eleonora) - audio: voce + musichetta sintetica + effetti. Esce audio/t015.wav (65.8 s)"""
import numpy as np, subprocess, wave
SR = 44100; DUR = 65.8; N = int(DUR * SR); rng = np.random.default_rng(15)
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
def saw(freqs_t, freqs, k=30): fr_ = np.interp(t, freqs_t, freqs); return lp(((np.cumsum(fr_) / SR) % 1.0) * 2 - 1, k)
subprocess.run(['/usr/local/bin/ffmpeg', '-y', '-loglevel', 'error', '-i', 'audio/voce_t015.mp3', '-ar', str(SR), '-ac', '1', 'audio/voce44_t015.wav'], check=True)
w = wave.open('audio/voce44_t015.wav'); v = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(float) / 32768; v = np.pad(v, (0, max(0, N - len(v))))[:N]

fx = np.zeros(N)
def pop(tp, g=0.55): put(fx, tp, tone(420, 900, 0.14, 16, 0.2) * g)
def thud(tp, g=1.0): put(fx, tp, tone(95, 45, 0.45, 7, 0.5) * 1.2 * g); put(fx, tp, burst(0.4, 15, 9) * 1.0 * g)
def whoosh(tp, dur=0.5, g=1.8, k=50): put(fx, tp, burst(dur, k, 5) * g * np.hanning(int(dur * SR)))
def step(tp, g=0.5, f=150): put(fx, tp, tone(f, f * 0.6, 0.06, 40, 0.4) * g); put(fx, tp, burst(0.04, 6, 50) * g * 0.6)
def chime(tp, k=0, g=0.08): put(fx, tp, tone(1760 + 260 * (k % 4), 1760 + 260 * (k % 4), 0.35, 8, 0.15) * g)
def laugh(tp, n=6, g=0.22):
    for k in range(n): put(fx, tp + 0.2 * k, sweep([190 - 6 * k, 150 - 5 * k], 0.11, g, 0.08, 40))
def dundun(tp, g=0.45):
    for k, f in enumerate((98, 73.4)): put(fx, tp + 0.55 * k, tone(f, f, 0.6, 4, 0.8) * g); put(fx, tp + 0.55 * k, tone(f * 2, f * 2, 0.5, 5, 0.5) * g * 0.5)
def bell(tp, g=0.14): put(fx, tp, tone(1245, 1245, 1.0, 3.5, 0.4) * g); put(fx, tp, tone(1870, 1870, 0.8, 4.5, 0.2) * g * 0.5)

def click(tp, f=1800, g=0.3): put(fx, tp, tone(f, f * 0.9, 0.03, 80, 0.3) * g); put(fx, tp, burst(0.015, 2, 120) * g)
def clang(tp, g=0.5):
    for f in (523, 787, 1245, 1620): put(fx, tp, tone(f, f, 0.7, 5, 0.1) * g * 0.3)
    put(fx, tp, burst(0.08, 3, 30) * g)

def wind(a, b, g, k=70, fi=0.3, fo=0.4):
    gust = np.clip(0.55 + 0.45 * np.sin(2 * np.pi * 0.23 * t + a) + 0.3 * np.sin(2 * np.pi * 0.61 * t + 2 * a), 0.08, 1.3)   # raffiche: sale e scende, non e' un rumore fisso
    return lp(rng.normal(0, 1, N), k) * env(a, b, fi, fo) * g * gust
def siren(a, b, g=0.07, rate=2.6, f0=650.0, f1=870.0):
    s = np.where((t * rate) % 1.0 < 0.5, f0, f1); return np.sin(2 * np.pi * np.cumsum(s) / SR) * np.interp(t, [a, a + 0.15, b - 0.3, b], [0, g, g, 0])
def rasp(tp, dur=0.7, g=0.12):
    i0, i1 = int(tp * SR), int((tp + dur) * SR); fx[i0:i1] += saw([tp, tp + dur], [95, 70], 6)[i0:i1] * g * np.hanning(i1 - i0)
def shutter(tp): click(tp, 3000, 0.7); put(fx, tp + 0.02, hiss(0.25, 3, 14) * 0.5)

def blip(tp, f, g=0.2, d=0.12): put(fx, tp, sweep([f, f], d, g))
def organ(tp, notes, d=0.5, g=0.05):
    for f in notes:
        n = int(d * SR); tt = np.arange(n) / SR; put(fx, tp, (np.sin(2 * np.pi * f * tt) + 0.5 * np.sin(4 * np.pi * f * tt) + 0.25 * np.sin(8 * np.pi * f * tt)) * np.minimum(1, tt * 30) * np.minimum(1, (d - tt) * 15) * g)

def ring(tp, n=4, g=0.12):
    for k in range(n):
        for j in range(6): put(fx, tp + 0.45 * k + 0.05 * j, tone(1400 if j % 2 else 1750, 1400 if j % 2 else 1750, 0.05, 30, 0.2) * g)
def gurgle(tp, d=1.0, g=0.35):
    n = int(d * SR); tt = np.arange(n) / SR; f = 90 + 60 * np.sin(2 * np.pi * 7 * tt) + 40 * np.sin(2 * np.pi * 13 * tt)
    put(fx, tp, np.sin(2 * np.pi * np.cumsum(f) / SR) * np.hanning(n) * g)

def rumble(a, b, g=1.0, k=300): return lp(rng.normal(0, 1, N), k) * env(a, b, 0.2, 0.5) * g * 12.0
def lava_pops(a, b, n, g=0.35):
    for k in range(n): tp = rng.uniform(a, b); put(fx, tp, burst(0.05, 4, 40) * g); put(fx, tp, tone(rng.uniform(80, 160), 50, 0.12, 15, 0.5) * g * 0.6)

def beep(a, b, per=1.0, g=0.035, f=1000):
    k = 0
    while a + k * per < b: put(fx, a + k * per, tone(f, f, 0.09, 25, 0.1) * g); k += 1
def cry(tp, g=0.10):
    for k in range(3): put(fx, tp + 0.32 * k, sweep([520, 760, 600], 0.28, g, 0.06, 7))
def woof(tp, g=0.3): put(fx, tp, sweep([330, 420, 250], 0.16, g, 0.15, 60)); put(fx, tp, burst(0.12, 10, 18) * g * 0.6)
def moo(tp, g=0.22): put(fx, tp, sweep([150, 170, 160, 120], 1.0, g, 0.04, 5)); put(fx, tp, sweep([300, 340, 320, 240], 1.0, g * 0.35, 0.04, 5))
def fart(tp, dur=0.35, g=0.30, f0=110, f1=70):
    i0, i1 = int(tp * SR), min(N, int((tp + dur) * SR))
    if i1 > i0: fx[i0:i1] += saw([tp, tp + dur], [f0, f1], 5)[i0:i1] * g * np.hanning(i1 - i0) * (1 + 0.6 * np.sign(np.sin(2 * np.pi * 23 * t[i0:i1])))
def shatter(tp, g=0.55):
    put(fx, tp, hiss(0.6, 2, 6) * g)
    for k in range(9): put(fx, tp + rng.uniform(0, 0.4), tone(rng.uniform(2500, 5200), rng.uniform(2000, 4000), 0.12, 30, 0.1) * g * 0.35)
def flutter(a, b, g=0.05): return lp(rng.normal(0, 1, N), 6) * env(a, b, 0.1, 0.2) * g * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 16 * t)))
def breath(a, b, g=0.07):
    for k in range(int((b - a) / 1.1)): put(fx, a + 1.1 * k, burst(0.5, 25, 3) * np.hanning(int(0.5 * SR)) * g); put(fx, a + 1.1 * k + 0.55, burst(0.45, 12, 3) * np.hanning(int(0.45 * SR)) * g * 0.7)
# --- gancio: le tre culle
dundun(0.15, 0.4); beep(0.0, 4.7, 0.9)
put(fx, 1.6, sweep([300, 260], 0.12, 0.12)); woof(2.0, 0.22); cry(3.2, 0.05)
put(fx, 3.4, sweep([700, 200], 0.8, 0.08, 0.05, 8))
# --- fuori dall'ospedale, corridoio
for k in range(4): chime(5.0 + 0.4 * k, k + 2, 0.04)
for k in range(8): put(fx, 7.25 + 0.37 * k, burst(0.06, 3, 40) * (0.35 if k % 2 else 0.15))                   # morsi al panino
beep(7.1, 10.4, 1.0, 0.015)
# --- spinge
beep(10.4, 14.5, 0.55, 0.04, 1050)
for tp in (10.6, 11.62, 13.24): put(fx, tp, sweep([120, 95], 0.6, 0.14, 0.2, 18)); thud(tp + 0.05, 0.3)
beep(14.5, 25.8, 0.8, 0.03)
# --- le nascite
pop(15.94, 0.6); cry(16.15, 0.10)
for k in range(6): chime(16.86 + 0.15 * k, k, 0.06)
pop(19.56, 0.6); cry(19.75, 0.10)
for k, f in enumerate((523, 659, 784, 1047)): put(fx, 21.2 + 0.11 * k, tone(f, f, 0.6, 3, 0.4) * 0.12)
pop(24.94, 0.6); woof(25.05, 0.32); put(fx, 24.9, sweep([900, 120], 0.35, 0.14, 0.0))           # disco che si inceppa
# --- Pippo si gira, Tumbo capisce
put(fx, 26.44, sweep([180, 175], 1.4, 0.05, 0.02, 3)); dundun(28.0, 0.42)
for k in range(4): put(fx, 28.1 + 0.25 * k, sweep([1300, 1500], 0.18, 0.05))                       # fischietta
put(fx, 30.35, tone(260, 180, 0.2, 10, 0.4) * 0.3); put(fx, 31.4, sweep([500, 900], 0.3, 0.06))   # glup
for k in range(6): step(32.3 + 0.07 * k, 0.35, 260)
whoosh(32.7, 0.45, 1.4); shatter(33.08, 0.6)
# --- fuori: la mucca fatata
shatter(33.78, 0.5); put(fx, 34.3, sweep([200, 600, 300], 0.35, 0.18, 0.1, 12)); moo(34.45, 0.22)
fx += flutter(34.2, 37.6, 0.05)
for k in range(8): chime(34.6 + 0.12 * k, k, 0.04)
whoosh(35.6, 0.8, 1.6)
for k in range(9): fart(35.95 + 0.17 * k, 0.15 + 0.05 * (k % 3), 0.20, 120 - 4 * k, 70)
# --- puzza, svenimento
fx += lp(rng.normal(0, 1, N), 30) * env(37.5, 39.6, 0.4, 0.5) * 0.35; gurgle(37.6, 1.2, 0.18)
put(fx, 39.7, sweep([400, 300, 450, 250], 1.3, 0.07, 0.08, 4)); whoosh(41.0, 0.4, 1.0); thud(41.45, 0.9)
for k in range(10): chime(41.7 + 0.2 * k, k, 0.035)
# --- si riprende e chiama
put(fx, 43.76, burst(0.3, 6, 10) * 0.25); put(fx, 43.8, sweep([300, 500], 0.25, 0.07))
for k, f in enumerate((1209, 1336, 1477, 1209, 1336)): put(fx, 44.95 + 0.12 * k, tone(f, f, 0.09, 20, 0.1) * 0.08)
ring(45.7, 2, 0.06)
# --- le volanti
fx += siren(47.3, 49.5, 0.06) + siren(47.5, 49.5, 0.04, 2.4, 600, 820)
put(fx, 48.55, hiss(0.5, 5, 6) * 0.35); put(fx, 48.6, sweep([1800, 1500], 0.45, 0.05, 0.05, 40))   # frenata
for k in range(6): put(fx, 49.6 + 0.22 * k, burst(0.08, 8, 25) * 0.25)                                         # annusano
for k in range(2): put(fx, 51.66 + 0.1 * k, burst(0.05, 3, 40) * 0.5); pop(51.7 + 0.1 * k, 0.35)
breath(51.9, 54.6, 0.08)
clang(53.9, 0.5); click(54.0, 2400, 0.4); dundun(53.85, 0.25)
# --- foto segnaletica
shutter(55.2); shutter(56.9); dundun(56.15, 0.4)
# --- caricata in volante e scorreggia di nuovo
fx += siren(58.0, 65.8, 0.04)
click(58.98, 2400, 0.4); clang(59.0, 0.3); whoosh(59.6, 0.3, 0.9)
fx += saw([60.3, 62.2], [55, 95], 10) * env(60.3, 62.25, 0.2, 0.05) * 0.10
fart(62.22, 0.9, 0.45, 90, 55); thud(62.3, 1.0); put(fx, 62.3, burst(1.2, 40, 3) * 1.5)
put(fx, 62.5, hiss(0.6, 5, 5) * 0.3)
# --- rinforzi
fx += siren(63.9, 65.8, 0.05, 2.9, 700, 930) + siren(64.1, 65.8, 0.04, 2.2, 560, 760) + siren(64.3, 65.8, 0.04, 3.3, 640, 880)
fx = np.tanh(fx * 1.1) * 0.45

# musichetta: valzerino pizzicato da reparto maternità (3/4, 150 bpm), poi suspense
bpm = 150; beat = 60 / bpm; chords = [(261.63, 329.63, 392.0), (293.66, 349.23, 440.0), (246.94, 293.66, 392.0), (261.63, 329.63, 392.0), (220.0, 261.63, 329.63), (174.61, 220.0, 261.63), (196.0, 246.94, 293.66), (196.0, 246.94, 349.23)]
m = np.zeros(N)
def pluck(f, t0, dur=0.4, amp=0.5):
    n = int(dur * SR); tt = np.arange(n) / SR; x = sum(np.sin(2 * np.pi * f * h * tt) * np.exp(-tt * (5 + 3 * h)) / h for h in range(1, 5)); put(m, t0, amp * x * np.minimum(1, tt * 400))
def section(a, b, sp=1.0, k0=0):
    bt = beat / sp; nb = int((b - a) / (bt * 3))
    for bar in range(nb):
        ch = chords[(bar + k0) % 8]; t0 = a + bar * bt * 3
        pluck(ch[0] / 2, t0, 0.5, 0.55); pluck(ch[1], t0 + bt, 0.3, 0.3); pluck(ch[2], t0 + bt, 0.3, 0.3); pluck(ch[1], t0 + 2 * bt, 0.3, 0.3); pluck(ch[2], t0 + 2 * bt, 0.3, 0.3)
        mel = [ch[2] * 2, ch[1] * 2, ch[0] * 2][bar % 3]; pluck(mel, t0, 0.35, 0.28); pluck(mel * 1.122, t0 + 1.5 * bt, 0.25, 0.2)
section(0.0, 24.9)
for k in range(int((33.7 - 25.9) / 0.5)): pluck(110.0 if k % 2 == 0 else 116.54, 25.9 + 0.5 * k, 0.5, 0.5)    # suspense
section(33.78, 65.8, 1.18, 4)
mus = m / np.abs(m).max() * 0.10
mus *= np.interp(t, [0, 0.6, 24.85, 24.95, 25.8, 26.0, 33.6, 33.78, 62.1, 62.25, 63.0, 63.4, DUR - 1.0, DUR], [0.6, 1, 1, 0, 0, 0.8, 0.8, 1, 1, 0, 0, 0.8, 0.8, 0])
mix = v * 1.0 + mus + fx
mix = np.clip(mix / max(1, np.abs(mix).max() / 0.95), -1, 1)
mix[-int(0.15 * SR):] *= np.linspace(1, 0, int(0.15 * SR))
st = np.stack([mix, mix], 1); pcm = (st * 32767).astype(np.int16)
with wave.open('audio/t015.wav', 'wb') as o:
    o.setnchannels(2); o.setsampwidth(2); o.setframerate(SR); o.writeframes(pcm.tobytes())
print('audio ok', np.abs(v).max(), np.abs(mus).max(), np.abs(fx).max())
