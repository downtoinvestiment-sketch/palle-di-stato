"""Test 007 - sottotitoli parola per parola con le parolacce censurate + titoli gialli. Esce t007/captions.ass"""
import json, re
W = json.load(open('audio/words_t007.json'))
toks = []
for s, e, w in W:
    if w.startswith("'") and toks: toks[-1][2] += w; toks[-1][1] = e; continue
    toks.append([s, e, w])
def merge(a, b, new):
    for i in range(len(toks) - 1):
        if toks[i][2] == a and toks[i + 1][2] == b:
            toks[i] = [toks[i][0], toks[i + 1][1], new]; del toks[i + 1]; return
    print('!! non trovato', a, b)
merge('a', 'terra', 'atterra'); merge('a', 'peso', 'appeso'); merge('appeso', 'la', 'appeso alla'); merge('Gli', 'lo', 'Glielo'); merge('Complimenti', 'di', 'Complimenti')
merge('porca', 'puttana.', 'p***a p*****a'); merge('di', 'puttana', 'di p*****a')
fix = {'coglione': 'c******e', 'coglione.': 'c******e', 'merda': 'm***a', 'merda.': 'm***a', 'cazzo,': 'c***o', 'cazzo.': 'c***o', 'stronzo': 'st****o', 'stronzo.': 'st****o',
       'culo': 'c**o', 'bastardo': 'b******o', 'gesto': 'gesso', 'cagata.': 'c****a', 'Sbuka': 'Sbuca', 'Busare': 'Bussare', 'Ne': 'Ne ha', '200': 'duecento',
       'cagacazzo': 'c***c***o', 'minchione.': 'm*******e'}
END = 67.6
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
TITLES = [('INNAMORATO', 4.2, 5.2), ('IL NANO DEL VICINO', 5.4, 7.2), ('LO VUOLE', 7.4, 8.3), ('LO SOGNA', 8.5, 9.4), ('GIANFRANCO', 11.3, 12.6),
          ('FACCIA DA C**O', 14.6, 15.3), ('CITOFONO ROTTO', 15.4, 16.4), ('STACCIONATA', 16.6, 17.7), ('SCALA', 18.3, 19.4), ('PIÙ ALTA', 20.1, 21.4),
          ('SCALA PIÙ LUNGA', 22.2, 23.5), ('ANCORA PIÙ ALTA', 24.6, 25.8), ('MURAGLIA CINESE', 28.1, 29.2), ('NANO DI GESSO', 29.3, 30.8),
          ('TAPPETO ELASTICO', 31.2, 32.4), ('SFONDATO', 33.1, 34.4), ('PALETTO', 35.6, 37.0), ('FACCIA DA CIABATTA', 40.6, 42.2), ('CATAPULTA', 42.4, 43.5),
          ('TROPPO FORTE', 43.6, 44.4), ('VICINO SBAGLIATO', 44.7, 46.4), ('PALLONCINI', 46.7, 47.6), ('TROPPO POCHI', 47.7, 48.5), ('LE MUTANDE', 49.6, 51.3),
          ('TUNNEL', 51.7, 52.4), ('FOSSA BIOLOGICA', 52.7, 54.0), ('PROFUMO DI VITTORIA', 54.1, 56.1), ('ULTIMO PIANO', 56.4, 57.3), ('BUSSARE', 57.5, 59.1),
          ('APRE', 59.6, 60.6), ('REGALATO', 60.9, 61.8), ('ALTRI 200', 61.9, 63.6), ('LI VUOLE TUTTI', 65.8, 68.3)]
for i, (t, s, e) in enumerate(TITLES):
    rot = -4 if i % 2 else 3; fs = '\\fs84' if len(t) > 19 else ''
    ev.append('Dialogue: 2,%s,%s,Title,,0,0,0,,{\\an8\\pos(540,330)\\frz%d%s\\fscx55\\fscy55\\t(0,140,\\fscx108\\fscy108)\\t(140,220,\\fscx100\\fscy100)}%s' % (ts(s), ts(e), rot, fs, t))
open('t007/captions.ass', 'w').write(hdr + '\n'.join(ev) + '\n')
print(len(ev), 'eventi;', ' | '.join(shown))
