"""
Plate - carbon fiber plate with rounded corners, 4x M3 arm-anchor patterns,
standoff holes, FC mount and lightening slots.

The corner anchor patterns match arm_hub.py: a 2x2 grid at +/- pattern_hole_offset,
so the hubs bolt straight onto the plate.

Run with the ocp_vscode standalone viewer running (python3.11 -m ocp_vscode),
or headless: exports plate.step / .stl / .dxf next to this file.
"""

import os
from pathlib import Path

from build123d import *
from build123d.exporters import ColorIndex

os.chdir(Path(__file__).parent)  # outputs land next to this script

# =============================================================================
# PARAMETERS
# =============================================================================

# ---- plate ----
frame_length = 200
frame_width = 90
plate_thickness = 2.5
corner_rounding = 10

# ---- M3 anchor patterns (one per corner) ----
screw_diameter = 3.2       # M3 clearance (2.5 for tapping)
pattern_hole_offset = 9.5  # half-spacing of the 2x2 grid; must match arm_hub.py
pattern_x = 30             # pattern center distance from the plate end (short) edge
pattern_y = 20             # pattern center distance from the plate side (long) edge
pattern_angle = 0          # rotation of every corner pattern, degrees

# ---- standoff holes (8 total: 4 corner + 4 middle) ----
standoff_diameter = 3.2          # M3 standoff screws
corner_standoff_offset = 10      # corner hole center distance from each edge
middle_standoff_edge_offset = 10 # middle hole center distance from the long edge
middle_standoff_x = 30           # middle hole distance from plate center along X (arm axis)

# ---- flight controller mount (standard 30.5x30.5 pattern) ----
fc_pattern_spacing = 30.5  # hole grid spacing
fc_hole_diameter = 3.2     # M3 clearance
fc_x = 0                 # shift the whole pattern along the length
fc_y = 0                 # shift the whole pattern along the width

# ---- lightening slots (weight reduction in the low-stress web) ----
lightening = True
slot_length = 22  # along X
slot_width = 15   # along Y
slot_radius = 4   # corner fillet - generous radii, sharp corners start cracks
slot_x = 42.5     # slot center distance from plate center, mirrored on both axes
slot_y = 20

# =============================================================================
# PART
# =============================================================================

# plate with rounded corners
with BuildSketch() as plan:
    rect = Rectangle(frame_length, frame_width)
    fillet(rect.vertices(), radius=corner_rounding)
plate = extrude(plan.sketch, amount=plate_thickness / 2, both=True)

# one 2x2 hole pattern, rotated about its center
def anchor_pattern():
    holes = None
    for dx in (-pattern_hole_offset, pattern_hole_offset):
        for dy in (-pattern_hole_offset, pattern_hole_offset):
            h = Pos(dx, dy, 0) * Cylinder(radius=screw_diameter / 2,
                                          height=plate_thickness + 2)
            holes = h if holes is None else holes + h
    return Rot(0, 0, pattern_angle) * holes

# cut the pattern at the four corners
for sx in (-1, 1):
    for sy in (-1, 1):
        cx = sx * (frame_length / 2 - pattern_x)
        cy = sy * (frame_width / 2 - pattern_y)
        plate -= Pos(cx, cy, 0) * anchor_pattern()

# standoff holes: 4 at the corners, 4 between the arm anchors
def standoff_hole():
    return Cylinder(radius=standoff_diameter / 2, height=plate_thickness + 2)

for sx in (-1, 1):
    for sy in (-1, 1):
        # corners: offset from both edges
        plate -= Pos(sx * (frame_length / 2 - corner_standoff_offset),
                     sy * (frame_width / 2 - corner_standoff_offset), 0) * standoff_hole()
        # middle: between the two anchor patterns on each long side
        plate -= Pos(sx * middle_standoff_x,
                     sy * (frame_width / 2 - middle_standoff_edge_offset), 0) * standoff_hole()

# flight controller mount: 30.5x30.5 grid, shifted by (fc_x, fc_y)
for dx in (-fc_pattern_spacing / 2, fc_pattern_spacing / 2):
    for dy in (-fc_pattern_spacing / 2, fc_pattern_spacing / 2):
        plate -= Pos(fc_x + dx, fc_y + dy, 0) * Cylinder(
            radius=fc_hole_diameter / 2, height=plate_thickness + 2)

# lightening slots: rounded rectangles in the web between FC and anchors
if lightening:
    with BuildSketch() as slot_plan:
        slot_rect = Rectangle(slot_length, slot_width)
        fillet(slot_rect.vertices(), radius=slot_radius)
    for sx in (-1, 1):
        for sy in (-1, 1):
            plate -= Pos(sx * slot_x, sy * slot_y, 0) * extrude(
                slot_plan.sketch, amount=plate_thickness / 2, both=True)

part = plate

# =============================================================================
# OUTPUT
# =============================================================================

print(f"plate: {frame_length} x {frame_width} x {plate_thickness} mm, "
      f"corner r{corner_rounding}")
print(f"4x M{screw_diameter} patterns at +/-({frame_length / 2 - pattern_x}, "
      f"{frame_width / 2 - pattern_y}), angle {pattern_angle} deg")
export_step(part, "plate.step")
export_stl(part, "plate.stl")

# DXF for the carbon cutter: outline, holes and slots on separate layers
top_face = part.faces().sort_by(Axis.Z)[-1]
dxf = ExportDXF(unit=Unit.MM)
dxf.add_layer("CUT", color=ColorIndex.GREEN)
dxf.add_layer("HOLES", color=ColorIndex.RED)
dxf.add_layer("SLOTS", color=ColorIndex.YELLOW)
dxf.add_shape(top_face.outer_wire(), layer="CUT")
for wire in top_face.inner_wires():
    is_circle = len(wire.edges()) == 1 and wire.edges()[0].geom_type == GeomType.CIRCLE
    dxf.add_shape(wire, layer="HOLES" if is_circle else "SLOTS")
dxf.write("plate.dxf")

# weight estimate (carbon plate ~1.55 g/cm3)
grams = part.volume / 1000 * 1.55
print(f"volume {part.volume:.0f} mm3 -> ~{grams:.1f} g carbon")
print("exported plate.step / .stl / .dxf")

try:
    from ocp_vscode import show

    show(part)
except Exception as e:
    print(f"(viewer not shown: {e})")
