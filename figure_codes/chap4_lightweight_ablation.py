"""第四章：轻量化采集消融（读取次数 / 磨损档位 / 字线采样）

生成 figure/chap4-lightweight-ablation.pdf。

用法（项目根目录）:
    python3 figure_codes/chap4_lightweight_ablation.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

from thesis_style import (
    C_GRID,
    C_PRIMARY,
    C_ZERO,
    FONT,
    PAIR_READ,
    PAIR_READ_LS,
    PAIR_READ_MK,
    apply_rc,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FIGURE_DIR = PROJECT_ROOT / "figure"
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


def _draw_panel(ax, xs, data, title: str, *, show_legend: bool = False) -> None:
    x = np.arange(len(xs))
    for rtype in ("DefaultRead", "BestRead"):
        ax.plot(
            x, data[rtype],
            color=PAIR_READ[rtype],
            ls=PAIR_READ_LS[rtype],
            marker=PAIR_READ_MK[rtype],
            lw=1.6, ms=5.5, label=rtype,
        )
    ax.axhline(0, color=C_ZERO, lw=0.8, ls="--", zorder=1)
    ax.axhline(BASELINE, color=C_PRIMARY, lw=0.9, ls=":", alpha=0.7, zorder=1)
    ax.set_xticks(x)
    ax.set_xticklabels(xs, rotation=30, ha="right")
    ax.set_title(title, fontsize=FONT["title"], pad=6)
    ax.grid(True, axis="y", linestyle="--", color=C_GRID, alpha=0.8)
    ax.set_axisbelow(True)
    if show_legend:
        handles, labels = ax.get_legend_handles_labels()
        handles.append(Line2D([0], [0], color=C_PRIMARY, ls=":", lw=0.9))
        labels.append(r"全量基准 $17.08\%$")
        ax.legend(handles, labels, frameon=False, loc="best", fontsize=FONT["legend"])


def plot(*, save_path: Path = OUT_PDF) -> plt.Figure:
    fig, axes = plt.subplots(1, 3, figsize=(12.0, 3.2), sharey=True)

    _draw_panel(axes[0], VALUE_X, VALUE, "(a) 读取次数", show_legend=True)
    _draw_panel(axes[1], LEVEL_X, LEVEL, "(b) 磨损档位", show_legend=True)
    _draw_panel(axes[2], WL_X, WL, "(c) 字线采样", show_legend=True)

    axes[0].set_ylabel(r"$R_{\mathrm{imp}}$ / \%", fontsize=FONT["label"])

    all_vals = (
        VALUE["BestRead"] + VALUE["DefaultRead"]
        + LEVEL["BestRead"] + LEVEL["DefaultRead"]
        + WL["BestRead"] + WL["DefaultRead"]
    )
    ymin, ymax = min(all_vals), max(all_vals)
    axes[0].set_ylim(ymin - 2.5, ymax + 2.5)

    fig.tight_layout()
    save_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(save_path, bbox_inches="tight", facecolor="white", pad_inches=0.08)
    return fig


def main() -> None:
    fig = plot()
    plt.close(fig)
    print(f"saved: {OUT_PDF}")


if __name__ == "__main__":
    main()
