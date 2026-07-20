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
FS_TITLE = drawio_fs("title", scale=_SCALE)
FS_LABEL = drawio_fs("label", scale=_SCALE)
FS_TICK = drawio_fs("tick", scale=_SCALE)
FS_BOX = drawio_fs("title", scale=(60 / 11) * _R)
FS_SWIM = drawio_fs("title", scale=(54 / 11) * _R)
FS_BODY = drawio_fs("label", scale=5.1 * _R)
FS_EDGE = drawio_fs("tick", scale=7.0 * _R)

TEXT = "text;html=1;strokeColor=none;fillColor=none;"


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
    # 左/右端与第二层、Focal 同步加宽；压缩第二层底部空档
    dx = 320
    out_w = 570 + dx          # 890，与左侧特征框同宽
    l2_w = 1200               # 原 900
    l2_extra = l2_w - 900
    out_extra = out_w - 480
    l2_h = 880                # 原 1170，收掉底部空档
    l2_x = 2460 + dx
    l2_y = 320
    out_x = 3540 + dx + l2_extra
    out_y = 620
    out_h = 480
    # Focal / 标签下移，与输出框拉开；避免竖向虚线压字
    focal_y = max(l2_y + l2_h + 120, out_y + out_h + 280)
    d = Diagram(page_w=4200 + dx + l2_extra + out_extra, page_h=max(1980, focal_y + 360))

    d.box(
        "input",
        "<b>短期时序突变特征</b><br>"
        '<font style="font-size:51px">'
        "z<sub>i,t</sub> ∈ ℝ<sup>|𝒜|W + |ℬ|(W+1)</sup><br>"
        "（A/B 组 Lag + B 组加权突变）</font>",
        120, 690, 570 + dx, 330,
        style=(
            "rounded=1;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;"
            f"fontSize={FS_BOX};arcSize=8;"
        ),
    )

    # layer 1 swimlane
    d.box(
        "layer1-box", "第一层：异构基分类器",
        840 + dx, 330, 900, 1096,
        style=(
            "swimlane;html=1;startSize=90;fillColor=#e3f2fd;strokeColor=#1565c0;"
            f"fontStyle=1;fontSize={FS_SWIM};rounded=1;arcSize=6;"
        ),
    )
    d.box(
        "layer1-formula",
        '<font style="font-size:51px">'
        "ℳ = {M<sub>m</sub>}<sub>m=1</sub><sup>N</sup></font>",
        30, 106, 840, 72,
        style=TEXT + "align=center;verticalAlign=middle;",
        parent="layer1-box",
    )
    d.box(
        "m1",
        "<b>M<sub>1</sub></b><br>"
        '<font style="font-size:45px">基分类器</font>',
        90, 204, 360, 180,
        style=(
            "rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#1565c0;"
            f"fontSize={FS_SWIM};"
        ),
        parent="layer1-box",
    )
    d.box(
        "m1-out",
        "p<sub>i,t</sub><sup>(1)</sup>",
        570, 220, 240, 150,
        style=(
            "rounded=1;whiteSpace=wrap;html=1;fillColor=#bbdefb;strokeColor=#1565c0;"
            f"fontSize={FS_BODY};"
        ),
        parent="layer1-box",
    )
    d.box(
        "dots1",
        '<font style="font-size:90px;color:#666666">⋮</font>',
        210, 414, 120, 120,
        style=TEXT + "align=center;verticalAlign=middle;",
        parent="layer1-box",
    )
    d.box(
        "dots-mid",
        '<font style="font-size:45px;color:#888888">M<sub>2</sub>, …, M<sub>N−1</sub></font>',
        90, 520, 720, 76,
        style=TEXT + "align=center;",
        parent="layer1-box",
    )
    d.box(
        "dots2",
        '<font style="font-size:90px;color:#666666">⋮</font>',
        210, 594, 120, 120,
        style=TEXT + "align=center;verticalAlign=middle;",
        parent="layer1-box",
    )
    d.box(
        "mN",
        "<b>M<sub>N</sub></b><br>"
        '<font style="font-size:45px">基分类器</font>',
        90, 744, 360, 180,
        style=(
            "rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#1565c0;"
            f"fontSize={FS_SWIM};"
        ),
        parent="layer1-box",
    )
    d.box(
        "mN-out",
        "p<sub>i,t</sub><sup>(N)</sup>",
        570, 760, 240, 150,
        style=(
            "rounded=1;whiteSpace=wrap;html=1;fillColor=#bbdefb;strokeColor=#1565c0;"
            f"fontSize={FS_BODY};"
        ),
        parent="layer1-box",
    )
    d.box(
        "layer1-note",
        '<font style="font-size:45px;color:#555555">'
        "N ≥ 2，基分类器使用<br>Bagging 族、梯度提升树等</font>",
        30, 970, 840, 106,
        style=TEXT + "align=center;",
        parent="layer1-box",
    )

    d.box(
        "pvec",
        "<b>概率向量</b><br>"
        '<font style="font-size:51px">'
        "p<sub>i,t</sub> =<br>"
        "[p<sup>(1)</sup>, …, p<sup>(N)</sup>]<sup>T</sup></font>",
        1890 + dx, 690, 390, 330,
        style=(
            "rounded=1;whiteSpace=wrap;html=1;fillColor=#e8eaf6;strokeColor=#3949ab;"
            f"fontSize={FS_SWIM};"
        ),
    )

    # layer 2：加宽；步骤略增高、间距收紧，去掉底部大块留白
    step_w = l2_w - 180
    d.box(
        "layer2-box", "第二层：Attention 样本级融合",
        l2_x, l2_y, l2_w, l2_h,
        style=(
            "swimlane;startSize=84;fillColor=#fff3e0;strokeColor=#e65100;"
            f"fontStyle=1;fontSize={FS_SWIM};rounded=1;arcSize=6;"
        ),
    )
    d.box(
        "attn-step1",
        "① 线性变换<br>"
        '<font style="font-size:45px">W<sub>α</sub>·p<sub>i,t</sub> + b<sub>α</sub></font>',
        90, 100, step_w, 185,
        style=(
            "rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#e65100;"
            f"fontSize={FS_BODY};"
        ),
        parent="layer2-box",
    )
    d.box(
        "attn-step2",
        "② Softmax 归一化<br>"
        '<font style="font-size:45px">'
        "α<sub>i,t</sub><sup>(m)</sup>，Σ<sub>m</sub>α = 1</font>",
        90, 320, step_w, 185,
        style=(
            "rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#e65100;"
            f"fontSize={FS_BODY};"
        ),
        parent="layer2-box",
    )
    d.box(
        "attn-step3",
        "③ 加权组合<br>"
        '<font style="font-size:45px">'
        "ŷ<sub>i,t</sub> = Σ<sub>m=1</sub><sup>N</sup> α<sup>(m)</sup>·p<sup>(m)</sup></font>",
        90, 540, step_w, 185,
        style=(
            "rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#e65100;"
            f"fontSize={FS_BODY};"
        ),
        parent="layer2-box",
    )
    d.box(
        "attn-note",
        '<font style="font-size:45px;color:#555555">'
        "样本自适应权重，可解释各专家贡献占比</font>",
        60, 755, l2_w - 120, 80,
        style=TEXT + "align=center;",
        parent="layer2-box",
    )

    d.box(
        "output",
        f'<font style="font-size:{FS_SWIM}px"><b>融合故障概率</b></font><br><br>'
        '<font style="font-size:51px">ŷ<sub>i,t</sub> ∈ [0, 1]</font>',
        out_x, out_y, out_w, out_h,
        style=(
            "rounded=1;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;"
            f"fontSize={FS_SWIM};arcSize=8;spacing=16;verticalAlign=middle;"
        ),
    )
    d.box(
        "focal",
        '<font style="font-size:54px"><b>Focal Loss</b>  ℒ<sub>FL</sub></font><br>'
        '<font style="font-size:42px">'
        "对易分样本降权，强化少数类故障样本<br>"
        "在验证集上更新 W<sub>α</sub>, b<sub>α</sub>（γ=2）</font>",
        l2_x, focal_y, l2_w, 200,
        style=(
            "rounded=1;whiteSpace=wrap;html=1;fillColor=#ffebee;strokeColor=#c62828;"
            "fontSize=42;dashed=1;dashPattern=8 8;"
            "align=center;verticalAlign=middle;spacingTop=14;spacingBottom=14;"
        ),
    )
    d.box(
        "ylabel",
        "标签 y<sub>i,t</sub> ∈ {0,1}",
        out_x, focal_y + 20, out_w, 160,
        style=(
            "rounded=1;whiteSpace=wrap;html=1;fillColor=#fce4ec;strokeColor=#c62828;"
            "fontSize=48;align=center;verticalAlign=middle;"
        ),
    )

    # legend（与 Focal 底对齐一带）
    leg_y = focal_y
    d.box(
        "legend-box", "", 120, leg_y, 600, 234,
        style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fafafa;strokeColor=#cccccc;dashed=1;",
    )
    d.box(
        "legend-title", "图例", 156, leg_y + 14, 120, 54,
        style=TEXT + f"fontStyle=1;fontSize={FS_BODY};",
    )
    d.free_edge(
        "legend1-line", 156, leg_y + 94, 306, leg_y + 94,
        style="endArrow=classic;html=1;strokeWidth=3;strokeColor=#333333;",
    )
    d.box(
        "legend1", "推理数据流", 336, leg_y + 68, 330, 60,
        style=TEXT + f"fontSize={FS_TICK};align=left;",
    )
    d.free_edge(
        "legend2-line", 156, leg_y + 166, 306, leg_y + 166,
        style="endArrow=classic;html=1;strokeWidth=3;strokeColor=#c62828;dashed=1;",
    )
    d.box(
        "legend2", "训练 / 损失", 336, leg_y + 140, 330, 60,
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
    d.edge(
        "e-out-focal", "output", "focal",
        style=(
            "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;"
            "html=1;strokeWidth=2;strokeColor=#c62828;dashed=1;"
            # 从输出框左侧下行，走第二层与输出之间的廊道，避开下方「标签」框
            "exitX=0;exitY=0.75;entryX=0.88;entryY=0;"
        ),
    )
    d.edge(
        "e-y-focal", "ylabel", "focal",
        style=(
            "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;"
            "html=1;strokeWidth=2;strokeColor=#c62828;dashed=1;"
            "exitX=0;exitY=0.5;entryX=1;entryY=0.55;"
        ),
    )
    d.edge(
        "e-focal-back", "focal", "layer2-box",
        style=(
            "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;"
            f"html=1;strokeWidth=2;strokeColor=#c62828;dashed=1;fontSize={FS_TICK};"
            "labelBackgroundColor=#FFFFFF;"
            "exitX=0.22;exitY=0;entryX=0.5;entryY=1;"
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
