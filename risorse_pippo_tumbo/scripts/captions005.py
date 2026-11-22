"""Test 005 - sottotitoli parola per parola (bianchi, bordo nero) + titoli gialli (bordo rosso). Esce t005/captions.ass"""
import json, re
W = json.load(open('audio/words_t005.json'))
toks = []
for s, e, w in W:
    if w.startswith("'") and toks: toks[-1][2] += w; toks[-1][1] = e; continue
    toks.append([s, e, w])
def merge(a, b, new):
    for i in range(len(toks) - 1):
        if toks[i][2] == a and toks[i + 1][2] == b:
            toks[i] = [toks[i][0], toks[i + 1][1], new]; del toks[i + 1]; return
    print('!! non trovato', a, b)
merge('a', 'terra', 'atterra'); merge('a', 'punti,', 'appunti'); merge('un', 'ala,', "un'ala")
fix = {'tumbo': 'Tumbo', 'carossi': 'Però si', 'budget': 'Budget:', 'serve': 'Serve', 'ora': 'Ora', 'soluzione': 'Soluzione:', 'allora': 'Allora', 'ultimo': 'Ultimo',
       'salta': 'Salta', 'apertura': 'Apertura', 'virata': 'Virata', 'atterraggio': 'Atterraggio', "l'aria": "L'aria", 'celle': 'Celle', 'paracadute': 'Paracadute'}
END = 45.6
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
    end = min(nxt, e + 0.45); end = min(max(end, s + 0.18), max(nxt, s + 0.12))
    w = fix.get(w, w); txt = re.sub(r'[.,]$', '', w)
    ev.append('Dialogue: 1,%s,%s,Word,,0,0,0,,{\\pos(540,1230)\\fscx70\\fscy70\\t(0,90,\\fscx100\\fscy100)}%s' % (ts(s), ts(end), txt))
TITLES = [('PIPPO VUOLE VOLARE', 0.1, 1.4), ('BUDGET: 1 TOVAGLIA', 1.6, 3.5), ('DAL TETTO', 3.8, 4.9), ('SACCO DI PATATE', 5.6, 7.0), ('BOCCIATO', 7.2, 8.5),
          ('PIÙ TELA', 8.7, 9.7), ('LENZUOLO', 9.8, 10.5), ('CORDE', 10.5, 11.1), ('IMBRACATURA', 11.1, 12.0), ('FRENA!', 12.1, 13.0),
          ('LAMPADARIO', 13.9, 14.9), ('TERREMOTO', 14.9, 15.8), ('BUCO IN CIMA', 16.4, 17.9), ('ADDIO DONDOLIO', 18.8, 20.3),
          ('VENTO', 21.9, 22.9), ('ALBERO', 23.8, 24.9), ('NIENTE CUPOLA', 25.2, 26.1), ('ALA', 26.3, 26.9), ('CELLE', 26.9, 27.9), ('COMANDI', 28.0, 29.2),
          ('FRENATA', 29.3, 30.8), ('ULTIMO TEST', 31.1, 32.0), ('AEREO', 32.1, 32.9), ('TANDEM', 33.2, 33.9), ('OCCHIALONI', 33.9, 34.6), ('ZERO PAURA', 34.6, 35.4),
          ('RISERVA', 35.6, 36.6), ('LA TOVAGLIA INSEGNA', 36.9, 38.0), ('APERTURA', 38.1, 39.1), ('VIRATA', 39.2, 40.3), ('ATTERRAGGIO', 40.4, 41.8),
          ('GIARDINO DEL VICINO', 42.0, 43.4), ('IL PALLONE', 43.9, 45.3)]
for i, (t, s, e) in enumerate(TITLES):
    rot = -4 if i % 2 else 3
    ev.append('Dialogue: 2,%s,%s,Title,,0,0,0,,{\\an8\\pos(540,330)\\frz%d\\fscx55\\fscy55\\t(0,140,\\fscx108\\fscy108)\\t(140,220,\\fscx100\\fscy100)}%s' % (ts(s), ts(e), rot, t))
open('t005/captions.ass', 'w').write(hdr + '\n'.join(ev) + '\n')
print(len(ev), 'eventi;', ' | '.join(fix.get(t[2], t[2]) for t in toks))
