"""Analisi di una canzone: tempo (BPM), fase delle battute, inizio e fine,
profilo di volume. Uso: python scripts/analisi_canzone.py file.wav [bpm_min bpm_max]
Scrive accanto al file un .json con i risultati."""
import sys, json, subprocess
import numpy as np

SR = 22050


def carica(path):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-ac', '1', '-ar', str(SR),
                          '-f', 'f32le', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).astype(np.float64)


def inviluppo(x, hop=256, n=1024):
    """Flusso spettrale (novita') campionato a SR/hop."""
    w = np.hanning(n)
    k = 1 + (len(x) - n) // hop
    idx = np.arange(n)[None, :] + hop * np.arange(k)[:, None]
    S = np.abs(np.fft.rfft(x[idx] * w, axis=1))
    S = np.log1p(200 * S)
    d = np.diff(S, axis=0)
    d[d < 0] = 0
    f = d.sum(axis=1)
    f = f - np.convolve(f, np.ones(43) / 43, mode='same')
    f[f < 0] = 0
    return f, SR / hop


def tempo(f, fr, lo=70, hi=180):
    f0 = f - f.mean()
    ac = np.correlate(f0, f0, mode='full')[len(f0) - 1:]
    ris = []
    for bpm in np.arange(lo, hi + 0.01, 0.1):
        lag = 60.0 / bpm * fr
        v = 0.0
        for m, p in ((1, 1.0), (2, 0.8), (4, 0.6), (0.5, 0.3)):
            L = lag * m
            i = int(L)
            if i + 1 >= len(ac):
                continue
            v += p * (ac[i] * (1 - (L - i)) + ac[i + 1] * (L - i))
        ris.append((v, bpm))
    ris.sort(reverse=True)
    return ris


def fase(f, fr, bpm):
    per = 60.0 / bpm * fr
    best = (-1, 0)
    for k in range(200):
        ph = per * k / 200
        t = np.arange(ph, len(f) - 1, per)
        i = t.astype(int)
        v = (f[i] * (1 - (t - i)) + f[i + 1] * (t - i)).mean()
        if v > best[0]:
            best = (v, ph)
    return best[1] / fr


if __name__ == '__main__':
    path = sys.argv[1]
    lo = float(sys.argv[2]) if len(sys.argv) > 2 else 70
    hi = float(sys.argv[3]) if len(sys.argv) > 3 else 180
    x = carica(path)
    dur = len(x) / SR
    # volume a finestre di 50 ms
    h = int(SR * 0.05)
    rms = np.sqrt(np.mean(x[:len(x) // h * h].reshape(-1, h) ** 2, axis=1))
    db = 20 * np.log10(rms + 1e-9)
    sopra = np.where(db > db.max() - 35)[0]
    t0, t1 = sopra[0] * 0.05, (sopra[-1] + 1) * 0.05
    f, fr = inviluppo(x)
    ris = tempo(f, fr, lo, hi)
    bpm = ris[0][1]
    # raffina il BPM intorno al massimo con passo fine
    ph = fase(f, fr, bpm)
    visti, cand = [], []
    for v, b in ris:
        if all(abs(b - c) > 3 for c in visti):
            visti.append(b); cand.append((round(b, 1), round(v / ris[0][0], 3)))
        if len(cand) == 5:
            break
    out = dict(file=path, durata=round(dur, 3), inizio=round(t0, 2), fine=round(t1, 2),
               bpm=round(float(bpm), 1), prima_battuta=round(float(ph), 3), candidati=cand,
               volume_db=[round(float(v), 1) for v in db])
    json.dump(out, open(path.rsplit('.', 1)[0] + '_analisi.json', 'w'))
    print({k: v for k, v in out.items() if k != 'volume_db'})
    # profilo a secondi
    sec = [round(float(np.mean(db[i:i + 20])), 1) for i in range(0, len(db), 20)]
    print('dB al secondo:', sec)
