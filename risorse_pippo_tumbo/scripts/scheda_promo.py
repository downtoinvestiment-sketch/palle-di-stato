"""Scheda di opzioni del video promo «Il terzo personaggio» (copione n. 12): il posto vuoto nella squadra su un palco con sipario rosso.
S sagoma nera con il punto di domanda, T forma coperta da un telo rosso, U cassa misteriosa con la coda che esce.
Uso:  python scheda_promo.py S   (una opzione per processo: S, T, U), poi  python scheda_promo.py componi
Immagini in ../out/scheda_promo/, scheda finale in ../schede/scelta_promo.png"""
import sys, os, math
QUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, QUI)
import bpy, bmesh
from mathutils import Vector
from common import *
from render_setup import *
import set004, props019, luci, kitlook
import pippo2
import tumbo
A = kitlook.A
OUT = os.path.join(QUI, '..', 'out', 'scheda_promo'); SCHEDE = os.path.join(QUI, '..', 'schede'); os.makedirs(OUT, exist_ok=True)
PI = math.pi
FONT = A.font('luckiest')
XS = 2.1                      # dove sta il posto vuoto


def tenda(C, mat, x0, x1, z0, z1, y, pieghe=0.26, prof=0.22, nome='Tenda', seg=220):
    """telo a pieghe verticali (sinusoide lungo x) da x0 a x1, da z0 a z1, alla profondita' y."""
    bm = bmesh.new(); n = seg; rows = 2
    vs = []
    for j in range(rows):
        z = z0 + (z1 - z0) * j / (rows - 1); r = []
        for i in range(n + 1):
            x = x0 + (x1 - x0) * i / n
            r.append(bm.verts.new((x, y + prof * 0.5 * math.sin(2 * PI * (x - x0) / pieghe) + prof * 0.25 * math.sin(2 * PI * (x - x0) / (pieghe * 2.7)), z)))
        vs.append(r)
    for i in range(n): bm.faces.new((vs[0][i], vs[0][i + 1], vs[1][i + 1], vs[1][i]))
    me = bpy.data.meshes.new(nome); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    o = bpy.data.objects.new(nome, me); C.objects.link(o); me.materials.append(mat); return o


def mat_emissione(nome, col, forza=3.0, alfa=1.0):
    m = bpy.data.materials.new(nome); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial'); em = nt.nodes.new('ShaderNodeEmission'); em.inputs['Color'].default_value = (*col, 1); em.inputs['Strength'].default_value = forza
    if alfa < 1.0:
        tr = nt.nodes.new('ShaderNodeBsdfTransparent'); mx = nt.nodes.new('ShaderNodeMixShader'); mx.inputs['Fac'].default_value = alfa
        nt.links.new(tr.outputs[0], mx.inputs[1]); nt.links.new(em.outputs[0], mx.inputs[2]); nt.links.new(mx.outputs[0], out.inputs['Surface'])
        try: m.surface_render_method = 'BLENDED'
        except Exception: pass
    else: nt.links.new(em.outputs[0], out.inputs['Surface'])
    return m


def cono_luce(C, x, mat, h=7.5, r=1.25):
    """fascio visibile dell'occhio di bue: cono aperto dall'alto al pavimento."""
    bpy.ops.mesh.primitive_cone_add(vertices=48, radius1=r, radius2=0.12, depth=h, end_fill_type='NOTHING', location=(x, 0.4, h / 2))
    o = bpy.context.active_object; o.name = 'Fascio'; o.data.materials.append(mat)
    for c in o.users_collection: c.objects.unlink(o)
    C.objects.link(o); A.niente_ombra(o); return o


def palco(C):
    legno = A.materiale('WoodFloor043', dimensione=2.0, tinta=(1.05, 0.9, 0.75))
    props019.box('Palco', (0, -2.0, -0.15), (20, 14, 0.3), legno, C)
    rosso = A.materiale('velour_velvet', dimensione=0.8, tinta=(1.6, 0.25, 0.25))
    tenda(C, rosso, -10, 10, -0.05, 14.0, 4.2, nome='Fondale')
    tenda(C, rosso, -8.5, -4.6, -0.05, 9.0, -0.9, pieghe=0.2, prof=0.35, nome='TendaSx')
    tenda(C, rosso, 4.6, 8.5, -0.05, 9.0, -0.9, pieghe=0.2, prof=0.35, nome='TendaDx')
    oro = material('Oro', (0.85, 0.6, 0.18), rough=0.3, metallic=0.9)
    tenda(C, rosso, -9, 9, 5.3, 6.6, -1.05, pieghe=0.5, prof=0.18, nome='Mantovana')
    props019.box('Frangia', (0, -1.15, 5.3), (18, 0.12, 0.14), oro, C)
    fascio = mat_emissione('Fascio', (1.0, 0.92, 0.7), forza=1.6, alfa=0.06)
    for x in (-2.4, -0.6, XS):
        cono_luce(C, x, fascio)
        l = bpy.data.lights.new('OcchioBue', 'SPOT'); l.energy = 900 if x != XS else 1300; l.color = (1.0, 0.9, 0.7); l.spot_size = 0.42; l.spot_blend = 0.25; l.shadow_soft_size = 0.05
        o = bpy.data.objects.new('OcchioBue', l); C.objects.link(o); o.location = (x, 0.4, 7.4); o.rotation_euler = (0, 0, 0)
    return legno


