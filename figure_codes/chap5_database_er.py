#!/usr/bin/env python3
"""生成第 5 章数据库概念 E-R 图（draw.io XML → PDF）。

命名与本章其它图一致（chap5-warning-gen-flow 等），采用 chap5-database-er。

用法:
    python figure_codes/chap5_database_er.py
"""

from __future__ import annotations

import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

from figure_paths import BUILD_DIR, GENERATED_DIR, PROJECT_ROOT as ROOT, ensure_output_dirs
from thesis_style import drawio_fs, fit_drawio_pdf_width

OUT_XML = BUILD_DIR / "chap5-database-er.xml"
OUT_PDF = GENERATED_DIR / "chap5-database-er.pdf"

# 导出后缩到栏宽；倍率≈当前裁剪宽/栏宽，使缩后字号接近 FONT
_SCALE = 1.36
FS_ENTITY = drawio_fs("title", scale=_SCALE)
FS_REL = drawio_fs("tick", scale=_SCALE)
FS_ATTR = drawio_fs("tick", scale=_SCALE)
FS_ATTR_MD = drawio_fs("annot", scale=_SCALE)
FS_ATTR_SM = drawio_fs("legend", scale=_SCALE)
FS_CARD = drawio_fs("annot", scale=_SCALE)

ENTITY = (
    "rounded=0;whiteSpace=wrap;html=1;align=center;"
    f"verticalAlign=middle;fontSize={FS_ENTITY};fontStyle=1;"
)
ATTR = "ellipse;whiteSpace=wrap;html=1;fontSize={fs};"
ATTR_PK = "ellipse;whiteSpace=wrap;html=1;fontSize={fs};fontStyle=4;"
REL = (
    "rhombus;whiteSpace=wrap;html=1;align=center;"
    f"verticalAlign=middle;fontSize={FS_REL};"
)
EDGE = "endArrow=none;html=1;rounded=0;"
EDGE_DASH = "endArrow=none;html=1;rounded=0;dashed=1;"
LABEL = "edgeLabel;html=1;align=center;verticalAlign=middle;fontSize={fs};"


def _geom(el: ET.Element, x: float, y: float, w: float, h: float) -> None:
    ET.SubElement(
        el, "mxGeometry",
        {"x": str(x), "y": str(y), "width": str(w), "height": str(h), "as": "geometry"},
    )


def _edge_geom(el: ET.Element) -> None:
    ET.SubElement(el, "mxGeometry", {"relative": "1", "as": "geometry"})


