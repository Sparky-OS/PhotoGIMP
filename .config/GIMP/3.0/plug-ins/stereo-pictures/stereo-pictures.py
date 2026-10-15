#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 Daniel Campos Ramos <Capitain_Jack@yahoo.com>
#
# Stereo pictures in GIMP 3: MPO, JPS and PNS open as one image with two
# layers, "Left eye" and "Right eye"; the same formats export from a pair of
# layers or a side-by-side canvas; a Stereo menu splits, joins and swaps eyes.
# The file formats are in stereo_files.py beside this plug-in; the layout
# names are those of the shared stereo library (Sparky-OS/stereo-layer).
#
# Sparky Stereo OS, Daniel Ramos's edition of SparkyLinux (by Paweł "pavroo"
# Pijanowski), shipped with PhotoGIMP.

import gettext
import io
import os
import sys

import gi

gi.require_version("Gimp", "3.0")
gi.require_version("Gegl", "0.4")
from gi.repository import Gegl, Gimp, GLib, GObject, Gio  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import stereo_files as sf  # noqa: E402

LEFT_EYE = "Left eye"
RIGHT_EYE = "Right eye"
LAYOUT_PARASITE = "stereo-pictures/layout"  # Stereo3DLayout text, persistent

# GIMP binds the domain for its C side; Python's gettext needs its own binding.
gettext.bindtextdomain("stereo-pictures", os.path.join(os.path.dirname(os.path.abspath(__file__)), "locale"))
gettext.textdomain("stereo-pictures")
_ = gettext.gettext


def _layer_bytes(layer, fmt, quality=95):
    """One layer encoded as JPEG or PNG through GIMP's own file plug-ins."""
    image = Gimp.Image.new(layer.get_width(), layer.get_height(), Gimp.ImageBaseType.RGB)
    copy = Gimp.Layer.new_from_drawable(layer, image)
    copy.set_offsets(0, 0)
    image.insert_layer(copy, None, 0)
    image.flatten()
    path = GLib.build_filenamev([GLib.get_tmp_dir(), "stereo-pictures-%d.%s" % (os.getpid(), fmt)])
    proc = Gimp.get_pdb().lookup_procedure("file-%s-export" % ("jpeg" if fmt == "jpg" else "png"))
    config = proc.create_config()
    config.set_property("run-mode", Gimp.RunMode.NONINTERACTIVE)
    config.set_property("image", image)
    config.set_property("file", Gio.File.new_for_path(path))
    if fmt == "jpg":
        config.set_property("quality", quality / 100.0)
    proc.run(config)
    image.delete()
    with open(path, "rb") as f:
        data = f.read()
    os.remove(path)
    return data


def _load_layer(image, data, name, fmt):
    path = GLib.build_filenamev([GLib.get_tmp_dir(), "stereo-pictures-%d-%s.%s" % (os.getpid(), name.replace(" ", "-"), fmt)])
    with open(path, "wb") as f:
        f.write(data)
    # The format's own loader, by name, so this plug-in's loaders are never
    # asked about the single views it writes out.
    proc = Gimp.get_pdb().lookup_procedure("file-%s-load" % ("jpeg" if fmt == "jpg" else "png"))
    config = proc.create_config()
    config.set_property("run-mode", Gimp.RunMode.NONINTERACTIVE)
    config.set_property("file", Gio.File.new_for_path(path))
    result = proc.run(config)
    os.remove(path)
    if result.index(0) != Gimp.PDBStatusType.SUCCESS:
        raise RuntimeError("could not load " + name)
    loaded = result.index(1)
    layer = Gimp.Layer.new_from_drawable(loaded.get_layers()[0], image)
    loaded.delete()
    layer.set_name(name)
    return layer


