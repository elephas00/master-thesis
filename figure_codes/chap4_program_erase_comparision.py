"""第四章：固定阈值 vs 理想策略 PE 对比（水平柱）

生成 figure/generated/chap4_pe_comparison.pdf（输出目录 figure/generated/）。

用法（项目根目录）:
    PYTHONPATH=figure_codes python3 figure_codes/chap4_program_erase_comparision.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt

from figure_paths import GENERATED_DIR as FIGURE_DIR, ensure_output_dirs
from thesis_style import (
    BAR_LW,
    C_EDGE,
    FONT,
    TEXT_WIDTH_IN,
    apply_rc,
    bar_key,
    bar_style,
    fig_shared_legend,
    legend_swatch,
    savefig_text_width,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUT_PDF = FIGURE_DIR / "chap4-program-erase-comparison.pdf"

apply_rc()

# 左段 / 右段：柱图优先序前两档
ST_LEFT = bar_style(0)
ST_RIGHT = bar_style(1)
KEY_LEFT = bar_key(0)
KEY_RIGHT = bar_key(1)

PE_VALUES = [9000, 8500, 9500, 10000, 10000, 10000]
THRESHOLD = 8500


def plot(*, save_path: Path = OUT_PDF) -> plt.Figure:
    pe_values = PE_VALUES
    threshold = THRESHOLD
    left_values = [min(pe, threshold) for pe in pe_values]
    right_values = [max(0, pe - threshold) for pe in pe_values]
    block_labels = [f"块{i + 1}" for i in range(len(pe_values))]

    # 图高适中；图例贴紧坐标轴顶边
    fig, ax = plt.subplots(figsize=(TEXT_WIDTH_IN, 2.35))
    y = range(len(pe_values))
    bar_h = 0.50

    ax.barh(
        y, left_values, height=bar_h,
        color=ST_LEFT["color"], hatch=ST_LEFT["hatch"],
        edgecolor=C_EDGE, linewidth=BAR_LW,
    )
    ax.barh(
        y, right_values, left=left_values, height=bar_h,
        color=ST_RIGHT["color"], hatch=ST_RIGHT["hatch"],
        edgecolor=C_EDGE, linewidth=BAR_LW,
    )
    ax.axvline(x=threshold, color=C_EDGE, linestyle="--", linewidth=1.2)

    ax.set_yticks(list(y))
    ax.set_yticklabels(block_labels, fontsize=FONT["tick"])
    ax.tick_params(axis="x", labelsize=FONT["tick"])
    ax.set_xlim(0, max(pe_values) * 1.12)
    # 收紧上下留白，避免图例与顶行柱之间出现大块空距
    ax.set_ylim(-0.35, len(pe_values) - 0.65)

    for i, pe in enumerate(pe_values):
        ax.text(pe + 80, i, f"{pe}", ha="left", va="center", fontsize=FONT["annot"])

    # 图例置顶；无子图标题，轴顶抬高使间距约 4–5 pt
    fig.subplots_adjust(left=0.10, right=0.98, top=0.935, bottom=0.13)
    fig_shared_legend(
        fig,
        handles=[
            legend_swatch(KEY_LEFT, "固定阈值策略每个块的 PE 次数"),
            legend_swatch(KEY_RIGHT, "理想策略可额外使用的 PE 次数"),
        ],
        loc="lower center",
        bbox_to_anchor=(0.54, 0.955),
        ncol=2,
        fontsize=FONT["note"],
        handlelength=1.6,
        handleheight=1.1,
        borderpad=0.28,
        borderaxespad=0.0,
    )
    savefig_text_width(fig, save_path, pad_inches=0.04)
    return fig


def main() -> None:
    ensure_output_dirs()
    fig = plot()
    plt.close(fig)
    print(f"saved: {OUT_PDF}")


if __name__ == "__main__":
    main()
