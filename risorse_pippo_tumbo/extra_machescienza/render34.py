"""Render di pop34.blend: una scena per processo (le altre vengono tolte, cosi' e' quella attiva). Salta i fotogrammi fatti.
Uso: python3 render34.py DIR SCENA [primo-ultimo | f1,f2,...] [pct]"""
import sys, os, time, json, bpy
QUI = os.path.dirname(os.path.abspath(__file__))
a = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:]
OUT = os.path.abspath(a[0]); os.makedirs(OUT, exist_ok=True); NOME = a[1]
REG = json.load(open(os.path.join(QUI, 'regimi.json')))
mie = [f for p, q, n in REG if n == NOME for f in range(p, q + 1)]
if len(a) > 2 and ',' in a[2]: fs = [int(x) for x in a[2].split(',')]
elif len(a) > 2 and '-' in a[2]: p, q = a[2].split('-'); fs = range(int(p), int(q) + 1)
else: fs = mie
fs = [f for f in fs if f in mie and not os.path.exists(os.path.join(OUT, 'f%04d.png' % f))]
if not fs: print('FINITO', flush=True); sys.exit(0)
bpy.ops.wm.open_mainfile(filepath=os.path.join(QUI, 'pop34.blend'))
for sc in list(bpy.data.scenes):
    if sc.name != NOME: bpy.data.scenes.remove(sc)
sc = bpy.context.scene; assert sc.name == NOME, sc.name
sc.render.resolution_percentage = int(a[3]) if len(a) > 3 else 100; sc.render.image_settings.file_format = 'PNG'
for f in fs:
    fin = os.path.join(OUT, 'f%04d.png' % f)
    if os.path.exists(fin): continue
    t0 = time.time(); sc.frame_set(f); tmp = os.path.join(OUT, 'tmp_f%04d.png' % f); sc.render.filepath = tmp; bpy.ops.render.render(write_still=True)
    os.replace(tmp, fin); print('rendered %d (%s) in %.1f s' % (f, NOME, time.time() - t0), flush=True)
print('FINITO', flush=True)
