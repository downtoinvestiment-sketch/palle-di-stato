"""Citta' vera in miniatura per il video 027 (Pippo popstar gigante): isolati con palazzi, strade con le righe, lampioni,
macchine che girano (modelli KayKit della libreria asset), skyline lontano nella foschia, e tutto quello che serve per
distruggerla a cartone animato: palazzi che si schiacciano, crollano o cadono come birilli, sbuffi di polvere, calcinacci,
coriandoli, onda d'urto. Pippo resta alto 2,3: e' la citta' a essere piccola (un isolato = 1 unita').
Non tocca pippo.py. Usato da anim027.py."""
import math, random
import bpy, bmesh
from mathutils import Vector, Euler
from common import *
import props024, props027

PI = math.pi
PASSO = 1.30; LATO = 1.00; STRADA = PASSO - LATO                    # passo della griglia, lato dell'isolato, larghezza della strada
ORIZZONTE = (1.0, 0.45, 0.15)                                       # colore del cielo all'orizzonte (tramonto C2): la foschia sfuma li'
CARD = {'+x': Vector((1, 0, 0)), '-x': Vector((-1, 0, 0)), '+y': Vector((0, 1, 0)), '-y': Vector((0, -1, 0))}


# --------------------------------------------------------------------------- materiali
def gruppo_impulso():
    """Gruppo di nodi condiviso da tutte le facciate: «Impulso» moltiplica le finestre accese, «Lampo» accende TUTTE le finestre.
    Si anima una volta sola (chiavi sui due nodi Value) e tutta la citta' pulsa a tempo."""
    g = bpy.data.node_groups.get('M27_Impulso')
    if g:
        return g
    g = bpy.data.node_groups.new('M27_Impulso', 'ShaderNodeTree')
    g.interface.new_socket('Impulso', in_out='OUTPUT', socket_type='NodeSocketFloat')
    g.interface.new_socket('Lampo', in_out='OUTPUT', socket_type='NodeSocketFloat')
    a = g.nodes.new('ShaderNodeValue'); a.name = 'Impulso'; a.outputs[0].default_value = 1.0
    b = g.nodes.new('ShaderNodeValue'); b.name = 'Lampo'; b.outputs[0].default_value = 0.0
    o = g.nodes.new('NodeGroupOutput'); g.links.new(a.outputs[0], o.inputs[0]); g.links.new(b.outputs[0], o.inputs[1])
    return g


def chiave_impulso(f, impulso=None, lampo=None):
    g = gruppo_impulso()
    for nome, v in (('Impulso', impulso), ('Lampo', lampo)):
        if v is not None:
            s = g.nodes[nome].outputs[0]; s.default_value = v; s.keyframe_insert('default_value', frame=f)


def _foschia(m, col=ORIZZONTE, d0=5.0, d1=24.0, mx=0.72):
    """Lontano dalla camera il materiale sfuma verso il colore dell'orizzonte: da' l'idea di una citta' enorme."""
    nt = m.node_tree; N, L = nt.nodes, nt.links
    out = next(n for n in N if n.type == 'OUTPUT_MATERIAL'); src = out.inputs['Surface'].links[0].from_socket
    cd = N.new('ShaderNodeCameraData'); mr = N.new('ShaderNodeMapRange'); mr.clamp = True
    mr.inputs['From Min'].default_value = d0; mr.inputs['From Max'].default_value = d1
    mr.inputs['To Min'].default_value = 0.0; mr.inputs['To Max'].default_value = mx
    L.new(cd.outputs['View Z Depth'], mr.inputs['Value'])
    em = N.new('ShaderNodeEmission'); em.inputs['Color'].default_value = (*col, 1); em.inputs['Strength'].default_value = 1.0
    mix = N.new('ShaderNodeMixShader'); L.new(mr.outputs['Result'], mix.inputs['Fac']); L.new(src, mix.inputs[1]); L.new(em.outputs[0], mix.inputs[2])
    L.new(mix.outputs[0], out.inputs['Surface'])
    return m


def mat_semplice(nome, colore, foschia=True, **k):
    gia = nome in bpy.data.materials
    m = material(nome, colore, **k)
    if foschia and not gia:
        _foschia(m)
    return m


def mat_facciata(nome, muro, vetro, acceso, soglia=0.8, forza=2.2, w=0.07, h=0.095):
    """Facciata con le finestre (griglia sulle UV, in unita' di scena). Una parte delle finestre e' accesa a caso (soglia);
    le accese seguono «Impulso», tutte insieme seguono «Lampo». Con la foschia."""
    if nome in bpy.data.materials:
        return bpy.data.materials[nome]
    m = bpy.data.materials.new(nome); m.use_nodes = True
    nt = m.node_tree; N, L = nt.nodes, nt.links
    b = N['Principled BSDF']
    tc = N.new('ShaderNodeTexCoord'); oi = N.new('ShaderNodeObjectInfo')
    mx = N.new('ShaderNodeMath'); mx.operation = 'MULTIPLY'; mx.inputs[1].default_value = 53.0
    my = N.new('ShaderNodeMath'); my.operation = 'MULTIPLY'; my.inputs[1].default_value = 17.0
    cb = N.new('ShaderNodeCombineXYZ'); ad = N.new('ShaderNodeVectorMath'); ad.operation = 'ADD'
    L.new(oi.outputs['Random'], mx.inputs[0]); L.new(oi.outputs['Random'], my.inputs[0])
    L.new(mx.outputs[0], cb.inputs['X']); L.new(my.outputs[0], cb.inputs['Y'])
    L.new(tc.outputs['UV'], ad.inputs[0]); L.new(cb.outputs[0], ad.inputs[1])
    br = N.new('ShaderNodeTexBrick'); br.offset = 0.0; br.squash = 1.0
    br.inputs['Color1'].default_value = (0, 0, 0, 1); br.inputs['Color2'].default_value = (1, 1, 1, 1); br.inputs['Mortar'].default_value = (0, 0, 0, 1)
    br.inputs['Scale'].default_value = 1.0; br.inputs['Mortar Size'].default_value = 0.014; br.inputs['Mortar Smooth'].default_value = 0.0
    br.inputs['Bias'].default_value = 0.0; br.inputs['Brick Width'].default_value = w; br.inputs['Row Height'].default_value = h
    L.new(ad.outputs[0], br.inputs['Vector'])
    rp = N.new('ShaderNodeValToRGB'); rp.color_ramp.interpolation = 'CONSTANT'
    rp.color_ramp.elements[0].position = 0.0; rp.color_ramp.elements[0].color = (0, 0, 0, 1)
    rp.color_ramp.elements[1].position = soglia; rp.color_ramp.elements[1].color = (1, 1, 1, 1)
    L.new(br.outputs['Color'], rp.inputs['Fac'])
    gi = N.new('ShaderNodeGroup'); gi.node_tree = gruppo_impulso()
    acc = N.new('ShaderNodeMath'); acc.operation = 'MULTIPLY'; L.new(rp.outputs['Color'], acc.inputs[0]); L.new(gi.outputs['Impulso'], acc.inputs[1])
    fin = N.new('ShaderNodeMath'); fin.operation = 'SUBTRACT'; fin.inputs[0].default_value = 1.0; L.new(br.outputs['Fac'], fin.inputs[1])      # 1 sulle finestre, 0 sul muro
    lam = N.new('ShaderNodeMath'); lam.operation = 'MULTIPLY'; L.new(fin.outputs[0], lam.inputs[0]); L.new(gi.outputs['Lampo'], lam.inputs[1])
    som = N.new('ShaderNodeMath'); som.operation = 'ADD'; L.new(acc.outputs[0], som.inputs[0]); L.new(lam.outputs[0], som.inputs[1])
    es = N.new('ShaderNodeMath'); es.operation = 'MULTIPLY'; es.inputs[1].default_value = forza
    L.new(som.outputs[0], es.inputs[0]); L.new(es.outputs[0], b.inputs['Emission Strength'])
    b.inputs['Emission Color'].default_value = (*acceso, 1)
    mixn = N.new('ShaderNodeMix'); mixn.data_type = 'RGBA'
    mixn.inputs[6].default_value = (*vetro, 1); mixn.inputs[7].default_value = (*muro, 1)
    L.new(br.outputs['Fac'], mixn.inputs[0]); L.new(mixn.outputs[2], b.inputs['Base Color'])
    rg = N.new('ShaderNodeMapRange'); rg.inputs['To Min'].default_value = 0.16; rg.inputs['To Max'].default_value = 0.62       # vetri lucidi, muri opachi
    L.new(br.outputs['Fac'], rg.inputs['Value']); L.new(rg.outputs['Result'], b.inputs['Roughness'])
    _foschia(m)
    return m


