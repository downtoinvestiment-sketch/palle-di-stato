"""Pippo v2 - stile 3D cartoon pulito (capsule, materiali opachi, occhi grandi con riflesso).
Solo primitive: capsule, ellissoidi, ciocche a goccia. Rig a empty gerarchici.
Pippo guarda verso -Y con rot_z = 0. Altezza ~1.95 m con i capelli."""
import bpy, bmesh, math, random
from mathutils import Vector
from common import *

HIP_Z = 0.70
NECK_Z = 1.50
HEAD_C = 0.27                      # centro testa sopra il collo
HR = (0.36, 0.32, 0.33)            # raggi testa
TORSO_R, TORSO_L, TORSO_C = 0.24, 0.38, 0.36   # raggio, tratto cilindrico, centro (locale al body)


def build_materials():
    M = {}
    M['skin']    = material('P_Skin',   (0.95, 0.60, 0.43), rough=0.75, spec=0.25)
    M['skin_d']  = material('P_SkinD',  (0.88, 0.46, 0.34), rough=0.75, spec=0.2)
    M['hair1']   = material('P_Hair1',  (0.26, 0.12, 0.05), rough=0.6, spec=0.35)
    M['hair2']   = material('P_Hair2',  (0.36, 0.18, 0.07), rough=0.6, spec=0.35)
    M['brow']    = material('P_Brow',   (0.15, 0.07, 0.03), rough=0.6)
    M['white']   = material('P_EyeW',   (1.0, 1.0, 1.0), rough=0.3, spec=0.5)
    M['pupil']   = material('P_Pupil',  (0.02, 0.015, 0.02), rough=0.15, spec=1.0)
    M['shine']   = material('P_Shine',  (1, 1, 1), rough=0.2, emit=(1, 1, 1), emit_strength=1.5)
    M['mouth']   = material('P_Mouth',  (0.38, 0.06, 0.07), rough=0.6)
    M['inside']  = material('P_Inside', (0.30, 0.03, 0.06), rough=0.7)
    M['tongue']  = material('P_Tongue', (0.95, 0.35, 0.42), rough=0.6)
    M['hoodie']  = material('P_Hoodie', (1.00, 0.30, 0.01), rough=0.8, spec=0.2)
    M['hoodie_d']= material('P_HoodieD',(0.82, 0.20, 0.01), rough=0.85, spec=0.15)
    M['cord']    = material('P_Cord',   (0.97, 0.93, 0.85), rough=0.7)
    M['bolt']    = material('P_Bolt',   (1.0, 0.82, 0.0), rough=0.5, spec=0.3,
                            emit=(1.0, 0.7, 0.0), emit_strength=0.15)
    M['pants']   = material('P_Pants',  (0.06, 0.20, 0.80), rough=0.8, spec=0.2)
    M['shoes']   = material('P_Shoes',  (0.30, 0.75, 1.00), rough=0.55, spec=0.35)
    return M


def _bolt(M, parent):
    """Fulmine estruso, proiettato sulla capsula del busto."""
    r, half = TORSO_R, TORSO_L / 2
    raw = [(-.01, .17), (.09, .17), (.035, .06), (.10, .06), (-.06, -.15), (-.02, .0), (-.09, .0)]
    pts = [(x * 0.95, z * 0.95 + 0.115) for x, z in raw]
    bm = bmesh.new()
    vs = [bm.verts.new((x, 0, z)) for x, z in pts]
    f = bm.faces.new(vs)
    bmesh.ops.triangulate(bm, faces=[f], quad_method='BEAUTY', ngon_method='EAR_CLIP')
    for _ in range(3):
        bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=1, use_grid_fill=False)
        bmesh.ops.triangulate(bm, faces=bm.faces[:])
    for v in bm.verts:
        x, z = v.co.x, v.co.z
        dz = max(0.0, abs(z) - half)
        t = max(0.0, r * r - x * x - dz * dz)
        v.co.y = -math.sqrt(t) - 0.010
    for fc in bm.faces: fc.smooth = True
    me = bpy.data.meshes.new('P_BoltMesh'); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new('P_Bolt', me)
    o.parent = parent; o.location = (0, 0, TORSO_C)
    me.materials.append(M['bolt'])
    bpy.context.scene.collection.objects.link(o)
    md = o.modifiers.new('solid', 'SOLIDIFY'); md.thickness = 0.028; md.offset = 0.0
    return o


