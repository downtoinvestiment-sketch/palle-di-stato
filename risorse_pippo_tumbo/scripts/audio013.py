"""Test 013 (Pippo e Tumbo in aereo) - audio: voce + musichetta sintetica + effetti. Esce audio/t013.wav (46.0 s)"""
import numpy as np, subprocess, wave
SR = 44100; DUR = 46.0; N = int(DUR * SR); rng = np.random.default_rng(13)
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
subprocess.run(['/usr/local/bin/ffmpeg', '-y', '-loglevel', 'error', '-i', 'audio/voce_t013.mp3', '-ar', str(SR), '-ac', '1', 'audio/voce44_t013.wav'], check=True)
w = wave.open('audio/voce44_t013.wav'); v = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(float) / 32768; v = np.pad(v, (0, max(0, N - len(v))))[:N]

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
# --- aeroporto
fx += lp(rng.normal(0, 1, N), 40) * env(0.0, 6.1, 0.3, 0.3) * 0.35                                      # brusio di pista
put(fx, 0.3, sweep([600, 900, 750], 0.4, 0.06)); put(fx, 0.75, sweep([750, 950], 0.4, 0.06))            # ding-dong aeroporto
for k in range(9): step(0.2 + 0.5 * k, 0.3, 160)
for k in range(18): put(fx, 0.2 + 0.25 * k, burst(0.03, 3, 60) * 0.18)                                    # rotelle della valigia
# --- decollo
fx += (saw([6.1, 7.55], [80, 200], 10) * 0.05 + lp(rng.normal(0, 1, N), 25) * 0.5) * env(5.9, 7.7, 0.4, 0.2)
whoosh(6.9, 0.8, 0.9)
# --- motori in volo (rumore di fondo) sulle scene interne
hum = (lp(rng.normal(0, 1, N), 160) * 0.55 + np.sin(2 * np.pi * 62 * t) * 0.012) * np.interp(t, [7.5, 7.8, 42.2, 42.5], [0, 1, 1, 0])
fx += hum * (1 - 0.6 * env(31.4, 36.5, 0.05, 0.05))
# --- il pilota e il gelato
for k in range(9): put(fx, 8.2 + 0.52 * k, sweep([300, 500], 0.18, 0.12, 0.1, 30))                       # leccate
gurgle(12.15, 1.1, 0.5); put(fx, 12.6, sweep([700, 300], 0.4, 0.1, 0.1, 18))
for k in range(9): step(13.4 + 0.13 * k, 0.4, 170)
thud(14.6, 0.6); put(fx, 14.65, tone(900, 900, 0.05, 50, 0.3) * 0.2)                                     # porta e chiavistello
# --- ai comandi
pop(15.2, 0.4); pop(15.45, 0.35); click(18.6, 1400, 0.5)
# --- karaoke: musichetta disco
kb_ = np.zeros(N); bpmk = 124; bk = 60 / bpmk
for k in range(int((29.95 - 18.85) / (bk / 2))):
    tp = 18.85 + k * bk / 2
    if k % 2 == 0: put(kb_, tp, tone(60, 40, 0.18, 18, 0.6) * 0.7)
    else: put(kb_, tp, hiss(0.06, 3, 50) * 0.45)
    f = [220, 277, 330, 277, 247, 311, 370, 311][(k // 2) % 8]; put(kb_, tp, sweep([f, f], 0.2, 0.08))
fx += kb_ * np.interp(t, [18.85, 19.0, 24.5, 24.6, 26.5, 26.6, 29.8, 29.95], [0, 1, 1, 0.45, 0.45, 0.8, 0.8, 0])
# --- Tumbo mangia il carrello
for k in range(14): tp = 20.9 + 0.2 * k; put(fx, tp, burst(0.07, 3, 30) * 0.9); put(fx, tp, tone(2400, 1600, 0.04, 50, 0.2) * 0.15)
put(fx, 23.9, sweep([180, 120, 90], 0.6, 0.45, 0.35, 32))                                                 # rutto
# --- annuncio
put(fx, 24.75, tone(1046, 1046, 0.35, 5, 0.3) * 0.12); put(fx, 25.0, tone(784, 784, 0.45, 5, 0.3) * 0.12)
for k in range(10): put(fx, 26.8 + 0.27 * k, sweep([400 + 60 * (k % 3), 900, 600], 0.25, 0.07, 0.15, 25))  # passeggeri che urlano
# --- telefono
ring(30.0, 3, 0.14)
# --- ospedale
for k in range(6): put(fx, 31.5 + 0.8 * k, tone(1000, 1000, 0.08, 20, 0.2) * 0.12)                       # bip del monitor
for k in range(5): put(fx, 33.7 + 0.5 * k, tone(1000, 1000, 0.06, 20, 0.2) * 0.12)
# --- guardano il manuale
dundun(36.6, 0.3); put(fx, 39.6, sweep([300, 400], 0.25, 0.08)); laugh(39.9, 3, 0.12)
click(41.5, 700, 0.6); put(fx, 41.55, tone(200, 120, 0.2, 12, 0.5) * 0.4)
# --- finale
fx += (saw([42.4, 46.0], [140, 110], 10) * 0.035 + lp(rng.normal(0, 1, N), 30) * 0.22) * env(42.35, 46.0, 0.1, 0.5)
whoosh(42.4, 1.0, 0.8)
for k, f in enumerate((392, 494, 587, 784)): put(fx, 44.3 + 0.18 * k, tone(f, f, 0.8, 3.0, 0.5) * 0.1)
fx = np.tanh(fx * 1.1) * 0.45

# musichetta: ukulele/marimba estiva, 120 bpm
bpm = 120; beat = 60 / bpm; chords = [(261.63, 329.63, 392.0), (293.66, 349.23, 440.0), (196.0, 246.94, 293.66), (261.63, 329.63, 392.0)]
m = np.zeros(N)
def mar(f, t0, dur=0.35, amp=0.5):
    n = int(dur * SR); tt = np.arange(n) / SR; put(m, t0, amp * (np.sin(2 * np.pi * f * tt) + 0.35 * np.sin(2 * np.pi * 2 * f * tt) * np.exp(-tt * 20)) * np.exp(-tt * 9))
pat = [0, 2, 1, 2, 0, 2, 1, 2]
for bar in range(int(DUR / (beat * 4)) + 1):
    ch = chords[bar % 4]
    for b in range(8):
        if b in (3, 7) and bar % 2: continue
        mar(ch[pat[b]] * 2, bar * beat * 4 + b * beat / 2, 0.3, 0.28)
    mar(ch[0] / 2, bar * beat * 4, 0.6, 0.45); mar(ch[1] / 2, bar * beat * 4 + 2 * beat, 0.6, 0.35)
mus = m / np.abs(m).max() * 0.11
mus *= np.interp(t, [0, 0.8, 18.8, 18.95, 29.9, 30.1, 31.3, 31.5, 36.4, 36.6, DUR - 1.1, DUR - 0.8, DUR], [0.6, 1, 1, 0.0, 0.0, 1, 1, 0.3, 0.3, 1, 1, 0.35, 0.0])
mix = v * 1.0 + mus + fx
mix = np.clip(mix / max(1, np.abs(mix).max() / 0.95), -1, 1)
mix[-int(0.15 * SR):] *= np.linspace(1, 0, int(0.15 * SR))
st = np.stack([mix, mix], 1); pcm = (st * 32767).astype(np.int16)
with wave.open('audio/t013.wav', 'wb') as o:
    o.setnchannels(2); o.setsampwidth(2); o.setframerate(SR); o.writeframes(pcm.tobytes())
print('audio ok', np.abs(v).max(), np.abs(mus).max(), np.abs(fx).max())