# Facciate VERE: foto di palazzi trovate sul web (ambientCG, licenza CC0: libere anche nei video monetizzati).
# aid = texture; lampo = texture gemella con piu' finestre accese (si accende col «Lampo»); col, piani = colonne di finestre e
# piani dentro una ripetizione; alto = solo sui palazzi alti (vetrate da grattacielo); tinta = correzione del colore.
SOLE = Vector((0.84, -0.54, 0.39)).normalized()                         # da dove arriva il sole del tramonto (luci.sole con la camera a -Y)
PIANO = 0.085                                                           # altezza di un piano in unita' di scena
FACCIATE_VERE = [
    dict(nome='mattoni', aid='Facade018B', lampo=None, col=6, piani=6, alto=False, tinta=(1.45, 0.95, 0.85), forza=1.3),
    dict(nome='cemento', aid='Facade019B', lampo=None, col=6, piani=6, alto=False, tinta=(1.45, 1.45, 1.5), forza=1.3),
    dict(nome='pilastri', aid='Facade020B', lampo='Facade020C', col=6, piani=6, alto=False, tinta=(1.9, 1.6, 1.3), forza=1.3),
    dict(nome='pilastri_accesi', aid='Facade020C', lampo=None, col=6, piani=6, alto=False, tinta=(1.0, 1.25, 1.8), forza=1.1),
    dict(nome='vetro', aid='Facade003', lampo='Facade004', col=16, piani=10, alto=True, tinta=(0.75, 1.05, 1.5), forza=1.0, piano=0.05),
    dict(nome='vetro_scuro', aid='Facade002', lampo='Facade004', col=16, piani=10, alto=True, tinta=(0.8, 1.15, 1.7), forza=1.2, piano=0.05),    # pannelli piccoli: vetrata continua
    dict(nome='uffici', aid='Facade006', lampo=None, col=14, piani=8, alto=True, tinta=(1.0, 1.2, 1.35), forza=0.0),
    dict(nome='lamelle', aid='Facade017', lampo=None, col=12, piani=10, alto=False, tinta=(1.5, 1.4, 1.3), forza=1.6),            # la 8 della scheda: la preferita dell'autore
    dict(nome='lamelle_blu', aid='Facade017', lampo=None, col=12, piani=10, alto=False, tinta=(1.0, 1.3, 1.9), forza=1.6),        # la stessa facciata con altri colori (se l'autore sceglie solo quella)
    dict(nome='lamelle_chiara', aid='Facade017', lampo=None, col=12, piani=10, alto=False, tinta=(2.3, 2.0, 1.7), forza=1.5),
    dict(nome='lamelle_rosa', aid='Facade017', lampo=None, col=12, piani=10, alto=False, tinta=(2.0, 1.25, 1.2), forza=1.6),
]


def mat_facciata_vera(A, d, piano=PIANO):
    """Materiale di una facciata vera: colore, rilievo, lucido e luci delle finestre vengono dalle foto. Le UV del palazzo sono
    gia' in «ripetizioni» (vedi _aggiungi con griglia), quindi le finestre non vengono mai tagliate a meta' agli spigoli.
    Le finestre accese seguono «Impulso»; col «Lampo» si accendono tutte (texture gemella) o si illumina tutta la facciata."""
    nome = 'M27f_' + d['nome']
    if nome in bpy.data.materials:
        return bpy.data.materials[nome]
    m = A.materiale(d['aid'], dimensione=1.0, proiezione='uv', nome=nome, tinta=d.get('tinta'), rilievo=0.8)
    nt = m.node_tree; N, L = nt.nodes, nt.links
    b = next(n for n in N if n.type == 'BSDF_PRINCIPLED'); mp_ = next(n for n in N if n.type == 'MAPPING')
    gi = N.new('ShaderNodeGroup'); gi.node_tree = gruppo_impulso()
    def scala(sock, fatt):
        v = N.new('ShaderNodeVectorMath'); v.operation = 'SCALE'; L.new(sock, v.inputs[0]); L.new(fatt, v.inputs['Scale'])
        return v.outputs['Vector']
    def immagine(aid, ruolo):
        import pt_assets
        mappe, _ = pt_assets._mappe(aid)
        if ruolo not in mappe:
            return None
        n = N.new('ShaderNodeTexImage'); n.image = bpy.data.images.load(mappe[ruolo], check_existing=True); L.new(mp_.outputs['Vector'], n.inputs['Vector'])
        return n.outputs['Color']
    ecol = b.inputs['Emission Color']; accese = ecol.links[0].from_socket if ecol.links else None
    col = b.inputs['Base Color'].links[0].from_socket
    parti = []
    if accese is not None:
        parti.append(scala(accese, gi.outputs['Impulso']))
    piene = immagine(d['lampo'], 'emissione') if d.get('lampo') else None
    if piene is not None:
        parti.append(scala(piene, gi.outputs['Lampo']))
    else:                                                               # niente gemella: col lampo si illumina tutta la facciata
        mz = N.new('ShaderNodeMath'); mz.operation = 'MULTIPLY'; mz.inputs[1].default_value = 0.55; L.new(gi.outputs['Lampo'], mz.inputs[0])
        parti.append(scala(col, mz.outputs[0]))
    # i vetri: nelle foto sono «metallo a specchio», che senza riflessi veri verrebbe nero. Qui diventano vetro lucido che
    # riflette il tramonto: arancio dove guarda verso il sole, rosa e poi blu-viola dalla parte opposta (cambia con la camera).
    met = b.inputs['Metallic']; vetro = met.links[0].from_socket if met.links else None
    if vetro is not None:
        for l in list(met.links):
            L.remove(l)
        met.default_value = 0.0
        tc = next(n for n in N if n.type == 'TEX_COORD')
        dp = N.new('ShaderNodeVectorMath'); dp.operation = 'DOT_PRODUCT'; L.new(tc.outputs['Reflection'], dp.inputs[0]); dp.inputs[1].default_value = tuple(SOLE)
        rp = N.new('ShaderNodeValToRGB'); e = rp.color_ramp.elements
        e[0].position = 0.0; e[0].color = (0.16, 0.18, 0.46, 1); e[1].position = 1.0; e[1].color = (1.0, 0.86, 0.55, 1)
        for pos, c in ((0.38, (0.46, 0.30, 0.56, 1)), (0.62, (0.95, 0.47, 0.36, 1)), (0.84, (1.0, 0.62, 0.26, 1))):
            q = e.new(pos); q.color = c
        mr = N.new('ShaderNodeMapRange'); mr.inputs['From Min'].default_value = -1.0; mr.inputs['From Max'].default_value = 1.0
        L.new(dp.outputs['Value'], mr.inputs['Value']); L.new(mr.outputs['Result'], rp.inputs['Fac'])
        lw = N.new('ShaderNodeLayerWeight'); lw.inputs['Blend'].default_value = 0.35
        fr = N.new('ShaderNodeMapRange'); fr.inputs['To Min'].default_value = 0.9; fr.inputs['To Max'].default_value = 2.4; L.new(lw.outputs['Facing'], fr.inputs['Value'])
        mk = N.new('ShaderNodeMath'); mk.operation = 'MULTIPLY'; L.new(vetro, mk.inputs[0]); L.new(fr.outputs['Result'], mk.inputs[1])
        mc = N.new('ShaderNodeMix'); mc.data_type = 'RGBA'; mc.blend_type = 'MULTIPLY'; mc.inputs['Factor'].default_value = 1.0     # il riflesso prende il disegno del vetro: resta scuro, ma colorato
        L.new(rp.outputs['Color'], mc.inputs['A']); L.new(col, mc.inputs['B'])
        parti.append(scala(mc.outputs['Result'], mk.outputs[0]))
    tot = parti[0]
    for q in parti[1:]:
        ad = N.new('ShaderNodeVectorMath'); ad.operation = 'ADD'; L.new(tot, ad.inputs[0]); L.new(q, ad.inputs[1]); tot = ad.outputs['Vector']
    for l in list(ecol.links):
        L.remove(l)
    L.new(tot, ecol); b.inputs['Emission Strength'].default_value = max(d.get('forza', 2.0), 1.0)
    _foschia(m)
    return m


