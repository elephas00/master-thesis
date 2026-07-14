"""测试集 TP 提前预警天数分布（分组柱图）

生成 figure/chap3-tp-lead-time-test.png。

协议与表 3.11 一致：Attention 集成；MB1 取 W=1,k=3，MB2 取 W=2,k=2；
jump_inter + Lag + r_k|Δ|；阈值 0.5。数据已固化，无需读取实验 CSV 或故障标签。

用法（项目根目录）:
    python3 figure_codes/chap3_tp_lead_time_test.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FIGURE_DIR = PROJECT_ROOT / "figure"
OUTPUT_PNG = FIGURE_DIR / "chap3-tp-lead-time-test.png"

plt.rcParams.update({
    "font.sans-serif": ["Arial Unicode MS", "PingFang SC", "SimHei", "DejaVu Sans"],
    "axes.unicode_minus": False,
    "figure.dpi": 120,
    "savefig.dpi": 180,
    "font.size": 10,
})

MODELS = ["MB1", "MB2"]
ROUNDS = [1, 2, 3]
ROUND_MONTH = {1: "2019-09", 2: "2019-10", 3: "2019-11"}
ROUND_FILL = {1: "#2563EB", 2: "#DC2626", 3: "#16A34A"}
ROUND_EDGE = {1: "#1E3A8A", 2: "#7F1D1D", 3: "#14532D"}
DAYS = np.arange(31)

# 各型号 × 轮次 × 提前天数 d 的 TP 盘数（d=0..30）
# 来源：Attention 集成 + 最优 W/k，codes/eda/run/tp_lead_time_test_attention_optimal_summary.json
HIST_COUNTS: dict[str, dict[int, list[int]]] = {
    "MB1": {
        1: [2, 33, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        2: [3, 43, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        3: [15, 51, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    },
    "MB2": {
        1: [5, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        2: [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        3: [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    },
}

# 图例统计：test 月内 TP / FP / 故障盘总数 FAIL
LEGEND_STATS: dict[str, dict[int, dict[str, int | str]]] = {
    "MB1": {
        1: {"test_month": "2019-09", "TP": 36, "FP": 0, "FAIL": 57},
        2: {"test_month": "2019-10", "TP": 47, "FP": 2, "FAIL": 72},
        3: {"test_month": "2019-11", "TP": 66, "FP": 1, "FAIL": 95},
    },
    "MB2": {
        1: {"test_month": "2019-09", "TP": 7, "FP": 0, "FAIL": 31},
        2: {"test_month": "2019-10", "TP": 2, "FP": 0, "FAIL": 14},
        3: {"test_month": "2019-11", "TP": 1, "FP": 0, "FAIL": 22},
    },
}


def _tail_label(round_id: int, day: int, count: float) -> str:
    return f"R{round_id}·d{day}·×{int(count)}"


def _legend_entries(model: str) -> tuple[list[Patch], list[str]]:
    handles, labels = [], []
    for rid in ROUNDS:
        stats = LEGEND_STATS[model][rid]
        handles.append(
            Patch(
                facecolor=ROUND_FILL[rid],
                edgecolor=ROUND_EDGE[rid],
                linewidth=0.85,
            )
        )
        labels.append(
            f"R{rid}  {stats['test_month']}  "
            f"TP={stats['TP']}  FP={stats['FP']}  FAIL={stats['FAIL']}"
        )
    return handles, labels


def plot_grouped_bars(
    *,
    bar_width: float = 0.28,
    cluster_max_day: int = 2,
    tail_day_threshold: int = 2,
    save_path: Path | None = None,
) -> plt.Figure:
    fig, axes = plt.subplots(1, 2, figsize=(12.0, 4.6), sharex=True)

    for ax, model in zip(axes, MODELS):
        cluster_peak = 0.0
        for rid in ROUNDS:
            hist = np.asarray(HIST_COUNTS[model][rid], dtype=float)
            cluster_peak = max(cluster_peak, hist[: cluster_max_day + 1].max())
        ymax = cluster_peak * 1.15 if cluster_peak > 0 else 1.0

        for i, rid in enumerate(ROUNDS):
            hist = np.asarray(HIST_COUNTS[model][rid], dtype=float)
            xs = DAYS + (i - 1) * bar_width
            bars = ax.bar(
                xs,
                hist,
                width=bar_width,
                color=ROUND_FILL[rid],
                edgecolor=ROUND_EDGE[rid],
                linewidth=0.85,
                zorder=3,
            )

            for d, (bar, c) in enumerate(zip(bars, hist)):
                if c <= 0 or d <= tail_day_threshold:
                    continue
                x = bar.get_x() + bar.get_width() / 2
                ax.annotate(
                    _tail_label(rid, d, c),
                    (x, float(c)),
                    textcoords="offset points",
                    xytext=(0, 4),
                    ha="center",
                    va="bottom",
                    fontsize=7.5,
                    color=ROUND_EDGE[rid],
                    fontweight="bold",
                    zorder=5,
                )

        ax.set_title(model, fontweight="bold")
        ax.set_xlim(-0.9, 30.9)
        ax.set_ylim(0, ymax)
        ax.set_xticks([0, 1, 2, 3, 5, 10, 15, 20, 25, 30])
        ax.set_ylabel("TP 盘数")
        ax.grid(axis="y", alpha=0.3, linewidth=0.6, zorder=0)
        ax.set_axisbelow(True)

        leg_handles, leg_labels = _legend_entries(model)
        ax.legend(
            leg_handles,
            leg_labels,
            loc="upper right",
            fontsize=7.5,
            framealpha=0.95,
            edgecolor="#CBD5E1",
            handlelength=1.2,
            handleheight=0.9,
        )

    fig.supxlabel("提前天数 $d=t_{\\mathrm{fail}}-t_{\\mathrm{alarm}}$（天）", y=0.02)
    fig.tight_layout()
    fig.subplots_adjust(bottom=0.16)

    if save_path is not None:
        fig.savefig(save_path, dpi=180, bbox_inches="tight")

    return fig


def main() -> None:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    fig = plot_grouped_bars(save_path=OUTPUT_PNG)
    plt.close(fig)
    print(f"saved: {OUTPUT_PNG}")


if __name__ == "__main__":
    main()
