# Runs inside gimp-console: does GIMP take the Tiling parasite the plug-in sets as
# a symmetry when the XCF is reopened? xcf-load.c (3.2.6, lines 829-856) removes
# the parasite from the image's list only when it deserialised into a symmetry
# and prints "Failed to deserialize symmetry parasite" otherwise. So: after save
# and load, the Tiling parasite must be gone and the plug-in's own parasites
# (edit mode, depth) must still be there. Control: a Tiling parasite with bad
# data must survive the reload as a parasite.
from gi.repository import Gimp, Gio
W = "/K3D/temp/partners/queue/gimp-stereo"
out = open(W + "/evidence/gimp-xcf.log", "w")
def say(s): out.write(s + "\n"); out.flush()
def check(name, cond): say(("PASS " if cond else "FAIL ") + name)
def run(img, name, **kw):
    proc = Gimp.get_pdb().lookup_procedure(name); cfg = proc.create_config()
    cfg.set_property("run-mode", Gimp.RunMode.NONINTERACTIVE); cfg.set_property("image", img)
    cfg.set_core_object_array("drawables", [img.get_layers()[0]])
    for k, v in kw.items(): cfg.set_property(k, v)
    return proc.run(cfg).index(0)
def text(img, name):
    p = img.get_parasite(name); return None if p is None else bytes(p.get_data()).rstrip(b"\0").decode()
for case, bad in [("good", False), ("bad-data control", True)]:
    img = Gimp.Image.new(240, 80, Gimp.ImageBaseType.RGB)
    layer = Gimp.Layer.new(img, "Stereo pair", 240, 80, Gimp.ImageType.RGBA_IMAGE, 100.0, Gimp.LayerMode.NORMAL)
    img.insert_layer(layer, None, 0); layer.fill(Gimp.FillType.WHITE)
    run(img, "stereo-edit-mode", mode="both-eyes", depth=12)
    if bad:
        img.attach_parasite(Gimp.Parasite.new("gimp-image-symmetry:GimpTiling", 1, b"(this is not a symmetry)"))
    say("%s: before save, tiling parasite: %r" % (case, text(img, "gimp-image-symmetry:GimpTiling")))
    path = W + "/evidence/modes-%s.xcf" % case.split()[0]
    Gimp.file_save(Gimp.RunMode.NONINTERACTIVE, img, Gio.File.new_for_path(path), None)
    img.delete()
    img2 = Gimp.file_load(Gimp.RunMode.NONINTERACTIVE, Gio.File.new_for_path(path))
    tiling = text(img2, "gimp-image-symmetry:GimpTiling")
    say("%s: after reload, tiling parasite: %r, edit-mode %r, depth %r, layers %s" % (case, tiling, text(img2, "stereo-pictures/edit-mode"), text(img2, "stereo-pictures/depth"), [l.get_name() for l in img2.get_layers()]))
    if bad:
        check("control: a bad Tiling parasite survives reload as a parasite", tiling is not None)
    else:
        check("good: the Tiling parasite was consumed into a symmetry on reload", tiling is None)
        check("good: edit mode and depth survive the XCF", text(img2, "stereo-pictures/edit-mode") == "both-eyes" and text(img2, "stereo-pictures/depth") == "12")
    img2.delete()
say("DONE"); out.close()
