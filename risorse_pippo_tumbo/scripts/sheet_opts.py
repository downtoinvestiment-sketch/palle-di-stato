"""Compone le schede di scelta con etichette: python3 sheet_opts.py"""
import os, sys
from PIL import Image, ImageDraw, ImageFont
OUT = os.path.abspath('../t016/opt'); DST = os.path.abspath('../out')
def font(sz):
    for p in ('/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'):
        if os.path.exists(p): return ImageFont.truetype(p, sz)
    return ImageFont.load_default()
SHEETS = {
 'alberi': ('A · ALBERI', [('A1', 'alberello'), ('A2', 'albero largo'), ('A3', 'albero contorto'), ('A4', 'albero basso'), ('A5', 'abete'), ('A6', 'albero africano'), ('A7', 'jacaranda'), ('A8', 'pino'), ('A9', 'cartoon a palla')]),
 'prato': ('B · PRATO', [('B1', 'prato folto'), ('B2', 'prato scuro'), ('B3', 'prato secco'), ('B4', 'prato fine'), ('B5', 'prato chiaro'), ('B6', 'colore piatto')]),
 'muri': ('C · MURI', [('C1', 'intonaco liscio'), ('C2', 'intonaco dipinto'), ('C3', 'intonaco grezzo'), ('C4', 'mattoni verdi'), ('C5', 'mattoni rossi'), ('C6', 'doghe di legno'), ('C7', 'pietra'), ('C8', 'colore piatto')]),
 'tetti': ('D · TETTI', [('D1', 'tegole rosse'), ('D2', 'coppi'), ('D3', 'tegole con muschio'), ('D4', 'ardesia'), ('D5', 'tegole scure'), ('D6', 'tegole vecchie'), ('D7', 'colore piatto')]),
 'cielo': ('E · CIELO', [('E1', 'blu con nuvole'), ('E2', 'nuvole grandi'), ('E3', 'blu limpido'), ('E4', 'blu intenso'), ('E5', 'velato'), ('E6', 'tramonto rosa')]),
}
TW, TH, COLS, PAD, BAR = 352, 626, 3, 6, 54
for key in (sys.argv[1:] or list(SHEETS)):
    title, items = SHEETS[key]; items = [(c, n) for c, n in items if os.path.exists(os.path.join(OUT, c + '.png'))]
    if not items: continue
    rows = (len(items) + COLS - 1) // COLS; W = COLS * TW + (COLS + 1) * PAD; H = 70 + rows * (TH + BAR + PAD) + PAD
    S = Image.new('RGB', (W, H), (18, 18, 22)); d = ImageDraw.Draw(S); d.text((PAD + 4, 12), title, font=font(38), fill=(255, 214, 10))
    for i, (c, n) in enumerate(items):
        x = PAD + (i % COLS) * (TW + PAD); y = 70 + (i // COLS) * (TH + BAR + PAD)
        S.paste(Image.open(os.path.join(OUT, c + '.png')).convert('RGB').resize((TW, TH), Image.LANCZOS), (x, y + BAR))
        d.rectangle((x, y, x + TW, y + BAR), fill=(255, 214, 10)); d.text((x + 8, y + 6), c, font=font(30), fill=(0, 0, 0)); d.text((x + 62, y + 14), n, font=font(19), fill=(0, 0, 0))
    S.save(os.path.join(DST, 'scelta_%s.png' % key)); print('ok', key, S.size)
