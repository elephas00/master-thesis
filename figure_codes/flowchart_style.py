"""论文流程图共用的黑白印刷样式。"""

from __future__ import annotations

from collections.abc import Sequence

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.patches import FancyBboxPatch, Polygon

INK = "#111111"
PAPER = "#FFFFFF"
LINE_WIDTH = 1.0
ARROW_SCALE = 9
FONT_SIZE = 10


def apply_flowchart_rc() -> None:
    """设置中文字体与可编辑的 PDF 字体。"""
    plt.rcParams.update({
        "font.sans-serif": [
            "Arial Unicode MS", "PingFang SC", "SimHei", "DejaVu Sans",
        ],
        "axes.unicode_minus": False,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "font.size": FONT_SIZE,
    })


def process(
    ax: Axes,
    center: tuple[float, float],
    width: float,
    height: float,
    text: str,
    *,
    fontsize: float = FONT_SIZE,
    hatch: str = "",
    linewidth: float = LINE_WIDTH,
) -> None:
    """绘制直角矩形处理节点。"""
    x, y = center
    patch = FancyBboxPatch(
        (x - width / 2, y - height / 2),
        width,
        height,
        boxstyle="square,pad=0",
        facecolor=PAPER,
        edgecolor=INK,
        linewidth=linewidth,
        hatch=hatch or None,
        zorder=2,
    )
    ax.add_patch(patch)
    ax.text(
        x,
        y,
        text,
        ha="center",
        va="center",
        fontsize=fontsize,
        color=INK,
        linespacing=1.25,
        zorder=3,
    )


def parallelogram(
    ax: Axes,
    center: tuple[float, float],
    width: float,
    height: float,
    text: str,
    *,
    fontsize: float = FONT_SIZE,
    skew: float = 0.22,
) -> None:
    """绘制平行四边形数据节点。"""
    x, y = center
    s = skew * height
    vertices = [
        (x - width / 2 + s, y - height / 2),
        (x + width / 2 + s, y - height / 2),
        (x + width / 2 - s, y + height / 2),
        (x - width / 2 - s, y + height / 2),
    ]
    ax.add_patch(Polygon(
        vertices,
        closed=True,
        facecolor=PAPER,
        edgecolor=INK,
        linewidth=LINE_WIDTH,
        zorder=2,
    ))
    ax.text(
        x, y, text, ha="center", va="center",
        fontsize=fontsize, color=INK, linespacing=1.25, zorder=3,
    )


def terminator(
    ax: Axes,
    center: tuple[float, float],
    width: float,
    height: float,
    text: str,
    *,
    fontsize: float = FONT_SIZE,
) -> None:
    """绘制圆角起止节点。"""
    x, y = center
    patch = FancyBboxPatch(
        (x - width / 2, y - height / 2),
        width,
        height,
        boxstyle=f"round,pad=0,rounding_size={height / 2}",
        facecolor=PAPER,
        edgecolor=INK,
        linewidth=LINE_WIDTH,
        zorder=2,
    )
    ax.add_patch(patch)
    ax.text(
        x, y, text, ha="center", va="center",
        fontsize=fontsize, color=INK, zorder=3,
    )


def decision(
    ax: Axes,
    center: tuple[float, float],
    width: float,
    height: float,
    text: str,
    *,
    fontsize: float = FONT_SIZE,
) -> None:
    """绘制菱形判断节点。"""
    x, y = center
    vertices = [
        (x, y + height / 2),
        (x + width / 2, y),
        (x, y - height / 2),
        (x - width / 2, y),
    ]
    ax.add_patch(Polygon(
        vertices,
        closed=True,
        facecolor=PAPER,
        edgecolor=INK,
        linewidth=LINE_WIDTH,
        zorder=2,
    ))
    ax.text(
        x,
        y,
        text,
        ha="center",
        va="center",
        fontsize=fontsize,
        color=INK,
        linespacing=1.2,
        zorder=3,
    )


def arrow(
    ax: Axes,
    start: tuple[float, float],
    end: tuple[float, float],
    *,
    linestyle: str = "solid",
) -> None:
    """绘制直线单向箭头。"""
    ax.annotate(
        "",
        xy=end,
        xytext=start,
        arrowprops={
            "arrowstyle": "-|>",
            "color": INK,
            "linewidth": LINE_WIDTH,
            "linestyle": linestyle,
            "mutation_scale": ARROW_SCALE,
            "shrinkA": 0,
            "shrinkB": 0,
        },
        zorder=1,
    )


def dashed_arrow(
    ax: Axes,
    start: tuple[float, float],
    end: tuple[float, float],
) -> None:
    """绘制虚线单向箭头。"""
    arrow(ax, start, end, linestyle=(0, (4, 3)))


def routed_arrow(
    ax: Axes,
    points: Sequence[tuple[float, float]],
    *,
    linestyle: str | tuple = "solid",
) -> None:
    """按折线路径绘制单向箭头。"""
    if len(points) < 2:
        raise ValueError("routed_arrow 至少需要两个点")
    if len(points) > 2:
        xs, ys = zip(*points[:-1])
        ax.plot(
            xs, ys, color=INK, linewidth=LINE_WIDTH,
            linestyle=linestyle, zorder=1,
        )
    arrow(ax, points[-2], points[-1], linestyle=linestyle)


def routed_dashed_arrow(
    ax: Axes,
    points: Sequence[tuple[float, float]],
) -> None:
    """按折线路径绘制虚线单向箭头。"""
    routed_arrow(ax, points, linestyle=(0, (4, 3)))


def edge_label(
    ax: Axes,
    position: tuple[float, float],
    text: str,
    *,
    fontsize: float = 9,
) -> None:
    """绘制带白色衬底的分支标签。"""
    ax.text(
        *position,
        text,
        ha="center",
        va="center",
        fontsize=fontsize,
        color=INK,
        bbox={"facecolor": PAPER, "edgecolor": "none", "pad": 0.8},
        zorder=4,
    )