class ER:
    def __init__(self, page_w: int = 980, page_h: int = 540) -> None:
        self.model = ET.Element(
            "mxGraphModel",
            {
                "dx": "1200", "dy": "800", "grid": "1", "gridSize": "10",
                "guides": "1", "tooltips": "1", "connect": "1", "arrows": "1",
                "fold": "1", "page": "1", "pageScale": "1",
                "pageWidth": str(page_w), "pageHeight": str(page_h),
                "math": "0", "shadow": "0",
            },
        )
        self.root = ET.SubElement(self.model, "root")
        ET.SubElement(self.root, "mxCell", {"id": "0"})
        ET.SubElement(self.root, "mxCell", {"id": "1", "parent": "0"})

    def _cell(self, cid: str, **attrs: str) -> ET.Element:
        return ET.SubElement(self.root, "mxCell", {"id": cid, "parent": "1", **attrs})

    def entity(self, cid: str, title: str, x: float, y: float,
               w: float = 120, h: float = 42) -> None:
        c = self._cell(cid, value=title, style=ENTITY, vertex="1")
        _geom(c, x, y, w, h)

    def attr(self, cid: str, title: str, x: float, y: float, *,
             pk: bool = False, w: float = 70, h: float = 32, fs: int = FS_ATTR) -> None:
        style = (ATTR_PK if pk else ATTR).format(fs=fs)
        c = self._cell(cid, value=title, style=style, vertex="1")
        _geom(c, x, y, w, h)

    def rel(self, cid: str, title: str, x: float, y: float,
            w: float = 84, h: float = 48) -> None:
        c = self._cell(cid, value=title, style=REL, vertex="1")
        _geom(c, x, y, w, h)

    def link_attr(self, cid: str, src: str, tgt: str) -> None:
        c = self._cell(cid, style=EDGE, edge="1", source=src, target=tgt)
        _edge_geom(c)

    def link(
        self, cid: str, src: str, tgt: str, *,
        dashed: bool = False,
        exit_: tuple[float, float] | None = None,
        entry: tuple[float, float] | None = None,
        perimeter: int = 1,
        card: str | None = None,
        card_x: float = 0.0,
        card_off: tuple[float, float] = (0, -10),
        card_fs: int = FS_ATTR,
    ) -> None:
        style = EDGE_DASH if dashed else EDGE
        if exit_ is not None:
            style += (
                f"exitX={exit_[0]};exitY={exit_[1]};"
                f"exitPerimeter={perimeter};"
            )
        if entry is not None:
            style += (
                f"entryX={entry[0]};entryY={entry[1]};"
                f"entryPerimeter={perimeter};"
            )
        c = self._cell(cid, style=style, edge="1", source=src, target=tgt)
        _edge_geom(c)
        if card is not None:
            lab = self._cell(
                f"{cid}-card", value=card,
                style=LABEL.format(fs=card_fs), vertex="1",
                connectable="0", parent=cid,
            )
            g = ET.SubElement(
                lab, "mxGeometry",
                {"x": str(card_x), "relative": "1", "as": "geometry"},
            )
            off: dict[str, str] = {"y": str(card_off[1]), "as": "offset"}
            if card_off[0]:
                off["x"] = str(card_off[0])
            ET.SubElement(g, "mxPoint", off)

    def to_xml(self) -> str:
        mxfile = ET.Element(
            "mxfile",
            {
                "host": "app.diagrams.net",
                "modified": "2026-07-18T00:00:00.000Z",
                "agent": "chap5_database_er.py",
                "version": "22.1.0",
            },
        )
        diagram = ET.SubElement(
            mxfile, "diagram", {"id": "database-er", "name": "数据库E-R图"},
        )
        diagram.append(self.model)
        ET.indent(mxfile, space="  ")
        return '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(
            mxfile, encoding="unicode",
        ) + "\n"


