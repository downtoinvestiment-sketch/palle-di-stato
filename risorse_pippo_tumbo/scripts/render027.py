"""Render finale del video 027: un fotogramma alla volta, saltando quelli gia' fatti (si puo' interrompere e far ripartire).
Ogni PNG viene scritto con un nome provvisorio e rinominato solo quando e' completo: niente fotogrammi a meta'.
Uso: python render027.py [primo-ultimo]      (default: tutti)   Lo fa girare render027.sh, che lo rilancia finche' non ha finito."""
import sys, os, time, bpy
QUI = os.path.dirname(os.path.abspath(__file__)); T27 = os.path.join(QUI, '..', 't027'); OUT = os.path.join(T27, 'final'); os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=os.path.join(T27, 'pippo_t027.blend'))
sc = bpy.context.scene; sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 1080, 1920, 100; sc.render.image_settings.file_format = 'PNG'
a, b = (int(x) for x in sys.argv[-1].split('-')) if len(sys.argv) > 1 and '-' in sys.argv[-1] and sys.argv[-1][0].isdigit() else (1, sc.frame_end)
for f in range(a, b + 1):
    fin = os.path.join(OUT, 'f%04d.png' % f)
    if os.path.exists(fin): continue
    t0 = time.time(); sc.frame_set(f); sc.render.filepath = os.path.join(OUT, 'tmp_f%04d.png' % f); bpy.ops.render.render(write_still=True)
    os.replace(os.path.join(OUT, 'tmp_f%04d.png' % f), fin); print('rendered %d in %.1f s' % (f, time.time() - t0), flush=True)
print('FINITO', flush=True)
