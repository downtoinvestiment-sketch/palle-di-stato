#!/usr/bin/env python3
"""Bozze della firma sonora di Pippo e Tumbo (vedi CANZONE_PIPPO.md).

Usa la voce vera del narratore: le parole vengono tagliate dai file
audio/voce_tNNN.mp3 con i tempi di audio/words_tNNN.json, poi alzate o
abbassate di tono. Niente generatori, niente spesa.

Uso:  python scripts/firma_sonora.py
Esce: audio/firma/firma_v0, micro_v0, ritmo_v0 (.wav e .mp3)
"""
import json
import os
import re
import subprocess
import wave

import numpy as np

SR = 44100
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = os.path.join(R, 'audio')
OUT = os.path.join(A, 'firma')


def dec(path, ss=None, to=None, af=None):
    cmd = ['ffmpeg', '-v', 'error']
    if ss is not None:
        cmd += ['-ss', f'{ss:.3f}']
    if to is not None:
        cmd += ['-to', f'{to:.3f}']
    cmd += ['-i', path]
    if af:
        cmd += ['-af', af]
    cmd += ['-ac', '1', '-ar', str(SR), '-f', 'f32le', '-']
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).copy()


def fade(x, a=0.006, r=0.02):
    x = x.copy()
    n1, n2 = int(a * SR), int(r * SR)
    if len(x) > n1:
        x[:n1] *= np.linspace(0, 1, n1)
    if len(x) > n2:
        x[-n2:] *= np.linspace(1, 0, n2)
    return x


def norm(x, peak=0.9):
    m = float(np.max(np.abs(x))) if len(x) else 0.0
    return x * (peak / m) if m > 0 else x


def voce(n, ss, to, semitoni=0, tempo=1.0):
    """Un pezzo della voce del narratore, con tono e velocita' cambiati."""
    af = None
    if semitoni or tempo != 1.0:
        af = f'rubberband=pitch={2 ** (semitoni / 12):.5f}:tempo={tempo:.3f}'
    return norm(fade(dec(os.path.join(A, f'voce_t{n}.mp3'), max(0.0, ss), to, af)))


def sfx(nome, d=None):
    x = norm(dec(os.path.join(A, 'sfx', 'mixkit', nome)))
    return fade(x[:int(d * SR)]) if d else x


def cassa(d=0.22):
    t = np.arange(int(d * SR)) / SR
    f = 45 + 90 * np.exp(-t * 28)
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 14)).astype(np.float32)


def bip(f=880.0, d=0.11):
    t = np.arange(int(d * SR)) / SR
    return fade(np.sin(2 * np.pi * f * t).astype(np.float32), 0.008, 0.03)


def mix(dur, eventi):
    y = np.zeros(int(dur * SR) + 1, dtype=np.float32)
    for t, x, g in eventi:
        i = int(t * SR)
        x = x[:max(0, len(y) - i)]
        y[i:i + len(x)] += x * g
    return y


def salva(nome, y):
    os.makedirs(OUT, exist_ok=True)
    y = norm(y, 0.89)
    p = os.path.join(OUT, nome + '.wav')
    with wave.open(p, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((y * 32767).astype('<i2').tobytes())
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', p, '-b:a', '192k', p[:-4] + '.mp3'], check=True)
    print(nome, round(len(y) / SR, 2), 's')


def pulisci(t):
    return re.sub(r'[^a-zàèéìòù]', '', t.lower())


def frase_logica(n):
    """Tempi di «Allora Pippo fa | la cosa piu' logica» nel video n."""
    w = json.load(open(os.path.join(A, f'words_t{n}.json')))
    k = [pulisci(x[2]) for x in w]
    i = max(j for j, t in enumerate(k) if t == 'logica')
    a = max(j for j in range(i) if k[j] == 'allora')
    f = max(j for j in range(a, i) if k[j] == 'fa')
    return w[a][0], w[f][1], w[f + 1][0], w[i][1]


# «Pippo,» in apertura del video 021 e «Tumbo.» a fine frase nel video 018:
# sono le due registrazioni piu' isolate (pausa prima o dopo).
def pip(tempo=1.15):
    return voce('021', 0.0, 0.56, semitoni=6, tempo=tempo)


def tum(tempo=1.25):
    return voce('018', 40.73, 41.34, semitoni=-5, tempo=tempo)


def firma():
    """Pip-po, (bau), Tum-bo, bip: quattro battiti a 120 BPM = 2 secondi."""
    b = 0.5
    pop = sfx('mk_Hard_pop_click.ogg', 0.15)  # segnaposto del «bau», da registrare
    return mix(2.4, [
        (0.0, pip(), 1.0),
        (b, pop, 0.5),
        (2 * b, tum(), 1.0), (2 * b, cassa(), 0.5), (2 * b + 0.25, cassa(), 0.35),
        (3 * b, bip(), 0.35),
    ])


def micro(n='024'):
    """Chiamata del narratore, pausa, risposta in coro, firma: 6-7 secondi."""
    s0, e_fa, s_la, e_log = frase_logica(n)
    chiamata = voce(n, s0 - 0.03, e_fa + 0.02)
    t1 = len(chiamata) / SR + 0.35
    coro = [(t1 + d, voce(n, s_la - 0.01, e_log + 0.10, semitoni=st), g)
            for st, d, g in ((0, 0, 1.0), (3, .015, .55), (-3, .025, .55),
                             (5, .035, .40), (-5, .020, .45), (7, .030, .30))]
    t2 = t1 + len(coro[0][1]) / SR + 0.30
    f = firma()
    colpo = sfx('mk_Short_bass_hit.ogg', 0.6)
    return mix(t2 + len(f) / SR, [(0, chiamata, 1.0), (t1, colpo, 0.8)] + coro + [(t2, f, 1.0)])


def ritmo(bpm=102, battute=6):
    """Il ritmo fatto con i due nomi (Canzone 2), circa 14 secondi."""
    b = 60 / bpm
    p, t_, pop = pip(1.5), tum(1.5), sfx('mk_Hard_pop_click.ogg', 0.15)
    ev = []
    for k in range(battute):
        t = k * 4 * b
        ev += [(t, p, 1.0), (t + b, pop, .35), (t + 2 * b, t_, 1.0),
               (t + 2 * b, cassa(), .5), (t + 2.5 * b, cassa(), .35), (t + 3 * b, pop, .35)]
        if k % 2:
            ev.append((t + b, p, .9))
    ev.append(((battute * 4 - 1) * b, bip(), .35))
    return mix(battute * 4 * b + 0.3, ev)


if __name__ == '__main__':
    salva('firma_v0', firma())
    salva('micro_v0', micro())
    salva('ritmo_v0', ritmo())
