"""Montaggio ep33 v2 (raddoppi): fotogrammi 720x1280 (frames34) -> 1080x1920, domanda al centro, contatore dell'altezza con «×2», scritte, canzone originale, 30 fps.
Uso: python3 monta34.py [prova.jpg v]  -> out/macheScienza_ep33-raddoppia_loop.mp4"""
import os, sys, subprocess, math, json
from PIL import Image, ImageDraw, ImageFont, ImageFilter
QUI = os.path.dirname(os.path.abspath(__file__)); FR = os.environ.get('FR34', os.path.join(QUI, 'frames34')); OUT = os.path.join(QUI, 'out'); os.makedirs(OUT, exist_ok=True)
FONT = '/home/claude/curiosita/engine/fonts/LilitaOne-Regular.ttf'; SONG = '/home/claude/ptv/audio/canzone_t027.m4a'
FPS = 24; OFF = 40; DUR = float(os.environ.get('DUR34', '46.0')); W, H = 1080, 1920
GIALLO = (255, 216, 74); BIANCO = (255, 255, 255); BORDO = (20, 12, 30)
RD = json.load(open(os.path.join(QUI, 'blender', 'raddoppi.json'))); D = [None] + RD['D']; T_BH = RD['T_BH']
DOMANDA = (0.0, D[1] - 0.02, "Cosa succederebbe se una popstar [raddoppiasse] la sua altezza?")
TESTI = [
    (D[1], D[4], "Mandalo a chi canta sempre sotto la doccia."),
    (D[5], D[9], "Ogni raddoppio pesa [8 volte] di più: le ginocchia scricchiolano."),
    (D[9], D[13] - 0.07, "Più alto del [Burj Khalifa]…"),
    (D[13], 15.8, "…e dell'[Everest]!"),
    (15.8, 18.9, "Sopra i [19 km] la saliva bollirebbe in bocca."),
    (18.9, 21.6, "È già [nello spazio]."),
    (D[23], D[26], "Più grande della [Terra]."),
    (D[28], D[29] + 0.48, "Arriva alla [Luna]."),
    (D[30], D[31] - 0.05, "Grande come il [Sole]…"),
    (D[32], D[35], "…e pesa più del Sole."),
    (D[38], T_BH - 0.05, "Più grande dell'[orbita della Terra]."),
    (T_BH, 43.6, "Troppa massa: diventa un [buco nero]. Neanche la luce può uscire."),
    (43.6, DUR + 0.1, "…ma la canzone ti resta in testa lo stesso."),
]

def parole(testo):
    out = []; giallo = False
    for tok in testo.replace('[', ' [ ').replace(']', ' ] ').split():
        if tok == '[': giallo = True
        elif tok == ']': giallo = False
        elif out and tok in '?.,:…!' and len(tok) == 1: out[-1] = (out[-1][0] + tok, out[-1][1])
        else: out.append((tok, giallo))
    return out

