"""Test 008 - due montaggi dagli stessi fotogrammi: 'full' (76.5 s) e 'cut' (~45 s: gancio, ali di cartone, lancio dal tetto, finale)."""
FPS = 24
SEG_FR = {'full': [(1, 1836)], 'cut': [(1, 238), (739, 996), (1242, 1836)]}
def segs(ver): return [((a - 1) / FPS, b / FPS) for a, b in SEG_FR[ver]]
def total(ver): return sum(b - a for a, b in segs(ver))
def tmap(ver, t):
    """tempo sorgente -> tempo nel montaggio (None se tagliato)."""
    off = 0.0
    for a, b in segs(ver):
        if a <= t < b: return off + t - a
        off += b - a
    return None
def tclip(ver, t0, t1):
    """intervallo sorgente -> intervallo nel montaggio, tagliato al segmento che contiene t0 (None se fuori)."""
    off = 0.0
    for a, b in segs(ver):
        if a <= t0 < b: return off + t0 - a, off + min(t1, b) - a
        off += b - a
    return None
def frames(ver): return [f for a, b in SEG_FR[ver] for f in range(a, b + 1)]
