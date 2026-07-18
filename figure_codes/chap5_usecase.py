#!/usr/bin/env python3
"""第五章用例图：用布局参数生成 draw.io XML（并可选导出 PDF）。

手写 XML 里散落的坐标、重复 include 边、迭代遗留注释都收敛到本文件。
改间距/列位置时只动 Layout，再运行本脚本即可。
"""

from __future__ import annotations

import subprocess
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_XML = Path(__file__).resolve().parent / "chap5-usecase.xml"
OUT_PDF = ROOT / "figure" / "chap5-usecase.pdf"


@dataclass(frozen=True)
class Layout:
    """画布与列几何：所有“硬编码坐标”的唯一来源。"""

    page_w: int = 1200
    page_h: int = 600

    boundary_x: int = 70
    boundary_y: int = 10
    boundary_w: int = 1010
    boundary_h: int = 555

    divider_x: int = 575
    divider_top: int = 50
    divider_bot: int = 550

    # 运维用户总线
    bus_x: int = 105
    bus_top_y: int = 117
    bus_mid_y: int = 307  # 对齐「管理 SMART 日志」中线
    bus_bot_y: int = 520
    actor_user_x: int = 20
    actor_user_y: int = 262
    actor_line_x0: int = 50

    # 管理侧列
    mgmt_primary_x: int = 150
    mgmt_child_x: int = 390
    primary_w: int = 150
    primary_h: int = 54
    child_w: int = 130
    child_h: int = 46
    child_w_narrow: int = 120

    # 预警侧列
    warn_primary_x: int = 690
    warn_child_x: int = 920
    sched_x: int = 640
    sched_y: int = 102
    sched_line_x0: int = 670
    sched_line_y: int = 127
    warn_riser_x: int = 660

    label_mgmt_x: int = 300
    label_warn_x: int = 800


@dataclass
class UseCase:
    uid: str
    title: str
    x: int
    y: int
    w: int
    h: int
    font: int = 14


@dataclass
class IncludeFan:
    """主用例 → 若干 include 子用例（同列垂直堆叠）。"""

    parent: str
    children: list[str]
    label_index: int = 0  # 哪一条带 <<include>> 标签


@dataclass
class Diagram:
    layout: Layout = field(default_factory=Layout)
    use_cases: dict[str, UseCase] = field(default_factory=dict)
    include_fans: list[IncludeFan] = field(default_factory=list)
    # 额外 include：source → target，方向与标签
    extra_includes: list[tuple[str, str, str, dict]] = field(default_factory=list)


def _build_diagram() -> Diagram:
    L = Layout()
    d = Diagram(layout=L)

    def add(uid: str, title: str, x: int, y: int, *, primary: bool = True, narrow: bool = False) -> None:
        w = L.child_w_narrow if narrow else (L.primary_w if primary else L.child_w)
        h = L.primary_h if primary else L.child_h
        d.use_cases[uid] = UseCase(uid, title, x, y, w, h, 14 if primary else 13)

    # 管理侧
    add("uc01", "维护SSD盘资产", L.mgmt_primary_x, 90)
    add("uc01a", "查询SSD盘列表", L.mgmt_child_x, 35, primary=False)
    add("uc01b", "新增SSD盘信息", L.mgmt_child_x, 88, primary=False)
    add("uc01c", "编辑SSD盘信息", L.mgmt_child_x, 141, primary=False)
    add("uc01d", "删除SSD盘记录", L.mgmt_child_x, 194, primary=False)
    add("uc02", "管理 SMART 日志", L.mgmt_primary_x, 280)
    add("uc02a", "按条件检索日志", L.mgmt_child_x, 265, primary=False)
    add("uc02b", "导入/维护日志", L.mgmt_child_x, 320, primary=False)
    add("uc05", "维护故障记录", L.mgmt_primary_x, 410)
    add("uc05a", "查询故障记录", L.mgmt_child_x, 395, primary=False)
    add("uc05b", "登记故障记录", L.mgmt_child_x, 450, primary=False)

    # 预警侧
    add("uc03", "生成故障预警", L.warn_primary_x, 100)
    add("uc03m", "手动触发故障预警", L.warn_primary_x, 200)
    add("uc03b", "拉取增量日志", L.warn_child_x, 50, primary=False)
    add("uc03c", "执行模型推理", L.warn_child_x, 105, primary=False)
    add("uc03d", "写入预警记录", L.warn_child_x, 160, primary=False)
    add("uc04", "处置预警记录", L.warn_primary_x, 340)
    add("uc04b", "忽略预警", L.warn_child_x, 310, primary=False, narrow=True)
    add("uc04a", "确认故障", L.warn_child_x, 375, primary=False, narrow=True)

    d.include_fans = [
        IncludeFan("uc01", ["uc01a", "uc01b", "uc01c", "uc01d"], label_index=1),
        IncludeFan("uc02", ["uc02a", "uc02b"], label_index=0),
        IncludeFan("uc05", ["uc05a", "uc05b"], label_index=0),
        IncludeFan("uc03", ["uc03b", "uc03c", "uc03d"], label_index=1),
        IncludeFan("uc04", ["uc04b", "uc04a"], label_index=1),
    ]
    # 手动触发 include 生成（竖直）
    d.extra_includes = [
        ("uc03m", "uc03", "vertical", {"exitX": 0.5, "exitY": 0.0, "entryX": 0.5, "entryY": 1.0}),
    ]
    return d


