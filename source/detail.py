# -*- coding: utf-8 -*-
# Interior walls, furniture, utilities (E-01..E-07, SN-01..SN-04), front yard.
# Group names use "<collection>::<object>" so Blender/web viewer can toggle per layer.
import math
import numpy as np

MATS.update({
    "Fabric_Grey": (0.55, 0.56, 0.57, 1.0), "Fabric_Beige": (0.80, 0.74, 0.64, 1.0),
    "Wood_Light": (0.78, 0.64, 0.46, 1.0), "Wood_Dark": (0.38, 0.27, 0.19, 1.0),
    "Mattress_White": (0.95, 0.95, 0.93, 1.0), "Ceramic_White": (0.96, 0.96, 0.96, 1.0),
    "Metal_Steel": (0.70, 0.72, 0.74, 1.0), "Cabinet_White": (0.93, 0.92, 0.90, 1.0),
    "Plant_Green": (0.25, 0.45, 0.22, 1.0), "Pot_Terracotta": (0.66, 0.38, 0.25, 1.0),
    "Car_Paint": (0.85, 0.86, 0.88, 1.0), "Tyre_Black": (0.08, 0.08, 0.08, 1.0),
    "TV_Black": (0.05, 0.05, 0.06, 1.0), "Light_Fixture": (1.0, 0.97, 0.88, 1.0),
    "Rug": (0.62, 0.58, 0.52, 1.0), "Counter_Top": (0.20, 0.20, 0.21, 1.0),
    "Pipe_Supply": (0.15, 0.40, 0.80, 1.0), "Pipe_Waste": (0.45, 0.45, 0.47, 1.0),
    "Pipe_Soil": (0.55, 0.33, 0.18, 1.0), "Pipe_Vent": (0.30, 0.65, 0.35, 1.0),
    "Pipe_Rain": (0.60, 0.60, 0.95, 1.0),
    "Conduit_Power": (0.95, 0.50, 0.10, 1.0), "Cable_Black": (0.05, 0.05, 0.05, 1.0),
    "Conduit_Telecom": (0.95, 0.85, 0.15, 1.0), "AC_White": (0.97, 0.97, 0.97, 1.0),
    "AC_Grey": (0.62, 0.63, 0.64, 1.0), "Refrig_Line": (0.12, 0.12, 0.12, 1.0),
    "Septic_Tank": (0.20, 0.42, 0.30, 1.0), "Manhole": (0.55, 0.55, 0.53, 1.0),
    "Hedge_Green": (0.22, 0.40, 0.18, 1.0), "Tree_Trunk": (0.35, 0.25, 0.17, 1.0),
    "Tree_Leaf": (0.28, 0.50, 0.22, 1.0), "Road": (0.62, 0.62, 0.60, 1.0),
    "Stepping_Stone": (0.80, 0.79, 0.76, 1.0), "Panel_Grey": (0.45, 0.46, 0.48, 1.0),
    "Grab_Bar": (0.85, 0.85, 0.86, 1.0),
})

L1 = "01 ชั้นล่าง-สถาปัตย์"; L2 = "02 ชั้นบน-สถาปัตย์"
F1 = "05 ตกแต่งภายใน ชั้นล่าง"; F2 = "06 ตกแต่งภายใน ชั้นบน"; FX = "04 ส่วนต่อเติม"
EL = "07 ระบบไฟฟ้า"; WS = "08 ระบบประปา"; DR = "09 ระบบระบายน้ำ-บำบัด"; AC = "10 ระบบปรับอากาศ"
TC = "11 ระบบสื่อสาร-ทีวี"; ST = "12 ภูมิทัศน์-รั้ว-ถนน"
def G_(layer, name): return f"{layer}::{name}"

CEIL1, CEIL2 = 3.30, 6.30          # ceiling levels ground / upper

# ---------------------------------------------------------------- generic helpers
def tube(group, mat, pts, r=0.03, n=12):
    pts = [np.array(p, float) for p in pts]
    for a, b in zip(pts[:-1], pts[1:]):
        d = b - a; L = np.linalg.norm(d)
        if L < 1e-6: continue
        d /= L
        ref = np.array([0, 0, 1.0]) if abs(d[2]) < 0.9 else np.array([1.0, 0, 0])
        u = np.cross(d, ref); u /= np.linalg.norm(u); v = np.cross(d, u)
        ring = [r * (math.cos(2*math.pi*k/n) * u + math.sin(2*math.pi*k/n) * v) for k in range(n)]
        A_ = [a + q for q in ring]; B_ = [b + q for q in ring]
        for k in range(n):
            add(group, mat + "~s", [A_[k], A_[(k+1) % n], B_[(k+1) % n], B_[k]])
        add(group, mat, A_[::-1]); add(group, mat, B_)

def sag(p0, p1, dip=0.6, n=10):
    p0, p1 = np.array(p0, float), np.array(p1, float)
    return [p0 + (p1 - p0) * t - np.array([0, 0, dip * 4 * t * (1 - t)]) for t in np.linspace(0, 1, n + 1)]

def disk(group, mat, x, y, z, r=0.10, h=0.03):
    cylinder(group, mat, x, y, r, z - h, z, n=16)

# ================================================================ 1. INTERIOR WALLS (read from A1-01 / A1-02)
GW = G_(L1, "ผนังภายใน ชั้นล่าง")
wall(GW, "x", 4.70, 2.9, 5.95, 0, SLAB_B, 0.10)                                         # bath-3 / closet
wall(GW, "y", 5.95, 3.0, 4.70, 0, SLAB_B, 0.10, [(3.35, 4.05, GF_FFL, GF_FFL + 2.05, "wood")])   # bath-3 door
wall(GW, "y", 5.95, 4.70, 6.75, 0, SLAB_B, 0.10, [(5.05, 5.85, GF_FFL, GF_FFL + 2.05, "wood")])  # walk-in closet door (former kitchen opening)
wall(GW, "y", 8.03, 0.0, 3.12, 0, SLAB_B, 0.10)                                         # stair / living (TV wall)
wall(GW, "x", 3.12, 6.97, 8.03, 0, SLAB_B, 0.10, [(7.15, 7.85, GF_FFL, GF_FFL + 2.0, "wood")])   # storage door
wall(GW, "y", 6.93, 1.03, 3.12, 0, GF_FFL + 1.5, 0.08)                                  # stringer wall flight-1 / storage
UW = G_(L2, "ผนังภายใน ชั้นบน")
wall(UW, "x", 3.12, 2.9, 5.91, SLAB_T, EAVE, 0.10)                                      # bed-2 / bed-3
wall(UW, "y", 8.03, 0.0, 6.2, SLAB_T, EAVE, 0.10, [(3.25, 3.95, SLAB_T, SLAB_T + 2.1, "wood")])  # bed-1 door
wall(UW, "x", 4.20, 5.91, 8.03, SLAB_T, EAVE, 0.10, [(6.60, 7.30, SLAB_T, SLAB_T + 2.05, "wood")])  # bath-2
wall(UW, "y", 9.59, 3.56, 6.2, SLAB_T, EAVE, 0.10, [(4.55, 5.25, SLAB_T, SLAB_T + 2.05, "wood")])  # bath-1
wall(UW, "x", 3.56, 9.59, 11.35, SLAB_T, EAVE, 0.10)
# ceilings (gypsum) so cut-away views read as rooms
box(G_(L1, "ฝ้าเพดาน ชั้นล่าง"), "Cabinet_White", 2.9, 0.0, CEIL1, 5.9, 6.75, CEIL1 + 0.01)
box(G_(L1, "ฝ้าเพดาน ชั้นล่าง"), "Cabinet_White", 8.03, 0.0, CEIL1, 11.35, 6.2, CEIL1 + 0.01)
box(G_(L1, "ฝ้าเพดาน ชั้นล่าง"), "Cabinet_White", 5.9, 3.12, CEIL1, 8.03, 6.2, CEIL1 + 0.01)