def _eye_layers(image):
    """(left, right) layers by name, else the two top layers in order."""
    layers = image.get_layers()
    left = next((l for l in layers if l.get_name() == LEFT_EYE), None)
    right = next((l for l in layers if l.get_name() == RIGHT_EYE), None)
    if left is None or right is None:
        if len(layers) < 2:
            return None
        left, right = layers[0], layers[1]
    return left, right


def _set_layout(image, layout):
    parasite = Gimp.Parasite.new(LAYOUT_PARASITE, Gimp.PARASITE_PERSISTENT, layout.encode())
    image.attach_parasite(parasite)


def _pair_image(left_data, right_data, fmt, layout):
    """One image, two layers: left eye at the top of the stack."""
    image = Gimp.Image.new(1, 1, Gimp.ImageBaseType.RGB)
    right = _load_layer(image, right_data, RIGHT_EYE, fmt)
    image.insert_layer(right, None, 0)
    left = _load_layer(image, left_data, LEFT_EYE, fmt)
    image.insert_layer(left, None, 0)
    image.resize(left.get_width(), left.get_height(), 0, 0)
    _set_layout(image, layout)
    return image


def _split_side_by_side(image, layer, layout):
    """Two eye layers from a side-by-side or top-and-bottom layer, by the layout."""
    w, h = layer.get_width(), layer.get_height()
    sbs = layout.startswith("sideBySide")
    vw, vh = (w // 2, h) if sbs else (w, h // 2)
    views = []
    for k in range(2):
        copy = Gimp.Layer.new_from_drawable(layer, image)
        image.insert_layer(copy, None, 0)
        ox, oy = (k * vw, 0) if sbs else (0, k * vh)
        copy.resize(vw, vh, -ox, -oy)
        copy.set_offsets(0, 0)
        views.append(copy)
    first, second = views
    left, right = (first, second) if layout.endswith("LeftFirst") else (second, first)
    left.set_name(LEFT_EYE)
    right.set_name(RIGHT_EYE)
    image.reorder_item(left, None, 0)
    image.reorder_item(right, None, 1)
    image.resize(vw, vh, 0, 0)
    _set_layout(image, layout)
    return left, right


def _join(image, left, right, layout):
    """One layer with both views in the layout's order."""
    w, h = left.get_width(), left.get_height()
    sbs = layout.startswith("sideBySide")
    joined = Gimp.Layer.new(image, _("Stereo pair"), w * 2 if sbs else w, h if sbs else h * 2, Gimp.ImageType.RGBA_IMAGE, 100.0, Gimp.LayerMode.NORMAL)
    image.insert_layer(joined, None, 0)
    first, second = (left, right) if layout.endswith("LeftFirst") else (right, left)
    for k, view in enumerate((first, second)):
        copy = Gimp.Layer.new_from_drawable(view, image)
        image.insert_layer(copy, None, 0)
        copy.set_offsets(k * w if sbs else 0, 0 if sbs else k * h)
        joined = image.merge_down(copy, Gimp.MergeType.CLIP_TO_BOTTOM_LAYER)
    joined.set_name(_("Stereo pair"))
    return joined


# ---------------------------------------------------------------- procedures

def load_mpo(procedure, run_mode, file, metadata, flags, config, data):
    with open(file.peek_path(), "rb") as f:
        raw = f.read()
    views = sf.mpo_views(raw)
    if views is None:
        return procedure.new_return_values(Gimp.PDBStatusType.EXECUTION_ERROR, GLib.Error(_("Not a stereo MPO: no pair of disparity frames")))
    image = _pair_image(views[0], views[1], "jpg", "mpo")
    return Gimp.ValueArray.new_from_values([GObject.Value(Gimp.PDBStatusType, Gimp.PDBStatusType.SUCCESS), GObject.Value(Gimp.Image, image)]), flags


def _load_packed(file, fmt, layout):
    """JPS or PNS: load the packed picture, then split it by its mark."""
    image = Gimp.Image.new(1, 1, Gimp.ImageBaseType.RGB)
    with open(file.peek_path(), "rb") as f:
        raw = f.read()
    layer = _load_layer(image, raw, _("Stereo pair"), fmt)
    image.insert_layer(layer, None, 0)
    image.resize(layer.get_width(), layer.get_height(), 0, 0)
    _split_side_by_side(image, layer, layout)
    image.remove_layer(layer)
    return image


def load_jps(procedure, run_mode, file, metadata, flags, config, data):
    with open(file.peek_path(), "rb") as f:
        raw = f.read()
    # The block when it is there; without one JPS is commonly cross-eyed
    # (right view first), a format fallback the user can override with Swap eyes.
    layout = sf.jps_read(raw) or sf.SIDE_BY_SIDE_RIGHT_FIRST
    if layout == sf.MONO:
        layout = sf.SIDE_BY_SIDE_RIGHT_FIRST
    image = _load_packed(file, "jpg", layout)
    return Gimp.ValueArray.new_from_values([GObject.Value(Gimp.PDBStatusType, Gimp.PDBStatusType.SUCCESS), GObject.Value(Gimp.Image, image)]), flags


def load_pns(procedure, run_mode, file, metadata, flags, config, data):
    with open(file.peek_path(), "rb") as f:
        raw = f.read()
    # sTER mode 1 is diverging (left first); mode 0 cross; no chunk: the .pns convention, cross.
    layout = sf.png_ster_read(raw) or sf.SIDE_BY_SIDE_RIGHT_FIRST
    image = _load_packed(file, "png", layout)
    return Gimp.ValueArray.new_from_values([GObject.Value(Gimp.PDBStatusType, Gimp.PDBStatusType.SUCCESS), GObject.Value(Gimp.Image, image)]), flags


def _views_for_export(image, layout_for_joined):
    eyes = _eye_layers(image)
    if eyes is None:
        # one layer: a packed canvas; split it by the chosen layout
        layer = image.get_layers()[0]
        eyes = _split_side_by_side(image, layer, layout_for_joined)
    return eyes


def export_mpo(procedure, run_mode, image, file, options, metadata, config, data):
    left, right = _views_for_export(image, sf.SIDE_BY_SIDE_LEFT_FIRST)
    quality = int(config.get_property("quality"))
    out = sf.mpo_write(_layer_bytes(left, "jpg", quality), _layer_bytes(right, "jpg", quality))
    with open(file.peek_path(), "wb") as f:
        f.write(out)
    return Gimp.ValueArray.new_from_values([GObject.Value(Gimp.PDBStatusType, Gimp.PDBStatusType.SUCCESS)])


def export_jps(procedure, run_mode, image, file, options, metadata, config, data):
    layout = config.get_property("layout")
    left, right = _views_for_export(image, layout)
    quality = int(config.get_property("quality"))
    joined = _join(image, left, right, layout)
    out = sf.jps_write(_layer_bytes(joined, "jpg", quality), layout)
    image.remove_layer(joined)
    with open(file.peek_path(), "wb") as f:
        f.write(out)
    return Gimp.ValueArray.new_from_values([GObject.Value(Gimp.PDBStatusType, Gimp.PDBStatusType.SUCCESS)])


def export_pns(procedure, run_mode, image, file, options, metadata, config, data):
    layout = config.get_property("layout")
    left, right = _views_for_export(image, layout)
    joined = _join(image, left, right, layout)
    out = sf.png_ster_write(_layer_bytes(joined, "png"), layout)
    image.remove_layer(joined)
    with open(file.peek_path(), "wb") as f:
        f.write(out)
    return Gimp.ValueArray.new_from_values([GObject.Value(Gimp.PDBStatusType, Gimp.PDBStatusType.SUCCESS)])


def stereo_split(procedure, run_mode, image, drawables, config, data):
    layout = config.get_property("layout")
    image.undo_group_start()
    _split_side_by_side(image, drawables[0], layout)
    image.remove_layer(drawables[0])
    image.undo_group_end()
    Gimp.displays_flush()
    return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())


