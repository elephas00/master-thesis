"""第二章：随机森林示意图

生成：
    figure/generated/chap2-random-forest.pdf

正文引用：figure/generated/chap2-random-forest.pdf

用法（项目根目录）:
    python3 figure_codes/chap2_random_forest.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import (
    Circle,
    Ellipse,
    FancyArrowPatch,
    FancyBboxPatch,
    Rectangle,
)

from figure_paths import GENERATED_DIR as FIGURE_DIR, ensure_output_dirs
from thesis_style import FONT, TEXT_WIDTH_IN, savefig_text_width

OUT_PDF = FIGURE_DIR / "chap2-random-forest.pdf"

FS = FONT["note"] - 1  # 7 pt，与其他流程图框内字一致

plt.rcParams.update({
    "font.sans-serif": ["Arial Unicode MS", "PingFang SC", "PingFang HK",
                        "Heiti TC", "STHeiti", "SimHei", "DejaVu Sans"],
    "axes.unicode_minus": False,
    "figure.dpi": 120,
    "savefig.dpi": 300,
    "font.size": FS,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})

C_FILL = "#FFFFFF"
C_EDGE = "#000000"
C_ARROW = "#000000"
C_TEXT = "#000000"
C_DOT = "#666666"

CYL_W, CYL_H, ELL_H = 6.4, 5.6, 1.4
TREE_W, TREE_H = 11.6, 8.8
LW = 1.35


def _cylinder(ax, cx, cy, label, *, fs=FS):
    x0, y0 = cx - CYL_W / 2, cy - CYL_H / 2
    ax.add_patch(Rectangle(
        (x0, y0), CYL_W, CYL_H, facecolor=C_FILL, edgecolor="none", zorder=2,
    ))
    ax.plot([x0, x0], [y0, y0 + CYL_H], color=C_EDGE, lw=LW, zorder=3)
    ax.plot([x0 + CYL_W, x0 + CYL_W], [y0, y0 + CYL_H], color=C_EDGE, lw=LW, zorder=3)
    ax.add_patch(Ellipse(
        (cx, y0), CYL_W, ELL_H, facecolor=C_FILL, edgecolor=C_EDGE, lw=LW, zorder=2,
    ))
    ax.add_patch(Ellipse(
        (cx, y0 + CYL_H), CYL_W, ELL_H,
        facecolor=C_FILL, edgecolor=C_EDGE, lw=LW, zorder=4,
    ))
    ax.text(cx, cy + 0.15, label, ha="center", va="center",
            fontsize=fs, color=C_TEXT, style="italic", zorder=5, fontfamily="serif")


def _arrow(ax, x0, y0, x1, y1, *, lw=1.5, ms=11):
    ax.add_patch(FancyArrowPatch(
        (x0, y0), (x1, y1),
        arrowstyle="-|>", mutation_scale=ms, lw=lw, color=C_ARROW, zorder=3,
    ))


def _vtext(ax, x, y, text, *, fs=FS, weight="normal"):
    chars = list(text)
    n = len(chars)
    spacing = (2.0 if n <= 4 else 1.75) * (fs / FS)
    y_top = y + (n - 1) * spacing / 2
    for i, ch in enumerate(chars):
        ax.text(x, y_top - i * spacing, ch, ha="center", va="center",
                fontsize=fs, color=C_TEXT, fontweight=weight, zorder=5)


def _tree_box(ax, cx, cy, label):
    ax.add_patch(FancyBboxPatch(
        (cx - TREE_W / 2, cy - TREE_H / 2), TREE_W, TREE_H,
        boxstyle="round,pad=0.12,rounding_size=0.55",
        facecolor=C_FILL, edgecolor=C_EDGE, lw=LW, zorder=2,
    ))
    s = 1.45
    r = 0.5 * s
    root = (cx, cy + 1.45 * s)
    left = (cx - 1.5 * s, cy - 0.65 * s)
    right = (cx + 1.5 * s, cy - 0.65 * s)
    for a, b in [(root, left), (root, right)]:
        ax.plot([a[0], b[0]], [a[1], b[1]], color=C_EDGE, lw=LW, zorder=4)
    for p in (root, left, right):
        ax.add_patch(Circle(p, r, facecolor=C_FILL, edgecolor=C_EDGE, lw=LW, zorder=5))
    ax.text(cx, cy - 3.15, label, ha="center", va="center",
            fontsize=FS, color=C_TEXT, style="italic", zorder=5,
            fontfamily="serif")


def _panel(ax, x0, y0, w, h, vlabel):
    ax.add_patch(FancyBboxPatch(
        (x0, y0), w, h,
        boxstyle="round,pad=0.1,rounding_size=0.55",
        facecolor=C_FILL, edgecolor=C_EDGE, lw=LW, zorder=2,
    ))
    _vtext(ax, x0 + w / 2, y0 + h / 2, vlabel, weight="bold")


def plot(*, save_pdf: Path = OUT_PDF) -> plt.Figure:
    # 收紧横坐标，使 equal 布局在栏宽下图标更大、更疏
    fig, ax = plt.subplots(figsize=(TEXT_WIDTH_IN, 3.0))
    ax.set_xlim(0, 104)
    ax.set_ylim(0, 48)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    ys = [36.5, 23.0, 9.5]
    mid = ys[1]
    band_y0, band_h = 4.2, 35.0
    fs = FS

    # D
    d_cx = 5.8
    _cylinder(ax, d_cx, mid, r"$D$", fs=fs + 1)

    # 自助采样
    bx0, bw = 13.2, 6.4
    _panel(ax, bx0, band_y0, bw, band_h, "自助采样")
    _arrow(ax, d_cx + CYL_W / 2 + 0.3, mid, bx0 - 0.3, mid, lw=1.7, ms=12)

    # 子集
    d_boot = 29.5
    ax.text(d_boot, 44.5, "采样子集", ha="center", va="center",
            fontsize=fs, fontweight="bold", color=C_TEXT, zorder=5)
    for y, lab in zip(ys, [r"$D_1$", r"$D_2$", r"$D_n$"]):
        _cylinder(ax, d_boot, y, lab, fs=fs)
        _arrow(ax, bx0 + bw + 0.2, y, d_boot - CYL_W / 2 - 0.35, y)
    ax.text(d_boot, (ys[1] + ys[2]) / 2, "⋮", ha="center", va="center",
            fontsize=fs + 2, color=C_DOT, zorder=5)

    # 决策树（框与树图标再放大）
    t_cx = 50.0
    ax.text(t_cx, 44.5, "决策树", ha="center", va="center",
            fontsize=fs, fontweight="bold", color=C_TEXT, zorder=5)
    for y, lab in zip(ys, [r"$T_1$", r"$T_2$", r"$T_n$"]):
        _arrow(ax, d_boot + CYL_W / 2 + 0.3, y, t_cx - TREE_W / 2 - 0.3, y)
        _tree_box(ax, t_cx, y, lab)
    ax.text(t_cx, (ys[1] + ys[2]) / 2, "⋮", ha="center", va="center",
            fontsize=fs + 2, color=C_DOT, zorder=5)

    # 投票/平均
    ex0, ew = 68.0, 6.4
    ax.text(ex0 + ew / 2, 44.5, "集成", ha="center", va="center",
            fontsize=fs, fontweight="bold", color=C_TEXT, zorder=5)
    _panel(ax, ex0, band_y0, ew, band_h, "投票/平均")
    for y in ys:
        _arrow(ax, t_cx + TREE_W / 2 + 0.3, y, ex0 - 0.3, y)

    # 最终结果（箭头终点与框留足间隙，避免箭头尖压字）
    ox, ow, oh = 91.0, 13.5, 6.8
    ax.add_patch(FancyBboxPatch(
        (ox - ow / 2, mid - oh / 2), ow, oh,
        boxstyle="round,pad=0.12,rounding_size=0.6",
        facecolor=C_FILL, edgecolor=C_EDGE, lw=LW, zorder=2,
    ))
    ax.text(ox, mid, "最终预测结果", ha="center", va="center",
            fontsize=fs, fontweight="bold", color=C_TEXT, zorder=5)
    _arrow(ax, ex0 + ew + 0.35, mid, ox - ow / 2 - 1.0, mid, lw=1.7, ms=11)

    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    savefig_text_width(fig, save_pdf, pad_inches=0.04)
    return fig


def main() -> None:
    ensure_output_dirs()
    fig = plot()
    plt.close(fig)
    print(f"saved: {OUT_PDF}")


if __name__ == "__main__":
    main()
