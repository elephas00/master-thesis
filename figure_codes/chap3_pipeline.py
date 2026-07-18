#!/usr/bin/env python3
"""第三章：本章方法总体流程（draw.io XML → PDF）。

对应 figure/generated/chap3-pipeline.pdf。

用法（项目根目录）:
    python3 figure_codes/chap3_pipeline.py
"""

from __future__ import annotations

import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

from figure_paths import BUILD_DIR, GENERATED_DIR, PROJECT_ROOT as ROOT, ensure_output_dirs
from thesis_style import drawio_fs

OUT_XML = BUILD_DIR / "chap3-pipeline.xml"
OUT_PDF = GENERATED_DIR / "chap3-pipeline.pdf"

_SCALE = 2.0
FS_TITLE = drawio_fs("title", scale=_SCALE)
FS_LABEL = drawio_fs("label", scale=_SCALE)
FS_TICK = drawio_fs("tick", scale=_SCALE)
FS_HEAD = drawio_fs("title", scale=25 / 11)
FS_LEGEND_TITLE = drawio_fs("legend", scale=17 / 9)
FS_LEGEND_TEXT = drawio_fs("legend", scale=15 / 9)
FS_ANNOT = drawio_fs("annot", scale=1.75)

BG = (
    "rounded=1;whiteSpace=wrap;html=1;fillColor=#F8FBFF;"
    "strokeColor=#90CAF9;strokeWidth=1.5;dashed=1;dashPattern=8 4;arcSize=6;"
)
PARA = (
    "shape=parallelogram;perimeter=parallelogramPerimeter;whiteSpace=wrap;"
    "html=1;fixedSize=1;fillColor=#EEEEEE;strokeColor=#757575;"
    f"strokeWidth=1.5;fontSize={FS_TITLE};fontFamily=Helvetica;"
)
PARA_OUT = (
    "shape=parallelogram;perimeter=parallelogramPerimeter;whiteSpace=wrap;"
    "html=1;fixedSize=1;fillColor=#F5F5F5;strokeColor=#9E9E9E;"
    f"strokeWidth=1.5;fontSize={FS_LABEL};fontFamily=Helvetica;"
)
BOX_GRAY = (
    "rounded=1;whiteSpace=wrap;html=1;fillColor=#F5F5F5;strokeColor=#9E9E9E;"
    f"strokeWidth=1.5;fontSize={FS_TITLE};fontFamily=Helvetica;arcSize=10;"
)
BOX_BLUE = (
    "rounded=1;whiteSpace=wrap;html=1;fillColor=#E3F2FD;strokeColor=#1565C0;"
    f"strokeWidth=2;fontSize={FS_LABEL};fontFamily=Helvetica;arcSize=10;"
)
BOX_ORANGE = (
    "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFF3E0;strokeColor=#E65100;"
    f"strokeWidth=2;fontSize={FS_LABEL};fontFamily=Helvetica;arcSize=10;"
)
BOX_GREEN = (
    "rounded=1;whiteSpace=wrap;html=1;fillColor=#E8F5E9;strokeColor=#2E7D32;"
    f"strokeWidth=1.5;fontSize={FS_LABEL};fontFamily=Helvetica;arcSize=10;"
)
EDGE = (
    "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;"
    "html=1;strokeWidth=2;strokeColor=#424242;endArrow=blockThin;endFill=1;"
)
EDGE_BLUE = (
    "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;"
    "html=1;strokeWidth=2;strokeColor=#1565C0;endArrow=blockThin;endFill=1;"
)
EDGE_DASH = (
    "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;"
    "html=1;strokeWidth=1.5;strokeColor=#E65100;dashed=1;dashPattern=8 4;"
    f"endArrow=blockThin;endFill=1;fontSize={FS_LEGEND_TEXT};fontColor=#E65100;fontFamily=Helvetica;"
)
TEXT = "text;html=1;strokeColor=none;fillColor=none;fontFamily=Helvetica;"


def _geom(el: ET.Element, x: float, y: float, w: float, h: float) -> None:
    ET.SubElement(
        el, "mxGeometry",
        {"x": str(x), "y": str(y), "width": str(w), "height": str(h), "as": "geometry"},
    )


