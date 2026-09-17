"""
Camera holder - sleeve for the DJI O4 Wide camera: a tunnel
holder_width x holder_height running straight through a holder_depth body,
open front and back, M2 side-hole pairs (16 mm spacing).

Standalone part - the canopy no longer carries the camera; the sleeve
mounts separately.

Print: PETG, on a side face or front face - open tunnel, no supports.

Run with the ocp_vscode standalone viewer running (python3.11 -m ocp_vscode),
or headless: exports camera_holder.step / .stl next to this file.
Tunnel axis along X (front toward +X), width along Y, height along Z.
"""

import os
from pathlib import Path

import yaml
from build123d import *


def sleeve_sketch(w, h, radius):
    with BuildSketch(Plane.YZ) as s:
        rect = Rectangle(w, h)
        if radius > 0:
            fillet(rect.vertices(), radius=radius)
    return s.sketch


def build_sleeve(h):
    """The holder sleeve from a config['camera_holder'] dict. Centered at
    the origin, tunnel along X, camera front face toward +X."""
    out_w = h["holder_width"] + 2 * h["wall"]
    out_h = h["holder_height"] + 2 * h["wall"]

    outer = extrude(sleeve_sketch(out_w, out_h, h["rounding"]),
                    amount=h["holder_depth"])
    # inner corners stay sharp - the camera body is square-cornered
    inner = extrude(sleeve_sketch(h["holder_width"], h["holder_height"], 0),
                    amount=h["holder_depth"] + 2)
    part = Pos(-h["holder_depth"] / 2, 0, 0) * (outer - inner)

    # camera holes: horizontal (Y), piercing the side walls into the tunnel.
    # Pair stacked vertically hole_spacing apart, centered hole_z, fixed at
    # holes_from_front from the sleeve's front face.
    hole_y = h["holder_width"] / 2 + h["wall"] / 2
    hole_x = h["holder_depth"] / 2 - h["holes_from_front"]
    for sy in (-1, 1):
        for sz in (-1, 1):
            part -= Pos(hole_x, sy * hole_y,
                        h["hole_z"] + sz * h["hole_spacing"] / 2
                        ) * Rot(90, 0, 0) * Cylinder(
                            radius=h["hole_diameter"] / 2, height=h["wall"] + 2)
    return part


if __name__ == "__main__":
    os.chdir(Path(__file__).parent)  # outputs land next to this script
    with open("config.yaml") as f:
        config = yaml.safe_load(f)
    h = config["camera_holder"]

    part = build_sleeve(h)

    print(f"camera holder: tunnel {h['holder_width']} x {h['holder_height']} x "
          f"{h['holder_depth']}, outer {h['holder_width'] + 2 * h['wall']} x "
          f"{h['holder_height'] + 2 * h['wall']} x {h['holder_depth']}, "
          f"wall {h['wall']}")
    print(f"M{h['hole_diameter']:g} side holes: pairs at "
          f"y +/-{h['holder_width'] / 2 + h['wall'] / 2:.2f}, "
          f"spaced {h['hole_spacing']:g} vertically, centered z {h['hole_z']:g}")
    export_step(part, "camera_holder.step")
    export_stl(part, "camera_holder.stl")
    print(f"volume {part.volume / 1000:.1f} cm3 -> "
          f"~{part.volume / 1000 * 1.27:.1f} g PETG")
    print("exported camera_holder.step / .stl")

    try:
        from ocp_vscode import show

        show(part)
    except Exception as e:
        print(f"(viewer not shown: {e})")
