"""
D16 'droplet' motor mount - teardrop shell cantilevered past the END of the
16mm carbon arm tube, carrying a 2812-size brushless motor on a flat
platform. The whole part lives inside the arm hub's vertical envelope:
centered bore at z=0, platform top at exactly +size_height/2 (11mm), nothing
below -size_height/2 (-11mm). Flush tops and bottoms with the arm hub ARE
the leveling mechanism (see below).

Geometry (shared values from config.yaml, motor_mount section):
- BLIND bore (glue well) = rod_diameter + rod_clearance = 16.4mm: the tube
  inserts insertion_depth (25mm) from the hub-facing end and bottoms against
  a stop face. Past the stop a 10mm hole opens into the droplet's hollow
  cavity, so the carbon tube's open end faces the cavity - the motor cable
  gets into the tube through it, no drilling.
- teardrop plan along the tube axis: round end (2 x droplet_radius, ~35mm
  across) carries the motor, tapering back to the D22 sleeve. Platform skin
  (3mm) at z=+11: 4x 3.2mm holes on a 19mm bolt circle at 45/135/225/315 deg
  (from skyfold's motor_adapter_19_25.scad), a 9mm center hole, and the cable
  opening (rounded rectangle, cable_slot_width x cable_slot_x1-x0) BETWEEN
  the bolt circle and the arm - like the classic aluminum clamp mounts, the
  motor leads exit the motor's rear edge and drop straight through into the
  cavity, then through the stop hole into the tube. No bend, no exposed wire.
- open bottom: a perimeter skirt (skirt_thickness) follows the droplet
  outline from the skin underside down to skirt_bottom_z like a shallow boat
  hull; the cavity is open from below so the M3 bolt heads (bolts come up
  from below into the motor's threaded base) are accessible. Two side ribs
  stiffen the skin, clear of the cable raceway and the head envelopes.
- leveling feet: three foot_size squares with bottoms at exactly z=-11 - a
  3-point stance (the round sleeve alone can't sit flat). Leveling: set the
  mount on a flat table next to the arm hub (or press both against a
  straightedge) while the epoxy cures; flush bottoms (-11) and tops (+11)
  guarantee rotational alignment.
- cable funnel: trumpet flare (10 -> 15mm) on the cavity side of the stop
  hole plus a small rim chamfer on the tube side, so wires feeding into the
  tube end are guided and the tube tip doesn't catch a sharp rim.

Print: platform skin DOWN on the bed (part flipped from its installed
orientation), bore axis horizontal - the open cavity faces up and needs no
supports; the blind bore prints as a horizontal hole, hence rod_clearance
0.4mm total for bridging sag (same reasoning as arm_hub.py).

Run with the ocp_vscode standalone viewer running (python3.11 -m ocp_vscode),
or headless: exports motor_mount-<rod_diameter>-<rod_clearance>.step/.stl
next to this file.
"""

import math
import os
from pathlib import Path

import yaml
from build123d import *

os.chdir(Path(__file__).parent)  # outputs land next to this script

# =============================================================================
# PARAMETERS — from config.yaml
# =============================================================================

with open("config.yaml") as f:
    config = yaml.safe_load(f)

cfg = config["motor_mount"]

rod_diameter = cfg["rod_diameter"]        # D16 carbon arm tube
rod_clearance = cfg["rod_clearance"]      # glue slip fit + horizontal-bore sag
sleeve_diameter = cfg["sleeve_diameter"]  # ~3mm wall over the rod
insertion_depth = cfg["insertion_depth"]  # blind bore: tube bottoms against the stop
stop_hole_diameter = cfg["stop_hole_diameter"]  # cable pass at the bore's inner end
droplet_radius = cfg["droplet_radius"]    # round end carrying the motor
droplet_center_x = cfg["droplet_center_x"]  # round end center, outboard of the stop
skin_thickness = cfg["skin_thickness"]    # platform top skin
skirt_thickness = cfg["skirt_thickness"]  # perimeter wall around the open cavity
skirt_bottom_z = cfg["skirt_bottom_z"]    # skirt lower edge; cavity open below
motor_bcd = cfg["motor_bcd"]              # 2812 bolt circle, 4x M3 at the 45 deg diagonals
motor_hole_diameter = cfg["motor_hole_diameter"]
center_hole_diameter = cfg["center_hole_diameter"]
cable_slot_x0 = cfg["cable_slot_x0"]  # cable opening, tube-side end
cable_slot_x1 = cfg["cable_slot_x1"]  # motor-side end (behind the rear bolt holes)
cable_slot_width = cfg["cable_slot_width"]
foot_size = cfg["foot_size"]              # 3 leveling feet

