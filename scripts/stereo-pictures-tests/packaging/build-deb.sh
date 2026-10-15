#!/bin/bash
# Created by Paweł "pavroo" Pijanowski and Daniel Ramos (Capitain Jack) 2026/10/14
# Copyright 2026 under the GNU GPL3 License
# Last update 2026/10/14
#
# Hand-assembled .deb of the stereo pictures plug-in for GIMP 3 (Sparky Stereo OS,
# Kind A formula): run in a debian:testing container, output dir as $1.
set -eu
HERE="$(cd "$(dirname "$0")" && pwd)"
SRC="$HERE/../../../.config/GIMP/3.0/plug-ins/stereo-pictures"
OUT="${1:-$HERE/out}"
PKG=gimp-stereo-pictures
VER=0.1.0
ARCH=amd64
PLUGDIR=usr/lib/x86_64-linux-gnu/gimp/3.0/plug-ins/stereo-pictures
ROOT="$OUT/$PKG-$VER"
rm -rf "$ROOT"; mkdir -p "$ROOT/DEBIAN" "$ROOT/$PLUGDIR" "$ROOT/usr/share/doc/$PKG"
install -m 755 "$SRC/stereo-pictures.py" "$ROOT/$PLUGDIR/"
install -m 644 "$SRC/stereo_files.py" "$ROOT/$PLUGDIR/"
for mo in "$SRC"/locale/*/LC_MESSAGES/stereo-pictures.mo; do
	lang=$(basename "$(dirname "$(dirname "$mo")")")
	install -D -m 644 "$mo" "$ROOT/$PLUGDIR/locale/$lang/LC_MESSAGES/stereo-pictures.mo"
done
install -m 644 "$SRC/README.md" "$ROOT/usr/share/doc/$PKG/README.md"
cat > "$ROOT/usr/share/doc/$PKG/copyright" <<'COPY'
Upstream Author(s):

    Daniel Ramos (Capitain Jack) <Capitain_Jack@yahoo.com>

Files: *
Copyright: 2026 Daniel Ramos (Capitain Jack) <Capitain_Jack@yahoo.com>
License: GPL-3

    This package is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 3 of the License, or
    (at your option) any later version.

    On Debian systems, the complete text of the GNU General Public
    License version 3 can be found in `/usr/share/common-licenses/GPL-3'.

Files: usr/lib/x86_64-linux-gnu/gimp/3.0/plug-ins/stereo-pictures/stereo_files.py
Comment: The MPO writer follows bravia_mpo.py from sony-bravia-linux
 (Daniel Campos Ramos, GPL-2.0). Daniel Ramos is the author of both; the
 licence of this copy is his to state.

Sparky Stereo OS, an edition of SparkyLinux, created by Paweł "pavroo" Pijanowski <pavroo@onet.eu> and Daniel Ramos (Capitain Jack) <Capitain_Jack@yahoo.com>
COPY
SIZE=$(du -sk "$ROOT" --exclude=DEBIAN | cut -f1)
cat > "$ROOT/DEBIAN/control" <<CTRL
Package: $PKG
Version: $VER
Architecture: $ARCH
Maintainer: Daniel Ramos (Capitain Jack) <Capitain_Jack@yahoo.com>
Installed-Size: $SIZE
Depends: gimp (>= 3.0), python3-gi
Recommends: libstereo-policy1
Section: Graphics
Priority: optional
Homepage: https://sparkylinux.org
Description: Stereo pictures for GIMP 3: MPO, JPS, PNS and both-eyes editing
  Opens MPO (CIPA DC-007), JPS and PNS stereo photographs as Left eye and
  Right eye layers, exports the same formats with each format's own stereo
  mark, and adds a Stereo menu: split, join, swap eyes, and stereo editing
  of a side-by-side picture with both eyes alike at a chosen depth.
  Strings in en, pl, pt_BR, fr, ja, ko, zh_CN and zh_TW.
  Part of Sparky Stereo OS, Daniel Ramos's edition of SparkyLinux.
CTRL
(cd "$ROOT" && find usr -type f -exec md5sum {} \; > DEBIAN/md5sums)
dpkg-deb --root-owner-group -b "$ROOT" "$OUT/${PKG}_${VER}_${ARCH}.deb"
rm -rf "$ROOT"
ls -l "$OUT/${PKG}_${VER}_${ARCH}.deb"
