"""Moto delle palline: pista procedurale (file sincronizzate) + vasca con piccola fisica numpy.
Output: cache/balls.npz con pos (N,F,3), color (N,), exit_frame, ecc."""
import story002 as ST
import sys, os, math
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from params002 import *

OUT = os.path.join(os.path.dirname(__file__), '..', 'cache')

def disp(x, a, V):
    """spostamento dopo x secondi dal rilascio (da fermo, accel a, tetto V)"""
    x = np.maximum(x, 0.0); xa = V / a
    return np.where(x < xa, 0.5 * a * x * x, 0.5 * a * xa * xa + V * (x - xa))

def vel(x, a, V):
    x = np.maximum(x, 0.0); return np.minimum(a * x, V)

def build():
    F = FRAMES
    balls = []   # dict: lane, row, color, kind
    paths = {}
    for l, rho in enumerate(RHO):
        paths[l] = lane_path(rho)
    paths['h'] = lane_path(RHO_HERO, with_ramp=True)
    # --- file a riposo
    rest = []   # (lane, row, s_rest, tau)
    for l in range(3):
        pts, s = paths[l]
        send = s[-1]
        for i in range(ROWS):
            srest = send - GATE_BACK - 0.16 - i * REST_SPACING
            tau = T_GATE + i * REST_SPACING / SWEEP_W
            rest.append((l, i, srest, tau))
    N = len(rest) + 1
    P = np.zeros((N, F, 3)); color = np.zeros(N, int); exit_f = np.full(N, -1)
    vel_exit = np.zeros((N, 3)); exit_t = np.full(N, np.nan)
    tl = np.arange(F) / FPS
    # tangente della lip
    tdir = np.array([-1.0, 0.0, -LIP_SLOPE]); tdir /= np.linalg.norm(tdir)
    track_active = np.zeros((N, F), bool)
    for n, (l, i, srest, tau) in enumerate(rest):
        pts, s = paths[l]
        q = srest + disp(tl - tau, ACC, VMAX)
        track_active[n] = q < s[-1]
        P[n] = pos_at(pts, s, q)
        color[n] = (i + l) % 7
        # istante e velocità di uscita
        # risolvi disp(x) = s_end - srest
        need = s[-1] - srest
        xs = np.linspace(0, 12, 24001); d = disp(xs, ACC, VMAX)
        x_ex = np.interp(need, d, xs)
        exit_t[n] = tau + x_ex
        vel_exit[n] = tdir * min(ACC * x_ex, VMAX)
    # --- eroe
    hp, hs = paths['h']
    hid = N - 1
    color[hid] = 4  # azzurro/ciano -> lo coloriamo bianco-perla nel materiale (palla speciale), vedi anim
    # caduta libera dalla mano alla rampa
    x0, y0 = HERO_HOLD; zr = ramp_z(y0) + BALL_R
    z_hold = zr + 0.32
    t_fall = math.sqrt(2 * (z_hold - zr) / G)
    v0 = 0.7                                  # velocità iniziale lungo -Y
    s_land = (RAMP_Y0 - y0) + v0 * t_fall
    hero_s = np.zeros(F); hero_pos = np.zeros((F, 3))
    for f in range(F):
        t = tl[f]
        if t < HERO_REL:
            hero_pos[f] = (x0, y0, z_hold); hero_s[f] = -1
        elif t < HERO_REL + t_fall:
            u = t - HERO_REL
            hero_pos[f] = (x0, y0 - v0 * u, z_hold - 0.5 * G * u * u); hero_s[f] = -1
        else:
            u = t - HERO_REL - t_fall
            q = s_land + v0 * u + (disp(u + v0 / HERO_ACC, HERO_ACC, HERO_VMAX) - disp(v0 / HERO_ACC, HERO_ACC, HERO_VMAX))
            hero_s[f] = q; hero_pos[f] = pos_at(hp, hs, q)
    P[hid] = hero_pos
    # tempo di uscita eroe
    u_ex = np.interp(hs[-1], np.where(hero_s >= 0, hero_s, 0), tl) if False else None
    ex = np.where(hero_s >= hs[-1])[0]
    if len(ex): exit_t[hid] = (ex[0]) / FPS
    else:
        # estrapola
        uu = np.linspace(0, 20, 20001)
        qq = s_land + v0 * uu + (disp(uu + v0 / HERO_ACC, HERO_ACC, HERO_VMAX) - disp(v0 / HERO_ACC, HERO_ACC, HERO_VMAX))
        exit_t[hid] = HERO_REL + t_fall + np.interp(hs[-1], qq, uu)
    vel_exit[hid] = tdir * HERO_VMAX
    return dict(P=P, color=color, exit_t=exit_t, vel_exit=vel_exit, N=N, paths=paths, hero_s=hero_s, rest=rest)

