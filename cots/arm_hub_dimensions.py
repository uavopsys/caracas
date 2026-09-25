"""
Arm hub dimension drawing - calls out the 4 arm-hub anchor patterns (2x2 M3
grids, one per corner) with the grid spacing and the center-to-center
distances between the hubs, for the canted-motor bar experiment.

Geometry comes from plate.step (run plate.py first) for the outline and the
full hole set (shown light gray for context); hub pattern coordinates are
computed straight from config.yaml the same way plate.py places them.

Run: python3.11 arm_hub_dimensions.py -> arm_hub_dimensions.pdf / .png
"""

import os
from math import cos, radians, sin
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

# ---- hub pattern coordinates, computed the same way plate.py places them ----
h = config["arm_hub"]["hole_grid"] / 2          # hole offset from pattern center
angle = 0                                       # pattern_angle_forward/aft = 0
reach = h * (cos(radians(angle)) + sin(radians(angle)))
hub_x = L / 2 - P["pattern_x"]                  # pattern center from plate center
hub_y = W / 2 - P["corner_standoff_offset"] - reach

centers = [(sx * hub_x, sy * hub_y) for sx in (-1, 1) for sy in (-1, 1)]
span_x = 2 * hub_x   # front hub <-> aft hub, same side
span_y = 2 * hub_y   # port hub <-> starboard hub, same end

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

# highlight the 16 hub holes + the 4 pattern centers
for cx, cy in centers:
    for dx in (-h, h):
        for dy in (-h, h):
            ax.add_patch(plt.Circle((cx + dx, cy + dy), P["screw_diameter"] / 2,
                                    fill=False, lw=1.6, color="black"))
    ax.plot([cx], [cy], "k+", ms=6, mew=1.0)

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

# hub-to-hub: front <-> aft on the port (+Y) side, center to center
dim((-hub_x, hub_y), (hub_x, hub_y), hub_y + 14, f"{span_x:.0f}", horizontal=True)
# hub-to-hub: port <-> starboard at the nose (+X) end, center to center
dim((hub_x, -hub_y), (hub_x, hub_y), hub_x + 14, f"{span_y:.0f}", horizontal=False)
# grid spacing within one pattern (nose-port hub)
dim((hub_x - h, hub_y + h), (hub_x + h, hub_y + h), hub_y + 14 + 10,
    f"{2 * h:.0f}", horizontal=True)

ax.set_xlim(-L / 2 - 30, L / 2 + 30)
ax.set_ylim(-W / 2 - 30, W / 2 + 30)
ax.set_title("Arm hub anchors (16x M3, black) - pattern centers marked +, "
             "other holes gray", fontsize=10)

fig.savefig("arm_hub_dimensions.pdf")
fig.savefig("arm_hub_dimensions.png", dpi=150)
print(f"hub pattern centers at (±{hub_x:.0f}, ±{hub_y:.0f})")
print(f"front <-> aft hub, center to center (each side): {span_x:.1f} mm")
print(f"port <-> starboard hub, center to center (each end): {span_y:.1f} mm")
print(f"hole grid within one pattern: {2 * h:.0f} mm")
print("exported arm_hub_dimensions.pdf / .png")
