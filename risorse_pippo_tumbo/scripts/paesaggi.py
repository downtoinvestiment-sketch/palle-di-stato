"""paesaggi.py - mattoni per posti ricchi e non piatti: terreno con colline, mare, bosco di alberi veri, oggetti sparsi che seguono il terreno,
piu' qualche oggetto costruito a mano (tenda, fuoco, semaforo, strisce pedonali).
Regola dell'autore: un posto non deve sembrare "un mondo piatto di Minecraft". Quindi sempre: rilievo sullo sfondo, alberi realistici,
tanti dettagli vicini (erba, cespugli, sassi), qualcosa in primo piano ai bordi dell'inquadratura.
Uso (dopo kitlook.upgrade):  import paesaggi as PS;  h = PS.colline(amp=6);  PS.terreno(envc, x0, mat, h);  PS.bosco(A, envc, x0, h, ...)"""
import bpy, math, random
from mathutils import Vector
from common import material, shape, empty
PI = math.pi

def sm(x): x = min(1.0, max(0.0, x)); return x * x * (3 - 2 * x)
def onde(x, y, s=1.0):
    """rumore morbido tra -1 e 1 fatto di seni: basta per colline e dune."""
    return (math.sin(x * 0.07 * s + 1.3) * math.cos(y * 0.05 * s + 0.4) + 0.5 * math.sin(x * 0.13 * s + y * 0.11 * s + 2.0) + 0.25 * math.sin(x * 0.31 * s - y * 0.27 * s)) / 1.75

def colline(amp=6.0, rx=12.0, ry=10.0, cy=3.0, bordo=16.0, lontano=9.0, fase=0.0):
    """altezza(x, y) con x relativo al centro del posto: piano dove recitano i personaggi (ellisse rx, ry), poi colline, poi una cresta lontana."""
    def h(x, y):
        r = math.hypot(x / rx, (y - cy) / ry); d = max(0.0, r - 1.0) * rx; k = sm(d / bordo)
        z = amp * k * (0.4 + 0.6 * (onde(x + fase, y + fase * 0.7) * 0.5 + 0.5))
        z += lontano * sm((math.hypot(x, y - cy) - 45.0) / 70.0) * (0.6 + 0.4 * onde(x * 0.6 + 40 + fase, y * 0.6))
        return z
    return h

def isola(rx=22.0, ry=18.0, cy=6.0, fondo=-2.2, colli=((-15, 16, 7.0, 70.0), (17, 14, 4.5, 45.0)), lontane=((-45, 80, 9.0, 500.0), (55, 100, 7.0, 400.0))):
    """altezza(x, y) di un'isola: spiaggia piana al centro, piccole dune, colli (x, y, altezza, larghezza), riva che scende nel mare, isole lontane."""
    def h(x, y):
        r = math.hypot(x / rx, (y - cy) / ry)
        terra = 0.25 * onde(x * 2.2, y * 2.2) * sm((r - 0.35) / 0.4) + sum(a * math.exp(-((x - cx) ** 2 + (y - cyy) ** 2) / w) for cx, cyy, a, w in colli)
        k = sm((r - 0.8) / 0.45)
        return terra * (1 - k) + fondo * k + sum(a * math.exp(-((x - cx) ** 2 + (y - cyy) ** 2) / w) for cx, cyy, a, w in lontane)
    return h

def terreno(coll, x0, mat, h, xr=(-110, 110), yr=(-30, 190), passo=2.0, nome='Terreno'):
    """maglia del terreno centrata in x0 con le altezze date da h(x, y). Ombreggiatura morbida."""
    nx = int((xr[1] - xr[0]) / passo) + 1; ny = int((yr[1] - yr[0]) / passo) + 1
    verts = [(x0 + xr[0] + i * passo, yr[0] + j * passo, h(xr[0] + i * passo, yr[0] + j * passo)) for j in range(ny) for i in range(nx)]
    faces = [(j * nx + i, j * nx + i + 1, (j + 1) * nx + i + 1, (j + 1) * nx + i) for j in range(ny - 1) for i in range(nx - 1)]
    me = bpy.data.meshes.new(nome); me.from_pydata(verts, [], faces); me.update()
    for p in me.polygons: p.use_smooth = True
    o = bpy.data.objects.new(nome, me); coll.objects.link(o); me.materials.append(mat); o.visible_shadow = False; return o

