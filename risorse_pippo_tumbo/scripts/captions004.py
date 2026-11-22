import json, re
W = json.load(open('audio/words_t004.json'))
fix = {'Tubo': 'Tumbo', 'tubo': 'Tumbo', 'pippo': 'Pippo', 'rimbalsi': 'rimbalzi', 'ghiaya': 'ghiaia', 'astrisce.': 'a strisce.', 'Allora,': 'Allora:', 'dignità.': 'dignità.'}
toks = []
i = 0
while i < len(W):
    s, e, w = W[i]
    if w == 'L' and i + 1 < len(W): w = "L" + W[i + 1][2]; e = W[i + 1][1]; i += 1
    toks.append([s, e, fix.get(w, w)]); i += 1
END = 46.45
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
ev = []
for k, (s, e, w) in enumerate(toks):
    nxt = toks[k + 1][0] if k + 1 < len(toks) else END
    end = min(nxt, e + 0.5) if nxt - e < 0.5 else e + 0.35
    end = max(end, s + 0.18)
    txt = re.sub(r'[.,:;]$', '', w).upper() if False else re.sub(r'[.,]$', '', w)
    ev.append('Dialogue: 1,%s,%s,Word,,0,0,0,,{\\pos(540,1230)\\fscx70\\fscy70\\t(0,90,\\fscx100\\fscy100)}%s' % (ts(s), ts(end), txt))
TITLES = [('DUE PORTE', 1.3, 2.1), ('DUE RIGHE', 2.1, 3.0), ('GATTO UBRIACO', 5.8, 7.0), ('TRE CAFFÈ', 7.9, 9.0), ('RUSPE', 9.6, 10.25), ('RULLI', 10.25, 10.8),
          ('RIGHE DRITTE', 10.8, 11.7), ('PIOGGIA', 11.9, 12.9), ('PISCINA OLIMPIONICA', 14.2, 15.7), ('TRINCEE', 18.0, 18.75), ('TUBI DRENANTI', 18.75, 19.75),
          ('GHIAIA', 19.75, 20.35), ('SABBIA', 20.35, 21.2), ('SINTETICO', 22.9, 23.85), ('GIUNZIONI', 23.9, 25.1), ('COLLA', 27.2, 27.95), ('SABBIA + GOMMA', 27.95, 28.85),
          ('SPAZZOLATA', 28.85, 29.8), ('FORNO!', 31.8, 33.0), ('CARBONI ARDENTI', 33.5, 34.9), ('ERBA VERA', 35.2, 36.1), ('ZOLLE', 36.1, 36.7), ('IRRIGATORI', 36.7, 37.85),
          ('TAGLIO A STRISCE', 37.85, 38.8), ('CHAMPIONS', 38.9, 39.9), ('GIARDINO DEL VICINO', 42.5, 43.6), ('PIPPO TUTTO FARE', 43.8, 45.2)]
for (t, s, e) in TITLES:
    rot = -4 if hash(t) % 2 else 3
    ev.append('Dialogue: 2,%s,%s,Title,,0,0,0,,{\\an8\\pos(540,330)\\frz%d\\fscx55\\fscy55\\t(0,140,\\fscx108\\fscy108)\\t(140,220,\\fscx100\\fscy100)}%s' % (ts(s), ts(e), rot, t))
open('t004/captions.ass', 'w').write(hdr + '\n'.join(ev) + '\n')
print(len(ev), 'events;', ' '.join(t[2] for t in toks[:12]))