def stereo_join(procedure, run_mode, image, drawables, config, data):
    eyes = _eye_layers(image)
    if eyes is None:
        return procedure.new_return_values(Gimp.PDBStatusType.CALLING_ERROR, GLib.Error(_("Two layers are needed: Left eye and Right eye")))
    layout = config.get_property("layout")
    image.undo_group_start()
    joined = _join(image, eyes[0], eyes[1], layout)
    w, h = joined.get_width(), joined.get_height()
    image.resize(w, h, 0, 0)
    image.undo_group_end()
    Gimp.displays_flush()
    return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())


def stereo_swap(procedure, run_mode, image, drawables, config, data):
    eyes = _eye_layers(image)
    if eyes is None:
        return procedure.new_return_values(Gimp.PDBStatusType.CALLING_ERROR, GLib.Error(_("Two layers are needed: Left eye and Right eye")))
    image.undo_group_start()
    eyes[0].set_name("stereo-swap")  # GIMP adds "#1" to a name still in use
    eyes[1].set_name(LEFT_EYE)
    eyes[0].set_name(RIGHT_EYE)
    image.reorder_item(eyes[1], None, 0)
    image.undo_group_end()
    Gimp.displays_flush()
    return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())


# ---------------------------------------------------------------- stereo editing modes
#
# Daniel (2026-10-14): two edit modes for a side-by-side picture. "Each eye on
# its own" is GIMP as it is, with a guide at the seam. "Both eyes alike" repeats
# an edit made in one view in the other view at the same place, shifted by the
# depth d: with the left view first, the repeat in the right view at +d pixels
# to the right is uncrossed disparity (behind the screen), a negative d brings
# it in front; 0 is the screen plane. d is the artist's setting, any whole
# number of pixels, no limits (a tool, not the desktop).
#
# Strokes: GIMP's Tiling symmetry (interval X = half the width + d, two strokes)
# repeats paint tools live. GIMP reads symmetry only from an XCF's parasites
# (app/xcf/xcf-load.c), so the parasite set here takes effect when the file is
# saved and reopened; until then the artist picks Tiling in Image > Symmetry
# Painting. Everything else (filters, fills, transforms, text, pasted layers)
# goes through "Apply to both eyes": the pixels that changed since the last
# apply, in either half, are copied into the other half at +d or -d.

