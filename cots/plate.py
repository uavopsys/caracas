"""
Plate - carbon fiber plate with rounded corners, 4x M3 arm-anchor patterns,
standoff holes, FC mount and lightening slots.

The corner anchor patterns match arm_hub.py: a 2x2 grid at +/- pattern_hole_offset,
so the hubs bolt straight onto the plate.

Run with the ocp_vscode standalone viewer running (python3.11 -m ocp_vscode),
or headless: exports plate.step / .stl / .dxf next to this file.
"""

import os
from math import cos, radians, sin
from pathlib import Path

import yaml
from build123d import *
from build123d.exporters import ColorIndex

os.chdir(Path(__file__).parent)  # outputs land next to this script

with open("config.yaml") as f:
    config = yaml.safe_load(f)

# =============================================================================
# PARAMETERS — from config.yaml; derived values computed below
# =============================================================================

globals().update(config["plate"])  # all plate:* keys become local variables

# derived: anchor grid half-spacing follows the hub
pattern_hole_offset = config["arm_hub"]["hole_grid"] / 2

# derived: lightening slots track the anchor patterns along the length
slot_x = frame_length / 2 - pattern_x - slot_gap_from_anchor

def pattern_center_y(angle_deg):
    """Pattern center distance from the plate centerline so that after
    rotation the OUTERMOST hole stays corner_standoff_offset from the long
    edge. A 2x2 grid rotated by a reaches h*(cos a + sin a) sideways."""
    a = abs(radians(angle_deg))
    reach = pattern_hole_offset * (cos(a) + sin(a))
    return frame_width / 2 - corner_standoff_offset - reach

# =============================================================================
# PART
# =============================================================================

# plate with rounded corners
with BuildSketch() as plan:
    rect = Rectangle(frame_length, frame_width)
    fillet(rect.vertices(), radius=corner_rounding)
plate = extrude(plan.sketch, amount=plate_thickness / 2, both=True)

# one 2x2 hole pattern, rotated about its center
def anchor_pattern(angle):
    holes = None
    for dx in (-pattern_hole_offset, pattern_hole_offset):
        for dy in (-pattern_hole_offset, pattern_hole_offset):
            h = Pos(dx, dy, 0) * Cylinder(radius=screw_diameter / 2,
                                          height=plate_thickness + 2)
            holes = h if holes is None else holes + h
    return Rot(0, 0, angle) * holes

# cut the pattern at the four corners. Forward (nose, +X) uses
# pattern_angle_forward, aft uses pattern_angle_aft; port (+Y) rotates CCW,
# starboard CW for the forward pair and the reverse aft -> sign = sx * sy.
# pattern_center_y() keeps the outermost hole flush with the standoff line.
for sx in (-1, 1):
    for sy in (-1, 1):
        cx = sx * (frame_length / 2 - pattern_x)
        base = pattern_angle_forward if sx > 0 else pattern_angle_aft
        angle = sx * sy * base
        cy = sy * pattern_center_y(angle)
        plate -= Pos(cx, cy, 0) * anchor_pattern(angle)

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

# flight controller mounts: concentric M3 grids at (fc_x, fc_y),
# optionally mirrored across the centerline
fc_centers = [(fc_x, fc_y)] + ([(fc_x, -fc_y)] if fc_mirror else [])
for cx, cy in fc_centers:
    for spacing in fc_pattern_spacings:
        for dx in (-spacing / 2, spacing / 2):
            for dy in (-spacing / 2, spacing / 2):
                plate -= Pos(cx + dx, cy + dy, 0) * Cylinder(
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

# forward marker: triangle cutout on the centerline web, pointing at the nose
if fwd_arrow:
    s = arrow_size
    pts = [(-s / 2, -s / 3), (s / 2, 0), (-s / 2, s / 3)]
    with BuildSketch() as arrow_plan:
        with BuildLine():
            Polyline(*pts, close=True)
        make_face()
    plate -= Pos(arrow_x, 0, 0) * extrude(arrow_plan.sketch,
                                          amount=plate_thickness / 2, both=True)

part = plate

# =============================================================================
# OUTPUT
# =============================================================================

print(f"plate: {frame_length} x {frame_width} x {plate_thickness} mm, "
      f"corner r{corner_rounding}")
print(f"4x M{screw_diameter} patterns {pattern_x} from ends, "
      f"outer holes {corner_standoff_offset} from long edge, "
      f"fwd {pattern_angle_forward} / aft {pattern_angle_aft} deg")
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