# vertical envelope: the arm hub is a size x size x size_height block with a
# centered bore, so its faces sit at +/- size_height/2 - the mount shares both
# planes (platform top at +env, feet bottoms at -env).
env = config["arm_hub"]["size_height"] / 2  # 11.0

# =============================================================================
# DERIVED
# =============================================================================

bore_diameter = rod_diameter + rod_clearance  # 16.4
bore_radius = bore_diameter / 2
sleeve_radius = sleeve_diameter / 2

skin_top_z = env                       # platform top: flush with the arm hub top
skin_bottom_z = skin_top_z - skin_thickness

# X layout: the bore stop face is at x=0; the tube/sleeve extends in -X
# (toward the arm hub), the droplet cantilevers outboard in +X.
sleeve_x0 = -insertion_depth           # tube entry face
stop_x1 = 3                            # stop wall thickness: x 0..3
funnel_x1 = 6                          # cable funnel: x 3..6
sleeve_x1 = funnel_x1                  # sleeve reaches into the droplet neck
neck_x = 2                             # teardrop neck circle center (on the sleeve)

hole_xy = motor_bcd / (2 * math.sqrt(2))  # hole center on each axis (+/-6.72)
motor_x = droplet_center_x             # motor pattern center
skin_mid_z = (skin_bottom_z + skin_top_z) / 2  # cuts centered here pierce the skin
slot_cx = (cable_slot_x0 + cable_slot_x1) / 2
slot_len = cable_slot_x1 - cable_slot_x0

# M3 socket head envelope (heads sit in the open cavity under the skin)
head_diameter = 5.5
head_height = 3.0

# ribs stiffening the skin: along X at the cavity sides, clear of the cable
# raceway (|y| <= 5 around the stop hole) and of the head envelopes (rim at
# |y| = hole_xy + head_diameter/2 = 9.47)
rib_y0 = 11
rib_thickness = 3

# leveling feet: two on the sleeve fore/aft, one under the droplet tip
feet = [(sleeve_x0 + 4, 0), (-4, 0), (droplet_center_x + droplet_radius - foot_size / 2 + 1, 0)]

# =============================================================================
# PART
# =============================================================================


def teardrop(x1, r1, x2, r2):
    """Convex hull of two circles on the X axis (the droplet plan outline):
    both circles plus the trapezoid between their external tangent points."""
    d = x2 - x1
    gamma = math.asin((r2 - r1) / d)  # tangent line tilt from the center line
    sg, cg = math.sin(gamma), math.cos(gamma)
    p1u = (x1 - r1 * sg, r1 * cg)
    p1l = (x1 - r1 * sg, -r1 * cg)
    p2u = (x2 - r2 * sg, r2 * cg)
    p2l = (x2 - r2 * sg, -r2 * cg)
    # the polygon must be counterclockwise (seen from +Z): a clockwise one has
    # a downward face normal and extrudes BELOW the sketch plane
    pts = [p1u, p2u, p2l, p1l]
    if sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(pts, pts[1:] + pts[:1])) < 0:
        pts.reverse()
    return (Pos(x1, 0) * Circle(r1) + Pos(x2, 0) * Circle(r2)
            + Polygon(*pts, align=None))


outline = teardrop(neck_x, sleeve_radius, droplet_center_x, droplet_radius)
# cavity outline: the hull eroded by the skirt thickness = hull of the
# circles shrunk by the same amount
outline_inner = teardrop(neck_x, sleeve_radius - skirt_thickness,
                         droplet_center_x, droplet_radius - skirt_thickness)

# droplet body: full teardrop prism from the skirt bottom to the platform top
body_height = skin_top_z - skirt_bottom_z
part = extrude(Plane.XY.offset(skirt_bottom_z) * outline, amount=body_height)

