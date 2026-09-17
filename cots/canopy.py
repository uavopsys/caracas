"""
Canopy - hollow lofted pod over the electronics bay, open at the bottom,
sitting on the plate with the full frame footprint. The walls converge up
to a flat top plate (top_length x top_width) whose back edge sits at
top_height above the plate, top_setback from the frame's back edge.

Drivers: top_height, top_setback, and an optional slope_angle. With
slope_angle = 0 the top lies flat at top_height; an angle tilts it so the
front edge rises to top_height + top_length*sin(angle). Wall and corner
angles all follow from where the top sits.

Ventilation: a slot row through the tail wall (exhaust) and NACA ducts
recessed in the roof opening at their front lip (intake). Slots above a
wall's top are skipped with a warning. Both side walls get a rounded
service opening between the middle standoffs (FC overhang clearance and
USB/button access); the width follows the plate's middle_standoff_x. The
plate's lightening slots are exposed through the canopy flange with the
cut reaching inward, so cables from below route into the pod interior
while the side wall stays intact; positions follow the plate config.

Print: PETG. wall_thickness 1.5 mm (4 perimeters at 0.4 line width) is
enough for a shell; bump to 2 mm in config.yaml for a stiffer cover.

Run with the ocp_vscode standalone viewer running (python3.11 -m ocp_vscode),
or headless: exports canopy-<top>Lx<top>W-<angle>-<wall>.step / .stl next to
this file.
"""

import os
from math import atan2, cos, radians, sin, tan
from pathlib import Path

import yaml
from build123d import *

os.chdir(Path(__file__).parent)  # outputs land next to this script

with open("config.yaml") as f:
    config = yaml.safe_load(f)

# =============================================================================
# PARAMETERS — from config.yaml; derived values computed below
# =============================================================================

globals().update(config["canopy"])  # all canopy:* keys become local variables

# derived: footprint follows the plate
length = config["plate"]["frame_length"]
width = config["plate"]["frame_width"]

a = radians(slope_angle)

# top plate: back edge at top_height above the plate, top_setback from the
# frame back edge; slope_angle tilts it up toward the nose from there
back_x = -length / 2
top_back_z = top_height
top_center = Vector(back_x + top_setback + top_length / 2 * cos(a), 0,
                    top_back_z + top_length / 2 * sin(a))
top_plane = Plane(origin=top_center, x_dir=(cos(a), 0, sin(a)),
                  z_dir=(-sin(a), 0, cos(a)))
top_front_z = top_back_z + top_length * sin(a)

# =============================================================================
# PART
# =============================================================================

top_rounding = min(rounding, top_width / 2 - 1, top_length / 2 - 1)

with BuildPart() as pod:
    with BuildSketch(Plane.XY):  # base: full frame footprint at plate level
        base = Rectangle(length, width)
        fillet(base.vertices(), radius=rounding)
    with BuildSketch(top_plane):
        top = Rectangle(top_length, top_width)
        fillet(top.vertices(), radius=top_rounding)
    loft()

# hollow by subtracting an inner loft. OCC's own offset/shell fails on lofted
# solids, and a plain horizontal inset would leave the shallow walls (front
# ramp, sides) paper-thin: for a wall leaning at angle b from horizontal the
# inset for a perpendicular thickness w is w/sin(b). Lean is computed per
# direction from the geometry; corners land somewhere in between, which is
# fine for a printed shell.
w = wall_thickness
rise_side = (top_back_z + top_front_z) / 2

def inset(run, rise):
    return w / sin(atan2(rise, run))

inset_back = inset(top_setback, top_back_z)
inset_front = inset(length - top_setback - top_length * cos(a), top_front_z)
inset_side = inset((width - top_width) / 2, rise_side)

# cavity base: asymmetric X insets shift its center; starts below the plate
# so the pod bottom stays open
base_cx = (inset_back - inset_front) / 2
base_l = length - inset_back - inset_front
base_w = width - 2 * inset_side

# cavity top: outer top plane lowered by w (perpendicular roof thickness),
# shrunk by the average X inset and the side inset
inset_x_top = (inset_back + inset_front) / 2 / cos(a)
inner_top_plane = Plane(origin=top_center - Vector(-sin(a), 0, cos(a)) * w,
                        x_dir=(cos(a), 0, sin(a)), z_dir=(-sin(a), 0, cos(a)))
