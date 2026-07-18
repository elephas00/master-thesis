"""第四章：轻量化采集消融（读取次数 / 磨损档位 / 字线采样）

生成 figure/generated/chap4-lightweight-ablation.pdf。

用法（项目根目录）:
    python3 figure_codes/chap4_lightweight_ablation.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.transforms import blended_transform_factory

from figure_paths import GENERATED_DIR as FIGURE_DIR, ensure_output_dirs
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
            lw=1.6, ms=5.5, label=rtype,
        )
    ax.axhline(0, color=C_ZERO, lw=0.8, ls="--", zorder=1)
    ax.axhline(BASELINE, color=C_PRIMARY, lw=0.9, ls=":", alpha=0.7, zorder=1)
    ax.set_xticks(x)
    ax.set_xticklabels(xs, rotation=30, ha="right")
    ax.set_title(title, fontsize=FONT["title"], pad=6)
    ax.grid(True, axis="y", linestyle="--", color=C_GRID, alpha=0.8)
    ax.set_axisbelow(True)


def plot(*, save_path: Path = OUT_PDF) -> plt.Figure:
    fig, axes = plt.subplots(1, 3, figsize=(12.0, 3.2), sharey=True)

    _draw_panel(axes[0], VALUE_X, VALUE, "(a) 读取次数")
    _draw_panel(axes[1], LEVEL_X, LEVEL, "(b) 磨损档位")
    _draw_panel(axes[2], WL_X, WL, "(c) 字线采样")

    axes[0].set_ylabel(r"$R_{\mathrm{imp}}$ / \%", fontsize=FONT["label"])

    all_vals = (
        VALUE["BestRead"] + VALUE["DefaultRead"]
        + LEVEL["BestRead"] + LEVEL["DefaultRead"]
        + WL["BestRead"] + WL["DefaultRead"]
    )
    ymin, ymax = min(all_vals), max(all_vals)
    axes[0].set_ylim(ymin - 2.5, ymax + 2.5)

    # 全量基准用虚线 + 纵轴刻度标出
    yticks = sorted({*np.round(axes[0].get_yticks(), 2), 0.0, BASELINE})
    yticks = [t for t in yticks if ymin - 2.5 <= t <= ymax + 2.5]
    axes[0].set_yticks(yticks)
    axes[2].text(
        len(WL_X) - 1, BASELINE,
        "全量基准",
        ha="right", va="bottom", fontsize=FONT["annot"], color=C_PRIMARY,
    )

    # 左下角、贴在 y=0 虚线上方（x 用轴坐标，y 用数据坐标）
    for ax in axes:
        trans = blended_transform_factory(ax.transAxes, ax.transData)
        ax.legend(
            frameon=False, loc="lower left", fontsize=FONT["legend"],
            bbox_to_anchor=(0.02, 0.8), bbox_transform=trans, borderaxespad=0,
        )

    fig.tight_layout()
    save_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(save_path, bbox_inches="tight", facecolor="white", pad_inches=0.08)
    return fig


def main() -> None:
    ensure_output_dirs()
    fig = plot()
    plt.close(fig)
    print(f"saved: {OUT_PDF}")


if __name__ == "__main__":
    main()
