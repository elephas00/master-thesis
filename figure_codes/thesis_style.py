"""学位论文统一绘图样式（第三、四章定量图共用）

柱状图字典 BAR_STYLE 与折线图字典 LINE_STYLE 分开。
柱图优先序：白底黑边为第 1 优先（印刷友好），其后为对照色。
需要 N 个系列时按 BAR_PRIORITY 取前 N；折线跳过白色（见 LINE_STYLE）。

多子图约定:
  - 每个子图各自维护图例
  - 跨子图语义相同的系列共用同一 swatch
  - 分栏展示可用同一主系列，不必为区分面板另占色位
"""

from __future__ import annotations

from typing import Any

# ---------------------------------------------------------------------------
# 色序（柱图 b1..b6 同下标；白为第 1 优先）
# ---------------------------------------------------------------------------
COLORS_PRIORITY: list[str] = [
    "#FFFFFF",  # 1 白底 — 优先（黑边勾勒，印刷清晰）
    "#1E3A5F",  # 2 深蓝灰 — 第一对照
    "#94A3B8",  # 3 灰蓝
    "#64748B",  # 4 石板灰
    "#0F766E",  # 5 青绿
    "#B45309",  # 6 琥珀
]

# 柱图底纹（与色序同下标；白、深蓝灰均无底纹）
HATCH_PRIORITY: list[str] = [
    "",         # 1 白
    "",         # 2 深蓝灰 — 无底纹
    "///",      # 3 灰蓝
    "\\\\\\",   # 4 石板灰
    "xx",       # 5 青绿
    "..",       # 6 琥珀
]

# 折线线型 / 标记
LINESTYLE_PRIORITY: list[str] = [
    "-",
    "--",
    "-.",
    ":",
    (0, (3, 1, 1, 1)),
    (0, (5, 2)),
]
MARKER_PRIORITY: list[str] = ["o", "s", "^", "D", "v", "P"]

C_PRIMARY = COLORS_PRIORITY[0]
C_SECONDARY = COLORS_PRIORITY[1]
C_TERTIARY = COLORS_PRIORITY[2]
C_QUATERNARY = COLORS_PRIORITY[3]

C_INK = "#111111"
C_ZERO = "#444444"
C_GRID = "#D0D0D0"
C_EDGE = C_INK
C_SEP = "#FFFFFF"
C_BG = "#FFFFFF"
BAR_LW = 0.85
C_LEGEND_FRAME = "#CBD5E1"
C_SPINE_MUTED = "#BDBDBD"


def _is_white(c: str) -> bool:
    return c.strip().upper() in {"#FFFFFF", "#FFF", "WHITE"}


# 折线用实色（跳过白）
COLORS_FILL: list[str] = [c for c in COLORS_PRIORITY if not _is_white(c)]

# ---------------------------------------------------------------------------
# 柱状图字典 b1..b6（白 = b1 = 第 1 优先）
# ---------------------------------------------------------------------------
BAR_STYLE: dict[str, dict[str, str]] = {
    f"b{i + 1}": {
        "color": COLORS_PRIORITY[i],
        "hatch": HATCH_PRIORITY[i],
        "edge": C_EDGE,
    }
    for i in range(6)
}

LEGEND_STYLE = BAR_STYLE

# 柱图优先序 = b1 → b6（与色序一致）
BAR_PRIORITY: list[str] = [f"b{i}" for i in range(1, 7)]

# ---------------------------------------------------------------------------
# 折线图字典（色 + 线型 + 标记；跳过白色，避免白底上看不见）
# ---------------------------------------------------------------------------
_n_line = min(6, len(COLORS_FILL), len(LINESTYLE_PRIORITY), len(MARKER_PRIORITY))
LINE_STYLE: dict[str, dict[str, Any]] = {
    f"l{i + 1}": {
        "color": COLORS_FILL[i],
        "ls": LINESTYLE_PRIORITY[i],
        "marker": MARKER_PRIORITY[i],
    }
    for i in range(_n_line)
}


def bar_priority_keys() -> list[str]:
    """柱图优先序键列表。"""
    return list(BAR_PRIORITY)


def bar_key(i: int) -> str:
    keys = bar_priority_keys()
    return keys[i % len(keys)]


def bar_style(i: int) -> dict[str, str]:
    """柱图第 i 个系列（0-based），按 BAR_PRIORITY 取。"""
    return dict(BAR_STYLE[bar_key(i)])


# ---------------------------------------------------------------------------
# 语义别名（柱图一律跟 BAR_PRIORITY 全序，不跳过白底）
# ---------------------------------------------------------------------------
_pair0, _pair1 = bar_style(0), bar_style(1)
PAIR_MB = {"MB1": _pair0["color"], "MB2": _pair1["color"]}
PAIR_MB_HATCH = {"MB1": _pair0["hatch"], "MB2": _pair1["hatch"]}

# 读模式：折线字典前两档（勿用 COLORS_PRIORITY 硬下标，白色会进 DefaultRead）
_ls0, _ls1 = LINE_STYLE["l1"], LINE_STYLE["l2"]
PAIR_READ = {"DefaultRead": _ls0["color"], "BestRead": _ls1["color"]}
PAIR_READ_HATCH = {"DefaultRead": HATCH_PRIORITY[0], "BestRead": HATCH_PRIORITY[1]}
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
    """折线第 i 个系列（0-based）→ l1..lN（跳过白色）。"""
    n = len(LINE_STYLE)
    st = LINE_STYLE[f"l{(i % n) + 1}"]
    return dict(st)


def series_style(i: int) -> dict[str, Any]:
    """兼容别名：等同 line_style（折线/散点）。"""
    st = line_style(i)
    st["hatch"] = HATCH_PRIORITY[i % len(HATCH_PRIORITY)]
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
