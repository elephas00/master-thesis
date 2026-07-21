#!/usr/bin/env python3
"""第三章：异构集成预测（draw.io XML → PDF）。

对应 figure/generated/chap3-ensemble.pdf。

用法（项目根目录）:
    python3 figure_codes/chap3_ensemble.py
"""

from __future__ import annotations

import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

from figure_paths import BUILD_DIR, GENERATED_DIR, PROJECT_ROOT as ROOT, ensure_output_dirs
from thesis_style import drawio_fs, fit_drawio_pdf_width

OUT_XML = BUILD_DIR / "chap3-ensemble.xml"
OUT_PDF = GENERATED_DIR / "chap3-ensemble.pdf"

_SCALE = 7.20
_R = _SCALE / 5.0
FS_LABEL = drawio_fs("label", scale=_SCALE)
FS_TICK = drawio_fs("tick", scale=_SCALE)
FS_NOTE = drawio_fs("note", scale=_SCALE)  # 缩栏后 ≈8 pt（公式/说明）
FS_BOX = drawio_fs("title", scale=(60 / 11) * _R)
FS_SWIM = drawio_fs("title", scale=(54 / 11) * _R)
FS_BODY = drawio_fs("label", scale=5.1 * _R)
FS_EDGE = drawio_fs("tick", scale=7.0 * _R)
# 装饰性省略号，略大于 title
FS_DOTS = max(1, int(round(12 * _SCALE)))

TEXT = "text;html=1;strokeColor=none;fillColor=none;"


def _html_fs(size: int, body: str, *, color: str | None = None) -> str:
    """HTML 内联字号：与 style 的 fontSize 一样走画布像素，缩栏后对齐 FONT。"""
    style = f"font-size:{size}px"
    if color:
        style += f";color:{color}"
    return f'<font style="{style}">{body}</font>'


def _geom(el: ET.Element, x: float, y: float, w: float, h: float) -> None:
    ET.SubElement(
        el, "mxGeometry",
        {"x": str(x), "y": str(y), "width": str(w), "height": str(h), "as": "geometry"},
    )