# ================================================================ 2. FURNITURE
def bed(group, x0, y0, x1, y1, head, z):          # head: 'x0','x1','y0','y1'
    box(group, "Wood_Dark", x0, y0, z, x1, y1, z + 0.30)
    box(group, "Mattress_White", x0 + 0.03, y0 + 0.03, z + 0.30, x1 - 0.03, y1 - 0.03, z + 0.52)
    if head == "x0":
        box(group, "Fabric_Beige", x0 - 0.06, y0, z, x0, y1, z + 1.10)
        for yy in (y0 + 0.2, (y0 + y1) / 2 + 0.05):
            box(group, "Mattress_White", x0 + 0.05, yy, z + 0.52, x0 + 0.45, yy + (y1 - y0) / 2 - 0.25, z + 0.66)
        box(group, "Fabric_Grey", x0 + (x1 - x0) * 0.55, y0 + 0.02, z + 0.52, x1 - 0.02, y1 - 0.02, z + 0.56)
    elif head == "x1":
        box(group, "Fabric_Beige", x1, y0, z, x1 + 0.06, y1, z + 1.10)
        for yy in (y0 + 0.2, (y0 + y1) / 2 + 0.05):
            box(group, "Mattress_White", x1 - 0.45, yy, z + 0.52, x1 - 0.05, yy + (y1 - y0) / 2 - 0.25, z + 0.66)
        box(group, "Fabric_Grey", x0 + 0.02, y0 + 0.02, z + 0.52, x0 + (x1 - x0) * 0.45, y1 - 0.02, z + 0.56)
    elif head == "y1":
        box(group, "Fabric_Beige", x0, y1, z, x1, y1 + 0.06, z + 1.10)
        for xx in (x0 + 0.15, (x0 + x1) / 2 + 0.05):
            box(group, "Mattress_White", xx, y1 - 0.45, z + 0.52, xx + (x1 - x0) / 2 - 0.2, y1 - 0.05, z + 0.66)
        box(group, "Fabric_Grey", x0 + 0.02, y0 + 0.02, z + 0.52, x1 - 0.02, y0 + (y1 - y0) * 0.45, z + 0.56)
    else:  # y0
        box(group, "Fabric_Beige", x0, y0 - 0.06, z, x1, y0, z + 1.10)
        for xx in (x0 + 0.15, (x0 + x1) / 2 + 0.05):
            box(group, "Mattress_White", xx, y0 + 0.05, z + 0.52, xx + (x1 - x0) / 2 - 0.2, y0 + 0.45, z + 0.66)
        box(group, "Fabric_Grey", x0 + 0.02, y0 + (y1 - y0) * 0.55, z + 0.52, x1 - 0.02, y1 - 0.02, z + 0.56)

def cabinet(group, x0, y0, x1, y1, z, h, mat="Cabinet_White", top=None):
    box(group, mat, x0, y0, z, x1, y1, z + h)
    if top: box(group, top, x0 - 0.01, y0 - 0.01, z + h, x1 + 0.01, y1 + 0.01, z + h + 0.04)

def chair(group, cx, cy, z, face, mat="Wood_Light"):    # face = direction the sitter looks: 'x+','x-','y+','y-'
    s = 0.22
    box(group, mat, cx - s, cy - s, z + 0.42, cx + s, cy + s, z + 0.47)
    for dx in (-s + 0.03, s - 0.03):
        for dy in (-s + 0.03, s - 0.03):
            box(group, mat, cx + dx - 0.02, cy + dy - 0.02, z, cx + dx + 0.02, cy + dy + 0.02, z + 0.42)
    bx = {"x+": (cx - s, cy - s, cx - s + 0.04, cy + s), "x-": (cx + s - 0.04, cy - s, cx + s, cy + s),
          "y+": (cx - s, cy - s, cx + s, cy - s + 0.04), "y-": (cx - s, cy + s - 0.04, cx + s, cy + s)}[face]
    box(group, mat, bx[0], bx[1], z + 0.47, bx[2], bx[3], z + 0.90)

def table(group, x0, y0, x1, y1, z, h=0.75, top="Wood_Light", leg="Wood_Dark"):
    box(group, top, x0, y0, z + h - 0.04, x1, y1, z + h)
    for (lx, ly) in ((x0 + 0.05, y0 + 0.05), (x1 - 0.09, y0 + 0.05), (x0 + 0.05, y1 - 0.09), (x1 - 0.09, y1 - 0.09)):
        box(group, leg, lx, ly, z, lx + 0.04, ly + 0.04, z + h - 0.04)

def sofa(group, x0, y0, x1, y1, z, back):          # back side: 'x0','x1','y0','y1'
    box(group, "Fabric_Grey", x0, y0, z, x1, y1, z + 0.42)
    t = 0.18
    bk = {"x0": (x0, y0, x0 + t, y1), "x1": (x1 - t, y0, x1, y1), "y0": (x0, y0, x1, y0 + t), "y1": (x0, y1 - t, x1, y1)}[back]
    box(group, "Fabric_Grey", bk[0], bk[1], z + 0.42, bk[2], bk[3], z + 0.85)
    if back in ("x0", "x1"):
        box(group, "Fabric_Grey", x0, y0, z + 0.42, x1, y0 + 0.15, z + 0.62); box(group, "Fabric_Grey", x0, y1 - 0.15, z + 0.42, x1, y1, z + 0.62)
    else:
        box(group, "Fabric_Grey", x0, y0, z + 0.42, x0 + 0.15, y1, z + 0.62); box(group, "Fabric_Grey", x1 - 0.15, y0, z + 0.42, x1, y1, z + 0.62)

def plant(group, x, y, z, h=1.1):
    cylinder(group, "Pot_Terracotta", x, y, 0.16, z, z + 0.32, n=10)
    cylinder(group, "Plant_Green", x, y, 0.28, z + 0.32, z + h, n=10)

def toilet(group, x, y, z, back):                  # back = wall side 'x0','x1','y0','y1'
    dx, dy = {"x0": (1, 0), "x1": (-1, 0), "y0": (0, 1), "y1": (0, -1)}[back]
    # tank against wall, bowl projecting
    tx, ty = x, y
    if dx: box(group, "Ceramic_White", tx - 0.10 * dx - 0.09, ty - 0.20, z, tx - 0.10 * dx + 0.09, ty + 0.20, z + 0.80)
    else:  box(group, "Ceramic_White", tx - 0.20, ty - 0.10 * dy - 0.09, z, tx + 0.20, ty - 0.10 * dy + 0.09, z + 0.80)
    cylinder(group, "Ceramic_White", x + dx * 0.25, y + dy * 0.25, 0.19, z, z + 0.42, n=14)

def basin(group, x0, y0, x1, y1, z):
    cabinet(group, x0, y0, x1, y1, z, 0.80, "Wood_Light", "Ceramic_White")
    cylinder(group, "Ceramic_White", (x0 + x1) / 2, (y0 + y1) / 2, 0.18, z + 0.84, z + 0.90, n=14)

def shower(group, x0, y0, x1, y1, z, glass_side, gx):
    box(group, "Panel_Grey", x0, y0, z, x1, y1, z + 0.02)                    # shower floor
    if glass_side == "x": box(group, "Glass", gx - 0.005, y0, z, gx + 0.005, y1, z + 2.0)
    else:                 box(group, "Glass", x0, gx - 0.005, z, x1, gx + 0.005, z + 2.0)

def tv(group, axis, c, a0, a1, z0, z1, side):
    if axis == "y": box(group, "TV_Black", c, a0, z0, c + 0.04 * side, a1, z1)
    else:           box(group, "TV_Black", a0, c, z0, a1, c + 0.04 * side, z1)

