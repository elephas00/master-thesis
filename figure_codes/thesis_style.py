"""学位论文统一绘图样式（第三、四章定量图共用）

柱状图与折线图使用**独立色序**：
  - 柱图 COLORS_BAR / BAR_STYLE：白底黑边为第 1 优先（印刷友好）
  - 折线 COLORS_LINE / LINE_STYLE：黑为第 1 优先（主系列），不含白色

需要 N 个系列时分别按 BAR_PRIORITY / LINE_PRIORITY 取前 N。

多子图约定:
  - 每个子图各自维护图例
  - 跨子图语义相同的系列共用同一 swatch
  - 分栏展示可用同一主系列，不必为区分面板另占色位
  - Figure 级共享图例用 fig_shared_legend（统一边框 +「图例」标题 + 整体居中）
"""

from __future__ import annotations

from typing import Any

# ---------------------------------------------------------------------------
# 版心宽度（研究生模板 A4、左右 2.5 cm → 160 mm）
# 出图固有宽对齐此值后，正文可用 \\includegraphics 默认尺寸插入。
# ---------------------------------------------------------------------------
TEXT_WIDTH_MM = 160.0
TEXT_WIDTH_IN = TEXT_WIDTH_MM / 25.4  # ≈ 6.299 in
TEXT_WIDTH_PT = TEXT_WIDTH_IN * 72.0  # ≈ 453.54 pt

# ---------------------------------------------------------------------------
# 墨色与版式常量（轴线/文字；非数据系列色）
# ---------------------------------------------------------------------------
C_INK = "#111111"
C_ZERO = "#444444"
C_GRID = "#D0D0D0"
C_EDGE = C_INK
C_SEP = "#FFFFFF"
C_BG = "#FFFFFF"
BAR_LW = 0.85
C_LEGEND_FRAME = "#CBD5E1"
C_SPINE_MUTED = "#BDBDBD"

# ---------------------------------------------------------------------------
# 柱图色序（b1..b6；白 = 第 1 优先）
# Okabe–Ito 改编：第 2 位用灰作第一对照，第 3 位恢复 Okabe 天蓝
# 因为只有基线对比用到了567的颜色，5是在TCAN的位置，都是0，这个蓝色不会显示，所以把后置获取更明显的对比
# ---------------------------------------------------------------------------
COLORS_BAR: list[str] = [
    "#FFFFFF",  # 1 白底 — 优先（黑边勾勒，印刷清晰）
    "#5D6D7E",  # 2 灰 — 第一对照
    "#56B4E9",  # 3 Okabe 天蓝
    "#E69F00",  # 4 琥珀
    "#0072B2",  # 7 Okabe 蓝
    "#CC79A7",  # 6 紫红
    "#009E73",  # 5 绿蓝
]

HATCH_BAR: list[str] = [
    "",         # 1 白
    "",         # 2 灰 — 无底纹
    "..",       # 3 天蓝
    "///",      # 4 琥珀
    "+++",       # 7 蓝
    "xxx",       # 6 紫红
    "\\\\\\",   # 5 绿蓝
]

# ---------------------------------------------------------------------------
# 折线色序（l1..l6；黑 = 第 1 优先，与柱图独立）
# Okabe–Ito 改编：黑优先，去掉白/黄（细线白底不可读）
# ---------------------------------------------------------------------------
COLORS_LINE: list[str] = [
    C_INK,      # 1 黑 — 主系列
    "#E69F00",  # 2 琥珀
    "#0072B2",  # 3 蓝
    "#009E73",  # 4 绿蓝
    "#D55E00",  # 5 朱红
    "#CC79A7",  # 6 紫红
]

LINESTYLE_PRIORITY: list[str] = [
    "-",                         # 1 实线
    (0, (8, 3)),                 # 2 长划（宽间隙）
    (0, (1, 1)),                 # 3 密点（比默认 : 更清晰）
    (0, (5, 2, 1, 2)),           # 4 划-点
    (0, (4, 1.5, 1, 1.5, 1, 1.5)),  # 5 划-点-点
    (0, (2, 2)),                 # 6 短密划（与长划对照）
]
MARKER_PRIORITY: list[str] = ["o", "s", "^", "D", "v", "x"]

