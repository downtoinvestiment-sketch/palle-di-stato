"""Parametri Test 003 - Pippo & Tumbo costruiscono un campo da calcio."""
import math, numpy as np
FPS = 24
# Blocchi (secondi, provvisori; vengono riscalati sulle durate degli audio)
BLOCKS = {1: (0.0, 11.7), 2: (11.7, 22.2), 3: (22.2, 31.2), 4: (31.2, 46.5)}
def tm(b, u):
    a, c = BLOCKS[b]; return a + (c - a) * u
def fr(t): return 1 + int(round(t * FPS))
TOTAL = BLOCKS[4][1]
FRAMES = int(round(TOTAL * FPS))

# Geometria (m). Campo 12 x 7.5, letto (bed) 14 x 8.7
PX, PY = 10.0, 6.25
BX, BY = 11.0, 7.1
CURB_H = 0.32
WATER_H = 0.24
GOAL_W, GOAL_H, GOAL_D = 3.4, 2.2, 1.1
BALL_R = 0.24
# livelli della pila
Z_GRAVEL, Z_SAND, Z_SYN, Z_GRASS = 0.14, 0.20, 0.23, 0.27
NSTRIP = 8

def H(x, y, A=1.5):
    """altezza del terreno sconnesso (analitica, usata da mesh e fisica)."""
    h = (0.10 * np.sin(0.9 * x + 1.3) * np.cos(0.7 * y) + 0.08 * np.sin(1.7 * y + 0.4 * x)
         + 0.07 * np.exp(-((x - 1.5) ** 2 + (y + 0.8) ** 2) / 0.5) - 0.09 * np.exp(-((x + 2.2) ** 2 + (y - 1.1) ** 2) / 0.35)
         + 0.05 * np.sin(2.3 * x) * np.sin(2.1 * y) + 0.07 * np.exp(-((x + 4.2) ** 2 + (y + 1.8) ** 2) / 0.6)
         - 0.08 * np.exp(-((x - 3.6) ** 2 + (y - 2.0) ** 2) / 0.5))
    edge = np.clip((np.minimum(BX - abs(x), BY - abs(y))) / 0.4, 0, 1)
    return A * h * edge