def wardrobe(group, x0, y0, x1, y1, z, h=2.3):
    box(group, "Wood_Light", x0, y0, z, x1, y1, z + h)
    # door seams
    if (x1 - x0) > (y1 - y0):
        n = max(2, int((x1 - x0) / 0.5));
        for i in range(1, n):
            xx = x0 + (x1 - x0) * i / n
            box(group, "Wood_Dark", xx - 0.006, y0 - 0.003, z + 0.05, xx + 0.006, y1 + 0.003, z + h - 0.05)
    else:
        n = max(2, int((y1 - y0) / 0.5))
        for i in range(1, n):
            yy = y0 + (y1 - y0) * i / n
            box(group, "Wood_Dark", x0 - 0.003, yy - 0.006, z + 0.05, x1 + 0.003, yy + 0.006, z + h - 0.05)

z1f, z2f = GF_FFL, SLAB_T
# ---- ground: living room (ห้องรับแขก)
g = G_(F1, "ห้องรับแขก")
box(g, "Rug", 8.9, 0.55, z1f, 10.9, 2.55, z1f + 0.01)
sofa(g, 10.35, 0.40, 11.20, 2.70, z1f, "x1")
sofa(g, 9.20, 0.30, 10.35, 0.95, z1f, "y0")                      # L-return
table(g, 9.35, 1.20, 10.0, 2.15, z1f, h=0.40, top="Wood_Dark")
cabinet(g, 8.10, 0.90, 8.50, 2.50, z1f, 0.45, "Wood_Dark")
tv(g, "y", 8.09, 1.0, 2.40, z1f + 0.95, z1f + 1.75, 1)
plant(g, 8.35, 2.80, z1f); plant(g, 11.05, 0.20, z1f, 1.4)
# ---- dining (ห้องรับประทานอาหาร)
g = G_(F1, "ห้องรับประทานอาหาร")
table(g, 6.55, 3.85, 7.45, 5.45, z1f)
for cy_ in (4.15, 4.65, 5.15):
    chair(g, 6.30, cy_, z1f, "x+"); chair(g, 7.70, cy_, z1f, "x-")
cabinet(g, 6.10, 5.75, 6.75, 6.12, z1f, 0.85, "Wood_Dark", "Counter_Top")         # sideboard
# ---- multipurpose (ห้องอเนกประสงค์)
g = G_(F1, "ห้องอเนกประสงค์")
box(g, "Rug", 9.4, 3.7, z1f, 10.9, 5.2, z1f + 0.01)
sofa(g, 9.6, 3.9, 10.4, 4.7, z1f, "x1"); sofa(g, 9.6, 4.75, 10.4, 5.55, z1f, "x1")
table(g, 8.9, 4.3, 9.4, 5.0, z1f, h=0.45, top="Wood_Dark")
cabinet(g, 10.95, 5.35, 11.28, 6.10, z1f, 1.8, "Wood_Light")
plant(g, 8.35, 5.95, z1f, 1.3)
# ---- walk-in closet (เดิม: ห้องครัว)
g = G_(F1, "Walk-in Closet (เดิมห้องครัว)")
wardrobe(g, 3.00, 6.10, 5.85, 6.68, z1f)                     # back wall
wardrobe(g, 3.00, 4.78, 5.20, 5.30, z1f)                     # against bath-3 wall
wardrobe(g, 5.30, 6.10, 5.88, 4.80 + 0.0, z1f) if False else None
cabinet(g, 3.80, 5.55, 4.90, 5.95, z1f, 0.85, "Wood_Dark", "Counter_Top")    # island dresser
box(g, "Metal_Steel", 5.86, 4.82, z1f + 0.3, 5.89, 5.0, z1f + 2.0)           # full-length mirror
chair(g, 5.4, 5.5, z1f, "x-", "Fabric_Beige")
# ---- bath-3 (ห้องน้ำ 3)
g = G_(F1, "ห้องน้ำ-3")
toilet(g, 4.26, 3.10, 0.56, "y0")
basin(g, 4.85, 3.08, 5.45, 3.55, 0.56)
shower(g, 3.0, 3.08, 3.75, 4.62, 0.56, "x", 3.75)
# ---- storage under stair
g = G_(F1, "ห้องเก็บของใต้บันได")
for zz in (0.9, 1.4, 1.9):
    box(g, "Wood_Light", 7.65, 1.15, zz, 7.98, 3.05, zz + 0.03)
# ---- carport: car + EV charger
g = G_(F1, "โรงจอดรถ-รถยนต์")
cx0, cy0 = 3.15, -1.55
box(g, "Car_Paint", cx0, cy0 + 0.05, 0.35 + CAR_FFL - 0.30, cx0 + 1.8, cy0 + 4.55, 0.95 + CAR_FFL - 0.30)
box(g, "Glass", cx0 + 0.12, cy0 + 1.25, 0.95, cx0 + 1.68, cy0 + 3.6, 1.45)
box(g, "Car_Paint", cx0 + 0.15, cy0 + 1.45, 1.40, cx0 + 1.65, cy0 + 3.40, 1.48)
for (wx, wy) in ((cx0 - 0.02, cy0 + 0.85), (cx0 + 1.62, cy0 + 0.85), (cx0 - 0.02, cy0 + 3.65), (cx0 + 1.62, cy0 + 3.65)):
    tube(g, "Tyre_Black", [(wx, wy, 0.33 + 0.02), (wx + 0.20, wy, 0.33 + 0.02)], r=0.33, n=14)
box(G_(EL, "EV Charger"), "Panel_Grey", 4.30, 2.93, 1.0, 4.62, 2.98, 1.45)
# ---- terrace
g = G_(F1, "เฉลียงหน้าบ้าน")
chair(g, 9.6, -0.6, TER_FFL, "x+", "Wood_Dark"); chair(g, 10.6, -0.6, TER_FFL, "x-", "Wood_Dark")
table(g, 9.95, -0.85, 10.25, -0.35, TER_FFL, h=0.5, top="Wood_Dark")
plant(g, 6.45, -0.9, TER_FFL, 1.2)

# ---- extension: elderly bedroom (ห้องนอนผู้สูงอายุ) in carport room
g = G_(FX, "ห้องนอนผู้สูงอายุ-เฟอร์นิเจอร์")
bed(g, 0.35, 4.55, 1.55, 6.62, "y1", RFL)                       # 3.5-ft bed, low height
cabinet(g, 1.62, 6.20, 2.05, 6.62, RFL, 0.55, "Wood_Light")      # bedside
cabinet(g, 0.15, 3.40, 0.55, 4.40, RFL, 0.75, "Wood_Light")      # low cabinet
chair(g, 2.30, 3.85, RFL, "y+", "Fabric_Beige")                  # armchair
box(g, "Fabric_Beige", 2.08, 3.63, RFL + 0.47, 2.12, 4.07, RFL + 0.70); box(g, "Fabric_Beige", 2.48, 3.63, RFL + 0.47, 2.52, 4.07, RFL + 0.70)
for (gx0, gy0, gx1, gy1) in ((2.75, 3.45, 2.79, 4.95), (1.60, 6.62, 2.70, 6.66)):   # grab rails along path to closet/bath
    box(g, "Grab_Bar", gx0, gy0, RFL + 0.85, gx1, gy1, RFL + 0.89)
