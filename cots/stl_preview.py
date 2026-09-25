"""
Quick STL preview - 2D wireframe projections (top XY + side XZ) of an STL,
saved as a PNG. matplotlib's mplot3d is broken on this machine, so this uses
plain 2D projection.

Run: python3.11 stl_preview.py some_part.stl  ->  some_part_preview.png
"""

import struct
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

stl_path = Path(sys.argv[1])
out_path = stl_path.with_name(stl_path.stem + "_preview.png")

def load_binary_stl(path):
    data = path.read_bytes()
    n = struct.unpack("<I", data[80:84])[0]
    tris = np.frombuffer(data, dtype=np.dtype([
        ("n", "<f4", 3), ("v", "<f4", (3, 3)), ("attr", "<u2")]),
        count=n, offset=84)
    return tris["v"].astype(np.float64)

tris = load_binary_stl(stl_path)

fig, axes = plt.subplots(2, 1, figsize=(14, 8))
for ax, (a, b, title) in zip(axes, [(0, 1, "top (XY)"), (0, 2, "side (XZ)")]):
    for t in tris:
        xs = [t[0][a], t[1][a], t[2][a], t[0][a]]
        ys = [t[0][b], t[1][b], t[2][b], t[0][b]]
        ax.plot(xs, ys, "k-", lw=0.1)
    ax.set_aspect("equal")
    ax.set_title(title, fontsize=9)
    ax.set_xlabel("x [mm]")
    ax.set_ylabel("y [mm]" if b == 1 else "z [mm]")

fig.suptitle(stl_path.name, fontsize=10)
fig.tight_layout()
fig.savefig(out_path, dpi=150)
print(f"exported {out_path}")
