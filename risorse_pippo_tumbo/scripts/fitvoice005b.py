"""Test 005b - adatta la nuova voce (sboccata) ai tempi delle scene gia' animate: taglia per frasi, accelera leggermente, riposiziona.
Esce audio/voce_fit_t005b.wav (44.1 kHz mono, 46 s) e audio/words_fit_t005b.json (tempi delle parole nel video)."""
import json, wave, subprocess, numpy as np, os
SR = 44100; DUR = 46.0; N = int(DUR * SR)
W = json.load(open('audio/words_t005b.json')); assert len(W) == 125, len(W)
subprocess.run(['/usr/local/bin/ffmpeg', '-y', '-loglevel', 'error', '-i', 'audio/voce_t005b.mp3', '-ar', str(SR), '-ac', '1', 'audio/voce44_t005b.wav'], check=True)
w = wave.open('audio/voce44_t005b.wav'); src = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
# (numero parole, inizio desiderato nel video, velocita')
CH = [(6, 0.0, 1.10), (3, 1.95, 1.10), (10, 3.6, 1.08), (6, 6.75, 1.08), (4, 8.45, 1.14), (1, 9.85, 1.0), (1, 10.55, 1.0), (1, 11.1, 1.05), (2, 12.1, 1.0),
      (7, 13.2, 1.08), (5, 15.9, 1.05), (6, 18.0, 1.05), (8, 20.7, 1.08), (6, 23.0, 1.10), (3, 25.06, 1.10), (2, 26.2, 1.10), (4, 26.85, 1.10), (3, 28.1, 1.10), (4, 29.3, 1.10),
      (4, 31.1, 1.12), (4, 32.7, 1.12), (7, 34.3, 1.15), (3, 35.8, 1.15), (6, 36.9, 1.15), (2, 38.2, 1.12), (2, 39.3, 1.12), (2, 40.45, 1.12), (4, 41.9, 1.10), (9, 43.4, 1.10)]
assert sum(c[0] for c in CH) == 125
out = np.zeros(N, np.float32); fit = []; i = 0; prev_end = 0.0; os.makedirs('audio/tmp', exist_ok=True)
for k, (n, tgt, tempo) in enumerate(CH):
    a = W[i][0]; b = W[i + n - 1][1]
    s0 = max(a - 0.04, W[i - 1][1] + 0.01 if i > 0 else 0.0); s1 = min(b + 0.10, W[i + n][0] - 0.02 if i + n < len(W) else len(src) / SR)
    seg = src[int(s0 * SR):int(s1 * SR)].copy(); f = int(0.012 * SR); seg[:f] *= np.linspace(0, 1, f); seg[-f:] *= np.linspace(1, 0, f)
    fa = 'audio/tmp/c%02d.wav' % k; fb = 'audio/tmp/c%02d_t.wav' % k
    with wave.open(fa, 'wb') as o: o.setnchannels(1); o.setsampwidth(2); o.setframerate(SR); o.writeframes((seg * 32767).astype(np.int16).tobytes())
    subprocess.run(['/usr/local/bin/ffmpeg', '-y', '-loglevel', 'error', '-i', fa, '-filter:a', 'atempo=%.3f' % tempo, fb], check=True)
    ww = wave.open(fb); x = np.frombuffer(ww.readframes(ww.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    st = max(tgt, prev_end + 0.02); j0 = int(st * SR); m = min(len(x), N - j0); out[j0:j0 + m] += x[:m]; prev_end = st + len(x) / SR
    for q in range(i, i + n): fit.append([round(st + (W[q][0] - s0) / tempo, 2), round(st + (W[q][1] - s0) / tempo, 2), W[q][2]])
    print('%2d %5.2f->%5.2f (voluto %5.2f) x%.2f  %s' % (k, st, prev_end, tgt, tempo, ' '.join(x_[2] for x_ in W[i:i + n])))
    i += n
with wave.open('audio/voce_fit_t005b.wav', 'wb') as o: o.setnchannels(1); o.setsampwidth(2); o.setframerate(SR); o.writeframes((np.clip(out, -1, 1) * 32767).astype(np.int16).tobytes())
json.dump(fit, open('audio/words_fit_t005b.json', 'w'), ensure_ascii=False)