box(g, "Rug", 0.6, 3.6, RFL, 1.9, 4.4, RFL + 0.01)
# ---- extension: rear kitchen (bay 3) – kitchen relocated here
g = G_(FX, "ครัวหลังบ้าน-เฟอร์นิเจอร์")
cabinet(g, 7.00, 7.82, 11.25, 8.42, 0.40, 0.85, "Cabinet_White", "Counter_Top")   # base run along back wall
box(g, "Metal_Steel", 8.10, 7.92, 1.26, 8.80, 8.32, 1.30)                     # sink
box(g, "TV_Black", 9.60, 7.92, 1.26, 10.30, 8.32, 1.28)                       # hob
box(g, "Metal_Steel", 9.65, 8.05, 2.00, 10.25, 8.42, 2.40)                    # hood
cabinet(g, 7.00, 8.08, 9.40, 8.42, 2.00, 0.70, "Cabinet_White")              # wall cabinets
box(g, "Metal_Steel", 6.90, 6.30, 0.40, 7.60, 6.95, 2.20)                     # fridge
table(g, 8.6, 6.6, 9.8, 7.3, 0.40, h=0.9, top="Counter_Top", leg="Cabinet_White")   # breakfast bar
# ---- extension: rear room (bay 2) – pantry / laundry room
g = G_(FX, "ห้องเตรียม-ซักรีด-เฟอร์นิเจอร์")
for zz in (0.9, 1.4, 1.9):
    box(g, "Wood_Light", 3.0, 8.05, zz, 6.7, 8.42, zz + 0.03)
table(g, 4.2, 7.1, 5.6, 7.6, 0.40, h=0.85, top="Wood_Light")
# ---- laundry yard (bay 1)
g = G_(FX, "ลานซักล้าง-เครื่องซักผ้า")
box(g, "Ceramic_White", 1.95, 6.95, CAR_FFL, 2.55, 7.55, CAR_FFL + 0.85)
box(g, "Ceramic_White", 1.30, 6.95, CAR_FFL, 1.90, 7.55, CAR_FFL + 0.85)
box(g, "Metal_Steel", 0.95, 8.05, CAR_FFL, 2.65, 8.40, CAR_FFL + 0.85)        # wash tub counter

# ---- upper: bedroom 1 (master)
g = G_(F2, "ห้องนอน-1")
bed(g, 9.25, 0.95, 11.25, 2.75, "x1", z2f)
cabinet(g, 10.75, 0.45, 11.25, 0.90, z2f, 0.5, "Wood_Dark"); cabinet(g, 10.75, 2.80, 11.25, 3.25, z2f, 0.5, "Wood_Dark")
box(g, "Rug", 8.6, 0.6, z2f, 9.25, 3.1, z2f + 0.01)
cabinet(g, 8.10, 1.0, 8.50, 2.6, z2f, 0.5, "Wood_Dark")
tv(g, "y", 8.09, 1.1, 2.5, z2f + 0.95, z2f + 1.75, 1)
g = G_(F2, "ห้องแต่งตัว")
wardrobe(g, 8.10, 4.28, 8.70, 6.12, z2f)
wardrobe(g, 8.75, 5.55, 9.52, 6.12, z2f)
cabinet(g, 9.0, 3.9, 9.5, 4.6, z2f, 0.75, "Wood_Dark", "Counter_Top")
g = G_(F2, "ห้องน้ำ-1")
toilet(g, 10.80, 3.62, z2f - 0.04, "y0")
basin(g, 10.78, 4.55, 11.28, 5.25, z2f - 0.04)
shower(g, 9.66, 5.35, 11.28, 6.13, z2f - 0.04, "y", 5.35)
# ---- bedroom 2
g = G_(F2, "ห้องนอน-2")
bed(g, 3.02, 0.10, 5.02, 1.75, "x0", z2f)
cabinet(g, 3.02, -0.40, 3.45, -0.02, z2f, 0.5, "Wood_Dark")
wardrobe(g, 3.02, 2.48, 4.90, 3.05, z2f)
plant(g, 5.55, -0.45, z2f, 1.2)
# ---- bedroom 3
g = G_(F2, "ห้องนอน-3")
bed(g, 3.55, 3.22, 5.15, 5.22, "y0", z2f)
wardrobe(g, 3.02, 5.35, 3.60, 6.65, z2f)
table(g, 3.80, 6.10, 5.10, 6.65, z2f, top="Wood_Light")
chair(g, 4.45, 5.80, z2f, "y+", "Fabric_Grey")
# ---- bath-2
g = G_(F2, "ห้องน้ำ-2")
toilet(g, 6.42, 4.26, z2f - 0.04, "y0")
basin(g, 7.15, 5.65, 7.95, 6.13, z2f - 0.04)
shower(g, 5.97, 5.10, 7.00, 6.13, z2f - 0.04, "y", 5.10)
# ---- hall + balcony
g = G_(F2, "โถงบันได-ระเบียง")
cabinet(g, 6.2, 3.95, 7.0, 4.13, z2f, 0.8, "Wood_Dark"); plant(g, 7.7, 3.85, z2f, 1.0)
chair(g, 9.2, -0.6, SLAB_T, "x+", "Wood_Dark"); chair(g, 10.2, -0.6, SLAB_T, "x-", "Wood_Dark")
table(g, 9.55, -0.85, 9.85, -0.35, SLAB_T, h=0.5, top="Wood_Dark")

# ================================================================ 3. ELECTRICAL (E-01 .. E-05): service, LP, 13 circuits, switches, outlets
MATS.update({
    "Wire_Light": (0.98, 0.80, 0.10, 1.0), "Wire_Outlet": (0.86, 0.22, 0.18, 1.0), "Wire_AC": (0.20, 0.48, 0.92, 1.0),
    "Wire_Special": (0.62, 0.32, 0.82, 1.0), "Wire_Outdoor": (0.10, 0.66, 0.56, 1.0),
    "Switch_Plate": (0.97, 0.97, 0.96, 1.0), "Lamp_Housing": (0.93, 0.93, 0.92, 1.0),
})
e = lambda n: G_(EL, n)
# meter pole outside front-left lot corner (E-02: J / SB at lot edge), service drop (E-01 overhead), U/G CV in HDPE
PX, PY = -0.55, -4.75
cylinder(e("เสาไฟฟ้า-มิเตอร์"), "Manhole", PX, PY, 0.14, 0, 8.5, n=12)
box(e("เสาไฟฟ้า-มิเตอร์"), "Panel_Grey", PX - 0.18, PY + 0.14, 1.4, PX + 0.18, PY + 0.32, 1.95)     # kWh meter box
box(e("เสาไฟฟ้า-มิเตอร์"), "Panel_Grey", PX + 0.25, PY + 0.14, 1.4, PX + 0.55, PY + 0.30, 1.8)      # SB (main switch box)
box(e("เสาไฟฟ้า-มิเตอร์"), "Manhole", PX - 0.8, PY - 0.05, 7.6, PX + 0.8, PY + 0.05, 7.7)          # cross arm
tube(e("สายไฟเมนใต้ดิน CV in HDPE"), "Conduit_Power",
     [(PX, PY + 0.25, 1.4), (PX, PY + 0.25, -0.45), (0.05, PY + 0.25, -0.45), (0.05, -0.1, -0.45),
      (5.80, 0.30, -0.45), (5.80, 0.30, 1.40)], r=0.035)
box(e("ตู้ LP (ตู้ไฟหลัก) ชานพักบันได"), "Panel_Grey", 5.96, 0.20, 1.35, 6.06, 0.75, 1.95)
tube(e("สายเมนอากาศ IEC01 (Overhead)"), "Cable_Black", sag((PX, PY, 7.5), (2.84, -0.82, 3.30), 0.7), r=0.008)
cylinder(e("หลักดิน Ground Rod"), "Metal_Steel", 12.55, 6.48, 0.02, -2.4, 0.15, n=8)
box(e("หลักดิน Ground Rod"), "Manhole", 12.40, 6.33, 0.0, 12.70, 6.63, 0.05)
tube(e("หลักดิน Ground Rod"), "Cable_Black", [(12.55, 6.48, -0.2), (11.45, 6.1, -0.2), (11.45, 6.1, 0.8)], r=0.006)

