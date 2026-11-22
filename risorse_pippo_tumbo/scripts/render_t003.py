import sys, os, bpy
sys.path.insert(0, os.path.dirname(__file__))
blend, outdir, w, h, samples = sys.argv[-6], sys.argv[-5], int(sys.argv[-4]), int(sys.argv[-3]), int(sys.argv[-2])
a_=sys.argv[-1]
frames = list(range(int(a_.split('-')[0]), int(a_.split('-')[1]) + 1)) if '-' in a_ else [int(x) for x in a_.split(',')]
bpy.ops.wm.open_mainfile(filepath=blend)
sc = bpy.context.scene
sc.render.resolution_x, sc.render.resolution_y = w, h
sc.eevee.taa_render_samples = samples
os.makedirs(outdir, exist_ok=True)
for f in frames:
    if os.path.exists(os.path.join(outdir, f'f{f:04d}.png')): continue
    sc.frame_set(f)
    sc.render.filepath = os.path.join(outdir, f'f{f:04d}.png')
    bpy.ops.render.render(write_still=True)
    print('rendered', f)
