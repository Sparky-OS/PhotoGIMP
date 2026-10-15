#!/usr/bin/env python3
# Both-view checks for stereo_files: the shared library's fixtures, round trips
# of our own LEFT/RIGHT pair in MPO, JPS and PNS, and a 2D picture left alone.
import io, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".config", "GIMP", "3.0", "plug-ins", "stereo-pictures"))
import stereo_files as sf
from PIL import Image, ImageDraw

FIX = "/K3D/GitHub/stereo-layer/autotests/readers"
fails = 0
def check(name, cond, extra=""):
    global fails
    print(("PASS " if cond else "FAIL ") + name + (" " + str(extra) if extra else ""))
    if not cond: fails += 1

lib = sf._load_policy()
check("libstereo-policy loaded (ctypes)", bool(lib), lib)
for v, want in [("sideBySideLeftFirst", "sideBySideLeftFirst"), ("sideBySideRightFirst", "sideBySideRightFirst"),
                ("topBottomLeftFirst", "topBottomLeftFirst"), ("topBottomRightFirst", "topBottomRightFirst"),
                ("mono", None), ("checkerboardLeftFirst", None), ("garbage", None)]:
    check("read_mark %s -> %s" % (v, want), sf.read_mark(v) == want, sf.read_mark(v))

# the shared library's JPS fixtures (picturetest.cpp: 2_0 right first, 2_1 left first)
check("fixture jps_2_0 right first", sf.jps_read(open(FIX + "/test_jps_2_0.jpg", "rb").read()) == "sideBySideRightFirst")
check("fixture jps_2_1 left first", sf.jps_read(open(FIX + "/test_jps_2_1.jpg", "rb").read()) == "sideBySideLeftFirst")
check("fixture jps_unmarked has no block", sf.jps_read(open(FIX + "/test_jps_unmarked.jps", "rb").read()) is None)
for f in ["test_mpo_1_0", "test_mpo_1_1", "test_mpo_0_0", "test_mpo_0_1", "test_mpo_unknown", "test_mpo_equal"]:
    d = open(FIX + "/" + f + ".mpo", "rb").read()
    frames = sf.mpo_read(d)
    types = [t for _, t, _ in frames]
    v = sf.mpo_views(d)
    check("fixture %s: 2 frames, types %s, pair=%s" % (f, ["0x%06x" % t for t in types], v is not None), len(frames) == 2)
    if v:
        for k, fr in enumerate(v):
            im = Image.open(io.BytesIO(fr)); check("  frame %d decodes %s" % (k, im.size), im.size == (16, 16))
for f in ["test_mpo_composite", "test_mpo_multangle"]:
    d = open(FIX + "/" + f + ".mpo", "rb").read()
    check("fixture %s is not a pair (types %s)" % (f, ["0x%08x" % a for _, _, a in sf.mpo_read(d)]), sf.mpo_views(d) is None)

# our own pair: LEFT red with text, RIGHT blue with text
def view(text, color):
    im = Image.new("RGB", (120, 80), color); ImageDraw.Draw(im).text((10, 30), text, fill="white"); return im
L, R = view("LEFT", (200, 0, 0)), view("RIGHT", (0, 0, 200))
def jpeg(im):
    b = io.BytesIO(); im.save(b, "JPEG", quality=95); return b.getvalue()
def dom(im):
    r, g, b = im.resize((1, 1), Image.BOX).getpixel((0, 0)); return "red" if r > b else "blue"

mpo = sf.mpo_write(jpeg(L), jpeg(R)); open("evidence/pair.mpo", "wb").write(mpo)
l, r = sf.mpo_views(mpo)
check("mpo round trip: left frame identical once its MPF segment is stripped", sf.strip_mpf(l) == jpeg(L))
check("mpo round trip: right frame identical once its MPF segment is stripped", sf.strip_mpf(r) == jpeg(R))
pil = Image.open(io.BytesIO(mpo)); check("Pillow sees MPO with 2 frames", pil.format == "MPO" and pil.n_frames == 2, (pil.format, getattr(pil, "n_frames", 1)))
pil.seek(0); check("Pillow frame 0 is LEFT (red)", dom(pil.convert("RGB")) == "red"); pil.seek(1); check("Pillow frame 1 is RIGHT (blue)", dom(pil.convert("RGB")) == "blue")

sbs = Image.new("RGB", (240, 80)); sbs.paste(L, (0, 0)); sbs.paste(R, (120, 0))
jps = sf.jps_write(jpeg(sbs), sf.SIDE_BY_SIDE_LEFT_FIRST); open("evidence/pair-left-first.jps", "wb").write(jps)
check("jps block reads back left first", sf.jps_read(jps) == "sideBySideLeftFirst", sf.jps_read(jps))
im = Image.open(io.BytesIO(jps)); check("jps still decodes 240x80", im.size == (240, 80))
check("jps left half red, right half blue", dom(im.crop((0, 0, 120, 80))) == "red" and dom(im.crop((120, 0, 240, 80))) == "blue")
jps2 = sf.jps_write(jps, sf.SIDE_BY_SIDE_RIGHT_FIRST); check("jps block replaced, right first", sf.jps_read(jps2) == "sideBySideRightFirst" and jps2.count(b"_JPSJPS_") == 1)
tb = sf.jps_write(jpeg(sbs), sf.TOP_BOTTOM_LEFT_FIRST); check("jps over/under code", sf.jps_read(tb) == "topBottomLeftFirst")

b = io.BytesIO(); sbs.save(b, "PNG"); pns = sf.png_ster_write(b.getvalue()); open("evidence/pair.pns", "wb").write(pns)
names = sf.png_check(pns); check("pns chunk order IHDR sTER ... IDAT ... IEND, CRCs valid", names[:2] == ["IHDR", "sTER"] and "IDAT" in names, names)
check("pns sTER reads diverging (left first)", sf.png_ster_read(pns) == "sideBySideLeftFirst")
im = Image.open(io.BytesIO(pns)); check("pns decodes, left red right blue", im.size == (240, 80) and dom(im.crop((0, 0, 120, 80))) == "red" and dom(im.crop((120, 0, 240, 80))) == "blue")
check("pns padded width rule: 120 -> 120, 121 -> 128", sf.ster_padded_width(120) == 120 and sf.ster_padded_width(121) == 128)
pns2 = sf.png_ster_write(pns, sf.SIDE_BY_SIDE_RIGHT_FIRST); check("pns sTER replaced once (cross)", sf.png_ster_read(pns2) == "sideBySideRightFirst" and pns2.count(b"sTER") == 1)

# a 2D picture: no mark found, nothing changed
flat = jpeg(L); check("2D JPEG: no JPS block, no MPF", sf.jps_read(flat) is None)
try: sf.mpo_read(flat); check("2D JPEG rejected by mpo_read", False)
except ValueError: check("2D JPEG rejected by mpo_read", True)
b = io.BytesIO(); L.save(b, "PNG"); check("2D PNG: no sTER", sf.png_ster_read(b.getvalue()) is None)
print("FAILURES:", fails); sys.exit(1 if fails else 0)