ZC1, ZC2 = CEIL1 + 0.05, CEIL2 + 0.05     # ceiling voids where circuits run (ground / upper)
LPX = 6.08
GFz, UFz = GF_FFL, SLAB_T
def lane(k, upper=False):
    """Home run of circuit k: out of the LP top, up the wall to the ceiling void (through the slab for upper floor)."""
    y, z = 0.24 + 0.04 * k, (ZC2 if upper else ZC1)
    return [(LPX, y, 1.95), (LPX, y, z), (LPX + 0.10 + 0.03 * k, y, z)]
def circuit(name, mat, k, targets, upper=False, r=0.011):
    """Manhattan routing in the ceiling void from the circuit trunk to each target, then a drop to the device."""
    g = e(name); h = lane(k, upper); tube(g, mat, h, r=r * 1.3, n=8)
    tx0, ty0, z = h[-1]
    for (tx, ty, tz) in targets:
        tube(g, mat, [(tx0, ty0, z), (tx0, ty, z), (tx, ty, z), (tx, ty, tz)], r=r, n=8)
def plate(group, x, y, z, axis, w=0.08, hgt=0.12, mat="Switch_Plate"):
    if axis == "x": box(group, mat, x - w / 2, y - 0.008, z - hgt / 2, x + w / 2, y + 0.008, z + hgt / 2)
    else:           box(group, mat, x - 0.008, y - w / 2, z - hgt / 2, x + 0.008, y + w / 2, z + hgt / 2)

# ---- lamp positions per room (also used by layer 13)
LAMPS_G = {
    "ดวงโคม Walk-in Closet": [(3.66, 5.64, CEIL1), (4.42, 5.64, CEIL1), (5.18, 5.64, CEIL1)],
    "ดวงโคม ห้องรับประทานอาหาร": [(6.84, 4.67, CEIL1)],
    "ดวงโคม ห้องอเนกประสงค์": [(8.61, 4.67, CEIL1), (10.40, 4.67, CEIL1)],
    "ดวงโคม ห้องรับแขก": [(8.61, 2.80, CEIL1), (10.40, 2.80, CEIL1), (8.61, 0.95, CEIL1), (10.40, 0.95, CEIL1)],
    "ดวงโคม โรงจอดรถ": [(1.66, 1.54, CEIL1), (4.40, 1.54, CEIL1)],
    "ดวงโคม ห้องน้ำ-3": [(3.90, 3.90, CEIL1)],
    "ดวงโคม ห้องเก็บของใต้บันได": [(7.50, 2.10, 2.30)],
}
LAMPS_U = {
    "ดวงโคม ห้องนอน-1 (ชั้นบน)": [(8.99, 2.70, CEIL2), (10.51, 2.70, CEIL2), (8.99, 0.95, CEIL2), (10.51, 0.95, CEIL2)],
    "ดวงโคม ห้องนอน-2 (ชั้นบน)": [(4.40, 2.30, CEIL2), (4.40, 0.80, CEIL2)],
    "ดวงโคม ห้องนอน-3 (ชั้นบน)": [(4.40, 5.66, CEIL2), (4.40, 4.15, CEIL2)],
    "ดวงโคม ห้องน้ำ-1 (ชั้นบน)": [(10.55, 5.50, CEIL2)],
    "ดวงโคม ห้องน้ำ-2 (ชั้นบน)": [(6.90, 5.20, CEIL2)],
    "ดวงโคม ห้องแต่งตัว (ชั้นบน)": [(9.03, 5.90, CEIL2)],
    "ดวงโคม โถงบันได (ชั้นบน)": [(7.31, 3.56, CEIL2)],
}
LAMPS_X = {
    "ดวงโคม ห้องนอนผู้สูงอายุ": [(1.45, 5.0, CEIL1)],
    "ดวงโคม ครัวหลังบ้าน": [(8.4, 7.3, 2.86), (10.2, 7.3, 2.86)],
    "ดวงโคม ห้องเตรียม-ซักรีด": [(4.8, 7.6, 2.86)],
    "ดวงโคม ลานซักล้าง": [(1.2, 7.6, 2.80)],
}
flat = lambda d: [p for v in d.values() for p in v]

# ---- C1/C2 lighting + switches
SW_G = [(8.09, 2.95, GFz + 1.2, "y"), (6.01, 3.40, GFz + 1.2, "y"), (5.89, 4.90, GFz + 1.2, "y"), (6.01, 4.15, GFz + 1.2, "y"),
        (7.00, 3.18, GFz + 1.2, "x"), (5.60, 2.89, CAR_FFL + 1.2, "x")]
SW_U = [(8.09, 3.15, UFz + 1.2, "y"), (5.82, 1.95, UFz + 1.2, "y"), (5.82, 4.05, UFz + 1.2, "y"), (6.50, 4.14, UFz + 1.2, "x"),
        (9.53, 4.45, UFz + 1.2, "y"), (6.02, 3.00, UFz + 1.2, "y"), (8.40, 0.08, UFz + 1.2, "x")]
circuit("วงจร C1 แสงสว่าง ชั้นล่าง", "Wire_Light", 0, flat(LAMPS_G) + [(5.98, 1.07, 3.10)] + [(x, y, z + 0.06) for x, y, z, _ in SW_G])
circuit("วงจร C2 แสงสว่าง ชั้นบน", "Wire_Light", 1, flat(LAMPS_U) + [(x, y, z + 0.06) for x, y, z, _ in SW_U], upper=True)
for x, y, z, ax in SW_G: plate(e("สวิตช์ไฟ ชั้นล่าง"), x, y, z, ax)
for x, y, z, ax in SW_U: plate(e("สวิตช์ไฟ ชั้นบน"), x, y, z, ax)
# ---- C3/C4 general outlets
OUT_G = [(8.09, 0.60, "y"), (11.25, 1.50, "y"), (8.09, 2.20, "y"), (6.01, 5.90, "y"), (11.25, 4.50, "y"), (10.00, 6.10, "x"), (3.01, 5.50, "y")]
OUT_U = [(11.25, 1.00, "y"), (8.09, 1.80, "y"), (11.25, 2.90, "y"), (2.99, -0.10, "y"), (2.99, 1.85, "y"), (3.45, 3.18, "x"), (5.25, 3.18, "x"), (4.45, 6.67, "x")]
circuit("วงจร C3 เต้ารับ ชั้นล่าง", "Wire_Outlet", 2, [(x, y, GFz + 0.36) for x, y, _ in OUT_G])
circuit("วงจร C4 เต้ารับ ชั้นบน", "Wire_Outlet", 3, [(x, y, UFz + 0.36) for x, y, _ in OUT_U], upper=True)
for x, y, ax in OUT_G: plate(e("เต้ารับ ชั้นล่าง"), x, y, GFz + 0.3, ax, w=0.12, hgt=0.08)
for x, y, ax in OUT_U: plate(e("เต้ารับ ชั้นบน"), x, y, UFz + 0.3, ax, w=0.12, hgt=0.08)
# ---- C5..C8 air-conditioners (one breaker each, home run to the FCU)
circuit("วงจร C5 แอร์ ห้องอเนกประสงค์", "Wire_AC", 4, [(9.75, 6.00, CEIL1 - 0.10)])
circuit("วงจร C6 แอร์ ห้องนอน-1 (ชั้นบน)", "Wire_AC", 5, [(9.75, 0.20, CEIL2 - 0.10)], upper=True)
circuit("วงจร C7 แอร์ ห้องนอน-2 (ชั้นบน)", "Wire_AC", 6, [(4.25, -0.55, CEIL2 - 0.10)], upper=True)
circuit("วงจร C8 แอร์ ห้องนอน-3 (ชั้นบน)", "Wire_AC", 7, [(4.45, 6.55, CEIL2 - 0.10)], upper=True)
# ---- C9 water heaters (3 bathrooms)
HT = [(3.03, 3.85, GFz + 1.6, "y", False), (10.50, 6.11, UFz + 1.6, "x", True), (5.99, 5.60, UFz + 1.6, "y", True)]
circuit("วงจร C9 เครื่องทำน้ำอุ่น", "Wire_Special", 8, [(x, y, z + 0.2) for x, y, z, _, u in HT if not u])
circuit("วงจร C9 เครื่องทำน้ำอุ่น", "Wire_Special", 8, [(x, y, z + 0.2) for x, y, z, _, u in HT if u], upper=True)
for x, y, z, ax, _ in HT: plate(e("เครื่องทำน้ำอุ่น"), x, y, z, ax, w=0.22, hgt=0.36, mat="AC_White")
# ---- C10 pump + washing machine (laundry yard)
g = e("วงจร C10 ปั๊มน้ำ-เครื่องซักผ้า"); h = lane(9); tube(g, "Wire_Special", h, r=0.014, n=8)
tube(g, "Wire_Special", [h[-1], (h[-1][0], 6.60, ZC1), (2.69, 6.60, ZC1), (2.69, 6.90, 2.80), (2.69, 6.97, 1.32)], r=0.011, n=8)
tube(g, "Wire_Special", [(2.69, 6.90, 2.80), (0.11, 6.90, 2.80), (0.11, 6.97, 1.32)], r=0.011, n=8)
for (ox, oy, oz) in ((0.11, 6.97, 1.2), (2.69, 6.97, 1.2), (-0.1, -4.25, 1.0)):
    box(e("เต้ารับพิเศษ (ปั๊มน้ำ/เครื่องซักผ้า/ประตูรีโมท)"), "Panel_Grey", ox - 0.06, oy - 0.04, oz, ox + 0.06, oy + 0.04, oz + 0.12)
