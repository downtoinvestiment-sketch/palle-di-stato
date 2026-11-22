"""Copertine per le storie in evidenza di Instagram: un personaggio per immagine, 1080x1920, sfondo colorato,
personaggio al centro (il cerchio della storia in evidenza mostra il centro). Uso: python copertine_storie.py [nome]
Escono in ../out/storie/ e ../schede/storie_personaggi.png (anteprima dei cerchi)."""
import sys, os, math
QUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, QUI)
import bpy
from mathutils import Vector
from common import *
from render_setup import *
import set004, luci, pippo2, tumbo, props009, giulia, props012, eleonora
OUT = os.path.join(QUI, '..', 'out', 'storie'); os.makedirs(OUT, exist_ok=True)

# nome: (colore sfondo, punto inquadrato, distanza camera, direzione camera, lente)
PERSONAGGI = {      # colore sfondo, punto inquadrato, distanza, direzione camera, lente, (nome, posizione del nome, misura)
    'pippo':     ((0.30, 0.62, 1.00), (0, 0, 1.78), 3.3, (0.30, -1, 0.06), 50, ('PIPPO', (0, 0, 2.30), 0.42)),
    'tumbo':     ((1.00, 0.80, 0.25), (0, -0.25, 0.68), 2.1, (0.40, -1, 0.12), 50, ('TUMBO', (0, -0.30, 1.05), 0.30)),
    'gualtiero': ((0.45, 0.80, 0.50), (0, 0, 1.80), 3.4, (-0.30, -1, 0.06), 50, ('GUALTIERO', (0, 0, 2.38), 0.34)),
    'giulia':    ((1.00, 0.55, 0.70), (0.1, 0, 1.78), 3.9, (0.25, -1, 0.06), 50, ('GIULIA', (0, 0, 2.55), 0.42)),
    'eleonora':  ((1.00, 0.90, 0.45), (0, 0, 1.45), 3.0, (0.20, -1, 0.05), 50, ('ELEONORA', (0, 0, 2.12), 0.32)),
    'prete':     ((0.70, 0.60, 1.00), (0, -0.6, 1.25), 3.4, (0.45, -1, 0.12), 50, ('IL PRETE', (0, -0.85, 1.80), 0.34)),
}


COLORE_NOME = {'tumbo': (0.85, 0.05, 0.08), 'eleonora': (0.04, 0.36, 0.05)}   # sugli sfondi gialli il giallo non si legge


def nome_3d(coll, testo, pos, misura, verso_camera, colore=(1.0, 0.80, 0.08)):
    """Scritta 3D sopra la testa: lettere gialle in rilievo con bordo scuro, girate verso la camera."""
    from props007 import text_obj
    font = bpy.data.fonts.load(os.path.join(QUI, '..', 'assets', 'font', 'LuckiestGuy-Regular.ttf'), check_existing=True)
    d = Vector(verso_camera); yaw = math.atan2(d.x, -d.y)
    giallo = material('NomeColore', colore, rough=0.35, spec=0.6)
    scuro = material('NomeBordo3', (0.015, 0.012, 0.03), rough=1.0, spec=0.0)
    avanti = Vector((math.sin(yaw), -math.cos(yaw), 0))          # verso la camera
    destra = Vector((math.cos(yaw), math.sin(yaw), 0))
    copie = [(0.0, 0.0)] + [(math.cos(a), math.sin(a)) for a in (k * math.pi / 6 for k in range(12))]
    for k, (cx, cz) in enumerate(copie):                            # bordo scuro: la scritta ripetuta tutt'intorno, dietro
        sp = Vector(pos) - avanti * 0.05 + (destra * cx + Vector((0, 0, 1)) * cz) * misura * 0.10
        o = text_obj(coll, 'NomeBordo%d' % k, testo, misura, scuro, tuple(sp), rot=(math.pi / 2, 0, yaw))
        cu = o.data; cu.font = font; cu.extrude = 0.035; cu.space_character = 1.05; o.visible_shadow = False
    o = text_obj(coll, 'Nome', testo, misura, giallo, tuple(pos), rot=(math.pi / 2, 0, yaw))
    cu = o.data; cu.font = font; cu.extrude = 0.07; cu.bevel_depth = 0.006; cu.bevel_resolution = 2; cu.space_character = 1.05
    o.visible_shadow = False


