"""
Caracas - Drone Frame (build123d port of caracas.scad)
======================================================
Run inside VS Code with the OCP CAD Viewer extension to see it,
or run headless: exports caracas_b123d.step / .stl next to this file.
"""

from math import sqrt

from build123d import *

# =============================================================================
# PARAMETERS — everything tunable lives in this block (mirrors caracas.scad)
# =============================================================================

# ---- props & frame ----
prop_size = 110                    # prop radius; 8 inch ≈ 110mm
frame_length = prop_size * 2       # keeps propellers from colliding
frame_width = 100
frame_thickness = 3                # case wall thickness
case_rounding = 25                 # case corner rounding

# ---- support plates (carbon fiber) ----
plate_thickness = 2.5
plate_clearance = 5                # per-side gap from the case shell

# ---- slice heights ----
z_top = 30
z_middle = 45
z_bottom = 30

# ---- arms (carbon rods) ----
arms_inner_diameter = 16           # rod diameter
arms_wall_thickness = 3            # support wall strength
arms_support_length = 30
arms_from_edge = prop_size / 2 - 10

# arm pairs: A+D is one rod (+x), B+C is one rod (-x).
# z is referenced from the "top"/"bottom" outer face.
arm_ad_x = frame_length / 2 - arms_from_edge
arm_bc_x = -(frame_length / 2 - arms_from_edge)

# ---- view ----
show_support_plates = True
explode = 30                       # z gap between slices (0 = assembled)
explode_y = 200                    # slides fit-check plates out in +y

# =============================================================================
# DERIVED VALUES — computed from the parameters above; do not edit directly
# =============================================================================

frame_height = (frame_thickness + z_top + plate_thickness + z_middle
                + plate_thickness + z_bottom + frame_thickness)

def arm_z(ref, off):
    return frame_height / 2 - off if ref == "top" else -frame_height / 2 + off

arm_ad_z = arm_z("top", z_top / 2 + arms_wall_thickness - plate_thickness)
arm_bc_z = arm_z("bottom", z_bottom / 2 + arms_wall_thickness - plate_thickness)

shell_rim_z = frame_height / 2 - case_rounding  # height where shell starts curving in


# =============================================================================
# PARTS
# =============================================================================

def rounded_box(l, w, h, r):
    """BOSL2 cuboid(..., rounding=r): box with all 12 edges filleted."""
    box = Box(l, w, h)
    return fillet(box.edges(), radius=r)


def arm_support():
    """Hollow tube for one arm rod, rims rounded (capped at wall/2 as in BOSL2)."""
    r_out = arms_inner_diameter / 2 + arms_wall_thickness
    r_in = arms_inner_diameter / 2
    # tube axis along Y, center shifted -1/4 length so 3/4 pokes inward
    tube = Pos(0, -arms_support_length / 4, 0) * Rot(90, 0, 0) * (
        Cylinder(radius=r_out, height=arms_support_length)
        - Cylinder(radius=r_in, height=arms_support_length + 2)
    )
    try:
        tube = fillet(tube.edges(), radius=min(2, arms_wall_thickness / 2))
    except Exception:
        pass  # rim rounding is cosmetic; skip if the kernel rejects it
    return tube


def arm_pair(x, z):
    """Two supports holding one continuous rod (front A/B, back D/C)."""
    front = Pos(x, -frame_width / 2 + frame_thickness, z) * arm_support()
    back = Pos(x, frame_width / 2 - frame_thickness, z) * Rot(180, 0, 0) * arm_support()
    return front + back


def body():
    # hollow rounded case: inner rounding shrinks by the wall thickness
    shell = rounded_box(frame_length, frame_width, frame_height, case_rounding) - rounded_box(
        frame_length - frame_thickness * 1.5,
        frame_width - frame_thickness * 1.5,
        frame_height - frame_thickness * 2,
        case_rounding - frame_thickness,
    )

    part = shell + arm_pair(arm_ad_x, arm_ad_z) + arm_pair(arm_bc_x, arm_bc_z)

    # open the walls where the arms will go
    for x, z in ((arm_ad_x, arm_ad_z), (arm_bc_x, arm_bc_z)):
        part -= Pos(x, 0, z) * Rot(90, 0, 0) * Cylinder(
            radius=arms_inner_diameter / 2, height=500
        )
    return part


# ---- support plates (carbon fiber — separate parts) --------------------------

def shell_inset(z):
    """Inward offset of the shell cross-section at height z."""
    az = abs(z)
    if az <= shell_rim_z:
        return 0
    return case_rounding - sqrt(case_rounding**2 - (az - shell_rim_z) ** 2)


def shell_corner(z):
    """Corner radius of the shell cross-section at height z."""
    az = abs(z)
    if az <= shell_rim_z:
        return case_rounding
    return sqrt(case_rounding**2 - (az - shell_rim_z) ** 2)


def support_plate(z):
    """One plate sized to the shell cross-section at height z (its center)."""
    inset = shell_inset(z) + plate_clearance
    corner = max(0, shell_corner(z) - plate_clearance)
    with BuildSketch() as plan:
        rect = Rectangle(frame_length - 2 * inset, frame_width - 2 * inset)
        if corner > 0:
            fillet(rect.vertices(), radius=corner)
    return extrude(plan.sketch, amount=plate_thickness / 2, both=True)


def support_plates():
    z_in = frame_height / 2 - frame_thickness   # inner top/bottom face of the case
    zc_tb = z_in - plate_thickness / 2          # center of the top/bottom plates
    zc_mid = z_middle / 2 + plate_thickness / 2  # center of the middle plates

    return (
        Pos(0, explode_y, zc_tb + explode) * support_plate(zc_tb)
        + Pos(0, explode_y, zc_mid) * support_plate(zc_mid)
        + Pos(0, explode_y, -zc_mid) * support_plate(-zc_mid)
        + Pos(0, explode_y, -zc_tb - explode) * support_plate(-zc_tb)
    )


# =============================================================================
# SLICING — bottom / middle / top, exploded like the OpenSCAD "all" view
# =============================================================================

slice_ranges = [  # (z0, z1) for bottom, middle, top
    (-frame_height / 2, -frame_height / 2 + z_bottom),
    (-z_middle / 2, z_middle / 2),
    (frame_height / 2 - z_top, frame_height / 2),
]

full_body = body()

slices = []
for i, (z0, z1) in enumerate(slice_ranges):
    slab = Pos(0, 0, (z0 + z1) / 2) * Box(frame_length * 2, frame_width * 6, z1 - z0)
    slices.append(Pos(0, 0, (i - 1) * explode) * (full_body & slab))

result = slices[0] + slices[1] + slices[2]
if show_support_plates:
    result += support_plates()

result = Compound(children=[result])  # single compound for show/export

# =============================================================================
# OUTPUT
# =============================================================================

print(f"frame: {frame_length} x {frame_width} x {frame_height} mm")
print(f"bounding box: {result.bounding_box().size}")

export_step(result, "caracas_b123d.step")
export_stl(result, "caracas_b123d.stl")
print("exported caracas_b123d.step / caracas_b123d.stl")

try:
    from ocp_vscode import show

    show(result)
except Exception as e:
    print(f"(viewer not shown: {e})")
