"""Test 009 (il toast di Pippo) - sottotitoli parola per parola (parolacce censurate) + titoli gialli. Esce t014/captions.ass"""
import json, re
toks = [list(x) for x in [(0.0, 0.44, 'Pippo'), (0.44, 0.68, 'vuole'), (0.68, 0.82, 'un'), (0.82, 1.24, 'toast!'), (1.56, 1.86, 'Uno'), (1.86, 2.2, 'solo!'), (2.6, 2.7, 'È'), (2.86, 3.02, 'appena'), (3.02, 3.48, 'distrutto'), (3.48, 3.74, 'mezzo'), (3.74, 4.2, 'pianeta,'), (4.32, 4.4, 'quel'), (4.4, 5.12, 'deficiente!'), (5.8, 6.44, 'Ricominciamo.'), (7.04, 7.52, 'Pippo'), (7.52, 7.82, 'vuole'), (7.82, 7.96, 'un'), (7.96, 8.44, 'toast'), (8.64, 8.78, 'ma'), (8.78, 8.9, 'non'), (8.9, 9.0, 'ha'), (9.0, 9.1, 'il'), (9.1, 9.6, 'tostapane.'), (9.98, 10.32, 'Allora'), (10.32, 10.86, 'costruisce'), (10.86, 10.98, 'un'), (10.98, 11.4, 'c***o'), (11.4, 11.52, 'di'), (11.52, 11.78, 'forno'), (11.78, 12.4, 'industriale.'), (12.9, 13.1, 'Il'), (13.1, 13.4, 'forno'), (13.4, 13.54, 'non'), (13.54, 13.9, 'scalda'), (13.9, 14.52, 'abbastanza.'), (14.94, 15.24, 'Allora'), (15.24, 15.54, 'Pippo'), (15.54, 16.04, 'costruisce'), (16.04, 16.14, 'un'), (16.14, 16.44, 'vulcano'), (16.44, 17.3, 'artificiale.'), (17.42, 17.6, 'In'), (17.6, 18.06, 'giardino.'), (18.32, 18.74, 'Porca'), (18.74, 19.28, 'miseria.'), (19.84, 20.0, 'Il'), (20.0, 20.32, 'vulcano'), (20.32, 20.72, 'scalda'), (20.72, 21.1, 'troppo.'), (21.46, 21.54, 'Si'), (21.54, 21.92, 'sciolgono'), (21.92, 22.08, 'le'), (22.08, 22.24, 'case'), (22.24, 22.42, 'dei'), (22.42, 22.82, 'vicini.'), (23.28, 23.56, 'Allora'), (23.56, 24.08, 'costruisce'), (24.08, 24.16, 'un'), (24.16, 24.58, 'impianto'), (24.58, 24.66, 'di'), (24.66, 25.22, 'raffreddamento'), (25.22, 25.64, 'grande'), (25.64, 25.86, 'come'), (25.86, 26.02, 'uno'), (26.02, 26.48, 'stadio,'), (26.56, 26.68, 'quel'), (26.68, 27.04, 'genio'), (27.04, 27.2, 'del'), (27.2, 27.7, 'c***o'), (27.7, 28.34, 'Serve'), (28.34, 28.76, 'portare'), (28.76, 28.86, 'il'), (28.86, 29.04, 'pane'), (29.04, 29.24, 'fino'), (29.24, 29.38, 'al'), (29.38, 29.78, 'forno,'), (30.06, 30.4, 'catena'), (30.4, 30.5, 'di'), (30.5, 31.04, 'montaggio,'), (31.22, 31.62, 'lunga'), (31.62, 31.72, 'un'), (31.72, 32.32, 'chilometro,'), (32.5, 32.58, 'che'), (32.58, 33.08, 'c***o'), (33.08, 33.2, 'di'), (33.2, 33.6, 'senso'), (33.6, 33.76, 'ha.'), (34.16, 34.3, 'Ma'), (34.3, 34.4, 'la'), (34.4, 34.68, 'fetta'), (34.68, 34.74, 'è'), (34.74, 35.1, 'troppo'), (35.1, 35.5, 'piccola'), (35.5, 35.64, 'per'), (35.64, 35.76, 'la'), (35.76, 36.2, 'macchina,'), (36.54, 36.74, 'allora'), (36.74, 37.1, 'Pippo'), (37.1, 37.58, 'costruisce'), (37.58, 37.68, 'una'), (37.68, 38.06, 'fetta'), (38.06, 38.14, 'di'), (38.14, 38.34, 'pane'), (38.34, 38.98, 'gigante,'), (39.16, 39.48, 'grande'), (39.48, 39.68, 'come'), (39.68, 39.82, 'un'), (39.82, 40.24, 'camion.'), (40.74, 40.9, 'Il'), (40.9, 41.18, 'toast'), (41.18, 41.28, 'è'), (41.28, 41.48, 'pronto,'), (41.94, 42.5, 'perfetto,'), (42.76, 43.22, 'dorato,'), (43.48, 44.02, 'fumante.'), (44.44, 44.82, 'Tumbo'), (44.82, 44.98, 'se'), (44.98, 45.1, 'lo'), (45.1, 45.36, 'mangia'), (45.36, 45.44, 'in'), (45.44, 45.52, 'un'), (45.52, 46.0, 'boccone,'), (46.3, 46.6, 'Pippo'), (46.6, 46.88, 'resta'), (46.88, 46.98, 'con'), (46.98, 47.12, 'una'), (47.12, 47.58, 'briciola,'), (47.78, 47.92, 'quel'), (47.92, 48.46, 'c******e')]]
fix = {}
END = 49.7
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
TITLES = [('UN TOAST', 0.5, 1.5), ('MEZZO PIANETA', 3.2, 4.4), ('RICOMINCIAMO', 5.8, 6.6), ('NIENTE TOSTAPANE', 8.8, 9.9), ('FORNO INDUSTRIALE', 10.6, 12.6), ('NON SCALDA', 13.0, 14.8),
          ('VULCANO ARTIFICIALE', 15.6, 17.4), ('IN GIARDINO', 17.5, 18.2), ('SCALDA TROPPO', 20.0, 21.4), ('CASE SCIOLTE', 21.5, 23.0), ('RAFFREDDAMENTO', 24.0, 25.4), ('GRANDE COME UNO STADIO', 25.5, 27.6),
          ('CATENA DI MONTAGGIO', 30.0, 31.2), ('1 KM', 31.2, 32.4), ('TROPPO PICCOLA', 34.7, 36.4), ('FETTA GIGANTE', 37.6, 39.1), ('GRANDE COME UN CAMION', 39.2, 40.6), ('PRONTO!', 40.9, 41.9),
          ('PERFETTO', 41.95, 42.7), ('DORATO', 42.76, 43.4), ('FUMANTE', 43.48, 44.3), ('UN BOCCONE', 45.0, 46.2), ('UNA BRICIOLA', 46.9, 47.9), ('C******E', 47.95, 49.7)]
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
open('t014/captions.ass', 'w').write(hdr + '\n'.join(ev) + '\n')
print(len(ev), 'eventi;', ' | '.join(shown))
