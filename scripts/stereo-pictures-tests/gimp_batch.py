# Runs inside gimp-console (python-fu-eval): open the MPO, JPS and PNS pairs,
# check each eye layer's colour, export MPO and JPS back, and leave a 2D JPEG alone.
import os
from gi.repository import Gimp, Gio
W = "/K3D/temp/partners/queue/gimp-stereo"
out = open(W + "/evidence/gimp-batch.log", "w")
def say(s): out.write(s + "\n"); out.flush()
def colour(layer):
    c = layer.get_pixel(5, 5)
    r, g, b, a = c.get_rgba(); return "red" if r > b else "blue"
def check(name, cond): say(("PASS " if cond else "FAIL ") + name)
for f in ["pair.mpo", "pair-left-first.jps", "pair.pns"]:
    img = Gimp.file_load(Gimp.RunMode.NONINTERACTIVE, Gio.File.new_for_path(W + "/evidence/" + f))
    layers = img.get_layers(); names = [l.get_name() for l in layers]
    say("%s: %dx%d layers %s" % (f, img.get_width(), img.get_height(), names))
    check(f + " two eye layers", names == ["Left eye", "Right eye"])
    if len(layers) == 2:
        check(f + " Left eye is red", colour(layers[0]) == "red")
        check(f + " Right eye is blue", colour(layers[1]) == "blue")
        check(f + " each view 120x80", layers[0].get_width() == 120 and layers[0].get_height() == 80)
    if f == "pair.mpo":
        for ext in ["mpo", "jps", "pns"]:
            proc = Gimp.get_pdb().lookup_procedure("file-%s-export" % ext)
            cfg = proc.create_config(); cfg.set_property("run-mode", Gimp.RunMode.NONINTERACTIVE)
            cfg.set_property("image", img); cfg.set_property("file", Gio.File.new_for_path(W + "/evidence/gimp-out." + ext))
            if ext != "mpo": cfg.set_property("layout", "sideBySideLeftFirst")
            r = proc.run(cfg); check("export %s status %s" % (ext, r.index(0)), r.index(0) == Gimp.PDBStatusType.SUCCESS)
    img.delete()
img = Gimp.file_load(Gimp.RunMode.NONINTERACTIVE, Gio.File.new_for_path(W + "/evidence/flat.jpg"))
check("2D JPEG: one layer, %dx%d" % (img.get_width(), img.get_height()), len(img.get_layers()) == 1 and img.get_width() == 120)
img.delete(); say("DONE"); out.close()
# Stereo menu: swap, join, split; eyes checked after each
out = open(W + "/evidence/gimp-batch.log", "a")
img = Gimp.file_load(Gimp.RunMode.NONINTERACTIVE, Gio.File.new_for_path(W + "/evidence/pair.mpo"))
def run(name, **kw):
    proc = Gimp.get_pdb().lookup_procedure(name); cfg = proc.create_config()
    cfg.set_property("run-mode", Gimp.RunMode.NONINTERACTIVE); cfg.set_property("image", img)
    cfg.set_core_object_array("drawables", img.get_layers())
    for k, v in kw.items(): cfg.set_property(k, v)
    return proc.run(cfg).index(0)
def eyes(): return [(l.get_name(), colour(l), l.get_width(), l.get_height()) for l in img.get_layers()]
st = run("stereo-swap-eyes"); e = eyes(); say("after swap: %s %s" % (st, e))
check("swap: Left eye now blue, Right eye now red", e[0][:2] == ("Left eye", "blue") and e[1][:2] == ("Right eye", "red"))
st = run("stereo-swap-eyes"); e = eyes(); check("swap back: Left eye red", e[0][:2] == ("Left eye", "red"))
st = run("stereo-join", layout="sideBySideLeftFirst"); e = eyes(); say("after join: %s %s image %dx%d" % (st, e, img.get_width(), img.get_height()))
top = img.get_layers()[0]
check("join: pair layer 240x80 on top", top.get_width() == 240 and top.get_height() == 80 and img.get_width() == 240)
c = top.get_pixel(5, 5).get_rgba(); c2 = top.get_pixel(125, 5).get_rgba()
check("join: left half red, right half blue", c[0] > c[2] and c2[2] > c2[0])
img.set_selected_layers([top]); img.remove_layer(img.get_layers()[1]); img.remove_layer(img.get_layers()[1])
st = run("stereo-split", layout="sideBySideLeftFirst"); e = eyes(); say("after split: %s %s image %dx%d" % (st, e, img.get_width(), img.get_height()))
check("split: Left eye red, Right eye blue, 120x80", e[0] == ("Left eye", "red", 120, 80) and e[1] == ("Right eye", "blue", 120, 80))
img.delete(); say("DONE 2"); out.close()
