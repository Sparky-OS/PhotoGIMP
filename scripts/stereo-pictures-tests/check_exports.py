#!/usr/bin/env python3
# The files GIMP wrote, read back by a second program: marks and eyes.
import io, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".config", "GIMP", "3.0", "plug-ins", "stereo-pictures"))
import stereo_files as sf
from PIL import Image
fails = 0
def check(n, c):
    global fails; print(("PASS " if c else "FAIL ") + n); fails += 0 if c else 1
def dom(im):
    r, g, b = im.resize((1, 1), Image.BOX).getpixel((0, 0)); return "red" if r > b else "blue"
d = open("evidence/gimp-out.mpo", "rb").read(); v = sf.mpo_views(d)
check("gimp-out.mpo: two disparity frames", v is not None)
check("gimp-out.mpo: frame 0 red (left), frame 1 blue (right)", dom(Image.open(io.BytesIO(v[0]))) == "red" and dom(Image.open(io.BytesIO(v[1]))) == "blue")
pil = Image.open("evidence/gimp-out.mpo"); check("Pillow: MPO, 2 frames, 120x80", pil.format == "MPO" and pil.n_frames == 2 and pil.size == (120, 80))
d = open("evidence/gimp-out.jps", "rb").read(); check("gimp-out.jps: block says left first", sf.jps_read(d) == "sideBySideLeftFirst")
im = Image.open(io.BytesIO(d)); check("gimp-out.jps: 240x80, left red, right blue", im.size == (240, 80) and dom(im.crop((0, 0, 120, 80))) == "red" and dom(im.crop((120, 0, 240, 80))) == "blue")
d = open("evidence/gimp-out.pns", "rb").read(); check("gimp-out.pns: chunks %s" % sf.png_check(d)[:3], sf.png_check(d)[:2] == ["IHDR", "sTER"])
check("gimp-out.pns: sTER diverging", sf.png_ster_read(d) == "sideBySideLeftFirst")
im = Image.open(io.BytesIO(d)); check("gimp-out.pns: 240x80, left red, right blue", im.size == (240, 80) and dom(im.crop((0, 0, 120, 80))) == "red" and dom(im.crop((120, 0, 240, 80))) == "blue")
print("FAILURES:", fails); sys.exit(1 if fails else 0)
