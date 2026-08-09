# Bundled Third-Party Libraries

The `libs/` folder bundles open-source OpenSCAD libraries used by the Caracas models. They are included here so you can render any SCAD file in this repo without installing the libraries separately.

## BOSL2

**Version:** bundled snapshot (see upstream for current release)
**Source:** https://github.com/BelfrySCAD/BOSL2
**License:** BSD 2-Clause License
**Authors:** Revar Desmera and contributors

The Belfry OpenScad Library (v2) — advanced geometry, attachments, paths, rounding, and more. Bundled inside `libs/jl_scad/BOSL2`.

## jl_scad

**Source:** https://github.com/jeffsch/jl_scad_project_box
**License:** MIT License (see `libs/jl_scad/LICENSE`)
**Authors:** Jeff Schöning and contributors

Project-box utilities used by SkyRelay-style enclosures. Depends on BOSL2.

## eazl

**Source:** https://github.com/aynacorp/eazl (internal utility)
**License:** CC-BY-SA 4.0 (matches this repo)
**Authors:** UAVOPSYS

Small helper library: `holder()`, `standoff()`, and friends used across multiple UAV mounts.

---

No changes have been made to the bundled upstream libraries. If you fork and update, please respect each library's license.
