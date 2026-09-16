"""
Standoff dimension drawing - calls out the 8 standoff hole positions (4
corner + 4 middle) with the spacings between them, for quick reference
during assembly/drilling.

Geometry comes from plate.step (run plate.py first) for the outline and the
full hole set (shown light gray for context); standoff coordinates are
computed straight from config.yaml the same way plate.py places them.

Run: python3.11 standoff_dimensions.py -> standoff_dimensions.pdf / .png
"""

import os
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
L, W = P["frame_length"], P["frame_width"]

source = import_step("plate.step")
top = source.faces().sort_by(Axis.Z)[-1]

def sample_wire(wire, n=24):
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

# ---- standoff coordinates, computed the same way plate.py places them ----
corner_y = W / 2 - P["corner_standoff_offset"]
middle_y = W / 2 - P["middle_standoff_edge_offset"]
corner_x = L / 2 - P["corner_standoff_offset"]
middle_x = P["middle_standoff_x"]

corners = [(sx * corner_x, sy * corner_y) for sx in (-1, 1) for sy in (-1, 1)]
middles = [(sx * middle_x, sy * middle_y) for sx in (-1, 1) for sy in (-1, 1)]

front_span = 2 * corner_y   # between the 2 corner standoffs at one end
side_span = 2 * middle_x    # between the 2 middle standoffs on one long side

# =============================================================================
# DRAWING
# =============================================================================

fig = plt.figure(figsize=(11.69, 8.27))  # A4 landscape
ax = fig.add_axes([0.06, 0.1, 0.88, 0.8])
ax.set_aspect("equal")
ax.axis("off")

def plot_wire(pts, **kw):
    xs = [p[0] for p in pts] + [pts[0][0]]
    ys = [p[1] for p in pts] + [pts[0][1]]
    ax.plot(xs, ys, **kw)

plot_wire(outline, color="0.3", lw=1.2)
for c in cutouts:
    plot_wire(c, color="0.75", lw=0.8)
for x, y, d in holes:
    ax.add_patch(plt.Circle((x, y), d / 2, fill=False, lw=0.7, color="0.75"))

# highlight the 8 standoffs
for x, y in corners + middles:
    ax.add_patch(plt.Circle((x, y), P["standoff_diameter"] / 2, fill=False,
                             lw=1.6, color="black"))
    ax.plot([x], [y], "k+", ms=4, mew=0.8)

def dim(p1, p2, offset, label, horizontal):
    """Dimension line offset perpendicular to the measured span."""
    if horizontal:
        y = offset
        ax.plot([p1[0], p1[0]], [p1[1], y], "k-", lw=0.5)
        ax.plot([p2[0], p2[0]], [p2[1], y], "k-", lw=0.5)
        ax.annotate("", xy=(p2[0], y), xytext=(p1[0], y),
                    arrowprops=dict(arrowstyle="<->", lw=0.9))
        ax.text((p1[0] + p2[0]) / 2, y, label, ha="center",
                va="bottom" if y > 0 else "top", fontsize=10,
                bbox=dict(fc="white", ec="none", pad=1))
    else:
        x = offset
        ax.plot([p1[0], x], [p1[1], p1[1]], "k-", lw=0.5)
        ax.plot([p2[0], x], [p2[1], p2[1]], "k-", lw=0.5)
        ax.annotate("", xy=(x, p2[1]), xytext=(x, p1[1]),
                    arrowprops=dict(arrowstyle="<->", lw=0.9))
        ax.text(x, (p1[1] + p2[1]) / 2, label, ha="left" if x > 0 else "right",
                va="center", fontsize=10, rotation=90,
                bbox=dict(fc="white", ec="none", pad=1))

# front span: between the 2 corner standoffs at the nose end (+X)
dim((corner_x, -corner_y), (corner_x, corner_y), corner_x + 14,
    f"{front_span:.0f}", horizontal=False)
# front span: same at the tail end (-X), shown for confirmation
dim((-corner_x, -corner_y), (-corner_x, corner_y), -corner_x - 14,
    f"{front_span:.0f}", horizontal=False)

# side span: between the 2 middle standoffs on the +Y (port) long edge
dim((-middle_x, middle_y), (middle_x, middle_y), middle_y + 12,
    f"{side_span:.0f}", horizontal=True)
# side span: same on the -Y (starboard) edge
dim((-middle_x, -middle_y), (middle_x, -middle_y), -middle_y - 12,
    f"{side_span:.0f}", horizontal=True)

# overall outline dims for reference
ax.annotate("", xy=(-L / 2, -W / 2 - 24), xytext=(L / 2, -W / 2 - 24),
            arrowprops=dict(arrowstyle="<->", lw=0.8, color="0.4"))
ax.text(0, -W / 2 - 27, f"{L:.0f}", ha="center", va="top", fontsize=8, color="0.4")

ax.set_xlim(-L / 2 - 35, L / 2 + 35)
ax.set_ylim(-W / 2 - 32, W / 2 + 26)
ax.set_title("Standoff spacing (8x M3, black) - other 24 holes gray for reference",
             fontsize=10)

fig.savefig("standoff_dimensions.pdf")
fig.savefig("standoff_dimensions.png", dpi=150)
print(f"front span (corner-to-corner, at each end): {front_span:.1f} mm")
print(f"side span (middle-to-middle, on each long edge): {side_span:.1f} mm")
print(f"corner standoff <-> middle standoff (same side): {corner_x - middle_x:.1f} mm")
print("exported standoff_dimensions.pdf / .png")
