"""Video 027: rifa' solo la zona della testa di Pippo (bocca corretta) su ogni fotogramma, con il «bordo» di render: molto piu' veloce
del fotogramma intero. Scrive t027/bocca/b%04d.png (immagine intera, nero fuori dal bordo) e t027/bocca/bordi.json (il rettangolo di
ogni fotogramma in pixel; assente = la faccia non si vede e il fotogramma resta com'e'). Riparte da dove era arrivato.
Uso: python render027_bocca.py [BLEND]   Poi: python componi027_bocca.py"""
import sys, os, json, time, bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
QUI = os.path.dirname(os.path.abspath(__file__)); T27 = os.path.join(QUI, '..', 't027'); OUT = os.path.join(T27, 'bocca'); os.makedirs(OUT, exist_ok=True)
BLEND = sys.argv[-1] if sys.argv[-1].endswith('.blend') else os.path.join(T27, 'pippo_t027.blend')
bpy.ops.wm.open_mainfile(filepath=BLEND)
sc = bpy.context.scene; sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 1080, 1920, 100; sc.render.image_settings.file_format = 'PNG'
W, H = 1080, 1920; cam = sc.camera; mo = bpy.data.objects['MouthOpen']; head = mo.parent
JS = os.path.join(OUT, 'bordi.json'); bordi = json.load(open(JS)) if os.path.exists(JS) else {}
escl = [tuple(x) for x in json.loads(os.environ.get('ESCLUDI027', '[]'))]                 # intervalli di fotogrammi da saltare: [[primo, ultimo], ...]
for f in range(1, sc.frame_end + 1):
    if str(f) in bordi or any(a <= f <= b for a, b in escl): continue
    fin = os.path.join(OUT, 'b%04d.png' % f); t0 = time.time()
    sc.frame_set(f); dg = bpy.context.evaluated_depsgraph_get(); bpy.context.view_layer.update()
    Mh = head.matrix_world; c = Mh @ Vector((0, -0.279, 0.27 - 0.17)); sca = Mh.to_scale().x      # centro della bocca nel mondo
    avanti = (Mh.to_3x3() @ Vector((0, -1, 0))).normalized(); verso_cam = (cam.matrix_world.translation - c).normalized()
    p = world_to_camera_view(sc, cam, c); r = 0.0
    for d in (Vector((0.26, 0, 0)), Vector((-0.26, 0, 0)), Vector((0, 0, 0.2)), Vector((0, 0, -0.2)), Vector((0, -0.1, 0))):   # quanto e' grande la zona sullo schermo
        q = world_to_camera_view(sc, cam, c + Mh.to_3x3() @ d); r = max(r, abs(q.x - p.x) * W, abs(q.y - p.y) * H)
    visibile = p.z > 0 and avanti.dot(verso_cam) > -0.25 and -0.1 < p.x < 1.1 and -0.1 < p.y < 1.1 and r >= 3.0
    if not visibile:
        bordi[str(f)] = None; json.dump(bordi, open(JS, 'w')); continue
    m = r + 14                                                                             # margine per la sfumatura
    x0, x1 = max(0, int(p.x * W - m)), min(W, int(p.x * W + m) + 1); y0, y1 = max(0, int((1 - p.y) * H - m)), min(H, int((1 - p.y) * H + m) + 1)
    if x1 - x0 < 8 or y1 - y0 < 8:
        bordi[str(f)] = None; json.dump(bordi, open(JS, 'w')); continue
    sc.render.use_border = True; sc.render.use_crop_to_border = False
    sc.render.border_min_x, sc.render.border_max_x = x0 / W, x1 / W; sc.render.border_min_y, sc.render.border_max_y = 1 - y1 / H, 1 - y0 / H
    sc.render.filepath = os.path.join(OUT, 'tmp_b%04d.png' % f); bpy.ops.render.render(write_still=True); os.replace(os.path.join(OUT, 'tmp_b%04d.png' % f), fin)
    bordi[str(f)] = [x0, y0, x1, y1]; json.dump(bordi, open(JS, 'w'))
    print('bocca %d: zona %dx%d in %.1f s' % (f, x1 - x0, y1 - y0, time.time() - t0), flush=True)
print('FINITO', flush=True)
