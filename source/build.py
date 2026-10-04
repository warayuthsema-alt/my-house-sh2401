"""Build 3D model of SC Asset PAVE-RV SH2401-A-P(RV)-L from plan/elevation dims.
Axes (metres): X along grid 5->1 (x=0 at grid 5, 11.35 at grid 1)
               Y from grid C (front, y=0) to grid A (back, y=6.20)
               Z up, z=0 = finished ground.
Outputs: COLLADA (.dae, coloured, grouped), STL, OBJ+MTL, preview PNG.
"""
import numpy as np, math, os

HOUSE_DIR = os.environ.get("HOUSE_DIR") or os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get("OUT_DIR", "/mnt/user-data/outputs")
try:
    os.makedirs(OUT, exist_ok=True)
except OSError:
    pass

MATS = {
    "Wall_White":   (0.902, 0.882, 0.847, 1.0),   # main wall – light warm grey
    "Wall_Grey":    (0.839, 0.820, 0.780, 1.0),
    "Slab_Concrete":(0.70, 0.70, 0.68, 1.0),
    "Roof_Tile":    (0.369, 0.290, 0.271, 1.0),   # chocolate-brown concrete tile
    "Glass":        (0.243, 0.333, 0.322, 0.55),  # dark green-tint glass
    "Accent_Taupe": (0.506, 0.478, 0.447, 1.0),   # taupe accent panels
    "Trim_White":   (0.957, 0.953, 0.941, 1.0),   # window surrounds / pilaster
    "Fascia_Brown": (0.275, 0.251, 0.239, 1.0),
    "Soffit_Dark":  (0.227, 0.220, 0.212, 1.0),
    "Roof_Membrane":(0.835, 0.855, 0.855, 1.0),   # flat roofs (waterproof coat)
    "Tile_Dark":    (0.310, 0.329, 0.325, 1.0),   # terrace floor tile
    "Fence_Grey":   (0.478, 0.494, 0.494, 1.0),
    "Door_Wood":    (0.55, 0.38, 0.22, 1.0),
    "Rail_Black":   (0.118, 0.122, 0.125, 1.0),
    "Ground_Grass": (0.45, 0.62, 0.35, 1.0),
    "Paving":       (0.82, 0.80, 0.76, 1.0),
}

groups = {}  # name -> list of (material, [poly verts])

def add(group, mat, poly):
    groups.setdefault(group, []).append((mat, [tuple(map(float, p)) for p in poly]))

