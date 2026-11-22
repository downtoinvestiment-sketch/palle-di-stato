"""Test 009 (Pippo contro Gualtiero, ep. 1) - sottotitoli parola per parola (parolacce censurate) + titoli gialli. Esce t009/captions.ass"""
import json, re
W = json.load(open('audio/words_t009.json'))
toks = []
for s, e, w in W:
    w = w.strip()
    if w.startswith("'") and toks: toks[-1][2] += w; toks[-1][1] = e; continue
    toks.append([s, e, w])
def merge(a, b, new):
    for i in range(len(toks) - 1):
        if toks[i][2] == a and toks[i + 1][2] == b:
            toks[i] = [toks[i][0], toks[i + 1][1], new]; del toks[i + 1]; return
    print('!! non trovato', a, b)
merge('ciccio', 'merda', 'cicciom***a'); merge('spara', 'neve', 'sparaneve'); merge('la', 'spira', "l'aspira"); merge("l'aspira", 'polvere.', "l'aspirapolvere")
merge('lancia', 'a', 'lancia'); merge('lancia', 'fiamme.', 'lanciafiamme')
for k in toks:
    if k[2] == 'Allora': k[0] = 28.35
fix = {'Cazzo!': 'C***o!', 'stronzo!': 'st****o!', 'nene': 'neve', 'fon,': 'phon', 'legca': 'lecca', "d'acetofono.": 'da citofono', 'Prostimo': 'Prossimo', 'Tim': 'Team', '1.': 'uno'}
END = 43.9
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
Style: Word,Poppins,118,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,9,3,5,40,40,0,1
Style: Title,Poppins,104,&H0019D2FF,&H0019D2FF,&H001A1ACC,&H80000000,1,0,0,0,100,100,0,0,1,11,4,8,40,40,150,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
ev = []; shown = []
for k, (s, e, w) in enumerate(toks):
    nxt = toks[k + 1][0] if k + 1 < len(toks) else END
    end = min(nxt, e + 0.45); end = min(max(end, s + 0.18), max(nxt, s + 0.12))
    w = fix.get(w, w); txt = re.sub(r'[.,]$', '', w); shown.append(txt)
    fs = '\\fs%d' % min(118, int(1000 / (0.62 * len(txt)))) if len(txt) > 12 else ''
    ev.append('Dialogue: 1,%s,%s,Word,,0,0,0,,{\\pos(540,1230)%s\\fscx70\\fscy70\\t(0,90,\\fscx100\\fscy100)}%s' % (ts(s), ts(end), fs, txt))
TITLES = [('GUALTIERO!', 0.5, 1.4), ('COL PHON', 2.6, 3.3), ('ST****O', 3.4, 4.5), ('PIPPO VS GUALTIERO', 4.8, 6.1), ('EPISODIO 1', 6.2, 7.3), ('VUOLE LA NEVE', 7.6, 8.8), ('AD AGOSTO', 9.0, 9.9),
          ('TENTATIVO 1', 10.1, 11.1), ('IL FREEZER', 11.6, 12.8), ('BARBECUE', 13.6, 14.9), ('TENTATIVO 2', 15.15, 16.0), ('MILLE GHIACCIOLI', 16.2, 17.9), ('LI LECCA TUTTI', 18.5, 19.6),
          ('CICCIOM***A', 19.8, 20.5), ('FACCIA DA CITOFONO', 20.6, 21.9), ('TENTATIVO 3', 22.0, 22.75), ('CANNONE SPARANEVE', 22.85, 24.9), ('GIRA IL TUBO', 25.5, 26.8),
          ('NEVICA IN SALOTTO', 27.0, 27.85), ('CAMION DI POLISTIROLO', 29.3, 30.8), ('NEVICA!', 31.0, 32.9), ('LA SUA MACCHINA', 33.4, 34.7), ('TERMOSIFONE CON LE CIABATTE', 34.9, 36.4),
          ('PROSSIMO EPISODIO', 36.6, 37.6), ('LANCIAFIAMME', 38.6, 39.7), ('TEAM PIPPO O TEAM GUALTIERO?', 39.9, 41.45), ('SCRIVILO NEI COMMENTI', 41.6, 43.9)]
def fit(t):
    """titolo lungo: va a capo vicino alla meta', poi il corpo si adatta alla riga piu' lunga (larghezza utile ~1000 px)."""
    lines = [t]
    if len(t) > 19:
        sp_ = [i for i, c in enumerate(t) if c == ' ']; i = min(sp_, key=lambda i: abs(i - len(t) / 2)); lines = [t[:i], t[i + 1:]]
    L = max(len(x) for x in lines); return '\\N'.join(lines), min(104, int(1000 / (0.64 * L)))
for i, (t, s, e) in enumerate(TITLES):
    rot = -4 if i % 2 else 3; txt, fs = fit(t)
    ev.append('Dialogue: 2,%s,%s,Title,,0,0,0,,{\\an8\\pos(540,300)\\frz%d\\fs%d\\fscx55\\fscy55\\t(0,140,\\fscx108\\fscy108)\\t(140,220,\\fscx100\\fscy100)}%s' % (ts(s), ts(e), rot, fs, txt))
open('t009/captions.ass', 'w').write(hdr + '\n'.join(ev) + '\n')
print(len(ev), 'eventi;', ' | '.join(shown))
