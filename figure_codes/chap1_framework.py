#!/usr/bin/env python3
"""第一章：本文研究框架（draw.io XML → PDF）。

对应 figure/generated/chap1-framework.pdf。

用法（项目根目录）:
    python3 figure_codes/chap1_framework.py
"""

from __future__ import annotations

import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

from figure_paths import BUILD_DIR, GENERATED_DIR, PROJECT_ROOT as ROOT, ensure_output_dirs
from thesis_style import drawio_fs

OUT_XML = BUILD_DIR / "chap1-framework.xml"
OUT_PDF = GENERATED_DIR / "chap1-framework.pdf"

_SCALE = 2.0
FS_TITLE = drawio_fs("title", scale=_SCALE)
FS_LABEL = drawio_fs("label", scale=_SCALE)
FS_TICK = drawio_fs("tick", scale=_SCALE)
FS_ANNOT = drawio_fs("annot", scale=_SCALE)
FS_LEGEND_SM = drawio_fs("annot", scale=1.75)

TEXT = "text;html=1;strokeColor=none;fillColor=none;fontFamily=Helvetica;"
EDGE = (
    "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;"
    "html=1;strokeWidth=2;strokeColor=#424242;endArrow=blockThin;endFill=1;"
)
EDGE_BLUE = EDGE.replace("strokeColor=#424242", "strokeColor=#1565C0")
EDGE_GREEN = EDGE.replace("strokeColor=#424242", "strokeColor=#2E7D32")
EDGE_DASH_GRAY = (
    "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;"
    "html=1;strokeWidth=1.5;strokeColor=#90A4AE;endArrow=blockThin;endFill=1;"
    "dashed=1;dashPattern=4 4;"
)
EDGE_DASH_GREEN = (
    "edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeWidth=1.5;"
    "strokeColor=#2E7D32;endArrow=blockThin;endFill=1;dashed=1;dashPattern=8 4;"
    f"fontSize={FS_LEGEND_SM};fontColor=#2E7D32;fontFamily=Helvetica;"
)
EDGE_CH3_CH5 = (
    "edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeWidth=2;"
    "strokeColor=#1565C0;endArrow=blockThin;endFill=1;"
    f"fontSize={FS_LEGEND_SM};fontColor=#1565C0;fontFamily=Helvetica;"
)
PARA = (
    "shape=parallelogram;perimeter=parallelogramPerimeter;whiteSpace=wrap;"
    "html=1;fixedSize=1;fillColor=#EEEEEE;strokeColor=#757575;"
    f"strokeWidth=1.5;fontSize={FS_LABEL};fontFamily=Helvetica;"
)
PARA_OUT = (
    "shape=parallelogram;perimeter=parallelogramPerimeter;whiteSpace=wrap;"
    "html=1;fixedSize=1;fillColor=#F5F5F5;strokeColor=#9E9E9E;"
    f"strokeWidth=1.5;fontSize={FS_TICK};fontFamily=Helvetica;"
)


def _geom(el: ET.Element, x: float, y: float, w: float, h: float) -> None:
    ET.SubElement(
        el, "mxGeometry",
        {"x": str(x), "y": str(y), "width": str(w), "height": str(h), "as": "geometry"},
    )


class Diagram:
    def __init__(self, page_w: int = 1400, page_h: int = 920) -> None:
        self.model = ET.Element(
            "mxGraphModel",
            {
                "dx": "1422", "dy": "900", "grid": "1", "gridSize": "10",
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
        *, style: str, parent: str = "1",
    ) -> None:
        c = ET.SubElement(
            self.root, "mxCell",
            {
                "id": cid, "value": value, "style": style,
                "vertex": "1", "parent": parent,
            },
        )
        _geom(c, x, y, w, h)

    def edge(
        self, cid: str, source: str, target: str, *, style: str, value: str = "",
    ) -> None:
        attrs = {
            "id": cid, "style": style, "edge": "1", "parent": "1",
            "source": source, "target": target,
        }
        if value:
            attrs["value"] = value
        c = ET.SubElement(self.root, "mxCell", attrs)
        ET.SubElement(c, "mxGeometry", {"relative": "1", "as": "geometry"})

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
                "agent": "chap1_framework.py",
                "version": "22.1.0",
            },
        )
        diagram = ET.SubElement(
            mxfile, "diagram",
            {"id": "thesis-framework", "name": "本文研究框架"},
        )
        diagram.append(self.model)
        ET.indent(mxfile, space="  ")
        return '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(
            mxfile, encoding="unicode",
        ) + "\n"


