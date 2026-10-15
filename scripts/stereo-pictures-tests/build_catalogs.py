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
    "d = 0 px: screen plane": dict(pl="d = 0 px: płaszczyzna ekranu", pt_BR="d = 0 px: plano da tela", fr="d = 0 px : plan de l'écran", ja="d = 0 px: スクリーン面", ko="d = 0 px: 화면 평면", zh_CN="d = 0 px：屏幕平面", zh_TW="d = 0 px：螢幕平面"),
    "d = +%d px: behind the screen": dict(pl="d = +%d px: za ekranem", pt_BR="d = +%d px: atrás da tela", fr="d = +%d px : derrière l'écran", ja="d = +%d px: スクリーンの奥", ko="d = +%d px: 화면 뒤", zh_CN="d = +%d px：屏幕后方", zh_TW="d = +%d px：螢幕後方"),
    "d = %d px: in front of the screen": dict(pl="d = %d px: przed ekranem", pt_BR="d = %d px: na frente da tela", fr="d = %d px : devant l'écran", ja="d = %d px: スクリーンの手前", ko="d = %d px: 화면 앞", zh_CN="d = %d px：屏幕前方", zh_TW="d = %d px：螢幕前方"),
    "Not a side-by-side picture: nothing to set": dict(pl="To nie jest obraz obok siebie: nic do ustawienia", pt_BR="Não é uma imagem lado a lado: nada a definir", fr="Ce n'est pas une image côte à côte : rien à régler", ja="サイドバイサイド画像ではありません: 設定するものがありません", ko="좌우 배치 이미지가 아닙니다: 설정할 것이 없습니다", zh_CN="不是左右排列的图像：无需设置", zh_TW="不是左右排列的影像：無需設定"),
    "Both eyes alike. %s. Paint tools repeat live with Image > Symmetry Painting > Tiling (interval X %d, two strokes), or after the file is saved and reopened; everything else: Stereo > Apply to both eyes.": dict(
        pl="Oba oczy jednakowo. %s. Narzędzia malowania powtarzają na żywo przez Obraz > Malowanie symetryczne > Kafelki (odstęp X %d, dwa pociągnięcia) albo po zapisaniu i ponownym otwarciu pliku; wszystko inne: Stereo > Zastosuj do obu oczu.",
        pt_BR="Ambos os olhos iguais. %s. As ferramentas de pintura repetem ao vivo com Imagem > Pintura simétrica > Ladrilho (intervalo X %d, dois traços), ou depois de salvar e reabrir o arquivo; o resto: Estéreo > Aplicar aos dois olhos.",
        fr="Les deux yeux à l'identique. %s. Les outils de peinture répètent en direct avec Image > Peinture en symétrie > Mosaïque (intervalle X %d, deux traits), ou après enregistrement et réouverture du fichier ; tout le reste : Stéréo > Appliquer aux deux yeux.",
        ja="両目を同じに。%s。描画ツールは「画像 > シンメトリー描画 > タイル」（間隔 X %d、2 ストローク）でライブに繰り返されます。ファイルを保存して再度開いた後も有効です。それ以外は「ステレオ > 両目に適用」を使ってください。",
        ko="양쪽 눈 동일. %s. 그리기 도구는 이미지 > 대칭 그리기 > 타일링(간격 X %d, 두 번 그리기)으로 실시간 반복되며, 파일을 저장하고 다시 열어도 적용됩니다. 그 외에는 스테레오 > 양쪽 눈에 적용을 사용하세요.",
        zh_CN="双眼一致。%s。绘画工具通过 图像 > 对称绘画 > 平铺（间隔 X %d，两笔）实时重复，或在保存并重新打开文件后生效；其他操作：立体 > 应用到双眼。",
        zh_TW="雙眼一致。%s。繪畫工具透過 影像 > 對稱繪畫 > 平鋪（間隔 X %d，兩筆）即時重複，或在儲存並重新開啟檔案後生效；其他操作：立體 > 套用到雙眼。"),
    "Stereo editing is not set to Both eyes alike": dict(pl="Edycja stereo nie jest ustawiona na Oba oczy jednakowo", pt_BR="A edição estéreo não está em Ambos os olhos iguais", fr="L'édition stéréo n'est pas réglée sur Les deux yeux à l'identique", ja="ステレオ編集が「両目を同じに」に設定されていません", ko="스테레오 편집이 양쪽 눈 동일로 설정되어 있지 않습니다", zh_CN="立体编辑未设为双眼一致", zh_TW="立體編輯未設為雙眼一致"),
    "No snapshot to compare with: set Both eyes alike first": dict(pl="Brak migawki do porównania: najpierw ustaw Oba oczy jednakowo", pt_BR="Não há instantâneo para comparar: defina Ambos os olhos iguais primeiro", fr="Aucun instantané à comparer : réglez d'abord Les deux yeux à l'identique", ja="比較するスナップショットがありません: まず「両目を同じに」を設定してください", ko="비교할 스냅샷이 없습니다: 먼저 양쪽 눈 동일을 설정하세요", zh_CN="没有可比较的快照：请先设为双眼一致", zh_TW="沒有可比較的快照：請先設為雙眼一致"),
    "%d changed pixels repeated in the other eye (%s)": dict(pl="%d zmienionych pikseli powtórzono w drugim oku (%s)", pt_BR="%d pixels alterados repetidos no outro olho (%s)", fr="%d pixels modifiés répétés dans l'autre œil (%s)", ja="%d 個の変更ピクセルをもう一方の目に繰り返しました (%s)", ko="변경된 픽셀 %d개를 다른 눈에 반복했습니다 (%s)", zh_CN="已将 %d 个更改的像素重复到另一眼 (%s)", zh_TW="已將 %d 個變更的像素重複到另一眼 (%s)"),
    "Stereo editing...": dict(pl="Edycja stereo...", pt_BR="Edição estéreo...", fr="Édition stéréo...", ja="ステレオ編集...", ko="스테레오 편집...", zh_CN="立体编辑...", zh_TW="立體編輯..."),
    "Each eye on its own, or both eyes alike: an edit in one view repeated in the other at the depth d": dict(
        pl="Każde oko osobno albo oba oczy jednakowo: edycja w jednym widoku powtórzona w drugim na głębokości d", pt_BR="Cada olho por si, ou ambos os olhos iguais: uma edição em uma vista repetida na outra à profundidade d",
        fr="Chaque œil séparément, ou les deux yeux à l'identique : une édition dans une vue répétée dans l'autre à la profondeur d", ja="それぞれの目を個別に、または両目を同じに: 一方のビューの編集を深さ d でもう一方に繰り返します",
        ko="각 눈 따로, 또는 양쪽 눈 동일: 한 뷰의 편집을 깊이 d로 다른 뷰에 반복", zh_CN="每只眼睛单独编辑，或双眼一致：一个视图中的编辑以深度 d 重复到另一视图", zh_TW="每隻眼睛單獨編輯，或雙眼一致：一個視圖中的編輯以深度 d 重複到另一視圖"),
    "Each eye on its own": dict(pl="Każde oko osobno", pt_BR="Cada olho por si", fr="Chaque œil séparément", ja="それぞれの目を個別に", ko="각 눈 따로", zh_CN="每只眼睛单独编辑", zh_TW="每隻眼睛單獨編輯"),
    "Both eyes alike": dict(pl="Oba oczy jednakowo", pt_BR="Ambos os olhos iguais", fr="Les deux yeux à l'identique", ja="両目を同じに", ko="양쪽 눈 동일", zh_CN="双眼一致", zh_TW="雙眼一致"),
    "Mode": dict(pl="Tryb", pt_BR="Modo", fr="Mode", ja="モード", ko="모드", zh_CN="模式", zh_TW="模式"),
    "How edits apply to the two views": dict(pl="Jak edycje działają na dwa widoki", pt_BR="Como as edições se aplicam às duas vistas", fr="Comment les éditions s'appliquent aux deux vues", ja="編集が 2 つのビューにどう適用されるか", ko="편집이 두 뷰에 적용되는 방식", zh_CN="编辑如何应用到两个视图", zh_TW="編輯如何套用到兩個視圖"),
    "Depth d (px)": dict(pl="Głębokość d (px)", pt_BR="Profundidade d (px)", fr="Profondeur d (px)", ja="深さ d (px)", ko="깊이 d (px)", zh_CN="深度 d (px)", zh_TW="深度 d (px)"),
    "Shift of the repeat in the right view, in pixels: positive is behind the screen, negative in front, 0 the screen plane; no limits": dict(
        pl="Przesunięcie powtórzenia w prawym widoku, w pikselach: dodatnie za ekranem, ujemne przed nim, 0 to płaszczyzna ekranu; bez ograniczeń", pt_BR="Deslocamento da repetição na vista direita, em pixels: positivo atrás da tela, negativo na frente, 0 o plano da tela; sem limites",
        fr="Décalage de la répétition dans la vue droite, en pixels : positif derrière l'écran, négatif devant, 0 le plan de l'écran ; sans limites", ja="右ビューでの繰り返しのずれ（ピクセル）: 正はスクリーンの奥、負は手前、0 はスクリーン面。制限なし",
        ko="오른쪽 뷰에서 반복의 이동량(픽셀): 양수는 화면 뒤, 음수는 앞, 0은 화면 평면. 제한 없음", zh_CN="右视图中重复内容的偏移（像素）：正值在屏幕后方，负值在前方，0 为屏幕平面；无限制", zh_TW="右視圖中重複內容的偏移（像素）：正值在螢幕後方，負值在前方，0 為螢幕平面；無限制"),
    "Apply to both eyes": dict(pl="Zastosuj do obu oczu", pt_BR="Aplicar aos dois olhos", fr="Appliquer aux deux yeux", ja="両目に適用", ko="양쪽 눈에 적용", zh_CN="应用到双眼", zh_TW="套用到雙眼"),
    "Repeat what changed in one view in the other view at the depth d": dict(pl="Powtarza to, co zmieniło się w jednym widoku, w drugim na głębokości d", pt_BR="Repete o que mudou em uma vista na outra vista à profundidade d", fr="Répète ce qui a changé dans une vue dans l'autre vue à la profondeur d", ja="一方のビューで変更された内容を深さ d でもう一方のビューに繰り返します", ko="한 뷰에서 바뀐 내용을 깊이 d로 다른 뷰에 반복합니다", zh_CN="将一个视图中的更改以深度 d 重复到另一视图", zh_TW="將一個視圖中的變更以深度 d 重複到另一視圖"),
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
