"""Video 027: per ogni fotogramma, dove sta la bocca di Pippo sullo schermo (pixel) e quanto e' grande la zona (raggio in pixel).
Serve a componi027_bocca.py per fondere solo un cerchio stretto attorno alla bocca. Toglie dalla scena tutto tranne Pippo e la camera,
cosi' passare 1166 fotogrammi costa pochi secondi. Scrive t027/bocca/centri.json. Uso: python centri027_bocca.py"""
import os, json, bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
QUI = os.path.dirname(os.path.abspath(__file__)); T27 = os.path.join(QUI, '..', 't027')
bpy.ops.wm.open_mainfile(filepath=os.path.join(T27, 'pippo_t027.blend'))
sc = bpy.context.scene; cam = sc.camera; mo = bpy.data.objects['MouthOpen']; head = mo.parent
tieni = {cam}; o = head
while o: tieni.add(o); o = o.parent
for c in cam.constraints:
    if getattr(c, 'target', None): tieni.add(c.target)
for o in list(bpy.data.objects):
    if o not in tieni: bpy.data.objects.remove(o, do_unlink=True)
W, H = 1080, 1920; out = {}
for f in range(1, sc.frame_end + 1):
    sc.frame_set(f); bpy.context.view_layer.update()
    Mh = head.matrix_world; c = Mh @ Vector((0, -0.279, 0.27 - 0.17)); p = world_to_camera_view(sc, cam, c); r = 0.0
    for d in (Vector((0.26, 0, 0)), Vector((-0.26, 0, 0)), Vector((0, 0, 0.2)), Vector((0, 0, -0.2)), Vector((0, -0.1, 0))):
        q = world_to_camera_view(sc, cam, c + Mh.to_3x3() @ d); r = max(r, abs(q.x - p.x) * W, abs(q.y - p.y) * H)
    out[str(f)] = [round(p.x * W, 1), round((1 - p.y) * H, 1), round(r, 1)]
json.dump(out, open(os.path.join(T27, 'bocca', 'centri.json'), 'w')); print('centri', len(out), out['22'], out['250'])
