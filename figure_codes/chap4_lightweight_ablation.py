"""第四章：轻量化采集消融（读取次数 / 磨损档位 / 字线采样）

生成 figure/chap4-lightweight-ablation.pdf。

数据固化自正文表：
  tab:partial-value-results
  tab:partial-level-results
  tab:partial-wl-results

用法（项目根目录）:
    python3 figure_codes/chap4_lightweight_ablation.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FIGURE_DIR = PROJECT_ROOT / "figure"
OUT_PDF = FIGURE_DIR / "chap4-lightweight-ablation.pdf"

plt.rcParams.update({
    "font.sans-serif": ["Arial Unicode MS", "PingFang SC", "SimHei", "DejaVu Sans"],
    "axes.unicode_minus": False,
    "font.size": 10,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})

# (a) 读取次数
VALUE_X = ["全部", "Value0", "Value1", "Value2", "Value3"]
VALUE = {
    "BestRead": [11.99, 11.43, 11.99, 11.99, 10.29],
    "DefaultRead": [17.08, 17.08, 16.52, 17.08, 17.08],
}

# (b) 磨损档位
LEVEL_X = ["全部", "0", "1000", "2000", "3000"]
LEVEL = {
    "BestRead": [11.99, 11.99, 1.24, 2.94, -0.45],
    "DefaultRead": [17.08, 13.12, 15.95, 13.69, 10.29],
}

# (c) 字线采样
WL_X = ["全部", "0-0", "0-1", "0-9", "0-49", "0-99", "0-199", "0-399", "0-799"]
WL = {
    "BestRead": [11.43, 17.08, 17.08, 17.08, 17.08, 15.95, 17.08, 17.08, 13.69],
    "DefaultRead": [17.08, 16.25, 14.25, 13.69, 17.08, 17.08, 17.08, 17.08, 17.08],
}

COLORS = {"BestRead": "#64748B", "DefaultRead": "#2563EB"}
MARKERS = {"BestRead": "o", "DefaultRead": "s"}
BASELINE = 17.08  # DefaultRead 全量集成基准


def _draw_panel(ax, xs, data, title: str, *, show_legend: bool = False) -> None:
    x = np.arange(len(xs))
    for rtype in ("BestRead", "DefaultRead"):
        ax.plot(
            x, data[rtype],
            color=COLORS[rtype], marker=MARKERS[rtype],
            lw=1.6, ms=5.5, label=rtype,
        )
    ax.axhline(0, color="#94A3B8", lw=0.8, ls="--", zorder=1)
    ax.axhline(BASELINE, color="#2563EB", lw=0.9, ls=":", alpha=0.55, zorder=1)
    ax.set_xticks(x)
    ax.set_xticklabels(xs, rotation=30, ha="right")
    ax.set_title(title, fontsize=10.5, pad=6)
    ax.grid(True, axis="y", linestyle="--", alpha=0.28)
    ax.set_axisbelow(True)
    if show_legend:
        ax.legend(frameon=False, loc="best", fontsize=9)


def plot(*, save_path: Path = OUT_PDF) -> plt.Figure:
    fig, axes = plt.subplots(1, 3, figsize=(12.0, 3.6), sharey=True)

    _draw_panel(axes[0], VALUE_X, VALUE, "(a) 读取次数", show_legend=True)
    _draw_panel(axes[1], LEVEL_X, LEVEL, "(b) 磨损档位")
    _draw_panel(axes[2], WL_X, WL, "(c) 字线采样")

    axes[0].set_ylabel(r"$R_{\mathrm{imp}}$ / \%")
    # 点线含义：DefaultRead 全量基准
    axes[1].text(
        0.98, 0.04, r"点线：$17.08\%$ 全量基准",
        transform=axes[1].transAxes, ha="right", va="bottom",
        fontsize=8, color="#475569",
    )

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