# ---------- XML helpers ----------

def _style(*flags: str, **kv: object) -> str:
    """draw.io style：裸 flag（如 ellipse）+ key=value。"""
    parts = [f"{f};" for f in flags]
    parts.extend(f"{k}={v};" for k, v in kv.items())
    return "".join(parts)


def _geom(parent: ET.Element, x: float, y: float, w: float, h: float) -> None:
    ET.SubElement(parent, "mxGeometry", {"x": str(x), "y": str(y), "width": str(w), "height": str(h), "as": "geometry"})


def _edge_geom(parent: ET.Element, *, points: list[tuple[float, float]] | None = None,
               source: tuple[float, float] | None = None, target: tuple[float, float] | None = None) -> None:
    g = ET.SubElement(parent, "mxGeometry", {"relative": "1", "as": "geometry"})
    if source is not None:
        ET.SubElement(g, "mxPoint", {"x": str(source[0]), "y": str(source[1]), "as": "sourcePoint"})
    if target is not None:
        ET.SubElement(g, "mxPoint", {"x": str(target[0]), "y": str(target[1]), "as": "targetPoint"})
    if points:
        arr = ET.SubElement(g, "Array", {"as": "points"})
        for px, py in points:
            ET.SubElement(arr, "mxPoint", {"x": str(px), "y": str(py)})


def _cell(root: ET.Element, cid: str, *, value: str = "", style: str = "",
          vertex: bool = False, edge: bool = False, source: str | None = None,
          target: str | None = None) -> ET.Element:
    attrs: dict[str, str] = {"id": cid, "value": value, "style": style, "parent": "1"}
    if vertex:
        attrs["vertex"] = "1"
    if edge:
        attrs["edge"] = "1"
    if source:
        attrs["source"] = source
    if target:
        attrs["target"] = target
    return ET.SubElement(root, "mxCell", attrs)


def _center(uc: UseCase) -> tuple[float, float]:
    return uc.x + uc.w / 2, uc.y + uc.h / 2


