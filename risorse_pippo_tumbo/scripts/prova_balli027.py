"""Provino dei movimenti registrati su Pippo vestito da popstar: per ogni registrazione una striscia di fotogrammi.
Uso: python prova_balli027.py NOME:PERCORSO[:t0:t1[:busto]] ...   -> ../out/balli027/NOME.jpg
(PERCORSO = file .bvh oppure nome in assets/mocap/cmu). La camera sta davanti e segue Pippo."""
import sys, os, math
QUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, QUI)
import bpy
from mathutils import Vector
from common import *
from render_setup import *
import luci, kitlook, pippo2, props027
import mocap_pippo as mp
from PIL import Image
A = kitlook.A
OUT = os.path.join(QUI, '..', 'out', 'balli027'); os.makedirs(OUT, exist_ok=True)
N = int(os.environ.get('NFOT', '10')); W, H = 300, 533


def provino(nome, percorso, t0=None, t1=None, busto=None):
    reset_scene(); scene = bpy.context.scene; C = collection('C')
    seq = mp.sequenza([mp.pezzo(mp.clip(percorso, t0=t0, t1=t1, busto=busto), verso=0.0)])
    setup_render(scene, W, H, samples=4, fps=24, frames=len(seq))
    A.qualita_eevee(preset='veloce', riflessi=False, scena=scene, risoluzione=(W, H))
    world(scene, top=(0.20, 0.15, 0.42), bottom=(1.0, 0.45, 0.15), strength=1.0)
    M = props027.mats027()
    pav = material('M27_prova_pav', (0.55, 0.55, 0.6), rough=0.9); riga = material('M27_prova_riga', (0.12, 0.12, 0.16), rough=0.9)
    props027.scatola('Pavimento', 40, 40, 0.1, pav, C, loc=(0, 0, -0.05), r=0.01)
    for i in range(-16, 17):
        props027.scatola('RigaX', 16, 0.012, 0.004, riga, C, loc=(0, i * 0.5, 0.001), r=0.001)
        props027.scatola('RigaY', 0.012, 16, 0.004, riga, C, loc=(i * 0.5, 0, 0.001), r=0.001)
    R = pippo2.build_pippo(C); props027.look_pop(C, R, 'P3', M)
    G, d_bocca, d_pubblico = props027.microfono_in_mano(C, R, M)
    mp.applica(R, seq, f0=1, braccio_mic=lambda k: (d_bocca, 1.0))
    pippo2.express(R, 1, smile=2.0, mouth_open=0.6, brow_lift=0.9)
    cam = bpy.data.objects.new('Cam', bpy.data.cameras.new('Cam')); C.objects.link(cam); scene.camera = cam; cam.data.lens = 30
    mira = empty('Mira', loc=(0, 0, 1.15), coll=C)
    for k, s in enumerate(seq):                                             # camera e mira seguono la posizione (non la rotazione)
        cam.location = (s['mondo'].x + 1.2, s['mondo'].y - 4.6, 1.35); cam.keyframe_insert('location', frame=1 + k)
        mira.location = (s['mondo'].x, s['mondo'].y, 1.15); mira.keyframe_insert('location', frame=1 + k)
    tk = cam.constraints.new('TRACK_TO'); tk.target = mira; tk.track_axis = 'TRACK_NEGATIVE_Z'; tk.up_axis = 'UP_Y'
    luci.sole(C, (1.2, -4.6, 0), lato=-1, energia=3.2, angolo_alto=30)
    luci.ombre_pulite(scene, mezza_risoluzione=False)
    fr = [1 + int(i * (len(seq) - 1) / (N - 1)) for i in range(N)]; ims = []
    for f in fr:
        scene.frame_set(f); scene.render.filepath = os.path.join(OUT, '_tmp_%s.png' % nome); bpy.ops.render.render(write_still=True)
        ims.append(Image.open(scene.render.filepath).convert('RGB'))
    im = Image.new('RGB', (W * N, H))
    for i, x in enumerate(ims): im.paste(x, (i * W, 0))
    im.save(os.path.join(OUT, nome + '.jpg'), quality=85); os.remove(os.path.join(OUT, '_tmp_%s.png' % nome))
    print('PROVINO', nome, len(seq), mp.controllo(seq), flush=True)


if __name__ == '__main__':
    for a in sys.argv[1:]:
        p = a.split(':'); nome, perc = p[0], p[1]
        t0 = float(p[2]) if len(p) > 2 and p[2] else None; t1 = float(p[3]) if len(p) > 3 and p[3] else None
        bu = float(p[4]) if len(p) > 4 and p[4] else None
        try: provino(nome, perc, t0, t1, bu)
        except Exception as e:
            import traceback; traceback.print_exc()
