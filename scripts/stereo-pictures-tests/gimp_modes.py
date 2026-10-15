# Runs inside gimp-console (python-fu-eval): Daniel's two edit modes on a 240x80
# side-by-side canvas. Mode 2 with a red 10x10 square painted in the left half at
# (30,20): after Apply to both eyes the square must appear in the right half at
# (30+120+d, 20) and nowhere else; d = 0, +4, -4, +40, -40, +100 (beyond the
# desktop's comfort range; part falls off the canvas and is dropped). Mode 1:
# apply refuses and the right half stays white. A 2D 120x80 image: mode refuses,
# 0 differing pixels.
from gi.repository import Gimp, Gegl, GLib
W = "/K3D/temp/partners/queue/gimp-stereo"
out = open(W + "/evidence/gimp-modes.log", "w")
def say(s): out.write(s + "\n"); out.flush()
def check(name, cond): say(("PASS " if cond else "FAIL ") + name)
def run(img, name, **kw):
    proc = Gimp.get_pdb().lookup_procedure(name); cfg = proc.create_config()
    cfg.set_property("run-mode", Gimp.RunMode.NONINTERACTIVE); cfg.set_property("image", img)
    cfg.set_core_object_array("drawables", [img.get_layers()[0]])
    for k, v in kw.items(): cfg.set_property(k, v)
    return proc.run(cfg).index(0)
def rgba(layer):
    buf = layer.get_buffer(); r = Gegl.Rectangle.new(0, 0, layer.get_width(), layer.get_height())
    return bytes(buf.get(r, 1.0, "R'G'B'A u8", Gegl.AbyssPolicy.NONE))
def paint(layer, x, y, size, colour):
    buf = layer.get_buffer(); r = Gegl.Rectangle.new(x, y, size, size)
    buf.set(r, "R'G'B'A u8", bytes(colour) * (size * size)); buf.flush(); layer.update(x, y, size, size)
def red_pixels(px, w, h):
    s = set()
    for y in range(h):
        for x in range(w):
            i = (y * w + x) * 4
            if px[i] > 200 and px[i + 2] < 50: s.add((x, y))
    return s
def canvas():
    img = Gimp.Image.new(240, 80, Gimp.ImageBaseType.RGB)
    layer = Gimp.Layer.new(img, "Stereo pair", 240, 80, Gimp.ImageType.RGBA_IMAGE, 100.0, Gimp.LayerMode.NORMAL)
    img.insert_layer(layer, None, 0); layer.fill(Gimp.FillType.WHITE)
    return img, layer
RED = (255, 0, 0, 255)
for d in [0, 4, -4, 40, -40, 100]:
    img, layer = canvas()
    st = run(img, "stereo-edit-mode", mode="both-eyes", depth=d)
    check("d=%d: edit mode set (status %s)" % (d, st), st == Gimp.PDBStatusType.SUCCESS)
    paint(layer, 30, 20, 10, RED)
    st = run(img, "stereo-apply-both-eyes")
    px = rgba(layer); reds = red_pixels(px, 240, 80)
    expected = {(x, y) for y in range(20, 30) for x in range(30, 40)}
    tx = 30 + 120 + d
    expected |= {(x, y) for y in range(20, 30) for x in range(tx, tx + 10) if 120 <= x < 240}
    say("d=%d: apply status %s, red pixels %d, expected %d, right-half red x range %s" % (d, st, len(reds), len(expected), sorted({x for x, y in reds if x >= 120})[:1] + sorted({x for x, y in reds if x >= 120})[-1:]))
    check("d=%d: red exactly at left (30..39) and right (%d..%d), nothing else" % (d, tx, tx + 9), reds == expected)
    if d in (0, 4):
        # proof pair: the canvas as the plug-in left it, full side by side, left view first
        from gi.repository import Gio
        Gimp.file_save(Gimp.RunMode.NONINTERACTIVE, img, Gio.File.new_for_path(W + "/evidence/proof/both-eyes-d%d.png" % d), None)
    img.delete()
# mode 1: each eye on its own
img, layer = canvas()
st = run(img, "stereo-edit-mode", mode="each-eye", depth=0)
paint(layer, 30, 20, 10, RED)
st = run(img, "stereo-apply-both-eyes"); reds = red_pixels(rgba(layer), 240, 80)
check("each eye: apply refuses (status %s) and only the left square is red (%d px)" % (st, len(reds)), st != Gimp.PDBStatusType.SUCCESS and reds == {(x, y) for y in range(20, 30) for x in range(30, 40)})
check("each eye: a guide at the seam x=120", 120 in [img.get_guide_position(g) for g in [img.find_next_guide(0)] if g])
img.delete()
# a 2D image: nothing happens
img = Gimp.Image.new(120, 80, Gimp.ImageBaseType.RGB)
layer = Gimp.Layer.new(img, "Background", 120, 80, Gimp.ImageType.RGBA_IMAGE, 100.0, Gimp.LayerMode.NORMAL)
img.insert_layer(layer, None, 0); layer.fill(Gimp.FillType.WHITE); before = rgba(layer)
st = run(img, "stereo-edit-mode", mode="both-eyes", depth=4)
check("2D image: edit mode refuses (status %s), 0 differing pixels, no snapshot layer, no guide" % st,
      st != Gimp.PDBStatusType.SUCCESS and rgba(layer) == before and len(img.get_layers()) == 1 and img.find_next_guide(0) == 0)
img.delete(); say("DONE"); out.close()
