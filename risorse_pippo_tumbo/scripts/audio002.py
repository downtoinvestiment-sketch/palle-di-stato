"""Audio procedurale Test 002 -> ../audio/t002.wav (44.1k stereo). Rimbalzi sincronizzati con hits_t/hits_v/hits_p."""
import numpy as np, os, wave
import story002 as S
from params002 import *
SR = 44100; DUR = 12.0
d = np.load(os.path.join(os.path.dirname(__file__), '..', 'cache', 'balls.npz'))
L = np.zeros(int(SR * DUR)); R = np.zeros_like(L)
rng = np.random.default_rng(7)
def add(sig, t0, pan=0.0, g=1.0):
    i = int(t0 * SR)
    if i < 0 or i >= len(L): return
    n = min(len(sig), len(L) - i)
    L[i:i + n] += sig[:n] * g * (1 - pan) * 0.5 * 2 ** 0.5 / 1.4
    R[i:i + n] += sig[:n] * g * (1 + pan) * 0.5 * 2 ** 0.5 / 1.4
def tone(f, dur, decay, kind='sine'):
    t = np.arange(int(SR * dur)) / SR
    w = np.sin(2 * np.pi * f * t) if kind == 'sine' else 2 * ((f * t) % 1) - 1
    return w * np.exp(-t * decay)
# --- musica: 120 bpm, basso + arpeggio + hat ---------------------------------------------
bpm = 120; beat = 60 / bpm
scale = [0, 2, 4, 7, 9, 12, 14, 16]
root = 110.0
def kick(t0):
    t = np.arange(int(SR * 0.25)) / SR
    f = 50 + 110 * np.exp(-t * 28); ph = 2 * np.pi * np.cumsum(f) / SR
    add(np.sin(ph) * np.exp(-t * 9), t0, 0, 0.55)
def hat(t0, g=0.12):
    t = np.arange(int(SR * 0.05)) / SR
    n = rng.standard_normal(len(t)); n = np.diff(n, prepend=0)
    add(n * np.exp(-t * 90), t0, rng.uniform(-.3, .3), g)
def pluck(f, t0, g=0.14, pan=0.0):
    add((tone(f, 0.35, 9) + 0.4 * tone(2 * f, 0.35, 12) + 0.25 * tone(f * 1.005, 0.35, 9, 'saw')) , t0, pan, g)
for b in range(int(DUR / beat)):
    t0 = 1.0 + b * beat * 0.5 if False else b * beat * 0.5
    if t0 < 0.5: continue
    step = b
    if step % 2 == 0 and t0 >= 2.0: kick(t0)
    if t0 >= 2.0: hat(t0 + beat * 0.25)
    if t0 >= 2.0:
        deg = [0, 4, 7, 12, 7, 4, 9, 12][step % 8] + (0 if (step // 8) % 2 == 0 else 5)
        pluck(root * 2 * 2 ** (deg / 12), t0, 0.10, (-1) ** step * 0.35)
    if step % 4 == 0 and t0 >= 2.0:
        add(tone(root / 2 * 2 ** (((step // 4) % 4 in (1, 3)) * 5 / 12), 0.9, 2.2, 'sine') * 0.5, t0, 0, 0.5)
# riser nella cascata (5-8s)
t = np.arange(int(SR * 3.0)) / SR
add(np.sin(2 * np.pi * (300 + 700 * t / 3) * t) * (t / 3) ** 2 * 0.12, 5.0, 0, 1)
# --- click iniziale: mano rilascia la pallina a t=0.9 ----------------------------------------
t = np.arange(int(SR * 0.04)) / SR
add(np.sin(2 * np.pi * 1800 * t) * np.exp(-t * 160), 0.88, 0, 0.6)
# pallina che cade e rotola (0.9-4.6 s): tick sulla rampa + rombo sottile
t = np.arange(int(SR * 4.0)) / SR
roll = np.convolve(rng.standard_normal(len(t)), np.ones(60) / 60, 'same') * np.clip((t - 0.6) / 1.5, 0, 1) * 0.5
add(roll * 0.35, 1.0, 0.0, 1.0)
# --- rimbalzi/impatti dai dati di simulazione ----------------------------------------------
ht, hv, hp = d['hits_t'], d['hits_v'], d['hits_p']
cxy = np.array(POOL_C)
def bounce(v, pitch):
    f = pitch; dur = 0.18
    t = np.arange(int(SR * dur)) / SR
    return (np.sin(2 * np.pi * f * t * (1 + 0.15 * np.exp(-t * 40))) + 0.3 * np.sin(2 * np.pi * 2.4 * f * t)) * np.exp(-t * 28)
last = {}
order = np.argsort(ht)
penta = [523.25, 587.33, 659.25, 783.99, 880.0, 1046.5]
for k in order:
    t0, v, p = ht[k], hv[k], hp[k]
    key = int(t0 * 60)
    last[key] = last.get(key, 0) + 1
    if last[key] > 2: continue                       # limita la densità
    g = min(1.0, v / 6.0) ** 0.8 * 0.22
    pan = float(np.clip((p[0] - cxy[0]) / 1.5, -1, 1))
    add(bounce(v, penta[int(abs(p[0] * 7 + p[1] * 3 + t0 * 5)) % 6] * (0.5 + 0.1 * min(v, 4))), t0, pan, g)
# --- tuffi: splash di Tumbo (8.9 s) e Pippo (10.8 s) ----------------------------------------------
def splash(t0, g, dur=0.9):
    t = np.arange(int(SR * dur)) / SR
    n = rng.standard_normal(len(t))
    lp = np.convolve(n, np.ones(8) / 8, 'same')
    add(lp * np.exp(-t * 4.5) * g + np.sin(2 * np.pi * 90 * t) * np.exp(-t * 9) * g * 0.8, t0, 0, 1)
splash(S.TUM_JUMP + S.TUM_FLIGHT, 0.45, 0.8); splash(S.PIP_JUMP + S.PIP_FLIGHT, 0.7, 1.2)
# --- finale: accordo morbido -------------------------------------------------------------------
for k, fq in enumerate((261.6, 329.6, 392.0, 523.3)):
    t = np.arange(int(SR * 1.4)) / SR
    add(np.sin(2 * np.pi * fq * t) * np.exp(-t * 2.2) * 0.12, 11.0 + k * 0.04, (k - 1.5) * 0.3, 1)
# master
m = max(np.abs(L).max(), np.abs(R).max()); L, R = L / m * 0.85, R / m * 0.85
fade = np.ones_like(L); n = int(SR * 0.3); fade[-n:] = np.linspace(1, 0, n); L *= fade; R *= fade
os.makedirs(os.path.join(os.path.dirname(__file__), '..', 'audio'), exist_ok=True)
out = os.path.join(os.path.dirname(__file__), '..', 'audio', 't002.wav')
x = (np.stack([L, R], 1) * 32767).astype('<i2')
with wave.open(out, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(x.tobytes())
print('audio ok', out, len(L) / SR, 's  hits usati:', sum(min(2, v) for v in last.values()))
