"""Test 009 (Pippo e la zucchina Eleonora) - sottotitoli parola per parola (parolacce censurate) + titoli gialli. Esce t012/captions.ass"""
import json, re
toks = [list(x) for x in [(0.00,0.50,'Pippo'),(0.82,0.96,'quel'),(0.96,1.50,'b******o'),(1.50,2.08,'monopalla'),(2.34,2.52,'si'),(2.52,2.60,'è'),(2.60,3.06,'innamorato'),(3.06,3.24,'di'),(3.24,3.74,'Eleonora!'),
 (4.20,4.84,'Eleonora'),(4.84,4.92,'è'),(4.92,5.06,'una'),(5.06,5.62,'zucchina'),(6.06,6.54,'Pippo'),(6.54,6.86,'prova'),(6.86,7.00,'a'),(7.00,7.14,'darle'),(7.14,7.32,'una'),(7.32,7.64,'rosa'),
 (8.26,8.40,'Lei'),(8.40,8.66,'rimane'),(8.66,9.30,'impassibile'),(9.70,9.82,'E'),(9.82,10.14,'grazie'),(10.14,10.30,'al'),(10.30,10.70,'c***o'),(10.72,10.78,'è'),(10.78,10.88,'una'),(10.88,11.40,'zucchina'),
 (11.52,11.80,'scimmia'),(11.80,11.88,'di'),(11.88,12.32,'m***a!'),(12.86,13.20,'Allora'),(13.20,13.54,'Pippo'),(13.54,13.66,'fa'),(13.66,13.76,'la'),(13.76,13.94,'cosa'),(13.94,14.12,'più'),(14.12,14.52,'logica'),
 (14.92,15.42,'Costruisce'),(15.44,15.62,'una'),(15.62,15.94,'bomba'),(15.94,16.40,'atomica'),(16.82,16.92,'In'),(16.92,17.18,'garage'),(17.52,17.76,'con'),(17.76,17.86,'lo'),(17.86,18.14,'scotch'),
 (18.68,18.78,'E'),(18.78,19.24,'bombarda'),(19.24,19.64,"l'orto"),(19.64,19.74,'del'),(19.74,20.16,'vicino'),(20.34,20.52,'per'),(20.52,21.10,'fare'),(21.10,21.56,'colpo'),
 (21.80,22.36,'Tre'),(22.84,23.14,'Due'),(23.68,23.94,'Uno'),(24.28,24.60,'E'),(24.60,25.14,'funziona'),(25.54,25.66,'La'),(25.66,26.00,'zucchina'),(26.00,26.18,'si'),(26.18,26.56,'alza'),
 (26.88,27.02,'Le'),(27.02,27.44,'spuntano'),(27.44,27.58,'gli'),(27.58,27.96,'occhi'),(28.24,28.36,'La'),(28.36,28.76,'bocca'),(29.10,29.20,'Le'),(29.20,29.64,'gambe'),(30.00,30.12,'E'),(30.12,30.36,'dice'),(30.36,30.78,'sì!'),
 (31.26,31.40,'Si'),(31.40,31.80,'sposano'),(31.80,32.26,'subito'),(32.56,32.72,'In'),(32.72,32.98,'moto'),(33.40,33.48,'E'),(33.48,33.58,'il'),(33.58,33.96,'prete'),(33.96,34.16,'è'),(34.16,34.26,'la'),(34.26,34.56,'moto'),
 (35.06,35.16,'Vi'),(35.16,35.62,'dichiaro'),(35.62,36.06,'marito'),(36.06,36.14,'e'),(36.14,36.64,'zucchina'),(36.94,37.12,'Brum'),(37.12,37.50,'brum'),(37.96,38.22,'Team'),(38.22,38.72,'Pippo'),(38.72,38.92,'o'),(38.92,39.14,'team'),(39.14,39.60,'zucchina?')]]
fix = {}
END = 40.5
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
TITLES = [('INNAMORATO', 2.4, 3.7), ('È UNA ZUCCHINA', 4.3, 5.8), ('UNA ROSA', 6.9, 8.0), ('IMPASSIBILE', 8.5, 9.5), ('È UNA ZUCCHINA!', 10.8, 12.4), ('LA COSA PIÙ LOGICA', 13.2, 14.6),
          ('BOMBA ATOMICA', 15.5, 16.6), ('CON LO SCOTCH', 17.5, 18.5), ("L'ORTO DEL VICINO", 19.0, 20.2), ('PER FARE COLPO', 20.4, 21.7), ('3', 21.85, 22.7), ('2', 22.84, 23.5), ('1', 23.68, 24.0),
          ('E FUNZIONA', 24.4, 25.3), ('SI ALZA', 25.7, 26.7), ('GLI OCCHI', 27.1, 28.1), ('LA BOCCA', 28.3, 29.0), ('LE GAMBE', 29.15, 29.9), ('DICE SÌ!', 30.1, 31.2), ('SPOSI!', 31.4, 32.4),
          ('IN MOTO', 32.6, 33.3), ('IL PRETE È LA MOTO', 33.5, 34.8), ('MARITO E ZUCCHINA', 35.1, 36.8), ('BRUM BRUM', 36.95, 37.8), ('TEAM PIPPO O TEAM ZUCCHINA?', 38.0, 40.5)]
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
open('t012/captions.ass', 'w').write(hdr + '\n'.join(ev) + '\n')
print(len(ev), 'eventi;', ' | '.join(shown))
