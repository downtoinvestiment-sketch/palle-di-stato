"""Test 011 (Pippo e il tornado) - audio: voce + musichetta sintetica + effetti. Esce audio/t011.wav (38.3 s)"""
import numpy as np, subprocess, wave
SR = 44100; DUR = 38.3; N = int(DUR * SR); rng = np.random.default_rng(11)
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
subprocess.run(['/usr/local/bin/ffmpeg', '-y', '-loglevel', 'error', '-i', 'audio/voce_t011.mp3', '-ar', str(SR), '-ac', '1', 'audio/voce44_t011.wav'], check=True)
w = wave.open('audio/voce44_t011.wav'); v = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(float) / 32768; v = np.pad(v, (0, max(0, N - len(v))))[:N]

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
# --- gancio: il tornado si mangia la casa
fx += wind(0.0, 3.0, 1.3, 60, 0.05) + wind(2.8, 18.9, 0.22, 110)
for k in range(14): tp_ = 0.8 + rng.uniform(0, 1.7); put(fx, tp_, burst(0.12, 6, 25) * rng.uniform(0.6, 1.3)); put(fx, tp_, tone(rng.uniform(140, 260), 90, 0.1, 25, 0.5) * 0.4)
put(fx, 0.9, sweep([200, 700], 1.6, 0.07)); thud(2.45, 0.9); put(fx, 2.6, sweep([130, 95, 70], 0.45, 0.45, 0.35, 34))          # rutto
put(fx, 0.2, sweep([500, 950, 800, 1000], 0.9, 0.08, 0.06, 18))
# --- team Pippo o team tornado
pop(3.35, 0.5); rasp(4.5, 0.7)
# --- polizia
for k, f in enumerate((941, 1209, 852)): put(fx, 6.45 + 0.17 * k, sweep([f, f], 0.11, 0.10))
fx += siren(7.85, 9.1); put(fx, 8.15, hiss(0.35, 4, 6) * 0.55); thud(8.4, 0.5); pop(8.47, 0.45)
whoosh(9.72, 0.5, 1.8); put(fx, 9.8, sweep([400, 1500], 1.2, 0.09)); put(fx, 10.0, sweep([300, 620], 0.4, 0.10, 0.03, 9)); laugh(10.5, 4, 0.14)
dundun(11.55, 0.4)
for k in range(5): click(12.3 + 0.13 * k, 600, 0.25)                                                                              # tic nervoso
for k, f in enumerate((697, 1336, 770, 1477)): put(fx, 13.65 + 0.15 * k, sweep([f, f], 0.10, 0.09))
put(fx, 14.5, hiss(0.5, 5, 6) * 0.2)
# --- arrivano in venti
fx += siren(15.7, 18.3, 0.05) + siren(15.8, 18.3, 0.04, 3.1, 700, 930) + siren(15.9, 18.3, 0.035, 2.2, 600, 800)
for k in range(5): put(fx, 15.85 + 0.07 * k, hiss(0.3, 4, 7) * 0.4); thud(16.25 + 0.07 * k, 0.35)
for k in range(19): put(fx, 15.95 + 0.035 * k, tone(500 + 30 * k, 800 + 30 * k, 0.06, 30, 0.2) * 0.14)
for k in range(22): step(17.0 + 0.032 * k, 0.4, 140 + 15 * (k % 3))
click(18.2, 2400, 0.7); click(18.28, 2100, 0.7); clang(18.22, 0.5); put(fx, 18.3, sweep([900, 500, 300], 0.5, 0.12, 0.05, 12))
# --- foto segnaletica
fx += wind(18.9, 21.5, 0.25, 30, 0.1, 0.1) * (1 + 0.5 * np.sin(2 * np.pi * 7 * t)); shutter(19.5); shutter(20.55)
for k in range(8): put(fx, 20.1 + 0.14 * k, tone(700 + 80 * (k % 2), 500, 0.05, 40, 0.2) * 0.15)
# --- il processo
fx += lp(rng.normal(0, 1, N), 90) * env(21.5, 23.4, 0.2, 0.3) * 1.0
for bt in (21.6, 21.85): put(fx, bt, tone(240, 180, 0.08, 30, 0.5) * 0.6)
put(fx, 23.65, sweep([420, 520, 470], 0.2, 0.14, 0.05, 20)); put(fx, 23.95, sweep([430, 640], 0.3, 0.14, 0.05, 20))               # "come si dichiara?"
fx += wind(24.85, 26.9, 1.5, 45, 0.15, 0.3); put(fx, 25.25, sweep([500, 1400, 1100, 1600], 1.2, 0.12, 0.08, 22)); whoosh(25.2, 0.6, 2.0)
put(fx, 26.9, sweep([1500, 400], 0.2, 0.1)); thud(27.12, 1.0)
for bt in (27.37, 28.22): put(fx, bt, tone(260, 170, 0.1, 25, 0.6) * 0.9); put(fx, bt, burst(0.05, 4, 40) * 0.8)
put(fx, 27.45, sweep([600, 1300, 900], 0.5, 0.10, 0.08, 20))
# --- in cella
put(fx, 29.05, sweep([900, 200], 0.15, 0.12)); thud(29.2, 1.1); clang(29.2, 0.9); clang(29.29, 0.4)
fx += wind(29.3, 32.6, 0.2, 25, 0.2, 0.2)
for k, f in enumerate((392, 370, 349, 262)): put(fx, 30.5 + 0.22 * k, sweep([f, f * 0.97], 0.26 if k < 3 else 0.5, 0.08, 0.03, 6))
whoosh(31.52, 0.45, 1.6); put(fx, 31.6, sweep([400, 1300], 0.8, 0.08))
# --- prossimo episodio: il terremoto
for k, f in enumerate((941, 1209, 852)): put(fx, 32.75 + 0.15 * k, sweep([f, f], 0.10, 0.08))
fx += (lp(rng.normal(0, 1, N), 200) * 9.0 + np.sin(2 * np.pi * 38 * t) * 0.25) * np.interp(t, [33.25, 33.5, 35.3, 35.6], [0, 1, 1, 0]) * (1 + 0.4 * np.sin(2 * np.pi * 11 * t))
put(fx, 33.35, burst(0.5, 5, 6) * 1.6)
for k in range(10): put(fx, 33.5 + rng.uniform(0, 1.9), tone(rng.uniform(150, 300), 90, 0.08, 25, 0.5) * 0.35)
# --- team Pippo o team tornado?
dundun(35.7, 0.4); rasp(36.9, 0.6)
for k, f in enumerate((196, 131)): put(fx, 37.4 + 0.3 * k, tone(f * 2, f * 2, 0.6, 5, 0.5) * 0.2)
fx = np.tanh(fx * 1.1) * 0.45
# --- taglio: via l'invito a commentare dopo il gancio (2.95-6.2 s), resta solo quello finale
CA, CB = 2.95, 6.2
def cut(x):
    i0, i1 = int(CA * SR), int(CB * SR); k = int(0.02 * SR); y0 = x[:i0].copy(); y1 = x[i1:].copy(); y0[-k:] *= np.linspace(1, 0, k); y1[:k] *= np.linspace(0, 1, k); return np.concatenate([y0, y1])
