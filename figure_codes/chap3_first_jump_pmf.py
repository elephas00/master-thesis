"""第三章：B 组首跳距故障日 PMF（含静默盘）

生成 figure/generated/chap3-first-jump-pmf.pdf。

布局：无跳变柱靠左 + MB1/MB2 日分布折线 + 右上 $d\\geq 3$ inset。

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
from matplotlib.lines import Line2D
from matplotlib.ticker import MaxNLocator, PercentFormatter

from figure_paths import GENERATED_DIR as FIGURE_DIR, ensure_output_dirs
from thesis_style import (
    BAR_LW,
    C_EDGE,
    C_GRID,
    FONT,
    TEXT_WIDTH_IN,
    apply_rc,
    line_style,
    savefig_text_width,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_PDF = FIGURE_DIR / "chap3-first-jump-pmf.pdf"

apply_rc()

MODELS = ["MB1", "MB2"]
MAX_D = 30
GAP = 2.0
BAR_W = 0.38

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
    days = np.arange(0, MAX_D + 1)
    x_silent = 0.0
    x0_days = 1.0 + GAP
    x_days = x0_days + days.astype(float)
    band_left = x_silent - 0.70
    band_right = x_silent + 0.70

    ls_map = {m: line_style(i) for i, m in enumerate(MODELS)}
    pmf: dict[str, dict[str, float | np.ndarray | int]] = {}
    for m in MODELS:
        n = META[m]["n_eligible"]
        pmf[m] = {
            "days": np.asarray(N_AT_D[m], dtype=float) / n,
            "silent": META[m]["n_silent"] / n,
            "n": n,
        }

    fig = plt.figure(figsize=(TEXT_WIDTH_IN, 2.15))  # 再压矮一点
    # 主轴下移，顶部留给图例外置
    ax = fig.add_axes([0.10, 0.16, 0.88, 0.68])

    # 无跳变区域浅底；柱序左 MB2 / 右 MB1（百分比见正文，图上不标）
    ax.axvspan(band_left, band_right, color="#F3F4F6", zorder=0, lw=0)

    bar_order = ["MB2", "MB1"]
    for i, m in enumerate(bar_order):
        off = -BAR_W / 2 if i == 0 else BAR_W / 2
        ax.bar(
            [x_silent + off],
            [float(pmf[m]["silent"])],
            width=BAR_W,
            color=ls_map[m]["color"],
            edgecolor=C_EDGE,
            linewidth=BAR_LW,
            zorder=2,
            alpha=0.90,
        )

    for m in MODELS:
        ls = ls_map[m]
        y = np.asarray(pmf[m]["days"], dtype=float)
        ax.plot(
            x_days,
            y,
            color=ls["color"],
            ls=ls["ls"],
            linewidth=1.55,
            zorder=3,
            solid_capstyle="round",
        )
        nz = y > 0
        ax.plot(
            x_days[nz],
            y[nz],
            color=ls["color"],
            ls="none",
            marker=ls["marker"],
            markersize=3.5,
            markeredgewidth=0.7,
            markeredgecolor="white",
            zorder=4,
        )

    tick_pos = [x_silent] + [x_days[int(d)] for d in days if d % 5 == 0]
    tick_lab = ["无跳变"] + [str(int(d)) for d in days if d % 5 == 0]
    ax.set_xticks(tick_pos)
    ax.set_xticklabels(tick_lab, fontsize=FONT["tick"])
    ax.set_xlabel("首跳距故障日 $d$", fontsize=FONT["label"], labelpad=3)
    ax.set_ylabel("占故障盘比例", fontsize=FONT["label"], labelpad=2)
    ax.yaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
    ax.yaxis.set_major_locator(MaxNLocator(4))
    ax.grid(axis="y", color=C_GRID, linestyle="-", linewidth=0.55, alpha=0.85)
    ax.set_axisbelow(True)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.spines["left"].set_color("#9CA3AF")
    ax.spines["bottom"].set_color("#9CA3AF")

    y_max = max(
        max(float(np.asarray(pmf[m]["days"]).max()) for m in MODELS),
        max(float(pmf[m]["silent"]) for m in MODELS),
    )
    ax.set_ylim(0, y_max * 1.12)
    ax.set_xlim(band_left - 0.15, x_days[-1] + 0.5)

    # 右上 inset：$d \geq 3$（矮图略缩小）
    axins = ax.inset_axes([0.60, 0.32, 0.36, 0.52])
    axins.set_facecolor("white")
    axins.patch.set_alpha(1.0)
    axins.set_zorder(6)
    mask = days >= 3
    for m in MODELS:
        ls = ls_map[m]
        y = np.asarray(pmf[m]["days"], dtype=float)
        axins.plot(
            days[mask],
            y[mask],
            color=ls["color"],
            ls=ls["ls"],
            linewidth=1.15,
            zorder=2,
        )
        nz = (y > 0) & mask
        axins.plot(
            days[nz],
            y[nz],
            color=ls["color"],
            ls="none",
            marker=ls["marker"],
            markersize=2.6,
            markeredgewidth=0.4,
            markeredgecolor="white",
            zorder=3,
        )
    axins.set_xlim(3, 30)
    axins.set_ylim(0, 0.0095)
    axins.yaxis.set_major_formatter(PercentFormatter(1.0, decimals=1))
    axins.yaxis.set_major_locator(MaxNLocator(3))
    axins.set_xticks([10, 20, 30])
    axins.tick_params(labelsize=7, length=2.5, colors="#6B7280")
    for sp in axins.spines.values():
        sp.set_color("#CBD5E1")
        sp.set_linewidth(0.9)
    axins.grid(axis="y", color="#E5E7EB", linewidth=0.5)
    axins.set_axisbelow(True)
    axins.set_title(r"$d\geq 3$", fontsize=8, color="#4B5563", pad=2)

    handles = [
        Line2D(
            [0],
            [0],
            color=ls_map[m]["color"],
            ls=ls_map[m]["ls"],
            marker=ls_map[m]["marker"],
            markersize=5.5,
            linewidth=1.55,
            markeredgecolor="white",
            markeredgewidth=0.5,
        )
        for m in MODELS
    ]
    labels = [f"{m}（$N$={pmf[m]['n']}）" for m in MODELS]
    # 图例外置于坐标轴正上方（loc=lower center：锚点在图例底边）
    fig.legend(
        handles,
        labels,
        loc="lower center",
        bbox_to_anchor=(0.54, 0.87),
        bbox_transform=fig.transFigure,
        ncol=2,
        frameon=False,
        fontsize=FONT["legend"],
        handlelength=2.0,
        columnspacing=1.2,
    )

    save_path.parent.mkdir(parents=True, exist_ok=True)
    savefig_text_width(fig, save_path)
    return fig


def main() -> None:
    ensure_output_dirs()
    fig = plot()
    plt.close(fig)
    print(f"saved: {OUTPUT_PDF}")


if __name__ == "__main__":
    main()
