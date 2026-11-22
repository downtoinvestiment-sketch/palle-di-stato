"""Test 009 (Pippo e Tumbo in aereo) - sottotitoli parola per parola (parolacce censurate) + titoli gialli. Esce t013/captions.ass"""
import json, re
toks = [list(x) for x in [(0.0, 0.5, 'Pippo'), (0.62, 1.06, 'quella'), (1.06, 1.52, 'm***a'), (1.52, 1.64, 'di'), (1.64, 1.94, 'animale'), (1.94, 2.48, 'mammifero'), (2.7, 2.98, 'parte'), (2.98, 3.2, 'per'), (3.2, 3.3, 'le'), (3.3, 3.62, 'Maldive'), (3.62, 3.84, 'con'), (3.84, 4.26, 'Tumbo'), (4.36, 4.5, 'quella'), (4.5, 5.12, 'polpetta'), (5.12, 5.24, 'con'), (5.24, 5.38, 'la'), (5.38, 5.66, 'coda!'), (6.2, 6.64, 'Salgono'), (6.64, 6.8, 'in'), (6.8, 7.24, 'aereo'), (7.6, 7.74, 'Il'), (7.74, 8.12, 'pilota'), (8.34, 9.08, "quell'imbecille"), (9.08, 9.38, 'figlio'), (9.38, 9.5, 'di'), (9.5, 9.92, 't***a'), (10.24, 10.32, 'si'), (10.32, 10.6, 'mangia'), (10.6, 10.68, 'un'), (10.68, 10.98, 'gelato'), (10.98, 11.1, 'da'), (11.1, 11.26, 'due'), (11.26, 11.48, 'chili'), (12.1, 12.56, 'Cagarella'), (13.3, 13.46, 'Il'), (13.46, 13.76, 'pilota'), (13.76, 14.2, 'sparisce'), (14.2, 14.32, 'in'), (14.32, 14.7, 'bagno'), (14.98, 15.22, 'Pippo'), (15.22, 15.28, 'e'), (15.28, 15.64, 'Tumbo'), (15.64, 16.0, 'prendono'), (16.0, 16.14, 'i'), (16.14, 16.48, 'comandi'), (16.96, 17.32, 'Pippo'), (17.32, 17.58, 'accende'), (17.58, 17.72, 'il'), (17.72, 17.96, 'pilota'), (17.96, 18.6, 'automatico'), (18.84, 19.0, 'Era'), (19.0, 19.14, 'il'), (19.14, 19.34, 'tasto'), (19.34, 19.58, 'della'), (19.58, 19.98, 'karaoke'), (20.45, 20.98, 'Tumbo'), (20.98, 21.28, 'apre'), (21.28, 21.38, 'il'), (21.38, 21.72, 'carrello'), (21.72, 21.86, 'delle'), (21.86, 22.28, 'bibite'), (22.28, 22.5, 'e'), (22.5, 22.56, 'se'), (22.56, 22.68, 'lo'), (22.68, 23.08, 'mangia'), (23.34, 23.76, 'Carrello'), (23.76, 24.24, 'compreso'), (24.9, 25.14, 'Pippo'), (25.14, 25.26, 'fa'), (25.26, 25.6, "l'annuncio"), (25.6, 25.7, 'ai'), (25.7, 26.36, 'passeggeri'), (26.74, 27.12, 'Allacciate'), (27.12, 27.24, 'le'), (27.24, 27.68, 'cinture'), (27.68, 28.04, 'e'), (28.04, 28.26, 'non'), (28.26, 28.78, 'chiedetemi'), (28.78, 28.96, 'come'), (28.96, 29.1, 'si'), (29.1, 29.56, 'atterra'), (30.0, 30.22, 'Poi'), (30.22, 30.5, 'squilla'), (30.5, 30.62, 'il'), (30.62, 31.08, 'telefono'), (31.44, 31.54, 'È'), (31.54, 32.04, 'Eleonora'), (32.22, 32.3, 'la'), (32.3, 32.76, 'zucchina'), (32.76, 32.88, 'di'), (32.88, 33.34, 'm***a'), (33.7, 34.08, 'Pippo!'), (34.38, 34.56, 'Sto'), (34.56, 34.72, 'per'), (34.72, 35.22, 'partorire!'), (35.56, 35.72, 'Vieni'), (35.72, 36.16, 'subito!'), (36.52, 36.92, 'Pippo'), (36.92, 37.2, 'guarda'), (37.2, 37.6, 'Tumbo'), (37.94, 38.36, 'Tumbo'), (38.36, 38.7, 'guarda'), (38.7, 38.76, 'il'), (38.76, 39.22, 'manuale'), (39.58, 39.7, 'Il'), (39.7, 40.08, 'manuale'), (40.08, 40.1, 'è'), (40.1, 40.6, 'mangiato'), (40.96, 41.44, 'Pippo'), (41.44, 41.7, 'tira'), (41.7, 41.84, 'la'), (41.84, 42.1, 'leva'), (42.5, 42.62, 'E'), (42.62, 43.08, "l'aereo"), (43.08, 43.38, 'punta'), (43.38, 43.76, 'dritto'), (43.76, 43.94, 'verso'), (43.94, 44.16, 'la'), (44.16, 44.54, 'città')]]
fix = {}
END = 45.9
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
TITLES = [('MALDIVE!', 2.9, 3.9), ('POLPETTA CON LA CODA', 4.4, 5.9), ('DECOLLO', 6.2, 7.4), ('IL PILOTA', 7.7, 8.6), ('GELATO DA 2 KG', 10.6, 11.8), ('CAGARELLA', 12.1, 13.2),
          ('SPARITO IN BAGNO', 13.6, 14.9), ('AI COMANDI', 15.2, 16.6), ('PILOTA AUTOMATICO', 17.4, 18.7), ('KARAOKE', 19.3, 20.3), ('CARRELLO DELLE BIBITE', 21.3, 22.6), ('COMPRESO', 23.4, 24.4),
          ("L'ANNUNCIO", 25.2, 26.5), ('ALLACCIATE LE CINTURE', 26.8, 27.9), ('COME SI ATTERRA?', 28.3, 29.8), ('SQUILLA IL TELEFONO', 30.1, 31.3), ('ELEONORA', 31.5, 32.2), ('STA PER PARTORIRE!', 34.4, 35.5),
          ('VIENI SUBITO!', 35.6, 36.4), ('IL MANUALE', 38.6, 39.5), ('MANGIATO', 40.0, 40.9), ('LA LEVA', 41.4, 42.3), ('VERSO LA CITTÀ', 43.4, 45.9)]
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
open('t013/captions.ass', 'w').write(hdr + '\n'.join(ev) + '\n')
print(len(ev), 'eventi;', ' | '.join(shown))