# sleeve over the tube
part += Pos((sleeve_x0 + sleeve_x1) / 2, 0, 0) * Rot(0, 90, 0) * Cylinder(
    radius=sleeve_radius, height=sleeve_x1 - sleeve_x0)

# open cavity: hollow the droplet outboard of the stop wall, up to the skin
cavity = extrude(Plane.XY.offset(skirt_bottom_z - 1) * outline_inner,
                 amount=skin_bottom_z - skirt_bottom_z + 1.1)
cavity &= Pos((stop_x1 + 100) / 2, 0, 0) * Box(100 - stop_x1, 4 * droplet_radius, body_height + 4)
part -= cavity

# side ribs, trimmed to the droplet outline
rib_solid = extrude(Plane.XY.offset(skirt_bottom_z) * outline,
                    amount=skin_bottom_z - skirt_bottom_z)
for sy in (1, -1):
    rib = Pos((funnel_x1 + droplet_center_x + 13) / 2, sy * (rib_y0 + rib_thickness / 2),
              (skirt_bottom_z + skin_bottom_z) / 2) * Box(
        droplet_center_x + 13 - funnel_x1, rib_thickness, skin_bottom_z - skirt_bottom_z)
    part += rib & rib_solid

# leveling feet, bottoms exactly at -env
for fx, fy in feet:
    part += Pos(fx, fy, -env + foot_size / 2) * Box(foot_size, foot_size, foot_size)

# blind bore (glue well): straight to the stop face at x=0
part -= Pos((sleeve_x0 - 1) / 2, 0, 0) * Rot(0, 90, 0) * Cylinder(
    radius=bore_radius, height=-sleeve_x0 + 1)

# stop hole + rim chamfer (tube side) + cable funnel (cavity side)
part -= Pos((stop_x1 - 0.2) / 2, 0, 0) * Rot(0, 90, 0) * Cylinder(
    radius=stop_hole_diameter / 2, height=stop_x1 + 0.2)
part -= Pos(0, 0, 0) * Rot(0, 90, 0) * Cone(bottom_radius=stop_hole_diameter / 2 + 1,
                                            top_radius=stop_hole_diameter / 2, height=1)
part -= Pos(stop_x1, 0, 0) * Rot(0, 90, 0) * Cone(bottom_radius=stop_hole_diameter / 2,
                                                  top_radius=stop_hole_diameter / 2 + 2.5,
                                                  height=funnel_x1 - stop_x1)

# platform features: 4x M3 holes on the bolt circle (45 deg diagonals),
# 9mm center hole (shaft clearance), and the cable opening: a rounded
# rectangle between the bolt circle and the arm (like the classic aluminum
# clamp mounts) - the motor leads exit the motor's rear edge and drop
# straight through into the cavity, right above the funnel
for sx in (1, -1):
    for sy in (1, -1):
        part -= Pos(motor_x + sx * hole_xy, sy * hole_xy, skin_mid_z) * Cylinder(
            radius=motor_hole_diameter / 2, height=skin_thickness + 1)
part -= Pos(motor_x, 0, skin_mid_z) * Cylinder(radius=center_hole_diameter / 2,
                                               height=skin_thickness + 1)
# cable opening near the arm: rounded rectangle between the bolt circle and
# the funnel (like the classic aluminum clamp mounts) - the motor leads exit
# the motor's rear edge and drop straight through into the cavity
slot_corner_r = 2
part -= Pos(slot_cx, 0, skin_mid_z) * Box(
    slot_len - 2 * slot_corner_r, cable_slot_width, skin_thickness + 1)
part -= Pos(slot_cx, 0, skin_mid_z) * Box(
    slot_len, cable_slot_width - 2 * slot_corner_r, skin_thickness + 1)
for ex in (slot_cx - slot_len / 2 + slot_corner_r, slot_cx + slot_len / 2 - slot_corner_r):
    for ey in (cable_slot_width / 2 - slot_corner_r, -(cable_slot_width / 2 - slot_corner_r)):
        part -= Pos(ex, ey, skin_mid_z) * Cylinder(radius=slot_corner_r,
                                                   height=skin_thickness + 1)

