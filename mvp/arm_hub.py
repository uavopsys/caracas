"""
Arm hub - 28x28x30mm block with D16 rod bore and M3 corner screw holes.
Z is 30mm to match 30mm m/F standoffs. M3 holes are 2.5mm self-tapping
pilots for printed plastic (no brass insert).

The hole grid (+/- size/2 - screw_edge_offset = +/-9.5mm) must match
pattern_hole_offset in plate.py.

Run with the ocp_vscode standalone viewer running (python3.11 -m ocp_vscode),
or headless: exports arm_hub.step / .stl next to this file.
"""

import os
from pathlib import Path

from build123d import *

os.chdir(Path(__file__).parent)  # outputs land next to this script

# =============================================================================
# PARAMETERS
# =============================================================================

size = 28                # cube edge length (Z is size+2 = 30, matches 30mm standoffs)
rod_diameter = 16        # through-hole for the carbon rod (D16)
screw_diameter = 2.5     # M3 self-tapping pilot for printed plastic (no insert)
screw_edge_offset = 4.5  # hole center distance from each cube edge

# =============================================================================
# PART
# =============================================================================

part = Box(size, size, size + 2)

# D16 bore, horizontal through the cube (along X)
part -= Rot(0, 90, 0) * Cylinder(radius=rod_diameter / 2, height=size + 2)

# 4 vertical M3 holes near the corners (through top and bottom faces)
o = size / 2 - screw_edge_offset
for x in (-o, o):
    for y in (-o, o):
        part -= Pos(x, y, 0) * Cylinder(radius=screw_diameter / 2, height=size + 6)

# =============================================================================
# OUTPUT
# =============================================================================

print(f"hub: {size} x {size} x {size + 2} mm, D{rod_diameter} bore, "
      f"4x M{screw_diameter} holes at +/-{o} mm")
export_step(part, "arm_hub.step")
export_stl(part, "arm_hub.stl")
print("exported arm_hub.step / .stl")

try:
    from ocp_vscode import show

    show(part)
except Exception as e:
    print(f"(viewer not shown: {e})")