def griglia_di(d, piano=PIANO):
    """(larghezza di una colonna, altezza di un piano, colonne per ripetizione, piani per ripetizione) di una facciata vera."""
    piano = d.get('piano', piano); lato = d['piani'] * piano
    return (lato / d['col'], piano, d['col'], d['piani'])


def mats_citta(tipo='C2', A=None, vere=None):
    """A = libreria asset: con A le facciate sono quelle vere (FACCIATE_VERE, o solo i nomi in «vere»); senza, quelle disegnate."""
    MC = _mats_citta_base(tipo)
    if A is not None:
        MC['n_base'] = len(MC['facciate'])
        scelte = [d for d in FACCIATE_VERE if (vere is None or d['nome'] in vere)]
        MC['facciate'] = [mat_facciata_vera(A, d) for d in scelte]
        MC['griglie'] = [griglia_di(d) for d in scelte]
        MC['alte'] = [d['alto'] for d in scelte]
        MC['nomi'] = [d['nome'] for d in scelte]
    return MC


def scegli_facciata(MC, h, rnd):
    """Indice della facciata per un palazzo alto h: le vetrate da grattacielo solo sui palazzi alti."""
    n = len(MC['facciate'])
    if 'alte' not in MC:
        return rnd.randrange(n)
    ok = [i for i in range(n) if (h >= 1.0 or not MC['alte'][i])] or list(range(n))
    pesi = MC.get('pesi') or [1.0] * n                                  # MC['pesi']: quanto spesso esce ogni facciata
    return rnd.choices(ok, weights=[pesi[i] for i in ok])[0]


def _mats_citta_base(tipo='C2'):
    S = props027.STILI_CITTA[tipo]
    muri = list(S['muri']) + ([(0.36, 0.44, 0.58), (0.88, 0.84, 0.78)] if tipo == 'C2' else [])        # in piu': una torre di vetro azzurro e una di pietra chiara
    fac = [mat_facciata('M27v_%s_%d' % (tipo, i), mu, S['vetro'], S['luci'][i % len(S['luci'])], S['soglia'], S['forza']) for i, mu in enumerate(muri)]
    return dict(
        facciate=fac,
        tetto=mat_semplice('M27v_tetto', (0.07, 0.065, 0.075), rough=0.85),
        asfalto=mat_semplice('M27v_asfalto', (0.035, 0.035, 0.045), rough=0.8),
        marciapiede=mat_semplice('M27v_marciapiede', (0.42, 0.40, 0.40), rough=0.9),
        righe=mat_semplice('M27v_righe', (0.95, 0.92, 0.80), rough=0.7, emit=(1.0, 0.95, 0.8), emit_strength=0.35),
        palo=mat_semplice('M27v_palo', (0.05, 0.05, 0.06), rough=0.5),
        lampione=material('M27v_lampione', (1.0, 0.85, 0.5), emit=(1.0, 0.80, 0.45), emit_strength=9.0),
        verde=mat_semplice('M27v_verde', (0.10, 0.30, 0.10), rough=0.9),
        faro_b=material('M27v_faro_b', (1.0, 0.95, 0.8), emit=(1.0, 0.93, 0.75), emit_strength=10.0),
        faro_r=material('M27v_faro_r', (1.0, 0.05, 0.02), emit=(1.0, 0.04, 0.02), emit_strength=7.0),
        polvere=material('M27v_polvere', (0.86, 0.80, 0.72), rough=1.0, emit=(0.95, 0.82, 0.66), emit_strength=0.22),
        onda=material('M27v_onda', (1.0, 0.9, 0.6), emit=(1.0, 0.85, 0.5), emit_strength=6.0),
    )


# --------------------------------------------------------------------------- geometria dei palazzi
def _livelli(sx, sy, h, rnd):
    """Un palazzo e' fatto di uno o piu' livelli (x0, x1, y0, y1, z0, z1): i grattacieli si stringono salendo."""
    liv = [(-sx / 2, sx / 2, -sy / 2, sy / 2, 0.0, h)]
    if h > 1.25 and rnd.random() < 0.75:
        k = rnd.uniform(0.55, 0.72); z1 = h * k; r = rnd.uniform(0.62, 0.8)
        liv = [(-sx / 2, sx / 2, -sy / 2, sy / 2, 0.0, z1), (-sx * r / 2, sx * r / 2, -sy * r / 2, sy * r / 2, z1, h)]
        if h > 1.9 and rnd.random() < 0.6:
            z2 = h * rnd.uniform(0.84, 0.9); r2 = r * 0.6
            liv[1] = (-sx * r / 2, sx * r / 2, -sy * r / 2, sy * r / 2, z1, z2); liv.append((-sx * r2 / 2, sx * r2 / 2, -sy * r2 / 2, sy * r2 / 2, z2, h))
    elif rnd.random() < 0.5:                                                    # casotto sul tetto
        a = rnd.uniform(0.25, 0.45); cx, cy = rnd.uniform(-0.2, 0.2) * sx, rnd.uniform(-0.2, 0.2) * sy
        liv.append((cx - sx * a / 2, cx + sx * a / 2, cy - sy * a / 2, cy + sy * a / 2, h, h + rnd.uniform(0.04, 0.10)))
    return liv


