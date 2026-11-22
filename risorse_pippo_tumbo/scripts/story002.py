"""Sceneggiatura/traiettorie di Pippo e Tumbo (usate sia dalla simulazione della vasca sia dall'animazione)."""
import math
import numpy as np
from params002 import *

def ease(x):  # smoothstep
    x = min(1.0, max(0.0, x)); return x * x * (3 - 2 * x)

# --- basi sulla pedana --------------------------------------------------------
HOLD = np.array([HERO_HOLD[0], HERO_HOLD[1], ramp_z(HERO_HOLD[1]) + BALL_R + 0.32])
ARM_D = np.array([0.62, -0.742, 0.258]); ARM_D /= np.linalg.norm(ARM_D)
ARM_REACH = 0.78
PIP_SHOULDER_R = HOLD - ARM_REACH * ARM_D
PIP_BASE = np.array([PIP_SHOULDER_R[0] - 0.315, PIP_SHOULDER_R[1], PIP_SHOULDER_R[2] - 1.35])
TUM_SCALE = 0.75
TUM_BASE = np.array([-3.45, 3.05, PLAT_Z])
POOLC = np.array([POOL_C[0], POOL_C[1]])
PLATC = np.array(PLAT_C)
_u = (POOLC - PLATC); _u /= np.linalg.norm(_u)
_perp = np.array([-_u[1], _u[0]])
EDGE = PLATC + 0.80 * _u

# --- tempi ---------------------------------------------------------------------
TUM_RUN0, TUM_JUMP, TUM_FLIGHT = 8.00, 8.40, 0.60
PIP_RUN0, PIP_JUMP, PIP_FLIGHT = 9.70, 10.10, 0.62
TUM_FINAL = np.array([-3.18, 1.92, 0.85])
PIP_FINAL = np.array([-3.60, 1.52, -0.25])
TUM_COM_H, PIP_COM_H = 0.45 * TUM_SCALE, 1.00

def _flight(t, tj, T, take_xy, com_h, land_xyz, com_land_z, base_z):
    """posizione del baricentro durante il volo (balistica con tempo T)."""
    x0 = np.array([take_xy[0], take_xy[1], base_z + com_h])
    x1 = np.array([land_xyz[0], land_xyz[1], com_land_z])
    u = (t - tj)
    v = (x1[:2] - x0[:2]) / T
    vz = (x1[2] - x0[2] + 0.5 * G * T * T) / T
    return np.array([x0[0] + v[0] * u, x0[1] + v[1] * u, x0[2] + vz * u - 0.5 * G * u * u]), np.array([v[0], v[1], vz - G * u])

def tumbo_state(t):
    """Ritorna (root_pos, yaw, pitch, phase). phase in {'idle','run','air','sink','rise','done'}"""
    land = np.array([TUM_FINAL[0] + 0.1, TUM_FINAL[1] - 0.1, 0.0])
    take = EDGE + 0.45 * _perp
    head = land[:2] - take; head /= np.linalg.norm(head)
    yaw = math.atan2(head[0], -head[1])
    com_land_z = 1.35
    if t < TUM_RUN0:
        return TUM_BASE.copy(), None, 0.0, 'idle'
    if t < TUM_JUMP:                          # corsa verso il bordo
        a = ease((t - TUM_RUN0) / (TUM_JUMP - TUM_RUN0))
        p = TUM_BASE.copy(); p[:2] = TUM_BASE[:2] * (1 - a) + take * a
        return p, yaw, 0.0, 'run'
    t_land = TUM_JUMP + TUM_FLIGHT
    if t < t_land:
        c, v = _flight(t, TUM_JUMP, TUM_FLIGHT, take, TUM_COM_H, land, com_land_z, PLAT_Z)
        ang = math.atan2(-v[2], np.linalg.norm(v[:2]))     # nose-down angle
        pitch = max(-0.6, min(1.0, ang))
        # root = baricentro - R*(0,0,COM_H) (approx: usa solo pitch)
        root = c - np.array([head[0] * math.sin(pitch), head[1] * math.sin(pitch), 0]) * 0 - np.array([0, 0, TUM_COM_H * math.cos(pitch)])
        return root, yaw, pitch, 'air'
    # dopo l'impatto: affonda poi riemerge
    tt = t - t_land
    c_land, _ = _flight(t_land, TUM_JUMP, TUM_FLIGHT, take, TUM_COM_H, land, com_land_z, PLAT_Z)
    root_land = c_land - np.array([0, 0, TUM_COM_H])
    deep = np.array([TUM_FINAL[0] + 0.05, TUM_FINAL[1] - 0.05, 0.10])
    if tt < 0.55:
        a = ease(tt / 0.55)
        p = root_land * (1 - a) + deep * a
        return p, yaw, 1.0 * (1 - a) + 0.0 * a, 'sink'
    if tt < 1.55:
        a = ease((tt - 0.55) / 1.0)
        p = deep * (1 - a) + TUM_FINAL * a
        return p, yaw * (1 - a) + (-0.35) * a, 0.0, 'rise'
    return TUM_FINAL.copy(), -0.35, 0.0, 'done'

