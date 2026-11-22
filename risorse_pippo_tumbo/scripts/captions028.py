"""Video 028 (Il pomodoro da undici euro) - sottotitoli parola per parola (parolacce con asterischi) + la domanda finale in giallo. Font: Luckiest Guy.
Esce t028/captions.ass. Uso, dalla cartella del progetto: python scripts/captions028.py
Le parole vengono da audio/words_t028.json; gli errori della trascrizione sono corretti qui sotto per numero di parola."""
import json, re
W = [[a, b, w.strip()] for a, b, w in json.load(open('audio/words_t028.json'))]
FIX = {14: 'undici', 28: 'del', 29: 'c***o!', 36: 'Cose', 37: 'Importantissime!', 60: 'm***a!', 106: 'c***o!', 108: 'Tumbo,', 110: 'bast***o'}
MERGE = {6: "l'acquisto", 22: "trent'anni,", 31: 'Arriva', 70: 'Addestra', 96: "un'inchiesta", 121: "trent'anni"}   # questa parola si unisce alla precedente
DROP = set()
toks = []; carry = None
for i, (a, b, w) in enumerate(W):
    if i in DROP: carry = a; continue
    if i in MERGE: toks[-1][1] = b; toks[-1][2] = MERGE[i]; continue
    toks.append([carry if carry is not None else a, b, FIX.get(i, w)]); carry = None
END = 44.45
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
ev = []; shown = []
for k, (s, e, w) in enumerate(toks):
    nxt = toks[k + 1][0] if k + 1 < len(toks) else END
    end = min(nxt, e + 0.45); end = min(max(end, s + 0.18), max(nxt, s + 0.12))
    txt = re.sub(r'[.,?…]+$', '', w); shown.append(txt)
    if s >= 42.6: continue                                             # la domanda finale e' il titolo giallo
    fs = '\\fs%d' % min(124, int(1000 / (0.66 * len(txt)))) if len(txt) > 11 else ''
    ev.append('Dialogue: 1,%s,%s,Word,,0,0,0,,{\\pos(540,1660)%s\\fscx70\\fscy70\\t(0,90,\\fscx100\\fscy100)}%s' % (ts(s), ts(end), fs, txt))
ev.append('Dialogue: 2,%s,%s,Title,,0,0,0,,{\\an5\\pos(540,1560)\\frz-3\\fs120\\fscx55\\fscy55\\t(0,140,\\fscx108\\fscy108)\\t(140,220,\\fscx100\\fscy100)}MUTUO' % (ts(42.70), ts(44.5)))
ev.append('Dialogue: 2,%s,%s,Word,,0,0,0,,{\\an5\\pos(540,1680)\\fs84}O' % (ts(43.16), ts(44.5)))
ev.append('Dialogue: 2,%s,%s,Title,,0,0,0,,{\\an5\\pos(540,1790)\\frz3\\fs112\\fscx55\\fscy55\\t(0,140,\\fscx108\\fscy108)\\t(140,220,\\fscx100\\fscy100)}PELLICANO?' % (ts(43.32), ts(44.5)))
open('t028/captions.ass', 'w').write(hdr + '\n'.join(ev) + '\n')
print(len(ev), 'eventi;', ' | '.join(shown))
