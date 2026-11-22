"""Test 014 (il toast di Pippo) - audio: voce + musichetta sintetica + effetti. Esce audio/t014.wav (49.8 s)"""
import numpy as np, subprocess, wave
SR = 44100; DUR = 49.8; N = int(DUR * SR); rng = np.random.default_rng(14)
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
subprocess.run(['/usr/local/bin/ffmpeg', '-y', '-loglevel', 'error', '-i', 'audio/voce_t014.mp3', '-ar', str(SR), '-ac', '1', 'audio/voce44_t014.wav'], check=True)
w = wave.open('audio/voce44_t014.wav'); v = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(float) / 32768; v = np.pad(v, (0, max(0, N - len(v))))[:N]

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
# --- gancio: il caos
fx += rumble(0.0, 5.75, 0.55) + lp(rng.normal(0, 1, N), 40) * env(0.0, 5.75, 0.1, 0.3) * 0.5
lava_pops(0.2, 5.6, 22); put(fx, 1.9, sweep([180, 140, 120], 0.6, 0.25, 0.3, 30))
# --- cucina
for k in range(3): put(fx, 6.0 + 1.1 * k, tone(1200, 1200, 0.03, 60, 0.2) * 0.05)                         # orologio
put(fx, 8.4, sweep([400, 600, 350], 0.5, 0.07, 0.05, 10)); dundun(9.1, 0.25)
# --- il forno sale dal terreno
fx += rumble(9.95, 11.1, 0.6); thud(10.85, 1.0); clang(10.9, 0.4); pop(11.1, 0.4)
put(fx, 12.9, sweep([300, 330], 0.6, 0.06)); put(fx, 13.7, sweep([500, 320], 0.5, 0.08, 0.05, 8))               # tiepido...
# --- il vulcano
fx += rumble(15.0, 16.7, 1.4); thud(16.4, 1.3); fx += rumble(16.4, 49.8, 0.25, 400)
put(fx, 16.6, burst(1.0, 60, 3) * 3.0); lava_pops(16.7, 49.5, 90, 0.3)
put(fx, 17.5, sweep([500, 900, 1200], 0.5, 0.12, 0.08, 20)); for_steps = [step(17.45 + 0.11 * k, 0.3, 300) for k in range(14)]
# --- troppo caldo: sfrigolio, case che si sciolgono
fx += (rng.normal(0, 1, N) - lp(rng.normal(0, 1, N), 3)) * env(19.8, 23.3, 0.2, 0.3) * 0.08
put(fx, 21.5, sweep([400, 300, 150], 1.6, 0.12, 0.04, 6)); put(fx, 22.2, sweep([380, 260, 120], 1.2, 0.10, 0.04, 5))
# --- le torri di raffreddamento
fx += rumble(23.3, 24.7, 1.1); thud(24.5, 1.1); fx += lp(rng.normal(0, 1, N), 8) * env(24.6, 49.8, 0.6, 0.5) * 0.10   # sibilo del vapore
# --- la catena di montaggio
for k in range(int((36.5 - 27.75) / 0.18)): put(fx, 27.75 + 0.18 * k, tone(220, 200, 0.03, 50, 0.3) * 0.12)     # tac-tac del nastro
whoosh(29.7, 0.6, 1.2); put(fx, 30.2, sweep([300, 900], 3.5, 0.03))
put(fx, 33.0, sweep([250, 200], 0.5, 0.15, 0.2, 20))
for k in range(10): put(fx, 34.15 + 0.08 * k, burst(0.04, 3, 50) * 0.5)                                         # rulli
put(fx, 34.6, sweep([900, 300], 0.5, 0.12)); put(fx, 35.15, tone(600, 500, 0.05, 40, 0.2) * 0.3)             # la fetta cade, tic
put(fx, 35.3, sweep([392, 370, 349, 262], 1.0, 0.08, 0.03, 6))
# --- il camion con la fetta gigante
fx += saw([36.5, 41.2], [55, 70], 10) * np.interp(t, [36.5, 36.9, 38.0, 38.3, 39.6, 40.0, 41.2], [0, 0.10, 0.10, 0.05, 0.05, 0.10, 0]) * (1 + 0.3 * np.sin(2 * np.pi * 13 * t))
for k in range(3): put(fx, 38.25 + 0.12 * k, tone(1100, 1100, 0.08, 20, 0.3) * 0.15)                               # bip retromarcia
whoosh(38.6, 1.0, 1.6); put(fx, 38.4, sweep([300, 250], 0.4, 0.15)); thud(40.15, 0.6); clang(40.4, 0.4)
# --- il toast è pronto
put(fx, 40.7, sweep([250, 230], 0.4, 0.12)); put(fx, 41.6, tone(1568, 1568, 1.0, 3, 0.3) * 0.2)                 # ding!
for k, f in enumerate((523, 659, 784, 1047)): put(fx, 41.75 + 0.12 * k, tone(f, f, 0.9, 3, 0.4) * 0.11)
for k in range(8): chime(42.3 + 0.25 * k, k, 0.05)
# --- Tumbo se lo mangia
whoosh(44.5, 0.5, 1.4); put(fx, 44.95, burst(0.25, 3, 12) * 1.6); put(fx, 44.95, tone(160, 70, 0.3, 10, 0.6) * 0.8)    # CHOMP
for k in range(5): put(fx, 45.2 + 0.12 * k, burst(0.05, 3, 40) * 0.6)                                              # masticare
put(fx, 46.4, sweep([140, 105, 80], 0.7, 0.45, 0.35, 32))                                                          # rutto
put(fx, 47.5, sweep([392, 370, 349, 262], 1.1, 0.07, 0.03, 6))
fx = np.tanh(fx * 1.1) * 0.45

