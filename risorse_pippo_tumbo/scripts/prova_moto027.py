"""Prova del SOLO movimento del video 027: Pippo cammina in avanti, balla e salta con i movimenti registrati (mocap CMU).
Uso: python prova_moto027.py fogli   (12 fotogrammi sparsi -> ../out/moto027/foglio.jpg)
     python prova_moto027.py video [da a]   (fotogrammi PNG in ../out/moto027/f_####.png; poi ffmpeg)"""
import sys, os, math
QUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, QUI)
import bpy
from mathutils import Vector
from common import *
from render_setup import *
import luci, kitlook, pippo2, props027, props024
import mocap_pippo as mp
A = kitlook.A
OUT = os.path.join(QUI, '..', 'out', 'moto027'); os.makedirs(OUT, exist_ok=True)
BPM = 124.0; BATT = 60.0 / BPM; LOOK = os.environ.get('LOOK027', 'P2')


def costruisci(w=360, h=640):
    reset_scene(); scene = bpy.context.scene; C = collection('C')
    seq = mp.sequenza([mp.cammino(8, BATT), mp.clip('05_02', durata=16 * BATT), mp.clip('16_01')], alza=1.6)
    setup_render(scene, w, h, samples=4, fps=24, frames=len(seq))
    A.qualita_eevee(preset='veloce', riflessi=False, scena=scene, risoluzione=(w, h))
    world(scene, top=(0.20, 0.15, 0.42), bottom=(1.0, 0.45, 0.15), strength=1.0)
    M = props027.mats027()
    pav = material('M27_prova_pav', (0.55, 0.55, 0.6), rough=0.9); riga = material('M27_prova_riga', (0.12, 0.12, 0.16), rough=0.9)
    props027.scatola('Pavimento', 30, 30, 0.1, pav, C, loc=(0, 0, -0.05), r=0.01)
    for i in range(-12, 13):                                                 # griglia: se un piede scivola si vede subito
        props027.scatola('RigaX', 12, 0.012, 0.004, riga, C, loc=(0, i * 0.5, 0.001), r=0.001)
        props027.scatola('RigaY', 0.012, 12, 0.004, riga, C, loc=(i * 0.5, 0, 0.001), r=0.001)
    R = pippo2.build_pippo(C)
    props027.look_pop(C, R, LOOK, M)
    G, d_bocca, d_pubblico = props027.microfono_in_mano(C, R, M)
    def braccio_mic(k):                                                      # canta al microfono; ogni 4 battute lo tende al pubblico per 2
        b = (k / 24.0) / BATT; fase = b % 8
        w_ = 0.0
        if 6.0 <= fase < 8.0:
            w_ = min(1.0, (fase - 6.0) / 0.4, (8.0 - fase) / 0.4)
        return Vector(d_bocca).lerp(d_pubblico, w_).normalized(), 1.0
    mp.applica(R, seq, f0=1, posto=(0, 4.3, 0), braccio_mic=braccio_mic)
    for k in range(0, len(seq), 3):                                          # bocca che canta (finta, finche' non c'e' la canzone)
        b = (k / 24.0) / BATT
        pippo2.express(R, 1 + k, smile=1.0, mouth_open=0.25 + 1.1 * abs(math.sin(b * math.pi)), brow_lift=0.6)
    cam = bpy.data.objects.new('Cam', bpy.data.cameras.new('Cam')); C.objects.link(cam); scene.camera = cam
    pc = (2.4, -4.6, 1.5); cam.location = pc; cam.data.lens = 34
    mira = empty('Mira', loc=(0, 0, 1.15), parent=R['root'], coll=C)          # la camera segue Pippo
    tk = cam.constraints.new('TRACK_TO'); tk.target = mira; tk.track_axis = 'TRACK_NEGATIVE_Z'; tk.up_axis = 'UP_Y'
    luci.cinema(C, (0.0, 1.5, 1.3), pc, distanza=5.0, lato=1, forza=1.3)
    luci.sole(C, (pc[0], pc[1], 0), lato=-1, energia=2.5, angolo_alto=25)
    luci.ombre_pulite(scene, mezza_risoluzione=False)
    print('CONTROLLO', mp.controllo(seq), flush=True)
    return scene, len(seq)


if __name__ == '__main__':
    modo = sys.argv[1] if len(sys.argv) > 1 else 'fogli'
    scene, n = costruisci()
    if modo == 'fogli':
        from PIL import Image
        fr = [1 + int(i * (n - 1) / 11) for i in range(12)]; ims = []
        for f in fr:
            scene.frame_set(f); scene.render.filepath = os.path.join(OUT, 'foglio_%04d.png' % f); bpy.ops.render.render(write_still=True)
            ims.append(Image.open(scene.render.filepath).convert('RGB'))
        W, H = ims[0].size; im = Image.new('RGB', (W * 6, H * 2))
        for i, x in enumerate(ims): im.paste(x, ((i % 6) * W, (i // 6) * H))
        im.save(os.path.join(OUT, 'foglio.jpg'), quality=85); print('FOGLIO', fr, flush=True)
    else:
        a = int(sys.argv[2]) if len(sys.argv) > 2 else 1; b = int(sys.argv[3]) if len(sys.argv) > 3 else n
        for f in range(a, b + 1):
            p = os.path.join(OUT, 'f_%04d.png' % f)
            if os.path.exists(p): continue
            scene.frame_set(f); scene.render.filepath = p; bpy.ops.render.render(write_still=True)
        print('VIDEO', a, b, flush=True)
