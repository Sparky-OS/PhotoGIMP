# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 Daniel Campos Ramos <Capitain_Jack@yahoo.com>
#
# Stereo picture files without GIMP: MPO (CIPA DC-007), JPS (the _JPSJPS_
# block in APP3) and PNG with the sTER chunk (PNG extensions 1.4.0, 3.6).
# The MPO writer follows sony-bravia-linux's bravia_mpo.py (GPL-2.0, Daniel
# Campos Ramos), which both BRAVIA sets accepted as a 3D still.
#
# Layout names are the Stereo3DLayout values of the shared stereo library
# (Sparky-OS/stereo-layer, libstereo-policy): "sideBySideLeftFirst",
# "sideBySideRightFirst", "topBottomLeftFirst", "topBottomRightFirst",
# "mono". When libstereo-policy is installed, read_mark() asks it; the
# small table below is the fallback and the test checks both agree.

import ctypes
import ctypes.util
import struct
import zlib

SIDE_BY_SIDE_LEFT_FIRST = "sideBySideLeftFirst"
SIDE_BY_SIDE_RIGHT_FIRST = "sideBySideRightFirst"
TOP_BOTTOM_LEFT_FIRST = "topBottomLeftFirst"
TOP_BOTTOM_RIGHT_FIRST = "topBottomRightFirst"
MONO = "mono"

# libstereo-policy enum values (stereo-policy.h)
_POLICY_LAYOUT = {1: "sideBySide", 2: "topBottom"}
_POLICY_ORDER = {0: "LeftFirst", 1: "RightFirst"}

_policy = None


def _load_policy():
    global _policy
    if _policy is None:
        name = ctypes.util.find_library("stereo-policy")
        try:
            _policy = ctypes.CDLL(name or "libstereo-policy.so.1")
        except OSError:
            _policy = False
    return _policy


def read_mark(value):
    """A Stereo3DLayout text to (layout, order) or None, through
    libstereo-policy when it is there, so every program decides alike."""
    lib = _load_policy()
    if lib:
        layout = ctypes.c_int()
        order = ctypes.c_int()
        anaglyph = ctypes.c_int()
        ok = lib.stereo_policy_read_mark(value.encode(), ctypes.byref(layout), ctypes.byref(order), ctypes.byref(anaglyph))
        if ok != 1 or layout.value not in _POLICY_LAYOUT:
            return None
        return _POLICY_LAYOUT[layout.value] + _POLICY_ORDER[order.value]
    if value in (SIDE_BY_SIDE_LEFT_FIRST, SIDE_BY_SIDE_RIGHT_FIRST, TOP_BOTTOM_LEFT_FIRST, TOP_BOTTOM_RIGHT_FIRST):
        return value
    return None


# ---------------------------------------------------------------- JPEG segments

def _segments(data):
    """Yield (marker, start, end) for the segments before the scan data."""
    if data[:2] != b"\xff\xd8":
        raise ValueError("not a JPEG (no SOI)")
    i = 2
    while i + 4 <= len(data) and data[i] == 0xFF:
        marker = data[i + 1]
        if marker == 0xDA:  # SOS: entropy coded data follows
            return
        length = struct.unpack(">H", data[i + 2:i + 4])[0]
        yield marker, i, i + 2 + length
        i += 2 + length


def _insert_point(data):
    """After SOI and any APP0/APP1, where the spec expects a new APPn."""
    i = 2
    for marker, start, end in _segments(data):
        if marker in (0xE0, 0xE1):
            i = end
        else:
            break
    return i


# ---------------------------------------------------------------- JPS

# Stereoscopic descriptor, 32 bits big endian: separation, flags, layout, media.
JPS_MEDIA_STEREO = 0x01
JPS_LAYOUT_INTERLEAVED = 0x01
JPS_LAYOUT_SIDE_BY_SIDE = 0x02
JPS_LAYOUT_OVER_UNDER = 0x03
JPS_LAYOUT_ANAGLYPH = 0x04
JPS_FLAG_HALF_HEIGHT = 0x01
JPS_FLAG_HALF_WIDTH = 0x02
JPS_FLAG_LEFT_FIRST = 0x04


def jps_read(data):
    """The layout a JPS block states, or None when the file has none.
    Without a block, JPS files are commonly cross-eyed (right view first);
    the caller applies that fallback so the user can override it."""
    for marker, start, end in _segments(data):
        if marker == 0xE3 and data[start + 4:start + 12] == b"_JPSJPS_":
            desc_len = struct.unpack(">H", data[start + 12:start + 14])[0]
            if desc_len < 4:
                return None
            separation, flags, layout, media = data[start + 14:start + 18]
            if media != JPS_MEDIA_STEREO:
                return MONO
            order = "LeftFirst" if flags & JPS_FLAG_LEFT_FIRST else "RightFirst"
            if layout == JPS_LAYOUT_SIDE_BY_SIDE:
                return "sideBySide" + order
            if layout == JPS_LAYOUT_OVER_UNDER:
                return "topBottom" + order
            return None
    return None


