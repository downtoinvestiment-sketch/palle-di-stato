"""Test 009 (Pippo contro Gualtiero, ep. 1) - audio: voce + musichetta sintetica + effetti. Esce audio/t009.wav (44 s)"""
import numpy as np, subprocess, wave
SR = 44100; DUR = 44.0; N = int(DUR * SR); rng = np.random.default_rng(9)
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
subprocess.run(['/usr/local/bin/ffmpeg', '-y', '-loglevel', 'error', '-i', 'audio/voce_t009.mp3', '-ar', str(SR), '-ac', '1', 'audio/voce44_t009.wav'], check=True)
w = wave.open('audio/voce44_t009.wav'); v = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(float) / 32768; v = np.pad(v, (0, max(0, N - len(v))))[:N]

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
# --- gancio: il phon scioglie il pupazzo
fx += (saw([0, 44], [185, 185], 12) * 0.035 + lp(rng.normal(0, 1, N), 14) * 0.22) * env(0.0, 4.45, 0.08, 0.25)
put(fx, 1.6, sweep([900, 700, 520, 300], 2.2, 0.08, 0.02, 5)); laugh(2.55, 8)
for k in range(9): put(fx, 0.5 + 0.42 * k, tone(1400 - 60 * k, 700, 0.05, 40, 0.2) * 0.12)            # gocce
# --- faccia a faccia
dundun(4.72); bell(6.25); bell(6.6, 0.10)
# --- la neve ad agosto
for k in range(6): chime(7.6 + 0.2 * k, k)
pop(8.95, 0.5); put(fx, 9.0, hiss(0.7, 3, 4) * 0.25)
for k, f in enumerate((349, 330, 262)): put(fx, 9.3 + 0.2 * k, sweep([f, f * 0.97], 0.24 if k < 2 else 0.4, 0.10, 0.03, 6))
# --- primo: il freezer, poi il barbecue
pop(10.05); put(fx, 10.9, sweep([500, 330, 420], 0.35, 0.07, 0.03, 12)); put(fx, 11.4, burst(0.6, 40, 4) * 1.0); thud(11.97, 0.9)
for k in range(30): put(fx, 11.8 + rng.uniform(0, 0.9), tone(2200 + rng.uniform(0, 1500), 1800, 0.035, 60, 0.2) * 0.13)
pop(13.0, 0.45); put(fx, 13.58, burst(0.5, 70, 6) * 3.0); put(fx, 13.58, tone(120, 60, 0.4, 7, 0.5) * 0.6)
for k in range(40): put(fx, 13.7 + rng.uniform(0, 1.3), burst(0.02, 2, 80) * rng.uniform(0.3, 0.8))  # scoppiettio
fx += (rng.normal(0, 1, N) - lp(rng.normal(0, 1, N), 3)) * env(13.9, 15.0, 0.2, 0.4) * 0.05            # sfrigolio
laugh(14.0, 5, 0.18)
# --- secondo: mille ghiaccioli, e Gualtiero li lecca tutti
for k in range(20): put(fx, 15.4 + 0.085 * k, tone(500 + 45 * k, 700 + 45 * k, 0.05, 30, 0.2) * 0.16)
pop(16.65, 0.4); put(fx, 18.2, sweep([200, 520, 300], 0.2, 0.3))
for k in range(18): put(fx, 18.38 + 0.105 * k, sweep([300, 950], 0.075, 0.2)); put(fx, 18.38 + 0.105 * k, hiss(0.05, 3, 40) * 0.25)
for k in range(13): step(18.4 + 0.15 * k, 0.35)
put(fx, 21.15, sweep([120, 95, 70], 0.55, 0.5, 0.35, 34)); put(fx, 20.45, tone(160, 160, 0.08, 25, 0.5) * 0.4); put(fx, 20.75, tone(160, 160, 0.08, 25, 0.5) * 0.4)
# --- terzo: il cannone sparaneve
pop(22.02, 0.45)
fx += saw([22.3, 22.8, 27.8, 27.9], [60, 210, 210, 80], 16) * np.interp(t, [22.3, 22.8, 27.7, 27.9], [0, 0.045, 0.045, 0]) + lp(rng.normal(0, 1, N), 25) * np.interp(t, [22.5, 22.9, 27.7, 27.9], [0, 0.55, 0.55, 0])
for k in range(6): put(fx, 24.4 + 0.15 * k, tone(520 + 40 * (k % 2), 500, 0.05, 40, 0.2) * 0.2)          # in punta di piedi
whoosh(25.6, 0.5, 1.6); put(fx, 25.75, sweep([300, 520, 380], 0.4, 0.09, 0.04, 14)); laugh(26.3, 3, 0.18)
put(fx, 27.0, burst(0.8, 60, 4) * 3.2); thud(27.05, 1.0); put(fx, 27.3, sweep([900, 1350, 800], 0.3, 0.22, 0.05, 30))
# --- il camion di polistirolo
fx += saw([27.9, 30.3, 30.6], [48, 62, 40], 10) * np.interp(t, [27.9, 28.3, 30.2, 30.7], [0, 0.10, 0.12, 0]) * (1 + 0.3 * np.sin(2 * np.pi * 13 * t))
for tp in (28.45, 28.95):
    for f in (330, 415): put(fx, tp, sweep([f, f], 0.36, 0.09))
