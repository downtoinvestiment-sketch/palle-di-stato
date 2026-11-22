"""Video 031 (Il Nobel per la pace) - sottotitoli parola per parola (parolacce con asterischi) + titoli gialli. Font scelto dall'autore: B, Luckiest Guy (assets/font).
Le battute dei personaggi (imitati dal narratore) sono tra «» e colorate: Cappellone oro, Rospina verde, Pippo arancione.
Esce t031/captions.ass. Uso, dalla cartella del progetto: python scripts/captions031.py
Le parole vengono da audio/words_t031.json; gli errori della trascrizione sono corretti qui sotto per numero di parola."""
import json, re
W = [[a, b, w.strip()] for a, b, w in json.load(open('audio/words_t031.json'))]
FIX = {1: 'Cappellone', 5: '«Voglio', 11: 'darling!»', 14: 'vincerlo...', 15: 'bombarda', 16: 'il', 17: 'Venezuela!', 21: 'Yemen!', 23: 'Somalia!', 27: 'GUALTIERO!',
       30: 'MA', 31: 'PERCHÉ,', 32: 'C***O?!', 33: '«Peace!', 34: 'Peace!', 35: 'Boom!»', 36: '«Io', 41: 'amica!»', 44: 'le', 49: 'cartello:', 50: '«Datemi', 52: 'calcio»!',
       60: 'logica!', 61: '«Tumbo,', 65: 'pizza!»', 74: "a mezz'aria!", 80: 'coriandoli,', 83: 'p*****a!', 89: 'pace...', 92: 'Tumbo.', 93: '«Bomb', 95: 'pizza!»', 98: 'Team', 99: 'Tumbo', 101: 'team', 102: 'Cappellone?'}
MERGE = {19: "l'Iran!", 25: "l'Iraq!", 81: 'coriandoli,'}        # parole che la trascrizione ha spezzato
DROP = set()
COL = {}                                                               # colore delle battute dei personaggi (ASS: &HBBGGRR)
for a_, b_, c_ in ((5, 11, '&H0030C8FF&'), (33, 35, '&H0030C8FF&'), (93, 95, '&H0030C8FF&'), (36, 41, '&H0070E060&'), (61, 65, '&H00309CFF&')):
    for k_ in range(a_, b_ + 1): COL[k_] = c_
toks = []; carry = None
for i, (a, b, w) in enumerate(W):
    if i in DROP: carry = a; continue
    if i in MERGE: toks[-1][1] = b; toks[-1][2] = MERGE[i]; continue
    toks.append([carry if carry is not None else a, b, FIX.get(i, w), COL.get(i)]); carry = None
END = 38.7
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
    """altezza della parola: di solito 1230; piu' in basso sui primi piani (Cappellone, Gualtiero a terra, Rospina, Pippo, Tumbo)."""
    for a, b in ((1.67, 4.79), (6.35, 10.25), (12.11, 14.81), (19.95, 21.85), (14.81, 16.79), (16.79, 18.65), (23.85, 25.69), (33.01, 35.25)):
        if a <= t < b: return 1690 if a == 19.95 else 1600
    return 1230
ev = []; shown = []
for k, (s, e, w, col) in enumerate(toks):
    nxt = toks[k + 1][0] if k + 1 < len(toks) else END
    end = min(nxt, e + 0.45); end = min(max(end, s + 0.18), max(nxt, s + 0.12))
    txt = re.sub(r'[.,]+$', '', w); txt = re.sub(r'[.,]+»$', '»', txt); shown.append(txt)
    fs = '\\fs%d' % min(124, int(1000 / (0.66 * len(txt)))) if len(txt) > 11 else ''
    ev.append('Dialogue: 1,%s,%s,Word,,0,0,0,,{\\pos(540,%d)%s\\fscx70\\fscy70\\t(0,90,\\fscx100\\fscy100)%s}%s' % (ts(s), ts(end), ypos(s), fs, ('\\c' + col) if col else '', txt))
TITLES = [('NOBEL PER LA PACE?', 3.06, 4.8), ('MA PERCHÉ?!', 13.16, 14.8), ('PIZZA!', 25.2, 25.72), ('CORIANDOLI!', 29.62, 31.42),
          ('IL NOBEL A TUMBO', 33.34, 33.95), ('TEAM TUMBO O TEAM CAPPELLONE?', 36.16, 38.7)]
def fit(t):
    lines = [t]
    if len(t) > 17:
        sp_ = [i for i, c in enumerate(t) if c == ' ']; i = min(sp_, key=lambda i: abs(i - len(t) / 2)); lines = [t[:i], t[i + 1:]]
    L = max(len(x) for x in lines); return '\\N'.join(lines), min(104, int(1000 / (0.68 * L)))
for i, (t, s, e) in enumerate(TITLES):
    rot = -4 if i % 2 else 3; txt, fs = fit(t)
    ev.append('Dialogue: 2,%s,%s,Title,,0,0,0,,{\\an8\\pos(540,300)\\frz%d\\fs%d\\fscx55\\fscy55\\t(0,140,\\fscx108\\fscy108)\\t(140,220,\\fscx100\\fscy100)}%s' % (ts(s), ts(e), rot, fs, txt))
open('t031/captions.ass', 'w').write(hdr + '\n'.join(ev) + '\n')
print(len(ev), 'eventi;', ' | '.join(shown))