top_l = top_length - 2 * inset_x_top
top_w = top_width - 2 * inset_side

with BuildPart() as cavity:
    with BuildSketch(Plane(origin=(base_cx, 0, -2))):
        cb = Rectangle(base_l, base_w)
        fillet(cb.vertices(), radius=max(0.5, rounding - max(inset_x_top, inset_side)))
    with BuildSketch(inner_top_plane):
        ct = Rectangle(top_l, top_w)
        fillet(ct.vertices(), radius=max(0.5, top_rounding - max(inset_x_top, inset_side)))
    loft()

cavity_solid = cavity.solid()
part = pod.solid() - cavity_solid

# mounting flange: flat ring at plate level (full footprint border) so the 8
# standoff screws seat flat even where the pod walls slope. Hole positions and
# diameter come from the plate config, so they match the standoffs by
# construction.
P = config["plate"]
with BuildSketch() as flange_plan:
    ring_out = Rectangle(length, width)
    fillet(ring_out.vertices(), radius=rounding)
    ring_in = Rectangle(length - 2 * flange_width, width - 2 * flange_width,
                        mode=Mode.SUBTRACT)
    fillet(ring_in.vertices(), radius=max(0.5, rounding - flange_width))
part += extrude(flange_plan.sketch, amount=flange_thickness)

standoff_xy = []
for sx in (-1, 1):
    for sy in (-1, 1):
        standoff_xy.append((sx * (length / 2 - P["corner_standoff_offset"]),
                            sy * (width / 2 - P["corner_standoff_offset"])))
        standoff_xy.append((sx * P["middle_standoff_x"],
                            sy * (width / 2 - P["middle_standoff_edge_offset"])))
for x, y in standoff_xy:
    part -= Pos(x, y, -1) * Cylinder(radius=P["standoff_diameter"] / 2,
                                     height=60)

# expose the plate's lightening slots through the canopy base for cable
# pass-through: vertical prisms through the flange ONLY, with the profile
# extended inward past the slit's inner edge - a cable coming up through
# the slit turns into the pod interior, and the side wall's outer face
# stays intact. Positions follow the plate config, so they track the
# slots by construction.
if expose_slots and P["lightening"]:
    slot_x = length / 2 - P["pattern_x"] - P["slot_gap_from_anchor"]
    ec = expose_slot_clearance
    with BuildSketch() as expose_plan:
        er = Rectangle(P["slot_length"] + 2 * ec,
                       P["slot_width"] + 2 * ec + expose_slot_extend_in)
        fillet(er.vertices(), radius=P["slot_radius"] + ec)
    for sx in (-1, 1):
        for sy in (-1, 1):
            part -= Pos(sx * slot_x,
                        sy * (P["slot_y"] - expose_slot_extend_in / 2), -1) \
                * extrude(expose_plan.sketch, amount=flange_thickness + 2)

# projected cutout: vertical cylinder, so the opening measures cutout_diameter
# on the plate plane even where it crosses the angled walls/roof. Extruded up
# from below the plate (a plain Cylinder is centered on z=0 and would sink
# below the roof as top_height grows)
if cutout_diameter:
    part -= Pos(back_x + cutout_x_from_back, cutout_y, -1) * extrude(
        Circle(radius=cutout_diameter / 2), amount=top_front_z + 20)

# side service openings: rounded-rectangular cutouts in both side walls
# between the middle standoffs, from the plate up to side_opening_height.
# Clears the FC board overhanging the plate edge and gives USB/button
# access. Width is derived from the plate's middle_standoff_x so the
# opening stays clear of the standoff posts by construction.
if side_openings:
    open_w = 2 * (P["middle_standoff_x"] - P["standoff_diameter"] / 2
                  - side_opening_clearance)
    open_r = min(side_opening_radius, side_opening_height / 2 - 0.5,
                 open_w / 2 - 0.5)
    # rounded profile in XZ, extruded across the whole width: pierces both
    # leaning side walls and the flange in one cut
    with BuildSketch(Plane.XZ) as opening_plan:
        oc = Rectangle(open_w, side_opening_height)
        fillet(oc.vertices(), radius=open_r)
    part -= Pos(0, 0, side_opening_height / 2) * extrude(
        opening_plan.sketch, amount=width / 2 + 10, both=True)

