"""suoni.py - effetti sonori e musica veri (non sintetici) per gli script audioNNN.py.

Cartelle:
  audio/sfx/kenney/<pacchetto>/*.ogg   effetti CC0 di Kenney (impatti, interfaccia, voci da annunciatore, jingle...)
  audio/musica/<umore>/*.mp3           musica di Kevin MacLeod, CC-BY 4.0: va citata nella descrizione del video
                                       (righe pronte in audio/LEGGIMI_AUDIO.md)

Uso dentro uno script audioNNN.py (che lavora in numpy a SR = 44100):
    import suoni as S
    S.cerca('punch')                              # elenco dei file che contengono la parola
    colpo = S.carica('impact-sounds/impactPunch_heavy_000', SR, volume=0.8)
    put(fx, 3.2, colpo)                           # come gli effetti sintetici
    mus = S.musica('comica', DUR, SR, brano='Monkeys_Spinning_Monkeys', volume=0.10)
    # mus ha gia' la lunghezza del video, con dissolvenza in entrata e in uscita

Da terminale:  python scripts/suoni.py cerca game over
"""
import glob
import os
import subprocess
import sys

import numpy as np

QUI = os.path.dirname(os.path.abspath(__file__))
AUDIO = os.path.join(os.path.dirname(QUI), 'audio')
FFMPEG = '/usr/local/bin/ffmpeg' if os.path.exists('/usr/local/bin/ffmpeg') else 'ffmpeg'
UMORI = ('comica', 'suspense', 'epica', 'brainrot', 'allegra')


def _tutti():
    return sorted(glob.glob(os.path.join(AUDIO, 'sfx', '**', '*.ogg'), recursive=True) +
                  glob.glob(os.path.join(AUDIO, 'musica', '**', '*.mp3'), recursive=True))


def cerca(*parole):
    """File audio il cui percorso contiene tutte le parole (in inglese: punch, glass, coin, game, over...)."""
    p = [w.lower() for w in parole]
    return [os.path.relpath(f, AUDIO) for f in _tutti() if all(w in f.lower() for w in p)]


def _trova(nome):
    if os.path.isfile(nome):
        return nome
    for base in (os.path.join(AUDIO, nome), os.path.join(AUDIO, 'sfx', 'kenney', nome), os.path.join(AUDIO, 'musica', nome)):
        for ext in ('', '.ogg', '.mp3'):
            if os.path.isfile(base + ext):
                return base + ext
    trovati = [f for f in _tutti() if nome.lower() in os.path.basename(f).lower()]
    if not trovati:
        raise FileNotFoundError(f"Nessun suono con nome '{nome}'. Prova cerca('{nome.split('_')[0]}')")
    return trovati[0]


def carica(nome, sr=44100, volume=1.0, mono=True):
    """Legge un file audio (ogg/mp3/wav) e lo restituisce come array numpy float32 a sr Hz, mono."""
    f = _trova(nome)
    out = subprocess.run([FFMPEG, '-v', 'error', '-i', f, '-f', 'f32le', '-ac', '1' if mono else '2',
                          '-ar', str(sr), '-'], capture_output=True, check=True).stdout
    return np.frombuffer(out, dtype=np.float32).copy() * volume


def musica(umore, durata, sr=44100, brano=None, volume=0.10, inizio=0.0, dissolvenza=1.0):
    """Sottofondo della durata del video: prende un brano dell'umore scelto (o quello indicato),
    lo taglia o lo ripete, e aggiunge dissolvenze. Restituisce un array numpy mono."""
    if umore not in UMORI:
        raise ValueError(f'umore deve essere uno di {UMORI}')
    file = sorted(glob.glob(os.path.join(AUDIO, 'musica', umore, '*.mp3')))
    if brano:
        file = [f for f in file if brano.lower() in os.path.basename(f).lower()] or file
    x = carica(file[0], sr)
    x = x[int(inizio * sr):]
    n = int(durata * sr)
    if len(x) < n:
        x = np.tile(x, n // len(x) + 1)
    x = x[:n].copy()
    k = int(dissolvenza * sr)
    if k > 0:
        x[:k] *= np.linspace(0, 1, k)
        x[-k:] *= np.linspace(1, 0, k)
    return x * volume


if __name__ == '__main__':
    if len(sys.argv) > 2 and sys.argv[1] == 'cerca':
        for r in cerca(*sys.argv[2:]):
            print(r)
    else:
        print(__doc__)
