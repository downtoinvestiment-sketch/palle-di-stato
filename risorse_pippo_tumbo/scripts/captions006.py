"""Test 006 - sottotitoli parola per parola con le parolacce censurate + titoli gialli. Esce t006/captions.ass"""
import json, re
W = json.load(open('audio/words_t006.json'))
toks = []
for s, e, w in W:
    if w.startswith("'") and toks: toks[-1][2] += w; toks[-1][1] = e; continue
    toks.append([s, e, w])
def merge(a, b, new):
    for i in range(len(toks) - 1):
        if toks[i][2] == a and toks[i + 1][2] == b:
            toks[i] = [toks[i][0], toks[i + 1][1], new]; del toks[i + 1]; return
    print('!! non trovato', a, b)
merge('tosta', 'pane,', 'tostapane'); merge('cazzo', 'netto,', 'cassonetto'); merge('roll', 'bar', 'roll-bar'); merge('caga', 'sotto', 'c***sotto'); merge('Formula', '1.', 'Formula 1')
fix = {'Budget,': 'Budget:', 'Primo,': 'Primo:', 'Soluzione,': 'Soluzione:', 'curda,': 'curva', 'Ma': 'Ma a', 'cazzo': 'c***o', 'cazzo.': 'c***o', 'merda,': 'm***a',
       'coglione': 'c******e', 'bastardo': 'b******o'}
END = 66.0
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
    fs = '\\fs92' if len(txt) > 12 else ''
    ev.append('Dialogue: 1,%s,%s,Word,,0,0,0,,{\\pos(540,1230)%s\\fscx70\\fscy70\\t(0,90,\\fscx100\\fscy100)}%s' % (ts(s), ts(end), fs, txt))
TITLES = [('CESSO AMBULANTE', 0.7, 1.8), ('FACCIA DA TOSTAPANE', 1.9, 3.0), ('MACCHINA DA CORSA', 3.3, 4.6), ('BUDGET: 1 CARRELLO', 5.0, 7.3), ('SENZA FRENI', 8.0, 9.5),
          ('CASSONETTO', 9.7, 11.0), ('RACCOLTA DIFFERENZIATA', 13.2, 15.3), ('FACCIA DA TERMOSIFONE', 17.6, 19.6), ('FRENI', 20.4, 22.3), ('LEVE', 22.8, 23.4),
          ('PATTINI', 23.5, 24.2), ('FRENA...', 24.3, 25.0), ('MA NON STERZA!', 25.1, 26.4), ('SIEPE', 26.9, 27.7), ('NEURONI MARCI', 28.0, 29.1),
          ('VOLANTE', 30.6, 31.3), ('PIANTONE', 31.3, 32.0), ('RUOTE STERZANTI', 32.0, 33.2), ('CURVA!', 33.6, 34.5), ('MIRACOLO DEL C***O', 34.5, 35.6),
          ('A SPINTA', 36.3, 37.9), ('LA VECCHIA', 38.3, 40.0), ('UMILIATO', 40.3, 42.5), ('MOTORE', 43.2, 44.3), ('TOSAERBA', 44.4, 45.2), ('CATENA', 45.3, 45.9),
          ('PIGNONE', 45.9, 46.5), ('ACCELERATORE', 46.5, 47.4), ('FORMULA 1', 49.9, 51.3), ('ULTIMO TEST', 51.6, 52.5), ('CASCO', 52.6, 53.3), ('ROLL-BAR', 53.3, 53.9),
          ('CINTURE', 53.9, 54.7), ('COPILOTA', 55.0, 56.0), ('CALZINO BAGNATO', 57.3, 58.4), ('PARTENZA', 58.5, 60.0), ('CURVA', 60.1, 61.1), ('SORPASSO', 61.2, 62.5),
          ('FRENI FINITI', 62.8, 63.7), ('GARAGE DEL VICINO', 64.0, 66.3)]
for i, (t, s, e) in enumerate(TITLES):
    rot = -4 if i % 2 else 3; fs = '\\fs84' if len(t) > 19 else ''
    ev.append('Dialogue: 2,%s,%s,Title,,0,0,0,,{\\an8\\pos(540,330)\\frz%d%s\\fscx55\\fscy55\\t(0,140,\\fscx108\\fscy108)\\t(140,220,\\fscx100\\fscy100)}%s' % (ts(s), ts(e), rot, fs, t))
open('t006/captions.ass', 'w').write(hdr + '\n'.join(ev) + '\n')
print(len(ev), 'eventi;', ' | '.join(shown))