def build_pippo(coll=None):
    M = build_materials()
    R = {'mats': M}
    coll = coll or collection('Pippo')
    S = lambda name, kind, loc, sc, parent, mat, rot=(0, 0, 0): shape(
        name, kind, loc, sc, rot, parent, mat, coll)
    E = lambda name, loc, parent: empty(name, loc, parent, coll)
    cap = lambda r, L: f'cap:{r}:{L}'

    root = E('Pippo_Root', (0, 0, 0), None)
    body = E('Pippo_Body', (0, 0, HIP_Z), root)
    R.update(root=root, body=body)

    # --- busto: felpa arancione --------------------------------------
    S('P_Torso', cap(TORSO_R, TORSO_L), (0, 0, TORSO_C), (1, 1, 1), body, M['hoodie'])
    S('P_HoodBack', 'sphere', (0, 0.12, 0.78), (0.20, 0.12, 0.10), body, M['hoodie_d'])
    S('P_Collar', 'sphere', (0, 0.0, 0.755), (0.165, 0.15, 0.07), body, M['hoodie_d'])
    S('P_Neck', 'sphere', (0, 0, 0.80), (0.085, 0.085, 0.08), body, M['skin'])
    for s in (-1, 1):                      # lacci del cappuccio
        S(f'P_Cord{s}', cap(0.014, 0.12), (s * 0.06, -0.185, 0.66), (1, 1, 1), body, M['cord'])
        S(f'P_CordEnd{s}', 'sphere', (s * 0.06, -0.19, 0.585), (0.02, 0.02, 0.025), body, M['cord'])

    # --- testa ---------------------------------------------------------
    head = E('Pippo_Head', (0, 0, NECK_Z - HIP_Z), body)
    R['head'] = head
    S('P_Head', 'sphere', (0, 0, HEAD_C), HR, head, M['skin'])
    for s in (-1, 1):
        S(f'P_Ear{s}', 'sphere', (s * 0.35, 0.0, HEAD_C - 0.02), (0.04, 0.06, 0.07), head, M['skin'])
    S('P_Nose', 'sphere', (0, -0.322, HEAD_C - 0.065), (0.072, 0.07, 0.066), head, M['skin_d'])

    for s_, nm in ((-1, 'L'), (1, 'R')):
        eye = E(f'Eye{nm}', (s_ * 0.127, -0.272, HEAD_C + 0.045), head)
        S(f'P_EyeW{nm}', 'sphere', (0, 0, 0), (0.118, 0.066, 0.13), eye, M['white'])
        pup = E(f'Pupil{nm}', (0, -0.058, 0), eye)
        S(f'P_Pup{nm}', 'sphere', (0, 0, 0), (0.066, 0.028, 0.078), pup, M['pupil'])
        S(f'P_Shine{nm}', 'sphere_lo', (-0.02, -0.024, 0.03), (0.02, 0.011, 0.022), pup, M['shine'])
        brow = E(f'Brow{nm}', (s_ * 0.13, -0.238, HEAD_C + 0.215), head)
        S(f'P_Brow{nm}', 'sphere', (0, 0, 0), (0.128, 0.04, 0.046), brow, M['brow'])
        R[f'eye{nm}'] = eye; R[f'pupil{nm}'] = pup; R[f'brow{nm}'] = brow

    cu = bpy.data.curves.new('P_MouthCurve', 'CURVE')
    cu.dimensions = '3D'; cu.bevel_depth = 0.014; cu.bevel_resolution = 4; cu.use_fill_caps = True
    sp = cu.splines.new('BEZIER'); sp.bezier_points.add(2)
    base = [(-0.075, -0.266, HEAD_C - 0.135), (0, -0.289, HEAD_C - 0.148), (0.075, -0.266, HEAD_C - 0.135)]
    for bp, co in zip(sp.bezier_points, base):
        bp.co = co; bp.handle_left_type = 'AUTO'; bp.handle_right_type = 'AUTO'
    mo = bpy.data.objects.new('P_Mouth', cu); mo.parent = head; coll.objects.link(mo)
    mo.data.materials.append(M['mouth'])
    R['mouth_curve'] = cu; R['mouth_base'] = base
    mopen = E('MouthOpen', (0, -0.279, HEAD_C - 0.15), head)
    S('P_MouthIn', 'sphere', (0, 0, 0), (0.075, 0.026, 0.055), mopen, M['inside'])
    S('P_Tongue', 'sphere', (0, -0.008, -0.026), (0.045, 0.018, 0.022), mopen, M['tongue'])
    mopen.scale = (0.001, 0.001, 0.001)
    R['mouth_open'] = mopen

    # --- capelli: calotta scura + ciocche separate arrotondate ----------
    rnd = random.Random(11)
    R['hair'] = []
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=72, v_segments=44, radius=1.0)
    dele = []
    for f in bm.faces:
        c = f.calc_center_median()
        hl = max(-0.25, min(0.74, 0.22 - 0.6 * c.y))
        if c.z < hl: dele.append(f)
    bmesh.ops.delete(bm, geom=dele, context='FACES')
    for f in bm.faces: f.smooth = True
    me = bpy.data.meshes.new('P_HairCapMesh'); bm.to_mesh(me); bm.free()
    cap_o = bpy.data.objects.new('P_HairCap', me); cap_o.parent = head
    cap_o.location = (0, 0.01, HEAD_C + 0.01)
    cap_o.scale = (HR[0] * 1.06, HR[1] * 1.06, HR[2] * 1.06)
    me.materials.append(M['hair1']); coll.objects.link(cap_o)
    md = cap_o.modifiers.new('solid', 'SOLIDIFY'); md.thickness = -0.02; md.offset = 1

    H = Vector(HR)
    n = 0
    while n < 34:
        d = Vector((rnd.uniform(-1, 1), rnd.uniform(-0.6, 1), rnd.uniform(0.15, 1))).normalized()
        hl = max(-0.25, min(0.74, 0.22 - 0.6 * d.y))
        if d.z < hl + 0.05: continue
        pos = Vector((d.x * H.x, d.y * H.y, d.z * H.z)) * 0.97
        tilt = Vector((rnd.uniform(-.7, .7), rnd.uniform(-.7, .7), rnd.uniform(-0.1, .3)))
        dirv = (d + tilt).normalized()
        if rnd.random() < 0.25:
            dirv = (dirv + Vector((rnd.choice([-1, 1]) * 1.0, rnd.uniform(-.6, .6), 0.15))).normalized()
        length = rnd.uniform(0.11, 0.19); rad = rnd.uniform(0.075, 0.115)
        pv = E(f'HairPivot{n}', (pos.x, pos.y, HEAD_C + pos.z), head)
        q = Vector((0, 0, 1)).rotation_difference(dirv)
        eu = q.to_euler(); eu.rotate_axis('Z', rnd.uniform(0, math.tau))
        pv.rotation_euler = eu
        S(f'P_Hair{n}', 'lock', (0, 0, -0.02), (rad, rad, length), pv, M['hair1'] if n % 2 else M['hair2'])
        R['hair'].append(pv); n += 1
    for i, (x, rx, rz) in enumerate(((-0.17, -1.05, 0.5), (-0.04, -1.15, 0.1), (0.09, -1.1, -0.2), (0.2, -0.95, -0.55))):
        pv = E(f'HairBang{i}', (x, -0.17, HEAD_C + 0.285), head)
        pv.rotation_euler = (rx, 0.0, rz)
        S(f'P_Bang{i}', 'lock', (0, 0, 0), (0.085, 0.085, 0.19), pv, M['hair2'] if i % 2 else M['hair1'])
        R['hair'].append(pv)

    # --- braccia: un solo cilindro lungo con estremità tonde, lungo i fianchi ---------
    for s_, nm in ((-1, 'L'), (1, 'R')):
        sh = E(f'Shoulder{nm}', (s_ * 0.315, 0, 0.65), body)
        S(f'P_Arm{nm}', cap(0.075, 0.46), (0, 0, -0.29), (1, 1, 1), sh, M['hoodie'])
        S(f'P_Cuff{nm}', 'sphere', (0, 0, -0.51), (0.082, 0.082, 0.04), sh, M['hoodie_d'])
        el = E(f'Elbow{nm}', (0, 0, -0.51), sh)          # solo come perno della mano
        S(f'P_Hand{nm}', 'sphere', (0, 0, -0.07), (0.088, 0.088, 0.092), el, M['skin'])
        R[f'shoulder{nm}'] = sh; R[f'elbow{nm}'] = el

    # --- gambe e scarpe ---------------------------------------------------
    for s, nm in ((-1, 'L'), (1, 'R')):
        hp = E(f'Hip{nm}', (s * 0.115, 0, HIP_Z), root)
        S(f'P_Leg{nm}', cap(0.108, 0.42), (0, 0, -0.30), (1, 1, 1), hp, M['pants'])
        ft = E(f'Foot{nm}', (0, 0, -0.62), hp)
        S(f'P_Shoe{nm}', 'sphere', (0, -0.055, 0.0), (0.125, 0.19, 0.085), ft, M['shoes'])
        R[f'hip{nm}'] = hp; R[f'foot{nm}'] = ft
    return R


