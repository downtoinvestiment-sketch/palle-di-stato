"""Test 008 - sottotitoli parola per parola (parolacce censurate) + titoli gialli. Uso: python scripts/captions008.py full|cut -> t008/captions_<ver>.ass"""
import sys, os, json, re
sys.path.insert(0, os.path.dirname(__file__))
import cut008
VER = sys.argv[1] if len(sys.argv) > 1 else 'full'
W = json.load(open('audio/words_t008.json'))
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
for n in '12345': merge('Lezione', n, 'Lezione ' + n)
merge('un', 'aquila', "un'aquila"); merge('porca', 'puttana!', 'p***a p*****a!'); merge('a', 'un', 'un'); merge('un', 'nuovo', 'un uovo'); merge('a', 'terra', 'atterra')
for k in toks:
    if k[2] == 'atterra': k[0] = 36.27
    if k[2] == 'poi': k[1] = 36.25
fix = {'coglione,': 'c******e', 'coglione': 'c******e', 'cazzo': 'c***o', 'stronza': 'st****a', 'tumbo': 'Tumbo', 'tumbo,': 'Tumbo', 'aelica.': 'a elica', 'al': 'ha il',
       "dell'uso.": 'deluso', '3.': 'tre', "l'esempio,": "l'esempio"}
if VER == 'cut': fix.update({'Lezione 3': 'Lezione 1', 'Lezione 5': 'Lezione 2'})
END = 76.4
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
    c = cut008.tclip(VER, s, end)
    if c is None: continue
    w = fix.get(w, w); txt = re.sub(r'[.,]$', '', w); shown.append(txt)
    fs = '\\fs92' if len(txt) > 12 else ''
    ev.append('Dialogue: 1,%s,%s,Word,,0,0,0,,{\\pos(540,1230)%s\\fscx70\\fscy70\\t(0,90,\\fscx100\\fscy100)}%s' % (ts(c[0]), ts(c[1]), fs, txt))
L = {'full': ('LEZIONE 3', 'LEZIONE 5'), 'cut': ('LEZIONE 1', 'LEZIONE 2')}[VER]
TITLES = [('UNA GALLINA', 2.3, 3.6), ("È UN'AQUILA", 4.3, 6.0), ('SAMANTHA', 6.9, 7.8), ('IMPARA A VOLARE', 8.2, 9.7),
          ('LEZIONE 1', 9.95, 10.9), ('MOTIVAZIONE', 11.0, 12.0), ('DOCUMENTARIO', 13.0, 14.4), ('UN UOVO', 15.5, 16.8),
          ('LEZIONE 2', 17.1, 18.1), ('LA RINCORSA', 18.2, 19.1), ('VENTILATORE ROTTO', 21.9, 23.6), ('LO GUARDA', 24.2, 25.1), ('ANCHE TUMBO', 25.7, 26.5),
          ('ANCHE IL VICINO', 27.1, 28.4), ('SILENZIO', 28.9, 30.5),
          (L[0], 30.85, 31.8), ('AERODINAMICA', 31.9, 32.9), ('ALI DI CARTONE', 33.7, 34.8), ('UN METRO', 35.2, 36.0), ('DI FACCIA', 36.5, 38.2), ('MATERASSO CON LA CODA', 39.8, 41.4),
          ('LEZIONE 4', 41.6, 42.6), ('IL VENTO', 42.7, 43.5), ('POTENZA MASSIMA', 44.7, 45.9), ('FERMA', 46.7, 47.5), ('DECOLLA', 48.0, 48.8), ('NELLA SIEPE', 49.1, 50.0),
          ('C******E A ELICA', 50.2, 51.6),
          (L[1], 51.8, 52.8), ('LANCIO DAL TETTO', 53.0, 54.1), ('UNO DUE TRE', 56.1, 56.8), ('DALLE SCALE', 58.3, 59.3), ('PIÙ FURBA DI LUI', 59.5, 60.4), ('UN CECE', 61.3, 62.15),
          ('ULTIMA IDEA', 62.4, 63.3), ('SI ARRENDE', 63.8, 65.0), ('SACCO DI PATATE', 65.2, 66.8), ('VOLA VIA', 69.2, 70.8), ('DA SEMPRE', 71.6, 72.7),
          ('NON AVEVA VOGLIA', 73.0, 73.9), ('ST****A PENNUTA', 74.0, 75.1)]
n = 0
for (t, s, e) in TITLES:
    c = cut008.tclip(VER, s, e)
    if c is None: continue
    rot = -4 if n % 2 else 3; fs = '\\fs84' if len(t) > 19 else ''; n += 1
    ev.append('Dialogue: 2,%s,%s,Title,,0,0,0,,{\\an8\\pos(540,330)\\frz%d%s\\fscx55\\fscy55\\t(0,140,\\fscx108\\fscy108)\\t(140,220,\\fscx100\\fscy100)}%s' % (ts(c[0]), ts(c[1]), rot, fs, t))
c = cut008.tclip(VER, 75.25, 76.5)                                                                        # domanda per i commenti
ev.append('Dialogue: 2,%s,%s,Title,,0,0,0,,{\\an5\\pos(540,1230)\\fs92\\frz-2\\fscx55\\fscy55\\t(0,140,\\fscx106\\fscy106)\\t(140,220,\\fscx100\\fscy100)}TEAM PIPPO\\NO TEAM SAMANTHA?' % (ts(c[0]), ts(c[1])))
open('t008/captions_%s.ass' % VER, 'w').write(hdr + '\n'.join(ev) + '\n')
print(len(ev), 'eventi;', ' | '.join(shown))