def jps_block(layout):
    flags = 0
    if layout.endswith("LeftFirst"):
        flags |= JPS_FLAG_LEFT_FIRST
    code = JPS_LAYOUT_OVER_UNDER if layout.startswith("topBottom") else JPS_LAYOUT_SIDE_BY_SIDE
    body = b"_JPSJPS_" + struct.pack(">H", 4) + bytes([0, flags, code, JPS_MEDIA_STEREO]) + struct.pack(">H", 0)
    return b"\xff\xe3" + struct.pack(">H", len(body) + 2) + body


def jps_write(jpeg, layout):
    """A side-by-side (or top-and-bottom) JPEG with the JPS block stating its
    layout; an existing block is replaced."""
    for marker, start, end in _segments(jpeg):
        if marker == 0xE3 and jpeg[start + 4:start + 12] == b"_JPSJPS_":
            jpeg = jpeg[:start] + jpeg[end:]
            break
    i = _insert_point(jpeg)
    return jpeg[:i] + jps_block(layout) + jpeg[i:]


# ---------------------------------------------------------------- MPO (CIPA DC-007)

MP_TYPE_DISPARITY = 0x020002
MP_TYPE_PRIMARY = 0x030000
ATTR_REPRESENTATIVE = 0x20000000


def _ifd(entries, next_off=0):
    b = struct.pack("<H", len(entries))
    for tag, typ, cnt, val in entries:
        b += struct.pack("<HHI", tag, typ, cnt) + val
    return b + struct.pack("<I", next_off)


def _u32(v):
    return struct.pack("<I", v)


def _app2(body):
    return b"\xff\xe2" + struct.pack(">H", len(body) + 4 + 2) + b"MPF\x00" + body


def _mpf_index_segment(sizes, offsets, attrs):
    n = len(sizes)
    ifd_len = 2 + 3 * 12 + 4
    attr_at = 8 + ifd_len
    entry_at = attr_at + ifd_len
    index = _ifd([(0xB000, 7, 4, b"0100"), (0xB001, 4, 1, _u32(n)), (0xB002, 7, 16 * n, _u32(entry_at))], next_off=attr_at)
    attr = _ifd([(0xB000, 7, 4, b"0100"), (0xB101, 4, 1, _u32(1)), (0xB204, 4, 1, _u32(1))])
    entries = b"".join(struct.pack("<IIIHH", a, sz, o, 0, 0) for a, sz, o in zip(attrs, sizes, offsets))
    return _app2(b"II" + struct.pack("<HI", 0x2A, 8) + index + attr + entries)


def _mpf_attr_segment(individual_num):
    attr = _ifd([(0xB000, 7, 4, b"0100"), (0xB101, 4, 1, _u32(individual_num)), (0xB204, 4, 1, _u32(1))])
    return _app2(b"II" + struct.pack("<HI", 0x2A, 8) + attr)


def mpo_write(left_jpeg, right_jpeg):
    """Two JPEG views into one MPO: both typed Disparity, numbered from the
    leftmost viewpoint, the first one representative (CIPA DC-007 6.2)."""
    ins2 = _insert_point(right_jpeg)
    right = right_jpeg[:ins2] + _mpf_attr_segment(2) + right_jpeg[ins2:]
    ins = _insert_point(left_jpeg)
    seg_len = len(_mpf_index_segment([0, 0], [0, 0], [0, 0]))
    tiff_at = ins + 2 + 2 + 4
    size1 = len(left_jpeg) + seg_len
    offset2 = size1 - tiff_at
    seg = _mpf_index_segment([size1, len(right)], [0, offset2], [ATTR_REPRESENTATIVE | MP_TYPE_DISPARITY, MP_TYPE_DISPARITY])
    return left_jpeg[:ins] + seg + left_jpeg[ins:] + right


class _Frames(list):
    individual = None


