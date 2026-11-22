"""Tumbo, il cane di Pippo - stesso stile (capsule, ellissoidi, materiali opachi).
Guarda verso -Y con rot_z = 0."""
import bpy, math
from mathutils import Vector
from common import *

def build_tumbo(coll=None, scale=0.75):
    coll = coll or collection('Tumbo')
    M = {
        'fur':   material('T_Fur',   (0.88, 0.52, 0.20), rough=0.85, spec=0.15),
        'fur_d': material('T_FurD',  (0.55, 0.28, 0.10), rough=0.85, spec=0.15),
        'cream': material('T_Cream', (1.0, 0.90, 0.72), rough=0.85, spec=0.15),
        'nose':  material('T_Nose',  (0.03, 0.02, 0.03), rough=0.25, spec=0.8),
        'white': material('T_EyeW',  (1, 1, 1), rough=0.3, spec=0.5),
        'pupil': material('T_Pupil', (0.02, 0.015, 0.02), rough=0.15, spec=1.0),
        'shine': material('T_Shine', (1, 1, 1), rough=0.2, emit=(1, 1, 1), emit_strength=1.5),
        'tongue':material('T_Tongue',(1.0, 0.38, 0.45), rough=0.6),
        'collar':material('T_Collar',(0.92, 0.08, 0.14), rough=0.7),
        'tag':   material('T_Tag',   (1.0, 0.80, 0.1), rough=0.35, spec=0.6),
    }
    R = {'mats': M}
    S = lambda n, k, loc, sc, par, mat, rot=(0, 0, 0): shape(n, k, loc, sc, rot, par, mat, coll)
    E = lambda n, loc, par: empty(n, loc, par, coll)
    cap = lambda r, L: f'cap:{r}:{L}'
    root = E('Tumbo_Root', (0, 0, 0), None); root.scale = (scale,) * 3
    body = E('Tumbo_Body', (0, 0, 0.45), root)
    R.update(root=root, body=body)
    # corpo: capsula orizzontale
    S('T_Body', cap(0.25, 0.34), (0, 0, 0), (1, 1, 1), body, M['fur'], rot=(math.pi / 2, 0, 0))
    S('T_Belly', 'sphere', (0, -0.02, -0.12), (0.2, 0.34, 0.15), body, M['cream'])
    S('T_Chest', 'sphere', (0, -0.34, 0.0), (0.19, 0.12, 0.2), body, M['cream'])
    # testa
    head = E('Tumbo_Head', (0, -0.42, 0.28), body); R['head'] = head
    S('T_Head', 'sphere', (0, 0, 0.0), (0.29, 0.27, 0.27), head, M['fur'])
    S('T_Snout', 'sphere', (0, -0.22, -0.07), (0.15, 0.16, 0.11), head, M['cream'])
    S('T_Nose', 'sphere', (0, -0.355, -0.015), (0.062, 0.05, 0.048), head, M['nose'])
    S('T_Chin', 'sphere', (0, -0.2, -0.15), (0.09, 0.1, 0.05), head, M['cream'])
    tongue = E('Tongue', (0, -0.30, -0.15), head)
    S('T_Tongue', 'sphere', (0, 0, -0.03), (0.045, 0.06, 0.06), tongue, M['tongue'], rot=(0.3, 0, 0))
    tongue.scale = (0.001,) * 3; R['tongue'] = tongue
    for s, nm in ((-1, 'L'), (1, 'R')):
        eye = E(f'Eye{nm}', (s * 0.105, -0.225, 0.075), head)
        S(f'T_EyeW{nm}', 'sphere', (0, 0, 0), (0.088, 0.052, 0.098), eye, M['white'])
        pup = E(f'Pupil{nm}', (0, -0.045, 0), eye)
        S(f'T_Pup{nm}', 'sphere', (0, 0, 0), (0.052, 0.022, 0.062), pup, M['pupil'])
        S(f'T_Shine{nm}', 'sphere_lo', (-0.016, -0.019, 0.024), (0.016, 0.009, 0.018), pup, M['shine'])
        brow = E(f'Brow{nm}', (s * 0.105, -0.2, 0.185), head)
        S(f'T_Brow{nm}', 'sphere', (0, 0, 0), (0.07, 0.03, 0.03), brow, M['fur_d'])
        ear = E(f'Ear{nm}', (s * 0.245, 0.03, 0.16), head)
        ear.rotation_euler = (0, -s * 0.35, 0)
        S(f'T_Ear{nm}', cap(0.085, 0.14), (0, 0, -0.14), (1, 1, 1), ear, M['fur_d'])
        R[f'eye{nm}'] = eye; R[f'pupil{nm}'] = pup; R[f'brow{nm}'] = brow; R[f'ear{nm}'] = ear
    # collare
    col = E('Collar', (0, -0.33, 0.10), body); col.rotation_euler = (-0.85, 0, 0)
    S('T_Collar', 'sphere', (0, 0, 0), (0.265, 0.265, 0.055), col, M['collar'])
    S('T_Tag', 'sphere', (0, -0.265, -0.04), (0.05, 0.015, 0.05), col, M['tag'])
    # zampe
    for fy, tag in ((-0.2, 'F'), (0.22, 'B')):
        for s, nm in ((-1, 'L'), (1, 'R')):
            lg = E(f'Leg{tag}{nm}', (s * 0.15, fy, -0.05), body)
            S(f'T_Leg{tag}{nm}', cap(0.078, 0.14), (0, 0, -0.14), (1, 1, 1), lg, M['fur'])
            S(f'T_Paw{tag}{nm}', 'sphere', (0, -0.015, -0.33), (0.095, 0.12, 0.075), lg, M['cream'])
            R[f'leg{tag}{nm}'] = lg
    # coda
    tail = E('Tail', (0, 0.36, 0.1), body); tail.rotation_euler = (-1.0, 0, 0); R['tail'] = tail
    S('T_Tail', cap(0.05, 0.2), (0, 0, 0.16), (1, 1, 1), tail, M['fur'])
    S('T_TailTip', 'sphere', (0, 0, 0.34), (0.06, 0.06, 0.07), tail, M['cream'])
    return R

def tumbo_express(R, f, tongue=0.0, brow=0.0, eye_scale=1.0, eye_open=1.0, look=(0, 0)):
    for s, nm in ((-1, 'L'), (1, 'R')):
        b = R[f'brow{nm}']; b.rotation_euler = (0, s * brow * 0.4, 0); b.keyframe_insert('rotation_euler', frame=f)
        e = R[f'eye{nm}']; e.scale = (eye_scale, 1, max(0.05, eye_open) * eye_scale); e.keyframe_insert('scale', frame=f)
        p = R[f'pupil{nm}']; p.location = (look[0] * 0.03, -0.045, look[1] * 0.035); p.keyframe_insert('location', frame=f)
    t = R['tongue']; t.scale = (0.001,) * 3 if tongue <= 0.01 else (1, 1, 0.5 + tongue); t.keyframe_insert('scale', frame=f)
