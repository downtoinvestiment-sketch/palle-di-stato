"""Test 021 (L'etciù) - sottotitoli parola per parola (parolacce con asterischi) + titoli gialli. Font scelto dall'autore: B, Luckiest Guy (assets/font).
Esce t021/captions.ass. Uso, dalla cartella del progetto: python scripts/captions017.py
Le parole vengono da audio/words_t021.json; gli errori della trascrizione sono corretti qui sotto per numero di parola."""
import json, re
W = [[a, b, w.strip()] for a, b, w in json.load(open('audio/words_t021.json'))]
FIX = {2: 'co***ne', 7: 'm***a', 16: 'c***o.', 21: 'p****na.', 27: 'Tumbo.', 56: 'ETCIÙ!', 60: 'c***o?', 64: 'Gualtiero,', 86: 'm***a.'}
MERGE = {40: 'Scolapasta.', 57: 'ETCIÙ!'}                              # questa parola si unisce alla precedente
DROP = set()
toks = []; carry = None
for i, (a, b, w) in enumerate(W):
    if i in DROP: carry = a; continue
    if i in MERGE: toks[-1][1] = b; toks[-1][2] = MERGE[i]; continue
    toks.append([carry if carry is not None else a, b, FIX.get(i, w)]); carry = None
END = 40.45
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
Style: Title,Luckiest Guy,104,&H0019D2FF,&H0019D2FF,&H001A1ACC,&H80000000,0,0,0,0,100,100,1,0,1,11,4,8,40,40,150,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
def ypos(t):
    """altezza della parola: di solito 1230; in basso quando al centro c'e' il naso con la porticina e Gualtiero."""
    if 26.5 <= t < 31.0 or 33.2 <= t < 41: return 1720
    return 1230
ev = []; shown = []
for k, (s, e, w) in enumerate(toks):
    nxt = toks[k + 1][0] if k + 1 < len(toks) else END
    end = min(nxt, e + 0.45); end = min(max(end, s + 0.18), max(nxt, s + 0.12))
    txt = re.sub(r'[.,]$', '', w); shown.append(txt)
    fs = '\\fs%d' % min(124, int(1000 / (0.66 * len(txt)))) if len(txt) > 11 else ''
    ev.append('Dialogue: 1,%s,%s,Word,,0,0,0,,{\\pos(540,%d)%s\\fscx70\\fscy70\\t(0,90,\\fscx100\\fscy100)}%s' % (ts(s), ts(end), ypos(s), fs, txt))
TITLES = [('STARNUTO BLOCCATO', 4.45, 6.4), ('3 GIORNI', 6.75, 7.8), ('NIENTE', 11.7, 12.45), ('UN CAMION!', 15.42, 16.4), ('GIÙ IL SOLE!', 21.45, 22.95),
          ('ETCIÙ!', 24.62, 25.9), ('MA CHE C***O?', 26.6, 27.8), ('GUALTIERO?!', 29.0, 29.95), ('AL COMPLETO', 38.3, 38.75), ('TRADITORE', 38.8, 40.45)]
def fit(t):
    lines = [t]
    if len(t) > 17:
        sp_ = [i for i, c in enumerate(t) if c == ' ']; i = min(sp_, key=lambda i: abs(i - len(t) / 2)); lines = [t[:i], t[i + 1:]]
    L = max(len(x) for x in lines); return '\\N'.join(lines), min(104, int(1000 / (0.68 * L)))
for i, (t, s, e) in enumerate(TITLES):
    rot = -4 if i % 2 else 3; txt, fs = fit(t)
    ev.append('Dialogue: 2,%s,%s,Title,,0,0,0,,{\\an8\\pos(540,300)\\frz%d\\fs%d\\fscx55\\fscy55\\t(0,140,\\fscx108\\fscy108)\\t(140,220,\\fscx100\\fscy100)}%s' % (ts(s), ts(e), rot, fs, txt))
open('t021/captions.ass', 'w').write(hdr + '\n'.join(ev) + '\n')
print(len(ev), 'eventi;', ' | '.join(shown))
