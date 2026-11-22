"""Test 012 (Pippo e la zucchina Eleonora) - audio: voce + musichetta sintetica + effetti. Esce audio/t012.wav (40.6 s)"""
import numpy as np, subprocess, wave
SR = 44100; DUR = 40.6; N = int(DUR * SR); rng = np.random.default_rng(12)
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
subprocess.run(['/usr/local/bin/ffmpeg', '-y', '-loglevel', 'error', '-i', 'audio/voce_t012.mp3', '-ar', str(SR), '-ac', '1', 'audio/voce44_t012.wav'], check=True)
w = wave.open('audio/voce44_t012.wav'); v = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(float) / 32768; v = np.pad(v, (0, max(0, N - len(v))))[:N]

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
# --- gancio: innamorato
for k in range(12): chime(0.05 + 0.13 * k, k, 0.06)
put(fx, 0.1, sweep([500, 800, 1100, 1500], 1.6, 0.03)); dundun(0.85, 0.3)
put(fx, 4.1, hiss(0.25, 6, 8) * 0.7); put(fx, 4.12, sweep([900, 300], 0.22, 0.12))                                      # disco che si ferma
fx += saw([4.3, 9.6], [190, 190], 8) * (1 + 0.5 * np.sin(2 * np.pi * 31 * t)) * env(4.3, 9.5, 0.2, 0.2) * 0.012 * (1 + np.sin(2 * np.pi * 0.8 * t))   # mosca
# --- la rosa
pop(6.25, 0.4); chime(6.35, 2, 0.08); chime(6.5, 3, 0.07)
cr = np.zeros(N)
for k in range(8):
    for j in range(3): put(cr, 8.3 + 0.14 * k + 0.035 * j, tone(4300, 4300, 0.025, 60, 0.1) * 0.05)
fx += cr; put(fx, 9.05, tone(1500, 1200, 0.03, 60, 0.2) * 0.2)
for k in range(5): put(fx, 11.5 + 0.16 * k, sweep([420 + 60 * (k % 2), 620 + 60 * (k % 2)], 0.1, 0.13, 0.06, 30))         # uh uh ah ah
thud(9.75, 0.4)
# --- l'idea e la bomba
put(fx, 13.2, tone(1568, 1568, 0.9, 4, 0.3) * 0.2); put(fx, 13.2, tone(2093, 2093, 0.9, 4, 0.2) * 0.12); laugh(13.5, 5, 0.14)
for k in range(9): clang(15.0 + 0.36 * k + 0.05 * np.sin(k * 2.2), 0.28)
for tp in (17.55, 17.77, 17.99): put(fx, tp, hiss(0.2, 3, 10) * 0.8 * np.linspace(0.3, 1, int(0.2 * SR))); put(fx, tp, sweep([500, 1400], 0.18, 0.06))
thud(18.85, 0.9); put(fx, 18.9, sweep([500, 1700], 0.6, 0.09)); put(fx, 19.5, sweep([1700, 350], 0.6, 0.10)); thud(20.1, 0.9)
chime(20.6, 1, 0.1); chime(20.75, 3, 0.1)
# --- tre, due, uno
for k, tp in enumerate((21.9, 22.84, 23.68)): blip(tp, 700 + 180 * k, 0.16, 0.16)
for k in range(17): click(21.95 + 0.125 * k * (1 - 0.012 * k), 1100, 0.18)
put(fx, 23.4, sweep([300, 700], 0.5, 0.10, 0.05, 14))
# --- BOOM
boom = lp(rng.normal(0, 1, N), 160) * np.interp(t, [23.98, 24.02, 24.5, 27.5], [0, 16, 9, 0]) + np.sin(2 * np.pi * 34 * t) * np.interp(t, [23.98, 24.02, 26.5], [0, 0.9, 0]) + lp(rng.normal(0, 1, N), 12) * np.interp(t, [23.98, 24.02, 24.6], [0, 1.6, 0])
fx += boom
fx += (lp(rng.normal(0, 1, N), 400) * 14.0 + np.sin(2 * np.pi * 27 * t) * 0.35) * np.interp(t, [24.0, 24.3, 27.0, 31.0], [0, 1, 0.45, 0.0])               # rombo lungo che si allontana
fx += lp(rng.normal(0, 1, N), 70) * np.interp(t, [24.1, 24.5, 26.0, 28.0], [0, 2.0, 0.8, 0.0])                                                # vento dell'onda d'urto
crk = np.zeros(N)
for k in range(260): tp = 24.4 + rng.uniform(0, 16.0); put(crk, tp, burst(0.015, 2, 90) * rng.uniform(0.2, 0.7))                               # fuochi che scoppiettano
for k in range(70): tp = 25.0 + rng.uniform(0, 15.3); put(crk, tp, tone(2600, 2600, 0.008, 200, 0.1) * 0.25)                                    # contatore geiger
fx += crk * 0.5
for k in range(16): tp = 24.9 + rng.uniform(0, 2.4); put(fx, tp, tone(rng.uniform(120, 240), 80, 0.09, 25, 0.5) * 0.3)                # piovono verdure
put(fx, 24.45, sweep([1200, 1000, 1150], 0.6, 0.05))
# --- la zucchina si alza
put(fx, 25.45, sweep([300, 1100], 0.9, 0.09)); pop(27.0, 0.6); chime(27.05, 2, 0.08); pop(28.3, 0.6); pop(29.2, 0.6); pop(29.32, 0.5)
for k in range(10): chime(30.1 + 0.1 * k, k, 0.07)
put(fx, 30.15, sweep([700, 1200, 1600], 0.5, 0.06))
# --- sposi in moto
for k in range(6): bell(31.3 + 0.36 * k, 0.09 if k % 2 else 0.12)
fx += saw([31.7, 40.6], [78, 96], 9) * (0.6 + 0.4 * (np.sin(2 * np.pi * 13 * t) > 0)) * np.interp(t, [31.6, 31.9, 39.9, 40.6], [0, 0.05, 0.05, 0])
organ(33.45, (261.6, 329.6, 392.0), 0.5); organ(34.0, (349.2, 440.0, 523.3), 0.6)
organ(35.05, (261.6, 329.6, 392.0), 0.45); organ(35.6, (293.7, 370.0, 440.0), 0.45); organ(36.1, (392.0, 493.9, 587.3), 0.6)
for tp in (36.94, 37.14):
    i0, i1 = int(tp * SR), int((tp + 0.34) * SR); fx[i0:i1] += saw([tp, tp + 0.34], [70, 150], 5)[i0:i1] * 0.16 * np.hanning(i1 - i0)