# 兼容旧名（柱图）
COLORS_PRIORITY = COLORS_BAR
HATCH_PRIORITY = HATCH_BAR
# 兼容旧名（折线实色；不再从柱图去白派生）
COLORS_FILL = COLORS_LINE

C_PRIMARY = COLORS_BAR[0]
C_SECONDARY = COLORS_BAR[1]
C_TERTIARY = COLORS_BAR[2]
C_QUATERNARY = COLORS_BAR[3]


# ---------------------------------------------------------------------------
# 柱状图字典 b1..b6
# ---------------------------------------------------------------------------
BAR_STYLE: dict[str, dict[str, str]] = {
    f"b{i + 1}": {
        "color": COLORS_BAR[i],
        "hatch": HATCH_BAR[i],
        "edge": C_EDGE,
    }
    for i in range(len(COLORS_BAR))
}

LEGEND_STYLE = BAR_STYLE
BAR_PRIORITY: list[str] = [f"b{i}" for i in range(1, len(COLORS_BAR) + 1)]

# ---------------------------------------------------------------------------
# 折线图字典 l1..lN（色 + 线型 + 标记）
# ---------------------------------------------------------------------------
_n_line = min(len(COLORS_LINE), len(LINESTYLE_PRIORITY), len(MARKER_PRIORITY))
LINE_STYLE: dict[str, dict[str, Any]] = {
    f"l{i + 1}": {
        "color": COLORS_LINE[i],
        "ls": LINESTYLE_PRIORITY[i],
        "marker": MARKER_PRIORITY[i],
    }
    for i in range(_n_line)
}
LINE_PRIORITY: list[str] = [f"l{i}" for i in range(1, _n_line + 1)]


def bar_priority_keys() -> list[str]:
    """柱图优先序键列表。"""
    return list(BAR_PRIORITY)


def bar_key(i: int) -> str:
    keys = bar_priority_keys()
    return keys[i % len(keys)]


def bar_style(i: int) -> dict[str, str]:
    """柱图第 i 个系列（0-based），按 BAR_PRIORITY 取。"""
    return dict(BAR_STYLE[bar_key(i)])


def line_priority_keys() -> list[str]:
    """折线优先序键列表。"""
    return list(LINE_PRIORITY)


def line_key(i: int) -> str:
    keys = line_priority_keys()
    return keys[i % len(keys)]


# ---------------------------------------------------------------------------
# 语义别名
# ---------------------------------------------------------------------------
_pair0, _pair1 = bar_style(0), bar_style(1)
PAIR_MB = {"MB1": _pair0["color"], "MB2": _pair1["color"]}
PAIR_MB_HATCH = {"MB1": _pair0["hatch"], "MB2": _pair1["hatch"]}

# 读模式：折线字典前两档（黑 / 深蓝灰）
_ls0, _ls1 = LINE_STYLE["l1"], LINE_STYLE["l2"]
PAIR_READ = {"DefaultRead": _ls0["color"], "BestRead": _ls1["color"]}
PAIR_READ_HATCH = {"DefaultRead": HATCH_BAR[0], "BestRead": HATCH_BAR[1]}
PAIR_READ_LS = {"DefaultRead": _ls0["ls"], "BestRead": _ls1["ls"]}
PAIR_READ_MK = {"DefaultRead": _ls0["marker"], "BestRead": _ls1["marker"]}

_METHOD_ORDER = ["本文方法", "Mut-Rule", "RF", "AE", "TCAN", "MVT-RF", "Mut-RF"]
METHOD_COLORS = {
    m: bar_style(i)["color"] for i, m in enumerate(_METHOD_ORDER)
}
METHOD_HATCH = {
    m: bar_style(i)["hatch"] for i, m in enumerate(_METHOD_ORDER)
}

ROUND_STYLES = {
    rid: bar_style(i)
    for i, rid in enumerate([1, 2, 3])
}

