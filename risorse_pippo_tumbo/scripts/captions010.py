"""Test 009 (Pippo contro Gualtiero, ep. 2) - sottotitoli parola per parola (parolacce censurate) + titoli gialli. Esce t010/captions.ass"""
import json, re
W = json.load(open('audio/words_t010.json'))
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
merge('Porca', 'puttana!', 'p***a p*****a!'); merge('ciccio', 'merda', 'cicciom***a'); merge('lancia', 'fiamme.', 'lanciafiamme'); merge('foto', '-segnaletica,', 'foto segnaletica')
fix = {'stronzo!': 'st****o!', '2.': 'due', 'Tim': 'Team', 'austionata.': 'ustionata', 'È': 'E', 'Prostimo': 'Prossimo', 'Sole.': 'Sole?'}
END = 45.7
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
TITLES = [('ROSSO COME UN GAMBERO', 1.3, 2.7), ('ST****O', 4.1, 5.2), ('PIPPO VS GUALTIERO', 5.45, 6.8), ('EPISODIO 2', 6.85, 7.8), ('TEAM PIPPO O TEAM SOLE?', 7.95, 10.5),
          ('CHIAMA LA POLIZIA', 10.8, 12.1), ('ARRESTATO', 12.9, 14.1), ('MANETTE', 14.3, 15.0), ('FOTO SEGNALETICA', 15.1, 16.1), ('IN CELLA', 16.2, 17.0), ('LAMPADINA MONTATA', 18.4, 19.8),
          ('IL PROCESSO', 20.0, 21.2), ("L'AVVOCATO GUALTIERO", 21.3, 22.5), ('CICCIOM***A', 22.6, 23.4), ('FACCIA DA CITOFONO', 23.45, 24.7), ('FACEVA IL SUO LAVORO', 25.6, 27.6),
          ('LA PROVA', 28.1, 29.4), ('SCHIENA USTIONATA', 29.6, 30.7), ('COLPEVOLE!', 31.3, 32.2), ('ERGASTOLO', 32.26, 33.3), ('BUIO', 33.9, 34.6), ('OVUNQUE', 34.7, 35.7), ('PER SEMPRE', 35.8, 36.8),
          ('PER FARE LUCE...', 37.6, 38.7), ('LANCIAFIAMME', 38.9, 40.1), ('PROSSIMO EPISODIO', 40.35, 41.5), ('ARRESTA LA PIOGGIA', 41.65, 43.2), ('TEAM PIPPO O TEAM GUALTIERO?', 43.36, 45.7)]
def fit(t):
    """titolo lungo: va a capo vicino alla meta', poi il corpo si adatta alla riga piu' lunga (larghezza utile ~1000 px)."""
    lines = [t]
    if len(t) > 19:
        sp_ = [i for i, c in enumerate(t) if c == ' ']; i = min(sp_, key=lambda i: abs(i - len(t) / 2)); lines = [t[:i], t[i + 1:]]
    L = max(len(x) for x in lines); return '\\N'.join(lines), min(104, int(1000 / (0.64 * L)))
for i, (t, s, e) in enumerate(TITLES):
    rot = -4 if i % 2 else 3; txt, fs = fit(t)
    ev.append('Dialogue: 2,%s,%s,Title,,0,0,0,,{\\an8\\pos(540,300)\\frz%d\\fs%d\\fscx55\\fscy55\\t(0,140,\\fscx108\\fscy108)\\t(140,220,\\fscx100\\fscy100)}%s' % (ts(s), ts(e), rot, fs, txt))
open('t010/captions.ass', 'w').write(hdr + '\n'.join(ev) + '\n')
print(len(ev), 'eventi;', ' | '.join(shown))