# ---- C11 EV charger
g = e("วงจร C11 EV Charger"); h = lane(10); tube(g, "Wire_Special", h, r=0.016, n=8)
tube(g, "Wire_Special", [h[-1], (h[-1][0], 2.85, ZC1), (4.46, 2.85, ZC1), (4.46, 2.90, 1.45)], r=0.014, n=8)
# ---- C12 extension: elderly bedroom, rear kitchen, pantry, laundry yard
g = e("วงจร C12 ส่วนต่อเติม"); h = lane(11); tube(g, "Wire_Light", h, r=0.014, n=8); x12 = h[-1][0]
tube(g, "Wire_Light", [h[-1], (x12, 4.40, ZC1), (1.45, 4.40, ZC1), (1.45, 5.00, ZC1), (1.45, 5.00, CEIL1)], r=0.011, n=8)
tube(g, "Wire_Light", [(1.45, 4.40, ZC1), (2.82, 4.40, ZC1), (2.82, 4.90, ZC1), (2.82, 4.90, RFL + 1.26)], r=0.011, n=8)       # switch
tube(g, "Wire_Light", [(2.77, 4.40, ZC1), (2.77, 4.27, RFL + 0.40)], r=0.011, n=8)                                          # night light
tube(g, "Wire_Outlet", [(1.45, 4.40, ZC1), (1.75, 4.40, ZC1), (1.75, 6.62, ZC1), (1.75, 6.62, RFL + 0.36)], r=0.011, n=8)
tube(g, "Wire_Outlet", [(0.6, 4.40, ZC1), (0.13, 4.40, ZC1), (0.13, 3.90, ZC1), (0.13, 3.90, RFL + 0.36)], r=0.011, n=8)
tube(g, "Wire_Light", [h[-1], (x12, 5.98, ZC1), (8.4, 5.98, ZC1), (8.4, 6.35, 2.86), (8.4, 7.3, 2.86)], r=0.011, n=8)
tube(g, "Wire_Light", [(8.4, 6.35, 2.86), (10.2, 6.35, 2.86), (10.2, 7.3, 2.86)], r=0.011, n=8)
tube(g, "Wire_Outlet", [(8.4, 6.35, 2.86), (7.6, 6.35, 2.86), (7.6, 8.36, 2.86), (7.6, 8.36, 1.35)], r=0.011, n=8)
tube(g, "Wire_Outlet", [(10.2, 6.35, 2.86), (10.8, 6.35, 2.86), (10.8, 8.36, 2.86), (10.8, 8.36, 1.35)], r=0.011, n=8)
tube(g, "Wire_Light", [h[-1], (x12, 6.55, ZC1), (4.8, 6.55, ZC1), (4.8, 6.90, 2.86), (4.8, 7.6, 2.86)], r=0.011, n=8)
tube(g, "Wire_Light", [(4.8, 6.90, 2.86), (1.2, 6.90, 2.86), (1.2, 7.6, 2.80)], r=0.011, n=8)
plate(e("สวิตช์ไฟ ส่วนต่อเติม"), 2.82, 4.90, RFL + 1.2, "y")
for x, y, z, ax in ((1.75, 6.62, RFL + 0.3, "x"), (0.13, 3.90, RFL + 0.3, "y"), (7.6, 8.36, 1.29, "x"), (10.8, 8.36, 1.29, "x")):
    plate(e("เต้ารับ ส่วนต่อเติม"), x, y, z, ax, w=0.12, hgt=0.08)
# ---- C13 outdoor lighting: terrace, balcony, gate lantern (underground to the mailbox pillar)
g = e("วงจร C13 ไฟภายนอก"); h = lane(12); tube(g, "Wire_Outdoor", h, r=0.014, n=8); x13 = h[-1][0]
tube(g, "Wire_Outdoor", [h[-1], (x13, -0.30, ZC1), (9.6, -0.30, ZC1), (9.6, -0.30, SLAB_B)], r=0.011, n=8)
hu = lane(12, upper=True); tube(g, "Wire_Outdoor", hu + [(hu[-1][0], -0.02, ZC2), (8.27, -0.02, ZC2), (8.27, -0.02, 5.45)], r=0.011, n=8)
tube(g, "Wire_Outdoor", [(LPX, 0.72, 1.35), (LPX, 0.72, -0.40), (6.75, 0.72, -0.40), (6.75, -4.32, -0.40), (6.75, -4.32, 1.40)], r=0.014, n=8)

# ================================================================ 13. LAMPS (ดวงโคม-หลอดไฟ) – one object per room, separate from wiring
LM = "13 ดวงโคม-หลอดไฟ"
def downlight(group, x, y, zc):
    cylinder(group, "Lamp_Housing", x, y, 0.085, zc - 0.014, zc, n=16)
    cylinder(group, "Light_Fixture", x, y, 0.064, zc - 0.019, zc - 0.014, n=16)
for d in (LAMPS_G, LAMPS_U, LAMPS_X):
    for name, pts in d.items():
        for (x, y, z) in pts: downlight(G_(LM, name), x, y, z)
