"""
Technical drawing generator - dimensioned A4 PDF for the machine shop.

Geometry comes from plate.step (run plate.py first), specs from config.yaml.
The shop gets: top view, overall dimensions, hole callout, and the
material/tolerance/finish notes they need for the quote.

Run: python3.11 drawing.py  ->  plate_drawing.pdf (+ .png preview)
"""

import os
from collections import Counter
from datetime import date
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import yaml
from build123d import *

os.chdir(Path(__file__).parent)  # outputs land next to this script

with open("config.yaml") as f:
    config = yaml.safe_load(f)
P = config["plate"]

source = import_step("plate.step")
top = source.faces().sort_by(Axis.Z)[-1]

def sample_wire(wire, n=24):
    """Approximate a wire as a polyline (n points per edge)."""
    pts = []
    for e in wire.edges():
        pts += [(e.position_at(t / n).X, e.position_at(t / n).Y) for t in range(n)]
    return pts

holes, cutouts = [], []
for w in top.inner_wires():
    if len(w.edges()) == 1 and w.edges()[0].geom_type == GeomType.CIRCLE:
        c = w.center()
        holes.append((c.X, c.Y, 2 * w.edges()[0].radius))
    else:
        cutouts.append(sample_wire(w))
outline = sample_wire(top.outer_wire())

# =============================================================================
# DRAWING
# =============================================================================

L, W = P["frame_length"], P["frame_width"]

fig = plt.figure(figsize=(11.69, 8.27))  # A4 landscape
ax = fig.add_axes([0.06, 0.24, 0.74, 0.68])
ax.set_aspect("equal")
ax.axis("off")

def plot_wire(pts):
    xs = [p[0] for p in pts] + [pts[0][0]]
    ys = [p[1] for p in pts] + [pts[0][1]]
    ax.plot(xs, ys, "k-", lw=1.2)

plot_wire(outline)
for c in cutouts:
    plot_wire(c)
for x, y, d in holes:
    ax.add_patch(plt.Circle((x, y), d / 2, fill=False, lw=0.9))
    ax.plot([x], [y], "k+", ms=3, mew=0.6)

ax.set_xlim(-L / 2 - 32, L / 2 + 45)
ax.set_ylim(-W / 2 - 32, W / 2 + 24)

# overall dimensions
ax.annotate("", xy=(-L / 2, -W / 2 - 12), xytext=(L / 2, -W / 2 - 12),
            arrowprops=dict(arrowstyle="<->", lw=0.8))
ax.text(0, -W / 2 - 15, f"{L:.0f}", ha="center", va="top", fontsize=9)
ax.annotate("", xy=(-L / 2 - 12, -W / 2), xytext=(-L / 2 - 12, W / 2),
            arrowprops=dict(arrowstyle="<->", lw=0.8))
ax.text(-L / 2 - 15, 0, f"{W:.0f}", ha="right", va="center", fontsize=9, rotation=90)

# hole callout (grouped by diameter)
counts = Counter(round(d, 2) for _, _, d in holes)
callout = "\n".join(f"{n}x \u2300{d:g} THRU" for d, n in sorted(counts.items()))
ax.text(L / 2 + 8, W / 2, callout, ha="left", va="top", fontsize=9)

# notes + title block
notes = "\n".join([
    "NOTES:",
    "1. MATERIAL: ALUMINIUM 6061-T6",
    f"2. THICKNESS: {P['plate_thickness']:g} mm",
    "3. ALL DIMENSIONS IN MM",
    "4. TOLERANCES: ISO 2768-mK",
    "5. DEBURR ALL EDGES",
    "6. SURFACE FINISH: Ra 3.2",
    "7. CUT GEOMETRY PER plate.dxf / plate.step",
])
fig.text(0.06, 0.17, notes, fontsize=8, va="top", family="monospace")
fig.text(0.82, 0.17,
         f"FRAME PLATE - OTC\n{date.today().isoformat()}\nSHEET 1/1",
         fontsize=8, va="top", family="monospace")

fig.savefig("plate_drawing.pdf")
fig.savefig("plate_drawing.png", dpi=150)
print(f"exported plate_drawing.pdf / .png ({len(holes)} holes, "
      f"{len(cutouts)} cutouts)")
