"""Mosaico dei fotogrammi di prova. Uso: python templates/mosaico_frames.py cartella uscita.png colonne [larghezza] [f1,f2,...]"""
import sys, glob, os
from PIL import Image, ImageDraw
d, out, cols = sys.argv[1], sys.argv[2], int(sys.argv[3]); tw = int(sys.argv[4]) if len(sys.argv) > 4 else 270
fs = sorted(glob.glob(os.path.join(d, 'f*.png')))
if len(sys.argv) > 5: want = set(int(x) for x in sys.argv[5].split(',')); fs = [f for f in fs if int(os.path.basename(f)[1:5]) in want]
ims = [Image.open(f).convert('RGB') for f in fs]; th = int(tw * ims[0].size[1] / ims[0].size[0]); rows = (len(ims) + cols - 1) // cols
M = Image.new('RGB', (tw * cols, th * rows), (20, 20, 20)); dr = ImageDraw.Draw(M)
for i, (f, im) in enumerate(zip(fs, ims)):
    x, y = (i % cols) * tw, (i // cols) * th; M.paste(im.resize((tw, th), Image.LANCZOS), (x, y)); dr.text((x + 4, y + 4), '%d  %s' % (i + 1, os.path.basename(f)[1:5]), fill=(255, 255, 0))
M.save(out); print(out, M.size)