v = cut(v); fx = cut(fx); N = len(v); DUR = N / SR; t = np.arange(N) / SR

bpm = 124; beat = 60 / bpm; chords = [(130.81, 155.56, 196.0), (103.83, 130.81, 155.56), (116.54, 146.83, 174.61), (98.0, 123.47, 146.83)]
m = np.zeros(N)
def pluck(f, t0, dur=0.5, amp=0.5):
    n = int(dur * SR); tt = np.arange(n) / SR; put(m, t0, amp * (np.sin(2 * np.pi * f * tt) + 0.4 * np.sin(4 * np.pi * f * tt) + 0.2 * np.sin(6 * np.pi * f * tt)) * np.exp(-tt * 7))
for bar in range(int(DUR / (beat * 4)) + 1):
    ch = chords[bar % 4]
    for b in range(8):
        t0 = bar * beat * 4 + b * beat / 2; f = ch[[0, 2, 1, 2, 0, 1, 2, 1][b]] * 2
        pluck(f, t0, 0.4, 0.30 if b % 2 == 0 else 0.22)
    pluck(ch[0] / 2, bar * beat * 4, 0.9, 0.5); pluck(ch[0] / 2, bar * beat * 4 + 1.5 * beat, 0.5, 0.35); pluck(ch[0] / 2, bar * beat * 4 + 2.5 * beat, 0.9, 0.4); pluck(ch[2] / 2, bar * beat * 4 + 3 * beat, 0.5, 0.3)
mus = m / np.abs(m).max() * 0.11
mus *= np.interp(t, [0, 0.8, DUR - 1.1, DUR - 0.8, DUR], [0.6, 1, 1, 0.35, 0.0])
mix = v * 1.0 + mus + fx
mix = np.clip(mix / max(1, np.abs(mix).max() / 0.95), -1, 1)
mix[-int(0.15 * SR):] *= np.linspace(1, 0, int(0.15 * SR))
st = np.stack([mix, mix], 1); pcm = (st * 32767).astype(np.int16)
with wave.open('audio/t011.wav', 'wb') as o:
    o.setnchannels(2); o.setsampwidth(2); o.setframerate(SR); o.writeframes(pcm.tobytes())
print('audio ok', np.abs(v).max(), np.abs(mus).max(), np.abs(fx).max())
