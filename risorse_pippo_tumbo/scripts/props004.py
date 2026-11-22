"""Attrezzi, giocatori, nuvole e pioggia per Test 003."""
import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
import bpy, bmesh, numpy as np
from mathutils import Vector
from common import *
from params003 import *
from set003 import obj, bx, cyl, ball_, box_c, box0, prism

def cart(coll, M):
    """segnalinee: origine al suolo sotto il corpo, fronte -Y. Maniglia verso +Y (verso chi spinge)."""
    r = empty('Cart', (0, 0, 0), None, coll)
    obj('CartBody', box_c(), (0, 0, 0.28), (0.5, 0.42, 0.26), M['white'], coll, parent=r)
    obj('Tank', shared_mesh('cyl:0.16:0.34'), (0, -0.02, 0.5), (1, 1, 1), M['red'], coll, parent=r)
    wheels = []
    for sx in (-0.30, 0.30):
        w = cyl('Wheel', 0.14, 0.08, (sx, 0, 0.14), M['dark'], coll, rot=(0, math.pi / 2, 0), parent=r); wheels.append(w)
    obj('Handle', shared_mesh('cyl:0.025:0.72'), (0, 0.40, 0.69), (1, 1, 1), M['steel'], coll, rot=(math.atan2(0.24, 0.67) * -1 + 0.0, 0, 0), parent=r)
    obj('HandleBar', shared_mesh('cyl:0.03:0.62'), (0, 0.52, 1.02), (1, 1, 1), M['steel'], coll, rot=(0, math.pi / 2, 0), parent=r)
    return r, wheels

def bulldozer(coll, M):
    """fronte +X; origine al suolo."""
    r = empty('Bulldozer', (0, 0, 0), None, coll)
    obj('Body', box_c(), (0, 0, 0.75), (1.9, 1.15, 0.7), M['yellow'], coll, parent=r)
    obj('Hood', box_c(), (0.55, 0, 1.25), (0.8, 0.9, 0.35), M['yellow'], coll, parent=r)
    obj('Cab', box_c(), (-0.35, 0, 1.45), (0.85, 0.95, 0.85), M['yellow'], coll, parent=r)
    obj('CabGlass', box_c(), (-0.35, 0, 1.5), (0.9, 0.9, 0.55), M['window'], coll, parent=r)
    obj('Roof', box_c(), (-0.35, 0, 1.92), (1.0, 1.1, 0.08), M['dark'], coll, parent=r)
    for sy in (-0.72, 0.72):
        obj('Track', box_c(), (0, sy, 0.3), (2.3, 0.36, 0.6), M['dark'], coll, parent=r)
        ball_('TrackF', 0.3, (1.15, sy, 0.3), M['dark'], coll, parent=r, sc=(1, 0.6, 1))
        ball_('TrackB', 0.3, (-1.15, sy, 0.3), M['dark'], coll, parent=r, sc=(1, 0.6, 1))
    obj('Blade', box_c(), (1.5, 0, 0.45), (0.22, 2.0, 0.85), M['steel'], coll, rot=(0, -0.12, 0), parent=r)
    for sy in (-0.85, 0.85):
        obj('Arm', box_c(), (1.2, sy, 0.5), (0.7, 0.1, 0.12), M['steel'], coll, parent=r)
    obj('Exhaust', shared_mesh('cyl:0.06:0.5'), (0.75, 0.3, 1.6), (1, 1, 1), M['dark'], coll, parent=r)
    return r

def roller(coll, M):
    """rullo compressore, fronte +X."""
    r = empty('Roller', (0, 0, 0), None, coll)
    drum = cyl('Drum', 0.55, 1.5, (0.75, 0, 0.55), M['yellow'], coll, rot=(math.pi / 2, 0, 0), parent=r)
    obj('Frame', box_c(), (-0.1, 0, 0.9), (1.3, 0.8, 0.5), M['yellow'], coll, parent=r)
    obj('Seat', box_c(), (-0.5, 0, 1.3), (0.4, 0.45, 0.3), M['dark'], coll, parent=r)
    obj('Roof', box_c(), (-0.5, 0, 2.0), (0.9, 0.9, 0.07), M['dark'], coll, parent=r)
    for sy in (-0.4, 0.4): obj('Pole', shared_mesh('cyl:0.04:0.7'), (-0.85, sy, 1.65), (1, 1, 1), M['dark'], coll, parent=r)
    rear = []
    for sy in (-0.65, 0.65):
        rear.append(cyl('RearWheel', 0.45, 0.35, (-0.75, sy, 0.45), M['dark'], coll, rot=(math.pi / 2, 0, 0), parent=r))
    return r, drum, rear