put(fx, 30.15, hiss(0.45, 4, 5) * 0.5); thud(30.35, 0.8)
put(fx, 30.85, sweep([180, 480], 0.8, 0.08)); put(fx, 31.2, burst(1.3, 90, 2.5) * 3.5)
for k in range(14): chime(31.5 + 0.2 * k, k * 3 + 1, 0.05)
for k in range(11): put(fx, 33.05 + 0.3 * k + 0.05 * np.sin(k * 2.3), tone(130, 80, 0.12, 18, 0.5) * 0.5); put(fx, 33.05 + 0.3 * k, burst(0.1, 30, 20) * 0.6)
for k in range(9): put(fx, 33.3 + 0.33 * k, sweep([170, 120, 150], 0.2, 0.22, 0.3, 30))                 # Gualtiero ringhia
whoosh(35.3, 0.35, 1.3, 25); put(fx, 36.15, tone(300, 200, 0.06, 40, 0.4) * 0.5)
# --- prossimo episodio: il lanciafiamme
fx += (np.sin(2 * np.pi * 55 * t) + np.sin(2 * np.pi * 58.3 * t)) * env(36.5, 38.6, 0.5, 0.15) * 0.10
put(fx, 37.6, tone(800, 760, 0.12, 25, 0.6) * 0.3); put(fx, 37.62, burst(0.06, 2, 50) * 0.8); put(fx, 37.85, tone(600, 560, 0.08, 30, 0.6) * 0.25)
fx += lp(rng.normal(0, 1, N), 45) * np.interp(t, [38.5, 38.62, 39.6, 39.8], [0, 4.5, 3.6, 0]) * (1 + 0.3 * np.sin(2 * np.pi * 9 * t)); put(fx, 38.55, tone(90, 45, 0.9, 3, 0.6) * 0.8)
put(fx, 39.15, sweep([420, 220], 0.16, 0.2))                                                           # glom
# --- team Pippo o team Gualtiero?
dundun(39.82, 0.4); bell(41.3); pop(41.62, 0.4)
fx += lp(rng.normal(0, 1, N), 30) * env(39.9, 43.7, 0.2, 0.4) * 0.35                                  # fiammella pilota
for k, f in enumerate((196, 131)): put(fx, 42.9 + 0.3 * k, tone(f * 2, f * 2, 0.6, 5, 0.5) * 0.2)
fx = np.tanh(fx * 1.1) * 0.45

bpm = 116; beat = 60 / bpm; chords = [(146.83, 174.61, 220.0), (116.54, 146.83, 174.61), (130.81, 164.81, 196.0), (110.0, 138.59, 164.81)]   # Dm Bb C A: un po' da duello
m = np.zeros(N)
def pluck(f, t0, dur=0.5, amp=0.5):
    n = int(dur * SR); tt = np.arange(n) / SR; put(m, t0, amp * (np.sin(2 * np.pi * f * tt) + 0.4 * np.sin(4 * np.pi * f * tt) + 0.2 * np.sin(6 * np.pi * f * tt)) * np.exp(-tt * 7))
for bar in range(int(DUR / (beat * 4)) + 1):
    ch = chords[bar % 4]
    for b in range(8):
        t0 = bar * beat * 4 + b * beat / 2; f = ch[[0, 2, 1, 2, 0, 1, 2, 1][b]] * 2
        pluck(f, t0, 0.4, 0.30 if b % 2 == 0 else 0.22)
    pluck(ch[0] / 2, bar * beat * 4, 0.9, 0.5); pluck(ch[0] / 2, bar * beat * 4 + 1.5 * beat, 0.5, 0.35); pluck(ch[0] / 2, bar * beat * 4 + 2.5 * beat, 0.9, 0.4); pluck(ch[2] / 2, bar * beat * 4 + 3 * beat, 0.5, 0.3)
mus = m / np.abs(m).max() * 0.19
mus *= np.interp(t, [0, 0.8, 36.4, 36.7, 39.7, 40.0, 42.9, 43.2, 44.0], [0.6, 1, 1, 0.3, 0.3, 1, 1, 0.35, 0.0])
mix = v * 1.0 + mus + fx
mix = np.clip(mix / max(1, np.abs(mix).max() / 0.95), -1, 1)
mix[-int(0.15 * SR):] *= np.linspace(1, 0, int(0.15 * SR))
st = np.stack([mix, mix], 1); pcm = (st * 32767).astype(np.int16)
with wave.open('audio/t009.wav', 'wb') as o:
    o.setnchannels(2); o.setsampwidth(2); o.setframerate(SR); o.writeframes(pcm.tobytes())
print('audio ok', np.abs(v).max(), np.abs(mus).max(), np.abs(fx).max())