def express(R, f, brow=0.0, brow_lift=0.0, eye_open=1.0, smile=0.0, mouth_open=0.0,
            look=(0.0, 0.0), eye_scale=1.0):
    """brow>0 = determinate, <0 = sorpresa/triste; brow_lift alza le sopracciglia;
    smile>0 sorriso; mouth_open 0..1; look=(x,z) sposta le pupille; eye_scale ingrandisce gli occhi."""
    for s, nm in ((-1, 'L'), (1, 'R')):
        br = R[f'brow{nm}']
        br.rotation_euler = (0, s * brow * 0.45, 0)
        br.location.z = HEAD_C + 0.215 + brow_lift * 0.07
        br.keyframe_insert('rotation_euler', frame=f); br.keyframe_insert('location', index=2, frame=f)
        eye = R[f'eye{nm}']
        eye.scale = (eye_scale, 1.0, max(0.05, eye_open) * eye_scale)
        eye.keyframe_insert('scale', frame=f)
        pu = R[f'pupil{nm}']
        pu.location = (look[0] * 0.035, -0.058, look[1] * 0.04)
        pu.keyframe_insert('location', frame=f)
    cu = R['mouth_curve']; base = R['mouth_base']
    for i, bp in enumerate(cu.splines[0].bezier_points):
        x, y, z = base[i]
        if i == 1: z = z - 0.035 * smile if smile > 0 else z - 0.03 * smile
        else:      z = z + 0.04 * smile
        bp.co = (x * (1 + 0.3 * smile), y, z)
        bp.handle_left_type = 'AUTO'; bp.handle_right_type = 'AUTO'
        bp.keyframe_insert('co', frame=f)
    mo = R['mouth_open']
    mo.scale = (0.001,) * 3 if mouth_open <= 0.01 else (0.5 + 0.5 * mouth_open, 1.0, 0.3 + 1.1 * mouth_open)
    mo.keyframe_insert('scale', frame=f)