def brush_machine(coll, M):
    """spazzola/distributore: avanza lungo +X, larga lungo Y."""
    r = empty('Brush', (0, 0, 0), None, coll)
    obj('Frame', box_c(), (0, 0, 0.55), (0.7, 3.4, 0.35), M['steel'], coll, parent=r)
    obj('Hopper', box_c(), (-0.1, 0, 0.9), (0.55, 3.0, 0.35), M['dark'], coll, parent=r)
    obj('Bristles', box_c(), (0.4, 0, 0.14), (0.28, 3.3, 0.14), M['yellow'], coll, parent=r)
    for sy in (-1.5, 1.5): cyl('Wheel', 0.2, 0.1, (-0.2, sy, 0.2), M['dark'], coll, rot=(math.pi / 2, 0, 0), parent=r)
    obj('Bar', shared_mesh('cyl:0.03:0.9'), (-0.6, 0, 1.0), (1, 1, 1), M['steel'], coll, rot=(0, math.pi / 2 - 0.5, 0), parent=r)
    return r

def sprinkler(coll, M):
    r = empty('Sprinkler', (0, 0, 0), None, coll)
    obj('Pipe', shared_mesh('cyl:0.06:0.30'), (0, 0, 0.15), (1, 1, 1), M['dark'], coll, parent=r)
    head = empty('SprHead', (0, 0, 0.32), r, coll)
    obj('Nozzle', shared_mesh('cyl:0.09:0.05'), (0, 0, 0), (1, 1, 1), M['steel'], coll, parent=head)
    sp = []
    for k in range(3):
        a = k * 2.1
        o = obj('Spray', shared_mesh('cone'), (0.12 * math.cos(a), 0.12 * math.sin(a), 0.0), (0.06, 0.06, 1.3), M['rain'], coll,
                rot=(0, 1.1, a), parent=head)
        sp.append(o)
    return r, head, sp

def flag(coll, M):
    r = empty('Flag', (0, 0, 0), None, coll)
    obj('Pole', shared_mesh('cyl:0.025:1.2'), (0, 0, 0.6), (1, 1, 1), M['white'], coll, parent=r)
    f = obj('Cloth', shared_mesh('cone'), (0.0, 0, 1.12), (0.18, 0.02, 0.5), M['red'], coll, rot=(0, math.pi / 2, 0), parent=r)
    return r

def floodlight(coll, M):
    r = empty('Floodlight', (0, 0, 0), None, coll)
    obj('Pole', shared_mesh('cyl:0.12:8.0'), (0, 0, 4.0), (1, 1, 1), M['steel'], coll, parent=r)
    head = empty('LampHead', (0, 0, 8.1), r, coll)
    obj('Panel', box_c(), (0, 0, 0), (1.6, 0.18, 0.9), M['dark'], coll, parent=head)
    lamp = obj('Bulbs', box_c(), (0, -0.1, 0), (1.45, 0.05, 0.75), M['lampfx'], coll, parent=head)
    return r, head, lamp

