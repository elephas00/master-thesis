"""第四章：块寿命标签构造流程

生成 figure/chap4-block-labeling-flow.pdf。
配色对齐第三章（蓝主色 / 橙决策 / 绿输出）。

用法（项目根目录）:
    python3 figure_codes/chap4_block_labeling_flow.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FIGURE_DIR = PROJECT_ROOT / "figure"
OUT_PDF = FIGURE_DIR / "chap4-block-labeling-flow.pdf"

plt.rcParams.update({
    "font.sans-serif": ["Arial Unicode MS", "PingFang SC", "SimHei", "DejaVu Sans"],
    "axes.unicode_minus": False,
    "figure.dpi": 120,
    "savefig.dpi": 300,
    "font.size": 11,
})

C_BLUE_F, C_BLUE_E = "#E3F2FD", "#1565C0"
C_GRAY_F, C_GRAY_E = "#F5F5F5", "#757575"
C_ORANGE_F, C_ORANGE_E = "#FFF3E0", "#E65100"
C_GREEN_F, C_GREEN_E = "#E8F5E9", "#2E7D32"
C_RED_F, C_RED_E = "#FFEBEE", "#C62828"
C_ARROW = "#424242"


def _box(ax, xy, w, h, text, fc, ec, fontsize=11, weight="bold"):
    patch = FancyBboxPatch(
        xy, w, h, boxstyle="round,pad=0.02,rounding_size=0.5",
        facecolor=fc, edgecolor=ec, linewidth=1.8, zorder=2,
    )
    ax.add_patch(patch)
    ax.text(xy[0] + w / 2, xy[1] + h / 2, text, ha="center", va="center",
            fontsize=fontsize, fontweight=weight, color="#212121", zorder=3)
    return patch


def _diamond(ax, cx, cy, w, h, text, fc, ec):
    verts = np.array([[cx, cy + h / 2], [cx + w / 2, cy], [cx, cy - h / 2], [cx - w / 2, cy]])
    poly = Polygon(verts, closed=True, facecolor=fc, edgecolor=ec, linewidth=1.8, zorder=2)
    ax.add_patch(poly)
    ax.text(cx, cy, text, ha="center", va="center", fontsize=10,
            fontweight="bold", color="#212121", zorder=3)


def _arrow(ax, x1, y1, x2, y2):
    ax.annotate(
        "", xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(arrowstyle="-|>", color=C_ARROW, lw=1.6,
                        mutation_scale=12),
        zorder=1,
    )


def plot(*, save_pdf: Path = OUT_PDF) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(5.2, 7.2))
    ax.set_xlim(0, 50)
    ax.set_ylim(0, 100)
    ax.axis("off")

    # 自上而下
    _box(ax, (12, 88), 26, 8, "物理 / 逻辑块\nBLOCK", C_GRAY_F, C_GRAY_E, fontsize=10)
    _arrow(ax, 25, 88, 25, 82)

    _box(ax, (12, 72), 26, 8, "代表性 FBC\n$P_{99}$（BestRead）", C_BLUE_F, C_BLUE_E, fontsize=10)
    _arrow(ax, 25, 72, 25, 66)

    _box(ax, (10, 56), 30, 8, "对照 FBC 门限 $=151$\n推导 LIFESPAN", C_BLUE_F, C_BLUE_E, fontsize=10)
    _arrow(ax, 25, 56, 25, 49)

    _diamond(ax, 25, 40, 22, 14, "LIFESPAN\n$=10000$？", C_ORANGE_F, C_ORANGE_E)

    # yes / no
    _arrow(ax, 14, 40, 8, 28)
    _arrow(ax, 36, 40, 42, 28)
    ax.text(9.5, 34, "是", fontsize=10, color=C_GREEN_E, fontweight="bold")
    ax.text(38.5, 34, "否", fontsize=10, color=C_RED_E, fontweight="bold")

    _box(ax, (1, 16), 14, 10, "强块\nLabel $=0$", C_GREEN_F, C_GREEN_E, fontsize=10)
    _box(ax, (35, 16), 14, 10, "弱块\nLabel $=1$", C_RED_F, C_RED_E, fontsize=10)

    ax.text(
        25, 6,
        "目标：识别能否安全使用至 10000 次 PE",
        ha="center", va="center", fontsize=9, color="#546E7A",
    )

    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(save_pdf, bbox_inches="tight", facecolor="white")
    return fig


def main() -> None:
    fig = plot()
    plt.close(fig)
    print(f"saved: {OUT_PDF}")


if __name__ == "__main__":
    main()