MODE_PARASITE = "stereo-pictures/edit-mode"
DEPTH_PARASITE = "stereo-pictures/depth"
SNAPSHOT_PARASITE = "stereo-pictures/snapshot"
MODE_EACH_EYE = "each-eye"
MODE_BOTH_EYES = "both-eyes"


def _parasite_text(image, name):
    parasite = image.get_parasite(name)
    if parasite is None:
        return None
    data = bytes(parasite.get_data())
    return data.rstrip(b"\0").decode()


def _attach_text(image, name, text):
    image.attach_parasite(Gimp.Parasite.new(name, Gimp.PARASITE_PERSISTENT, text.encode()))


def _is_pair_canvas(image):
    """A side-by-side canvas: a stereo layout parasite says side by side, or the
    shape is a pair by the shared library's rule (2:1 to 3.6:1)."""
    layout = _parasite_text(image, LAYOUT_PARASITE)
    if layout:
        return layout.startswith("sideBySide")
    if _eye_layers(image) is not None and len(image.get_layers()) == 2:
        return False  # two eye layers: each eye is its own layer, no seam to mirror across
    w, h = image.get_width(), image.get_height()
    lib = sf._load_policy()
    if lib:
        return lib.stereo_policy_picture_pair_by_shape(w, h) == 1
    return 2.0 <= w / float(h) <= 3.6


