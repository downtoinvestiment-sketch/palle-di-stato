"""Test 016 (il secondo parto di Eleonora) - audio: voce + musichetta sintetica + effetti. Esce audio/t016.wav (59.3 s, senza prossimo episodio e CTA)"""
import numpy as np, subprocess, wave
SR = 44100; DUR = 59.3; N = int(DUR * SR); rng = np.random.default_rng(16)
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
subprocess.run(['/usr/local/bin/ffmpeg', '-y', '-loglevel', 'error', '-i', 'audio/voce_t016.mp3', '-ar', str(SR), '-ac', '1', 'audio/voce44_t016.wav'], check=True)
w = wave.open('audio/voce44_t016.wav'); v = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(float) / 32768; v = np.pad(v, (0, max(0, N - len(v))))[:N]

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

def crunch(tp, g=0.25): put(fx, tp, hiss(0.07, 2, 30) * g); put(fx, tp + 0.04, burst(0.05, 2, 40) * g * 0.6)
def fsiren(a, b, g=0.06):                                     # sirena pompieri a due toni
    k = 0
    while a + 0.5 * k < b: f = 960 if k % 2 == 0 else 720; put(fx, a + 0.5 * k, sweep([f, f], 0.48, g, 0.0)); k += 1
def pchord(tp, notes, g=0.16, d=1.6):
    for f in notes:
        n = int(d * SR); tt = np.arange(n) / SR; x = sum(np.sin(2 * np.pi * f * h * tt) * np.exp(-tt * (2.5 + 1.5 * h)) / h ** 1.3 for h in range(1, 6)); put(fx, tp, x * g * np.minimum(1, tt * 300))
def scratch(tp, g=0.3): put(fx, tp, sweep([900, 300, 1200, 200], 0.35, g, 0.2, 40)); put(fx, tp, hiss(0.35, 3, 4) * g * 0.6)
# --- gancio: sala parto
beep(0.0, 6.7, 0.85, 0.035, 1000); breath(0.4, 2.8, 0.06)
for tp in (0.7, 1.6, 2.4): put(fx, tp, sweep([120, 95], 0.5, 0.12, 0.2, 18))
dundun(4.7, 0.42); put(fx, 4.9, sweep([180, 175], 1.6, 0.05, 0.02, 3))
# --- ospedale, spinge, corridoio con il panino
for k in range(3): chime(6.75 + 0.25 * k, k + 1, 0.04)
put(fx, 7.9, sweep([120, 95], 0.6, 0.14, 0.2, 18)); thud(8.0, 0.25)
for k in range(10): put(fx, 9.1 + 0.3 * k, burst(0.06, 3, 40) * (0.35 if k % 2 else 0.15))
# --- le nascite
beep(12.0, 29.9, 0.9, 0.025, 1000)
for tb in (13.08, 16.30): pop(tb, 0.6); cry(tb + 0.2, 0.09); thud(tb + 0.75, 0.15)
put(fx, 14.1, tone(880, 880, 0.18, 12, 0.2) * 0.08); put(fx, 17.55, tone(880, 880, 0.18, 12, 0.2) * 0.08)
pop(19.78, 0.8); put(fx, 19.85, sweep([200, 600, 300], 0.4, 0.2, 0.1, 12)); thud(20.4, 0.9)
fsiren(20.4, 29.2, 0.07)
fx += lp(rng.normal(0, 1, N), 120) * env(20.5, 28.4, 0.2, 0.4) * 1.2 * (1 + 0.5 * np.sin(2 * np.pi * 7 * t))   # motore
for tp in (22.1, 24.6, 27.0): clang(tp, 0.25)
for k in range(5): click(25.3 + 0.18 * k, 2600, 0.18)                                                            # scrive
pop(29.98, 0.7); thud(30.6, 0.9); pchord(30.65, [261.63, 329.63, 392.0, 523.25], 0.12)
pop(32.16, 0.8); put(fx, 32.2, sweep([220, 440], 0.3, 0.12)); thud(33.55, 0.8)
for k in range(5): put(fx, 34.6 + 0.4 * k, burst(0.05, 2, 40) * 0.12)                                            # baffi
for k in range(7): step(37.95 + 0.11 * k, 0.4, 230)
click(38.4, 900, 0.3); put(fx, 38.45, sweep([300, 260], 0.3, 0.05)); thud(39.1, 0.4)
# --- rivelazioni
dundun(39.4, 0.45); put(fx, 41.8, hiss(0.35, 3, 6) * 0.3); thud(43.1, 0.5); woof(43.2, 0.3); put(fx, 43.15, hiss(0.4, 4, 5) * 0.4)
dundun(44.2, 0.38); put(fx, 47.95, sweep([500, 700], 0.35, 0.05)); whoosh(49.8, 0.6, 1.6)
for k in range(10): crunch(51.0 + 0.24 * k, 0.28)
dundun(53.3, 0.42); whoosh(55.2, 0.6, 1.7); scratch(55.75, 0.3); thud(55.7, 0.5)
thud(58.1, 1.0); put(fx, 58.1, burst(0.4, 10, 6) * 0.6)                                                         # panino a terra
pchord(58.8, [110.0, 164.81, 220.0, 277.18], 0.10, 0.5); thud(58.8, 0.5)                                  # chiusura
fx = np.tanh(fx * 1.1) * 0.45

