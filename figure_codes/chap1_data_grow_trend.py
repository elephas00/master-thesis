"""全球每年新产生的数据总量预测趋势图（黑白灰）

生成 figure/chap1-data-growth-trend.pdf。
数据来源：用户提供的图表 OCR 结果 (2015-2030)。

用法（项目根目录）:
    python3 figure_codes/chap1_data_grow_trend.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FIGURE_DIR = PROJECT_ROOT / "figure"
OUT_PDF = FIGURE_DIR / "chap1-data-growth-trend.pdf"

plt.rcParams.update({
    "font.sans-serif": ["Arial Unicode MS", "PingFang SC", "SimHei", "DejaVu Sans"],
    "axes.unicode_minus": False,
    "figure.dpi": 120,
    "font.size": 10,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})

# 黑白灰
C_LINE = "#222222"
C_FILL = "#C8C8C8"
C_MARKER = "#111111"
C_TEXT = "#222222"
C_SPINE = "#000000"

years = [str(y) for y in range(2015, 2031)]
values = [11, 15, 20, 26, 33, 44, 58, 77, 102, 133, 175, 236, 325, 460, 670, 1003]


def plot_growth_trend(*, save_path_pdf: Path | None = None) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(12.8, 5))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    # 下方阴影：浅灰；折线/标记：深灰黑
    ax.fill_between(years, values, color=C_FILL, alpha=0.85, zorder=1)
    ax.plot(
        years, values,
        color=C_LINE, linewidth=1.6, marker="o", markersize=3.5,
        markerfacecolor=C_MARKER, markeredgecolor=C_MARKER, zorder=2,
    )

    ax.set_yticks(np.arange(0, 1201, 200))
    ax.set_xticks(range(len(years)))
    ax.set_xticklabels(years, rotation=0, fontsize=8)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(C_SPINE)
    ax.spines["bottom"].set_color(C_SPINE)
    ax.tick_params(colors="#000000")

    for i, val in enumerate(values):
        ax.text(
            i, val + 30, str(val),
            ha="center", va="bottom", fontsize=8, color=C_TEXT,
        )

    fig.tight_layout()
    if save_path_pdf is not None:
        save_path_pdf.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(save_path_pdf, bbox_inches="tight", facecolor="white")
    return fig


def main() -> None:
    fig = plot_growth_trend(save_path_pdf=OUT_PDF)
    plt.close(fig)
    print(f"saved: {OUT_PDF}")


if __name__ == "__main__":
    main()