def _tiling_parasite(image, interval_x):
    """The Tiling symmetry as GIMP serialises it (gimp_config_serialize_to_parasite,
    app/core/gimpsymmetry.c): read when the XCF is loaded."""
    text = "(active yes)\n(version 0)\n(interval-x %d.000000)\n(interval-y 0.000000)\n(shift 0.000000)\n(max-x 2)\n(max-y 1)\n" % interval_x
    image.attach_parasite(Gimp.Parasite.new("gimp-image-symmetry:GimpTiling", Gimp.PARASITE_PERSISTENT, text.encode()))


def _snapshot(image, layer):
    """A hidden copy of the layer, the reference "Apply to both eyes" diffs against."""
    old = _parasite_text(image, SNAPSHOT_PARASITE)
    for l in image.get_layers():
        if l.get_name() == "stereo-pictures snapshot":
            image.remove_layer(l)
    copy = Gimp.Layer.new_from_drawable(layer, image)
    image.insert_layer(copy, None, len(image.get_layers()))
    copy.set_name("stereo-pictures snapshot")
    copy.set_visible(False)
    copy.set_lock_content(True)
    return copy


def _depth_text(d):
    if d == 0:
        return _("d = 0 px: screen plane")
    if d > 0:
        return _("d = +%d px: behind the screen") % d
    return _("d = %d px: in front of the screen") % d


def stereo_edit_mode(procedure, run_mode, image, drawables, config, data):
    mode = config.get_property("mode")
    d = int(config.get_property("depth"))
    if not _is_pair_canvas(image):
        return procedure.new_return_values(Gimp.PDBStatusType.CALLING_ERROR, GLib.Error(_("Not a side-by-side picture: nothing to set")))
    image.undo_group_start()
    _attach_text(image, MODE_PARASITE, mode)
    _attach_text(image, DEPTH_PARASITE, str(d))
    half = image.get_width() // 2
    if not any(g == half for g in _vertical_guides(image)):
        image.add_vguide(half)
    if mode == MODE_BOTH_EYES:
        _tiling_parasite(image, half + d)
        _snapshot(image, drawables[0])
        Gimp.message(_("Both eyes alike. %s. Paint tools repeat live with Image > Symmetry Painting > Tiling (interval X %d, two strokes), or after the file is saved and reopened; everything else: Stereo > Apply to both eyes.") % (_depth_text(d), half + d))
    else:
        parasite = image.get_parasite("gimp-image-symmetry:GimpTiling")
        if parasite is not None:
            image.detach_parasite("gimp-image-symmetry:GimpTiling")
        for l in image.get_layers():
            if l.get_name() == "stereo-pictures snapshot":
                image.remove_layer(l)
    image.undo_group_end()
    Gimp.displays_flush()
    return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())


def _vertical_guides(image):
    guides = []
    g = image.find_next_guide(0)
    while g:
        if image.get_guide_orientation(g) == Gimp.OrientationType.VERTICAL:
            guides.append(image.get_guide_position(g))
        g = image.find_next_guide(g)
    return guides


def _read_rgba(layer):
    buf = layer.get_buffer()
    rect = Gegl.Rectangle.new(0, 0, layer.get_width(), layer.get_height())
    return bytes(buf.get(rect, 1.0, "R'G'B'A u8", Gegl.AbyssPolicy.NONE))


