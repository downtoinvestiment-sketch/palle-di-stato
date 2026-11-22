"""Video 022 (Il barattolo di cetriolini) - sottotitoli parola per parola (parolacce con asterischi) + titoli gialli. Font scelto dall'autore: B, Luckiest Guy (assets/font).
Esce t022/captions.ass. Uso, dalla cartella del progetto: python scripts/captions018.py
Le parole vengono da audio/words_t022.json; gli errori della trascrizione sono corretti qui sotto per numero di parola."""
import json, re
W = [[a, b, w.strip()] for a, b, w in json.load(open('audio/words_t022.json'))]
FIX = {5: 'Pippo', 20: 'cetriolini', 49: 'Tumbo', 65: 'ELEFANTE', 76: 'RAZZO!'}
MERGE = {95: "c'è", 116: 'cazzone'}                                      # questa parola si unisce alla precedente («Quel cazzo ne» = «Quel cazzone»)
toks = []
for i, (a, b, w) in enumerate(W):
    if i in MERGE: toks[-1][1] = b; toks[-1][2] = MERGE[i]; continue
    toks.append([a, b, FIX.get(i, w)])
for t_ in toks: t_[2] = re.sub(r'(?i)(c)azz', lambda m: m.group(1) + '***', t_[2])      # parolacce con gli asterischi
END = 48.9
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
    """altezza della parola: piu' in basso nei primi piani dove la faccia sta al centro."""
    if 31.34 <= t < 33.0 or 34.6 <= t < 37.04: return 1500
    return 1230
ev = []; shown = []
for k, (s, e, w) in enumerate(toks):
    nxt = toks[k + 1][0] if k + 1 < len(toks) else END
    end = min(nxt, e + 0.45); end = min(max(end, s + 0.18), max(nxt, s + 0.12))
    txt = re.sub(r'[.,]$', '', w); shown.append(txt)
    fs = '\\fs%d' % min(124, int(1000 / (0.66 * len(txt)))) if len(txt) > 11 else ''
    ev.append('Dialogue: 1,%s,%s,Word,,0,0,0,,{\\pos(540,%d)%s\\fscx70\\fscy70\\t(0,90,\\fscx100\\fscy100)}%s' % (ts(s), ts(end), ypos(s), fs, txt))
TITLES = [('UN BARATTOLO DI CETRIOLINI', 3.9, 6.9), ('NON SI APRE', 9.4, 11.4), ('UN ELEFANTE', 20.2, 22.1), ('RAZZO', 24.28, 25.9),
          ('SI SVITA DA SOLO', 28.8, 31.2), ('IN MUTANDE', 35.0, 36.9), ("L'AMANTE DI ELEONORA", 37.5, 40.2), ('NESSUNO', 46.0, 48.6)]
def fit(t):
    lines = [t]
    if len(t) > 17:
        sp_ = [i for i, c in enumerate(t) if c == ' ']; i = min(sp_, key=lambda i: abs(i - len(t) / 2)); lines = [t[:i], t[i + 1:]]
    L = max(len(x) for x in lines); return '\\N'.join(lines), min(104, int(1000 / (0.68 * L)))
for i, (t, s, e) in enumerate(TITLES):
    rot = -4 if i % 2 else 3; txt, fs = fit(t)
    y = 300
    if t in ('RAZZO', 'NESSUNO'): fs = 140
    ev.append('Dialogue: 2,%s,%s,Title,,0,0,0,,{\\an8\\pos(540,%d)\\frz%d\\fs%d\\fscx55\\fscy55\\t(0,140,\\fscx108\\fscy108)\\t(140,220,\\fscx100\\fscy100)}%s' % (ts(s), ts(e), y, rot, fs, txt))
open('t022/captions.ass', 'w').write(hdr + '\n'.join(ev) + '\n')
print(len(ev), 'eventi;', ' | '.join(shown))
