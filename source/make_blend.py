import bpy, bmesh, math, os
HOUSE_DIR = os.environ.get('HOUSE_DIR') or os.path.dirname(os.path.abspath(__file__))
os.environ['HOUSE_DIR'] = HOUSE_DIR
BLEND_OUT = os.environ.get('BLEND_OUT', '/mnt/user-data/outputs/SH2401_house.blend')
GLB_OUT = os.environ.get('GLB_OUT', os.path.join(HOUSE_DIR, 'viewer', 'house.glb'))
RENDER_DIR = os.environ.get('RENDER_DIR', HOUSE_DIR)
src = open(os.path.join(HOUSE_DIR, 'build.py'), encoding='utf-8').read().split('# ================================================================ writers')[0]
exec(src)

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'

# ---------- materials
def mk_mat(name, rgba):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    r, g, bl, a = rgba
    b.inputs["Base Color"].default_value = (r**2.2, g**2.2, bl**2.2, 1)
    b.inputs["Roughness"].default_value = 0.6
    if name == "Glass":
        b.inputs["Transmission Weight"].default_value = 1.0
        b.inputs["Roughness"].default_value = 0.05
        b.inputs["IOR"].default_value = 1.45
    if name == "Rail_Black":
        b.inputs["Metallic"].default_value = 0.6; b.inputs["Roughness"].default_value = 0.4
    if name == "Roof_Tile":
        b.inputs["Roughness"].default_value = 0.8
    if name.startswith("Roof_Tile_R"):
        nt = m.node_tree; N = nt.nodes
        tc = N.new("ShaderNodeTexCoord"); wv = N.new("ShaderNodeTexWave")
        wv.wave_type = 'BANDS'; wv.bands_direction = 'X' if name.endswith("RX") else 'Y'
        wv.inputs["Scale"].default_value = 1.05; wv.inputs["Distortion"].default_value = 0.0
        ns = N.new("ShaderNodeTexNoise"); ns.inputs["Scale"].default_value = 3.0
        mix = N.new("ShaderNodeMix"); mix.data_type = 'RGBA'; mix.inputs[0].default_value = 0.12
        mix.inputs[6].default_value = (r**2.2, g**2.2, bl**2.2, 1); mix.inputs[7].default_value = ((r*0.8)**2.2, (g*0.8)**2.2, (bl*0.8)**2.2, 1)
        nt.links.new(ns.outputs["Fac"], mix.inputs[0])
        nt.links.new(mix.outputs[2], b.inputs["Base Color"])
        bp = N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.6; bp.inputs["Distance"].default_value = 0.04
        nt.links.new(tc.outputs["Object"], wv.inputs["Vector"])
        nt.links.new(wv.outputs["Fac"], bp.inputs["Height"])
        nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
        b.inputs["Roughness"].default_value = 0.55
    m.diffuse_color = (r, g, bl, a)
    return m
mats = {k: mk_mat(k, v) for k, v in MATS.items()}

# ---------- objects (one per group), organised in toggleable collections
LEGACY = {
 "Site": ("12 ภูมิทัศน์-รั้ว-ถนน", "พื้นหญ้า-ลานคอนกรีต"), "Fence": ("12 ภูมิทัศน์-รั้ว-ถนน", "รั้วรอบบ้าน-ประตูรั้ว"),
 "Slabs": ("01 ชั้นล่าง-สถาปัตย์", "พื้น-คาน ชั้นล่าง"), "Ground floor walls": ("01 ชั้นล่าง-สถาปัตย์", "ผนังภายนอก ชั้นล่าง"),
 "Columns": ("01 ชั้นล่าง-สถาปัตย์", "เสา-ครีบผนัง"), "Stair": ("01 ชั้นล่าง-สถาปัตย์", "บันได-ราวบันได"),
 "Upper slab": ("02 ชั้นบน-สถาปัตย์", "พื้นชั้น 2 (มีช่องบันได)"), "Upper floor walls": ("02 ชั้นบน-สถาปัตย์", "ผนังภายนอก ชั้นบน"),
 "Trim": ("02 ชั้นบน-สถาปัตย์", "คิ้วกรอบหน้าต่าง-โคมผนัง"), "Balcony railing": ("02 ชั้นบน-สถาปัตย์", "ราวระเบียง"),
 "Roof": ("03 หลังคา", "โครงหลังคา-เชิงชาย"), "Roof tiles": ("03 หลังคา", "กระเบื้องหลังคา"),
 "Roof ridges": ("03 หลังคา", "ครอบสัน-ตะเข้ราง"), "Gable": ("03 หลังคา", "หน้าจั่ว"),
 "Ext - Carport room": ("04 ส่วนต่อเติม", "ห้องนอนผู้สูงอายุ-ผนัง"), "Ext - Rear room": ("04 ส่วนต่อเติม", "ห้องเตรียม-ซักรีด-ผนัง"),
 "Ext - Rear kitchen": ("04 ส่วนต่อเติม", "ครัวหลังบ้าน-ผนัง"), "Ext - Laundry yard": ("04 ส่วนต่อเติม", "ลานซักล้าง-ระแนง-ถังน้ำ"),
 "Ext - Roof": ("04 ส่วนต่อเติม", "หลังคาส่วนต่อเติม"),
}
root = bpy.data.collections.new("SH2401 House"); scene.collection.children.link(root)
COLL = {}
def coll(name):
    if name not in COLL:
        c = bpy.data.collections.new(name); root.children.link(c); COLL[name] = c
    return COLL[name]
