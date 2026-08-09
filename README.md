# Caracas — Drone Frame

Parametric drone frame model in OpenSCAD, built on the jl_scad project-box
library and BOSL2 (both bundled in `libs/` — no separate install needed).

## Layout

- `caracas.scad` — main model (frame body, arm supports, slice/export logic)
- `libs/` — bundled libraries (`jl_scad`, `BOSL2`, `eazl.scad`); see `libs/ATTRIBUTION.md`

## Rendering

OpenSCAD runs as a flatpak here (`org.openscad.OpenSCAD`, 2021.01):

```bash
# preview (fast, OpenCSG)
flatpak run org.openscad.OpenSCAD -o preview.png --imgsize=800,600 caracas.scad

# export STL (full CGAL render — slow at fine quality; coarsen while iterating)
flatpak run org.openscad.OpenSCAD -D '$fs=0.5' -D '$fa=6' -o caracas.stl caracas.scad
```

## Parts and slices

Top-level variables in `caracas.scad` (also exposed in the Customizer):

- `part` — `"all"` | `"bottom"` | `"middle"` | `"top"`: which frame slice to render
- `explode` — Z gap (mm) between slices in the `part="all"` view; `0` = assembled
- `z_bottom` / `z_middle` / `z_top` — slice heights; `frame_height` is derived
  from them plus `plate_thickness` and `frame_thickness`

Export a single slice for printing:

```bash
flatpak run org.openscad.OpenSCAD -D 'part="middle"' -o middle.stl caracas.scad
```
