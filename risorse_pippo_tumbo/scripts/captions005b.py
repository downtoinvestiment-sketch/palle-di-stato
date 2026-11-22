"""Test 005b - sottotitoli parola per parola con le parolacce censurate (asterischi) + titoli gialli. Esce t005/captions_b.ass"""
import json, re
W = json.load(open('audio/words_fit_t005b.json'))
toks = []
for s, e, w in W:
    if w.startswith("'") and toks: toks[-1][2] += w; toks[-1][1] = e; continue
    toks.append([s, e, w])
def merge(a, b, new):
    for i in range(len(toks) - 1):
        if toks[i][2] == a and toks[i + 1][2] == b:
            toks[i] = [toks[i][0], toks[i + 1][1], new]; del toks[i + 1]; return
    print('!! non trovato', a, b)
merge('a', 'punti', 'appunti'); merge('un', 'ala.', "un'ala"); merge('caga', 'sotto.', 'c***sotto'); merge('porca', 'puttana!', 'p***a p*****a!')
fix = {'pippo': 'Pippo', 'Tombo': 'Tumbo', 'Budget,': 'Budget:', 'Soluzione,': 'Soluzione:', 'deficente,': 'deficiente', 'spiaccicassi.': 'spiaccicarsi', 'è': 'ha', 'ora': 'Ora',
       'coglione': 'c******e', 'merda.': 'm***a', 'stronzo.': 'st****o', 'cazzo': 'c***o', 'stronzata.': 'st******a', "L'aria": "L'aria"}
END = 45.8
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
    ev.append('Dialogue: 1,%s,%s,Word,,0,0,0,,{\\pos(540,1230)\\fscx70\\fscy70\\t(0,90,\\fscx100\\fscy100)}%s' % (ts(s), ts(end), txt))
TITLES = [('VUOLE VOLARE', 0.9, 1.9), ('BUDGET: 1 TOVAGLIA', 2.0, 3.5), ('DAL TETTO', 3.7, 4.9), ('SACCO DI M***A', 5.1, 6.6), ('BOCCIATO', 6.9, 8.4),
          ('PIÙ TELA', 8.5, 9.8), ('LENZUOLO', 9.85, 10.55), ('CORDE', 10.55, 11.1), ('IMBRACATURA', 11.1, 12.0), ('FRENA!', 12.1, 13.0),
          ('LAMPADARIO', 13.9, 14.5), ('P***A P*****A!', 14.5, 15.6), ('BUCO IN CIMA', 16.9, 17.9), ('ADDIO DONDOLIO', 18.9, 20.2),
          ('VENTO', 22.3, 23.0), ('ALBERO', 24.1, 25.05), ('NIENTE CUPOLA', 25.3, 26.15), ('ALA', 26.25, 26.8), ('CELLE', 26.85, 28.0), ('COMANDI', 28.1, 29.25),
          ('FRENATA', 29.3, 30.8), ('ULTIMO TEST', 31.1, 31.9), ('AEREO', 31.95, 32.7), ('TANDEM', 33.05, 33.6), ('OCCHIALONI', 33.65, 34.3), ('C***SOTTO', 35.1, 35.8),
          ('RISERVA', 36.2, 36.9), ('TOVAGLIA = ST******A', 37.1, 38.25), ('APERTURA', 38.3, 39.4), ('VIRATA', 39.45, 40.45), ('ATTERRAGGIO', 40.5, 41.8),
          ('GIARDINO DEL VICINO', 42.1, 43.35), ('IL PALLONE', 43.9, 45.6)]
for i, (t, s, e) in enumerate(TITLES):
    rot = -4 if i % 2 else 3
    ev.append('Dialogue: 2,%s,%s,Title,,0,0,0,,{\\an8\\pos(540,330)\\frz%d\\fscx55\\fscy55\\t(0,140,\\fscx108\\fscy108)\\t(140,220,\\fscx100\\fscy100)}%s' % (ts(s), ts(e), rot, t))
open('t005/captions_b.ass', 'w').write(hdr + '\n'.join(ev) + '\n')
print(len(ev), 'eventi;', ' | '.join(shown))
