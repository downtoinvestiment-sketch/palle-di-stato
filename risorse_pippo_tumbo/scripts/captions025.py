"""Video 025 (Martina nel water) - sottotitoli parola per parola (parolacce con asterischi) + titoli gialli. Font scelto dall'autore: Luckiest Guy.
Esce t025/captions.ass. Uso, dalla cartella del progetto: python scripts/captions025.py
Le parole vengono da audio/words_t025.json; gli errori della trascrizione sono corretti qui sotto per numero di parola."""
import json, re
W = [[a, b, w.strip()] for a, b, w in json.load(open('audio/words_t025.json'))]
FIX = {2: 'co***ne', 8: 'in ferie,', 21: 'sciacquone!', 23: 'risale!', 24: 'Con', 31: 'lui,', 33: 'st***za!', 40: 'logica!', 41: 'Compra', 43: 'elefante!', 44: 'E',
       51: 'casqué,', 55: 'c***o', 60: 'tutto,', 62: 'p****na!', 66: 'allaga....', 77: 'Tumbo', 86: 'SCIAF!', 93: 'salotto.', 94: 'E', 107: 'team'}
MERGE = {69: "dall'acqua", 103: "l'elefante!"}                          # questa parola si unisce alla precedente
DROP = {9, 29, 73}                                                     # «è» e «sought» inventati dalla trascrizione, la «a» di «alta a 40»
toks = []; carry = None
for i, (a, b, w) in enumerate(W):
    if i in DROP: carry = a; continue
    if i in MERGE: toks[-1][1] = b; toks[-1][2] = MERGE[i]; continue
    toks.append([carry if carry is not None else a, b, FIX.get(i, w)]); carry = None
END = 36.9
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
    """altezza della parola: in basso; piu' in alto sulla ripresa dall'alto di Martina-tappeto (la sua faccia e' in basso)."""
    if 30.2 <= t < 31.9: return 1230
    return 1660
ev = []; shown = []
for k, (s, e, w) in enumerate(toks):
    nxt = toks[k + 1][0] if k + 1 < len(toks) else END
    end = min(nxt, e + 0.45); end = min(max(end, s + 0.18), max(nxt, s + 0.12))
    txt = re.sub(r'[.,]$', '', w); shown.append(txt)
    fs = '\\fs%d' % min(124, int(1000 / (0.66 * len(txt)))) if len(txt) > 11 else ''
    ev.append('Dialogue: 1,%s,%s,Word,,0,0,0,,{\\pos(540,%d)%s\\fscx70\\fscy70\\t(0,90,\\fscx100\\fscy100)}%s' % (ts(s), ts(end), ypos(s), fs, txt))
TITLES = [('È UNO SCARAFAGGIO', 4.7, 6.3), ('UN ELEFANTE!', 14.6, 15.2), ('TANGO!', 15.7, 16.7), ('BOOM!', 19.95, 20.8), ('40 METRI', 25.4, 26.1),
          ('SCIAF!', 29.3, 30.2), ('TEAM PIPPO O TEAM MARTINA?', 34.68, 37.4)]
def fit(t):
    lines = [t]
    if len(t) > 17:
        sp_ = [i for i, c in enumerate(t) if c == ' ']; i = min(sp_, key=lambda i: abs(i - len(t) / 2)); lines = [t[:i], t[i + 1:]]
    L = max(len(x) for x in lines); return '\\N'.join(lines), min(104, int(1000 / (0.68 * L)))
for i, (t, s, e) in enumerate(TITLES):
    rot = -4 if i % 2 else 3; txt, fs = fit(t)
    ev.append('Dialogue: 2,%s,%s,Title,,0,0,0,,{\\an8\\pos(540,300)\\frz%d\\fs%d\\fscx55\\fscy55\\t(0,140,\\fscx108\\fscy108)\\t(140,220,\\fscx100\\fscy100)}%s' % (ts(s), ts(e), rot, fs, txt))
open('t025/captions.ass', 'w').write(hdr + '\n'.join(ev) + '\n')
print(len(ev), 'eventi;', ' | '.join(shown))