def player(coll, name, shirt, shorts, skin, hair, scale=1.0):
    """giocatore semplice (non e' Pippo): fronte -Y, piedi a z=0."""
    cm = lambda n, c, ro=0.6: material(n + name, c, rough=ro)
    ms, mh, mk, mhr = cm('Shirt', shirt), cm('Shorts', shorts), cm('Skin', skin, 0.7), cm('Hair', hair, 0.9)
    msock = cm('Sock', (0.95, 0.95, 0.95))
    R = {}
    R['root'] = empty(name, (0, 0, 0), None, coll); R['root'].scale = (scale, scale, scale)
    r = R['root']
    shape('Torso', 'cap:0.24:0.3', (0, 0, 1.12), parent=r, mat=ms, coll=coll)
    shape('Hips', 'cap:0.22:0.05', (0, 0, 0.82), parent=r, mat=mh, coll=coll)
    shape('Neck', 'cyl:0.08:0.1', (0, 0, 1.55), parent=r, mat=mk, coll=coll)
    head = empty('Head', (0, 0, 1.82), r, coll)
    shape('Skull', 'sphere', (0, 0, 0), scale=(0.28, 0.26, 0.30), parent=head, mat=mk, coll=coll)
    shape('Hair', 'sphere', (0, 0.05, 0.1), scale=(0.29, 0.26, 0.24), parent=head, mat=mhr, coll=coll)
    for sx in (-0.10, 0.10):
        shape('Eye', 'sphere', (sx, -0.23, 0.04), scale=(0.055, 0.03, 0.07), parent=head, mat=material('Eye' + name, (0.05, 0.05, 0.06), rough=0.3), coll=coll)
    shape('Smile', 'sphere', (0, -0.25, -0.1), scale=(0.07, 0.025, 0.025), parent=head, mat=material('Mouth' + name, (0.5, 0.15, 0.15), rough=0.5), coll=coll)
    for nm, sx in (('L', -0.34), ('R', 0.34)):
        sh = empty('shoulder' + nm, (sx, 0, 1.42), r, coll); R['shoulder' + nm] = sh
        shape('Arm', 'cap:0.085:0.42', (0, 0, -0.30), parent=sh, mat=ms, coll=coll)
        shape('Hand', 'sphere', (0, 0, -0.66), scale=(0.09, 0.09, 0.09), parent=sh, mat=mk, coll=coll)
        hp = empty('hip' + nm, (sx * 0.38, 0, 0.82), r, coll); R['hip' + nm] = hp
        shape('Leg', 'cap:0.105:0.40', (0, 0, -0.34), parent=hp, mat=msock, coll=coll)
        shape('Short', 'cap:0.12:0.1', (0, 0, -0.1), parent=hp, mat=mh, coll=coll)
        shape('Shoe', 'sphere', (0, -0.08, -0.78), scale=(0.11, 0.18, 0.08), parent=hp, mat=material('Shoe' + name, (0.1, 0.1, 0.12), rough=0.5), coll=coll)
    return R

def cloud(coll, M, loc, s=1.0):
    r = empty('Cloud', loc, None, coll)
    for (dx, dy, dz, rr) in [(0, 0, 0, 1.5), (1.4, 0.3, -0.1, 1.2), (-1.4, -0.2, -0.15, 1.2), (0.6, -0.5, 0.5, 1.1), (-0.5, 0.5, 0.45, 1.0), (2.3, 0, -0.3, 0.8), (-2.3, 0, -0.35, 0.8)]:
        ball_('Puff', rr * s, (dx * s, dy * s, dz * s), M['cloud'], coll, parent=r, sc=(1, 1, 0.65))
    return r

def rain_layer(coll, M, seed, n=700, area=(10.0, 7.0), zmax=11.0):
    rng = np.random.default_rng(seed)
    bm = bmesh.new()
    for _ in range(n):
        x = rng.uniform(-area[0], area[0]); y = rng.uniform(-area[1], area[1]); z = rng.uniform(0, zmax)
        v = [bm.verts.new((x + dx, y + dy, z + dz)) for dx, dy, dz in [(-.012, 0, 0), (.012, 0, 0), (.012, 0, .55), (-.012, 0, .55)]]
        bm.faces.new(v)
    me = bpy.data.meshes.new('rain%d' % seed); bm.to_mesh(me); bm.free(); me.materials.append(None)
    o = bpy.data.objects.new('Rain%d' % seed, me); o.material_slots[0].link = 'OBJECT'; o.material_slots[0].material = M['rain']
    coll.objects.link(o)
    return o
