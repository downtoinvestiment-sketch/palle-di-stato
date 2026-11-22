"""Test 010 (Pippo contro Gualtiero, ep. 2: il processo al sole) - audio: voce + musichetta sintetica + effetti. Esce audio/t010.wav (45.8 s)"""
import numpy as np, subprocess, wave
SR = 44100; DUR = 45.8; N = int(DUR * SR); rng = np.random.default_rng(10)
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
subprocess.run(['/usr/local/bin/ffmpeg', '-y', '-loglevel', 'error', '-i', 'audio/voce_t010.mp3', '-ar', str(SR), '-ac', '1', 'audio/voce44_t010.wav'], check=True)
w = wave.open('audio/voce44_t010.wav'); v = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(float) / 32768; v = np.pad(v, (0, max(0, N - len(v))))[:N]

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
# --- gancio: Pippo arrosto, il sole se la ride
fx += (rng.normal(0, 1, N) - lp(rng.normal(0, 1, N), 3)) * env(0.0, 5.2, 0.05, 0.3) * 0.07 * (1 + 0.5 * np.sin(2 * np.pi * 11 * t))
put(fx, 0.15, sweep([500, 950, 800, 1000, 700], 1.0, 0.10, 0.06, 18))
for k in range(4): chime(2.85 + 0.12 * k, k, 0.09)
laugh(3.0, 7, 0.16)
dundun(5.42); laugh(5.6, 8, 0.2); bell(6.9)
# --- team Pippo o team Sole
pop(7.95, 0.5); put(fx, 8.5, saw([8.5, 9.3], [95, 70], 6)[int(8.5 * SR):int(9.3 * SR)] * 0.12 * np.hanning(int(9.3 * SR) - int(8.5 * SR)))   # pernacchia
# --- la telefonata e l'arresto
for k, f in enumerate((941, 1209, 852)): put(fx, 10.8 + 0.17 * k, sweep([f, f], 0.11, 0.10))
for k in range(2): put(fx, 11.45 + 0.32 * k, sweep([440, 440], 0.22, 0.07, 0.08, 25))
sir = np.where((t * 2.6) % 1.0 < 0.5, 650.0, 870.0); fx += np.sin(2 * np.pi * np.cumsum(sir) / SR) * np.interp(t, [12.15, 12.3, 13.9, 14.2], [0, 0.085, 0.085, 0])
put(fx, 12.45, hiss(0.35, 4, 6) * 0.55); thud(12.66, 0.5)
for k in range(9): click(12.75 + 0.05 * k, 900 + 60 * k, 0.22)
for k in range(8): step(13.2 + 0.08 * k, 0.4, 420 + 30 * k)
click(13.9, 2400, 0.6); click(13.98, 2100, 0.6); clang(13.92, 0.35); put(fx, 14.3, sweep([520, 300], 0.5, 0.12, 0.04, 7))
# --- foto segnaletica e cella
click(15.53, 3000, 0.7); put(fx, 15.55, hiss(0.25, 3, 14) * 0.5); put(fx, 15.6, sweep([3000, 6000], 0.5, 0.03))
put(fx, 16.2, sweep([900, 200], 0.16, 0.12)); thud(16.36, 1.1); clang(16.36, 0.9); clang(16.45, 0.4)
for k in range(4): put(fx, 17.3 + 0.55 * k, tone(1500, 900, 0.05, 40, 0.2) * 0.14)                                 # gocce in cella
for k, f in enumerate((392, 370, 349, 262)): put(fx, 17.9 + 0.3 * k, sweep([f, f * 0.97], 0.34 if k < 3 else 0.6, 0.09, 0.03, 6))
# --- il processo
fx += lp(rng.normal(0, 1, N), 90) * env(19.9, 22.4, 0.3, 0.4) * 1.0                                                # brusio
for bt in (20.05, 20.3): put(fx, bt, tone(240, 180, 0.08, 30, 0.5) * 0.6)
dundun(22.6, 0.35)
for k, f in enumerate((523, 659, 784, 1047)): put(fx, 25.6, tone(f, f, 2.0, 1.2, 0.1) * 0.05)                     # coro angelico
for k in range(5): chime(25.65 + 0.3 * k, k, 0.06)
whoosh(29.35, 0.35, 1.5); fx += (rng.normal(0, 1, N) - lp(rng.normal(0, 1, N), 3)) * env(29.5, 30.8, 0.05, 0.3) * 0.09
put(fx, 29.7, sweep([300, 620], 0.5, 0.10, 0.03, 9)); put(fx, 29.75, sweep([380, 760], 0.5, 0.07, 0.03, 11))      # ooh
for bt in (31.37, 32.32): put(fx, bt, tone(260, 170, 0.1, 25, 0.6) * 0.9); put(fx, bt, burst(0.05, 4, 40) * 0.8)
put(fx, 31.45, sweep([600, 1300, 900], 0.5, 0.12, 0.08, 20)); fx += lp(rng.normal(0, 1, N), 20) * env(32.5, 33.8, 0.2, 0.5) * 0.5   # urlo del sole, applausi
# --- buio
click(33.9, 700, 0.8); put(fx, 33.92, sweep([400, 60], 0.7, 0.2))
cr = np.zeros(N)
for k in range(19):
    for j in range(3): put(cr, 34.4 + 0.14 * k + 0.035 * j, tone(4300, 4300, 0.025, 60, 0.1) * 0.05)
