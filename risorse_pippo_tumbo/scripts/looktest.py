import bpy, sys
bpy.ops.wm.open_mainfile(filepath='../t003/pippo_t003.blend'); sc=bpy.context.scene
sc.render.resolution_x,sc.render.resolution_y=360,640; sc.eevee.taa_render_samples=3
print('LOOKS',[i.identifier for i in sc.view_settings.bl_rna.properties['look'].enum_items][:20])
for tag,vt,lk in (('std','Standard','None'),('agx','AgX','None'),('punchy','AgX','AgX - Punchy')):
    sc.view_settings.view_transform=vt
    try: sc.view_settings.look=lk
    except Exception as e: print(e)
    sc.frame_set(1+round(2.0*24)); sc.render.filepath='/tmp/lk_%s.png'%tag; bpy.ops.render.render(write_still=True)