def build_xml(d: Diagram) -> str:
    L = d.layout
    model = ET.Element(
        "mxGraphModel",
        {
            "dx": "1400", "dy": "800", "grid": "1", "gridSize": "10",
            "page": "1", "pageScale": "1",
            "pageWidth": str(L.page_w), "pageHeight": str(L.page_h),
            "math": "0", "shadow": "0",
        },
    )
    root = ET.SubElement(model, "root")
    ET.SubElement(root, "mxCell", {"id": "0"})
    ET.SubElement(root, "mxCell", {"id": "1", "parent": "0"})

    # 边界 / 分区
    c = _cell(root, "boundary", value="智慧 SSD 运维系统",
              style=_style(rounded=0, whiteSpace="wrap", html=1, dashed=1, dashPattern="8 8",
                           strokeWidth=2, verticalAlign="top", align="left",
                           spacingLeft=12, spacingTop=6, fontStyle=1, fontSize=16),
              vertex=True)
    _geom(c, L.boundary_x, L.boundary_y, L.boundary_w, L.boundary_h)

    for cid, text, x in (("label-left", "管理侧", L.label_mgmt_x), ("label-right", "预警侧", L.label_warn_x)):
        c = _cell(root, cid, value=text,
                  style=_style("text", html=1, align="center", fontSize=14, fontStyle=1, fontColor="#666666"),
                  vertex=True)
        _geom(c, x, 26, 70, 22)

    c = _cell(root, "divider", style=_style(endArrow="none", html=1, strokeColor="#BDBDBD",
                                            dashed=1, dashPattern="6 6"), edge=True)
    _edge_geom(c, source=(L.divider_x, L.divider_top), target=(L.divider_x, L.divider_bot))

    # Actors
    c = _cell(root, "actor-user", value="运维用户",
              style=_style(shape="umlActor", verticalLabelPosition="bottom", verticalAlign="top",
                           html=1, outlineConnect=0, fontSize=15),
              vertex=True)
    _geom(c, L.actor_user_x, L.actor_user_y, 30, 60)

    c = _cell(root, "actor-scheduler", value="定时调度器",
              style=_style(shape="umlActor", verticalLabelPosition="bottom", verticalAlign="top",
                           html=1, outlineConnect=0, fontSize=14),
              vertex=True)
    _geom(c, L.sched_x, L.sched_y, 30, 50)

    # Use cases
    for uc in d.use_cases.values():
        c = _cell(root, uc.uid, value=uc.title,
                  style=_style("ellipse", whiteSpace="wrap", html=1, fontSize=uc.font),
                  vertex=True)
        _geom(c, uc.x, uc.y, uc.w, uc.h)

    # 运维用户：水平干线 + 竖总线 + 短分支 + 底边
    uc02 = d.use_cases["uc02"]
    uc01 = d.use_cases["uc01"]
    uc05 = d.use_cases["uc05"]
    uc03m = d.use_cases["uc03m"]
    uc04 = d.use_cases["uc04"]

    c = _cell(root, "e-user-uc02",
              style=_style(endArrow="none", html=1, rounded=0, entryX=0, entryY=0.5),
              edge=True, target="uc02")
    _edge_geom(c, source=(L.actor_line_x0, L.bus_mid_y))

    c = _cell(root, "e-vbus", style=_style(endArrow="none", html=1, rounded=0), edge=True)
    _edge_geom(c, source=(L.bus_x, L.bus_top_y), target=(L.bus_x, L.bus_bot_y))

    c = _cell(root, "e-bus-uc01",
              style=_style(endArrow="none", html=1, rounded=0, entryX=0, entryY=0.5),
              edge=True, target="uc01")
    _edge_geom(c, source=(L.bus_x, uc01.y + uc01.h / 2))

    c = _cell(root, "e-bus-uc05",
              style=_style(endArrow="none", html=1, rounded=0, entryX=0, entryY=0.5),
              edge=True, target="uc05")
    _edge_geom(c, source=(L.bus_x, uc05.y + uc05.h / 2))

    c = _cell(root, "e-bot-h", style=_style(endArrow="none", html=1, rounded=0), edge=True)
    _edge_geom(c, source=(L.bus_x, L.bus_bot_y), target=(L.warn_riser_x, L.bus_bot_y))

    c = _cell(root, "e-bot-uc03m",
              style=_style(endArrow="none", html=1, rounded=0, entryX=0, entryY=0.5),
              edge=True, target="uc03m")
    _edge_geom(c, source=(L.warn_riser_x, L.bus_bot_y),
               points=[(L.warn_riser_x, uc03m.y + uc03m.h / 2)])

    c = _cell(root, "e-bot-uc04",
              style=_style(endArrow="none", html=1, rounded=0, entryX=0.5, entryY=1),
              edge=True, target="uc04")
    cx4, _ = _center(uc04)
    _edge_geom(c, source=(L.warn_riser_x, L.bus_bot_y), points=[(cx4, L.bus_bot_y)])

    # 调度器
    c = _cell(root, "e-sched-uc03",
              style=_style(endArrow="none", html=1, rounded=0, entryX=0, entryY=0.5),
              edge=True, target="uc03")
    _edge_geom(c, source=(L.sched_line_x0, L.sched_line_y))

    # include fans
    for fan in d.include_fans:
        n = len(fan.children)
        for i, child in enumerate(fan.children):
            exit_y = 0.2 + 0.6 * i / max(n - 1, 1) if n > 1 else 0.5
            # 两端均匀时用固定比例更贴近现图
            if n == 2:
                exit_y = 0.35 if i == 0 else 0.65
            elif n == 3:
                exit_y = (0.25, 0.5, 0.75)[i]
            elif n == 4:
                exit_y = (0.2, 0.4, 0.6, 0.8)[i]
            labeled = i == fan.label_index
            style_kw: dict[str, object] = dict(
                endArrow="open", dashed=1, html=1, rounded=0,
                exitX=1, exitY=exit_y, entryX=0, entryY=0.5, fontSize=11,
            )
            if labeled:
                style_kw["labelBackgroundColor"] = "#FFFFFF"
            c = _cell(root, f"e-inc-{fan.parent}-{child}",
                      value="<<include>>" if labeled else "",
                      style=_style(**style_kw), edge=True,
                      source=fan.parent, target=child)
            _edge_geom(c)

    for src, tgt, _kind, ports in d.extra_includes:
        style = _style(
            endArrow="open", dashed=1, html=1, rounded=0, fontSize=11,
            labelBackgroundColor="#FFFFFF",
            exitX=ports["exitX"], exitY=ports["exitY"],
            entryX=ports["entryX"], entryY=ports["entryY"],
        )
        c = _cell(root, f"e-inc-{src}-{tgt}", value="<<include>>",
                  style=style, edge=True, source=src, target=tgt)
        _edge_geom(c)

    # 确认故障 → 登记故障记录（下出、右入）
    uc04a = d.use_cases["uc04a"]
    uc05b = d.use_cases["uc05b"]
    jx = uc05b.x + uc05b.w + 8
    jy = uc05b.y + uc05b.h / 2 - 2
    drop_x = uc04a.x + uc04a.w / 2
    mid_y = uc05b.y + uc05b.h / 2

    c = _cell(root, "j-reg-right",
              style=_style("ellipse", fillColor="none", strokeColor="none",
                           movable=0, resizable=0, rotatable=0, deletable=0),
              vertex=True)
    _geom(c, jx, jy, 4, 4)

    c = _cell(root, "e-inc-04a-j", value="<<include>>",
              style=_style(endArrow="none", dashed=1, html=1, rounded=0,
                           exitX=0.5, exitY=1, entryX=0.5, entryY=0.5, fontSize=11,
                           labelBackgroundColor="#FFFFFF"),
              edge=True, source="uc04a", target="j-reg-right")
    _edge_geom(c, points=[(drop_x, mid_y)])

    c = _cell(root, "e-inc-j-05b",
              style=_style(endArrow="open", dashed=1, html=1, rounded=0,
                           exitX=0, exitY=0.5, entryX=1, entryY=0.5, entryPerimeter=0),
              edge=True, source="j-reg-right", target="uc05b")
    _edge_geom(c)

    # 包装为 mxfile
    mxfile = ET.Element("mxfile", {"host": "app.diagrams.net", "agent": "chap5_usecase.py", "version": "22.1.0"})
    diagram = ET.SubElement(mxfile, "diagram", {"id": "usecase", "name": "用例图"})
    diagram.append(model)

    # html=1 下需双重转义，否则 <<include>> 会被当成 HTML 标签吃掉
    rough = ET.tostring(mxfile, encoding="unicode")
    rough = rough.replace(
        'value="&lt;&lt;include&gt;&gt;"',
        'value="&amp;lt;&amp;lt;include&amp;gt;&amp;gt;"',
    )
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + rough + "\n"


def export_pdf(xml_path: Path, pdf_path: Path) -> bool:
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        subprocess.run(
            ["drawio", "-x", "-f", "pdf", "--crop", "-b", "0",
             "-o", str(pdf_path), str(xml_path)],
            check=True,
            capture_output=True,
            text=True,
        )
        return True
    except (FileNotFoundError, subprocess.CalledProcessError) as exc:
        print(f"[warn] drawio 导出失败，仅写入 XML: {exc}")
        return False


def main() -> None:
    diagram = _build_diagram()
    xml = build_xml(diagram)
    OUT_XML.write_text(xml, encoding="utf-8")
    print(f"wrote {OUT_XML.relative_to(ROOT)}")
    if export_pdf(OUT_XML, OUT_PDF):
        print(f"wrote {OUT_PDF.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
