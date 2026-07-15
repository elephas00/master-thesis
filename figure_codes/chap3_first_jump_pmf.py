"""第三章：B 组首跳距故障日 PMF（含静默盘）

生成 figure/chap3-first-jump-pmf.pdf。

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

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FIGURE_DIR = PROJECT_ROOT / "figure"
OUTPUT_PDF = FIGURE_DIR / "chap3-first-jump-pmf.pdf"

plt.rcParams.update({
    "font.sans-serif": ["Arial Unicode MS", "PingFang SC", "SimHei", "DejaVu Sans"],
    "axes.unicode_minus": False,
    "figure.dpi": 120,
    "font.size": 11,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})

MODELS = ["MB1", "MB2"]
MAX_D = 30
NEAR_END = 14
COLORS = {"MB1": "#1565C0", "MB2": "#EF6C00"}
SILENT_COLOR = "#9E9E9E"

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
    fig, axes = plt.subplots(1, 2, figsize=(16, 4.6))
    days = np.arange(0, MAX_D + 1)

    for ax, model in zip(axes, MODELS):
        n = META[model]["n_eligible"]
        n_silent = META[model]["n_silent"]
        counts = np.asarray(N_AT_D[model], dtype=float)
        pmf_all = np.concatenate([[n_silent / n], counts / n])
        labels_all = ["无跳变"] + [str(int(d)) for d in days]
        x = np.arange(len(labels_all))
        colors_bar = [SILENT_COLOR] + [COLORS[model]] * len(days)

        bars = ax.bar(x, pmf_all, color=colors_bar, alpha=0.88, width=0.82)
        ax.set_xticks(x)
        ax.set_xticklabels(labels_all, rotation=0, ha="center", fontsize=6)
        ax.yaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
        ax.set_title(f"{model}（$N$={n}）")
        ax.set_ylabel("占故障盘比例")
        ax.set_ylim(0, max(float(pmf_all.max()) * 1.12, 0.08))
        ax.grid(axis="y", alpha=0.25)
        ax.text(0, pmf_all[0] + 0.01, f"{pmf_all[0]:.0%}", ha="center", fontsize=8, color="#444")
        for i, day in enumerate(days, start=1):
            if day > NEAR_END and pmf_all[i] > 0:
                bars[i].set_alpha(0.72)

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