def mare(coll, x0, z=-0.35, colore=(0.02, 0.30, 0.48), mezzo=260, nome='Mare'):
    """piano d'acqua lucido con increspature."""
    me = bpy.data.meshes.new(nome); me.from_pydata([(x0 - mezzo, -mezzo, z), (x0 + mezzo, -mezzo, z), (x0 + mezzo, mezzo * 1.6, z), (x0 - mezzo, mezzo * 1.6, z)], [], [(0, 1, 2, 3)]); me.update()
    m = bpy.data.materials.new('PS_mare'); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*colore, 1); b.inputs['Roughness'].default_value = 0.07
    tc = nt.nodes.new('ShaderNodeTexCoord'); no = nt.nodes.new('ShaderNodeTexNoise'); no.inputs['Scale'].default_value = 1.3; no.inputs['Detail'].default_value = 3.0
    bu = nt.nodes.new('ShaderNodeBump'); bu.inputs['Strength'].default_value = 0.22; bu.inputs['Distance'].default_value = 0.4
    nt.links.new(tc.outputs['Object'], no.inputs['Vector']); nt.links.new(no.outputs['Fac'], bu.inputs['Height']); nt.links.new(bu.outputs['Normal'], b.inputs['Normal'])
    o = bpy.data.objects.new(nome, me); coll.objects.link(o); me.materials.append(m); o.visible_shadow = False; return o

def posa(objs, x0, h, giu=0.0):
    """appoggia gli oggetti sul terreno (z = altezza nel punto)."""
    for o in objs: o.location.z = h(o.location.x - x0, o.location.y) - giu
    return objs

def bosco(A, coll, x0, h, specie, quanti, r0=11.0, r1=48.0, alt=(9.0, 14.0), seme=1, rx=1.0, ry=1.0, cy=3.0, a0=-0.25, a1=PI + 0.25, ombra_vicini=0, giu=0.25, evita=()):
    """anello di alberi realistici (sagome fotografiche) intorno alla scena, appoggiati al terreno. a0..a1: arco in radianti (0 = destra, pi/2 = fondo)."""
    rnd = random.Random(seme); out = []
    for k in range(quanti):
        an = rnd.uniform(a0, a1); rr = r0 + (r1 - r0) * rnd.random() ** 1.6; x = rr * math.cos(an) * rx; y = cy + rr * math.sin(an) * ry
        if any(math.hypot(x - ex, y - ey) < er for ex, ey, er in evita): continue
        o = A.albero_cartonato(specie[k % len(specie)], posizione=(x0 + x, y, h(x, y) - giu), altezza=rnd.uniform(*alt), collezione=coll, vista=k, ombra=k < ombra_vicini)
        if rnd.random() < 0.5: o.scale.x = -1
        out.append(o)
    return out

def tenda(coll, loc, rot=0.0, colore=(0.95, 0.45, 0.08), largo=2.4, lungo=3.0, alto=1.7, nome='Tenda'):
    """tenda canadese: apertura verso -Y con rot = 0."""
    w, l, a = largo / 2, lungo / 2, alto
    me = bpy.data.meshes.new(nome); me.from_pydata([(-w, -l, 0), (w, -l, 0), (w, l, 0), (-w, l, 0), (0, -l, a), (0, l, a)], [], [(0, 3, 5, 4), (1, 4, 5, 2), (3, 2, 5), (0, 1, 2, 3)]); me.update()
    tela = material('PS_tela_%s' % nome, colore, rough=0.9, spec=0.1); buio = material('PS_tenda_buio', (0.03, 0.02, 0.02), rough=1.0); palo = material('PS_tenda_palo', (0.75, 0.75, 0.78), rough=0.4)
    o = bpy.data.objects.new(nome, me); coll.objects.link(o); me.materials.append(tela); o.location = loc; o.rotation_euler = (0, 0, rot)
    mf = bpy.data.meshes.new(nome + 'Porta'); mf.from_pydata([(-w * 0.62, -l - 0.01, 0), (w * 0.62, -l - 0.01, 0), (0, -l - 0.01, a * 0.62)], [], [(0, 1, 2)]); mf.update()
    f = bpy.data.objects.new(nome + 'Porta', mf); coll.objects.link(f); mf.materials.append(buio); f.parent = o
    mb = bpy.data.meshes.new(nome + 'Bordo'); mb.from_pydata([(-w, -l - 0.005, 0), (w, -l - 0.005, 0), (0, -l - 0.005, a)], [], [(0, 1, 2)]); mb.update()
    bo = bpy.data.objects.new(nome + 'Bordo', mb); coll.objects.link(bo); mb.materials.append(tela); bo.parent = o
    for y in (-l - 0.05, l + 0.05): shape(nome + 'Palo', 'cyl:0.025:%g' % (a + 0.15), (0, y, (a + 0.15) / 2), parent=o, mat=palo, coll=coll)
    return o

