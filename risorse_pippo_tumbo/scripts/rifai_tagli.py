"""Rifà senza mosso i fotogrammi accanto a ogni stacco di camera (il mosso di Eevee usa le posizioni del fotogramma prima e dopo:
sullo stacco la camera «salta» e l'immagine viene strisciata). Uso: python scripts/rifai_tagli.py tNNN [1080 1920 4]"""
import sys, os, json, bpy
T = sys.argv[-4] if len(sys.argv) >= 5 else sys.argv[-1]
w, h, s = (int(sys.argv[-3]), int(sys.argv[-2]), int(sys.argv[-1])) if len(sys.argv) >= 5 else (1080, 1920, 4)
base = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', T)
shots = json.load(open(os.path.join(base, 'shots.json'))); FPS = 24
fr = lambda t: max(1, int(round(t * FPS)) + 1)
tagli = sorted({f for a, b in shots[1:] for f in (fr(a) - 1, fr(a), fr(a) + 1)})
blend = os.environ.get('BLENDNAME') or [f for f in os.listdir(base) if f.endswith('.blend')][0]
bpy.ops.wm.open_mainfile(filepath=os.path.join(base, blend)); sc = bpy.context.scene
sc.render.resolution_x, sc.render.resolution_y = w, h; sc.eevee.taa_render_samples = s; sc.render.use_motion_blur = False
FATTI = set(int(x) for x in os.environ.get('FATTI', '').split(',') if x)
for f in [f for f in tagli if f not in FATTI]:
    if f > sc.frame_end: continue
    sc.frame_set(f); sc.render.filepath = os.path.join(base, 'final', 'f%04d.png' % f); bpy.ops.render.render(write_still=True); print('rifatto', f)
