#!/usr/bin/env python3
"""第五章：智慧 SSD 运维软件总体架构（四层）。

用布局参数生成 draw.io XML，并可选导出 PDF。
对应 figure/chap5-software-structure.pdf。

用法（项目根目录）:
    python3 figure_codes/chap5_software_structure.py
"""

from __future__ import annotations

import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_XML = Path(__file__).resolve().parent / "chap5-software-structure.xml"
OUT_PDF = ROOT / "figure" / "chap5-software-structure.pdf"

# 黑白印刷：外层虚线框，内层实线白底
LAYER = (
    "rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;"
    "strokeColor=#111111;dashed=1;dashPattern=8 6;"
)
GROUP = (
    "rounded=0;whiteSpace=wrap;html=1;align=left;verticalAlign=top;"
    "spacingLeft=10;spacingTop=6;fillColor=#ffffff;strokeColor=#111111;"
    "fontSize=12;fontStyle=1;"
)
GROUP_DASH = GROUP + "dashed=1;dashPattern=6 4;"
BOX = (
    "rounded=0;whiteSpace=wrap;html=1;align=center;verticalAlign=middle;"
    "fillColor=#ffffff;strokeColor=#111111;fontSize=12;"
)
CYL = (
    "shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;"
    "backgroundOutline=1;size=10;fillColor=#ffffff;strokeColor=#111111;"
    "fontSize=13;fontStyle=1;align=center;verticalAlign=middle;"
)
LABEL = (
    "text;html=1;align=center;verticalAlign=middle;"
    "fontSize=13;fontStyle=1;strokeColor=none;fillColor=none;"
)


def _geom(el: ET.Element, x: float, y: float, w: float, h: float) -> None:
    ET.SubElement(
        el, "mxGeometry",
        {"x": str(x), "y": str(y), "width": str(w), "height": str(h), "as": "geometry"},
    )


class Arch:
    def __init__(self, page_w: int = 1040, page_h: int = 320) -> None:
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

    def box(
        self, cid: str, value: str, x: float, y: float, w: float, h: float,
        *, style: str = BOX,
    ) -> None:
        c = self._cell(cid, value=value, style=style, vertex="1")
        _geom(c, x, y, w, h)

    def to_xml(self) -> str:
        mxfile = ET.Element(
            "mxfile",
            {
                "host": "app.diagrams.net",
                "modified": "2026-07-18T00:00:00.000Z",
                "agent": "chap5_software_structure.py",
                "version": "22.1.0",
            },
        )
        diagram = ET.SubElement(
            mxfile, "diagram",
            {"id": "software-structure", "name": "软件总体架构"},
        )
        diagram.append(self.model)
        ET.indent(mxfile, space="  ")
        return '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(
            mxfile, encoding="unicode",
        ) + "\n"


def build() -> Arch:
    """四层架构：业务层 / 服务层 / 数据层 / 基础层（与当前 PDF 一致）。"""
    a = Arch()

    # 画布：左标签 + 右内容区
    lx, lw = 8, 100          # 层名标签
    cx, cw = 118, 900        # 各层内容外框
    gap = 8
    y = 8

    # ---------- 业务层 ----------
    h1 = 58
    a.box("lab1", "业务层<br>（前端承载）", lx, y, lw, h1, style=LABEL)
    a.box("L1", "", cx, y, cw, h1, style=LAYER)
    bw, bh = 160, 36
    by = y + (h1 - bh) / 2
    a.box("biz1", "SSD 盘管理", cx + 210, by, bw, bh)
    a.box("biz2", "预警处理", cx + 520, by, bw, bh)
    y += h1 + gap

    # ---------- 服务层 ----------
    h2 = 118
    a.box("lab2", "服务层", lx, y, lw, h2, style=LABEL)
    a.box("L2", "", cx, y, cw, h2, style=LAYER)

    # 左：数据管理类服务
    g1x, g1y, g1w, g1h = cx + 12, y + 8, 430, 102
    a.box("g-data", "数据管理类服务", g1x, g1y, g1w, g1h, style=GROUP)
    sw, sh = 92, 52
    sy = g1y + 36
    sx0 = g1x + 16
    gap_s = 10
    for i, title in enumerate([
        "SSD 盘数据<br>管理服务",
        "日志数据<br>管理服务",
        "故障数据<br>管理服务",
        "预警数据<br>管理服务",
    ]):
        a.box(f"svc{i}", title, sx0 + i * (sw + gap_s), sy, sw, sh)

    # 右：故障预测算法服务
    g2x, g2y, g2w, g2h = cx + 456, y + 8, 430, 102
    a.box(
        "g-algo",
        "故障预测算法服务（定时调度 / 手动触发）",
        g2x, g2y, g2w, g2h, style=GROUP_DASH,
    )
    aw, ah = 88, 52
    ay = g2y + 36
    ax0 = g2x + 18
    gap_a = 12
    for i, title in enumerate(["预处理", "特征构造", "模型推理", "阈值判定"]):
        a.box(f"algo{i}", title, ax0 + i * (aw + gap_a), ay, aw, ah)
    y += h2 + gap

    # ---------- 数据层 ----------
    h3 = 72
    a.box("lab3", "数据层", lx, y, lw, h3, style=LABEL)
    a.box("L3", "", cx, y, cw, h3, style=LAYER)
    cyl_w, cyl_h = 110, 48
    a.box(
        "db", "MySQL",
        cx + 280, y + (h3 - cyl_h) / 2, cyl_w, cyl_h, style=CYL,
    )
    a.box(
        "model", "模型文件<br>（S3 / OSS 等）",
        cx + 500, y + (h3 - 44) / 2, 160, 44,
    )
    y += h3 + gap

    # ---------- 基础层 ----------
    h4 = 40
    a.box("lab4", "基础层", lx, y, lw, h4, style=LABEL)
    a.box("L4", "", cx, y, cw, h4, style=LAYER)
    a.box(
        "infra", "计算资源 · 存储系统 · 网络环境",
        cx, y, cw, h4,
        style=(
            "text;html=1;align=center;verticalAlign=middle;"
            "fontSize=13;strokeColor=none;fillColor=none;"
        ),
    )

    return a


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
    xml = build().to_xml()
    OUT_XML.write_text(xml, encoding="utf-8")
    print(f"wrote {OUT_XML.relative_to(ROOT)}")
    if export_pdf(OUT_XML, OUT_PDF):
        print(f"wrote {OUT_PDF.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
