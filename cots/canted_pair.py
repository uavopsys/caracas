"""
Canted pair - jig for the 45 deg canted-motor experiment, built step by step.

Step 1: two identical motor mounts, A and B, side by side (spaced along Y),
both upright - motor holes on the platform top, sleeve (cylinder) below.
No rotations, no bar yet.

The mount geometry is read from the exported motor_mount STEP (run
motor_mount.py first) - this script never modifies it.

Run headless: exports canted_pair.step/.stl next to this file.
"""

import os
from pathlib import Path

import yaml
from build123d import *

os.chdir(Path(__file__).parent)  # outputs land next to this script

with open("config.yaml") as f:
    config = yaml.safe_load(f)

arm_cfg = config["arm_hub"]

# spacing between the two mounts (center to center, along Y)
mount_spacing = 140

# connector rod between the mounts: span minus a D16 tube diameter, plus 1mm
# bite into each side
rod_diameter = 6
rod_length = mount_spacing - 16-(0.4*2)   # 126

# cant: each mount clocks about its own bore axis (local X); A goes negative,
# B positive
cant_angle = 45

mount_step = f"motor_mount-{str(arm_cfg['rod_diameter']).replace('.', '')}-" \
             f"{str(arm_cfg['rod_clearance']).replace('.', '')}.step"
mount = import_step(mount_step)

# =============================================================================
# PART
# =============================================================================

# A and B: same orientation (droplet +X), each clocked about its local X
# (bore) axis; the rod passes through both bore axes, so they spin around it
mount_a = Pos(0, mount_spacing / 2, 0) * Rot(-cant_angle, 0, 0) * mount
mount_b = Pos(0, -mount_spacing / 2, 0) * Rot(cant_angle, 0, 0) * mount

# rod: along Y, tangent to the bottom end of the sleeves from the outside -
# center 3mm (its radius) past the tube-entry faces, the floor of the "U"
rod_x = -config["motor_mount"]["insertion_depth"] + rod_diameter / 2  # -22
rod = Pos(rod_x, 0, 0) * Rot(90, 0, 0) * Cylinder(radius=rod_diameter / 2,
                                                  height=rod_length)

part = mount_a + mount_b + rod

# =============================================================================
# OUTPUT
# =============================================================================

bb = part.bounding_box()
print(f"canted pair, step 1: 2x motor mount side by side, "
      f"centers {mount_spacing}mm apart in Y")
print(f"rod: D{rod_diameter} x {rod_length}mm along Y between the centers")
print(f"overall x {bb.min.X:.1f}..{bb.max.X:.1f}, "
      f"y {bb.min.Y:.1f}..{bb.max.Y:.1f}, z {bb.min.Z:.1f}..{bb.max.Z:.1f} mm")

export_step(part, "canted_pair.step")
export_stl(part, "canted_pair.stl")
print("exported canted_pair.step / .stl")

try:
    from ocp_vscode import show

    show(part)
except Exception as e:
    print(f"(viewer not shown: {e})")