# =============================================================================
# VERIFICATION — probe solids intersected with the part (no eyeballing)
# =============================================================================

TOL = 1e-3  # mm3; tangent-surface noise floor for "clear" probes


def hit_volume(probe):
    """Intersection volume of a probe solid with the part (~0 = clear)."""
    return (part & probe).volume


checks = []


def check(name, ok, detail):
    checks.append(ok)
    print(f"  {'PASS' if ok else 'FAIL'}: {name} ({detail})")


def bore_probe(r, x0, x1):
    return Pos((x0 + x1) / 2, 0, 0) * Rot(0, 90, 0) * Cylinder(radius=r, height=x1 - x0)


print("geometry checks:")

# (a) blind bore = D16.4, stop at the insertion depth: a hair under the bore
# passes clear from the entry to the stop face; a hair over hits the wall;
# the same tube-sized probe pushed past the stop face hits the stop
v_fit = hit_volume(bore_probe(bore_radius - 0.01, sleeve_x0 - 1, 0))
v_over = hit_volume(bore_probe(bore_radius + 0.1, sleeve_x0 - 1, 0))
check(f"bore is D{bore_diameter} over the full insertion depth ({insertion_depth}mm)",
      v_fit < TOL and v_over > 1,
      f"D{bore_diameter - 0.02:.2f} hits {v_fit:.4f}mm3, D{bore_diameter + 0.2:.2f} hits {v_over:.1f}mm3")
v_stop = hit_volume(bore_probe(bore_radius - 0.2, sleeve_x0 - 1, 1))
check(f"bore is blind: stop face at x=0 (insertion depth {insertion_depth}mm)",
      v_stop > 1, f"D{bore_diameter - 0.4:.1f} probe past the stop hits {v_stop:.1f}mm3")

# (b) platform top at exactly +env, all feet bottoms at exactly -env
for i, (px, py) in enumerate([(motor_x - 12, 8), (motor_x + 12, 0), (motor_x, 12), (motor_x, -12)]):
    v_below = hit_volume(Pos(px, py, skin_top_z - 0.05) * Box(2, 2, 0.1))
    v_above = hit_volume(Pos(px, py, skin_top_z + 0.05) * Box(2, 2, 0.1))
    check(f"platform top #{i + 1} at z=+{env}", v_below > 0.3 and v_above < TOL,
          f"{v_below:.2f}mm3 just below, {v_above:.4f}mm3 just above")
for i, (fx, fy) in enumerate(feet):
    v_above = hit_volume(Pos(fx, fy, -env + 0.05) * Box(2, 2, 0.1))
    v_below = hit_volume(Pos(fx, fy, -env - 0.05) * Box(2, 2, 0.1))
    check(f"foot #{i + 1} bottom at z=-{env}", v_above > 0.3 and v_below < TOL,
          f"{v_above:.2f}mm3 just above, {v_below:.4f}mm3 just below")

# (c) cable raceway: three overlapping probes form a clear path from above
# slit S, through the cavity, through the stop hole and into the bore void.
# p1 vertical through the slot, p2 horizontal across the cavity at z=2,
# p3 through the stop hole into the bore
v_p1 = hit_volume(Pos(slot_cx, 0, 5.8) * Cylinder(radius=2, height=11.6))
v_p2 = hit_volume(Pos((1 + slot_cx) / 2, 0, 2) * Rot(0, 90, 0) * Cylinder(
    radius=2, height=slot_cx - 1))
v_p3 = hit_volume(Pos(-3, 0, 0) * Rot(0, 90, 0) * Cylinder(radius=3.5, height=10))
check("raceway: cable slot -> cavity -> stop hole -> tube bore",
      max(v_p1, v_p2, v_p3) < TOL,
      f"slot probe {v_p1:.4f}mm3, cavity probe {v_p2:.4f}mm3, stop-hole probe {v_p3:.4f}mm3")

