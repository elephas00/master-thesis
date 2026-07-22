"""全球每年新产生的数据总量预测趋势图

生成 figure/generated/chap1-data-growth-trend.pdf。
数据来源：用户提供的图表 OCR 结果 (2015-2030)。
样式：thesis_style（与第三、四章定量图一致）。

用法（项目根目录）:
    python3 figure_codes/chap1_data_grow_trend.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from figure_paths import GENERATED_DIR as FIGURE_DIR, ensure_output_dirs
from thesis_style import (
    C_EDGE,
    C_GRID,
    C_INK,
    FONT,
    TEXT_WIDTH_IN,
    apply_rc,
    line_style,
    savefig_text_width,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUT_PDF = FIGURE_DIR / "chap1-data-growth-trend.pdf"

apply_rc()

YEARS = [str(y) for y in range(2015, 2031)]
VALUES = [11, 15, 20, 26, 33, 44, 58, 77, 102, 133, 175, 236, 325, 460, 670, 1003]


def plot(*, save_path: Path = OUT_PDF) -> plt.Figure:
    st = line_style(0)
    # 高约加一行正文（≈0.28 in），便于图后正文换到次页
    fig, ax = plt.subplots(figsize=(TEXT_WIDTH_IN, 2.48))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    ax.fill_between(YEARS, VALUES, color=C_GRID, alpha=0.85, zorder=1)
    ax.plot(
        YEARS,
        VALUES,
        color=st["color"],
        linewidth=1.3,
        linestyle=st["ls"],
        marker=st["marker"],
        markersize=2.8,
        markerfacecolor=st["color"],
        markeredgecolor=st["color"],
        zorder=2,
    )

    ax.set_yticks(np.arange(0, 1201, 200))
    ax.set_xticks(range(len(YEARS)))
    ax.set_xticklabels(YEARS, rotation=0, fontsize=FONT["annot"] - 1)
    ax.tick_params(axis="y", labelsize=FONT["annot"] - 1)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(C_EDGE)
    ax.spines["bottom"].set_color(C_EDGE)
    ax.tick_params(colors=C_INK)

    # 用点偏移（而非数据坐标 +14），避免后期数值贴线
    for i, val in enumerate(VALUES):
        ax.annotate(
            str(val),
            (i, val),
            textcoords="offset points",
            xytext=(0, 5),
            ha="center",
            va="bottom",
            fontsize=FONT["annot"] - 1,
            color=C_INK,
            clip_on=False,
        )

    ax.set_ylim(0, max(VALUES) * 1.12)
    fig.tight_layout()
    savefig_text_width(fig, save_path)
    return fig


def main() -> None:
    ensure_output_dirs()
    fig = plot(save_path=OUT_PDF)
    plt.close(fig)
    print(f"saved: {OUT_PDF}")


if __name__ == "__main__":
    main()
