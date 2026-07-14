"""第四章：BlockFilter 逻辑组划分示意

生成 figure/chap4-blockfilter-grouping.png / .pdf。
配色对齐第三章流程图（蓝系主色，灰系辅色）。

用法（项目根目录）:
    python3 figure_codes/chap4_blockfilter_grouping.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FIGURE_DIR = PROJECT_ROOT / "figure"
OUT_PNG = FIGURE_DIR / "chap4-blockfilter-grouping.png"
OUT_PDF = FIGURE_DIR / "chap4-blockfilter-grouping.pdf"

plt.rcParams.update({
    "font.sans-serif": ["Arial Unicode MS", "PingFang SC", "SimHei", "DejaVu Sans"],
    "axes.unicode_minus": False,
    "figure.dpi": 120,
    "savefig.dpi": 300,
    "font.size": 10,
})

# 与 chap3 draw.io 一致
C_GROUP_FILL = "#E3F2FD"
C_GROUP_EDGE = "#1565C0"
C_CELL_FILL = "#FFFFFF"
C_CELL_EDGE = "#90A4AE"
C_TEXT = "#212121"
C_MUTED = "#546E7A"


def _group_cells(remainder: int) -> list[str]:
    # B_{4k+r} → 组 r；示例展示前/后若干编号
    early = [remainder, remainder + 4]
    late = [32 + remainder, 36 + remainder]
    return [f"B{i}" for i in early + late]


def plot(*, save_png: Path = OUT_PNG, save_pdf: Path = OUT_PDF) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(9.2, 5.6))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    # 2×2 逻辑组
    layout = [
        (0, 52, 0),  # r=0 左上
        (52, 52, 1),
        (0, 4, 2),
        (52, 4, 3),
    ]
    box_w, box_h = 42, 42

    for x0, y0, r in layout:
        group = FancyBboxPatch(
            (x0, y0), box_w, box_h,
            boxstyle="round,pad=0.4,rounding_size=1.2",
            facecolor=C_GROUP_FILL, edgecolor=C_GROUP_EDGE, linewidth=1.8,
        )
        ax.add_patch(group)
        ax.text(
            x0 + box_w / 2, y0 + box_h - 4.2,
            f"逻辑组 $r={r}$（BlockFilter $\\mathrm{{mod}}\\,4 = {r}$）",
            ha="center", va="top", fontsize=10, fontweight="bold", color=C_GROUP_EDGE,
        )

        cells = _group_cells(r)
        # 2×2 单元格 + 中间省略
        positions = [
            (x0 + 4, y0 + 22), (x0 + 22, y0 + 22),
            (x0 + 4, y0 + 5), (x0 + 22, y0 + 5),
        ]
        for (cx, cy), label in zip(positions, cells):
            cell = FancyBboxPatch(
                (cx, cy), 14, 10,
                boxstyle="round,pad=0.2,rounding_size=0.6",
                facecolor=C_CELL_FILL, edgecolor=C_CELL_EDGE, linewidth=1.2,
            )
            ax.add_patch(cell)
            ax.text(cx + 7, cy + 5, label, ha="center", va="center",
                    fontsize=11, color=C_TEXT, fontweight="bold")

        ax.text(x0 + box_w / 2, y0 + 17.5, "⋯", ha="center", va="center",
                fontsize=16, color=C_MUTED)

    # 组间省略号
    ax.text(48, 72, "⋯", ha="center", va="center", fontsize=18, color=C_MUTED)
    ax.text(48, 24, "⋯", ha="center", va="center", fontsize=18, color=C_MUTED)
    ax.text(22, 48, "⋯", ha="center", va="center", fontsize=18, color=C_MUTED)
    ax.text(74, 48, "⋯", ha="center", va="center", fontsize=18, color=C_MUTED)

    ax.text(
        50, 97.5,
        "同一余数组内不同物理块共同构成一条逻辑块观测轨迹",
        ha="center", va="top", fontsize=10, color=C_MUTED,
    )

    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    # fig.savefig(save_png, bbox_inches="tight", facecolor="white")
    fig.savefig(save_pdf, bbox_inches="tight", facecolor="white")
    return fig


def main() -> None:
    fig = plot()
    plt.close(fig)
    print(f"saved: {OUT_PNG}")
    print(f"saved: {OUT_PDF}")


if __name__ == "__main__":
    main()
