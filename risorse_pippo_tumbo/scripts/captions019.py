"""Video 019 (Il doppio gioco) - sottotitoli parola per parola (parolacce con asterischi) + titoli gialli. Font scelto dall'autore: B, Luckiest Guy (assets/font).
Esce t019/captions.ass. Uso, dalla cartella del progetto: python scripts/captions018.py
Le parole vengono da audio/words_t019.json; gli errori della trascrizione sono corretti qui sotto per numero di parola."""
import json, re
W = [[a, b, w.strip()] for a, b, w in json.load(open('audio/words_t019.json'))]
FIX = {2: 'ATOMICHE', 5: 'scontrarsi', 8: 'STACCIONATA', 20: 'FORCHETTA', 31: 'BAZOOKA!', 36: 'ARMATO!', 39: 'SOTTOMARINO', 42: 'GONFIABILE',
       47: 'BOMBA', 48: 'ATOMICA!', 54: 'c***o', 58: 'PRETE', 61: 'DOPPIO', 62: 'GIOCO', 78: 'SPOSA!', 82: 'GEMELLI'}
MERGE = {72: "l'unica", 78: 'LE SPOSA!'}                                   # questa parola si unisce alla precedente
SPLIT = {}
toks = []
for i, (a, b, w) in enumerate(W):
    if i in MERGE: toks[-1][1] = b; toks[-1][2] = MERGE[i]; continue
    toks.append([a, b, FIX.get(i, w)])
END = 36.4
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
    """altezza della parola: di solito 1230; piu' in alto nel primo piano di Pippo e nella culla (non copre le facce)."""
    if 21.96 <= t < 24.6: return 1500
    return 1230
ev = []; shown = []
for k, (s, e, w) in enumerate(toks):
    nxt = toks[k + 1][0] if k + 1 < len(toks) else END
    end = min(nxt, e + 0.45); end = min(max(end, s + 0.18), max(nxt, s + 0.12))
    txt = re.sub(r'[.,]$', '', w); shown.append(txt)
    fs = '\\fs%d' % min(124, int(1000 / (0.66 * len(txt)))) if len(txt) > 11 else ''
    ev.append('Dialogue: 1,%s,%s,Word,,0,0,0,,{\\pos(540,%d)%s\\fscx70\\fscy70\\t(0,90,\\fscx100\\fscy100)}%s' % (ts(s), ts(end), ypos(s), fs, txt))
TITLES = [('SOPRA UNA STACCIONATA', 2.55, 4.2), ('PER UNA PALLINA', 5.6, 6.6), ('BAZOOKA', 12.3, 13.1), ('NELLA PISCINA GONFIABILE', 16.8, 18.35),
          ('LA BOMBA ATOMICA', 19.45, 20.8), ('IL PRETE', 24.64, 25.9), ('DOPPIO GIOCO', 25.92, 27.25), ("L'UNICA COSA CHE SA FARE", 29.6, 31.6),
          ('LE SPOSA!', 31.66, 33.0), ('9 MESI DOPO', 33.04, 34.5), ('GEMELLI', 34.56, 36.9)]
def fit(t):
    lines = [t]
    if len(t) > 17:
        sp_ = [i for i, c in enumerate(t) if c == ' ']; i = min(sp_, key=lambda i: abs(i - len(t) / 2)); lines = [t[:i], t[i + 1:]]
    L = max(len(x) for x in lines); return '\\N'.join(lines), min(104, int(1000 / (0.68 * L)))
for i, (t, s, e) in enumerate(TITLES):
    rot = -4 if i % 2 else 3; txt, fs = fit(t)
    y = 300 if t != '9 MESI DOPO' else 860
    if t in ('9 MESI DOPO', 'LE SPOSA!', 'GEMELLI'): fs = 140
    ev.append('Dialogue: 2,%s,%s,Title,,0,0,0,,{\\an8\\pos(540,%d)\\frz%d\\fs%d\\fscx55\\fscy55\\t(0,140,\\fscx108\\fscy108)\\t(140,220,\\fscx100\\fscy100)}%s' % (ts(s), ts(e), y, rot, fs, txt))
open('t019/captions.ass', 'w').write(hdr + '\n'.join(ev) + '\n')
print(len(ev), 'eventi;', ' | '.join(shown))
