"""Luce «cinema» per tutti i video di Pippo e Tumbo (regola dell'autore dal 17 novembre 2026, scelta sulla scheda schede/luci017.png).
L'idea: niente luce piatta dall'alto. Una luce principale calda, di lato e dall'alto, con ombre nette; un riempimento freddo e debole dal lato della camera;
un controluce azzurro alle spalle che stacca i personaggi dal fondo; poca luce ambiente dal cielo.

Uso tipico (dopo aver creato il cielo con A.cielo e la camera):
    import luci
    luci.cielo_basso(scene.world, 0.15)                 # il cielo si VEDE com'e', ma illumina poco (0.15 interni, 0.35-0.5 esterni)
    L = luci.cinema(coll, soggetto=(x, y, 1.0), camera=(cx, cy, cz))     # tre luci attorno al soggetto, pensate per quella camera
    luci.ombre_pulite(scene)                            # ombre nette senza grana anche a 4 campioni
Per un secondo ambiente lontano (es. una stanza a x = 200) richiama cinema() con un altro nome e spegni con le chiavi di visibilita' le luci dell'ambiente non inquadrato.
All'aperto: stessa idea con sole() al posto della luce principale (sole basso e caldo di lato) e cielo_basso(world, 0.4).
I valori di riferimento sono quelli del video 017 (scripts/anim017.py, variante C)."""
import math, bpy
from mathutils import Vector

CALDA = (1.0, 0.78, 0.5); FREDDA = (0.75, 0.85, 1.0); AZZURRA = (0.65, 0.8, 1.0)

def punta(o, verso):
    """gira una luce (o una camera) verso un punto."""
    o.rotation_euler = (Vector(verso) - Vector(o.location)).to_track_quat('-Z', 'Y').to_euler(); return o

def _luce(coll, nome, tipo, pos, verso, energia, colore, ombra=True, **k):
    l = bpy.data.lights.new(nome, tipo); l.energy = energia; l.color = colore; l.use_shadow = ombra
    for a, v in k.items(): setattr(l, a, v)
    o = bpy.data.objects.new(nome, l); coll.objects.link(o); o.location = pos; return punta(o, verso)

def cinema(coll, soggetto, camera, distanza=4.5, forza=1.0, lato=1, altezza=1.85, nome='Cinema', riempimento=1.0, controluce=1.0):
    """Tre luci attorno al soggetto, viste dalla camera. soggetto e camera sono punti (x, y, z).
    lato = +1 mette la luce principale a destra della camera, -1 a sinistra (scegli il lato verso cui guardano le facce).
    distanza = quanto sta lontana la luce principale dal soggetto: l'energia viene scalata da sola. forza = moltiplicatore generale.
    Restituisce dict(chiave, riempimento, controluce): tre oggetti luce nella collezione coll."""
    s = Vector(soggetto); c = Vector(camera); d = Vector((c.x - s.x, c.y - s.y, 0.0))
    if d.length < 1e-6: d = Vector((0, -1, 0))
    d.normalize(); r = Vector((-d.y, d.x, 0.0)) * lato                      # d = dal soggetto verso la camera; r = di lato
    k = (distanza / 4.5) ** 2 * forza
    a = math.radians(28)                                                       # la principale: 28 gradi di lato rispetto alla camera, in alto
    pk = s + (d * math.cos(a) + r * math.sin(a)) * distanza + Vector((0, 0, altezza))
    chiave = _luce(coll, nome + 'Chiave', 'SPOT', pk, s, 3400 * k, CALDA, True, spot_size=1.25, spot_blend=0.7, shadow_soft_size=0.05)
    pf = s + (d * 0.75 - r * 0.65) * distanza + Vector((0, 0, altezza * 0.7))  # riempimento: dall'altra parte della camera, debole e freddo, senza ombre
    fill = _luce(coll, nome + 'Riempimento', 'AREA', pf, s, 40 * k * riempimento, FREDDA, False, size=3.0)
    pr = s + (-d * 0.8 - r * 0.6) * distanza * 0.75 + Vector((0, 0, altezza * 0.85))   # controluce: dietro il soggetto, dal lato opposto alla principale
    rim = _luce(coll, nome + 'Controluce', 'AREA', pr, s + Vector((0, 0, 0.3)), 520 * k * controluce, AZZURRA, False, size=1.5)
    return dict(chiave=chiave, riempimento=fill, controluce=rim)

