"""Video 032 (Francesco ci prova) - sottotitoli parola per parola (parolacce con asterischi) + titoli gialli. Font scelto dall'autore: Luckiest Guy.
Esce t032/captions.ass. Uso, dalla cartella del progetto: python scripts/captions027.py
Le parole vengono da audio/words_t032.json; gli errori della trascrizione sono corretti qui sotto per numero di parola."""
import json, re
W = [[a, b, w.strip()] for a, b, w in json.load(open('audio/words_t032.json'))]
FIX = {0: 'FRANCESCO!', 2: 'c***o', 30: 'GHOSTATO!', 71: 'Ma Tumbo', 110: 'm***a!'}
MERGE = {17: 'tostapane!', 41: 'centrifuga', 54: "l'emozione.", 75: 'Wi-Fi.'}   # questa parola si unisce alla precedente
DROP = set()
HUSS = {30}
HUSS_EXTRA = ()
FILE = {0: ('G',)}   # come in audio026.py                                                 # il ritornello: parola gigante gialla che trema
toks = []; carry = None
for i, (a, b, w) in enumerate(W):
    if i in DROP: carry = a; continue
    if i in MERGE: toks[-1][1] = b; toks[-1][2] = MERGE[i]; continue
    toks.append([carry if carry is not None else a, b, FIX.get(i, w)]); carry = None
END = 41.5
def ts(t):
    t = max(0, t); h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return '%d:%02d:%05.2f' % (h, m, s)
hdr = '''[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Word,Luckiest Guy,124,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,0,0,0,0,100,100,1,0,1,10,3,5,40,40,0,1
Style: Huss,Luckiest Guy,230,&H0019D2FF,&H0019D2FF,&H00000000,&H80000000,0,0,0,0,100,100,2,0,1,14,5,5,40,40,0,1
Style: Title,Luckiest Guy,104,&H0019D2FF,&H0019D2FF,&H001A1ACC,&H80000000,0,0,0,0,100,100,1,0,1,11,4,8,40,40,150,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
def ypos(t):
    return 1660
ev = []; shown = []; ih = [i for i in range(len(W)) if i not in MERGE]
for k, (s, e, w) in enumerate(toks):
    nxt = toks[k + 1][0] if k + 1 < len(toks) else END
    end = min(nxt, e + 0.45); end = min(max(end, s + 0.18), max(nxt, s + 0.12))
    txt = re.sub(r'[.,?…]+$', '', w); shown.append(txt)
    if ih[k] in HUSS:
        ordine = sorted(HUSS).index(ih[k]); fila = FILE[ordine]
        if fila == ('G',):                                              # lo tsunami: un HUSS solo, gigante, che trema
            ev.append('Dialogue: 2,%s,%s,Huss,,0,0,0,,{\\pos(540,1450)\\fscx40\\fscy40\\t(0,90,\\fscx95\\fscy95)\\t(90,200,\\fscx85\\fscy85)\\t(200,500,\\frz-5)}GHOSTATO!' % (ts(s), ts(min(nxt, s + 0.9))))
            continue
        for j, dt in enumerate(fila):
            s0 = s + dt; e0 = s + fila[j + 1] if j + 1 < len(fila) else min(max(nxt, s0 + 0.3), s0 + 0.5)
            ev.append('Dialogue: 2,%s,%s,Huss,,0,0,0,,{\\pos(540,%d)\\fscx40\\fscy40\\t(0,70,\\fscx118\\fscy118)\\t(70,140,\\fscx100\\fscy100)\\frz%d}HUSS' % (ts(s0), ts(e0), 1500 - 40 * (j % 2), (-4 if j % 2 else 3)))
        continue
        ev.append('Dialogue: 2,%s,%s,Huss,,0,0,0,,{\\pos(540,1500)\\fscx40\\fscy40\\t(0,80,\\fscx118\\fscy118)\\t(80,160,\\fscx100\\fscy100)\\t(160,700,\\frz-3)}HUSS' % (ts(s), ts(end)))
        continue
    fs = '\\fs%d' % min(124, int(1000 / (0.66 * len(txt)))) if len(txt) > 11 else ''
    ev.append('Dialogue: 1,%s,%s,Word,,0,0,0,,{\\pos(540,%d)%s\\fscx70\\fscy70\\t(0,90,\\fscx100\\fscy100)}%s' % (ts(s), ts(end), ypos(s), fs, txt))
TITLES = []
for s0 in HUSS_EXTRA:                                                  # HUSS di Tumbo nelle pause prima della notte 7 e della 30
    ev.append('Dialogue: 2,%s,%s,Huss,,0,0,0,,{\\pos(540,1500)\\fscx40\\fscy40\\t(0,70,\\fscx118\\fscy118)\\t(70,140,\\fscx100\\fscy100)\\frz3}HUSS' % (ts(s0), ts(s0 + 0.32)))
def fit(t):
    lines = [t]
    if len(t) > 17:
        sp_ = [i for i, c in enumerate(t) if c == ' ']; i = min(sp_, key=lambda i: abs(i - len(t) / 2)); lines = [t[:i], t[i + 1:]]
    L = max(len(x) for x in lines); return '\\N'.join(lines), min(104, int(1000 / (0.68 * L)))
for i, (t, s, e) in enumerate(TITLES):
    rot = -4 if i % 2 else 3; txt, fs = fit(t)
    ev.append('Dialogue: 2,%s,%s,Title,,0,0,0,,{\\an8\\pos(540,300)\\frz%d\\fs%d\\fscx55\\fscy55\\t(0,140,\\fscx108\\fscy108)\\t(140,220,\\fscx100\\fscy100)}%s' % (ts(s), ts(e), rot, fs, txt))
open('t032/captions.ass', 'w').write(hdr + '\n'.join(ev) + '\n')
print(len(ev), 'eventi;', ' | '.join(shown))
