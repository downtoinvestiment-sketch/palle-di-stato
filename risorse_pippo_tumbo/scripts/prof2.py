import bpy, time
bpy.ops.wm.open_mainfile(filepath='../t003/pippo_t003.blend'); sc=bpy.context.scene
print('PROPS',[p for p in dir(sc.eevee) if 'shadow' in p or 'ray' in p or 'fast' in p or 'light' in p])
def run(tag,w=540,h=960,sp=4,f=400):
    sc.render.resolution_x,sc.render.resolution_y=w,h; sc.eevee.taa_render_samples=sp; sc.frame_set(f); sc.render.filepath='/tmp/p_%s.png'%tag.replace(' ','_')
    t=time.time(); bpy.ops.render.render(write_still=True); print('PROF',tag,round(time.time()-t,1),flush=True)
run('warm',135,240,1)
for o in bpy.data.objects:
    if o.type=='LIGHT' and o.data.type!='SUN': o.data.use_shadow=False
run('spots noshadow')
try: sc.eevee.shadow_resolution_scale=0.25
except Exception as e: print(e)
run('res .25')
try: sc.eevee.shadow_ray_count=1; sc.eevee.shadow_step_count=1
except Exception as e: print(e)
run('steps1')
sc.eevee.use_shadows=False
run('noshadows')