def _aggiungi(bm, uv, livelli, ox=0.0, oy=0.0, du=0.0, dv=0.0, antenna=0.0, griglia=None, rnd=None):
    """griglia = (larghezza colonna, altezza piano, colonne per ripetizione, piani per ripetizione): le UV vanno in ripetizioni
    della texture e ogni muro prende un numero INTERO di colonne e di piani (finestre mai tagliate). Senza griglia: UV in unita' di scena."""
    for (x0, x1, y0, y1, z0, z1) in livelli:
        v = [bm.verts.new((ox + x, oy + y, z)) for (x, y, z) in ((x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1))]
        if griglia:
            cw, ph, nc, npi = griglia
            p0 = int(round(z0 / ph)); p1 = max(p0 + 1, int(round(z1 / ph)))
            sv = (rnd.randrange(npi) if rnd else 0) / npi
        for a, b_, c, d, w in ((0, 1, 5, 4, x1 - x0), (1, 2, 6, 5, y1 - y0), (2, 3, 7, 6, x1 - x0), (3, 0, 4, 7, y1 - y0)):
            f = bm.faces.new((v[a], v[b_], v[c], v[d]))
            if griglia:
                k = max(1, int(round(w / cw))); su = (rnd.randrange(nc) if rnd else 0) / nc
                quad = ((su, p0 / npi + sv), (su + k / nc, p0 / npi + sv), (su + k / nc, p1 / npi + sv), (su, p1 / npi + sv))
            else:
                quad = ((du, z0 + dv), (w + du, z0 + dv), (w + du, z1 + dv), (du, z1 + dv))
            for l, q in zip(f.loops, quad):
                l[uv].uv = q
        f = bm.faces.new((v[4], v[5], v[6], v[7])); f.material_index = 1
        for l in f.loops:
            l[uv].uv = (0, 0)
    if antenna > 0:                                                             # asta sul tetto
        z = livelli[-1][5]; s = 0.008
        v = [bm.verts.new((ox + x, oy + y, zz)) for zz in (z, z + antenna) for (x, y) in ((-s, -s), (s, -s), (s, s), (-s, s))]
        for a, b_, c, d in ((0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7), (4, 5, 6, 7)):
            f = bm.faces.new((v[a], v[b_], v[c], v[d])); f.material_index = 1
            for l in f.loops:
                l[uv].uv = (0, 0)


def _mesh(nome, bm, mats, coll, loc=(0, 0, 0)):
    me = bpy.data.meshes.new(nome); bm.to_mesh(me); bm.free()
    for m in mats:
        me.materials.append(m)
    o = bpy.data.objects.new(nome, me); o.location = loc; coll.objects.link(o)
    return o


def _scatole(nome, lista, mat, coll, ombra=True):
    """Tante scatole (cx, cy, cz, sx, sy, sz) in una mesh sola."""
    bm = bmesh.new()
    for (cx, cy, cz, sx, sy, sz) in lista:
        r = bmesh.ops.create_cube(bm, size=1.0)
        for v in r['verts']:
            v.co = Vector((cx + v.co.x * sx, cy + v.co.y * sy, cz + v.co.z * sz))
    o = _mesh(nome, bm, [mat], coll)
    o.visible_shadow = ombra
    return o