def stereo_apply_both(procedure, run_mode, image, drawables, config, data):
    if _parasite_text(image, MODE_PARASITE) != MODE_BOTH_EYES:
        return procedure.new_return_values(Gimp.PDBStatusType.CALLING_ERROR, GLib.Error(_("Stereo editing is not set to Both eyes alike")))
    d = int(_parasite_text(image, DEPTH_PARASITE) or "0")
    layer = drawables[0]
    snapshot = next((l for l in image.get_layers() if l.get_name() == "stereo-pictures snapshot"), None)
    if snapshot is None:
        return procedure.new_return_values(Gimp.PDBStatusType.CALLING_ERROR, GLib.Error(_("No snapshot to compare with: set Both eyes alike first")))
    w, h = layer.get_width(), layer.get_height()
    half = w // 2
    now = bytearray(_read_rgba(layer))
    before = _read_rgba(snapshot)
    stride = w * 4
    changed = 0
    out = bytearray(now)
    for y in range(h):
        row = y * stride
        for x in range(w):
            i = row + x * 4
            if now[i:i + 4] != before[i:i + 4]:
                # the other view: the right half at +d, the left half at -d
                tx = x + half + d if x < half else x - half - d
                if 0 <= tx < w and (tx >= half) == (x < half):
                    j = row + tx * 4
                    out[j:j + 4] = now[i:i + 4]
                    changed += 1
    image.undo_group_start()
    buf = layer.get_buffer()
    rect = Gegl.Rectangle.new(0, 0, w, h)
    buf.set(rect, "R'G'B'A u8", bytes(out))
    buf.flush()
    layer.update(0, 0, w, h)
    snapshot.set_lock_content(False)
    sbuf = snapshot.get_buffer()
    sbuf.set(rect, "R'G'B'A u8", bytes(out))
    sbuf.flush()
    snapshot.set_lock_content(True)
    image.undo_group_end()
    Gimp.displays_flush()
    Gimp.message(_("%d changed pixels repeated in the other eye (%s)") % (changed, _depth_text(d)))
    return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())


# ---------------------------------------------------------------- align: automatic vertical estimate
#
# Vertical disparity is a defect (the eyes cannot fuse it); a pair from two
# cameras can carry a few rows of it. The estimate finds the vertical shift of
# the right view that best matches the left one (least sum of absolute grey
# differences over the central region, coarse at quarter size, then refined at
# full size), and moves the Right eye layer by it. Rotation and fine work stay
# with GIMP's own tools: set the Right eye layer to Difference mode and use
# Move and Rotate with a live view of the mismatch.

def _grey_rows(layer, x0, y0, w, h):
    buf = layer.get_buffer()
    data = bytes(buf.get(Gegl.Rectangle.new(x0, y0, w, h), 1.0, "Y' u8", Gegl.AbyssPolicy.CLAMP))
    return [data[r * w:(r + 1) * w] for r in range(h)]


def _best_shift(left_rows, right_rows, search):
    """The dy with the least sum of absolute differences; right row y+dy against left row y."""
    h = len(left_rows)
    best = (None, 0)
    for dy in range(-search, search + 1):
        total = 0
        rows = 0
        for y in range(max(0, -dy), min(h, h - dy)):
            l, r = left_rows[y], right_rows[y + dy]
            total += sum(abs(a - b) for a, b in zip(l, r))
            rows += 1
        if rows:
            score = total / rows
            if best[0] is None or score < best[0]:
                best = (score, dy)
    return best[1]