CMAP_HEAT_HEX = [
    "#FFFFFF",
    "#B8D0E8",
    "#5B8FBF",
    "#2A5280",
    "#1E3A5F",
]


def _make_cmap_heat():
    from matplotlib.colors import LinearSegmentedColormap

    return LinearSegmentedColormap.from_list("thesis_blues", CMAP_HEAT_HEX, N=256)


CMAP_HEAT = _make_cmap_heat()

FONT = {
    "title": 11,
    "label": 10,
    "tick": 9,
    "legend": 9,
    "annot": 8,
    "note": 8,
}


def drawio_fs(role: str, *, scale: float) -> int:
    """drawio 画布字号：论文 FONT[role] × 画布倍率（导出后再缩到版心）。"""
    return max(1, int(round(FONT[role] * scale)))


def line_style(i: int) -> dict[str, Any]:
    """折线第 i 个系列（0-based）→ l1..lN（独立色序，含黑）。"""
    return dict(LINE_STYLE[line_key(i)])


def series_style(i: int) -> dict[str, Any]:
    """兼容别名：等同 line_style（折线/散点）；附带 hatch/edge 供偶发复用。"""
    st = line_style(i)
    st["hatch"] = HATCH_BAR[i % len(HATCH_BAR)]
    st["edge"] = C_EDGE
    return st


def bar_patch_kwargs(st: dict[str, str] | None = None, **extra: Any) -> dict[str, Any]:
    """ax.bar / Patch 统一参数：填充 + 底纹 + 黑边。"""
    if st is None:
        st = {"color": C_PRIMARY, "hatch": "", "edge": C_EDGE}
    kw: dict[str, Any] = {
        "color": st["color"],
        "hatch": st.get("hatch", ""),
        "edgecolor": st.get("edge", C_EDGE),
        "linewidth": BAR_LW,
    }
    kw.update(extra)
    return kw


def legend_swatch(key: str, label: str):
    """从 BAR_STYLE 取 Patch（柱图图例）。"""
    from matplotlib.patches import Patch

    st = BAR_STYLE[key]
    return Patch(
        facecolor=st["color"],
        hatch=st["hatch"],
        edgecolor=st["edge"],
        linewidth=BAR_LW,
        label=label,
    )


def apply_rc() -> None:
    import matplotlib.pyplot as plt

    plt.rcParams.update({
        "font.sans-serif": [
            "Arial Unicode MS", "PingFang SC", "SimHei", "DejaVu Sans",
        ],
        "axes.unicode_minus": False,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "font.size": FONT["tick"],
        "axes.titlesize": FONT["title"],
        "axes.labelsize": FONT["label"],
        "xtick.labelsize": FONT["tick"],
        "ytick.labelsize": FONT["tick"],
        "legend.fontsize": FONT["legend"],
    })


def savefig_text_width(
    fig,
    path,
    *,
    pad_inches: float = 0.04,
    facecolor: str = "white",
    match_width: bool = True,
    **kwargs: Any,
) -> None:
    """保存 PDF；默认将页面宽度精确缩放到 ``TEXT_WIDTH_PT``（栏宽）。

    先按 ``bbox_inches='tight'`` 裁白边，再整体等比缩放，避免仅改
    ``figsize`` 时 tight 裁剪导致最终宽度偏离版心。
    """
    import io
    from pathlib import Path

    from pypdf import PdfReader, PdfWriter

    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    if not match_width:
        fig.savefig(
            out,
            bbox_inches="tight",
            pad_inches=pad_inches,
            facecolor=facecolor,
            **kwargs,
        )
        return

    buf = io.BytesIO()
    fig.savefig(
        buf,
        format="pdf",
        bbox_inches="tight",
        pad_inches=pad_inches,
        facecolor=facecolor,
        **kwargs,
    )
    buf.seek(0)
    page = PdfReader(buf).pages[0]
    w = float(page.mediabox.width)
    if w <= 0:
        raise ValueError(f"empty PDF width for {out}")
    page.scale_by(TEXT_WIDTH_PT / w)
    writer = PdfWriter()
    writer.add_page(page)
    with out.open("wb") as fh:
        writer.write(fh)