g = G_(LM, "โคมไฟห้อย โต๊ะอาหาร")
tube(g, "Cable_Black", [(7.0, 4.65, CEIL1 - 0.62), (7.0, 4.65, CEIL1)], r=0.005, n=6)
cylinder(g, "Wood_Dark", 7.0, 4.65, 0.22, CEIL1 - 0.78, CEIL1 - 0.62, n=24)
cylinder(g, "Light_Fixture", 7.0, 4.65, 0.17, CEIL1 - 0.80, CEIL1 - 0.78, n=24)
g = G_(LM, "ดวงโคม ห้องนอนผู้สูงอายุ")
box(g, "Lamp_Housing", 2.76, 4.18, RFL + 0.30, 2.80, 4.36, RFL + 0.40)                                     # night light (path to door)
box(g, "Light_Fixture", 2.755, 4.20, RFL + 0.32, 2.76, 4.34, RFL + 0.38)
g = G_(LM, "ดวงโคม บันได")
box(g, "Lamp_Housing", 5.96, 1.00, 2.90, 6.00, 1.15, 3.10); box(g, "Light_Fixture", 6.00, 1.02, 2.92, 6.01, 1.13, 3.08)
g = G_(LM, "ไฟภายนอก เฉลียง")
downlight(g, 9.6, -0.30, SLAB_B)
g = G_(LM, "ไฟภายนอก ระเบียง (ชั้นบน)")
box(g, "Lamp_Housing", 8.20, -0.14, 5.20, 8.34, -0.08, 5.45); box(g, "Light_Fixture", 8.22, -0.15, 5.23, 8.32, -0.14, 5.42)
g = G_(LM, "ไฟภายนอก ประตูรั้ว")
box(g, "Lamp_Housing", 6.65, -4.43, 1.40, 6.85, -4.23, 1.43)
box(g, "Light_Fixture", 6.68, -4.40, 1.43, 6.82, -4.26, 1.60)
box(g, "Rail_Black", 6.63, -4.45, 1.60, 6.87, -4.21, 1.63)

# ================================================================ 4. TELECOM (E-01, E-04, E-05)
t = lambda n: G_(TC, n)
tube(t("สาย Drop Wire Optic"), "Conduit_Telecom", sag((PX, PY, 6.6), (2.70, -0.82, 3.20), 0.8), r=0.006)
box(t("ตู้ TC / MATV BOX"), "Panel_Grey", 8.09, 1.80, 0.90, 8.14, 2.15, 1.25)
box(t("ตู้ TC / MATV BOX"), "Panel_Grey", 8.09, 1.55, SLAB_T + 0.3, 8.14, 1.75, SLAB_T + 0.45)   # bed-1 RG6/CAT6
box(t("ตู้ TC / MATV BOX"), "Panel_Grey", 5.83, 2.95, SLAB_T + 0.3, 5.86, 3.10, SLAB_T + 0.45)
tube(t("ท่อสาย RG6/CAT6"), "Conduit_Telecom", [(2.84, -0.70, 3.30), (2.95, 0.4, 3.30), (8.10, 1.95, 3.30), (8.10, 1.95, 1.25)], r=0.012)

# ================================================================ 5. WATER SUPPLY (SN-01, SN-02)
w = lambda n: G_(WS, n)
box(w("มาตรวัดน้ำ Water Meter"), "Panel_Grey", -0.95, -4.65, 0.0, -0.65, -4.35, 0.25)
# pump next to tank (tank modelled in laundry yard)
box(w("ปั๊มน้ำ"), "Pipe_Supply", 0.95, 7.15, CAR_FFL, 1.35, 7.45, CAR_FFL + 0.40)
SUP = [(-0.80, -4.50, -0.35), (-0.80, 7.60, -0.35), (-0.80, 7.60, 0.6), (-0.15, 7.85, 0.6)]   # city main -> tank
tube(w("ท่อประปาเมน"), "Pipe_Supply", SUP, r=0.02)
tube(w("ท่อประปาจ่ายในบ้าน"), "Pipe_Supply",
     [(1.15, 7.30, 0.70), (1.15, 6.88, 0.70), (2.69, 6.88, 0.70), (2.69, 6.88, -0.25), (10.74, 6.40, -0.25), (10.74, 6.40, 0.4)], r=0.016)
tube(w("ท่อประปาจ่ายในบ้าน"), "Pipe_Supply", [(2.69, 6.88, -0.25), (2.69, 4.36, -0.25), (4.9, 3.3, -0.25), (4.9, 3.3, 1.0)], r=0.013)   # bath-3
tube(w("ท่อประปาจ่ายในบ้าน"), "Pipe_Supply", [(2.69, 4.36, -0.25), (0.40, 4.36, -0.25), (0.40, -0.10, -0.25), (0.15, -0.10, 0.5)], r=0.013)  # HB carport
tube(w("ท่อประปาจ่ายในบ้าน"), "Pipe_Supply", [(2.69, 6.88, 0.70), (2.69, 8.46, 0.70)], r=0.013)                 # HB back
tube(w("ท่อประปาจ่ายในบ้าน"), "Pipe_Supply", [(10.74, 6.40, -0.25), (11.50, 6.40, -0.25), (11.50, 3.03, -0.25), (11.50, 3.03, 0.6)], r=0.013)  # HB right
tube(w("ท่อประปาจ่ายในบ้าน"), "Pipe_Supply", [(8.0, 6.45, -0.25), (8.45, 8.1, -0.25), (8.45, 8.1, 1.0)], r=0.013)   # kitchen sink (relocated)
tube(w("ท่อประปาขึ้นชั้น 2 (CW Riser)"), "Pipe_Supply", [(10.74, 6.40, 0.4), (10.93, 6.30, 0.4), (10.93, 6.30, SLAB_T + 0.9), (10.95, 5.0, SLAB_T + 0.9)], r=0.016)
tube(w("ท่อประปาขึ้นชั้น 2 (CW Riser)"), "Pipe_Supply", [(5.95, 6.40, -0.25), (5.95, 6.40, SLAB_T + 0.9), (6.5, 6.1, SLAB_T + 0.9)], r=0.016)
for (hx, hy) in ((0.15, -0.10), (2.69, 8.46), (11.50, 3.03)):
    box(w("ก๊อกสนาม HB"), "Metal_Steel", hx - 0.04, hy - 0.04, 0.5, hx + 0.04, hy + 0.04, 0.6)

# ================================================================ 6. DRAINAGE / SEPTIC (SN-03, SN-04)
d = lambda n: G_(DR, n)
cylinder(d("ถังบำบัดน้ำเสีย"), "Septic_Tank", 8.46, 7.92, 0.80, -1.55, -0.05, n=24)
cylinder(d("ถังบำบัดน้ำเสีย"), "Manhole", 8.46, 7.92, 0.25, -0.05, 0.42, n=16)        # access riser to floor
cylinder(d("ถังดักไขมัน GT-1"), "Septic_Tank", 7.09, 7.35, 0.25, -0.65, -0.05, n=16)
cylinder(d("ถังดักไขมัน GT-1"), "Manhole", 7.09, 7.35, 0.12, -0.05, 0.42, n=12)
for (mx, my) in ((-0.72, 8.60), (2.90, 8.60), (6.78, 8.60), (10.27, 8.20), (-0.72, 2.51), (-0.72, -3.77)):
    box(d("บ่อพัก / บ่อดักขยะ"), "Manhole", mx - 0.22, my - 0.22, -0.6, mx + 0.22, my + 0.22, 0.04)
# boundary drain (slope 1:200) back -> left side -> catch basin -> public
tube(d("ท่อระบายน้ำรอบบ้าน (ลงสาธารณะ)"), "Pipe_Waste",
     [(10.27, 8.60, -0.45), (-0.72, 8.60, -0.50), (-0.72, -3.77, -0.56), (-0.72, -4.60, -0.58)], r=0.05)
