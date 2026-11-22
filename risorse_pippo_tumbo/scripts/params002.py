"""Parametri condivisi - Test 002 (The Perfect Rainbow Cascade). Unità: metri. Gravità cartoon g=15."""
import math
import numpy as np

FPS, FRAMES = 24, 288
G = 15.0
BALL_R = 0.14
D = 2 * BALL_R
REST_SPACING = 0.30                 # distanza fra centri a riposo (gap 2 cm)

# --- elica della pista (antioraria vista dall'alto) -----------------------
R_MEAN = 1.50
LANE_OFF = [-0.31, 0.0, 0.31]       # corsie delle palline (3)
HERO_OFF = 0.62                     # corsia separata dell'eroe (esterna)
RHO = [R_MEAN + o for o in LANE_OFF]
RHO_HERO = R_MEAN + HERO_OFF
RHO_IN, RHO_OUT = 0.98, 2.30        # bordi pista
RHO_SEP = R_MEAN + 0.465            # parete fra corsie e corsia eroe
PHI0 = math.pi
TURNS = 1.75
PHI_END = PHI0 + 2 * math.pi * TURNS     # = 4.5*pi  -> (0,+rho) tangente -X
Z_TOP = 5.30                        # quota inizio elica
DROP = 2.60
K = DROP / (PHI_END - PHI0)         # m per radiante
LIP_LEN = 0.9                       # tratto rettilineo finale (verso -X)
LIP_SLOPE = 0.12

# --- rampa di lancio (eroe) ------------------------------------------------
RAMP_Y0 = 3.30                      # y dove Pippo lascia la pallina
RAMP_DZ = 0.40

# --- vasca -------------------------------------------------------------------
POOL_C = (-3.45, 1.65)
POOL_R = 0.85
POOL_FLOOR = 0.25
POOL_H = 1.05                       # altezza pareti sopra il pavimento vasca

# --- pedana -------------------------------------------------------------------
PLAT_C = (-3.05, 3.70)
PLAT_R = 0.95
PLAT_Z = 4.60                       # quota piano pedana (spalla di Pippo all'altezza della pallina)

def lane_path(rho, with_ramp=False):
    """Polilinea (N,3) del centro-pallina di una corsia: [rampa] + elica + lip. Ritorna (pts, s)."""
    pts = []
    if with_ramp:
        x = -rho
        for y in np.linspace(RAMP_Y0, 0.0, 40, endpoint=False):
            z = Z_TOP + RAMP_DZ * (y / RAMP_Y0)
            pts.append((x, y, z))
    n = int(abs(PHI_END - PHI0) / math.radians(1.5))
    for phi in np.linspace(PHI0, PHI_END, n):
        pts.append((rho * math.cos(phi), rho * math.sin(phi), Z_TOP - K * (phi - PHI0)))
    p = np.array(pts[-1]); t = np.array([-1.0, 0.0, 0.0])
    zl = p[2]
    for u in np.linspace(0, LIP_LEN, 20)[1:]:
        pts.append((p[0] + t[0] * u, p[1], zl - LIP_SLOPE * u))
    pts = np.array(pts)
    pts[:, 2] += BALL_R
    seg = np.linalg.norm(np.diff(pts, axis=0), axis=1)
    s = np.concatenate([[0], np.cumsum(seg)])
    return pts, s

def pos_at(pts, s, q):
    q = np.clip(q, 0, s[-1])
    return np.stack([np.interp(q, s, pts[:, i]) for i in range(3)], axis=-1)

def helix_z(phi):
    return Z_TOP - K * (phi - PHI0)

RAINBOW = [(1.0, 0.04, 0.06), (1.0, 0.38, 0.0), (1.0, 0.85, 0.0), (0.12, 0.85, 0.15),
           (0.0, 0.75, 1.0), (0.10, 0.25, 1.0), (0.62, 0.15, 0.95)]

# --- moto delle palline -------------------------------------------------------
ROWS = 32
GATE_BACK = 4.5                      # distanza (lungo la corsia) fra fermo e fine pista
T_GATE = 3.0                         # apertura dei fermi (s)
SWEEP_W = 14.0                       # velocità dell'onda di rilascio (m/s) dal fronte verso il fondo
ACC, VMAX = 3.5, 5.5                 # accelerazione e velocità massima delle file
HERO_ACC, HERO_VMAX = 2.4, 6.0
HERO_REL = 0.90                      # istante in cui Pippo lascia la pallina (s)
HERO_HOLD = (-RHO_HERO, RAMP_Y0 - 0.05)
def ramp_z(y): return Z_TOP + RAMP_DZ * (y / RAMP_Y0)
