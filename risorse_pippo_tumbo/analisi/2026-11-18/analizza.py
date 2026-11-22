"""Analisi dei video di Pippo e Tumbo: trascrizione con tempi, parolacce, nomi, stacchi, primi 5 secondi.
Uso: python analizza.py  (scrive risultati.json, trascrizioni.txt e frames/*.jpg)"""
import json, os, re, subprocess
from faster_whisper import WhisperModel
import numpy as np

def audio(p):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-ac', '1', '-ar', '16000', '-f', 's16le', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768.0


OUT = '/home/claude/pippo/out'
AUD = '/home/claude/pippo-tumbo-video/audio'
ITEMS = [
    ('T002', f'{OUT}/PIPPO_TUMBO_T002.mp4'),
    ('T003', f'{OUT}/PIPPO_TUMBO_T003_v2.mp4'),
    ('T004', f'{OUT}/PIPPO_TUMBO_T004.mp4'),
    ('T005', f'{OUT}/PIPPO_TUMBO_T005.mp4'),
    ('T006', f'{OUT}/PIPPO_TUMBO_T006.mp4'),
    ('T007', f'{OUT}/PIPPO_TUMBO_T007.mp4'),
    ('T008', f'{OUT}/PIPPO_TUMBO_T008.mp4'),
    ('T008_45s', f'{OUT}/PIPPO_TUMBO_T008_45s.mp4'),
    ('GUALTIERO_EP1', f'{OUT}/PIPPO_GUALTIERO_EP1.mp4'),
    ('GUALTIERO_EP2', f'{OUT}/PIPPO_GUALTIERO_EP2.mp4'),
    ('TORNADO', f'{OUT}/PIPPO_TORNADO.mp4'),
    ('TORNADO_v2', f'{OUT}/PIPPO_TORNADO_v2.mp4'),
    ('ZUCCHINA', f'{OUT}/PIPPO_ZUCCHINA_v2.mp4'),
    ('AEREO', f'{OUT}/PIPPO_AEREO_v2.mp4'),
    ('TOAST', f'{OUT}/PIPPO_TOAST.mp4'),
    ('PARTO_ELEONORA', f'{OUT}/PIPPO_PARTO_ELEONORA.mp4'),
    ('T017', f'{OUT}/pippo_t017.mp4'),
    ('T021', f'{OUT}/pippo_t021.mp4'),
    ('T018_voce', f'{AUD}/voce_t018.mp3'),
    ('T020_voce', f'{AUD}/voce_t020.mp3'),
    ('T022_voce', f'{AUD}/voce_t022.mp3'),
]

FORTI = r'cazz|troi|puttan|vaffancul|fancul|minchi|mignott|zoccol|\bfiga\b|incazz'
MODERATE = r'merd|stronz|coglion|\bcul[oi]\b|bastard|cagat|cesso|porca|porco|rincoglion'
INSULTI = r'idiot|cretin|deficient|imbecill|scem|pezzent|somar|babbe|sfigat|demente|disgraziat|poveracc|cicci|testa di|pezzo di|coglion|stronz|bastard|cesso'
NOMI = ['Pippo', 'Tumbo', 'Gualtiero', 'Eleonora', 'Giulia']


def durata(p):
    return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p]).decode().strip())


def stacchi(p):
    r = subprocess.run(['ffmpeg', '-hide_banner', '-i', p, '-vf', "select='gt(scene,0.3)',showinfo", '-an', '-f', 'null', '-'],
                       capture_output=True, text=True)
    return [round(float(m), 2) for m in re.findall(r'pts_time:([0-9.]+)', r.stderr)]


def fotogrammi(nome, p):
    tempi = [0.0, 0.7, 1.4, 2.1, 2.8, 3.5, 4.2, 4.9]
    out = f'frames/{nome}_primi5s.jpg'
    if os.path.exists(out):
        return out
    filt = []
    ins = []
    for i, t in enumerate(tempi):
        ins += ['-ss', str(t), '-i', p]
        filt.append(f'[{i}:v]scale=180:320,setsar=1[v{i}]')
    filt.append(''.join(f'[v{i}]' for i in range(len(tempi))) + f'hstack=inputs={len(tempi)}')
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y'] + ins +
                   ['-filter_complex', ';'.join(filt), '-frames:v', '1', '-q:v', '4', out], check=True)
    return out


m = WhisperModel('small', device='cpu', compute_type='int8')
ris = {}
if os.path.exists('risultati.json'):
    ris = json.load(open('risultati.json'))
for nome, p in ITEMS:
    if nome in ris:
        continue
    d = durata(p)
    segs, _ = m.transcribe(audio(p), language='it', word_timestamps=True, vad_filter=False)
    parole = []
    for s in segs:
        for w in (s.words or []):
            parole.append((round(w.start, 2), round(w.end, 2), w.word.strip()))
    testo = ' '.join(w for _, _, w in parole)
    forti = [(t, w) for t, _, w in parole if re.search(FORTI, w.lower())]
    moder = [(t, w) for t, _, w in parole if re.search(MODERATE, w.lower()) and not re.search(FORTI, w.lower())]
    insulti = [(t, w) for t, _, w in parole if re.search(INSULTI, w.lower())]
    tutte = sorted(forti + moder)
    nomi = {n: [t for t, _, w in parole if n.lower() in w.lower()] for n in NOMI}
    r = {
        'file': p, 'durata': round(d, 1), 'parole': len(parole),
        'parole_al_secondo': round(len(parole) / d, 2) if d else None,
        'prima_parola_s': parole[0][0] if parole else None,
        'prima_parolaccia_s': tutte[0][0] if tutte else None,
        'parolacce_forti': forti, 'parolacce_moderate': moder,
        'parolacce_al_minuto': round(len(tutte) / d * 60, 1) if d else None,
        'parolacce_primi5s': [w for t, w in tutte if t < 5],
        'insulti': insulti, 'nomi': {k: len(v) for k, v in nomi.items()},
        'primi_5s': ' '.join(w for t, _, w in parole if t < 5),
        'testo': testo, 'parole_tempi': parole,
    }
    if p.endswith('.mp4'):
        c = stacchi(p)
        r['stacchi'] = len(c)
        r['durata_media_inquadratura_s'] = round(d / (len(c) + 1), 2)
        r['frames_primi5s'] = fotogrammi(nome, p)
    ris[nome] = r
    json.dump(ris, open('risultati.json', 'w'), ensure_ascii=False, indent=1)
    print(nome, 'ok', flush=True)

with open('trascrizioni.txt', 'w') as f:
    for nome, r in ris.items():
        f.write(f"## {nome} ({r['durata']} s, {r['parole']} parole, prima parola a {r['prima_parola_s']} s)\n")
        righe, riga, t0 = [], [], None
        for t, _, w in r['parole_tempi']:
            if t0 is None:
                t0 = t
            riga.append(w)
            if w.endswith(('.', '!', '?')):
                righe.append(f'[{t0:5.1f}] ' + ' '.join(riga))
                riga, t0 = [], None
        if riga:
            righe.append(f'[{t0:5.1f}] ' + ' '.join(riga))
        f.write('\n'.join(righe) + '\n\n')
print('fine')
