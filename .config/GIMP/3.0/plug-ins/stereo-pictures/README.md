# Stereo pictures for GIMP 3

A Python plug-in that opens and saves stereo photographs as a pair of layers, "Left eye" and "Right eye".

- **Open:** MPO (the twin-lens camera format, CIPA DC-007), JPS (side-by-side JPEG with the `_JPSJPS_` block) and PNS (side-by-side PNG with the `sTER` chunk, PNG extensions 1.4.0 section 3.6).
- **Export:** the same three formats, each with its own stereo mark, so other programs know which view is which.
- **Stereo menu:** Split into eye layers, Join eye layers into a pair, Swap eyes.

A JPS or PNS without a mark is read as cross-eyed (right view first), the common order of such files; Swap eyes corrects a file whose order was guessed wrong.
Layout names follow the shared stereo library of Sparky Stereo OS (`libstereo-policy`, used through ctypes when installed).

Strings: en, pl, pt_BR, fr, ja, ko, zh_CN, zh_TW (`locale/`); rebuild the catalogues with `scripts/stereo-pictures-tests/build_catalogs.py`.
Tests: `scripts/stereo-pictures-tests/` (pure Python checks against fixtures, and a `gimp-console` batch run).

Written for Sparky Stereo OS, Daniel Ramos's edition of SparkyLinux (by Paweł "pavroo" Pijanowski), to ship with PhotoGIMP. GPL-3.0-or-later.
The MPO writer follows `bravia_mpo.py` from sony-bravia-linux (Daniel Campos Ramos, GPL-2.0); Daniel Ramos is the author of both, and the licence of this copy is his to state.

## Stereo editing (side-by-side pictures)

Stereo > Stereo editing... offers two modes for a side-by-side canvas (Daniel Ramos, 2026-10-14):

- **Each eye on its own** (default): GIMP as it is, with a guide at the seam.
- **Both eyes alike:** an edit made in one view is repeated in the other view at the same place, shifted by the depth d.
  Paint tools repeat live through GIMP's own Symmetry Painting, Tiling, with interval X = half the width + d and two strokes; the plug-in stores that symmetry in the file, and GIMP applies it when the XCF is reopened (GIMP reads symmetry settings only on load, `app/xcf/xcf-load.c`).
  Everything else (filters, fills, transforms, text, pasted layers) is repeated by Stereo > Apply to both eyes: the pixels that changed since the mode was set, or since the last apply, are copied into the other view at +d (right view) or −d (left view).

**Depth d** is the artist's setting, in whole pixels, with no limits: with the left view first, a positive d puts the painted thing behind the screen (uncrossed disparity), a negative d in front, 0 on the screen plane.
The value and the mode are kept with the image (persistent parasites), and GIMP remembers the last values of the dialog.
