"""第三章：日历缺失分布

生成 figure/chap3-temporal-missing-distribution.pdf。

用法（项目根目录）:
    python3 figure_codes/chap3_temporal_missing_distribution.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from thesis_style import BAR_LW, C_EDGE, C_GRID, FONT, PAIR_MB, PAIR_MB_HATCH, apply_rc

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FIGURE_DIR = PROJECT_ROOT / "figure"
OUTPUT_PDF = FIGURE_DIR / "chap3-temporal-missing-distribution.pdf"

apply_rc()

MAX_GAP_LABELS = ["0", "1–7", "8–30", "31–90", ">90"]
COV_LABELS = ["<0.5", "0.5–0.8", "0.8–0.95", "≥0.95"]
RULE_LABELS = ["轻度\n(拟进入补全)", "中度\n(拟进入补全)", "重度\n(拟整盘剔除)"]

N_DISKS = {"MB1": 44401, "MB2": 48811}
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


def _bar_pair(ax, x, models, values_fn) -> None:
    width = 0.36
    for i, model in enumerate(models):
        ax.bar(
            x + (i - 0.5) * width,
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
    fig, axes = plt.subplots(1, 3, figsize=(12.5, 4.2))

    ax = axes[0]
    x = np.arange(len(MAX_GAP_LABELS))
    _bar_pair(ax, x, models, lambda m: _pct(GAP_COUNTS[m]))
    ax.set_xticks(x)
    ax.set_xticklabels(MAX_GAP_LABELS)
    ax.set_xlabel(r"最长连续缺失天数 $G_{\max}$")
    ax.set_ylabel(r"磁盘占比 / \%")
    ax.set_title("(a) 按最长中断分档", fontsize=FONT["title"])
    ax.legend(frameon=False, fontsize=FONT["legend"])
    ax.set_ylim(0, max(75, ax.get_ylim()[1] * 1.05))
    ax.grid(axis="y", linestyle="--", color=C_GRID, alpha=0.8)

    ax = axes[1]
    x = np.arange(len(COV_LABELS))
    _bar_pair(ax, x, models, lambda m: _pct(COV_COUNTS[m]))
    ax.set_xticks(x)
    ax.set_xticklabels(COV_LABELS)
    ax.set_xlabel(r"日历覆盖率 $\mathrm{cov}=n_{\mathrm{obs}}/\mathrm{span}$")
    ax.set_ylabel(r"磁盘占比 / \%")
    ax.set_title("(b) 按覆盖率分档", fontsize=FONT["title"])
    ax.legend(frameon=False, fontsize=FONT["legend"])
    ax.grid(axis="y", linestyle="--", color=C_GRID, alpha=0.8)

    ax = axes[2]
    _bar_pair(ax, np.arange(3), models, lambda m: RULE_PCT[m])
    ax.set_xticks(np.arange(3))
    ax.set_xticklabels(RULE_LABELS)
    ax.set_ylabel(r"磁盘占比 / \%")
    ax.set_title("(c) 预处理分流（示意频数）", fontsize=FONT["title"])
    ax.legend(frameon=False, loc="upper right", fontsize=FONT["legend"])
    ax.grid(axis="y", linestyle="--", color=C_GRID, alpha=0.8)

    fig.tight_layout()
    save_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(save_path, bbox_inches="tight", facecolor="white")
    return fig


def main() -> None:
    fig = plot()
    plt.close(fig)
    print(f"saved: {OUTPUT_PDF}")


if __name__ == "__main__":
    main()