# --------------------------------------------------------------------------- la citta'
def citta_vera(coll, MC, seme=11, colonne=(-6, 6), righe=(-7, 10), altezza=None, vicino=None, vuoto=None, origine=(0.0, 0.0), niente_isolato=None):
    """Isolati quadrati (lato 1, strade larghe 0,30) su una griglia: colonna i -> x = i * PASSO, riga j -> y = j * PASSO.
    Ogni isolato ha 2 x 2 palazzi. altezza(i, j, x, y, rnd) -> altezza del palazzo (default: bassi al centro, alti ai lati).
    vicino(x, y) -> True: il palazzo resta un oggetto a se' (puo' essere distrutto). vuoto(x, y) -> True: li' niente palazzo.
    origine = (ox, oy): sposta tutta la griglia. niente_isolato(i, j) -> True: quell'isolato non c'e' (piazza).
    Restituisce dict(palazzi=[...], strade_x=[y...], strade_y=[x...], limiti=(x0, x1, y0, y1))."""
    rnd = random.Random(seme); fac = MC['facciate']; ox, oy = origine
    rf = random.Random(seme * 7919 + 13); nb = MC.get('n_base', len(fac))      # rf: scelte delle facciate vere, senza toccare la sequenza di «rnd» (la citta' resta identica)
    def alt(i, j, x, y, r):
        a = abs(x)
        if a < 0.6: return r.uniform(0.28, 0.62)
        if a < 1.9: return r.uniform(0.55, 1.35)
        if a < 3.2: return r.uniform(0.9, 2.0)
        return r.uniform(1.1, 2.6)
    altezza = altezza or alt
    pal = []; fermi = [bmesh.new() for _ in fac]; fuv = [b.loops.layers.uv.new() for b in fermi]
    marc = []; verdi = []
    for i in range(colonne[0], colonne[1] + 1):
        for j in range(righe[0], righe[1] + 1):
            bx_, by_ = i * PASSO + ox, j * PASSO + oy
            if niente_isolato and niente_isolato(i, j):
                continue
            marc.append((bx_, by_, 0.007, LATO, LATO, 0.014))
            parco = (abs(i) >= 2 and rnd.random() < 0.07)
            if parco:                                                           # ogni tanto un giardino al posto dei palazzi
                verdi.append((bx_, by_, 0.02, LATO * 0.86, LATO * 0.86, 0.02))
                for _ in range(5):
                    verdi.append((bx_ + rnd.uniform(-0.33, 0.33), by_ + rnd.uniform(-0.33, 0.33), 0.09, 0.12, 0.12, 0.14))
                continue
            for qx in (-1, 1):
                for qy in (-1, 1):
                    x = bx_ + qx * 0.25 + rnd.uniform(-0.025, 0.025); y = by_ + qy * 0.25 + rnd.uniform(-0.025, 0.025)
                    if vuoto and vuoto(x, y):
                        continue
                    sx, sy = rnd.uniform(0.34, 0.45), rnd.uniform(0.34, 0.45)
                    h = altezza(i, j, x, y, rnd); mi = rnd.randrange(nb); gr = None
                    if 'griglie' in MC:
                        mi = scegli_facciata(MC, h, rf); gr = MC['griglie'][mi]
                    liv = _livelli(sx, sy, h, rnd); ant = rnd.uniform(0.12, 0.3) if (h > 1.5 and rnd.random() < 0.45) else 0.0
                    if vicino is None or vicino(x, y):
                        bm = bmesh.new(); uv = bm.loops.layers.uv.new(); _aggiungi(bm, uv, liv, antenna=ant, griglia=gr, rnd=rf)
                        o = _mesh('Palazzo', bm, [fac[mi], MC['tetto']], coll, loc=(x, y, 0))
                        pal.append(dict(o=o, x=x, y=y, sx=sx, sy=sy, h=h, stato='su', col=i, riga=j, mat=mi))
                    else:
                        _aggiungi(fermi[mi], fuv[mi], liv, ox=x, oy=y, du=rnd.randrange(40) * 0.07, dv=rnd.randrange(30) * 0.095, antenna=ant, griglia=gr, rnd=rf)
    x0 = (colonne[0] - 0.5) * PASSO + ox; x1 = (colonne[1] + 0.5) * PASSO + ox; y0 = (righe[0] - 0.5) * PASSO + oy; y1 = (righe[1] + 0.5) * PASSO + oy
    # skyline lontano: una corona di palazzoni che si perdono nella foschia
    for k in range(150):
        a = rnd.uniform(0, 2 * PI); d = rnd.uniform(1.0, 9.0)
        cx = (x0 + x1) / 2 + math.cos(a) * ((x1 - x0) / 2 + d); cy = (y0 + y1) / 2 + math.sin(a) * ((y1 - y0) / 2 + d)
        if x0 - 0.4 < cx < x1 + 0.4 and y0 - 0.4 < cy < y1 + 0.4:
            continue
        sx, sy = rnd.uniform(0.6, 1.2), rnd.uniform(0.6, 1.2); h = rnd.uniform(1.2, 3.4) + d * 0.12; mi = rnd.randrange(nb)
        if 'griglie' in MC:
            mi = scegli_facciata(MC, h, rf)
        _aggiungi(fermi[mi], fuv[mi], _livelli(sx, sy, h, rnd), ox=cx, oy=cy, du=rnd.randrange(40) * 0.07, dv=rnd.randrange(30) * 0.095,
                  griglia=MC['griglie'][mi] if 'griglie' in MC else None, rnd=rf)
    for mi, b in enumerate(fermi):
        _mesh('PalazziFermi%d' % mi, b, [fac[mi], MC['tetto']], coll)
    _scatole('Marciapiedi', marc, MC['marciapiede'], coll, ombra=False)
    if verdi:
        _scatole('Giardini', verdi, MC['verde'], coll)
    suolo = _scatole('Asfalto', [(0, 0, -0.05, 90, 90, 0.1)], MC['asfalto'], coll, ombra=False)
    # strade: righe tratteggiate al centro, strisce pedonali agli incroci, lampioni agli angoli degli isolati
    sx_ = [(j + 0.5) * PASSO + oy for j in range(righe[0], righe[1])]         # strade lungo X: una per ogni y
    sy_ = [(i + 0.5) * PASSO + ox for i in range(colonne[0], colonne[1])]     # strade lungo Y: una per ogni x
    righe_ = []; pali = []; luci = []
    for y in sx_:
        x = x0
        while x < x1:
            if abs(((x + 0.06 - ox) / PASSO - 0.5) % 1.0 - 0.0) > 0.16 and abs(((x + 0.06 - ox) / PASSO - 0.5) % 1.0 - 1.0) > 0.16:      # non dentro gli incroci
                righe_.append((x + 0.06, y, 0.002, 0.10, 0.012, 0.003))
            x += 0.2
    for xx in sy_:
        y = y0
        while y < y1:
            if abs(((y + 0.06 - oy) / PASSO - 0.5) % 1.0 - 0.0) > 0.16 and abs(((y + 0.06 - oy) / PASSO - 0.5) % 1.0 - 1.0) > 0.16:
                righe_.append((xx, y + 0.06, 0.002, 0.012, 0.10, 0.003))
            y += 0.2
    for xx in sy_:
        for y in sx_:
            for s in (-1, 1):                                                   # strisce pedonali sui quattro lati dell'incrocio
                for k in range(5):
                    t = -0.11 + 0.055 * k
                    righe_.append((xx + s * (STRADA / 2 + 0.045), y + t, 0.002, 0.05, 0.022, 0.003))
                    righe_.append((xx + t, y + s * (STRADA / 2 + 0.045), 0.002, 0.022, 0.05, 0.003))
            for sa in (-1, 1):                                                  # un lampione su due angoli
                px, py = xx + sa * (STRADA / 2 + 0.03), y + sa * (STRADA / 2 + 0.03)
                pali.append((px, py, 0.06, 0.008, 0.008, 0.12)); luci.append((px - sa * 0.03, py - sa * 0.03, 0.122, 0.035, 0.035, 0.012))
    _scatole('Righe', righe_, MC['righe'], coll, ombra=False)
    _scatole('Pali', pali, MC['palo'], coll, ombra=False)
    _scatole('Lampioni', luci, MC['lampione'], coll, ombra=False)
    return dict(palazzi=pal, strade_x=sx_, strade_y=sy_, limiti=(x0, x1, y0, y1), suolo=suolo)


def palazzo_singolo(coll, MC, x, y, sx, sy, h, mi=0, seme=0, antenna=0.0, nome='Grattacielo', livelli=True):
    """Un palazzo messo a mano (i bersagli dei colpi di Pippo). Restituisce il dizionario come quelli di citta_vera."""
    rnd = random.Random(seme); fac = MC['facciate']
    liv = _livelli(sx, sy, h, rnd) if livelli else [(-sx / 2, sx / 2, -sy / 2, sy / 2, 0.0, h)]
    mi = mi % len(fac)
    bm = bmesh.new(); uv = bm.loops.layers.uv.new(); _aggiungi(bm, uv, liv, antenna=antenna, griglia=MC['griglie'][mi] if 'griglie' in MC else None, rnd=rnd)
    o = _mesh(nome, bm, [fac[mi], MC['tetto']], coll, loc=(x, y, 0))
    return dict(o=o, x=x, y=y, sx=sx, sy=sy, h=h, stato='su', col=0, riga=0, mat=mi, bersaglio=nome)


