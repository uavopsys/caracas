"""
GPS/compass holder - arc band spanning the two corner standoffs on one short
side of the frame, bowing outward away from the drone to carry the
GPS/compass clear of the electronics.

Geometry (all shared values from config.yaml):
- span = plate frame_width - 2*corner_standoff_offset (80mm): the chord
  between the two corner standoffs on one short end of the plate.
- reach (60mm): how far the arc apex bows out from the chord midpoint.
  With reach > chord/2 the band is a major arc (>180 deg, a big "C").
- height = arm_hub size_height (22mm): the standoff stack height, so the
  band fills the gap between the bottom and top plates.
- thickness (3mm): radial thickness of the band.
- Each end has a boss bored at standoff_diameter + standoff_clearance
  (5.2mm) to slip over the round standoff posts.
- twist_angle (deg): the wall twists at the apex like twist_arm.py, each
  section rotating about its TOP-OUTER corner. The outer side wall sweeps up
  to become the top surface, so at 90 deg the far end lies flat with its top
  face exactly in the Z=height plane (flush with the top plate) - a spoiler
  blade extending outward, height wide x thickness tall, still anchored
  vertical at the standoffs. The twist ramps in and back out over twist_span
  of the arc (max 1/3, half on each side of the flat region), holding the
  full angle over flat_span of the arc at the apex. twist_angle=0 gives the
  plain vertical wall. Note: with twist the part leaves the Z=0 plane in the
  twist/flat zones - it needs supports to print as oriented.

Orientation: chord along Y centered at the origin, apex bowing toward +X,
base at Z=0 (sitting on the bottom plate). Print flat on the bed.

Run with the ocp_vscode standalone viewer running (python3.11 -m ocp_vscode),
or headless: exports gps_holder-<standoff_diameter>-<reach>-<thickness>.step/.stl
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

cfg = config["gps_holder"]
plate = config["plate"]
arm_hub = config["arm_hub"]

standoff_diameter = cfg["standoff_diameter"]    # round standoff post OD
standoff_clearance = cfg["standoff_clearance"]  # slip fit over the post
reach = cfg["reach"]                            # apex distance from chord midpoint
thickness = cfg["thickness"]                    # radial band thickness
twist_angle = cfg["twist_angle"]                # wall twist at the apex (deg from vertical)
twist_span = cfg["twist_span"]                  # arc fraction for both twist ramps together
flat_span = cfg["flat_span"]                    # arc fraction held flat (full twist) at the apex

span = plate["frame_width"] - 2 * plate["corner_standoff_offset"]  # chord
height = arm_hub["size_height"]                 # standoff stack height

# =============================================================================
# ARC GEOMETRY
# =============================================================================
# Chord along Y from (0, -span/2) to (0, +span/2), apex bowing to +X.
# Circle through both standoff points with sagitta = reach.

half_span = span / 2
radius = (reach**2 + half_span**2) / (2 * reach)
cx = reach - radius  # circle center x (apex side of the chord when reach > radius)

# half-angle (at the circle center) of the chord endpoints, measured from +X.
# The endpoints sit past +-90 deg when reach > chord/2, so the arc through
# the apex is the major arc sweeping 2*a (>180 deg, a big "C").
a = math.degrees(math.atan2(half_span, -cx))
arc_sweep = 2 * a

r_out = radius + thickness / 2
r_in = radius - thickness / 2

boss_radius = standoff_diameter / 2 + thickness
bore_diameter = standoff_diameter + standoff_clearance

print(f"arc: span {span}mm, reach {reach}mm -> R{radius:.2f}mm, "
      f"sweep {arc_sweep:.1f} deg, band {r_in:.2f}-{r_out:.2f}mm")

# =============================================================================
# PART
# =============================================================================

# Twist profile along the arc: f is the arc fraction (0 and 1 at the standoff
# ends, 0.5 at the apex). The wall is vertical at the ends; the twist ramps in
# and back out over twist_span of the arc (half each side, cosine-eased) and
# holds the full angle over flat_span of the arc around the apex.
ramp = twist_span / 2
hold = flat_span / 2
if twist_span + flat_span > 1:
    print(f"WARNING: twist_span + flat_span = {twist_span + flat_span:.2f} > 1 - "
          f"the ramps overlap the standoff ends")


def twist_at(f):
    d = abs(f - 0.5)
    if d <= hold:
        return twist_angle
    if d >= hold + ramp:
        return 0.0
    u = 1 - (d - hold) / ramp
    return twist_angle * (1 - math.cos(math.pi * u)) / 2


# Loft stations: every ~3 deg along the arc, plus the exact profile
# breakpoints (ramp start, flat start, apex, ...) so the loft tracks the twist.
arc_len = radius * math.radians(arc_sweep)
fracs = {i / round(arc_sweep / 3) for i in range(round(arc_sweep / 3) + 1)}
fracs |= {0.5 - hold - ramp, 0.5 - hold, 0.5, 0.5 + hold, 0.5 + hold + ramp}


def section_sketch(f):
    """Rectangle (thickness x height) perpendicular to the arc tangent at arc
    fraction f, rotated by the twist angle about its TOP-OUTER corner. The
    outer side wall sweeps up to become the top surface, so at 90 deg the
    blade lies flat with its top face exactly in the Z=height plane (nothing
    pokes above it into the top plate), extending outward - the spoiler
    blade. Local x is the outward radial direction, local y is +Z."""
    ang = math.radians(a - arc_sweep * f)  # arc angle at this station
    px, py = cx + radius * math.cos(ang), radius * math.sin(ang)
    phi = math.radians(twist_at(f))
    cp, sp = math.cos(phi), math.sin(phi)
    t2 = thickness / 2

    def rot(u, v):  # rotate section point about the top-outer corner (t2, height)
        du, dv = u - t2, v - height
        return (t2 + du * cp - dv * sp, height + du * sp + dv * cp)

    plane = Plane(origin=(px, py, 0),
                  x_dir=(math.cos(ang), math.sin(ang), 0),
                  z_dir=(math.sin(ang), -math.cos(ang), 0))
    return plane * Polygon(rot(-t2, 0), rot(t2, 0), rot(t2, height),
                           rot(-t2, height), align=None)


part = loft(sections=[section_sketch(f) for f in sorted(fracs)], ruled=True)

# end bosses over the standoff posts (at the chord endpoints)
for y in (-half_span, half_span):
    part += Pos(0, y, height / 2) * Cylinder(radius=boss_radius, height=height)
    part -= Pos(0, y, height / 2) * Cylinder(radius=bore_diameter / 2, height=height + 4)

# =============================================================================
# OUTPUT
# =============================================================================

bb = part.bounding_box()
print(f"holder: {span}mm span, apex at x={bb.max.X:.1f}mm, "
      f"{height}mm tall, band {thickness}mm thick, "
      f"2x bores D{bore_diameter} for D{standoff_diameter} standoffs")
if twist_angle:
    print(f"twist: {twist_angle} deg at the apex (section rotates about its top-outer "
          f"edge; at 90 the far end lies flat in the Z={height} plane, extending "
          f"{height}mm outward), ramps over {twist_span * 100:.0f}% of the arc, "
          f"flat over {flat_span * 100:.0f}%")

# tag the output filename with the parameters that vary between test prints:
# gps_holder-<standoff_diameter>-<reach>-<thickness>-t<twist_angle>
tag = lambda v: str(v).replace(".", "")
out_name = f"gps_holder-{tag(standoff_diameter)}-{tag(reach)}-{tag(thickness)}-t{tag(twist_angle)}"
export_step(part, f"{out_name}.step")
export_stl(part, f"{out_name}.stl")
print(f"exported {out_name}.step / .stl")

try:
    from ocp_vscode import show

    show(part)
except Exception as e:
    print(f"(viewer not shown: {e})")
