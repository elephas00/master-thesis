"""第四章：不同读模式 × 模型 × 页类型的写入量提升率

生成 figure/generated/chap4-rimp-by-model-readtype.pdf。

方案 C：1×2 折线；横轴 LP → MP → UP → 集成，三条线=模型。

用法（项目根目录）:
    python3 figure_codes/chap4_rimp_by_model_readtype.py
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
    TEXT_WIDTH_IN,
    apply_rc,
    fig_shared_legend,
    savefig_text_width,
    series_style,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUT_PDF = FIGURE_DIR / "chap4-rimp-by-model-readtype.pdf"

apply_rc()

MODELS = ["XGBoost", "LightGBM", "随机森林"]
COLS = ["LP", "MP", "UP", "集成"]
BASELINE = 17.08

DATA = {
    "BestRead": {
        "LP": [-6.11, -11.76, -11.76],
        "MP": [11.43, 11.99, -0.45],
        "UP": [-11.76, -11.76, -11.76],
        "集成": [11.43, 11.99, -0.45],
    },
    "DefaultRead": {
        "LP": [17.08, 17.08, 17.08],
        "MP": [15.95, 14.82, 16.52],
        "UP": [0.68, -2.71, 17.08],
        "集成": [17.08, 17.08, 17.08],
    },
}


def _series_for_model(read_type: str, model_idx: int) -> list[float]:
    return [DATA[read_type][col][model_idx] for col in COLS]


def _draw_panel(ax, read_type: str, *, show_ylabel: bool) -> None:
    x = np.arange(len(COLS))
    for i, model in enumerate(MODELS):
        st = series_style(i)
        ax.plot(
            x, _series_for_model(read_type, i),
            color=st["color"], ls=st["ls"], marker=st["marker"],
            lw=1.7, ms=6, label=model, zorder=3,
        )

    ax.axhline(0, color=C_ZERO, lw=0.9, zorder=2)
    ax.axhline(BASELINE, color=C_PRIMARY, lw=0.9, ls=":", alpha=0.7, zorder=2)
    ax.set_xticks(x)
    ax.set_xticklabels(COLS, fontsize=FONT["tick"])
    ax.set_title(read_type, fontsize=FONT["title"], pad=4)
    if show_ylabel:
        ax.set_ylabel(r"$R_{\mathrm{imp}}$ / \%", fontsize=FONT["note"])
    ax.tick_params(axis="y", labelsize=FONT["tick"])
    ax.grid(True, axis="y", linestyle="--", color=C_GRID, alpha=0.8)
    ax.set_axisbelow(True)


def plot(*, save_path: Path = OUT_PDF) -> plt.Figure:
    fig, axes = plt.subplots(1, 2, figsize=(TEXT_WIDTH_IN, 2.95), sharey=True)

    _draw_panel(axes[0], "BestRead", show_ylabel=True)
    _draw_panel(axes[1], "DefaultRead", show_ylabel=False)

    all_vals = [v for rt in DATA.values() for col in COLS for v in rt[col]]
    ymin, ymax = min(all_vals), max(all_vals)
    axes[0].set_ylim(ymin - 2.5, ymax + 2.5)

    yticks = sorted({*np.round(axes[0].get_yticks(), 2), 0.0, BASELINE})
    yticks = [t for t in yticks if ymin - 2.5 <= t <= ymax + 2.5]
    axes[0].set_yticks(yticks)
    axes[1].text(
        len(COLS) - 1, BASELINE,
        "全量基准",
        ha="right", va="bottom", fontsize=FONT["annot"], color=C_PRIMARY,
    )

    fig.subplots_adjust(left=0.10, right=0.99, top=0.88, bottom=0.22, wspace=0.18)
    handles, labels = axes[0].get_legend_handles_labels()
    fig_shared_legend(
        fig,
        handles=handles,
        labels=labels,
        loc="lower center",
        bbox_to_anchor=(0.5, 0.01),
        ncol=3,
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
