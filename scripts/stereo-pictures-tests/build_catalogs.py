#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 Daniel Campos Ramos <Capitain_Jack@yahoo.com>
#
# The plug-in's strings in the edition's eight languages (en is the source;
# pl, pt_BR, fr, ja, ko, zh_CN, zh_TW), written as .po files and compiled to
# .mo without gettext's tools, so the test image needs nothing more.
# Run from the workspace: python3 tests/build_catalogs.py
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOCALE = os.path.join(HERE, "..", "..", ".config", "GIMP", "3.0", "plug-ins", "stereo-pictures", "locale")
DOMAIN = "stereo-pictures"

# msgid: {lang: msgstr}
STRINGS = {
    "Stereo pair": dict(pl="Para stereo", pt_BR="Par estéreo", fr="Paire stéréo", ja="ステレオペア", ko="스테레오 쌍", zh_CN="立体图像对", zh_TW="立體影像對"),
    "Not a stereo MPO: no pair of disparity frames": dict(
        pl="To nie jest stereoskopowy plik MPO: brak pary klatek dysparycji", pt_BR="Não é um MPO estéreo: não há par de quadros de disparidade",
        fr="Ce n'est pas un MPO stéréo : aucune paire d'images de disparité", ja="ステレオ MPO ではありません: 視差フレームのペアがありません",
        ko="스테레오 MPO가 아닙니다: 시차 프레임 쌍이 없습니다", zh_CN="不是立体 MPO 文件：没有视差帧对", zh_TW="不是立體 MPO 檔案：沒有視差幀對"),
    "Two layers are needed: Left eye and Right eye": dict(
        pl="Potrzebne są dwie warstwy: Left eye i Right eye", pt_BR="São necessárias duas camadas: Left eye e Right eye",
        fr="Deux calques sont nécessaires : Left eye et Right eye", ja="2 つのレイヤーが必要です: Left eye と Right eye",
        ko="두 개의 레이어가 필요합니다: Left eye와 Right eye", zh_CN="需要两个图层：Left eye 和 Right eye", zh_TW="需要兩個圖層：Left eye 和 Right eye"),
    "Side by side, left eye first": dict(pl="Obok siebie, lewe oko pierwsze", pt_BR="Lado a lado, olho esquerdo primeiro", fr="Côte à côte, œil gauche en premier",
                                         ja="サイドバイサイド、左目が先", ko="좌우 배치, 왼쪽 눈 먼저", zh_CN="左右排列，左眼在前", zh_TW="左右排列，左眼在前"),
    "Side by side, right eye first (cross-eyed)": dict(pl="Obok siebie, prawe oko pierwsze (zez)", pt_BR="Lado a lado, olho direito primeiro (visão cruzada)",
                                                       fr="Côte à côte, œil droit en premier (vision croisée)", ja="サイドバイサイド、右目が先（交差法）",
                                                       ko="좌우 배치, 오른쪽 눈 먼저 (교차 시)", zh_CN="左右排列，右眼在前（交叉视）", zh_TW="左右排列，右眼在前（交叉視）"),
    "Top and bottom, left eye on top": dict(pl="Góra i dół, lewe oko na górze", pt_BR="Em cima e embaixo, olho esquerdo em cima", fr="Haut et bas, œil gauche en haut",
                                            ja="トップアンドボトム、左目が上", ko="상하 배치, 왼쪽 눈 위", zh_CN="上下排列，左眼在上", zh_TW="上下排列，左眼在上"),
    "Top and bottom, right eye on top": dict(pl="Góra i dół, prawe oko na górze", pt_BR="Em cima e embaixo, olho direito em cima", fr="Haut et bas, œil droit en haut",
                                             ja="トップアンドボトム、右目が上", ko="상하 배치, 오른쪽 눈 위", zh_CN="上下排列，右眼在上", zh_TW="上下排列，右眼在上"),
    "Stereo MPO picture": dict(pl="Obraz stereo MPO", pt_BR="Imagem estéreo MPO", fr="Image stéréo MPO", ja="ステレオ MPO 画像", ko="스테레오 MPO 이미지", zh_CN="立体 MPO 图像", zh_TW="立體 MPO 影像"),
    "Stereo JPS picture": dict(pl="Obraz stereo JPS", pt_BR="Imagem estéreo JPS", fr="Image stéréo JPS", ja="ステレオ JPS 画像", ko="스테레오 JPS 이미지", zh_CN="立体 JPS 图像", zh_TW="立體 JPS 影像"),
    "Stereo PNS picture": dict(pl="Obraz stereo PNS", pt_BR="Imagem estéreo PNS", fr="Image stéréo PNS", ja="ステレオ PNS 画像", ko="스테레오 PNS 이미지", zh_CN="立体 PNS 图像", zh_TW="立體 PNS 影像"),
    "Stereo %s picture": dict(pl="Obraz stereo %s", pt_BR="Imagem estéreo %s", fr="Image stéréo %s", ja="ステレオ %s 画像", ko="스테레오 %s 이미지", zh_CN="立体 %s 图像", zh_TW="立體 %s 影像"),
    "Load a stereo MPO (CIPA DC-007) as Left eye and Right eye layers": dict(
        pl="Wczytuje stereoskopowy plik MPO (CIPA DC-007) jako warstwy Left eye i Right eye", pt_BR="Carrega um MPO estéreo (CIPA DC-007) como camadas Left eye e Right eye",
        fr="Charge un MPO stéréo (CIPA DC-007) en calques Left eye et Right eye", ja="ステレオ MPO（CIPA DC-007）を Left eye と Right eye のレイヤーとして読み込みます",
        ko="스테레오 MPO(CIPA DC-007)를 Left eye와 Right eye 레이어로 불러옵니다", zh_CN="将立体 MPO（CIPA DC-007）载入为 Left eye 和 Right eye 图层", zh_TW="將立體 MPO（CIPA DC-007）載入為 Left eye 和 Right eye 圖層"),
    "Load a JPS (side-by-side JPEG) as Left eye and Right eye layers": dict(
        pl="Wczytuje plik JPS (JPEG obok siebie) jako warstwy Left eye i Right eye", pt_BR="Carrega um JPS (JPEG lado a lado) como camadas Left eye e Right eye",
        fr="Charge un JPS (JPEG côte à côte) en calques Left eye et Right eye", ja="JPS（サイドバイサイド JPEG）を Left eye と Right eye のレイヤーとして読み込みます",
        ko="JPS(좌우 배치 JPEG)를 Left eye와 Right eye 레이어로 불러옵니다", zh_CN="将 JPS（左右排列的 JPEG）载入为 Left eye 和 Right eye 图层", zh_TW="將 JPS（左右排列的 JPEG）載入為 Left eye 和 Right eye 圖層"),
    "Load a PNS (side-by-side PNG with the sTER chunk) as Left eye and Right eye layers": dict(
        pl="Wczytuje plik PNS (PNG obok siebie z blokiem sTER) jako warstwy Left eye i Right eye", pt_BR="Carrega um PNS (PNG lado a lado com o bloco sTER) como camadas Left eye e Right eye",
        fr="Charge un PNS (PNG côte à côte avec le bloc sTER) en calques Left eye et Right eye", ja="PNS（sTER チャンク付きサイドバイサイド PNG）を Left eye と Right eye のレイヤーとして読み込みます",
        ko="PNS(sTER 청크가 있는 좌우 배치 PNG)를 Left eye와 Right eye 레이어로 불러옵니다", zh_CN="将 PNS（带 sTER 数据块的左右排列 PNG）载入为 Left eye 和 Right eye 图层", zh_TW="將 PNS（帶 sTER 資料區塊的左右排列 PNG）載入為 Left eye 和 Right eye 圖層"),
    "Export the Left eye and Right eye layers as a stereo %s file": dict(
        pl="Eksportuje warstwy Left eye i Right eye jako stereoskopowy plik %s", pt_BR="Exporta as camadas Left eye e Right eye como um arquivo estéreo %s",
        fr="Exporte les calques Left eye et Right eye en fichier stéréo %s", ja="Left eye と Right eye のレイヤーをステレオ %s ファイルとしてエクスポートします",
        ko="Left eye와 Right eye 레이어를 스테레오 %s 파일로 내보냅니다", zh_CN="将 Left eye 和 Right eye 图层导出为立体 %s 文件", zh_TW="將 Left eye 和 Right eye 圖層匯出為立體 %s 檔案"),
    "Quality": dict(pl="Jakość", pt_BR="Qualidade", fr="Qualité", ja="品質", ko="품질", zh_CN="质量", zh_TW="品質"),
    "JPEG quality": dict(pl="Jakość JPEG", pt_BR="Qualidade JPEG", fr="Qualité JPEG", ja="JPEG の品質", ko="JPEG 품질", zh_CN="JPEG 质量", zh_TW="JPEG 品質"),
    "Layout": dict(pl="Układ", pt_BR="Disposição", fr="Disposition", ja="配置", ko="배치", zh_CN="排列方式", zh_TW="排列方式"),
    "Which view comes first in the file": dict(pl="Który widok jest pierwszy w pliku", pt_BR="Qual vista vem primeiro no arquivo", fr="Quelle vue vient en premier dans le fichier",
                                               ja="ファイル内でどちらのビューが先か", ko="파일에서 어느 뷰가 먼저인지", zh_CN="文件中哪一视图在前", zh_TW="檔案中哪一視圖在前"),
    "Split into eye layers": dict(pl="Podziel na warstwy oczu", pt_BR="Dividir em camadas por olho", fr="Séparer en calques par œil", ja="目ごとのレイヤーに分割", ko="눈별 레이어로 분할", zh_CN="拆分为左右眼图层", zh_TW="拆分為左右眼圖層"),
    "Split a side-by-side or top-and-bottom layer into Left eye and Right eye layers": dict(
        pl="Dzieli warstwę obok siebie lub góra-dół na warstwy Left eye i Right eye", pt_BR="Divide uma camada lado a lado ou em cima e embaixo nas camadas Left eye e Right eye",
        fr="Sépare un calque côte à côte ou haut et bas en calques Left eye et Right eye", ja="サイドバイサイドまたはトップアンドボトムのレイヤーを Left eye と Right eye のレイヤーに分割します",
        ko="좌우 또는 상하 배치 레이어를 Left eye와 Right eye 레이어로 분할합니다", zh_CN="将左右或上下排列的图层拆分为 Left eye 和 Right eye 图层", zh_TW="將左右或上下排列的圖層拆分為 Left eye 和 Right eye 圖層"),
    "How the views are packed in the layer": dict(pl="Jak widoki są ułożone w warstwie", pt_BR="Como as vistas estão dispostas na camada", fr="Comment les vues sont disposées dans le calque",
                                                  ja="レイヤー内でビューがどう配置されているか", ko="레이어에 뷰가 어떻게 배치되어 있는지", zh_CN="图层中视图的排列方式", zh_TW="圖層中視圖的排列方式"),
    "Join eye layers into a pair": dict(pl="Połącz warstwy oczu w parę", pt_BR="Juntar as camadas dos olhos em um par", fr="Réunir les calques des yeux en une paire", ja="目のレイヤーをペアに結合", ko="눈 레이어를 쌍으로 결합", zh_CN="将左右眼图层合并为图像对", zh_TW="將左右眼圖層合併為影像對"),
    "Join the Left eye and Right eye layers into one side-by-side or top-and-bottom layer": dict(
        pl="Łączy warstwy Left eye i Right eye w jedną warstwę obok siebie lub góra-dół", pt_BR="Junta as camadas Left eye e Right eye em uma camada lado a lado ou em cima e embaixo",
        fr="Réunit les calques Left eye et Right eye en un calque côte à côte ou haut et bas", ja="Left eye と Right eye のレイヤーをサイドバイサイドまたはトップアンドボトムの 1 枚のレイヤーに結合します",
        ko="Left eye와 Right eye 레이어를 좌우 또는 상하 배치의 한 레이어로 결합합니다", zh_CN="将 Left eye 和 Right eye 图层合并为一个左右或上下排列的图层", zh_TW="將 Left eye 和 Right eye 圖層合併為一個左右或上下排列的圖層"),
    "How to pack the views": dict(pl="Jak ułożyć widoki", pt_BR="Como dispor as vistas", fr="Comment disposer les vues", ja="ビューの配置方法", ko="뷰 배치 방법", zh_CN="视图的排列方式", zh_TW="視圖的排列方式"),
    "Swap eyes": dict(pl="Zamień oczy", pt_BR="Trocar os olhos", fr="Permuter les yeux", ja="左右の目を入れ替え", ko="눈 바꾸기", zh_CN="交换左右眼", zh_TW="交換左右眼"),
    "Exchange the Left eye and Right eye layers": dict(pl="Zamienia warstwy Left eye i Right eye", pt_BR="Troca as camadas Left eye e Right eye", fr="Permute les calques Left eye et Right eye",
                                                       ja="Left eye と Right eye のレイヤーを入れ替えます", ko="Left eye와 Right eye 레이어를 서로 바꿉니다", zh_CN="交换 Left eye 和 Right eye 图层", zh_TW="交換 Left eye 和 Right eye 圖層"),
}
LANGS = ["pl", "pt_BR", "fr", "ja", "ko", "zh_CN", "zh_TW"]


