"""Schede dei fotogrammi di prova del video 017 da far approvare all'autore: 3 fogli da 9 scene (con il numero e la frase della voce) e un foglio con i font dei sottotitoli.
Uso: python scheda_scene017.py   (legge ../t017/test/fNNNN.png, scrive ../out/scene017_1.png ... e ../out/font017.png)"""
import os
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); TEST = os.path.join(HERE, '../t017/test'); OUT = os.path.join(HERE, '../out'); FD = os.path.join(HERE, '../assets/font')
os.makedirs(OUT, exist_ok=True)
SCENE = [(1, 'Un camion dei pompieri...'), (40, '...è appena entrato in una zucchina!'), (123, 'E non è più uscito, c***o.'), (176, 'Eleonora deve partorire. Ma il bambino non esce.'), (242, 'Pippo bussa. «Occupato.»'),
         (289, 'Allora prova con un panino.'), (348, 'Esce una manina. Prende il panino.'), (407, 'Quindi manda dentro Tumbo.'), (443, 'Tumbo non torna.'), (472, 'Chiama la polizia!'), (499, 'Entra un agente.'),
         (525, 'Non torna.'), (552, 'Chiama i pompieri!'), (578, 'Entra tutto il camion!'), (621, 'Indovinate.'), (652, 'Allora entra Pippo.'), (696, 'Ma che c***o...'), (728, 'Una discoteca!'),
         (761, 'Duecento neonati!'), (792, 'Il poliziotto balla!'), (827, 'E il DJ è Tumbo!'), (874, "All'ingresso, il buttafuori..."), (915, '...Gualtiero.'), (942, 'Pippo non è in lista.'), (970, '(finale)')]
TW, TH, CH = 360, 640, 64
fn = ImageFont.truetype(os.path.join(FD, 'Poppins-Black.ttf'), 30); fc = ImageFont.truetype(os.path.join(FD, 'Poppins-ExtraBold.ttf'), 19)
def wrap(d, text, font, width):
    out, line = [], ''
    for w in text.split():
        t = (line + ' ' + w).strip()
        if d.textlength(t, font=font) <= width: line = t
        else: out.append(line); line = w
    return out + [line]
for s in range(3):
    part = SCENE[s * 9:(s + 1) * 9]; rows = (len(part) + 2) // 3
    M = Image.new('RGB', (TW * 3, (TH + CH) * rows), (18, 18, 22)); d = ImageDraw.Draw(M)
    for i, (f, txt) in enumerate(part):
        x, y = (i % 3) * TW, (i // 3) * (TH + CH); im = Image.open(os.path.join(TEST, 'f%04d.png' % f)).convert('RGB').resize((TW, TH), Image.LANCZOS); M.paste(im, (x, y))
        n = s * 9 + i + 1; d.rectangle((x + 8, y + 8, x + 62, y + 50), fill=(255, 214, 0)); d.text((x + 35, y + 29), str(n), font=fn, fill=(0, 0, 0), anchor='mm')
        for k, ln in enumerate(wrap(d, txt, fc, TW - 16)[:2]): d.text((x + TW // 2, y + TH + 18 + k * 24), ln, font=fc, fill=(255, 255, 255), anchor='mm')
        d.rectangle((x, y, x + TW - 1, y + TH + CH - 1), outline=(18, 18, 22), width=2)
    p = os.path.join(OUT, 'scene017_%d.png' % (s + 1)); M.save(p); print(p, M.size)
# font dei sottotitoli: stessa scena, stessa parola, sei font
FONTS = [('A', 'Poppins (quello di adesso)', 'Poppins-Black.ttf'), ('B', 'Luckiest Guy', 'LuckiestGuy-Regular.ttf'), ('C', 'Bangers', 'Bangers-Regular.ttf'), ('D', 'Titan One', 'TitanOne-Regular.ttf'), ('E', 'Lilita One', 'LilitaOne-Regular.ttf'), ('F', 'Anton', 'Anton-Regular.ttf')]
base = Image.open(os.path.join(TEST, 'f0123.png')).convert('RGB').resize((TW, TH), Image.LANCZOS)
M = Image.new('RGB', (TW * 3, (TH + 40) * 2), (18, 18, 22)); d = ImageDraw.Draw(M)
for i, (let, name, file) in enumerate(FONTS):
    x, y = (i % 3) * TW, (i // 3) * (TH + 40); M.paste(base, (x, y))
    fw = ImageFont.truetype(os.path.join(FD, file), 58); ft = ImageFont.truetype(os.path.join(FD, file), 34)
    d.text((x + TW // 2, y + 330), 'ZUCCHINA!', font=fw, fill=(255, 255, 255), anchor='mm', stroke_width=5, stroke_fill=(0, 0, 0))
    d.text((x + TW // 2, y + 96), 'NON ESCE PIÙ', font=ft, fill=(255, 214, 0), anchor='mm', stroke_width=4, stroke_fill=(0, 0, 0))
    d.rectangle((x + 8, y + 8, x + 62, y + 50), fill=(255, 214, 0)); d.text((x + 35, y + 29), let, font=fn, fill=(0, 0, 0), anchor='mm')
    d.text((x + TW // 2, y + TH + 20), name, font=fc, fill=(255, 255, 255), anchor='mm')
p = os.path.join(OUT, 'font017.png'); M.save(p); print(p, M.size)