def mpo_read(data):
    """The frames of an MPO as a list of JPEG byte strings, in stored order,
    with each frame's MP type. Raises ValueError when there is no MPF index."""
    for marker, start, end in _segments(data):
        if marker == 0xE2 and data[start + 4:start + 8] == b"MPF\x00":
            tiff = start + 8
            break
    else:
        raise ValueError("no MPF APP2 segment: not an MPO")
    endian = data[tiff:tiff + 2]
    fmt = "<" if endian == b"II" else ">"
    ifd_off = struct.unpack_from(fmt + "I", data, tiff + 4)[0]
    ifd = tiff + ifd_off
    count = struct.unpack_from(fmt + "H", data, ifd)[0]
    n = 0
    entries_at = None
    for k in range(count):
        tag, typ, cnt, val = struct.unpack_from(fmt + "HHII", data, ifd + 2 + 12 * k)
        if tag == 0xB001:
            n = val
        elif tag == 0xB002:
            entries_at = tiff + val
    if not n or entries_at is None:
        raise ValueError("MPF index without entries")
    # The first image's MP Attribute IFD follows the index: its MP Individual
    # Image Number says whether the frame is a view (1 or more; stereo-layer
    # keeps unknown 0xFFFFFFFF in stored order) or a composite record (0).
    individual = None
    next_ifd = struct.unpack_from(fmt + "I", data, ifd + 2 + 12 * count)[0]
    if next_ifd:
        a = tiff + next_ifd
        acount = struct.unpack_from(fmt + "H", data, a)[0]
        for k in range(acount):
            tag, typ, cnt, val = struct.unpack_from(fmt + "HHII", data, a + 2 + 12 * k)
            if tag == 0xB101:
                individual = val
    frames = _Frames()
    for k in range(n):
        attr, size, off, _, _ = struct.unpack_from(fmt + "IIIHH", data, entries_at + 16 * k)
        pos = 0 if k == 0 else tiff + off
        frames.append((data[pos:pos + size], attr & 0xFFFFFF, attr))
    frames.individual = individual
    return frames


def strip_mpf(jpeg):
    """A frame without its MPF APP2 segment: the view as it was before packing."""
    for marker, start, end in _segments(jpeg):
        if marker == 0xE2 and jpeg[start + 4:start + 8] == b"MPF\x00":
            return jpeg[:start] + jpeg[end:]
    return jpeg


def mpo_views(data):
    """(left, right) JPEG bytes of a stereo MPO, left first by CIPA DC-007
    (Disparity frames numbered from the leftmost viewpoint). Frames of
    another type (Baseline primary with thumbnails, composite, multi-angle)
    are not a pair: None."""
    frames = mpo_read(data)
    if len(frames) < 2 or frames.individual == 0:
        return None
    types = {t for _, t, _ in frames}
    if types - {MP_TYPE_DISPARITY}:
        return None
    return frames[0][0], frames[1][0]


# ---------------------------------------------------------------- PNG sTER

STER_CROSS = 0  # right view on the left
STER_DIVERGING = 1  # left view on the left: our full side by side


def _png_chunks(data):
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not a PNG")
    i = 8
    while i + 8 <= len(data):
        length = struct.unpack(">I", data[i:i + 4])[0]
        kind = data[i + 4:i + 8]
        yield kind, i, i + 12 + length
        i += 12 + length


def _chunk(kind, body):
    return struct.pack(">I", len(body)) + kind + body + struct.pack(">I", zlib.crc32(kind + body) & 0xFFFFFFFF)


def png_ster_read(data):
    """The layout a PNG sTER chunk states, or None (PNG extensions 1.4.0,
    section 3.6: mode 0 cross-fuse, mode 1 diverging-fuse)."""
    for kind, start, end in _png_chunks(data):
        if kind == b"sTER":
            mode = data[start + 8]
            if mode == STER_DIVERGING:
                return SIDE_BY_SIDE_LEFT_FIRST
            if mode == STER_CROSS:
                return SIDE_BY_SIDE_RIGHT_FIRST
            return None
        if kind == b"IDAT":
            break
    return None


def png_ster_write(png, layout=SIDE_BY_SIDE_LEFT_FIRST):
    """Insert (or replace) the sTER chunk right after IHDR."""
    mode = STER_DIVERGING if layout == SIDE_BY_SIDE_LEFT_FIRST else STER_CROSS
    out = b""
    last = 0
    ihdr_end = None
    for kind, start, end in _png_chunks(png):
        if kind == b"sTER":
            out += png[last:start]
            last = end
        elif kind == b"IHDR":
            ihdr_end = end
    out += png[last:]
    if ihdr_end is None:
        raise ValueError("PNG without IHDR")
    return out[:ihdr_end] + _chunk(b"sTER", bytes([mode])) + out[ihdr_end:]


def png_check(data):
    """Chunk order and CRCs; returns the list of chunk names (a parser that can fail)."""
    names = []
    for kind, start, end in _png_chunks(data):
        body = data[start + 8:end - 4]
        crc = struct.unpack(">I", data[end - 4:end])[0]
        if crc != zlib.crc32(kind + body) & 0xFFFFFFFF:
            raise ValueError("bad CRC on " + kind.decode())
        names.append(kind.decode())
    if names[0] != "IHDR" or names[-1] != "IEND":
        raise ValueError("chunk order " + " ".join(names))
    return names


def ster_padded_width(view_width):
    """The right view starts on a multiple of 8 columns (PNG extensions 1.4.0, 3.6)."""
    return (view_width + 7) // 8 * 8