class Diagram:
    def __init__(self, page_w: int = 1400, page_h: int = 520) -> None:
        self.model = ET.Element(
            "mxGraphModel",
            {
                "dx": "1422", "dy": "794", "grid": "1", "gridSize": "10",
                "guides": "1", "tooltips": "1", "connect": "1", "arrows": "1",
                "fold": "1", "page": "1", "pageScale": "1",
                "pageWidth": str(page_w), "pageHeight": str(page_h),
                "math": "0", "shadow": "0",
            },
        )
        self.root = ET.SubElement(self.model, "root")
        ET.SubElement(self.root, "mxCell", {"id": "0"})
        ET.SubElement(self.root, "mxCell", {"id": "1", "parent": "0"})

    def box(
        self, cid: str, value: str, x: float, y: float, w: float, h: float,
        *, style: str,
    ) -> None:
        c = ET.SubElement(
            self.root, "mxCell",
            {"id": cid, "value": value, "style": style, "vertex": "1", "parent": "1"},
        )
        _geom(c, x, y, w, h)

    def edge(
        self, cid: str, source: str, target: str, *, style: str,
        value: str = "", points: list[tuple[float, float]] | None = None,
    ) -> None:
        attrs = {
            "id": cid, "style": style, "edge": "1", "parent": "1",
            "source": source, "target": target,
        }
        if value:
            attrs["value"] = value
        c = ET.SubElement(self.root, "mxCell", attrs)
        geo = ET.SubElement(c, "mxGeometry", {"relative": "1", "as": "geometry"})
        if points:
            arr = ET.SubElement(geo, "Array", {"as": "points"})
            for px, py in points:
                ET.SubElement(arr, "mxPoint", {"x": str(px), "y": str(py)})

    def free_edge(
        self, cid: str, x1: float, y1: float, x2: float, y2: float, *, style: str,
    ) -> None:
        c = ET.SubElement(
            self.root, "mxCell",
            {"id": cid, "value": "", "style": style, "edge": "1", "parent": "1"},
        )
        geo = ET.SubElement(
            c, "mxGeometry",
            {"width": "50", "height": "50", "relative": "1", "as": "geometry"},
        )
        ET.SubElement(geo, "mxPoint", {"x": str(x1), "y": str(y1), "as": "sourcePoint"})
        ET.SubElement(geo, "mxPoint", {"x": str(x2), "y": str(y2), "as": "targetPoint"})

    def to_xml(self) -> str:
        mxfile = ET.Element(
            "mxfile",
            {
                "host": "app.diagrams.net",
                "agent": "chap3_pipeline.py",
                "version": "22.1.0",
            },
        )
        diagram = ET.SubElement(
            mxfile, "diagram",
            {"id": "chap3-pipeline", "name": "本章方法总体流程"},
        )
        diagram.append(self.model)
        ET.indent(mxfile, space="  ")
        return '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(
            mxfile, encoding="unicode",
        ) + "\n"


