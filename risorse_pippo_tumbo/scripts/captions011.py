"""Test 009 (Pippo e il tornado) - sottotitoli parola per parola (parolacce censurate) + titoli gialli. Esce t011/captions.ass"""
import json, re
W = json.load(open('audio/words_t011.json'))
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
for k in toks:
    if k[2] == 'Arrivano' and k[0] < 9: k[2] = 'Arriva'
    if k[2] == 'una': k[2] = 'un'
    if k[2] == 'gente.': k[2] = 'agente'
fix = {'Tim': 'Team', 'inventi.': 'in venti', '10': 'dieci', 'Prostimo': 'Prossimo', 'tornado,': 'tornado'}
END = 38.2
CA, CB = 2.95, 6.2      # taglio dell'invito a commentare dopo il gancio
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
TITLES = [('TORNADO GIGANTE', 0.2, 1.5), ('CASA MANGIATA', 1.6, 2.9), ('TEAM PIPPO O TEAM TORNADO?', 3.35, 6.0), ('CHIAMA LA POLIZIA', 6.45, 7.7), ('UN AGENTE', 8.1, 9.0), ('IL CAPPELLO!', 10.1, 11.2),
          ('ORA È PERSONALE', 11.6, 13.2), ('LA POLIZIA CHIAMA LA POLIZIA', 13.7, 15.5), ('IN VENTI', 15.8, 16.8), ('ARRESTATO', 17.1, 18.1), ('MANETTE', 18.2, 18.9), ('FOTO SEGNALETICA', 19.0, 20.0),
          ('NON STA FERMO', 20.1, 21.3), ('IL PROCESSO', 21.75, 23.4), ('COME SI DICHIARA?', 23.6, 24.6), ('VOLA VIA IL GIUDICE', 25.0, 26.8), ('COLPEVOLE!', 27.2, 28.0), ('10 ANNI', 28.06, 29.0),
          ('IN CELLA', 29.3, 30.6), ('DA SOLO', 30.7, 31.4), ('FA CORRENTE', 31.5, 32.5), ('PROSSIMO EPISODIO', 32.85, 33.9), ('DENUNCIA UN TERREMOTO', 34.05, 35.5), ('TEAM PIPPO O TEAM TORNADO?', 35.75, 38.2)]
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
open('t011/captions.ass', 'w').write(hdr + '\n'.join(ev) + '\n')
print(len(ev), 'eventi;', ' | '.join(shown))