def copertina(nome):
    col, tgt, dist, dirc, lens, (scritta, pos_scritta, misura) = PERSONAGGI[nome]
    reset_scene(); set004._c.clear(); scene = bpy.context.scene; C = collection('C')
    w = bpy.data.worlds.new('W'); scene.world = w; w.use_nodes = True
    bg = w.node_tree.nodes['Background']; bg.inputs['Color'].default_value = (*col, 1); bg.inputs['Strength'].default_value = 1.0
    if nome == 'pippo':
        P = pippo2.build_pippo(C); pippo2.express(P, 1, smile=1.0, brow_lift=0.3)
    elif nome == 'tumbo':
        T = tumbo.build_tumbo(C, scale=0.75); tumbo.tumbo_express(T, 1, tongue=0.8)
    elif nome == 'gualtiero':
        G = props009.gualtiero(C, props009.mats009()); props009.gex(G, 1, brow=0.7, mouth=0.3)
    elif nome == 'giulia':
        GM = giulia.mats_giulia(); J = giulia.giulia(C, GM); giulia.giex(J, None, brow=0.8, mouth=0.3, lid=0.35, naso=-0.4)
        giulia.mattarello(C, GM, J).rotation_euler = (0, 0, math.pi / 2); J['shoulderR'].rotation_euler = (0, -2.3, 0)
    elif nome == 'eleonora':
        Z = eleonora.zucchina(C, props012.mats012()); Z['root'].scale = (1.3,) * 3; Z['root'].location = (0, 0, 0.42)
        eleonora.velo(Z, False); eleonora.emozione(Z, None, 'felice')
    elif nome == 'prete':
        Z12 = props012.mats012(); m, face, _, _ = props012.moto(C, Z12); props012.moto_extras(C, Z12, m, face); m.rotation_euler = (0, 0, 0.0)
    setup_render(scene, 1080, 1920, samples=32, fps=24, frames=3)
    t = Vector(tgt); d = Vector(dirc).normalized()
    nome_3d(C, scritta, pos_scritta, misura, d, COLORE_NOME.get(nome, (1.0, 0.80, 0.08)))
    cam = camera('Cam', t + d * dist, t, lens=lens, coll=C); scene.camera = cam   # d = dal personaggio verso la camera (davanti = -Y)
    luci.cielo_basso(w, 0.35, vista=1.0); luci.cinema(C, tuple(t), tuple(cam.location), distanza=4.0, forza=0.7, lato=1); luci.ombre_pulite(scene, mezza_risoluzione=False)
    scene.render.filepath = os.path.join(OUT, nome + '.png'); bpy.ops.render.render(write_still=True); print('RESA', nome, flush=True)


def anteprima():
    from PIL import Image, ImageDraw, ImageFont
    F = os.path.join(QUI, '..', 'assets', 'font', 'Poppins-ExtraBold.ttf')
    nomi = list(PERSONAGGI); S = 300
    im = Image.new('RGB', (S * 3 + 80, (S + 80) * 2 + 20), (250, 250, 250)); d = ImageDraw.Draw(im)
    for i, n in enumerate(nomi):
        c = Image.open(os.path.join(OUT, n + '.png')).convert('RGB'); c = c.crop((0, (1920 - 1080) // 2, 1080, (1920 + 1080) // 2)).resize((S, S))
        m = Image.new('L', (S, S), 0); ImageDraw.Draw(m).ellipse((0, 0, S, S), fill=255)
        x, y = 20 + (i % 3) * (S + 20), 20 + (i // 3) * (S + 80)
        im.paste(c, (x, y), m); d.text((x + S // 2, y + S + 30), n.capitalize(), font=ImageFont.truetype(F, 30), fill=(30, 30, 30), anchor='mm')
    im.save(os.path.join(QUI, '..', 'schede', 'storie_personaggi.png'))


if __name__ == '__main__':
    scelti = [a for a in sys.argv[1:] if a in PERSONAGGI] or list(PERSONAGGI)
    for n in scelti:
        copertina(n)
    anteprima(); print('ANTEPRIMA FATTA')