def fuoco(coll, loc, scala=1.0, luce=700.0, nome='Fuoco'):
    """fiamme stilizzate luminose piu' una luce calda. Restituisce (radice, luce)."""
    r = empty(nome, loc, None, coll); r.scale = (scala,) * 3
    for i, (dx, dy, s, c, e) in enumerate(((0, 0, (0.24, 0.24, 0.74), (1.0, 0.42, 0.02), 1.1), (0.12, 0.05, (0.15, 0.15, 0.5), (1.0, 0.5, 0.03), 1.2), (-0.11, -0.06, (0.14, 0.14, 0.44), (1.0, 0.46, 0.02), 1.2), (0, -0.03, (0.11, 0.11, 0.36), (1.0, 0.8, 0.12), 1.5))):
        shape('%sF%d' % (nome, i), 'cone', (dx, dy, 0.05), scale=s, parent=r, mat=material('PS_fuoco%d' % i, c, rough=1.0, emit=c, emit_strength=e), coll=coll)
    l_ = bpy.data.lights.new(nome + 'Luce', 'POINT'); lo = bpy.data.objects.new(nome + 'Luce', l_); coll.objects.link(lo); lo.location = (loc[0], loc[1] - 0.1, loc[2] + 0.7); l_.energy = luce; l_.color = (1.0, 0.5, 0.15); l_.shadow_soft_size = 0.4
    return r, lo

def semaforo(coll, loc, rot=0.0, acceso='verde', nome='Semaforo'):
    """semaforo su palo: le luci guardano verso -Y con rot = 0."""
    r = empty(nome, loc, None, coll); r.rotation_euler = (0, 0, rot)
    buio = material('PS_sem_palo', (0.06, 0.07, 0.08), rough=0.5); shape(nome + 'Palo', 'cyl:0.08:3.6', (0, 0, 1.8), parent=r, mat=buio, coll=coll)
    shape(nome + 'Cassa', 'cyl:0.24:1.15', (0, 0, 3.75), scale=(1, 0.75, 1), parent=r, mat=buio, coll=coll)
    for i, (nm, c) in enumerate((('rosso', (1.0, 0.05, 0.03)), ('giallo', (1.0, 0.7, 0.05)), ('verde', (0.1, 1.0, 0.25)))):
        on = nm == acceso; col = c if on else tuple(v * 0.12 for v in c)
        shape(nome + nm, 'sphere', (0, -0.15, 4.1 - i * 0.35), scale=(0.13, 0.07, 0.13), parent=r, mat=material('PS_sem_%s_%d' % (nm, on), col, rough=0.3, emit=c if on else None, emit_strength=9.0 if on else 0.0), coll=coll)
    return r

def strisce(coll, x0, y0, mezza=6.0, lunghe=3.2, passo=1.1, nome='Strisce'):
    """strisce pedonali che attraversano una strada lungo X (la strada corre lungo Y)."""
    bianco = material('PS_strisce', (0.92, 0.92, 0.9), rough=0.7); out = []; x = -mezza + 0.4
    while x < mezza - 0.4:
        me = bpy.data.meshes.new(nome); me.from_pydata([(x0 + x, y0, 0.012), (x0 + x + 0.55, y0, 0.012), (x0 + x + 0.55, y0 + lunghe, 0.012), (x0 + x, y0 + lunghe, 0.012)], [], [(0, 1, 2, 3)]); me.update()
        o = bpy.data.objects.new(nome, me); coll.objects.link(o); me.materials.append(bianco); o.visible_shadow = False; out.append(o); x += passo
    return out

# ---------------------------------------------------------------- modelli: leggeri in memoria (il limite della macchina e' 8 GB)
def kenney(A, aid, coll, x, y, z=0.0, h=None, w=None, s=None, rot=0.0, rx=0.0):
    """modello cartoon del kit (id senza 'kenney/'): h = altezza in metri, w = lato piu' lungo in pianta, s = scala fissa; (x, y) = centro della base."""
    r = A.modello('kenney/' + aid, collezione=coll); r.rotation_mode = 'XYZ'; r.location = (0, 0, 0); r.scale = (1, 1, 1)
    r.rotation_euler = (math.radians(rx), 0, math.radians(rot)); bpy.context.view_layer.update()
    def bb():
        pts = [o.matrix_world @ Vector(c) for o in list(r.children_recursive) if o.type == 'MESH' for c in o.bound_box]
        return [min(p[i] for p in pts) for i in range(3)], [max(p[i] for p in pts) for i in range(3)]
    mn, mx = bb()
    if h: s = h / max(1e-6, mx[2] - mn[2])
    elif w: s = w / max(1e-6, max(mx[0] - mn[0], mx[1] - mn[1]))
    s = s or 1.0; r.scale = (s, s, s); bpy.context.view_layer.update(); mn, mx = bb()
    r.location = (x - (mn[0] + mx[0]) / 2, y - (mn[1] + mx[1]) / 2, z - mn[2]); bpy.context.view_layer.update()
    return r, (mx[0] - mn[0], mx[1] - mn[1], mx[2] - mn[2])