def punto_domanda(C, loc, s=1.0, mat=None):
    mat = mat or mat_emissione('Domanda', (1.0, 0.82, 0.12), forza=2.2)
    cu = bpy.data.curves.new('Domanda', 'FONT'); cu.body = '?'; cu.size = 1.25 * s; cu.align_x = 'CENTER'; cu.align_y = 'CENTER'; cu.extrude = 0.08 * s; cu.bevel_depth = 0.02 * s
    cu.font = bpy.data.fonts.load(FONT, check_existing=True)
    o = bpy.data.objects.new('Domanda', cu); o.location = loc; o.rotation_euler = (PI / 2, 0, 0); C.objects.link(o); cu.materials.append(mat); return o


def metablob(C, mat, pezzi, nome='Blob', voxel=0.035):
    """forma morbida unica: ellissoidi uniti e rifusi con Remesh a voxel (niente giunture)."""
    objs = []
    for tipo, co, r, sc in pezzi:
        sc = sc or (1, 1, 1)
        objs.append(set004.ball_(nome + 'P', r, (XS + co[0], 0.4 + co[1], co[2]), mat, C, sc=sc))
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs: o.data = o.data.copy(); o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]; bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bpy.context.view_layer.objects.active = objs[0]; bpy.ops.object.join(); o = objs[0]; o.name = nome
    rm = o.modifiers.new('Rifondi', 'REMESH'); rm.mode = 'VOXEL'; rm.voxel_size = voxel
    sm = o.modifiers.new('Liscia', 'SMOOTH'); sm.iterations = 12; sm.factor = 0.8
    for p in o.data.polygons: p.use_smooth = True
    return o


def sagoma(C):
    nero = material('SagomaNera', (0.01, 0.01, 0.015), rough=0.25, spec=0.8, coat=0.6)
    metablob(C, nero, [('E', (0, 0, 0.85), 0.55, (0.95, 0.8, 1.15)),
                       ('E', (0, 0, 1.75), 0.5, None),
                       ('E', (0.32, 0, 2.3), 0.16, (0.9, 0.9, 2.2)),           # un corno storto
                       ('E', (-0.55, 0, 2.05), 0.26, (1.4, 0.55, 0.8)),         # un orecchio enorme
                       ('E', (0.72, 0.15, 0.55), 0.17, (2.2, 0.8, 0.7)),        # coda
                       ('E', (-0.2, 0, 0.18), 0.2, None), ('E', (0.2, 0, 0.18), 0.2, None)], 'Sagoma')
    punto_domanda(C, (XS, 0.1, 3.35), 1.0)


def telo(C):
    rosso = A.materiale('velour_velvet', dimensione=0.35, tinta=(0.9, 0.06, 0.07))
    metablob(C, rosso, [('E', (0, 0, 0.55), 0.75, (1.0, 0.95, 0.75)),
                        ('E', (0, 0, 1.35), 0.6, (1.0, 1.0, 1.1)),
                        ('E', (0, 0, 2.0), 0.42, None),
                        ('E', (0.3, 0, 2.45), 0.15, (1.0, 1.0, 1.8)),
                        ('E', (-0.36, 0, 2.38), 0.18, (1.0, 1.0, 1.3)),
                        ('E', (0.8, -0.1, 0.75), 0.2, (1.5, 0.8, 0.8))], 'Telo')
    oro = material('OroTelo', (0.9, 0.65, 0.15), rough=0.3, metallic=0.9)
    props019.box('Fiocco', (XS, 0.4 - 0.62, 1.15), (1.5, 0.05, 0.07), oro, C, rot=(0, 0.15, 0))
    punto_domanda(C, (XS, 0.4 - 1.05, 1.2), 0.75, material('DomandaBianca', (1, 1, 1), rough=0.4))
    punto_domanda(C, (XS, 0.1, 3.3), 0.8)


