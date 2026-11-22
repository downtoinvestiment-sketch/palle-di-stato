"""Test 015 (il parto di Eleonora) - sottotitoli parola per parola (parolacce censurate) + titoli gialli. Esce t015/captions.ass"""
import json, re
W = json.load(open('audio/words_t015.json'))
toks = []
for (a, b, w) in W:
    w = w.strip().lstrip('«').rstrip('»')
    if toks and (w.startswith("'") or w.startswith('-') or (toks[-1][2] in ('E', 'L', 'l') and w in ('Leonora', "'ospedale,", "'aria!", "'accusa", "'aria"))):
        pw = toks[-1][2]; toks[-1][1] = b; toks[-1][2] = ('Eleonora' if w == 'Leonora' else pw + w); continue
    toks.append([a, b, w])
for t_ in toks:
    if t_[2].startswith(('L\'', 'l\'')) and False: pass
fix = {'salaparto.': 'sala parto.', 'tumbo.': 'Tumbo.', 'tape': 'tutto', 'indostano': 'indossano', 'anti-gas': 'antigas', "L'aria!": "l'aria!", "l'ospedale,": "l'ospedale,", 'arrestano…': 'arrestano…'}
END = 65.7
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
TITLES = [('3 FIGLI', 1.4, 2.6), ('SCOPERTA TERRIFICANTE', 3.0, 4.7), ('SALA PARTO', 5.5, 6.9), ('PANINO AL PROSCIUTTO', 8.9, 10.3), ('SPINGE!', 10.6, 11.55), ('SPINGE!!', 11.62, 13.1), ('SPINGE!!!', 13.24, 14.4),
          ('1. ZUCCHINA', 15.9, 18.0), ('2. BAMBINO', 19.5, 20.3), ('NORMALE', 20.34, 21.1), ('BUONA NOTIZIA', 21.9, 23.2), ('3. UN CANE', 24.9, 25.7), ('GUARDA TUMBO', 27.9, 28.6),
          ('IL CORNUTO A 4 ZAMPE', 29.8, 31.3), ('CAPISCE TUTTO', 31.4, 32.3), ('DALLA FINESTRA', 32.6, 33.7), ('MUCCA FATATA', 34.3, 35.6), ('SCORREGGIANDO', 36.0, 37.4), ('ALLARME PUZZA', 37.6, 39.5),
          ('K.O.', 41.1, 42.0), ('SI RIPRENDE', 43.7, 44.9), ('CHIAMA LA POLIZIA', 45.2, 47.2), ('SIRENE SPIEGATE', 48.2, 49.4), ('MASCHERE ANTIGAS', 51.6, 52.7), ("ARRESTATA: L'ARIA", 53.8, 54.6),
          ('ACCUSA GRAVISSIMA', 55.2, 56.1), ('FAVOREGGIAMENTO DI SCORREGGIA AGGRAVATA', 56.1, 57.9), ('AMMANETTATA', 58.9, 59.7), ('SCORREGGIA DI NUOVO', 62.2, 63.8), ('RINFORZI', 64.5, 65.7)]
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
open('t015/captions.ass', 'w').write(hdr + '\n'.join(ev) + '\n')
print(len(ev), 'eventi;', ' | '.join(shown))