# (d) bolt-head clearance under the skin at each hole: the spec'd 3.5mm open
# gap, plus the real M3 socket head envelope (5.5 x 3mm)
v_gap_max = v_head_max = 0
for sx in (1, -1):
    for sy in (1, -1):
        v_gap_max = max(v_gap_max, hit_volume(
            Pos(motor_x + sx * hole_xy, sy * hole_xy, skin_bottom_z - 1.75) * Cylinder(
                radius=motor_hole_diameter / 2, height=3.5)))
        v_head_max = max(v_head_max, hit_volume(
            Pos(motor_x + sx * hole_xy, sy * hole_xy, skin_bottom_z - head_height / 2) * Cylinder(
                radius=head_diameter / 2 - 0.05, height=head_height)))
check(">=3.5mm open gap under the skin at all 4 holes", v_gap_max < TOL,
      f"worst hole hits {v_gap_max:.4f}mm3")
check(f"M3 head ({head_diameter}x{head_height}) fits at all 4 holes", v_head_max < TOL,
      f"worst hole hits {v_head_max:.4f}mm3")

# holes and slit break THROUGH the platform top: probes sitting just above the
# skin must come back clear (a blind hole leaves skin material in the probe)
v_top_max = 0
for sx in (1, -1):
    for sy in (1, -1):
        v_top_max = max(v_top_max, hit_volume(
            Pos(motor_x + sx * hole_xy, sy * hole_xy, skin_top_z + 0.5) * Cylinder(
                radius=motor_hole_diameter / 2 - 0.05, height=2)))
v_top_max = max(v_top_max, hit_volume(
    Pos(motor_x, 0, skin_top_z + 0.5) * Cylinder(radius=center_hole_diameter / 2 - 0.05,
                                                 height=2)))
v_top_max = max(v_top_max, hit_volume(
    Pos(slot_cx, 0, skin_top_z + 0.5) * Cylinder(
        radius=min(slot_len, cable_slot_width) / 2 - 0.5, height=2)))
check("holes, center hole and slit pierce the platform top", v_top_max < TOL,
      f"worst probe hits {v_top_max:.4f}mm3")

# (e) envelope: nothing anywhere below z=-env or above z=+env
span = part.bounding_box()
v_low = hit_volume(Pos((span.min.X + span.max.X) / 2, 0, -env - 1.5) * Box(
    span.max.X - span.min.X + 4, 4 * droplet_radius + 4, 3))
v_high = hit_volume(Pos((span.min.X + span.max.X) / 2, 0, env + 1.5) * Box(
    span.max.X - span.min.X + 4, 4 * droplet_radius + 4, 3))
check(f"nothing below z=-{env}", v_low < TOL, f"hits {v_low:.4f}mm3")
check(f"nothing above z=+{env}", v_high < TOL, f"hits {v_high:.4f}mm3")

if not all(checks):
    print("WARNING: geometry checks FAILED - inspect the part before printing")

# =============================================================================
# OUTPUT
# =============================================================================

bb = part.bounding_box()
print(f"mount: blind bore D{bore_diameter} x {insertion_depth}mm (D{rod_diameter} tube + "
      f"{rod_clearance} clearance), sleeve D{sleeve_diameter}, droplet "
      f"{2 * droplet_radius}mm across, overall x {bb.min.X:.1f}..{bb.max.X:.1f}mm")
print(f"platform: top at z=+{env} (flush with the arm hub top), skin {skin_thickness}mm, "
      f"4x D{motor_hole_diameter} on {motor_bcd}mm BCD at the 45 deg diagonals, "
      f"D{center_hole_diameter} center hole, cable slot {cable_slot_width}x{slot_len}mm "
      f"near the arm (x {cable_slot_x0}..{cable_slot_x1})")
print(f"leveling: 3x {foot_size}x{foot_size}mm feet, bottoms at z=-{env}; "
      f"raceway: slot -> cavity -> D{stop_hole_diameter} stop hole (funnel) -> tube")

# tag the output filename with the parameters that vary between test prints:
# motor_mount-<rod_diameter>-<rod_clearance>
tag = lambda v: str(v).replace(".", "")
out_name = f"motor_mount-{tag(rod_diameter)}-{tag(rod_clearance)}"
export_step(part, f"{out_name}.step")
export_stl(part, f"{out_name}.stl")
print(f"exported {out_name}.step / .stl")

try:
    from ocp_vscode import show

    show(part)
except Exception as e:
    print(f"(viewer not shown: {e})")
