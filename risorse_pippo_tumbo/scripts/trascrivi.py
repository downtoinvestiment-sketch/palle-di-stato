"""Trascrive la voce con i tempi di ogni parola.
Uso:  python scripts/trascrivi.py /percorso/voce.mp3 016
Crea: audio/voce_t016.mp3 (copia), audio/voce16_t016.wav (16 kHz mono), audio/words_t016.json = [[inizio, fine, parola], ...]
Serve: pip install faster-whisper ; ffmpeg. Modello: Systran/faster-whisper-small (si scarica da solo la prima volta)."""
import sys, os, json, shutil, subprocess
src, tag = sys.argv[1], sys.argv[2]
os.makedirs('audio', exist_ok=True)
mp3 = f'audio/voce_t{tag}.mp3'; wav = f'audio/voce16_t{tag}.wav'
if os.path.abspath(src) != os.path.abspath(mp3): shutil.copy(src, mp3)
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', mp3, '-ar', '16000', '-ac', '1', wav], check=True)
from faster_whisper import WhisperModel
m = WhisperModel('small', device='cpu', compute_type='int8')
import wave, numpy as np
wf = wave.open(wav); audio = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
segs, info = m.transcribe(audio, language='it', word_timestamps=True, vad_filter=False)
words = [[round(w.start, 2), round(w.end, 2), w.word] for s in segs for w in s.words]
json.dump(words, open(f'audio/words_t{tag}.json', 'w'), ensure_ascii=False)
dur = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', mp3]).decode().strip())
print('durata %.2f s, %d parole' % (dur, len(words)))
print(' '.join('%s@%.2f' % (w[2].strip(), w[0]) for w in words))
