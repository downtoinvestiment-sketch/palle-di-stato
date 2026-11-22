"""Genera sagome (immagini con sfondo trasparente) da modelli realistici della libreria.
Uso: python crea_sagome.py fir_tree_01 jacaranda_tree ... [--angoli 0,110] [--max 6]
     ->  alberi_cartonati/<nome>_<n>.webp            (angolo 0)
         alberi_cartonati/<nome>_<n>_a110.webp       (altri angoli: lo stesso albero visto da un altro lato)
Se il modello contiene piu' esemplari affiancati (tre abeti, sei ciuffi d'erba) ne esce una sagoma per
esemplare, fino a --max (6). I pezzi di uno stesso oggetto (vaso, terra, pianta) restano in un'unica sagoma.
Scarica da solo il modello se manca e salta le sagome gia' fatte, quindi si puo' sempre far ripartire."""
import bpy, sys, os, math
from mathutils import Vector
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pt_assets as A

OUT = A.percorso('alberi_cartonati'); os.makedirs(OUT, exist_ok=True)
args = sys.argv[1:]
angoli = [0]
if '--angoli' in args:
    i = args.index('--angoli'); angoli = [int(x) for x in args[i + 1].split(',')]; args = args[:i] + args[i + 2:]
massimo = 6
if '--max' in args:
    i = args.index('--max'); massimo = int(args[i + 1]); args = args[:i] + args[i + 2:]

for aid in args:
    try:
        A.scarica(aid)
        bpy.ops.wm.read_factory_settings(use_empty=True)
        sc = A.qualita_eevee(campioni=16, riflessi=False)
        A.cielo('kloofendal_48d_partly_cloudy_puresky', forza=0.75, rotazione=160, ombre_sole=False)
        L = bpy.data.objects.new('Sole', bpy.data.lights.new('Sole', 'SUN')); sc.collection.objects.link(L)
        L.data.energy = 3.5; L.data.angle = math.radians(8); L.rotation_euler = (math.radians(58), 0, math.radians(-35))
        sc.render.film_transparent = True
        sc.render.image_settings.file_format = 'WEBP'; sc.render.image_settings.color_mode = 'RGBA'; sc.render.image_settings.quality = 88
        objs = A._carica_blend(aid, A.percorso(A.info(aid)['blend']), lod=1)
        for o in objs: sc.collection.objects.link(o)
        perno = bpy.data.objects.new('Perno', None); sc.collection.objects.link(perno)
        for o in objs:
            if o.parent is None: o.parent = perno
        bpy.context.view_layer.update()
        top = sorted([o for o in objs if o.type == 'MESH' and o.parent == perno], key=lambda o: o.name)
        # Esemplari diversi stanno affiancati (ognuno diventa una sagoma); i pezzi di uno stesso oggetto
        # (vaso + terra + pianta) si sovrappongono e restano insieme in un'unica sagoma.
        def ingombro(o):
            pts = [q.matrix_world @ Vector(c) for q in [o] + [c for c in o.children_recursive if c.type == 'MESH'] for c in q.bound_box]
            return min(p.x for p in pts), max(p.x for p in pts), min(p.y for p in pts), max(p.y for p in pts)
        def sovrapposti(a, b):
            dx = min(a[1], b[1]) - max(a[0], b[0]); dy = min(a[3], b[3]) - max(a[2], b[2])
            return dx > 0.3 * min(a[1] - a[0], b[1] - b[0]) and dy > 0.3 * min(a[3] - a[2], b[3] - b[2])
        gruppi = []
        for o in top:
            vicini = [g for g in gruppi if any(sovrapposti(ingombro(o), ingombro(q)) for q in g)]
            gruppi = [g for g in gruppi if g not in vicini] + [[o] + [q for g in vicini for q in g]]
        gruppi = sorted((sorted(g, key=lambda o: o.name) for g in gruppi), key=lambda g: g[0].name)[:massimo]
        if not gruppi or A._triangoli(top) == 0: gruppi = [None]   # nessun esemplare riconoscibile: un'unica sagoma
        top = gruppi
        cam = bpy.data.objects.new('C', bpy.data.cameras.new('C')); sc.collection.objects.link(cam); cam.data.type = 'ORTHO'; sc.camera = cam
        for ang in angoli:
            perno.rotation_euler[2] = math.radians(ang); bpy.context.view_layer.update()
            for vi, t in enumerate(top):
                nome = f'{aid}_{vi}' + (f'_a{ang}' if ang else '')
                if os.path.exists(f'{OUT}/{nome}.webp'): continue
                grp = [o for o in objs if o.type == 'MESH'] if t is None else [q for o in t for q in [o] + [c for c in o.children_recursive if c.type == 'MESH']]
                for o in objs:
                    if o.type == 'MESH': o.hide_render = o not in grp
                pts = [o.matrix_world @ Vector(c) for o in grp for c in o.bound_box]
                xs = [p.x for p in pts]; ys = [p.y for p in pts]; zs = [p.z for p in pts]
                cx = (min(xs) + max(xs)) / 2; w = (max(xs) - min(xs)) * 1.04; h = (max(zs) - min(zs)) * 1.02; z0 = min(zs)
                if w < 1e-4 or h < 1e-4: continue
                cam.location = (cx, min(ys) - 50, z0 + h / 2); cam.rotation_euler = (math.radians(90), 0, 0)
                cam.data.ortho_scale = max(w, h); cam.data.clip_end = 500
                H = 1024; W = max(64, int(round(H * w / h)))
                if W > 1536: W = 1536; H = max(64, int(round(W * h / w)))
                sc.render.resolution_x, sc.render.resolution_y = W, H
                sc.render.filepath = f'{OUT}/{nome}.webp'
                bpy.ops.render.render(write_still=True)
                print('CARD', nome, W, H, 'alt %.2fm' % h, flush=True)
    except Exception as e:
        print('ERR', aid, repr(e)[:200], flush=True)