def build() -> Diagram:
    d = Diagram()

    d.box("method-bg", "", 455, 30, 560, 300, style=BG)
    d.box(
        "method-bg-label", "本章方法三模块",
        845, 36, 160, 30,
        style=TEXT + f"align=right;verticalAlign=middle;fontStyle=1;fontSize={FS_HEAD};fontColor=#1565C0;",
    )

    d.box(
        "in",
        "<b>SMART 日级日志</b><br>+ 故障工单<br>"
        '<font style="font-size:17px;color:#666666">MB1 / MB2</font>',
        15, 100, 200, 135, style=PARA,
    )
    d.box(
        "prep",
        "<b>预处理与 A/B 归纳</b><br>"
        '<font style="font-size:17px;color:#555555">'
        "字段筛选 · 缺失补全<br>A 组磨损/环境<br>B 组异常/突变</font>",
        235, 78, 210, 180, style=BOX_GRAY,
    )
    d.box(
        "feat",
        "<b>① 短期时序突变特征</b><br>"
        '<font style="font-size:15px;color:#0D47A1">'
        "W 阶 Lag(A/B) + r<sub>k</sub>|Δ|(B)</font>",
        475, 55, 220, 95, style=BOX_BLUE,
    )
    d.box(
        "label",
        "<b>② 混合标注</b><br>"
        '<font style="font-size:15px;color:#BF360C">'
        "y = y<sup>fail</sup> · y<sup>jump</sup><br>故障前 k 日 ∩ 首跳后</font>",
        475, 195, 220, 105, style=BOX_ORANGE,
    )
    d.box(
        "align",
        '<font style="font-size:14px;color:#795548">W、k 超参数</font>',
        545, 158, 80, 22,
        style=TEXT + f"align=center;verticalAlign=middle;fontSize={FS_ANNOT};",
    )
    d.free_edge(
        "align-line", 585, 158, 585, 195,
        style="endArrow=classic;startArrow=classic;html=1;strokeWidth=1;"
              "strokeColor=#FFB300;dashed=1;dashPattern=4 4;",
    )
    d.box(
        "ens",
        "<b>③ 异构集成预测</b><br>"
        '<font style="font-size:15px;color:#0D47A1">'
        "RF / XGB / LGB<br>→ Attention 融合<br>FocalLoss优化</font>",
        735, 115, 195, 125, style=BOX_BLUE,
    )
    d.box(
        "prob",
        "<b>样本级概率</b><br>"
        '<font style="font-size:15px;color:#1B5E20">'
        "ŷ<sub>i,t</sub> ∈ [0, 1]</font>",
        970, 115, 155, 125, style=BOX_GREEN,
    )
    d.box(
        "eval",
        "<b>盘级最早告警评估</b><br>"
        '<font style="font-size:15px;color:#555555">'
        "H = 30 天<br>TPR · FPR · F<sub>0.5</sub></font>",
        1165, 130, 195, 95, style=PARA_OUT,
    )

    d.edge("e-in-prep", "in", "prep", style=EDGE)
    d.edge("e-prep-feat", "prep", "feat", style=EDGE)
    d.edge("e-feat-ens", "feat", "ens", style=EDGE_BLUE)
    d.edge("e-ens-prob", "ens", "prob", style=EDGE)
    d.edge("e-prob-eval", "prob", "eval", style=EDGE)
    d.edge("e-prep-label", "prep", "label", style=EDGE_DASH, value="监督信号")
    d.edge(
        "e-label-ens", "label", "ens", style=EDGE_DASH, value="(z, y)",
        points=[(715, 248), (715, 178)],
    )

    d.box(
        "legend-box", "", 120, 380, 1160, 62,
        style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FAFAFA;strokeColor=#E0E0E0;strokeWidth=1;",
    )
    d.box(
        "legend-title", "图例", 136, 396, 48, 28,
        style=TEXT + f"fontStyle=1;fontSize={FS_LEGEND_TITLE};align=center;",
    )
    d.box(
        "lg1", "", 196, 404, 30, 20,
        style="rounded=1;whiteSpace=wrap;html=1;fillColor=#F5F5F5;strokeColor=#9E9E9E;",
    )
    d.box(
        "lg1t", "数据预处理 / 盘级评估", 232, 398, 180, 28,
        style=TEXT + f"fontSize={FS_LEGEND_TEXT};",
    )
    d.box(
        "lg2", "", 430, 404, 30, 20,
        style="rounded=1;whiteSpace=wrap;html=1;fillColor=#E3F2FD;strokeColor=#1565C0;",
    )
    d.box(
        "lg2t", "方法模块 ①③（特征与集成）", 466, 398, 210, 28,
        style=TEXT + f"fontSize={FS_LEGEND_TEXT};",
    )
    d.box(
        "lg3", "", 700, 404, 30, 20,
        style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFF3E0;strokeColor=#E65100;",
    )
    d.box(
        "lg3t", "方法模块 ②（混合标注）", 736, 398, 180, 28,
        style=TEXT + f"fontSize={FS_LEGEND_TEXT};",
    )
    d.free_edge(
        "lg4", 940, 414, 990, 414,
        style="endArrow=blockThin;html=1;strokeWidth=1.5;strokeColor=#E65100;"
              "dashed=1;dashPattern=8 4;",
    )
    d.box(
        "lg4t", "虚线：监督标注支路", 998, 398, 160, 28,
        style=TEXT + f"fontSize={FS_LEGEND_TEXT};",
    )
    return d


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
        if isinstance(exc, subprocess.CalledProcessError) and exc.stderr:
            print(exc.stderr)
        return False


def main() -> None:
    ensure_output_dirs()
    xml = build().to_xml()
    OUT_XML.write_text(xml, encoding="utf-8")
    print(f"wrote {OUT_XML.relative_to(ROOT)}")
    if export_pdf(OUT_XML, OUT_PDF):
        print(f"wrote {OUT_PDF.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