def build() -> ER:
    """属性与改名前进稿一致，仅概念层关键字段。"""
    er = ER()

    er.entity("e-disk", "SSD盘信息", 190, 150, w=132)
    er.entity("e-log", "SMART 日志", 555, 150)
    er.entity("e-warn", "预警记录", 196, 395)
    er.entity("e-fault", "故障记录", 555, 395)

    # SSD盘信息：上侧 3 + 左侧 2
    for i, (name, x, y, pk) in enumerate([
        ("设备ID", 110, 28, True),
        ("序列号", 205, 22, False),
        ("型号", 300, 32, False),
        ("容量", 35, 135, False),
        ("制造商", 35, 190, False),
    ]):
        cid = f"a-disk-{i}"
        er.attr(cid, name, x, y, pk=pk)
        er.link_attr(f"ld{i}", cid, "e-disk")

    # SMART 日志：上侧 3 + 右侧 Normalized + 下侧 raw
    for i, (name, x, y, w, pk) in enumerate([
        ("日志ID", 485, 22, 70, True),
        ("设备ID", 580, 16, 70, False),
        ("采集日期", 675, 28, 78, False),
    ]):
        cid = f"a-log-{i}"
        er.attr(cid, name, x, y, pk=pk, w=w)
        er.link_attr(f"ll{i}", cid, "e-log")

    for i, (name, x) in enumerate([
        ("raw属性值1", 545),
        ("raw属性值…", 665),
        ("raw属性值n", 785),
    ]):
        cid = f"a-log-{i + 3}"
        er.attr(cid, name, x, 270, w=100, fs=FS_ATTR_MD)
        er.link_attr(f"ll{i + 3}", cid, "e-log")

    for i, (name, y) in enumerate([
        ("Normalized属性值1", 70),
        ("Normalized属性值…", 135),
        ("Normalized属性值n", 200),
    ]):
        cid = f"a-log-{i + 6}"
        er.attr(cid, name, 720, y, w=130, fs=FS_ATTR_SM)
        er.link_attr(f"ll{i + 6}", cid, "e-log")

    # 预警记录：左侧 2 + 下侧 3
    for i, (name, x, y, w, pk) in enumerate([
        ("预警ID", 30, 375, 70, True),
        ("设备ID", 30, 425, 70, False),
        ("预警日期", 110, 480, 78, False),
        ("处置状态", 205, 480, 78, False),
        ("预警评分", 300, 480, 78, False),
    ]):
        cid = f"a-warn-{i}"
        er.attr(cid, name, x, y, pk=pk, w=w)
        er.link_attr(f"lw{i}", cid, "e-warn")

    # 故障记录：右侧 2 + 下侧 2
    for i, (name, x, y, w, pk) in enumerate([
        ("故障ID", 720, 375, 70, True),
        ("设备ID", 720, 425, 70, False),
        ("故障日期", 515, 480, 78, False),
        ("来源", 610, 480, 70, False),
    ]):
        cid = f"a-fault-{i}"
        er.attr(cid, name, x, y, pk=pk, w=w)
        er.link_attr(f"lf{i}", cid, "e-fault")

    er.rel("r-own", "拥有", 400, 147)
    er.rel("r-gen", "产生", 214, 275)
    er.rel("r-map", "对应", 370, 250)
    er.rel("r-confirm", "确认生成", 375, 392, w=90)

    er.link(
        "l-d-own", "e-disk", "r-own",
        exit_=(1, 0.5), entry=(0, 0.5),
        card="1", card_x=-0.15, card_off=(0, -10),
    )
    er.link(
        "l-own-l", "r-own", "e-log",
        exit_=(1, 0.5), entry=(0, 0.5),
        card="n", card_x=0.15, card_off=(0, -10),
    )
    er.link(
        "l-d-gen", "e-disk", "r-gen",
        exit_=(0.5, 1), entry=(0.5, 0), perimeter=0,
        card="1", card_x=-0.1, card_off=(12, 0),
    )
    er.link(
        "l-gen-w", "r-gen", "e-warn",
        exit_=(0.5, 1), entry=(0.5, 0), perimeter=0,
        card="n", card_x=0.15, card_off=(12, 0),
    )
    er.link(
        "l-d-map", "e-disk", "r-map",
        exit_=(1, 1), entry=(0, 0.5), perimeter=0,
        card="1", card_x=-0.2, card_off=(0, -10),
    )
    er.link(
        "l-map-f", "r-map", "e-fault",
        exit_=(1, 0.5), entry=(0, 0), perimeter=0,
        card="n", card_x=0.1, card_off=(0, -10),
    )
    er.link(
        "l-w-c", "e-warn", "r-confirm",
        dashed=True, exit_=(1, 0.5), entry=(0, 0.5),
        card="0..1", card_x=-0.1, card_off=(0, -12), card_fs=FS_CARD,
    )
    er.link(
        "l-c-f", "r-confirm", "e-fault",
        dashed=True, exit_=(1, 0.5), entry=(0, 0.5),
        card="0..1", card_x=0.1, card_off=(0, -12), card_fs=FS_CARD,
    )

    return er


def export_pdf(xml_path: Path, pdf_path: Path) -> bool:
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        subprocess.run(
            ["drawio", "-x", "-f", "pdf", "--crop", "-b", "8",
             "-o", str(pdf_path), str(xml_path)],
            check=True, capture_output=True, text=True,
        )
        return True
    except (FileNotFoundError, subprocess.CalledProcessError) as exc:
        print(f"[warn] drawio 导出失败，仅写入 XML: {exc}")
        return False


def main() -> None:
    ensure_output_dirs()
    xml = build().to_xml()
    OUT_XML.write_text(xml, encoding="utf-8")
    print(f"wrote {OUT_XML.relative_to(ROOT)}")
    if export_pdf(OUT_XML, OUT_PDF):
        s = fit_drawio_pdf_width(OUT_PDF)
        print(f"wrote {OUT_PDF.relative_to(ROOT)} (fit×{s:.3f})")


if __name__ == "__main__":
    main()
