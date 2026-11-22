import bpy, time, sys
bpy.ops.wm.open_mainfile(filepath='../t003/pippo_t003.blend'); sc=bpy.context.scene
def run(tag,w,h,sp,f=400):
    sc.render.resolution_x,sc.render.resolution_y=w,h; sc.eevee.taa_render_samples=sp; sc.frame_set(f); sc.render.filepath='/tmp/p.png'
    t=time.time(); bpy.ops.render.render(write_still=True); print('PROF',tag,round(time.time()-t,1),flush=True)
run('warm',135,240,1)
run('tiny1',135,240,1)
run('540x960 sp1',540,960,1)
run('540x960 sp4',540,960,4)
sc.eevee.use_shadows=False
run('noshadow sp4',540,960,4)
sc.eevee.use_shadows=True
for o in bpy.data.objects:
    if o.type=='LIGHT' and o.data.type!='SUN': o.hide_render=True
run('nospot sp4',540,960,4)
print('objs',len(bpy.data.objects),'meshes',sum(1 for o in bpy.data.objects if o.type=='MESH'))