# --------------------------------------------------------------------------- macchine
def modelli_auto(A, MC, altezza=0.062):
    """Carica una volta i cinque modelli di auto della libreria (KayKit city-builder-bits) e fa di ognuno UNA mesh,
    con i fari davanti (bianchi) e dietro (rossi) che fanno luce. Lunghezza lungo Y. Restituisce una lista di mesh."""
    out = []
    for nome in ('car_taxi', 'car_sedan', 'car_hatchback', 'car_stationwagon', 'car_police'):
        r = A.modello('kaykit/city-builder-bits/' + nome, altezza=altezza)
        bpy.context.view_layer.update()
        figli = [c for c in [r] + list(r.children_recursive) if c.type == 'MESH']
        bm = bmesh.new(); mats = []; inv = r.matrix_world.inverted()
        for c in figli:
            tmp = bmesh.new(); tmp.from_mesh(c.data); idx = {}
            for k, sl in enumerate(c.material_slots):
                if sl.material not in mats: mats.append(sl.material)
                idx[k] = mats.index(sl.material)
            me2 = bpy.data.meshes.new('tmp');
            for f in tmp.faces: f.material_index = idx.get(f.material_index, 0)
            tmp.transform(inv @ c.matrix_world); tmp.to_mesh(me2); tmp.free()
            bm.from_mesh(me2); bpy.data.meshes.remove(me2)
        xs = [v.co.x for v in bm.verts]; ys = [v.co.y for v in bm.verts]; zs = [v.co.z for v in bm.verts]
        sc = r.scale.x                                                           # la scala sta sulla radice: la porto nella mesh
        for v in bm.verts: v.co = v.co * sc
        x0, x1, y0, y1, z1 = min(xs) * sc, max(xs) * sc, min(ys) * sc, max(ys) * sc, max(zs) * sc
        nb, nr = len(mats), len(mats) + 1
        for (yy, mi) in ((y0 - 0.0015, nb), (y1 + 0.0015, nr)):                # fari: davanti = -Y
            for sx_ in (-1, 1):
                cx = sx_ * (x1 - x0) * 0.30; cz = z1 * 0.40; a = 0.008
                vv = [bm.verts.new((cx + dx, yy, cz + dz)) for dx, dz in ((-a, -a * 0.7), (a, -a * 0.7), (a, a * 0.7), (-a, a * 0.7))]
                f = bm.faces.new(vv); f.material_index = mi
        me = bpy.data.meshes.new('M27_' + nome); bm.to_mesh(me); bm.free()
        for m in mats + [MC['faro_b'], MC['faro_r']]:
            me.materials.append(m)
        me['lung'] = y1 - y0; me['larg'] = x1 - x0
        for c in [r] + list(r.children_recursive):
            bpy.data.objects.remove(c, do_unlink=True)
        out.append(me)
    return out


class Traffico:
    """Macchine che girano sulle strade. Tutte alla stessa velocita' e in fase con la griglia, cosi' agli incroci non si scontrano
    (quelle lungo X passano l'incrocio quando quelle lungo Y sono a meta' isolato). Si fermano davanti a un ostacolo
    (il piede di Pippo, un palazzo caduto, un'auto ferma) e vengono schiacciate da quello che gli cade sopra.
    Uso: T = Traffico(...); per ogni fotogramma T.passo(f, ostacoli); alla fine T.chiavi()."""
    def __init__(self, coll, meshes, C, seme=5, v=0.42, zona=(-4.6, 4.6, -6.6, 9.2), pieno=0.62, fps=24, scala=1.0, strada_ok=None):
        rnd = random.Random(seme); self.fps = fps; self.v = v; self.auto = []; self.coll = coll; self.eventi = []
        x0, x1, y0, y1 = C['limiti']; P = PASSO
        def corsia(asse, c, verso):
            # asse 'x': strada a y = c, si muove lungo x; asse 'y': strada a x = c, si muove lungo y
            a0, a1 = (x0, x1) if asse == 'x' else (y0, y1); L = a1 - a0
            fase = 0.0 if asse == 'x' else P / 2
            n = int(round(L / P))
            for k in range(n):
                if rnd.random() > pieno: continue
                # posizione al tempo 0: all'incrocio quando v*t = fase (mod P)
                s0 = (0.5 * P - fase * verso) + k * P                           # misurata dal bordo a0 della griglia degli isolati
                s0 = s0 % L
                m = rnd.choice(meshes); o = bpy.data.objects.new('Auto', m); coll.objects.link(o); o.scale = (scala,) * 3
                lat = -verso * 0.068 if asse == 'x' else verso * 0.068          # si tiene la destra
                self.auto.append(dict(o=o, asse=asse, c=c + lat, verso=verso, s=s0, a0=a0, L=L, stato='va', ferma=False, lung=m['lung'] * scala,
                                      tr=[], prev=None, zona=zona))
        ok = strada_ok or (lambda asse, c: True)
        for y in C['strade_x']:
            if zona[2] <= y <= zona[3] and ok('x', y):
                corsia('x', y, 1); corsia('x', y, -1)
        for x in C['strade_y']:
            if zona[0] <= x <= zona[1] and ok('y', x):
                corsia('y', x, 1); corsia('y', x, -1)

    @staticmethod
    def pos(a, s=None):
        s = a['s'] if s is None else s
        u = a['a0'] + (s if a['verso'] > 0 else a['L'] - s)
        return Vector((u, a['c'], 0.0)) if a['asse'] == 'x' else Vector((a['c'], u, 0.0))

    def aggiungi(self, mesh, x, y, rot=0.0, scala=1.0):
        """Un'auto ferma messa a mano (parcheggiata o in mezzo alla strada)."""
        o = bpy.data.objects.new('AutoFerma', mesh); self.coll.objects.link(o); o.location = (x, y, 0.0); o.rotation_euler = (0, 0, rot); o.scale = (scala,) * 3
        a = dict(o=o, asse='p', c=0, verso=1, s=0, a0=0, L=1, stato='parcheggiata', ferma=True, lung=mesh['lung'] * scala, tr=[], prev=None, xy=Vector((x, y, 0)))
        self.auto.append(a); return a

    def dove(self, a):
        return a['xy'] if a['asse'] == 'p' else self.pos(a)

    def passo(self, f, cerchi=(), rettangoli=()):
        """Avanza di un fotogramma. cerchi = [(x, y, r)] ostacoli tondi (piedi a terra); rettangoli = [(x0, x1, y0, y1)] (palazzi caduti)."""
        dt = 1.0 / self.fps
        fermi = [(self.dove(b).x, self.dove(b).y, b) for b in self.auto if b['stato'] != 'va' or b['ferma']]
        for a in self.auto:
            if a['stato'] != 'va':
                continue
            p = self.pos(a); px, py = p.x, p.y
            dx, dy = ((a['verso'], 0.0) if a['asse'] == 'x' else (0.0, a['verso']))
            blocco = False
            for (cx, cy, r) in cerchi:                                           # qualcosa davanti entro 0,3?
                av = (cx - px) * dx + (cy - py) * dy; lat = abs((cx - px) * dy - (cy - py) * dx)
                if -0.02 < av < 0.30 + r and lat < r + 0.05: blocco = True; break
            if not blocco:
                qx, qy = px + dx * 0.22, py + dy * 0.22
                for (rx0, rx1, ry0, ry1) in rettangoli:
                    if rx0 - 0.03 < qx < rx1 + 0.03 and ry0 - 0.03 < qy < ry1 + 0.03: blocco = True; break
            if not blocco:
                for (bx_, by_, b) in fermi:                                      # un'auto ferma davanti nella stessa corsia
                    if b is a: continue
                    av = (bx_ - px) * dx + (by_ - py) * dy
                    if 0.0 < av < 0.26 and abs((bx_ - px) * dy - (by_ - py) * dx) < 0.05: blocco = True; break
            if blocco and not a['ferma']:
                self.eventi.append(dict(tipo='clacson', f=f, x=px, y=py))
            a['ferma'] = blocco
            if not blocco:
                a['s'] += self.v * dt
                if a['s'] >= a['L']:
                    a['s'] -= a['L']; a['tr'].append((f, 'salto'))
            a['tr'].append((f, self.pos(a).copy(), blocco))

    def schiaccia_sotto(self, f, cerchi=(), rettangoli=()):
        """Schiaccia le auto che stanno sotto un piede che atterra (cerchi) o sotto un palazzo caduto (rettangoli). Restituisce quelle colpite."""
        out = []
        for a in self.auto:
            if a['stato'] == 'piatta': continue
            p = self.dove(a); colpita = any((p.x - cx) ** 2 + (p.y - cy) ** 2 < (r + 0.03) ** 2 for (cx, cy, r) in cerchi) or \
                any(rx0 < p.x < rx1 and ry0 < p.y < ry1 for (rx0, rx1, ry0, ry1) in rettangoli)
            if colpita:
                a['stato'] = 'piatta'; a['f_piatta'] = f; out.append(a)
                self.eventi.append(dict(tipo='auto', f=f, x=p.x, y=p.y))
        return out

    def salta(self, f, x, y, raggio=1.6, forza=1.0):
        """Le auto vicine a un colpo fanno un saltello (chiavi su z)."""
        for a in self.auto:
            if a['stato'] == 'piatta': continue
            p = self.dove(a); d = math.hypot(p.x - x, p.y - y)
            if d < raggio:
                a.setdefault('salti', []).append((f + int(d * 3), 0.05 * forza * (1 - d / raggio) + 0.01))

    def chiavi(self, f_fine):
        """Scrive le chiavi: tratti dritti (poche chiavi su x e y), salto da un capo all'altro della strada, saltelli (z), schiacciate (scala)."""
        for a in self.auto:
            o = a['o']
            if a['asse'] != 'p':
                o.rotation_euler = (0, 0, {('x', 1): PI / 2, ('x', -1): -PI / 2, ('y', 1): PI, ('y', -1): 0.0}[(a['asse'], a['verso'])])
                tr = [t for t in a['tr'] if t[1] != 'salto']; salti = set(t[0] for t in a['tr'] if t[1] == 'salto'); ch = set()
                for i, (f, p, fermo) in enumerate(tr):
                    if i == 0 or i == len(tr) - 1: ch.add(i)
                    if f in salti: ch.add(i); ch.add(i - 1)
                    if i and fermo != tr[i - 1][2]: ch.add(i); ch.add(i - 1)
                for i in sorted(x for x in ch if x >= 0):
                    f, p, fermo = tr[i]; o.location = (p.x, p.y, 0.0)
                    o.keyframe_insert('location', index=0, frame=f); o.keyframe_insert('location', index=1, frame=f)
            base = {}                                                            # saltelli: chiavi su z
            for (f, h) in a.get('salti', []):
                if a.get('f_piatta') and f >= a['f_piatta'] - 1: continue
                for df, k in ((0, 0.0), (2, 1.0), (4, 0.0)):
                    base[f + df] = max(base.get(f + df, 0.0), h * k)
            for f in sorted(base):
                o.location.z = base[f]; o.keyframe_insert('location', index=2, frame=f)
            o.location.z = 0.0
            if a['stato'] == 'piatta':
                f = a['f_piatta']; sc = o.scale.x
                o.scale = (sc, sc, sc); o.keyframe_insert('scale', frame=max(1, f - 1))
                for df, z in ((0, 0.45), (1, 0.14), (3, 0.20), (5, 0.16)):
                    o.scale = (sc * 1.25, sc * 1.18, sc * z); o.keyframe_insert('scale', frame=f + df)