def fit_drawio_pdf_width(path) -> float:
    """将 draw.io 导出的 PDF 页宽精确缩放到 ``TEXT_WIDTH_PT``。

    返回施加的缩放系数（``TEXT_WIDTH_PT / 原宽``）。画布字号宜用
    ``drawio_fs(..., scale≈原宽/栏宽)``，缩栏后接近 ``FONT`` 字号。
    """
    from pathlib import Path

    from pypdf import PdfReader, PdfWriter

    out = Path(path)
    reader = PdfReader(str(out))
    page = reader.pages[0]
    w = float(page.mediabox.width)
    if w <= 0:
        raise ValueError(f"empty PDF width for {out}")
    scale = TEXT_WIDTH_PT / w
    if abs(scale - 1.0) > 1e-6:
        page.scale_by(scale)
        writer = PdfWriter()
        writer.add_page(page)
        with out.open("wb") as fh:
            writer.write(fh)
    return scale


def fig_legend_title(
    fig,
    leg,
    *,
    title: str = "图例",
    gap: float = 0.008,
    fontsize: float | None = None,
    fontweight: str = "bold",
    center_x: float = 0.5,
    anchor_xy: tuple[float, float],
) -> None:
    """在 fig.legend 左侧加标题，并将「标题 + 图例」整体水平居中。

    ``anchor_xy`` 为创建时传给 ``fig.legend(..., bbox_to_anchor=...)`` 的坐标；
    本函数会按整体宽度将其右移/左移，使标题不把视觉中心拉偏。
    """
    if fontsize is None:
        fontsize = FONT["legend"]
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    inv = fig.transFigure.inverted()
    lbb = leg.get_window_extent(renderer).transformed(inv)
    mid_y = (lbb.y0 + lbb.y1) / 2
    txt = fig.text(
        lbb.x0 - gap, mid_y, title,
        transform=fig.transFigure, ha="right", va="center",
        fontsize=fontsize, fontweight=fontweight,
    )
    fig.canvas.draw()
    tbb = txt.get_window_extent(renderer).transformed(inv)
    lbb = leg.get_window_extent(renderer).transformed(inv)
    dx = center_x - 0.5 * (tbb.x0 + lbb.x1)
    ax, ay = anchor_xy
    # 必须显式用 figure 坐标；默认会落到 axes.transAxes，图例被裁切只剩标题
    leg.set_bbox_to_anchor((ax + dx, ay), transform=fig.transFigure)
    txt.set_position((lbb.x0 - gap + dx, mid_y))


def fig_shared_legend(
    fig,
    handles=None,
    labels=None,
    *,
    loc: str,
    bbox_to_anchor: tuple[float, float],
    ncol: int = 1,
    title: str = "图例",
    **kwargs: Any,
):
    """Figure 级共享图例：统一浅灰细边框 + 左侧「图例」+ 整体居中。

    顶/底位置由 ``loc`` / ``bbox_to_anchor`` 按版面决定；色块与文案仍由调用方提供。
    ``handlelength`` 等可按系列类型覆盖。
    """
    kw: dict[str, Any] = {
        "frameon": True,
        "framealpha": 0.95,
        "edgecolor": C_LEGEND_FRAME,
        "fancybox": False,
        "borderpad": 0.4,
        "handletextpad": 0.5,
        "columnspacing": 1.0,
        "fontsize": FONT["legend"],
        "loc": loc,
        "bbox_to_anchor": bbox_to_anchor,
        "ncol": ncol,
    }
    kw.update(kwargs)
    if handles is not None and labels is not None:
        leg = fig.legend(handles, labels, **kw)
    elif handles is not None:
        leg = fig.legend(handles=handles, **kw)
    else:
        leg = fig.legend(**kw)
    fig_legend_title(fig, leg, title=title, anchor_xy=bbox_to_anchor)
    return leg
