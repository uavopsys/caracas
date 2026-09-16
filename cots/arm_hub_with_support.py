"""
Arm hub - 28x28x30mm block with D16 rod bore and M3 corner screw holes.
Z is 30mm to match 30mm m/F standoffs. M3 holes are 2.5mm self-tapping
pilots for printed plastic (no brass insert).

The hole grid (+/- size/2 - screw_edge_offset = +/-9.5mm) must match
pattern_hole_offset in plate.py.

Run with the ocp_vscode standalone viewer running (python3.11 -m ocp_vscode),
or headless: exports arm_hub.step / .stl next to this file.
"""

import math
import os
from pathlib import Path

import yaml
from build123d import *

os.chdir(Path(__file__).parent)  # outputs land next to this script

# =============================================================================
# PARAMETERS — from config.yaml (shared with plate.py)
# =============================================================================

with open("config.yaml") as f:
    cfg = yaml.safe_load(f)["arm_hub"]

size = cfg["size"]                  # block edge (X/Y)
size_height = cfg["size_height"]    # block height (Z)
rod_diameter = cfg["rod_diameter"]  # through-bore for the carbon rod (D16)
rod_clearance = cfg["rod_clearance"]  # printing clearance added to rod_diameter
screw_diameter = cfg["screw_diameter"]  # M3 self-tapping pilot (no insert)
hole_grid = cfg["hole_grid"]        # 2x2 screw spacing; plate reads the same

screw_edge_offset = (size - hole_grid) / 2  # hole center distance from each edge
o = hole_grid / 2                           # hole center distance from block center

# ---- T/B orientation markers, engraved into the top and bottom faces ----
mark_depth = 0.6   # engrave depth
mark_size = 10     # letter height (mm)
mark_offset_y = 6  # letter placement along Y

# ---- tube extension on one bore opening ----
# Hollow cylinder with the same opening as the bore, welded onto one side of
# the block, following bore_angle. Outer diameter equals the block height, so
# the tube is flush with the top and bottom faces (wall ends up
# (size_height - bore_diameter) / 2).
tube_stickout = 20 # protrusion past the block, at the furthest point

# ---- bore path ----
# The bore enters from the tube side at bore_angle (deg from X, toward Y),
# runs straight, then at bend_start mm from the block center turns
# -bore_angle so it exits the -X face perpendicular, at bend_exit_y.
# The bend radius is derived so the exit lands exactly on bend_exit_y;
# bend_exit_y=0 centers the exit between the two corner screw posts on that
# face, keeping both at equal strength. bore_angle=0 = straight bore along X.
bore_angle = 0
bend_start = 8   # distance from block center along the bore axis where the turn starts
bend_exit_y = 0  # where the bore centerline exits the -X face

# rod_clearance (config.yaml) is 3D-printing clearance added to the nominal
# rod diameter. The bore's axis is horizontal (lies in XY), so the printer
# builds the top of the circle as an unsupported bridge that sags inward -
# horizontal holes need more clearance than vertical ones (0.2-0.25mm/side
# vs 0.1-0.15mm/side), on top of the usual extrusion-width undersizing.
bore_diameter = rod_diameter + rod_clearance

theta = math.radians(bore_angle)
ct, st = math.cos(theta), math.sin(theta)
a = size / 2  # block half-width
m, n = max(abs(ct), abs(st)), min(abs(ct), abs(st))  # dominant / minor axis components

# tube dimensions (built in PART below)
tube_radius = size_height / 2  # flush with the top and bottom faces
tube_reach = (a + tube_radius * n) / m + tube_stickout

# bore centerline: straight from just past the tube tip to the bend point,
# then an arc turning -bore_angle, then straight out the -X face
ub = Vector(ct, st, 0)                       # bore axis, toward the tube side
travel = -ub                                 # from the tube into the block
start_pt = (tube_reach + 1) * ub
bend_pt = bend_start * ub
bend_radius = (bend_start * st - bend_exit_y) / (1 - ct) if bore_angle != 0 else 0
arc_center = bend_pt + bend_radius * Vector(travel.Y, -travel.X, 0)  # right of travel
exit_arc_pt = arc_center + bend_radius * Vector(0, -1, 0)            # tangent now (-1, 0)
exit_pt = Vector(-a - 2, bend_exit_y, 0)

