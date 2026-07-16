"""第二章：随机森林示意图

生成：
    figure/chap2-random-forest.pdf
    figure/chap2-random-forest.png

正文引用：figure/chap2-random-forest.pdf

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
from matplotlib.lines import Line2D

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FIGURE_DIR = PROJECT_ROOT / "figure"
OUT_PDF = FIGURE_DIR / "chap2-random-forest.pdf"
OUT_PNG = FIGURE_DIR / "chap2-random-forest.png"

plt.rcParams.update({
    "font.sans-serif": ["Arial Unicode MS", "PingFang SC", "PingFang HK",
                        "Heiti TC", "STHeiti", "SimHei", "DejaVu Sans"],
    "axes.unicode_minus": False,
    "figure.dpi": 120,
    "savefig.dpi": 300,
    "font.size": 11,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})

# 配色：黑白教材风格，容器白底/无底色
C_FILL = "#FFFFFF"
C_EDGE = "#000000"
C_ARROW = "#000000"
C_DASH = "#666666"
C_TEXT = "#000000"
C_TREE = "#000000"

CYL_W = 7.0
CYL_H = 6.2
ELL_H = 1.6


def _cylinder(ax, cx, cy, w=CYL_W, h=CYL_H, label=r"$D$", fs=16):
    """3D 风格圆柱：矩形体 + 上下椭圆（白底黑框）。"""
    x0, y0 = cx - w / 2, cy - h / 2
    ax.add_patch(Rectangle(
        (x0, y0), w, h,
        facecolor=C_FILL, edgecolor="none", zorder=2,
    ))
    ax.plot([x0, x0], [y0, y0 + h], color=C_EDGE, lw=1.6, zorder=3)
    ax.plot([x0 + w, x0 + w], [y0, y0 + h], color=C_EDGE, lw=1.6, zorder=3)
    ax.add_patch(Ellipse(
        (cx, y0), w, ELL_H,
        facecolor=C_FILL, edgecolor=C_EDGE, lw=1.6, zorder=2,
    ))
    ax.add_patch(Ellipse(
        (cx, y0 + h), w, ELL_H,
        facecolor=C_FILL, edgecolor=C_EDGE, lw=1.6, zorder=4,
    ))
    ax.text(cx, cy + 0.2, label, ha="center", va="center",
            fontsize=fs, color=C_TEXT, style="italic", zorder=5,
            fontfamily="serif")


def _arrow(ax, x0, y0, x1, y1, *, lw=2.2, mutation_scale=14):
    ax.add_patch(FancyArrowPatch(
        (x0, y0), (x1, y1),
        arrowstyle="-|>", mutation_scale=mutation_scale,
        lw=lw, color=C_ARROW, zorder=3,
        connectionstyle="arc3,rad=0",
    ))


def _vtext(ax, x, y, text, *, fs=10, color=C_TEXT, weight="normal"):
    """竖排中文（逐字自上而下）。"""
    chars = list(text)
    n = len(chars)
    spacing = 1.85 if n <= 4 else 1.55
    total = (n - 1) * spacing
    y_top = y + total / 2
    for i, ch in enumerate(chars):
        ax.text(x, y_top - i * spacing, ch, ha="center", va="center",
                fontsize=fs, color=color, fontweight=weight, zorder=5)


def _decision_tree_icon(ax, cx, cy, scale=1.0):
    """框内简易决策树：一根 + 两叶。"""
    r = 0.48 * scale
    root = (cx, cy + 1.25 * scale)
    left = (cx - 1.3 * scale, cy - 0.7 * scale)
    right = (cx + 1.3 * scale, cy - 0.7 * scale)
    for (a, b) in [(root, left), (root, right)]:
        ax.plot([a[0], b[0]], [a[1], b[1]],
                color=C_TREE, lw=1.5, zorder=4)
    for p in (root, left, right):
        ax.add_patch(Circle(
            p, r, facecolor=C_FILL, edgecolor=C_TREE, lw=1.5, zorder=5,
        ))


def _tree_box(ax, cx, cy, label=None, *, show_tree=True):
    w, h = 9.5, 7.2
    box = FancyBboxPatch(
        (cx - w / 2, cy - h / 2), w, h,
        boxstyle="round,pad=0.15,rounding_size=0.7",
        facecolor=C_FILL, edgecolor=C_EDGE, lw=1.6, zorder=2,
    )
    ax.add_patch(box)
    if show_tree:
        _decision_tree_icon(ax, cx, cy + (0.5 if label else 0.15), scale=0.9)
    if label:
        ax.text(cx, cy - 2.4, label, ha="center", va="center",
                fontsize=12, color=C_TEXT, style="italic", zorder=5,
                fontfamily="serif")


def plot(*, save_pdf: Path = OUT_PDF) -> plt.Figure:
    # 更扁：横向加宽感强，竖向压缩
    fig, ax = plt.subplots(figsize=(13.2, 4.6))
    ax.set_xlim(0, 132)
    ax.set_ylim(0, 46)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    # ---- 纵列 y 坐标（三路并行，间距收紧）----
    ys = [36.0, 23.0, 10.0]  # D1/T1, D2/T2, Dn/Tn
    mid_y = ys[1]

    # ---- 1. 原始数据 D ----
    d_cx, d_cy = 8.5, mid_y
    _cylinder(ax, d_cx, d_cy, label=r"$D$", fs=17)

    # ---- 2. 自助采样：圆角矩形（与右侧集成模块呼应）----
    boot_x0, boot_w = 18.0, 8.0
    boot_y0, boot_h = 5.5, 34.0
    boot_box = FancyBboxPatch(
        (boot_x0, boot_y0), boot_w, boot_h,
        boxstyle="round,pad=0.12,rounding_size=0.7",
        facecolor=C_FILL, edgecolor=C_EDGE, lw=1.6, zorder=2,
    )
    ax.add_patch(boot_box)
    _vtext(ax, boot_x0 + boot_w / 2, mid_y, "自助采样", fs=12, weight="bold")

    # D → 自助采样
    _arrow(ax, d_cx + CYL_W / 2 + 0.4, d_cy, boot_x0 - 0.3, d_cy,
           lw=2.4, mutation_scale=16)

    # ---- 3. Bootstrap 子数据集 ----
    boot_cx = 40.0
    ax.text(boot_cx, 43.0, "Bootstrap采样", ha="center", va="center",
            fontsize=12, color=C_TEXT, fontweight="bold", zorder=5)

    for y, lab in zip(ys, [r"$D_1$", r"$D_2$", r"$D_n$"]):
        _cylinder(ax, boot_cx, y, label=lab, fs=13)
        _arrow(ax, boot_x0 + boot_w + 0.15, y, boot_cx - CYL_W / 2 - 0.5, y,
               lw=1.8, mutation_scale=12)

    ax.text(boot_cx, (ys[1] + ys[2]) / 2, "⋮", ha="center", va="center",
            fontsize=15, color=C_EDGE, zorder=5)

    # ---- 分隔线 1 ----
    sep1 = 48.5
    ax.add_line(Line2D([sep1, sep1], [4.0, 43.5],
                       color=C_DASH, lw=1.4, ls="--", zorder=1))

    # ---- 4. 决策树模型 ----
    tree_cx = 62.0
    ax.text(tree_cx, 43.0, r"决策树模型", ha="center", va="center",
            fontsize=12, color=C_TEXT, fontweight="bold", zorder=5)

    feat_x = 71.5
    for y, lab in zip(ys, [r"$T_1$", r"$T_2$", r"$T_n$"]):
        _arrow(ax, boot_cx + CYL_W / 2 + 0.4, y, tree_cx - 5.0, y,
               lw=1.8, mutation_scale=12)
        _tree_box(ax, tree_cx, y, label=lab)
        _vtext(ax, feat_x, y, "随机特征选择", fs=9, color=C_TEXT)

    ax.text(tree_cx, (ys[1] + ys[2]) / 2, "⋮", ha="center", va="center",
            fontsize=15, color=C_EDGE, zorder=5)

    # ---- 分隔线 2 ----
    sep2 = 78.0
    ax.add_line(Line2D([sep2, sep2], [4.0, 43.5],
                       color=C_DASH, lw=1.4, ls="--", zorder=1))

    # ---- 5. 集成预测模块 ----
    ens_x0, ens_w = 83.5, 7.5
    ens_y0, ens_h = 5.5, 34.0
    ax.text(ens_x0 + ens_w / 2, 43.0, "集成预测模块", ha="center", va="center",
            fontsize=12, color=C_TEXT, fontweight="bold", zorder=5)
    ens = FancyBboxPatch(
        (ens_x0, ens_y0), ens_w, ens_h,
        boxstyle="round,pad=0.12,rounding_size=0.7",
        facecolor=C_FILL, edgecolor=C_EDGE, lw=1.6, zorder=2,
    )
    ax.add_patch(ens)
    _vtext(ax, ens_x0 + ens_w / 2, ens_y0 + ens_h / 2, "投票/平均",
           fs=11, weight="bold")

    for y in ys:
        _arrow(ax, feat_x + 2.0, y, ens_x0 - 0.3, y, lw=1.8, mutation_scale=12)

    # ---- 6. 最终预测结果 ----
    out_cx, out_cy = 111.5, mid_y
    out_w, out_h = 17.0, 8.5
    out = FancyBboxPatch(
        (out_cx - out_w / 2, out_cy - out_h / 2), out_w, out_h,
        boxstyle="round,pad=0.15,rounding_size=0.8",
        facecolor=C_FILL, edgecolor=C_EDGE, lw=1.8, zorder=2,
    )
    ax.add_patch(out)
    ax.text(out_cx, out_cy, "最终预测结果", ha="center", va="center",
            fontsize=13, color=C_TEXT, fontweight="bold", zorder=5)

    _arrow(ax, ens_x0 + ens_w + 0.3, out_cy, out_cx - out_w / 2 - 0.4, out_cy,
           lw=2.4, mutation_scale=16)

    return fig


def main() -> None:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    fig = plot()
    fig.savefig(OUT_PDF, bbox_inches="tight", facecolor="white",
                edgecolor="none", pad_inches=0.12)
    # fig.savefig(OUT_PNG, bbox_inches="tight", facecolor="white",
    #             edgecolor="none", pad_inches=0.12)
    plt.close(fig)
    print(f"saved: {OUT_PDF}")


if __name__ == "__main__":
    main()