def box(group, mat, x0, y0, z0, x1, y1, z1):
    x0, x1 = sorted((x0, x1)); y0, y1 = sorted((y0, y1)); z0, z1 = sorted((z0, z1))
    if x1 - x0 < 1e-4 or y1 - y0 < 1e-4 or z1 - z0 < 1e-4:
        return
    v = [(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),
         (x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)]
    faces = [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    for f in faces:
        add(group, mat, [v[i] for i in f])

def prism(group, mat, profile_xz, y0, y1):
    """Extrude polygon in XZ plane (CCW seen from -Y) along Y."""
    a = [(x, y0, z) for x, z in profile_xz]
    b = [(x, y1, z) for x, z in profile_xz]
    add(group, mat, a)                 # front face (normal -Y)
    add(group, mat, b[::-1])           # back face
    n = len(a)
    for i in range(n):
        j = (i + 1) % n
        add(group, mat, [a[j], a[i], b[i], b[j]])

def wall(group, axis, c, s0, s1, z0, z1, t, openings=(), mat="Wall_White"):
    """Wall along `axis` ('x' or 'y') whose centre line is at other coord c,
    running s0..s1, height z0..z1, thickness t.
    openings: list of (a0, a1, zb, zt, fill) with fill in {None,'glass','wood'}."""
    ops = sorted(openings)
    def put(a0, a1, b0, b1, m=mat, th=t):
        if axis == "x":
            box(group, m, a0, c - th/2, b0, a1, c + th/2, b1)
        else:
            box(group, m, c - th/2, a0, b0, c + th/2, a1, b1)
    cur = s0
    for a0, a1, zb, zt, fill in ops:
        put(cur, a0, z0, z1)          # solid strip before opening
        put(a0, a1, z0, zb)           # below opening
        put(a0, a1, zt, z1)           # above opening
        if fill == "glass":
            fr = 0.05
            # frame
            put(a0, a1, zb, zb+fr, "Rail_Black", 0.06)
            put(a0, a1, zt-fr, zt, "Rail_Black", 0.06)
            put(a0, a0+fr, zb, zt, "Rail_Black", 0.06)
            put(a1-fr, a1, zb, zt, "Rail_Black", 0.06)
            if a1 - a0 > 1.0:  # mullion for sliding / double panels
                m = (a0 + a1) / 2
                put(m-0.025, m+0.025, zb, zt, "Rail_Black", 0.06)
            put(a0+fr, a1-fr, zb+fr, zt-fr, "Glass", 0.02)
        elif fill == "wood":
            put(a0, a1, zb, zt, "Door_Wood", 0.05)
        cur = a1
    put(cur, s1, z0, z1)

def trim(group, axis, c, side, a0, a1, zb, zt, w=0.10, d=0.04, mat="Trim_White"):
    """White surround on the outside face of a wall opening. side = +1/-1 (outward)."""
    f0 = c + side * 0.0
    f1 = c + side * d
    def b(p0, p1, q0, q1):
        if axis == "x": box(group, mat, p0, min(f0, f1), q0, p1, max(f0, f1), q1)
        else:           box(group, mat, min(f0, f1), p0, q0, max(f0, f1), p1, q1)
    b(a0 - w, a1 + w, zt, zt + w); b(a0 - w, a1 + w, zb - w, zb)
    b(a0 - w, a0, zb, zt);         b(a1, a1 + w, zb, zt)

# ---------------------------------------------------------------- levels
GF_FFL, CAR_FFL, TER_FFL = 0.60, 0.30, 0.50
SLAB_B, SLAB_T = 3.40, 3.70      # 2nd-floor slab (FFL +3.70)
EAVE = 6.40                      # wall top / eave
TG, TU = 0.20, 0.15              # wall thickness ground / upper
G = "Ground floor walls"; U = "Upper floor walls"

# ---------------------------------------------------------------- site & slabs
box("Site", "Ground_Grass", -4, -7, -0.05, 15.5, 11, 0.0)
box("Site", "Paving", -0.95, -4.25, 0.0, 6.2, 0.0, 0.03)            # concrete driveway (photo)
box("Slabs", "Paving", 0, 0.0, 0, 5.9, 6.8, CAR_FFL)              # carport (front edge on grid C per A1-01)
box("Slabs", "Paving", -0.6, 6.8, 0, 2.9, 8.25, CAR_FFL)          # laundry yard
box("Slabs", "Tile_Dark", 5.9, -1.15, 0, 11.35, 0, TER_FFL)   # front terrace
box("Slabs", "Slab_Concrete", 5.9, 0, 0, 11.35, 6.2, GF_FFL)      # living/dining
box("Slabs", "Slab_Concrete", 2.9, 3.0, 0, 6.75, 6.75, GF_FFL)    # kitchen / bath-3
US = "Upper slab"
for (ax0, ay0, ax1, ay1) in ((-0.15, -1.25, 5.91, 6.9), (8.03, -1.25, 11.5, 6.9),
                             (5.91, -1.25, 8.03, 0.0), (5.91, 3.0, 8.03, 6.9), (5.91, 1.5, 6.97, 3.0)):
    box(US, "Wall_White", ax0, ay0, SLAB_B, ax1, ay1, SLAB_T)      # 2F slab with stair voids
box(US, "Roof_Membrane", -0.15, -1.25, SLAB_T, 2.9, 6.9, SLAB_T + 0.02)   # canopy roof coat
box(US, "Tile_Dark", 5.95, -1.2, SLAB_T, 11.3, -0.08, SLAB_T + 0.02)       # balcony tile

# ---------------------------------------------------------------- ground floor walls
H1 = SLAB_B
wall(G, "x", 0.0, 5.9, 11.35, 0, H1, TG, [(8.6, 10.6, GF_FFL, 2.6, "glass")])          # front (terrace)
trim("Trim", "x", -TG/2, -1, 8.6, 10.6, GF_FFL + 0.1, 2.6, w=0.12)
wall(G, "y", 11.35, 0.0, 6.2, 0, H1, TG, [(0.70, 2.26, GF_FFL, 2.55, "glass"),
                                           (3.68, 5.20, GF_FFL, 2.55, "glass")])      # right side
wall(G, "x", 6.2, 6.75, 11.35, 0, H1, TG, [(6.99, 8.54, GF_FFL, 2.55, "glass"),
                                           (8.98, 10.63, GF_FFL, 2.55, "glass")])     # rear
wall(G, "y", 6.75, 6.2, 6.75, 0, H1, TG)                                               # rear step
wall(G, "x", 6.75, 2.9, 6.75, 0, H1, TG, [(3.66, 5.09, 1.45, 2.15, "glass")])          # kitchen rear
wall(G, "y", 2.9, 3.0, 6.75, 0, H1, TG, [(5.0, 5.9, GF_FFL, 2.6, "wood")])             # kitchen side (to carport)
wall(G, "x", 3.0, 2.9, 5.9, 0, H1, TG)                                                 # bath-3 front
wall(G, "y", 5.9, 0.0, 3.0, 0, H1, TG)                                                 # stair/living side
# carport side wall on grid 5 (light wall with openings per elevation 2)
# (removed: carport side is open with piers per A1-01 + photos)
# deep edge beam along the front & carport side (photo shows thick band)
box("Slabs", "Wall_White", -0.15, -1.25, 2.95, 11.5, -1.05, SLAB_B)
box("Slabs", "Wall_White", -0.15, -1.25, 2.95, 0.05, 6.85, SLAB_B)
# wall lamp beside balcony door (photo)
box("Trim", "Rail_Black", 7.85, -0.16, 5.05, 7.95, -0.09, 5.35)
# front columns
# piers / columns read from A1-01 (hatched)
for (cx0, cy0, cx1, cy1) in ((-0.10, -0.14, 0.12, 0.46),      # carport front-left
                             (-0.10, 2.55, 0.12, 3.82),       # carport side pier
                             (-0.10, 6.55, 0.12, 6.85),       # carport back-left
                             (5.85, -1.22, 6.15, 0.0),        # pier between carport & terrace
                             (11.05, -1.22, 11.37, 0.0)):     # terrace right pier
    box("Columns", "Wall_White", cx0, cy0, 0, cx1, cy1, 2.95)

# ---------------------------------------------------------------- upper floor walls
z0, z1 = SLAB_T, EAVE
wall(U, "y", 2.9, -0.75, 6.75, z0, z1, TU, [(-0.42, -0.02, 4.4, 5.55, "glass"),
                                             (1.87, 2.34, 4.4, 5.55, "glass"),
                                             (4.15, 5.67, 4.4, 5.55, "glass")])       # left (bed 2,3)
wall(U, "x", -0.75, 2.9, 5.9, z0, z1, TU, [(3.2, 5.2, SLAB_T + 0.05, 5.5, "glass")], mat="Accent_Taupe")  # bed-2 front
box(U, "Rail_Black", 3.2, -0.78, 4.58, 5.2, -0.72, 4.64)                        # transom -> 2x2 panes
trim("Trim", "x", -0.75 - TU/2, -1, 3.2, 5.2, SLAB_T + 0.05, 5.5, w=0.14)
wall(U, "x", 6.75, 2.9, 5.9, z0, z1, TU, [(3.61, 5.18, 4.4, 5.6, "glass")])            # bed-3 rear
wall(U, "y", 5.9, -0.75, 6.75, z0, z1, TU, [(2.05, 2.85, SLAB_T, SLAB_T + 2.1, "wood"), (3.25, 3.95, SLAB_T, SLAB_T + 2.1, "wood")])  # bed2/bed3 doors
wall(U, "x", 0.0, 5.9, 11.35, z0, z1, TU, [(6.4, 7.35, SLAB_T, 5.5, "glass"),
                                            (8.5, 10.55, SLAB_T, 5.5, "glass")])       # front to balcony
trim("Trim", "x", -TU/2 - 0.03, -1, 8.5, 10.55, SLAB_T + 0.1, 5.5, w=0.12, mat="Accent_Taupe")
trim("Trim", "x", -TU/2 - 0.03, -1, 6.4, 7.35, SLAB_T + 0.1, 5.5, w=0.10)
wall(U, "y", 11.35, 0.0, 6.2, z0, z1, TU, [(0.42, 0.93, 4.4, 5.55, "glass"),
                                            (2.73, 3.20, 4.4, 5.55, "glass")])         # right
wall(U, "x", 6.2, 5.9, 11.35, z0, z1, TU, [(6.32, 6.89, 4.4, 5.6, "glass"),
                                            (8.98, 9.49, 4.4, 5.6, "glass"),
                                            (9.83, 10.44, 4.4, 5.6, "glass")])         # rear

# balcony railing (y = -1.15)
R = "Balcony railing"
box(R, "Rail_Black", 5.9, -1.20, SLAB_T + 0.95, 11.35, -1.10, SLAB_T + 1.0)
box(R, "Rail_Black", 5.9, -1.18, SLAB_T + 0.05, 11.35, -1.12, SLAB_T + 0.10)
x = 5.95
while x < 11.33:
    box(R, "Rail_Black", x, -1.17, SLAB_T + 0.10, x + 0.03, -1.13, SLAB_T + 0.95)
    x += 0.12

# ---------------------------------------------------------------- roofs
RF = "Roof"
# main hip roof (closed solid: eave plane + 4 slopes)
ex0, ex1, ey0, ey1 = 1.80, 12.40, -1.05, 7.30
run = (ey1 - ey0) / 2
ym = (ey0 + ey1) / 2
pitch = math.radians(36)
zr = EAVE + run * math.tan(pitch)
rx0, rx1 = ex0 + run, ex1 - run
A = (ex0, ey0, EAVE); B = (ex1, ey0, EAVE); C = (ex1, ey1, EAVE); D = (ex0, ey1, EAVE)
P = (rx0, ym, zr); Q = (rx1, ym, zr)
add(RF, "Roof_Tile", [C, D, P, Q])
add(RF, "Roof_Tile", [D, A, P])
add(RF, "Roof_Tile", [B, C, Q])
# fascia band
for (a, b) in ((A, B), (B, C), (C, D), (D, A)):
    pass
box(RF, "Fascia_Brown", ex0, ey1, EAVE - 0.18, ex1, ey1 + 0.03, EAVE)
box(RF, "Fascia_Brown", ex0 - 0.03, ey0, EAVE - 0.18, ex0, ey1, EAVE)
box(RF, "Fascia_Brown", ex1, ey0, EAVE - 0.18, ex1 + 0.03, ey1, EAVE)

# front gable roof over balcony (ridge along Y at x = 8.62)
gx0, gx1 = 5.30, 11.95
gc = (gx0 + gx1) / 2
gpitch = math.radians(35)
gz = EAVE + (gc - gx0) * math.tan(gpitch)
slope_front = math.tan(pitch)
gy_back = ey0 + (gz - EAVE) / slope_front + 0.05   # where gable ridge meets hip roof
gy0 = -1.30
# gable roof as two thin sloped slabs (open gable end shows soffit + gable wall)
prism(RF, "Roof_Tile", [(gx0, EAVE - 0.12), (gc, gz - 0.12), (gc, gz), (gx0, EAVE)], gy0, gy_back)
prism(RF, "Roof_Tile", [(gc, gz - 0.12), (gx1, EAVE - 0.12), (gx1, EAVE), (gc, gz)], gy0, gy_back)
# gable frame (thick white trim, per elevation 1)
tr = 0.18
prism("Gable", "Wall_White", [(gx0, EAVE - 0.2), (gx0 + 0.25, EAVE - 0.2), (gc, gz - 0.3),
                               (gx1 - 0.25, EAVE - 0.2), (gx1, EAVE - 0.2), (gx1, EAVE), (gc, gz + 0.02), (gx0, EAVE)],
      gy0 - 0.02, gy0 + tr) if False else None
def roof_z(xx):
    return gz - abs(xx - gc) * math.tan(gpitch)
# gable infill wall above balcony doors (grey vertical cladding)
gl, grt = 5.9, 11.35
prism("Gable", "Wall_White", [(gl, EAVE), (grt, EAVE), (grt, roof_z(grt) - 0.08), (gc, gz - 0.12), (gl, roof_z(gl) - 0.08)],
      -TU/2, TU/2)
# gable white frame posts down to balcony (portal frame in elevation 1)
for px in (6.0, 11.25):
    box("Gable", "Wall_White", px - 0.1, -1.30, SLAB_T, px + 0.1, -1.10, roof_z(px) - 0.05)
# raking trim boards under the gable roof edge at front
L = math.hypot(gc - gx0, gz - EAVE)
for sgn in (-1, 1):
    pts = []
    x_out = gc + sgn * (gc - gx0)
    # thin board following the rake, 0.25 deep, 0.2 high
    prof = [(x_out, EAVE - 0.2), (x_out, EAVE), (gc, gz), (gc, gz - 0.2)] if sgn == 1 else \
           [(gc, gz - 0.2), (gc, gz), (x_out, EAVE), (x_out, EAVE - 0.2)]
    prism("Gable", "Fascia_Brown", prof, gy0 - 0.02, gy0 + 0.25)
# dark soffit under the projecting gable roof
for xo in (gx0, gx1):
    add("Gable", "Soffit_Dark", [(xo, gy0, EAVE - 0.01), (gc, gy0, gz - 0.01), (gc, 0.0, gz - 0.01), (xo, 0.0, EAVE - 0.01)])
# taupe vertical-board panel left of balcony door, white pilaster
GP = "Gable"; px0, px1 = 5.95, 7.55; fy = -TU/2 - 0.02
wall(GP, "x", fy, px0, px1, SLAB_T, EAVE, 0.03, [(6.4, 7.35, SLAB_T, 5.5, None)], mat="Accent_Taupe")
prism(GP, "Accent_Taupe", [(px0, EAVE), (px1, EAVE), (px1, roof_z(px1) - 0.1), (px0, roof_z(px0) - 0.1)], fy - 0.015, fy + 0.015)
xg = px0 + 0.25
while xg < px1 - 0.1:
    box(GP, "Soffit_Dark", xg, fy - 0.02, EAVE - 0.05 if 6.4 < xg < 7.35 else SLAB_T, xg + 0.012, fy - 0.014, roof_z(xg) - 0.12)
    xg += 0.30
box(GP, "Trim_White", px1, fy - 0.03, SLAB_T, px1 + 0.22, fy + 0.02, roof_z(px1 + 0.22) - 0.08)
# right-side taupe return band inside gable frame
box(GP, "Accent_Taupe", 11.05, -1.0, SLAB_T, 11.30, -0.08, roof_z(11.2) - 0.1)

# ================================================================ ROOF DETAIL: tile courses, ridge caps, valleys, finial
MATS["Roof_Tile_RX"] = MATS["Roof_Tile"]          # ribs vary along X (front/back slopes)
MATS["Roof_Tile_RY"] = MATS["Roof_Tile"]          # ribs vary along Y (side slopes, gable slopes)
MATS["Roof_Ridge"] = (0.32, 0.25, 0.235, 1.0)
MATS["Flashing"] = (0.25, 0.25, 0.26, 1.0)
def cylinder(group, mat, cx, cy, r, z0, z1, n=32):
    pts = [(cx + r*math.cos(2*math.pi*i/n), cy + r*math.sin(2*math.pi*i/n)) for i in range(n)]
    add(group, mat, [(x, y, z0) for x, y in pts[::-1]])
    add(group, mat, [(x, y, z1) for x, y in pts])
    for i in range(n):
        (xa, ya), (xb, yb) = pts[i], pts[(i+1) % n]
        add(group, mat + "~s", [(xa, ya, z0), (xb, yb, z0), (xb, yb, z1), (xa, ya, z1)])

RT = "Roof tiles"; RR = "Roof ridges"
V = lambda *a: np.array(a, dtype=float)

def clip(poly, f, keep_ge, val):
    out = []
    n = len(poly)
    for i in range(n):
        p, q = poly[i], poly[(i+1) % n]
        fp, fq = f(p) - val, f(q) - val
        if not keep_ge: fp, fq = -fp, -fq
        if fp >= 0: out.append(p)
        if (fp >= 0) != (fq >= 0):
            t = fp / (fp - fq); out.append(p + t * (q - p))
    return out

def tile_courses(poly, e0, e1, mat, course=0.32, lip=0.055, base=0.015, cuts=()):
    poly = [V(*p) for p in poly]; e0, e1 = V(*e0), V(*e1)
    ed = (e1 - e0) / np.linalg.norm(e1 - e0)
    nrm = np.cross(poly[1] - poly[0], poly[2] - poly[0]); nrm /= np.linalg.norm(nrm)
    if nrm[2] < 0: nrm = -nrm
    u = np.cross(nrm, ed); u /= np.linalg.norm(u)
    if np.dot(np.mean(poly, 0) - e0, u) < 0: u = -u
    f = lambda p: np.dot(p - e0, u)
    tmax = max(f(p) for p in poly)
    t0 = -0.03
    while t0 < tmax:
        t1 = t0 + course
        band = clip(clip(poly, f, True, max(t0, 0.0)), f, False, t1)
        for cf, ge, cv in cuts:
            if len(band) >= 3: band = clip(band, cf, ge, cv)
        if len(band) >= 3:
            off = lambda p: p + nrm * (base + lip * (t1 - f(p)) / course)
            bot = [p + nrm * 0.002 for p in band]
            top = [off(p) for p in band]
            add(RT, mat, top)
            add(RT, mat, bot[::-1])
            for i in range(len(band)):
                j = (i + 1) % len(band)
                add(RT, mat, [bot[i], bot[j], top[j], top[i]])
        t0 = t1

def ridge(a, b, r=0.11, mat="Roof_Ridge", seg=8, lift=0.05, ring=0.42):
    a, b = V(*a), V(*b)
    d = b - a; L = np.linalg.norm(d); d /= L
    s = np.cross(d, [0, 0, 1.0]);
    s = s / np.linalg.norm(s) if np.linalg.norm(s) > 1e-6 else V(1, 0, 0)
    up = np.cross(s, d)
    prof = [s * r * math.cos(math.pi * k / seg) + up * (lift + r * 0.8 * math.sin(math.pi * k / seg)) for k in range(seg + 1)]
    pa = [a + p for p in prof]; pb = [b + p for p in prof]
    for k in range(seg):
        add(RR, mat, [pa[k], pa[k+1], pb[k+1], pb[k]])
    add(RR, mat, pa[::-1]); add(RR, mat, pb)
    n = int(L / ring)                                   # overlap rings of ridge tiles
    for i in range(1, n + 1):
        c = a + d * min(i * ring, L - 0.02)
        rp = [c + p * 1.06 - up * 0.004 for p in prof]
        rq = [q + d * 0.04 for q in rp]
        for k in range(seg):
            add(RR, mat, [rp[k], rp[k+1], rq[k+1], rq[k]])

Av, Bv, Cv, Dv, Pv, Qv = map(lambda t: V(*t), (A, B, C, D, P, Q))
# hip roof faces
tgp = math.tan(gpitch)
FX = lambda p: p[0]
ZL = lambda p: p[2] - (EAVE + (p[0] - gx0) * tgp)      # >=0 : hip above left gable slope
ZR = lambda p: p[2] - (EAVE + (gx1 - p[0]) * tgp)      # >=0 : hip above right gable slope
FRONT_CUTS = [((FX, False, gx0),), ((FX, True, gx1),),
              ((FX, True, gx0), (FX, False, gc), (ZL, True, 0.0)),
              ((FX, True, gc), (FX, False, gx1), (ZR, True, 0.0))]
front = [V(*A), V(*B), V(*Q), V(*P)]
for cs in FRONT_CUTS:
    tile_courses([A, B, Q, P], A, B, "Roof_Tile_RX", cuts=cs)
    pc = front
    for cf, ge, cv in cs:
        if len(pc) >= 3: pc = clip(pc, cf, ge, cv)
    if len(pc) >= 3: add(RF, "Roof_Tile", pc)          # base surface under the tiles
# hip soffit, left open under the projecting gable (in front of gable wall)
sof = [V(*A), V(*D), V(*C), V(*B)]
FY = lambda p: p[1]
for cs in (((FX, False, gx0),), ((FX, True, gx1),), ((FX, True, gx0), (FX, False, gx1), (FY, True, 0.0))):
    pc = sof
    for cf, ge, cv in cs:
        if len(pc) >= 3: pc = clip(pc, cf, ge, cv)
    if len(pc) >= 3: add(RF, "Soffit_Dark", pc)
# front fascia only outside the gable
box(RF, "Fascia_Brown", ex0, ey0 - 0.03, EAVE - 0.18, gx0, ey0, EAVE)
box(RF, "Fascia_Brown", gx1, ey0 - 0.03, EAVE - 0.18, ex1, ey0, EAVE)
tile_courses([C, D, P, Q], C, D, "Roof_Tile_RX")
tile_courses([D, A, P], D, A, "Roof_Tile_RY")
tile_courses([B, C, Q], B, C, "Roof_Tile_RY")
# gable slopes
GL = [(gx0, gy0, EAVE), (gx0, gy_back, EAVE), (gc, gy_back, gz), (gc, gy0, gz)]
GR = [(gx1, gy_back, EAVE), (gx1, gy0, EAVE), (gc, gy0, gz), (gc, gy_back, gz)]
tile_courses(GL, GL[0], GL[1], "Roof_Tile_RY")
tile_courses(GR, GR[0], GR[1], "Roof_Tile_RY")
# ridges & hips
ridge(P, Q)
for e, top in ((A, P), (D, P), (B, Q), (C, Q)):
    ridge(e, top)
yv = ey0 + (gz - EAVE) / math.tan(pitch)
ridge((gc, gy0 - 0.05, gz), (gc, yv, gz))                                  # gable ridge
# valleys where gable meets hip roof (metal flashing strip)
for xo in (gx0, gx1):
    a = V(xo, ey0, EAVE); b = V(gc, yv, gz)
    d = b - a; d /= np.linalg.norm(d); s = np.cross(d, [0, 0, 1.0]); s /= np.linalg.norm(s)
    add(RR, "Flashing", [a - s*0.18 + V(0,0,0.03), a + s*0.18 + V(0,0,0.03), b + s*0.18 + V(0,0,0.03), b - s*0.18 + V(0,0,0.03)])
# gable apex finial + hip-end caps
cylinder(RR, "Roof_Ridge", gc, gy0 + 0.05, 0.12, gz + 0.04, gz + 0.20, n=12)
for e in (A, B, C, D):
    cylinder(RR, "Roof_Ridge", e[0], e[1], 0.10, EAVE + 0.02, EAVE + 0.14, n=10)
# eave bird-stop / first-course edge strip
for (xa, xb, yy) in ((ex0, gx0, ey0), (gx1, ex1, ey0), (ex0, ex1, ey1)):
    box(RR, "Fascia_Brown", xa, yy - 0.01, EAVE - 0.01, xb, yy + 0.01, EAVE + 0.07)
for (p0, p1) in ((D, A), (B, C)):
    box(RR, "Fascia_Brown", p0[0] - 0.01, min(p0[1], p1[1]), EAVE - 0.01, p0[0] + 0.01, max(p0[1], p1[1]), EAVE + 0.07)

# ================================================================ EXTENSIONS (ส่วนต่อเติม)
MATS["Slat_White"] = (0.97, 0.97, 0.97, 1.0)
MATS["Floor_Tile"] = (0.86, 0.84, 0.80, 1.0)
MATS["Tank_White"] = (0.96, 0.96, 0.96, 1.0)

def cylinder(group, mat, cx, cy, r, z0, z1, n=32):
    pts = [(cx + r*math.cos(2*math.pi*i/n), cy + r*math.sin(2*math.pi*i/n)) for i in range(n)]
    add(group, mat, [(x, y, z0) for x, y in pts[::-1]])
    add(group, mat, [(x, y, z1) for x, y in pts])
    for i in range(n):
        (xa, ya), (xb, yb) = pts[i], pts[(i+1) % n]
        add(group, mat + "~s", [(xa, ya, z0), (xb, yb, z0), (xb, yb, z1), (xa, ya, z1)])

# --- 1) New room in carport (2.89 x 3.52 m) between grid 5-4, against kitchen
XR = "Ext - Carport room"
RX0, RX1, RY0, RY1 = 0.0, 2.89, 3.23, 6.75
RFL = 0.45
box(XR, "Floor_Tile", RX0, RY0, CAR_FFL, RX1, RY1, RFL)
wall(XR, "y", RX0 + 0.06, RY0, RY1, 0, H1, 0.12, [(4.0, 5.9, 1.0, 2.2, "glass")])        # side window (grid 5)
wall(XR, "x", RY0 + 0.06, RX0, RX1, 0, H1, 0.12, [(0.55, 2.25, RFL, 2.5, "glass")])      # front sliding window-door
wall(XR, "x", RY1 - 0.06, RX0, 2.8, 0, H1, 0.12)                                          # back wall
# (door to kitchen = existing kitchen side door on x = 2.9)

# --- 2) Rear extension: 3 bays behind the house
EY0, EY1 = 6.75, 8.50          # depth of extension
EZ_W, EZ_R = 2.95, 3.15        # wall top / roof top
B1 = "Ext - Laundry yard"; B2 = "Ext - Rear room"; B3 = "Ext - Rear kitchen"; ER = "Ext - Roof"
# floors (on ground beams + piles per sketch)
box(B2, "Floor_Tile", 2.85, EY0, 0, 6.80, EY1, 0.40)
box(B3, "Floor_Tile", 6.80, 6.20, 0, 11.45, EY1, 0.40)

# bay 1 – laundry yard: slat screens on side + back, water tank
X1a, X1b = -0.55, 2.85
def slat_screen(group, axis, c, s0, s1, z0=CAR_FFL, z1=EZ_W):
    posts = [s0, s1] + [s0 + (s1 - s0) * k / 2 for k in (1,)]
    for p in posts:
        if axis == "x": box(group, "Rail_Black", p-0.04, c-0.04, 0, p+0.04, c+0.04, z1)
        else:           box(group, "Rail_Black", c-0.04, p-0.04, 0, c+0.04, p+0.04, z1)
    for zr in (z0 + 0.05, (z0 + z1) / 2, z0 + 2*(z1 - z0)/3 + 0.25, z1 - 0.05):
        if axis == "x": box(group, "Rail_Black", s0, c-0.03, zr-0.03, s1, c+0.03, zr+0.03)
        else:           box(group, "Rail_Black", c-0.03, s0, zr-0.03, c+0.03, s1, zr+0.03)
    s = s0 + 0.08
    while s < s1 - 0.08:
        if axis == "x": box(group, "Slat_White", s, c-0.015, z0+0.08, s+0.05, c+0.015, z1-0.08)
        else:           box(group, "Slat_White", c-0.015, s, z0+0.08, c+0.015, s+0.05, z1-0.08)
        s += 0.10
slat_screen(B1, "y", X1a, EY0 + 0.05, EY1)       # side screen (boundary side)
slat_screen(B1, "x", EY1, X1a, X1b)              # back screen
cylinder("08 ระบบประปา::ถังเก็บน้ำ 1,000 ลิตร", "Tank_White", 0.35, 7.85, 0.50, CAR_FFL, CAR_FFL + 1.9)   # water tank

# bay 2 – rear room (behind kitchen)
wall(B2, "x", EY1 - 0.06, 2.85, 6.80, 0, EZ_W, 0.12)                                       # back
wall(B2, "y", 2.91, EY0, EY1, 0, EZ_W, 0.12, [(7.5, 8.3, 0.40, 2.3, "glass")])            # left (to laundry)
wall(B2, "y", 6.80, EY0, EY1, 0, EZ_W, 0.15, [(7.3, 8.2, 0.40, 2.3, "glass")])            # partition to bay 3

# bay 3 – rear kitchen / wash area
wall(B3, "x", EY1 - 0.06, 6.80, 11.45, 0, EZ_W, 0.12)                                      # back
wall(B3, "y", 11.39, 6.20, EY1, 0, EZ_W, 0.12, [(7.2, 8.15, 0.40, 2.4, "glass")])         # end wall with glass door

# roofs: three flat slabs with skylight glass + rafters underneath
for (rx0, rx1, zt, sky) in ((X1a - 0.15, X1b, EZ_R - 0.05, (0.85, 2.45)),
                            (X1b, 6.80, EZ_R, (3.65, 5.15)),
                            (6.80, 11.75, EZ_R, None)):
    ry0, ry1 = EY0 - 0.05 if rx1 <= 6.8 else 6.15, EY1 + 0.20
    if sky:
        sx0, sx1 = sky
        box(ER, "Roof_Membrane", rx0, ry0, zt - 0.15, sx0, ry1, zt)
        box(ER, "Roof_Membrane", sx1, ry0, zt - 0.15, rx1, ry1, zt)
        box(ER, "Roof_Membrane", sx0, ry0, zt - 0.15, sx1, ry0 + 0.15, zt)
        box(ER, "Roof_Membrane", sx0, ry1 - 0.15, zt - 0.15, sx1, ry1, zt)
        box(ER, "Glass", sx0, ry0 + 0.15, zt - 0.08, sx1, ry1 - 0.15, zt - 0.05)
        for gx in (sx0, (sx0 + sx1) / 2, sx1):          # glazing bars
            box(ER, "Rail_Black", gx - 0.025, ry0 + 0.15, zt - 0.08, gx + 0.025, ry1 - 0.15, zt - 0.02)
        for gy in (ry0 + (ry1 - ry0) / 2,):
            box(ER, "Rail_Black", sx0, gy - 0.025, zt - 0.08, sx1, gy + 0.025, zt - 0.02)
    else:
        box(ER, "Roof_Membrane", rx0, ry0, zt - 0.15, rx1, ry1, zt)
    box(ER, "Wall_White", rx0, ry1 - 0.02, zt - 0.30, rx1, ry1 + 0.03, zt + 0.03)   # fascia
    xr = rx0 + 0.4
    while xr < rx1 - 0.2:                                                        # rafters
        box(ER, "Rail_Black", xr - 0.03, ry0, zt - 0.27, xr + 0.03, ry1 - 0.05, zt - 0.15)
        xr += 0.9

# ---------------------------------------------------------------- boundary fence (grey, per photos)
FN = "Fence"
LX0, LX1, LY0, LY1 = -1.10, 14.30, -4.25, 8.80
box(FN, "Fence_Grey", LX0 - 0.15, LY0, 0, LX0, LY1, 2.0)
box(FN, "Fence_Grey", LX1, LY0, 0, LX1 + 0.15, LY1, 2.0)
box(FN, "Fence_Grey", LX0 - 0.15, LY1, 0, LX1 + 0.15, LY1 + 0.15, 2.0)
box(FN, "Fence_Grey", LX0 - 0.15, LY0 - 0.15, 0, -0.2, LY0, 1.2)            # front low wall (left)
box(FN, "Fence_Grey", 6.3, LY0 - 0.15, 0, 7.2, LY0, 1.4)                     # mailbox pillar
box(FN, "Fence_Grey", 8.4, LY0 - 0.15, 0, LX1 + 0.15, LY0, 1.2)             # front low wall (right)
for gx0_, gx1_ in ((-0.2, 6.3), (7.2, 8.4)):                                  # black gates
    box(FN, "Rail_Black", gx0_, LY0 - 0.10, 0.05, gx1_, LY0 - 0.05, 0.10)
    box(FN, "Rail_Black", gx0_, LY0 - 0.10, 1.45, gx1_, LY0 - 0.05, 1.50)
    xb = gx0_ + 0.05
    while xb < gx1_:
        box(FN, "Rail_Black", xb, LY0 - 0.09, 0.10, xb + 0.025, LY0 - 0.06, 1.45); xb += 0.12


# ---------------------------------------------------------------- U-stair per A1-01/A1-02
# flight 1 rises from dining side (y 2.0) toward the front, winders at front, flight 2 rises back to upper hall (y 3.0)
S = "Stair"; rise = (SLAB_T - GF_FFL) / 18
def tread(x0_, y0_, x1_, y1_, k):
    box(S, "Stair_Wood", x0_, y0_, GF_FFL + k*rise - 0.04, x1_, y1_, GF_FFL + k*rise)
    box(S, "Wall_White", x0_, y0_, GF_FFL, x1_, y1_, GF_FFL + k*rise - 0.04)
for k in range(1, 6):                                   # flight 1 (5 treads)
    tread(5.97, 2.0 - k*0.25, 6.93, 2.25 - k*0.25, k)
tread(5.97, 0.40, 6.93, 0.75, 6); tread(5.97, 0.05, 6.93, 0.40, 7)   # winders
tread(6.97, 0.05, 7.99, 0.40, 8); tread(6.97, 0.40, 7.99, 0.75, 9)
for k in range(10, 18):                                 # flight 2 (8 treads)
    yy = 0.75 + (k - 10) * 0.28
    box(S, "Stair_Wood", 6.97, yy, GF_FFL + k*rise - 0.04, 7.99, yy + 0.28, GF_FFL + k*rise)
    box(S, "Wall_White", 6.97, yy, GF_FFL + k*rise - 0.30, 7.99, yy + 0.28, GF_FFL + k*rise - 0.04)  # waist slab
# handrails: stair side + upper void balustrades
def rail(group, x0_, y0_, z0_, x1_, y1_, z1_, h=0.9):
    import numpy as _np
    a = _np.array([x0_, y0_, z0_]); b = _np.array([x1_, y1_, z1_])
    L = _np.linalg.norm(b - a); n_ = max(2, int(L / 0.12))
    for i in range(n_ + 1):
        p = a + (b - a) * i / n_
        box(group, "Rail_Black", p[0]-0.012, p[1]-0.012, p[2], p[0]+0.012, p[1]+0.012, p[2] + h)
    d = (b - a) / L
    add(group, "Rail_Black", [a + [0, 0, h], b + [0, 0, h], b + [0, 0, h + 0.05], a + [0, 0, h + 0.05]])
    add(group, "Rail_Black", [a + [0, 0, h + 0.05], b + [0, 0, h + 0.05], b + [0, 0, h], a + [0, 0, h]])
rail(S, 6.95, 2.0, GF_FFL, 6.95, 0.75, GF_FFL + 5*rise)                 # inner rail flight 1
rail(S, 6.99, 0.75, GF_FFL + 9*rise, 6.99, 2.99, GF_FFL + 17*rise)      # inner rail flight 2
rail(S, 5.93, 1.5, SLAB_T, 6.97, 1.5, SLAB_T)                           # upper void edge
rail(S, 6.97, 1.5, SLAB_T, 6.97, 3.0, SLAB_T)
MATS["Stair_Wood"] = (0.62, 0.45, 0.30, 1.0)

exec(open(os.path.join(HOUSE_DIR, "detail.py"), encoding="utf-8").read())

# (exporters live in make_blend.py: Blender scene + GLB for the web app)