fx += cr; put(fx, 35.1, sweep([300, 420], 0.25, 0.10)); put(fx, 36.1, sweep([220, 180], 0.22, 0.2, 0.2, 30))
put(fx, 37.6, tone(800, 760, 0.12, 25, 0.6) * 0.3); click(37.62, 1500, 0.5); click(37.95, 1200, 0.4)
fx += lp(rng.normal(0, 1, N), 45) * np.interp(t, [38.9, 39.02, 40.0, 40.2], [0, 4.5, 3.6, 0]) * (1 + 0.3 * np.sin(2 * np.pi * 9 * t)); put(fx, 38.95, tone(90, 45, 0.9, 3, 0.6) * 0.8)
put(fx, 39.3, sweep([900, 1400, 700], 0.4, 0.12, 0.08, 25))
# --- prossimo episodio: la pioggia
put(fx, 40.22, burst(1.2, 120, 2.5) * 5.0); put(fx, 40.22, tone(70, 40, 1.0, 3, 0.7) * 0.7)
fx += (rng.normal(0, 1, N) - lp(rng.normal(0, 1, N), 2)) * env(40.3, 43.2, 0.2, 0.2) * 0.05
for k, f in enumerate((941, 1209, 852)): put(fx, 41.7 + 0.17 * k, sweep([f, f], 0.11, 0.09))
# --- team Pippo o team Gualtiero?
fx += lp(rng.normal(0, 1, N), 30) * env(43.25, 45.6, 0.1, 0.4) * 0.35; dundun(43.3, 0.4); laugh(44.3, 5, 0.16)
for k, f in enumerate((196, 131)): put(fx, 44.9 + 0.3 * k, tone(f * 2, f * 2, 0.6, 5, 0.5) * 0.2)
fx = np.tanh(fx * 1.1) * 0.45

bpm = 116; beat = 60 / bpm; chords = [(146.83, 174.61, 220.0), (116.54, 146.83, 174.61), (130.81, 164.81, 196.0), (110.0, 138.59, 164.81)]
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
mus *= np.interp(t, [0, 0.8, 33.85, 33.95, 40.1, 40.3, 44.7, 45.0, 45.8], [0.6, 1, 1, 0.0, 0.0, 1, 1, 0.35, 0.0])
mix = v * 1.0 + mus + fx
mix = np.clip(mix / max(1, np.abs(mix).max() / 0.95), -1, 1)
mix[-int(0.15 * SR):] *= np.linspace(1, 0, int(0.15 * SR))
st = np.stack([mix, mix], 1); pcm = (st * 32767).astype(np.int16)
with wave.open('audio/t010.wav', 'wb') as o:
    o.setnchannels(2); o.setsampwidth(2); o.setframerate(SR); o.writeframes(pcm.tobytes())
print('audio ok', np.abs(v).max(), np.abs(mus).max(), np.abs(fx).max())
