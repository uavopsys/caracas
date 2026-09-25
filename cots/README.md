# Caracas build123d parts

This folder contains the current Python/build123d CAD models. Running a part
script exports its generated files (`.stl`, `.step`, and, for some scripts,
`.dxf`) into this folder.

## First-time setup

Python 3.11 is required. From this folder, run:

```bash
./setup.sh
source .venv/bin/activate
```

The first command creates a local `.venv` and installs the versions in
`requirements.txt`. The second command activates it for the current shell.
Repeat only the `source` command when opening a new shell.

If `setup.sh` is not executable after copying the project, run it as:

```bash
bash setup.sh
```

## Generate parts

With the virtual environment active, run any part script directly:

```bash
python arm_hub.py
python plate.py
python motor_mount.py
python canopy.py
```

For example, `python plate.py` creates `plate.step`, `plate.stl`, and
`plate.dxf`. Parameter-tagged models such as the arm hub and motor mount put
their dimensions in the output filename. Shared dimensions are read from
`config.yaml`.

Activation is optional if you call the virtual-environment interpreter
explicitly:

```bash
.venv/bin/python arm_hub.py
```

The optional 3D viewer can be started in a second terminal after activation:

```bash
python -m ocp_vscode
```

The exports are still produced when the viewer is not running. The drawing
scripts (`drawing.py` and `standoff_dimensions.py`) create documentation
images/PDFs rather than STL/STEP parts.