if bore_angle != 0:
    if bend_radius <= 0:
        print(f"WARNING: bend_radius={bend_radius:.1f} - bend_start too small "
              f"for bend_exit_y={bend_exit_y}; no bend possible")
    if exit_arc_pt.X < -a:
        print(f"WARNING: the bend ends at x={exit_arc_pt.X:.1f}, past the -X face "
              f"({-a}) - increase bend_start or raise bend_exit_y")
    if abs(bend_exit_y) + bore_diameter / 2 > a:
        print(f"WARNING: bore exits at y={bend_exit_y}, the circle needs "
              f"|y| <= {a - bore_diameter / 2:.2f} - it will clip the +/-Y faces")
    post_clear = min(math.hypot(a - o, sy - bend_exit_y) for sy in (-o, o)) \
        - bore_diameter / 2 - screw_diameter / 2
    print(f"bore exits -X face at y={bend_exit_y}, bend R{bend_radius:.1f}mm, "
          f"clearance to corner screw posts: {post_clear:.2f}mm")

# =============================================================================
# PART
# =============================================================================

part = Box(size, size, size_height)

# tube on the +axis side of the bore (outer cylinder only - the bore sweep
# below cuts the opening through it). Starts at the block center (fully
# embedded, so it is completely connected at any bore_angle) and ends
# tube_stickout beyond the last point where the tube's outer circle still
# touches the block - that point sits (a + R*n)/m along the bore axis.
part += Rot(0, 0, bore_angle) * Rot(0, 90, 0) * Pos(0, 0, tube_reach / 2) * Cylinder(
    radius=tube_radius, height=tube_reach)

# bent bore: sweep the bore circle along the centerline
with BuildPart() as bore_bp:
    with BuildLine() as bore_path:
        if bore_angle == 0:
            Line(start_pt, exit_pt)
        else:
            Line(start_pt, bend_pt)
            JernArc(bend_pt, tangent=(travel.X, travel.Y, 0),
                    radius=bend_radius, arc_size=-bore_angle)
            Line(exit_arc_pt, exit_pt)
    with BuildSketch(Plane(origin=start_pt, z_dir=(travel.X, travel.Y, 0))):
        Circle(bore_diameter / 2)
    sweep()
part -= bore_bp.part

# 4 vertical M3 holes near the corners (through top and bottom faces)
for x in (-o, o):
    for y in (-o, o):
        part -= Pos(x, y, 0) * Cylinder(radius=screw_diameter / 2, height=size + 6)


def engrave_letter(letter, top):
    """Cut `letter` into the top or bottom face, legible when viewed from
    that face's own outward side (bottom text is mirrored via a flipped
    x_dir plane, not mirror(), which flips face orientation and can send
    the cut the wrong way)."""
    z = size_height / 2 if top else -size_height / 2
    if top:
        plane = Plane.XY.offset(z)
        cut_dir = (0, 0, -1)
    else:
        plane = Plane(origin=(0, 0, z), x_dir=(-1, 0, 0), z_dir=(0, 0, -1))
        cut_dir = (0, 0, 1)
    with BuildSketch(plane) as sk:
        with Locations((0, mark_offset_y)):
            Text(letter, font_size=mark_size)
    return extrude(sk.sketch, amount=mark_depth, dir=cut_dir)


part -= engrave_letter("T", top=True)
part -= engrave_letter("B", top=False)

# =============================================================================
# OUTPUT
# =============================================================================

print(f"hub: {size} x {size} x {size_height} mm, D{rod_diameter} rod bore cut at "
      f"{bore_diameter}mm (+{rod_clearance}mm print clearance), "
      f"4x M{screw_diameter} holes at +/-{o} mm")

# tag the output filename with diameter-clearance-angle so different test
# prints (e.g. exploring bore_angle) land in separate files instead of each
# run overwriting the last: arm_hub-<rod_diameter>-<rod_clearance>-<bore_angle>
tag = lambda v: str(v).replace(".", "")
out_name = f"arm_hub_with_support-{tag(rod_diameter)}-{tag(rod_clearance)}-{tag(bore_angle)}"
export_step(part, f"{out_name}.step")
export_stl(part, f"{out_name}.stl")
print(f"exported {out_name}.step / .stl")

try:
    from ocp_vscode import show

    show(part)
except Exception as e:
    print(f"(viewer not shown: {e})")
