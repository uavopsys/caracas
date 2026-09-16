# Caracas

CAD project for a drone frame (carbon plate + printed arm hubs). Two toolchains
coexist: OpenSCAD (`.scad`, older) and Python/build123d (`.py`, current).

## Toolchain

- Use `python3.11` for the Python CAD scripts — it has `build123d`, `yaml`,
  and `matplotlib`. The default `python3` does **not** have these.
- Parts export `.step` and `.stl` headlessly; scripts also try to show the part
  in the ocp_vscode viewer (`python3.11 -m ocp_vscode`) and silently skip it if
  not running.
- matplotlib's 3D toolkit (`mplot3d`) is broken on this machine (mixed
  system/pip installs) — use 2D projection for STL previews instead.
- Scripts `os.chdir` to their own directory at startup; outputs land next to
  the script.

## Structure

- `cots/` — current work. Config-driven build123d scripts sharing
  `cots/config.yaml` (`arm_hub.py` and `plate.py` both read it, so the hub's
  corner-hole grid and the plate's anchor patterns stay in sync by
  construction). Exported parts are filename-tagged with the parameters that
  vary between test prints, e.g. `arm_hub-<rod_diameter>-<rod_clearance>-<bore_angle>.stl`.
- `mvp/` — earlier standalone build123d scripts (hardcoded parameters,
  superseded by `cots/`).
- Root `*.scad`, `*.stl`, `*.3mf` — legacy OpenSCAD versions; `libs/` holds
  OpenSCAD libraries (`jl_scad`, `eazl.scad`).

## Conventions

- Shared dimensions that more than one script must agree on live in
  `cots/config.yaml`; scripts compute derived values themselves. Don't
  hardcode a value in one script that another script needs to match.
- Docstrings at the top of each script document the part's intent and print
  settings (clearances, self-tapping pilots) — keep them in sync when
  parameters move to config or change.
