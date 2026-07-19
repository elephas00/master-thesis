"""第四章：轻量化采集消融（读取次数 / 磨损档位 / 字线采样）

生成 figure/generated/chap4-lightweight-ablation.pdf。

用法（项目根目录）:
    python3 figure_codes/chap4_lightweight_ablation.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from figure_paths import GENERATED_DIR as FIGURE_DIR, ensure_output_dirs
from thesis_style import (
    C_GRID,
    C_PRIMARY,
    C_ZERO,
    FONT,
    PAIR_READ,
    PAIR_READ_LS,
    PAIR_READ_MK,
    TEXT_WIDTH_IN,
    apply_rc,
    fig_shared_legend,
    savefig_text_width,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUT_PDF = FIGURE_DIR / "chap4-lightweight-ablation.pdf"

apply_rc()

VALUE_X = ["全部", "Value0", "Value1", "Value2", "Value3"]
VALUE = {
    "BestRead": [11.99, 11.43, 11.99, 11.99, 10.29],
    "DefaultRead": [17.08, 17.08, 16.52, 17.08, 17.08],
}
LEVEL_X = ["全部", "0", "1000", "2000", "3000"]
LEVEL = {
    "BestRead": [11.99, 11.99, 1.24, 2.94, -0.45],
    "DefaultRead": [17.08, 13.12, 15.95, 13.69, 10.29],
}
WL_X = ["全部", "0-0", "0-1", "0-9", "0-49", "0-99", "0-199", "0-399", "0-799"]
WL = {
    "BestRead": [11.43, 17.08, 17.08, 17.08, 17.08, 15.95, 17.08, 17.08, 13.69],
    "DefaultRead": [17.08, 16.25, 14.25, 13.69, 17.08, 17.08, 17.08, 17.08, 17.08],
}
BASELINE = 17.08


def _draw_panel(ax, xs, data, title: str) -> None:
    x = np.arange(len(xs))
    for rtype in ("DefaultRead", "BestRead"):
        ax.plot(
            x, data[rtype],
            color=PAIR_READ[rtype],
            ls=PAIR_READ_LS[rtype],
            marker=PAIR_READ_MK[rtype],
            lw=1.6, ms=5.0, label=rtype,
        )
    ax.axhline(0, color=C_ZERO, lw=0.8, ls="--", zorder=1)
    ax.axhline(BASELINE, color=C_PRIMARY, lw=0.9, ls=":", alpha=0.7, zorder=1)
    ax.set_xticks(x)
    ax.set_xticklabels(xs, rotation=35, ha="right", fontsize=FONT["note"])
    ax.set_title(title, fontsize=FONT["legend"], pad=3)
    ax.tick_params(axis="y", labelsize=FONT["tick"])
    ax.grid(True, axis="y", linestyle="--", color=C_GRID, alpha=0.8)
    ax.set_axisbelow(True)


def plot(*, save_path: Path = OUT_PDF) -> plt.Figure:
    fig, axes = plt.subplots(1, 3, figsize=(TEXT_WIDTH_IN, 2.25), sharey=True)

    _draw_panel(axes[0], VALUE_X, VALUE, "(a) 读取次数")
    _draw_panel(axes[1], LEVEL_X, LEVEL, "(b) 磨损档位")
    _draw_panel(axes[2], WL_X, WL, "(c) 字线采样")

    axes[0].set_ylabel(r"$R_{\mathrm{imp}}$ / \%", fontsize=FONT["note"])

    all_vals = (
        VALUE["BestRead"] + VALUE["DefaultRead"]
        + LEVEL["BestRead"] + LEVEL["DefaultRead"]
        + WL["BestRead"] + WL["DefaultRead"]
    )
    ymin, ymax = min(all_vals), max(all_vals)
    axes[0].set_ylim(ymin - 2.5, ymax + 2.5)

    yticks = sorted({*np.round(axes[0].get_yticks(), 2), 0.0, BASELINE})
    yticks = [t for t in yticks if ymin - 2.5 <= t <= ymax + 2.5]
    axes[0].set_yticks(yticks)
    axes[2].text(
        len(WL_X) - 1, BASELINE,
        "全量基准",
        ha="right", va="bottom", fontsize=FONT["annot"], color=C_PRIMARY,
    )

    fig.subplots_adjust(left=0.09, right=0.99, top=0.86, bottom=0.30, wspace=0.20)
    handles, labels = axes[0].get_legend_handles_labels()
    fig_shared_legend(
        fig,
        handles=handles,
        labels=labels,
        loc="lower center",
        bbox_to_anchor=(0.5, 0.01),
        ncol=2,
        fontsize=FONT["note"],
    )
    save_path.parent.mkdir(parents=True, exist_ok=True)
    savefig_text_width(fig, save_path, pad_inches=0.04)
    return fig


def main() -> None:
    ensure_output_dirs()
    fig = plot()
    plt.close(fig)
    print(f"saved: {OUT_PDF}")


if __name__ == "__main__":
    main()
