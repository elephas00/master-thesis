"""第三章：日历缺失分布

生成 figure/generated/chap3-temporal-missing-distribution.pdf。

用法（项目根目录）:
    python3 figure_codes/chap3_temporal_missing_distribution.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from figure_paths import GENERATED_DIR as FIGURE_DIR, ensure_output_dirs
from thesis_style import (
    BAR_LW,
    C_EDGE,
    C_GRID,
    FONT,
    PAIR_MB,
    PAIR_MB_HATCH,
    TEXT_WIDTH_IN,
    apply_rc,
    savefig_text_width,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_PDF = FIGURE_DIR / "chap3-temporal-missing-distribution.pdf"

apply_rc()

MAX_GAP_LABELS = ["0", "1–7", "8–30", "31–90", ">90"]
COV_LABELS = ["<.5", ".5–.8", ".8–.95", "≥.95"]
RULE_LABELS = ["轻度\n(拟补全)", "中度\n(拟补全)", "重度\n(拟剔除)"]

GAP_COUNTS = {
    "MB1": [252, 28933, 9086, 2494, 3636],
    "MB2": [246, 30733, 10043, 2607, 5182],
}
COV_COUNTS = {
    "MB1": [337, 3355, 10458, 30251],
    "MB2": [1422, 4857, 8593, 33939],
}
RULE_PCT = {
    "MB1": [65.73, 20.46, 13.81],
    "MB2": [63.47, 20.58, 15.96],
}


def _pct(counts: list[int]) -> np.ndarray:
    arr = np.asarray(counts, dtype=float)
    return 100.0 * arr / arr.sum()


def _bar_pair(ax, x, models, values_fn, *, width: float = 0.26) -> None:
    """组内柱更窄、更靠拢，组间空隙更大。"""
    offset = width * 0.55
    for i, model in enumerate(models):
        ax.bar(
            x + (i - 0.5) * 2 * offset,
            values_fn(model),
            width=width,
            label=model,
            color=PAIR_MB[model],
            hatch=PAIR_MB_HATCH[model],
            edgecolor=C_EDGE,
            linewidth=BAR_LW,
        )


def plot(*, save_path: Path = OUTPUT_PDF) -> plt.Figure:
    models = ["MB1", "MB2"]
    fig, axes = plt.subplots(1, 3, figsize=(TEXT_WIDTH_IN, 1.65))

    ax = axes[0]
    x = np.arange(len(MAX_GAP_LABELS))
    _bar_pair(ax, x, models, lambda m: _pct(GAP_COUNTS[m]))
    ax.set_xticks(x)
    ax.set_xticklabels(MAX_GAP_LABELS, fontsize=FONT["note"])
    ax.set_xlim(-0.65, len(MAX_GAP_LABELS) - 0.35)
    ax.set_xlabel(r"$G_{\max}$（天）", fontsize=FONT["note"])
    ax.set_ylabel(r"盘占比 / \%", fontsize=FONT["note"])
    ax.set_title("(a) 按最长中断分档", fontsize=FONT["legend"], pad=2)
    ax.legend(frameon=False, fontsize=FONT["note"])
    ax.tick_params(axis="y", labelsize=FONT["note"])
    ax.set_ylim(0, max(75, ax.get_ylim()[1] * 1.05))
    ax.grid(axis="y", linestyle="--", color=C_GRID, alpha=0.8)
    ax.set_axisbelow(True)

    ax = axes[1]
    x = np.arange(len(COV_LABELS), dtype=float) * 1.15
    _bar_pair(ax, x, models, lambda m: _pct(COV_COUNTS[m]))
    ax.set_xticks(x)
    ax.set_xticklabels(COV_LABELS, fontsize=FONT["note"])
    ax.set_xlim(x[0] - 0.65, x[-1] + 0.65)
    ax.set_xlabel(r"$\mathrm{cov}$", fontsize=FONT["note"])
    ax.set_title("(b) 按覆盖率分档", fontsize=FONT["legend"], pad=2)
    ax.legend(frameon=False, fontsize=FONT["note"])
    ax.tick_params(axis="y", labelsize=FONT["note"])
    ax.grid(axis="y", linestyle="--", color=C_GRID, alpha=0.8)
    ax.set_axisbelow(True)

    ax = axes[2]
    x = np.arange(3)
    _bar_pair(ax, x, models, lambda m: RULE_PCT[m])
    ax.set_xticks(x)
    ax.set_xticklabels(RULE_LABELS, fontsize=FONT["note"])
    ax.set_xlim(-0.65, 3 - 0.35)
    ax.set_title("(c) 预处理分流", fontsize=FONT["legend"], pad=2)
    ax.legend(frameon=False, loc="upper right", fontsize=FONT["note"])
    ax.tick_params(axis="y", labelsize=FONT["note"])
    ax.grid(axis="y", linestyle="--", color=C_GRID, alpha=0.8)
    ax.set_axisbelow(True)

    fig.subplots_adjust(left=0.07, right=0.99, top=0.86, bottom=0.22, wspace=0.32)
    save_path.parent.mkdir(parents=True, exist_ok=True)
    savefig_text_width(fig, save_path, pad_inches=0.02)
    return fig


def main() -> None:
    ensure_output_dirs()
    fig = plot()
    plt.close(fig)
    print(f"saved: {OUTPUT_PDF}")


if __name__ == "__main__":
    main()
