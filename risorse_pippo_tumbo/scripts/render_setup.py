import bpy, math
from common import *

def setup_render(scene, w, h, samples=16, fps=24, frames=240):
    r = scene.render
    r.engine = 'BLENDER_EEVEE'
    r.resolution_x, r.resolution_y, r.resolution_percentage = w, h, 100
    r.fps = fps
    scene.frame_start, scene.frame_end = 1, frames
    scene.eevee.taa_render_samples = samples
    scene.eevee.use_raytracing = False
    scene.eevee.use_shadows = True
    try: scene.eevee.shadow_ray_count = 1; scene.eevee.shadow_step_count = 6
    except Exception: pass
    scene.view_settings.view_transform = 'Standard'
    scene.view_settings.look = 'None'
    r.image_settings.file_format = 'PNG'
    r.film_transparent = False

def world(scene, top=(0.75, 0.88, 1.0), bottom=(0.95, 0.9, 0.85), strength=0.9):
    w = bpy.data.worlds.new('World'); scene.world = w; w.use_nodes = True
    nt = w.node_tree; nt.nodes.clear()
    tc = nt.nodes.new('ShaderNodeTexCoord'); sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    ramp = nt.nodes.new('ShaderNodeValToRGB'); bg = nt.nodes.new('ShaderNodeBackground')
    out = nt.nodes.new('ShaderNodeOutputWorld')
    mp = nt.nodes.new('ShaderNodeMapRange')
    mp.inputs['From Min'].default_value = -1; mp.inputs['From Max'].default_value = 1
    nt.links.new(tc.outputs['Generated'], sep.inputs[0])   # generated 0..1
    mp.inputs['From Min'].default_value = 0; mp.inputs['From Max'].default_value = 1
    # Generated per il world = direzione normalizzata -> usare Window? usiamo 'Object' coords
    nt.links.new(tc.outputs['Object'], sep.inputs[0])
    mp.inputs['From Min'].default_value = -1
    nt.links.new(sep.outputs['Z'], mp.inputs['Value'])
    nt.links.new(mp.outputs['Result'], ramp.inputs['Fac'])
    ramp.color_ramp.elements[0].color = (*bottom, 1); ramp.color_ramp.elements[1].color = (*top, 1)
    bg.inputs['Strength'].default_value = strength
    nt.links.new(ramp.outputs['Color'], bg.inputs['Color'])
    nt.links.new(bg.outputs['Background'], out.inputs['Surface'])

def area_light(name, loc, target, energy, size, color=(1, 1, 1), coll=None):
    ld = bpy.data.lights.new(name, 'AREA'); ld.energy = energy; ld.size = size; ld.color = color
    o = bpy.data.objects.new(name, ld); o.location = loc
    (coll or bpy.context.scene.collection).objects.link(o)
    d = (target - o.location)
    o.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    return o

def camera(name, loc, target, lens=35, coll=None):
    cd = bpy.data.cameras.new(name); cd.lens = lens; cd.sensor_fit = 'HORIZONTAL'; cd.sensor_width = 36
    cd.clip_start = 0.05; cd.clip_end = 100
    o = bpy.data.objects.new(name, cd); o.location = loc
    (coll or bpy.context.scene.collection).objects.link(o)
    o.rotation_euler = (target - o.location).to_track_quat('-Z', 'Y').to_euler()
    return o
