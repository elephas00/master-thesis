"""学位论文统一绘图样式（第三、四章定量图共用）

柱状图与折线图使用**独立色序**：
  - 柱图 COLORS_BAR / BAR_STYLE：白底黑边为第 1 优先（印刷友好）
  - 折线 COLORS_LINE / LINE_STYLE：黑为第 1 优先（主系列），不含白色

需要 N 个系列时分别按 BAR_PRIORITY / LINE_PRIORITY 取前 N。

多子图约定:
  - 每个子图各自维护图例
  - 跨子图语义相同的系列共用同一 swatch
  - 分栏展示可用同一主系列，不必为区分面板另占色位
"""

from __future__ import annotations

from typing import Any

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
# Okabe–Ito 改编：第 2 位原蓝改为灰，印刷对照更稳
# ---------------------------------------------------------------------------
COLORS_BAR: list[str] = [
    "#FFFFFF",  # 1 白底 — 优先（黑边勾勒，印刷清晰）
    "#5D6D7E",  # 2 灰（替 Okabe 蓝，作第一对照）
    "#E69F00",  # 3 琥珀
    "#009E73",  # 4 绿蓝
    "#CC79A7",  # 5 紫红
    "#56B4E9",  # 6 天蓝
]

HATCH_BAR: list[str] = [
    "",         # 1 白
    "",         # 2 灰 — 无底纹
    "///",      # 3 琥珀
    "\\\\\\",   # 4 绿蓝
    "xx",       # 5 紫红
    "..",       # 6 天蓝
]

# ---------------------------------------------------------------------------
# 折线色序（l1..l6；黑 = 第 1 优先，与柱图独立）
# ---------------------------------------------------------------------------
COLORS_LINE: list[str] = [
    C_INK,      # 1 黑 — 主系列
    "#1E3A5F",  # 2 深蓝灰
    "#64748B",  # 3 石板灰
    "#0072B2",  # 4 标准蓝
    "#8B7355",  # 5 低饱和褐
    "#5B8FA8",  # 6 青灰（最浅）
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

_METHOD_ORDER = ["本文方法", "RF", "AE", "TCAN", "MVT-RF", "Mut-RF"]
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