def build() -> Diagram:
    d = Diagram()

    d.box(
        "top-banner",
        "<b>研究目标</b>：兼顾误报代价，提升故障检出能力与寿命利用效率",
        40, 20, 1320, 52,
        style=(
            "rounded=1;whiteSpace=wrap;html=1;fillColor=#ECEFF1;strokeColor=#607D8B;"
            f"strokeWidth=2;fontSize={FS_TITLE};fontFamily=Helvetica;arcSize=8;"
        ),
    )
    d.box(
        "prob1",
        "<b>核心问题一</b><br>"
        '<font style="font-size:16px;color:#37474F">'
        "阿里云公开 SMART 数据集故障模式探索<br>"
        "近端突变前兆刻画 · 盘级 30 天预警</font>",
        60, 92, 600, 78,
        style=(
            "rounded=1;whiteSpace=wrap;html=1;fillColor=#FAFAFA;strokeColor=#9E9E9E;"
            f"strokeWidth=1.5;fontSize={FS_LABEL};fontFamily=Helvetica;arcSize=10;"
        ),
    )
    d.box(
        "prob2",
        "<b>核心问题二</b><br>"
        '<font style="font-size:16px;color:#37474F">'
        "块级寿命预测结果 → 差异化写入策略<br>"
        "在不突破可靠性边界前提下提升可写入量</font>",
        740, 92, 600, 78,
        style=(
            "rounded=1;whiteSpace=wrap;html=1;fillColor=#FAFAFA;strokeColor=#9E9E9E;"
            f"strokeWidth=1.5;fontSize={FS_LABEL};fontFamily=Helvetica;arcSize=10;"
        ),
    )

    d.box(
        "ch3-bg", "", 50, 188, 620, 500,
        style=(
            "rounded=1;whiteSpace=wrap;html=1;fillColor=#F8FBFF;strokeColor=#90CAF9;"
            "strokeWidth=1.5;dashed=1;dashPattern=8 4;arcSize=6;"
        ),
    )
    d.box(
        "ch3-label", "第三章 · 盘级故障预测",
        430, 194, 220, 28,
        style=TEXT + f"align=right;verticalAlign=middle;fontStyle=1;fontSize={FS_LABEL};fontColor=#1565C0;",
    )
    d.box(
        "ch4-bg", "", 730, 188, 620, 470,
        style=(
            "rounded=1;whiteSpace=wrap;html=1;fillColor=#F1F8E9;strokeColor=#81C784;"
            "strokeWidth=1.5;dashed=1;dashPattern=8 4;arcSize=6;"
        ),
    )
    d.box(
        "ch4-label", "第四章 · 块级寿命提升",
        1110, 194, 220, 28,
        style=TEXT + f"align=right;verticalAlign=middle;fontStyle=1;fontSize={FS_LABEL};fontColor=#2E7D32;",
    )

    # ch3 stack
    d.box(
        "ch3-in",
        "<b>阿里云公开 SMART + 故障工单</b><br>"
        '<font style="font-size:15px;color:#666666">MB1 / MB2 日级日志</font>',
        130, 228, 460, 62, style=PARA,
    )
    d.box(
        "ch3-eda",
        "<b>故障模式探索</b><br>"
        '<font style="font-size:14px;color:#455A64">'
        "B 组近端突变前兆观察 · A/B 属性归纳</font>",
        130, 308, 460, 58,
        style=(
            "rounded=1;whiteSpace=wrap;html=1;fillColor=#F5F5F5;strokeColor=#78909C;"
            f"strokeWidth=1.5;fontSize={FS_TICK};fontFamily=Helvetica;arcSize=10;"
        ),
    )
    d.box(
        "ch3-label-box",
        "<b>混合标注</b><br>"
        '<font style="font-size:14px;color:#BF360C">'
        "抑制静默段标签噪声 · 与突变特征同尺度</font>",
        130, 384, 460, 58,
        style=(
            "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFF3E0;strokeColor=#E65100;"
            f"strokeWidth=2;fontSize={FS_TICK};fontFamily=Helvetica;arcSize=10;"
        ),
    )
    d.box(
        "ch3-feat",
        "<b>短期时序突变特征</b><br>"
        '<font style="font-size:14px;color:#0D47A1">'
        "W 阶 Lag(A/B) + r<sub>k</sub>|Δ|(B)</font>",
        130, 460, 460, 58,
        style=(
            "rounded=1;whiteSpace=wrap;html=1;fillColor=#E3F2FD;strokeColor=#1565C0;"
            f"strokeWidth=2;fontSize={FS_TICK};fontFamily=Helvetica;arcSize=10;"
        ),
    )
    d.box(
        "ch3-ens",
        "<b>异构集成预测</b><br>"
        '<font style="font-size:14px;color:#0D47A1">'
        "RF / XGB / LGB → Attention 融合<br>FocalLoss优化</font>",
        130, 530, 460, 68,
        style=(
            "rounded=1;whiteSpace=wrap;html=1;fillColor=#E3F2FD;strokeColor=#1565C0;"
            f"strokeWidth=2;fontSize={FS_TICK};fontFamily=Helvetica;arcSize=10;"
        ),
    )
    d.box(
        "ch3-out",
        "<b>盘级最早告警评估</b><br>"
        '<font style="font-size:14px;color:#555555">'
        "预警窗口 H = 30 天<br>验证集上以 F₀.₅ 优化阈值<br>"
        "报告 TPR · FPR · Precision</font>",
        130, 612, 460, 78, style=PARA_OUT,
    )

    # ch4 stack
    d.box(
        "ch4-in",
        "<b>实验室高温磨损 FBC 数据</b><br>"
        '<font style="font-size:15px;color:#666666">块级 PE 轨迹 · TLC 颗粒</font>',
        810, 228, 460, 62, style=PARA,
    )
    d.box(
        "ch4-group",
        "<b>逻辑块分组与寿命标签</b><br>"
        '<font style="font-size:14px;color:#33691E">分位数聚合 · 定义 LIFESPAN</font>',
        810, 318, 460, 58,
        style=(
            "rounded=1;whiteSpace=wrap;html=1;fillColor=#DCEDC8;strokeColor=#558B2F;"
            f"strokeWidth=1.5;fontSize={FS_TICK};fontFamily=Helvetica;arcSize=10;"
        ),
    )
    d.box(
        "ch4-cls",
        "<b>强块 / 弱块二分类</b><br>"
        '<font style="font-size:14px;color:#33691E">'
        "RF / XGB / LGB 集成学习 · LP/MP/UP 分区建模</font>",
        810, 408, 460, 58,
        style=(
            "rounded=1;whiteSpace=wrap;html=1;fillColor=#DCEDC8;strokeColor=#558B2F;"
            f"strokeWidth=1.5;fontSize={FS_TICK};fontFamily=Helvetica;arcSize=10;"
        ),
    )
    d.box(
        "ch4-pe",
        "<b>差异化 PE 上限策略</b><br>"
        '<font style="font-size:14px;color:#33691E">强块适度放宽 · 弱块保守退役</font>',
        810, 498, 460, 58,
        style=(
            "rounded=1;whiteSpace=wrap;html=1;fillColor=#C8E6C9;strokeColor=#2E7D32;"
            f"strokeWidth=2;fontSize={FS_TICK};fontFamily=Helvetica;arcSize=10;"
        ),
    )
    d.box(
        "ch4-out",
        "<b>可写入量评估</b><br>"
        '<font style="font-size:14px;color:#555555">相对统一 PE 阈值策略约 +17%</font>',
        810, 588, 460, 58, style=PARA_OUT,
    )

    # ch5
    d.box(
        "ch5-bg", "", 120, 710, 1160, 100,
        style=(
            "rounded=1;whiteSpace=wrap;html=1;fillColor=#F3E5F5;strokeColor=#BA68C8;"
            "strokeWidth=1.5;dashed=1;dashPattern=8 4;arcSize=6;"
        ),
    )
    d.box(
        "ch5-label", "第五章 · 工程落地",
        136, 716, 160, 24,
        style=TEXT + f"align=left;verticalAlign=middle;fontStyle=1;fontSize={FS_TICK};fontColor=#7B1FA2;",
    )
    d.box(
        "ch5-main",
        "<b>智慧 SSD 运维原型系统</b><br>"
        '<font style="font-size:16px;color:#4A148C">'
        "数据管理 → 预测预警 → 人工处置 → 结果沉淀</font>",
        320, 732, 760, 64,
        style=(
            "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#9C27B0;"
            f"strokeWidth=2;fontSize={FS_LABEL};fontFamily=Helvetica;arcSize=10;"
        ),
    )

    d.edge("e-p1-ch3", "prob1", "ch3-bg", style=EDGE_DASH_GRAY)
    d.edge("e-p2-ch4", "prob2", "ch4-bg", style=EDGE_DASH_GRAY)
    d.edge("e3-1", "ch3-in", "ch3-eda", style=EDGE)
    d.edge("e3-2", "ch3-eda", "ch3-label-box", style=EDGE)
    d.edge("e3-3", "ch3-label-box", "ch3-feat", style=EDGE_BLUE)
    d.edge("e3-4", "ch3-feat", "ch3-ens", style=EDGE_BLUE)
    d.edge("e3-5", "ch3-ens", "ch3-out", style=EDGE)
    d.edge("e4-1", "ch4-in", "ch4-group", style=EDGE)
    d.edge("e4-2", "ch4-group", "ch4-cls", style=EDGE_GREEN)
    d.edge("e4-3", "ch4-cls", "ch4-pe", style=EDGE_GREEN)
    d.edge("e4-4", "ch4-pe", "ch4-out", style=EDGE)
    d.edge("e-ch3-ch5", "ch3-out", "ch5-main", style=EDGE_CH3_CH5, value="盘级预警服务")
    d.edge("e-ch4-ch5", "ch4-out", "ch5-main", style=EDGE_DASH_GREEN, value="策略可扩展")

    # legend
    d.box(
        "legend-box", "", 120, 830, 1160, 58,
        style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FAFAFA;strokeColor=#E0E0E0;strokeWidth=1;",
    )
    d.box("legend-title", "图例", 266, 844, 48, 28, style=TEXT + f"fontStyle=1;fontSize={FS_ANNOT};align=center;")
    d.box(
        "lg-ch3", "", 326, 850, 28, 18,
        style="rounded=1;whiteSpace=wrap;html=1;fillColor=#E3F2FD;strokeColor=#1565C0;",
    )
    d.box("lg-ch3t", "第三章方法模块", 358, 844, 120, 28, style=TEXT + f"fontSize={FS_LEGEND_SM};")
    d.box(
        "lg-label", "", 494, 850, 28, 18,
        style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFF3E0;strokeColor=#E65100;",
    )
    d.box("lg-labelt", "混合标注", 526, 844, 72, 28, style=TEXT + f"fontSize={FS_LEGEND_SM};")
    d.box(
        "lg-ch4", "", 614, 850, 28, 18,
        style="rounded=1;whiteSpace=wrap;html=1;fillColor=#DCEDC8;strokeColor=#558B2F;",
    )
    d.box("lg-ch4t", "第四章方法模块", 646, 844, 120, 28, style=TEXT + f"fontSize={FS_LEGEND_SM};")
    d.box(
        "lg-ch5", "", 782, 850, 28, 18,
        style="rounded=1;whiteSpace=wrap;html=1;fillColor=#F3E5F5;strokeColor=#BA68C8;",
    )
    d.box("lg-ch5t", "第五章工程落地", 814, 844, 110, 28, style=TEXT + f"fontSize={FS_LEGEND_SM};")
    d.free_edge(
        "lg-dash", 940, 859, 990, 859,
        style="endArrow=blockThin;html=1;strokeWidth=1.5;strokeColor=#2E7D32;dashed=1;dashPattern=8 4;",
    )
    d.box("lg-dasht", "虚线：策略可扩展衔接", 998, 844, 160, 28, style=TEXT + f"fontSize={FS_LEGEND_SM};")
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