def sole(coll, verso_camera, lato=1, energia=4.5, angolo_alto=32, nome='SoleCinema'):
    """All'aperto: un sole caldo e basso di lato al posto della luce principale. verso_camera = direzione (x, y) dal soggetto alla camera."""
    d = Vector((verso_camera[0], verso_camera[1], 0.0)).normalized(); r = Vector((-d.y, d.x, 0.0)) * lato; e = math.radians(angolo_alto)
    da = (d * 0.55 + r * 0.85).normalized() * math.cos(e) + Vector((0, 0, math.sin(e)))            # da dove arriva la luce
    return _luce(coll, nome, 'SUN', (0, 0, 20), Vector((0, 0, 20)) - da, energia, (1.0, 0.86, 0.66), True, angle=math.radians(1.5))

def cielo_basso(world, luce=0.15, vista=None):
    """Il cielo resta visibile com'e' (o con forza `vista`), ma illumina la scena con forza `luce`. Restituisce il nodo che comanda la luce
    (per metterci le chiavi: nodo.inputs['Strength']). In Eevee la luce del cielo entra anche nelle stanze chiuse: per un interno buio va quasi a zero."""
    nt = world.node_tree; bg = next(n for n in nt.nodes if n.type == 'BACKGROUND'); out = next(n for n in nt.nodes if n.type == 'OUTPUT_WORLD')
    if nt.nodes.get('PT_cielo_vista'): bg.inputs['Strength'].default_value = luce; return bg
    v = bg.inputs['Strength'].default_value if vista is None else vista
    bg2 = nt.nodes.new('ShaderNodeBackground'); bg2.name = 'PT_cielo_vista'; bg2.inputs['Strength'].default_value = v
    if bg.inputs['Color'].is_linked: nt.links.new(bg.inputs['Color'].links[0].from_socket, bg2.inputs['Color'])
    else: bg2.inputs['Color'].default_value = bg.inputs['Color'].default_value
    lp = nt.nodes.new('ShaderNodeLightPath'); mix = nt.nodes.new('ShaderNodeMixShader')
    nt.links.new(lp.outputs['Is Camera Ray'], mix.inputs['Fac']); nt.links.new(bg.outputs['Background'], mix.inputs[1]); nt.links.new(bg2.outputs['Background'], mix.inputs[2]); nt.links.new(mix.outputs['Shader'], out.inputs['Surface'])
    bg.inputs['Strength'].default_value = luce; return bg

def ombre_pulite(scene, raggi=2, mezza_risoluzione=True):
    """Ombre nette senza grana a pochi campioni: due raggi per le ombre e, negli interni, mappe a meta' risoluzione (non si vede la differenza, il render e' piu' svelto).
    Le luci larghe con le ombre accese fanno grana quando la luce ambiente e' poca: lasciale senza ombre (use_shadow = False) e fai fare le ombre solo alla luce principale."""
    scene.eevee.shadow_ray_count = raggi
    if mezza_risoluzione: scene.eevee.shadow_resolution_scale = 0.5

if __name__ == '__main__':                                                     # prova veloce: crea le luci in una scena vuota
    bpy.ops.wm.read_factory_settings(use_empty=True); sc = bpy.context.scene; sc.world = bpy.data.worlds.new('W'); sc.world.use_nodes = True
    L = cinema(sc.collection, (0, 0, 1), (3, -4, 1.6)); S = sole(sc.collection, (3, -4)); n = cielo_basso(sc.world, 0.15); ombre_pulite(sc)
    print({k: tuple(round(v, 2) for v in o.location) for k, o in L.items()}, round(n.inputs['Strength'].default_value, 2), S.data.type)
