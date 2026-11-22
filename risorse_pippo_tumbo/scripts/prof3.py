import bpy, time
bpy.ops.wm.open_mainfile(filepath='../t004/pippo_t004.blend'); sc=bpy.context.scene
sc.render.resolution_x,sc.render.resolution_y=720,1280; sc.eevee.taa_render_samples=4
for f in (300,500,700,900,1050):
    sc.frame_set(f); sc.render.filepath='/tmp/p3.png'; t=time.time(); bpy.ops.render.render(write_still=True); print('PROF',f,round(time.time()-t,1),flush=True)