# =============================================================================
# VENTILATION
# =============================================================================

# slot row through the tail (exhaust) wall, so hot air has a way out. Cutters
# are horizontal boxes long enough in X to pierce the leaning wall wherever
# it is; the wall's X at a given z is interpolated between base and top edge.
_slot_warnings = []

def _slot_row(name, x_base, x_top, z_top, z0, count, pitch, slot_w, slot_h):
    run = abs(x_base - x_top)
    for i in range(count):
        z = z0 + i * pitch
        if z + slot_h / 2 > z_top:
            _slot_warnings.append(
                f"{name} slot {i} at z={z:g} is above the wall top "
                f"({z_top:g}) - it cuts nothing")
            continue
        yield Pos(_wall_x(x_base, x_top, z_top, z), 0, z) * Box(
            2 * run + 10, slot_w, slot_h)

def _wall_x(x_base, x_top, z_top, z):
    return x_base + (x_top - x_base) * z / z_top if z_top > 0 else x_base

if exhaust_slots:
    for c in _slot_row("exhaust", back_x, back_x + top_setback, top_back_z,
                       exhaust_slot_z, exhaust_slot_count, exhaust_slot_pitch,
                       exhaust_slot_width, exhaust_slot_height):
        part -= c

# NACA ducts in the roof: recessed ramps, flush and narrow at the rear,
# opening through the shell at the front lip (which faces the airflow).
# Cross-sections are perpendicular to the slope direction: width across (Y)
# x depth along the roof normal; the rear one is a shallow sliver tangent to
# the surface, the front one pierces the shell.
if naca_count:
    xdir = Vector(cos(a), 0, sin(a))  # slope direction (duct length axis)
    nrm = Vector(-sin(a), 0, cos(a))  # roof outward normal (duct depth axis)

    def roof_pt(s, y, off):
        return top_center + xdir * s + Vector(0, 1, 0) * y + nrm * off

    lip_s = top_length / 2 - naca_lip_margin  # front lip position along slope
    tail_s = lip_s - naca_length
    ys = [0] if naca_count == 1 else [
        (i - (naca_count - 1) / 2) * naca_spacing for i in range(naca_count)]
    for dy in ys:
        with BuildPart() as duct:
            # rear end: sliver just breaking the surface (top edge proud)
            with BuildSketch(Plane(origin=roof_pt(tail_s, dy, -0.1),
                                   x_dir=(0, 1, 0), z_dir=xdir)):
                Rectangle(naca_width_tail, 0.4)
            # front lip: proud of the surface by 0.3, reaching naca_depth in
            with BuildSketch(Plane(origin=roof_pt(lip_s, dy, -(naca_depth / 2 - 0.3)),
                                   x_dir=(0, 1, 0), z_dir=xdir)):
                Rectangle(naca_width_lip, naca_depth)
            loft()
        part -= duct.solid()

# =============================================================================
# OUTPUT - only when run directly; `import canopy` just builds canopy.part
# =============================================================================

if __name__ == "__main__":
    print(f"canopy: {length} x {width} base, top {top_length} x {top_width} at "
          f"{slope_angle} deg, {top_setback} from back, r{rounding}, "
          f"wall {wall_thickness}")
    print(f"top plate: back z {top_back_z:.1f} -> front z {top_front_z:.1f} "
          f"(peak of the pod)")
    for warn in _slot_warnings:
        print(f"WARNING: {warn}")
    tag = f"canopy-{top_length:g}x{top_width:g}-{slope_angle:g}-{wall_thickness:g}"
    export_step(part, f"{tag}.step")
    export_stl(part, f"{tag}.stl")
    # weight estimate (PETG ~1.27 g/cm3; thin walls print solid, ~all perimeter)
    print(f"volume {part.volume / 1000:.1f} cm3 -> "
          f"~{part.volume / 1000 * 1.27:.1f} g PETG")
    print(f"exported {tag}.step / .stl")

    try:
        from ocp_vscode import show

        show(part)
    except Exception as e:
        print(f"(viewer not shown: {e})")