def pulisci():
    """le copie della stessa texture caricate piu' volte diventano una sola e i dati rimasti orfani vengono liberati: risparmia molta memoria."""
    visti = {}
    for img in list(bpy.data.images):
        k = bpy.path.abspath(img.filepath) if img.filepath and img.source == 'FILE' else None
        if not k: continue
        if k in visti: img.user_remap(visti[k]); bpy.data.images.remove(img)
        else: visti[k] = img
    try: bpy.data.orphans_purge(do_recursive=True)
    except Exception: pass

def alleggerisci(radice, lato=512):
    """rende definitiva la semplificazione della geometria e rimpicciolisce le texture del modello (lato massimo in pixel)."""
    bpy.context.view_layer.update(); dg = bpy.context.evaluated_depsgraph_get()
    for o in [radice] + list(radice.children_recursive):
        if o.type != 'MESH': continue
        if any(m.type == 'DECIMATE' for m in o.modifiers) and not any(m.type == 'ARMATURE' for m in o.modifiers):
            me = bpy.data.meshes.new_from_object(o.evaluated_get(dg)); old = o.data; o.modifiers.clear(); o.data = me
            if old.users == 0: bpy.data.meshes.remove(old)
        for sl in o.material_slots:
            if sl.material and sl.material.node_tree:
                for n in sl.material.node_tree.nodes:
                    if n.type == 'TEX_IMAGE' and n.image and max(n.image.size) > lato:
                        k = lato / max(n.image.size); n.image.scale(max(1, int(n.image.size[0] * k)), max(1, int(n.image.size[1] * k)))
    return radice

def modello(A, coll, x0, h, aid, x, y, alt, rot=0.0, tri=None, z=None, lato=512):
    """modello realistico appoggiato al terreno, gia' alleggerito."""
    return alleggerisci(A.modello(aid, posizione=(x0 + x, y, h(x, y) if z is None else z), altezza=alt, rotazione=rot, max_triangoli=tri, collezione=coll), lato)

def sparsi(KL, coll, x0, h, aid, n, area, alt, seed, shadow=False, keep=None, via=((0.7, 0.0, 1.6),), lato=512):
    """ciuffi, cespugli e fiori sparsi sul terreno (varianti del modello), lontani dai punti 'via' (x, y, raggio). KL = modulo kitlook."""
    out = KL.variants(aid, n, (x0 + area[0], x0 + area[1], area[2], area[3]), alt, seed=seed, coll=coll, shadow=shadow, keep=keep); rr = random.Random(seed + 99)
    for o in out:
        for _ in range(8):
            if all(math.hypot(o.location.x - x0 - vx, o.location.y - vy) > vr for vx, vy, vr in via): break
            o.location.x = x0 + rr.uniform(area[0], area[1]); o.location.y = rr.uniform(area[2], area[3])
    pulisci()
    for o in out: alleggerisci(o, lato)
    return posa(out, x0, h)

def sparsi2(A, coll, x0, h, aid, n, area, alt, seed, tri=None, lato=512):
    """copie dello stesso modello sparse sul terreno (sassi, cespugli a variante unica)."""
    out = A.sparpaglia(aid, n, (x0 + area[0], x0 + area[1], area[2], area[3]), altezza=alt, seme=seed, max_triangoli=tri, collezione=coll)
    vecchie = {o.data: o for o in out[0].children_recursive if o.type == 'MESH'}; alleggerisci(out[0], lato)
    for r in out[1:]:
        for o in r.children_recursive:
            if o.type == 'MESH' and o.data in vecchie: o.modifiers.clear(); o.data = vecchie[o.data].data
    pulisci(); return posa(out, x0, h)

def rss():
    """memoria usata dal processo, in MB."""
    for l in open('/proc/self/status'):
        if l.startswith('VmRSS'): return int(l.split()[1]) // 1024
