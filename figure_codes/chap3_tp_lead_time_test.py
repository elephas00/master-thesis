"""测试集 TP 提前预警天数分布（近端分面 + 远端时间轴）

生成 figure/generated/chap3-tp-lead-time-test.pdf。

布局：上排 MB1/MB2 分面仅画 $d\\in\\{0,1,2\\}$（各自 y）；
下排全宽时间轴标出 $d>2$ 的稀疏远端检出（点旁短注）。

协议与表 3.11 一致：Attention 集成；MB1 取 W=1,k=2，MB2 取 W=2,k=2；
jump_inter + Lag + r_k|Δ|；阈值 0.5。数据已固化，无需读取实验 CSV 或故障标签。

用法（项目根目录）:
    python3 figure_codes/chap3_tp_lead_time_test.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.gridspec import GridSpec
from matplotlib.patches import Patch

from figure_paths import GENERATED_DIR as FIGURE_DIR, ensure_output_dirs
from thesis_style import (
    BAR_LW,
    C_GRID,
    FONT,
    ROUND_STYLES,
    TEXT_WIDTH_IN,
    apply_rc,
    fig_shared_legend,
    savefig_text_width,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_PDF = FIGURE_DIR / "chap3-tp-lead-time-test.pdf"

apply_rc()

MODELS = ["MB1", "MB2"]
ROUNDS = [1, 2, 3]
NEAR_DAYS = np.arange(0, 3)
BAR_W = 0.24
TAIL_DAY_THRESHOLD = 2

# 各型号 × 轮次 × 提前天数 d 的 TP 盘数（d=0..30）
# 来源：Attention 集成 + 最优 W/k，codes/eda/run/tp_lead_time_test_attention_optimal_summary.json
HIST_COUNTS: dict[str, dict[int, list[int]]] = {
    "MB1": {
        1: [2, 33, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        2: [2, 43, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        3: [15, 51, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    },
    "MB2": {
        1: [5, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        2: [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        3: [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    },
}

LEGEND_STATS: dict[str, dict[int, dict[str, int | str]]] = {
    "MB1": {
        1: {"test_month": "2019-09", "TP": 36, "FP": 0, "FAIL": 57},
        2: {"test_month": "2019-10", "TP": 46, "FP": 2, "FAIL": 72},
        3: {"test_month": "2019-11", "TP": 66, "FP": 1, "FAIL": 95},
    },
    "MB2": {
        1: {"test_month": "2019-09", "TP": 7, "FP": 0, "FAIL": 31},
        2: {"test_month": "2019-10", "TP": 2, "FP": 0, "FAIL": 14},
        3: {"test_month": "2019-11", "TP": 1, "FP": 0, "FAIL": 22},
    },
}


def _tail_events() -> list[tuple[str, int, int, int]]:
    rows: list[tuple[str, int, int, int]] = []
    for model in MODELS:
        for rid in ROUNDS:
            for d, c in enumerate(HIST_COUNTS[model][rid]):
                if d > TAIL_DAY_THRESHOLD and c > 0:
                    rows.append((model, rid, d, int(c)))
    return rows


def plot(*, save_path: Path | None = None) -> plt.Figure:
    """近端分面柱图 + 远端检出时间轴（精简排版）。"""
    fig = plt.figure(figsize=(TEXT_WIDTH_IN, 3.15))
    outer = GridSpec(
        2, 1, figure=fig,
        height_ratios=[3.4, 1.0],
        hspace=0.38,
        left=0.10, right=0.98, top=0.84, bottom=0.12,
    )
    gs_top = outer[0].subgridspec(1, 2, wspace=0.28)
    ax_l = fig.add_subplot(gs_top[0, 0])
    ax_r = fig.add_subplot(gs_top[0, 1])
    ax_t = fig.add_subplot(outer[1])

    for ax, model in zip((ax_l, ax_r), MODELS):
        peak = max(
            HIST_COUNTS[model][rid][d]
            for rid in ROUNDS
            for d in range(TAIL_DAY_THRESHOLD + 1)
        )
        for i, rid in enumerate(ROUNDS):
            hist = np.asarray(
                HIST_COUNTS[model][rid][: TAIL_DAY_THRESHOLD + 1], dtype=float,
            )
            st = ROUND_STYLES[rid]
            bars = ax.bar(
                NEAR_DAYS + (i - 1) * BAR_W,
                hist,
                width=BAR_W * 0.88,
                color=st["color"],
                hatch=st["hatch"],
                edgecolor=st["edge"],
                linewidth=BAR_LW,
                zorder=3,
            )
            for bar, c in zip(bars, hist):
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    float(c),
                    f"{int(c)}",
                    ha="center", va="bottom",
                    fontsize=FONT["annot"],
                    color="#333333",
                    zorder=4,
                    clip_on=False,
                )
        ax.set_title(model, fontsize=FONT["title"], pad=4)
        ax.set_xticks(NEAR_DAYS)
        ax.set_xticklabels(["0", "1", "2"])
        ax.set_xlabel(r"近端 $d$", fontsize=FONT["label"], labelpad=2)
        ax.set_ylim(0, max(peak * 1.22, 1.0))
        ax.yaxis.set_major_locator(plt.MaxNLocator(nbins=4, integer=True))
        ax.grid(axis="y", color=C_GRID, linewidth=0.55, alpha=0.85, zorder=0)
        ax.set_axisbelow(True)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
        ax.spines["left"].set_color("#9CA3AF")
        ax.spines["bottom"].set_color("#9CA3AF")
        ax.tick_params(labelsize=FONT["tick"])

    ax_l.set_ylabel("TP 盘数", fontsize=FONT["label"], labelpad=3)

    # ---- 共享图例（仅轮次）----
    handles = [
        Patch(
            facecolor=ROUND_STYLES[rid]["color"],
            hatch=ROUND_STYLES[rid]["hatch"],
            edgecolor=ROUND_STYLES[rid]["edge"],
            linewidth=BAR_LW,
            label=f"R{rid}  {LEGEND_STATS['MB1'][rid]['test_month']}",
        )
        for rid in ROUNDS
    ]
    fig_shared_legend(
        fig, handles,
        loc="lower center",
        bbox_to_anchor=(0.54, 0.97),
        ncol=3,
        title="图例",
        handlelength=1.3,
    )

    # ---- 远端：全宽时间轴，点旁短标注 ----
    ax_t.set_xlim(3.5, 27.5)
    ax_t.set_ylim(0.12, 0.88)
    ax_t.set_yticks([0.68, 0.32])
    ax_t.set_yticklabels(MODELS, fontsize=FONT["tick"])
    ax_t.set_xticks([5, 10, 15, 20, 25])
    ax_t.set_xlabel(r"远端检出 $d$（$d>2$）", fontsize=FONT["label"], labelpad=2)
    ax_t.tick_params(labelsize=FONT["tick"], length=3)
    for sp in ("top", "right"):
        ax_t.spines[sp].set_visible(False)
    ax_t.spines["left"].set_visible(False)
    ax_t.spines["bottom"].set_color("#9CA3AF")
    ax_t.tick_params(axis="y", length=0)

    lane_y = {"MB1": 0.68, "MB2": 0.32}
    for y0 in lane_y.values():
        ax_t.axhline(y0, color="#EDF0F3", lw=5.5, solid_capstyle="round", zorder=1)

    events = _tail_events()
    for model, rid, day, count in events:
        st = ROUND_STYLES[rid]
        y0 = lane_y[model]
        ax_t.plot(
            day, y0,
            marker="o", markersize=6.5,
            color=st["color"],
            markeredgecolor=st["edge"],
            markeredgewidth=0.85,
            linestyle="none",
            zorder=3,
        )
        # 标注放点右侧，避免压到 x 轴；TP 恒为 1 时仍写出以与图注一致
        ax_t.annotate(
            rf"R{rid},$d$={day},TP={count}",
            xy=(day, y0),
            xytext=(5, 0),
            textcoords="offset points",
            ha="left", va="center",
            fontsize=FONT["annot"], color="#4B5563",
            zorder=4, clip_on=False,
        )

    out = OUTPUT_PDF if save_path is None else save_path
    out.parent.mkdir(parents=True, exist_ok=True)
    savefig_text_width(fig, out)
    return fig


def plot_grouped_bars(*, save_path: Path | None = None, **_kwargs) -> plt.Figure:
    return plot(save_path=save_path)


def main() -> None:
    ensure_output_dirs()
    fig = plot(save_path=OUTPUT_PDF)
    plt.close(fig)
    print(f"saved: {OUTPUT_PDF}")


if __name__ == "__main__":
    main()