for k in range(40): tp = 31.8 + rng.uniform(0, 8.4); put(fx, tp, tone(rng.uniform(1800, 3200), 1500, 0.03, 70, 0.2) * 0.07)        # barattoli
for k, f in enumerate((262, 330, 392, 523)): put(fx, 39.65 + 0.12 * k, tone(f * 2, f * 2, 0.6, 5, 0.5) * 0.14)
fx = np.tanh(fx * 1.1) * 0.45

# musichetta diversa dal solito: marimba saltellante in maggiore, 132 bpm
bpm = 132; beat = 60 / bpm; chords = [(261.63, 329.63, 392.0), (220.0, 261.63, 329.63), (174.61, 220.0, 261.63), (196.0, 246.94, 293.66)]
m = np.zeros(N)
def mar(f, t0, dur=0.35, amp=0.5):
    n = int(dur * SR); tt = np.arange(n) / SR; put(m, t0, amp * (np.sin(2 * np.pi * f * tt) + 0.25 * np.sin(2 * np.pi * 4 * f * tt) * np.exp(-tt * 30)) * np.exp(-tt * 11))
pat = [0, None, 2, 1, None, 2, 0, 2]
for bar in range(int(DUR / (beat * 4)) + 1):
    ch = chords[bar % 4]
    for b in range(8):
        if pat[b] is None: continue
        mar(ch[pat[b]] * 2, bar * beat * 4 + b * beat / 2, 0.35, 0.3)
    for b in (1, 3):
        for f in ch: mar(f, bar * beat * 4 + b * beat, 0.25, 0.12)
    mar(ch[0] / 2, bar * beat * 4, 0.6, 0.5); mar(ch[2] / 4 * 2, bar * beat * 4 + 2 * beat, 0.6, 0.4)
mus = m / np.abs(m).max() * 0.12
mus *= np.interp(t, [0, 0.8, 23.6, 24.0, 25.3, 25.8, DUR - 1.1, DUR - 0.8, DUR], [0.6, 1, 1, 0.0, 0.0, 1, 1, 0.35, 0.0])
mix = v * 1.0 + mus + fx
mix = np.clip(mix / max(1, np.abs(mix).max() / 0.95), -1, 1)
mix[-int(0.15 * SR):] *= np.linspace(1, 0, int(0.15 * SR))
st = np.stack([mix, mix], 1); pcm = (st * 32767).astype(np.int16)
with wave.open('audio/t012.wav', 'wb') as o:
    o.setnchannels(2); o.setsampwidth(2); o.setframerate(SR); o.writeframes(pcm.tobytes())
print('audio ok', np.abs(v).max(), np.abs(mus).max(), np.abs(fx).max())