def cassa(C):
    legno = A.materiale('weathered_planks', dimensione=0.9)
    nero = material('Buio', (0, 0, 0), rough=1.0)
    w, h = 1.7, 1.55
    props019.box('Interno', (XS, 0.4, h / 2), (w - 0.08, w - 0.08, h - 0.04), nero, C)
    for sx in (-1, 1):
        props019.box('Lato', (XS + sx * w / 2, 0.4, h / 2), (0.08, w, h), legno, C)
        props019.box('Lato', (XS, 0.4 + sx * w / 2, h / 2), (w, 0.08, h), legno, C)
    props019.box('Coperchio', (XS + 0.15, 0.4, h + 0.32), (w + 0.1, w + 0.1, 0.09), legno, C, rot=(0, -0.28, 0.08))
    props019.box('Croce', (XS, 0.4 - w / 2 - 0.05, h / 2), (0.14, 0.04, h * 1.25), legno, C, rot=(0, 0.83, 0))
    props019.box('Croce', (XS, 0.4 - w / 2 - 0.05, h / 2), (0.14, 0.04, h * 1.25), legno, C, rot=(0, -0.83, 0))
    occhio = mat_emissione('OcchiBuio', (1.0, 0.95, 0.4), forza=8.0)
    for sx in (-1, 1): set004.ball_('Occhio', 0.09, (XS - 0.1 + sx * 0.2, 0.4 - 0.55, h + 0.08), occhio, C, sc=(1, 0.4, 0.7))
    vernice = material('Vernice', (0.95, 0.85, 0.15), rough=0.6)
    punto_domanda(C, (XS - 0.45, 0.4 - w / 2 - 0.09, 1.05), 0.55, vernice)
    # coda a strisce che esce dal fianco
    viola = material('CodaViola', (0.45, 0.1, 0.75), rough=0.4); verde = material('CodaVerde', (0.35, 0.9, 0.2), rough=0.4)
    for k in range(9):
        t = k / 8.0; x = XS - w / 2 - 0.05 - 0.8 * t; z = 0.55 + 0.9 * math.sin(t * 2.6)
        set004.ball_('Coda', 0.16 - 0.06 * t, (x, 0.0, z), viola if k % 2 else verde, C)
    punto_domanda(C, (XS + 0.15, 0.1, 3.1), 0.8)


def scena(op):
    reset_scene(); set004._c.clear(); scene = bpy.context.scene
    C = collection('C')
    W, H = 720, 1280
    setup_render(scene, W, H, samples=8, fps=24, frames=1)
    A.qualita_eevee(preset='equilibrato', riflessi=True, scena=scene, risoluzione=(W, H)); scene.view_settings.exposure = 0.1
    scene.world = bpy.data.worlds.new('W'); scene.world.use_nodes = True
    bg = next(n for n in scene.world.node_tree.nodes if n.type == 'BACKGROUND'); bg.inputs['Color'].default_value = (0.02, 0.02, 0.04, 1); bg.inputs['Strength'].default_value = 1.0
    luci.cielo_basso(scene.world, 0.12)
    cam = bpy.data.objects.new('Cam', bpy.data.cameras.new('Cam')); C.objects.link(cam); scene.camera = cam; cam.data.clip_start = 0.02
    cam.location = (0.0, -7.4, 1.7); luci.punta(cam, (0.0, 0.4, 2.0)); cam.data.lens = 23
    palco(C)
    P = pippo2.build_pippo(C); P['root'].location = (-2.4, 0.4, 0); P['root'].rotation_euler = (0, 0, 0.35)
    pippo2.emozione(P, 1, 'sorpreso')
    T = tumbo.build_tumbo(C, scale=0.75); T['root'].location = (-0.6, 0.2, 0); T['root'].rotation_euler = (0, 0, 0.5)
    tumbo.tumbo_express(T, 1, tongue=0.6, brow=0.3, look=(0.6, 0.1))
    {'S': sagoma, 'T': telo, 'U': cassa}[op](C)
    luci.cinema(C, (0.0, 0.4, 1.4), tuple(cam.location), distanza=6.0, lato=1, forza=0.7)
    luci.ombre_pulite(scene, mezza_risoluzione=False)
    scene.render.filepath = os.path.join(OUT, op + '.png'); bpy.ops.render.render(write_still=True); print('RESA', op, flush=True)


def componi():
    from PIL import Image, ImageDraw, ImageFont
    def tit(im, testo, xy, size=50, col=(255, 225, 60)):
        ImageDraw.Draw(im).text(xy, testo, font=ImageFont.truetype(FONT, size), fill=col, stroke_width=max(3, size // 11), stroke_fill=(20, 20, 30), anchor='mm')
    ops = (('S', 'sagoma nera'), ('T', 'telo rosso'), ('U', 'cassa misteriosa'))
    w = 720; im = Image.new('RGB', (3 * w + 40, 1280 + 110), (20, 20, 30))
    for i, (k, d) in enumerate(ops):
        p = os.path.join(OUT, k + '.png')
        if os.path.exists(p): im.paste(Image.open(p).convert('RGB'), (i * (w + 20), 110))
        tit(im, k + '  ' + d, (i * (w + 20) + w // 2, 55))
    im.save(os.path.join(SCHEDE, 'scelta_promo.png')); print('SCHEDA FATTA', flush=True)


if __name__ == '__main__':
    a = sys.argv[-1]
    if a == 'componi': componi()
    else: scena(a)
