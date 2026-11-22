"""Compone le schede di scelta 3 (altre cose del pacchetto) con etichette: python3 sheet_opts3.py [cose enormi posti animali]"""
import os, sys
from PIL import Image, ImageDraw, ImageFont
OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../t016/opt3')); DST = os.path.abspath(os.path.join(os.path.dirname(__file__), '../out'))
def font(sz):
    for p in ('/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'):
        if os.path.exists(p): return ImageFont.truetype(p, sz)
    return ImageFont.load_default()
SHEETS = {
 'cose': ('L · COSE ASSURDE', [('L1', 'ambulanza'), ('L2', 'trattore'), ('L3', 'kart'), ('L4', 'vasca da bagno'), ('L5', 'water'), ('L6', 'frigorifero'), ('L7', 'torta gigante'), ('L8', 'ciambella gigante'), ('L9', 'tacchino gigante')]),
 'enormi': ('M · COSE ENORMI', [('M1', 'nave pirata'), ('M2', 'transatlantico'), ('M3', 'locomotiva'), ('M4', 'razzo'), ('M5', 'meteorite'), ('M6', 'catapulta'), ('M7', 'cannone'), ('M8', 'bara'), ('M9', 'pupazzo di neve')]),
 'posti': ('N · POSTI NUOVI (rifatti)', [('N1', 'cimitero'), ('N2', 'luna'), ('N3', 'isola dei pirati'), ('N4', 'castello'), ('N5', 'neve'), ('N6', 'campeggio nel bosco'), ('N7', 'centro città'), ('N8', 'porto'), ('N9', 'stazione')]),
 'posti2': ('N · POSTI RIFATTI (più ricchi)', [('N3', 'isola dei pirati'), ('N6', 'campeggio nel bosco'), ('N7', 'centro città')]),
 'animali': ('O · ANIMALI FATTI A MANO', [('O1', 'mucca'), ('O2', 'elefante'), ('O3', 'pinguino'), ('O4', 'giraffa'), ('O5', 'maiale'), ('O6', 'leone'), ('O7', 'scimmia'), ('O8', 'pulcino'), ('O9', 'granchio')]),
}
TW, COLS, PAD, BAR = 352, 3, 6, 54
for key in ([a for a in sys.argv[1:] if a in SHEETS] or list(SHEETS)):
    TH = 626 if key.startswith('posti') else 352
    title, items = SHEETS[key]; items = [(c, n) for c, n in items if os.path.exists(os.path.join(OUT, c + '.png'))]
    if not items: continue
    rows = (len(items) + COLS - 1) // COLS; W = COLS * TW + (COLS + 1) * PAD; H = 70 + rows * (TH + BAR + PAD) + PAD
    S = Image.new('RGB', (W, H), (18, 18, 22)); d = ImageDraw.Draw(S); d.text((PAD + 4, 12), title, font=font(38), fill=(255, 214, 10))
    for i, (c, n) in enumerate(items):
        x = PAD + (i % COLS) * (TW + PAD); y = 70 + (i // COLS) * (TH + BAR + PAD)
        S.paste(Image.open(os.path.join(OUT, c + '.png')).convert('RGB').resize((TW, TH), Image.LANCZOS), (x, y + BAR))
        d.rectangle((x, y, x + TW, y + BAR), fill=(255, 214, 10)); d.text((x + 8, y + 6), c, font=font(30), fill=(0, 0, 0)); d.text((x + 62, y + 14), n, font=font(19), fill=(0, 0, 0))
    S.save(os.path.join(DST, 'scelta3_%s.png' % key)); print('ok', key, S.size)