def pippo_state(t):
    """(root_pos, yaw, tilt_x, phase)  tilt_x: rotazione attorno a X (testa avanti/giù)."""
    land = np.array([PIP_FINAL[0] + 0.05, PIP_FINAL[1] + 0.10, 0.0])
    take = EDGE - 0.25 * _perp
    head = land[:2] - take; head /= np.linalg.norm(head)
    yaw = math.atan2(head[0], -head[1])
    if t < PIP_RUN0:
        return PIP_BASE.copy(), None, 0.0, 'idle'
    if t < PIP_JUMP:
        a = ease((t - PIP_RUN0) / (PIP_JUMP - PIP_RUN0))
        p = PIP_BASE.copy(); p[:2] = PIP_BASE[:2] * (1 - a) + take * a
        return p, yaw, 0.0, 'run'
    t_land = PIP_JUMP + PIP_FLIGHT
    if t < t_land:
        u = (t - PIP_JUMP) / PIP_FLIGHT
        tilt = math.radians(115) * ease(u * 1.15)
        c, v = _flight(t, PIP_JUMP, PIP_FLIGHT, take, PIP_COM_H, land, 1.55, PLAT_Z)
        root = c - np.array([0, 0, 0]) - np.array([0.0, 0.0, 0.0])
        # baricentro a COM_H lungo l'asse del corpo
        axis = np.array([-head[0] * math.sin(tilt), -head[1] * math.sin(tilt) * 0 + 0, math.cos(tilt)])
        axis3 = np.array([head[0] * math.sin(tilt), head[1] * math.sin(tilt), math.cos(tilt)])
        root = c - axis3 * PIP_COM_H
        return root, yaw, tilt, 'air'
    tt = t - t_land
    tilt0 = math.radians(115)
    c_land, _ = _flight(t_land, PIP_JUMP, PIP_FLIGHT, take, PIP_COM_H, land, 1.55, PLAT_Z)
    axis3 = np.array([head[0] * math.sin(tilt0), head[1] * math.sin(tilt0), math.cos(tilt0)])
    root_land = c_land - axis3 * PIP_COM_H
    deep = np.array([PIP_FINAL[0], PIP_FINAL[1], -1.15])
    if tt < 0.80:
        a = ease(tt / 0.80)
        p = root_land * (1 - a) + deep * a
        return p, yaw, tilt0 * (1 - a) + math.radians(40) * a, 'sink'
    if tt < 1.60:
        a = ease((tt - 0.80) / 0.80)
        p = deep * (1 - a) + PIP_FINAL * a
        return p, yaw * (1 - a) + 0.0 * a, math.radians(40) * (1 - a), 'rise'
    return PIP_FINAL.copy(), 0.0, 0.0, 'done'

# --- sfere di collisione (nel riferimento del personaggio) -------------------------
PIP_SPHERES = [(0, 0, 1.76, 0.40), (0, 0, 1.38, 0.27), (0, 0, 1.08, 0.30), (0, 0, 0.78, 0.27),
               (-0.115, 0, 0.55, 0.14), (0.115, 0, 0.55, 0.14), (-0.115, 0, 0.22, 0.14), (0.115, 0, 0.22, 0.14),
               (-0.315, 0, 1.1, 0.13), (0.315, 0, 1.1, 0.13), (-0.315, 0, 0.75, 0.12), (0.315, 0, 0.75, 0.12)]
TUM_SPHERES = [(0, -0.42 * 1.0, 0.73, 0.30), (0, -0.2, 0.45, 0.26), (0, 0.15, 0.45, 0.26),
               (-0.15, -0.2, 0.15, 0.1), (0.15, -0.2, 0.15, 0.1), (-0.15, 0.22, 0.15, 0.1), (0.15, 0.22, 0.15, 0.1)]

def rot_matrix(yaw, tilt):
    cy, sy, cx, sx = math.cos(yaw), math.sin(yaw), math.cos(tilt), math.sin(tilt)
    Rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    Rz = np.array([[cy, -sy, 0], [sy, cy, 0], [0, 0, 1]])
    return Rz @ Rx

def colliders(t):
    """lista (centro(3), raggio) di tutte le sfere attive a t."""
    out = []
    p, yaw, tilt, ph = pippo_state(t)
    R = rot_matrix(0.0 if yaw is None else yaw, tilt)
    for (x, y, z, r) in PIP_SPHERES:
        out.append((p + R @ np.array([x, y, z]), r))
    p, yaw, pitch, ph = tumbo_state(t)
    R = rot_matrix(0.0 if yaw is None else yaw, pitch)
    for (x, y, z, r) in TUM_SPHERES:
        out.append((p + R @ (TUM_SCALE * np.array([x, y, z])), r * TUM_SCALE))
    return out
