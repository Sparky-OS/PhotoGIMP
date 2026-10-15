# Runs inside gimp-console: the automatic vertical estimate. A textured left view
# (a gradient with blocks), the right view the same picture shifted DOWN by dy
# rows (dy = 0, 3, -5, 11); after Align eyes vertically the Right eye layer's
# offset must be -dy exactly, so the overlapping rows are identical. A pair
# with no vertical shift must stay put (0).
from gi.repository import Gimp, Gegl
W = "/K3D/temp/partners/queue/gimp-stereo"
out = open(W + "/evidence/gimp-align.log", "w")
def say(s): out.write(s + "\n"); out.flush()
def check(name, cond): say(("PASS " if cond else "FAIL ") + name)
def run(img, name, **kw):
    proc = Gimp.get_pdb().lookup_procedure(name); cfg = proc.create_config()
    cfg.set_property("run-mode", Gimp.RunMode.NONINTERACTIVE); cfg.set_property("image", img)
    cfg.set_core_object_array("drawables", [img.get_layers()[0]])
    for k, v in kw.items(): cfg.set_property(k, v)
    return proc.run(cfg).index(0)
Wd, Hd = 160, 120
def texture(shift):
    # pixel (x,y) of the view = pattern at (x, y - shift): the right view shows the scene lower by `shift` rows
    px = bytearray()
    for y in range(Hd):
        for x in range(Wd):
            yy = y - shift
            v = (x * 7 + yy * 13) % 256
            if (x // 16 + yy // 16) % 3 == 0: v = 255 - v
            px += bytes((v, (v * 3) % 256, (255 - v), 255))
    return bytes(px)
def layer_with(img, name, px):
    l = Gimp.Layer.new(img, name, Wd, Hd, Gimp.ImageType.RGBA_IMAGE, 100.0, Gimp.LayerMode.NORMAL)
    img.insert_layer(l, None, len(img.get_layers()))
    l.get_buffer().set(Gegl.Rectangle.new(0, 0, Wd, Hd), "R'G'B'A u8", px); l.get_buffer().flush(); l.update(0, 0, Wd, Hd)
    return l
for dy in [0, 3, -5, 11]:
    img = Gimp.Image.new(Wd, Hd, Gimp.ImageBaseType.RGB)
    left = layer_with(img, "Left eye", texture(0)); right = layer_with(img, "Right eye", texture(dy))
    st = run(img, "stereo-align-vertical", search=16)
    off = right.get_offsets()
    oy = off[2] if len(off) == 3 else off[1]
    say("dy=%d: status %s, Right eye offsets %s" % (dy, st, tuple(off)))
    check("dy=%d: Right eye moved to y offset %d" % (dy, -dy), st == Gimp.PDBStatusType.SUCCESS and oy == -dy)
    img.delete()
say("DONE"); out.close()