# soil (S) & waste (W) lines under floor
tube(d("ท่อส้วม (S)"), "Pipe_Soil", [(4.26, 3.30, -0.30), (9.70, 3.70, -0.33), (9.70, 6.40, -0.36), (8.95, 7.55, -0.40)], r=0.05)
tube(d("ท่อส้วม (S)"), "Pipe_Soil", [(11.12, 6.55, SLAB_T), (11.12, 6.55, -0.36), (9.70, 6.40, -0.36)], r=0.05)       # S riser bath-1
tube(d("ท่อส้วม (S)"), "Pipe_Soil", [(6.36, 6.40, SLAB_T), (6.36, 6.40, -0.36), (8.10, 7.55, -0.40)], r=0.05)       # S riser bath-2
tube(d("ท่อน้ำทิ้ง (W)"), "Pipe_Waste", [(5.15, 3.30, -0.25), (8.42, 4.74, -0.28), (8.42, 6.40, -0.30), (8.42, 8.60, -0.45)], r=0.035)
tube(d("ท่อน้ำทิ้ง (W)"), "Pipe_Waste", [(10.95, 6.45, SLAB_T), (10.95, 6.45, -0.30), (8.42, 6.40, -0.30)], r=0.035)  # W riser bath-1
tube(d("ท่อน้ำทิ้ง (W)"), "Pipe_Waste", [(8.45, 8.10, 0.3), (7.30, 7.50, -0.30), (7.09, 7.35, -0.30)], r=0.035)     # kitchen sink -> GT
tube(d("ท่อน้ำทิ้ง (W)"), "Pipe_Waste", [(7.09, 7.35, -0.35), (6.78, 8.60, -0.45)], r=0.035)                        # GT -> drain
tube(d("ท่อน้ำทิ้ง (W)"), "Pipe_Waste", [(2.69, 7.70, -0.25), (2.90, 8.60, -0.45)], r=0.035)                        # washing machine D.
tube(d("ท่อน้ำทิ้ง (W)"), "Pipe_Waste", [(9.30, 7.92, -0.40), (10.27, 8.20, -0.42), (10.27, 8.60, -0.45)], r=0.05)   # septic outlet
tube(d("ท่ออากาศ (V)"), "Pipe_Vent", [(9.10, 8.45, 0.0), (9.10, 8.45, 3.40)], r=0.025)                             # vent from tank
tube(d("ท่ออากาศ (V)"), "Pipe_Vent", [(11.20, 6.62, SLAB_T), (11.20, 6.62, EAVE + 0.4)], r=0.025)
tube(d("ท่อ AC Pipe (น้ำทิ้งแอร์)"), "Pipe_Waste", [(-0.72, -2.40, -0.55), (-0.72, -2.40, 0.10)], r=0.03)
# floor drains
for (fx, fy, fz) in ((3.35, 3.85, 0.57), (10.50, 5.75, SLAB_T - 0.03), (6.45, 5.60, SLAB_T - 0.03), (2.2, 8.1, CAR_FFL)):
    box(d("ตะแกรงน้ำทิ้งพื้น FD"), "Metal_Steel", fx - 0.08, fy - 0.08, fz, fx + 0.08, fy + 0.08, fz + 0.012)

# ================================================================ 7. AIR CONDITIONING (E-06, E-07)
a = lambda n: G_(AC, n)
def fcu(name, x0, y0, x1, y1, z):
    box(a(name), "AC_White", x0, y0, z, x1, y1, z + 0.30)
    box(a(name), "AC_Grey", x0 + 0.05, y0 + 0.01 if y1 - y0 < x1 - x0 else y0 + 0.05, z + 0.02,
        x1 - 0.05, y1 - 0.01 if y1 - y0 < x1 - x0 else y1 - 0.05, z + 0.06)
def cdu(name, x, y, z):
    box(a(name), "AC_Grey", x - 0.40, y - 0.15, z, x + 0.40, y + 0.15, z + 0.55)
    cylinder(a(name), "TV_Black", x - 0.08, y - 0.16, 0.20, z + 0.07, z + 0.48, n=16) if False else \
        box(a(name), "TV_Black", x - 0.30, y - 0.16, z + 0.08, x + 0.10, y - 0.15, z + 0.48)
fcu("FCU-1-1 24,000 BTU (ห้องอเนกประสงค์)", 9.30, 5.88, 10.20, 6.12, CEIL1 - 0.40)
fcu("FCU-2-1 18,000 BTU (ห้องนอน-1)", 9.30, 0.08, 10.20, 0.32, CEIL2 - 0.40)
fcu("FCU-2-2 12,000 BTU (ห้องนอน-2)", 3.80, -0.67, 4.70, -0.43, CEIL2 - 0.40)
fcu("FCU-2-3 12,000 BTU (ห้องนอน-3)", 4.00, 6.43, 4.90, 6.67, CEIL2 - 0.40)
cdu("CDU-1-1 (บนหลังคาส่วนต่อเติม)", 7.60, 7.70, EZ_R)
cdu("CDU-2-3 (บนหลังคาส่วนต่อเติม)", 5.60, 7.70, EZ_R)
cdu("CDU-2-2 (บนกันสาด)", 2.30, 3.10, SLAB_T + 0.02)
box(a("CDU-2-1 (ขาแขวนผนังขวา)"), "Metal_Steel", 11.40, 0.20, 4.10, 11.85, 0.90, 4.15)
cdu("CDU-2-1 (ขาแขวนผนังขวา)", 11.63, 0.55, 4.15) if False else box(a("CDU-2-1 (ขาแขวนผนังขวา)"), "AC_Grey", 11.45, 0.15, 4.15, 11.80, 0.95, 4.70)
RL = "ท่อน้ำยาแอร์ + สายไฟ"
tube(a(RL), "Refrig_Line", [(9.75, 6.10, CEIL1 - 0.25), (9.75, 6.35, CEIL1 - 0.25), (7.6, 6.35, CEIL1 - 0.25), (7.6, 7.55, EZ_R + 0.2)], r=0.03)
tube(a(RL), "Refrig_Line", [(4.45, 6.68, CEIL2 - 0.25), (4.45, 6.85, CEIL2 - 0.25), (5.6, 7.0, EZ_R + 0.6), (5.6, 7.55, EZ_R + 0.2)], r=0.03)
tube(a(RL), "Refrig_Line", [(3.80, -0.55, CEIL2 - 0.25), (2.98, -0.55, CEIL2 - 0.25), (2.85, 2.95, SLAB_T + 0.3)], r=0.03)
tube(a(RL), "Refrig_Line", [(10.20, 0.20, CEIL2 - 0.25), (11.42, 0.30, CEIL2 - 0.25), (11.55, 0.40, 4.70)], r=0.03)

# ================================================================ 8. FRONT YARD / STREET (photos)
s_ = lambda n: G_(ST, n)
box(s_("ถนนหน้าบ้าน"), "Road", -4.0, -9.0, -0.02, 15.5, -4.40, 0.02)
box(s_("ขอบทางเท้า"), "Stepping_Stone", -4.0, -4.62, 0.0, 15.5, -4.40, 0.12)
yy = -4.0
while yy < -1.3:                                                        # stepping stones gate -> terrace
    box(s_("ทางเดินแผ่นหิน"), "Stepping_Stone", 7.45, yy, 0.0, 8.15, yy + 0.30, 0.04)
    yy += 0.48
box(s_("รั้วต้นไม้ (Hedge)"), "Hedge_Green", 8.45, -4.05, 0.0, 14.15, -3.60, 0.95)
box(s_("รั้วต้นไม้ (Hedge)"), "Hedge_Green", -1.05, -4.05, 0.0, -0.98, -3.60, 0.01)
box(s_("รั้วต้นไม้ (Hedge)"), "Hedge_Green", 13.75, -3.60, 0.0, 14.15, 6.0, 0.95)
cylinder(s_("ต้นไม้หน้าบ้าน"), "Tree_Trunk", 12.3, -2.4, 0.15, 0.0, 2.4, n=10)
for (rz, rr, hz) in ((2.2, 1.6, 1.0), (3.0, 1.9, 1.1), (3.9, 1.3, 0.9)):
    cylinder(s_("ต้นไม้หน้าบ้าน"), "Tree_Leaf", 12.3, -2.4, rr, rz, rz + hz, n=14)
box(s_("ตู้จดหมาย"), "Metal_Steel", 6.55, LY0 - 0.20, 0.95, 6.95, LY0 - 0.14, 1.25)
