"""Video 020 (Il terzo personaggio) - sottotitoli parola per parola (parolacce con asterischi) + titoli gialli. Font scelto dall'autore: B, Luckiest Guy (assets/font).
Esce t020/captions.ass. Uso, dalla cartella del progetto: python scripts/captions017.py
Le parole vengono da audio/words_t020.json; gli errori della trascrizione sono corretti qui sotto per numero di parola."""
import json, re
W = [[a, b, w.strip()] for a, b, w in json.load(open('audio/words_t020.json'))]
FIX = {0: 'FERMI', 1: 'TUTTI!', 4: 'c******e', 43: 'st****o', 6: 'pedali', 29: 'merda', 36: 'c***o', 37: 'ESPLODE!', 41: 'Gualtiero', 54: 'LO', 55: 'CREATE', 56: 'VOI,', 57: 'BRANCO', 58: 'DI', 59: 'SCIMMIE!', 73: 'REGOLE!', 95: 'UFFICIALE!', 101: 'DUE', 104: 'm***a', 105: 'NO!', 108: 'c**o', 110: 'COMMENTA,', 111: 'TESTA', 112: 'DI', 113: 'C***O!'}
MERGE = {29: 'cicciom***a', 40: 'candida'}        # parole che la trascrizione ha spezzato
DROP = set()                                                           # «la» che la voce non dice: il suo tempo va alla parola dopo
toks = []; carry = None
for i, (a, b, w) in enumerate(W):
    if i in DROP: carry = a; continue
    if i in MERGE: toks[-1][1] = b; toks[-1][2] = MERGE[i]; continue
    toks.append([carry if carry is not None else a, b, FIX.get(i, w)]); carry = None
END = 45.1
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
    """altezza della parola: di solito 1230; in basso sui primi piani del telefono e di Gualtiero, e sul pianto di Pippo."""
    if 39.75 <= t < 42.05: return 1650
    if 9.3 <= t < 10.4: return 1600
    return 1230
ev = []; shown = []
for k, (s, e, w) in enumerate(toks):
    nxt = toks[k + 1][0] if k + 1 < len(toks) else END
    end = min(nxt, e + 0.45); end = min(max(end, s + 0.18), max(nxt, s + 0.12))
    txt = re.sub(r'[.,]+$', '', w); shown.append(txt)
    fs = '\\fs%d' % min(124, int(1000 / (0.66 * len(txt)))) if len(txt) > 11 else ''
    ev.append('Dialogue: 1,%s,%s,Word,,0,0,0,,{\\pos(540,%d)%s\\fscx70\\fscy70\\t(0,90,\\fscx100\\fscy100)}%s' % (ts(s), ts(end), ypos(s), fs, txt))
TITLES = [('MODALITÀ AEREO', 3.4, 4.45), ('MANCA QUALCUNO', 5.05, 5.95), ('BOOM!', 13.08, 13.95), ('RESPINTO', 17.92, 19.05), ('LO CREATE VOI!', 21.68, 22.58),
          ('REGOLE', 29.4, 30.25), ('1. SEGUI IL PROFILO', 30.3, 31.22), ('2. METTI LIKE', 31.26, 31.95), ('3. COMMENTA LA TUA IDEA', 31.98, 33.55), ('48 ORE', 33.62, 34.7),
          ('IL PIÙ VOTATO VINCE', 34.74, 35.85), ('PERSONAGGIO UFFICIALE', 35.88, 38.1), ('GUALTIERO 2?!', 39.8, 40.75), ('COMMENTA ORA!', 43.32, 45.1)]
def fit(t):
    lines = [t]
    if len(t) > 17:
        sp_ = [i for i, c in enumerate(t) if c == ' ']; i = min(sp_, key=lambda i: abs(i - len(t) / 2)); lines = [t[:i], t[i + 1:]]
    L = max(len(x) for x in lines); return '\\N'.join(lines), min(104, int(1000 / (0.68 * L)))
for i, (t, s, e) in enumerate(TITLES):
    rot = -4 if i % 2 else 3; txt, fs = fit(t)
    ev.append('Dialogue: 2,%s,%s,Title,,0,0,0,,{\\an8\\pos(540,300)\\frz%d\\fs%d\\fscx55\\fscy55\\t(0,140,\\fscx108\\fscy108)\\t(140,220,\\fscx100\\fscy100)}%s' % (ts(s), ts(e), rot, fs, txt))
open('t020/captions.ass', 'w').write(hdr + '\n'.join(ev) + '\n')
print(len(ev), 'eventi;', ' | '.join(shown))
