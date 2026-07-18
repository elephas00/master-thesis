"""第四章：BlockFilter 逻辑组划分示意（黑白印刷版）。

生成 figure/generated/chap4-blockfilter-grouping.pdf。

用法（项目根目录）:
    python3 figure_codes/chap4_blockfilter_grouping.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from figure_paths import GENERATED_DIR as FIGURE_DIR, ensure_output_dirs
from flowchart_style import (
    INK,
    LINE_WIDTH,
    PAPER,
    apply_flowchart_rc,
    process,
)
from thesis_style import FONT

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUT_PDF = FIGURE_DIR / "chap4-blockfilter-grouping.pdf"

def _group_cells(remainder: int) -> list[str]:
    """返回同一余数组中的四个示例物理块。"""
    early = [remainder, remainder + 4]
    late = [32 + remainder, 36 + remainder]
    return [f"TU30_CH1_CE1_L1_B{i}" for i in early + late]


def plot(*, save_pdf: Path = OUT_PDF) -> plt.Figure:
    apply_flowchart_rc()
    fig, ax = plt.subplots(figsize=(10.6, 5.0))
    ax.set_xlim(0, 19.4)
    ax.set_ylim(0, 9.4)
    ax.axis("off")

    layout = [
        (0.3, 4.9, 0),
        (9.85, 4.9, 1),
        (0.3, 0.3, 2),
        (9.85, 0.3, 3),
    ]
    group_w, group_h = 9.2, 4.1

    for x0, y0, r in layout:
        ax.add_patch(Rectangle(
            (x0, y0),
            group_w,
            group_h,
            facecolor=PAPER,
            edgecolor=INK,
            linewidth=LINE_WIDTH,
            linestyle=(0, (5, 3)),
            zorder=0,
        ))
        ax.text(
            x0 + group_w / 2,
            y0 + group_h - 0.45,
            f"逻辑组 B{r}（BlockFilter $\\mathrm{{mod}}\\ 4={r}$）",
            ha="center",
            va="center",
            fontsize=FONT["title"],
            color=INK,
        )

        cells = _group_cells(r)
        positions = [
            (x0 + 2.35, y0 + 2.55),
            (x0 + 6.85, y0 + 2.55),
            (x0 + 2.35, y0 + 0.95),
            (x0 + 6.85, y0 + 0.95),
        ]
        for center, label in zip(positions, cells):
            process(ax, center, 4.2, 1.15, label, fontsize=FONT["label"])

    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(save_pdf, bbox_inches="tight", pad_inches=0.06, facecolor="white")
    return fig


def main() -> None:
    ensure_output_dirs()
    fig = plot()
    plt.close(fig)
    print(f"saved: {OUT_PDF}")


if __name__ == "__main__":
    main()
