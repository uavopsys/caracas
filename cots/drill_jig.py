"""
Drill jig generator - builds a drilling template from plate.step.

Imports the plate STEP, detects every through-hole (cylindrical faces
bounded by two full circles), and builds a skeleton jig:
  - an 8mm boss with a drill bore at each hole position
  - 5mm wide ribs connecting the bosses

Connection model:
  - minimum spanning tree over the hole positions (guarantees one connected
    body with the least material)
  - plus a rib between any two holes closer than link_max_distance
    (triangulates local clusters -> rigidity)

Run plate.py first, then this. Run with the ocp_vscode standalone viewer
(python3.11 -m ocp_vscode), or headless: exports drill_jig.step / .stl
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

# drill the bores LAST so ribs crossing the bosses don't plug them
for x, y, d in holes:
    jig -= Pos(x, y, jig_height / 2) * Cylinder(radius=(d + bore_clearance) / 2,
                                                height=jig_height + 2)

part = jig

# =============================================================================
# OUTPUT
# =============================================================================

print(f"jig: {len(holes)} bosses OD{boss_diameter} x {jig_height}mm, "
      f"rib width {rib_width}mm")
export_step(part, "drill_jig.step")
export_stl(part, "drill_jig.stl")
print("exported drill_jig.step / .stl")

try:
    from ocp_vscode import show

    show(part)
except Exception as e:
    print(f"(viewer not shown: {e})")
