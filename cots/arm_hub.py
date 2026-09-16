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
mark_offset_y = 6  # shifted off-center so it clears the central hex nut trap below

# ---- central M3 through-hole + hex nut traps (top and bottom) ----
# Vertical M3 clearance hole through the block center (T to B), with a
# recessed hex pocket at each end so a screw + nut can clamp through it.
center_hole_diameter = 3.4  # M3 clearance (printed plastic, not self-tapping)
nut_width = 6                # hex recess width across flats
nut_depth = 3                # hex recess depth, cut in from each face

# ---- bore orientation ----
# Rotates the rod bore around Z; the 4 screw holes are untouched (their
# corner positions don't depend on this). 0 = bore along X (nose/tail),
# 90 = bore along Y (port/starboard). Length is computed below so the bore
# always reaches through at any angle; a corner-clearance check warns when
# the block's square corners intrude on the round bore instead (only clean
# near 0/90 - a square's corners sit exactly on the 45 deg diagonal, so
# 45 deg always clips regardless of size).
bore_angle = 30

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

# Reaching the exit face along the CENTERLINE isn't enough: the cylinder's
# flat end caps are tilted relative to that flat face (by bore_angle), so the
# trailing edge of each disc needs an extra r*tan(angle) of length to clear
# the material there too - otherwise a crescent of it is left un-cut even
# though the centerline calculation says the length is "enough".
bore_length = (size + bore_diameter * n) / m + 1  # reaches both exit faces + margin
corner_clearance = min(abs(cx * st - cy * ct) for cx in (-a, a) for cy in (-a, a))
if corner_clearance < bore_diameter / 2:
    print(f"WARNING: bore_angle={bore_angle} clips a block corner "
          f"(clearance {corner_clearance:.2f}mm < bore radius {bore_diameter / 2}mm) - "
          f"the hole will break out through an adjacent face instead of staying round")

# =============================================================================
# PART
# =============================================================================

part = Box(size, size, size_height)

# D16 bore, horizontal through the cube, swept around Z by bore_angle
part -= Rot(0, 0, bore_angle) * Rot(0, 90, 0) * Cylinder(radius=bore_diameter / 2, height=bore_length)

# 4 vertical M3 holes near the corners (through top and bottom faces)
for x in (-o, o):
    for y in (-o, o):
        part -= Pos(x, y, 0) * Cylinder(radius=screw_diameter / 2, height=size + 6)

# central M3 through-hole (T to B) + hex nut trap recessed into each face
part -= Cylinder(radius=center_hole_diameter / 2, height=size_height + 4)
for sign in (1, -1):
    z = sign * size_height / 2
    with BuildSketch(Plane.XY.offset(z)) as hex_sk:
        RegularPolygon(radius=nut_width / 2, side_count=6, major_radius=False)
    part -= extrude(hex_sk.sketch, amount=nut_depth, dir=(0, 0, -sign))


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
out_name = f"arm_hub-{tag(rod_diameter)}-{tag(rod_clearance)}-{tag(bore_angle)}"
export_step(part, f"{out_name}.step")
export_stl(part, f"{out_name}.stl")
print(f"exported {out_name}.step / .stl")

try:
    from ocp_vscode import show

    show(part)
except Exception as e:
    print(f"(viewer not shown: {e})")