def cartello(testo, size=94, maxw=940, scatola=False):
    f = ImageFont.truetype(FONT, size); sp = f.getlength(' '); righe = [[]]; lw = 0
    for p, g in parole(testo):
        wpx = f.getlength(p)
        if righe[-1] and lw + sp + wpx > maxw: righe.append([]); lw = 0
        lw += (sp if righe[-1] else 0) + wpx; righe[-1].append((p, g, wpx))
    lh = int(size * 1.12); hh = lh * len(righe) + 50
    im = Image.new('RGBA', (W, hh), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    if scatola:
        larg = max(sum(x[2] for x in r) + sp * (len(r) - 1) for r in righe)
        d.rounded_rectangle(((W - larg) / 2 - 40, 4, (W + larg) / 2 + 40, hh - 4), radius=38, fill=(15, 8, 30, 175))
    for i, r in enumerate(righe):
        tot = sum(x[2] for x in r) + sp * (len(r) - 1); x = (W - tot) / 2; y = 22 + i * lh
        for p, g, wpx in r:
            d.text((x, y), p, font=f, fill=GIALLO if g else BIANCO, stroke_width=9, stroke_fill=BORDO); x += wpx + sp
    om = Image.new('RGBA', im.size, (0, 0, 0, 0)); om.putalpha(im.getchannel('A').filter(ImageFilter.GaussianBlur(10)).point(lambda a: int(a * 0.5)))
    sh = Image.new('RGBA', im.size, (0, 0, 0, 0)); sh.paste(om, (0, 8)); return Image.alpha_composite(sh, im)

def misura(n):
    h = 1.8 * 2 ** n
    def it(x, dec): return ('%.*f' % (dec, x)).replace('.', ',')
    def mig(x): return '{:,}'.format(int(x)).replace(',', '.')
    def sig3(x):
        e = 10 ** max(0, int(math.floor(math.log10(x))) - 2); return round(x / e) * e
    if h < 10: return it(h, 1) + ' m'
    if h < 1000: return mig(sig3(h)) + ' m'
    k = h / 1000
    if k < 10: return it(k, 1) + ' km'
    if k < 1e6: return mig(sig3(k)) + ' km'
    m = k / 1e6
    if m < 1000: return (it(m, 1) if m < 10 else mig(sig3(m))) + ' milioni di km'
    g = m / 1000; return (it(g, 1) if g < 10 and abs(g - round(g)) > 0.05 else mig(round(g))) + ' miliardi di km'

CART = [(a, b, cartello(t)) for a, b, t in TESTI]
CDOM = cartello(DOMANDA[2], size=104, maxw=900, scatola=True)
CONT = {}
def contatore(n):
    if n not in CONT:
        t = misura(n); size = 112 if len(t) < 12 else (96 if len(t) < 16 else 84)
        f = ImageFont.truetype(FONT, size); im = Image.new('RGBA', (W, size + 50), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        wpx = f.getlength(t); d.text(((W - wpx) / 2, 18), t, font=f, fill=GIALLO, stroke_width=10, stroke_fill=BORDO); CONT[n] = im
    return CONT[n]
F2 = ImageFont.truetype(FONT, 120)
X2 = Image.new('RGBA', (360, 190), (0, 0, 0, 0)); ImageDraw.Draw(X2).text((30, 20), '×2', font=F2, fill=BIANCO, stroke_width=11, stroke_fill=(200, 30, 110))
Y_TESTO = 300; Y_CONT = 110

def pop(c, k): return c.resize((max(1, int(c.width * k)), max(1, int(c.height * k))), Image.LANCZOS)
def metti(im, c, cx, cy, k=1.0, al=1.0):
    cc = pop(c, k) if abs(k - 1) > 1e-3 else c
    if al < 1: cc = cc.copy(); cc.putalpha(cc.getchannel('A').point(lambda x: int(x * al)))
    im.alpha_composite(cc, (int(cx - cc.width / 2), int(cy - cc.height / 2)))

def componi(v):
    f = min(OFF + 1 + int(round(v * FPS)), OFF + int(round(46.0 * FPS)))
    im = Image.open(os.path.join(FR, 'f%04d.png' % f)).convert('RGB').resize((W, H), Image.LANCZOS).convert('RGBA')
    a, b, _ = DOMANDA
    if a <= v < b:
        u = min(1.0, v / 0.25); k = 0.85 + 0.15 * (1 - (1 - u) ** 3) + 0.04 * math.sin(math.pi * u); al = min(1.0, v / 0.12 + 0.3, (b - v) / 0.15)
        metti(im, CDOM, W / 2, 820, k, al)
    n = sum(1 for k_ in range(1, 43) if D[k_] <= v)
    if 2.4 <= v < T_BH:
        u = (v - D[n]) / 0.22 if n else 1.0; k = 1.0 + (0.25 * math.sin(math.pi * min(1.0, u)) if n and u < 1 else 0.0)
        c = contatore(n); metti(im, c, W / 2, Y_CONT + c.height / 2, k, min(1.0, (v - 2.4) / 0.2))
        if n and v - D[n] < 0.5:
            q = (v - D[n]) / 0.5; metti(im, X2, W / 2 + 330, Y_CONT + 60 - 40 * q, 0.7 + 0.5 * math.sin(math.pi * min(1, q * 1.4)), 1 - q ** 3)
    for a, b, c in CART:
        if a <= v < b:
            u = min(1.0, (v - a) / 0.16); k = 0.82 + 0.18 * (1 - (1 - u) ** 3) + 0.05 * math.sin(math.pi * u)
            al = min(1.0, (v - a) / 0.08, (b - v) / 0.12)
            metti(im, c, W / 2, Y_TESTO + 150 + c.height / 2 - 150, k, al)
    return im.convert('RGB')

if __name__ == '__main__':
    if len(sys.argv) > 2:
        componi(float(sys.argv[2])).save(sys.argv[1], quality=90); sys.exit(0)
    dst = os.environ.get('DST34', os.path.join(OUT, 'macheScienza_ep33-raddoppia_loop.mp4')); n = int(round(DUR * FPS))
    cmd = ['ffmpeg', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '%dx%d' % (W, H), '-r', str(FPS), '-i', '-',
           '-ss', '%.4f' % (OFF / FPS), '-t', '%.3f' % DUR, '-i', SONG,
           '-filter_complex', '[0:v]fps=30[v];[1:a]afade=t=in:d=0.03,afade=t=out:st=%.2f:d=0.25[a]' % (DUR - 0.25),
           '-map', '[v]', '-map', '[a]', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p',
           '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', '-t', '%.3f' % DUR, dst]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(n): p.stdin.write(componi(i / FPS).tobytes())
    p.stdin.close(); p.wait(); print('FATTO', dst)
