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
The MPO writer follows `bravia_mpo.py` from sony-bravia-linux (Daniel Campos Ramos, GPL-2.0).