# --------------------------------------------------------------------------- effetti
class Sbuffi:
    """Sbuffi di polvere da cartone: palline che si gonfiano e spariscono. Un mucchio di palline riusate nel tempo."""
    def __init__(self, coll, mat, n=90, seme=3):
        self.o = []; self.lib = []; self.rnd = random.Random(seme)
        for i in range(n):
            o = shape('Sbuffo', 'sphere_lo', loc=(0, 0, -3), scale=(0, 0, 0), mat=mat, coll=coll); o.visible_shadow = False
            o.keyframe_insert('scale', frame=1); o.keyframe_insert('location', frame=1)
            self.o.append(o); self.lib.append(2)

    def uno(self, f, p0, p1, r, dur):
        i = min(range(len(self.o)), key=lambda j: self.lib[j])
        if self.lib[i] > f - 1:
            return False
        o = self.o[i]
        o.scale = (0, 0, 0); o.keyframe_insert('scale', frame=f - 1); o.location = p0; o.keyframe_insert('location', frame=f - 1)
        for df, k in ((1, 0.65), (3, 1.0), (int(dur * 0.6), 0.8), (dur, 0.0)):
            o.scale = (r * k,) * 3; o.keyframe_insert('scale', frame=f + df)
        o.location = p1; o.keyframe_insert('location', frame=f + dur)
        self.lib[i] = f + dur + 2
        return True

    def nuvola(self, f, x, y, raggio=0.3, n=6, grande=0.12, z=0.04, dur=14, dir=None):
        """n sbuffi attorno a (x, y) che si allargano. dir = (dx, dy): solo da quella parte."""
        rnd = self.rnd
        for k in range(n):
            a = rnd.uniform(0, 2 * PI) if dir is None else math.atan2(dir[1], dir[0]) + rnd.uniform(-1.0, 1.0)
            d0 = raggio * rnd.uniform(0.2, 0.6); d1 = raggio * rnd.uniform(0.9, 1.5)
            p0 = (x + math.cos(a) * d0, y + math.sin(a) * d0, z + rnd.uniform(0, grande * 0.5))
            p1 = (x + math.cos(a) * d1, y + math.sin(a) * d1, z + rnd.uniform(0.05, 0.25))
            self.uno(f + rnd.randrange(0, 3), p0, p1, grande * rnd.uniform(0.6, 1.25), dur + rnd.randrange(-3, 5))