# musichetta: fanfara da fabbrica saltellante, 128 bpm
bpm = 128; beat = 60 / bpm; chords = [(220.0, 261.63, 329.63), (174.61, 220.0, 261.63), (196.0, 246.94, 293.66), (164.81, 207.65, 246.94)]
m = np.zeros(N)
def mar(f, t0, dur=0.3, amp=0.5):
    n = int(dur * SR); tt = np.arange(n) / SR; put(m, t0, amp * (np.sin(2 * np.pi * f * tt) + 0.3 * np.sign(np.sin(2 * np.pi * f * tt)) * 0.3) * np.exp(-tt * 10))
for bar in range(int(DUR / (beat * 4)) + 1):
    ch = chords[bar % 4]
    for b in range(8):
        if b % 4 == 3: continue
        mar(ch[[0, 1, 2, 1, 2, 0, 1, 2][b]] * 2, bar * beat * 4 + b * beat / 2, 0.25, 0.26)
    mar(ch[0] / 2, bar * beat * 4, 0.5, 0.5); mar(ch[0] / 2, bar * beat * 4 + beat, 0.3, 0.35); mar(ch[2] / 2, bar * beat * 4 + 2 * beat, 0.5, 0.45); mar(ch[1] / 2, bar * beat * 4 + 3 * beat, 0.3, 0.35)
mus = m / np.abs(m).max() * 0.10
mus *= np.interp(t, [0, 0.8, 44.8, 45.0, 46.0, 46.4, DUR - 1.1, DUR - 0.8, DUR], [0.6, 1, 1, 0.0, 0.0, 0.6, 0.6, 0.3, 0.0])
mix = v * 1.0 + mus + fx
mix = np.clip(mix / max(1, np.abs(mix).max() / 0.95), -1, 1)
mix[-int(0.15 * SR):] *= np.linspace(1, 0, int(0.15 * SR))
st = np.stack([mix, mix], 1); pcm = (st * 32767).astype(np.int16)
with wave.open('audio/t014.wav', 'wb') as o:
    o.setnchannels(2); o.setsampwidth(2); o.setframerate(SR); o.writeframes(pcm.tobytes())
print('audio ok', np.abs(v).max(), np.abs(mus).max(), np.abs(fx).max())