# musichetta: boogie col basso che cammina e i battiti di mani (diversa dal valzer del parto)
bpm = 132; beat = 60 / bpm; m = np.zeros(N)
def pl(f, t0, dur=0.3, amp=0.5, dec=6):
    n = int(dur * SR); tt = np.arange(n) / SR; x = sum(np.sin(2 * np.pi * f * h * tt) * np.exp(-tt * (dec + 2 * h)) / h for h in range(1, 5)); put(m, t0, amp * x * np.minimum(1, tt * 400))
def clap(t0, a=0.25): put(m, t0, hiss(0.08, 2, 30) * a)
prog = [110.0, 110.0, 146.83, 110.0, 164.81, 146.83, 110.0, 164.81]
walk = [0, 4, 7, 9, 10, 9, 7, 4]
def boogie(a, b, k0=0):
    nb = int((b - a) / (beat * 4))
    for bar in range(nb):
        root = prog[(bar + k0) % 8]; t0 = a + bar * beat * 4
        for i in range(8): pl(root * 2 ** (walk[i] / 12) / 2, t0 + i * beat / 2, 0.28, 0.5)
        for i in (1, 3): clap(t0 + i * beat)
        for i in (0, 2): pl(root * 2, t0 + i * beat + beat / 2, 0.2, 0.18, 9); pl(root * 2 * 1.26, t0 + i * beat + beat / 2, 0.2, 0.15, 9)
boogie(0.0, 39.3); boogie(44.2, 47.4, 3); boogie(50.9, 55.0, 5); boogie(55.9, 59.3, 1)
for k in range(int((44.1 - 39.4) / 0.6)): pl(98.0 if k % 2 == 0 else 103.83, 39.4 + 0.6 * k, 0.6, 0.5, 3)   # suspense
mus = m / np.abs(m).max() * 0.10
mus *= np.interp(t, [0, 0.5, 39.2, 39.4, 44.1, 44.3, 47.3, 47.5, 50.8, 51.0, 54.9, 55.1, 55.8, 56.1, DUR - 0.5, DUR], [0.6, 1, 1, 0.7, 0.7, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0])
mix = v * 1.0 + mus + fx
mix = np.clip(mix / max(1, np.abs(mix).max() / 0.95), -1, 1)
mix[-int(0.25 * SR):] *= np.linspace(1, 0, int(0.25 * SR))
st = np.stack([mix, mix], 1); pcm = (st * 32767).astype(np.int16)
with wave.open('audio/t016.wav', 'wb') as o:
    o.setnchannels(2); o.setsampwidth(2); o.setframerate(SR); o.writeframes(pcm.tobytes())
print('audio ok', np.abs(v).max(), np.abs(mus).max(), np.abs(fx).max())
