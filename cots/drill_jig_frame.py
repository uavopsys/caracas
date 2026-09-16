"""
Drill jig with alignment frame - like drill_jig.py, plus a perimeter rim
whose OUTER face is the plate's cut line: the jig footprint equals the plate
outline (minus rim_clearance), so you rough-cut the carbon oversized, clamp
the jig on it, and cut/sand the frame flush to the jig edge.

The outline is detected from the plate STEP, so it follows the plate's
own parameters (size, corner rounding). Footprint = outline - rim_clearance.

Run plate.py first, then this. Run with the ocp_vscode standalone viewer
(python3.11 -m ocp_vscode), or headless: exports drill_jig_frame.step / .stl
next to this file.
"""

import os
from math import atan2, degrees, dist
from pathlib import Path

from build123d import *

os.chdir(Path(__file__).parent)  # outputs land next to this script

# =============================================================================
# PARAMETERS
# =============================================================================

source_step = "plate.step"

boss_diameter = 8        # cylinder around each hole (the drill guide)
jig_height = 8           # height of bosses and ribs
rib_width = 5            # connector width (4-5mm)
link_max_distance = 35   # extra ribs between holes closer than this (triangulation)
bore_clearance = 0.0     # add to detected hole diameter for the drill bore

# ---- perimeter alignment frame ----
rim = True
rim_clearance = 0.3      # jig undersize: rim outer face is this far inside the plate edge
rim_wall = 4             # rim wall thickness (extends inward)
rim_height = 6           # rim height (>= plate thickness to work as a guide)
rim_link_max = 20        # connect bosses to the rim when closer than this

# =============================================================================
# HOLE DETECTION — a through-hole is a cylindrical face bounded by two FULL
# circles (seam lines from the STEP export are ignored; rounded-corner
# fillets are partial arcs and are skipped)
# =============================================================================

source = import_step(source_step)

holes = []  # (x, y, diameter)
for face in source.faces():
    if face.geom_type != GeomType.CYLINDER:
        continue
    circles = [e for e in face.edges() if e.geom_type == GeomType.CIRCLE]
    if len(circles) == 2 and all(e.is_closed for e in circles):
        c = face.center()
        holes.append((c.X, c.Y, 2 * circles[0].radius))

print(f"detected {len(holes)} holes in {source_step}")
if not holes:
    raise SystemExit("no holes found - check source_step")

# =============================================================================
# CONNECTION GRAPH — MST backbone + short-range triangulation ribs
# =============================================================================

points = [(x, y) for x, y, _ in holes]

def mst_edges(pts):
    """Prim's algorithm: edges connecting all points with minimum total length."""
    in_tree = {0}
    edges = set()
    while len(in_tree) < len(pts):
        _, i, j = min(
            (dist(pts[a], pts[b]), a, b)
            for a in in_tree
            for b in range(len(pts))
            if b not in in_tree
        )
        edges.add((min(i, j), max(i, j)))
        in_tree.add(j)
    return edges

edges = mst_edges(points)
for i in range(len(points)):
    for j in range(i + 1, len(points)):
        if dist(points[i], points[j]) <= link_max_distance:
            edges.add((i, j))

print(f"connecting with {len(edges)} ribs")

# =============================================================================
# JIG BODY
# =============================================================================

jig = None
for x, y, d in holes:
    boss = Pos(x, y, jig_height / 2) * Cylinder(radius=boss_diameter / 2,
                                                height=jig_height)
    jig = boss if jig is None else jig + boss

for i, j in edges:
    (x1, y1), (x2, y2) = points[i], points[j]
    length = dist((x1, y1), (x2, y2))
    angle = degrees(atan2(y2 - y1, x2 - x1))
    rib = Pos((x1 + x2) / 2, (y1 + y2) / 2, jig_height / 2) * Rot(0, 0, angle) * Box(
        length, rib_width, jig_height
    )
    jig += rib

# ---- perimeter rim: wall INSIDE the plate outline, so the jig's outer face
#      is the plate's cut line (template for cutting/sanding the frame flush)
if rim:
    outline = source.faces().sort_by(Axis.Z)[-1].outer_wire()
    outline_face = Face(outline)
    rim_2d = (offset(outline_face, -rim_clearance)
              - offset(outline_face, -(rim_clearance + rim_wall)))
    # the outline wire sits at the plate's top-face z; bring the rim to z=0
    jig += Pos(0, 0, -outline.center().Z) * extrude(rim_2d, amount=rim_height)

    # bridge nearby bosses to the rim so it is one body with the skeleton
    obb = outline.bounding_box()
    hx, hy = obb.size.X / 2, obb.size.Y / 2
    for px, py in points:
        q = min(((hx, py), (-hx, py), (px, hy), (px, -hy)),
                key=lambda q: dist((px, py), q))
        d = dist((px, py), q)
        if d <= rim_link_max:
            length = d - rim_clearance  # reach the rim outer face, not past it
            if length <= 0:
                continue
            angle = degrees(atan2(q[1] - py, q[0] - px))
            mid = (px + (q[0] - px) / d * length / 2,
                   py + (q[1] - py) / d * length / 2)
            jig += Pos(mid[0], mid[1], jig_height / 2) * Rot(0, 0, angle) * Box(
                length, rib_width, jig_height
            )

# drill the bores LAST so ribs crossing the bosses don't plug them
for x, y, d in holes:
    jig -= Pos(x, y, jig_height / 2) * Cylinder(radius=(d + bore_clearance) / 2,
                                                height=jig_height + 2)

# clamp the whole jig to the cut line: nothing may stick out past the rim's
# outer face (boolean fuzz from concentric arcs can otherwise leave slivers)
if rim:
    jig &= Pos(0, 0, -outline.center().Z) * extrude(
        offset(outline_face, -rim_clearance), amount=100)

part = jig

# =============================================================================
# OUTPUT
# =============================================================================

print(f"jig: {len(holes)} bosses OD{boss_diameter} x {jig_height}mm, "
      f"rib width {rib_width}mm")
if rim:
    print(f"rim: wall {rim_wall}mm x {rim_height}mm, clearance {rim_clearance}mm")
export_step(part, "drill_jig_frame.step")
export_stl(part, "drill_jig_frame.stl")
print("exported drill_jig_frame.step / .stl")

try:
    from ocp_vscode import show

    show(part)
except Exception as e:
    print(f"(viewer not shown: {e})")