def stereo_align_vertical(procedure, run_mode, image, drawables, config, data):
    eyes = _eye_layers(image)
    if eyes is None:
        return procedure.new_return_values(Gimp.PDBStatusType.CALLING_ERROR, GLib.Error(_("Two layers are needed: Left eye and Right eye")))
    left, right = eyes
    w, h = left.get_width(), left.get_height()
    search = max(2, int(config.get_property("search")))
    # central region: half the width and height, where the subject usually is
    cx, cy, cw, ch = w // 4, h // 4, w // 2, h // 2
    coarse = max(1, min(cw, ch) // 64)  # about 64 rows at the coarse pass
    lc = _grey_rows(left, cx, cy, cw, ch)[::coarse]
    rc = _grey_rows(right, cx, cy, cw, ch)[::coarse]
    lc = [row[::coarse] for row in lc]
    rc = [row[::coarse] for row in rc]
    dy = _best_shift(lc, rc, max(1, search // coarse)) * coarse
    if coarse > 1:
        lf = _grey_rows(left, cx, cy, cw, ch)
        rf = _grey_rows(right, cx, cy + dy, cw, ch)
        dy += _best_shift(lf, rf, coarse)
    image.undo_group_start()
    ox, oy = right.get_offsets()[1:] if len(right.get_offsets()) == 3 else right.get_offsets()
    right.set_offsets(ox, oy - dy)
    _attach_text(image, "stereo-pictures/vertical-offset", str(dy))
    image.undo_group_end()
    Gimp.displays_flush()
    Gimp.message(_("Right eye moved by %d px vertically") % (-dy))
    return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())


LAYOUT_CHOICES = [
    (sf.SIDE_BY_SIDE_LEFT_FIRST, "Side by side, left eye first"),
    (sf.SIDE_BY_SIDE_RIGHT_FIRST, "Side by side, right eye first (cross-eyed)"),
    (sf.TOP_BOTTOM_LEFT_FIRST, "Top and bottom, left eye on top"),
    (sf.TOP_BOTTOM_RIGHT_FIRST, "Top and bottom, right eye on top"),
]


def _layout_choice(default):
    choice = Gimp.Choice.new()
    for k, (value, label) in enumerate(LAYOUT_CHOICES):
        choice.add(value, k, _(label), "")
    return choice


class StereoPictures(Gimp.PlugIn):
    def do_set_i18n(self, procname):
        return True, "stereo-pictures", "locale"

    def do_query_procedures(self):
        return ["file-mpo-load", "file-mpo-export", "file-jps-load", "file-jps-export", "file-pns-load", "file-pns-export",
                "stereo-split", "stereo-join", "stereo-swap-eyes", "stereo-edit-mode", "stereo-apply-both-eyes", "stereo-align-vertical"]

    def do_create_procedure(self, name):
        if name == "file-mpo-load":
            procedure = Gimp.LoadProcedure.new(self, name, Gimp.PDBProcType.PLUGIN, load_mpo, None)
            procedure.set_menu_label(_("Stereo MPO picture"))
            procedure.set_documentation(_("Load a stereo MPO (CIPA DC-007) as Left eye and Right eye layers"), None, name)
            procedure.set_mime_types("image/x-mpo")
            procedure.set_extensions("mpo")
        elif name == "file-jps-load":
            procedure = Gimp.LoadProcedure.new(self, name, Gimp.PDBProcType.PLUGIN, load_jps, None)
            procedure.set_menu_label(_("Stereo JPS picture"))
            procedure.set_documentation(_("Load a JPS (side-by-side JPEG) as Left eye and Right eye layers"), None, name)
            procedure.set_mime_types("image/x-jps")
            procedure.set_extensions("jps")
        elif name == "file-pns-load":
            procedure = Gimp.LoadProcedure.new(self, name, Gimp.PDBProcType.PLUGIN, load_pns, None)
            procedure.set_menu_label(_("Stereo PNS picture"))
            procedure.set_documentation(_("Load a PNS (side-by-side PNG with the sTER chunk) as Left eye and Right eye layers"), None, name)
            procedure.set_mime_types("image/x-pns")
            procedure.set_extensions("pns")
        elif name in ("file-mpo-export", "file-jps-export", "file-pns-export"):
            fmt = name.split("-")[1]
            run = {"mpo": export_mpo, "jps": export_jps, "pns": export_pns}[fmt]
            procedure = Gimp.ExportProcedure.new(self, name, Gimp.PDBProcType.PLUGIN, False, run, None)
            procedure.set_image_types("*")
            procedure.set_menu_label(_("Stereo %s picture") % fmt.upper())
            procedure.set_documentation(_("Export the Left eye and Right eye layers as a stereo %s file") % fmt.upper(), None, name)
            procedure.set_extensions(fmt)
            if fmt != "pns":
                procedure.add_int_argument("quality", _("Quality"), _("JPEG quality"), 0, 100, 95, GObject.ParamFlags.READWRITE)
            if fmt != "mpo":
                default = sf.SIDE_BY_SIDE_RIGHT_FIRST  # the common order of JPS and PNS files
                procedure.add_choice_argument("layout", _("Layout"), _("Which view comes first in the file"), _layout_choice(default), default, GObject.ParamFlags.READWRITE)
        else:
            run = {"stereo-split": stereo_split, "stereo-join": stereo_join, "stereo-swap-eyes": stereo_swap,
                   "stereo-edit-mode": stereo_edit_mode, "stereo-apply-both-eyes": stereo_apply_both,
                   "stereo-align-vertical": stereo_align_vertical}[name]
            procedure = Gimp.ImageProcedure.new(self, name, Gimp.PDBProcType.PLUGIN, run, None)
            procedure.set_image_types("*")
            procedure.set_sensitivity_mask(Gimp.ProcedureSensitivityMask.DRAWABLE | Gimp.ProcedureSensitivityMask.DRAWABLES)
            if name == "stereo-split":
                procedure.set_menu_label(_("Split into eye layers"))
                procedure.set_documentation(_("Split a side-by-side or top-and-bottom layer into Left eye and Right eye layers"), None, name)
                procedure.add_choice_argument("layout", _("Layout"), _("How the views are packed in the layer"), _layout_choice(sf.SIDE_BY_SIDE_LEFT_FIRST), sf.SIDE_BY_SIDE_LEFT_FIRST, GObject.ParamFlags.READWRITE)
            elif name == "stereo-join":
                procedure.set_menu_label(_("Join eye layers into a pair"))
                procedure.set_documentation(_("Join the Left eye and Right eye layers into one side-by-side or top-and-bottom layer"), None, name)
                procedure.add_choice_argument("layout", _("Layout"), _("How to pack the views"), _layout_choice(sf.SIDE_BY_SIDE_LEFT_FIRST), sf.SIDE_BY_SIDE_LEFT_FIRST, GObject.ParamFlags.READWRITE)
            elif name == "stereo-swap-eyes":
                procedure.set_menu_label(_("Swap eyes"))
                procedure.set_documentation(_("Exchange the Left eye and Right eye layers"), None, name)
            elif name == "stereo-edit-mode":
                procedure.set_menu_label(_("Stereo editing..."))
                procedure.set_documentation(_("Each eye on its own, or both eyes alike: an edit in one view repeated in the other at the depth d"), None, name)
                mode = Gimp.Choice.new()
                mode.add(MODE_EACH_EYE, 0, _("Each eye on its own"), "")
                mode.add(MODE_BOTH_EYES, 1, _("Both eyes alike"), "")
                procedure.add_choice_argument("mode", _("Mode"), _("How edits apply to the two views"), mode, MODE_EACH_EYE, GObject.ParamFlags.READWRITE)
                procedure.add_int_argument("depth", _("Depth d (px)"), _("Shift of the repeat in the right view, in pixels: positive is behind the screen, negative in front, 0 the screen plane; no limits"),
                                           -GLib.MAXINT32, GLib.MAXINT32, 0, GObject.ParamFlags.READWRITE)
            elif name == "stereo-apply-both-eyes":
                procedure.set_menu_label(_("Apply to both eyes"))
                procedure.set_documentation(_("Repeat what changed in one view in the other view at the depth d"), None, name)
            else:
                procedure.set_menu_label(_("Align eyes vertically (automatic)"))
                procedure.set_documentation(_("Estimate the vertical offset between the Left eye and Right eye layers and move the Right eye by it"), None, name)
                procedure.add_int_argument("search", _("Search range (px)"), _("Largest vertical offset to look for, in pixels"), 1, 4096, 32, GObject.ParamFlags.READWRITE)
            procedure.add_menu_path("<Image>/Stereo/")
        procedure.set_attribution("Daniel Campos Ramos", "Sparky Stereo OS", "2026")
        return procedure


Gimp.main(StereoPictures.__gtype__, sys.argv)