class Diagram:
    def __init__(self, page_w: int = 4200, page_h: int = 1860) -> None:
        self.model = ET.Element(
            "mxGraphModel",
            {
                "dx": "1200", "dy": "700", "grid": "1", "gridSize": "10",
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
        points: list[tuple[float, float]] | None = None,
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
        geo = ET.SubElement(c, "mxGeometry", {"relative": "1", "as": "geometry"})
        ET.SubElement(geo, "mxPoint", {"x": str(x1), "y": str(y1), "as": "sourcePoint"})
        ET.SubElement(geo, "mxPoint", {"x": str(x2), "y": str(y2), "as": "targetPoint"})

    def to_xml(self) -> str:
        mxfile = ET.Element(
            "mxfile",
            {
                "host": "app.diagrams.net",
                "agent": "chap3_ensemble.py",
                "version": "22.1.0",
            },
        )
        diagram = ET.SubElement(
            mxfile, "diagram",
            {"id": "chap3-ensemble", "name": "异构集成预测"},
        )
        diagram.append(self.model)
        ET.indent(mxfile, space="  ")
        return '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(
            mxfile, encoding="unicode",
        ) + "\n"


def build() -> Diagram:
    # 左/右端与第二层、Focal 同步加宽；字号加大后抬高各容器，避免贴边溢出
    dx = 320
    out_w = 570 + dx          # 890，与左侧特征框同宽
    l2_w = 1200               # 原 900
    l2_extra = l2_w - 900
    out_extra = out_w - 480
    head_h = 140
    l2_x = 2460 + dx
    lane_y = 220  # 第一层 / 第二层顶对齐
    l2_y = lane_y
    out_x = 3540 + dx + l2_extra
    out_h = 600

    # 第二层内容高度：底边贴紧底注，只留少量边距
    step_h = 280
    step_gap = 52
    step1_y = head_h + 40
    step2_y = step1_y + step_h + step_gap
    step3_y = step2_y + step_h + step_gap
    note_h = 140
    note_y = step3_y + step_h + 48
    l2_h = note_y + note_h + 48

    # 与第二层中部对齐
    out_y = l2_y + (l2_h - out_h) // 2
    # Focal 在第二层下方；输出下侧出线后下行再左转
    ylabel_h = 200
    focal_h = 380
    focal_y = max(l2_y + l2_h + 140, out_y + out_h + 80)
    # 左转高度落在 Focal 右侧中上部
    arrow_y = focal_y + int(0.28 * focal_h)
    # 标签底边略高于 Focal 底边，且仍在左转廊道之下
    ylabel_y = focal_y + focal_h - ylabel_h - 40
    if ylabel_y < arrow_y + 70:
        ylabel_y = arrow_y + 70
    page_h = max(2700, max(focal_y + focal_h, ylabel_y + ylabel_h) + 220)
    d = Diagram(
        page_w=4200 + dx + l2_extra + out_extra,
        page_h=page_h,
    )

    in_h = 440
    in_y = out_y + (out_h - in_h) // 2
    d.box(
        "input",
        "<b>短期时序突变特征</b><br>"
        + _html_fs(
            FS_NOTE,
            "z<sub>i,t</sub> ∈ ℝ<sup>|𝒜|W + |ℬ|(W+1)</sup><br>"
            "（A/B 组 Lag + B 组加权突变）",
        ),
        120, in_y, 570 + dx, in_h,
        style=(
            "rounded=1;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;"
            f"fontSize={FS_BOX};arcSize=8;"
            "spacingTop=18;spacingBottom=18;verticalAlign=middle;"
        ),
    )

    # layer 1 swimlane（加高标题栏，标题文字与底边分开）
    l1_h = 1530
    l1_y = lane_y
    d.box(
        "layer1-box", "第一层：异构基分类器",
        840 + dx, l1_y, 900, l1_h,
        style=(
            f"swimlane;html=1;startSize={head_h};fillColor=#e3f2fd;strokeColor=#1565c0;"
            f"fontStyle=1;fontSize={FS_SWIM};rounded=1;arcSize=6;"
        ),
    )
    d.box(
        "layer1-formula",
        _html_fs(FS_NOTE, "ℳ = {M<sub>m</sub>}<sub>m=1</sub><sup>N</sup>"),
        30, head_h + 24, 840, 80,
        style=TEXT + "align=center;verticalAlign=middle;",
        parent="layer1-box",
    )
    d.box(
        "m1",
        "<b>M<sub>1</sub></b><br>"
        + _html_fs(FS_NOTE, "基分类器"),
        90, 270, 360, 210,
        style=(
            "rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#1565c0;"
            f"fontSize={FS_SWIM};spacingTop=12;spacingBottom=12;verticalAlign=middle;"
        ),
        parent="layer1-box",
    )
    d.box(
        "m1-out",
        "p<sub>i,t</sub><sup>(1)</sup>",
        570, 286, 240, 180,
        style=(
            "rounded=1;whiteSpace=wrap;html=1;fillColor=#bbdefb;strokeColor=#1565c0;"
            f"fontSize={FS_BODY};verticalAlign=middle;"
        ),
        parent="layer1-box",
    )
    d.box(
        "dots1",
        _html_fs(FS_DOTS, "⋮", color="#666666"),
        210, 510, 120, 110,
        style=TEXT + "align=center;verticalAlign=middle;",
        parent="layer1-box",
    )
    d.box(
        "dots-mid",
        _html_fs(FS_NOTE, "M<sub>2</sub>, …, M<sub>N−1</sub>", color="#888888"),
        90, 620, 720, 80,
        style=TEXT + "align=center;verticalAlign=middle;",
        parent="layer1-box",
    )
    d.box(
        "dots2",
        _html_fs(FS_DOTS, "⋮", color="#666666"),
        210, 710, 120, 110,
        style=TEXT + "align=center;verticalAlign=middle;",
        parent="layer1-box",
    )
    d.box(
        "mN",
        "<b>M<sub>N</sub></b><br>"
        + _html_fs(FS_NOTE, "基分类器"),
        90, 850, 360, 210,
        style=(
            "rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#1565c0;"
            f"fontSize={FS_SWIM};spacingTop=12;spacingBottom=12;verticalAlign=middle;"
        ),
        parent="layer1-box",
    )
    d.box(
        "mN-out",
        "p<sub>i,t</sub><sup>(N)</sup>",
        570, 866, 240, 180,
        style=(
            "rounded=1;whiteSpace=wrap;html=1;fillColor=#bbdefb;strokeColor=#1565c0;"
            f"fontSize={FS_BODY};verticalAlign=middle;"
        ),
        parent="layer1-box",
    )
    d.box(
        "layer1-note",
        _html_fs(
            FS_NOTE,
            "N ≥ 2，基分类器使用<br>Bagging 族、梯度提升树等",
            color="#555555",
        ),
        30, 1170, 840, 180,
        style=TEXT + "align=center;verticalAlign=middle;",
        parent="layer1-box",
    )

    d.box(
        "pvec",
        "<b>概率向量</b><br>"
        + _html_fs(
            FS_NOTE,
            "p<sub>i,t</sub> =<br>"
            "[p<sup>(1)</sup>, …, p<sup>(N)</sup>]<sup>T</sup>",
        ),
        1890 + dx, in_y, 390, in_h,
        style=(
            "rounded=1;whiteSpace=wrap;html=1;fillColor=#e8eaf6;strokeColor=#3949ab;"
            f"fontSize={FS_SWIM};spacingTop=18;spacingBottom=18;verticalAlign=middle;"
        ),
    )

    # layer 2：底边贴紧底注
    step_w = l2_w - 180
    d.box(
        "layer2-box", "第二层：Attention 样本级融合",
        l2_x, l2_y, l2_w, l2_h,
        style=(
            f"swimlane;startSize={head_h};fillColor=#fff3e0;strokeColor=#e65100;"
            f"fontStyle=1;fontSize={FS_SWIM};rounded=1;arcSize=6;"
        ),
    )
    d.box(
        "attn-step1",
        "① 线性变换<br>"
        + _html_fs(FS_NOTE, "W<sub>α</sub>·p<sub>i,t</sub> + b<sub>α</sub>"),
        90, step1_y, step_w, step_h,
        style=(
            "rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#e65100;"
            f"fontSize={FS_BODY};spacingTop=22;spacingBottom=22;verticalAlign=middle;"
        ),
        parent="layer2-box",
    )
    d.box(
        "attn-step2",
        "② Softmax 归一化<br>"
        + _html_fs(FS_NOTE, "α<sub>i,t</sub><sup>(m)</sup>，Σ<sub>m</sub>α = 1"),
        90, step2_y, step_w, step_h,
        style=(
            "rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#e65100;"
            f"fontSize={FS_BODY};spacingTop=22;spacingBottom=22;verticalAlign=middle;"
        ),
        parent="layer2-box",
    )
    d.box(
        "attn-step3",
        "③ 加权组合<br>"
        + _html_fs(
            FS_NOTE,
            "ŷ<sub>i,t</sub> = Σ<sub>m=1</sub><sup>N</sup> α<sup>(m)</sup>·p<sup>(m)</sup>",
        ),
        90, step3_y, step_w, step_h,
        style=(
            "rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#e65100;"
            f"fontSize={FS_BODY};spacingTop=22;spacingBottom=22;verticalAlign=middle;"
        ),
        parent="layer2-box",
    )
    d.box(
        "attn-note",
        _html_fs(FS_NOTE, "样本自适应权重，可解释各专家贡献占比", color="#555555"),
        60, note_y, l2_w - 120, note_h,
        style=TEXT + "align=center;verticalAlign=middle;",
        parent="layer2-box",
    )

    d.box(
        "output",
        _html_fs(FS_SWIM, "<b>融合故障概率</b>")
        + "<br><br>"
        + _html_fs(FS_NOTE, "ŷ<sub>i,t</sub> ∈ [0, 1]"),
        out_x, out_y, out_w, out_h,
        style=(
            "rounded=1;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;"
            f"fontSize={FS_SWIM};arcSize=8;spacing=20;verticalAlign=middle;"
        ),
    )
    d.box(
        "focal",
        _html_fs(FS_LABEL, "<b>Focal Loss</b>  ℒ<sub>FL</sub>")
        + "<br>"
        + _html_fs(
            FS_NOTE,
            "对易分样本降权，强化少数类故障样本<br>"
            "在验证集上更新 W<sub>α</sub>, b<sub>α</sub>（γ=2）",
        ),
        l2_x, focal_y, l2_w, focal_h,
        style=(
            "rounded=1;whiteSpace=wrap;html=1;fillColor=#ffebee;strokeColor=#c62828;"
            f"fontSize={FS_NOTE};dashed=1;dashPattern=8 8;"
            "align=center;verticalAlign=middle;spacingTop=36;spacingBottom=36;"
        ),
    )
    d.box(
        "ylabel",
        "标签 y<sub>i,t</sub> ∈ {0,1}",
        out_x, ylabel_y, out_w, ylabel_h,
        style=(
            "rounded=1;whiteSpace=wrap;html=1;fillColor=#fce4ec;strokeColor=#c62828;"
            f"fontSize={FS_NOTE};align=center;verticalAlign=middle;"
            "spacingTop=16;spacingBottom=16;"
        ),
    )

    # legend（与 Focal 顶对齐一带；标题与条目拉开）
    leg_y = focal_y
    leg_h = max(340, focal_h)
    d.box(
        "legend-box", "", 120, leg_y, 600, leg_h,
        style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fafafa;strokeColor=#cccccc;dashed=1;",
    )
    d.box(
        "legend-title", "图例", 156, leg_y + 28, 120, 54,
        style=TEXT + f"fontStyle=1;fontSize={FS_BODY};",
    )
    d.free_edge(
        "legend1-line", 156, leg_y + 180, 306, leg_y + 180,
        style="endArrow=classic;html=1;strokeWidth=3;strokeColor=#333333;",
    )
    d.box(
        "legend1", "推理数据流", 336, leg_y + 154, 330, 60,
        style=TEXT + f"fontSize={FS_TICK};align=left;",
    )
    d.free_edge(
        "legend2-line", 156, leg_y + 270, 306, leg_y + 270,
        style="endArrow=classic;html=1;strokeWidth=3;strokeColor=#c62828;dashed=1;",
    )
    d.box(
        "legend2", "训练 / 损失", 336, leg_y + 244, 330, 60,
        style=TEXT + f"fontSize={FS_TICK};align=left;",
    )

    # inference edges
    d.edge(
        "e-in-m1", "input", "m1",
        style=(
            "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;"
            "html=1;strokeWidth=2;strokeColor=#333333;"
            "exitX=1;exitY=0.3;entryX=0;entryY=0.5;"
        ),
    )
    d.edge(
        "e-in-mN", "input", "mN",
        style=(
            "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;"
            "html=1;strokeWidth=2;strokeColor=#333333;"
            "exitX=1;exitY=0.7;entryX=0;entryY=0.5;"
        ),
    )
    d.edge(
        "e-in-dots", "input", "dots-mid",
        style=(
            "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;"
            "html=1;strokeWidth=1.5;strokeColor=#999999;dashed=1;"
            f"exitX=1;exitY=0.5;entryX=0;entryY=0.5;fontSize={FS_EDGE};fontColor=#888888;"
        ),
        value="⋯",
    )
    d.edge(
        "e-m1-out", "m1", "m1-out",
        style=(
            "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;"
            "html=1;strokeWidth=1.5;strokeColor=#1565c0;"
            "exitX=1;exitY=0.5;entryX=0;entryY=0.5;"
        ),
    )
    d.edge(
        "e-mN-out", "mN", "mN-out",
        style=(
            "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;"
            "html=1;strokeWidth=1.5;strokeColor=#1565c0;"
            "exitX=1;exitY=0.5;entryX=0;entryY=0.5;"
        ),
    )
    d.edge(
        "e-p1-pvec", "m1-out", "pvec",
        style=(
            "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;"
            "html=1;strokeWidth=2;strokeColor=#3949ab;"
            "exitX=1;exitY=0.5;entryX=0;entryY=0.25;"
        ),
    )
    d.edge(
        "e-pN-pvec", "mN-out", "pvec",
        style=(
            "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;"
            "html=1;strokeWidth=2;strokeColor=#3949ab;"
            "exitX=1;exitY=0.5;entryX=0;entryY=0.75;"
        ),
    )
    d.edge(
        "e-pvec-attn", "pvec", "attn-step1",
        style=(
            "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;"
            "html=1;strokeWidth=2;strokeColor=#333333;"
            "exitX=1;exitY=0.5;entryX=0;entryY=0.5;"
        ),
    )
    d.edge(
        "e-attn-12", "attn-step1", "attn-step2",
        style=(
            "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;"
            "html=1;strokeWidth=1.5;strokeColor=#e65100;"
            "exitX=0.5;exitY=1;entryX=0.5;entryY=0;"
        ),
    )
    d.edge(
        "e-attn-23", "attn-step2", "attn-step3",
        style=(
            "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;"
            "html=1;strokeWidth=1.5;strokeColor=#e65100;"
            "exitX=0.5;exitY=1;entryX=0.5;entryY=0;"
        ),
    )
    d.edge(
        "e-attn-out", "attn-step3", "output",
        style=(
            "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;"
            "html=1;strokeWidth=2;strokeColor=#333333;"
            "exitX=1;exitY=0.5;entryX=0;entryY=0.5;"
        ),
    )
    # 输出框下侧出线 → 下行 → 左转进 Focal 右侧
    entry_y = (arrow_y - focal_y) / float(focal_h)
    d.edge(
        "e-out-focal", "output", "focal",
        style=(
            "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=0;jettySize=0;"
            "html=1;strokeWidth=2;strokeColor=#c62828;dashed=1;"
            f"exitX=0.5;exitY=1;entryX=1;entryY={entry_y:.3f};"
        ),
        points=[(out_x + out_w // 2, arrow_y)],
    )
    # 标签 → Focal：水平直线（对齐标签中线）
    y_mid = ylabel_y + ylabel_h / 2
    y_entry = max(0.05, min(0.95, (y_mid - focal_y) / float(focal_h)))
    d.edge(
        "e-y-focal", "ylabel", "focal",
        style=(
            "endArrow=classic;html=1;rounded=0;"
            "strokeWidth=2;strokeColor=#c62828;dashed=1;"
            f"exitX=0;exitY=0.5;entryX=1;entryY={y_entry:.3f};"
        ),
    )
    d.edge(
        "e-focal-back", "focal", "layer2-box",
        style=(
            "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=0;jettySize=0;"
            f"html=1;strokeWidth=2;strokeColor=#c62828;dashed=1;fontSize={FS_TICK};"
            "labelBackgroundColor=#FFFFFF;"
            "exitX=0.5;exitY=0;entryX=0.5;entryY=1;"
        ),
        value="更新 W<sub>α</sub>, b<sub>α</sub>",
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
