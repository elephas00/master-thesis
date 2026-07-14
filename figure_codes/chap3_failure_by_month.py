"""第三章：月度故障盘分布

生成 figure/failure-by-month.png。

数据固化自 codes/eda/scripts/plot_failure_by_month.py
（源：ssd_failure_label.csv 按型号×月聚合）。

用法（项目根目录）:
    python3 figure_codes/chap3_failure_by_month.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FIGURE_DIR = PROJECT_ROOT / "figure"
OUTPUT_PNG = FIGURE_DIR / "failure-by-month.png"

plt.rcParams.update({
    "font.sans-serif": ["Arial Unicode MS", "PingFang SC", "SimHei", "DejaVu Sans"],
    "axes.unicode_minus": False,
    "font.size": 11,
})

MONTHS = [
    "2018-01", "2018-02", "2018-03", "2018-04", "2018-05", "2018-06",
    "2018-07", "2018-08", "2018-09", "2018-10", "2018-11", "2018-12",
    "2019-01", "2019-02", "2019-03", "2019-04", "2019-05", "2019-06",
    "2019-07", "2019-08", "2019-09", "2019-10", "2019-11", "2019-12",
]
COUNTS = {
    "MB1": [6, 7, 10, 14, 395, 79, 86, 84, 59, 67, 42, 57, 48, 45, 84, 27, 81, 109, 85, 52, 57, 72, 95, 146],
    "MB2": [3, 4, 13, 20, 55, 20, 33, 31, 20, 23, 22, 25, 50, 22, 21, 55, 27, 28, 18, 29, 31, 14, 22, 18],
}
COLORS = {"MB1": "#2563EB", "MB2": "#F97316"}


def plot(*, save_path: Path = OUTPUT_PNG) -> plt.Figure:
    x = range(len(MONTHS))
    width = 0.38
    fig, ax = plt.subplots(figsize=(10, 4.5))

    for model, offset in zip(("MB1", "MB2"), (-width / 2, width / 2)):
        ax.bar(
            [i + offset for i in x],
            COUNTS[model],
            width=width,
            label=model,
            color=COLORS[model],
            edgecolor="white",
            linewidth=0.6,
        )

    ax.set_xticks(list(x))
    ax.set_xticklabels(MONTHS, rotation=45, ha="right")
    ax.set_xlabel("月份")
    ax.set_ylabel("故障盘数量")
    ax.legend(frameon=False)
    ax.grid(axis="y", linestyle="--", alpha=0.35)
    ax.set_axisbelow(True)
    fig.tight_layout()

    save_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(save_path, dpi=300, bbox_inches="tight")
    return fig


def main() -> None:
    fig = plot()
    plt.close(fig)
    print(f"saved: {OUTPUT_PNG}")


if __name__ == "__main__":
    main()