for cname in ["01 ชั้นล่าง-สถาปัตย์", "02 ชั้นบน-สถาปัตย์", "03 หลังคา", "04 ส่วนต่อเติม", "05 ตกแต่งภายใน ชั้นล่าง",
              "06 ตกแต่งภายใน ชั้นบน", "07 ระบบไฟฟ้า", "08 ระบบประปา", "09 ระบบระบายน้ำ-บำบัด", "10 ระบบปรับอากาศ",
              "11 ระบบสื่อสาร-ทีวี", "12 ภูมิทัศน์-รั้ว-ถนน"]:
    coll(cname)
OBJ = {}
for gname, polys in groups.items():
    if "::" in gname: cname, oname = gname.split("::", 1)
    else: cname, oname = LEGACY[gname]
    verts, idx, faces, fmats = [], {}, [], []
    mlist = sorted({m.split("~")[0] for m, _ in polys})
    smooth = []
    for m, p in polys:
        f = []
        for v in p:
            k = tuple(round(c, 5) for c in v)
            if k not in idx: idx[k] = len(verts); verts.append(k)
            f.append(idx[k])
        g = [x for i, x in enumerate(f) if x != f[i-1]]
        if len(g) >= 3 and len(set(g)) == len(g):
            faces.append(g); fmats.append(mlist.index(m.split("~")[0])); smooth.append(m.endswith("~s"))
    full = cname[:2] + "|" + oname
    me = bpy.data.meshes.new(full)
    me.from_pydata(verts, [], faces); me.update()
    for m in mlist: me.materials.append(mats[m])
    BEVEL = (cname[:2] in ("01", "02", "04", "05", "06") or "รั้ว" in oname or "โครงหลังคา" in oname or "หน้าจั่ว" in oname)
    for poly, mi, sm in zip(me.polygons, fmats, smooth): poly.material_index = mi; poly.use_smooth = sm or BEVEL
    bm = bmesh.new(); bm.from_mesh(me)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me); bm.free()
    # box-projected UVs in metres so procedural textures map at real-world scale
    uvl = me.uv_layers.new(name="UVMap")
    for poly in me.polygons:
        nx, ny, nz = (abs(c) for c in poly.normal)
        for li in poly.loop_indices:
            co = me.vertices[me.loops[li].vertex_index].co
            uvl.data[li].uv = (co.x, co.y) if nz >= nx and nz >= ny else ((co.y, co.z) if nx >= ny else (co.x, co.z))
    ob = bpy.data.objects.new(full, me); coll(cname).objects.link(ob)
    if BEVEL:
        bv = ob.modifiers.new("bevel", "BEVEL"); bv.width = 0.012; bv.segments = 2
        bv.limit_method = "ANGLE"; bv.angle_limit = math.radians(35); bv.harden_normals = True
    OBJ[full] = ob
for n in ("Light_Fixture",):
    b = mats[n].node_tree.nodes.get("Principled BSDF")
    b.inputs["Emission Color"].default_value = (1.0, 0.92, 0.75, 1); b.inputs["Emission Strength"].default_value = 3.0