def pool_sim(D_):
    P, exit_t, vexit, N = D_['P'], D_['exit_t'], D_['vel_exit'], D_['N']
    F = FRAMES
    SUB = 20; dt = 1.0 / (FPS * SUB)
    cx, cy = POOL_C
    Rin = POOL_R; zf = POOL_FLOOR + BALL_R; rim = POOL_FLOOR + POOL_H
    X = np.zeros((N, 3)); V = np.zeros((N, 3)); dyn = np.zeros(N, bool); sleep = np.zeros(N, bool)
    # posizione di uscita (fine lip)
    exit_pos = {}
    for n in range(N):
        pass
    order = np.argsort(exit_t)
    iu = np.triu_indices(N, 1)
    e_ball, e_floor, e_wall = 0.45, 0.32, 0.25
    out = P.copy()
    inside = np.zeros(N, bool)
    hits = []   # (t, speed) per audio: urti con pavimento/palline
    min_gap = 1e9
    paths = D_['paths']
    lane_of = {}
    for n in range(N - 1):
        lane_of[n] = D_['rest'][n][0]
    lane_of[N - 1] = 'h'
    for f in range(F):
        for sub in range(SUB):
            t = f / FPS + sub * dt
            # attiva palle che escono
            for n in range(N):
                if not dyn[n] and t >= exit_t[n]:
                    pts, s = paths[lane_of[n]]
                    X[n] = pts[-1] + vexit[n] * 0.0
                    # il corpo ha già percorso un po' oltre: posizione = fine lip + v * (t-exit_t)
                    X[n] = pts[-1] + vexit[n] * (t - exit_t[n])
                    V[n] = vexit[n]; dyn[n] = True
            idx = np.where(dyn)[0]
            if len(idx) == 0: continue
            col_now = ST.colliders(t) if t >= 8.0 else []
            col_nxt = ST.colliders(t + dt) if t >= 8.0 else []
            V[idx, 2] -= G * dt
            X[idx] += V[idx] * dt
            contact = np.zeros(N, bool)
            for it in range(8 if col_now else 4):
                Xi = X[idx]
                # sfere
                d = Xi[:, None, :] - Xi[None, :, :]
                dist = np.linalg.norm(d, axis=2) + np.eye(len(idx)) * 1e9
                ov = np.where(dist < D)
                for a, b in zip(*ov):
                    if a >= b: continue
                    ia, ib = idx[a], idx[b]
                    nrm = d[a, b] / max(dist[a, b], 1e-9)
                    pen = D - dist[a, b]
                    X[ia] += nrm * pen * 0.5; X[ib] -= nrm * pen * 0.5
                    vn = np.dot(V[ia] - V[ib], nrm)
                    if vn < 0:
                        j = -(1 + e_ball) * vn * 0.5
                        V[ia] += nrm * j; V[ib] -= nrm * j
                        if it == 0 and -vn > 0.6: hits.append((t, -vn, X[ia].copy()))
                    contact[ia] = contact[ib] = True
                # personaggi (sfere cinematiche)
                for (c0, r0), (c1, _) in zip(col_now, col_nxt):
                    cv = (c1 - c0) / dt
                    cn = np.linalg.norm(cv)
                    if cn > 2.5: cv = cv * 2.5 / cn
                    dd = X[idx] - c0
                    ds = np.linalg.norm(dd, axis=1)
                    near = np.where(ds < r0 + BALL_R)[0]
                    for k in near:
                        n = idx[k]; nrm = dd[k] / max(ds[k], 1e-9)
                        X[n] = c0 + nrm * (r0 + BALL_R)
                        vn = np.dot(V[n] - cv, nrm)
                        if vn < 0:
                            V[n] -= (1 + 0.2) * vn * nrm
                            if it == 0 and -vn > 0.8: hits.append((t, -vn, X[n].copy()))
                        contact[n] = True
                # pavimento
                fl = idx[X[idx, 2] < zf]
                for n in fl:
                    # solo se dentro il raggio della vasca
                    if math.hypot(X[n, 0] - cx, X[n, 1] - cy) < Rin + 0.05:
                        X[n, 2] = zf
                        if V[n, 2] < 0:
                            if -V[n, 2] > 0.8 and it == 0: hits.append((t, -V[n, 2], X[n].copy()))
                            V[n, 2] = -V[n, 2] * e_floor if -V[n, 2] > 0.9 else 0.0
                            V[n, 0] *= 0.68; V[n, 1] *= 0.68      # attrito di impatto
                        contact[n] = True
                # parete (solo sotto il bordo)
                for n in idx:
                    dx, dy = X[n, 0] - cx, X[n, 1] - cy
                    r_ = math.hypot(dx, dy)
                    if r_ < Rin - 0.12 and X[n, 2] < rim + 0.5: inside[n] = True
                    top = rim + (1.3 if inside[n] else 0.0)
                    if r_ > Rin - BALL_R and r_ < Rin + (1.5 if inside[n] else 0.3) and X[n, 2] < top:
                        # dentro la vasca? (se la palla è dentro il raggio+margine) -> spingi dentro
                        nx, ny = dx / r_, dy / r_
                        X[n, 0] = cx + nx * (Rin - BALL_R); X[n, 1] = cy + ny * (Rin - BALL_R)
                        vr = V[n, 0] * nx + V[n, 1] * ny
                        if vr > 0:
                            V[n, 0] -= (1 + e_wall) * vr * nx; V[n, 1] -= (1 + e_wall) * vr * ny
                            if vr > 1.0 and it == 0: hits.append((t, vr, X[n].copy()))
                        contact[n] = True
            if col_now:
                for _ in range(6):
                    Xi = X[idx]; dd = Xi[:, None, :] - Xi[None, :, :]
                    ds = np.linalg.norm(dd, axis=2) + np.eye(len(idx)) * 1e9
                    for a, b in zip(*np.where(np.triu(ds < D, 1))):
                        nrm = dd[a, b] / max(ds[a, b], 1e-9); pen = D - ds[a, b]
                        X[idx[a]] += nrm * pen * 0.5; X[idx[b]] -= nrm * pen * 0.5
            if col_now:
                sp = np.linalg.norm(V[idx], axis=1); big = idx[sp > 4.0]
                V[big] *= (4.0 / sp[sp > 4.0])[:, None]
            # attrito di rotolamento/dissipazione quando si è a contatto
            c = idx[contact[idx]]
            V[c] *= math.exp(-3.0 * dt)
            slow = c[np.linalg.norm(V[c], axis=1) < 0.05]
            V[slow] = 0
        out[dyn, f] = X[dyn]
        # per le palle non ancora dinamiche P[n,f] resta il percorso procedurale
        # distanza minima (diagnostica)
    return out, hits

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    D_ = build()
    print('N palline:', D_['N'])
    et = D_['exit_t']; print('uscita palline: prima %.2fs ultima %.2fs  eroe %.2fs' % (np.nanmin(et[:-1]), np.nanmax(et[:-1]), et[-1]))
    pos, hits = pool_sim(D_)
    # diagnostica: distanze minime
    N = D_['N']; mg = 1e9; worst = None; viol = 0
    for f in range(FRAMES):
        Xf = pos[:, f]; d = np.linalg.norm(Xf[:, None] - Xf[None], axis=2) + np.eye(N) * 1e9
        m = d.min()
        if m < D * 0.97: viol += 1
        if m < mg: mg = m; worst = f
    print('distanza minima centri %.3f (diametro %.3f) al frame %d; frame con compenetrazione >3%%: %d' % (mg, D, worst, viol))
    fin = pos[:, -1]; inpool = np.hypot(fin[:, 0] - POOL_C[0], fin[:, 1] - POOL_C[1]) < POOL_R
    print('palline in vasca a fine video: %d/%d  quota max centro %.2f  rim %.2f' % (inpool.sum(), N, fin[:, 2].max(), POOL_FLOOR + POOL_H))
    ang = np.arctan2(fin[:, 1] - POOL_C[1], fin[:, 0] - POOL_C[0])
    rank = np.argsort(np.argsort(ang)); newcol = (rank * 7 // N).astype(int)
    D_['color'] = newcol
    np.savez(os.path.join(OUT, 'balls.npz'), pos=pos, color=D_['color'], exit_t=et, hits_t=np.array([h[0] for h in hits]),
             hits_v=np.array([h[1] for h in hits]), hits_p=np.array([h[2] for h in hits]) if hits else np.zeros((0, 3)))
    print('urti registrati:', len(hits))
