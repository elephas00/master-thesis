"""第三章：B 组首跳距故障日 PMF（含静默盘）

生成 figure/generated/chap3-first-jump-pmf.pdf。

数据固化自 codes/eda/notebooks/eda_first_jump_cdf.ipynb
（源：eda/run/first_jump_detail_*.parquet / first_jump_cdf_points.csv；
分母为 eligible 故障盘，$d=0..30$ 逐日 + 「无跳变」，总和 = 1）。

用法（项目根目录）:
    python3 figure_codes/chap3_first_jump_pmf.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import PercentFormatter

from figure_paths import GENERATED_DIR as FIGURE_DIR, ensure_output_dirs
from thesis_style import BAR_LW, C_ZERO, FONT, apply_rc, bar_key, bar_style, legend_swatch

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_PDF = FIGURE_DIR / "chap3-first-jump-pmf.pdf"

apply_rc()

MODELS = ["MB1", "MB2"]
MAX_D = 30
NEAR_END = 14

# 按柱图优先序：第 1 位 b1 白底（无跳变），第 2 位（有跳变）；两栏同色
ST_SILENT = bar_style(0)
ST_JUMP = bar_style(1)
KEY_SILENT = bar_key(0)
KEY_JUMP = bar_key(1)

# eligible 故障盘数、静默盘数、d=0..30 的盘数
META = {
    "MB1": {"n_eligible": 1131, "n_silent": 342},
    "MB2": {"n_eligible": 460, "n_silent": 371},
}
N_AT_D = {
    "MB1": [
        50, 685, 6, 2, 1, 6, 1, 1, 0, 1, 0, 3, 3, 2, 2, 4, 2, 3, 1, 1,
        0, 0, 0, 3, 1, 1, 1, 1, 8, 0, 0,
    ],
    "MB2": [
        27, 34, 3, 1, 2, 0, 0, 1, 0, 1, 0, 0, 2, 0, 0, 1, 1, 1, 1, 1,
        1, 2, 0, 2, 1, 2, 1, 0, 4, 0, 0,
    ],
}


def plot(*, save_path: Path = OUTPUT_PDF) -> plt.Figure:
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 3.6))
    days = np.arange(0, MAX_D + 1)
    # 「无跳变」放在 d=30 之后，与日柱之间留空
    GAP_BEFORE_SILENT = 1.2

    for ax, model in zip(axes, MODELS):
        n = META[model]["n_eligible"]
        n_silent = META[model]["n_silent"]
        counts = np.asarray(N_AT_D[model], dtype=float)
        pmf_days = counts / n
        pmf_silent = n_silent / n
        x_days = np.arange(len(days), dtype=float)
        x_silent = float(len(days) - 1) + 1.0 + GAP_BEFORE_SILENT
        colors_days = [ST_JUMP["color"]] * len(days)
        hatches_days = [ST_JUMP["hatch"]] * len(days)

        bars_days = ax.bar(
            x_days, pmf_days, color=colors_days, hatch=hatches_days,
            edgecolor=ST_JUMP["edge"], linewidth=BAR_LW, width=0.82,
        )
        ax.bar(
            [x_silent], [pmf_silent], color=ST_SILENT["color"],
            hatch=ST_SILENT["hatch"], edgecolor=ST_JUMP["edge"],
            linewidth=BAR_LW, width=0.82,
        )

        # 横轴：d 标 0,5,...,30；「无跳变」在末尾
        tick_pos = [x_days[int(d)] for d in days if d % 5 == 0] + [x_silent]
        tick_lab = [str(int(d)) for d in days if d % 5 == 0] + ["无跳变"]
        ax.set_xticks(tick_pos)
        ax.set_xticklabels(
            tick_lab,
            rotation=0,
            ha="center",
            fontsize=FONT["tick"],
        )
        ax.yaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
        ax.set_title(f"{model}（$N$={n}）", fontsize=FONT["title"])
        ax.set_ylabel("占故障盘比例", fontsize=FONT["label"])
        y_max = max(float(pmf_days.max()), float(pmf_silent))
        ax.set_ylim(0, max(y_max * 1.12, 0.08))
        ax.grid(axis="y", alpha=0.25)
        ax.text(
            x_silent, pmf_silent + 0.01, f"{pmf_silent:.0%}",
            ha="center", fontsize=FONT["annot"], color=C_ZERO,
        )
        for day, bar in zip(days, bars_days):
            if day > NEAR_END and pmf_days[int(day)] > 0:
                bar.set_alpha(0.72)

        legend_loc = "upper right" if model == "MB1" else "upper left"
        ax.legend(
            handles=[
                legend_swatch(KEY_JUMP, f"{model} 有跳变"),
                legend_swatch(KEY_SILENT, "无跳变"),
            ],
            frameon=False, fontsize=FONT["legend"], loc=legend_loc,
        )

    fig.tight_layout()
    save_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(save_path, bbox_inches="tight", facecolor="white")
    return fig


def main() -> None:
    ensure_output_dirs()
    fig = plot()
    plt.close(fig)
    print(f"saved: {OUTPUT_PDF}")


if __name__ == "__main__":
    main()