# ---------- light, sky, camera
sun = bpy.data.lights.new("Sun", 'SUN'); sun.energy = 4; sun.angle = math.radians(3)
so = bpy.data.objects.new("Sun", sun); scene.collection.objects.link(so)
so.rotation_euler = (math.radians(50), 0, math.radians(-30))
world = bpy.data.worlds.new("World"); scene.world = world; world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.75, 0.85, 1.0, 1)
world.node_tree.nodes["Background"].inputs[1].default_value = 0.8

def camera(name, loc, target):
    cam = bpy.data.cameras.new(name); cam.lens = 30
    co = bpy.data.objects.new(name, cam); scene.collection.objects.link(co)
    co.location = loc
    import mathutils
    d = mathutils.Vector(target) - mathutils.Vector(loc)
    co.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    return co
c1 = camera("Cam_Front", (-6.5, -17, 6.0), (5.5, 2.5, 3.6))
c2 = camera("Cam_FrontRight", (20, -13, 6.5), (6.5, 2.5, 3.6))
c3 = camera("Cam_Rear", (15, 22, 7.0), (5.5, 3.0, 3.6))
c4 = camera("Cam_Street", (7.5, -13.5, 1.6), (6.8, 2.0, 4.6))
c6 = camera("Cam_RoofClose", (14.5, -6.5, 10.5), (8.0, 1.5, 7.5))
c5 = camera("Cam_Drone", (3.0, -16.0, 17.0), (6.0, 2.5, 2.5))
scene.camera = c1

scene.render.engine = 'CYCLES'
scene.cycles.samples = 32
scene.cycles.use_denoising = True
scene.render.resolution_x, scene.render.resolution_y = 1400, 900
scene.view_settings.view_transform = 'AgX' if 'AgX' in [i.identifier for i in scene.view_settings.bl_rna.properties['view_transform'].enum_items] else 'Filmic'

c7 = camera("Cam_Cutaway_Ground", (-1.5, -8.0, 13.0), (5.4, 3.4, 0.6))
c8 = camera("Cam_Cutaway_Upper", (-1.0, -7.5, 16.0), (6.2, 3.0, 3.8))
c9 = camera("Cam_Utilities", (-8.5, 15.5, 11.0), (5.0, 1.5, 0.0))
for c in (c7, c8): c.data.lens = 21
c9.data.lens = 24
(BLEND_OUT and bpy.ops.wm.save_as_mainfile(filepath=BLEND_OUT))
def show_only(hide_codes=(), hide_names=()):
    for n, ob in OBJ.items():
        code = n[:2]
        ob.hide_render = (code in hide_codes) or any(h in n for h in hide_names)
SHOTS = [
  (c4, "render_street", (), ()),
  (c5, "render_drone", (), ()),
  (c7, "render_cut_ground", ("02", "03", "06", "10"), ("ฝ้าเพดาน", "หลังคาส่วนต่อเติม", "โคมไฟเพดาน ชั้นบน")),
  (c8, "render_cut_upper", ("03",), ("หลังคาส่วนต่อเติม",)),
  (c9, "render_utilities", ("02", "03", "05", "06"), ("พื้นหญ้า", "ฝ้าเพดาน", "หลังคาส่วนต่อเติม", "ผนังภายนอก ชั้นล่าง",
       "ผนังภายใน ชั้นล่าง", "พื้น-คาน", "เฟอร์นิเจอร์", "เครื่องซักผ้า", "ระแนง", "ผนัง", "รถยนต์", "รั้ว", "ต้นไม้", "ถนน", "ขอบทาง", "บันได")),
]
import sys
only = [a for a in sys.argv if a.startswith("SHOT=")]
for c, fn, hc, hn in SHOTS:
    if "NORENDER" in sys.argv: break
    if only and fn not in only[0]: continue
    show_only(hc, hn)
    scene.camera = c
    scene.render.filepath = os.path.join(RENDER_DIR, fn + ".png")
    bpy.ops.render.render(write_still=True)
show_only()
scene.camera = c4
(BLEND_OUT and bpy.ops.wm.save_as_mainfile(filepath=BLEND_OUT))
try:
    bpy.ops.export_scene.gltf(filepath=GLB_OUT, export_format='GLB', export_apply=True,
                              export_lights=False, export_cameras=False)
    print("glb ok")
except Exception as ex:
    print("glb fail", ex)
print("done")
