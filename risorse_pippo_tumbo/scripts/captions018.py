"""Test 018 (La mente, voce con gli insulti) - sottotitoli parola per parola (parolacce con asterischi) + titoli gialli. Font scelto dall'autore: B, Luckiest Guy (assets/font).
Esce t018/captions.ass. Uso, dalla cartella del progetto: python scripts/captions018.py
Le parole vengono da audio/words_t018.json; gli errori della trascrizione sono corretti qui sotto per numero di parola."""
import json, re
W = [[a, b, w.strip()] for a, b, w in json.load(open('audio/words_t018.json'))]
FIX = {19: 'SQUALO!', 23: 'c******e', 26: 'quel', 27: 'ladro', 29: 'm***a', 47: 's*****o', 52: 'C***O', 54: 'BASE', 56: 'SUPERSICUREZZA!',
       57: 'Telecamere!', 58: 'Laser!', 59: 'Squali!', 66: 'b******o', 72: 'apre', 73: 'Tumbo', 81: 'ZOOM', 95: 'c***o?', 99: 'GIULIA!', 100: 'QUELLA',
       101: 'T***A', 102: 'DI', 103: 'M***A!', 105: 'moglie!', 106: 'Minuscola!', 111: 'Tumbo', 116: 'p*****a', 122: '«Occupato»', 123: 'V********o!'}
MERGE = {4: "dell'umido", 71: 'Gliela', 98: "c'è", 113: "Un'altra"}      # questa parola si unisce alla precedente
toks = []
for i, (a, b, w) in enumerate(W):
    if i in MERGE: toks[-1][1] = b; toks[-1][2] = MERGE[i]; continue
    toks.append([a, b, FIX.get(i, w)])
# «a pretumbo»: la trascrizione ha unito «apre» e «Tumbo»: «a» diventa «apre», «pretumbo» diventa «Tumbo»
END = 48.6
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
    """altezza della parola: di solito 1230; piu' in basso sulle inquadrature dall'alto dentro le teste (non copre Giulia)."""
    if 35.2 <= t < 37.74 or 41.3 <= t < 44.14: return 1650
    return 1230
ev = []; shown = []
for k, (s, e, w) in enumerate(toks):
    nxt = toks[k + 1][0] if k + 1 < len(toks) else END
    end = min(nxt, e + 0.45); end = min(max(end, s + 0.18), max(nxt, s + 0.12))
    txt = re.sub(r'[.,]$', '', w); shown.append(txt)
    fs = '\\fs%d' % min(124, int(1000 / (0.66 * len(txt)))) if len(txt) > 11 else ''
    ev.append('Dialogue: 1,%s,%s,Word,,0,0,0,,{\\pos(540,%d)%s\\fscx70\\fscy70\\t(0,90,\\fscx100\\fscy100)}%s' % (ts(s), ts(end), ypos(s), fs, txt))
TITLES = [('SU UNO SQUALO?!', 5.3, 6.1), ('PER UN GIORNALE', 6.12, 7.5), ('ZONA GIORNALE', 17.0, 18.2), ('BALLANDO', 21.55, 22.95), ('TUMBO?!', 24.5, 25.15),
          ('ZOOM', 28.35, 29.2), ('NON SBATTE MAI LE PALPEBRE', 29.6, 31.4), ('TOC TOC', 32.32, 33.2), ('GIULIA', 35.7, 37.7), ('LA MOGLIE DI GUALTIERO', 37.74, 39.3),
          ("UN'ALTRA GIULIA", 41.75, 43.2), ('TOC TOC', 45.0, 45.8), ('OCCUPATO', 45.9, 46.7)]
def fit(t):
    lines = [t]
    if len(t) > 17:
        sp_ = [i for i, c in enumerate(t) if c == ' ']; i = min(sp_, key=lambda i: abs(i - len(t) / 2)); lines = [t[:i], t[i + 1:]]
    L = max(len(x) for x in lines); return '\\N'.join(lines), min(104, int(1000 / (0.68 * L)))
for i, (t, s, e) in enumerate(TITLES):
    rot = -4 if i % 2 else 3; txt, fs = fit(t)
    y = 300 if t != 'LA MOGLIE DI GUALTIERO' else 470
    if t == 'GIULIA': fs = 150
    ev.append('Dialogue: 2,%s,%s,Title,,0,0,0,,{\\an8\\pos(540,%d)\\frz%d\\fs%d\\fscx55\\fscy55\\t(0,140,\\fscx108\\fscy108)\\t(140,220,\\fscx100\\fscy100)}%s' % (ts(s), ts(e), y, rot, fs, txt))
open('t018/captions.ass', 'w').write(hdr + '\n'.join(ev) + '\n')
print(len(ev), 'eventi;', ' | '.join(shown))
