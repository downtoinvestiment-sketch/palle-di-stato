"""Scheda delle luci della sala parto (video 017): gli stessi fotogrammi con le varianti A (com'e' adesso), B, C, D, una colonna per variante.
Uso: python scheda_luci017.py   (A viene dai fotogrammi finali in ../t017/final, le altre da ../t017/luci/<lettera>; scrive ../out/luci017.png)"""
import os, sys
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); T = os.path.join(HERE, '../t017'); FD = os.path.join(HERE, '../assets/font')
FR = [int(x) for x in (sys.argv[1].split(',') if len(sys.argv) > 1 else '1,40,176,242,472,621'.split(','))]
VAR = [v.split('=') for v in (sys.argv[2].split(',') if len(sys.argv) > 2 else 'A=Adesso,B=Sole caldo,C=Cinema,D=Morbida calda'.split(','))]
OUT = sys.argv[3] if len(sys.argv) > 3 else os.path.join(HERE, '../out/luci017.png')
TW, TH, HH = 1080 // len(VAR), int(1080 // len(VAR) * 16 / 9), 70
fn = ImageFont.truetype(os.path.join(FD, 'Poppins-Black.ttf'), 34); fc = ImageFont.truetype(os.path.join(FD, 'Poppins-ExtraBold.ttf'), 20)
M = Image.new('RGB', (TW * len(VAR), HH + TH * len(FR)), (18, 18, 22)); d = ImageDraw.Draw(M)
for c, (let, name) in enumerate(VAR):
    d.rectangle((c * TW + 8, 8, c * TW + 60, 60), fill=(255, 214, 0)); d.text((c * TW + 34, 34), let, font=fn, fill=(0, 0, 0), anchor='mm'); d.text((c * TW + 70, 34), name, font=fc, fill=(255, 255, 255), anchor='lm')
    for r, f in enumerate(FR):
        p = os.path.join(T, 'final' if let == 'A' else 'luci/' + let, 'f%04d.png' % f)
        if os.path.exists(p): M.paste(Image.open(p).convert('RGB').resize((TW, TH), Image.LANCZOS), (c * TW, HH + r * TH))
        d.rectangle((c * TW, HH + r * TH, c * TW + TW - 1, HH + r * TH + TH - 1), outline=(18, 18, 22), width=2)
M.save(OUT); print(OUT, M.size)
