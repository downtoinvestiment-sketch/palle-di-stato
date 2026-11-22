"""Test 016 (il secondo parto di Eleonora) - sottotitoli parola per parola (parolacce censurate) + titoli gialli. Esce t016/captions.ass"""
import json, re
W = json.load(open('audio/words_t016.json'))
toks = []
for (a, b, w) in W:
    w = w.strip()
    if toks and (w.startswith("'") or (toks[-1][2] == 'E' and w.lower().startswith('leonora')) or (toks[-1][2] == 'piano' and w.startswith('forte'))):
        pw = toks[-1][2]; toks[-1][1] = b
        toks[-1][2] = ('Eleonora' + w[7:]) if pw == 'E' else (pw + w); continue
    toks.append([a, b, w])
fix = {'tumbo,': 'Tumbo,', 'tumbo.': 'Tumbo.', 'tumbo': 'Tumbo', 'sisteme': 'sistema', 'Prostimo': 'Prossimo', 'Tim': 'Team', 'Cocomero': 'cocomero', 'Cocomero?': 'cocomero?', 'Zucchina!': 'zucchina!', 'Zucchina': 'zucchina',
       'cazzo,': 'c***o,', 'cazzo.': 'c***o.', 'cazzo…': 'c***o…', 'cazzo': 'c***o', 'puttana!': 'p******a!', 'troia!': 't***a!', 'vaffanculo!': 'v*********o!', 'partorendo…': 'partorendo!'}
END = 59.2
toks = [t_ for t_ in toks if t_[0] < END]
CA, CB = 99.0, 99.5      # taglio dell'invito a commentare dopo il gancio
def tcut(s, e):
    if CA <= s < CB: return None
    if s < CA: return s, min(e, CA)
    return s - (CB - CA), e - (CB - CA)
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
    cc = tcut(s, end)
    if cc is None: continue
    s, end = cc
    w = fix.get(w, w); txt = re.sub(r'[.,]$', '', w); shown.append(txt)
    fs = '\\fs%d' % min(118, int(1000 / (0.62 * len(txt)))) if len(txt) > 12 else ''
    ev.append('Dialogue: 1,%s,%s,Word,,0,0,0,,{\\pos(540,1230)%s\\fscx70\\fscy70\\t(0,90,\\fscx100\\fscy100)}%s' % (ts(s), ts(end), fs, txt))
TITLES = [('STA PARTORENDO!', 1.0, 2.8), ('QUALCOSA NON TORNA', 4.9, 6.6), ('PANINO', 10.8, 12.0), ('1. ZUCCHINA', 13.1, 14.0), ('NORMALE', 14.1, 15.0), ('2. ZUCCHINA', 16.3, 17.5), ('NORMALE', 17.55, 18.5),
          ('3. CAMION DEI POMPIERI', 19.8, 21.4), ('P******A!', 22.5, 23.7), ('"NORMALE"', 26.2, 27.4), ('NORMALE UN C***O', 27.55, 28.7), ('4. PIANOFORTE', 30.0, 31.2), ('5. GUALTIERO', 32.2, 33.0), ('MA PORCA T***A!', 33.05, 34.4),
          ('HO SBAGLIATO PORTA', 36.8, 38.9), ('È TUMBO', 43.06, 44.1), ('CHI C\'È FUORI?', 44.6, 46.5), ('ELEONORA', 51.0, 53.1), ('UN COCOMERO!', 55.8, 57.7), ('V*********O!', 57.85, 59.2)]
def fit(t):
    """titolo lungo: va a capo vicino alla meta', poi il corpo si adatta alla riga piu' lunga (larghezza utile ~1000 px)."""
    lines = [t]
    if len(t) > 19:
        sp_ = [i for i, c in enumerate(t) if c == ' ']; i = min(sp_, key=lambda i: abs(i - len(t) / 2)); lines = [t[:i], t[i + 1:]]
    L = max(len(x) for x in lines); return '\\N'.join(lines), min(104, int(1000 / (0.64 * L)))
for i, (t, s, e) in enumerate(TITLES):
    cc = tcut(s, e)
    if cc is None: continue
    s, e = cc
    rot = -4 if i % 2 else 3; txt, fs = fit(t)
    ev.append('Dialogue: 2,%s,%s,Title,,0,0,0,,{\\an8\\pos(540,300)\\frz%d\\fs%d\\fscx55\\fscy55\\t(0,140,\\fscx108\\fscy108)\\t(140,220,\\fscx100\\fscy100)}%s' % (ts(s), ts(e), rot, fs, txt))
open('t016/captions.ass', 'w').write(hdr + '\n'.join(ev) + '\n')
print(len(ev), 'eventi;', ' | '.join(shown))