class Scoppi:
    """Pezzi che schizzano via (calcinacci o coriandoli): una mesh con due chiavi di forma, «fuori» (si allargano) e «giu»
    (cadono); animate insieme danno un arco da lancio. Un mucchio di mesh riusate nel tempo."""
    def __init__(self, coll, colori, n=18, pezzi=28, seme=9, nome='Calcinacci', lato=(0.018, 0.045), piatti=False, luce=0.0, giu=1.0, raggio=1.0):
        rnd = random.Random(seme); self.o = []; self.lib = []; self.k = []
        mats = [material('M27v_%s_%d' % (nome, i), c, rough=0.8, emit=c if luce > 0 else None, emit_strength=luce) for i, c in enumerate(colori)]
        for i in range(n):
            bm = bmesh.new(); gruppi = []
            for p in range(pezzi):
                s = rnd.uniform(*lato); r = bmesh.ops.create_cube(bm, size=1.0)
                E = Euler((rnd.uniform(0, PI), rnd.uniform(0, PI), rnd.uniform(0, PI))).to_matrix()
                sc = Vector((s, s * rnd.uniform(0.6, 1.4), s * (0.12 if piatti else rnd.uniform(0.5, 1.2))))
                mi = rnd.randrange(len(mats))
                for v in r['verts']:
                    v.co = E @ Vector((v.co.x * sc.x, v.co.y * sc.y, v.co.z * sc.z))
                for f in set(f for v in r['verts'] for f in v.link_faces):
                    f.material_index = mi
            bm.verts.ensure_lookup_table(); bm.faces.ensure_lookup_table()
            idx = [[v.index for v in bm.verts[p * 8:(p + 1) * 8]] for p in range(pezzi)]
            me = bpy.data.meshes.new(nome); bm.to_mesh(me); bm.free()
            for m in mats:
                me.materials.append(m)
            o = bpy.data.objects.new(nome, me); coll.objects.link(o); o.visible_shadow = False
            o.shape_key_add(name='Basis'); k1 = o.shape_key_add(name='fuori'); k2 = o.shape_key_add(name='giu')
            for g in idx:
                a = rnd.uniform(0, 2 * PI); el = rnd.uniform(0.25, 1.35); d = rnd.uniform(0.35, 1.0) * raggio
                off1 = Vector((math.cos(a) * math.cos(el), math.sin(a) * math.cos(el), math.sin(el))) * d
                off2 = Vector((off1.x * 0.35, off1.y * 0.35, -giu * rnd.uniform(0.7, 1.3) * (0.4 + off1.z)))
                for vi in g:
                    k1.data[vi].co = me.vertices[vi].co + off1; k2.data[vi].co = me.vertices[vi].co + off2
            o.scale = (0, 0, 0); o.keyframe_insert('scale', frame=1); o.location = (0, 0, -3); o.keyframe_insert('location', frame=1)
            k1.value = 0; k2.value = 0; k1.keyframe_insert('value', frame=1); k2.keyframe_insert('value', frame=1)
            self.o.append(o); self.lib.append(2); self.k.append((k1, k2))

    def uno(self, f, pos, scala=1.0, dur=20):
        i = min(range(len(self.o)), key=lambda j: self.lib[j])
        if self.lib[i] > f - 1:
            return False
        o = self.o[i]; k1, k2 = self.k[i]
        o.scale = (0, 0, 0); o.keyframe_insert('scale', frame=f - 1); o.location = pos; o.keyframe_insert('location', frame=f - 1)
        k1.value = 0; k2.value = 0; k1.keyframe_insert('value', frame=f - 1); k2.keyframe_insert('value', frame=f - 1)
        for df in range(0, dur + 1):
            t = df / dur
            k1.value = 1 - (1 - t) ** 2.4; k2.value = t * t
            k1.keyframe_insert('value', frame=f + df); k2.keyframe_insert('value', frame=f + df)
        o.scale = (scala,) * 3; o.keyframe_insert('scale', frame=f); o.keyframe_insert('scale', frame=f + dur - 4)
        o.scale = (0, 0, 0); o.keyframe_insert('scale', frame=f + dur)
        self.lib[i] = f + dur + 2
        return True


def onda_urto(coll, mat, f, x, y, raggio=5.0, dur=14, nome='Onda'):
    """Anello luminoso che si allarga per terra dal punto del colpo."""
    o = props024.anello(nome, 1.0, 0.018, mat, coll, loc=(x, y, 0.03)); o.visible_shadow = False
    o.scale = (0, 0, 0); o.keyframe_insert('scale', frame=1); o.keyframe_insert('scale', frame=f - 1)
    for df in range(0, dur + 1):
        t = df / dur; r = raggio * (1 - (1 - t) ** 2); sp = (1 - t) * 3.0 + 0.2
        o.scale = (r, r, sp); o.keyframe_insert('scale', frame=f + df)
    o.scale = (0, 0, 0); o.keyframe_insert('scale', frame=f + dur + 1)
    return o


# --------------------------------------------------------------------------- distruzione dei palazzi
def anim_schiaccia(pal, f, lento=False):
    """Il palazzo si schiaccia a fisarmonica (lento = crolla su se stesso in mezzo secondo). Restituisce il fotogramma in cui e' a terra."""
    o = pal['o']
    o.scale = (1, 1, 1); o.keyframe_insert('scale', frame=max(1, f - 1))
    prof = ((0, 0.9), (1, 0.76), (2, 0.58), (3, 0.40), (4, 0.25), (5, 0.15), (6, 0.10), (8, 0.14), (10, 0.11)) if lento else ((0, 0.5), (1, 0.16), (2, 0.08), (4, 0.13), (6, 0.10))
    for df, z in prof:
        k = 1 + (1 - z) * 0.2
        o.scale = (k, k, z); o.keyframe_insert('scale', frame=f + df)
    pal['stato'] = 'piatto'; pal['f'] = f
    return f + (6 if lento else 2)


def durata_caduta(h, fps=24):
    return max(7, int(round(fps * (0.30 + 0.13 * h))))


def anim_ribalta(pal, f, verso, fps=24):
    """Il palazzo cade come un birillo nella direzione verso ('+x', '-x', '+y', '-y') girando sullo spigolo di base, poi si
    appiattisce con un rimbalzo. Restituisce (fotogramma dell'impatto, rettangolo a terra (x0, x1, y0, y1))."""
    o = pal['o']; d = CARD[verso]; lato = pal['sx'] if verso[1] == 'x' else pal['sy']; largo = pal['sy'] if verso[1] == 'x' else pal['sx']
    c = Vector((pal['x'], pal['y'], 0.0)); T = durata_caduta(pal['h'], fps)
    o.rotation_euler = (0, 0, 0); o.keyframe_insert('rotation_euler', frame=max(1, f - 1))
    o.location = c; o.keyframe_insert('location', frame=max(1, f - 1))
    o.scale = (1, 1, 1); o.keyframe_insert('scale', frame=max(1, f - 1))
    def posa(th, piatto=1.0):
        if verso == '+x': o.rotation_euler = (0, th, 0)
        elif verso == '-x': o.rotation_euler = (0, -th, 0)
        elif verso == '+y': o.rotation_euler = (-th, 0, 0)
        else: o.rotation_euler = (th, 0, 0)
        o.location = c + d * (lato / 2) * (1 - math.cos(th)) + Vector((0, 0, (lato / 2) * math.sin(th) * piatto))
        o.scale = (piatto if verso[1] == 'x' else 1.0, piatto if verso[1] == 'y' else 1.0, 1.0)
    for k in range(0, T + 1):
        posa((PI / 2) * (k / T) ** 2.3)
        o.keyframe_insert('rotation_euler', frame=f + k); o.keyframe_insert('location', frame=f + k)
    for df, pz in ((1, 0.6), (2, 0.40), (4, 0.52), (6, 0.45)):                 # impatto: si appiattisce e rimbalza
        posa(PI / 2, pz)
        o.keyframe_insert('location', frame=f + T + df); o.keyframe_insert('scale', frame=f + T + df)
    o.scale = (1, 1, 1); o.keyframe_insert('scale', frame=f + T)
    a = c + d * (lato / 2); b = a + d * pal['h']                                 # striscia a terra dallo spigolo alla cima
    if verso[1] == 'x':
        ret = (min(a.x, b.x), max(a.x, b.x), c.y - largo / 2, c.y + largo / 2)
    else:
        ret = (c.x - largo / 2, c.x + largo / 2, min(a.y, b.y), max(a.y, b.y))
    pal['stato'] = 'caduto'; pal['f'] = f; pal['f_terra'] = f + T; pal['ret'] = ret; pal['verso'] = verso
    return f + T, ret


def verso_cardinale(dx, dy):
    if abs(dx) >= abs(dy):
        return '+x' if dx >= 0 else '-x'
    return '+y' if dy >= 0 else '-y'
