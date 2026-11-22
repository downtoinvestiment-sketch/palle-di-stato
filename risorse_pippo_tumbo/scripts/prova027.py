"""Fotogrammi di prova del video 027, a meta' risoluzione, e foglio riassuntivo.
Uso: python prova027.py rendi T1 T2 ...     -> ../out/prova027/p_SSSS.png (S = centesimi di secondo)
     python prova027.py foglio [colonne]    -> ../out/prova027/foglio.jpg (tutti i p_*.png in ordine di tempo)"""
import sys, os, time, glob
QUI = os.path.dirname(os.path.abspath(__file__)); OUT = os.environ.get('OUT027', os.path.join(QUI, '..', 'out', 'prova027')); os.makedirs(OUT, exist_ok=True)
if sys.argv[1] == 'rendi':
    import bpy
    bpy.ops.wm.open_mainfile(filepath=os.environ.get('BLEND027', os.path.join(QUI, '..', 't027', 'pippo_t027.blend')))
    sc = bpy.context.scene; sc.render.resolution_percentage = int(os.environ.get('PERC', '50')); sc.render.image_settings.file_format = 'PNG'
    for a in sys.argv[2:]:
        t = float(a); f = int(round(t * 24)) + 1; t0 = time.time()
        sc.frame_set(f); sc.render.filepath = os.path.join(OUT, 'p_%04d.png' % int(round(t * 100))); bpy.ops.render.render(write_still=True)
        print('FATTO %.2f s (fotogramma %d) in %.1f s' % (t, f, time.time() - t0), flush=True)
else:
    from PIL import Image, ImageDraw
    col = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    fs = sorted(glob.glob(os.path.join(OUT, 'p_*.png'))); ims = [Image.open(f).convert('RGB') for f in fs]
    W, H = 300, 533; rows = (len(ims) + col - 1) // col
    im = Image.new('RGB', (W * col, H * rows), (20, 20, 20)); d = ImageDraw.Draw(im)
    for i, (f, x) in enumerate(zip(fs, ims)):
        im.paste(x.resize((W, H)), ((i % col) * W, (i // col) * H))
        d.text(((i % col) * W + 6, (i // col) * H + 4), '%.2f s' % (int(os.path.basename(f)[2:6]) / 100.0), fill=(255, 255, 0))
    im.save(os.path.join(OUT, 'foglio.jpg'), quality=86); print('foglio', len(ims))