def po_escape(s):
    return s.replace("\\", "\\\\").replace('"', '\\"')


def write_mo(path, pairs):
    """GNU .mo (gettext manual, 'The Format of GNU MO Files'), one entry per string."""
    pairs = sorted(pairs.items())
    ids = b""
    strs = b""
    offsets = []
    for k, v in pairs:
        kb, vb = k.encode(), v.encode()
        offsets.append((len(ids), len(kb), len(strs), len(vb)))
        ids += kb + b"\0"
        strs += vb + b"\0"
    n = len(pairs)
    key_start = 7 * 4 + 16 * n
    value_start = key_start + len(ids)
    table_k = b"".join(struct.pack("<II", l, key_start + o) for o, l, _, _ in offsets)
    table_v = b"".join(struct.pack("<II", l, value_start + o) for _, _, o, l in offsets)
    header = struct.pack("<7I", 0x950412DE, 0, n, 7 * 4, 7 * 4 + 8 * n, 0, 0)
    with open(path, "wb") as f:
        f.write(header + table_k + table_v + ids + strs)


def main():
    for lang in LANGS:
        pairs = {"": "Project-Id-Version: stereo-pictures\nLanguage: %s\nMIME-Version: 1.0\nContent-Type: text/plain; charset=UTF-8\nContent-Transfer-Encoding: 8bit\n" % lang}
        po = ['# Sparky Stereo OS, stereo pictures plug-in for GIMP 3: %s strings\n# SPDX-License-Identifier: GPL-3.0-or-later\nmsgid ""\nmsgstr ""\n"%s"\n' % (lang, po_escape(pairs[""]).replace("\n", '\\n"\n"')[:-1])]
        for msgid, tr in STRINGS.items():
            if lang not in tr:
                print("missing", lang, msgid)
                sys.exit(1)
            pairs[msgid] = tr[lang]
            po.append('msgid "%s"\nmsgstr "%s"\n' % (po_escape(msgid), po_escape(tr[lang])))
        d = os.path.join(LOCALE, lang, "LC_MESSAGES")
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(LOCALE, lang + ".po"), "w") as f:
            f.write("\n".join(po))
        write_mo(os.path.join(d, DOMAIN + ".mo"), pairs)
    print("catalogs written for", ", ".join(LANGS), "(%d strings each)" % len(STRINGS))


if __name__ == "__main__":
    main()
